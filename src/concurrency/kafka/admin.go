package kafka

import "omni-engines/core/result"

func CreateTopic(topic string) result.Result[bool] { return result.Ok(true) }

