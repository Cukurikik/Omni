;; OMNI Metaprogramming — Clojure Macro DSL
;; Generates complex Kubernetes/Helm configuration structures programmatically

(ns omni.config.dsl)

(defmacro defdeployment [name replicas image]
  `(def ~name
     {:apiVersion "apps/v1"
      :kind "Deployment"
      :metadata {:name ~(str name)}
      :spec {:replicas ~replicas
             :selector {:matchLabels {:app ~(str name)}}
             :template {:metadata {:labels {:app ~(str name)}}
                        :spec {:containers [{:name ~(str name)
                                             :image ~image}]}}}}))

;; Usage of the macro
(defdeployment omni-inference-node 5 "omni/inference:v3.0.0")
(defdeployment omni-api-gateway 2 "omni/gateway:v1.2.0")

(defn generate-yaml [deployment]
  (println "Generating YAML for:" (:metadata deployment))
  ;; Simulated YAML generation
  )
