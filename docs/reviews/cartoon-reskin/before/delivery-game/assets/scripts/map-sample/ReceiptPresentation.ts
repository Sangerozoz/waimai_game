import { AcceptedDelivery } from './OrderBook';

/** Session-only presentation state: awards remain exclusively in OrderBook. */
export class ReceiptPresentation {
  private lastShown='';
  observe(active:Readonly<AcceptedDelivery>|null):boolean {
    if(active?.mode!=='done'||!active.receipt)return false;
    const key=`${active.receipt.completedOrders}/${active.receipt.orderId}`;
    if(key===this.lastShown)return false;
    this.lastShown=key;return true;
  }
}
