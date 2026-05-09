;; @omni-layer Metaprogramming | @omni-lang Clojure | @omni-batch 18 | @omni-semester 16
;; @omni-description Clojure transformer pipeline DSL with immutable data flow,
;; transducer composition, and model chain orchestration.

(ns omni.transformer.pipeline
  (:require [clojure.string :as str]))

(defprotocol IModelStep
  (execute [this input] "Execute a model step on input data")
  (step-name [this] "Return step identifier"))

(defrecord TokenizerStep [vocab-size]
  IModelStep
  (execute [_ input]
    (let [words (str/split (str input) #"\s+")
          token-ids (mapv (fn [w]
                           (mod (reduce + (map-indexed #(* (inc %1) (int %2)) w))
                                vocab-size))
                         words)]
      {:token-ids token-ids :original-text (str input) :n-tokens (count token-ids)}))
  (step-name [_] "tokenizer"))

(defrecord EmbeddingStep [dim]
  IModelStep
  (execute [_ input]
    (let [tids (:token-ids input)
          embeddings (mapv (fn [tid]
                            (mapv (fn [d]
                                    (* 0.01 (Math/sin (* (inc tid) (inc d) 0.001))))
                                  (range dim)))
                          tids)]
      (assoc input :embeddings embeddings :dim dim)))
  (step-name [_] "embedding"))

(defrecord AttentionStep [n-heads]
  IModelStep
  (execute [_ input]
    (let [embs (:embeddings input)
          n (count embs)
          d (count (first embs))
          scale (/ 1.0 (Math/sqrt (double (/ d n-heads))))
          scores (mapv (fn [i]
                        (let [qi (nth embs i)
                              raw (mapv (fn [j]
                                         (* scale (reduce + (map * qi (nth embs j)))))
                                       (range n))
                              mx (apply max raw)
                              exps (mapv #(Math/exp (- % mx)) raw)
                              sm (reduce + exps)]
                          (mapv #(/ % (+ sm 1e-10)) exps)))
                      (range n))
          attended (mapv (fn [i]
                          (mapv (fn [d]
                                  (reduce + (map (fn [j] (* (nth (nth scores i) j)
                                                           (nth (nth embs j) d)))
                                                (range n))))
                                (range d)))
                        (range n))]
      (assoc input :attention-output attended :attention-scores scores)))
  (step-name [_] "attention"))

(defrecord ClassifierStep [n-classes]
  IModelStep
  (execute [_ input]
    (let [embs (:attention-output input)
          pooled (mapv (fn [d] (/ (reduce + (map #(nth % d) embs)) (count embs)))
                      (range (count (first embs))))
          logits (mapv (fn [c] (reduce + (map-indexed #(* %2 (Math/sin (* (inc c) (inc %1) 0.001)))
                                                      (take 32 pooled))))
                      (range n-classes))
          mx (apply max logits)
          exps (mapv #(Math/exp (- % mx)) logits)
          sm (reduce + exps)
          probs (mapv #(/ % (+ sm 1e-10)) exps)
          best-idx (.indexOf probs (apply max probs))]
      (assoc input :logits logits :probabilities probs :predicted-class best-idx)))
  (step-name [_] "classifier"))

(defn build-pipeline
  "Build a transformer pipeline from step specs."
  [& steps]
  (fn [input]
    (reduce (fn [data step]
              (let [result (execute step data)]
                (assoc result :pipeline-trace
                       (conj (or (:pipeline-trace data) []) (step-name step)))))
            {:raw-input input}
            steps)))

(defn create-text-classifier [& {:keys [vocab-size dim n-heads n-classes]
                                  :or {vocab-size 32000 dim 256 n-heads 4 n-classes 10}}]
  (build-pipeline
    (->TokenizerStep vocab-size)
    (->EmbeddingStep dim)
    (->AttentionStep n-heads)
    (->ClassifierStep n-classes)))
