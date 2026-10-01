with Ada.Unchecked_Conversion;
with System.Storage_Elements;
with Resource_Reservation_Lifecycle;
with Worldline.Resources;

package body Worldline.Reservation_Lifecycle_C_API with SPARK_Mode => Off is
   use type U8;
   use type Size;
   use type System.Address;
   use System.Storage_Elements;
   package L renames Resource_Reservation_Lifecycle;
   package R renames Worldline.Resources;
   use type L.Result_Status;

   type Byte_Access is access all U8;
   type Row_Access is access all Row_C;
   function As_Byte is new Ada.Unchecked_Conversion (System.Address, Byte_Access);
   function As_Row is new Ada.Unchecked_Conversion (System.Address, Row_Access);

   function ABI_Version return Interfaces.Unsigned_32 is (1);
   function Layout_Size return Size is
     (Row_C'Object_Size / System.Storage_Unit);
   function Layout_Offset (Field : U8) return Size is
      Row : constant Row_C := (1, 0, 0);
   begin
      return (case Field is
         when 1 => Row.First'Position,
         when 2 => Row.Length'Position,
         when 3 => Row.Observed'Position,
         when others => Size'Last);
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

   function Copy_Data (Address : System.Address; Length : Size)
      return R.Byte_Array is
      Value : R.Byte_Array (1 .. R.Byte_Count (Length));
   begin
      for I in Value'Range loop
         Value (I) := As_Byte (Address + Storage_Offset (I - 1)).all;
      end loop;
      return Value;
   end Copy_Data;

   function Plan
     (Data : System.Address; Data_Length : Size;
      Rows : System.Address; Row_Count : Size;
      Mode, Present : U8; Requested_First, Requested_Length : Size;
      Removed : System.Address; Removed_Length : Size) return U8
   is
      Row_Size : constant Size := Layout_Size;
   begin
      if Data_Length > Size (R.Byte_Count'Last) or else
        Row_Count > Size (R.Byte_Count'Last) or else
        Removed_Length > Size (R.Byte_Count'Last) or else
        Row_Count > Size (Storage_Offset'Last) / Row_Size or else
        Present > 1 or else
        (Present = 1 and then
          (Requested_First < 1 or else
           Requested_First > Size (R.Byte_Count'Last) or else
           Requested_Length > Size (R.Byte_Count'Last))) or else
        not Extent_Valid (Data, Data_Length) or else
        not Extent_Valid (Rows, Row_Count * Row_Size, Row_C'Alignment) or else
        not Extent_Valid (Removed, Removed_Length)
      then
         return 255;
      end if;
      declare
         Arena : constant R.Byte_Array := Copy_Data (Data, Data_Length);
         Typed_Rows : L.Entry_Array (1 .. R.Byte_Count (Row_Count));
         Mask : L.Removal_Array (1 .. R.Byte_Count (Removed_Length)) :=
           (others => False);
         Requested : constant L.Optional_Identity :=
           (if Present = 0 then (Present => False)
            else (Present => True,
                  Value => (R.Byte_Index (Requested_First),
                            R.Byte_Count (Requested_Length))));
         Selected_Mode : constant L.Operation :=
           (case Mode is
              when 1 => L.Release_Exact,
              when 2 => L.Reconcile_Observed,
              when others => L.Unknown_Operation);
         Status : L.Result_Status;
      begin
         for I in Typed_Rows'Range loop
            declare
               Row : constant Row_C := As_Row
                 (Rows + Storage_Offset (Size (I - 1) * Row_Size)).all;
            begin
               if Row.First < 1 or else Row.First > Size (R.Byte_Count'Last) or else
                 Row.Length > Size (R.Byte_Count'Last) or else Row.Observed > 2
               then
                  return 255;
               end if;
               Typed_Rows (I) :=
                 (Identity => (R.Byte_Index (Row.First), R.Byte_Count (Row.Length)),
                  Observed => L.Liveness'Val (Row.Observed));
            end;
         end loop;
         L.Plan (Arena, Typed_Rows, Requested, Selected_Mode, Mask, Status);
         if Status in L.No_Change | L.Removal_Planned then
            for I in Mask'Range loop
               As_Byte (Removed + Storage_Offset (I - 1)).all :=
                 Boolean'Pos (Mask (I));
            end loop;
         end if;
         return L.Result_Status'Pos (Status);
      end;
   exception
      when others => return 255;
   end Plan;
end Worldline.Reservation_Lifecycle_C_API;
