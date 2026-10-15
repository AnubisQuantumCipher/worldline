with Interfaces;
with Resource_Quantities;
with Worldline.Archive_Text;

-- UNAPPLIED CANDIDATE. Not compiled, tested, or proved. This package only
-- decodes source codepoints; it does not admit JSON or replace its grammar.
package Worldline.JSON_Source_Cursor with SPARK_Mode is
   package Q renames Resource_Quantities;
   package T renames Worldline.Archive_Text;
   subtype Count is Q.Byte_Count;
   subtype Span is T.Span;
   subtype Code_Point is T.Code_Point;
   subtype Word_16 is Interfaces.Unsigned_32 range 0 .. 16#FFFF#;
   use type Count;
   use type Interfaces.Unsigned_32;
   use type T.Span;

   type Encoding is (UTF8, UTF16_BE, UTF16_LE, UTF32_BE, UTF32_LE);
   type Cursor is record
      Item : Span := (First => 1, Length => 0);
      Kind : Encoding := UTF8;
      Offset : Count := 0;
   end record;
   type Step_Status is
     (Decoded, End_Of_Text, Invalid_Position, Invalid_Sequence);
   type Step is record
      Status : Step_Status := Invalid_Position;
      Start, Next_Offset : Count := 0;
      Value : Code_Point := 0;
   end record;

   -- Explicit byte equations are small local contracts, not preconditions
   -- on the public total Initial/Read operations. No complete text is built.
   function Byte_At (Data : Q.Byte_Array; Item : Span; Offset : Count)
      return Interfaces.Unsigned_32 is
     (Interfaces.Unsigned_32 (Data (Item.First + Offset)))
   with Global => null,
     Pre => T.Span_Valid (Data, Item) and then Offset < Item.Length,
     Post => Byte_At'Result <= 255;

   function Unit_16
     (Data : Q.Byte_Array; Item : Span; Kind : Encoding; Offset : Count)
      return Word_16 is
     (if Kind = UTF16_LE then
         Byte_At (Data, Item, Offset) + 256 * Byte_At (Data, Item, Offset + 1)
      else Byte_At (Data, Item, Offset) * 256 + Byte_At (Data, Item, Offset + 1))
   with Global => null,
     Pre => T.Span_Valid (Data, Item) and then Offset <= Item.Length and then
       Item.Length - Offset >= 2 and then Kind in UTF16_BE | UTF16_LE;

   function Unit_32
     (Data : Q.Byte_Array; Item : Span; Kind : Encoding; Offset : Count)
      return Interfaces.Unsigned_32 is
     (if Kind = UTF32_BE then
         ((Byte_At (Data, Item, Offset) * 256 +
           Byte_At (Data, Item, Offset + 1)) * 256 +
           Byte_At (Data, Item, Offset + 2)) * 256 +
           Byte_At (Data, Item, Offset + 3)
      else
         ((Byte_At (Data, Item, Offset + 3) * 256 +
           Byte_At (Data, Item, Offset + 2)) * 256 +
           Byte_At (Data, Item, Offset + 1)) * 256 +
           Byte_At (Data, Item, Offset))
   with Global => null,
     Pre => T.Span_Valid (Data, Item) and then Offset <= Item.Length and then
       Item.Length - Offset >= 4 and then Kind in UTF32_BE | UTF32_LE;

   function Pair_Value (High, Low : Word_16) return Code_Point is
     (65536 + (High - 16#D800#) * 1024 + Low - 16#DC00#)
   with Global => null,
     Pre => High in 16#D800# .. 16#DBFF# and then
       Low in 16#DC00# .. 16#DFFF#;

   -- These are the original Decode_JSON detection clauses in precedence
   -- order. Invalid spans are never read; empty valid spans are preserved.
   function Detected_Encoding (Data : Q.Byte_Array; Item : Span)
      return Encoding is
     (if not T.Span_Valid (Data, Item) then UTF8
      elsif Item.Length >= 4 and then Byte_At (Data, Item, 0) = 0 and then
        Byte_At (Data, Item, 1) = 0 and then Byte_At (Data, Item, 2) = 254 and then
        Byte_At (Data, Item, 3) = 255 then UTF32_BE
      elsif Item.Length >= 4 and then Byte_At (Data, Item, 0) = 255 and then
        Byte_At (Data, Item, 1) = 254 and then Byte_At (Data, Item, 2) = 0 and then
        Byte_At (Data, Item, 3) = 0 then UTF32_LE
      elsif Item.Length >= 2 and then Byte_At (Data, Item, 0) = 254 and then
        Byte_At (Data, Item, 1) = 255 then UTF16_BE
      elsif Item.Length >= 2 and then Byte_At (Data, Item, 0) = 255 and then
        Byte_At (Data, Item, 1) = 254 then UTF16_LE
      elsif Item.Length >= 3 and then Byte_At (Data, Item, 0) = 239 and then
        Byte_At (Data, Item, 1) = 187 and then Byte_At (Data, Item, 2) = 191 then UTF8
      elsif Item.Length >= 4 then
        (if Byte_At (Data, Item, 0) = 0 then
            (if Byte_At (Data, Item, 1) /= 0 then UTF16_BE else UTF32_BE)
         elsif Byte_At (Data, Item, 1) = 0 then
            (if Byte_At (Data, Item, 2) /= 0 or else
                Byte_At (Data, Item, 3) /= 0 then UTF16_LE else UTF32_LE)
         else UTF8)
      elsif Item.Length = 2 then
        (if Byte_At (Data, Item, 0) = 0 then UTF16_BE
         elsif Byte_At (Data, Item, 1) = 0 then UTF16_LE else UTF8)
      else UTF8)
   with Global => null;

   function BOM_Length (Data : Q.Byte_Array; Item : Span) return Count is
     (if not T.Span_Valid (Data, Item) then 0
      elsif Item.Length >= 4 and then
        ((Byte_At (Data, Item, 0) = 0 and then Byte_At (Data, Item, 1) = 0 and then
          Byte_At (Data, Item, 2) = 254 and then Byte_At (Data, Item, 3) = 255) or else
         (Byte_At (Data, Item, 0) = 255 and then Byte_At (Data, Item, 1) = 254 and then
          Byte_At (Data, Item, 2) = 0 and then Byte_At (Data, Item, 3) = 0)) then 4
      elsif Item.Length >= 2 and then
        ((Byte_At (Data, Item, 0) = 254 and then Byte_At (Data, Item, 1) = 255) or else
         (Byte_At (Data, Item, 0) = 255 and then Byte_At (Data, Item, 1) = 254)) then 2
      elsif Item.Length >= 3 and then Byte_At (Data, Item, 0) = 239 and then
        Byte_At (Data, Item, 1) = 187 and then Byte_At (Data, Item, 2) = 191 then 3
      else 0)
   with Global => null, Post => BOM_Length'Result <= Item.Length;

   function Initial (Data : Q.Byte_Array; Item : Span) return Cursor
   with Global => null,
     Post => Initial'Result.Item = Item and then
       Initial'Result.Kind = Detected_Encoding (Data, Item) and then
       Initial'Result.Offset = BOM_Length (Data, Item) and then
       Initial'Result.Offset <= Item.Length;

   -- Local denotation of the original Scalar operation, without its hidden
   -- Invalid flag or Natural-sized output. This expression is fully within
   -- proof scope. It is never called by Read's executable implementation.
   function Reference_Read (Data : Q.Byte_Array; Current : Cursor) return Step is
     (if not T.Span_Valid (Data, Current.Item) or else
         Current.Offset > Current.Item.Length then
         (Invalid_Position, Current.Offset, Current.Offset, 0)
      elsif Current.Offset = Current.Item.Length then
         (End_Of_Text, Current.Offset, Current.Offset, 0)
      else
        (case Current.Kind is
          when UTF8 =>
            (if T.Unit_Width (Data, Current.Item, Current.Offset) = 0 then
                (Invalid_Sequence, Current.Offset, Current.Offset, 0)
             else
                (Decoded, Current.Offset,
                 Current.Offset + T.Unit_Width (Data, Current.Item, Current.Offset),
                 T.Value_At (Data, Current.Item, Current.Offset))),
          when UTF16_BE | UTF16_LE =>
            (if Current.Item.Length - Current.Offset < 2 then
                (Invalid_Sequence, Current.Offset, Current.Offset, 0)
             elsif Unit_16 (Data, Current.Item, Current.Kind, Current.Offset)
                 in 16#D800# .. 16#DBFF# and then
                 Current.Item.Length - Current.Offset >= 4 and then
                 Unit_16 (Data, Current.Item, Current.Kind, Current.Offset + 2)
                 in 16#DC00# .. 16#DFFF# then
                (Decoded, Current.Offset, Current.Offset + 4,
                 Pair_Value
                   (Unit_16 (Data, Current.Item, Current.Kind, Current.Offset),
                    Unit_16 (Data, Current.Item, Current.Kind, Current.Offset + 2)))
             else
                (Decoded, Current.Offset, Current.Offset + 2,
                 Unit_16 (Data, Current.Item, Current.Kind, Current.Offset))),
          when UTF32_BE | UTF32_LE =>
            (if Current.Item.Length - Current.Offset < 4 or else
                Unit_32 (Data, Current.Item, Current.Kind, Current.Offset) >
                  Code_Point'Last then
                (Invalid_Sequence, Current.Offset, Current.Offset, 0)
             else
                (Decoded, Current.Offset, Current.Offset + 4,
                 Unit_32 (Data, Current.Item, Current.Kind, Current.Offset)))))
   with Ghost, Global => null,
     Post => Reference_Read'Result.Start = Current.Offset and then
       (if Reference_Read'Result.Status = Decoded then
           T.Span_Valid (Data, Current.Item) and then
           Reference_Read'Result.Next_Offset > Current.Offset and then
           Reference_Read'Result.Next_Offset <= Current.Item.Length
        else Reference_Read'Result.Next_Offset = Current.Offset and then
           Reference_Read'Result.Value = 0) and then
       ((Reference_Read'Result.Status = Invalid_Position) =
          (not T.Span_Valid (Data, Current.Item) or else
           Current.Offset > Current.Item.Length)) and then
       ((Reference_Read'Result.Status = End_Of_Text) =
          (T.Span_Valid (Data, Current.Item) and then
           Current.Offset = Current.Item.Length));

   -- Total for any typed Data/span/encoding/offset, including forged or
   -- stale cursors. A successful step certifies only this scalar, not an
   -- earlier prefix, a later suffix, JSON grammar, or source custody.
   function Read (Data : Q.Byte_Array; Current : Cursor) return Step
   with Global => null,
     Post => Read'Result = Reference_Read (Data, Current) and then
       Read'Result.Start = Current.Offset and then
       (if Read'Result.Status = Decoded then
           T.Span_Valid (Data, Current.Item) and then
           Read'Result.Next_Offset > Current.Offset and then
           Read'Result.Next_Offset <= Current.Item.Length
        else Read'Result.Next_Offset = Current.Offset and then
           Read'Result.Value = 0) and then
       ((Read'Result.Status = Invalid_Position) =
          (not T.Span_Valid (Data, Current.Item) or else
           Current.Offset > Current.Item.Length)) and then
       ((Read'Result.Status = End_Of_Text) =
          (T.Span_Valid (Data, Current.Item) and then
           Current.Offset = Current.Item.Length));
end Worldline.JSON_Source_Cursor;
