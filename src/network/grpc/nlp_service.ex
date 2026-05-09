#=============================================================================
# OMNI NETWORK LAYER — NLP GRPC SERVICE (ELIXIR)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Elixir gRPC handler providing highly concurrent endpoints for 
#              NLP inference (NER, Sentiment, Hierarchy encoding).
#=============================================================================

defmodule Omni.Network.NLPService do
  @moduledoc """
  OMNI IDIOM: Elixir concurrency layer bridging to Python/Mojo Compute.
  """
  use GRPC.Server, service: Omni.Proto.NLP.Service

  require Logger

  @spec analyze_sentiment(Omni.Proto.SentimentRequest.t(), GRPC.Server.Stream.t()) :: Omni.Proto.SentimentResponse.t()
  def analyze_sentiment(request, _stream) do
    Logger.debug("Received sentiment request for text length: #{byte_size(request.text)}")
    
    # Delegate to Omni Event Loop -> Python Compute (Sentiment BERT)
    case OmniBridge.call_sync("compute.nlp.sentiment", %{text: request.text}) do
      {:ok, result} ->
        Omni.Proto.SentimentResponse.new(
          positive: result["positive"],
          neutral: result["neutral"],
          negative: result["negative"]
        )
      {:error, reason} ->
        Logger.error("Sentiment analysis failed: #{reason}")
        raise GRPC.RPCError, status: :internal, message: "Compute layer failure"
    end
  end

  @spec extract_entities(Omni.Proto.NERRequest.t(), GRPC.Server.Stream.t()) :: Omni.Proto.NERResponse.t()
  def extract_entities(request, _stream) do
    case OmniBridge.call_sync("compute.nlp.ner", %{text: request.text}) do
      {:ok, result} ->
        entities = Enum.map(result["entities"], fn e -> 
          Omni.Proto.Entity.new(text: e["entity"], label: e["label"]) 
        end)
        Omni.Proto.NERResponse.new(entities: entities)
      {:error, reason} ->
        raise GRPC.RPCError, status: :internal, message: reason
    end
  end
end
