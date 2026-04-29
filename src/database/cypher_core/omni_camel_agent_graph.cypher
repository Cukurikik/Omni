-- Omni CAMEL Agent Interaction Graph (Cypher)
-- Ref: camel-ai/multi-agent-streamlit-ui
CREATE CONSTRAINT camel_agent_name IF NOT EXISTS FOR (a:Agent) REQUIRE a.name IS UNIQUE;
CREATE (p:Agent {name: 'planner', role: 'planner'})
CREATE (a:Agent {name: 'assistant', role: 'assistant'})
CREATE (c:Agent {name: 'critic', role: 'critic'})
CREATE (u:Agent {name: 'user_proxy', role: 'user_proxy'})
CREATE (p)-[:DELEGATES_TO {step: 1}]->(a)
CREATE (a)-[:REVIEWS_WITH {step: 2}]->(c)
CREATE (c)-[:REPORTS_TO {step: 3}]->(u);
