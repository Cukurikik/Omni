<template>
  <div class="listen-moe-player">
    <h3>🎵 OMNI LISTEN-moe Radio</h3>
    <button @click="togglePlay">Play / Pause</button>
  </div>
</template>

<script>
// OMNI MOTHER: LISTEN-moe Vue Audio Player
export default {
  name: 'OmniListenMoePlayer',
  methods: {
    togglePlay() {
      console.log("[OMNI] Toggling radio stream.");
    }
  }
}
</script>

<style scoped>
.listen-moe-player {
  background: #ff76a2;
  color: white;
  padding: 1rem;
  border-radius: 8px;
}
</style>
