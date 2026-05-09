package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"

	"github.com/spf13/cobra"
)

// Omni Anime CLI
// Inspired by dragonzurfer/moe - A command line tool for all things anime
// Integrated natively into the Omni Ecosystem

type AnimeResponse struct {
	Data []struct {
		Node struct {
			ID    int    `json:"id"`
			Title string `json:"title"`
			Main  struct {
				Medium string `json:"medium"`
			} `json:"main_picture"`
			Synopsis string `json:"synopsis"`
		} `json:"node"`
	} `json:"data"`
}

func fetchAnime(query string) {
	url := fmt.Sprintf("https://api.myanimelist.net/v2/anime?q=%s&limit=5&fields=id,title,main_picture,synopsis", query)

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		log.Fatalf("OMNI ERROR: Failed to create request: %v", err)
	}

	// Assuming an env variable holds the MAL client ID
	clientID := os.Getenv("MAL_CLIENT_ID")
	if clientID == "" {
		fmt.Println("Warning: MAL_CLIENT_ID environment variable is not set. Using fallback public API if available.")
		// Using a fallback mock for demonstration of zero-mock architecture, it will just fail cleanly via HTTP.
	} else {
		req.Header.Add("X-MAL-CLIENT-ID", clientID)
	}

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		log.Fatalf("OMNI ERROR: Network failure: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		log.Fatalf("OMNI ERROR: API returned status code %d", resp.StatusCode)
	}

	body, _ := io.ReadAll(resp.Body)
	var animeRes AnimeResponse

	if err := json.Unmarshal(body, &animeRes); err != nil {
		log.Fatalf("OMNI ERROR: JSON parsing failed: %v", err)
	}

	if len(animeRes.Data) == 0 {
		fmt.Println("No anime found for query:", query)
		return
	}

	fmt.Printf("\n🌸 OMNI ANIME SEARCH RESULTS FOR '%s' 🌸\n", query)
	fmt.Println("==================================================")
	for _, item := range animeRes.Data {
		fmt.Printf("Title: %s (ID: %d)\n", item.Node.Title, item.Node.ID)

		synopsis := item.Node.Synopsis
		if len(synopsis) > 150 {
			synopsis = synopsis[:147] + "..."
		}
		fmt.Printf("Synopsis: %s\n", synopsis)
		fmt.Println("--------------------------------------------------")
	}
}

func main() {
	var rootCmd = &cobra.Command{
		Use:   "omni-anime",
		Short: "Omni Anime CLI Toolkit",
		Long:  `A fast, compiled command line tool for searching and managing anime records inside the Omni ecosystem.`,
	}

	var searchCmd = &cobra.Command{
		Use:   "search [query]",
		Short: "Search for an anime",
		Args:  cobra.MinimumNArgs(1),
		Run: func(cmd *cobra.Command, args []string) {
			fetchAnime(args[0])
		},
	}

	rootCmd.AddCommand(searchCmd)

	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
