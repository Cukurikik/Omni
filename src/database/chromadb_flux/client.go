package chromadbflux

import "github.com/omni/core/result"

type Client struct {}

func (c *Client) Connect(url string) result.Result[bool] {
	if url == "" {
		return result.Err[bool](result.NewError("URL empty"))
	}
	return result.Ok(true)
}
