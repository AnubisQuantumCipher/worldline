package body Worldline.Custody_V2_Load_Input with SPARK_Mode is
   package T renames V.S;
   package M renames A.M;
   use type Q.Byte;
   use type S.SQL_Class;
   use type E.Value_Kind;
   use type E.Encoding_Level;
   use type M.Subject_Kind;
   function Sextet (B : Q.Byte) return E.Count is
     (if B in 65 .. 90 then E.Count (B - 65)
      elsif B in 97 .. 122 then E.Count (B - 97) + 26
      elsif B in 48 .. 57 then E.Count (B - 48) + 52
      elsif B = 43 then 62 elsif B = 47 then 63 else 0);
   function View_Length (Data : E.Bytes; Item : E.Byte_View) return E.Count
     with Global => null, Subprogram_Variant => (Decreases => Item.Level);
   function View_Byte (Data : E.Bytes; Item : E.Byte_View; Offset : E.Count)
      return Q.Byte with Global => null,
      Subprogram_Variant => (Decreases => Item.Level);
   function View_Byte (Data : E.Bytes; Item : E.Byte_View; Offset : E.Count)
      return Q.Byte is
   begin
      if Item.Level = 0 then
         if Offset >= Item.Encoded.Length or else
            not E.C.P.Valid (Data, Item.Encoded) then return 0; end if;
         return Data (Item.Encoded.First + Offset);
      end if;
      declare
         Prior : constant E.Byte_View := (Item.Encoded, Item.Level - 1);
         Base : constant E.Count := Offset / 3 * 4;
         A0 : constant E.Count := Sextet (View_Byte (Data, Prior, Base));
         A1 : constant E.Count := Sextet (View_Byte (Data, Prior, Base + 1));
         A2 : constant E.Count := Sextet (View_Byte (Data, Prior, Base + 2));
         A3 : constant E.Count := Sextet (View_Byte (Data, Prior, Base + 3));
      begin
         return Q.Byte
           (case Offset mod 3 is
              when 0 => A0 * 4 + A1 / 16,
              when 1 => A1 mod 16 * 16 + A2 / 4,
              when others => A2 mod 4 * 64 + A3);
      end;
   end View_Byte;
   function View_Length (Data : E.Bytes; Item : E.Byte_View) return E.Count is
   begin
      if Item.Level = 0 then return Item.Encoded.Length; end if;
      declare
         Prior : constant E.Byte_View := (Item.Encoded, Item.Level - 1);
         L : constant E.Count := View_Length (Data, Prior);
      begin
         if L = 0 then return 0; end if;
         if L mod 4 /= 0 then return 0; end if;
         return L / 4 * 3 -
           (if View_Byte (Data, Prior, L - 1) = 61 then
              (if View_Byte (Data, Prior, L - 2) = 61 then 2 else 1) else 0);
      end;
   end View_Length;
   function Payload (Data : E.Bytes; Item : E.Span; Field : String)
      return E.Byte_View is
     (E.Decode (Data, T.A.Field (Data, Item, Field), E.Operation).Payload);
   function SQL_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
     (V.Valid_Text (Data, Item) or else V.Valid_Bytes (Data, Item) or else
      V.Is_Integer (Data, Item) or else V.Is_Null (Data, Item) or else
      (V.Type_Is (Data, Item, "float") and then V.Valid_Hex_Field (Data, Item, "bits")
       and then View_Length (Data, Payload (Data, Item, "bits")) = 16));
   function SQL_Length (Data : E.Bytes; Item : E.Span) return E.Count is
     (if V.Valid_Text (Data, Item) then View_Length (Data, Payload (Data, Item, "value"))
      elsif V.Valid_Bytes (Data, Item) then View_Length (Data, Payload (Data, Item, "value")) / 2
      elsif V.Is_Integer (Data, Item) then View_Length (Data, Payload (Data, Item, "magnitude")) / 2
      elsif V.Type_Is (Data, Item, "float") then 8 else 0);
   function SQL_Byte_Count (Data : E.Bytes; Encoded : E.Span) return E.Count is
     (if SQL_Valid (Data, Encoded) then SQL_Length (Data, Encoded) else 0);
   function In_Prefix (Data : E.Bytes; Encoded : E.Span; Used : E.Count) return Boolean is
     (Used <= Data'Length and then Encoded.Length > 0 and then
      E.C.P.Valid (Data, Encoded) and then Encoded.First >= Data'First and then
      Encoded.First - Data'First < Used and then
      Encoded.Length <= Used - (Encoded.First - Data'First));
   procedure Append_SQL_Cell
     (Data : in out E.Bytes; Encoded : E.Span; Used : in out E.Count;
      Cell : out S.SQL_Cell; Status : out Decode_Status) is
      function Nibble (B : Q.Byte) return Q.Byte is
        (if B in 48 .. 57 then B - 48 else B - 97 + 10);
      Span : E.Span := (1, 0);
      Raw : E.Byte_View;
      Hex : Boolean := False;
      Sign : Boolean := False;
      Kind : S.SQL_Class := S.SQL_Null;
      Length : E.Count;
   begin
      Cell := (Kind => S.SQL_Null); Status := Malformed;
      if not In_Prefix (Data, Encoded, Used) or else not SQL_Valid (Data, Encoded) then return; end if;
      if V.Is_Null (Data, Encoded) then Status := Parsed; return; end if;
      if V.Valid_Text (Data, Encoded) then
         Raw := Payload (Data, Encoded, "value"); Kind := S.SQL_Text;
      elsif V.Valid_Bytes (Data, Encoded) then
         Raw := Payload (Data, Encoded, "value"); Kind := S.SQL_Blob; Hex := True;
      elsif V.Is_Integer (Data, Encoded) then
         Raw := Payload (Data, Encoded, "magnitude"); Kind := S.SQL_Integer;
         Hex := True; Sign := V.Negative (Data, Encoded);
      else Raw := Payload (Data, Encoded, "bits"); Kind := S.SQL_Real; Hex := True;
      end if;
      Length := View_Length (Data, Raw) / (if Hex then 2 else 1);
      if Length > Data'Length - Used then Status := Storage_Extent; return; end if;
      if Length > 0 then Span := (Data'First + Used, Length); end if;
      for I in E.Count range 1 .. Length loop
         if Hex then
            Data (Span.First + I - 1) := Nibble (View_Byte (Data, Raw, (I - 1) * 2)) * 16 +
              Nibble (View_Byte (Data, Raw, (I - 1) * 2 + 1));
         else Data (Span.First + I - 1) := View_Byte (Data, Raw, I - 1);
         end if;
      end loop;
      Used := Used + Length;
      case Kind is
         when S.SQL_Integer =>
            Cell := (Kind => S.SQL_Integer, Integer_Value => (Sign, Span.First, Span.Length));
         when S.SQL_Text => Cell := (Kind => S.SQL_Text, Bytes => (Span.First, Span.Length));
         when S.SQL_Blob => Cell := (Kind => S.SQL_Blob, Bytes => (Span.First, Span.Length));
         when S.SQL_Real => Cell := (Kind => S.SQL_Real, Bytes => (Span.First, Span.Length));
         when S.SQL_Null => Cell := (Kind => S.SQL_Null);
      end case;
      Status := Parsed;
   end Append_SQL_Cell;
   function Event_Extra_Byte_Count (Data : E.Bytes; Record_Archive : E.Span) return E.Count is
      Primitives : constant E.Span := T.Field (Data,
        T.Field (Data, Record_Archive, "x5"), "primitive_inputs");
      Total : E.Count := 0;
      procedure Add (Name : String) is
         Amount : constant E.Count := SQL_Byte_Count (Data, T.Field (Data, Primitives, Name));
      begin
         if Amount > E.Count'Last - Total then Total := E.Count'Last;
         else Total := Total + Amount; end if;
      end Add;
      Cause : constant E.Span := T.Field (Data, Primitives, "unknown_cause");
      Original : constant E.Span := T.Field (Data, Record_Archive, "original");
      procedure Add_Image (Item : E.Span) is
         Amount : constant E.Count := (if V.Valid_Bytes (Data, Item) then SQL_Length (Data, Item) else 0);
      begin
         if Amount > E.Count'Last - Total then Total := E.Count'Last;
         else Total := Total + Amount; end if;
      end Add_Image;
   begin
      Add ("reattach_epoch"); Add ("position"); Add ("next_subgeneration");
      Add ("transfer_mode"); Add ("abort_class");
      if T.Valid (Data, Cause) and then not V.Is_Null (Data, Cause) then
         if E.Count'Last - Total < 64 then return E.Count'Last; end if;
         Total := Total + 64;
      end if;
      Add_Image (Original);
      Add_Image (T.Field (Data, T.Field (Data, Record_Archive, "x5"), "root_evidence"));
      Add_Image (T.Field (Data, T.Field (Data, Record_Archive, "x5"), "native_observations"));
      Add_Image (T.Field (Data, T.Field (Data, Record_Archive, "x5"), "subject_evidence_raw"));
      return Total;
   end Event_Extra_Byte_Count;
   procedure Append_Event_Extras
     (Data : in out E.Bytes; Record_Archive : E.Span; Used : in out E.Count;
      Extras : out Event_Extra; Status : out Decode_Status) is
      Primitives : constant E.Span := T.Field (Data,
        T.Field (Data, Record_Archive, "x5"), "primitive_inputs");
      Cause : constant E.Span := T.Field (Data, Primitives, "unknown_cause");
      Original : constant E.Span := T.Field (Data, Record_Archive, "original");
      procedure Extra (Name : String; Cell : out S.SQL_Cell; Magnitude : Boolean := False) is
         Item : constant E.Span := T.Field (Data, Primitives, Name);
         Result : Decode_Status;
      begin
         Cell := (Kind => S.SQL_Null);
         if Status /= Parsed or else not SQL_Valid (Data, Item) or else V.Is_Null (Data, Item) then return; end if;
         Append_SQL_Cell (Data, Item, Used, Cell, Result);
         if Result /= Parsed then Status := Result; return; end if;
         if Magnitude and then Cell.Kind = S.SQL_Integer and then not Cell.Integer_Value.Negative then
            Cell := (Kind => S.SQL_Blob, Bytes => (Cell.Integer_Value.First, Cell.Integer_Value.Length));
         end if;
      end Extra;
      function Hex (B : Q.Byte) return Q.Byte is (if B < 10 then B + 48 else B - 10 + 97);
      procedure Materialize_Image
        (Item : E.Span; Payload : out E.Span; Format : out Original_Format) is
         Image : S.SQL_Cell;
      begin
         Payload := (1, 0); Format := No_Original;
         if Status /= Parsed then return; end if;
         if V.Valid_Bytes (Data, Item) then
            Append_SQL_Cell (Data, Item, Used, Image, Status);
            if Status /= Parsed then return; end if;
            if Image.Kind /= S.SQL_Blob then Status := Malformed; return; end if;
            Payload := (Image.Bytes.First, Image.Bytes.Length);
            if V.S.A.Valid (Data, Payload) then Format := Operation_Original; end if;
         elsif T.Valid (Data, Item) and then not V.Is_Null (Data, Item) then
            Payload := Item; Format := Scoped_Original;
         end if;
      end Materialize_Image;
   begin
      Extras := (Reattach_Epoch | Position | Next_Subgeneration | Transfer_Mode |
         Abort_Class | Unknown_Cause => (Kind => S.SQL_Null), Cause_Archive => (1, 0),
         Original_Payload | Root_Evidence_Payload | Native_Observations_Payload | Subject_Evidence_Payload => (1, 0),
         Original_Encoding | Root_Evidence_Encoding | Native_Observations_Encoding | Subject_Evidence_Encoding => No_Original);
      Status := Malformed;
      if not In_Prefix (Data, Record_Archive, Used) then return; end if;
      if Event_Extra_Byte_Count (Data, Record_Archive) > Data'Length - Used then
         Status := Storage_Extent; return;
      end if;
      Status := Parsed;
      Extra ("reattach_epoch", Extras.Reattach_Epoch, True);
      Extra ("position", Extras.Position, True);
      Extra ("next_subgeneration", Extras.Next_Subgeneration, True);
      Extra ("transfer_mode", Extras.Transfer_Mode);
      Extra ("abort_class", Extras.Abort_Class);
      if Status /= Parsed then return; end if;
      if T.Valid (Data, Cause) and then not V.Is_Null (Data, Cause) then
         declare Hash : constant C.SHA.Digest := C.G.Hash (Data, Cause);
                 First : constant Q.Byte_Index := Data'First + Used; begin
            Extras.Cause_Archive := Cause;
            Extras.Unknown_Cause := (Kind => S.SQL_Text, Bytes => (First, 64));
            for I in Hash'Range loop
               Data (First + E.Count (I - Hash'First) * 2) := Hex (Hash (I) / 16);
               Data (First + E.Count (I - Hash'First) * 2 + 1) := Hex (Hash (I) mod 16);
            end loop;
            Used := Used + 64;
         end;
      end if;
      Materialize_Image (Original, Extras.Original_Payload, Extras.Original_Encoding);
      Materialize_Image (T.Field (Data, T.Field (Data, Record_Archive, "x5"), "root_evidence"),
         Extras.Root_Evidence_Payload, Extras.Root_Evidence_Encoding);
      Materialize_Image (T.Field (Data, T.Field (Data, Record_Archive, "x5"), "native_observations"),
         Extras.Native_Observations_Payload, Extras.Native_Observations_Encoding);
      Materialize_Image (T.Field (Data, T.Field (Data, Record_Archive, "x5"), "subject_evidence_raw"),
         Extras.Subject_Evidence_Payload, Extras.Subject_Evidence_Encoding);
   end Append_Event_Extras;
   function Root_Name (Value : M.Root_Phase) return String is
     (case Value is
        when M.Front_Owned => "FRONT_OWNED",
        when M.Prepared => "PREPARED",
        when M.Held => "HELD",
        when M.Running => "RUNNING",
        when M.Execution_Native => "EXECUTION_NATIVE",
        when M.Execution_Ack => "EXECUTION_ACK",
        when M.Handoff_Intent => "HANDOFF_INTENT",
        when M.Front_Close_Intent => "FRONT_CLOSE_INTENT",
        when M.Front_Closed => "FRONT_CLOSED",
        when M.Transfer_Sent => "TRANSFER_SENT",
        when M.Roster_Evidence => "ROSTER_EVIDENCE",
        when M.Worker_Owned => "WORKER_OWNED",
        when M.Original_Result => "ORIGINAL_RESULT",
        when M.Handler_Terminal => "HANDLER_TERMINAL",
        when M.Worker_Relinquish => "WORKER_RELINQUISH",
        when M.Abandoned => "ABANDONED",
        when M.Front_Retained_Escrow => "FRONT_RETAINED_ESCROW",
        when M.Handoff_Aborted => "HANDOFF_ABORTED",
        when M.Custody_Returned => "CUSTODY_RETURNED",
        when M.Historical_Settlement => "HISTORICAL_SETTLEMENT",
        when M.Front_Reconstruction => "FRONT_RECONSTRUCTION",
        when M.Ended => "ENDED",
        when M.Unknown => "UNKNOWN");
   function Request_Name (Value : M.Request_Phase) return String is
     (case Value is
        when M.Queued => "QUEUED",
        when M.Transfer_Intent => "TRANSFER_INTENT",
        when M.Intake => "INTAKE",
        when M.Abandoned => "ABANDONED",
        when M.Responded => "RESPONDED",
        when M.Lost => "LOST");
   function Descriptor_Name (Value : M.Descriptor_Phase) return String is
     (case Value is
        when M.Front_Held => "FRONT_HELD",
        when M.Stop_Intent => "STOP_INTENT",
        when M.Frozen => "FROZEN",
        when M.Ofd_Evidence => "OFD_EVIDENCE",
        when M.Intake => "INTAKE",
        when M.Abandoned => "ABANDONED",
        when M.Released => "RELEASED",
        when M.Reclaimed => "RECLAIMED");
   function Abort_Name (Value : M.Abort_Class) return String is
     (case Value is
        when M.Never_Dispatched => "NEVER_DISPATCHED",
        when M.Dispatched => "DISPATCHED");
   function Mode_Name (Value : M.Transfer_Mode) return String is
     (case Value is
        when M.None => "NONE",
        when M.Fresh => "FRESH",
        when M.Relay => "RELAY");
   function Symbol_Length return E.Count is
      Total : E.Count := 1;
   begin
      for P in M.Root_Phase loop Total := Total + Root_Name (P)'Length; end loop;
      for P in M.Request_Phase loop Total := Total + Request_Name (P)'Length; end loop;
      for P in M.Descriptor_Phase loop Total := Total + Descriptor_Name (P)'Length; end loop;
      for P in M.Abort_Class loop Total := Total + Abort_Name (P)'Length; end loop;
      for P in M.Transfer_Mode loop Total := Total + Mode_Name (P)'Length; end loop;
      return Total;
   end Symbol_Length;
   function Counts (Data : E.Bytes; Envelope : E.Span) return Sizes is
      Input : constant E.Span := Envelope;
      Result : Sizes;
      Good : Boolean := True;
      procedure Add (Amount : E.Count) is
      begin
         if Amount > E.Count'Last - Result.Arena then
            Good := False; Result.Status := Storage_Extent;
         else Result.Arena := Result.Arena + Amount; end if;
      end Add;
      procedure Table (Name : String; Width : Positive; Rows : out E.Count) is
         Seq : constant E.Span := T.Field (Data, Input, Name);
      begin
         Rows := 0;
         if not V.Is_Sequence (Data, Seq) then Good := False; return; end if;
         Rows := V.Count (Data, Seq);
         for I in E.Count range 1 .. Rows loop
            declare
               Row : constant E.Span := V.Element (Data, Seq, I - 1);
            begin
               if not V.Is_Sequence (Data, Row) or else
                 V.Count (Data, Row) /= E.Count (Width) then Good := False; return; end if;
               for J in 1 .. Width loop
                  declare
                     Cell : constant E.Span := V.Element (Data, Row, E.Count (J - 1));
                  begin
                     if not SQL_Valid (Data, Cell) then Good := False; return; end if;
                     Add (SQL_Length (Data, Cell));
                  end;
               end loop;
            end;
         end loop;
      end Table;
      procedure Bytes_Field (Name : String; Text : Boolean := False) is
         Item : constant E.Span := T.Field (Data, Input, Name);
      begin
         if (if Text then not V.Valid_Text (Data, Item) else not V.Valid_Bytes (Data, Item)) then
            Good := False;
         else Add (SQL_Length (Data, Item)); end if;
      end Bytes_Field;
   begin
      if not T.Valid (Data, Input) or else T.Member_Count (Data, Input) /= 13 or else
         not T.Text_Is (Data, T.Field (Data, Input, "schema"), "worldline.custody-load-v2") then
         return Result;
      end if;
      Result.Arena := Data'Length;
      Add (Symbol_Length);
      Bytes_Field ("key"); Bytes_Field ("genesis_file"); Bytes_Field ("genesis_row");
      Bytes_Field ("genesis_message"); Bytes_Field ("genesis_mac", True);
      if not T.Valid (Data, T.Field (Data, Input, "owner_roster")) then return Result; end if;
      declare
         Capture : constant E.Span := T.Field (Data,
           T.Field (Data, T.Field (Data, Input, "owner_roster"), "startup_native"), "capture");
      begin
         if V.Valid_Bytes (Data, Capture) then Add (SQL_Length (Data, Capture)); end if;
      end;
      Table ("events", 13, Result.Events); Table ("heads", 5, Result.Heads);
      Table ("roots", 16, Result.Roots); Table ("subjects", 9, Result.Subjects);
      Table ("alternatives", 7, Result.Alternatives); Table ("blobs", 3, Result.Blobs);
      declare
         Messages : constant E.Span := T.Field (Data, T.Field (Data, Input, "owner_roster"), "custody_head_messages");
      begin
         if not V.Is_Sequence (Data, Messages) or else V.Count (Data, Messages) /= Result.Heads then
            Good := False;
         else
            for I in E.Count range 1 .. Result.Heads loop
               declare Item : constant E.Span := V.Element (Data, Messages, I - 1);
               begin
                  if not V.Valid_Bytes (Data, Item) then Good := False;
                  else Add (SQL_Length (Data, Item)); end if;
               end;
            end loop;
         end if;
      end;
      for I in E.Count range 1 .. Result.Events loop
         declare
            Row : constant E.Span := V.Element (Data, T.Field (Data, Input, "events"), I - 1);
            Record_Cell : constant E.Span := V.Element (Data, Row, 10);
         begin
            if V.Valid_Bytes (Data, Record_Cell) then
               declare
                  Raw : constant E.Bytes := V.Bytes_Value (Data, Record_Cell);
               begin
                  Add (Event_Extra_Byte_Count (Raw, (Raw'First, Raw'Length)));
               end;
            end if;
         end;
      end loop;
      if Good then Result.Status := Parsed; end if;
      return Result;
   end Counts;
   function Counts (Data : E.Bytes) return Sizes is
     (Counts (Data, (Data'First, Data'Length)));

   function Parsed_Spans_Valid (Value : Parsed_Input) return Boolean is
      function Cells (Rows : SQL_Rows; Count : E.Count) return Boolean is
        (Count <= Rows'Length (1) and then (for all I in E.Count range 1 .. Count =>
           (for all J in Rows'Range (2) =>
              (case Rows (I, J).Kind is
                 when S.SQL_Null => True,
                 when S.SQL_Integer => Q.Span_Valid (Value.Arena, Rows (I, J).Integer_Value),
                 when others => S.Span_Valid (Value.Arena, Rows (I, J).Bytes)))));
   begin
      return Value.Decoded_Event_Count <= Value.Event_Count and then
        Value.Arena_Used <= Value.Arena_Count and then
        E.C.P.Valid (Value.Arena, Value.Input) and then
        E.C.P.Valid (Value.Arena, Value.Source_Input) and then
        Value.Source_Input.First = 1 and then Value.Input.First >= Value.Source_Input.First and then
        Value.Input.First - Value.Source_Input.First <= Value.Source_Input.Length and then
        Value.Input.Length <= Value.Source_Input.Length - (Value.Input.First - Value.Source_Input.First) and then
        E.C.P.Valid (Value.Arena, Value.Key) and then
        E.C.P.Valid (Value.Arena, Value.Genesis_File) and then
        E.C.P.Valid (Value.Arena, Value.Genesis_Row) and then
        E.C.P.Valid (Value.Arena, Value.Genesis_Message) and then
        E.C.P.Valid (Value.Arena, Value.Genesis_Mac) and then
        E.C.P.Valid (Value.Arena, Value.Owner_Roster) and then
        E.C.P.Valid (Value.Arena, Value.Startup_Capture_Payload) and then
        (for all I in E.Count range 1 .. Value.Decoded_Event_Count =>
           E.C.P.Valid (Value.Arena, Value.Extras (I).Cause_Archive) and then
           E.C.P.Valid (Value.Arena, Value.Extras (I).Original_Payload) and then
           E.C.P.Valid (Value.Arena, Value.Extras (I).Root_Evidence_Payload) and then
           E.C.P.Valid (Value.Arena, Value.Extras (I).Subject_Evidence_Payload) and then
           E.C.P.Valid (Value.Arena, Value.Extras (I).Native_Observations_Payload)) and then
        Cells (Value.Event_SQL, Value.Decoded_Event_Count) and then Cells (Value.Head_SQL, Value.Head_Count) and then
        Cells (Value.Root_SQL, Value.Root_Count) and then Cells (Value.Subject_SQL, Value.Subject_Count) and then
        Cells (Value.Alternative_SQL, Value.Alternative_Count) and then Cells (Value.Blob_SQL, Value.Blob_Count);
   end Parsed_Spans_Valid;
   procedure Decode_Into (Data : E.Bytes; Envelope : E.Span; Value : out Parsed_Input;
                          Decoded_Used : out E.Count; Grown : Boolean) is
      Size : constant Sizes := Counts (Data, Envelope);
      Used : E.Count := Data'Length;
      Good : Boolean := True;
      function Nibble (B : Q.Byte) return Q.Byte is
        (if B in 48 .. 57 then B - 48 else B - 97 + 10);
      procedure Cell (Encoded : E.Span; Result : out S.SQL_Cell) is
         Status : Decode_Status;
      begin
         Append_SQL_Cell (Value.Arena, Encoded, Used, Result, Status);
         if Status /= Parsed then Good := False; end if;
      end Cell;
      procedure Global_Field (Name : String; Span : out E.Span) is
         Result : S.SQL_Cell;
      begin
         Cell (T.Field (Value.Arena, Value.Input, Name), Result);
         if Result.Kind not in S.SQL_Text | S.SQL_Blob then Good := False; Span := (1, 0);
         else Span := (Result.Bytes.First, Result.Bytes.Length); end if;
      end Global_Field;
      procedure Table (Name : String; Rows : in out SQL_Rows; Encoded : in out Span_Array;
                       Count : E.Count) is
         Seq : constant E.Span := T.Field (Value.Arena, Value.Input, Name);
      begin
         for I in E.Count range 1 .. Count loop
            Encoded (I) := V.Element (Value.Arena, Seq, I - Rows'First (1));
            for J in Rows'Range (2) loop
               Cell (V.Element (Value.Arena, Encoded (I), E.Count (J - Rows'First (2))), Rows (I, J));
            end loop;
         end loop;
      end Table;
      function Raw_Span (Cell : S.SQL_Cell; Kind : S.SQL_Class) return E.Span is
      begin
         if Cell.Kind /= Kind or else Kind not in S.SQL_Text | S.SQL_Blob | S.SQL_Real then
            return (1, 0);
         end if;
         return (Cell.Bytes.First, Cell.Bytes.Length);
      end Raw_Span;
      function Optional (Cell : S.SQL_Cell) return C.Optional_Span is
      begin
         if Cell.Kind = S.SQL_Null then return (Present => False); end if;
         return (Present => True, Value => Raw_Span (Cell, S.SQL_Text));
      end Optional;
      function Quantity (Cell : S.SQL_Cell) return Q.Quantity is
         Span : constant E.Span := Raw_Span (Cell, S.SQL_Blob);
      begin return (False, Span.First, Span.Length); end Quantity;
      function Identity (Cell : S.SQL_Cell) return M.Identity is
      begin
         case Cell.Kind is
            when S.SQL_Null => return (Present => False);
            when S.SQL_Integer => return (Present => True, Value =>
              (Cell.Integer_Value.First, Cell.Integer_Value.Length));
            when others => return (Present => True, Value => (Cell.Bytes.First, Cell.Bytes.Length));
         end case;
      end Identity;
      function Digest (Cell : S.SQL_Cell) return M.Digest is
         Span : constant E.Span := Raw_Span (Cell, S.SQL_Text);
         Result : M.Digest := (others => 0);
      begin
         if Span.Length /= 64 then return Result; end if;
         for B in E.Count range 0 .. Span.Length - 1 loop
            if Value.Arena (Span.First + B) not in 48 .. 57 | 97 .. 102 then
               return Result;
            end if;
         end loop;
         for I in Result'Range loop
            Result (I) := Nibble (Value.Arena (Span.First + E.Count (I - Result'First) * 2)) * 16 +
              Nibble (Value.Arena (Span.First + E.Count (I - Result'First) * 2 + 1));
         end loop;
         return Result;
      end Digest;
      procedure Intern (Name : String; Result : out S.SQL_Cell) is
         Span : E.Span := (1, 0);
      begin
         if Name'Length > Value.Arena_Count - Used then Good := False;
         elsif Name'Length > 0 then
            Span := (Used + 1, Name'Length);
            for I in Name'Range loop
               Value.Arena (Span.First + E.Count (I - Name'First)) := Q.Byte (Character'Pos (Name (I)));
            end loop;
            Used := Used + Name'Length;
         end if;
         Result := (Kind => S.SQL_Text, Bytes => (Span.First, Span.Length));
      end Intern;
      procedure Event_Extras (Index : Q.Byte_Index) is
         Result : Decode_Status;
      begin
         Append_Event_Extras (Value.Arena, Value.Events (Index).Record_Archive, Used, Value.Extras (Index), Result);
         if Result /= Parsed then Good := False; end if;
      end Event_Extras;
   begin
      Decoded_Used := 0; Value.Decoded_Event_Count := 0; Value.Arena_Used := 0;
      Value.Status := Malformed;
      for I in Value.Arena'Range loop
         if I <= Data'Length then Value.Arena (I) := Data (Data'First + I - 1);
         else Value.Arena (I) := 0;
         end if;
      end loop;
      Value.Input := (1, 0); Value.Key := (1, 0); Value.Genesis_File := (1, 0);
      Value.Source_Input := (1, 0);
      Value.Genesis_Row := (1, 0); Value.Genesis_Message := (1, 0);
      Value.Genesis_Mac := (1, 0); Value.Owner_Roster := (1, 0);
      Value.Startup_Capture_Payload := (1, 0);
      Value.Startup_Capture_Encoding := No_Original;
      Value.Events := (others => (others => (1, 0)));
      Value.Extras := (others => (Reattach_Epoch | Position | Next_Subgeneration |
         Transfer_Mode | Abort_Class | Unknown_Cause => (Kind => S.SQL_Null),
         Cause_Archive | Original_Payload | Root_Evidence_Payload | Native_Observations_Payload | Subject_Evidence_Payload => (1, 0),
         Original_Encoding | Root_Evidence_Encoding | Native_Observations_Encoding | Subject_Evidence_Encoding => No_Original));
      Value.Heads := (others => (Name | Kind | Mac | Message => (1, 0),
         Event_Id | Origin => (Present => False)));
      Value.Roots := (others => (Present => False)); Value.Subjects := (others => (Present => False));
      Value.Alternatives := (others => (Generation | Subgeneration => (False, 1, 0),
         Operation | Subject => (Present => False), Kind_Of_Subject => M.Root,
         Set => A.Ack_Set, Event_Id => (others => 0)));
      Value.Event_SQL := (others => (others => (Kind => S.SQL_Null)));
      Value.Head_SQL := (others => (others => (Kind => S.SQL_Null)));
      Value.Root_SQL := (others => (others => (Kind => S.SQL_Null)));
      Value.Subject_SQL := (others => (others => (Kind => S.SQL_Null)));
      Value.Alternative_SQL := (others => (others => (Kind => S.SQL_Null)));
      Value.Blob_SQL := (others => (others => (Kind => S.SQL_Null)));
      Value.Event_Encoded := (others => (1, 0)); Value.Head_Encoded := (others => (1, 0));
      Value.Root_Encoded := (others => (1, 0)); Value.Subject_Encoded := (others => (1, 0));
      Value.Alternative_Encoded := (others => (1, 0)); Value.Blob_Encoded := (others => (1, 0));
      Value.Symbols := (Root => (others => (Kind => S.SQL_Null)),
         Request => (others => (Kind => S.SQL_Null)), Descriptor => (others => (Kind => S.SQL_Null)),
         Abort_Name => (others => (Kind => S.SQL_Null)), Mode => (others => (Kind => S.SQL_Null)),
         Zero | One | Zero_Magnitude | Empty_Text => (Kind => S.SQL_Null));
      if Size.Status /= Parsed then Value.Status := Size.Status; return; end if;
      if (if Grown then Value.Arena_Count < Size.Arena or else
            Value.Event_Count <= Size.Events or else Value.Event_Count - Size.Events /= 1
          else Value.Arena_Count /= Size.Arena or else Value.Event_Count /= Size.Events) or else
         Value.Head_Count /= Size.Heads or else Value.Root_Count /= Size.Roots or else
         Value.Subject_Count /= Size.Subjects or else Value.Alternative_Count /= Size.Alternatives or else
         Value.Blob_Count /= Size.Blobs then Value.Status := Storage_Extent; return; end if;
      Value.Input := (Envelope.First - Data'First + 1, Envelope.Length);
      Value.Source_Input := (1, Data'Length);
      Value.Decoded_Event_Count := Size.Events;
      Value.Owner_Roster := T.Field (Value.Arena, Value.Input, "owner_roster");
      declare
         Capture : constant E.Span := T.Field (Value.Arena,
           T.Field (Value.Arena, Value.Owner_Roster, "startup_native"), "capture");
         Image : S.SQL_Cell;
      begin
         if V.Valid_Bytes (Value.Arena, Capture) then
            Cell (Capture, Image);
            if Image.Kind = S.SQL_Blob then
               Value.Startup_Capture_Payload := (Image.Bytes.First, Image.Bytes.Length);
               if V.S.A.Valid (Value.Arena, Value.Startup_Capture_Payload) then
                  Value.Startup_Capture_Encoding := Operation_Original;
               end if;
            end if;
         end if;
      end;
      Global_Field ("key", Value.Key); Global_Field ("genesis_file", Value.Genesis_File);
      Global_Field ("genesis_row", Value.Genesis_Row); Global_Field ("genesis_message", Value.Genesis_Message);
      Global_Field ("genesis_mac", Value.Genesis_Mac);
      Table ("events", Value.Event_SQL, Value.Event_Encoded, Size.Events);
      Table ("heads", Value.Head_SQL, Value.Head_Encoded, Size.Heads);
      Table ("roots", Value.Root_SQL, Value.Root_Encoded, Size.Roots);
      Table ("subjects", Value.Subject_SQL, Value.Subject_Encoded, Size.Subjects);
      Table ("alternatives", Value.Alternative_SQL, Value.Alternative_Encoded, Size.Alternatives);
      Table ("blobs", Value.Blob_SQL, Value.Blob_Encoded, Size.Blobs);
      for I in E.Count range 1 .. Size.Events loop
         Value.Events (I) :=
           (Event_Id => Raw_Span (Value.Event_SQL (I, 2), S.SQL_Text),
            Previous => Raw_Span (Value.Event_SQL (I, 3), S.SQL_Text),
            Generation => Raw_Span (Value.Event_SQL (I, 4), S.SQL_Blob),
            Operation => Raw_Span (Value.Event_SQL (I, 5), S.SQL_Text),
            Subject_Kind => Raw_Span (Value.Event_SQL (I, 6), S.SQL_Text),
            Subject => Raw_Span (Value.Event_SQL (I, 7), S.SQL_Text),
            Subgeneration => Raw_Span (Value.Event_SQL (I, 8), S.SQL_Blob),
            Kind => Raw_Span (Value.Event_SQL (I, 9), S.SQL_Text),
            Actor => Raw_Span (Value.Event_SQL (I, 10), S.SQL_Text),
            Record_Archive => Raw_Span (Value.Event_SQL (I, 11), S.SQL_Blob),
            Base_Archive => Raw_Span (Value.Event_SQL (I, 12), S.SQL_Blob),
            Mac => Raw_Span (Value.Event_SQL (I, 13), S.SQL_Text));
      end loop;
      declare
         Messages : constant E.Span := T.Field (Value.Arena, Value.Owner_Roster, "custody_head_messages");
      begin
         for I in Value.Heads'Range loop
            Value.Heads (I) := (Name => Raw_Span (Value.Head_SQL (I, 1), S.SQL_Text),
              Kind => Raw_Span (Value.Head_SQL (I, 2), S.SQL_Text),
              Event_Id => Optional (Value.Head_SQL (I, 3)), Origin => Optional (Value.Head_SQL (I, 4)),
              Mac => Raw_Span (Value.Head_SQL (I, 5), S.SQL_Text), Message => (1, 0));
            declare Head_Message : S.SQL_Cell; begin
               Cell (V.Element (Value.Arena, Messages, I - 1), Head_Message);
               Value.Heads (I).Message := Raw_Span (Head_Message, S.SQL_Blob);
            end;
         end loop;
      end;
      for I in Value.Roots'Range loop
         Value.Roots (I) := (Present => True, Columns =>
           (Generation => Value.Root_SQL (I, 1),
            Operation => Value.Root_SQL (I, 2),
            Phase => Value.Root_SQL (I, 3),
            Before_Unknown => Value.Root_SQL (I, 4),
            Owners_Open => Value.Root_SQL (I, 5),
            Abort_Kind => Value.Root_SQL (I, 6),
            Launched => Value.Root_SQL (I, 7),
            Closure_NS => Value.Root_SQL (I, 8),
            Closure_Outer => Value.Root_SQL (I, 9),
            Closure_Raw => Value.Root_SQL (I, 10),
            Witness => Value.Root_SQL (I, 11),
            Settled => Value.Root_SQL (I, 12),
            Released_Unlaunched => Value.Root_SQL (I, 13),
            Unknown_Cause => Value.Root_SQL (I, 14),
            Reattach_Epoch => Value.Root_SQL (I, 15),
            Head_Event => Value.Root_SQL (I, 16)));
      end loop;
      for I in Value.Subjects'Range loop
         Value.Subjects (I) := (Present => True, Columns =>
           (Generation => Value.Subject_SQL (I, 1),
            Kind_Of_Subject => Value.Subject_SQL (I, 2),
            Subject => Value.Subject_SQL (I, 3),
            Subgeneration => Value.Subject_SQL (I, 4),
            Phase => Value.Subject_SQL (I, 5),
            Mode => Value.Subject_SQL (I, 6),
            Position => Value.Subject_SQL (I, 7),
            Carried_From => Value.Subject_SQL (I, 8),
            Head_Event => Value.Subject_SQL (I, 9)));
      end loop;
      for I in Value.Alternatives'Range loop
         declare
            Kind : M.Subject_Kind := M.Root;
            Family : A.Alternative_Set := A.Ack_Set;
         begin
            if S.Text_Is (Value.Arena, Value.Alternative_SQL (I, 3), "REQUEST") then Kind := M.Request;
            elsif S.Text_Is (Value.Arena, Value.Alternative_SQL (I, 3), "DESCRIPTOR") then Kind := M.Descriptor;
            elsif not S.Text_Is (Value.Arena, Value.Alternative_SQL (I, 3), "ROOT") then Good := False; end if;
            if S.Text_Is (Value.Arena, Value.Alternative_SQL (I, 6), "REQUEST") then Family := A.Request_Set;
            elsif S.Text_Is (Value.Arena, Value.Alternative_SQL (I, 6), "DRAIN") then Family := A.Drain_Set;
            elsif not S.Text_Is (Value.Arena, Value.Alternative_SQL (I, 6), "ACK") then Good := False; end if;
            Value.Alternatives (I) := (Generation => Quantity (Value.Alternative_SQL (I, 1)),
              Operation => Identity (Value.Alternative_SQL (I, 2)), Kind_Of_Subject => Kind,
              Subject => Identity (Value.Alternative_SQL (I, 4)), Subgeneration => Quantity (Value.Alternative_SQL (I, 5)),
              Set => Family, Event_Id => Digest (Value.Alternative_SQL (I, 7)));
         end;
      end loop;
      for I in E.Count range 1 .. Size.Events loop Event_Extras (I); end loop;
      for P in M.Root_Phase loop Intern (Root_Name (P), Value.Symbols.Root (P)); end loop;
      for P in M.Request_Phase loop Intern (Request_Name (P), Value.Symbols.Request (P)); end loop;
      for P in M.Descriptor_Phase loop Intern (Descriptor_Name (P), Value.Symbols.Descriptor (P)); end loop;
      for P in M.Abort_Class loop Intern (Abort_Name (P), Value.Symbols.Abort_Name (P)); end loop;
      for P in M.Transfer_Mode loop Intern (Mode_Name (P), Value.Symbols.Mode (P)); end loop;
      Intern ("", Value.Symbols.Empty_Text);
      Value.Symbols.Zero := (Kind => S.SQL_Integer, Integer_Value => (False, 1, 0));
      Value.Symbols.Zero_Magnitude := (Kind => S.SQL_Blob, Bytes => (1, 0));
      if Used < Value.Arena_Count then
         Used := Used + 1; Value.Arena (Used) := 1;
         Value.Symbols.One := (Kind => S.SQL_Integer, Integer_Value => (False, Used, 1));
      else Good := False; end if;
      Decoded_Used := Used; Value.Arena_Used := Used;
      if Good and then Used = Size.Arena and then Parsed_Spans_Valid (Value) and then
         N.Valid (Value.Arena, Value.Symbols) then Value.Status := Parsed; end if;
   end Decode_Into;
   procedure Decode (Data : E.Bytes; Envelope : E.Span; Value : out Parsed_Input) is
      Used : E.Count;
   begin
      Decode_Into (Data, Envelope, Value, Used, False);
   end Decode;
   procedure Decode_Grown (Data : E.Bytes; Envelope : E.Span; Value : out Parsed_Input; Used : out E.Count) is
   begin
      Decode_Into (Data, Envelope, Value, Used, True);
   end Decode_Grown;
   procedure Decode (Data : E.Bytes; Value : out Parsed_Input) is
   begin
      Decode (Data, (Data'First, Data'Length), Value);
   end Decode;
end Worldline.Custody_V2_Load_Input;
