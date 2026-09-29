with Ada.Text_IO;
with Interfaces.C;
with Attest;
with Attest.SHA256;
with Interfaces;
with Worldline;
with Worldline.Ancestry;
with Worldline.C_API;
with Worldline.Causal_Graph;
with Worldline.Collapse;
with Worldline.Evaluation;
with Worldline.Receipts;
with Worldline.Transitions;
with Worldline.World;
with System;

procedure Worldline_Core_Tests is
   use type Worldline.Hash;
   use type Worldline.Collapse.Decision;
   use type Worldline.Transitions.Transaction_State;
   use type Worldline.Evaluation.Execution_State;
   use type Worldline.Evaluation.Outcome;
   use type Interfaces.Unsigned_8;
   use type Interfaces.Unsigned_32;
   use type Interfaces.C.size_t;

   procedure Check (Condition : Boolean; Message : String) is
   begin
      if not Condition then
         raise Program_Error with Message;
      end if;
   end Check;

   function Filled (Value : Attest.Byte) return Worldline.Hash is
     [others => Value];

   H0 : constant Worldline.Hash := Filled (0);
   H1 : constant Worldline.Hash := Filled (1);
   H2 : constant Worldline.Hash := Filled (2);
   H3 : constant Worldline.Hash := Filled (3);
   H4 : constant Worldline.Hash := Filled (4);
   H5 : constant Worldline.Hash := Filled (5);
   H6 : constant Worldline.Hash := Filled (6);
   H7 : constant Worldline.Hash := Filled (7);

   Empty : constant Attest.Byte_Array (1 .. 0) := [others => 0];
   Empty_SHA256 : constant Worldline.Hash :=
     [16#e3#, 16#b0#, 16#c4#, 16#42#, 16#98#, 16#fc#, 16#1c#, 16#14#,
      16#9a#, 16#fb#, 16#f4#, 16#c8#, 16#99#, 16#6f#, 16#b9#, 16#24#,
      16#27#, 16#ae#, 16#41#, 16#e4#, 16#64#, 16#9b#, 16#93#, 16#4c#,
      16#a4#, 16#95#, 16#99#, 16#1b#, 16#78#, 16#52#, 16#b8#, 16#55#];

   Request : Worldline.Collapse.Collapse_Request :=
     (Candidate_State => Worldline.Transitions.Valid,
      Has_Conflicts => False,
      Has_Foreign_Managed_Writes => False,
      Expected_Parent => H1,
      Candidate_Parent => H1,
      Expected_Owner => H2,
      Candidate_Owner => H2,
      Expected_Base => H3,
      Candidate_Base => H3,
      Expected_Delta => H4,
      Candidate_Delta => H4,
      Expected_Root_Set => H5,
      Candidate_Root_Set => H5,
      Expected_Staged_Root => H6,
      Actual_Staged_Root => H6,
      Expected_Validation_Context => H1,
      Candidate_Validation_Context => H1,
      Tested_Root => H2,
      Staged_Content_Root => H2,
      Execution_Evidence_Complete => True,
      Expected_Executed_Verifier => H7,
      Actual_Executed_Verifier => H7,
      Mode => Worldline.Collapse.Candidate_Evaluation,
      Checkpoint_Witnessed => False,
      Expected_Checkpoint => H0,
      Witnessed_Checkpoint => H0);

   Full_Presence : constant Worldline.Evaluation.Evidence_Presence :=
     (Record_Identified | Verdict_Recorded | Binding_Established |
      Declaration_Matches | Bundle_Identified => True);

   C_Request : aliased Worldline.C_API.C_Collapse_Request;
   C_Value : aliased Worldline.C_API.C_Evaluation_Classification;
   C_Presence : aliased Worldline.C_API.C_Evidence_Presence :=
     (others => 1);
   C_State : aliased Interfaces.Unsigned_8;
   Roster_Bytes : aliased array (1 .. 3) of Interfaces.Unsigned_8 :=
     [1, 1, 1];

   Parent : Worldline.Ancestry.Parent_Guard :=
     Worldline.Ancestry.New_Parent_Guard (H1);
   Owner : Worldline.Ancestry.Owner_Guard :=
     Worldline.Ancestry.New_Owner_Guard (H2);
   Causal : Worldline.Causal_Graph.Chain :=
     Worldline.Causal_Graph.New_Chain (H0);
   Receipt : Worldline.Receipts.Chain :=
     Worldline.Receipts.New_Chain (H0);
   Transaction : Worldline.Transitions.Transaction_State :=
     Worldline.Transitions.Prepared;
   Evaluation_State : Worldline.Evaluation.Execution_State :=
     Worldline.Evaluation.Not_Attempted;
   Evaluation_Facts : Worldline.Evaluation.Observations :=
     (Source => Worldline.Evaluation.External,
      Status => Worldline.Evaluation.Pass_Status,
      Channel => Worldline.Evaluation.Accepted_Channel,
      Stage => Worldline.Evaluation.No_Stage,
      Exit_Present => True,
      Exit_Integer => True,
      Supervisor => Worldline.Evaluation.No_Supervision,
      Supervisor_Stopped => False,
      Bundle_Present => True,
      Bundle_Is_Mapping => True,
      Bundle_Stable => True,
      Bundle_Changed => False,
      Unsatisfied_Imports => False);
   Evaluation_Result : Worldline.Evaluation.Classification;
   Linked : Worldline.Hash;
   Identity_One : Worldline.Hash;
   Identity_Two : Worldline.Hash;
begin
   Check
     (Attest.SHA256.Hash (Empty) = Empty_SHA256,
      "published empty SHA-256 vector failed");

   Identity_One := Worldline.World.Identity (H0, H1, H2, H3, H4, H5);
   Identity_Two := Worldline.World.Identity (H0, H1, H2, H3, H4, H5);
   Check (Identity_One = Identity_Two, "world identity is not deterministic");
   Check
     (Identity_One /= Worldline.World.Identity (H0, H1, H2, H3, H4, H6),
      "evidence root omitted from world identity");

   Worldline.Ancestry.Claim (Parent, H1, H1);
   Check (Worldline.Ancestry.Accepted (Parent), "valid parent rejected");
   Worldline.Ancestry.Claim (Parent, H1, H2);
   Check (not Worldline.Ancestry.Accepted (Parent), "bad claim accepted");
   Worldline.Ancestry.Claim (Parent, H1, H1);
   Check (not Worldline.Ancestry.Accepted (Parent), "parent denial unstuck");

   Worldline.Ancestry.Check_Owner (Owner, H3);
   Check
     (not Worldline.Ancestry.Owner_Accepted (Owner),
      "owner mismatch accepted");
   Worldline.Ancestry.Check_Owner (Owner, H2);
   Check
     (not Worldline.Ancestry.Owner_Accepted (Owner),
      "owner denial unstuck");

   Check
     (Worldline.Transitions.Allowed
        (Worldline.Transitions.Mutable, Worldline.Transitions.Finalizing),
      "mutable to finalizing denied");
   Check
     (not Worldline.Transitions.Allowed
        (Worldline.Transitions.Dead, Worldline.Transitions.Valid),
      "dead world became valid");
   Check
     (not Worldline.Transitions.Allowed
        (Worldline.Transitions.Degraded, Worldline.Transitions.Collapsed),
      "degraded world became collapsible");

   Worldline.Transitions.Advance
     (Transaction, Worldline.Transitions.Denied);
   Worldline.Transitions.Advance
     (Transaction, Worldline.Transitions.Committed);
   Check
     (Transaction = Worldline.Transitions.Denied,
      "denied transaction committed");

   --  The C export must agree with the proved unit for every pair, and
   --  refuse every out-of-range code, so the Python runtime that consults
   --  wl_transaction_transition_allowed sees exactly the proved lifecycle.
   for From in Worldline.Transitions.Transaction_State loop
      for To in Worldline.Transitions.Transaction_State loop
         Check
           (Worldline.C_API.Transaction_Transition_Allowed
              (Interfaces.Unsigned_8
                 (Worldline.Transitions.Transaction_State'Pos (From)),
               Interfaces.Unsigned_8
                 (Worldline.Transitions.Transaction_State'Pos (To))) =
            (if Worldline.Transitions.Transaction_Allowed (From, To)
             then 1 else 0),
            "C transaction lifecycle export disagrees with proved unit");
      end loop;
   end loop;
   Check
     (Worldline.C_API.Transaction_Transition_Allowed (5, 0) = 0
      and then Worldline.C_API.Transaction_Transition_Allowed (0, 255) = 0,
      "out-of-range transaction code accepted");
   Check
     (Worldline.C_API.Transaction_Transition_Allowed (2, 3) = 0,
      "C export let a denied transaction commit");

   Worldline.Evaluation.Advance
     (Evaluation_State, Worldline.Evaluation.Prepared);
   Worldline.Evaluation.Advance
     (Evaluation_State, Worldline.Evaluation.Started);
   Worldline.Evaluation.Advance
     (Evaluation_State, Worldline.Evaluation.Completed);
   Worldline.Evaluation.Advance
     (Evaluation_State, Worldline.Evaluation.Started);
   Check
     (Evaluation_State = Worldline.Evaluation.Completed,
      "completed evaluation resumed under the same identity");
   Evaluation_Result := Worldline.Evaluation.Classify (Evaluation_Facts);
   Check
     (Evaluation_Result.Execution = Worldline.Evaluation.Completed
      and Evaluation_Result.Result = Worldline.Evaluation.Passed,
      "trusted completed pass was not classified");
   Check
     (Worldline.Evaluation.Admissible
        (Evaluation_Result, Worldline.Evaluation.Verified_Report,
         Full_Presence),
      "complete report was not admitted");
   Check
     (not Worldline.Evaluation.Admissible
        (Evaluation_Result, Worldline.Evaluation.Verified_Report,
         (Full_Presence with delta Binding_Established => False)),
      "unestablished examiner provenance admitted");
   Check
     (not Worldline.Evaluation.Admissible
        (Evaluation_Result, Worldline.Evaluation.Verified_Report,
         (Full_Presence with delta Declaration_Matches => False)),
      "an undeclared evaluator format admitted");

   --  An examiner whose staged bundle cannot satisfy its own imports: a FAIL
   --  is not a verdict on the candidate; a PASS resolved its imports.
   Evaluation_Facts.Unsatisfied_Imports := True;
   Evaluation_Facts.Status := Worldline.Evaluation.Fail_Status;
   Evaluation_Result := Worldline.Evaluation.Classify (Evaluation_Facts);
   Check
     (Evaluation_Result.Execution = Worldline.Evaluation.Evaluator_Incomplete
      and Evaluation_Result.Result = Worldline.Evaluation.No_Outcome,
      "a failure from an incomplete evaluator became a candidate verdict");
   Evaluation_Facts.Status := Worldline.Evaluation.Pass_Status;
   Evaluation_Result := Worldline.Evaluation.Classify (Evaluation_Facts);
   Check
     (Evaluation_Result.Execution = Worldline.Evaluation.Completed
      and Evaluation_Result.Result = Worldline.Evaluation.Passed,
      "a pass whose imports resolved was not completed");
   Evaluation_Facts.Unsatisfied_Imports := False;

   --  The lifecycle export agrees with the proved relation for every pair.
   for From in Worldline.Evaluation.Execution_State loop
      for To in Worldline.Evaluation.Execution_State loop
         Check
           (Worldline.C_API.Evaluation_Transition_Allowed
              (Interfaces.Unsigned_8
                 (Worldline.Evaluation.Execution_State'Pos (From)),
               Interfaces.Unsigned_8
                 (Worldline.Evaluation.Execution_State'Pos (To))) =
            (if Worldline.Evaluation.Transition_Allowed (From, To)
             then 1 else 0),
            "C evaluation lifecycle export disagrees with proved unit");
      end loop;
   end loop;
   Check
     (Worldline.C_API.Evaluation_Transition_Allowed (9, 0) = 255
      and then Worldline.C_API.Evaluation_Transition_Allowed (0, 9) = 255,
      "out-of-range evaluation state accepted");
   C_State := 0;
   Check
     (Worldline.C_API.Evaluation_Advance (C_State'Unchecked_Access, 8) = 0
      and then C_State = 0,
      "not-attempted evaluation jumped to completed");
   Check
     (Worldline.C_API.Evaluation_Advance (C_State'Unchecked_Access, 1) = 0
      and then C_State = 1,
      "prepare step refused");
   Check
     (Worldline.C_API.Evaluation_Advance (C_State'Unchecked_Access, 200) = 255,
      "invalid requested state accepted");
   Check
     (Worldline.C_API.Evaluation_Advance (null, 1) = 255,
      "null state accepted");

   --  Roster: nothing required is complete only when declared so.
   declare
      None : constant Worldline.Evaluation.Admissions (1 .. 0) :=
        [others => True];
   begin
      Check
        (not Worldline.Evaluation.Roster_Complete (None, False),
         "an undeclared empty roster was complete");
      Check
        (Worldline.Evaluation.Roster_Complete (None, True),
         "a declared empty roster was incomplete");
      Check
        (not Worldline.Evaluation.Roster_Complete ([True, False, True], True),
         "a roster with a refused check was complete");
   end;
   Check
     (Worldline.C_API.Evaluation_Roster_Complete
        (Roster_Bytes'Address, 3, 0) = 1,
      "complete C roster refused");
   Roster_Bytes (2) := 0;
   Check
     (Worldline.C_API.Evaluation_Roster_Complete
        (Roster_Bytes'Address, 3, 1) = 0,
      "C roster with a refused check admitted");
   Roster_Bytes (2) := 2;
   Check
     (Worldline.C_API.Evaluation_Roster_Complete
        (Roster_Bytes'Address, 3, 1) = 255,
      "non-Boolean C roster byte accepted");
   Roster_Bytes (2) := 1;
   Check
     (Worldline.C_API.Evaluation_Roster_Complete
        (System.Null_Address, 0, 0) = 0
      and then Worldline.C_API.Evaluation_Roster_Complete
        (System.Null_Address, 0, 1) = 1
      and then Worldline.C_API.Evaluation_Roster_Complete
        (System.Null_Address, 1, 1) = 255
      and then Worldline.C_API.Evaluation_Roster_Complete
        (Roster_Bytes'Address, 4097, 1) = 255
      and then Worldline.C_API.Evaluation_Roster_Complete
        (Roster_Bytes'Address, 3, 2) = 255,
      "C roster boundary encodings misread");

   --  Admissibility over C: incoherent classifications and non-Boolean
   --  presence bytes are invalid encodings, not denials to reinterpret.
   C_Value := (Execution => 8, Outcome => 1, Bundle => 1);
   Check
     (Worldline.C_API.Evaluation_Admissible
        (C_Value'Unchecked_Access, 1, C_Presence'Unchecked_Access) = 1,
      "C admission of a complete pass refused");
   C_Value := (Execution => 8, Outcome => 0, Bundle => 1);
   Check
     (Worldline.C_API.Evaluation_Admissible
        (C_Value'Unchecked_Access, 1, C_Presence'Unchecked_Access) = 255,
      "completion without an outcome accepted as an encoding");
   C_Value := (Execution => 7, Outcome => 1, Bundle => 1);
   Check
     (Worldline.C_API.Evaluation_Admissible
        (C_Value'Unchecked_Access, 1, C_Presence'Unchecked_Access) = 255,
      "an outcome without completion accepted as an encoding");
   C_Value := (Execution => 8, Outcome => 1, Bundle => 1);
   C_Presence.Bundle_Identified := 2;
   Check
     (Worldline.C_API.Evaluation_Admissible
        (C_Value'Unchecked_Access, 1, C_Presence'Unchecked_Access) = 255,
      "non-Boolean presence byte accepted");
   C_Presence.Bundle_Identified := 0;
   Check
     (Worldline.C_API.Evaluation_Admissible
        (C_Value'Unchecked_Access, 1, C_Presence'Unchecked_Access) = 0,
      "an unidentified declared bundle admitted");
   Check
     (Worldline.C_API.Evaluation_Admissible
        (C_Value'Unchecked_Access, 1, null) = 255,
      "null presence accepted");

   Check (Worldline.C_API.ABI_Generation = 4, "ABI generation is not 4");
   Check
     (Worldline.C_API.Layout_Size (0) = C_Request'Size / 8
      and then Worldline.C_API.Layout_Size (3) = 5
      and then Worldline.C_API.Layout_Size (9) = 0,
      "layout sizes misreported");
   declare
      function Offset (Selector : Interfaces.Unsigned_8; Name : String) return Interfaces.C.size_t is
        (Worldline.C_API.Layout_Offset (Selector, Name'Address, Interfaces.C.size_t (Name'Length)));
   begin
      Check
        (Offset (0, "candidate_state") = 0
         and then Offset (0, "expected_parent") = 4
         and then Offset (3, "bundle_identified") = 4
         and then Offset (3, "nonexistent") = Interfaces.C.size_t'Last
         and then Offset (9, "candidate_state") = Interfaces.C.size_t'Last
         and then Offset (0, "Candidate_State") = Interfaces.C.size_t'Last,
         "layout offsets misreported");
   end;
   C_Value := (Execution => 1, Outcome => 0, Bundle => 1);
   Check
     (Worldline.C_API.Evaluation_Admissible
        (C_Value'Unchecked_Access, 1, C_Presence'Unchecked_Access) = 255,
      "an in-flight classification accepted as an encoding");
   Evaluation_Facts.Channel := Worldline.Evaluation.Malformed_Channel;
   Evaluation_Result := Worldline.Evaluation.Classify (Evaluation_Facts);
   Check
     (Evaluation_Result.Execution = Worldline.Evaluation.Unclassified
      and Evaluation_Result.Result = Worldline.Evaluation.No_Outcome,
      "malformed channel became a completed pass");
   Evaluation_Facts.Channel := Worldline.Evaluation.Accepted_Channel;
   Evaluation_Facts.Exit_Present := False;
   Evaluation_Facts.Exit_Integer := False;
   Evaluation_Result := Worldline.Evaluation.Classify (Evaluation_Facts);
   Check
     (Evaluation_Result.Execution /= Worldline.Evaluation.Completed,
      "missing supervised exit became completed");

   Check
     (Worldline.Collapse.Decide (Request) = Worldline.Collapse.Authorized,
      "valid collapse denied");
   Request.Candidate_State := Worldline.Transitions.Dead;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Invalid_Candidate,
      "dead candidate authorized");
   Request.Candidate_State := Worldline.Transitions.Valid;
   Request.Candidate_Parent := H7;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Parent_Mismatch,
      "parent mismatch missed");
   Request.Candidate_Parent := H1;
   Request.Candidate_Owner := H7;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Owner_Mismatch,
      "owner mismatch missed");
   Request.Candidate_Owner := H2;
   Request.Candidate_Base := H7;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Base_Mismatch,
      "base mismatch missed");
   Request.Candidate_Base := H3;
   Request.Candidate_Delta := H7;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Delta_Mismatch,
      "delta mismatch missed");
   Request.Candidate_Delta := H4;
   Request.Candidate_Root_Set := H7;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Root_Set_Mismatch,
      "root-set mismatch missed");
   Request.Candidate_Root_Set := H5;
   Request.Actual_Staged_Root := H7;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Staged_Root_Mismatch,
      "staged-root mismatch missed");
   Request.Actual_Staged_Root := H6;
   Request.Candidate_Validation_Context := H7;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Validation_Context_Mismatch,
      "validation-context mismatch missed");
   Request.Candidate_Validation_Context := H1;
   Request.Staged_Content_Root := H7;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Staged_Untested,
      "untested staged result authorized");
   Request.Staged_Content_Root := H2;
   --  Execution-time verifier identity: a result nobody can attach to the examiner WORLDLINE
   --  authorised is not an ordinary pass, and an incomplete roster is not a satisfied one.
   Request.Execution_Evidence_Complete := False;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Execution_Evidence_Incomplete,
      "incomplete execution evidence authorized");
   Request.Execution_Evidence_Complete := True;
   Request.Actual_Executed_Verifier := H3;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Verifier_Execution_Identity_Mismatch,
      "a candidate judged by a different examiner was authorized");
   Request.Actual_Executed_Verifier := H7;
   Check
     (Worldline.Collapse.Decide (Request) = Worldline.Collapse.Authorized,
      "restoring the execution identity did not re-authorize");
   --  Checkpoint return: no candidate evaluation is consulted, and the case
   --  must carry a lineage witness rather than pass by having nothing to check.
   Request.Mode := Worldline.Collapse.Checkpoint_Return;
   Request.Execution_Evidence_Complete := False;
   Request.Candidate_Validation_Context := H7;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Checkpoint_Unwitnessed,
      "an unwitnessed checkpoint return was authorized");
   Request.Checkpoint_Witnessed := True;
   Request.Expected_Checkpoint := H3;
   Request.Witnessed_Checkpoint := H4;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Checkpoint_Unwitnessed,
      "a checkpoint witness naming other content was accepted");
   Request.Witnessed_Checkpoint := H3;
   Check
     (Worldline.Collapse.Decide (Request) = Worldline.Collapse.Authorized,
      "a witnessed checkpoint return was denied");
   Request.Staged_Content_Root := H7;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Staged_Untested,
      "checkpoint mode skipped the tested-bytes obligation");
   Request.Staged_Content_Root := H2;
   Request.Mode := Worldline.Collapse.Candidate_Evaluation;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Validation_Context_Mismatch,
      "a checkpoint witness authorized a candidate evaluation");
   Request.Candidate_Validation_Context := H1;
   Request.Execution_Evidence_Complete := True;
   Request.Checkpoint_Witnessed := False;
   Request.Has_Conflicts := True;
   Check
     (Worldline.Collapse.Decide (Request) = Worldline.Collapse.Conflict,
      "conflict missed");
   Request.Has_Conflicts := False;
   Request.Has_Foreign_Managed_Writes := True;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Foreign_Managed_Write,
      "foreign write missed");

   --  C boundary: every Boolean byte is 0 or 1, every reserved byte is 0.
   C_Request := (Candidate_State => 2, others => <>);
   C_Request.Has_Conflicts := 0;
   C_Request.Has_Foreign_Managed_Writes := 0;
   C_Request.Reserved := 0;
   C_Request.Execution_Evidence_Complete := 1;
   C_Request.Reserved_2 := 0;
   C_Request.Reserved_3 := 0;
   C_Request.Reserved_4 := 0;
   C_Request.Evaluation_Mode := 0;
   C_Request.Checkpoint_Witnessed := 0;
   C_Request.Reserved_5 := 0;
   C_Request.Reserved_6 := 0;
   C_Request.Expected_Parent := [others => 1];
   C_Request.Candidate_Parent := [others => 1];
   C_Request.Expected_Owner := [others => 1];
   C_Request.Candidate_Owner := [others => 1];
   C_Request.Expected_Base := [others => 1];
   C_Request.Candidate_Base := [others => 1];
   C_Request.Expected_Delta := [others => 1];
   C_Request.Candidate_Delta := [others => 1];
   C_Request.Expected_Root_Set := [others => 1];
   C_Request.Candidate_Root_Set := [others => 1];
   C_Request.Expected_Staged_Root := [others => 1];
   C_Request.Actual_Staged_Root := [others => 1];
   C_Request.Expected_Validation_Context := [others => 1];
   C_Request.Candidate_Validation_Context := [others => 1];
   C_Request.Tested_Root := [others => 1];
   C_Request.Staged_Content_Root := [others => 1];
   C_Request.Expected_Executed_Verifier := [others => 1];
   C_Request.Actual_Executed_Verifier := [others => 1];
   C_Request.Expected_Checkpoint := [others => 0];
   C_Request.Witnessed_Checkpoint := [others => 0];
   Check
     (Worldline.C_API.Collapse_Decide (C_Request'Unchecked_Access) = 0,
      "valid C collapse request denied");
   for Field in 1 .. 8 loop
      declare
         Bad : aliased Worldline.C_API.C_Collapse_Request := C_Request;
      begin
         case Field is
            when 1 => Bad.Execution_Evidence_Complete := 2;
            when 2 => Bad.Reserved_2 := 1;
            when 3 => Bad.Reserved_3 := 1;
            when 4 => Bad.Reserved_4 := 1;
            when 5 => Bad.Reserved_5 := 1;
            when 6 => Bad.Reserved_6 := 1;
            when 7 => Bad.Evaluation_Mode := 2;
            when others => Bad.Checkpoint_Witnessed := 2;
         end case;
         Check
           (Worldline.C_API.Collapse_Decide (Bad'Unchecked_Access) = 255,
            "malformed C collapse byte accepted");
      end;
   end loop;

   Linked := Worldline.Causal_Graph.Link (H0, H1);
   Worldline.Causal_Graph.Append (Causal, H0, H1);
   Check
     (Worldline.Causal_Graph.Accepted (Causal)
      and then Worldline.Causal_Graph.Head (Causal) = Linked,
      "valid causal link rejected");
   Worldline.Causal_Graph.Append (Causal, H7, H2);
   Check
     (not Worldline.Causal_Graph.Accepted (Causal),
      "causal predecessor mismatch accepted");
   Worldline.Causal_Graph.Append (Causal, Linked, H2);
   Check
     (not Worldline.Causal_Graph.Accepted (Causal),
      "causal rejection unstuck");

   Linked := Worldline.Receipts.Link (H0, H1);
   Worldline.Receipts.Append (Receipt, H0, H1);
   Check
     (Worldline.Receipts.Accepted (Receipt)
      and then Worldline.Receipts.Head (Receipt) = Linked,
      "valid receipt link rejected");
   Worldline.Receipts.Append (Receipt, H7, H2);
   Check
     (not Worldline.Receipts.Accepted (Receipt),
      "receipt predecessor mismatch accepted");
   Worldline.Receipts.Append (Receipt, Linked, H2);
   Check
     (not Worldline.Receipts.Accepted (Receipt),
      "receipt rejection unstuck");

   Ada.Text_IO.Put_Line ("worldline_core_tests: PASS");
end Worldline_Core_Tests;
