with Evaluation_Pending;

-- Original json.loads(bytes) decoding and protected_startup.exact_json's
-- noncanonical admission over the ONE Producer_Values whole JSON grammar.
-- No source acquisition, digest authentication or authorization follows.
package Worldline.Raw_JSON with SPARK_Mode is
   package P renames Evaluation_Pending;
   type Decoded_JSON (Length : Natural) is record
      Valid : Boolean;
      Data : String (1 .. Length);
   end record;
   function Decode_JSON (Data : P.Bytes; Item : P.Span) return Decoded_JSON
     with Global => null;
   function Original_Exact_JSON (Data : P.Bytes; Item : P.Span) return Boolean
     with Global => null;
   function Raw_JSON_Operation_Matches
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span)
      return Boolean with Global => null;
   -- Ordinary json.loads/json.dumps projection (last duplicate wins and
   -- nonfinite constants accepted). Textual NaN loses sign/payload/object
   -- identity: this MUST NOT replace original opaque-value/source equality.
   -- Authority-bearing joins must independently retain whole IEEE archives.
   function Ordinary_JSON_Operation_Matches
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span)
      return Boolean with Global => null;
   function Ordinary_JSON_Scoped_Matches
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span)
      return Boolean with Global => null;
   -- The caller supplies the existing archive codec, never inferred from a
   -- dictionary's user-controlled "type" field. Primitive types remain exact.
   function JSON_Source_Value_Matches
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span;
      Canonical, Scoped : Boolean) return Boolean with Global => null;
   function Ordinary_JSON_Finalization_Matches
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span)
      return Boolean with Global => null;
   function Raw_JSON_Scoped_Matches
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span)
      return Boolean with Global => null;
   -- Original Python ==, not archive roundtrip equality: bool/int/float
   -- compare numerically, signed floating zero compares equal, and dict
   -- insertion order does not affect equality. Exact-json admission remains.
   function Raw_JSON_Operation_Equal
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span)
      return Boolean with Global => null;
   function Raw_JSON_Scoped_Equal
     (JSON_Data, Archive_Data : P.Bytes; JSON_Value, Encoded : P.Span)
      return Boolean with Global => null;
   -- Same whole AST, original numeric/string/container value equality over
   -- JSON metadata. NaN is unequal. No opaque tuple/bytes/object-identity
   -- reconstruction is possible from JSON; authentic archives remain separate.
   function Python_JSON_Equal (Left, Right : String) return Boolean
     with Global => null;
   -- protected_owner.exact: ensure_ascii=True, sorted decoded keys, exact
   -- JSON separators, allow_nan=False, zero or one trailing LF.
   -- Text is UTF8-surrogatepass from native decoded string fields. Invalid
   -- encoding yields an empty (non-JSON) result, never a substitute string.
   function Canonical_ASCII_Quote (Text : String) return String
     with Global => null;
   -- The canonical predicate reuses the AST and native binary64 renderer.
   function Canonical_ASCII_Valid (Data : String) return Boolean
     with Global => null;
end Worldline.Raw_JSON;
