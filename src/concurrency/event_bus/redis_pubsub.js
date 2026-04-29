const Redis = require('ioredis');

class OmniEventBus {
    constructor(redisUrl) {
        this.pub = new Redis(redisUrl);
        this.sub = new Redis(redisUrl);
        this.handlers = new Map();
        
        this.sub.on('message', (channel, message) => {
            const parsed = JSON.parse(message);
            const handler = this.handlers.get(channel);
            if (handler) {
                // Non-blocking async dispatch
                setImmediate(() => handler(parsed).catch(console.error));
            }
        });
    }

    async subscribe(channel, handler) {
        if (!this.handlers.has(channel)) {
            await this.sub.subscribe(channel);
        }
        this.handlers.set(channel, handler);
        return { success: true, channel };
    }

    async publish(channel, payload) {
        const result = await this.pub.publish(channel, JSON.stringify(payload));
        return { success: true, receivers: result };
    }
}

module.exports = { OmniEventBus };
