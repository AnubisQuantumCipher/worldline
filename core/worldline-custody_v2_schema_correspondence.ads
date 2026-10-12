with Worldline.Custody_V2_Values;
package Worldline.Custody_V2_Schema_Correspondence with SPARK_Mode is
   package V renames Worldline.Custody_V2_Values;
   package E renames V.E;
   type Table_Name is (Genesis, Events, Alternatives, Root_State, Subject_State, Blobs, Head);
   function Name (Table : Table_Name) return String with Global => null;
   function DDL (Table : Table_Name) return String with Global => null;
   function Width (Table : Table_Name) return Positive with Global => null;
   function Table_Matches (Data : E.Bytes; Item : E.Span; Table : Table_Name)
      return Boolean with Global => null;
   function Database_Matches (Data : E.Bytes; Item : E.Span) return Boolean
      with Global => null;
end Worldline.Custody_V2_Schema_Correspondence;
