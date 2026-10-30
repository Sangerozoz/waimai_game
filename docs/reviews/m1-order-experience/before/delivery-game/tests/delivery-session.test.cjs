const assert = require('node:assert/strict');
const test = require('node:test');
const { DeliverySession } = require(process.env.DELIVERY_SESSION_MODULE);

function complete(game, route = 'fast') {
  game.acceptOrder(game.getState().orders[0].id);
  game.depart(route);
  game.advance(1000);
  return game.settle();
}

function normalGame(rng = () => 0.99) {
  const game = new DeliverySession(rng);
  complete(game);
  game.returnToOrders();
  return game;
}

function alterSave(game, change) {
  const saved = JSON.parse(game.serialize());
  change(saved.state, saved);
  return JSON.stringify(saved);
}

test('first delivery awards 2180 cents, 10 XP and one order from 100 yuan', () => {
  const game = new DeliverySession(() => 0.99);
  const initial = game.getState();
  assert.equal(initial.orders.length, 1);
  assert.equal(initial.orders[0].weightKg, 1);
  assert.equal(initial.orders[0].fragility, 'durable');
  assert.equal(initial.orders[0].rain, false);
  assert.deepEqual(initial.player, {
    cashCents: 10000, rating: 80, experience: 0, completedOrders: 0,
    vehicleTier: 1, stationLevel: 1, level: 1,
  });
  const receipt = complete(game);
  assert.equal(receipt.incomeCents, 2180);
  assert.equal(receipt.ratingDelta, 0);
  assert.equal(receipt.newCashCents, 12180);
  assert.equal(game.getState().player.experience, 10);
  assert.equal(game.getState().player.completedOrders, 1);
  assert.equal(game.getState().tutorialComplete, false);
});

test('returning after tutorial enables five orders and refills only the accepted slot', () => {
  const game = normalGame();
  assert.equal(game.getState().tutorialComplete, true);
  assert.equal(game.getState().player.cashCents, 12180);
  const previous = game.getState().orders.map(order => order.id);
  complete(game);
  game.returnToOrders();
  const next = game.getState().orders;
  assert.equal(next.length, 5);
  assert.equal(new Set(next.map(order => order.id)).size, 5);
  assert.ok(previous.slice(1).every(id => next.some(order => order.id === id)));
  assert.ok(!next.some(order => order.id === previous[0]));
});

test('route previews show exact timing and risk without starting delivery or changing rating', () => {
  const game = new DeliverySession(() => 0.99);
  game.acceptOrder(game.getState().orders[0].id);
  const before = game.serialize();
  const previews = game.previewRoutes();
  assert.deepEqual(previews.map(route => [route.id, route.name, route.durationSeconds, route.damageChance]), [
    ['fast', '快捷路', 5, 0.08], ['main', '主干道', 10, 0.04], ['smooth', '平稳路', 13, 0.01],
  ]);
  assert.ok(previews.every(route => route.lateSeconds === 0 && route.arrivalTemperature === null));
  game.advance(300);
  assert.equal(game.serialize(), before);
  game.depart('smooth');
  game.advance(1000);
  assert.equal(game.getState().elapsedSeconds, 13);
  assert.equal(game.settle().ratingDelta, 0);
});

test('generated urgent order late penalty occurs once using route duration, never a large dt', () => {
  let value = 0.99;
  const game = new DeliverySession(() => value);
  complete(game);
  value = 0.15;
  game.returnToOrders();
  const urgent = game.getState().orders.find(order => order.type === 'urgent');
  assert.ok(urgent);
  assert.equal(urgent.deadlineSeconds, 8);
  game.acceptOrder(urgent.id);
  value = 0.99;
  game.depart('smooth');
  game.advance(50000);
  const receipt = game.settle();
  assert.equal(receipt.lateSeconds, 5);
  assert.equal(receipt.ratingDelta, -3);
  assert.equal(receipt.ratingAfter, 77);
  assert.equal(receipt.incomeCents, Math.round(urgent.basePriceCents * 1.081));
  const cash = game.getState().player.cashCents;
  assert.deepEqual(game.settle(), receipt);
  assert.equal(game.getState().player.cashCents, cash);
});

