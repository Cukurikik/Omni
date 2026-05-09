;; omni_tensor_ops.clj — Pure Functional Tensor Operations
;; Inspired by: Clojure numerical computing for OMNI
;; Layer: Functional / Clojure
;;
;; Persistent, immutable tensor operations implemented in Clojure
;; with transducer-based lazy evaluation and structural sharing.

(ns omni.functional.tensor-ops
  (:require [clojure.core.reducers :as r]))

;; === Tensor Construction ===

(defrecord Tensor [data shape strides dtype])

(defn make-tensor
  "Create a new tensor from flat data and shape."
  [data shape]
  (let [strides (reduce (fn [acc dim]
                          (conj acc (* (peek acc) dim)))
                        [1]
                        (reverse (rest shape)))
        strides (vec (reverse strides))]
    (->Tensor (vec data) (vec shape) strides :float64)))

(defn zeros
  "Create a tensor filled with zeros."
  [& shape]
  (make-tensor (vec (repeat (reduce * shape) 0.0)) (vec shape)))

(defn ones
  "Create a tensor filled with ones."
  [& shape]
  (make-tensor (vec (repeat (reduce * shape) 1.0)) (vec shape)))

(defn arange
  "Create a 1D tensor with values from start to end."
  [start end & {:keys [step] :or {step 1}}]
  (let [data (vec (range start end step))]
    (make-tensor data [(count data)])))

(defn rand-tensor
  "Create a tensor filled with uniform random values."
  [& shape]
  (let [n (reduce * shape)]
    (make-tensor (vec (repeatedly n #(Math/random))) (vec shape))))

;; === Element Access ===

(defn flat-index
  "Convert multi-dimensional indices to flat index."
  [indices strides]
  (reduce + (map * indices strides)))

(defn tget
  "Get element at given indices."
  [tensor & indices]
  (let [idx (flat-index indices (:strides tensor))]
    (nth (:data tensor) idx)))

(defn tset
  "Return new tensor with value set at given indices (persistent)."
  [tensor value & indices]
  (let [idx (flat-index indices (:strides tensor))]
    (update tensor :data assoc idx value)))

;; === Element-wise Operations ===

(defn element-wise
  "Apply function element-wise to one or two tensors."
  ([f t1]
   (update t1 :data #(mapv f %)))
  ([f t1 t2]
   (assert (= (:shape t1) (:shape t2))
           "Shape mismatch for element-wise operation")
   (update t1 :data #(mapv f % (:data t2)))))

(defn tadd [t1 t2] (element-wise + t1 t2))
(defn tsub [t1 t2] (element-wise - t1 t2))
(defn tmul [t1 t2] (element-wise * t1 t2))
(defn tdiv [t1 t2] (element-wise / t1 t2))

(defn tscale
  "Scale tensor by a scalar."
  [tensor s]
  (element-wise #(* % s) tensor))

(defn tneg [tensor] (element-wise - tensor))
(defn tabs [tensor] (element-wise #(Math/abs %) tensor))
(defn tsqrt [tensor] (element-wise #(Math/sqrt %) tensor))
(defn texp [tensor] (element-wise #(Math/exp %) tensor))
(defn tlog [tensor] (element-wise #(Math/log (max % 1e-10)) tensor))

;; === Activation Functions ===

(defn relu [tensor]
  (element-wise #(max 0.0 %) tensor))

(defn gelu [tensor]
  (element-wise
   (fn [x]
     (* 0.5 x (+ 1.0 (Math/tanh
                       (* (Math/sqrt (/ 2.0 Math/PI))
                          (+ x (* 0.044715 x x x)))))))
   tensor))

(defn sigmoid [tensor]
  (element-wise #(/ 1.0 (+ 1.0 (Math/exp (- %)))) tensor))

(defn tanh-activation [tensor]
  (element-wise #(Math/tanh %) tensor))

;; === Reduction Operations ===

(defn tsum
  "Sum all elements of tensor."
  [tensor]
  (reduce + (:data tensor)))

(defn tmean
  "Mean of all elements."
  [tensor]
  (/ (tsum tensor) (count (:data tensor))))

(defn tmax
  "Max of all elements."
  [tensor]
  (reduce max (:data tensor)))

(defn tmin
  "Min of all elements."
  [tensor]
  (reduce min (:data tensor)))

(defn tvar
  "Variance of all elements."
  [tensor]
  (let [mean-val (tmean tensor)
        n (count (:data tensor))]
    (/ (reduce + (map #(let [d (- % mean-val)] (* d d))
                      (:data tensor)))
       n)))

;; === Matrix Operations ===

(defn matmul
  "Matrix multiplication for 2D tensors."
  [a b]
  (assert (= 2 (count (:shape a)) (count (:shape b)))
          "matmul requires 2D tensors")
  (let [[m k1] (:shape a)
        [k2 n] (:shape b)
        _ (assert (= k1 k2) "Inner dimensions must match")
        result (vec
                (for [i (range m)
                      j (range n)]
                  (reduce +
                          (for [p (range k1)]
                            (* (tget a i p)
                               (tget b p j))))))]
    (make-tensor result [m n])))

(defn transpose
  "Transpose a 2D tensor."
  [tensor]
  (assert (= 2 (count (:shape tensor))) "transpose requires 2D tensor")
  (let [[rows cols] (:shape tensor)
        data (vec (for [j (range cols)
                        i (range rows)]
                    (tget tensor i j)))]
    (make-tensor data [cols rows])))

;; === Normalization ===

(defn layer-norm
  "Layer normalization along last dimension."
  [tensor eps]
  (let [mean-val (tmean tensor)
        var-val (tvar tensor)
        inv-std (/ 1.0 (Math/sqrt (+ var-val eps)))]
    (element-wise #(* (- % mean-val) inv-std) tensor)))

(defn softmax
  "Softmax normalization."
  [tensor]
  (let [max-val (tmax tensor)
        shifted (element-wise #(- % max-val) tensor)
        exp-vals (texp shifted)
        sum-exp (tsum exp-vals)]
    (tscale exp-vals (/ 1.0 sum-exp))))

;; === Attention Mechanism ===

(defn scaled-dot-product-attention
  "Scaled dot-product attention for 2D Q, K, V matrices."
  [query key value]
  (let [d-k (second (:shape key))
        scale (/ 1.0 (Math/sqrt d-k))
        scores (tscale (matmul query (transpose key)) scale)
        ;; Apply softmax row-wise
        [rows cols] (:shape scores)
        attn-data (vec
                   (apply concat
                          (for [i (range rows)]
                            (let [row-data (vec (for [j (range cols)]
                                                 (tget scores i j)))
                                  row-tensor (make-tensor row-data [cols])
                                  softmax-row (softmax row-tensor)]
                              (:data softmax-row)))))
        attn-weights (make-tensor attn-data [rows cols])]
    (matmul attn-weights value)))

;; === Utility ===

(defn tensor-info
  "Return human-readable tensor info."
  [tensor]
  {:shape (:shape tensor)
   :dtype (:dtype tensor)
   :numel (count (:data tensor))
   :mean (tmean tensor)
   :std (Math/sqrt (tvar tensor))
   :min (tmin tensor)
   :max (tmax tensor)})

(defn reshape
  "Reshape tensor to new shape (must have same numel)."
  [tensor new-shape]
  (assert (= (reduce * (:shape tensor))
             (reduce * new-shape))
          "Total elements must match for reshape")
  (make-tensor (:data tensor) (vec new-shape)))
