// moe_chat_navigator_parser.go — Network Layer: Chat Navigator Parser
// Parses incoming streaming HTML/markdown chunks from LLMs over WebSockets.

package network_moe

import (
	"bytes"
	"strings"

	"golang.org/x/net/html"
)

type ParsedNode struct {
	Tag     string
	Content string
}

func ExtractHeadings(htmlContent []byte) ([]ParsedNode, error) {
	var headings []ParsedNode

	doc, err := html.Parse(bytes.NewReader(htmlContent))
	if err != nil {
		return nil, err
	}

	var f func(*html.Node)
	f = func(n *html.Node) {
		if n.Type == html.ElementNode && (n.Data == "h1" || n.Data == "h2" || n.Data == "h3") {
			// Extract text content safely
			var textContent strings.Builder
			var extractText func(*html.Node)
			extractText = func(c *html.Node) {
				if c.Type == html.TextNode {
					textContent.WriteString(c.Data)
				}
				for child := c.FirstChild; child != nil; child = child.NextSibling {
					extractText(child)
				}
			}
			extractText(n)
			headings = append(headings, ParsedNode{
				Tag:     n.Data,
				Content: strings.TrimSpace(textContent.String()),
			})
		}
		for c := n.FirstChild; c != nil; c = c.NextSibling {
			f(c)
		}
	}
	f(doc)

	return headings, nil
}

