package body Worldline.Resources with SPARK_Mode is
   function Digit_At (Value : Byte_Array; Offset : Byte_Count) return Natural is
   begin
      if Offset < Value'Length then
         return Natural (Value (Value'First + Offset));
      end if;
      return 0;
   end Digit_At;

   function Subtract_Column
     (Available, Withheld, Floor, Requested : Byte;
      Previous : Borrow) return Column_Result
   is
      Debit : constant Natural := Natural (Withheld) + Natural (Floor)
        + Natural (Requested) + Previous;
      Credit : constant Natural := Natural (Available);
   begin
      if Debit <= Credit then
         return (Remainder => Byte (Credit - Debit), Next => 0);
      else
         declare
            Difference : constant Natural := Debit - Credit;
            Next : constant Borrow := (Difference - 1) / 256 + 1;
         begin
            return (Remainder => Byte (Next * 256 - Difference), Next => Next);
         end;
      end if;
   end Subtract_Column;

   function Fits_By_Addition
     (Available, Withheld, Floor, Requested : Byte_Array) return Boolean
   is
      Count : constant Byte_Count := Byte_Count'Max
        (Byte_Count'Max (Available'Length, Withheld'Length),
         Byte_Count'Max (Floor'Length, Requested'Length));
      type Ordering is (Less, Equal, Greater);
      Comparison : Ordering := Equal;
      Carry : Natural range 0 .. 2 := 0;
   begin
      if Count = 0 then
         return True;
      end if;
      for Offset in 0 .. Count - 1 loop
         declare
            Sum : constant Natural := Digit_At (Withheld, Offset)
              + Digit_At (Floor, Offset) + Digit_At (Requested, Offset) + Carry;
            Wanted : constant Natural := Sum mod 256;
            Credit : constant Natural := Digit_At (Available, Offset);
         begin
            Carry := Sum / 256;
            if Credit < Wanted then
               Comparison := Less;
            elsif Credit > Wanted then
               Comparison := Greater;
            end if;
         end;
      end loop;
      return Carry = 0 and then Comparison /= Less;
   end Fits_By_Addition;

   function Can_Reserve
     (Available, Withheld, Floor, Requested : Byte_Array) return Boolean
   is
      Count : constant Byte_Count := Byte_Count'Max
        (Byte_Count'Max (Available'Length, Withheld'Length),
         Byte_Count'Max (Floor'Length, Requested'Length));
      Previous : Borrow := 0;
   begin
      if Count = 0 then
         return True;
      end if;
      for Offset in 0 .. Count - 1 loop
         declare
            Column : constant Column_Result := Subtract_Column
              (Byte (Digit_At (Available, Offset)),
               Byte (Digit_At (Withheld, Offset)),
               Byte (Digit_At (Floor, Offset)),
               Byte (Digit_At (Requested, Offset)), Previous);
         begin
            Previous := Column.Next;
         end;
      end loop;
      return Previous = 0;
   end Can_Reserve;

   function Sum_Equals
     (Left, Right, Result : Byte_Array) return Boolean
   is
      Count : constant Byte_Count := Byte_Count'Max
        (Byte_Count'Max (Left'Length, Right'Length), Result'Length);
      Carry : Natural range 0 .. 1 := 0;
   begin
      if Count = 0 then
         return True;
      end if;
      for Offset in 0 .. Count - 1 loop
         declare
            Sum : constant Natural := Digit_At (Left, Offset)
              + Digit_At (Right, Offset) + Carry;
         begin
            if Digit_At (Result, Offset) /= Sum mod 256 then
               return False;
            end if;
            Carry := Sum / 256;
         end;
      end loop;
      return Carry = 0;
   end Sum_Equals;

   procedure Try_Reserve
     (State : in out Reservation_State;
      Requested : Byte_Array;
      Accepted : out Boolean)
   is
      Carry : Natural range 0 .. 1 := 0;
   begin
      Accepted := Can_Reserve
        (State.Available, State.Outstanding, State.Floor, Requested);
      if not Accepted then
         return;
      end if;
      for Index in State.Outstanding'Range loop
         declare
            Sum : constant Natural := Natural (State.Outstanding (Index))
              + Digit_At (Requested, Index - State.Outstanding'First) + Carry;
         begin
            State.Outstanding (Index) := Byte (Sum mod 256);
            Carry := Sum / 256;
         end;
      end loop;
      pragma Assert (Carry = 0);
   end Try_Reserve;
end Worldline.Resources;
