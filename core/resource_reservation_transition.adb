package body Resource_Reservation_Transition with SPARK_Mode is
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
            return False;
         end if;
         Carry := Column / 256;
         Offset := Offset + 1;
      end loop;
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
      while Offset < Count loop
         pragma Loop_Invariant (Offset <= Count);
         pragma Loop_Invariant
           (Prefix_Value (Data, After, Offset) + To_Big_Integer (Carry) *
              Radix_Power (Offset) = Prefix_Value (Data, Before, Offset) + 1);
         pragma Loop_Variant (Decreases => Count - Offset);
         Column := Digit (Data, Before, Offset) + Carry;
         if Digit (Data, After, Offset) /= Column mod 256 then
            return False;
         end if;
         Carry := Column / 256;
         Offset := Offset + 1;
      end loop;
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
