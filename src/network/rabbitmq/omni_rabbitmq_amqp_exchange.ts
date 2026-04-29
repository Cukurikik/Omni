// OMNI RabbitMQ AMQP Exchange Engine — Concurrency Layer (TypeScript)
// Absorbing rabbitmq/amqp091 standards
// Deterministic routing key evaluations (Direct and Topic bindings)

export type RabbitResult<T> = {
    ok: boolean;
    value: T | null;
    error: string;
};

export interface Binding {
    queueQueueName: string;
    routingKey: string;
}

export class OmniRabbitmqAmqpExchange {
    private routes_evaluated: number = 0;
    private bindings: Binding[] = [];

    public bind_queue(queue: string, routingKey: string): RabbitResult<boolean> {
        try {
            if (!queue || !routingKey) {
                return { ok: false, value: false, error: "Empty bindings passed." };
            }
            this.bindings.push({ queueQueueName: queue, routingKey });
            return { ok: true, value: true, error: "" };
        } catch (e: any) {
            return { ok: false, value: false, error: `Binding Panic: ${e.message}` };
        }
    }

    private topic_match(bindingKey: string, routingKey: string): boolean {
        // Implements RabbitMQ topic wildcards (* exactly one word, # zero or more words)
        // Zero-mock regex conversion bound representation
        
        let regexStr = "^" + bindingKey
            .split('.')
            .map(part => {
                if (part === "*") return "[^.]+";
                if (part === "#") return ".*";
                return part;
            })
            .join('\\.') + "$";
            
        // Clean up # boundaries
        regexStr = regexStr.replace(/\\.\.\*/g, ".*").replace(/\.\*\\./g, ".*");
        
        const regex = new RegExp(regexStr);
        return regex.test(routingKey);
    }

    public publish_message(routingKey: string, type: 'DIRECT' | 'TOPIC'): RabbitResult<string[]> {
        /*
         * Resolves queue bindings based on Exchange Type math.
         */
        try {
            if (!routingKey) {
                return { ok: false, value: null, error: "Empty message routing path." };
            }

            this.routes_evaluated++;
            let dispatchedQueues: string[] = [];

            for (const b of this.bindings) {
                if (type === 'DIRECT') {
                    if (b.routingKey === routingKey) {
                        dispatchedQueues.push(b.queueQueueName);
                    }
                } else if (type === 'TOPIC') {
                    if (this.topic_match(b.routingKey, routingKey)) {
                        dispatchedQueues.push(b.queueQueueName);
                    }
                }
            }

            // Deduplicate bound matches
            dispatchedQueues = [...new Set(dispatchedQueues)];
            return { ok: true, value: dispatchedQueues, error: "" };
        } catch (e: any) {
            return { ok: false, value: null, error: `Publish Panic: ${e.message}` };
        }
    }

    public diagnostics(): Record<string, any> {
        return {
            engine: "OmniRabbitmqAmqpExchange",
            routes_eval: this.routes_evaluated,
            active_bindings: this.bindings.length,
            status: "Operational"
        };
    }
}
