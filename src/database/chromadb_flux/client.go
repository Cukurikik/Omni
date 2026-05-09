package chromadbflux

import "omni-engines/core/result"

type Client struct{}

func (c *Client) Connect(url string) result.Result[bool] {
	if url == "" {
		return result.Err[bool](result.NewError("URL empty"))
	}
	return result.Ok(true)
}
