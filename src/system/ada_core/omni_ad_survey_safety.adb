-- Omni AD Survey Safety (Ada)
-- System Layer: Hard real-time safety critical bounds for Autonomous Driving scenarios.

package Omni_AD_Survey_Safety is
   type Speed_Mps is new Float range 0.0 .. 100.0;
   type Distance_Meters is new Float range 0.0 .. 1000.0;
   
   type Safety_Status is (SAFE, WARNING, CRITICAL_BRAKE);
   
   function Evaluate_Time_To_Collision (V : Speed_Mps; D : Distance_Meters) return Safety_Status;
end Omni_AD_Survey_Safety;

package body Omni_AD_Survey_Safety is
   function Evaluate_Time_To_Collision (V : Speed_Mps; D : Distance_Meters) return Safety_Status is
      TTC : Float;
   begin
      if V = 0.0 then
         return SAFE;
      end if;
      
      TTC := Float(D) / Float(V);
      
      if TTC < 2.0 then
         return CRITICAL_BRAKE;
      elsif TTC < 5.0 then
         return WARNING;
      else
         return SAFE;
      end if;
   end Evaluate_Time_To_Collision;
end Omni_AD_Survey_Safety;
