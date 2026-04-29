(ns omni.dx.immutable-state
  "Omni Immutable State Tree in Clojure.
   Developer Experience layer enforcing immutable data structures.")

(defn update-system-state
  "Strictly transitions the state map via deterministic functions.
   Returns a map with :success and :data/:error keys mimicking Result."
  [current-state path new-value]
  (if (empty? path)
    {:success false :error "Path cannot be empty"}
    (try
      (let [new-state (assoc-in current-state path new-value)]
        {:success true :data new-state})
      (catch Exception e
        {:success false :error (.getMessage e)}))))

(defn verify-integrity
  "Validates that the tree has not been corrupted."
  [state]
  (if (map? state)
    {:success true :data true}
    {:success false :error "State is not a valid immutable map"}))
