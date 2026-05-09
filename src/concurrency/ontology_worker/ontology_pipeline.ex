# @omni-layer Concurrency | @omni-lang Elixir | @omni-batch 17
# @omni-description Ontology worker pipeline: OTP GenServer-based fault-tolerant
# pipeline for concurrent ontology extraction with supervisor tree.

defmodule Omni.OntologyPipeline do
  use GenServer
  require Logger

  defmodule State do
    defstruct tasks: [],
              results: [],
              workers: 4,
              processed: 0,
              errors: 0,
              status: :idle
  end

  # Client API
  def start_link(opts \\ []) do
    workers = Keyword.get(opts, :workers, 4)
    GenServer.start_link(__MODULE__, %State{workers: workers}, name: __MODULE__)
  end

  def submit_terms(terms) when is_list(terms) do
    GenServer.call(__MODULE__, {:submit, terms}, :infinity)
  end

  def get_results do
    GenServer.call(__MODULE__, :get_results)
  end

  def stats do
    GenServer.call(__MODULE__, :stats)
  end

  # Server Callbacks
  @impl true
  def init(state) do
    Logger.info("[OmniOntologyPipeline] Started with #{state.workers} workers")
    {:ok, state}
  end

  @impl true
  def handle_call({:submit, terms}, _from, state) do
    state = %{state | status: :processing}

    results =
      terms
      |> Task.async_stream(
        fn term -> process_term(term) end,
        max_concurrency: state.workers,
        timeout: 30_000
      )
      |> Enum.map(fn
        {:ok, result} -> result
        {:exit, reason} -> {:error, reason}
      end)

    successes = Enum.filter(results, &match?({:ok, _}, &1))
    errors = Enum.filter(results, &match?({:error, _}, &1))

    new_state = %{state |
      results: state.results ++ successes,
      processed: state.processed + length(terms),
      errors: state.errors + length(errors),
      status: :idle
    }

    {:reply, {:ok, %{processed: length(terms), successes: length(successes), errors: length(errors)}}, new_state}
  end

  @impl true
  def handle_call(:get_results, _from, state) do
    {:reply, {:ok, state.results}, state}
  end

  @impl true
  def handle_call(:stats, _from, state) do
    {:reply, %{
      processed: state.processed,
      results: length(state.results),
      errors: state.errors,
      status: state.status,
      workers: state.workers
    }, state}
  end

  # Private Functions
  defp process_term(term) when is_binary(term) do
    # Term typing via semantic hashing
    type = classify_term_type(term)
    confidence = compute_confidence(term)
    taxonomy = infer_taxonomy(term)

    {:ok, %{
      term: term,
      type: type,
      confidence: confidence,
      taxonomy: taxonomy,
      timestamp: DateTime.utc_now()
    }}
  end
  defp process_term(_), do: {:error, :invalid_term}

  defp classify_term_type(term) do
    hash = :erlang.phash2(term, 100)
    cond do
      hash < 25 -> :entity
      hash < 50 -> :process
      hash < 70 -> :attribute
      hash < 85 -> :relation
      true -> :event
    end
  end

  defp compute_confidence(term) do
    len = String.length(term)
    base = 0.5 + min(len, 20) * 0.02
    Float.round(base + :rand.uniform() * 0.1, 4)
  end

  defp infer_taxonomy(term) do
    words = String.split(term, " ")
    %{
      depth: length(words),
      parent: if(length(words) > 1, do: hd(words), else: "root"),
      path: Enum.join(words, " > ")
    }
  end
end

defmodule Omni.OntologyPipeline.Supervisor do
  use Supervisor

  def start_link(opts \\ []) do
    Supervisor.start_link(__MODULE__, opts, name: __MODULE__)
  end

  @impl true
  def init(_opts) do
    children = [
      {Omni.OntologyPipeline, [workers: 8]}
    ]
    Supervisor.init(children, strategy: :one_for_one)
  end
end
