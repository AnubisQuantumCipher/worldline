--  OUTSIDE-PRODUCTION CANDIDATE. UNCOMPILED / UNPROVED / UNRUN.
with Worldline.Producer_Values;
package body UTF8_Chunk_Proposal with SPARK_Mode is
   package V renames Worldline.Producer_Values;

   function Character_At (Text : String; Offset : Natural) return Character
     with Global => null, Pre => Offset < Text'Length
   is
   begin
      pragma Assert (Offset <= Text'Last - Text'First);
      return Text (Text'First + Offset);
   end Character_At;

   function Text_Slice (Text : String; First, After : Natural) return String
     with Global => null,
       Pre => First <= After and then After <= Text'Length,
       Post => Text_Slice'Result'Length = After - First
   is
   begin
      if First = After then return ""; end if;
      return Text (Text'First + First .. Text'First + (After - 1));
   end Text_Slice;

   function Code (Text : String; Offset : Natural; Width : Positive)
      return Natural
     with Global => null, Pre => Width <= 4 and then Offset < Text'Length
       and then Width <= Text'Length - Offset
   is
      Lead : constant Natural := Character'Pos (Text (Text'First + Offset));
   begin
      case Width is
         when 1 => return Lead;
         when 2 =>
            return (Lead mod 32) * 64
              + Character'Pos (Text (Text'First + Offset + 1)) mod 64;
         when 3 =>
            return ((Lead mod 16) * 64
              + Character'Pos (Text (Text'First + Offset + 1)) mod 64) * 64
              + Character'Pos (Text (Text'First + Offset + 2)) mod 64;
         when others =>
            return (((Lead mod 8) * 64
              + Character'Pos (Text (Text'First + Offset + 1)) mod 64) * 64
              + Character'Pos (Text (Text'First + Offset + 2)) mod 64) * 64
              + Character'Pos (Text (Text'First + Offset + 3)) mod 64;
      end case;
   end Code;

   procedure Step
     (Bytes : String; Position : Natural; Advance, Width : out Natural)
     with Global => null, Always_Terminates,
       Pre => Position < Bytes'Length,
       Post => Advance >= 1 and then Advance <= 4 and then
         Advance <= Bytes'Length - Position and then Width <= 4 and then
         Width <= Bytes'Length - Position and then
         (if Width > 0 then Advance = Width)
   is
      Lead, Next, Wanted : Natural;
   begin
      Width := V.UTF8_Width (Bytes, Position);
      if Width > 0 and then Code (Bytes, Position, Width) not in 16#D800# .. 16#DFFF# then
         Advance := Width; return;
      end if;
      Width := 0; Advance := 1;
      Lead := Character'Pos (Character_At (Bytes, Position));
      Wanted := (if Lead in 16#C2# .. 16#DF# then 2 elsif Lead in 16#E0# .. 16#EF# then 3
                 elsif Lead in 16#F0# .. 16#F4# then 4 else 1);
      while Advance < Wanted and then Advance < Bytes'Length - Position loop
         pragma Loop_Invariant (Advance >= 1 and then Advance <= 4);
         pragma Loop_Invariant (Advance <= Bytes'Length - Position);
         pragma Loop_Variant (Increases => Advance);
         Next := Character'Pos (Character_At (Bytes, Position + Advance));
         exit when Next not in 16#80# .. 16#BF# or else
           (Advance = 1 and then ((Lead = 16#E0# and then Next < 16#A0#) or else
            (Lead = 16#ED# and then Next >= 16#A0#) or else
            (Lead = 16#F0# and then Next < 16#90#) or else
            (Lead = 16#F4# and then Next >= 16#90#)));
         Advance := Advance + 1;
      end loop;
   end Step;

   function Quota_For (Input_Length : Natural) return Positive is
     (Natural'Max (Minimum_Quota, Input_Length / Checkpoint_Bound +
       (if Input_Length mod Checkpoint_Bound = 0 then 0 else 1)));

   function Buffer_Capacity (Remaining : Natural; Quota : Positive)
      return Positive is (3 * (Natural'Min (Quota, Remaining) + 3));

   function Decode_Chunk
     (Bytes : String; Start : Natural; Quota : Positive;
      Replace_Errors : Boolean) return Chunk_Result
   is
      Bound : constant Natural := Natural'Min (Quota, Bytes'Length - Start);
      Capacity : constant Positive := Buffer_Capacity (Bytes'Length - Start, Quota);
      Position : Natural := Start;
      Used : Natural := 0;
      Advance, Width, Added : Natural;
      Valid : Boolean := True;
   begin
      return Result : Chunk_Result (Capacity) do
         Result.Item := (Start, 0, True);
         Result.Data := [others => Character'Val (0)];
         while Position < Bytes'Length and then Position - Start < Quota loop
            pragma Loop_Invariant (Valid);
            pragma Loop_Invariant (Position >= Start and then Position <= Bytes'Length);
            pragma Loop_Invariant (Position - Start <= Bound + 3);
            pragma Loop_Invariant (Used <= 3 * (Position - Start));
            pragma Loop_Invariant (Used <= Capacity);
            pragma Loop_Variant (Increases => Position);
            Step (Bytes, Position, Advance, Width);
            if Width = 0 and then not Replace_Errors then
               Valid := False; exit;
            end if;
            Added := (if Width = 0 then 3 else Width);
            pragma Assert (Added <= 3 * Advance);
            pragma Assert (Position - Start + Advance <= Bound + 3);
            pragma Assert (Used + Added <= Capacity);
            if Width > 0 then
               Result.Data (Used + 1 .. Used + Width) :=
                 Text_Slice (Bytes, Position, Position + Width);
            else
               Result.Data (Used + 1 .. Used + 3) :=
                 Character'Val (16#EF#) & Character'Val (16#BF#) & Character'Val (16#BD#);
            end if;
            Used := Used + Added;
            Position := Position + Advance;
         end loop;
         Result.Item := (Position, Used, Valid);
      end return;
   end Decode_Chunk;
end UTF8_Chunk_Proposal;

