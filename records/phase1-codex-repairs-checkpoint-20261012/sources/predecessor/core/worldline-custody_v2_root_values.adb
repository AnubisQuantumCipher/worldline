package body Worldline.Custody_V2_Root_Values with SPARK_Mode is
   use type E.Value_Kind;
   use type Q.Byte;
   function View (Data : E.Bytes; Item : E.Span) return E.View is
     (E.Decode (Data, Item, E.Operation));
   function Valid (Data : E.Bytes; Item : E.Span) return Boolean is
     (S.A.Valid (Data, Item));
   function Record_Field (Data : E.Bytes; Item : E.Span; Name : String) return E.Span is
      Whole : constant E.View := View (Data, Item);
   begin
      if not Valid (Data, Item) then return (1, 0); end if;
      if Whole.Form /= E.Record_Value then return S.A.Field (Data, Item, Name); end if;
      for I in E.Count range 1 .. E.Array_Length (Data, Whole.Children) loop
         pragma Loop_Variant (Increases => I);
         declare Pair : constant E.View := E.Decode
           (Data, E.Array_Element (Data, Whole.Children, I - 1), E.Finalization);
         begin
            if Pair.Form = E.List_Value and then E.Array_Length (Data, Pair.Children) = 2 and then
               E.Text_Is (Data, E.Decode (Data, E.Array_Element (Data, Pair.Children, 0), E.Finalization), Name)
            then return E.Array_Element (Data, Pair.Children, 1); end if;
         end;
      end loop;
      return (1, 0);
   end Record_Field;
   function Bytes_Key_Field (Data : E.Bytes; Item : E.Span; Name : String)
      return E.Span
   is
      Whole : constant E.View := View (Data, Item);
   begin
      if not Valid (Data, Item) or else Whole.Form /= E.Object_Value then return (1, 0); end if;
      for I in E.Count range 1 .. E.Array_Length (Data, Whole.Children) loop
         pragma Loop_Variant (Increases => I);
         declare
            Pair : constant E.View := E.Decode
              (Data, E.Array_Element (Data, Whole.Children, I - 1), E.Finalization);
            Key : constant E.Span := E.Array_Element (Data, Pair.Children, 0);
         begin
            if Pair.Form = E.List_Value and then E.Array_Length (Data, Pair.Children) = 2 and then
               Valid_Bytes (Data, Key) then
               declare Raw : constant E.Bytes := Bytes_Value (Data, Key); begin
                  if Raw'Length = Name'Length and then
                     (for all J in Name'Range => Raw (Raw'First + E.Count (J - Name'First)) = Q.Byte (Character'Pos (Name (J))))
                  then return E.Array_Element (Data, Pair.Children, 1); end if;
               end;
            end if;
         end;
      end loop;
      return (1, 0);
   end Bytes_Key_Field;
   function Valid_Text (Data : E.Bytes; Item : E.Span) return Boolean is
     (View (Data, Item).Form = E.Text_Value and then E.Bytes_Valid (Data, View (Data, Item).Payload));
   function Valid_Bytes (Data : E.Bytes; Item : E.Span) return Boolean is
     (View (Data, Item).Form = E.Bytes_Value and then E.Bytes_Valid (Data, View (Data, Item).Payload));
   function Is_Integer (Data : E.Bytes; Item : E.Span) return Boolean is
     (View (Data, Item).Form = E.Integer_Value and then E.Bytes_Valid (Data, View (Data, Item).Payload));
   function Is_Null (Data : E.Bytes; Item : E.Span) return Boolean is
     (View (Data, Item).Form = E.Null_Value);
   function Is_Sequence (Data : E.Bytes; Item : E.Span) return Boolean is
     (View (Data, Item).Form in E.List_Value | E.Tuple_Value and then Valid (Data, Item));
   function Type_Is (Data : E.Bytes; Item : E.Span; Name : String) return Boolean is
     (if Name = "str" then Valid_Text (Data, Item)
      elsif Name = "bytes" then Valid_Bytes (Data, Item)
      elsif Name = "integer" then Is_Integer (Data, Item)
      elsif Name = "bool" then View (Data, Item).Form = E.Boolean_Value
      elsif Name = "NoneType" then Is_Null (Data, Item)
      elsif Name = "dict" then View (Data, Item).Form = E.Object_Value and then Valid (Data, Item)
      elsif Name = "list" then View (Data, Item).Form = E.List_Value and then Valid (Data, Item)
      elsif Name = "tuple" then View (Data, Item).Form = E.Tuple_Value and then Valid (Data, Item)
      else False);
   function Text_Value (Data : E.Bytes; Item : E.Span) return E.Bytes is
     (E.Materialize (Data, View (Data, Item).Payload));
   function Bytes_Value (Data : E.Bytes; Item : E.Span) return E.Bytes is
     (E.Materialize (Data, View (Data, Item).Payload));
   function Magnitude_Value (Data : E.Bytes; Item : E.Span) return E.Bytes is
     (E.Materialize (Data, View (Data, Item).Payload));
   function Negative (Data : E.Bytes; Item : E.Span) return Boolean is (View (Data, Item).Sign);
   function Text_Is (Data : E.Bytes; Item : E.Span; Name : String) return Boolean is
     (Valid_Text (Data, Item) and then E.Text_Is (Data, View (Data, Item), Name));
   function Text_Matches (Data : E.Bytes; Item, Expected : E.Span) return Boolean is
   begin
      if not Valid_Text (Data, Item) or else not E.C.P.Valid (Data, Expected) then return False; end if;
      declare Raw : constant E.Bytes := Text_Value (Data, Item); begin
         return Raw'Length = Expected.Length and then
           (for all I in Raw'Range => Raw (I) = Data (Expected.First + I - Raw'First));
      end;
   end Text_Matches;
   function Hex_Field (Data : E.Bytes; Item : E.Span; Field : String) return E.Span is
   begin
      if Field = "value" and then Valid_Text (Data, Item) then
         return Item;
      else
         return Record_Field (Data, Item, Field);
      end if;
   end Hex_Field;
   function Valid_Hex_Field (Data : E.Bytes; Item : E.Span; Field : String) return Boolean is
   begin
      if not Valid_Text (Data, Hex_Field (Data, Item, Field)) then return False; end if;
      return Original.Hex_Domain (Text_Value (Data, Hex_Field (Data, Item, Field)));
   end Valid_Hex_Field;
   function Nibble (Value : Q.Byte) return Q.Byte is
     (if Value in Character'Pos ('0') .. Character'Pos ('9') then Value - Character'Pos ('0')
      else Value - Character'Pos ('a') + 10)
      with Pre => Value in Character'Pos ('0') .. Character'Pos ('9') | Character'Pos ('a') .. Character'Pos ('f');
   function Hex_Value (Data : E.Bytes; Item : E.Span; Field : String) return E.Bytes is
      Raw : constant E.Bytes := Text_Value (Data, Hex_Field (Data, Item, Field));
   begin
      return Result : E.Bytes (1 .. Raw'Length / 2) do
         for I in Result'Range loop
            pragma Loop_Variant (Increases => I);
            Result (I) := Nibble (Raw (Raw'First + (I - 1) * 2)) * 16 + Nibble (Raw (Raw'First + (I - 1) * 2 + 1));
         end loop;
      end return;
   end Hex_Value;
   function Count (Data : E.Bytes; Item : E.Span) return E.Count is
     (if Is_Sequence (Data, Item) then E.Array_Length (Data, View (Data, Item).Children) else 0);
   function Element (Data : E.Bytes; Item : E.Span; Ordinal : E.Count) return E.Span is
   begin
      if Is_Sequence (Data, Item) then
         return E.Array_Element (Data, View (Data, Item).Children, Ordinal);
      else
         return (1, 0);
      end if;
   end Element;
   function Nonnegative_Count (Data : E.Bytes; Item : E.Span) return Count_Result is
      Result : E.Count := 0;
   begin
      if not Is_Integer (Data, Item) or else Negative (Data, Item) then return (Present => False); end if;
      declare Raw : constant E.Bytes := Magnitude_Value (Data, Item); begin
         for I in reverse Raw'Range loop
            pragma Loop_Variant (Decreases => I);
            if Result > E.Count'Last / 256 or else
               (Result = E.Count'Last / 256 and then E.Count (Raw (I)) > E.Count'Last mod 256)
            then return (Present => False); end if;
            Result := Result * 256 + E.Count (Raw (I));
         end loop;
      end;
      return (Present => True, Value => Result);
   end Nonnegative_Count;
end Worldline.Custody_V2_Root_Values;
