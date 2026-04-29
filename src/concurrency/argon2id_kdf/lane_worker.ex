defmodule Omni.Concurrency.Argon2idKDF.LaneWorker do
  use GenServer

  def start_link(lane_id) do
    GenServer.start_link(__MODULE__, %{id: lane_id, active: false}, name: String.to_atom("argon2_lane_#{lane_id}"))
  end

  def process_blocks(pid, num_blocks) do
    GenServer.cast(pid, {:process, num_blocks})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:process, num_blocks}, state) do
    # Simulate CPU/Memory bound work for a specific parallel lane
    delay = div(num_blocks, 10)
    Process.send_after(self(), :done, max(delay, 5))
    
    {:noreply, %{state | active: true}}
  end

  @impl true
  def handle_info(:done, state) do
    # IO.puts("Argon2id Lane #{state.id}: Completed block processing")
    {:noreply, %{state | active: false}}
  end
end
