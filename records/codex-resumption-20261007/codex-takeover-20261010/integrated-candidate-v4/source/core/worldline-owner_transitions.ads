with Evaluation_History;

--  Native owner transitions are distinct from ordinary promotion grants.
--  This value relation owns no issuer, socket, store, clock or effects. The
--  protected producer must authenticate and durably reserve the complete grant
--  before an attempt starts, retaining its reason and failed/head bindings.
package Worldline.Owner_Transitions with SPARK_Mode is
   package E renames Evaluation_History;
   use type E.Byte_Count;
   use type E.Lifecycle;
   use type E.Verdict;

   type Optional_Identity (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : E.Identity_Span;
      end case;
   end record;

   type Operation is (Retry_Evaluation, Adopt_Requirement);
   type Grant_State is (Issued, Reserved, Consumed, Revoked);
   type Owner_Grant is record
      Action : Operation;
      State : Grant_State;
      Grant, Use_Id, Issuer, Principal, Subject, Content, Transaction : Optional_Identity;
      Current_Requirement, Expected_Requirement, Reason : Optional_Identity;
      Failed_Run, Prior_Head, Next_Run : E.Optional_Cursor;
      Epoch : E.Optional_Epoch;
      --  Independent protected issue and reservation records name the same
      --  complete grant/use. Equality here cannot authenticate either record.
      Issued_Grant, Reserved_Grant, Reserved_Use : Optional_Identity;
   end record;

   type Request is record
      Action : Operation;
      --  Actual SO_PEERCRED principal and configured owner are separate reads.
      Peer, Owner, Trusted_Issuer, Subject, Content, Transaction : Optional_Identity;
      Current_Requirement, Resulting_Requirement : Optional_Identity;
      Current_Head, Attempt : E.Optional_Cursor;
      Current_Epoch : E.Optional_Epoch;
      Grant : Owner_Grant;
   end record;

   type Decision is
     (Input_Absent, Input_Invalid, Requester_Not_Owner, Issuer_Mismatch,
      Grant_Unavailable, Operation_Mismatch, Subject_Mismatch,
      Content_Mismatch, Transaction_Mismatch, Requirement_Mismatch, Reason_Absent,
      Reservation_Mismatch, Epoch_Mismatch, History_Invalid,
      Failed_Head_Mismatch, Attempt_Mismatch, Ready);

   function Present (A : E.Byte_Array; I : Optional_Identity) return Boolean is
     (I.Present and then E.Span_Valid (A, I.Value)) with Global => null;
   function Same (A : E.Byte_Array; L, R : Optional_Identity) return Boolean is
     (Present (A, L) and then Present (A, R)
      and then E.Same_Identity (A, L.Value, R.Value)) with Global => null;
   function Cursor_Present (A : E.Byte_Array; C : E.Optional_Cursor)
      return Boolean is
     (C.Present and then C.Value.Sequence.Present
      and then E.Epoch_Valid (A, C.Value.Sequence.Value)
      and then E.Span_Valid (A, E.Identity_Span (C.Value.Run)))
     with Global => null;
   function Same_Cursor (A : E.Byte_Array; L, R : E.Optional_Cursor)
      return Boolean is
     (Cursor_Present (A, L) and then Cursor_Present (A, R)
      and then E.Same_Epoch (A, L.Value.Sequence.Value, R.Value.Sequence.Value)
      and then E.Same_Identity
        (A, E.Identity_Span (L.Value.Run), E.Identity_Span (R.Value.Run)))
     with Global => null;

   function Common_Present (Q : Request) return Boolean is
     (Q.Peer.Present and then Q.Owner.Present and then Q.Trusted_Issuer.Present
      and then Q.Subject.Present and then Q.Content.Present and then Q.Transaction.Present
      and then Q.Current_Requirement.Present and then Q.Resulting_Requirement.Present
      and then Q.Current_Epoch.Present and then Q.Grant.Epoch.Present
      and then Q.Grant.Grant.Present and then Q.Grant.Use_Id.Present
      and then Q.Grant.Issuer.Present and then Q.Grant.Principal.Present
      and then Q.Grant.Subject.Present and then Q.Grant.Content.Present and then Q.Grant.Transaction.Present
      and then Q.Grant.Current_Requirement.Present
      and then Q.Grant.Expected_Requirement.Present
      and then Q.Grant.Issued_Grant.Present
      and then Q.Grant.Reserved_Grant.Present and then Q.Grant.Reserved_Use.Present)
     with Global => null;
   function Common_Valid (A : E.Byte_Array; Q : Request) return Boolean is
     (Present (A, Q.Peer) and then Present (A, Q.Owner)
      and then Present (A, Q.Trusted_Issuer) and then Present (A, Q.Subject)
      and then Present (A, Q.Content) and then Present (A, Q.Transaction)
      and then Present (A, Q.Current_Requirement)
      and then Present (A, Q.Resulting_Requirement)
      and then Q.Current_Epoch.Present and then Q.Grant.Epoch.Present
      and then E.Epoch_Valid (A, Q.Current_Epoch.Value)
      and then E.Epoch_Valid (A, Q.Grant.Epoch.Value)
      and then Present (A, Q.Grant.Grant) and then Present (A, Q.Grant.Use_Id)
      and then Present (A, Q.Grant.Issuer) and then Present (A, Q.Grant.Principal)
      and then Present (A, Q.Grant.Subject) and then Present (A, Q.Grant.Content)
      and then Present (A, Q.Grant.Transaction)
      and then Present (A, Q.Grant.Current_Requirement)
      and then Present (A, Q.Grant.Expected_Requirement)
      and then Present (A, Q.Grant.Issued_Grant)
      and then Present (A, Q.Grant.Reserved_Grant)
      and then Present (A, Q.Grant.Reserved_Use)) with Global => null;

   function Latest_Failed_Head
     (A : E.Byte_Array; H : E.History; F : E.Optional_Record;
      Query : E.Query; C : E.Optional_Cursor) return Boolean is
     (Cursor_Present (A, C)
      and then
        ((F.Present and then E.Is_Current_Failure (A, F.Value, Query)
          and then E.Cursor_Matches (A, C, F.Value)
          and then (for all I in H'Range =>
                      not E.Is_Current_Failure (A, H (I), Query)))
         or else
          (for some I in H'Range =>
             E.Is_Current_Failure (A, H (I), Query)
             and then E.Cursor_Matches (A, C, H (I))
             and then (for all J in H'Range =>
               (if J > I then not E.Is_Current_Failure (A, H (J), Query))))))
     with Global => null;

   function Query_Equation (Q : Request) return E.Query is
     (Subject => (if Q.Subject.Present
                    then (Present => True, Value => E.Subject_Id (Q.Subject.Value))
                    else (Present => False)),
      Content => (if Q.Content.Present
                    then (Present => True, Value => E.Content_Id (Q.Content.Value))
                    else (Present => False)),
      Requirement => (if Q.Current_Requirement.Present
                    then (Present => True, Value => E.Requirement_Id (Q.Current_Requirement.Value))
                    else (Present => False)),
      Current_Head => Q.Current_Head, Prepared_Evidence => Q.Current_Head)
     with Ghost, Global => null;

   function Retry_Equation
     (A : E.Byte_Array; H : E.History; F : E.Optional_Record; Q : Request)
      return Boolean is
     (E.Query_Complete (Query_Equation (Q)) and then E.Query_Valid (A, Query_Equation (Q))
        and then E.Finalization_Valid (A, F, Query_Equation (Q))
        and then E.History_Valid (A, H, F, Query_Equation (Q))
        and then E.Head_Record (H, F).Present and then E.Cursor_Matches (A, Q.Current_Head, E.Head_Record (H, F).Value)
        and then Same_Cursor (A, Q.Current_Head, Q.Grant.Prior_Head)
        and then Latest_Failed_Head (A, H, F, Query_Equation (Q), Q.Grant.Failed_Run)
        and then Cursor_Present (A, Q.Attempt)
        and then Same_Cursor (A, Q.Attempt, Q.Grant.Next_Run)
        and then E.Next_Epoch
          (A, Q.Current_Head.Value.Sequence.Value, Q.Attempt.Value.Sequence.Value)
        and then not E.Same_Identity
          (A, E.Identity_Span (Q.Attempt.Value.Run), E.Identity_Span (E.Head_Record (H, F).Value.Run.Value))
        and then (not F.Present or else not F.Value.Run.Present or else
           not E.Same_Identity
             (A, E.Identity_Span (Q.Attempt.Value.Run), E.Identity_Span (F.Value.Run.Value)))
        and then (for all I in H'Range =>
          H (I).Run.Present and then not E.Same_Identity
            (A, E.Identity_Span (Q.Attempt.Value.Run), E.Identity_Span (H (I).Run.Value)))) with Ghost, Global => null;

   function Retry_Holds
     (A : E.Byte_Array; H : E.History; F : E.Optional_Record; Q : Request)
      return Boolean with Global => null,
        Post => Retry_Holds'Result = Retry_Equation (A, H, F, Q);
   function Retry_Reference
     (A : E.Byte_Array; H : E.History; F : E.Optional_Record; Q : Request)
      return Decision with Global => null,
        Post => (Retry_Reference'Result = Ready) = Retry_Holds (A, H, F, Q);
   function Reference
     (A : E.Byte_Array; H : E.History; F : E.Optional_Record; Q : Request)
      return Decision with Global => null,
        Post => (if Reference'Result = Ready then
           Same (A, Q.Peer, Q.Owner)
           and then Same (A, Q.Peer, Q.Grant.Principal)
           and then Same (A, Q.Trusted_Issuer, Q.Grant.Issuer)
           and then Same (A, Q.Subject, Q.Grant.Subject)
           and then Same (A, Q.Content, Q.Grant.Content)
           and then Same (A, Q.Transaction, Q.Grant.Transaction)
           and then Same (A, Q.Current_Requirement, Q.Grant.Current_Requirement)
           and then Q.Grant.State = Reserved
           and then Q.Action = Q.Grant.Action
           and then Same (A, Q.Resulting_Requirement, Q.Grant.Expected_Requirement)
           and then (if Q.Action = Retry_Evaluation then Retry_Holds (A, H, F, Q)));
   function Authorize
     (A : E.Byte_Array; H : E.History; F : E.Optional_Record; Q : Request)
      return Decision
     with Global => null,
       Post => Authorize'Result = Reference (A, H, F, Q)
         and then (if Authorize'Result = Ready then
           Same (A, Q.Peer, Q.Owner)
           and then Same (A, Q.Peer, Q.Grant.Principal)
           and then Same (A, Q.Trusted_Issuer, Q.Grant.Issuer)
           and then Same (A, Q.Subject, Q.Grant.Subject)
           and then Same (A, Q.Content, Q.Grant.Content)
           and then Same (A, Q.Transaction, Q.Grant.Transaction)
           and then Same (A, Q.Current_Requirement, Q.Grant.Current_Requirement)
           and then Q.Grant.State = Reserved
           and then Q.Action = Q.Grant.Action
           and then Same (A, Q.Resulting_Requirement, Q.Grant.Expected_Requirement)
           and then (if Q.Action = Retry_Evaluation then Retry_Holds (A, H, F, Q)));
end Worldline.Owner_Transitions;
