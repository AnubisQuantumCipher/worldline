with Attest;
with Attest.SHA256;
with Interfaces;
package body Worldline.Producer_Bytes with SPARK_Mode is
   use type Interfaces.Unsigned_8;
   use type Interfaces.Unsigned_64;

   subtype Sextet_Value is Integer range -1 .. 63;
   function Sextet (C : Character) return Sextet_Value is
     (if C in 'A' .. 'Z' then Character'Pos (C) - Character'Pos ('A')
      elsif C in 'a' .. 'z' then Character'Pos (C) - Character'Pos ('a') + 26
      elsif C in '0' .. '9' then Character'Pos (C) - Character'Pos ('0') + 52
      elsif C = '+' then 62 elsif C = '/' then 63 else -1);

   --  Count and decode use the same recognizer. The empty count-only output
   --  avoids a source-wide validity precondition or a second parsing model.
   procedure Scan_Base64
     (Encoded : String; Render : Boolean; Output : out String; Size : out Extent)
   with
     Global => null,
     Pre => Render or else Output'Length = 0,
     Relaxed_Initialization => Output,
     Post => Output'Initialized
   is
      Phase : Natural range 0 .. 3 := 0;
      Carry : Natural range 0 .. 63 := 0;
      Used, Padding : Natural := 0;
      Padded, Seen_Digit : Boolean := False;
      Accepted : Boolean := True;
   begin
      for I in Encoded'Range loop
         pragma Loop_Invariant (Used <= I - Encoded'First);
         pragma Loop_Invariant (Padding <= I - Encoded'First);
         pragma Loop_Invariant (if Render then Used <= Output'Length);
         pragma Loop_Invariant (if not Render then Carry = 0);
         pragma Loop_Invariant (if Phase = 2 then Carry <= 15);
         pragma Loop_Invariant (if Phase = 3 then Carry <= 3);
         pragma Loop_Invariant
           (if Render and then Used > 0 then
              Output (Output'First .. Output'First + (Used - 1))'Initialized);
         if Encoded (I) = '=' then
            if not Seen_Digit or else Phase not in 0 | 2 | 3 then
               Accepted := False;
               exit;
            end if;
            Padded := True;
            Padding := Padding + 1;
         else
            declare
               Raw : constant Sextet_Value := Sextet (Encoded (I));
            begin
               if Padded or else Raw < 0 then
                  Accepted := False;
                  exit;
               end if;
               declare
                  Digit : constant Natural range 0 .. 63 := Natural (Raw);
               begin
                  Seen_Digit := True;
                  if Phase = 0 then
                     if Render then Carry := Digit; end if;
                     Phase := 1;
                  else
                     if Render then
                        if Used = Output'Length then
                           Accepted := False;
                           exit;
                        end if;
                        declare
                           Byte : constant Character := Character'Val
                             (if Phase = 1 then Carry * 4 + Digit / 16
                              elsif Phase = 2 then Carry * 16 + Digit / 4
                              else Carry * 64 + Digit);
                        begin
                           Used := Used + 1;
                           Output (Output'First + (Used - 1)) := Byte;
                        end;

                     else
                        Used := Used + 1;
                     end if;
                     --  Keep the phase and its carry bound in the same branch.
                     --  Count-only scans retain their zero carry.
                     if Phase = 1 then
                        if Render then Carry := Digit mod 16; end if;
                        Phase := 2;
                     elsif Phase = 2 then
                        if Render then Carry := Digit mod 4; end if;
                        Phase := 3;
                     else
                        Carry := 0;
                        Phase := 0;
                     end if;
                  end if;
               end;
            end;
         end if;
      end loop;
      --  In particular, phase zero deliberately permits any padding count.
      if not Accepted or else Phase = 1 or else
        (Phase = 2 and then Padding /= 2) or else
        (Phase = 3 and then Padding /= 1) or else
        (Render and then Used /= Output'Length)
      then
         Output := (others => Character'Val (0));
         Size := (0, False);
      else
         pragma Assert (Output'Initialized);
         Size := (Used, True);
      end if;
   end Scan_Base64;

   function Base64_Extent (Encoded : String) return Extent is
      Empty : String (1 .. 0);
      Size : Extent;
   begin
      Scan_Base64 (Encoded, False, Empty, Size);
      pragma Assert (Empty = "");
      return Size;
   end Base64_Extent;

   procedure Decode_Base64
     (Encoded : String; Output : out String; Valid : out Boolean)
   is
      Size : Extent;
   begin
      Scan_Base64 (Encoded, True, Output, Size);
      Valid := Size.Valid;
   end Decode_Base64;

   function Base64 (Encoded : String) return Decoded is
      Size : constant Extent := Base64_Extent (Encoded);
      Output : String (1 .. Size.Length);
      Rendered : Extent;
   begin
      if not Size.Valid then return (0, False, ""); end if;
      Scan_Base64 (Encoded, True, Output, Rendered);
      return (Size.Length, Rendered.Valid, Output);
   end Base64;

   function Digest (Data : String) return String is
      State : Attest.SHA256.Context := Attest.SHA256.Initial;
      Block : Attest.Byte_Array (0 .. 63) with Relaxed_Initialization;
      Fill : Natural range 0 .. 63 := 0;
      Result : String (1 .. 64) with Relaxed_Initialization;
      Alphabet : constant String := "0123456789abcdef";
   begin
      for I in Data'Range loop
         pragma Loop_Invariant
           (Attest.SHA256.Absorbed (State) <=
              Interfaces.Unsigned_64 (Data'Length));
         pragma Loop_Invariant
           (Attest.SHA256.Absorbed (State) + Interfaces.Unsigned_64 (Fill) =
              Interfaces.Unsigned_64 (I - Data'First));
         pragma Loop_Invariant
           (if Fill > 0 then Block (0 .. Fill - 1)'Initialized);
         Block (Fill) := Interfaces.Unsigned_8 (Character'Pos (Data (I)));
         if Fill = 63 then
            pragma Assert (Block'Initialized);
            Attest.SHA256.Update (State, Block);
            Fill := 0;
         else
            Fill := Fill + 1;
         end if;
      end loop;
      if Fill > 0 then
         Attest.SHA256.Update (State, Block (0 .. Fill - 1));
      end if;
      declare
         Hash : constant Attest.SHA256.Digest := Attest.SHA256.Final (State);
      begin
         for I in Hash'Range loop
            Result (2 * I + 1) := Alphabet (Natural (Hash (I) / 16) + 1);
            Result (2 * I + 2) := Alphabet (Natural (Hash (I) mod 16) + 1);
            pragma Loop_Invariant
              (Result (1 .. 2 * I + 2)'Initialized);
         end loop;
      end;
      pragma Assert (Result'Initialized);
      return Result;
   end Digest;
end Worldline.Producer_Bytes;
