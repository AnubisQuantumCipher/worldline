with Resource_Quantities;
with SPARK.Big_Integers;

package Worldline.Emitter_Ordinal with SPARK_Mode is
   package Q renames Resource_Quantities;
   use SPARK.Big_Integers;
   use type Q.Byte_Count;
   use type Q.Byte;

   --  Mathematical references only: executable arithmetic remains byte-wise.
   function Unsigned_Span (Data : Q.Byte_Array) return Q.Quantity is
     ((False, Data'First, Data'Length))
   with Ghost, Global => null;

   function Canonical_Text (Text : Q.Byte_Array) return Boolean is
     (Text'Length > 0 and then
      (Text'Length = 1 or else Text (Text'First) /= 48) and then
      (for all I in Text'Range => Text (I) in 48 .. 57))
   with Ghost, Global => null;

   function Decimal_Prefix (Text : Q.Byte_Array; Count : Q.Byte_Count)
      return Valid_Big_Integer is
     (if Count = 0 then To_Big_Integer (0)
      else Decimal_Prefix (Text, Count - 1) * 10 +
        To_Big_Integer (Integer (Text (Text'First + (Count - 1))) - 48))
   with Ghost, Global => null, Pre => Count <= Text'Length,
     Subprogram_Variant => (Decreases => Count);

   function Minimal_Length (Magnitude : Q.Byte_Array) return Q.Byte_Count
   with Global => null,
     Post => Minimal_Length'Result >= 1 and then
       Minimal_Length'Result <= Q.Byte_Count'Max (1, Magnitude'Length) and then
       Q.Magnitude (Magnitude, Unsigned_Span (Magnitude)) <
         Q.Power_Reference (Minimal_Length'Result) and then
       (if Minimal_Length'Result > 1 then
          Q.Magnitude (Magnitude, Unsigned_Span (Magnitude)) >=
            Q.Power_Reference (Minimal_Length'Result - 1));

   function Same_Value (Left, Right : Q.Byte_Array) return Boolean
   with Global => null,
     Post => Same_Value'Result =
       (Q.Value (Left, Unsigned_Span (Left)) =
        Q.Value (Right, Unsigned_Span (Right)));

   --  Empty and high-order zero octets are legal. Output is zero-filled beyond
   --  the minimal successor; a short buffer receives its low-order prefix.
   --  Needed = 0 denotes an unrepresentable storage extent, not a value cap.
   procedure Successor
     (Input : Q.Byte_Array; Output : out Q.Byte_Array;
      Needed : out Q.Byte_Count; Complete : out Boolean)
   with Global => null,
     Post => Complete = (Needed > 0 and then Needed <= Output'Length) and then
       (if Needed = 0 then
          Q.Magnitude (Input, Unsigned_Span (Input)) + 1 >=
            Q.Power_Reference (Q.Byte_Count'Last) and then
          (for all I in Output'Range => Output (I) = 0)
        else
          Q.Magnitude (Input, Unsigned_Span (Input)) + 1 <
            Q.Power_Reference (Needed) and then
          (if Needed > 1 then
             Q.Magnitude (Input, Unsigned_Span (Input)) + 1 >=
               Q.Power_Reference (Needed - 1)) and then
          Q.Value (Output, Unsigned_Span (Output)) =
            (Q.Value (Input, Unsigned_Span (Input)) + 1) mod
              Q.Power_Reference (Output'Length));

   function Canonical_Decimal_Matches
     (Text, Magnitude : Q.Byte_Array) return Boolean
   with Global => null,
     Post => Canonical_Decimal_Matches'Result =
       (Canonical_Text (Text) and then
        Decimal_Prefix (Text, Text'Length) =
          Q.Magnitude (Magnitude, Unsigned_Span (Magnitude)));
end Worldline.Emitter_Ordinal;
