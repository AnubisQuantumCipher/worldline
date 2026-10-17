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

   procedure Round
     (A, Bb, Cc, D, E, F, G, Hh : in out Unsigned_32;
      Word, Key_Word : Unsigned_32)
     with Global => null, Always_Terminates,
       Post => Hh = G'Old and then G = F'Old and then F = E'Old
         and then E = D'Old + (((Hh'Old + Sigma1 (E'Old)) + Ch (E'Old, F'Old, G'Old)) + Key_Word) + Word
         and then D = Cc'Old and then Cc = Bb'Old and then Bb = A'Old
         and then A = ((((Hh'Old + Sigma1 (E'Old)) + Ch (E'Old, F'Old, G'Old)) + Key_Word) + Word)
           + (Sigma0 (A'Old) + Maj (A'Old, Bb'Old, Cc'Old))
   is
      T1 : constant Unsigned_32 :=
        (((Hh + Sigma1 (E)) + Ch (E, F, G)) + Key_Word) + Word;
      T2 : constant Unsigned_32 := Sigma0 (A) + Maj (A, Bb, Cc);
   begin
      Hh := G; G := F; F := E; E := D + T1;
      D := Cc; Cc := Bb; Bb := A; A := T1 + T2;
   end Round;

   type Octet is record
      W0, W1, W2, W3, W4, W5, W6, W7 : Unsigned_32;
   end record;
   type Schedule_Words is record
      P0, P1, P2, P3, P4, P5, P6, P7 : Octet;
   end record;
   type Block_Record is record
      B00, B01, B02, B03, B04, B05, B06, B07,
      B08, B09, B10, B11, B12, B13, B14, B15,
      B16, B17, B18, B19, B20, B21, B22, B23,
      B24, B25, B26, B27, B28, B29, B30, B31,
      B32, B33, B34, B35, B36, B37, B38, B39,
      B40, B41, B42, B43, B44, B45, B46, B47,
      B48, B49, B50, B51, B52, B53, B54, B55,
      B56, B57, B58, B59, B60, B61, B62, B63 : Byte;
   end record;
   function To_Octet (H : State) return Octet is
     (W0 => H (0), W1 => H (1), W2 => H (2), W3 => H (3), W4 => H (4), W5 => H (5), W6 => H (6), W7 => H (7));
   function From_Octet (P : Octet) return State is
     (0 => P.W0, 1 => P.W1, 2 => P.W2, 3 => P.W3, 4 => P.W4, 5 => P.W5, 6 => P.W6, 7 => P.W7);
   function To_Block (B : Block) return Block_Record is
     (B00 => B (0),
      B01 => B (1),
      B02 => B (2),
      B03 => B (3),
      B04 => B (4),
      B05 => B (5),
      B06 => B (6),
      B07 => B (7),
      B08 => B (8),
      B09 => B (9),
      B10 => B (10),
      B11 => B (11),
      B12 => B (12),
      B13 => B (13),
      B14 => B (14),
      B15 => B (15),
      B16 => B (16),
      B17 => B (17),
      B18 => B (18),
      B19 => B (19),
      B20 => B (20),
      B21 => B (21),
      B22 => B (22),
      B23 => B (23),
      B24 => B (24),
      B25 => B (25),
      B26 => B (26),
      B27 => B (27),
      B28 => B (28),
      B29 => B (29),
      B30 => B (30),
      B31 => B (31),
      B32 => B (32),
      B33 => B (33),
      B34 => B (34),
      B35 => B (35),
      B36 => B (36),
      B37 => B (37),
      B38 => B (38),
      B39 => B (39),
      B40 => B (40),
      B41 => B (41),
      B42 => B (42),
      B43 => B (43),
      B44 => B (44),
      B45 => B (45),
      B46 => B (46),
      B47 => B (47),
      B48 => B (48),
      B49 => B (49),
      B50 => B (50),
      B51 => B (51),
      B52 => B (52),
      B53 => B (53),
      B54 => B (54),
      B55 => B (55),
      B56 => B (56),
      B57 => B (57),
      B58 => B (58),
      B59 => B (59),
      B60 => B (60),
      B61 => B (61),
      B62 => B (62),
      B63 => B (63));
   function To_Words (W : Schedule) return Schedule_Words is
     (P0 => (W0 => W (0), W1 => W (1), W2 => W (2), W3 => W (3),
             W4 => W (4), W5 => W (5), W6 => W (6), W7 => W (7)),
      P1 => (W0 => W (8), W1 => W (9), W2 => W (10), W3 => W (11),
             W4 => W (12), W5 => W (13), W6 => W (14), W7 => W (15)),
      P2 => (W0 => W (16), W1 => W (17), W2 => W (18), W3 => W (19),
             W4 => W (20), W5 => W (21), W6 => W (22), W7 => W (23)),
      P3 => (W0 => W (24), W1 => W (25), W2 => W (26), W3 => W (27),
             W4 => W (28), W5 => W (29), W6 => W (30), W7 => W (31)),
      P4 => (W0 => W (32), W1 => W (33), W2 => W (34), W3 => W (35),
             W4 => W (36), W5 => W (37), W6 => W (38), W7 => W (39)),
      P5 => (W0 => W (40), W1 => W (41), W2 => W (42), W3 => W (43),
             W4 => W (44), W5 => W (45), W6 => W (46), W7 => W (47)),
      P6 => (W0 => W (48), W1 => W (49), W2 => W (50), W3 => W (51),
             W4 => W (52), W5 => W (53), W6 => W (54), W7 => W (55)),
      P7 => (W0 => W (56), W1 => W (57), W2 => W (58), W3 => W (59),
             W4 => W (60), W5 => W (61), W6 => W (62), W7 => W (63)));
   function Word_At (W : Schedule_Words; I : Natural) return Unsigned_32 is
      Group : constant Octet := (case I / 8 is
         when 0 => W.P0,
         when 1 => W.P1,
         when 2 => W.P2,
         when 3 => W.P3,
         when 4 => W.P4,
         when 5 => W.P5,
         when 6 => W.P6,
         when 7 => W.P7,
         when others => W.P0);
      Slot : constant Natural := I mod 8;
   begin
      return (case Slot is
         when 0 => Group.W0,
         when 1 => Group.W1,
         when 2 => Group.W2,
         when 3 => Group.W3,
         when 4 => Group.W4,
         when 5 => Group.W5,
         when 6 => Group.W6,
         when 7 => Group.W7,
         when others => 0);
   end Word_At;
   function Schedule_From (B : Block_Record) return Schedule_Words is
      Raw : Block := [others => 0];
      W : Schedule := [others => 0];
   begin
      Raw (0) := B.B00;
      Raw (1) := B.B01;
      Raw (2) := B.B02;
      Raw (3) := B.B03;
      Raw (4) := B.B04;
      Raw (5) := B.B05;
      Raw (6) := B.B06;
      Raw (7) := B.B07;
      Raw (8) := B.B08;
      Raw (9) := B.B09;
      Raw (10) := B.B10;
      Raw (11) := B.B11;
      Raw (12) := B.B12;
      Raw (13) := B.B13;
      Raw (14) := B.B14;
      Raw (15) := B.B15;
      Raw (16) := B.B16;
      Raw (17) := B.B17;
      Raw (18) := B.B18;
      Raw (19) := B.B19;
      Raw (20) := B.B20;
      Raw (21) := B.B21;
      Raw (22) := B.B22;
      Raw (23) := B.B23;
      Raw (24) := B.B24;
      Raw (25) := B.B25;
      Raw (26) := B.B26;
      Raw (27) := B.B27;
      Raw (28) := B.B28;
      Raw (29) := B.B29;
      Raw (30) := B.B30;
      Raw (31) := B.B31;
      Raw (32) := B.B32;
      Raw (33) := B.B33;
      Raw (34) := B.B34;
      Raw (35) := B.B35;
      Raw (36) := B.B36;
      Raw (37) := B.B37;
      Raw (38) := B.B38;
      Raw (39) := B.B39;
      Raw (40) := B.B40;
      Raw (41) := B.B41;
      Raw (42) := B.B42;
      Raw (43) := B.B43;
      Raw (44) := B.B44;
      Raw (45) := B.B45;
      Raw (46) := B.B46;
      Raw (47) := B.B47;
      Raw (48) := B.B48;
      Raw (49) := B.B49;
      Raw (50) := B.B50;
      Raw (51) := B.B51;
      Raw (52) := B.B52;
      Raw (53) := B.B53;
      Raw (54) := B.B54;
      Raw (55) := B.B55;
      Raw (56) := B.B56;
      Raw (57) := B.B57;
      Raw (58) := B.B58;
      Raw (59) := B.B59;
      Raw (60) := B.B60;
      Raw (61) := B.B61;
      Raw (62) := B.B62;
      Raw (63) := B.B63;
      for I in 0 .. 15 loop
         W (I) := Shift_Left (Unsigned_32 (Raw (4 * I)), 24) or
           Shift_Left (Unsigned_32 (Raw (4 * I + 1)), 16) or
           Shift_Left (Unsigned_32 (Raw (4 * I + 2)), 8) or
           Unsigned_32 (Raw (4 * I + 3));
      end loop;
      for I in 16 .. Schedule'Last loop
         W (I) := ((Theta1 (W (I - 2)) + W (I - 7)) + Theta0 (W (I - 15))) + W (I - 16);
      end loop;
      return To_Words (W);
   end Schedule_From;
   function Mix (H : Octet; W : Schedule_Words) return Octet is
      A : Unsigned_32 := H.W0;
      Bb : Unsigned_32 := H.W1;
      Cc : Unsigned_32 := H.W2;
      D : Unsigned_32 := H.W3;
      E : Unsigned_32 := H.W4;
      F : Unsigned_32 := H.W5;
      G : Unsigned_32 := H.W6;
      Hh : Unsigned_32 := H.W7;
   begin
      for I in 0 .. 63 loop
         Round (A, Bb, Cc, D, E, F, G, Hh, Word_At (W, I), K (I));
      end loop;
      --  Feed the round result forward into the incoming chaining state.
      return (W0 => H.W0 + A, W1 => H.W1 + Bb,
              W2 => H.W2 + Cc, W3 => H.W3 + D,
              W4 => H.W4 + E, W5 => H.W5 + F,
              W6 => H.W6 + G, W7 => H.W7 + Hh);
   end Mix;
   --  The expression supplies the exact defining equation without a duplicate
   --  checked evaluation of the schedule and rounds.
   function Applied (H : State; B : Block) return State is
     (From_Octet (Mix (To_Octet (H), Schedule_From (To_Block (B)))))
     with Global => null;

   procedure Compress (H : in out State; B : Block)
     with Global => null,
          Depends => (H => (H, B)),
          Post => H = Applied (H'Old, B),
          Always_Terminates
   is
   begin
      H := Applied (H, B);
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

      declare
         J : Natural := 0;
      begin
         while J <= 7 loop
            pragma Loop_Invariant (J in 0 .. 7 + 1);
            pragma Loop_Variant (Increases => J);
            W.Buf (Block_Bytes - 8 + J) :=
              Byte (Shift_Right (Bits, 8 * (7 - J)) and 16#FF#);
            J := J + 1;
         end loop;
      end;

      Compress (W.H, W.Buf);

      declare
         I : Natural := State_Index'First;
      begin
         while I <= State_Index'Last loop
            pragma Loop_Invariant
              (I in State_Index'First .. State_Index'Last + 1);
            pragma Loop_Variant (Increases => I);
            D (4 * I)     := Low_Byte (W.H (I), 24);
            D (4 * I + 1) := Low_Byte (W.H (I), 16);
            D (4 * I + 2) := Low_Byte (W.H (I), 8);
            D (4 * I + 3) := Low_Byte (W.H (I), 0);
            I := I + 1;
         end loop;
      end;

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

   function Receipt_Link_Digest (Previous, Root : Digest_Record) return Digest is
      Domain : constant Byte_Array :=
        [Byte (Character'Pos ('w')), Byte (Character'Pos ('o')),
         Byte (Character'Pos ('r')), Byte (Character'Pos ('l')),
         Byte (Character'Pos ('d')), Byte (Character'Pos ('l')),
         Byte (Character'Pos ('i')), Byte (Character'Pos ('n')),
         Byte (Character'Pos ('e')), Byte (Character'Pos ('-')),
         Byte (Character'Pos ('r')), Byte (Character'Pos ('e')),
         Byte (Character'Pos ('c')), Byte (Character'Pos ('e')),
         Byte (Character'Pos ('i')), Byte (Character'Pos ('p')),
         Byte (Character'Pos ('t')), Byte (Character'Pos ('-')),
         Byte (Character'Pos ('v')), Byte (Character'Pos ('1'))];
      C : Context := Initial;
   begin
      Update (C, Domain);
      Update (C, From_Digest_Bytes (Previous));
      Update (C, From_Digest_Bytes (Root));
      return Final (C);
   end Receipt_Link_Digest;
   function Causal_Link_Digest (Previous, Root : Digest_Record) return Digest is
      Domain : constant Byte_Array :=
        [Byte (Character'Pos ('w')), Byte (Character'Pos ('o')),
         Byte (Character'Pos ('r')), Byte (Character'Pos ('l')),
         Byte (Character'Pos ('d')), Byte (Character'Pos ('l')),
         Byte (Character'Pos ('i')), Byte (Character'Pos ('n')),
         Byte (Character'Pos ('e')), Byte (Character'Pos ('-')),
         Byte (Character'Pos ('c')), Byte (Character'Pos ('a')),
         Byte (Character'Pos ('u')), Byte (Character'Pos ('s')),
         Byte (Character'Pos ('a')), Byte (Character'Pos ('l')),
         Byte (Character'Pos ('-')), Byte (Character'Pos ('v')),
         Byte (Character'Pos ('1'))];
      C : Context := Initial;
   begin
      Update (C, Domain);
      Update (C, From_Digest_Bytes (Previous));
      Update (C, From_Digest_Bytes (Root));
      return Final (C);
   end Causal_Link_Digest;








end Attest.SHA256;
