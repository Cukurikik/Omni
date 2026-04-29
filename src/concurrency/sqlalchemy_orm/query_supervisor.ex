defmodule Omni.Concurrency.SqlAlchemyORM.QuerySupervisor do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{active_queries: 0}, name: __MODULE__)
  end

  def execute_query(pid, query_hash) do
    GenServer.cast(pid, {:execute, query_hash})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:execute, query_hash}, state) do
    IO.puts("ORM Supervisor: Dispatching Query [#{query_hash}] to connection pool")
    
    # Simulate DB latency deterministically
    Process.send_after(self(), :query_done, 20)
    
    {:noreply, %{state | active_queries: state.active_queries + 1}}
  end

  @impl true
  def handle_info(:query_done, state) do
    new_active = max(0, state.active_queries - 1)
    IO.puts("ORM Supervisor: Query complete. Active queries: #{new_active}")
    {:noreply, %{state | active_queries: new_active}}
  end
end
