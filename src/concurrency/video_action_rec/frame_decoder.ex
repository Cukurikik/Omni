defmodule Omni.Concurrency.VideoActionRec.FrameDecoder do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{frame_count: 0, buffer: []}, name: __MODULE__)
  end

  def ingest_frame(pid, raw_data) do
    GenServer.call(pid, {:ingest, raw_data})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:ingest, raw_data}, _from, state) do
    if is_nil(raw_data) do
      {:reply, {:error, "Raw frame data cannot be nil"}, state}
    else
      new_count = state.frame_count + 1
      # Deterministic tuple construction for buffer
      frame_obj = {new_count, :os.system_time(:millisecond), raw_data}
      
      new_buffer = [frame_obj | state.buffer]
      
      # Keep buffer bounded to 30 frames (1 sec at 30fps)
      bounded_buffer = Enum.take(new_buffer, 30)
      
      new_state = %{state | frame_count: new_count, buffer: bounded_buffer}
      
      {:reply, {:ok, "Frame #{new_count} decoded"}, new_state}
    end
  end
end
