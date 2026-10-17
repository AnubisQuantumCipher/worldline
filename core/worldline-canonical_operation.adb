with Worldline.Collapse;
package body Worldline.Canonical_Operation with SPARK_Mode is
   function Reference(Data : A.Q.Byte_Array; G : A.Grants; H : A.Uses;
      B : A.Binding; Now : A.Q.Quantity; E : A.Evidence;
      State : L.Ledger_State; Rows : L.Row_Array; Observed : L.Native_Array;
      Bound : L.Binding; Requester : L.Identity; Peer : A.Optional_UID;
      Collapse : C.Raw_Request) return Decision is
      Empty : A.C.Retained_Rows(1..0);
   begin
      if A.Decide(Data,G,H,B,Now,A.Reserve_Use,E,Empty,Empty)/=A.Reserved_Replay then return Authority_Refused; end if;
      if not L.Conserved(Data,State,Rows) or else not L.Contained(Data,Rows)
        or else not L.Native_Valid(Data,State,Rows,Observed)
        or else not (for some I in Rows'Range => L.Same_Binding(Data,Rows(I).Bound,Bound)
          and then Rows(I).State in L.Reserved | L.Launch_Intent | L.Running)
      then return Resource_Refused; end if;
      if not A.Same(B.Peer,Peer) or else not L.Same(Data,Bound.Owner,Requester)
        or else not Digest_Matches(Data,Bound.Operation,B.Id(A.Operation_Id))
        or else not Digest_Matches(Data,Bound.Capability,B.Id(A.Grant_Id))
        or else not Digest_Matches(Data,Bound.Grant_Use,B.Id(A.Use_Id))
        or else not Digest_Matches(Data,Bound.Reservation,B.Id(A.Reservation))
        or else not Digest_Matches(Data,Bound.Universe_Head,B.Id(A.Universe_Head))
        or else not Digest_Matches(Data,Bound.Workload,B.Id(A.Target))
        or else not Digest_Matches(Data,Bound.Provenance,B.Id(A.Provenance))
        or else not Digest_Matches(Data,State.Scope.Instance,B.Id(A.Instance))
        or else not Digest_Matches(Data,State.Scope.Policy,B.Id(A.Policy))
        or else not A.R.Same(Data,State.Scope.Policy_Epoch,B.Policy_Epoch)
        or else not A.R.Same(Data,Bound.Resource_Epoch,B.Resource_Epoch)
      then return Binding_Mismatch; end if;
      if B.Action in A.Commit_Collapse | A.Commit_Transaction then
         if not C.Well_Formed(Collapse) or else C.Decode(Collapse).Request_Phase/=Worldline.Collapse.Commit
           or else C.Decide_Wire(Collapse)/=C.Byte(Worldline.Collapse.Decision'Pos(Worldline.Collapse.Authorized))
         then return Collapse_Refused; end if;
      end if;
      return Ready;
   end Reference;
   function Decide(Data : A.Q.Byte_Array; G : A.Grants; H : A.Uses;
      B : A.Binding; Now : A.Q.Quantity; E : A.Evidence;
      State : L.Ledger_State; Rows : L.Row_Array; Observed : L.Native_Array;
      Bound : L.Binding; Requester : L.Identity; Peer : A.Optional_UID;
      Collapse : C.Raw_Request) return Decision is
   begin return Reference(Data,G,H,B,Now,E,State,Rows,Observed,Bound,Requester,Peer,Collapse); end Decide;
end Worldline.Canonical_Operation;
