with Interfaces;
with SPARK.Big_Integers;

package Resource_Quantities with SPARK_Mode is
   use SPARK.Big_Integers;
   subtype Byte is Interfaces.Unsigned_8;
   type Byte_Count is range 0 .. Long_Long_Integer'Last;
   subtype Byte_Index is Byte_Count range 1 .. Byte_Count'Last;
   type Byte_Array is array (Byte_Index range <>) of Byte;

   --  Little-endian magnitude in caller-owned storage. Host indexes bound
   --  storage, never the numerical value. Empty/leading-zero spans are legal.
   type Quantity is record
      Negative : Boolean;
      First    : Byte_Index;
      Length   : Byte_Count;
   end record;
   type Optional_Quantity (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True  => Value : Quantity;
      end case;
   end record;

   function Span_Valid (Data : Byte_Array; Q : Quantity) return Boolean is
     (Q.Length = 0 or else
        (Q.First in Data'Range and then
         Q.Length <= Data'Last - Q.First + 1));

   function Digit
     (Data : Byte_Array; Q : Quantity; Offset : Byte_Count) return Natural
   with Global => null,
     Post => Digit'Result <= 255 and then
       (if Span_Valid (Data, Q) and then Offset < Q.Length then
          Digit'Result = Natural (Data (Q.First + Offset))
        else Digit'Result = 0);

   function Radix_Power (Exponent : Byte_Count) return Valid_Big_Integer
   with Ghost, Global => null,
     Subprogram_Variant => (Decreases => Exponent),
     Post => Radix_Power'Result >= 1 and then
       (if Exponent = 0 then Radix_Power'Result = 1
        else Radix_Power'Result =
          To_Big_Integer (256) * Radix_Power (Exponent - 1));

   function Prefix_Value
     (Data : Byte_Array; Q : Quantity; Count : Byte_Count)
     return Valid_Big_Integer
   with Ghost, Global => null,
     Subprogram_Variant => (Decreases => Count),
     Post => Prefix_Value'Result >= 0 and then
       (if Count = 0 then Prefix_Value'Result = 0
        else Prefix_Value'Result = Prefix_Value (Data, Q, Count - 1) +
          To_Big_Integer (Digit (Data, Q, Count - 1)) *
          Radix_Power (Count - 1));

   function Magnitude (Data : Byte_Array; Q : Quantity)
      return Valid_Big_Integer
   with Ghost, Global => null,
     Post => Magnitude'Result >= 0 and then Magnitude'Result =
       (if Span_Valid (Data, Q) then Prefix_Value (Data, Q, Q.Length)
        else To_Big_Integer (0));

   function Value (Data : Byte_Array; Q : Quantity)
      return Valid_Big_Integer
   with Ghost, Global => null,
     Post => Value'Result =
       (if Q.Negative then -Magnitude (Data, Q) else Magnitude (Data, Q));

   function Is_Zero (Data : Byte_Array; Q : Quantity) return Boolean
   with Global => null,
     Post => Is_Zero'Result = (Magnitude (Data, Q) = 0);

   function Is_Negative (Data : Byte_Array; Q : Quantity) return Boolean
   with Global => null,
     Post => Is_Negative'Result = (Value (Data, Q) < 0);

   type Ordering is (Invalid, Less, Equal, Greater);
   function Compare (Data : Byte_Array; Left, Right : Quantity)
      return Ordering
   with Global => null,
     Post =>
       (if not Span_Valid (Data, Left) or else
           not Span_Valid (Data, Right) then Compare'Result = Invalid
        elsif Value (Data, Left) < Value (Data, Right) then
           Compare'Result = Less
        elsif Value (Data, Left) > Value (Data, Right) then
           Compare'Result = Greater
        else Compare'Result = Equal);

   --  Total comparison of unsigned magnitudes, independent mathematical Post.
   --  Invalid spans return False; the policy reports their exact field first.
   function Capacity_Fits
     (Data : Byte_Array; Available, Withheld, Floor, Requested : Quantity)
      return Boolean
   with Global => null,
     Post => Capacity_Fits'Result =
       (Span_Valid (Data, Available) and then
        Span_Valid (Data, Withheld) and then Span_Valid (Data, Floor) and then
        Span_Valid (Data, Requested) and then
        Magnitude (Data, Available) >= Magnitude (Data, Withheld) +
          Magnitude (Data, Floor) + Magnitude (Data, Requested));
end Resource_Quantities;
