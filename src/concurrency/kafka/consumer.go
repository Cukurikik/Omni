package kafka

import "omni-engines/core/result"

func ConsumeMessages(topic string) result.Result[[]byte] {
	return result.Ok([]byte("data"))
}

