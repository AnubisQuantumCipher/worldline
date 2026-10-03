package body Resource_Quantities with SPARK_Mode is
   function Digit
     (Data : Byte_Array; Q : Quantity; Offset : Byte_Count) return Natural is
   begin
      if Span_Valid (Data, Q) and then Offset < Q.Length then
         return Natural (Data (Q.First + Offset));
      end if;
      return 0;
   end Digit;

   --  Actual proof computation for a nonnegative product. The caller proves
   --  the sign premise; this is not an imported multiplication theorem.
   --  Factor has the whole Natural domain. It is a byte-column factor at the
   --  present call sites, never a cap on a represented resource magnitude.
   function Scale_Column
     (Factor : Natural; Unit_Value : Valid_Big_Integer)
      return Valid_Big_Integer
   with Ghost, Global => null,
     Pre => Unit_Value >= 0,
     Post => Scale_Column'Result = To_Big_Integer (Factor) * Unit_Value
       and then Scale_Column'Result >= 0
       and then (if Factor > 0 then Scale_Column'Result >= Unit_Value)
   is
      Completed : Natural := 0;
      Accumulated : Valid_Big_Integer := To_Big_Integer (0);
   begin
      while Completed < Factor loop
         pragma Loop_Invariant (Completed <= Factor);
         pragma Loop_Invariant (Accumulated >= 0);
         pragma Loop_Invariant
           (Accumulated = To_Big_Integer (Completed) * Unit_Value);
         pragma Loop_Invariant
           (if Completed > 0 then Accumulated >= Unit_Value);
         pragma Loop_Variant (Decreases => Factor - Completed);
         Accumulated := Accumulated + Unit_Value;
         Completed := Completed + 1;
      end loop;
      return Accumulated;
   end Scale_Column;

   procedure Column_Bounds
     (Low, Unit_Value : Valid_Big_Integer; Column : Natural)
   with Ghost, Global => null, Always_Terminates,
     Pre => Low >= 0 and then Unit_Value > 0 and then Low < Unit_Value
       and then Column <= 255,
     Post => Low + To_Big_Integer (Column) * Unit_Value >= 0
       and then Low + To_Big_Integer (Column) * Unit_Value <
         To_Big_Integer (256) * Unit_Value
   is
      Contribution : constant Valid_Big_Integer :=
        Scale_Column (Column, Unit_Value);
      Unused : constant Valid_Big_Integer :=
        Scale_Column (255 - Column, Unit_Value);
      Gap : constant Valid_Big_Integer := Unit_Value - Low;
   begin
      pragma Assert (Contribution >= 0 and then Unused >= 0);
      pragma Assert (Gap > 0);
      pragma Assert
        ((Low + Contribution) + Gap + Unused =
           To_Big_Integer (256) * Unit_Value);
      pragma Assert (Gap + Unused > 0);
      pragma Assert (Low + Contribution >= 0);
      pragma Assert (Low + Contribution < To_Big_Integer (256) * Unit_Value);
   end Column_Bounds;

   procedure Higher_Column_Order
     (Higher_Low, Lower_Low, Unit_Value : Valid_Big_Integer;
      Higher_Digit, Lower_Digit : Natural)
   with Ghost, Global => null, Always_Terminates,
     Pre => Unit_Value > 0
       and then Higher_Low >= 0 and then Higher_Low < Unit_Value
       and then Lower_Low >= 0 and then Lower_Low < Unit_Value
       and then Higher_Digit <= 255 and then Lower_Digit <= 255
       and then Higher_Digit > Lower_Digit,
     Post => Higher_Low + To_Big_Integer (Higher_Digit) * Unit_Value >
       Lower_Low + To_Big_Integer (Lower_Digit) * Unit_Value
   is
      Extra_Digits : constant Natural := Higher_Digit - Lower_Digit - 1;
      Extra : constant Valid_Big_Integer :=
        Scale_Column (Extra_Digits, Unit_Value);
      Gap : constant Valid_Big_Integer :=
        Unit_Value - Lower_Low + Higher_Low;
   begin
      pragma Assert (Extra >= 0);
      pragma Assert (Unit_Value - Lower_Low > 0);
      pragma Assert (Gap > 0);
      pragma Assert
        ((Higher_Low + To_Big_Integer (Higher_Digit) * Unit_Value)
         - (Lower_Low + To_Big_Integer (Lower_Digit) * Unit_Value) =
           Gap + Extra);
      pragma Assert (Gap + Extra > 0);
   end Higher_Column_Order;

   --  Private iterative producer; its complete value equation and the
   --  Inline_For_Proof correspondence are mandatory proof obligations.
   --  No smaller public producer is called by this worker body.
   function Radix_Power_Worker (Exponent : Byte_Count)
      return Valid_Big_Integer
   with Ghost, Global => null,
     Post => Radix_Power_Worker'Result = Power_Reference (Exponent),
     Annotate => (GNATprove, Inline_For_Proof)
   is
      Completed : Byte_Count := 0;
      Result : Valid_Big_Integer := To_Big_Integer (1);
      Previous : Valid_Big_Integer := To_Big_Integer (1);
   begin
      while Completed < Exponent loop
         pragma Loop_Invariant (Completed <= Exponent);
         pragma Loop_Invariant (Result >= 1);
         pragma Loop_Invariant (Result = Power_Reference (Completed));
         pragma Loop_Invariant
           (if Completed > 0 then
              Previous = Power_Reference (Completed - 1));
         pragma Loop_Invariant
           (if Completed = 0 then Result = 1
            else Result = To_Big_Integer (256) * Previous);
         pragma Loop_Variant (Decreases => Exponent - Completed);
         Previous := Result;
         Result := To_Big_Integer (256) * Previous;
         Completed := Completed + 1;
      end loop;
      --  The independent predecessor reference avoids repeating the producer
      --  here. Its body and the complete original recursive producer Post
      --  remain required proof and checked-runtime obligations.
      if Exponent > 0 then
         declare
            Prior_Result : constant Valid_Big_Integer :=
              Power_Reference (Exponent - 1);
         begin
            pragma Assert (Completed = Exponent);
            pragma Assert (Prior_Result = Power_Reference (Exponent - 1));
            pragma Assert (Previous = Prior_Result);
            pragma Assert (Result = To_Big_Integer (256) * Prior_Result);
         end;
      end if;
      return Result;
   end Radix_Power_Worker;

   --  The public declaration, including every original recursive Post
   --  conjunct and numeric variant, remains byte-for-byte unchanged.
   function Radix_Power (Exponent : Byte_Count) return Valid_Big_Integer is
     (Radix_Power_Worker (Exponent));

   --  Full-domain independent prefix equation; no span/length Pre is added.
   --  The moved loop, all assertions and all original variants remain below.
   function Prefix_Value_Worker
     (Data : Byte_Array; Q : Quantity; Count : Byte_Count)
      return Valid_Big_Integer
   with Ghost, Global => null,
     Post => Prefix_Value_Worker'Result = Prefix_Reference (Data, Q, Count),
     Annotate => (GNATprove, Inline_For_Proof)
   is
      Completed : Byte_Count := 0;
      Result : Valid_Big_Integer := To_Big_Integer (0);
      Place : Valid_Big_Integer := To_Big_Integer (1);
      Previous_Result : Valid_Big_Integer := To_Big_Integer (0);
      Previous_Place : Valid_Big_Integer := To_Big_Integer (1);
   begin
      while Completed < Count loop
         pragma Loop_Invariant (Completed <= Count);
         pragma Loop_Invariant (Result >= 0 and then Place >= 1);
         pragma Loop_Invariant
           (Result = Prefix_Reference (Data, Q, Completed));
         pragma Loop_Invariant (Place = Power_Reference (Completed));
         pragma Loop_Invariant
           (if Completed > 0 then
              Previous_Result = Prefix_Reference (Data, Q, Completed - 1)
              and then Previous_Place = Power_Reference (Completed - 1));
         pragma Loop_Invariant
           (if Completed = 0 then Result = 0 and then Place = 1
            else Result = Previous_Result +
              To_Big_Integer (Digit (Data, Q, Completed - 1)) *
                Previous_Place and then
              Place = To_Big_Integer (256) * Previous_Place);
         pragma Loop_Variant (Decreases => Count - Completed);
         Previous_Result := Result;
         Previous_Place := Place;
         Result := Previous_Result +
           To_Big_Integer (Digit (Data, Q, Completed)) * Previous_Place;
         Place := To_Big_Integer (256) * Previous_Place;
         Completed := Completed + 1;
      end loop;
      if Count > 0 then
         declare
            Prior_Result : constant Valid_Big_Integer :=
              Prefix_Reference (Data, Q, Count - 1);
            Prior_Place : constant Valid_Big_Integer :=
              Power_Reference (Count - 1);
         begin
            pragma Assert (Completed = Count);
            pragma Assert
              (Prior_Result = Prefix_Reference (Data, Q, Count - 1));
            pragma Assert (Prior_Place = Power_Reference (Count - 1));
            pragma Assert (Previous_Result = Prior_Result);
            pragma Assert (Previous_Place = Prior_Place);
            pragma Assert
              (Result = Prior_Result +
                 To_Big_Integer (Digit (Data, Q, Count - 1)) * Prior_Place);
         end;
      end if;
      return Result;
   end Prefix_Value_Worker;

   function Prefix_Value
     (Data : Byte_Array; Q : Quantity; Count : Byte_Count)
      return Valid_Big_Integer is
     (Prefix_Value_Worker (Data, Q, Count));

   function Magnitude (Data : Byte_Array; Q : Quantity)
      return Valid_Big_Integer is
   begin
      if not Span_Valid (Data, Q) then
         return To_Big_Integer (0);
      end if;
      return Prefix_Value (Data, Q, Q.Length);
   end Magnitude;

   function Value (Data : Byte_Array; Q : Quantity)
      return Valid_Big_Integer is
   begin
      if Q.Negative then
         return -Magnitude (Data, Q);
      end if;
      return Magnitude (Data, Q);
   end Value;

   --  Proof-only induction over the closed independent prefix equations.
   --  Every body, assertion, Pre at callers and termination variant is required.
   procedure Prefix_Bounds
     (Data : Byte_Array; Q : Quantity; Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Subprogram_Variant => (Decreases => Count),
     Post => Prefix_Reference (Data, Q, Count) >= 0 and then
       Prefix_Reference (Data, Q, Count) < Power_Reference (Count);

   procedure Prefix_Bounds
     (Data : Byte_Array; Q : Quantity; Count : Byte_Count) is
   begin
      if Count > 0 then
         Prefix_Bounds (Data, Q, Count - 1);
         pragma Assert (Digit (Data, Q, Count - 1) <= 255);
         pragma Assert
           (Prefix_Reference (Data, Q, Count) =
              Prefix_Reference (Data, Q, Count - 1) +
                To_Big_Integer (Digit (Data, Q, Count - 1)) *
                  Power_Reference (Count - 1));
         pragma Assert
           (Power_Reference (Count) =
              To_Big_Integer (256) * Power_Reference (Count - 1));
         Column_Bounds
           (Prefix_Reference (Data, Q, Count - 1),
            Power_Reference (Count - 1), Digit (Data, Q, Count - 1));
         pragma Assert
           (Prefix_Reference (Data, Q, Count) < Power_Reference (Count));
      end if;
   end Prefix_Bounds;

   procedure Prefix_Monotone
     (Data : Byte_Array; Q : Quantity; Smaller, Larger : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Smaller <= Larger,
     Subprogram_Variant => (Decreases => Larger),
     Post => Prefix_Reference (Data, Q, Smaller) <=
       Prefix_Reference (Data, Q, Larger);

   procedure Prefix_Monotone
     (Data : Byte_Array; Q : Quantity; Smaller, Larger : Byte_Count) is
   begin
      if Smaller < Larger then
         Prefix_Monotone (Data, Q, Smaller, Larger - 1);
         pragma Assert
           (Prefix_Reference (Data, Q, Larger) >=
              Prefix_Reference (Data, Q, Larger - 1));
      end if;
   end Prefix_Monotone;

   procedure Prefix_Padding
     (Data : Byte_Array; Q : Quantity; Count : Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Span_Valid (Data, Q) and then Q.Length <= Count,
     Subprogram_Variant => (Decreases => Count),
     Post => Prefix_Reference (Data, Q, Count) = Magnitude (Data, Q);

   procedure Prefix_Padding
     (Data : Byte_Array; Q : Quantity; Count : Byte_Count) is
   begin
      if Count > Q.Length then
         Prefix_Padding (Data, Q, Count - 1);
         pragma Assert (Digit (Data, Q, Count - 1) = 0);
      else
         pragma Assert
           (Prefix_Reference (Data, Q, Count) =
              Prefix_Value (Data, Q, Q.Length));
      end if;
   end Prefix_Padding;

   procedure Borrow_Column_Facts (Debit, Credit, Next : Natural)
   with Ghost, Global => null, Always_Terminates,
     Pre => Debit <= 3 * 255 + 3 and then Credit <= 255 and then
       Next = (if Debit <= Credit then 0 else (Debit - Credit - 1) / 256 + 1),
     Post => Credit + 256 * Next >= Debit and then
       Credit + 256 * Next - Debit <= 255;

   procedure Borrow_Column_Facts (Debit, Credit, Next : Natural) is
   begin
      if Debit > Credit then
         pragma Assert
           (Debit - Credit - 1 =
              256 * ((Debit - Credit - 1) / 256) +
                (Debit - Credit - 1) mod 256);
         pragma Assert ((Debit - Credit - 1) mod 256 < 256);
      end if;
   end Borrow_Column_Facts;

   function Is_Zero (Data : Byte_Array; Q : Quantity) return Boolean is
   begin
      if not Span_Valid (Data, Q) or else Q.Length = 0 then
         return True;
      end if;
      for Offset in 0 .. Q.Length - 1 loop
         pragma Loop_Invariant
           (Prefix_Reference (Data, Q, Offset) = 0);
         if Digit (Data, Q, Offset) /= 0 then
            Prefix_Monotone (Data, Q, Offset + 1, Q.Length);
            pragma Assert (Prefix_Reference (Data, Q, Offset + 1) > 0);
            pragma Assert (Magnitude (Data, Q) > 0);
            return False;
         end if;
         pragma Assert (Prefix_Reference (Data, Q, Offset + 1) = 0);
      end loop;
      return True;
   end Is_Zero;

   function Is_Negative (Data : Byte_Array; Q : Quantity) return Boolean is
   begin
      return Q.Negative and then not Is_Zero (Data, Q);
   end Is_Negative;

   function Compare (Data : Byte_Array; Left, Right : Quantity)
      return Ordering
   is
      Count : constant Byte_Count := Byte_Count'Max (Left.Length, Right.Length);
      Left_Negative : Boolean;
      Right_Negative : Boolean;
   begin
      if not Span_Valid (Data, Left) or else not Span_Valid (Data, Right) then
         return Invalid;
      end if;
      Prefix_Padding (Data, Left, Count);
      Prefix_Padding (Data, Right, Count);
      Left_Negative := Is_Negative (Data, Left);
      Right_Negative := Is_Negative (Data, Right);
      if Left_Negative /= Right_Negative then
         return (if Left_Negative then Less else Greater);
      end if;
      pragma Assert
        (Value (Data, Left) =
           (if Left_Negative then -Magnitude (Data, Left)
            else Magnitude (Data, Left)));
      pragma Assert
        (Value (Data, Right) =
           (if Right_Negative then -Magnitude (Data, Right)
            else Magnitude (Data, Right)));
      if Count = 0 then
         return Equal;
      end if;
      for Offset in reverse 0 .. Count - 1 loop
         pragma Loop_Invariant
           (Magnitude (Data, Left) - Magnitude (Data, Right) =
              Prefix_Reference (Data, Left, Offset + 1) -
                Prefix_Reference (Data, Right, Offset + 1));
         Prefix_Bounds (Data, Left, Offset);
         Prefix_Bounds (Data, Right, Offset);
         if Digit (Data, Left, Offset) < Digit (Data, Right, Offset) then
            Higher_Column_Order
              (Prefix_Reference (Data, Right, Offset),
               Prefix_Reference (Data, Left, Offset), Power_Reference (Offset),
               Digit (Data, Right, Offset), Digit (Data, Left, Offset));
            pragma Assert
              (Prefix_Reference (Data, Left, Offset + 1) <
                 Prefix_Reference (Data, Right, Offset + 1));
            pragma Assert (Magnitude (Data, Left) < Magnitude (Data, Right));
            return (if Left_Negative then Greater else Less);
         elsif Digit (Data, Left, Offset) > Digit (Data, Right, Offset) then
            Higher_Column_Order
              (Prefix_Reference (Data, Left, Offset),
               Prefix_Reference (Data, Right, Offset), Power_Reference (Offset),
               Digit (Data, Left, Offset), Digit (Data, Right, Offset));
            pragma Assert
              (Prefix_Reference (Data, Left, Offset + 1) >
                 Prefix_Reference (Data, Right, Offset + 1));
            pragma Assert (Magnitude (Data, Left) > Magnitude (Data, Right));
            return (if Left_Negative then Less else Greater);
         end if;
         pragma Assert
           (Magnitude (Data, Left) - Magnitude (Data, Right) =
              Prefix_Reference (Data, Left, Offset) -
                Prefix_Reference (Data, Right, Offset));
      end loop;
      return Equal;
   end Compare;

   function Capacity_Fits
     (Data : Byte_Array; Available, Withheld, Floor, Requested : Quantity)
      return Boolean
   is
      Count : constant Byte_Count := Byte_Count'Max
        (Byte_Count'Max (Available.Length, Withheld.Length),
         Byte_Count'Max (Floor.Length, Requested.Length));
      subtype Borrow is Natural range 0 .. 3;
      Previous : Borrow := 0;
      Residue : Valid_Big_Integer := To_Big_Integer (0) with Ghost;
      Place : Valid_Big_Integer := To_Big_Integer (1) with Ghost;
   begin
      if not Span_Valid (Data, Available) or else
        not Span_Valid (Data, Withheld) or else
        not Span_Valid (Data, Floor) or else
        not Span_Valid (Data, Requested)
      then
         return False;
      end if;
      Prefix_Padding (Data, Available, Count);
      Prefix_Padding (Data, Withheld, Count);
      Prefix_Padding (Data, Floor, Count);
      Prefix_Padding (Data, Requested, Count);
      if Count = 0 then
         return True;
      end if;
      for Offset in 0 .. Count - 1 loop
         pragma Loop_Invariant (Place = Power_Reference (Offset));
         pragma Loop_Invariant (Residue >= 0 and then Residue < Place);
         pragma Loop_Invariant
           (Prefix_Reference (Data, Available, Offset) -
              Prefix_Reference (Data, Withheld, Offset) -
              Prefix_Reference (Data, Floor, Offset) -
              Prefix_Reference (Data, Requested, Offset) =
                Residue - To_Big_Integer (Previous) * Place);
         declare
            Debit : constant Natural := Digit (Data, Withheld, Offset) +
              Digit (Data, Floor, Offset) + Digit (Data, Requested, Offset) +
              Previous;
            Credit : constant Natural := Digit (Data, Available, Offset);
            Before_Residue : constant Valid_Big_Integer := Residue with Ghost;
            Before_Place : constant Valid_Big_Integer := Place with Ghost;
         begin
            if Debit <= Credit then
               Previous := 0;
            else
               Previous := (Debit - Credit - 1) / 256 + 1;
            end if;
            Borrow_Column_Facts (Debit, Credit, Previous);
            declare
               Column_Value : constant Natural :=
                 Credit + 256 * Previous - Debit with Ghost;
               Contribution : constant Valid_Big_Integer :=
                 Scale_Column (Column_Value, Place) with Ghost;
            begin
               pragma Assert (Column_Value <= 255);
               pragma Assert (Before_Residue >= 0 and then Before_Place > 0);
               pragma Assert (Contribution >= 0);
               pragma Assert
                 (Contribution =
                    To_Big_Integer (Credit + 256 * Previous - Debit) * Place);
               pragma Assert
                 (To_Big_Integer (Credit + 256 * Previous - Debit) * Place >= 0);
            end;
            Residue := Residue +
              To_Big_Integer (Credit + 256 * Previous - Debit) * Place;
            pragma Assert
              (Residue = Before_Residue +
                 To_Big_Integer (Credit + 256 * Previous - Debit) * Before_Place);
            pragma Assert (Residue >= 0);
            Place := To_Big_Integer (256) * Place;
            pragma Assert (Place = Power_Reference (Offset + 1));
            pragma Assert (Residue >= 0 and then Residue < Place);
            pragma Assert
              (Prefix_Reference (Data, Available, Offset + 1) -
                 Prefix_Reference (Data, Withheld, Offset + 1) -
                 Prefix_Reference (Data, Floor, Offset + 1) -
                 Prefix_Reference (Data, Requested, Offset + 1) =
                   Residue - To_Big_Integer (Previous) * Place);
         end;
      end loop;
      return Previous = 0;
   end Capacity_Fits;
end Resource_Quantities;
