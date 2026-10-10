with Ada.Text_IO;
with Worldline.Evaluation_Authority;
procedure Test_Evaluation_Authority is
   package A renames Worldline.Evaluation_Authority;
   package W renames A.W;
   use type W.Byte;
   Raw : W.Raw_Record := W.Zero_Record;
begin
   pragma Assert (A.Report_Of (Raw) = W.E.Report_Integrity'Pos (W.E.Not_Applicable));
   Raw.Observations (W.Source_Field) := W.E.Origin'Pos (W.E.Engine);
   Raw.Observations (W.Status_Field) := W.E.Raw_Status'Pos (W.E.Pass_Status);
   Raw.Presence := (others => 1);
   pragma Assert (W.Admit_Wire (Raw) = 1);
   pragma Assert (A.Report_Of (Raw) = W.E.Report_Integrity'Pos (W.E.Not_Applicable));
   Raw.Report_Based := W.Invalid_Record;
   pragma Assert (A.Report_Of (Raw) = W.Invalid_Record);
   Ada.Text_IO.Put_Line ("ordinary raw authority query controls passed");
end Test_Evaluation_Authority;
