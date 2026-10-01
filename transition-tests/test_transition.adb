with Ada.Text_IO;
with Resource_Quantities;
with Resource_Reservation_Transition;

--  Ordinary direct controls, outside SPARK proof scope. This finite owned
--  arena is TEST_ONLY, never an input-magnitude or identity policy limit.
--  Numeric expectations are pinned in the accompanying JACKAL receipts.
procedure Test_Transition is
   use Resource_Quantities;
   use Resource_Reservation_Transition;

   Data : constant Byte_Array (1 .. 48) :=
     (1 => 0, 2 => 1, 3 => 2, 4 => 3, 5 => 4, 6 => 5,
      7 => 8, 8 => 9, 9 => 10, 10 => 255, 11 => 0, 12 => 1,
      16 .. 23 => 255, 32 => 1, 41 => 16#80#, 42 => 16#FF#,
      others => 0);
   Zero : constant Quantity := (False, 1, 0);
   Negative_Zero : constant Quantity := (True, 13, 2);
   One : constant Quantity := (False, 2, 1);
   Two : constant Quantity := (False, 3, 1);
   Three : constant Quantity := (False, 4, 1);
   Five : constant Quantity := (False, 6, 1);
   Eight : constant Quantity := (False, 7, 1);
   Minus_Three : constant Quantity := (True, 4, 1);
   Minus_Five : constant Quantity := (True, 6, 1);
   Minus_Eight : constant Quantity := (True, 7, 1);
   Carry_Before : constant Quantity := (False, 10, 1);
   Carry_After : constant Quantity := (False, 11, 2);
   Wide_Before : constant Quantity := (False, 16, 8);
   Wide_After : constant Quantity := (False, 24, 9);
   Padded_One : constant Quantity := (False, 12, 3);
   Absent_Id : constant Optional_Identity := (Present => False);
   Universe_Id : constant Optional_Identity := (True, (41, 2));
   Policy_Id : constant Optional_Identity := (True, (42, 1));
   Resource_Id : constant Optional_Identity := (True, (41, 1));
   Empty_Id : constant Optional_Identity := (True, (48, 0));
   Scope : constant Context := (Universe_Id, Policy_Id, Resource_Id);
   Binding : constant Reservation_Binding :=
     (Reservation => Empty_Id, Operation => Policy_Id, Owner => Resource_Id,
      Universe => Universe_Id, Head => Empty_Id, Candidate => Universe_Id);
   Row : constant Reservation_Record := (Binding, Five);
   Before : constant Ledger_State :=
     (Scope => Scope, Epoch => (True, One), Total => Three,
      Other_Reservations => Three, Selected => (Present => False));
   Reserved : constant Ledger_State :=
     (Scope => Scope, Epoch => (True, Two), Total => Eight,
      Other_Reservations => Three,
      Selected => (Present => True, Value => Row, Phase => Active));
   Consume_After : constant Ledger_State :=
     (Scope => Scope, Epoch => (True, Three), Total => Eight,
      Other_Reservations => Three,
      Selected => (Present => True, Value => Row, Phase => Consumed));
   Release_After : constant Ledger_State :=
     (Scope => Scope, Epoch => (True, Three), Total => Three,
      Other_Reservations => Three,
      Selected => (Present => True, Value => Row, Phase => Released));
   Water : constant High_Water_Observation := (Scope, (True, One));
   Reserve_Request : constant Request :=
     (Kind => Reserve, Requester => Resource_Id, Expected_Epoch => (True, One),
      New_Reservation => Row, Ceiling => Eight);
   Consume_Request : constant Request :=
     (Kind => Consume, Requester => Resource_Id,
      Reservation => Empty_Id, Operation => Policy_Id);
   Release_Request : constant Request :=
     (Kind => Release, Requester => Resource_Id,
      Reservation => Empty_Id, Operation => Policy_Id);

   procedure Require (Name : String; Condition : Boolean) is
   begin
      if not Condition then
         raise Program_Error with Name;
      end if;
   end Require;

   procedure Boolean_Case (Name : String; Actual, Expected : Boolean) is
   begin
      Require (Name, Actual = Expected);
      Ada.Text_IO.Put_Line ("PASS " & Name);
   end Boolean_Case;

   procedure Decision_Case
     (Name : String; B, P : Ledger_State; H : High_Water_Observation;
      R : Request; Expected : Result_Status)
   is
      Current : Ledger_State := B;
      Status : Result_Status;
   begin
      Require (Name & ":Check", Check (Data, B, P, H, R) = Expected);
      Apply (Data, Current, P, H, R, Status);
      Require (Name & ":ApplyStatus", Status = Expected);
      if Expected = Ready then
         Require (Name & ":exact proposed record", Current = P);
      else
         Require (Name & ":exact before record", Current = B);
      end if;
      Ada.Text_IO.Put_Line ("PASS " & Name);
   end Decision_Case;
