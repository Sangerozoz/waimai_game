const {test}=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const {newCountyPlayer,countyDamageChance,countySettlement}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'CountyRules.js'));
const offer={id:'first',feeCents:2000,type:'normal',fragility:'durable',demand:'none'};
const outcome={displaySeconds:1200,deadlineSeconds:1500,damage:'none',doorAnswer:null};
test('the real county first delivery credits 21.80 yuan and ten XP once to the 100 yuan opening balance',()=>{
 const before=newCountyPlayer(),{player,receipt}=countySettlement(before,offer,outcome);
 assert.equal(before.cashCents,10000);assert.equal(player.cashCents,12180);assert.equal(player.experience,10);
 assert.equal(receipt.incomeCents,2180);assert.equal(player.completedOrders,1);assert.equal(player.rating,80);
});
test('late severe damage and a disturbed doorstep request use one capped rating penalty and one income reduction',()=>{
 const before={...newCountyPlayer(),rating:21};
 const {player,receipt}=countySettlement(before,{...offer,type:'urgent',fragility:'fragile',demand:'door'},{...outcome,displaySeconds:1800,damage:'severe',doorAnswer:false});
 assert.equal(receipt.ratingDelta,-10);assert.equal(player.rating,20);assert.equal(receipt.incomeCents,910);
 assert.equal(receipt.lateSeconds,300);
});
test('all three positive conditions cap at +6 and income uses new rating but the old experience level',()=>{
 const before={...newCountyPlayer(),experience:90,completedOrders:9};
 const {player,receipt}=countySettlement(before,{...offer,type:'urgent',fragility:'fragile',demand:'door'},{...outcome,doorAnswer:true});
 assert.equal(receipt.ratingDelta,6);assert.equal(player.rating,86);assert.equal(receipt.incomeCents,2216);
 assert.equal(player.experience,100);assert.equal(player.level,2);
});
test('formal risk comes from meal fragility and road preference rather than trip animation length',()=>{
 assert.equal(countyDamageChance('fast','fragile'),.45);assert.equal(countyDamageChance('smooth','durable'),.01);
 assert.equal(countyDamageChance('main','normal'),.10);
});

test('the fifth receipt earns at departure Lv1 and unlocks Lv2 at fifty XP',()=>{
 const fifth=countySettlement({...newCountyPlayer(),experience:40,completedOrders:4},offer,outcome);
 assert.equal(fifth.receipt.levelBefore,1);assert.equal(fifth.receipt.incomeCents,2180);assert.equal(fifth.player.experience,50);assert.equal(fifth.player.level,2);
 assert.equal(countySettlement(fifth.player,offer,outcome).receipt.incomeCents,2245);
});

test('county levels retain later increments while the original game thresholds stay unchanged',()=>{
 const {countyExperienceLevel,COUNTY_VEHICLES}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'CountyConfig.js'));
 const {getExperienceLevel,VEHICLES}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'../domain/GameConfig.js'));
 for(const [xp,level] of [[0,1],[40,1],[49,1],[50,2],[184,2],[185,3],[366,3],[367,4]])assert.equal(countyExperienceLevel(xp),level);
 assert.equal(getExperienceLevel(50),1);assert.equal(VEHICLES[1].upgradeFeeCents,32000);
 assert.equal(COUNTY_VEHICLES[0].speedKph,12);assert.equal(COUNTY_VEHICLES[1].speedKph,13.2);assert.equal(COUNTY_VEHICLES[1].capacityKg,8);
});
