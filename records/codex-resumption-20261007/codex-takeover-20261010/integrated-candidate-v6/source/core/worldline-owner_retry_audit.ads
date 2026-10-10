with Evaluation_History;
with Worldline.Owner_Transitions;

--  Additive owner retry evidence relation. The original default FAIL veto is
--  unchanged. These values do not authenticate their producer or journal.
package Worldline.Owner_Retry_Audit with SPARK_Mode is
   package E renames Evaluation_History;
   package K renames Worldline.Owner_Transitions;
   use type E.Byte_Count;
   use type E.Lifecycle;
   use type E.Verdict;
   use type K.Decision;
   use type K.Operation;
   use type K.Grant_State;
   type Use_Receipt is record
      Consumed : K.Owner_Grant;
      Issued_Event, Reserved_Event, Consumed_Event : K.Optional_Identity;
      Consumed_Issue, Consumed_Reservation : K.Optional_Identity;
   end record;
   type Audit is record
      Before_Request : K.Request;
      Receipt : Use_Receipt;
      Current_Head, Prepared_Evidence : E.Optional_Cursor;
      Current_Epoch : E.Optional_Epoch;
   end record;
   type Decision is (Input_Invalid, Before_Not_Authorized, Prefix_Changed,
      After_Invalid, Attempt_Not_Completed_Pass, Use_Not_Consumed,
      Current_Binding_Changed, Ready);
   function Query_For (Q : K.Request; Head : E.Optional_Cursor) return E.Query
     with Global => null;
   function Same_Row (A : E.Byte_Array; L, R : E.Evaluation_Record)
      return Boolean with Global => null;
   function Same_Finalization (A : E.Byte_Array; L, R : E.Optional_Record)
      return Boolean is
     (L.Present = R.Present and then
        (not L.Present or else Same_Row (A, L.Value, R.Value)))
     with Global => null;
   function Same_Prefix (A : E.Byte_Array; Before, After : E.History)
      return Boolean is
     (After'Length > 0 and then Before'Length = After'Length - 1
      and then (for all I in Before'Range => Same_Row
        (A, Before (I), After (After'First + (I - Before'First)))))
     with Global => null;
   function Same_Grant (A : E.Byte_Array; L, R : K.Owner_Grant)
      return Boolean with Global => null;
   function Receipt_Holds (A : E.Byte_Array; Reserved : K.Owner_Grant;
      Receipt : Use_Receipt) return Boolean is
     (Reserved.State = K.Reserved and then Receipt.Consumed.State = K.Consumed
      and then Same_Grant (A, Reserved, Receipt.Consumed)
      and then K.Present (A, Receipt.Issued_Event)
      and then Receipt.Issued_Event.Value.Length > 0
      and then K.Present (A, Receipt.Reserved_Event)
      and then Receipt.Reserved_Event.Value.Length > 0
      and then K.Present (A, Receipt.Consumed_Event)
      and then Receipt.Consumed_Event.Value.Length > 0
      and then not K.Same (A, Receipt.Issued_Event, Receipt.Reserved_Event)
      and then not K.Same (A, Receipt.Reserved_Event, Receipt.Consumed_Event)
      and then not K.Same (A, Receipt.Issued_Event, Receipt.Consumed_Event)
      and then K.Same (A, Receipt.Issued_Event, Receipt.Consumed_Issue)
      and then K.Same (A, Receipt.Reserved_Event, Receipt.Consumed_Reservation))
     with Global => null;
   function Attempt_Holds (A : E.Byte_Array; After : E.History;
      Q : K.Request) return Boolean is
     (After'Length > 0 and then After (After'Last).State = E.Completed
      and then After (After'Last).Outcome = E.Passed
      and then E.Cursor_Matches (A, Q.Attempt, After (After'Last))
      and then After (After'Last).Requirement.Present
      and then Q.Current_Requirement.Present
      and then E.Same_Identity (A,
        E.Identity_Span (After (After'Last).Requirement.Value),
        Q.Current_Requirement.Value))
     with Global => null;
   function Binding_Holds (A : E.Byte_Array; After : E.History;
      Q : Audit) return Boolean is
     (After'Length > 0
      and then K.Same_Cursor (A, Q.Current_Head, Q.Before_Request.Attempt)
      and then K.Same_Cursor (A, Q.Prepared_Evidence, Q.Before_Request.Attempt)
      and then E.Cursor_Matches (A, Q.Current_Head, After (After'Last))
      and then Q.Current_Epoch.Present
      and then Q.Before_Request.Current_Epoch.Present
      and then E.Same_Epoch (A, Q.Current_Epoch.Value,
        Q.Before_Request.Current_Epoch.Value)) with Global => null;
   function Before_Closed (Before : E.History; F : E.Optional_Record) return Boolean is
     ((not F.Present or else F.Value.State = E.Completed)
      and then (for all J in Before'Range => Before (J).State = E.Completed))
     with Global => null;
   function Holds (A : E.Byte_Array; Before, After : E.History;
      Before_Final, After_Final : E.Optional_Record; Q : Audit)
      return Boolean is
     (Q.Before_Request.Action = K.Retry_Evaluation
      and then Before_Closed (Before, Before_Final)
      and then K.Reference (A, Before, Before_Final, Q.Before_Request) = K.Ready
      and then Same_Finalization (A, Before_Final, After_Final)
      and then Same_Prefix (A, Before, After)
      and then E.Query_Complete (Query_For (Q.Before_Request, Q.Current_Head))
      and then E.Query_Valid (A, Query_For (Q.Before_Request, Q.Current_Head))
      and then E.Finalization_Valid (A, After_Final,
        Query_For (Q.Before_Request, Q.Current_Head))
      and then E.History_Valid (A, After, After_Final,
        Query_For (Q.Before_Request, Q.Current_Head))
      and then Attempt_Holds (A, After, Q.Before_Request)
      and then Receipt_Holds (A, Q.Before_Request.Grant, Q.Receipt)
      and then Binding_Holds (A, After, Q)) with Global => null;
   function Reference (A : E.Byte_Array; Before, After : E.History;
      Before_Final, After_Final : E.Optional_Record; Q : Audit)
      return Decision with Global => null,
      Post => (Reference'Result = Ready) = Holds
        (A, Before, After, Before_Final, After_Final, Q);
   function Decide (A : E.Byte_Array; Before, After : E.History;
      Before_Final, After_Final : E.Optional_Record; Q : Audit)
      return Decision with Global => null,
      Post => Decide'Result = Reference
        (A, Before, After, Before_Final, After_Final, Q)
        and then (Decide'Result = Ready) = Holds
          (A, Before, After, Before_Final, After_Final, Q);
end Worldline.Owner_Retry_Audit;
