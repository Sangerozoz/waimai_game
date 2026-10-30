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

    constructor(private storage: StoragePort, private key: string = COUNTY_SAVE_KEY) {}

    get available(): boolean { return this.statusAvailable; }
    get message(): string { return this.statusMessage; }

    load<T>(restore: (serialized: string) => T, fresh: () => T): { session: T; message: string } {
        this.knownGood = null;
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
                const session = restore(raw);
                this.knownGood = raw;
                this.statusMessage = '已恢复县城存档。';
                return { session, message: this.statusMessage };
            } catch (_) {
                prefix = '主存档损坏，原始数据已保留；';
            }
            try {
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
                const session = restore(backup);
                this.knownGood = backup;
                this.statusMessage = prefix + '已从备份恢复。';
                return { session, message: this.statusMessage };
            } catch (_) {
                prefix += '备份存档也已损坏；';
            }
        }
        this.statusMessage = prefix + '开始新的县城配送。';
        return { session: fresh(), message: this.statusMessage };
    }

    save(serialized: string): boolean {
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
            this.storage.setItem(this.key, serialized);
        } catch (_) {
            return this.fail('存档写入失败，未确认保存成功，请检查存储空间或浏览器权限。');
        }
        this.knownGood = serialized;
        this.expectedPrimary = serialized;
        this.statusAvailable = true;
        this.statusMessage = '县城进度已保存。';
        return true;
    }

    private fail(message: string, block = false): false {
        this.statusAvailable = false;
        this.statusMessage = message;
        if (block) this.writeBlocked = true;
        return false;
    }
}
