with Resource_Quantities;
generic
   type Item_Type is private;
   with function Load (Data : Resource_Quantities.Byte_Array) return Item_Type;
   with function Padding_Valid
     (Data : Resource_Quantities.Byte_Array; Raw : Item_Type) return Boolean;
   Value_Width : Resource_Quantities.Byte_Count;
procedure Raw_Decode_Case;
