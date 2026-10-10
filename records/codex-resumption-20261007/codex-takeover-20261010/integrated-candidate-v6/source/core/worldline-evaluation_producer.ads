with Worldline.Evaluation_Wire;
with Worldline.Evaluation_Report_Facts;
with Worldline.Archive_Envelope;

--  Native full-record/acquisition projection. No caller admission decisions.
package Worldline.Evaluation_Producer with SPARK_Mode is
   package W renames Worldline.Evaluation_Wire;
   package R renames Worldline.Evaluation_Report_Facts;
   package E renames Worldline.Archive_Envelope;
   type Provider_Gap is
     (No_Provider_Gap, Acquisition_Unavailable, Protected_Custody_Unavailable);
   type Produced_Record is record
      Raw : W.Raw_Record := W.Zero_Record;
      Confinement : R.Confinement_Observation := R.Confinement_Unmeasured;
      Gap : Provider_Gap := Acquisition_Unavailable;
   end record;
   -- Pure full-record projection. The recovery material owner establishes
   -- original archive/subject/issuer correspondence before historical use.
   -- All original observations, report facts and presence fields are retained;
   -- no original report or custody label establishes observed confinement.
   function Original_Projection
     (Result_Record, Declared : String;
      Parser_Declaration : String := ""; Raw_Capsule : String := "")
      return Produced_Record with Global => null;
   -- Expected/Observed are the independent invocation-start/acquisition sources.
   -- Their JSON-null, no-source domain uses the complete original projection
   -- before classification; supplied empty/malformed sources never select it.
   -- Retained invocation, acquisition, provider or independent terminal bytes
   -- keep the acquisition relation. Native engine inputs are redecided in either
   -- domain, not replaced by carried status. Record-only control objects must
   -- retain engine origin; mixed roles keep the acquisition relation.
   -- All strings contain original UTF8 bytes, not truncated/native labels.
   -- Current results retain their protected syntax operands. Historical replay
   -- supplies separate authenticated facts without modifying any original key.
   function Derive
     (Expected, Observed, Result_Record, Declared : String;
      Parser_Declaration : String := ""; Raw_Capsule : String := "";
      Agent_Data : E.Bytes := (1 .. 0 => 0);
      Agent_Capture : E.Span := (1, 0))
      return Produced_Record with Global => null;
end Worldline.Evaluation_Producer;
