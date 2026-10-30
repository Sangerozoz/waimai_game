const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const PRIMARY = 'delivery-county-save-v1';
const BACKUP = PRIMARY + ':backup';
const CORRUPT = PRIMARY + ':corrupt';
const LEGACY = 'delivery-game-save-v1';

class MemoryStorage {
  constructor(values = {}) {
    this.values = new Map(Object.entries(values));
    this.failedReads = new Set();
    this.failedWrites = new Set();
  }

  getItem(key) {
    if (this.failedReads.has(key)) throw new Error('Storage read denied');
    return this.values.has(key) ? this.values.get(key) : null;
  }

  setItem(key, value) {
    if (this.failedWrites.has(key)) throw new Error('QuotaExceededError');
    this.values.set(key, value);
  }

  bytes(key) {
    return this.values.has(key) ? this.values.get(key) : null;
  }
}

function createStore(storage, key) {
  const modulePath = process.env.COUNTY_SAVE_STORE_MODULE;
  assert.ok(modulePath && fs.existsSync(modulePath), 'The county persistence boundary must exist to save a session');
  const { CountySaveStore } = require(path.resolve(modulePath));
  return new CountySaveStore(storage, key);
}

function restore(raw) {
  const session = JSON.parse(raw);
  if (!session || !Number.isInteger(session.turn) || session.turn < 0) {
    throw new Error('Invalid county session');
  }
  return session;
}

const fresh = () => ({ turn: 0 });

test('a fresh session can be saved and restored by a new store', () => {
  const storage = new MemoryStorage();
  const store = createStore(storage);
  assert.deepEqual(store.load(restore, fresh).session, { turn: 0 });
  assert.equal(store.save('{"turn":3}'), true);
  assert.equal(storage.bytes(PRIMARY), '{"turn":3}');
  assert.equal(store.available, true);

  const reloaded = createStore(storage);
  const result = reloaded.load(restore, fresh);
  assert.deepEqual(result.session, { turn: 3 });
  assert.equal(result.message, reloaded.message);
  assert.match(result.message, /恢复/);
});

test('a replacement keeps the previous confirmed session as backup', () => {
  const storage = new MemoryStorage({ [PRIMARY]: '{"turn":2}' });
  const store = createStore(storage);
  store.load(restore, fresh);
  assert.equal(store.save('{"turn":3}'), true);
  assert.equal(storage.bytes(BACKUP), '{"turn":2}');
  assert.equal(storage.bytes(PRIMARY), '{"turn":3}');

  assert.equal(store.save('{"turn":3}'), true);
  assert.equal(storage.bytes(BACKUP), '{"turn":2}', 'an unchanged autosave must keep the previous distinct session');
  assert.equal(store.save('{"turn":4}'), true);
  assert.equal(storage.bytes(BACKUP), '{"turn":3}');
});

test('a custom namespace saves independently and leaves the legacy game key intact', () => {
  const storage = new MemoryStorage({ [LEGACY]: 'legacy-bytes' });
  storage.failedReads.add(LEGACY);
  storage.failedWrites.add(LEGACY);
  const store = createStore(storage, 'another-county');
  store.load(restore, fresh);
  assert.equal(store.save('{"turn":5}'), true);
  assert.equal(store.save('{"turn":6}'), true);
  assert.equal(storage.bytes('another-county'), '{"turn":6}');
  assert.equal(storage.bytes('another-county:backup'), '{"turn":5}');
  assert.equal(storage.bytes(PRIMARY), null);
  assert.equal(storage.bytes(LEGACY), 'legacy-bytes');
});

test('a corrupt primary is retained before a valid backup is used and replaced', () => {
  const storage = new MemoryStorage({
    [PRIMARY]: '{"turn":',
    [BACKUP]: '{"turn":7}',
    [LEGACY]: 'legacy-bytes',
  });
  const store = createStore(storage);
  const result = store.load(restore, fresh);
  assert.deepEqual(result.session, { turn: 7 });
  assert.match(result.message, /损坏.*保留.*备份恢复/);
  assert.equal(store.available, true);
  assert.equal(storage.bytes(PRIMARY), '{"turn":', 'load must not replace the damaged primary');

  assert.equal(store.save('{"turn":8}'), true);
  assert.equal(storage.bytes(CORRUPT), '{"turn":');
  assert.equal(storage.bytes(BACKUP), '{"turn":7}');
  assert.equal(storage.bytes(PRIMARY), '{"turn":8}');
  assert.equal(storage.bytes(LEGACY), 'legacy-bytes');
});

