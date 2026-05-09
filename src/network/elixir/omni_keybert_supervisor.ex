# OMNI Framework - Elixir OTP Supervisor for KeyBERT Extractors
# Ensures fault tolerance when calling out to the Python ML subsystem.

defmodule OmniFramework.KeyBERTExtractor.Supervisor do
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      {OmniFramework.KeyBERTExtractor.WorkerPool, pool_size: 10},
      {OmniFramework.KeyBERTExtractor.Cache, []}
    ]

    # One-for-one means if a worker crashes, only that worker is restarted
    Supervisor.init(children, strategy: :one_for_one, max_restarts: 5)
  end
end
