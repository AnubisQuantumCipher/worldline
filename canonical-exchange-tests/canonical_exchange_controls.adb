with Worldline;
with Worldline.Canonical_Exchange;
with Worldline.Collapse_Wire;
with Interfaces;
procedure Canonical_Exchange_Controls is
   package X renames Worldline.Canonical_Exchange;
   package A renames X.A; package R renames X.R; package C renames X.C;
   package L renames X.L; package Q renames A.Q;
   use type X.Decision; use type A.Decision;
   Data:Q.Byte_Array(1..Worldline.Hash'Length):=[others=>1];
   Zero:Q.Quantity:=(Negative=>False,First=>1,Length=>0);
   One:Q.Quantity:=(Negative=>False,First=>1,Length=>1);
   Large:Q.Quantity:=(Negative=>False,First=>1,Length=>Data'Length);
   Epoch:R.Optional_Epoch:=(Present=>True,Value=>Zero);
   Id:R.Optional_Digest:=(Present=>True,Value=>[others=>1]);
   Other_Id:R.Optional_Digest:=(Present=>True,Value=>[others=>2]);
   Owner:A.Optional_UID:=(Present=>True,Value=>7);
   B:A.Binding:=(Action=>A.Commit_Collapse,Id=>[others=>Id],Peer=>Owner,Preparer=>Owner,
      Owner=>Owner,Target_Owner=>Owner,Policy_Epoch=>Epoch,Resource_Epoch=>Epoch);
   G:A.Grants(1..1):=[1=>(Id=>Id,Parent=>(Present=>False,Value=>[others=>0]),Issuer=>Id,
      Instance=>Id,Root_Set=>Id,Policy=>Id,Subject=>Owner,Owner=>Owner,Allowed=>[others=>True],
      State=>A.Active,Epoch=>Epoch,Ceiling=>Large,Issued_At=>Zero,Expires_At=>Large)];
   H:A.Uses(1..1):=[1=>(Bound=>B,State=>A.Reserved)];
   Owner_H:A.Uses(1..2);
   E:A.Evidence:=(Effect_Binding=>B,Actual_Receipt_Root=>Id,Actual_Causal_Root=>Id,
      No_Effect_Binding=>B,Owner_Resolution=>B,Quarantine_Head=>Id,
      Witnessed_Receipt_Head=>Id,Witnessed_Causal_Head=>Id,
      Recovery_Issued=>(Mode=>R.Candidate,Policy_Epoch=>Epoch,Resource_Epoch=>Epoch,others=>Id),
      Recovery_Recovered=>(Mode=>R.Candidate,Policy_Epoch=>Epoch,Resource_Epoch=>Epoch,others=>Id),
      Recovery_Historical=>R.Unestablished,Recovery_Native=>(Live_Mapping=>Id,Live_Root=>Id),Original_Use=>Id,
      Effect_Material=>(1,0));
   I:L.Identity:=(Present=>True,Value=>(First=>1,Length=>Data'Length));
   None:L.Identity:=(Present=>False);
   Scope:L.Context:=(Policy_Epoch=>Epoch,others=>I);
   Bound:L.Binding:=(Resource_Epoch=>Epoch,others=>I);
   State:L.Ledger_State:=(Scope=>Scope,Resource_Epoch=>Epoch,Universe_Head=>I,Ledger_Head=>I,
      Capacity=>One,Held_Total=>One,Charged_Total=>Zero);
   Rows:L.Row_Array(1..1):=[1=>(Scope=>Scope,Bound=>Bound,Parent=>None,Kind=>L.Held_Capacity,
      State=>L.Reserved,Amount=>One,Observed_Usage=>(Present=>False),
      Planned_Unit=>None,Actual_Unit=>None,Cgroup=>None,Invocation=>None)];
   Native:L.Native_Array(1..1):=[1=>(Scope=>Scope,Resource_Epoch=>Epoch,Bound=>Bound,
      Actual_Unit=>None,Cgroup=>None,Invocation=>None,Observation_Head=>I,Observed=>L.Never_Launched)];
   M:X.Material:=(Worker_Issued=>(Mode=>R.Candidate,Policy_Epoch=>Epoch,Resource_Epoch=>Epoch,others=>Id),
      Worker_Recovered=>(Mode=>R.Candidate,Policy_Epoch=>Epoch,Resource_Epoch=>Epoch,others=>Id),
      Canonical_Issued=>(Mode=>R.Candidate,Policy_Epoch=>Epoch,Resource_Epoch=>Epoch,others=>Id),
      Canonical_Recovered=>(Mode=>R.Candidate,Policy_Epoch=>Epoch,Resource_Epoch=>Epoch,others=>Id),
      Worker_Native=>(Live_Mapping=>Id,Live_Root=>Id),Canonical_Native=>(Live_Mapping=>Id,Live_Root=>Id),others=>Id);
   Receipts,Events:C.Retained_Rows(1..1);
   Owner_B:A.Binding:=B;
   procedure Check(Test:Boolean) is
   begin pragma Assert(Test); if not Test then raise Program_Error; end if; end Check;
   procedure Put (Field : out Worldline.Collapse_Wire.Raw_Optional_Hash;
                  V : Interfaces.Unsigned_8) is
   begin
      Field.Present := 1;
      Field.Value := [others => V];
   end Put;

   function Good_Wire return Worldline.Collapse_Wire.Raw_Request is
      use Worldline.Collapse_Wire;
      Absent : constant Raw_Optional_Hash := (Present => 0, Value => [others => 0]);
      R : Raw_Request :=
        (Candidate_State => 2, Phase => 0, Evaluation_Mode => 0, Conflicts => 1,
         Foreign_Writes => 1, Roster_Complete => 1, Staged_Roster_Complete => 0,
         Generation_Before => (Present => 1, Value_LE => [41, others => 0]),
         Generation_After => (Present => 1, Value_LE => [41, others => 0]),
         others => Absent);
   begin
      Put (R.Expected_Parent, 1); Put (R.Candidate_Parent, 1);
      Put (R.Expected_Subject, 2); Put (R.Evidence_Subject, 2);
      Put (R.Expected_Base, 3); Put (R.Candidate_Base, 3);
      Put (R.Expected_Delta, 4); Put (R.Candidate_Delta, 4);
      Put (R.Expected_Root_Set, 5); Put (R.Candidate_Root_Set, 5);
      Put (R.Expected_Staged_Root, 6); Put (R.Actual_Staged_Root, 6);
      Put (R.Staged_Content_Root, 7); Put (R.Tested_Root, 7);
      Put (R.Current_Requirement, 8); Put (R.Resulting_Requirement, 8);
      Put (R.Evaluated_Requirement, 8);
      Put (R.Declared_Verifiers, 9); Put (R.Executed_Verifiers, 9);
      Put (R.Registered_Watch_Set, 10); Put (R.Watched_Set, 10);
      return R;
   end Good_Wire;
   Collapse:Worldline.Collapse_Wire.Raw_Request:=Good_Wire;
   function Decide(P:X.Phase; Mode:X.Command:=X.Advance) return X.Decision is
     (X.Decide(Data,G,H,B,Zero,E,State,Rows,Native,Bound,I,Owner,Collapse,M,P,Mode,
         Receipts,Events,Receipts,Events));
begin
   -- Pure native value fixtures only; they confer no protected custody.
   M.Worker_Issued.Subject:=(Present=>True,Value=>Worldline.Collapse_Wire.Digest(Collapse.Expected_Subject.Value));
   M.Worker_Issued.Staged_Root:=(Present=>True,Value=>Worldline.Collapse_Wire.Digest(Collapse.Actual_Staged_Root.Value));
   M.Worker_Issued.Current_Requirement:=(Present=>True,Value=>Worldline.Collapse_Wire.Digest(Collapse.Current_Requirement.Value));
   M.Worker_Issued.Resulting_Requirement:=(Present=>True,Value=>Worldline.Collapse_Wire.Digest(Collapse.Resulting_Requirement.Value));
   B.Id(A.Requirement):=M.Worker_Issued.Current_Requirement;
   H(1).Bound:=B;E.Effect_Binding:=B;E.No_Effect_Binding:=B;
   Owner_B:=B;
   M.Worker_Issued.Staged_Mapping:=Other_Id;
   M.Canonical_Issued:=M.Worker_Issued;
   M.Worker_Recovered:=M.Worker_Issued;
   M.Canonical_Issued.Staged_Mapping:=Other_Id;
   M.Canonical_Recovered:=M.Canonical_Issued;
   M.Worker_Receipt_Head:=(Present=>True,Value=>C.Link(C.Receipt_Chain,Id.Value,Id.Value));
   M.Worker_Causal_Head:=(Present=>True,Value=>C.Link(C.Causal_Chain,Id.Value,Id.Value));
   Receipts(1):=(Previous=>Id,Actual_Payload_Root=>Id,Stored_Payload_Root=>Id,Stored_Head=>M.Worker_Receipt_Head);
   Events(1):=(Previous=>Id,Actual_Payload_Root=>Id,Stored_Payload_Root=>Id,Stored_Head=>M.Worker_Causal_Head);
   Check(Decide(X.Issued)=X.Dispatch_Worker);
   M.Worker_Native.Live_Mapping:=Other_Id;
   M.Worker_Native.Live_Root:=M.Worker_Issued.Staged_Root;
   Check(Decide(X.Worker_Intent)=X.Record_Worker);
   Check(Decide(X.Worker_Observed)=X.Dispatch_Canonical);
   G(1).State:=A.Revoked;
   Check(Decide(X.Worker_Observed)=X.Refused);
   M.Canonical_Native.Live_Mapping:=Other_Id;
   M.Canonical_Native.Live_Root:=M.Canonical_Issued.Staged_Root;
   Check(Decide(X.Canonical_Intent)=X.Record_Effect);
   H(1).State:=A.Effect_Observed;
   E.Witnessed_Receipt_Head:=M.Worker_Receipt_Head;
   E.Witnessed_Causal_Head:=M.Worker_Causal_Head;
   Check(Decide(X.Effect_Observed,X.Settle_Historical)=X.Settle_Same_Use);
   H(1).State:=A.Settled;
   Check(Decide(X.Settled,X.Replay_Historical)=X.Replay_Same_Use);
   M.Canonical_Native.Live_Mapping.Present:=False;
   Check(Decide(X.Settled,X.Replay_Historical)=X.Refused);
   M.Canonical_Native.Live_Mapping:=Other_Id;
   M.Worker_Recovered.Operation:=Other_Id;
   Check(Decide(X.Settled,X.Replay_Historical)=X.Refused);
   M.Worker_Recovered:=M.Worker_Issued;
   G(1).State:=A.Active;H(1).State:=A.Quarantined;
   Owner_B.Action:=A.Resolve_Quarantine;Owner_B.Id(A.Operation_Id):=Other_Id;
   E.Owner_Resolution:=Owner_B;
   Owner_H:=[1=>H(1),2=>(Bound=>Owner_B,State=>A.Reserved)];
   Check(X.Decide(Data,G,Owner_H,B,Zero,E,State,Rows,Native,Bound,I,Owner,Collapse,M,
      X.Quarantined,X.Resolve_Owner,Receipts,Events,Receipts,Events)=X.Owner_Record_Effect);
   M.Worker_Native.Live_Mapping:=Id;M.Canonical_Native.Live_Mapping:=Id;
   M.Worker_Native.Live_Root:=Id;M.Canonical_Native.Live_Root:=Id;
   Check(X.Decide(Data,G,Owner_H,B,Zero,E,State,Rows,Native,Bound,I,Owner,Collapse,M,
      X.Quarantined,X.Resolve_Owner,Receipts,Events,Receipts,Events)=X.Owner_Record_Abort);
   M.Worker_Native.Live_Mapping:=Other_Id;
   Check(X.Decide(Data,G,Owner_H,B,Zero,E,State,Rows,Native,Bound,I,Owner,Collapse,M,
      X.Quarantined,X.Resolve_Owner,Receipts,Events,Receipts,Events)=X.Refused);
   -- Preserve the original genuinely authorized checkpoint-return wire case.
   G(1).State:=A.Active;H(1).State:=A.Reserved;
   M.Worker_Native:=(Live_Mapping=>Id,Live_Root=>Id);
   M.Canonical_Native:=M.Worker_Native;
   Collapse.Evaluation_Mode:=1;Collapse.Roster_Complete:=0;
   Collapse.Evaluated_Requirement:=(Present=>0,Value=>[others=>0]);
   Collapse.Executed_Verifiers:=(Present=>0,Value=>[others=>0]);
   Put(Collapse.Expected_Checkpoint,11);Put(Collapse.Witnessed_Checkpoint,11);
   Collapse.Resulting_Requirement:=(Present=>0,Value=>[others=>0]);
   M.Worker_Issued.Mode:=R.Checkpoint_Return;
   M.Worker_Issued.Resulting_Requirement:=(Present=>False,Value=>[others=>0]);
   M.Worker_Recovered:=M.Worker_Issued;
   M.Canonical_Issued:=M.Worker_Issued;M.Canonical_Recovered:=M.Worker_Issued;
   Check(Decide(X.Issued)=X.Dispatch_Worker);
   M.Worker_Recovered.Resulting_Requirement:=Id;
   Check(Decide(X.Issued)=X.Refused);
   M.Worker_Recovered:=M.Worker_Issued;
   Put(Collapse.Resulting_Requirement,8);
   Check(Decide(X.Issued)=X.Refused);
   Collapse.Resulting_Requirement:=(Present=>0,Value=>[others=>0]);
   M.Worker_Issued.Mode:=R.Candidate;M.Worker_Recovered:=M.Worker_Issued;
   M.Canonical_Issued:=M.Worker_Issued;M.Canonical_Recovered:=M.Worker_Issued;
   Check(Decide(X.Issued)=X.Refused);
end Canonical_Exchange_Controls;
