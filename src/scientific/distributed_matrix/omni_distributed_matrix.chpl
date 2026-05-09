// @omni-layer Scientific | @omni-lang Chapel | @omni-batch 17
// @omni-description Distributed matrix operations: Chapel parallel DGEMM
// with domain maps, locale-aware distribution, and reduction primitives.

module OmniDistributedMatrix {

  use LinearAlgebra;
  use BlockDist;

  config const n = 1024;         // Matrix dimension
  config const tileSize = 64;    // Tile size for blocked multiply
  config const numTrials = 3;    // Benchmark iterations

  // Distributed domain for matrix distribution across locales
  const Space = {1..n, 1..n};
  const BlockSpace = Space dmapped Block(Space);

  // Dense General Matrix Multiply: C = A * B
  proc omniDGEMM(ref A: [BlockSpace] real, ref B: [BlockSpace] real, ref C: [BlockSpace] real) {
    forall (i, j) in BlockSpace {
      var sum: real = 0.0;
      for k in 1..n {
        sum += A[i, k] * B[k, j];
      }
      C[i, j] = sum;
    }
  }

  // Tiled DGEMM for cache efficiency
  proc omniTiledDGEMM(ref A: [BlockSpace] real, ref B: [BlockSpace] real, ref C: [BlockSpace] real) {
    forall (ii, jj) in {1..n by tileSize, 1..n by tileSize} {
      for kk in 1..n by tileSize {
        for i in ii..min(ii + tileSize - 1, n) {
          for j in jj..min(jj + tileSize - 1, n) {
            var sum: real = C[i, j];
            for k in kk..min(kk + tileSize - 1, n) {
              sum += A[i, k] * B[k, j];
            }
            C[i, j] = sum;
          }
        }
      }
    }
  }

  // Frobenius norm (parallel reduction)
  proc omniFrobeniusNorm(ref A: [BlockSpace] real): real {
    var normSq: real = 0.0;
    forall (i, j) in BlockSpace with (+ reduce normSq) {
      normSq += A[i, j] * A[i, j];
    }
    return sqrt(normSq);
  }

  // Matrix trace
  proc omniTrace(ref A: [BlockSpace] real): real {
    var trace: real = 0.0;
    forall i in 1..n with (+ reduce trace) {
      trace += A[i, i];
    }
    return trace;
  }

  // Column-wise mean
  proc omniColumnMeans(ref A: [BlockSpace] real, ref means: [1..n] real) {
    forall j in 1..n {
      var sum: real = 0.0;
      for i in 1..n { sum += A[i, j]; }
      means[j] = sum / n: real;
    }
  }

  // Dot product of two vectors
  proc omniDotProduct(ref a: [1..n] real, ref b: [1..n] real): real {
    var dot: real = 0.0;
    forall i in 1..n with (+ reduce dot) {
      dot += a[i] * b[i];
    }
    return dot;
  }

  // L2 norm
  proc omniL2Norm(ref v: [1..n] real): real {
    return sqrt(omniDotProduct(v, v));
  }

  // Benchmark harness
  proc omniBenchmark() {
    var A: [BlockSpace] real;
    var B: [BlockSpace] real;
    var C: [BlockSpace] real;

    // Initialize with structured data
    forall (i, j) in BlockSpace {
      A[i, j] = sin(i: real * 0.01) * cos(j: real * 0.01);
      B[i, j] = cos(i: real * 0.01) * sin(j: real * 0.01);
      C[i, j] = 0.0;
    }

    writeln("[OmniHPC] Matrix size: ", n, "x", n);
    writeln("[OmniHPC] Locales: ", numLocales);
    writeln("[OmniHPC] Tile size: ", tileSize);

    for trial in 1..numTrials {
      omniTiledDGEMM(A, B, C);
      var norm = omniFrobeniusNorm(C);
      writeln("[OmniHPC] Trial ", trial, " Frobenius norm: ", norm);
    }
  }

  proc main() {
    omniBenchmark();
  }
}
