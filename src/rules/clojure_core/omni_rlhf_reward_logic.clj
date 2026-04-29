;; Omni RLHF Reward Logic (Clojure)
;; Rules Layer: Functional reward model scoring for RLHF.
;; Ref: yihedeng9/rlhf-summary-notes
(ns omni.rlhf.reward)
(defn compute-reward [chosen-score rejected-score margin]
  (let [diff (- chosen-score rejected-score)]
    (if (> diff margin) {:status :accepted :margin diff} {:status :rejected :margin diff})))
(defn bradley-terry-loss [chosen rejected]
  (- (Math/log (/ 1.0 (+ 1.0 (Math/exp (- rejected chosen)))))))
