package body Worldline.Emitter_Ordinal with SPARK_Mode is
   function Significant_Length (Data : Q.Byte_Array) return Q.Byte_Count
   with Global => null,
     Post => Significant_Length'Result <= Data'Length and then
       (for all K in Q.Byte_Count range Significant_Length'Result ..
          Data'Length - 1 => Data (Data'First + K) = 0) and then
       (if Significant_Length'Result > 0 then
          Data (Data'First + (Significant_Length'Result - 1)) /= 0) and then
       Q.Magnitude (Data, Unsigned_Span (Data)) =
         Q.Prefix_Value (Data, Unsigned_Span (Data), Significant_Length'Result)
   is
      Length : Q.Byte_Count := Data'Length;
   begin
      while Length > 0 and then Data (Data'First + (Length - 1)) = 0 loop
         pragma Loop_Variant (Decreases => Length);
         pragma Loop_Invariant (Length <= Data'Length);
         pragma Loop_Invariant
           (for all K in Q.Byte_Count range Length .. Data'Length - 1 =>
              Data (Data'First + K) = 0);
         pragma Loop_Invariant
           (Q.Magnitude (Data, Unsigned_Span (Data)) =
              Q.Prefix_Value (Data, Unsigned_Span (Data), Length));
         Length := Length - 1;
      end loop;
      return Length;
   end Significant_Length;

   function Minimal_Length (Magnitude : Q.Byte_Array) return Q.Byte_Count is
     (Q.Byte_Count'Max (1, Significant_Length (Magnitude)));

   function Same_Value (Left, Right : Q.Byte_Array) return Boolean is
      Length : constant Q.Byte_Count := Significant_Length (Left);
   begin
      if Length /= Significant_Length (Right) then
         return False;
      end if;
      for Offset in Q.Byte_Count range 0 .. Length - 1 loop
         pragma Loop_Variant (Increases => Offset);
         pragma Loop_Invariant (Length <= Left'Length);
         pragma Loop_Invariant (Length <= Right'Length);
         pragma Loop_Invariant
           (Q.Prefix_Value (Left, Unsigned_Span (Left), Offset) =
              Q.Prefix_Value (Right, Unsigned_Span (Right), Offset));
         if Left (Left'First + Offset) /= Right (Right'First + Offset) then
            return False;
         end if;
      end loop;
      return True;
   end Same_Value;

   function Successor_Length (Input : Q.Byte_Array) return Q.Byte_Count
   with Global => null,
     Post =>
       (if Successor_Length'Result = 0 then
          Q.Magnitude (Input, Unsigned_Span (Input)) + 1 >=
            Q.Power_Reference (Q.Byte_Count'Last)
        else
          Q.Magnitude (Input, Unsigned_Span (Input)) + 1 <
            Q.Power_Reference (Successor_Length'Result) and then
          (if Successor_Length'Result > 1 then
             Q.Magnitude (Input, Unsigned_Span (Input)) + 1 >=
               Q.Power_Reference (Successor_Length'Result - 1)))
   is
      Length : constant Q.Byte_Count := Significant_Length (Input);
   begin
      if Length = 0 then
         return 1;
      end if;
      for Offset in Q.Byte_Count range 0 .. Length - 1 loop
         pragma Loop_Variant (Increases => Offset);
         pragma Loop_Invariant (Length <= Input'Length);
         pragma Loop_Invariant
           (for all K in Q.Byte_Count range 0 .. Offset - 1 =>
              Input (Input'First + K) = 255);
         if Input (Input'First + Offset) /= 255 then
            return Length;
         end if;
      end loop;
      return (if Length = Q.Byte_Count'Last then 0 else Length + 1);
   end Successor_Length;

   procedure Successor
     (Input : Q.Byte_Array; Output : out Q.Byte_Array;
      Needed : out Q.Byte_Count; Complete : out Boolean)
   is
      Carry : Boolean := True;
   begin
      Output := (others => 0);
      Needed := Successor_Length (Input);
      Complete := False;
      if Needed = 0 then
         return;
      end if;
      --  Same carry kernel as Mutation_Decision.Append_Successor, without
      --  its concatenated arena or dependency on a custody policy predicate.
      for Offset in Q.Byte_Count range 0 ..
        Q.Byte_Count'Min (Needed, Output'Length) - 1
      loop
         pragma Loop_Variant (Increases => Offset);
         pragma Loop_Invariant (Needed > 0);
         pragma Loop_Invariant
           (for all K in Q.Byte_Count range Offset .. Output'Length - 1 =>
              Output (Output'First + K) = 0);
         pragma Loop_Invariant
           (Q.Prefix_Value (Input, Unsigned_Span (Input), Offset) + 1 =
              Q.Prefix_Value (Output, Unsigned_Span (Output), Offset) +
                (if Carry then Q.Power_Reference (Offset)
                 else To_Big_Integer (0)));
         declare
            B : constant Q.Byte :=
              (if Offset < Input'Length then Input (Input'First + Offset)
               else 0);
         begin
            if Carry and then B = 255 then
               Output (Output'First + Offset) := 0;
            elsif Carry then
               Output (Output'First + Offset) := B + 1;
               Carry := False;
            else
               Output (Output'First + Offset) := B;
            end if;
         end;
      end loop;
      Complete := Needed <= Output'Length;
   end Successor;

   function Canonical_Decimal_Matches
     (Text, Magnitude : Q.Byte_Array) return Boolean
   is
   begin
      if Text'Length = 0 or else
        (Text'Length > 1 and then Text (Text'First) = 48)
      then
         return False;
      end if;
      for I in Text'Range loop
         pragma Loop_Variant (Increases => I);
         pragma Loop_Invariant
           (for all K in Q.Byte_Count range 0 .. I - Text'First - 1 =>
              Text (Text'First + K) in 48 .. 57);
         if Text (I) not in 48 .. 57 then
            return False;
         end if;
      end loop;
      if Text'Length = 1 and then Text (Text'First) = 48 then
         return Q.Is_Zero (Magnitude, (False, Magnitude'First, Magnitude'Length));
      end if;
      if Magnitude'Length = 0 then
         return False;
      end if;
      declare
         --  Reuse Subject_Evidence.Decimal_Matches' decimal multiply/add
         --  vector. Neither text length nor storage length caps its value.
         --  A carry beyond the supplied magnitude extent cannot match it.
         Work : Q.Byte_Array
           (1 .. Q.Byte_Count'Min (Text'Length, Magnitude'Length)) :=
             (others => 0);
         Used : Q.Byte_Count := 0;
         Carry : Natural range 0 .. 9;
         Digit : Natural range 0 .. 2559;
      begin
         for I in Text'Range loop
            pragma Loop_Variant (Increases => I);
            pragma Loop_Invariant (Used <= I - Text'First);
            pragma Loop_Invariant (Used <= Work'Length);
            pragma Loop_Invariant
              (for all K in Q.Byte_Count range Used + 1 .. Work'Length =>
                 Work (K) = 0);
            pragma Loop_Invariant
              (Q.Prefix_Value (Work, Unsigned_Span (Work), Used) =
                 Decimal_Prefix (Text, I - Text'First));
            Carry := Natural (Text (I) - 48);
            for K in Q.Byte_Count range 1 .. Used loop
               pragma Loop_Variant (Increases => K);
               pragma Loop_Invariant (Carry <= 9);
               pragma Loop_Invariant (Used <= Work'Length);
               pragma Loop_Invariant
                 (for all J in Q.Byte_Count range K .. Used =>
                    Work (J) = Work'Loop_Entry (J));
               pragma Loop_Invariant
                 (Q.Prefix_Value (Work, Unsigned_Span (Work), K - 1) +
                    To_Big_Integer (Carry) * Q.Power_Reference (K - 1) +
                    10 * (Q.Prefix_Value
                      (Work'Loop_Entry, Unsigned_Span (Work'Loop_Entry), Used) -
                      Q.Prefix_Value
                        (Work'Loop_Entry, Unsigned_Span (Work'Loop_Entry), K - 1)) =
                    Decimal_Prefix (Text, I - Text'First) * 10 +
                      To_Big_Integer (Integer (Text (I)) - 48));
               Digit := Natural (Work (K)) * 10 + Carry;
               Work (K) := Q.Byte (Digit mod 256);
               Carry := Digit / 256;
            end loop;
            if Carry > 0 then
               if Used = Work'Length then
                  return False;
               end if;
               Used := Used + 1;
               Work (Used) := Q.Byte (Carry);
            end if;
         end loop;
         return Same_Value (Work, Magnitude);
      end;
   end Canonical_Decimal_Matches;
end Worldline.Emitter_Ordinal;
