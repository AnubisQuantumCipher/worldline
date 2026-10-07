--  Actual core library controls, source only: UNBUILT and UNRUN.
--  Finite specimen extents are TEST_ONLY, never a resource magnitude cap.
--  JACKAL exact/not-formal full oracle receipts are in jackal-controls-v2.json.
with Ada.Text_IO;
with Resource_Quantities;
with Resource_Ledger;

procedure Test_Resource_Ledger_Correspondence is
   use Resource_Quantities;
   use Resource_Ledger;
   use type Byte;
   procedure Require (Name : String; Condition : Boolean) is
   begin
      if not Condition then
         raise Program_Error with Name;
      end if;
      Ada.Text_IO.Put_Line ("PASS " & Name);
   end Require;
   Data : constant Byte_Array (10 .. 17) := [3, 2, 1, 2, 1, 2, 1, 255];
   Rows : constant Reservation_Array (7 .. 11) :=
     [((False, 10, 1), (Present => False)),
      ((False, 10, 1), (Present => True, Value => (False, 11, 1))),
      ((False, 12, 1), (Present => True, Value => (False, 13, 1))),
      ((True, 14, 1), (Present => False)),
      ((False, 15, 1), (Present => True, Value => (True, 16, 1)))];
   Slots : constant Span_Array (20 .. 24) :=
     [(30, 2), (24, 2), (40, 2), (26, 2), (36, 2)];
   Detail_Data : Byte_Array (23 .. 43);
   Total_Data : Byte_Array (50 .. 51);
   Details : Quantity_Array (70 .. 74);
   Total : Quantity;
   Status : Result_Status;
begin
   Compute (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total, Status);
   Require ("gapped_nonmonotone_slots_signed_total", Status = Computed
     and then Total = Quantity'(False, 50, 1) and then Total_Data = Byte_Array'[6, 0]);
   Require ("earlier_signed_details_retained",
     Details = Quantity_Array'[(False, 30, 1), (False, 24, 1), Empty,
                               (True, 26, 1), (False, 36, 1)]
     and then Detail_Data (30) = 3 and then Detail_Data (24) = 1
     and then Detail_Data (26) = 1 and then Detail_Data (36) = 3);
   Require ("whole_detail_padding_and_frame",
     (for all I in Detail_Data'Range =>
        (if I /= 30 and then I /= 24 and then I /= 26 and then I /= 36
         then Detail_Data (I) = 0)));
   declare
      Carry_Rows : constant Reservation_Array (3 .. 4) :=
        [((False, 17, 1), (Present => False)),
         ((False, 12, 1), (Present => False))];
      Carry_Slots : constant Span_Array (7 .. 8) := [(1, 1), (3, 1)];
      D : Byte_Array (1 .. 3);
      T : Byte_Array (8 .. 9);
      V : Quantity_Array (12 .. 13);
      Q : Quantity;
      S : Result_Status;
   begin
      Compute (Data, Carry_Rows, Carry_Slots, D, T, V, Q, S);
      Require ("written_carry_prefix", S = Computed
        and then T = Byte_Array'[0, 1] and then Q = Quantity'(False, 8, 2));
      declare
         Small : Byte_Array (5 .. 5);
      begin
         Compute (Data, Carry_Rows, Carry_Slots, D, Small, V, Q, S);
         Require ("ordered_storage_refusal_zeros_full_result",
           S = Insufficient_Storage and then Q = Empty
           and then (for all I in V'Range => V (I) = Empty)
           and then (for all I in D'Range => D (I) = 0)
           and then (for all I in Small'Range => Small (I) = 0));
      end;
   end;
   declare
      Wide : Byte_Array (1 .. 33) := [others => 0];
      Wide_Rows : constant Reservation_Array (9 .. 10) :=
        [((False, 1, 33), (Present => False)),
         ((True, 1, 33), (Present => False))];
      Wide_Slots : constant Span_Array (4 .. 5) := [(1, 34), (36, 34)];
      D : Byte_Array (1 .. 69);
      T : Byte_Array (1 .. 34);
      V : Quantity_Array (13 .. 14);
      Q : Quantity;
      S : Result_Status;
   begin
      Wide (Wide'Last) := 1;
      Compute (Wide, Wide_Rows, Wide_Slots, D, T, V, Q, S);
      Require ("full_magnitude_signed_cancellation", S = Computed
        and then Q = Empty and then (for all I in T'Range => T (I) = 0)
        and then V = Quantity_Array'[(False, 1, 33), (True, 36, 33)]);
      declare
         Small : Byte_Array (1 .. 32);
      begin
         Compute (Wide, Wide_Rows, Wide_Slots, D, Small, V, Q, S);
         Require ("nonzero_intermediate_not_final_only_capacity",
           S = Insufficient_Storage and then Q = Empty
           and then (for all I in D'Range => D (I) = 0)
           and then (for all I in Small'Range => Small (I) = 0)
           and then (for all I in V'Range => V (I) = Empty));
      end;
   end;
   declare
      High : constant Byte_Array (Byte_Index'Last .. Byte_Index'Last) := [1];
      High_Rows : constant Reservation_Array (Byte_Index'Last .. Byte_Index'Last) :=
        [((False, Byte_Index'Last, 1), (Present => False))];
      High_Slots : constant Span_Array (Byte_Index'Last .. Byte_Index'Last) :=
        [(Byte_Index'Last, 1)];
      D, T : Byte_Array (Byte_Index'Last .. Byte_Index'Last);
      V : Quantity_Array (Byte_Index'Last .. Byte_Index'Last);
      Q : Quantity;
      S : Result_Status;
   begin
      Compute (High, High_Rows, High_Slots, D, T, V, Q, S);
      Require ("actual_last_index_source_and_destination", S = Computed
        and then D (D'First) = 1 and then T (T'First) = 1
        and then Q = Quantity'(False, Byte_Index'Last, 1));
   end;
   declare
      Empty_Data : constant Byte_Array (7 .. 6) := [];
      Empty_Rows : constant Reservation_Array (9 .. 8) := [];
      Empty_Slots : constant Span_Array (3 .. 2) := [];
      D, T : Byte_Array (5 .. 4);
      V : Quantity_Array (10 .. 9);
      Q : Quantity;
      S : Result_Status;
   begin
      Compute (Empty_Data, Empty_Rows, Empty_Slots, D, T, V, Q, S);
      Require ("typed_empty_genesis", S = Computed and then Q = Empty);
   end;
   declare
      Bad_Rows : constant Reservation_Array (3 .. 3) :=
        [((False, 10, 1), (Present => True, Value => (False, 18, 1)))];
      Bad_Slots : constant Span_Array (7 .. 7) := [(1, 1)];
      D, T : Byte_Array (1 .. 1);
      V : Quantity_Array (5 .. 5);
      Q : Quantity;
      S : Result_Status;
   begin
      Compute (Data, Bad_Rows, Bad_Slots, D, T, V, Q, S);
      Require ("present_invalid_usage_never_absence", S = Invalid_Input
        and then Q = Empty and then D (1) = 0 and then T (1) = 0
        and then V (5) = Empty);
   end;
end Test_Resource_Ledger_Correspondence;
