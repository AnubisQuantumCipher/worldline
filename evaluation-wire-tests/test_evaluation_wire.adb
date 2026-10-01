with Ada.Text_IO;
with Worldline.Evaluation_Wire;
with Evaluation_Raw_Roster;

procedure Test_Evaluation_Wire is
   package W renames Worldline.Evaluation_Wire;
   package E renames W.E;
   package R renames Evaluation_Raw_Roster;
   package T renames R.T;
   use type W.Byte;
   use type E.Execution_State;
   use type E.Outcome;
   use type E.Report_Integrity;
   use type E.Bundle_Integrity;
   use type T.Count;
   use type R.Classification;

   procedure Check (Value : Boolean; Name : String) is
   begin
      if not Value then raise Program_Error with Name; end if;
      Ada.Text_IO.Put_Line (Name);
   end Check;
   function Engine_Pass return W.Raw_Record is
      Raw : W.Raw_Record := W.Zero_Record;
   begin
      Raw.Observations (W.Source_Field) := E.Origin'Pos (E.Engine);
      Raw.Observations (W.Status_Field) := E.Raw_Status'Pos (E.Pass_Status);
      Raw.Presence := (others => 1);
      return Raw;
   end Engine_Pass;
   function External_Pass return W.Raw_Record is
      Raw : W.Raw_Record := Engine_Pass;
   begin
      Raw.Observations (W.Source_Field) := E.Origin'Pos (E.External);
      Raw.Observations (W.Channel_Field) := E.Channel_State'Pos (E.Accepted_Channel);
      Raw.Observations (W.Exit_Present_Field) := 1;
      Raw.Observations (W.Exit_Integer_Field) := 1;
      Raw.Observations (W.Supervisor_Field) := E.Supervision_State'Pos (E.Supervised);
      Raw.Observations (W.Isolation_Field) := E.Examiner_Isolation'Pos (E.Separate_Principal);
      Raw.Observations (W.Bundle_Present_Field) := 1;
      Raw.Observations (W.Bundle_Is_Mapping_Field) := 1;
      Raw.Observations (W.Bundle_Stable_Field) := 1;
      Raw.Report_Based := 1;
      Raw.Report_Facts := (others => 1);
      return Raw;
   end External_Pass;
   Raw : W.Raw_Record;
   Empty : W.Raw_Array (2 .. 1);
   Bounded : W.Raw_Roster := (0, 0, 1, Engine_Pass, (others => W.Zero_Record));
   Arena : T.Bytes (1 .. 512) := (others => 0); -- TEST_ONLY owned fixture arena.
   Next : T.Index := Arena'First;
   function Add (Text : String) return T.Span is
      First : constant T.Index := Next;
   begin
      for C of Text loop
         Arena (Next) := T.P.Byte (Character'Pos (C));
         Next := Next + 1;
      end loop;
      return (First, T.Count (Text'Length));
   end Add;
   Store : constant T.Span := Add ("store");
   Subject : constant T.Span := Add ("subject");
   Content : constant T.Span := Add ("content");
   Run_A : constant T.Span := Add ("run-a");
   Run_B : constant T.Span := Add ("run-b");
   Req_A : constant T.Span := Add ("requirement-a");
   Req_B : constant T.Span := Add ("requirement-b");
   Check_Id : constant T.Span := Add ("check");
   Other_Id : constant T.Span := Add ("unrelated");
   Completion_Id : constant T.Span := Add ("evaluation-complete");
   Declared : constant T.Span := Add ("declaration");
   Root : constant T.Span := Add ("observed-root");
   Source : constant T.Span := Add ("external");
   Engine_Source : constant T.Span := Add ("engine");
   Epoch_A : constant T.Span := Add (String'(1 => Character'Val (1)));
   Epoch_B : constant T.Span := Add (String'(1 => Character'Val (2)));
   Binding : T.Attempt_Binding :=
     (T.Store_Identity (Store), T.Subject_Identity (Subject), T.Content_Identity (Content),
      T.Run_Identity (Run_A), T.Epoch (Epoch_A),
      (Present => True, Value => T.Requirement_Identity (Req_A)));
   Context : R.Context_Measurement :=
     (Binding, T.Captured_Bytes (Root), T.Captured_Bytes (Root));
   Required : R.Check_Array (1 .. 1) :=
     (1 => (T.Check_Identity (Check_Id), T.Captured_Bytes (Declared)));
   Completion : constant R.Required_Check :=
     (T.Check_Identity (Completion_Id), T.Captured_Bytes (Declared));
   function Result_Row (Is_Completion, Passed : Boolean) return R.Measured_Result is
      Value : W.Raw_Record := (if Is_Completion then Engine_Pass else External_Pass);
   begin
      if not Passed then Value.Observations (W.Status_Field) := E.Raw_Status'Pos (E.Fail_Status); end if;
      return (Item =>
        (Binding => Binding,
         Check => T.Check_Identity ((if Is_Completion then Completion_Id else Check_Id)),
         Source => T.Source_Identity ((if Is_Completion then Engine_Source else Source)),
         Execution => (Present => False), Verifier => (Present => False),
         State => T.E.Completed,
         Outcome => (if Passed then T.E.Passed else T.E.Failed),
         Payload => T.Captured_Bytes'(1, 0)),
        Raw => Value, Confinement => E.Confinement_Observation'Pos (E.F.Confinement_Established),
        Declared => T.Captured_Bytes (Declared));
   end Result_Row;
   Rows : R.Measured_Array (1 .. 5);
   History : R.Captured_History (1 .. 2);
   Current : T.Attempt_Binding;
begin
   Check (E.Report_Integrity_Of
     (False, (E.Unclassified, E.No_Outcome, E.Unbound), (others => False)) = E.Not_Applicable,
     "literal D26 non-report input preserves Not_Applicable");
   Check (E.Report_Integrity_Of
     (True, (E.Completed, E.No_Outcome, E.Verified), (others => True)) = E.Verified_Report,
     "literal D26 report integrity does not invent or constrain outcome");
   Check (W.Admit_Wire (W.Zero_Record) = 0, "missing fields do not manufacture admission");
   Check (W.Admit_Wire (Engine_Pass) = 1, "engine completion record admitted from raw facts");
   Check (W.Admit_Wire (External_Pass) = 1, "complete external report admitted");
   Raw := External_Pass;
   Raw.Observations (W.Isolation_Field) := E.Examiner_Isolation'Pos (E.Shared_Process);
   Check (W.Classify_Wire (Raw).Execution = E.Execution_State'Pos (E.Evaluator_Incomplete), "shared examiner incomplete");
   Raw := External_Pass;
   Raw.Observations (W.Unsatisfied_Imports_Field) := 1;
   Check (W.Classify_Wire (Raw).Execution = E.Execution_State'Pos (E.Evaluator_Incomplete), "external PASS import gap incomplete");
   Raw := External_Pass;
   Raw.Observations (W.Supervisor_Stopped_Field) := 1;
   Check (W.Classify_Wire (Raw).Execution = E.Execution_State'Pos (E.Interrupted), "stopped external interrupted");
   Raw := External_Pass;
   Raw.Observations (W.Supervisor_Field) := E.Supervision_State'Pos (E.No_Supervision);
   Check (W.Classify_Wire (Raw).Execution = E.Execution_State'Pos (E.Incomplete_Unknown), "external missing supervision unknown");
   Raw := External_Pass;
   Raw.Observations (W.Bundle_Present_Field) := 0;
   Raw.Observations (W.Bundle_Is_Mapping_Field) := 0;
   Raw.Observations (W.Bundle_Stable_Field) := 0;
   Check (W.Classify_Wire (Raw).Bundle = E.Bundle_Integrity'Pos (E.Unbound) and then W.Admit_Wire (Raw) = 0, "external absent bundle unbound refusal");
   Raw := External_Pass;
   Raw.Observations (W.Exit_Present_Field) := 0;
   Check (W.Admit_Wire (Raw) = W.Invalid_Record, "dependent exit facts malformed");
   Raw := External_Pass;
   Raw.Presence (W.Binding_Established_Field) := 0;
   Check (W.Admit_Wire (Raw) = 0, "binding absence refuses");
   for F in W.R.Fact_Index loop
      Raw := External_Pass;
      Raw.Report_Facts (F) := 0;
      Check (W.Admit_Wire (Raw) = 0, "each named report fact required: " & F'Image);
   end loop;
   Raw := External_Pass;
   Raw.Observations (W.Source_Field) := W.Invalid_Record;
   Check (W.Classify_Wire (Raw).Status = W.Invalid_Record, "unknown source byte refused");
   Check (W.Confined_Admit_Wire (External_Pass, 0) = 0, "audit true with confinement absent refuses stronger claim");
   Check (W.Roster_Wire (Empty, 1, Engine_Pass) = 1, "declared empty roster with engine completion");
   Check (W.Roster_Wire (Empty, 0, Engine_Pass) = 0, "undeclared empty roster refuses");
   Check (W.Roster_Wire (Empty, 1, W.Zero_Record) = 0, "empty roster without completion refuses");
   Check (W.Roster_Wire (Bounded) = 1, "bounded D30 empty transport");
   Bounded.Rows (W.Slot'Last) := Engine_Pass;
   Check (W.Roster_Wire (Bounded) = W.Invalid_Record, "nonzero unused storage refused");

   Rows (1) := Result_Row (False, False);
   Rows (2) := Result_Row (False, True);
   Rows (3) := Result_Row (True, True);
   Check (R.Classify (Arena, Binding, Rows (1 .. 3), Required, R.Old.Required_Checks, Context, Completion) =
       (E.Completed, E.Failed, False), "required FAIL survives later duplicate PASS");
   Rows (1).Item.State := T.E.Incomplete_Unknown;
   Rows (1).Item.Outcome := T.E.No_Outcome;
   Check (R.Classify (Arena, Binding, Rows (1 .. 3), Required, R.Old.Required_Checks, Context, Completion).Outcome = E.Failed,
     "carried incomplete summary cannot erase raw completed failure");
   Rows (1).Item.State := T.E.Completed;
   Rows (1).Item.Outcome := T.E.Failed;
   Rows (2).Raw.Presence (W.Record_Identified_Field) := 0;
   Check (R.Classify (Arena, Binding, Rows (1 .. 3), Required, R.Old.Required_Checks, Context, Completion).Outcome = E.Failed,
     "unadmitted sibling does not erase genuine failure");
   Rows (3).Raw := W.Zero_Record;
   Check (R.Classify (Arena, Binding, Rows (1 .. 3), Required, R.Old.Required_Checks, Context, Completion).State = E.Incomplete_Unknown,
     "raw failure without admitted final completion stays incomplete");
   Rows (3) := Result_Row (True, True);
   Rows (2) := Result_Row (False, True);
   Rows (1).Item.Check := T.Check_Identity (Other_Id);
   Check (R.Classify (Arena, Binding, Rows (1 .. 3), Required, R.Old.Required_Checks, Context, Completion).Outcome = E.Passed,
     "unrelated failure retained without required failure latch");
   Rows (1).Item.Check := T.Check_Identity (Check_Id);
   History (1) := (Binding, (1, 3), R.Check_Span'(1, 1), R.Old.Required_Checks, Context, Completion);
   Binding.Run := T.Run_Identity (Run_B);
   Binding.Sequence := T.Epoch (Epoch_B);
   Context.Binding := Binding;
   Rows (4) := Result_Row (False, True);
   Rows (5) := Result_Row (True, True);
   History (2) := (Binding, (4, 2), R.Check_Span'(1, 1), R.Old.Required_Checks, Context, Completion);
   Current := Binding;
   Check (R.Any_Completed_Failure (Arena, Rows, Required, History, Current), "earlier genuine failure survives later run PASS");
   Current.Requirement := (Present => True, Value => T.Requirement_Identity (Req_B));
   Check (not R.Any_Completed_Failure (Arena, Rows, Required, History, Current), "changed requirement is distinct without deleting prior rows");
   Current.Requirement := (Present => False);
   Check (not R.Any_Completed_Failure (Arena, Rows, Required, History, Current), "absent requirement cannot authorize failure relation");
   Ada.Text_IO.Put_Line ("ordinary raw evaluation controls complete");
end Test_Evaluation_Wire;
