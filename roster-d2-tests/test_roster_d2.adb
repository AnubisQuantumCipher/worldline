with Ada.Text_IO;
with Evaluation_Completion;
with Evaluation_Completion_Roster;

--  Ordinary TEST_ONLY supplied records. Actual Classify bodies execute; no
--  record here authenticates a producer or establishes the full proof target.
procedure Test_Roster_D2 is
   package T renames Evaluation_Completion;
   package R renames Evaluation_Completion_Roster;
   package E renames T.E;
   use type T.Count;
   use type E.Execution_State;
   use type E.Outcome;
   A : T.Bytes (1 .. 256) := (others => 0);
   Used : T.Count := 0;
   function Put (S : String) return T.Span is
      First : constant T.Index := Used + 1;
   begin
      for C of S loop
         Used := Used + 1;
         A (Used) := T.P.Byte (Character'Pos (C));
      end loop;
      return (First, T.Count (S'Length));
   end Put;
   Store_S : constant T.Span := Put ("store");
   Subject_S : constant T.Span := Put ("world");
   Content_S : constant T.Span := Put ("content");
   Run_S : constant T.Span := Put ("run");
   Req_S : constant T.Span := Put ("requirement");
   Epoch_S : constant T.Span := Put (String'(1 => Character'Val (1)));
   Root_S : constant T.Span := Put ("same-measured-root");
   Source_S : constant T.Span := Put ("owned-test-input");
   Check_S : constant T.Span := Put ("required-check");
   Unrelated_S : constant T.Span := Put ("unrelated-check");
   Complete_S : constant T.Span := Put (R.Engine_Completion_Name);
   Declaration_S : constant T.Span := Put ("engine-declaration");
   Payload_S : constant T.Span := Put ("retained-input-bytes");
   Binding : constant T.Attempt_Binding :=
     (T.Store_Identity (Store_S), T.Subject_Identity (Subject_S),
      T.Content_Identity (Content_S), T.Run_Identity (Run_S), T.Epoch (Epoch_S),
      (True, T.Requirement_Identity (Req_S)));
   Context : constant R.Context_Measurement :=
     (Binding, T.Captured_Bytes (Root_S), T.Captured_Bytes (Root_S));
   Required : constant R.Check_Array (1 .. 1) :=
     (1 => (T.Check_Identity (Check_S), T.Captured_Bytes (Declaration_S)));
   Completion : constant R.Required_Check :=
     (T.Check_Identity (Complete_S), T.Captured_Bytes (Declaration_S));

   function Measured (Check : T.Span; Status : E.Raw_Status)
      return R.Measured_Result
   is
      Facts : constant E.Observations :=
        (Source => E.Engine, Status => Status, Channel => E.Absent_Channel,
         Stage => E.No_Stage, Exit_Present => False, Exit_Integer => False,
         Supervisor => E.No_Supervision, Supervisor_Stopped => False,
         Bundle_Present => False, Bundle_Is_Mapping => False,
         Bundle_Stable => False, Bundle_Changed => False,
         Unsatisfied_Imports => False);
      Classified : constant E.Classification := E.Classify (Facts);
   begin
      return
        (Item => (Binding, T.Check_Identity (Check), T.Source_Identity (Source_S),
           (Present => False), (Present => False), Classified.Execution,
           Classified.Result, T.Captured_Bytes (Payload_S)),
         Facts => Facts, Report => E.Not_Applicable,
         Presence => (Record_Identified => True, Verdict_Recorded => True,
           Binding_Established => True, Declaration_Matches => True,
           Bundle_Identified => True),
         Declared => T.Captured_Bytes (Declaration_S));
   end Measured;

   Failed_Row : constant R.Measured_Result := Measured (Check_S, E.Fail_Status);
   Passed_Row : constant R.Measured_Result := Measured (Check_S, E.Pass_Status);
   Completion_Row : constant R.Measured_Result := Measured (Complete_S, E.Pass_Status);
   Unrelated_Failure : constant R.Measured_Result := Measured (Unrelated_S, E.Fail_Status);
   Duplicated : constant R.Measured_Array (1 .. 3) :=
     (Failed_Row, Passed_Row, Completion_Row);
   Missing_Completion : constant R.Measured_Array (1 .. 2) :=
     (Failed_Row, Passed_Row);
   Nonrequired_Failure : constant R.Measured_Array (1 .. 3) :=
     (Unrelated_Failure, Passed_Row, Completion_Row);
   Only_Passed : constant R.Measured_Array (1 .. 2) :=
     (Passed_Row, Completion_Row);
   Answer : R.Classification;
begin
   pragma Assert (Failed_Row.Item.State = E.Completed);
   pragma Assert (Failed_Row.Item.Outcome = E.Failed);
   pragma Assert (Passed_Row.Item.Outcome = E.Passed);

   --  Last-row PASS policy remains separately satisfied, but D2 still wins.
   pragma Assert
     (R.Promotion_Roster (A, Binding, Duplicated, Required,
                         R.Required_Checks, Context, Completion));
   pragma Assert (R.Failure_For_Check (A, Duplicated, T.Check_Identity (Check_S)));
   Answer := R.Classify (A, Binding, Duplicated, Required,
                         R.Required_Checks, Context, Completion);
   pragma Assert (Answer.State = E.Completed and then Answer.Outcome = E.Failed
                  and then not Answer.Promotion_Ready);
   Ada.Text_IO.Put_Line ("PASS required_fail_then_duplicate_pass_with_completion");

   pragma Assert (R.Failure_For_Check (A, Missing_Completion, T.Check_Identity (Check_S)));
   pragma Assert
     (not R.Genuine_Required_Failure
       (A, Binding, Missing_Completion, Required, Context, Completion));
   Answer := R.Classify (A, Binding, Missing_Completion, Required,
                         R.Required_Checks, Context, Completion);
   pragma Assert (Answer.State = E.Incomplete_Unknown
                  and then Answer.Outcome = E.No_Outcome
                  and then not Answer.Promotion_Ready);
   Ada.Text_IO.Put_Line ("PASS missing_final_completion_retains_incomplete");

   pragma Assert
     (not R.Failure_For_Check (A, Nonrequired_Failure, T.Check_Identity (Check_S)));
   Answer := R.Classify (A, Binding, Nonrequired_Failure, Required,
                         R.Required_Checks, Context, Completion);
   pragma Assert (Answer.State = E.Completed and then Answer.Outcome = E.Passed
                  and then Answer.Promotion_Ready);
   Ada.Text_IO.Put_Line ("PASS nonrequired_fail_is_not_required_fail_latch");

   Answer := R.Classify (A, Binding, Only_Passed, Required,
                         R.Required_Checks, Context, Completion);
   pragma Assert (Answer.State = E.Completed and then Answer.Outcome = E.Passed
                  and then Answer.Promotion_Ready);
   Ada.Text_IO.Put_Line ("PASS original_required_pass_remains_admitted");
end Test_Roster_D2;
