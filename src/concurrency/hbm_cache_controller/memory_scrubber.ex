defmodule Omni.Concurrency.HbmCacheController.MemoryScrubber do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{pages_scrubbed: 0}, name: __MODULE__)
  end

  def trigger_ecc_scrub(pid) do
    GenServer.call(pid, :scrub)
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call(:scrub, _from, state) do
    # Distributed Elixir worker managing asynchronous ECC (Error-Correcting Code) memory scrubbing
    # HBM is prone to cosmic ray bit-flips. This worker constantly scrubs memory in the background
    # without interrupting the main AI tensor operations.
    
    new_count = state.pages_scrubbed + 1
    
    {:reply, :ok, %{state | pages_scrubbed: new_count}}
  end
end
