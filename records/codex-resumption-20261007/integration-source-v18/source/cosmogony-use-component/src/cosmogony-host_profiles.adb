package body Cosmogony.Host_Profiles with SPARK_Mode => On is

   function Admit
     (H : Cosmogony.Hierarchy.Hierarchy_State;
      S : Host_Observation;
      Request : Cosmogony.Hierarchy.Resources;
      Now_Tick : Interfaces.Unsigned_64) return Admission_Kind is
   begin
      if Can_Admit (H, S, Request, Now_Tick) then
         return Eligible_Reservation;
      else
         return Refused;
      end if;
   end Admit;

end Cosmogony.Host_Profiles;
