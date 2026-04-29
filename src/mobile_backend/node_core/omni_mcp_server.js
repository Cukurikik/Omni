// Omni MCP Server (Node.js/Deno)
// Ref: ErickWendel/erickwendel-contributions-mcp — MIT
const tools = new Map();

function registerTool(name, description, handler) {
  tools.set(name, { name, description, handler });
}

function listTools() {
  return Array.from(tools.values()).map(t => ({ name: t.name, description: t.description }));
}

async function callTool(name, args) {
  const tool = tools.get(name);
  if (!tool) return { error: `Tool '${name}' not found` };
  try {
    const result = await tool.handler(args);
    return { tool: name, result, status: 'success' };
  } catch (e) {
    return { tool: name, error: e.message, status: 'error' };
  }
}

module.exports = { registerTool, listTools, callTool };
