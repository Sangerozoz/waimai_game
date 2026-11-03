import { isTripProfile } from './TripClock';
export const COUNTY_SAVE_KEY = 'delivery-county-save-v1';

export interface StoragePort {
    getItem(key: string): string | null;
    setItem(key: string, value: string): void;
}

export class CountySaveStore {
    private knownGood: string | null = null;
    private statusAvailable = true;
    private statusMessage = '';
    private writeBlocked = false;
    private primaryKnown = false;
    private expectedPrimary: string | null = null;

    private revision=0;
    private lastCommand='';
    private pending:{id:string;serialized:string;expectedRevision:number}|null=null;
    constructor(private storage: StoragePort, private key: string = COUNTY_SAVE_KEY, private canWrite:()=>boolean=()=>false) {}
    get currentRevision():number{return this.revision;}
    private decode<T>(raw:string,restore:(serialized:string)=>T):T {
        const value=JSON.parse(raw);
        if(value?.format!=='county-commit')return restore(raw);
        if(value.version!==1||!Number.isSafeInteger(value.revision)||value.revision<1||typeof value.commandId!=='string'||!value.commandId||typeof value.snapshot!=='string')throw new Error('无效提交记录');
        const session=restore(value.snapshot);this.revision=value.revision;this.lastCommand=value.commandId;return session;
    }

    get available(): boolean { return this.statusAvailable&&this.canWrite(); }
    get message(): string { return this.statusMessage; }

    load<T>(restore: (serialized: string) => T, fresh: () => T): { session: T; message: string } {
        this.knownGood = null;
        this.revision=0;this.lastCommand='';this.pending=null;
        this.statusAvailable = true;
        this.writeBlocked = false;
        this.primaryKnown = false;
        let raw: string | null;
        try {
            raw = this.storage.getItem(this.key);
        } catch (_) {
            this.fail('存档读取失败，已暂停保存以保护原数据。', true);
            return { session: fresh(), message: this.statusMessage };
        }
        this.primaryKnown = true;
        this.expectedPrimary = raw;
        let prefix = '';
        if (raw !== null) {
            try {
                const session = this.decode(raw,restore);
                this.knownGood = raw;
                this.statusMessage = '已恢复县城存档。';
                return { session, message: this.statusMessage };
            } catch (_) {
                // A newer version is not corruption: preserve it and prohibit writes.
                let future = false;
                try { const value = JSON.parse(raw); future = this.futureVersion(value); } catch (_) {}
                if (future) {
                    this.fail('存档版本较新，已暂停保存以保护原数据。', true);
                    return { session: fresh(), message: this.statusMessage };
                }
                prefix = '主存档损坏，原始数据已保留；';
            }
            try {
                if(!this.canWrite())throw new Error('只读');
                this.storage.setItem(this.key + ':corrupt', raw);
            } catch (_) {
                prefix = '主存档损坏，无法保留原始数据，已暂停保存以避免覆盖；';
                this.fail(prefix, true);
            }
        }
        let backup: string | null;
        try {
            backup = this.storage.getItem(this.key + ':backup');
        } catch (_) {
            this.fail(prefix + '备份读取失败，已暂停保存以保护原数据。', true);
            return { session: fresh(), message: this.statusMessage };
        }
        if (backup !== null) {
            try {
                const session = this.decode(backup,restore);
                this.knownGood = backup;
                this.statusMessage = prefix + '已从备份恢复。';
                return { session, message: this.statusMessage };
            } catch (_) {
                let future = false;
                try { const value = JSON.parse(backup); future = this.futureVersion(value); } catch (_) {}
                if (future) {
                    this.fail(prefix + '备份存档版本较新，已暂停保存以保护原数据。', true);
                    return { session: fresh(), message: this.statusMessage };
                }
                prefix += '备份存档也已损坏；';
            }
        }
        this.statusMessage = prefix + '开始新的县城配送。';
        return { session: fresh(), message: this.statusMessage };
    }

    save(serialized: string, commandId?:string, expectedRevision=this.revision): boolean {
        if(!this.canWrite())return this.fail('当前页面只读：需要安全写入权限，请关闭其他游戏页后重新打开。',true);
        if(commandId&&commandId===this.lastCommand)return serialized===this.decodeSnapshot(this.knownGood);
        if(!this.pending)this.pending={id:commandId||`${this.revision+1}-${Date.now()}-${Math.random().toString(36).slice(2)}`,serialized,expectedRevision};
        const pending=this.pending;
        if(pending.serialized!==serialized||pending.expectedRevision!==this.revision)return this.fail('有未完成提交或版本冲突，请重试原操作或重新打开。');
        const committed=JSON.stringify({format:'county-commit',version:1,revision:this.revision+1,commandId:pending.id,snapshot:serialized});
        if (this.writeBlocked) return false;
        let current: string | null;
        try {
            current = this.storage.getItem(this.key);
        } catch (_) {
            return this.fail('存档读取失败，本次保存已取消以保护原数据。');
        }
        if (!this.primaryKnown) {
            if (current !== null) {
                return this.fail('请先读取并校验已有存档，已暂停保存以避免覆盖。', true);
            }
            this.primaryKnown = true;
            this.expectedPrimary = null;
        } else if (current !== this.expectedPrimary) {
            return this.fail('存档已被其他操作变更，已暂停保存，请重新读取。', true);
        }
        if (this.knownGood !== null && this.knownGood !== serialized) {
            try {
                this.storage.setItem(this.key + ':backup', this.knownGood);
            } catch (_) {
                return this.fail('备份写入失败，未覆盖原存档，请检查存储空间或浏览器权限。');
            }
        }
        try {
            // The original pre-envelope snapshot is retained once, before migration.
            if(this.expectedPrimary!==null&&!this.isCommit(this.expectedPrimary)&&this.storage.getItem(this.key+':pre-foundation')===null)this.storage.setItem(this.key+':pre-foundation',this.expectedPrimary);
            this.storage.setItem(this.key, committed);
        } catch (_) {
            return this.fail('存档写入失败，未确认保存成功，请检查存储空间或浏览器权限。');
        }
        this.knownGood = committed;
        this.expectedPrimary = committed;
        this.revision++;this.lastCommand=pending.id;this.pending=null;
        this.statusAvailable = true;
        this.statusMessage = '县城进度已保存。';
        return true;
    }

    private futureVersion(value:any):boolean {
        if(!value||typeof value!=='object')return false;
        if(value.format==='county-commit') {
            if(value.version!==1)return true;
            try{return this.futureVersion(JSON.parse(value.snapshot));}catch{return false;}
        }
        return Number.isSafeInteger(value.version)&&value.version>7 || value.vehicles!==undefined&&value.vehicles?.version!==1 || value.billing?.version>2 || value.active?.mileage!==undefined&&value.active.mileage?.profile!=='road-increment-v1' || value.active?.tripProfile!==undefined&&!isTripProfile(value.active.tripProfile);
    }
    private isCommit(raw:string):boolean {try{return JSON.parse(raw)?.format==='county-commit';}catch{return false;}}
    private decodeSnapshot(raw:string|null):string|null {
        if(raw===null)return null;
        try{const value=JSON.parse(raw);return value.format==='county-commit'?value.snapshot:raw;}catch{return null;}
    }
    private fail(message: string, block = false): false {
        this.statusAvailable = false;
        this.statusMessage = message;
        if (block) this.writeBlocked = true;
        return false;
    }
}
