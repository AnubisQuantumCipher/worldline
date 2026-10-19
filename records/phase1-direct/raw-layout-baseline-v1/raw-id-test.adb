with Ada.Text_IO;
with System;
with Resource_Quantities;
with Resource_Run_Ledger_Wire;
with Worldline.Retained_Raw_Decode;

procedure Raw_Decode_Tests is
   package Q renames Resource_Quantities;
   package W renames Resource_Run_Ledger_Wire;
   package D renames Worldline.Retained_Raw_Decode;
   use type Q.Byte_Count;
   use type W.U8;
   use type W.I64;
   Width : constant Q.Byte_Count := W.Raw_Id'Size / System.Storage_Unit;

   procedure Check_Id (First : Q.Byte_Index) is
      Data : constant Q.Byte_Array (First .. First + (Width - 1)) := [others => 255];
      Value : constant W.Raw_Id := D.Load (Data);
   begin
      pragma Assert (Value.Present = 255);
      pragma Assert (Value.First = -1 and then Value.Length = -1);
   end Check_Id;
begin
   Check_Id (7);
   Ada.Text_IO.Put_Line ("PASS rebased raw ID decoding");
   Check_Id (Q.Byte_Index'Last - (Width - 1));
   Ada.Text_IO.Put_Line ("PASS maximum-index raw ID decoding");
end Raw_Decode_Tests;
