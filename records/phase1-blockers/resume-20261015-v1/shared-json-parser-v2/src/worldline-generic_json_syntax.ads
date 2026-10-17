with Worldline.JSON_Syntax_Types; use Worldline.JSON_Syntax_Types;
use type Worldline.JSON_Syntax_Types.Count;

generic
   type Source_Data (<>) is private;
   type Source_Context is private;
   with function Source_Length_Impl
     (Data : Source_Data; Context : Source_Context) return Count;
   with function Read_Unit_Impl
     (Data : Source_Data; Context : Source_Context; Position : Count)
      return Reader_Unit;
package Worldline.Generic_JSON_Syntax with SPARK_Mode is
   use Worldline.JSON_Syntax_Types;
   use type Worldline.JSON_Syntax_Types.Count;
   -- Every actual instance must establish the callback requirements through
   -- these ordinary analyzed wrappers; the formal callbacks are not axioms.
   function Source_Length
     (Data : Source_Data; Context : Source_Context) return Count
   with Global => null;
   function Read_Unit
     (Data : Source_Data; Context : Source_Context; Position : Count)
      return Reader_Unit
   with Global => null,
     Post =>
       (if Read_Unit'Result.Kind in ASCII_Unit | Non_ASCII_Unit then
           Read_Unit'Result.Next_Offset > Position and then
           Read_Unit'Result.Next_Offset <= Source_Length (Data, Context)
        else Read_Unit'Result.Next_Offset = Position) and then
       (if Read_Unit'Result.Kind = End_Of_Source then
           Position = Source_Length (Data, Context));
   procedure Space
     (Data : Source_Data; Context : Source_Context; Position : in out Count)
   with Global => null,
     Post => Position >= Position'Old and then
       (if Position'Old <= Source_Length (Data, Context) then
           Position <= Source_Length (Data, Context)
        else Position = Position'Old);

   procedure Scan_String
     (Data : Source_Data; Context : Source_Context;
      Position : in out Count; Valid : out Boolean)
   with Global => null,
     Post => Position >= Position'Old and then
       (if Position'Old <= Source_Length (Data, Context) then
           Position <= Source_Length (Data, Context)
        else Position = Position'Old) and then
       (if Valid then Position > Position'Old);

   procedure Scan
     (Data : Source_Data; Context : Source_Context;
      Position : in out Count; Item : out Node)
   with Global => null, Always_Terminates,
     Subprogram_Variant =>
       (Decreases => Source_Length (Data, Context) -
          Count'Min (Position, Source_Length (Data, Context))),
     Post => Position >= Position'Old and then
       (if Position'Old <= Source_Length (Data, Context) then
           Position <= Source_Length (Data, Context)
        else Position = Position'Old) and then
       Within (Item, Source_Length (Data, Context)) and then
       (if Item.Form /= Missing then
           Position > Position'Old and then Item.First >= Position'Old and then
           Item.After = Position);

   function Parse
     (Data : Source_Data; Context : Source_Context; Start : Count := 0)
      return Node
   with Global => null,
     Post => Within (Parse'Result, Source_Length (Data, Context));
   -- Starts at the caller-supplied source offset and requires complete
   -- consumption through EOF. String adapter passes zero; wide adapter
   -- passes its detected BOM end. There is no start-alignment precondition.
end Worldline.Generic_JSON_Syntax;
