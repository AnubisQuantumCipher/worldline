with Ada.Unchecked_Conversion;
with System.Storage_Elements;
with Worldline.Resources;
with Worldline.Resource_Wire;

package body Worldline.Resources_C_API with SPARK_Mode => Off is
   use type Interfaces.Unsigned_8;
   use type Interfaces.C.size_t;
   use type System.Address;
   use System.Storage_Elements;

   type Byte_Access is access all Resources.Byte;
   function As_Byte is new Ada.Unchecked_Conversion
     (System.Address, Byte_Access);

   function ABI_Version return Interfaces.Unsigned_32 is (1);

   function Valid (Address : System.Address; Length : Interfaces.C.size_t)
     return Boolean is
     (Length <= Interfaces.C.size_t (Resources.Byte_Count'Last)
      and then (Length = 0 or else Address /= System.Null_Address));

   function Decode
     (Address : System.Address; Length : Interfaces.C.size_t)
      return Resources.Byte_Array
   is
      Result : Resources.Byte_Array (1 .. Resources.Byte_Count (Length));
   begin
      for Index in Result'Range loop
         Result (Index) := As_Byte
           (Address + Storage_Offset (Index - Result'First)).all;
      end loop;
      return Result;
   end Decode;

   function Can_Reserve
     (Available_Negative : Interfaces.Unsigned_8;
      Available : System.Address; Available_Length : Interfaces.C.size_t;
      Withheld : System.Address; Withheld_Length : Interfaces.C.size_t;
      Floor : System.Address; Floor_Length : Interfaces.C.size_t;
      Requested : System.Address; Requested_Length : Interfaces.C.size_t)
      return Interfaces.Unsigned_8
   is
   begin
      if Available_Negative > 1
        or else not Valid (Available, Available_Length)
        or else not Valid (Withheld, Withheld_Length)
        or else not Valid (Floor, Floor_Length)
        or else not Valid (Requested, Requested_Length)
      then
         return 255;
      end if;
      if Resource_Wire.Can_Reserve
        (Available_Negative = 1,
         Decode (Available, Available_Length),
         Decode (Withheld, Withheld_Length),
         Decode (Floor, Floor_Length),
         Decode (Requested, Requested_Length))
      then
         return 1;
      end if;
      return 0;
   exception
      when others => return 255;
   end Can_Reserve;
end Worldline.Resources_C_API;
