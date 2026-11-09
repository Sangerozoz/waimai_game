"""Checks of the standalone planning model; never imports or runs the game."""
import json
from pathlib import Path
from simulate import Sim,mean_batch
BASE=Path(__file__).parent
c=json.loads((BASE/'calibrated-parameters.json').read_text())
# Exact guided milestones are requirements, not implementation mirror checks.
r=Sim(c,'manual',45,seed=23).run(1)
assert r['milestones']['firstCar']['heroOrders']==10
assert r['milestones']['npc1']['heroOrders']==15
assert r['milestones']['firstCar']['cash']==0
assert r['milestones']['npc1']['cash']==0
# Capacity cannot count ineligible 3kg orders in a 2kg vehicle.
assert mean_batch(2,1,(1,2,3))==1
assert 1<=mean_batch(2,10,(1,2,3))<2
# Banked quota caps and offline idempotent accrual.
s=Sim(c);s.completed=1000;s.q=1800;s.credit();assert s.q==1800
s.hero_done=20;s.newnpc({'car':-1,'level':1});s.q=90;s.offline();cash=s.cash;s.offline()
assert s.q==0 and s.cash==cash
# Every reported whole-path bank account must reconcile.
results=json.loads((BASE/'simulation-results.json').read_text())
for row in results:
 assert abs(100+sum(row['gross'].values())-sum(row['spend'].values())-row['final']['cash'])<.1
 assert abs(row['accountingDrift'])<.05
 assert len(row['endEquipment'])==row['final']['npcCount']
 assert all(x['level']<=30 and x['training']<=30 for x in row['endEquipment'])
 # Once post-tutorial NPC exists, no transaction needs a negative balance.
 assert all(t['cash']>=-.01 for t in row['transactions'])
print('PASS: 10/15-order milestones, legal capacity, quota cap, no repeated offline payout, 10 full-path ledgers and asset counts.')
