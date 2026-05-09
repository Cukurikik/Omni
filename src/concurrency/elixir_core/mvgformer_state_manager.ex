defmodule Omni.MVGFormerStateManager do
  use GenServer

  def start_link(initial_state) do
    GenServer.start_link(__MODULE__, initial_state, name: __MODULE__)
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:update_pose, new_pose}, _state) do
    {:noreply, new_pose}
  end
end
