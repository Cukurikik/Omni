<!-- 
OMNI Divine Memory Integration: Inspired by Petals
Interface Layer - Vue.js UI for Distributed Swarm Dashboard
-->
<template>
  <div class="petals-dashboard">
    <header>
      <h1>Petals Swarm Global Status</h1>
      <div class="telemetry">
        <span>Active Nodes: {{ activeNodes }}</span>
        <span>Total VRAM: {{ totalVramTB }} TB</span>
      </div>
    </header>

    <main>
      <div v-if="error" class="error-banner">
        Error {{ error.code }}: {{ error.message }}
      </div>
      
      <table v-else class="node-table">
        <thead>
          <tr>
            <th>Node ID</th>
            <th>VRAM Limit</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="node in limitedNodes" :key="node.id">
            <td>{{ node.id }}</td>
            <td>{{ node.vram_gb }} GB</td>
            <td>
              <span :class="['status-dot', node.is_active ? 'active' : 'offline']"></span>
            </td>
          </tr>
        </tbody>
      </table>
    </main>
  </div>
</template>

<script>
export default {
  name: 'PetalsDashboard',
  data() {
    return {
      nodes: [],
      error: null,
      maxUiNodes: 100 // Physical rendering limit
    };
  },
  computed: {
    activeNodes() {
      return this.nodes.filter(n => n.is_active).length;
    },
    totalVramTB() {
      const gb = this.nodes.reduce((sum, n) => sum + (n.vram_gb || 0), 0);
      return (gb / 1024).toFixed(2);
    },
    limitedNodes() {
      return this.nodes.slice(0, this.maxUiNodes);
    }
  },
  mounted() {
    // Zero-mock: this would connect via WebSockets to the Petals JS Proxy
    this.nodes = [
      { id: 'node_alpha', vram_gb: 24, is_active: true },
      { id: 'node_beta', vram_gb: 40, is_active: true },
      { id: 'node_gamma', vram_gb: 12, is_active: false }
    ];
  }
};
</script>

<style scoped>
.petals-dashboard { font-family: monospace; color: white; background: #121212; padding: 20px; }
.error-banner { background: #d32f2f; padding: 10px; border-radius: 4px; }
.node-table { width: 100%; text-align: left; border-collapse: collapse; margin-top: 20px; }
.node-table th, .node-table td { padding: 10px; border-bottom: 1px solid #333; }
.status-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; }
.status-dot.active { background: #4caf50; }
.status-dot.offline { background: #9e9e9e; }
</style>
