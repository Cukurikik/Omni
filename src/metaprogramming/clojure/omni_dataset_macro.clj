;; OMNI Framework - Dataset Metaprogramming (Clojure)
;; Defines macros to generate data transformation boilerplate automatically.

(ns omni.dataset.macro)

(defmacro def-smashed-transform
  "Generates a standard text transformation function for the SMASHED pipeline"
  [transform-name field operation]
  `(defn ~transform-name [record#]
     (let [val# (~field record#)
           new-val# (~operation val#)]
       (assoc record# ~field new-val#))))

;; Usage example inside the macro context:
;; (def-smashed-transform uppercase-text :text clojure.string/upper-case)
;; This expands to:
;; (defn uppercase-text [record] (assoc record :text (clojure.string/upper-case (:text record))))

(defn apply-pipeline [records pipeline-fns]
  (map (fn [record]
         (reduce (fn [acc-record f] (f acc-record))
                 record
                 pipeline-fns))
       records))
