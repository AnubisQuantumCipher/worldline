package body Evaluation_Epoch with SPARK_Mode is
   function Nonnegative_Valid (Data : Byte_Array; Q : Quantity) return Boolean
   with Global => null,
     Post => Nonnegative_Valid'Result =
       (Span_Valid (Data, Q) and then Value (Data, Q) >= 0)
   is
   begin
      return Span_Valid (Data, Q) and then not Is_Negative (Data, Q);
   end Nonnegative_Valid;

   --  These total Ghost helpers expose the byte-column equations already
   --  required by Resource_Quantities. They do not call either Epoch decision.
   --  Every helper body, access, Post and termination argument remains required.
   function Scale_Column
     (Factor : Natural; Unit_Value : Valid_Big_Integer)
      return Valid_Big_Integer
   with Ghost, Global => null,
     Post => Scale_Column'Result = To_Big_Integer (Factor) * Unit_Value
       and then (if Unit_Value >= 0 then Scale_Column'Result >= 0)
   is
      Done : Natural := 0;
      Result : Valid_Big_Integer := To_Big_Integer (0);
   begin
      while Done < Factor loop
         pragma Loop_Invariant (Done <= Factor);
         pragma Loop_Invariant
           (Result = To_Big_Integer (Done) * Unit_Value);
         pragma Loop_Invariant (if Unit_Value >= 0 then Result >= 0);
         pragma Loop_Variant (Decreases => Factor - Done);
         Result := Result + Unit_Value;
         Done := Done + 1;
      end loop;
      return Result;
   end Scale_Column;

   procedure Column_Bounds
     (Low, Place : Valid_Big_Integer; Digit_Value : Natural)
   with Ghost, Global => null, Always_Terminates,
     Post => (if Place > 0 and then Low >= 0 and then Low < Place
                  and then Digit_Value <= 255 then
       Low + To_Big_Integer (Digit_Value) * Place >= 0 and then
       Low + To_Big_Integer (Digit_Value) * Place <
         To_Big_Integer (256) * Place)
   is
   begin
      if Place <= 0 or else Low < 0 or else Low >= Place
        or else Digit_Value > 255 then
         return;
      end if;
      declare
         Contribution : constant Valid_Big_Integer :=
           Scale_Column (Digit_Value, Place);
         Unused : constant Valid_Big_Integer :=
           Scale_Column (255 - Digit_Value, Place);
         Gap : constant Valid_Big_Integer := Place - Low;
      begin
         pragma Assert (Contribution >= 0 and then Unused >= 0);
         pragma Assert (Gap > 0);
         pragma Assert
           (Low + Contribution + Gap + Unused =
              To_Big_Integer (256) * Place);
         pragma Assert (Low + Contribution >= 0);
         pragma Assert (Low + Contribution < To_Big_Integer (256) * Place);
      end;
   end Column_Bounds;

   procedure Prefix_Step
     (Data : Byte_Array; Q : Quantity; Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Post => (if Count < Byte_Count'Last then
       Radix_Power (Count + 1) = To_Big_Integer (256) * Radix_Power (Count)
       and then Prefix_Value (Data, Q, Count + 1) =
         Prefix_Value (Data, Q, Count) +
           To_Big_Integer (Digit (Data, Q, Count)) * Radix_Power (Count))
   is
   begin
      if Count < Byte_Count'Last then
         pragma Assert
           (Power_Reference (Count + 1) =
              To_Big_Integer (256) * Power_Reference (Count));
         pragma Assert
           (Prefix_Reference (Data, Q, Count + 1) =
              Prefix_Reference (Data, Q, Count) +
                To_Big_Integer (Digit (Data, Q, Count)) *
                  Power_Reference (Count));
         pragma Assert (Radix_Power (Count) = Power_Reference (Count));
         pragma Assert
           (Prefix_Value (Data, Q, Count) = Prefix_Reference (Data, Q, Count));
         pragma Assert
           (Radix_Power (Count + 1) =
              To_Big_Integer (256) * Radix_Power (Count));
         pragma Assert
           (Prefix_Value (Data, Q, Count + 1) =
              Prefix_Value (Data, Q, Count) +
                To_Big_Integer (Digit (Data, Q, Count)) * Radix_Power (Count));
      end if;
   end Prefix_Step;

   procedure Prefix_Bounds
     (Data : Byte_Array; Q : Quantity; Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Subprogram_Variant => (Decreases => Count),
     Post => Prefix_Value (Data, Q, Count) >= 0 and then
       Prefix_Value (Data, Q, Count) < Radix_Power (Count)
   is
   begin
      if Count > 0 then
         Prefix_Bounds (Data, Q, Count - 1);
         Prefix_Step (Data, Q, Count - 1);
         Column_Bounds
           (Prefix_Value (Data, Q, Count - 1), Radix_Power (Count - 1),
            Digit (Data, Q, Count - 1));
      else
         pragma Assert (Prefix_Value (Data, Q, Count) = 0);
         pragma Assert (Radix_Power (Count) = 1);
      end if;
   end Prefix_Bounds;

   procedure Prefix_Padding
     (Data : Byte_Array; Q : Quantity; Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Subprogram_Variant => (Decreases => Count),
     Post => (if Span_Valid (Data, Q) and then Q.Length <= Count then
       Prefix_Value (Data, Q, Count) = Magnitude (Data, Q))
   is
   begin
      if not Span_Valid (Data, Q) or else Count < Q.Length then
         return;
      end if;
      if Count > Q.Length then
         Prefix_Padding (Data, Q, Count - 1);
         Prefix_Step (Data, Q, Count - 1);
         pragma Assert (Digit (Data, Q, Count - 1) = 0);
         pragma Assert
           (Prefix_Value (Data, Q, Count) = Prefix_Value (Data, Q, Count - 1));
      else
         pragma Assert (Prefix_Value (Data, Q, Count) = Magnitude (Data, Q));
      end if;
   end Prefix_Padding;

   function Power_Factor (Low, High : Byte_Count) return Valid_Big_Integer
   with Ghost, Global => null,
     Subprogram_Variant => (Decreases => High),
     Post => Power_Factor'Result >= 1 and then
       (if Low <= High then Radix_Power (High) =
          Radix_Power (Low) * Power_Factor'Result)
   is
   begin
      if High <= Low then
         return To_Big_Integer (1);
      end if;
      declare
         Prior : constant Valid_Big_Integer := Power_Factor (Low, High - 1);
      begin
         pragma Assert
           (Radix_Power (High) = To_Big_Integer (256) * Radix_Power (High - 1));
         pragma Assert (Radix_Power (High - 1) = Radix_Power (Low) * Prior);
         return To_Big_Integer (256) * Prior;
      end;
   end Power_Factor;

   function Prefix_Tail
     (Data : Byte_Array; Q : Quantity; Low, High : Byte_Count)
      return Valid_Big_Integer
   with Ghost, Global => null,
     Subprogram_Variant => (Decreases => High),
     Post => Prefix_Tail'Result >= 0 and then
       (if Low <= High then Prefix_Value (Data, Q, High) =
          Prefix_Value (Data, Q, Low) + Radix_Power (Low) * Prefix_Tail'Result)
   is
   begin
      if High <= Low then
         return To_Big_Integer (0);
      end if;
      declare
         Prior : constant Valid_Big_Integer := Prefix_Tail (Data, Q, Low, High - 1);
         Position : constant Valid_Big_Integer := Power_Factor (Low, High - 1);
         Contribution : constant Valid_Big_Integer :=
           Scale_Column (Digit (Data, Q, High - 1), Position);
      begin
         Prefix_Step (Data, Q, High - 1);
         pragma Assert
           (Prefix_Value (Data, Q, High - 1) =
              Prefix_Value (Data, Q, Low) + Radix_Power (Low) * Prior);
         pragma Assert (Radix_Power (High - 1) = Radix_Power (Low) * Position);
         pragma Assert
           (Prefix_Value (Data, Q, High) = Prefix_Value (Data, Q, Low) +
              Radix_Power (Low) * (Prior + Contribution));
         return Prior + Contribution;
      end;
   end Prefix_Tail;

   --  Keep the scalar Euclidean witness separate from recursive byte-prefix
   --  producers. These total Ghost bodies are additional proof obligations;
   --  no imported theorem or unchecked assumption establishes their Posts.
   procedure Positive_Multiple
     (Place, Multiplier : Valid_Big_Integer)
   with Ghost, Global => null, Always_Terminates,
     Post => (if Place > 0 and then Multiplier >= 1 then
       Place * Multiplier >= Place)
   is
   begin
      if Place <= 0 or else Multiplier < 1 then
         return;
      end if;
      declare
         Excess : constant Valid_Big_Integer := Multiplier - 1;
         Contribution : constant Valid_Big_Integer := Place * Excess;
      begin
         pragma Assert (Excess >= 0);
         pragma Assert (Contribution >= 0);
         pragma Assert (Place * Multiplier = Place + Contribution);
         pragma Assert (Place * Multiplier >= Place);
      end;
   end Positive_Multiple;

   procedure Remainder_From_Witness
     (Low, Place, Tail : Valid_Big_Integer)
   with Ghost, Global => null, Always_Terminates,
     Post => (if Place > 0 and then Low >= 0 and then Low < Place
                  and then Tail >= 0 then
       (Low + Place * Tail) / Place = Tail and then
       (Low + Place * Tail) mod Place = Low)
   is
   begin
      if Place <= 0 or else Low < 0 or else Low >= Place or else Tail < 0 then
         return;
      end if;
      declare
         Whole : constant Valid_Big_Integer := Low + Place * Tail;
         Quotient : constant Valid_Big_Integer := Whole / Place;
         Remainder : constant Valid_Big_Integer := Whole mod Place;
      begin
         pragma Assert (Whole >= 0);
         pragma Assert (Quotient >= 0);
         pragma Assert (Remainder >= 0 and then Remainder < Place);
         pragma Assert (Whole = Place * Quotient + Remainder);
         if Quotient < Tail then
            declare
               Difference : constant Valid_Big_Integer := Tail - Quotient;
            begin
               pragma Assert (Difference >= 1);
               Positive_Multiple (Place, Difference);
               pragma Assert
                 (Place * Tail = Place * Quotient + Place * Difference);
               pragma Assert (Remainder = Low + Place * Difference);
               pragma Assert (Remainder >= Place);
               pragma Assert (False);
            end;
         elsif Quotient > Tail then
            declare
               Difference : constant Valid_Big_Integer := Quotient - Tail;
            begin
               pragma Assert (Difference >= 1);
               Positive_Multiple (Place, Difference);
               pragma Assert
                 (Place * Quotient = Place * Tail + Place * Difference);
               pragma Assert (Low = Remainder + Place * Difference);
               pragma Assert (Low >= Place);
               pragma Assert (False);
            end;
         end if;
         pragma Assert (Quotient = Tail);
         pragma Assert (Remainder = Low);
      end;
   end Remainder_From_Witness;

   procedure Prefix_Modulus
     (Data : Byte_Array; Q : Quantity; Low, High : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Post => (if Low <= High then
       Prefix_Value (Data, Q, High) mod Radix_Power (Low) =
         Prefix_Value (Data, Q, Low))
   is
   begin
      if Low > High then
         return;
      end if;
      Prefix_Bounds (Data, Q, Low);
      declare
         Tail : constant Valid_Big_Integer := Prefix_Tail (Data, Q, Low, High);
      begin
         pragma Assert
           (Prefix_Value (Data, Q, High) = Prefix_Value (Data, Q, Low) +
              Radix_Power (Low) * Tail);
         Remainder_From_Witness
           (Prefix_Value (Data, Q, Low), Radix_Power (Low), Tail);
         pragma Assert
           (Prefix_Value (Data, Q, High) mod Radix_Power (Low) =
              Prefix_Value (Data, Q, Low));
      end;
   end Prefix_Modulus;

   procedure Magnitude_Modulus
     (Data : Byte_Array; Q : Quantity; Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Post => (if Span_Valid (Data, Q) then
       Magnitude (Data, Q) mod Radix_Power (Count) =
         Prefix_Value (Data, Q, Count))
   is
   begin
      if not Span_Valid (Data, Q) then
         return;
      end if;
      if Count >= Q.Length then
         Prefix_Padding (Data, Q, Count);
         Prefix_Bounds (Data, Q, Count);
      else
         Prefix_Modulus (Data, Q, Count, Q.Length);
         pragma Assert
           (Magnitude (Data, Q) = Prefix_Value (Data, Q, Q.Length));
      end if;
      pragma Assert
        (Magnitude (Data, Q) mod Radix_Power (Count) =
           Prefix_Value (Data, Q, Count));
   end Magnitude_Modulus;

   procedure Unsigned_Value (Data : Byte_Array; Q : Quantity)
   with Ghost, Global => null, Always_Terminates,
     Post => (if Nonnegative_Valid (Data, Q) then
       Value (Data, Q) = Magnitude (Data, Q))
   is
   begin
      if Nonnegative_Valid (Data, Q) then
         if Q.Negative then
            pragma Assert (Is_Zero (Data, Q));
            pragma Assert (Magnitude (Data, Q) = 0);
         end if;
         pragma Assert (Value (Data, Q) = Magnitude (Data, Q));
      end if;
   end Unsigned_Value;

   function Carry_Input
     (Data : Byte_Array; Before, After : Quantity;
      Offset : Byte_Count; Carry : Natural) return Boolean is
     (Offset < Byte_Count'Last and then Carry <= 1 and then
        Prefix_Value (Data, After, Offset) +
          To_Big_Integer (Carry) * Radix_Power (Offset) =
            Prefix_Value (Data, Before, Offset) + 1)
   with Ghost, Global => null;

   procedure Column_Division (Column : Natural)
   with Ghost, Global => null, Always_Terminates,
     Post => (if Column <= 256 then
       Column / 256 <= 1 and then Column mod 256 <= 255 and then
       To_Big_Integer (Column) = To_Big_Integer (Column mod 256) +
         To_Big_Integer (256) * To_Big_Integer (Column / 256))
   is
   begin
      if Column <= 256 then
         pragma Assert (Column = Column mod 256 + 256 * (Column / 256));
         pragma Assert
           (To_Big_Integer (Column) = To_Big_Integer (Column mod 256) +
              To_Big_Integer (256) * To_Big_Integer (Column / 256));
      end if;
   end Column_Division;

   procedure Matching_Column
     (Data : Byte_Array; Before, After : Quantity;
      Offset : Byte_Count; Carry : Natural)
   with Ghost, Global => null, Always_Terminates,
     Post => (if Carry_Input (Data, Before, After, Offset, Carry)
       and then Digit (Data, After, Offset) =
         (Digit (Data, Before, Offset) + Carry) mod 256 then
       Prefix_Value (Data, After, Offset + 1) +
         To_Big_Integer ((Digit (Data, Before, Offset) + Carry) / 256) *
           Radix_Power (Offset + 1) =
             Prefix_Value (Data, Before, Offset + 1) + 1)
   is
   begin
      if not Carry_Input (Data, Before, After, Offset, Carry) then
         return;
      end if;
      if Digit (Data, After, Offset) /=
        (Digit (Data, Before, Offset) + Carry) mod 256 then
         return;
      end if;
      Prefix_Step (Data, Before, Offset);
      Prefix_Step (Data, After, Offset);
      Column_Division (Digit (Data, Before, Offset) + Carry);
      pragma Assert
        (To_Big_Integer (Digit (Data, Before, Offset) + Carry) =
           To_Big_Integer (Digit (Data, Before, Offset)) + To_Big_Integer (Carry));
      pragma Assert
        (Prefix_Value (Data, After, Offset + 1) +
           To_Big_Integer ((Digit (Data, Before, Offset) + Carry) / 256) *
             Radix_Power (Offset + 1) =
               Prefix_Value (Data, Before, Offset + 1) + 1);
   end Matching_Column;

   procedure Increment_Modulus (Value, Place : Valid_Big_Integer)
   with Ghost, Global => null, Always_Terminates,
     Post => (if Value >= 0 and then Place > 0 then
       (Value + 1) mod Place = ((Value mod Place) + 1) mod Place)
   is
   begin
      if Value < 0 or else Place <= 0 then
         return;
      end if;
      pragma Assert (Value = Place * (Value / Place) + Value mod Place);
      pragma Assert
        ((Value + 1) mod Place = ((Value mod Place) + 1) mod Place);
   end Increment_Modulus;

   procedure Mismatching_Column
     (Data : Byte_Array; Before, After : Quantity;
      Offset : Byte_Count; Carry : Natural)
   with Ghost, Global => null, Always_Terminates,
     Post => (if Span_Valid (Data, Before) and then Span_Valid (Data, After)
       and then Carry_Input (Data, Before, After, Offset, Carry)
       and then Digit (Data, After, Offset) /=
         (Digit (Data, Before, Offset) + Carry) mod 256 then
       Magnitude (Data, After) /= Magnitude (Data, Before) + 1)
   is
   begin
      if not Span_Valid (Data, Before) or else not Span_Valid (Data, After)
        or else not Carry_Input (Data, Before, After, Offset, Carry) then
         return;
      end if;
      if Digit (Data, After, Offset) =
        (Digit (Data, Before, Offset) + Carry) mod 256 then
         return;
      end if;
      Prefix_Step (Data, Before, Offset);
      Prefix_Step (Data, After, Offset);
      Prefix_Bounds (Data, After, Offset);
      Column_Division (Digit (Data, Before, Offset) + Carry);
      Magnitude_Modulus (Data, Before, Offset + 1);
      Magnitude_Modulus (Data, After, Offset + 1);
      Increment_Modulus (Magnitude (Data, Before), Radix_Power (Offset + 1));
      declare
         Place : constant Valid_Big_Integer := Radix_Power (Offset);
         Low : constant Valid_Big_Integer := Prefix_Value (Data, After, Offset);
         Column : constant Natural := Digit (Data, Before, Offset) + Carry;
         Wanted : constant Valid_Big_Integer :=
           Low + To_Big_Integer (Column mod 256) * Place;
      begin
         Column_Bounds (Low, Place, Column mod 256);
         pragma Assert (Wanted >= 0 and then Wanted < Radix_Power (Offset + 1));
         pragma Assert
           (Prefix_Value (Data, Before, Offset + 1) + 1 =
              Wanted + To_Big_Integer (Column / 256) * Radix_Power (Offset + 1));
         pragma Assert
           ((Prefix_Value (Data, Before, Offset + 1) + 1)
              mod Radix_Power (Offset + 1) = Wanted);
         pragma Assert
           ((Magnitude (Data, Before) + 1) mod Radix_Power (Offset + 1) = Wanted);
         pragma Assert (Prefix_Value (Data, After, Offset + 1) /= Wanted);
         pragma Assert (Magnitude (Data, After) /= Magnitude (Data, Before) + 1);
      end;
   end Mismatching_Column;

   function Same_Value (Data : Byte_Array; Left, Right : Quantity) return Boolean is
   begin
      --  Full executable digit equality is sufficient even when distinct
      --  owned spans carry the same epoch. Empty and signed-zero quantities
      --  still use the original nonnegative/valid guards. Unequal lengths,
      --  differing digits and other inputs retain the original comparison.
      if Nonnegative_Valid (Data, Left) and then
        Nonnegative_Valid (Data, Right) and then
        Left.Length = Right.Length and then
        (Left.Length = 0 or else
           (for all Offset in Byte_Count range 0 .. Left.Length - 1 =>
              Digit (Data, Left, Offset) = Digit (Data, Right, Offset)))
      then
         return True;
      end if;
      return Nonnegative_Valid (Data, Left) and then
        Nonnegative_Valid (Data, Right) and then Compare (Data, Left, Right) = Equal;
   end Same_Value;

   function Is_Successor
     (Data : Byte_Array; Before, After : Quantity) return Boolean
   is
      Count : constant Byte_Count := Byte_Count'Max (Before.Length, After.Length);
      Offset : Byte_Count := 0;
      Carry : Natural range 0 .. 1 := 1;
      Column : Natural;
   begin
      if not Nonnegative_Valid (Data, Before) or else
        not Nonnegative_Valid (Data, After) then
         return False;
      end if;
      --  Exact padding and sign bridges retain negative-zero acceptance.
      Prefix_Padding (Data, Before, Count);
      Prefix_Padding (Data, After, Count);
      Unsigned_Value (Data, Before);
      Unsigned_Value (Data, After);
      while Offset < Count loop
         pragma Loop_Invariant (Offset <= Count);
         pragma Loop_Invariant
           (Prefix_Value (Data, After, Offset) + To_Big_Integer (Carry) *
              Radix_Power (Offset) = Prefix_Value (Data, Before, Offset) + 1);
         pragma Loop_Variant (Decreases => Count - Offset);
         Column := Digit (Data, Before, Offset) + Carry;
         if Digit (Data, After, Offset) /= Column mod 256 then
            Mismatching_Column (Data, Before, After, Offset, Carry);
            pragma Assert (Value (Data, After) /= Value (Data, Before) + 1);
            return False;
         end if;
         Matching_Column (Data, Before, After, Offset, Carry);
         Carry := Column / 256;
         Offset := Offset + 1;
      end loop;
      pragma Assert (Offset = Count);
      pragma Assert
        (Prefix_Value (Data, Before, Count) = Magnitude (Data, Before));
      pragma Assert
        (Prefix_Value (Data, After, Count) = Magnitude (Data, After));
      pragma Assert
        (Value (Data, After) + To_Big_Integer (Carry) * Radix_Power (Count) =
           Value (Data, Before) + 1);
      pragma Assert
        ((Carry = 0) = (Value (Data, After) = Value (Data, Before) + 1));
      return Carry = 0;
   end Is_Successor;
end Evaluation_Epoch;
