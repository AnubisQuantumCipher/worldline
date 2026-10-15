with Worldline.Producer_Values;

-- SOURCE-ONLY PROPOSED FIXTURES. Not run by their preparer. Expectations are
-- fixture literals/properties, not calls to a candidate reference decoder.
procedure String_Parser_Controls with SPARK_Mode is
   package P renames Worldline.Producer_Values;
   use type P.Value_Kind;
   Q : constant Character := '"';
   B : constant Character := '\';
   HT : constant Character := Character'Val (9);
   LF : constant Character := Character'Val (10);
   CR : constant Character := Character'Val (13);
   WS : constant String := ' ' & HT & LF & CR;
   True_Token : constant String := "true";
   Spaced : constant String := WS & "true" & WS;
   Shifted : constant String (7 .. 10) := "null";
   Endpoint : constant String (Positive'Last - 3 .. Positive'Last) := "null";
   Simple_Escapes : constant String :=
     Q & B & Q & B & B & B & '/' & B & 'b' & B & 'f' &
     B & 'n' & B & 'r' & B & 't' & B & "u0041" & Q;
   Escaped_Result : constant String :=
     Q & B & '/' & Character'Val (8) & Character'Val (12) & LF & CR & HT & 'A';
   Surrogate : constant String :=
     Character'Val (16#ED#) & Character'Val (16#A0#) & Character'Val (16#80#);
   Multi_Byte : constant String :=
     Character'Val (16#C2#) & Character'Val (16#A2#);
   BOM : constant String :=
     Character'Val (16#EF#) & Character'Val (16#BB#) & Character'Val (16#BF#);
   Huge_Integer : constant String := "1234567890123456789012345678901234567890";
   Dup : constant String := "{""x"":1,""x"":2}";
   Escaped_Dup : constant String := "{""x"":1,""\u0078"":2}";
   Unique : constant String := "{""x"":2}";
   Object_Data : constant String := "{""b"":false,""a"":null}";
   Array_Data : constant String := "[null,true,false,0,-0,1.5,""a"",[],{}]";
begin
   -- Every top-level syntax alternative, including the original nonfinite set.
   pragma Assert (P.Parse ("null").Form = P.Null_Value, "null");
   pragma Assert (P.Parse ("true").Form = P.Boolean_Value, "true");
   pragma Assert (P.Parse ("false").Form = P.Boolean_Value, "false");
   pragma Assert (P.Parse ("0").Form = P.Integer_Value, "zero");
   pragma Assert (P.Parse ("-0").Form = P.Integer_Value, "negative zero integer");
   pragma Assert (P.Parse ("123").Form = P.Integer_Value, "nonzero digits");
   pragma Assert (P.Parse ("-123").Form = P.Integer_Value, "minus digits");
   pragma Assert (P.Parse (Huge_Integer).Form = P.Integer_Value, "long finite fixture token");
   pragma Assert (P.Parse ("0.5").Form = P.Number_Value, "fraction");
   pragma Assert (P.Parse ("1e2").Form = P.Number_Value, "lower exponent");
   pragma Assert (P.Parse ("1E+2").Form = P.Number_Value, "upper positive exponent");
   pragma Assert (P.Parse ("-1.25e-2").Form = P.Number_Value, "fraction negative exponent");
   pragma Assert (P.Parse ("NaN").Form = P.Number_Value, "NaN");
   pragma Assert (P.Parse ("Infinity").Form = P.Number_Value, "Infinity");
   pragma Assert (P.Parse ("-Infinity").Form = P.Number_Value, "negative Infinity");
   pragma Assert (P.Parse (Q & Q).Form = P.String_Value, "empty string");
   pragma Assert (P.Parse (Q & "abc" & Q).Form = P.String_Value, "ASCII string");
   pragma Assert (P.Parse (Simple_Escapes).Form = P.String_Value, "simple and unicode escapes");
   pragma Assert (P.Parse (Q & B & "u00aF" & Q).Form = P.String_Value, "mixed hex case");
   pragma Assert (P.Parse (Q & B & "uD800" & Q).Form = P.String_Value, "escaped lone high surrogate");
   pragma Assert (P.Parse (Q & B & "uDC00" & Q).Form = P.String_Value, "escaped lone low surrogate");
   pragma Assert (P.Parse (Q & B & "uD800" & B & "uDC00" & Q).Form = P.String_Value, "escaped pair syntax");
   pragma Assert (P.Parse (Q & Multi_Byte & Q).Form = P.String_Value, "raw canonical multibyte");
   pragma Assert (P.Parse (Q & Surrogate & Q).Form = P.String_Value, "raw surrogatepass");
   pragma Assert (P.Parse ("[]").Form = P.Array_Value, "empty array");
   pragma Assert (P.Parse ("{}").Form = P.Object_Value, "empty object");
   pragma Assert (P.Parse (Array_Data).Form = P.Array_Value, "all nested kinds");
   pragma Assert (P.Parse ("{""k"":[{},[true],""x""]}").Form = P.Object_Value, "nested object");

   -- Original byte-relative String Node coordinates; array origin is irrelevant.
   declare N : constant P.Node := P.Parse (Spaced); begin
      pragma Assert (N.Form = P.Boolean_Value, "all original whitespace");
      pragma Assert (N.First = WS'Length + 1, "leading whitespace first");
      pragma Assert (N.Last = WS'Length + True_Token'Length, "token last before trailing whitespace");
      pragma Assert (P.Slice (Spaced, N) = "true", "spaced token slice");
   end;
   declare N : constant P.Node := P.Parse (Shifted); begin
      pragma Assert (N.Form = P.Null_Value and then N.First = 1 and then N.Last = Shifted'Length, "shifted String origin");
   end;
   declare N : constant P.Node := P.Parse (Endpoint); begin
      pragma Assert (N.Form = P.Null_Value and then N.First = 1 and then N.Last = Endpoint'Length, "finite String endpoint origin");
   end;

   -- Malformed/partial tokens cannot be promoted to complete JSON.
   pragma Assert (P.Parse ("").Form = P.Missing, "empty input");
   pragma Assert (P.Parse (WS).Form = P.Missing, "whitespace only");
   pragma Assert (P.Parse ("nullx").Form = P.Missing, "literal suffix");
   pragma Assert (P.Parse ("tru").Form = P.Missing, "truncated literal");
   pragma Assert (P.Parse ("falsX").Form = P.Missing, "bad literal");
   pragma Assert (P.Parse ("NaNx").Form = P.Missing, "nonfinite suffix");
   pragma Assert (P.Parse ("Infinit").Form = P.Missing, "truncated nonfinite");
   pragma Assert (P.Parse ("-Infinit").Form = P.Missing, "truncated negative nonfinite");
   pragma Assert (P.Parse ("+").Form = P.Missing, "leading plus");
   pragma Assert (P.Parse ("-").Form = P.Missing, "minus only");
   pragma Assert (P.Parse ("01").Form = P.Missing, "leading zero suffix");
   pragma Assert (P.Parse ("-01").Form = P.Missing, "negative leading zero suffix");
   pragma Assert (P.Parse ("1.").Form = P.Missing, "missing fraction digit");
   pragma Assert (P.Parse ("1e").Form = P.Missing, "missing exponent");
   pragma Assert (P.Parse ("1e+").Form = P.Missing, "missing signed exponent");
   pragma Assert (P.Parse ("1e-").Form = P.Missing, "missing negative exponent");
   pragma Assert (P.Parse ("[1,]").Form = P.Missing, "array trailing comma");
   pragma Assert (P.Parse ("{""x"":1,}").Form = P.Missing, "object trailing comma");
   pragma Assert (P.Parse ("{""x"" 1}").Form = P.Missing, "missing colon");
   pragma Assert (P.Parse ("{1:2}").Form = P.Missing, "non-string key");
   pragma Assert (P.Parse ("[1}").Form = P.Missing, "wrong close");
   pragma Assert (P.Parse ("[1").Form = P.Missing, "missing close");
   pragma Assert (P.Parse ("[]x").Form = P.Missing, "container suffix");
   pragma Assert (P.Parse ("true false").Form = P.Missing, "multiple roots");
   pragma Assert (P.Parse (Q & "x").Form = P.Missing, "unclosed string");
   pragma Assert (P.Parse (Q & B).Form = P.Missing, "trailing escape");
   pragma Assert (P.Parse (Q & B & 'x' & Q).Form = P.Missing, "unknown escape");
   pragma Assert (P.Parse (Q & B & "u123" & Q).Form = P.Missing, "short unicode escape");
   pragma Assert (P.Parse (Q & B & "u00g0" & Q).Form = P.Missing, "nonhex unicode escape");
   pragma Assert (P.Parse (Q & LF & Q).Form = P.Missing, "raw control inside string");
   pragma Assert (P.Parse (Q & Character'Val (0) & Q).Form = P.Missing, "raw NUL");
   pragma Assert (P.Parse (Q & Character'Val (16#80#) & Q).Form = P.Missing, "stray continuation");
   pragma Assert (P.Parse (Q & Character'Val (16#C0#) & Character'Val (16#80#) & Q).Form = P.Missing, "overlong UTF8");
   pragma Assert (P.Parse (Q & Character'Val (16#E2#) & Character'Val (16#82#)).Form = P.Missing, "truncated UTF8");
   pragma Assert (P.Parse (Q & Character'Val (16#F4#) & Character'Val (16#90#) & Character'Val (16#80#) & Character'Val (16#80#) & Q).Form = P.Missing, "out-of-range UTF8");
   pragma Assert (P.Parse (BOM & "null").Form = P.Missing, "String parser does not strip BOM");
   pragma Assert (P.Parse (Multi_Byte & "null").Form = P.Missing, "non-ASCII before token");
   pragma Assert (P.Parse ("null" & Character'Val (0)).Form = P.Missing, "malformed complete suffix");

   -- Existing selectors and admission predicates stay distinct.
   pragma Assert (P.Parse (Dup).Form = P.Object_Value, "ordinary duplicate parse");
   pragma Assert (P.Standard_JSON (Dup), "ordinary duplicates remain standard syntax");
   pragma Assert (not P.Duplicate_Free (Dup), "duplicate predicate");
   pragma Assert (not P.Original_Exact_JSON (Dup), "original exact duplicate refusal");
   pragma Assert (P.Field (Dup, "x") = "2", "last duplicate wins");
   pragma Assert (P.Count (Dup) = 1, "count unique decoded keys");
   pragma Assert (P.Field (Escaped_Dup, "x") = "2", "escaped equivalent duplicate wins");
   pragma Assert (P.Count (Escaped_Dup) = 1 and then not P.Duplicate_Free (Escaped_Dup), "decoded-key uniqueness");
   pragma Assert (P.Original_Exact_JSON (Unique), "unique standard object");
   pragma Assert (P.Equal (Dup, Unique), "duplicate object equality uses last value");
   pragma Assert (P.Equal (Object_Data, "{""a"":null,""b"":false}"), "object order independence");
   pragma Assert (not P.Equal ("[1,2]", "[2,1]"), "array order retained");
   pragma Assert (not P.Equal ("1", "1.0"), "original syntax-value equality keeps numeric kinds");
   pragma Assert (not P.Equal ("0", "-0"), "original integer equality keeps token spelling");
   pragma Assert (P.Equal (Q & "A" & Q, Q & B & "u0041" & Q), "decoded text equality");
   pragma Assert (P.Member_Name (Object_Data, P.Parse (Object_Data), 1) = "b", "member order first");
   pragma Assert (P.Member_Name (Object_Data, P.Parse (Object_Data), 2) = "a", "member order second");
   pragma Assert (P.Kind (Object_Data) = P.Object_Value, "Kind convenience API");
   pragma Assert (P.Is_False (Object_Data, P.Field (Object_Data, P.Parse (Object_Data), "b")), "Field node API");
   pragma Assert (P.Count (Object_Data, P.Parse (Object_Data)) = 2, "Count node API");
   pragma Assert (P.Text (Object_Data, P.Member_Key (Object_Data, P.Parse (Object_Data), 1)) = "b", "member key node");
   pragma Assert (P.Field (Object_Data, "absent") = "", "absent field");
   pragma Assert (P.Element ("[false,true]", 0) = "false", "zero-based convenience element");
   pragma Assert (P.Is_True ("[false,true]", P.Element ("[false,true]", P.Parse ("[false,true]"), 2)), "one-based node element");
   pragma Assert (P.Element ("[]", 0) = "", "absent element");
   pragma Assert (P.Count ("[]") = 0 and then P.Count ("{}") = 0, "empty counts");
   pragma Assert (not P.Standard_JSON ("NaN") and then P.Duplicate_Free ("NaN"), "NaN predicate distinction");
   pragma Assert (not P.Standard_JSON ("Infinity") and then not P.Standard_JSON ("-Infinity"), "infinity standard refusal");
   pragma Assert (not P.Original_Exact_JSON ("[NaN]"), "nested nonfinite refusal");

   -- Actual retained text/numeric/render dependencies, no substitute models.
   pragma Assert (P.Text (Simple_Escapes) = Escaped_Result, "all escape decoded values");
   pragma Assert (P.Text (Q & B & "uD800" & Q) = Surrogate, "lone surrogate emitted unchanged");
   pragma Assert (P.Is_Text (Q & "A" & Q, P.Parse (Q & "A" & Q), "A"), "Is_Text");
   pragma Assert (P.Nonempty_Text (Q & "A" & Q, P.Parse (Q & "A" & Q)), "nonempty text");
   pragma Assert (not P.Nonempty_Text (Q & B & "u0000" & Q, P.Parse (Q & B & "u0000" & Q)), "NUL text is not nonempty-text predicate");
   pragma Assert (P.Is_False ("false", P.Parse ("false")), "Is_False");
   pragma Assert (P.Is_Null (P.Parse ("null")), "Is_Null");
   pragma Assert (P.Present (P.Parse ("0")) and then not P.Present (P.Parse ("bad")), "Present");
   pragma Assert (P.Equal ("true", P.Parse ("true"), "true", P.Parse ("true")), "Equal node API");
   pragma Assert (P.Truth ("true", P.Parse ("true")), "Truth node API");
   pragma Assert (P.Decimal (Huge_Integer, P.Parse (Huge_Integer)) = Huge_Integer, "integer token retained");
   pragma Assert (P.Nonnegative ("-0", P.Parse ("-0")) and then not P.Nonnegative ("-1", P.Parse ("-1")), "nonnegative signed zero");
   pragma Assert (P.Number_Image (Huge_Integer, P.Parse (Huge_Integer)) = Huge_Integer, "long integer image");
   pragma Assert (P.Number_Image ("-0", P.Parse ("-0")) = "0", "integer negative-zero image");
   pragma Assert (P.Number_Image ("1.5", P.Parse ("1.5")) = "1.5", "finite exact decimal and binary64 path");
   pragma Assert (P.Number_Image ("-0.0", P.Parse ("-0.0")) = "-0.0", "binary64 negative-zero image");
   pragma Assert (P.Number_Image ("NaN", P.Parse ("NaN")) = "nan", "NaN image");
   pragma Assert (P.Number_Image ("Infinity", P.Parse ("Infinity")) = "inf", "positive infinity image");
   pragma Assert (P.Number_Image ("-Infinity", P.Parse ("-Infinity")) = "-inf", "negative infinity image");
   pragma Assert (not P.Truth ("null") and then not P.Truth ("false") and then not P.Truth ("0") and then not P.Truth ("-0.0"), "false values");
   pragma Assert (P.Truth ("true") and then P.Truth ("1") and then P.Truth ("NaN") and then P.Truth ("[0]"), "true values");
   pragma Assert (P.Quote ("A" & LF) = Q & "A" & B & 'n' & Q, "actual JSON rendering");
   pragma Assert (P.Python_String ("[null,true,false]") = "[None, True, False]", "actual Python rendering");
   pragma Assert (P.Python_String (Q & "A" & Q) = "A", "Python String value");
end String_Parser_Controls;
