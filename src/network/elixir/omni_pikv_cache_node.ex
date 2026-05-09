defmodule OmniMoE.PiKVCacheNode do
  use GenServer

  # OMNI MOTHER: Elixir PiKV Distributed Cache Node
  # Stores stateful KV pairs across the cluster using OTP

  def start_link(opts) do
    name = Keyword.get(opts, :name, __MODULE__)
    GenServer.start_link(__MODULE__, :ok, name: name)
  end

  @impl true
  def init(:ok) do
    # Map of sequence_id -> kv_blocks
    {:ok, %{blocks: %{}, memory_used: 0}}
  end

  @impl true
  def handle_call({:allocate, seq_id, size}, _from, state) do
    new_blocks = Map.put(state.blocks, seq_id, size)
    new_state = %{state | blocks: new_blocks, memory_used: state.memory_used + size}
    {:reply, :ok, new_state}
  end
end
