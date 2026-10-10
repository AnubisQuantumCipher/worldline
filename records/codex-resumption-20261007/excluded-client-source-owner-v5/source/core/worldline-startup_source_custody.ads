with Worldline.Custody_V2_Load_Input;
package Worldline.Startup_Source_Custody with SPARK_Mode is
   package L renames Worldline.Custody_V2_Load_Input;
   function Corresponds
     (Data : L.E.Bytes; Source, Installation : L.E.Span) return Boolean
     with Global => null;
   -- Fresh clean-exec helper bootstrap may precede its ENTRY compilation.
   -- This factual closure check never grants target execution by itself.
   function Bootstrap_Corresponds
     (Data : L.E.Bytes; Source, Installation : L.E.Span) return Boolean
     with Global => null;
   -- Every projected record is byte/mode identical to the private owner
   -- envelope and exactly selected by Closure. DATA is restricted to the
   -- unchanged original request selection and its complete requests.
   function Projection_Corresponds
     (Data : L.E.Bytes; Owner_Source, Actor_Source, Closure, Request,
      Request_Path, Entry : L.E.Span) return Boolean with Global => null;
   function File_Corresponds
     (Data : L.E.Bytes; Source, Path, Raw_Bytes : L.E.Span) return Boolean
     with Global => null;
   function Image_Corresponds
     (Data : L.E.Bytes; Source, Path, Raw_Bytes : L.E.Span) return Boolean
     with Global => null;
   function Role_Selected
     (Data : L.E.Bytes; Source, Path : L.E.Span; Role : String) return Boolean
     with Global => null;
   -- Fresh original named/held/readback captures for every private owner
   -- FILE and the envelope itself. Actor observations are never substituted.
   function Readbacks_Correspond
     (Data : L.E.Bytes; Source : L.E.Span) return Boolean with Global => null;
   -- The actual selected FILE readback, not a second documentary named inode.
   function File_Identity_Corresponds
     (Data : L.E.Bytes; Source, Path, Identity : L.E.Span) return Boolean
     with Global => null,
       Depends => (File_Identity_Corresponds'Result => (Data, Source, Path, Identity));
   -- Original complete envelope has neither a FILE nor ABSENT selection for
   -- this path. This is a factual relation, not artifact creation permission.
   function Unselected_Path
     (Data : L.E.Bytes; Source, Path : L.E.Span) return Boolean
     with Global => null;
end Worldline.Startup_Source_Custody;
