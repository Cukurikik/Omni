-- Omni Me-LLaMA Safety (Ada)
-- System Layer: Hard real-time safety bounds for medical inference.
-- Ref: BIDS-Xu-Lab/Me-LLaMA

package Omni_Medical_Safety is
   type Confidence is new Float range 0.0 .. 1.0;
   type Safety_Level is (SAFE, REVIEW_REQUIRED, UNSAFE);

   function Evaluate_Confidence (C : Confidence) return Safety_Level;
end Omni_Medical_Safety;

package body Omni_Medical_Safety is
   function Evaluate_Confidence (C : Confidence) return Safety_Level is
   begin
      if C >= 0.9 then return SAFE;
      elsif C >= 0.5 then return REVIEW_REQUIRED;
      else return UNSAFE;
      end if;
   end Evaluate_Confidence;
end Omni_Medical_Safety;
