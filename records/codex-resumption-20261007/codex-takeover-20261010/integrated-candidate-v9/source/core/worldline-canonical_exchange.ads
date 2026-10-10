with Worldline.Canonical_Operation;
package Worldline.Canonical_Exchange with SPARK_Mode is
   package K renames Worldline.Canonical_Operation;
   package A renames K.A;
   package R renames A.R;
   package C renames A.C;
   package L renames K.L;
   use type A.Use_State; use type A.Operation; use type A.Decision; use type K.Decision; use type R.Native_State;
   use type Hash; use type K.C.Byte;
   use type R.Historical_Verdict; use type R.Promotion_Mode; use type C.Reason;
   type Phase is (Issued, Worker_Intent, Worker_Observed, Canonical_Intent,
      Effect_Observed, Settled, Aborted, Quarantined);
   type Command is (Advance, Settle_Historical, Replay_Historical, Resolve_Owner);
   type Decision is (Refused, Dispatch_Worker, Record_Worker, Dispatch_Canonical,
      Record_Effect, Settle_Same_Use, Replay_Same_Use, Owner_Record_Abort,
      Owner_Record_Effect);
   type Material is record
      Worker_Issued, Worker_Recovered, Canonical_Issued, Canonical_Recovered : R.Binding;
      Worker_Native, Canonical_Native : R.Native_Observation;
      Worker_Receipt_Genesis, Owner_Receipt_Genesis, Worker_Receipt_Head : R.Optional_Digest;
      Worker_Causal_Genesis, Owner_Causal_Genesis, Worker_Causal_Head : R.Optional_Digest;
      Quarantine_Head : R.Optional_Digest;
   end record;
   -- All mappings and payloads are actual independent native captures. These
   -- value rules confer no custody on a serialized material record. Complete
   -- original packet, peer, writer, issuer and source correspondence remain
   -- mandatory protected producer/full-body/native/cost obligations.
   -- The original checkpoint-return question requires typed absence of its
   -- unused resulting requirement. This complete relation is additive; the
   -- historical V3 all-present relation is retained byte-for-byte.
   function Same_Packet_Binding
     (Data : A.Q.Byte_Array; Left, Right : R.Binding) return Boolean is
     (Left.Mode = Right.Mode
      and then R.Same (Left.Operation, Right.Operation)
      and then R.Same (Left.Transaction, Right.Transaction)
      and then R.Same (Left.Capability, Right.Capability)
      and then R.Same (Left.Universe_Head, Right.Universe_Head)
      and then R.Same (Left.Instance, Right.Instance)
      and then R.Same (Left.Subject, Right.Subject)
      and then R.Same (Left.Staged_Root, Right.Staged_Root)
      and then R.Same (Left.Current_Requirement, Right.Current_Requirement)
      and then (if Left.Mode = R.Checkpoint_Return then
         not Left.Resulting_Requirement.Present
         and then not Right.Resulting_Requirement.Present
         and then Left.Resulting_Requirement.Value = Zero_Hash
         and then Right.Resulting_Requirement.Value = Zero_Hash
       else R.Same (Left.Resulting_Requirement, Right.Resulting_Requirement))
      and then R.Same (Left.Requester, Right.Requester)
      and then R.Same (Left.Grant_Use, Right.Grant_Use)
      and then R.Same (Left.Policy_Identity, Right.Policy_Identity)
      and then R.Same (Left.Selected_Evaluation, Right.Selected_Evaluation)
      and then R.Same (Left.History_Head, Right.History_Head)
      and then R.Same (Left.Reservation, Right.Reservation)
      and then R.Same (Left.Host, Right.Host)
      and then R.Same (Left.Before_Prime, Right.Before_Prime)
      and then R.Same (Left.Before_Root, Right.Before_Root)
      and then R.Same (Left.Before_Mapping, Right.Before_Mapping)
      and then R.Same (Left.Staged_Mapping, Right.Staged_Mapping)
      and then R.Same (Left.Input_Snapshot, Right.Input_Snapshot)
      and then R.Same (Left.Kernel_Build, Right.Kernel_Build)
      and then R.Same (Left.Kernel_Library, Right.Kernel_Library)
      and then R.Same (Left.Kernel_Mapping, Right.Kernel_Mapping)
      and then R.Same (Left.Issuer_Head, Right.Issuer_Head)
      and then R.Same (Left.Receipt_Head, Right.Receipt_Head)
      and then R.Same (Left.Causal_Head, Right.Causal_Head)
      and then R.Same (Data, Left.Policy_Epoch, Right.Policy_Epoch)
      and then R.Same (Data, Left.Resource_Epoch, Right.Resource_Epoch))
     with Global => null;

   function Raw_Matches (Raw : K.C.Raw_Optional_Hash; Id : R.Optional_Digest)
      return Boolean is
     (K.C.Hash_Well_Formed(Raw) and then Raw.Present=1
      and then Id.Present and then K.C.Digest(Raw.Value)=Id.Value)
      with Global=>null;
   function Original_Packet (Collapse : K.C.Raw_Request; M : Material)
      return Boolean is
     (K.C.Well_Formed(Collapse) and then Collapse.Phase=0
      and then Raw_Matches(Collapse.Expected_Subject,M.Worker_Issued.Subject)
      and then Raw_Matches(Collapse.Actual_Staged_Root,M.Worker_Issued.Staged_Root)
      and then Raw_Matches(Collapse.Current_Requirement,M.Worker_Issued.Current_Requirement)
      and then (if M.Worker_Issued.Mode=R.Checkpoint_Return then
        Collapse.Evaluation_Mode=1 and then Collapse.Resulting_Requirement.Present=0
        and then not M.Worker_Issued.Resulting_Requirement.Present
        and then M.Worker_Issued.Resulting_Requirement.Value=Zero_Hash
       else Collapse.Evaluation_Mode=0
        and then Raw_Matches(Collapse.Resulting_Requirement,M.Worker_Issued.Resulting_Requirement)))
      with Global=>null;
   function Joins (Data : A.Q.Byte_Array; B : A.Binding;
      Collapse : K.C.Raw_Request; M : Material) return Boolean is
     (A.Valid(Data,B) and then B.Action in A.Commit_Collapse | A.Commit_Transaction
      and then Same_Packet_Binding(Data,M.Worker_Issued,M.Worker_Recovered)
      and then Same_Packet_Binding(Data,M.Canonical_Issued,M.Canonical_Recovered)
      and then Original_Packet(Collapse,M)
      and then M.Worker_Issued.Mode=M.Canonical_Issued.Mode
      and then R.Same(B.Id(A.Operation_Id),M.Worker_Issued.Operation)
      and then R.Same(B.Id(A.Operation_Id),M.Canonical_Issued.Operation)
      and then R.Same(B.Id(A.Transaction),M.Worker_Issued.Transaction)
      and then R.Same(B.Id(A.Transaction),M.Canonical_Issued.Transaction)
      and then R.Same(B.Id(A.Grant_Id),M.Worker_Issued.Capability)
      and then R.Same(B.Id(A.Grant_Id),M.Canonical_Issued.Capability)
      and then R.Same(B.Id(A.Use_Id),M.Worker_Issued.Grant_Use)
      and then R.Same(B.Id(A.Use_Id),M.Canonical_Issued.Grant_Use)
      and then R.Same(B.Id(A.Reservation),M.Worker_Issued.Reservation)
      and then R.Same(B.Id(A.Reservation),M.Canonical_Issued.Reservation)
      and then R.Same(B.Id(A.Instance),M.Worker_Issued.Instance)
      and then R.Same(B.Id(A.Prime),M.Worker_Issued.Before_Prime)
      and then R.Same(B.Id(A.Requirement),M.Worker_Issued.Current_Requirement)
      and then R.Same(B.Id(A.Input_Snapshot),M.Worker_Issued.Input_Snapshot)
      and then R.Same(B.Id(A.Universe_Head),M.Worker_Issued.Universe_Head)
      and then R.Same(B.Id(A.Universe_Head),M.Canonical_Issued.Universe_Head)
      and then R.Same(B.Id(A.Issuer_Head),M.Worker_Issued.Issuer_Head)
      and then R.Same(B.Id(A.Issuer_Head),M.Canonical_Issued.Issuer_Head)
      and then R.Same(B.Id(A.Kernel_Mapping),M.Worker_Issued.Kernel_Mapping)
      and then R.Same(B.Id(A.Kernel_Mapping),M.Canonical_Issued.Kernel_Mapping)
      and then R.Same(M.Worker_Issued.Instance,M.Canonical_Issued.Instance)
      and then R.Same(M.Worker_Issued.Subject,M.Canonical_Issued.Subject)
      and then R.Same(M.Worker_Issued.Requester,M.Canonical_Issued.Requester)
      and then R.Same(M.Worker_Issued.Staged_Root,M.Canonical_Issued.Staged_Root)
      and then R.Same(M.Worker_Issued.Before_Root,M.Canonical_Issued.Before_Root)
      and then R.Same(M.Worker_Issued.Current_Requirement,M.Canonical_Issued.Current_Requirement)
      and then (if M.Worker_Issued.Mode=R.Checkpoint_Return then
         not M.Canonical_Issued.Resulting_Requirement.Present
         and then M.Canonical_Issued.Resulting_Requirement.Value=Zero_Hash
       else R.Same(M.Worker_Issued.Resulting_Requirement,M.Canonical_Issued.Resulting_Requirement))
      and then R.Same(M.Worker_Issued.Selected_Evaluation,M.Canonical_Issued.Selected_Evaluation)
      and then R.Same(M.Worker_Issued.History_Head,M.Canonical_Issued.History_Head)
      and then R.Same(M.Worker_Issued.Input_Snapshot,M.Canonical_Issued.Input_Snapshot)
      and then R.Same(M.Worker_Issued.Policy_Identity,B.Id(A.Policy))
      and then R.Same(M.Canonical_Issued.Policy_Identity,B.Id(A.Policy))
      and then R.Same(M.Worker_Issued.Kernel_Build,B.Id(A.Kernel_Build))
      and then R.Same(M.Canonical_Issued.Kernel_Build,B.Id(A.Kernel_Build))
      and then R.Same(M.Worker_Issued.Kernel_Library,B.Id(A.Kernel_Library))
      and then R.Same(M.Canonical_Issued.Kernel_Library,B.Id(A.Kernel_Library))
      and then R.Same(Data,M.Worker_Issued.Policy_Epoch,B.Policy_Epoch)
      and then R.Same(Data,M.Canonical_Issued.Policy_Epoch,B.Policy_Epoch)
      and then R.Same(Data,M.Worker_Issued.Resource_Epoch,B.Resource_Epoch)
      and then R.Same(Data,M.Canonical_Issued.Resource_Epoch,B.Resource_Epoch)) with Global=>null;
   function Worker_Chains (M : Material; Receipts, Events : C.Retained_Rows)
      return Boolean is
     (Receipts'Length>0 and then Events'Length>0
      and then C.Replay(C.Receipt_Chain,Receipts,M.Worker_Receipt_Genesis,
         M.Owner_Receipt_Genesis,M.Worker_Receipt_Head).Disposition=C.Ready
      and then C.Replay(C.Causal_Chain,Events,M.Worker_Causal_Genesis,
         M.Owner_Causal_Genesis,M.Worker_Causal_Head).Disposition=C.Ready)
      with Global=>null;
   function Retained_Use(Data : A.Q.Byte_Array; H : A.Uses; B : A.Binding)
      return Boolean is
     (for some I in H'Range => A.Same(Data,H(I).Bound,B)
        and then H(I).State in A.Reserved | A.Effect_Observed | A.Settled | A.Quarantined)
      with Global=>null;
   function Reference(Data : A.Q.Byte_Array; G : A.Grants; H : A.Uses;
      B : A.Binding; Now : A.Q.Quantity; E : A.Evidence;
      State : L.Ledger_State; Rows : L.Row_Array; Observed : L.Native_Array;
      Bound : L.Binding; Requester : L.Identity; Peer : A.Optional_UID;
      Collapse : K.C.Raw_Request; M : Material; Before : Phase; Mode : Command;
      Worker_Receipts, Worker_Events, Effect_Receipts, Effect_Events : C.Retained_Rows)
      return Decision with Global=>null;
   function Decide(Data : A.Q.Byte_Array; G : A.Grants; H : A.Uses;
      B : A.Binding; Now : A.Q.Quantity; E : A.Evidence;
      State : L.Ledger_State; Rows : L.Row_Array; Observed : L.Native_Array;
      Bound : L.Binding; Requester : L.Identity; Peer : A.Optional_UID;
      Collapse : K.C.Raw_Request; M : Material; Before : Phase; Mode : Command;
      Worker_Receipts, Worker_Events, Effect_Receipts, Effect_Events : C.Retained_Rows)
      return Decision with Global=>null,
      Post=>Decide'Result=Reference(Data,G,H,B,Now,E,State,Rows,Observed,Bound,
         Requester,Peer,Collapse,M,Before,Mode,Worker_Receipts,Worker_Events,
         Effect_Receipts,Effect_Events);
end Worldline.Canonical_Exchange;
