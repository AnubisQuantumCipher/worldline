package body Resource_Ledger with SPARK_Mode is
   use type Byte;

   --  Closed arithmetic/frame bridges. Every body, recursive call, range,
   --  predicate, assertion and termination check is an actual obligation.
   --  These checked Ghost operations are not claimed to have zero native cost.
   function Whole (Data : Byte_Array) return Quantity is
     ((False, (if Data'Length = 0 then 1 else Data'First), Data'Length))
   with Ghost, Global => null;

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
            pragma Assert
              (Previous + Current * Place < To_Big_Integer (256) * Place);
         end;
      end if;
   end Bounded_Prefix;

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

   function Prefix_Total
     (Data : Byte_Array; Rows : Reservation_Array; Count : Byte_Count)
      return Valid_Big_Integer is
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
   end Prefix_Total;

   function Storage_Sufficient
     (Data : Byte_Array; Rows : Reservation_Array; Slots : Span_Array;
      Total_Capacity : Byte_Count) return Boolean is
   begin
      if Slots'Length /= Rows'Length then
         return False;
      end if;
      for I in Rows'Range loop
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

   function Result_Conforms
     (Data : Byte_Array; Rows : Reservation_Array; Slots : Span_Array;
      Detail_Data, Total_Data : Byte_Array; Details : Quantity_Array;
      Total : Quantity; Status : Result_Status) return Boolean is
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
         for I in Rows'Range loop
            declare
               Item : constant Quantity := Details
                 (Details'First + (I - Rows'First));
            begin
               if not Span_Valid (Detail_Data, Item) or else
                 Value (Detail_Data, Item) /= Withheld_Reference (Data, Rows (I))
               then
                  return False;
               end if;
            end;
         end loop;
         if not Output_Representation
           (Detail_Data, Total_Data, Slots, Details, Total)
         then
            return False;
         end if;
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
   begin
      Padded_Prefix (Left_Data, Left, Count);
      Padded_Prefix (Right_Data, Right, Count);
      if Count > 0 then
         for Offset in reverse 0 .. Count - 1 loop
            pragma Loop_Invariant
              (Magnitude (Left_Data, Left) - Magnitude (Right_Data, Right) =
                 Prefix_Reference (Left_Data, Left, Offset + 1) -
                   Prefix_Reference (Right_Data, Right, Offset + 1));
            Bounded_Prefix (Left_Data, Left, Offset);
            Bounded_Prefix (Right_Data, Right, Offset);
            if Digit (Left_Data, Left, Offset) < Digit (Right_Data, Right, Offset) then
               return Less;
            elsif Digit (Left_Data, Left, Offset) > Digit (Right_Data, Right, Offset) then
               return Greater;
            end if;
            pragma Assert
              (Magnitude (Left_Data, Left) - Magnitude (Right_Data, Right) =
                 Prefix_Reference (Left_Data, Left, Offset) -
                   Prefix_Reference (Right_Data, Right, Offset));
         end loop;
      end if;
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
   begin
      Output := (others => 0);
      Result := Empty;
      Success := False;
      Padded_Prefix (Left_Data, Left, Count);
      Padded_Prefix (Right_Data, Right, Count);
      if not Add_Magnitudes then
         Order := Magnitude_Order (Left_Data, Right_Data, Left, Right);
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
      if Count > 0 then
         for Offset in 0 .. Count - 1 loop
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
              (abs Binary_Reference
                 (Left_Data, Right_Data, Left, Right, Negate_Right)
                   mod Power_Reference (Offset) = Produced);
            pragma Loop_Invariant
              (for all I in Output'Range =>
                 (if I - Output'First >= Offset then Output (I) = 0));
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
            Produced := Produced +
              To_Big_Integer (Octet) * Power_Reference (Offset);
            pragma Assert (Produced >= 0);
            pragma Assert (Produced < Power_Reference (Offset + 1));
            pragma Assert
              (abs Binary_Reference
                 (Left_Data, Right_Data, Left, Right, Negate_Right)
                   mod Power_Reference (Offset + 1) = Produced);
            if Offset < Output'Length then
               Output (Output'First + Offset) := Byte (Octet);
               Equal_Prefix (Before_Output, Output,
                             Whole (Before_Output), Whole (Output), Offset);
            elsif Octet /= 0 then
               pragma Assert
                 (abs Binary_Reference
                    (Left_Data, Right_Data, Left, Right, Negate_Right) >=
                      Radix_Power (Output'Length));
               Output := (others => 0);
               return;
            end if;
            pragma Assert
              (Produced = Prefix_Reference
                 (Output, Whole (Output), Offset + 1));
         end loop;
      end if;
      pragma Assert
        (for all I in Output'Range =>
           (if I - Output'First >= Count then Output (I) = 0));
      if Add_Magnitudes and then Carry /= 0 then
         if Count < Output'Length then
            Output (Output'First + Count) := Byte (Carry);
         else
            Output := (others => 0);
            return;
         end if;
      end if;
      pragma Assert
        (Magnitude (Output, Whole (Output)) =
           abs Binary_Reference
             (Left_Data, Right_Data, Left, Right, Negate_Right));
      pragma Assert
        (abs Binary_Reference
           (Left_Data, Right_Data, Left, Right, Negate_Right) <
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

   procedure Compute
     (Data : Byte_Array; Rows : Reservation_Array; Slots : Span_Array;
      Detail_Data, Total_Data : out Byte_Array;
      Details : out Quantity_Array; Total : out Quantity;
      Status : out Result_Status)
   is
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
            Lift_Slice (Detail_Data, Slot, Item);
            pragma Assert (Span_Valid (Total_Data, Total));
            pragma Assert (Span_Valid (Detail_Data, Item));
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
