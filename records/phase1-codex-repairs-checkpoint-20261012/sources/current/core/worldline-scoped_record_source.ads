with Worldline.Archive_Envelope;
package Worldline.Scoped_Record_Source with SPARK_Mode is
   package E renames Worldline.Archive_Envelope;
   use type E.Count;
   -- Explicit carrier codec only: raw AO(S.record(source)), or
   -- AO(S.record(S.record(source))). This is source equality, not authority.
   function Scoped_Record_Value_Matches
     (Data : E.Bytes; Encoded, Typed : E.Span;
      Carrier_Scoped, Typed_Scoped : Boolean := False) return Boolean
     with Global => null;
   -- Original source_restore union: legacy S.record or its explicitly declared
   -- complete SourceImage. Bytes-key grammar stays inside the raw image, never
   -- in the unchanged public S.record grammar.
   function Source_Record_Value_Matches
     (Data : E.Bytes; Encoded, Typed : E.Span;
      Carrier_Scoped, Typed_Scoped : Boolean := False) return Boolean
     with Global => null;
end Worldline.Scoped_Record_Source;
