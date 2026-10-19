with Worldline.Archive_Envelope;

--  Actual operation_capture grammar over original nested archive bytes.
--  A syntactic/typed archive result does not assert authentic source custody,
--  JSON number correspondence, HMAC integrity, semantic evidence or X5 fold.
package Worldline.Operation_Archive with SPARK_Mode is
   package E renames Worldline.Archive_Envelope;
   use type E.Count;
   --  Share the original explicit record field roster across the two archive
   --  grammars; this validates constructors, never evaluation authority.
   function Record_Fields (Data : E.Bytes; Item : E.View) return Boolean
     with Global => null;
   function Valid (Data : E.Bytes; Encoded : E.Span) return Boolean
     with Global => null,
       Subprogram_Variant => (Decreases => Encoded.Length);
   function Field (Data : E.Bytes; Encoded : E.Span; Name : String)
      return E.Span
     with Global => null,
       Post => Field'Result.Length <= Encoded.Length;
   --  Original restore_archive's exact roundtrip equality. Object insertion
   --  order and float bits are preserved, not Python's numeric/coercing ==.
   function Same_Encoding (Data : E.Bytes; Left, Right : E.Span) return Boolean
     with Global => null;
end Worldline.Operation_Archive;
