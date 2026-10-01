package body Evaluation_Completion_Roster with SPARK_Mode is
   function Selected (A : T.Bytes; Rows : Measured_Array; Check : T.Check_Identity)
      return T.Count is
      Last : T.Count := 0;
   begin
      for J in Rows'Range loop
         if T.P.Same (A, T.Span (Rows (J).Item.Check), T.Span (Check)) then Last := J; end if;
         pragma Loop_Invariant (if Last = 0 then
           (for all K in Rows'First .. J => not T.P.Same (A, T.Span (Rows (K).Item.Check), T.Span (Check)))
          else Last in Rows'First .. J
           and then T.P.Same (A, T.Span (Rows (Last).Item.Check), T.Span (Check))
           and then (for all K in Rows'First .. J =>
             (if K > Last then not T.P.Same (A, T.Span (Rows (K).Item.Check), T.Span (Check)))));
      end loop;
      return Last;
   end Selected;
   function Failure_For_Check
     (A : T.Bytes; Rows : Measured_Array; Check : T.Check_Identity)
      return Boolean is
   begin
      for J in Rows'Range loop
         if T.P.Same (A, T.Span (Rows (J).Item.Check), T.Span (Check))
           and then E.Classify (Rows (J).Facts).Execution = E.Completed
           and then E.Classify (Rows (J).Facts).Result = E.Failed
         then
            return True;
         end if;
         pragma Loop_Invariant
           (for all K in Rows'First .. J =>
              not (T.P.Same (A, T.Span (Rows (K).Item.Check), T.Span (Check))
                and then E.Classify (Rows (K).Facts).Execution = E.Completed
                and then E.Classify (Rows (K).Facts).Result = E.Failed));
      end loop;
      return False;
   end Failure_For_Check;
   function Classify
     (A : T.Bytes; Binding : T.Attempt_Binding; Rows : Measured_Array;
      Required : Check_Array; Policy : Declaration; Context : Context_Measurement;
      Completion : Required_Check) return Classification is
      Failed : Boolean := False;
      Promotion : Boolean;
      Choice : T.Count;
   begin
      if not Evaluation_Completed (A, Binding, Rows, Context, Completion) then
         return (E.Incomplete_Unknown, E.No_Outcome, False);
      end if;
      Promotion := Policy /= Missing_Declaration and then
        ((Policy = Explicit_Empty) = (Required'Length = 0));
      for I in Required'Range loop
         Failed := Failed or else Failure_For_Check (A, Rows, Required (I).Check);
         Choice := Selected (A, Rows, Required (I).Check);
         if Choice = 0 then
            Promotion := False;
         else
            Promotion := Promotion and then Required_Evidence (A, Rows (Choice), Required (I));
         end if;
         pragma Loop_Invariant (Failed = (for some K in Required'First .. I =>
           Failure_For_Check_Reference (A, Rows, Required (K).Check)));
         pragma Loop_Invariant (Promotion =
           (Policy /= Missing_Declaration and then ((Policy = Explicit_Empty) = (Required'Length = 0))
            and then (for all K in Required'First .. I =>
              Selected (A, Rows, Required (K).Check) /= 0 and then
              Required_Evidence (A, Rows (Selected (A, Rows, Required (K).Check)), Required (K)))));
      end loop;
      if Failed then
         return (E.Completed, E.Failed, False);
      elsif Promotion then
         return (E.Completed, E.Passed, True);
      else
         return (E.Incomplete_Unknown, E.No_Outcome, False);
      end if;
   end Classify;
end Evaluation_Completion_Roster;
