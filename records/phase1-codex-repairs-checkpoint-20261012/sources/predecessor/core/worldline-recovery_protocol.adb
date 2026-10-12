package body Worldline.Recovery_Protocol with SPARK_Mode is
   function Advance (Before : State; Cause : Event) return State is
   begin
      if Cause = Unknown_Observation then
         return Quarantined;
      end if;
      case Before is
         when Issued =>
            if Cause = Fresh_Claim then
               return Effect_Intent;
            elsif Cause = No_Effect_Released then
               return Aborted;
            end if;
         when Effect_Intent =>
            if Cause = Historical_Effect then
               return Effect_Observed;
            elsif Cause = No_Effect_Released then
               return Aborted;
            end if;
         when Effect_Observed =>
            if Cause = Settlement_Complete then
               return Settled;
            end if;
         when Quarantined =>
            if Cause = Owner_Effect_Resolution then
               return Effect_Observed;
            elsif Cause = Owner_No_Effect_Resolution then
               return Aborted;
            end if;
         when Settled | Aborted => null;
      end case;
      return Before;
   end Advance;
end Worldline.Recovery_Protocol;
