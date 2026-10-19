with Ada.Text_IO;
with Resource_Quantities;
with Worldline.Resource_Policy_C_API;

--  Exercise the real typed entry point with owned storage and malformed wire
--  shapes. These controls do not claim foreign-pointer or host provenance.
procedure Resource_Policy_Transport_Tests is
   package Q renames Resource_Quantities;
   package T renames Worldline.Resource_Policy_C_API;
   use type T.U8;
   use type T.Input_C;
   use type T.Disk_C;
   use type T.Result_C;
   type Fault is (Data_Bounds, Disk_Bounds, Input_Shape, Disk_Shape);

   procedure Check (Problem : Fault) is
      Data_First : constant Q.Byte_Index :=
        (if Problem = Data_Bounds then 2 else 1);
      Disk_First : constant Q.Byte_Index :=
        (if Problem = Disk_Bounds then 2 else 1);
      Data : aliased Q.Byte_Array := [Data_First => 7];
      Zero : constant T.Quantity_C := (1, 0, 0);
      Input : aliased T.Input_C :=
        (Concurrency_Limit | Memory_Pressure => (0, Zero), others => Zero);
      Disks : aliased T.Disk_Array :=
        [Disk_First => (Free_Bytes | Free_Inodes => Zero)];
      Result : T.Result_C := (Disk_Index => 17, others => 165);
      Code : T.U8;
   begin
      if Problem = Input_Shape then Input.Outstanding_Count.Negative := 2; end if;
      if Problem = Disk_Shape then Disks (Disk_First).Free_Bytes.Negative := 2; end if;
      declare
         Saved_Input : constant T.Input_C := Input;
         Saved_Disk : constant T.Disk_C := Disks (Disk_First);
      begin
         Code := T.Admit (Data'Access, Input'Access, Disks'Access, Result);
         pragma Assert (Code = 255);
         pragma Assert (Result = T.Result_C'(Disk_Index => 0, others => 0));
         pragma Assert (Input = Saved_Input and then Disks (Disk_First) = Saved_Disk);
         pragma Assert (Data (Data_First) = 7);
      end;
   end Check;
begin
   for Problem in Fault loop Check (Problem); end loop;
   Ada.Text_IO.Put_Line ("PASS typed policy malformed-input refusal controls");
end Resource_Policy_Transport_Tests;
