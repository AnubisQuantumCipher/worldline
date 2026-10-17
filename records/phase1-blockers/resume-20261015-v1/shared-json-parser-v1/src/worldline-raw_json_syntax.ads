with Resource_Quantities;
with Worldline.JSON_Source_Cursor;
with Worldline.JSON_Syntax_Types;
with Worldline.Generic_JSON_Syntax;

-- UNAPPLIED wide syntax adapter. This does not implement the wide selectors,
-- decoded text/numeric values, canonical rendering or Raw_JSON relations.
package Worldline.Raw_JSON_Syntax with SPARK_Mode is
   package Q renames Resource_Quantities;
   package C renames Worldline.JSON_Source_Cursor;
   package JS renames Worldline.JSON_Syntax_Types;
   use type JS.Count;
   use type JS.Unit_Kind;
   use type JS.Value_Kind;

   function Source_Length (Data : Q.Byte_Array; Context : C.Cursor) return JS.Count
   with Global => null,
     Post => Source_Length'Result = Context.Item.Length;

   function Read_Unit
     (Data : Q.Byte_Array; Context : C.Cursor; Position : JS.Count)
      return JS.Reader_Unit
   with Global => null,
     Post =>
       (if Read_Unit'Result.Kind in JS.ASCII_Unit | JS.Non_ASCII_Unit then
           Read_Unit'Result.Next_Offset > Position and then
           Read_Unit'Result.Next_Offset <= Source_Length (Data, Context)
        else Read_Unit'Result.Next_Offset = Position) and then
       (if Read_Unit'Result.Kind = JS.End_Of_Source then
           Position = Source_Length (Data, Context));

   package Grammar is new Worldline.Generic_JSON_Syntax
     (Source_Data => Q.Byte_Array, Source_Context => C.Cursor,
      Source_Length => Source_Length, Read_Unit => Read_Unit);

   function Parse (Data : Q.Byte_Array; Item : C.Span) return JS.Node
   with Global => null,
     Post => JS.Within (Parse'Result, Item.Length);
   -- Initial detection supplies the start; all successful node coordinates
   -- remain relative to the original full Item, including its BOM prefix.
end Worldline.Raw_JSON_Syntax;
