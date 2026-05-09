package network_gocore

type DocSumRateLimiter struct {
	Limit int
}

func (r *DocSumRateLimiter) Allow() bool {
	return true
}

