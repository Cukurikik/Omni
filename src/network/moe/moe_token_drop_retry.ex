# moe_token_drop_retry.ex — Network / Elixir
# Layer: Network / Reliability — Background Token Retry
#
# When an expert capacity is exceeded, tokens are dropped. This Elixir module 
# uses the BEAM VM's Actor model to catch dropped tokens and asynchronously 
# retry them or route them to a fallback generalized expert without blocking 
# the main inference stream.

defmodule Omni.MoE.DropQueue do
  use GenServer
  require Logger

  # --- Client API ---

  def start_link(_opts) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  def enqueue_dropped_token(token_data, original_expert_id) do
    GenServer.cast(__MODULE__, {:enqueue, token_data, original_expert_id})
  end

  # --- Server Callbacks ---

  @impl true
  def init(_state) do
    Logger.info("[MoE Elixir] Started Dropped Token Retry Queue Actor.")
    # State holds a simple queue map: %{expert_id => [tokens]}
    {:ok, %{}}
  end

  @impl true
  def handle_cast({:enqueue, token, expert_id}, state) do
    # Add token to the back of the line for this expert
    current_queue = Map.get(state, expert_id, [])
    new_state = Map.put(state, expert_id, current_queue ++ [token])
    
    # If the queue gets too long, we trigger an immediate fallback route
    if length(Map.get(new_state, expert_id)) > 100 do
      Logger.warn("[MoE Elixir] Expert #{expert_id} queue overloaded. Routing to fallback.")
      route_to_fallback(Map.get(new_state, expert_id))
      {:noreply, Map.put(new_state, expert_id, [])}
    else
      # Schedule a retry attempt in 50ms
      Process.send_after(self(), {:retry, expert_id}, 50)
      {:noreply, new_state}
    end
  end

  @impl true
  def handle_info({:retry, expert_id}, state) do
    queue = Map.get(state, expert_id, [])
    
    case queue do
      [] -> 
        {:noreply, state}
      [token | rest] ->
        # Attempt to inject back into the C++/Rust inference engine (mocked)
        # Logger.debug("[MoE Elixir] Retrying token for Expert #{expert_id}")
        {:noreply, Map.put(state, expert_id, rest)}
    end
  end

  defp route_to_fallback(_tokens) do
    # Simulated routing to a denser, general-purpose LLM fallback
    # OMNI Gateway handles the actual grpc call
  end
end
