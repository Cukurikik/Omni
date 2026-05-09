// OmniTransformer.scala — Scala Transformer Implementation
// Inspired by: Memformer + RQ-Transformer architecture
// Layer: Compute / Scala
//
// Type-safe transformer with pattern matching, immutable state,
// and monadic error handling in Scala's type system.

package omni.compute.transformer

import scala.math.{sqrt, exp, log, tanh, Pi}
import scala.collection.immutable.Vector

sealed trait TransformerError
case class DimensionMismatch(expected: Int, got: Int) extends TransformerError
case class InvalidConfig(message: String) extends TransformerError
case class NumericalInstability(location: String) extends TransformerError

case class TransformerConfig(
  dim: Int = 512,
  heads: Int = 8,
  ffMult: Int = 4,
  depth: Int = 6,
  dropout: Double = 0.1,
  maxSeqLen: Int = 2048,
  vocabSize: Int = 32000
) {
  require(dim % heads == 0, s"dim ($dim) must be divisible by heads ($heads)")
  val headDim: Int = dim / heads
  val ffDim: Int = dim * ffMult
}

case class Tensor(data: Vector[Vector[Double]], rows: Int, cols: Int) {
  require(data.length == rows, s"Expected $rows rows, got ${data.length}")

  def apply(row: Int, col: Int): Double = data(row)(col)

  def +(other: Tensor): Either[TransformerError, Tensor] = {
    if (rows != other.rows || cols != other.cols)
      Left(DimensionMismatch(rows * cols, other.rows * other.cols))
    else {
      val result = data.zip(other.data).map { case (a, b) =>
        a.zip(b).map { case (x, y) => x + y }
      }
      Right(Tensor(result, rows, cols))
    }
  }

  def matMul(other: Tensor): Either[TransformerError, Tensor] = {
    if (cols != other.rows)
      Left(DimensionMismatch(cols, other.rows))
    else {
      val otherT = other.transpose
      val result = data.map { row =>
        otherT.data.map { col =>
          row.zip(col).map { case (a, b) => a * b }.sum
        }
      }
      Right(Tensor(result, rows, other.cols))
    }
  }

  def transpose: Tensor = {
    val transposed = (0 until cols).map { j =>
      (0 until rows).map { i => data(i)(j) }.toVector
    }.toVector
    Tensor(transposed, cols, rows)
  }

  def scale(factor: Double): Tensor = {
    Tensor(data.map(_.map(_ * factor)), rows, cols)
  }
}

object Tensor {
  def zeros(rows: Int, cols: Int): Tensor =
    Tensor(Vector.fill(rows)(Vector.fill(cols)(0.0)), rows, cols)

  def ones(rows: Int, cols: Int): Tensor =
    Tensor(Vector.fill(rows)(Vector.fill(cols)(1.0)), rows, cols)
}

object Activations {
  def gelu(x: Double): Double =
    0.5 * x * (1.0 + tanh(sqrt(2.0 / Pi) * (x + 0.044715 * x * x * x)))

  def softmax(xs: Vector[Double]): Vector[Double] = {
    val maxVal = xs.max
    val exps = xs.map(x => exp(x - maxVal))
    val sumExps = exps.sum
    exps.map(_ / sumExps)
  }
}

object LayerNorm {
  def apply(xs: Vector[Double], eps: Double = 1e-6): Vector[Double] = {
    val n = xs.length.toDouble
    val mean = xs.sum / n
    val variance = xs.map(x => (x - mean) * (x - mean)).sum / n
    val std = sqrt(variance + eps)
    xs.map(x => (x - mean) / std)
  }

  def applySeq(tensor: Tensor): Tensor = {
    val normed = tensor.data.map(LayerNorm.apply(_))
    Tensor(normed, tensor.rows, tensor.cols)
  }
}

object Attention {
  def scaledDotProduct(
    queries: Tensor, keys: Tensor, values: Tensor
  ): Either[TransformerError, (Tensor, Tensor)] = {
    val scale = 1.0 / sqrt(queries.cols.toDouble)
    val scaledQ = queries.scale(scale)

    for {
      scores <- scaledQ.matMul(keys.transpose)
      weights = Tensor(
        scores.data.map(row => Activations.softmax(row)),
        scores.rows, scores.cols
      )
      attended <- weights.matMul(values)
    } yield (attended, weights)
  }

  def multiHead(
    config: TransformerConfig, query: Tensor, key: Tensor, value: Tensor
  ): Either[TransformerError, Tensor] = {
    val headDim = config.headDim
    val numHeads = config.heads

    val headResults = (0 until numHeads).map { h =>
      val qHead = Tensor(
        query.data.map(row => row.slice(h * headDim, (h + 1) * headDim)),
        query.rows, headDim
      )
      val kHead = Tensor(
        key.data.map(row => row.slice(h * headDim, (h + 1) * headDim)),
        key.rows, headDim
      )
      val vHead = Tensor(
        value.data.map(row => row.slice(h * headDim, (h + 1) * headDim)),
        value.rows, headDim
      )
      scaledDotProduct(qHead, kHead, vHead).map(_._1)
    }

    val collected = headResults.foldLeft(Right(Vector.empty[Tensor]): Either[TransformerError, Vector[Tensor]]) {
      case (Right(acc), Right(t)) => Right(acc :+ t)
      case (Left(e), _) => Left(e)
      case (_, Left(e)) => Left(e)
    }

    collected.map { heads =>
      val concatenated = (0 until query.rows).map { i =>
        heads.flatMap(_.data(i)).toVector
      }.toVector
      Tensor(concatenated, query.rows, config.dim)
    }
  }
}

object FeedForward {
  def apply(dim: Int, ffDim: Int, input: Tensor): Tensor = {
    val activated = input.data.map { row =>
      val projected = row.flatMap(v => Vector.fill(ffDim / dim)(v)).take(ffDim)
      val geluApplied = projected.map(Activations.gelu)
      geluApplied.grouped(ffDim / dim).map(_.head).toVector.take(dim)
    }
    Tensor(activated, input.rows, dim)
  }
}

case class TransformerLayer(config: TransformerConfig) {
  def forward(input: Tensor): Either[TransformerError, Tensor] = {
    val normed1 = LayerNorm.applySeq(input)

    for {
      attnOut <- Attention.multiHead(config, normed1, normed1, normed1)
      residual1 <- input + attnOut
      normed2 = LayerNorm.applySeq(residual1)
      ffOut = FeedForward(config.dim, config.ffDim, normed2)
      residual2 <- residual1 + ffOut
    } yield residual2
  }
}

case class OmniTransformerEncoder(config: TransformerConfig) {
  private val layers = (0 until config.depth).map(_ => TransformerLayer(config))

  def forward(input: Tensor): Either[TransformerError, Tensor] = {
    layers.foldLeft(Right(input): Either[TransformerError, Tensor]) {
      case (Right(current), layer) => layer.forward(current)
      case (left @ Left(_), _) => left
    }.map(LayerNorm.applySeq)
  }
}
