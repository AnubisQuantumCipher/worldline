package body Worldline.Resources with SPARK_Mode is
   use type Byte;

   --  Every lemma below has an ordinary checked Ghost body. Its Post,
   --  call-site Pre, recursion and arithmetic remain proof obligations.
   procedure Power_Order (Low, High : Byte_Count)
     with Ghost, Global => null, Always_Terminates,
          Pre => Low <= High,
          Post => Radix_Power (Low) <= Radix_Power (High)
            and then Radix_Power (High) mod Radix_Power (Low) = 0,
          Subprogram_Variant => (Decreases => High)
   is
   begin
      if Low < High then
         Power_Order (Low, High - 1);
      end if;
   end Power_Order;

   procedure Complete_Prefix (Value : Byte_Array; Count : Byte_Count)
     with Ghost, Global => null, Always_Terminates,
          Pre => Count >= Value'Length,
          Post => Prefix_Value (Value, Count) = Magnitude (Value),
          Subprogram_Variant => (Decreases => Count)
   is
   begin
      if Count > Value'Length then
         Complete_Prefix (Value, Count - 1);
      end if;
   end Complete_Prefix;

   procedure Prefix_Growth (Value : Byte_Array; Low, High : Byte_Count)
     with Ghost, Global => null, Always_Terminates,
          Pre => Low <= High,
          Post => Prefix_Value (Value, Low) <= Prefix_Value (Value, High)
            and then
              (if Prefix_Value (Value, High) < Radix_Power (Low) then
                 Prefix_Value (Value, Low) = Prefix_Value (Value, High)),
          Subprogram_Variant => (Decreases => High)
   is
   begin
      if Low < High then
         Prefix_Growth (Value, Low, High - 1);
         Power_Order (Low, High - 1);
      end if;
   end Prefix_Growth;

   procedure Low_Prefix_Exact (Value : Byte_Array; Count : Byte_Count)
     with Ghost, Global => null, Always_Terminates,
          Post => (if Magnitude (Value) < Radix_Power (Count) then
                     Prefix_Value (Value, Count) = Magnitude (Value))
   is
   begin
      if Count >= Value'Length then
         Complete_Prefix (Value, Count);
      else
         Prefix_Growth (Value, Count, Value'Length);
      end if;
   end Low_Prefix_Exact;

   procedure Prefix_Modulus
     (Value : Byte_Array; Low, High : Byte_Count)
     with Ghost, Global => null, Always_Terminates,
          Pre => Low <= High,
          Post => Prefix_Value (Value, High) mod Radix_Power (Low) =
                    Prefix_Value (Value, Low),
          Subprogram_Variant => (Decreases => High)
   is
   begin
      if Low < High then
         Prefix_Modulus (Value, Low, High - 1);
         Power_Order (Low, High - 1);
      end if;
   end Prefix_Modulus;

   procedure Value_Modulus (Value : Byte_Array; Count : Byte_Count)
     with Ghost, Global => null, Always_Terminates,
          Post => Magnitude (Value) mod Radix_Power (Count) =
                    Prefix_Value (Value, Count)
   is
   begin
      if Count >= Value'Length then
         Complete_Prefix (Value, Count);
      else
         Prefix_Modulus (Value, Count, Value'Length);
      end if;
   end Value_Modulus;

   procedure Matching_Prefix
     (Left, Right : Byte_Array; Count : Byte_Count)
     with Ghost, Global => null, Always_Terminates,
          Pre => (if Count > 0 then
                    (for all Offset in 0 .. Count - 1 =>
                       Digit_At (Left, Offset) = Digit_At (Right, Offset))),
          Post => Prefix_Value (Left, Count) = Prefix_Value (Right, Count),
          Subprogram_Variant => (Decreases => Count)
   is
   begin
      if Count > 0 then
         Matching_Prefix (Left, Right, Count - 1);
      end if;
   end Matching_Prefix;

   procedure Mismatching_Sum_Column
     (Left, Right, Result : Byte_Array; Offset : Byte_Count; Carry : Natural)
     with Ghost, Global => null, Always_Terminates,
          Pre => Offset < Byte_Count'Last and then Carry <= 1
            and then Prefix_Value (Left, Offset) + Prefix_Value (Right, Offset)
              = Prefix_Value (Result, Offset)
                + To_Big_Integer (Carry) * Radix_Power (Offset)
            and then Digit_At (Result, Offset) /=
              (Digit_At (Left, Offset) + Digit_At (Right, Offset) + Carry)
                mod 256,
          Post => Magnitude (Result) /= Magnitude (Left) + Magnitude (Right)
   is
   begin
      Value_Modulus (Left, Offset + 1);
      Value_Modulus (Right, Offset + 1);
      Value_Modulus (Result, Offset + 1);
      pragma Assert
        ((Prefix_Value (Left, Offset + 1)
          + Prefix_Value (Right, Offset + 1)) mod Radix_Power (Offset + 1)
         /= Prefix_Value (Result, Offset + 1));
   end Mismatching_Sum_Column;

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
      Low_Sum : Big_Natural := 0 with Ghost;
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
            Low_Sum := Low_Sum
              + To_Big_Integer (Wanted) * Radix_Power (Offset);
            Carry := Sum / 256;
            if Credit < Wanted then
               Comparison := Less;
            elsif Credit > Wanted then
               Comparison := Greater;
            end if;
         end;
         pragma Loop_Invariant (Low_Sum < Radix_Power (Offset + 1));
         pragma Loop_Invariant
           (Prefix_Value (Withheld, Offset + 1)
            + Prefix_Value (Floor, Offset + 1)
            + Prefix_Value (Requested, Offset + 1)
            = Low_Sum + To_Big_Integer (Carry) * Radix_Power (Offset + 1));
         pragma Loop_Invariant
           ((Comparison = Less) =
              (Prefix_Value (Available, Offset + 1) < Low_Sum));
         pragma Loop_Invariant
           ((Comparison = Equal) =
              (Prefix_Value (Available, Offset + 1) = Low_Sum));
         pragma Loop_Invariant
           ((Comparison = Greater) =
              (Prefix_Value (Available, Offset + 1) > Low_Sum));
      end loop;
      Complete_Prefix (Available, Count);
      Complete_Prefix (Withheld, Count);
      Complete_Prefix (Floor, Count);
      Complete_Prefix (Requested, Count);
      return Carry = 0 and then Comparison /= Less;
   end Fits_By_Addition;

   function Can_Reserve
     (Available, Withheld, Floor, Requested : Byte_Array) return Boolean
   is
      Count : constant Byte_Count := Byte_Count'Max
        (Byte_Count'Max (Available'Length, Withheld'Length),
         Byte_Count'Max (Floor'Length, Requested'Length));
      Previous : Borrow := 0;
      Remainder_Value : Big_Natural := 0 with Ghost;
      Column : Column_Result;
   begin
      if Count = 0 then
         return True;
      end if;
      for Offset in 0 .. Count - 1 loop
         Column := Subtract_Column
           (Byte (Digit_At (Available, Offset)),
            Byte (Digit_At (Withheld, Offset)),
            Byte (Digit_At (Floor, Offset)),
            Byte (Digit_At (Requested, Offset)), Previous);
         Remainder_Value := Remainder_Value
           + To_Big_Integer (Natural (Column.Remainder))
             * Radix_Power (Offset);
         Previous := Column.Next;
         pragma Loop_Invariant
           (Remainder_Value < Radix_Power (Offset + 1));
         pragma Loop_Invariant
           (Prefix_Value (Available, Offset + 1)
            + To_Big_Integer (Previous) * Radix_Power (Offset + 1)
            = Prefix_Value (Withheld, Offset + 1)
              + Prefix_Value (Floor, Offset + 1)
              + Prefix_Value (Requested, Offset + 1) + Remainder_Value);
      end loop;
      Complete_Prefix (Available, Count);
      Complete_Prefix (Withheld, Count);
      Complete_Prefix (Floor, Count);
      Complete_Prefix (Requested, Count);
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
         pragma Assert
           (Prefix_Value (Left, Offset) + Prefix_Value (Right, Offset)
            = Prefix_Value (Result, Offset)
              + To_Big_Integer (Carry) * Radix_Power (Offset));
         declare
            Sum : constant Natural := Digit_At (Left, Offset)
              + Digit_At (Right, Offset) + Carry;
         begin
            if Digit_At (Result, Offset) /= Sum mod 256 then
               Mismatching_Sum_Column (Left, Right, Result, Offset, Carry);
               return False;
            end if;
            Carry := Sum / 256;
         end;
         pragma Loop_Invariant
           (Prefix_Value (Left, Offset + 1) + Prefix_Value (Right, Offset + 1)
            = Prefix_Value (Result, Offset + 1)
              + To_Big_Integer (Carry) * Radix_Power (Offset + 1));
      end loop;
      Complete_Prefix (Left, Count);
      Complete_Prefix (Right, Count);
      Complete_Prefix (Result, Count);
      return Carry = 0;
   end Sum_Equals;

   procedure Try_Reserve
     (State : in out Reservation_State;
      Requested : Byte_Array;
      Accepted : out Boolean)
   is
      Carry : Natural range 0 .. 1 := 0;
      Original : constant Byte_Array := State.Outstanding with Ghost;
   begin
      Accepted := Can_Reserve
        (State.Available, State.Outstanding, State.Floor, Requested);
      if not Accepted then
         return;
      end if;
      pragma Assert
        (Magnitude (Original) + Magnitude (Requested)
         < Radix_Power (State.Capacity));
      Low_Prefix_Exact (Requested, State.Capacity);
      declare
         --  The workspace encloses the loop because this toolchain rejects
         --  loop-local composite declarations before a loop invariant.
         --  The complete snapshot is still assigned at each original capture
         --  point. Its checked copy, storage and lifetime are not free.
         Before_Step : Byte_Array (State.Outstanding'Range) with Ghost;
      begin
         for Index in State.Outstanding'Range loop
            pragma Assert
              (Prefix_Value (State.Outstanding, Index - State.Outstanding'First)
               + To_Big_Integer (Carry)
                 * Radix_Power (Index - State.Outstanding'First)
               = Prefix_Value (Original, Index - State.Outstanding'First)
                 + Prefix_Value (Requested, Index - State.Outstanding'First));
            pragma Assert
              (for all Rest in Index .. State.Outstanding'Last =>
                 State.Outstanding (Rest) = Original (Rest));
            Before_Step := State.Outstanding;
            declare
               Offset : constant Byte_Count := Index - State.Outstanding'First
                 with Ghost;
               Sum : constant Natural := Natural (State.Outstanding (Index))
                 + Digit_At (Requested, Index - State.Outstanding'First) + Carry;
            begin
               State.Outstanding (Index) := Byte (Sum mod 256);
               Carry := Sum / 256;
               Matching_Prefix (Before_Step, State.Outstanding, Offset);
            end;
            pragma Loop_Invariant
              (Prefix_Value
                 (State.Outstanding, Index - State.Outstanding'First + 1)
               + To_Big_Integer (Carry)
                 * Radix_Power (Index - State.Outstanding'First + 1)
               = Prefix_Value (Original, Index - State.Outstanding'First + 1)
                 + Prefix_Value (Requested, Index - State.Outstanding'First + 1));
            pragma Loop_Invariant
              (if Index < State.Outstanding'Last then
                 (for all Rest in Index + 1 .. State.Outstanding'Last =>
                    State.Outstanding (Rest) = Original (Rest)));
         end loop;
      end;
      pragma Assert (Carry = 0);
   end Try_Reserve;
end Worldline.Resources;
