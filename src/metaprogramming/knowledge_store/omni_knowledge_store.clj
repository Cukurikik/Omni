;; @omni-layer Metaprogramming | @omni-lang Clojure | @omni-batch 17
;; @omni-description Transactional knowledge store: Clojure STM-based
;; immutable knowledge base with transactional updates and query DSL.

(ns omni.knowledge-store
  (:require [clojure.set :as set]
            [clojure.string :as str]))

;; === Core Data Structures (Immutable) ===
(def knowledge-db (ref {:concepts {}
                         :relations []
                         :taxonomy {}
                         :version 0
                         :stats {:inserts 0 :queries 0}}))

;; === OmniResult Monad ===
(defn ok [data] {:status :ok :data data :error nil})
(defn err [msg] {:status :error :data nil :error msg})
(defn ok? [result] (= :ok (:status result)))

;; === Concept Management (STM Transactions) ===
(defn add-concept!
  "Add a concept to the knowledge base transactionally."
  [name type confidence & {:keys [source embedding]}]
  (if (or (str/blank? name) (not (#{:entity :process :attribute :relation :event} type)))
    (err "Invalid concept")
    (dosync
      (alter knowledge-db
             (fn [db]
               (-> db
                   (assoc-in [:concepts name]
                             {:name name
                              :type type
                              :confidence confidence
                              :source (or source "manual")
                              :embedding embedding
                              :created-at (System/currentTimeMillis)})
                   (update-in [:version] inc)
                   (update-in [:stats :inserts] inc))))
      (ok {:added name :type type}))))

;; === Relation Management ===
(defn add-relation!
  "Add a semantic relation between two concepts."
  [subject predicate object & {:keys [confidence] :or {confidence 0.8}}]
  (dosync
    (alter knowledge-db
           (fn [db]
             (let [rel {:subject subject
                        :predicate predicate
                        :object object
                        :confidence confidence
                        :timestamp (System/currentTimeMillis)}]
               (-> db
                   (update :relations conj rel)
                   (cond->
                     (= predicate :is-a) (assoc-in [:taxonomy subject] object))
                   (update-in [:version] inc)
                   (update-in [:stats :inserts] inc)))))
    (ok {:relation [subject predicate object]})))

;; === Query DSL ===
(defn query-concepts
  "Query concepts by type and minimum confidence."
  [& {:keys [type min-confidence] :or {min-confidence 0.0}}]
  (dosync
    (alter knowledge-db update-in [:stats :queries] inc)
    (let [concepts (vals (:concepts @knowledge-db))
          filtered (cond->> concepts
                     type (filter #(= type (:type %)))
                     true (filter #(>= (:confidence %) min-confidence)))]
      (ok {:results (vec filtered) :count (count filtered)}))))

(defn query-relations
  "Query relations by predicate or subject."
  [& {:keys [subject predicate]}]
  (dosync
    (alter knowledge-db update-in [:stats :queries] inc)
    (let [rels (:relations @knowledge-db)
          filtered (cond->> rels
                     subject (filter #(= subject (:subject %)))
                     predicate (filter #(= predicate (:predicate %))))]
      (ok {:results (vec filtered) :count (count filtered)}))))

;; === Taxonomy Traversal ===
(defn ancestors
  "Get all ancestors via IS-A taxonomy."
  [concept]
  (let [taxonomy (:taxonomy @knowledge-db)]
    (loop [current concept acc []]
      (if-let [parent (get taxonomy current)]
        (recur parent (conj acc parent))
        (ok {:concept concept :ancestors acc :depth (count acc)})))))

(defn common-ancestor
  "Find lowest common ancestor of two concepts."
  [a b]
  (let [ancestors-a (set (:ancestors (:data (ancestors a))))
        ancestors-b (set (:ancestors (:data (ancestors b))))
        common (set/intersection ancestors-a ancestors-b)]
    (ok {:concept-a a :concept-b b :common-ancestors (vec common)})))

;; === Embedding Similarity ===
(defn cosine-similarity [a b]
  (when (and a b (= (count a) (count b)))
    (let [dot (reduce + (map * a b))
          na (Math/sqrt (reduce + (map #(* % %) a)))
          nb (Math/sqrt (reduce + (map #(* % %) b)))]
      (if (> (* na nb) 1e-8)
        (/ dot (* na nb))
        0.0))))

(defn find-similar
  "Find concepts most similar to a query embedding."
  [query-embedding top-k]
  (let [concepts (vals (:concepts @knowledge-db))
        scored (->> concepts
                    (filter :embedding)
                    (map (fn [c] (assoc c :similarity (cosine-similarity query-embedding (:embedding c)))))
                    (sort-by :similarity >)
                    (take top-k))]
    (ok {:results (vec scored) :count (count scored)})))

;; === Statistics ===
(defn stats []
  (let [db @knowledge-db]
    (ok {:concepts (count (:concepts db))
         :relations (count (:relations db))
         :taxonomy-depth (count (:taxonomy db))
         :version (:version db)
         :operations (:stats db)})))
