with Evaluation_Pending;
package Evaluation_Pending_V2 with SPARK_Mode is
   package P renames Evaluation_Pending;
   use type P.Count;
   use type P.Plan;
   use type P.Intent;
   use type P.Decision;
   subtype Bytes is P.Bytes;
   subtype Span is P.Span;
   subtype Count is P.Count;
   subtype Index is P.Index;
   type Requirement_Id is new Span;
   type Optional_Requirement (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : Requirement_Id;
      end case;
   end record;
   --  Additive typed schema. Legacy Intent/ABI v1 remain byte-exact. The actual
   --  prepared producer uses this record, never an unbound requirement sidecar.
   type Intent is record
      Base : P.Intent;
      Requirement : Optional_Requirement;
   end record;
   type Journal is array (Index range <>) of Intent;
   function Valid (A : Bytes; R : Optional_Requirement) return Boolean is
     (not R.Present or else P.Valid (A, Span (R.Value))) with Global => null;
   function Same (A : Bytes; L, R : Optional_Requirement) return Boolean is
     (L.Present = R.Present and then
       (not L.Present or else P.Same (A, Span (L.Value), Span (R.Value))))
     with Global => null;
   function Base_Of (J : Journal) return P.Journal
     with Global => null,
          Post => Base_Of'Result'First = J'First
            and then Base_Of'Result'Last = J'Last
            and then (for all I in J'Range => Base_Of'Result (I) = J (I).Base);
   function Requirements_Valid (A : Bytes; J : Journal) return Boolean is
     (for all I in J'Range => Valid (A, J (I).Requirement)) with Global => null;
   function Journal_Valid
     (A : Bytes; J : Journal; Store_Id, Subject, Content : Span) return Boolean is
     (Requirements_Valid (A, J)
      and then P.Journal_Valid (A, Base_Of (J), Store_Id, Subject, Content))
     with Global => null;
   type Decision is
     (Input_Invalid, Journal_Invalid, Journal_Cursor_Mismatch,
      Target_Cursor_Mismatch, Replay_Required, Run_Already_Used,
      Epoch_Proposal_Invalid, Replay_Absent, Reserve_New, Write_Pending,
      Acknowledge_Link, Already_Linked, Requirement_Conflict);
   type Plan is record
      Reason : Decision;
      Sequence : Span;
      Selected : Count;
      Requirement : Optional_Requirement;
   end record;
   function Refusal (Reason : Decision) return Plan is
     (Reason, (1, 0), 0, (Present => False)) with Global => null;
   function Bind_Plan
     (A : Bytes; J : Journal; Required : Optional_Requirement; Legacy : P.Plan)
      return Plan is
     (if Legacy.Reason = P.Reserve_New then
         (Reserve_New, Legacy.Sequence, Legacy.Selected, Required)
      elsif Legacy.Reason in P.Write_Pending | P.Acknowledge_Link | P.Already_Linked then
         (if Legacy.Selected not in J'Range then Refusal (Journal_Invalid)
          elsif not Same (A, Required, J (Legacy.Selected).Requirement)
          then Refusal (Requirement_Conflict)
          else (Decision'Val (P.Decision'Pos (Legacy.Reason)),
                Legacy.Sequence, Legacy.Selected, J (Legacy.Selected).Requirement))
      else (Decision'Val (P.Decision'Pos (Legacy.Reason)),
            Legacy.Sequence, Legacy.Selected, (Present => False)))
     with Global => null;
   function Reference
     (A : Bytes; J : Journal; Store_Id, Subject, Content, Run, Proposed_Epoch : Span;
      Required : Optional_Requirement; Authority_Head, Target_Head : P.Cursor;
      Op : P.Operation) return Plan is
     (if not Valid (A, Required) then Refusal (Input_Invalid)
      elsif not Requirements_Valid (A, J) then Refusal (Journal_Invalid)
      else Bind_Plan (A, J, Required,
        P.Reference (A, Base_Of (J), Store_Id, Subject, Content, Run,
                     Proposed_Epoch, Authority_Head, Target_Head, Op)))
     with Global => null;
   function Decide
     (A : Bytes; J : Journal; Store_Id, Subject, Content, Run, Proposed_Epoch : Span;
      Required : Optional_Requirement; Authority_Head, Target_Head : P.Cursor;
      Op : P.Operation) return Plan
     with Global => null,
          Post => Decide'Result = Reference
            (A, J, Store_Id, Subject, Content, Run, Proposed_Epoch,
             Required, Authority_Head, Target_Head, Op);
end Evaluation_Pending_V2;
