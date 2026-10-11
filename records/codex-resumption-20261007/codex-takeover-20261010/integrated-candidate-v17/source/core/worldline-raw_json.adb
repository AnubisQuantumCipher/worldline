with Interfaces;
with SPARK.Big_Integers;
with Exact_Decimal;
with Decimal_Binary64;
with Worldline.Archive_Text;
with Worldline.Operation_Archive;
with Worldline.Scoped_Archive;
with Worldline.Producer_Values;

package body Worldline.Raw_JSON with SPARK_Mode is
   package V renames Worldline.Producer_Values;
   package E renames Worldline.Operation_Archive.E;
   package O renames Worldline.Operation_Archive;
   package S renames Worldline.Scoped_Archive;
   package T renames Worldline.Archive_Text;
   use SPARK.Big_Integers;
   use type P.Count;
   use type P.Byte;
   use type V.Value_Kind;
   use type E.Value_Kind;
   use type E.Layer;
   use type Interfaces.Unsigned_32;
   use type Interfaces.Unsigned_64;

   function Decode_JSON (Data : P.Bytes; Item : P.Span) return Decoded_JSON is
      type Encoding is (UTF8, UTF16_BE, UTF16_LE, UTF32_BE, UTF32_LE);
      Kind : Encoding := UTF8;
      Start, Offset : P.Count := 0;
      Length : Natural := 0;
      Invalid : Boolean := False;
      function Byte (At_Offset : P.Count) return Natural is
        (if At_Offset < Item.Length then Natural (Data (Item.First + At_Offset)) else 0);
      function Unit_16 (At_Offset : P.Count) return Natural is
        (if Kind = UTF16_LE then Byte (At_Offset) + 256 * Byte (At_Offset + 1)
         else Byte (At_Offset) * 256 + Byte (At_Offset + 1));
      procedure Scalar (Position : in out P.Count; Code : out Natural) is
         Width : P.Count;
         Next : Natural;
         U : Interfaces.Unsigned_32;
      begin
         Code := 0;
         case Kind is
            when UTF8 =>
               Width := T.Unit_Width (Data,(Item.First,Item.Length),Position);
               if Width = 0 then Invalid := True; return; end if;
               Code := Natural (T.Value_At (Data,(Item.First,Item.Length),Position));
               Position := Position + Width;
            when UTF16_LE | UTF16_BE =>
               if Item.Length - Position < 2 then Invalid := True; return; end if;
               Code := Unit_16 (Position); Position := Position + 2;
               if Code in 16#D800# .. 16#DBFF# and then Item.Length - Position >= 2 then
                  Next := Unit_16 (Position);
                  if Next in 16#DC00# .. 16#DFFF# then
                     Code := 65536 + (Code - 16#D800#) * 1024 + Next - 16#DC00#;
                     Position := Position + 2;
                  end if;
               end if;
            when UTF32_LE | UTF32_BE =>
               if Item.Length - Position < 4 then Invalid := True; return; end if;
               U := 0;
               for K in P.Count range 0 .. 3 loop
                  U := U * 256 + Interfaces.Unsigned_32
                    (Byte (Position + (if Kind = UTF32_BE then K else 3 - K)));
               end loop;
               if U > 16#10FFFF# then Invalid := True; return; end if;
               Code := Natural (U); Position := Position + 4;
         end case;
      end Scalar;
      function Width (C : Natural) return Positive is
        (if C < 128 then 1 elsif C < 2048 then 2 elsif C < 65536 then 3 else 4);
   begin
      if not P.Valid (Data,Item) then return (0,False,""); end if;
      -- Exact json.detect_encoding(bytes) precedence, including BOM-less
      -- UTF16/32 and UTF8-sig. Decoding uses the original surrogatepass policy.
      if Item.Length >= 4 and then Byte (0) = 0 and then Byte (1) = 0
        and then Byte (2) = 254 and then Byte (3) = 255 then Kind := UTF32_BE; Start := 4;
      elsif Item.Length >= 4 and then Byte (0) = 255 and then Byte (1) = 254
        and then Byte (2) = 0 and then Byte (3) = 0 then Kind := UTF32_LE; Start := 4;
      elsif Item.Length >= 2 and then Byte (0) = 254 and then Byte (1) = 255 then Kind := UTF16_BE; Start := 2;
      elsif Item.Length >= 2 and then Byte (0) = 255 and then Byte (1) = 254 then Kind := UTF16_LE; Start := 2;
      elsif Item.Length >= 3 and then Byte (0) = 239 and then Byte (1) = 187 and then Byte (2) = 191 then Start := 3;
      elsif Item.Length >= 4 then
         if Byte (0) = 0 then Kind := (if Byte (1) /= 0 then UTF16_BE else UTF32_BE);
         elsif Byte (1) = 0 then Kind := (if Byte (2) /= 0 or else Byte (3) /= 0 then UTF16_LE else UTF32_LE);
         end if;
      elsif Item.Length = 2 then
         if Byte (0) = 0 then Kind := UTF16_BE;
         elsif Byte (1) = 0 then Kind := UTF16_LE;
         end if;
      end if;
      Offset := Start;
      while Offset < Item.Length loop
         pragma Loop_Variant (Decreases => Item.Length - Offset);
         declare C : Natural; begin
            Scalar (Offset,C);
            if Invalid then return (0,False,""); end if;
            Length := Length + Width (C);
         end;
      end loop;
      -- One exact-size owned String feeds the existing String-native grammar.
      -- There is no token/depth/magnitude/number-of-rows admission bound.
      declare
         Text : String (1 .. Length);
         Used : Natural := 0;
         procedure Emit (B : Natural) is
         begin Used := Used + 1; Text (Used) := Character'Val (B); end Emit;
      begin
         Offset := Start;
         while Offset < Item.Length loop
            pragma Loop_Variant (Decreases => Item.Length - Offset);
            declare C : Natural; begin
               Scalar (Offset,C);
               if C < 128 then Emit (C);
               elsif C < 2048 then Emit (192 + C / 64); Emit (128 + C mod 64);
               elsif C < 65536 then Emit (224 + C / 4096); Emit (128 + C / 64 mod 64); Emit (128 + C mod 64);
               else Emit (240 + C / 262144); Emit (128 + C / 4096 mod 64); Emit (128 + C / 64 mod 64); Emit (128 + C mod 64);
               end if;
            end;
         end loop;
         return (Length,True,Text);
      end;
   end Decode_JSON;

   function Original_Exact_JSON (Data : P.Bytes; Item : P.Span) return Boolean is
      Decoded : constant Decoded_JSON := Decode_JSON (Data,Item);
   begin
      return Decoded.Valid and then V.Original_Exact_JSON (Decoded.Data);
   end Original_Exact_JSON;

   function Native_Number (Data : String; Item : V.Node) return Exact_Decimal.Number is
      Token : constant String := V.Slice (Data,Item);
      Arena : P.Bytes (1 .. P.Count (Token'Length));
   begin
      for K in Token'Range loop Arena (P.Count (K - Token'First + 1)) := P.Byte (Character'Pos (Token (K))); end loop;
      return Exact_Decimal.Parse (Arena,(1,Arena'Length),0);
   end Native_Number;
   function Text_Matches (Data : String; Item : V.Node; Archive : P.Bytes; View : E.View) return Boolean is
      Text : constant String := V.Text (Data,Item);
   begin
      if Item.Form /= V.String_Value or else View.Form /= E.Text_Value or else
        not E.Bytes_Valid (Archive,View.Payload) then return False; end if;
      declare Raw : constant P.Bytes := E.Materialize (Archive,View.Payload); begin
         return Raw'Length = P.Count (Text'Length) and then
           (for all K in Text'Range => Raw (Raw'First + P.Count (K - Text'First)) = Character'Pos (Text (K)));
      end;
   end Text_Matches;
   function Hex (C : P.Byte) return Integer is
     (if C in 48 .. 57 then Integer (C) - 48
      elsif C in 97 .. 102 then Integer (C) - 97 + 10 else -1);

   type Numeric_Kind is (Not_Numeric, Integral, Floating);
   type Scalar_Number is record
      Kind : Numeric_Kind := Not_Numeric;
      Negative : Boolean := False;
      Coefficient : Big_Integer := To_Big_Integer (0);
      Bits : Decimal_Binary64.Bits := 0;
   end record;
   function JSON_Number (Data : String; Item : V.Node) return Scalar_Number is
      Result : Scalar_Number;
   begin
      if Item.Form = V.Boolean_Value then
         Result.Kind := Integral;
         Result.Coefficient := To_Big_Integer (Boolean'Pos (V.Is_True (Data,Item)));
      elsif Item.Form in V.Integer_Value | V.Number_Value then
         declare N : constant Exact_Decimal.Number := Native_Number (Data,Item); begin
            if not N.Valid then
               declare Token : constant String := V.Slice (Data,Item); begin
                  if Token not in "NaN" | "Infinity" | "-Infinity" then return Result; end if;
                  Result.Kind := Floating;
                  Result.Bits := (if Token = "NaN" then Decimal_Binary64.Infinity + 1
                    elsif Token = "-Infinity" then Decimal_Binary64.Sign_Bit + Decimal_Binary64.Infinity
                    else Decimal_Binary64.Infinity);
                  return Result;
               end;
            end if;
            if N.After /= P.Count (Item.Last - Item.First + 1) then return Result; end if;
            if Item.Form = V.Integer_Value then
               Result.Kind := Integral;
               Result.Negative := N.Negative and then N.Coefficient /= To_Big_Integer (0);
               Result.Coefficient := N.Coefficient;
            else
               declare C : constant Decimal_Binary64.Conversion := Decimal_Binary64.Convert (N); begin
                  Result.Kind := Floating;
                  Result.Bits := (if C.Valid then C.Encoding elsif N.Negative then
                    Decimal_Binary64.Sign_Bit + Decimal_Binary64.Infinity else Decimal_Binary64.Infinity);
               end;
            end if;
         end;
      end if;
      return Result;
   end JSON_Number;
   function Archive_Number
     (Archive : P.Bytes; Encoded : P.Span; Scoped : Boolean) return Scalar_Number
   is
      Result : Scalar_Number;
      Value : E.View := E.Decode (Archive,Encoded,E.Operation);
      Typ : E.View;
   begin
      if Scoped then
         Typ := E.Decode (Archive,O.Field (Archive,Encoded,"type"),E.Operation);
         if E.Text_Is (Archive,Typ,"bool") then
            Value := E.Decode (Archive,O.Field (Archive,Encoded,"value"),E.Operation);
         elsif E.Text_Is (Archive,Typ,"integer") then
            Value := E.Decode (Archive,O.Field (Archive,Encoded,"negative"),E.Operation);
            if Value.Form /= E.Boolean_Value then return Result; end if;
            Result.Negative := Value.Boolean_Bit;
            Result.Kind := Integral;
            Value := E.Decode (Archive,O.Field (Archive,Encoded,"magnitude"),E.Operation);
         elsif E.Text_Is (Archive,Typ,"float") then
            Result.Kind := Floating;
            Value := E.Decode (Archive,O.Field (Archive,Encoded,"bits"),E.Operation);
         else return Result;
         end if;
      elsif Value.Form = E.Integer_Value then
         Result.Kind := Integral;
         Result.Negative := Value.Sign;
      elsif Value.Form = E.Float_Value then Result.Kind := Floating;
      end if;
      if Value.Form = E.Boolean_Value then
         Result.Kind := Integral;
         Result.Coefficient := To_Big_Integer (Boolean'Pos (Value.Boolean_Bit));
         return Result;
      end if;
      if Result.Kind = Not_Numeric or else not E.Bytes_Valid (Archive,Value.Payload) then
         return (Not_Numeric,False,To_Big_Integer (0),0);
      end if;
      declare Raw : constant P.Bytes := E.Materialize (Archive,Value.Payload); begin
         if Result.Kind = Floating then
            if Raw'Length /= (if Scoped then 16 else 8) then return (Not_Numeric,False,To_Big_Integer (0),0); end if;
            for K in Raw'Range loop
               if Scoped then
                  declare Digit : constant Integer := Hex (Raw (K)); begin
                     if Digit < 0 then return (Not_Numeric,False,To_Big_Integer (0),0); end if;
                     Result.Bits := Result.Bits * 16 + Interfaces.Unsigned_64 (Digit);
                  end;
               else Result.Bits := Result.Bits * 256 + Interfaces.Unsigned_64 (Raw (K));
               end if;
            end loop;
         else
            declare Position : P.Count := Raw'Length; begin
               if Scoped and then Position mod 2 /= 0 then return (Not_Numeric,False,To_Big_Integer (0),0); end if;
               while Position > 0 loop
                  pragma Loop_Variant (Decreases => Position);
                  if Scoped then
                     Position := Position - 2;
                     declare Hi : constant Integer := Hex (Raw (Raw'First + Position));
                             Lo : constant Integer := Hex (Raw (Raw'First + Position + 1)); begin
                        if Hi < 0 or else Lo < 0 then return (Not_Numeric,False,To_Big_Integer (0),0); end if;
                        Result.Coefficient := Result.Coefficient * To_Big_Integer (256) + To_Big_Integer (Hi * 16 + Lo);
                     end;
                  else
                     Position := Position - 1;
                     Result.Coefficient := Result.Coefficient * To_Big_Integer (256) +
                       To_Big_Integer (Integer (Raw (Raw'First + Position)));
                  end if;
               end loop;
            end;
            if Result.Coefficient = To_Big_Integer (0) then Result.Negative := False; end if;
         end if;
      end;
      return Result;
   end Archive_Number;
   function Numbers_Equal (Left, Right : Scalar_Number) return Boolean is
      package D renames Decimal_Binary64;
      function Integer_Float (I, F : Scalar_Number) return Boolean is
      begin
         if not D.Finite (F.Bits) or else
           (I.Negative /= (F.Bits >= D.Sign_Bit) and then D.Magnitude (F.Bits) /= 0) then return False; end if;
         declare R : constant D.Rational := D.Value (D.Magnitude (F.Bits)); begin
            return R.Numerator mod R.Denominator = To_Big_Integer (0)
              and then I.Coefficient = R.Numerator / R.Denominator;
         end;
      end Integer_Float;
   begin
      if Left.Kind = Not_Numeric or else Right.Kind = Not_Numeric then return False;
      elsif Left.Kind = Integral and then Right.Kind = Integral then
         return Left.Negative = Right.Negative and then Left.Coefficient = Right.Coefficient;
      elsif Left.Kind = Integral then return Integer_Float (Left,Right);
      elsif Right.Kind = Integral then return Integer_Float (Right,Left);
      else
         return D.Magnitude (Left.Bits) <= D.Infinity and then D.Magnitude (Right.Bits) <= D.Infinity
           and then ((D.Magnitude (Left.Bits) = 0 and then D.Magnitude (Right.Bits) = 0)
             or else Left.Bits = Right.Bits);
      end if;
   end Numbers_Equal;

   function JSON_Trees_Equal
     (Left_Data, Right_Data : String; Left, Right : V.Node) return Boolean
     with Subprogram_Variant => (Decreases => Left.Last - Natural'Min (Left.First,Left.Last));
   function JSON_Trees_Equal
     (Left_Data, Right_Data : String; Left, Right : V.Node) return Boolean is
   begin
      if Left.Form = V.Missing or else Right.Form = V.Missing then return False; end if;
      if Left.Form in V.Boolean_Value | V.Integer_Value | V.Number_Value and then
        Right.Form in V.Boolean_Value | V.Integer_Value | V.Number_Value then
         return Numbers_Equal (JSON_Number (Left_Data,Left),JSON_Number (Right_Data,Right));
      end if;
      if Left.Form /= Right.Form then return False; end if;
      case Left.Form is
         when V.Null_Value => return True;
         when V.String_Value => return V.Text (Left_Data,Left) = V.Text (Right_Data,Right);
         when V.Array_Value | V.Object_Value =>
            if V.Count (Left_Data,Left) /= V.Count (Right_Data,Right) then return False; end if;
            for K in 1 .. V.Count (Left_Data,Left) loop
               if Left.Form = V.Object_Value then
                  declare
                     Name : constant String := V.Member_Name (Left_Data,Left,K);
                     L_Item : constant V.Node := V.Field (Left_Data,Left,Name);
                     R_Item : constant V.Node := V.Field (Right_Data,Right,Name);
                  begin
                     if not JSON_Trees_Equal (Left_Data,Right_Data,L_Item,R_Item) then return False; end if;
                  end;
               elsif not JSON_Trees_Equal (Left_Data,Right_Data,
                 V.Element (Left_Data,Left,K),V.Element (Right_Data,Right,K)) then return False;
               end if;
            end loop;
            return True;
         when V.Boolean_Value | V.Integer_Value | V.Number_Value | V.Missing => return False;
      end case;
   end JSON_Trees_Equal;
   function Python_JSON_Equal (Left, Right : String) return Boolean is
     (JSON_Trees_Equal (Left,Right,V.Parse (Left),V.Parse (Right)));

   function Match_Tree
     (Data : String; Item : V.Node; Archive : P.Bytes; Encoded : P.Span;
      Scoped, Python_Equality : Boolean; Object_Order_Independent : Boolean := False;
      At_Layer : E.Layer := E.Operation)
      return Boolean
     with Subprogram_Variant => (Decreases => Item.Last - Natural'Min (Item.First,Item.Last));
   function Match_Tree
     (Data : String; Item : V.Node; Archive : P.Bytes; Encoded : P.Span;
      Scoped, Python_Equality : Boolean; Object_Order_Independent : Boolean := False;
      At_Layer : E.Layer := E.Operation)
      return Boolean
   is
      Value : E.View := E.Decode (Archive,Encoded,At_Layer);
      Typ : E.View;
      Children : P.Count;
      Pair : E.View;
      Child : P.Span;
   begin
      if Item.Form = V.Missing then return False; end if;
      if Python_Equality and then Item.Form in V.Boolean_Value | V.Integer_Value | V.Number_Value then
         return Numbers_Equal (JSON_Number (Data,Item),Archive_Number (Archive,Encoded,Scoped));
      end if;
      if Scoped then
         Typ := E.Decode (Archive,O.Field (Archive,Encoded,"type"),E.Operation);
         case Item.Form is
            when V.Null_Value | V.Boolean_Value | V.String_Value =>
               Value := E.Decode (Archive,O.Field (Archive,Encoded,"value"),E.Operation);
               if not E.Text_Is (Archive,Typ,
                 (if Item.Form = V.Null_Value then "NoneType" elsif Item.Form = V.Boolean_Value then "bool" else "str")) then return False; end if;
            when V.Array_Value =>
               if not E.Text_Is (Archive,Typ,"list") then return False; end if;
               Value := E.Decode (Archive,O.Field (Archive,Encoded,"items"),E.Operation);
            when V.Object_Value =>
               if not E.Text_Is (Archive,Typ,"dict") then return False; end if;
               Value := E.Decode (Archive,O.Field (Archive,Encoded,"fields"),E.Operation);
            when V.Integer_Value | V.Number_Value => null;
            when V.Missing => return False;
         end case;
      end if;
      case Item.Form is
         when V.Null_Value => return Value.Form = E.Null_Value;
         when V.Boolean_Value => return Value.Form = E.Boolean_Value and then Value.Boolean_Bit = V.Is_True (Data,Item);
         when V.String_Value => return Text_Matches (Data,Item,Archive,Value);
         when V.Integer_Value | V.Number_Value =>
            declare
               Token : constant String := V.Slice (Data,Item);
               N : constant Exact_Decimal.Number := Native_Number (Data,Item);
            begin
               if not N.Valid and then Token not in "NaN" | "Infinity" | "-Infinity" then return False; end if;
               if N.Valid and then N.After /= P.Count (Token'Length) then return False; end if;
               if Item.Form = V.Number_Value then
                  declare
                     C : Decimal_Binary64.Conversion := Decimal_Binary64.No_Conversion;
                     Bits, Expected : Interfaces.Unsigned_64 := 0;
                  begin
                     if N.Valid then
                        if not N.Floating then return False; end if;
                        C := Decimal_Binary64.Convert (N);
                        Expected := (if C.Valid then C.Encoding elsif N.Negative then
                          Decimal_Binary64.Sign_Bit + Decimal_Binary64.Infinity else Decimal_Binary64.Infinity);
                     elsif Token = "Infinity" then Expected := Decimal_Binary64.Infinity;
                     elsif Token = "-Infinity" then Expected := Decimal_Binary64.Sign_Bit + Decimal_Binary64.Infinity;
                     end if;
                     if Scoped then
                        if not E.Text_Is (Archive,Typ,"float") then return False; end if;
                        Value := E.Decode (Archive,O.Field (Archive,Encoded,"bits"),E.Operation);
                        if Value.Form /= E.Text_Value then return False; end if;
                     elsif Value.Form /= E.Float_Value then return False;
                     end if;
                     if not E.Bytes_Valid (Archive,Value.Payload) then return False; end if;
                     declare Raw : constant P.Bytes := E.Materialize (Archive,Value.Payload); begin
                        if Raw'Length /= (if Scoped then 16 else 8) then return False; end if;
                        for K in Raw'Range loop
                           if Scoped then
                              declare D : constant Integer := Hex (Raw (K)); begin
                                 if D < 0 then return False; end if;
                                 Bits := Bits * 16 + Interfaces.Unsigned_64 (D);
                              end;
                           else Bits := Bits * 256 + Interfaces.Unsigned_64 (Raw (K));
                           end if;
                        end loop;
                     end;
                     -- NaN JSON is an intentionally lossy textual projection;
                     -- the authentic full archive must retain payload/sign bits
                     -- independently. This relation grants no float identity.
                     return (if Token = "NaN" then Decimal_Binary64.Magnitude (Bits) > Decimal_Binary64.Infinity
                       else Bits = Expected);
                  end;
               else
                  declare
                     Negative : constant Boolean := N.Negative and then N.Coefficient /= 0;
                     Magnitude : Big_Integer := To_Big_Integer (0);
                  begin
                     if Scoped then
                        if not E.Text_Is (Archive,Typ,"integer") then return False; end if;
                        Value := E.Decode (Archive,O.Field (Archive,Encoded,"negative"),E.Operation);
                        if Value.Form /= E.Boolean_Value or else Value.Boolean_Bit /= Negative then return False; end if;
                        Value := E.Decode (Archive,O.Field (Archive,Encoded,"magnitude"),E.Operation);
                        if Value.Form /= E.Text_Value then return False; end if;
                     elsif Value.Form /= E.Integer_Value or else Value.Sign /= Negative then return False;
                     end if;
                     if not E.Bytes_Valid (Archive,Value.Payload) then return False; end if;
                     declare Raw : constant P.Bytes := E.Materialize (Archive,Value.Payload); Position : P.Count := Raw'Length; begin
                        if Scoped and then Position mod 2 /= 0 then return False; end if;
                        while Position > 0 loop
                           pragma Loop_Variant (Decreases => Position);
                           if Scoped then
                              Position := Position - 2;
                              declare Hi : constant Integer := Hex (Raw (Raw'First + Position));
                                      Lo : constant Integer := Hex (Raw (Raw'First + Position + 1)); begin
                                 if Hi < 0 or else Lo < 0 then return False; end if;
                                 Magnitude := Magnitude * To_Big_Integer (256) + To_Big_Integer (Hi * 16 + Lo);
                              end;
                           else
                              Position := Position - 1;
                              Magnitude := Magnitude * To_Big_Integer (256) + To_Big_Integer (Integer (Raw (Raw'First + Position)));
                           end if;
                        end loop;
                     end;
                     return Magnitude = N.Coefficient;
                  end;
               end if;
            end;
         when V.Array_Value | V.Object_Value =>
            if (Item.Form = V.Array_Value and then Value.Form /= E.List_Value) or else
              (Item.Form = V.Object_Value and then Value.Form /= E.Object_Value) then return False; end if;
            Children := E.Array_Length (Archive,Value.Children);
            if Children /= P.Count (V.Count (Data,Item)) then return False; end if;
            for K in 1 .. V.Count (Data,Item) loop
               Child := E.Array_Element (Archive,Value.Children,P.Count (K - 1));
               if Item.Form = V.Object_Value then
                  if Python_Equality or else Object_Order_Independent then
                     declare
                        Key : constant V.Node := V.Member_Key (Data,Item,K);
                        Found : Boolean := False;
                     begin
                        for Ordinal in P.Count range 0 .. Children - 1 loop
                           declare
                              Candidate : constant P.Span := E.Array_Element (Archive,Value.Children,Ordinal);
                              Entry_View : constant E.View := E.Decode
                                (Archive,Candidate,(if At_Layer = E.Finalization then E.Terminal else E.Finalization));
                           begin
                              if Entry_View.Form = E.List_Value and then E.Array_Length (Archive,Entry_View.Children) = 2
                                and then Text_Matches (Data,Key,Archive,E.Decode
                                  (Archive,E.Array_Element (Archive,Entry_View.Children,0),
                                   (if At_Layer = E.Finalization then E.Terminal else E.Operation))) then
                                 Child := Candidate; Found := True; exit;
                              end if;
                           end;
                        end loop;
                        if not Found then return False; end if;
                     end;
                  end if;
                  Pair := E.Decode (Archive,Child,
                    (if At_Layer = E.Finalization then E.Terminal else E.Finalization));
                  if Pair.Form /= E.List_Value or else E.Array_Length (Archive,Pair.Children) /= 2 then return False; end if;
                  declare Key : constant V.Node := V.Member_Key (Data,Item,K); begin
                     if not Text_Matches (Data,Key,Archive,E.Decode
                       (Archive,E.Array_Element (Archive,Pair.Children,0),
                        (if At_Layer = E.Finalization then E.Terminal else E.Operation))) then return False; end if;
                     if not Match_Tree (Data,V.Field (Data,Item,V.Text (Data,Key)),Archive,
                       E.Array_Element (Archive,Pair.Children,1),Scoped,Python_Equality,
                       Object_Order_Independent,At_Layer) then return False; end if;
                  end;
               elsif not Match_Tree (Data,V.Element (Data,Item,K),Archive,Child,
                 Scoped,Python_Equality,Object_Order_Independent,At_Layer) then return False;
               end if;
            end loop;
            return True;
         when V.Missing => return False;
      end case;
   end Match_Tree;

   function Matches
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span; Scoped, Exact : Boolean;
      Python_Equality : Boolean := False; Object_Order_Independent : Boolean := False)
      return Boolean is
      Decoded : constant Decoded_JSON := Decode_JSON (JSON_Data,JSON_Value);
   begin
      if not Decoded.Valid or else V.Parse (Decoded.Data).Form = V.Missing
        or else (Exact and then not V.Original_Exact_JSON (Decoded.Data))
        or else not P.Valid (Archive_Data,Encoded) then return False; end if;
      if Scoped then if not S.Valid (Archive_Data,Encoded) then return False; end if;
      elsif not O.Valid (Archive_Data,Encoded) then return False;
      end if;
      return Match_Tree (Decoded.Data,V.Parse (Decoded.Data),Archive_Data,Encoded,
        Scoped,Python_Equality,Object_Order_Independent);
   end Matches;
   function Raw_JSON_Operation_Matches
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span) return Boolean is
     (Matches (JSON_Data,Archive_Data,JSON_Value,Encoded,False,True));
   function Raw_JSON_Scoped_Matches
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span) return Boolean is
     (Matches (JSON_Data,Archive_Data,JSON_Value,Encoded,True,True));
   function Ordinary_JSON_Operation_Matches
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span) return Boolean is
     (Matches (JSON_Data,Archive_Data,JSON_Value,Encoded,False,False));
   function Ordinary_JSON_Scoped_Matches
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span) return Boolean is
     (Matches (JSON_Data,Archive_Data,JSON_Value,Encoded,True,False));
   function JSON_Source_Value_Matches
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span;
      Canonical, Scoped : Boolean) return Boolean
   is
      Decoded : constant Decoded_JSON := Decode_JSON (JSON_Data,JSON_Value);
   begin
      return Decoded.Valid and then
        (not Canonical or else Canonical_ASCII_Valid (Decoded.Data)) and then
        Matches (JSON_Data,Archive_Data,JSON_Value,Encoded,Scoped,False,False,True);
   end JSON_Source_Value_Matches;
   function Ordinary_JSON_Finalization_Matches
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span) return Boolean
   is
      Decoded : constant Decoded_JSON := Decode_JSON (JSON_Data,JSON_Value);
   begin
      return Decoded.Valid and then P.Valid (Archive_Data,Encoded) and then
        Match_Tree (Decoded.Data,V.Parse (Decoded.Data),Archive_Data,Encoded,
          False,False,True,E.Finalization);
   end Ordinary_JSON_Finalization_Matches;
   function Raw_JSON_Operation_Equal
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span) return Boolean is
     (Matches (JSON_Data,Archive_Data,JSON_Value,Encoded,False,True,True));
   function Raw_JSON_Scoped_Equal
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span) return Boolean is
     (Matches (JSON_Data,Archive_Data,JSON_Value,Encoded,True,True,True));

   function Scalar_Code (Text : String; Offset, Width : Natural) return Natural is
      Code : Natural := Character'Pos (Text (Text'First + Offset));
   begin
      if Width > 1 then
         Code := Code mod (if Width = 2 then 32 elsif Width = 3 then 16 else 8);
         for K in 1 .. Width - 1 loop Code := Code * 64 + Character'Pos (Text (Text'First + Offset + K)) mod 64; end loop;
      end if;
      return Code;
   end Scalar_Code;
   function Hex_Unit (C : Natural) return String is
      Hexes : constant String := "0123456789abcdef";
   begin
      return "\u" & Hexes (C / 4096 mod 16 + 1) & Hexes (C / 256 mod 16 + 1)
        & Hexes (C / 16 mod 16 + 1) & Hexes (C mod 16 + 1);
   end Hex_Unit;
   function ASCII_Piece (Code : Natural) return String is
     (if Code = 34 then "\""" elsif Code = 92 then "\\"
      elsif Code = 8 then "\b" elsif Code = 9 then "\t" elsif Code = 10 then "\n"
      elsif Code = 12 then "\f" elsif Code = 13 then "\r"
      elsif Code in 32 .. 126 then String'(1 => Character'Val (Code))
      elsif Code <= 65535 then Hex_Unit (Code)
      else Hex_Unit (16#D800# + (Code - 65536) / 1024) & Hex_Unit (16#DC00# + (Code - 65536) mod 1024));
   function Canonical_ASCII_Quote (Text : String) return String is
      Offset, Length, Width : Natural := 0;
   begin
      while Offset < Text'Length loop
         Width := V.UTF8_Width (Text,Offset);
         if Width = 0 then return ""; end if;
         Length := Length + ASCII_Piece (Scalar_Code (Text,Offset,Width))'Length;
         Offset := Offset + Width;
      end loop;
      declare Result : String (1 .. Length + 2); Used : Natural := 1; begin
         Result (1) := '"'; Offset := 0;
         while Offset < Text'Length loop
            Width := V.UTF8_Width (Text,Offset);
            declare Piece : constant String := ASCII_Piece (Scalar_Code (Text,Offset,Width)); begin
               Result (Used + 1 .. Used + Piece'Length) := Piece; Used := Used + Piece'Length;
            end;
            Offset := Offset + Width;
         end loop;
         Result (Result'Last) := '"'; return Result;
      end;
   end Canonical_ASCII_Quote;

   function Canonical_ASCII_Valid (Data : String) return Boolean is
      Root : constant V.Node := V.Parse (Data);
      function Byte (Offset : Natural) return Character is
        (if Offset < Data'Length then Data (Data'First + Offset) else Character'Val (0));
      function String_Canonical (Item : V.Node) return Boolean is
         Text : constant String := V.Text (Data,Item);
         Offset : Natural := 0;
         Position : Natural := Item.First;
         Width, Code : Natural;
         function Consume (Piece : String) return Boolean is
           (Piece'Length <= Item.Last - Position and then
             Data (Data'First + Position .. Data'First + Position + Piece'Length - 1) = Piece);
      begin
         while Offset < Text'Length loop
            Width := V.UTF8_Width (Text,Offset);
            if Width = 0 then return False; end if;
            Code := Scalar_Code (Text,Offset,Width);
            declare Piece : constant String := ASCII_Piece (Code);
            begin
               if not Consume (Piece) then return False; end if;
               Position := Position + Piece'Length;
            end;
            Offset := Offset + Width;
         end loop;
         return Position = Item.Last - 1;
      end String_Canonical;
      function Canonical (Item : V.Node) return Boolean
        with Subprogram_Variant => (Decreases => Item.Last - Natural'Min (Item.First,Item.Last));
      function Canonical (Item : V.Node) return Boolean is
         Position : Natural := Item.First;
         Child, Key, Prior : V.Node := V.No_Node;
      begin
         case Item.Form is
            when V.Missing => return False;
            when V.Null_Value | V.Boolean_Value => return True;
            when V.String_Value => return String_Canonical (Item);
            when V.Integer_Value | V.Number_Value => return V.Slice (Data,Item) = V.Number_Image (Data,Item);
            when V.Array_Value | V.Object_Value =>
               for K in 1 .. V.Count (Data,Item) loop
                  if Item.Form = V.Object_Value then
                     Key := V.Member_Key (Data,Item,K);
                     if Key.First /= Position + 1 or else not String_Canonical (Key)
                       or else Byte (Key.Last) /= ':' then return False; end if;
                     if Prior.Form /= V.Missing and then not (V.Text (Data,Prior) < V.Text (Data,Key)) then return False; end if;
                     Prior := Key; Position := Key.Last + 1;
                     Child := V.Field (Data,Item,V.Text (Data,Key));
                  else Child := V.Element (Data,Item,K);
                  end if;
                  if Child.First /= Position + 1 or else not Canonical (Child) then return False; end if;
                  Position := Child.Last;
                  if K < V.Count (Data,Item) then
                     if Byte (Position) /= ',' then return False; end if;
                     Position := Position + 1;
                  end if;
               end loop;
               return Position = Item.Last - 1;
         end case;
      end Canonical;
   begin
      return V.Original_Exact_JSON (Data) and then Root.First = 1 and then
        (Root.Last = Data'Length or else
          (Root.Last < Data'Length and then Data'Length - Root.Last = 1 and then Byte (Root.Last) = Character'Val (10)))
        and then Canonical (Root);
   end Canonical_ASCII_Valid;
end Worldline.Raw_JSON;
