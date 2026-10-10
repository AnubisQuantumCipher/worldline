with Worldline.Custody_V2_Values;
package Worldline.Custody_V2_Root_Values with SPARK_Mode is
   package Original renames Worldline.Custody_V2_Values;
   package S renames Original.S;
   package E renames Original.E;
   package Q renames Original.Q;
   subtype Count_Result is Original.Count_Result;
   use type E.Count;
   -- Explicit ORIGINAL operation-image semantics only. A user dictionary with
   -- type/value keys remains a dictionary. Scoped metadata is handled by its
   -- separate compiled reader, never by inspecting an alleged encoding flag.
   function Valid (Data : E.Bytes; Item : E.Span) return Boolean with Global => null;
   function Type_Is (Data : E.Bytes; Item : E.Span; Name : String) return Boolean with Global => null;
   function Record_Field (Data : E.Bytes; Item : E.Span; Name : String) return E.Span with Global => null;
   --  Exact ORIGINAL BYTES-key lookup (e.g. untouched HELD manager properties).
   --  This never projects or rewrites a dictionary into a scoped text-key DTO.
   function Bytes_Key_Field (Data : E.Bytes; Item : E.Span; Name : String)
      return E.Span with Global => null;
   function Valid_Text (Data : E.Bytes; Item : E.Span) return Boolean with Global => null;
   function Valid_Bytes (Data : E.Bytes; Item : E.Span) return Boolean with Global => null;
   function Is_Integer (Data : E.Bytes; Item : E.Span) return Boolean with Global => null;
   function Is_Null (Data : E.Bytes; Item : E.Span) return Boolean with Global => null;
   function Is_Sequence (Data : E.Bytes; Item : E.Span) return Boolean with Global => null;
   function Text_Value (Data : E.Bytes; Item : E.Span) return E.Bytes
     with Global => null, Pre => Valid_Text (Data, Item);
   function Bytes_Value (Data : E.Bytes; Item : E.Span) return E.Bytes
     with Global => null, Pre => Valid_Bytes (Data, Item);
   function Magnitude_Value (Data : E.Bytes; Item : E.Span) return E.Bytes
     with Global => null, Pre => Is_Integer (Data, Item);
   function Negative (Data : E.Bytes; Item : E.Span) return Boolean
     with Global => null, Pre => Is_Integer (Data, Item);
   function Text_Is (Data : E.Bytes; Item : E.Span; Name : String) return Boolean with Global => null;
   function Text_Matches (Data : E.Bytes; Item, Expected : E.Span) return Boolean with Global => null;
   function Valid_Hex_Field (Data : E.Bytes; Item : E.Span; Field : String) return Boolean with Global => null;
   function Hex_Value (Data : E.Bytes; Item : E.Span; Field : String) return E.Bytes
     with Global => null, Pre => Valid_Hex_Field (Data, Item, Field);
   function Count (Data : E.Bytes; Item : E.Span) return E.Count
     with Global => null, Post => Count'Result <= Item.Length;
   function Element (Data : E.Bytes; Item : E.Span; Ordinal : E.Count) return E.Span with Global => null;
   function Nonnegative_Count (Data : E.Bytes; Item : E.Span) return Count_Result with Global => null;
end Worldline.Custody_V2_Root_Values;
