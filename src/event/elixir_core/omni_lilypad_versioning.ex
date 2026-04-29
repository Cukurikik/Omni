defmodule Omni.Lilypad.Versioning do
  @moduledoc """
  Omni Lilypad Versioning (Elixir)
  Based on Mirascope/lilypad.
  Fault-tolerant event sourcing for LLM prompt versioning and tracing.
  """

  @doc """
  Registers a new prompt version deterministically.
  Returns a Monadic-style tuple.
  """
  @spec register_prompt(String.t(), String.t(), String.t()) :: {:ok, map()} | {:error, String.t()}
  def register_prompt(project_id, prompt_text, author) do
    if project_id == "" or prompt_text == "" do
      {:error, "Project ID and prompt text cannot be empty"}
    else
      # Deterministic hash for versioning
      hash = :crypto.hash(:sha256, prompt_text) |> Base.encode16()
      
      record = %{
        project: project_id,
        version_hash: hash,
        text: prompt_text,
        author: author,
        timestamp: :os.system_time(:second)
      }
      
      {:ok, record}
    end
  end
end
