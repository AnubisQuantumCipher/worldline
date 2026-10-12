with Resource_Quantities;

-- Canonical archive byte-leaf decoding. Neither JSON extraction nor authority.
package Worldline.Archive_Base64 with SPARK_Mode is
   package Q renames Resource_Quantities;
   use type Q.Byte;
   use type Q.Byte_Count;

   type Span is record
      First : Q.Byte_Index;
      Length : Q.Byte_Count;
   end record;
   function Span_Valid (Data : Q.Byte_Array; Item : Span) return Boolean is
     (Item.Length = 0 or else
      (Item.First in Data'Range and then
       Item.Length <= Data'Last - Item.First + 1))
   with Global => null;

   -- Standard alphabet selected by original base64.b64encode/b64decode;
   -- URL-safe substitutions and whitespace are not accepted archive text.
   function Is_Digit (Value : Q.Byte) return Boolean is
     (Value in Character'Pos ('A') .. Character'Pos ('Z') or else
      Value in Character'Pos ('a') .. Character'Pos ('z') or else
      Value in Character'Pos ('0') .. Character'Pos ('9') or else
      Value = Character'Pos ('+') or else Value = Character'Pos ('/'))
   with Global => null;

   function Digit (Value : Q.Byte) return Q.Byte is
     (if Value in Character'Pos ('A') .. Character'Pos ('Z') then
         Value - Character'Pos ('A')
      elsif Value in Character'Pos ('a') .. Character'Pos ('z') then
         Value - Character'Pos ('a') + 26
      elsif Value in Character'Pos ('0') .. Character'Pos ('9') then
         Value - Character'Pos ('0') + 52
      elsif Value = Character'Pos ('+') then 62 else 63)
   with Global => null, Pre => Is_Digit (Value), Post => Digit'Result <= 63;

   -- Only count terminal padding; Canonical below validates every character,
   -- legal location, quartet size and unused low bits. Not sufficient alone.
   function Padding (Data : Q.Byte_Array; Item : Span) return Q.Byte_Count is
     (if Data (Item.First + (Item.Length - 1)) /= Character'Pos ('=') then 0
      elsif Data (Item.First + (Item.Length - 2)) = Character'Pos ('=') then 2
      else 1)
   with Global => null,
     Pre => Span_Valid (Data, Item) and then Item.Length >= 4,
     Post => Padding'Result <= 2;

   function Canonical (Data : Q.Byte_Array; Item : Span) return Boolean is
     (Span_Valid (Data, Item) and then
      (Item.Length = 0 or else
       (Item.Length >= 4 and then Item.Length mod 4 = 0 and then
        (for all Offset in Q.Byte_Count range 0 .. Item.Length - 1 =>
           (if Offset < Item.Length - Padding (Data, Item) then
               Is_Digit (Data (Item.First + Offset))
            else Data (Item.First + Offset) = Character'Pos ('='))) and then
        (case Padding (Data, Item) is
           when 2 => Digit (Data (Item.First + (Item.Length - 3))) mod 16 = 0,
           when 1 => Digit (Data (Item.First + (Item.Length - 2))) mod 4 = 0,
           when others => True))))
   with Global => null;

   --  Only the span and the terminal padding are read. The local condition is
   --  tested first, so a run-time-checked call (-gnata) costs O(1) instead of
   --  re-validating the whole span on every call; a canonical span satisfies
   --  it, and the original canonical precondition remains a sufficient case.
   function Decoded_Length (Data : Q.Byte_Array; Item : Span)
      return Q.Byte_Count is
     (if Item.Length = 0 then 0
      else (Item.Length / 4) * 3 - Padding (Data, Item))
   with Global => null,
     Pre => (Span_Valid (Data, Item) and then
             (Item.Length = 0 or else Item.Length >= 4))
            or else Canonical (Data, Item),
     Post => Decoded_Length'Result <= Item.Length;

   --  The two sextets that output byte Offset is projected from lie inside
   --  the span and are alphabet digits (never padding).
   function Byte_Readable
     (Data : Q.Byte_Array; Item : Span; Offset : Q.Byte_Count) return Boolean is
     (Span_Valid (Data, Item) and then Offset / 3 < Item.Length / 4 and then
      Is_Digit (Data (Item.First + ((Offset / 3) * 4 + Offset mod 3))) and then
      Is_Digit (Data (Item.First + ((Offset / 3) * 4 + Offset mod 3 + 1))))
   with Global => null;

   -- Projection of every output byte, in original byte order. Full-span
   -- canonicality prevents any selected sextet from designating padding.
   -- Byte_Readable states exactly what the projection reads and is tested
   -- first, so a run-time-checked call (-gnata) costs O(1) rather than a
   -- full-span re-validation per byte (quadratic decoding under checks); the
   -- original canonical precondition remains a sufficient case unchanged.
   function Decoded_Byte
     (Data : Q.Byte_Array; Item : Span; Offset : Q.Byte_Count) return Q.Byte is
     (case Offset mod 3 is
        when 0 =>
          Digit (Data (Item.First + (Offset / 3) * 4)) * 4 +
          Digit (Data (Item.First + ((Offset / 3) * 4 + 1))) / 16,
        when 1 =>
          (Digit (Data (Item.First + ((Offset / 3) * 4 + 1))) mod 16) * 16 +
          Digit (Data (Item.First + ((Offset / 3) * 4 + 2))) / 4,
        when others =>
          (Digit (Data (Item.First + ((Offset / 3) * 4 + 2))) mod 4) * 64 +
          Digit (Data (Item.First + ((Offset / 3) * 4 + 3))))
   with Global => null,
     Pre => Byte_Readable (Data, Item, Offset)
            or else (Canonical (Data, Item) and then Offset < Decoded_Length (Data, Item));

   -- Complete output, with no silent truncation and no output allocation cap.
   -- The supplied Ada array's validity/ownership remains language-level;
   -- this is not a foreign pointer reader or a caller authenticity assertion.
   procedure Decode
     (Data : Q.Byte_Array; Item : Span; Result : out Q.Byte_Array)
   --  Result contributes its incoming bounds, never incoming element values.
   with Global => null, Depends => (Result => (Result, Data, Item)),
     Always_Terminates,
     Pre => Canonical (Data, Item) and then
       Result'Length = Decoded_Length (Data, Item),
     Post => (for all I in Result'Range =>
       Result (I) = Decoded_Byte (Data, Item, I - Result'First));
end Worldline.Archive_Base64;
