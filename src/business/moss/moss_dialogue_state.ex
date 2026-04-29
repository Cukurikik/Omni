# OMNI Divine Memory Integration: Inspired by MOSS
# Business Layer - Elixir GenServer Actor for Dialogue State Management

defmodule Omni.Moss.DialogueState do
  use GenServer

  @max_history_length 100
  @max_tokens_per_message 4096

  # Omni Error Structure
  defmodule OmniError do
    defstruct [:code, :message]
  end

  # Client API
  def start_link(session_id) do
    GenServer.start_link(__MODULE__, %{session_id: session_id, history: []}, name: via_tuple(session_id))
  end

  def add_message(session_id, role, content) do
    GenServer.call(via_tuple(session_id), {:add_message, role, content})
  end

  def get_history(session_id) do
    GenServer.call(via_tuple(session_id), :get_history)
  end

  # Server Callbacks
  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:add_message, _role, content}, _from, state) when byte_size(content) > @max_tokens_per_message do
    err = %OmniError{code: 413, message: "Message exceeds maximum physical token byte size."}
    {:reply, {:error, err}, state}
  end

  @impl true
  def handle_call({:add_message, role, content}, _from, state) do
    new_msg = %{role: role, content: content, timestamp: System.system_time(:millisecond)}
    new_history = [new_msg | state.history] |> Enum.take(@max_history_length)
    
    new_state = %{state | history: new_history}
    {:reply, {:ok, new_history}, new_state}
  end

  @impl true
  def handle_call(:get_history, _from, state) do
    {:reply, {:ok, Enum.reverse(state.history)}, state}
  end

  defp via_tuple(session_id), do: {:global, {:moss_session, session_id}}
end
