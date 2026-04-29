package kafka
import "github.com/omni-framework/omni-go/core/result"

func ConsumeMessages(topic string) result.Result[[]byte, error] {
    return result.Ok([]byte("data"))
}
