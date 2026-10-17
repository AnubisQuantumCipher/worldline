with Resource_Quantities;
with Resource_Run_Ledger;
with Resource_Run_Ledger_Wire;
with Evaluation_History;
with Worldline.Owner_Transitions;
with Worldline.Owner_Transitions_Wire;

--  Actual value decoders and total owner selector; no OS/issuer authority claim.
procedure Test_Wire_Initialization is
   package Q renames Resource_Quantities;
   package L renames Resource_Run_Ledger;
   package W renames Resource_Run_Ledger_Wire;
   package E renames Evaluation_History;
   package K renames Worldline.Owner_Transitions;
   package O renames Worldline.Owner_Transitions_Wire;
   use type Q.Byte_Count;
   use type L.Row;
   use type L.Native_Row;
   use type E.Evaluation_Record;
   use type K.Decision;

   Data : constant Q.Byte_Array (7 .. 7) := (7 => 1);
   Absent : constant W.Raw_Id := (Present => 0, First => 1, Length => 0);
   Id : constant W.Raw_Id := (Present => 1, First => 7, Length => 1);
   Zero : constant W.Raw_Quantity := (Negative => 0, First => 1, Length => 0);
   Epoch : constant W.Raw_Epoch := (Present => 1, Value => Zero);
   Context : constant W.Raw_Context :=
     (Universe => Id, Policy => Id, Resource => Id, Unit => Id,
      Instance => Id, Host => Id, Boot => Id, Authority => Id,
      Policy_Epoch => Epoch);
   Bound : constant W.Raw_Binding :=
     (Reservation => Id, Operation => Id, Owner => Id, Workload => Id,
      Universe_Head => Id, Capability => Id, Grant_Use => Id, Payload => Id,
      Provenance => Id, Resource_Epoch => Epoch);
   Raw : constant W.Raw_Row :=
     (Scope => Context, Bound => Bound, Parent => Absent,
      Kind => L.Charge_Kind'Pos (L.Held_Capacity),
      State => L.Phase'Pos (L.Reserved), Amount => Zero,
      Observed_Usage => (Present => 0, Value => Zero),
      Planned_Unit => Absent, Actual_Unit => Absent,
      Cgroup => Absent, Invocation => Absent);
   Native : constant W.Raw_Native :=
     (Scope => Context, Resource_Epoch => Epoch, Bound => Bound,
      Actual_Unit => Id, Cgroup => Id, Invocation => Id,
      Observation_Head => Id, Observed => L.Liveness'Pos (L.Reaped));

   Owner_Id : constant O.Raw_Identity := (Present => 1, First => 7, Length => 1);
   Owner_Absent : constant O.Raw_Identity :=
     (Present => 0, First => O.Size'Last, Length => O.Size'Last);
   No_Cursor : constant O.Raw_Cursor :=
     (Present => 0, Sequence => Owner_Absent, Run => Owner_Absent);
   Owner_Row : constant O.Raw_Row :=
     (Subject => Owner_Id, Content => Owner_Id, Requirement => Owner_Id,
      Run => Owner_Id, Sequence => Owner_Id,
      State => E.Lifecycle'Pos (E.Completed), Outcome => E.Verdict'Pos (E.Passed));
   Absent_Row : constant O.Raw_Row :=
     (Subject => Owner_Absent, Content => Owner_Absent,
      Requirement => Owner_Absent, Run => Owner_Absent, Sequence => Owner_Absent,
      State => E.Lifecycle'Pos (E.Pending), Outcome => E.Verdict'Pos (E.No_Verdict));
   Invalid_Final : constant O.Raw_Row :=
     (Subject => Owner_Absent, Content => Owner_Absent,
      Requirement => Owner_Absent, Run => Owner_Absent, Sequence => Owner_Absent,
      State => O.U8'Last, Outcome => O.U8'Last);
   Grant : constant O.Raw_Grant :=
     (Action => K.Operation'Pos (K.Adopt_Requirement),
      State => K.Grant_State'Pos (K.Reserved), Grant => Owner_Id,
      Use_Id => Owner_Id, Issuer => Owner_Id, Principal => Owner_Id,
      Subject => Owner_Id, Content => Owner_Id, Transaction => Owner_Id,
      Current_Requirement => Owner_Id, Expected_Requirement => Owner_Id,
      Reason => Owner_Id, Issued_Grant => Owner_Id, Reserved_Grant => Owner_Id,
      Reserved_Use => Owner_Id, Failed_Run => No_Cursor,
      Prior_Head => No_Cursor, Next_Run => No_Cursor, Epoch => Owner_Id);
   Request : constant O.Raw_Request :=
     (Action => K.Operation'Pos (K.Adopt_Requirement),
      Peer => Owner_Id, Owner => Owner_Id, Trusted_Issuer => Owner_Id,
      Subject => Owner_Id, Content => Owner_Id, Transaction => Owner_Id,
      Current_Requirement => Owner_Id, Resulting_Requirement => Owner_Id,
      Current_Head => No_Cursor, Attempt => No_Cursor,
      Current_Epoch => Owner_Id, Grant => Grant);

   procedure Check_Rows (Input : W.Raw_Row_Array) is
      Output : constant L.Row_Array := W.Decode_Rows (Data, Input);
   begin
      pragma Assert (Output'First = Input'First and then Output'Last = Input'Last);
      for I in Input'Range loop
         pragma Assert (Output (I) = W.Decode (Data, Input (I)));
         pragma Assert (Output (I).Scope.Universe.Present);
         pragma Assert (Output (I).Scope.Universe.Value.First = 7);
         pragma Assert (Output (I).Scope.Universe.Value.Length = 1);
         pragma Assert (not Output (I).Parent.Present);
         pragma Assert (not Output (I).Amount.Negative and then Output (I).Amount.Length = 0);
         pragma Assert (not Output (I).Observed_Usage.Present);
      end loop;
   end Check_Rows;

   procedure Check_Native (Input : W.Raw_Native_Array) is
      Output : constant L.Native_Array := W.Decode_Native (Data, Input);
   begin
      pragma Assert (Output'First = Input'First and then Output'Last = Input'Last);
      for I in Input'Range loop
         pragma Assert (Output (I) = W.Decode (Data, Input (I)));
         pragma Assert (Output (I).Actual_Unit.Present and then Output (I).Invocation.Present);
      end loop;
   end Check_Native;

   procedure Check_Owner (Input : O.Raw_Rows) is
      Output : constant E.History := O.Rows (Input);
   begin
      pragma Assert (Output'First = Input'First and then Output'Last = Input'Last);
      for I in Input'Range loop
         pragma Assert (Output (I) = O.Row (Input (I)));
      end loop;
      pragma Assert (O.Decide (Data, Input, Invalid_Final, 0, Request) = K.Ready);
      pragma Assert (O.Decide (Data, Input, Owner_Row, 1, Request) = K.Ready);
      pragma Assert (O.Decide (Data, Input, Invalid_Final, 1, Request) = K.Input_Invalid);
      pragma Assert (O.Decide (Data, Input, Owner_Row, O.U8'Last, Request) = K.Input_Invalid);
      pragma Assert (O.Decide (Data, Input, Owner_Row, 1, Request) =
        K.Reference (Data, Output, (Present => True, Value => O.Row (Owner_Row)), O.Decode (Request)));
   end Check_Owner;
begin
   Check_Rows ((7 => Raw, 8 => Raw, 9 => Raw));
   Check_Rows (W.Raw_Row_Array'(Q.Byte_Index'Last => Raw));
   Check_Rows (W.Raw_Row_Array'(2 .. 1 => Raw));
   Check_Native ((7 => Native, 8 => Native, 9 => Native));
   Check_Native (W.Raw_Native_Array'(Q.Byte_Index'Last => Native));
   Check_Native (W.Raw_Native_Array'(2 .. 1 => Native));
   Check_Owner ((7 => Absent_Row, 8 => Owner_Row, 9 => Absent_Row));
   Check_Owner (O.Raw_Rows'(E.Byte_Index'Last => Owner_Row));
   Check_Owner (O.Raw_Rows'(2 .. 1 => Owner_Row));
end Test_Wire_Initialization;
