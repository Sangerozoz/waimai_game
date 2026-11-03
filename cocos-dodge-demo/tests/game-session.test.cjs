const { test } = require('node:test');
const assert = require('node:assert/strict');
const { GameSession } = require(process.env.GAME_SESSION_MODULE);

// Catches missing bounds, repeated scoring, scoring after a hit, and stale restart state.
test('player stays fully within the playfield', () => {
  const game = new GameSession();
  game.setPlayerX(10000);
  assert.equal(game.playerX, 300);
  game.setPlayerX(-10000);
  assert.equal(game.playerX, -300);
});

test('avoided obstacles each count once and leave the active set', () => {
  const game = new GameSession(() => 0);
  game.start();
  game.setPlayerX(300);
  for (let frame = 0; frame < 250; frame++) game.step(0.02);
  assert.equal(game.state, 'playing');
  assert.ok(game.score > 0);
  assert.ok(game.obstacles.every(obstacle => obstacle.y > -680));
  const score = game.score;
  game.step(0);
  assert.equal(game.score, score);
});

test('collision ends the run and freezes score and obstacle positions', () => {
  const game = new GameSession(() => 0.5);
  game.start();
  for (let frame = 0; frame < 250; frame++) game.step(0.02);
  assert.equal(game.state, 'game-over');
  const snapshot = JSON.stringify({ score: game.score, obstacles: game.obstacles });
  game.step(10);
  assert.equal(JSON.stringify({ score: game.score, obstacles: game.obstacles }), snapshot);
});

test('restart clears the old run and starts with a centered player', () => {
  const game = new GameSession(() => 0);
  game.start();
  game.setPlayerX(300);
  for (let frame = 0; frame < 250; frame++) game.step(0.02);
  assert.ok(game.score > 0);
  assert.ok(game.obstacles.length > 0);
  game.start();
  assert.equal(game.state, 'playing');
  assert.equal(game.score, 0);
  assert.equal(game.playerX, 0);
  assert.deepEqual(game.obstacles, []);
  game.step(0.1);
  assert.equal(game.obstacles.length, 0);
});
