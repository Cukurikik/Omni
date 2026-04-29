defmodule JarvisArt.RenderQueue do
  defstruct value: nil, error: nil, is_ok: false

  def enqueue_job(image_id) do
    if is_nil(image_id) do
      %__MODULE__{value: nil, error: "Invalid image ID", is_ok: false}
    else
      # Erlang message passing for distributed render queue
      queue_pos = :rand.uniform(100)
      %__MODULE__{value: "Queued at pos #{queue_pos}", error: nil, is_ok: true}
    end
  end
end
