// OMNI MOTHER: Enka.network Redis Cache (Production Grade)
// Robust Redis-backed caching system for Genshin Impact player profiles.
// Prevents rate-limiting and ensures high availability.

import { createClient, RedisClientType } from 'redis';
import { EnkaResponse } from './omni_enka_types';

export class OmniEnkaCache {
    private client: RedisClientType;
    private readonly ttlSeconds: number;
    private readonly prefix: string = "omni:enka:uid:";
    private isConnected: boolean = false;

    constructor(redisUrl: string = 'redis://localhost:6379', ttlSeconds: number = 300) {
        this.ttlSeconds = ttlSeconds;
        this.client = createClient({
            url: redisUrl,
            socket: {
                reconnectStrategy: (retries) => {
                    console.warn(`[OMNI ENKA CACHE] Redis reconnecting... attempt ${retries}`);
                    return Math.min(retries * 100, 3000); // Exponential backoff max 3s
                }
            }
        });

        this.client.on('error', (err) => {
            console.error('[OMNI ENKA CACHE] Redis Client Error', err);
            this.isConnected = false;
        });

        this.client.on('ready', () => {
            console.log('[OMNI ENKA CACHE] Redis Client Ready');
            this.isConnected = true;
        });
    }

    /**
     * Initializes the Redis connection. Must be called before use.
     */
    public async connect(): Promise<void> {
        if (!this.isConnected) {
            await this.client.connect();
        }
    }

    /**
     * Safely closes the Redis connection.
     */
    public async disconnect(): Promise<void> {
        if (this.isConnected) {
            await this.client.quit();
            this.isConnected = false;
        }
    }

    /**
     * Retrieves profile data from cache.
     * @param uid The Genshin Impact UID
     * @returns The cached EnkaResponse or null if not found
     */
    public async getProfile(uid: string): Promise<EnkaResponse | null> {
        if (!this.isConnected) {
            console.warn('[OMNI ENKA CACHE] Cannot get profile, Redis not connected. Bypassing cache.');
            return null;
        }

        try {
            const key = `${this.prefix}${uid}`;
            const data = await this.client.get(key);
            
            if (data) {
                console.debug(`[OMNI ENKA CACHE] Cache HIT for UID: ${uid}`);
                return JSON.parse(data) as EnkaResponse;
            } else {
                console.debug(`[OMNI ENKA CACHE] Cache MISS for UID: ${uid}`);
                return null;
            }
        } catch (error) {
            console.error(`[OMNI ENKA CACHE] Error retrieving UID ${uid} from cache:`, error);
            return null; // Fallback to fetching directly
        }
    }

    /**
     * Stores profile data into cache with TTL.
     * @param uid The Genshin Impact UID
     * @param data The profile data to cache
     */
    public async setProfile(uid: string, data: EnkaResponse): Promise<void> {
        if (!this.isConnected) {
            console.warn('[OMNI ENKA CACHE] Cannot set profile, Redis not connected.');
            return;
        }

        try {
            const key = `${this.prefix}${uid}`;
            const serialized = JSON.stringify(data);
            await this.client.setEx(key, this.ttlSeconds, serialized);
            console.debug(`[OMNI ENKA CACHE] Stored UID: ${uid} in cache with TTL ${this.ttlSeconds}s`);
        } catch (error) {
            console.error(`[OMNI ENKA CACHE] Error setting UID ${uid} in cache:`, error);
        }
    }

    /**
     * Invalidates a specific UID from the cache.
     */
    public async invalidateProfile(uid: string): Promise<void> {
        if (this.isConnected) {
            const key = `${this.prefix}${uid}`;
            await this.client.del(key);
            console.log(`[OMNI ENKA CACHE] Invalidated cache for UID: ${uid}`);
        }
    }
}
