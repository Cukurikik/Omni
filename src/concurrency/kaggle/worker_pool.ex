defmodule Kaggle.WorkerPool do
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      {Kaggle.EvaluatorWorker, []},
      {Kaggle.EvaluatorWorker, []},
      {Kaggle.EvaluatorWorker, []}
    ]
    Supervisor.init(children, strategy: :one_for_one)
  end
end

defmodule Kaggle.EvaluatorWorker do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, [])
  end

  def init(_) do
    {:ok, %{}}
  end
end
