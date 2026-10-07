--  Additive direct actual-core-library controls: UNBUILT and UNRUN.
--  Original ordinary resource fixtures and all native/proof controls remain exact.
--  Finite specimen storage is TEST_ONLY, never an accepted quantity/length cap.
with Ada.Text_IO;
with Worldline.Resources;

procedure Test_Resources_Prefix_Correspondence is
   use Worldline.Resources;
   use type Byte;
   Empty : constant Byte_Array (1 .. 0) := [];
   Zero : constant Byte_Array := [0];
   Large : Byte_Array (1 .. 33) := [others => 0];

   procedure Require (Name : String; Condition : Boolean) is
   begin
      if not Condition then
         raise Program_Error with Name;
      end if;
      Ada.Text_IO.Put_Line ("PASS " & Name);
   end Require;
begin
   Require ("empty_sum", Sum_Equals (Empty, Empty, Empty));
   Require ("empty_zero_padding", Sum_Equals (Empty, Empty, [0, 0]));
   Require ("small_sum", Sum_Equals ([2], [3], [5]));
   Require ("small_sum_reverse", Sum_Equals ([3], [2], [5]));
   Require ("lower_mismatching_result", not Sum_Equals ([1], [1], [1]));
   Require ("higher_mismatching_result", not Sum_Equals ([1], [1], [3]));
   Require ("carry_sum", Sum_Equals ([255], [1], [0, 1]));
   Require ("carry_sum_padding", Sum_Equals ([255, 0], [1, 0, 0], [0, 1, 0]));
   Require ("carry_not_wrapped", not Sum_Equals ([255], [1], [0]));
   Require ("mismatching_high_column", not Sum_Equals ([255], [1], [0, 0]));
   Require ("arbitrary_lower_bounds", Sum_Equals ([9 => 2], [4 => 3], [12 => 5]));
   Require ("high_index_bounds", Sum_Equals
     ([Byte_Index'Last => 2], [Byte_Index'Last => 3], [Byte_Index'Last => 5]));
   Large (Large'Last) := 1;
   Require ("wide_full_alias", Sum_Equals (Large, Empty, Large));
   Require ("wide_full_alias_reverse", Sum_Equals (Empty, Large, Large));
   Require ("wide_not_zero", not Sum_Equals (Large, Empty, Zero));
   declare
      State : Reservation_State (2) :=
        (Capacity => 2, Available => [10, 0], Floor => [3, 0],
         Outstanding => [2, 0]);
      Before : constant Reservation_State := State;
      Accepted : Boolean;
   begin
      Try_Reserve (State, [5], Accepted);
      Require ("reserve_projection", Accepted and then State.Outstanding = Byte_Array'[7, 0]);
      Require ("reserve_capacity_and_observations", State.Capacity = Before.Capacity
        and then State.Available = Before.Available and then State.Floor = Before.Floor);
      declare
         Retained : constant Reservation_State := State;
      begin
         Try_Reserve (State, [1], Accepted);
         Require ("refusal_preserves_full_state", not Accepted and then State = Retained);
      end;
   end;
   declare
      State : Reservation_State (2) :=
        (Capacity => 2, Available => [0, 1], Floor => [0, 0],
         Outstanding => [255, 0]);
      Accepted : Boolean;
   begin
      Try_Reserve (State, [1, 0, 0], Accepted);
      Require ("reserve_carry_and_request_padding",
               Accepted and then State.Outstanding = Byte_Array'[0, 1]);
   end;
   declare
      State : Reservation_State (Large'Last) :=
        (Capacity => Large'Last, Available => Large, Floor => [others => 0],
         Outstanding => Large);
      Before : constant Reservation_State := State;
      Accepted : Boolean;
   begin
      Try_Reserve (State, Empty, Accepted);
      Require ("wide_zero_request_retains_whole_state", Accepted and then State = Before);
   end;
end Test_Resources_Prefix_Correspondence;
