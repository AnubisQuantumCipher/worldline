package body Worldline.Custody_V2_Schema_Correspondence with SPARK_Mode is
   package T renames V.S;
   use type E.Count;
   use type V.Q.Byte;
   function Name (Table : Table_Name) return String is
     (case Table is
        when Genesis => "genesis",
        when Events => "events",
        when Alternatives => "alternatives",
        when Root_State => "root_state",
        when Subject_State => "subject_state",
        when Blobs => "blobs",
        when Head => "head");
   function DDL (Table : Table_Name) return String is
     (case Table is
        when Genesis => "CREATE TABLE genesis (" & Character'Val (10) &
           "  name  TEXT PRIMARY KEY CHECK (name = 'owner-genesis')," & Character'Val (10) &
           "  value BLOB NOT NULL CHECK (typeof(value) = 'blob')," & Character'Val (10) &
           "  mac   TEXT NOT NULL CHECK (typeof(mac) = 'text' AND length(mac) = 64)" & Character'Val (10) &
           ")",
        when Events => "CREATE TABLE events (" & Character'Val (10) &
           "  seq           INTEGER PRIMARY KEY," & Character'Val (10) &
           "  event_id      TEXT NOT NULL UNIQUE CHECK (typeof(event_id) = 'text' AND length(event_id) = 64)," & Character'Val (10) &
           "  previous      TEXT NOT NULL UNIQUE CHECK (typeof(previous) = 'text' AND length(previous) = 64)," & Character'Val (10) &
           "  generation    BLOB NOT NULL CHECK (typeof(generation) = 'blob' AND length(generation) >= 1" & Character'Val (10) &
           "                  AND substr(generation, length(generation), 1) <> x'00')," & Character'Val (10) &
           "  operation     TEXT NOT NULL CHECK (typeof(operation) = 'text')," & Character'Val (10) &
           "  subject_kind  TEXT NOT NULL CHECK (subject_kind IN ('ROOT','REQUEST','DESCRIPTOR'))," & Character'Val (10) &
           "  subject       TEXT NOT NULL CHECK (typeof(subject) = 'text')," & Character'Val (10) &
           "  subgeneration BLOB NOT NULL CHECK (typeof(subgeneration) = 'blob' AND (length(subgeneration) = 0" & Character'Val (10) &
           "                  OR substr(subgeneration, length(subgeneration), 1) <> x'00'))," & Character'Val (10) &
           "  kind          TEXT NOT NULL CHECK (kind IN (" & Character'Val (10) &
           "    'PREPARED','HELD','RUNNING','EXECUTION_NATIVE','EXECUTION_ACK','HANDOFF_INTENT'," & Character'Val (10) &
           "    'FRONT_CLOSE_INTENT','FRONT_CLOSED','TRANSFER_SENT','ROSTER_EVIDENCE','CUSTODY_ACK','ABANDON'," & Character'Val (10) &
           "    'FRONT_RETAINED_ESCROW','HANDOFF_ABORT','ORIGINAL_PROGRESS','ORIGINAL_RESULT','HANDLER_TERMINAL'," & Character'Val (10) &
           "    'WORKER_RELINQUISH','WORKER_REATTACHED','CUSTODY_RETURNED','CLOSED_NS','CLOSED_OUTER','CLOSED_RAW'," & Character'Val (10) &
           "    'CLOSED_WITNESS','PHYSICAL_SETTLED','HISTORICAL_SETTLEMENT','FRONT_RECONSTRUCTION','FRONT_OWNED'," & Character'Val (10) &
           "    'UNKNOWN','RECONCILED'," & Character'Val (10) &
           "    'REQUEST_QUEUED','REQUEST_TRANSFER_INTENT','REQUEST_INTAKE','REQUEST_ABANDON','REQUEST_RESPONDED'," & Character'Val (10) &
           "    'REQUEST_LOST'," & Character'Val (10) &
           "    'DRAIN_STOP_INTENT','DRAIN_FREEZE','DRAIN_OFD_EVIDENCE','DRAIN_INTAKE','DRAIN_ABANDON'," & Character'Val (10) &
           "    'DRAIN_RELEASED','DRAIN_RECLAIMED'))," & Character'Val (10) &
           "  actor         TEXT NOT NULL CHECK (actor IN ('FRONT','WORKER','COLLECTOR','RECONCILER'))," & Character'Val (10) &
           "  record        BLOB NOT NULL CHECK (typeof(record) = 'blob')," & Character'Val (10) &
           "  base          BLOB NOT NULL CHECK (typeof(base) = 'blob')," & Character'Val (10) &
           "  mac           TEXT NOT NULL CHECK (typeof(mac) = 'text' AND length(mac) = 64)," & Character'Val (10) &
           "  CHECK ((subject_kind = 'ROOT') = (subject = ''))" & Character'Val (10) &
           ")",
        when Alternatives => "CREATE TABLE alternatives (" & Character'Val (10) &
           "  generation      BLOB NOT NULL CHECK (typeof(generation) = 'blob')," & Character'Val (10) &
           "  operation       TEXT NOT NULL," & Character'Val (10) &
           "  subject_kind    TEXT NOT NULL CHECK (subject_kind IN ('ROOT','REQUEST','DESCRIPTOR'))," & Character'Val (10) &
           "  subject         TEXT NOT NULL," & Character'Val (10) &
           "  subgeneration   BLOB NOT NULL CHECK (typeof(subgeneration) = 'blob')," & Character'Val (10) &
           "  alternative_set TEXT NOT NULL CHECK (alternative_set IN ('ACK','REQUEST','DRAIN'))," & Character'Val (10) &
           "  event_id        TEXT NOT NULL UNIQUE REFERENCES events(event_id)," & Character'Val (10) &
           "  PRIMARY KEY (generation, operation, subject_kind, subject, subgeneration, alternative_set)" & Character'Val (10) &
           ")",
        when Root_State => "CREATE TABLE root_state (" & Character'Val (10) &
           "  generation          BLOB PRIMARY KEY CHECK (typeof(generation) = 'blob' AND length(generation) >= 1" & Character'Val (10) &
           "                        AND substr(generation, length(generation), 1) <> x'00')," & Character'Val (10) &
           "  operation           TEXT NOT NULL CHECK (typeof(operation) = 'text')," & Character'Val (10) &
           "  phase               TEXT NOT NULL CHECK (phase IN (" & Character'Val (10) &
           "    'FRONT_OWNED','PREPARED','HELD','RUNNING','EXECUTION_NATIVE','EXECUTION_ACK','HANDOFF_INTENT'," & Character'Val (10) &
           "    'FRONT_CLOSE_INTENT','FRONT_CLOSED','TRANSFER_SENT','ROSTER_EVIDENCE','WORKER_OWNED'," & Character'Val (10) &
           "    'ORIGINAL_RESULT','HANDLER_TERMINAL','WORKER_RELINQUISH','ABANDONED','FRONT_RETAINED_ESCROW'," & Character'Val (10) &
           "    'HANDOFF_ABORTED','CUSTODY_RETURNED','HISTORICAL_SETTLEMENT','FRONT_RECONSTRUCTION','ENDED'," & Character'Val (10) &
           "    'UNKNOWN'))," & Character'Val (10) &
           "  before_unknown      TEXT," & Character'Val (10) &
           "  owners_open         INTEGER NOT NULL CHECK (owners_open IN (0,1))," & Character'Val (10) &
           "  abort_class         TEXT CHECK (abort_class IS NULL OR abort_class IN ('NEVER_DISPATCHED','DISPATCHED'))," & Character'Val (10) &
           "  launched            INTEGER NOT NULL CHECK (launched IN (0,1))," & Character'Val (10) &
           "  closure_ns          INTEGER NOT NULL CHECK (closure_ns IN (0,1))," & Character'Val (10) &
           "  closure_outer       INTEGER NOT NULL CHECK (closure_outer IN (0,1))," & Character'Val (10) &
           "  closure_raw         INTEGER NOT NULL CHECK (closure_raw IN (0,1))," & Character'Val (10) &
           "  witness             INTEGER NOT NULL CHECK (witness IN (0,1))," & Character'Val (10) &
           "  settled             INTEGER NOT NULL CHECK (settled IN (0,1))," & Character'Val (10) &
           "  released_unlaunched INTEGER NOT NULL CHECK (released_unlaunched IN (0,1))," & Character'Val (10) &
           "  unknown_cause       TEXT CHECK (unknown_cause IS NULL OR length(unknown_cause) = 64)," & Character'Val (10) &
           "  reattach_epoch      BLOB NOT NULL CHECK (typeof(reattach_epoch) = 'blob' AND (length(reattach_epoch) = 0" & Character'Val (10) &
           "                        OR substr(reattach_epoch, length(reattach_epoch), 1) <> x'00'))," & Character'Val (10) &
           "  head_event          TEXT NOT NULL REFERENCES events(event_id)," & Character'Val (10) &
           "  CHECK ((phase = 'UNKNOWN') = (before_unknown IS NOT NULL))," & Character'Val (10) &
           "  CHECK (before_unknown IS NULL OR before_unknown NOT IN ('UNKNOWN','ENDED'))" & Character'Val (10) &
           ")",
        when Subject_State => "CREATE TABLE subject_state (" & Character'Val (10) &
           "  generation    BLOB NOT NULL REFERENCES root_state(generation)," & Character'Val (10) &
           "  subject_kind  TEXT NOT NULL CHECK (subject_kind IN ('REQUEST','DESCRIPTOR'))," & Character'Val (10) &
           "  subject       TEXT NOT NULL," & Character'Val (10) &
           "  subgeneration BLOB NOT NULL CHECK (typeof(subgeneration) = 'blob' AND (length(subgeneration) = 0" & Character'Val (10) &
           "                  OR substr(subgeneration, length(subgeneration), 1) <> x'00'))," & Character'Val (10) &
           "  phase         TEXT NOT NULL," & Character'Val (10) &
           "  mode          TEXT NOT NULL CHECK (mode IN ('NONE','FRESH','RELAY'))," & Character'Val (10) &
           "  position      BLOB CHECK (position IS NULL OR (typeof(position) = 'blob' AND (length(position) = 0" & Character'Val (10) &
           "                  OR substr(position, length(position), 1) <> x'00')))," & Character'Val (10) &
           "  carried_from  BLOB CHECK (carried_from IS NULL OR (typeof(carried_from) = 'blob' AND length(carried_from) >= 1" & Character'Val (10) &
           "                  AND substr(carried_from, length(carried_from), 1) <> x'00'))," & Character'Val (10) &
           "  head_event    TEXT NOT NULL REFERENCES events(event_id)," & Character'Val (10) &
           "  PRIMARY KEY (generation, subject_kind, subject)," & Character'Val (10) &
           "  CHECK ((subject_kind = 'REQUEST' AND phase IN" & Character'Val (10) &
           "           ('QUEUED','TRANSFER_INTENT','INTAKE','ABANDONED','RESPONDED','LOST'))" & Character'Val (10) &
           "      OR (subject_kind = 'DESCRIPTOR' AND phase IN" & Character'Val (10) &
           "           ('FRONT_HELD','STOP_INTENT','FROZEN','OFD_EVIDENCE','INTAKE','ABANDONED','RELEASED','RECLAIMED')))" & Character'Val (10) &
           ")",
        when Blobs => "CREATE TABLE blobs (" & Character'Val (10) &
           "  sha256 TEXT PRIMARY KEY CHECK (length(sha256) = 64)," & Character'Val (10) &
           "  kind   TEXT NOT NULL CHECK (kind IN ('RAW_OBSERVATION','SPOOL_CHUNK','CAPTURE','RESPONSE'))," & Character'Val (10) &
           "  bytes  BLOB NOT NULL" & Character'Val (10) &
           ")",
        when Head => "CREATE TABLE head (" & Character'Val (10) &
           "  name      TEXT PRIMARY KEY CHECK (name = 'current')," & Character'Val (10) &
           "  head_kind TEXT NOT NULL CHECK (head_kind IN ('ORIGIN','EVENT'))," & Character'Val (10) &
           "  event_id  TEXT REFERENCES events(event_id)," & Character'Val (10) &
           "  origin    TEXT CHECK (origin IS NULL OR length(origin) = 64)," & Character'Val (10) &
           "  mac       TEXT NOT NULL CHECK (length(mac) = 64)," & Character'Val (10) &
           "  CHECK ((head_kind = 'ORIGIN' AND event_id IS NULL AND origin IS NOT NULL)" & Character'Val (10) &
           "      OR (head_kind = 'EVENT' AND event_id IS NOT NULL AND origin IS NULL))" & Character'Val (10) &
           ")");
   function Width (Table : Table_Name) return Positive is
     (case Table is
        when Genesis => 3,
        when Events => 13,
        when Alternatives => 7,
        when Root_State => 16,
        when Subject_State => 9,
        when Blobs => 3,
        when Head => 5);
   function Integer_Is (Data : E.Bytes; Item : E.Span; Number : Natural) return Boolean is
      Got : constant V.Count_Result := V.Nonnegative_Count (Data, Item);
   begin return Got.Present and then Got.Value = E.Count (Number); end Integer_Is;
   function Column_Matches (Data : E.Bytes; Item : E.Span; Table : Table_Name;
                            Ordinal : E.Count) return Boolean is
      function Column (Name, Kind : String; Not_Null, Key : Natural) return Boolean is
        (V.Is_Sequence (Data, Item) and then V.Count (Data, Item) = 7 and then
         Integer_Is (Data, V.Element (Data, Item, 0), Natural (Ordinal)) and then
         T.Text_Is (Data, V.Element (Data, Item, 1), Name) and then
         T.Text_Is (Data, V.Element (Data, Item, 2), Kind) and then
         Integer_Is (Data, V.Element (Data, Item, 3), Not_Null) and then
         V.Is_Null (Data, V.Element (Data, Item, 4)) and then
         Integer_Is (Data, V.Element (Data, Item, 5), Key) and then
         Integer_Is (Data, V.Element (Data, Item, 6), 0));
   begin
      case Table is
         when Genesis =>
            case Ordinal is
               when 0 => return Column ("name", "TEXT", 0, 1);
               when 1 => return Column ("value", "BLOB", 1, 0);
               when 2 => return Column ("mac", "TEXT", 1, 0);
               when others => return False;
            end case;
         when Events =>
            case Ordinal is
               when 0 => return Column ("seq", "INTEGER", 0, 1);
               when 1 => return Column ("event_id", "TEXT", 1, 0);
               when 2 => return Column ("previous", "TEXT", 1, 0);
               when 3 => return Column ("generation", "BLOB", 1, 0);
               when 4 => return Column ("operation", "TEXT", 1, 0);
               when 5 => return Column ("subject_kind", "TEXT", 1, 0);
               when 6 => return Column ("subject", "TEXT", 1, 0);
               when 7 => return Column ("subgeneration", "BLOB", 1, 0);
               when 8 => return Column ("kind", "TEXT", 1, 0);
               when 9 => return Column ("actor", "TEXT", 1, 0);
               when 10 => return Column ("record", "BLOB", 1, 0);
               when 11 => return Column ("base", "BLOB", 1, 0);
               when 12 => return Column ("mac", "TEXT", 1, 0);
               when others => return False;
            end case;
         when Alternatives =>
            case Ordinal is
               when 0 => return Column ("generation", "BLOB", 1, 1);
               when 1 => return Column ("operation", "TEXT", 1, 2);
               when 2 => return Column ("subject_kind", "TEXT", 1, 3);
               when 3 => return Column ("subject", "TEXT", 1, 4);
               when 4 => return Column ("subgeneration", "BLOB", 1, 5);
               when 5 => return Column ("alternative_set", "TEXT", 1, 6);
               when 6 => return Column ("event_id", "TEXT", 1, 0);
               when others => return False;
            end case;
         when Root_State =>
            case Ordinal is
               when 0 => return Column ("generation", "BLOB", 0, 1);
               when 1 => return Column ("operation", "TEXT", 1, 0);
               when 2 => return Column ("phase", "TEXT", 1, 0);
               when 3 => return Column ("before_unknown", "TEXT", 0, 0);
               when 4 => return Column ("owners_open", "INTEGER", 1, 0);
               when 5 => return Column ("abort_class", "TEXT", 0, 0);
               when 6 => return Column ("launched", "INTEGER", 1, 0);
               when 7 => return Column ("closure_ns", "INTEGER", 1, 0);
               when 8 => return Column ("closure_outer", "INTEGER", 1, 0);
               when 9 => return Column ("closure_raw", "INTEGER", 1, 0);
               when 10 => return Column ("witness", "INTEGER", 1, 0);
               when 11 => return Column ("settled", "INTEGER", 1, 0);
               when 12 => return Column ("released_unlaunched", "INTEGER", 1, 0);
               when 13 => return Column ("unknown_cause", "TEXT", 0, 0);
               when 14 => return Column ("reattach_epoch", "BLOB", 1, 0);
               when 15 => return Column ("head_event", "TEXT", 1, 0);
               when others => return False;
            end case;
         when Subject_State =>
            case Ordinal is
               when 0 => return Column ("generation", "BLOB", 1, 1);
               when 1 => return Column ("subject_kind", "TEXT", 1, 2);
               when 2 => return Column ("subject", "TEXT", 1, 3);
               when 3 => return Column ("subgeneration", "BLOB", 1, 0);
               when 4 => return Column ("phase", "TEXT", 1, 0);
               when 5 => return Column ("mode", "TEXT", 1, 0);
               when 6 => return Column ("position", "BLOB", 0, 0);
               when 7 => return Column ("carried_from", "BLOB", 0, 0);
               when 8 => return Column ("head_event", "TEXT", 1, 0);
               when others => return False;
            end case;
         when Blobs =>
            case Ordinal is
               when 0 => return Column ("sha256", "TEXT", 0, 1);
               when 1 => return Column ("kind", "TEXT", 1, 0);
               when 2 => return Column ("bytes", "BLOB", 1, 0);
               when others => return False;
            end case;
         when Head =>
            case Ordinal is
               when 0 => return Column ("name", "TEXT", 0, 1);
               when 1 => return Column ("head_kind", "TEXT", 1, 0);
               when 2 => return Column ("event_id", "TEXT", 0, 0);
               when 3 => return Column ("origin", "TEXT", 0, 0);
               when 4 => return Column ("mac", "TEXT", 1, 0);
               when others => return False;
            end case;
      end case;
   end Column_Matches;
   function Foreign_Keys_Match (Data : E.Bytes; Item : E.Span; Table : Table_Name)
      return Boolean is
      function FK (Ordinal : E.Count; Target, Source, Destination : String) return Boolean is
         Row : constant E.Span := V.Element (Data, Item, Ordinal);
      begin
         return V.Is_Sequence (Data, Row) and then V.Count (Data, Row) = 8 and then
           Integer_Is (Data, V.Element (Data, Row, 0), Natural (Ordinal)) and then
           Integer_Is (Data, V.Element (Data, Row, 1), 0) and then
           T.Text_Is (Data, V.Element (Data, Row, 2), Target) and then
           T.Text_Is (Data, V.Element (Data, Row, 3), Source) and then
           T.Text_Is (Data, V.Element (Data, Row, 4), Destination) and then
           T.Text_Is (Data, V.Element (Data, Row, 5), "NO ACTION") and then
           T.Text_Is (Data, V.Element (Data, Row, 6), "NO ACTION") and then
           T.Text_Is (Data, V.Element (Data, Row, 7), "NONE");
      end FK;
   begin
      if not V.Is_Sequence (Data, Item) then return False; end if;
      case Table is
         when Alternatives | Head => return V.Count (Data, Item) = 1 and then
            FK (0, "events", "event_id", "event_id");
         when Root_State => return V.Count (Data, Item) = 1 and then
            FK (0, "events", "head_event", "event_id");
         when Subject_State => return V.Count (Data, Item) = 2 and then
            FK (0, "events", "head_event", "event_id") and then
            FK (1, "root_state", "generation", "generation");
         when others => return V.Count (Data, Item) = 0;
      end case;
   end Foreign_Keys_Match;
   function Table_Matches (Data : E.Bytes; Item : E.Span; Table : Table_Name)
      return Boolean is
      Columns : constant E.Span := T.Field (Data, Item, "columns");
      Rows : constant E.Span := T.Field (Data, Item, "rows");
   begin
      return T.Valid (Data, Item) and then T.Member_Count (Data, Item) = 5 and then
        T.Text_Is (Data, T.Field (Data, Item, "name"), Name (Table)) and then
        T.Text_Is (Data, T.Field (Data, Item, "query"),
          "SELECT rowid,* FROM " & '"' & Name (Table) & '"' & " ORDER BY rowid") and then
        V.Is_Sequence (Data, Columns) and then V.Count (Data, Columns) = E.Count (Width (Table)) and then
        (for all I in E.Count range 1 .. E.Count (Width (Table)) =>
           Column_Matches (Data, V.Element (Data, Columns, I - 1), Table, I - 1)) and then
        V.Is_Sequence (Data, Rows) and then
        (for all I in E.Count range 1 .. V.Count (Data, Rows) =>
           V.Is_Sequence (Data, V.Element (Data, Rows, I - 1)) and then
           V.Count (Data, V.Element (Data, Rows, I - 1)) = E.Count (Width (Table)) + 1 and then
           V.Is_Integer (Data, V.Element (Data, V.Element (Data, Rows, I - 1), 0))) and then
        Foreign_Keys_Match (Data, T.Field (Data, Item, "foreign_key_list"), Table);
   end Table_Matches;
   function Database_Matches (Data : E.Bytes; Item : E.Span) return Boolean is
      Schema : constant E.Span := T.Field (Data, Item, "schema");
      Tables : constant E.Span := T.Field (Data, Item, "tables");
      FK_Check : constant E.Span := T.Field (Data, Item, "foreign_key_check");
      function Singleton (Name : String; Text : String := ""; Number : Natural := 0;
                          Is_Text : Boolean := False) return Boolean is
         Rows : constant E.Span := T.Field (Data, Item, Name);
         Row : constant E.Span := V.Element (Data, Rows, 0);
         Cell : constant E.Span := V.Element (Data, Row, 0);
      begin
         return V.Is_Sequence (Data, Rows) and then V.Count (Data, Rows) = 1 and then
           V.Is_Sequence (Data, Row) and then V.Count (Data, Row) = 1 and then
           (if Is_Text then T.Text_Is (Data, Cell, Text) else Integer_Is (Data, Cell, Number));
      end Singleton;
      function Metadata_Scalar (Name : String; Text : Boolean := False) return Boolean is
         Rows : constant E.Span := T.Field (Data, Item, Name);
         Row : constant E.Span := V.Element (Data, Rows, 0);
         Cell : constant E.Span := V.Element (Data, Row, 0);
      begin
         return V.Is_Sequence (Data, Rows) and then V.Count (Data, Rows) = 1 and then
           V.Is_Sequence (Data, Row) and then V.Count (Data, Row) = 1 and then
           (if Text then V.Valid_Text (Data, Cell) else V.Is_Integer (Data, Cell));
      end Metadata_Scalar;
      function Schema_Row (Row : E.Span; Table : Table_Name; Index : Natural := 0) return Boolean is
      begin
         return V.Is_Sequence (Data, Row) and then V.Count (Data, Row) = 5 and then
           T.Text_Is (Data, V.Element (Data, Row, 0), (if Index = 0 then "table" else "index")) and then
           T.Text_Is (Data, V.Element (Data, Row, 1), (if Index = 0 then Name (Table) else
              "sqlite_autoindex_" & Name (Table) & "_" & (if Index = 1 then "1" else "2"))) and then
           T.Text_Is (Data, V.Element (Data, Row, 2), Name (Table)) and then
           V.Is_Integer (Data, V.Element (Data, Row, 3)) and then
           (if Index = 0 then T.Text_Is (Data, V.Element (Data, Row, 4), DDL (Table)) else
              V.Is_Null (Data, V.Element (Data, Row, 4)));
      end Schema_Row;
      function Index_Count (Table : Table_Name) return Natural is
        (if Table in Events | Alternatives then 2 else 1);
      function Schema_Multiplicity (Table : Table_Name; Index : Natural) return E.Count is
         Found : E.Count := 0;
      begin
         for I in E.Count range 1 .. V.Count (Data, Schema) loop
            if Schema_Row (V.Element (Data, Schema, I - 1), Table, Index) then Found := Found + 1; end if;
         end loop;
         return Found;
      end Schema_Multiplicity;
      function Table_Multiplicity (Table : Table_Name) return E.Count is
         Found : E.Count := 0;
      begin
         for I in E.Count range 1 .. V.Count (Data, Tables) loop
            if Table_Matches (Data, V.Element (Data, Tables, I - 1), Table) then Found := Found + 1; end if;
         end loop;
         return Found;
      end Table_Multiplicity;
   begin
      if not T.Valid (Data, Item) or else T.Member_Count (Data, Item) /= 8 or else
         not V.Is_Sequence (Data, Schema) or else V.Count (Data, Schema) /= 16 or else
         not V.Is_Sequence (Data, Tables) or else V.Count (Data, Tables) /= 7 or else
         not V.Is_Sequence (Data, FK_Check) or else V.Count (Data, FK_Check) /= 0 or else
         not Singleton ("integrity", "ok", Is_Text => True) or else
         not Metadata_Scalar ("encoding", Text => True) or else
         not Singleton ("foreign_keys", Number => 1) or else
         not Metadata_Scalar ("user_version") or else not Metadata_Scalar ("application_id") then return False; end if;
      return (for all Table in Table_Name => Table_Multiplicity (Table) = 1 and then
         Schema_Multiplicity (Table, 0) = 1 and then
         (for all Index in 1 .. Index_Count (Table) => Schema_Multiplicity (Table, Index) = 1));
   end Database_Matches;
end Worldline.Custody_V2_Schema_Correspondence;
