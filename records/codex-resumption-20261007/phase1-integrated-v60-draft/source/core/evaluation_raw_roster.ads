with Evaluation_Completion;
with Evaluation_Completion_Roster;
with Worldline.Evaluation_Wire;

--  Full retained raw stream, with byte identities. These relations check the
--  supplied observations; they do not authenticate a store, capture or cursor.
package Evaluation_Raw_Roster with SPARK_Mode is
   package T renames Evaluation_Completion;
   package Old renames Evaluation_Completion_Roster;
   package W renames Worldline.Evaluation_Wire;
   package E renames W.E;
   use type T.Count;
   use type T.P.Byte;
   use type E.Execution_State;
   use type E.Outcome;
   use type E.Origin;
   use type T.E.Execution_State;
   use type T.E.Outcome;
   type Measured_Result is record
      Item : T.Result_Record;
      Raw : W.Raw_Record;
      Confinement : W.Byte;
      Declared : T.Captured_Bytes;
   end record;
   type Measured_Array is array (T.Index range <>) of Measured_Result;
   subtype Required_Check is Old.Required_Check;
   subtype Check_Array is Old.Check_Array;
   subtype Declaration is Old.Declaration;
   subtype Context_Measurement is Old.Context_Measurement;
   use type Declaration;
   type Classification is record
      State : E.Terminal_State;
      Outcome : E.Outcome;
      Promotion_Ready : Boolean;
   end record;

   function Matches_Classification (R : Measured_Result) return Boolean is
     (W.Well_Formed (R.Raw) and then
      T.E.Execution_State'Pos (R.Item.State) =
        E.Execution_State'Pos (E.Expected_Classification (W.Decode (R.Raw).Value.Facts).Execution)
      and then T.E.Outcome'Pos (R.Item.Outcome) =
        E.Outcome'Pos (E.Expected_Classification (W.Decode (R.Raw).Value.Facts).Result))
     with Global => null;
   --  A carried lifecycle/verdict is not a classification authority. Raw D2
   --  ignores that projection; promotion separately requires it to agree.
   function Row_Bound
     (A : T.Bytes; R : Measured_Result; Binding : T.Attempt_Binding) return Boolean is
     (T.Same_Binding (A, R.Item.Binding, Binding)
      and then T.P.Valid (A, T.Span (R.Item.Check))
      and then T.P.Valid (A, T.Span (R.Item.Source))
      and then T.P.Valid (A, T.Span (R.Item.Payload))
      and then (not R.Item.Execution.Present or else
        T.P.Valid (A, T.Span (R.Item.Execution.Value)))
      and then (not R.Item.Verifier.Present or else
        T.P.Valid (A, T.Span (R.Item.Verifier.Value)))
      and then T.P.Valid (A, T.Span (R.Declared))) with Global => null;

   function Required_Evidence
     (A : T.Bytes; R : Measured_Result; Required : Required_Check) return Boolean is
     (T.P.Valid (A, T.Span (Required.Check))
      and then T.P.Valid (A, T.Span (Required.Declared))
      and then T.P.Valid (A, T.Span (R.Declared))
      and then T.P.Same (A, T.Span (R.Item.Check), T.Span (Required.Check))
      and then T.P.Same (A, T.Span (R.Declared), T.Span (Required.Declared))
      and then W.Confined_Admit_Wire (R.Raw, R.Confinement) = 1)
     with Global => null;

   function Selected (A : T.Bytes; Rows : Measured_Array; Check : T.Check_Identity)
      return T.Count with Global => null,
      Post => (if Selected'Result = 0 then
        (for all J in Rows'Range => not T.P.Same (A, T.Span (Rows (J).Item.Check), T.Span (Check)))
       else Selected'Result in Rows'Range
        and then T.P.Same (A, T.Span (Rows (Selected'Result).Item.Check), T.Span (Check))
        and then (for all J in Rows'Range =>
          (if J > Selected'Result then not T.P.Same (A, T.Span (Rows (J).Item.Check), T.Span (Check)))));

   --  D15/D2: engine completion is derived from its own final RAW record.
   --  A sibling's failed promotion evidence cannot erase an admitted engine
   --  completion and genuine required failure. Full stream coherence is the
   --  distinct promotion gate below; no row is discarded or rewritten.
   function Evaluation_Completed
     (A : T.Bytes; Binding : T.Attempt_Binding; Rows : Measured_Array;
      Context : Context_Measurement; Completion : Required_Check) return Boolean is
     (Old.Names_Completion (A, Completion.Check)
      and then Old.Context_Matches (A, Binding, Context)
      and then Rows'Length /= 0
      and then Row_Bound (A, Rows (Rows'Last), Binding)
      and then W.Completion_Admitted (Rows (Rows'Last).Raw)
      and then Required_Evidence (A, Rows (Rows'Last), Completion))
     with Global => null;
   function Failure_For_Check_Reference
     (A : T.Bytes; Binding : T.Attempt_Binding;
      Rows : Measured_Array; Check : T.Check_Identity) return Boolean is
     (for some J in Rows'Range =>
       Row_Bound (A, Rows (J), Binding)
       and then T.P.Same (A, T.Span (Rows (J).Item.Check), T.Span (Check))
       and then W.Well_Formed (Rows (J).Raw)
       and then E.Expected_Classification (W.Decode (Rows (J).Raw).Value.Facts).Execution = E.Completed
       and then E.Expected_Classification (W.Decode (Rows (J).Raw).Value.Facts).Result = E.Failed)
     with Global => null;
   function Failure_For_Check
     (A : T.Bytes; Binding : T.Attempt_Binding;
      Rows : Measured_Array; Check : T.Check_Identity) return Boolean
     with Global => null,
       Post => Failure_For_Check'Result = Failure_For_Check_Reference (A, Binding, Rows, Check);
   function Genuine_Required_Failure
     (A : T.Bytes; Binding : T.Attempt_Binding; Rows : Measured_Array;
      Required : Check_Array; Context : Context_Measurement;
      Completion : Required_Check) return Boolean is
     (Evaluation_Completed (A, Binding, Rows, Context, Completion)
      and then (for some I in Required'Range =>
        Failure_For_Check_Reference (A, Binding, Rows, Required (I).Check)))
     with Global => null;
   function Promotion_Roster
     (A : T.Bytes; Binding : T.Attempt_Binding; Rows : Measured_Array;
      Required : Check_Array; Policy : Declaration; Context : Context_Measurement;
      Completion : Required_Check) return Boolean is
     (Evaluation_Completed (A, Binding, Rows, Context, Completion)
      and then Policy /= Old.Missing_Declaration
      and then ((Policy = Old.Explicit_Empty) = (Required'Length = 0))
      and then (for all J in Rows'Range =>
        Row_Bound (A, Rows (J), Binding) and then Matches_Classification (Rows (J)))
      and then (for all I in Required'Range =>
        Selected (A, Rows, Required (I).Check) /= 0 and then
        Required_Evidence (A, Rows (Selected (A, Rows, Required (I).Check)), Required (I))))
     with Global => null;
   function Reference
     (A : T.Bytes; Binding : T.Attempt_Binding; Rows : Measured_Array;
      Required : Check_Array; Policy : Declaration; Context : Context_Measurement;
      Completion : Required_Check) return Classification is
     (if not Evaluation_Completed (A, Binding, Rows, Context, Completion)
      then (E.Incomplete_Unknown, E.No_Outcome, False)
      elsif Genuine_Required_Failure (A, Binding, Rows, Required, Context, Completion)
      then (E.Completed, E.Failed, False)
      elsif Promotion_Roster (A, Binding, Rows, Required, Policy, Context, Completion)
      then (E.Completed, E.Passed, True)
      else (E.Incomplete_Unknown, E.No_Outcome, False)) with Global => null;
   function Classify
     (A : T.Bytes; Binding : T.Attempt_Binding; Rows : Measured_Array;
      Required : Check_Array; Policy : Declaration; Context : Context_Measurement;
      Completion : Required_Check) return Classification
     with Global => null,
       Post => Classify'Result = Reference (A, Binding, Rows, Required, Policy, Context, Completion);

   type Row_Span is record
      First : T.Index;
      Length : T.Count;
   end record;
   type Check_Span is new Row_Span;
   function Valid_Rows (Rows : Measured_Array; S : Row_Span) return Boolean is
     (S.Length = 0 or else (S.First in Rows'Range
       and then S.Length - 1 <= Rows'Last - S.First)) with Global => null;
   function Valid_Checks (Required : Check_Array; S : Check_Span) return Boolean is
     (S.Length = 0 or else (S.First in Required'Range
       and then S.Length - 1 <= Required'Last - S.First)) with Global => null;
   type Captured_Evaluation is record
      Binding : T.Attempt_Binding;
      Rows : Row_Span;
      Required : Check_Span;
      Policy : Declaration;
      Context : Context_Measurement;
      Completion : Required_Check;
   end record;
   type Captured_History is array (T.Index range <>) of Captured_Evaluation;

   function Same_Current_Requirement
     (A : T.Bytes; Recorded, Current : T.Attempt_Binding) return Boolean is
     (T.Valid_Binding (A, Recorded) and then T.Valid_Binding (A, Current)
      and then Recorded.Requirement.Present and then Current.Requirement.Present
      and then T.P.Same (A, T.Span (Recorded.Store), T.Span (Current.Store))
      and then T.P.Same (A, T.Span (Recorded.Subject), T.Span (Current.Subject))
      and then T.P.Same (A, T.Span (Recorded.Content), T.Span (Current.Content))
      and then T.Same_Requirement (A, Recorded.Requirement, Current.Requirement)) with Global => null;
   --  No sequence/count cap or digest identity is introduced. Invalid spans
   --  are inputs and cannot create a failure. They remain explicit refusal
   --  obligations for a future complete history selector, not silently valid.
   function Captured_Failure
     (A : T.Bytes; Rows : Measured_Array; Required : Check_Array;
      Captured : Captured_Evaluation; Current : T.Attempt_Binding) return Boolean is
     (Valid_Rows (Rows, Captured.Rows) and then Valid_Checks (Required, Captured.Required)
      and then Same_Current_Requirement (A, Captured.Binding, Current)
      and then Captured.Rows.Length /= 0 and then Captured.Required.Length /= 0
      and then Genuine_Required_Failure
        (A, Captured.Binding,
         Rows (Captured.Rows.First .. Captured.Rows.First + (Captured.Rows.Length - 1)),
         Required (Captured.Required.First .. Captured.Required.First + (Captured.Required.Length - 1)),
         Captured.Context, Captured.Completion)) with Global => null;
   function Any_Completed_Failure
     (A : T.Bytes; Rows : Measured_Array; Required : Check_Array;
      History : Captured_History; Current : T.Attempt_Binding) return Boolean
     with Global => null,
       Post => Any_Completed_Failure'Result =
         (for some I in History'Range => Captured_Failure (A, Rows, Required, History (I), Current));
end Evaluation_Raw_Roster;
