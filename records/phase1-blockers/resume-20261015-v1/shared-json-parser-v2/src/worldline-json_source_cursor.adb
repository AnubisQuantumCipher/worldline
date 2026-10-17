package body Worldline.JSON_Source_Cursor with SPARK_Mode is
   function Initial (Data : Q.Byte_Array; Item : Span) return Cursor is
   begin
      return (Item => Item, Kind => Detected_Encoding (Data, Item),
              Offset => BOM_Length (Data, Item));
   end Initial;

   function Read (Data : Q.Byte_Array; Current : Cursor) return Step is
      Position : constant Count := Current.Offset;
   begin
      if not T.Span_Valid (Data, Current.Item) or else
          Position > Current.Item.Length then
         return (Invalid_Position, Position, Position, 0);
      elsif Position = Current.Item.Length then
         return (End_Of_Text, Position, Position, 0);
      end if;

      case Current.Kind is
         when UTF8 =>
            declare
               Width : constant Count := T.Unit_Width (Data, Current.Item, Position);
            begin
               if Width = 0 then
                  return (Invalid_Sequence, Position, Position, 0);
               end if;
               return (Decoded, Position, Position + Width,
                       T.Value_At (Data, Current.Item, Position));
            end;
         when UTF16_BE | UTF16_LE =>
            if Current.Item.Length - Position < 2 then
               return (Invalid_Sequence, Position, Position, 0);
            end if;
            declare
               High : constant Word_16 :=
                 Unit_16 (Data, Current.Item, Current.Kind, Position);
               After_High : constant Count := Position + 2;
            begin
               if High in 16#D800# .. 16#DBFF# and then
                   Current.Item.Length - After_High >= 2 then
                  declare
                     Low : constant Word_16 :=
                       Unit_16 (Data, Current.Item, Current.Kind, After_High);
                  begin
                     if Low in 16#DC00# .. 16#DFFF# then
                        return (Decoded, Position, After_High + 2,
                                Pair_Value (High, Low));
                     end if;
                  end;
               end if;
               -- A lone high or low surrogate remains an accepted codepoint.
               -- A non-low lookahead is left for the next call unchanged.
               return (Decoded, Position, After_High, High);
            end;
         when UTF32_BE | UTF32_LE =>
            if Current.Item.Length - Position < 4 then
               return (Invalid_Sequence, Position, Position, 0);
            end if;
            declare
               U : Interfaces.Unsigned_32 := 0;
            begin
               -- The same original byte-order recurrence. Fixed encoding
               -- width is not an input/token/depth/count cap.
               for K in Count range 0 .. 3 loop
                  U := U * 256 + Byte_At
                    (Data, Current.Item,
                     Position + (if Current.Kind = UTF32_BE then K else 3 - K));
               end loop;
               if U > Code_Point'Last then
                  return (Invalid_Sequence, Position, Position, 0);
               end if;
               return (Decoded, Position, Position + 4, U);
            end;
      end case;
   end Read;
end Worldline.JSON_Source_Cursor;
