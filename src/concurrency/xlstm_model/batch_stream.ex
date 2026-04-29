defmodule Omni.Concurrency.xLSTMModel.BatchStream do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{sequence_buffer: [], is_streaming: false}, name: __MODULE__)
  end

  def ingest_token(pid, token_id) do
    GenServer.cast(pid, {:ingest, token_id})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:ingest, token_id}, state) do
    new_buffer = [token_id | state.sequence_buffer]
    
    # Process sequence chunk deterministically every 10 tokens
    if length(new_buffer) >= 10 do
      _chunk_to_process = Enum.reverse(new_buffer)
      
      # Simulate downstream inference pipeline hook
      
      {:noreply, %{state | sequence_buffer: []}}
    else
      {:noreply, %{state | sequence_buffer: new_buffer}}
    end
  end
end
