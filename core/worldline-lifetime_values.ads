with Interfaces;
package Worldline.Lifetime_Values with SPARK_Mode is
   subtype U64 is Interfaces.Unsigned_64;
   type Value_Kind is (Invalid, Null_Value, False_Value, True_Value,
      Integer_Value, Text_Value, Bytes_Value, Tuple_Value, Unavailable_Value);
   type Node is record
      Kind : Value_Kind := Invalid;
      First, Last, Count : Natural := 0;
   end record;
   No_Node : constant Node := (Invalid, 0, 0, 0);
   function Parse (Data : String; First, Last : Natural) return Node with Global => null;
   function Element (Data : String; Parent : Node; Index : Positive) return Node with Global => null,
     Post => (if Element'Result.Kind = Invalid then Element'Result = No_Node
              else Element'Result.First > Parent.First and then Element'Result.Last <= Parent.Last
                and then Element'Result.Last >= Element'Result.First);
   function Text (Data : String; Item : Node) return String with Global => null;
   function Bytes (Data : String; Item : Node) return String with Global => null;
   function Equal (Data : String; L, R : Node) return Boolean with Global => null,
     Subprogram_Variant => (Decreases => (if L.Kind = Tuple_Value then 1 else 0), Increases => L.First);
   function Compare (Data : String; L, R : Node) return Integer with Global => null;
   function Matches (Data : String; Item : Node; Value : U64) return Boolean with Global => null;
   function Nonnegative (Data : String; Item : Node) return Boolean with Global => null;
   function Positive_Integer (Data : String; Item : Node) return Boolean with Global => null;
   function Mod_256 (Data : String; Item : Node) return Natural with Global => null;
   function Word (Data : String; First : Natural; Width : Positive) return U64 with Global => null,
     Pre => Width <= 8 and then First > 0 and then First <= Data'Length and then Width - 1 <= Data'Length - First;
   function Complete (Data : String; Item : Node) return Boolean with Global => null,
     Subprogram_Variant => (Decreases => (if Item.Kind = Tuple_Value then 1 else 0), Increases => Item.First);
end Worldline.Lifetime_Values;
