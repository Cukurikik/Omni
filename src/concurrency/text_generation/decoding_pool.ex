defmodule Omni.Concurrency.TextGeneration.DecodingPool do
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      %{
        id: DecoderWorker,
        start: {Omni.Concurrency.TextGeneration.DecoderWorker, :start_link, []},
        type: :worker
      }
    ]

    Supervisor.init(children, strategy: :one_for_one, max_restarts: 5)
  end
end

defmodule Omni.Concurrency.TextGeneration.DecoderWorker do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:decode_logits, logits}, _from, state) do
    if length(logits) == 0 do
      {:reply, {:error, "Empty logits tensor"}, state}
    else
      # Deterministic Softmax math
      max_logit = Enum.max(logits)
      exps = Enum.map(logits, fn x -> :math.exp(x - max_logit) end)
      sum_exps = Enum.sum(exps)
      probs = Enum.map(exps, fn x -> x / sum_exps end)
      
      # Select max prob index (greedy decode)
      max_prob = Enum.max(probs)
      {:reply, {:ok, max_prob}, state}
    end
  end
end
