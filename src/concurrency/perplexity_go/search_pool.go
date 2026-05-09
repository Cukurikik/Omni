package perplexity_go

type SearchTask struct {
	QueryID string
	URL     string
}

type SearchResult struct {
	QueryID string
	Content string
	Err     error
}

type Perp string
