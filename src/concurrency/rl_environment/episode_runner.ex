defmodule Omni.Concurrency.RLEnvironment.EpisodeRunner do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{episode: 0, steps: 0, is_running: false}, name: __MODULE__)
  end

  def start_episode(pid) do
    GenServer.cast(pid, :start_episode)
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast(:start_episode, state) do
    new_state = %{state | episode: state.episode + 1, steps: 0, is_running: true}
    Process.send_after(self(), :step, 100)
    {:noreply, new_state}
  end

  @impl true
  def handle_info(:step, state) do
    if state.is_running do
      new_steps = state.steps + 1
      
      # Terminate episode after 50 steps
      if new_steps >= 50 do
        {:noreply, %{state | steps: new_steps, is_running: false}}
      else
        Process.send_after(self(), :step, 100)
        {:noreply, %{state | steps: new_steps}}
      end
    else
      {:noreply, state}
    end
  end
end
