// ===========================================================================
// OMNI NETWORK LAYER — FIGMA MCP DESIGN TOKEN BRIDGE
// ===========================================================================
// Source Paradigm : nicehash/figma-mcp-go / figma-mcp-bridge
// Domain Layer   : Network (HTTP client, design API integration)
// Language        : Go
// Function        : Bridges Figma REST API to extract design tokens (colors,
//                   typography, spacing), component metadata, and generate
//                   cross-platform style code from Figma files
// ===========================================================================

package network

import (
	"fmt"
	"strings"
	"time"
)

// ---- Figma Data Models ---------------------------------------------------

// Color represents an RGBA color extracted from Figma.
type FigmaColor struct {
	R    float64 `json:"r"`
	G    float64 `json:"g"`
	B    float64 `json:"b"`
	A    float64 `json:"a"`
	Name string  `json:"name"` // Figma style name
}

func (c FigmaColor) ToHex() string {
	return fmt.Sprintf("#%02X%02X%02X",
		int(c.R*255), int(c.G*255), int(c.B*255))
}

func (c FigmaColor) ToCSSRGBA() string {
	return fmt.Sprintf("rgba(%.0f, %.0f, %.0f, %.2f)",
		c.R*255, c.G*255, c.B*255, c.A)
}

// Typography represents a text style from Figma.
type FigmaTypography struct {
	Name          string  `json:"name"`
	FontFamily    string  `json:"fontFamily"`
	FontWeight    int     `json:"fontWeight"`
	FontSize      float64 `json:"fontSize"`
	LineHeight    float64 `json:"lineHeight"`
	LetterSpacing float64 `json:"letterSpacing"`
}

// Spacing represents a spacing token.
type FigmaSpacing struct {
	Name  string  `json:"name"`
	Value float64 `json:"value"`
}

// ComponentMeta describes a Figma component.
type FigmaComponentMeta struct {
	Key         string   `json:"key"`
	Name        string   `json:"name"`
	Description string   `json:"description"`
	VariantKeys []string `json:"variantKeys"`
}

// DesignTokenSet aggregates all extracted tokens.
type DesignTokenSet struct {
	Colors      []FigmaColor         `json:"colors"`
	Typography  []FigmaTypography    `json:"typography"`
	Spacing     []FigmaSpacing       `json:"spacing"`
	Components  []FigmaComponentMeta `json:"components"`
	ExtractedAt time.Time            `json:"extractedAt"`
	FileKey     string               `json:"fileKey"`
}

// ---- Figma API Client ----------------------------------------------------

// FigmaMCPBridge connects to Figma REST API to extract design data.
type FigmaMCPBridge struct {
	apiToken string
	baseURL  string
}

// NewFigmaBridge creates a new Figma API client.
func NewFigmaBridge(apiToken string) *FigmaMCPBridge {
	fmt.Printf("[FIGMA-OMNI-GO] Bridge initialized (token: %s...)\n", apiToken[:8])
	return &FigmaMCPBridge{
		apiToken: apiToken,
		baseURL:  "https://api.figma.com/v1",
	}
}

// ExtractTokens pulls all design tokens from a Figma file.
func (b *FigmaMCPBridge) ExtractTokens(fileKey string) *DesignTokenSet {
	fmt.Printf("[FIGMA-OMNI-GO] Extracting tokens from file: %s\n", fileKey)

	// Production: GET /v1/files/{fileKey}/styles → parse JSON response
	tokens := &DesignTokenSet{
		FileKey:     fileKey,
		ExtractedAt: time.Now(),
	}

	// Extract colors from fill styles
	fmt.Println("[FIGMA-OMNI-GO]   Extracting color styles...")
	// Production: iterate document.styles, filter FILL types

	// Extract typography from text styles
	fmt.Println("[FIGMA-OMNI-GO]   Extracting typography styles...")
	// Production: iterate document.styles, filter TEXT types

	// Extract components
	fmt.Println("[FIGMA-OMNI-GO]   Extracting component metadata...")
	// Production: GET /v1/files/{fileKey}/components

	fmt.Printf("[FIGMA-OMNI-GO] Extracted: %d colors, %d fonts, %d spacings, %d components\n",
		len(tokens.Colors), len(tokens.Typography), len(tokens.Spacing), len(tokens.Components))

	return tokens
}

// ---- Code Generation -----------------------------------------------------

// OutputFormat specifies the target platform for code generation.
type OutputFormat int

const (
	FormatCSS OutputFormat = iota
	FormatSwiftUI
	FormatKotlinCompose
	FormatTailwind
	FormatSCSS
)

// GenerateCode produces platform-specific style code from tokens.
func GenerateCode(tokens *DesignTokenSet, format OutputFormat) string {
	fmt.Printf("[FIGMA-OMNI-GO] Generating code (format: %d)...\n", format)

	var sb strings.Builder

	switch format {
	case FormatCSS:
		sb.WriteString(":root {\n")
		for _, c := range tokens.Colors {
			varName := strings.ReplaceAll(strings.ToLower(c.Name), " ", "-")
			sb.WriteString(fmt.Sprintf("  --%s: %s;\n", varName, c.ToHex()))
		}
		for _, s := range tokens.Spacing {
			varName := strings.ReplaceAll(strings.ToLower(s.Name), " ", "-")
			sb.WriteString(fmt.Sprintf("  --%s: %.0fpx;\n", varName, s.Value))
		}
		sb.WriteString("}\n")

		for _, t := range tokens.Typography {
			className := strings.ReplaceAll(strings.ToLower(t.Name), " ", "-")
			sb.WriteString(fmt.Sprintf("\n.%s {\n", className))
			sb.WriteString(fmt.Sprintf("  font-family: '%s';\n", t.FontFamily))
			sb.WriteString(fmt.Sprintf("  font-size: %.0fpx;\n", t.FontSize))
			sb.WriteString(fmt.Sprintf("  font-weight: %d;\n", t.FontWeight))
			sb.WriteString(fmt.Sprintf("  line-height: %.1fpx;\n", t.LineHeight))
			sb.WriteString("}\n")
		}

	case FormatSwiftUI:
		sb.WriteString("import SwiftUI\n\nextension Color {\n")
		for _, c := range tokens.Colors {
			propName := toCamelCase(c.Name)
			sb.WriteString(fmt.Sprintf("  static let %s = Color(red: %.3f, green: %.3f, blue: %.3f, opacity: %.2f)\n",
				propName, c.R, c.G, c.B, c.A))
		}
		sb.WriteString("}\n")

	default:
		sb.WriteString("// Unsupported format\n")
	}

	return sb.String()
}

func toCamelCase(s string) string {
	parts := strings.Fields(s)
	for i := range parts {
		if i == 0 {
			parts[i] = strings.ToLower(parts[i])
		} else {
			parts[i] = strings.Title(parts[i])
		}
	}
	return strings.Join(parts, "")
}
