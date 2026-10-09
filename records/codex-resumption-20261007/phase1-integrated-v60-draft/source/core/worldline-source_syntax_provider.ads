package Worldline.Source_Syntax_Provider with SPARK_Mode is
   type Parsed_Syntax (Length : Natural) is record
      Valid : Boolean := False;
      AST : String (1 .. Length);
   end record;
   -- Original_Result is the independently retained, pre-enrichment JSON UTF8.
   -- Declaration is independently selected; capsule is actual protected output.
   function Project (Original_Result, Parser_Declaration, Raw_Capsule : String)
      return Parsed_Syntax with Global => null;
   function Authentic
     (Original_Result, Parser_Declaration, Raw_Capsule, Native_AST : String)
      return Boolean with Global => null;
   -- The adjunct root carries the exact original text, not its reserialization.
   -- Only the four named syntax adjunct fields may differ from that original.
   function Original_Joined (Result_Record : String) return Boolean
      with Global => null;
   function Authentic (Result_Record : String) return Boolean with Global => null;
end Worldline.Source_Syntax_Provider;
