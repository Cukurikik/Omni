;; Omni BertNet KG Merge (Clojure)
;; Ref: tanyuqian/knowledge-harvest-from-lms
(ns omni.bertnet-kg)
(defn merge-triples [& graphs]
  (->> (apply concat graphs)
       (group-by (juxt :head :relation :tail))
       (map (fn [[k v]] (assoc (first v) :confidence
                               (apply max (map :confidence v)))))
       (sort-by :confidence >)))
(defn filter-by-confidence [triples threshold]
  (filter #(>= (:confidence %) threshold) triples))
