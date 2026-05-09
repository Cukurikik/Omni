-- OMNI Framework Avionics Control Module
-- Written in Ada for Hard Real-Time safety constraints

package body Omni_Avionics_Control is

   procedure Adjust_Thrust (Current_Speed : in Float; Target_Speed : in Float; Thrust_Cmd : out Float) is
      Error : Float := Target_Speed - Current_Speed;
      Kp : constant Float := 0.5;
   begin
      if Error > 10.0 then
         Thrust_Cmd := 1.0; -- Max thrust
      elsif Error < -10.0 then
         Thrust_Cmd := 0.0; -- Idle
      else
         Thrust_Cmd := 0.5 + (Error * Kp);
      end if;
   end Adjust_Thrust;

end Omni_Avionics_Control;
