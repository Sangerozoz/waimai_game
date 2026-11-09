import { StoragePort } from './CountySaveStore';
import { WebWriterLease } from './WebWriterLease';

/** Exactly one game snapshot; epoch contains concurrency metadata only. */
export const V2_RUNTIME_SAVE_KEY = 'delivery-county-single-slot-v1';
export const V2_SLOT_EPOCH_KEY = 'delivery-county-single-slot-epoch-v1';
export const LEGACY_GAME_SAVE_KEYS: readonly string[] = [
    'delivery-game-save-v1', 'delivery-game-save-v1-recovery',
    ...['delivery-county-save-v1', 'delivery-county-v2-economy-save-v1', 'delivery-county-v2-runtime-save-v1']
        .flatMap(key => [key, key + ':backup', key + ':corrupt', key + ':pre-foundation']),
];
export interface V2WriterPort { readonly writable: boolean; acquire(): Promise<boolean>; release(): void }
export interface SingleSlotStorage extends StoragePort { removeItem?(key: string): void }

/** No migration, backup, archive, or fallback. All writes require the shared legacy Web Lock. */
export class V2RuntimeStore {
    private stopped = false;
    private closed = false;
    private initialized = false;
    private epoch: string | null = null;
    private expected: string | null = null;
    private status = '';
    constructor(private readonly storage: SingleSlotStorage, private readonly writer: V2WriterPort = new WebWriterLease()) {}
    get writable(): boolean {
        if (!this.initialized || this.stopped || this.closed) return false;
        try {
            if (!this.writer.writable) throw new Error('已失去进度写入权，请关闭其他游戏页后重新打开');
            if (this.storage.getItem(V2_SLOT_EPOCH_KEY) !== this.epoch) throw new Error('进度写入世代已改变，请重新打开游戏');
            return true;
        } catch (error) { this.stopped = true; this.status = String(error); return false; }
    }
    get message(): string { return this.status; }
    private remove(key: string): void {
        if (this.storage.getItem(key) === null) return;
        if (!this.storage.removeItem) throw new Error('存储不支持清除进度');
        this.storage.removeItem(key);
        if (this.storage.getItem(key) !== null) throw new Error('旧进度清除失败，请检查浏览器存储权限');
    }
    private cleanLegacy(): void { for (const key of LEGACY_GAME_SAVE_KEYS) this.remove(key); }
    private newEpoch(): string { return Date.now().toString(36) + '-' + Math.random().toString(36).slice(2); }
    private async acquire(): Promise<void> {
        if (this.closed || !await this.writer.acquire()) throw new Error('请先关闭其他游戏页，再继续游戏');
        if (this.closed) { this.writer.release(); throw new Error('存储已关闭'); }
    }
    /** Called by the entry screen on startup, without touching a browser outside the running game. */
    async prepare(): Promise<boolean> {
        await this.acquire();
        try { this.cleanLegacy(); return this.storage.getItem(V2_RUNTIME_SAVE_KEY) !== null; }
        finally { this.writer.release(); }
    }
    async open<T>(mode: 'new' | 'restore' | 'continue' | 'reset', restore: (raw: string) => T, fresh: () => T): Promise<T> {
        if (this.initialized || this.closed) throw new Error('存储已经打开或关闭');
        await this.acquire();
        try {
            this.cleanLegacy();
            this.epoch = this.storage.getItem(V2_SLOT_EPOCH_KEY);
            if (this.epoch === null) { this.epoch = this.newEpoch(); this.storage.setItem(V2_SLOT_EPOCH_KEY, this.epoch); }
            this.expected = this.storage.getItem(V2_RUNTIME_SAVE_KEY);
            if (mode === 'reset') return this.reset(fresh);
            if (mode === 'new' && this.expected !== null) throw new Error('已有当前进度，请继续游戏');
            if (mode === 'restore' && this.expected === null) throw new Error('没有当前进度，请开始游戏');
            let session: T;
            if (this.expected === null) session = fresh();
            else {
                try { session = restore(this.expected); }
                catch { throw new Error('当前进度损坏或版本不兼容，已保留原进度并停止载入；请联系支持或使用兼容版本。'); }
            }
            this.initialized = true;
            return session;
        } catch (error) { this.writer.release(); throw error; }
    }
    reset<T>(fresh: () => T): T {
        if (this.closed || !this.writer.writable) throw new Error('没有进度写入权，请关闭其他游戏页');
        // Revoke every older runtime before deleting any bytes. Failure never resumes autosave.
        this.initialized = false; this.stopped = true;
        try {
            this.epoch = this.newEpoch();
            this.storage.setItem(V2_SLOT_EPOCH_KEY, this.epoch);
            this.remove(V2_RUNTIME_SAVE_KEY);
            this.cleanLegacy();
            this.expected = null;
            const session = fresh();
            this.stopped = false; this.initialized = true;
            return session;
        } catch (error) { this.status = String(error); throw error; }
    }
    commit(serialized: string): void {
        try {
            if (!this.writable) throw new Error('进度写入已停止，请重新打开游戏');
            if (this.storage.getItem(V2_RUNTIME_SAVE_KEY) !== this.expected) throw new Error('进度已被其他操作改变，请重新打开游戏');
            this.storage.setItem(V2_RUNTIME_SAVE_KEY, serialized);
            this.expected = serialized;
            this.status = '进度已保存';
        } catch (error) { this.stopped = true; this.status = String(error); throw error; }
    }
    close(): void { this.closed = true; this.writer.release(); }
}
