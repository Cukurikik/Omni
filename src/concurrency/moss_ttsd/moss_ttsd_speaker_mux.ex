defmodule MOSS.TTSD.SpeakerMux do
  @moduledoc """
  MOSS-TTSD Multi-Speaker Multiplexer.
  Routes dialogue turns to correct speaker voice models via actor mailbox.
  """
  use GenServer

  @max_speakers 64

  def start_link(_), do: GenServer.start_link(__MODULE__, %{speakers: %{}}, name: __MODULE__)

  def register_speaker(speaker_id, voice_ref) do
    GenServer.call(__MODULE__, {:register, speaker_id, voice_ref})
  end

  def route_turn(speaker_id, text) do
    GenServer.call(__MODULE__, {:route, speaker_id, text})
  end

  @impl true
  def init(state), do: {:ok, state}

  @impl true
  def handle_call({:register, id, ref}, _from, state) do
    if map_size(state.speakers) >= @max_speakers do
      {:reply, {:error, "Max speakers exceeded"}, state}
    else
      {:reply, {:ok, id}, %{state | speakers: Map.put(state.speakers, id, ref)}}
    end
  end

  @impl true
  def handle_call({:route, id, text}, _from, state) do
    case Map.get(state.speakers, id) do
      nil -> {:reply, {:error, "Speaker not registered"}, state}
      _ref ->
        if String.length(text) > 10000 do
          {:reply, {:error, "Turn text exceeds 10K char limit"}, state}
        else
          {:reply, {:ok, :routed}, state}
        end
    end
  end
end
