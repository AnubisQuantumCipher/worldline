with Ada.Text_IO;
with Evaluation_Completion;

--  Unexecuted ordinary typed controls. This fixture arena is TEST_ONLY, not a
--  production cap. It creates supplied records, never authenticated evidence.
procedure Test_Completion is
   use Evaluation_Completion;
   use type Count;
   use type H.Lifecycle;
   use type H.Verdict;
   use type H.Decision;
   use type H.Evaluation_Record;
   use type H.History;
   A : Bytes (1 .. 256) := (others => 0);
   Used : Count := 0;
   function Put (S : String) return Span is
      First : constant Index := Used + 1;
   begin
      for C of S loop
         Used := Used + 1;
         A (Used) := P.Byte (Character'Pos (C));
      end loop;
      return (First, Count (S'Length));
   end Put;
   Store_S : constant Span := Put ("store");
   Subject_S : constant Span := Put ("world");
   Content_S : constant Span := Put ("content");
   Run_S : constant Span := Put ("run");
   Req_S : constant Span := Put ("requirement");
   Other_Req_S : constant Span := Put ("different-requirement");
   Source_S : constant Span := Put ("capture-source");
   Check_S : constant Span := Put ("ordinary-check");
   Verifier_S : constant Span := Put ("executed-verifier");
   Other_Verifier_S : constant Span := Put ("other-verifier");
   Execution_S : constant Span := Put ("execution-run");
   Context_S : constant Span := Put ("context-bytes");
   Payload_S : constant Span := Put ("result-bytes");
   Epoch_S : constant Span := Put (String'(1 => Character'Val (1)));
   B : constant Attempt_Binding :=
     (Store_Identity (Store_S), Subject_Identity (Subject_S),
      Content_Identity (Content_S), Run_Identity (Run_S), Epoch (Epoch_S),
      (True, Requirement_Identity (Req_S)));
   Current : constant Cursor := (True, Run_Identity (Run_S), Epoch (Epoch_S));
   J : constant R.Journal (1 .. 1) :=
     (1 => (Base => (Store_S, Subject_S, Content_S, Run_S, Epoch_S,
            (Present => False), P.Linked), Requirement => B.Requirement));
   Empty_J : constant R.Journal (1 .. 0) := (others => <>);
   T : constant Terminal_Record :=
     (B, Source_Identity (Source_S), Captured_Bytes (Context_S),
      E.Completed, E.Passed);
   Result_Row : constant Result_Record :=
     (B, Check_Identity (Check_S), Source_Identity (Source_S),
      (True, Execution_Identity (Execution_S)),
      (True, Verifier_Identity (Verifier_S)), E.Completed, E.Passed,
      Captured_Bytes (Payload_S));
   Rows : constant Result_Array (1 .. 1) := (1 => Result_Row);
   Shifted : constant Result_Array (2 .. 2) := (2 => Result_Row);
   Empty_Rows : constant Result_Array (1 .. 0) := (others => <>);
   Other_Rows : Result_Array (1 .. 1) := Rows;
   Other_T : Terminal_Record := T;
   Projected : Optional_History_Record;
   procedure Expect (Label_Text : String; Actual, Expected : Decision) is
   begin
      pragma Assert (Actual = Expected);
      Ada.Text_IO.Put_Line ("PASS " & Label_Text);
   end Expect;
begin
   Expect ("retain_completed_record",
     Decide (A, J, Current, T, Rows, (Present => False), Empty_Rows),
     Retain_Terminal);
   Expect ("exact_terminal_replay",
     Decide (A, J, Current, T, Rows, (True, T), Rows), Already_Retained);
   Other_T.Outcome := E.Failed;
   Expect ("terminal_failed_record_cannot_be_replaced",
     Decide (A, J, Current, T, Rows, (True, Other_T), Rows),
     Terminal_Conflict);
   Other_Rows (1).Verifier := (True, Verifier_Identity (Other_Verifier_S));
   Expect ("different_executed_verifier_conflicts",
     Decide (A, J, Current, T, Rows, (True, T), Other_Rows),
     Terminal_Conflict);
   Other_T := T;
   Other_T.Binding.Requirement := (True, Requirement_Identity (Other_Req_S));
   Expect ("requirement_binding_is_not_defaulted",
     Decide (A, J, Current, Other_T, Rows,
             (Present => False), Empty_Rows), Capture_Binding_Mismatch);
   Expect ("absent_current_cursor_refuses",
     Decide (A, J, (Present => False), T, Rows,
             (Present => False), Empty_Rows), Cursor_Mismatch);
   Other_T := T;
   Other_T.Outcome := E.No_Outcome;
   Expect ("completed_without_verdict_is_invalid",
     Decide (A, J, Current, Other_T, Rows,
             (Present => False), Empty_Rows), Input_Invalid);
   Other_T := T;
   Other_T.Binding.Requirement := (Present => False);
   Expect ("completed_without_requirement_is_invalid",
     Decide (A, J, Current, Other_T, Rows,
             (Present => False), Empty_Rows), Input_Invalid);
   Other_T := T;
   Other_T.State := E.Interrupted;
   Other_T.Outcome := E.No_Outcome;
   Expect ("interruption_remains_no_verdict",
     Decide (A, J, Current, Other_T, Rows,
             (Present => False), Empty_Rows), Retain_Terminal);
   Projected := Project (A, Other_T);
   pragma Assert (Projected.Present and then Projected.Value.State = H.Error
                  and then Projected.Value.Outcome = H.No_Verdict);
   Ada.Text_IO.Put_Line ("PASS incomplete_history_projection");
   Projected := Project (A, T);
   pragma Assert (Projected.Present and then Projected.Value.State = H.Completed
                  and then Projected.Value.Outcome = H.Passed);
   Ada.Text_IO.Put_Line ("PASS completed_history_projection");
   Expect ("empty_capture_is_not_a_roster_admission",
     Decide (A, J, Current, T, Empty_Rows,
             (Present => False), Empty_Rows), Retain_Terminal);
   pragma Assert (Same_Results (A, Rows, Shifted));
   Ada.Text_IO.Put_Line ("PASS ordered_result_equality_ignores_array_origin");
   Other_T := T;
   Other_T.Context := (A'Last, A'Length);
   Expect ("malformed_context_span_refuses",
     Decide (A, J, Current, Other_T, Rows,
             (Present => False), Empty_Rows), Input_Invalid);
   Expect ("empty_journal_contains_no_run",
     Decide (A, Empty_J, (Present => False), T, Rows,
             (Present => False), Empty_Rows), Run_Absent);
   declare
      Later_Run : constant Span := Put ("later-run");
      --  Existing retained pending controls pin epoch successor 1 -> 2.
      Later_Epoch : constant Span := Put (String'(1 => Character'Val (2)));
      Later_Binding : Attempt_Binding := B;
      Later_Terminal : Terminal_Record := T;
      Failure : Terminal_Record := T;
      Failure_Rows : Result_Array (Rows'Range) := Rows;
      Both : R.Journal (1 .. 2);
      Full : H.History (1 .. 2);
      Before_Update : H.History (Full'Range);
      New_Current : constant Cursor :=
        (True, Run_Identity (Later_Run), Epoch (Later_Epoch));
      Update_Result : Decision;
      Query : H.Query;
      Selection : H.Selection;
   begin
      Later_Binding.Run := Run_Identity (Later_Run);
      Later_Binding.Sequence := Epoch (Later_Epoch);
      Later_Terminal.Binding := Later_Binding;
      Failure.Outcome := E.Failed;
      Failure_Rows (1).Outcome := E.Failed;
      Both (1) := J (1);
      Both (2) := (Base =>
        (Store_S, Subject_S, Content_S, Later_Run, Later_Epoch,
         (True, Epoch_S, Run_S), P.Linked), Requirement => B.Requirement);
      Full (1) := Project (A, T).Value;
      Full (1).State := H.Pending;
      Full (1).Outcome := H.No_Verdict;
      Full (2) := Project (A, Later_Terminal).Value;
      Before_Update := Full;
      Apply (A, Both, New_Current, Failure, Failure_Rows,
             (Present => False), Empty_Rows, Full, Update_Result);
      Expect ("late_failure_for_retained_run", Update_Result, Retain_Terminal);
      pragma Assert (Full (2) = Before_Update (2));
      pragma Assert (Full (1).Outcome = H.Failed);
      Ada.Text_IO.Put_Line ("PASS late_completion_preserves_newer_row_and_head");
      Query := (Full (2).Subject, Full (2).Content, Full (2).Requirement,
        (True, (Full (2).Sequence, Full (2).Run.Value)),
        (True, (Full (2).Sequence, Full (2).Run.Value)));
      Selection := H.Select_Evidence (A, Full, (Present => False), Query);
      pragma Assert (Selection.Reason = H.Evidence_Fail_Terminal);
      Ada.Text_IO.Put_Line ("PASS retained_late_fail_blocks_newer_pass_same_requirement");
      Before_Update := Full;
      Apply (A, Both, New_Current, Failure, Failure_Rows,
             (True, Failure), Failure_Rows, Full, Update_Result);
      Expect ("late_failure_duplicate_replay", Update_Result, Already_Retained);
      pragma Assert (Full = Before_Update);
      Apply (A, Both, New_Current, T, Rows,
             (True, Failure), Failure_Rows, Full, Update_Result);
      Expect ("late_failed_run_cannot_be_revived", Update_Result, Terminal_Conflict);
      pragma Assert (Full = Before_Update);
      Apply (A, Both, Current, Failure, Failure_Rows,
             (True, Failure), Failure_Rows, Full, Update_Result);
      Expect ("old_cursor_is_not_current_head", Update_Result, Cursor_Mismatch);
      pragma Assert (Full = Before_Update);
   end;
end Test_Completion;
