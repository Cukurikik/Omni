;; OMNI Framework - Clojure Metaprogramming for Grokking Datasets
(ns omni.grokking.macros)

(defmacro def-modulo-operation
  "Defines a fast modulo arithmetic function for Grokking dataset generation."
  [op-name op modulo-val]
  `(defn ~op-name [a# b#]
     (mod (~op a# b#) ~modulo-val)))

;; Example usage expanded by the macro
;; (def-modulo-operation mod-add + 97)
;; (def-modulo-operation mod-sub - 97)

(defn generate-dataset
  "Generates a dataset of size N using the provided modulo operation function."
  [n op-fn mod-val]
  (repeatedly n (fn [] 
                  (let [a (rand-int mod-val)
                        b (rand-int mod-val)]
                    {:a a :b b :result (op-fn a b)}))))
