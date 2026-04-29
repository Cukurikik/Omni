defmodule OmniConcurrency.AILiterature.ArxivScraperSupervisor do
  @moduledoc """
  OMNI CONCURRENCY LAYER: Arxiv Scraper
  Supervisor for concurrently fetching metadata from the arXiv API.
  """
  use Task.Supervisor

  def start_link(opts) do
    Task.Supervisor.start_link(__MODULE__, opts)
  end

  def fetch_papers(supervisor, query_list) do
    try do
      tasks = Enum.map(query_list, fn query ->
        Task.Supervisor.async(supervisor, fn ->
          fetch_from_arxiv(query)
        end)
      end)

      results = Task.await_many(tasks, 15_000)
      {:ok, results}
    rescue
      e -> {:error, "Scraping failed: #{Exception.message(e)}"}
    end
  end

  defp fetch_from_arxiv(query) do
    # Simulated HTTP call to Arxiv API
    # In production, this uses HTTPoison or Finch to parse XML results
    Process.sleep(100) 
    %{query: query, title: "Attention Is All You Need", citations: Enum.random(100..10000)}
  end
end
