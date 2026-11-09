/** Engine-independent V2 ad entitlements. Does not award cash or simulate an SDK. */
export type AdBenefit = 'special' | 'auto';
export type AdOutcome = 'completed' | 'cancelled' | 'failed';
export interface AdTicket { id: string; benefit: AdBenefit; orderId: string | null; expiresAt: number }
export interface RewardedAdSDK {
    /** Adapter must report completed only after the provider's verified reward event. */
    show(ticket: Readonly<AdTicket>, callback: (ticket: AdTicket, outcome: AdOutcome) => void): void;
}
export interface SpecialCandidate { id: string; coins: number; status: 'offered' | 'authorized' | 'consumed' | 'dismissed' }
export interface BatchOrder { id: string; kind: 'normal' | 'special' }
interface TicketRecord extends AdTicket { issuedAt: number; status: 'pending' | 'completed' | 'cancelled' | 'failed' | 'expired' }
interface State {
    version: 1; sequence: number; autoRemainingSeconds: number;
    entries: { id: string; candidateId: string | null }[];
    candidates: SpecialCandidate[]; tickets: TicketRecord[];
    activeBatch: { orders: BatchOrder[]; specialCoins: number | null } | null;
}
function valid(ok: boolean): asserts ok { if (!ok) throw new Error('Invalid rewards-v2 input/state'); }
function id(value: unknown): asserts value is string { valid(typeof value === 'string' && value.trim().length > 0); }
function number(value: unknown): asserts value is number { valid(typeof value === 'number' && Number.isFinite(value) && value >= 0); }
function unit(value: unknown): asserts value is number { number(value); valid(value < 1); }
function clone<T>(value: T): T { return JSON.parse(JSON.stringify(value)); }
function benefit(value: unknown): asserts value is AdBenefit { valid(value === 'auto' || value === 'special'); }
function ticket(value: AdTicket): void {
    valid(!!value && typeof value === 'object'); id(value.id); benefit(value.benefit); number(value.expiresAt);
    if (value.benefit === 'auto') valid(value.orderId === null); else id(value.orderId);
}
export class RewardSession {
    private state: State = { version: 1, sequence: 0, autoRemainingSeconds: 0, entries: [], candidates: [], tickets: [], activeBatch: null };
    get autoRemainingSeconds(): number { return this.state.autoRemainingSeconds; }
    get hasPendingAd(): boolean { return this.state.tickets.some(t => t.status === 'pending'); }
    snapshot(): Readonly<State> { return clone(this.state); }
    serialize(): string { return JSON.stringify(this.state); }
    private next(prefix: string): string { valid(this.state.sequence < Number.MAX_SAFE_INTEGER); return `${prefix}-${++this.state.sequence}`; }

