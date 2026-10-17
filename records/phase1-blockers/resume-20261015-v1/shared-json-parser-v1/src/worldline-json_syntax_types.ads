with Resource_Quantities;

-- UNAPPLIED parser representation candidate. No value/text materialization.
package Worldline.JSON_Syntax_Types with SPARK_Mode is
   subtype Count is Resource_Quantities.Byte_Count;
   use type Count;
   type Value_Kind is (Missing, Null_Value, Boolean_Value, Integer_Value,
                      Number_Value, String_Value, Array_Value, Object_Value);
   type Node (Form : Value_Kind := Missing) is record
      case Form is
         when Missing => null;
         when others => First, After : Count := 0;
      end case;
   end record;
   No_Node : constant Node := (Form => Missing);
   function Within (Item : Node; Length : Count) return Boolean is
     (Item.Form = Missing or else
       (Item.First < Item.After and then Item.After <= Length))
   with Global => null;

   subtype ASCII_Character is Character range Character'Val (0) .. Character'Val (127);
   type Unit_Kind is (ASCII_Unit, Non_ASCII_Unit, End_Of_Source, Invalid_Unit);
   type Reader_Unit (Kind : Unit_Kind := Invalid_Unit) is record
      Next_Offset : Count := 0;
      case Kind is
         when ASCII_Unit => Value : ASCII_Character := Character'Val (0);
         when others => null;
      end case;
   end record;
   -- Non_ASCII_Unit certifies a valid source encoding unit, not its full
   -- codepoint value. Syntax only needs its non-ASCII classification. Text
   -- and numeric consumers must use their own exact source/value readers.
end Worldline.JSON_Syntax_Types;
