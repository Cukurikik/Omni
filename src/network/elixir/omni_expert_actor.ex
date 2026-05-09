defmodule OmniMoE.ExpertActor do
  use GenServer

  # OMNI MOTHER: Actor Model for MoE Expert State
  
  def start_link(opts) do
    name = Keyword.get(opts, :name, __MODULE__)
    GenServer.start_link(__MODULE__, :ok, name: name)
  end

  @impl true
  def init(:ok) do
    {:ok, %{processed_tokens: 0, status: :online}}
  end

  @impl true
  def handle_call({:process, tokens}, _from, state) do
    new_state = %{state | processed_tokens: state.processed_tokens + tokens}
    {:reply, :ok, new_state}
  end
end
