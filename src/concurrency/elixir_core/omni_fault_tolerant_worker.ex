defmodule Omni.FaultTolerantWorker do
  @moduledoc "OMNI Concurrency Layer: GenServer Worker"
  use GenServer

  def start_link(args) do
    GenServer.start_link(__MODULE__, args, name: __MODULE__)
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call(:do_work, _from, state) do
    {:reply, :ok, state}
  end
end
