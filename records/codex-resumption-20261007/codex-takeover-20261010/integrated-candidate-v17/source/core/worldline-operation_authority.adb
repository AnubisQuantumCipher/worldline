with Worldline.Operation_Result_Relations;
package body Worldline.Operation_Authority with SPARK_Mode is
   function Ancestor (G : Grants; Ancestor_Id, Child_Id : R.Optional_Digest)
      return Boolean is
      Current : R.Optional_Digest := Child_Id;
      Limit : Q.Byte_Count := G'Length;
   begin
      while Limit > 0 loop
         pragma Loop_Invariant (Limit <= G'Length);
         pragma Loop_Variant (Decreases => Limit);
         if R.Same(Current,Ancestor_Id) then return True; end if;
         declare
            Found : Boolean := False;
         begin
            for I in G'Range loop
               if I-G'First < Limit and then R.Same(G(I).Id,Current) then
                  Current := G(I).Parent;
                  Limit := I-G'First;
                  Found := True;
                  exit;
               end if;
            end loop;
            if not Found then return False; end if;
         end;
      end loop;
      return R.Same(Current,Ancestor_Id);
   end Ancestor;
   function Count_Uses (G : Grants; H : Uses; Grant_Id : R.Optional_Digest)
      return Valid_Big_Integer is
      Count : Q.Byte_Count := 0;
      Total : Valid_Big_Integer := To_Big_Integer(0);
   begin
      while Count < H'Length loop
         pragma Loop_Invariant (Count <= H'Length);
         pragma Loop_Invariant (Total = Count_Reference(G,H,Grant_Id,Count));
         pragma Loop_Variant (Decreases => Q.Byte_Count(H'Length)-Count);
         if H(H'First+Count).State /= Released and then
            Ancestor(G,Grant_Id,H(H'First+Count).Bound.Id(Operation_Authority.Grant_Id))
         then Total := Total+To_Big_Integer(1); end if;
         Count := Count+1;
      end loop;
      return Total;
   end Count_Uses;
   function Eligible (Data : Q.Byte_Array; G : Grants; H : Uses; B : Binding;
                      Now : Q.Quantity; Additional : Boolean := True) return Boolean is
   begin
      if not Valid(Data,B) or else not Roster_Valid(Data,G,B.Id(Issuer),B.Owner)
        or else not Q.Span_Valid(Data,Now) or else Q.Is_Negative(Data,Now)
        or else (Owner_Only(B.Action) and then
          (not Same(B.Peer,B.Owner) or else not Same(B.Target_Owner,B.Owner)))
        or else (B.Action in Commit_Collapse | Commit_Transaction | Abort_Transaction
          and then not Same(B.Peer,B.Preparer))
      then return False; end if;
      if not (for some I in G'Range => R.Same(G(I).Id,B.Id(Grant_Id))
          and then Same(G(I).Subject,B.Peer) and then G(I).Allowed(B.Action))
      then return False; end if;
      for I in G'Range loop
         if Ancestor(G,G(I).Id,B.Id(Grant_Id)) then
            if G(I).State /= Active or else not G(I).Allowed(B.Action)
              or else not R.Same(G(I).Instance,B.Id(Instance))
              or else not R.Same(G(I).Root_Set,B.Id(Root_Set))
              or else not R.Same(G(I).Policy,B.Id(Policy))
              or else not R.Same(Data,G(I).Epoch,B.Policy_Epoch)
              or else Q.Compare(Data,Now,G(I).Issued_At) not in Q.Equal | Q.Greater
              or else Q.Compare(Data,Now,G(I).Expires_At) /= Q.Less
              or else Resource_Run_Ledger.Exact_Value(Data,G(I).Ceiling)
                < Count_Uses(G,H,G(I).Id) + (if Additional then To_Big_Integer(1) else To_Big_Integer(0))
            then return False; end if;
         end if;
      end loop;
      return True;
   end Eligible;
   function Chain_Effect (Data : Q.Byte_Array; B : Binding; E : Evidence;
                         Receipts, Events : C.Retained_Rows) return Boolean is
     (Same(Data,B,E.Effect_Binding)
      and then Operation_Result_Relations.Matches
        (Data, B, E, Receipts, Events)
      and then Receipts'Length > 0 and then Events'Length > 0
      and then (R.Same(B.Id(Receipt_Head),B.Id(Receipt_Genesis)) or else
         (for some I in Receipts'Range => R.Same(Receipts(I).Stored_Head,B.Id(Receipt_Head))))
      and then (R.Same(B.Id(Causal_Head),B.Id(Causal_Genesis)) or else
         (for some I in Events'Range => R.Same(Events(I).Stored_Head,B.Id(Causal_Head))))
      and then (for some I in Receipts'Range =>
        R.Same(E.Actual_Receipt_Root,Receipts(I).Actual_Payload_Root))
      and then (for some I in Events'Range =>
        R.Same(E.Actual_Causal_Root,Events(I).Actual_Payload_Root))
      and then C.Replay(C.Receipt_Chain,Receipts,B.Id(Receipt_Genesis),
             E.Effect_Binding.Id(Receipt_Genesis),E.Witnessed_Receipt_Head).Disposition=C.Ready
      and then C.Replay(C.Causal_Chain,Events,B.Id(Causal_Genesis),
             E.Effect_Binding.Id(Causal_Genesis),E.Witnessed_Causal_Head).Disposition=C.Ready);
   function Reservation_Decision
     (Data : Q.Byte_Array; G : Grants; H : Uses; B : Binding; Now : Q.Quantity) return Decision is
      Found : Boolean := False;
      State : Use_State := Quarantined;
   begin
      if not Roster_Valid(Data,G,B.Id(Issuer),B.Owner) then return Refused; end if;
      for I in H'Range loop
         if not Valid(Data,H(I).Bound) or else
           not (for some J in G'Range => R.Same(G(J).Id,H(I).Bound.Id(Grant_Id))) or else
           (for some J in H'Range => J < I and then
             R.Same(H(J).Bound.Id(Operation_Id),H(I).Bound.Id(Operation_Id)))
         then return Refused; end if;
         if R.Same(H(I).Bound.Id(Operation_Id),B.Id(Operation_Id)) then
            if not Same(Data,H(I).Bound,B) then return Refused; end if;
            Found := True; State := H(I).State;
         end if;
         pragma Loop_Invariant (for all K in H'First .. I =>
           Valid(Data,H(K).Bound)
           and then (for some J in G'Range => R.Same(G(J).Id,H(K).Bound.Id(Grant_Id)))
           and then not (for some J in H'Range => J < K and then
             R.Same(H(J).Bound.Id(Operation_Id),H(K).Bound.Id(Operation_Id)))
           and then (if R.Same(H(K).Bound.Id(Operation_Id),B.Id(Operation_Id))
             then Same(Data,H(K).Bound,B)));
         pragma Loop_Invariant (Found =
           (for some K in H'First .. I => R.Same(H(K).Bound.Id(Operation_Id),B.Id(Operation_Id))));
         pragma Loop_Invariant (if Found then
           (for some K in H'First .. I => R.Same(H(K).Bound.Id(Operation_Id),B.Id(Operation_Id))
             and then H(K).State=State));
      end loop;
      if Found then
         return (if State=Reserved and then Eligible(Data,G,H,B,Now,False)
                 then Reserved_Replay else Refused);
      end if;
      return (if Eligible(Data,G,H,B,Now) then Reserved_New else Refused);
   end Reservation_Decision;
   function Reference (Data : Q.Byte_Array; G : Grants; H : Uses; B : Binding;
                       Now : Q.Quantity; Mode : Command; E : Evidence;
                       Receipts, Events : C.Retained_Rows) return Decision is
      Found : Boolean := False;
      State : Use_State := Quarantined;
   begin
      -- Pure source/owner-package data validation. This result is not an
      -- issuance event and grants no operation or installation permission.
      if Mode=Check_Grants then
         return (if Roster_Valid(Data,G,B.Id(Issuer),B.Owner) then Grants_Valid else Refused);
      end if;
      if Mode=Reserve_Use then return Reservation_Decision (Data,G,H,B,Now); end if;
      if not Roster_Valid(Data,G,B.Id(Issuer),B.Owner) then return Refused; end if;
      -- Complete retained operation roster; no duplicate or changed row may
      -- borrow an existing reservation. Release never erases its history.
      for I in H'Range loop
         if not Valid(Data,H(I).Bound) or else
           not (for some J in G'Range => R.Same(G(J).Id,H(I).Bound.Id(Grant_Id))) or else
           (for some J in H'Range => J < I and then
             R.Same(H(J).Bound.Id(Operation_Id),H(I).Bound.Id(Operation_Id)))
         then return Refused; end if;
         if R.Same(H(I).Bound.Id(Operation_Id),B.Id(Operation_Id)) then
            if not Same(Data,H(I).Bound,B) then return Refused; end if;
            Found := True; State := H(I).State;
         end if;
      end loop;
      if not Found then return Refused; end if;
      case Mode is
         when Authorize_Execution =>
            -- The authenticated original result may precede an asynchronous
            -- original worker. It still consumes the same original use; full
            -- native historical chains are mandatory after result observation.
            return (if (State=Reserved or else
                       (State in Effect_Observed | Settled and then
                         Chain_Effect(Data,B,E,Receipts,Events)))
                       and then Execution_Reference(Data,G,H,B,E.Owner_Resolution,Now)
                    then Execution_Ready else Refused);
         when Authorize_Followup =>
            return (if Followup_Reference(Data,G,H,B,E.Owner_Resolution,Now,E,
                       Receipts,Events) then Followup_Ready else Refused);
         when Quarantine_Use =>
            return (if State in Reserved | Effect_Observed | Quarantined then Quarantined_New else Refused);
         when Resolve_Recovery =>
            if State /= Reserved or else B.Action /= Resolve_Quarantine
              or else not Eligible(Data,G,H,B,Now,False)
              or else not R.Same(B.Id(Quarantine_Head),E.Quarantine_Head)
              or else not R.Same(B.Id(Original_Operation),E.Recovery_Issued.Operation)
              or else not R.Same(B.Id(Transaction),E.Recovery_Issued.Transaction)
              or else not R.Same(Data,E.Recovery_Issued,E.Recovery_Recovered)
            then return Refused; end if;
            declare
               Choice : constant R.Recovery_Action := R.Select_Action(Data,R.Claimed,
                  E.Recovery_Issued,E.Recovery_Recovered,R.Refused,E.Recovery_Historical,False,E.Recovery_Native);
            begin
               if Choice=R.Settle and then R.Same(E.Original_Use,E.Recovery_Issued.Grant_Use) then return Owner_Settle;
               elsif Choice=R.Abort_Use then return Owner_Abort;
               else return Refused; end if;
            end;
         when Observe_Effect =>
            return (if State=Reserved and then Chain_Effect(Data,B,E,Receipts,Events)
                    then Effect_Accepted else Refused);
         when Settle_Use =>
            return (if State in Effect_Observed | Settled and then Chain_Effect(Data,B,E,Receipts,Events)
                    then (if State=Settled then Settled_Replay else Settled_New) else Refused);
         when Release_Use =>
            return (if State in Reserved | Released and then Same(Data,B,E.No_Effect_Binding)
                    then (if State=Released then Released_Replay else Released_New) else Refused);
         when Resolve_No_Effect | Resolve_Effect =>
            if State/=Quarantined or else E.Owner_Resolution.Action/=Resolve_Quarantine
              or else not Eligible(Data,G,H,E.Owner_Resolution,Now,False)
              or else not (for some I in H'Range => H(I).State=Reserved and then Same(Data,H(I).Bound,E.Owner_Resolution))
              or else not R.Same(E.Owner_Resolution.Id(Original_Operation),B.Id(Operation_Id))
              or else not R.Same(E.Owner_Resolution.Id(Transaction),B.Id(Transaction))
              or else not R.Same(E.Owner_Resolution.Id(Quarantine_Head),E.Quarantine_Head)
            then return Refused; end if;
            return (if Mode=Resolve_No_Effect and then Same(Data,B,E.No_Effect_Binding)
                    then Resolved_No_Effect
                    elsif Mode=Resolve_Effect and then Chain_Effect(Data,B,E,Receipts,Events)
                    then Resolved_Effect else Refused);
         when Replay_Use =>
            return (if State=Settled and then Chain_Effect(Data,B,E,Receipts,Events) then Settled_Replay
                    elsif State=Released and then Same(Data,B,E.No_Effect_Binding) then Released_Replay
                    else Refused);
         when Reserve_Use | Check_Grants => return Refused;
      end case;
   end Reference;
   function Decide (Data : Q.Byte_Array; G : Grants; H : Uses; B : Binding;
                    Now : Q.Quantity; Mode : Command; E : Evidence;
                    Receipts, Events : C.Retained_Rows) return Decision is
   begin
      return Reference(Data,G,H,B,Now,Mode,E,Receipts,Events);
   end Decide;
end Worldline.Operation_Authority;
