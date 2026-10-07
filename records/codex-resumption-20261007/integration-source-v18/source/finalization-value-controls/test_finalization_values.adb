with Evaluation_Finalization;
with Evaluation_Finalization.Values;
with Worldline;
procedure Test_Finalization_Values is
   package F renames Evaluation_Finalization;
   package V renames F.Values;
   use type F.Write_Decision;
   use type F.Optional_Start;
   use type F.Optional_Input;
   A : constant F.T.Bytes := (1 .. 0 => 0);
   Plans : constant F.R.Check_Array := (1 .. 0 => ((1, 0), (1, 0)));
   S : constant F.Start_Record :=
     (Store => (1, 0), Subject => (1, 0), Run => (1, 0), Sequence => (1, 0),
      Requirement => (Present => False), Policy => (1, 0), Verifier_Plan => (1, 0),
      Base_Context => (1, 0), Parent => Worldline.Zero_Hash,
      Config => Worldline.Zero_Hash, Repository => Worldline.Zero_Hash,
      Required => (1, 0), Declaration => F.R.Old.Missing_Declaration);
   I : constant F.Input_Record :=
     (Start => S, Root => (1, 0), Manifests => (1, 0),
      Filesystem => Worldline.Zero_Hash, Config => Worldline.Zero_Hash,
      Repository => Worldline.Zero_Hash);
   Absent_Start : constant F.Optional_Start (False) := (Present => False);
   Absent_Input : constant F.Optional_Input (False) := (Present => False);
   Present_Start : constant F.Optional_Start (True) := (Present => True, Value => S);
   Present_Input : constant F.Optional_Input (True) := (Present => True, Value => I);
   Different_Start : F.Start_Record := S;
   Different_Input : F.Input_Record := I;
   Invalid_Start : F.Start_Record := S;
   Invalid_Input : F.Input_Record := I;
   Start_Result : V.Start_Update;
   Input_Result : V.Input_Update;
begin
   -- The complete values are returned; constrained input storage is untouched.
   pragma Assert (F.Start_Valid (A, S, Plans));
   pragma Assert (F.Input_Valid (A, S, I, Plans));
   Start_Result := V.Record_Start_Value (A, S, Plans, Absent_Start);
   pragma Assert (Start_Result.Decision = F.Insert and then Start_Result.Updated = (True, S));
   pragma Assert (not Absent_Start.Present);
   Input_Result := V.Record_Input_Value (A, S, I, Plans, Absent_Input);
   pragma Assert (Input_Result.Decision = F.Insert and then Input_Result.Updated = (True, I));
   pragma Assert (not Absent_Input.Present);
   Start_Result := V.Record_Start_Value (A, S, Plans, Present_Start);
   pragma Assert (Start_Result.Decision = F.Already_Present and then Start_Result.Updated = Present_Start);
   Input_Result := V.Record_Input_Value (A, S, I, Plans, Present_Input);
   pragma Assert (Input_Result.Decision = F.Already_Present and then Input_Result.Updated = Present_Input);
   Different_Start.Repository (Worldline.Hash'First) := 1;
   Start_Result := V.Record_Start_Value (A, Different_Start, Plans, Present_Start);
   pragma Assert (Start_Result.Decision = F.Conflict and then Start_Result.Updated = Present_Start);
   Different_Input.Filesystem (Worldline.Hash'First) := 1;
   Input_Result := V.Record_Input_Value (A, S, Different_Input, Plans, Present_Input);
   pragma Assert (Input_Result.Decision = F.Conflict and then Input_Result.Updated = Present_Input);
   Invalid_Start.Sequence := (First => 1, Length => 1);
   Start_Result := V.Record_Start_Value (A, Invalid_Start, Plans, Absent_Start);
   pragma Assert (Start_Result.Decision = F.Invalid and then Start_Result.Updated = Absent_Start);
   Invalid_Input.Root := (First => 1, Length => 1);
   Input_Result := V.Record_Input_Value (A, S, Invalid_Input, Plans, Absent_Input);
   pragma Assert (Input_Result.Decision = F.Invalid and then Input_Result.Updated = Absent_Input);
end Test_Finalization_Values;
