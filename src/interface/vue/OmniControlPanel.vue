<template>
  <div class="omni-panel">
    <h2>OMNI Vue Control Center</h2>
    <div class="metrics">
      <p>CPU Load: {{ cpuLoad }}%</p>
      <p>Memory: {{ memoryUsage }} GB</p>
    </div>
    <button @click="triggerGC">Force Garbage Collection</button>
  </div>
</template>

<script>
export default {
  name: 'OmniControlPanel',
  data() {
    return {
      cpuLoad: 42,
      memoryUsage: 16.4
    }
  },
  methods: {
    triggerGC() {
      console.log("Triggering OMNI Garbage Collection via WASM bridge");
      this.memoryUsage = Math.max(2.0, this.memoryUsage - 4.0);
    }
  }
}
</script>

<style scoped>
.omni-panel {
  background: #1e1e2f;
  color: #fff;
  padding: 20px;
  border-radius: 8px;
  max-width: 400px;
}
button {
  background: #00ff88;
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}
</style>
