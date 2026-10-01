package body Evaluation_Completion with SPARK_Mode is
   function Results_Valid
     (A : Bytes; Rows : Result_Array; Binding : Attempt_Binding) return Boolean
   is
   begin
      if not Valid_Binding (A, Binding) then
         return False;
      end if;
      for I in Rows'Range loop
         if not Valid_Result (A, Rows (I)) or else
           not Same_Binding (A, Rows (I).Binding, Binding)
         then
            return False;
         end if;
         pragma Loop_Invariant
           (for all J in Rows'First .. I =>
              Valid_Result (A, Rows (J)) and then
              Same_Binding (A, Rows (J).Binding, Binding));
      end loop;
      return True;
   end Results_Valid;

   function Same_Results (A : Bytes; L, R : Result_Array) return Boolean is
   begin
      if L'Length /= R'Length then
         return False;
      end if;
      for I in L'Range loop
         if not Same_Result (A, L (I), R (R'First + (I - L'First))) then
            return False;
         end if;
         pragma Loop_Invariant
           (for all J in L'First .. I =>
              Same_Result (A, L (J), R (R'First + (J - L'First))));
      end loop;
      return True;
   end Same_Results;

   function Find_Run (A : Bytes; Journal : R.Journal; Run : Run_Identity)
      return Count is
   begin
      for I in Journal'Range loop
         if P.Same (A, Journal (I).Base.Run, Span (Run)) then
            return I;
         end if;
         pragma Loop_Invariant
           (for all K in Journal'First .. I =>
              not P.Same (A, Journal (K).Base.Run, Span (Run)));
      end loop;
      return 0;
   end Find_Run;

   function Decide
     (A : Bytes; Journal : R.Journal; Current : Cursor;
      Capture : Terminal_Record; Captured_Results : Result_Array;
      Retained : Optional_Terminal; Retained_Results : Result_Array)
      return Decision
   is
      Selected : Count;
   begin
      if not Valid_Cursor (A, Current) or else not Valid_Terminal (A, Capture) then
         return Input_Invalid;
      elsif not R.Journal_Valid
        (A, Journal, Span (Capture.Binding.Store),
         Span (Capture.Binding.Subject), Span (Capture.Binding.Content))
      then
         return Pending_Journal_Invalid;
      elsif not Current_Matches_Head (A, Journal, Current) then
         return Cursor_Mismatch;
      end if;
      Selected := Find_Run (A, Journal, Capture.Binding.Run);
      if Selected = 0 then
         return Run_Absent;
      elsif Journal (Selected).Base.State /= P.Linked then
         return Pending_Not_Linked;
      elsif not Same_Binding
        (A, Capture.Binding, Intent_Binding (Journal (Selected)))
      then
         return Capture_Binding_Mismatch;
      elsif not Results_Valid (A, Captured_Results, Capture.Binding) then
         return Capture_Results_Invalid;
      elsif not Retained.Present then
         if Retained_Results'Length /= 0 then
            return Retained_Record_Invalid;
         end if;
         return Retain_Terminal;
      elsif not Valid_Terminal (A, Retained.Value)
        or else not Results_Valid (A, Retained_Results, Retained.Value.Binding)
      then
         return Retained_Record_Invalid;
      elsif not Same_Binding (A, Retained.Value.Binding, Capture.Binding) then
         return Retained_Binding_Mismatch;
      elsif Same_Terminal (A, Capture, Retained.Value)
        and then Same_Results (A, Captured_Results, Retained_Results)
      then
         return Already_Retained;
      else
         return Terminal_Conflict;
      end if;
   end Decide;

   function Project (A : Bytes; T : Terminal_Record)
      return Optional_History_Record
   is
   begin
      if not Valid_Terminal (A, T) then
         return (Present => False);
      end if;
      return (Present => True, Value =>
        (Subject => (True, H.Subject_Id'(First => T.Binding.Subject.First,
                             Length => T.Binding.Subject.Length)),
         Content => (True, H.Content_Id'(First => T.Binding.Content.First,
                             Length => T.Binding.Content.Length)),
         Requirement =>
           (if T.Binding.Requirement.Present then
              (True, H.Requirement_Id'(First => T.Binding.Requirement.Value.First,
                             Length => T.Binding.Requirement.Value.Length))
            else (Present => False)),
         Run => (True, H.Evaluation_Id'(First => T.Binding.Run.First,
                             Length => T.Binding.Run.Length)),
         Sequence => (True, H.Epoch_Id'(First => T.Binding.Sequence.First,
                             Length => T.Binding.Sequence.Length)),
         State => (if T.State = E.Completed then H.Completed else H.Error),
         Outcome => (if T.Outcome = E.Passed then H.Passed
                     elsif T.Outcome = E.Failed then H.Failed
                     else H.No_Verdict)));
   end Project;
   procedure Apply
     (A : Bytes; Journal : R.Journal; Current : Cursor;
      Capture : Terminal_Record; Captured_Results : Result_Array;
      Retained : Optional_Terminal; Retained_Results : Result_Array;
      History : in out H.History; Result : out Decision)
   is
      Selected : Count;
      Position : Count;
   begin
      Result := Decide (A, Journal, Current, Capture, Captured_Results,
                        Retained, Retained_Results);
      if Result not in Retain_Terminal | Already_Retained then
         return;
      elsif not History_Reference (A, Journal, History) then
         Result := History_Invalid;
         return;
      end if;
      Selected := Find_Run (A, Journal, Capture.Binding.Run);
      Position := History_Index (Journal, History, Selected);
      if Position = 0 then
         Result := History_Invalid;
         return;
      elsif not Retained_Summary_Matches (A, History (Position), Retained) then
         Result := History_Conflict;
         return;
      end if;
      if Result = Retain_Terminal then
         declare
            Summary : constant Optional_History_Record := Project (A, Capture);
         begin
            pragma Assert (Summary.Present);
            History (Position) := Summary.Value;
         end;
      end if;
   end Apply;
end Evaluation_Completion;
