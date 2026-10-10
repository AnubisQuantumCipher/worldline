with Interfaces;
with Resource_Quantities;
with Evaluation_Epoch;

--  Pure journal-transition relation. It cannot certify the custody of either
--  observed store, nor that a reported durable write actually occurred.
package Evaluation_Pending with SPARK_Mode is
   subtype Byte is Interfaces.Unsigned_8;
   subtype Count is Resource_Quantities.Byte_Count;
   subtype Index is Count range 1 .. Count'Last;
   subtype Bytes is Resource_Quantities.Byte_Array;
   use type Interfaces.Unsigned_8;
   use type Resource_Quantities.Byte_Count;

   type Span is record
      First : Index;
      Length : Count;
   end record;
   type Cursor (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Sequence : Span; Run : Span;
      end case;
   end record;
   type Link_State is (Reserved, Linked);
   type Intent is record
      Store_Id, Subject, Content, Run : Span;
      Sequence : Span;
      Previous : Cursor;
      State : Link_State;
   end record;
   type Journal is array (Index range <>) of Intent;
   type Operation is (Begin_New, Replay);
   type Decision is
     (Input_Invalid, Journal_Invalid, Journal_Cursor_Mismatch,
      Target_Cursor_Mismatch, Replay_Required, Run_Already_Used,
      Epoch_Proposal_Invalid, Replay_Absent, Reserve_New, Write_Pending,
      Acknowledge_Link, Already_Linked);
   type Plan is record
      Reason : Decision;
      Sequence : Span;
      Selected : Count;
   end record;
   function Refusal (Reason : Decision) return Plan is
     ((Reason => Reason, Sequence => (First => 1, Length => 0), Selected => 0))
     with Global => null;

   function Valid (A : Bytes; S : Span) return Boolean is
     (S.Length = 0 or else
        (S.First in A'Range and then S.Length - 1 <= A'Last - S.First))
     with Global => null;
   function Same (A : Bytes; L, R : Span) return Boolean is
     (Valid (A, L) and then Valid (A, R) and then L.Length = R.Length
      and then (for all K in Count range 0 .. L.Length - 1 =>
         A (L.First + K) = A (R.First + K)))
     with Global => null;
   function Epoch_Same (A : Bytes; L, R : Span) return Boolean is
     (Valid (A, L) and then Valid (A, R) and then
       Evaluation_Epoch.Same_Value
         (A, (False, L.First, L.Length), (False, R.First, R.Length)))
     with Global => null;
   function Successor (A : Bytes; Before, After : Span) return Boolean is
     (Valid (A, Before) and then Valid (A, After) and then
       Evaluation_Epoch.Is_Successor
         (A, (False, Before.First, Before.Length),
          (False, After.First, After.Length))) with Global => null;
   function Valid_Cursor (A : Bytes; C : Cursor) return Boolean is
     (not C.Present or else (Valid (A, C.Run) and then Valid (A, C.Sequence))) with Global => null;
   function Same_Cursor (A : Bytes; L, R : Cursor) return Boolean is
     (L.Present = R.Present and then
        (not L.Present or else
           (Epoch_Same (A, L.Sequence, R.Sequence) and then Same (A, L.Run, R.Run))))
     with Global => null;
   function Head (J : Journal) return Cursor is
     (if J'Length = 0 then (Present => False)
      else (Present => True, Sequence => J (J'Last).Sequence,
            Run => J (J'Last).Run)) with Global => null;

   --  Complete ordered intent log, with no forgotten earlier intent. Only its
   --  last row can be unlinked. Identity comparison is full byte equality.
   function Journal_Valid
     (A : Bytes; J : Journal; Store_Id, Subject, Content : Span)
      return Boolean is
     (for all I in J'Range =>
        Valid (A, J (I).Run) and then Valid (A, J (I).Sequence)
        and then Same (A, Store_Id, J (I).Store_Id)
        and then Same (A, Subject, J (I).Subject)
        and then Same (A, Content, J (I).Content)
        and then Valid_Cursor (A, J (I).Previous)
        and then
          (if I = J'First then
              Successor (A, (1, 0), J (I).Sequence)
              and then not J (I).Previous.Present
           else J (I - 1).State = Linked
             and then Successor (A, J (I - 1).Sequence, J (I).Sequence)
             and then Same_Cursor
               (A, J (I).Previous,
                (Present => True, Sequence => J (I - 1).Sequence,
                 Run => J (I - 1).Run)))
        and then (for all K in J'Range =>
          (if K < I then not Same (A, J (K).Run, J (I).Run))))
     with Global => null;
   function Target_Valid (A : Bytes; J : Journal; Target : Cursor)
      return Boolean is
     (Valid_Cursor (A, Target) and then
        (if J'Length = 0 then not Target.Present
         elsif J (J'Last).State = Linked then
            Same_Cursor (A, Target, Head (J))
         else Same_Cursor (A, Target, Head (J)) or else
              Same_Cursor (A, Target, J (J'Last).Previous)))
     with Global => null;
   function Run_Index (A : Bytes; J : Journal; Run : Span) return Count
     with Global => null,
          Post =>
            (if Run_Index'Result = 0 then
                (for all I in J'Range => not Same (A, J (I).Run, Run))
             else Run_Index'Result in J'Range
               and then Same (A, J (Run_Index'Result).Run, Run)
               and then (for all I in J'Range =>
                 (if I < Run_Index'Result then
                    not Same (A, J (I).Run, Run))));

   function Reference
     (A : Bytes; J : Journal; Store_Id, Subject, Content, Run, Proposed_Epoch : Span;
      Authority_Head, Target_Head : Cursor; Op : Operation) return Plan is
     (if not Valid (A, Store_Id) or else not Valid (A, Subject)
         or else not Valid (A, Content) or else not Valid (A, Run)
         or else not Valid (A, Proposed_Epoch)
         or else not Valid_Cursor (A, Authority_Head)
         or else not Valid_Cursor (A, Target_Head) then Refusal (Input_Invalid)
      elsif not Journal_Valid (A, J, Store_Id, Subject, Content)
      then Refusal (Journal_Invalid)
      elsif not Same_Cursor (A, Authority_Head, Head (J))
      then Refusal (Journal_Cursor_Mismatch)
      elsif not Target_Valid (A, J, Target_Head)
      then Refusal (Target_Cursor_Mismatch)
      elsif Op = Begin_New then
        (if J'Length /= 0 and then J (J'Last).State = Reserved
         then Refusal (Replay_Required)
         elsif Run_Index (A, J, Run) /= 0 then Refusal (Run_Already_Used)
         elsif not Successor
           (A, (if J'Length = 0 then (1, 0) else J (J'Last).Sequence),
            Proposed_Epoch) then Refusal (Epoch_Proposal_Invalid)
         else (Reason => Reserve_New,
               Sequence => Proposed_Epoch, Selected => 0))
      elsif Run_Index (A, J, Run) = 0 then Refusal (Replay_Absent)
      elsif J (Run_Index (A, J, Run)).State = Linked then
         (Reason => Already_Linked,
          Sequence => J (Run_Index (A, J, Run)).Sequence,
          Selected => Run_Index (A, J, Run))
      elsif Same_Cursor (A, Target_Head, Head (J)) then
         (Reason => Acknowledge_Link, Sequence => J (J'Last).Sequence,
          Selected => J'Last)
      else (Reason => Write_Pending, Sequence => J (J'Last).Sequence,
            Selected => J'Last)) with Global => null;

   --  Total for every typed arena, arbitrary/null journal and cursor. No
   --  supplied success/provenance Boolean replaces the complete relation.
   function Decide
     (A : Bytes; J : Journal; Store_Id, Subject, Content, Run, Proposed_Epoch : Span;
      Authority_Head, Target_Head : Cursor; Op : Operation) return Plan
     with Global => null,
          Post => Decide'Result = Reference
            (A, J, Store_Id, Subject, Content, Run, Proposed_Epoch,
             Authority_Head, Target_Head, Op);
end Evaluation_Pending;
