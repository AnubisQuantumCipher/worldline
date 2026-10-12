--  Original JSON values, including unbounded integer and finite-float tokens.
--  This parser supplies syntax and selectors, never acquisition authority.
package Worldline.Producer_Values with SPARK_Mode is
   type Value_Kind is (Missing, Null_Value, Boolean_Value, Integer_Value,
                      Number_Value, String_Value, Array_Value, Object_Value);
   type Node is record
      Form : Value_Kind := Missing;
      First, Last : Natural := 0;
   end record;
   No_Node : constant Node := (Missing, 0, 0);
   function Parse (Data : String) return Node with Global => null;
   function Member_Key (Data : String; Parent : Node; Index : Positive)
      return Node with Global => null;
   -- The same whole grammar has distinct admission predicates. Ordinary
   -- Parse/Field/Count retain json.loads last-key-wins semantics.
   function Standard_JSON (Data : String) return Boolean with Global => null;
   function Duplicate_Free (Data : String) return Boolean with Global => null;
   function Original_Exact_JSON (Data : String) return Boolean is
     (Standard_JSON (Data) and then Duplicate_Free (Data)) with Global => null;
   -- Canonical surrogatepass UTF8 unit width; no Unicode normalization.
   function UTF8_Width (Data : String; Offset : Natural) return Natural
     with Global => null,
       Post => UTF8_Width'Result <= 4 and then
         (if UTF8_Width'Result > 0 then
            Offset < Data'Length and then UTF8_Width'Result <= Data'Length - Offset);
   -- Original str(json.loads numeric value), including signed zero,
   -- nearest-even binary64 and Python nan/inf spellings.
   function Number_Image (Data : String; Item : Node) return String
     with Global => null;
   function Field (Data : String; Parent : Node; Name : String) return Node
     with Global => null,
       Post => (if Field'Result.Form /= Missing then Parent.First > 0 and then
                  Field'Result.First > Parent.First and then Field'Result.First <= Data'Length);
   function Element (Data : String; Parent : Node; Index : Positive) return Node
     with Global => null,
       Post => (if Element'Result.Form /= Missing then Parent.First > 0 and then
                  Element'Result.First > Parent.First and then Element'Result.First <= Data'Length);
   function Count (Data : String; Parent : Node) return Natural
     with Global => null,
       Post => (if Count'Result > 0 then Parent.First in 1 .. Data'Length);
   function Text (Data : String; Item : Node) return String with Global => null;
   function Is_Text (Data : String; Item : Node; Expected : String) return Boolean
     with Global => null;
   function Is_True (Data : String; Item : Node) return Boolean with Global => null;
   function Is_False (Data : String; Item : Node) return Boolean with Global => null;
   function Is_Null (Item : Node) return Boolean is (Item.Form = Null_Value)
     with Global => null;
   function Present (Item : Node) return Boolean is (Item.Form /= Missing)
     with Global => null;
   function Nonempty_Text (Data : String; Item : Node) return Boolean
     with Global => null;
   function Equal (Left : String; L : Node; Right : String; R : Node) return Boolean
     with Global => null,
       Subprogram_Variant => (Decreases =>
         (if L.Form = Missing then 0
          else Long_Long_Integer (Left'Length) + 1 - Long_Long_Integer (Natural'Min (L.First, Left'Length))));
   function Truth (Data : String; Item : Node) return Boolean with Global => null;
   function Decimal (Data : String; Item : Node) return String with Global => null;
   function Nonnegative (Data : String; Item : Node) return Boolean
     with Global => null;
   function Slice (Data : String; Item : Node) return String
     with Global => null,
       Post => Slice'Result'Length <= Data'Length and then
         (if Item.Form /= Missing and then Item.First > 0 and then
             Item.First <= Item.Last and then Item.Last <= Data'Length
          then Slice'Result'Length = Item.Last - Item.First + 1
          else Slice'Result'Length = 0);
   function Member_Name (Data : String; Parent : Node; Index : Positive)
      return String with Global => null;
   function Field (Data, Name : String) return String with Global => null;
   function Element (Data : String; Index : Natural) return String with Global => null;
   function Text (Data : String) return String with Global => null;
   function Kind (Data : String) return Value_Kind with Global => null;
   function Count (Data : String) return Natural with Global => null;
   function Truth (Data : String) return Boolean with Global => null;
   function Equal (Left, Right : String) return Boolean with Global => null;
   function Quote (Text : String) return String with Global => null;
   function Python_String (Value : String) return String with Global => null;
end Worldline.Producer_Values;
