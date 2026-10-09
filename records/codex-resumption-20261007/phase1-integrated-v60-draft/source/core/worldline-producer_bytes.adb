with Attest;
with Attest.SHA256;
with Interfaces;
package body Worldline.Producer_Bytes with SPARK_Mode is
   use type Interfaces.Unsigned_8;
   function Sextet (C : Character) return Integer is
     (if C in 'A' .. 'Z' then Character'Pos (C) - Character'Pos ('A')
      elsif C in 'a' .. 'z' then Character'Pos (C) - Character'Pos ('a') + 26
      elsif C in '0' .. '9' then Character'Pos (C) - Character'Pos ('0') + 52
      elsif C = '+' then 62 elsif C = '/' then 63 else -1);

   function Base64_Extent (Encoded : String) return Extent is
      Used : Natural := 0;
      Phase : Natural range 0 .. 3 := 0;
      Padding : Natural := 0;
      Padded, Seen_Digit : Boolean := False;
   begin
      for C of Encoded loop
         if C = '=' then
            if not Seen_Digit or else Phase not in 0 | 2 | 3 then return (0, False); end if;
            Padded := True; Padding := Padding + 1;
         else
            if Padded or else Sextet (C) < 0 then return (0, False); end if;
            Seen_Digit := True;
            if Phase /= 0 then Used := Used + 1; end if;
            Phase := (Phase + 1) mod 4;
         end if;
      end loop;
      if Phase = 1 or else (Phase = 2 and then Padding /= 2) or else
        (Phase = 3 and then Padding /= 1) then return (0, False); end if;
      return (Used, True);
   end Base64_Extent;
   procedure Render_Base64 (Encoded : String; Output : out String) is
      Phase : Natural range 0 .. 3 := 0;
      Carry : Natural range 0 .. 63 := 0;
      Used : Natural := 0;
   begin
      for C of Encoded loop
         if C /= '=' then
            declare Digit : constant Natural := Natural (Sextet (C));
            begin
               case Phase is
                  when 0 => Carry := Digit;
                  when 1 =>
                     Used := Used + 1;
                     Output (Output'First + Used - 1) := Character'Val (Carry * 4 + Digit / 16);
                     Carry := Digit mod 16;
                  when 2 =>
                     Used := Used + 1;
                     Output (Output'First + Used - 1) := Character'Val (Carry * 16 + Digit / 4);
                     Carry := Digit mod 4;
                  when 3 =>
                     Used := Used + 1;
                     Output (Output'First + Used - 1) := Character'Val (Carry * 64 + Digit);
                     Carry := 0;
               end case;
               Phase := (Phase + 1) mod 4;
            end;
         end if;
      end loop;
   end Render_Base64;
   procedure Decode_Base64 (Encoded : String; Output : out String; Valid : out Boolean) is
      Size : constant Extent := Base64_Extent (Encoded);
   begin
      Valid := Size.Valid and then Size.Length = Output'Length;
      if not Valid then Output := (others => Character'Val (0)); return; end if;
      Render_Base64 (Encoded, Output);
   end Decode_Base64;
   function Base64 (Encoded : String) return Decoded is
      Size : constant Extent := Base64_Extent (Encoded);
      Output : String (1 .. Size.Length);
   begin
      if not Size.Valid then return (0, False, ""); end if;
      Render_Base64 (Encoded, Output);
      return (Size.Length, True, Output);
   end Base64;
   function Digest (Data : String) return String is
      State : Attest.SHA256.Context := Attest.SHA256.Initial;
      Block : Attest.Byte_Array (0 .. 63);
      Fill : Natural range 0 .. 63 := 0;
      Result : String (1 .. 64);
      Alphabet : constant String := "0123456789abcdef";
   begin
      for C of Data loop
         Block (Fill) := Interfaces.Unsigned_8 (Character'Pos (C));
         if Fill = 63 then
            Attest.SHA256.Update (State, Block);
            Fill := 0;
         else Fill := Fill + 1;
         end if;
      end loop;
      if Fill > 0 then Attest.SHA256.Update (State, Block (0 .. Fill - 1)); end if;
      declare
         Hash : constant Attest.SHA256.Digest := Attest.SHA256.Final (State);
      begin
         for I in Hash'Range loop
            Result (2 * I + 1) := Alphabet (Natural (Hash (I) / 16) + 1);
            Result (2 * I + 2) := Alphabet (Natural (Hash (I) mod 16) + 1);
         end loop;
      end;
      return Result;
   end Digest;
end Worldline.Producer_Bytes;
