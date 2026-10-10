with Worldline.Custody_V2_Archive_Projection;
-- Proof-only composition of the ACTUAL Render_Delta restricted JSON grammar.
-- This does not recognize or authorize arbitrary original JSON/event payloads.
package Worldline.Custody_V2_Delta_Grammar with SPARK_Mode is
   package A renames Worldline.Custody_V2_Archive_Projection;
   package E renames A.E;
   use type E.Count;
   type Bound_Result is record
      Valid : Boolean := False;
      JSON_Length : E.Count := 0;
   end record;
   -- The only numeric JSON leaves in native deltas are SQL class ordinals 0..4.
   -- Arbitrary original SQL integers/text/REAL/BLOB stay unbounded hex strings.
   -- All strings are unescaped ASCII: fixed compiled names/schema or hex.
   function Bound (Data : E.Bytes; Item : E.Span; Layer : E.Layer := E.Operation)
      return Bound_Result with Ghost, Global => null,
        Subprogram_Variant => (Decreases => Item.Length, Decreases => 2),
        Post => (if Bound'Result.Valid then Bound'Result.JSON_Length <= Item.Length);
end Worldline.Custody_V2_Delta_Grammar;
