// Omni KnowPAT Stream (Scala)
// Event Layer: Fast data stream processing for Preference Alignment updates.

package dev.omni.knowpat

object OmniKnowPatStream {

  sealed trait AlignmentEvent
  case class PreferenceUpdate(entityA: String, entityB: String, confidence: Double) extends AlignmentEvent
  case class GraphError(msg: String) extends AlignmentEvent

  def processEvent(event: AlignmentEvent): Either[String, Double] = {
    event match {
      case PreferenceUpdate(_, _, conf) if conf >= 0.0 && conf <= 1.0 =>
        Right(conf * 0.1) // Delta update step
      case PreferenceUpdate(_, _, _) =>
        Left("OMNI_ERR: Confidence out of bounds [0, 1]")
      case GraphError(msg) =>
        Left(s"OMNI_ERR: Upstream error - $msg")
    }
  }
}
