with Worldline.Resources;
with Worldline.Resource_Wire;

package body Worldline.Resources_C_API with SPARK_Mode => On is
   use type Interfaces.Unsigned_8;


   function ABI_Version return Interfaces.Unsigned_32 is (1);


   procedure Decode
     (Source : not null access constant Resources.Byte_Array;
      Result : out Resources.Byte_Array)
     with Pre => Source'First = 1 and then Result'First = 1
       and then Result'Length = Source'Length
   is
   begin
      for Index in Result'Range loop
         Result (Index) := Source (Index);
      end loop;
   end Decode;

   function Can_Reserve
     (Available_Negative : Interfaces.Unsigned_8;
      Available, Withheld, Floor, Requested : not null access constant Resources.Byte_Array)
      return Interfaces.Unsigned_8
   is
   begin
      if Available_Negative > 1 then return 255; end if;
      if Available'First /= 1 or else Withheld'First /= 1 or else Floor'First /= 1 or else Requested'First /= 1 then return 255; end if;
      declare
         Available_Bytes : Resources.Byte_Array
           (1 .. Resources.Byte_Count (Available'Length));
         Withheld_Bytes : Resources.Byte_Array
           (1 .. Resources.Byte_Count (Withheld'Length));
         Floor_Bytes : Resources.Byte_Array
           (1 .. Resources.Byte_Count (Floor'Length));
         Requested_Bytes : Resources.Byte_Array
           (1 .. Resources.Byte_Count (Requested'Length));
      begin
         Decode (Available, Available_Bytes);
         Decode (Withheld, Withheld_Bytes);
         Decode (Floor, Floor_Bytes);
         Decode (Requested, Requested_Bytes);
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
