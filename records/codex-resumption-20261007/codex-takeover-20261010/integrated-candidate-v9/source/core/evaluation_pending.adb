package body Evaluation_Pending with SPARK_Mode is
   function Run_Index (A : Bytes; J : Journal; Run : Span) return Count is
   begin
      for I in J'Range loop
         if Same (A, J (I).Run, Run) then
            return I;
         end if;
         pragma Loop_Invariant
           (for all K in J'First .. I => not Same (A, J (K).Run, Run));
      end loop;
      return 0;
   end Run_Index;

   function Decide
     (A : Bytes; J : Journal; Store_Id, Subject, Content, Run, Proposed_Epoch : Span;
      Authority_Head, Target_Head : Cursor; Op : Operation) return Plan is
      Selected : Count;
   begin
      if not Valid (A, Store_Id) or else not Valid (A, Subject)
        or else not Valid (A, Content) or else not Valid (A, Run)
        or else not Valid (A, Proposed_Epoch)
        or else not Valid_Cursor (A, Authority_Head)
        or else not Valid_Cursor (A, Target_Head)
      then
         return Refusal (Input_Invalid);
      elsif not Journal_Valid (A, J, Store_Id, Subject, Content) then
         return Refusal (Journal_Invalid);
      elsif not Same_Cursor (A, Authority_Head, Head (J)) then
         return Refusal (Journal_Cursor_Mismatch);
      elsif not Target_Valid (A, J, Target_Head) then
         return Refusal (Target_Cursor_Mismatch);
      end if;
      Selected := Run_Index (A, J, Run);
      if Op = Begin_New then
         if J'Length /= 0 and then J (J'Last).State = Reserved then
            return Refusal (Replay_Required);
         elsif Selected /= 0 then
            return Refusal (Run_Already_Used);
         elsif not Successor
           (A, (if J'Length = 0 then (1, 0) else J (J'Last).Sequence),
            Proposed_Epoch) then
            return Refusal (Epoch_Proposal_Invalid);
         else
            return (Reserve_New, Proposed_Epoch, 0);
         end if;
      elsif Selected = 0 then
         return Refusal (Replay_Absent);
      elsif J (Selected).State = Linked then
         return (Already_Linked, J (Selected).Sequence, Selected);
      elsif Same_Cursor (A, Target_Head, Head (J)) then
         return (Acknowledge_Link, J (J'Last).Sequence, J'Last);
      else
         return (Write_Pending, J (J'Last).Sequence, J'Last);
      end if;
   end Decide;
end Evaluation_Pending;
