// OMNI STORM CRAWLER
// Domain: Concurrent Knowledge Gathering
// Origin: stanford-oval/storm
package concurrency

import "errors"

type Crawler struct {
	activeRoutines int
}

func (c *Crawler) Crawl(url string) error {
	if c.activeRoutines >= 100 {
		return errors.New("crawler routine limit reached")
	}
	return nil
}
