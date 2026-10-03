with Interfaces;
with Resource_Quantities;
with SPARK.Big_Integers;

--  Candidate-evaluation history only.  Checkpoint-return lineage and tested-root
--  selection remain a distinct caller path.  This unit owns no store or effects.
package Evaluation_History with SPARK_Mode is
   use type Interfaces.Unsigned_8;
   use type Resource_Quantities.Byte_Count;
   use SPARK.Big_Integers;
   subtype Byte_Count is Resource_Quantities.Byte_Count;
   subtype Byte_Index is Resource_Quantities.Byte_Index;
   subtype Byte_Array is Resource_Quantities.Byte_Array;
   type Identity_Span is record
      First : Byte_Index;
      Length : Byte_Count;
   end record;
   type Subject_Id is new Identity_Span;
   type Content_Id is new Identity_Span;
   type Requirement_Id is new Identity_Span;
   type Evaluation_Id is new Identity_Span;
   function Span_Valid (A : Byte_Array; S : Identity_Span) return Boolean is
     (S.Length = 0 or else
       (S.First in A'Range and then S.Length - 1 <= A'Last - S.First))
     with Global => null;
   function Same_Identity (A : Byte_Array; L, R : Identity_Span)
      return Boolean is
     (Span_Valid (A, L) and then Span_Valid (A, R)
      and then L.Length = R.Length
      and then (L.Length = 0 or else
        (for all Offset in Byte_Count range 0 .. L.Length - 1 =>
          A (L.First + Offset) = A (R.First + Offset))))
     with Global => null;
   -- Epoch storage length is bounded by the owned arena, never its value.
   -- Empty and leading-zero little-endian magnitudes are valid zero/padding.
   type Epoch_Id is new Identity_Span;
   function Epoch_Quantity (E : Epoch_Id) return Resource_Quantities.Quantity is
     (Negative => False, First => E.First, Length => E.Length)
     with Global => null;
   function Epoch_Valid (A : Byte_Array; E : Epoch_Id) return Boolean is
     (Span_Valid (A, Identity_Span (E))) with Global => null;
   function Epoch_Zero (A : Byte_Array; E : Epoch_Id) return Boolean is
     (Epoch_Valid (A, E) and then Resource_Quantities.Is_Zero (A, Epoch_Quantity (E)))
     with Global => null,
       Post => Epoch_Zero'Result =
         (Epoch_Valid (A, E) and then
          Resource_Quantities.Magnitude (A, Epoch_Quantity (E)) = 0);
   function Epoch_One (A : Byte_Array; E : Epoch_Id) return Boolean
     with Global => null,
       Post => Epoch_One'Result =
         (Epoch_Valid (A, E) and then
          Resource_Quantities.Magnitude (A, Epoch_Quantity (E)) = 1);
   function Same_Epoch (A : Byte_Array; L, R : Epoch_Id) return Boolean
     with Global => null,
       Post => Same_Epoch'Result =
         (Epoch_Valid (A, L) and then Epoch_Valid (A, R) and then
          Resource_Quantities.Magnitude (A, Epoch_Quantity (L)) =
          Resource_Quantities.Magnitude (A, Epoch_Quantity (R)));
   function Next_Epoch (A : Byte_Array; Before, After : Epoch_Id) return Boolean
     with Global => null,
       Post => Next_Epoch'Result =
         (Epoch_Valid (A, Before) and then Epoch_Valid (A, After) and then
          SPARK.Big_Integers."="
            (Resource_Quantities.Magnitude (A, Epoch_Quantity (After)),
             SPARK.Big_Integers."+"
               (Resource_Quantities.Magnitude (A, Epoch_Quantity (Before)),
                SPARK.Big_Integers.To_Big_Integer (1))));
   type Optional_Epoch (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : Epoch_Id;
      end case;
   end record;

   type Optional_Subject (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : Subject_Id;
      end case;
   end record;
   type Optional_Content (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : Content_Id;
      end case;
   end record;
   type Optional_Requirement (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : Requirement_Id;
      end case;
   end record;
   type Optional_Evaluation (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : Evaluation_Id;
      end case;
   end record;
   type Cursor is record
      Sequence : Optional_Epoch;
      Run : Evaluation_Id;
   end record;
   type Optional_Cursor (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : Cursor;
      end case;
   end record;

   --  Lifecycle and verdict are separate.  Invalid combinations remain inputs
   --  to the total selector and receive a named refusal, never a public Pre.
   type Lifecycle is (Pending, Error, Rollback_Fence, Completed);
   type Verdict is (No_Verdict, Passed, Failed);
   type Evaluation_Record is record
      Subject : Optional_Subject;
      Content : Optional_Content;
      Requirement : Optional_Requirement;
      Run : Optional_Evaluation;
      Sequence : Optional_Epoch;
      State : Lifecycle;
      Outcome : Verdict;
   end record;
   type Optional_Record (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : Evaluation_Record;
      end case;
   end record;
   type History is array (Byte_Index range <>) of Evaluation_Record;

   type Query is record
      Subject : Optional_Subject;
      Content : Optional_Content;
      Requirement : Optional_Requirement;
      --  Independently reread protected cursor and the prepared evidence cursor.
      --  Their provenance/authenticity are producer obligations, not Booleans
      --  manufactured by this pure rule.  Both include run identity and epoch.
      Current_Head : Optional_Cursor;
      Prepared_Evidence : Optional_Cursor;
   end record;

   type Source_Kind is (Absent, Finalization, History_Entry);
   type Record_Reference (Kind : Source_Kind := Absent) is record
      case Kind is
         when Absent | Finalization => null;
         when History_Entry => Index : Byte_Index;
      end case;
   end record;
   No_Record : constant Record_Reference := (Kind => Absent);

   type Decision is
     (Input_Absent, Input_Invalid, Finalization_Invalid, History_Invalid, Evidence_Absent,
      Evidence_Superseded, Requirement_Absent, Requirement_Changed,
      Evidence_Fenced, Evaluation_Incomplete, Evidence_Fail_Terminal,
      Ready);
   type Selection is record
      Reason : Decision;
      Head : Record_Reference;
      Completed_Failure : Record_Reference;
   end record;

   function Query_Complete (Q : Query) return Boolean is
     (Q.Subject.Present and then Q.Content.Present
      and then Q.Requirement.Present and then Q.Current_Head.Present
      and then Q.Prepared_Evidence.Present
      and then Q.Current_Head.Value.Sequence.Present
      and then Q.Prepared_Evidence.Value.Sequence.Present)
     with Global => null;

   function Query_Valid (A : Byte_Array; Q : Query) return Boolean is
     ((not Q.Subject.Present or else Span_Valid (A, Identity_Span (Q.Subject.Value)))
      and then (not Q.Content.Present or else Span_Valid (A, Identity_Span (Q.Content.Value)))
      and then (not Q.Requirement.Present or else Span_Valid (A, Identity_Span (Q.Requirement.Value)))
      and then (not Q.Current_Head.Present or else Span_Valid (A, Identity_Span (Q.Current_Head.Value.Run)))
      and then (not Q.Prepared_Evidence.Present or else Span_Valid (A, Identity_Span (Q.Prepared_Evidence.Value.Run)))
      and then (not Q.Current_Head.Present or else not Q.Current_Head.Value.Sequence.Present or else Epoch_Valid (A, Q.Current_Head.Value.Sequence.Value))
      and then (not Q.Prepared_Evidence.Present or else not Q.Prepared_Evidence.Value.Sequence.Present or else Epoch_Valid (A, Q.Prepared_Evidence.Value.Sequence.Value)))
     with Global => null;

   function Row_Valid (A : Byte_Array; R : Evaluation_Record; Q : Query) return Boolean is
     (Q.Subject.Present and then Q.Content.Present
      and then R.Subject.Present and then R.Content.Present
      and then R.Run.Present and then R.Sequence.Present
      and then Span_Valid (A, Identity_Span (R.Run.Value))
      and then Epoch_Valid (A, R.Sequence.Value)
      and then (not R.Requirement.Present or else Span_Valid (A, Identity_Span (R.Requirement.Value)))
      and then Same_Identity (A, Identity_Span (R.Subject.Value), Identity_Span (Q.Subject.Value))
      and then Same_Identity (A, Identity_Span (R.Content.Value), Identity_Span (Q.Content.Value))
      and then (if R.State = Completed then
                   R.Requirement.Present and then R.Outcome /= No_Verdict
                else R.Outcome = No_Verdict))
     with Global => null;

   function Finalization_Valid
     (A : Byte_Array; F : Optional_Record; Q : Query) return Boolean is
     (not F.Present or else
        (Row_Valid (A, F.Value, Q) and then Epoch_Zero (A, F.Value.Sequence.Value)))
     with Global => null;

   --  The entire ordered roster is checked; no malformed or wrong-subject row
   --  can be silently dropped while searching for a PASS.  Index bounds are
   --  arbitrary, including null arrays.  There is no fixed roster-length cap.
   function History_Valid
     (A : Byte_Array; H : History; F : Optional_Record; Q : Query) return Boolean is
     (for all I in H'Range =>
        Row_Valid (A, H (I), Q)
        and then
          (if I = H'First then Epoch_One (A, H (I).Sequence.Value)
           else H (I - 1).Sequence.Present and then
             Next_Epoch (A, H (I - 1).Sequence.Value, H (I).Sequence.Value))
        and then
          (not F.Present or else not F.Value.Run.Present or else
             not Same_Identity (A, Identity_Span (H (I).Run.Value), Identity_Span (F.Value.Run.Value)))
        and then (for all J in H'Range =>
          (if J < I then H (J).Run.Present and then
             not Same_Identity (A, Identity_Span (H (J).Run.Value), Identity_Span (H (I).Run.Value)))))
     with Global => null;

   function Is_Current_Failure
     (A : Byte_Array; R : Evaluation_Record; Q : Query) return Boolean is
     (Row_Valid (A, R, Q) and then Q.Requirement.Present
      and then R.Requirement.Present
      and then Same_Identity (A, Identity_Span (R.Requirement.Value), Identity_Span (Q.Requirement.Value))
      and then R.State = Completed and then R.Outcome = Failed)
     with Global => null;

   function Head_Reference
     (H : History; F : Optional_Record) return Record_Reference is
     (if H'Length /= 0 then (Kind => History_Entry, Index => H'Last)
      elsif F.Present then (Kind => Finalization)
      else No_Record)
     with Global => null;

   function Head_Record
     (H : History; F : Optional_Record) return Optional_Record is
     (if H'Length /= 0 then (Present => True, Value => H (H'Last))
      else F)
     with Global => null;

   function Cursor_Matches
     (A : Byte_Array; C : Optional_Cursor; R : Evaluation_Record) return Boolean is
     (C.Present and then C.Value.Sequence.Present
      and then R.Run.Present and then R.Sequence.Present
      and then Same_Epoch (A, C.Value.Sequence.Value, R.Sequence.Value)
      and then Same_Identity (A, Identity_Span (C.Value.Run), Identity_Span (R.Run.Value)))
     with Global => null;

   --  Total closed relation for the earliest retained completed FAIL.  The
   --  finalization precedes every history row.  ERROR/Pending/fence do not latch.
   function Failure_Reference_Conforms
     (A : Byte_Array; H : History; F : Optional_Record; Q : Query;
      Ref : Record_Reference) return Boolean is
     (case Ref.Kind is
         when Absent =>
           (not F.Present or else not Is_Current_Failure (A, F.Value, Q))
           and then (for all I in H'Range =>
                       not Is_Current_Failure (A, H (I), Q)),
         when Finalization =>
           F.Present and then Is_Current_Failure (A, F.Value, Q),
         when History_Entry =>
           Ref.Index in H'Range
           and then (not F.Present or else
                       not Is_Current_Failure (A, F.Value, Q))
           and then Is_Current_Failure (A, H (Ref.Index), Q)
           and then (for all I in H'Range =>
             (if I < Ref.Index then not Is_Current_Failure (A, H (I), Q))))
     with Global => null;

   function Find_Completed_Failure
     (A : Byte_Array; H : History; F : Optional_Record; Q : Query) return Record_Reference
     with Global => null,
          Post => Failure_Reference_Conforms (A, H, F, Q, Find_Completed_Failure'Result);

   --  Decision precedence after complete input/roster validation.  Every access
   --  is guarded; the function also has a defined answer on malformed inputs.
   function Head_Decision
     (A : Byte_Array; R : Optional_Record; Q : Query; Failure : Record_Reference)
      return Decision is
     (if not R.Present then Evidence_Absent
      elsif not Cursor_Matches (A, Q.Current_Head, R.Value)
        or else not Cursor_Matches (A, Q.Prepared_Evidence, R.Value)
      then Evidence_Superseded
      elsif not Q.Requirement.Present or else
            not R.Value.Requirement.Present then Requirement_Absent
      elsif not Same_Identity (A, Identity_Span (R.Value.Requirement.Value), Identity_Span (Q.Requirement.Value))
      then Requirement_Changed
      elsif R.Value.State = Rollback_Fence then Evidence_Fenced
      elsif R.Value.State /= Completed then Evaluation_Incomplete
      elsif Failure.Kind /= Absent then Evidence_Fail_Terminal
      elsif R.Value.Outcome /= Passed then Evaluation_Incomplete
      else Ready)
     with Global => null;

   --  Independent complete semantic result equation.  It is not implemented in
   --  terms of Select_Evidence and does not assume its desired postcondition.
   function Result_Conforms
     (A : Byte_Array; H : History; F : Optional_Record; Q : Query; R : Selection)
      return Boolean is
     (if not Query_Complete (Q) then
         R = (Reason => Input_Absent, Head => No_Record,
              Completed_Failure => No_Record)
      elsif not Query_Valid (A, Q) then
         R = (Reason => Input_Invalid, Head => No_Record,
              Completed_Failure => No_Record)
      elsif not Finalization_Valid (A, F, Q) then
         R = (Reason => Finalization_Invalid, Head => No_Record,
              Completed_Failure => No_Record)
      elsif not History_Valid (A, H, F, Q) then
         R = (Reason => History_Invalid, Head => No_Record,
              Completed_Failure => No_Record)
      else
         R.Head = Head_Reference (H, F)
         and then Failure_Reference_Conforms (A, H, F, Q, R.Completed_Failure)
         and then R.Reason =
           Head_Decision (A, Head_Record (H, F), Q, R.Completed_Failure))
     with Global => null;

   function Select_Evidence
     (A : Byte_Array; H : History; F : Optional_Record; Q : Query) return Selection
     with Global => null,
          Post => Result_Conforms (A, H, F, Q, Select_Evidence'Result)
            and then
              (if Select_Evidence'Result.Reason = Ready then
                 Query_Complete (Q) and then Query_Valid (A, Q)
                 and then Finalization_Valid (A, F, Q)
                 and then History_Valid (A, H, F, Q)
                 and then Head_Record (H, F).Present
                 and then Head_Record (H, F).Value.State = Completed
                 and then Head_Record (H, F).Value.Outcome = Passed
                 and then Cursor_Matches (A, Q.Current_Head, Head_Record (H, F).Value)
                 and then Cursor_Matches (A, Q.Prepared_Evidence, Head_Record (H, F).Value)
                 and then Select_Evidence'Result.Completed_Failure.Kind = Absent
                 and then (not F.Present or else
                   not Is_Current_Failure (A, F.Value, Q))
                 and then (for all I in H'Range =>
                   not Is_Current_Failure (A, H (I), Q)));
end Evaluation_History;
