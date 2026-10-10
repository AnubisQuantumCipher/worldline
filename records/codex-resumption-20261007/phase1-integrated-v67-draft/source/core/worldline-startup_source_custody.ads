with Worldline.Custody_V2_Load_Input;
package Worldline.Startup_Source_Custody with SPARK_Mode is
   package L renames Worldline.Custody_V2_Load_Input;
   function Corresponds
     (Data : L.E.Bytes; Source, Installation : L.E.Span) return Boolean
     with Global => null;
   function File_Corresponds
     (Data : L.E.Bytes; Source, Path, Raw_Bytes : L.E.Span) return Boolean
     with Global => null;
   -- Original complete envelope has neither a FILE nor ABSENT selection for
   -- this path. This is a factual relation, not artifact creation permission.
   function Unselected_Path
     (Data : L.E.Bytes; Source, Path : L.E.Span) return Boolean
     with Global => null;
end Worldline.Startup_Source_Custody;
