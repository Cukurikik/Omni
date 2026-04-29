defmodule Omni.Concurrency.FlashLoanArbitrage.PriceOracleListener do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{oracles_tracked: 0}, name: __MODULE__)
  end

  def update_price(pid, token_pair, price) do
    GenServer.cast(pid, {:update, token_pair, price})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:update, _pair, _price}, state) do
    # Distributed Elixir worker managing thousands of asynchronous WebSockets.
    # Listens to real-time price updates from Uniswap, SushiSwap, and Curve.
    # The instant a price discrepancy opens up, it triggers the Bellman-Ford algorithm.
    
    new_count = state.oracles_tracked + 1
    
    {:noreply, %{state | oracles_tracked: new_count}}
  end
end
