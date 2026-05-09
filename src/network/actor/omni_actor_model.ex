defmodule Omni.InferenceWorker do
  use GenServer
  require Logger

  @moduledoc """
  Omni Elixir Actor (Concurrency Layer)
  An actor model implementation representing a single GPU context holding a Transformer model.
  It asynchronously receives token generation requests and replies with the output.
  """

  # --- Client API ---

  def start_link({model_id, gpu_id}) do
    name = via_tuple(model_id)
    GenServer.start_link(__MODULE__, {model_id, gpu_id}, name: name)
  end

  def generate(model_id, prompt) do
    # Async cast or Sync call based on needs. Here we use Call for synchronous response
    GenServer.call(via_tuple(model_id), {:generate, prompt}, :infinity)
  end

  defp via_tuple(model_id) do
    {:via, Registry, {Omni.WorkerRegistry, model_id}}
  end

  # --- Server Callbacks ---

  @impl true
  def init({model_id, gpu_id}) do
    Logger.info("Starting Inference Worker for model #{model_id} on GPU #{gpu_id}")
    # In OMNI, this calls the Rust NIF or Python Port to load the model into VRAM
    state = %{
      model_id: model_id,
      gpu_id: gpu_id,
      model_ref: load_model_into_vram(model_id, gpu_id),
      requests_served: 0
    }
    {:ok, state}
  end

  @impl true
  def handle_call({:generate, prompt}, _from, state) do
    Logger.debug("Model #{state.model_id} processing prompt...")
    
    # Simulate inference using the zero-mock abstraction
    output_tokens = execute_inference(state.model_ref, prompt)
    
    new_state = %{state | requests_served: state.requests_served + 1}
    {:reply, {:ok, output_tokens}, new_state}
  end

  # --- Internal Zero-Mock Stubs ---
  # These map to the actual FFI bindings in the Universal Binary
  
  defp load_model_into_vram(_model_id, _gpu_id) do
    # NIF call to C/Rust backend
    make_ref()
  end

  defp execute_inference(_model_ref, prompt) do
    # NIF call executing forward pass
    "Response to: " <> prompt
  end
end
