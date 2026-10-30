import { BillingView } from './DeliveryLedger';
export function billingRows(view:BillingView):Array<{title:string;value:string}> {
  const d=view.today,prefix=view.partialToday?'≥':'',history=view.partialHistory?'≥':'';
  const money=(cents:number):string=>'¥'+(cents/100).toFixed(2),two=(n:number):string=>String(100+n).slice(1);
  const seconds=Math.floor(d.onlineMs/1000),time=`${Math.floor(seconds/3600)}:${two(Math.floor(seconds/60)%60)}:${two(seconds%60)}`;
  return [
    {title:'今日收入',value:prefix+money(d.incomeCents)},
    {title:'今日订单数',value:prefix+d.orders},
    {title:'今日好评',value:prefix+d.good},
    {title:'钱包余额',value:money(view.walletCents)},
    {title:'在线时长',value:(view.partialOnline?'≥':'')+time},
    {title:'配送里程',value:prefix+(d.metres/1000).toFixed(2)+' km'},
    {title:'准时率',value:d.orders&&!view.partialToday?((d.orders-d.late)/d.orders*100).toFixed(1)+'%':'—'},
    {title:'超时',value:prefix+d.late},
    {title:'差评',value:prefix+d.bad},
    {title:'累计配送费',value:history+money(view.totalIncomeCents)},
    {title:'累计完成订单',value:String(view.completedOrders)},
    {title:'单日最高订单数',value:history+view.highestDailyOrders},
  ];
}
