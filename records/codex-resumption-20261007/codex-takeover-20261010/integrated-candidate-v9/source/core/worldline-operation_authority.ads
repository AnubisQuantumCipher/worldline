with Interfaces;
with Resource_Quantities;
with Resource_Run_Ledger;
with Worldline.Recovery_Authorization_V3;
with Worldline.Chain_Authority;
with SPARK.Big_Integers;
with Worldline.Archive_Envelope;

-- Distinct WORLDLINE grants. No COSMOGONY Genesis action is enlarged or mapped
-- to these rights. Protected issuer/owner/peer/kernel/resource producers remain
-- responsible for authenticity; this relation is a complete value rule.
package Worldline.Operation_Authority with SPARK_Mode is
   package Q renames Resource_Quantities;
   package R renames Worldline.Recovery_Authorization_V3;
   package C renames Worldline.Chain_Authority;
   use SPARK.Big_Integers;
   use type Q.Byte_Count; use type Q.Ordering; use type Interfaces.Unsigned_32;
   use type C.Reason; use type R.Recovery_Action;
   type Operation is (Ping, Status, List_Worlds, Show_World, Verify_Log, Initialize, Add_Root, Remove_Root, List_Roots, Fork_World, Race_Worlds, Graph, Log, Why, Inspect, Switch, Prepare_Collapse, Commit_Collapse, Commit_Transaction, Abort_Transaction, List_Transactions, Show_Transaction, Prepare_Return, Cancel_Job, Simulate, Doctor, Adapters, Enable_Ghost, Disable_Ghost, Ghost_Status, Run_Ghost, Shell_Info, Prune, Anchor_Status, Revalidate, Validation_Status, Return_Services, Return_Terminals, Return_Windows, Automatic_Ghosts, Resolve_Quarantine);
   type Rights is array (Operation) of Boolean;
   type Identity_Field is (Operation_Id, Request_Id, Transaction, Universe_Head, Instance, Root_Set, Prime, Policy, Requirement, Issuer, Issuer_Head, Grant_Id, Use_Id, Reservation, Resource_Head, Receipt_Genesis, Receipt_Head, Causal_Genesis, Causal_Head, Input_Snapshot, Kernel_Build, Kernel_Library, Kernel_Mapping, Provenance, Target, Quarantine_Head, Original_Operation);
   type Identities is array (Identity_Field) of R.Optional_Digest;
   type Optional_UID is record
      Present : Boolean := False;
      Value : Interfaces.Unsigned_32 := 0;
   end record;
   function Same (L, V : Optional_UID) return Boolean is
     (L.Present and then V.Present and then L.Value = V.Value) with Global => null;
   function Owner_Only (Op : Operation) return Boolean is
     (Op in Initialize | Add_Root | Remove_Root | Switch | Prune | Abort_Transaction | Enable_Ghost | Disable_Ghost | Return_Services | Return_Terminals | Return_Windows | Resolve_Quarantine) with Global => null;
   function Transaction_Operation (Op : Operation) return Boolean is
     (Op in Commit_Collapse | Commit_Transaction | Abort_Transaction |
       Return_Services | Return_Terminals | Return_Windows |
       Resolve_Quarantine) with Global => null;
   type Binding is record
      Action : Operation;
      Id : Identities;
      Peer, Preparer, Owner, Target_Owner : Optional_UID;
      Policy_Epoch, Resource_Epoch : R.Optional_Epoch;
   end record;
   function Valid (Data : Q.Byte_Array; B : Binding) return Boolean is
     (B.Peer.Present and then B.Owner.Present
      and then R.Same (Data, B.Policy_Epoch, B.Policy_Epoch)
      and then R.Same (Data, B.Resource_Epoch, B.Resource_Epoch)
      and then (for all F in Identity_Field =>
        (if F not in Transaction | Prime | Requirement | Quarantine_Head | Original_Operation then B.Id (F).Present))
      and then (if B.Action not in Ping | Status | List_Worlds | Show_World | Verify_Log | Initialize | Add_Root | List_Roots | Graph | Log | Doctor | Adapters | Shell_Info | Anchor_Status | Validation_Status | Automatic_Ghosts then B.Id(Prime).Present and then B.Id(Requirement).Present)
      and then (if Transaction_Operation (B.Action) then B.Id (Transaction).Present)
      and then (if B.Action in Commit_Collapse | Commit_Transaction | Abort_Transaction
                then B.Preparer.Present)
      and then (if Owner_Only (B.Action) then B.Target_Owner.Present)
      and then (if B.Action = Resolve_Quarantine then
        B.Id (Quarantine_Head).Present and then B.Id (Original_Operation).Present)) with Global => null;
   function Same (Data : Q.Byte_Array; L, V : Binding) return Boolean is
     (L.Action = V.Action and then Valid (Data,L) and then Valid (Data,V)
      and then Same (L.Peer,V.Peer) and then Same (L.Owner,V.Owner)
      and then L.Preparer = V.Preparer and then L.Target_Owner = V.Target_Owner
      and then R.Same (Data,L.Policy_Epoch,V.Policy_Epoch)
      and then R.Same (Data,L.Resource_Epoch,V.Resource_Epoch)
      and then (for all F in Identity_Field =>
        L.Id(F).Present = V.Id(F).Present and then
          (if L.Id(F).Present then R.Same (L.Id(F),V.Id(F))))) with Global => null;
   type Grant_State is (Active, Revoked);
   type Grant is record
      Id, Parent, Issuer, Instance, Root_Set, Policy : R.Optional_Digest;
      Subject, Owner : Optional_UID;
      Allowed : Rights;
      State : Grant_State;
      Epoch : R.Optional_Epoch;
      Ceiling, Issued_At, Expires_At : Q.Quantity;
   end record;
   type Grants is array (Q.Byte_Index range <>) of Grant;
   function Grant_Valid (Data : Q.Byte_Array; G : Grant) return Boolean is
     (G.Id.Present and then G.Issuer.Present and then G.Instance.Present
      and then G.Root_Set.Present and then G.Policy.Present
      and then G.Subject.Present and then G.Owner.Present
      and then R.Same (Data,G.Epoch,G.Epoch)
      and then Q.Span_Valid(Data,G.Ceiling) and then not Q.Is_Negative(Data,G.Ceiling)
      and then Q.Span_Valid(Data,G.Issued_At) and then not Q.Is_Negative(Data,G.Issued_At)
      and then Q.Span_Valid(Data,G.Expires_At) and then not Q.Is_Negative(Data,G.Expires_At)
      and then Q.Compare(Data,G.Issued_At,G.Expires_At) = Q.Less
      and then (for all Op in Operation =>
        (if Owner_Only(Op) and then G.Allowed(Op) then Same(G.Subject,G.Owner)))) with Global => null;
   function Attenuates (Data : Q.Byte_Array; Parent, Child : Grant) return Boolean is
     (Grant_Valid(Data,Parent) and then Grant_Valid(Data,Child)
      and then R.Same(Child.Parent,Parent.Id)
      and then R.Same(Child.Issuer,Parent.Issuer)
      and then R.Same(Child.Instance,Parent.Instance)
      and then R.Same(Child.Root_Set,Parent.Root_Set)
      and then R.Same(Child.Policy,Parent.Policy)
      and then Same(Child.Owner,Parent.Owner)
      and then R.Same(Data,Child.Epoch,Parent.Epoch)
      and then (for all Op in Operation => not Child.Allowed(Op) or else Parent.Allowed(Op))
      and then Q.Compare(Data,Child.Ceiling,Parent.Ceiling) in Q.Less | Q.Equal
      and then Q.Compare(Data,Child.Issued_At,Parent.Issued_At) in Q.Equal | Q.Greater
      and then Q.Compare(Data,Child.Expires_At,Parent.Expires_At) in Q.Less | Q.Equal) with Global => null;
   function Roster_Valid (Data : Q.Byte_Array; G : Grants; Issuer : R.Optional_Digest;
                          Owner : Optional_UID) return Boolean is
     (G'Length > 0 and then
      (for all I in G'Range => Grant_Valid(Data,G(I))
       and then R.Same(G(I).Issuer,Issuer) and then Same(G(I).Owner,Owner)
       and then (for all J in G'Range => (if J /= I then not R.Same(G(I).Id,G(J).Id)))
       and then (if G(I).Parent.Present then
          (for some J in G'Range => J < I and then Attenuates(Data,G(J),G(I)))
         else Same(G(I).Subject,Owner)))) with Global => null;
   -- Strict parent-before-child ordering prevents cycles. Every old grant is
   -- retained; revocation is state, not deletion of a lineage component.
   function Ancestor (G : Grants; Ancestor_Id, Child_Id : R.Optional_Digest)
      return Boolean with Global => null;
   type Use_State is (Reserved, Effect_Observed, Settled, Released, Quarantined);
   type Use_Row is record
      Bound : Binding;
      State : Use_State;
   end record;
   type Uses is array (Q.Byte_Index range <>) of Use_Row;
   function Count_Reference (G : Grants; H : Uses; Grant_Id : R.Optional_Digest;
                             Count : Q.Byte_Count) return Valid_Big_Integer is
     (if Count = 0 then To_Big_Integer(0) else
       Count_Reference(G,H,Grant_Id,Count-1) +
       (if Count <= H'Length and then H(H'First+(Count-1)).State /= Released
          and then Ancestor(G,Grant_Id,H(H'First+(Count-1)).Bound.Id(Operation_Authority.Grant_Id))
        then To_Big_Integer(1) else To_Big_Integer(0)))
     with Ghost, Global => null, Subprogram_Variant => (Decreases => Count);
   function Count_Uses (G : Grants; H : Uses; Grant_Id : R.Optional_Digest)
      return Valid_Big_Integer with Global => null,
      Post => Count_Uses'Result = Count_Reference(G,H,Grant_Id,H'Length);
   function Eligible (Data : Q.Byte_Array; G : Grants; H : Uses; B : Binding;
                      Now : Q.Quantity; Additional : Boolean := True) return Boolean with Global => null;
   type Command is (Reserve_Use, Observe_Effect, Settle_Use, Release_Use,
                    Resolve_No_Effect, Resolve_Effect, Replay_Use, Quarantine_Use, Resolve_Recovery, Check_Grants, Authorize_Followup, Authorize_Execution);
   type Decision is (Refused, Reserved_New, Reserved_Replay, Effect_Accepted,
                     Settled_New, Settled_Replay, Released_New, Released_Replay,
                     Resolved_No_Effect, Resolved_Effect, Quarantined_New, Owner_Abort, Owner_Settle, Grants_Valid, Followup_Ready, Execution_Ready);
   function Reservation_Reference
     (Data : Q.Byte_Array; G : Grants; H : Uses; B : Binding; Now : Q.Quantity) return Decision is
     (if not Roster_Valid (Data, G, B.Id (Issuer), B.Owner)
       or else not (for all I in H'Range =>
         Valid (Data, H(I).Bound)
         and then (for some J in G'Range => R.Same (G(J).Id, H(I).Bound.Id (Grant_Id)))
         and then not (for some J in H'Range => J < I
           and then R.Same (H(J).Bound.Id (Operation_Id), H(I).Bound.Id (Operation_Id)))
         and then (if R.Same (H(I).Bound.Id (Operation_Id), B.Id (Operation_Id))
           then Same (Data, H(I).Bound, B)))
      then Refused
      elsif (for some I in H'Range => R.Same (H(I).Bound.Id (Operation_Id), B.Id (Operation_Id)))
      then (if (for some I in H'Range =>
             R.Same (H(I).Bound.Id (Operation_Id), B.Id (Operation_Id))
             and then H(I).State = Reserved)
           and then Eligible (Data, G, H, B, Now, False)
            then Reserved_Replay else Refused)
      else (if Eligible (Data, G, H, B, Now) then Reserved_New else Refused))
     with Ghost, Global => null;
   -- Shared original ReserveUse path, also used to redecide the complete
   -- original reservation observation without recursing through Chain_Effect.
   function Reservation_Decision
     (Data : Q.Byte_Array; G : Grants; H : Uses; B : Binding; Now : Q.Quantity) return Decision
     with Global => null,
       Post => Reservation_Decision'Result = Reservation_Reference (Data, G, H, B, Now);
   type Evidence is record
      Effect_Binding : Binding;
      Actual_Receipt_Root, Actual_Causal_Root : R.Optional_Digest;
      -- An authenticated original native Before/After observation supplies
      -- these bindings. Unknown has typed absence; matching flags cannot.
      No_Effect_Binding : Binding;
      Owner_Resolution : Binding;
      Quarantine_Head, Witnessed_Receipt_Head, Witnessed_Causal_Head : R.Optional_Digest;
      Recovery_Issued, Recovery_Recovered : R.Binding;
      Recovery_Historical : R.Historical_Verdict;
      Recovery_Native : R.Native_Observation;
      Original_Use : R.Optional_Digest;
      -- Original full capture/result and both complete payload rosters. Absence
      -- remains admissible for commands that do not claim an observed effect.
      Effect_Material : Worldline.Archive_Envelope.Span := (1, 0);
   end record;
   function Chain_Effect (Data : Q.Byte_Array; B : Binding; E : Evidence;
                         Receipts, Events : C.Retained_Rows) return Boolean with Global => null;
   -- Follow-up effects consume no new use and cannot issue an exchange. The
   -- original full effect/chain is historical; each selected right is fresh.
   -- Evidence.Owner_Resolution carries the independently captured current
   -- follow-up binding for this command only, never an asserted owner verdict.
   function Followup_Reference (Data : Q.Byte_Array; G : Grants; H : Uses;
      Original, Current : Binding; Now : Q.Quantity; E : Evidence;
      Receipts, Events : C.Retained_Rows) return Boolean is
     (Original.Action in Commit_Collapse | Commit_Transaction
      and then Current.Action in Return_Services | Return_Terminals |
        Return_Windows | Automatic_Ghosts
      and then Valid(Data,Current)
      and then Same(Original.Peer,Current.Peer)
      and then Same(Original.Owner,Current.Owner)
      and then Original.Preparer=Current.Preparer
      and then (for all F in Identity_Field =>
        (if F in Operation_Id | Request_Id | Transaction | Instance | Root_Set |
          Issuer | Grant_Id | Use_Id | Reservation | Kernel_Build | Kernel_Library |
          Kernel_Mapping | Provenance | Target then
          Original.Id(F).Present=Current.Id(F).Present and then
            (if Original.Id(F).Present then R.Same(Original.Id(F),Current.Id(F)))))
      and then Chain_Effect(Data,Original,E,Receipts,Events)
      and then (for some I in H'Range => H(I).State in Effect_Observed | Settled
        and then Same(Data,H(I).Bound,Original))
      and then Eligible(Data,G,H,Current,Now,False)) with Global => null;
   -- Fresh before-exec capability eligibility for the exact existing use. The
   -- separate scoped resource/actor conjunct must redecide the full current
   -- observation and native packet, never a matching event-id or verdict DTO.
   function Execution_Reference(Data : Q.Byte_Array; G : Grants; H : Uses;
      Original, Current : Binding; Now : Q.Quantity) return Boolean is
     (Same(Data,Original,Original) and then Valid(Data,Current)
      and then Original.Action=Current.Action
      and then Same(Original.Peer,Current.Peer)
      and then Same(Original.Owner,Current.Owner)
      and then Original.Preparer=Current.Preparer
      and then Original.Target_Owner=Current.Target_Owner
      and then (for all F in Identity_Field =>
        (if F not in Universe_Head | Issuer_Head | Resource_Head |
          Receipt_Head | Causal_Head then
          Original.Id(F).Present=Current.Id(F).Present and then
            (if Original.Id(F).Present then R.Same(Original.Id(F),Current.Id(F)))))
      and then (for some I in H'Range => H(I).State in Reserved | Effect_Observed | Settled
        and then Same(Data,H(I).Bound,Original))
      and then Eligible(Data,G,H,Current,Now,False)) with Global=>null;
   function Reference (Data : Q.Byte_Array; G : Grants; H : Uses; B : Binding;
                       Now : Q.Quantity; Mode : Command; E : Evidence;
                       Receipts, Events : C.Retained_Rows) return Decision
      with Global => null;
   function Decide (Data : Q.Byte_Array; G : Grants; H : Uses; B : Binding;
                    Now : Q.Quantity; Mode : Command; E : Evidence;
                    Receipts, Events : C.Retained_Rows) return Decision
      with Global => null,
        Post => Decide'Result = Reference(Data,G,H,B,Now,Mode,E,Receipts,Events);
end Worldline.Operation_Authority;
