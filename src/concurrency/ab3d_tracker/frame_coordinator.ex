defmodule Omni.Concurrency.Ab3dTracker.FrameCoordinator do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{frame_id: 0, tracks: %{}}, name: __MODULE__)
  end

  def process_detections(pid, detections) do
    GenServer.call(pid, {:process, detections})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:process, _detections}, _from, state) do
    # Coordinate Kalman prediction, Hungarian matching, and state updates per frame
    new_frame_id = state.frame_id + 1
    
    {:reply, :ok, %{state | frame_id: new_frame_id}}
  end
end
