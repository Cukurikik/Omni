// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Weaviate GraphQL Schema (OMNI Zero-Mock Implementation)
// Implements Go-based vector schema definition parsing.

package weaviate

import (
	"errors"
	"strings"
)

type Result struct {
	Value interface{}
	Error error
	IsOk  bool
}

func Ok(val interface{}) Result {
	return Result{Value: val, Error: nil, IsOk: true}
}

func Err(err string) Result {
	return Result{Value: nil, Error: errors.New(err), IsOk: false}
}

type Property struct {
	Name     string
	DataType []string
}

type Class struct {
	Class       string
	Description string
	Properties  []Property
}

func ValidateSchema(c Class) Result {
	if c.Class == "" {
		return Err("Class name cannot be empty.")
	}
	
	if strings.ToUpper(c.Class[:1]) != c.Class[:1] {
		return Err("Weaviate class name must start with a capital letter.")
	}

	for _, prop := range c.Properties {
		if prop.Name == "" {
			return Err("Property name cannot be empty.")
		}
		if len(prop.DataType) == 0 {
			return Err("Property must have at least one data type.")
		}
		
		dt := prop.DataType[0]
		validTypes := map[string]bool{"text": true, "int": true, "number": true, "boolean": true}
		if !validTypes[dt] {
			return Err("Invalid data type: " + dt)
		}
	}

	return Ok(true)
}
