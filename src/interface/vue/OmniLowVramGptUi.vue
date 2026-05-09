<!-- OMNI Framework - Basic UI for GPT Neo Low VRAM -->
<template>
  <div class="omni-low-vram-ui">
    <header class="header">
      <h1>OMNI GPT-Neo Control Center (Low VRAM Mode)</h1>
      <span class="status" :class="{ 'ready': isReady }">{{ isReady ? 'Model Ready' : 'Loading Model...' }}</span>
    </header>

    <main class="content">
      <div class="input-section">
        <label for="prompt">Input Prompt:</label>
        <textarea id="prompt" v-model="promptText" rows="6" placeholder="Enter text to generate..."></textarea>
      </div>

      <div class="controls">
        <div class="control-group">
          <label>Max Tokens: {{ maxTokens }}</label>
          <input type="range" v-model="maxTokens" min="10" max="200" />
        </div>
        <div class="control-group">
          <label>Temperature: {{ temperature }}</label>
          <input type="range" v-model="temperature" min="0.1" max="1.0" step="0.1" />
        </div>
        <button @click="generateText" :disabled="!isReady || isGenerating" class="btn-generate">
          {{ isGenerating ? 'Generating...' : 'Generate' }}
        </button>
      </div>

      <div class="output-section" v-if="generatedResult">
        <h3>Generated Output:</h3>
        <p class="output-text">{{ generatedResult }}</p>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'OmniLowVramGptUi',
  data() {
    return {
      isReady: false,
      isGenerating: false,
      promptText: '',
      maxTokens: 50,
      temperature: 0.7,
      generatedResult: ''
    }
  },
  mounted() {
    // Simulate model loading in low vram environment
    setTimeout(() => {
      this.isReady = true;
    }, 2000);
  },
  methods: {
    async generateText() {
      if (!this.promptText) return;
      this.isGenerating = true;
      
      // Simulate API call to OMNI backend
      setTimeout(() => {
        this.generatedResult = `${this.promptText} ... [Generated continuation taking Low VRAM constraints into account]`;
        this.isGenerating = false;
      }, 1500);
    }
  }
}
</script>

<style scoped>
.omni-low-vram-ui {
  font-family: 'Inter', sans-serif;
  background-color: #1e1e1e;
  color: #e0e0e0;
  padding: 2rem;
  border-radius: 8px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #333;
  padding-bottom: 1rem;
}
.status.ready { color: #4caf50; }
.input-section textarea {
  width: 100%;
  background-color: #2d2d2d;
  color: white;
  border: 1px solid #444;
  padding: 10px;
  border-radius: 4px;
}
.controls {
  display: flex;
  gap: 20px;
  margin-top: 15px;
}
.btn-generate {
  background-color: #007acc;
  color: white;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  border-radius: 4px;
}
.btn-generate:disabled {
  background-color: #555;
}
.output-text {
  background-color: #252526;
  padding: 15px;
  border-left: 4px solid #007acc;
}
</style>
