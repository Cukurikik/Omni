defmodule OmniFramework.Business.CheckoutSaga do
  @moduledoc """
  OMNI Saga pattern implementation in Elixir for distributed transactions.
  """
  use GenServer

  def start_link(initial_state) do
    GenServer.start_link(__MODULE__, initial_state, name: __MODULE__)
  end

  def init(state) do
    {:ok, state}
  end

  def process_checkout(user_id, amount) do
    GenServer.cast(__MODULE__, {:checkout, user_id, amount})
  end

  def handle_cast({:checkout, user_id, amount}, state) do
    # Step 1: Reserve Inventory
    with {:ok, _} <- reserve_inventory(user_id),
         # Step 2: Charge Payment
         {:ok, _} <- charge_payment(user_id, amount),
         # Step 3: Dispatch Order
         {:ok, _} <- dispatch_order(user_id) do
      {:noreply, state}
    else
      {:error, reason} ->
        compensate_transaction(user_id, reason)
        {:noreply, state}
    end
  end

  defp reserve_inventory(_user_id), do: {:ok, :reserved}
  defp charge_payment(_user_id, _amount), do: {:ok, :charged}
  defp dispatch_order(_user_id), do: {:ok, :dispatched}
  
  defp compensate_transaction(user_id, reason) do
    IO.puts("Rolling back transaction for #{user_id}: #{reason}")
  end
end
