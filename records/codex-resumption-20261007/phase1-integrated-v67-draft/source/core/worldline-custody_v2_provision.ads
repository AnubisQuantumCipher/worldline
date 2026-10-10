with Canonical_Artifacts;
with Worldline.Retained_V1_Migration;
package Worldline.Custody_V2_Provision with SPARK_Mode is
   package M renames Worldline.Retained_V1_Migration;
   package C renames M.C;
   package E renames M.E;
   package S renames C.S;
   package G renames M.G;
   use type C.Status;
   use type E.Count;
   type Artifact is (Descriptor, Plan, Genesis_File);
   type Selected_Artifact is record
      Raw, Encoded, Path : E.Span;
   end record;
   type Selected_Artifacts is array (Artifact) of Selected_Artifact;
   type Status is (Selected_Context_Refused, Prior_Context_Refused,
                   Retained_Chain_Refused, Operation_Not_Closed,
                   New_Origin_Eligible, Closed_V1_Migration_Eligible);
   type Result is record
      State : Status;
      Position : E.Count := 0;
   end record;
   function Selected_Matches
     (Data : E.Bytes; Selected : Selected_Artifacts; Journal_Path, Key : E.Span)
      return Boolean with Global => null;
   function Prior_Matches
     (Data : E.Bytes; Selected : Selected_Artifacts; Journal_Path : E.Span;
      Prior : M.Context_Inputs; Prior_Descriptor, Prior_Plan,
      Prior_Genesis, Retained_Head : E.Span) return Boolean with Global => null;
   -- NEW is an explicit selected operator mode with prior_custody=null. It
   -- never follows from missing mutable state. Source/OFD custody is a caller
   -- obligation; eligibility permits only exclusive offline artifact creation.
   function Decide
     (Data : E.Bytes; Selected : Selected_Artifacts; Journal_Path, Key, Mode : E.Span;
      Prior : M.Context_Inputs; Prior_Descriptor, Prior_Plan, Prior_Genesis,
      Prior_Head, Retained_Head : E.Span; Genesis : C.Genesis_Rows;
      Rows : C.Event_Rows; Heads : C.Head_Rows) return Result
     with Global => null,
       Post =>
         (if Decide'Result.State in New_Origin_Eligible | Closed_V1_Migration_Eligible
          then Selected_Matches (Data, Selected, Journal_Path, Key)) and then
         (if Decide'Result.State = New_Origin_Eligible then
            M.Literal (Data, Mode, "NEW") and then
            Genesis'Length = 0 and then Rows'Length = 0 and then Heads'Length = 0) and then
         (if Decide'Result.State = Closed_V1_Migration_Eligible then
            M.Literal (Data, Mode, "MIGRATE") and then
            Prior_Matches (Data, Selected, Journal_Path, Prior, Prior_Descriptor,
                           Prior_Plan, Prior_Genesis, Retained_Head) and then
            M.Same (Data, Key, Prior (M.Issuer_Key).Raw) and then
            C.Verify (Data, Key, Prior_Genesis, Prior_Head, Genesis, Rows, Heads).State =
              C.Retained_Chain_Matches and then
            M.Closed_Operations (Data, Rows) and then
            Heads'Length = 1 and then M.Same (Data, Heads (Heads'First).Event_Id, Retained_Head));
end Worldline.Custody_V2_Provision;
