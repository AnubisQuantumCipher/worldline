with Worldline.Producer_Values;
with Worldline.Protected_Paths;
package body Worldline.Policy_Syntax with SPARK_Mode is
   package V renames Worldline.Producer_Values;
   use type V.Value_Kind;
   function Named (Name, Allowed : String) return Boolean is
   begin
      for I in 1 .. V.Count (Allowed) loop
         if V.Text (V.Element (Allowed, I - 1)) = Name then return True; end if;
      end loop;
      return False;
   end Named;
   function Fields (Value, Required, Allowed : String) return Boolean is
   begin
      if V.Kind (Value) /= V.Object_Value then return False; end if;
      for I in 1 .. V.Count (Required) loop
         if V.Kind (V.Field (Value, V.Text (V.Element (Required, I - 1)))) = V.Missing then return False; end if;
      end loop;
      for I in 1 .. V.Count (Value) loop
         if not Named (V.Member_Name (Value, V.Parse (Value), I), Allowed) then return False; end if;
      end loop;
      return True;
   end Fields;
   function Relative (Value : String) return Boolean is
      Text : constant String := V.Text (Value);
      First : Natural := 0;
   begin
      if V.Kind (Value) /= V.String_Value or else Text'Length = 0 then return False; end if;
      for C of Text loop
         if C = Character'Val (0) then return False; end if;
      end loop;
      if Text = "." then return True; end if;
      for I in 0 .. Text'Length loop
         if I = Text'Length or else Text (Text'First + I) = '/' then
            declare Part : constant String := Text (Text'First + First .. Text'First + I - 1);
            begin
               if Part = "" or else Part = "." or else Part = ".." then return False; end if;
            end;
            if I < Text'Length then First := I + 1; end if;
         end if;
      end loop;
      return True;
   end Relative;
   function Paths (Value : String) return Boolean is
   begin
      if V.Kind (Value) /= V.Array_Value then return False; end if;
      for I in 1 .. V.Count (Value) loop
         if not Relative (V.Element (Value, I - 1)) then return False; end if;
      end loop;
      return True;
   end Paths;
   function Argv (Value : String) return Boolean is
   begin
      if V.Kind (Value) /= V.Array_Value or else V.Count (Value) = 0 then return False; end if;
      for I in 1 .. V.Count (Value) loop
         if not V.Nonempty_Text (Value, V.Element (Value, V.Parse (Value), I)) then return False; end if;
      end loop;
      return True;
   end Argv;
   function Identifier (Value, Rows : String; Ordinal : Positive) return Boolean is
      Name : constant String := V.Text (Value);
      function Alnum (C : Character) return Boolean is
        (C in 'A' .. 'Z' or else C in 'a' .. 'z' or else C in '0' .. '9');
   begin
      -- This is the inherited _SAFE_IDENTIFIER limit, not a new source cap.
      if V.Kind (Value) /= V.String_Value or else Name'Length not in 1 .. 128 or else
        not Alnum (Name (Name'First))
      then return False; end if;
      for C of Name loop
         if not Alnum (C) and then C /= '_' and then C /= '.' and then C /= '-' then return False; end if;
      end loop;
      for I in 1 .. Ordinal - 1 loop
         if V.Equal (Value, V.Field (V.Element (Rows, I - 1), "id")) then return False; end if;
      end loop;
      return True;
   end Identifier;
   function Defaulted (Value, Name, Default : String) return String is
      Item : constant String := V.Field (Value, Name);
   begin
      return (if V.Kind (Item) = V.Missing then Default else Item);
   end Defaulted;
   function Has_Glob (Text : String) return Boolean is
   begin
      for C of Text loop
         if C = '*' or else C = '?' or else C = '[' then return True; end if;
      end loop;
      return False;
   end Has_Glob;
   function Probe (Pattern : String; First : Natural := 0) return String
     with Subprogram_Variant => (Decreases => Pattern'Length - Natural'Min (First, Pattern'Length))
   is
      Last : Natural := First;
   begin
      if First >= Pattern'Length then return "__probe__"; end if;
      while Last < Pattern'Length and then Pattern (Pattern'First + Last) /= '/' loop
         Last := Last + 1;
      end loop;
      declare Part : constant String := Pattern (Pattern'First + First .. Pattern'First + Last - 1);
      begin
         if Has_Glob (Part) then
            return (if Last < Pattern'Length then Probe (Pattern, Last + 1) else "__probe__");
         end if;
         return Part & "/" & (if Last < Pattern'Length then Probe (Pattern, Last + 1) else "__probe__");
      end;
   end Probe;
   function Verifier_Separate (Verifiers, Covers : String) return Boolean is
   begin
      for I in 1 .. V.Count (Verifiers) loop
         declare
            Pattern : constant String := V.Text (V.Element (Verifiers, I - 1));
            Path : constant String := (if Has_Glob (Pattern) then Probe (Pattern) else Pattern);
         begin
            for J in 1 .. V.Count (Covers) loop
               declare Cover : constant String := V.Text (V.Element (Covers, J - 1));
               begin
                  -- Relative validation forbids trailing slash components;
                  -- for trailing stars fnmatch already includes the subtree.
                  if Pattern = Cover or else Worldline.Protected_Paths.Matches (Cover, Path) then return False; end if;
               end;
            end loop;
         end;
      end loop;
      return True;
   end Verifier_Separate;
   function Checks (Rows : String) return Boolean is
      Private_Started : Boolean := False;
   begin
      if V.Kind (Rows) /= V.Array_Value then return False; end if;
      for I in 1 .. V.Count (Rows) loop
         declare
            Row : constant String := V.Element (Rows, I - 1);
            Name : constant String := V.Text (V.Field (Row, "id"));
            Format : constant String := V.Text (V.Field (Row, "format"));
            Profile : constant String := V.Text (Defaulted (Row, "profile", """legacy"""));
            Cwd : constant String := Defaulted (Row, "cwd", "null");
            Result_Path : constant String := Defaulted (Row, "result", "null");
            Covers : constant String := Defaulted (Row, "covers", "[]");
            Verifiers : constant String := Defaulted (Row, "verifiers", "[]");
         begin
            if not Fields (Row, "[""id"",""kind"",""argv"",""required"",""format""]",
              "[""id"",""kind"",""argv"",""cwd"",""required"",""format"",""result"",""covers"",""verifiers"",""profile""]") or else
              not Identifier (V.Field (Row, "id"), Rows, I) or else Name = "agent" or else Name = "protected-paths" or else
              not Named (V.Text (V.Field (Row, "kind")), "[""build"",""tests"",""proofs"",""benchmark"",""health""]") or else
              not Argv (V.Field (Row, "argv")) or else
              (V.Kind (Cwd) /= V.Null_Value and then not Relative (Cwd)) or else
              V.Kind (V.Field (Row, "required")) /= V.Boolean_Value or else
              not Named (Format, "[""exit"",""junit"",""gnatprove"",""worldline-benchmark-v1""]") or else
              (V.Kind (Result_Path) /= V.Null_Value and then not Relative (Result_Path)) or else
              not Paths (Covers) or else not Paths (Verifiers) or else
              (Profile /= "legacy" and then Profile /= "private-evaluator-v1") or else
              not Verifier_Separate (Verifiers, Covers)
            then return False; end if;
            if Profile = "private-evaluator-v1" then
               Private_Started := True;
               if Format = "exit" or else V.Kind (Result_Path) /= V.Null_Value or else V.Count (Verifiers) = 0 then return False; end if;
            elsif Private_Started then return False;
            end if;
         end;
      end loop;
      return True;
   end Checks;
   type Scalar_Match is record
      Matches : Boolean := False;
      Next : Natural := 0;
   end record;
   function Secret_Letter (Text : String; Position : Natural; Letter : Character) return Scalar_Match is
      Code, Width : Natural;
      First : Natural;
   begin
      if Position >= Text'Length then return (False, Position); end if;
      First := Character'Pos (Text (Text'First + Position));
      if First < 128 then Code := First; Width := 1;
      elsif First in 192 .. 223 then Code := First mod 32; Width := 2;
      elsif First in 224 .. 239 then Code := First mod 16; Width := 3;
      elsif First in 240 .. 244 then Code := First mod 8; Width := 4;
      else return (False, Position);
      end if;
      if Width > Text'Length - Position then return (False, Position); end if;
      for I in 1 .. Width - 1 loop
         declare Next : constant Natural := Character'Pos (Text (Text'First + Position + I));
         begin
            if Next not in 128 .. 191 then return (False, Position); end if;
            Code := Code * 64 + Next mod 64;
         end;
      end loop;
      if Code in Character'Pos ('a') .. Character'Pos ('z') then Code := Code - 32;
      elsif Code = 304 or else Code = 305 then Code := Character'Pos ('I');
      elsif Code = 383 then Code := Character'Pos ('S');
      elsif Code = 8490 then Code := Character'Pos ('K');
      end if;
      return (Code = Character'Pos (Letter), Position + Width);
   end Secret_Letter;
   function Has_Secret (Text : String) return Boolean is
      Words : constant String := "[""TOKEN"",""KEY"",""PASSWORD"",""PASSWD"",""SECRET"",""CREDENTIAL"",""AUTH"",""COOKIE""]";
      Position : Natural;
      Match : Boolean;
   begin
      for I in 0 .. Text'Length loop
         for J in 1 .. V.Count (Words) loop
            declare Word : constant String := V.Text (V.Element (Words, J - 1));
            begin
               Position := I; Match := True;
               for Letter of Word loop
                  declare Step : constant Scalar_Match := Secret_Letter (Text, Position, Letter);
                  begin
                     if not Step.Matches then Match := False; exit; end if;
                     Position := Step.Next;
                  end;
               end loop;
               if Match then return True; end if;
            end;
         end loop;
      end loop;
      return False;
   end Has_Secret;
   function Environment (Value : String) return Boolean is
   begin
      if V.Kind (Value) /= V.Object_Value then return False; end if;
      for I in 1 .. V.Count (Value) loop
         declare Name : constant String := V.Member_Name (Value, V.Parse (Value), I);
         begin
            if V.Kind (V.Field (Value, Name)) /= V.String_Value or else Has_Secret (Name) then return False; end if;
         end;
      end loop;
      return True;
   end Environment;
   function Services (Rows : String) return Boolean is
      Fields_List : constant String := "[""id"",""argv"",""cwd"",""env"",""healthArgv"",""restart""]";
   begin
      if V.Kind (Rows) /= V.Array_Value then return False; end if;
      for I in 1 .. V.Count (Rows) loop
         declare Row : constant String := V.Element (Rows, I - 1);
         begin
            if not Fields (Row, Fields_List, Fields_List) or else
              not Identifier (V.Field (Row, "id"), Rows, I) or else
              not Argv (V.Field (Row, "argv")) or else not Argv (V.Field (Row, "healthArgv")) or else
              not Relative (V.Field (Row, "cwd")) or else not Environment (V.Field (Row, "env")) or else
              not Named (V.Text (V.Field (Row, "restart")), "[""never"",""on-failure""]")
            then return False; end if;
         end;
      end loop;
      return True;
   end Services;
   function Generated (Rows : String) return Boolean is
      Fields_List : constant String := "[""root"",""glob""]";
   begin
      if V.Kind (Rows) /= V.Array_Value then return False; end if;
      for I in 1 .. V.Count (Rows) loop
         declare Row : constant String := V.Element (Rows, I - 1);
         begin
            if not Fields (Row, Fields_List, Fields_List) or else
              V.Kind (V.Field (Row, "root")) /= V.String_Value or else not Relative (V.Field (Row, "glob"))
            then return False; end if;
         end;
      end loop;
      return True;
   end Generated;
   function Valid (Source : String) return Boolean is
   begin
      return Fields (Source, "[""schemaVersion"",""generated"",""checks"",""services""]",
          "[""schemaVersion"",""generated"",""checks"",""services"",""protected""]") and then
        Paths (Defaulted (Source, "protected", "[]")) and then
        Generated (V.Field (Source, "generated")) and then
        Checks (V.Field (Source, "checks")) and then Services (V.Field (Source, "services"));
   end Valid;
end Worldline.Policy_Syntax;
