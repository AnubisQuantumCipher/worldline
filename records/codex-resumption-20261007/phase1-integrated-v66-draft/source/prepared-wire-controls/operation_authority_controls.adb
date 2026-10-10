with Worldline;
with Worldline.Operation_Authority;
with Interfaces;
with Ada.Environment_Variables;
with Operation_Effect_Fixtures;
procedure Operation_Authority_Controls is
   package A renames Worldline.Operation_Authority;
   package Q renames A.Q; package R renames A.R; package C renames A.C;
   use type A.Decision; use type Interfaces.Unsigned_32;
   use type Q.Byte_Count; use type Q.Byte_Array;
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
      Recovery_Historical=>R.Unestablished,Recovery_Native=>(Live_Mapping=>Id,Live_Root=>Id),Original_Use=>Id,
      Effect_Material=>(1,0));
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
   declare
      F : constant Operation_Effect_Fixtures.Fixture := Operation_Effect_Fixtures.Load
        (Ada.Environment_Variables.Value ("WORLDLINE_OPERATION_EFFECT_FIXTURE"));
      Data : constant Q.Byte_Array := F.Arena & Q.Byte_Array'[0,16];
      B : constant A.Binding := F.Bound;
      G : A.Grants := F.Grants;
      H : A.Uses := F.Uses;
      E : A.Evidence := F.Facts;
      Receipts : constant C.Retained_Rows := F.Receipts;
      Events : constant C.Retained_Rows := F.Events;
      Limit : constant Q.Quantity := (False, Data'Last, 1);
      Selected_Use : Q.Byte_Index := H'First;
      Selected_Grant : Q.Byte_Index := G'First;
      Use_Found, Grant_Found : Boolean := False;
   begin
      for I in H'Range loop
         if R.Same (H(I).Bound.Id(A.Operation_Id), B.Id(A.Operation_Id)) then
            Check (not Use_Found); Selected_Use := I; Use_Found := True;
         end if;
      end loop;
      for I in G'Range loop
         if R.Same (G(I).Id, B.Id(A.Grant_Id)) then
            Check (not Grant_Found); Selected_Grant := I; Grant_Found := True;
         end if;
      end loop;
      Check (Use_Found and Grant_Found);
      -- The inherited assertions now consume the genuine full operation
      -- capture/result and ALL rows of the original observation.
      Check(A.Decide(Data,G,H,B,Zero,A.Observe_Effect,E,Receipts,Events)=A.Effect_Accepted);
      H(Selected_Use).State:=A.Effect_Observed;G(Selected_Grant).State:=A.Revoked;
      Check(A.Decide(Data,G,H,B,Limit,A.Settle_Use,E,Receipts,Events)=A.Settled_New);
      H(Selected_Use).State:=A.Settled;
      Check(A.Decide(Data,G,H,B,Limit,A.Settle_Use,E,Receipts,Events)=A.Settled_Replay);
      E.Witnessed_Causal_Head.Present:=False;
      Check(A.Decide(Data,G,H,B,Limit,A.Settle_Use,E,Receipts,Events)=A.Refused);
   end;
   E.Effect_Binding:=B;
   E.Witnessed_Receipt_Head:=(Present=>True,Value=>C.Link(C.Receipt_Chain,Id.Value,Id.Value));
   E.Witnessed_Causal_Head:=(Present=>True,Value=>C.Link(C.Causal_Chain,Id.Value,Id.Value));
   Receipts(1):=(Previous=>Id,Actual_Payload_Root=>Id,Stored_Payload_Root=>Id,Stored_Head=>E.Witnessed_Receipt_Head);
   Events(1):=(Previous=>Id,Actual_Payload_Root=>Id,Stored_Payload_Root=>Id,Stored_Head=>E.Witnessed_Causal_Head);
   -- Retain the former bare-root success construction as a bug-negative:
   -- matching hashes without interpreted original material cannot observe.
   Check(A.Decide(Data,G,H,B,Zero,A.Observe_Effect,E,Receipts,Events)=A.Refused);
   G(1).State:=A.Active;H(1).State:=A.Quarantined;B.Action:=A.Resolve_Quarantine;
   -- A copied/matching unresolved observation is insufficient for K4.
   H(1).Bound:=B;H(1).State:=A.Reserved;
   Check(A.Decide(Data,G,H,B,Zero,A.Resolve_Recovery,E,R_Empty,R_Empty)=A.Refused);
end Operation_Authority_Controls;
