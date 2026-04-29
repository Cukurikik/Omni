defmodule Omni.Concurrency.Model2VecEmbedder.BatchTokenizer do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{token_buffer: [], batch_size: 256}, name: __MODULE__)
  end

  def enqueue_text(pid, text_payload) do
    GenServer.cast(pid, {:enqueue, text_payload})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:enqueue, text_payload}, state) do
    # Deterministic simulation of text splitting
    tokens = String.split(text_payload, " ")
    
    new_buffer = state.token_buffer ++ tokens
    
    if length(new_buffer) >= state.batch_size do
      {batch, remainder} = Enum.split(new_buffer, state.batch_size)
      
      # Emit to downstream computation logic here
      _processed = length(batch)
      
      {:noreply, %{state | token_buffer: remainder}}
    else
      {:noreply, %{state | token_buffer: new_buffer}}
    end
  end
end
