with Worldline;
with Worldline.Canonical_Exchange;
with Worldline.Canonical_Owner_Completion;
with Worldline.Collapse_Wire;
with Interfaces;
procedure Canonical_Owner_Completion_Controls is
   package Y renames Worldline.Canonical_Owner_Completion;
   use type Y.Decision;
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
   Historical_G : A.Grants(1..1);
   Historical_H,Current_H : A.Uses(1..2);
   Historical_E,Current_E : A.Evidence;
   Historical_M : X.Material;
   function Complete return Y.Decision is
     (Y.Decide(Data,Historical_G,Historical_H,B,Zero,Historical_E,State,Rows,
       Native,Bound,I,Owner,Collapse,Historical_M,Receipts,Events,Receipts,Events,
       G,Current_H,B,Current_E,Receipts,Events));
begin
   -- These genuine complete pure value controls confer no protected custody.
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
   Owner_B:=B;Owner_B.Action:=A.Resolve_Quarantine;
   Owner_B.Id(A.Operation_Id):=Other_Id;Owner_B.Id(A.Use_Id):=Other_Id;
   Owner_B.Id(A.Original_Operation):=B.Id(A.Operation_Id);
   H(1).State:=A.Quarantined;
   Owner_H:=[1=>H(1),2=>(Bound=>Owner_B,State=>A.Reserved)];
   E.Owner_Resolution:=Owner_B;
   E.Witnessed_Receipt_Head:=M.Worker_Receipt_Head;
   E.Witnessed_Causal_Head:=M.Worker_Causal_Head;
   M.Worker_Native.Live_Mapping:=Other_Id;
   M.Worker_Native.Live_Root:=M.Worker_Issued.Staged_Root;
   M.Canonical_Native.Live_Mapping:=Other_Id;
   M.Canonical_Native.Live_Root:=M.Canonical_Issued.Staged_Root;
   Historical_G:=G;Historical_H:=Owner_H;Current_H:=Owner_H;
   Historical_E:=E;Current_E:=E;Historical_M:=M;
   Check(Complete=Y.Resolve_Effect);
   -- Original owner effect capture remains usable after fresh revocation and
   -- expiry. It cannot supply a fresh pre-exec capability authorization.
   G(1).State:=A.Revoked;
   Check(Complete=Y.Resolve_Effect);
   Check(A.Decide(Data,G,H,B,Large,A.Authorize_Execution,E,Receipts,Events)=A.Refused);
   Current_H(1).State:=A.Effect_Observed;
   Check(Complete=Y.Effect_Already);
   Current_H(1).State:=A.Settled;
   Check(Complete=Y.Effect_Already);
   Current_H(1).State:=A.Quarantined;
   Historical_M.Worker_Recovered.Operation:=Other_Id;
   Check(Complete=Y.Refused);
   Historical_M:=M;
   Current_E.Owner_Resolution.Peer:=(Present=>True,Value=>8);
   Check(Complete=Y.Refused);
   Current_E:=E;
   Current_H(2).Bound.Id(A.Transaction):=Other_Id;
   Check(Complete=Y.Refused);
   Current_H:=Owner_H;
   G(1).Ceiling:=One;
   Check(Complete=Y.Refused);
   G:=Historical_G;
   Current_E.Witnessed_Receipt_Head:=Other_Id;
   Check(Complete=Y.Refused);
   Current_E:=E;
   -- Genuine complete Before/Before permits no-effect completion; split or
   -- unknown observations refuse. Duplicate terminal returns no new use.
   Historical_M.Worker_Native:=(Live_Mapping=>Id,Live_Root=>Id);
   Historical_M.Canonical_Native:=Historical_M.Worker_Native;
   Check(Complete=Y.Resolve_No_Effect);
   Current_H(1).State:=A.Released;
   Check(Complete=Y.No_Effect_Already);
   Historical_M.Canonical_Native.Live_Mapping:=Other_Id;
   Check(Complete=Y.Refused);
   Historical_M.Canonical_Native:=(Live_Mapping=>Id,Live_Root=>Id);
   Historical_M.Worker_Native.Live_Mapping.Present:=False;
   Check(Complete=Y.Refused);
   -- Before execution uses the complete reserved history and original peer,
   -- consumes no second use, and checks every fresh ancestor's attenuation.
   H(1).State:=A.Reserved;E.Owner_Resolution:=B;
   Check(A.Decide(Data,G,H,B,Zero,A.Authorize_Execution,E,Receipts,Events)=A.Execution_Ready);
   Check(A.Decide(Data,G,H,B,Large,A.Authorize_Execution,E,Receipts,Events)=A.Refused);
   G(1).State:=A.Revoked;
   Check(A.Decide(Data,G,H,B,Zero,A.Authorize_Execution,E,Receipts,Events)=A.Refused);
   G:=Historical_G;
   E.Owner_Resolution.Peer:=(Present=>True,Value=>8);
   Check(A.Decide(Data,G,H,B,Zero,A.Authorize_Execution,E,Receipts,Events)=A.Refused);
   E.Owner_Resolution:=B;H(1).State:=A.Settled;
   Check(A.Decide(Data,G,H,B,Zero,A.Authorize_Execution,E,Receipts,Events)=A.Execution_Ready);
   E.Witnessed_Receipt_Head:=Other_Id;
   Check(A.Decide(Data,G,H,B,Zero,A.Authorize_Execution,E,Receipts,Events)=A.Refused);
end Canonical_Owner_Completion_Controls;
