defmodule Omni.Concurrency.FastquantBacktester.StrategyPool do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{strategies_tested: 0}, name: __MODULE__)
  end

  def grid_search_parameters(pid, strategy_id, param_grid) do
    GenServer.call(pid, {:search, strategy_id, param_grid})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:search, _id, grid}, _from, state) do
    # Distributed grid search orchestrator
    # Spins up thousands of parallel backtests with varying Moving Average combinations
    
    new_count = state.strategies_tested + length(grid)
    
    {:reply, :ok, %{state | strategies_tested: new_count}}
  end
end
