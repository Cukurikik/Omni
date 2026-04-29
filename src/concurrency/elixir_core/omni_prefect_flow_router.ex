# Omni Langchain-Prefect Workflow Actor (Elixir)
# Ref: prefect-archive/langchain-prefect
defmodule Omni.PrefectFlowRouter do
  def route_task(task_type, priority \\ :normal) do
    case task_type do
      :retrieval -> {:ok, :rag_worker, priority}
      :generation -> {:ok, :llm_worker, priority}
      :embedding -> {:ok, :embed_worker, priority}
      _ -> {:error, :unknown_task_type}
    end
  end
end
