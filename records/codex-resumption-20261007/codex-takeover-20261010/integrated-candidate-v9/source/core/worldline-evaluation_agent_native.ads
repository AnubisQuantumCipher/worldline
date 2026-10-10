with Worldline.Archive_Envelope;
with Worldline.Evaluation_Wire;

--  Independent raw agent replay. The enclosing custody consumer authenticates
--  Expected/Observed/Result_Record and the unchanged complete finalization
--  archive; this package does not turn a source label into custody authority.
package Worldline.Evaluation_Agent_Native with SPARK_Mode is
   package E renames Worldline.Archive_Envelope;
   package W renames Worldline.Evaluation_Wire;
   type Missing_Fact is
     (None, Job_Source, Launch_Source, Wait_Source, Stop_Membership_Source,
      Supervisor_Source, Resource_Source, Protocol_Source,
      Materialization_Source, Source_Mismatch, Terminal_Incomplete);
   type Facts is record
      Valid : Boolean := False;
      Status : W.Byte := 0;
      Supervisor : W.Byte := 0;
      Stopped : Boolean := False;
      Stage : W.Byte := 0;
      Missing : Missing_Fact := None;
   end record;
   type Supervisor_Facts is record
      Valid : Boolean := False;
      Kind : W.Byte := 0;
      Stopped : Boolean := False;
   end record;
   --  Shared original SystemdAdapter.outcome replay for private evaluators.
   --  Since_Us/Launcher_Exit are independently retained original JSON values;
   --  Stopped is independently native-derived cancellation/timer membership.
   function Supervisor_Decide
     (Observed, Acquisition_Kind, Unit, Since_Us, Launcher_Exit,
      Supervisor_Record : String; Stopped : Boolean;
      Reader_UID : String := "") return Supervisor_Facts
     with Global => null;
   function Decide
     (Expected, Observed, Result_Record : String;
      Data : E.Bytes; Capture : E.Span) return Facts
     with Global => null;
end Worldline.Evaluation_Agent_Native;
