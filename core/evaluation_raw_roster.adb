package body Evaluation_Raw_Roster with SPARK_Mode is
   function Selected (A : T.Bytes; Rows : Measured_Array; Check : T.Check_Identity)
      return T.Count is
      Found : T.Count := 0;
   begin
      for I in Rows'Range loop
         if T.P.Same (A, T.Span (Rows (I).Item.Check), T.Span (Check)) then Found := I; end if;
         pragma Loop_Invariant
           (if Found = 0 then
              (for all J in Rows'First .. I =>
                not T.P.Same (A, T.Span (Rows (J).Item.Check), T.Span (Check)))
            else Found in Rows'First .. I
              and then T.P.Same (A, T.Span (Rows (Found).Item.Check), T.Span (Check))
              and then (for all J in Rows'First .. I =>
                (if J > Found then not T.P.Same (A, T.Span (Rows (J).Item.Check), T.Span (Check)))));
      end loop;
      return Found;
   end Selected;

   function Failure_For_Check
     (A : T.Bytes; Binding : T.Attempt_Binding;
      Rows : Measured_Array; Check : T.Check_Identity) return Boolean is
   begin
      for I in Rows'Range loop
         if Row_Bound (A, Rows (I), Binding)
           and then T.P.Same (A, T.Span (Rows (I).Item.Check), T.Span (Check))
         then
            declare
               C : constant W.Wire_Classification := W.Classify_Wire (Rows (I).Raw);
            begin
               if C.Status = 0 and then C.Execution = E.Execution_State'Pos (E.Completed)
                 and then C.Result = E.Outcome'Pos (E.Failed) then return True; end if;
            end;
         end if;
         pragma Loop_Invariant
           (for all J in Rows'First .. I =>
              not (Row_Bound (A, Rows (J), Binding)
               and then T.P.Same (A, T.Span (Rows (J).Item.Check), T.Span (Check))
               and then W.Well_Formed (Rows (J).Raw)
               and then E.Expected_Classification (W.Decode (Rows (J).Raw).Value.Facts).Execution = E.Completed
               and then E.Expected_Classification (W.Decode (Rows (J).Raw).Value.Facts).Result = E.Failed));
      end loop;
      return False;
   end Failure_For_Check;

   function Classify
     (A : T.Bytes; Binding : T.Attempt_Binding; Rows : Measured_Array;
      Required : Check_Array; Policy : Declaration; Context : Context_Measurement;
      Completion : Required_Check) return Classification is
   begin
      if not Evaluation_Completed (A, Binding, Rows, Context, Completion) then
         return (E.Incomplete_Unknown, E.No_Outcome, False);
      end if;
      for I in Required'Range loop
         if Failure_For_Check (A, Binding, Rows, Required (I).Check) then
            return (E.Completed, E.Failed, False);
         end if;
         pragma Loop_Invariant (for all J in Required'First .. I =>
           not Failure_For_Check_Reference (A, Binding, Rows, Required (J).Check));
      end loop;
      if Promotion_Roster (A, Binding, Rows, Required, Policy, Context, Completion) then
         return (E.Completed, E.Passed, True);
      end if;
      return (E.Incomplete_Unknown, E.No_Outcome, False);
   end Classify;

   function Any_Completed_Failure
     (A : T.Bytes; Rows : Measured_Array; Required : Check_Array;
      History : Captured_History; Current : T.Attempt_Binding) return Boolean is
   begin
      for I in History'Range loop
         if Captured_Failure (A, Rows, Required, History (I), Current) then return True; end if;
         pragma Loop_Invariant (for all J in History'First .. I =>
           not Captured_Failure (A, Rows, Required, History (J), Current));
      end loop;
      return False;
   end Any_Completed_Failure;
end Evaluation_Raw_Roster;
