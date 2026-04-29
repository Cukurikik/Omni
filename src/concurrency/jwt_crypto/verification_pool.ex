defmodule Omni.Concurrency.JWTCrypto.VerificationPool do
  use GenServer

  def start_link(pool_size) do
    GenServer.start_link(__MODULE__, %{pool_size: pool_size, active: 0, queue: []}, name: __MODULE__)
  end

  def verify_token(pid, req_id, token) do
    GenServer.cast(pid, {:verify, req_id, token})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:verify, req_id, token}, state) do
    new_queue = state.queue ++ [{req_id, token}]
    {:noreply, try_dispatch(%{state | queue: new_queue})}
  end

  defp try_dispatch(state) do
    if state.active < state.pool_size and length(state.queue) > 0 do
      [{req_id, _token} | rest] = state.queue
      
      # Simulate HMAC cryptographic processing time deterministically
      Process.send_after(self(), {:done, req_id}, 5)
      
      try_dispatch(%{state | queue: rest, active: state.active + 1})
    else
      state
    end
  end

  @impl true
  def handle_info({:done, req_id}, state) do
    # Log success to demonstrate flow
    # IO.puts("JWT Crypto: Token [#{req_id}] cryptographically verified.")
    new_state = %{state | active: state.active - 1}
    {:noreply, try_dispatch(new_state)}
  end
end
