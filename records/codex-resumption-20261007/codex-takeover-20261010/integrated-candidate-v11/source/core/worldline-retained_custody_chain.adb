with Interfaces;
with Worldline.Archive_Text;
package body Worldline.Retained_Custody_Chain with SPARK_Mode is
   use type E.Q.Byte;
   use type Interfaces.Unsigned_64;
   use type Attest.Byte_Array;
   Domain : constant String := "worldline.protected-root-custody-v1" & Character'Val (0);
   Hex : constant String := "0123456789abcdef";
   subtype Block is Attest.Byte_Array (0 .. SHA.Block_Bytes - 1);

   function Same (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (E.C.P.Valid (Data, Left) and then E.C.P.Valid (Data, Right) and then
      Left.Length = Right.Length and then
      (if Left.Length > 0 then
       (for all I in E.Count range 0 .. Left.Length - 1 =>
        Data (Left.First + I) = Data (Right.First + I))));
   function Literal (Data : E.Bytes; Item : E.Span; Text : String) return Boolean is
     (E.C.P.Valid (Data, Item) and then Item.Length = Text'Length and then
      (for all I in Text'Range =>
       Data (Item.First + E.Count (I - Text'First)) = Character'Pos (Text (I))));
   function Hex_Matches (Data : E.Bytes; Item : E.Span; Digest : SHA.Digest)
      return Boolean is
   begin
      if not E.C.P.Valid (Data, Item) or else Item.Length /= Digest'Length * 2 then
         return False;
      end if;
      for I in Digest'Range loop
         if Data (Item.First + E.Count (I) * 2) /=
              Character'Pos (Hex (Natural (Digest (I) / 16) + 1)) or else
            Data (Item.First + E.Count (I) * 2 + 1) /=
              Character'Pos (Hex (Natural (Digest (I) mod 16) + 1)) then
            return False;
         end if;
      end loop;
      return True;
   end Hex_Matches;
   function Kind_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
     (Literal (Data, Item, "PREPARED") or else Literal (Data, Item, "HELD") or else
      Literal (Data, Item, "RUNNING") or else Literal (Data, Item, "EXECUTION_NATIVE") or else
      Literal (Data, Item, "EXECUTION_ACK") or else Literal (Data, Item, "HANDOFF_INTENT") or else
      Literal (Data, Item, "CUSTODY_ACK") or else Literal (Data, Item, "ORIGINAL_PROGRESS") or else
      Literal (Data, Item, "ORIGINAL_RESULT") or else Literal (Data, Item, "HANDLER_TERMINAL") or else
      Literal (Data, Item, "CLOSED") or else Literal (Data, Item, "UNKNOWN") or else
      Literal (Data, Item, "FRONT_RECONSTRUCTION") or else Literal (Data, Item, "HISTORICAL_SETTLEMENT"));

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
   with Pre => E.C.P.Valid (Data, Item)
   is
      Context : SHA.Context := SHA.Initial;
   begin
      Feed (Context, Data, Item);
      return SHA.Final (Context);
   end Hash;
   function Mac (Data : E.Bytes; Key, Message : E.Span) return SHA.Digest
   with Pre => E.C.P.Valid (Data, Key) and then E.C.P.Valid (Data, Message)
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
   function Verify
     (Data : E.Bytes; Key, Genesis_Archive, Head_Archive : E.Span;
      Genesis : Genesis_Rows; Rows : Event_Rows; Heads : Head_Rows) return Result
   is
      Answer : Result;
   begin
      if not E.C.P.Valid (Data, Key) or else not S.Valid (Data, Genesis_Archive) or else
        not S.Valid (Data, Head_Archive) then return Answer; end if;
      if Genesis'Length /= 1 or else
        not Literal (Data, Genesis (Genesis'First).Name, "owner-genesis") or else
        not Same (Data, Genesis (Genesis'First).Value, Genesis_Archive) then
         Answer.State := Genesis_Mismatch; return Answer;
      end if;
      Answer.Origin := Hash (Data, Genesis_Archive); Answer.Head := Answer.Origin;
      for I in Rows'Range loop
         Answer.Failing_Row := I;
         declare
            Row : constant Event_Row := Rows (I);
         begin
            if not Kind_Valid (Data, Row.Kind) or else
              not Worldline.Archive_Text.Text_Valid (Data, (Row.Operation.First, Row.Operation.Length)) or else
              not J.V1_Base_Matches (Data, Row.Base_Archive, Row.Previous, Row.Operation, Row.Kind, Row.Record_Archive) then
               Answer.State := Row_Malformed; return Answer;
            end if;
            if not Hex_Matches (Data, Row.Previous, Answer.Head) then
               Answer.State := Row_Link; return Answer;
            end if;
            Answer.Head := Hash (Data, Row.Base_Archive);
            if not Hex_Matches (Data, Row.Event_Id, Answer.Head) then
               Answer.State := Row_Id; return Answer;
            end if;
            if I > Rows'First then
               for Earlier in Rows'First .. I - 1 loop
                  if Same (Data, Row.Event_Id, Rows (Earlier).Event_Id) then
                     Answer.State := Row_Duplicate; return Answer;
                  end if;
               end loop;
            end if;
            if not Hex_Matches (Data, Row.Mac, Mac (Data, Key, Row.Base_Archive)) then
               Answer.State := Row_Mac; return Answer;
            end if;
         end;
      end loop;
      Answer.Failing_Row := 0;
      if Heads'Length /= 1 or else not Literal (Data, Heads (Heads'First).Name, "current") or else
        not Hex_Matches (Data, Heads (Heads'First).Event_Id, Answer.Head) then
         Answer.State := Head_Mismatch; return Answer;
      end if;
      if S.Member_Count (Data, Head_Archive) /= 2 or else
        not S.Member_Name_Is (Data, Head_Archive, 0, "head") or else
        not S.Member_Name_Is (Data, Head_Archive, 1, "genesis") or else
        not S.Text_Matches (Data, S.Field (Data, Head_Archive, "head"), Heads (Heads'First).Event_Id) or else
        not S.A.Same_Encoding (Data, S.Field (Data, Head_Archive, "genesis"), Genesis_Archive) then
         Answer.State := Head_Archive_Mismatch; return Answer;
      end if;
      if not Hex_Matches (Data, Heads (Heads'First).Mac, Mac (Data, Key, Head_Archive)) then
         Answer.State := Head_Mac; return Answer;
      end if;
      Answer.State := Retained_Chain_Matches;
      return Answer;
   end Verify;
end Worldline.Retained_Custody_Chain;
