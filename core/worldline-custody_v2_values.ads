with Worldline.Scoped_Archive;
package Worldline.Custody_V2_Values with SPARK_Mode is
   package S renames Worldline.Scoped_Archive;
   package E renames S.E;
   package Q renames E.Q;
   use type E.Count;
   use type E.Value_Kind;
   function Type_Is (Data : E.Bytes; Item : E.Span; Name : String)
      return Boolean with Global => null;
   function Valid_Text_Field (Data : E.Bytes; Item : E.Span; Field : String)
      return Boolean is
     (S.Valid (Data, Item) and then
      E.Decode (Data, S.A.Field (Data, Item, Field), E.Operation).Form = E.Text_Value and then
      E.Bytes_Valid (Data, E.Decode
        (Data, S.A.Field (Data, Item, Field), E.Operation).Payload)) with Global => null;
   function Hex_Text (Data : E.Bytes; Item : E.Span; Field : String)
      return E.Bytes is
     (E.Materialize (Data, E.Decode
        (Data, S.A.Field (Data, Item, Field), E.Operation).Payload))
      with Global => null, Pre => Valid_Text_Field (Data, Item, Field);
   function Hex_Domain (Raw : E.Bytes) return Boolean is
     (Raw'Length mod 2 = 0 and then
      (for all B of Raw => B in Character'Pos ('0') .. Character'Pos ('9') |
                             Character'Pos ('a') .. Character'Pos ('f')))
      with Global => null;
   function Valid_Hex_Field (Data : E.Bytes; Item : E.Span; Field : String)
      return Boolean is
     (Valid_Text_Field (Data, Item, Field) and then
      Hex_Domain (Hex_Text (Data, Item, Field))) with Global => null;
   function Valid_Text (Data : E.Bytes; Item : E.Span) return Boolean is
     (Type_Is (Data, Item, "str") and then Valid_Text_Field (Data, Item, "value"))
      with Global => null;
   function Valid_Bytes (Data : E.Bytes; Item : E.Span) return Boolean is
     (Type_Is (Data, Item, "bytes") and then Valid_Hex_Field (Data, Item, "value"))
      with Global => null;
   function Is_Integer (Data : E.Bytes; Item : E.Span) return Boolean is
     (Type_Is (Data, Item, "integer") and then Valid_Hex_Field (Data, Item, "magnitude"))
      with Global => null;
   function Is_Null (Data : E.Bytes; Item : E.Span) return Boolean is
     (Type_Is (Data, Item, "NoneType")) with Global => null;
   function Is_Sequence (Data : E.Bytes; Item : E.Span) return Boolean is
     (Type_Is (Data, Item, "list") or else Type_Is (Data, Item, "tuple"))
      with Global => null;
   function Text_Value (Data : E.Bytes; Item : E.Span) return E.Bytes
      with Global => null, Pre => Valid_Text (Data, Item),
        Post => Text_Value'Result'Length <= Item.Length;
   function Hex_Value (Data : E.Bytes; Item : E.Span; Field : String)
      return E.Bytes with Global => null,
        Pre => Valid_Hex_Field (Data, Item, Field),
        Post => Hex_Value'Result'Length <= Item.Length;
   function Bytes_Value (Data : E.Bytes; Item : E.Span) return E.Bytes is
     (Hex_Value (Data, Item, "value"))
      with Global => null, Pre => Valid_Bytes (Data, Item);
   function Magnitude_Value (Data : E.Bytes; Item : E.Span) return E.Bytes is
     (Hex_Value (Data, Item, "magnitude"))
      with Global => null, Pre => Is_Integer (Data, Item);
   function Negative (Data : E.Bytes; Item : E.Span) return Boolean is
     (E.Decode (Data, S.A.Field (Data, Item, "negative"), E.Operation).Boolean_Bit)
      with Global => null, Pre => Is_Integer (Data, Item);
   function Count (Data : E.Bytes; Item : E.Span) return E.Count
      with Global => null, Post => Count'Result <= Item.Length;
   function Element (Data : E.Bytes; Item : E.Span; Ordinal : E.Count)
      return E.Span with Global => null,
        Post => Element'Result.Length = 0 or else
          Element'Result.Length < Item.Length;
   function Record_Field (Data : E.Bytes; Item : E.Span; Name : String)
      return E.Span with Global => null;
   type Count_Result (Present : Boolean := False) is record
      case Present is
         when True => Value : E.Count;
         when False => null;
      end case;
   end record;
   function Nonnegative_Count (Data : E.Bytes; Item : E.Span)
      return Count_Result with Global => null;
end Worldline.Custody_V2_Values;
