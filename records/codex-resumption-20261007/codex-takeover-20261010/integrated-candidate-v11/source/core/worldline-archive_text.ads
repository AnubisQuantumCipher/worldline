with Interfaces;
with Resource_Quantities;

-- Exact decoded archive string bytes: UTF-8 with surrogatepass, not strict
-- Unicode scalar values. No normalization, source authentication or JSON tags.
package Worldline.Archive_Text with SPARK_Mode is
   package Q renames Resource_Quantities;
   use type Q.Byte;
   use type Q.Byte_Count;
   use type Interfaces.Unsigned_32;
   subtype Code_Point is Interfaces.Unsigned_32 range 0 .. 16#10_FFFF#;
   type Span is record
      First : Q.Byte_Index;
      Length : Q.Byte_Count;
   end record;
   function Span_Valid (Data : Q.Byte_Array; Item : Span) return Boolean is
     (Item.Length = 0 or else
      (Item.First in Data'Range and then Item.Length <= Data'Last - Item.First + 1))
   with Global => null;
   function Continuation (Value : Q.Byte) return Boolean is
     (Value in 16#80# .. 16#BF#) with Global => null;

   -- Zero means no complete canonical surrogatepass codepoint starts here.
   -- Length checks precede every tail access; arithmetic uses offsets and
   -- never forms a one-past-last arena index.
   function Unit_Width (Data : Q.Byte_Array; Item : Span; Offset : Q.Byte_Count)
      return Q.Byte_Count is
     (if not Span_Valid (Data, Item) or else Offset >= Item.Length then 0
      elsif Data (Item.First + Offset) <= 16#7F# then 1
      elsif Data (Item.First + Offset) in 16#C2# .. 16#DF# and then
        Item.Length - Offset >= 2 and then
        Continuation (Data (Item.First + (Offset + 1))) then 2
      elsif Item.Length - Offset >= 3 and then
        ((Data (Item.First + Offset) = 16#E0# and then
          Data (Item.First + (Offset + 1)) in 16#A0# .. 16#BF#) or else
         (Data (Item.First + Offset) in 16#E1# .. 16#EF# and then
          Continuation (Data (Item.First + (Offset + 1))))) and then
        Continuation (Data (Item.First + (Offset + 2))) then 3
      elsif Item.Length - Offset >= 4 and then
        ((Data (Item.First + Offset) = 16#F0# and then
          Data (Item.First + (Offset + 1)) in 16#90# .. 16#BF#) or else
         (Data (Item.First + Offset) in 16#F1# .. 16#F3# and then
          Continuation (Data (Item.First + (Offset + 1)))) or else
         (Data (Item.First + Offset) = 16#F4# and then
          Data (Item.First + (Offset + 1)) in 16#80# .. 16#8F#)) and then
        Continuation (Data (Item.First + (Offset + 2))) and then
        Continuation (Data (Item.First + (Offset + 3))) then 4
      else 0)
   with Global => null,
     Post => Unit_Width'Result <= 4 and then
       (if Unit_Width'Result > 0 then
          Span_Valid (Data, Item) and then Offset < Item.Length and then
          Unit_Width'Result <= Item.Length - Offset);

   -- Every byte is either a complete codepoint head or a continuation inside
   -- a complete preceding codepoint. The bounded lookback is the encoding's
   -- codepoint width, not a string/input/domain cap.
   function Text_Valid (Data : Q.Byte_Array; Item : Span) return Boolean is
     (Span_Valid (Data, Item) and then
      (if Item.Length > 0 then
         (for all Offset in Q.Byte_Count range 0 .. Item.Length - 1 =>
            Unit_Width (Data, Item, Offset) > 0 or else
            (Continuation (Data (Item.First + Offset)) and then
             ((Offset >= 1 and then Unit_Width (Data, Item, Offset - 1) >= 2) or else
              (Offset >= 2 and then Unit_Width (Data, Item, Offset - 2) >= 3) or else
              (Offset >= 3 and then Unit_Width (Data, Item, Offset - 3) = 4))))))
   with Global => null;

   -- The resulting range includes surrogate codepoints deliberately. This
   -- matches the original surrogatepass identity/text pair, not RFC3629's
   -- exclusion of surrogate scalar values.
   function Value_At (Data : Q.Byte_Array; Item : Span; Offset : Q.Byte_Count)
      return Code_Point is
     (case Unit_Width (Data, Item, Offset) is
        when 1 => Interfaces.Unsigned_32 (Data (Item.First + Offset)),
        when 2 =>
          Interfaces.Unsigned_32 (Data (Item.First + Offset) mod 32) * 64 +
          Interfaces.Unsigned_32 (Data (Item.First + (Offset + 1)) mod 64),
        when 3 =>
          Interfaces.Unsigned_32 (Data (Item.First + Offset) mod 16) * 4096 +
          Interfaces.Unsigned_32 (Data (Item.First + (Offset + 1)) mod 64) * 64 +
          Interfaces.Unsigned_32 (Data (Item.First + (Offset + 2)) mod 64),
        when others =>
          Interfaces.Unsigned_32 (Data (Item.First + Offset) mod 8) * 262144 +
          Interfaces.Unsigned_32 (Data (Item.First + (Offset + 1)) mod 64) * 4096 +
          Interfaces.Unsigned_32 (Data (Item.First + (Offset + 2)) mod 64) * 64 +
          Interfaces.Unsigned_32 (Data (Item.First + (Offset + 3)) mod 64))
   with Global => null, Pre => Unit_Width (Data, Item, Offset) > 0;

   type Decode_Status is (Decoded, End_Of_Text, Invalid_Position, Invalid_Sequence);
   type Scalar_Result (Status : Decode_Status := Invalid_Position) is record
      Raw : Span;
      Start : Q.Byte_Count;
      case Status is
         when Decoded =>
            Value : Code_Point;
            Width, Next_Offset : Q.Byte_Count;
         when End_Of_Text | Invalid_Position | Invalid_Sequence => null;
      end case;
   end record;

   -- Total cursor operation. A successful individual codepoint never claims
   -- that any preceding/following bytes or the whole archive are valid.
   function Read (Data : Q.Byte_Array; Item : Span; Offset : Q.Byte_Count)
      return Scalar_Result
   with Global => null,
     Post => Read'Result.Raw = Item and then Read'Result.Start = Offset and then
       (if not Span_Valid (Data, Item) or else Offset > Item.Length then
           Read'Result.Status = Invalid_Position
        elsif Offset = Item.Length then Read'Result.Status = End_Of_Text
        elsif Unit_Width (Data, Item, Offset) = 0 then
           Read'Result.Status = Invalid_Sequence
        else Read'Result.Status = Decoded and then
           Read'Result.Value = Value_At (Data, Item, Offset) and then
           Read'Result.Width = Unit_Width (Data, Item, Offset) and then
           Read'Result.Next_Offset = Offset + Read'Result.Width and then
           Read'Result.Next_Offset > Offset and then
           Read'Result.Next_Offset <= Item.Length);
end Worldline.Archive_Text;
