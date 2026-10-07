with System.Address_To_Access_Conversions;
with System.Storage_Elements;
with Worldline.Resources;
with Worldline.Resource_Wire;

package body Worldline.Resources_C_API with SPARK_Mode => On is
   use type Interfaces.Unsigned_8;
   use type Interfaces.C.size_t;
   use type System.Address;
   use System.Storage_Elements;

   package Byte_Pointers is new System.Address_To_Access_Conversions (Resources.Byte);
   use type Byte_Pointers.Object_Pointer;

   function ABI_Version return Interfaces.Unsigned_32 is (1);

   function Valid (Address : System.Address; Length : Interfaces.C.size_t)
     return Boolean is
     (Length <= Interfaces.C.size_t (Resources.Byte_Count'Last)
      and then (Length = 0 or else Address /= System.Null_Address));

   procedure Decode
     (Address : System.Address; Length : Interfaces.C.size_t;
      Result : out Resources.Byte_Array)
     with Pre => Length <= Interfaces.C.size_t (Resources.Byte_Count'Last)
            and then Result'First = 1
            and then Result'Length = Resources.Byte_Count (Length)
            and then (Length = 0 or else Address /= System.Null_Address),
          Exceptional_Cases => (others => True)
   is
   begin
      for Index in Result'Range loop
         declare
            Pointer : constant Byte_Pointers.Object_Pointer :=
              Byte_Pointers.To_Pointer (Address + Storage_Offset (Index - Result'First));
         begin
            if Pointer = null then
               raise Constraint_Error;
            end if;
            Result (Index) := Pointer.all;
         end;
      end loop;
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
      declare
         Available_Bytes : Resources.Byte_Array
           (1 .. Resources.Byte_Count (Available_Length));
         Withheld_Bytes : Resources.Byte_Array
           (1 .. Resources.Byte_Count (Withheld_Length));
         Floor_Bytes : Resources.Byte_Array
           (1 .. Resources.Byte_Count (Floor_Length));
         Requested_Bytes : Resources.Byte_Array
           (1 .. Resources.Byte_Count (Requested_Length));
      begin
         Decode (Available, Available_Length, Available_Bytes);
         Decode (Withheld, Withheld_Length, Withheld_Bytes);
         Decode (Floor, Floor_Length, Floor_Bytes);
         Decode (Requested, Requested_Length, Requested_Bytes);
         if Resource_Wire.Can_Reserve
           (Available_Negative = 1, Available_Bytes, Withheld_Bytes,
            Floor_Bytes, Requested_Bytes)
         then
            return 1;
         end if;
      end;
      return 0;
   exception
      when others => return 255;
   end Can_Reserve;
end Worldline.Resources_C_API;
