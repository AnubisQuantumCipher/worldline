with Ada.Unchecked_Conversion;
with System.Storage_Elements;
with Resource_Quantities;
with Resource_Ledger;

package body Worldline.Resource_Ledger_C_API with SPARK_Mode => Off is
   use type U8;
   use type Size;
   use type System.Address;
   use System.Storage_Elements;
   package Q renames Resource_Quantities;
   package L renames Resource_Ledger;
   use type Q.Byte_Count;

   type Byte_Access is access all Q.Byte;
   type Row_Access is access all Row_C;
   type Quantity_Access is access all Quantity_C;
   type Result_Access is access all Result_C;
   function As_Byte is new Ada.Unchecked_Conversion (System.Address, Byte_Access);
   function As_Row is new Ada.Unchecked_Conversion (System.Address, Row_Access);
   function As_Quantity is new Ada.Unchecked_Conversion
     (System.Address, Quantity_Access);
   function As_Result is new Ada.Unchecked_Conversion
     (System.Address, Result_Access);

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
              when 1 => VR.Reserved'Position, when 2 => VR.Used'Position,
              when 3 => VR.Output_First'Position,
              when 4 => VR.Output_Length'Position, when others => Size'Last);
         when 4 =>
            return (case Field is
              when 1 => VT.Status'Position, when 2 => VT.Total'Position,
              when others => Size'Last);
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
   function Encode (V : Q.Quantity) return Quantity_C is
     ((First => Size (V.First), Length => Size (V.Length),
       Negative => Boolean'Pos (V.Negative)));

   function Copy_Data (Address : System.Address; Length : Size)
      return Q.Byte_Array
   is
      Value : Q.Byte_Array (1 .. Q.Byte_Count (Length));
   begin
      for I in Value'Range loop
         Value (I) := As_Byte (Address + Storage_Offset (I - 1)).all;
      end loop;
      return Value;
   end Copy_Data;

   procedure Write_Data (Address : System.Address; Value : Q.Byte_Array) is
   begin
      for I in Value'Range loop
         As_Byte (Address + Storage_Offset (I - Value'First)).all := Value (I);
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
         Arena : constant Q.Byte_Array := Copy_Data (Data, Data_Length);
         Typed_Rows : L.Reservation_Array (1 .. Q.Byte_Count (Row_Count));
         Slots : L.Span_Array (Typed_Rows'Range);
         Detail_Arena : Q.Byte_Array (1 .. Q.Byte_Count (Detail_Length));
         Total_Arena : Q.Byte_Array (1 .. Q.Byte_Count (Total_Length));
         Typed_Details : L.Quantity_Array (Typed_Rows'Range);
         Total : Q.Quantity;
         Status : L.Result_Status;
      begin
         for I in Typed_Rows'Range loop
            declare
               V : constant Row_C := As_Row
                 (Rows + Storage_Offset (Size (I - 1) * Row_Size)).all;
            begin
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
            As_Quantity
              (Details + Storage_Offset (Size (I - 1) * Quantity_Size)).all :=
                Encode (Typed_Details (I));
         end loop;
         As_Result (Result).all :=
           (Status => L.Result_Status'Pos (Status), Total => Encode (Total));
         return 0;
      end;
   exception
      when others => return 255;
   end Compute;
end Worldline.Resource_Ledger_C_API;
