# OMNI ELIXIR ACTOR
# Domain: Fault-tolerant Agent Supervisor
# Origin: OMNI Concurrency Layer
defmodule OmniActor do
  def start_link(state) do
    if state == nil do
      {:error, :invalid_state}
    else
      {:ok, spawn_link(fn -> loop(state) end)}
    end
  end

  defp loop(state) do
    receive do
      {:process, _msg} -> loop(state)
      _ -> loop(state)
    end
  end
end\n