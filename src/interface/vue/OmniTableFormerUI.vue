<!-- OMNI Framework - Vue.js Interface for TableFormer -->
<template>
  <div class="omni-tableformer-ui">
    <h2>OMNI TableFormer Extractor</h2>
    <div v-if="loading" class="loader">Processing structural data...</div>
    
    <table v-if="!loading && tableData.length > 0" class="omni-table">
      <thead>
        <tr>
          <th v-for="header in headers" :key="header">{{ header }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, rowIndex) in tableData" :key="rowIndex">
          <td v-for="(cell, cellIndex) in row" :key="cellIndex">{{ cell }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'OmniTableFormerUI',
  data() {
    return {
      loading: true,
      headers: [],
      tableData: []
    }
  },
  mounted() {
    // Simulate fetching extracted table data from OMNI backend
    setTimeout(() => {
      this.headers = ['Entity', 'Q1 Revenue', 'Q2 Revenue'];
      this.tableData = [
        ['Alpha Corp', '$1.2M', '$1.4M'],
        ['Beta Ltd', '$0.8M', '$0.9M']
      ];
      this.loading = false;
    }, 1500);
  }
}
</script>

<style scoped>
.omni-tableformer-ui {
  font-family: 'Inter', sans-serif;
  color: #c9d1d9;
  background-color: #0d1117;
  padding: 20px;
}
.omni-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}
.omni-table th, .omni-table td {
  border: 1px solid #30363d;
  padding: 10px;
  text-align: left;
}
.omni-table th {
  background-color: #161b22;
  color: #58a6ff;
}
</style>
