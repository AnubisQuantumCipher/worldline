with Worldline.Custody_V2_Prepared;
with Worldline.Custody_V2_Prepared_Wire;
with Worldline;
with Worldline.Operation_Authority;
with Interfaces;
procedure Prepared_Operation_Heads_Controls is
   package A renames Worldline.Operation_Authority;
   package Q renames A.Q; package R renames A.R; package C renames A.C;
   use type A.Decision; use type Interfaces.Unsigned_32;
   Data : Q.Byte_Array := [0,16];
   Zero : Q.Quantity := (Negative=>False,First=>1,Length=>0);
   Limit : Q.Quantity := (Negative=>False,First=>2,Length=>1);
   Epoch : R.Optional_Epoch := (Present=>True,Value=>Zero);
   Id : R.Optional_Digest := (Present=>True,Value=>[others=>1]);
   Owner : A.Optional_UID := (Present=>True,Value=>7);
   B : A.Binding := (Action=>A.Ping,Id=>[others=>Id],Peer=>Owner,Preparer=>Owner,
      Owner=>Owner,Target_Owner=>Owner,Policy_Epoch=>Epoch,Resource_Epoch=>Epoch);
   G : A.Grants(1..1) := [1=>(Id=>Id,Parent=>(Present=>False,Value=>[others=>0]),
      Issuer=>Id,Instance=>Id,Root_Set=>Id,Policy=>Id,Subject=>Owner,Owner=>Owner,
      Allowed=>[others=>True],State=>A.Active,Epoch=>Epoch,Ceiling=>Limit,Issued_At=>Zero,Expires_At=>Limit)];
   Empty : A.Uses(1..0);
   H : A.Uses(1..1);
   R_Empty : C.Retained_Rows(1..0);
   Receipts,Events : C.Retained_Rows(1..1);
   E : A.Evidence := (Effect_Binding=>B,Actual_Receipt_Root=>Id,Actual_Causal_Root=>Id,
      No_Effect_Binding=>B,Owner_Resolution=>B,Quarantine_Head=>Id,
      Witnessed_Receipt_Head=>Id,Witnessed_Causal_Head=>Id,
      Recovery_Issued=>(Mode=>R.Candidate,Policy_Epoch=>Epoch,Resource_Epoch=>Epoch,others=>Id),
      Recovery_Recovered=>(Mode=>R.Candidate,Policy_Epoch=>Epoch,Resource_Epoch=>Epoch,others=>Id),
      Recovery_Historical=>R.Unestablished,Recovery_Native=>(Live_Mapping=>Id,Live_Root=>Id),Original_Use=>Id);
   procedure Check(Test:Boolean) is
   begin pragma Assert(Test); if not Test then raise Program_Error; end if; end Check;
