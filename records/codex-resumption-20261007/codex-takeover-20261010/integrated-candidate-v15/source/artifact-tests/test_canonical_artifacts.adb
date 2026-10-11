with Ada.Text_IO;
with Attest.SHA256;
with Canonical_Artifacts;
with Evaluation_Pending;
with Worldline;
procedure Test_Canonical_Artifacts is
   package C renames Canonical_Artifacts;
   package P renames Evaluation_Pending;
   use type P.Count;
   use type Worldline.Hash;
   function Bytes (Text : String) return P.Bytes is
      A : P.Bytes (17 .. 16 + P.Count (Text'Length));
   begin
      for K in Text'Range loop A (17 + P.Count (K - Text'First)) := P.Byte (Character'Pos (Text (K))); end loop;
      return A;
   end Bytes;
   procedure Check (Name, Text : String; Expected : Boolean) is
      A : constant P.Bytes := Bytes (Text);
   begin
      pragma Assert (C.Canonical (A, (A'First, A'Length)) = Expected);
      Ada.Text_IO.Put_Line ("PASS " & Name);
   end Check;
   procedure Root_View is
      Text : constant String := "{""a"":[{""root"":""nested""}],""root"":""unvalidated spelling"",""z"":""root: text""}";
      Original : constant String := "worldline-evidence-v1{""a"":[{""root"":""nested""}],""z"":""root: text""}";
      A : constant P.Bytes := Bytes (Text);
      Message : Attest.Byte_Array (1 .. Original'Length);
      Actual : constant C.Hash_Result := C.Artifact_Hash (A, (A'First, A'Length), True);
   begin
      for K in Original'Range loop Message (K) := Attest.Byte (Character'Pos (Original (K))); end loop;
      pragma Assert (Actual.Valid and then Actual.Digest = Attest.SHA256.Hash (Message));
      pragma Assert (not C.Root_Matches (A, (A'First, A'Length), Actual.Digest));
      Ada.Text_IO.Put_Line ("PASS only_top_level_root_view");
   end Root_View;
begin
   Check ("null", "null", True);
   Check ("true", "true", True);
   Check ("false", "false", True);
   Check ("integer", "12345678901234567890123456789012345678901234567890", True);
   Check ("negative_integer", "-12345678901234567890123456789012345678901234567890", True);
   Check ("empty_array", "[]", True);
   Check ("empty_object", "{}", True);
   Check ("nested", "{""a"":[null,false,{""root"":""decoy""}],""root"":""outer"",""z"":0}", True);
   Check ("controls", """\u0000\b\t\n\f\r\u001f""", True);
   Check ("leading_space", " null", False);
   Check ("trailing_space", "null ", False);
   Check ("duplicate", "{""a"":null,""a"":true}", False);
   Check ("unsorted", "{""z"":0,""a"":1}", False);
   Check ("minus_zero", "-0", False);
   Check ("leading_zero", "01", False);
   Check ("float", "1.0", False);
   Check ("exponent", "1e0", False);
   Check ("short_escape_required", """\u000a""", False);
   Check ("noncontrol_escape", """\u0061""", False);
   Check ("upper_escape", """\u001F""", False);
   Check ("slash_escape", """\/""", False);
   Check ("trailing_array_comma", "[null,]", False);
   Check ("trailing_object_comma", "{""a"":0,}", False);
   Check ("unfinished", "{""a"":[", False);
   Check ("utf8_scalar", '"' & Character'Val (16#F0#) & Character'Val (16#9F#)
     & Character'Val (16#98#) & Character'Val (16#80#) & '"', True);
   Check ("utf8_overlong", '"' & Character'Val (16#C0#) & Character'Val (16#80#) & '"', False);
   Check ("utf8_surrogate", '"' & Character'Val (16#ED#) & Character'Val (16#A0#)
     & Character'Val (16#80#) & '"', False);
   Root_View;
end Test_Canonical_Artifacts;
