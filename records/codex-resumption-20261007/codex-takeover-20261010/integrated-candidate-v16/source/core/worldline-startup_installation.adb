with Attest.SHA256;
with Interfaces;
with Worldline.Archive_Base64;
with Canonical_Artifacts;
with Worldline.Startup_Source_Custody;

package body Worldline.Startup_Installation with SPARK_Mode is
   package SHA renames Attest.SHA256;
   package B64 renames Worldline.Archive_Base64;
   use type E.Count;
   use type E.Value_Kind;
   use type E.Encoding_Level;
   use type E.Q.Byte;
   use type Attest.Byte;
   use type Interfaces.Unsigned_64;
   use type Canonical_Artifacts.Genesis_Correspondence;
   function F (D : E.Bytes; X : E.Span; Name : String) return E.Span renames S.Field;

   --  Project archive byte views directly. In particular, neither raw installed
   --  files nor the full source envelope are materialized into a second array.
   function Length (D : E.Bytes; X : E.Byte_View) return E.Count;
   function Byte_At (D : E.Bytes; X : E.Byte_View; I : E.Count) return E.Q.Byte;
   function Length (D : E.Bytes; X : E.Byte_View) return E.Count is
      Prior : E.Byte_View;
      N, Padding : E.Count;
   begin
      if X.Level = 0 then return X.Encoded.Length; end if;
      Prior := (X.Encoded, X.Level - 1);
      N := Length (D, Prior);
      if N = 0 then return 0; end if;
      if Byte_At (D, Prior, N - 1) /= Character'Pos ('=') then Padding := 0;
      elsif Byte_At (D, Prior, N - 2) = Character'Pos ('=') then Padding := 2;
      else Padding := 1; end if;
      return (N / 4) * 3 - Padding;
   end Length;
   function Byte_At (D : E.Bytes; X : E.Byte_View; I : E.Count) return E.Q.Byte is
      Prior : E.Byte_View;
      At_Quartet : E.Count;
   begin
      if X.Level = 0 then return D (X.Encoded.First + I); end if;
      Prior := (X.Encoded, X.Level - 1);
      At_Quartet := (I / 3) * 4;
      case I mod 3 is
         when 0 => return B64.Digit (Byte_At (D, Prior, At_Quartet)) * 4 +
           B64.Digit (Byte_At (D, Prior, At_Quartet + 1)) / 16;
         when 1 => return (B64.Digit (Byte_At (D, Prior, At_Quartet + 1)) mod 16) * 16 +
           B64.Digit (Byte_At (D, Prior, At_Quartet + 2)) / 4;
         when others => return (B64.Digit (Byte_At (D, Prior, At_Quartet + 2)) mod 4) * 64 +
           B64.Digit (Byte_At (D, Prior, At_Quartet + 3));
      end case;
   end Byte_At;
   function Payload (D : E.Bytes; X : E.Span; Name : String := "value") return E.Byte_View is
     (E.Decode (D, S.A.Field (D, X, Name), E.Operation).Payload);
   function Equal (D : E.Bytes; A, B : E.Byte_View) return Boolean is
     (Length (D, A) = Length (D, B) and then
      (for all I in E.Count range 1 .. Length (D, A) =>
         Byte_At (D, A, I - 1) = Byte_At (D, B, I - 1)));
   function Same_Text (D : E.Bytes; A, B : E.Span) return Boolean is
     (V.Valid_Text (D, A) and then V.Valid_Text (D, B) and then
      Equal (D, Payload (D, A), Payload (D, B)));
   function Raw_Key_Matches (D : E.Bytes; Key, Text : E.Span) return Boolean is
      K : constant E.View := E.Decode (D, Key, E.Operation);
   begin
      return K.Form = E.Text_Value and then E.Bytes_Valid (D, K.Payload) and then
        V.Valid_Text (D, Text) and then Equal (D, K.Payload, Payload (D, Text));
   end Raw_Key_Matches;
   function Pair_Part (D : E.Bytes; Dict : E.Span; I, Part : E.Count) return E.Span is
      Fields : constant E.View := E.Decode (D, S.A.Field (D, Dict, "fields"), E.Operation);
      Pair : constant E.View := E.Decode (D, E.Array_Element (D, Fields.Children, I), E.Finalization);
   begin
      return E.Array_Element (D, Pair.Children, Part);
   end Pair_Part;

   --  pathlib.Path lexical normalization, not resolve(): '.' and redundant
   --  slashes disappear; '..' remains, and exactly two initial slashes remain.
   type Path_Cursor is record
      Offset, Stop, Roots : E.Count := 0;
      Had_Component, In_Component, Absolute, Finished : Boolean := False;
   end record;
   function Join_Separator (D : E.Bytes; X : E.Byte_View; Suffix : String) return E.Count is
     (if Suffix'Length > 0 and then Length (D, X) > 0 and then
       Byte_At (D, X, Length (D, X) - 1) /= Character'Pos ('/') then 1 else 0);
   function Suffix_Skip (Suffix : String) return E.Count is
     (if Suffix'Length > 0 and then Suffix (Suffix'First) = '/' then 1 else 0);
   function Raw_Length (D : E.Bytes; X : E.Byte_View; Suffix : String) return E.Count is
     (Length (D, X) + Join_Separator (D, X, Suffix) + E.Count (Suffix'Length) - Suffix_Skip (Suffix));
   function Raw_Byte (D : E.Bytes; X : E.Byte_View; Suffix : String; I : E.Count) return E.Q.Byte is
      N : constant E.Count := Length (D, X);
      Separator : constant E.Count := Join_Separator (D, X, Suffix);
   begin
      if I < N then return Byte_At (D, X, I);
      elsif Separator = 1 and then I = N then return Character'Pos ('/');
      else return Character'Pos (Suffix (Suffix'First + Integer (I - N - Separator + Suffix_Skip (Suffix)))); end if;
   end Raw_Byte;
   procedure Initialize (D : E.Bytes; X : E.Byte_View; Suffix : String; C : out Path_Cursor) is
      N : constant E.Count := Raw_Length (D, X, Suffix);
      Start, Slashes : E.Count := 0;
   begin
      C := (others => <>);
      while Start < N and then Raw_Byte (D, X, Suffix, Start) = Character'Pos ('/') loop
         Slashes := Slashes + 1; Start := Start + 1;
      end loop;
      C.Offset := Start;
      C.Roots := (if Slashes = 2 then 2 elsif Slashes > 0 then 1 else 0);
      C.Absolute := Slashes > 0;
   end Initialize;
   procedure Next_Path
     (D : E.Bytes; X : E.Byte_View; Suffix : String; C : in out Path_Cursor;
      Present : out Boolean; Value : out E.Q.Byte)
   is
      N : constant E.Count := Raw_Length (D, X, Suffix);
      First : E.Count;
   begin
      Present := True; Value := 0;
      if C.Finished then Present := False; return; end if;
      if C.Roots > 0 then C.Roots := C.Roots - 1; Value := Character'Pos ('/');
         C.Had_Component := False; return; end if;
      if C.In_Component then
         Value := Raw_Byte (D, X, Suffix, C.Offset); C.Offset := C.Offset + 1;
         if C.Offset = C.Stop then C.In_Component := False; end if;
         return;
      end if;
      loop
         while C.Offset < N and then Raw_Byte (D, X, Suffix, C.Offset) = Character'Pos ('/') loop
            C.Offset := C.Offset + 1;
         end loop;
         First := C.Offset;
         while C.Offset < N and then Raw_Byte (D, X, Suffix, C.Offset) /= Character'Pos ('/') loop
            C.Offset := C.Offset + 1;
         end loop;
         exit when C.Offset = First or else C.Offset - First /= 1 or else
           Raw_Byte (D, X, Suffix, First) /= Character'Pos ('.');
      end loop;
      if C.Offset = First then
         C.Finished := True;
         if not C.Had_Component and then not C.Absolute then Value := Character'Pos ('.');
         else Present := False; end if;
         return;
      end if;
      C.Stop := C.Offset; C.Offset := First; C.In_Component := True;
      if C.Had_Component then Value := Character'Pos ('/');
      else
         Value := Raw_Byte (D, X, Suffix, C.Offset); C.Offset := C.Offset + 1;
         if C.Offset = C.Stop then C.In_Component := False; end if;
      end if;
      C.Had_Component := True;
   end Next_Path;
   function Paths_Match (D : E.Bytes; A, B : E.Byte_View; Suffix : String) return Boolean is
      CA, CB : Path_Cursor;
      PA, PB : Boolean;
      BA, BB : E.Q.Byte;
   begin
      if Length (D, B) > E.Count'Last - Suffix'Length - 1 then return False; end if;
      Initialize (D, A, "", CA); Initialize (D, B, Suffix, CB);
      loop
         Next_Path (D, A, "", CA, PA, BA); Next_Path (D, B, Suffix, CB, PB, BB);
         if PA /= PB then return False; end if;
         if not PA then return True; end if;
         if BA /= BB then return False; end if;
      end loop;
   end Paths_Match;
   function Path_Bytes_Equivalent (Left, Right : E.Bytes) return Boolean is
      A : constant E.Byte_View := ((Left'First, Left'Length), 0);
      B : constant E.Byte_View := ((Right'First, Right'Length), 0);
      CA, CB : Path_Cursor;
      PA, PB : Boolean;
      BA, BB : E.Q.Byte;
   begin
      Initialize (Left, A, "", CA); Initialize (Right, B, "", CB);
      loop
         Next_Path (Left, A, "", CA, PA, BA); Next_Path (Right, B, "", CB, PB, BB);
         if PA /= PB then return False; end if;
         if not PA then return True; end if;
         if BA /= BB then return False; end if;
      end loop;
   end Path_Bytes_Equivalent;
   function Path_Equivalent (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (V.Valid_Text (Data, Left) and then V.Valid_Text (Data, Right) and then
      Paths_Match (Data, Payload (Data, Left), Payload (Data, Right), ""));
   function Joined_Path (Data : E.Bytes; Word, Base : E.Span; Suffix : String) return Boolean is
     (V.Valid_Text (Data, Word) and then V.Valid_Text (Data, Base) and then
      Paths_Match (Data, Payload (Data, Word), Payload (Data, Base), Suffix));

   function Number (D : E.Bytes; X : E.Span) return V.Count_Result renames V.Nonnegative_Count;
   function Same_Number (D : E.Bytes; A, B : E.Span) return Boolean is
     (V.Is_Integer (D, A) and then V.Is_Integer (D, B) and then S.A.Same_Encoding (D, A, B));
   function Identity_Valid (D : E.Bytes; X : E.Span) return Boolean is
   begin
      if not V.Type_Is (D, X, "dict") or else S.Member_Count (D, X) /= 9 then return False; end if;
      for I in 1 .. 9 loop
         declare Name : constant String := (case I is when 1 => "dev", when 2 => "inode", when 3 => "uid",
           when 4 => "gid", when 5 => "mode", when 6 => "nlink", when 7 => "size",
           when 8 => "mtime_ns", when 9 => "ctime_ns"); begin
            if not V.Is_Integer (D, F (D, X, Name)) or else
               (I <= 7 and then V.Negative (D, F (D, X, Name))) then return False; end if;
         end;
      end loop;
      return True;
   end Identity_Valid;
   function Identity_Field (D : E.Bytes; A, B : E.Span; Name : String) return Boolean is
     (Same_Number (D, F (D, A, Name), F (D, B, Name)));
   function Protected_Identity (D : E.Bytes; Identity : E.Span; Directory : Boolean) return Boolean is
      Mode : constant V.Count_Result := Number (D, F (D, Identity, "mode"));
   begin
      return Identity_Valid (D, Identity) and then Mode.Present and then
        Number (D, F (D, Identity, "uid")).Present and then
        Number (D, F (D, Identity, "uid")).Value = 0 and then
        Mode.Value / 16 mod 2 = 0 and then Mode.Value / 2 mod 2 = 0 and then
        Mode.Value / 4096 mod 16 = (if Directory then 4 else 8);
   end Protected_Identity;
   function Canonical_Absolute (D : E.Bytes; Path : E.Span) return Boolean is
      C : Path_Cursor;
      Present : Boolean;
      Value : E.Q.Byte;
      I : E.Count := 0;
   begin
      if not V.Valid_Text (D, Path) then return False; end if;
      declare P : constant E.Byte_View := Payload (D, Path); N : constant E.Count := Length (D, P); begin
         if N = 0 or else Byte_At (D, P, 0) /= Character'Pos ('/') then return False; end if;
         Initialize (D, P, "", C);
         loop
            Next_Path (D, P, "", C, Present, Value); exit when not Present;
            if I = N or else Value /= Byte_At (D, P, I) or else Value = 0 then return False; end if;
            I := I + 1;
         end loop;
         if I /= N then return False; end if;
         for J in E.Count range 0 .. N - 1 loop
            if Byte_At (D, P, J) = Character'Pos ('.') and then J + 1 < N and then
              Byte_At (D, P, J + 1) = Character'Pos ('.') and then
              (J = 0 or else Byte_At (D, P, J - 1) = Character'Pos ('/')) and then
              (J + 2 = N or else Byte_At (D, P, J + 2) = Character'Pos ('/')) then return False; end if;
         end loop;
         return True;
      end;
   end Canonical_Absolute;
   function Ancestors (D : E.Bytes; Path, Components : E.Span) return Boolean is
   begin
      if not Canonical_Absolute (D, Path) or else not V.Is_Sequence (D, Components) then return False; end if;
      declare P : constant E.Byte_View := Payload (D, Path); N : constant E.Count := Length (D, P);
              Roots : constant E.Count := (if N >= 2 and then Byte_At (D, P, 1) = Character'Pos ('/') then 2 else 1);
              Stop : E.Count := Roots; Found : E.Count; begin
         loop
            Found := 0;
            for I in E.Count range 1 .. V.Count (D, Components) loop
               declare C : constant E.Span := V.Element (D, Components, I - 1);
                       CP : constant E.Span := F (D, C, "path"); begin
                  if V.Valid_Text (D, CP) and then Length (D, Payload (D, CP)) = Stop and then
                    (for all J in E.Count range 0 .. Stop - 1 =>
                      Byte_At (D, Payload (D, CP), J) = Byte_At (D, P, J)) then
                     if not S.Text_Is (D, F (D, C, "kind"), "DIRECTORY") or else
                       not Protected_Identity (D, F (D, C, "identity"), True) then return False; end if;
                     Found := Found + 1;
                  end if;
               end;
            end loop;
            if Found /= 1 then return False; end if;
            exit when Stop = N;
            if Stop = Roots then
               while Stop < N and then Byte_At (D, P, Stop) /= Character'Pos ('/') loop Stop := Stop + 1; end loop;
            else
               Stop := Stop + 1;
               while Stop < N and then Byte_At (D, P, Stop) /= Character'Pos ('/') loop Stop := Stop + 1; end loop;
            end if;
            exit when Stop = N; -- Final component is checked as file/directory separately.
         end loop;
         return True;
      end;
   end Ancestors;
   function Read_Intact (D : E.Bytes; Tree_Entry : E.Span) return Boolean is
      Named : constant E.Span := F (D, Tree_Entry, "identity");
      Held : constant E.Span := F (D, Tree_Entry, "held_identity");
      After : constant E.Span := F (D, Tree_Entry, "after_identity");
      Named_After : constant E.Span := F (D, Tree_Entry, "named_after_identity");
      Raw : constant E.Span := F (D, Tree_Entry, "raw");
      Size : constant V.Count_Result := Number (D, F (D, Held, "size"));
   begin
      if not Identity_Valid (D, Named) or else not Identity_Valid (D, Held) or else
        not Identity_Valid (D, After) or else not Identity_Valid (D, Named_After) or else
        not V.Valid_Bytes (D, Raw) or else not Size.Present or else
        Length (D, Payload (D, Raw)) / 2 /= Size.Value then return False; end if;
      for I in 1 .. 9 loop
         declare Name : constant String := (case I is when 1 => "dev", when 2 => "inode", when 3 => "uid",
           when 4 => "gid", when 5 => "mode", when 6 => "nlink", when 7 => "size",
           when 8 => "mtime_ns", when 9 => "ctime_ns"); begin
            if not Identity_Field (D, Named, Held, Name) or else
               not Identity_Field (D, Held, After, Name) or else
               not Identity_Field (D, After, Named_After, Name) then return False; end if;
         end;
      end loop;
      return True;
   end Read_Intact;
   function Entry_Protected (D : E.Bytes; Tree_Entry, Components : E.Span) return Boolean is
      Directory : constant Boolean := S.Text_Is (D, F (D, Tree_Entry, "kind"), "DIRECTORY");
   begin
      return (Directory or else S.Text_Is (D, F (D, Tree_Entry, "kind"), "REGULAR")) and then
        Protected_Identity (D, F (D, Tree_Entry, "identity"), Directory) and then
        Ancestors (D, F (D, Tree_Entry, "path"), Components) and then
        V.Is_Null (D, F (D, Tree_Entry, "link_target")) and then
        (if Directory then V.Is_Null (D, F (D, Tree_Entry, "raw")) else Read_Intact (D, Tree_Entry));
   end Entry_Protected;
   function Hex_Digit (Value : E.Q.Byte) return E.Q.Byte is
     (if Value in Character'Pos ('0') .. Character'Pos ('9') then Value - Character'Pos ('0')
      else Value - Character'Pos ('a') + 10);
   function Mode_Matches (D : E.Bytes; Word : E.Byte_View; Mode : E.Count; Prefix : Boolean) return Boolean is
      N : constant E.Count := Length (D, Word);
      First : constant E.Count := (if Prefix then 2 else 0);
      Value : E.Count := 0;
   begin
      if N <= First or else (Prefix and then (Byte_At (D, Word, 0) /= Character'Pos ('0') or else
        Byte_At (D, Word, 1) /= Character'Pos ('o'))) or else
        (N - First > 1 and then Byte_At (D, Word, First) = Character'Pos ('0')) then return False; end if;
      for I in E.Count range First .. N - 1 loop
         declare C : constant E.Q.Byte := Byte_At (D, Word, I); begin
            if C not in Character'Pos ('0') .. Character'Pos ('7') or else
              Value > (E.Count'Last - 7) / 8 then return False; end if;
            Value := Value * 8 + E.Count (C - Character'Pos ('0'));
         end;
      end loop;
      return Value = Mode mod 4096;
   end Mode_Matches;
   function Digest_Matches (D : E.Bytes; Raw, Digest : E.Span) return Boolean is
      Context : SHA.Context := SHA.Initial;
      Block : Attest.Byte_Array (0 .. SHA.Block_Bytes - 1);
      Used : Natural := 0;
   begin
      if not V.Valid_Bytes (D, Raw) or else not V.Valid_Text (D, Digest) then return False; end if;
      declare R : constant E.Byte_View := Payload (D, Raw);
              H : constant E.Byte_View := Payload (D, Digest);
              N : constant E.Count := Length (D, R) / 2; begin
         if Length (D, H) /= 64 then return False; end if;
         for I in E.Count range 1 .. N loop
            Block (Used) := Attest.Byte (Hex_Digit (Byte_At (D, R, (I - 1) * 2)) * 16 +
              Hex_Digit (Byte_At (D, R, (I - 1) * 2 + 1)));
            Used := Used + 1;
            if Used = SHA.Block_Bytes then SHA.Update (Context, Block); Used := 0; end if;
         end loop;
         if Used > 0 then SHA.Update (Context, Block (0 .. Used - 1)); end if;
         declare Actual : constant SHA.Digest := SHA.Final (Context);
                 Hex : constant String := "0123456789abcdef"; begin
            for I in Actual'Range loop
               if Byte_At (D, H, E.Count (I) * 2) /= Character'Pos (Hex (Integer (Actual (I) / 16) + 1)) or else
                  Byte_At (D, H, E.Count (I) * 2 + 1) /= Character'Pos (Hex (Integer (Actual (I) mod 16) + 1)) then return False; end if;
            end loop;
         end;
         return True;
      end;
   end Digest_Matches;
   function Manifest_File (D : E.Bytes; Tree_Entry, Expected : E.Span) return Boolean is
      Mode : constant V.Count_Result := Number (D, F (D, F (D, Tree_Entry, "identity"), "mode"));
      Word : constant E.Span := F (D, Expected, "mode");
   begin
      return V.Type_Is (D, Expected, "dict") and then S.Member_Count (D, Expected) = 2 and then
        Mode.Present and then V.Valid_Text (D, Word) and then
        Mode_Matches (D, Payload (D, Word), Mode.Value, True) and then
        Digest_Matches (D, F (D, Tree_Entry, "raw"), F (D, Expected, "sha256"));
   end Manifest_File;
   function Bytecode_Name (D : E.Bytes; Path : E.Span) return Boolean is
      P : constant E.Byte_View := Payload (D, Path);
      N : constant E.Count := Length (D, P);
      Start : E.Count := 0;
      Cache : constant String := "__pycache__";
   begin
      for I in E.Count range 0 .. N - 1 loop
         if Byte_At (D, P, I) = Character'Pos ('/') then Start := I + 1; end if;
      end loop;
      return (N - Start = Cache'Length and then
        (for all I in Cache'Range => Byte_At (D, P, Start + E.Count (I - Cache'First)) = Character'Pos (Cache (I)))) or else
        (N - Start > 4 and then Byte_At (D, P, N - 4) = Character'Pos ('.') and then
         Byte_At (D, P, N - 3) = Character'Pos ('p') and then Byte_At (D, P, N - 2) = Character'Pos ('y') and then
         Byte_At (D, P, N - 1) = Character'Pos ('c'));
   end Bytecode_Name;
   function Tree_Matches (D : E.Bytes; Tree, Expected, Components : E.Span) return Boolean is
      Entries : constant E.Span := F (D, Tree, "entries");
      Root : constant E.Span := F (D, Tree, "path");
      Regulars : E.Count := 0;
   begin
      if not V.Type_Is (D, Expected, "dict") or else not V.Is_Sequence (D, Entries) or else
         not Canonical_Absolute (D, Root) or else not Path_Equivalent (D, Root, F (D, Tree, "selector")) or else
         not Protected_Identity (D, F (D, Tree, "identity"), True) or else not Ancestors (D, Root, Components) then return False; end if;
      for I in E.Count range 1 .. V.Count (D, Entries) loop
         declare Tree_Entry : constant E.Span := V.Element (D, Entries, I - 1);
                 Path : constant E.Span := F (D, Tree_Entry, "path");
                 Relative : constant E.Span := F (D, Tree_Entry, "relative"); Found : E.Count := 0; begin
            if not Entry_Protected (D, Tree_Entry, Components) or else not V.Valid_Text (D, Relative) or else
               Same_Text (D, Root, Path) then return False; end if;
            declare R : constant E.Byte_View := Payload (D, Relative);
                    P : constant E.Byte_View := Payload (D, Path);
                    B : constant E.Byte_View := Payload (D, Root);
                    BN : constant E.Count := Length (D, B);
                    Separator : constant E.Count :=
                      (if Byte_At (D, B, BN - 1) = Character'Pos ('/') then 0 else 1);
                    RN : constant E.Count := Length (D, R); begin
               if RN = 0 or else Byte_At (D, R, 0) = Character'Pos ('/') or else
                 BN > Length (D, P) or else Length (D, P) - BN /= RN + Separator or else
                 (for some K in E.Count range 1 .. BN =>
                    Byte_At (D, B, K - 1) /= Byte_At (D, P, K - 1)) or else
                 (Separator = 1 and then Byte_At (D, P, BN) /= Character'Pos ('/')) or else
                 (for some K in E.Count range 1 .. RN =>
                    Byte_At (D, R, K - 1) /= Byte_At (D, P, BN + Separator + K - 1)) then return False; end if;
            end;
            for J in E.Count range 1 .. I - 1 loop
               if Same_Text (D, Path, F (D, V.Element (D, Entries, J - 1), "path")) then return False; end if;
            end loop;
            if S.Text_Is (D, F (D, Tree_Entry, "kind"), "REGULAR") then
               if Bytecode_Name (D, Path) then return False; end if;
               Regulars := Regulars + 1;
               for J in E.Count range 1 .. S.Member_Count (D, Expected) loop
                  if Raw_Key_Matches (D, Pair_Part (D, Expected, J - 1, 0), Relative) then
                     if not Manifest_File (D, Tree_Entry, Pair_Part (D, Expected, J - 1, 1)) then return False; end if;
                     Found := Found + 1;
                  end if;
               end loop;
               if Found /= 1 then return False; end if;
            end if;
         end;
      end loop;
      -- Every observed directory below this root is also an rglob entry;
      -- ancestors cannot serve as an unenumerated remainder of the tree.
      declare R : constant E.Byte_View := Payload (D, Root);
              RN : constant E.Count := Length (D, R);
              Root_Slash : constant Boolean := Byte_At (D, R, RN - 1) = Character'Pos ('/'); begin
         for I in E.Count range 1 .. V.Count (D, Components) loop
            declare Component : constant E.Span := V.Element (D, Components, I - 1);
                    Path : constant E.Span := F (D, Component, "path");
                    Found : E.Count := 0; begin
               if V.Valid_Text (D, Path) then
                  declare P : constant E.Byte_View := Payload (D, Path); begin
                     if Length (D, P) > RN and then
                       (for all K in E.Count range 1 .. RN => Byte_At (D, R, K - 1) = Byte_At (D, P, K - 1)) and then
                       (Root_Slash or else Byte_At (D, P, RN) = Character'Pos ('/')) then
                        for J in E.Count range 1 .. V.Count (D, Entries) loop
                           declare Entry_Value : constant E.Span := V.Element (D, Entries, J - 1); begin
                              if Same_Text (D, F (D, Entry_Value, "path"), Path) and then
                                S.Text_Is (D, F (D, Entry_Value, "kind"), "DIRECTORY") then Found := Found + 1; end if;
                           end;
                        end loop;
                        if Found /= 1 then return False; end if;
                     end if;
                  end;
               end if;
            end;
         end loop;
      end;
      return Regulars = S.Member_Count (D, Expected);
   end Tree_Matches;

   function Installed_Entry (D : E.Bytes; Inventory, Path : E.Span) return E.Span is
      Files : constant E.Span := F (D, Inventory, "files");
      Trees : constant E.Span := F (D, Inventory, "trees");
      Result : E.Span := (1, 0);
   begin
      for I in E.Count range 1 .. V.Count (D, Files) loop
         declare Entry_Value : constant E.Span := V.Element (D, Files, I - 1); begin
            if Path_Equivalent (D, F (D, Entry_Value, "path"), Path) then Result := Entry_Value; end if;
         end;
      end loop;
      for I in E.Count range 1 .. V.Count (D, Trees) loop
         declare Entries : constant E.Span := F (D, V.Element (D, Trees, I - 1), "entries"); begin
            for J in E.Count range 1 .. V.Count (D, Entries) loop
               declare Entry_Value : constant E.Span := V.Element (D, Entries, J - 1); begin
                  if S.Text_Is (D, F (D, Entry_Value, "kind"), "REGULAR") and then
                    Path_Equivalent (D, F (D, Entry_Value, "path"), Path) then Result := Entry_Value; end if;
               end;
            end loop;
         end;
      end loop;
      return Result;
   end Installed_Entry;
   type Word_Span is record
      First, Length : E.Count := 0;
   end record;
   type Line_Parts is array (1 .. 5) of Word_Span;
   function Envelope_Byte (D : E.Bytes; Hex : E.Byte_View; I : E.Count) return E.Q.Byte is
     (Hex_Digit (Byte_At (D, Hex, I * 2)) * 16 +
      Hex_Digit (Byte_At (D, Hex, I * 2 + 1)));
   procedure Next_Line (D : E.Bytes; Hex : E.Byte_View; Offset : in out E.Count;
     Parts : out Line_Parts; Fields : out Natural; Valid : out Boolean)
   is
      First : E.Count := Offset;
      N : constant E.Count := Length (D, Hex) / 2;
   begin
      Parts := (others => (0, 0)); Fields := 1; Valid := False;
      while Offset < N and then Envelope_Byte (D, Hex, Offset) /= 10 loop
         if Envelope_Byte (D, Hex, Offset) = 9 then
            if Fields = 5 then return; end if;
            Parts (Fields) := (First, Offset - First); Fields := Fields + 1; First := Offset + 1;
         end if;
         Offset := Offset + 1;
      end loop;
      if Offset = N then return; end if;
      Parts (Fields) := (First, Offset - First); Offset := Offset + 1; Valid := True;
   end Next_Line;
   function Envelope_Text (D : E.Bytes; Hex : E.Byte_View; Word : Word_Span; Text : String) return Boolean is
     (Word.Length = Text'Length and then (for all I in Text'Range =>
       Envelope_Byte (D, Hex, Word.First + E.Count (I - Text'First)) = Character'Pos (Text (I))));
   function Envelope_Hex_Path (D : E.Bytes; Envelope : E.Byte_View; Word : Word_Span; Path : E.Span) return Boolean is
      Hex : constant String := "0123456789abcdef";
   begin
      if not V.Valid_Text (D, Path) then return False; end if;
      declare P : constant E.Byte_View := Payload (D, Path); begin
         return Word.Length mod 2 = 0 and then Word.Length / 2 = Length (D, P) and then
           (for all I in E.Count range 1 .. Length (D, P) =>
             Envelope_Byte (D, Envelope, Word.First + (I - 1) * 2) = Character'Pos (Hex (Integer (Byte_At (D, P, I - 1) / 16) + 1)) and then
             Envelope_Byte (D, Envelope, Word.First + (I - 1) * 2 + 1) = Character'Pos (Hex (Integer (Byte_At (D, P, I - 1) mod 16) + 1)));
      end;
   end Envelope_Hex_Path;
   function Executable_Files (D : E.Bytes; Source, Inventory : E.Span) return Boolean is
      Encoded : constant E.Span := F (D, Source, "envelope_bytes_hex");
      Offset : E.Count := 0;
      Parts : Line_Parts;
      Fields : Natural;
      Valid : Boolean;
      Interpreter_Count, Helper_Count, Entry_Count : E.Count := 0;
   begin
      if not V.Valid_Text (D, Encoded) or else not V.Valid_Hex_Field (D, Encoded, "value") then return False; end if;
      declare Envelope : constant E.Byte_View := Payload (D, Encoded); begin
         Next_Line (D, Envelope, Offset, Parts, Fields, Valid);
         if not Valid or else Fields /= 1 or else
           not Envelope_Text (D, Envelope, Parts (1), "WORLDLINE-APPROVED-SOURCE-ENVELOPE-V1") then return False; end if;
         while Offset < Length (D, Envelope) / 2 loop
            Next_Line (D, Envelope, Offset, Parts, Fields, Valid);
            if not Valid then return False; end if;
            if Fields = 5 and then Envelope_Text (D, Envelope, Parts (1), "FILE") and then
              (Envelope_Text (D, Envelope, Parts (2), "HELPER") or else
               Envelope_Text (D, Envelope, Parts (2), "ENTRY") or else
               Envelope_Text (D, Envelope, Parts (2), "INTERPRETER") or else
               Envelope_Text (D, Envelope, Parts (2), "EXECUTABLE") or else
               Envelope_Text (D, Envelope, Parts (2), "SOURCE") or else
               Envelope_Text (D, Envelope, Parts (2), "EXTENSION") or else
               Envelope_Text (D, Envelope, Parts (2), "CACHE")) then
               declare Found : E.Count := 0;
                       Trees : constant E.Span := F (D, Inventory, "trees");
                       Files : constant E.Span := F (D, Inventory, "files");
                       procedure Check (Entry_Value : E.Span) is
                          Mode : constant V.Count_Result := Number (D, F (D, F (D, Entry_Value, "identity"), "mode"));
                          Bytes : constant E.Span := F (D, Entry_Value, "raw");
                          Octal : E.Count := 0;
                       begin
                          if not S.Text_Is (D, F (D, Entry_Value, "kind"), "REGULAR") or else
                            not Envelope_Hex_Path (D, Envelope, Parts (3), F (D, Entry_Value, "path")) then return; end if;
                          if not Mode.Present or else not V.Valid_Bytes (D, Bytes) or else Parts (4).Length = 0 then return; end if;
                          if Parts (4).Length > 1 and then
                            Envelope_Byte (D, Envelope, Parts (4).First) = Character'Pos ('0') then return; end if;
                          for I in E.Count range 1 .. Parts (4).Length loop
                             declare C : constant E.Q.Byte := Envelope_Byte (D, Envelope, Parts (4).First + I - 1); begin
                                if C not in Character'Pos ('0') .. Character'Pos ('7') or else
                                  Octal > (E.Count'Last - 7) / 8 then return; end if;
                                Octal := Octal * 8 + E.Count (C - Character'Pos ('0'));
                             end;
                          end loop;
                          declare H : constant E.Byte_View := Payload (D, Bytes); begin
                             if Octal /= Mode.Value mod 4096 or else Parts (5).Length /= Length (D, H) then return; end if;
                             if Envelope_Text (D, Envelope, Parts (2), "EXECUTABLE") and then
                               (Octal / 64) mod 2 = 0 and then (Octal / 8) mod 2 = 0 and then Octal mod 2 = 0
                             then return; end if;
                             for I in E.Count range 1 .. Parts (5).Length loop
                                if Envelope_Byte (D, Envelope, Parts (5).First + I - 1) /= Byte_At (D, H, I - 1) then return; end if;
                             end loop;
                             Found := Found + 1;
                          end;
                       end Check;
               begin
                  for I in E.Count range 1 .. V.Count (D, Files) loop Check (V.Element (D, Files, I - 1)); end loop;
                  for I in E.Count range 1 .. V.Count (D, Trees) loop
                     declare Entries : constant E.Span := F (D, V.Element (D, Trees, I - 1), "entries"); begin
                        for J in E.Count range 1 .. V.Count (D, Entries) loop Check (V.Element (D, Entries, J - 1)); end loop;
                     end;
                  end loop;
                  if Found = 0 then return False; end if;
                  if Envelope_Text (D, Envelope, Parts (2), "INTERPRETER") then
                     if not Envelope_Hex_Path (D, Envelope, Parts (3), F (D, Source, "interpreter")) then return False; end if;
                     Interpreter_Count := Interpreter_Count + 1;
                  end if;
                  if Envelope_Text (D, Envelope, Parts (2), "HELPER") then
                     if not Envelope_Hex_Path (D, Envelope, Parts (3), F (D, Inventory, "helper")) then return False; end if;
                     Helper_Count := Helper_Count + 1;
                  end if;
                  if Envelope_Text (D, Envelope, Parts (2), "ENTRY") then Entry_Count := Entry_Count + 1; end if;
               end;
            end if;
         end loop;
      end;
      return Interpreter_Count = 1 and then Helper_Count = 1 and then Entry_Count > 0;
   end Executable_Files;

   function Corresponds (Data : E.Bytes; Roster, Profile : E.Span) return Boolean is
      Spec : constant E.Span := F (Data, Roster, "installation");
      Inventory : constant E.Span := F (Data, Profile, "installation_inventory");
      Source : constant E.Span := F (Data, Roster, "source");
      Trees : constant E.Span := F (Data, Inventory, "trees");
      Files : constant E.Span := F (Data, Inventory, "files");
      Components : constant E.Span := F (Data, Inventory, "components");
      Runtime : constant E.Span := F (Data, Spec, "runtime");
      Expected_Trees : constant E.Span := F (Data, Spec, "trees");
      Expected_Files : constant E.Span := F (Data, Spec, "files");
      Flags : constant E.Span := F (Data, Inventory, "interpreter_flags");
      Environment : constant E.Span := F (Data, Inventory, "environment_keys");
      Tools : constant E.Span := F (Data, Runtime, "tools");
      Shared : constant E.Span := F (Data, Runtime, "shared_objects");
      Resolutions : constant E.Span := F (Data, Inventory, "tool_resolutions");
   begin
      if not V.Type_Is (Data, Spec, "dict") or else not V.Type_Is (Data, Inventory, "dict") or else
        not V.Type_Is (Data, Expected_Trees, "dict") or else S.Member_Count (Data, Expected_Trees) = 0 or else
        not V.Type_Is (Data, Expected_Files, "dict") or else S.Member_Count (Data, Expected_Files) = 0 or else
        not V.Is_Sequence (Data, Trees) or else not V.Is_Sequence (Data, Files) or else
        not V.Is_Sequence (Data, Components) or else
        V.Count (Data, Trees) /= S.Member_Count (Data, Expected_Trees) or else
        V.Count (Data, Files) /= S.Member_Count (Data, Expected_Files) then return False; end if;
      for I in E.Count range 1 .. S.Member_Count (Data, Expected_Trees) loop
         declare Found : E.Count := 0; begin
            for J in E.Count range 1 .. V.Count (Data, Trees) loop
               declare Tree : constant E.Span := V.Element (Data, Trees, J - 1); begin
                  if Raw_Key_Matches (Data, Pair_Part (Data, Expected_Trees, I - 1, 0), F (Data, Tree, "selector")) then
                     if not Tree_Matches (Data, Tree, Pair_Part (Data, Expected_Trees, I - 1, 1), Components) then return False; end if;
                     Found := Found + 1;
                  end if;
               end;
            end loop;
            if Found /= 1 then return False; end if;
         end;
      end loop;
      for I in E.Count range 1 .. S.Member_Count (Data, Expected_Files) loop
         declare Found : E.Count := 0; begin
            for J in E.Count range 1 .. V.Count (Data, Files) loop
               declare Entry_Value : constant E.Span := V.Element (Data, Files, J - 1); begin
                  if Raw_Key_Matches (Data, Pair_Part (Data, Expected_Files, I - 1, 0), F (Data, Entry_Value, "selector")) then
                     if not S.Text_Is (Data, F (Data, Entry_Value, "kind"), "REGULAR") or else
                       not Path_Equivalent (Data, F (Data, Entry_Value, "path"), F (Data, Entry_Value, "selector")) or else
                       not Entry_Protected (Data, Entry_Value, Components) or else
                       not Manifest_File (Data, Entry_Value, Pair_Part (Data, Expected_Files, I - 1, 1)) then return False; end if;
                     Found := Found + 1;
                  end if;
               end;
            end loop;
            if Found /= 1 then return False; end if;
         end;
      end loop;
      if not V.Type_Is (Data, Runtime, "dict") or else
        (S.Member_Count (Data, Runtime) /= 9 and then S.Member_Count (Data, Runtime) /= 10)
      then return False; end if;
      for I in 1 .. 9 loop
         declare Name : constant String := (case I is when 1 => "interpreter", when 2 => "worldline_source",
           when 3 => "gate_source", when 4 => "principal_source", when 5 => "native_library",
           when 6 => "proof_manifest", when 7 => "proof_summary", when 8 => "tools", when 9 => "shared_objects"); begin
            if F (Data, Runtime, Name).Length = 0 then return False; end if;
            if I /= 2 and then I <= 7 and then Installed_Entry (Data, Inventory, F (Data, Runtime, Name)).Length = 0 then return False; end if;
         end;
      end loop;
      if S.Member_Count (Data, Runtime) = 10 then
         declare Scoped : constant E.Span := F (Data, Inventory, "resource_scoped_producer");
                 Selected : constant E.Span := F (Data, Runtime, "resource_scoped_producer");
                 Config : constant E.Span := F (Data, Scoped, "config");
                 Raw : constant E.Span := F (Data, Scoped, "raw");
                 Entry_Value : constant E.Span := Installed_Entry (Data, Inventory, Selected);
                 Helper : constant E.Span := F (Data, Tools, "resource_supervisor_v3"); begin
            if S.Member_Count (Data, Scoped) /= 3 or else not V.Valid_Bytes (Data, Raw) or else
              not Joined_Path (Data, Selected, F (Data, F (Data, Spec, "paths"), "authority_root"),
                "/authority/resource/run-scoped-config-v1.json") or else
              not Path_Equivalent (Data, Selected, F (Data, Scoped, "path")) or else
              Entry_Value.Length = 0 or else not Equal (Data, Payload (Data, Raw), Payload (Data, F (Data, Entry_Value, "raw"))) or else
              not Worldline.Startup_Source_Custody.Role_Selected (Data, Source, Selected, "DATA") or else
              not Worldline.Startup_Source_Custody.File_Corresponds (Data, Source, Selected, Raw) or else
              not V.Type_Is (Data, Config, "dict") or else
              not Path_Equivalent (Data, F (Data, Config, "helper"), Helper) or else
              Installed_Entry (Data, Inventory, Helper).Length = 0 or else
              not Worldline.Startup_Source_Custody.Role_Selected (Data, Source, Helper, "EXECUTABLE")
            then return False; end if;
            declare B : constant E.Bytes := V.Bytes_Value (Data, Raw); begin
               if Canonical_Artifacts.Scoped_Archive_JSON_Matches (B, Data, (B'First, B'Length), Config) /=
                 Canonical_Artifacts.Typed_Tree_Matches_Source_Custody_Open then return False; end if;
            end;
         end;
      end if;
      if not Path_Equivalent (Data, F (Data, F (Data, Inventory, "interpreter"), "path"), F (Data, Runtime, "interpreter")) or else
        not Same_Text (Data, F (Data, Source, "interpreter"), F (Data, Installed_Entry (Data, Inventory, F (Data, Runtime, "interpreter")), "path")) or else
        not Path_Equivalent (Data, F (Data, Inventory, "helper_module"), F (Data, Inventory, "helper")) or else
        Installed_Entry (Data, Inventory, F (Data, Inventory, "helper")).Length = 0 or else
        not Joined_Path (Data, F (Data, Inventory, "startup_module"), F (Data, Runtime, "worldline_source"), "runtime/worldline/protected_startup.py") then return False; end if;
      for I in 1 .. 2 loop
         declare Name : constant String := (if I = 1 then "isolated" else "no_site");
                 Flag : constant V.Count_Result := Number (Data, F (Data, Flags, Name)); begin
            if not Flag.Present or else Flag.Value = 0 then return False; end if;
         end;
      end loop;
      declare Flag : constant E.Span := F (Data, Flags, "dont_write_bytecode");
              Actual : constant E.View := E.Decode (Data, S.A.Field (Data, Flag, "value"), E.Operation); begin
         if not V.Type_Is (Data, Flag, "bool") or else Actual.Form /= E.Boolean_Value or else not Actual.Boolean_Bit then return False; end if;
      end;
      if not V.Type_Is (Data, Tools, "dict") or else S.Member_Count (Data, Tools) = 0 or else
        not V.Type_Is (Data, Shared, "list") or else not V.Type_Is (Data, Resolutions, "dict") or else
        S.Member_Count (Data, Resolutions) /= S.Member_Count (Data, Tools) or else
        not V.Is_Sequence (Data, Environment) then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Environment) loop
         declare Key : constant E.Span := V.Element (Data, Environment, I - 1); begin
            if not V.Valid_Text (Data, Key) then return False; end if;
            declare K : constant E.Byte_View := Payload (Data, Key);
                    function Prefix (Text : String) return Boolean is
                      (Length (Data, K) >= Text'Length and then (for all J in Text'Range =>
                        Byte_At (Data, K, E.Count (J - Text'First)) = Character'Pos (Text (J)))); begin
               if Prefix ("PYTHON") or else Prefix ("LD_") then return False; end if;
            end;
         end;
      end loop;
      for I in E.Count range 1 .. V.Count (Data, Shared) loop
         if Installed_Entry (Data, Inventory, V.Element (Data, Shared, I - 1)).Length = 0 then return False; end if;
      end loop;
      for I in E.Count range 1 .. S.Member_Count (Data, Tools) loop
         declare Expected : constant E.Span := Pair_Part (Data, Tools, I - 1, 1);
                 Key : constant E.Span := Pair_Part (Data, Tools, I - 1, 0);
                 Found : E.Count := 0; begin
            if Installed_Entry (Data, Inventory, Expected).Length = 0 then return False; end if;
            for J in E.Count range 1 .. S.Member_Count (Data, Resolutions) loop
               declare Other_Key : constant E.Span := Pair_Part (Data, Resolutions, J - 1, 0);
                       K : constant E.View := E.Decode (Data, Key, E.Operation);
                       O : constant E.View := E.Decode (Data, Other_Key, E.Operation); begin
                  if K.Form = E.Text_Value and then O.Form = E.Text_Value and then Equal (Data, K.Payload, O.Payload) then
                     if not Path_Equivalent (Data, Expected, Pair_Part (Data, Resolutions, J - 1, 1)) then return False; end if;
                     Found := Found + 1;
                  end if;
               end;
            end loop;
            if Found /= 1 then return False; end if;
         end;
      end loop;
      return Executable_Files (Data, Source, Inventory);
   end Corresponds;

   function Cross_View (A, B : E.Bytes; Left, Right : E.Byte_View) return Boolean is
     (Length (A, Left) = Length (B, Right) and then
      (for all I in E.Count range 1 .. Length (A, Left) =>
        Byte_At (A, Left, I - 1) = Byte_At (B, Right, I - 1)));
   function Cross_Encoding (A, B : E.Bytes; Left, Right : E.Span) return Boolean is
     (E.C.P.Valid (A, Left) and then E.C.P.Valid (B, Right) and then
      Left.Length = Right.Length and then
      (for all I in E.Count range 1 .. Left.Length =>
        A (Left.First + I - 1) = B (Right.First + I - 1)));
   function Semantic_Same (A, B : E.Bytes; Left, Right : E.Span) return Boolean is
      N : E.Count;
   begin
      if not S.Valid (A, Left) or else not S.Valid (B, Right) then return False; end if;
      if V.Type_Is (A, Left, "dict") then
         if not V.Type_Is (B, Right, "dict") then return False; end if;
         N := S.Member_Count (A, Left);
         if N /= S.Member_Count (B, Right) then return False; end if;
         for I in E.Count range 1 .. N loop
            declare Key : constant E.View := E.Decode (A, Pair_Part (A, Left, I - 1, 0), E.Operation);
                    Found : E.Count := 0; begin
               for J in E.Count range 1 .. N loop
                  declare Other : constant E.View := E.Decode (B, Pair_Part (B, Right, J - 1, 0), E.Operation); begin
                     if Key.Form = E.Text_Value and then Other.Form = E.Text_Value and then
                       Cross_View (A, B, Key.Payload, Other.Payload) then
                        if not Semantic_Same (A, B, Pair_Part (A, Left, I - 1, 1),
                          Pair_Part (B, Right, J - 1, 1)) then return False; end if;
                        Found := Found + 1;
                     end if;
                  end;
               end loop;
               if Found /= 1 then return False; end if;
            end;
         end loop;
         return True;
      elsif V.Is_Sequence (A, Left) then
         if not V.Is_Sequence (B, Right) or else V.Count (A, Left) /= V.Count (B, Right) then return False; end if;
         for I in E.Count range 1 .. V.Count (A, Left) loop
            if not Semantic_Same (A, B, V.Element (A, Left, I - 1), V.Element (B, Right, I - 1)) then return False; end if;
         end loop;
         return True;
      else
         --  Original scoped scalar encodings are canonical and lossless.
         return Cross_Encoding (A, B, Left, Right);
      end if;
   end Semantic_Same;
   function Directory_Stable (A, B : E.Bytes; Left, Right : E.Span) return Boolean is
   begin
      if not Identity_Valid (A, Left) or else not Identity_Valid (B, Right) then return False; end if;
      for I in 1 .. 6 loop
         declare Name : constant String := (case I is when 1 => "dev", when 2 => "inode",
           when 3 => "uid", when 4 => "gid", when 5 => "mode", when 6 => "nlink"); begin
            if not Semantic_Same (A, B, F (A, Left, Name), F (B, Right, Name)) then return False; end if;
         end;
      end loop;
      return True;
   end Directory_Stable;
   function Entries_Stable
     (A, B : E.Bytes; Left, Right : E.Span; Trees : Boolean;
      Selectors : Boolean := False) return Boolean;
   function Entry_Stable
     (A, B : E.Bytes; Left, Right : E.Span; Tree : Boolean) return Boolean
   is
      Directory : constant Boolean := Tree or else S.Text_Is (A, F (A, Left, "kind"), "DIRECTORY");
   begin
      if not V.Type_Is (A, Left, "dict") or else not V.Type_Is (B, Right, "dict") or else
        S.Member_Count (A, Left) /= S.Member_Count (B, Right) then return False; end if;
      if not Tree and then not Semantic_Same (A, B, F (A, Left, "kind"), F (B, Right, "kind")) then return False; end if;
      for I in E.Count range 1 .. S.Member_Count (A, Left) loop
         declare Key : constant E.View := E.Decode (A, Pair_Part (A, Left, I - 1, 0), E.Operation);
                 Found : E.Count := 0; begin
            for J in E.Count range 1 .. S.Member_Count (B, Right) loop
               declare Other : constant E.View := E.Decode (B, Pair_Part (B, Right, J - 1, 0), E.Operation);
                       Value : constant E.Span := Pair_Part (A, Left, I - 1, 1);
                       Other_Value : constant E.Span := Pair_Part (B, Right, J - 1, 1); begin
                  if Key.Form = E.Text_Value and then Other.Form = E.Text_Value and then Cross_View (A, B, Key.Payload, Other.Payload) then
                     if Directory and then E.Text_Is (A, Key, "identity") then
                        if not Directory_Stable (A, B, Value, Other_Value) then return False; end if;
                     elsif Tree and then E.Text_Is (A, Key, "entries") then
                        if not Entries_Stable (A, B, Value, Other_Value, False) then return False; end if;
                     elsif not Semantic_Same (A, B, Value, Other_Value) then return False;
                     end if;
                     Found := Found + 1;
                  end if;
               end;
            end loop;
            if Found /= 1 then return False; end if;
         end;
      end loop;
      return True;
   end Entry_Stable;
   function Entries_Stable
     (A, B : E.Bytes; Left, Right : E.Span; Trees : Boolean;
      Selectors : Boolean := False) return Boolean
   is
      Name : constant String := (if Trees or Selectors then "selector" else "path");
   begin
      if not V.Is_Sequence (A, Left) or else not V.Is_Sequence (B, Right) or else
        V.Count (A, Left) /= V.Count (B, Right) then return False; end if;
      for I in E.Count range 1 .. V.Count (A, Left) loop
         declare Entry_Value : constant E.Span := V.Element (A, Left, I - 1); Found : E.Count := 0; begin
            for J in E.Count range 1 .. V.Count (B, Right) loop
               declare Other : constant E.Span := V.Element (B, Right, J - 1); begin
                  if Semantic_Same (A, B, F (A, Entry_Value, Name), F (B, Other, Name)) then
                     if not Entry_Stable (A, B, Entry_Value, Other, Trees) then return False; end if;
                     Found := Found + 1;
                  end if;
               end;
            end loop;
            if Found /= 1 then return False; end if;
         end;
      end loop;
      return True;
   end Entries_Stable;
   function Environment_Stable (A, B : E.Bytes; Left, Right : E.Span) return Boolean is
   begin
      if not V.Is_Sequence (A, Left) or else not V.Is_Sequence (B, Right) or else
        V.Count (A, Left) /= V.Count (B, Right) then return False; end if;
      for I in E.Count range 1 .. V.Count (A, Left) loop
         declare Found : E.Count := 0; begin
            for J in E.Count range 1 .. V.Count (B, Right) loop
               if Semantic_Same (A, B, V.Element (A, Left, I - 1), V.Element (B, Right, J - 1)) then Found := Found + 1; end if;
            end loop;
            if Found /= 1 then return False; end if;
         end;
      end loop;
      return True;
   end Environment_Stable;
   function Stable
     (Before_Data, After_Data : E.Bytes;
      Before_Profile, After_Profile : E.Span) return Boolean
   is
      A : constant E.Span := F (Before_Data, Before_Profile, "installation_inventory");
      B : constant E.Span := F (After_Data, After_Profile, "installation_inventory");
   begin
      if not V.Type_Is (Before_Data, A, "dict") or else not V.Type_Is (After_Data, B, "dict") or else
        S.Member_Count (Before_Data, A) /= S.Member_Count (After_Data, B) then return False; end if;
      for I in E.Count range 1 .. S.Member_Count (Before_Data, A) loop
         declare Key : constant E.View := E.Decode (Before_Data, Pair_Part (Before_Data, A, I - 1, 0), E.Operation);
                 Value : constant E.Span := Pair_Part (Before_Data, A, I - 1, 1);
                 Found : E.Count := 0; begin
            for J in E.Count range 1 .. S.Member_Count (After_Data, B) loop
               declare Other : constant E.View := E.Decode (After_Data, Pair_Part (After_Data, B, J - 1, 0), E.Operation);
                       Other_Value : constant E.Span := Pair_Part (After_Data, B, J - 1, 1); begin
                  if Key.Form = E.Text_Value and then Other.Form = E.Text_Value and then
                    Cross_View (Before_Data, After_Data, Key.Payload, Other.Payload) then
                     if E.Text_Is (Before_Data, Key, "trees") then
                        if not Entries_Stable (Before_Data, After_Data, Value, Other_Value, True) then return False; end if;
                     elsif E.Text_Is (Before_Data, Key, "files") then
                        if not Entries_Stable (Before_Data, After_Data, Value, Other_Value, False, True) then return False; end if;
                     elsif E.Text_Is (Before_Data, Key, "components") then
                        if not Entries_Stable (Before_Data, After_Data, Value, Other_Value, False) then return False; end if;
                     elsif E.Text_Is (Before_Data, Key, "environment_keys") then
                        if not Environment_Stable (Before_Data, After_Data, Value, Other_Value) then return False; end if;
                     elsif not Semantic_Same (Before_Data, After_Data, Value, Other_Value) then return False;
                     end if;
                     Found := Found + 1;
                  end if;
               end;
            end loop;
            if Found /= 1 then return False; end if;
         end;
      end loop;
      return True;
   end Stable;
end Worldline.Startup_Installation;
