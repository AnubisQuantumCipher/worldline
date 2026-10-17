with SPARK.Big_Integers;
with Worldline.Custody_V2_Root_Evidence;
with Worldline.Custody_V2_Requester_Join;
with Worldline.Startup_Installation;
package body Worldline.Startup_Source_Custody with SPARK_Mode is
   package E renames L.E;
   package V renames L.V;
   package S renames V.S;
   use type E.Count;
   use type E.Bytes;
   use type E.Value_Kind;
   use type E.Q.Byte;
   function F (D : E.Bytes; X : E.Span; Name : String) return E.Span renames S.Field;
   type Fields is array (1 .. 5) of E.Span;
   type Line is record
      Valid : Boolean := False;
      Count : Natural range 0 .. 5 := 0;
      Parts : Fields := (others => (1, 0));
   end record;
   procedure Next_Line (B : E.Bytes; Offset : in out E.Count; Result : out Line) is
      First : E.Count := Offset;
      N : Natural := 1;
   begin
      Result := (others => <>);
      if Offset >= B'Length then return; end if;
      while Offset < B'Length and then B (B'First + Offset) /= 10 loop
         if B (B'First + Offset) = 9 then
            if N = 5 then return; end if;
            Result.Parts (N) := (B'First + First, Offset - First);
            N := N + 1; First := Offset + 1;
         end if;
         Offset := Offset + 1;
      end loop;
      if Offset = B'Length then return; end if;
      Result.Parts (N) := (B'First + First, Offset - First);
      Result.Count := N; Result.Valid := True; Offset := Offset + 1;
   end Next_Line;
   function Plain (B : E.Bytes; X : E.Span; Text : String) return Boolean is
     (E.C.P.Valid (B, X) and then X.Length = Text'Length and then
      (for all I in Text'Range => B (X.First + E.Count (I - Text'First)) = Character'Pos (Text (I))));
   function Same_Raw (B : E.Bytes; X : E.Span; Raw : E.Bytes) return Boolean is
     (E.C.P.Valid (B, X) and then X.Length = Raw'Length and then
      (for all I in E.Count range 1 .. X.Length => B (X.First + (I - 1)) = Raw (Raw'First + (I - 1))));
   function Lower_Hex (B : E.Bytes; X : E.Span) return Boolean is
     (E.C.P.Valid (B, X) and then X.Length mod 2 = 0 and then
      (for all I in E.Count range 1 .. X.Length => B (X.First + (I - 1)) in
        Character'Pos ('0') .. Character'Pos ('9') | Character'Pos ('a') .. Character'Pos ('f')));
   function Hex_Matches (B : E.Bytes; X : E.Span; Raw : E.Bytes) return Boolean is
      Hex : constant String := "0123456789abcdef";
   begin
      return Lower_Hex (B, X) and then X.Length / 2 = Raw'Length and then
        (for all I in E.Count range 1 .. Raw'Length =>
          B (X.First + (I - 1) * 2) = Character'Pos (Hex (Integer (Raw (Raw'First + (I - 1)) / 16) + 1)) and then
          B (X.First + (I - 1) * 2 + 1) = Character'Pos (Hex (Integer (Raw (Raw'First + (I - 1)) mod 16) + 1)));
   end Hex_Matches;
   function Text_Hex_Matches (D, B : E.Bytes; X, Text : E.Span) return Boolean is
     (V.Valid_Text (D, Text) and then Hex_Matches (B, X, V.Text_Value (D, Text)));
   function Path_Hex_Matches (D, B : E.Bytes; X, Text : E.Span) return Boolean is
      function Digit (Byte : E.Q.Byte) return E.Q.Byte is
        (if Byte in Character'Pos ('0') .. Character'Pos ('9') then Byte - Character'Pos ('0')
         else Byte - Character'Pos ('a') + 10);
   begin
      if not V.Valid_Text (D, Text) or else not Lower_Hex (B, X) then return False; end if;
      declare Path : E.Bytes (1 .. X.Length / 2); begin
         for I in Path'Range loop
            Path (I) := Digit (B (X.First + (I - 1) * 2)) * 16 + Digit (B (X.First + (I - 1) * 2 + 1));
         end loop;
         return Worldline.Startup_Installation.Path_Bytes_Equivalent (Path, V.Text_Value (D, Text));
      end;
   end Path_Hex_Matches;
   function Hex_Text (D, B : E.Bytes; X, Encoded : E.Span) return Boolean is
     (V.Valid_Hex_Field (D, Encoded, "value") and then Lower_Hex (B, X) and then
      Same_Raw (B, X, V.Hex_Text (D, Encoded, "value")));
   function Role (B : E.Bytes; X : E.Span; Expected : String) return Boolean is
     (Expected'Length = 0 or else Plain (B, X, Expected));
   function File_Matches
     (D, B : E.Bytes; Path, Bytes_Hex : E.Span; Expected_Role : String) return Boolean is
      Offset : E.Count := 0;
      Item : Line;
      Found : E.Count := 0;
   begin
      while Offset < B'Length loop
         Next_Line (B, Offset, Item);
         if not Item.Valid then return False; end if;
         if Item.Count = 5 and then Plain (B, Item.Parts (1), "FILE") and then
            Text_Hex_Matches (D, B, Item.Parts (3), Path) then
            if not Role (B, Item.Parts (2), Expected_Role) or else
               not Hex_Text (D, B, Item.Parts (5), Bytes_Hex) then return False; end if;
            Found := Found + 1;
         elsif Item.Count = 2 and then Plain (B, Item.Parts (1), "ABSENT") and then
               Text_Hex_Matches (D, B, Item.Parts (2), Path) then return False;
         end if;
      end loop;
      return Found = 1;
   end File_Matches;
   function Image_Matches (D, B : E.Bytes; Event : E.Span; Kind : String) return Boolean is
      Offset : E.Count := 0;
      Item : Line;
      Found : E.Count := 0;
      Name : constant E.Span := F (D, Event, "image_member");
   begin
      if not V.Valid_Text (D, F (D, Event, "module")) or else not V.Valid_Text (D, Name) then return False; end if;
      while Offset < B'Length loop
         Next_Line (B, Offset, Item);
         if not Item.Valid then return False; end if;
         if Item.Count = 2 and then Plain (B, Item.Parts (1), Kind) and then
            Text_Hex_Matches (D, B, Item.Parts (2), Name) then Found := Found + 1; end if;
      end loop;
      return Found = 1;
   end Image_Matches;
   function Interpreter_Selected (D, B : E.Bytes; Path : E.Span) return Boolean is
      Offset : E.Count := 0;
      Item : Line;
      Found : E.Count := 0;
   begin
      while Offset < B'Length loop
         Next_Line (B, Offset, Item);
         if not Item.Valid then return False; end if;
         if Item.Count = 5 and then Plain (B, Item.Parts (1), "FILE") and then Plain (B, Item.Parts (2), "INTERPRETER") then
            if not Text_Hex_Matches (D, B, Item.Parts (3), Path) then return False; end if;
            Found := Found + 1;
         end if;
      end loop;
      return Found = 1;
   end Interpreter_Selected;
   function Cache_Matches (D, B : E.Bytes; Candidate : E.Span) return Boolean is
      Offset : E.Count := 0;
      Item : Line;
      Found : E.Count := 0;
      Path : constant E.Span := F (D, Candidate, "path");
      Presence : constant E.Span := F (D, Candidate, "present");
      Actual : constant E.View := E.Decode (D, S.A.Field (D, Presence, "value"), E.Operation);
   begin
      if not V.Type_Is (D, Presence, "bool") or else Actual.Form /= E.Boolean_Value then return False; end if;
      if Actual.Boolean_Bit then return File_Matches (D, B, Path, F (D, Candidate, "bytes_hex"), "CACHE"); end if;
      while Offset < B'Length loop
         Next_Line (B, Offset, Item);
         if not Item.Valid then return False; end if;
         if Item.Count = 2 and then Plain (B, Item.Parts (1), "ABSENT") and then
            Text_Hex_Matches (D, B, Item.Parts (2), Path) then Found := Found + 1; end if;
         if Item.Count = 5 and then Plain (B, Item.Parts (1), "FILE") and then
            Text_Hex_Matches (D, B, Item.Parts (3), Path) then return False; end if;
      end loop;
      return Found = 1;
   end Cache_Matches;
   function Flags_Match (D, B : E.Bytes; Flags : E.Span) return Boolean is
      Offset : E.Count;
      Item : Line;
   begin
      if S.Member_Count (D, Flags) /= 4 then return False; end if;
      for I in 1 .. 4 loop
         declare Name : constant String := (case I is when 1 => "optimize", when 2 => "cache_tag", when 3 => "magic", when 4 => "version");
                 Found : E.Count := 0; begin
            Offset := 0;
            while Offset < B'Length loop
               Next_Line (B, Offset, Item);
               if not Item.Valid then return False; end if;
               if Item.Count = 3 and then Plain (B, Item.Parts (1), "FLAG") and then Plain (B, Item.Parts (2), Name) then
                  if not Text_Hex_Matches (D, B, Item.Parts (3), F (D, Flags, Name)) then return False; end if;
                  Found := Found + 1;
               end if;
            end loop;
            if Found /= 1 then return False; end if;
         end;
      end loop;
      return True;
   end Flags_Match;
   function Cache_Paths_Match
     (D : E.Bytes; Path, Candidates, Flags : E.Span) return Boolean is
      First : constant E.Span := F (D, V.Element (D, Candidates, 0), "path");
      Second : constant E.Span := F (D, V.Element (D, Candidates, 1), "path");
      Tag : constant E.Span := F (D, Flags, "cache_tag");
      Optimize : constant E.Span := F (D, Flags, "optimize");
   begin
      if not V.Valid_Text (D, Path) or else not V.Valid_Text (D, First) or else
         not V.Valid_Text (D, Second) or else not V.Valid_Text (D, Tag) or else
         not V.Valid_Text (D, Optimize) then return False; end if;
      declare Source : constant E.Bytes := V.Text_Value (D, Path);
              Computed : constant E.Bytes := V.Text_Value (D, First);
              Adjacent : constant E.Bytes := V.Text_Value (D, Second);
              Cache_Tag : constant E.Bytes := V.Text_Value (D, Tag);
              Opt : constant E.Bytes := V.Text_Value (D, Optimize);
              Slash, Dot, Cursor, Keep : E.Count := 0;
              Matched : Boolean;
              --  The matchers advance the shared Cursor, so SPARK requires
              --  them to be procedures; each original short-circuit chain
              --  below is written as the same sequence of guarded steps.
              procedure Match_Source (Target : E.Bytes; Start, Length : E.Count; OK : out Boolean) is
              begin
                 OK := False;
                 if Cursor > Target'Length or else Length > Target'Length - Cursor or else
                    Start > Source'Length or else Length > Source'Length - Start then return; end if;
                 for I in E.Count range 1 .. Length loop
                    if Target (Target'First + Cursor + I - 1) /= Source (Source'First + Start + I - 1) then return; end if;
                 end loop;
                 Cursor := Cursor + Length; OK := True;
              end Match_Source;
              procedure Match_Text (Target : E.Bytes; Text : String; OK : out Boolean) is
              begin
                 OK := False;
                 if Cursor > Target'Length or else Text'Length > Target'Length - Cursor then return; end if;
                 for I in Text'Range loop
                    if Target (Target'First + Cursor + E.Count (I - Text'First)) /= Character'Pos (Text (I)) then return; end if;
                 end loop;
                 Cursor := Cursor + Text'Length; OK := True;
              end Match_Text;
              procedure Match_Bytes (Target, Bytes : E.Bytes; OK : out Boolean) is
              begin
                 OK := False;
                 if Cursor > Target'Length or else Bytes'Length > Target'Length - Cursor then return; end if;
                 for I in E.Count range 1 .. Bytes'Length loop
                    if Target (Target'First + Cursor + I - 1) /= Bytes (Bytes'First + I - 1) then return; end if;
                 end loop;
                 Cursor := Cursor + Bytes'Length; OK := True;
              end Match_Bytes;
      begin
         for I in E.Count range 1 .. Source'Length loop
            if Source (Source'First + I - 1) = Character'Pos ('/') then Slash := I; Dot := 0;
            elsif Source (Source'First + I - 1) = Character'Pos ('.') then Dot := I; end if;
         end loop;
         Match_Source (Computed, 0, Slash, Matched);
         if not Matched then return False; end if;
         Match_Text (Computed, "__pycache__/", Matched);
         if not Matched then return False; end if;
         Match_Source (Computed, Slash, (if Dot > Slash then Dot - Slash - 1 else Source'Length - Slash), Matched);
         if not Matched then return False; end if;
         Match_Text (Computed, ".", Matched);
         if not Matched then return False; end if;
         Match_Bytes (Computed, Cache_Tag, Matched);
         if not Matched then return False; end if;
         if not S.Text_Is (D, Optimize, "0") then
            Match_Text (Computed, ".opt-", Matched);
            if not Matched then return False; end if;
            Match_Bytes (Computed, Opt, Matched);
            if not Matched then return False; end if;
         end if;
         Match_Text (Computed, ".pyc", Matched);
         if not Matched or else Cursor /= Computed'Length then return False; end if;
         Keep := Source'Length;
         for I in 1 .. 3 loop
            if Keep = 0 then exit; end if;
            Keep := Keep - 1;
            while Keep > 0 and then Source (Source'First + Keep) in 128 .. 191 loop
               pragma Loop_Variant (Decreases => Keep);
               Keep := Keep - 1;
            end loop;
         end loop;
         Cursor := 0;
         Match_Source (Adjacent, 0, Keep, Matched);
         if not Matched then return False; end if;
         Match_Text (Adjacent, ".pyc", Matched);
         return Matched and then Cursor = Adjacent'Length;
      end;
   end Cache_Paths_Match;
   function Envelope_Valid (B : E.Bytes) return Boolean is
      Offset, Previous_Offset : E.Count := 0;
      Item, Earlier, Header : Line;
      Helper_Count, Interpreter_Count : E.Count := 0;
      function Equal (A, C : E.Span) return Boolean is
        (A.Length = C.Length and then
         (for all I in E.Count range 1 .. A.Length => B (A.First + I - 1) = B (C.First + I - 1)));
      function Octal (X : E.Span) return Boolean is
        (X.Length > 0 and then (X.Length = 1 or else B (X.First) /= Character'Pos ('0')) and then
         (for all I in E.Count range 1 .. X.Length => B (X.First + I - 1) in Character'Pos ('0') .. Character'Pos ('7')));
      function Key (X : Line) return E.Span is
      begin
         if Plain (B, X.Parts (1), "FILE") then
            return X.Parts (3);
         else
            return X.Parts (2);
         end if;
      end Key;
   begin
      Next_Line (B, Offset, Header);
      if not Header.Valid or else Header.Count /= 1 or else
         not Plain (B, Header.Parts (1), "WORLDLINE-APPROVED-SOURCE-ENVELOPE-V1") then return False; end if;
      while Offset < B'Length loop
         Previous_Offset := Offset;
         Next_Line (B, Offset, Item);
         if not Item.Valid then return False; end if;
         if Plain (B, Item.Parts (1), "FILE") then
            if Item.Count /= 5 or else not Lower_Hex (B, Item.Parts (3)) or else
               Item.Parts (3).Length = 0 or else not Octal (Item.Parts (4)) or else
               not Lower_Hex (B, Item.Parts (5)) or else
               not (Plain (B, Item.Parts (2), "HELPER") or else Plain (B, Item.Parts (2), "ENTRY") or else
                    Plain (B, Item.Parts (2), "INTERPRETER") or else Plain (B, Item.Parts (2), "EXECUTABLE") or else
                    Plain (B, Item.Parts (2), "SOURCE") or else
                    Plain (B, Item.Parts (2), "EXTENSION") or else Plain (B, Item.Parts (2), "CACHE") or else
                    Plain (B, Item.Parts (2), "DATA")) then return False; end if;
            if Plain (B, Item.Parts (2), "EXECUTABLE") then
               declare Mode : constant E.Span := Item.Parts (4);
                       Executable : Boolean := False; begin
                  for I in E.Count range 1 .. E.Count'Min (3, Mode.Length) loop
                     if B (Mode.First + Mode.Length - I) in
                       Character'Pos ('1') | Character'Pos ('3') | Character'Pos ('5') | Character'Pos ('7')
                     then Executable := True; end if;
                  end loop;
                  if not Executable then return False; end if;
               end;
            end if;
            if Plain (B, Item.Parts (2), "HELPER") then Helper_Count := Helper_Count + 1; end if;
            if Plain (B, Item.Parts (2), "INTERPRETER") then Interpreter_Count := Interpreter_Count + 1; end if;
         elsif Plain (B, Item.Parts (1), "ABSENT") or else Plain (B, Item.Parts (1), "BUILTIN") or else
               Plain (B, Item.Parts (1), "FROZEN") then
            if Item.Count /= 2 or else Item.Parts (2).Length = 0 or else
               not Lower_Hex (B, Item.Parts (2)) then return False; end if;
         elsif Plain (B, Item.Parts (1), "DIRECTORY") then
            if Item.Count /= 3 or else Item.Parts (2).Length = 0 or else
               not Lower_Hex (B, Item.Parts (2)) or else not Octal (Item.Parts (3)) then return False; end if;
         elsif Plain (B, Item.Parts (1), "FLAG") then
            if Item.Count /= 3 or else not Lower_Hex (B, Item.Parts (3)) or else
               not (Plain (B, Item.Parts (2), "optimize") or else Plain (B, Item.Parts (2), "cache_tag") or else
                    Plain (B, Item.Parts (2), "magic") or else Plain (B, Item.Parts (2), "version")) then return False; end if;
         else return False;
         end if;
         declare Scan : E.Count := 0; begin
            Next_Line (B, Scan, Earlier);
            while Scan < Previous_Offset loop
               Next_Line (B, Scan, Earlier);
               if not Earlier.Valid then return False; end if;
               if Equal (Key (Item), Key (Earlier)) and then
                  (Equal (Item.Parts (1), Earlier.Parts (1)) or else
                   ((Plain (B, Item.Parts (1), "FILE") or else Plain (B, Item.Parts (1), "ABSENT")) and then
                    (Plain (B, Earlier.Parts (1), "FILE") or else Plain (B, Earlier.Parts (1), "ABSENT")))) then return False; end if;
            end loop;
         end;
      end loop;
      return Helper_Count = 1 and then Interpreter_Count = 1;
   end Envelope_Valid;
   function Closure_Corresponds
     (Data : L.E.Bytes; Source, Installation : L.E.Span; Require_Entry : Boolean) return Boolean is
      Encoded : constant E.Span := F (Data, Source, "envelope_bytes_hex");
      Events : constant E.Span := F (Data, Source, "events");
      Entry_Count : E.Count := 0;
   begin
      if not S.Text_Is (Data, F (Data, Source, "schema"), "worldline.approved-executed-code-observation-v1") or else
         not V.Valid_Hex_Field (Data, Encoded, "value") or else not V.Is_Sequence (Data, Events) or else
         not Worldline.Startup_Installation.Path_Equivalent (Data, F (Data, Source, "interpreter"),
           F (Data, F (Data, Installation, "runtime"), "interpreter")) then return False; end if;
      declare B : constant E.Bytes := V.Hex_Value (Data, Encoded, "value");
              Offset : E.Count := 0;
              Header : Line; begin
         if not Envelope_Valid (B) or else not Interpreter_Selected (Data, B, F (Data, Source, "interpreter")) then return False; end if;
         Next_Line (B, Offset, Header);
         if not Header.Valid or else Header.Count /= 1 or else
            not Plain (B, Header.Parts (1), "WORLDLINE-APPROVED-SOURCE-ENVELOPE-V1") or else
            not Flags_Match (Data, B, F (Data, Source, "interpreter_flags")) then return False; end if;
         -- Source-code equality is joined to the original full-byte envelope;
         -- initial-cache semantic fidelity remains the original genuine loader
         -- producer's complete code comparison, never its success Boolean.
         for I in E.Count range 1 .. V.Count (Data, Events) loop
            declare Event : constant E.Span := V.Element (Data, Events, I - 1);
                    Kind : constant E.Span := F (Data, Event, "kind");
                    Path : constant E.Span := F (Data, Event, "path");
                    Source_Hex : constant E.Span := F (Data, Event, "source_bytes_hex");
                    Bytes_Hex : constant E.Span := F (Data, Event, "bytes_hex"); begin
               if S.Text_Is (Data, Kind, "ENTRY_COMPILED_BEFORE_EXEC") then
                  Entry_Count := Entry_Count + 1;
                  if not File_Matches (Data, B, Path, Source_Hex, "ENTRY") then return False; end if;
               elsif S.Text_Is (Data, Kind, "INITIAL_HELPER_SOURCE") then
                  if not File_Matches (Data, B, Path, Bytes_Hex, "HELPER") then return False; end if;
               elsif S.Text_Is (Data, Kind, "SOURCE_COMPILED_BEFORE_EXEC") then
                  if not (File_Matches (Data, B, Path, Source_Hex, "SOURCE") or else
                          File_Matches (Data, B, Path, Source_Hex, "ENTRY") or else
                          File_Matches (Data, B, Path, Source_Hex, "HELPER")) then return False; end if;
               elsif S.Text_Is (Data, Kind, "EXPLICIT_SOURCE_COMPILED_BEFORE_EXEC") then
                  if not (File_Matches (Data, B, Path, Source_Hex, "SOURCE") or else
                          File_Matches (Data, B, Path, Source_Hex, "ENTRY")) then return False; end if;
               elsif S.Text_Is (Data, Kind, "EXTENSION_BEFORE_CREATE") then
                  if not File_Matches (Data, B, Path, Bytes_Hex, "EXTENSION") then return False; end if;
               elsif S.Text_Is (Data, Kind, "INITIAL_SOURCE_CANDIDATES") then
                  if not File_Matches (Data, B, Path, Source_Hex, "SOURCE") then return False; end if;
                  declare Candidates : constant E.Span := F (Data, Event, "cache_candidates"); begin
                     if V.Count (Data, Candidates) /= 2 then return False; end if;
                     if not Cache_Paths_Match (Data, Path, Candidates, F (Data, Source, "interpreter_flags")) then return False; end if;
                     for K in E.Count range 1 .. 2 loop
                        if not Cache_Matches (Data, B, V.Element (Data, Candidates, K - 1)) then return False; end if;
                     end loop;
                     if S.A.Same_Encoding (Data, F (Data, V.Element (Data, Candidates, 0), "path"),
                        F (Data, V.Element (Data, Candidates, 1), "path")) then return False; end if;
                  end;
               elsif S.Text_Is (Data, Kind, "INITIAL_BUILTIN") then
                  if not Image_Matches (Data, B, Event, "BUILTIN") then return False; end if;
               elsif S.Text_Is (Data, Kind, "INITIAL_FROZEN") then
                  if not Image_Matches (Data, B, Event, "FROZEN") then return False; end if;
               else return False;
               end if;
            end;
         end loop;
      end;
      return not Require_Entry or else Entry_Count > 0;
   end Closure_Corresponds;
   function Corresponds (Data : L.E.Bytes; Source, Installation : L.E.Span) return Boolean is
     (Closure_Corresponds (Data, Source, Installation, True));
   function Bootstrap_Corresponds (Data : L.E.Bytes; Source, Installation : L.E.Span) return Boolean is
     (Closure_Corresponds (Data, Source, Installation, False));
   function Projection_Corresponds
     (Data : L.E.Bytes; Owner_Source, Actor_Source, Closure, Request,
      Request_Path, Entry_Path : L.E.Span) return Boolean
   is
      Owner_Hex : constant E.Span := F (Data, Owner_Source, "envelope_bytes_hex");
      Actor_Hex : constant E.Span := F (Data, Actor_Source, "envelope_bytes_hex");
      function Listed (B : E.Bytes; Path, Roster : E.Span; Membership : Boolean := False) return Boolean is
         Found : E.Count := 0;
      begin
         if not V.Is_Sequence (Data, Roster) then return False; end if;
         for I in E.Count range 1 .. V.Count (Data, Roster) loop
            if Text_Hex_Matches (Data, B, Path, V.Element (Data, Roster, I - 1)) then
               Found := Found + 1;
            end if;
         end loop;
         return (if Membership then Found > 0 else Found = 1);
      end Listed;
   begin
      if not V.Valid_Hex_Field (Data, Owner_Hex, "value") or else
         not V.Valid_Hex_Field (Data, Actor_Hex, "value") or else
         S.Member_Count (Data, Closure) /= 5 then return False; end if;
      declare Owner : constant E.Bytes := V.Hex_Value (Data, Owner_Hex, "value");
              Actor : constant E.Bytes := V.Hex_Value (Data, Actor_Hex, "value");
              Offset, Scan, Start, Old_Start : E.Count := 0;
              Item, Original : Line;
              Files, Dirs, Absent, Builtins, Frozen, Flags, Entries : E.Count := 0;
      begin
         if not Envelope_Valid (Owner) or else not Envelope_Valid (Actor) then return False; end if;
         Next_Line (Actor, Offset, Item);
         while Offset < Actor'Length loop
            Start := Offset; Next_Line (Actor, Offset, Item);
            if not Item.Valid then return False; end if;
            Scan := 0;
            declare Matches : E.Count := 0; begin
               while Scan < Owner'Length loop
                  Old_Start := Scan; Next_Line (Owner, Scan, Original);
                  if not Original.Valid then return False; end if;
                  if Offset - Start = Scan - Old_Start and then
                    (for all I in E.Count range 0 .. Offset - Start - 1 =>
                       Actor (Actor'First + Start + I) = Owner (Owner'First + Old_Start + I)) then
                     Matches := Matches + 1;
                  end if;
               end loop;
               if Matches /= 1 then return False; end if;
            end;
            if Plain (Actor, Item.Parts (1), "FILE") then
               Files := Files + 1;
               if not Listed (Actor, Item.Parts (3), F (Data, Closure, "files")) then return False; end if;
               if Plain (Actor, Item.Parts (2), "DATA") then
                  if not Text_Hex_Matches (Data, Actor, Item.Parts (3), Request_Path) and then
                     not Listed (Actor, Item.Parts (3), F (Data, Request, "requests"), True) then return False; end if;
               elsif Plain (Actor, Item.Parts (2), "ENTRY") then
                  Entries := Entries + 1;
                  if not Text_Hex_Matches (Data, Actor, Item.Parts (3), Entry_Path) then return False; end if;
               end if;
            elsif Plain (Actor, Item.Parts (1), "DIRECTORY") then
               Dirs := Dirs + 1;
               if not Listed (Actor, Item.Parts (2), F (Data, Closure, "directories")) then return False; end if;
            elsif Plain (Actor, Item.Parts (1), "ABSENT") then
               Absent := Absent + 1;
               if not Listed (Actor, Item.Parts (2), F (Data, Closure, "absent")) then return False; end if;
            elsif Plain (Actor, Item.Parts (1), "BUILTIN") then
               Builtins := Builtins + 1;
               if not Listed (Actor, Item.Parts (2), F (Data, Closure, "builtins")) then return False; end if;
            elsif Plain (Actor, Item.Parts (1), "FROZEN") then
               Frozen := Frozen + 1;
               if not Listed (Actor, Item.Parts (2), F (Data, Closure, "frozen")) then return False; end if;
            elsif Plain (Actor, Item.Parts (1), "FLAG") then Flags := Flags + 1;
            else return False;
            end if;
         end loop;
         return Entries = 1 and then
           Files = V.Count (Data, F (Data, Closure, "files")) and then
           Dirs = V.Count (Data, F (Data, Closure, "directories")) and then
           Absent = V.Count (Data, F (Data, Closure, "absent")) and then
           Builtins = V.Count (Data, F (Data, Closure, "builtins")) and then
           Frozen = V.Count (Data, F (Data, Closure, "frozen")) and then Flags = 4;
      end;
   end Projection_Corresponds;
   function File_Corresponds (Data : L.E.Bytes; Source, Path, Raw_Bytes : L.E.Span) return Boolean is
      Encoded : constant E.Span := F (Data, Source, "envelope_bytes_hex");
   begin
      if not V.Valid_Hex_Field (Data, Encoded, "value") or else not V.Valid_Bytes (Data, Raw_Bytes) then return False; end if;
      declare B : constant E.Bytes := V.Hex_Value (Data, Encoded, "value");
              Offset : E.Count := 0;
              Item : Line;
              Found : E.Count := 0; begin
         while Offset < B'Length loop
            Next_Line (B, Offset, Item);
            if not Item.Valid then return False; end if;
            if Item.Count = 5 and then Plain (B, Item.Parts (1), "FILE") and then
               Path_Hex_Matches (Data, B, Item.Parts (3), Path) then
               if not Plain (B, Item.Parts (2), "DATA") or else
                  not Same_Raw (B, Item.Parts (5), V.Hex_Text (Data, Raw_Bytes, "value")) then return False; end if;
               Found := Found + 1;
            end if;
         end loop;
         return Found = 1;
      end;
   end File_Corresponds;
   function Image_Corresponds
     (Data : L.E.Bytes; Source, Path, Raw_Bytes : L.E.Span) return Boolean is
      Encoded : constant E.Span := F (Data, Source, "envelope_bytes_hex");
   begin
      if not V.Valid_Hex_Field (Data, Encoded, "value") or else not V.Valid_Bytes (Data, Raw_Bytes) then return False; end if;
      declare B : constant E.Bytes := V.Hex_Value (Data, Encoded, "value");
              Offset, Found : E.Count := 0; Item : Line; begin
         while Offset < B'Length loop
            Next_Line (B, Offset, Item);
            if not Item.Valid then return False; end if;
            if Item.Count = 5 and then Plain (B, Item.Parts (1), "FILE") and then
               Path_Hex_Matches (Data, B, Item.Parts (3), Path) then
               if not Same_Raw (B, Item.Parts (5), V.Hex_Text (Data, Raw_Bytes, "value")) then return False; end if;
               Found := Found + 1;
            end if;
         end loop;
         return Found = 1;
      end;
   end Image_Corresponds;
   function Role_Selected
     (Data : L.E.Bytes; Source, Path : L.E.Span; Role : String) return Boolean is
      Encoded : constant E.Span := F (Data, Source, "envelope_bytes_hex");
   begin
      if not V.Valid_Hex_Field (Data, Encoded, "value") then return False; end if;
      declare B : constant E.Bytes := V.Hex_Value (Data, Encoded, "value");
              Offset, Found : E.Count := 0; Item : Line; begin
         if not Envelope_Valid (B) then return False; end if;
         while Offset < B'Length loop
            Next_Line (B, Offset, Item);
            if Item.Count = 5 and then Plain (B, Item.Parts (1), "FILE") and then
               Path_Hex_Matches (Data, B, Item.Parts (3), Path) then
               if not Plain (B, Item.Parts (2), Role) then return False; end if;
               Found := Found + 1;
            end if;
         end loop;
         return Found = 1;
      end;
   end Role_Selected;
   function Readbacks_Correspond (Data : L.E.Bytes; Source : L.E.Span) return Boolean is
      Encoded : constant E.Span := F (Data, Source, "envelope_bytes_hex");
      Rows : constant E.Span := F (Data, Source, "file_readbacks");
      use SPARK.Big_Integers;
      function Mode_Matches (B : E.Bytes; Mode : E.Span; Row : E.Span) return Boolean is
         Expected : Valid_Big_Integer := 0;
      begin
         for I in E.Count range 1 .. Mode.Length loop
            if B (Mode.First + I - 1) not in Character'Pos ('0') .. Character'Pos ('7') then return False; end if;
            Expected := Expected * 8 + To_Big_Integer (Integer (B (Mode.First + I - 1)) - Character'Pos ('0'));
         end loop;
         return V.Is_Integer (Data, F (Data, F (Data, Row, "held_before"), "mode")) and then
           Worldline.Custody_V2_Root_Evidence.Number (Data, F (Data, F (Data, Row, "held_before"), "mode")) = 32_768 + Expected;
      end Mode_Matches;
      function Stable (Row : E.Span) return Boolean is
         Before : constant E.Span := F (Data, Row, "held_before");
      begin
         for K in 1 .. 3 loop
            declare After : constant E.Span := F (Data, Row, (case K is when 1 => "named_before",
              when 2 => "held_after", when 3 => "named_after")); begin
               for N in 1 .. 9 loop
                  declare Name : constant String := (case N is when 1 => "device", when 2 => "inode",
                    when 3 => "mode", when 4 => "uid", when 5 => "gid", when 6 => "nlink",
                    when 7 => "size", when 8 => "mtime_ns", when 9 => "ctime_ns"); begin
                     if not V.Is_Integer (Data, F (Data, Before, Name)) or else
                        not S.A.Same_Encoding (Data, F (Data, Before, Name), F (Data, After, Name)) then return False; end if;
                  end;
               end loop;
            end;
         end loop;
         return Worldline.Custody_V2_Requester_Join.Integer_Is (Data, F (Data, Before, "uid"), 0) and then
           Worldline.Custody_V2_Root_Evidence.Number (Data, F (Data, Before, "mode")) / 4_096 = 8 and then
           Worldline.Custody_V2_Requester_Join.Integer_Is (Data, F (Data, Before, "nlink"), 1);
      end Stable;
   begin
      if not V.Valid_Hex_Field (Data, Encoded, "value") or else not V.Is_Sequence (Data, Rows) then return False; end if;
      declare B : constant E.Bytes := V.Hex_Value (Data, Encoded, "value");
              Offset, Files, Envelopes : E.Count := 0; Item : Line; begin
         if not Envelope_Valid (B) then return False; end if;
         while Offset < B'Length loop
            Next_Line (B, Offset, Item);
            if not Item.Valid then return False; end if;
            if Item.Count = 5 and then Plain (B, Item.Parts (1), "FILE") then
               Files := Files + 1;
               declare Found : E.Count := 0; begin
                  for I in E.Count range 1 .. V.Count (Data, Rows) loop
                     declare Row : constant E.Span := V.Element (Data, Rows, I - 1); begin
                        if Path_Hex_Matches (Data, B, Item.Parts (3), F (Data, Row, "path")) then
                           if not Stable (Row) or else not Mode_Matches (B, Item.Parts (4), Row) or else
                              not Hex_Text (Data, B, Item.Parts (5), F (Data, Row, "raw_hex")) then return False; end if;
                           Found := Found + 1;
                        end if;
                     end;
                  end loop;
                  if Found /= 1 then return False; end if;
               end;
            end if;
         end loop;
         for I in E.Count range 1 .. V.Count (Data, Rows) loop
            declare Row : constant E.Span := V.Element (Data, Rows, I - 1); begin
               if S.A.Same_Encoding (Data, F (Data, Row, "path"), F (Data, Source, "envelope_path")) then
                  if not Stable (Row) or else not V.Valid_Hex_Field (Data, F (Data, Row, "raw_hex"), "value") or else
                     (Worldline.Custody_V2_Root_Evidence.Number (Data, F (Data, F (Data, Row, "held_before"), "mode")) mod 64) /= 0 or else
                     V.Hex_Value (Data, F (Data, Row, "raw_hex"), "value") /= B then return False; end if;
                  Envelopes := Envelopes + 1;
               end if;
            end;
         end loop;
         return Envelopes = 1 and then Files < E.Count'Last and then V.Count (Data, Rows) = Files + 1;
      end;
   end Readbacks_Correspond;
   function File_Identity_Corresponds
     (Data : L.E.Bytes; Source, Path, Identity : L.E.Span) return Boolean is
      Rows : constant E.Span := F (Data, Source, "file_readbacks");
      Found : E.Count := 0;
   begin
      if not Readbacks_Correspond (Data, Source) or else
         S.A.Same_Encoding (Data, Path, F (Data, Source, "envelope_path")) then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Rows) loop
         declare Row : constant E.Span := V.Element (Data, Rows, I - 1); begin
            if S.A.Same_Encoding (Data, F (Data, Row, "path"), Path) then
               for K in 1 .. 9 loop
                  declare Name : constant String := (case K is when 1 => "device", when 2 => "inode",
                    when 3 => "mode", when 4 => "uid", when 5 => "gid", when 6 => "nlink",
                    when 7 => "size", when 8 => "mtime_ns", when others => "ctime_ns"); begin
                     if not V.Is_Integer (Data, F (Data, Identity, Name)) or else
                       not S.A.Same_Encoding (Data, F (Data, Identity, Name),
                         F (Data, F (Data, Row, "held_before"), Name)) then return False; end if;
                  end;
               end loop;
               Found := Found + 1;
            end if;
         end;
      end loop;
      return Found = 1;
   end File_Identity_Corresponds;
   function Unselected_Path
     (Data : L.E.Bytes; Source, Path : L.E.Span) return Boolean is
      Encoded : constant E.Span := F (Data, Source, "envelope_bytes_hex");
   begin
      if not V.Valid_Text (Data, Path) or else not V.Valid_Hex_Field (Data, Encoded, "value") then return False; end if;
      declare B : constant E.Bytes := V.Hex_Value (Data, Encoded, "value");
              Offset : E.Count := 0;
              Item : Line; begin
         if not Envelope_Valid (B) then return False; end if;
         while Offset < B'Length loop
            Next_Line (B, Offset, Item);
            if not Item.Valid then return False; end if;
            if Item.Count = 5 and then Plain (B, Item.Parts (1), "FILE") then
               if Path_Hex_Matches (Data, B, Item.Parts (3), Path) then return False; end if;
            elsif Item.Count = 2 and then Plain (B, Item.Parts (1), "ABSENT") then
               if Path_Hex_Matches (Data, B, Item.Parts (2), Path) then return False; end if;
            end if;
         end loop;
         return True;
      end;
   end Unselected_Path;
end Worldline.Startup_Source_Custody;