test('urgent on-time arrival rewards two rating points with the new rating income multiplier', () => {
  let value = 0.99;
  const game = new DeliverySession(() => value);
  complete(game);
  value = 0.15;
  game.returnToOrders();
  const urgent = game.getState().orders[0];
  game.acceptOrder(urgent.id);
  value = 0.99;
  game.depart('fast');
  game.advance(5);
  const receipt = game.settle();
  assert.equal(receipt.ratingAfter, 82);
  assert.equal(receipt.ratingDelta, 2);
  assert.equal(receipt.incomeCents, Math.round(urgent.basePriceCents * 1.096));
});

for (const [severityRoll, damage, ratingAfter, incomeCents] of [
  [0.69, 'minor', 78, 1951], [0.70, 'moderate', 75, 1613], [0.95, 'severe', 70, 1060],
]) {
  test(`${damage} damage is sampled at departure and uses its one retained-income fraction`, () => {
    const rolls = [0, severityRoll];
    const game = new DeliverySession(() => {
      assert.ok(rolls.length > 0, 'damage must never be sampled again');
      return rolls.shift();
    });
    game.acceptOrder(game.getState().orders[0].id);
    game.depart('fast');
    assert.equal(rolls.length, 0);
    game.advance(5);
    const receipt = game.settle();
    assert.equal(receipt.damage, damage);
    assert.equal(receipt.ratingAfter, ratingAfter);
    assert.equal(receipt.incomeCents, incomeCents);
    assert.deepEqual(game.settle(), receipt);
  });
}

test('save in transit keeps route, progress and fixed damage without any new random roll', () => {
  const rolls = [0, 0.8];
  const game = new DeliverySession(() => rolls.shift());
  game.acceptOrder(game.getState().orders[0].id);
  game.depart('main');
  game.advance(3);
  const restored = DeliverySession.restore(game.serialize(), () => { throw new Error('must not reroll'); });
  assert.deepEqual(restored.getState(), game.getState());
  restored.advance(7);
  game.advance(7);
  assert.deepEqual(restored.settle(), game.settle());
});

test('restoring a result cannot award it a second time and returns defensive receipts', () => {
  const game = new DeliverySession(() => 0.99);
  const receipt = complete(game);
  const restored = DeliverySession.restore(game.serialize());
  const returned = restored.settle();
  returned.summary.push('tamper');
  returned.incomeCents = 999999;
  assert.deepEqual(restored.settle(), receipt);
  assert.equal(restored.getState().player.cashCents, 12180);
  assert.equal(restored.getState().player.experience, 10);
});

test('snapshots and previews cannot mutate any nested live state', () => {
  const game = new DeliverySession(() => 0.99);
  const snapshot = game.getState();
  snapshot.player.cashCents = -100;
  snapshot.orders[0].basePriceCents = 0;
  snapshot.orders.length = 0;
  game.acceptOrder(game.getState().orders[0].id);
  const routes = game.previewRoutes();
  routes[0].durationSeconds = 0;
  game.depart('fast');
  const active = game.getState();
  active.activeOrder.weightKg = 999;
  active.activeRoute.durationSeconds = 0;
  game.advance(5);
  assert.equal(game.settle().incomeCents, 2180);
});

test('advance ignores negative and nonfinite input, and only moves the delivering phase', () => {
  const game = new DeliverySession(() => 0.99);
  game.advance(8);
  assert.equal(game.getState().elapsedSeconds, 0);
  game.acceptOrder(game.getState().orders[0].id);
  game.depart('fast');
  for (const bad of [-1, NaN, Infinity, -Infinity]) game.advance(bad);
  assert.equal(game.getState().elapsedSeconds, 0);
  game.advance(4.999);
  assert.equal(game.getState().phase, 'delivering');
  game.advance(0.001);
  assert.equal(game.getState().phase, 'arrived');
  game.advance(10);
  assert.equal(game.getState().elapsedSeconds, 5);
});

