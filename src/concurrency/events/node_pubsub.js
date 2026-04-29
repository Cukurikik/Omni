const EventEmitter = require('events');

class OmniPubSub extends EventEmitter {
    constructor() {
        super();
        this.setMaxListeners(100);
    }

    publish(topic, payload) {
        if (!topic || typeof topic !== 'string') {
            throw new Error('Invalid topic');
        }
        this.emit(topic, payload);
    }

    subscribe(topic, callback) {
        this.on(topic, callback);
        return () => this.off(topic, callback); // Returns unsubscribe function
    }
}

module.exports = { OmniPubSub };
