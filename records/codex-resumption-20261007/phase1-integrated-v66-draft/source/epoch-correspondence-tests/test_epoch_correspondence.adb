--  Additive direct actual-library source controls, UNBUILT and UNRUN.
--  Original transition/recovery controls remain mandatory and byte exact.
--  The finite arena is TEST_ONLY, never an epoch, value, history or packet cap.
with Ada.Text_IO;
with Evaluation_Epoch;
with Resource_Quantities;

procedure Test_Epoch_Correspondence is
   use Resource_Quantities;
   package E renames Evaluation_Epoch;
   --  Arena and named specimens retain the original transition-test bytes.
   Data : constant Byte_Array (1 .. 48) :=
     [1 => 0, 2 => 1, 3 => 2, 4 => 3, 5 => 4, 6 => 5,
      7 => 8, 8 => 9, 9 => 10, 10 => 255, 11 => 0, 12 => 1,
      16 .. 23 => 255, 32 => 1, 41 => 16#80#, 42 => 16#FF#,
      others => 0];
   Zero : constant Quantity := (False, 1, 0);
   Negative_Zero : constant Quantity := (True, 13, 2);
   One : constant Quantity := (False, 2, 1);
   Two : constant Quantity := (False, 3, 1);
   Three : constant Quantity := (False, 4, 1);
   Minus_Five : constant Quantity := (True, 6, 1);
   Carry_Before : constant Quantity := (False, 10, 1);
   Carry_After : constant Quantity := (False, 11, 2);
   Wide_Before : constant Quantity := (False, 16, 8);
   Wide_After : constant Quantity := (False, 24, 9);
   Padded_One : constant Quantity := (False, 12, 3);
   Padded_Wide : constant Quantity := (False, 16, 9);
   Invalid_Span : constant Quantity := (False, 48, 2);
   Empty_Outside : constant Quantity := (False, Byte_Index'Last, 0);
   High_Data : constant Byte_Array (Byte_Index'Last - 1 .. Byte_Index'Last) := [1, 2];
   High_One : constant Quantity := (False, High_Data'First, 1);
   High_Two : constant Quantity := (False, High_Data'Last, 1);
   High_Invalid : constant Quantity := (False, High_Data'Last, 2);

   procedure Require (Name : String; Condition : Boolean) is
   begin
      if not Condition then
         raise Program_Error with Name;
      end if;
      Ada.Text_IO.Put_Line ("PASS " & Name);
   end Require;
begin
   Require ("same_alias", E.Same_Value (Data, One, One));
   Require ("same_padding", E.Same_Value (Data, One, Padded_One));
   Require ("same_padding_reverse", E.Same_Value (Data, Padded_One, One));
   Require ("same_signed_zero", E.Same_Value (Data, Zero, Negative_Zero));
   Require ("same_empty_outside", E.Same_Value (Data, Zero, Empty_Outside));
   Require ("same_wide_padding", E.Same_Value (Data, Wide_Before, Padded_Wide));
   Require ("different_valid", not E.Same_Value (Data, One, Two));
   Require ("negative_self_refused", not E.Same_Value (Data, Minus_Five, Minus_Five));
   Require ("invalid_self_refused", not E.Same_Value (Data, Invalid_Span, Invalid_Span));
   Require ("invalid_right_refused", not E.Same_Value (Data, One, Invalid_Span));
   Require ("invalid_left_refused", not E.Same_Value (Data, Invalid_Span, One));
   Require ("carry_successor", E.Is_Successor (Data, Carry_Before, Carry_After));
   Require ("wide_successor", E.Is_Successor (Data, Wide_Before, Wide_After));
   Require ("wide_no_wrap", not E.Is_Successor (Data, Wide_Before, Zero));
   Require ("padding_successor", E.Is_Successor (Data, Padded_One, Two));
   Require ("signed_zero_successor", E.Is_Successor (Data, Negative_Zero, One));
   --  Exercise both ordered distinct-column branches, and final carry refusal.
   Require ("lower_mismatching_column", not E.Is_Successor (Data, One, One));
   Require ("higher_mismatching_column", not E.Is_Successor (Data, One, Three));
   Require ("negative_epoch_refused", not E.Is_Successor (Data, Minus_Five, Zero));
   Require ("invalid_successor_refused", not E.Is_Successor (Data, One, Invalid_Span));
   Require ("high_bound_self", E.Same_Value (High_Data, High_Two, High_Two));
   Require ("high_bound_successor", E.Is_Successor (High_Data, High_One, High_Two));
   Require ("high_bound_invalid_refused", not E.Same_Value (High_Data, High_Invalid, High_Invalid));
end Test_Epoch_Correspondence;
