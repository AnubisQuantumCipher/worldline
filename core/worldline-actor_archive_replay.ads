with Worldline.Retained_Evidence_Replay;
with Worldline.Resource_Actor_Execution;
package Worldline.Actor_Archive_Replay with SPARK_Mode is
   package R renames Worldline.Retained_Evidence_Replay;
   package E renames R.E;
   package A renames R.A;
   package X renames Worldline.Resource_Actor_Execution;
   -- Native_Status/Action/Id are meaningful only after native redecision.
   -- Decode_Refused defaults are not an admission or a native verdict.
   -- Native_Redecided retains genuine original native refusals as values;
   -- the original authenticated caller applies its own consequential policy.
   type Actor_Replay_Result is record
      State : R.Replay_State := R.Decode_Refused;
      Native_Status : X.Status := X.Status'First;
      Action : A.Operation := A.Operation'First;
      Id : A.Identities := (others => (Present => False, Value => (others => 0)));
   end record;
   function Reestablish_Actor_Observation
     (Data : E.Bytes; Observation_Archive : E.Span) return Actor_Replay_Result
     with Global => null;
   type Boundary_Kind is (Actor_Execution, Followup, Full_Broker);
   -- The caller authenticates the entire original operation journal first.
   -- Context is its factual owner/source/history capture, never permission flags.
   -- Material is original boundary.material, or boundary.value for Full_Broker.
   function Operation_Boundary_Matches
     (Data : E.Bytes; Material, Event, Context : E.Span; Kind : Boundary_Kind)
      return Boolean with Global => null;
end Worldline.Actor_Archive_Replay;
