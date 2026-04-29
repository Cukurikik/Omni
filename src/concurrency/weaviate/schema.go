package weaviate
import "github.com/omni-framework/omni-go/core/result"

func CreateSchema(class string) result.Result[bool, error] {
    return result.Ok(true)
}
