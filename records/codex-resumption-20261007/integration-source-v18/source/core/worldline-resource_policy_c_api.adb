with System.Address_To_Access_Conversions;
with System.Storage_Elements;
with Resource_Quantities;
with Resource_Admission;

package body Worldline.Resource_Policy_C_API with SPARK_Mode => On is
   use type U8;
   use type Size;
   use type System.Address;
   use System.Storage_Elements;
   package Q renames Resource_Quantities;
   package P renames Resource_Admission;
   use type Q.Byte_Count;

   package Byte_Pointers is new System.Address_To_Access_Conversions (Q.Byte);
   package Input_Pointers is new System.Address_To_Access_Conversions (Input_C);
   package Disk_Pointers is new System.Address_To_Access_Conversions (Disk_C);
   package Result_Pointers is new System.Address_To_Access_Conversions (Result_C);
   use type Byte_Pointers.Object_Pointer;
   use type Input_Pointers.Object_Pointer;
   use type Disk_Pointers.Object_Pointer;
   use type Result_Pointers.Object_Pointer;

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
      pragma Compile_Time_Error (VQ.First'Position /= 0, "Quantity.First");
      pragma Compile_Time_Error (VQ.Length'Position /= 8, "Quantity.Length");
      pragma Compile_Time_Error (VQ.Negative'Position /= 16, "Quantity.Negative");
      pragma Compile_Time_Error (VO.Present'Position /= 0, "Optional.Present");
      pragma Compile_Time_Error (VO.Value'Position /= 8, "Optional.Value");
      pragma Compile_Time_Error (VI.Outstanding_Count'Position /= 0, "Input.Outstanding");
      pragma Compile_Time_Error (VI.Concurrency_Limit'Position /= 24, "Input.Concurrency");
      pragma Compile_Time_Error (VI.Memory_Pressure'Position /= 56, "Input.Pressure");
      pragma Compile_Time_Error
        (VI.Memory_Pressure_Ceiling'Position /= 88, "Input.Ceiling");
      pragma Compile_Time_Error (VI.Disk_Byte_Floor'Position /= 112, "Input.Disk_Bytes");
      pragma Compile_Time_Error (VI.Disk_Inode_Floor'Position /= 136, "Input.Disk_Inodes");
      pragma Compile_Time_Error (VI.Available_Memory'Position /= 160, "Input.Available");
      pragma Compile_Time_Error (VI.Withheld_Memory'Position /= 184, "Input.Withheld");
      pragma Compile_Time_Error (VI.Memory_Floor'Position /= 208, "Input.Floor");
      pragma Compile_Time_Error (VI.Requested_Memory'Position /= 232, "Input.Requested");
      pragma Compile_Time_Error (VD.Free_Bytes'Position /= 0, "Disk.Bytes");
      pragma Compile_Time_Error (VD.Free_Inodes'Position /= 24, "Disk.Inodes");
      pragma Compile_Time_Error (VR.Status'Position /= 0, "Result.Status");
      pragma Compile_Time_Error (VR.Failed_Gate'Position /= 1, "Result.Gate");
      pragma Compile_Time_Error (VR.Field'Position /= 2, "Result.Field");
      pragma Compile_Time_Error (VR.Disk_Present'Position /= 3, "Result.Disk_Present");
      pragma Compile_Time_Error (VR.Disk_Index'Position /= 8, "Result.Disk_Index");
      case Selector is
         when 1 =>
            return (case Field is
              when 1 => 0, when 2 => 8, when 3 => 16, when others => Size'Last);
         when 2 =>
            return (case Field is
              when 1 => 0, when 2 => 8, when others => Size'Last);
         when 3 =>
            return (case Field is
              when 1 => 0, when 2 => 24, when 3 => 56, when 4 => 88,
              when 5 => 112, when 6 => 136, when 7 => 160, when 8 => 184,
              when 9 => 208, when 10 => 232, when others => Size'Last);
         when 4 =>
            return (case Field is
              when 1 => 0, when 2 => 24, when others => Size'Last);
         when 5 =>
            return (case Field is
              when 1 => 0, when 2 => 1, when 3 => 2, when 4 => 3, when 5 => 8,
              when others => Size'Last);
         when others => return Size'Last;
      end case;
   end Layout_Offset;

   function Extent_Valid
     (Address : System.Address; Length : Size; Alignment : Size := 1)
      return Boolean is
     (Alignment /= 0 and then
      Length <= Size (Storage_Offset'Last) and then
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
       Length => Q.Byte_Count (V.Length)))
   with Pre => Shape (V);
   function Decode (V : Optional_C) return Q.Optional_Quantity is
     (if V.Present = 0 then (Present => False)
      else (Present => True, Value => Decode (V.Value)))
   with Pre => Shape (V);

   procedure Read_Byte (Address : System.Address; Item : out Q.Byte)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Byte_Pointers.Object_Pointer := Byte_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Item := Pointer.all;
   end Read_Byte;

   procedure Read_Input (Address : System.Address; Item : out Input_C)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Input_Pointers.Object_Pointer := Input_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Item := Pointer.all;
   end Read_Input;

   procedure Read_Disk (Address : System.Address; Item : out Disk_C)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Disk_Pointers.Object_Pointer := Disk_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Item := Pointer.all;
   end Read_Disk;

   procedure Write_Result (Address : System.Address; Item : Result_C)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Result_Pointers.Object_Pointer := Result_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Pointer.all := Item;
   end Write_Result;

   procedure Decode_Data
     (Address : System.Address; Length : Size; Value : out Q.Byte_Array)
     with Pre => Length <= Size (Q.Byte_Count'Last)
            and then Value'First = 1
            and then Value'Length = Q.Byte_Count (Length)
            and then (Length = 0 or else Address /= System.Null_Address),
          Exceptional_Cases => (others => True)
   is
   begin
      for I in Value'Range loop
         Read_Byte (Address + Storage_Offset (I - 1), Value (I));
      end loop;
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
         V : Input_C;
      begin
         Read_Input (Input, V);
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
            Blank : constant Q.Quantity :=
              (Negative => False, First => 1, Length => 0);
            Rows : P.Disk_Array (1 .. Q.Byte_Count (Disk_Count)) :=
              (others => (Free_Bytes => Blank, Free_Inodes => Blank));
         begin
            for I in Rows'Range loop
               declare
                  Row : Disk_C;
               begin
                  Read_Disk (Disks + Storage_Offset (Size (I - 1) * Disk_Size), Row);
                  if not Shape (Row.Free_Bytes) or else
                    not Shape (Row.Free_Inodes)
                  then
                     return 255;
                  end if;
                  Rows (I) := (Decode (Row.Free_Bytes), Decode (Row.Free_Inodes));
               end;
            end loop;
            declare
               Arena : Q.Byte_Array (1 .. Q.Byte_Count (Data_Length));
               D : P.Decision;
            begin
               Decode_Data (Data, Data_Length, Arena);
               D := P.Admit (Arena, State, Rows);
               Write_Result
                 (Result,
                  (Status => P.Check_Status'Pos (D.Check.Status),
                   Failed_Gate => P.Gate'Pos (D.Failed_Gate),
                   Field => P.Quantity_Field'Pos (D.Check.Field),
                   Disk_Present => Boolean'Pos (D.Disk.Present),
                   Disk_Index =>
                     (if D.Disk.Present then Size (D.Disk.Value) else 0)));
               return 0;
            end;
         end;
      end;
   exception
      when others => return 255;
   end Admit;
end Worldline.Resource_Policy_C_API;
