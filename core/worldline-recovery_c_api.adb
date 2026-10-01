with Ada.Unchecked_Conversion;
with System.Storage_Elements;
with Worldline.Recovery;

package body Worldline.Recovery_C_API with SPARK_Mode => Off is
   package R renames Worldline.Recovery;
   use type R.Byte_Count;
   subtype Size is Interfaces.C.size_t;
   use type Size;
   use type Interfaces.Unsigned_8;
   use type System.Address;
   use System.Storage_Elements;
   type Byte_Access is access all Interfaces.Unsigned_8;
   function As_Byte is new Ada.Unchecked_Conversion (System.Address, Byte_Access);

   function ABI_Version return Interfaces.Unsigned_32 is (1);

   function Shape (Address : System.Address; Length : Size) return Boolean is
     (Length <= Size (R.Byte_Count'Last) and then
      Length <= Size (Storage_Offset'Last) and then
      (Length = 0 or else
        (Address /= System.Null_Address and then
         Integer_Address (Length - 1) <=
           Integer_Address'Last - To_Integer (Address))));

   function Copy (Address : System.Address; Length : Size)
      return R.Identity_Bytes
   is
      Value : R.Identity_Bytes (1 .. R.Byte_Count (Length));
   begin
      for I in Value'Range loop
         Value (I) := As_Byte (Address + Storage_Offset (I - 1)).all;
      end loop;
      return Value;
   end Copy;

   function Marker
     (Present : Interfaces.Unsigned_8; Address : System.Address; Length : Size)
      return R.Optional_Marker is
   begin
      if Present = 0 then
         return Result : R.Optional_Marker (Present => False, Length => 0) do
            null;
         end return;
      end if;
      return Result : R.Optional_Marker
        (Present => True, Length => R.Byte_Count (Length))
      do
         Result.Value := Copy (Address, Length);
      end return;
   end Marker;

   function Select_Action
     (Expected : System.Address; Expected_Length : Interfaces.C.size_t;
      Live_Present : Interfaces.Unsigned_8;
      Live : System.Address; Live_Length : Interfaces.C.size_t;
      Prepared_Present : Interfaces.Unsigned_8;
      Prepared : System.Address; Prepared_Length : Interfaces.C.size_t)
      return Interfaces.Unsigned_8 is
   begin
      if Live_Present > 1 or else Prepared_Present > 1 or else
        not Shape (Expected, Expected_Length) or else
        (Live_Present = 1 and then not Shape (Live, Live_Length)) or else
        (Prepared_Present = 1 and then not Shape (Prepared, Prepared_Length))
      then
         return 255;
      end if;
      declare
         Expected_Value : constant R.Identity_Bytes :=
           Copy (Expected, Expected_Length);
         Live_Value : constant R.Optional_Marker
           (Present => Live_Present = 1,
            Length => (if Live_Present = 1 then R.Byte_Count (Live_Length)
                       else 0)) := Marker (Live_Present, Live, Live_Length);
         Prepared_Value : constant R.Optional_Marker
           (Present => Prepared_Present = 1,
            Length => (if Prepared_Present = 1
                       then R.Byte_Count (Prepared_Length) else 0)) :=
             Marker (Prepared_Present, Prepared, Prepared_Length);
      begin
         return R.Recovery_Action'Pos
           (R.Select_Action (Expected_Value, Live_Value, Prepared_Value));
      end;
   exception
      when others => return 255;
   end Select_Action;
end Worldline.Recovery_C_API;
