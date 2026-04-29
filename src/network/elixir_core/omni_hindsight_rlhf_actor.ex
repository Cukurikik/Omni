defmodule Omni.Network.HindsightRLHFActor do
  @moduledoc """
  Actor for 'Chain of Hindsight' RLHF next-token prediction processing.
  Enforces strict Elixir/OTP fault tolerance.
  """
  use GenServer

  def start_link(initial_state) do
    GenServer.start_link(__MODULE__, initial_state, name: __MODULE__)
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:process_hindsight, good_reward, bad_reward}, _from, state) do
    if good_reward <= bad_reward do
      {:reply, {:error, "Good reward must strictly exceed bad reward in CoH"}, state}
    else
      hindsight_delta = good_reward - bad_reward
      {:reply, {:ok, hindsight_delta}, state + 1}
    end
  end
end
