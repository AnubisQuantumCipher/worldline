with Canonical_Artifacts;
with Exact_Decimal;
with Decimal_Binary64;
with Interfaces;

--  Additive SPARK caller/control. The public evaluation artifact grammar MUST
--  remain nonfloat even after the genesis-only internal parser gains floats.
procedure Genesis_Float_Domain_Controls with SPARK_Mode is
   package A renames Canonical_Artifacts;
   use type A.Count;
   use type A.Bytes;
   use type A.JSON_Kind;
   use type Interfaces.Unsigned_64;
   Float_Token : constant A.Bytes (1 .. 3) := (49, 46, 48); -- 1.0
   Nested : constant A.Bytes (1 .. 5) := (91, 49, 46, 48, 93); -- [1.0]
   Integer_Token : constant A.Bytes (1 .. 1) := (1 => 49); -- 1
   Token : constant Exact_Decimal.Number := Exact_Decimal.Parse (Float_Token, (1, 3), 0);
   Converted : constant Decimal_Binary64.Conversion := Decimal_Binary64.Canonical (Float_Token, (1, 3));
   Partial : constant A.Node := A.Prefix (Float_Token, (1, 3), 0);
   --  {"body":{"a":1.0},"mac":"x"}; original body value occupies bytes9..17.
   Envelope : constant A.Bytes (1 .. 28) :=
     (123,34,98,111,100,121,34,58,123,34,97,34,58,49,46,48,125,44,
      34,109,97,99,34,58,34,120,34,125);
   Envelope_LF : constant A.Bytes (1 .. 29) := Envelope & A.Bytes'(1 => 10);
   Body_Span : constant A.Span := A.Canonical_JSON_Field (Envelope, (1, 28), "body");
   Body_LF : constant A.Span := A.Canonical_JSON_Field (Envelope_LF, (1, 29), "body");
   JSON_Float : constant A.JSON_Node := A.JSON_Prefix (Float_Token, (1, 3), 0);
   JSON_Integer : constant A.JSON_Node := A.JSON_Prefix (Integer_Token, (1, 1), 0);
begin
   pragma Assert (not A.Canonical (Float_Token, (1, 3)));
   pragma Assert (not A.Canonical (Nested, (1, 5)));
   pragma Assert (A.Canonical (Integer_Token, (1, 1)));
   pragma Assert (Partial.Valid and then Partial.After = 1);
   pragma Assert (Token.Valid and then Token.Floating and then Token.After = 3);
   pragma Assert (Converted.Valid and then Converted.Encoding = 16#3FF0_0000_0000_0000#);
   pragma Assert (not A.Field (Envelope, (1, 28), "body").Found);
   pragma Assert (Body_Span.First = 9 and then Body_Span.Length = 9);
   pragma Assert (Body_LF.First = Body_Span.First and then Body_LF.Length = Body_Span.Length);
   pragma Assert (A.Canonical_JSON_Field (Envelope, (1, 28), "absent").Length = 0);
   pragma Assert (A.Canonical_JSON_Field (Nested, (1, 5), "body").Length = 0);
   pragma Assert (JSON_Float.Valid and then JSON_Float.Form = A.Float_JSON_Value);
   pragma Assert (JSON_Integer.Valid and then JSON_Integer.Form = A.Integer_JSON_Value);
   pragma Assert (A.Canonical_JSON_Valid (Envelope, (1, 28)));
   pragma Assert (A.Canonical_JSON_Valid (Envelope_LF, (1, 29)));
   pragma Assert (A.Canonical_JSON_Valid (Nested, (1, 5)));
end Genesis_Float_Domain_Controls;
