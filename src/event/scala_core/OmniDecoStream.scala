// Omni DeCo Correction Stream (Scala)
// Event Layer: Streaming correction event processing.
// Ref: zjunlp/Deco — ICLR 2025
package dev.omni.deco
object OmniDecoStream {
  sealed trait CorrectionEvent
  case class TokenCorrected(tokenIdx: Int, penalty: Double) extends CorrectionEvent
  case class OutputFinalized(totalCorrections: Int, confidence: Double) extends CorrectionEvent
  def processEvent(event: CorrectionEvent): Either[String, Double] = event match {
    case TokenCorrected(_, p) if p > 5.0 => Left(s"OMNI_ERR: Excessive penalty $p")
    case TokenCorrected(_, p) => Right(p)
    case OutputFinalized(_, c) => Right(c)
  }
}
