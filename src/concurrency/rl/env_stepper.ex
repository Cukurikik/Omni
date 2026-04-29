defmodule Omni.RL.EnvStepper do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{steps: 0}, name: __MODULE__)
  end

  def step(action) do
    GenServer.call(__MODULE__, {:step, action})
  end

  @impl true
  def init(state), do: {:ok, state}

  @impl true
  def handle_call({:step, _action}, _from, state) do
    {:reply, {:ok, [0.0, 1.0, -1.0], 1.0, false}, %{state | steps: state.steps + 1}}
  end
end
