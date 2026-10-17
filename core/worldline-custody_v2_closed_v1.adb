with Attest;
with SPARK.Big_Integers;
with Canonical_Artifacts;
with Worldline.Custody_V2_Root_Values;
with Worldline.Custody_V2_Archive_Projection;
with Worldline.Custody_V2_Delta_Encoding;
with Worldline.Custody_V2_Values;
package body Worldline.Custody_V2_Closed_V1 with SPARK_Mode is
   package O renames Worldline.Custody_V2_Root_Values;
   package AP renames Worldline.Custody_V2_Archive_Projection;
   package D renames Worldline.Custody_V2_Delta_Encoding;
   package V renames Worldline.Custody_V2_Values;
   package S renames R.S;
   package Q renames E.Q;
   package C renames Canonical_Artifacts;
   use SPARK.Big_Integers;
   use type E.Count;
   use type E.Value_Kind;
   use type Q.Byte;
   use type R.Status;
   use type C.Genesis_Correspondence;
   use type Attest.Byte;
   use type D.Length_Result;
   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span
     renames O.Record_Field;
   function Payload (Data : E.Bytes; Item : E.Span) return E.Byte_View is
     (E.Decode (Data, Item, E.Operation).Payload);
   function Length (Data : E.Bytes; Item : E.Span) return E.Count is
     (AP.Byte_Length (Data, Payload (Data, Item)));
   function Equal (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (O.Valid (Data, Left) and then O.Valid (Data, Right) and then
      E.Decode (Data, Left, E.Operation).Form = E.Decode (Data, Right, E.Operation).Form and then
      AP.Bytes_Equal (Data, Data, Payload (Data, Left), Payload (Data, Right)));
   function Number (Data : E.Bytes; Item : E.Span) return Valid_Big_Integer is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
      Value : Big_Integer := To_Big_Integer (0);
      N : constant E.Count := AP.Byte_Length (Data, View.Payload);
   begin
      if View.Form /= E.Integer_Value or else not AP.Borrow_Valid (Data, View.Payload)
      then return To_Big_Integer (0); end if;
      for I in reverse E.Count range 1 .. N loop
         Value := Value * 256 + To_Big_Integer (Integer (AP.Byte_At (Data, View.Payload, I - 1)));
      end loop;
      return (if View.Sign then -Value else Value);
   end Number;
   function Hash (Data : E.Bytes; Item : E.Byte_View) return R.SHA.Digest is
      Context : R.SHA.Context := R.SHA.Initial;
   begin
      for I in E.Count range 1 .. AP.Byte_Length (Data, Item) loop
         R.SHA.Update (Context, Attest.Byte_Array'(0 => Attest.Byte (AP.Byte_At (Data, Item, I - 1))));
      end loop;
      return R.SHA.Final (Context);
   end Hash;
   function Digest_Matches
     (Data : E.Bytes; Item : E.Span; Digest : R.SHA.Digest) return Boolean
   is
      View : constant E.View := E.Decode (Data, S.A.Field (Data, Item, "value"), E.Operation);
      Hex : constant String := "0123456789abcdef";
   begin
      if not V.Valid_Text (Data, Item) or else View.Form /= E.Text_Value or else
         not AP.Borrow_Valid (Data, View.Payload) or else
         AP.Byte_Length (Data, View.Payload) /= 64 then return False; end if;
      for I in Digest'Range loop
         if AP.Byte_At (Data, View.Payload, E.Count (I) * 2) /=
              Character'Pos (Hex (Natural (Digest (I) / 16) + 1)) or else
            AP.Byte_At (Data, View.Payload, E.Count (I) * 2 + 1) /=
              Character'Pos (Hex (Natural (Digest (I) mod 16) + 1))
         then return False; end if;
      end loop;
      return True;
   end Digest_Matches;
   function JSON_String_Is (Data : E.Bytes; Item : E.Span; Word : String) return Boolean is
     (E.C.P.Valid (Data, Item) and then Item.Length = Word'Length + 2 and then
      Data (Item.First) = Character'Pos ('"') and then
      Item.First <= E.Count'Last - Item.Length and then
      Data (Item.First + Item.Length - 1) = Character'Pos ('"') and then
      (for all I in Word'Range => Data (Item.First + 1 + E.Count (I - Word'First)) = Character'Pos (Word (I))));
   -- Fixed encoder member names, not a field/count or archive-domain bound.
   Names_Text : constant String := "previousoperationkindrecordheadgenesis";
   function Names_Bytes return E.Bytes is
      Answer : E.Bytes (1 .. Names_Text'Length) := (others => 0);
   begin
      for I in Names_Text'Range loop Answer (E.Count (I)) := Character'Pos (Names_Text (I)); end loop;
      return Answer;
   end Names_Bytes;
   Names : constant E.Bytes := Names_Bytes;
   Previous_Name : constant E.Span := (1, 8);
   Operation_Name : constant E.Span := (9, 9);
   Kind_Name : constant E.Span := (18, 4);
   Record_Name : constant E.Span := (22, 6);
   Head_Name : constant E.Span := (28, 4);
   Genesis_Name : constant E.Span := (32, 7);
   function Base_Fields (Row : R.Event_Row) return D.Members is
     (1 => (Previous_Name, (D.Text_Node, Row.Previous)),
      2 => (Operation_Name, (D.Text_Node, Row.Operation)),
      3 => (Kind_Name, (D.Text_Node, Row.Kind)),
      4 => (Record_Name, (D.Copy_Archive, Row.Record_Archive)));
   function Head_Fields (Head, Genesis : E.Span) return D.Members is
     (1 => (Head_Name, (D.Text_Node, Head)),
      2 => (Genesis_Name, (D.Copy_Archive, Genesis)));
   Empty_Row : constant R.Event_Row := (others => (1, 0));
   Base_Fixed : constant D.Length_Result := D.Dictionary_Length (Names, Base_Fields (Empty_Row));
   Head_Fixed : constant D.Length_Result := D.Dictionary_Length (Names, Head_Fields ((1, 0), (1, 0)));
   procedure Add (Size : in out D.Length_Result; N : E.Count) is
   begin
      if not Size.Valid or else N > E.Count'Last - Size.Needed then Size.Valid := False;
      else Size.Needed := Size.Needed + N; end if;
   end Add;
   procedure Add_Base64 (Size : in out D.Length_Result; N : E.Count) is
   begin
      if N / 3 > E.Count'Last / 4 then Size.Valid := False; return; end if;
      Add (Size, (N / 3) * 4);
      if N mod 3 /= 0 then Add (Size, 4); end if;
   end Add_Base64;
   function Row_Valid (Data : E.Bytes; Row : E.Span; Width, Blob : E.Count) return Boolean is
   begin
      if not O.Is_Sequence (Data, Row) or else O.Count (Data, Row) /= Width or else Width = 0 or else
         not O.Is_Integer (Data, O.Element (Data, Row, 0)) then return False; end if;
      for I in E.Count range 1 .. Width - 1 loop
         declare Item : constant E.Span := O.Element (Data, Row, I); begin
            if (if I = Blob then not O.Valid_Bytes (Data, Item) else not O.Valid_Text (Data, Item))
            then return False; end if;
         end;
      end loop;
      return True;
   end Row_Valid;
   function Matches
     (Data : E.Bytes; Owner_Key : E.Span; State, Database, Owner_Plan : E.Span) return Boolean
   is
      Tables : constant E.Span := F (Data, Database, "tables");
      Auth : constant E.Span := F (Data, Database, "authenticated_root_events");
      Auth_Head : constant E.Span := F (Data, Database, "authenticated_root_head");
      Gen_Table, Events_Table, Head_Table : E.Span := (1, 0);
      Gen_Rows, Event_Rows, Head_Rows : E.Span;
      Size : D.Length_Result := (Base_Fixed.Valid and then Head_Fixed.Valid, Names'Length);
      Gen_Row, Head_Row : E.Span;
      Previous_Id : Big_Integer := To_Big_Integer (0);
      Descriptor : constant E.Span := F (Data, State, "descriptor_raw");
   begin
      if not E.C.P.Valid (Data, Owner_Key) or else not O.Valid (Data, State) or else
         not O.Valid (Data, Database) or else not O.Is_Sequence (Data, Tables) or else
         O.Count (Data, Tables) /= 3 or else not O.Is_Sequence (Data, Auth) or else
         not O.Valid_Text (Data, Auth_Head) or else not O.Valid_Bytes (Data, Descriptor) or else
         not O.Valid_Bytes (Data, Owner_Plan)
      then return False; end if;
      for I in E.Count range 1 .. O.Count (Data, Tables) loop
         declare Table : constant E.Span := O.Element (Data, Tables, I - 1); begin
            if O.Text_Is (Data, F (Data, Table, "name"), "genesis") then
               if O.Valid (Data, Gen_Table) then return False; end if; Gen_Table := Table;
            elsif O.Text_Is (Data, F (Data, Table, "name"), "events") then
               if O.Valid (Data, Events_Table) then return False; end if; Events_Table := Table;
            elsif O.Text_Is (Data, F (Data, Table, "name"), "head") then
               if O.Valid (Data, Head_Table) then return False; end if; Head_Table := Table;
            else return False; end if;
         end;
      end loop;
      Gen_Rows := F (Data, Gen_Table, "rows"); Event_Rows := F (Data, Events_Table, "rows");
      Head_Rows := F (Data, Head_Table, "rows");
      if not O.Is_Sequence (Data, Gen_Rows) or else O.Count (Data, Gen_Rows) /= 1 or else
         not O.Is_Sequence (Data, Head_Rows) or else O.Count (Data, Head_Rows) /= 1 or else
         not O.Is_Sequence (Data, Event_Rows) or else O.Count (Data, Event_Rows) /= O.Count (Data, Auth)
      then return False; end if;
      Gen_Row := O.Element (Data, Gen_Rows, 0); Head_Row := O.Element (Data, Head_Rows, 0);
      if not Row_Valid (Data, Gen_Row, 3, 2) or else not Row_Valid (Data, Head_Row, 4, 0) or else
         not Equal (Data, O.Element (Data, Head_Row, 2), Auth_Head) then return False; end if;
      Add (Size, Owner_Key.Length);
      for I in E.Count range 1 .. 2 loop Add (Size, Length (Data, O.Element (Data, Gen_Row, I))); end loop;
      for I in E.Count range 1 .. 3 loop Add (Size, Length (Data, O.Element (Data, Head_Row, I))); end loop;
      Add (Size, Head_Fixed.Needed);
      Add_Base64 (Size, Length (Data, O.Element (Data, Head_Row, 2)));
      Add (Size, Length (Data, O.Element (Data, Gen_Row, 2)));
      for I in E.Count range 1 .. O.Count (Data, Event_Rows) loop
         declare
            Row : constant E.Span := O.Element (Data, Event_Rows, I - 1);
            DTO : constant E.Span := O.Element (Data, Auth, I - 1);
         begin
            if not Row_Valid (Data, Row, 7, 5) or else not O.Type_Is (Data, DTO, "dict") or else
               E.Array_Length (Data, E.Decode (Data, DTO, E.Operation).Children) /= 6
            then return False; end if;
            declare Id : constant Valid_Big_Integer := Number (Data, O.Element (Data, Row, 0)); begin
               if I > 1 and then Id <= Previous_Id then return False; end if; Previous_Id := Id;
            end;
            if not Equal (Data, O.Element (Data, Row, 1), F (Data, DTO, "event_id")) or else
               not Equal (Data, O.Element (Data, Row, 2), F (Data, DTO, "previous")) or else
               not Equal (Data, O.Element (Data, Row, 3), F (Data, DTO, "operation")) or else
               not Equal (Data, O.Element (Data, Row, 4), F (Data, DTO, "kind")) or else
               not Equal (Data, O.Element (Data, Row, 6), F (Data, DTO, "mac"))
            then return False; end if;
            for J in E.Count range 1 .. 6 loop Add (Size, Length (Data, O.Element (Data, Row, J))); end loop;
            Add (Size, Base_Fixed.Needed);
            for J in E.Count range 2 .. 4 loop Add_Base64 (Size, Length (Data, O.Element (Data, Row, J))); end loop;
            Add (Size, Length (Data, O.Element (Data, Row, 5)));
         end;
      end loop;
      if not Size.Valid then return False; end if;
      -- Refusals with exactly the original's raising conditions: an arena of
      -- E.Count'Last bytes cannot be allocated (Storage_Error), and an arena
      -- shorter than the fixed names failed the first slice copy below.
      if Size.Needed = E.Count'Last or else Size.Needed < Names'Length then return False; end if;
      declare
         Arena_Size : constant E.Count := Size.Needed;
         Event_Count : constant E.Count := O.Count (Data, Event_Rows);
         Arena : E.Bytes (1 .. Arena_Size) := (others => 0);
         Used : E.Count;
         Key, Head_Message : E.Span;
         Genesis : R.Genesis_Rows (1 .. 1) := (others => (others => (1, 0)));
         Rows : R.Event_Rows (1 .. Event_Count) := (others => (others => (1, 0)));
         Heads : R.Head_Rows (1 .. 1) := (others => (others => (1, 0)));
         Valid : Boolean := True;
         procedure Put_View (Item : E.Byte_View; Into : out E.Span) is
            N : constant E.Count := AP.Byte_Length (Data, Item);
         begin
            Into := (1, 0);
            if not Valid or else not AP.Borrow_Valid (Data, Item) or else
               Used > Arena'Length or else N > Arena'Length - Used then Valid := False; return; end if;
            Into := (Arena'First + Used, N);
            for I in E.Count range 1 .. N loop Arena (Arena'First + Used + I - 1) := AP.Byte_At (Data, Item, I - 1); end loop;
            Used := Used + N;
         end Put_View;
         procedure Put_Cell (Item : E.Span; Into : out E.Span) is
         begin Put_View (Payload (Data, Item), Into); end Put_Cell;
         procedure Dictionary (Fields : D.Members; Into : out E.Span) is
            Needed : constant D.Length_Result := D.Dictionary_Length (Arena, Fields);
            Written : D.Length_Result;
            Complete : Boolean;
         begin
            Into := (1, 0);
            if not Valid or else not Needed.Valid or else Used > Arena'Length or else
               Needed.Needed > Arena'Length - Used then Valid := False; return; end if;
            Into := (Arena'First + Used, Needed.Needed);
            -- Encoder reads only the occupied immutable prefix; its output is
            -- the disjoint exact next slice, not a second copied source arena.
            -- SPARK cannot separate two dynamic slices of one array passed as
            -- in and out, so the output is encoded into an exact-size buffer
            -- and placed into that slice: the copy is O(output), never a copy
            -- of the source prefix.
            declare
               Encoded : E.Bytes (1 .. Needed.Needed);
            begin
               D.Encode_Dictionary (Arena (Arena'First .. Arena'First + Used - 1), Fields,
                 Encoded, Written, Complete);
               if not Complete or else Written /= Needed then Valid := False; return; end if;
               Arena (Into.First .. Into.First + Into.Length - 1) := Encoded;
            end;
            Used := Used + Into.Length;
         end Dictionary;
         function Genesis_Context return Boolean is
            G : constant E.Span := Genesis (1).Value;
            Paths : constant E.Span := F (Data, State, "paths");
            Plan_JSON : constant E.Bytes := E.Materialize (Data, Payload (Data, Owner_Plan));
            Whole : constant E.Span := (Plan_JSON'First, Plan_JSON'Length);
            Schema : constant E.Span := C.Canonical_JSON_Field (Plan_JSON, Whole, "schema");
            Journal_Path : constant E.Span := C.Canonical_JSON_Field (Plan_JSON, Whole, "handoff_journal");
            Genesis_Path : constant E.Span := C.Canonical_JSON_Field (Plan_JSON, Whole, "handoff_genesis");
            Genesis_Found, Database_Found : Boolean := False;
         begin
            if not S.Valid (Arena, G) or else S.Member_Count (Arena, G) /= 6 or else
               not S.Text_Is (Arena, S.Field (Arena, G, "schema"), "worldline.owner-provisioned-root-custody-v1") or else
               not AP.Scoped_Archive_Operation_Matches (Arena, Data, S.Field (Arena, G, "installation"),
                 F (Data, F (Data, State, "installation"), "installation_id")) or else
               not Digest_Matches (Arena, S.Field (Arena, G, "startup_descriptor_sha256"), Hash (Data, Payload (Data, Descriptor))) or else
               not Digest_Matches (Arena, S.Field (Arena, G, "issuer_key_sha256"), Hash (Data, (Owner_Key, 0))) or else
               not Digest_Matches (Arena, S.Field (Arena, G, "owner_plan_sha256"), Hash (Data, Payload (Data, Owner_Plan))) or else
               not S.Valid (Arena, S.Field (Arena, G, "initial_event")) or else
               not O.Is_Sequence (Data, Paths) or else
               not JSON_String_Is (Plan_JSON, Schema, "worldline.protected-root-worker-plan-v1") or else
               not C.Operation_Archive_JSON_Matches (Plan_JSON, Data,
                 C.Canonical_JSON_Field (Plan_JSON, Whole, "installation"),
                 F (Data, F (Data, State, "installation"), "installation_id"))
            then return False; end if;
            -- Exact selected original paths, never a scan for a compatible
            -- genesis belonging to another root or a stored-genesis self-join.
            for I in E.Count range 1 .. O.Count (Data, Paths) loop
               declare
                  Entry_Value : constant E.Span := O.Element (Data, Paths, I - 1);
                  Path : constant E.Span := F (Data, Entry_Value, "path");
                  Observed : constant E.Span := F (Data, Entry_Value, "logical_database");
                  Raw : constant E.Span := F (Data, Entry_Value, "raw");
               begin
                  if Observed.First = Database.First and then Observed.Length = Database.Length then
                     if Database_Found or else not C.Operation_Archive_JSON_Matches (Plan_JSON, Data, Journal_Path, Path)
                     then return False; end if;
                     Database_Found := True;
                  end if;
                  if C.Operation_Archive_JSON_Matches (Plan_JSON, Data, Genesis_Path, Path) then
                     if Genesis_Found or else not O.Valid_Bytes (Data, Raw) then return False; end if;
                     declare File_Bytes : constant E.Bytes := E.Materialize (Data, Payload (Data, Raw)); begin
                        if C.Scoped_Archive_JSON_Matches (File_Bytes, Arena,
                          (File_Bytes'First, File_Bytes'Length), G) /= C.Typed_Tree_Matches_Source_Custody_Open
                        then return False; end if;
                     end;
                     Genesis_Found := True;
                  end if;
               end;
            end loop;
            return Genesis_Found and then Database_Found;
         end Genesis_Context;
      begin
         Arena (1 .. Names'Length) := Names; Used := Names'Length;
         Put_View ((Owner_Key, 0), Key);
         Put_Cell (O.Element (Data, Gen_Row, 1), Genesis (1).Name);
         Put_Cell (O.Element (Data, Gen_Row, 2), Genesis (1).Value);
         Put_Cell (O.Element (Data, Head_Row, 1), Heads (1).Name);
         Put_Cell (O.Element (Data, Head_Row, 2), Heads (1).Event_Id);
         Put_Cell (O.Element (Data, Head_Row, 3), Heads (1).Mac);
         for I in Rows'Range loop
            declare Row : constant E.Span := O.Element (Data, Event_Rows, I - 1); begin
               Put_Cell (O.Element (Data, Row, 1), Rows (I).Event_Id);
               Put_Cell (O.Element (Data, Row, 2), Rows (I).Previous);
               Put_Cell (O.Element (Data, Row, 3), Rows (I).Operation);
               Put_Cell (O.Element (Data, Row, 4), Rows (I).Kind);
               Put_Cell (O.Element (Data, Row, 5), Rows (I).Record_Archive);
               Put_Cell (O.Element (Data, Row, 6), Rows (I).Mac);
               Rows (I).Base_Archive := (1, 0);
               if not Valid or else not S.Valid (Arena, Rows (I).Record_Archive) or else
                  not AP.Scoped_Archive_Operation_Matches (Arena, Data, Rows (I).Record_Archive,
                    F (Data, O.Element (Data, Auth, I - 1), "record")) then return False; end if;
               Dictionary (Base_Fields (Rows (I)), Rows (I).Base_Archive);
            end;
         end loop;
         Dictionary (Head_Fields (Heads (1).Event_Id, Genesis (1).Value), Head_Message);
         return Valid and then Used = Arena'Length and then Genesis_Context and then
           R.Verify (Arena, Key, Genesis (1).Value, Head_Message, Genesis, Rows, Heads).State = R.Retained_Chain_Matches;
      end;
   end Matches;
end Worldline.Custody_V2_Closed_V1;
