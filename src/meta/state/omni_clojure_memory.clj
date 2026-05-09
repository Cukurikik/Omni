(ns omni.core.memory
  (:require [clojure.core.async :as a]))

;; Omni Persistent Memory State (Clojure)
;; Developer Experience & Metaprogramming Layer
;; Manages the immutable state trees of the OMNI execution context.
;; Provides lock-free concurrency over model configurations.

(defonce system-state (atom {:active-models {}
                             :gpu-registry {}
                             :global-epoch 0}))

;; Pure function to compute the next state
(defn register-model [state model-id config]
  (assoc-in state [:active-models model-id] config))

(defn deregister-model [state model-id]
  (update state :active-models dissoc model-id))

(defn update-gpu-load [state gpu-id load-pct]
  (assoc-in state [:gpu-registry gpu-id :load] load-pct))

;; Transactional state mutations
(defn deploy-new-transformer! [model-id param-count architecture]
  (swap! system-state register-model model-id 
         {:params param-count 
          :arch architecture
          :status :loading
          :deployed-at (System/currentTimeMillis)}))

(defn purge-transformer! [model-id]
  (swap! system-state deregister-model model-id))

(defn log-current-state []
  (let [snapshot @system-state]
    (println "OMNI Mother Nexus State:")
    (println "Active Models: " (count (:active-models snapshot)))
    (println "Global Epoch: " (:global-epoch snapshot))))

;; Core Async channel for processing incoming state telemetry
(def telemetry-chan (a/chan 100))

(a/go-loop []
  (when-let [msg (a/<! telemetry-chan)]
    (let [{:keys [gpu-id load]} msg]
      (swap! system-state update-gpu-load gpu-id load))
    (recur)))
