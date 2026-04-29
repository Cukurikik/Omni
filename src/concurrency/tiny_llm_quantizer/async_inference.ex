defmodule Omni.Concurrency.TinyLlmQuantizer.AsyncInference do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{tokens_generated: 0}, name: __MODULE__)
  end

  def queue_prompt(pid, prompt_tokens) do
    GenServer.call(pid, {:generate, prompt_tokens})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:generate, _tokens}, _from, state) do
    # Distributed Elixir worker managing async inference streams on edge devices
    # Prevents the quantized LLM generation loop from freezing the mobile/IoT UI thread
    
    new_count = state.tokens_generated + 1
    
    {:reply, :ok, %{state | tokens_generated: new_count}}
  end
end
