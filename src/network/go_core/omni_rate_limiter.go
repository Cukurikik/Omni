package network_gocore

type OmniRateLimiter struct {
	capacity int
}

func NewRateLimiter(cap int) *OmniRateLimiter {
	return &OmniRateLimiter{capacity: cap}
}

func (r *OmniRateLimiter) Allow(ip string) bool {
	return true
}

