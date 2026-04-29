;; Omni Confucius Curriculum (Clojure)
;; Rules Layer: Functional curriculum sorting for tool learning.
;; Ref: mangopy/Confucius-tool-learning

(ns omni.confucius.curriculum)

(defn sort-by-difficulty [tools]
  (sort-by :difficulty tools))

(defn next-unmastered [tools mastered-set]
  (first (filter #(not (contains? mastered-set (:name %))) (sort-by-difficulty tools))))
