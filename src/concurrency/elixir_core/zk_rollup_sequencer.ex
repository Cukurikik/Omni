defmodule Omni.Concurrency.ZkRollupSequencer do
  @moduledoc """
  OMNI Framework - Zero-Knowledge Rollup Sequencer
  Aggregates transactions and sequences them into a block for ZK proving.
  """
  use GenServer

  def start_link(opts) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  def add_transaction(pid, tx_data) do
    GenServer.cast(pid, {:add_tx, tx_data})
  end

  def get_current_batch(pid) do
    GenServer.call(pid, :get_batch)
  end

  @impl true
  def init(_opts) do
    {:ok, %{tx_pool: [], batch_id: 1}}
  end

  @impl true
  def handle_cast({:add_tx, tx_data}, state) do
    new_pool = [tx_data | state.tx_pool]
    
    # If pool size reaches threshold, we would trigger proving
    if length(new_pool) >= 100 do
      # Trigger to Rust prover logic here
      {:noreply, %{tx_pool: [], batch_id: state.batch_id + 1}}
    else
      {:noreply, %{state | tx_pool: new_pool}}
    end
  end

  @impl true
  def handle_call(:get_batch, _from, state) do
    {:reply, state.tx_pool, state}
  end
end
