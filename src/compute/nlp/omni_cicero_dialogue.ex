defmodule Omni.CICERO.Dialogue do
  @moduledoc """
  CICERO: Commonsense Inference in Dialogue
  Elixir Actor model for managing stateful, multi-turn commonsense reasoning dialogue trees.
  """

  use GenServer

  # Represents a single dialogue turn
  defmodule Turn do
    @enforce_keys [:speaker, :utterance, :commonsense_inferences]
    defstruct [:speaker, :utterance, :commonsense_inferences]
  end

  # --- Client API ---

  def start_link(dialogue_id) do
    GenServer.start_link(__MODULE__, %{id: dialogue_id, history: []}, name: via_tuple(dialogue_id))
  end

  def add_utterance(dialogue_id, speaker, utterance) do
    GenServer.call(via_tuple(dialogue_id), {:add_utterance, speaker, utterance})
  end

  def get_context(dialogue_id) do
    GenServer.call(via_tuple(dialogue_id), :get_context)
  end

  defp via_tuple(id), do: {:via, Registry, {Omni.DialogueRegistry, id}}

  # --- Server Callbacks ---

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:add_utterance, speaker, utterance}, _from, state) do
    # Trigger an asynchronous inference pipeline (simulated)
    # The transformer model will generate commonsense relations (xIntent, xReact, etc.)
    inferences = generate_commonsense_inferences(utterance)
    
    turn = %Turn{
      speaker: speaker,
      utterance: utterance,
      commonsense_inferences: inferences
    }
    
    new_state = %{state | history: [turn | state.history]}
    {:reply, :ok, new_state}
  end

  @impl true
  def handle_call(:get_context, _from, state) do
    # Return reversed history so chronological order is maintained
    {:reply, Enum.reverse(state.history), state}
  end

  # --- Internal Logic ---

  defp generate_commonsense_inferences(utterance) do
    # In a true Omni deployment, this dispatches via Rust NIF or gRPC to the RoBERTa model.
    cond do
      String.contains?(String.downcase(utterance), "hungry") ->
        %{"xIntent" => "to eat food", "xNeed" => "find a restaurant"}
      String.contains?(String.downcase(utterance), "tired") ->
        %{"xIntent" => "to sleep", "xReact" => "feels exhausted"}
      true ->
        %{"xAttr" => "neutral"}
    end
  end
end
