with Worldline.Scoped_Archive;
with Worldline.Archive_Text;
with Attest.SHA256;
with Interfaces;
with SPARK.Big_Integers;
with Exact_Decimal;
with Decimal_Binary64;

package body Canonical_Artifacts with SPARK_Mode is
   use type Interfaces.Unsigned_64;
   use SPARK.Big_Integers;
   package SHA renames Attest.SHA256;
   subtype U64 is Interfaces.Unsigned_64;

   function Byte_At (A : Bytes; S : Span; O : Count) return Natural is
     (if P.Valid (A, S) and then O < S.Length
      then Natural (A (S.First + O)) else 0)
     with Global => null,
       Post => Byte_At'Result <= Natural (P.Byte'Last);
   function Match (A : Bytes; S : Span; O : Count; Text : String)
      return Boolean is
     (P.Valid (A, S) and then O <= S.Length
      and then Text'Length <= S.Length - O
      and then (for all K in Text'Range =>
        Byte_At (A, S, O + Count (K - Text'First)) = Character'Pos (Text (K))))
     with Global => null,
       Post => (if Match'Result then P.Valid (A, S) and then
         O <= S.Length and then Text'Length <= S.Length - O);
   function Part (Whole : Span; First, After : Count) return Span is
   begin
      if First > After or else After > Whole.Length or else First = After then
         return (1, 0);
      elsif First > Count'Last - Whole.First then
         -- Invalid whole spans cannot force arithmetic before validation.
         return (1, After - First);
      end if;
      return (Whole.First + First, After - First);
   end Part;
   function Hex (C : Natural) return Integer is
     (if C in Character'Pos ('0') .. Character'Pos ('9') then C - Character'Pos ('0')
      elsif C in Character'Pos ('a') .. Character'Pos ('f') then C - Character'Pos ('a') + 10
      else -1);
   type Scalar is record
      Valid : Boolean := False;
      Code : Natural := 0;
      After : Count := 0;
   end record;
   No_Scalar : constant Scalar := (False, 0, 0);
   function Character_At (A : Bytes; S : Span; O : Count) return Scalar
     with Global => null,
       Post => (if Character_At'Result.Valid then P.Valid (A, S)
         and then O < Character_At'Result.After
         and then Character_At'Result.After <= S.Length)
   is
      B, C, D, E, Value : Natural;
      Size : Count;
   begin
      if not P.Valid (A, S) or else O >= S.Length then return No_Scalar; end if;
      B := Byte_At (A, S, O);
      if B < 16#20# or else B = Character'Pos ('"') then return No_Scalar; end if;
      if B = Character'Pos ('\') then
         if S.Length - O < 2 then return No_Scalar; end if;
         C := Byte_At (A, S, O + 1);
         case C is
            when Character'Pos ('"') | Character'Pos ('\') => Value := C;
            when Character'Pos ('b') => Value := 8;
            when Character'Pos ('t') => Value := 9;
            when Character'Pos ('n') => Value := 10;
            when Character'Pos ('f') => Value := 12;
            when Character'Pos ('r') => Value := 13;
            when Character'Pos ('u') =>
               if S.Length - O < 6 or else not Match (A, S, O + 2, "00")
                 or else Hex (Byte_At (A, S, O + 4)) < 0
                 or else Hex (Byte_At (A, S, O + 5)) < 0
               then return No_Scalar; end if;
               Value := Natural (Hex (Byte_At (A, S, O + 4))) * 16
                 + Natural (Hex (Byte_At (A, S, O + 5)));
               if Value >= 16#20# or else Value in 8 | 9 | 10 | 12 | 13
               then return No_Scalar; end if;
               return (True, Value, O + 6);
            when others => return No_Scalar;
         end case;
         return (True, Value, O + 2);
      elsif B < 16#80# then
         return (True, B, O + 1);
      elsif B in 16#C2# .. 16#DF# then Size := 2;
      elsif B in 16#E0# .. 16#EF# then Size := 3;
      elsif B in 16#F0# .. 16#F4# then Size := 4;
      else return No_Scalar;
      end if;
      if S.Length - O < Size then return No_Scalar; end if;
      C := Byte_At (A, S, O + 1);
      if C not in 16#80# .. 16#BF# then return No_Scalar; end if;
      if Size = 2 then return (True, (B - 16#C0#) * 64 + C - 16#80#, O + 2); end if;
      D := Byte_At (A, S, O + 2);
      if D not in 16#80# .. 16#BF#
        or else (B = 16#E0# and then C < 16#A0#)
        or else (B = 16#ED# and then C >= 16#A0#)
        or else (B = 16#F0# and then C < 16#90#)
        or else (B = 16#F4# and then C >= 16#90#)
      then return No_Scalar; end if;
      if Size = 3 then
         return (True, ((B - 16#E0#) * 64 + C - 16#80#) * 64 + D - 16#80#, O + 3);
      end if;
      E := Byte_At (A, S, O + 3);
      if E not in 16#80# .. 16#BF# then return No_Scalar; end if;
      Value := (((B - 16#F0#) * 64 + C - 16#80#) * 64 + D - 16#80#) * 64 + E - 16#80#;
      return (True, Value, O + 4);
   end Character_At;

   function String_Node (A : Bytes; S : Span; From : Count) return Node
     with Global => null,
       Post => (if String_Node'Result.Valid then P.Valid (A, S)
         and then String_Node'Result.First = From
         and then From < String_Node'Result.After
         and then String_Node'Result.After <= S.Length
         and then String_Node'Result.Form = String_Value)
   is
      O : Count := From;
      C : Scalar;
   begin
      if not P.Valid (A, S) or else From >= S.Length
        or else Byte_At (A, S, From) /= Character'Pos ('"') then return No_Node; end if;
      O := O + 1;
      while O < S.Length loop
         pragma Loop_Invariant (P.Valid (A, S));
         pragma Loop_Invariant (From < O and then O <= S.Length);
         pragma Loop_Variant (Decreases => S.Length - O);
         if Byte_At (A, S, O) = Character'Pos ('"') then
            return (True, String_Value, From, O + 1);
         end if;
         C := Character_At (A, S, O);
         if not C.Valid then return No_Node; end if;
         O := C.After;
      end loop;
      return No_Node;
   end String_Node;
   function Key_Less (A : Bytes; S : Span; L, R : Node) return Boolean is
      I : Count := 0;
      J : Count := 0;
      X, Y : Scalar;
   begin
      if not P.Valid (A, S) or else not L.Valid or else not R.Valid
        or else L.Form /= String_Value or else R.Form /= String_Value
        or else L.First >= L.After or else R.First >= R.After
        or else L.After > S.Length or else R.After > S.Length
        or else L.After - L.First < 2 or else R.After - R.First < 2
      then return False; end if;
      I := L.First + 1; J := R.First + 1;
      while I < L.After - 1 and then J < R.After - 1 loop
         pragma Loop_Variant (Decreases => L.After - I);
         X := Character_At (A, S, I); Y := Character_At (A, S, J);
         if not X.Valid or else not Y.Valid then return False; end if;
         if X.Code /= Y.Code then return X.Code < Y.Code; end if;
         I := X.After; J := Y.After;
      end loop;
      return I = L.After - 1 and then J < R.After - 1;
   end Key_Less;

   --  The mode is internal: public evaluation Prefix always selects False.
   --  Genesis numbers retain the private Integer_Value node shape; the
   --  fractional/exponent syntax is distinguished before typed-tree dispatch.
   function Prefix_Of (A : Bytes; S : Span; From : Count; Genesis : Boolean)
     return Node
     with Global => null,
       Post => (if Prefix_Of'Result.Valid then
         P.Valid (A, S) and then Prefix_Of'Result.First = From
         and then From < Prefix_Of'Result.After
         and then Prefix_Of'Result.After <= S.Length
         and then Prefix_Of'Result.Form /= Invalid_Value),
       Subprogram_Variant => (Decreases => S.Length - Count'Min (From, S.Length));
   function Prefix_Of (A : Bytes; S : Span; From : Count; Genesis : Boolean)
     return Node is
      O : Count := From;
      Child, Key, Previous : Node := No_Node;
      B : Natural;
      Negative, Zero_Head : Boolean := False;
   begin
      if not P.Valid (A, S) or else From >= S.Length then return No_Node; end if;
      B := Byte_At (A, S, From);
      if B = Character'Pos ('"') then return String_Node (A, S, From);
      elsif Match (A, S, From, "null") then
         pragma Assert (From < From + 4);
         return (True, Null_Value, From, From + 4);
      elsif Match (A, S, From, "true") then
         pragma Assert (From < From + 4);
         return (True, Boolean_Value, From, From + 4);
      elsif Match (A, S, From, "false") then
         pragma Assert (From < From + 5);
         return (True, Boolean_Value, From, From + 5);
      elsif B = Character'Pos ('[') then
         O := O + 1;
         if O < S.Length and then Byte_At (A, S, O) = Character'Pos (']') then
            pragma Assert (From < O + 1);
            return (True, Array_Value, From, O + 1);
         end if;
         while O < S.Length loop
            pragma Loop_Invariant (P.Valid (A, S));
            pragma Loop_Invariant (From < O and then O <= S.Length);
            pragma Loop_Variant (Decreases => S.Length - O);
            Child := Prefix_Of (A, S, O, Genesis);
            if not Child.Valid then return No_Node; end if;
            O := Child.After;
            if O >= S.Length then return No_Node; end if;
            if Byte_At (A, S, O) = Character'Pos (']') then
               pragma Assert (From < O + 1);
               return (True, Array_Value, From, O + 1);
            elsif Byte_At (A, S, O) /= Character'Pos (',') then return No_Node;
            end if;
            O := O + 1;
         end loop;
         return No_Node;
      elsif B = Character'Pos ('{') then
         O := O + 1;
         if O < S.Length and then Byte_At (A, S, O) = Character'Pos ('}') then
            pragma Assert (From < O + 1);
            return (True, Object_Value, From, O + 1);
         end if;
         while O < S.Length loop
            pragma Loop_Invariant (P.Valid (A, S));
            pragma Loop_Invariant (From < O and then O <= S.Length);
            pragma Loop_Variant (Decreases => S.Length - O);
            Key := String_Node (A, S, O);
            if not Key.Valid or else (Previous.Valid and then not Key_Less (A, S, Previous, Key))
            then return No_Node; end if;
            Previous := Key;
            O := Key.After;
            if O >= S.Length or else Byte_At (A, S, O) /= Character'Pos (':') then return No_Node; end if;
            O := O + 1;
            Child := Prefix_Of (A, S, O, Genesis);
            if not Child.Valid then return No_Node; end if;
            O := Child.After;
            if O >= S.Length then return No_Node; end if;
            if Byte_At (A, S, O) = Character'Pos ('}') then
               pragma Assert (From < O + 1);
               return (True, Object_Value, From, O + 1);
            elsif Byte_At (A, S, O) /= Character'Pos (',') then return No_Node;
            end if;
            O := O + 1;
         end loop;
         return No_Node;
      else
         if B = Character'Pos ('-') then
            Negative := True; O := O + 1;
            if O >= S.Length then return No_Node; end if;
         end if;
         B := Byte_At (A, S, O);
         if B = Character'Pos ('0') then
            Zero_Head := True;
            O := O + 1;
         elsif B in Character'Pos ('1') .. Character'Pos ('9') then
            O := O + 1;
            while O < S.Length and then Byte_At (A, S, O) in
              Character'Pos ('0') .. Character'Pos ('9') loop
               pragma Loop_Invariant (From < O and then O <= S.Length);
               pragma Loop_Variant (Decreases => S.Length - O);
               O := O + 1;
            end loop;
         else return No_Node;
         end if;
         --  Nonfloat evaluation/genesis integers need no Big_Integer parse.
         if Genesis and then O < S.Length and then Byte_At (A, S, O) in
           Character'Pos ('.') | Character'Pos ('e') | Character'Pos ('E')
         then
            declare
               Number : constant Exact_Decimal.Number := Exact_Decimal.Parse (A, S, From);
            begin
               if not Number.Valid or else not Number.Floating then return No_Node; end if;
               declare
                  C : constant Decimal_Binary64.Conversion := Decimal_Binary64.Convert (Number);
               begin
                  if not C.Valid or else not Decimal_Binary64.Spelling_Matches
                    (A, Part (S, From, Number.After), C.Encoding) then return No_Node; end if;
               end;
               return (True, Integer_Value, From, Number.After);
            end;
         end if;
         if Negative and then Zero_Head then return No_Node; end if;
         pragma Assert (From < O);
         return (True, Integer_Value, From, O);
      end if;
   end Prefix_Of;
   function Prefix (A : Bytes; S : Span; From : Count) return Node is
     (Prefix_Of (A, S, From, False));
   function Genesis_Prefix (A : Bytes; S : Span; From : Count) return Node is
     (Prefix_Of (A, S, From, True))
     with Global => null,
       Post => (if Genesis_Prefix'Result.Valid then
         P.Valid (A, S) and then Genesis_Prefix'Result.First = From
         and then From < Genesis_Prefix'Result.After
         and then Genesis_Prefix'Result.After <= S.Length
         and then Genesis_Prefix'Result.Form /= Invalid_Value);
   function Canonical (A : Bytes; S : Span) return Boolean is
      N : constant Node := Prefix (A, S, 0);
   begin
      return N.Valid and then N.After = S.Length;
   end Canonical;
   function String_Is (A : Bytes; S : Span; N : Node; Text : String) return Boolean is
     (N.Valid and then N.Form = String_Value and then N.After > N.First
      and then N.After - N.First >= 2 and then N.After - N.First - 2 = Text'Length
      and then Match (A, S, N.First + 1, Text));
   function Field_Of (A : Bytes; S : Span; Name : String; Genesis : Boolean)
      return Member
     with Global => null,
       Post => (if Field_Of'Result.Found then
         P.Valid (A, S) and then Field_Of'Result.Value.Valid
         and then Field_Of'Result.First < Field_Of'Result.After
         and then Field_Of'Result.After <= S.Length
         and then Field_Of'Result.Value.First < Field_Of'Result.Value.After
         and then Field_Of'Result.Value.After <= S.Length);
   function Field_Of (A : Bytes; S : Span; Name : String; Genesis : Boolean)
      return Member
   is
      Whole : constant Node := Prefix_Of (A, S, 0, Genesis);
      O, First : Count;
      Key, Value : Node;
   begin
      if not Whole.Valid or else Whole.Form /= Object_Value or else Whole.After /= S.Length or else S.Length < 2
      then return No_Member; end if;
      O := 1;
      while O < S.Length - 1 loop
         pragma Loop_Invariant (O in 1 .. S.Length);
         pragma Loop_Invariant (P.Valid (A, S));
         pragma Loop_Variant (Decreases => S.Length - O);
         First := O; Key := String_Node (A, S, O);
         if not Key.Valid or else Key.After >= S.Length then return No_Member; end if;
         Value := Prefix_Of (A, S, Key.After + 1, Genesis);
         if not Value.Valid then return No_Member; end if;
         if String_Is (A, S, Key, Name) then return (True, Value, First, Value.After); end if;
         O := Value.After;
         if O < S.Length - 1 then O := O + 1; end if;
      end loop;
      return No_Member;
   end Field_Of;
   function Field (A : Bytes; S : Span; Name : String) return Member is
     (Field_Of (A, S, Name, False));
   function Canonical_JSON_Field (A : Bytes; S : Span; Name : String) return Span is
      Document : Span := S;
   begin
      if not P.Valid (A, S) then return (1, 0); end if;
      if S.Length > 0 and then Byte_At (A, S, S.Length - 1) = Character'Pos (ASCII.LF)
      then Document := Part (S, 0, S.Length - 1); end if;
      declare
         M : constant Member := Field_Of (A, Document, Name, True);
      begin
         if not M.Found then return (1, 0); end if;
         return Part (Document, M.Value.First, M.Value.After);
      end;
   end Canonical_JSON_Field;
   function JSON_Prefix (A : Bytes; S : Span; From : Count) return JSON_Node is
      N : constant Node := Genesis_Prefix (A, S, From);
      Form : JSON_Kind;
      O : Count;
   begin
      if not N.Valid then return No_JSON_Node; end if;
      case N.Form is
         when Invalid_Value => return No_JSON_Node;
         when Null_Value => Form := Null_JSON_Value;
         when Boolean_Value => Form := Boolean_JSON_Value;
         when String_Value => Form := String_JSON_Value;
         when Array_Value => Form := Array_JSON_Value;
         when Object_Value => Form := Object_JSON_Value;
         when Integer_Value =>
            Form := Integer_JSON_Value;
            O := N.First;
            while O < N.After loop
               pragma Loop_Invariant (O in N.First .. N.After);
               pragma Loop_Variant (Decreases => N.After - O);
               if Byte_At (A, S, O) in Character'Pos ('.') | Character'Pos ('e') |
                 Character'Pos ('E')
               then Form := Float_JSON_Value; exit; end if;
               O := O + 1;
            end loop;
      end case;
      return (True, Form, N.First, N.After);
   end JSON_Prefix;
   function Canonical_JSON_Valid (A : Bytes; S : Span) return Boolean is
      N : constant JSON_Node := JSON_Prefix (A, S, 0);
   begin
      if not N.Valid then return False; end if;
      return N.After = S.Length or else
        (N.After < S.Length and then S.Length - N.After = 1 and then
         Byte_At (A, S, N.After) = Character'Pos (ASCII.LF));
   end Canonical_JSON_Valid;
   function Root_Matches (A : Bytes; S : Span; Digest : Worldline.Hash) return Boolean is
      N : constant Node := Prefix (A, S, 0);
      Tag : constant String := "sha256:";
      Hexes : constant String := "0123456789abcdef";
      O : Count;
   begin
      if not N.Valid or else N.Form /= String_Value or else N.After /= S.Length
        or else S.Length /= Tag'Length + Digest'Length * 2 + 2
        or else not Match (A, S, 1, Tag)
      then return False; end if;
      O := 1 + Tag'Length;
      for K in Digest'Range loop
         if Byte_At (A, S, O) /= Character'Pos (Hexes (Integer (Digest (K)) / 16 + Hexes'First))
           or else Byte_At (A, S, O + 1) /= Character'Pos (Hexes (Integer (Digest (K)) mod 16 + Hexes'First))
         then return False; end if;
         O := O + 2;
      end loop;
      return True;
   end Root_Matches;

   function B64_Digit (C : Natural) return Integer is
     (if C in Character'Pos ('A') .. Character'Pos ('Z') then C - Character'Pos ('A')
      elsif C in Character'Pos ('a') .. Character'Pos ('z') then C - Character'Pos ('a') + 26
      elsif C in Character'Pos ('0') .. Character'Pos ('9') then C - Character'Pos ('0') + 52
      elsif C = Character'Pos ('+') then 62
      elsif C = Character'Pos ('/') then 63 else -1);
   type Binary_String is record
      Valid : Boolean := False;
      First, Length : Count := 0;
   end record;
   No_Binary : constant Binary_String := (False, 0, 0);
   function Base64 (A : Bytes; S : Span; N : Node) return Binary_String is
      Size, Padding, O : Count := 0;
   begin
      if not P.Valid (A, S) or else not N.Valid or else N.Form /= String_Value
        or else N.First >= N.After or else N.After > S.Length
        or else N.After - N.First < 2 then return No_Binary; end if;
      Size := N.After - N.First - 2;
      if Size mod 4 /= 0 then return No_Binary; end if;
      if Size = 0 then return (True, N.First + 1, 0); end if;
      if Byte_At (A, S, N.After - 2) = Character'Pos ('=') then Padding := 1; end if;
      if Byte_At (A, S, N.After - 3) = Character'Pos ('=') then Padding := 2; end if;
      O := N.First + 1;
      while O < N.After - 1 - Padding loop
         pragma Loop_Variant (Decreases => N.After - O);
         if B64_Digit (Byte_At (A, S, O)) < 0 then return No_Binary; end if;
         O := O + 1;
      end loop;
      while O < N.After - 1 loop
         pragma Loop_Variant (Decreases => N.After - O);
         if Byte_At (A, S, O) /= Character'Pos ('=') then return No_Binary; end if;
         O := O + 1;
      end loop;
      if (Padding = 1 and then B64_Digit (Byte_At (A, S, N.After - 3)) mod 4 /= 0)
        or else (Padding = 2 and then B64_Digit (Byte_At (A, S, N.After - 4)) mod 16 /= 0)
      then return No_Binary; end if;
      return (True, N.First + 1, (Size / 4) * 3 - Padding);
   end Base64;
   function Binary_At (A : Bytes; S : Span; B : Binary_String; O : Count)
      return Natural is
      Q : Count;
      X, Y : Integer;
   begin
      if not P.Valid (A, S) or else not B.Valid or else O >= B.Length
        or else B.First > S.Length or else O / 3 > (S.Length - B.First) / 4
      then return 0; end if;
      Q := B.First + (O / 3) * 4;
      if S.Length - Q < 4 then return 0; end if;
      case O mod 3 is
         when 0 => X := B64_Digit (Byte_At (A, S, Q)); Y := B64_Digit (Byte_At (A, S, Q + 1));
            if X < 0 or else Y < 0 then return 0; end if;
            return Natural (X * 4 + Y / 16);
         when 1 => X := B64_Digit (Byte_At (A, S, Q + 1)); Y := B64_Digit (Byte_At (A, S, Q + 2));
            if X < 0 or else Y < 0 then return 0; end if;
            return Natural ((X mod 16) * 16 + Y / 4);
         when others => X := B64_Digit (Byte_At (A, S, Q + 2)); Y := B64_Digit (Byte_At (A, S, Q + 3));
            if X < 0 or else Y < 0 then return 0; end if;
            return Natural ((X mod 4) * 64 + Y);
      end case;
   end Binary_At;
   function String_Binary_Matches
     (A : Bytes; J : Span; N : Node; T : Span; B : Binary_String) return Boolean is
      O : Count := N.First;
      Position : Count := 0;
      C : Scalar;
      Length : Count;
      Octet : Natural;
   begin
      if not P.Valid (A, J) or else not N.Valid or else N.Form /= String_Value
        or else N.First >= N.After or else N.After > J.Length
        or else N.After - N.First < 2 or else not B.Valid then return False; end if;
      O := O + 1;
      while O < N.After - 1 loop
         pragma Loop_Variant (Decreases => N.After - O);
         C := Character_At (A, J, O);
         if not C.Valid then return False; end if;
         if C.Code < 16#80# then Length := 1;
         elsif C.Code < 16#800# then Length := 2;
         elsif C.Code < 16#10000# then Length := 3;
         else Length := 4; end if;
         if Position > B.Length or else Length > B.Length - Position then return False; end if;
         for K in Count range 0 .. Length - 1 loop
            if Length = 1 then Octet := C.Code;
            elsif K = 0 then
               if Length = 2 then Octet := 16#C0# + C.Code / 64;
               elsif Length = 3 then Octet := 16#E0# + C.Code / 4096;
               else Octet := 16#F0# + C.Code / 262144; end if;
            elsif K = Length - 1 then Octet := 16#80# + C.Code mod 64;
            elsif K = Length - 2 then Octet := 16#80# + (C.Code / 64) mod 64;
            else Octet := 16#80# + (C.Code / 4096) mod 64; end if;
            if Binary_At (A, T, B, Position + K) /= Octet then return False; end if;
         end loop;
         Position := Position + Length; O := C.After;
      end loop;
      return Position = B.Length;
   end String_Binary_Matches;

   -- This iterator counts/reads only the supplied array, with no fixed row
   -- bound or allocation proportional to a caller-controlled count.
   function Element (A : Bytes; S : Span; Position : Count) return Node is
      Whole : constant Node := Prefix (A, S, 0);
      O : Count := 1;
      K : Count := 0;
      N : Node;
   begin
      if not Whole.Valid or else Whole.Form /= Array_Value or else Whole.After /= S.Length or else S.Length < 2
      then return No_Node; end if;
      while O < S.Length - 1 loop
         pragma Loop_Invariant (O in 1 .. S.Length);
         pragma Loop_Invariant (K < O);
         pragma Loop_Invariant (P.Valid (A, S));
         pragma Loop_Variant (Decreases => S.Length - O);
         N := Prefix (A, S, O);
         if not N.Valid then return No_Node; end if;
         if K = Position then return N; end if;
         K := K + 1; O := N.After;
         if O < S.Length - 1 then O := O + 1; end if;
      end loop;
      return No_Node;
   end Element;
   function Elements (A : Bytes; S : Span) return Count
     with Global => null,
       Post => Elements'Result <= S.Length
   is
      Whole : constant Node := Prefix (A, S, 0);
      O : Count := 1;
      K : Count := 0;
      N : Node;
   begin
      if not Whole.Valid or else Whole.Form /= Array_Value or else Whole.After /= S.Length or else S.Length < 2
      then return 0; end if;
      while O < S.Length - 1 loop
         pragma Loop_Invariant (O in 1 .. S.Length);
         pragma Loop_Invariant (K < O);
         pragma Loop_Invariant (P.Valid (A, S));
         pragma Loop_Variant (Decreases => S.Length - O);
         N := Prefix (A, S, O);
         if not N.Valid then return 0; end if;
         K := K + 1; O := N.After;
         if O < S.Length - 1 then O := O + 1; end if;
      end loop;
      return K;
   end Elements;
   function Integer_Matches
     (A : Bytes; J : Span; N : Node; T : Span; Sign, Magnitude : Node) return Boolean is
      B : constant Binary_String := Base64 (A, T, Magnitude);
      Negative : constant Boolean := Byte_At (A, J, N.First) = Character'Pos ('-');
      O : Count := N.First;
      Decimal_Value, Binary_Value : Big_Integer := To_Big_Integer (0);
      Product, Addend : Big_Integer := To_Big_Integer (0);
   begin
      if not N.Valid or else N /= Prefix (A, J, 0) or else N.Form /= Integer_Value
        or else N.After /= J.Length or else not B.Valid
        or else not Sign.Valid or else Sign.Form /= Boolean_Value
        or else (Negative /= Match (A, T, Sign.First, "true"))
        or else (B.Length > 0 and then Binary_At (A, T, B, B.Length - 1) = 0)
        or else (Negative and then B.Length = 0)
      then return False; end if;
      if Negative then O := O + 1; end if;
      while O < N.After loop
         pragma Loop_Variant (Decreases => N.After - O);
         Product := Decimal_Value * To_Big_Integer (10);
         Addend := To_Big_Integer (Integer (Byte_At (A, J, O) - Character'Pos ('0')));
         Decimal_Value := Product + Addend;
         O := O + 1;
      end loop;
      O := B.Length;
      while O > 0 loop
         pragma Loop_Variant (Decreases => O);
         O := O - 1;
         Product := Binary_Value * To_Big_Integer (256);
         Addend := To_Big_Integer (Integer (Binary_At (A, T, B, O)));
         Binary_Value := Product + Addend;
      end loop;
      return Decimal_Value = Binary_Value;
   end Integer_Matches;

   function Tagged_Matches (A : Bytes; JSON_Value, Tagged_Value : Span) return Boolean is
      J : constant Node := Prefix (A, JSON_Value, 0);
      T : constant Node := Prefix (A, Tagged_Value, 0);
      Tag : Node;
      Value, Sign, Pair, Key, Child, Pair_Key, Pair_Value : Node;
      Data, Pair_Span : Span;
      O, Other_Offset, Position, Members, Matches, Data_Count : Count := 0;
      Binary : Binary_String;
   begin
      if not J.Valid or else J.After /= JSON_Value.Length
        or else not T.Valid or else T.Form /= Array_Value or else T.After /= Tagged_Value.Length
      then return False; end if;
      Tag := Element (A, Tagged_Value, 0);
      case J.Form is
         when Null_Value =>
            return Elements (A, Tagged_Value) = 1 and then String_Is (A, Tagged_Value, Tag, "null");
         when Boolean_Value =>
            Value := Element (A, Tagged_Value, 1);
            return Elements (A, Tagged_Value) = 2 and then String_Is (A, Tagged_Value, Tag, "bool")
              and then Value.Valid and then Value.Form = Boolean_Value
              and then P.Same (A, JSON_Value, Part (Tagged_Value, Value.First, Value.After));
         when String_Value =>
            Value := Element (A, Tagged_Value, 1);
            return Elements (A, Tagged_Value) = 2 and then String_Is (A, Tagged_Value, Tag, "str")
              and then String_Binary_Matches (A, JSON_Value, J, Tagged_Value, Base64 (A, Tagged_Value, Value));
         when Integer_Value =>
            Sign := Element (A, Tagged_Value, 1); Value := Element (A, Tagged_Value, 2);
            return Elements (A, Tagged_Value) = 3 and then String_Is (A, Tagged_Value, Tag, "int")
              and then Integer_Matches (A, JSON_Value, J, Tagged_Value, Sign, Value);
         when Array_Value =>
            Value := Element (A, Tagged_Value, 1);
            if Elements (A, Tagged_Value) /= 2 or else not String_Is (A, Tagged_Value, Tag, "array")
              or else not Value.Valid or else Value.Form /= Array_Value then return False; end if;
            Data := Part (Tagged_Value, Value.First, Value.After);
            --  A shorter payload cannot satisfy Other_Offset = Data.Length - 1:
            --  Other_Offset starts at 1 and never decreases. Refuse before the
            --  loop so the existing invariant is not a new length cap.
            if Data.Length < 2 then
               return False;
            end if;
            O := 1; Other_Offset := 1;
            while O < JSON_Value.Length - 1 loop
               pragma Loop_Invariant (JSON_Value.Length >= 2 and then Data.Length >= 2);
               pragma Loop_Invariant (O in 1 .. JSON_Value.Length);
               pragma Loop_Invariant (Other_Offset in 1 .. Data.Length);
               pragma Loop_Invariant (P.Valid (A, JSON_Value));
               pragma Loop_Variant (Decreases => JSON_Value.Length - O);
               Child := Prefix (A, JSON_Value, O); Value := Prefix (A, Data, Other_Offset);
               if not Child.Valid or else not Value.Valid or else not Tagged_Matches
                 (A, Part (JSON_Value, Child.First, Child.After), Part (Data, Value.First, Value.After))
               then return False; end if;
               O := Child.After; Other_Offset := Value.After;
               if O < JSON_Value.Length - 1 then O := O + 1; end if;
               if Other_Offset < Data.Length - 1 then Other_Offset := Other_Offset + 1; end if;
            end loop;
            return Other_Offset = Data.Length - 1;
         when Object_Value =>
            Value := Element (A, Tagged_Value, 1);
            if Elements (A, Tagged_Value) /= 2 or else not String_Is (A, Tagged_Value, Tag, "object")
              or else not Value.Valid or else Value.Form /= Array_Value then return False; end if;
            Data := Part (Tagged_Value, Value.First, Value.After);
            Data_Count := Elements (A, Data);
            if Data.Length < 2 then return False; end if;
            O := 1;
            while O < JSON_Value.Length - 1 loop
               pragma Loop_Invariant (JSON_Value.Length >= 2 and then Data.Length >= 2);
               pragma Loop_Invariant (O in 1 .. JSON_Value.Length);
               pragma Loop_Invariant (Members < O);
               pragma Loop_Invariant (Data_Count <= Data.Length);
               pragma Loop_Invariant (P.Valid (A, JSON_Value));
               pragma Loop_Variant (Decreases => JSON_Value.Length - O);
               Key := String_Node (A, JSON_Value, O);
               if not Key.Valid or else Key.After >= JSON_Value.Length then return False; end if;
               Child := Prefix (A, JSON_Value, Key.After + 1);
               if not Child.Valid then return False; end if;
               Position := 0; Matches := 0; Other_Offset := 1;
               while Position < Data_Count loop
                  pragma Loop_Invariant (Position <= Data_Count and then Data_Count <= Data.Length);
                  pragma Loop_Invariant (Matches <= Position);
                  pragma Loop_Invariant (Other_Offset in 1 .. Data.Length - 1);
                  pragma Loop_Variant (Decreases => Data_Count - Position);
                  -- Data was completely parsed above. Follow its immutable
                  -- child spans instead of revalidating/scanning the whole
                  -- array again at every indexed lookup for this JSON key.
                  Pair := Prefix (A, Data, Other_Offset);
                  if not Pair.Valid or else Pair.Form /= Array_Value
                    or else Pair.After >= Data.Length then return False; end if;
                  Pair_Span := Part (Data, Pair.First, Pair.After);
                  Pair_Key := Element (A, Pair_Span, 0); Pair_Value := Element (A, Pair_Span, 1);
                  Binary := Base64 (A, Pair_Span, Pair_Key);
                  if Elements (A, Pair_Span) /= 2 or else not Binary.Valid or else not Pair_Value.Valid
                  then return False; end if;
                  if String_Binary_Matches (A, JSON_Value, Key, Pair_Span, Binary) then
                     Matches := Matches + 1;
                     if not Tagged_Matches (A, Part (JSON_Value, Child.First, Child.After),
                        Part (Pair_Span, Pair_Value.First, Pair_Value.After)) then return False; end if;
                  end if;
                  Position := Position + 1;
                  Other_Offset := Pair.After;
                  if Position < Data_Count then
                     if Other_Offset >= Data.Length - 1
                       or else Byte_At (A, Data, Other_Offset) /= Character'Pos (',')
                     then return False; end if;
                     Other_Offset := Other_Offset + 1;
                  end if;
               end loop;
               if Matches /= 1 or else Other_Offset /= Data.Length - 1
               then return False; end if;
               Members := Members + 1; O := Child.After;
               if O < JSON_Value.Length - 1 then O := O + 1; end if;
            end loop;
            -- Every unique canonical key occurs exactly once, and there are
            -- no extra pairs. Tagged dictionary order may be arbitrary.
            return Members = Data_Count;
         when Invalid_Value => return False;
      end case;
   end Tagged_Matches;

   function Array_Payloads_Match
     (A : Bytes; JSON_Array : Span; Payloads : Span_Array) return Boolean is
      Whole : constant Node := Prefix (A, JSON_Array, 0);
      O : Count := 1;
      N : Node;
   begin
      if not Whole.Valid or else Whole.Form /= Array_Value or else Whole.After /= JSON_Array.Length or else JSON_Array.Length < 2
        or else Elements (A, JSON_Array) /= Payloads'Length then return False; end if;
      for K in Payloads'Range loop
         N := Prefix (A, JSON_Array, O);
         if not N.Valid or else not Tagged_Matches
           (A, Part (JSON_Array, N.First, N.After), Payloads (K)) then return False; end if;
         O := N.After;
         if O < JSON_Array.Length - 1 then O := O + 1; end if;
      end loop;
      return O = JSON_Array.Length - 1;
   end Array_Payloads_Match;

   function Artifact_Hash (A : Bytes; S : Span; Evidence : Boolean)
      return Hash_Result is
      Whole : constant Node := Prefix (A, S, 0);
      Tag : constant String :=
        (if Evidence then "worldline-evidence-v1" else "worldline-environment-v1");
      Root : Member;
      Skip_First, Skip_After : Count := 0;
      O : Count := 0;
      C : SHA.Context := SHA.Initial;
      Buffer : Attest.Byte_Array (0 .. SHA.Block_Bytes - 1) := (others => 0);
      Fill : Natural := 0;
      procedure Feed (Value : Natural) is
      begin
         -- Checked obligations on genuine callers, never assumed admission.
         pragma Assert (Fill < Buffer'Length);
         pragma Assert (Value <= Natural (Attest.Byte'Last));
         Buffer (Fill) := Attest.Byte (Value);
         Fill := Fill + 1;
         if Fill = Buffer'Length then
            pragma Assert
              (SHA.Absorbed (C) <= SHA.Max_Message_Bytes - U64 (Buffer'Length));
            SHA.Update (C, Buffer);
            Fill := 0;
         end if;
      end Feed;
   begin
      if not Whole.Valid or else Whole.Form /= Object_Value or else Whole.After /= S.Length or else S.Length < 2
      then return (False, Worldline.Zero_Hash); end if;
      if Evidence then
         Root := Field (A, S, "root");
         if not Root.Found or else Root.Value.Form /= String_Value then
            return (False, Worldline.Zero_Hash);
         end if;
         Skip_First := Root.First; Skip_After := Root.After;
         if Skip_First > 1 then
            -- The preceding separator belongs to this top-level member.
            Skip_First := Skip_First - 1;
         elsif Skip_After < S.Length - 1 then
            Skip_After := Skip_After + 1;
         end if;
      end if;
      -- This is the inherited SHA message-domain bound, including the exact
      -- original domain-separation tag. It is not an arena/combined-span cap.
      if U64 (S.Length - (Skip_After - Skip_First)) >
        SHA.Max_Message_Bytes - U64 (Tag'Length)
      then return (False, Worldline.Zero_Hash); end if;
      pragma Assert (Skip_First <= Skip_After and then Skip_After <= S.Length);
      for K in Tag'Range loop
         Feed (Character'Pos (Tag (K)));
         pragma Loop_Invariant (Fill < Buffer'Length);
         pragma Loop_Invariant
           (SHA.Absorbed (C) <= SHA.Max_Message_Bytes - U64 (Fill));
         pragma Loop_Invariant
           (SHA.Absorbed (C) + U64 (Fill) = U64 (K - Tag'First) + 1);
      end loop;
      while O < S.Length loop
         pragma Loop_Invariant (O <= S.Length);
         pragma Loop_Invariant (Fill < Buffer'Length);
         pragma Loop_Invariant (Skip_First <= Skip_After and then Skip_After <= S.Length);
         pragma Loop_Invariant (O <= Skip_First or else O >= Skip_After);
         pragma Loop_Invariant
           (SHA.Absorbed (C) <= SHA.Max_Message_Bytes - U64 (Fill));
         pragma Loop_Invariant
           (SHA.Absorbed (C) + U64 (Fill) = U64 (Tag'Length) +
             U64 (O - (if O >= Skip_After then Skip_After - Skip_First else 0)));
         pragma Loop_Variant (Decreases => S.Length - O);
         if O = Skip_First and then Skip_First < Skip_After then
            O := Skip_After;
         else
            Feed (Byte_At (A, S, O)); O := O + 1;
         end if;
      end loop;
      pragma Assert (Fill < Buffer'Length);
      pragma Assert (SHA.Absorbed (C) <= SHA.Max_Message_Bytes - U64 (Fill));
      if Fill > 0 then SHA.Update (C, Buffer (0 .. Fill - 1)); end if;
      return (True, SHA.Final (C));
   end Artifact_Hash;

   function Bindings
     (A : Bytes; Evidence, Environment, Context : Span;
      Payloads : Span_Array;
      Evidence_Root, Environment_Root : Worldline.Hash) return Boolean is
      Evidence_Hash : constant Hash_Result := Artifact_Hash (A, Evidence, True);
      Environment_Hash : constant Hash_Result := Artifact_Hash (A, Environment, False);
      Root : constant Member := Field (A, Evidence, "root");
      Checks : constant Member := Field (A, Evidence, "checks");
      Validation : constant Member := Field (A, Evidence, "validationContext");
      Included_Evidence : constant Member := Field (A, Environment, "evidence");
   begin
      return Evidence_Hash.Valid and then Environment_Hash.Valid
        and then Evidence_Hash.Digest = Evidence_Root
        and then Environment_Hash.Digest = Environment_Root
        and then Root.Found and then Root_Matches
          (A, Part (Evidence, Root.Value.First, Root.Value.After), Evidence_Root)
        and then Included_Evidence.Found and then P.Same
          (A, Evidence, Part (Environment, Included_Evidence.Value.First, Included_Evidence.Value.After))
        and then Checks.Found and then Array_Payloads_Match
          (A, Part (Evidence, Checks.Value.First, Checks.Value.After), Payloads)
        and then Validation.Found and then Tagged_Matches
          (A, Part (Evidence, Validation.Value.First, Validation.Value.After), Context);
   end Bindings;
   function JSON_Text_Matches
     (JSON_Data, Archive_Data : Bytes; J : Span; V : Worldline.Scoped_Archive.E.View)
     return Boolean with Global => null
   is
      package E renames Worldline.Scoped_Archive.E;
      package Text renames Worldline.Archive_Text;
      use type E.Value_Kind;
      use type Text.Decode_Status;
      N : constant Node := Prefix (JSON_Data, J, 0);
      O : Count := 1;
      B : Count := 0;
      Ch : Scalar;
   begin
      if not N.Valid or else N.Form /= String_Value or else
        N.After /= J.Length or else V.Form /= E.Text_Value or else
        not E.Bytes_Valid (Archive_Data, V.Payload) then return False; end if;
      declare
         Raw : constant Bytes := E.Materialize (Archive_Data, V.Payload);
         R : Text.Scalar_Result;
      begin
         while O < J.Length - 1 loop
            pragma Loop_Invariant (O in 1 .. J.Length - 1);
            pragma Loop_Invariant (B <= Raw'Length);
            pragma Loop_Variant (Decreases => J.Length - O);
            Ch := Character_At (JSON_Data, J, O);
            R := Text.Read (Raw, (Raw'First, Raw'Length), B);
            if not Ch.Valid or else R.Status /= Text.Decoded or else
              Ch.Code /= Natural (R.Value) then return False; end if;
            O := Ch.After;
            B := R.Next_Offset;
         end loop;
         return O = J.Length - 1 and then B = Raw'Length;
      end;
   end JSON_Text_Matches;

   function Operation_Archive_JSON_Matches
     (JSON_Data, Archive_Data : Bytes; JSON_Value, Encoded : Span) return Boolean
   is
      package O renames Worldline.Scoped_Archive.A;
      package E renames O.E;
      use type E.Value_Kind;
      function Match_Tree (J, Archive : Span) return Boolean
        with Global => (Input => (JSON_Data, Archive_Data)),
          Subprogram_Variant => (Decreases => J.Length);
      function Match_Tree (J, Archive : Span) return Boolean is
         N : constant Node := Genesis_Prefix (JSON_Data, J, 0);
         V : constant E.View := E.Decode (Archive_Data, Archive, E.Operation);
         At_JSON : Count := 1;
         Count_JSON : Count := 0;
         Children : Count;
         Child, Key : Node;
         Pair : E.View;
         Next_Value : Span;
         Found : Boolean;
      begin
         if not N.Valid or else N.After /= J.Length then return False; end if;
         case N.Form is
            when Null_Value => return V.Form = E.Null_Value;
            when Boolean_Value => return V.Form = E.Boolean_Value and then
              V.Boolean_Bit = Match (JSON_Data, J, 0, "true");
            when String_Value => return JSON_Text_Matches (JSON_Data, Archive_Data, J, V);
            when Integer_Value =>
               declare
                  Number : constant Exact_Decimal.Number := Exact_Decimal.Parse (JSON_Data, J, 0);
               begin
                  if not Number.Valid or else Number.After /= J.Length then return False; end if;
                  if Number.Floating then
                     if V.Form /= E.Float_Value or else
                       not E.Bytes_Valid (Archive_Data, V.Payload) then return False; end if;
                     declare
                        C : constant Decimal_Binary64.Conversion :=
                          Decimal_Binary64.Convert (Number);
                        Raw : constant Bytes := E.Materialize (Archive_Data, V.Payload);
                        Encoding : U64 := 0;
                     begin
                        if not C.Valid or else Raw'Length /= 8 or else
                          not Decimal_Binary64.Spelling_Matches (JSON_Data, J, C.Encoding)
                        then return False; end if;
                        for I in Raw'Range loop
                           pragma Loop_Invariant (Encoding <= 16#00FF_FFFF_FFFF_FFFF#);
                           Encoding := Encoding * 256 + U64 (Raw (I));
                        end loop;
                        return Encoding = C.Encoding;
                     end;
                  else
                     if V.Form /= E.Integer_Value or else V.Sign /= Number.Negative or else
                       not E.Bytes_Valid (Archive_Data, V.Payload) then return False; end if;
                     declare
                        Raw : constant Bytes := E.Materialize (Archive_Data, V.Payload);
                        At_Byte : Count := Raw'Length;
                        Magnitude : Big_Integer := To_Big_Integer (0);
                     begin
                        while At_Byte > 0 loop
                           pragma Loop_Invariant (At_Byte <= Raw'Length);
                           pragma Loop_Variant (Decreases => At_Byte);
                           At_Byte := At_Byte - 1;
                           Magnitude := Magnitude * To_Big_Integer (256) +
                             To_Big_Integer (Integer (Raw (Raw'First + At_Byte)));
                        end loop;
                        return Magnitude = Number.Coefficient;
                     end;
                  end if;
               end;
            when Array_Value | Object_Value =>
               if (N.Form = Array_Value and then V.Form /= E.List_Value) or else
                 (N.Form = Object_Value and then V.Form /= E.Object_Value)
               then return False; end if;
               Children := E.Array_Length (Archive_Data, V.Children);
               while At_JSON < J.Length - 1 loop
                  pragma Loop_Invariant (At_JSON in 1 .. J.Length - 1);
                  pragma Loop_Invariant (Count_JSON < At_JSON);
                  pragma Loop_Variant (Decreases => J.Length - At_JSON);
                  if N.Form = Object_Value then
                     Key := Prefix (JSON_Data, J, At_JSON);
                     if not Key.Valid or else Key.Form /= String_Value or else
                       Key.After >= J.Length then return False; end if;
                     Found := False;
                     Next_Value := (1, 0);
                     if Children > 0 then
                        for I in Count range 0 .. Children - 1 loop
                           Pair := E.Decode (Archive_Data,
                             E.Array_Element (Archive_Data, V.Children, I), E.Finalization);
                           if Pair.Form /= E.List_Value or else
                             E.Array_Length (Archive_Data, Pair.Children) /= 2
                           then return False; end if;
                           if JSON_Text_Matches (JSON_Data, Archive_Data,
                             Part (J, Key.First, Key.After),
                             E.Decode (Archive_Data,
                               E.Array_Element (Archive_Data, Pair.Children, 0), E.Operation))
                           then
                              if Found then return False; end if;
                              Found := True;
                              Next_Value := E.Array_Element (Archive_Data, Pair.Children, 1);
                           end if;
                        end loop;
                     end if;
                     if not Found then return False; end if;
                     At_JSON := Key.After + 1;
                  else
                     if Count_JSON >= Children then return False; end if;
                     Next_Value := E.Array_Element (Archive_Data, V.Children, Count_JSON);
                  end if;
                  Child := Genesis_Prefix (JSON_Data, J, At_JSON);
                  if not Child.Valid or else Child.After <= Child.First or else
                    Child.After - Child.First >= J.Length or else
                    not Match_Tree (Part (J, Child.First, Child.After), Next_Value)
                  then return False; end if;
                  At_JSON := Child.After;
                  Count_JSON := Count_JSON + 1;
                  if At_JSON < J.Length - 1 then At_JSON := At_JSON + 1; end if;
               end loop;
               return At_JSON = J.Length - 1 and then Count_JSON = Children;
            when Invalid_Value => return False;
         end case;
      end Match_Tree;
   begin
      if not P.Valid (JSON_Data, JSON_Value) or else not P.Valid (Archive_Data, Encoded) or else
        not O.Valid (Archive_Data, Encoded) then return False; end if;
      return Match_Tree (JSON_Value, Encoded);
   end Operation_Archive_JSON_Matches;

   function Scoped_Matches_Of
     (JSON_Data, Archive_Data : Bytes; JSON_Value, Encoded : Span;
      Preserve_Object_Order : Boolean) return Genesis_Correspondence
     with Global => null,
       Post => (if Scoped_Matches_Of'Result = Typed_Tree_Matches_Source_Custody_Open then
         P.Valid (JSON_Data, JSON_Value) and then P.Valid (Archive_Data, Encoded));
   function Scoped_Matches_Of
     (JSON_Data, Archive_Data : Bytes; JSON_Value, Encoded : Span;
      Preserve_Object_Order : Boolean) return Genesis_Correspondence
   is
      A : Bytes renames JSON_Data;
      package S renames Worldline.Scoped_Archive;
      package E renames S.E;
      use type E.Value_Kind;
      File_Value : Span := JSON_Value;

      function Text_Matches (J : Span; V : E.View) return Boolean is
        (JSON_Text_Matches (A, Archive_Data, J, V));

      function Match_Tree (J, Encoded : Span) return Boolean
        with Global => (Input => (JSON_Data, Archive_Data, Preserve_Object_Order)),
          Subprogram_Variant => (Decreases => J.Length);
      function Match_Tree (J, Encoded : Span) return Boolean is
         N : constant Node := Genesis_Prefix (A, J, 0);
         Typ : constant E.View := E.Decode
           (Archive_Data, S.A.Field (Archive_Data, Encoded, "type"), E.Operation);
         Payload : E.View;
         O : Count := 1;
         K : Count := 0;
         Child, Key : Node;
         Pair : E.View;
         Next_Value : Span;
      begin
         if not N.Valid or else N.After /= J.Length then return False; end if;
         case N.Form is
            when Null_Value | Boolean_Value | String_Value =>
               Payload := E.Decode
                 (Archive_Data, S.A.Field (Archive_Data, Encoded, "value"), E.Operation);
               if N.Form = Null_Value then
                  return E.Text_Is (Archive_Data, Typ, "NoneType") and then Payload.Form = E.Null_Value;
               elsif N.Form = Boolean_Value then
                  return E.Text_Is (Archive_Data, Typ, "bool") and then Payload.Form = E.Boolean_Value
                    and then Payload.Boolean_Bit = Match (A, J, 0, "true");
               else
                  return E.Text_Is (Archive_Data, Typ, "str") and then Text_Matches (J, Payload);
               end if;
            when Integer_Value =>
               declare
                  Number : constant Exact_Decimal.Number := Exact_Decimal.Parse (A, J, 0);
               begin
                  if not Number.Valid or else Number.After /= J.Length then return False; end if;
                  if Number.Floating then
                     if not E.Text_Is (Archive_Data, Typ, "float") then return False; end if;
                     declare
                        C : constant Decimal_Binary64.Conversion := Decimal_Binary64.Convert (Number);
                        V : constant E.View := E.Decode
                          (Archive_Data, S.A.Field (Archive_Data, Encoded, "bits"), E.Operation);
                        Encoded_Bits : U64 := 0;
                     begin
                        if not C.Valid or else V.Form /= E.Text_Value or else
                          not E.Bytes_Valid (Archive_Data, V.Payload) or else
                          not Decimal_Binary64.Spelling_Matches (A, J, C.Encoding)
                        then return False; end if;
                        declare
                           Raw : constant Bytes := E.Materialize (Archive_Data, V.Payload);
                        begin
                           if Raw'Length /= 16 then return False; end if;
                           for K in Raw'Range loop
                              pragma Loop_Invariant
                                (Encoded_Bits <= 16#0FFF_FFFF_FFFF_FFFF#);
                              declare
                                 D : constant Integer := Hex (Natural (Raw (K)));
                              begin
                                 if D < 0 then return False; end if;
                                 Encoded_Bits := Encoded_Bits * 16 + U64 (D);
                              end;
                           end loop;
                        end;
                        return C.Encoding = Encoded_Bits;
                     end;
                  end if;
                  if not E.Text_Is (Archive_Data, Typ, "integer") then return False; end if;
                  declare
                     Sign : constant E.View := E.Decode
                       (Archive_Data, S.A.Field (Archive_Data, Encoded, "negative"), E.Operation);
                     Mag : constant E.View := E.Decode
                       (Archive_Data, S.A.Field (Archive_Data, Encoded, "magnitude"), E.Operation);
                     Negative : constant Boolean := Number.Negative;
                     Binary_Value : Big_Integer := To_Big_Integer (0);
                     At_Byte : Count := 0;
                  begin
                     if Sign.Form /= E.Boolean_Value or else Sign.Boolean_Bit /= Negative
                       or else Mag.Form /= E.Text_Value or else
                       not E.Bytes_Valid (Archive_Data, Mag.Payload) then return False; end if;
                     declare
                        Raw : constant Bytes := E.Materialize (Archive_Data, Mag.Payload);
                     begin
                        if Raw'Length mod 2 /= 0 then return False; end if;
                        At_Byte := Raw'Length;
                        while At_Byte > 0 loop
                           pragma Loop_Invariant (At_Byte <= Raw'Length and then At_Byte mod 2 = 0);
                           pragma Loop_Variant (Decreases => At_Byte);
                           At_Byte := At_Byte - 2;
                           declare
                              Hi : constant Integer := Hex (Natural (Raw (Raw'First + At_Byte)));
                              Lo : constant Integer := Hex (Natural (Raw (Raw'First + (At_Byte + 1))));
                           begin
                              if Hi < 0 or else Lo < 0 then return False; end if;
                              Binary_Value := Binary_Value * To_Big_Integer (256) +
                                To_Big_Integer (Hi * 16 + Lo);
                           end;
                        end loop;
                     end;
                     return Number.Coefficient = Binary_Value;
                  end;
               end;
            when Array_Value | Object_Value =>
               if N.Form = Array_Value then
                  if not E.Text_Is (Archive_Data, Typ, "list") then return False; end if;
                  Payload := E.Decode (Archive_Data, S.A.Field (Archive_Data, Encoded, "items"), E.Operation);
                  if Payload.Form /= E.List_Value then return False; end if;
               else
                  if not E.Text_Is (Archive_Data, Typ, "dict") then return False; end if;
                  Payload := E.Decode (Archive_Data, S.A.Field (Archive_Data, Encoded, "fields"), E.Operation);
                  if Payload.Form /= E.Object_Value then return False; end if;
               end if;
               while O < J.Length - 1 loop
                  pragma Loop_Invariant (O in 1 .. J.Length - 1);
                  pragma Loop_Invariant (K < O);
                  pragma Loop_Variant (Decreases => J.Length - O);
                  Next_Value := E.Array_Element (Archive_Data, Payload.Children, K);
                  if N.Form = Object_Value then
                     Key := Prefix (A, J, O);
                     if not Key.Valid or else Key.Form /= String_Value or else
                       Key.After >= J.Length then return False; end if;
                     if Preserve_Object_Order then
                        Pair := E.Decode (Archive_Data, Next_Value, E.Finalization);
                        if Pair.Form /= E.List_Value or else
                          E.Array_Length (Archive_Data, Pair.Children) /= 2 or else
                          not Text_Matches (Part (J, Key.First, Key.After), E.Decode
                            (Archive_Data, E.Array_Element (Archive_Data, Pair.Children, 0), E.Operation))
                        then return False; end if;
                        Next_Value := E.Array_Element (Archive_Data, Pair.Children, 1);
                     else
                        --  Canonical JSON sorts names; original S.record keeps
                        --  dict insertion order. Find the unique decoded name,
                        --  without rewriting either original archive allocation.
                        declare
                           Found : Boolean := False;
                           Children : constant Count := E.Array_Length (Archive_Data, Payload.Children);
                        begin
                           if Children > 0 then
                              for I in Count range 0 .. Children - 1 loop
                                 Pair := E.Decode (Archive_Data,
                                   E.Array_Element (Archive_Data, Payload.Children, I), E.Finalization);
                                 if Pair.Form /= E.List_Value or else
                                   E.Array_Length (Archive_Data, Pair.Children) /= 2
                                 then return False; end if;
                                 if Text_Matches (Part (J, Key.First, Key.After), E.Decode
                                   (Archive_Data, E.Array_Element (Archive_Data, Pair.Children, 0), E.Operation))
                                 then
                                    if Found then return False; end if;
                                    Found := True;
                                    Next_Value := E.Array_Element (Archive_Data, Pair.Children, 1);
                                 end if;
                              end loop;
                           end if;
                           if not Found then return False; end if;
                        end;
                     end if;
                     O := Key.After + 1;
                  end if;
                  Child := Genesis_Prefix (A, J, O);
                  if not Child.Valid or else Child.After <= Child.First or else
                    Child.After - Child.First >= J.Length or else
                    not Match_Tree (Part (J, Child.First, Child.After), Next_Value)
                  then return False; end if;
                  O := Child.After;
                  K := K + 1;
                  if O < J.Length - 1 then O := O + 1; end if;
               end loop;
               return O = J.Length - 1 and then K = E.Array_Length (Archive_Data, Payload.Children);
            when Invalid_Value => return False;
         end case;
      end Match_Tree;
   begin
      if not P.Valid (A, File_Value) then return JSON_Grammar_Unimplemented_Or_Invalid; end if;
      if File_Value.Length > 0 and then
        Byte_At (A, File_Value, File_Value.Length - 1) = Character'Pos (ASCII.LF)
      then File_Value := Part (File_Value, 0, File_Value.Length - 1); end if;
      declare
         Root : constant Node := Genesis_Prefix (A, File_Value, 0);
      begin
         if not Root.Valid or else Root.After /= File_Value.Length then
            return JSON_Grammar_Unimplemented_Or_Invalid;
         end if;
      end;
      if not S.Valid (Archive_Data, Encoded) then return Scoped_Archive_Invalid; end if;
      if not Match_Tree (File_Value, Encoded) then return Typed_Tree_Differs; end if;
      return Typed_Tree_Matches_Source_Custody_Open;
   end Scoped_Matches_Of;

   function Scoped_Archive_JSON_Matches
     (JSON_Data, Archive_Data : Bytes; JSON_Value, Encoded : Span)
      return Genesis_Correspondence
   is (Scoped_Matches_Of (JSON_Data, Archive_Data, JSON_Value, Encoded, False));

   function Genesis_Archive_Matches
     (A : Bytes; Genesis_File, Genesis_Row : Span) return Genesis_Correspondence
   is (Scoped_Matches_Of (A, A, Genesis_File, Genesis_Row, True));
end Canonical_Artifacts;
