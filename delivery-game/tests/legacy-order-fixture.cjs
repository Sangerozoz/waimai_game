// Explicitly exercise archived automatic activity semantics; new orders are tested separately.
module.exports=function legacyOrderFixture(OrderBook){
 const accept=OrderBook.prototype.accept;
 OrderBook.prototype.accept=function(id){accept.call(this,id);delete this.accepted.handoff;this.snapshotVersion=3;};
};
