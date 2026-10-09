with Worldline.Operation_Archive;
package Worldline.Scoped_Archive with SPARK_Mode is
   package A renames Worldline.Operation_Archive;
   package E renames A.E;
   use type E.Count;
   -- Original root_worker_codec's scoped record layer and roundtrip order.
   -- This validates bytes/types only, never native decision/status semantics.
   function Valid (Data : E.Bytes; Encoded : E.Span) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Encoded.Length);
   -- Exact dictionary member's SCOPED encoded subtree, not decoded permission.
   function Field (Data : E.Bytes; Encoded : E.Span; Name : String) return E.Span
     with Global => null;
   function Text_Is (Data : E.Bytes; Encoded : E.Span; Text : String) return Boolean
     with Global => null;
   function Text_Matches (Data : E.Bytes; Encoded, Expected : E.Span) return Boolean
     with Global => null;
   function Member_Count (Data : E.Bytes; Encoded : E.Span) return E.Count
     with Global => null;
   function Member_Name_Is
     (Data : E.Bytes; Encoded : E.Span; Ordinal : E.Count; Name : String)
      return Boolean with Global => null;
end Worldline.Scoped_Archive;
