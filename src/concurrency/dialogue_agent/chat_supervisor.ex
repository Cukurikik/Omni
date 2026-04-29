defmodule Omni.Concurrency.DialogueAgent.ChatSupervisor do
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      %{
        id: ChatSession,
        start: {Omni.Concurrency.DialogueAgent.ChatSession, :start_link, []},
        type: :worker
      }
    ]

    Supervisor.init(children, strategy: :one_for_one, max_restarts: 10)
  end
end

defmodule Omni.Concurrency.DialogueAgent.ChatSession do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:process_tokens, token_count}, _from, state) do
    if token_count <= 0 do
      {:reply, {:error, "Invalid token count"}, state}
    else
      # Deterministic throughput math
      latency_ms = token_count * 1.5 + 10.0
      {:reply, {:ok, latency_ms}, state}
    end
  end
end
