package body Worldline.Custody_V2_Values with SPARK_Mode is
   use type Q.Byte;
   function Type_Is (Data : E.Bytes; Item : E.Span; Name : String)
      return Boolean is
     (S.Valid (Data, Item) and then E.Text_Is
       (Data, E.Decode (Data, S.A.Field (Data, Item, "type"), E.Operation), Name));

   function Text_Value (Data : E.Bytes; Item : E.Span) return E.Bytes is
      Value : constant E.View := E.Decode
        (Data, S.A.Field (Data, Item, "value"), E.Operation);
   begin
      return E.Materialize (Data, Value.Payload);
   end Text_Value;

   function Nibble (Value : Q.Byte) return Q.Byte is
     (if Value in Character'Pos ('0') .. Character'Pos ('9') then
         Value - Character'Pos ('0')
      else Value - Character'Pos ('a') + 10)
      with Pre => Value in Character'Pos ('0') .. Character'Pos ('9') |
                          Character'Pos ('a') .. Character'Pos ('f'),
           Post => Nibble'Result <= 15;

   function Hex_Value (Data : E.Bytes; Item : E.Span; Field : String)
      return E.Bytes
   is
      Value : constant E.View := E.Decode
        (Data, S.A.Field (Data, Item, Field), E.Operation);
      Raw : constant E.Bytes := E.Materialize (Data, Value.Payload);
   begin
      return Result : E.Bytes (1 .. Raw'Length / 2) do
         for I in Result'Range loop
            pragma Loop_Variant (Increases => I);
            Result (I) := Nibble (Raw (Raw'First + (I - 1) * 2)) * 16 +
              Nibble (Raw (Raw'First + (I - 1) * 2 + 1));
         end loop;
      end return;
   end Hex_Value;

   function Children (Data : E.Bytes; Item : E.Span) return E.Span is
      Value : constant E.View := E.Decode
        (Data, S.A.Field (Data, Item, "items"), E.Operation);
   begin
      if not Is_Sequence (Data, Item) or else Value.Form /= E.List_Value then
         return (1, 0);
      end if;
      return Value.Children;
   end Children;

   function Count (Data : E.Bytes; Item : E.Span) return E.Count is
     (if Is_Sequence (Data, Item) then E.Array_Length (Data, Children (Data, Item)) else 0);
   function Element (Data : E.Bytes; Item : E.Span; Ordinal : E.Count)
      return E.Span is
     (if Is_Sequence (Data, Item) then E.Array_Element (Data, Children (Data, Item), Ordinal)
      else (1, 0));

   function Record_Field (Data : E.Bytes; Item : E.Span; Name : String)
      return E.Span
   is
      Fields : constant E.Span := S.A.Field (Data, Item, "fields");
   begin
      if not S.Valid (Data, Item) then return (1, 0); end if;
      return S.A.Field (Data, Fields, Name);
   end Record_Field;

   function Nonnegative_Count (Data : E.Bytes; Item : E.Span)
      return Count_Result
   is
      Value : E.Count := 0;
   begin
      if not Is_Integer (Data, Item) or else Negative (Data, Item) then
         return (Present => False);
      end if;
      declare
         Raw : constant E.Bytes := Magnitude_Value (Data, Item);
      begin
         for I in reverse Raw'Range loop
            pragma Loop_Variant (Decreases => I);
            if Value > (E.Count'Last - E.Count (Raw (I))) / 256 then
               return (Present => False);
            end if;
            Value := Value * 256 + E.Count (Raw (I));
         end loop;
      end;
      return (Present => True, Value => Value);
   end Nonnegative_Count;
end Worldline.Custody_V2_Values;
