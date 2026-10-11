package body Worldline.Owner_Retry_Audit with SPARK_Mode is
   function Query_For (Q : K.Request; Head : E.Optional_Cursor) return E.Query is
     (Subject => (if Q.Subject.Present then
        (Present => True, Value => E.Subject_Id (Q.Subject.Value))
        else (Present => False)),
      Content => (if Q.Content.Present then
        (Present => True, Value => E.Content_Id (Q.Content.Value))
        else (Present => False)),
      Requirement => (if Q.Current_Requirement.Present then
        (Present => True, Value => E.Requirement_Id (Q.Current_Requirement.Value))
        else (Present => False)), Current_Head => Head, Prepared_Evidence => Head);
   function Same_Row (A : E.Byte_Array; L, R : E.Evaluation_Record)
      return Boolean is
     (L.Subject.Present = R.Subject.Present
      and then (not L.Subject.Present or else E.Same_Identity (A,
        E.Identity_Span (L.Subject.Value), E.Identity_Span (R.Subject.Value)))
      and then L.Content.Present = R.Content.Present
      and then (not L.Content.Present or else E.Same_Identity (A,
        E.Identity_Span (L.Content.Value), E.Identity_Span (R.Content.Value)))
      and then L.Requirement.Present = R.Requirement.Present
      and then (not L.Requirement.Present or else E.Same_Identity (A,
        E.Identity_Span (L.Requirement.Value), E.Identity_Span (R.Requirement.Value)))
      and then L.Run.Present = R.Run.Present
      and then (not L.Run.Present or else E.Same_Identity (A,
        E.Identity_Span (L.Run.Value), E.Identity_Span (R.Run.Value)))
      and then L.Sequence.Present = R.Sequence.Present
      and then (not L.Sequence.Present or else
        E.Same_Epoch (A, L.Sequence.Value, R.Sequence.Value))
      and then L.State = R.State and then L.Outcome = R.Outcome);
   function Same_Grant (A : E.Byte_Array; L, R : K.Owner_Grant)
      return Boolean is
     (L.Action = R.Action and then K.Same (A, L.Grant, R.Grant)
      and then K.Same (A, L.Use_Id, R.Use_Id)
      and then K.Same (A, L.Issuer, R.Issuer)
      and then K.Same (A, L.Principal, R.Principal)
      and then K.Same (A, L.Subject, R.Subject)
      and then K.Same (A, L.Content, R.Content)
      and then K.Same (A, L.Transaction, R.Transaction)
      and then K.Same (A, L.Current_Requirement, R.Current_Requirement)
      and then K.Same (A, L.Expected_Requirement, R.Expected_Requirement)
      and then K.Same (A, L.Reason, R.Reason)
      and then K.Same (A, L.Issued_Grant, R.Issued_Grant)
      and then K.Same (A, L.Reserved_Grant, R.Reserved_Grant)
      and then K.Same (A, L.Reserved_Use, R.Reserved_Use)
      and then L.Failed_Run.Present = R.Failed_Run.Present
      and then (not L.Failed_Run.Present or else
        K.Same_Cursor (A, L.Failed_Run, R.Failed_Run))
      and then L.Prior_Head.Present = R.Prior_Head.Present
      and then (not L.Prior_Head.Present or else
        K.Same_Cursor (A, L.Prior_Head, R.Prior_Head))
      and then L.Next_Run.Present = R.Next_Run.Present
      and then (not L.Next_Run.Present or else
        K.Same_Cursor (A, L.Next_Run, R.Next_Run))
      and then L.Epoch.Present and then R.Epoch.Present
      and then E.Same_Epoch (A, L.Epoch.Value, R.Epoch.Value));
   function Reference (A : E.Byte_Array; Before, After : E.History;
      Before_Final, After_Final : E.Optional_Record; Q : Audit)
      return Decision is
      Query : constant E.Query := Query_For (Q.Before_Request, Q.Current_Head);
   begin
      if Q.Before_Request.Action /= K.Retry_Evaluation
        or else not Before_Closed (Before, Before_Final)
        or else K.Authorize (A, Before, Before_Final, Q.Before_Request) /= K.Ready
      then return Before_Not_Authorized;
      elsif not Same_Finalization (A, Before_Final, After_Final)
        or else not Same_Prefix (A, Before, After) then return Prefix_Changed;
      elsif not E.Query_Complete (Query) or else not E.Query_Valid (A, Query)
        or else not E.Finalization_Valid (A, After_Final, Query)
        or else not E.History_Valid (A, After, After_Final, Query)
      then return After_Invalid;
      elsif not Attempt_Holds (A, After, Q.Before_Request)
      then return Attempt_Not_Completed_Pass;
      elsif not Receipt_Holds (A, Q.Before_Request.Grant, Q.Receipt)
      then return Use_Not_Consumed;
      elsif not Binding_Holds (A, After, Q)
      then return Current_Binding_Changed;
      else return Ready;
      end if;
   end Reference;
   function Decide (A : E.Byte_Array; Before, After : E.History;
      Before_Final, After_Final : E.Optional_Record; Q : Audit)
      return Decision is
   begin return Reference (A, Before, After, Before_Final, After_Final, Q); end Decide;
end Worldline.Owner_Retry_Audit;
