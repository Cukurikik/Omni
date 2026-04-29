;; Omni K2 Geoscience DSL (Clojure)
;; Metaprogramming Layer: Domain Specific Language for Geospatial queries.

(ns omni.k2.geoscience)

;; Pure functional monadic evaluation
(defn evaluate-geo-bounds [lat lon]
  (if (or (< lat -90) (> lat 90) (< lon -180) (> lon 180))
    {:ok false :error "Coordinate bounds violation"}
    {:ok true  :data {:lat lat :lon lon :sector (str "SEC-" (Math/abs (int lat)))}}))

(defmacro def-geo-region [region-name lat lon]
  `(def ~region-name
     (let [res# (evaluate-geo-bounds ~lat ~lon)]
       (if (:ok res#)
         (:data res#)
         (throw (Exception. (:error res#)))))))
