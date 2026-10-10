with Worldline;
with Worldline.Actuation;
with Worldline.Actuation_Full_Wire;
with Worldline.Collapse_Wire;
with Interfaces;
procedure Physical_Value_Controls is
   package W renames Worldline.Actuation_Full_Wire;
   package A renames Worldline.Actuation;
   use type A.Decision;
   procedure Check (Value : Boolean) is
   begin
      pragma Assert (Value);
      if not Value then raise Program_Error; end if;
   end Check;
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
   Facts : W.Raw_Request :=
     (Collapse_Facts => Good_Wire,
      Expected_Live => (Present => 1, Device => 1, Inode => 1),
      Observed_Live => (Present => 1, Device => 1, Inode => 1),
      Expected_Stage => (Present => 1, Device => 1, Inode => 2),
      Observed_Stage => (Present => 1, Device => 1, Inode => 2),
      Expected_Marker_Digest => [others => 1],
      Observed_Marker_Digest => [others => 1],
      Payload_Durable => 1, Recovery_Clean => 1);
   Original : constant W.Raw_Request := Facts;
begin
   -- Synthetic value fixtures: no OS directories or protected authority.
   Check (W.Well_Formed (Facts));
   Check (A.Decide (W.Decode (Facts)) = A.Authorized);
   Facts.Payload_Durable := 0;
   Check (A.Decide (W.Decode (Facts)) = A.Payload_Not_Durable);
   Facts := Original; Facts.Recovery_Clean := 0;
   Check (A.Decide (W.Decode (Facts)) = A.Recovery_Unclean);
   Facts := Original; Facts.Observed_Live := Facts.Observed_Stage;
   Check (A.Decide (W.Decode (Facts)) = A.Live_Changed);
   Facts := Original; Facts.Observed_Stage := Facts.Observed_Live;
   Check (A.Decide (W.Decode (Facts)) = A.Stage_Changed);
   Facts := Original; Facts.Expected_Stage := Facts.Expected_Live;
   Facts.Observed_Stage := Facts.Observed_Live;
   Check (A.Decide (W.Decode (Facts)) = A.Same_Entry_Refused);
   Facts := Original; Facts.Observed_Marker_Digest := Worldline.Zero_Hash;
   Check (A.Decide (W.Decode (Facts)) = A.Marker_Mismatch);
   Facts := Original; Facts.Collapse_Facts.Expected_Subject.Present := 0;
   Check (not W.Well_Formed (Facts));
end Physical_Value_Controls;