test('schema-invalid JSON is treated as corrupt and the fresh session can be saved safely', () => {
  const storage = new MemoryStorage({
    [PRIMARY]: '{"turn":"invalid"}',
    [BACKUP]: '{"turn":-1}',
  });
  const store = createStore(storage);
  const result = store.load(restore, fresh);
  assert.deepEqual(result.session, { turn: 0 });
  assert.match(result.message, /损坏/);
  assert.equal(store.save('{"turn":1}'), true);
  assert.equal(storage.bytes(CORRUPT), '{"turn":"invalid"}');
  assert.equal(storage.bytes(BACKUP), '{"turn":-1}', 'fresh bytes are not a confirmed backup before their first successful primary write');
  assert.equal(storage.bytes(PRIMARY), '{"turn":1}');
});

test('a missing primary can recover its valid backup', () => {
  const storage = new MemoryStorage({ [BACKUP]: '{"turn":4}' });
  const store = createStore(storage);
  const result = store.load(restore, fresh);
  assert.deepEqual(result.session, { turn: 4 });
  assert.match(result.message, /备份恢复/);
  assert.equal(store.save('{"turn":5}'), true);
  assert.equal(storage.bytes(BACKUP), '{"turn":4}');
  assert.equal(storage.bytes(PRIMARY), '{"turn":5}');
});

test('empty corrupt bytes are preserved in the custom namespace', () => {
  const storage = new MemoryStorage({ 'another-county': '' });
  const store = createStore(storage, 'another-county');
  assert.deepEqual(store.load(restore, fresh).session, { turn: 0 });
  assert.equal(store.save('{"turn":1}'), true);
  assert.equal(storage.bytes('another-county:corrupt'), '');
  assert.equal(storage.bytes(CORRUPT), null);
});

test('a primary read failure is visible and cannot overwrite unread existing progress', () => {
  const storage = new MemoryStorage({ [PRIMARY]: '{"turn":9}' });
  storage.failedReads.add(PRIMARY);
  const store = createStore(storage);
  const result = store.load(restore, fresh);
  assert.deepEqual(result.session, { turn: 0 });
  assert.equal(store.available, false);
  assert.equal(result.message, store.message);
  assert.match(result.message, /读取失败.*暂停保存/);
  storage.failedReads.clear();
  assert.equal(store.save('{"turn":1}'), false);
  assert.equal(storage.bytes(PRIMARY), '{"turn":9}');
  assert.equal(store.available, false);
});

test('an unreadable backup blocks replacement after primary corruption', () => {
  const storage = new MemoryStorage({ [PRIMARY]: 'bad-primary', [BACKUP]: '{"turn":9}' });
  storage.failedReads.add(BACKUP);
  const store = createStore(storage);
  assert.deepEqual(store.load(restore, fresh).session, { turn: 0 });
  assert.equal(store.available, false);
  assert.match(store.message, /读取失败/);
  assert.equal(store.save('{"turn":1}'), false);
  assert.equal(storage.bytes(PRIMARY), 'bad-primary');
  assert.equal(storage.bytes(BACKUP), '{"turn":9}');
});

test('a failed previous-good backup write leaves the primary unchanged', () => {
  const storage = new MemoryStorage({ [PRIMARY]: '{"turn":2}', [BACKUP]: '{"turn":1}' });
  const store = createStore(storage);
  store.load(restore, fresh);
  storage.failedWrites.add(BACKUP);
  assert.equal(store.save('{"turn":3}'), false);
  assert.equal(store.available, false);
  assert.match(store.message, /备份.*写入失败/);
  assert.equal(storage.bytes(PRIMARY), '{"turn":2}');
  assert.equal(storage.bytes(BACKUP), '{"turn":1}');
});

test('a primary quota failure is visible and preserves the last confirmed progress', () => {
  const storage = new MemoryStorage({ [PRIMARY]: '{"turn":2}' });
  const store = createStore(storage);
  store.load(restore, fresh);
  storage.failedWrites.add(PRIMARY);
  assert.equal(store.save('{"turn":3}'), false);
  assert.equal(store.available, false);
  assert.match(store.message, /存档.*写入失败/);
  assert.equal(storage.bytes(PRIMARY), '{"turn":2}');
  assert.equal(storage.bytes(BACKUP), '{"turn":2}');

  storage.failedWrites.clear();
  assert.equal(store.save('{"turn":4}'), true);
  assert.equal(store.available, true);
  assert.equal(storage.bytes(PRIMARY), '{"turn":4}');
  assert.equal(storage.bytes(BACKUP), '{"turn":2}', 'the failed turn 3 must never become a confirmed backup');
});

