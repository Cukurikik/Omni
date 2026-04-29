defmodule ChineseLlama.InferencePool do
  defstruct value: nil, error: nil, is_ok: false

  def enqueue_prompt(prompt) do
    if is_nil(prompt) or prompt == "" do
      %__MODULE__{value: nil, error: "Empty prompt", is_ok: false}
    else
      # Elixir actor-based load balancer for Chinese-Llama-2 inference requests
      %__MODULE__{value: :queued, error: nil, is_ok: true}
    end
  end
end
