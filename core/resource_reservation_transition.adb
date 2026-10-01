package body Resource_Reservation_Transition with SPARK_Mode is
   --  Additive proof computations. Every body, recursive call, caller Pre,
   --  assertion and Post remains a required full-scope proof obligation.
   --  The checked profile executes Ghost code: no zero-cost/native claim.
   Zero_Quantity : constant Quantity :=
     (Negative => False, First => Byte_Index'First, Length => 0) with Ghost;

   procedure Prefix_Step
     (Data : Byte_Array; Q : Quantity; Offset : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Offset < Byte_Count'Last,
     Post =>
       Prefix_Value (Data, Q, Offset + 1) = Prefix_Value (Data, Q, Offset)
         + To_Big_Integer (Digit (Data, Q, Offset)) * Radix_Power (Offset)
       and then Radix_Power (Offset + 1) =
         To_Big_Integer (256) * Radix_Power (Offset)
   is
   begin
      pragma Assert
        (Prefix_Reference (Data, Q, Offset + 1) =
           Prefix_Reference (Data, Q, Offset)
             + To_Big_Integer (Digit (Data, Q, Offset))
               * Power_Reference (Offset));
      pragma Assert
        (Power_Reference (Offset + 1) =
           To_Big_Integer (256) * Power_Reference (Offset));
      pragma Assert
        (Prefix_Value (Data, Q, Offset) =
           Prefix_Reference (Data, Q, Offset));
      pragma Assert
        (Prefix_Value (Data, Q, Offset + 1) =
           Prefix_Reference (Data, Q, Offset + 1));
   end Prefix_Step;

   procedure Prefix_Padding
     (Data : Byte_Array; Q : Quantity; Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Span_Valid (Data, Q) and then Q.Length <= Count,
     Subprogram_Variant => (Decreases => Count),
     Post => Prefix_Value (Data, Q, Count) = Magnitude (Data, Q);

   procedure Prefix_Padding
     (Data : Byte_Array; Q : Quantity; Count : Byte_Count) is
   begin
      if Q.Length < Count then
         Prefix_Padding (Data, Q, Count - 1);
         pragma Assert (Digit (Data, Q, Count - 1) = 0);
         pragma Assert
           (Prefix_Reference (Data, Q, Count) =
              Prefix_Reference (Data, Q, Count - 1));
      else
         pragma Assert
           (Magnitude (Data, Q) = Prefix_Value (Data, Q, Q.Length));
      end if;
   end Prefix_Padding;

   procedure Power_Factor (First, Stop : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => First <= Stop,
     Subprogram_Variant => (Decreases => Stop),
     Post => Power_Reference (Stop) =
       Power_Reference (First) * Power_Reference (Stop - First);

   procedure Power_Factor (First, Stop : Byte_Count) is
   begin
      if First < Stop then
         Power_Factor (First, Stop - 1);
         pragma Assert
           (Power_Reference (Stop) =
              To_Big_Integer (256) * Power_Reference (Stop - 1));
         pragma Assert
           (Power_Reference (Stop - First) =
              To_Big_Integer (256) * Power_Reference (Stop - First - 1));
         pragma Assert
           (Power_Reference (Stop - 1) =
              Power_Reference (First) * Power_Reference (Stop - First - 1));
      else
         pragma Assert (Power_Reference (Stop - First) = 1);
      end if;
   end Power_Factor;

   --  Closed quotient witness over the original Digit domain. Invalid spans
   --  still have Digit's original zero semantics; valid spans are required
   --  only by the later bridge to Magnitude. This is not an imported theorem.
   function Prefix_Tail
     (Data : Byte_Array; Q : Quantity; First, Stop : Byte_Count)
      return Valid_Big_Integer is
     (if First = Stop then To_Big_Integer (0)
      else Prefix_Tail (Data, Q, First, Stop - 1)
        + To_Big_Integer (Digit (Data, Q, Stop - 1))
          * Power_Reference (Stop - First - 1))
   with Ghost, Global => null,
     Pre => First <= Stop,
     Subprogram_Variant => (Decreases => Stop),
     Post => Prefix_Tail'Result >= 0;

   procedure Prefix_Decomposition
     (Data : Byte_Array; Q : Quantity; First, Stop : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => First <= Stop,
     Subprogram_Variant => (Decreases => Stop),
     Post => Prefix_Reference (Data, Q, Stop) =
       Prefix_Reference (Data, Q, First) + Power_Reference (First)
         * Prefix_Tail (Data, Q, First, Stop);

   procedure Prefix_Decomposition
     (Data : Byte_Array; Q : Quantity; First, Stop : Byte_Count) is
   begin
      if First < Stop then
         Prefix_Decomposition (Data, Q, First, Stop - 1);
         Power_Factor (First, Stop - 1);
         pragma Assert
           (Prefix_Reference (Data, Q, Stop) =
              Prefix_Reference (Data, Q, Stop - 1)
                + To_Big_Integer (Digit (Data, Q, Stop - 1))
                  * Power_Reference (Stop - 1));
         pragma Assert
           (Prefix_Tail (Data, Q, First, Stop) =
              Prefix_Tail (Data, Q, First, Stop - 1)
                + To_Big_Integer (Digit (Data, Q, Stop - 1))
                  * Power_Reference (Stop - First - 1));
      else
         pragma Assert (Prefix_Tail (Data, Q, First, Stop) = 0);
      end if;
   end Prefix_Decomposition;

   procedure Magnitude_Columns
     (Data : Byte_Array; Q : Quantity; Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Span_Valid (Data, Q),
     Post => Magnitude (Data, Q) = Prefix_Value (Data, Q, Count)
       + Radix_Power (Count)
         * Prefix_Tail (Data, Q, Count, Byte_Count'Max (Count, Q.Length))
   is
      Stop : constant Byte_Count := Byte_Count'Max (Count, Q.Length);
   begin
      Prefix_Padding (Data, Q, Stop);
      Prefix_Decomposition (Data, Q, Count, Stop);
      pragma Assert
        (Prefix_Value (Data, Q, Stop) = Prefix_Reference (Data, Q, Stop));
      pragma Assert
        (Prefix_Value (Data, Q, Count) = Prefix_Reference (Data, Q, Count));
      pragma Assert (Radix_Power (Count) = Power_Reference (Count));
   end Magnitude_Columns;

   procedure Column_Quotient (Column : Natural)
   with Ghost, Global => null, Always_Terminates,
     Pre => Column <= 255 + 255 + 1,
     Post => To_Big_Integer (Column) =
       To_Big_Integer (Column / 256) * To_Big_Integer (256)
         + To_Big_Integer (Column mod 256)
       and then Column / 256 <= 1
       and then Column mod 256 <= 255
   is
   begin
      pragma Assert (Column = (Column / 256) * 256 + Column mod 256);
      pragma Assert
        (To_Big_Integer ((Column / 256) * 256) =
           To_Big_Integer (Column / 256) * To_Big_Integer (256));
      pragma Assert
        (To_Big_Integer (Column) =
           To_Big_Integer ((Column / 256) * 256)
             + To_Big_Integer (Column mod 256));
   end Column_Quotient;

   --  An explicit signed quotient and the unique small remainder. The caller
   --  supplies a whole-value equation only as a hypothesis inside a guarded
   --  contradiction branch; it never assumes the producer's desired result.
   procedure Unique_Column
     (Column, Digit_Value : Natural; Quotient : Valid_Big_Integer)
   with Ghost, Global => null, Always_Terminates,
     Pre => Column <= 255 + 255 + 1 and then Digit_Value <= 255
       and then To_Big_Integer (Column) =
         To_Big_Integer (256) * Quotient + To_Big_Integer (Digit_Value),
     Post => Digit_Value = Column mod 256
   is
      Ordinary_Quotient : constant Valid_Big_Integer :=
        To_Big_Integer (Column / 256);
      Difference : constant Valid_Big_Integer := Quotient - Ordinary_Quotient;
   begin
      Column_Quotient (Column);
      pragma Assert
        (To_Big_Integer (256) * Difference =
           To_Big_Integer (Column mod 256) - To_Big_Integer (Digit_Value));
      if Difference < 0 then
         pragma Assert (Difference <= -1);
         pragma Assert (To_Big_Integer (256) * Difference <= -256);
         pragma Assert
           (To_Big_Integer (Column mod 256) - To_Big_Integer (Digit_Value)
              > -256);
         pragma Assert (False);
      elsif Difference > 0 then
         pragma Assert (Difference >= 1);
         pragma Assert (To_Big_Integer (256) * Difference >= 256);
         pragma Assert
           (To_Big_Integer (Column mod 256) - To_Big_Integer (Digit_Value)
              < 256);
         pragma Assert (False);
      end if;
      pragma Assert (Difference = 0);
      pragma Assert
        (To_Big_Integer (Column mod 256) = To_Big_Integer (Digit_Value));
   end Unique_Column;

   procedure Addition_Step
     (Data : Byte_Array; Left, Right, Sum : Quantity;
      Offset : Byte_Count; Carry, Column, Bias : Natural)
   with Ghost, Global => null, Always_Terminates,
     Pre => Offset < Byte_Count'Last and then Carry <= 1
       and then Column = Digit (Data, Left, Offset)
         + Digit (Data, Right, Offset) + Carry
       and then Digit (Data, Sum, Offset) = Column mod 256
       and then Prefix_Value (Data, Sum, Offset)
         + To_Big_Integer (Carry) * Radix_Power (Offset)
           = Prefix_Value (Data, Left, Offset)
             + Prefix_Value (Data, Right, Offset) + To_Big_Integer (Bias),
     Post => Prefix_Value (Data, Sum, Offset + 1)
       + To_Big_Integer (Column / 256) * Radix_Power (Offset + 1)
         = Prefix_Value (Data, Left, Offset + 1)
           + Prefix_Value (Data, Right, Offset + 1) + To_Big_Integer (Bias)
   is
   begin
      Prefix_Step (Data, Left, Offset);
      Prefix_Step (Data, Right, Offset);
      Prefix_Step (Data, Sum, Offset);
      Column_Quotient (Column);
      pragma Assert
        (To_Big_Integer (Column) =
           To_Big_Integer (Digit (Data, Left, Offset))
             + To_Big_Integer (Digit (Data, Right, Offset))
             + To_Big_Integer (Carry));
      pragma Assert
        (Prefix_Value (Data, Left, Offset + 1)
           + Prefix_Value (Data, Right, Offset + 1) + To_Big_Integer (Bias)
             = Prefix_Value (Data, Sum, Offset)
               + To_Big_Integer (Column) * Radix_Power (Offset));
   end Addition_Step;

   procedure Addition_Mismatch
     (Data : Byte_Array; Left, Right, Sum : Quantity;
      Offset : Byte_Count; Carry, Column, Bias : Natural)
   with Ghost, Global => null, Always_Terminates,
     Pre => Span_Valid (Data, Left) and then Span_Valid (Data, Right)
       and then Span_Valid (Data, Sum) and then Offset < Byte_Count'Last
       and then Carry <= 1
       and then Column = Digit (Data, Left, Offset)
         + Digit (Data, Right, Offset) + Carry
       and then Digit (Data, Sum, Offset) /= Column mod 256
       and then Prefix_Value (Data, Sum, Offset)
         + To_Big_Integer (Carry) * Radix_Power (Offset)
           = Prefix_Value (Data, Left, Offset)
             + Prefix_Value (Data, Right, Offset) + To_Big_Integer (Bias),
     Post => Magnitude (Data, Sum) /= Magnitude (Data, Left)
       + Magnitude (Data, Right) + To_Big_Integer (Bias)
   is
      Next : constant Byte_Count := Offset + 1;
      Place : constant Valid_Big_Integer := Radix_Power (Offset);
      Tail_Difference : constant Valid_Big_Integer :=
        Prefix_Tail (Data, Sum, Next, Byte_Count'Max (Next, Sum.Length))
          - Prefix_Tail (Data, Left, Next, Byte_Count'Max (Next, Left.Length))
          - Prefix_Tail (Data, Right, Next, Byte_Count'Max (Next, Right.Length));
   begin
      Prefix_Step (Data, Left, Offset);
      Prefix_Step (Data, Right, Offset);
      Prefix_Step (Data, Sum, Offset);
      Magnitude_Columns (Data, Left, Next);
      Magnitude_Columns (Data, Right, Next);
      Magnitude_Columns (Data, Sum, Next);
      pragma Assert (Place > 0);
      pragma Assert
        (To_Big_Integer (Column) =
           To_Big_Integer (Digit (Data, Left, Offset))
             + To_Big_Integer (Digit (Data, Right, Offset))
             + To_Big_Integer (Carry));
      if Magnitude (Data, Sum) = Magnitude (Data, Left)
        + Magnitude (Data, Right) + To_Big_Integer (Bias)
      then
         pragma Assert
           ((To_Big_Integer (Column)
               - To_Big_Integer (Digit (Data, Sum, Offset))) * Place
                 = Radix_Power (Next) * Tail_Difference);
         pragma Assert
           ((To_Big_Integer (Column)
               - To_Big_Integer (Digit (Data, Sum, Offset))) * Place
                 = (To_Big_Integer (256) * Tail_Difference) * Place);
         pragma Assert
           (To_Big_Integer (Column) =
              To_Big_Integer (256) * Tail_Difference
                + To_Big_Integer (Digit (Data, Sum, Offset)));
         Unique_Column (Column, Digit (Data, Sum, Offset), Tail_Difference);
         pragma Assert (False);
      end if;
   end Addition_Mismatch;

   procedure Addition_Finish
     (Data : Byte_Array; Left, Right, Sum : Quantity;
      Count : Byte_Count; Carry, Bias : Natural)
   with Ghost, Global => null, Always_Terminates,
     Pre => Span_Valid (Data, Left) and then Span_Valid (Data, Right)
       and then Span_Valid (Data, Sum) and then Left.Length <= Count
       and then Right.Length <= Count and then Sum.Length <= Count
       and then Carry <= 1
       and then Prefix_Value (Data, Sum, Count)
         + To_Big_Integer (Carry) * Radix_Power (Count)
           = Prefix_Value (Data, Left, Count)
             + Prefix_Value (Data, Right, Count) + To_Big_Integer (Bias),
     Post => (Carry = 0) =
       (Magnitude (Data, Sum) = Magnitude (Data, Left)
          + Magnitude (Data, Right) + To_Big_Integer (Bias))
   is
   begin
      Prefix_Padding (Data, Left, Count);
      Prefix_Padding (Data, Right, Count);
      Prefix_Padding (Data, Sum, Count);
      pragma Assert (Radix_Power (Count) > 0);
      pragma Assert
        (Magnitude (Data, Sum) + To_Big_Integer (Carry) * Radix_Power (Count)
           = Magnitude (Data, Left) + Magnitude (Data, Right)
             + To_Big_Integer (Bias));
      if Carry /= 0 then
         pragma Assert (Carry = 1);
         pragma Assert
           (Magnitude (Data, Sum) < Magnitude (Data, Left)
              + Magnitude (Data, Right) + To_Big_Integer (Bias));
      end if;
   end Addition_Finish;

   procedure Zero_Prefix (Data : Byte_Array; Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Subprogram_Variant => (Decreases => Count),
     Post => Span_Valid (Data, Zero_Quantity)
       and then Prefix_Value (Data, Zero_Quantity, Count) = 0
       and then Magnitude (Data, Zero_Quantity) = 0
       and then Digit (Data, Zero_Quantity, Count) = 0;

   procedure Zero_Prefix (Data : Byte_Array; Count : Byte_Count) is
   begin
      if Count > 0 then
         Zero_Prefix (Data, Count - 1);
         pragma Assert (Digit (Data, Zero_Quantity, Count - 1) = 0);
         pragma Assert
           (Prefix_Reference (Data, Zero_Quantity, Count) =
              Prefix_Reference (Data, Zero_Quantity, Count - 1));
      end if;
      pragma Assert (Prefix_Value (Data, Zero_Quantity, 0) = 0);
      pragma Assert (Magnitude (Data, Zero_Quantity) = 0);
   end Zero_Prefix;

   procedure Nonnegative_Magnitude (Data : Byte_Array; Q : Quantity)
   with Ghost, Global => null, Always_Terminates,
     Pre => Span_Valid (Data, Q) and then Value (Data, Q) >= 0,
     Post => Value (Data, Q) = Magnitude (Data, Q)
   is
   begin
      if Q.Negative then
         pragma Assert (Value (Data, Q) = -Magnitude (Data, Q));
         pragma Assert (Magnitude (Data, Q) >= 0);
         pragma Assert (Magnitude (Data, Q) = 0);
      else
         pragma Assert (Value (Data, Q) = Magnitude (Data, Q));
      end if;
   end Nonnegative_Magnitude;

   function Nonnegative_Valid (Data : Byte_Array; Q : Quantity) return Boolean is
   begin
      return Span_Valid (Data, Q) and then not Is_Negative (Data, Q);
   end Nonnegative_Valid;

   function Magnitude_Sum_Equals
     (Data : Byte_Array; Left, Right, Sum : Quantity) return Boolean
   is
      Count : constant Byte_Count := Byte_Count'Max
        (Left.Length, Byte_Count'Max (Right.Length, Sum.Length));
      Offset : Byte_Count := 0;
      Carry : Natural range 0 .. 1 := 0;
      Column : Natural;
   begin
      if not Span_Valid (Data, Left) or else not Span_Valid (Data, Right)
        or else not Span_Valid (Data, Sum) then
         return False;
      end if;
      while Offset < Count loop
         pragma Loop_Invariant (Offset <= Count);
         pragma Loop_Invariant
           (Prefix_Value (Data, Sum, Offset) + To_Big_Integer (Carry) *
              Radix_Power (Offset) = Prefix_Value (Data, Left, Offset) +
              Prefix_Value (Data, Right, Offset));
         pragma Loop_Variant (Decreases => Count - Offset);
         Column := Digit (Data, Left, Offset) + Digit (Data, Right, Offset) + Carry;
         if Digit (Data, Sum, Offset) /= Column mod 256 then
            Addition_Mismatch (Data, Left, Right, Sum, Offset, Carry, Column, 0);
            return False;
         end if;
         Addition_Step (Data, Left, Right, Sum, Offset, Carry, Column, 0);
         Carry := Column / 256;
         Offset := Offset + 1;
      end loop;
      Addition_Finish (Data, Left, Right, Sum, Count, Carry, 0);
      return Carry = 0;
   end Magnitude_Sum_Equals;

   function Signed_Sum_Equals
     (Data : Byte_Array; Left, Right, Sum : Quantity) return Boolean
   is
      Left_Negative, Right_Negative, Sum_Negative : Boolean;
   begin
      if not Span_Valid (Data, Left) or else not Span_Valid (Data, Right)
        or else not Span_Valid (Data, Sum) then
         return False;
      end if;
      Left_Negative := Is_Negative (Data, Left);
      Right_Negative := Is_Negative (Data, Right);
      Sum_Negative := Is_Negative (Data, Sum);
      if Left_Negative = Right_Negative then
         return Sum_Negative = Left_Negative and then
           Magnitude_Sum_Equals (Data, Left, Right, Sum);
      elsif Left_Negative then
         if Sum_Negative then
            return Magnitude_Sum_Equals (Data, Right, Sum, Left);
         else
            return Magnitude_Sum_Equals (Data, Left, Sum, Right);
         end if;
      else
         if Sum_Negative then
            return Magnitude_Sum_Equals (Data, Left, Sum, Right);
         else
            return Magnitude_Sum_Equals (Data, Right, Sum, Left);
         end if;
      end if;
   end Signed_Sum_Equals;

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
      Nonnegative_Magnitude (Data, Before);
      Nonnegative_Magnitude (Data, After);
      while Offset < Count loop
         pragma Loop_Invariant (Offset <= Count);
         pragma Loop_Invariant
           (Prefix_Value (Data, After, Offset) + To_Big_Integer (Carry) *
              Radix_Power (Offset) = Prefix_Value (Data, Before, Offset) + 1);
         pragma Loop_Variant (Decreases => Count - Offset);
         Column := Digit (Data, Before, Offset) + Carry;
         Zero_Prefix (Data, Offset);
         if Digit (Data, After, Offset) /= Column mod 256 then
            Addition_Mismatch
              (Data, Before, Zero_Quantity, After, Offset, Carry, Column, 1);
            return False;
         end if;
         Zero_Prefix (Data, Offset + 1);
         Addition_Step
           (Data, Before, Zero_Quantity, After, Offset, Carry, Column, 1);
         Carry := Column / 256;
         Offset := Offset + 1;
      end loop;
      Zero_Prefix (Data, Count);
      Addition_Finish (Data, Before, Zero_Quantity, After, Count, Carry, 1);
      return Carry = 0;
   end Is_Successor;

   function Conserved (Data : Byte_Array; S : Ledger_State) return Boolean is
   begin
      if not State_Shape (Data, S) then
         return False;
      elsif S.Selected.Present and then S.Selected.Phase /= Released then
         return Signed_Sum_Equals (Data, S.Other_Reservations,
                                   S.Selected.Value.Amount, S.Total);
      else
         return Compare (Data, S.Total, S.Other_Reservations) = Equal;
      end if;
   end Conserved;

   function Same_Reservation
     (Data : Byte_Array; Left, Right : Reservation_Record) return Boolean is
   begin
      return Same_Binding (Data, Left.Binding, Right.Binding) and then
        Compare (Data, Left.Amount, Right.Amount) = Equal;
   end Same_Reservation;

   function Proposed_Row
     (Data : Byte_Array; Before, Proposed : Ledger_State; R : Request)
      return Boolean is
   begin
      case R.Kind is
         when Unknown_Operation => return False;
         when Reserve =>
            return Proposed.Selected.Present and then
              Proposed.Selected.Phase = Active and then
              Same_Reservation (Data, Proposed.Selected.Value, R.New_Reservation);
         when Consume | Release =>
            return Before.Selected.Present and then Proposed.Selected.Present
              and then Proposed.Selected.Phase =
                (if R.Kind = Consume then Consumed else Released)
              and then Same_Reservation
                (Data, Before.Selected.Value, Proposed.Selected.Value);
      end case;
   end Proposed_Row;

   function Change_Conserved
     (Data : Byte_Array; Before, Proposed : Ledger_State; R : Request)
      return Boolean is
   begin
      case R.Kind is
         when Unknown_Operation => return False;
         when Reserve =>
            return Signed_Sum_Equals
              (Data, Before.Total, R.New_Reservation.Amount, Proposed.Total);
         when Consume =>
            return Compare (Data, Before.Total, Proposed.Total) = Equal;
         when Release =>
            return Before.Selected.Present and then Signed_Sum_Equals
              (Data, Proposed.Total, Before.Selected.Value.Amount, Before.Total);
      end case;
   end Change_Conserved;

   function Check
     (Data : Byte_Array; Before, Proposed : Ledger_State;
      High_Water : High_Water_Observation; R : Request) return Result_Status is
   begin
      if R.Kind = Unknown_Operation then
         return Unknown_Kind;
      elsif not State_Shape (Data, Before) then
         return Invalid_Before;
      elsif not State_Shape (Data, Proposed) then
         return Invalid_Proposed;
      elsif not High_Water.Epoch.Present then
         return Observation_Absent;
      elsif not Context_Valid (Data, High_Water.Scope) or else
        not Epoch_Valid (Data, High_Water.Epoch) then
         return Observation_Invalid;
      elsif not Same_Context (Data, Before.Scope, High_Water.Scope) then
         return Observation_Scope_Mismatch;
      elsif Compare (Data, Before.Epoch.Value, High_Water.Epoch.Value) /= Equal then
         return High_Water_Mismatch;
      elsif not Request_Shape (Data, Before, R) then
         return Request_Invalid;
      end if;
      case R.Kind is
         when Unknown_Operation => return Unknown_Kind;
         when Reserve =>
            if Compare (Data, R.Expected_Epoch.Value, Before.Epoch.Value) /= Equal then
               return Stale_Reserve_Epoch;
            elsif Before.Selected.Present then
               return Slot_Already_Exists;
            end if;
         when Consume | Release =>
            if not Before.Selected.Present then
               return Reservation_Absent;
            elsif not Same_Identity
              (Data, R.Requester, Before.Selected.Value.Binding.Owner) then
               return Wrong_Owner;
            elsif not Same_Identity
              (Data, R.Reservation, Before.Selected.Value.Binding.Reservation) then
               return Reservation_Mismatch;
            elsif not Same_Identity
              (Data, R.Operation, Before.Selected.Value.Binding.Operation) then
               return Operation_Mismatch;
            elsif Before.Selected.Phase = Released then
               return Already_Released;
            elsif Before.Selected.Phase = Consumed then
               return Already_Consumed;
            end if;
      end case;
      if not Conserved (Data, Before) then
         return Before_Conservation_Mismatch;
      elsif not Same_Context (Data, Before.Scope, Proposed.Scope) then
         return Context_Changed;
      elsif Compare (Data, Before.Other_Reservations, Proposed.Other_Reservations) /= Equal then
         return Remainder_Changed;
      elsif not Proposed_Row (Data, Before, Proposed, R) then
         return Proposed_Row_Mismatch;
      elsif not Is_Successor (Data, Before.Epoch.Value, Proposed.Epoch.Value) then
         return Epoch_Not_Successor;
      elsif not Conserved (Data, Proposed) then
         return Proposed_Conservation_Mismatch;
      elsif not Change_Conserved (Data, Before, Proposed, R) then
         return Transition_Conservation_Mismatch;
      elsif R.Kind = Reserve and then Compare (Data, Proposed.Total, R.Ceiling) = Greater then
         return Limit_Exceeded;
      else
         return Ready;
      end if;
   end Check;

   procedure Apply
     (Data : Byte_Array; State : in out Ledger_State; Proposed : Ledger_State;
      High_Water : High_Water_Observation; R : Request; Status : out Result_Status) is
   begin
      Status := Check (Data, State, Proposed, High_Water, R);
      if Status = Ready then
         State := Proposed;
      end if;
   end Apply;
end Resource_Reservation_Transition;
