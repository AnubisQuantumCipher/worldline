with Evaluation_Pending;
with Evaluation_Pending_V2;
with Evaluation_History;
with Worldline.Evaluation;

package Evaluation_Completion with SPARK_Mode is
   --  Pure terminal-retention dependency. No supplied record, cursor or source
   --  identity authenticates its own origin. No decision here permits effects
   --  or promotion. The protected capture/durable-commit producers remain open.
   package P renames Evaluation_Pending;
   package H renames Evaluation_History;
   package R renames Evaluation_Pending_V2;
   package E renames Worldline.Evaluation;
   use type P.Count;
   use type P.Link_State;
   use type E.Execution_State;
   use type E.Outcome;
   use type H.Lifecycle;
   use type H.Verdict;
   use type H.Evaluation_Record;
   use type H.History;
   subtype Count is P.Count;
   subtype Index is P.Index;
   subtype Bytes is P.Bytes;
   subtype Span is P.Span;

   --  Full byte identities, with explicit domains and no digest compression.
   type Store_Identity is new Span;
   type Subject_Identity is new Span;
   type Content_Identity is new Span;
   subtype Requirement_Identity is R.Requirement_Id;
   type Run_Identity is new Span;
   type Source_Identity is new Span;
   type Check_Identity is new Span;
   type Execution_Identity is new Span;
   type Verifier_Identity is new Span;
   type Epoch is new Span;
   type Captured_Bytes is new Span;

   subtype Optional_Requirement is R.Optional_Requirement;
   type Optional_Execution (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : Execution_Identity;
      end case;
   end record;
   type Optional_Verifier (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : Verifier_Identity;
      end case;
   end record;

   type Attempt_Binding is record
      Store       : Store_Identity;
      Subject     : Subject_Identity;
      Content     : Content_Identity;
      Run         : Run_Identity;
      Sequence    : Epoch;
      Requirement : Optional_Requirement;
   end record;
   type Cursor (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True =>
            Run : Run_Identity;
            Sequence : Epoch;
      end case;
   end record;
   --  Capture records retain category, optional-field presence and full bytes.
   --  Absence is never upgraded to a verifier/execution identity. In-process
   --  checks and incomplete observations are representable without inventions.
   type Result_Record is record
      Binding   : Attempt_Binding;
      Check     : Check_Identity;
      Source    : Source_Identity;
      Execution : Optional_Execution;
      Verifier  : Optional_Verifier;
      State     : E.Execution_State;
      Outcome   : E.Outcome;
      Payload   : Captured_Bytes;
   end record;
   type Result_Array is array (Index range <>) of Result_Record;
   type Terminal_Record is record
      Binding : Attempt_Binding;
      Source  : Source_Identity;
      Context : Captured_Bytes;
      State   : E.Terminal_State;
      Outcome : E.Outcome;
   end record;
   type Optional_Terminal (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : Terminal_Record;
      end case;
   end record;

   function Valid_Binding (A : Bytes; B : Attempt_Binding) return Boolean is
     (P.Valid (A, Span (B.Store)) and then P.Valid (A, Span (B.Subject))
      and then P.Valid (A, Span (B.Content)) and then P.Valid (A, Span (B.Run))
      and then P.Valid (A, Span (B.Sequence))
      and then (not B.Requirement.Present or else
                  P.Valid (A, Span (B.Requirement.Value))))
     with Global => null;
   function Same_Requirement
     (A : Bytes; L, R : Optional_Requirement) return Boolean is
     (L.Present = R.Present and then
        (not L.Present or else
           P.Same (A, Span (L.Value), Span (R.Value))))
     with Global => null;
   function Same_Binding (A : Bytes; L, R : Attempt_Binding) return Boolean is
     (Valid_Binding (A, L) and then Valid_Binding (A, R)
      and then P.Same (A, Span (L.Store), Span (R.Store))
      and then P.Same (A, Span (L.Subject), Span (R.Subject))
      and then P.Same (A, Span (L.Content), Span (R.Content))
      and then P.Same (A, Span (L.Run), Span (R.Run))
      and then P.Epoch_Same (A, Span (L.Sequence), Span (R.Sequence))
      and then Same_Requirement (A, L.Requirement, R.Requirement))
     with Global => null;
   function Valid_Cursor (A : Bytes; C : Cursor) return Boolean is
     (not C.Present or else
        (P.Valid (A, Span (C.Run)) and then P.Valid (A, Span (C.Sequence))))
     with Global => null;
   function Cursor_Matches
     (A : Bytes; C : Cursor; B : Attempt_Binding) return Boolean is
     (C.Present and then Valid_Cursor (A, C) and then Valid_Binding (A, B)
      and then P.Same (A, Span (C.Run), Span (B.Run))
      and then P.Epoch_Same (A, Span (C.Sequence), Span (B.Sequence)))
     with Global => null;

   function Intent_Binding (I : R.Intent) return Attempt_Binding is
     (Store_Identity (I.Base.Store_Id), Subject_Identity (I.Base.Subject),
      Content_Identity (I.Base.Content), Run_Identity (I.Base.Run),
      Epoch (I.Base.Sequence), I.Requirement) with Global => null;
   function Find_Run (A : Bytes; Journal : R.Journal; Run : Run_Identity)
      return Count
     with Global => null,
          Post => Find_Run'Result =
            P.Run_Index (A, R.Base_Of (Journal), Span (Run));
   function Current_Matches_Head
     (A : Bytes; Journal : R.Journal; Current : Cursor) return Boolean is
     (P.Same_Cursor
       (A, (if Current.Present then
              (True, Span (Current.Sequence), Span (Current.Run))
            else (Present => False)), P.Head (R.Base_Of (Journal))))
     with Global => null;

   function Valid_Result (A : Bytes; R : Result_Record) return Boolean is
     (Valid_Binding (A, R.Binding)
      and then P.Valid (A, Span (R.Check))
      and then P.Valid (A, Span (R.Source))
      and then P.Valid (A, Span (R.Payload))
      and then (not R.Execution.Present or else
                  P.Valid (A, Span (R.Execution.Value)))
      and then (not R.Verifier.Present or else
                  P.Valid (A, Span (R.Verifier.Value)))
      and then ((R.State = E.Completed) = (R.Outcome /= E.No_Outcome)))
     with Global => null;
   function Valid_Terminal (A : Bytes; T : Terminal_Record) return Boolean is
     (Valid_Binding (A, T.Binding)
      and then P.Valid (A, Span (T.Source))
      and then P.Valid (A, Span (T.Context))
      and then ((T.State = E.Completed) = (T.Outcome /= E.No_Outcome))
      and then (T.State /= E.Completed or else T.Binding.Requirement.Present))
     with Global => null;
   function Same_Execution
     (A : Bytes; L, R : Optional_Execution) return Boolean is
     (L.Present = R.Present and then
        (not L.Present or else P.Same (A, Span (L.Value), Span (R.Value))))
     with Global => null;
   function Same_Verifier
     (A : Bytes; L, R : Optional_Verifier) return Boolean is
     (L.Present = R.Present and then
        (not L.Present or else P.Same (A, Span (L.Value), Span (R.Value))))
     with Global => null;
   function Same_Result (A : Bytes; L, R : Result_Record) return Boolean is
     (Valid_Result (A, L) and then Valid_Result (A, R)
      and then Same_Binding (A, L.Binding, R.Binding)
      and then P.Same (A, Span (L.Check), Span (R.Check))
      and then P.Same (A, Span (L.Source), Span (R.Source))
      and then Same_Execution (A, L.Execution, R.Execution)
      and then Same_Verifier (A, L.Verifier, R.Verifier)
      and then L.State = R.State and then L.Outcome = R.Outcome
      and then P.Same (A, Span (L.Payload), Span (R.Payload)))
     with Global => null;
   function Same_Terminal (A : Bytes; L, R : Terminal_Record) return Boolean is
     (Valid_Terminal (A, L) and then Valid_Terminal (A, R)
      and then Same_Binding (A, L.Binding, R.Binding)
      and then P.Same (A, Span (L.Source), Span (R.Source))
      and then P.Same (A, Span (L.Context), Span (R.Context))
      and then L.State = R.State and then L.Outcome = R.Outcome)
     with Global => null;

   --  Independent closed whole-array equations. All positions are retained,
   --  including optional, incomplete, unclassified and duplicate check names.
   --  No roster admission semantics are inferred from capture membership.
   function Results_Reference
     (A : Bytes; Rows : Result_Array; Binding : Attempt_Binding) return Boolean is
     (Valid_Binding (A, Binding) and then
        (for all I in Rows'Range =>
           Valid_Result (A, Rows (I)) and then
           Same_Binding (A, Rows (I).Binding, Binding)))
     with Global => null;
   function Same_Results_Reference
     (A : Bytes; L, R : Result_Array) return Boolean is
     (L'Length = R'Length and then
        (for all I in L'Range =>
           Same_Result (A, L (I), R (R'First + (I - L'First)))))
     with Global => null;
   function Results_Valid
     (A : Bytes; Rows : Result_Array; Binding : Attempt_Binding) return Boolean
     with Global => null,
          Post => Results_Valid'Result = Results_Reference (A, Rows, Binding);
   function Same_Results (A : Bytes; L, R : Result_Array) return Boolean
     with Global => null,
          Post => Same_Results'Result = Same_Results_Reference (A, L, R);

   type Decision is
     (Input_Invalid, Pending_Journal_Invalid, Pending_Not_Linked,
      Cursor_Mismatch, Run_Absent, Capture_Binding_Mismatch,
      Capture_Results_Invalid, Retained_Record_Invalid,
      Retained_Binding_Mismatch, Terminal_Conflict, Retain_Terminal,
      Already_Retained, History_Invalid, History_Conflict);

   function Reference
     (A : Bytes; Journal : R.Journal; Current : Cursor;
      Capture : Terminal_Record; Captured_Results : Result_Array;
      Retained : Optional_Terminal; Retained_Results : Result_Array)
      return Decision is
     (if not Valid_Cursor (A, Current) or else not Valid_Terminal (A, Capture)
      then Input_Invalid
      elsif not R.Journal_Valid
        (A, Journal, Span (Capture.Binding.Store),
         Span (Capture.Binding.Subject), Span (Capture.Binding.Content))
      then Pending_Journal_Invalid
      elsif not Current_Matches_Head (A, Journal, Current) then Cursor_Mismatch
      elsif Find_Run (A, Journal, Capture.Binding.Run) = 0 then Run_Absent
      elsif Journal (Find_Run (A, Journal, Capture.Binding.Run)).Base.State /= P.Linked
      then Pending_Not_Linked
      elsif not Same_Binding (A, Capture.Binding,
        Intent_Binding (Journal (Find_Run (A, Journal, Capture.Binding.Run))))
      then Capture_Binding_Mismatch
      elsif not Results_Reference (A, Captured_Results, Capture.Binding)
      then Capture_Results_Invalid
      elsif not Retained.Present then
         (if Retained_Results'Length /= 0 then Retained_Record_Invalid
          else Retain_Terminal)
      elsif not Valid_Terminal (A, Retained.Value)
         or else not Results_Reference (A, Retained_Results, Retained.Value.Binding)
      then Retained_Record_Invalid
      elsif not Same_Binding (A, Retained.Value.Binding, Capture.Binding)
      then Retained_Binding_Mismatch
      elsif Same_Terminal (A, Capture, Retained.Value)
         and then Same_Results_Reference (A, Captured_Results, Retained_Results)
      then Already_Retained else Terminal_Conflict)
     with Global => null;

   function Decide
     (A : Bytes; Journal : R.Journal; Current : Cursor;
      Capture : Terminal_Record; Captured_Results : Result_Array;
      Retained : Optional_Terminal; Retained_Results : Result_Array)
      return Decision
     with Global => null,
          Post => Decide'Result = Reference
            (A, Journal, Current, Capture, Captured_Results,
             Retained, Retained_Results);

   --  Actual summary construction for the existing history consumer. The
   --  complete record and ordered result payload still require atomic durable
   --  retention; this lossy summary is never their replacement or provenance.
   type Optional_History_Record (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : H.Evaluation_Record;
      end case;
   end record;
   function Project_Reference (A : Bytes; T : Terminal_Record)
      return Optional_History_Record is
     (if not Valid_Terminal (A, T) then (Present => False)
      else (Present => True, Value =>
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
                     else H.No_Verdict))))
     with Global => null;
   function Project (A : Bytes; T : Terminal_Record)
      return Optional_History_Record
     with Global => null,
          Post => Project'Result = Project_Reference (A, T);
   function From_History (S : H.Identity_Span) return Span is
     (S.First, S.Length) with Global => null;
   function History_Binding_Matches
     (A : Bytes; Row : H.Evaluation_Record; B : Attempt_Binding) return Boolean is
     (Valid_Binding (A, B)
      and then Row.Subject.Present and then Row.Content.Present
      and then Row.Run.Present and then Row.Sequence.Present
      and then P.Same (A, From_History (H.Identity_Span (Row.Subject.Value)), Span (B.Subject))
      and then P.Same (A, From_History (H.Identity_Span (Row.Content.Value)), Span (B.Content))
      and then P.Same (A, From_History (H.Identity_Span (Row.Run.Value)), Span (B.Run))
      and then P.Epoch_Same (A, From_History (H.Identity_Span (Row.Sequence.Value)), Span (B.Sequence))
      and then Row.Requirement.Present = B.Requirement.Present
      and then (not Row.Requirement.Present or else
        P.Same (A, From_History (H.Identity_Span (Row.Requirement.Value)),
                Span (B.Requirement.Value)))) with Global => null;
   function History_Row_Conforms
     (A : Bytes; I : R.Intent; Row : H.Evaluation_Record) return Boolean is
     (History_Binding_Matches (A, Row, Intent_Binding (I))
      and then ((Row.State = H.Completed) = (Row.Outcome /= H.No_Verdict))
      and then (Row.State /= H.Completed or else Row.Requirement.Present)
      and then (I.Base.State = P.Linked or else Row.State = H.Pending))
     with Global => null;
   function History_Reference
     (A : Bytes; Journal : R.Journal; History : H.History) return Boolean is
     (Journal'Length = History'Length and then
       (for all I in Journal'Range =>
         History_Row_Conforms
           (A, Journal (I), History (History'First + (I - Journal'First)))))
     with Global => null;
   function History_Index
     (Journal : R.Journal; History : H.History; Selected : Count) return Count is
     (if Journal'Length /= History'Length or else Selected not in Journal'Range
      then 0 else History'First + (Selected - Journal'First))
     with Global => null,
       Post => (if History_Index'Result /= 0 then
                  History_Index'Result in History'Range);
   function Retained_Summary_Matches
     (A : Bytes; Row : H.Evaluation_Record; Retained : Optional_Terminal)
      return Boolean is
     (if not Retained.Present then Row.State = H.Pending and Row.Outcome = H.No_Verdict
      else Valid_Terminal (A, Retained.Value)
        and then History_Binding_Matches (A, Row, Retained.Value.Binding)
        and then Project_Reference (A, Retained.Value).Present
        and then Row.State = Project_Reference (A, Retained.Value).Value.State
        and then Row.Outcome = Project_Reference (A, Retained.Value).Value.Outcome)
     with Global => null;
   function Update_Reference
     (A : Bytes; Journal : R.Journal; Current : Cursor;
      Capture : Terminal_Record; Captured_Results : Result_Array;
      Retained : Optional_Terminal; Retained_Results : Result_Array;
      History : H.History) return Decision is
     (if Reference (A, Journal, Current, Capture, Captured_Results,
                    Retained, Retained_Results) not in Retain_Terminal | Already_Retained
      then Reference (A, Journal, Current, Capture, Captured_Results,
                      Retained, Retained_Results)
      elsif not History_Reference (A, Journal, History) then History_Invalid
      elsif History_Index (Journal, History, Find_Run (A, Journal, Capture.Binding.Run)) = 0
      then History_Invalid
      elsif not Retained_Summary_Matches
        (A, History (History_Index (Journal, History,
                     Find_Run (A, Journal, Capture.Binding.Run))), Retained)
      then History_Conflict
      else Reference (A, Journal, Current, Capture, Captured_Results,
                      Retained, Retained_Results))
     with Global => null;

   --  All supplied history is retained. Only the selected pending row can
   --  change; its run/epoch/requirement remain bound to the retained intent.
   --  Current and Journal are input-only, so completing an older run never
   --  rewrites head. Finalization remains the separate unchanged consumer input.
   procedure Apply
     (A : Bytes; Journal : R.Journal; Current : Cursor;
      Capture : Terminal_Record; Captured_Results : Result_Array;
      Retained : Optional_Terminal; Retained_Results : Result_Array;
      History : in out H.History; Result : out Decision)
     with Global => null, Always_Terminates,
          Post => Result = Update_Reference
            (A, Journal, Current, Capture, Captured_Results,
             Retained, Retained_Results, History'Old)
            and then
             (if Result = Retain_Terminal then
                Project_Reference (A, Capture).Present
                and then Find_Run (A, Journal, Capture.Binding.Run) in Journal'Range
                and then Journal'Length = History'Length
                and then (for all I in History'Range =>
                  (if I = History_Index (Journal, History,
                            Find_Run (A, Journal, Capture.Binding.Run)) then
                      History (I) = Project_Reference (A, Capture).Value
                   else History (I) = History'Old (I)))
              else History = History'Old);
end Evaluation_Completion;
