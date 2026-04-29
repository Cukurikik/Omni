;; Omni Efficient-AIGC Pruning Analyzer (Clojure)
;; Ref: Efficient-ML/Awesome-Efficient-AIGC
(ns omni.efficient-aigc)

(defn compute-sparsity [weights]
  (let [total (count weights)
        zeros (count (filter #(< (Math/abs %) 1e-8) weights))]
    (if (pos? total) (/ (double zeros) total) 0.0)))

(defn magnitude-prune [weights ratio]
  (let [sorted (sort-by #(Math/abs %) weights)
        cutoff (int (* (count weights) ratio))
        threshold (if (pos? cutoff) (Math/abs (nth sorted (dec cutoff))) 0.0)]
    (mapv #(if (< (Math/abs %) threshold) 0.0 %) weights)))

(defn quantize-to-bits [values bits]
  (let [max-val (apply max (map #(Math/abs %) values))
        levels (dec (int (Math/pow 2 bits)))
        scale (if (pos? max-val) (/ max-val levels) 1.0)]
    {:quantized (mapv #(Math/round (/ % scale)) values) :scale scale}))