test('invalid phase transitions cannot award money, switch route or abandon an order', () => {
  const game = new DeliverySession(() => 0.99);
  const id = game.getState().orders[0].id;
  assert.throws(() => game.settle());
  assert.throws(() => game.depart('fast'));
  assert.throws(() => game.returnToOrders());
  assert.throws(() => game.acceptOrder('missing'));
  game.acceptOrder(id);
  assert.throws(() => game.acceptOrder(id));
  assert.throws(() => game.depart('unknown'));
  game.depart('fast');
  assert.throws(() => game.settle());
  assert.throws(() => game.depart('smooth'));
  assert.throws(() => game.returnToOrders());
  assert.equal(game.getState().player.cashCents, 10000);
});

for (const rngValue of [0, 0.99, 1, -1, NaN, Infinity]) {
  test(`candidate generation terminates with five unique feasible capacity-safe orders for RNG ${rngValue}`, () => {
    let calls = 0;
    const game = normalGame(() => { assert.ok(++calls < 200, 'generation must be bounded'); return rngValue; });
    const state = game.getState();
    assert.equal(state.orders.length, 5);
    assert.equal(new Set(state.orders.map(order => order.id)).size, 5);
    assert.ok(state.orders.filter(order => order.weightKg <= 5).length >= 3);
    for (const order of state.orders) {
      assert.ok(order.basePriceCents >= 1500 && order.basePriceCents <= 2500);
      assert.ok(order.weightKg >= 1 && order.weightKg <= 5);
      const restored = DeliverySession.restore(game.serialize(), () => 0.99);
      restored.acceptOrder(order.id);
      assert.ok(restored.previewRoutes().some(route => route.lateSeconds === 0 && route.arrivalTemperature === null));
    }
  });
}

test('rain, distance and tier speed scale duration; fast vehicles respect the two-second floor', () => {
  const game = new DeliverySession(() => 0.99);
  const rainy = DeliverySession.restore(alterSave(game, state => {
    state.orders[0].rain = true;
    state.orders[0].distanceFactor = 1.3;
  }));
  rainy.acceptOrder(rainy.getState().orders[0].id);
  assert.ok(Math.abs(rainy.previewRoutes()[0].durationSeconds - 8.45) < 1e-10);
  assert.equal(rainy.previewRoutes()[0].damageChance, 0.13);
  const quick = DeliverySession.restore(alterSave(game, state => {
    state.player.vehicleTier = 10;
    state.orders[0].distanceFactor = 0.1;
  }));
  quick.acceptOrder(quick.getState().orders[0].id);
  assert.ok(quick.previewRoutes().every(route => route.durationSeconds === 2));
});

test('combined severe damage and lateness respect the per-order delta cap and rating floor', () => {
  const game = new DeliverySession(() => 0.99);
  const prepared = DeliverySession.restore(alterSave(game, state => {
    state.player.rating = 21;
    state.orders[0].type = 'urgent';
    state.orders[0].deadlineSeconds = 8;
  }), (() => { const rolls = [0, 0.99]; return () => rolls.shift(); })());
  prepared.acceptOrder(prepared.getState().orders[0].id);
  prepared.depart('smooth');
  prepared.advance(13);
  const receipt = prepared.settle();
  assert.equal(receipt.damage, 'severe');
  assert.equal(receipt.ratingDelta, -10);
  assert.equal(receipt.ratingAfter, 20);
  assert.equal(receipt.incomeCents, 910);
});

test('experience income uses the level before awarding XP and reaches level two at 100 XP', () => {
  const game = new DeliverySession(() => 0.99);
  const prepared = DeliverySession.restore(alterSave(game, state => {
    state.player.experience = 90;
    state.player.completedOrders = 9;
  }), () => 0.99);
  assert.equal(complete(prepared).incomeCents, 2180);
  assert.equal(prepared.getState().player.level, 2);
  assert.equal(prepared.getState().player.experience, 100);
  prepared.returnToOrders();
  assert.equal(complete(prepared).incomeCents, Math.round(2490 * 1.09 * 1.03));
});

