package body Worldline.Canonical_Exchange with SPARK_Mode is
   function Reference(Data : A.Q.Byte_Array; G : A.Grants; H : A.Uses;
      B : A.Binding; Now : A.Q.Quantity; E : A.Evidence;
      State : L.Ledger_State; Rows : L.Row_Array; Observed : L.Native_Array;
      Bound : L.Binding; Requester : L.Identity; Peer : A.Optional_UID;
      Collapse : K.C.Raw_Request; M : Material; Before : Phase; Mode : Command;
      Worker_Receipts, Worker_Events, Effect_Receipts, Effect_Events : C.Retained_Rows)
      return Decision is
      Worker : constant R.Native_State:=R.Classify_Native(M.Worker_Issued,M.Worker_Native);
      Root : constant R.Native_State:=R.Classify_Native(M.Canonical_Issued,M.Canonical_Native);
      History : constant Boolean:=Worker_Chains(M,Worker_Receipts,Worker_Events);
   begin
      if not Joins(Data,B,Collapse,M) or else not Retained_Use(Data,H,B)
        or else Worker=R.Uncertain or else Root=R.Uncertain then return Refused; end if;
      if Mode=Resolve_Owner then
         -- K4 is a separate reserved native owner operation. It cannot dispatch
         -- either exchange or turn a split/unknown pair into observed success.
         if Before/=Quarantined or else E.Owner_Resolution.Action/=A.Resolve_Quarantine
           or else not R.Same(E.Owner_Resolution.Id(A.Original_Operation),B.Id(A.Operation_Id))
           or else not R.Same(E.Owner_Resolution.Id(A.Transaction),B.Id(A.Transaction))
           or else not R.Same(E.Owner_Resolution.Id(A.Quarantine_Head),M.Quarantine_Head)
           or else not (for some I in H'Range => H(I).State=A.Reserved
             and then A.Same(Data,H(I).Bound,E.Owner_Resolution))
           or else not A.Eligible(Data,G,H,E.Owner_Resolution,Now,False)
         then return Refused; end if;
         if Worker=R.Before_Effect and then Root=R.Before_Effect then return Owner_Record_Abort;
         elsif Worker=R.After_Effect and then Root=R.After_Effect and then History
         then return Owner_Record_Effect;
         else return Refused; end if;
      end if;
      if Before in Effect_Observed | Settled and then Worker=R.After_Effect
        and then Root=R.After_Effect and then History then
         -- Fresh denied/revoked policy is intentionally not read here. The
         -- full original native use and actual effect chains are redecided.
         if Mode=Settle_Historical and then
           A.Decide(Data,G,H,B,Now,A.Settle_Use,E,Effect_Receipts,Effect_Events)
             in A.Settled_New | A.Settled_Replay then return Settle_Same_Use;
         elsif Mode=Replay_Historical and then Before=Settled and then
           A.Decide(Data,G,H,B,Now,A.Replay_Use,E,Effect_Receipts,Effect_Events)=A.Settled_Replay
         then return Replay_Same_Use; end if;
      end if;
      if Mode/=Advance then return Refused; end if;
      if Before=Worker_Intent and then Worker=R.After_Effect and then Root=R.Before_Effect
        and then History then return Record_Worker;
      elsif Before=Canonical_Intent and then Worker=R.After_Effect and then Root=R.After_Effect
        and then History then return Record_Effect;
      end if;
      -- Only a fresh complete native authority/resource/peer/collapse
      -- conjunction can dispatch. Neither recovery nor a receipt does so.
      if K.Decide(Data,G,H,B,Now,E,State,Rows,Observed,Bound,Requester,Peer,Collapse)/=K.Ready then return Refused; end if;
      if Before=Issued and then Worker=R.Before_Effect and then Root=R.Before_Effect then return Dispatch_Worker;
      elsif Before=Worker_Observed and then Worker=R.After_Effect and then Root=R.Before_Effect and then History
      then return Dispatch_Canonical;
      else return Refused; end if;
   end Reference;
   function Decide(Data : A.Q.Byte_Array; G : A.Grants; H : A.Uses;
      B : A.Binding; Now : A.Q.Quantity; E : A.Evidence;
      State : L.Ledger_State; Rows : L.Row_Array; Observed : L.Native_Array;
      Bound : L.Binding; Requester : L.Identity; Peer : A.Optional_UID;
      Collapse : K.C.Raw_Request; M : Material; Before : Phase; Mode : Command;
      Worker_Receipts, Worker_Events, Effect_Receipts, Effect_Events : C.Retained_Rows)
      return Decision is
   begin return Reference(Data,G,H,B,Now,E,State,Rows,Observed,Bound,Requester,Peer,
      Collapse,M,Before,Mode,Worker_Receipts,Worker_Events,Effect_Receipts,Effect_Events); end Decide;
end Worldline.Canonical_Exchange;
