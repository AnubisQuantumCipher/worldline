package Worldline.Recovery_Protocol with SPARK_Mode is
   --  Protocol ordering only. Events are emitted by the protected principal
   --  after authentic capture/native redecision and acknowledged durability.
   --  No event is itself evidence, a capability, or permission to exchange.
   type State is
     (Issued, Effect_Intent, Effect_Observed, Settled, Aborted, Quarantined);
   type Event is
     (Fresh_Claim, Historical_Effect, Settlement_Complete,
      No_Effect_Released, Unknown_Observation, Owner_Effect_Resolution,
      Owner_No_Effect_Resolution, Replay);
   function Reference (Before : State; Cause : Event) return State is
     (if Cause = Unknown_Observation then Quarantined
      elsif Before = Issued and then Cause = Fresh_Claim then Effect_Intent
      elsif Before = Effect_Intent and then Cause = Historical_Effect
        then Effect_Observed
      elsif Before = Effect_Observed and then Cause = Settlement_Complete
        then Settled
      elsif (Before = Issued or else Before = Effect_Intent)
        and then Cause = No_Effect_Released then Aborted
      elsif Before = Quarantined and then Cause = Owner_Effect_Resolution
        then Effect_Observed
      elsif Before = Quarantined and then Cause = Owner_No_Effect_Resolution
        then Aborted
      else Before)
     with Global => null;
   function Advance (Before : State; Cause : Event) return State
     with Global => null,
       Post => Advance'Result = Reference (Before, Cause);
   function Changed_Only_By_Resolution
     (Before : State; Cause : Event) return Boolean is
     (Before /= Quarantined
      or else Advance (Before, Cause) = Quarantined
      or else Cause = Owner_Effect_Resolution
      or else Cause = Owner_No_Effect_Resolution)
     with Global => null,
       Post => Changed_Only_By_Resolution'Result;
end Worldline.Recovery_Protocol;
