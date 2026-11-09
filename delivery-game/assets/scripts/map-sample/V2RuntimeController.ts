import { _decorator, Component, Game, game, sys } from 'cc';
import { V2EconomySnapshot } from '../domain/V2EconomySession';
import { V2DispatchSession, EmergencyLoanStatus } from '../domain/V2DispatchSession';
import { CityData, Preference } from './MapTypes';
import { V2RouteOrder } from './V2RouteSession';
import { V2GameSession } from './V2GameSession';
import { RewardedAdSDK } from '../rewards-v2/RewardSession';
import { V2RuntimeStore, V2WriterPort, SingleSlotStorage } from './V2RuntimeStore';


const { ccclass, property } = _decorator;
type EconomyCommand = Parameters<V2DispatchSession['command']>[0];
type Orders = V2RouteOrder[];
export interface V2RuntimePorts {
    city: CityData;
    ads: RewardedAdSDK;
    /** Stable absolute seconds shared with the ad adapter, never frame delta. */
    nowSeconds: () => number;
    storage?: SingleSlotStorage;
    writer?: V2WriterPort;
}

/** Opt-in component. No scene, SDK, old UI or legacy storage is wired implicitly. */
@ccclass('V2RuntimeController')
export class V2RuntimeController extends Component {
    @property enableV2 = false;
    public lastError = '';
    private ports: V2RuntimePorts | null = null;
    private store: V2RuntimeStore | null = null;
    private openingStore: V2RuntimeStore | null = null;
    private live: V2GameSession | null = null;
    private foreground = true;
    private paused = false;
    private frame = 0;
    private opening = false;
    private destroyed = false;
    private bound = false;
    private generation = 0;
    // Every published live state has these exact, successfully committed bytes.
    private committed: string | null = null;
    private publishedAtSeconds = -Infinity;
    private static readonly DRIVE_INTERVAL_SECONDS = 1 / 30;
    private readonly diagnosedErrors = new WeakSet<object>();
    private lastDiagnosticKey = '';
    /** Bounded code-location diagnostics only; never log commands, snapshots or storage. */
    private recordRuntimeError(error: unknown, stage: string): void {
        try { this.lastError = String(error); }
        catch { this.lastError = 'V2运行操作失败'; }
        try {
            if (error !== null && (typeof error === 'object' || typeof error === 'function')) {
                if (this.diagnosedErrors.has(error)) return;
                this.diagnosedErrors.add(error);
            }
            const frames = error instanceof Error && typeof error.stack === 'string'
                ? error.stack.split('\n').filter(line => /^\s*at\s/.test(line)).slice(0, 8)
                    .map(line => line.replace(/[?#][^\s)]*/g, '[redacted]').slice(0, 240)) : [];
            const errorType = error instanceof TypeError ? 'TypeError' : error instanceof RangeError ? 'RangeError' : error instanceof Error ? 'Error' : 'ThrownValue';
            const diagnostic = { stage, errorType, frames }, key = JSON.stringify(diagnostic);
            if (key !== this.lastDiagnosticKey) {
                this.lastDiagnosticKey = key;
                console.error('[V2 runtime failure]', diagnostic);
            }
        } catch { /* Diagnostics must not replace the original transaction failure. */ }
    }
    private dayKey(nowMs:number):string {
        const d=new Date(nowMs);return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
    }
    get ledgerQuery() {
        const nowMs=Math.round(this.ports!.nowSeconds()*1000),recentDayKeys:string[]=[];
        for(let i=0;i<7;i++){const d=new Date(nowMs);d.setDate(d.getDate()-i);recentDayKeys.push(this.dayKey(d.getTime()));}
        return {todayDayKey:this.dayKey(nowMs),recentDayKeys};
    }
    get batchSummary() {
        const state=(this.snapshot?.economy as V2EconomySnapshot|undefined)?.state,t=this.tripState,base=t?.batchAccounting;
        if(!state||!t||!base)return null;
        const incomeCents=state.ledger.entries.filter(e=>base.orderIds.some(id=>e.id===`order:${id}`)).reduce((n,e)=>n+e.amountCents,0);
        const supplyCents=(base.end?.supplySpentCents??t.supplySpentCents)-base.supplySpentCentsStart;
        const inventoryUsed=Object.values(base.end?.inventoryUsed??t.inventoryUsed).reduce((n,count)=>n+count,0)-Object.values(base.inventoryUsedStart).reduce((n,count)=>n+count,0);
        return {incomeCents,supplyCents,netCents:incomeCents-supplyCents,inventoryUsed};
    }

    configure(ports: V2RuntimePorts): void {
        if (this.live || this.opening || this.destroyed) throw new Error('运行中不能更换V2端口');
        this.ports = ports;
    }
    startNew(): Promise<void> { return this.open('new'); }
    startOrContinue(): Promise<void> { return this.open('continue'); }
    /** Compatibility guards only: players cannot replace existing progress. */
    startOver(): Promise<void> { return Promise.reject(new Error('不支持重新开始，请继续当前进度')); }
    restart(): void { throw new Error('不支持重新开始，请继续当前进度'); }
    restoreSaved(): Promise<void> { return this.open('restore'); }
    get snapshot(): ReturnType<V2DispatchSession['snapshot']> | null { return this.live?.snapshot() || null; }
    get ready(): boolean {
        if (!this.enableV2 || !this.live || !this.store || this.destroyed) return false;
        if (!this.store.writable) { this.lastError = this.store.message || '进度写入已停止，请重新打开游戏'; return false; }
        return true;
    }
    private async open(mode: 'new' | 'restore' | 'continue'): Promise<void> {
        if (!this.enableV2 || !this.ports || this.live || this.opening || this.destroyed) throw new Error('请先显式启用并配置V2端口');
        this.opening = true;
        const ports = this.ports;
        const store = new V2RuntimeStore(ports.storage || {
            getItem: key => sys.localStorage.getItem(key), setItem: (key, value) => sys.localStorage.setItem(key, value),
            removeItem: key => sys.localStorage.removeItem(key),
        }, ports.writer);
        this.openingStore = store;
        try {
            const session = await store.open(mode, raw => V2GameSession.restore(ports.city, raw), () => new V2GameSession(ports.city, ports.nowSeconds()));
            if (this.destroyed || !this.enableV2) throw new Error('V2组件已停用');
            // Persist a new session and synchronize the restored clock before publication.
            this.frame = session.snapshot().frame.sequence;
            const nowSeconds=ports.nowSeconds();
            session.dispatch.setLedgerDayKeyResolver(atMs=>this.dayKey(atMs));
            session.dispatch.setLedgerContext({nowMs:Math.round(nowSeconds*1000),dayKey:this.dayKey(Math.round(nowSeconds*1000))});
            session.tick(++this.frame, nowSeconds, false, true);
            const serialized = session.serialize();
            store.commit(serialized);
            this.committed = serialized; this.publishedAtSeconds = nowSeconds;
            this.store = store; this.live = session; this.lastError = '';
            game.on(Game.EVENT_HIDE, this.onHide, this); game.on(Game.EVENT_SHOW, this.onShow, this); this.bound = true;
        } catch (error) { store.close(); this.lastError = String(error); throw error; }
        finally { this.openingStore = null; this.opening = false; }
    }
    private mutate<T>(action: (session: V2GameSession, nowSeconds:number) => T, synchronizeClock = true): T {
        if (!this.ready || !this.ports || !this.live || !this.store || this.committed === null) throw new Error(this.lastError || 'V2尚未就绪或保存已停止');
        let stage = 'transaction.restore';
        try {
            const candidate = V2GameSession.restore(this.ports.city, this.committed!, { preserveClock: true });
            candidate.dispatch.setLedgerDayKeyResolver(atMs=>this.dayKey(atMs));
            // Account for elapsed operating time with the pre-command assets/quota.
            // In particular, a completion must not replenish quota retroactively.
            stage = 'transaction.clock-context';
            const nowSeconds=this.ports.nowSeconds();
            candidate.dispatch.setLedgerContext({nowMs:Math.round(nowSeconds*1000),dayKey:this.dayKey(Math.round(nowSeconds*1000))});
            stage = 'transaction.sync-tick';
            if (synchronizeClock) candidate.tick(++this.frame, nowSeconds, this.foreground, this.paused);
            stage = 'transaction.action';
            const result = action(candidate,nowSeconds);
            stage = 'transaction.serialize';
            const serialized = candidate.serialize();
            stage = 'transaction.validate';
            V2GameSession.restore(this.ports.city, serialized, { preserveClock: true });
            stage = 'transaction.commit';
            if (serialized !== this.committed) this.store.commit(serialized);
            // Publish and update the cache only after validation and durable commit.
            this.committed = serialized; this.publishedAtSeconds = nowSeconds;
            this.live = candidate;
            this.lastError = '';
            return result;
        } catch (error) { this.recordRuntimeError(error, stage); throw error; }
    }
    get tripState() { return this.live?.tripState || null; }
    supplyOptions() { return this.live?.supplyOptions() || []; }
    supply(kind: Parameters<V2GameSession['supply']>[0],source:'purchase'|'inventory'='purchase'): void {
        this.mutate(session => session.supply(kind,source));
    }
    configureAutoSupply(policy: Parameters<V2GameSession['configureAutoSupply']>[0]): void {
        this.mutate(session => session.configureAutoSupply(policy));
    }
    get routeSnapshot() { return this.live?.routeSnapshot || null; }
    get routeMotion() { return this.live?.routeMotion || null; }
    /** Signed active-delivery units/effects; a legacy active batch remains kilograms. */
    get deliveryEffects() { return this.live?.dispatch.deliveryEffects || null; }
    /** Current owned-asset effects for the next unsigned slot batch. */
    get nextBatchEffects() { return this.live?.dispatch.nextBatchEffects || null; }
    get emergencyLoanStatus(): EmergencyLoanStatus {
        return this.live?.dispatch.emergencyLoanStatus || { phase: 'unavailable', sequence: 0, loanSequence: null, returnVehicleIds: [], canStartBatch: false, reason: '游戏尚未载入' };
    }
    vehicleEffects(vehicleId:string) { return this.live?.dispatch.vehicleEffectProjection(vehicleId) || null; }
    riderEffects(riderId:string) { return this.live?.dispatch.riderEffectProjection(riderId) || null; }
    vehicleUpgradeQuote(vehicleId:string) { return this.live?.dispatch.vehicleUpgradePrice(vehicleId)||null; }
    riderUpgradeQuote(riderId:string) { return this.live?.dispatch.riderUpgradePrice(riderId)||null; }
    normalCandidates(count = 8) { if (!this.live) return []; return this.live.normalCandidates(count); }
    /** Read-only preview using the same signed contract as acceptance; never saves or accepts live orders. */
    quoteCandidates(orders: Orders) {
        if (!this.live || !this.ports) throw new Error('V2尚未就绪');
        const draft = V2GameSession.restore(this.ports.city, this.committed!, { preserveClock: true });
        draft.dispatch.setLedgerDayKeyResolver(atMs=>this.dayKey(atMs));
        const quotes = draft.acceptBatch(orders);
        return { quotes, totalIncomeCents: quotes.reduce((sum, quote) => sum + quote.incomeCents, 0),
            deadlines: draft.tripState.orders.map(order => ({ id: order.id, gameSeconds: order.deadlineGameSeconds })) };
    }
    specialCandidate(id: string) { return this.live?.specialCandidate(id) || null; }
    routeChoices() { return this.live?.routeChoices() || []; }
    private requireForegroundTripCommand(): void {
        if (!this.foreground) throw new Error('后台不能操作配送，请回到游戏后继续');
        // Detail/supply pages deliberately pause hero time. Their explicit commands
        // may select the next action; only returning home resumes its clock.
    }
    beginTrip(preference: Preference = 'fast'): void {
        this.mutate(session => { this.requireForegroundTripCommand(); session.beginTrip(preference); });
    }
    pickup(): void { this.mutate(session => { this.requireForegroundTripCommand(); session.pickup(); }); }
    continueTrip(): void {
        // mutate synchronizes the old ready interval before changing phase. Never
        // apply the time spent waiting at the merchant to the newly started leg.
        this.mutate(session => { this.requireForegroundTripCommand(); session.continueTrip(); });
    }
    command(command: EconomyCommand): ReturnType<V2DispatchSession['command']> { return this.mutate(session => session.command(command)); }
    stopAutomation(): void { this.mutate(session => session.dispatch.stopAutomation()); }
    resumeAutomation(): void { this.mutate(session => session.dispatch.resumeAutomation()); }
    acceptBatch(orders: Orders): ReturnType<V2GameSession['acceptBatch']> { return this.mutate(session => session.acceptBatch(orders)); }
    completeDelivery(id: string, arrivalToken: string): ReturnType<V2DispatchSession['completeDelivery']> {
        return this.mutate(session => session.completeDelivery(id, arrivalToken));
    }
    cancelDelivery(id: string): void { this.mutate(session => session.cancelDelivery(id)); }
    enterLobby(entryId: string, appearanceRoll: number, priceRoll: number): ReturnType<V2DispatchSession['enterLobby']> {
        return this.mutate(session => session.dispatch.enterLobby(entryId, appearanceRoll, priceRoll));
    }
    requestAd(kind: 'special' | 'auto', orderId: string | null, ttlSeconds: number): void {
        if (!this.ports) throw new Error('广告端口未配置');
        const ports = this.ports, generation = this.generation;
        const ticket = this.mutate((session,nowSeconds) => session.dispatch.requestAd(kind, orderId, nowSeconds, ttlSeconds));
        try {
            ports.ads.show(Object.freeze({ ...ticket }), (returned, outcome) => {
                if (!this.ready || generation !== this.generation) return;
                try { this.mutate((session,nowSeconds) => session.dispatch.resolveAd(returned, outcome, nowSeconds)); }
                catch (error) { this.lastError = String(error); }
            });
        } catch (error) {
            this.mutate((session,nowSeconds) => session.dispatch.resolveAd(ticket, 'failed', nowSeconds));
            this.lastError = String(error);
            throw error; // Let the caller display SDK unavailability as failure, never success.
        }
    }
    /** Only hero travel/actions pause; the session continues NPC wall-clock settlement. */
    setPaused(paused: boolean): void {
        if (this.paused === paused) return;
        this.drive(true); this.paused = paused; this.drive(true);
    }
    update(_delta: number): void { this.drive(); }
    private drive(force = false): void {
        if (!this.enableV2 || !this.live || !this.ports || this.destroyed) return;
        let stage = 'drive.clock';
        try {
            const nowSeconds = this.ports.nowSeconds();
            // Coalesce render callbacks, not elapsed time. Commands and lifecycle edges
            // bypass this gate; the session still receives the complete absolute clock.
            // A clock rollback must reach domain validation/rebasing instead of stalling.
            if (!force && nowSeconds >= this.publishedAtSeconds &&
                nowSeconds - this.publishedAtSeconds < V2RuntimeController.DRIVE_INTERVAL_SECONDS) return;
            stage = 'drive.tick';
            this.mutate((session,nowSeconds) => session.tick(++this.frame, nowSeconds, this.foreground, this.paused), false);
        }
        catch (error) { this.recordRuntimeError(error, stage); }
    }
    private onHide(): void { this.foreground = false; this.drive(true); }
    private onShow(): void { this.foreground = true; this.drive(true); }
    onDestroy(): void {
        this.destroyed = true; this.generation++;
        if (this.bound) { game.off(Game.EVENT_HIDE, this.onHide, this); game.off(Game.EVENT_SHOW, this.onShow, this); }
        this.openingStore?.close(); this.store?.close(); this.live = null; this.committed = null;
    }
}
