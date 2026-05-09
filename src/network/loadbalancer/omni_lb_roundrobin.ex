# omni_lb_roundrobin.ex — Round Robin Load Balancer
# Layer: Network / Elixir
#
# OTP module managing a pool of inference worker connections and distributing
# incoming gRPC requests evenly across them using a round-robin strategy.

defmodule Omni.Network.LoadBalancer do
  use GenServer
  require Logger

  # State: {queue_of_endpoints, map_of_endpoint_health}

  def start_link(endpoints) do
    GenServer.start_link(__MODULE__, endpoints, name: __MODULE__)
  end

  @doc """
  Returns the next healthy endpoint to route a request to.
  """
  def next_endpoint() do
    GenServer.call(__MODULE__, :next_endpoint)
  end

  def mark_failed(endpoint) do
    GenServer.cast(__MODULE__, {:mark_failed, endpoint})
  end

  # --- Callbacks ---

  @impl true
  def init(endpoints) do
    # Initialize with all endpoints marked as healthy
    health_map = Map.new(endpoints, fn ep -> {ep, :healthy} end)
    {:ok, {endpoints, health_map}}
  end

  @impl true
  def handle_call(:next_endpoint, _from, {queue, health_map}) do
    {endpoint, new_queue} = find_next_healthy(queue, health_map, length(queue))
    
    if endpoint == nil do
      {:reply, {:error, :no_healthy_endpoints}, {new_queue, health_map}}
    else
      {:reply, {:ok, endpoint}, {new_queue, health_map}}
    end
  end

  @impl true
  def handle_cast({:mark_failed, endpoint}, {queue, health_map}) do
    Logger.warn("Marking endpoint #{endpoint} as failed.")
    new_health = Map.put(health_map, endpoint, :failed)
    {:noreply, {queue, new_health}}
  end

  # Helper to rotate queue until a healthy endpoint is found
  defp find_next_healthy(_queue, _health_map, 0), do: {nil, []}
  defp find_next_healthy([current | rest], health_map, attempts_left) do
    status = Map.get(health_map, current, :failed)
    
    if status == :healthy do
      # Move current to end of queue (Round Robin)
      {current, rest ++ [current]}
    else
      # Endpoint failed, skip it and try next
      find_next_healthy(rest ++ [current], health_map, attempts_left - 1)
    end
  end
end
