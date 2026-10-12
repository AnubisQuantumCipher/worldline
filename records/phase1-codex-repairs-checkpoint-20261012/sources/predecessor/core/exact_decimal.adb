package body Exact_Decimal with SPARK_Mode is
   package Count_Conversions is new SPARK.Big_Integers.Signed_Conversions (P.Count);
   Zero : constant Big_Integer := To_Big_Integer (0);
   Ten : constant Big_Integer := To_Big_Integer (10);
   function Byte_At (A : P.Bytes; S : P.Span; O : P.Count) return Natural is
     (if P.Valid (A, S) and then O < S.Length
      then Natural (A (S.First + O)) else 0)
     with Global => null, Post => Byte_At'Result <= 255;
   function Digit (A : P.Bytes; S : P.Span; O : P.Count) return Integer is
      C : constant Natural := Byte_At (A, S, O);
   begin
      if not P.Valid (A, S) or else O >= S.Length or else
        C not in Character'Pos ('0') .. Character'Pos ('9')
      then return -1; end if;
      return C - Character'Pos ('0');
   end Digit;

   function Digit_Fold (A : P.Bytes; S : P.Span; First, After : P.Count)
     return Big_Integer
   is
      O : P.Count := First;
      Result : Big_Integer := To_Big_Integer (0);
   begin
      while O < After loop
         pragma Loop_Invariant (First <= O and then O <= After);
         pragma Loop_Invariant (Result >= To_Big_Integer (0));
         pragma Loop_Variant (Decreases => After - O);
         if Digit (A, S, O) >= 0 then
            Result := Result * To_Big_Integer (10) + To_Big_Integer (Digit (A, S, O));
         end if;
         O := O + 1;
      end loop;
      return Result;
   end Digit_Fold;

   function Fraction_Digits (A : P.Bytes; S : P.Span; First, After : P.Count)
     return Big_Integer
   is
      O : P.Count := First;
      Result : Big_Integer := To_Big_Integer (0);
      Fraction : Boolean := False;
   begin
      while O < After loop
         pragma Loop_Invariant (First <= O and then O <= After);
         pragma Loop_Invariant (Result >= To_Big_Integer (0));
         pragma Loop_Variant (Decreases => After - O);
         if Byte_At (A, S, O) = Character'Pos ('.') then Fraction := True;
         elsif Fraction and then Digit (A, S, O) >= 0 then
            Result := Result + To_Big_Integer (1);
         end if;
         O := O + 1;
      end loop;
      return Result;
   end Fraction_Digits;

   function Exponent_Value (A : P.Bytes; S : P.Span; First, After : P.Count)
     return Big_Integer
   is
      V : constant Big_Integer := Digit_Fold (A, S, First, After);
   begin
      if After - First > 1 and then Byte_At (A, S, First + 1) = Character'Pos ('-') then
         return -V;
      end if;
      return V;
   end Exponent_Value;

   function Digit_Count (Coefficient : Big_Integer) return Big_Integer is
      Q : Big_Integer := Coefficient;
      Result : Big_Integer := To_Big_Integer (0);
   begin
      while Q > To_Big_Integer (0) loop
         pragma Loop_Invariant (Q >= To_Big_Integer (0));
         pragma Loop_Invariant (Result >= To_Big_Integer (0));
         pragma Loop_Variant (Decreases => Q);
         Q := Q / To_Big_Integer (10);
         Result := Result + To_Big_Integer (1);
      end loop;
      return Result;
   end Digit_Count;

   function Parse (A : P.Bytes; S : P.Span; From : P.Count) return Number is
      N : Number := No_Number;
      O : P.Count := From;
      Exp : Big_Integer := Zero;
      Fraction, Significant : P.Count := 0;
      Exp_Negative : Boolean := False;
      D : Integer;
      procedure Accumulate
        (N : in out Number; Significant : in out P.Count; Value : Integer)
        with Global => null,
          Pre => Value in 0 .. 9 and then N.Coefficient >= Zero
            and then Significant < P.Count'Last
            and then ((N.Coefficient = Zero) = (Significant = 0)),
          Post => N.Coefficient = N.Coefficient'Old * Ten + To_Big_Integer (Value)
            and then N.Coefficient >= Zero
            and then Significant = Significant'Old +
              (if N.Coefficient = Zero then 0 else 1)
            and then ((N.Coefficient = Zero) = (Significant = 0))
      is
      begin
         if N.Coefficient = Zero and then Value = 0 then return; end if;
         if Value = 0 then N.Coefficient := N.Coefficient * Ten;
         else N.Coefficient := N.Coefficient * Ten + To_Big_Integer (Value);
         end if;
         Significant := Significant + 1;
      end Accumulate;
   begin
      if not P.Valid (A, S) or else From >= S.Length then return No_Number; end if;
      if Byte_At (A, S, O) = Character'Pos ('-') then
         N.Negative := True;
         O := O + 1;
         if O = S.Length then return No_Number; end if;
      end if;
      D := Digit (A, S, O);
      if D = 0 then
         O := O + 1;
         if Digit (A, S, O) >= 0 then return No_Number; end if;
      elsif D in 1 .. 9 then
         while O < S.Length and then Digit (A, S, O) >= 0 loop
            pragma Loop_Invariant (P.Valid (A, S) and then From <= O and then O <= S.Length);
            pragma Loop_Invariant (N.Coefficient >= To_Big_Integer (0));
            pragma Loop_Invariant (Significant <= O);
            pragma Loop_Invariant ((N.Coefficient = Zero) = (Significant = 0));
            pragma Loop_Variant (Decreases => S.Length - O);
            Accumulate (N, Significant, Digit (A, S, O));
            O := O + 1;
         end loop;
      else return No_Number;
      end if;
      if O < S.Length and then Byte_At (A, S, O) = Character'Pos ('.') then
         N.Floating := True;
         O := O + 1;
         if Digit (A, S, O) < 0 then return No_Number; end if;
         while O < S.Length and then Digit (A, S, O) >= 0 loop
            pragma Loop_Invariant (P.Valid (A, S) and then From < O and then O <= S.Length);
            pragma Loop_Invariant (Fraction <= O);
            pragma Loop_Invariant (N.Coefficient >= To_Big_Integer (0));
            pragma Loop_Invariant (Significant <= O);
            pragma Loop_Invariant ((N.Coefficient = Zero) = (Significant = 0));
            pragma Loop_Variant (Decreases => S.Length - O);
            Accumulate (N, Significant, Digit (A, S, O));
            Fraction := Fraction + 1;
            O := O + 1;
         end loop;
      end if;
      N.Mantissa_After := O;
      if O < S.Length and then Byte_At (A, S, O) in Character'Pos ('e') | Character'Pos ('E') then
         N.Floating := True;
         O := O + 1;
         if O < S.Length and then Byte_At (A, S, O) in Character'Pos ('+') | Character'Pos ('-') then
            Exp_Negative := Byte_At (A, S, O) = Character'Pos ('-');
            O := O + 1;
         end if;
         if Digit (A, S, O) < 0 then return No_Number; end if;
         while O < S.Length and then Digit (A, S, O) >= 0 loop
            pragma Loop_Invariant (P.Valid (A, S) and then From < O and then O <= S.Length);
            pragma Loop_Invariant (Exp >= To_Big_Integer (0));
            pragma Loop_Variant (Decreases => S.Length - O);
            D := Digit (A, S, O);
            if D > 0 then Exp := Exp * Ten + To_Big_Integer (D);
            elsif Exp /= Zero then Exp := Exp * Ten;
            end if;
            O := O + 1;
         end loop;
      end if;
      N.Exponent := (if Exp_Negative then -Exp else Exp) -
        Count_Conversions.To_Big_Integer (Fraction);
      N.Significant_Digits := Count_Conversions.To_Big_Integer (Significant);
      N.After := O;
      N.Valid := True;
      return N;
   end Parse;

   function Power_Model (Base, Exponent : Big_Integer) return Big_Integer is
     (if Exponent = To_Big_Integer (0) then To_Big_Integer (1)
      elsif Exponent mod To_Big_Integer (2) = To_Big_Integer (0) then
        Power_Model (Base, Exponent / To_Big_Integer (2)) ** 2
      else Base * Power_Model (Base, Exponent / To_Big_Integer (2)) ** 2);

   function Power (Base : Positive; Exponent : Big_Integer) return Big_Integer is
      E : Big_Integer := Exponent;
      Factor : Big_Integer := To_Big_Integer (Base);
      Result : Big_Integer := To_Big_Integer (1);
   begin
      while E > To_Big_Integer (0) loop
         pragma Loop_Invariant (E >= To_Big_Integer (0));
         pragma Loop_Invariant (Factor >= To_Big_Integer (1));
         pragma Loop_Invariant (Result >= To_Big_Integer (1));
         pragma Loop_Invariant
           (Result * Power_Model (Factor, E) =
            Power_Model (To_Big_Integer (Base), Exponent));
         pragma Loop_Variant (Decreases => E);
         if E mod To_Big_Integer (2) = To_Big_Integer (1) then
            Result := Result * Factor;
         end if;
         E := E / To_Big_Integer (2);
         if E > To_Big_Integer (0) then Factor := Factor * Factor; end if;
      end loop;
      return Result;
   end Power;
end Exact_Decimal;
