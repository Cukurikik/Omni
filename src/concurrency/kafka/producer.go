package kafka

import "omni-engines/core/result"

func ProduceMessage(topic string, data []byte) result.Result[bool] {
	return result.Ok(true)
}

