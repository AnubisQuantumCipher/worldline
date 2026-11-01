with Evaluation_Pending;
with SPARK.Big_Integers;

--  JSON number lexing and exact, unbounded decimal arithmetic.  No machine
--  exponent, token-length or significand bound is an admission condition.
package Exact_Decimal with SPARK_Mode is
   package P renames Evaluation_Pending;
   use SPARK.Big_Integers;
   use type P.Count;
   type Number is record
      Valid, Negative, Floating : Boolean := False;
      After, Mantissa_After : P.Count := 0;
      Coefficient : Big_Integer := To_Big_Integer (0);
      Exponent : Big_Integer := To_Big_Integer (0);
      Significant_Digits : Big_Integer := To_Big_Integer (0);
   end record;
   No_Number : constant Number :=
     (Valid => False, Negative => False, Floating => False,
      After => 0, Mantissa_After => 0, Coefficient => To_Big_Integer (0),
      Exponent => To_Big_Integer (0), Significant_Digits => To_Big_Integer (0));
   function Digit (A : P.Bytes; S : P.Span; O : P.Count) return Integer
     with Global => null, Post => Digit'Result in -1 .. 9;
   --  Independent denotation models. Non-digits contribute no coefficient;
   --  Parse separately establishes JSON syntax and the mantissa boundary.
   function Digit_Fold (A : P.Bytes; S : P.Span; First, After : P.Count)
     return Big_Integer
     with Ghost, Global => null,
       Pre => P.Valid (A, S) and then First <= After and then After <= S.Length,
       Post => Digit_Fold'Result >= To_Big_Integer (0);
   function Fraction_Digits (A : P.Bytes; S : P.Span; First, After : P.Count)
     return Big_Integer
     with Ghost, Global => null,
       Pre => P.Valid (A, S) and then First <= After and then After <= S.Length,
       Post => Fraction_Digits'Result >= To_Big_Integer (0);
   function Exponent_Value (A : P.Bytes; S : P.Span; First, After : P.Count)
     return Big_Integer
     with Ghost, Global => null,
       Pre => P.Valid (A, S) and then First <= After and then After <= S.Length;
   function Digit_Count (Coefficient : Big_Integer) return Big_Integer
     with Ghost, Global => null, Pre => Coefficient >= To_Big_Integer (0),
       Post => Digit_Count'Result >= To_Big_Integer (0);
   --  Consume the maximal JSON number prefix, without accepting whitespace,
   --  leading '+', leading integer zeros, or incomplete fraction/exponent.
   --  Value magnitude is Coefficient * 10 ** Exponent.  Fraction/exponent
   --  syntax is a distinct type even when its magnitude is an integer or zero.
   function Parse (A : P.Bytes; S : P.Span; From : P.Count) return Number
     with Global => null,
       Post => (if Parse'Result.Valid then
         P.Valid (A, S) and then From < Parse'Result.After
         and then Parse'Result.After <= S.Length
         and then From < Parse'Result.Mantissa_After
         and then Parse'Result.Mantissa_After <= Parse'Result.After
         and then Parse'Result.Coefficient =
           Digit_Fold (A, S, From, Parse'Result.Mantissa_After)
         and then Parse'Result.Exponent =
           Exponent_Value (A, S, Parse'Result.Mantissa_After, Parse'Result.After) -
           Fraction_Digits (A, S, From, Parse'Result.Mantissa_After)
         and then Parse'Result.Significant_Digits = Digit_Count (Parse'Result.Coefficient)
         and then Parse'Result.Negative =
           (Natural (A (S.First + From)) = Character'Pos ('-'))
         and then Parse'Result.Floating =
           (Parse'Result.Mantissa_After < Parse'Result.After or else
             (for some O in From .. Parse'Result.Mantissa_After - 1 =>
               Natural (A (S.First + O)) = Character'Pos ('.')))
         and then Parse'Result.Coefficient >= To_Big_Integer (0)
         and then Parse'Result.Significant_Digits >= To_Big_Integer (0)
         and then ((Parse'Result.Coefficient = To_Big_Integer (0)) =
                   (Parse'Result.Significant_Digits = To_Big_Integer (0))));
   --  Independent exact recurrence used by the executable power contract.
   function Power_Model (Base, Exponent : Big_Integer) return Big_Integer
     with Ghost, Global => null,
       Pre => Base >= To_Big_Integer (1) and then Exponent >= To_Big_Integer (0),
       Post => Power_Model'Result >= To_Big_Integer (1),
       Subprogram_Variant => (Decreases => Exponent);
   --  Exponentiation by squaring: the loop variant is the nonnegative exact
   --  exponent, not a conversion to Natural/Integer or a finite input cap.
   function Power (Base : Positive; Exponent : Big_Integer) return Big_Integer
     with Global => null, Pre => Exponent >= To_Big_Integer (0),
       Post => Power'Result >= To_Big_Integer (1) and then
         Power'Result = Power_Model (To_Big_Integer (Base), Exponent);
end Exact_Decimal;
