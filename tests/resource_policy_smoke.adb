with Ada.Text_IO;
with Ada.Exceptions;
with Resource_Quantities;
with Resource_Admission;

procedure Resource_Policy_Smoke is
   package Q renames Resource_Quantities;
   package P renames Resource_Admission;
   Data : constant Q.Byte_Array := [1 => 1, 2 => 2];
   One : constant Q.Quantity := (False, 1, 1);
   Two : constant Q.Quantity := (False, 2, 1);
   Zero : constant Q.Quantity := (False, 1, 0);
   Policy : constant P.Policy_Input :=
     (Outstanding_Count => One,
      Concurrency_Limit => (Present => True, Value => One),
      Memory_Pressure => (Present => False),
      Memory_Pressure_Ceiling => Two,
      Disk_Byte_Floor => Two, Disk_Inode_Floor => Two,
      Available_Memory => Two, Withheld_Memory => Zero,
      Memory_Floor => Zero, Requested_Memory => Zero);
   Empty : constant P.Disk_Array (1 .. 0) := [others => (One, Two)];
begin
   Ada.Text_IO.Put_Line ("compare=" & Q.Ordering'Image (Q.Compare (Data, One, Two)));
   Ada.Text_IO.Put_Line ("binary=" & P.Check_Status'Image
     (P.Check_Binary (Data, One, One, P.At_Least,
                     P.Outstanding_Count_Field, P.Concurrency_Limit_Field).Status));
   Ada.Text_IO.Put_Line ("admit=" & P.Gate'Image (P.Admit (Data, Policy, Empty).Failed_Gate));
exception
   when E : others =>
      Ada.Text_IO.Put_Line (Ada.Exceptions.Exception_Information (E));
      raise;
end Resource_Policy_Smoke;
