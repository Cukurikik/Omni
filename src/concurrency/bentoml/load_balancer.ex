defmodule Omni.BentoML.LoadBalancer do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, [], name: __MODULE__)
  end

  def init(_) do
    {:ok, %{workers: [], index: 0}}
  end

  def handle_call({:route_request, request}, _from, state) do
    if Enum.empty?(state.workers) do
      {:reply, {:error, :no_workers}, state}
    else
      worker = Enum.at(state.workers, state.index)
      next_index = rem(state.index + 1, length(state.workers))
      {:reply, {:ok, worker}, %{state | index: next_index}}
    end
  end

  def handle_cast({:register_worker, pid}, state) do
    {:noreply, %{state | workers: [pid | state.workers]}}
  end
end
