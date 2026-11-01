with Worldline.Producer_Values;
package Worldline.Producer_Render with SPARK_Mode is
   use type Worldline.Producer_Values.Value_Kind;
   --  Count the actual escaped byte extent, then construct the whole result.
   --  A genuinely unrepresentable extent raises Constraint_Error; it is never
   --  reported as an empty string or a successful empty container.
   function Quote_Size (Text : String) return Natural with Global => null,
     Post => Quote_Size'Result >= 2;
   --  Write directly into the final, exactly sized destination. A mismatched
   --  destination raises Program_Error, not a truncated or empty result.
   procedure Write_Quote (Text : String; Output : out String)
     with Global => null, Relaxed_Initialization => Output,
       Post => Output'Initialized and then Output'Length >= 2;
   --  The node overloads stream Text's decoded bytes, without materializing
   --  the decoded name/value merely to count or quote it. As with Quote(Text),
   --  any malformed decoded unit discards the whole prefix and yields "".
   function Quote_Size
     (Data : String; Item : Worldline.Producer_Values.Node) return Natural
     with Global => null,
       Pre => Item.Form = Worldline.Producer_Values.String_Value and then
         Item.First > 0 and then Item.First < Item.Last and then Item.Last <= Data'Length,
       Post => Quote_Size'Result >= 2;
   procedure Write_Quote
     (Data : String; Item : Worldline.Producer_Values.Node; Output : out String)
     with Global => null, Relaxed_Initialization => Output,
       Pre => Item.Form = Worldline.Producer_Values.String_Value and then
         Item.First > 0 and then Item.First < Item.Last and then Item.Last <= Data'Length,
       Post => Output'Initialized and then Output'Length >= 2;
   function Quote (Text : String) return String with Global => null,
     Post => Quote'Result'Length >= 2;
   --  Preserve Python str/repr, including first-key order and last-key values.
   --  No expansion-factor input limit is imposed on either operation.
   function Python_String (Value : String) return String with Global => null;
end Worldline.Producer_Render;
