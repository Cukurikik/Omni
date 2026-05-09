package weaviatedb

import "omni-engines/core/result"

type SchemaManager struct {
	schema map[string]interface{}
}

func NewSchemaManager() result.Result[*SchemaManager] {
	return result.Ok(&SchemaManager{schema: make(map[string]interface{})})
}

func (s *SchemaManager) RegisterClass(className string) result.Result[bool] {
	if className == "" {
		return result.Err[bool](result.NewError("className cannot be empty"))
	}
	s.schema[className] = true
	return result.Ok(true)
}
