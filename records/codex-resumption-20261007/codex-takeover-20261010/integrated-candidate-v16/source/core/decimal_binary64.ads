with Evaluation_Pending;
with Interfaces;
with SPARK.Big_Integers;
with Exact_Decimal;

--  Software binary64: no floating operation, foreign conversion, Value/Image,
--  host rounding mode, or caller-computed authorization input.
package Decimal_Binary64 with SPARK_Mode is
   package P renames Evaluation_Pending;
   use SPARK.Big_Integers;
   subtype Bits is Interfaces.Unsigned_64;
   use type Bits;
   use type P.Count;
   Sign_Bit : constant Bits := 16#8000_0000_0000_0000#;
   Infinity : constant Bits := 16#7FF0_0000_0000_0000#;
   Max_Finite : constant Bits := Infinity - 1;
   function Magnitude (B : Bits) return Bits is (B and (Sign_Bit - 1))
     with Global => null;
   function Finite (B : Bits) return Boolean is (Magnitude (B) < Infinity)
     with Global => null;
   type Rational is record
      Numerator : Big_Integer := To_Big_Integer (0);
      Denominator : Big_Integer := To_Big_Integer (1);
   end record;
   function Valid (R : Rational) return Boolean is
     (R.Numerator >= To_Big_Integer (0) and then R.Denominator > To_Big_Integer (0))
     with Global => null;
   package Representation_Conversions is new SPARK.Big_Integers.Unsigned_Conversions (Bits);
   function Numerator_Model (B : Bits) return Big_Integer is
     (if B = Infinity then Exact_Decimal.Power_Model (To_Big_Integer (2), To_Big_Integer (1024))
      elsif B / 16#0010_0000_0000_0000# = 0 then
        Representation_Conversions.To_Big_Integer (B and 16#000F_FFFF_FFFF_FFFF#)
      elsif B / 16#0010_0000_0000_0000# < 1075 then
        Representation_Conversions.To_Big_Integer
          (16#0010_0000_0000_0000# + (B and 16#000F_FFFF_FFFF_FFFF#))
      else Representation_Conversions.To_Big_Integer
          (16#0010_0000_0000_0000# + (B and 16#000F_FFFF_FFFF_FFFF#)) *
        Exact_Decimal.Power_Model (To_Big_Integer (2),
          To_Big_Integer (Integer (B / 16#0010_0000_0000_0000#) - 1075)))
     with Ghost, Global => null, Pre => B <= Infinity;
   function Denominator_Model (B : Bits) return Big_Integer is
     (if B = Infinity or else B / 16#0010_0000_0000_0000# >= 1075 then To_Big_Integer (1)
      elsif B / 16#0010_0000_0000_0000# = 0 then
        Exact_Decimal.Power_Model (To_Big_Integer (2), To_Big_Integer (1074))
      else Exact_Decimal.Power_Model (To_Big_Integer (2),
        To_Big_Integer (1075 - Integer (B / 16#0010_0000_0000_0000#))))
     with Ghost, Global => null, Pre => B <= Infinity;
   --  Infinity is ONLY the virtual next binade value 2**1024 when forming
   --  the maximum finite rounding interval; it is never an admitted result.
   function Value (B : Bits) return Rational
     with Global => null, Pre => B <= Infinity,
       Post => Valid (Value'Result)
         and then Value'Result.Numerator = Numerator_Model (B)
         and then Value'Result.Denominator = Denominator_Model (B);
   function Less (L, R : Rational) return Boolean is
     (L.Numerator * R.Denominator < R.Numerator * L.Denominator)
     with Global => null, Pre => Valid (L) and then Valid (R);
   function Equal (L, R : Rational) return Boolean is
     (L.Numerator * R.Denominator = R.Numerator * L.Denominator)
     with Global => null, Pre => Valid (L) and then Valid (R);
   function Midpoint (L, R : Rational) return Rational
     with Global => null, Pre => Valid (L) and then Valid (R),
       Post => Valid (Midpoint'Result)
         and then Midpoint'Result.Numerator =
           L.Numerator * R.Denominator + R.Numerator * L.Denominator
         and then Midpoint'Result.Denominator =
           To_Big_Integer (2) * L.Denominator * R.Denominator;
   --  Exact closed/open midpoint interval with binary ties-to-even.  Zero's
   --  half-subnormal boundary is included; maximum-finite overflow tie is not.
   function Rounds_To (R : Rational; B : Bits) return Boolean
     with Global => null, Pre => Valid (R) and then B < Infinity;
   function Overflows (R : Rational) return Boolean
     with Global => null, Pre => Valid (R);
   type Conversion is record
      Valid : Boolean := False;
      Encoding : Bits := 0;
   end record;
   No_Conversion : constant Conversion := (False, 0);
   function Round (R : Rational) return Conversion
     with Global => null, Pre => Valid (R),
       Post => (Round'Result.Valid = not Overflows (R)) and then
         (if Round'Result.Valid then Round'Result.Encoding < Infinity
          and then Rounds_To (R, Round'Result.Encoding)
          else Round'Result.Encoding = 0);
   function Decimal_Denotation (N : Exact_Decimal.Number) return Rational
     with Ghost, Global => null, Pre => N.Coefficient >= To_Big_Integer (0),
       Post => Valid (Decimal_Denotation'Result);
   --  These exact-order models avoid materializing astronomically large
   --  powers in executable contracts for zero/extreme-exponent tokens.
   function Input_Finite (N : Exact_Decimal.Number) return Boolean
     with Ghost, Global => null,
       Post => (if Input_Finite'Result then N.Valid and then N.Floating
         and then N.Coefficient >= To_Big_Integer (0)
         and then N.Significant_Digits >= To_Big_Integer (0));
   function Input_Rounds_To (N : Exact_Decimal.Number; B : Bits) return Boolean
     with Ghost, Global => null;
   function Convert (N : Exact_Decimal.Number) return Conversion
     with Global => null,
       Post => Convert'Result.Valid = Input_Finite (N) and then
         (if Convert'Result.Valid then N.Valid and then N.Floating
          and then Finite (Convert'Result.Encoding)
          and then Input_Rounds_To (N, Convert'Result.Encoding)
          and then ((Convert'Result.Encoding >= Sign_Bit) = N.Negative)
          else Convert'Result.Encoding = 0);
   --  Direct virtual-digit layout model transcribed from retained
   --  Python/pystrtod.c format_float_short 'r'/ADD_DOT_0, not Value/Image.
   function Expected_Repr (B : Bits) return String
     with Ghost, Global => null, Pre => Finite (B),
       Post => Expected_Repr'Result'First = 1
         and then Expected_Repr'Result'Length in 3 .. 32;
   --  Repr is the mode-0 nearest shortest decimal with decimal ties-to-even,
   --  then the original Python 'r'/ADD_DOT_0 layout.  32 is a derived binary64
   --  output workspace, NOT an input/token/exponent/depth admission cap.
   function Repr (B : Bits) return String
     with Global => null, Pre => Finite (B),
       Post => Repr'Result'First = 1 and then Repr'Result'Length in 3 .. 32
         and then Repr'Result = Expected_Repr (B);
   function Spelling_Matches (A : P.Bytes; S : P.Span; B : Bits) return Boolean
     with Global => null, Pre => Finite (B),
       Post => (if Spelling_Matches'Result then P.Valid (A, S));
   function Canonical (A : P.Bytes; S : P.Span) return Conversion
     with Global => null,
       Post => (if Canonical'Result.Valid then P.Valid (A, S)
         and then Finite (Canonical'Result.Encoding)
         and then Spelling_Matches (A, S, Canonical'Result.Encoding)
         else Canonical'Result.Encoding = 0);
end Decimal_Binary64;
