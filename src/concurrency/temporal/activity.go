package temporal
import "github.com/omni-framework/omni-go/core/result"

func RegisterActivity(name string) result.Result[bool, error] {
    return result.Ok(true)
}