test('corrupt or unknown saves fail clearly instead of poisoning the session', () => {
  const game = new DeliverySession(() => 0.99);
  for (const invalid of ['bad json', 'null', '{}', '{"version":999}']) {
    assert.throws(() => DeliverySession.restore(invalid), /save|存档/i);
  }
  for (const change of [
    state => { state.player.cashCents = -1; },
    state => { state.player.rating = 101; },
    state => { state.player.experience = 100; }, // stale level
    state => { state.player.vehicleTier = 0; },
    state => { state.orders[0].weightKg = 0; },
    state => { state.orders[0].deadlineSeconds = -1; },
    state => { state.orders[0].fragility = 'unknown'; },
    state => { state.phase = 'delivering'; },
    state => { state.orders = []; },
    state => { state.elapsedSeconds = null; },
  ]) assert.throws(() => DeliverySession.restore(alterSave(game, change)), /save|存档/i);
  complete(game);
  assert.throws(() => DeliverySession.restore(alterSave(game, state => {
    state.receipt.newCashCents += 1;
  })), /save|存档/i);
});

test('receipt integrity rejects altered income or rating effects even if wallet is unchanged', () => {
  const game = new DeliverySession(() => 0.99);
  complete(game);
  for (const change of [
    state => { state.receipt.incomeCents += 1; },
    state => { state.receipt.ratingDelta = -3; },
    state => { state.player.experience = 0; state.player.level = 1; },
  ]) assert.throws(() => DeliverySession.restore(alterSave(game, change)), /save|存档/i);
});

test('saving route selection and arrival preserves those phases and never awards early', () => {
  const game = new DeliverySession(() => 0.99);
  game.acceptOrder(game.getState().orders[0].id);
  const routes = DeliverySession.restore(game.serialize(), () => 0.99);
  assert.deepEqual(routes.getState(), game.getState());
  assert.throws(() => routes.settle());
  routes.depart('fast');
  routes.advance(5);
  const arrived = DeliverySession.restore(routes.serialize(), () => { throw new Error('unexpected RNG'); });
  assert.equal(arrived.getState().phase, 'arrived');
  assert.equal(arrived.getState().player.cashCents, 10000);
  assert.equal(arrived.settle().newCashCents, 12180);
});

test('frozen XP thresholds, extrapolated thresholds and the income cap affect real settlements', () => {
  for (const [experience, level, incomeCents] of [
    [0, 1, 2180], [100, 2, 2245], [235, 3, 2311], [417, 4, 2376],
    [663, 5, 2442], [995, 6, 2507], [1443, 7, 2572], [2048, 8, 2638],
    [2865, 9, 2703], [3967, 10, 2769], [5455, 11, 2834], [7464, 12, 2899],
    [115108, 21, 3488], [155495, 22, 3488],
  ]) {
    const game = new DeliverySession(() => 0.99);
    const restored = DeliverySession.restore(alterSave(game, state => {
      state.player.experience = experience;
      state.player.level = level;
    }), () => 0.99);
    assert.equal(complete(restored).incomeCents, incomeCents, `level ${level}`);
  }
});

test('restored route timing, duplicate ids and fixed damage cannot contradict delivery state', () => {
  const game = normalGame();
  assert.throws(() => DeliverySession.restore(alterSave(game, state => {
    state.orders[1].id = state.orders[0].id;
  })), /save|存档/i);
  game.acceptOrder(game.getState().orders[0].id);
  game.depart('fast');
  for (const change of [
    state => { state.activeRoute.durationSeconds += 1; },
    state => { state.elapsedSeconds = 6; },
    (_state, saved) => { saved.fixedDamage = null; },
    (_state, saved) => { saved.sequence = 1; },
  ]) assert.throws(() => DeliverySession.restore(alterSave(game, change)), /save|存档/i);
});
