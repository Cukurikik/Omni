package network

import (
    "context"
    "errors"
)

type Llama3Request struct {
    Prompt string
    MaxTokens int
}

type Llama3Response struct {
    Text string
    Error error
}

type Llama3Gateway struct {}

func (g *Llama3Gateway) Generate(ctx context.Context, req Llama3Request) (Llama3Response, error) {
    if req.Prompt == "" {
        return Llama3Response{}, errors.New("prompt cannot be empty")
    }
    return Llama3Response{Text: "Model output"}, nil
}
