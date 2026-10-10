with Worldline.Archive_Envelope;
package Worldline.Recovery_Syntax with SPARK_Mode is
   package E renames Worldline.Archive_Envelope;
   -- Private transport only: original signed packet/result bytes are unchanged.
   -- Each Operation-list item has exactly result/declaration/capsule byte fields.
   type Capsule_Operands is record
      Present : Boolean := False;
      Declaration, Capture : E.Span := (1, 0);
   end record;
   function Valid (Facts_Data : E.Bytes; Capsules : E.Span) return Boolean
     with Global => null;
   function Find
     (Original_Result : String; Facts_Data : E.Bytes; Capsules : E.Span)
      return Capsule_Operands with Global => null;
   function Operand_Text (Facts_Data : E.Bytes; Operand : E.Span) return String
     with Global => null;
   -- Present is a complete original-result transport join, NEVER parser/source
   -- admission. Evaluation_Producer.Derive's explicit native source policy
   -- independently authenticates both complete operands and redecides closure.
end Worldline.Recovery_Syntax;
