defmodule Omni.Concurrency.TextVisualization.DataStreamer do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, [], name: __MODULE__)
  end

  @impl true
  def init(_) do
    {:ok, []}
  end

  @impl true
  def handle_cast({:push_data, point}, state) do
    # Deterministic limit to 100 points
    new_state = if length(state) >= 100 do
      tl(state) ++ [point]
    else
      state ++ [point]
    end
    {:noreply, new_state}
  end

  @impl true
  def handle_call(:get_data, _from, state) do
    {:reply, {:ok, state}, state}
  end
end