test('a failed first save does not promote fresh bytes to the known-good backup', () => {
  const storage = new MemoryStorage();
  const store = createStore(storage);
  store.load(restore, fresh);
  storage.failedWrites.add(PRIMARY);
  assert.equal(store.save('{"turn":1}'), false);
  assert.equal(storage.bytes(PRIMARY), null);
  assert.equal(storage.bytes(BACKUP), null);

  storage.failedWrites.clear();
  assert.equal(store.save('{"turn":2}'), true);
  assert.equal(storage.bytes(BACKUP), null);
  assert.equal(store.save('{"turn":3}'), true);
  assert.equal(storage.bytes(BACKUP), '{"turn":2}');
});

test('when corrupt bytes cannot be retained their only copy cannot be overwritten later', () => {
  const storage = new MemoryStorage({ [PRIMARY]: 'only-corrupt-copy' });
  storage.failedWrites.add(CORRUPT);
  const store = createStore(storage);
  const result = store.load(restore, fresh);
  assert.deepEqual(result.session, { turn: 0 });
  assert.equal(store.available, false);
  assert.match(result.message, /损坏.*无法保留.*暂停保存/);
  storage.failedWrites.clear();
  assert.equal(store.save('{"turn":1}'), false);
  assert.equal(storage.bytes(PRIMARY), 'only-corrupt-copy');
  assert.equal(storage.bytes(CORRUPT), null);
});

test('a valid backup can recover gameplay even while corrupt preservation failure disables saving', () => {
  const storage = new MemoryStorage({ [PRIMARY]: 'only-corrupt-copy', [BACKUP]: '{"turn":8}' });
  storage.failedWrites.add(CORRUPT);
  const store = createStore(storage);
  const result = store.load(restore, fresh);
  assert.deepEqual(result.session, { turn: 8 });
  assert.equal(store.available, false);
  assert.match(result.message, /无法保留.*备份恢复/);
  assert.equal(store.save('{"turn":9}'), false);
  assert.equal(storage.bytes(PRIMARY), 'only-corrupt-copy');
  assert.equal(storage.bytes(BACKUP), '{"turn":8}');
});

test('a read failure during save returns failure without replacing stored progress', () => {
  const storage = new MemoryStorage({ [PRIMARY]: '{"turn":6}', [BACKUP]: '{"turn":5}' });
  const store = createStore(storage);
  store.load(restore, fresh);
  storage.failedReads.add(PRIMARY);
  assert.equal(store.save('{"turn":7}'), false);
  assert.equal(store.available, false);
  assert.match(store.message, /读取失败/);
  assert.equal(storage.bytes(PRIMARY), '{"turn":6}');
  assert.equal(storage.bytes(BACKUP), '{"turn":5}');

  storage.failedReads.clear();
  assert.equal(store.save('{"turn":8}'), true);
  assert.equal(storage.bytes(BACKUP), '{"turn":6}');
});

test('save refuses to overwrite an existing session that this store has not loaded', () => {
  const storage = new MemoryStorage({ [PRIMARY]: '{"turn":6}' });
  const store = createStore(storage);
  assert.equal(store.save('{"turn":1}'), false);
  assert.equal(store.available, false);
  assert.match(store.message, /读取.*校验/);
  assert.equal(storage.bytes(PRIMARY), '{"turn":6}');

  assert.deepEqual(store.load(restore, fresh).session, { turn: 6 });
  assert.equal(store.save('{"turn":7}'), true);
  assert.equal(storage.bytes(BACKUP), '{"turn":6}');
});

test('save detects a primary changed by another writer instead of overwriting its bytes', () => {
  const storage = new MemoryStorage({ [PRIMARY]: '{"turn":2}' });
  const store = createStore(storage);
  store.load(restore, fresh);
  storage.setItem(PRIMARY, 'newly-corrupt-primary');
  assert.equal(store.save('{"turn":3}'), false);
  assert.equal(store.available, false);
  assert.match(store.message, /变更.*重新读取/);
  assert.equal(storage.bytes(PRIMARY), 'newly-corrupt-primary');

  assert.deepEqual(store.load(restore, fresh).session, { turn: 0 });
  assert.equal(store.save('{"turn":1}'), true);
  assert.equal(storage.bytes(CORRUPT), 'newly-corrupt-primary');
});

test('a store may write its first session without load when the primary is empty', () => {
  const storage = new MemoryStorage();
  const store = createStore(storage);
  assert.equal(store.save('{"turn":1}'), true);
  assert.equal(storage.bytes(PRIMARY), '{"turn":1}');
  assert.equal(store.save('{"turn":2}'), true);
  assert.equal(storage.bytes(BACKUP), '{"turn":1}');
});
