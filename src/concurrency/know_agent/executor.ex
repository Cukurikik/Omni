defmodule KnowAgent.Executor do
  def execute(task) when is_binary(task) and byte_size(task) > 0 do
    {:ok, "Successfully executed: " <> task}
  end
  def execute(_) do
    {:error, "Task must be a non-empty string"}
  end
end
