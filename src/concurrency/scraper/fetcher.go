package scraper

import (
	"time"
	"context"
	"io"
	"net/http"
)

type Fetcher struct {
	client *http.Client
}

func NewFetcher() *Fetcher {
	return &Fetcher{
		client: &http.Client{Timeout: 10 * time.Second},
	}
}

func (f *Fetcher) FetchURL(ctx context.Context, url string) ([]byte, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", "Omni-AutoScraper/1.0")

	resp, err := f.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	return io.ReadAll(resp.Body)
}
