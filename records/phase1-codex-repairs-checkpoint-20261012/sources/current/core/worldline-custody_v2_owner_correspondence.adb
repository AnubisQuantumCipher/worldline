with Interfaces;
with Resource_Run_Ledger;
with Worldline.Custody_V2_Schema_Correspondence;
with Worldline.Custody_V2_Archive_Projection;
with Worldline.Scoped_Capture_Projection;
with Worldline.Scoped_Capture_Owner_Projection;
package body Worldline.Custody_V2_Owner_Correspondence with SPARK_Mode is
   package V renames L.V;
   package T renames V.S;
   package D renames Worldline.Custody_V2_Schema_Correspondence;
   package AP renames Worldline.Custody_V2_Archive_Projection;
   package CP renames Worldline.Scoped_Capture_Projection;
   package OP renames Worldline.Scoped_Capture_Owner_Projection;
   use type L.Original_Format;
   use type E.Count;
   use type L.Decode_Status;
   use type Interfaces.Unsigned_32;
   use type V.Q.Byte;
   use type R.Scoped_Entry;
   function Equal (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (T.Valid (Data, Left) and then T.Valid (Data, Right) and then
      T.A.Same_Encoding (Data, Left, Right));
   function Same_Field (Data : E.Bytes; Left, Right : E.Span; Name : String) return Boolean is
     (Equal (Data, T.Field (Data, Left, Name), T.Field (Data, Right, Name)));
   function Current_Capture_Matches
     (Source_Data, Capture_Data : E.Bytes; Roster, Capture : E.Span)
      return Boolean
   is
      Startup : constant E.Span := T.Field (Source_Data, Roster, "startup_native");
      Current : constant E.Span := T.Field (Source_Data, Roster, "current");
      Packet : constant E.Span := T.A.Field (Capture_Data, Capture, "packet");
      Observation : constant E.Span := T.A.Field (Capture_Data, Capture, "observation");
      Provenance : constant E.Span := T.A.Field (Capture_Data, Capture, "provenance");
      Projection : constant E.Span := T.A.Field (Capture_Data, Capture, "projection");
      Owner : constant E.Span := T.A.Field (Capture_Data, Capture, "owner");
   begin
      if not T.Valid (Source_Data, Roster) or else
         not T.A.Valid (Capture_Data, Capture) then return False; end if;
      return AP.Scoped_Archive_Operation_Matches
          (Source_Data, Capture_Data, T.Field (Source_Data, Startup, "material"), Packet) and then
        AP.Scoped_Archive_Operation_Matches
          (Source_Data, Capture_Data, T.Field (Source_Data, Startup, "observation"), Observation) and then
        AP.Scoped_Archive_Operation_Matches (Source_Data, Capture_Data, Current, Owner) and then
        CP.Scoped_Capture_Matches (Capture_Data, Observation, Provenance) and then
        OP.Owner_Source_Matches (Capture_Data, Packet, Projection, Owner);
   end Current_Capture_Matches;
   function Current_Capture_Matches (Value : L.Parsed_Input) return Boolean is
     (Value.Status = L.Parsed and then
      Value.Startup_Capture_Encoding = L.Operation_Original and then
      Current_Capture_Matches
        (Value.Arena, Value.Arena, Value.Owner_Roster, Value.Startup_Capture_Payload));
   function Owner_Rows_Correspond (Value : L.Parsed_Input) return Boolean is
      Data : E.Bytes renames Value.Arena;
      Roster : constant E.Span := Value.Owner_Roster;
      Before : constant E.Span := T.Field (Data, Roster, "before");
      Current : constant E.Span := T.Field (Data, Roster, "current");
      Old_Paths : constant E.Span := T.Field (Data, Before, "paths");
      Paths : constant E.Span := T.Field (Data, Current, "paths");
      Installation : constant E.Span := T.Field (Data, Current, "installation");
      Provisioned : constant E.Span := T.Field (Data, Installation, "provisioned_state");
      Locks : constant E.Span := T.Field (Data, Current, "held_locks");
      Journal_Path : constant E.Span := T.Field (Data, Roster, "custody_database_path");
      Genesis_Path : constant E.Span := T.Field (Data, Roster, "custody_genesis_path");
      Custody_Lock : constant E.Span := T.Field (Data, Roster, "custody_lock");
      Selected_Paths : constant E.Span := T.Field (Data, Installation, "paths");
      Authority : constant E.Span := T.Field (Data, Selected_Paths, "authority_root");
      State_Path : constant E.Span := T.Field (Data, Selected_Paths, "state");
      Transactions : constant E.Span := T.Field (Data, Installation, "actuator_transactions");
      function Joined_Path (Word, Base : E.Span; Suffix : String) return Boolean is
      begin
         if not V.Valid_Text (Data, Word) or else not V.Valid_Text (Data, Base) then return False; end if;
         declare W : constant E.Bytes := V.Text_Value (Data, Word);
                 B : constant E.Bytes := V.Text_Value (Data, Base); begin
            return W'Length >= B'Length and then W'Length - B'Length = Suffix'Length and then
              (for all I in B'Range => W (W'First + I - B'First) = B (I)) and then
              (for all I in Suffix'Range => W (W'First + B'Length + E.Count (I - Suffix'First)) =
                 Character'Pos (Suffix (I)));
         end;
      end Joined_Path;
      function Required_Lock (Base : E.Span; Suffix : String) return Boolean is
         Found : E.Count := 0;
      begin
         for I in E.Count range 1 .. V.Count (Data, Locks) loop
            if Joined_Path (T.Field (Data, V.Element (Data, Locks, I - 1), "path"), Base, Suffix) then
               Found := Found + 1;
            end if;
         end loop;
         return Found = 1;
      end Required_Lock;
      function Complete_Locks return Boolean is
      begin
         if not V.Is_Sequence (Data, Transactions) or else
            V.Count (Data, Locks) < 6 or else V.Count (Data, Locks) - 6 /= V.Count (Data, Transactions) or else
            not Required_Lock (State_Path, "/worldline-store.lock") or else
            not Required_Lock (Authority, "/authority/gate/state/gate.lock") or else
            not Required_Lock (Authority, "/authority/state/broker.lock") or else
            not Required_Lock (Authority, "/authority/issuer/state/issuer.lock") or else
            not Required_Lock (Authority, "/authority/universe/root/universe.lock") or else
            not Joined_Path (T.Field (Data, Custody_Lock, "path"), Journal_Path, ".lock") then return False; end if;
         for I in E.Count range 1 .. V.Count (Data, Transactions) loop
            declare Word : constant E.Span := V.Element (Data, Transactions, I - 1); begin
               if not V.Valid_Text (Data, Word) then return False; end if;
               declare Raw : constant E.Bytes := V.Text_Value (Data, Word);
                       Name : String (1 .. Raw'Length); begin
                  if Raw'Length = 0 then return False; end if;
                  for J in Name'Range loop
                     if Raw (Raw'First + E.Count (J - Name'First)) = Character'Pos ('/') then return False; end if;
                     Name (J) := Character'Val (Raw (Raw'First + E.Count (J - Name'First)));
                  end loop;
                  if Name in "." | ".." or else
                     not Required_Lock (Authority, "/canonical/actuator/" & Name & "/service.lock") then return False; end if;
               end;
               for J in E.Count range 1 .. I - 1 loop
                  if Equal (Data, Word, V.Element (Data, Transactions, J - 1)) then return False; end if;
               end loop;
            end;
         end loop;
         return True;
      end Complete_Locks;
      function Path_Matches (Path_Entry, Word : E.Span) return Boolean is
        (Equal (Data, T.Field (Data, Path_Entry, "path"), Word));
      function Path_Count (Word : E.Span) return E.Count is
         Found : E.Count := 0;
      begin
         for I in E.Count range 1 .. V.Count (Data, Paths) loop
            if Path_Matches (V.Element (Data, Paths, I - 1), Word) then Found := Found + 1; end if;
         end loop;
         return Found;
      end Path_Count;
      function Native_Bytes_Match (Encoded, Owned : E.Span) return Boolean is
      begin
         if not V.Valid_Bytes (Data, Encoded) or else not E.C.P.Valid (Data, Owned) then return False; end if;
         declare Raw : constant E.Bytes := V.Bytes_Value (Data, Encoded); begin
            return Raw'Length = Owned.Length and then
              (for all I in E.Count range 1 .. Owned.Length =>
                 Raw (Raw'First + I - 1) = Data (Owned.First + I - 1));
         end;
      end Native_Bytes_Match;
      function Native_Text_Match (Encoded, Owned : E.Span) return Boolean is
        (T.Text_Matches (Data, Encoded, Owned));
      function SQL_Rows_Match
        (Rows : E.Span; Encoded : L.Span_Array; Count : E.Count;
         Is_Event : Boolean := False)
         return Boolean is
      begin
         if Count > Encoded'Length or else not V.Is_Sequence (Data, Rows) or else
            V.Count (Data, Rows) /= Count then return False; end if;
         for I in E.Count range 1 .. Count loop
            declare
               Actual : constant E.Span := V.Element (Data, Rows, I - Encoded'First);
               Expected : constant E.Span := Encoded (I);
            begin
               if not V.Is_Sequence (Data, Actual) or else
                  V.Count (Data, Actual) /= V.Count (Data, Expected) + 1 then return False; end if;
               if Is_Event and then not Equal (Data, V.Element (Data, Actual, 0),
                                              V.Element (Data, Expected, 0)) then return False; end if;
               for J in E.Count range 1 .. V.Count (Data, Expected) loop
                  if not Equal (Data, V.Element (Data, Actual, J),
                                V.Element (Data, Expected, J - 1)) then return False; end if;
               end loop;
               for J in Encoded'First .. I - 1 loop
                  if Equal (Data, V.Element (Data, Actual, 0),
                     V.Element (Data, V.Element (Data, Rows, J - Encoded'First), 0)) then return False; end if;
               end loop;
            end;
         end loop;
         return True;
      end SQL_Rows_Match;
      function Journal_Matches (Database : E.Span) return Boolean is
         Tables : constant E.Span := T.Field (Data, Database, "tables");
      begin
         if not D.Database_Matches (Data, Database) then return False; end if;
         for I in E.Count range 1 .. V.Count (Data, Tables) loop
            declare
               Table : constant E.Span := V.Element (Data, Tables, I - 1);
               Name : constant E.Span := T.Field (Data, Table, "name");
               Rows : constant E.Span := T.Field (Data, Table, "rows");
            begin
               if T.Text_Is (Data, Name, "events") then
                  if not SQL_Rows_Match (Rows, Value.Event_Encoded, Value.Decoded_Event_Count, True) then return False; end if;
               elsif T.Text_Is (Data, Name, "head") then
                  if not SQL_Rows_Match (Rows, Value.Head_Encoded, Value.Head_Encoded'Length) then return False; end if;
               elsif T.Text_Is (Data, Name, "root_state") then
                  if not SQL_Rows_Match (Rows, Value.Root_Encoded, Value.Root_Encoded'Length) then return False; end if;
               elsif T.Text_Is (Data, Name, "subject_state") then
                  if not SQL_Rows_Match (Rows, Value.Subject_Encoded, Value.Subject_Encoded'Length) then return False; end if;
               elsif T.Text_Is (Data, Name, "alternatives") then
                  if not SQL_Rows_Match (Rows, Value.Alternative_Encoded, Value.Alternative_Encoded'Length) then return False; end if;
               elsif T.Text_Is (Data, Name, "blobs") then
                  if not SQL_Rows_Match (Rows, Value.Blob_Encoded, Value.Blob_Encoded'Length) then return False; end if;
               elsif T.Text_Is (Data, Name, "genesis") then
                  if V.Count (Data, Rows) /= 1 then return False; end if;
                  declare Row : constant E.Span := V.Element (Data, Rows, 0); begin
                     if not T.Text_Is (Data, V.Element (Data, Row, 1), "owner-genesis") or else
                        not Native_Bytes_Match (V.Element (Data, Row, 2), Value.Genesis_Row) or else
                        not Native_Text_Match (V.Element (Data, Row, 3), Value.Genesis_Mac) then return False; end if;
                  end;
               else return False;
               end if;
            end;
         end loop;
         return True;
      end Journal_Matches;
      function Identity_Matches (Left, Right : E.Span) return Boolean is
        (Same_Field (Data, Left, Right, "device") and then
         Same_Field (Data, Left, Right, "inode") and then
         Same_Field (Data, Left, Right, "uid") and then
         Same_Field (Data, Left, Right, "gid"));
      Journal_Found, Genesis_Found, Lock_Found : Boolean := False;
   begin
      if Value.Status /= L.Parsed or else not L.Parsed_Spans_Valid (Value) or else
         not T.Text_Is (Data, T.Field (Data, Roster, "schema"), "worldline.protected-current-owner-roster-v2") or else
         not Same_Field (Data, Before, Current, "installation") or else
         not Same_Field (Data, Before, Current, "descriptor_raw") or else
         not Same_Field (Data, Before, Current, "source") or else
         not Same_Field (Data, Before, Current, "held_locks") or else
         not V.Is_Sequence (Data, Old_Paths) or else not V.Is_Sequence (Data, Paths) or else
         V.Count (Data, Old_Paths) /= V.Count (Data, Paths) or else
         not V.Is_Sequence (Data, Provisioned) or else V.Count (Data, Provisioned) /= V.Count (Data, Paths) or else
         not V.Is_Sequence (Data, Locks) or else not Complete_Locks then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Provisioned) loop
         if Path_Count (V.Element (Data, Provisioned, I - 1)) /= 1 then return False; end if;
         for J in E.Count range 1 .. I - 1 loop
            if Equal (Data, V.Element (Data, Provisioned, I - 1), V.Element (Data, Provisioned, J - 1)) then
               return False;
            end if;
         end loop;
      end loop;
      for I in E.Count range 1 .. V.Count (Data, Paths) loop
         declare
            Old : constant E.Span := V.Element (Data, Old_Paths, I - 1);
            Now : constant E.Span := V.Element (Data, Paths, I - 1);
            Old_DB : constant E.Span := T.Field (Data, Old, "logical_database");
            Now_DB : constant E.Span := T.Field (Data, Now, "logical_database");
         begin
            if not Same_Field (Data, Old, Now, "path") or else
               not Same_Field (Data, Old, Now, "identity") then return False; end if;
            if Old_DB.Length > 0 or else Now_DB.Length > 0 then
               if not Equal (Data, Old_DB, Now_DB) then return False; end if;
            elsif not Same_Field (Data, Old, Now, "raw") then return False;
            end if;
            if Path_Matches (Now, Journal_Path) then
               if Journal_Found or else not Journal_Matches (Now_DB) then return False; end if;
               Journal_Found := True;
            end if;
            if Path_Matches (Now, Genesis_Path) then
               if Genesis_Found or else not Native_Bytes_Match (T.Field (Data, Now, "raw"), Value.Genesis_File) then
                  return False;
               end if;
               Genesis_Found := True;
            end if;
            for J in E.Count range 1 .. V.Count (Data, Locks) loop
               declare Held : constant E.Span := V.Element (Data, Locks, J - 1); begin
                  if Same_Field (Data, Held, Now, "path") and then not Identity_Matches
                    (T.Field (Data, Held, "identity"), T.Field (Data, Now, "identity")) then return False; end if;
               end;
            end loop;
         end;
      end loop;
      for I in E.Count range 1 .. V.Count (Data, Locks) loop
         declare Held : constant E.Span := V.Element (Data, Locks, I - 1); begin
            if Path_Count (T.Field (Data, Held, "path")) /= 1 then return False; end if;
            if Same_Field (Data, Held, Custody_Lock, "path") then
               if Lock_Found or else not Same_Field (Data, Held, Custody_Lock, "identity") then return False; end if;
               Lock_Found := True;
            end if;
            for J in E.Count range 1 .. I - 1 loop
               if Same_Field (Data, Held, V.Element (Data, Locks, J - 1), "path") then return False; end if;
            end loop;
         end;
      end loop;
      return Journal_Found and then Genesis_Found and then Lock_Found;
   end Owner_Rows_Correspond;
   function Owner_Corresponds (Value : L.Parsed_Input) return Boolean is
     (Owner_Rows_Correspond (Value) and then Current_Capture_Matches (Value));
   procedure Reestablish_Startup
     (Value : L.Parsed_Input; Result : out R.Scoped_Replay_Result; Contains_Unknown : out Boolean) is
      Data : E.Bytes renames Value.Arena;
      Startup : constant E.Span := T.Field (Data, Value.Owner_Roster, "startup_native");
      Material : constant E.Span := T.Field (Data, Startup, "material");
      Observation : constant E.Span := T.Field (Data, Startup, "observation");
      Current : constant E.Span := T.Field (Data, Value.Owner_Roster, "current");
      Classifications : constant E.Span := T.Field (Data, Startup, "classification");
      Classification_Material : constant E.Span := T.Field (Data, Startup, "classification_material");
      Physical : constant E.Span := T.Field (Data, Startup, "physical");
      Rows : constant E.Span := V.Record_Field (Data, Material, "rows");
      Observed : constant E.Span := V.Record_Field (Data, Material, "observed");
      Facts : constant E.Span := V.Record_Field (Data, Material, "facts");
      Classifications_Complete, Has_Unknown : Boolean;
      function Record_Same (Left, Right : E.Span; Name : String) return Boolean is
        (Equal (Data, V.Record_Field (Data, Left, Name), V.Record_Field (Data, Right, Name)));
      function Packets_Match (Classify_Material : E.Span) return Boolean is
        (Record_Same (Material, Classify_Material, "before") and then
         Record_Same (Material, Classify_Material, "history") and then
         Record_Same (Material, Classify_Material, "rows") and then
         Record_Same (Material, Classify_Material, "projection") and then
         Record_Same (Material, Classify_Material, "buckets") and then
         Record_Same (Material, Classify_Material, "proposed") and then
         Record_Same (Material, Classify_Material, "proposed_history") and then
         Record_Same (Material, Classify_Material, "proposed_rows") and then
         Record_Same (Material, Classify_Material, "proposed_projection") and then
         Record_Same (Material, Classify_Material, "proposed_buckets") and then
         Record_Same (Material, Classify_Material, "actual_buckets") and then
         Record_Same (Material, Classify_Material, "facts") and then
         Record_Same (Material, Classify_Material, "current"));
      function Reservation_Matches (Source, Reservation : E.Span) return Boolean is
         Word : constant E.Span := T.Field (Data, Source, "reservation");
         function Hex (B : V.Q.Byte) return V.Q.Byte is
           (if B < 10 then B + 48 else B - 10 + 97);
      begin
         if not V.Valid_Text (Data, Word) or else not V.Valid_Bytes (Data, Reservation) then return False; end if;
         declare Text : constant E.Bytes := V.Text_Value (Data, Word);
                 Bytes : constant E.Bytes := V.Bytes_Value (Data, Reservation); begin
            return Text'Length mod 2 = 0 and then Text'Length / 2 = Bytes'Length and then
              (for all I in Bytes'Range =>
                 Text (Text'First + (I - Bytes'First) * 2) = Hex (Bytes (I) / 16) and then
                 Text (Text'First + (I - Bytes'First) * 2 + 1) = Hex (Bytes (I) mod 16));
         end;
      end Reservation_Matches;
      procedure Reestablish_Classifications (Complete : out Boolean; Unknown : out Boolean) is
      begin
         Complete := False; Unknown := False;
         if not V.Is_Sequence (Data, Classifications) or else
            not V.Is_Sequence (Data, Classification_Material) or else
            not V.Is_Sequence (Data, Physical) or else not V.Is_Sequence (Data, Rows) or else
            not V.Is_Sequence (Data, Observed) or else not V.Is_Sequence (Data, Facts) or else
            V.Count (Data, Classifications) /= V.Count (Data, Rows) or else
            V.Count (Data, Classification_Material) /= V.Count (Data, Rows) or else
            V.Count (Data, Physical) /= V.Count (Data, Rows) or else
            V.Count (Data, Observed) /= V.Count (Data, Rows) or else
            V.Count (Data, Facts) /= V.Count (Data, Rows) then return; end if;
         for I in E.Count range 1 .. V.Count (Data, Rows) loop
            declare
               Native : constant E.Span := V.Element (Data, Classifications, I - 1);
               Initial : constant E.Span := V.Element (Data, Classification_Material, I - 1);
               Row : constant E.Span := V.Element (Data, Rows, I - 1);
               Final_Observed : constant E.Span := V.Element (Data, Observed, I - 1);
               Fact : constant E.Span := V.Element (Data, Facts, I - 1);
               Bound : constant E.Span := V.Record_Field (Data, Row, "bound");
               Reservation : constant E.Span := V.Record_Field (Data, Bound, "reservation");
               Initial_Observed : constant E.Span := V.Element (Data,
                 V.Record_Field (Data, Initial, "observed"), I - 1);
            begin
               if not Packets_Match (Initial) or else not R.Scoped_Material_Matches (Data, Native, Initial) or else
                  not Record_Same (Row, Final_Observed, "bound") or else
                  not Record_Same (Row, Final_Observed, "scope") or else
                  not Record_Same (Initial_Observed, Final_Observed, "resource_epoch") or else
                  not Equal (Data, V.Record_Field (Data, Final_Observed, "resource_epoch"),
                    V.Record_Field (Data, V.Record_Field (Data, Material, "before"), "resource_epoch")) or else
                  not Equal (Data, V.Record_Field (Data, Fact, "retained"), Bound) or else
                  not Record_Same (Fact, Final_Observed, "observation_head") or else
                  not Reservation_Matches (V.Element (Data, Physical, I - 1), Reservation) or else
                  not V.Valid_Bytes (Data, Reservation) then return; end if;
               declare
                  Got : constant R.Scoped_Replay_Result := R.Reestablish_Scoped_Observation (Data, Native);
               begin
                  if Got.State /= R.Native_Redecided or else Got.Roster_Entry /= R.Classify_Entry or else
                     Got.Native_Status > Resource_Run_Ledger.Liveness'Pos (Resource_Run_Ledger.Liveness'Last) or else
                     not T.Text_Is (Data, V.Record_Field (Data, Final_Observed, "observed"),
                       Resource_Run_Ledger.Liveness'Image (Resource_Run_Ledger.Liveness'Val (Got.Native_Status))) or else
                     not R.Scoped_Identity_Matches (Data, Native, V.Bytes_Value (Data, Reservation), True) then return; end if;
                  if Got.Native_Status = Resource_Run_Ledger.Liveness'Pos (Resource_Run_Ledger.Unknown) then
                     Unknown := True;
                  end if;
                  if Got.Native_Status in Resource_Run_Ledger.Liveness'Pos (Resource_Run_Ledger.Live) |
                                          Resource_Run_Ledger.Liveness'Pos (Resource_Run_Ledger.Reaped) then
                     if not Record_Same (Fact, Final_Observed, "actual_unit") or else
                        not Record_Same (Fact, Final_Observed, "cgroup") or else
                        not Record_Same (Fact, Final_Observed, "invocation") then return; end if;
                  elsif not Record_Same (Row, Final_Observed, "actual_unit") or else
                        not Record_Same (Row, Final_Observed, "cgroup") or else
                        not Record_Same (Row, Final_Observed, "invocation") then return;
                  end if;
                  if not T.Text_Is (Data, V.Record_Field (Data, Initial_Observed, "observed"), "UNKNOWN") then
                     return;
                  end if;
               end;
            end;
         end loop;
         Complete := True;
      end Reestablish_Classifications;
   begin
      Result := (others => <>); Contains_Unknown := False;
      if not T.Valid (Data, Startup) or else
         not Same_Field (Data, Startup, Current, "source") or else
         not R.Scoped_Material_Matches (Data, Observation, Material) then return; end if;
      Reestablish_Classifications (Classifications_Complete, Has_Unknown);
      if not Classifications_Complete then return; end if;
      declare Replayed : constant R.Scoped_Replay_Result := R.Reestablish_Scoped_Observation (Data, Observation); begin
         if Replayed.State /= R.Native_Redecided or else Replayed.Roster_Entry not in R.Check_Entry | R.Validate_Entry then
            return;
         end if;
         Result := Replayed; Contains_Unknown := Has_Unknown;
      end;
   end Reestablish_Startup;
   procedure Context_Decide
     (Value : L.Parsed_Input; Owner_Matches : out Boolean; Native : out R.Scoped_Replay_Result;
      Contains_Unknown : out Boolean) is
   begin
      Owner_Matches := Owner_Corresponds (Value);
      Native := (others => <>); Contains_Unknown := False;
      if Owner_Matches then Reestablish_Startup (Value, Native, Contains_Unknown); end if;
   end Context_Decide;
   procedure Context_Decide
     (Value : L.Parsed_Input; Owner_Matches : out Boolean; Native : out R.Scoped_Replay_Result) is
      Unknown : Boolean;
   begin
      Context_Decide (Value, Owner_Matches, Native, Unknown);
   end Context_Decide;
   function Startup_Native (Value : L.Parsed_Input) return R.Scoped_Replay_Result is
      Owner_Matches : Boolean;
      Native : R.Scoped_Replay_Result;
   begin
      Context_Decide (Value, Owner_Matches, Native);
      return Native;
   end Startup_Native;
   function Startup_Contains_Unknown (Value : L.Parsed_Input) return Boolean is
      Owner_Matches, Unknown : Boolean;
      Native : R.Scoped_Replay_Result;
   begin
      Context_Decide (Value, Owner_Matches, Native, Unknown);
      return Unknown;
   end Startup_Contains_Unknown;
end Worldline.Custody_V2_Owner_Correspondence;
