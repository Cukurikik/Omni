defmodule MiniMax.InferenceQueue do
  defstruct value: nil, error: nil, is_ok: false

  def enqueue_request(request_payload) do
    if is_nil(request_payload) do
      %__MODULE__{value: nil, error: "Empty request payload", is_ok: false}
    else
      # Elixir actor-based high-throughput queuing for MiniMax M2.1
      %__MODULE__{value: :queued, error: nil, is_ok: true}
    end
  end
end
