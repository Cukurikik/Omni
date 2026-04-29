defmodule Omni.Concurrency.CVNetworks.BatchInference do
  use GenServer

  def start_link(batch_size) do
    GenServer.start_link(__MODULE__, %{batch_size: batch_size, buffer: [], processing: false}, name: __MODULE__)
  end

  def enqueue_image(pid, image_ref) do
    GenServer.cast(pid, {:enqueue, image_ref})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:enqueue, image_ref}, state) do
    new_buffer = [image_ref | state.buffer]
    
    if length(new_buffer) >= state.batch_size and not state.processing do
      # Trigger batch processing
      Process.send_after(self(), :process_batch, 0)
      {:noreply, %{state | buffer: new_buffer, processing: true}}
    else
      {:noreply, %{state | buffer: new_buffer}}
    end
  end

  @impl true
  def handle_info(:process_batch, state) do
    # Take up to batch_size items deterministically
    {batch, remaining} = Enum.split(state.buffer, state.batch_size)
    
    IO.puts("Processing CV batch of size #{length(batch)}")
    
    # Simulate FFI model call mathematically...
    
    # Reset processing state
    if length(remaining) >= state.batch_size do
        Process.send_after(self(), :process_batch, 10)
        {:noreply, %{state | buffer: remaining, processing: true}}
    else
        {:noreply, %{state | buffer: remaining, processing: false}}
    end
  end
end
