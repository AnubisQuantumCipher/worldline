package body Worldline.Owner_Subject_Projection with SPARK_Mode is
   Hex : constant String := "0123456789abcdef";
   procedure Feed (C : in out Attest.SHA256.Context; B : Interfaces.Unsigned_8;
      Valid : in out Boolean) is
      One : constant Attest.Byte_Array (0 .. 0) := (0 => B);
   begin
      if Valid then
         if Attest.SHA256.Absorbed (C) < Attest.SHA256.Max_Message_Bytes
         then Attest.SHA256.Update (C, One); else Valid := False; end if;
      end if;
   end Feed;
   procedure Feed_String (C : in out Attest.SHA256.Context; S : String;
      Valid : in out Boolean) is
   begin
      for J in S'Range loop Feed (C, Character'Pos (S (J)), Valid); end loop;
   end Feed_String;
   function UTF8_Valid (A : E.Byte_Array; S : E.Identity_Span) return Boolean is
      Offset : E.Byte_Count := 0;
      N : E.Byte_Count;
      B, Low, High : Interfaces.Unsigned_8;
   begin
      -- RFC 3629 section 4 byte grammar; reject overlong and surrogate encodings.
      while Offset < S.Length loop
         B := A (S.First + Offset); Low := 16#80#; High := 16#BF#;
         if B <= 16#7F# then N := 1;
         elsif B in 16#C2# .. 16#DF# then N := 2;
         elsif B = 16#E0# then N := 3; Low := 16#A0#;
         elsif B in 16#E1# .. 16#EC# or else B in 16#EE# .. 16#EF# then N := 3;
         elsif B = 16#ED# then N := 3; High := 16#9F#;
         elsif B = 16#F0# then N := 4; Low := 16#90#;
         elsif B in 16#F1# .. 16#F3# then N := 4;
         elsif B = 16#F4# then N := 4; High := 16#8F#;
         else return False; end if;
         if N > S.Length - Offset then return False; end if;
         if N > 1 then
            if A (S.First + Offset + 1) not in Low .. High then return False; end if;
            for J in E.Byte_Count range 2 .. N - 1 loop
               if A (S.First + Offset + J) not in 16#80# .. 16#BF# then return False; end if;
            end loop;
         end if;
         Offset := Offset + N;
         pragma Loop_Invariant (Offset <= S.Length);
         pragma Loop_Variant (Decreases => S.Length - Offset);
      end loop;
      return True;
   end UTF8_Valid;
   procedure Quoted (C : in out Attest.SHA256.Context; A : E.Byte_Array;
      S : E.Identity_Span; Valid : in out Boolean) is
      B : Interfaces.Unsigned_8;
   begin
      Feed (C, Character'Pos ('"'), Valid);
      if S.Length > 0 then
         for J in E.Byte_Count range 0 .. S.Length - 1 loop
            B := A (S.First + J);
            if B = Character'Pos ('"') or else B = Character'Pos ('\') then
               Feed (C, Character'Pos ('\'), Valid); Feed (C, B, Valid);
            elsif B = 8 then Feed_String (C, "\b", Valid);
            elsif B = 9 then Feed_String (C, "\t", Valid);
            elsif B = 10 then Feed_String (C, "\n", Valid);
            elsif B = 12 then Feed_String (C, "\f", Valid);
            elsif B = 13 then Feed_String (C, "\r", Valid);
            elsif B < 16#20# then
               Feed_String (C, "\u00", Valid);
               Feed (C, Character'Pos (Hex (Integer (B / 16) + 1)), Valid);
               Feed (C, Character'Pos (Hex (Integer (B mod 16) + 1)), Valid);
            else Feed (C, B, Valid); end if;
         end loop;
      end if;
      Feed (C, Character'Pos ('"'), Valid);
   end Quoted;
   function Reference (A : E.Byte_Array; Subject : K.Optional_Identity;
      Checkpoint : Boolean) return I.Optional_Subject_Id is
      C : Attest.SHA256.Context := Attest.SHA256.Initial;
      Return_C : Attest.SHA256.Context := Attest.SHA256.Initial;
      Valid : Boolean := True;
      Return_Digest : Hash := Zero_Hash;
   begin
      if not K.Present (A, Subject) or else Subject.Value.Length = 0
        or else not UTF8_Valid (A, Subject.Value) then return (Present => False, Value => (others => 0)); end if;
      if Checkpoint then
         Feed_String (Return_C, "worldline-return-v1", Valid);
         for J in E.Byte_Count range 0 .. Subject.Value.Length - 1 loop
            if A (Subject.Value.First + J) > 16#7F# then return (Present => False, Value => (others => 0)); end if;
            Feed (Return_C, A (Subject.Value.First + J), Valid);
         end loop;
         if not Valid then return (Present => False, Value => (others => 0)); end if;
         Return_Digest := Attest.SHA256.Final (Return_C);
      end if;
      Feed_String (C, "worldline-subject-v1", Valid); Feed (C, Character'Pos ('['), Valid);
      Quoted (C, A, Subject.Value, Valid); Feed_String (C, ",""", Valid);
      if Checkpoint then
         Feed_String (C, "sha256:", Valid);
         for J in Return_Digest'Range loop
            Feed (C, Character'Pos (Hex (Integer (Return_Digest (J) / 16) + 1)), Valid);
            Feed (C, Character'Pos (Hex (Integer (Return_Digest (J) mod 16) + 1)), Valid);
         end loop;
      end if;
      Feed_String (C, """]", Valid);
      if not Valid then return (Present => False, Value => (others => 0)); end if;
      return (Present => True, Value => I.Subject_Id (Attest.SHA256.Final (C)));
   end Reference;
   function Project (A : E.Byte_Array; Subject : K.Optional_Identity;
      Checkpoint : Boolean) return I.Optional_Subject_Id is
   begin return Reference (A, Subject, Checkpoint); end Project;
end Worldline.Owner_Subject_Projection;
