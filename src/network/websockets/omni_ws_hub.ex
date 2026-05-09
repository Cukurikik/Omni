# omni_ws_hub.ex — WebSocket Broadcast Hub
# Layer: Network / Elixir
#
# PubSub Hub managing real-time WebSocket connections to broadcast
# inference outputs and system metrics to connected UI dashboards.

defmodule Omni.Network.WebSocketHub do
  use GenServer
  require Logger

  # --- Client API ---

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  def broadcast_metrics(payload) do
    GenServer.cast(__MODULE__, {:broadcast, "metrics_topic", payload})
  end

  def subscribe(pid, topic) do
    GenServer.call(__MODULE__, {:subscribe, pid, topic})
  end

  # --- Server Callbacks ---

  @impl true
  def init(_) do
    # State maps topic strings to lists of PIDs
    {:ok, %{}}
  end

  @impl true
  def handle_call({:subscribe, pid, topic}, _from, state) do
    Process.monitor(pid)
    
    current_subscribers = Map.get(state, topic, [])
    new_state = Map.put(state, topic, [pid | current_subscribers])
    
    Logger.info("Process #{inspect(pid)} subscribed to #{topic}")
    {:reply, :ok, new_state}
  end

  @impl true
  def handle_cast({:broadcast, topic, payload}, state) do
    subscribers = Map.get(state, topic, [])
    
    Enum.each(subscribers, fn pid ->
      send(pid, {:ws_message, topic, payload})
    end)
    
    {:noreply, state}
  end

  @impl true
  def handle_info({:DOWN, _ref, :process, pid, _reason}, state) do
    # Remove dead PIDs from all topics
    new_state = Enum.into(state, %{}, fn {topic, pids} ->
      {topic, List.delete(pids, pid)}
    end)
    
    Logger.info("Cleaned up dead subscriber #{inspect(pid)}")
    {:noreply, new_state}
  end
end
