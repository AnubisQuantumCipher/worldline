package body Resource_Quantities with SPARK_Mode is
   function Digit
     (Data : Byte_Array; Q : Quantity; Offset : Byte_Count) return Natural is
   begin
      if Span_Valid (Data, Q) and then Offset < Q.Length then
         return Natural (Data (Q.First + Offset));
      end if;
      return 0;
   end Digit;

   function Radix_Power (Exponent : Byte_Count) return Valid_Big_Integer is
      Completed : Byte_Count := 0;
      Result : Valid_Big_Integer := To_Big_Integer (1);
      Previous : Valid_Big_Integer := To_Big_Integer (1);
   begin
      while Completed < Exponent loop
         pragma Loop_Invariant (Completed <= Exponent);
         pragma Loop_Invariant (Result >= 1);
         pragma Loop_Invariant
           (if Completed = 0 then Result = 1
            else Result = To_Big_Integer (256) * Previous);
         pragma Loop_Variant (Decreases => Exponent - Completed);
         Previous := Result;
         Result := To_Big_Integer (256) * Previous;
         Completed := Completed + 1;
      end loop;
      return Result;
   end Radix_Power;

   function Prefix_Value
     (Data : Byte_Array; Q : Quantity; Count : Byte_Count)
      return Valid_Big_Integer is
      Completed : Byte_Count := 0;
      Result : Valid_Big_Integer := To_Big_Integer (0);
      Place : Valid_Big_Integer := To_Big_Integer (1);
      Previous_Result : Valid_Big_Integer := To_Big_Integer (0);
      Previous_Place : Valid_Big_Integer := To_Big_Integer (1);
   begin
      while Completed < Count loop
         pragma Loop_Invariant (Completed <= Count);
         pragma Loop_Invariant (Result >= 0 and then Place >= 1);
         pragma Loop_Invariant
           (if Completed = 0 then Result = 0 and then Place = 1
            else Result = Previous_Result +
              To_Big_Integer (Digit (Data, Q, Completed - 1)) *
                Previous_Place and then
              Place = To_Big_Integer (256) * Previous_Place);
         pragma Loop_Variant (Decreases => Count - Completed);
         Previous_Result := Result;
         Previous_Place := Place;
         Result := Previous_Result +
           To_Big_Integer (Digit (Data, Q, Completed)) * Previous_Place;
         Place := To_Big_Integer (256) * Previous_Place;
         Completed := Completed + 1;
      end loop;
      return Result;
   end Prefix_Value;

   function Magnitude (Data : Byte_Array; Q : Quantity)
      return Valid_Big_Integer is
   begin
      if not Span_Valid (Data, Q) then
         return To_Big_Integer (0);
      end if;
      return Prefix_Value (Data, Q, Q.Length);
   end Magnitude;

   function Value (Data : Byte_Array; Q : Quantity)
      return Valid_Big_Integer is
   begin
      if Q.Negative then
         return -Magnitude (Data, Q);
      end if;
      return Magnitude (Data, Q);
   end Value;

   function Is_Zero (Data : Byte_Array; Q : Quantity) return Boolean is
   begin
      if not Span_Valid (Data, Q) or else Q.Length = 0 then
         return True;
      end if;
      for Offset in 0 .. Q.Length - 1 loop
         if Digit (Data, Q, Offset) /= 0 then
            return False;
         end if;
      end loop;
      return True;
   end Is_Zero;

   function Is_Negative (Data : Byte_Array; Q : Quantity) return Boolean is
   begin
      return Q.Negative and then not Is_Zero (Data, Q);
   end Is_Negative;

   function Compare (Data : Byte_Array; Left, Right : Quantity)
      return Ordering
   is
      Count : constant Byte_Count := Byte_Count'Max (Left.Length, Right.Length);
      Left_Negative : Boolean;
      Right_Negative : Boolean;
   begin
      if not Span_Valid (Data, Left) or else not Span_Valid (Data, Right) then
         return Invalid;
      end if;
      Left_Negative := Is_Negative (Data, Left);
      Right_Negative := Is_Negative (Data, Right);
      if Left_Negative /= Right_Negative then
         return (if Left_Negative then Less else Greater);
      end if;
      if Count = 0 then
         return Equal;
      end if;
      for Offset in reverse 0 .. Count - 1 loop
         if Digit (Data, Left, Offset) < Digit (Data, Right, Offset) then
            return (if Left_Negative then Greater else Less);
         elsif Digit (Data, Left, Offset) > Digit (Data, Right, Offset) then
            return (if Left_Negative then Less else Greater);
         end if;
      end loop;
      return Equal;
   end Compare;

   function Capacity_Fits
     (Data : Byte_Array; Available, Withheld, Floor, Requested : Quantity)
      return Boolean
   is
      Count : constant Byte_Count := Byte_Count'Max
        (Byte_Count'Max (Available.Length, Withheld.Length),
         Byte_Count'Max (Floor.Length, Requested.Length));
      subtype Borrow is Natural range 0 .. 3;
      Previous : Borrow := 0;
   begin
      if not Span_Valid (Data, Available) or else
        not Span_Valid (Data, Withheld) or else
        not Span_Valid (Data, Floor) or else
        not Span_Valid (Data, Requested)
      then
         return False;
      end if;
      if Count = 0 then
         return True;
      end if;
      for Offset in 0 .. Count - 1 loop
         declare
            Debit : constant Natural := Digit (Data, Withheld, Offset) +
              Digit (Data, Floor, Offset) + Digit (Data, Requested, Offset) +
              Previous;
            Credit : constant Natural := Digit (Data, Available, Offset);
         begin
            if Debit <= Credit then
               Previous := 0;
            else
               Previous := (Debit - Credit - 1) / 256 + 1;
            end if;
         end;
      end loop;
      return Previous = 0;
   end Capacity_Fits;
end Resource_Quantities;
