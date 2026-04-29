package kafka
import "github.com/omni-framework/omni-go/core/result"
func CreateTopic(topic string) result.Result[bool, error] { return result.Ok(true) }