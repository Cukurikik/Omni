# ===========================================================================
# OMNI PLUG ENGINE (SEMESTER 3 — BATCH 38.8)
# ===========================================================================
# Absorbed From  : Plug + Phoenix Router + Plug.Conn + Middleware pipeline
# Logic Inherited: Elixir / Network Layer (HTTP Pipeline & Request Processing)
# ===========================================================================
#
# By studying Plug and Phoenix, Mother learned:
#   1. Plug.Conn is the immutable request/response struct
#   2. Plugs are composable middleware: init/2 + call/2
#   3. Plug.Router provides route matching with macros
#   4. Plug.Builder chains multiple plugs into a pipeline
#   5. Halting: conn.halted? prevents further plug execution

defmodule Omni.PlugEngine do
  @moduledoc """
  OMNI Plug Engine: HTTP pipeline processing with composable
  plugs, route matching, and middleware chain.
  """

  # ============================================================
  # PART 1: Connection Struct
  # ============================================================

  defmodule Conn do
    @moduledoc "Immutable HTTP connection (request + response)."

    defstruct [
      method: "GET",
      path: "/",
      headers: %{},
      params: %{},
      query_string: "",
      body: nil,
      status: nil,
      resp_headers: %{},
      resp_body: nil,
      assigns: %{},
      halted: false,
      private: %{},
      request_id: nil
    ]

    @type t :: %__MODULE__{}

    @doc "Set response status and body."
    def send_resp(%__MODULE__{} = conn, status, body) do
      %{conn | status: status, resp_body: body}
    end

    @doc "Set a response header."
    def put_resp_header(%__MODULE__{} = conn, key, value) do
      %{conn | resp_headers: Map.put(conn.resp_headers, key, value)}
    end

    @doc "Assign a value to the connection."
    def assign(%__MODULE__{} = conn, key, value) do
      %{conn | assigns: Map.put(conn.assigns, key, value)}
    end

    @doc "Halt the pipeline (no more plugs will run)."
    def halt(%__MODULE__{} = conn) do
      %{conn | halted: true}
    end

    @doc "Get a request header value."
    def get_req_header(%__MODULE__{} = conn, key) do
      Map.get(conn.headers, String.downcase(key))
    end

    @doc "Build a new connection from request parameters."
    def build(method, path, opts \\ []) do
      %__MODULE__{
        method: String.upcase(to_string(method)),
        path: path,
        headers: Keyword.get(opts, :headers, %{}),
        params: Keyword.get(opts, :params, %{}),
        body: Keyword.get(opts, :body, nil),
        query_string: Keyword.get(opts, :query_string, ""),
        request_id: generate_request_id()
      }
    end

    defp generate_request_id do
      :crypto.strong_rand_bytes(8) |> Base.hex_encode32(case: :lower, padding: false)
    end
  end

  # ============================================================
  # PART 2: Plug Behavior
  # ============================================================

  @doc "Plug behavior: init/1 returns options, call/2 processes connection."
  @callback init(opts :: keyword()) :: keyword()
  @callback call(conn :: Conn.t(), opts :: keyword()) :: Conn.t()

  # ============================================================
  # PART 3: Built-in Plugs
  # ============================================================

  defmodule Logger do
    @moduledoc "Logging plug: logs method, path, status, and duration."
    @behaviour Omni.PlugEngine

    @impl true
    def init(opts), do: opts

    @impl true
    def call(%Conn{} = conn, _opts) do
      start = System.monotonic_time(:microsecond)

      conn
      |> Conn.assign(:request_start, start)
      |> tap(fn c ->
        IO.puts("[#{c.method}] #{c.path} - request_id=#{c.request_id}")
      end)
    end
  end

  defmodule RequestId do
    @moduledoc "Ensures every request has a unique ID."
    @behaviour Omni.PlugEngine

    @impl true
    def init(opts), do: opts

    @impl true
    def call(%Conn{} = conn, _opts) do
      case conn.request_id do
        nil ->
          id = :crypto.strong_rand_bytes(8) |> Base.hex_encode32(case: :lower, padding: false)
          %{conn | request_id: id}
          |> Conn.put_resp_header("x-request-id", id)
        _ ->
          conn
      end
    end
  end

  defmodule Cors do
    @moduledoc "CORS middleware plug."
    @behaviour Omni.PlugEngine

    @impl true
    def init(opts), do: opts

    @impl true
    def call(%Conn{} = conn, opts) do
      origin = Keyword.get(opts, :origin, "*")
      methods = Keyword.get(opts, :methods, "GET, POST, PUT, DELETE, OPTIONS")

      conn
      |> Conn.put_resp_header("access-control-allow-origin", origin)
      |> Conn.put_resp_header("access-control-allow-methods", methods)
      |> Conn.put_resp_header("access-control-allow-headers", "content-type, authorization")
      |> handle_preflight()
    end

    defp handle_preflight(%Conn{method: "OPTIONS"} = conn) do
      conn |> Conn.send_resp(204, "") |> Conn.halt()
    end
    defp handle_preflight(conn), do: conn
  end

  defmodule Auth do
    @moduledoc "Bearer token authentication plug."
    @behaviour Omni.PlugEngine

    @impl true
    def init(opts), do: opts

    @impl true
    def call(%Conn{} = conn, opts) do
      valid_tokens = Keyword.get(opts, :tokens, MapSet.new())

      case Conn.get_req_header(conn, "authorization") do
        "Bearer " <> token when token in valid_tokens ->
          Conn.assign(conn, :authenticated, true)
          |> Conn.assign(:token, token)

        _ ->
          conn
          |> Conn.send_resp(401, "Unauthorized")
          |> Conn.halt()
      end
    end
  end

  # ============================================================
  # PART 4: Pipeline Builder
  # ============================================================

  defmodule Pipeline do
    @moduledoc "Chains multiple plugs into a processing pipeline."

    defstruct plugs: [], total_requests: 0

    def new, do: %__MODULE__{}

    def plug(%__MODULE__{} = pipeline, plug_module, opts \\ []) do
      initialized_opts = plug_module.init(opts)
      %{pipeline | plugs: pipeline.plugs ++ [{plug_module, initialized_opts}]}
    end

    def call(%__MODULE__{} = pipeline, %Conn{} = conn) do
      pipeline = %{pipeline | total_requests: pipeline.total_requests + 1}

      final_conn = Enum.reduce_while(pipeline.plugs, conn, fn {plug_mod, opts}, acc ->
        if acc.halted do
          {:halt, acc}
        else
          result = plug_mod.call(acc, opts)
          {:cont, result}
        end
      end)

      {final_conn, pipeline}
    end

    def diagnostics(%__MODULE__{} = pipeline) do
      %{
        engine: "OmniPlugEngine",
        layer: "Elixir Network",
        total_plugs: length(pipeline.plugs),
        plug_names: Enum.map(pipeline.plugs, fn {mod, _} -> inspect(mod) end),
        total_requests: pipeline.total_requests,
        learned_logic: [
          "plug-conn-immutable-transform",
          "init-call-two-phase-plug",
          "halt-short-circuit-pipeline",
          "reduce-while-plug-chain",
          "cors-preflight-options",
          "bearer-token-auth-pattern",
          "request-id-tracing",
          "pipeline-builder-composition"
        ]
      }
    end
  end
end
