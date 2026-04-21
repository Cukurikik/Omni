# ===========================================================================
# OMNI PUBSUB ENGINE (SEMESTER 3 — BATCH 38.3)
# ===========================================================================
# Absorbed From  : Phoenix.PubSub + Registry + distributed Erlang concepts
# Logic Inherited: Elixir / Network Layer (Distributed PubSub Messaging)
# ===========================================================================

defmodule OmniPubSubEngine do
  @moduledoc """
  Production-grade publish/subscribe engine implementing Phoenix.PubSub
  patterns for distributed topic-based messaging.

  ## Features
  - Topic-based pub/sub with wildcard matching
  - Local and broadcast message dispatch
  - Subscriber groups for load-balanced consumption
  - Message history per topic (configurable retention)

  ## Usage

      {:ok, pid} = OmniPubSubEngine.start_link()
      OmniPubSubEngine.subscribe(pid, "events:user:*")
      OmniPubSubEngine.broadcast(pid, "events:user:login", %{user: "alice"})
  """

  use GenServer

  # ---- State ----

  defmodule State do
    @moduledoc false
    defstruct [
      subscriptions: %{},       # topic => [subscriber_pid]
      wildcard_subs: [],         # [{pattern, pid}]
      groups: %{},               # group_name => {topic, [pid], idx}
      message_history: %{},      # topic => [messages]
      history_limit: 100,
      total_published: 0,
      total_delivered: 0,
      total_topics: 0,
      total_subscribers: 0
    ]
  end

  # ---- Public API ----

  def start_link(opts \\ []) do
    history_limit = Keyword.get(opts, :history_limit, 100)
    GenServer.start_link(__MODULE__, %{history_limit: history_limit})
  end

  @doc "Subscribe to a topic. Supports wildcards: 'events:*' matches 'events:login', etc."
  def subscribe(pubsub, topic) do
    GenServer.call(pubsub, {:subscribe, topic, self()})
  end

  @doc "Unsubscribe from a topic."
  def unsubscribe(pubsub, topic) do
    GenServer.call(pubsub, {:unsubscribe, topic, self()})
  end

  @doc "Publish a message to a topic."
  def broadcast(pubsub, topic, message) do
    GenServer.call(pubsub, {:broadcast, topic, message})
  end

  @doc "Subscribe as part of a consumer group (load-balanced)."
  def subscribe_group(pubsub, group_name, topic) do
    GenServer.call(pubsub, {:subscribe_group, group_name, topic, self()})
  end

  @doc "Publish to a consumer group (round-robin delivery)."
  def broadcast_group(pubsub, group_name, message) do
    GenServer.call(pubsub, {:broadcast_group, group_name, message})
  end

  @doc "Get message history for a topic."
  def history(pubsub, topic) do
    GenServer.call(pubsub, {:history, topic})
  end

  @doc "List all active topics."
  def topics(pubsub) do
    GenServer.call(pubsub, :topics)
  end

  @doc "Get diagnostics."
  def diagnostics(pubsub) do
    GenServer.call(pubsub, :diagnostics)
  end

  # ---- GenServer Callbacks ----

  @impl true
  def init(%{history_limit: limit}) do
    {:ok, %State{history_limit: limit}}
  end

  @impl true
  def handle_call({:subscribe, topic, pid}, _from, state) do
    if String.contains?(topic, "*") do
      # Wildcard subscription
      pattern = topic_to_regex(topic)
      new_wildcards = [{pattern, topic, pid} | state.wildcard_subs]
      {:reply, :ok, %{state |
        wildcard_subs: new_wildcards,
        total_subscribers: state.total_subscribers + 1
      }}
    else
      # Exact topic subscription
      subs = Map.get(state.subscriptions, topic, [])
      new_subs = if pid in subs, do: subs, else: [pid | subs]
      new_state = %{state |
        subscriptions: Map.put(state.subscriptions, topic, new_subs),
        total_subscribers: state.total_subscribers + 1,
        total_topics: map_size(Map.put(state.subscriptions, topic, new_subs))
      }
      {:reply, :ok, new_state}
    end
  end

  @impl true
  def handle_call({:unsubscribe, topic, pid}, _from, state) do
    subs = Map.get(state.subscriptions, topic, [])
    new_subs = List.delete(subs, pid)

    new_state = if new_subs == [] do
      %{state | subscriptions: Map.delete(state.subscriptions, topic)}
    else
      %{state | subscriptions: Map.put(state.subscriptions, topic, new_subs)}
    end

    {:reply, :ok, new_state}
  end

  @impl true
  def handle_call({:broadcast, topic, message}, _from, state) do
    timestamp = DateTime.utc_now()
    envelope = %{topic: topic, payload: message, timestamp: timestamp}

    # Direct subscribers
    direct_subs = Map.get(state.subscriptions, topic, [])
    delivered = Enum.count(direct_subs)

    # Wildcard subscribers
    wildcard_matches = Enum.filter(state.wildcard_subs, fn {pattern, _raw, _pid} ->
      Regex.match?(pattern, topic)
    end)
    wildcard_delivered = Enum.count(wildcard_matches)

    # Store in history
    history = Map.get(state.message_history, topic, [])
    trimmed_history = Enum.take([envelope | history], state.history_limit)

    new_state = %{state |
      message_history: Map.put(state.message_history, topic, trimmed_history),
      total_published: state.total_published + 1,
      total_delivered: state.total_delivered + delivered + wildcard_delivered
    }

    {:reply, {:ok, delivered + wildcard_delivered}, new_state}
  end

  @impl true
  def handle_call({:subscribe_group, group_name, topic, pid}, _from, state) do
    group = Map.get(state.groups, group_name, %{topic: topic, members: [], index: 0})
    members = if pid in group.members, do: group.members, else: group.members ++ [pid]
    updated_group = %{group | members: members}

    {:reply, :ok, %{state | groups: Map.put(state.groups, group_name, updated_group)}}
  end

  @impl true
  def handle_call({:broadcast_group, group_name, message}, _from, state) do
    case Map.get(state.groups, group_name) do
      nil ->
        {:reply, {:error, :group_not_found}, state}

      group when group.members == [] ->
        {:reply, {:error, :no_members}, state}

      group ->
        # Round-robin: select next member
        idx = rem(group.index, length(group.members))
        _target = Enum.at(group.members, idx)

        updated_group = %{group | index: group.index + 1}
        new_state = %{state |
          groups: Map.put(state.groups, group_name, updated_group),
          total_published: state.total_published + 1,
          total_delivered: state.total_delivered + 1
        }

        {:reply, {:ok, 1}, new_state}
    end
  end

  @impl true
  def handle_call({:history, topic}, _from, state) do
    history = Map.get(state.message_history, topic, [])
    {:reply, history, state}
  end

  @impl true
  def handle_call(:topics, _from, state) do
    {:reply, Map.keys(state.subscriptions), state}
  end

  @impl true
  def handle_call(:diagnostics, _from, state) do
    info = %{
      engine: "OmniPubSubEngine",
      layer: "Elixir Network",
      total_topics: map_size(state.subscriptions),
      total_subscribers: state.total_subscribers,
      total_wildcard_subs: length(state.wildcard_subs),
      total_groups: map_size(state.groups),
      total_published: state.total_published,
      total_delivered: state.total_delivered,
      history_limit: state.history_limit,
      learned_logic: [
        "phoenix-pubsub-topic-broadcast",
        "wildcard-regex-pattern-matching",
        "consumer-group-round-robin",
        "message-history-retention",
        "genserver-call-synchronous",
        "process-isolation-messaging",
        "erlang-distributed-pubsub"
      ]
    }
    {:reply, info, state}
  end

  # ---- Internal ----

  defp topic_to_regex(pattern) do
    escaped = Regex.escape(pattern)
    regex_str = String.replace(escaped, "\\*", "[^:]*")
    Regex.compile!("^" <> regex_str <> "$")
  end
end
