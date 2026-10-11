with Ada.Text_IO;
with Archive_Leaf_Fixtures;

--  Finite unexecuted codec controls. No equivalence/authentication/proof claim.
procedure Archive_Leaf_Controls is
begin
   Archive_Leaf_Fixtures.Run;
   Ada.Text_IO.Put_Line ("ARCHIVE_LEAF_CONTROLS_PASS");
end Archive_Leaf_Controls;
