with Worldline.Producer_Values;
with Worldline.Producer_Bytes;
with Worldline.Source_Syntax;
with Worldline.Source_Syntax_Provider;
package body Worldline.Source_Audit_Native with SPARK_Mode is
   package V renames Worldline.Producer_Values;
   package B renames Worldline.Producer_Bytes;
   use type V.Value_Kind;

   --  True exactly when Prefix (Value, <head of length Width>) raised in the
   --  original (Value'First + Width passes Integer'Last: Value ends there).
   function At_End (Value : String; Width : Natural) return Boolean is
     (Width > 0 and then Value'Length = Width and then Value'Last = Integer'Last)
     with Global => null;
   function Prefix (Value, Head : String) return Boolean is
     (Value'Length >= Head'Length and then Value (Value'First .. Value'First + Head'Length - 1) = Head)
     with Pre => Head'Length > 0 and then not At_End (Value, Head'Length);
   --  The original Contains, with Overflowed marking exactly the point where
   --  it raised (a slice bound past Integer'Last); each caller refuses there.
   type Search_Result is (Absent, Present, Overflowed);
   function Search (Value, Needle : String) return Search_Result
     with Global => null
   is
   begin
      if Needle'Length > Value'Length then return Absent; end if;
      for I in 0 .. Value'Length - Needle'Length loop
         if Long_Long_Integer (Value'First) + Long_Long_Integer (I) + Long_Long_Integer (Needle'Length) > Long_Long_Integer (Integer'Last)
           or else Long_Long_Integer (Value'First) + Long_Long_Integer (I) + Long_Long_Integer (Needle'Length) - 1 < Long_Long_Integer (Integer'First)
         then return Overflowed; end if;
         if Value (Value'First + I .. Value'First + I + Needle'Length - 1) = Needle then return Present; end if;
      end loop;
      return Absent;
   end Search;
   function Head (Name : String) return String is
   begin
      for I in Name'Range loop
         if Name (I) = '.' then return Name (Name'First .. I - 1); end if;
      end loop;
      return Name;
   end Head;
   function Tail (Name : String) return String
     with Pre => Name'Length = 0 or else Name'Last < Integer'Last or else Name (Name'Last) /= '.'
   is
   begin
      for I in reverse Name'Range loop
         if Name (I) = '.' then return Name (I + 1 .. Name'Last); end if;
      end loop;
      return Name;
   end Tail;
   function Denied_Import (Name : String) return Boolean is
      List : constant String := "|importlib|runpy|pkgutil|zipimport|site|pickle|shelve|marshal|code|codeop|timeit|doctest|pdb|bdb|trace|profile|cProfile|ctypes|_ctypes|subprocess|multiprocessing|pty|unittest|logging.config|http.server|webbrowser|builtins|";
   begin
      --  The original raised Constraint_Error exactly here; deny that name.
      if Head (Name)'Length > Natural'Last - 2 then return True; end if;
      if Search (List, "|" & Head (Name) & "|") /= Absent then return True; end if;
      if Name = "logging.config" then return True; end if;
      --  At_End: the original raised in Prefix exactly there; deny.
      if At_End (Name, 15) then return True; end if;
      if Prefix (Name, "logging.config.") then return True; end if;
      if Name = "http.server" then return True; end if;
      if At_End (Name, 12) then return True; end if;
      return Prefix (Name, "http.server.");
   end Denied_Import;
   function Denied_Name (Name : String) return Boolean is
     (Name in "exec" | "eval" | "compile" | "__import__" | "breakpoint" | "__builtins__");
   --  At_End and the Tail guard mark exactly where the original raised; deny.
   function Denied_Attribute (Name : String) return Boolean is
   begin
      if At_End (Name, 3) then return True; end if;
      if Prefix (Name, "os.") then
         declare
            Attribute : constant String := Name (Name'First + 3 .. Name'Last);
         begin
            if Attribute in "system" | "popen" | "fork" | "forkpty" | "startfile" then return True; end if;
            if At_End (Attribute, 4) then return True; end if;
            if Prefix (Attribute, "exec") then return True; end if;
            if At_End (Attribute, 5) then return True; end if;
            if Prefix (Attribute, "spawn") then return True; end if;
            if At_End (Attribute, 11) then return True; end if;
            return Prefix (Attribute, "posix_spawn");
         end;
      end if;
      if Name = "concurrent.futures.ProcessPoolExecutor" then return True; end if;
      if At_End (Name, 8) then return True; end if;
      if not Prefix (Name, "sqlite3.") then return False; end if;
      if Name (Name'Last) = '.' and then Name'Last = Integer'Last then return True; end if;
      return Tail (Name) in "enable_load_extension" | "load_extension";
   end Denied_Attribute;
   --  At_End marks exactly where the original raised in Prefix; a state name.
   function State_Name (Name : String; Descendants : Boolean) return Boolean is
   begin
      if Name in "sys.path" | "sys.meta_path" | "sys.path_hooks" | "sys.path_importer_cache" | "sys.modules" then return True; end if;
      if not Descendants then return False; end if;
      if At_End (Name, 9) then return True; end if;
      if Prefix (Name, "sys.path.") then return True; end if;
      if At_End (Name, 14) then return True; end if;
      if Prefix (Name, "sys.meta_path.") then return True; end if;
      if At_End (Name, 15) then return True; end if;
      if Prefix (Name, "sys.path_hooks.") then return True; end if;
      if At_End (Name, 24) then return True; end if;
      if Prefix (Name, "sys.path_importer_cache.") then return True; end if;
      if At_End (Name, 12) then return True; end if;
      return Prefix (Name, "sys.modules.");
   end State_Name;
   function Mutator (Name : String) return Boolean is
     (Name in "append" | "extend" | "insert" | "remove" | "pop" | "clear" | "reverse" | "sort" |
      "update" | "setdefault" | "popitem" | "__setitem__" | "__delitem__" | "__iadd__" | "__imul__" | "__ior__" | "__init__");
   function Image (N : Natural) return String
     with Global => null
   is
      S : constant String := Natural'Image (N);
   begin return S (S'First + 1 .. S'Last); end Image;
   --  True exactly when Left & <operands of total length Rest> does not raise:
   --  a non-null left operand keeps its lower bound, a null one yields the rest.
   function Fits (Left : String; Rest : Natural) return Boolean is
     (Rest <= Natural'Last - (if Left'Length = 0 then 0 else Left'Last))
     with Global => null;
   --  The same for Left & <non-null literal of length Middle> & <length Right>.
   function Fits2 (Left : String; Middle, Right : Natural) return Boolean is
     (Middle <= Natural'Last - (if Left'Length = 0 then 0 else Left'Last) and then
      Right <= Natural'Last - (if Left'Length = 0 then 0 else Left'Last) - Middle)
     with Global => null;

   function Canonical (Encoded : String; Value : B.Decoded) return Boolean is
      function Digit (C : Character) return Natural is
      begin
         case C is
            when 'A' .. 'Z' => return Character'Pos (C) - Character'Pos ('A');
            when 'a' .. 'z' => return Character'Pos (C) - Character'Pos ('a') + 26;
            when '0' .. '9' => return Character'Pos (C) - Character'Pos ('0') + 52;
            when '+' => return 62;
            when '/' => return 63;
            when others => return 64;
         end case;
      end Digit;
   begin
      if not Value.Valid or else Value.Length > 268_435_456 or else
        Encoded'Length /= ((Value.Length + 2) / 3) * 4 then return False; end if;
      if Value.Length mod 3 = 1 then
         return Encoded (Encoded'Last - 1 .. Encoded'Last) = "==" and then
           Digit (Encoded (Encoded'Last - 2)) mod 16 = 0;
      elsif Value.Length mod 3 = 2 then
         return Encoded (Encoded'Last) = '=' and then Digit (Encoded (Encoded'Last - 1)) mod 4 = 0;
      end if;
      return Value.Length = 0 or else Encoded (Encoded'Last) /= '=';
   end Canonical;

   function Closure_Clean_Joined (Result_Record, Native_AST : String; Parsed_AST : V.Node) return Boolean
     with Global => null,
       Pre => Native_AST'Length <= Natural'Last - 1 - (if Result_Record'Length = 0 then 0 else Result_Record'Last)
         and then (Parsed_AST.Form = V.Missing or else
           (Parsed_AST.First <= Natural'Last - 1 - Result_Record'Length and then
            Parsed_AST.Last <= Natural'Last - 1 - Result_Record'Length))
   is
      -- Two independent documents share a selector arena, not a rebuilt JSON
      -- root. Every original member remains untouched, including old adjuncts.
      Data : constant String := Result_Record & Character'Val (10) & Native_AST;
      Root : constant V.Node := V.Parse (Result_Record);
      function F (Node : V.Node; Name : String) return V.Node is (V.Field (Data, Node, Name));
      function S (Node : V.Node; Name : String) return String is (V.Text (Data, F (Node, Name)));
      function El (Node : V.Node; Index : Positive) return V.Node is (V.Element (Data, Node, Index));
      Audit : constant V.Node := F (Root, "examinerAudit");
      AST : constant V.Node :=
        (if Parsed_AST.Form = V.Missing then V.No_Node else
         (Parsed_AST.Form, Result_Record'Length + 1 + Parsed_AST.First,
          Result_Record'Length + 1 + Parsed_AST.Last));
      Executed : constant V.Node := F (Root, "executedVerifierSet");
      Members : constant V.Node := F (Executed, "members");
      Argv : constant V.Node := F (Root, "argv");
      Rewrites : constant V.Node := F (Executed, "argvRewrites");
      function Relative (Path : String) return Boolean is
         First : Natural := 0;
         Last : Natural;
      begin
         if Path'Length = 0 or else Path (Path'First) = '/' or else
            (for some C of Path => C = Character'Val (0)) then return False; end if;
         while First < Path'Length loop
            pragma Loop_Variant (Increases => First);
            Last := First;
            while Last < Path'Length and then Path (Path'First + Last) /= '/' loop
               pragma Loop_Invariant (Last in First .. Path'Length - 1); pragma Loop_Variant (Increases => Last);
               Last := Last + 1;
            end loop;
            if Last = First then return False; end if;
            --  The original raised (Path'First + Last) exactly here; refuse.
            if Last = Path'Length and then Path'Last = Integer'Last then return False; end if;
            if Path (Path'First + First .. Path'First + Last - 1) = "." or else
              Path (Path'First + First .. Path'First + Last - 1) = ".." then return False; end if;
            exit when Last = Path'Length;
            First := Last + 1;
            if First = Path'Length then return False; end if;
         end loop;
         return True;
      end Relative;
      function Entry_Name return String is
         Found : V.Node := V.No_Node;
      begin
         if Argv.Form /= V.Array_Value or else V.Count (Data, Argv) < 2 or else
           not V.Is_Text (Data, El (Argv, 1), "/usr/bin/python3") or else Rewrites.Form /= V.Array_Value then return ""; end if;
         for I in 1 .. V.Count (Data, Rewrites) loop
            declare
               Item : constant V.Node := El (Rewrites, I);
            begin
               if V.Equal (Data, F (Item, "from"), Data, El (Argv, 2)) then
                  if V.Present (Found) and then not V.Equal (Data, Found, Data, F (Item, "to")) then return ""; end if;
                  Found := F (Item, "to");
               end if;
            end;
         end loop;
         declare
            Mounted : constant String := V.Text (Data, Found);
            Start : constant String := "/run/worldline-verifiers/";
         begin
            --  At_End: the original raised in Prefix exactly there; refuse.
            if At_End (Mounted, Start'Length) then return ""; end if;
            if not Prefix (Mounted, Start) then return ""; end if;
            return Mounted (Mounted'First + Start'Length .. Mounted'Last);
         end;
      end Entry_Name;
      Entry_Path : constant String := Entry_Name;
      function Parent_Path (Path : String) return String
        with Post => Parent_Path'Result'Length = 0 or else
          (Parent_Path'Result'First = Path'First and then Parent_Path'Result'Last < Path'Last)
      is
      begin
         for I in reverse Path'Range loop
            if Path (I) = '/' then return Path (Path'First .. I - 1); end if;
         end loop;
         return "";
      end Parent_Path;
      function To_Path (Module_Name : String) return String
        with Pre => Module_Name'Length = 0 or else Module_Name'Last < Integer'Last,
          Post => To_Path'Result'First = 1 and then To_Path'Result'Length = Module_Name'Length
      is
         Result : String (1 .. Module_Name'Length);
      begin
         for I in Result'Range loop
            Result (I) := (if Module_Name (Module_Name'First + I - 1) = '.' then '/' else Module_Name (Module_Name'First + I - 1));
         end loop;
         return Result;
      end To_Path;

      function Phase_Clean (Phase : String) return Boolean is
         Observation : constant V.Node := F (Audit, Phase);
         Files : constant V.Node := F (Observation, "files");
         Syntax_Files : constant V.Node := F (AST, Phase);
         Directories : constant V.Node := F (Observation, "directories");
         Runtime : constant V.Node := F (Observation, "runtime");
         Suffixes : constant V.Node := F (Runtime, "extensionSuffixes");
         Standard : constant V.Node := F (Runtime, "stdlibNames");
         File_Count : constant Natural := V.Count (Data, Files);
         type Marks is array (Positive range <>, Natural range <>) of Boolean;
         Pending, Seen : Marks (1 .. File_Count, 0 .. 2) := (others => (others => False));
         Failed : Boolean := False;
         function File_Index (Path : String) return Natural
           with Post => File_Index'Result <= File_Count
         is
         begin
            for I in 1 .. File_Count loop
               if V.Is_Text (Data, F (El (Files, I), "path"), Path) then return I; end if;
            end loop;
            return 0;
         end File_Index;
         function Directory (Path : String) return Boolean is
         begin
            for I in 1 .. V.Count (Data, Directories) loop
               if V.Is_Text (Data, El (Directories, I), Path) then return True; end if;
            end loop;
            return False;
         end Directory;
         function Syntax (I : Positive) return V.Node is
         begin
            for J in 1 .. V.Count (Data, Syntax_Files) loop
               if V.Equal (Data, F (El (Syntax_Files, J), "path"), Data, F (El (Files, I), "path")) and then
                 V.Equal (Data, F (El (Syntax_Files, J), "payloadB64"), Data, F (El (Files, I), "payloadB64")) then
                  return F (El (Syntax_Files, J), "syntax");
               end if;
            end loop;
            return V.No_Node;
         end Syntax;
         function Package_File (Path : String) return Boolean is
           (Path'Length >= 12 and then Path (Path'Last - 11 .. Path'Last) = "/__init__.py");
         function Module_Of (I : Positive; Location : Natural) return String is
            Path : constant String := S (El (Files, I), "path");
            From : Natural := (if Location = 2 then Parent_Path (Entry_Path)'Length + 1 else 0);
            Last : Natural := Path'Length;
         begin
            if Location = 0 then return "__main__"; end if;
            if Package_File (Path) then Last := Last - 12;
            elsif Path'Length >= 3 then Last := Last - 3;
            else return "";
            end if;
            if From > Last then return ""; end if;
            declare
               Part : constant String := Path (Path'First + From .. Path'First + Last - 1);
               Name : String (1 .. Part'Length);
            begin
               for K in Name'Range loop Name (K) := (if Part (Part'First + K - 1) = '/' then '.' else Part (Part'First + K - 1)); end loop;
               return Name;
            end;
         end Module_Of;
         -- Full existing resolution order: both search roots, package before
         -- module, extension suffixes before .py, namespace directories,
         -- observed stdlib names, and optional from-import member lookups.
         procedure Resolve (Name : String; Optional : Boolean; Resolved : out Boolean)
           with Always_Terminates
         is
            Position : Natural := 0;
            Component_End : Natural;
            Selected : Natural;
            Was_Package : Boolean;
            Namespaces : array (1 .. 2) of Boolean := (others => True);
         begin
            Resolved := False;
            if Name = "candidate" then return; end if;
            while Position < Name'Length loop
               pragma Loop_Variant (Increases => Position);
               Component_End := Position;
               while Component_End < Name'Length and then Name (Name'First + Component_End) /= '.' loop
                  pragma Loop_Invariant (Component_End in Position .. Name'Length - 1);
                  pragma Loop_Variant (Increases => Component_End);
                  Component_End := Component_End + 1;
               end loop;
               if Component_End = Position then Failed := Failed or not Optional; return; end if;
               Selected := 0; Was_Package := False;
               for Location in 1 .. 2 loop
                  if Namespaces (Location) then
                     declare
                        Root_Path : constant String := (if Location = 1 or else Parent_Path (Entry_Path)'Length = 0 then "" else Parent_Path (Entry_Path) & "/");
                     begin
                        --  The original raised exactly at these points; refuse there.
                        if Component_End > Integer'Last - Name'First then Failed := True; return; end if;
                        if not Fits (Root_Path, Component_End) then Failed := True; return; end if;
                     declare
                        Base : constant String := Root_Path & To_Path (Name (Name'First .. Name'First + Component_End - 1));
                     begin
                        if V.Count (Data, Suffixes) > Natural'Last - 5 then Failed := True; return; end if;
                        for Package_Search in 1 .. 2 loop
                           for K in 1 .. V.Count (Data, Suffixes) + 5 loop
                              declare
                                 Extra : constant Natural := V.Count (Data, Suffixes);
                                 Suffix : constant String := (if K <= Extra then V.Text (Data, El (Suffixes, K)) else
                                   (case K - Extra is when 1 => ".py", when 2 => ".pyc", when 3 => ".pyd", when 4 => ".so", when others => ".zip"));
                                 Middle : constant Natural := (if Package_Search = 1 then 9 else 0);
                              begin
                                 if Suffix'Length > Natural'Last - Middle or else not Fits (Base, Middle + Suffix'Length) then
                                    Failed := True; return;
                                 end if;
                              declare
                                 Candidate : constant String := Base & (if Package_Search = 1 then "/__init__" else "") & Suffix;
                              begin
                                 Selected := File_Index (Candidate);
                                 if Selected > 0 then
                                    Was_Package := Package_Search = 1;
                                    if Suffix /= ".py" then Failed := True; return; end if;
                                    Pending (Selected, Location) := True;
                                    exit;
                                 end if;
                              end;
                              end;
                           end loop;
                           exit when Selected > 0;
                        end loop;
                        if Selected > 0 then
                           for Other in Namespaces'Range loop Namespaces (Other) := Other = Location; end loop;
                        else Namespaces (Location) := Directory (Base);
                        end if;
                     end;
                     end;
                  end if;
                  exit when Selected > 0;
               end loop;
               if Selected = 0 and then Position = 0 then
                  --  The original raised (Name'First + Component_End) exactly here.
                  if V.Count (Data, Standard) >= 1 and then Component_End > Integer'Last - Name'First then
                     Failed := True; return;
                  end if;
                  for K in 1 .. V.Count (Data, Standard) loop
                     if V.Is_Text (Data, El (Standard, K), Name (Name'First .. Name'First + Component_End - 1)) then return; end if;
                  end loop;
               end if;
               if Selected = 0 and then not Namespaces (1) and then not Namespaces (2) then
                  Failed := Failed or not Optional; return;
               elsif Selected > 0 and then not Was_Package and then Component_End < Name'Length then
                  Failed := Failed or not Optional; return;
               end if;
               if Component_End = Name'Length then Resolved := Selected > 0; return; end if;
               Position := Component_End + 1;
            end loop;
            Failed := Failed or not Optional;
         end Resolve;

         procedure Wildcard (Module_Name : String)
           with Always_Terminates
         is
            File : Natural := 0;
            function Node_At (Nodes, Ref : V.Node) return V.Node is
               Token : constant String := V.Decimal (Data, F (Ref, "node"));
               Index : Natural := 0;
               Bound : constant Natural := V.Count (Data, Nodes);
            begin
               if Token'Length = 0 then return V.No_Node; end if;
               for C of Token loop
                  if C not in '0' .. '9' or else Index > Bound / 10 or else
                     (Index = Bound / 10 and then Character'Pos (C) - 48 > Bound mod 10) then return V.No_Node; end if;
                  --  The original raised (Index * 10 + Pos) exactly here; no node.
                  if Index * 10 > Integer'Last - Character'Pos (C) then return V.No_Node; end if;
                  Index := Index * 10 + Character'Pos (C) - 48;
               end loop;
               if Index < Bound then
                  return El (Nodes, Index + 1);
               end if;
               return V.No_Node;
            end Node_At;
         begin
            for I in 1 .. File_Count loop
               for Location in 1 .. 2 loop
                  if Pending (I, Location) and then Package_File (S (El (Files, I), "path")) and then
                     Module_Of (I, Location) = Module_Name then File := I; exit; end if;
               end loop;
               exit when File > 0;
            end loop;
            if File = 0 then return; end if;
            declare
               Parsed : constant V.Node := Syntax (File);
               Nodes : constant V.Node := F (Parsed, "nodes");
               Scopes : constant V.Node := F (Parsed, "scopes");
               Members : constant V.Node := F (El (Scopes, 1), "nodes");
               function Ref (Item : V.Node) return V.Node is (Node_At (Nodes, Item));
               function A (Item : V.Node; Name : String) return V.Node is (F (F (Item, "fields"), Name));
               function AS (Item : V.Node; Name : String) return String is (V.Text (Data, A (Item, Name)));
               function K (Item : V.Node) return String is (S (Item, "kind"));
               --  Active is "" or a concatenation that starts at index 1.
               function Alias (Name, Active : String) return Boolean
                 with Pre => Active'Length = 0 or else Active'First = 1,
                   Subprogram_Variant => (Increases => Active'Length) is
               begin
                  if Name = "__all__" then return True; end if;
                  --  The original raised Constraint_Error exactly where these
                  --  texts pass Positive'Last (never for decoded strings of Data).
                  if Name'Length > Natural'Last - 2 then return True; end if;
                  case Search (Active, "|" & Name & "|") is
                     when Present => return False;
                     --  The original raised in Contains exactly here; an alias.
                     when Overflowed => return True;
                     when Absent => null;
                  end case;
                  for I in 1 .. V.Count (Data, Members) loop
                     declare
                        Item : constant V.Node := Ref (El (Members, I));
                        Value : constant V.Node := Ref (A (Item, "value"));
                        Targets : constant V.Node := A (Item, "targets");
                     begin
                        if K (Item) in "Assign" | "AnnAssign" | "NamedExpr" and then K (Value) = "Name" then
                           if K (Item) = "Assign" then
                              for J in 1 .. V.Count (Data, Targets) loop
                                 declare Target : constant V.Node := Ref (El (Targets, J));
                                 begin
                                    if K (Target) = "Name" and then AS (Target, "id") = Name and then
                                       (Active'Length > Natural'Last - 2 - Name'Length or else
                                        Alias (AS (Value, "id"), Active & "|" & Name & "|")) then return True; end if;
                                 end;
                              end loop;
                           else
                              declare Target : constant V.Node := Ref (A (Item, "target"));
                              begin
                                 if K (Target) = "Name" and then AS (Target, "id") = Name and then
                                    (Active'Length > Natural'Last - 2 - Name'Length or else
                                     Alias (AS (Value, "id"), Active & "|" & Name & "|")) then return True; end if;
                              end;
                           end if;
                        end if;
                     end;
                  end loop;
                  return False;
               end Alias;
               --  Valid syntax (checked below before any use) makes every
               --  field-bearing reference preorder, so a value chain visits at
               --  most Count (Nodes) + 1 nodes; Fuel = 0 is unreachable there.
               Chain_Fuel : constant Long_Long_Integer := Long_Long_Integer (V.Count (Data, Nodes)) + 1;
               function Is_Alias (Item : V.Node; Fuel : Long_Long_Integer := Chain_Fuel) return Boolean
                 with Subprogram_Variant => (Decreases => Fuel) is
               begin
                  if K (Item) in "Attribute" | "Subscript" then
                     if Fuel <= 0 then return True; end if;
                     return Is_Alias (Ref (A (Item, "value")), Fuel - 1);
                  end if;
                  return K (Item) = "Name" and then Alias (AS (Item, "id"), "");
               end Is_Alias;
               procedure Literal (Item : V.Node; Single : Boolean := False)
                 with Always_Terminates, Subprogram_Variant => (Decreases => Boolean'Pos (not Single))
               is
                  Ignored : Boolean;
               begin
                  if K (Item) = "Constant" and then
                    (A (Item, "value").Form = V.String_Value or else
                     V.Is_Text (Data, F (A (Item, "value"), "constantType"), "str")) then
                     if Single then
                        if A (Item, "value").Form = V.String_Value then
                           declare Member : constant String := V.Text (Data, A (Item, "value")); begin
                              --  The original raised exactly here; refuse.
                              if not Fits2 (Module_Name, 1, Member'Length) then Failed := True;
                              else Resolve (Module_Name & "." & Member, True, Ignored);
                              end if;
                           end;
                        else
                           declare Value : constant B.Decoded := B.Base64 (S (A (Item, "value"), "payloadB64"));
                           begin
                              if Value.Valid and then not Fits2 (Module_Name, 1, Value.Data'Length) then Failed := True;
                              elsif Value.Valid then Resolve (Module_Name & "." & Value.Data, True, Ignored);
                              else Failed := True;
                              end if;
                           end;
                        end if;
                     else Failed := True;
                     end if;
                  elsif not Single and then K (Item) in "List" | "Tuple" | "Set" then
                     for I in 1 .. V.Count (Data, A (Item, "elts")) loop
                        Literal (Ref (El (A (Item, "elts"), I)), True);
                     end loop;
                  elsif not Single and then K (Item) = "Call" and then
                    K (Ref (A (Item, "func"))) = "Name" and then
                    AS (Ref (A (Item, "func")), "id") = "set" and then
                    V.Count (Data, A (Item, "args")) = 0 and then
                    V.Count (Data, A (Item, "keywords")) = 0 then
                     null;
                  else Failed := True;
                  end if;
               end Literal;
               procedure Target (Item, Value : V.Node; Augmented : Boolean)
                 with Always_Terminates
               is
               begin
                  if K (Item) = "Name" and then AS (Item, "id") = "__all__" then Literal (Value);
                  elsif Augmented and then K (Item) = "Name" and then Alias (AS (Item, "id"), "") then Literal (Value);
                  elsif K (Item) in "Subscript" | "Attribute" and then Is_Alias (Item) then Literal (Value, True);
                  end if;
               end Target;
            begin
               if F (Parsed, "exception").Form /= V.Null_Value then return; end if;
               --  This package file is Pending, so Examine later refuses an
               --  invalid syntax anyway (Failed is read only by the final
               --  verdict); refusing it here first keeps the walk below finite.
               if not Worldline.Source_Syntax.Valid (V.Slice (Data, Parsed)) then
                  Failed := True; return;
               end if;
               for I in 1 .. V.Count (Data, Members) loop
                  declare
                     Item : constant V.Node := Ref (El (Members, I));
                     Kind : constant String := K (Item);
                  begin
                     if Kind = "Assign" then
                        for J in 1 .. V.Count (Data, A (Item, "targets")) loop Target (Ref (El (A (Item, "targets"), J)), Ref (A (Item, "value")), False); end loop;
                     elsif Kind in "AnnAssign" | "AugAssign" then Target (Ref (A (Item, "target")), Ref (A (Item, "value")), Kind = "AugAssign");
                     end if;
                     if Kind in "Import" | "ImportFrom" then
                        for J in 1 .. V.Count (Data, A (Item, "names")) loop
                           declare
                              Import_Alias : constant V.Node := Ref (El (A (Item, "names"), J));
                              Name : constant String := AS (Import_Alias, "asname");
                           begin
                              Failed := Failed or (if Name'Length > 0 then Name else Head (AS (Import_Alias, "name"))) = "__all__";
                           end;
                        end loop;
                     elsif Kind = "Call" then
                        declare
                           Function_Node : constant V.Node := Ref (A (Item, "func"));
                           Arguments : constant V.Node := A (Item, "args");
                           Attribute : constant String := AS (Function_Node, "attr");
                        begin
                           if K (Function_Node) = "Attribute" and then Is_Alias (Ref (A (Function_Node, "value"))) then
                              if Attribute in "append" | "extend" | "__iadd__" | "__setitem__" | "insert" and then
                                 V.Count (Data, A (Item, "keywords")) = 0 then
                                 if Attribute in "append" | "extend" | "__iadd__" and then V.Count (Data, Arguments) = 1 then
                                    Literal (Ref (El (Arguments, 1)), Attribute = "append");
                                 elsif Attribute in "insert" | "__setitem__" and then V.Count (Data, Arguments) = 2 then Literal (Ref (El (Arguments, 2)), True);
                                 else Failed := True;
                                 end if;
                              elsif Attribute not in "clear" | "pop" | "remove" | "reverse" | "sort" | "__delitem__" | "__imul__" | "copy" | "count" | "index" then Failed := True;
                              end if;
                           else
                              for J in 1 .. V.Count (Data, Arguments) loop Failed := Failed or Is_Alias (Ref (El (Arguments, J))); end loop;
                              for J in 1 .. V.Count (Data, A (Item, "keywords")) loop Failed := Failed or Is_Alias (Ref (A (Ref (El (A (Item, "keywords"), J)), "value"))); end loop;
                           end if;
                        end;
                     end if;
                  end;
               end loop;
            end;
         end Wildcard;

         procedure Examine (File : Positive; Location : Natural)
           with Always_Terminates
         is
            Parsed : constant V.Node := Syntax (File);
            Nodes : constant V.Node := F (Parsed, "nodes");
            Scopes : constant V.Node := F (Parsed, "scopes");
            Module_Name : constant String := Module_Of (File, Location);
            Is_Package : constant Boolean := Package_File (S (El (Files, File), "path"));
            function Number (Item : V.Node; Bound : Natural) return Natural is
               Token : constant String := V.Decimal (Data, Item);
               Value : Natural := 0;
            begin
               if Token'Length = 0 then return Bound; end if;
               for C of Token loop
                  if C not in '0' .. '9' then return Bound; end if;
                  if Value > Bound / 10 or else (Value = Bound / 10 and then Character'Pos (C) - 48 > Bound mod 10) then return Bound; end if;
                  --  The original raised (Value * 10 + Pos) exactly here; no index.
                  if Value * 10 > Integer'Last - Character'Pos (C) then return Bound; end if;
                  Value := Value * 10 + Character'Pos (C) - 48;
               end loop;
               return Value;
            end Number;
            function Ref (Item : V.Node) return V.Node is
               Index : constant Natural := Number (F (Item, "node"), V.Count (Data, Nodes));
            begin
               if Index < V.Count (Data, Nodes) then
                  return El (Nodes, Index + 1);
               end if;
               return V.No_Node;
            end Ref;
            function A (Item : V.Node; Name : String) return V.Node is (F (F (Item, "fields"), Name));
            function AS (Item : V.Node; Name : String) return String is (V.Text (Data, A (Item, Name)));
            function K (Item : V.Node) return String is (S (Item, "kind"));
            function Scope (Index : Natural) return V.Node is
            begin
               if Index < V.Count (Data, Scopes) then
                  return El (Scopes, Index + 1);
               end if;
               return V.No_Node;
            end Scope;
            function Parent (Index : Natural) return Natural is
               Candidate : constant Natural := Number (F (Scope (Index), "parent"), V.Count (Data, Scopes));
            begin
               if Candidate < V.Count (Data, Scopes) and then K (Ref (F (Scope (Candidate), "root"))) = "ClassDef" then
                  return Number (F (Scope (Candidate), "parent"), V.Count (Data, Scopes));
               end if;
               return Candidate;
            end Parent;
            function Named (Array_Node : V.Node; Name : String) return Boolean is
            begin
               for I in 1 .. V.Count (Data, Array_Node) loop
                  if V.Is_Text (Data, El (Array_Node, I), Name) then return True; end if;
               end loop;
               return False;
            end Named;
            function Parameter (Root_Node : V.Node; Name : String) return Boolean is
               Arguments : constant V.Node := Ref (A (Root_Node, "args"));
            begin
               if K (Root_Node) not in "FunctionDef" | "AsyncFunctionDef" | "Lambda" then return False; end if;
               for Part in 1 .. 5 loop
                  declare
                     Key : constant String := (case Part is when 1 => "posonlyargs", when 2 => "args", when 3 => "kwonlyargs", when 4 => "vararg", when others => "kwarg");
                     Items : constant V.Node := A (Arguments, Key);
                  begin
                     if Part > 3 then
                        if AS (Ref (Items), "arg") = Name then return True; end if;
                     else
                        for I in 1 .. V.Count (Data, Items) loop
                           if AS (Ref (El (Items, I)), "arg") = Name then return True; end if;
                        end loop;
                     end if;
                  end;
               end loop;
               return False;
            end Parameter;
            function Match (Name : String; Mode : Positive) return Boolean is
              (case Mode is when 1 => Denied_Attribute (Name), when 2 => State_Name (Name, True),
               when 3 => State_Name (Name, False), when others => Name in "sqlite3.connect" | "sqlite3.Connection");
            --  Termination witness. Examine's syntax is Valid (checked first):
            --  node references are preorder and scope parents precede their
            --  scope, so between two growths of Active (a new binding key)
            --  at most Count (Nodes) + Count (Scopes) + 1 calls occur; Fuel = 0
            --  is unreachable for every input reaching this code.
            Fuel_Full : constant Long_Long_Integer :=
              Long_Long_Integer (V.Count (Data, Nodes)) + Long_Long_Integer (V.Count (Data, Scopes)) + 4;
            function Any_Origin (Expression : V.Node; Scope_Index : Natural; Suffix : String;
               Mode : Positive; Active : String; Fuel : Long_Long_Integer; Assignment : Boolean := False) return Boolean
              with Pre => Active'Length = 0 or else Active'First = 1,
                Subprogram_Variant => (Increases => Active'Length, Decreases => Fuel);
            function Binding (Name : String; Scope_Index : Natural; Suffix : String;
               Mode : Positive; Active : String; Fuel : Long_Long_Integer) return Boolean
              with Pre => Active'Length = 0 or else Active'First = 1,
                Subprogram_Variant => (Increases => Active'Length, Decreases => Fuel)
            is
               Members : constant V.Node := F (Scope (Scope_Index), "nodes");
               Local : Boolean := Parameter (Ref (F (Scope (Scope_Index), "root")), Name);
               Outer, Imported : Boolean := False;
            begin
               --  The original raised Constraint_Error building Active_Key exactly
               --  here (never for a decoded string of Data); refuse as an origin.
               if Name'Length > Natural'Last - 3 - Image (Scope_Index)'Length then return True; end if;
               declare
               Active_Key : constant String := Character'Val (0) & Image (Scope_Index) & ":" & Name & Character'Val (0);
               Seen : constant Search_Result := Search (Active, Active_Key);
               Seen_Binding : constant Boolean := Seen = Present;
            begin
               --  The original raised in Contains exactly here; refuse as an origin.
               if Seen = Overflowed then return True; end if;
               for I in 1 .. V.Count (Data, Members) loop
                  declare
                     Item : constant V.Node := Ref (El (Members, I));
                     Kind : constant String := K (Item);
                     Aliases : constant V.Node := A (Item, "names");
                  begin
                     if Kind = "Name" and then AS (Item, "id") = Name and then K (Ref (A (Item, "ctx"))) in "Store" | "Del" then Local := True;
                     elsif Kind = "arg" and then AS (Item, "arg") = Name then Local := True;
                     elsif Kind in "Global" | "Nonlocal" and then Named (Aliases, Name) then Outer := True;
                     elsif Kind in "Import" | "ImportFrom" then
                        for J in 1 .. V.Count (Data, Aliases) loop
                           declare
                              Alias : constant V.Node := Ref (El (Aliases, J));
                              Import_Name : constant String := AS (Alias, "name");
                              As_Name : constant String := AS (Alias, "asname");
                              Bound : constant String := (if As_Name'Length > 0 then As_Name elsif Kind = "Import" then Head (Import_Name) else Import_Name);
                           begin
                              if Bound = Name and then (Kind = "Import" or else
                                (V.Decimal (Data, A (Item, "level")) = "0" and then AS (Item, "module")'Length > 0 and then Import_Name /= "*")) then
                                 Imported := True;
                                 declare
                                    Module : constant String := (if Kind = "Import" then "" else AS (Item, "module"));
                                 begin
                                    --  The original raised building these exactly when a
                                    --  guard holds (never for Data's strings); refuse there.
                                    if Kind /= "Import" and then not Fits2 (Module, 1, Import_Name'Length) then return True; end if;
                                    declare
                                       Qualified : constant String := (if Kind = "Import" then (if As_Name'Length > 0 then Import_Name else Head (Import_Name)) else
                                         Module & "." & Import_Name);
                                    begin
                                       if not Fits (Qualified, Suffix'Length) then return True; end if;
                                       if Match (Qualified & Suffix, Mode) then return True; end if;
                                    end;
                                 end;
                              end if;
                           end;
                        end loop;
                     end if;
                  end;
               end loop;
               if Outer or else (not Imported and then not Local) then
                  if Parent (Scope_Index) < V.Count (Data, Scopes) then
                     if Fuel <= 0 then return True; end if;
                     if Binding (Name, Parent (Scope_Index), Suffix, Mode, Active, Fuel - 1) then return True; end if;
                  elsif not Imported and then (not Fits (Name, Suffix'Length) or else Match (Name & Suffix, Mode)) then return True;
                  end if;
               end if;
               if Seen_Binding then return False; end if;
               for I in 1 .. V.Count (Data, Members) loop
                  declare
                     Item : constant V.Node := Ref (El (Members, I));
                     Kind : constant String := K (Item);
                     Targets : constant V.Node := A (Item, "targets");
                     Value : constant V.Node := Ref (A (Item, "value"));
                  begin
                     if Kind in "Assign" | "AnnAssign" | "NamedExpr" then
                        if Kind /= "Assign" then
                           declare Target : constant V.Node := Ref (A (Item, "target"));
                           begin
                              if K (Target) = "Name" and then AS (Target, "id") = Name and then
                                (Active'Length > Natural'Last - Active_Key'Length or else
                                 Any_Origin (Value, Scope_Index, Suffix, Mode, Active & Active_Key, Fuel_Full, True)) then return True; end if;
                           end;
                        else
                           for J in 1 .. V.Count (Data, Targets) loop
                              declare Target : constant V.Node := Ref (El (Targets, J));
                              begin
                                 if K (Target) = "Name" and then AS (Target, "id") = Name and then
                                   (Active'Length > Natural'Last - Active_Key'Length or else
                                    Any_Origin (Value, Scope_Index, Suffix, Mode, Active & Active_Key, Fuel_Full, True)) then return True; end if;
                              end;
                           end loop;
                        end if;
                     end if;
                  end;
               end loop;
               return False;
               end;
            end Binding;
            function Any_Origin (Expression : V.Node; Scope_Index : Natural; Suffix : String;
               Mode : Positive; Active : String; Fuel : Long_Long_Integer; Assignment : Boolean := False) return Boolean is
               Kind : constant String := K (Expression);
            begin
               if Kind in "Name" | "Attribute" | "Call" or else (Kind = "Subscript" and then not Assignment) then
                  if Fuel <= 0 then return True; end if;
               end if;
               if Kind = "Name" then return Binding (AS (Expression, "id"), Scope_Index, Suffix, Mode, Active, Fuel - 1);
               elsif Kind = "Attribute" then
                  declare Attribute : constant String := AS (Expression, "attr"); begin
                     --  The original raised exactly here (never for Data's strings).
                     if Attribute'Length > Natural'Last - 1 - Suffix'Length then return True; end if;
                     return Any_Origin (Ref (A (Expression, "value")), Scope_Index, "." & Attribute & Suffix, Mode, Active, Fuel - 1, Assignment);
                  end;
               elsif Kind = "Subscript" and then not Assignment then return Any_Origin (Ref (A (Expression, "value")), Scope_Index, Suffix, Mode, Active, Fuel - 1);
               elsif Kind = "Call" and then Any_Origin (Ref (A (Expression, "func")), Scope_Index, "", 4, Active, Fuel - 1, Assignment) then
                  if Suffix'Length > Natural'Last - 18 then return True; end if;
                  return Match ("sqlite3.Connection" & Suffix, Mode);
               end if;
               return False;
            end Any_Origin;
            function Relative_Module (Name : String; Level : Natural) return String is
               Parts : Natural := 1;
               Last : Natural := Module_Name'Length;
            begin
               if not Is_Package then
                  for I in reverse Module_Name'Range loop
                     pragma Loop_Invariant (Last <= Module_Name'Length);
                     if Module_Name (I) = '.' then Last := I - Module_Name'First; exit; end if;
                     if I = Module_Name'First then Last := 0; end if;
                  end loop;
               end if;
               if Last = 0 then return ""; end if;
               for I in 0 .. Last - 1 loop
                  pragma Loop_Invariant (Parts <= I + 1);
                  if Module_Name (Module_Name'First + I) = '.' then
                     --  The original raised (Parts + 1) exactly here; "" refuses.
                     if Parts = Natural'Last then return ""; end if;
                     Parts := Parts + 1;
                  end if;
               end loop;
               if Level > Parts then return ""; end if;
               for Removed in 1 .. Level - 1 loop
                  pragma Loop_Invariant (Last <= Module_Name'Length);
                  for I in reverse 0 .. Last - 1 loop
                     if Module_Name (Module_Name'First + I) = '.' then Last := I; exit; end if;
                  end loop;
               end loop;
               --  The original raised exactly here; "" is ImportFrom's refusal.
               if Last = Module_Name'Length and then Module_Name'Last = Integer'Last then return ""; end if;
               if Name'Length > 0 and then not Fits2 (Module_Name (Module_Name'First .. Module_Name'First + Last - 1), 1, Name'Length) then
                  return "";
               end if;
               return Module_Name (Module_Name'First .. Module_Name'First + Last - 1) & (if Name'Length > 0 then "." & Name else "");
            end Relative_Module;
         begin
            if not Worldline.Source_Syntax.Valid (V.Slice (Data, Parsed)) then
               Failed := True; return;
            end if;
            for Scope_Index in 0 .. V.Count (Data, Scopes) - 1 loop
               declare
                  Items : constant V.Node := F (Scope (Scope_Index), "nodes");
               begin
                  for I in 1 .. V.Count (Data, Items) loop
                     declare
                        Item : constant V.Node := Ref (El (Items, I));
                        Kind : constant String := K (Item);
                        Resolved : Boolean;
                     begin
                        if Kind = "Import" then
                           for J in 1 .. V.Count (Data, A (Item, "names")) loop
                              declare Name : constant String := AS (Ref (El (A (Item, "names"), J)), "name");
                              begin
                                 Failed := Failed or Denied_Import (Name) or Denied_Attribute (Name);
                                 declare Ignored : Boolean;
                                 begin Resolve (Name, False, Ignored); end;
                              end;
                           end loop;
                        elsif Kind = "ImportFrom" then
                           --  The original raised exactly here; refuse.
                           if Module_Name'Length = Natural'Last then Failed := True; return; end if;
                           declare
                              Level : constant Natural := Number (A (Item, "level"), Module_Name'Length + 1);
                              Name : constant String := (if Level = 0 then AS (Item, "module") else Relative_Module (AS (Item, "module"), Level));
                           begin
                              if Name'Length = 0 then Failed := True;
                              else
                                 Failed := Failed or Denied_Import (Name);
                                 Resolve (Name, False, Resolved);
                                 for J in 1 .. V.Count (Data, A (Item, "names")) loop
                                    declare
                                       Member : constant String := AS (Ref (El (A (Item, "names"), J)), "name");
                                    begin
                                       --  The original raised exactly here; refuse.
                                       if not Fits2 (Name, 1, Member'Length) then Failed := True; return; end if;
                                       Failed := Failed or Denied_Import (Name & "." & Member) or Denied_Attribute (Name & "." & Member) or Denied_Name (Member);
                                       if Resolved and then Member /= "*" then
                                          declare Ignored : Boolean;
                                          begin Resolve (Name & "." & Member, True, Ignored); end;
                                       elsif Resolved then Wildcard (Name);
                                       end if;
                                    end;
                                 end loop;
                              end if;
                           end;
                        elsif Kind = "Name" then Failed := Failed or Denied_Name (AS (Item, "id"));
                        end if;
                        if Kind = "Attribute" then Failed := Failed or Any_Origin (Item, Scope_Index, "", 1, "", Fuel_Full); end if;
                        if Kind in "Attribute" | "Subscript" | "Name" and then K (Ref (A (Item, "ctx"))) in "Store" | "Del" then
                           Failed := Failed or Any_Origin (Item, Scope_Index, "", 2, "", Fuel_Full);
                        end if;
                        if Kind = "Call" and then K (Ref (A (Item, "func"))) = "Attribute" then
                           declare Function_Node : constant V.Node := Ref (A (Item, "func"));
                           begin
                              Failed := Failed or (Mutator (AS (Function_Node, "attr")) and then
                                Any_Origin (Ref (A (Function_Node, "value")), Scope_Index, "", 3, "", Fuel_Full));
                           end;
                        end if;
                     end;
                  end loop;
               end;
            end loop;
         end Examine;
         Total : Natural := 0;
         Work : Boolean;
      begin
         if Observation.Form /= V.Object_Value or else Files.Form /= V.Array_Value or else
           not V.Equal (Data, Runtime, Data, F (AST, "runtime")) or else
           Syntax_Files.Form /= V.Array_Value or else File_Count = 0 or else Members.Form /= V.Array_Value or else
           not Relative (Entry_Path) or else S (Observation, "entry") /= Entry_Path or else
           S (Observation, "schema") /= "worldline-examiner-audit-v1" or else
           Directories.Form /= V.Array_Value or else not Directory ("") then return False; end if;
         if File_Count > 100_000 or else V.Count (Data, Directories) > 100_000 - File_Count or else
           V.Count (Data, Syntax_Files) /= File_Count or else
           F (Observation, "executedDigests").Form /= V.Object_Value or else
           V.Count (Data, F (Observation, "executedDigests")) /= File_Count then return False; end if;
         for I in 1 .. V.Count (Data, Directories) loop
            declare Path : constant String := V.Text (Data, El (Directories, I));
            begin
               if El (Directories, I).Form /= V.String_Value or else (Path /= "" and then not Relative (Path)) or else
                 (I > 1 and then V.Text (Data, El (Directories, I - 1)) >= Path) then return False; end if;
            end;
         end loop;
         for I in 1 .. File_Count loop
            declare
               Item : constant V.Node := El (Files, I);
               Path : constant String := S (Item, "path");
               Decoded : constant B.Decoded := B.Base64 (S (Item, "payloadB64"));
               Found : Boolean := False;
            begin
               if Item.Form /= V.Object_Value or else V.Count (Data, Item) /= 2 or else
                 F (Item, "path").Form /= V.String_Value or else F (Item, "payloadB64").Form /= V.String_Value or else
                 not Relative (Path) or else Directory (Path) or else
                 not Canonical (S (Item, "payloadB64"), Decoded) or else not Directory (Parent_Path (Path)) or else
                 Decoded.Length > 268_435_456 - Total or else
                 V.Text (Data, F (F (Observation, "executedDigests"), Path)) /= B.Digest (Decoded.Data) then return False; end if;
               Total := Total + Decoded.Length;
               for J in 1 .. V.Count (Data, Members) loop
                  declare Member : constant V.Node := El (Members, J);
                          Member_Root : constant String := S (Member, "rootKey");
                          Member_Path : constant String := S (Member, "path");
                  begin
                     --  The original raised exactly at these two guards; refuse there.
                     if not Fits2 (Member_Root, 1, Member_Path'Length) then return False; end if;
                     if Member_Root & "/" & Member_Path = Path then
                        if Found or else not Relative (S (Member, "rootKey")) or else Search (Member_Root, "/") /= Absent or else
                           not Relative (S (Member, "path")) or else Path'Length > Natural'Last - 25 or else
                           S (Member, "executedAs") /= "/run/worldline-verifiers/" & Path or else
                           S (Member, "sha256") /= B.Digest (Decoded.Data) then return False; end if;
                        Found := True;
                     end if;
                  end;
               end loop;
               if not Found then return False; end if;
               for J in I + 1 .. File_Count loop
                  if V.Equal (Data, F (Item, "path"), Data, F (El (Files, J), "path")) then return False; end if;
               end loop;
            end;
         end loop;
         if File_Count /= V.Count (Data, Members) then return False; end if;
         declare Initial : constant Natural := File_Index (Entry_Path);
         begin if Initial = 0 then return False; end if; Pending (Initial, 0) := True; end;
         --  Every working round marks a new Seen pair (3 * File_Count of them),
         --  so the original loop ran at most 3 * File_Count + 1 rounds.
         for Round in 0 .. 3 * File_Count loop
            Work := False;
            for I in 1 .. File_Count loop
               for Location in 0 .. 2 loop
                  if Pending (I, Location) and then not Seen (I, Location) then
                     Work := True; Seen (I, Location) := True;
                     Examine (I, Location);
                  end if;
               end loop;
            end loop;
            exit when not Work;
         end loop;
         declare
            Closure : constant V.Node := F (Observation, "closure");
            Seen_Count : Natural := 0;
         begin
            if Closure.Form /= V.Array_Value then return False; end if;
            for I in 1 .. File_Count loop
               pragma Loop_Invariant (Seen_Count < I);
               if (for some L in 0 .. 2 => Seen (I, L)) then
                  Seen_Count := Seen_Count + 1;
                  declare
                     Path : constant String := S (El (Files, I), "path");
                     Found : Boolean := False;
                     Payload : constant B.Decoded := B.Base64 (S (El (Files, I), "payloadB64"));
                  begin
                     for J in 1 .. V.Count (Data, Closure) loop
                        declare Item : constant V.Node := El (Closure, J);
                        begin
                           if S (Item, "path") = Path then
                              if Found or else V.Count (Data, Item) /= 2 or else S (Item, "sha256") /= B.Digest (Payload.Data) then return False; end if;
                              Found := True;
                           end if;
                        end;
                     end loop;
                     if not Found then return False; end if;
                  end;
               end if;
            end loop;
            if Seen_Count /= V.Count (Data, Closure) then return False; end if;
            for I in 2 .. V.Count (Data, Closure) loop
               if S (El (Closure, I - 1), "path") >= S (El (Closure, I), "path") then return False; end if;
            end loop;
         end;
         return not Failed;
      end Phase_Clean;
   begin
      return Root.Form = V.Object_Value and then Audit.Form = V.Object_Value and then AST.Form = V.Object_Value and then
        S (Audit, "mount") = "/run/worldline-verifiers" and then
        V.Equal (Data, F (F (Audit, "before"), "files"), Data, F (F (Audit, "after"), "files")) and then
        V.Equal (Data, F (F (Audit, "before"), "directories"), Data, F (F (Audit, "after"), "directories")) and then
        Phase_Clean ("before") and then Phase_Clean ("after");
   end Closure_Clean_Joined;
   function Closure_Clean (Result_Record, Native_AST : String) return Boolean is
      Parsed_AST : constant V.Node := V.Parse (Native_AST);
   begin
      --  Totalized: the original raised Constraint_Error building the joint
      --  arena or the rebased AST span exactly when this holds; refuse it.
      if Native_AST'Length > Natural'Last - 1 - (if Result_Record'Length = 0 then 0 else Result_Record'Last)
        or else (Parsed_AST.Form /= V.Missing and then
          (Parsed_AST.First > Natural'Last - 1 - Result_Record'Length or else
           Parsed_AST.Last > Natural'Last - 1 - Result_Record'Length))
      then return False; end if;
      return Closure_Clean_Joined (Result_Record, Native_AST, Parsed_AST);
   end Closure_Clean;
   function Clean (Result_Record : String) return Boolean is
     (Worldline.Source_Syntax_Provider.Authentic (Result_Record) and then
      Closure_Clean (Result_Record, V.Field (Result_Record, "nativeSourceAST")));
   function Clean (Original_Result, Parser_Declaration, Raw_Capsule : String)
      return Boolean is
      Original : constant V.Node := V.Parse (Original_Result);
      Parsed : constant Worldline.Source_Syntax_Provider.Parsed_Syntax :=
        Worldline.Source_Syntax_Provider.Project (Original_Result, Parser_Declaration, Raw_Capsule);
   begin
      if Original.Form /= V.Object_Value or else not Parsed.Valid then return False; end if;
      return Closure_Clean (Original_Result, Parsed.AST);
   end Clean;
end Worldline.Source_Audit_Native;
