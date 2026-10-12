with Interfaces;
with SPARK.Big_Integers;
with Worldline.Recovery_Archive;
with Worldline.Scoped_Archive;
with Worldline.Scoped_Capture_Projection;

package body Worldline.SQLite_Parameter_Source with SPARK_Mode is
   package RA renames Worldline.Recovery_Archive;
   package SA renames Worldline.Scoped_Archive;
   package OA renames SA.A;
   package P renames Worldline.Scoped_Capture_Projection;
   use SPARK.Big_Integers;
   use type E.Count;
   use type E.Value_Kind;
   use type E.Bytes;
   use type E.Q.Byte;
   subtype U64 is Interfaces.Unsigned_64;
   subtype U32 is Interfaces.Unsigned_32;
   use type U64;
   use type U32;
   High_Bit : constant U64 := 16#8000_0000_0000_0000#;
   Fraction : constant U64 := 16#000F_FFFF_FFFF_FFFF#;
   Infinity : constant U64 := 16#7FF0_0000_0000_0000#;
   type Scalar_Kind is (Other, Null_Value, Boolean_Value, Integer_Value,
                        Real_Value, Text_Value, Blob_Value, Sequence_Value, Mapping_Value);

   function Tag (Data : E.Bytes; Item : E.Span; Name : String) return Boolean is
     (E.Text_Is (Data, E.Decode (Data, OA.Field (Data, Item, "type"), E.Operation), Name));
   function Kind (Data : E.Bytes; Item : E.Span; Scoped : Boolean) return Scalar_Kind is
      V : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if not RA.Source_Valid (Data, Item, Scoped) then return Other; end if;
      if Scoped then
         if Tag (Data, Item, "NoneType") then return Null_Value;
         elsif Tag (Data, Item, "bool") then return Boolean_Value;
         elsif Tag (Data, Item, "integer") then return Integer_Value;
         elsif Tag (Data, Item, "float") then return Real_Value;
         elsif Tag (Data, Item, "str") then return Text_Value;
         elsif Tag (Data, Item, "bytes") then return Blob_Value;
         elsif Tag (Data, Item, "list") or else Tag (Data, Item, "tuple") then return Sequence_Value;
         elsif Tag (Data, Item, "dict") then return Mapping_Value;
         else return Other; end if;
      else
         case V.Form is
            when E.Null_Value => return Null_Value;
            when E.Boolean_Value => return Boolean_Value;
            when E.Integer_Value => return Integer_Value;
            when E.Float_Value => return Real_Value;
            when E.Text_Value => return Text_Value;
            when E.Bytes_Value => return Blob_Value;
            when E.List_Value | E.Tuple_Value => return Sequence_Value;
            when E.Object_Value => return Mapping_Value;
            when others => return Other;
         end case;
      end if;
   end Kind;
   function Text_View (Data : E.Bytes; Item : E.Span; Scoped : Boolean) return E.View is
     (E.Decode (Data, (if Scoped then OA.Field (Data, Item, "value") else Item), E.Operation));
   function Text_Valid (Data : E.Bytes; Item : E.Span; Scoped : Boolean) return Boolean is
     (Kind (Data, Item, Scoped) = Text_Value and then
      E.Bytes_Valid (Data, Text_View (Data, Item, Scoped).Payload));
   function Text_Is (Data : E.Bytes; Item : E.Span; Scoped : Boolean; Word : String) return Boolean is
     (Text_Valid (Data, Item, Scoped) and then E.Text_Is (Data, Text_View (Data, Item, Scoped), Word));
   function Digit (Byte : E.Q.Byte) return U64 is
     (if Byte in 48 .. 57 then U64 (Byte - 48)
      elsif Byte in 97 .. 102 then U64 (Byte - 87) else 0);
   function Real_Bits (Data : E.Bytes; Item : E.Span; Scoped : Boolean) return U64 is
      Result : U64 := 0;
   begin
      if Scoped then
         declare
            Encoded : constant E.View := E.Decode (Data, OA.Field (Data, Item, "bits"), E.Operation);
         begin
            if not E.Bytes_Valid (Data, Encoded.Payload) then return 0; end if;
            declare Raw : constant E.Bytes := E.Materialize (Data, Encoded.Payload); begin
               for Byte of Raw loop Result := Result * 16 + Digit (Byte); end loop;
            end;
         end;
      else
         declare V : constant E.View := E.Decode (Data, Item, E.Operation); begin
            if not E.Bytes_Valid (Data, V.Payload) then return 0; end if;
            declare Raw : constant E.Bytes := E.Materialize (Data, V.Payload); begin
               for Byte of Raw loop Result := Result * 256 + U64 (Byte); end loop;
            end;
         end;
      end if;
      return Result;
   end Real_Bits;
   function Truthy (Data : E.Bytes; Selector : E.Span; Scoped : Boolean := False) return Boolean is
   begin
      case Kind (Data, Selector, Scoped) is
         when Null_Value => return False;
         when Boolean_Value => return R.Archive_Boolean_Is (Data, Selector, True);
         when Integer_Value => return P.Number (Data, Selector) /= To_Big_Integer (0);
         when Real_Value => return (Real_Bits (Data, Selector, Scoped) and not High_Bit) /= 0;
         --  Kind has validated the whole source; canonical base64 is empty
         --  exactly when its decoded text is empty, at every codec layer.
         when Text_Value => return Text_View (Data, Selector, Scoped).Payload.Encoded.Length > 0;
         when Blob_Value => return R.Archive_Bytes (Data, Selector)'Length > 0;
         when Sequence_Value => return R.Archive_Length (Data, Selector) > 0;
         when Mapping_Value =>
            if Scoped then return SA.Member_Count (Data, Selector) > 0;
            else return E.Array_Length (Data, E.Decode (Data, Selector, E.Operation).Children) > 0; end if;
         when Other => return True;
      end case;
   end Truthy;

   -- SQLite 3.53.4 src/util.c: powerOfTen, sqlite3Multiply128/160,
   -- sqlite3Fp2Convert10, sqlite3Fp10Convert2, sqlite3FpDecode. These are the
   -- integer operations of the real producer, not an ideal decimal formatter.
   -- src/printf.c etGENERIC is rendered below; src/main.c sets nFpDigit=17
   -- and src/vdbemem.c vdbeMemRenderNum uses %!.*g with that connection value.
   -- Primary source: https://github.com/sqlite/sqlite/tree/version-3.53.4/src
   type Table64 is array (Natural range <>) of U64;
   type Table32 is array (Natural range <>) of U32;
   Base : constant Table64 (0 .. 26) :=
     (16#8000000000000000#,16#a000000000000000#,16#c800000000000000#,16#fa00000000000000#,
      16#9c40000000000000#,16#c350000000000000#,16#f424000000000000#,16#9896800000000000#,
      16#bebc200000000000#,16#ee6b280000000000#,16#9502f90000000000#,16#ba43b74000000000#,
      16#e8d4a51000000000#,16#9184e72a00000000#,16#b5e620f480000000#,16#e35fa931a0000000#,
      16#8e1bc9bf04000000#,16#b1a2bc2ec5000000#,16#de0b6b3a76400000#,16#8ac7230489e80000#,
      16#ad78ebc5ac620000#,16#d8d726b7177a8000#,16#878678326eac9000#,16#a968163f0a57b400#,
      16#d3c21bcecceda100#,16#84595161401484a0#,16#a56fa5b99019a5c8#);
   Scale : constant Table64 (0 .. 25) :=
     (16#8049a4ac0c5811ae#,16#cf42894a5dce35ea#,16#a76c582338ed2621#,16#873e4f75e2224e68#,
      16#da7f5bf590966848#,16#b080392cc4349dec#,16#8e938662882af53e#,16#e65829b3046b0afa#,
      16#ba121a4650e4ddeb#,16#964e858c91ba2655#,16#f2d56790ab41c2a2#,16#c428d05aa4751e4c#,
      16#9e74d1b791e07e48#,16#cccccccccccccccc#,16#cecb8f27f4200f3a#,16#a70c3c40a64e6c51#,
      16#86f0ac99b4e8dafd#,16#da01ee641a708de9#,16#b01ae745b101e9e4#,16#8e41ade9fbebc27d#,
      16#e5d3ef282a242e81#,16#b9a74a0637ce2ee1#,16#95f83d0a1fb69cd9#,16#f24a01a73cf2dccf#,
      16#c3b8358109e84f07#,16#9e19db92b4e31ba9#);
   Scale_Low : constant Table32 (0 .. 25) :=
     (16#205b896d#,16#52064cad#,16#af2af2b8#,16#5a7744a7#,16#af39a475#,16#bd8d794e#,
      16#547eb47b#,16#0cb4a5a3#,16#92f34d62#,16#3a6a07f9#,16#fae27299#,16#aa97e14c#,
      16#775ea265#,16#cccccccc#,0,16#999090b6#,16#69a028bb#,16#e80e6f48#,
      16#5ec05dd0#,16#14588f14#,16#8f1668c9#,16#6d953e2c#,16#4abdaf10#,
      16#bc633b39#,16#0a862f81#,16#6c07a2c2#);
   procedure Multiply128 (A, B : U64; Hi, Lo : out U64) is
      A0 : constant U64 := A and 16#FFFF_FFFF#;
      A1 : constant U64 := Interfaces.Shift_Right (A, 32);
      B0 : constant U64 := B and 16#FFFF_FFFF#;
      B1 : constant U64 := Interfaces.Shift_Right (B, 32);
      A0B0 : constant U64 := A0 * B0;
      A1B1 : constant U64 := A1 * B1;
      A0B1 : constant U64 := A0 * B1;
      A1B0 : constant U64 := A1 * B0;
      T : constant U64 := Interfaces.Shift_Right (A0B0, 32) +
        (A0B1 and 16#FFFF_FFFF#) + (A1B0 and 16#FFFF_FFFF#);
   begin
      Lo := (A0B0 and 16#FFFF_FFFF#) or Interfaces.Shift_Left (T, 32);
      Hi := A1B1 + Interfaces.Shift_Right (A0B1, 32) +
        Interfaces.Shift_Right (A1B0, 32) + Interfaces.Shift_Right (T, 32);
   end Multiply128;
   procedure Multiply160 (A : U64; A_Low : U32; B : U64; Hi : out U64; Lo : out U32) is
      H, L, LH, LL, Carry : U64;
   begin
      Multiply128 (A, B, H, L);
      Multiply128 (U64 (A_Low), B, LH, LL);
      Carry := Interfaces.Shift_Left (LH, 32) or Interfaces.Shift_Right (LL, 32);
      Lo := U32 (Interfaces.Shift_Right (L + Carry, 32));
      Hi := H + (if L + Carry < L then 1 else 0);
   end Multiply160;
   procedure Power_Of_Ten (Power : Integer; Hi : out U64; Lo : out U32)
     with Pre => Power in -348 .. 347
   is
      G : Integer := Power / 27;
      N : Integer := Power rem 27;
   begin
      if Power = -1 then Hi := Scale (13); Lo := Scale_Low (13); return;
      elsif Power in 0 .. 26 then Hi := Base (Power); Lo := 0; return;
      end if;
      if N < 0 then G := G - 1; N := N + 27; end if;
      if N = 0 then Hi := Scale (G + 13); Lo := Scale_Low (G + 13);
      else
         Multiply160 (Scale (G + 13), Scale_Low (G + 13), Base (N), Hi, Lo);
         if (Hi and High_Bit) = 0 then
            Hi := Interfaces.Shift_Left (Hi, 1) or U64 (Interfaces.Shift_Right (Lo, 31));
            Lo := Interfaces.Shift_Left (Lo, 1) or 1;
         end if;
      end if;
   end Power_Of_Ten;
   function Floor_Divide (N : Integer; D : Positive) return Integer is
     (N / D - (if N < 0 and then N rem D /= 0 then 1 else 0));
   function Power10_To_2 (N : Integer) return Integer
   is (Floor_Divide (N * 108853, 32768))
     with Pre => N in -348 .. 347;
   function Power2_To_10 (N : Integer) return Integer
   is (Floor_Divide (N * 78913, 262144))
     with Pre => N in -1074 .. 1023;
   function Leading_Zeros (Value : U64) return Natural is
      V : U64 := Value;
      N : Natural := 0;
   begin
      while N < 64 and then (V and High_Bit) = 0 loop
         pragma Loop_Variant (Increases => N);
         V := Interfaces.Shift_Left (V, 1); N := N + 1;
      end loop;
      return N;
   end Leading_Zeros;
   procedure Convert10 (Mantissa : U64; Exponent : Integer; Significant : Positive;
                        Value : out U64; Power : out Integer)
     with Pre => Mantissa >= High_Bit and then Exponent in -1137 .. 960
       and then Significant in 16 | 18
   is
      P10 : constant Integer := Significant - 1 - Power2_To_10 (Exponent + 63);
      H, L, Scale_Hi : U64;
      Scale_Lo : U32;
   begin
      Power_Of_Ten (P10, Scale_Hi, Scale_Lo);
      Multiply128 (Mantissa, Scale_Hi, H, L);
      if Significant = 18 then
         H := Interfaces.Shift_Right (H, -(Exponent + Power10_To_2 (P10) + 2));
         Value := Interfaces.Shift_Right (H + (Interfaces.Shift_Left (H, 1) and 2), 1);
      else
         Value := Interfaces.Shift_Right (H, -(Exponent + Power10_To_2 (P10) + 1));
      end if;
      Power := -P10;
   end Convert10;
   function Convert2 (Value : U64; Power : Integer) return U64
     with Pre => Value > 0 and then Power in -348 .. 347
   is
      B : constant Integer := 64 - Leading_Zeros (Value);
      LP : constant Integer := Power10_To_2 (Power);
      Exponent : Integer := 53 - B - LP;
      S : Integer;
      Scale_Hi, X, Hi, Lo, Sticky, U, M : U64;
      Scale_Lo, Mid1, Mid2 : U32;
   begin
      if Power < -348 then return 0; elsif Power > 347 then return Infinity; end if;
      if Exponent > 1074 then
         if Exponent >= 1130 then return 0; end if; Exponent := 1074;
      end if;
      S := -(Exponent - (64 - B) + LP + 3);
      Power_Of_Ten (Power, Scale_Hi, Scale_Lo);
      if Scale_Lo /= 0 then Scale_Hi := Scale_Hi + 1; Scale_Lo := not Scale_Lo; end if;
      X := Interfaces.Shift_Left (Value, 64 - B);
      Multiply128 (X, Scale_Hi, Hi, Lo);
      Mid1 := U32 (Interfaces.Shift_Right (Lo, 32)); Sticky := 1;
      if (Hi and (Interfaces.Shift_Left (U64'(1), S) - 1)) = 0 then
         Multiply128 (X, Interfaces.Shift_Left (U64 (Scale_Lo), 32), U, Lo);
         Mid2 := U32 (Interfaces.Shift_Right (U, 32));
         Sticky := (if Mid1 - Mid2 > 1 then 1 else 0);
         Hi := Hi - (if Mid1 < Mid2 then 1 else 0);
      end if;
      U := Interfaces.Shift_Right (Hi, S) or Sticky;
      if U >= Interfaces.Shift_Left (U64'(1), 55) - 2 then
         U := Interfaces.Shift_Right (U, 1) or (U and 1); Exponent := Exponent - 1;
      end if;
      M := Interfaces.Shift_Right (U + 1 + (Interfaces.Shift_Right (U, 2) and 1), 2);
      if Exponent <= -972 then return Infinity; end if;
      if (M and Interfaces.Shift_Left (U64'(1), 52)) /= 0 then
         M := (M and not Interfaces.Shift_Left (U64'(1), 52)) or
           Interfaces.Shift_Left (U64 (1075 - Exponent), 52);
      end if;
      return M;
   end Convert2;
   function Real_Text (Bits : U64; Precision : Positive) return String
     with Pre => (Bits and not High_Bit) <= Infinity and then Precision in 15 | 17
   is
      Positive_Bits : constant U64 := Bits and not High_Bit;
      V : U64 := Positive_Bits and Fraction;
      Exponent : Integer := Integer (Interfaces.Shift_Right (Positive_Bits, 52));
      Power, DP : Integer;
      --  SQLite's digit scratch uses zero-based positions, unlike String.
      type Digit_Array is array (Natural range <>) of Character;
      Z : Digit_Array (0 .. 20) := (others => '0');
      First : Natural := 20;
      N, Round : Natural;
      Result : String (1 .. 32) := (others => ' ');
      Last : Natural := 0;
      procedure Append (C : Character)
        with Pre => Last < Result'Length
      is
      begin Last := Last + 1; Result (Last) := C; end Append;
      function Prefix_Value (Width : Natural) return U64
        with Pre => Width in 1 .. 17 and then First + Width <= Z'Last + 1
      is
         Value : U64 := 0;
      begin
         for I in Natural range 0 .. Width - 1 loop
            Value := Value * 10 + U64 (Character'Pos (Z (First + I)) - Character'Pos ('0'));
         end loop;
         return Value;
      end Prefix_Value;
   begin
      if Positive_Bits = 0 then return "0.0";
      elsif Exponent = 2047 then return (if Bits >= High_Bit then "-Inf" else "Inf"); end if;
      if Exponent = 0 then
         declare NN : constant Natural := Leading_Zeros (V); begin
            V := Interfaces.Shift_Left (V, NN); Exponent := -1074 - NN;
         end;
      else V := Interfaces.Shift_Left (V, 11) or High_Bit; Exponent := Exponent - 1086;
      end if;
      Convert10 (V, Exponent, (if Precision >= 18 then 18 else Precision + 1), V, Power);
      while V > 0 loop
         pragma Loop_Variant (Decreases => V);
         First := First - 1; Z (First) := Character'Val (48 + Integer (V mod 10)); V := V / 10;
      end loop;
      N := 20 - First; DP := N + Power; Round := Precision;
      if Round < N or else N > 20 then
         if Round = 17 then
            if Z (First + 15) = '9' and then Z (First + 14) = '9' then
               declare J : Natural := 14; V2 : U64; begin
                  while J > 0 and then Z (First + J - 1) = '9' loop pragma Loop_Variant (Decreases => J); J := J - 1; end loop;
                  V2 := (if J = 0 then 1 else Prefix_Value (J) + 1);
                  if Convert2 (V2, Power + N - J) = Positive_Bits then Round := J + 1; end if;
               end;
            elsif DP >= N or else (Z (First + 15) = '0' and then Z (First + 14) = '0' and then Z (First + 13) = '0') then
               declare J : Natural := 13; begin
                  while J > 1 and then Z (First + J - 1) = '0' loop pragma Loop_Variant (Decreases => J); J := J - 1; end loop;
                  if Convert2 (Prefix_Value (J), Power + N - J) = Positive_Bits then Round := J + 1; end if;
               end;
            end if;
         end if;
         N := Round;
         if Z (First + Round) >= '5' then
            declare J : Natural := First + Round - 1; begin
               loop
                  pragma Loop_Variant (Decreases => J);
                  Z (J) := Character'Succ (Z (J));
                  exit when Z (J) <= '9';
                  Z (J) := '0';
                  if J = First then First := First - 1; Z (First) := '1'; N := N + 1; DP := DP + 1; exit; end if;
                  J := J - 1;
               end loop;
            end;
         end if;
      end if;
      while N > 1 and then Z (First + N - 1) = '0' loop pragma Loop_Variant (Decreases => N); N := N - 1; end loop;
      if Bits >= High_Bit then Append ('-'); end if;
      Exponent := DP - 1;
      if Exponent < -4 or else Exponent >= Precision then
         Append (Z (First)); Append ('.');
         if N = 1 then Append ('0'); else
            for I in Natural range 1 .. N - 1 loop Append (Z (First + I)); end loop;
         end if;
         Append ('e'); Append ((if Exponent < 0 then '-' else '+')); Exponent := abs Exponent;
         if Exponent >= 100 then Append (Character'Val (48 + Exponent / 100)); Exponent := Exponent mod 100; end if;
         Append (Character'Val (48 + Exponent / 10)); Append (Character'Val (48 + Exponent mod 10));
      else
         if DP <= 0 then Append ('0'); else
            for I in Integer range 0 .. DP - 1 loop
               Append ((if I < N then Z (First + I) else '0'));
            end loop;
         end if;
         Append ('.');
         if DP <= 0 then
            for I in Integer range 1 .. -DP loop Append ('0'); end loop;
         end if;
         if DP < N then
            for I in Integer range Integer'Max (DP, 0) .. N - 1 loop Append (Z (First + I)); end loop;
         else Append ('0'); end if;
      end if;
      return Result (1 .. Last);
   end Real_Text;
   function Integer_Text (Data : E.Bytes; Item : E.Span; Scoped : Boolean; Value : Big_Integer) return Boolean is
      Remaining : Big_Integer := abs Value;
   begin
      if not Text_Valid (Data, Item, Scoped) then return False; end if;
      declare Raw : constant E.Bytes := E.Materialize (Data, Text_View (Data, Item, Scoped).Payload);
              Sign : constant E.Count := (if Value < To_Big_Integer (0) then 1 else 0);
      begin
         if Raw'Length <= Sign or else (Sign = 1 and then Raw (Raw'First) /= 45)
           or else (Raw'Length - Sign > 1 and then Raw (Raw'First + Sign) = 48) then return False; end if;
         for I in reverse E.Count range Sign .. Raw'Length - 1 loop
            if Raw (Raw'First + I) not in 48 .. 57 or else
              To_Big_Integer (Integer (Raw (Raw'First + I) - 48)) /= Remaining mod To_Big_Integer (10) then return False; end if;
            Remaining := Remaining / To_Big_Integer (10);
         end loop;
         return Remaining = To_Big_Integer (0);
      end;
   end Integer_Text;
   function Text_Affinity_Matches
     (Data : E.Bytes; Selector, Cast_Text : E.Span; Scoped : Boolean := False;
      Precision : Positive := 17) return Boolean is
   begin
      if not RA.Source_Valid (Data, Selector, Scoped) or else
        not RA.Source_Valid (Data, Cast_Text, Scoped) then return False; end if;
      case Kind (Data, Selector, Scoped) is
         when Null_Value => return Kind (Data, Cast_Text, Scoped) = Null_Value;
         when Boolean_Value => return Text_Is (Data, Cast_Text, Scoped,
           (if R.Archive_Boolean_Is (Data, Selector, True) then "1" else "0"));
         when Integer_Value =>
            declare Value : constant Big_Integer := P.Number (Data, Selector);
                    Bound : constant Big_Integer := To_Big_Integer (2) ** 63;
            begin
               return Value >= -Bound and then Value < Bound and then Integer_Text (Data, Cast_Text, Scoped, Value);
            end;
         when Real_Value =>
            declare Bits : constant U64 := Real_Bits (Data, Selector, Scoped);
                    Magnitude : constant U64 := Bits and not High_Bit;
            begin
               -- sqlite3VdbeMemSetDouble maps every NaN binding to SQL NULL.
               if Magnitude > Infinity then return Kind (Data, Cast_Text, Scoped) = Null_Value; end if;
               return Precision in 15 | 17 and then Text_Is (Data, Cast_Text, Scoped, Real_Text (Bits, Precision));
            end;
         when Text_Value => return RA.Ordered_Source_Value_Matches (Data, Data, Selector, Cast_Text, Scoped, Scoped);
         when Blob_Value =>
            return Text_Valid (Data, Cast_Text, Scoped) and then
              R.Archive_Bytes (Data, Selector) = E.Materialize (Data, Text_View (Data, Cast_Text, Scoped).Payload);
         when others => return False;
      end case;
   end Text_Affinity_Matches;
   function Parameter_Equals_Text
     (Data : E.Bytes; Selector, Column : E.Span; Scoped : Boolean := False;
      Precision : Positive := 17) return Boolean is
   begin
      -- TEXT affinity transforms only numeric parameters. BLOB remains BLOB;
      -- SQL NULL (including a bound NaN) cannot satisfy = against any TEXT.
      if not Text_Valid (Data, Column, Scoped) then return False; end if;
      case Kind (Data, Selector, Scoped) is
         when Text_Value | Boolean_Value | Integer_Value | Real_Value =>
            return Text_Affinity_Matches (Data, Selector, Column, Scoped, Precision);
         when others => return False;
      end case;
   end Parameter_Equals_Text;
end Worldline.SQLite_Parameter_Source;
