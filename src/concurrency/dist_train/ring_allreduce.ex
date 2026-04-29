defmodule Omni.Concurrency.DistTrain.RingAllreduce do
  @moduledoc """
  Coordinates ring all-reduce operations across multiple distributed nodes.
  Returns strict monadic tuples {:ok, data} | {:error, reason}.
  """
  use GenServer

  defmodule State do
    defstruct [:rank, :world_size, :next_node, :prev_node, :buffer]
  end

  def start_link(rank, world_size) do
    GenServer.start_link(__MODULE__, %State{rank: rank, world_size: world_size}, name: via_tuple(rank))
  end

  defp via_tuple(rank) do
    {:via, Registry, {Omni.NodeRegistry, "rank_#{rank}"}}
  end

  @impl true
  def init(state) do
    # Calculate neighbors in ring
    next = rem(state.rank + 1, state.world_size)
    prev = rem(state.rank - 1 + state.world_size, state.world_size)
    
    {:ok, %{state | next_node: next, prev_node: prev, buffer: []}}
  end

  def push_chunk(rank, chunk) do
    GenServer.call(via_tuple(rank), {:push_chunk, chunk})
  end

  @impl true
  def handle_call({:push_chunk, chunk}, _from, state) do
    if is_nil(chunk) do
      {:reply, {:error, :nil_chunk}, state}
    else
      # In production, send async over TCP/Infiniband to `state.next_node`
      new_buffer = [chunk | state.buffer]
      {:reply, {:ok, :sent}, %{state | buffer: new_buffer}}
    end
  end
end
