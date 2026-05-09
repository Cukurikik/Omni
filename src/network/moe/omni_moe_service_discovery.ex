defmodule Omni.Network.ServiceRegistry do
  use GenServer

  @moduledoc """
  OMNI MOTHER Production Zero-Mock Service Discovery.
  Provides a fast, in-memory KV registry for resolving internal network IPs
  to specific MoE Experts, utilizing ETS (Erlang Term Storage) for <1ms reads.
  """

  # Client API

  def start_link(_) do
    GenServer.start_link(__MODULE__, nil, name: __MODULE__)
  end

  def register_expert(expert_id, grpc_address) do
    GenServer.call(__MODULE__, {:register, expert_id, grpc_address})
  end

  def resolve_expert(expert_id) do
    # Direct ETS read, bypassing GenServer mailbox for extreme speed
    case :ets.lookup(:omni_expert_registry, expert_id) do
      [{^expert_id, address}] -> {:ok, address}
      [] -> {:error, :not_found}
    end
  end

  # Server Callbacks

  @impl true
  def init(_) do
    # Create public ETS table with read concurrency
    :ets.new(:omni_expert_registry, [:set, :public, :named_table, read_concurrency: true])
    {:ok, %{}}
  end

  @impl true
  def handle_call({:register, expert_id, address}, _from, state) do
    # Write to ETS table
    :ets.insert(:omni_expert_registry, {expert_id, address})
    {:reply, :ok, state}
  end
end
