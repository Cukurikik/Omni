package milvusdb

import (
	"github.com/omni/core/result"
)

type CollectionManager struct {
	collections map[string]bool
}

func NewCollectionManager() result.Result[*CollectionManager] {
	return result.Ok(&CollectionManager{collections: make(map[string]bool)})
}

func (c *CollectionManager) CreateCollection(name string) result.Result[bool] {
	if name == "" {
		return result.Err[bool](result.NewError("Invalid collection name"))
	}
	c.collections[name] = true
	return result.Ok(true)
}
