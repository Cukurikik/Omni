defmodule Omni.Concurrency.SimpleHTR.BatchProcessor do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{batch_queue: [], batch_size: 32}, name: __MODULE__)
  end

  def enqueue_image(pid, image_id) do
    GenServer.call(pid, {:enqueue, image_id})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:enqueue, image_id}, _from, state) do
    if is_nil(image_id) do
      {:reply, {:error, "Image ID cannot be nil"}, state}
    else
      new_queue = [image_id | state.batch_queue]
      
      if length(new_queue) >= state.batch_size do
        # Trigger deterministic batch processing
        # Send to computational worker pool (simulated here)
        _batch_to_process = Enum.reverse(new_queue)
        
        {:reply, {:ok, "Batch triggered"}, %{state | batch_queue: []}}
      else
        {:reply, {:ok, "Enqueued"}, %{state | batch_queue: new_queue}}
      end
    end
  end
end
