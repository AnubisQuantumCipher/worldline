with Interfaces;
with Attest.SHA256;
with SPARK.Big_Integers;
with Worldline.Scoped_Archive;
with Worldline.Recovery_Archive;
with Worldline.Scoped_Capture_Projection;
with Worldline.Custody_V2_Domain_Hmac;
with Worldline.SQLite_Parameter_Source;

package body Worldline.Scoped_Capture_Owner_Projection with SPARK_Mode is
   package P renames Worldline.Scoped_Capture_Projection;
   package SA renames Worldline.Scoped_Archive;
   package OA renames SA.A;
   package RA renames Worldline.Recovery_Archive;
   package SHA renames Attest.SHA256;
   package H renames Worldline.Custody_V2_Domain_Hmac;
   package SQL_Source renames Worldline.SQLite_Parameter_Source;
   use SPARK.Big_Integers;
   use type E.Count;
   use type E.Span;
   use type E.Bytes;
   use type E.Value_Kind;
   use type E.Q.Byte;
   use type R.Replay_State;
   use type R.Scoped_Entry;
   use type Interfaces.Unsigned_32;
   Empty : constant E.Span := (1, 0);
   function Owner_Source_Matches
     (Data : E.Bytes; Packet, Projection, Owner : E.Span;
      Scoped_Transport : Boolean := False) return Boolean is
   function Source_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
     (RA.Source_Valid (Data, Item, Scoped_Transport));
   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if Scoped_Transport then return R.Archive_Field (Data, Item, Name); end if;
      if not RA.Source_Valid (Data, Item, False) or else View.Form not in E.Record_Value | E.Object_Value then return Empty; end if;
      for I in E.Count range 1 .. E.Array_Length (Data, View.Children) loop
         declare Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, View.Children, I - 1), E.Finalization); begin
            if E.Text_Is (Data, E.Decode (Data, E.Array_Element (Data, Pair.Children, 0),
              (if View.Form = E.Record_Value then E.Finalization else E.Operation)), Name)
            then return E.Array_Element (Data, Pair.Children, 1); end if;
         end;
      end loop;
      return Empty;
   end F;
   function Seq (Data : E.Bytes; Item : E.Span) return Boolean is
     (Source_Valid (Data, Item) and then (if Scoped_Transport then R.Archive_Is_Sequence (Data, Item)
      else E.Decode (Data, Item, E.Operation).Form in E.List_Value | E.Tuple_Value));
   function Element (Data : E.Bytes; Item : E.Span; Index : E.Count) return E.Span is
     (if not Seq (Data, Item) then Empty elsif Scoped_Transport then R.Archive_Index (Data, Item, Index)
      else E.Array_Element (Data, E.Decode (Data, Item, E.Operation).Children, Index));
   function Len (Data : E.Bytes; Item : E.Span) return E.Count is
     (if not Seq (Data, Item) then 0 elsif Scoped_Transport then R.Archive_Length (Data, Item)
      else E.Array_Length (Data, E.Decode (Data, Item, E.Operation).Children));
   function Same (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (RA.Ordered_Source_Value_Matches (Data, Data, Left, Right, Scoped_Transport, Scoped_Transport));
   function Text (Data : E.Bytes; Item : E.Span; Value : String) return Boolean is
     (Source_Valid (Data, Item) and then (if Scoped_Transport then SA.Text_Is (Data, Item, Value)
      else E.Text_Is (Data, E.Decode (Data, Item, E.Operation), Value)));
   function Is_None (Data : E.Bytes; Item : E.Span) return Boolean is
     (Source_Valid (Data, Item) and then (if Scoped_Transport then R.Archive_Is_None (Data, Item)
      else E.Decode (Data, Item, E.Operation).Form = E.Null_Value));
   function BValid (Data : E.Bytes; Item : E.Span) return Boolean is
     (Source_Valid (Data, Item) and then (if Scoped_Transport then R.Archive_Bytes_Valid (Data, Item)
      else E.Decode (Data, Item, E.Operation).Form = E.Bytes_Value and then
        E.Bytes_Valid (Data, E.Decode (Data, Item, E.Operation).Payload)));
   function B (Data : E.Bytes; Item : E.Span) return E.Bytes
   is (if Scoped_Transport then R.Archive_Bytes (Data, Item)
       else E.Materialize (Data, E.Decode (Data, Item, E.Operation).Payload))
     with Pre => BValid (Data, Item);
   function SF (Data : E.Bytes; Left, Right : E.Span; Name : String) return Boolean is
     (Same (Data, F (Data, Left, Name), F (Data, Right, Name)));
   function N (Data : E.Bytes; Item : E.Span; Value : E.Count) return Boolean is
      Remaining : E.Count := Value;
      Expected : Big_Integer := To_Big_Integer (0);
      Place : Big_Integer := To_Big_Integer (1);
   begin
      while Remaining > 0 loop
         Expected := Expected + To_Big_Integer (Integer (Remaining mod 256)) * Place;
         Place := Place * To_Big_Integer (256); Remaining := Remaining / 256;
      end loop;
      return R.Archive_Integer_Valid (Data, Item) and then P.Number (Data, Item) = Expected;
   end N;
   function TV (Data : E.Bytes; Item : E.Span) return E.View is
     (if Scoped_Transport then E.Decode (Data, OA.Field (Data, Item, "value"), E.Operation)
      else E.Decode (Data, Item, E.Operation));
   function TValid (Data : E.Bytes; Item : E.Span) return Boolean is
     (Source_Valid (Data, Item) and then TV (Data, Item).Form = E.Text_Value
      and then E.Bytes_Valid (Data, TV (Data, Item).Payload));
   function TB (Data : E.Bytes; Item : E.Span) return E.Bytes
   is (E.Materialize (Data, TV (Data, Item).Payload))
     with Pre => TValid (Data, Item);
   function Joined (Data : E.Bytes; Word, Root : E.Span; Suffix : String) return Boolean is
   begin
      if not TValid (Data, Word) or else not TValid (Data, Root) then return False; end if;
      declare W : constant E.Bytes := TB (Data, Word); R : constant E.Bytes := TB (Data, Root); begin
         return W'Length >= R'Length and then W'Length - R'Length = Suffix'Length
           and then (for all I in R'Range => W (W'First + I - R'First) = R (I))
           and then (for all I in Suffix'Range => W (W'First + R'Length + E.Count (I - Suffix'First)) = Character'Pos (Suffix (I)));
      end;
   end Joined;
   function Find_Path (Data : E.Bytes; Paths, Word : E.Span) return E.Span is
      Found : E.Span := Empty;
   begin
      if not Seq (Data, Paths) then return Empty; end if;
      for I in E.Count range 1 .. Len (Data, Paths) loop
         declare Item : constant E.Span := Element (Data, Paths, I - 1); begin
            if Same (Data, F (Data, Item, "path"), Word) then
               if Found.Length > 0 then return Empty; end if; Found := Item;
            end if;
         end;
      end loop;
      return Found;
   end Find_Path;
   function Find_Joined (Data : E.Bytes; Paths, Root : E.Span; Suffix : String) return E.Span is
      Found : E.Span := Empty;
   begin
      if not Seq (Data, Paths) then return Empty; end if;
      for I in E.Count range 1 .. Len (Data, Paths) loop
         declare Item : constant E.Span := Element (Data, Paths, I - 1); begin
            if Joined (Data, F (Data, Item, "path"), Root, Suffix) then
               if Found.Length > 0 then return Empty; end if; Found := Item;
            end if;
         end;
      end loop;
      return Found;
   end Find_Joined;
   function Table (Data : E.Bytes; Database : E.Span; Name : String) return E.Span is
      Tables : constant E.Span := F (Data, Database, "tables");
      Found : E.Span := Empty;
   begin
      if not Seq (Data, Tables) then return Empty; end if;
      for I in E.Count range 1 .. Len (Data, Tables) loop
         declare Item : constant E.Span := Element (Data, Tables, I - 1); begin
            if Text (Data, F (Data, Item, "name"), Name) then
               if Found.Length > 0 then return Empty; end if; Found := Item;
            end if;
         end;
      end loop;
      return Found;
   end Table;
   function Column_Index (Data : E.Bytes; T : E.Span; Name : String) return E.Count is
      Columns : constant E.Span := F (Data, T, "columns");
      Result : E.Count := 0;
   begin
      for I in E.Count range 1 .. Len (Data, Columns) loop
         if Text (Data, Element (Data, Element (Data, Columns, I - 1), 1), Name) then
            if Result > 0 then return 0; end if; Result := I;
         end if;
      end loop;
      return Result;
   end Column_Index;
   function Cell (Data : E.Bytes; T, Row : E.Span; Name : String) return E.Span is
      Index : constant E.Count := Column_Index (Data, T, Name);
      Width : constant E.Count := Len (Data, F (Data, T, "columns"));
   begin
      if Index = 0 or else not Seq (Data, Row) then return Empty; end if;
      if Len (Data, Row) = Width then return Element (Data, Row, Index - 1);
      elsif Width < E.Count'Last and then Len (Data, Row) = Width + 1 then return Element (Data, Row, Index);
      else return Empty; end if;
   end Cell;
   function Named_Row (Data : E.Bytes; T : E.Span; Name, Key : String) return E.Span is
      Rows : constant E.Span := F (Data, T, "rows"); Found : E.Span := Empty;
   begin
      for I in E.Count range 1 .. Len (Data, Rows) loop
         declare Row : constant E.Span := Element (Data, Rows, I - 1); begin
            if Text (Data, Cell (Data, T, Row, Name), Key) then
               if Found.Length > 0 then return Empty; end if; Found := Row;
            end if;
         end;
      end loop;
      return Found;
   end Named_Row;
   -- These are complete independent logical captures, not projections of selected
   -- columns. Source acquisition/custody is a separate caller conjunction.
   function Database_Same (Data : E.Bytes; Left, Right : E.Span) return Boolean is
   begin
      return SF (Data, Left, Right, "schema") and then SF (Data, Left, Right, "tables")
        and then SF (Data, Left, Right, "encoding") and then SF (Data, Left, Right, "user_version")
        and then SF (Data, Left, Right, "application_id") and then SF (Data, Left, Right, "integrity")
        and then SF (Data, Left, Right, "foreign_keys") and then SF (Data, Left, Right, "journal_mode")
        and then SF (Data, Left, Right, "foreign_key_check");
   end Database_Same;
   function Database_Well_Formed (Data : E.Bytes; DB : E.Span) return Boolean is
      Tables : constant E.Span := F (Data, DB, "tables");
      Schema : constant E.Span := F (Data, DB, "schema");
      Table_Count : E.Count := 0;
   begin
      -- Preserve complete factual diagnostics, not a new blanket database
      -- health policy. Original source consumers/native kernels decide policy.
      if not Seq (Data, Tables) or else not Seq (Data, Schema)
        or else not Seq (Data, F (Data, DB, "integrity"))
        or else not Seq (Data, F (Data, DB, "foreign_key_check")) then return False; end if;
      for I in E.Count range 1 .. Len (Data, Schema) loop
         declare Row : constant E.Span := Element (Data, Schema, I - 1); begin
            if not Seq (Data, Row) or else Len (Data, Row) /= 5 then return False; end if;
            if Text (Data, Element (Data, Row, 0), "table") then Table_Count := Table_Count + 1; end if;
         end;
      end loop;
      if Table_Count /= Len (Data, Tables) then return False; end if;
      for I in E.Count range 1 .. Len (Data, Tables) loop
         declare
            T : constant E.Span := Element (Data, Tables, I - 1);
            Columns : constant E.Span := F (Data, T, "columns");
            Rows : constant E.Span := F (Data, T, "rows");
            Name : constant E.Span := F (Data, T, "name");
            Found : E.Count := 0;
         begin
            if not TValid (Data, Name) or else not Seq (Data, Columns) or else not Seq (Data, Rows)
              or else Len (Data, Columns) = 0 or else not TValid (Data, F (Data, T, "query"))
              or else not Seq (Data, F (Data, T, "foreign_key_list")) then return False; end if;
            for K in E.Count range 1 .. Len (Data, Schema) loop
               declare Row : constant E.Span := Element (Data, Schema, K - 1); begin
                  if Text (Data, Element (Data, Row, 0), "table") and then Same (Data, Element (Data, Row, 1), Name) then
                     if not Same (Data, Element (Data, Row, 2), Name) or else not TValid (Data, Element (Data, Row, 4)) then return False; end if;
                     Found := Found + 1;
                  end if;
               end;
            end loop;
            if Found /= 1 then return False; end if;
            for K in E.Count range 1 .. I - 1 loop
               if Same (Data, F (Data, Element (Data, Tables, K - 1), "name"), Name) then return False; end if;
            end loop;
            for K in E.Count range 1 .. Len (Data, Columns) loop
               declare C : constant E.Span := Element (Data, Columns, K - 1); begin
                  if not Seq (Data, C) or else Len (Data, C) /= 7 or else not N (Data, Element (Data, C, 0), K - 1)
                    or else not TValid (Data, Element (Data, C, 1)) or else not TValid (Data, Element (Data, C, 2)) then return False; end if;
                  for M in E.Count range 1 .. K - 1 loop
                     if Same (Data, Element (Data, C, 1), Element (Data, Element (Data, Columns, M - 1), 1)) then return False; end if;
                  end loop;
               end;
            end loop;
            for K in E.Count range 1 .. Len (Data, Rows) loop
               declare Row : constant E.Span := Element (Data, Rows, K - 1); begin
                  if not Seq (Data, Row) or else (Len (Data, Row) /= Len (Data, Columns)
                    and then (Len (Data, Columns) = E.Count'Last or else Len (Data, Row) /= Len (Data, Columns) + 1)) then return False; end if;
               end;
            end loop;
         end;
      end loop;
      return True;
   end Database_Well_Formed;
   function Has_Columns (Data : E.Bytes; T : E.Span; Names : String; Width : E.Count) return Boolean is
      Start : Positive := Names'First; Index : E.Count := 1;
   begin
      if Len (Data, F (Data, T, "columns")) /= Width then return False; end if;
      for I in Names'Range loop
         if Names (I) = ',' then
            if Column_Index (Data, T, Names (Start .. I - 1)) /= Index then return False; end if;
            Index := Index + 1; Start := I + 1;
         end if;
      end loop;
      return Index = Width and then Column_Index (Data, T, Names (Start .. Names'Last)) = Index;
   end Has_Columns;
   function Hex_Is (Sum : SHA.Digest; Data : E.Bytes; Expected : E.Span) return Boolean is
      Hex_Digits : constant String := "0123456789abcdef";
   begin
      if not TValid (Data, Expected) then return False; end if;
      declare Raw : constant E.Bytes := TB (Data, Expected); begin
         return Raw'Length = Sum'Length * 2 and then
           (for all I in Sum'Range => Raw (Raw'First + E.Count (I - Sum'First) * 2) = Character'Pos (Hex_Digits (Integer (Sum (I) / 16) + 1))
             and then Raw (Raw'First + E.Count (I - Sum'First) * 2 + 1) = Character'Pos (Hex_Digits (Integer (Sum (I) mod 16) + 1)));
      end;
   end Hex_Is;
   function Hash (Data : E.Bytes; Raw, Expected : E.Span) return Boolean is
      C : SHA.Context := SHA.Initial;
   begin
      if not BValid (Data, Raw) and then not TValid (Data, Raw) then return False; end if;
      declare Bytes : constant E.Bytes := (if BValid (Data, Raw) then B (Data, Raw) else TB (Data, Raw)); begin
         for Byte of Bytes loop SHA.Update (C, Attest.Byte_Array'(0 => Attest.Byte (Byte))); end loop;
         return Hex_Is (SHA.Final (C), Data, Expected);
      end;
   end Hash;
   function MAC (Data : E.Bytes; Key, Raw, Expected : E.Span; Domain : String) return Boolean is
   begin
      if not BValid (Data, Key) or else not BValid (Data, Raw) then return False; end if;
      declare K : constant E.Bytes := B (Data, Key); M : constant E.Bytes := B (Data, Raw); begin
         return Hex_Is (H.Mac (K, M, (K'First, K'Length), (M'First, M'Length), Domain), Data, Expected);
      end;
   end MAC;
   function Object_Width (Data : E.Bytes; Item : E.Span; Width : E.Count) return Boolean is
      V : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if Scoped_Transport then
         return Source_Valid (Data, Item) and then E.Text_Is (Data, E.Decode (Data, OA.Field (Data, Item, "type"), E.Operation), "dict")
           and then SA.Member_Count (Data, Item) = Width;
      else
         return RA.Source_Valid (Data, Item, False) and then V.Form = E.Object_Value
           and then E.Array_Length (Data, V.Children) = Width;
      end if;
   end Object_Width;

   function Hex_Bytes (Raw : E.Bytes; Data : E.Bytes; Encoded : E.Span) return Boolean is
      Hex_Digits : constant String := "0123456789abcdef";
   begin
      if not TValid (Data, Encoded) or else Raw'Length > E.Count'Last / 2 then return False; end if;
      declare Got : constant E.Bytes := TB (Data, Encoded); begin
         return Got'Length = Raw'Length * 2 and then (for all I in Raw'Range =>
           Got (Got'First + (I - Raw'First) * 2) = Character'Pos (Hex_Digits (Integer (Raw (I) / 16) + 1))
           and then Got (Got'First + (I - Raw'First) * 2 + 1) = Character'Pos (Hex_Digits (Integer (Raw (I) mod 16) + 1)));
      end;
   end Hex_Bytes;
   -- Original resource_run_ledger.dto_record, not a second model/codec.
   -- Every typed field is joined recursively to its original JSON operand.
   function Legacy (Data : E.Bytes; Typed, Encoded : E.Span) return Boolean
     with Subprogram_Variant => (Decreases => Typed.Length)
   is
      V : constant E.View := E.Decode (Data, Typed, E.Operation);
      Fields : constant E.Span := (if Scoped_Transport then
         E.Decode (Data, OA.Field (Data, Typed, "fields"), E.Operation).Children else V.Children);
      Is_Record : constant Boolean := (if Scoped_Transport then
        R.Archive_Record_Is (Data, Typed, "RunContext") or else R.Archive_Record_Is (Data, Typed, "RunBinding") or else
        R.Archive_Record_Is (Data, Typed, "RunRow") or else R.Archive_Record_Is (Data, Typed, "RunState") or else
        R.Archive_Record_Is (Data, Typed, "RunObservation") or else R.Archive_Record_Is (Data, Typed, "RunRequest")
        else V.Form = E.Record_Value);
   begin
      if not Source_Valid (Data, Typed) or else not Source_Valid (Data, Encoded) then return False; end if;
      if Is_None (Data, Typed) then return Is_None (Data, Encoded);
      elsif BValid (Data, Typed) then
         return Object_Width (Data, Encoded, 1) and then Hex_Bytes (B (Data, Typed), Data, F (Data, Encoded, "bytes"));
      elsif R.Archive_Integer_Valid (Data, Typed) then
         return Object_Width (Data, Encoded, 2)
           and then R.Archive_Boolean_Is (Data, F (Data, Encoded, "negative"), R.Archive_Integer_Negative (Data, Typed))
           and then Hex_Bytes (R.Archive_Integer_Magnitude (Data, Typed), Data, F (Data, Encoded, "magnitude"));
      elsif TValid (Data, Typed) then return Same (Data, Typed, Encoded);
      elsif Is_Record then
         if E.Array_Length (Data, Fields) > E.Count'Last - 2
           or else not Object_Width (Data, Encoded, E.Array_Length (Data, Fields) + 2)
           or else not N (Data, F (Data, Encoded, "schema_version"), 1) then return False; end if;
         if Scoped_Transport then
            if not RA.Ordered_Source_Value_Matches (Data, Data, OA.Field (Data, Typed, "type"),
              F (Data, Encoded, "type"), False, True) then return False; end if;
         elsif not E.Bytes_Valid (Data, V.Record_Name) or else not TValid (Data, F (Data, Encoded, "type"))
           or else E.Materialize (Data, V.Record_Name) /= TB (Data, F (Data, Encoded, "type")) then return False; end if;
         for I in E.Count range 1 .. E.Array_Length (Data, Fields) loop
            declare Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, Fields, I - 1), E.Finalization);
                    Key : constant E.Span := E.Array_Element (Data, Pair.Children, 0);
                    Value : constant E.Span := E.Array_Element (Data, Pair.Children, 1);
                    Key_View : constant E.View := E.Decode (Data, Key,
                      (if Scoped_Transport then E.Operation else E.Finalization)); begin
               -- Field names are metadata at their explicit carrier layer;
               -- full Source_Valid(Typed) above validates the record grammar.
               if Key_View.Form /= E.Text_Value or else not E.Bytes_Valid (Data, Key_View.Payload) then return False; end if;
               declare Name : constant E.Bytes := E.Materialize (Data, Key_View.Payload); Word : String (1 .. Name'Length); begin
                  for K in Word'Range loop Word (K) := Character'Val (Name (Name'First + E.Count (K - Word'First))); end loop;
                  if not Legacy (Data, Value, F (Data, Encoded, Word)) then return False; end if;
               end;
            end;
         end loop;
         return True;
      elsif Seq (Data, Typed) then
         if not Seq (Data, Encoded) or else Len (Data, Typed) /= Len (Data, Encoded) then return False; end if;
         for I in E.Count range 1 .. Len (Data, Typed) loop
            if not Legacy (Data, Element (Data, Typed, I - 1), Element (Data, Encoded, I - 1)) then return False; end if;
         end loop;
         return True;
      else return False; end if;
   end Legacy;

      Source : constant E.Span := F (Data, Projection, "source");
      Receipt : constant E.Span := F (Data, Projection, "owner_sql_source");
      Paths : constant E.Span := F (Data, Owner, "paths");
      Selected : constant E.Span := F (Data, Owner, "selected_files");
      Installation : constant E.Span := F (Data, Owner, "installation");
      Locations : constant E.Span := F (Data, Installation, "paths");
      Authority : constant E.Span := F (Data, Locations, "authority_root");
      State : constant E.Span := F (Data, Locations, "state");
      Files : constant E.Span := F (Data, Receipt, "files");
      DBs : constant E.Span := F (Data, Receipt, "databases");
      Journals : constant E.Span := F (Data, Receipt, "journals");
      History_Owner : constant E.Span := F (Data, Projection, "history_owner");
      Key : constant E.Span := F (Data, Find_Joined (Data, Paths, Authority, "/authority/issuer/state/issuer-key.bin"), "raw");
      UKey : constant E.Span := F (Data, Find_Joined (Data, Paths, Authority, "/authority/universe/root/universe-key.bin"), "raw");
      Config : constant E.Span := F (Data, Receipt, "scoped_config");
      Lease : constant E.Span := F (Data, Receipt, "lease_genesis");
      function JSON (Data : E.Bytes; Raw, Value : E.Span; Canonical : Boolean := True) return Boolean is
        (P.JSON_Source_Value_Matches (Data, Raw, Value, Canonical, Scoped_Transport));
      function Root_History_Matches return Boolean is
         Expected : constant E.Span := F (Data, History_Owner, "root_events");
         Position : E.Count := 0;
         function Columns_Match (T, Row, Event : E.Span; Names : String) return Boolean is
            Start : Positive := Names'First;
         begin
            for I in Names'Range loop
               if Names (I) = ',' then
                  if not Same (Data, Cell (Data, T, Row, Names (Start .. I - 1)),
                    F (Data, Event, Names (Start .. I - 1))) then return False; end if;
                  Start := I + 1;
               end if;
            end loop;
            return Same (Data, Cell (Data, T, Row, Names (Start .. Names'Last)),
              F (Data, Event, Names (Start .. Names'Last)));
         end Columns_Match;
      begin
         if not Seq (Data, Expected) then return False; end if;
         for I in E.Count range 1 .. Len (Data, Paths) loop
            declare
               SQL : constant E.Span := F (Data, Element (Data, Paths, I - 1), "logical_database");
               Events : constant E.Span := F (Data, SQL, "authenticated_root_events");
               T : constant E.Span := Table (Data, SQL, "events");
               Rows : constant E.Span := F (Data, T, "rows");
               V2 : constant Boolean := Has_Columns (Data, T,
                 "seq,event_id,previous,generation,operation,subject_kind,subject,subgeneration,kind,actor,record,base,mac", 13);
            begin
               if Events.Length > 0 then
                  if not Seq (Data, Events) or else not Database_Well_Formed (Data, SQL)
                    or else not Seq (Data, Rows) or else Len (Data, Events) /= Len (Data, Rows)
                    or else (not V2 and then not Has_Columns (Data, T,
                      "event_id,previous,operation,kind,record,mac", 6)) then return False; end if;
                  for K in E.Count range 1 .. Len (Data, Events) loop
                     declare
                        Event : constant E.Span := Element (Data, Events, K - 1);
                        Row : constant E.Span := Element (Data, Rows, K - 1);
                        Raw : constant E.Span := Cell (Data, T, Row, "record");
                        Retained : constant E.Span := F (Data, Event, "retained_record");
                     begin
                        if Position >= Len (Data, Expected) or else
                          not Same (Data, Event, Element (Data, Expected, Position)) then return False; end if;
                        Position := Position + 1;
                        if V2 then
                           -- Exact original RootCustodyJournalV2._event output;
                           -- all 13 acquired columns and both wrapper values.
                           if not Object_Width (Data, Event, 14) or else not Object_Width (Data, Retained, 2)
                             or else not Columns_Match (T, Row, Event,
                               "seq,event_id,previous,generation,operation,subject_kind,subject,subgeneration,kind,actor,base,mac")
                             or else not P.Archive_Image_Matches (Data, Raw, Retained, True, Scoped_Transport, Scoped_Transport)
                             or else not P.Archive_Image_Matches (Data, F (Data, Retained, "original"),
                               F (Data, Event, "record"), False, Scoped_Transport, Scoped_Transport) then return False; end if;
                        else
                           -- Original retained V1 loader, with no aliases or
                           -- new authority derived from this factual array.
                           if not Object_Width (Data, Event, 6) or else not Columns_Match
                             (T, Row, Event, "event_id,previous,operation,kind,mac")
                             or else not P.Archive_Image_Matches (Data, Raw,
                               F (Data, Event, "record"), True, Scoped_Transport, Scoped_Transport) then return False; end if;
                        end if;
                     end;
                  end loop;
               end if;
            end;
         end loop;
         -- No captured journal remains the original empty/ENOENT domain.
         -- Actual journal acquisition/HMAC/native load is a separate conjunct.
         return Position = Len (Data, Expected);
      end Root_History_Matches;
      function Owned_File (Word : E.Span) return E.Span is
         Actual : E.Span := Find_Path (Data, Paths, Word);
      begin
         if Actual.Length = 0 then Actual := Find_Path (Data, Selected, Word); end if;
         return F (Data, Actual, "raw");
      end Owned_File;
      function File_Receipt (Root : E.Span; Suffix : String) return E.Span is
        (Find_Joined (Data, Files, Root, Suffix));
      function File_Value (Root : E.Span; Suffix : String) return E.Span is
        (F (Data, File_Receipt (Root, Suffix), "value"));
      function DB (Root : E.Span; Suffix : String) return E.Span is
         Actual : constant E.Span := Find_Joined (Data, Paths, Root, Suffix);
         Observed : constant E.Span := Find_Path (Data, DBs, F (Data, Actual, "path"));
         SQL : constant E.Span := F (Data, Actual, "logical_database");
      begin
         if Actual.Length = 0 or else not Database_Same (Data, SQL, F (Data, Observed, "logical_database"))
           or else not Database_Well_Formed (Data, SQL) then return Empty; end if;
         return SQL;
      end DB;
      function Journal (Name : String) return E.Span is
         Found : E.Span := Empty;
      begin
         for I in E.Count range 1 .. Len (Data, Journals) loop
            declare Item : constant E.Span := Element (Data, Journals, I - 1); begin
               if Text (Data, F (Data, Item, "kind"), Name) then
                  if Found.Length > 0 then return Empty; end if; Found := Item;
               end if;
            end;
         end loop;
         return Found;
      end Journal;
      function Row_Number (T : E.Span; Index : E.Count; Name : String := "ordinal") return E.Span is
         Rows : constant E.Span := F (Data, T, "rows"); Found : E.Span := Empty;
      begin
         for I in E.Count range 1 .. Len (Data, Rows) loop
            declare Row : constant E.Span := Element (Data, Rows, I - 1); begin
               if N (Data, Cell (Data, T, Row, Name), Index) then
                  if Found.Length > 0 then return Empty; end if; Found := Row;
               end if;
            end;
         end loop;
         return Found;
      end Row_Number;
      function Snapshot_Values (Snap, Material : E.Span; Proposed : Boolean := False) return Boolean is
      begin
         return Object_Width (Data, Snap, 5) and then
           Same (Data, F (Data, Snap, "state"), F (Data, Material, (if Proposed then "proposed" else "before")))
           and then Same (Data, F (Data, Snap, "history"), F (Data, Material, (if Proposed then "proposed_history" else "history")))
           and then Same (Data, F (Data, Snap, "rows"), F (Data, Material, (if Proposed then "proposed_rows" else "rows")))
           and then Same (Data, F (Data, Snap, "projection"), F (Data, Material, (if Proposed then "proposed_projection" else "projection")))
           and then Same (Data, F (Data, Snap, "buckets"), F (Data, Material, (if Proposed then "proposed_buckets" else "buckets")));
      end Snapshot_Values;
      function Snapshot (Snap, Material : E.Span; Proposed : Boolean := False) return Boolean is
         Values : constant E.Span := F (Data, Snap, "fields");
      begin
         -- snapshot_record is S.record(the complete five-value dictionary),
         -- not a transported ScopedSnapshot DTO or an untagged value mapping.
         return Object_Width (Data, Snap, 2) and then Text (Data, F (Data, Snap, "type"), "dict")
           and then Object_Width (Data, Values, 5)
           and then P.Scoped_Record_Matches (Data, F (Data, Values, "state"),
             F (Data, Material, (if Proposed then "proposed" else "before")), Scoped_Transport, Scoped_Transport)
           and then P.Scoped_Record_Matches (Data, F (Data, Values, "history"),
             F (Data, Material, (if Proposed then "proposed_history" else "history")), Scoped_Transport, Scoped_Transport)
           and then P.Scoped_Record_Matches (Data, F (Data, Values, "rows"),
             F (Data, Material, (if Proposed then "proposed_rows" else "rows")), Scoped_Transport, Scoped_Transport)
           and then P.Scoped_Record_Matches (Data, F (Data, Values, "projection"),
             F (Data, Material, (if Proposed then "proposed_projection" else "projection")), Scoped_Transport, Scoped_Transport)
           and then P.Scoped_Record_Matches (Data, F (Data, Values, "buckets"),
             F (Data, Material, (if Proposed then "proposed_buckets" else "buckets")), Scoped_Transport, Scoped_Transport);
      end Snapshot;
      function Next_Packet (Old, New_Value : E.Span) return Boolean is
      begin
         return Same (Data, F (Data, Old, "proposed"), F (Data, New_Value, "before"))
           and then Same (Data, F (Data, Old, "proposed_history"), F (Data, New_Value, "history"))
           and then Same (Data, F (Data, Old, "proposed_rows"), F (Data, New_Value, "rows"))
           and then Same (Data, F (Data, Old, "proposed_projection"), F (Data, New_Value, "projection"))
           and then Same (Data, F (Data, Old, "proposed_buckets"), F (Data, New_Value, "buckets"));
      end Next_Packet;
      function Journal_Matches (Name, Suffix, Meta_Name, Events_Name, Domain : String; Is_Scoped, Is_Observation : Boolean) return Boolean is
         Value : constant E.Span := Journal (Name);
         SQL : constant E.Span := DB (Authority, Suffix);
         Meta : constant E.Span := Table (Data, SQL, Meta_Name);
         Events : constant E.Span := Table (Data, SQL, Events_Name);
         MRows : constant E.Span := F (Data, Meta, "rows");
         MRow : constant E.Span := Element (Data, MRows, 0);
         Bodies : constant E.Span := F (Data, Value, "events");
         Receipts : constant E.Span := F (Data, Value, "event_receipts");
         Anchor : constant E.Span := F (Data, Value, "anchor");
         Initial : constant E.Span := F (Data, Value, "initial");
         Old_Packet : E.Span := Empty;
         Old_Head : E.Span := F (Data, F (Data, Value, "genesis"), "event_head");
      begin
         if Value.Length = 0 or else SQL.Length = 0 or else Len (Data, F (Data, SQL, "tables")) /= 2
           or else not Has_Columns (Data, Meta, (if Is_Scoped then "binding,genesis,original_prefix,snapshot,head,mac" else "binding,genesis,head,mac"), (if Is_Scoped then 6 else 4))
           or else not Has_Columns (Data, Events, (if Is_Scoped then "ordinal,request_id,record,mac" elsif Is_Observation then "ordinal,cause,reservation,record,mac" else "ordinal,record,mac"), (if Is_Scoped then 4 elsif Is_Observation then 5 else 3))
           or else Len (Data, MRows) /= 1 or else not Seq (Data, Bodies) or else not Seq (Data, Receipts)
           or else Len (Data, Bodies) /= Len (Data, Receipts) or else Len (Data, Bodies) /= Len (Data, F (Data, Events, "rows"))
           or else not Joined (Data, F (Data, Value, "path"), Authority, Suffix)
           or else not JSON (Data, Cell (Data, Meta, MRow, "binding"), F (Data, Value, "binding"))
           or else not JSON (Data, Cell (Data, Meta, MRow, "genesis"), F (Data, Value, "genesis"))
           or else not SF (Data, Anchor, Value, "binding") or else not SF (Data, Anchor, Value, "genesis")
           or else not SF (Data, Anchor, Value, "head")
           or else not JSON (Data, F (Data, Value, "anchor_json"), Anchor)
           or else not Same (Data, Cell (Data, Meta, MRow, "head"), F (Data, Value, "head"))
           or else not MAC (Data, Key, F (Data, Value, "anchor_json"), Cell (Data, Meta, MRow, "mac"), Domain & "head" & Character'Val (0)) then return False; end if;
         if Is_Scoped then
            if not Object_Width (Data, Anchor, 5) or else not Object_Width (Data, Initial, 3)
              or else not SF (Data, Initial, Value, "binding") or else not SF (Data, Initial, Value, "genesis")
              or else not Same (Data, F (Data, Initial, "original_prefix"), F (Data, Config, "original_prefix"))
              or else not JSON (Data, F (Data, Value, "initial_json"), Initial)
              or else not Hash (Data, F (Data, Value, "initial_json"), F (Data, Value, "initial_head"))
              or else not Same (Data, F (Data, Anchor, "original_prefix"), F (Data, Config, "original_prefix"))
              or else not JSON (Data, Cell (Data, Meta, MRow, "original_prefix"), F (Data, Config, "original_prefix"))
              or else not JSON (Data, Cell (Data, Meta, MRow, "snapshot"), F (Data, Anchor, "snapshot"))
              or else not Same (Data, F (Data, Value, "genesis"), F (Data, Config, "genesis"))
              or else not Same (Data, F (Data, Value, "binding"), F (Data, Receipt, "scoped_binding")) then return False; end if;
            Old_Head := F (Data, Value, "initial_head");
         elsif not Object_Width (Data, Anchor, 3) then return False;
         end if;
         for I in E.Count range 1 .. Len (Data, Bodies) loop
            declare
               Row : constant E.Span := Row_Number (Events, I - 1);
               Body_Value : constant E.Span := Element (Data, Bodies, I - 1);
               ER : constant E.Span := Element (Data, Receipts, I - 1);
               Raw : constant E.Span := Cell (Data, Events, Row, "record");
               EP : constant E.Span := F (Data, ER, "packet");
               Native : constant E.Span := F (Data, ER, "native");
            begin
               if Row.Length = 0 or else not Same (Data, Body_Value, F (Data, ER, "event"))
                 or else not Same (Data, Raw, F (Data, ER, "raw")) or else not JSON (Data, Raw, Body_Value)
                 or else not Same (Data, F (Data, Body_Value, "prior"), Old_Head)
                 or else not MAC (Data, Key, Raw, Cell (Data, Events, Row, "mac"), Domain & "event" & Character'Val (0)) then return False; end if;
               if Is_Scoped then
                  declare Replay : constant R.Scoped_Replay_Result := R.Reestablish_Scoped_Observation (Data, Native); begin
                     if not Object_Width (Data, Body_Value, 7)
                       or else not Text (Data, F (Data, Body_Value, "schema"), "worldline.protected-scoped-resource-event-v1")
                       or else not P.Scoped_Record_Matches (Data, F (Data, Body_Value, "packet"), EP, Scoped_Transport, Scoped_Transport)
                       or else not P.Scoped_Record_Matches (Data, F (Data, Body_Value, "native"), Native, Scoped_Transport, Scoped_Transport)
                       or else not Same (Data, F (Data, Body_Value, "principal"), F (Data, Receipt, "scoped_binding"))
                       -- IMAGE and old S source encodings both join every
                       -- actual original source value to its acquired receipt.
                       or else not P.Source_Record_Matches (Data, F (Data, Body_Value, "source"), F (Data, ER, "source"), Scoped_Transport, Scoped_Transport)
                       or else not P.Scoped_Record_Matches (Data, F (Data, F (Data, ER, "source"), "packet"), EP, Scoped_Transport, Scoped_Transport)
                       or else not Object_Width (Data, F (Data, Body_Value, "reply"), 6)
                       or else not Text (Data, F (Data, F (Data, Body_Value, "reply"), "schema"), "worldline.protected-scoped-resource-reply-v1")
                       or else not Text (Data, F (Data, F (Data, Body_Value, "reply"), "status"), "READY")
                       or else not P.Id_Hex (Data, F (Data, F (Data, EP, "request"), "request_id"), F (Data, F (Data, Body_Value, "reply"), "request_id"))
                       or else not Snapshot (F (Data, F (Data, Body_Value, "reply"), "snapshot"), EP, True)
                       or else not P.Scoped_Record_Matches (Data, F (Data, F (Data, Body_Value, "reply"), "native"), Native, Scoped_Transport, Scoped_Transport)
                       or else not Same (Data, F (Data, F (Data, Body_Value, "reply"), "prior"), Old_Head)
                       or else Replay.State /= R.Native_Redecided or else Replay.Roster_Entry /= R.Check_Entry
                       or else Replay.Native_Status /= 0
                       or else not R.Scoped_Material_Matches (Data, Native, EP)
                       or else not Same (Data, Cell (Data, Events, Row, "request_id"), F (Data, F (Data, EP, "request"), "request_id"))
                       or else (I = 1 and then not Snapshot (F (Data, Config, "genesis"), EP))
                       or else (I > 1 and then not Next_Packet (Old_Packet, EP)) then return False; end if;
                  end;
                  for K in E.Count range 1 .. I - 1 loop
                     if Same (Data, Cell (Data, Events, Row, "request_id"), Cell (Data, Events, Row_Number (Events, K - 1), "request_id")) then return False; end if;
                  end loop;
                  Old_Packet := EP;
               elsif Is_Observation then
                  if not Object_Width (Data, Body_Value, 5)
                    or else not Text (Data, F (Data, Body_Value, "schema"), "worldline.protected-scoped-observation-event-v1")
                    or else not Same (Data, F (Data, Body_Value, "cause"), Cell (Data, Events, Row, "cause"))
                    or else not Same (Data, F (Data, Body_Value, "reservation"), Cell (Data, Events, Row, "reservation")) then return False; end if;
               elsif not Object_Width (Data, Body_Value, 4) then return False;
               end if;
               -- The next predecessor is the actual canonical raw event digest.
               if I < Len (Data, Bodies) then
                  Old_Head := F (Data, Element (Data, Bodies, I), "prior");
               else Old_Head := F (Data, Value, "head"); end if;
               if not Hash (Data, Raw, Old_Head) then return False; end if;
            end;
         end loop;
         if Len (Data, Bodies) = 0 and then not Same (Data, Old_Head, F (Data, Value, "head")) then return False; end if;
         if Is_Scoped then
            return (if Len (Data, Bodies) = 0 then Same (Data, F (Data, Anchor, "snapshot"), F (Data, Config, "genesis"))
              else Snapshot (F (Data, Anchor, "snapshot"), Old_Packet, True))
              and then Snapshot (F (Data, Anchor, "snapshot"), Packet)
              and then Same (Data, F (Data, Anchor, "snapshot"), F (Data, Source, "scoped_before"));
         elsif Is_Observation then
            return Same (Data, Bodies, F (Data, History_Owner, "observation_events"))
              and then Same (Data, F (Data, Value, "head"), F (Data, History_Owner, "observation_head"))
              and then Same (Data, F (Data, Value, "binding"), F (Data, Receipt, "scoped_binding"))
              and then Same (Data, F (Data, Value, "genesis"), F (Data, Config, "observation_genesis"));
         else
            return Same (Data, Bodies, F (Data, Source, "launch_prefix"))
              and then Same (Data, Bodies, F (Data, History_Owner, "launch_events"))
              and then Same (Data, F (Data, Value, "head"), F (Data, History_Owner, "launch_head"))
              and then Same (Data, F (Data, Value, "binding"), F (Data, Projection, "binding"))
              and then Same (Data, F (Data, Value, "genesis"), F (Data, F (Data, Projection, "resource_config"), "launch_genesis"));
         end if;
      end Journal_Matches;

      function Decoded_Cell (Database, T, Row : E.Span; Name : String) return E.Span is
         Found : E.Span := Empty;
      begin
         for I in E.Count range 1 .. Len (Data, DBs) loop
            declare D : constant E.Span := Element (Data, DBs, I - 1); Decoded : constant E.Span := F (Data, D, "decoded"); begin
               if F (Data, Find_Path (Data, Paths, F (Data, D, "path")), "logical_database") = Database then
                  for K in E.Count range 1 .. Len (Data, Decoded) loop
                     declare Item : constant E.Span := Element (Data, Decoded, K - 1); Cells : constant E.Span := F (Data, Item, "cells"); begin
                        if Same (Data, F (Data, Item, "table"), F (Data, T, "name")) and then Same (Data, F (Data, Item, "row"), Row) then
                           for M in E.Count range 1 .. Len (Data, Cells) loop
                              declare C : constant E.Span := Element (Data, Cells, M - 1); begin
                                 if Text (Data, F (Data, C, "column"), Name) then
                                    if Found.Length > 0 or else not Same (Data, F (Data, C, "raw"), Cell (Data, T, Row, Name))
                                      or else not JSON (Data, F (Data, C, "raw"), F (Data, C, "value"), False) then return Empty; end if;
                                    Found := F (Data, C, "value");
                                 end if;
                              end;
                           end loop;
                        end if;
                     end;
                  end loop;
               end if;
            end;
         end loop;
         return Found;
      end Decoded_Cell;
      function Chain_Hash (Raw, Prior, Expected : E.Span; Domain : String) return Boolean is
         C : SHA.Context := SHA.Initial;
         function Digit (Byte : E.Q.Byte) return Integer is
           (if Byte in 48 .. 57 then Integer (Byte) - 48 elsif Byte in 97 .. 102 then Integer (Byte) - 87 else -1);
      begin
         if not TValid (Data, Prior) or else (not BValid (Data, Raw) and then not TValid (Data, Raw)) then return False; end if;
         declare Previous : constant E.Bytes := TB (Data, Prior);
                 Bytes : constant E.Bytes := (if BValid (Data, Raw) then B (Data, Raw) else TB (Data, Raw)); begin
            if Previous'Length /= 64 then return False; end if;
            for Letter of Domain loop SHA.Update (C, Attest.Byte_Array'(0 => Character'Pos (Letter))); end loop;
            for I in E.Count range 0 .. 31 loop
               declare Hi : constant Integer := Digit (Previous (Previous'First + I * 2));
                       Lo : constant Integer := Digit (Previous (Previous'First + I * 2 + 1)); begin
                  if Hi < 0 or else Lo < 0 then return False; end if;
                  SHA.Update (C, Attest.Byte_Array'(0 => Attest.Byte (Hi * 16 + Lo)));
               end;
            end loop;
            for Byte of Bytes loop SHA.Update (C, Attest.Byte_Array'(0 => Attest.Byte (Byte))); end loop;
            return Hex_Is (SHA.Final (C), Data, Expected);
         end;
      end Chain_Hash;
      function Authority_History (Universe_Mode : Boolean) return Boolean is
         SQL : constant E.Span := DB (Authority, (if Universe_Mode then "/authority/universe/root/universes.sqlite" else "/authority/issuer/state/capabilities.sqlite"));
         T : constant E.Span := Table (Data, SQL, "events");
         Rows : constant E.Span := F (Data, T, "rows");
         Head : constant E.Span := File_Value (Authority, (if Universe_Mode then "/authority/universe/root/registry.json" else "/authority/issuer/state/head.json"));
         Base : constant E.Span := F (Data, Receipt, (if Universe_Mode then "registry_base" else "issuer_base"));
         Base_JSON : constant E.Span := F (Data, Receipt, (if Universe_Mode then "registry_base_json" else "issuer_base_json"));
         Observation : constant E.Span := F (Data, Source, (if Universe_Mode then "universe" else "issuer_head"));
         Previous : E.Span := Empty;
         Last_Body : E.Span := Empty;
      begin
         if SQL.Length = 0 or else Len (Data, F (Data, SQL, "tables")) /= 1
           or else not Has_Columns (Data, T, (if Universe_Mode then "universe_id,seq,previous_hash,body_json,event_hash" else "seq,previous_hash,body_json,event_hash"), (if Universe_Mode then 5 else 4))
           or else not Object_Width (Data, Head, (if Universe_Mode then 6 else 5))
           or else not Object_Width (Data, Base, (if Universe_Mode then 5 else 4))
           or else not N (Data, F (Data, Head, "schema"), 1)
           or else not SF (Data, Head, Base, "schema") or else not SF (Data, Head, Base, "sequence")
           or else not SF (Data, Head, Base, "event_head")
           or else not JSON (Data, Base_JSON, Base)
           or else not MAC (Data, (if Universe_Mode then UKey else Key), Base_JSON, F (Data, Head, "mac"),
             (if Universe_Mode then "COSMOGONY-UNIVERSE-REGISTRY-v1" else "COSMOGONY-PROTECTED-ISSUER-HEAD-v1") & Character'Val (0))
           or else not SF (Data, Head, Observation, "sequence") or else not SF (Data, Head, Observation, "event_head") then return False; end if;
         if Universe_Mode then
            if Len (Data, Rows) = 0 or else not N (Data, F (Data, Head, "sequence"), Len (Data, Rows) - 1)
              or else not SF (Data, Head, Base, "universe_id") or else not SF (Data, Head, Base, "genesis_sha256")
              or else not SF (Data, Head, Observation, "universe_id")
              or else not Hash (Data, F (Data, File_Receipt (Authority, "/authority/universe/root/genesis.json"), "raw"), F (Data, Head, "genesis_sha256"))
              or else not Same (Data, F (Data, Head, "genesis_sha256"), F (Data, F (Data, Projection, "gate_config"), "universe_genesis_sha256"))
              or else not Text (Data, F (Data, Observation, "authority"), "LOCAL_ROOT_ANCHORED_UNIVERSE_VALUE_ONLY") then return False; end if;
         else
            if not N (Data, F (Data, Head, "sequence"), Len (Data, Rows))
              or else not SF (Data, Head, Base, "policy_sha256")
              or else not Hash (Data, F (Data, File_Receipt (Authority, "/authority/issuer/state/policy.json"), "raw"), F (Data, Head, "policy_sha256"))
              or else not Same (Data, F (Data, Head, "mac"), F (Data, Observation, "head_mac"))
              or else not Text (Data, F (Data, Observation, "authority"), "LOCAL_ROOT_ANCHORED_CAPABILITY_VALUE_ONLY") then return False; end if;
         end if;
         for I in E.Count range 1 .. Len (Data, Rows) loop
            declare Row : constant E.Span := Row_Number (T, I - 1, "seq");
                    Raw : constant E.Span := Cell (Data, T, Row, "body_json");
                    Body_Value : constant E.Span := Decoded_Cell (SQL, T, Row, "body_json");
                    Prior : constant E.Span := Cell (Data, T, Row, "previous_hash"); begin
               if Row.Length = 0 or else Body_Value.Length = 0 or else not JSON (Data, Raw, Body_Value)
                 or else (I = 1 and then not Text (Data, Prior, "0000000000000000000000000000000000000000000000000000000000000000"))
                 or else (I > 1 and then not Same (Data, Prior, Previous))
                 or else not Chain_Hash (Raw, Prior, Cell (Data, T, Row, "event_hash"),
                   (if Universe_Mode then "COSMOGONY-EVENT-v1" else "COSMOGONY-CAPABILITY-EVENT-v1") & Character'Val (0)) then return False; end if;
               if Universe_Mode then
                  if not Same (Data, Cell (Data, T, Row, "universe_id"), F (Data, Observation, "universe_id"))
                    or else (I = 1 and then (not Text (Data, F (Data, Body_Value, "kind"), "genesis")
                      or else not Same (Data, F (Data, Body_Value, "args"), File_Value (Authority, "/authority/universe/root/genesis.json")))) then return False; end if;
               end if;
               Previous := Cell (Data, T, Row, "event_hash"); Last_Body := Body_Value;
            end;
         end loop;
         if Len (Data, Rows) = 0 then
            return not Universe_Mode and then Text (Data, F (Data, Head, "event_head"), "0000000000000000000000000000000000000000000000000000000000000000");
         else
            return Same (Data, Previous, F (Data, Head, "event_head")) and then
              (not Universe_Mode or else (Same (Data, F (Data, Last_Body, "record"), F (Data, Observation, "record"))
                and then Text (Data, F (Data, F (Data, Last_Body, "record"), "parent_id"), "0000000000000000000000000000000000000000000000000000000000000000")));
         end if;
      end Authority_History;
      function Store_Schema (SQL : E.Span) return Boolean is
         Actual : constant E.Span := F (Data, SQL, "schema");
         Expected : constant E.Span := F (Data, F (Data, Lease, "store"), "schema");
         Count : E.Count := 0;
         function Internal (Name : E.Span) return Boolean is
         begin
            if not TValid (Data, Name) then return False; end if;
            declare Bytes : constant E.Bytes := TB (Data, Name); Prefix : constant String := "sqlite_"; begin
               return Bytes'Length >= Prefix'Length and then (for all I in Prefix'Range => Bytes (Bytes'First + E.Count (I - Prefix'First)) = Character'Pos (Prefix (I)));
            end;
         end Internal;
      begin
         if not Seq (Data, Expected) or else not Same (Data, Element (Data, Element (Data, F (Data, SQL, "user_version"), 0), 0), F (Data, F (Data, Lease, "store"), "version")) then return False; end if;
         for I in E.Count range 1 .. Len (Data, Actual) loop
            declare A : constant E.Span := Element (Data, Actual, I - 1); Found : E.Count := 0; begin
               if not Internal (Element (Data, A, 1)) then
                  Count := Count + 1;
                  for K in E.Count range 1 .. Len (Data, Expected) loop
                     declare X : constant E.Span := Element (Data, Expected, K - 1); begin
                        if Seq (Data, X) and then Len (Data, X) = 4 and then Same (Data, Element (Data, A, 0), Element (Data, X, 0))
                          and then Same (Data, Element (Data, A, 1), Element (Data, X, 1)) and then Same (Data, Element (Data, A, 2), Element (Data, X, 2))
                          and then Same (Data, Element (Data, A, 4), Element (Data, X, 3)) then Found := Found + 1; end if;
                     end;
                  end loop;
                  if Found /= 1 then return False; end if;
               end if;
            end;
         end loop;
         return Count = Len (Data, Expected);
      end Store_Schema;
      function Store_Matches return Boolean is
         SQL : constant E.Span := DB (State, "/worldline.sqlite3");
         Meta : constant E.Span := Table (Data, SQL, "meta");
         Roots : constant E.Span := Table (Data, SQL, "roots");
         Worlds : constant E.Span := Table (Data, SQL, "worlds");
         Actual_Roots : constant E.Span := F (Data, Source, "actual_roots");
         Prime : constant E.Span := F (Data, Source, "actual_prime");
         Prime_Query : constant E.Span := F (Data, Receipt, "prime_query");
         Selected_Row : constant E.Span := F (Data, Prime_Query, "row");
         Selector : constant E.Span := F (Data, Prime_Query, "selector");
         Root_Rows : constant E.Span := F (Data, Roots, "rows");
         World_Rows : constant E.Span := F (Data, Worlds, "rows");
         Prime_Meta : constant E.Span := Named_Row (Data, Meta, "key", "primeInstance");
         function Root_Less (Left, Right : E.Span) return Boolean is
            L : constant E.Span := F (Data, Left, "path"); R : constant E.Span := F (Data, Right, "path");
         begin
            if not BValid (Data, L) or else not BValid (Data, R) then return False; end if;
            declare LB : constant E.Bytes := B (Data, L); RB : constant E.Bytes := B (Data, R); begin
               for I in E.Count range 1 .. E.Count'Min (LB'Length, RB'Length) loop
                  if LB (LB'First + I - 1) /= RB (RB'First + I - 1) then return LB (LB'First + I - 1) < RB (RB'First + I - 1); end if;
               end loop;
               return LB'Length < RB'Length;
            end;
         end Root_Less;
         function Truthy (Item : E.Span) return Boolean is
           (SQL_Source.Truthy (Data, Item, Scoped_Transport));
         function Descendants return Boolean is
            Total : E.Count := 0;
            Target : constant E.Span := F (Data, Prime, "instance_id");
         begin
            for I in E.Count range 1 .. Len (Data, World_Rows) loop
               declare Parent : E.Span := Cell (Data, Worlds, Element (Data, World_Rows, I - 1), "parent_instance");
                       Steps : E.Count := 0; begin
                  while not Is_None (Data, Parent) loop
                     if Steps >= Len (Data, World_Rows) then return False; end if;
                     Steps := Steps + 1;
                     if Same (Data, Parent, Target) then Total := Total + 1; exit; end if;
                     declare Next_Row : E.Span := Empty; begin
                        for K in E.Count range 1 .. Len (Data, World_Rows) loop
                           declare Candidate : constant E.Span := Element (Data, World_Rows, K - 1); begin
                              if Same (Data, Cell (Data, Worlds, Candidate, "instance_id"), Parent) then
                                 if Next_Row.Length > 0 then return False; end if; Next_Row := Candidate;
                              end if;
                           end;
                        end loop;
                        if Next_Row.Length = 0 then return False; end if;
                        Parent := Cell (Data, Worlds, Next_Row, "parent_instance");
                     end;
                  end loop;
               end;
            end loop;
            return N (Data, F (Data, Prime, "descendants"), Total);
         end Descendants;
      begin
         if SQL.Length = 0 or else not Store_Schema (SQL)
           or else not Has_Columns (Data, Meta, "key,value", 2)
           or else not Has_Columns (Data, Roots, "root_key,path,display_path,kind,device,primary_root,generation_id,manifest_root,added_at", 9)
           or else not Has_Columns (Data, Worlds, "instance_id,alias,parent_instance,parent_content,cause,actor,born,ended,state,components,content_id,payload_path,mission_hash,agent_reference,evidence,workspace,base_payload_path,base_root,root_set_hash,delta_hash,delta,conflicts,contamination,world_kind,complexity,risk,payload_pruned,pruned_at", 28)
           or else not Seq (Data, Actual_Roots) or else Len (Data, Actual_Roots) /= Len (Data, Root_Rows)
           or else not JSON (Data, Cell (Data, Meta, Named_Row (Data, Meta, "key", "protectedStoreGenesis"), "value"), F (Data, Source, "actual_store_genesis"), False)
           or else not JSON (Data, Cell (Data, Meta, Named_Row (Data, Meta, "key", "finalizationStoreId"), "value"), F (Data, Source, "actual_store_id"), False)
           or else not Same (Data, F (Data, Source, "actual_store_genesis"), F (Data, F (Data, Lease, "store"), "identity"))
           or else not Text (Data, F (Data, Prime_Query, "query"), "SELECT * FROM worlds WHERE instance_id=? OR alias=? OR content_id=?")
           or else not Object_Width (Data, Prime_Query, 6)
           or else not Seq (Data, F (Data, Prime_Query, "columns")) or else Len (Data, F (Data, Prime_Query, "columns")) /= 28
           or else not Text (Data, F (Data, Prime_Query, "affinity_query"), "SELECT CAST(? AS TEXT)")
           or else (if Truthy (Selector) then
             not SQL_Source.Text_Affinity_Matches (Data, Selector, F (Data, Prime_Query, "affinity"), Scoped_Transport, 17)
             else not Is_None (Data, F (Data, Prime_Query, "affinity")))
           or else (Prime_Meta.Length = 0 and then not Is_None (Data, Selector))
           or else (Prime_Meta.Length > 0 and then not JSON (Data, Cell (Data, Meta, Prime_Meta, "value"), Selector, False)) then return False; end if;
         for I in E.Count range 1 .. Len (Data, Actual_Roots) loop
            declare Root : constant E.Span := Element (Data, Actual_Roots, I - 1); Found : E.Count := 0; begin
               if not Object_Width (Data, Root, 9) then return False; end if;
               for K in E.Count range 1 .. Len (Data, Root_Rows) loop
                  declare Row : constant E.Span := Element (Data, Root_Rows, K - 1); begin
                     if Same (Data, Cell (Data, Roots, Row, "root_key"), F (Data, Root, "root_key")) then
                        Found := Found + 1;
                        for M in E.Count range 1 .. 9 loop
                           declare Column : constant E.Span := Element (Data, F (Data, Roots, "columns"), M - 1);
                                   Name : constant E.Bytes := TB (Data, Element (Data, Column, 1));
                                   Word : String (1 .. Name'Length); begin
                              for X in Word'Range loop Word (X) := Character'Val (Name (Name'First + E.Count (X - Word'First))); end loop;
                              if not Same (Data, Cell (Data, Roots, Row, Word), F (Data, Root, Word)) then return False; end if;
                           end;
                        end loop;
                     end if;
                  end;
               end loop;
               if Found /= 1 then return False; end if;
               for K in E.Count range 1 .. I - 1 loop
                  if SF (Data, Root, Element (Data, Actual_Roots, K - 1), "root_key") then return False; end if;
               end loop;
               if I > 1 then
                  declare Prior : constant E.Span := Element (Data, Actual_Roots, I - 2);
                          LP : constant E.Span := F (Data, Prior, "primary_root"); RP : constant E.Span := F (Data, Root, "primary_root"); begin
                     if not R.Archive_Integer_Valid (Data, LP) or else not R.Archive_Integer_Valid (Data, RP)
                       or else P.Number (Data, LP) < P.Number (Data, RP)
                       or else (P.Number (Data, LP) = P.Number (Data, RP) and then not Root_Less (Prior, Root)) then return False; end if;
                  end;
               end if;
            end;
         end loop;
         for M in E.Count range 1 .. 28 loop
            if not Same (Data, Element (Data, F (Data, Prime_Query, "columns"), M - 1),
              Element (Data, Element (Data, F (Data, Worlds, "columns"), M - 1), 1)) then return False; end if;
         end loop;
         if not Truthy (Selector) then return Is_None (Data, Prime) and then Is_None (Data, Selected_Row); end if;
         if Is_None (Data, Prime) or else not Object_Width (Data, Prime, 29)
           or else not Seq (Data, Selected_Row) or else Len (Data, Selected_Row) /= 28 then return False; end if;
         declare Found : E.Count := 0; begin
            for K in E.Count range 1 .. Len (Data, World_Rows) loop
               declare Row : constant E.Span := Element (Data, World_Rows, K - 1); Match : Boolean := True; begin
                  for M in E.Count range 1 .. 28 loop
                     declare Column : constant E.Span := Element (Data, F (Data, Worlds, "columns"), M - 1);
                             Name : constant E.Bytes := TB (Data, Element (Data, Column, 1)); Word : String (1 .. Name'Length); begin
                        for X in Word'Range loop Word (X) := Character'Val (Name (Name'First + E.Count (X - Word'First))); end loop;
                        if not Same (Data, Cell (Data, Worlds, Row, Word), Element (Data, Selected_Row, M - 1)) then Match := False; end if;
                     end;
                  end loop;
                  if Match then Found := Found + 1; end if;
               end;
            end loop;
            if Found /= 1 then return False; end if;
         end;
         for M in E.Count range 1 .. 28 loop
            declare Column : constant E.Span := Element (Data, F (Data, Worlds, "columns"), M - 1);
                    Name : constant E.Bytes := TB (Data, Element (Data, Column, 1)); Word : String (1 .. Name'Length);
                    Value : constant E.Span := Element (Data, Selected_Row, M - 1); begin
               for X in Word'Range loop Word (X) := Character'Val (Name (Name'First + E.Count (X - Word'First))); end loop;
               if Word in "components" | "evidence" | "workspace" | "delta" | "conflicts" | "contamination" then
                  if not JSON (Data, Value, F (Data, Prime, Word), False) then return False; end if;
               elsif Word = "payload_pruned" then
                  if not R.Archive_Integer_Valid (Data, Value) or else not R.Archive_Boolean_Is
                    (Data, F (Data, Prime, Word), P.Number (Data, Value) /= To_Big_Integer (0)) then return False; end if;
               elsif not Same (Data, Value, F (Data, Prime, Word)) then return False;
               end if;
            end;
         end loop;
         -- Bind the actual parameter storage class, not merely its CAST text:
         -- a BLOB whose bytes spell a TEXT ID must not select that TEXT row.
         return (SQL_Source.Parameter_Equals_Text (Data, Selector, F (Data, Prime, "instance_id"), Scoped_Transport, 17) or else
           SQL_Source.Parameter_Equals_Text (Data, Selector, F (Data, Prime, "alias"), Scoped_Transport, 17) or else
           SQL_Source.Parameter_Equals_Text (Data, Selector, F (Data, Prime, "content_id"), Scoped_Transport, 17)) and then Descendants;
      end Store_Matches;

      function Original_Prefix_Matches return Boolean is
         SQL : constant E.Span := DB (Authority, "/authority/resource/run-state-v1/ledger.sqlite");
         Meta : constant E.Span := Table (Data, SQL, "run_meta");
         Rows : constant E.Span := Table (Data, SQL, "run_rows");
         Events : constant E.Span := Table (Data, SQL, "run_events");
         MRow : constant E.Span := Element (Data, F (Data, Meta, "rows"), 0);
         Prefix : constant E.Span := F (Data, Config, "original_prefix");
         Typed : constant E.Span := F (Data, Receipt, "original_prefix_typed");
         Roster : constant E.Span := F (Data, Prefix, "rows");
         Event_Roster : constant E.Span := F (Data, Prefix, "events");
      begin
         if SQL.Length = 0 or else Len (Data, F (Data, SQL, "tables")) /= 3
           or else not Has_Columns (Data, Meta, "config_sha,genesis,head", 3)
           or else not Has_Columns (Data, Rows, "ordinal,record", 2)
           or else not Has_Columns (Data, Events, "ordinal,request_id,record", 3)
           or else Len (Data, F (Data, Meta, "rows")) /= 1
           or else not Object_Width (Data, Prefix, 4) or else not Object_Width (Data, Typed, 4)
           or else not JSON (Data, Cell (Data, Meta, MRow, "genesis"), F (Data, Prefix, "genesis"))
           or else not JSON (Data, Cell (Data, Meta, MRow, "head"), F (Data, Prefix, "state"))
           or else not Hash (Data, F (Data, File_Receipt (Authority, "/authority/resource/run-config-v1.json"), "raw"), Cell (Data, Meta, MRow, "config_sha"))
           or else not Same (Data, F (Data, File_Value (Authority, "/authority/resource/run-config-v1.json"), "genesis"), F (Data, Prefix, "genesis"))
           or else not Legacy (Data, F (Data, Typed, "genesis"), F (Data, Prefix, "genesis"))
           or else not Legacy (Data, F (Data, Typed, "state"), F (Data, Prefix, "state"))
           or else not Legacy (Data, F (Data, Typed, "rows"), Roster)
           or else not Seq (Data, Roster) or else not Seq (Data, Event_Roster)
           or else Len (Data, Roster) /= Len (Data, F (Data, Rows, "rows"))
           or else Len (Data, Event_Roster) /= Len (Data, F (Data, Events, "rows"))
           or else not Same (Data, F (Data, Typed, "rows"), F (Data, F (Data, Config, "genesis"), "rows"))
           or else not Seq (Data, F (Data, Typed, "events")) or else Len (Data, F (Data, Typed, "events")) /= Len (Data, Event_Roster) then return False; end if;
         for I in E.Count range 1 .. Len (Data, Roster) loop
            if not JSON (Data, Cell (Data, Rows, Row_Number (Rows, I - 1), "record"), Element (Data, Roster, I - 1)) then return False; end if;
         end loop;
         for I in E.Count range 1 .. Len (Data, Event_Roster) loop
            declare Row : constant E.Span := Row_Number (Events, I - 1);
                    Raw : constant E.Span := Cell (Data, Events, Row, "record");
                    Encoded : constant E.Span := Element (Data, Event_Roster, I - 1);
                    Event_Value : constant E.Span := Decoded_Cell (SQL, Events, Row, "record"); begin
               if not BValid (Data, Raw) or else not Hex_Bytes (B (Data, Raw), Data, Encoded)
                 or else not Same (Data, Raw, Element (Data, F (Data, Typed, "events"), I - 1))
                 or else Event_Value.Length = 0 or else not JSON (Data, Raw, Event_Value)
                 or else not BValid (Data, Cell (Data, Events, Row, "request_id"))
                 or else not Hex_Bytes (B (Data, Cell (Data, Events, Row, "request_id")), Data,
                   F (Data, F (Data, F (Data, Event_Value, "request"), "request_id"), "bytes")) then return False; end if;
            end;
         end loop;
         return True;
      end Original_Prefix_Matches;
   begin
      if not RA.Source_Valid (Data, Owner, Scoped_Transport)
        or else not RA.Source_Valid (Data, Receipt, Scoped_Transport)
        or else not Text (Data, F (Data, Receipt, "schema"), "worldline.scoped-owner-sql-source-v1")
        or else not Same (Data, Installation, F (Data, Source, "installation"))
        or else not Same (Data, Installation, F (Data, History_Owner, "installation"))
        or else not JSON (Data, F (Data, Owner, "descriptor_raw"), Installation, False)
        or else not P.Current_Source_Matches (Data, Packet, Projection)
        or else not Snapshot_Values (F (Data, Projection, "before_values"), Packet)
        or else not Seq (Data, Files) or else Len (Data, Files) /= 9
        or else not Seq (Data, DBs) or else not Seq (Data, Journals) or else Len (Data, Journals) /= 3
        or else not BValid (Data, Key) or else not BValid (Data, UKey) then return False; end if;
      for I in E.Count range 1 .. Len (Data, Files) loop
         declare File : constant E.Span := Element (Data, Files, I - 1); begin
            if not Same (Data, F (Data, File, "raw"), Owned_File (F (Data, File, "path")))
              or else not JSON (Data, F (Data, File, "raw"), F (Data, File, "value"), False)
              or else not JSON (Data, F (Data, File, "canonical"), F (Data, File, "value")) then return False; end if;
            for K in E.Count range 1 .. I - 1 loop
               if SF (Data, File, Element (Data, Files, K - 1), "path") then return False; end if;
            end loop;
         end;
      end loop;
      if not Same (Data, F (Data, File_Receipt (Authority, "/authority/gate/config.json"), "raw"), F (Data, Source, "gate_config_raw"))
        or else not Same (Data, File_Value (Authority, "/authority/gate/config.json"), F (Data, Projection, "gate_config"))
        or else not Same (Data, File_Value (Authority, "/authority/resource/os-producer-v1.json"), F (Data, Projection, "resource_config"))
        or else not Same (Data, File_Value (Authority, "/authority/resource/run-scoped-config-v1.json"), Config)
        or else not Same (Data, F (Data, Projection, "binding"), F (Data, History_Owner, "binding")) then return False; end if;
      -- _context selects the optional owner genesis only when PRIME is absent.
      -- A provisioned crosswalk may also remain in a normal PRIME config.
      if not Is_None (Data, F (Data, Source, "original_owner_genesis")) and then
        not Same (Data, F (Data, F (Data, Projection, "resource_config"), "store_genesis_context"),
          F (Data, Source, "original_owner_genesis")) then return False; end if;
      declare Genesis_File : constant E.Span := Find_Path (Data, Files, F (Data, Installation, "genesis")); begin
         if not Same (Data, F (Data, Genesis_File, "value"), Lease)
           or else not SF (Data, Lease, Installation, "installation_id")
           or else not SF (Data, Config, Installation, "installation_id")
           or else not Same (Data, F (Data, Config, "catalogue"), F (Data, Projection, "catalogue_encoded")) then return False; end if;
      end;
      if not Hash (Data, Key, F (Data, F (Data, Projection, "binding"), "issuer_key_sha256"))
        or else not Hash (Data, Key, F (Data, F (Data, Receipt, "scoped_binding"), "key_sha256"))
        or else not Hash (Data, F (Data, File_Receipt (Authority, "/authority/issuer/state/policy.json"), "raw"),
          F (Data, F (Data, Projection, "binding"), "issuer_policy_sha256"))
        or else not Hash (Data, F (Data, File_Receipt (Authority, "/authority/issuer/state/policy.json"), "raw"),
          F (Data, F (Data, Receipt, "scoped_binding"), "issuer_policy_sha256"))
        or else not Hash (Data, F (Data, File_Receipt (Authority, "/authority/gate/config.json"), "raw"),
          F (Data, F (Data, Projection, "binding"), "gate_config_sha256"))
        or else not Hash (Data, F (Data, File_Receipt (Authority, "/authority/gate/config.json"), "raw"),
          F (Data, F (Data, Receipt, "scoped_binding"), "gate_config_sha256"))
        or else not Hash (Data, F (Data, File_Receipt (Authority, "/authority/resource/run-scoped-config-v1.json"), "raw"),
          F (Data, F (Data, Receipt, "scoped_binding"), "config_sha256"))
        or else not Hash (Data, F (Data, File_Receipt (Authority, "/authority/resource/run-config-v1.json"), "raw"),
          F (Data, F (Data, Receipt, "scoped_binding"), "original_config_sha256")) then return False; end if;
      return Store_Matches and then Original_Prefix_Matches and then Authority_History (True) and then Authority_History (False)
        and then Root_History_Matches
        and then Journal_Matches ("scoped", "/authority/resource/run-scoped-state-v1/ledger.sqlite", "scoped_meta", "scoped_events", "WORLDLINE-protected-scoped-resource-journal-v1" & Character'Val (0), True, False)
        and then Journal_Matches ("launch", "/authority/resource/run-state-v1/launch.sqlite", "launch_meta", "launch_events", "WORLDLINE-protected-resource-launch-v1" & Character'Val (0), False, False)
        and then Journal_Matches ("observations", "/authority/resource/run-scoped-state-v1/observations.sqlite", "observations_meta", "observations_events", "WORLDLINE-protected-scoped-observation-journal-v1" & Character'Val (0), False, True);
   end Owner_Source_Matches;
end Worldline.Scoped_Capture_Owner_Projection;
