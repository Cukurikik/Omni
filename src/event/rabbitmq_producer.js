// OMNI Event Layer - RabbitMQ AMQP Node
const amqp = require('amqplib');

async function startRabbitMQProducer() {
    try {
        const connection = await amqp.connect('amqp://localhost');
        const channel = await connection.createChannel();
        const queue = 'omni_task_queue';

        await channel.assertQueue(queue, { durable: true });

        const msg = JSON.stringify({ task: 'Reindex Knowledge Base', priority: 'HIGH' });
        channel.sendToQueue(queue, Buffer.from(msg), { persistent: true });
        
        console.log("OMNI RabbitMQ: Sent %s", msg);

        setTimeout(() => {
            connection.close();
        }, 500);
    } catch (error) {
        console.error("OMNI RabbitMQ Error:", error);
    }
}

startRabbitMQProducer();
