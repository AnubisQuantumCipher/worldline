with Interfaces;
with Worldline;
with Worldline.C_API;
with Worldline.Collapse;
with Worldline.Collapse_Wire;
with Worldline.Identities;
with Worldline.Transitions;

package body Worldline_Collapse_Checks is
   use Worldline.Collapse;
   use Worldline.Identities;
   use type Interfaces.Unsigned_8;

   procedure Check (Condition : Boolean; Message : String) is
   begin
      if not Condition then
         raise Program_Error with Message;
      end if;
   end Check;

   function H (V : Interfaces.Unsigned_8) return Worldline.Hash is ([others => V]);

   function C (V : Interfaces.Unsigned_8) return Optional_Content_Id is
     (Present => True, Value => Content_Id (H (V)));
   function S (V : Interfaces.Unsigned_8) return Optional_Subject_Id is
     (Present => True, Value => Subject_Id (H (V)));
   function St (V : Interfaces.Unsigned_8) return Optional_State_Root is
     (Present => True, Value => State_Root (H (V)));
   function Cr (V : Interfaces.Unsigned_8) return Optional_Content_Root is
     (Present => True, Value => Content_Root (H (V)));
   function D (V : Interfaces.Unsigned_8) return Optional_Delta_Id is
     (Present => True, Value => Delta_Id (H (V)));
   function Rs (V : Interfaces.Unsigned_8) return Optional_Root_Set_Id is
     (Present => True, Value => Root_Set_Id (H (V)));
   function Rq (V : Interfaces.Unsigned_8) return Optional_Requirement_Id is
     (Present => True, Value => Requirement_Id (H (V)));
   function Vs (V : Interfaces.Unsigned_8) return Optional_Verifier_Set_Id is
     (Present => True, Value => Verifier_Set_Id (H (V)));
   function Ws (V : Interfaces.Unsigned_8) return Optional_Watch_Set_Id is
     (Present => True, Value => Watch_Set_Id (H (V)));
   function G (V : Interfaces.Unsigned_64) return Optional_Generation is
     (Present => True, Value => V);

   --  A request every obligation holds for, at Commit, in candidate mode.
   Good : constant Collapse_Request :=
     (Candidate_State => Worldline.Transitions.Valid,
      Request_Phase => Commit,
      Mode => Candidate_Evaluation,
      Conflicts => None_Found,
      Foreign_Writes => None_Found,
      Roster_Complete => True,
      Staged_Roster_Complete => False,
      Expected_Parent => C (1), Candidate_Parent => C (1),
      Expected_Subject => S (2), Evidence_Subject => S (2),
      Expected_Base => St (3), Candidate_Base => St (3),
      Expected_Delta => D (4), Candidate_Delta => D (4),
      Expected_Root_Set => Rs (5), Candidate_Root_Set => Rs (5),
      Expected_Staged_Root => St (6), Actual_Staged_Root => St (6),
      Staged_Content_Root => Cr (7), Tested_Root => Cr (7),
      Current_Requirement => Rq (8), Evaluated_Requirement => Rq (8),
      Declared_Verifiers => Vs (9), Executed_Verifiers => Vs (9),
      Staged_Evaluated_Requirement => (others => <>),
      Staged_Executed_Verifiers => (others => <>),
      Staged_Examined_Root => (others => <>),
      Expected_Checkpoint => (others => <>),
      Witnessed_Checkpoint => (others => <>),
      Registered_Watch_Set => Ws (10), Watched_Set => Ws (10),
      Generation_Before => G (41), Generation_After => G (41));

   procedure Expect (R : Collapse_Request; Want : Decision; Message : String) is
   begin
      Check (Decide (R) = Want,
             Message & ": got " & Decision'Image (Decide (R)));
   end Expect;

   procedure Typed_Decisions is
      R : Collapse_Request := Good;
   begin
      Expect (R, Authorized, "a request every obligation holds for");

      R := Good; R.Candidate_State := Worldline.Transitions.Degraded;
      Expect (R, Invalid_Candidate, "degraded candidate");
      R := Good; R.Conflicts := Found;
      --  Conflicted merges have no staged tree; absence is not reported first.
      R.Expected_Staged_Root := (others => <>); R.Actual_Staged_Root := (others => <>);
      R.Staged_Content_Root := (others => <>);
      Expect (R, Conflict, "conflict with no staged tree");
      R := Good; R.Foreign_Writes := Found;
      Expect (R, Foreign_Managed_Write, "foreign write");
      R := Good; R.Conflicts := Unmeasured;
      Expect (R, Measurement_Absent, "conflicts unmeasured");
      R := Good; R.Foreign_Writes := Unmeasured;
      Expect (R, Measurement_Absent, "foreign writes unmeasured");
      R := Good; R.Generation_Before := (others => <>);
      Expect (R, Measurement_Absent, "no generation before");
      R := Good; R.Generation_Before := (others => <>); R.Generation_After := (others => <>);
      Expect (R, Measurement_Absent, "no watcher at all");
      R := Good; R.Watched_Set := (others => <>);
      Expect (R, Measurement_Absent, "no watch set");
      R := Good; R.Watched_Set := Ws (11);
      Expect (R, Watch_Incomplete, "a root not under watch");
      R := Good; R.Generation_After := G (42);
      Expect (R, Prime_Changed, "PRIME moved during the decision");
      R := Good; R.Roster_Complete := False; R.Executed_Verifiers := (others => <>);
      Expect (R, Execution_Evidence_Incomplete, "roster false with no verifier set");

      --  Every required identity: one side absent, and both absent (the old
      --  zero-equals-zero case). Never authorized.
      for Field in 1 .. 12 loop
         for Both in Boolean loop
            R := Good;
            case Field is
               when 1 => R.Candidate_Parent := (others => <>);
                         if Both then R.Expected_Parent := (others => <>); end if;
               when 2 => R.Evidence_Subject := (others => <>);
                         if Both then R.Expected_Subject := (others => <>); end if;
               when 3 => R.Candidate_Base := (others => <>);
                         if Both then R.Expected_Base := (others => <>); end if;
               when 4 => R.Candidate_Delta := (others => <>);
                         if Both then R.Expected_Delta := (others => <>); end if;
               when 5 => R.Candidate_Root_Set := (others => <>);
                         if Both then R.Expected_Root_Set := (others => <>); end if;
               when 6 => R.Actual_Staged_Root := (others => <>);
                         if Both then R.Expected_Staged_Root := (others => <>); end if;
               when 7 => R.Staged_Content_Root := (others => <>);
                         if Both then R.Tested_Root := (others => <>); end if;
               when 8 => R.Evaluated_Requirement := (others => <>);
                         if Both then R.Current_Requirement := (others => <>); end if;
               when 9 => R.Executed_Verifiers := (others => <>);
                         if Both then R.Declared_Verifiers := (others => <>); end if;
               when 10 => R.Current_Requirement := (others => <>);
               when 11 => R.Declared_Verifiers := (others => <>);
               when others => R.Expected_Parent := (others => <>);
            end case;
            Expect (R, Identity_Absent, "a required identity absent");
         end loop;
      end loop;

      R := Good; R.Candidate_Parent := C (99);
      Expect (R, Parent_Mismatch, "parent");
      R := Good; R.Evidence_Subject := S (99);
      Expect (R, Evidence_Subject_Mismatch, "evidence subject");
      R := Good; R.Candidate_Base := St (99);
      Expect (R, Base_Mismatch, "base");
      R := Good; R.Candidate_Delta := D (99);
      Expect (R, Delta_Mismatch, "delta");
      R := Good; R.Candidate_Root_Set := Rs (99);
      Expect (R, Root_Set_Mismatch, "root set");
      R := Good; R.Actual_Staged_Root := St (99);
      Expect (R, Staged_Root_Mismatch, "staged root at commit");
      R := Good; R.Evaluated_Requirement := Rq (99);
      Expect (R, Validation_Context_Mismatch, "stale requirement");
      R := Good; R.Executed_Verifiers := Vs (99);
      Expect (R, Verifier_Execution_Identity_Mismatch, "other verifiers ran");

      --  Prepare: one staged observation suffices, the second is Commit's.
      R := Good; R.Request_Phase := Prepare; R.Actual_Staged_Root := (others => <>);
      Expect (R, Authorized, "prepare with the merge's own capture");
      R := Good; R.Request_Phase := Prepare; R.Actual_Staged_Root := St (99);
      Expect (R, Authorized, "prepare does not consult the second capture");

      --  What the primary evaluation examined must be what goes live, unless
      --  a staged-merge evaluation covers the staged bytes.
      R := Good; R.Tested_Root := (others => <>);
      Expect (R, Staged_Untested, "tested root absent");
      R := Good; R.Tested_Root := Cr (99);
      Expect (R, Staged_Untested, "tested root differs");
      R := Good; R.Tested_Root := Cr (99);
      R.Staged_Evaluated_Requirement := Rq (8); R.Staged_Roster_Complete := True;
      R.Staged_Executed_Verifiers := Vs (9); R.Staged_Examined_Root := Cr (7);
      Expect (R, Authorized, "a staged evaluation covers the merge result");
      declare
         Covered_Base : constant Collapse_Request := R;
      begin
         R := Covered_Base; R.Staged_Evaluated_Requirement := Rq (98);
         Expect (R, Staged_Untested, "staged evaluation against a stale requirement");
         R := Covered_Base; R.Staged_Roster_Complete := False;
         Expect (R, Staged_Untested, "staged roster incomplete");
         R := Covered_Base; R.Staged_Executed_Verifiers := (others => <>);
         Expect (R, Staged_Untested, "staged verifiers absent");
         R := Covered_Base; R.Staged_Executed_Verifiers := Vs (98);
         Expect (R, Staged_Untested, "staged verifiers differ");
         R := Covered_Base; R.Staged_Examined_Root := (others => <>);
         Expect (R, Staged_Untested, "staged examined root absent");
         R := Covered_Base; R.Staged_Examined_Root := Cr (98);
         Expect (R, Staged_Untested, "staged evaluation examined other bytes");
         --  A covering staged evaluation never excuses the primary evidence.
         R := Covered_Base; R.Roster_Complete := False;
         Expect (R, Execution_Evidence_Incomplete, "primary roster incomplete");
         R := Covered_Base; R.Evaluated_Requirement := Rq (97);
         Expect (R, Validation_Context_Mismatch, "primary evidence stale");
      end;

      --  Checkpoint return.
      R := Good;
      R.Mode := Checkpoint_Return;
      R.Evaluated_Requirement := (others => <>); R.Executed_Verifiers := (others => <>);
      R.Roster_Complete := False;
      R.Expected_Checkpoint := C (20); R.Witnessed_Checkpoint := C (20);
      Expect (R, Authorized, "a witnessed checkpoint return");
      declare
         Returned : constant Collapse_Request := R;
      begin
         R := Returned; R.Witnessed_Checkpoint := (others => <>);
         Expect (R, Checkpoint_Unwitnessed, "no witness");
         R := Returned; R.Witnessed_Checkpoint := C (21);
         Expect (R, Checkpoint_Mismatch, "witness disagrees");
         R := Returned; R.Expected_Checkpoint := (others => <>);
         Expect (R, Identity_Absent, "subject content absent");
         R := Returned; R.Tested_Root := Cr (99);
         Expect (R, Staged_Untested, "checkpoint mode keeps the tested-bytes obligation");
      end;

      --  The zeroed request is never authorized.
      declare
         Zeroed : Collapse_Request;
      begin
         Zeroed.Candidate_State := Worldline.Transitions.Valid;
         Zeroed.Request_Phase := Commit;
         Zeroed.Mode := Candidate_Evaluation;
         Zeroed.Conflicts := Unmeasured;
         Zeroed.Foreign_Writes := Unmeasured;
         Zeroed.Roster_Complete := False;
         Zeroed.Staged_Roster_Complete := False;
         Check (Decide (Zeroed) /= Authorized, "the zeroed request was authorized");
      end;
   end Typed_Decisions;

   --  The wire: a Well_Formed good request decides as the typed one does, and
   --  every malformed encoding is 255.
   procedure Put (Field : out Worldline.Collapse_Wire.Raw_Optional_Hash;
                  V : Interfaces.Unsigned_8) is
   begin
      Field.Present := 1;
      Field.Value := [others => V];
   end Put;

   function Good_Wire return Worldline.Collapse_Wire.Raw_Request is
      use Worldline.Collapse_Wire;
      Absent : constant Raw_Optional_Hash := (Present => 0, Value => [others => 0]);
      R : Raw_Request :=
        (Candidate_State => 2, Phase => 0, Evaluation_Mode => 0, Conflicts => 1,
         Foreign_Writes => 1, Roster_Complete => 1, Staged_Roster_Complete => 0,
         Generation_Before => (Present => 1, Value_LE => [41, others => 0]),
         Generation_After => (Present => 1, Value_LE => [41, others => 0]),
         others => Absent);
   begin
      Put (R.Expected_Parent, 1); Put (R.Candidate_Parent, 1);
      Put (R.Expected_Subject, 2); Put (R.Evidence_Subject, 2);
      Put (R.Expected_Base, 3); Put (R.Candidate_Base, 3);
      Put (R.Expected_Delta, 4); Put (R.Candidate_Delta, 4);
      Put (R.Expected_Root_Set, 5); Put (R.Candidate_Root_Set, 5);
      Put (R.Expected_Staged_Root, 6); Put (R.Actual_Staged_Root, 6);
      Put (R.Staged_Content_Root, 7); Put (R.Tested_Root, 7);
      Put (R.Current_Requirement, 8); Put (R.Evaluated_Requirement, 8);
      Put (R.Declared_Verifiers, 9); Put (R.Executed_Verifiers, 9);
      Put (R.Registered_Watch_Set, 10); Put (R.Watched_Set, 10);
      return R;
   end Good_Wire;

   procedure Wire is
      use Worldline.Collapse_Wire;
      Base : aliased constant Raw_Request := Good_Wire;
      Bad : aliased Raw_Request;
   begin
      Check (Well_Formed (Base), "good wire request is not well formed");
      Check (Decode (Base) = Good, "wire decode differs from the typed request");
      Check (Worldline.C_API.Collapse_Decide (Base'Unchecked_Access) = 0,
             "good wire request not authorized");
      Check (Worldline.C_API.Collapse_Decide (null) = 255, "null request accepted");
      for Case_Number in 1 .. 16 loop
         Bad := Base;
         case Case_Number is
            when 1 => Bad.Expected_Parent.Present := 2;
            when 2 => Bad.Expected_Parent := (Present => 0, Value => [others => 1]);
            when 3 => Bad.Expected_Parent := (Present => 1, Value => [others => 0]);
            when 4 => Bad.Generation_Before := (Present => 0, Value_LE => [1, others => 0]);
            when 5 => Bad.Generation_Before.Present := 2;
            when 6 => Bad.Candidate_State := 7;
            when 7 => Bad.Phase := 2;
            when 8 => Bad.Evaluation_Mode := 2;
            when 9 => Bad.Conflicts := 3;
            when 10 => Bad.Foreign_Writes := 3;
            when 11 => Bad.Roster_Complete := 2;
            when 12 => Bad.Staged_Roster_Complete := 2;
            when 13 => Bad.Phase := 1;  --  prepare with the second capture present
            when 14 => Put (Bad.Witnessed_Checkpoint, 20);  --  a checkpoint field in candidate mode
            when 15 => Bad.Evaluation_Mode := 1;  --  checkpoint mode with primary evidence present
            when others => Bad.Tested_Root := (Present => 1, Value => [others => 0]);
         end case;
         Check (not Well_Formed (Bad), "malformed wire request is well formed");
         Check (Worldline.C_API.Collapse_Decide (Bad'Unchecked_Access) = 255,
                "malformed wire request was decided");
      end loop;
   end Wire;

   procedure Run is
   begin
      Typed_Decisions;
      Wire;
   end Run;

end Worldline_Collapse_Checks;
