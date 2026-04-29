defmodule Omni.Concurrency.DiamondRL.TrajectoryBuffer do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{buffer: [], capacity: 10000}, name: __MODULE__)
  end

  def add_experience(pid, state, action, reward, next_state) do
    GenServer.cast(pid, {:add, {state, action, reward, next_state}})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:add, experience}, state) do
    new_buffer = [experience | state.buffer]
    
    # Deterministic ring buffer enforcement
    pruned_buffer = if length(new_buffer) > state.capacity do
      Enum.take(new_buffer, state.capacity)
    else
      new_buffer
    end
    
    {:noreply, %{state | buffer: pruned_buffer}}
  end
end
