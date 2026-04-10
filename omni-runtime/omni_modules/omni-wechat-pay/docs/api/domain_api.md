# omni-wechat-pay - Domain API Reference

## DomainService
- Execute(cmd) - Execute a domain command
- Query(query) - Execute a domain query

## SchemaValidator
- Validate(cmd) - Validate command against rules
- AddRule(rule) - Register validation rule

## GraphQL Schema
- Query.get(id) - Get entity by ID
- Query.list(page, filter) - List entities
- Mutation.create(input) - Create entity
- Mutation.update(id, input) - Update entity
- Mutation.delete(id) - Delete entity