begin
   Boolean_Case ("magnitude_sum", Magnitude_Sum_Equals (Data, Three, Five, Eight), True);
   Boolean_Case ("signed_positive", Signed_Sum_Equals (Data, Minus_Five, Eight, Three), True);
   Boolean_Case ("signed_negative", Signed_Sum_Equals (Data, Minus_Eight, Five, Minus_Three), True);
   Boolean_Case ("signed_cancellation", Signed_Sum_Equals (Data, Five, Minus_Five, Zero), True);
   Boolean_Case ("negative_zero", Signed_Sum_Equals (Data, Negative_Zero, Three, Three), True);
   Boolean_Case ("carry_successor", Is_Successor (Data, Carry_Before, Carry_After), True);
   Boolean_Case ("wide_successor", Is_Successor (Data, Wide_Before, Wide_After), True);
   Boolean_Case ("wide_no_wrap", Is_Successor (Data, Wide_Before, Zero), False);
   Boolean_Case ("padded_epoch", Is_Successor (Data, Padded_One, Two), True);
   Boolean_Case ("negative_epoch", Is_Successor (Data, Minus_Five, Zero), False);
   Boolean_Case ("empty_identity_present", Same_Identity (Data, Empty_Id, (True, (1, 0))), True);
   Boolean_Case ("empty_identity_absent", Same_Identity (Data, Empty_Id, Absent_Id), False);

   Decision_Case ("reserve_exact_ceiling", Before, Reserved, Water, Reserve_Request, Ready);
   Decision_Case ("consume_without_request_epoch", Reserved, Consume_After,
                  (Scope, (True, Two)), Consume_Request, Ready);
   Decision_Case ("release_without_request_epoch", Reserved, Release_After,
                  (Scope, (True, Two)), Release_Request, Ready);
   declare
      B : Ledger_State := Before;
      P : Ledger_State := Reserved;
      H : High_Water_Observation := Water;
      R : Request := Reserve_Request;
   begin
      B.Total := Zero;
      B.Other_Reservations := Zero;
      B.Epoch := (True, Wide_Before);
      P.Total := Wide_After;
      P.Other_Reservations := Zero;
      P.Epoch := (True, Wide_After);
      P.Selected.Value.Amount := Wide_After;
      H.Epoch := B.Epoch;
      R.Expected_Epoch := B.Epoch;
      R.New_Reservation.Amount := Wide_After;
      R.Ceiling := Wide_After;
      Decision_Case ("wide_reserve", B, P, H, R, Ready);
   end;
   declare
      P : Ledger_State := Reserved;
      R : Request := Reserve_Request;
   begin
      R.New_Reservation.Amount := Negative_Zero;
      P.Selected.Value.Amount := Negative_Zero;
      P.Total := Three;
      Decision_Case ("zero_reserve", Before, P, Water, R, Ready);
   end;
   declare
      B : Ledger_State := Before;
      P : Ledger_State := Reserved;
      H : High_Water_Observation := Water;
      R : Request := Reserve_Request;
   begin
      B.Epoch := (Present => False);
      Decision_Case ("unknown_before_shape", B, P, H,
                     (Kind => Unknown_Operation, Requester => Absent_Id), Unknown_Kind);
      Decision_Case ("before_epoch_absent", B, P, H, R, Invalid_Before);
      B := Before;
      P.Epoch := (Present => False);
      Decision_Case ("proposed_epoch_absent", B, P, H, R, Invalid_Proposed);
      P := Reserved;
      H.Epoch := (Present => False);
      Decision_Case ("observation_absent", B, P, H, R, Observation_Absent);
      H.Epoch := (True, Minus_Five);
      Decision_Case ("observation_negative", B, P, H, R, Observation_Invalid);
      H := Water;
      H.Scope.Policy := Empty_Id;
      Decision_Case ("observation_scope", B, P, H, R, Observation_Scope_Mismatch);
      H := Water;
      H.Epoch := (True, Two);
      Decision_Case ("high_water_mismatch", B, P, H, R, High_Water_Mismatch);
      H := Water;
      R.Expected_Epoch := (Present => False);
      Decision_Case ("request_epoch_absent", B, P, H, R, Request_Invalid);
      R.Expected_Epoch := (True, Two);
      Decision_Case ("reserve_stale_epoch", B, P, H, R, Stale_Reserve_Epoch);
      R := Reserve_Request;
      B.Selected := Reserved.Selected;
      Decision_Case ("existing_slot_before_conservation", B, P, H, R, Slot_Already_Exists);
      B := Before;
      B.Total := Eight;
      Decision_Case ("before_conservation", B, P, H, R, Before_Conservation_Mismatch);
      B := Before;
      P.Scope.Policy := Empty_Id;
      Decision_Case ("context_changed", B, P, H, R, Context_Changed);
      P := Reserved;
      P.Other_Reservations := Five;
      Decision_Case ("remainder_changed", B, P, H, R, Remainder_Changed);
      P := Reserved;
      P.Selected.Value.Amount := Three;
      Decision_Case ("proposed_row", B, P, H, R, Proposed_Row_Mismatch);
      P := Reserved;
      P.Epoch := (True, One);
      Decision_Case ("epoch_no_advance", B, P, H, R, Epoch_Not_Successor);
      P := Reserved;
      P.Total := Three;
      Decision_Case ("proposed_conservation", B, P, H, R, Proposed_Conservation_Mismatch);
      P := Reserved;
      R.Ceiling := Minus_Five;
      Decision_Case ("signed_ceiling", B, P, H, R, Limit_Exceeded);
   end;
   declare
      B : Ledger_State := Reserved;
      R : Request := Release_Request;
   begin
      B.Selected := (Present => False);
      Decision_Case ("reservation_absent", B, Release_After,
                     (Scope, (True, Two)), R, Reservation_Absent);
      B := Reserved;
      R.Requester := Empty_Id;
      Decision_Case ("wrong_owner", B, Release_After,
                     (Scope, (True, Two)), R, Wrong_Owner);
      R := Release_Request;
      R.Reservation := Resource_Id;
      Decision_Case ("reservation_mismatch", B, Release_After,
                     (Scope, (True, Two)), R, Reservation_Mismatch);
      R := Release_Request;
      R.Operation := Empty_Id;
      Decision_Case ("operation_mismatch", B, Release_After,
                     (Scope, (True, Two)), R, Operation_Mismatch);
      R := Release_Request;
      B.Selected := (True, Row, Released);
      B.Total := Three;
      Decision_Case ("already_released", B, Release_After,
                     (Scope, (True, Two)), R, Already_Released);
      B := Reserved;
      B.Selected := (True, Row, Consumed);
      Decision_Case ("already_consumed", B, Release_After,
                     (Scope, (True, Two)), R, Already_Consumed);
   end;
   declare
      B : Ledger_State := Before;
   begin
      --  Well-typed descriptor whose nonempty extent exceeds this owned arena.
      B.Total := (False, Data'Last, 2);
      Decision_Case ("invalid_before_span", B, Reserved, Water,
                     Reserve_Request, Invalid_Before);
   end;
   declare
      B : Ledger_State := Before;
      P : Ledger_State := Reserved;
      H : High_Water_Observation := Water;
      R : Request := Reserve_Request;
   begin
      B.Epoch := (True, Carry_Before);
      H.Epoch := B.Epoch;
      R.Expected_Epoch := B.Epoch;
      --  The supplied valid output span keeps only the low carry byte.
      --  It cannot represent the required successor. No wrap is admitted.
      P.Epoch := (True, (False, Carry_After.First, 1));
      Decision_Case ("epoch_carry_output_short", B, P, H, R,
                     Epoch_Not_Successor);
   end;
   Ada.Text_IO.Put_Line ("PASS transition ordinary controls complete");
end Test_Transition;
