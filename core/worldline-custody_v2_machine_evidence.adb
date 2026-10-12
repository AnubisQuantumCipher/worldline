with Interfaces;
with Interfaces.C;
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
   use type Q.Byte;
   use type Q.Byte_Array;
   use type Interfaces.Unsigned_64;
   use type P.Size;
   use type P.Quantity_C;
   use type Resource_Ledger.Result_Status;
   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span
     renames V.Record_Field;
   function Word (Raw : E.Bytes; Offset : E.Count; Length : E.Count)
      return Interfaces.Unsigned_64
   is
      Result : Interfaces.Unsigned_64 := 0;
   begin
      if Length > 8 or else Offset > Raw'Length or else Length > Raw'Length - Offset then return 0; end if;
      for I in E.Count range 1 .. Length loop
         Result := Result or Interfaces.Shift_Left
           (Interfaces.Unsigned_64 (Raw (Raw'First + Offset + I - 1)), Natural ((I - 1) * 8));
      end loop;
      return Result;
   end Word;
   function Quantity (Raw : E.Bytes; Offset : E.Count) return P.Quantity_C is
      Sample : P.Quantity_C := (1, 0, 0);
   begin
      if Offset > Raw'Length or else P.Quantity_C'Size / System.Storage_Unit > Raw'Length - Offset then return Sample; end if;
      Sample.First := P.Size (Word (Raw, Offset + Sample.First'Position, Sample.First'Size / System.Storage_Unit));
      Sample.Length := P.Size (Word (Raw, Offset + Sample.Length'Position, Sample.Length'Size / System.Storage_Unit));
      Sample.Negative := Q.Byte (Word (Raw, Offset + Sample.Negative'Position, 1));
      return Sample;
   end Quantity;
   function Optional (Raw : E.Bytes; Offset : E.Count) return P.Optional_C is
      Sample : P.Optional_C := (0, (1, 0, 0));
   begin
      if Offset > Raw'Length or else P.Optional_C'Size / System.Storage_Unit > Raw'Length - Offset then return Sample; end if;
      Sample.Present := Q.Byte (Word (Raw, Offset + Sample.Present'Position, 1));
      Sample.Value := Quantity (Raw, Offset + Sample.Value'Position);
      return Sample;
   end Optional;
   function Input (Raw : E.Bytes) return P.Input_C is
      Sample : P.Input_C;
   begin
      Sample.Outstanding_Count := Quantity (Raw, Sample.Outstanding_Count'Position);
      Sample.Concurrency_Limit := Optional (Raw, Sample.Concurrency_Limit'Position);
      Sample.Memory_Pressure := Optional (Raw, Sample.Memory_Pressure'Position);
      Sample.Memory_Pressure_Ceiling := Quantity (Raw, Sample.Memory_Pressure_Ceiling'Position);
      Sample.Disk_Byte_Floor := Quantity (Raw, Sample.Disk_Byte_Floor'Position);
      Sample.Disk_Inode_Floor := Quantity (Raw, Sample.Disk_Inode_Floor'Position);
      Sample.Available_Memory := Quantity (Raw, Sample.Available_Memory'Position);
      Sample.Withheld_Memory := Quantity (Raw, Sample.Withheld_Memory'Position);
      Sample.Memory_Floor := Quantity (Raw, Sample.Memory_Floor'Position);
      Sample.Requested_Memory := Quantity (Raw, Sample.Requested_Memory'Position);
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
      V.Valid_Hex_Field (Data, Item, "magnitude") and then
      V.Type_Is (Data, F (Data, Item, "negative"), "bool"));
   function Matches (Data : E.Bytes; Item : E.Span; Arena : E.Bytes;
                     Raw : P.Quantity_C) return Boolean is
   begin
      if not Shape (Arena, Raw) or else not Lossless_Number (Data, Item) then return False; end if;
      declare Magnitude : constant E.Bytes := V.Hex_Value (Data, Item, "magnitude"); begin
         return Value (Arena, Raw) = Resource_Run_Ledger.Exact_Value
           (Magnitude, (E.Decode (Data, F (Data, Item, "negative"), E.Operation).Boolean_Bit,
                        Magnitude'First, Magnitude'Length));
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
   begin
      if not V.Valid (Data, Machine) or else
         not V.Text_Is (Data, F (Data, Machine, "schema"), "worldline.protected-machine-admission-v1") or else
         not V.Text_Is (Data, F (Data, Policy, "entry_point"), "wl_resource_policy_admit") or else
         not V.Text_Is (Data, F (Data, Ledger, "entry_point"), "wl_resource_ledger_compute") or else
         not Zero (Data, F (Data, Policy, "transport_status")) or else
         not Zero (Data, F (Data, Ledger, "transport_status")) or else
         not V.Valid_Bytes (Data, F (Data, Policy, "arena")) or else
         not V.Valid_Bytes (Data, F (Data, Policy, "input")) or else
         not V.Valid_Bytes (Data, F (Data, Policy, "disks")) or else
         not V.Valid_Bytes (Data, F (Data, Policy, "output")) or else
         not V.Valid_Bytes (Data, F (Data, Ledger, "arena")) or else
         not V.Valid_Bytes (Data, F (Data, Ledger, "rows")) or else
         not V.Valid_Bytes (Data, F (Data, Ledger, "detail_output")) or else
         not V.Valid_Bytes (Data, F (Data, Ledger, "total_output")) or else
         not V.Valid_Bytes (Data, F (Data, Ledger, "details")) or else
         not V.Valid_Bytes (Data, F (Data, Ledger, "output")) or else
         not V.Is_Sequence (Data, Disk_Input) or else not V.Is_Sequence (Data, Ledger_Input) or else
         not V.Is_Sequence (Data, Slots)
      then return False; end if;
      declare
         PA : aliased E.Bytes := V.Bytes_Value (Data, F (Data, Policy, "arena"));
         PI : constant E.Bytes := V.Bytes_Value (Data, F (Data, Policy, "input"));
         PD : constant E.Bytes := V.Bytes_Value (Data, F (Data, Policy, "disks"));
         PO : constant E.Bytes := V.Bytes_Value (Data, F (Data, Policy, "output"));
         LA : aliased E.Bytes := V.Bytes_Value (Data, F (Data, Ledger, "arena"));
         LR : constant E.Bytes := V.Bytes_Value (Data, F (Data, Ledger, "rows"));
         Expected_Detail : constant E.Bytes := V.Bytes_Value (Data, F (Data, Ledger, "detail_output"));
         Expected_Total : constant E.Bytes := V.Bytes_Value (Data, F (Data, Ledger, "total_output"));
         Expected_Quantities : constant E.Bytes := V.Bytes_Value (Data, F (Data, Ledger, "details"));
         LO : constant E.Bytes := V.Bytes_Value (Data, F (Data, Ledger, "output"));
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
            Disks : aliased P.Disk_Array := [1 .. PD'Length / Disk_Size => <>];
            Rows : aliased L.Row_Array := [1 .. LR'Length / Row_Size => <>];
            Details : Resource_Ledger.Quantity_Array (Rows'Range);
            Detail_Arena : E.Bytes (1 .. Expected_Detail'Length);
            Total_Arena : E.Bytes (1 .. Expected_Total'Length);
            Total : Q.Quantity;
            Ledger_Status : Resource_Ledger.Result_Status;
            Policy_Result : P.Result_C;
            Transport : Q.Byte;
            Disk_Sample : P.Disk_C;
            Row_Sample : L.Row_C;
            Policy_Result_Sample : P.Result_C;
            Ledger_Result_Sample : L.Result_C;
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
               Disks (I) := (Quantity (PD, (I - 1) * Disk_Size + Disk_Sample.Free_Bytes'Position),
                             Quantity (PD, (I - 1) * Disk_Size + Disk_Sample.Free_Inodes'Position));
               declare Pair : constant E.Span := F (Data, V.Element (Data, Disk_Input, I - 1), "value"); begin
                  if V.Count (Data, Pair) /= 2 or else
                     not Matches (Data, V.Element (Data, Pair, 0), PA, Disks (I).Free_Bytes) or else
                     not Matches (Data, V.Element (Data, Pair, 1), PA, Disks (I).Free_Inodes) then return False; end if;
               end;
            end loop;
            for I in Rows'Range loop
               Rows (I) := (Quantity (LR, (I - 1) * Row_Size + Row_Sample.Reserved'Position),
                 Optional (LR, (I - 1) * Row_Size + Row_Sample.Used'Position),
                 P.Size (Word (LR, (I - 1) * Row_Size + Row_Sample.Output_First'Position, Row_Sample.Output_First'Size / System.Storage_Unit)),
                 P.Size (Word (LR, (I - 1) * Row_Size + Row_Sample.Output_Length'Position, Row_Sample.Output_Length'Size / System.Storage_Unit)));
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
            Transport := L.Compute (LA'Access, Rows'Access, Detail_Arena, Total_Arena, Details, Total, Ledger_Status);
            if Transport /= 0 or else Ledger_Status /= Resource_Ledger.Computed or else
               Detail_Arena /= Expected_Detail or else Total_Arena /= Expected_Total or else
               Word (LO, Ledger_Result_Sample.Status'Position, 1) /= Resource_Ledger.Result_Status'Pos (Ledger_Status) or else
               Quantity (LO, Ledger_Result_Sample.Total'Position) /= L.Encode (Total) or else
               not Shape (Total_Arena, Quantity (LO, Ledger_Result_Sample.Total'Position)) or else
               Value (Total_Arena, Quantity (LO, Ledger_Result_Sample.Total'Position)) /=
                 Resource_Run_Ledger.Exact_Value (Total_Arena, Total) or else
               Value (PA, Policy_Input.Withheld_Memory) /= Resource_Run_Ledger.Exact_Value (Total_Arena, Total)
            then return False; end if;
            for I in Details'Range loop
               if not Shape (Detail_Arena, Quantity (Expected_Quantities, (I - 1) * Quantity_Size)) or else
                  Quantity (Expected_Quantities, (I - 1) * Quantity_Size) /= L.Encode (Details (I)) or else
                  Value (Detail_Arena, Quantity (Expected_Quantities, (I - 1) * Quantity_Size)) /=
                    Resource_Run_Ledger.Exact_Value (Detail_Arena, Details (I)) then return False; end if;
            end loop;
            Transport := P.Admit (PA'Access, Policy_Input'Access, Disks'Access, Policy_Result);
            return Transport = 0 and then Policy_Result.Status = 0 and then Policy_Result.Failed_Gate = 0 and then
              Policy_Result.Disk_Present = 0 and then
              Word (PO, Policy_Result_Sample.Status'Position, 1) = Interfaces.Unsigned_64 (Policy_Result.Status) and then
              Word (PO, Policy_Result_Sample.Failed_Gate'Position, 1) = Interfaces.Unsigned_64 (Policy_Result.Failed_Gate) and then
              Word (PO, Policy_Result_Sample.Field'Position, 1) = Interfaces.Unsigned_64 (Policy_Result.Field) and then
              Word (PO, Policy_Result_Sample.Disk_Present'Position, 1) = Interfaces.Unsigned_64 (Policy_Result.Disk_Present) and then
              Word (PO, Policy_Result_Sample.Disk_Index'Position, Policy_Result_Sample.Disk_Index'Size / System.Storage_Unit) =
                 Interfaces.Unsigned_64 (Policy_Result.Disk_Index);
         end;
      end;
   end Joined;
end Worldline.Custody_V2_Machine_Evidence;
