with Evaluation_Completion;
package Evaluation_Completion_Roster with SPARK_Mode is
   package T renames Evaluation_Completion;
   package E renames T.E;
   use type T.Count;
   use type E.Execution_State;
   use type E.Outcome;
   use type E.Bundle_Integrity;
   use type E.Report_Integrity;
   use type E.Origin;
   use type T.P.Byte;
   type Measured_Result is record
      Item : T.Result_Record;
      Facts : E.Observations;
      Report : E.Report_Integrity;
      Presence : E.Evidence_Presence;
      Declared : T.Captured_Bytes;
   end record;
   type Measured_Array is array (T.Index range <>) of Measured_Result;
   type Required_Check is record
      Check : T.Check_Identity;
      Declared : T.Captured_Bytes;
   end record;
   type Check_Array is array (T.Index range <>) of Required_Check;
   type Declaration is (Missing_Declaration, Explicit_Empty, Required_Checks);
   type Context_Measurement is record
      Binding : T.Attempt_Binding;
      Before_Root, After_Root : T.Captured_Bytes;
   end record;
   type Classification is record
      State : E.Terminal_State;
      Outcome : E.Outcome;
      Promotion_Ready : Boolean;
   end record;
   -- Exact required PASS evidence conditions retain original Admissible.
   -- D2 failure retention is the distinct predicate below. Raw fact
   -- decoding, invocation/root provenance and custody are mandatory producers,
   -- not certified by these supplied finite observations or their byte labels.
   function Required_Evidence (A : T.Bytes; R : Measured_Result;
                                Required : Required_Check) return Boolean is
     (T.P.Valid (A, T.Span (Required.Check))
      and then T.P.Valid (A, T.Span (Required.Declared))
      and then T.P.Valid (A, T.Span (R.Declared))
      and then T.P.Same (A, T.Span (R.Item.Check), T.Span (Required.Check))
      and then T.P.Same (A, T.Span (R.Declared), T.Span (Required.Declared))
      and then R.Item.State = E.Classify (R.Facts).Execution
      and then R.Item.Outcome = E.Classify (R.Facts).Result
      and then E.Classify (R.Facts).Execution = E.Completed
      and then E.Classify (R.Facts).Result = E.Passed
      and then E.Classify (R.Facts).Bundle in E.Not_Covered | E.Verified
      and then R.Report in E.Not_Applicable | E.Verified_Report
      and then E.Evidence_Complete (R.Presence)
      and then E.Admissible (E.Classify (R.Facts), R.Report, R.Presence)) with Global => null;
   function Selected (A : T.Bytes; Rows : Measured_Array; Check : T.Check_Identity)
      return T.Count with Global => null,
      Post => (if Selected'Result = 0 then
        (for all J in Rows'Range => not T.P.Same (A, T.Span (Rows (J).Item.Check), T.Span (Check)))
       else Selected'Result in Rows'Range
        and then T.P.Same (A, T.Span (Rows (Selected'Result).Item.Check), T.Span (Check))
        and then (for all J in Rows'Range =>
          (if J > Selected'Result then not T.P.Same (A, T.Span (Rows (J).Item.Check), T.Span (Check)))));
   -- Preserve original results_by_id selection: last matching result, not an
   -- arbitrary earlier PASS; unrelated captured rows stay retained unchanged.
   Engine_Completion_Name : constant String := "evaluation-complete";
   function Names_Completion (A : T.Bytes; Check : T.Check_Identity) return Boolean is
     (T.P.Valid (A, T.Span (Check))
      and then Check.Length = Engine_Completion_Name'Length
      and then (for all I in Engine_Completion_Name'Range =>
        A (Check.First + T.Count (I - Engine_Completion_Name'First)) =
          T.P.Byte (Character'Pos (Engine_Completion_Name (I))))) with Global => null;
   function Context_Matches
     (A : T.Bytes; Binding : T.Attempt_Binding; Context : Context_Measurement)
      return Boolean is
     (T.Same_Binding (A, Binding, Context.Binding) and then Binding.Requirement.Present
      and then T.P.Same (A, T.Span (Context.Before_Root), T.Span (Context.After_Root)))
     with Global => null;
   function Evaluation_Completed
     (A : T.Bytes; Binding : T.Attempt_Binding; Rows : Measured_Array;
      Context : Context_Measurement; Completion : Required_Check) return Boolean is
     (Names_Completion (A, Completion.Check)
      and then Context_Matches (A, Binding, Context)
      and then Rows'Length /= 0
      and then (for all J in Rows'Range => T.Valid_Result (A, Rows (J).Item)
        and then T.Same_Binding (A, Rows (J).Item.Binding, Binding)
        and then Rows (J).Item.State = E.Classify (Rows (J).Facts).Execution
        and then Rows (J).Item.Outcome = E.Classify (Rows (J).Facts).Result)
      and then Rows (Rows'Last).Facts.Source = E.Engine
      and then Required_Evidence (A, Rows (Rows'Last), Completion))
     with Global => null;
   -- D2 is independent of other rows' promotion admission. Missing/conflicting
   -- evidence still refuses promotion and remains retained, without erasing an
   -- admitted completion record and an actual required Completed/Failed result.
   --  D2 is existential over the complete retained raw stream. Selection of
   --  the last result is only the separate promotion-roster policy.
   function Failure_For_Check_Reference
     (A : T.Bytes; Rows : Measured_Array; Check : T.Check_Identity)
      return Boolean is
     (for some J in Rows'Range =>
        T.P.Same (A, T.Span (Rows (J).Item.Check), T.Span (Check))
        and then E.Classify (Rows (J).Facts).Execution = E.Completed
        and then E.Classify (Rows (J).Facts).Result = E.Failed)
     with Global => null;
   function Failure_For_Check
     (A : T.Bytes; Rows : Measured_Array; Check : T.Check_Identity)
      return Boolean
     with Global => null,
       Post => Failure_For_Check'Result = Failure_For_Check_Reference (A, Rows, Check);
   function Genuine_Required_Failure
     (A : T.Bytes; Binding : T.Attempt_Binding; Rows : Measured_Array;
      Required : Check_Array; Context : Context_Measurement;
      Completion : Required_Check) return Boolean is
     (Evaluation_Completed (A, Binding, Rows, Context, Completion)
      and then (for some I in Required'Range =>
        Failure_For_Check_Reference (A, Rows, Required (I).Check)))
     with Global => null;
   function Promotion_Roster
     (A : T.Bytes; Binding : T.Attempt_Binding; Rows : Measured_Array;
      Required : Check_Array; Policy : Declaration; Context : Context_Measurement;
      Completion : Required_Check) return Boolean is
     (Evaluation_Completed (A, Binding, Rows, Context, Completion)
      and then Policy /= Missing_Declaration
      and then ((Policy = Explicit_Empty) = (Required'Length = 0))
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
      else (E.Incomplete_Unknown, E.No_Outcome, False))
     with Global => null;
   function Classify
     (A : T.Bytes; Binding : T.Attempt_Binding; Rows : Measured_Array;
      Required : Check_Array; Policy : Declaration; Context : Context_Measurement;
      Completion : Required_Check) return Classification
     with Global => null,
       Post => Classify'Result = Reference (A, Binding, Rows, Required, Policy, Context, Completion);
end Evaluation_Completion_Roster;
