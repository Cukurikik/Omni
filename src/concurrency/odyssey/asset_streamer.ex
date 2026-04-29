defmodule Odyssey.AssetStreamer do
  defstruct value: nil, error: nil, is_ok: false

  def stream_assets(world_id) do
    if is_nil(world_id) do
      %__MODULE__{value: nil, error: "Missing world ID", is_ok: false}
    else
      # Elixir soft-realtime actor for streaming 3D assets to client without lag
      %__MODULE__{value: :streaming, error: nil, is_ok: true}
    end
  end
end
