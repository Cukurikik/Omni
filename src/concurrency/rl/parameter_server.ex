defmodule Omni.Concurrency.RL.ParameterServer do
  @moduledoc """
  OMNI RL - Distributed Parameter Server
  Elixir OTP Actor for managing global model weights across distributed workers.
  """
  use GenServer

  # Client API

  def start_link(initial_weights) do
    GenServer.start_link(__MODULE__, initial_weights, name: __MODULE__)
  end

  def get_weights do
    GenServer.call(__MODULE__, :get_weights)
  end

  def update_weights(gradients) do
    GenServer.cast(__MODULE__, {:apply_gradients, gradients})
  end

  # Server Callbacks

  @impl true
  def init(initial_weights) do
    # Weights are stored in ETS for fast concurrent reads by workers if needed,
    # but here we keep it in actor state for strict consistency.
    {:ok, %{weights: initial_weights, version: 0}}
  end

  @impl true
  def handle_call(:get_weights, _from, state) do
    {:reply, {:ok, state.weights, state.version}, state}
  end

  @impl true
  def handle_cast({:apply_gradients, gradients}, state) do
    case apply_gradients(state.weights, gradients) do
      {:ok, new_weights} ->
        {:noreply, %{state | weights: new_weights, version: state.version + 1}}

      {:error, reason} ->
        # Monadic error handling - log and drop, do not crash the parameter server
        # In a real OMNI system, this would emit an event to the Kafka error topic
        IO.puts("Failed to apply gradients: #{reason}")
        {:noreply, state}
    end
  end

  # Internal Math Logic
  defp apply_gradients(weights, gradients) do
    if length(weights) != length(gradients) do
      {:error, "Dimension mismatch"}
    else
      # Simple SGD step for demonstration. In practice, use Adam state.
      learning_rate = 0.001
      new_weights = Enum.zip(weights, gradients)
                    |> Enum.map(fn {w, g} -> w - (learning_rate * g) end)
      {:ok, new_weights}
    end
  end
end
