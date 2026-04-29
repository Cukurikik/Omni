defmodule Omni.Concurrency.DistributedRegistry do
  use GenServer

  @impl true
  def init(init_arg) do
    {:ok, %{actors: %{}, metrics: %{registrations: 0}}}
  end

  @impl true
  def handle_call({:register, actor_id, pid}, _from, state) do
    if Map.has_key?(state.actors, actor_id) do
      {:reply, {:error, :already_registered}, state}
    else
      new_state = state
        |> put_in([:actors, actor_id], pid)
        |> update_in([:metrics, :registrations], &(&1 + 1))
      {:reply, :ok, new_state}
    end
  end

  @impl true
  def handle_call({:lookup, actor_id}, _from, state) do
    case Map.fetch(state.actors, actor_id) do
      {:ok, pid} -> {:reply, {:ok, pid}, state}
      :error -> {:reply, {:error, :not_found}, state}
    end
  end
end