    /** Caller creates a fresh ID only for a genuine lobby open, never scroll/detail return. */
    enterLobby(entryId: string, appearanceRoll: number, priceRoll: number): SpecialCandidate | null {
        id(entryId); unit(appearanceRoll); unit(priceRoll);
        const prior = this.state.entries.find(e => e.id === entryId);
        if (prior) {
            const candidate = this.state.candidates.find(c => c.id === prior.candidateId && (c.status === 'offered' || c.status === 'authorized'));
            return candidate ? clone(candidate) : null;
        }
        // Every genuine entry rolls independently. Preserve paid/pending rights separately
        // from whether this entry displays a candidate. Unpaid unbound offers expire.
        const live = this.state.candidates.find(c => c.status === 'offered' || c.status === 'authorized');
        const protectedOffer = live && (live.status === 'authorized' || this.state.tickets.some(t => t.status === 'pending' && t.orderId === live.id));
        if (live && !protectedOffer) live.status = 'dismissed';
        const candidate = appearanceRoll < 0.8
            ? (protectedOffer ? live! : { id: this.next('special'), coins: 100 + Math.floor(priceRoll * 51), status: 'offered' as const })
            : null;
        if (candidate && !protectedOffer) this.state.candidates.push(candidate);
        this.state.entries.push({ id: entryId, candidateId: candidate ? candidate.id : null });
        return candidate ? clone(candidate) : null;
    }
    expirePending(now: number): void {
        number(now);
        for (const t of this.state.tickets) if (t.status === 'pending' && t.expiresAt <= now) t.status = 'expired';
    }
    /** Timestamps are seconds on a caller-owned stable clock; ttl is explicit SDK policy. */
    requestAd(kind: AdBenefit, orderId: string | null, now: number, ttl: number): AdTicket {
        benefit(kind); number(now); number(ttl); valid(ttl > 0 && Number.isFinite(now + ttl));
        if (kind === 'special') {
            id(orderId);
            valid(this.state.candidates.some(c => c.id === orderId && c.status === 'offered'));
        } else { valid(orderId === null && this.state.autoRemainingSeconds === 0 && this.state.activeBatch === null); }
        // Only one SDK presentation at a time. Expire stale pending presentations first.
        this.expirePending(now);
        valid(!this.state.tickets.some(t => t.status === 'pending'));
        const t: TicketRecord = { id: this.next('ad'), benefit: kind, orderId, expiresAt: now + ttl, issuedAt: now, status: 'pending' };
        this.state.tickets.push(t);
        return { id: t.id, benefit: t.benefit, orderId: t.orderId, expiresAt: t.expiresAt };
    }
    /** Unknown/mismatched/stale callbacks are ignored, malformed callbacks throw. */
    resolveAd(callback: AdTicket, outcome: AdOutcome, now: number): boolean {
        ticket(callback); number(now); valid(['completed', 'cancelled', 'failed'].includes(outcome));
        const t = this.state.tickets.find(t => t.id === callback.id);
        if (!t || t.status !== 'pending' || t.benefit !== callback.benefit || t.orderId !== callback.orderId || t.expiresAt !== callback.expiresAt) return false;
        valid(now >= t.issuedAt);
        if (now >= t.expiresAt) { t.status = 'expired'; return false; }
        t.status = outcome;
        if (outcome !== 'completed') return false;
        if (t.benefit === 'auto') { this.state.autoRemainingSeconds = 600; return true; }
        const candidate = this.state.candidates.find(c => c.id === t.orderId && c.status === 'offered');
        valid(!!candidate); candidate.status = 'authorized'; return true;
    }
    beginBatch(orders: BatchOrder[]): { orders: BatchOrder[]; specialCoins: number | null } {
        valid(this.state.activeBatch === null && Array.isArray(orders) && orders.length > 0);
        const seen = new Set<string>();
        for (const order of orders) {
            valid(!!order); id(order.id); valid(order.kind === 'normal' || order.kind === 'special');
            valid(!seen.has(order.id)); seen.add(order.id);
            // A known special ID cannot be relabelled as a normal order.
            if (order.kind === 'normal') valid(!this.state.candidates.some(c => c.id === order.id));
        }
        let specialCoins: number | null = null;
        if (orders.some(o => o.kind === 'special')) {
            valid(orders.length === 1);
            const c = this.state.candidates.find(c => c.id === orders[0].id && c.status === 'authorized');
            valid(!!c); specialCoins = c.coins; c.status = 'consumed';
        }
        this.state.activeBatch = { orders: clone(orders), specialCoins }; return clone(this.state.activeBatch);
    }
    /** Delivery/settlement belongs to caller. Cancellation does not resurrect an ad candidate. */
    endBatch(): void { valid(this.state.activeBatch !== null); this.state.activeBatch = null; }
    /** Caller MUST advance auto movement by runSeconds only, then hand the in-flight batch to manual. */
    advanceAuto(deltaSeconds: number, foreground: boolean, paused: boolean): { runSeconds: number; manualRequired: boolean } {
        number(deltaSeconds); valid(typeof foreground === 'boolean' && typeof paused === 'boolean');
        valid(!this.state.activeBatch || !this.state.activeBatch.orders.some(o => o.kind === 'special'));
        const runSeconds = foreground && !paused ? Math.min(deltaSeconds, this.state.autoRemainingSeconds) : 0;
        this.state.autoRemainingSeconds -= runSeconds;
        return { runSeconds, manualRequired: this.state.autoRemainingSeconds === 0 };
    }
    static restore(serialized: string): RewardSession {
        valid(typeof serialized === 'string');
        const s: State = JSON.parse(serialized);
        valid(!!s && s.version === 1); number(s.sequence); valid(Number.isSafeInteger(s.sequence));
        number(s.autoRemainingSeconds); valid(s.autoRemainingSeconds <= 600);
        valid(Array.isArray(s.entries) && Array.isArray(s.candidates) && Array.isArray(s.tickets));
        const ids = new Set<string>();
        for (const c of s.candidates) {
            valid(!!c); id(c.id); valid(!ids.has(c.id)); ids.add(c.id);
            valid(Number.isInteger(c.coins) && c.coins >= 100 && c.coins <= 150);
            valid(['offered', 'authorized', 'consumed', 'dismissed'].includes(c.status));
        }
        valid(s.candidates.filter(c => (c.status === 'offered' || c.status === 'authorized')).length <= 1);
        const entries = new Set<string>();
        for (const e of s.entries) {
            valid(!!e); id(e.id); valid(!entries.has(e.id)); entries.add(e.id);
            valid(e.candidateId === null || s.candidates.some(c => c.id === e.candidateId));
        }
        for (const t of s.tickets) {
            ticket(t); number(t.issuedAt); valid(t.issuedAt < t.expiresAt); valid(!ids.has(t.id)); ids.add(t.id);
            valid(['pending', 'completed', 'cancelled', 'failed', 'expired'].includes(t.status));
            if (t.benefit === 'special') valid(s.candidates.some(c => c.id === t.orderId && (t.status !== 'pending' || c.status === 'offered')));
            if (t.benefit === 'auto' && t.status === 'pending') valid(s.autoRemainingSeconds === 0);
        }
        valid(s.tickets.filter(t => t.status === 'pending').length <= 1);
        for (const c of s.candidates) {
            const completed = s.tickets.filter(t => t.benefit === 'special' && t.orderId === c.id && t.status === 'completed');
            valid(completed.length === (c.status === 'offered' || c.status === 'dismissed' ? 0 : 1));
        }
        valid(s.autoRemainingSeconds === 0 || s.tickets.some(t => t.benefit === 'auto' && t.status === 'completed'));
        // Generated IDs must remain below sequence to prevent callback replay via ID reuse.
        for (const value of ids) { valid(/^(special|ad)-[1-9][0-9]*$/.test(value)); valid(Number(value.split('-')[1]) <= s.sequence); }
        const active = s.activeBatch;
        valid(active === null || (!!active && Array.isArray(active.orders)));
        if (active) {
            valid(active.orders.length > 0); const batchIds = new Set<string>();
            for (const o of active.orders) {
                valid(!!o); id(o.id); valid(!batchIds.has(o.id)); batchIds.add(o.id);
                valid(o.kind === 'normal' || o.kind === 'special');
                if (o.kind === 'normal') valid(!s.candidates.some(c => c.id === o.id));
            }
            if (active.orders.some(o => o.kind === 'special')) {
                valid(active.orders.length === 1);
                const c = s.candidates.find(c => c.id === active.orders[0].id && c.status === 'consumed');
                valid(!!c && c.coins === active.specialCoins);
            } else valid(active.specialCoins === null);
        }
        const result = new RewardSession(); result.state = clone(s); return result;
    }
}
