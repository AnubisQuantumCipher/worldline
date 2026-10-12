with Attest.SHA256;
with Worldline.Recovery_Archive;
with Interfaces;
with SPARK.Big_Integers;
with Worldline.Scoped_Archive;
with Worldline.Scoped_Capture_Owner_Projection;
with Worldline.Scoped_Capture_History_Projection;
with Worldline.Scoped_Capture_Evolution_Projection;
with Worldline.Scoped_Capture_Namespace_Projection;
with Worldline.Raw_JSON;
with Worldline.Scoped_Record_Source;

package body Worldline.Scoped_Capture_Projection with SPARK_Mode is
   package SA renames Worldline.Scoped_Archive;
   package OA renames SA.A;
   package RA renames Worldline.Recovery_Archive;
   package Q renames E.Q;
   package SHA renames Attest.SHA256;
   use SPARK.Big_Integers;
   use type E.Count;
   use type E.Span;
   use type E.Value_Kind;
   use type E.Bytes;
   use type Q.Byte;
   use type Interfaces.Unsigned_64;
   use type R.Replay_State;
   use type R.Scoped_Entry;
   function Raw_Source_Field (Data : E.Bytes; Item : E.Span; Name : String) return E.Span is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if not RA.Source_Valid (Data, Item, False)
        or else View.Form not in E.Record_Value | E.Object_Value
      then return (1, 0); end if;
      if E.Array_Length (Data, View.Children) > 0 then
         for I in E.Count range 0 .. E.Array_Length (Data, View.Children) - 1 loop
            declare
               Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, View.Children, I), E.Finalization);
            begin
               if E.Text_Is (Data, E.Decode (Data, E.Array_Element (Data, Pair.Children, 0),
                 (if View.Form = E.Record_Value then E.Finalization else E.Operation)), Name)
               then return E.Array_Element (Data, Pair.Children, 1); end if;
            end;
         end loop;
      end if;
      return (1, 0);
   end Raw_Source_Field;
   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span renames Raw_Source_Field;
   function Element (Data : E.Bytes; Item : E.Span; Index : E.Count) return E.Span
     with Global => null,
       Post => Element'Result.Length = 0 or else Element'Result.Length < Item.Length
   is
      V : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if not RA.Source_Valid (Data, Item, False) or else V.Form not in E.Tuple_Value | E.List_Value then return (1, 0); end if;
      return E.Array_Element (Data, V.Children, Index);
   end Element;
   function Len (Data : E.Bytes; Item : E.Span) return E.Count
     with Global => null,
       Post => Len'Result <= Item.Length and then (if Len'Result > 0 then Item.Length >= 2)
   is
      V : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if not RA.Source_Valid (Data, Item, False) or else V.Form not in E.Tuple_Value | E.List_Value then return 0; end if;
      return E.Array_Length (Data, V.Children);
   end Len;
   function Sequence_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
     (RA.Source_Valid (Data, Item, False)
      and then E.Decode (Data, Item, E.Operation).Form in E.Tuple_Value | E.List_Value);
   function Integer_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
     (RA.Source_Valid (Data, Item, False)
      and then E.Decode (Data, Item, E.Operation).Form = E.Integer_Value
      and then R.Archive_Integer_Valid (Data, Item));
   function Text (Data : E.Bytes; Item : E.Span; Value : String) return Boolean is
     (RA.Source_Valid (Data, Item, False) and then E.Text_Is (Data, E.Decode (Data, Item, E.Operation), Value));
   function Is_None (Data : E.Bytes; Item : E.Span) return Boolean is
     (RA.Source_Valid (Data, Item, False) and then E.Decode (Data, Item, E.Operation).Form = E.Null_Value);
   function Bytes_Valid (Data : E.Bytes; Item : E.Span) return Boolean
     with Global => null
   is
      V : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      return RA.Source_Valid (Data, Item, False) and then V.Form = E.Bytes_Value and then E.Bytes_Valid (Data, V.Payload);
   end Bytes_Valid;
   function Bytes (Data : E.Bytes; Item : E.Span) return E.Bytes
   is (E.Materialize (Data, E.Decode (Data, Item, E.Operation).Payload))
     with Pre => Bytes_Valid (Data, Item);

   function Number (Data : E.Bytes; Item : E.Span) return Valid_Big_Integer is
      Result : Big_Integer := To_Big_Integer (0);
   begin
      if not Integer_Valid (Data, Item) then return To_Big_Integer (-1); end if;
      declare
         Raw : constant E.Bytes := R.Archive_Integer_Magnitude (Data, Item);
      begin
         for I in reverse Raw'Range loop
            Result := Result * To_Big_Integer (256) + To_Big_Integer (Integer (Raw (I)));
         end loop;
      end;
      return (if R.Archive_Integer_Negative (Data, Item) then -Result else Result);
   end Number;
   function Count_Number (Value : E.Count) return Valid_Big_Integer
     with Global => null
   is
      Remaining : E.Count := Value;
      Result : Big_Integer := To_Big_Integer (0);
      Place : Big_Integer := To_Big_Integer (1);
   begin
      while Remaining > 0 loop
         pragma Loop_Variant (Decreases => Remaining);
         Result := Result + To_Big_Integer (Integer (Remaining mod 256)) * Place;
         Place := Place * To_Big_Integer (256); Remaining := Remaining / 256;
      end loop;
      return Result;
   end Count_Number;
   function Is_Number (Data : E.Bytes; Item : E.Span; Value : Integer) return Boolean is
     (Integer_Valid (Data, Item) and then Number (Data, Item) = To_Big_Integer (Value));

   function Text_View (Data : E.Bytes; Item : E.Span) return E.View is
     (E.Decode (Data, Item, E.Operation));
   function Text_Valid (Data : E.Bytes; Item : E.Span) return Boolean
     with Global => null
   is
      V : constant E.View := Text_View (Data, Item);
   begin
      return RA.Source_Valid (Data, Item, False) and then V.Form = E.Text_Value and then E.Bytes_Valid (Data, V.Payload);
   end Text_Valid;
   function Text_Bytes (Data : E.Bytes; Item : E.Span) return E.Bytes
   is (E.Materialize (Data, Text_View (Data, Item).Payload))
     with Pre => Text_Valid (Data, Item);
   function Members (Data : E.Bytes; Item : E.Span) return E.Span
     with Global => null, Post => Members'Result.Length <= Item.Length
   is
      V : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if RA.Source_Valid (Data, Item, False) and then V.Form in E.Object_Value | E.Record_Value then
         return V.Children;
      else return (1, 0); end if;
   end Members;
   function Member_Value (Data : E.Bytes; Item, Name : E.Span) return E.Span is
      M : constant E.Span := Members (Data, Item);
      Count : constant E.Count := E.Array_Length (Data, M);
   begin
      if Count > 0 then
         for I in E.Count range 0 .. Count - 1 loop
            declare
               Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, M, I), E.Finalization);
               Key : constant E.Span := E.Array_Element (Data, Pair.Children, 0);
            begin
               if RA.Ordered_Source_Value_Matches (Data, Data, Key, Name, False, False) then return E.Array_Element (Data, Pair.Children, 1); end if;
            end;
         end loop;
      end if;
      return (1, 0);
   end Member_Value;
   function Nibble (B : Q.Byte) return Integer;
   function Float_Valid (Data : E.Bytes; Item : E.Span) return Boolean
     with Global => null
   is
      V : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      return RA.Source_Valid (Data, Item, False) and then V.Form = E.Float_Value
        and then E.Bytes_Valid (Data, V.Payload) and then E.Materialize (Data, V.Payload)'Length = 8;
   end Float_Valid;
   function Float_Bits (Data : E.Bytes; Item : E.Span) return E.Bytes
   is (E.Materialize (Data, E.Decode (Data, Item, E.Operation).Payload))
     with Pre => Float_Valid (Data, Item);
   function Same (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (RA.Ordered_Source_Value_Matches (Data, Data, Left, Right, False, False));
   function Field_Same (Data : E.Bytes; Left, Right : E.Span; Name : String) return Boolean is
     (Same (Data, F (Data, Left, Name), F (Data, Right, Name)));

   function Nibble (B : Q.Byte) return Integer is
     (if B in 48 .. 57 then Integer (B) - 48 elsif B in 97 .. 102 then Integer (B) - 87 else -1);
   function Hex_Matches (Raw, Hex : E.Bytes) return Boolean
     with Global => null
   is
   begin
      if Raw'Length > E.Count'Last / 2 or else Hex'Length /= Raw'Length * 2 then return False; end if;
      for I in Raw'Range loop
         declare
            J : constant Q.Byte_Index := Hex'First + (I - Raw'First) * 2;
            H : constant Integer := Nibble (Hex (J));
            L : constant Integer := Nibble (Hex (J + 1));
         begin
            if H < 0 or else L < 0 or else Integer (Raw (I)) /= H * 16 + L then return False; end if;
         end;
      end loop;
      return True;
   end Hex_Matches;
   function Id_Hex (Data : E.Bytes; Id, Encoded : E.Span) return Boolean is
     (Bytes_Valid (Data, Id) and then Text_Valid (Data, Encoded)
      and then Bytes (Data, Id)'Length > 0 and then Hex_Matches (Bytes (Data, Id), Text_Bytes (Data, Encoded)));
   function Id_Text (Data : E.Bytes; Id, Encoded : E.Span) return Boolean is
     (Bytes_Valid (Data, Id) and then Text_Valid (Data, Encoded) and then Bytes (Data, Id) = Text_Bytes (Data, Encoded));
   function Digest_Matches (Raw : E.Bytes; Data : E.Bytes; Id : E.Span; Prefix : String := "") return Boolean
     with Global => null
   is
      C : SHA.Context := SHA.Initial;
   begin
      if not Bytes_Valid (Data, Id) or else Bytes (Data, Id)'Length /= SHA.Digest_Bytes
        or else Interfaces.Unsigned_64 (Raw'Length) > SHA.Max_Message_Bytes
        or else Interfaces.Unsigned_64 (Prefix'Length) > SHA.Max_Message_Bytes - Interfaces.Unsigned_64 (Raw'Length)
      then return False; end if;
      --  Same bytes in the same order; the indices only expose the count absorbed.
      for K in Prefix'Range loop
         pragma Loop_Invariant (SHA.Absorbed (C) = Interfaces.Unsigned_64 (K - Prefix'First));
         SHA.Update (C, [0 => Attest.Byte (Character'Pos (Prefix (K)))]);
      end loop;
      for K in Raw'Range loop
         pragma Loop_Invariant (SHA.Absorbed (C) = Interfaces.Unsigned_64 (Prefix'Length) + Interfaces.Unsigned_64 (K - Raw'First));
         SHA.Update (C, [0 => Attest.Byte (Raw (K))]);
      end loop;
      declare
         H : constant SHA.Digest := SHA.Final (C);
         Value : constant E.Bytes := Bytes (Data, Id);
      begin
         return (for all I in H'Range => Q.Byte (H (I)) = Value (Value'First + E.Count (I)));
      end;
   end Digest_Matches;
   function JSON_Matches (Data : E.Bytes; JSON, Item : E.Span) return Boolean
     with Global => null
   is
   begin
      if not Bytes_Valid (Data, JSON) then return False; end if;
      declare Raw : constant E.Bytes := Bytes (Data, JSON); begin
         return E.C.Operation_Archive_JSON_Matches (Raw, Data, (Raw'First, Raw'Length), Item);
      end;
   end JSON_Matches;
   function Hash_Field (Data : E.Bytes; Raw, Id : E.Span; Prefix : String := "") return Boolean is
     (Bytes_Valid (Data, Raw) and then Digest_Matches (Bytes (Data, Raw), Data, Id, Prefix));

   function Stable_Identity (Data : E.Bytes; Left, Right : E.Span) return Boolean
     with Global => null
   is
   begin
      return Field_Same (Data, Left, Right, "device") and then Field_Same (Data, Left, Right, "inode")
        and then Field_Same (Data, Left, Right, "mode") and then Field_Same (Data, Left, Right, "uid")
        and then Field_Same (Data, Left, Right, "gid");
   end Stable_Identity;
   function Syscall (Data : E.Bytes; Item : E.Span; Call : String; Result : Integer) return Boolean is
     (Text (Data, F (Data, Item, "call"), Call) and then Is_Number (Data, F (Data, Item, "result"), Result)
      and then Is_Number (Data, F (Data, Item, "errno"), 0));
   function Descriptor (Data : E.Bytes; Inventory, Name : E.Span) return E.Span is
     (Member_Value (Data, F (Data, Inventory, "current_descriptors"), Name));

   function Line (Raw : E.Bytes; Name : String; Separator : Q.Byte) return E.Span is
      Start : Q.Byte_Index;
      Found : E.Span := (1, 0);
   begin
      --  A null Raw has no line (the original raised initializing Start when
      --  its lower bound lay outside Byte_Index).
      if Raw'Length = 0 then return Found; end if;
      Start := Raw'First;
      while Start <= Raw'Last loop
         pragma Loop_Variant (Increases => Start);
         pragma Loop_Invariant (Start >= Raw'First);
         declare
            Finish : Q.Byte_Index := Start;
         begin
            while Finish <= Raw'Last and then Raw (Finish) /= 10 loop
               pragma Loop_Invariant (Finish in Start .. Raw'Last); pragma Loop_Variant (Increases => Finish);
               --  The original raised (Finish + 1) exactly here; refuse.
               if Finish = E.Count'Last then return (1, 0); end if;
               Finish := Finish + 1;
            end loop;
            if Finish - Start > E.Count (Name'Length)
              and then (for all I in Name'Range => Raw (Start + E.Count (I - Name'First)) = Character'Pos (Name (I)))
              and then Raw (Start + E.Count (Name'Length)) = Separator
            then
               if Found.Length > 0 then return (1, 0); end if;
               Found := (Start + E.Count (Name'Length) + 1, Finish - Start - E.Count (Name'Length) - 1);
            end if;
            if Finish = Raw'Last then exit; end if;
            --  The original raised (Start := Finish + 1) exactly here; refuse.
            if Finish = E.Count'Last then return (1, 0); end if;
            Start := Finish + 1;
         end;
      end loop;
      return Found;
   end Line;
   function Space (B : Q.Byte) return Boolean is (B in 9 .. 13 or else B = 32);
   function Word (Raw : E.Bytes; Item : E.Span; Index : Positive) return E.Span is
      Position : E.Count := 0;
      Current : Positive := 1;
   begin
      if not E.C.P.Valid (Raw, Item) then return (1, 0); end if;
      while Position < Item.Length loop
         pragma Loop_Variant (Increases => Position);
         while Position < Item.Length and then Space (Raw (Item.First + Position)) loop
            pragma Loop_Invariant (Position in Position'Loop_Entry .. Item.Length); pragma Loop_Variant (Increases => Position);
            Position := Position + 1;
         end loop;
         declare Start : constant E.Count := Position; begin
            while Position < Item.Length and then not Space (Raw (Item.First + Position)) loop
               pragma Loop_Invariant (Position in Start .. Item.Length); pragma Loop_Variant (Increases => Position);
               Position := Position + 1;
            end loop;
            if Position > Start then
               if Current = Index then return (Item.First + Start, Position - Start); end if;
               if Current = Positive'Last then return (1, 0); end if;
               Current := Current + 1;
            end if;
         end;
      end loop;
      return (1, 0);
   end Word;
   function Decimal (Raw : E.Bytes; Item : E.Span) return Valid_Big_Integer is
      Value : Big_Integer := To_Big_Integer (0);
   begin
      if not E.C.P.Valid (Raw, Item) or else Item.Length = 0 then return To_Big_Integer (-1); end if;
      for I in E.Count range 0 .. Item.Length - 1 loop
         if Raw (Item.First + I) not in 48 .. 57 then return To_Big_Integer (-1); end if;
         Value := Value * To_Big_Integer (10) + To_Big_Integer (Integer (Raw (Item.First + I)) - 48);
      end loop;
      return Value;
   end Decimal;
   function Stat_Number (Raw : E.Bytes; Index : Positive) return Valid_Big_Integer is
      Close : E.Count := 0;
   begin
      if Raw'Length < 4 then return To_Big_Integer (-1); end if;
      if Index = 1 then return Decimal (Raw, Word (Raw, (Raw'First, Raw'Length), 1)); end if;
      for I in Raw'Range loop
         if I < Raw'Last and then Raw (I) = 41 and then Raw (I + 1) = 32 then Close := I; end if;
      end loop;
      if Close = 0 or else Close >= Raw'Last then return To_Big_Integer (-1); end if;
      --  The original raised exactly here (Close + 2 past E.Count, or the
      --  Positive word index Index - 2 = 0); refuse with the non-number.
      if Close > E.Count'Last - 2 or else Index = 2 then return To_Big_Integer (-1); end if;
      return Decimal (Raw, Word (Raw, (Close + 2, Raw'Last - Close - 1), Index - 2));
   end Stat_Number;
   --  An index past E.Count (where the original raised) reads as a mismatch.
   function Byte_Part_Equals (Raw : E.Bytes; Item : E.Span; Expected : E.Bytes) return Boolean is
     (E.C.P.Valid (Raw, Item) and then Item.Length = Expected'Length
      and then (for all I in Expected'Range =>
        Item.First <= E.Count'Last - I and then Raw (Item.First + I - Expected'First) = Expected (I)));
   function Property (Data : E.Bytes; Manager : E.Span; Name : String; Id : E.Span) return Boolean is
      Stdout : constant E.Span := F (Data, Manager, "stdout");
   begin
      if not Bytes_Valid (Data, Stdout) or else not Bytes_Valid (Data, Id) then return False; end if;
      declare Raw : constant E.Bytes := Bytes (Data, Stdout); begin
         return Byte_Part_Equals (Raw, Line (Raw, Name, 61), Bytes (Data, Id));
      end;
   end Property;
   function Parts_Same (Left : E.Bytes; L : E.Span; Right : E.Bytes; R : E.Span) return Boolean is
     (E.C.P.Valid (Left, L) and then E.C.P.Valid (Right, R) and then L.Length > 0 and then L.Length = R.Length
      and then (for all I in E.Count range 0 .. L.Length - 1 => Left (L.First + I) = Right (R.First + I)));
   function Role_Entry (Data : E.Bytes; Inventory, Name : E.Span) return E.Span
     with Global => null
   is
      Roles : constant E.Span := F (Data, Inventory, "roles");
   begin
      if Len (Data, Roles) > 0 then
         for I in E.Count range 0 .. Len (Data, Roles) - 1 loop
            if Same (Data, F (Data, Element (Data, Roles, I), "role"), Name) then return Element (Data, Roles, I); end if;
         end loop;
      end if;
      return (1, 0);
   end Role_Entry;
   function Poll_Matches (Data : E.Bytes; Item, Expected_Wait, Fd : E.Span) return Boolean
     with Global => null
   is
      Poll : constant E.Span := F (Data, Item, "poll");
      Args : constant E.Span := F (Data, Poll, "args");
      Returned : constant E.Span := F (Data, Poll, "returned");
   begin
      if not Text (Data, F (Data, Poll, "call"), "poll") or else not Same (Data, F (Data, Args, "fd"), Fd)
        or else not Is_Number (Data, F (Data, Args, "events"), 25)
        or else not Is_Number (Data, F (Data, Args, "timeout"), 0)
        or else not Is_Number (Data, F (Data, Poll, "errno"), 0)
        or else not Sequence_Valid (Data, Returned)
        or else not Same (Data, F (Data, Item, "wait"), Expected_Wait)
      then return False; end if;
      if Len (Data, Returned) = 0 then
         return Is_Number (Data, F (Data, Poll, "result"), 0) and then Bytes_Valid (Data, Expected_Wait)
           and then Bytes (Data, Expected_Wait) = [80,73,68,70,68,95,76,73,86,69];
      elsif Len (Data, Returned) = 1 then
         return Is_Number (Data, F (Data, Poll, "result"), 1) and then Len (Data, Element (Data, Returned, 0)) = 2
           and then Same (Data, Element (Data, Element (Data, Returned, 0), 0), Fd)
           and then Integer_Valid (Data, Element (Data, Element (Data, Returned, 0), 1))
           and then Number (Data, Element (Data, Element (Data, Returned, 0), 1)) > To_Big_Integer (0)
           and then Bytes_Valid (Data, Expected_Wait)
           and then Bytes (Data, Expected_Wait) = [80,73,68,70,68,95,84,69,82,77,73,78,65,76];
      else return False; end if;
   end Poll_Matches;

   function Credential_Number (Data : E.Bytes; Item : E.Span; Part : Positive) return Valid_Big_Integer
     with Global => null
   is
      Result : Big_Integer := To_Big_Integer (0);
   begin
      if Part > 3 or else not Bytes_Valid (Data, Item) then return To_Big_Integer (-1); end if;
      declare Raw : constant E.Bytes := Bytes (Data, Item); begin
         if Raw'Length /= 12 then return To_Big_Integer (-1); end if;
         for I in reverse E.Count range 0 .. 3 loop
            Result := Result * To_Big_Integer (256)
              + To_Big_Integer (Integer (Raw (Raw'First + E.Count (Part - 1) * 4 + I)));
         end loop;
         if Part = 1 and then Result >= To_Big_Integer (2) ** 31 then Result := Result - To_Big_Integer (2) ** 32; end if;
      end;
      return Result;
   end Credential_Number;
   function Maps_Match (Data : E.Bytes; Maps, Inventory : E.Span) return Boolean is
      Files : constant E.Span := F (Data, Inventory, "current_source_files");
   begin
      if not Bytes_Valid (Data, Maps) or else not Sequence_Valid (Data, Files) then return False; end if;
      declare
         Raw : constant E.Bytes := Bytes (Data, Maps);
         Offset : E.Count := 0;
      begin
         while Offset < Raw'Length loop
            pragma Loop_Variant (Increases => Offset);
            declare
               Start : constant E.Count := Offset;
               Found : Boolean := False;
            begin
               while Offset < Raw'Length and then Raw (Raw'First + Offset) /= 10 loop
                  pragma Loop_Invariant (Offset in Start .. Raw'Length - 1); pragma Loop_Variant (Increases => Offset);
                  Offset := Offset + 1;
               end loop;
               declare
                  Line_Span : constant E.Span := (Raw'First + Start, Offset - Start);
                  Fifth : constant E.Span := Word (Raw, Line_Span, 5);
                  Tail : E.Count := (if Fifth.Length = 0 then Offset else Fifth.First - Raw'First + Fifth.Length);
               begin
                  while Tail < Offset and then Raw (Raw'First + Tail) in 9 | 32 loop
                     pragma Loop_Invariant (Tail < Offset); pragma Loop_Variant (Increases => Tail);
                     Tail := Tail + 1;
                  end loop;
                  if Tail < Offset and then Raw (Raw'First + Tail) = 47 then
                     if Len (Data, Files) > 0 then
                        for I in E.Count range 0 .. Len (Data, Files) - 1 loop
                           declare File : constant E.Span := Element (Data, Files, I);
                                   File_Path : constant E.Span := F (Data, File, "path"); begin
                              if Text_Valid (Data, File_Path)
                                and then Parts_Same (Raw, (Raw'First + Tail, Offset - Tail),
                                  Text_Bytes (Data, File_Path), (1, Text_Bytes (Data, File_Path)'Length))
                                and then (Text (Data, F (Data, File, "role"), "INTERPRETER")
                                  or else Text (Data, F (Data, File, "role"), "EXECUTABLE")
                                  or else Text (Data, F (Data, File, "role"), "EXTENSION")
                                  or else Text (Data, F (Data, File, "role"), "DATA"))
                              then Found := True; exit; end if;
                           end;
                        end loop;
                     end if;
                     if not Found then return False; end if;
                  end if;
               end;
               if Offset < Raw'Length then Offset := Offset + 1; end if;
            end;
         end loop;
      end;
      return True;
   end Maps_Match;
   function Process_Image_Matches (Data : E.Bytes; Source, Inventory : E.Span) return Boolean
     with Global => null
   is
      Files : constant E.Span := F (Data, Inventory, "current_source_files");
   begin
      if Len (Data, Files) > 0 then
         for I in E.Count range 0 .. Len (Data, Files) - 1 loop
            declare File : constant E.Span := Element (Data, Files, I); begin
               if Same (Data, F (Data, File, "path"), F (Data, Source, "image")) then
                  return (Text (Data, F (Data, File, "role"), "INTERPRETER") or else Text (Data, F (Data, File, "role"), "EXECUTABLE"))
                    and then Same (Data, F (Data, File, "raw"), F (Data, Source, "image_bytes"));
               end if;
            end;
         end loop;
      end if;
      return False;
   end Process_Image_Matches;
   function Process_Cgroup_Matches (Data : E.Bytes; Raw, Native : E.Span) return Boolean is
   begin
      if not Bytes_Valid (Data, Raw) or else not Bytes_Valid (Data, Native) then return False; end if;
      declare
         Source : constant E.Bytes := Bytes (Data, Raw);
         Projected : constant E.Bytes := Bytes (Data, Native);
      begin
         if Projected'Length = 0 or else Source'Length /= Projected'Length + 4
           or else Source (Source'First) /= 48 or else Source (Source'First + 1) /= 58
           or else Source (Source'First + 2) /= 58 or else Source (Source'Last) /= 10
           or else Projected (Projected'First) /= 47 then return False; end if;
         for I in E.Count range 0 .. Projected'Length - 1 loop
            if Source (Source'First + 3 + I) /= Projected (Projected'First + I)
              or else Projected (Projected'First + I) = 10 then return False; end if;
         end loop;
         return True;
      end;
   end Process_Cgroup_Matches;
   function Process_Matches (Data : E.Bytes; Item, Inventory, Namespace, Unit, Invocation : E.Span) return Boolean
     with Global => null
   is
      Observation : constant E.Span := F (Data, Item, "observation");
      Source : constant E.Span := F (Data, Item, "raw");
      Before : constant E.Span := F (Data, Source, "raw");
      After : constant E.Span := F (Data, Source, "after");
      Descriptor_Id : constant E.Span := Descriptor (Data, Inventory, F (Data, Item, "descriptor"));
      Parent : constant E.Span := F (Data, Source, "parent_stat");
      Parent_After : constant E.Span := F (Data, Source, "parent_after");
      Role : constant E.Span := Role_Entry (Data, Inventory, F (Data, Item, "descriptor"));
      Fd : constant E.Span := F (Data, Role, (if Is_None (Data, F (Data, Role, "worker_fd")) then "front_fd" else "worker_fd"));
      Wait_Item : constant E.Span := F (Data, Item, "wait");
      Before_Status : constant E.Span := F (Data, Before, "status");
      After_Status : constant E.Span := F (Data, After, "status");
      Before_Stat : constant E.Span := F (Data, Before, "stat");
      After_Stat : constant E.Span := F (Data, After, "stat");
      Pidfd_Item : constant E.Span := F (Data, Observation, "raw_pidfd_info");
   begin
      if Is_None (Data, F (Data, Item, "descriptor")) then
         return Is_None (Data, F (Data, Item, "poll")) and then Is_None (Data, Observation) and then Is_None (Data, Source);
      end if;
      if not Bytes_Valid (Data, F (Data, Descriptor_Id, "fdinfo")) or else not Bytes_Valid (Data, Wait_Item) then return False; end if;
      if not Same (Data, F (Data, F (Data, Item, "poll"), "source"), F (Data, Inventory, "current_source")) then return False; end if;
      if not Poll_Matches (Data, Item, F (Data, Item, "wait"), Fd) then return False; end if;
      declare Wait : constant E.Bytes := Bytes (Data, Wait_Item); begin
         if Wait = [80,73,68,70,68,95,84,69,82,77,73,78,65,76] then
            return Is_None (Data, Observation) and then Stable_Identity (Data, Descriptor_Id, F (Data, Source, "identity"))
              and then Same (Data, F (Data, Source, "actual_pidfd_wait"), F (Data, Item, "wait"))
              and then Same (Data, F (Data, Source, "full_fdinfo"), F (Data, F (Data, Source, "identity"), "fdinfo"))
              and then Same (Data, F (Data, Source, "full_fdinfo"), F (Data, Descriptor_Id, "fdinfo"));
         elsif Wait /= [80,73,68,70,68,95,76,73,86,69] then return False; end if;
      end;
      if not R.Archive_Record_Is (Data, Observation, "ProcessObservation")
        or else not Stable_Identity (Data, Descriptor_Id, F (Data, Source, "worker_pidfd_identity"))
        or else not Stable_Identity (Data, Namespace, F (Data, Source, "namespace_identity"))
        or else not Stable_Identity (Data, F (Data, F (Data, Inventory, "current_descriptors"), "host_proc"), F (Data, Source, "host_proc_identity"))
        or else not Same (Data, F (Data, Source, "source"), F (Data, Inventory, "current_source"))
        or else not Same (Data, F (Data, Observation, "actual_unit"), Unit)
        or else not Same (Data, F (Data, Observation, "invocation"), Invocation)
        or else not Same (Data, F (Data, Observation, "raw_status"), F (Data, Before, "status"))
        or else not Same (Data, F (Data, Observation, "raw_stat"), F (Data, Before, "stat"))
        or else not Same (Data, F (Data, Observation, "raw_cgroup"), F (Data, Before, "cgroup"))
        or else not Process_Cgroup_Matches (Data, F (Data, Before, "cgroup"), F (Data, Observation, "cgroup"))
        or else not Same (Data, F (Data, Observation, "raw_maps"), F (Data, Before, "maps"))
        or else not Maps_Match (Data, F (Data, Before, "maps"), Inventory)
        or else not Process_Image_Matches (Data, Source, Inventory)
        or else not Namespace_Matches (Data, F (Data, Observation, "namespace"), Namespace)
        or else not Hash_Field (Data, F (Data, Inventory, "installation_json"), F (Data, Observation, "source_lease"))
        or else not JSON_Source_Value_Matches (Data, F (Data, Inventory, "installation_json"), F (Data, Inventory, "installation_scoped"), True)
        or else not Scoped_Record_Matches (Data, F (Data, Inventory, "installation_scoped"), F (Data, F (Data, Inventory, "frame"), "installation"))
        or else not Same (Data, F (Data, Observation, "raw_cmdline"), F (Data, Before, "cmdline"))
        or else not Field_Same (Data, Before, After, "cgroup") or else not Field_Same (Data, Before, After, "maps")
        or else not Field_Same (Data, Before, After, "cmdline")
        or else not Bytes_Valid (Data, Before_Status) or else not Bytes_Valid (Data, After_Status)
        or else not Bytes_Valid (Data, Before_Stat) or else not Bytes_Valid (Data, After_Stat)
        or else not Bytes_Valid (Data, Parent) or else not Bytes_Valid (Data, Parent_After)
        or else not Bytes_Valid (Data, Pidfd_Item)
      then return False; end if;
      declare
         Status : constant E.Bytes := Bytes (Data, Before_Status);
         Later_Status : constant E.Bytes := Bytes (Data, After_Status);
         Stat : constant E.Bytes := Bytes (Data, Before_Stat);
         Later_Stat : constant E.Bytes := Bytes (Data, After_Stat);
         Parent_Stat : constant E.Bytes := Bytes (Data, Parent);
         Parent_Last : constant E.Bytes := Bytes (Data, Parent_After);
         Pidfd : constant E.Bytes := Bytes (Data, Pidfd_Item);
         Pid : constant Big_Integer := Number (Data, F (Data, Observation, "host_pid"));
         Ppid : constant Big_Integer := Number (Data, F (Data, Observation, "parent_pid"));
         Start : constant Big_Integer := Number (Data, F (Data, Observation, "start_tick"));
      begin
         if Pid <= To_Big_Integer (0) or else Ppid < To_Big_Integer (0) or else Start < To_Big_Integer (0)
           or else Decimal (Status, Word (Status, Line (Status, "Pid", 58), 1)) /= Pid
           or else Decimal (Later_Status, Word (Later_Status, Line (Later_Status, "Pid", 58), 1)) /= Pid
           or else Decimal (Status, Word (Status, Line (Status, "PPid", 58), 1)) /= Ppid
           or else Decimal (Later_Status, Word (Later_Status, Line (Later_Status, "PPid", 58), 1)) /= Ppid
           or else Decimal (Pidfd, Word (Pidfd, Line (Pidfd, "Pid", 58), 1)) /= Pid
           or else Stat_Number (Stat, 1) /= Pid or else Stat_Number (Later_Stat, 1) /= Pid
           or else Stat_Number (Stat, 4) /= Ppid or else Stat_Number (Later_Stat, 4) /= Ppid
           or else Stat_Number (Stat, 22) /= Start or else Stat_Number (Later_Stat, 22) /= Start
           or else Stat_Number (Parent_Stat, 1) /= Ppid or else Stat_Number (Parent_Last, 1) /= Ppid
           or else Stat_Number (Parent_Stat, 22) /= Number (Data, F (Data, Observation, "parent_start_tick"))
           or else Stat_Number (Parent_Last, 22) /= Number (Data, F (Data, Observation, "parent_start_tick"))
           or else not Parts_Same (Status, Line (Status, "NSpid", 58), Later_Status, Line (Later_Status, "NSpid", 58))
           or else Word (Status, Line (Status, "Uid", 58), 5).Length /= 0
           or else Word (Status, Line (Status, "Gid", 58), 5).Length /= 0
           or else Word (Later_Status, Line (Later_Status, "Uid", 58), 5).Length /= 0
           or else Word (Later_Status, Line (Later_Status, "Gid", 58), 5).Length /= 0
         then return False; end if;
         for I in Positive range 1 .. 4 loop
            if Decimal (Status, Word (Status, Line (Status, "Uid", 58), I)) /= Decimal (Later_Status, Word (Later_Status, Line (Later_Status, "Uid", 58), I))
              or else Decimal (Status, Word (Status, Line (Status, "Gid", 58), I)) /= Decimal (Later_Status, Word (Later_Status, Line (Later_Status, "Gid", 58), I))
              or else Decimal (Status, Word (Status, Line (Status, "Uid", 58), I)) < To_Big_Integer (0)
              or else Decimal (Status, Word (Status, Line (Status, "Gid", 58), I)) < To_Big_Integer (0)
            then return False; end if;
         end loop;
         return Number (Data, F (Data, Observation, "real_uid")) = Decimal (Status, Word (Status, Line (Status, "Uid", 58), 1))
           and then Number (Data, F (Data, Observation, "effective_uid")) = Decimal (Status, Word (Status, Line (Status, "Uid", 58), 2))
           and then Number (Data, F (Data, Observation, "saved_uid")) = Decimal (Status, Word (Status, Line (Status, "Uid", 58), 3))
           and then Number (Data, F (Data, Observation, "real_gid")) = Decimal (Status, Word (Status, Line (Status, "Gid", 58), 1))
           and then Number (Data, F (Data, Observation, "effective_gid")) = Decimal (Status, Word (Status, Line (Status, "Gid", 58), 2))
           and then Number (Data, F (Data, Observation, "saved_gid")) = Decimal (Status, Word (Status, Line (Status, "Gid", 58), 3));
      end;
   end Process_Matches;

   function Rights_Matches (Data : E.Bytes; Receipt, Fd : E.Span; Sending : Boolean) return Boolean
     with Global => null
   is
      Sender : constant E.Span := F (Data, Receipt, "sender");
   begin
      return Bytes_Valid (Data, Sender)
        and then Bytes (Data, Sender)'Length = 12
        and then Worldline.Scoped_Capture_Namespace_Projection.FD_Receipt_Matches
          (Data, Receipt, Fd, Sender, Sending);
   end Rights_Matches;
   function Source_Files_Match (Data : E.Bytes; Inventory : E.Span) return Boolean
     with Global => null
   is
      Frame : constant E.Span := F (Data, Inventory, "frame");
      Before : constant E.Span := F (Data, Frame, "source_files");
      Current : constant E.Span := F (Data, Inventory, "current_source_files");
   begin
      if not Sequence_Valid (Data, Before) or else not Sequence_Valid (Data, Current)
        or else Len (Data, Before) /= Len (Data, Current)
        or else not Field_Same (Data, F (Data, Frame, "source"), F (Data, Inventory, "current_source"), "envelope_path")
        or else not Field_Same (Data, F (Data, Frame, "source"), F (Data, Inventory, "current_source"), "envelope_bytes_hex")
        or else not Field_Same (Data, F (Data, Frame, "source"), F (Data, Inventory, "current_source"), "interpreter")
      then return False; end if;
      if Len (Data, Before) > 0 then
         for I in E.Count range 0 .. Len (Data, Before) - 1 loop
            declare O : constant E.Span := Element (Data, Before, I); C : constant E.Span := Element (Data, Current, I); begin
               if not Field_Same (Data, O, C, "path") or else not Field_Same (Data, O, C, "role")
                 or else not Field_Same (Data, O, C, "descriptor") or else not Field_Same (Data, O, C, "raw")
                 or else not Same (Data, F (Data, C, "raw"), F (Data, C, "lease_raw"))
                 or else not Stable_Identity (Data, F (Data, C, "identity"), F (Data, C, "named"))
                 or else not Stable_Identity (Data, F (Data, C, "identity"), Descriptor (Data, Inventory, F (Data, C, "descriptor")))
               then return False; end if;
            end;
         end loop;
      end if;
      return True;
   end Source_Files_Match;
   function Reconstruction_Matches (Data : E.Bytes; Inventory : E.Span) return Boolean
     with Global => null
   is
      Reconstruction : constant E.Span := F (Data, Inventory, "reconstruction");
      Frame : constant E.Span := F (Data, Inventory, "frame");
      Original : constant E.Span := F (Data, Reconstruction, "original_frame");
      Duplicates : constant E.Span := F (Data, Reconstruction, "duplicates");
      Roles : constant E.Span := F (Data, Frame, "original_roles");
      Original_Inventory : constant E.Span := F (Data, Reconstruction, "original_inventory");
      Registry : constant E.Span := F (Data, Reconstruction, "service_registry");
      Extensions : constant E.Span := F (Data, Frame, "extensions");
   begin
      if Is_None (Data, Reconstruction) then return True; end if;
      if not Sequence_Valid (Data, Duplicates) or else Len (Data, Duplicates) /= Len (Data, Roles)
        or else not Field_Same (Data, Frame, Original, "installation")
        or else not Field_Same (Data, Frame, Original, "source_files")
        or else not Field_Same (Data, Frame, Original, "lease_locks")
        or else not Field_Same (Data, Frame, Original, "rows")
        or else not Field_Same (Data, Frame, Original, "packet")
        or else not Same (Data, Original, F (Data, Original_Inventory, "frame"))
        or else (not (F (Data, Frame, "retained_roles").Length = 0 and then F (Data, Original, "retained_roles").Length = 0)
          and then not Field_Same (Data, Frame, Original, "retained_roles"))
        or else (not (F (Data, Frame, "closed_roles").Length = 0 and then F (Data, Original, "closed_roles").Length = 0)
          and then not Field_Same (Data, Frame, Original, "closed_roles"))
        or else (Len (Data, Registry) > 0 and then Len (Data, Registry) /= Len (Data, Extensions))
        or else (Len (Data, Registry) = 0 and then Len (Data, Extensions) > 0
          and then not Field_Same (Data, Frame, Original, "extensions"))
      then return False; end if;
      if Len (Data, Registry) > 0 then
         for I in E.Count range 0 .. Len (Data, Extensions) - 1 loop
            declare
               Extension : constant E.Span := Element (Data, Extensions, I);
               Registered : constant E.Span := Element (Data, Registry, I);
               Prefix : constant String := "extension/";
               Descriptor_Text : constant E.Span := F (Data, Extension, "descriptor");
               Role_Text : constant E.Span := F (Data, Registered, "role");
            begin
               if not Text_Valid (Data, Descriptor_Text)
                 or else not Text_Valid (Data, Role_Text)
                 or else not Same (Data, F (Data, Extension, "source_fd"), F (Data, Registered, "fd"))
                 or else not Stable_Identity (Data, F (Data, Extension, "identity"), F (Data, Registered, "identity"))
               then return False; end if;
               declare
                  Name : constant E.Bytes := Text_Bytes (Data, Descriptor_Text);
                  Suffix : constant E.Bytes := Text_Bytes (Data, Role_Text);
               begin
                  if Name'Length /= Prefix'Length + Suffix'Length then return False; end if;
                  for J in E.Count range 0 .. Prefix'Length - 1 loop
                     if Name (Name'First + J) /= Q.Byte (Character'Pos (Prefix (Prefix'First + Natural (J)))) then return False; end if;
                  end loop;
                  if Suffix'Length > 0 then
                     for J in E.Count range 0 .. Suffix'Length - 1 loop
                        if Name (Name'First + Prefix'Length + J) /= Suffix (Suffix'First + J) then return False; end if;
                     end loop;
                  end if;
               end;
            end;
         end loop;
      end if;
      if Len (Data, Duplicates) > 0 then
         for I in E.Count range 0 .. Len (Data, Duplicates) - 1 loop
            declare
               Item : constant E.Span := Element (Data, Duplicates, I);
               Role : constant E.Span := Element (Data, Roles, I);
               Dup : constant E.Span := F (Data, Item, "dup");
               Kcmp : constant E.Span := F (Data, Item, "kcmp");
               Name : constant E.Span := F (Data, Item, "role");
               Old : E.Span := Member_Value (Data, F (Data, Original, "descriptors"), Name);
               Origin_Role : constant E.Span := Role_Entry (Data, Original_Inventory, Name);
               Origin_Fd : E.Span := F (Data, Origin_Role,
                 (if Is_None (Data, F (Data, Origin_Role, "worker_fd")) then "front_fd" else "worker_fd"));
            begin
               if Len (Data, Registry) > 0 and then Len (Data, Extensions) > 0 then
                  for J in E.Count range 0 .. Len (Data, Extensions) - 1 loop
                     declare Extension : constant E.Span := Element (Data, Extensions, J); begin
                        if Same (Data, Name, F (Data, Extension, "descriptor")) then
                           if Origin_Role.Length > 0 then
                              declare
                                 Rebinds : constant E.Span := F (Data, Reconstruction, "extension_rebinds");
                                 Rebind : E.Span := (1, 0);
                              begin
                                 if Len (Data, Rebinds) > 0 then
                                    for K in E.Count range 0 .. Len (Data, Rebinds) - 1 loop
                                       if Same (Data, Name, F (Data, Element (Data, Rebinds, K), "role")) then
                                          if Rebind.Length > 0 then return False; end if;
                                          Rebind := Element (Data, Rebinds, K);
                                       end if;
                                    end loop;
                                 end if;
                                 declare Link : constant E.Span := F (Data, Rebind, "kcmp"); begin
                                    if not Same (Data, F (Data, Rebind, "original_fd"), Origin_Fd)
                                      or else not Same (Data, F (Data, Rebind, "registry_fd"), F (Data, Extension, "source_fd"))
                                      or else not Stable_Identity (Data, F (Data, Rebind, "original_identity"), F (Data, Origin_Role, "current"))
                                      or else not Stable_Identity (Data, F (Data, Rebind, "registry_identity"), F (Data, Extension, "identity"))
                                      or else not Syscall (Data, Link, "kcmp", 0)
                                      or else not Same (Data, F (Data, Link, "source"), F (Data, Reconstruction, "source"))
                                      or else not Same (Data, F (Data, F (Data, Link, "args"), "idx1"), Origin_Fd)
                                      or else not Same (Data, F (Data, F (Data, Link, "args"), "idx2"), F (Data, Extension, "source_fd"))
                                      or else not Same (Data, F (Data, F (Data, Link, "args"), "pid1"), F (Data, F (Data, Role, "front_actor"), "pid"))
                                      or else not Same (Data, F (Data, F (Data, Link, "args"), "pid2"), F (Data, F (Data, Role, "front_actor"), "pid"))
                                      or else not Is_Number (Data, F (Data, F (Data, Link, "args"), "type"), 0)
                                    then return False; end if;
                                 end;
                              end;
                           end if;
                           Old := F (Data, Extension, "identity");
                           Origin_Fd := F (Data, Extension, "source_fd"); exit;
                        end if;
                     end;
                  end loop;
               end if;
               if Old.Length = 0 then
                  if Len (Data, Extensions) > 0 then
                     for J in E.Count range 0 .. Len (Data, Extensions) - 1 loop
                        declare Extension : constant E.Span := Element (Data, Extensions, J); begin
                           if Same (Data, Name, F (Data, Extension, "descriptor")) then
                              Old := F (Data, Extension, "identity");
                              Origin_Fd := F (Data, Extension, "source_fd"); exit;
                           end if;
                        end;
                     end loop;
                  end if;
               end if;
               if not Same (Data, Name, F (Data, Role, "role"))
                 or else not Stable_Identity (Data, F (Data, Item, "origin"), Old)
                 or else not Same (Data, Origin_Fd, F (Data, F (Data, Dup, "args"), "fd"))
                 or else (Origin_Role.Length > 0 and then
                   (not Stable_Identity (Data, F (Data, Origin_Role, "current"), F (Data, Item, "origin"))
                    or else not Stable_Identity (Data, Descriptor (Data, Original_Inventory, Name), F (Data, Item, "origin"))))
                 or else not Stable_Identity (Data, F (Data, Item, "current"), F (Data, Role, "identity"))
                 or else not Text (Data, F (Data, Dup, "call"), "dup")
                 or else not Is_Number (Data, F (Data, Dup, "errno"), 0)
                 or else not Same (Data, F (Data, Dup, "result"), F (Data, Role, "fd"))
                 or else not Same (Data, F (Data, F (Data, Dup, "args"), "role"), Name)
                 or else not Same (Data, F (Data, Dup, "source"), F (Data, Reconstruction, "source"))
                 or else not Syscall (Data, Kcmp, "kcmp", 0)
                 or else not Same (Data, F (Data, Kcmp, "source"), F (Data, Reconstruction, "source"))
                 or else not Same (Data, F (Data, F (Data, Kcmp, "args"), "idx1"), F (Data, F (Data, Dup, "args"), "fd"))
                 or else not Same (Data, F (Data, F (Data, Kcmp, "args"), "idx2"), F (Data, Role, "fd"))
                 or else not Is_Number (Data, F (Data, F (Data, Kcmp, "args"), "type"), 0)
                 or else not Same (Data, F (Data, F (Data, Kcmp, "args"), "pid1"), F (Data, F (Data, Role, "front_actor"), "pid"))
                 or else not Same (Data, F (Data, F (Data, Kcmp, "args"), "pid2"), F (Data, F (Data, Role, "front_actor"), "pid"))
               then return False; end if;
            end;
         end loop;
      end if;
      return True;
   end Reconstruction_Matches;
   function Role_Roster_Matches (Data : E.Bytes; Inventory : E.Span) return Boolean is
      Frame : constant E.Span := F (Data, Inventory, "frame");
      Original : constant E.Span := F (Data, Frame, "original_roles");
      Current : constant E.Span := F (Data, Inventory, "roles");
      Before : constant E.Span := F (Data, Frame, "descriptors");
      After : constant E.Span := F (Data, Inventory, "current_descriptors");
      Broker : constant E.Span := F (Data, Inventory, "sender_role_roster");
      Sender_Roles : constant E.Span := F (Data, Broker, "roles");
   begin
      if not Text (Data, F (Data, Frame, "schema"), "worldline.complete-owned-scoped-descriptor-roster-v1")
        or else not Sequence_Valid (Data, Original) or else not Sequence_Valid (Data, Current)
        or else Len (Data, Original) /= Len (Data, Current)
        or else E.Array_Length (Data, Members (Data, Before)) /= Len (Data, Original)
        or else E.Array_Length (Data, Members (Data, After)) /= Len (Data, Original)
      then return False; end if;
      if Len (Data, Original) > 0 then
         for I in E.Count range 0 .. Len (Data, Original) - 1 loop
            declare
               O : constant E.Span := Element (Data, Original, I);
               C : constant E.Span := Element (Data, Current, I);
               Name : constant E.Span := F (Data, O, "role");
               Kcmp : E.Span := F (Data, C, "kcmp");
               Kcmp_Source : E.Span := F (Data, Inventory, "current_source");
               Kcmp_Pid : E.Span := F (Data, F (Data, Inventory, "current_actor"), "pid");
               Kcmp_Origin_Pid : E.Span := F (Data, F (Data, O, "front_actor"), "pid");
               Received : constant Boolean := not Is_None (Data, F (Data, C, "worker_fd"));
            begin
               if not Same (Data, Name, F (Data, C, "role"))
                 or else not Stable_Identity (Data, F (Data, O, "identity"), Member_Value (Data, Before, Name))
                 or else not Stable_Identity (Data, F (Data, C, "current"), Member_Value (Data, After, Name))
                 or else not Stable_Identity (Data, F (Data, C, "origin"), F (Data, O, "identity"))
                 or else not Stable_Identity (Data, F (Data, C, "current"), F (Data, C, "origin"))
                 or else not Syscall (Data, F (Data, C, "fstat"), "fstat", 0)
                 or else not Stable_Identity (Data, F (Data, F (Data, C, "fstat"), "identity"), F (Data, C, "current"))
                 or else not Same (Data, F (Data, O, "front_actor"), F (Data, C, "front_actor"))
                 or else not Same (Data, F (Data, O, "worker_pidfd"), F (Data, C, "worker_pidfd"))
                 or else not Field_Same (Data, O, C, "lock_path")
               then return False; end if;
               if Received then
                  declare
                     Send : constant E.Span := Member_Value (Data, F (Data, Inventory, "sender_receipts"), Name);
                     Receive : constant E.Span := Member_Value (Data, F (Data, Inventory, "receive_receipts"), Name);
                  begin
                     if not Rights_Matches (Data, Send, F (Data, O, "fd"), True)
                       or else Len (Data, Receive) /= 1
                       or else not Rights_Matches (Data, Element (Data, Receive, 0), F (Data, C, "worker_fd"), False)
                       or else not Worldline.Scoped_Capture_Namespace_Projection.SCM_Credentials_Match
                         (Data, Send, Element (Data, Receive, 0), F (Data, O, "front_actor"),
                          F (Data, Inventory, "current_actor"), F (Data, Inventory, "namespace_source"))
                     then return False; end if;
                  end;
                  if not Is_None (Data, Broker) then
                     if Len (Data, Sender_Roles) /= Len (Data, Original)
                       or else not Same (Data, F (Data, Element (Data, Sender_Roles, I), "role"), Name)
                       or else not Same (Data, F (Data, Element (Data, Sender_Roles, I), "front_fd"), F (Data, O, "fd"))
                       or else not Same (Data, F (Data, Element (Data, Sender_Roles, I), "worker_fd"), F (Data, C, "worker_fd"))
                       or else not Stable_Identity (Data, F (Data, Element (Data, Sender_Roles, I), "origin"), F (Data, O, "identity"))
                       or else not Stable_Identity (Data, F (Data, Element (Data, Sender_Roles, I), "current"), F (Data, C, "current"))
                       or else not Field_Same (Data, F (Data, Broker, "actor"), F (Data, O, "front_actor"), "pid")
                       or else not Field_Same (Data, F (Data, Broker, "actor"), F (Data, O, "front_actor"), "boot")
                       or else not Field_Same (Data, F (Data, Broker, "actor"), F (Data, O, "front_actor"), "start_tick")
                       or else not Field_Same (Data, F (Data, Broker, "actor"), F (Data, O, "front_actor"), "credentials")
                       or else not Stable_Identity (Data, F (Data, Broker, "worker_pidfd"), F (Data, O, "worker_pidfd"))
                       or else not Field_Same (Data, F (Data, Broker, "source"), F (Data, Frame, "source"), "envelope_path")
                       or else not Field_Same (Data, F (Data, Broker, "source"), F (Data, Frame, "source"), "envelope_bytes_hex")
                       or else not Field_Same (Data, F (Data, Broker, "source"), F (Data, Frame, "source"), "interpreter")
                     then return False; end if;
                     Kcmp := F (Data, Element (Data, Sender_Roles, I), "kcmp");
                     Kcmp_Source := F (Data, Broker, "source"); Kcmp_Pid := F (Data, Broker, "worker_host_pid");
                     if not Is_None (Data, F (Data, Broker, "reverse_host_broker")) then
                        if not Worldline.Scoped_Capture_Namespace_Projection.Reverse_Host_Matches
                          (Data, Inventory, Broker) then return False; end if;
                        Kcmp_Origin_Pid := F (Data, F (Data, Broker, "reverse_host_broker"), "sender_host_pid");
                     end if;
                  end if;
                  if not Syscall (Data, Kcmp, "kcmp", 0)
                    or else not Same (Data, F (Data, Kcmp, "source"), Kcmp_Source)
                    or else not Same (Data, F (Data, F (Data, Kcmp, "args"), "pid2"), Kcmp_Pid)
                    or else not Is_Number (Data, F (Data, F (Data, Kcmp, "args"), "type"), 0)
                    or else not Same (Data, F (Data, F (Data, Kcmp, "args"), "pid1"), Kcmp_Origin_Pid)
                    or else not Same (Data, F (Data, F (Data, Kcmp, "args"), "idx1"), F (Data, O, "fd"))
                    or else not Same (Data, F (Data, F (Data, Kcmp, "args"), "idx2"), F (Data, C, "worker_fd"))
                  then return False; end if;
                  if not Is_None (Data, F (Data, C, "lock_path")) and then
                    (not Syscall (Data, F (Data, C, "flock"), "flock", 0)
                     or else not Is_Number (Data, F (Data, F (Data, F (Data, C, "flock"), "args"), "operation"), 6)
                     or else not Same (Data, F (Data, F (Data, F (Data, C, "flock"), "args"), "fd"), F (Data, C, "worker_fd")))
                  then return False; end if;
               elsif not Is_None (Data, Kcmp) or else not Same (Data, F (Data, C, "front_fd"), F (Data, O, "fd")) then return False; end if;
               if I > 0 then
                  for J in E.Count range 0 .. I - 1 loop
                     if Same (Data, Name, F (Data, Element (Data, Original, J), "role")) then return False; end if;
                  end loop;
               end if;
            end;
         end loop;
      end if;
      declare Closed : constant E.Span := F (Data, Frame, "closed_roles"); begin
         if Closed.Length > 0 and then E.Array_Length (Data, Members (Data, Closed)) > 0 then
            for I in E.Count range 0 .. E.Array_Length (Data, Members (Data, Closed)) - 1 loop
               declare
                  Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, Members (Data, Closed), I), E.Finalization);
                  Closure : constant E.Span := E.Array_Element (Data, Pair.Children, 1);
                  Before_Inventory : constant E.Span := F (Data, Closure, "before_inventory");
               begin
                  if Before_Inventory.Length >= Inventory.Length
                    or else not Role_Roster_Matches (Data, Before_Inventory)
                  then return False; end if;
               end;
            end loop;
         end if;
      end;
      return Source_Files_Match (Data, Inventory) and then Reconstruction_Matches (Data, Inventory)
        and then Worldline.Scoped_Capture_Evolution_Projection.Closed_Roles_Match (Data, Inventory)
        and then Worldline.Scoped_Capture_Evolution_Projection.Evolution_Matches (Data, Inventory)
        and then
          ((F (Data, Inventory, "initial_root_transport").Length = 0
            and then Worldline.Scoped_Capture_Evolution_Projection.Subject_Transport_Matches (Data, Inventory))
           or else (F (Data, Inventory, "initial_root_transport").Length > 0
             and then F (Data, Inventory, "subject_transport").Length = 0
             and then Worldline.Scoped_Capture_Evolution_Projection.Initial_Root_Transport_Matches (Data, Inventory)));
   end Role_Roster_Matches;

   function Lossless_Matches (Data : E.Bytes; Original, Wrapped : E.Span) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Original.Length)
   is
      V : constant E.View := E.Decode (Data, Original, E.Operation);
      Kind : constant E.Span := F (Data, Wrapped, "kind");
      Value : constant E.Span := F (Data, Wrapped, "value");
      Magnitude : constant E.Span := F (Data, Wrapped, "magnitude");
   begin
      if not RA.Source_Valid (Data, Original, False) or else not RA.Source_Valid (Data, Wrapped, False) then return False; end if;
      if Is_None (Data, Original) then return Text (Data, Kind, "NoneType") and then Is_None (Data, Value);
      elsif Bytes_Valid (Data, Original) then return Text (Data, Kind, "bytes") and then Text_Valid (Data, Value)
        and then Hex_Matches (Bytes (Data, Original), Text_Bytes (Data, Value));
      elsif Integer_Valid (Data, Original) then
         return Text (Data, Kind, "int-magnitude") and then R.Archive_Boolean_Is (Data, F (Data, Wrapped, "negative"), R.Archive_Integer_Negative (Data, Original))
           and then Text_Valid (Data, Magnitude)
           and then Hex_Matches (R.Archive_Integer_Magnitude (Data, Original), Text_Bytes (Data, Magnitude));
      elsif V.Form = E.Float_Value and then E.Bytes_Valid (Data, V.Payload) then
         return Text (Data, Kind, "float-binary") and then Text_Valid (Data, Value)
           and then Hex_Matches (E.Materialize (Data, V.Payload), Text_Bytes (Data, Value));
      elsif Text_Valid (Data, Original) then return Text (Data, Kind, "str") and then Same (Data, Original, Value);
      elsif V.Form = E.Boolean_Value then return Text (Data, Kind, "bool") and then Same (Data, Original, Value);
      elsif Sequence_Valid (Data, Original) then
         if not Text (Data, Kind, (if V.Form = E.List_Value then "list" else "tuple"))
           or else not Sequence_Valid (Data, Value) or else Len (Data, Original) /= Len (Data, Value)
         then return False; end if;
         if Len (Data, Original) > 0 then
            for I in E.Count range 0 .. Len (Data, Original) - 1 loop
               if not Lossless_Matches (Data, Element (Data, Original, I), Element (Data, Value, I)) then return False; end if;
            end loop;
         end if;
         return True;
      elsif V.Form = E.Object_Value and then Text (Data, Kind, "dict") then
         declare
            M : constant E.Span := Members (Data, Original);
            Count : constant E.Count := E.Array_Length (Data, M);
         begin
            if Count /= E.Array_Length (Data, Members (Data, Value)) then return False; end if;
            if Count > 0 then
               for I in E.Count range 0 .. Count - 1 loop
                  declare
                     Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, M, I), E.Finalization);
                     Key : constant E.Span := E.Array_Element (Data, Pair.Children, 0);
                  begin
                     if not Lossless_Matches (Data, E.Array_Element (Data, Pair.Children, 1), Member_Value (Data, Value, Key)) then return False; end if;
                  end;
               end loop;
            end if;
            return True;
         end;
      else return False; end if;
   end Lossless_Matches;

   function UUID_Matches (Data : E.Bytes; Id, Value : E.Span) return Boolean
     with Global => null
   is
   begin
      if not Bytes_Valid (Data, Id) or else not Text_Valid (Data, Value) then return False; end if;
      declare
         Raw : constant E.Bytes := Bytes (Data, Id);
         Spelling : constant E.Bytes := Text_Bytes (Data, Value);
         Position : E.Count := 0;
      begin
         if Raw'Length /= 16 or else Spelling'Length /= 36 then return False; end if;
         for I in Raw'Range loop
            pragma Loop_Invariant (Position = 2 * (I - Raw'First) +
              (if I - Raw'First <= 4 then 0 elsif I - Raw'First <= 6 then 1
               elsif I - Raw'First <= 8 then 2 elsif I - Raw'First <= 10 then 3 else 4));
            if Position in 8 | 13 | 18 | 23 then
               if Spelling (Spelling'First + Position) /= 45 then return False; end if;
               Position := Position + 1;
            end if;
            if Nibble (Spelling (Spelling'First + Position)) < 0 or else Nibble (Spelling (Spelling'First + Position + 1)) < 0
              or else Integer (Raw (I)) /= Nibble (Spelling (Spelling'First + Position)) * 16 + Nibble (Spelling (Spelling'First + Position + 1))
            then return False; end if;
            Position := Position + 2;
         end loop;
         return Position = Spelling'Length;
      end;
   end UUID_Matches;
   function Current_History_Matches (Data : E.Bytes; Packet, Projection : E.Span) return Boolean
     with Global => null
   is
      Current : constant E.Span := F (Data, Packet, "current");
      Before : constant E.Span := F (Data, Packet, "before");
      Old_History : constant E.Span := F (Data, Packet, "history");
      History : constant E.Span := F (Data, Packet, "proposed_history");
      Advance : constant E.Span := F (Data, Projection, "context_advance");
      Frame : constant E.Span := F (Data, Advance, "frame");
      Model : constant E.Span := F (Data, Advance, "frame_model");
      Fields : constant E.Span := Members (Data, Frame);
   begin
      if Text (Data, F (Data, F (Data, Packet, "request"), "kind"), "ORDINARY") then
         return Field_Same (Data, Current, Before, "history_head") and then Advance.Length = 0;
      end if;
      if not Text (Data, F (Data, F (Data, Packet, "request"), "kind"), "ADVANCE_CONTEXT")
        or else not Sequence_Valid (Data, Old_History)
        or else not Sequence_Valid (Data, History)
        --  The original raised (Len + 1) exactly here; refuse.
        or else Len (Data, Old_History) = E.Count'Last
        or else Len (Data, History) /= Len (Data, Old_History) + 1
        or else not Same (Data, Frame, Element (Data, History, Len (Data, History) - 1))
        or else E.Array_Length (Data, Fields) /= 15
        or else E.Array_Length (Data, Members (Data, Model)) /= 15
        or else not Is_None (Data, F (Data, Model, "frame_head"))
        or else not Scoped_Record_Matches (Data, F (Data, Advance, "frame_scoped"), Model)
        or else not JSON_Matches (Data, F (Data, Advance, "frame_preimage"), F (Data, Advance, "frame_scoped"))
        or else not Hash_Field (Data, F (Data, Advance, "frame_preimage"), F (Data, Frame, "frame_head"))
        or else not Same (Data, F (Data, Frame, "frame_head"), F (Data, Current, "history_head"))
        or else not Same (Data, F (Data, Frame, "prior_frame"), F (Data, Before, "history_head"))
        or else Number (Data, F (Data, Frame, "first_epoch")) /= Number (Data, F (Data, Before, "resource_epoch")) + 1
      then return False; end if;
      if Len (Data, Old_History) > 0 then
         for I in E.Count range 0 .. Len (Data, Old_History) - 1 loop
            if not Same (Data, Element (Data, Old_History, I), Element (Data, History, I)) then return False; end if;
         end loop;
      end if;
      return Field_Same (Data, Frame, Model, "scope")
        and then Field_Same (Data, Frame, Model, "first_epoch")
        and then Field_Same (Data, Frame, Model, "universe_head")
        and then Field_Same (Data, Frame, Model, "prior_frame")
        and then Field_Same (Data, Frame, Model, "store_genesis")
        and then Field_Same (Data, Frame, Model, "store_id")
        and then Field_Same (Data, Frame, Model, "root_head")
        and then Field_Same (Data, Frame, Model, "prime")
        and then Field_Same (Data, Frame, Model, "root_count")
        and then Field_Same (Data, Frame, Model, "cause")
        and then Field_Same (Data, Frame, Model, "requester")
        and then Field_Same (Data, Frame, Model, "receipt")
        and then Field_Same (Data, Frame, Model, "catalogue_head")
        and then Field_Same (Data, Frame, Model, "observation_head")
        and then Field_Same (Data, Frame, Current, "scope")
        and then Field_Same (Data, Frame, Current, "universe_head")
        and then Field_Same (Data, Frame, Current, "store_genesis")
        and then Field_Same (Data, Frame, Current, "store_id")
        and then Field_Same (Data, Frame, Current, "root_head")
        and then Field_Same (Data, Frame, Current, "prime")
        and then Field_Same (Data, Frame, Current, "root_count")
        and then Field_Same (Data, Frame, Current, "cause")
        and then Field_Same (Data, Frame, Current, "requester")
        and then Field_Same (Data, Frame, Current, "receipt")
        and then Field_Same (Data, Frame, Current, "catalogue_head")
        and then Field_Same (Data, Frame, Current, "observation_head");
   end Current_History_Matches;

   function Current_Matches (Data : E.Bytes; Packet, Projection : E.Span) return Boolean
     with Global => null
   is
      C : constant E.Span := F (Data, Packet, "current");
      Scope : constant E.Span := F (Data, C, "scope");
      Source : constant E.Span := F (Data, Projection, "source");
      Universe : constant E.Span := F (Data, Source, "universe");
      Roster_Entry : constant E.Span := F (Data, Universe, "record");
      Policy : constant E.Span := F (Data, Roster_Entry, "policy");
      Config : constant E.Span := F (Data, Projection, "gate_config");
      Root : constant E.Span := F (Data, Projection, "root_value");
      Root_Fields : constant E.Span := F (Data, Root, "value");
      Catalogue : constant E.Span := F (Data, Projection, "catalogue");
      Entries : constant E.Span := F (Data, Catalogue, "entries");
      Prime : constant E.Span := F (Data, Source, "actual_prime");
      Owner : constant E.Span := F (Data, Source, "original_owner_genesis");
      Current_Prime : constant E.Span := F (Data, C, "prime");
      Found : Boolean := False;
   begin
      if not Text (Data, F (Data, Projection, "schema"), "worldline.complete-scoped-capture-source-v1")
        or else not Same (Data, C, F (Data, Projection, "current"))
        or else not Scoped_Record_Matches (Data, F (Data, Projection, "source_scoped"), Source)
        or else not Scoped_Record_Matches (Data, F (Data, Source, "scoped_before"), F (Data, Projection, "before_values"))
        or else not Same (Data, F (Data, Packet, "before"), F (Data, F (Data, Projection, "before_values"), "state"))
        or else not Same (Data, F (Data, Packet, "history"), F (Data, F (Data, Projection, "before_values"), "history"))
        or else not Same (Data, F (Data, Packet, "rows"), F (Data, F (Data, Projection, "before_values"), "rows"))
        or else not Same (Data, F (Data, Packet, "projection"), F (Data, F (Data, Projection, "before_values"), "projection"))
        or else not Same (Data, F (Data, Packet, "buckets"), F (Data, F (Data, Projection, "before_values"), "buckets"))
        or else not JSON_Matches (Data, F (Data, Projection, "source_json"), F (Data, Projection, "source_scoped"))
        or else not JSON_Matches (Data, F (Data, Source, "gate_config_raw"), Config)
        or else not JSON_Matches (Data, F (Data, Projection, "binding_json"), F (Data, Projection, "binding"))
        or else not JSON_Matches (Data, F (Data, Projection, "catalogue_json"), F (Data, Projection, "catalogue_encoded"))
        or else not Same (Data, F (Data, Projection, "catalogue_json"), F (Data, Source, "catalogue_raw"))
        or else not Same (Data, Catalogue, F (Data, Projection, "catalogue_encoded"))
        or else not JSON_Matches (Data, F (Data, Projection, "root_json"), Root)
        or else not Text (Data, F (Data, Root, "kind"), "dict")
        or else not Lossless_Matches (Data, F (Data, Source, "actual_store_genesis"), F (Data, Root_Fields, "store_genesis"))
        or else not Lossless_Matches (Data, F (Data, Source, "actual_store_id"), F (Data, Root_Fields, "store_id"))
        or else not Lossless_Matches (Data, F (Data, Source, "actual_roots"), F (Data, Root_Fields, "roots"))
        or else not Lossless_Matches (Data, Prime, F (Data, Root_Fields, "prime"))
        or else not Id_Hex (Data, F (Data, Scope, "universe"), F (Data, Universe, "universe_id"))
        or else not Id_Hex (Data, F (Data, Scope, "policy"), F (Data, Config, "policy_id"))
        or else not Id_Hex (Data, F (Data, Scope, "resource"), F (Data, Policy, "resource_id"))
        or else not Id_Hex (Data, F (Data, Scope, "authority"), F (Data, Policy, "authority_id"))
        or else not Field_Same (Data, Scope, Roster_Entry, "policy_epoch")
        or else not Same (Data, F (Data, Scope, "host"), F (Data, Source, "host_raw"))
        or else not Same (Data, F (Data, Scope, "boot"), F (Data, Source, "boot_raw"))
        or else not Id_Hex (Data, F (Data, C, "universe_head"), F (Data, Universe, "event_head"))
        or else not Id_Text (Data, F (Data, C, "store_genesis"), F (Data, Source, "actual_store_genesis"))
        or else not Id_Text (Data, F (Data, C, "store_id"), F (Data, Source, "actual_store_id"))
        or else not Sequence_Valid (Data, F (Data, Source, "actual_roots"))
        or else Number (Data, F (Data, C, "root_count")) /= Count_Number (Len (Data, F (Data, Source, "actual_roots")))
        or else not Field_Same (Data, C, F (Data, Packet, "before"), "resource_epoch")
        or else not Field_Same (Data, C, F (Data, Packet, "before"), "ledger_head")
        or else not Current_History_Matches (Data, Packet, Projection)
        or else not Hash_Field (Data, F (Data, Projection, "catalogue_json"), F (Data, C, "physical_head"))
        or else not Hash_Field (Data, F (Data, Projection, "catalogue_json"), F (Data, C, "catalogue_head"))
        or else not Hash_Field (Data, F (Data, Projection, "root_json"), F (Data, C, "root_head"))
        or else not Hash_Field (Data, F (Data, Projection, "source_json"), F (Data, C, "cause"))
        or else not Hash_Field (Data, F (Data, Projection, "source_json"), F (Data, C, "observation_head"))
        or else not Hash_Field (Data, F (Data, Projection, "binding_json"), F (Data, C, "requester"))
        or else not Hash_Field (Data, F (Data, Projection, "source_json"), F (Data, C, "receipt"), "WORLDLINE-scoped-current-source" & Character'Val (0))
        or else not Text (Data, F (Data, Catalogue, "schema"), "worldline.protected-physical-catalogue-v1")
        or else not Sequence_Valid (Data, Entries)
      then return False; end if;
      if Len (Data, Entries) > 0 then
         for I in E.Count range 0 .. Len (Data, Entries) - 1 loop
            declare P : constant E.Span := Element (Data, Entries, I); begin
               if Same (Data, F (Data, P, "scope_policy"), F (Data, Scope, "policy"))
                 and then Same (Data, F (Data, P, "scope_resource"), F (Data, Scope, "resource"))
               then
                  Found := True;
                  if not Same (Data, F (Data, P, "scope_unit"), F (Data, Scope, "unit")) then return False; end if;
               end if;
            end;
         end loop;
      end if;
      if not Found then return False; end if;
      if Is_None (Data, Prime) then
         return Is_None (Data, F (Data, C, "prime")) and then Text (Data, F (Data, Owner, "schema"), "worldline.owner-provisioned-empty-store-resource-context-v1")
           and then Field_Same (Data, Owner, F (Data, Source, "installation"), "installation_id")
           and then Same (Data, F (Data, Owner, "store_genesis"), F (Data, Source, "actual_store_genesis"))
           and then Same (Data, F (Data, Owner, "finalization_store_id"), F (Data, Source, "actual_store_id"))
           and then Field_Same (Data, Owner, Universe, "universe_id") and then Is_None (Data, F (Data, Owner, "prime"))
           and then Sequence_Valid (Data, F (Data, Owner, "roots")) and then Len (Data, F (Data, Owner, "roots")) = 0
           and then Id_Hex (Data, F (Data, Scope, "instance"), F (Data, Owner, "instance_id"))
           and then Same (Data, F (Data, Owner, "instance_id"), F (Data, Roster_Entry, "prime_worldline_id"));
      else
         return Bytes_Valid (Data, Current_Prime) and then Bytes (Data, Current_Prime)'Length = 16
           and then UUID_Matches (Data, Current_Prime, F (Data, Prime, "instance_id"))
           and then Digest_Matches (Bytes (Data, Current_Prime), Data, F (Data, Scope, "instance"), "COSMOGONY-worldline-instance-v1" & Character'Val (0))
           and then Id_Hex (Data, F (Data, Scope, "instance"), F (Data, Roster_Entry, "prime_worldline_id"))
           and then Id_Hex (Data, F (Data, Scope, "instance"), F (Data, F (Data, Config, "managed_observation"), "worldline_instance_id"));
      end if;
   end Current_Matches;

   function Classifier_Matches (Data : E.Bytes; Packet, Item, Projection, Initial : E.Span; Index : E.Count) return Boolean
     with Global => null
   is
      Native : constant E.Span := F (Data, Item, "native_classification");
      Material : constant E.Span := F (Data, Item, "classification_material");
      Replay : constant R.Scoped_Replay_Result := R.Reestablish_Scoped_Observation (Data, Native);
      Row : constant E.Span := Element (Data, F (Data, Packet, "rows"), Index);
      Request : constant E.Span := F (Data, F (Data, Material, "request"), "original");
      Fact : constant E.Span := Element (Data, F (Data, Packet, "facts"), Index);
      Observed : constant E.Span := F (Data, Item, "observed");
      Intent : constant E.Span := F (Data, Material, "request");
      Baseline : constant E.Span := F (Data, Packet, "before");
      Effective : constant Boolean := Text (Data, F (Data, Native, "status"), "LIVE") or else Text (Data, F (Data, Native, "status"), "REAPED");
   begin
      return Replay.State = R.Native_Redecided and then Replay.Roster_Entry = R.Classify_Entry
        and then R.Scoped_Material_Matches (Data, Native, Material)
        and then Field_Same (Data, Packet, Material, "before") and then Field_Same (Data, Packet, Material, "history")
        and then Field_Same (Data, Packet, Material, "rows") and then Field_Same (Data, Packet, Material, "projection")
        and then Field_Same (Data, Packet, Material, "buckets")
        and then Same (Data, F (Data, Material, "proposed"), F (Data, Packet, "before"))
        and then Same (Data, F (Data, Material, "proposed_history"), F (Data, Packet, "history"))
        and then Same (Data, F (Data, Material, "proposed_rows"), F (Data, Packet, "rows"))
        and then Same (Data, F (Data, Material, "proposed_projection"), F (Data, Packet, "projection"))
        and then Same (Data, F (Data, Material, "proposed_buckets"), F (Data, Packet, "buckets"))
        and then Same (Data, F (Data, Material, "actual_buckets"), F (Data, Packet, "buckets"))
        and then Field_Same (Data, Packet, Material, "facts")
        and then Field_Same (Data, Packet, Material, "current")
        and then Same (Data, F (Data, Material, "observed"), Initial)
        and then Text (Data, F (Data, Intent, "kind"), "ORDINARY")
        and then Same (Data, F (Data, Intent, "expected_epoch"), F (Data, Baseline, "resource_epoch"))
        and then Same (Data, F (Data, Request, "expected_epoch"), F (Data, Baseline, "resource_epoch"))
        and then Same (Data, F (Data, Intent, "expected_ledger_head"), F (Data, Baseline, "ledger_head"))
        and then Same (Data, F (Data, Request, "expected_ledger_head"), F (Data, Baseline, "ledger_head"))
        and then JSON_Source_Value_Matches (Data, F (Data, Projection, "before_json"),
          F (Data, F (Data, Projection, "source"), "scoped_before"), True, False)
        and then Hash_Field (Data, F (Data, Projection, "before_json"), F (Data, Request, "request_id"))
        and then Field_Same (Data, Intent, Request, "request_id")
        and then Same (Data, F (Data, Intent, "cause"), F (Data, F (Data, Packet, "current"), "cause"))
        and then Same (Data, F (Data, Intent, "requester"), F (Data, F (Data, Packet, "current"), "requester"))
        and then Same (Data, F (Data, Intent, "receipt"), F (Data, F (Data, Packet, "current"), "receipt"))
        and then Same (Data, F (Data, Observed, "scope"), F (Data, Row, "scope"))
        and then Same (Data, F (Data, Observed, "bound"), F (Data, Row, "bound"))
        and then Same (Data, F (Data, Observed, "resource_epoch"), F (Data, Baseline, "resource_epoch"))
        and then Same (Data, F (Data, Observed, "actual_unit"), F (Data, (if Effective then Fact else Row), "actual_unit"))
        and then Same (Data, F (Data, Observed, "cgroup"), F (Data, (if Effective then Fact else Row), "cgroup"))
        and then Same (Data, F (Data, Observed, "invocation"), F (Data, (if Effective then Fact else Row), "invocation"))
        and then Same (Data, F (Data, Observed, "observation_head"), F (Data, Fact, "observation_head"))
        and then Same (Data, F (Data, Request, "scope"), F (Data, Row, "scope"))
        and then Same (Data, F (Data, Request, "bound"), F (Data, Row, "bound"))
        and then Same (Data, F (Data, Request, "new_row"), Row)
        and then Text (Data, F (Data, Request, "kind"), "UNKNOWN_OPERATION")
        and then Same (Data, F (Data, Request, "operation_id"), F (Data, F (Data, Row, "bound"), "operation"))
        and then Same (Data, F (Data, Request, "reservation"), F (Data, F (Data, Row, "bound"), "reservation"))
        and then Same (Data, F (Data, Request, "requester"), F (Data, F (Data, Row, "bound"), "owner"))
        and then Same (Data, F (Data, Native, "status"), F (Data, F (Data, Item, "observed"), "observed"));
   end Classifier_Matches;

   function Namespace_Matches (Data : E.Bytes; Id, Identity : E.Span) return Boolean is
   begin
      if not Bytes_Valid (Data, Id) then return False; end if;
      declare
         Raw : constant E.Bytes := Bytes (Data, Id);
         Whole : constant E.Span := (Raw'First, Raw'Length);
      begin
         if not E.C.Canonical_JSON_Valid (Raw, Whole) or else Raw'Length = 0 or else Raw (Raw'Last) = 10 then return False; end if;
         return Decimal (Raw, E.C.Canonical_JSON_Field (Raw, Whole, "device")) = Number (Data, F (Data, Identity, "device"))
           and then Decimal (Raw, E.C.Canonical_JSON_Field (Raw, Whole, "inode")) = Number (Data, F (Data, Identity, "inode"))
           and then Decimal (Raw, E.C.Canonical_JSON_Field (Raw, Whole, "uid")) = Number (Data, F (Data, Identity, "uid"))
           and then Decimal (Raw, E.C.Canonical_JSON_Field (Raw, Whole, "gid")) = Number (Data, F (Data, Identity, "gid"))
           and then Decimal (Raw, E.C.Canonical_JSON_Field (Raw, Whole, "mode")) = Number (Data, F (Data, Identity, "mode")) mod To_Big_Integer (4096);
      end;
   end Namespace_Matches;
   function Cgroup_Identity (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (Field_Same (Data, Left, Right, "device") and then Field_Same (Data, Left, Right, "inode")
      and then Field_Same (Data, Left, Right, "uid") and then Field_Same (Data, Left, Right, "gid")
      and then Number (Data, F (Data, Left, "mode")) mod To_Big_Integer (4096) = Number (Data, F (Data, Right, "mode")) mod To_Big_Integer (4096));
   function Image_Matches (Data : E.Bytes; Projection, Inventory, Image : E.Span) return Boolean
     with Global => null
   is
      Files : constant E.Span := F (Data, Inventory, "current_source_files");
   begin
      if Len (Data, Files) > 0 then
         for I in E.Count range 0 .. Len (Data, Files) - 1 loop
            declare File : constant E.Span := Element (Data, Files, I); begin
               if Same (Data, F (Data, File, "path"), F (Data, Projection, "helper_path")) then
                  return Text (Data, F (Data, File, "role"), "EXECUTABLE")
                    and then Same (Data, F (Data, File, "raw"), F (Data, Projection, "helper_image_bytes"))
                    and then Hash_Field (Data, F (Data, File, "raw"), Image);
               end if;
            end;
         end loop;
      end if;
      return False;
   end Image_Matches;
   function Head_Matches (Data : E.Bytes; Fact, Source : E.Span) return Boolean
     with Global => null
   is
      Tree : constant E.Span := F (Data, Source, "head_tree");
      Raw : constant E.Span := F (Data, Source, "head_preimage");
      Raw_View : constant E.View := E.Decode (Data, Raw, E.Operation);
      Count : constant E.Count := E.Array_Length (Data, Members (Data, Tree));
   begin
      if not Text (Data, F (Data, Source, "head_encoding"), "ROOT_RAW_ARCHIVE")
        or else not Bytes_Valid (Data, Raw) or else Raw_View.Form /= E.Bytes_Value
        or else not Hash_Field (Data, Raw, F (Data, Fact, "observation_head"))
      then return False; end if;
      declare Encoded : constant E.Bytes := Bytes (Data, Raw); begin
         if not RA.Ordered_Source_Value_Matches (Encoded, Data, (Encoded'First, Encoded'Length), Tree, False, False) then return False; end if;
      end;
      if Count > 0 then
         for I in E.Count range 0 .. Count - 1 loop
            declare
               Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, Members (Data, Tree), I), E.Finalization);
               Key : constant E.Span := E.Array_Element (Data, Pair.Children, 0);
            begin
               if not Same (Data, E.Array_Element (Data, Pair.Children, 1), Member_Value (Data, Source, Key))
                 and then not (Text (Data, Key, "head_tree") or else Text (Data, Key, "head_preimage")
                   or else Text (Data, Key, "head_encoding"))
               then return False; end if;
            end;
         end loop;
      end if;
      return True;
   end Head_Matches;
   function Peer_Matches (Data : E.Bytes; Fact, Source, Inventory, Roster_Entry : E.Span) return Boolean
     with Global => null
   is
      Raw : constant E.Span := F (Data, Source, "kernel");
      Peer : constant E.Span := F (Data, Fact, "peer");
      Held_Peer : constant E.Span := F (Data, F (Data, Roster_Entry, "held"), "peer");
      Provenance : constant E.Span := F (Data, Raw, "peer_source");
      Process : constant E.Span := F (Data, F (Data, F (Data, Source, "process_inventory"), "helper_pidfd"), "observation");
      Host_Info : constant E.Span := F (Data, Provenance, "host_pidfd_info");
   begin
      if not (Same (Data, Peer, Held_Peer) or else Id_Hex (Data, Peer, Held_Peer))
        or else not Same (Data, F (Data, Raw, "held"), F (Data, Roster_Entry, "held"))
        or else not Same (Data, F (Data, Raw, "closed"), F (Data, Roster_Entry, "closed"))
      then return False; end if;
      if not Is_None (Data, Process) then
         if not Same (Data, F (Data, Provenance, "host_credentials"), Peer)
           or else Credential_Number (Data, Peer, 1) /= Number (Data, F (Data, Process, "host_pid"))
           or else Credential_Number (Data, Peer, 2) /= Number (Data, F (Data, Process, "real_uid"))
           or else Credential_Number (Data, Peer, 3) /= Number (Data, F (Data, Process, "real_gid"))
           or else Credential_Number (Data, F (Data, Provenance, "relative_kernel_credentials"), 2) /= Credential_Number (Data, Peer, 2)
           or else Credential_Number (Data, F (Data, Provenance, "relative_kernel_credentials"), 3) /= Credential_Number (Data, Peer, 3)
           or else not Bytes_Valid (Data, Host_Info)
         then return False; end if;
         declare Info : constant E.Bytes := Bytes (Data, Host_Info); begin
            if Decimal (Info, Word (Info, Line (Info, "Pid", 58), 1)) /= Number (Data, F (Data, Process, "host_pid")) then return False; end if;
         end;
         declare Files : constant E.Span := F (Data, Inventory, "current_source_files"); begin
            if Len (Data, Files) > 0 then
               for I in E.Count range 0 .. Len (Data, Files) - 1 loop
                  if Text (Data, F (Data, Element (Data, Files, I), "path"), "/usr/include/asm-generic/socket.h")
                    and then Text (Data, F (Data, Element (Data, Files, I), "role"), "DATA")
                    and then Same (Data, F (Data, Element (Data, Files, I), "raw"), F (Data, Provenance, "selected_header"))
                  then return True; end if;
               end loop;
            end if;
         end;
         return False;
      else
         return Same (Data, F (Data, Provenance, "actual_cached_credentials"), Peer)
           or else (Same (Data, F (Data, Provenance, "retained_terminal_peer"), Peer)
             and then Same (Data, F (Data, Provenance, "relative_peer"), Peer));
      end if;
   end Peer_Matches;
   function Physical_Matches (Data : E.Bytes; Row, Fact, Source, Inventory, Roster_Entry, History : E.Span) return Boolean
     with Global => null
   is
      Raw : constant E.Span := F (Data, Source, "kernel");
      Manager : constant E.Span := F (Data, Raw, "manager");
      Roles : constant E.Span := F (Data, Roster_Entry, "roles");
      Cgroup : constant E.Span := F (Data, Raw, "cgroup");
      Identity : constant E.Span := F (Data, Cgroup, "identity");
      Process_Inventory : constant E.Span := F (Data, Source, "process_inventory");
      Projection : constant E.Span := F (Data, Source, "physical_projection");
      Cg_Source : constant E.Span := F (Data, Source, "cgroup_descriptor");
   begin
      if not Same (Data, F (Data, Fact, "retained"), F (Data, Row, "bound")) then return False; end if;
      if Text (Data, F (Data, Fact, "phase"), "UNAVAILABLE") or else Text (Data, F (Data, Fact, "phase"), "NEVER_DISPATCHED") then
         return Worldline.Scoped_Capture_History_Projection.Unavailable_Source_Matches (Data, Row, Fact, Source, History);
      end if;
      if F (Data, Source, "historical").Length > 0 and then not Is_None (Data, F (Data, Source, "historical")) then
         return Worldline.Scoped_Capture_History_Projection.Historical_Source_Matches (Data, Row, Fact, Source, History);
      end if;
      if not Role_Roster_Matches (Data, Inventory) or else Is_None (Data, Roles)
        or else not Head_Matches (Data, Fact, Source)
        or else not Peer_Matches (Data, Fact, Source, Inventory, Roster_Entry)
        or else not Is_Number (Data, F (Data, Manager, "returncode"), 0)
        or else not Property (Data, Manager, "Id", F (Data, Fact, "actual_unit"))
        or else not Property (Data, Manager, "ControlGroup", F (Data, Fact, "cgroup"))
        or else not Property (Data, Manager, "InvocationID", F (Data, Fact, "invocation"))
        or else not Property (Data, Manager, "Delegate", F (Data, Fact, "manager_delegate"))
        or else not Same (Data, F (Data, Fact, "actual_unit"), F (Data, Row, "planned_unit"))
        or else not Same (Data, F (Data, Fact, "cgroup_events"), F (Data, Cgroup, "events"))
        or else not Same (Data, F (Data, Fact, "cgroup_type"), F (Data, Cgroup, "type"))
        or else not Field_Same (Data, Fact, Raw, "namespace_wait") or else not Field_Same (Data, Fact, Raw, "helper_wait")
        or else not Cgroup_Identity (Data, Descriptor (Data, Inventory, F (Data, F (Data, Roles, "cgroup"), "descriptor")), Identity)
        or else not Stable_Identity (Data, F (Data, Cg_Source, "identity"), F (Data, Cg_Source, "named"))
        or else not Stable_Identity (Data, F (Data, Cg_Source, "identity"), Descriptor (Data, Inventory, F (Data, F (Data, Roles, "cgroup"), "descriptor")))
        or else not Same (Data, F (Data, Cg_Source, "events"), F (Data, Fact, "cgroup_events"))
        or else not Same (Data, F (Data, Cg_Source, "type"), F (Data, Fact, "cgroup_type"))
        or else not Namespace_Matches (Data, F (Data, Fact, "namespace"), Descriptor (Data, Inventory, F (Data, Roles, "worker_namespace")))
        or else not Stable_Identity (Data, F (Data, Projection, "namespace_identity"), Descriptor (Data, Inventory, F (Data, Roles, "worker_namespace")))
        or else not JSON_Matches (Data, F (Data, Projection, "dispatch_json"), F (Data, Projection, "dispatch_value"))
        or else not Hash_Field (Data, F (Data, Projection, "dispatch_json"), F (Data, Fact, "dispatch"))
        or else not Id_Hex (Data, F (Data, Fact, "challenge"), F (Data, Projection, "challenge_hex"))
        or else not Image_Matches (Data, Projection, Inventory, F (Data, Fact, "helper_image"))
        or else not Same (Data, F (Data, Fact, "cgroup_owner"), F (Data, Identity, "uid"))
        or else Number (Data, F (Data, Fact, "cgroup_group_write")) /= (Number (Data, F (Data, Identity, "mode")) / To_Big_Integer (16)) mod To_Big_Integer (2) * To_Big_Integer (16)
        or else Number (Data, F (Data, Fact, "cgroup_other_write")) /= (Number (Data, F (Data, Identity, "mode")) / To_Big_Integer (2)) mod To_Big_Integer (2) * To_Big_Integer (2)
        or else not Same (Data, F (Data, Fact, "namespace"), F (Data, Fact, "held_namespace"))
        or else not Same (Data, F (Data, Fact, "peer"), F (Data, Fact, "held_peer"))
        or else not Same (Data, F (Data, Fact, "helper_image"), F (Data, Fact, "expected_helper_image"))
        or else not Same (Data, F (Data, Fact, "challenge"), F (Data, Fact, "held_challenge"))
      then return False; end if;
      for Role in Positive range 1 .. 4 loop
         declare
            Name : constant String := (case Role is when 1 => "namespace_pidfd", when 2 => "helper_pidfd", when 3 => "worker_pidfd", when others => "actor_pidfd");
            P : constant E.Span := F (Data, Process_Inventory, Name);
            Namespace : constant E.Span := Descriptor (Data, Inventory, F (Data, Roles, (if Role = 2 then "helper_namespace" else "worker_namespace")));
         begin
            if not Same (Data, F (Data, P, "descriptor"), F (Data, Roles, Name))
              or else not Process_Matches (Data, P, Inventory, Namespace, F (Data, Fact, "actual_unit"), F (Data, Fact, "invocation"))
            then return False; end if;
         end;
      end loop;
      if not Same (Data, F (Data, Fact, "namespace_wait"), F (Data, F (Data, Process_Inventory, "namespace_pidfd"), "wait"))
        or else not Same (Data, F (Data, Fact, "helper_wait"), F (Data, F (Data, Process_Inventory, "helper_pidfd"), "wait"))
      then return False; end if;
      return Worldline.Scoped_Capture_History_Projection.Owned_Protocol_Matches (Data, Row, Fact, Source, Roster_Entry, History);
   end Physical_Matches;

   function Subject_Capture_Matches (Data : E.Bytes; Subject, Primary, Packet : E.Span) return Boolean is
      Inventory : constant E.Span := F (Data, Subject, "inventory");
      Frame : constant E.Span := F (Data, Inventory, "frame");
      Root_Frame : constant E.Span := F (Data, Primary, "frame");
      Rows : constant E.Span := F (Data, Frame, "rows");
      Root_Rows : constant E.Span := F (Data, Root_Frame, "rows");
      Aliases : constant E.Span := F (Data, Subject, "scope_aliases");
      Actor : constant E.Span := F (Data, Inventory, "current_actor");
      Root_Actor : constant E.Span := F (Data, Primary, "current_actor");
      Files : constant E.Span := F (Data, Inventory, "current_source_files");
      Root_Files : constant E.Span := F (Data, Primary, "current_source_files");
      Namespace : constant E.Span := F (Data, F (Data, Inventory, "namespace_source"), "receiver_actor_namespace");
      Root_Namespace : constant E.Span := F (Data, F (Data, Primary, "namespace_source"), "receiver_actor_namespace");
      Expected : E.Count := 0;
      function Width (Item : E.Span; Count : E.Count) return Boolean is
        (RA.Source_Valid (Data, Item, False)
         and then E.Decode (Data, Item, E.Operation).Form = E.Object_Value
         and then E.Array_Length (Data, Members (Data, Item)) = Count);
      function Role_Name (Index : Positive) return String is
        (case Index is when 1 => "listener", when 2 => "supervisor_channel",
           when 3 => "worker_namespace", when 4 => "namespace_pidfd", when 5 => "helper_pidfd",
           when 6 => "worker_pidfd", when 7 => "actor_pidfd", when 8 => "credential_receiver",
           when 9 => "custody_channel", when 10 => "stdout_fd", when 11 => "stderr_fd",
           when 12 => "stdin_fd", when 13 => "retained_peer", when 14 => "helper_namespace",
           when others => "cgroup");
      function Role_FD (Here, Name : E.Span) return E.Span is
         Roles : constant E.Span := F (Data, Here, "roles");
      begin
         if Len (Data, Roles) > 0 then
            for I in E.Count range 0 .. Len (Data, Roles) - 1 loop
               declare Role : constant E.Span := Element (Data, Roles, I); begin
                  if Same (Data, F (Data, Role, "role"), Name) then return F (Data, F (Data, Role, "fstat"), "fd"); end if;
               end;
            end loop;
         end if;
         return (1, 0);
      end Role_FD;
   begin
      if not Width (Subject, 3) or else not Sequence_Valid (Data, Rows)
        or else not Sequence_Valid (Data, Root_Rows) or else not Sequence_Valid (Data, Aliases)
        or else not Role_Roster_Matches (Data, Inventory)
        or else not Role_Roster_Matches (Data, Primary)
        or else not
          ((F (Data, Inventory, "subject_transport").Length > 0
            and then F (Data, Inventory, "initial_root_transport").Length = 0)
           or else (F (Data, Inventory, "initial_root_transport").Length > 0
             and then F (Data, Inventory, "subject_transport").Length = 0))
        or else not Same (Data, F (Data, Subject, "native_packet"), Packet)
        or else not Field_Same (Data, Frame, Root_Frame, "installation")
        or else not Field_Same (Data, Actor, Root_Actor, "pid")
        or else not Field_Same (Data, Actor, Root_Actor, "boot")
        or else not Field_Same (Data, Actor, Root_Actor, "start_tick")
        or else not Field_Same (Data, Actor, Root_Actor, "credentials")
        or else not Field_Same (Data, F (Data, Inventory, "current_source"), F (Data, Primary, "current_source"), "envelope_path")
        or else not Field_Same (Data, F (Data, Inventory, "current_source"), F (Data, Primary, "current_source"), "envelope_bytes_hex")
        or else not Field_Same (Data, F (Data, Inventory, "current_source"), F (Data, Primary, "current_source"), "interpreter")
        or else not Sequence_Valid (Data, Files) or else not Sequence_Valid (Data, Root_Files)
        or else Len (Data, Files) /= Len (Data, Root_Files)
        or else not Stable_Identity (Data, F (Data, Namespace, "proc_identity"), F (Data, Root_Namespace, "proc_identity"))
        or else not Field_Same (Data, Namespace, Root_Namespace, "boot")
        or else not Field_Same (Data, F (Data, Namespace, "raw"), F (Data, Root_Namespace, "raw"), "uid_map")
        or else not Field_Same (Data, F (Data, Namespace, "raw"), F (Data, Root_Namespace, "raw"), "gid_map")
        or else not Same (Data, F (Data, F (Data, Namespace, "namespaces"), "pid"), F (Data, F (Data, Root_Namespace, "namespaces"), "pid"))
        or else not Same (Data, F (Data, F (Data, Namespace, "namespaces"), "user"), F (Data, F (Data, Root_Namespace, "namespaces"), "user"))
      then return False; end if;
      if Len (Data, Files) > 0 then
         for I in E.Count range 0 .. Len (Data, Files) - 1 loop
            declare Left : constant E.Span := Element (Data, Files, I);
              Right : constant E.Span := Element (Data, Root_Files, I); begin
               if not Field_Same (Data, Left, Right, "path") or else not Field_Same (Data, Left, Right, "role")
                 or else not Field_Same (Data, Left, Right, "raw") or else not Field_Same (Data, Left, Right, "lease_raw")
                 or else not Stable_Identity (Data, F (Data, Left, "identity"), F (Data, Right, "identity"))
               then return False; end if;
            end;
         end loop;
      end if;
      if Len (Data, Rows) > 0 then
         for I in E.Count range 0 .. Len (Data, Rows) - 1 loop
            declare
               Item : constant E.Span := Element (Data, Rows, I);
               Row : constant E.Span := F (Data, Item, "row");
               Root_Item : E.Span := (1, 0);
               Matches : E.Count := 0;
            begin
               if Len (Data, Root_Rows) > 0 then
                  for J in E.Count range 0 .. Len (Data, Root_Rows) - 1 loop
                     pragma Loop_Invariant (Matches <= J);
                     declare Candidate : constant E.Span := Element (Data, Root_Rows, J); begin
                        if Same (Data, F (Data, Row, "bound"), F (Data, F (Data, Candidate, "row"), "bound"))
                          and then Same (Data, F (Data, Row, "scope"), F (Data, F (Data, Candidate, "row"), "scope"))
                        then Root_Item := Candidate; Matches := Matches + 1; end if;
                     end;
                  end loop;
               end if;
               if Matches /= 1
                 or else not Field_Same (Data, Row, F (Data, Root_Item, "row"), "actual_unit")
                 or else not Field_Same (Data, Row, F (Data, Root_Item, "row"), "cgroup")
                 or else not Field_Same (Data, Row, F (Data, Root_Item, "row"), "invocation")
                 or else not Field_Same (Data, Row, F (Data, Root_Item, "row"), "planned_unit")
               then return False; end if;
               if Is_None (Data, F (Data, Item, "roles")) then
                  if not Is_None (Data, F (Data, Root_Item, "roles")) then return False; end if;
               else
                  if Is_None (Data, F (Data, Root_Item, "roles")) then return False; end if;
                  for K in Positive range 1 .. 15 loop
                     declare
                        Name : constant String := Role_Name (K);
                        Subject_Role : constant E.Span := F (Data, F (Data, Item, "roles"), Name);
                        Root_Role : constant E.Span := F (Data, F (Data, Root_Item, "roles"), Name);
                        Subject_Name : constant E.Span := (if K = 15 and then not Is_None (Data, Subject_Role)
                          then F (Data, Subject_Role, "descriptor") else Subject_Role);
                        Root_Name : constant E.Span := (if K = 15 and then not Is_None (Data, Root_Role)
                          then F (Data, Root_Role, "descriptor") else Root_Role);
                        Alias_Value : E.Span;
                     begin
                        if Is_None (Data, Subject_Name) then
                           if not Is_None (Data, Root_Name) then return False; end if;
                        else
                           if Is_None (Data, Root_Name) then return False; end if;
                           if Expected >= Len (Data, Aliases) then return False; end if;
                           Alias_Value := Element (Data, Aliases, Expected);
                           if not Width (Alias_Value, 10)
                             or else not Same (Data, F (Data, Alias_Value, "bound"), F (Data, Row, "bound"))
                             or else not Same (Data, F (Data, Alias_Value, "scope"), F (Data, Row, "scope"))
                             or else not Text (Data, F (Data, Alias_Value, "logical_role"), Name)
                           then return False; end if;
                           Expected := Expected + 1;
                           declare
                              Subject_Id : constant E.Span := Descriptor (Data, Inventory, Subject_Name);
                              Root_Id : constant E.Span := Descriptor (Data, Primary, Root_Name);
                              Kcmp : constant E.Span := F (Data, Alias_Value, "kcmp");
                              Args : constant E.Span := F (Data, Kcmp, "args");
                           begin
                              if not Same (Data, F (Data, Alias_Value, "subject_descriptor"), Subject_Name)
                                or else not Same (Data, F (Data, Alias_Value, "root_descriptor"), Root_Name)
                                or else not Same (Data, F (Data, Alias_Value, "subject_fd"), Role_FD (Inventory, Subject_Name))
                                or else not Same (Data, F (Data, Alias_Value, "root_fd"), Role_FD (Primary, Root_Name))
                                or else not Stable_Identity (Data, F (Data, Alias_Value, "subject_identity"), Subject_Id)
                                or else not Stable_Identity (Data, F (Data, Alias_Value, "root_identity"), Root_Id)
                                or else not Stable_Identity (Data, Subject_Id, Root_Id)
                                or else not Width (Kcmp, 5) or else not Width (Args, 5)
                                or else not Syscall (Data, Kcmp, "kcmp", 0)
                                or else not Same (Data, F (Data, Kcmp, "source"), F (Data, Inventory, "current_source"))
                                or else not Same (Data, F (Data, Args, "pid1"), F (Data, Actor, "pid"))
                                or else not Same (Data, F (Data, Args, "pid2"), F (Data, Root_Actor, "pid"))
                                or else not Is_Number (Data, F (Data, Args, "type"), 0)
                                or else not Same (Data, F (Data, Args, "idx1"), F (Data, Alias_Value, "subject_fd"))
                                or else not Same (Data, F (Data, Args, "idx2"), F (Data, Alias_Value, "root_fd"))
                              then return False; end if;
                           end;
                        end if;
                     end;
                  end loop;
               end if;
            end;
         end loop;
      end if;
      return Expected = Len (Data, Aliases);
   end Subject_Capture_Matches;

   function Scoped_Capture_Matches (Data : E.Bytes; Observation, Provenance : E.Span) return Boolean is
      Capture : E.Span := F (Data, Provenance, "owned_descriptor_roster");
      Packet : E.Span;
      Projection : E.Span := F (Data, Provenance, "scoped_projection");
      Rows, Facts, Observed, Sources, Inventory, Entries : E.Span;
      Owner : E.Span := F (Data, Provenance, "owner_state");
      Initial : E.Span;
   begin
      if Capture.Length = 0 then Capture := F (Data, Provenance, "complete_scoped_capture"); end if;
      if Capture.Length = 0 and then F (Data, Provenance, "packet").Length > 0 then Capture := Provenance; end if;
      if Capture.Length = 0 then return False; end if;
      Packet := F (Data, Capture, "packet");
      if Projection.Length = 0 then Projection := F (Data, Capture, "scoped_projection"); end if;
      if Owner.Length = 0 then Owner := F (Data, Capture, "owner_state"); end if;
      if not (R.Scoped_Material_Matches (Data, Observation, Packet)
        or else R.Root_Scoped_Material_Matches (Data, Observation, Packet))
        or else not Current_Matches (Data, Packet, Projection)
        or else not Worldline.Scoped_Capture_Owner_Projection.Owner_Source_Matches (Data, Packet, Projection, Owner, False)
      then return False; end if;
      Rows := F (Data, Packet, "rows"); Facts := F (Data, Packet, "facts"); Observed := F (Data, Packet, "observed");
      Sources := F (Data, Capture, "rows"); Inventory := F (Data, Capture, "inventory");
      Entries := F (Data, F (Data, Inventory, "frame"), "rows");
      if not Sequence_Valid (Data, Rows) or else not Sequence_Valid (Data, Sources)
        or else Len (Data, Rows) /= Len (Data, Facts) or else Len (Data, Rows) /= Len (Data, Observed)
        or else Len (Data, Rows) /= Len (Data, Sources)
        or else (not Is_None (Data, Inventory) and then Len (Data, Entries) /= Len (Data, Rows))
      then return False; end if;
      if F (Data, Provenance, "subject_capture").Length > 0
        and then not Subject_Capture_Matches
          (Data, F (Data, Provenance, "subject_capture"), Inventory, Packet)
      then return False; end if;
      if Len (Data, Rows) > 0 then
         Initial := F (Data, F (Data, Element (Data, Sources, 0), "classification_material"), "observed");
         if Len (Data, Initial) /= Len (Data, Rows) then return False; end if;
         for I in E.Count range 0 .. Len (Data, Rows) - 1 loop
            declare
               Native : constant E.Span := Element (Data, Initial, I);
               Row : constant E.Span := Element (Data, Rows, I);
               Fact : constant E.Span := Element (Data, Facts, I);
            begin
               if not Text (Data, F (Data, Native, "observed"), "UNKNOWN")
                 or else not Same (Data, F (Data, Native, "scope"), F (Data, Row, "scope"))
                 or else not Same (Data, F (Data, Native, "bound"), F (Data, Row, "bound"))
                 or else not Same (Data, F (Data, Native, "resource_epoch"), F (Data, F (Data, Packet, "before"), "resource_epoch"))
                 or else not Field_Same (Data, Native, Row, "actual_unit")
                 or else not Field_Same (Data, Native, Row, "cgroup")
                 or else not Field_Same (Data, Native, Row, "invocation")
                 or else not Field_Same (Data, Native, Fact, "observation_head")
               then return False; end if;
            end;
         end loop;
         for I in E.Count range 0 .. Len (Data, Rows) - 1 loop
            declare
               Item : constant E.Span := Element (Data, Sources, I);
               Fact : constant E.Span := Element (Data, Facts, I);
               Row : constant E.Span := Element (Data, Rows, I);
               Native : constant E.Span := Element (Data, Observed, I);
               Roster_Entry : constant E.Span := Element (Data, Entries, I);
            begin
               if not Same (Data, Row, F (Data, Item, "row")) or else not Same (Data, Fact, F (Data, Item, "physical"))
                 or else not Same (Data, Native, F (Data, Item, "observed"))
                 or else not Classifier_Matches (Data, Packet, Item, Projection, Initial, I)
                 or else not Same (Data, F (Data, Fact, "current"), F (Data, F (Data, Packet, "current"), "scope"))
                 or else not Same (Data, F (Data, Fact, "current_epoch"), F (Data, F (Data, Packet, "current"), "resource_epoch"))
                 or else not Same (Data, F (Data, Fact, "current_universe_head"), F (Data, F (Data, Packet, "current"), "universe_head"))
                 or else not Same (Data, F (Data, Fact, "current_ledger_head"), F (Data, F (Data, Packet, "current"), "ledger_head"))
                 or else (not Is_None (Data, Inventory) and then
                   (not Same (Data, F (Data, Row, "bound"), F (Data, F (Data, Roster_Entry, "row"), "bound"))
                    or else not Same (Data, F (Data, Row, "scope"), F (Data, F (Data, Roster_Entry, "row"), "scope"))))
                 or else not Physical_Matches (Data, Row, Fact, F (Data, Item, "source"), Inventory, Roster_Entry,
                   F (Data, Projection, "history_owner"))
               then return False; end if;
            end;
         end loop;
      end if;
      return True;
   end Scoped_Capture_Matches;
   function Scoped_Record_Matches (Data : E.Bytes; Encoded, Typed : E.Span; Scoped, Typed_Scoped : Boolean := False) return Boolean is
     (Worldline.Scoped_Record_Source.Scoped_Record_Value_Matches (Data, Encoded, Typed, Scoped, Typed_Scoped));
   function JSON_Source_Value_Matches (Data : E.Bytes; Raw, Value : E.Span; Canonical : Boolean; Scoped : Boolean := False) return Boolean is
   begin
      if Bytes_Valid (Data, Raw) then
         declare JSON : constant E.Bytes := Bytes (Data, Raw); begin
            return Worldline.Raw_JSON.JSON_Source_Value_Matches (JSON, Data, (JSON'First, JSON'Length), Value, Canonical, Scoped);
         end;
      elsif Text_Valid (Data, Raw) then
         declare JSON : constant E.Bytes := Text_Bytes (Data, Raw); begin
            return Worldline.Raw_JSON.JSON_Source_Value_Matches (JSON, Data, (JSON'First, JSON'Length), Value, Canonical, Scoped);
         end;
      else return False; end if;
   end JSON_Source_Value_Matches;
   function Source_Record_Matches (Data : E.Bytes; Encoded, Raw_Source : E.Span; Scoped, Raw_Scoped : Boolean := False) return Boolean is
     (Worldline.Scoped_Record_Source.Source_Record_Value_Matches (Data, Encoded, Raw_Source, Scoped, Raw_Scoped));
   function Value_Matches (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (Same (Data, Left, Right));
   function JSON_Value_Matches (Data : E.Bytes; JSON, Item : E.Span) return Boolean is
     (JSON_Matches (Data, JSON, Item));
   function Current_Source_Matches (Data : E.Bytes; Packet, Projection : E.Span) return Boolean is
     (Current_Matches (Data, Packet, Projection));
   function Head_Source_Matches (Data : E.Bytes; Fact, Source : E.Span) return Boolean is
     (Head_Matches (Data, Fact, Source));
   function Process_Source_Matches (Data : E.Bytes; Item, Inventory, Namespace, Unit, Invocation : E.Span) return Boolean is
     (Process_Matches (Data, Item, Inventory, Namespace, Unit, Invocation));

   function Scoped_Descriptor_Alias_Matches (Data, Actual_Data : E.Bytes;
     Inventory, Role, FD, Identity : E.Span) return Boolean
   is
      function Cross (Left, Right : E.Span) return Boolean is
        (Worldline.Recovery_Archive.Ordered_Source_Value_Matches (Data, Actual_Data, Left, Right, False, False));
      function Cross_Identity (Left, Right : E.Span) return Boolean is
        (Cross (F (Data, Left, "device"), OA.Field (Actual_Data, Right, "device"))
         and then Cross (F (Data, Left, "inode"), OA.Field (Actual_Data, Right, "inode"))
         and then Cross (F (Data, Left, "mode"), OA.Field (Actual_Data, Right, "mode"))
         and then Cross (F (Data, Left, "uid"), OA.Field (Actual_Data, Right, "uid"))
         and then Cross (F (Data, Left, "gid"), OA.Field (Actual_Data, Right, "gid")));
      Holder : constant E.Span := F (Data, Inventory, "current_actor");
      function Find (Here : E.Span) return Boolean
        with Subprogram_Variant => (Decreases => Here.Length)
      is
         Frame : constant E.Span := F (Data, Here, "frame");
         Current : constant E.Span := F (Data, Here, "roles");
         Reconstruction : constant E.Span := F (Data, Here, "reconstruction");
         Registry : constant E.Span := F (Data, Reconstruction, "service_registry");
         Extensions : constant E.Span := F (Data, Frame, "extensions");
         Actor : constant E.Span := F (Data, Here, "current_actor");
         Same_Holder : constant Boolean :=
           Field_Same (Data, Actor, Holder, "pid") and then Field_Same (Data, Actor, Holder, "boot")
           and then Field_Same (Data, Actor, Holder, "start_tick") and then Field_Same (Data, Actor, Holder, "credentials");
         Prior : E.Span := F (Data, Reconstruction, "original_inventory");
      begin
         if not Role_Roster_Matches (Data, Here) then return False; end if;
         if Same_Holder and then Len (Data, Current) > 0 then
            for I in E.Count range 0 .. Len (Data, Current) - 1 loop
               declare Item : constant E.Span := Element (Data, Current, I); begin
                  if Same (Data, F (Data, Item, "role"), Role)
                    and then Cross (F (Data, Item, (if Is_None (Data, F (Data, Item, "worker_fd")) then "front_fd" else "worker_fd")), FD)
                    and then Cross_Identity (F (Data, Item, "current"), Identity) then return True; end if;
               end;
            end loop;
         end if;
         if Same_Holder and then Len (Data, Registry) = Len (Data, Extensions) and then Len (Data, Registry) > 0 then
            for I in E.Count range 0 .. Len (Data, Registry) - 1 loop
               declare
                  Item : constant E.Span := Element (Data, Registry, I);
                  Extension : constant E.Span := Element (Data, Extensions, I);
               begin
                  if Same (Data, F (Data, Extension, "descriptor"), Role)
                    and then Cross (F (Data, Item, "fd"), FD)
                    and then Cross_Identity (F (Data, Item, "identity"), Identity) then return True; end if;
               end;
            end loop;
         end if;
         declare Closures : constant E.Span := F (Data, Frame, "closed_roles"); begin
            if E.Array_Length (Data, Members (Data, Closures)) > 0 then
               for I in E.Count range 0 .. E.Array_Length (Data, Members (Data, Closures)) - 1 loop
                  declare
                     Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, Members (Data, Closures), I), E.Finalization);
                     Closed : constant E.Span := E.Array_Element (Data, Pair.Children, 1);
                     Before : constant E.Span := F (Data, Closed, "before_inventory");
                  begin
                     if Before.Length > 0 and then Before.Length < Here.Length and then Find (Before) then return True; end if;
                  end;
               end loop;
            end if;
         end;
         if Prior.Length = 0 then Prior := F (Data, F (Data, Frame, "evolution"), "original_inventory"); end if;
         if Prior.Length = 0 or else Prior.Length >= Here.Length then return False; end if;
         return Find (Prior);
      end Find;
   begin
      return Integer_Valid (Actual_Data, FD) and then RA.Source_Valid (Actual_Data, Identity, False)
        and then E.Decode (Actual_Data, Identity, E.Operation).Form = E.Object_Value and then Find (Inventory);
   end Scoped_Descriptor_Alias_Matches;
end Worldline.Scoped_Capture_Projection;
