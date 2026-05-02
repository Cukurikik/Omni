# @omni-domain Concurrency Layer (Ray Serve)
# @omni-source ray-project/ray
# @omni-description Ray Serve Worker mimicking distributed serving replica.
# @omni-requirement zero-mock, monadic-error

defmodule RayServe.Worker do
  @moduledoc """
  Distributed worker mimicking Ray Serve replica processing.
  """
  use GenServer

  def start_link(model_name) do
    GenServer.start_link(__MODULE__, model_name, name: via_tuple(model_name))
  end

  def predict(model_name, input_data) do
    if is_binary(input_data) do
      GenServer.call(via_tuple(model_name), {:predict, input_data})
    else
      {:error, "Input data must be binary"}
    end
  end

  defp via_tuple(name) do
    {:global, {:ray_serve, name}}
  end

  @impl true
  def init(model_name) do
    {:ok, %{model: model_name, request_count: 0}}
  end

  @impl true
  def handle_call({:predict, data}, _from, state) do
    result = "Prediction for #{state.model}: #{byte_size(data)} bytes processed"
    new_state = %{state | request_count: state.request_count + 1}
    {:reply, {:ok, result}, new_state}
  end
end
