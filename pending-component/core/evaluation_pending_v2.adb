package body Evaluation_Pending_V2 with SPARK_Mode is
   function Base_Of (J : Journal) return P.Journal is
      --  Initialize every result component from its corresponding actual input.
      --  The null range reads no element; optional cursor variants are copied
      --  exactly, rather than fabricated as a default present or absent value.
      --  Keep the original loop and full projection invariant below.
      Result : P.Journal (J'Range) := (for I in J'Range => J (I).Base);
   begin
      for I in J'Range loop
         Result (I) := J (I).Base;
         pragma Loop_Invariant
           (for all K in J'First .. I => Result (K) = J (K).Base);
      end loop;
      return Result;
   end Base_Of;
   function Decide
     (A : Bytes; J : Journal; Store_Id, Subject, Content, Run, Proposed_Epoch : Span;
      Required : Optional_Requirement; Authority_Head, Target_Head : P.Cursor;
      Op : P.Operation) return Plan
   is
      Legacy : P.Plan;
   begin
      if not Valid (A, Required) then
         return Refusal (Input_Invalid);
      elsif not Requirements_Valid (A, J) then
         return Refusal (Journal_Invalid);
      end if;
      Legacy := P.Decide (A, Base_Of (J), Store_Id, Subject, Content, Run,
                         Proposed_Epoch, Authority_Head, Target_Head, Op);
      if Legacy.Reason = P.Reserve_New then
         return (Reserve_New, Legacy.Sequence, Legacy.Selected, Required);
      elsif Legacy.Reason in P.Write_Pending | P.Acknowledge_Link | P.Already_Linked then
         if Legacy.Selected not in J'Range then
            return Refusal (Journal_Invalid);
         elsif not Same (A, Required, J (Legacy.Selected).Requirement) then
            return Refusal (Requirement_Conflict);
         end if;
         return (Decision'Val (P.Decision'Pos (Legacy.Reason)),
                 Legacy.Sequence, Legacy.Selected, J (Legacy.Selected).Requirement);
      end if;
      return (Decision'Val (P.Decision'Pos (Legacy.Reason)),
              Legacy.Sequence, Legacy.Selected, (Present => False));
   end Decide;
end Evaluation_Pending_V2;
