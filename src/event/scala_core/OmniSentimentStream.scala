// Omni Sentiment Stream (Scala)
// Event Layer: Streaming sentiment events for healthcare analytics.
// Ref: leduckhai/Sentiment-Reasoning

package dev.omni.sentiment

object OmniSentimentStream {
  sealed trait SentimentEvent
  case class Classified(label: String, confidence: Double) extends SentimentEvent
  case class StreamError(msg: String) extends SentimentEvent

  def processEvent(event: SentimentEvent): Either[String, Double] = event match {
    case Classified(_, conf) if conf >= 0.0 && conf <= 1.0 => Right(conf)
    case Classified(_, _) => Left("OMNI_ERR: Confidence out of [0,1]")
    case StreamError(msg) => Left(s"OMNI_ERR: $msg")
  }
}
