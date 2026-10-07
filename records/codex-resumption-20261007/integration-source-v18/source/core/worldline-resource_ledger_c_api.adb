with System.Address_To_Access_Conversions;
with System.Storage_Elements;
with Resource_Quantities;
with Resource_Ledger;

package body Worldline.Resource_Ledger_C_API with SPARK_Mode => On is
   use type U8;
   use type Size;
   use type System.Address;
   use System.Storage_Elements;
   package Q renames Resource_Quantities;
   package L renames Resource_Ledger;
   use type Q.Byte_Count;

   package Byte_Pointers is new System.Address_To_Access_Conversions (Q.Byte);
   package Row_Pointers is new System.Address_To_Access_Conversions (Row_C);
   package Quantity_Pointers is new System.Address_To_Access_Conversions (Quantity_C);
   package Result_Pointers is new System.Address_To_Access_Conversions (Result_C);
   use type Byte_Pointers.Object_Pointer;
   use type Row_Pointers.Object_Pointer;
   use type Quantity_Pointers.Object_Pointer;
   use type Result_Pointers.Object_Pointer;

   function ABI_Version return Interfaces.Unsigned_32 is (1);
   function Layout_Size (Selector : U8) return Size is
     (case Selector is
         when 1 => Quantity_C'Object_Size / System.Storage_Unit,
         when 2 => Optional_C'Object_Size / System.Storage_Unit,
         when 3 => Row_C'Object_Size / System.Storage_Unit,
         when 4 => Result_C'Object_Size / System.Storage_Unit,
         when others => Size'Last);

   function Layout_Offset (Selector, Field : U8) return Size is
      VQ : constant Quantity_C := (First => 1, Length => 0, Negative => 0);
      VO : constant Optional_C := (Present => 0, Value => VQ);
      VR : constant Row_C := (Reserved => VQ, Used => VO,
                             Output_First => 1, Output_Length => 0);
      VT : constant Result_C := (Status => 0, Total => VQ);
   begin
      pragma Compile_Time_Error (VQ.First'Position /= 0, "Quantity.First");
      pragma Compile_Time_Error (VQ.Length'Position /= 8, "Quantity.Length");
      pragma Compile_Time_Error (VQ.Negative'Position /= 16, "Quantity.Negative");
      pragma Compile_Time_Error (VO.Present'Position /= 0, "Optional.Present");
      pragma Compile_Time_Error (VO.Value'Position /= 8, "Optional.Value");
      pragma Compile_Time_Error (VR.Reserved'Position /= 0, "Row.Reserved");
      pragma Compile_Time_Error (VR.Used'Position /= 24, "Row.Used");
      pragma Compile_Time_Error (VR.Output_First'Position /= 56, "Row.Output_First");
      pragma Compile_Time_Error (VR.Output_Length'Position /= 64, "Row.Output_Length");
      pragma Compile_Time_Error (VT.Status'Position /= 0, "Result.Status");
      pragma Compile_Time_Error (VT.Total'Position /= 8, "Result.Total");
      case Selector is
         when 1 =>
            return (case Field is
              when 1 => 0, when 2 => 8, when 3 => 16, when others => Size'Last);
         when 2 =>
            return (case Field is
              when 1 => 0, when 2 => 8, when others => Size'Last);
         when 3 =>
            return (case Field is
              when 1 => 0, when 2 => 24, when 3 => 56, when 4 => 64,
              when others => Size'Last);
         when 4 =>
            return (case Field is
              when 1 => 0, when 2 => 8, when others => Size'Last);
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
   function Encode (V : Q.Quantity) return Quantity_C is
     ((First => Size (V.First), Length => Size (V.Length),
       Negative => Boolean'Pos (V.Negative)));

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

   procedure Write_Byte (Address : System.Address; Item : Q.Byte)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Byte_Pointers.Object_Pointer := Byte_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Pointer.all := Item;
   end Write_Byte;

   procedure Read_Row (Address : System.Address; Item : out Row_C)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Row_Pointers.Object_Pointer := Row_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Item := Pointer.all;
   end Read_Row;

   procedure Read_Quantity (Address : System.Address; Item : out Quantity_C)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Quantity_Pointers.Object_Pointer := Quantity_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Item := Pointer.all;
   end Read_Quantity;

   procedure Write_Quantity (Address : System.Address; Item : Quantity_C)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Quantity_Pointers.Object_Pointer := Quantity_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Pointer.all := Item;
   end Write_Quantity;

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

   procedure Copy_Data
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
   end Copy_Data;

   procedure Write_Data (Address : System.Address; Value : Q.Byte_Array)
     with Pre => (Value'Length = 0 or else Address /= System.Null_Address),
          Exceptional_Cases => (others => True)
   is
   begin
      for I in Value'Range loop
         Write_Byte (Address + Storage_Offset (I - Value'First), Value (I));
      end loop;
   end Write_Data;

   function Compute
     (Data : System.Address; Data_Length : Size;
      Rows : System.Address; Row_Count : Size;
      Detail_Data : System.Address; Detail_Length : Size;
      Total_Data : System.Address; Total_Length : Size;
      Details : System.Address; Result : System.Address) return U8
   is
      Row_Size : constant Size := Row_C'Object_Size / System.Storage_Unit;
      Quantity_Size : constant Size := Quantity_C'Object_Size / System.Storage_Unit;
   begin
      if Data_Length > Size (Q.Byte_Count'Last) or else
        Detail_Length > Size (Q.Byte_Count'Last) or else
        Total_Length > Size (Q.Byte_Count'Last) or else
        Row_Count > Size (Q.Byte_Count'Last) or else
        Row_Count > Size (Storage_Offset'Last) / Row_Size or else
        Row_Count > Size (Storage_Offset'Last) / Quantity_Size or else
        not Extent_Valid (Data, Data_Length) or else
        not Extent_Valid (Detail_Data, Detail_Length) or else
        not Extent_Valid (Total_Data, Total_Length) or else
        not Extent_Valid (Rows, Row_Count * Row_Size, Row_C'Alignment) or else
        not Extent_Valid (Details, Row_Count * Quantity_Size,
                         Quantity_C'Alignment) or else
        not Extent_Valid (Result, Result_C'Object_Size / System.Storage_Unit,
                         Result_C'Alignment)
      then
         return 255;
      end if;
      declare
         Arena : Q.Byte_Array (1 .. Q.Byte_Count (Data_Length));
         Blank_Row : constant L.Reservation_Row :=
           (Reserved => L.Empty, Used => (Present => False));
         Blank_Slot : constant L.Output_Span := (First => 1, Length => 0);
         Typed_Rows : L.Reservation_Array (1 .. Q.Byte_Count (Row_Count)) :=
           (others => Blank_Row);
         Slots : L.Span_Array (Typed_Rows'Range) := (others => Blank_Slot);
         Detail_Arena : Q.Byte_Array (1 .. Q.Byte_Count (Detail_Length));
         Total_Arena : Q.Byte_Array (1 .. Q.Byte_Count (Total_Length));
         Typed_Details : L.Quantity_Array (Typed_Rows'Range);
         Total : Q.Quantity;
         Status : L.Result_Status;
      begin
         Copy_Data (Data, Data_Length, Arena);
         for I in Typed_Rows'Range loop
            declare
               V : Row_C;
            begin
               Read_Row (Rows + Storage_Offset (Size (I - 1) * Row_Size), V);
               if not Shape (V.Reserved) or else not Shape (V.Used) or else
                 V.Output_First < 1 or else
                 V.Output_First > Size (Q.Byte_Count'Last) or else
                 V.Output_Length > Size (Q.Byte_Count'Last)
               then
                  return 255;
               end if;
               Typed_Rows (I) := (Decode (V.Reserved), Decode (V.Used));
               Slots (I) := (Q.Byte_Index (V.Output_First),
                             Q.Byte_Count (V.Output_Length));
            end;
         end loop;
         L.Compute (Arena, Typed_Rows, Slots, Detail_Arena, Total_Arena,
                    Typed_Details, Total, Status);
         Write_Data (Detail_Data, Detail_Arena);
         Write_Data (Total_Data, Total_Arena);
         for I in Typed_Details'Range loop
            Write_Quantity
              (Details + Storage_Offset (Size (I - 1) * Quantity_Size),
               Encode (Typed_Details (I)));
         end loop;
         Write_Result
           (Result,
            (Status => L.Result_Status'Pos (Status), Total => Encode (Total)));
         return 0;
      end;
   exception
      when others => return 255;
   end Compute;
   function Headroom
     (Data : System.Address; Data_Length : Size;
      Available, Withheld, Floor : System.Address;
      Output : System.Address; Output_Length : Size;
      Result : System.Address) return U8
   is
      Quantity_Size : constant Size := Quantity_C'Object_Size / System.Storage_Unit;
   begin
      if Data_Length > Size (Q.Byte_Count'Last) or else
        Output_Length > Size (Q.Byte_Count'Last) or else
        not Extent_Valid (Data, Data_Length) or else
        not Extent_Valid (Output, Output_Length) or else
        not Extent_Valid (Available, Quantity_Size, Quantity_C'Alignment) or else
        not Extent_Valid (Withheld, Quantity_Size, Quantity_C'Alignment) or else
        not Extent_Valid (Floor, Quantity_Size, Quantity_C'Alignment) or else
        not Extent_Valid (Result, Result_C'Object_Size / System.Storage_Unit,
                         Result_C'Alignment)
      then
         return 255;
      end if;
      declare
         A, W, F : Quantity_C;
      begin
         Read_Quantity (Available, A);
         Read_Quantity (Withheld, W);
         Read_Quantity (Floor, F);
         if not Shape (A) or else not Shape (W) or else not Shape (F) then
            return 255;
         end if;
         declare
            Arena : Q.Byte_Array (1 .. Q.Byte_Count (Data_Length));
            Output_Arena : Q.Byte_Array (1 .. Q.Byte_Count (Output_Length));
            Typed_Result : Q.Quantity;
            Status : L.Result_Status;
         begin
            Copy_Data (Data, Data_Length, Arena);
            L.Compute_Headroom
              (Arena, Decode (A), Decode (W), Decode (F),
               Output_Arena, Typed_Result, Status);
            Write_Data (Output, Output_Arena);
            Write_Result
              (Result,
               (Status => L.Result_Status'Pos (Status),
                Total => Encode (Typed_Result)));
            return 0;
         end;
      end;
   exception
      when others => return 255;
   end Headroom;
end Worldline.Resource_Ledger_C_API;
