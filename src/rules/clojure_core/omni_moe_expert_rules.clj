;; Omni MoE Expert Selection Logic (Clojure)
;; Rules Layer: Functional expert gating rules.
;; Ref: arpita8/Awesome-Mixture-of-Experts-Papers
(ns omni.moe.rules)
(defn select-experts [logits k]
  (let [indexed (map-indexed vector logits)
        sorted (sort-by second > indexed)]
    (take k sorted)))
(defn balance-penalty [counts n-experts]
  (let [total (reduce + counts)
        uniform (/ 1.0 n-experts)]
    (reduce + (map #(Math/pow (- (/ % total) uniform) 2) counts))))
