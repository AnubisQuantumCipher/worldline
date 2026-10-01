package body Evaluation_Epoch with SPARK_Mode is
   function Nonnegative_Valid (Data : Byte_Array; Q : Quantity) return Boolean is
   begin
      return Span_Valid (Data, Q) and then not Is_Negative (Data, Q);
   end Nonnegative_Valid;

   function Same_Value (Data : Byte_Array; Left, Right : Quantity) return Boolean is
   begin
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
end Evaluation_Epoch;
