# OMNI Framework - Elixir PubSub Broadcaster for Audiolizr Transcriptions
# Distributes real-time transcription events across the Erlang VM cluster.

defmodule OmniFramework.Audiolizr.Broadcaster do
  @topic "audiolizr_transcriptions"

  def subscribe do
    Phoenix.PubSub.subscribe(OmniFramework.PubSub, @topic)
  end

  def broadcast_transcription(audio_id, text_result) do
    payload = %{
      event: "transcription_complete",
      id: audio_id,
      text: text_result,
      timestamp: System.system_time(:millisecond)
    }
    
    Phoenix.PubSub.broadcast(
      OmniFramework.PubSub,
      @topic,
      {:audiolizr_event, payload}
    )
  end
end
