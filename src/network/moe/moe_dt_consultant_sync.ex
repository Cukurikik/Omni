# moe_dt_consultant_sync.ex — Network Layer: DT Consultant Sync
# Elixir GenServer synchronizing state across multiple digital transformation assistant bots.

defmodule Omni.Network.DTConsultantSync do
  use GenServer

  # Client API
  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, :ok, opts ++ [name: __MODULE__])
  end

  def update_session_state(session_id, state_data) do
    GenServer.cast(__MODULE__, {:update_state, session_id, state_data})
  end

  def get_session_state(session_id) do
    GenServer.call(__MODULE__, {:get_state, session_id})
  end

  # Server Callbacks
  @impl true
  def init(:ok) do
    # Map storing active consultant session states
    {:ok, %{}}
  end

  @impl true
  def handle_cast({:update_state, session_id, state_data}, state) do
    new_state = Map.put(state, session_id, state_data)
    {:noreply, new_state}
  end

  @impl true
  def handle_call({:get_state, session_id}, _from, state) do
    session_data = Map.get(state, session_id, %{status: "not_found"})
    {:reply, session_data, state}
  end
end
