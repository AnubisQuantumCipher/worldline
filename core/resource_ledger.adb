
package body Resource_Ledger with SPARK_Mode is
   use type Byte;

   --  Closed arithmetic/frame bridges. Every body, recursive call, range,
   --  predicate, assertion and termination check is an actual obligation.
   --  These checked Ghost operations are not claimed to have zero native cost.
   function Whole (Data : Byte_Array) return Quantity is
     ((False, (if Data'Length = 0 then 1 else Data'First), Data'Length))
   with Ghost, Global => null;

   --  Private arithmetic decompositions. These are checked Ghost bodies, not
   --  imported facts. Their own assertions, Posts and termination must prove.
   function Column_Product
     (Factor : Natural; Place : Valid_Big_Integer) return Valid_Big_Integer
   with Ghost, Global => null,
     Pre => Place >= 0,
     Post => Column_Product'Result = To_Big_Integer (Factor) * Place
       and then Column_Product'Result >= 0
       and then (if Factor > 0 then Column_Product'Result >= Place)
   is
      Done : Natural := 0;
      Product : Valid_Big_Integer := To_Big_Integer (0);
   begin
      while Done < Factor loop
         pragma Loop_Invariant (Done <= Factor);
         pragma Loop_Invariant (Product >= 0);
         pragma Loop_Invariant (Product = To_Big_Integer (Done) * Place);
         pragma Loop_Invariant (if Done > 0 then Product >= Place);
         pragma Loop_Variant (Decreases => Factor - Done);
         Product := Product + Place;
         Done := Done + 1;
      end loop;
      return Product;
   end Column_Product;

   procedure Column_Bounds
     (Low, Place : Valid_Big_Integer; Column : Natural)
   with Ghost, Global => null, Always_Terminates,
     Pre => Low >= 0 and then Place > 0 and then Low < Place
       and then Column <= 255,
     Post => Low + To_Big_Integer (Column) * Place >= 0
       and then Low + To_Big_Integer (Column) * Place <
         To_Big_Integer (256) * Place
   is
      Used : constant Valid_Big_Integer := Column_Product (Column, Place);
      Spare : constant Valid_Big_Integer := Column_Product (255 - Column, Place);
      Gap : constant Valid_Big_Integer := Place - Low;
   begin
      pragma Assert (Used >= 0 and then Spare >= 0 and then Gap > 0);
      pragma Assert
        ((Low + Used) + Gap + Spare = To_Big_Integer (256) * Place);
      pragma Assert (Gap + Spare > 0);
   end Column_Bounds;

   procedure Power_Factor (Low, Extra : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Post => (if Low <= Byte_Count'Last - Extra then
       Power_Reference (Low + Extra) =
         Power_Reference (Low) * Power_Reference (Extra)),
     Subprogram_Variant => (Decreases => Extra)
   is
   begin
      if Low <= Byte_Count'Last - Extra and then Extra > 0 then
         Power_Factor (Low, Extra - 1);
         pragma Assert
           (Power_Reference (Low + Extra) =
              To_Big_Integer (256) * Power_Reference (Low + Extra - 1));
         pragma Assert
           (Power_Reference (Extra) =
              To_Big_Integer (256) * Power_Reference (Extra - 1));
      end if;
   end Power_Factor;

   procedure Power_Monotone (Low, High : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Post => (if Low <= High then
       Power_Reference (Low) <= Power_Reference (High)),
     Subprogram_Variant => (Decreases => High)
   is
   begin
      if Low < High then
         Power_Monotone (Low, High - 1);
         pragma Assert (Power_Reference (High - 1) >= 1);
         pragma Assert
           (Power_Reference (High) =
              To_Big_Integer (256) * Power_Reference (High - 1));
      end if;
   end Power_Monotone;

   procedure Prefix_Quotient
     (Data : Byte_Array; Item : Quantity; Low, High : Byte_Count;
      Quotient : out Valid_Big_Integer)
   with Ghost, Global => null, Always_Terminates,
     Post => Quotient >= 0 and then
       (if Low <= High then
          Prefix_Reference (Data, Item, High) =
            Prefix_Reference (Data, Item, Low) +
              Power_Reference (Low) * Quotient),
     Subprogram_Variant => (Decreases => High)
   is
   begin
      Quotient := To_Big_Integer (0);
      if Low < High then
         Prefix_Quotient (Data, Item, Low, High - 1, Quotient);
         Power_Factor (Low, High - 1 - Low);
         declare
            Prior : constant Valid_Big_Integer := Quotient;
            Tail : constant Valid_Big_Integer :=
              To_Big_Integer (Digit (Data, Item, High - 1)) *
                Power_Reference (High - 1 - Low);
         begin
            pragma Assert (Tail >= 0);
            pragma Assert
              (Prefix_Reference (Data, Item, High - 1) =
                 Prefix_Reference (Data, Item, Low) +
                   Power_Reference (Low) * Prior);
            Quotient := Prior + Tail;
            pragma Assert
              (Power_Reference (Low) * Quotient =
                 Power_Reference (Low) * Prior +
                   To_Big_Integer (Digit (Data, Item, High - 1)) *
                     Power_Reference (High - 1));
         end;
      end if;
   end Prefix_Quotient;

   procedure Remainder_Witness
     (Value, Low, Place, Quotient : Valid_Big_Integer)
   with Ghost, Global => null, Always_Terminates,
     Pre => Value >= 0 and then Place > 0 and then Low >= 0
       and then Low < Place and then Value = Low + Place * Quotient,
     Post => Value mod Place = Low and then Value >= Low
   is
      Actual_Q : constant Valid_Big_Integer := Value / Place;
      Actual_R : constant Valid_Big_Integer := Value mod Place;
   begin
      pragma Assert (Value = Actual_Q * Place + Actual_R);
      pragma Assert (Actual_R >= 0 and then Actual_R < Place);
      if Quotient < Actual_Q then
         pragma Assert ((Actual_Q - Quotient) * Place >= Place);
         pragma Assert (Low = (Actual_Q - Quotient) * Place + Actual_R);
         pragma Assert (False);
      elsif Quotient > Actual_Q then
         pragma Assert ((Quotient - Actual_Q) * Place >= Place);
         pragma Assert (Actual_R = (Quotient - Actual_Q) * Place + Low);
         pragma Assert (False);
      end if;
      pragma Assert (Quotient = Actual_Q and then Low = Actual_R);
   end Remainder_Witness;

   procedure Advance_Column
     (Left_Low, Right_Low, Low, Place : Valid_Big_Integer;
      Left_Digit, Right_Digit, Old_Carry, New_Carry, Octet : Natural;
      Add : Boolean)
   with Ghost, Global => null, Always_Terminates,
     Pre => Place > 0 and then Low >= 0 and then Low < Place
       and then Left_Digit <= 255 and then Right_Digit <= 255
       and then Old_Carry <= 1 and then New_Carry <= 1 and then Octet <= 255
       and then
         (if Add then
            Left_Low + Right_Low = Low + To_Big_Integer (Old_Carry) * Place
            and then Left_Digit + Right_Digit + Old_Carry =
              Octet + 256 * New_Carry
          else Left_Low - Right_Low = Low - To_Big_Integer (Old_Carry) * Place
            and then Left_Digit + 256 * New_Carry =
              Right_Digit + Old_Carry + Octet),
     Post => Low + To_Big_Integer (Octet) * Place >= 0 and then
       Low + To_Big_Integer (Octet) * Place < To_Big_Integer (256) * Place
       and then
         (if Add then
            (Left_Low + To_Big_Integer (Left_Digit) * Place) +
              (Right_Low + To_Big_Integer (Right_Digit) * Place) =
              (Low + To_Big_Integer (Octet) * Place) +
                To_Big_Integer (New_Carry) * (To_Big_Integer (256) * Place)
          else
            (Left_Low + To_Big_Integer (Left_Digit) * Place) -
              (Right_Low + To_Big_Integer (Right_Digit) * Place) =
              (Low + To_Big_Integer (Octet) * Place) -
                To_Big_Integer (New_Carry) * (To_Big_Integer (256) * Place))
   is
   begin
      Column_Bounds (Low, Place, Octet);
      if Add then
         pragma Assert
           (To_Big_Integer (Left_Digit) + To_Big_Integer (Right_Digit) +
              To_Big_Integer (Old_Carry) = To_Big_Integer (Octet) +
                To_Big_Integer (256) * To_Big_Integer (New_Carry));
      else
         pragma Assert
           (To_Big_Integer (Left_Digit) +
              To_Big_Integer (256) * To_Big_Integer (New_Carry) =
                To_Big_Integer (Right_Digit) + To_Big_Integer (Old_Carry) +
                  To_Big_Integer (Octet));
      end if;
   end Advance_Column;

   procedure Combined_Remainder
     (Left, Right, Left_Low, Right_Low, Produced, Place : Valid_Big_Integer;
      Carry : Natural; Add : Boolean)
   with Ghost, Global => null, Always_Terminates,
     Pre => Left >= 0 and then Right >= 0 and then Place > 0
       and then Left_Low = Left mod Place and then Right_Low = Right mod Place
       and then Produced >= 0 and then Produced < Place and then Carry <= 1
       and then
         (if Add then Left_Low + Right_Low =
            Produced + To_Big_Integer (Carry) * Place
          else Left >= Right and then Left_Low - Right_Low =
            Produced - To_Big_Integer (Carry) * Place),
     Post => (if Add then (Left + Right) mod Place = Produced
                 and then Left + Right >= Produced
              else (Left - Right) mod Place = Produced
                 and then Left - Right >= Produced)
   is
      Left_High : constant Valid_Big_Integer := Left / Place;
      Right_High : constant Valid_Big_Integer := Right / Place;
   begin
      pragma Assert (Left = Left_Low + Place * Left_High);
      pragma Assert (Right = Right_Low + Place * Right_High);
      if Add then
         declare
            High : constant Valid_Big_Integer :=
              Left_High + Right_High + To_Big_Integer (Carry);
            Value : constant Valid_Big_Integer := Left + Right;
         begin
            pragma Assert (Value = Produced + Place * High);
            Remainder_Witness (Value, Produced, Place, High);
         end;
      else
         declare
            High : constant Valid_Big_Integer :=
              Left_High - Right_High - To_Big_Integer (Carry);
            Value : constant Valid_Big_Integer := Left - Right;
         begin
            pragma Assert (Value = Produced + Place * High);
            Remainder_Witness (Value, Produced, Place, High);
         end;
      end if;
   end Combined_Remainder;

   procedure Equal_Prefix
     (Left_Data, Right_Data : Byte_Array; Left, Right : Quantity;
      Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => (if Count > 0 then
       (for all K in 0 .. Count - 1 =>
          Digit (Left_Data, Left, K) = Digit (Right_Data, Right, K))),
     Post => Prefix_Reference (Left_Data, Left, Count) =
       Prefix_Reference (Right_Data, Right, Count),
     Subprogram_Variant => (Decreases => Count)
   is
   begin
      if Count > 0 then
         Equal_Prefix (Left_Data, Right_Data, Left, Right, Count - 1);
         pragma Assert
           (Digit (Left_Data, Left, Count - 1) =
              Digit (Right_Data, Right, Count - 1));
      end if;
   end Equal_Prefix;

   procedure Padded_Prefix
     (Data : Byte_Array; Item : Quantity; Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Span_Valid (Data, Item) and then Count >= Item.Length,
     Post => Prefix_Reference (Data, Item, Count) = Magnitude (Data, Item),
     Subprogram_Variant => (Decreases => Count)
   is
   begin
      if Count > Item.Length then
         Padded_Prefix (Data, Item, Count - 1);
         pragma Assert (Digit (Data, Item, Count - 1) = 0);
      else
         pragma Assert
           (Prefix_Value (Data, Item, Count) =
              Prefix_Reference (Data, Item, Count));
      end if;
   end Padded_Prefix;

   procedure Bounded_Prefix
     (Data : Byte_Array; Item : Quantity; Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Post => Prefix_Reference (Data, Item, Count) >= 0 and then
       Prefix_Reference (Data, Item, Count) < Power_Reference (Count),
     Subprogram_Variant => (Decreases => Count)
   is
   begin
      if Count > 0 then
         Bounded_Prefix (Data, Item, Count - 1);
         declare
            Previous : constant Valid_Big_Integer :=
              Prefix_Reference (Data, Item, Count - 1);
            Place : constant Valid_Big_Integer := Power_Reference (Count - 1);
            Current : constant Valid_Big_Integer :=
              To_Big_Integer (Digit (Data, Item, Count - 1));
         begin
            pragma Assert (Current >= 0 and then Current <= 255);
            pragma Assert (Previous < Place and then Place >= 1);
            Column_Bounds (Previous, Place, Digit (Data, Item, Count - 1));
            pragma Assert
              (Previous + Current * Place < To_Big_Integer (256) * Place);
         end;
      end if;
   end Bounded_Prefix;

   procedure Magnitude_Remainder
     (Data : Byte_Array; Item : Quantity; Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Span_Valid (Data, Item),
     Post => Magnitude (Data, Item) mod Power_Reference (Count) =
       Prefix_Reference (Data, Item, Count)
   is
      Full_Count : constant Byte_Count := Byte_Count'Max (Count, Item.Length);
      High : Valid_Big_Integer := To_Big_Integer (0);
   begin
      Prefix_Quotient (Data, Item, Count, Full_Count, High);
      Padded_Prefix (Data, Item, Full_Count);
      Bounded_Prefix (Data, Item, Count);
      Remainder_Witness
        (Magnitude (Data, Item), Prefix_Reference (Data, Item, Count),
         Power_Reference (Count), High);
   end Magnitude_Remainder;

   procedure Zero_Extension
     (Data : Byte_Array; Item : Quantity; Low, High : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Low <= High and then
       (if Low < High then
          (for all K in Low .. High - 1 => Digit (Data, Item, K) = 0)),
     Post => Prefix_Reference (Data, Item, High) =
       Prefix_Reference (Data, Item, Low),
     Subprogram_Variant => (Decreases => High)
   is
   begin
      if Low < High then
         Zero_Extension (Data, Item, Low, High - 1);
         pragma Assert (Digit (Data, Item, High - 1) = 0);
      end if;
   end Zero_Extension;

   procedure Output_Prefix_Value (Data : Byte_Array; Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => (for all I in Data'Range =>
       (if I - Data'First >= Count then Data (I) = 0)),
     Post => Magnitude (Data, Whole (Data)) =
       Prefix_Reference (Data, Whole (Data), Count)
   is
   begin
      if Count < Data'Length then
         pragma Assert
           (for all K in Count .. Data'Length - 1 =>
              Digit (Data, Whole (Data), K) = 0);
         Zero_Extension (Data, Whole (Data), Count, Data'Length);
         Padded_Prefix (Data, Whole (Data), Data'Length);
      else
         Padded_Prefix (Data, Whole (Data), Count);
      end if;
   end Output_Prefix_Value;


   procedure Trimmed_Value (Data : Byte_Array; Item : Quantity)
   with Ghost, Global => null, Always_Terminates,
     Pre => Span_Valid (Data, Item) and then
       (Item.Length = 0 or else Item.First = Data'First) and then
       (for all I in Data'Range =>
          (if I - Data'First >= Item.Length then Data (I) = 0)),
     Post => Magnitude (Data, Item) = Magnitude (Data, Whole (Data))
   is
   begin
      pragma Assert
        (for all K in Byte_Count range 0 .. Data'Length - 1 =>
           Digit (Data, Item, K) = Digit (Data, Whole (Data), K));
      Equal_Prefix (Data, Data, Item, Whole (Data), Data'Length);
      Padded_Prefix (Data, Item, Data'Length);
      Padded_Prefix (Data, Whole (Data), Data'Length);
   end Trimmed_Value;

   procedure Lift_Slice
     (Data : Byte_Array; Slot : Output_Span; Item : Quantity)
   with Ghost, Global => null, Always_Terminates,
     Pre => Slot_Valid (Data, Slot) and then
       Canonical_In_Slot
         (Data (Slot.First ..
            (if Slot.Length = 0 then Slot.First - 1
             else Slot.First + (Slot.Length - 1))), Slot, Item),
     Post => Span_Valid (Data, Item) and then
       Canonical_In_Slot (Data, Slot, Item) and then
       Value (Data, Item) = Value
         (Data (Slot.First ..
            (if Slot.Length = 0 then Slot.First - 1
             else Slot.First + (Slot.Length - 1))), Item)
   is
      Last : constant Byte_Count :=
        (if Slot.Length = 0 then Slot.First - 1
         else Slot.First + (Slot.Length - 1));
   begin
      pragma Assert (Span_Valid (Data, Item));
      pragma Assert
        (if Item.Length > 0 then
           (for all K in 0 .. Item.Length - 1 =>
              Digit (Data, Item, K) =
                Digit (Data (Slot.First .. Last), Item, K)));
      Equal_Prefix (Data, Data (Slot.First .. Last), Item, Item, Item.Length);
      pragma Assert (Canonical_In_Slot (Data, Slot, Item));
   end Lift_Slice;


   function Withheld_Reference
     (Data : Byte_Array; Row : Reservation_Row) return Valid_Big_Integer
   is
      Reserved_Value : constant Valid_Big_Integer := Value (Data, Row.Reserved);
   begin
      if not Span_Valid (Data, Row.Reserved) or else
        (Row.Used.Present and then not Span_Valid (Data, Row.Used.Value))
      then
         return To_Big_Integer (0);
      elsif not Row.Used.Present then
         return Reserved_Value;
      else
         declare
            Difference : constant Valid_Big_Integer :=
              Reserved_Value - Value (Data, Row.Used.Value);
         begin
            return (if Difference > 0 then Difference else To_Big_Integer (0));
         end;
      end if;
   end Withheld_Reference;

   function Row_Reference
     (Data : Byte_Array; Rows : Reservation_Array; Offset : Byte_Count)
      return Valid_Big_Integer is
   begin
      if Offset < Rows'Length then
         return Withheld_Reference (Data, Rows (Rows'First + Offset));
      end if;
      return To_Big_Integer (0);
   end Row_Reference;

   function Prefix_Total_Worker
     (Data : Byte_Array; Rows : Reservation_Array; Count : Byte_Count)
      return Valid_Big_Integer
   with Ghost, Global => null,
     Post => Prefix_Total_Worker'Result = Total_Reference (Data, Rows, Count)
   is
      Result : Valid_Big_Integer := To_Big_Integer (0);
   begin
      if Count > 0 then
         for Offset in 0 .. Count - 1 loop
            pragma Loop_Invariant
              (Result = Total_Reference (Data, Rows, Offset));
            Result := Result + Row_Reference (Data, Rows, Offset);
            pragma Assert
              (Result = Total_Reference (Data, Rows, Offset + 1));
         end loop;
         declare
            --  Strictly smaller actual producer call. Its body and variant
            --  remain required; this is not an assumed reference bridge.
            Previous : constant Valid_Big_Integer :=
              Total_Reference (Data, Rows, Count - 1);
         begin
            pragma Assert (Previous = Total_Reference (Data, Rows, Count - 1));
            pragma Assert
              (Result = Previous + Row_Reference (Data, Rows, Count - 1));
         end;
      end if;
      return Result;
   end Prefix_Total_Worker;

   --  Checked correspondence for the actual iterative total worker.  This
   --  total Ghost procedure has no caller restriction and no assumed theorem.
   procedure Total_Worker_Recurrence
     (Data : Byte_Array; Rows : Reservation_Array; Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Post =>
       (if Count = 0 then Prefix_Total_Worker (Data, Rows, Count) = 0
        else Prefix_Total_Worker (Data, Rows, Count) =
          Prefix_Total_Worker (Data, Rows, Count - 1) +
            Row_Reference (Data, Rows, Count - 1))
   is
      Current : constant Valid_Big_Integer :=
        Prefix_Total_Worker (Data, Rows, Count);
   begin
      pragma Assert (Current = Total_Reference (Data, Rows, Count));
      if Count > 0 then
         declare
            Previous : constant Valid_Big_Integer :=
              Prefix_Total_Worker (Data, Rows, Count - 1);
         begin
            pragma Assert
              (Previous = Total_Reference (Data, Rows, Count - 1));
            pragma Assert
              (Total_Reference (Data, Rows, Count) =
                 Total_Reference (Data, Rows, Count - 1) +
                   Row_Reference (Data, Rows, Count - 1));
            pragma Assert
              (Current = Previous + Row_Reference (Data, Rows, Count - 1));
         end;
      else
         pragma Assert (Current = 0);
      end if;
   end Total_Worker_Recurrence;

   --  Total guarded theorem over independent full column equations.  The
   --  Natural difference is taken only in the branch that proves its order.
   procedure Ordered_Magnitude_Columns
     (Left_Low, Right_Low, Place : Valid_Big_Integer;
      Left_Digit, Right_Digit : Natural)
   with Ghost, Global => null, Always_Terminates,
     Post =>
       (if Place > 0 and then Left_Low >= 0 and then Left_Low < Place
           and then Right_Low >= 0 and then Right_Low < Place
           and then Left_Digit <= 255 and then Right_Digit <= 255
        then
          (if Left_Digit < Right_Digit then
             Left_Low + To_Big_Integer (Left_Digit) * Place <
               Right_Low + To_Big_Integer (Right_Digit) * Place
           elsif Left_Digit > Right_Digit then
             Left_Low + To_Big_Integer (Left_Digit) * Place >
               Right_Low + To_Big_Integer (Right_Digit) * Place))
   is
   begin
      if Place > 0 and then Left_Low >= 0 and then Left_Low < Place
        and then Right_Low >= 0 and then Right_Low < Place
        and then Left_Digit <= 255 and then Right_Digit <= 255
      then
         if Left_Digit < Right_Digit then
            declare
               Difference : constant Natural := Right_Digit - Left_Digit;
               Extra : constant Valid_Big_Integer :=
                 Column_Product (Difference, Place);
               Gap : constant Valid_Big_Integer := Place - Left_Low;
            begin
               pragma Assert (Difference > 0);
               pragma Assert (Extra >= Place and then Gap > 0);
               pragma Assert
                 ((Right_Low + To_Big_Integer (Right_Digit) * Place) -
                    (Left_Low + To_Big_Integer (Left_Digit) * Place) =
                      Right_Low + Gap + (Extra - Place));
               pragma Assert (Right_Low + Gap + (Extra - Place) > 0);
            end;
         elsif Left_Digit > Right_Digit then
            declare
               Difference : constant Natural := Left_Digit - Right_Digit;
               Extra : constant Valid_Big_Integer :=
                 Column_Product (Difference, Place);
               Gap : constant Valid_Big_Integer := Place - Right_Low;
            begin
               pragma Assert (Difference > 0);
               pragma Assert (Extra >= Place and then Gap > 0);
               pragma Assert
                 ((Left_Low + To_Big_Integer (Left_Digit) * Place) -
                    (Right_Low + To_Big_Integer (Right_Digit) * Place) =
                      Left_Low + Gap + (Extra - Place));
               pragma Assert (Left_Low + Gap + (Extra - Place) > 0);
            end;
         end if;
      end if;
   end Ordered_Magnitude_Columns;

   --  Bridge a real write and its complete before image to the closed prefix
   --  equation.  Counts outside represented storage retain Digit's zero rule.
   procedure Written_Prefix_Step
     (Before, After : Byte_Array; Count : Byte_Count; Octet : Natural)
   with Ghost, Global => null, Always_Terminates,
     Post =>
       (if Count < Byte_Count'Last and then
           (if Count > 0 then
              (for all K in 0 .. Count - 1 =>
                 Digit (Before, Whole (Before), K) =
                   Digit (After, Whole (After), K)))
           and then Digit (After, Whole (After), Count) = Octet
        then Prefix_Reference (After, Whole (After), Count + 1) =
          Prefix_Reference (Before, Whole (Before), Count) +
            To_Big_Integer (Octet) * Power_Reference (Count))
   is
   begin
      if Count < Byte_Count'Last and then
        (if Count > 0 then
           (for all K in 0 .. Count - 1 =>
              Digit (Before, Whole (Before), K) =
                Digit (After, Whole (After), K)))
        and then Digit (After, Whole (After), Count) = Octet
      then
         Equal_Prefix (Before, After, Whole (Before), Whole (After), Count);
         pragma Assert
           (Prefix_Reference (After, Whole (After), Count + 1) =
              Prefix_Reference (After, Whole (After), Count) +
                To_Big_Integer (Digit (After, Whole (After), Count)) *
                  Power_Reference (Count));
      end if;
   end Written_Prefix_Step;

   --  The complete unchanged slot, including padding and the signed descriptor,
   --  determines the same full value in another equal-bounds arena.
   procedure Quantity_Slot_Frame
     (Before, After : Byte_Array; Slot : Output_Span; Item : Quantity)
   with Ghost, Global => null, Always_Terminates,
     Post =>
       (if Before'First = After'First and then Before'Last = After'Last
           and then Canonical_In_Slot (Before, Slot, Item)
           and then (for all I in Before'Range =>
             (if Contains (Slot, I) then Before (I) = After (I)))
        then Canonical_In_Slot (After, Slot, Item) and then
          Span_Valid (After, Item) and then
          Value (After, Item) = Value (Before, Item))
   is
   begin
      if Before'First = After'First and then Before'Last = After'Last
        and then Canonical_In_Slot (Before, Slot, Item)
        and then (for all I in Before'Range =>
          (if Contains (Slot, I) then Before (I) = After (I)))
      then
         pragma Assert (Span_Valid (After, Item));
         pragma Assert
           (if Item.Length > 0 then
              (for all K in 0 .. Item.Length - 1 =>
                 Contains (Slot, Item.First + K) and then
                   Digit (Before, Item, K) = Digit (After, Item, K)));
         Equal_Prefix (Before, After, Item, Item, Item.Length);
         pragma Assert
           (Magnitude (Before, Item) = Magnitude (After, Item));
         pragma Assert (Value (Before, Item) = Value (After, Item));
         pragma Assert (Canonical_In_Slot (After, Slot, Item));
      end if;
   end Quantity_Slot_Frame;

   --  Explicit checked induction step for the actual detail validator.  The
   --  ordinal and row-index forms remain distinct, with their exact crosswalk.
   procedure Checked_Detail_Step
     (Data, Detail_Data : Byte_Array; Rows : Reservation_Array;
      Details : Quantity_Array; Offset : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Post =>
       (if Details'Length = Rows'Length and then Offset < Rows'Length
           and then
             (for all J in Rows'Range =>
                (if J - Rows'First < Offset then
                   Span_Valid (Detail_Data, Details (Details'First + (J - Rows'First)))
                   and then Value
                     (Detail_Data, Details (Details'First + (J - Rows'First))) =
                       Withheld_Reference (Data, Rows (J))))
           and then Span_Valid (Detail_Data, Details (Details'First + Offset))
           and then Value (Detail_Data, Details (Details'First + Offset)) =
             Withheld_Reference (Data, Rows (Rows'First + Offset))
        then
          (for all J in Rows'Range =>
             (if J - Rows'First < Offset + 1 then
                Span_Valid (Detail_Data, Details (Details'First + (J - Rows'First)))
                and then Value
                  (Detail_Data, Details (Details'First + (J - Rows'First))) =
                    Withheld_Reference (Data, Rows (J)))))
   is
   begin
      if Details'Length = Rows'Length and then Offset < Rows'Length
        and then
          (for all J in Rows'Range =>
             (if J - Rows'First < Offset then
                Span_Valid (Detail_Data, Details (Details'First + (J - Rows'First)))
                and then Value
                  (Detail_Data, Details (Details'First + (J - Rows'First))) =
                    Withheld_Reference (Data, Rows (J))))
        and then Span_Valid (Detail_Data, Details (Details'First + Offset))
        and then Value (Detail_Data, Details (Details'First + Offset)) =
          Withheld_Reference (Data, Rows (Rows'First + Offset))
      then
         for J in Rows'Range loop
            pragma Loop_Invariant
              (for all K in Rows'Range =>
                 (if K < J and then K - Rows'First < Offset + 1 then
                    Span_Valid (Detail_Data, Details (Details'First + (K - Rows'First)))
                    and then Value
                      (Detail_Data, Details (Details'First + (K - Rows'First))) =
                        Withheld_Reference (Data, Rows (K))));
            if J - Rows'First < Offset + 1 then
               if J - Rows'First = Offset then
                  pragma Assert (J = Rows'First + Offset);
               else
                  pragma Assert (J - Rows'First < Offset);
               end if;
               pragma Assert
                 (Span_Valid (Detail_Data, Details (Details'First + (J - Rows'First))));
               pragma Assert
                 (Value (Detail_Data, Details (Details'First + (J - Rows'First))) =
                    Withheld_Reference (Data, Rows (J)));
            end if;
         end loop;
      end if;
   end Checked_Detail_Step;

   --  Preserve every earlier retained detail through the actual disjoint
   --  current-slot write.  Full bytes and descriptors, never sampled values.
   procedure Retained_Detail_Frame
     (Before, After : Byte_Array; Rows : Reservation_Array;
      Slots : Span_Array; Details : Quantity_Array; Offset : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Post =>
       (if Before'First = After'First and then Before'Last = After'Last
           and then Offset < Rows'Length
           and then Layout_Valid (Before, Slots, Details, Rows'Length)
           and then
             (for all I in Before'Range =>
                (if not Contains (Slots (Slots'First + Offset), I) then
                   Before (I) = After (I)))
           and then
             (for all J in Rows'Range =>
                (if J - Rows'First < Offset then
                   Canonical_In_Slot
                     (Before, Slots (Slots'First + (J - Rows'First)),
                      Details (Details'First + (J - Rows'First)))))
        then
          (for all J in Rows'Range =>
             (if J - Rows'First < Offset then
                Canonical_In_Slot
                  (After, Slots (Slots'First + (J - Rows'First)),
                   Details (Details'First + (J - Rows'First))) and then
                Value (After, Details (Details'First + (J - Rows'First))) =
                  Value (Before, Details (Details'First + (J - Rows'First))))))
   is
   begin
      if Before'First = After'First and then Before'Last = After'Last
        and then Offset < Rows'Length
        and then Layout_Valid (Before, Slots, Details, Rows'Length)
        and then
          (for all I in Before'Range =>
             (if not Contains (Slots (Slots'First + Offset), I) then
                Before (I) = After (I)))
        and then
          (for all J in Rows'Range =>
             (if J - Rows'First < Offset then
                Canonical_In_Slot
                  (Before, Slots (Slots'First + (J - Rows'First)),
                   Details (Details'First + (J - Rows'First)))))
      then
         for J in Rows'Range loop
            pragma Loop_Invariant
              (for all K in Rows'Range =>
                 (if K < J and then K - Rows'First < Offset then
                    Canonical_In_Slot
                      (After, Slots (Slots'First + (K - Rows'First)),
                       Details (Details'First + (K - Rows'First))) and then
                    Value (After, Details (Details'First + (K - Rows'First))) =
                      Value (Before, Details (Details'First + (K - Rows'First)))));
            if J - Rows'First < Offset then
               declare
                  Prior : constant Output_Span :=
                    Slots (Slots'First + (J - Rows'First));
                  Changed : constant Output_Span := Slots (Slots'First + Offset);
                  Item : constant Quantity :=
                    Details (Details'First + (J - Rows'First));
               begin
                  pragma Assert (Disjoint (Prior, Changed));
                  pragma Assert
                    (for all I in Before'Range =>
                       (if Contains (Prior, I) then not Contains (Changed, I)));
                  pragma Assert
                    (for all I in Before'Range =>
                       (if Contains (Prior, I) then Before (I) = After (I)));
                  Quantity_Slot_Frame (Before, After, Prior, Item);
               end;
            end if;
         end loop;
      end if;
   end Retained_Detail_Frame;


   --  The public expression executes this checked bridge. Both its body and
   --  its equivalent recurrence Post use the independent predecessor, without
   --  reentering the public checker. All original body assertions still run.
   function Prefix_Total_Checked
     (Data : Byte_Array; Rows : Reservation_Array; Count : Byte_Count)
      return Valid_Big_Integer
   is
      Result : Valid_Big_Integer := To_Big_Integer (0);
   begin
      if Count = 0 then
         Result := To_Big_Integer (0);
         pragma Assert
           (Total_Reference (Data, Rows, Count) = To_Big_Integer (0));
      else
         declare
            Previous : constant Valid_Big_Integer :=
              Total_Reference (Data, Rows, Count - 1);
            Step : constant Valid_Big_Integer :=
              Row_Reference (Data, Rows, Count - 1);
         begin
            pragma Assert
              (Previous = Total_Reference (Data, Rows, Count - 1));
            Result := Previous + Step;
            pragma Assert
              (Total_Reference (Data, Rows, Count) =
                 Total_Reference (Data, Rows, Count - 1) + Step);
         end;
      end if;
      pragma Assert (Result = Total_Reference (Data, Rows, Count));
      pragma Assert (Result = Prefix_Total_Worker (Data, Rows, Count));
      return Result;
   end Prefix_Total_Checked;

   function Storage_Sufficient
     (Data : Byte_Array; Rows : Reservation_Array; Slots : Span_Array;
      Total_Capacity : Byte_Count) return Boolean is
   begin
      if Slots'Length /= Rows'Length then
         return False;
      end if;
      for I in Rows'Range loop
         pragma Loop_Invariant
           (for all J in Rows'Range =>
              (if J < I then
                 abs Withheld_Reference (Data, Rows (J)) <
                   Radix_Power (Slots (Slots'First + (J - Rows'First)).Length)
                 and then abs Prefix_Total (Data, Rows, (J - Rows'First) + 1) <
                   Radix_Power (Total_Capacity)));
         declare
            Offset : constant Byte_Count := I - Rows'First;
            Item : constant Valid_Big_Integer :=
              Withheld_Reference (Data, Rows (I));
            Prefix : constant Valid_Big_Integer :=
              Prefix_Total (Data, Rows, Offset + 1);
         begin
            if abs Item >= Radix_Power (Slots (Slots'First + Offset).Length)
              or else abs Prefix >= Radix_Power (Total_Capacity)
            then
               return False;
            end if;
         end;
      end loop;
      return True;
   end Storage_Sufficient;

   --  Opaque checked-prefix of the detail validator. Callers hide the body
   --  and use congruence on Count. The lemmas below are where it unfolds.
   function Details_Checked
     (Data, Detail_Data : Byte_Array; Rows : Reservation_Array;
      Details : Quantity_Array; Count : Byte_Count) return Boolean is
     (Details'Length = Rows'Length and then
        (for all J in Rows'Range =>
           (if J - Rows'First < Count then
              Span_Valid
                (Detail_Data, Details (Details'First + (J - Rows'First)))
              and then Value
                (Detail_Data, Details (Details'First + (J - Rows'First))) =
                  Withheld_Reference (Data, Rows (J)))))
   with Ghost, Global => null;

   procedure Lengths_From_Layout
     (Data : Byte_Array; Slots : Span_Array; Details : Quantity_Array;
      Row_Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Layout_Valid (Data, Slots, Details, Row_Count),
     Post => Slots'Length = Row_Count and then Details'Length = Row_Count
   is
   begin
      pragma Assert (Slots'Length = Row_Count);
      pragma Assert (Details'Length = Row_Count);
   end Lengths_From_Layout;

   procedure Details_Checked_Zero
     (Data, Detail_Data : Byte_Array; Rows : Reservation_Array;
      Details : Quantity_Array)
   with Ghost, Global => null, Always_Terminates,
     Pre => Details'Length = Rows'Length,
     Post => Details_Checked (Data, Detail_Data, Rows, Details, 0)
   is
   begin
      pragma Assert
        (Details_Checked (Data, Detail_Data, Rows, Details, 0));
   end Details_Checked_Zero;

   procedure Close_Detail_Step
     (Data, Detail_Data : Byte_Array; Rows : Reservation_Array;
      Details : Quantity_Array; Offset : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Details_Checked (Data, Detail_Data, Rows, Details, Offset)
       and then Offset < Rows'Length
       and then Span_Valid
         (Detail_Data, Details (Details'First + Offset))
       and then Value (Detail_Data, Details (Details'First + Offset)) =
         Withheld_Reference (Data, Rows (Rows'First + Offset)),
     Post => Details_Checked (Data, Detail_Data, Rows, Details, Offset + 1)
   is
   begin
      pragma Assert (Details'Length = Rows'Length);
      Checked_Detail_Step (Data, Detail_Data, Rows, Details, Offset);
      pragma Assert
        (for all J in Rows'Range =>
           (if J - Rows'First < Offset + 1 then
              Span_Valid
                (Detail_Data, Details (Details'First + (J - Rows'First)))
              and then Value
                (Detail_Data, Details (Details'First + (J - Rows'First))) =
                  Withheld_Reference (Data, Rows (J))));
      pragma Assert
        (Details_Checked (Data, Detail_Data, Rows, Details, Offset + 1));
   end Close_Detail_Step;

   procedure Open_Details_Checked
     (Data, Detail_Data : Byte_Array; Rows : Reservation_Array;
      Details : Quantity_Array; Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Count = Rows'Length
       and then Details_Checked (Data, Detail_Data, Rows, Details, Count),
     Post =>
       (for all J in Rows'Range =>
          Span_Valid
            (Detail_Data, Details (Details'First + (J - Rows'First)))
          and then Value
            (Detail_Data, Details (Details'First + (J - Rows'First))) =
              Withheld_Reference (Data, Rows (J)))
   is
   begin
      pragma Assert
        (for all J in Rows'Range => J - Rows'First < Count);
      pragma Assert
        (for all J in Rows'Range =>
           Span_Valid
             (Detail_Data, Details (Details'First + (J - Rows'First)))
           and then Value
             (Detail_Data, Details (Details'First + (J - Rows'First))) =
               Withheld_Reference (Data, Rows (J)));
   end Open_Details_Checked;

   --  The detail-slot index is a machine-integer addition. Prove it in this
   --  tiny context; do not restate it in a caller's precondition.
   procedure Index_In_Details
     (Rows : Reservation_Array; Details : Quantity_Array)
   with Ghost, Global => null, Always_Terminates,
     Pre => Details'Length = Rows'Length,
     Post =>
       (for all I in Rows'Range =>
          (Details'First + (I - Rows'First)) in Details'Range)
   is
   begin
      pragma Assert
        (for all I in Rows'Range => I - Rows'First < Rows'Length);
      pragma Assert
        (for all I in Rows'Range => I - Rows'First < Details'Length);
      pragma Assert
        (for all I in Rows'Range =>
           (Details'First + (I - Rows'First)) in Details'Range);
   end Index_In_Details;

   --  Public success formula, proved here from facts the caller already
   --  holds. The precondition does not repeat the detail index.
   function Conforms_Success
     (Data : Byte_Array; Rows : Reservation_Array; Slots : Span_Array;
      Detail_Data, Total_Data : Byte_Array; Details : Quantity_Array;
      Total : Quantity; Status : Result_Status) return Boolean
   with Ghost, Global => null,
     Pre => Rows_Valid (Data, Rows)
       and then Layout_Valid (Detail_Data, Slots, Details, Rows'Length)
       and then Storage_Sufficient (Data, Rows, Slots, Total_Data'Length)
       and then Status = Computed
       and then Span_Valid (Total_Data, Total)
       and then Value (Total_Data, Total) =
         Prefix_Total (Data, Rows, Rows'Length)
       and then Details'Length = Rows'Length
       and then Slots'Length = Rows'Length
       and then Details_Checked
         (Data, Detail_Data, Rows, Details, Rows'Length)
       and then Output_Representation
         (Detail_Data, Total_Data, Slots, Details, Total),
     Post => Conforms_Success'Result =
       ((if not Rows_Valid (Data, Rows) then Status = Invalid_Input
         elsif not Layout_Valid (Detail_Data, Slots, Details, Rows'Length) then
           Status = Invalid_Output_Layout
         elsif not Storage_Sufficient (Data, Rows, Slots, Total_Data'Length) then
           Status = Insufficient_Storage
         else Status = Computed) and then
        (if Status = Computed then
           Span_Valid (Total_Data, Total) and then
           Value (Total_Data, Total) = Prefix_Total (Data, Rows, Rows'Length)
           and then
           (for all I in Rows'Range =>
              Span_Valid
                (Detail_Data, Details (Details'First + (I - Rows'First)))
              and then Value
                (Detail_Data, Details (Details'First + (I - Rows'First))) =
                  Withheld_Reference (Data, Rows (I)))
           and then Output_Representation
             (Detail_Data, Total_Data, Slots, Details, Total)
         else Total = Empty and then
           (for all I in Details'Range => Details (I) = Empty) and then
           (for all I in Detail_Data'Range => Detail_Data (I) = 0) and then
           (for all I in Total_Data'Range => Total_Data (I) = 0)))
   is
   begin
      pragma Assert (Status = Computed);
      pragma Assert (Rows_Valid (Data, Rows));
      pragma Assert
        (Layout_Valid (Detail_Data, Slots, Details, Rows'Length));
      pragma Assert
        (Storage_Sufficient (Data, Rows, Slots, Total_Data'Length));
      pragma Assert (Details'Length = Rows'Length);
      pragma Assert (Slots'Length = Rows'Length);
      Index_In_Details (Rows, Details);
      Open_Details_Checked
        (Data, Detail_Data, Rows, Details, Rows'Length);
      pragma Assert
        ((if not Rows_Valid (Data, Rows) then Status = Invalid_Input
          elsif not Layout_Valid (Detail_Data, Slots, Details, Rows'Length)
          then
            Status = Invalid_Output_Layout
          elsif not Storage_Sufficient (Data, Rows, Slots, Total_Data'Length)
          then
            Status = Insufficient_Storage
          else Status = Computed)
         and then
         (if Status = Computed then
            Span_Valid (Total_Data, Total) and then
            Value (Total_Data, Total) =
              Prefix_Total (Data, Rows, Rows'Length)
            and then
            (for all I in Rows'Range =>
               Span_Valid
                 (Detail_Data, Details (Details'First + (I - Rows'First)))
               and then Value
                 (Detail_Data, Details (Details'First + (I - Rows'First))) =
                   Withheld_Reference (Data, Rows (I)))
            and then Output_Representation
              (Detail_Data, Total_Data, Slots, Details, Total)
          else Total = Empty and then
            (for all I in Details'Range => Details (I) = Empty) and then
            (for all I in Detail_Data'Range => Detail_Data (I) = 0) and then
            (for all I in Total_Data'Range => Total_Data (I) = 0)));
      return True;
   end Conforms_Success;

   function Result_Conforms
     (Data : Byte_Array; Rows : Reservation_Array; Slots : Span_Array;
      Detail_Data, Total_Data : Byte_Array; Details : Quantity_Array;
      Total : Quantity; Status : Result_Status) return Boolean
   is
      Completed : Byte_Count := 0 with Ghost;
   begin
      if not Rows_Valid (Data, Rows) then
         if Status /= Invalid_Input then
            return False;
         end if;
      elsif not Layout_Valid (Detail_Data, Slots, Details, Rows'Length) then
         if Status /= Invalid_Output_Layout then
            return False;
         end if;
      elsif not Storage_Sufficient (Data, Rows, Slots, Total_Data'Length) then
         if Status /= Insufficient_Storage then
            return False;
         end if;
      else
         if Status /= Computed or else not Span_Valid (Total_Data, Total)
           or else Value (Total_Data, Total) /=
             Prefix_Total (Data, Rows, Rows'Length)
         then
            return False;
         end if;
         Lengths_From_Layout
           (Detail_Data, Slots, Details, Rows'Length);
         pragma Assert (Details'Length = Rows'Length);
         pragma Assert (Slots'Length = Rows'Length);
         Details_Checked_Zero (Data, Detail_Data, Rows, Details);
         for I in Rows'Range loop
            pragma Loop_Invariant (Completed = I - Rows'First);
            pragma Loop_Invariant (Details'Length = Rows'Length);
            pragma Loop_Invariant (Slots'Length = Rows'Length);
            pragma Loop_Invariant
              (Details_Checked (Data, Detail_Data, Rows, Details, Completed));
            declare
               Item : constant Quantity := Details
                 (Details'First + (I - Rows'First));
               Offset : constant Byte_Count := I - Rows'First;
            begin
               if not Span_Valid (Detail_Data, Item) or else
                 Value (Detail_Data, Item) /= Withheld_Reference (Data, Rows (I))
               then
                  return False;
               end if;
               pragma Assert (Completed = Offset);
               pragma Assert (Details'Length = Rows'Length);
               pragma Assert (Offset < Rows'Length);
               pragma Assert
                 (Details_Checked
                    (Data, Detail_Data, Rows, Details, Offset));
               Close_Detail_Step
                 (Data, Detail_Data, Rows, Details, Offset);
               Completed := Offset + 1;
               pragma Assert
                 (Details_Checked
                    (Data, Detail_Data, Rows, Details, Completed));
            end;
         end loop;
         pragma Assert (Completed = Rows'Length);
         Open_Details_Checked
           (Data, Detail_Data, Rows, Details, Completed);
         if not Output_Representation
           (Detail_Data, Total_Data, Slots, Details, Total)
         then
            return False;
         end if;
         --  Both original By operands remain checked. Non-short-circuit
         --  "and" evaluates both operands; neither is an assumed premise.
         pragma Assert_And_Cut
           ((Conforms_Success
                 (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total,
                  Status)
               and then Details'Length = Rows'Length
               and then Slots'Length = Rows'Length)
            and (Rows_Valid (Data, Rows)
               and then Layout_Valid
                 (Detail_Data, Slots, Details, Rows'Length)
               and then Storage_Sufficient
                 (Data, Rows, Slots, Total_Data'Length)
               and then Status = Computed
               and then Span_Valid (Total_Data, Total)
               and then Value (Total_Data, Total) =
                 Prefix_Total (Data, Rows, Rows'Length)
               and then Details'Length = Rows'Length
               and then Slots'Length = Rows'Length
               and then Details_Checked
                 (Data, Detail_Data, Rows, Details, Rows'Length)
               and then Output_Representation
                 (Detail_Data, Total_Data, Slots, Details, Total)));
         return True;
      end if;
      return Total = Empty and then
        (for all I in Details'Range => Details (I) = Empty) and then
        (for all I in Detail_Data'Range => Detail_Data (I) = 0) and then
        (for all I in Total_Data'Range => Total_Data (I) = 0);
   end Result_Conforms;

   function Magnitude_Order
     (Left_Data, Right_Data : Byte_Array; Left, Right : Quantity)
      return Ordering
   with Global => null,
     Pre => Span_Valid (Left_Data, Left) and then Span_Valid (Right_Data, Right),
     Post =>
       (if Magnitude (Left_Data, Left) < Magnitude (Right_Data, Right) then
          Magnitude_Order'Result = Less
        elsif Magnitude (Left_Data, Left) > Magnitude (Right_Data, Right) then
          Magnitude_Order'Result = Greater
        else Magnitude_Order'Result = Equal);

   function Magnitude_Order
     (Left_Data, Right_Data : Byte_Array; Left, Right : Quantity)
      return Ordering is
      Count : constant Byte_Count := Byte_Count'Max (Left.Length, Right.Length);
      Remaining : Byte_Count := Count with Ghost;
   begin
      Padded_Prefix (Left_Data, Left, Count);
      Padded_Prefix (Right_Data, Right, Count);
      if Count > 0 then
         for Offset in reverse 0 .. Count - 1 loop
            pragma Loop_Invariant (Remaining = Offset + 1);
            pragma Loop_Invariant
              (Magnitude (Left_Data, Left) - Magnitude (Right_Data, Right) =
                 Prefix_Reference (Left_Data, Left, Remaining) -
                   Prefix_Reference (Right_Data, Right, Remaining));
            pragma Loop_Invariant
              (Magnitude (Left_Data, Left) - Magnitude (Right_Data, Right) =
                 Prefix_Reference (Left_Data, Left, Offset + 1) -
                   Prefix_Reference (Right_Data, Right, Offset + 1));
            Bounded_Prefix (Left_Data, Left, Offset);
            Bounded_Prefix (Right_Data, Right, Offset);
            if Digit (Left_Data, Left, Offset) < Digit (Right_Data, Right, Offset) then
               Ordered_Magnitude_Columns
                 (Prefix_Reference (Left_Data, Left, Offset),
                  Prefix_Reference (Right_Data, Right, Offset),
                  Power_Reference (Offset), Digit (Left_Data, Left, Offset),
                  Digit (Right_Data, Right, Offset));
               pragma Assert
                 (Prefix_Reference (Left_Data, Left, Offset + 1) <
                    Prefix_Reference (Right_Data, Right, Offset + 1));
               pragma Assert
                 (Magnitude (Left_Data, Left) < Magnitude (Right_Data, Right));
               return Less;
            elsif Digit (Left_Data, Left, Offset) > Digit (Right_Data, Right, Offset) then
               Ordered_Magnitude_Columns
                 (Prefix_Reference (Left_Data, Left, Offset),
                  Prefix_Reference (Right_Data, Right, Offset),
                  Power_Reference (Offset), Digit (Left_Data, Left, Offset),
                  Digit (Right_Data, Right, Offset));
               pragma Assert
                 (Prefix_Reference (Left_Data, Left, Offset + 1) >
                    Prefix_Reference (Right_Data, Right, Offset + 1));
               pragma Assert
                 (Magnitude (Left_Data, Left) > Magnitude (Right_Data, Right));
               return Greater;
            end if;
            pragma Assert
              (Magnitude (Left_Data, Left) - Magnitude (Right_Data, Right) =
                 Prefix_Reference (Left_Data, Left, Offset) -
                   Prefix_Reference (Right_Data, Right, Offset));
            Remaining := Offset;
         end loop;
      end if;
      pragma Assert (Remaining = 0);
      pragma Assert (Magnitude (Left_Data, Left) = Magnitude (Right_Data, Right));
      return Equal;
   end Magnitude_Order;

   procedure Canonicalize
     (Data : Byte_Array; Negative : Boolean; Result : out Quantity)
   with Global => null, Always_Terminates,
     Post => Span_Valid (Data, Result) and then
       Magnitude (Data, Result) =
         Magnitude (Data, (False,
           (if Data'Length = 0 then 1 else Data'First), Data'Length)) and then
       Result.Negative = (Negative and then Magnitude (Data, Result) /= 0) and then
       Canonical_In_Slot
         (Data, ((if Data'Length = 0 then 1 else Data'First), Data'Length),
          Result);

   procedure Canonicalize
     (Data : Byte_Array; Negative : Boolean; Result : out Quantity) is
   begin
      Result := Empty;
      for I in reverse Data'Range loop
         --  The reverse scan has observed every higher byte to be zero.
         --  These are producer obligations over actual input bytes, not an
         --  assumed canonical result or a restricted caller premise.
         pragma Loop_Invariant (Result = Empty);
         pragma Loop_Invariant
           (for all J in Data'Range => (if J > I then Data (J) = 0));
         if Data (I) /= 0 then
            Result := (Negative, Data'First, I - Data'First + 1);
            Trimmed_Value (Data, Result);
            pragma Assert (Magnitude (Data, Result) > 0);
            pragma Assert
              (Canonical_In_Slot
                 (Data, ((if Data'Length = 0 then 1 else Data'First),
                         Data'Length), Result));
            return;
         end if;
      end loop;
      pragma Assert (for all J in Data'Range => Data (J) = 0);
      Trimmed_Value (Data, Result);
      pragma Assert
        (Canonical_In_Slot
           (Data, ((if Data'Length = 0 then 1 else Data'First), Data'Length),
            Result));
   end Canonicalize;

   function Binary_Reference
     (Left_Data, Right_Data : Byte_Array; Left, Right : Quantity;
      Negate_Right : Boolean) return Valid_Big_Integer is
     (Value (Left_Data, Left) +
       (if Negate_Right then -Value (Right_Data, Right)
        else Value (Right_Data, Right)))
   with Ghost, Global => null;

   procedure Binary_Signs
     (Left_Data, Right_Data : Byte_Array; Left, Right : Quantity;
      Negate_Right : Boolean; Order : Ordering)
   with Ghost, Global => null, Always_Terminates,
     Pre => Span_Valid (Left_Data, Left) and then Span_Valid (Right_Data, Right)
       and then
         (if Left.Negative /= (Right.Negative xor Negate_Right) then
            (if Magnitude (Left_Data, Left) < Magnitude (Right_Data, Right)
             then Order = Less
             elsif Magnitude (Left_Data, Left) > Magnitude (Right_Data, Right)
             then Order = Greater else Order = Equal)),
     Post =>
       (if Left.Negative = (Right.Negative xor Negate_Right) then
          abs Binary_Reference
            (Left_Data, Right_Data, Left, Right, Negate_Right) =
            Magnitude (Left_Data, Left) + Magnitude (Right_Data, Right)
        elsif Order = Less then
          abs Binary_Reference
            (Left_Data, Right_Data, Left, Right, Negate_Right) =
            Magnitude (Right_Data, Right) - Magnitude (Left_Data, Left)
        else
          abs Binary_Reference
            (Left_Data, Right_Data, Left, Right, Negate_Right) =
            Magnitude (Left_Data, Left) - Magnitude (Right_Data, Right))
       and then
       (if (if Left.Negative /= (Right.Negative xor Negate_Right)
               and then Order = Less
             then Right.Negative xor Negate_Right else Left.Negative)
        then Binary_Reference
          (Left_Data, Right_Data, Left, Right, Negate_Right) <= 0
        else Binary_Reference
          (Left_Data, Right_Data, Left, Right, Negate_Right) >= 0)
   is
      L : constant Valid_Big_Integer := Magnitude (Left_Data, Left);
      R : constant Valid_Big_Integer := Magnitude (Right_Data, Right);
      Signed : constant Valid_Big_Integer :=
        Binary_Reference (Left_Data, Right_Data, Left, Right, Negate_Right);
      Right_Negative : constant Boolean := Right.Negative xor Negate_Right;
   begin
      pragma Assert (L >= 0 and then R >= 0);
      if Left.Negative = Right_Negative then
         if Left.Negative then
            pragma Assert (Signed = -(L + R));
         else
            pragma Assert (Signed = L + R);
         end if;
         pragma Assert (abs Signed = L + R);
      elsif Order = Less then
         pragma Assert (R > L);
         if Right_Negative then
            pragma Assert (Signed = -(R - L));
         else
            pragma Assert (Signed = R - L);
         end if;
         pragma Assert (abs Signed = R - L);
      else
         pragma Assert (L >= R);
         if Left.Negative then
            pragma Assert (Signed = -(L - R));
         else
            pragma Assert (Signed = L - R);
         end if;
         pragma Assert (abs Signed = L - R);
      end if;
   end Binary_Signs;

   procedure Binary
     (Left_Data, Right_Data : Byte_Array; Left, Right : Quantity;
      Negate_Right : Boolean; Output : out Byte_Array;
      Result : out Quantity; Success : out Boolean)
   with Global => null, Always_Terminates,
     Pre => Span_Valid (Left_Data, Left) and then Span_Valid (Right_Data, Right),
     Post => Success =
       (abs Binary_Reference (Left_Data, Right_Data, Left, Right, Negate_Right)
          < Radix_Power (Output'Length)) and then
       (if Success then Span_Valid (Output, Result) and then
          Value (Output, Result) = Binary_Reference
            (Left_Data, Right_Data, Left, Right, Negate_Right) and then
          Canonical_In_Slot
            (Output, ((if Output'Length = 0 then 1 else Output'First),
                      Output'Length), Result)
        else Result = Empty and then (for all I in Output'Range => Output (I) = 0));

   --  The stored octet is the Digit of the whole arena at that offset.
   procedure Written_Digit
     (Data : Byte_Array; Offset : Byte_Count; Octet : Natural)
   with Ghost, Global => null, Always_Terminates,
     Pre => Offset < Data'Length and then Octet <= 255
       and then Data (Data'First + Offset) = Byte (Octet),
     Post => Digit (Data, Whole (Data), Offset) = Octet
   is
   begin
      pragma Assert (Data'Length > 0);
      pragma Assert (Span_Valid (Data, Whole (Data)));
      pragma Assert (Whole (Data).First = Data'First);
      pragma Assert (Offset < Whole (Data).Length);
      pragma Assert
        (Digit (Data, Whole (Data), Offset) =
           Natural (Data (Data'First + Offset)));
      pragma Assert (Natural (Byte (Octet)) = Octet);
      pragma Assert (Digit (Data, Whole (Data), Offset) = Octet);
   end Written_Digit;

   --  Offsets past the arena are Digit zero, including a zero column that
   --  was not stored because the output has no such byte.
   procedure Absent_Digit
     (Data : Byte_Array; Offset : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Offset >= Data'Length,
     Post => Digit (Data, Whole (Data), Offset) = 0
   is
   begin
      pragma Assert (Offset >= Whole (Data).Length);
      pragma Assert (Digit (Data, Whole (Data), Offset) = 0);
   end Absent_Digit;

   procedure Produced_Step
     (Before, After : Byte_Array; Offset : Byte_Count; Octet : Natural;
      Prior, Produced : Valid_Big_Integer)
   with Ghost, Global => null, Always_Terminates,
     Pre => Offset < Byte_Count'Last
       and then Produced =
         Prior + To_Big_Integer (Octet) * Power_Reference (Offset)
       and then Prior = Prefix_Reference (Before, Whole (Before), Offset)
       and then (if Offset > 0 then
                   (for all K in 0 .. Offset - 1 =>
                      Digit (Before, Whole (Before), K) =
                        Digit (After, Whole (After), K)))
       and then Digit (After, Whole (After), Offset) = Octet,
     Post => Produced =
       Prefix_Reference (After, Whole (After), Offset + 1)
   is
   begin
      Written_Prefix_Step (Before, After, Offset, Octet);
      pragma Assert
        (Prefix_Reference (After, Whole (After), Offset + 1) =
           Prefix_Reference (Before, Whole (Before), Offset) +
             To_Big_Integer (Octet) * Power_Reference (Offset));
      pragma Assert
        (Produced = Prefix_Reference (After, Whole (After), Offset + 1));
   end Produced_Step;

   procedure Binary
     (Left_Data, Right_Data : Byte_Array; Left, Right : Quantity;
      Negate_Right : Boolean; Output : out Byte_Array;
      Result : out Quantity; Success : out Boolean)
   is
      Count : constant Byte_Count := Byte_Count'Max (Left.Length, Right.Length);
      Right_Negative : constant Boolean := Right.Negative xor Negate_Right;
      Add_Magnitudes : constant Boolean := Left.Negative = Right_Negative;
      Order : Ordering := Equal;
      Negative : Boolean := Left.Negative;
      Carry : Natural range 0 .. 1 := 0;
      Credit, Debit, Column, Octet : Natural := 0;
      Produced : Valid_Big_Integer := To_Big_Integer (0) with Ghost;
      Before_Output : Byte_Array (Output'Range) with Ghost;
      Prior_Produced : Valid_Big_Integer := To_Big_Integer (0) with Ghost;
      Prior_Carry : Natural range 0 .. 1 := 0 with Ghost;
      Completed : Byte_Count := 0 with Ghost;
      --  Inputs are immutable for this call. Reuse the exact mathematical
      --  reference in checked proof checks instead of reconstructing the
      --  same large values at every column.
      Expected : constant Valid_Big_Integer :=
        Binary_Reference
          (Left_Data, Right_Data, Left, Right, Negate_Right) with Ghost;
   begin
      Output := (others => 0);
      Result := Empty;
      Success := False;
      Padded_Prefix (Left_Data, Left, Count);
      Padded_Prefix (Right_Data, Right, Count);
      if not Add_Magnitudes then
         Order := Magnitude_Order (Left_Data, Right_Data, Left, Right);
         Binary_Signs (Left_Data, Right_Data, Left, Right, Negate_Right, Order);
         if Order = Equal then
            pragma Assert
              (Canonical_In_Slot
                 (Output, ((if Output'Length = 0 then 1 else Output'First),
                           Output'Length), Result));
            Success := True;
            return;
         elsif Order = Less then
            Negative := Right_Negative;
         end if;
      end if;
      Binary_Signs (Left_Data, Right_Data, Left, Right, Negate_Right, Order);
      if Count > 0 then
         for Offset in 0 .. Count - 1 loop
            pragma Loop_Invariant (Completed = Offset);
            pragma Loop_Invariant
              (Produced = Prefix_Reference (Output, Whole (Output), Completed));
            pragma Loop_Invariant (Carry <= 1);
            pragma Loop_Invariant (Produced >= 0);
            pragma Loop_Invariant (Produced < Power_Reference (Offset));
            pragma Loop_Invariant
              (Produced = Prefix_Reference (Output, Whole (Output), Offset));
            pragma Loop_Invariant
              (if Add_Magnitudes then
                 Prefix_Reference (Left_Data, Left, Offset) +
                   Prefix_Reference (Right_Data, Right, Offset) = Produced +
                     To_Big_Integer (Carry) * Power_Reference (Offset)
               elsif Order = Less then
                 Prefix_Reference (Right_Data, Right, Offset) -
                   Prefix_Reference (Left_Data, Left, Offset) = Produced -
                     To_Big_Integer (Carry) * Power_Reference (Offset)
               else
                 Prefix_Reference (Left_Data, Left, Offset) -
                   Prefix_Reference (Right_Data, Right, Offset) = Produced -
                     To_Big_Integer (Carry) * Power_Reference (Offset));
            pragma Loop_Invariant
              (abs Expected
                   mod Power_Reference (Offset) = Produced);
            pragma Loop_Invariant
              (for all I in Output'Range =>
                 (if I - Output'First >= Offset then Output (I) = 0));
            Prior_Produced := Produced;
            Prior_Carry := Carry;
            Before_Output := Output;
            if Add_Magnitudes then
               Column := Digit (Left_Data, Left, Offset) +
                 Digit (Right_Data, Right, Offset) + Carry;
               Octet := Column mod 256;
               Carry := Column / 256;
            else
               if Order = Less then
                  Credit := Digit (Right_Data, Right, Offset);
                  Debit := Digit (Left_Data, Left, Offset) + Carry;
               else
                  Credit := Digit (Left_Data, Left, Offset);
                  Debit := Digit (Right_Data, Right, Offset) + Carry;
               end if;
               if Credit >= Debit then
                  Octet := Credit - Debit;
                  Carry := 0;
               else
                  Octet := Credit + 256 - Debit;
                  Carry := 1;
               end if;
            end if;
            if Add_Magnitudes or else Order /= Less then
               Advance_Column
                 (Prefix_Reference (Left_Data, Left, Offset),
                  Prefix_Reference (Right_Data, Right, Offset),
                  Prior_Produced, Power_Reference (Offset),
                  Digit (Left_Data, Left, Offset),
                  Digit (Right_Data, Right, Offset),
                  Prior_Carry, Carry, Octet, Add_Magnitudes);
            else
               Advance_Column
                 (Prefix_Reference (Right_Data, Right, Offset),
                  Prefix_Reference (Left_Data, Left, Offset),
                  Prior_Produced, Power_Reference (Offset),
                  Digit (Right_Data, Right, Offset),
                  Digit (Left_Data, Left, Offset),
                  Prior_Carry, Carry, Octet, False);
            end if;
            Produced := Produced +
              To_Big_Integer (Octet) * Power_Reference (Offset);
            Magnitude_Remainder (Left_Data, Left, Offset + 1);
            Magnitude_Remainder (Right_Data, Right, Offset + 1);
            if Add_Magnitudes or else Order /= Less then
               Combined_Remainder
                 (Magnitude (Left_Data, Left), Magnitude (Right_Data, Right),
                  Prefix_Reference (Left_Data, Left, Offset + 1),
                  Prefix_Reference (Right_Data, Right, Offset + 1),
                  Produced, Power_Reference (Offset + 1), Carry, Add_Magnitudes);
            else
               Combined_Remainder
                 (Magnitude (Right_Data, Right), Magnitude (Left_Data, Left),
                  Prefix_Reference (Right_Data, Right, Offset + 1),
                  Prefix_Reference (Left_Data, Left, Offset + 1),
                  Produced, Power_Reference (Offset + 1), Carry, False);
            end if;
            pragma Assert (Produced >= 0);
            pragma Assert (Produced < Power_Reference (Offset + 1));
            pragma Assert
              (abs Expected
                   mod Power_Reference (Offset + 1) = Produced);
            if Offset < Output'Length then
               Output (Output'First + Offset) := Byte (Octet);
               Written_Digit (Output, Offset, Octet);
               Equal_Prefix (Before_Output, Output,
                             Whole (Before_Output), Whole (Output), Offset);
            elsif Octet /= 0 then
               Power_Monotone (Output'Length, Offset);
               declare
                  Contribution : constant Valid_Big_Integer :=
                    Column_Product (Octet, Power_Reference (Offset)) with Ghost;
               begin
                  pragma Assert (Contribution >= Power_Reference (Offset));
                  pragma Assert (Produced = Prior_Produced + Contribution);
               end;
               pragma Assert
                 (abs Expected >=
                      Radix_Power (Output'Length));
               Output := (others => 0);
               return;
            else
               Absent_Digit (Output, Offset);
            end if;
            Produced_Step
              (Before_Output, Output, Offset, Octet, Prior_Produced, Produced);
            Completed := Offset + 1;
         end loop;
      end if;
      pragma Assert (Completed = Count);
      pragma Assert
        (if Add_Magnitudes then
           abs Expected =
               Produced + To_Big_Integer (Carry) * Power_Reference (Count)
         else
           abs Expected =
               Produced - To_Big_Integer (Carry) * Power_Reference (Count));
      if not Add_Magnitudes then
         pragma Assert (Carry = 0);
      end if;
      pragma Assert
        (for all I in Output'Range =>
           (if I - Output'First >= Count then Output (I) = 0));
      if Add_Magnitudes and then Carry /= 0 then
         if Count < Output'Length then
            Prior_Produced := Produced;
            Before_Output := Output;
            Output (Output'First + Count) := Byte (Carry);
            Written_Digit (Output, Count, Carry);
            Equal_Prefix (Before_Output, Output,
                          Whole (Before_Output), Whole (Output), Count);
            Produced :=
              Prior_Produced + To_Big_Integer (Carry) * Power_Reference (Count);
            Produced_Step
              (Before_Output, Output, Count, Carry, Prior_Produced, Produced);
            Completed := Count + 1;
            pragma Assert
              (Produced = Prefix_Reference (Output, Whole (Output), Completed));
         else
            Power_Monotone (Output'Length, Count);
            pragma Assert
              (abs Expected >=
                   Radix_Power (Output'Length));
            Output := (others => 0);
            return;
         end if;
      end if;
      Output_Prefix_Value (Output, Completed);
      Bounded_Prefix (Output, Whole (Output), Output'Length);
      Padded_Prefix (Output, Whole (Output), Output'Length);
      pragma Assert
        (Magnitude (Output, Whole (Output)) =
           abs Expected);
      pragma Assert
        (abs Expected <
             Radix_Power (Output'Length));
      Canonicalize (Output, Negative, Result);
      pragma Assert
        (Canonical_In_Slot
           (Output, ((if Output'Length = 0 then 1 else Output'First),
                     Output'Length), Result));
      Success := True;
   end Binary;

   procedure Compute_Row
     (Data : Byte_Array; Row : Reservation_Row; Output : out Byte_Array;
      Result : out Quantity; Success : out Boolean)
   with Global => null, Always_Terminates,
     Pre => Span_Valid (Data, Row.Reserved) and then
       (not Row.Used.Present or else Span_Valid (Data, Row.Used.Value)),
     Post => Success =
       (abs Withheld_Reference (Data, Row) < Radix_Power (Output'Length)) and then
       (if Success then Span_Valid (Output, Result) and then
          Value (Output, Result) = Withheld_Reference (Data, Row) and then
          Canonical_In_Slot
            (Output, ((if Output'Length = 0 then 1 else Output'First),
                      Output'Length), Result)
        else Result = Empty and then (for all I in Output'Range => Output (I) = 0));

   procedure Compute_Row
     (Data : Byte_Array; Row : Reservation_Row; Output : out Byte_Array;
      Result : out Quantity; Success : out Boolean) is
   begin
      if not Row.Used.Present then
         pragma Assert
           (Withheld_Reference (Data, Row) = Value (Data, Row.Reserved));
         Binary (Data, Data, Row.Reserved, Empty, False, Output, Result, Success);
      elsif Compare (Data, Row.Reserved, Row.Used.Value) in Less | Equal then
         pragma Assert (Withheld_Reference (Data, Row) = 0);
         Output := (others => 0);
         Result := Empty;
         Success := True;
         pragma Assert
           (Canonical_In_Slot
              (Output, ((if Output'Length = 0 then 1 else Output'First),
                        Output'Length), Result));
      else
         pragma Assert
           (Withheld_Reference (Data, Row) =
              Value (Data, Row.Reserved) - Value (Data, Row.Used.Value));
         Binary (Data, Data, Row.Reserved, Row.Used.Value, True,
                 Output, Result, Success);
      end if;
   end Compute_Row;


   function Processed_Conforms
     (Data : Byte_Array; Rows : Reservation_Array; Slots : Span_Array;
      Detail_Data, Total_Data : Byte_Array; Details : Quantity_Array;
      Total : Quantity; Processed : Byte_Count) return Boolean is
     (Processed <= Rows'Length and then Rows_Valid (Data, Rows) and then
      Layout_Valid (Detail_Data, Slots, Details, Rows'Length) and then
      Canonical_In_Slot (Total_Data,
        ((if Total_Data'Length = 0 then 1 else Total_Data'First),
         Total_Data'Length), Total) and then
      Value (Total_Data, Total) = Prefix_Total (Data, Rows, Processed) and then
      (for all I in Rows'Range =>
         (if I - Rows'First < Processed then
            Canonical_In_Slot
              (Detail_Data, Slots (Slots'First + (I - Rows'First)),
               Details (Details'First + (I - Rows'First))) and then
            Value (Detail_Data, Details (Details'First + (I - Rows'First))) =
              Withheld_Reference (Data, Rows (I)) and then
            abs Withheld_Reference (Data, Rows (I)) <
              Radix_Power (Slots (Slots'First + (I - Rows'First)).Length) and then
            abs Prefix_Total (Data, Rows, (I - Rows'First) + 1) <
              Radix_Power (Total_Data'Length)
          else Details (Details'First + (I - Rows'First)) = Empty)) and then
      (for all I in Detail_Data'Range =>
         (if not (for some S in Slots'Range =>
            S - Slots'First < Processed and then Contains (Slots (S), I))
          then Detail_Data (I) = 0)))
   with Ghost, Global => null;

   procedure Canonical_At_Ordinal
     (Detail_Data : Byte_Array; Rows : Reservation_Array;
      Slots : Span_Array; Details : Quantity_Array; Ordinal : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Ordinal < Rows'Length
       and then Slots'Length = Rows'Length
       and then Details'Length = Rows'Length
       and then
         (for all I in Rows'Range =>
            Canonical_In_Slot
              (Detail_Data, Slots (Slots'First + (I - Rows'First)),
               Details (Details'First + (I - Rows'First)))),
     Post => Canonical_In_Slot
       (Detail_Data, Slots (Slots'First + Ordinal),
        Details (Details'First + Ordinal))
   is
   begin
      pragma Assert ((Rows'First + Ordinal) in Rows'Range);
      pragma Assert
        (Canonical_In_Slot
           (Detail_Data, Slots (Slots'First + Ordinal),
            Details (Details'First + Ordinal)));
   end Canonical_At_Ordinal;

   --  Success correspondence lives here so the final Post does not reopen
   --  Compute's whole proof context. The public Post is unchanged.
   procedure Finish_Computed
     (Data : Byte_Array; Rows : Reservation_Array; Slots : Span_Array;
      Detail_Data, Total_Data : Byte_Array; Details : Quantity_Array;
      Total : Quantity)
   with Ghost, Global => null, Always_Terminates,
     Pre => Processed_Conforms
       (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total,
        Rows'Length),
     Post => Result_Conforms
       (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total, Computed)
   is
      Seen : Byte_Count := 0 with Ghost;
   begin
      pragma Assert (Rows_Valid (Data, Rows));
      pragma Assert
        (Layout_Valid (Detail_Data, Slots, Details, Rows'Length));
      pragma Assert (Span_Valid (Total_Data, Total));
      pragma Assert
        (Value (Total_Data, Total) =
           Prefix_Total (Data, Rows, Rows'Length));
      pragma Assert
        (Canonical_In_Slot
           (Total_Data,
            ((if Total_Data'Length = 0 then 1 else Total_Data'First),
             Total_Data'Length), Total));
      for I in Rows'Range loop
         pragma Loop_Invariant (Seen = I - Rows'First);
         pragma Loop_Invariant
           (for all J in Rows'Range =>
              (if J - Rows'First < Seen then
                 Canonical_In_Slot
                   (Detail_Data, Slots (Slots'First + (J - Rows'First)),
                    Details (Details'First + (J - Rows'First)))
                 and then Span_Valid
                   (Detail_Data,
                    Details (Details'First + (J - Rows'First)))
                 and then Value
                   (Detail_Data,
                    Details (Details'First + (J - Rows'First))) =
                     Withheld_Reference (Data, Rows (J))
                 and then abs Withheld_Reference (Data, Rows (J)) <
                   Radix_Power
                     (Slots (Slots'First + (J - Rows'First)).Length)
                 and then abs Prefix_Total
                   (Data, Rows, (J - Rows'First) + 1) <
                     Radix_Power (Total_Data'Length)));
         pragma Assert (I - Rows'First < Rows'Length);
         pragma Assert
           (Canonical_In_Slot
              (Detail_Data, Slots (Slots'First + (I - Rows'First)),
               Details (Details'First + (I - Rows'First))));
         pragma Assert
           (Span_Valid
              (Detail_Data, Details (Details'First + (I - Rows'First))));
         pragma Assert
           (Value
              (Detail_Data, Details (Details'First + (I - Rows'First))) =
              Withheld_Reference (Data, Rows (I)));
         pragma Assert
           (abs Withheld_Reference (Data, Rows (I)) <
              Radix_Power (Slots (Slots'First + (I - Rows'First)).Length));
         pragma Assert
           (abs Prefix_Total (Data, Rows, (I - Rows'First) + 1) <
              Radix_Power (Total_Data'Length));
         Seen := (I - Rows'First) + 1;
      end loop;
      pragma Assert (Seen = Rows'Length);
      pragma Assert
        (for all I in Rows'Range =>
           Span_Valid
             (Detail_Data, Details (Details'First + (I - Rows'First)))
           and then Value
             (Detail_Data, Details (Details'First + (I - Rows'First))) =
               Withheld_Reference (Data, Rows (I))
           and then abs Withheld_Reference (Data, Rows (I)) <
             Radix_Power (Slots (Slots'First + (I - Rows'First)).Length)
           and then abs Prefix_Total (Data, Rows, (I - Rows'First) + 1) <
             Radix_Power (Total_Data'Length));
      pragma Assert
        (Storage_Sufficient (Data, Rows, Slots, Total_Data'Length));
      pragma Assert
        (for all I in Detail_Data'Range =>
           (if not (for some S in Slots'Range => Contains (Slots (S), I)) then
              Detail_Data (I) = 0));
      pragma Assert (Slots'Length = Rows'Length);
      pragma Assert (Details'Length = Rows'Length);
      pragma Assert
        (for all I in Rows'Range =>
           Canonical_In_Slot
             (Detail_Data, Slots (Slots'First + (I - Rows'First)),
              Details (Details'First + (I - Rows'First))));
      for S in Slots'Range loop
         pragma Loop_Invariant
           (for all T in Slots'Range =>
              (if T < S then
                 Canonical_In_Slot
                   (Detail_Data, Slots (T),
                    Details (Details'First + (T - Slots'First)))));
         declare
            Ordinal : constant Byte_Count := S - Slots'First;
         begin
            pragma Assert (Ordinal < Rows'Length);
            pragma Assert (S = Slots'First + Ordinal);
            Canonical_At_Ordinal
              (Detail_Data, Rows, Slots, Details, Ordinal);
            pragma Assert
              (Canonical_In_Slot
                 (Detail_Data, Slots (S),
                  Details (Details'First + (S - Slots'First))));
         end;
      end loop;
      pragma Assert
        (for all S in Slots'Range =>
           Canonical_In_Slot
             (Detail_Data, Slots (S),
              Details (Details'First + (S - Slots'First))));
      pragma Assert
        (Output_Representation
           (Detail_Data, Total_Data, Slots, Details, Total));
      pragma Assert
        (Result_Conforms
           (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total,
            Computed));
   end Finish_Computed;

   procedure Computed_Status
     (Data : Byte_Array; Rows : Reservation_Array; Slots : Span_Array;
      Detail_Data, Total_Data : Byte_Array; Details : Quantity_Array;
      Total : Quantity; Status : Result_Status)
   with Ghost, Global => null, Always_Terminates,
     Pre => Status = Computed
       and then Result_Conforms
         (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total,
          Computed),
     Post => Result_Conforms
       (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total, Status)
   is
   begin
      pragma Assert (Status = Computed);
      pragma Assert
        (Result_Conforms
           (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total,
            Status));
   end Computed_Status;

   --  The row loop stays here so Compute's post is a call, not this path.
   --  Success stops at Processed_Conforms. Finish_Computed is Compute's step.
   procedure Produce
     (Data : Byte_Array; Rows : Reservation_Array; Slots : Span_Array;
      Detail_Data, Total_Data : out Byte_Array;
      Details : out Quantity_Array; Total : out Quantity;
      Status : out Result_Status)
   with Global => null, Always_Terminates,
     Post =>
       (if Status = Computed then
          Processed_Conforms
            (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total,
             Rows'Length)
        else
          Result_Conforms
            (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total,
             Status))
   is
      Before_Detail_Data : Byte_Array (Detail_Data'Range) with Ghost;
      Workspace : Byte_Array (Total_Data'Range);
      Item, New_Total : Quantity := Empty;
      Success : Boolean := False;
   begin
      Detail_Data := (others => 0);
      Total_Data := (others => 0);
      Details := (others => Empty);
      Total := Empty;
      Status := Invalid_Input;
      if not Rows_Valid (Data, Rows) then
         return;
      end if;
      Status := Invalid_Output_Layout;
      if not Layout_Valid (Detail_Data, Slots, Details, Rows'Length) then
         return;
      end if;
      Status := Insufficient_Storage;
      for I in Rows'Range loop
         pragma Loop_Invariant (Status = Insufficient_Storage);
         pragma Loop_Invariant
           (Processed_Conforms
              (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total,
               I - Rows'First));
         pragma Loop_Invariant (Span_Valid (Total_Data, Total));
         declare
            Offset : constant Byte_Count := I - Rows'First;
            Slot : constant Output_Span := Slots (Slots'First + Offset);
            Last : constant Byte_Count :=
              (if Slot.Length = 0 then Slot.First - 1
               else Slot.First + (Slot.Length - 1));
         begin
            Before_Detail_Data := Detail_Data;
            Compute_Row (Data, Rows (I), Detail_Data (Slot.First .. Last),
                         Item, Success);
            if not Success then
               pragma Assert
                 (abs Withheld_Reference (Data, Rows (I)) >=
                    Radix_Power (Slot.Length));
               Detail_Data := (others => 0);
               Total_Data := (others => 0);
               Details := (others => Empty);
               Total := Empty;
               return;
            end if;
            pragma Assert
              (for all K in Detail_Data'Range =>
                 (if not Contains (Slot, K) then
                    Before_Detail_Data (K) = Detail_Data (K)));
            Retained_Detail_Frame
              (Before_Detail_Data, Detail_Data, Rows, Slots, Details, Offset);
            Lift_Slice (Detail_Data, Slot, Item);
            pragma Assert (Span_Valid (Total_Data, Total));
            pragma Assert (Span_Valid (Detail_Data, Item));
            pragma Assert
              (Prefix_Total (Data, Rows, Offset + 1) =
                 Prefix_Total (Data, Rows, Offset) +
                   Withheld_Reference (Data, Rows (I)));
            pragma Assert
              (Value (Detail_Data, Item) = Withheld_Reference (Data, Rows (I)));
            Binary (Total_Data, Detail_Data, Total, Item, False,
                    Workspace, New_Total, Success);
            if not Success then
               pragma Assert
                 (abs Prefix_Total (Data, Rows, Offset + 1) >=
                    Radix_Power (Total_Data'Length));
               Detail_Data := (others => 0);
               Total_Data := (others => 0);
               Details := (others => Empty);
               Total := Empty;
               return;
            end if;
            Details (Details'First + Offset) := Item;
            Total_Data := Workspace;
            Total := New_Total;
            pragma Assert
              (Details (Details'First + Offset) = Item);
            pragma Assert
              (Value (Detail_Data, Details (Details'First + Offset)) =
                 Withheld_Reference (Data, Rows (I)));
            Checked_Detail_Step (Data, Detail_Data, Rows, Details, Offset);
            pragma Assert
              (Processed_Conforms
                 (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total,
                  Offset + 1));
         end;
      end loop;
      pragma Assert
        (Processed_Conforms
           (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total,
            Rows'Length));
      Status := Computed;
      pragma Assert (Status = Computed);
      pragma Assert
        (Processed_Conforms
           (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total,
            Rows'Length));
   end Produce;

   procedure Compute
     (Data : Byte_Array; Rows : Reservation_Array; Slots : Span_Array;
      Detail_Data, Total_Data : out Byte_Array;
      Details : out Quantity_Array; Total : out Quantity;
      Status : out Result_Status)
   is
   begin
      Produce
        (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total, Status);
      if Status = Computed then
         Finish_Computed
           (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total);
         Computed_Status
           (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total,
            Status);
      end if;
   end Compute;
   procedure Compute_Headroom
     (Data : Byte_Array; Available, Withheld, Floor : Quantity;
      Output : out Byte_Array; Result : out Quantity;
      Status : out Result_Status)
   is
      Workspace : Byte_Array (Output'Range);
      Intermediate : Quantity := Empty;
      Success : Boolean := False;
   begin
      Output := (others => 0);
      Result := Empty;
      Status := Invalid_Input;
      if not Headroom_Input_Valid (Data, Available, Withheld, Floor) then
         return;
      end if;
      Status := Insufficient_Storage;
      Binary (Data, Data, Available, Withheld, True,
              Workspace, Intermediate, Success);
      if not Success then
         return;
      end if;
      Binary (Workspace, Data, Intermediate, Floor, True,
              Output, Result, Success);
      if Success then
         Status := Computed;
      end if;
   end Compute_Headroom;

end Resource_Ledger;
