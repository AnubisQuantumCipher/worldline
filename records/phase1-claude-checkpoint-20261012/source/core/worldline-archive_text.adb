package body Worldline.Archive_Text with SPARK_Mode is
   function Read (Data : Q.Byte_Array; Item : Span; Offset : Q.Byte_Count)
      return Scalar_Result is
   begin
      if not Span_Valid (Data, Item) or else Offset > Item.Length then
         return (Status => Invalid_Position, Raw => Item, Start => Offset);
      elsif Offset = Item.Length then
         return (Status => End_Of_Text, Raw => Item, Start => Offset);
      else
         declare
            Width : constant Q.Byte_Count := Unit_Width (Data, Item, Offset);
         begin
            if Width = 0 then
               return (Status => Invalid_Sequence, Raw => Item, Start => Offset);
            else
               return (Status => Decoded, Raw => Item, Start => Offset,
                       Value => Value_At (Data, Item, Offset), Width => Width,
                       Next_Offset => Offset + Width);
            end if;
         end;
      end if;
   end Read;
end Worldline.Archive_Text;
