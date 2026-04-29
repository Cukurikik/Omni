defmodule Omni.Concurrency.Genomics.FastaChunkPool do
  @moduledoc """
  Actor-based worker pool for parallel processing of massive FASTA/FASTQ files.
  """
  use GenServer

  defmodule State do
    defstruct [:workers, :task_queue, :results]
  end

  def start_link(num_workers) do
    GenServer.start_link(__MODULE__, num_workers, name: __MODULE__)
  end

  @impl true
  def init(num_workers) do
    # Spawn worker processes
    workers = Enum.map(1..num_workers, fn i -> 
      {:ok, pid} = Task.Supervisor.start_link(name: :"fasta_worker_#{i}")
      pid
    end)
    
    {:ok, %State{workers: workers, task_queue: [], results: []}}
  end

  def submit_chunk(chunk) do
    GenServer.cast(__MODULE__, {:submit, chunk})
  end

  def get_results do
    GenServer.call(__MODULE__, :get_results)
  end

  @impl true
  def handle_cast({:submit, chunk}, state) do
    # In a real implementation, we'd round-robin to a worker
    worker = Enum.random(state.workers)
    
    # Asynchronously process the chunk
    Task.Supervisor.async_nolink(worker, fn -> 
      process_chunk(chunk) 
    end)
    
    {:noreply, state}
  end

  @impl true
  def handle_info({ref, result}, state) when is_reference(ref) do
    # Receive task result
    {:noreply, %{state | results: [result | state.results]}}
  end

  @impl true
  def handle_info({:DOWN, _ref, :process, _pid, _reason}, state) do
    {:noreply, state}
  end

  @impl true
  def handle_call(:get_results, _from, state) do
    {:reply, {:ok, state.results}, %{state | results: []}}
  end

  defp process_chunk(chunk) do
    # Simulate processing (e.g. GC content calculation)
    gc_count = chunk
      |> String.graphemes()
      |> Enum.count(fn char -> char == "G" or char == "C" end)
      
    %{chunk_size: String.length(chunk), gc_count: gc_count}
  end
end
