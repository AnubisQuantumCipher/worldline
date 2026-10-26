with Ada.Command_Line;
with Ada.Exceptions;
with Ada.Text_IO;
with Resource_Quantities;
with SPARK.Big_Integers;

-- Diagnostic only: no daemon, authority operation or external input.
procedure Significant_Magnitude_Counterexample is
   pragma Assertion_Policy (Check);
   package Q renames Resource_Quantities;
   use type SPARK.Big_Integers.Big_Integer;
   Data : constant Q.Byte_Array (1 .. 805) := [805 => 1, others => 0];
   Original : constant Q.Quantity := (False, Data'First, Data'Length);
begin
   -- This is a genuinely significant 805th byte, not redundant zero padding.
   -- The original public model admits this span and promises its magnitude.
   pragma Assert
     (Q.Magnitude (Data, Original) >= SPARK.Big_Integers.To_Big_Integer (0));
   Ada.Text_IO.Put_Line ("PASS: admitted significant magnitude model completed");
exception
   when Error : others =>
      Ada.Text_IO.Put_Line
        (Ada.Text_IO.Standard_Error, Ada.Exceptions.Exception_Information (Error));
      Ada.Command_Line.Set_Exit_Status (Ada.Command_Line.Failure);
end Significant_Magnitude_Counterexample;
