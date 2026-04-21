# ===========================================================================
# OMNI GENSERVER ENGINE (SEMESTER 3 — BATCH 38.8)
# ===========================================================================
# Absorbed From  : Elixir GenServer + Supervisor + Agent + Task
# Logic Inherited: Elixir / Network Layer (OTP Server Abstraction)
# ===========================================================================
#
# By studying OTP GenServer, Mother learned:
#   1. GenServer encapsulates state + message handling in a process
#   2. handle_call = sync request/response
#   3. handle_cast = async fire-and-forget
#   4. handle_info = system/timeout messages
#   5. Supervisor tree restarts failed GenServers automatically

defmodule Omni.GenServerEngine do
  @moduledoc """
  OMNI GenServer Engine: production-grade OTP server abstraction
  with call/cast/info patterns, timeouts, and state management.
  """

  use GenServer

  # ============================================================
  # Client API
  # ============================================================

  @doc "Start a new GenServer with initial state."
  def start_link(opts \\ []) do
    name = Keyword.get(opts, :name, __MODULE__)
    initial_state = Keyword.get(opts, :initial_state, %{})

    state = %{
      data: initial_state,
      total_calls: 0,
      total_casts: 0,
      total_infos: 0,
      created_at: DateTime.utc_now(),
      handlers: %{},
      version: 0
    }

    GenServer.start_link(__MODULE__, state, name: name)
  end

  @doc "Synchronous call: send request and wait for response."
  def call_sync(server, request, timeout \\ 5000) do
    GenServer.call(server, {:call, request}, timeout)
  end

  @doc "Asynchronous cast: fire-and-forget."
  def cast_async(server, message) do
    GenServer.cast(server, {:cast, message})
  end

  @doc "Get current state."
  def get_state(server) do
    GenServer.call(server, :get_state)
  end

  @doc "Update state with a function."
  def update_state(server, update_fn) when is_function(update_fn, 1) do
    GenServer.call(server, {:update_state, update_fn})
  end

  @doc "Register a custom handler."
  def register_handler(server, message_type, handler_fn) do
    GenServer.call(server, {:register_handler, message_type, handler_fn})
  end

  @doc "Get diagnostics."
  def diagnostics(server) do
    GenServer.call(server, :diagnostics)
  end

  # ============================================================
  # Server Callbacks
  # ============================================================

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:call, request}, _from, state) do
    state = %{state | total_calls: state.total_calls + 1}

    # Check for registered handler
    case Map.get(state.handlers, request_type(request)) do
      nil ->
        {:reply, {:ok, state.data}, state}

      handler when is_function(handler, 2) ->
        case handler.(request, state.data) do
          {:reply, response, new_data} ->
            new_state = %{state | data: new_data, version: state.version + 1}
            {:reply, {:ok, response}, new_state}

          {:error, reason} ->
            {:reply, {:error, reason}, state}
        end
    end
  end

  @impl true
  def handle_call(:get_state, _from, state) do
    state = %{state | total_calls: state.total_calls + 1}
    {:reply, {:ok, state.data}, state}
  end

  @impl true
  def handle_call({:update_state, update_fn}, _from, state) do
    state = %{state | total_calls: state.total_calls + 1}

    try do
      new_data = update_fn.(state.data)
      new_state = %{state | data: new_data, version: state.version + 1}
      {:reply, {:ok, new_data}, new_state}
    rescue
      error ->
        {:reply, {:error, Exception.message(error)}, state}
    end
  end

  @impl true
  def handle_call({:register_handler, message_type, handler_fn}, _from, state) do
    handlers = Map.put(state.handlers, message_type, handler_fn)
    new_state = %{state | handlers: handlers}
    {:reply, :ok, new_state}
  end

  @impl true
  def handle_call(:diagnostics, _from, state) do
    diag = %{
      engine: "OmniGenServerEngine",
      layer: "Elixir Network",
      total_calls: state.total_calls,
      total_casts: state.total_casts,
      total_infos: state.total_infos,
      version: state.version,
      registered_handlers: Map.keys(state.handlers),
      uptime_seconds: DateTime.diff(DateTime.utc_now(), state.created_at),
      learned_logic: [
        "genserver-call-sync-reply",
        "genserver-cast-async-noreply",
        "handle-info-system-messages",
        "state-version-tracking",
        "dynamic-handler-registration",
        "try-rescue-error-isolation",
        "supervisor-restart-strategy",
        "otp-process-lifecycle"
      ]
    }
    {:reply, {:ok, diag}, state}
  end

  @impl true
  def handle_cast({:cast, message}, state) do
    state = %{state | total_casts: state.total_casts + 1}

    case Map.get(state.handlers, request_type(message)) do
      nil ->
        {:noreply, state}

      handler when is_function(handler, 2) ->
        case handler.(message, state.data) do
          {:noreply, new_data} ->
            {:noreply, %{state | data: new_data, version: state.version + 1}}
          _ ->
            {:noreply, state}
        end
    end
  end

  @impl true
  def handle_info(msg, state) do
    state = %{state | total_infos: state.total_infos + 1}
    {:noreply, state}
  end

  # ============================================================
  # Private Helpers
  # ============================================================

  defp request_type(request) when is_atom(request), do: request
  defp request_type(request) when is_tuple(request), do: elem(request, 0)
  defp request_type(request) when is_map(request), do: Map.get(request, :type, :unknown)
  defp request_type(_), do: :unknown
end

# ============================================================
# Supervisor Module
# ============================================================

defmodule Omni.GenServerSupervisor do
  @moduledoc "Supervisor for OmniGenServer processes."

  use Supervisor

  def start_link(children_specs) do
    Supervisor.start_link(__MODULE__, children_specs, name: __MODULE__)
  end

  @impl true
  def init(children_specs) do
    children = Enum.map(children_specs, fn spec ->
      {Omni.GenServerEngine, spec}
    end)

    Supervisor.init(children, strategy: :one_for_one)
  end
end
