defmodule Omni.Concurrency.AudioMIDI.ChunkSupervisor do
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      {Omni.Concurrency.AudioMIDI.TranscriptionWorker, name: :transcriber_alpha},
      {Omni.Concurrency.AudioMIDI.TranscriptionWorker, name: :transcriber_beta}
    ]

    Supervisor.init(children, strategy: :one_for_one)
  end
end

defmodule Omni.Concurrency.AudioMIDI.TranscriptionWorker do
  use GenServer

  def start_link(opts) do
    GenServer.start_link(__MODULE__, :ok, opts)
  end

  @impl true
  def init(:ok) do
    {:ok, %{processed_chunks: 0}}
  end

  @impl true
  def handle_call({:process_chunk, chunk_data}, _from, state) do
    if byte_size(chunk_data) == 0 do
      {:reply, {:error, "Audio chunk is empty"}, state}
    else
      # Math logic representing data checksum verification
      checksum = :erlang.crc32(chunk_data)
      new_state = %{state | processed_chunks: state.processed_chunks + 1}
      
      {:reply, {:ok, %{status: "transcribed", checksum: checksum}}, new_state}
    end
  end
end
