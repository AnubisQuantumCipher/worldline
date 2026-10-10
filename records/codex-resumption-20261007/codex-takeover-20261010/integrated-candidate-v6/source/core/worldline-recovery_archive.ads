with Worldline.Archive_Envelope;
package Worldline.Recovery_Archive with SPARK_Mode is
   package E renames Worldline.Archive_Envelope;
   function Record_Is
     (Data : E.Bytes; Encoded : E.Span; Module_Name, Record_Name : String)
      return Boolean with Global => null;
   use type E.Count;
   function Valid (Data : E.Bytes; Encoded : E.Span) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Encoded.Length);
   function Field (Data : E.Bytes; Encoded : E.Span; Name : String) return E.Span
     with Global => null;
   function Same_Encoding (Data : E.Bytes; Left, Right : E.Span) return Boolean
     with Global => null;
   -- Original Python typed equality, used only where the original relation used
   -- ==. It is deliberately distinct from explicit archive roundtrip equality.
   function Equal
     (L_Data, R_Data : E.Bytes; Left, Right : E.Span) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Left.Length);
   -- The same equality engine over the original operation_capture grammar.
   -- This does not broaden Recovery's immutable DTO constructor whitelist.
   function Equal_Operation
     (L_Data, R_Data : E.Bytes; Left, Right : E.Span) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Left.Length);
   --  Original finalization_journal.record_bytes, not the four-item archive DTO.
   --  Field returns an unchanged span at Finalization_Record, or an empty span.
   function Valid_Finalization_Record (Data : E.Bytes; Encoded : E.Span) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Encoded.Length);
   function Finalization_Record_Field
     (Data : E.Bytes; Encoded : E.Span; Name : String) return E.Span
     with Global => null;
   function Equal_Finalization_Record
     (L_Data, R_Data : E.Bytes; Left, Right : E.Span;
      Right_Layer : E.Layer := E.Recovery) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Left.Length);
   -- Closed selected root raw DTO transport, or unchanged scoped transport.
   -- Syntax/constructor validity is not a native lifecycle authorization.
   function Source_Valid
     (Data : E.Bytes; Encoded : E.Span; Scoped : Boolean := False) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Encoded.Length);
   -- Exact source-preimage relation, distinct from Python numeric equality.
   function Source_Value_Matches
     (L_Data, R_Data : E.Bytes; Left, Right : E.Span;
      Left_Scoped, Right_Scoped : Boolean := False) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Left.Length);
   -- Exact source archive equality preserves dictionary insertion order;
   -- legacy Python == consumers continue to use the unchanged profile above.
   function Ordered_Source_Value_Matches
     (L_Data, R_Data : E.Bytes; Left, Right : E.Span;
      Left_Scoped, Right_Scoped : Boolean := False) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Left.Length);
   -- One/two original S.record layers at an explicit compiled source position.
   -- S.restore accepts metadata/constructor-field permutations and padded or
   -- negative-zero integer magnitudes; restored dict insertion order survives.
   -- The typed right tree and every constructor/field remain fully validated.
   subtype Record_Restore_Depth is Positive range 1 .. 2;
   function Restored_Source_Value_Matches
     (L_Data, R_Data : E.Bytes; Left, Right : E.Span;
      Left_Record_Depth : Record_Restore_Depth;
      Right_Scoped : Boolean := False) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Left.Length);
   function Text_Is (Data : E.Bytes; Encoded : E.Span; Text : String) return Boolean
     with Global => null;
   function Boolean_Is (Data : E.Bytes; Encoded : E.Span; Value : Boolean) return Boolean
     with Global => null;
   function Stored_Bytes_Valid (Data : E.Bytes; Encoded : E.Span) return Boolean
     with Global => null;
   function Stored_Bytes (Data : E.Bytes; Encoded : E.Span) return E.Bytes
     with Global => null, Pre => Stored_Bytes_Valid (Data, Encoded);
   function Integer_Valid (Data : E.Bytes; Encoded : E.Span) return Boolean
     with Global => null;
   function Integer_Negative (Data : E.Bytes; Encoded : E.Span) return Boolean
     with Global => null;
   function Integer_Magnitude (Data : E.Bytes; Encoded : E.Span) return E.Bytes
     with Global => null, Pre => Integer_Valid (Data, Encoded);
end Worldline.Recovery_Archive;
