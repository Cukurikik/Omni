# @omni-layer System | @omni-lang Nim | @omni-batch 18 | @omni-semester 16
# @omni-description Nim transformer inference runtime: compile-time generic
# tensor ops, attention kernels, and model serving with zero-overhead abstractions.

import math, strformat, tables, times, hashes

type
  Tensor[T] = object
    data: seq[T]
    shape: seq[int]

  AttentionConfig = object
    dModel: int
    nHeads: int
    headDim: int
    scale: float

  InferenceStats = object
    requests: int
    totalLatencyMs: float
    avgLatencyMs: float

proc newTensor[T](rows, cols: int): Tensor[T] =
  result.data = newSeq[T](rows * cols)
  result.shape = @[rows, cols]

proc `[]`[T](t: Tensor[T], i, j: int): T =
  t.data[i * t.shape[1] + j]

proc `[]=`[T](t: var Tensor[T], i, j: int, val: T) =
  t.data[i * t.shape[1] + j] = val

proc softmax(data: var seq[float]) =
  var maxVal = data[0]
  for v in data[1..^1]:
    if v > maxVal: maxVal = v
  var sum = 0.0
  for i in 0..<data.len:
    data[i] = exp(data[i] - maxVal)
    sum += data[i]
  let inv = 1.0 / (sum + 1e-10)
  for i in 0..<data.len:
    data[i] *= inv

proc layerNorm(data: var seq[float], eps: float = 1e-5) =
  let n = data.len.float
  var mean = 0.0
  for v in data: mean += v
  mean /= n
  var variance = 0.0
  for v in data:
    let d = v - mean
    variance += d * d
  variance /= n
  let invStd = 1.0 / sqrt(variance + eps)
  for i in 0..<data.len:
    data[i] = (data[i] - mean) * invStd

proc matmul(a, b: Tensor[float]): Tensor[float] =
  assert a.shape[1] == b.shape[0]
  result = newTensor[float](a.shape[0], b.shape[1])
  for i in 0..<a.shape[0]:
    for j in 0..<b.shape[1]:
      var sum = 0.0
      for k in 0..<a.shape[1]:
        sum += a[i, k] * b[k, j]
      result[i, j] = sum

proc scaledDotProductAttention(q, k, v: Tensor[float], headDim: int): Tensor[float] =
  let n = q.shape[0]
  let scale = 1.0 / sqrt(headDim.float)
  var scores = newTensor[float](n, n)
  for i in 0..<n:
    for j in 0..<n:
      var dot = 0.0
      for d in 0..<min(headDim, q.shape[1]):
        dot += q[i, d] * k[j, d]
      scores[i, j] = dot * scale
  for i in 0..<n:
    var row = scores.data[i * n ..< (i + 1) * n]
    softmax(row)
    for j in 0..<n:
      scores[i, j] = row[j]
  result = newTensor[float](n, v.shape[1])
  for i in 0..<n:
    for d in 0..<v.shape[1]:
      var sum = 0.0
      for j in 0..<n:
        sum += scores[i, j] * v[j, d]
      result[i, d] = sum

proc newAttentionConfig(dModel, nHeads: int): AttentionConfig =
  let headDim = dModel div nHeads
  AttentionConfig(
    dModel: dModel,
    nHeads: nHeads,
    headDim: headDim,
    scale: 1.0 / sqrt(headDim.float)
  )

proc embed(tokenIds: seq[int], dim: int): Tensor[float] =
  let n = tokenIds.len
  result = newTensor[float](n, dim)
  for i in 0..<n:
    for d in 0..<dim:
      result[i, d] = sin(float(tokenIds[i] + 1) * float(d + 1) * 0.001) * 0.1 +
                      cos(float(i) * 0.01 + float(d) * 0.001) * 0.05
