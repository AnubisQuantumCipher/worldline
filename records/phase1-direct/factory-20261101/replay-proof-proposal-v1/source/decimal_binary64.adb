package body Decimal_Binary64 with SPARK_Mode is
   package U64_Conversions renames Representation_Conversions;
   Zero : constant Big_Integer := To_Big_Integer (0);
   One : constant Big_Integer := To_Big_Integer (1);
   Two : constant Big_Integer := To_Big_Integer (2);
   Ten : constant Big_Integer := To_Big_Integer (10);
   Fraction_Mask : constant Bits := 16#000F_FFFF_FFFF_FFFF#;
   Hidden_Bit : constant Bits := 16#0010_0000_0000_0000#;

   function Value (B : Bits) return Rational is
      E : constant Natural := Natural (B / Hidden_Bit);
      M : constant Bits := B and Fraction_Mask;
      R : Rational;
      Shift : Integer;
   begin
      if B = Infinity then
         return (Exact_Decimal.Power (2, To_Big_Integer (1024)), One);
      elsif E = 0 then
         return (U64_Conversions.To_Big_Integer (M),
                 Exact_Decimal.Power (2, To_Big_Integer (1074)));
      end if;
      R.Numerator := U64_Conversions.To_Big_Integer (Hidden_Bit + M);
      Shift := Integer (E) - 1075;
      if Shift < 0 then
         R.Denominator := Exact_Decimal.Power (2, To_Big_Integer (-Shift));
      else
         R.Numerator := R.Numerator * Exact_Decimal.Power (2, To_Big_Integer (Shift));
      end if;
      return R;
   end Value;

   function Midpoint (L, R : Rational) return Rational is
     ((L.Numerator * R.Denominator + R.Numerator * L.Denominator,
       Two * L.Denominator * R.Denominator));

   function Rounds_To (R : Rational; B : Bits) return Boolean is
      Upper : constant Rational := Midpoint (Value (B), Value (B + 1));
      Even : constant Boolean := B mod 2 = 0;
   begin
      if not (Less (R, Upper) or else (Even and then Equal (R, Upper))) then
         return False;
      end if;
      if B = 0 then return True; end if;
      declare
         Lower : constant Rational := Midpoint (Value (B - 1), Value (B));
      begin
         return Less (Lower, R) or else (Even and then Equal (R, Lower));
      end;
   end Rounds_To;

   function Overflows (R : Rational) return Boolean is
      Boundary : constant Rational := Midpoint (Value (Max_Finite), Value (Infinity));
   begin
      return not Less (R, Boundary);
   end Overflows;

   function Round (R : Rational) return Conversion is
      Low : Bits := 0;
      High : Bits := Infinity;
      M : Bits;
   begin
      if Overflows (R) then return No_Conversion; end if;
      --  Bracket the exact rational between adjacent ordered encodings.
      --  The upper sentinel denotes 2**1024, never a hardware infinity.
      while High - Low > 1 loop
         pragma Loop_Invariant (Low < High and then High <= Infinity);
         pragma Loop_Invariant (not Less (R, Value (Low)));
         pragma Loop_Invariant (Less (R, Value (High)));
         pragma Loop_Variant (Decreases => High - Low);
         M := Low + (High - Low) / 2;
         if Less (R, Value (M)) then High := M;
         else Low := M;
         end if;
      end loop;
      declare
         Boundary : constant Rational := Midpoint (Value (Low), Value (High));
      begin
         if Less (R, Boundary) or else
           (Equal (R, Boundary) and then Low mod 2 = 0)
         then return (True, Low);
         else
            pragma Assert (High < Infinity);
            return (True, High);
         end if;
      end;
   end Round;

   function Decimal_Denotation (N : Exact_Decimal.Number) return Rational is
     (if N.Exponent < Zero then
        (N.Coefficient, Exact_Decimal.Power (10, -N.Exponent))
      else (N.Coefficient * Exact_Decimal.Power (10, N.Exponent), One));

   function Input_Finite (N : Exact_Decimal.Number) return Boolean is
   begin
      if not N.Valid or else not N.Floating or else N.Coefficient < Zero or else
        N.Significant_Digits < Zero then return False; end if;
      if N.Coefficient = Zero then return True; end if;
      if N.Significant_Digits + N.Exponent > To_Big_Integer (309) then return False;
      elsif N.Significant_Digits + N.Exponent < To_Big_Integer (-323) then return True;
      else return not Overflows (Decimal_Denotation (N));
      end if;
   end Input_Finite;

   function Input_Rounds_To (N : Exact_Decimal.Number; B : Bits) return Boolean is
   begin
      if not Input_Finite (N) or else not Finite (B) or else
        ((B >= Sign_Bit) /= N.Negative) then return False; end if;
      if N.Coefficient = Zero or else
        N.Significant_Digits + N.Exponent < To_Big_Integer (-323)
      then return Magnitude (B) = 0;
      else return Rounds_To (Decimal_Denotation (N), Magnitude (B));
      end if;
   end Input_Rounds_To;

   function Convert (N : Exact_Decimal.Number) return Conversion is
      R : Rational;
      C : Conversion;
      Order : Big_Integer;
   begin
      if not N.Valid or else not N.Floating or else N.Coefficient < Zero
        or else N.Significant_Digits < Zero then return No_Conversion; end if;
      if N.Coefficient = Zero then
         return (True, (if N.Negative then Sign_Bit else 0));
      end if;
      Order := N.Significant_Digits + N.Exponent;
      --  These are mathematical early decisions, not token/exponent caps.
      --  Positive x with order >309 exceeds 10**309 and the overflow
      --  midpoint.  Order <-323 implies x <10**-324 <2**-1075.
      if Order > To_Big_Integer (309) then return No_Conversion;
      elsif Order < To_Big_Integer (-323) then
         return (True, (if N.Negative then Sign_Bit else 0));
      end if;
      R.Numerator := N.Coefficient;
      if N.Exponent < Zero then
         R.Denominator := Exact_Decimal.Power (10, -N.Exponent);
      else
         R.Numerator := R.Numerator * Exact_Decimal.Power (10, N.Exponent);
      end if;
      C := Round (R);
      if C.Valid and then N.Negative then C.Encoding := C.Encoding or Sign_Bit; end if;
      return C;
   end Convert;

   --  Candidate is on the decimal lattice Q * 10**E.  The two neighbours
   --  of the exact value are inspected separately: binary power-of-two
   --  rounding intervals are asymmetric, so nearest alone is insufficient.
   type Decimal_Image is record
      Found : Boolean := False;
      Coefficient : Big_Integer := Zero;
      Exponent : Integer := 0;
      Precision : Natural := 0;
   end record;
   function Decimal_Value (Q : Big_Integer; E : Integer) return Rational
     with Global => null, Pre => Q >= Zero and then E in -340 .. 309,
       Post => Valid (Decimal_Value'Result)
   is
   begin
      if E < 0 then return (Q, Exact_Decimal.Power (10, To_Big_Integer (-E)));
      else return (Q * Exact_Decimal.Power (10, To_Big_Integer (E)), One);
      end if;
   end Decimal_Value;

   --  Independent nearest-member reference on the exact decimal lattice.
   --  Only floor/ceiling can be nearest; membership handles asymmetric
   --  binary intervals before residual distance and decimal parity decide.
   function Nearest_Coefficient (B : Bits; E : Integer) return Big_Integer
     with Ghost, Global => null,
       Pre => B > 0 and then B < Infinity and then E in -340 .. 308,
       Post => Nearest_Coefficient'Result >= Zero
   is
      V : constant Rational := Value (B);
      N : constant Big_Integer := (if E < 0 then
        V.Numerator * Exact_Decimal.Power (10, To_Big_Integer (-E)) else V.Numerator);
      D : constant Big_Integer := (if E >= 0 then
        V.Denominator * Exact_Decimal.Power (10, To_Big_Integer (E)) else V.Denominator);
      Q : constant Big_Integer := N / D;
      Residual : constant Big_Integer := N mod D;
      Down : constant Boolean := Q > Zero and then Rounds_To (Decimal_Value (Q, E), B);
      Up : constant Boolean := Rounds_To (Decimal_Value (Q + One, E), B);
   begin
      if Down and then (not Up or else Two * Residual < D or else
        (Two * Residual = D and then Q mod Two = Zero)) then return Q;
      elsif Up then return Q + One;
      else return Zero;
      end if;
   end Nearest_Coefficient;

   function Candidate (B : Bits; E : Integer) return Decimal_Image
     with Global => null, Pre => B > 0 and then B < Infinity and then E in -340 .. 308,
       Post => Candidate'Result.Coefficient = Nearest_Coefficient (B, E)
         and then Candidate'Result.Found = (Candidate'Result.Coefficient > Zero)
         and then Candidate'Result.Exponent = E
         and then (if Candidate'Result.Found then
           Rounds_To (Decimal_Value (Candidate'Result.Coefficient, E), B))
   is
      V : constant Rational := Value (B);
      N : Big_Integer := V.Numerator;
      D : Big_Integer := V.Denominator;
      Q, Residual : Big_Integer;
      Down, Up : Boolean;
   begin
      if E < 0 then N := N * Exact_Decimal.Power (10, To_Big_Integer (-E));
      else D := D * Exact_Decimal.Power (10, To_Big_Integer (E)); end if;
      Q := N / D;
      Residual := N mod D;
      Down := Q > Zero and then Rounds_To (Decimal_Value (Q, E), B);
      Up := Rounds_To (Decimal_Value (Q + One, E), B);
      if Down and then (not Up or else Residual * Two < D or else
        (Residual * Two = D and then Q mod Two = Zero))
      then return (True, Q, E, 0);
      elsif Up then return (True, Q + One, E, 0);
      else return (False, Zero, E, 0);
      end if;
   end Candidate;

   function Decimal_Exponent (B : Bits) return Integer
     with Global => null, Pre => B > 0 and then B < Infinity,
       Post => Decimal_Exponent'Result in -324 .. 308
         and then not Less (Value (B), Decimal_Value (One, Decimal_Exponent'Result))
         and then Less (Value (B), Decimal_Value (One, Decimal_Exponent'Result + 1))
   is
      V : constant Rational := Value (B);
      N : Big_Integer := V.Numerator;
      D : Big_Integer := V.Denominator;
      K : Integer := 0;
   begin
      while N < D loop
         pragma Loop_Invariant (K in -324 .. 0);
         pragma Loop_Invariant (N > Zero and then D > Zero);
         pragma Loop_Variant (Decreases => K + 324);
         pragma Assert (K > -324);
         N := N * Ten;
         K := K - 1;
      end loop;
      while N >= D * Ten loop
         pragma Loop_Invariant (K in -324 .. 308);
         pragma Loop_Invariant (N > Zero and then D > Zero);
         pragma Loop_Variant (Decreases => 308 - K);
         pragma Assert (K < 308);
         D := D * Ten;
         K := K + 1;
      end loop;
      return K;
   end Decimal_Exponent;

   function Shortest (B : Bits) return Decimal_Image
     with Global => null, Pre => B > 0 and then B < Infinity,
       Post => Shortest'Result.Found and then Shortest'Result.Coefficient > Zero
         and then Shortest'Result.Coefficient < Exact_Decimal.Power (10, To_Big_Integer (17))
         and then Shortest'Result.Exponent in -340 .. 308
         and then Shortest'Result.Precision in 1 .. 17
         and then Candidate (B,
           Decimal_Exponent (B) - Shortest'Result.Precision + 1).Found
         and then (for all P in 1 .. Shortest'Result.Precision - 1 =>
           not Candidate (B, Decimal_Exponent (B) - P + 1).Found)
         and then Equal
           (Decimal_Value (Shortest'Result.Coefficient, Shortest'Result.Exponent),
            Decimal_Value
              (Candidate (B, Decimal_Exponent (B) -
                Shortest'Result.Precision + 1).Coefficient,
               Decimal_Exponent (B) - Shortest'Result.Precision + 1))
         and then Rounds_To (Decimal_Value
           (Shortest'Result.Coefficient, Shortest'Result.Exponent), B)
   is
      K : constant Integer := Decimal_Exponent (B);
      C : Decimal_Image;
      Precision : Positive := 1;
   begin
      loop
         pragma Loop_Invariant (Precision in 1 .. 17);
         pragma Loop_Invariant
           (for all P in 1 .. Precision - 1 => not Candidate (B, K - P + 1).Found);
         pragma Loop_Variant (Decreases => 17 - Precision);
         C := Candidate (B, K - Precision + 1);
         exit when C.Found;
         --  Binary64 has at most 53 significand bits.  A 17-digit nearest
         --  decimal has error below both half-ULPs, including the narrower
         --  lower interval of a power of two.  This is a proof obligation,
         --  not an assumed claim or an alternate refusal at this boundary.
         pragma Assert (Precision < 17);
         Precision := Precision + 1;
      end loop;
      C.Precision := Precision;
      --  dtoa mode 0 suppresses trailing zeros, including rounding carry.
      while C.Coefficient mod Ten = Zero loop
         pragma Loop_Invariant (C.Coefficient > Zero);
         pragma Loop_Invariant (C.Exponent in -340 .. 308);
         pragma Loop_Invariant (C.Precision = Precision);
         pragma Loop_Invariant (Rounds_To (Decimal_Value (C.Coefficient, C.Exponent), B));
         pragma Loop_Invariant
           (Equal (Decimal_Value (C.Coefficient, C.Exponent),
                   Decimal_Value (Candidate (B, K - Precision + 1).Coefficient,
                                  K - Precision + 1)));
         pragma Loop_Variant (Decreases => C.Coefficient);
         pragma Assert (C.Exponent < 308);
         C.Coefficient := C.Coefficient / Ten;
         C.Exponent := C.Exponent + 1;
      end loop;
      return C;
   end Shortest;

   procedure Append (Buffer : in out String; Used : in out Natural; C : Character)
     with Global => null,
       Pre => Buffer'First = 1 and then Used < Buffer'Length,
       Post => Used = Used'Old + 1 and then Buffer (Used) = C
   is
   begin
      Used := Used + 1;
      Buffer (Used) := C;
   end Append;

   procedure Model_Append (Buffer : in out String; Used : in out Natural; C : Character)
     with Ghost, Global => null,
       Pre => Buffer'First = 1 and then Used < Buffer'Length,
       Post => Used = Used'Old + 1 and then Buffer (Used) = C
   is
   begin
      Used := Used + 1;
      Buffer (Used) := C;
   end Model_Append;

   function Expected_Repr (B : Bits) return String is
      M : constant Bits := Magnitude (B);
      C : Decimal_Image;
      Coefficient_Digits : String (1 .. 17) := (others => '0');
      Start : Natural := 18;
      Buffer : String (1 .. 32) := (others => ' ');
      Used : Natural := 0;
      Q : Big_Integer;
      Length, Point, Virtual_Start, Virtual_End : Integer;
      Use_Exponent : Boolean;
      Exponent : Integer := 0;
      Abs_Exponent : Natural;
   begin
      if M = 0 then return (if B >= Sign_Bit then "-0.0" else "0.0"); end if;
      C := Shortest (M);
      Q := C.Coefficient;
      while Q > Zero loop
         pragma Loop_Invariant (Start in 1 .. 18);
         pragma Loop_Invariant (Q >= Zero);
         pragma Loop_Invariant (Q < Exact_Decimal.Power (10, To_Big_Integer (Start - 1)));
         pragma Loop_Variant (Decreases => Q);
         pragma Assert (Start > 1);
         Start := Start - 1;
         Coefficient_Digits (Start) :=
           Character'Val (Character'Pos ('0') + To_Integer (Q mod Ten));
         Q := Q / Ten;
      end loop;
      Length := 18 - Start;
      Point := Length + C.Exponent;
      Use_Exponent := Point <= -4 or else Point > 16;
      if Use_Exponent then Exponent := Point - 1; Point := 1; end if;
      Virtual_Start := (if Point <= 0 then Point - 1 else 0);
      Virtual_End := Integer'Max (Length, (if Use_Exponent then Point else Point + 1));
      if B >= Sign_Bit then Model_Append (Buffer, Used, '-'); end if;
      --  Source's virtual decimal digit string padded with zeros on each side.
      for I in Virtual_Start .. Virtual_End - 1 loop
         pragma Loop_Invariant (Used < 25);
         Model_Append (Buffer, Used,
           (if I >= 0 and then I < Length then Coefficient_Digits (Start + I) else '0'));
         if I + 1 = Point and then (I + 1 < Virtual_End or else not Use_Exponent) then
            Model_Append (Buffer, Used, '.');
         end if;
      end loop;
      if Use_Exponent then
         Model_Append (Buffer, Used, 'e');
         Model_Append (Buffer, Used, (if Exponent < 0 then '-' else '+'));
         Abs_Exponent := abs Exponent;
         pragma Assert (Abs_Exponent <= 324);
         if Abs_Exponent >= 100 then
            Model_Append (Buffer, Used,
              Character'Val (Character'Pos ('0') + Abs_Exponent / 100));
         end if;
         Model_Append (Buffer, Used,
           Character'Val (Character'Pos ('0') + (Abs_Exponent / 10) mod 10));
         Model_Append (Buffer, Used,
           Character'Val (Character'Pos ('0') + Abs_Exponent mod 10));
      end if;
      return Buffer (1 .. Used);
   end Expected_Repr;

   function Repr (B : Bits) return String is
      M : constant Bits := Magnitude (B);
      C : Decimal_Image;
      Decimal_Digits : String (1 .. 17) := (others => '0');
      Start : Natural := 18;
      Buffer : String (1 .. 32) := (others => ' ');
      Used : Natural := 0;
      Q : Big_Integer;
      Length, Decimal_Point : Integer;
      Scientific : Boolean;
      Exponent : Integer;
      Abs_Exponent : Natural;
   begin
      if M = 0 then return (if B >= Sign_Bit then "-0.0" else "0.0"); end if;
      C := Shortest (M);
      Q := C.Coefficient;
      while Q > Zero loop
         pragma Loop_Invariant (Start in 1 .. 18);
         pragma Loop_Invariant (Q >= Zero);
         pragma Loop_Variant (Decreases => Q);
         pragma Assert (Start > 1);
         Start := Start - 1;
         Decimal_Digits (Start) := Character'Val (Character'Pos ('0') + To_Integer (Q mod Ten));
         Q := Q / Ten;
      end loop;
      Length := 18 - Start;
      Decimal_Point := Length + C.Exponent;
      Scientific := Decimal_Point <= -4 or else Decimal_Point > 16;
      if B >= Sign_Bit then Append (Buffer, Used, '-'); end if;
      if Scientific then
         Append (Buffer, Used, Decimal_Digits (Start));
         if Length > 1 then
            Append (Buffer, Used, '.');
            for I in Start + 1 .. 17 loop
               pragma Loop_Invariant (Used < 20);
               Append (Buffer, Used, Decimal_Digits (I));
            end loop;
         end if;
         Exponent := Decimal_Point - 1;
         Append (Buffer, Used, 'e');
         Append (Buffer, Used, (if Exponent < 0 then '-' else '+'));
         Abs_Exponent := abs Exponent;
         pragma Assert (Abs_Exponent <= 324);
         if Abs_Exponent >= 100 then
            Append (Buffer, Used, Character'Val (Character'Pos ('0') + Abs_Exponent / 100));
         end if;
         Append (Buffer, Used, Character'Val (Character'Pos ('0') + (Abs_Exponent / 10) mod 10));
         Append (Buffer, Used, Character'Val (Character'Pos ('0') + Abs_Exponent mod 10));
      elsif Decimal_Point <= 0 then
         Append (Buffer, Used, '0');
         Append (Buffer, Used, '.');
         for I in 1 .. -Decimal_Point loop
            pragma Loop_Invariant (Used < 8);
            Append (Buffer, Used, '0');
         end loop;
         for I in Start .. 17 loop
            pragma Loop_Invariant (Used < 25);
            Append (Buffer, Used, Decimal_Digits (I));
         end loop;
      else
         for I in 1 .. Integer'Max (Decimal_Point, Length) loop
            pragma Loop_Invariant (Used < 25);
            if I <= Length then Append (Buffer, Used, Decimal_Digits (Start + I - 1));
            else Append (Buffer, Used, '0'); end if;
            if I = Decimal_Point then Append (Buffer, Used, '.'); end if;
         end loop;
         if Decimal_Point >= Length then Append (Buffer, Used, '0'); end if;
      end if;
      return Buffer (1 .. Used);
   end Repr;

   function Spelling_Matches (A : P.Bytes; S : P.Span; B : Bits) return Boolean is
      Text : constant String := Repr (B);
   begin
      return P.Valid (A, S) and then S.Length = P.Count (Text'Length) and then
        (for all K in Text'Range =>
           Natural (A (S.First + P.Count (K - Text'First))) = Character'Pos (Text (K)));
   end Spelling_Matches;

   function Canonical (A : P.Bytes; S : P.Span) return Conversion is
      N : constant Exact_Decimal.Number := Exact_Decimal.Parse (A, S, 0);
      C : Conversion;
   begin
      if not N.Valid or else N.After /= S.Length or else not N.Floating then
         return No_Conversion;
      end if;
      C := Convert (N);
      if not C.Valid or else not Spelling_Matches (A, S, C.Encoding) then
         return No_Conversion;
      end if;
      return C;
   end Canonical;
end Decimal_Binary64;
