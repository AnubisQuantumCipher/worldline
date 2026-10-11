with Worldline.Archive_Envelope;

--  Explicit derived JSON transport of original archive values. This is not an
--  original JSON-file observation or source-custody assertion. Binary leaves
--  use the existing producer's exact base64 envelope; tuples become JSON arrays.
package Worldline.Transaction_Archive_JSON with SPARK_Mode is
   package E renames Worldline.Archive_Envelope;
   type Projection is (Whole_Value, Context_Body, Requirement_Body, Policy_Body,
                       Receipt_Body, Receipt_Id_Body, Root_Set, Root_Set_Member);
   function Render (Data : E.Bytes; Encoded : E.Span;
                    Layer : E.Layer := E.Operation;
                    Mode : Projection := Whole_Value) return String
     with Global => null;
end Worldline.Transaction_Archive_JSON;
