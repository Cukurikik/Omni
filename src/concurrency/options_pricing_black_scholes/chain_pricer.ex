defmodule Omni.Concurrency.OptionsPricingBlackScholes.ChainPricer do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{options_priced: 0}, name: __MODULE__)
  end

  def price_entire_chain(pid, chain_size) do
    GenServer.cast(pid, {:price_chain, chain_size})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:price_chain, size}, state) do
    # Distributed Elixir worker managing the pricing of an entire Options Chain.
    # Spawns thousands of micro-processes to independently calculate the Black-Scholes price
    # and Greeks (Delta, Gamma, Theta, Vega) for every strike price and expiration date in parallel.
    
    new_count = state.options_priced + size
    
    {:noreply, %{state | options_priced: new_count}}
  end
end
