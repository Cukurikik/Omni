// OMNI UI & Admin Layer
// Vue.js Monitoring Dashboard
// Based on vuejs/vue. Provides a reactive frontend for Omni's telemetry stream.

import { ref, onMounted, onUnmounted } from 'vue';

export const OmniVueMonitoringDashboard = {
    name: 'OmniMonitoring',
    template: `
        <div class="omni-monitor">
            <h2>OMNI Universal Engine Telemetry</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>CPU Usage</h3>
                    <div class="value" :class="{ 'danger': metrics.cpu > 85 }">{{ metrics.cpu.toFixed(1) }}%</div>
                </div>
                <div class="metric-card">
                    <h3>VRAM Allocation</h3>
                    <div class="value">{{ metrics.vram_gb.toFixed(2) }} GB</div>
                </div>
                <div class="metric-card">
                    <h3>Active Tensor Allocs</h3>
                    <div class="value">{{ metrics.tensor_count }}</div>
                </div>
                <div class="metric-card">
                    <h3>Job Queue Depth</h3>
                    <div class="value">{{ metrics.queue_depth }}</div>
                </div>
            </div>
            
            <div class="log-stream">
                <h3>Live Logs</h3>
                <ul>
                    <li v-for="(log, idx) in logs" :key="idx" :class="log.level">
                        [{{ log.timestamp }}] {{ log.message }}
                    </li>
                </ul>
            </div>
        </div>
    `,
    setup() {
        const metrics = ref({
            cpu: 0,
            vram_gb: 0,
            tensor_count: 0,
            queue_depth: 0
        });

        const logs = ref([]);
        let eventSource = null;

        onMounted(() => {
            console.log("OMNI Vue: Mounting telemetry dashboard...");
            
            // In production, this connects to the Omni Go Telemetry Server via SSE
            eventSource = new EventSource('/api/v1/telemetry/stream');
            
            eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'metric') {
                    metrics.value = data.payload;
                } else if (data.type === 'log') {
                    logs.value.unshift(data.payload);
                    if (logs.value.length > 50) logs.value.pop();
                }
            };
            
            eventSource.onerror = () => {
                console.error("OMNI Vue: Telemetry stream disconnected. Retrying...");
            };
        });

        onUnmounted(() => {
            if (eventSource) {
                eventSource.close();
            }
        });

        return {
            metrics,
            logs
        };
    }
};
