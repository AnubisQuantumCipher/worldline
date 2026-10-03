package body Worldline.Resources with SPARK_Mode is
   use type Byte;

   --  Every lemma below has an ordinary checked Ghost body. Its Post,
   --  call-site Pre, recursion and arithmetic remain proof obligations.
   --  Keep a complete quotient witness instead of asking the solver to infer
   --  divisibility directly from recursive powers.  This is a candidate lemma
   --  with an actual body, not an imported or assumed arithmetic theorem.
   function Power_Quotient (Low, High : Byte_Count) return Big_Positive
     with Ghost, Global => null,
          Pre => Low <= High,
          Post => Radix_Power (High) =
            Radix_Power (Low) * Power_Quotient'Result,
          Subprogram_Variant => (Decreases => High)
   is
   begin
      if Low = High then
         return 1;
      else
         declare
            Previous : constant Big_Positive :=
              Power_Quotient (Low, High - 1);
         begin
            pragma Assert
              (Radix_Power (High - 1) = Radix_Power (Low) * Previous);
            pragma Assert
              (Radix_Power (High) = 256 * Radix_Power (High - 1));
            return 256 * Previous;
         end;
      end if;
   end Power_Quotient;

   function Prefix_Quotient
     (Value : Byte_Array; Low, High : Byte_Count) return Big_Natural
     with Ghost, Global => null,
          Pre => Low <= High,
          Post => Prefix_Value (Value, High) = Prefix_Value (Value, Low)
            + Radix_Power (Low) * Prefix_Quotient'Result,
          Subprogram_Variant => (Decreases => High)
   is
   begin
      if Low = High then
         return 0;
      else
         declare
            Previous : constant Big_Natural :=
              Prefix_Quotient (Value, Low, High - 1);
            Position : constant Big_Positive :=
              Power_Quotient (Low, High - 1);
            Digit : constant Big_Natural :=
              To_Big_Integer (Digit_At (Value, High - 1));
         begin
            pragma Assert
              (Prefix_Value (Value, High - 1) = Prefix_Value (Value, Low)
               + Radix_Power (Low) * Previous);
            pragma Assert
              (Radix_Power (High - 1) = Radix_Power (Low) * Position);
            pragma Assert
              (Prefix_Value (Value, High) = Prefix_Value (Value, High - 1)
               + Digit * Radix_Power (High - 1));
            return Previous + Digit * Position;
         end;
      end if;
   end Prefix_Quotient;

   --  Source-equivalent scalar witness bodies from Evaluation_Epoch, adapted
   --  by lexical visibility to this package's Ada Big_Integer type. They are
   --  total checked Ghost procedures, not imported facts. Every body, Post,
   --  division, validity check and caller remains a proof obligation. No new
   --  recursion or byte-prefix traversal is introduced by these procedures.
   procedure Positive_Multiple
     (Place, Multiplier : Valid_Big_Integer)
   with Ghost, Global => null, Always_Terminates,
     Post => (if Place > 0 and then Multiplier >= 1 then
       Place * Multiplier >= Place)
   is
   begin
      if Place <= 0 or else Multiplier < 1 then
         return;
      end if;
      declare
         Excess : constant Valid_Big_Integer := Multiplier - 1;
         Contribution : constant Valid_Big_Integer := Place * Excess;
      begin
         pragma Assert (Excess >= 0);
         pragma Assert (Contribution >= 0);
         pragma Assert (Place * Multiplier = Place + Contribution);
         pragma Assert (Place * Multiplier >= Place);
      end;
   end Positive_Multiple;

   procedure Remainder_From_Witness
     (Low, Place, Tail : Valid_Big_Integer)
   with Ghost, Global => null, Always_Terminates,
     Post => (if Place > 0 and then Low >= 0 and then Low < Place
                  and then Tail >= 0 then
       (Low + Place * Tail) / Place = Tail and then
       (Low + Place * Tail) mod Place = Low)
   is
   begin
      if Place <= 0 or else Low < 0 or else Low >= Place or else Tail < 0 then
         return;
      end if;
      declare
         Whole : constant Valid_Big_Integer := Low + Place * Tail;
         Quotient : constant Valid_Big_Integer := Whole / Place;
         Remainder : constant Valid_Big_Integer := Whole mod Place;
      begin
         pragma Assert (Whole >= 0);
         pragma Assert (Quotient >= 0);
         pragma Assert (Remainder >= 0 and then Remainder < Place);
         pragma Assert (Whole = Place * Quotient + Remainder);
         if Quotient < Tail then
            declare
               Difference : constant Valid_Big_Integer := Tail - Quotient;
            begin
               pragma Assert (Difference >= 1);
               Positive_Multiple (Place, Difference);
               pragma Assert
                 (Place * Tail = Place * Quotient + Place * Difference);
               pragma Assert (Remainder = Low + Place * Difference);
               pragma Assert (Remainder >= Place);
               pragma Assert (False);
            end;
         elsif Quotient > Tail then
            declare
               Difference : constant Valid_Big_Integer := Quotient - Tail;
            begin
               pragma Assert (Difference >= 1);
               Positive_Multiple (Place, Difference);
               pragma Assert
                 (Place * Quotient = Place * Tail + Place * Difference);
               pragma Assert (Low = Remainder + Place * Difference);
               pragma Assert (Low >= Place);
               pragma Assert (False);
            end;
         end if;
         pragma Assert (Quotient = Tail);
         pragma Assert (Remainder = Low);
      end;
   end Remainder_From_Witness;

   procedure Power_Order (Low, High : Byte_Count)
     with Ghost, Global => null, Always_Terminates,
          Pre => Low <= High,
          Post => Radix_Power (Low) <= Radix_Power (High)
            and then Radix_Power (High) mod Radix_Power (Low) = 0,
          Subprogram_Variant => (Decreases => High)
   is
      Quotient : constant Big_Positive := Power_Quotient (Low, High);
   begin
      if Low < High then
         Power_Order (Low, High - 1);
      end if;
      pragma Assert
        (Radix_Power (High) = Radix_Power (Low) * Quotient);
      Positive_Multiple (Radix_Power (Low), Quotient);
      Remainder_From_Witness (0, Radix_Power (Low), Quotient);
      pragma Assert
        (Radix_Power (High) mod Radix_Power (Low) = 0);
   end Power_Order;

   procedure Complete_Prefix (Value : Byte_Array; Count : Byte_Count)
     with Ghost, Global => null, Always_Terminates,
          Pre => Count >= Value'Length,
          Post => Prefix_Value (Value, Count) = Magnitude (Value),
          Subprogram_Variant => (Decreases => Count)
   is
   begin
      if Count > Value'Length then
         Complete_Prefix (Value, Count - 1);
      end if;
   end Complete_Prefix;

   procedure Prefix_Growth (Value : Byte_Array; Low, High : Byte_Count)
     with Ghost, Global => null, Always_Terminates,
          Pre => Low <= High,
          Post => Prefix_Value (Value, Low) <= Prefix_Value (Value, High)
            and then
              (if Prefix_Value (Value, High) < Radix_Power (Low) then
                 Prefix_Value (Value, Low) = Prefix_Value (Value, High)),
          Subprogram_Variant => (Decreases => High)
   is
   begin
      if Low < High then
         Prefix_Growth (Value, Low, High - 1);
         Power_Order (Low, High - 1);
      end if;
   end Prefix_Growth;

   procedure Low_Prefix_Exact (Value : Byte_Array; Count : Byte_Count)
     with Ghost, Global => null, Always_Terminates,
          Post => (if Magnitude (Value) < Radix_Power (Count) then
                     Prefix_Value (Value, Count) = Magnitude (Value))
   is
   begin
      if Count >= Value'Length then
         Complete_Prefix (Value, Count);
      else
         Prefix_Growth (Value, Count, Value'Length);
      end if;
   end Low_Prefix_Exact;

   procedure Prefix_Modulus
     (Value : Byte_Array; Low, High : Byte_Count)
     with Ghost, Global => null, Always_Terminates,
          Pre => Low <= High,
          Post => Prefix_Value (Value, High) mod Radix_Power (Low) =
                    Prefix_Value (Value, Low),
          Subprogram_Variant => (Decreases => High)
   is
      Quotient : constant Big_Natural := Prefix_Quotient (Value, Low, High);
   begin
      if Low < High then
         Prefix_Modulus (Value, Low, High - 1);
         Power_Order (Low, High - 1);
      end if;
      pragma Assert
        (Prefix_Value (Value, High) = Prefix_Value (Value, Low)
         + Radix_Power (Low) * Quotient);
      pragma Assert (Prefix_Value (Value, Low) < Radix_Power (Low));
      Remainder_From_Witness
        (Prefix_Value (Value, Low), Radix_Power (Low), Quotient);
      pragma Assert
        (Prefix_Value (Value, High) mod Radix_Power (Low) =
           Prefix_Value (Value, Low));
   end Prefix_Modulus;

   procedure Value_Modulus (Value : Byte_Array; Count : Byte_Count)
     with Ghost, Global => null, Always_Terminates,
          Post => Magnitude (Value) mod Radix_Power (Count) =
                    Prefix_Value (Value, Count)
   is
   begin
      if Count >= Value'Length then
         Complete_Prefix (Value, Count);
      else
         Prefix_Modulus (Value, Count, Value'Length);
      end if;
   end Value_Modulus;

   procedure Matching_Prefix
     (Left, Right : Byte_Array; Count : Byte_Count)
     with Ghost, Global => null, Always_Terminates,
          Pre => (if Count > 0 then
                    (for all Offset in 0 .. Count - 1 =>
                       Digit_At (Left, Offset) = Digit_At (Right, Offset))),
          Post => Prefix_Value (Left, Count) = Prefix_Value (Right, Count),
          Subprogram_Variant => (Decreases => Count)
   is
   begin
      if Count > 0 then
         Matching_Prefix (Left, Right, Count - 1);
      end if;
   end Matching_Prefix;

   --  Additive column decompositions. These total Ghost procedures have
   --  actual bodies; every conditional Post and caller remains a proof target.
   procedure Prefix_Step (Value : Byte_Array; Offset : Byte_Count)
     with Ghost, Global => null, Always_Terminates,
          Post => (if Offset < Byte_Count'Last then
            Radix_Power (Offset + 1) = 256 * Radix_Power (Offset)
            and then Prefix_Value (Value, Offset + 1) =
              Prefix_Value (Value, Offset)
              + To_Big_Integer (Digit_At (Value, Offset))
                * Radix_Power (Offset))
   is
   begin
      if Offset = Byte_Count'Last then
         return;
      end if;
      pragma Assert (Offset + 1 - 1 = Offset);
      pragma Assert
        (Radix_Power (Offset + 1) = 256 * Radix_Power (Offset));
      pragma Assert
        (Prefix_Value (Value, Offset + 1) = Prefix_Value (Value, Offset)
         + To_Big_Integer (Digit_At (Value, Offset)) * Radix_Power (Offset));
   end Prefix_Step;

   procedure Extended_Digit_Bound
     (Low, Place : Valid_Big_Integer; Digit : Natural)
     with Ghost, Global => null, Always_Terminates,
          Post => (if Place > 0 and then Low >= 0 and then Low < Place
                       and then Digit <= 255 then
            Low + To_Big_Integer (Digit) * Place >= 0
            and then Low + To_Big_Integer (Digit) * Place < 256 * Place)
   is
   begin
      if Place <= 0 or else Low < 0 or else Low >= Place
        or else Digit > 255
      then
         return;
      end if;
      declare
         D : constant Big_Natural := To_Big_Integer (Digit);
         Gap : constant Big_Positive := 256 - D;
      begin
         Positive_Multiple (Place, Gap);
         pragma Assert (Gap * Place >= Place);
         pragma Assert (D * Place + Gap * Place = 256 * Place);
         pragma Assert (Low + D * Place < 256 * Place);
      end;
   end Extended_Digit_Bound;

   procedure Compare_Extensions
     (Left, Right, Place : Valid_Big_Integer;
      Left_Digit, Right_Digit : Natural)
     with Ghost, Global => null, Always_Terminates,
          Post => (if Place > 0 and then Left >= 0 and then Left < Place
                       and then Right >= 0 and then Right < Place
                       and then Left_Digit <= 255 and then Right_Digit <= 255
                   then
            (Left + To_Big_Integer (Left_Digit) * Place
              < Right + To_Big_Integer (Right_Digit) * Place) =
              (Left_Digit < Right_Digit
               or else (Left_Digit = Right_Digit and then Left < Right))
            and then
            (Left + To_Big_Integer (Left_Digit) * Place
              = Right + To_Big_Integer (Right_Digit) * Place) =
              (Left_Digit = Right_Digit and then Left = Right)
            and then
            (Left + To_Big_Integer (Left_Digit) * Place
              > Right + To_Big_Integer (Right_Digit) * Place) =
              (Left_Digit > Right_Digit
               or else (Left_Digit = Right_Digit and then Left > Right)))
   is
   begin
      if Place <= 0 or else Left < 0 or else Left >= Place
        or else Right < 0 or else Right >= Place
        or else Left_Digit > 255 or else Right_Digit > 255
      then
         return;
      end if;
      declare
         L : constant Big_Natural := To_Big_Integer (Left_Digit);
         R : constant Big_Natural := To_Big_Integer (Right_Digit);
      begin
         if Left_Digit < Right_Digit then
            declare
               Gap : constant Big_Positive := R - L;
            begin
               Positive_Multiple (Place, Gap);
               pragma Assert (R * Place = L * Place + Gap * Place);
               pragma Assert (Left + L * Place < Right + R * Place);
            end;
         elsif Left_Digit > Right_Digit then
            declare
               Gap : constant Big_Positive := L - R;
            begin
               Positive_Multiple (Place, Gap);
               pragma Assert (L * Place = R * Place + Gap * Place);
               pragma Assert (Left + L * Place > Right + R * Place);
            end;
         else
            pragma Assert (L = R);
            pragma Assert ((Left + L * Place < Right + R * Place)
                           = (Left < Right));
            pragma Assert ((Left + L * Place = Right + R * Place)
                           = (Left = Right));
            pragma Assert ((Left + L * Place > Right + R * Place)
                           = (Left > Right));
         end if;
      end;
   end Compare_Extensions;

   procedure Addition_Column
     (X, Y, Z, Low, Place : Valid_Big_Integer;
      A, B, C, Incoming : Natural)
     with Ghost, Global => null, Always_Terminates,
          Post => (if A <= 255 and then B <= 255 and then C <= 255
                       and then Incoming <= 2 and then Place > 0
                       and then X + Y + Z = Low
                         + To_Big_Integer (Incoming) * Place then
            (X + To_Big_Integer (A) * Place)
            + (Y + To_Big_Integer (B) * Place)
            + (Z + To_Big_Integer (C) * Place)
            = Low + To_Big_Integer ((A + B + C + Incoming) mod 256) * Place
              + To_Big_Integer ((A + B + C + Incoming) / 256) * (256 * Place))
   is
   begin
      if A > 255 or else B > 255 or else C > 255 or else Incoming > 2
        or else Place <= 0
        or else X + Y + Z /= Low + To_Big_Integer (Incoming) * Place
      then
         return;
      end if;
      declare
         Sum : constant Natural := A + B + C + Incoming;
         Digit : constant Natural := Sum mod 256;
         Next : constant Natural := Sum / 256;
         S : constant Big_Natural := To_Big_Integer (Sum);
         D : constant Big_Natural := To_Big_Integer (Digit);
         N : constant Big_Natural := To_Big_Integer (Next);
         I : constant Big_Natural := To_Big_Integer (Incoming);
      begin
         pragma Assert (Sum = Digit + 256 * Next);
         pragma Assert (S = D + 256 * N);
         pragma Assert
           (S = To_Big_Integer (A) + To_Big_Integer (B)
                + To_Big_Integer (C) + I);
         pragma Assert
           ((X + To_Big_Integer (A) * Place)
            + (Y + To_Big_Integer (B) * Place)
            + (Z + To_Big_Integer (C) * Place)
            = X + Y + Z + (S - I) * Place);
         pragma Assert (X + Y + Z + (S - I) * Place = Low + S * Place);
         pragma Assert (S * Place = D * Place + (256 * N) * Place);
         pragma Assert ((256 * N) * Place = N * (256 * Place));
      end;
   end Addition_Column;

   procedure Subtraction_Column
     (Credit, Debit, Low, Place : Valid_Big_Integer;
      A, W, F, R, Incoming, Outgoing, Digit : Natural)
     with Ghost, Global => null, Always_Terminates,
          Post => (if A <= 255 and then W <= 255 and then F <= 255
                       and then R <= 255 and then Digit <= 255
                       and then Incoming <= 3 and then Outgoing <= 3
                       and then Place > 0
                       and then A + 256 * Outgoing = W + F + R + Incoming + Digit
                       and then Credit + To_Big_Integer (Incoming) * Place
                         = Debit + Low then
            Credit + To_Big_Integer (A) * Place
              + To_Big_Integer (Outgoing) * (256 * Place)
            = Debit + (To_Big_Integer (W) + To_Big_Integer (F)
                       + To_Big_Integer (R)) * Place
              + Low + To_Big_Integer (Digit) * Place)
   is
   begin
      if A > 255 or else W > 255 or else F > 255 or else R > 255
        or else Digit > 255 or else Incoming > 3 or else Outgoing > 3
        or else Place <= 0
        or else A + 256 * Outgoing /= W + F + R + Incoming + Digit
        or else Credit + To_Big_Integer (Incoming) * Place /= Debit + Low
      then
         return;
      end if;
      declare
         BA : constant Big_Natural := To_Big_Integer (A);
         BW : constant Big_Natural := To_Big_Integer (W);
         BF : constant Big_Natural := To_Big_Integer (F);
         BR : constant Big_Natural := To_Big_Integer (R);
         BI : constant Big_Natural := To_Big_Integer (Incoming);
         BO : constant Big_Natural := To_Big_Integer (Outgoing);
         BD : constant Big_Natural := To_Big_Integer (Digit);
      begin
         pragma Assert (BA + 256 * BO = BW + BF + BR + BI + BD);
         pragma Assert ((BA + 256 * BO) * Place
                        = (BW + BF + BR + BI + BD) * Place);
         pragma Assert (Credit + BA * Place + BO * (256 * Place)
                        = Credit + BI * Place + (BW + BF + BR) * Place
                          + BD * Place);
         pragma Assert (Credit + BI * Place = Debit + Low);
      end;
   end Subtraction_Column;

   procedure Sum_Modulus (Left, Right, Place : Valid_Big_Integer)
     with Ghost, Global => null, Always_Terminates,
          Post => (if Left >= 0 and then Right >= 0 and then Place > 0 then
            (Left + Right) mod Place =
              ((Left mod Place) + (Right mod Place)) mod Place)
   is
   begin
      if Left < 0 or else Right < 0 or else Place <= 0 then
         return;
      end if;
      declare
         LQ : constant Big_Natural := Left / Place;
         LR : constant Big_Natural := Left mod Place;
         RQ : constant Big_Natural := Right / Place;
         RR : constant Big_Natural := Right mod Place;
         Low : constant Big_Natural := LR + RR;
         CQ : constant Big_Natural := Low / Place;
         CR : constant Big_Natural := Low mod Place;
         Tail : constant Big_Natural := LQ + RQ + CQ;
      begin
         pragma Assert (Left = LR + Place * LQ);
         pragma Assert (Right = RR + Place * RQ);
         pragma Assert (Low = CR + Place * CQ);
         pragma Assert (CR < Place);
         pragma Assert (Left + Right = Low + Place * (LQ + RQ));
         pragma Assert (Low + Place * (LQ + RQ) = CR + Place * Tail);
         Remainder_From_Witness (CR, Place, Tail);
         pragma Assert ((Left + Right) mod Place = CR);
      end;
   end Sum_Modulus;

   procedure Mismatching_Sum_Column
     (Left, Right, Result : Byte_Array; Offset : Byte_Count; Carry : Natural)
     with Ghost, Global => null, Always_Terminates,
          Pre => Offset < Byte_Count'Last and then Carry <= 1
            and then Prefix_Value (Left, Offset) + Prefix_Value (Right, Offset)
              = Prefix_Value (Result, Offset)
                + To_Big_Integer (Carry) * Radix_Power (Offset)
            and then Digit_At (Result, Offset) /=
              (Digit_At (Left, Offset) + Digit_At (Right, Offset) + Carry)
                mod 256,
          Post => Magnitude (Result) /= Magnitude (Left) + Magnitude (Right)
   is
   begin
      Value_Modulus (Left, Offset + 1);
      Value_Modulus (Right, Offset + 1);
      Value_Modulus (Result, Offset + 1);
      Prefix_Step (Left, Offset);
      Prefix_Step (Right, Offset);
      Prefix_Step (Result, Offset);
      declare
         Place : constant Big_Positive := Radix_Power (Offset);
         Next_Place : constant Big_Positive := Radix_Power (Offset + 1);
         Low : constant Big_Natural := Prefix_Value (Result, Offset);
         L : constant Natural := Digit_At (Left, Offset);
         R : constant Natural := Digit_At (Right, Offset);
         D : constant Natural := Digit_At (Result, Offset);
         Sum : constant Natural := L + R + Carry;
         Wanted : constant Natural := Sum mod 256;
         Next : constant Natural := Sum / 256;
         Extended : constant Big_Natural := Low + To_Big_Integer (Wanted) * Place;
      begin
         Extended_Digit_Bound (Low, Place, Wanted);
         Addition_Column
           (Prefix_Value (Left, Offset), Prefix_Value (Right, Offset),
            0, Low, Place, L, R, 0, Carry);
         Compare_Extensions (Low, Low, Place, Wanted, D);
         pragma Assert (Wanted /= D);
         pragma Assert (Next_Place = 256 * Place);
         pragma Assert (Extended < Next_Place);
         pragma Assert
           (Prefix_Value (Left, Offset + 1) + Prefix_Value (Right, Offset + 1)
            = Extended + To_Big_Integer (Next) * Next_Place);
         Remainder_From_Witness (Extended, Next_Place, To_Big_Integer (Next));
         pragma Assert
           ((Prefix_Value (Left, Offset + 1) + Prefix_Value (Right, Offset + 1))
              mod Next_Place = Extended);
         pragma Assert (Prefix_Value (Result, Offset + 1)
                        = Low + To_Big_Integer (D) * Place);
         pragma Assert (Extended /= Prefix_Value (Result, Offset + 1));
         Sum_Modulus (Magnitude (Left), Magnitude (Right), Next_Place);
      end;
      pragma Assert
        ((Prefix_Value (Left, Offset + 1)
          + Prefix_Value (Right, Offset + 1)) mod Radix_Power (Offset + 1)
         /= Prefix_Value (Result, Offset + 1));
      if Magnitude (Result) = Magnitude (Left) + Magnitude (Right) then
         pragma Assert
           ((Magnitude (Left) + Magnitude (Right)) mod Radix_Power (Offset + 1)
            = Magnitude (Result) mod Radix_Power (Offset + 1));
         pragma Assert
           ((Prefix_Value (Left, Offset + 1) + Prefix_Value (Right, Offset + 1))
              mod Radix_Power (Offset + 1) = Prefix_Value (Result, Offset + 1));
         pragma Assert (False);
      end if;
   end Mismatching_Sum_Column;

   function Digit_At (Value : Byte_Array; Offset : Byte_Count) return Natural is
   begin
      if Offset < Value'Length then
         return Natural (Value (Value'First + Offset));
      end if;
      return 0;
   end Digit_At;

   function Subtract_Column
     (Available, Withheld, Floor, Requested : Byte;
      Previous : Borrow) return Column_Result
   is
      Debit : constant Natural := Natural (Withheld) + Natural (Floor)
        + Natural (Requested) + Previous;
      Credit : constant Natural := Natural (Available);
   begin
      if Debit <= Credit then
         return (Remainder => Byte (Credit - Debit), Next => 0);
      else
         declare
            Difference : constant Natural := Debit - Credit;
            Next : constant Borrow := (Difference - 1) / 256 + 1;
         begin
            return (Remainder => Byte (Next * 256 - Difference), Next => Next);
         end;
      end if;
   end Subtract_Column;

   function Fits_By_Addition
     (Available, Withheld, Floor, Requested : Byte_Array) return Boolean
   is
      Count : constant Byte_Count := Byte_Count'Max
        (Byte_Count'Max (Available'Length, Withheld'Length),
         Byte_Count'Max (Floor'Length, Requested'Length));
      type Ordering is (Less, Equal, Greater);
      Comparison : Ordering := Equal;
      Carry : Natural range 0 .. 2 := 0;
      Low_Sum : Big_Natural := 0 with Ghost;
   begin
      if Count = 0 then
         return True;
      end if;
      for Offset in 0 .. Count - 1 loop
         declare
            Sum : constant Natural := Digit_At (Withheld, Offset)
              + Digit_At (Floor, Offset) + Digit_At (Requested, Offset) + Carry;
            Wanted : constant Natural := Sum mod 256;
            Credit : constant Natural := Digit_At (Available, Offset);
         begin
            Prefix_Step (Available, Offset);
            Prefix_Step (Withheld, Offset);
            Prefix_Step (Floor, Offset);
            Prefix_Step (Requested, Offset);
            Extended_Digit_Bound (Low_Sum, Radix_Power (Offset), Wanted);
            Compare_Extensions
              (Prefix_Value (Available, Offset), Low_Sum,
               Radix_Power (Offset), Credit, Wanted);
            Addition_Column
              (Prefix_Value (Withheld, Offset), Prefix_Value (Floor, Offset),
               Prefix_Value (Requested, Offset), Low_Sum, Radix_Power (Offset),
               Digit_At (Withheld, Offset), Digit_At (Floor, Offset),
               Digit_At (Requested, Offset), Carry);
            Low_Sum := Low_Sum
              + To_Big_Integer (Wanted) * Radix_Power (Offset);
            Carry := Sum / 256;
            if Credit < Wanted then
               Comparison := Less;
            elsif Credit > Wanted then
               Comparison := Greater;
            end if;
         end;
         pragma Loop_Invariant (Low_Sum < Radix_Power (Offset + 1));
         pragma Loop_Invariant
           (Prefix_Value (Withheld, Offset + 1)
            + Prefix_Value (Floor, Offset + 1)
            + Prefix_Value (Requested, Offset + 1)
            = Low_Sum + To_Big_Integer (Carry) * Radix_Power (Offset + 1));
         pragma Loop_Invariant
           ((Comparison = Less) =
              (Prefix_Value (Available, Offset + 1) < Low_Sum));
         pragma Loop_Invariant
           ((Comparison = Equal) =
              (Prefix_Value (Available, Offset + 1) = Low_Sum));
         pragma Loop_Invariant
           ((Comparison = Greater) =
              (Prefix_Value (Available, Offset + 1) > Low_Sum));
      end loop;
      Complete_Prefix (Available, Count);
      Complete_Prefix (Withheld, Count);
      Complete_Prefix (Floor, Count);
      Complete_Prefix (Requested, Count);
      return Carry = 0 and then Comparison /= Less;
   end Fits_By_Addition;

   function Can_Reserve
     (Available, Withheld, Floor, Requested : Byte_Array) return Boolean
   is
      Count : constant Byte_Count := Byte_Count'Max
        (Byte_Count'Max (Available'Length, Withheld'Length),
         Byte_Count'Max (Floor'Length, Requested'Length));
      Previous : Borrow := 0;
      Remainder_Value : Big_Natural := 0 with Ghost;
      Column : Column_Result;
   begin
      if Count = 0 then
         return True;
      end if;
      declare
         --  These Ghost lifetimes enclose the loop. GNATprove does not support
         --  iteration-local non-scalar objects before a loop invariant.
         Remainder_Digit : Big_Natural := 0 with Ghost;
         Position : Big_Positive := 1 with Ghost;
         Contribution : Big_Natural := 0 with Ghost;
      begin
         for Offset in 0 .. Count - 1 loop
            Column := Subtract_Column
              (Byte (Digit_At (Available, Offset)),
               Byte (Digit_At (Withheld, Offset)),
               Byte (Digit_At (Floor, Offset)),
               Byte (Digit_At (Requested, Offset)), Previous);
            Prefix_Step (Available, Offset);
            Prefix_Step (Withheld, Offset);
            Prefix_Step (Floor, Offset);
            Prefix_Step (Requested, Offset);
            Extended_Digit_Bound
              (Remainder_Value, Radix_Power (Offset), Natural (Column.Remainder));
            Subtraction_Column
              (Prefix_Value (Available, Offset),
               Prefix_Value (Withheld, Offset) + Prefix_Value (Floor, Offset)
                 + Prefix_Value (Requested, Offset),
               Remainder_Value, Radix_Power (Offset),
               Digit_At (Available, Offset), Digit_At (Withheld, Offset),
               Digit_At (Floor, Offset), Digit_At (Requested, Offset),
               Previous, Column.Next, Natural (Column.Remainder));
            Remainder_Digit := To_Big_Integer (Natural (Column.Remainder));
            Position := Radix_Power (Offset);
            Contribution := Remainder_Digit * Position;
            pragma Assert (Remainder_Digit >= 0);
            pragma Assert (Position > 0);
            pragma Assert (Contribution >= 0);
            pragma Assert (Remainder_Value >= 0);
            Remainder_Value := Remainder_Value + Contribution;
            Previous := Column.Next;
            pragma Loop_Invariant
              (Remainder_Value < Radix_Power (Offset + 1));
            pragma Loop_Invariant
              (Prefix_Value (Available, Offset + 1)
               + To_Big_Integer (Previous) * Radix_Power (Offset + 1)
               = Prefix_Value (Withheld, Offset + 1)
                 + Prefix_Value (Floor, Offset + 1)
                 + Prefix_Value (Requested, Offset + 1) + Remainder_Value);
         end loop;
      end;
      Complete_Prefix (Available, Count);
      Complete_Prefix (Withheld, Count);
      Complete_Prefix (Floor, Count);
      Complete_Prefix (Requested, Count);
      return Previous = 0;
   end Can_Reserve;

   function Sum_Equals
     (Left, Right, Result : Byte_Array) return Boolean
   is
      Count : constant Byte_Count := Byte_Count'Max
        (Byte_Count'Max (Left'Length, Right'Length), Result'Length);
      Carry : Natural range 0 .. 1 := 0;
   begin
      if Count = 0 then
         return True;
      end if;
      for Offset in 0 .. Count - 1 loop
         pragma Assert
           (Prefix_Value (Left, Offset) + Prefix_Value (Right, Offset)
            = Prefix_Value (Result, Offset)
              + To_Big_Integer (Carry) * Radix_Power (Offset));
         declare
            Sum : constant Natural := Digit_At (Left, Offset)
              + Digit_At (Right, Offset) + Carry;
         begin
            if Digit_At (Result, Offset) /= Sum mod 256 then
               Mismatching_Sum_Column (Left, Right, Result, Offset, Carry);
               return False;
            end if;
            Prefix_Step (Left, Offset);
            Prefix_Step (Right, Offset);
            Prefix_Step (Result, Offset);
            Addition_Column
              (Prefix_Value (Left, Offset), Prefix_Value (Right, Offset),
               0, Prefix_Value (Result, Offset), Radix_Power (Offset),
               Digit_At (Left, Offset), Digit_At (Right, Offset), 0, Carry);
            Carry := Sum / 256;
         end;
         pragma Loop_Invariant
           (Prefix_Value (Left, Offset + 1) + Prefix_Value (Right, Offset + 1)
            = Prefix_Value (Result, Offset + 1)
              + To_Big_Integer (Carry) * Radix_Power (Offset + 1));
      end loop;
      Complete_Prefix (Left, Count);
      Complete_Prefix (Right, Count);
      Complete_Prefix (Result, Count);
      return Carry = 0;
   end Sum_Equals;

   procedure Try_Reserve
     (State : in out Reservation_State;
      Requested : Byte_Array;
      Accepted : out Boolean)
   is
      Carry : Natural range 0 .. 1 := 0;
      Original : constant Byte_Array := State.Outstanding with Ghost;
   begin
      Accepted := Can_Reserve
        (State.Available, State.Outstanding, State.Floor, Requested);
      if not Accepted then
         return;
      end if;
      pragma Assert
        (Magnitude (Original) + Magnitude (Requested)
         < Radix_Power (State.Capacity));
      Low_Prefix_Exact (Requested, State.Capacity);
      declare
         --  The workspace encloses the loop because this toolchain rejects
         --  loop-local composite declarations before a loop invariant.
         --  The complete snapshot is still assigned at each original capture
         --  point. Its checked copy, storage and lifetime are not free.
         Before_Step : Byte_Array (Original'Range) with Ghost;
      begin
         for Index in State.Outstanding'Range loop
            pragma Assert
              (Prefix_Value (State.Outstanding, Index - State.Outstanding'First)
               + To_Big_Integer (Carry)
                 * Radix_Power (Index - State.Outstanding'First)
               = Prefix_Value (Original, Index - State.Outstanding'First)
                 + Prefix_Value (Requested, Index - State.Outstanding'First));
            pragma Assert
              (for all Rest in Index .. State.Outstanding'Last =>
                 State.Outstanding (Rest) = Original (Rest));
            Before_Step := State.Outstanding;
            declare
               Offset : constant Byte_Count := Index - State.Outstanding'First
                 with Ghost;
               Sum : constant Natural := Natural (State.Outstanding (Index))
                 + Digit_At (Requested, Index - State.Outstanding'First) + Carry;
            begin
               Prefix_Step (Original, Offset);
               Prefix_Step (Requested, Offset);
               Prefix_Step (Before_Step, Offset);
               pragma Assert (Digit_At (Before_Step, Offset)
                              = Digit_At (Original, Offset));
               Addition_Column
                 (Prefix_Value (Original, Offset), Prefix_Value (Requested, Offset),
                  0, Prefix_Value (Before_Step, Offset), Radix_Power (Offset),
                  Digit_At (Original, Offset), Digit_At (Requested, Offset), 0, Carry);
               pragma Assert (Sum = Digit_At (Original, Offset)
                                    + Digit_At (Requested, Offset) + Carry);
               State.Outstanding (Index) := Byte (Sum mod 256);
               Carry := Sum / 256;
               Matching_Prefix (Before_Step, State.Outstanding, Offset);
               Prefix_Step (State.Outstanding, Offset);
               pragma Assert (Digit_At (State.Outstanding, Offset) = Sum mod 256);
            end;
            pragma Loop_Invariant
              (Prefix_Value
                 (State.Outstanding, Index - State.Outstanding'First + 1)
               + To_Big_Integer (Carry)
                 * Radix_Power (Index - State.Outstanding'First + 1)
               = Prefix_Value (Original, Index - State.Outstanding'First + 1)
                 + Prefix_Value (Requested, Index - State.Outstanding'First + 1));
            pragma Loop_Invariant
              (if Index < State.Outstanding'Last then
                 (for all Rest in Index + 1 .. State.Outstanding'Last =>
                    State.Outstanding (Rest) = Original (Rest)));
         end loop;
      end;
      pragma Assert (Carry = 0);
   end Try_Reserve;
end Worldline.Resources;
