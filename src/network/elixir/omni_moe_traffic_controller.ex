defmodule Omni.MoE.TrafficController do
  @moduledoc """
  OMNI Framework - MoE Traffic Controller (Elixir/OTP)
  High-concurrency reverse proxy and rate-limiter for MoE API endpoints.
  Uses the Actor Model to manage state independently per tenant without locking.
  """
  use GenServer

  require Logger

  # Client API

  def start_link(opts) do
    tenant_id = Keyword.fetch!(opts, :tenant_id)
    GenServer.start_link(__MODULE__, opts, name: via_tuple(tenant_id))
  end

  def request_access(tenant_id, requested_tokens) do
    GenServer.call(via_tuple(tenant_id), {:request_access, requested_tokens})
  end

  # Server Callbacks

  @impl true
  def init(opts) do
    tenant_id = Keyword.fetch!(opts, :tenant_id)
    limit = Keyword.get(opts, :limit, 100_000)
    
    Logger.info("OMNI Elixir: Started Traffic Controller for Tenant #{tenant_id} (Limit: #{limit})")
    
    # Reset tokens every minute
    :timer.send_interval(60_000, :reset_quota)

    {:ok, %{tenant_id: tenant_id, limit: limit, used: 0}}
  end

  @impl true
  def handle_call({:request_access, requested_tokens}, _from, state) do
    if state.used + requested_tokens <= state.limit do
      new_state = %{state | used: state.used + requested_tokens}
      {:reply, :ok, new_state}
    else
      Logger.warning("OMNI Elixir: Tenant #{state.tenant_id} hit rate limit. Used: #{state.used}, Requested: #{requested_tokens}")
      {:reply, {:error, :rate_limited}, state}
    end
  end

  @impl true
  def handle_info(:reset_quota, state) do
    {:noreply, %{state | used: 0}}
  end

  # Helpers

  defp via_tuple(tenant_id) do
    # In a real distributed cluster, this uses Horde or Swarm. Local Registry for now.
    {:via, Registry, {Omni.TenantRegistry, tenant_id}}
  end
end
