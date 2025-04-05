import axios from 'axios';
import { EventEmitter } from 'events';

interface Voucher {
    id: string;
    code: string;
    destination: string;
    description: string;
    imageUrl: string;
    expiryDate: Date;
    isHidden: boolean;
}

class VoucherAgent extends EventEmitter {
    private vouchers: Map<string, Voucher> = new Map();
    private static instance: VoucherAgent;
    private isRunning: boolean = false;
    private lastRunTime: Date = new Date();

    private constructor() {
        super();
        this.startPeriodicCollection();
    }

    public static getInstance(): VoucherAgent {
        if (!VoucherAgent.instance) {
            VoucherAgent.instance = new VoucherAgent();
        }
        return VoucherAgent.instance;
    }

    private async collectVouchers(): Promise<void> {
        if (this.isRunning) return;
        this.isRunning = true;

        try {
            // List of popular hotel booking sites to scrape
            const sites = [
                'https://www.booking.com',
                'https://www.expedia.com',
                'https://www.hotels.com',
                'https://www.agoda.com'
            ];

            const newVouchers: Voucher[] = [];
            
            for (const site of sites) {
                try {
                    const response = await axios.get(site);
                    const voucherData = this.extractVoucherData(response.data);
                    newVouchers.push(...voucherData);
                } catch (error) {
                    console.error(`Error scraping ${site}:`, error);
                }
            }

            // Update voucher repository
            this.updateVoucherRepository(newVouchers);
            
            // Clean expired vouchers
            this.cleanExpiredVouchers();
            
            this.emit('vouchersUpdated', Array.from(this.vouchers.values()));
        } catch (error) {
            console.error('Error in voucher collection:', error);
        } finally {
            this.isRunning = false;
            this.lastRunTime = new Date();
        }
    }

    private extractVoucherData(html: string): Voucher[] {
        // Implement intelligent scraping logic here
        // This is a placeholder for the actual implementation
        return [];
    }

    private updateVoucherRepository(newVouchers: Voucher[]): void {
        for (const voucher of newVouchers) {
            if (!this.vouchers.has(voucher.id)) {
                this.vouchers.set(voucher.id, {
                    ...voucher,
                    isHidden: true
                });
            }
        }
    }

    private cleanExpiredVouchers(): void {
        const now = new Date();
        for (const [id, voucher] of this.vouchers.entries()) {
            if (voucher.expiryDate < now) {
                this.vouchers.delete(id);
            }
        }
    }

    private startPeriodicCollection(): void {
        // Run every 4 hours
        setInterval(() => this.collectVouchers(), 4 * 60 * 60 * 1000);
    }

    public async getVouchers(forceRefresh: boolean = false): Promise<Voucher[]> {
        if (forceRefresh || this.shouldRefresh()) {
            await this.collectVouchers();
        }
        return Array.from(this.vouchers.values());
    }

    private shouldRefresh(): boolean {
        const now = new Date();
        const timeSinceLastRun = now.getTime() - this.lastRunTime.getTime();
        return timeSinceLastRun > 4 * 60 * 60 * 1000; // 4 hours
    }

    public async revealVoucher(voucherId: string, userId: string): Promise<string | null> {
        const voucher = this.vouchers.get(voucherId);
        if (!voucher) return null;
        
        // Check user authentication here
        // This is a placeholder for actual authentication logic
        const isAuthenticated = await this.verifyUserAuthentication(userId);
        
        if (!isAuthenticated) {
            throw new Error('User authentication required');
        }

        return voucher.code;
    }

    private async verifyUserAuthentication(userId: string): Promise<boolean> {
        // Implement actual user authentication verification
        // This is a placeholder for the actual implementation
        return true;
    }
}

export default VoucherAgent; 