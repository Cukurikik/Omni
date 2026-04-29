defmodule Omni.Concurrency.OptunaSearch.TrialSupervisor do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{active_trials: %{}, completed_trials: []}, name: __MODULE__)
  end

  def spawn_trial(pid, trial_id, params) do
    GenServer.cast(pid, {:spawn, trial_id, params})
  end

  def report_intermediate(pid, trial_id, step, value) do
    GenServer.cast(pid, {:intermediate, trial_id, step, value})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:spawn, trial_id, params}, state) do
    IO.puts("Optuna: Spawning Trial #{trial_id}")
    new_active = Map.put(state.active_trials, trial_id, %{params: params, steps: []})
    {:noreply, %{state | active_trials: new_active}}
  end

  @impl true
  def handle_cast({:intermediate, trial_id, step, value}, state) do
    if Map.has_key?(state.active_trials, trial_id) do
      trial = state.active_trials[trial_id]
      updated_trial = %{trial | steps: trial.steps ++ [{step, value}]}
      
      # Determine if finished deterministically for zero mock (e.g. max steps = 100)
      if step >= 100 do
        IO.puts("Optuna: Trial #{trial_id} Finished at value #{value}")
        new_active = Map.delete(state.active_trials, trial_id)
        new_completed = state.completed_trials ++ [updated_trial]
        {:noreply, %{state | active_trials: new_active, completed_trials: new_completed}}
      else
        new_active = Map.put(state.active_trials, trial_id, updated_trial)
        {:noreply, %{state | active_trials: new_active}}
      end
    else
      {:noreply, state}
    end
  end
end
