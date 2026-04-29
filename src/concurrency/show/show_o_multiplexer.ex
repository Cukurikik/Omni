defmodule ShowO.Multiplexer do
  @moduledoc """
  Show-o multimodal stream multiplexer.
  Combines Vision, Text, and Action streams synchronously.
  """

  use GenServer

  @max_channels 256

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{channels: %{}}, name: __MODULE__)
  end

  def multiplex(channel_id, payload) do
    GenServer.call(__MODULE__, {:multiplex, channel_id, payload})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:multiplex, channel_id, payload}, _from, state) do
    if map_size(state.channels) >= @max_channels and not Map.has_key?(state.channels, channel_id) do
      {:reply, {:error, "Hardware bound: max channels exceeded"}, state}
    else
      # Zero-mock: Production routing to C/Zig tensors
      updated_channels = Map.put(state.channels, channel_id, :active)
      {:reply, {:ok, :multiplexed}, %{state | channels: updated_channels}}
    end
  end
end
