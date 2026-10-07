with System.Address_To_Access_Conversions;
with System.Storage_Elements;
with Worldline.Recovery;

package body Worldline.Recovery_C_API with SPARK_Mode => On is
   package R renames Worldline.Recovery;
   use type R.Byte_Count;
   subtype Size is Interfaces.C.size_t;
   use type Size;
   use type Interfaces.Unsigned_8;
   use type System.Address;
   use System.Storage_Elements;
   package Byte_Pointers is new System.Address_To_Access_Conversions (Interfaces.Unsigned_8);
   use type Byte_Pointers.Object_Pointer;

   function ABI_Version return Interfaces.Unsigned_32 is (1);

   function Shape (Address : System.Address; Length : Size) return Boolean is
     (Length <= Size (R.Byte_Count'Last) and then
      Length <= Size (Storage_Offset'Last) and then
      (Length = 0 or else
        (Address /= System.Null_Address and then
         Integer_Address (Length - 1) <=
           Integer_Address'Last - To_Integer (Address))));

   procedure Copy
     (Address : System.Address; Length : Size; Value : out R.Identity_Bytes)
     with Pre => Length <= Size (R.Byte_Count'Last)
            and then Value'First = 1
            and then Value'Length = R.Byte_Count (Length)
            and then (Length = 0 or else Address /= System.Null_Address),
          Exceptional_Cases => (others => True)
   is
   begin
      for I in Value'Range loop
         declare
            Pointer : constant Byte_Pointers.Object_Pointer :=
              Byte_Pointers.To_Pointer (Address + Storage_Offset (I - 1));
         begin
            if Pointer = null then
               raise Constraint_Error;
            end if;
            Value (I) := Pointer.all;
         end;
      end loop;
   end Copy;

   procedure Fill_Marker
     (Present : Interfaces.Unsigned_8; Address : System.Address; Length : Size;
      Result : out R.Optional_Marker)
     with Pre => Result.Present = (Present = 1)
            and then (if Result.Present then
                        Length <= Size (R.Byte_Count'Last)
                        and then Result.Length = R.Byte_Count (Length)
                        and then (Length = 0
                                  or else Address /= System.Null_Address)
                      else Result.Length = 0),
          Exceptional_Cases => (others => True)
   is
   begin
      if Result.Present then
         declare
            Bound : constant R.Byte_Count := Result.Length;
            Value : R.Identity_Bytes (1 .. Bound);
         begin
            Copy (Address, Length, Value);
            Result := (Present => True, Length => Bound, Value => Value);
         end;
      else
         Result := (Present => False, Length => 0);
      end if;
   end Fill_Marker;

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
         Expected_Value : R.Identity_Bytes
           (1 .. R.Byte_Count (Expected_Length));
         Live_Value : R.Optional_Marker
           (Present => Live_Present = 1,
            Length => (if Live_Present = 1 then R.Byte_Count (Live_Length)
                       else 0));
         Prepared_Value : R.Optional_Marker
           (Present => Prepared_Present = 1,
            Length => (if Prepared_Present = 1
                       then R.Byte_Count (Prepared_Length) else 0));
      begin
         Copy (Expected, Expected_Length, Expected_Value);
         Fill_Marker (Live_Present, Live, Live_Length, Live_Value);
         Fill_Marker (Prepared_Present, Prepared, Prepared_Length, Prepared_Value);
         return R.Recovery_Action'Pos
           (R.Select_Action (Expected_Value, Live_Value, Prepared_Value));
      end;
   exception
      when others => return 255;
   end Select_Action;
end Worldline.Recovery_C_API;
