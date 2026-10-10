with Interfaces;
package body Worldline.Custody_V2_Empty_Seed with SPARK_Mode is
   use type E.Q.Byte;
   use type Interfaces.Unsigned_64;
   use type Attest.Byte_Array;
   Domain : constant String := "worldline.protected-root-custody-v2" & Character'Val (0);
   Hex : constant String := "0123456789abcdef";
   subtype Block is Attest.Byte_Array (0 .. SHA.Block_Bytes - 1);
   function Origin_Matches (Data : E.Bytes; Origin_Text : E.Span; Origin : SHA.Digest)
      return Boolean is
   begin
      if not E.C.P.Valid (Data, Origin_Text) or else Origin_Text.Length /= Origin'Length * 2 then
         return False;
      end if;
      for I in Origin'Range loop
         if Data (Origin_Text.First + E.Count (I) * 2) /=
              Character'Pos (Hex (Natural (Origin (I) / 16) + 1)) or else
            Data (Origin_Text.First + E.Count (I) * 2 + 1) /=
              Character'Pos (Hex (Natural (Origin (I) mod 16) + 1)) then
            return False;
         end if;
      end loop;
      return True;
   end Origin_Matches;
   -- Streams the original quantity-indexed arena; never casts its full length
   -- to Natural or truncates it to an Attest.Byte_Array extent.
   procedure Feed (Context : in out SHA.Context; Data : E.Bytes; Item : E.Span)
   with Pre => E.C.P.Valid (Data, Item),
     Post => SHA.Absorbed (Context) = SHA.Absorbed (Context'Old) + Interfaces.Unsigned_64 (Item.Length)
   is
      Before : constant Interfaces.Unsigned_64 := SHA.Absorbed (Context);
   begin
      if Item.Length > 0 then
         for I in E.Count range 0 .. Item.Length - 1 loop
            pragma Loop_Invariant (SHA.Absorbed (Context) = Before + Interfaces.Unsigned_64 (I));
            SHA.Update (Context, Attest.Byte_Array'(0 => Data (Item.First + I)));
         end loop;
      end if;
   end Feed;
   function Hash (Data : E.Bytes; Item : E.Span) return SHA.Digest
   is
      Context : SHA.Context := SHA.Initial;
   begin
      Feed (Context, Data, Item);
      return SHA.Final (Context);
   end Hash;
   function Mac (Data : E.Bytes; Key, Message : E.Span) return SHA.Digest
   is
      K0, Inner_Pad, Outer_Pad : Block := (others => 0);
      Inner_Context, Outer_Context : SHA.Context := SHA.Initial;
   begin
      if Key.Length > SHA.Block_Bytes then
         K0 (SHA.Digest'Range) := Hash (Data, Key);
      elsif Key.Length > 0 then
         for I in E.Count range 0 .. Key.Length - 1 loop
            K0 (Natural (I)) := Data (Key.First + I);
         end loop;
      end if;
      for I in Block'Range loop
         Inner_Pad (I) := K0 (I) xor 16#36#;
         Outer_Pad (I) := K0 (I) xor 16#5C#;
      end loop;
      SHA.Update (Inner_Context, Inner_Pad);
      for C of Domain loop
         SHA.Update (Inner_Context, Attest.Byte_Array'(0 => Character'Pos (C)));
      end loop;
      Feed (Inner_Context, Data, Message);
      SHA.Update (Outer_Context, Outer_Pad);
      SHA.Update (Outer_Context, SHA.Final (Inner_Context));
      return SHA.Final (Outer_Context);
   end Mac;

   function Archives_Match
     (Data : E.Bytes; Genesis_Row, Genesis_Message, Head_Message : E.Span)
      return Boolean is
     (S.Valid (Data, Genesis_Row) and then
      S.Valid (Data, Genesis_Message) and then S.Member_Count (Data, Genesis_Message) = 1 and then
      S.Member_Name_Is (Data, Genesis_Message, 0, "genesis") and then
      S.A.Same_Encoding (Data, S.Field (Data, Genesis_Message, "genesis"), Genesis_Row) and then
      S.Valid (Data, Head_Message) and then S.Member_Count (Data, Head_Message) = 3 and then
      S.Member_Name_Is (Data, Head_Message, 0, "head_kind") and then
      S.Member_Name_Is (Data, Head_Message, 1, "head") and then
      S.Member_Name_Is (Data, Head_Message, 2, "genesis") and then
      S.Text_Is (Data, S.Field (Data, Head_Message, "head_kind"), "ORIGIN") and then
      S.A.Same_Encoding (Data, S.Field (Data, Head_Message, "genesis"), Genesis_Row));

   function Construct
     (Data : E.Bytes; Key, Genesis_Row, Genesis_Message,
      Head_Message, Origin_Text : E.Span;
      Event_Count, Alternative_Count, Root_Count, Subject_Count, Blob_Count : E.Count)
      return Result is
      Answer : Result;
   begin
      if not E.C.P.Valid (Data, Key) or else not E.C.P.Valid (Data, Genesis_Row) or else
        not E.C.P.Valid (Data, Genesis_Message) or else not E.C.P.Valid (Data, Head_Message) or else
        not E.C.P.Valid (Data, Origin_Text) then return Answer; end if;
      if Event_Count /= 0 or else Alternative_Count /= 0 or else Root_Count /= 0 or else
        Subject_Count /= 0 or else Blob_Count /= 0 then
         Answer.State := Nonempty_State; return Answer;
      end if;
      if not Archives_Match (Data, Genesis_Row, Genesis_Message, Head_Message) then
         Answer.State := Archive_Mismatch; return Answer;
      end if;
      Answer.Origin := Hash (Data, Genesis_Row);
      if not Origin_Matches (Data, Origin_Text, Answer.Origin) or else
        not S.Text_Matches (Data, S.Field (Data, Head_Message, "head"), Origin_Text) then
         Answer.State := Origin_Mismatch; return Answer;
      end if;
      Answer.Genesis_Mac := Mac (Data, Key, Genesis_Message);
      Answer.Head_Mac := Mac (Data, Key, Head_Message);
      Answer.State := Constructed_Empty_Authentication;
      return Answer;
   end Construct;
end Worldline.Custody_V2_Empty_Seed;
