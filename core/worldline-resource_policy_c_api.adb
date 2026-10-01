with Ada.Unchecked_Conversion;
with System.Storage_Elements;
with Resource_Quantities;
with Resource_Admission;

package body Worldline.Resource_Policy_C_API with SPARK_Mode => Off is
   use type U8;
   use type Size;
   use type System.Address;
   use System.Storage_Elements;
   package Q renames Resource_Quantities;
   package P renames Resource_Admission;
   use type Q.Byte_Count;

   type Byte_Access is access all Q.Byte;
   type Input_Access is access all Input_C;
   type Disk_Access is access all Disk_C;
   type Result_Access is access all Result_C;
   function As_Byte is new Ada.Unchecked_Conversion (System.Address, Byte_Access);
   function As_Input is new Ada.Unchecked_Conversion (System.Address, Input_Access);
   function As_Disk is new Ada.Unchecked_Conversion (System.Address, Disk_Access);
   function As_Result is new Ada.Unchecked_Conversion (System.Address, Result_Access);

   function ABI_Version return Interfaces.Unsigned_32 is (1);

   function Layout_Size (Selector : U8) return Size is
     (case Selector is
         when 1 => Quantity_C'Object_Size / System.Storage_Unit,
         when 2 => Optional_C'Object_Size / System.Storage_Unit,
         when 3 => Input_C'Object_Size / System.Storage_Unit,
         when 4 => Disk_C'Object_Size / System.Storage_Unit,
         when 5 => Result_C'Object_Size / System.Storage_Unit,
         when others => Size'Last);

   function Layout_Offset (Selector, Field : U8) return Size is
      VQ : constant Quantity_C := (First => 1, Length => 0, Negative => 0);
      VO : constant Optional_C := (Present => 0, Value => VQ);
      VI : constant Input_C :=
        (Concurrency_Limit => VO, Memory_Pressure => VO, others => VQ);
      VD : constant Disk_C := (others => VQ);
      VR : constant Result_C := (Disk_Index => 0, others => 0);
   begin
      case Selector is
         when 1 =>
            return (case Field is
              when 1 => VQ.First'Position, when 2 => VQ.Length'Position,
              when 3 => VQ.Negative'Position, when others => Size'Last);
         when 2 =>
            return (case Field is
              when 1 => VO.Present'Position, when 2 => VO.Value'Position,
              when others => Size'Last);
         when 3 =>
            return (case Field is
              when 1 => VI.Outstanding_Count'Position,
              when 2 => VI.Concurrency_Limit'Position,
              when 3 => VI.Memory_Pressure'Position,
              when 4 => VI.Memory_Pressure_Ceiling'Position,
              when 5 => VI.Disk_Byte_Floor'Position,
              when 6 => VI.Disk_Inode_Floor'Position,
              when 7 => VI.Available_Memory'Position,
              when 8 => VI.Withheld_Memory'Position,
              when 9 => VI.Memory_Floor'Position,
              when 10 => VI.Requested_Memory'Position,
              when others => Size'Last);
         when 4 =>
            return (case Field is
              when 1 => VD.Free_Bytes'Position,
              when 2 => VD.Free_Inodes'Position, when others => Size'Last);
         when 5 =>
            return (case Field is
              when 1 => VR.Status'Position, when 2 => VR.Failed_Gate'Position,
              when 3 => VR.Field'Position, when 4 => VR.Disk_Present'Position,
              when 5 => VR.Disk_Index'Position, when others => Size'Last);
         when others => return Size'Last;
      end case;
   end Layout_Offset;

   function Extent_Valid
     (Address : System.Address; Length : Size; Alignment : Size := 1)
      return Boolean is
     (Length <= Size (Storage_Offset'Last) and then
      (Length = 0 or else
        (Address /= System.Null_Address and then
         To_Integer (Address) mod Integer_Address (Alignment) = 0 and then
         Integer_Address (Length - 1) <=
           Integer_Address'Last - To_Integer (Address))));

   function Shape (V : Quantity_C) return Boolean is
     (V.Negative <= 1 and then V.First >= 1 and then
      V.First <= Size (Q.Byte_Count'Last) and then
      V.Length <= Size (Q.Byte_Count'Last));
   function Shape (V : Optional_C) return Boolean is
     (V.Present <= 1 and then (V.Present = 0 or else Shape (V.Value)));

   function Decode (V : Quantity_C) return Q.Quantity is
     ((Negative => V.Negative = 1, First => Q.Byte_Index (V.First),
       Length => Q.Byte_Count (V.Length)));
   function Decode (V : Optional_C) return Q.Optional_Quantity is
     (if V.Present = 0 then (Present => False)
      else (Present => True, Value => Decode (V.Value)));

   function Decode_Data (Address : System.Address; Length : Size)
      return Q.Byte_Array
   is
      Value : Q.Byte_Array (1 .. Q.Byte_Count (Length));
   begin
      for I in Value'Range loop
         Value (I) := As_Byte (Address + Storage_Offset (I - 1)).all;
      end loop;
      return Value;
   end Decode_Data;

   function Admit
     (Data : System.Address; Data_Length : Size;
      Input : System.Address; Disks : System.Address; Disk_Count : Size;
      Result : System.Address) return U8
   is
      Disk_Size : constant Size := Disk_C'Object_Size / System.Storage_Unit;
   begin
      if Data_Length > Size (Q.Byte_Count'Last) or else
        Disk_Count > Size (Q.Byte_Count'Last) or else
        Disk_Count > Size (Storage_Offset'Last) / Disk_Size or else
        not Extent_Valid (Data, Data_Length) or else
        not Extent_Valid (Input, Input_C'Object_Size / System.Storage_Unit,
                         Input_C'Alignment) or else
        not Extent_Valid (Result, Result_C'Object_Size / System.Storage_Unit,
                         Result_C'Alignment) or else
        not Extent_Valid (Disks, Disk_Count * Disk_Size, Disk_C'Alignment)
      then
         return 255;
      end if;
      declare
         V : constant Input_C := As_Input (Input).all;
      begin
         if not Shape (V.Outstanding_Count) or else
           not Shape (V.Concurrency_Limit) or else not Shape (V.Memory_Pressure)
           or else not Shape (V.Memory_Pressure_Ceiling) or else
           not Shape (V.Disk_Byte_Floor) or else not Shape (V.Disk_Inode_Floor)
           or else not Shape (V.Available_Memory) or else
           not Shape (V.Withheld_Memory) or else not Shape (V.Memory_Floor)
           or else not Shape (V.Requested_Memory)
         then
            return 255;
         end if;
         declare
            State : constant P.Policy_Input :=
              (Decode (V.Outstanding_Count), Decode (V.Concurrency_Limit),
               Decode (V.Memory_Pressure), Decode (V.Memory_Pressure_Ceiling),
               Decode (V.Disk_Byte_Floor), Decode (V.Disk_Inode_Floor),
               Decode (V.Available_Memory), Decode (V.Withheld_Memory),
               Decode (V.Memory_Floor), Decode (V.Requested_Memory));
            Rows : P.Disk_Array (1 .. Q.Byte_Count (Disk_Count));
         begin
            for I in Rows'Range loop
               declare
                  Row : constant Disk_C := As_Disk
                    (Disks + Storage_Offset (Size (I - 1) * Disk_Size)).all;
               begin
                  if not Shape (Row.Free_Bytes) or else
                    not Shape (Row.Free_Inodes)
                  then
                     return 255;
                  end if;
                  Rows (I) := (Decode (Row.Free_Bytes), Decode (Row.Free_Inodes));
               end;
            end loop;
            declare
               Arena : constant Q.Byte_Array := Decode_Data (Data, Data_Length);
               D : constant P.Decision := P.Admit (Arena, State, Rows);
            begin
               As_Result (Result).all :=
                 (Status => P.Check_Status'Pos (D.Check.Status),
                  Failed_Gate => P.Gate'Pos (D.Failed_Gate),
                  Field => P.Quantity_Field'Pos (D.Check.Field),
                  Disk_Present => Boolean'Pos (D.Disk.Present),
                  Disk_Index => (if D.Disk.Present then Size (D.Disk.Value) else 0));
               return 0;
            end;
         end;
      end;
   exception
      when others => return 255;
   end Admit;
end Worldline.Resource_Policy_C_API;
