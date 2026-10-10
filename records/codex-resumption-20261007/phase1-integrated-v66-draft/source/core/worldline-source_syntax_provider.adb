with Worldline.Producer_Values;
with Worldline.Producer_Bytes;
with Worldline.Report_Custody_Native;
with Worldline.Source_Syntax_Reference;
package body Worldline.Source_Syntax_Provider with SPARK_Mode is
   package V renames Worldline.Producer_Values;
   package B renames Worldline.Producer_Bytes;
   use type V.Value_Kind;
   function Image (N : Natural) return String is
      S : constant String := Natural'Image (N);
   begin return S (S'First + 1 .. S'Last); end Image;
   function Project (Original_Result, Parser_Declaration, Raw_Capsule : String)
      return Parsed_Syntax is
      D : String renames Raw_Capsule;
      Root : constant V.Node := V.Parse (D);
      Original : constant V.Node := V.Parse (Original_Result);
      Decl : constant V.Node := V.Parse (Parser_Declaration);
      function F (P : V.Node; K : String) return V.Node is (V.Field (D, P, K));
      function E (P : V.Node; I : Positive) return V.Node is (V.Element (D, P, I));
      function S (P : V.Node; K : String) return String is (V.Text (D, F (P, K)));
      function N (P : V.Node; K : String) return String is (V.Decimal (D, F (P, K)));
      function Same (L, R : V.Node) return Boolean is (V.Equal (D, L, D, R));
      function Leaf (P : V.Node) return B.Decoded is
      begin
         if P.Form /= V.Object_Value or else not V.Is_Text (D, F (P, "encoding"), "base64") or else F (P, "payload").Form /= V.String_Value then return (0, False, ""); end if;
         return B.Base64 (S (P, "payload"));
      end Leaf;
      Historical : constant V.Node := F (Root, "historicalAudit");
      Parser : constant V.Node := F (Root, "parserSource");
      Parser_Read : constant V.Node := F (Parser, "read");
      Helper : constant B.Decoded := Leaf (F (Parser_Read, "bytes"));
      Prior : constant V.Node := F (Root, "priorExpectedDeclaration");
      Approved : constant B.Decoded := Leaf (F (Prior, "parserBytes"));
      Candidate_Digest : constant String := B.Digest (Original_Result);
      Helper_Digest : constant String := B.Digest (Helper.Data);
      function Modulo (Text : String; Modulus : Positive) return Natural is
         Remainder : Natural := 0;
      begin
         for C of Text loop
            if C not in '0' .. '9' then return Modulus; end if;
            Remainder := (Remainder * 10 + Character'Pos (C) - Character'Pos ('0')) mod Modulus;
         end loop;
         return Remainder;
      end Modulo;
      function Held_Read (Read : V.Node; Content : B.Decoded) return Boolean is
         File : constant V.Node := F (Read, "file");
         Before : constant V.Node := F (File, "before");
         Directories : constant V.Node := F (Read, "directories");
         function Path_Joined return Boolean is
            Text : constant String := S (Read, "path");
            Offset : Natural := 1;
         begin
            if Text'Length = 0 or else Text (Text'First) /= '/' then return False; end if;
            for I in 2 .. V.Count (D, Directories) loop
               declare Component : constant String := S (E (Directories, I), "component");
               begin
                  if Component'Length = 0 or else Component in "." | ".." or else
                    Offset >= Text'Length or else Component'Length > Text'Length - Offset - 1 or else
                    Text (Text'First + Offset .. Text'First + Offset + Component'Length - 1) /= Component or else
                    Text (Text'First + Offset + Component'Length) /= '/' then return False; end if;
                  Offset := Offset + Component'Length + 1;
               end;
            end loop;
            return Offset < Text'Length and then Text (Text'First + Offset .. Text'Last) = S (File, "component");
         end Path_Joined;
      begin
         if not Content.Valid or else not V.Is_True (D, F (Read, "readReturned")) or else
           not V.Is_True (D, F (Read, "readReachedEof")) or else F (Read, "exception").Form /= V.Null_Value or else
           not V.Nonnegative (D, F (File, "descriptor")) or else
           not V.Is_True (D, F (File, "closed")) or else F (File, "closeException").Form /= V.Null_Value or else
           Before.Form /= V.Array_Value or else V.Count (D, Before) /= 9 or else
           Modulo (V.Decimal (D, E (Before, 3)), 65_536) / 4096 /= 8 or else
           V.Decimal (D, E (Before, 6)) /= Image (Content.Length) or else V.Decimal (D, E (Before, 9)) /= "1" or else
           not Same (Before, F (File, "after")) or else not Same (Before, F (File, "edgeAfter")) or else
           Directories.Form /= V.Array_Value or else V.Count (D, Directories) = 0 or else
           not Path_Joined then return False; end if;
         for I in 1 .. V.Count (D, Directories) loop
            declare Row : constant V.Node := E (Directories, I);
            begin
               if not V.Nonnegative (D, F (Row, "descriptor")) or else
                 Modulo (N (F (Row, "before"), "mode"), 65_536) / 4096 /= 4 or else
                 not V.Is_True (D, F (Row, "closed")) or else F (Row, "closeException").Form /= V.Null_Value or else
                 not Same (F (Row, "before"), F (Row, "after")) or else
                 (I = 1 and then (S (Row, "component") /= "/" or else F (Row, "edgeAfter").Form /= V.Null_Value)) or else
                 (I > 1 and then not Same (F (Row, "before"), F (Row, "edgeAfter"))) then return False; end if;
            end;
         end loop;
         return True;
      end Held_Read;
      function Helper_Read_Valid return Boolean is
        (Helper.Valid and then Approved.Valid and then Helper.Data = Approved.Data and then
         Worldline.Source_Syntax_Reference.Matches (Helper.Data) and then
         S (Parser, "sha256") = Helper_Digest and then
         S (Parser_Read, "path") = S (Parser, "path") and then Held_Read (Parser_Read, Helper));
      function Phase_Valid (Phase, Artifact_Data : String) return Boolean is
         A : constant V.Node := V.Parse (Artifact_Data);
         Row : constant V.Node := F (F (Root, "phases"), Phase);
         Request : constant V.Node := F (Row, "request");
         Historical_Phase : constant V.Node := F (Historical, Phase);
         Result : constant V.Node := F (Row, "result");
         Capture : constant V.Node := F (Result, "protectedProviderCapture");
         Leases : constant V.Node := F (Capture, "sourceLeases");
         Saved : constant V.Node := F (Historical_Phase, "files");
         Profile : constant V.Node := V.Field (Artifact_Data, A, "profile");
         Files : constant V.Node := V.Field (Artifact_Data, Profile, "files");
         Input : constant V.Node := V.Field (Artifact_Data, A, "input");
         Sources : constant V.Node := V.Field (Artifact_Data, Input, "sourceReads");
         function AF (P : V.Node; K : String) return V.Node is (V.Field (Artifact_Data, P, K));
         function AE (P : V.Node; I : Positive) return V.Node is (V.Element (Artifact_Data, P, I));
         Invocation : constant V.Node := F (Request, "invocation");
         Binding : constant V.Node := F (Request, "privateReportBinding");
         Declared_Report : constant V.Node := V.Field
           (Parser_Declaration, V.Field (Parser_Declaration, Decl, "phaseReports"), Phase);
         Binding_Read : constant V.Node := F (Row, "privateBindingRead");
         Binding_Bytes : constant B.Decoded := Leaf (F (Binding_Read, "bytes"));
         Read_Binding : constant V.Node := V.Parse (Binding_Bytes.Data);
         Directory_Reads : constant V.Node := AF (Input, "directoryReads");
         Binding_Directories : constant V.Node := F (Binding_Read, "directories");
         function Report_Directory_Joined return Boolean is
            Count : constant Natural := V.Count (D, Binding_Directories);
            Parent : constant V.Node := F (E (Binding_Directories, (if Count = 0 then 1 else Count)), "before");
            Report_Directory : constant V.Node := F (F (Capture, "expected"), "reportDirectory");
         begin
            if Count = 0 or else Parent.Form /= V.Object_Value or else Report_Directory.Form /= V.Object_Value then return False; end if;
            for I in 1 .. 5 loop
               declare Key : constant String := (case I is when 1 => "device", when 2 => "inode",
                 when 3 => "mode", when 4 => "uid", when others => "gid");
               begin
                  if not V.Nonnegative (D, F (Parent, Key)) or else not Same (F (Parent, Key), F (Report_Directory, Key)) then return False; end if;
               end;
            end loop;
            return True;
         end Report_Directory_Joined;
         Helper_Seen : Boolean := False;
      begin
         if not V.Is_Text (Artifact_Data, AF (A, "schema"), "worldline-protected-source-syntax-artifact-v1") or else
           not Worldline.Report_Custody_Native.Captured (V.Slice (D, F (Request, "invocation")), V.Slice (D, F (Row, "acquisitions")), V.Slice (D, Result)) or else
           not V.Equal (D, F (Request, "invocation"), Parser_Declaration, V.Field (Parser_Declaration, V.Field (Parser_Declaration, Decl, "phaseInvocations"), Phase)) or else
           not V.Equal (D, Binding, Parser_Declaration, V.Field (Parser_Declaration, Declared_Report, "binding")) or else
           not V.Nonempty_Text (D, F (Invocation, "invocationId")) or else
           S (Invocation, "phase") /= Phase or else S (Request, "phase") /= Phase or else
           S (Invocation, "checkId") /= "worldline-source-syntax-phase" or else
           S (Invocation, "candidateScope") /= Candidate_Digest or else
           Binding.Form /= V.Object_Value or else V.Count (D, Binding) /= 4 or else
           S (Binding, "runId") /= S (Invocation, "invocationId") or else
           S (Binding, "checkId") /= "worldline-source-syntax-phase" or else
           S (Binding, "candidateIdentity") /= Candidate_Digest or else
           S (Binding, "verifierIdentity") /= Helper_Digest or else
           S (Binding_Read, "path") /= V.Text (Parser_Declaration, V.Field (Parser_Declaration, Declared_Report, "directory")) & "/.binding" or else
           not Held_Read (Binding_Read, Binding_Bytes) or else
           not Report_Directory_Joined or else
           not V.Equal (D, Binding, Binding_Bytes.Data, Read_Binding) or else
           not Same (F (Request, "historicalRoster"), Saved) or else not Same (F (Request, "historicalRuntime"), F (Historical_Phase, "runtime")) or else
           not V.Equal (D, F (Historical_Phase, "runtime"), Artifact_Data, AF (Profile, "runtime")) or else
           not V.Equal (D, F (Historical_Phase, "runtime"), Parser_Declaration, V.Field (Parser_Declaration, Decl, "runtime")) or else
           not V.Equal (D, F (Historical_Phase, "directories"), Artifact_Data, AF (Input, "directories")) or else
           V.Decimal (Artifact_Data, AF (AF (Input, "root"), "closeReturn")) /= "0" then return False; end if;
         if V.Decimal (Artifact_Data, AF (AF (Input, "root"), "closeErrno")) /= "0" or else Saved.Form /= V.Array_Value or else Files.Form /= V.Array_Value or else Sources.Form /= V.Array_Value or else V.Count (D, Saved) /= V.Count (Artifact_Data, Files) or else V.Count (D, Saved) /= V.Count (Artifact_Data, Sources) then return False; end if;
         declare Dirs : constant V.Node := F (Historical_Phase, "directories");
            Dir_Count : constant Natural := V.Count (D, Dirs);
         begin
            if Dirs.Form /= V.Array_Value or else Dir_Count = 0 or else Dir_Count > 100_000 or else
              Directory_Reads.Form /= V.Array_Value or else V.Count (Artifact_Data, Directory_Reads) /= 2 * Dir_Count - 1 then return False; end if;
            for I in 1 .. Dir_Count loop
               declare Path : constant String := V.Text (D, E (Dirs, I));
                  Seen, Closed : Boolean := False;
                  Descriptor : V.Node := V.No_Node;
               begin
                  for J in 1 .. V.Count (Artifact_Data, Directory_Reads) loop
                     declare Row : constant V.Node := AE (Directory_Reads, J);
                        Stat : constant V.Node := AF (Row, "before");
                     begin
                        if V.Is_Text (Artifact_Data, AF (Row, "path"), (if Path = "" then "" else Path & "/")) and then
                          Stat.Form = V.Object_Value then
                           if Seen or else not V.Nonnegative (Artifact_Data, AF (Row, "fd")) or else
                             Modulo (V.Decimal (Artifact_Data, AF (Stat, "mode")), 65_536) / 4096 /= 4 or else
                             not V.Equal (Artifact_Data, Stat, Artifact_Data, AF (Row, "after")) or else
                             AF (Row, "names").Form /= V.Array_Value or else
                             not V.Equal (Artifact_Data, AF (Row, "names"), Artifact_Data, AF (Row, "afterNames")) then return False; end if;
                           Seen := True; Descriptor := AF (Row, "fd");
                        end if;
                     end;
                  end loop;
                  if not Seen then return False; end if;
                  if Path = "" then
                     Closed := V.Equal (Artifact_Data, Descriptor, Artifact_Data, AF (AF (Input, "root"), "fd"));
                  else
                     for J in 1 .. V.Count (Artifact_Data, Directory_Reads) loop
                        declare Row : constant V.Node := AE (Directory_Reads, J);
                        begin
                           if V.Is_Text (Artifact_Data, AF (Row, "path"), Path) and then AF (Row, "before").Form = V.Missing then
                              if Closed or else not V.Equal (Artifact_Data, Descriptor, Artifact_Data, AF (Row, "fd")) or else
                                not V.Equal (Artifact_Data, AF (Row, "openReturn"), Artifact_Data, Descriptor) or else
                                V.Decimal (Artifact_Data, AF (Row, "openErrno")) /= "0" or else
                                V.Decimal (Artifact_Data, AF (Row, "closeReturn")) /= "0" or else
                                V.Decimal (Artifact_Data, AF (Row, "closeErrno")) /= "0" then return False; end if;
                              Closed := True;
                           end if;
                        end;
                     end loop;
                  end if;
                  if not Closed then return False; end if;
               end;
            end loop;
         end;
         for I in 1 .. V.Count (D, Leases) loop
            declare Lease : constant V.Node := E (Leases, I); Bytes : constant B.Decoded := Leaf (F (Lease, "bytes"));
            begin
               if S (Lease, "member") = "protected_syntax_helper.py" and then
                 S (F (Lease, "binding"), "path") = "/run/worldline-verifiers/protected_syntax_helper.py" then
                  if Helper_Seen or else not Bytes.Valid or else Bytes.Data /= Helper.Data or else
                    S (F (Lease, "binding"), "sha256") /= Helper_Digest or else
                    N (F (Lease, "binding"), "byteCount") /= Image (Helper.Length) then return False; end if;
                  Helper_Seen := True;
               end if;
            end;
         end loop;
         if not Helper_Seen then return False; end if;
         for I in 1 .. V.Count (D, Saved) loop
            declare Old : constant V.Node := E (Saved, I); Path : constant String := S (Old, "path"); Content : constant B.Decoded := B.Base64 (S (Old, "payloadB64")); Found, Read_Seen, Lease_Seen : Boolean := False;
            begin
               if not Content.Valid then return False; end if;
               for J in 1 .. V.Count (Artifact_Data, Files) loop
                  declare File : constant V.Node := AE (Files, J);
                  begin
                     if V.Is_Text (Artifact_Data, AF (File, "path"), Path) then
                        if Found or else not V.Equal (D, F (Old, "payloadB64"), Artifact_Data, AF (File, "payloadB64")) or else AF (File, "exception").Form /= V.Null_Value then return False; end if; Found := True;
                     end if;
                  end;
               end loop;
               for J in 1 .. V.Count (Artifact_Data, Sources) loop
                  declare Source : constant V.Node := AE (Sources, J);
                     Bytes : constant B.Decoded := B.Base64 (V.Text (Artifact_Data, AF (AF (Source, "bytes"), "payload")));
                     Stat : constant V.Node := AF (Source, "before");
                  begin
                     if V.Is_Text (Artifact_Data, AF (Source, "path"), Path) then
                        if Read_Seen or else not Bytes.Valid or else Bytes.Data /= Content.Data or else
                          Modulo (V.Decimal (Artifact_Data, AF (Stat, "mode")), 65_536) / 4096 /= 8 or else
                          V.Decimal (Artifact_Data, AF (Stat, "nlink")) /= "1" or else
                          not V.Equal (Artifact_Data, Stat, Artifact_Data, AF (Source, "after")) or else not V.Equal (Artifact_Data, Stat, Artifact_Data, AF (Source, "named")) or else not V.Equal (Artifact_Data, Stat, Artifact_Data, AF (Source, "edgeAfter")) or else
                          V.Decimal (Artifact_Data, AF (Source, "openErrno")) /= "0" or else
                          not V.Equal (Artifact_Data, AF (Source, "openReturn"), Artifact_Data, AF (Source, "fd")) or else
                          not V.Nonnegative (Artifact_Data, AF (Source, "fd")) or else
                          not V.Is_Text (Artifact_Data, AF (AF (Source, "bytes"), "encoding"), "base64") or else
                          V.Decimal (Artifact_Data, AF (Stat, "size")) /= Image (Content.Length) or else
                          V.Decimal (Artifact_Data, AF (Source, "closeReturn")) /= "0" or else V.Decimal (Artifact_Data, AF (Source, "closeErrno")) /= "0" then return False; end if;
                        declare Parent_Seen : Boolean := False;
                        begin
                           for K in 1 .. V.Count (Artifact_Data, Directory_Reads) loop
                              declare Directory : constant V.Node := AE (Directory_Reads, K);
                                 Prefix : constant String := V.Text (Artifact_Data, AF (Directory, "path"));
                              begin
                                 if AF (Directory, "before").Form = V.Object_Value and then
                                   V.Equal (Artifact_Data, AF (Directory, "fd"), Artifact_Data, AF (Source, "parentFd")) and then
                                   Path'Length > Prefix'Length and then
                                   Path (Path'First .. Path'First + Prefix'Length - 1) = Prefix then
                                    declare Immediate : Boolean := True;
                                    begin
                                       for C of Path (Path'First + Prefix'Length .. Path'Last) loop
                                          if C = '/' then Immediate := False; end if;
                                       end loop;
                                       if Immediate then
                                          if Parent_Seen then return False; end if;
                                          Parent_Seen := True;
                                       end if;
                                    end;
                                 end if;
                              end;
                           end loop;
                           if not Parent_Seen then return False; end if;
                        end;
                        declare Rows : constant V.Node := AF (Source, "reads"); Offset : Natural := 0; EOF : Boolean := False;
                        begin
                           if Rows.Form /= V.Array_Value then return False; end if;
                           for K in 1 .. V.Count (Artifact_Data, Rows) loop
                              declare RR : constant V.Node := AE (Rows, K); Chunk : constant B.Decoded := B.Base64 (V.Text (Artifact_Data, AF (AF (RR, "bytes"), "payload")));
                              begin
                                 if EOF or else not Chunk.Valid or else not V.Is_Text (Artifact_Data, AF (AF (RR, "bytes"), "encoding"), "base64") or else
                                   not V.Equal (Artifact_Data, AF (RR, "fd"), Artifact_Data, AF (Source, "fd")) or else V.Decimal (Artifact_Data, AF (RR, "offset")) /= Image (Offset) or else V.Decimal (Artifact_Data, AF (RR, "return")) /= Image (Chunk.Length) or else V.Decimal (Artifact_Data, AF (RR, "errno")) /= "0" or else Chunk.Length > Content.Length - Offset then return False; end if;
                                 if Chunk.Length > 0 and then Chunk.Data /= Content.Data (Offset + 1 .. Offset + Chunk.Length) then return False; end if;
                                 Offset := Offset + Chunk.Length; EOF := Chunk.Length = 0;
                              end;
                           end loop;
                           if not EOF or else Offset /= Content.Length then return False; end if;
                        end;
                        for K in 1 .. V.Count (D, Leases) loop
                           declare Lease : constant V.Node := E (Leases, K); Binding : constant V.Node := F (Lease, "binding"); Lease_Bytes : constant B.Decoded := Leaf (F (Lease, "bytes"));
                           begin
                              if S (Binding, "kind") = "readonly-input" and then S (Binding, "historicalPath") = Path and then S (Binding, "path") = "/logical/worldline-syntax-input/" & Path then
                                 if Lease_Seen or else not Lease_Bytes.Valid or else Lease_Bytes.Data /= Content.Data or else not V.Equal (D, F (Lease, "before"), Artifact_Data, Stat) then return False; end if; Lease_Seen := True;
                              end if;
                           end;
                        end loop;
                        Read_Seen := True;
                     end if;
                  end;
               end loop;
               if not Found or else not Read_Seen or else not Lease_Seen then return False; end if;
            end;
         end loop;
         return True;
      end Phase_Valid;
      Before : constant V.Node := F (F (Root, "phases"), "before");
      After : constant V.Node := F (F (Root, "phases"), "after");
      Before_Bytes : constant B.Decoded := Leaf (F (Before, "artifact"));
      After_Bytes : constant B.Decoded := Leaf (F (After, "artifact"));
   begin
      if Root.Form /= V.Object_Value or else Decl.Form /= V.Object_Value or else Original.Form /= V.Object_Value or else
        S (Root, "schema") /= "worldline-protected-source-syntax-v1" or else not V.Equal (D, Prior, Parser_Declaration, Decl) or else
        not V.Equal (D, Historical, Original_Result, V.Field (Original_Result, Original, "examinerAudit")) or else not Helper_Read_Valid or else
        not Before_Bytes.Valid or else not After_Bytes.Valid or else
        S (F (F (Before, "request"), "invocation"), "invocationId") =
          S (F (F (After, "request"), "invocation"), "invocationId") then
         return (0, False, "");
      end if;
      if not Same (F (Before, "artifact"), F (F (F (F (F (Before, "result"), "protectedProviderCapture"), "report"), "sealed"), "bytes")) or else
        not Same (F (After, "artifact"), F (F (F (F (F (After, "result"), "protectedProviderCapture"), "report"), "sealed"), "bytes")) or else
        S (Before, "artifactSha256") /= B.Digest (Before_Bytes.Data) or else S (After, "artifactSha256") /= B.Digest (After_Bytes.Data) or else
        not Phase_Valid ("before", Before_Bytes.Data) or else not Phase_Valid ("after", After_Bytes.Data) then return (0, False, ""); end if;
      declare
         BP : constant V.Node := V.Field (Before_Bytes.Data, V.Parse (Before_Bytes.Data), "profile");
         AP : constant V.Node := V.Field (After_Bytes.Data, V.Parse (After_Bytes.Data), "profile");
         AST : constant String := "{""runtime"":" & V.Slice (Before_Bytes.Data, V.Field (Before_Bytes.Data, BP, "runtime")) &
           ",""before"":" & V.Slice (Before_Bytes.Data, V.Field (Before_Bytes.Data, BP, "files")) &
           ",""after"":" & V.Slice (After_Bytes.Data, V.Field (After_Bytes.Data, AP, "files")) & "}";
      begin return (AST'Length, True, AST); end;
   end Project;
   function Authentic
     (Original_Result, Parser_Declaration, Raw_Capsule, Native_AST : String)
      return Boolean is
      Parsed : constant Parsed_Syntax := Project (Original_Result, Parser_Declaration, Raw_Capsule);
   begin
      return Parsed.Valid and then V.Equal (Parsed.AST, V.Parse (Parsed.AST), Native_AST, V.Parse (Native_AST));
   end Authentic;
   function Original_Joined (Result_Record : String) return Boolean is
      Root : constant V.Node := V.Parse (Result_Record);
      Original_Field : constant V.Node := V.Field (Result_Record, Root, "sourceParserOriginalResult");
      Original_Data : constant String := V.Text (Result_Record, Original_Field);
      Original : constant V.Node := V.Parse (Original_Data);
      function Adjunct (Key : String) return Boolean is
        (Key in "nativeSourceAST" | "sourceParserDeclaration" | "sourceParserCapture" | "sourceParserOriginalResult");
   begin
      if Root.Form /= V.Object_Value or else Original_Field.Form /= V.String_Value or else
        Original.Form /= V.Object_Value or else not V.Duplicate_Free (Result_Record) or else
        not V.Duplicate_Free (Original_Data) or else V.Count (Result_Record, Root) /= V.Count (Original_Data, Original) + 4 then return False; end if;
      for I in 1 .. V.Count (Original_Data, Original) loop
         declare Key : constant String := V.Member_Name (Original_Data, Original, I);
         begin
            if Adjunct (Key) or else not V.Equal (Original_Data, V.Field (Original_Data, Original, Key),
              Result_Record, V.Field (Result_Record, Root, Key)) then return False; end if;
         end;
      end loop;
      for I in 1 .. V.Count (Result_Record, Root) loop
         declare Key : constant String := V.Member_Name (Result_Record, Root, I);
         begin
            if not Adjunct (Key) and then not V.Present (V.Field (Original_Data, Original, Key)) then return False; end if;
         end;
      end loop;
      return V.Field (Result_Record, Root, "nativeSourceAST").Form = V.Object_Value and then
        V.Field (Result_Record, Root, "sourceParserDeclaration").Form = V.Object_Value and then
        V.Field (Result_Record, Root, "sourceParserCapture").Form = V.Object_Value;
   end Original_Joined;
   function Authentic (Result_Record : String) return Boolean is
      Root : constant V.Node := V.Parse (Result_Record);
   begin
      return Original_Joined (Result_Record) and then Authentic
        (V.Text (Result_Record, V.Field (Result_Record, Root, "sourceParserOriginalResult")),
         V.Slice (Result_Record, V.Field (Result_Record, Root, "sourceParserDeclaration")),
         V.Slice (Result_Record, V.Field (Result_Record, Root, "sourceParserCapture")),
         V.Slice (Result_Record, V.Field (Result_Record, Root, "nativeSourceAST")));
   end Authentic;
end Worldline.Source_Syntax_Provider;
