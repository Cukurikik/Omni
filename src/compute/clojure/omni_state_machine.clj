(ns omni-framework.compute.state-machine
  (:require [clojure.core.async :as async :refer [go <! >! chan]]))

(defrecord OmniState [status memory])

(defn transition [state event]
  (case (:status state)
    :init (if (= event :start) (assoc state :status :running) state)
    :running (if (= event :stop) (assoc state :status :stopped) state)
    :stopped state
    state))

(defn run-machine []
  (let [event-channel (chan 10)
        state-atom (atom (->OmniState :init 0))]
    
    (go
      (loop []
        (let [event (<! event-channel)]
          (when event
            (swap! state-atom transition event)
            (println "OMNI State transitioned to:" (:status @state-atom))
            (recur)))))
    
    event-channel))