begin
   -- Pure native value fixtures only. These are not protected issuance,
   -- authenticated OS observations, custody, runtime acceptance or proofs.
   for Op in A.Operation loop
      B.Action:=Op;
      Check(A.Decide(Data,G,Empty,B,Zero,A.Reserve_Use,E,R_Empty,R_Empty)=A.Reserved_New);
      H(1):=(Bound=>B,State=>A.Reserved);
      Check(A.Decide(Data,G,H,B,Zero,A.Reserve_Use,E,R_Empty,R_Empty)=A.Reserved_Replay);
      G(1).Allowed(Op):=False;
      Check(A.Decide(Data,G,H,B,Zero,A.Reserve_Use,E,R_Empty,R_Empty)=A.Refused);
      G(1).Allowed(Op):=True;
      E.No_Effect_Binding:=B;
      Check(A.Decide(Data,G,H,B,Zero,A.Release_Use,E,R_Empty,R_Empty)=A.Released_New);
   end loop;
   -- Additional simulated values exercise the real PREPARED operation
   -- redecision, including its complete grant/use/evidence/chain arrays.
   B.Action := A.Fork_World;
   H (1) := (Bound => B, State => A.Reserved);
   Check (Worldline.Custody_V2_Prepared.Operation_Heads_Reestablished
     (Data, G, Empty, H, B, Zero, Zero, E, E,
      R_Empty, R_Empty, R_Empty, R_Empty));
   Check (not Worldline.Custody_V2_Prepared.Operation_Heads_Reestablished
     (Data, G, Empty, Empty, B, Zero, Zero, E, E,
      R_Empty, R_Empty, R_Empty, R_Empty));
   G (1).State := A.Revoked;
   Check (not Worldline.Custody_V2_Prepared.Operation_Heads_Reestablished
     (Data, G, Empty, H, B, Zero, Zero, E, E,
      R_Empty, R_Empty, R_Empty, R_Empty));
   G (1).State := A.Active;
   B.Action := A.Ping;
   H (1) := (Bound => B, State => A.Reserved);
   Check (not Worldline.Custody_V2_Prepared.Operation_Heads_Reestablished
     (Data, G, Empty, H, B, Zero, Zero, E, E,
      R_Empty, R_Empty, R_Empty, R_Empty));
   B.Action:=A.Commit_Collapse; B.Preparer.Value:=8;
   Check(A.Decide(Data,G,Empty,B,Zero,A.Reserve_Use,E,R_Empty,R_Empty)=A.Refused);
   B.Preparer:=Owner; B.Action:=A.Prune; B.Peer.Value:=8;
   Check(A.Decide(Data,G,Empty,B,Zero,A.Reserve_Use,E,R_Empty,R_Empty)=A.Refused);
   B.Peer:=Owner; B.Action:=A.Ping; B.Id(A.Prime).Present:=False; B.Id(A.Requirement).Present:=False;
   Check(A.Decide(Data,G,Empty,B,Zero,A.Reserve_Use,E,R_Empty,R_Empty)=A.Reserved_New);
   B.Id(A.Prime):=Id;B.Id(A.Requirement):=Id;
   G(1).Ceiling:=Zero;
   Check(A.Decide(Data,G,Empty,B,Zero,A.Reserve_Use,E,R_Empty,R_Empty)=A.Refused);
   G(1).Ceiling:=Limit;H(1):=(Bound=>B,State=>A.Reserved);
   E.Effect_Binding:=B;
   E.Witnessed_Receipt_Head:=(Present=>True,Value=>C.Link(C.Receipt_Chain,Id.Value,Id.Value));
   E.Witnessed_Causal_Head:=(Present=>True,Value=>C.Link(C.Causal_Chain,Id.Value,Id.Value));
   Receipts(1):=(Previous=>Id,Actual_Payload_Root=>Id,Stored_Payload_Root=>Id,Stored_Head=>E.Witnessed_Receipt_Head);
   Events(1):=(Previous=>Id,Actual_Payload_Root=>Id,Stored_Payload_Root=>Id,Stored_Head=>E.Witnessed_Causal_Head);
   Check(A.Decide(Data,G,H,B,Zero,A.Observe_Effect,E,Receipts,Events)=A.Effect_Accepted);
   H(1).State:=A.Effect_Observed;G(1).State:=A.Revoked;
   Check(A.Decide(Data,G,H,B,Limit,A.Settle_Use,E,Receipts,Events)=A.Settled_New);
   H(1).State:=A.Settled;
   Check(A.Decide(Data,G,H,B,Limit,A.Settle_Use,E,Receipts,Events)=A.Settled_Replay);
   E.Witnessed_Causal_Head.Present:=False;
   Check(A.Decide(Data,G,H,B,Limit,A.Settle_Use,E,Receipts,Events)=A.Refused);
   G(1).State:=A.Active;H(1).State:=A.Quarantined;B.Action:=A.Resolve_Quarantine;
   -- A copied/matching unresolved observation is insufficient for K4.
   H(1).Bound:=B;H(1).State:=A.Reserved;
   Check(A.Decide(Data,G,H,B,Zero,A.Resolve_Recovery,E,R_Empty,R_Empty)=A.Refused);
end Prepared_Operation_Heads_Controls;
