with Canonical_Artifacts;
with SPARK.Big_Integers;
with Worldline.Startup_Source_Custody;
with Worldline.Startup_Installation;
with Worldline.Custody_V2_Requester_Join;
with Worldline.Custody_V2_Root_Evidence;
package body Worldline.Excluded_Source_Owner with SPARK_Mode is
   package V renames L.V;
   package S renames V.S;
   package C renames Worldline.Startup_Source_Custody;
   package P renames Worldline.Startup_Installation;
   package J renames Worldline.Custody_V2_Requester_Join;
   package R renames Worldline.Custody_V2_Root_Evidence;
   use SPARK.Big_Integers;
   use type E.Count;
   use type E.Bytes;
   use type E.Q.Byte;
   use type E.Value_Kind;
   use type Canonical_Artifacts.Genesis_Correspondence;
   function F (D : E.Bytes; X : E.Span; Name : String) return E.Span renames S.Field;
   function Same (D : E.Bytes; A, B : E.Span) return Boolean renames J.Same;
   function Num (D : E.Bytes; X : E.Span; N : Long_Long_Integer) return Boolean renames J.Integer_Is;
   function JSON_Matches (D : E.Bytes; Raw, Value : E.Span) return Boolean
     with Global => null, Depends => (JSON_Matches'Result => (D, Raw, Value)) is
   begin
      if not V.Valid_Bytes (D, Raw) then return False; end if;
      declare B : constant E.Bytes := V.Bytes_Value (D, Raw); begin
         return Canonical_Artifacts.Scoped_Archive_JSON_Matches
           (B, D, (B'First, B'Length), Value) = Canonical_Artifacts.Typed_Tree_Matches_Source_Custody_Open;
      end;
   end JSON_Matches;
   function Hex_Matches (D : E.Bytes; Hex, Raw : E.Span) return Boolean
     with Global => null, Depends => (Hex_Matches'Result => (D, Hex, Raw)) is
     (V.Valid_Hex_Field (D, Hex, "value") and then V.Valid_Bytes (D, Raw) and then
      V.Hex_Value (D, Hex, "value") = V.Bytes_Value (D, Raw));
   function Bit (N : Valid_Big_Integer; Position : Natural) return Boolean
     with Global => null, Depends => (Bit'Result => (N, Position)) is
     ((N / (To_Big_Integer (2) ** Position)) mod 2 = 1);
   function Sealed (D : E.Bytes; Value : E.Span) return Boolean
     with Global => null, Depends => (Sealed'Result => (D, Value)) is
     (V.Is_Integer (D, Value) and then R.Number (D, Value) >= 0 and then
      (for all I in Natural range 0 .. 3 => Bit (R.Number (D, Value), I)));
   function Identity (D : E.Bytes; A, B : E.Span) return Boolean
     with Global => null, Depends => (Identity'Result => (D, A, B)) is
   begin
      for I in 1 .. 5 loop
         declare Name : constant String := (case I is when 1 => "device", when 2 => "inode",
           when 3 => "mode", when 4 => "uid", when 5 => "gid"); begin
            if not V.Is_Integer (D, F (D, A, Name)) or else not Same (D, F (D, A, Name), F (D, B, Name)) then
               return False;
            end if;
         end;
      end loop;
      return True;
   end Identity;
   function FD_Number (D : E.Bytes; X : E.Span) return Boolean
     with Global => null, Depends => (FD_Number'Result => (D, X)) is
     (V.Is_Integer (D, X) and then R.Number (D, X) >= 0 and then R.Number (D, X) <= 2_147_483_647);
   function Descriptor_Reference (D : E.Bytes; X : E.Span) return Boolean
     with Global => null, Depends => (Descriptor_Reference'Result => (D, X)) is
     (FD_Number (D, F (D, X, "fd")) and then V.Is_Integer (D, F (D, X, "mode")) and then
      R.Number (D, F (D, X, "mode")) >= 0 and then
      (V.Valid_Bytes (D, F (D, X, "fdinfo")) or else V.Valid_Hex_Field (D, F (D, X, "fdinfo_hex"), "value")));
   function Process_Reference (D : E.Bytes; Process, Raw : E.Span) return Boolean
     with Global => null, Depends => (Process_Reference'Result => (D, Process, Raw)) is
     (V.Is_Integer (D, F (D, Process, "pid")) and then R.Number (D, F (D, Process, "pid")) > 0 and then
      V.Is_Integer (D, F (D, Process, "start_tick")) and then R.Number (D, F (D, Process, "start_tick")) >= 0 and then
      Hex_Matches (D, F (D, Process, "stat_hex"), Raw) and then
      R.Stat_Field (D, Raw, 1) = R.Number (D, F (D, Process, "pid")) and then
      R.Stat_Field (D, Raw, 22) = R.Number (D, F (D, Process, "start_tick")));
   function Projection_Reference (D : E.Bytes; Capture, Descriptor, Projected : E.Span) return Boolean
     with Global => null, Depends => (Projection_Reference'Result => (D, Capture, Descriptor, Projected)) is
      Before : constant E.Span := F (D, Capture, "before");
      Encoded : constant E.Span := F (D, Projected, "envelope_bytes_hex");
   begin
      if not Descriptor_Reference (D, Before) or else not Descriptor_Reference (D, Descriptor) or else
         not Same (D, F (D, Capture, "fd"), F (D, Before, "fd")) or else
         not Identity (D, Before, Descriptor) or else
         not Num (D, F (D, Before, "uid"), 0) or else R.Number (D, F (D, Before, "mode")) / 4096 /= 8 or else
         not V.Valid_Hex_Field (D, Encoded, "value") or else
         not Same (D, F (D, Capture, "raw_hex"), Encoded) or else
         not Same (D, F (D, Capture, "readback_hex"), Encoded) or else
         not Sealed (D, F (D, Capture, "seals_before")) or else not Sealed (D, F (D, Capture, "seals_after")) or else
         not J.Unsigned_Is (D, F (D, Before, "size"), V.Hex_Value (D, Encoded, "value")'Length) then return False; end if;
      for I in 1 .. 2 loop
         declare Current : constant E.Span := F (D, Capture, (if I = 1 then "after" else "final")); begin
            if not Descriptor_Reference (D, Current) or else not Identity (D, Before, Current) or else
               not Same (D, F (D, Before, "size"), F (D, Current, "size")) or else
               not Same (D, F (D, Before, "fd"), F (D, Current, "fd")) then return False; end if;
         end;
      end loop;
      return True;
   end Projection_Reference;
   function Root_Directory (D : E.Bytes; X : E.Span) return Boolean
     with Global => null, Depends => (Root_Directory'Result => (D, X)) is
      Mode : constant E.Span := F (D, X, "mode");
   begin
      return V.Is_Integer (D, Mode) and then Num (D, F (D, X, "uid"), 0) and then
        R.Number (D, Mode) / 4096 = 4 and then not Bit (R.Number (D, Mode), 1) and then
        not Bit (R.Number (D, Mode), 4);
   end Root_Directory;
   function Boolean_Is (D : E.Bytes; X : E.Span; B : Boolean) return Boolean
     with Global => null, Depends => (Boolean_Is'Result => (D, X, B)) is
     (V.Type_Is (D, X, "bool") and then
      E.Decode (D, S.A.Field (D, X, "value"), E.Operation).Form = E.Boolean_Value and then
      E.Decode (D, S.A.Field (D, X, "value"), E.Operation).Boolean_Bit = B);
   function Prefix_Events (D : E.Bytes; Before, After : E.Span) return Boolean
     with Global => null, Depends => (Prefix_Events'Result => (D, Before, After)) is
   begin
      if not V.Is_Sequence (D, Before) or else not V.Is_Sequence (D, After) or else
         V.Count (D, Before) > V.Count (D, After) then return False; end if;
      for I in E.Count range 1 .. V.Count (D, Before) loop
         if not Same (D, V.Element (D, Before, I - 1), V.Element (D, After, I - 1)) then return False; end if;
      end loop;
      return True;
   end Prefix_Events;
   function Decimal (B : E.Bytes; First, Last : E.Count) return Valid_Big_Integer
     with Global => null, Depends => (Decimal'Result => (B, First, Last)) is
      Result : Valid_Big_Integer := To_Big_Integer (0);
   begin
      if First not in B'Range or else Last not in B'Range or else First > Last then return To_Big_Integer (-1); end if;
      for I in First .. Last loop
         if B (I) not in Character'Pos ('0') .. Character'Pos ('9') then return To_Big_Integer (-1); end if;
         Result := Result * 10 + To_Big_Integer (Integer (B (I) - Character'Pos ('0')));
      end loop;
      return Result;
   end Decimal;
   -- Kernel status is independently acquired by the owner and by the actor.
   -- Parse complete original columns, including supplementary group multiplicity.
   function Status_Columns
     (D : E.Bytes; Raw, Expected : E.Span; Name : String; Repeat : Boolean; Columns : E.Count := 0) return Boolean
     with Global => null, Depends => (Status_Columns'Result => (D, Raw, Expected, Name, Repeat, Columns)) is
      Found : Boolean := False;
      Seen : E.Count := 0;
   begin
      if not V.Valid_Bytes (D, Raw) then return False; end if;
      declare B : constant E.Bytes := V.Bytes_Value (D, Raw);
              Start : E.Count := B'First; begin
         for Stop in B'Range loop
            if B (Stop) = 10 then
               if Stop - Start >= Name'Length and then
                 (for all I in Name'Range => B (Start + E.Count (I - Name'First)) = Character'Pos (Name (I))) then
                  if Found then return False; end if;
                  Found := True;
                  declare At : E.Count := Start + Name'Length;
                          First : E.Count := 0; begin
                     while At < Stop loop
                        if B (At) in Character'Pos ('0') .. Character'Pos ('9') then
                           First := At;
                           while At < Stop and then B (At) in Character'Pos ('0') .. Character'Pos ('9') loop
                              At := At + 1;
                           end loop;
                           if Repeat then
                              if not V.Is_Integer (D, Expected) or else Decimal (B, First, At - 1) /= R.Number (D, Expected) then
                                 return False;
                              end if;
                           else
                              if Seen >= V.Count (D, Expected) or else not V.Is_Integer (D, V.Element (D, Expected, Seen)) or else
                                 Decimal (B, First, At - 1) /= R.Number (D, V.Element (D, Expected, Seen)) then return False; end if;
                           end if;
                           Seen := Seen + 1;
                        elsif B (At) = 9 or else B (At) = 32 then At := At + 1;
                        else return False;
                        end if;
                     end loop;
                  end;
               end if;
               if Stop < B'Last then Start := Stop + 1; end if;
            end if;
         end loop;
      end;
      return Found and then Seen = (if Repeat then Columns else V.Count (D, Expected));
   end Status_Columns;
   function Group_Multiset (D : E.Bytes; Actual, Selected : E.Span) return Boolean
     with Global => null, Depends => (Group_Multiset'Result => (D, Actual, Selected)) is
   begin
      if not V.Is_Sequence (D, Actual) or else not V.Is_Sequence (D, Selected) or else
         V.Count (D, Actual) /= V.Count (D, Selected) then return False; end if;
      for I in E.Count range 1 .. V.Count (D, Actual) loop
         declare Item : constant E.Span := V.Element (D, Actual, I - 1);
                 A, B : E.Count := 0; begin
            if not V.Is_Integer (D, Item) then return False; end if;
            for K in E.Count range 1 .. V.Count (D, Actual) loop
               if Same (D, Item, V.Element (D, Actual, K - 1)) then A := A + 1; end if;
               if Same (D, Item, V.Element (D, Selected, K - 1)) then B := B + 1; end if;
            end loop;
            if A /= B then return False; end if;
         end;
      end loop;
      return True;
   end Group_Multiset;
   function Poll_Matches (D : E.Bytes; Poll, Pidfd : E.Span; Terminal : Boolean) return Boolean
     with Global => null, Depends => (Poll_Matches'Result => (D, Poll, Pidfd, Terminal)) is
   begin
      return S.Text_Is (D, F (D, Poll, "call"), "poll") and then
        Same (D, F (D, F (D, Poll, "args"), "fd"), F (D, Pidfd, "fd")) and then
        Num (D, F (D, F (D, Poll, "args"), "events"), 25) and then
        Num (D, F (D, F (D, Poll, "args"), "timeout"), 0) and then Num (D, F (D, Poll, "errno"), 0) and then
        (if Terminal then Num (D, F (D, Poll, "result"), 1) and then
           (Num (D, F (D, Poll, "revents"), 1) or else Num (D, F (D, Poll, "revents"), 16) or else
            Num (D, F (D, Poll, "revents"), 17))
         else Num (D, F (D, Poll, "result"), 0) and then Num (D, F (D, Poll, "revents"), 0));
   end Poll_Matches;
   function Text_Number (D : E.Bytes; Text, Number : E.Span) return Boolean
     with Global => null, Depends => (Text_Number'Result => (D, Text, Number)) is
   begin
      if not V.Valid_Text (D, Text) or else not V.Is_Integer (D, Number) then return False; end if;
      declare B : constant E.Bytes := V.Text_Value (D, Text); begin
         return FD_Number (D, Number) and then B'Length > 0 and then
           Decimal (B, B'First, B'Last) >= 0 and then Decimal (B, B'First, B'Last) = R.Number (D, Number);
      end;
   end Text_Number;
   function Argv_Raw (D : E.Bytes; Arguments, Raw : E.Span) return Boolean
     with Global => null, Depends => (Argv_Raw'Result => (D, Arguments, Raw)) is
      Cursor : E.Count := 0;
   begin
      if not V.Is_Sequence (D, Arguments) or else not V.Valid_Bytes (D, Raw) then return False; end if;
      declare B : constant E.Bytes := V.Bytes_Value (D, Raw); begin
         for I in E.Count range 1 .. V.Count (D, Arguments) loop
            declare Item : constant E.Span := V.Element (D, Arguments, I - 1); begin
               if not V.Valid_Text (D, Item) then return False; end if;
               declare A : constant E.Bytes := V.Text_Value (D, Item); begin
                  if Cursor >= B'Length or else A'Length >= B'Length - Cursor then return False; end if;
                  for K in E.Count range 1 .. A'Length loop
                     if A (A'First + K - 1) = 0 or else
                        A (A'First + K - 1) /= B (B'First + Cursor + K - 1) then return False; end if;
                  end loop;
                  Cursor := Cursor + A'Length;
                  if B (B'First + Cursor) /= 0 then return False; end if;
                  Cursor := Cursor + 1;
               end;
            end;
         end loop;
         return Cursor = B'Length;
      end;
   end Argv_Raw;
   function Invocation_Reference (D : E.Bytes; Frame : E.Span) return Boolean
     with Global => null, Depends => (Invocation_Reference'Result => (D, Frame)) is
      A : constant E.Span := F (D, Frame, "actor_argv");
      O : constant E.Span := F (D, Frame, "original_argv");
      Plan : constant E.Span := F (D, Frame, "plan");
      Source : constant E.Span := F (D, Frame, "owner_source");
      Optimize : constant E.Span := F (D, F (D, Source, "interpreter_flags"), "optimize");
      Offset : E.Count := 0;
      Tail : E.Count;
      function At (Args : E.Span; Index : E.Count) return E.Span is
        (V.Element (D, Args, Index));
   begin
      if S.Text_Is (D, Optimize, "1") or else S.Text_Is (D, Optimize, "2") then Offset := 1;
      elsif not S.Text_Is (D, Optimize, "0") then return False; end if;
      if V.Count (D, O) < 7 then return False; end if;
      Tail := V.Count (D, O) - 7;
      return V.Count (D, A) = 15 + Offset and then
        (if Offset = 1 then S.Text_Is (D, At (A, 4), (if S.Text_Is (D, Optimize, "1") then "-O" else "-OO"))) and then
        Argv_Raw (D, A, F (D, Frame, "actor_argv_raw")) and then
        Argv_Raw (D, O, F (D, Frame, "original_argv_raw")) and then
        Hex_Matches (D, F (D, F (D, Frame, "owner"), "cmdline_hex"), F (D, Frame, "original_argv_raw")) and then
        Same (D, At (A, 0), F (D, Source, "interpreter")) and then
        Same (D, At (A, 4 + Offset), F (D, Source, "helper")) and then
        Same (D, At (O, Tail), F (D, Source, "helper")) and then
        S.Text_Is (D, At (A, 1), "-I") and then S.Text_Is (D, At (A, 2), "-S") and then S.Text_Is (D, At (A, 3), "-B") and then
        Boolean_Is (D, F (D, F (D, Source, "bootstrap_flags"), "isolated"), True) and then
        Boolean_Is (D, F (D, F (D, Source, "bootstrap_flags"), "no_site"), True) and then
        Boolean_Is (D, F (D, F (D, Source, "bootstrap_flags"), "dont_write_bytecode"), True) and then
        S.Text_Is (D, At (A, 5 + Offset), "--actor-source-owner") and then
        Text_Number (D, At (A, 6 + Offset), F (D, F (D, Frame, "actor_channel_origin"), "fd")) and then
        Text_Number (D, At (A, 7 + Offset), F (D, F (D, Frame, "projection"), "fd")) and then
        Text_Number (D, At (A, 8 + Offset), F (D, F (D, Frame, "endpoint_parent"), "fd")) and then
        S.Text_Is (D, At (A, 9 + Offset), "--deadline") and then Same (D, At (A, 10 + Offset), F (D, Frame, "deadline_word")) and then
        S.Text_Is (D, At (A, 11 + Offset), "--entry") and then Same (D, At (A, 12 + Offset), F (D, Plan, "entry")) and then
        S.Text_Is (D, At (A, 13 + Offset), "--request") and then Same (D, At (A, 14 + Offset), F (D, Plan, "request")) and then
        S.Text_Is (D, At (O, Tail + 1), "--bootstrap-envelope") and then
        Same (D, At (O, Tail + 2), F (D, Source, "envelope_path")) and then
        S.Text_Is (D, At (O, Tail + 3), "--entry") and then Same (D, At (O, Tail + 4), F (D, Plan, "entry")) and then
        S.Text_Is (D, At (O, Tail + 5), "--request") and then Same (D, At (O, Tail + 6), F (D, Plan, "request")) and then
        P.Joined_Path (D, F (D, Frame, "plan_path"), F (D, Plan, "request"), ".source-owner.json");
   end Invocation_Reference;
   function Hex_Number (B : E.Bytes; Start, Length : E.Count) return Valid_Big_Integer
     with Global => null, Depends => (Hex_Number'Result => (B, Start, Length)) is
      N : Valid_Big_Integer := 0;
      Digit : Integer;
   begin
      if Length = 0 or else Start > B'Length or else Length > B'Length - Start then return -1; end if;
      for I in E.Count range 1 .. Length loop
         declare Byte : constant Natural := Natural (B (B'First + Start + I - 1)); begin
            if Byte in Character'Pos ('0') .. Character'Pos ('9') then Digit := Integer (Byte) - Character'Pos ('0');
            elsif Byte in Character'Pos ('a') .. Character'Pos ('f') then Digit := Integer (Byte) - Character'Pos ('a') + 10;
            else return -1; end if;
            N := N * 16 + To_Big_Integer (Digit);
         end;
      end loop;
      return N;
   end Hex_Number;
   function Map_Line (D : E.Bytes; Frame, Image, Row : E.Span) return Boolean
     with Global => null, Depends => (Map_Line'Result => (D, Frame, Image, Row)) is
      Raw : constant E.Span := F (D, Row, "proc_raw");
      Encoded : constant E.Span := F (D, F (D, Frame, "owner_current"), "maps_hex");
   begin
      if not V.Valid_Bytes (D, Raw) or else not V.Valid_Hex_Field (D, Encoded, "value") or else
         not V.Valid_Text (D, F (D, Row, "bounds")) or else
         not V.Valid_Text (D, F (D, Row, "permissions")) or else
         not V.Valid_Text (D, F (D, Image, "path")) then return False; end if;
      declare B : constant E.Bytes := V.Bytes_Value (D, Raw);
              Maps : constant E.Bytes := V.Hex_Value (D, Encoded, "value");
              Bounds : constant E.Bytes := V.Text_Value (D, F (D, Row, "bounds"));
              Modes : constant E.Bytes := V.Text_Value (D, F (D, Row, "permissions"));
              Path : constant E.Bytes := V.Text_Value (D, F (D, Image, "path"));
              Seen : E.Count := 0; begin
         if B'Length = 0 or else B (B'Last) /= 10 or else Bounds'Length >= B'Length or else
            Modes'Length >= B'Length - Bounds'Length or else
            Path'Length >= B'Length or else B'Length > Maps'Length then return False; end if;
         for I in E.Count range 1 .. Bounds'Length loop
            if B (B'First + I - 1) /= Bounds (Bounds'First + I - 1) then return False; end if;
         end loop;
         if B (B'First + Bounds'Length) /= 32 then return False; end if;
         for I in E.Count range 1 .. Modes'Length loop
            if B (B'First + Bounds'Length + I) /= Modes (Modes'First + I - 1) then return False; end if;
         end loop;
         if Bounds'Length + Modes'Length + 1 >= B'Length or else
            B (B'First + Bounds'Length + Modes'Length + 1) /= 32 then return False; end if;
         for I in E.Count range 1 .. Path'Length loop
            if B (B'Last - Path'Length + I - 1) /= Path (Path'First + I - 1) then return False; end if;
         end loop;
         declare
            type Token_Array is array (1 .. 5) of E.Span;
            Tokens : Token_Array := (others => (1, 0));
            Cursor, Colon : E.Count := B'First;
            Offset, Major, Minor, Inode : Valid_Big_Integer;
         begin
            for T in Tokens'Range loop
               while Cursor < B'Last and then B (Cursor) = 32 loop Cursor := Cursor + 1; end loop;
               Tokens (T).First := Cursor;
               while Cursor < B'Last and then B (Cursor) /= 32 loop Cursor := Cursor + 1; end loop;
               Tokens (T).Length := Cursor - Tokens (T).First;
               if Tokens (T).Length = 0 or else Cursor = B'Last then return False; end if;
            end loop;
            Colon := 0;
            for I in E.Count range 1 .. Tokens (4).Length loop
               if B (Tokens (4).First + I - 1) = Character'Pos (':') then
                  if Colon /= 0 then return False; end if; Colon := I;
               end if;
            end loop;
            if Colon <= 1 or else Colon >= Tokens (4).Length then return False; end if;
            Offset := Hex_Number (B, Tokens (3).First - B'First, Tokens (3).Length);
            Major := Hex_Number (B, Tokens (4).First - B'First, Colon - 1);
            Minor := Hex_Number (B, Tokens (4).First - B'First + Colon, Tokens (4).Length - Colon);
            Inode := Decimal (B, Tokens (5).First, Tokens (5).First + Tokens (5).Length - 1);
            if Offset < 0 or else Major < 0 or else Minor < 0 or else Inode < 0 or else
               not V.Is_Integer (D, F (D, Row, "offset")) or else Offset /= R.Number (D, F (D, Row, "offset")) or else
               not V.Is_Integer (D, F (D, Row, "device_major")) or else Major /= R.Number (D, F (D, Row, "device_major")) or else
               not V.Is_Integer (D, F (D, Row, "device_minor")) or else Minor /= R.Number (D, F (D, Row, "device_minor")) or else
               not V.Is_Integer (D, F (D, Row, "inode")) or else Inode /= R.Number (D, F (D, Row, "inode")) or else
               Inode /= R.Number (D, F (D, F (D, Row, "identity"), "inode")) or else
               (Major mod 4096) * 256 + (Minor mod 256) + (Minor / 256) * 1_048_576 +
                 (Major / 4096) * 17_592_186_044_416 /= R.Number (D, F (D, F (D, Row, "identity"), "device"))
            then return False; end if;
         end;
         for Start in E.Count range 0 .. Maps'Length - B'Length loop
            if (Start = 0 or else Maps (Maps'First + Start - 1) = 10) and then
              (for all I in E.Count range 1 .. B'Length =>
                 Maps (Maps'First + Start + I - 1) = B (B'First + I - 1)) then Seen := Seen + 1; end if;
         end loop;
         return Seen = 1;
      end;
   end Map_Line;
   function Mapped_Reference (D : E.Bytes; Frame : E.Span) return Boolean
     with Global => null, Depends => (Mapped_Reference'Result => (D, Frame)) is
      Image : constant E.Span := F (D, Frame, "native_mapping");
      Source : constant E.Span := F (D, Frame, "owner_source");
      Maps : constant E.Span := F (D, Image, "maps");
      Symbol : constant E.Span := F (D, Image, "symbol");
      Executable : Boolean := False;
   begin
      if not Same (D, F (D, Image, "path"), F (D, F (D, F (D, Frame, "installation"), "runtime"), "native_library")) or else
         not C.Image_Corresponds (D, Source, F (D, Image, "path"), F (D, Image, "raw")) or else
         not C.File_Identity_Corresponds (D, Source, F (D, Image, "path"), F (D, Image, "named")) or else
         not V.Is_Integer (D, Symbol) or else R.Number (D, Symbol) <= 0 or else
         not V.Is_Sequence (D, Maps) or else V.Count (D, Maps) = 0 then return False; end if;
      for I in E.Count range 1 .. V.Count (D, Maps) loop
         declare Row : constant E.Span := V.Element (D, Maps, I - 1);
                 Bounds : constant E.Span := F (D, Row, "bounds");
                 Permissions : constant E.Span := F (D, Row, "permissions"); begin
            if not Map_Line (D, Frame, Image, Row) then return False; end if;
            if not Identity (D, F (D, Row, "identity"), F (D, Image, "named")) or else
               not C.File_Identity_Corresponds (D, Source, F (D, Image, "path"), F (D, Row, "identity")) or else
               not Same (D, F (D, Row, "raw"), F (D, Image, "raw")) or else
               not V.Valid_Text (D, Bounds) or else not V.Valid_Text (D, Permissions) then return False; end if;
            declare B : constant E.Bytes := V.Text_Value (D, Bounds);
                    Modes : constant E.Bytes := V.Text_Value (D, Permissions);
                    Dash : E.Count := 0;
                    First, Last : Valid_Big_Integer; begin
               for K in E.Count range 1 .. B'Length loop
                  if B (B'First + K - 1) = Character'Pos ('-') then
                     if Dash /= 0 then return False; end if; Dash := K;
                  end if;
               end loop;
               if Dash = 0 then return False; end if;
               First := Hex_Number (B, 0, Dash - 1); Last := Hex_Number (B, Dash, B'Length - Dash);
               if First < 0 or else Last <= First or else Modes'Length /= 4 then return False; end if;
               if Modes (Modes'First + 2) = Character'Pos ('x') and then
                  First <= R.Number (D, Symbol) and then R.Number (D, Symbol) < Last then Executable := True; end if;
            end;
         end;
      end loop;
      return Executable;
   end Mapped_Reference;
   function Owner_Reference (D : E.Bytes; Frame, Current, Source, Status, Raw_Stat : E.Span) return Boolean
     with Global => null, Depends => (Owner_Reference'Result => (D, Frame, Current, Source, Status, Raw_Stat)) is
      Original : constant E.Span := F (D, Frame, "owner");
      Owner_Pid : constant E.Span := F (D, Original, "pid");
   begin
      if not V.Is_Integer (D, Owner_Pid) or else R.Number (D, Owner_Pid) <= 0 or else
         not Process_Reference (D, Original, F (D, Frame, "owner_origin_stat")) or else
         not Process_Reference (D, Current, Raw_Stat) or else
         not Same (D, Owner_Pid, F (D, Current, "pid")) or else
         not Same (D, F (D, Original, "start_tick"), F (D, Current, "start_tick")) or else
         not Same (D, F (D, Original, "boot_hex"), F (D, Current, "boot_hex")) or else
         not Same (D, F (D, Original, "namespaces"), F (D, Current, "namespaces")) or else
         not Same (D, F (D, Original, "uid_map_hex"), F (D, Current, "uid_map_hex")) or else
         not Same (D, F (D, Original, "gid_map_hex"), F (D, Current, "gid_map_hex")) or else
         not Same (D, F (D, Current, "exe"), F (D, Source, "interpreter")) or else
         not Hex_Matches (D, F (D, Current, "cmdline_hex"), F (D, Frame, "original_argv_raw")) or else
         not Hex_Matches (D, F (D, Current, "status_hex"), Status) or else
         V.Count (D, F (D, Current, "kernel_uid")) /= 4 or else V.Count (D, F (D, Current, "kernel_gid")) /= 4 or else
         not Num (D, V.Element (D, F (D, Current, "kernel_uid"), 1), 0) or else
         not Same (D, F (D, Current, "real_uid"), V.Element (D, F (D, Current, "kernel_uid"), 0)) or else
         not Same (D, F (D, Current, "real_gid"), V.Element (D, F (D, Current, "kernel_gid"), 0)) or else
         not Same (D, F (D, Current, "resuid"), F (D, Original, "resuid")) or else
         not Same (D, F (D, Current, "resgid"), F (D, Original, "resgid")) or else
         not C.Corresponds (D, Source, F (D, Frame, "installation")) or else
         not C.Readbacks_Correspond (D, Source) or else
         not Status_Columns (D, Status, F (D, Current, "kernel_uid"), "Uid:", False) or else
         not Status_Columns (D, Status, F (D, Current, "kernel_gid"), "Gid:", False) or else
         not Status_Columns (D, Status, F (D, Current, "groups"), "Groups:", False) then return False; end if;
      for I in E.Count range 0 .. 2 loop
         if not Same (D, V.Element (D, F (D, Current, "resuid"), I), V.Element (D, F (D, Current, "kernel_uid"), I)) or else
            not Same (D, V.Element (D, F (D, Current, "resgid"), I), V.Element (D, F (D, Current, "kernel_gid"), I))
         then return False; end if;
      end loop;
      return True;
   end Owner_Reference;
   function Receipt_Source (D : E.Bytes; Frame, Source : E.Span) return Boolean
     with Global => null, Depends => (Receipt_Source'Result => (D, Frame, Source)) is
     (C.Corresponds (D, Source, F (D, Frame, "installation")) and then C.Readbacks_Correspond (D, Source) and then
      Same (D, F (D, Source, "envelope_bytes_hex"), F (D, F (D, Frame, "owner_source"), "envelope_bytes_hex")));
   function Creator_Reference (D : E.Bytes; Frame : E.Span) return Boolean
     with Global => null, Depends => (Creator_Reference'Result => (D, Frame)) is
      Capture : constant E.Span := F (D, Frame, "owner_channel_capture");
      Source : constant E.Span := F (D, Capture, "source");
      FD : constant E.Span := F (D, Capture, "fd");
      Owner : constant E.Span := F (D, Frame, "owner");
      Peer : constant E.Span := F (D, F (D, Capture, "peercred"), "raw");
      Held : constant E.Span := F (D, Capture, "fstat");
   begin
      if not FD_Number (D, FD) or else
         not S.Text_Is (D, F (D, Held, "call"), "fstat") or else
         not Same (D, F (D, Held, "fd"), FD) or else
         not Same (D, F (D, F (D, Held, "args"), "fd"), FD) or else
         not Num (D, F (D, Held, "result"), 0) or else not Num (D, F (D, Held, "errno"), 0) or else
         not Same (D, F (D, Held, "source"), Source) or else
         not Receipt_Source (D, Frame, Source) or else
         not Same (D, Peer, F (D, F (D, Frame, "owner_channel"), "peer")) or else
         not J.SCM_Credentials_Match (D, Peer, F (D, Owner, "pid"), F (D, Owner, "real_uid"), F (D, Owner, "real_gid")) or else
         not Identity (D, F (D, F (D, Capture, "fstat"), "identity"), F (D, F (D, Frame, "owner_channel"), "identity")) or else
         not V.Is_Integer (D, F (D, F (D, F (D, Capture, "fstat"), "identity"), "mode")) or else
         R.Number (D, F (D, F (D, F (D, Capture, "fstat"), "identity"), "mode")) / 4096 /= 12 or else
         not C.Corresponds (D, Source, F (D, Frame, "installation")) or else not C.Readbacks_Correspond (D, Source)
      then return False; end if;
      for I in 1 .. 3 loop
         declare Receipt : constant E.Span := F (D, Capture, (case I is when 1 => "domain", when 2 => "type", when others => "peercred")); begin
            if not S.Text_Is (D, F (D, Receipt, "call"), "getsockopt") or else
               not Same (D, F (D, Receipt, "fd"), FD) or else not Same (D, F (D, Receipt, "source"), Source) or else
               not Num (D, F (D, Receipt, "result"), 0) or else not Num (D, F (D, Receipt, "errno"), 0) or else
               not Num (D, F (D, Receipt, "level"), 1) or else
               not Num (D, F (D, Receipt, "option"), (if I = 1 then 39 elsif I = 2 then 3 else 17)) or else
               not Num (D, F (D, Receipt, "requested"), (if I = 3 then 12 else 4)) or else
               not Num (D, F (D, Receipt, "length"), (if I = 3 then 12 else 4))
            then return False; end if;
            if I < 3 and then (not V.Valid_Bytes (D, F (D, Receipt, "raw")) or else
              V.Bytes_Value (D, F (D, Receipt, "raw")) /= E.Bytes'(1, 0, 0, 0)) then return False; end if;
         end;
      end loop;
      return True;
   end Creator_Reference;
   function Receive_Reference
     (D : E.Bytes; Frame, Receipt, Descriptor, Pid, Uid, Gid, Source : E.Span) return Boolean
     with Global => null, Depends => (Receive_Reference'Result => (D, Frame, Receipt, Descriptor, Pid, Uid, Gid, Source)) is
      Args : constant E.Span := F (D, Receipt, "args");
      Controls : constant E.Span := F (D, Receipt, "controls");
      Rights : constant E.Span := F (D, Args, "rights");
      Rights_Count, Credential_Count : E.Count := 0;
   begin
      if not S.Text_Is (D, F (D, Receipt, "call"), "recvmsg") or else
         not Descriptor_Reference (D, Descriptor) or else
         not FD_Number (D, F (D, Receipt, "fd")) or else
         not Same (D, F (D, Receipt, "fd"), F (D, F (D, Frame, "owner_channel_capture"), "fd")) or else
         not Receipt_Source (D, Frame, Source) or else
         not Num (D, F (D, Receipt, "result"), 1) or else not Num (D, F (D, Receipt, "errno"), 0) or else
         not Num (D, F (D, Receipt, "input_flags"), 1_073_741_824) or else
         not Num (D, F (D, Args, "flags"), 1_073_741_824) or else
         not (Num (D, F (D, Receipt, "flags"), 0) or else Num (D, F (D, Receipt, "flags"), 1_073_741_824)) or else
         not Same (D, F (D, Receipt, "flags"), F (D, Receipt, "msg_flags")) or else
         not Same (D, F (D, Receipt, "sender"), F (D, Receipt, "sender_credentials")) or else
         not Same (D, F (D, Receipt, "source"), Source) or else
         not Identity (D, F (D, Args, "channel"), F (D, F (D, Frame, "owner_channel"), "identity")) or else
         not Same (D, F (D, Args, "peer"), F (D, F (D, Frame, "owner_channel"), "peer")) or else
         not J.SCM_Credentials_Match (D, F (D, Receipt, "sender"), Pid, Uid, Gid) or else
         not V.Is_Sequence (D, Rights) or else V.Count (D, Rights) /= 1 or else
         not Same (D, V.Element (D, Rights, 0), F (D, Descriptor, "fd")) or else
         not J.Signed_32_Matches (D, F (D, Receipt, "rights"), F (D, Descriptor, "fd")) or else
         not V.Is_Sequence (D, Controls) or else V.Count (D, Controls) /= 2 then return False; end if;
      declare B : constant E.Span := F (D, Receipt, "frame"); begin
         if not V.Valid_Bytes (D, B) then return False; end if;
         declare Raw : constant E.Bytes := V.Bytes_Value (D, B); begin
            if Raw'Length /= 1 or else Raw (Raw'First) /= Character'Pos ('F') then return False; end if;
         end;
         if not Same (D, B, F (D, Args, "body")) then return False; end if;
      end;
      for I in E.Count range 1 .. V.Count (D, Controls) loop
         declare Control : constant E.Span := V.Element (D, Controls, I - 1); begin
            if V.Count (D, Control) /= 3 or else not Num (D, V.Element (D, Control, 0), 1) then return False; end if;
            if Num (D, V.Element (D, Control, 1), 1) then
               Rights_Count := Rights_Count + 1;
               if not Same (D, V.Element (D, Control, 2), F (D, Receipt, "rights")) then return False; end if;
            elsif Num (D, V.Element (D, Control, 1), 2) then
               Credential_Count := Credential_Count + 1;
               if not Same (D, V.Element (D, Control, 2), F (D, Receipt, "sender")) then return False; end if;
            else return False;
            end if;
         end;
      end loop;
      return Rights_Count = 1 and then Credential_Count = 1;
   end Receive_Reference;
   function Close_Reference (D : E.Bytes; Frame, Close, Descriptor, Source : E.Span) return Boolean
     with Global => null, Depends => (Close_Reference'Result => (D, Frame, Close, Descriptor, Source)) is
      Readback : constant E.Span := F (D, Close, "readback");
   begin
      return S.Text_Is (D, F (D, Close, "call"), "close") and then
        Descriptor_Reference (D, Descriptor) and then
        Receipt_Source (D, Frame, Source) and then Same (D, F (D, Close, "source"), Source) and then
        Same (D, F (D, Close, "fd"), F (D, Descriptor, "fd")) and then
        Same (D, F (D, F (D, Close, "args"), "fd"), F (D, Descriptor, "fd")) and then
        Num (D, F (D, Close, "result"), 0) and then Num (D, F (D, Close, "errno"), 0) and then
        S.Text_Is (D, F (D, Readback, "call"), "fstat") and then
        Same (D, F (D, Readback, "fd"), F (D, Descriptor, "fd")) and then
        Same (D, F (D, Readback, "source"), Source) and then
        Num (D, F (D, Readback, "result"), -1) and then Num (D, F (D, Readback, "errno"), 9);
   end Close_Reference;
   function Wrapped_Text (D : E.Bytes; Value, Middle : E.Span; Prefix, Suffix : String) return Boolean
     with Global => null, Depends => (Wrapped_Text'Result => (D, Value, Middle, Prefix, Suffix)) is
   begin
      if not V.Valid_Text (D, Value) or else not V.Valid_Text (D, Middle) then return False; end if;
      declare B : constant E.Bytes := V.Text_Value (D, Value);
              M : constant E.Bytes := V.Text_Value (D, Middle);
              Cursor : E.Count := 0;
              function Match (Text : String) return Boolean is
              begin
                 if Cursor > B'Length or else Text'Length > B'Length - Cursor then return False; end if;
                 for I in Text'Range loop
                    if B (B'First + Cursor + E.Count (I - Text'First)) /= Character'Pos (Text (I)) then return False; end if;
                 end loop;
                 Cursor := Cursor + Text'Length; return True;
              end Match;
      begin
         if not Match (Prefix) or else Cursor > B'Length or else M'Length > B'Length - Cursor then return False; end if;
         for I in E.Count range 1 .. M'Length loop
            if B (B'First + Cursor + I - 1) /= M (M'First + I - 1) then return False; end if;
         end loop;
         Cursor := Cursor + M'Length;
         return Match (Suffix) and then Cursor = B'Length;
      end;
   end Wrapped_Text;
   function Peer_Name (D : E.Bytes; Receipt, Descriptor, Endpoint : E.Span) return Boolean
     with Global => null, Depends => (Peer_Name'Result => (D, Receipt, Descriptor, Endpoint)) is
   begin
      if not S.Text_Is (D, F (D, Receipt, "call"), "getpeername") or else
         not Same (D, F (D, Receipt, "fd"), F (D, Descriptor, "fd")) or else
         not Num (D, F (D, Receipt, "result"), 0) or else not Num (D, F (D, Receipt, "errno"), 0) or else
         not V.Valid_Bytes (D, F (D, Receipt, "raw")) or else not V.Valid_Text (D, Endpoint) then return False; end if;
      declare B : constant E.Bytes := V.Bytes_Value (D, F (D, Receipt, "raw"));
              Name : constant E.Bytes := V.Text_Value (D, Endpoint); begin
         if B'Length < 3 or else Name'Length /= B'Length - 3 or else
            B (B'First) /= 1 or else B (B'First + 1) /= 0 or else B (B'Last) /= 0 then return False; end if;
         for I in E.Count range 1 .. Name'Length loop
            if B (B'First + I + 1) /= Name (Name'First + I - 1) then return False; end if;
         end loop;
         return True;
      end;
   end Peer_Name;
   function Target_Reference (D : E.Bytes; Frame : E.Span; Closed : Boolean) return Boolean
     with Global => null, Depends => (Target_Reference'Result => (D, Frame, Closed)) is
      Target : constant E.Span := F (D, Frame, "target");
      Message : constant E.Span := F (D, Target, "message");
      Descriptor : constant E.Span := F (D, Target, "descriptor");
      Capture : constant E.Span := F (D, Target, "capture");
      Actor_Fd : constant E.Span := F (D, Message, "descriptor");
      Request : constant E.Span := F (D, Frame, "request");
      Kcmp : constant E.Span := F (D, Target, "kcmp");
      Owner_Source : constant E.Span := F (D, Capture, "source");
      Rows : constant E.Span := F (D, Frame, "messages");
      Sequence : constant E.Span := F (D, Target, "sequence");
      Sequence_Index : E.Count := 0;
      Optimize : constant E.Span := F (D, F (D, F (D, Frame, "owner_source"), "interpreter_flags"), "optimize");
      Parent_Argument : constant E.Count := (if S.Text_Is (D, Optimize, "0") then 8 else 9);
   begin
      for I in E.Count range 1 .. V.Count (D, Rows) loop
         if J.Unsigned_Is (D, Sequence, I) then Sequence_Index := I; end if;
      end loop;
      if Sequence_Index < 2 or else
         not Same (D, F (D, Message, "original"), F (D, Request, "endpoint")) or else
         not Same (D, F (D, Message, "peername"), F (D, Request, "endpoint")) or else
         not Wrapped_Text (D, F (D, Message, "connected_path"),
           V.Element (D, F (D, Frame, "actor_argv"), Parent_Argument), "/proc/self/fd/", "/intent.sock") or else
         not Peer_Name (D, F (D, Capture, "peername"), Descriptor, F (D, Request, "endpoint")) or else
         not J.Ucred_Matches (D, F (D, F (D, Capture, "peercred"), "raw"), F (D, Target, "peer")) or else
         not Num (D, F (D, Message, "domain"), 1) or else not Num (D, F (D, Message, "type"), 1) or else
         not Identity (D, Actor_Fd, Descriptor) or else
         not Descriptor_Reference (D, Actor_Fd) or else not Descriptor_Reference (D, Descriptor) or else
         R.Number (D, F (D, Actor_Fd, "mode")) / 4096 /= 12 or else
         not Identity (D, Actor_Fd, F (D, Target, "kernel_descriptor")) or else
         not Same (D, F (D, Actor_Fd, "uid"), F (D, Request, "uid")) or else
         not Same (D, F (D, Actor_Fd, "gid"), F (D, Request, "gid")) or else
         not Receive_Reference (D, Frame, F (D, Target, "receive"), Descriptor, F (D, Frame, "child_pid"),
           F (D, Request, "uid"), F (D, Request, "gid"), Owner_Source) or else
         not Same (D, F (D, Capture, "fd"), F (D, Descriptor, "fd")) or else
         not S.Text_Is (D, F (D, F (D, Capture, "fstat"), "call"), "fstat") or else
         not Same (D, F (D, F (D, Capture, "fstat"), "fd"), F (D, Descriptor, "fd")) or else
         not Same (D, F (D, F (D, F (D, Capture, "fstat"), "args"), "fd"), F (D, Descriptor, "fd")) or else
         not Same (D, F (D, F (D, Capture, "fstat"), "source"), Owner_Source) or else
         not Identity (D, F (D, F (D, Capture, "fstat"), "identity"), Descriptor) or else
         not Num (D, F (D, F (D, Capture, "fstat"), "result"), 0) or else
         not Num (D, F (D, F (D, Capture, "fstat"), "errno"), 0) or else
         not S.Text_Is (D, F (D, Kcmp, "call"), "kcmp") or else
         not Same (D, F (D, F (D, Kcmp, "args"), "pid1"), F (D, F (D, Frame, "owner"), "pid")) or else
         not Same (D, F (D, F (D, Kcmp, "args"), "pid2"), F (D, Frame, "child_pid")) or else
         not Num (D, F (D, F (D, Kcmp, "args"), "type"), 0) or else
         not Same (D, F (D, F (D, Kcmp, "args"), "idx1"), F (D, Descriptor, "fd")) or else
         not Same (D, F (D, F (D, Kcmp, "args"), "idx2"), F (D, Actor_Fd, "fd")) or else
         not Num (D, F (D, Kcmp, "result"), 0) or else not Num (D, F (D, Kcmp, "errno"), 0) or else
         not Same (D, F (D, Kcmp, "source"), Owner_Source) or else
         not C.Corresponds (D, Owner_Source, F (D, Frame, "installation")) or else
         not C.Readbacks_Correspond (D, Owner_Source) or else
         (Closed and then not Close_Reference (D, Frame, F (D, Target, "close"), Descriptor, Owner_Source)) then return False; end if;
      declare Index : constant E.Count := Sequence_Index - 1;
              Row : constant E.Span := V.Element (D, Rows, Index);
              Own : constant E.Span := F (D, Row, "message");
              Prior : constant E.Span := F (D, V.Element (D, Rows, Index - 1), "message"); begin
         if not Same (D, F (D, Own, "target"), Message) or else
            not S.Text_Is (D, F (D, Prior, "stage"), "ACTOR") or else
            not Same (D, F (D, Message, "resuid"), F (D, Own, "resuid")) or else
            not Same (D, F (D, Message, "resgid"), F (D, Own, "resgid")) or else
            not Same (D, F (D, Message, "groups"), F (D, Own, "groups")) then return False; end if;
         for I in 1 .. 8 loop
            declare Name : constant String := (case I is when 1 => "pid", when 2 => "start_tick", when 3 => "boot_hex",
                      when 4 => "namespaces", when 5 => "exe", when 6 => "cmdline_hex", when 7 => "uid_map_hex", when others => "gid_map_hex"); begin
               if not Same (D, F (D, F (D, Message, "actor"), Name), F (D, F (D, Own, "actor"), Name)) then return False; end if;
            end;
         end loop;
      end;
      for I in 1 .. 3 loop
         declare Receipt : constant E.Span := F (D, Capture, (if I = 1 then "domain" elsif I = 2 then "type" else "peercred")); begin
            if not S.Text_Is (D, F (D, Receipt, "call"), "getsockopt") or else
               not Same (D, F (D, Receipt, "fd"), F (D, Descriptor, "fd")) or else
               not Num (D, F (D, Receipt, "level"), 1) or else
               not Num (D, F (D, Receipt, "option"), (if I = 1 then 39 elsif I = 2 then 3 else 17)) or else
               not Num (D, F (D, Receipt, "result"), 0) or else not Num (D, F (D, Receipt, "errno"), 0) or else
               not Same (D, F (D, Receipt, "source"), Owner_Source) then return False; end if;
            if I < 3 then
               if not Num (D, F (D, Receipt, "requested"), 4) or else not Num (D, F (D, Receipt, "length"), 4) or else
                  not J.Signed_32_Matches (D, F (D, Receipt, "raw"), F (D, Message, (if I = 1 then "domain" else "type")))
               then return False; end if;
            elsif not Num (D, F (D, Receipt, "requested"), 12) or else not Num (D, F (D, Receipt, "length"), 12) or else
                  not Hex_Matches (D, F (D, Message, "server_credentials_hex"), F (D, Receipt, "raw")) then return False;
            end if;
         end;
      end loop;
      return True;
   end Target_Reference;
   function Pidfd_OFD_Reference (D : E.Bytes; Frame, OFD : E.Span) return Boolean
     with Global => null, Depends => (Pidfd_OFD_Reference'Result => (D, Frame, OFD)) is
      Origin : constant E.Span := F (D, Frame, "pidfd");
      Duplicate : constant E.Span := F (D, Frame, "pidfd_duplicate");
      Call : constant E.Span := F (D, OFD, "kcmp");
      Args : constant E.Span := F (D, Call, "args");
      Dup : constant E.Span := F (D, Frame, "pidfd_dup");
   begin
      return Descriptor_Reference (D, Origin) and then Descriptor_Reference (D, Duplicate) and then
        not Same (D, F (D, Origin, "fd"), F (D, Duplicate, "fd")) and then
        Same (D, F (D, OFD, "origin"), Origin) and then Same (D, F (D, OFD, "duplicate_origin"), Duplicate) and then
        Descriptor_Reference (D, F (D, OFD, "current")) and then
        Descriptor_Reference (D, F (D, OFD, "duplicate_current")) and then
        Identity (D, Origin, F (D, OFD, "current")) and then Identity (D, Duplicate, F (D, OFD, "duplicate_current")) and then
        Same (D, F (D, F (D, OFD, "current"), "fd"), F (D, Origin, "fd")) and then
        Same (D, F (D, F (D, OFD, "duplicate_current"), "fd"), F (D, Duplicate, "fd")) and then
        S.Text_Is (D, F (D, Dup, "call"), "dup") and then
        Same (D, F (D, F (D, Dup, "args"), "fd"), F (D, Origin, "fd")) and then
        Same (D, F (D, Dup, "result"), F (D, Duplicate, "fd")) and then Num (D, F (D, Dup, "errno"), 0) and then
        Receipt_Source (D, Frame, F (D, Dup, "source")) and then
        S.Text_Is (D, F (D, Call, "call"), "kcmp") and then Num (D, F (D, Args, "type"), 0) and then
        Same (D, F (D, Args, "pid1"), F (D, F (D, Frame, "owner"), "pid")) and then
        Same (D, F (D, Args, "pid2"), F (D, F (D, Frame, "owner"), "pid")) and then
        Same (D, F (D, Args, "idx1"), F (D, Origin, "fd")) and then
        Same (D, F (D, Args, "idx2"), F (D, Duplicate, "fd")) and then
        Num (D, F (D, Call, "result"), 0) and then Num (D, F (D, Call, "errno"), 0) and then
        Same (D, F (D, Call, "source"), F (D, OFD, "source")) and then
        Receipt_Source (D, Frame, F (D, OFD, "source"));
   end Pidfd_OFD_Reference;
   function Dead_Pidfd_Info (D : E.Bytes; Raw : E.Span) return Boolean
     with Global => null, Depends => (Dead_Pidfd_Info'Result => (D, Raw)) is
      Seen : Natural := 0;
      Word : constant String := "Pid:" & Character'Val (9) & "-1";
   begin
      if not V.Valid_Bytes (D, Raw) then return False; end if;
      declare B : constant E.Bytes := V.Bytes_Value (D, Raw); First : E.Count := B'First; begin
         for Last in B'Range loop
            if B (Last) = 10 then
               if Last - First >= 4 and then
                 (for all I in 1 .. 4 => B (First + E.Count (I - 1)) = Character'Pos (Word (I))) then
                  if Last - First /= Word'Length or else
                    not (for all I in Word'Range => B (First + E.Count (I - Word'First)) = Character'Pos (Word (I)))
                  then return False; end if;
                  if Seen /= 0 then return False; end if; Seen := 1;
               end if;
               if Last < B'Last then First := Last + 1; end if;
            end if;
         end loop;
         return Seen = 1 and then B'Length > 0 and then B (B'Last) = 10;
      end;
   end Dead_Pidfd_Info;
   function Terminal_Reference (D : E.Bytes; Frame, Terminal : E.Span) return Boolean
     with Global => null, Depends => (Terminal_Reference'Result => (D, Frame, Terminal)) is
      Wait : constant E.Span := F (D, Terminal, "waitid_receipt");
      Before : constant E.Span := F (D, Wait, "before_reap");
      Pidfd : constant E.Span := F (D, Frame, "pidfd");
      Child : constant E.Span := F (D, Frame, "child_pid");
   begin
      if V.Count (D, F (D, Frame, "messages")) = 0 then return False; end if;
      declare Reap : constant E.Span := F (D, Terminal, "reap");
              Last : constant E.Span := F (D, V.Element (D, F (D, Frame, "messages"),
                V.Count (D, F (D, Frame, "messages")) - 1), "message"); begin
         return S.Text_Is (D, F (D, Wait, "call"), "waitid") and then
           Num (D, F (D, F (D, Wait, "args"), "idtype"), 3) and then
           Same (D, F (D, F (D, Wait, "args"), "id"), F (D, Pidfd, "fd")) and then
           Num (D, F (D, F (D, Wait, "args"), "options"), 16_777_220) and then
           Num (D, F (D, Wait, "result"), 0) and then Num (D, F (D, Wait, "errno"), 0) and then
           Same (D, F (D, Wait, "api_result"), F (D, Terminal, "waitid")) and then
           Receipt_Source (D, Frame, F (D, Wait, "source")) and then
           Same (D, F (D, Before, "source"), F (D, Wait, "source")) and then
           Pidfd_OFD_Reference (D, Frame, F (D, Before, "ofd")) and then
           Descriptor_Reference (D, F (D, Before, "pidfd")) and then
           Identity (D, F (D, Before, "pidfd"), Pidfd) and then
           Same (D, F (D, F (D, Before, "pidfd"), "fd"), F (D, Pidfd, "fd")) and then
           R.Pidfd_Pid (D, F (D, F (D, Before, "pidfd"), "fdinfo")) = R.Number (D, Child) and then
           Process_Reference (D, F (D, Before, "kernel"), F (D, Before, "kernel_stat")) and then
           Same (D, F (D, F (D, Before, "kernel"), "pid"), Child) and then
           Same (D, F (D, F (D, Before, "kernel"), "start_tick"), F (D, F (D, Last, "actor"), "start_tick")) and then
           Status_Columns (D, F (D, Before, "kernel_status"), F (D, F (D, Frame, "request"), "uid"), "Uid:", True, 4) and then
           Status_Columns (D, F (D, Before, "kernel_status"), F (D, F (D, Frame, "request"), "gid"), "Gid:", True, 4) and then
           S.Text_Is (D, F (D, Reap, "call"), "waitpid") and then
           Same (D, F (D, F (D, Reap, "args"), "pid"), Child) and then
           Num (D, F (D, F (D, Reap, "args"), "options"), 0) and then
           Same (D, F (D, Reap, "result"), Child) and then Num (D, F (D, Reap, "errno"), 0) and then
           V.Count (D, F (D, Reap, "api_result")) = 2 and then
           Same (D, V.Element (D, F (D, Reap, "api_result"), 0), Child) and then
           Num (D, V.Element (D, F (D, Reap, "api_result"), 1), 0) and then
           Receipt_Source (D, Frame, F (D, Reap, "source")) and then
           Pidfd_OFD_Reference (D, Frame, F (D, Terminal, "post_reap_ofd")) and then
           Dead_Pidfd_Info (D, F (D, F (D, Terminal, "pidfd_current"), "fdinfo"));
      end;
   end Terminal_Reference;
   function FD_Path (D : E.Bytes; Raw, FD : E.Span) return Boolean
     with Global => null, Depends => (FD_Path'Result => (D, Raw, FD)) is
      Prefix : constant String := "/proc/self/fd/";
   begin
      if not V.Valid_Bytes (D, Raw) or else not FD_Number (D, FD) then return False; end if;
      declare B : constant E.Bytes := V.Bytes_Value (D, Raw); begin
         return B'Length > Prefix'Length and then
           (for all I in Prefix'Range => B (B'First + E.Count (I - Prefix'First)) = Character'Pos (Prefix (I))) and then
           Decimal (B, B'First + Prefix'Length, B'Last) = R.Number (D, FD);
      end;
   end FD_Path;
   function Word_32 (B : E.Bytes; At : E.Count) return Valid_Big_Integer
     with Global => null, Depends => (Word_32'Result => (B, At)) is
      N : Valid_Big_Integer := 0;
   begin
      if At not in B'Range or else B'Last - At < 3 then return -1; end if;
      for I in reverse Natural range 0 .. 3 loop
         N := N * 256 + To_Big_Integer (Integer (B (At + E.Count (I))));
      end loop;
      return N;
   end Word_32;
   function Watch_Reference (D : E.Bytes; Frame, Terminal : E.Span) return Boolean
     with Global => null, Depends => (Watch_Reference'Result => (D, Frame, Terminal)) is
      Origin : constant E.Span := F (D, Frame, "output_watch_origin");
      Descriptor : constant E.Span := F (D, Origin, "descriptor");
      Parts : constant E.Span := F (D, Terminal, "watch_parts");
      Seen : Boolean := False;
   begin
      if not S.Text_Is (D, F (D, Origin, "call"), "inotify_init1") or else
        not Num (D, F (D, F (D, Origin, "args"), "flags"), 526_336) or else
        not Descriptor_Reference (D, Descriptor) or else
        not Same (D, F (D, Origin, "result"), F (D, Descriptor, "fd")) or else
        not Num (D, F (D, Origin, "errno"), 0) or else
        not Receipt_Source (D, Frame, F (D, Origin, "source")) or else
        not V.Is_Sequence (D, Parts) or else V.Count (D, Parts) = 0 then return False; end if;
      for I in 1 .. 2 loop
         declare Stream : constant E.Span := F (D, F (D, Frame, "output_origins"), (if I = 1 then "stdout" else "stderr"));
                 Watch : constant E.Span := F (D, Stream, "watch"); begin
            if not S.Text_Is (D, F (D, Watch, "call"), "inotify_add_watch") or else
               not Same (D, F (D, Watch, "fd"), F (D, Descriptor, "fd")) or else
               not Identity (D, F (D, Watch, "descriptor"), Descriptor) or else
               not FD_Number (D, F (D, Watch, "result")) or else
               not Num (D, F (D, Watch, "mask"), 3_082) or else not Num (D, F (D, Watch, "errno"), 0) or else
               not Descriptor_Reference (D, F (D, Stream, "reader_origin")) or else
               not Identity (D, F (D, Stream, "reader_origin"), F (D, Stream, "origin")) or else
               not FD_Path (D, F (D, Watch, "path"), F (D, F (D, Stream, "reader_origin"), "fd")) or else
               not Receipt_Source (D, Frame, F (D, Watch, "source")) then return False; end if;
         end;
      end loop;
      for I in E.Count range 1 .. V.Count (D, Parts) loop
         declare Part : constant E.Span := V.Element (D, Parts, I - 1);
                 Raw : constant E.Span := F (D, Part, "raw"); begin
            if not S.Text_Is (D, F (D, Part, "call"), "read") or else
               not Same (D, F (D, F (D, Part, "args"), "fd"), F (D, Descriptor, "fd")) or else
               not Num (D, F (D, F (D, Part, "args"), "count"), 65_536) or else
               not Descriptor_Reference (D, F (D, Part, "descriptor")) or else
               not Identity (D, F (D, Part, "descriptor"), Descriptor) or else
               not Receipt_Source (D, Frame, F (D, Part, "source")) or else not V.Valid_Bytes (D, Raw)
            then return False; end if;
            declare B : constant E.Bytes := V.Bytes_Value (D, Raw); At : E.Count := 0; begin
               if Num (D, F (D, Part, "result"), -1) then
                  if not Num (D, F (D, Part, "errno"), 11) or else B'Length /= 0 then return False; end if;
               else
                  if B'Length = 0 or else not J.Unsigned_Is (D, F (D, Part, "result"), B'Length) or else
                    not Num (D, F (D, Part, "errno"), 0) then return False; end if;
                  while At < B'Length loop
                     if B'Length - At < 16 then return False; end if;
                     declare WD : constant Valid_Big_Integer := Word_32 (B, B'First + At);
                             Mask : constant Valid_Big_Integer := Word_32 (B, B'First + At + 4);
                             Name_Length : constant Valid_Big_Integer := Word_32 (B, B'First + At + 12);
                             Found : Natural := 0; begin
                        if (Mask /= 2 and then Mask /= 8 and then Mask /= 10) or else Name_Length /= 0 then return False; end if;
                        for K in 1 .. 2 loop
                           declare Watch : constant E.Span := F (D, F (D, F (D, Frame, "output_origins"),
                             (if K = 1 then "stdout" else "stderr")), "watch"); begin
                              if WD = R.Number (D, F (D, Watch, "result")) then Found := Found + 1; end if;
                           end;
                        end loop;
                        if Found /= 1 then return False; end if;
                        Seen := True; At := At + 16;
                     end;
                  end loop;
               end if;
            end;
         end;
      end loop;
      return Seen and then Num (D, F (D, V.Element (D, Parts, V.Count (D, Parts) - 1), "result"), -1) and then
        Num (D, F (D, V.Element (D, Parts, V.Count (D, Parts) - 1), "errno"), 11);
   end Watch_Reference;
   function Stream_Reference (D : E.Bytes; Frame, Stream, Origin : E.Span) return Boolean
     with Global => null, Depends => (Stream_Reference'Result => (D, Frame, Stream, Origin)) is
      Parts : constant E.Span := F (D, Stream, "parts");
      Raw : constant E.Span := F (D, Stream, "raw");
      Cursor : E.Count := 0;
   begin
      if not V.Valid_Bytes (D, Raw) or else not V.Is_Sequence (D, Parts) or else V.Count (D, Parts) = 0 or else
         not Num (D, F (D, Stream, "eof"), 0) or else
         not S.Text_Is (D, F (D, F (D, Stream, "fsync"), "call"), "fsync") or else
         not Num (D, F (D, F (D, Stream, "fsync"), "result"), 0) or else
         not Num (D, F (D, F (D, Stream, "fsync"), "errno"), 0) or else
         not Same (D, F (D, F (D, F (D, Stream, "fsync"), "args"), "fd"), F (D, F (D, Origin, "reader_origin"), "fd")) or else
         not Receipt_Source (D, Frame, F (D, F (D, Stream, "fsync"), "source")) or else
         not Same (D, Raw, F (D, Stream, "readback")) or else
         not Descriptor_Reference (D, F (D, Stream, "before")) or else
         not Descriptor_Reference (D, F (D, Stream, "identity")) or else
         not Identity (D, F (D, Stream, "before"), F (D, Stream, "identity")) or else
         not Same (D, F (D, F (D, Stream, "before"), "size"), F (D, F (D, Stream, "identity"), "size")) or else
         not Num (D, F (D, F (D, Origin, "origin"), "uid"), 0) or else
         not Num (D, F (D, F (D, Origin, "origin"), "mode"), 33_152) or else
         not Identity (D, F (D, Stream, "identity"), F (D, Origin, "origin")) or else
         not Close_Reference (D, Frame, F (D, Origin, "writer_close"), F (D, Origin, "origin"),
           F (D, Origin, "writer_close_source")) then return False; end if;
      declare B : constant E.Bytes := V.Bytes_Value (D, Raw); begin
         if V.Count (D, F (D, Stream, "reads")) /= 2 then return False; end if;
         for I in E.Count range 0 .. 1 loop
            declare Read : constant E.Span := V.Element (D, F (D, Stream, "reads"), I); begin
               if not S.Text_Is (D, F (D, Read, "call"), "pread") or else
                  not Same (D, F (D, F (D, Read, "args"), "fd"), F (D, F (D, Origin, "reader_origin"), "fd")) or else
                  not Same (D, F (D, F (D, Read, "args"), "count"), F (D, F (D, Stream, "before"), "size")) or else
                  not Num (D, F (D, F (D, Read, "args"), "offset"), 0) or else
                  not Same (D, F (D, Read, "raw"), Raw) or else
                  not J.Unsigned_Is (D, F (D, Read, "result"), B'Length) or else
                  not Num (D, F (D, Read, "errno"), 0) or else not Receipt_Source (D, Frame, F (D, Read, "source"))
               then return False; end if;
            end;
         end loop;
         if not J.Unsigned_Is (D, F (D, F (D, Stream, "identity"), "size"), B'Length) then return False; end if;
         for I in E.Count range 1 .. V.Count (D, Parts) loop
            declare Part : constant E.Span := V.Element (D, Parts, I - 1);
                    Bytes : constant E.Span := F (D, Part, "raw"); begin
               if not V.Valid_Bytes (D, Bytes) or else not Num (D, F (D, Part, "errno"), 0) then return False; end if;
               if not S.Text_Is (D, F (D, Part, "call"), "read") or else
                  not Same (D, F (D, F (D, Part, "args"), "fd"), F (D, F (D, Origin, "reader_origin"), "fd")) or else
                  not Num (D, F (D, F (D, Part, "args"), "count"), 65_536) or else
                  not Descriptor_Reference (D, F (D, Part, "descriptor")) or else
                  not Identity (D, F (D, Part, "descriptor"), F (D, Origin, "reader_origin")) or else
                  not Receipt_Source (D, Frame, F (D, Part, "source")) then return False; end if;
               declare P : constant E.Bytes := V.Bytes_Value (D, Bytes); begin
                  if not J.Unsigned_Is (D, F (D, Part, "result"), P'Length) or else Cursor > B'Length or else
                     P'Length > B'Length - Cursor then return False; end if;
                  for K in E.Count range 1 .. P'Length loop
                     if P (P'First + K - 1) /= B (B'First + Cursor + K - 1) then return False; end if;
                  end loop;
                  Cursor := Cursor + P'Length;
                  if I = V.Count (D, Parts) and then P'Length /= 0 then return False; end if;
               end;
            end;
         end loop;
         return Cursor = B'Length;
      end;
   end Stream_Reference;
   function Capabilities_Dropped (D : E.Bytes; Frame, Status : E.Span) return Boolean
     with Global => null, Depends => (Capabilities_Dropped'Result => (D, Frame, Status)) is
      Zero : constant E.Span := V.Element (D, F (D, F (D, Frame, "owner_current"), "kernel_uid"), 1);
   begin
      return Num (D, Zero, 0) and then
        Status_Columns (D, Status, Zero, "CapInh:", True, 1) and then
        Status_Columns (D, Status, Zero, "CapPrm:", True, 1) and then
        Status_Columns (D, Status, Zero, "CapEff:", True, 1) and then
        Status_Columns (D, Status, Zero, "CapAmb:", True, 1);
   end Capabilities_Dropped;
   function Traversal_Reference (D : E.Bytes; Parent, Request : E.Span) return Boolean
     with Global => null, Depends => (Traversal_Reference'Result => (D, Parent, Request)) is
      Groups : constant E.Span := F (D, Request, "groups");
      Group : Boolean := Same (D, F (D, Parent, "gid"), F (D, Request, "gid"));
   begin
      if not V.Is_Sequence (D, Groups) or else not V.Is_Integer (D, F (D, Parent, "mode")) then return False; end if;
      for I in E.Count range 1 .. V.Count (D, Groups) loop
         if Same (D, F (D, Parent, "gid"), V.Element (D, Groups, I - 1)) then Group := True; end if;
      end loop;
      declare Mode : constant Valid_Big_Integer := R.Number (D, F (D, Parent, "mode")); begin
         return (if Same (D, F (D, Parent, "uid"), F (D, Request, "uid")) then Bit (Mode, 6)
           elsif Group then Bit (Mode, 3) else Bit (Mode, 0));
      end;
   end Traversal_Reference;
   function Read_Allowed (D : E.Bytes; Identity, Request : E.Span) return Boolean
     with Global => null, Depends => (Read_Allowed'Result => (D, Identity, Request)) is
      Groups : constant E.Span := F (D, Request, "groups");
      Group : Boolean := Same (D, F (D, Identity, "gid"), F (D, Request, "gid"));
   begin
      if not V.Is_Sequence (D, Groups) or else not V.Is_Integer (D, F (D, Identity, "mode")) then return False; end if;
      for I in E.Count range 1 .. V.Count (D, Groups) loop
         if Same (D, F (D, Identity, "gid"), V.Element (D, Groups, I - 1)) then Group := True; end if;
      end loop;
      declare Mode : constant Valid_Big_Integer := R.Number (D, F (D, Identity, "mode")); begin
         return (if Same (D, F (D, Identity, "uid"), F (D, Request, "uid")) then Bit (Mode, 8)
           elsif Group then Bit (Mode, 5) else Bit (Mode, 2));
      end;
   end Read_Allowed;
   function Ancestor_Path (D : E.Bytes; Ancestor, Path : E.Span) return Boolean
     with Global => null, Depends => (Ancestor_Path'Result => (D, Ancestor, Path)) is
   begin
      if not V.Valid_Text (D, Ancestor) or else not V.Valid_Text (D, Path) then return False; end if;
      declare A : constant E.Bytes := V.Text_Value (D, Ancestor);
              P : constant E.Bytes := V.Text_Value (D, Path); begin
         return A'Length > 0 and then A'Length <= P'Length and then A (A'First) = 47 and then
           (for all I in E.Count range 1 .. A'Length => A (A'First + I - 1) = P (P'First + I - 1)) and then
           (A'Length = 1 or else A'Length = P'Length or else P (P'First + A'Length) = 47);
      end;
   end Ancestor_Path;
   function Private_Topology_Reference (D : E.Bytes; Frame, Row, Readback : E.Span) return Boolean
     with Global => null, Depends => (Private_Topology_Reference'Result => (D, Frame, Row, Readback)) is
      Components : constant E.Span := F (D, Row, "components");
      Request : constant E.Span := F (D, Frame, "request");
      Path : constant E.Span := F (D, Row, "path");
      Common, Count : E.Count := 0;
      Denied : Boolean := False;
   begin
      if not Same (D, Path, F (D, Readback, "path")) or else not V.Valid_Text (D, Path) or else
         not V.Is_Sequence (D, Components) or else V.Count (D, Components) = 0 then return False; end if;
      for I in 1 .. 9 loop
         declare Name : constant String := (case I is when 1 => "device", when 2 => "inode",
           when 3 => "mode", when 4 => "uid", when 5 => "gid", when 6 => "nlink", when 7 => "size",
           when 8 => "mtime_ns", when others => "ctime_ns"); begin
            if not Same (D, F (D, F (D, Row, "identity"), Name), F (D, F (D, Readback, "named_after"), Name))
            then return False; end if;
         end;
      end loop;
      declare B : constant E.Bytes := V.Text_Value (D, Path); begin
         if B'Length = 0 or else B (B'First) /= 47 then return False; end if;
         for At in B'Range loop
            if B (At) = 47 then
               if Count >= V.Count (D, Components) then return False; end if;
               declare Component : constant E.Span := V.Element (D, Components, Count);
                       Expected_Length : constant E.Count := (if At = B'First then 1 else At - B'First);
                       Name : constant E.Span := F (D, Component, "path"); begin
                  if not V.Valid_Text (D, Name) or else not Root_Directory (D, F (D, Component, "identity"))
                  then return False; end if;
                  declare Actual : constant E.Bytes := V.Text_Value (D, Name); begin
                     if Actual'Length /= Expected_Length or else
                        not (for all I in E.Count range 1 .. Expected_Length =>
                          Actual (Actual'First + I - 1) = B (B'First + I - 1)) then return False; end if;
                  end;
                  if Ancestor_Path (D, Name, F (D, Frame, "endpoint_parent_path")) then Common := Count + 1; end if;
               end;
               Count := Count + 1;
            end if;
         end loop;
         if Count /= V.Count (D, Components) or else Common = 0 then return False; end if;
      end;
      Denied := not Read_Allowed (D, F (D, Row, "identity"), Request);
      -- An inherited directory capability may bypass ancestors above its
      -- common ancestor with this target. Those ancestors cannot prove denial.
      for I in E.Count range Common .. V.Count (D, Components) loop
         if not Traversal_Reference (D, F (D, V.Element (D, Components, I - 1), "identity"), Request)
         then Denied := True; end if;
      end loop;
      return Denied;
   end Private_Topology_Reference;
   function Private_Source_Reference (D : E.Bytes; Frame : E.Span) return Boolean
     with Global => null, Depends => (Private_Source_Reference'Result => (D, Frame)) is
      Source : constant E.Span := F (D, Frame, "owner_source");
      Readbacks : constant E.Span := F (D, Source, "file_readbacks");
      Rows : constant E.Span := F (D, Frame, "private_source_topology");
      Request : constant E.Span := F (D, Frame, "request");
      Expected : E.Count := 0;
   begin
      if not C.Readbacks_Correspond (D, Source) or else not V.Is_Sequence (D, Rows) or else
         not V.Is_Integer (D, F (D, Request, "uid")) or else R.Number (D, F (D, Request, "uid")) = 0 then return False; end if;
      for I in E.Count range 1 .. V.Count (D, Readbacks) loop
         declare Readback : constant E.Span := V.Element (D, Readbacks, I - 1);
                 Path : constant E.Span := F (D, Readback, "path");
                 Selected : Boolean := Same (D, Path, F (D, F (D, Frame, "plan"), "request"));
                 Found : E.Count := 0; begin
            for K in E.Count range 1 .. V.Count (D, F (D, Request, "requests")) loop
               if Same (D, Path, V.Element (D, F (D, Request, "requests"), K - 1)) then Selected := True; end if;
            end loop;
            if Same (D, Path, F (D, Source, "envelope_path")) or else
              (not Selected and then C.Role_Selected (D, Source, Path, "DATA")) then
               Expected := Expected + 1;
               for K in E.Count range 1 .. V.Count (D, Rows) loop
                  declare Row : constant E.Span := V.Element (D, Rows, K - 1); begin
                     if Same (D, Path, F (D, Row, "path")) then
                        if not Private_Topology_Reference (D, Frame, Row, Readback) then return False; end if;
                        Found := Found + 1;
                     end if;
                  end;
               end loop;
               if Found /= 1 then return False; end if;
            end if;
         end;
      end loop;
      return Expected > 0 and then Expected = V.Count (D, Rows);
   end Private_Source_Reference;
   function Memory_Reference (D : E.Bytes; Frame : E.Span) return Boolean
     with Global => null, Depends => (Memory_Reference'Result => (D, Frame)) is
   begin
      for I in 1 .. 2 loop
         declare Call : constant E.Span := F (D, Frame, (if I = 1 then "owner_memory_set" else "owner_memory_get"));
                 Args : constant E.Span := F (D, Call, "args");
                 Caller : constant E.Span := F (D, Call, "caller"); begin
            if not S.Text_Is (D, F (D, Call, "call"), "prctl") or else
               not Num (D, F (D, Args, "option"), (if I = 1 then 4 else 3)) or else
               not Num (D, F (D, Call, "result"), 0) or else not Num (D, F (D, Call, "errno"), 0) or else
               not Process_Reference (D, Caller, F (D, Call, "caller_stat")) or else
               not Same (D, F (D, Caller, "pid"), F (D, F (D, Frame, "owner"), "pid")) or else
               not Same (D, F (D, Caller, "start_tick"), F (D, F (D, Frame, "owner"), "start_tick")) or else
               not Same (D, F (D, Caller, "namespaces"), F (D, F (D, Frame, "owner"), "namespaces")) or else
               not Receipt_Source (D, Frame, F (D, Call, "source")) then return False; end if;
            for K in 2 .. 5 loop
               declare Name : constant String := (case K is when 2 => "arg2", when 3 => "arg3", when 4 => "arg4", when others => "arg5"); begin
                  if not Num (D, F (D, Args, Name), 0) then return False; end if;
               end;
            end loop;
         end;
      end loop;
      return True;
   end Memory_Reference;
   function Launch_Reference (Data : E.Bytes; Frame : E.Span) return Boolean is
      Plan : constant E.Span := F (Data, Frame, "plan");
      Request : constant E.Span := F (Data, Frame, "request");
      Source : constant E.Span := F (Data, Frame, "owner_source");
      Install : constant E.Span := F (Data, Frame, "installation");
      Projected : constant E.Span := F (Data, Frame, "projected_source");
      Parent : constant E.Span := F (Data, Frame, "endpoint_parent");
      Socket : constant E.Span := F (Data, Frame, "endpoint_named");
      Requests : constant E.Span := F (Data, Frame, "requests");
   begin
      if not S.Valid (Data, Frame) or else
         not S.Text_Is (Data, F (Data, Frame, "schema"), "worldline.fixed-original-client-source-custody-v1") or else
         not S.Text_Is (Data, F (Data, Plan, "schema"), "worldline.fixed-original-client-source-owner-v1") or else
         S.Member_Count (Data, Plan) /= 8 or else S.Member_Count (Data, Request) /= 8 or else
         not JSON_Matches (Data, F (Data, Frame, "plan_raw"), Plan) or else
         not JSON_Matches (Data, F (Data, Frame, "request_raw"), Request) or else
         not JSON_Matches (Data, F (Data, Frame, "descriptor_raw"), Install) or else
         not C.Corresponds (Data, Source, Install) or else
         not Invocation_Reference (Data, Frame) or else
         not Owner_Reference (Data, Frame, F (Data, Frame, "owner_current"), Source,
           F (Data, Frame, "owner_status"), F (Data, Frame, "owner_stat")) or else
         not Mapped_Reference (Data, Frame) or else
         not C.Role_Selected (Data, Source, F (Data, Source, "helper"), "HELPER") or else
         not C.Role_Selected (Data, Source, F (Data, Plan, "entry"), "ENTRY") or else
         not JSON_Matches (Data, F (Data, Frame, "deadline_raw"), F (Data, Frame, "deadline")) or else
         not V.Is_Integer (Data, F (Data, Frame, "deadline_ns")) or else
         not V.Is_Integer (Data, F (Data, Frame, "observed_at_ns")) or else
         R.Number (Data, F (Data, Frame, "observed_at_ns")) > R.Number (Data, F (Data, Frame, "deadline_ns")) or else
         not Projection_Reference (Data, F (Data, Frame, "projection_readback"), F (Data, Frame, "projection"), Projected) or else
         not Projection_Reference (Data, F (Data, Frame, "projection_current_readback"), F (Data, Frame, "projection"), Projected) or else
         not Creator_Reference (Data, Frame) or else
         not Private_Source_Reference (Data, Frame) or else
         not Memory_Reference (Data, Frame) or else
         not Descriptor_Reference (Data, Parent) or else
         not FD_Number (Data, F (Data, F (Data, Frame, "actor_channel_origin"), "fd")) or else
         not Identity (Data, Parent, F (Data, Frame, "endpoint_parent_current")) or else
         not Identity (Data, Parent, F (Data, Frame, "endpoint_held_current")) or else
         not Identity (Data, Socket, F (Data, Frame, "endpoint_current")) or else
         V.Count (Data, F (Data, Plan, "import_roots")) /= 1 or else
         not P.Joined_Path (Data, V.Element (Data, F (Data, Plan, "import_roots"), 0),
           F (Data, F (Data, Install, "runtime"), "worldline_source"), "/runtime") or else
         not C.File_Corresponds (Data, Source, F (Data, Frame, "plan_path"), F (Data, Frame, "plan_raw")) or else
         not C.File_Corresponds (Data, Source, F (Data, Plan, "request"), F (Data, Frame, "request_raw")) or else
         not C.File_Corresponds (Data, Source, F (Data, Plan, "descriptor"), F (Data, Frame, "descriptor_raw")) or else
         not C.Projection_Corresponds (Data, Source, Projected, F (Data, Plan, "actor_closure"),
           Request, F (Data, Plan, "request"), F (Data, Plan, "entry")) or else
         not C.File_Corresponds (Data, Projected, F (Data, Plan, "request"), F (Data, Frame, "request_raw")) or else
         not S.Text_Is (Data, F (Data, Request, "schema"), "worldline.original-custody-client-v1") or else
         not Same (Data, F (Data, Request, "endpoint"), F (Data, F (Data, Install, "endpoint"), "path")) or else
         not Same (Data, F (Data, Request, "uid"), F (Data, F (Data, Install, "endpoint"), "requester_uid")) or else
         not Same (Data, F (Data, Request, "gid"), F (Data, F (Data, Install, "endpoint"), "requester_gid")) or else
         not P.Joined_Path (Data, F (Data, Request, "endpoint"), F (Data, F (Data, Install, "paths"), "authority_root"),
           "/authority/protected-runtime/intent.sock") or else
         not P.Joined_Path (Data, F (Data, Frame, "endpoint_parent_path"),
           F (Data, F (Data, Install, "paths"), "authority_root"), "/authority/protected-runtime") or else
         not Root_Directory (Data, Parent) or else
         not Traversal_Reference (Data, Parent, Request) or else
         not Identity (Data, Parent, F (Data, Frame, "endpoint_parent_named")) or else
         not V.Is_Integer (Data, F (Data, Socket, "mode")) or else
         R.Number (Data, F (Data, Socket, "mode")) /= 49_152 + 432 or else
         not Num (Data, F (Data, Socket, "uid"), 0) or else
         not Same (Data, F (Data, Socket, "gid"), F (Data, Request, "gid")) or else
         not V.Is_Sequence (Data, Requests) or else V.Count (Data, Requests) = 0 or else
         V.Count (Data, Requests) /= V.Count (Data, F (Data, Request, "requests")) then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Requests) loop
         declare Row : constant E.Span := V.Element (Data, Requests, I - 1);
                 Path : constant E.Span := V.Element (Data, F (Data, Request, "requests"), I - 1);
                 Raw : constant E.Span := F (Data, Row, "raw"); begin
            if not Same (Data, F (Data, Row, "path"), Path) or else not V.Valid_Bytes (Data, Raw) or else
               not C.File_Corresponds (Data, Source, Path, Raw) or else not C.File_Corresponds (Data, Projected, Path, Raw)
            then return False; end if;
            declare B : constant E.Bytes := V.Bytes_Value (Data, Raw);
                    Lines : E.Count := 0; begin
               for Byte of B loop if Byte = 10 then Lines := Lines + 1; end if; end loop;
               if B'Length = 0 or else B (B'Last) /= 10 or else Lines /= 1 then return False; end if;
            end;
         end;
      end loop;
      return True;
   end Launch_Reference;
   function Acquisition_Reference (Data : E.Bytes; Frame : E.Span) return Boolean is
      Request : constant E.Span := F (Data, Frame, "request");
      Rows : constant E.Span := F (Data, Frame, "messages");
      Pidfd : constant E.Span := F (Data, Frame, "pidfd");
      Child : constant E.Span := F (Data, Frame, "child_pid");
      Prior_Actor, Prior_Events : E.Span := (1, 0);
      Excluded : Boolean := False;
      Complete : Boolean := False;
   begin
      if not Launch_Reference (Data, Frame) or else not V.Is_Sequence (Data, Rows) or else
         V.Count (Data, Rows) = 0 or else not V.Is_Integer (Data, Child) or else R.Number (Data, Child) <= 0 or else
         R.Pidfd_Pid (Data, F (Data, Pidfd, "fdinfo")) /= R.Number (Data, Child) then return False; end if;
      if not Descriptor_Reference (Data, Pidfd) then return False; end if;
      if not Pidfd_OFD_Reference (Data, Frame, F (Data, Frame, "pidfd_ofd_current")) then return False; end if;
      if Same (Data, Child, F (Data, F (Data, Frame, "owner"), "pid")) or else
         not S.Text_Is (Data, F (Data, F (Data, Frame, "pidfd_open"), "call"), "pidfd_open") or else
         not Same (Data, F (Data, F (Data, F (Data, Frame, "pidfd_open"), "args"), "pid"), Child) or else
         not Num (Data, F (Data, F (Data, F (Data, Frame, "pidfd_open"), "args"), "flags"), 0) or else
         not Same (Data, F (Data, F (Data, Frame, "pidfd_open"), "result"), F (Data, Pidfd, "fd")) or else
         not Num (Data, F (Data, F (Data, Frame, "pidfd_open"), "errno"), 0) or else
         not Receipt_Source (Data, Frame, F (Data, F (Data, Frame, "pidfd_open"), "source")) then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Rows) loop
         declare Row : constant E.Span := V.Element (Data, Rows, I - 1);
                 Message : constant E.Span := F (Data, Row, "message");
                 Actor : constant E.Span := F (Data, Message, "actor");
                 Kernel : constant E.Span := F (Data, Row, "kernel");
                 Source : constant E.Span := F (Data, Message, "source");
                 Receive : constant E.Span := F (Data, Row, "receive");
                 Uids : constant E.Span := F (Data, Message, "resuid");
                 Gids : constant E.Span := F (Data, Message, "resgid");
                 Groups : constant E.Span := F (Data, Message, "groups");
                 Uid : constant E.Span := V.Element (Data, Uids, 0);
                 Gid : constant E.Span := V.Element (Data, Gids, 0);
                 Is_Actor : constant Boolean := S.Text_Is (Data, F (Data, Message, "stage"), "ACTOR"); begin
            if Complete or else not JSON_Matches (Data, F (Data, Row, "message_raw"), Message) or else
               not S.Text_Is (Data, F (Data, Message, "schema"), "worldline.fixed-source-actor-message-v1") or else
               S.Member_Count (Data, Message) /= 15 or else
               S.Member_Count (Data, F (Data, Source, "bootstrap_flags")) /= 3 or else
               not Boolean_Is (Data, F (Data, F (Data, Source, "bootstrap_flags"), "isolated"), True) or else
               not Boolean_Is (Data, F (Data, F (Data, Source, "bootstrap_flags"), "no_site"), True) or else
               not Boolean_Is (Data, F (Data, F (Data, Source, "bootstrap_flags"), "dont_write_bytecode"), True) or else
               not J.Unsigned_Is (Data, F (Data, Message, "sequence"), I) or else
               (not Is_Actor and then not S.Text_Is (Data, F (Data, Message, "stage"), "BOOTSTRAP")) or else
               (Excluded and then not Is_Actor) or else V.Count (Data, Uids) /= 3 or else V.Count (Data, Gids) /= 3 or else
               not V.Is_Integer (Data, Uid) or else not V.Is_Integer (Data, Gid) or else
               not Receive_Reference (Data, Frame, Receive, F (Data, Row, "message_descriptor"), Child, Uid, Gid,
                 F (Data, Row, "owner_source")) or else
               not Sealed (Data, F (Data, Row, "message_seals")) or else
               R.Number (Data, F (Data, F (Data, Row, "message_descriptor"), "mode")) / 4096 /= 8 or else
               not J.Unsigned_Is (Data, F (Data, F (Data, Row, "message_descriptor"), "size"),
                 V.Bytes_Value (Data, F (Data, Row, "message_raw"))'Length) or else
               not Same (Data, F (Data, F (Data, Row, "message_descriptor"), "uid"), V.Element (Data, Uids, 1)) or else
               not Same (Data, F (Data, F (Data, Row, "message_descriptor"), "gid"), V.Element (Data, Gids, 1)) or else
               not Owner_Reference (Data, Frame, F (Data, Row, "owner_current"), F (Data, Row, "owner_source"),
                 F (Data, Row, "owner_status"), F (Data, Row, "owner_stat")) or else
               not V.Is_Integer (Data, F (Data, Row, "observed_at_ns")) or else
               R.Number (Data, F (Data, Row, "observed_at_ns")) > R.Number (Data, F (Data, Frame, "deadline_ns")) or else
               not Same (Data, F (Data, Actor, "pid"), Child) or else not Same (Data, F (Data, Kernel, "pid"), Child) or else
               R.Stat_Field (Data, F (Data, Row, "actor_stat"), 4) /= R.Number (Data, F (Data, F (Data, Frame, "owner"), "pid")) or else
               R.Stat_Field (Data, F (Data, Row, "kernel_stat"), 4) /= R.Number (Data, F (Data, F (Data, Frame, "owner"), "pid")) or else
               not Same (Data, F (Data, Actor, "boot_hex"), F (Data, Kernel, "boot_hex")) or else
               not Same (Data, F (Data, Actor, "boot_hex"), F (Data, F (Data, Frame, "owner"), "boot_hex")) or else
               not Same (Data, F (Data, Actor, "start_tick"), F (Data, Kernel, "start_tick")) or else
               not Same (Data, F (Data, Actor, "exe"), F (Data, Kernel, "exe")) or else
               not Same (Data, F (Data, Kernel, "exe"), F (Data, F (Data, F (Data, Frame, "installation"), "runtime"), "interpreter")) or else
               not Same (Data, F (Data, Actor, "namespaces"), F (Data, Kernel, "namespaces")) or else
               not Same (Data, F (Data, Kernel, "namespaces"), F (Data, F (Data, Frame, "owner"), "namespaces")) or else
               not Same (Data, F (Data, Kernel, "uid_map_hex"), F (Data, F (Data, Frame, "owner"), "uid_map_hex")) or else
               not Same (Data, F (Data, Kernel, "gid_map_hex"), F (Data, F (Data, Frame, "owner"), "gid_map_hex")) or else
               not Same (Data, F (Data, Actor, "uid_map_hex"), F (Data, Kernel, "uid_map_hex")) or else
               not Same (Data, F (Data, Actor, "gid_map_hex"), F (Data, Kernel, "gid_map_hex")) or else
               not Same (Data, F (Data, Actor, "cmdline_hex"), F (Data, Kernel, "cmdline_hex")) or else
               not Hex_Matches (Data, F (Data, Kernel, "cmdline_hex"), F (Data, Frame, "actor_argv_raw")) or else
               not Process_Reference (Data, Actor, F (Data, Row, "actor_stat")) or else
               not Process_Reference (Data, Kernel, F (Data, Row, "kernel_stat")) or else
               not Hex_Matches (Data, F (Data, Actor, "status_hex"), F (Data, Row, "actor_status")) or else
               not Hex_Matches (Data, F (Data, Kernel, "status_hex"), F (Data, Row, "kernel_status")) or else
               not Poll_Matches (Data, F (Data, Row, "poll"), Pidfd, False) or else
               not Hex_Matches (Data, F (Data, Message, "carrier_peer_hex"), F (Data, F (Data, Frame, "owner_channel"), "peer")) or else
               not Descriptor_Reference (Data, F (Data, Message, "channel")) or else
               R.Number (Data, F (Data, F (Data, Message, "channel"), "mode")) / 4096 /= 12 or else
               not Descriptor_Reference (Data, F (Data, Message, "endpoint_parent")) or else
               not Identity (Data, F (Data, Message, "channel"), F (Data, Frame, "actor_channel_origin")) or else
               not Identity (Data, F (Data, Row, "channel_current"), F (Data, Frame, "actor_channel_origin")) or else
               not Identity (Data, F (Data, Message, "endpoint_parent"), F (Data, Frame, "endpoint_parent")) or else
               not Identity (Data, F (Data, Row, "parent_current"), F (Data, Frame, "endpoint_parent")) or else
               not Identity (Data, F (Data, Message, "projection"), F (Data, Frame, "projection")) or else
               not Projection_Reference (Data, F (Data, Source, "projection_readback"), F (Data, Message, "projection"),
                 F (Data, Frame, "projected_source")) or else
               not Identity (Data, F (Data, Row, "projection_current"), F (Data, Frame, "projection")) or else
               not C.Corresponds (Data, F (Data, Row, "owner_source"), F (Data, Frame, "installation")) or else
               not Same (Data, F (Data, F (Data, Row, "owner_source"), "envelope_bytes_hex"),
                 F (Data, F (Data, Frame, "owner_source"), "envelope_bytes_hex")) or else
               not Same (Data, F (Data, Source, "envelope_bytes_hex"), F (Data, F (Data, Frame, "projected_source"), "envelope_bytes_hex"))
            then return False; end if;
            for K in E.Count range 1 .. 3 loop
               if not Same (Data, V.Element (Data, Uids, K - 1),
                    (if Is_Actor then Uid else V.Element (Data, F (Data, F (Data, Frame, "owner"), "resuid"), K - 1))) or else
                  not Same (Data, V.Element (Data, Gids, K - 1),
                    (if Is_Actor then Gid else V.Element (Data, F (Data, F (Data, Frame, "owner"), "resgid"), K - 1)))
               then return False; end if;
            end loop;
            if not Same (Data, F (Data, Actor, "kernel_uid"), F (Data, Kernel, "kernel_uid")) or else
               not Same (Data, F (Data, Actor, "kernel_gid"), F (Data, Kernel, "kernel_gid")) or else
               not Status_Columns (Data, F (Data, Row, "actor_status"), F (Data, Actor, "kernel_uid"), "Uid:", False) or else
               not Status_Columns (Data, F (Data, Row, "kernel_status"), F (Data, Kernel, "kernel_uid"), "Uid:", False) or else
               not Status_Columns (Data, F (Data, Row, "actor_status"), F (Data, Actor, "kernel_gid"), "Gid:", False) or else
               not Status_Columns (Data, F (Data, Row, "kernel_status"), F (Data, Kernel, "kernel_gid"), "Gid:", False) or else
               not Status_Columns (Data, F (Data, Row, "actor_status"), Groups, "Groups:", False) or else
               not Status_Columns (Data, F (Data, Row, "kernel_status"), Groups, "Groups:", False) then return False; end if;
            if Is_Actor then
               if not Same (Data, Uid, F (Data, Request, "uid")) or else not Same (Data, Gid, F (Data, Request, "gid")) or else
                  not Group_Multiset (Data, Groups, F (Data, Request, "groups")) or else
                  not Status_Columns (Data, F (Data, Row, "actor_status"), Uid, "Uid:", True, 4) or else
                  not Status_Columns (Data, F (Data, Row, "kernel_status"), Uid, "Uid:", True, 4) or else
                  not Status_Columns (Data, F (Data, Row, "actor_status"), Gid, "Gid:", True, 4) or else
                  not Status_Columns (Data, F (Data, Row, "kernel_status"), Gid, "Gid:", True, 4) or else
                  R.Number (Data, Uid) = 0 or else
                  not Capabilities_Dropped (Data, Frame, F (Data, Row, "actor_status")) or else
                  not Capabilities_Dropped (Data, Frame, F (Data, Row, "kernel_status")) or else
                  not C.Corresponds (Data, Source, F (Data, Frame, "installation")) then return False; end if;
               Excluded := True;
            else
               if not Num (Data, V.Element (Data, Uids, 1), 0) or else
                  not Group_Multiset (Data, Groups, F (Data, F (Data, Frame, "owner"), "groups")) or else
                  not C.Bootstrap_Corresponds (Data, Source, F (Data, Frame, "installation")) then return False; end if;
            end if;
            for Name in 1 .. 2 loop
               declare Key : constant String := (if Name = 1 then "stdout" else "stderr");
                       Origin : constant E.Span := F (Data, F (Data, Frame, "output_origins"), Key); begin
                  if not Identity (Data, F (Data, F (Data, Row, "output_current"), Key), F (Data, Origin, "origin")) or else
                     not Num (Data, F (Data, Origin, "actor_fd"), Long_Long_Integer (Name)) or else
                     not Num (Data, F (Data, F (Data, Origin, "origin"), "uid"), 0) or else
                     not Num (Data, F (Data, F (Data, Origin, "origin"), "mode"), 33_152) or else
                     not Close_Reference (Data, Frame, F (Data, Origin, "writer_close"), F (Data, Origin, "origin"),
                       F (Data, Origin, "writer_close_source")) then return False; end if;
               end;
            end loop;
            if not V.Is_Null (Data, F (Data, Message, "target")) then
               if not Is_Actor or else not Same (Data, F (Data, Message, "target"), F (Data, F (Data, Frame, "target"), "message")) or else
                  not Target_Reference (Data, Frame, not V.Is_Null (Data, F (Data, F (Data, Frame, "target"), "close")))
               then return False; end if;
            elsif not V.Is_Null (Data, F (Data, Frame, "target")) and then
               R.Number (Data, F (Data, F (Data, Frame, "target"), "sequence")) < R.Number (Data, F (Data, Message, "sequence"))
            then return False; end if;
            if Prior_Actor.Length /= 0 then
               if not Same (Data, F (Data, Actor, "boot_hex"), F (Data, Prior_Actor, "boot_hex")) or else
                  not Same (Data, F (Data, Actor, "start_tick"), F (Data, Prior_Actor, "start_tick")) or else
                  not Same (Data, F (Data, Actor, "namespaces"), F (Data, Prior_Actor, "namespaces")) or else
                  not Prefix_Events (Data, Prior_Events, F (Data, Source, "events")) then return False; end if;
            end if;
            Prior_Actor := Actor; Prior_Events := F (Data, Source, "events");
            if S.Text_Is (Data, F (Data, Message, "kind"), "COMPLETE") then
               if not Is_Actor or else not Boolean_Is (Data, F (Data, F (Data, Message, "terminal"), "final_check"), True) then
                  return False;
               end if;
               Complete := True;
            elsif not S.Text_Is (Data, F (Data, Message, "kind"), "ACQUIRE") or else
                  not V.Is_Null (Data, F (Data, Message, "terminal")) then return False;
            end if;
         end;
      end loop;
      return True;
   end Acquisition_Reference;
   function Completion_Reference (Data : E.Bytes; Frame : E.Span) return Boolean is
      Rows : constant E.Span := F (Data, Frame, "messages");
      Terminal : constant E.Span := F (Data, Frame, "terminal");
      Owner : constant E.Span := F (Data, Frame, "owner_final_source");
   begin
      if not Acquisition_Reference (Data, Frame) or else not V.Is_Null (Data, F (Data, Frame, "error")) or else
         not C.Corresponds (Data, Owner, F (Data, Frame, "installation")) or else
         not C.Readbacks_Correspond (Data, Owner) or else not Target_Reference (Data, Frame, True) or else
         not Same (Data, F (Data, Owner, "envelope_bytes_hex"), F (Data, F (Data, Frame, "owner_source"), "envelope_bytes_hex")) or else
         not Num (Data, F (Data, Terminal, "wait"), 0) or else
         not Same (Data, F (Data, F (Data, Terminal, "waitid"), "si_pid"), F (Data, Frame, "child_pid")) or else
         not Num (Data, F (Data, F (Data, Terminal, "waitid"), "si_code"), 1) or else
         not Num (Data, F (Data, F (Data, Terminal, "waitid"), "si_status"), 0) or else
         not Num (Data, F (Data, F (Data, Terminal, "waitid"), "si_signo"), 17) or else
         not Same (Data, F (Data, F (Data, Terminal, "waitid"), "si_uid"), F (Data, F (Data, Frame, "request"), "uid")) or else
         not Terminal_Reference (Data, Frame, Terminal) or else not Watch_Reference (Data, Frame, Terminal) or else
         not Identity (Data, F (Data, Terminal, "pidfd_current"), F (Data, Frame, "pidfd")) or else
         not Same (Data, F (Data, F (Data, Terminal, "pidfd_current"), "fd"), F (Data, F (Data, Frame, "pidfd"), "fd")) or else
         not V.Valid_Bytes (Data, F (Data, F (Data, Terminal, "pidfd_current"), "fdinfo")) or else
         not Poll_Matches (Data, F (Data, Terminal, "poll"), F (Data, Frame, "pidfd"), True) then return False; end if;
      declare Last : constant E.Span := F (Data, V.Element (Data, Rows, V.Count (Data, Rows) - 1), "message"); begin
         if not S.Text_Is (Data, F (Data, Last, "kind"), "COMPLETE") or else
            not Num (Data, F (Data, F (Data, Last, "terminal"), "exit_status"), 0) or else
            not V.Is_Null (Data, F (Data, F (Data, Last, "terminal"), "exception")) then return False; end if;
      end;
      for I in 1 .. 2 loop
         declare Stream : constant E.Span := F (Data, Terminal, (if I = 1 then "stdout" else "stderr")); begin
            if not Stream_Reference (Data, Frame, Stream, F (Data, F (Data, Frame, "output_origins"),
                 (if I = 1 then "stdout" else "stderr"))) then return False; end if;
         end;
      end loop;
      return True;
   end Completion_Reference;
   function Result_Reference (Data : E.Bytes; Result : Action) return Boolean is
      Frame : constant E.Span := (Data'First, Data'Length);
      Phase : constant E.Span := F (Data, Frame, "phase");
   begin
      if S.Text_Is (Data, Phase, "LAUNCH") then
         return Result = (if Launch_Reference (Data, Frame) then Bootstrap_Acquired else Refused);
      elsif S.Text_Is (Data, Phase, "ACQUIRE") then
         if not Acquisition_Reference (Data, Frame) then return Result = Refused; end if;
         declare Rows : constant E.Span := F (Data, Frame, "messages");
                 Last : constant E.Span := F (Data, V.Element (Data, Rows, V.Count (Data, Rows) - 1), "message"); begin
            return Result = (if S.Text_Is (Data, F (Data, Last, "stage"), "ACTOR") then Actor_Acquired else Bootstrap_Acquired);
         end;
      elsif S.Text_Is (Data, Phase, "COMPLETE") then
         return Result = (if Completion_Reference (Data, Frame) then Completed else Refused);
      end if;
      return Result = Refused;
   end Result_Reference;
   function Decide (Data : E.Bytes) return Action is
      Frame : constant E.Span := (Data'First, Data'Length);
      Phase : constant E.Span := F (Data, Frame, "phase");
   begin
      if S.Text_Is (Data, Phase, "LAUNCH") then
         return (if Launch_Reference (Data, Frame) then Bootstrap_Acquired else Refused);
      elsif S.Text_Is (Data, Phase, "ACQUIRE") then
         if not Acquisition_Reference (Data, Frame) then return Refused; end if;
         declare Rows : constant E.Span := F (Data, Frame, "messages");
                 Last : constant E.Span := F (Data, V.Element (Data, Rows, V.Count (Data, Rows) - 1), "message"); begin
            return (if S.Text_Is (Data, F (Data, Last, "stage"), "ACTOR") then Actor_Acquired else Bootstrap_Acquired);
         end;
      elsif S.Text_Is (Data, Phase, "COMPLETE") then
         return (if Completion_Reference (Data, Frame) then Completed else Refused);
      end if;
      return Refused;
   end Decide;
end Worldline.Excluded_Source_Owner;
