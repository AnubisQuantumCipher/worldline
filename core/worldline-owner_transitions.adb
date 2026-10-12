package body Worldline.Owner_Transitions with SPARK_Mode is
   function Query_For (Q : Request) return E.Query is
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
     with Global => null, Post => E."=" (Query_For'Result, Query_Equation (Q));

   function Retry_Holds
     (A : E.Byte_Array; H : E.History; F : E.Optional_Record; Q : Request)
      return Boolean is
      Query : constant E.Query := Query_For (Q);
      Head : constant E.Optional_Record := E.Head_Record (H, F);
   begin
      return E.Query_Complete (Query) and then E.Query_Valid (A, Query)
        and then E.Finalization_Valid (A, F, Query)
        and then E.History_Valid (A, H, F, Query)
        and then Head.Present and then E.Cursor_Matches (A, Q.Current_Head, Head.Value)
        and then Same_Cursor (A, Q.Current_Head, Q.Grant.Prior_Head)
        and then Latest_Failed_Head (A, H, F, Query, Q.Grant.Failed_Run)
        and then Cursor_Present (A, Q.Attempt)
        and then Same_Cursor (A, Q.Attempt, Q.Grant.Next_Run)
        and then E.Next_Epoch
          (A, Q.Current_Head.Value.Sequence.Value, Q.Attempt.Value.Sequence.Value)
        and then not E.Same_Identity
          (A, E.Identity_Span (Q.Attempt.Value.Run), E.Identity_Span (Head.Value.Run.Value))
        and then (not F.Present or else not F.Value.Run.Present or else
           not E.Same_Identity
             (A, E.Identity_Span (Q.Attempt.Value.Run), E.Identity_Span (F.Value.Run.Value)))
        and then (for all I in H'Range =>
          H (I).Run.Present and then not E.Same_Identity
            (A, E.Identity_Span (Q.Attempt.Value.Run), E.Identity_Span (H (I).Run.Value)));
   end Retry_Holds;

   function Retry_Reference
     (A : E.Byte_Array; H : E.History; F : E.Optional_Record; Q : Request)
      return Decision is
      Query : constant E.Query := Query_For (Q);
      Head : constant E.Optional_Record := E.Head_Record (H, F);
      Result : Decision;
   begin
      if not E.Query_Complete (Query) or else not E.Query_Valid (A, Query)
        or else not E.Finalization_Valid (A, F, Query)
        or else not E.History_Valid (A, H, F, Query)
      then Result := History_Invalid;
      elsif not Head.Present
        or else not E.Cursor_Matches (A, Q.Current_Head, Head.Value)
        or else not Same_Cursor (A, Q.Current_Head, Q.Grant.Prior_Head)
        or else not Latest_Failed_Head (A, H, F, Query, Q.Grant.Failed_Run)
      then Result := Failed_Head_Mismatch;
      elsif not Cursor_Present (A, Q.Attempt)
        or else not Same_Cursor (A, Q.Attempt, Q.Grant.Next_Run)
        or else not E.Next_Epoch
          (A, Q.Current_Head.Value.Sequence.Value, Q.Attempt.Value.Sequence.Value)
        or else E.Same_Identity
          (A, E.Identity_Span (Q.Attempt.Value.Run), E.Identity_Span (Head.Value.Run.Value))
        or else (F.Present and then F.Value.Run.Present and then
           E.Same_Identity
             (A, E.Identity_Span (Q.Attempt.Value.Run), E.Identity_Span (F.Value.Run.Value)))
        or else (for some I in H'Range =>
          not H (I).Run.Present or else E.Same_Identity
            (A, E.Identity_Span (Q.Attempt.Value.Run), E.Identity_Span (H (I).Run.Value)))
      then Result := Attempt_Mismatch;
      else Result := Ready;
      end if;
      return Result;
   end Retry_Reference;

   function Reference
     (A : E.Byte_Array; H : E.History; F : E.Optional_Record; Q : Request)
      return Decision is
   begin
      if not Common_Present (Q) then return Input_Absent;
      elsif not Common_Valid (A, Q) then return Input_Invalid;
      elsif not Same (A, Q.Peer, Q.Owner)
        or else not Same (A, Q.Peer, Q.Grant.Principal) then return Requester_Not_Owner;
      elsif not Same (A, Q.Trusted_Issuer, Q.Grant.Issuer) then return Issuer_Mismatch;
      elsif Q.Grant.State /= Reserved then return Grant_Unavailable;
      elsif Q.Action /= Q.Grant.Action then return Operation_Mismatch;
      elsif not Same (A, Q.Subject, Q.Grant.Subject) then return Subject_Mismatch;
      elsif not Same (A, Q.Content, Q.Grant.Content) then return Content_Mismatch;
      elsif not Same (A, Q.Transaction, Q.Grant.Transaction) then return Transaction_Mismatch;
      elsif not Same (A, Q.Current_Requirement, Q.Grant.Current_Requirement)
        or else not Same (A, Q.Resulting_Requirement, Q.Grant.Expected_Requirement)
        or else (Q.Action = Retry_Evaluation
          and then not Same (A, Q.Current_Requirement, Q.Resulting_Requirement))
      then return Requirement_Mismatch;
      elsif not Present (A, Q.Grant.Reason) or else Q.Grant.Reason.Value.Length = 0
      then return Reason_Absent;
      elsif not Same (A, Q.Grant.Grant, Q.Grant.Issued_Grant)
        or else not Same (A, Q.Grant.Grant, Q.Grant.Reserved_Grant)
        or else not Same (A, Q.Grant.Use_Id, Q.Grant.Reserved_Use)
      then return Reservation_Mismatch;
      elsif not E.Same_Epoch (A, Q.Current_Epoch.Value, Q.Grant.Epoch.Value)
      then return Epoch_Mismatch;
      elsif Q.Action = Retry_Evaluation then return Retry_Reference (A, H, F, Q);
      else return Ready;
      end if;
   end Reference;

   function Authorize
     (A : E.Byte_Array; H : E.History; F : E.Optional_Record; Q : Request)
      return Decision is
   begin
      --  Executable dispatch and contract use the complete relation; independent
      --  proof, protected producer and actual caller controls remain required.
      return Reference (A, H, F, Q);
   end Authorize;
end Worldline.Owner_Transitions;
