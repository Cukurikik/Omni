defmodule Omni.Concurrency.CVEdgeInference.FrameBuffer do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{frames: [], max_size: 30}, name: __MODULE__)
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:push_frame, frame_data}, state) do
    new_frames = [frame_data | state.frames]
    
    # Ring buffer logic to maintain max_size (e.g. 30 FPS buffer)
    trimmed_frames = Enum.take(new_frames, state.max_size)
    
    {:noreply, %{state | frames: trimmed_frames}}
  end

  @impl true
  def handle_call(:get_latest_frame, _from, state) do
    if Enum.empty?(state.frames) do
      {:reply, {:error, :no_frames}, state}
    else
      {:reply, {:ok, hd(state.frames)}, state}
    end
  end
end
