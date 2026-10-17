with Resource_Quantities;
with Worldline.JSON_Source_Cursor;
with Worldline.JSON_Syntax_Types;
with Worldline.Raw_JSON_Syntax;

-- Independent literal-byte fixtures. No original/reference Parse or decode
-- result is used to manufacture an expected result. Not executed.
procedure Wide_Parser_Controls with SPARK_Mode is
   package Q renames Resource_Quantities;
   package C renames Worldline.JSON_Source_Cursor;
   package J renames Worldline.JSON_Syntax_Types;
   package R renames Worldline.Raw_JSON_Syntax;
   use type Q.Byte_Count;
   use type J.Value_Kind;
   Empty : constant Q.Byte_Array (1 .. 0) := [others => 0];
   UTF8_Array : constant Q.Byte_Array := [16#5B#, 16#5D#];
   UTF8_BOM_Array : constant Q.Byte_Array := [16#EF#, 16#BB#, 16#BF#, 16#5B#, 16#5D#];
   UTF16_BE_Array : constant Q.Byte_Array := [16#FE#, 16#FF#, 0, 16#5B#, 0, 16#5D#];
   UTF16_LE_Array : constant Q.Byte_Array := [16#FF#, 16#FE#, 16#5B#, 0, 16#5D#, 0];
   UTF32_BE_Array : constant Q.Byte_Array := [0, 0, 16#FE#, 16#FF#, 0, 0, 0, 16#5B#, 0, 0, 0, 16#5D#];
   UTF32_LE_Array : constant Q.Byte_Array := [16#FF#, 16#FE#, 0, 0, 16#5B#, 0, 0, 0, 16#5D#, 0, 0, 0];
   Bare16_BE : constant Q.Byte_Array := [0, 16#5B#, 0, 16#5D#];
   Bare16_LE : constant Q.Byte_Array := [16#5B#, 0, 16#5D#, 0];
   Bare32_BE : constant Q.Byte_Array := [0, 0, 0, 16#5B#, 0, 0, 0, 16#5D#];
   Bare32_LE : constant Q.Byte_Array := [16#5B#, 0, 0, 0, 16#5D#, 0, 0, 0];
   Two16_BE : constant Q.Byte_Array := [0, 16#30#];
   Two16_LE : constant Q.Byte_Array := [16#30#, 0];
   UTF8_Surrogate : constant Q.Byte_Array := [16#22#, 16#ED#, 16#A0#, 16#80#, 16#22#];
   UTF16_BE_Surrogate : constant Q.Byte_Array := [16#FE#, 16#FF#, 0, 16#22#, 16#D8#, 0, 0, 16#22#];
   UTF16_LE_Low : constant Q.Byte_Array := [16#FF#, 16#FE#, 16#22#, 0, 0, 16#DC#, 16#22#, 0];
   UTF16_BE_Pair : constant Q.Byte_Array := [16#FE#, 16#FF#, 0, 16#22#, 16#D8#, 0, 16#DC#, 0, 0, 16#22#];
   UTF32_LE_Surrogate : constant Q.Byte_Array := [16#FF#, 16#FE#, 0, 0, 16#22#, 0, 0, 0, 0, 16#D8#, 0, 0, 16#22#, 0, 0, 0];
   UTF8_Last : constant Q.Byte_Array := [16#22#, 16#F4#, 16#8F#, 16#BF#, 16#BF#, 16#22#];
   UTF32_BE_Last : constant Q.Byte_Array := [0, 0, 16#FE#, 16#FF#, 0, 0, 0, 16#22#, 0, 16#10#, 16#FF#, 16#FF#, 0, 0, 0, 16#22#];
   UTF16_LE_NaN : constant Q.Byte_Array := [16#FF#, 16#FE#, 16#4E#, 0, 16#61#, 0, 16#4E#, 0];
   UTF16_BE_Escape : constant Q.Byte_Array := [16#FE#, 16#FF#, 0, 16#22#, 0, 16#5C#, 0, 16#75#, 0, 16#30#, 0, 16#30#, 0, 16#34#, 0, 16#31#, 0, 16#22#];
   Duplicate_Object : constant Q.Byte_Array := [16#7B#, 16#22#, 16#78#, 16#22#, 16#3A#, 16#30#, 16#2C#, 16#22#, 16#78#, 16#22#, 16#3A#, 16#31#, 16#7D#];
   Spaced : constant Q.Byte_Array := [16#20#, 16#5B#, 16#5D#, 16#0A#];
   Token_Suffix : constant Q.Byte_Array := [16#5B#, 16#5D#, 16#78#];
   Bad_UTF8_Suffix : constant Q.Byte_Array := [16#5B#, 16#5D#, 16#80#];
   Odd16_Suffix : constant Q.Byte_Array := [16#FE#, 16#FF#, 0, 16#5B#, 0, 16#5D#, 0];
   Short32_Suffix : constant Q.Byte_Array := [0, 0, 16#FE#, 16#FF#, 0, 0, 0, 16#5B#, 0, 0, 0, 16#5D#, 0];
   Invalid32_String : constant Q.Byte_Array := [0, 0, 16#FE#, 16#FF#, 0, 0, 0, 16#22#, 0, 16#11#, 0, 0, 0, 0, 0, 16#22#];
   Bad_UTF8_String : constant Q.Byte_Array := [16#22#, 16#C0#, 16#80#, 16#22#];
   Short_UTF8_String : constant Q.Byte_Array := [16#22#, 16#E2#, 16#82#];
   Raw_Control : constant Q.Byte_Array := [16#22#, 16#0A#, 16#22#];
   Short16_String : constant Q.Byte_Array := [16#FE#, 16#FF#, 0, 16#22#, 16#D8#, 0];
   Bad_Escape : constant Q.Byte_Array := [16#22#, 16#5C#, 16#75#, 16#30#, 16#30#, 16#67#, 16#30#, 16#22#];
   Missing_Colon : constant Q.Byte_Array := [16#7B#, 16#22#, 16#78#, 16#22#, 16#30#, 16#7D#];
   Trailing_Comma : constant Q.Byte_Array := [16#5B#, 16#30#, 16#2C#, 16#5D#];
   Short_Exponent : constant Q.Byte_Array := [16#31#, 16#65#, 16#2B#];
   BOM_Only8 : constant Q.Byte_Array := [16#EF#, 16#BB#, 16#BF#];
   BOM_Only16 : constant Q.Byte_Array := [16#FE#, 16#FF#];
   BOM_Only32 : constant Q.Byte_Array := [16#FF#, 16#FE#, 0, 0];
   Double_BOM : constant Q.Byte_Array := [16#EF#, 16#BB#, 16#BF#, 16#EF#, 16#BB#, 16#BF#, 16#30#];
   Three_Byte_NUL : constant Q.Byte_Array := [0, 16#30#, 0];
   Shifted : constant Q.Byte_Array (7 .. 12) := [16#FF#, 0, 16#5B#, 0, 16#5D#, 16#FF#];
   Last_Byte : constant Q.Byte_Array (Q.Byte_Count'Last .. Q.Byte_Count'Last) := [others => 16#30#];
   Last_Array : constant Q.Byte_Array (Q.Byte_Count'Last - 3 .. Q.Byte_Count'Last) := [0, 16#5B#, 0, 16#5D#];
   Unaligned : constant Q.Byte_Array := [16#FF#, 16#30#, 0];
begin
   declare N : constant J.Node := R.Parse (UTF8_Array, (1, UTF8_Array'Length)); begin
      pragma Assert (N.Form = J.Array_Value and then N.First = 0 and then N.After = UTF8_Array'Length, "UTF8 array offsets");
   end;
   declare N : constant J.Node := R.Parse (UTF8_BOM_Array, (1, UTF8_BOM_Array'Length)); begin
      pragma Assert (N.Form = J.Array_Value and then N.First = 3 and then N.After = UTF8_BOM_Array'Length, "UTF8 BOM source offsets");
   end;
   declare N : constant J.Node := R.Parse (UTF16_BE_Array, (1, UTF16_BE_Array'Length)); begin
      pragma Assert (N.Form = J.Array_Value and then N.First = 2 and then N.After = UTF16_BE_Array'Length, "UTF16 BE");
   end;
   declare N : constant J.Node := R.Parse (UTF16_LE_Array, (1, UTF16_LE_Array'Length)); begin
      pragma Assert (N.Form = J.Array_Value and then N.First = 2 and then N.After = UTF16_LE_Array'Length, "UTF16 LE");
   end;
   declare N : constant J.Node := R.Parse (UTF32_BE_Array, (1, UTF32_BE_Array'Length)); begin
      pragma Assert (N.Form = J.Array_Value and then N.First = 4 and then N.After = UTF32_BE_Array'Length, "UTF32 BE");
   end;
   declare N : constant J.Node := R.Parse (UTF32_LE_Array, (1, UTF32_LE_Array'Length)); begin
      pragma Assert (N.Form = J.Array_Value and then N.First = 4 and then N.After = UTF32_LE_Array'Length, "UTF32 LE overlaps UTF16 BOM");
   end;
   pragma Assert (R.Parse (Bare16_BE, (1, Bare16_BE'Length)).Form = J.Array_Value, "BOMless UTF16 BE");
   pragma Assert (R.Parse (Bare16_LE, (1, Bare16_LE'Length)).Form = J.Array_Value, "BOMless UTF16 LE");
   pragma Assert (R.Parse (Bare32_BE, (1, Bare32_BE'Length)).Form = J.Array_Value, "BOMless UTF32 BE");
   pragma Assert (R.Parse (Bare32_LE, (1, Bare32_LE'Length)).Form = J.Array_Value, "BOMless UTF32 LE");
   pragma Assert (R.Parse (Two16_BE, (1, Two16_BE'Length)).Form = J.Integer_Value, "two-byte UTF16 BE heuristic");
   pragma Assert (R.Parse (Two16_LE, (1, Two16_LE'Length)).Form = J.Integer_Value, "two-byte UTF16 LE heuristic");
   pragma Assert (R.Parse (UTF8_Surrogate, (1, UTF8_Surrogate'Length)).Form = J.String_Value, "UTF8 surrogatepass");
   pragma Assert (R.Parse (UTF16_BE_Surrogate, (1, UTF16_BE_Surrogate'Length)).Form = J.String_Value, "UTF16 high surrogatepass");
   pragma Assert (R.Parse (UTF16_LE_Low, (1, UTF16_LE_Low'Length)).Form = J.String_Value, "UTF16 low surrogatepass");
   pragma Assert (R.Parse (UTF16_BE_Pair, (1, UTF16_BE_Pair'Length)).Form = J.String_Value, "UTF16 paired surrogate");
   pragma Assert (R.Parse (UTF32_LE_Surrogate, (1, UTF32_LE_Surrogate'Length)).Form = J.String_Value, "UTF32 surrogatepass");
   pragma Assert (R.Parse (UTF8_Last, (1, UTF8_Last'Length)).Form = J.String_Value, "UTF8 maximum codepoint");
   pragma Assert (R.Parse (UTF32_BE_Last, (1, UTF32_BE_Last'Length)).Form = J.String_Value, "UTF32 maximum codepoint");
   pragma Assert (R.Parse (UTF16_LE_NaN, (1, UTF16_LE_NaN'Length)).Form = J.Number_Value, "encoded NaN accepted ordinary syntax");
   pragma Assert (R.Parse (UTF16_BE_Escape, (1, UTF16_BE_Escape'Length)).Form = J.String_Value, "encoded hex escape");
   pragma Assert (R.Parse (Duplicate_Object, (1, Duplicate_Object'Length)).Form = J.Object_Value, "wide syntax does not reject duplicates");
   declare N : constant J.Node := R.Parse (Spaced, (1, Spaced'Length)); begin
      pragma Assert (N.Form = J.Array_Value and then N.First = 1 and then N.After = 3, "whitespace outside node remains consumed");
   end;

   pragma Assert (R.Parse (Token_Suffix, (1, Token_Suffix'Length)).Form = J.Missing, "ordinary suffix");
   pragma Assert (R.Parse (Bad_UTF8_Suffix, (1, Bad_UTF8_Suffix'Length)).Form = J.Missing, "invalid UTF8 suffix is not EOF");
   pragma Assert (R.Parse (Odd16_Suffix, (1, Odd16_Suffix'Length)).Form = J.Missing, "odd UTF16 suffix");
   pragma Assert (R.Parse (Short32_Suffix, (1, Short32_Suffix'Length)).Form = J.Missing, "truncated UTF32 suffix");
   pragma Assert (R.Parse (Invalid32_String, (1, Invalid32_String'Length)).Form = J.Missing, "UTF32 ceiling");
   pragma Assert (R.Parse (Bad_UTF8_String, (1, Bad_UTF8_String'Length)).Form = J.Missing, "overlong UTF8");
   pragma Assert (R.Parse (Short_UTF8_String, (1, Short_UTF8_String'Length)).Form = J.Missing, "truncated UTF8");
   pragma Assert (R.Parse (Raw_Control, (1, Raw_Control'Length)).Form = J.Missing, "raw control inside string");
   pragma Assert (R.Parse (Short16_String, (1, Short16_String'Length)).Form = J.Missing, "lone surrogate without closing quote");
   pragma Assert (R.Parse (Bad_Escape, (1, Bad_Escape'Length)).Form = J.Missing, "nonhex escape");
   pragma Assert (R.Parse (Missing_Colon, (1, Missing_Colon'Length)).Form = J.Missing, "missing object colon");
   pragma Assert (R.Parse (Trailing_Comma, (1, Trailing_Comma'Length)).Form = J.Missing, "trailing comma");
   pragma Assert (R.Parse (Short_Exponent, (1, Short_Exponent'Length)).Form = J.Missing, "missing exponent digit");
   pragma Assert (R.Parse (Empty, (Q.Byte_Count'Last, 0)).Form = J.Missing, "empty decode is not JSON");
   pragma Assert (R.Parse (BOM_Only8, (1, BOM_Only8'Length)).Form = J.Missing, "UTF8 BOM only");
   pragma Assert (R.Parse (BOM_Only16, (1, BOM_Only16'Length)).Form = J.Missing, "UTF16 BOM only");
   pragma Assert (R.Parse (BOM_Only32, (1, BOM_Only32'Length)).Form = J.Missing, "UTF32 BOM only");
   pragma Assert (R.Parse (Double_BOM, (1, Double_BOM'Length)).Form = J.Missing, "second BOM is content");
   pragma Assert (R.Parse (Three_Byte_NUL, (1, Three_Byte_NUL'Length)).Form = J.Missing, "three-byte heuristic not invented");
   pragma Assert (R.Parse (UTF8_Array, (2, 2)).Form = J.Missing, "invalid source extent");
   pragma Assert (R.Parse (Empty, (1, Q.Byte_Count'Last)).Form = J.Missing, "invalid huge span");

   declare N : constant J.Node := R.Parse (Shifted, (8, 4)); begin
      pragma Assert (N.Form = J.Array_Value and then N.First = 0 and then N.After = 4, "shifted arena and inner span");
   end;
   declare N : constant J.Node := R.Parse (Last_Byte, (Last_Byte'First, Last_Byte'Length)); begin
      pragma Assert (N.Form = J.Integer_Value and then N.First = 0 and then N.After = Last_Byte'Length, "finite byte array at endpoint");
   end;
   declare N : constant J.Node := R.Parse (Last_Array, (Last_Array'First, Last_Array'Length)); begin
      pragma Assert (N.Form = J.Array_Value and then N.First = 0 and then N.After = Last_Array'Length, "finite UTF16 array at endpoint");
   end;
   declare
      Context : constant C.Cursor := ((1, Unaligned'Length), C.UTF16_LE, 0);
      N : constant J.Node := R.Grammar.Parse (Unaligned, Context, 1);
   begin
      pragma Assert (N.Form = J.Integer_Value and then N.First = 1 and then N.After = Unaligned'Length, "generic source start has no alignment rule");
      pragma Assert (R.Grammar.Parse (Unaligned, Context, Q.Byte_Count'Last).Form = J.Missing, "generic invalid starting offset");
   end;
end Wide_Parser_Controls;
