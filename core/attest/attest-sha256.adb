package body Attest.SHA256 with SPARK_Mode is

   type Schedule is array (0 .. 63) of Unsigned_32;

   K : constant Schedule :=
     [16#428a2f98#, 16#71374491#, 16#b5c0fbcf#, 16#e9b5dba5#,
      16#3956c25b#, 16#59f111f1#, 16#923f82a4#, 16#ab1c5ed5#,
      16#d807aa98#, 16#12835b01#, 16#243185be#, 16#550c7dc3#,
      16#72be5d74#, 16#80deb1fe#, 16#9bdc06a7#, 16#c19bf174#,
      16#e49b69c1#, 16#efbe4786#, 16#0fc19dc6#, 16#240ca1cc#,
      16#2de92c6f#, 16#4a7484aa#, 16#5cb0a9dc#, 16#76f988da#,
      16#983e5152#, 16#a831c66d#, 16#b00327c8#, 16#bf597fc7#,
      16#c6e00bf3#, 16#d5a79147#, 16#06ca6351#, 16#14292967#,
      16#27b70a85#, 16#2e1b2138#, 16#4d2c6dfc#, 16#53380d13#,
      16#650a7354#, 16#766a0abb#, 16#81c2c92e#, 16#92722c85#,
      16#a2bfe8a1#, 16#a81a664b#, 16#c24b8b70#, 16#c76c51a3#,
      16#d192e819#, 16#d6990624#, 16#f40e3585#, 16#106aa070#,
      16#19a4c116#, 16#1e376c08#, 16#2748774c#, 16#34b0bcb5#,
      16#391c0cb3#, 16#4ed8aa4a#, 16#5b9cca4f#, 16#682e6ff3#,
      16#748f82ee#, 16#78a5636f#, 16#84c87814#, 16#8cc70208#,
      16#90befffa#, 16#a4506ceb#, 16#bef9a3f7#, 16#c67178f2#];

   Init_State : constant State :=
     [16#6a09e667#, 16#bb67ae85#, 16#3c6ef372#, 16#a54ff53a#,
      16#510e527f#, 16#9b05688c#, 16#1f83d9ab#, 16#5be0cd19#];

   function Ch (X, Y, Z : Unsigned_32) return Unsigned_32 is
     ((X and Y) xor ((not X) and Z));

   function Maj (X, Y, Z : Unsigned_32) return Unsigned_32 is
     ((X and Y) xor (X and Z) xor (Y and Z));

   function Sigma0 (X : Unsigned_32) return Unsigned_32 is
     (Rotate_Right (X, 2) xor Rotate_Right (X, 13) xor Rotate_Right (X, 22));

   function Sigma1 (X : Unsigned_32) return Unsigned_32 is
     (Rotate_Right (X, 6) xor Rotate_Right (X, 11) xor Rotate_Right (X, 25));

   function Theta0 (X : Unsigned_32) return Unsigned_32 is
     (Rotate_Right (X, 7) xor Rotate_Right (X, 18) xor Shift_Right (X, 3));

   function Theta1 (X : Unsigned_32) return Unsigned_32 is
     (Rotate_Right (X, 17) xor Rotate_Right (X, 19) xor Shift_Right (X, 10));

   function Low_Byte (X : Unsigned_32; Shift : Natural) return Byte is
     (Byte (Shift_Right (X, Shift) and 16#FF#))
     with Pre => Shift in 0 | 8 | 16 | 24;

   ----------------
   -- Compress --
   ----------------

   procedure Compress (H : in out State; B : Block) is
      W : Schedule := [others => 0];
      A, Bb, Cc, D, E, F, G, Hh, T1, T2 : Unsigned_32;
   begin
      for I in 0 .. 15 loop
         W (I) := Shift_Left (Unsigned_32 (B (4 * I)),     24) or
                  Shift_Left (Unsigned_32 (B (4 * I + 1)), 16) or
                  Shift_Left (Unsigned_32 (B (4 * I + 2)),  8) or
                              Unsigned_32 (B (4 * I + 3));
      end loop;

      for I in 16 .. 63 loop
         W (I) := Theta1 (W (I - 2)) + W (I - 7) +
                  Theta0 (W (I - 15)) + W (I - 16);
      end loop;

      A  := H (0); Bb := H (1); Cc := H (2); D  := H (3);
      E  := H (4); F  := H (5); G  := H (6); Hh := H (7);

      for I in Schedule'Range loop
         T1 := Hh + Sigma1 (E) + Ch (E, F, G) + K (I) + W (I);
         T2 := Sigma0 (A) + Maj (A, Bb, Cc);
         Hh := G;  G := F;  F := E;  E := D + T1;
         D  := Cc; Cc := Bb; Bb := A; A := T1 + T2;
      end loop;

      H (0) := H (0) + A;  H (1) := H (1) + Bb;
      H (2) := H (2) + Cc; H (3) := H (3) + D;
      H (4) := H (4) + E;  H (5) := H (5) + F;
      H (6) := H (6) + G;  H (7) := H (7) + Hh;
   end Compress;

   -------------
   -- Initial --
   -------------

   function Initial return Context is
     (H => Init_State, Buf => [others => 0], Fill => 0, Count => 0);

   ------------
   -- Update --
   ------------

   procedure Update (C : in out Context; Input : Byte_Array) is
   begin
      for I in Input'Range loop
         pragma Loop_Invariant (C.Count = C.Count'Loop_Entry);

         --  Fill is kept strictly below Block_Bytes at every step: the block
         --  that would complete it is consumed in the same iteration.
         if C.Fill = Block_Bytes - 1 then
            C.Buf (Block_Bytes - 1) := Input (I);
            Compress (C.H, C.Buf);
            C.Fill := 0;
         else
            C.Buf (C.Fill) := Input (I);
            C.Fill := C.Fill + 1;
         end if;
      end loop;

      C.Count := C.Count + Unsigned_64 (Input'Length);
   end Update;

   -----------
   -- Final --
   -----------

   function Final (C : Context) return Digest is
      W    : Context             := C;
      Bits : constant Unsigned_64 := Shift_Left (C.Count, 3);
      L    : Natural              := C.Fill;
      D    : Digest               := [others => 0];
   begin
      --  Mandatory 1 bit, then zeroes, then the 64-bit length.
      W.Buf (L) := 16#80#;
      L := L + 1;

      if L > Block_Bytes - 8 then
         while L < Block_Bytes loop
            pragma Loop_Invariant (L in Block_Bytes - 7 .. Block_Bytes);
            pragma Loop_Variant (Increases => L);
            W.Buf (L) := 0;
            L := L + 1;
         end loop;
         Compress (W.H, W.Buf);
         L := 0;
      end if;

      while L < Block_Bytes - 8 loop
         pragma Loop_Invariant (L in 0 .. Block_Bytes - 8);
         pragma Loop_Variant (Increases => L);
         W.Buf (L) := 0;
         L := L + 1;
      end loop;

      for J in 0 .. 7 loop
         W.Buf (Block_Bytes - 8 + J) :=
           Byte (Shift_Right (Bits, 8 * (7 - J)) and 16#FF#);
      end loop;

      Compress (W.H, W.Buf);

      for I in State_Index loop
         D (4 * I)     := Low_Byte (W.H (I), 24);
         D (4 * I + 1) := Low_Byte (W.H (I), 16);
         D (4 * I + 2) := Low_Byte (W.H (I), 8);
         D (4 * I + 3) := Low_Byte (W.H (I), 0);
      end loop;

      return D;
   end Final;

   ----------
   -- Hash --
   ----------

   function Hash (Input : Byte_Array) return Digest is
      C : Context := Initial;
   begin
      Update (C, Input);
      return Final (C);
   end Hash;

end Attest.SHA256;
