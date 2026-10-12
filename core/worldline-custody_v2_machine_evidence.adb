with Interfaces;
with System;
with SPARK.Big_Integers;
with Resource_Ledger;
with Resource_Run_Ledger;
with Worldline.Resource_Policy_C_API;
with Worldline.Resource_Ledger_C_API;
package body Worldline.Custody_V2_Machine_Evidence with SPARK_Mode is
   package P renames Worldline.Resource_Policy_C_API;
   package L renames Worldline.Resource_Ledger_C_API;
   package Q renames E.Q;
   use SPARK.Big_Integers;
   use type Q.Byte_Count;
   use type Q.Byte_Array;
   use type Interfaces.Unsigned_64;
   use type P.Size;
   use type P.Quantity_C;
   use type Resource_Ledger.Result_Status;
   Blank_Quantity : constant P.Quantity_C := (1, 0, 0);
   Blank_Optional : constant P.Optional_C := (0, Blank_Quantity);
   Blank_Input : constant P.Input_C :=
     (Concurrency_Limit => Blank_Optional, Memory_Pressure => Blank_Optional, others => Blank_Quantity);
   Blank_Disk : constant P.Disk_C := (Blank_Quantity, Blank_Quantity);
   Blank_Row : constant L.Row_C := (Blank_Quantity, Blank_Optional, 0, 0);
   Blank_Policy_Result : constant P.Result_C := (0, 0, 0, 0, 0);
   Blank_Ledger_Result : constant L.Result_C := (0, Blank_Quantity);
   Magnitude_Field : constant String := "magnitude";
   --  Wire offsets of the C records. GNATprove models 'Position as an opaque value (only >= 0 is
   --  known), so the offsets are named here and pinned to the real layout at compile time, exactly as
   --  the Resource_Policy_C_API / Resource_Ledger_C_API bodies pin theirs.
   Quantity_First_Offset : constant := 0;  Quantity_Length_Offset : constant := 8;  Quantity_Negative_Offset : constant := 16;
   Optional_Present_Offset : constant := 0;  Optional_Value_Offset : constant := 8;
   Input_Outstanding_Count_Offset : constant := 0;  Input_Concurrency_Limit_Offset : constant := 24;
   Input_Memory_Pressure_Offset : constant := 56;  Input_Memory_Pressure_Ceiling_Offset : constant := 88;
   Input_Disk_Byte_Floor_Offset : constant := 112;  Input_Disk_Inode_Floor_Offset : constant := 136;
   Input_Available_Memory_Offset : constant := 160;  Input_Withheld_Memory_Offset : constant := 184;
   Input_Memory_Floor_Offset : constant := 208;  Input_Requested_Memory_Offset : constant := 232;
   Disk_Free_Bytes_Offset : constant := 0;  Disk_Free_Inodes_Offset : constant := 24;
   Row_Reserved_Offset : constant := 0;  Row_Used_Offset : constant := 24;
   Row_Output_First_Offset : constant := 56;  Row_Output_Length_Offset : constant := 64;
   Policy_Status_Offset : constant := 0;  Policy_Failed_Gate_Offset : constant := 1;  Policy_Field_Offset : constant := 2;
   Policy_Disk_Present_Offset : constant := 3;  Policy_Disk_Index_Offset : constant := 8;
   Ledger_Status_Offset : constant := 0;  Ledger_Total_Offset : constant := 8;
   pragma Compile_Time_Error
     (Blank_Quantity.First'Position /= Quantity_First_Offset or else
      Blank_Quantity.Length'Position /= Quantity_Length_Offset or else
      Blank_Quantity.Negative'Position /= Quantity_Negative_Offset, "Quantity_C wire offsets");
   pragma Compile_Time_Error
     (Blank_Optional.Present'Position /= Optional_Present_Offset or else
      Blank_Optional.Value'Position /= Optional_Value_Offset, "Optional_C wire offsets");
   pragma Compile_Time_Error
     (Blank_Input.Outstanding_Count'Position /= Input_Outstanding_Count_Offset or else
      Blank_Input.Concurrency_Limit'Position /= Input_Concurrency_Limit_Offset or else
      Blank_Input.Memory_Pressure'Position /= Input_Memory_Pressure_Offset or else
      Blank_Input.Memory_Pressure_Ceiling'Position /= Input_Memory_Pressure_Ceiling_Offset or else
      Blank_Input.Disk_Byte_Floor'Position /= Input_Disk_Byte_Floor_Offset or else
      Blank_Input.Disk_Inode_Floor'Position /= Input_Disk_Inode_Floor_Offset or else
      Blank_Input.Available_Memory'Position /= Input_Available_Memory_Offset or else
      Blank_Input.Withheld_Memory'Position /= Input_Withheld_Memory_Offset or else
      Blank_Input.Memory_Floor'Position /= Input_Memory_Floor_Offset or else
      Blank_Input.Requested_Memory'Position /= Input_Requested_Memory_Offset, "Input_C wire offsets");
   pragma Compile_Time_Error
     (Blank_Disk.Free_Bytes'Position /= Disk_Free_Bytes_Offset or else
      Blank_Disk.Free_Inodes'Position /= Disk_Free_Inodes_Offset, "Disk_C wire offsets");
   pragma Compile_Time_Error
     (Blank_Row.Reserved'Position /= Row_Reserved_Offset or else Blank_Row.Used'Position /= Row_Used_Offset or else
      Blank_Row.Output_First'Position /= Row_Output_First_Offset or else
      Blank_Row.Output_Length'Position /= Row_Output_Length_Offset, "Row_C wire offsets");
   pragma Compile_Time_Error
     (Blank_Policy_Result.Status'Position /= Policy_Status_Offset or else
      Blank_Policy_Result.Failed_Gate'Position /= Policy_Failed_Gate_Offset or else
      Blank_Policy_Result.Field'Position /= Policy_Field_Offset or else
      Blank_Policy_Result.Disk_Present'Position /= Policy_Disk_Present_Offset or else
      Blank_Policy_Result.Disk_Index'Position /= Policy_Disk_Index_Offset, "policy Result_C wire offsets");
   pragma Compile_Time_Error
     (Blank_Ledger_Result.Status'Position /= Ledger_Status_Offset or else
      Blank_Ledger_Result.Total'Position /= Ledger_Total_Offset, "ledger Result_C wire offsets");
   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span
     renames V.Record_Field;
   function Word (Raw : E.Bytes; Offset : E.Count; Length : E.Count)
      return Interfaces.Unsigned_64
     with Post => (if Length <= 1 then Word'Result <= 255)
   is
      Result : Interfaces.Unsigned_64 := 0;
   begin
      if Length > 8 or else Offset > Raw'Length or else Length > Raw'Length - Offset then return 0; end if;
      for I in E.Count range 1 .. Length loop
         pragma Loop_Invariant (if Length <= 1 then Result <= 255);
         Result := Result or Interfaces.Shift_Left
           (Interfaces.Unsigned_64 (Raw (Raw'First + (Offset + I - 1))), Natural ((I - 1) * 8));
      end loop;
      return Result;
   end Word;
   function Quantity (Raw : E.Bytes; Offset : E.Count) return P.Quantity_C
     with Global => null
   is
      Sample : P.Quantity_C := (1, 0, 0);
   begin
      if Offset > Raw'Length or else P.Quantity_C'Size / System.Storage_Unit > Raw'Length - Offset then return Sample; end if;
      Sample.First := P.Size (Word (Raw, Offset + Quantity_First_Offset, Sample.First'Size / System.Storage_Unit));
      Sample.Length := P.Size (Word (Raw, Offset + Quantity_Length_Offset, Sample.Length'Size / System.Storage_Unit));
      Sample.Negative := Q.Byte (Word (Raw, Offset + Quantity_Negative_Offset, 1));
      return Sample;
   end Quantity;
   function Optional (Raw : E.Bytes; Offset : E.Count) return P.Optional_C
     with Global => null
   is
      Sample : P.Optional_C := (0, (1, 0, 0));
   begin
      if Offset > Raw'Length or else P.Optional_C'Size / System.Storage_Unit > Raw'Length - Offset then return Sample; end if;
      Sample.Present := Q.Byte (Word (Raw, Offset + Optional_Present_Offset, 1));
      Sample.Value := Quantity (Raw, Offset + Optional_Value_Offset);
      return Sample;
   end Optional;
   function Input (Raw : E.Bytes) return P.Input_C
     with Global => null
   is
      Sample : P.Input_C;
   begin
      Sample.Outstanding_Count := Quantity (Raw, Input_Outstanding_Count_Offset);
      Sample.Concurrency_Limit := Optional (Raw, Input_Concurrency_Limit_Offset);
      Sample.Memory_Pressure := Optional (Raw, Input_Memory_Pressure_Offset);
      Sample.Memory_Pressure_Ceiling := Quantity (Raw, Input_Memory_Pressure_Ceiling_Offset);
      Sample.Disk_Byte_Floor := Quantity (Raw, Input_Disk_Byte_Floor_Offset);
      Sample.Disk_Inode_Floor := Quantity (Raw, Input_Disk_Inode_Floor_Offset);
      Sample.Available_Memory := Quantity (Raw, Input_Available_Memory_Offset);
      Sample.Withheld_Memory := Quantity (Raw, Input_Withheld_Memory_Offset);
      Sample.Memory_Floor := Quantity (Raw, Input_Memory_Floor_Offset);
      Sample.Requested_Memory := Quantity (Raw, Input_Requested_Memory_Offset);
      return Sample;
   end Input;
   function Shape (Arena : E.Bytes; Item : P.Quantity_C) return Boolean is
     (Item.Negative <= 1 and then Item.First <= P.Size (Q.Byte_Count'Last) and then
      Item.Length <= P.Size (Q.Byte_Count'Last) and then
      (Item.Length = 0 or else (Item.First > 0 and then Item.First <= P.Size (Arena'Length) and then
       Item.Length <= P.Size (Arena'Length) - Item.First + 1)));
   function Value (Arena : E.Bytes; Item : P.Quantity_C) return Valid_Big_Integer is
   begin
      if not Shape (Arena, Item) then return To_Big_Integer (0); end if;
      return Resource_Run_Ledger.Exact_Value
        (Arena, (Item.Negative /= 0, (if Item.Length = 0 then 1 else Q.Byte_Index (Item.First)), Q.Byte_Count (Item.Length)));
   end Value;
   function Lossless_Number (Data : E.Bytes; Item : E.Span) return Boolean is
     (V.Text_Is (Data, F (Data, Item, "kind"), "int-magnitude") and then
      V.Valid_Hex_Field (Data, Item, Magnitude_Field) and then
      V.Type_Is (Data, F (Data, Item, "negative"), "bool"));
   function Matches (Data : E.Bytes; Item : E.Span; Arena : E.Bytes;
                     Raw : P.Quantity_C) return Boolean is
   begin
      if not Shape (Arena, Raw) or else not Lossless_Number (Data, Item) then return False; end if;
      declare Magnitude : constant E.Bytes := V.Hex_Value (Data, Item, Magnitude_Field); begin
         return Value (Arena, Raw) = Resource_Run_Ledger.Exact_Value
           (Magnitude, (E.Decode (Data, F (Data, Item, "negative"), E.Operation).Boolean_Bit,
                        (if Magnitude'Length = 0 then 1 else Magnitude'First), Magnitude'Length));
      end;
   end Matches;
   function Optional_Matches (Data : E.Bytes; Item : E.Span; Arena : E.Bytes;
                              Raw : P.Optional_C) return Boolean is
     (Raw.Present <= 1 and then
       (if Raw.Present = 0 then V.Text_Is (Data, F (Data, Item, "kind"), "NoneType")
        else Matches (Data, Item, Arena, Raw.Value)));
   function Zero (Data : E.Bytes; Item : E.Span) return Boolean is
      Count : constant V.Count_Result := V.Nonnegative_Count (Data, Item);
   begin return Count.Present and then Count.Value = 0; end Zero;
   function Count_Is (Data : E.Bytes; Item : E.Span; Expected : E.Count) return Boolean is
      Count : constant V.Count_Result := V.Nonnegative_Count (Data, Item);
   begin return Count.Present and then Count.Value = Expected; end Count_Is;
   function Joined (Data : E.Bytes; Machine : E.Span) return Boolean is
      Policy : constant E.Span := F (Data, Machine, "full_original_policy_native");
      Ledger : constant E.Span := F (Data, Machine, "full_original_ledger_native");
      NI : constant E.Span := F (Data, F (Data, Machine, "native_input"), "value");
      Disk_Input : constant E.Span := F (Data, F (Data, NI, "disks"), "value");
      Ledger_Input : constant E.Span := F (Data, F (Data, Machine, "ledger_input"), "value");
      Slots : constant E.Span := F (Data, Ledger, "slots");
      PA_Span : constant E.Span := F (Data, Policy, "arena");
      PI_Span : constant E.Span := F (Data, Policy, "input");
      PD_Span : constant E.Span := F (Data, Policy, "disks");
      PO_Span : constant E.Span := F (Data, Policy, "output");
      LA_Span : constant E.Span := F (Data, Ledger, "arena");
      LR_Span : constant E.Span := F (Data, Ledger, "rows");
      Detail_Span : constant E.Span := F (Data, Ledger, "detail_output");
      Total_Span : constant E.Span := F (Data, Ledger, "total_output");
      Quantities_Span : constant E.Span := F (Data, Ledger, "details");
      LO_Span : constant E.Span := F (Data, Ledger, "output");
   begin
      if not V.Valid (Data, Machine) or else
         not V.Text_Is (Data, F (Data, Machine, "schema"), "worldline.protected-machine-admission-v1") or else
         not V.Text_Is (Data, F (Data, Policy, "entry_point"), "wl_resource_policy_admit") or else
         not V.Text_Is (Data, F (Data, Ledger, "entry_point"), "wl_resource_ledger_compute") or else
         not Zero (Data, F (Data, Policy, "transport_status")) or else
         not Zero (Data, F (Data, Ledger, "transport_status")) or else
         not V.Valid_Bytes (Data, PA_Span) or else not V.Valid_Bytes (Data, PI_Span) or else
         not V.Valid_Bytes (Data, PD_Span) or else not V.Valid_Bytes (Data, PO_Span) or else
         not V.Valid_Bytes (Data, LA_Span) or else not V.Valid_Bytes (Data, LR_Span) or else
         not V.Valid_Bytes (Data, Detail_Span) or else not V.Valid_Bytes (Data, Total_Span) or else
         not V.Valid_Bytes (Data, Quantities_Span) or else not V.Valid_Bytes (Data, LO_Span) or else
         not V.Is_Sequence (Data, Disk_Input) or else not V.Is_Sequence (Data, Ledger_Input) or else
         not V.Is_Sequence (Data, Slots)
      then return False; end if;
      declare
         PA : aliased E.Bytes := V.Bytes_Value (Data, PA_Span);
         PI : constant E.Bytes := V.Bytes_Value (Data, PI_Span);
         PD : constant E.Bytes := V.Bytes_Value (Data, PD_Span);
         PO : constant E.Bytes := V.Bytes_Value (Data, PO_Span);
         LA : aliased E.Bytes := V.Bytes_Value (Data, LA_Span);
         LR : constant E.Bytes := V.Bytes_Value (Data, LR_Span);
         Expected_Detail : constant E.Bytes := V.Bytes_Value (Data, Detail_Span);
         Expected_Total : constant E.Bytes := V.Bytes_Value (Data, Total_Span);
         Expected_Quantities : constant E.Bytes := V.Bytes_Value (Data, Quantities_Span);
         LO : constant E.Bytes := V.Bytes_Value (Data, LO_Span);
         Disk_Size : constant E.Count := P.Disk_C'Size / System.Storage_Unit;
         Row_Size : constant E.Count := L.Row_C'Size / System.Storage_Unit;
         Quantity_Size : constant E.Count := P.Quantity_C'Size / System.Storage_Unit;
      begin
         if PI'Length /= P.Input_C'Size / System.Storage_Unit or else
            PO'Length /= P.Result_C'Size / System.Storage_Unit or else PD'Length mod Disk_Size /= 0 or else
            LR'Length mod Row_Size /= 0 or else LO'Length /= L.Result_C'Size / System.Storage_Unit or else
            Expected_Quantities'Length /= LR'Length / Row_Size * Quantity_Size or else
            V.Count (Data, Disk_Input) /= PD'Length / Disk_Size or else
            V.Count (Data, Ledger_Input) /= LR'Length / Row_Size or else
            V.Count (Data, Slots) /= LR'Length / Row_Size or else
            not Count_Is (Data, F (Data, Policy, "disk_count"), PD'Length / Disk_Size) or else
            not Count_Is (Data, F (Data, Ledger, "row_count"), LR'Length / Row_Size)
         then return False; end if;
         declare
            Policy_Input : aliased P.Input_C := Input (PI);
            Disks : aliased P.Disk_Array := [1 .. PD'Length / Disk_Size => Blank_Disk];
            Rows : aliased L.Row_Array := [1 .. LR'Length / Row_Size => Blank_Row];
            Details : Resource_Ledger.Quantity_Array (Rows'Range);
            Detail_Arena : E.Bytes (1 .. Expected_Detail'Length);
            Total_Arena : E.Bytes (1 .. Expected_Total'Length);
            Total : Q.Quantity;
            Ledger_Status : Resource_Ledger.Result_Status;
            Policy_Result : P.Result_C;
            Transport : Q.Byte;
            function Input_Field (Name : String; Raw : P.Quantity_C) return Boolean is
              (Matches (Data, F (Data, NI, Name), PA, Raw));
         begin
            if not Input_Field ("outstanding_count", Policy_Input.Outstanding_Count) or else
               not Optional_Matches (Data, F (Data, NI, "concurrency_limit"), PA, Policy_Input.Concurrency_Limit) or else
               not Optional_Matches (Data, F (Data, NI, "memory_pressure"), PA, Policy_Input.Memory_Pressure) or else
               not Input_Field ("memory_pressure_ceiling", Policy_Input.Memory_Pressure_Ceiling) or else
               not Input_Field ("disk_byte_floor", Policy_Input.Disk_Byte_Floor) or else
               not Input_Field ("disk_inode_floor", Policy_Input.Disk_Inode_Floor) or else
               not Input_Field ("available_memory", Policy_Input.Available_Memory) or else
               not Input_Field ("withheld_memory", Policy_Input.Withheld_Memory) or else
               not Input_Field ("memory_floor", Policy_Input.Memory_Floor) or else
               not Input_Field ("requested_memory", Policy_Input.Requested_Memory)
            then return False; end if;
            for I in Disks'Range loop
               Disks (I) := (Quantity (PD, (I - 1) * Disk_Size + Disk_Free_Bytes_Offset),
                             Quantity (PD, (I - 1) * Disk_Size + Disk_Free_Inodes_Offset));
               declare Pair : constant E.Span := F (Data, V.Element (Data, Disk_Input, I - 1), "value"); begin
                  if V.Count (Data, Pair) /= 2 or else
                     not Matches (Data, V.Element (Data, Pair, 0), PA, Disks (I).Free_Bytes) or else
                     not Matches (Data, V.Element (Data, Pair, 1), PA, Disks (I).Free_Inodes) then return False; end if;
               end;
            end loop;
            for I in Rows'Range loop
               Rows (I) := (Quantity (LR, (I - 1) * Row_Size + Row_Reserved_Offset),
                 Optional (LR, (I - 1) * Row_Size + Row_Used_Offset),
                 P.Size (Word (LR, (I - 1) * Row_Size + Row_Output_First_Offset, Blank_Row.Output_First'Size / System.Storage_Unit)),
                 P.Size (Word (LR, (I - 1) * Row_Size + Row_Output_Length_Offset, Blank_Row.Output_Length'Size / System.Storage_Unit)));
               declare Pair : constant E.Span := F (Data, V.Element (Data, Ledger_Input, I - 1), "value"); begin
                  if V.Count (Data, Pair) /= 2 or else
                     not Matches (Data, V.Element (Data, Pair, 0), LA, Rows (I).Reserved) or else
                     not Optional_Matches (Data, V.Element (Data, Pair, 1), LA, Rows (I).Used) then return False; end if;
               end;
               declare
                  Slot : constant E.Span := V.Element (Data, Slots, I - 1);
                  First : constant V.Count_Result := V.Nonnegative_Count (Data, V.Element (Data, Slot, 0));
                  Length : constant V.Count_Result := V.Nonnegative_Count (Data, V.Element (Data, Slot, 1));
               begin
                  if not V.Is_Sequence (Data, Slot) or else V.Count (Data, Slot) /= 2 or else
                     not First.Present or else not Length.Present or else
                     P.Size (First.Value) /= Rows (I).Output_First or else
                     P.Size (Length.Value) /= Rows (I).Output_Length then return False; end if;
               end;
            end loop;
            declare
               LA_Ref : constant not null access constant Q.Byte_Array := LA'Access;
               Rows_Ref : constant not null access constant L.Row_Array := Rows'Access;
            begin
               Transport := L.Compute (LA_Ref, Rows_Ref, Detail_Arena, Total_Arena, Details, Total, Ledger_Status);
            end;
            if Transport /= 0 or else Ledger_Status /= Resource_Ledger.Computed or else
               Detail_Arena /= Expected_Detail or else Total_Arena /= Expected_Total or else
               Word (LO, Ledger_Status_Offset, 1) /= Resource_Ledger.Result_Status'Pos (Ledger_Status) or else
               Quantity (LO, Ledger_Total_Offset) /= L.Encode (Total) or else
               not Shape (Total_Arena, Quantity (LO, Ledger_Total_Offset)) or else
               Value (Total_Arena, Quantity (LO, Ledger_Total_Offset)) /=
                 Resource_Run_Ledger.Exact_Value (Total_Arena, Total) or else
               Value (PA, Policy_Input.Withheld_Memory) /= Resource_Run_Ledger.Exact_Value (Total_Arena, Total)
            then return False; end if;
            for I in Details'Range loop
               if not Shape (Detail_Arena, Quantity (Expected_Quantities, (I - 1) * Quantity_Size)) or else
                  Quantity (Expected_Quantities, (I - 1) * Quantity_Size) /= L.Encode (Details (I)) or else
                  Value (Detail_Arena, Quantity (Expected_Quantities, (I - 1) * Quantity_Size)) /=
                    Resource_Run_Ledger.Exact_Value (Detail_Arena, Details (I)) then return False; end if;
            end loop;
            declare
               PA_Ref : constant not null access constant Q.Byte_Array := PA'Access;
               Policy_Input_Ref : constant not null access constant P.Input_C := Policy_Input'Access;
               Disks_Ref : constant not null access constant P.Disk_Array := Disks'Access;
            begin
               Transport := P.Admit (PA_Ref, Policy_Input_Ref, Disks_Ref, Policy_Result);
            end;
            return Transport = 0 and then Policy_Result.Status = 0 and then Policy_Result.Failed_Gate = 0 and then
              Policy_Result.Disk_Present = 0 and then
              Word (PO, Policy_Status_Offset, 1) = Interfaces.Unsigned_64 (Policy_Result.Status) and then
              Word (PO, Policy_Failed_Gate_Offset, 1) = Interfaces.Unsigned_64 (Policy_Result.Failed_Gate) and then
              Word (PO, Policy_Field_Offset, 1) = Interfaces.Unsigned_64 (Policy_Result.Field) and then
              Word (PO, Policy_Disk_Present_Offset, 1) = Interfaces.Unsigned_64 (Policy_Result.Disk_Present) and then
              Word (PO, Policy_Disk_Index_Offset, Blank_Policy_Result.Disk_Index'Size / System.Storage_Unit) =
                 Interfaces.Unsigned_64 (Policy_Result.Disk_Index);
         end;
      end;
   end Joined;
end Worldline.Custody_V2_Machine_Evidence;
