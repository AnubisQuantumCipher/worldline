with Resource_Quantities;
with SPARK.Big_Integers;

package Resource_Ledger with SPARK_Mode is
   use Resource_Quantities;
   use SPARK.Big_Integers;
   use type Byte;

   type Reservation_Row is record
      Reserved : Quantity;
      Used     : Optional_Quantity;
   end record;
   type Reservation_Array is array (Byte_Index range <>) of Reservation_Row;
   type Quantity_Array is array (Byte_Index range <>) of Quantity;
   type Output_Span is record
      First  : Byte_Index;
      Length : Byte_Count;
   end record;
   type Span_Array is array (Byte_Index range <>) of Output_Span;
   Empty : constant Quantity := (Negative => False, First => 1, Length => 0);

   function Rows_Valid
     (Data : Byte_Array; Rows : Reservation_Array) return Boolean is
     (for all I in Rows'Range =>
        Span_Valid (Data, Rows (I).Reserved) and then
        (not Rows (I).Used.Present or else
           Span_Valid (Data, Rows (I).Used.Value)));

   function Slot_Valid (Data : Byte_Array; Slot : Output_Span)
      return Boolean is
     (Span_Valid (Data, (False, Slot.First, Slot.Length)));

   function Disjoint (Left, Right : Output_Span) return Boolean is
     (Left.Length = 0 or else Right.Length = 0 or else
        (if Left.First <= Right.First then
            Left.Length <= Right.First - Left.First
         else Right.Length <= Left.First - Right.First));

   --  Slots name distinct writable extents in an owned output arena. Their
   --  ordinal order is the original reservation order, even for nonunit bases.
   function Layout_Valid
     (Data : Byte_Array; Slots : Span_Array; Details : Quantity_Array;
      Row_Count : Byte_Count) return Boolean is
     (Slots'Length = Row_Count and then Details'Length = Row_Count and then
        (for all I in Slots'Range => Slot_Valid (Data, Slots (I))) and then
        (for all I in Slots'Range =>
           (for all J in Slots'Range =>
              (if I < J then Disjoint (Slots (I), Slots (J))))));

   --  Total interval membership without forming a possibly overflowing upper
   --  bound. Empty spans contain no byte, wherever their First points.
   function Contains (Slot : Output_Span; Index : Byte_Index) return Boolean is
     (Slot.Length /= 0 and then Index >= Slot.First and then
        Index - Slot.First < Slot.Length)
   with Ghost, Global => null;

   --  A nonzero result starts at its assigned slot and has no high zero digit.
   --  Zero has exactly Empty's descriptor, including its sign and First.
   --  All remaining bytes of the slot are zero; input quantities remain free
   --  to use any previously admitted empty or leading-zero representation.
   function Canonical_In_Slot
     (Data : Byte_Array; Slot : Output_Span; Item : Quantity) return Boolean is
     (Slot_Valid (Data, Slot) and then Span_Valid (Data, Item) and then
        (if Item.Length = 0 then Item = Empty
         else Item.First = Slot.First and then Item.Length <= Slot.Length and then
           Data (Item.First + (Item.Length - 1)) /= 0) and then
        (for all I in Data'Range =>
           (if Contains (Slot, I) and then
              not Contains ((Item.First, Item.Length), I)
            then Data (I) = 0)))
   with Ghost, Global => null;

   --  These are out arenas: the successful frame outside every assigned slot
   --  is zero, not preservation of unspecified incoming out-parameter bytes.
   function Arena_Frame_Zero
     (Data : Byte_Array; Slots : Span_Array) return Boolean is
     (for all I in Data'Range =>
        (if not (for some S in Slots'Range => Contains (Slots (S), I)) then
           Data (I) = 0))
   with Ghost, Global => null;

   function Output_Representation
     (Detail_Data, Total_Data : Byte_Array; Slots : Span_Array;
      Details : Quantity_Array; Total : Quantity) return Boolean is
     (Layout_Valid (Detail_Data, Slots, Details, Slots'Length) and then
        Canonical_In_Slot
          (Total_Data,
           ((if Total_Data'Length = 0 then 1 else Total_Data'First),
            Total_Data'Length), Total) and then
        (for all S in Slots'Range =>
           Canonical_In_Slot
             (Detail_Data, Slots (S),
              Details (Details'First + (S - Slots'First)))) and then
        Arena_Frame_Zero (Detail_Data, Slots))
   with Ghost, Global => null;

   --  Independent complete Python integer relation, including signed reserved
   --  values when this pure unit is used outside the validated ledger loader.
   function Withheld_Reference
     (Data : Byte_Array; Row : Reservation_Row) return Valid_Big_Integer
   with Ghost, Global => null;

   function Row_Reference
     (Data : Byte_Array; Rows : Reservation_Array; Offset : Byte_Count)
      return Valid_Big_Integer
   with Ghost, Global => null;

   --  Closed recurrence independent of the iterative Prefix_Total producer.
   --  No public validity/capacity precondition or numeric bound is added.
   function Total_Reference
     (Data : Byte_Array; Rows : Reservation_Array; Count : Byte_Count)
      return Valid_Big_Integer is
     (if Count = 0 then To_Big_Integer (0)
      else Total_Reference (Data, Rows, Count - 1) +
        Row_Reference (Data, Rows, Count - 1))
   with Ghost, Global => null,
     Subprogram_Variant => (Decreases => Count);

   function Prefix_Total
     (Data : Byte_Array; Rows : Reservation_Array; Count : Byte_Count)
      return Valid_Big_Integer
   with Ghost, Global => null,
     Subprogram_Variant => (Decreases => Count),
     Post => Prefix_Total'Result =
       (if Count = 0 then To_Big_Integer (0)
        else Prefix_Total (Data, Rows, Count - 1) +
          Row_Reference (Data, Rows, Count - 1)) and then
       Prefix_Total'Result = Total_Reference (Data, Rows, Count);

   --  This is an exact storage relation, not a bound on accepted integers.
   --  The supplied total arena must hold every ordered partial sum. A caller
   --  must provision it; cancellation in the final sum does not create space
   --  for an earlier intermediate. No final-only capacity claim is made.
   function Storage_Sufficient
     (Data : Byte_Array; Rows : Reservation_Array; Slots : Span_Array;
      Total_Capacity : Byte_Count) return Boolean
   with Ghost, Global => null;

   type Result_Status is
     (Computed, Invalid_Input, Invalid_Output_Layout, Insufficient_Storage);

   function Result_Conforms
     (Data : Byte_Array; Rows : Reservation_Array; Slots : Span_Array;
      Detail_Data, Total_Data : Byte_Array; Details : Quantity_Array;
      Total : Quantity; Status : Result_Status) return Boolean
   with Ghost, Global => null;

   --  Total typed numeric projection only; no public Pre. Input observations
   --  carry values, never assertions of producer truth. All output storage is
   --  caller-owned and disjoint under SPARK's ordinary aliasing rules.
   --  On every refusal all outputs are empty/zero; no partial result is valid.
   --  Success also has canonical slot-confined descriptors, zero slot/total
   --  padding, and a zero detail-arena frame outside all assigned slots.
   --  No ledger/filter/lock/epoch/lifecycle or protected-effect action occurs.
   procedure Compute
     (Data : Byte_Array; Rows : Reservation_Array; Slots : Span_Array;
      Detail_Data, Total_Data : out Byte_Array;
      Details : out Quantity_Array; Total : out Quantity;
      Status : out Result_Status)
   with Global => null, Always_Terminates,
     Post => Result_Conforms
       (Data, Rows, Slots, Detail_Data, Total_Data, Details, Total, Status);
   --  Complete signed headroom projection. Input representations keep the
   --  same total quantity domain, including empty and high-zero magnitudes.
   function Headroom_Input_Valid
     (Data : Byte_Array; Available, Withheld, Floor : Quantity)
      return Boolean is
     (Span_Valid (Data, Available) and then Span_Valid (Data, Withheld)
        and then Span_Valid (Data, Floor))
   with Global => null;

   function Headroom_Reference
     (Data : Byte_Array; Available, Withheld, Floor : Quantity)
      return Valid_Big_Integer is
     (if Headroom_Input_Valid (Data, Available, Withheld, Floor) then
         Value (Data, Available) - Value (Data, Withheld) - Value (Data, Floor)
      else To_Big_Integer (0))
   with Ghost, Global => null;

   --  Both the ordered intermediate and final signed magnitudes must fit.
   --  This is caller-owned storage sufficiency, not a bound on input values.
   function Headroom_Storage_Sufficient
     (Data : Byte_Array; Available, Withheld, Floor : Quantity;
      Capacity : Byte_Count) return Boolean is
     (Headroom_Input_Valid (Data, Available, Withheld, Floor) and then
        abs (Value (Data, Available) - Value (Data, Withheld)) <
          Radix_Power (Capacity) and then
        abs Headroom_Reference (Data, Available, Withheld, Floor) <
          Radix_Power (Capacity))
   with Ghost, Global => null;

   function Headroom_Conforms
     (Data : Byte_Array; Available, Withheld, Floor : Quantity;
      Output : Byte_Array; Result : Quantity; Status : Result_Status)
      return Boolean is
     ((if not Headroom_Input_Valid (Data, Available, Withheld, Floor) then
          Status = Invalid_Input
       elsif not Headroom_Storage_Sufficient
         (Data, Available, Withheld, Floor, Output'Length)
       then Status = Insufficient_Storage
       else Status = Computed) and then
      (if Status = Computed then
          Canonical_In_Slot
            (Output, ((if Output'Length = 0 then 1 else Output'First),
                      Output'Length), Result) and then
          Value (Output, Result) =
            Headroom_Reference (Data, Available, Withheld, Floor)
       else Result = Empty and then
          (for all I in Output'Range => Output (I) = 0)))
   with Ghost, Global => null;

   --  No public Pre; malformed spans and insufficient supplied storage have
   --  exact typed refusals, never a partial or clamped numeric answer.
   procedure Compute_Headroom
     (Data : Byte_Array; Available, Withheld, Floor : Quantity;
      Output : out Byte_Array; Result : out Quantity;
      Status : out Result_Status)
   with Global => null, Always_Terminates,
     Post => Headroom_Conforms
       (Data, Available, Withheld, Floor, Output, Result, Status);

end Resource_Ledger;
