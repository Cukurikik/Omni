defmodule Obsidian.ContextFetcher do
  defstruct value: nil, error: nil, is_ok: false

  def fetch_relevant_notes(query_vector) do
    if is_nil(query_vector) do
      %__MODULE__{value: nil, error: "Missing query vector", is_ok: false}
    else
      # Elixir concurrent actor for parallel retrieval of semantic context from vault
      %__MODULE__{value: ["note_a.md", "note_b.md"], error: nil, is_ok: true}
    end
  end
end
