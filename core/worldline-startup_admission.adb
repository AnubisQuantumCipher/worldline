with Ada.Characters.Latin_1;
with Canonical_Artifacts;
with Attest;
with Interfaces;
with Worldline.Custody_V2_Domain_Hmac;
with Worldline.Custody_V2_Owner_Correspondence;
with Worldline.Startup_Source_Custody;
with Worldline.Startup_Issuer_Source;
with Worldline.Startup_Installation;
package body Worldline.Startup_Admission with SPARK_Mode is
   package E renames L.E;
   package V renames L.V;
   package S renames V.S;
   package J renames Canonical_Artifacts;
   package H renames Worldline.Custody_V2_Domain_Hmac;
   use type E.Count;
   use type E.Bytes;
   use type E.Value_Kind;
   use type L.Decode_Status;
   use type J.Genesis_Correspondence;
   package Install renames Worldline.Startup_Installation;
   use type J.JSON_Kind;
   use type Interfaces.Unsigned_64;
   use type E.Q.Byte;
   function F (D : E.Bytes; X : E.Span; Name : String) return E.Span
     renames S.Field;
   function Same (D : E.Bytes; A, B : E.Span) return Boolean is
     (S.Valid (D, A) and then S.Valid (D, B) and then S.A.Same_Encoding (D, A, B));
   function Cross (A, B : E.Bytes; X, Y : E.Span) return Boolean is
     (J.P.Valid (A, X) and then J.P.Valid (B, Y) and then X.Length = Y.Length and then
      (for all I in E.Count range 1 .. X.Length => A (X.First + I - 1) = B (Y.First + I - 1)));
   subtype U64 is Interfaces.Unsigned_64;
   function Number (D : E.Bytes; X : E.Span) return Boolean is
     (V.Is_Integer (D, X) or else V.Type_Is (D, X, "bool") or else V.Type_Is (D, X, "float"));
   function Integer_Magnitude (D : E.Bytes; X : E.Span) return E.Bytes is
     (if V.Is_Integer (D, X) then V.Magnitude_Value (D, X) else
       E.Bytes'(1 => (if E.Decode (D, S.A.Field (D, X, "value"), E.Operation).Boolean_Bit then 1 else 0)));
   function Float_Bits (D : E.Bytes; X : E.Span) return U64 is
      Result : U64 := 0;
      function Digit (Byte : E.Q.Byte) return U64 is
        (if Byte in Character'Pos ('0') .. Character'Pos ('9') then U64 (Byte - Character'Pos ('0'))
         else U64 (Byte - Character'Pos ('a') + 10));
   begin
      if not V.Valid_Hex_Field (D, X, "bits") then return 16#7FF8_0000_0000_0000#; end if;
      declare Hex : constant E.Bytes := V.Hex_Text (D, X, "bits"); begin
         if Hex'Length /= 16 then return 16#7FF8_0000_0000_0000#; end if;
         for Byte of Hex loop
            Result := Interfaces.Shift_Left (Result, 4) or Digit (Byte);
         end loop;
      end;
      return Result;
   end Float_Bits;
   function Float_Integer_Equal (Bits : U64; D : E.Bytes; X : E.Span) return Boolean is
      Exponent : constant U64 := Interfaces.Shift_Right (Bits, 52) and 16#7FF#;
      Mantissa : U64 := Bits and 16#000F_FFFF_FFFF_FFFF#;
      Shift : Integer := (if Exponent = 0 then -1074 else Integer (Exponent) - 1075);
      Width : E.Count := 0;
      Mag : constant E.Bytes := Integer_Magnitude (D, X);
      Used : E.Count := Mag'Length;
      Negative : constant Boolean := V.Is_Integer (D, X) and then V.Negative (D, X);
   begin
      if Exponent = 16#7FF# then return False; end if;
      while Used > 0 and then Mag (Mag'First + Used - 1) = 0 loop
         pragma Loop_Invariant (Used <= Mag'Length);
         pragma Loop_Variant (Decreases => Used);
         Used := Used - 1;
      end loop;
      if Exponent /= 0 then Mantissa := Mantissa or 16#0010_0000_0000_0000#; end if;
      if Mantissa = 0 then return Used = 0; end if;
      if Used = 0 or else Negative /= ((Bits and 16#8000_0000_0000_0000#) /= 0) then return False; end if;
      if Shift < 0 then
         if Shift <= -64 or else
           (Mantissa and (Interfaces.Shift_Left (U64 (1), Natural (-Shift)) - 1)) /= 0 then return False; end if;
         Mantissa := Interfaces.Shift_Right (Mantissa, Natural (-Shift));
         Shift := 0;
      end if;
      declare Remaining : U64 := Mantissa; begin
         while Remaining > 0 loop
            pragma Loop_Variant (Decreases => Remaining);
            Width := Width + 1;
            Remaining := Remaining / 2;
         end loop;
      end;
      if Used /= (Width + E.Count (Shift) + 7) / 8 then return False; end if;
      for I in E.Count range 0 .. Used - 1 loop
         declare Expected : E.Q.Byte := 0; begin
            for K in 0 .. 7 loop
               declare Bit : constant Integer := Integer (I * 8) + K - Shift; begin
                  if Bit in 0 .. 63 and then (Interfaces.Shift_Right (Mantissa, Natural (Bit)) and 1) /= 0 then
                     Expected := Expected + E.Q.Byte (2 ** K);
                  end if;
               end;
            end loop;
            if Mag (Mag'First + I) /= Expected then return False; end if;
         end;
      end loop;
      return True;
   end Float_Integer_Equal;
   function Numeric_Equal (A, B : E.Bytes; X, Y : E.Span) return Boolean is
   begin
      if V.Type_Is (A, X, "float") then
         declare Bits : constant U64 := Float_Bits (A, X); begin
            if V.Type_Is (B, Y, "float") then
               declare Other : constant U64 := Float_Bits (B, Y); begin
                  return (Interfaces.Shift_Right (Bits, 52) and 16#7FF#) /= 16#7FF# and then
                    (Interfaces.Shift_Right (Other, 52) and 16#7FF#) /= 16#7FF# and then
                    (Bits = Other or else ((Bits and 16#7FFF_FFFF_FFFF_FFFF#) = 0 and then
                     (Other and 16#7FFF_FFFF_FFFF_FFFF#) = 0));
               end;
            end if;
            return Float_Integer_Equal (Bits, B, Y);
         end;
      elsif V.Type_Is (B, Y, "float") then return Float_Integer_Equal (Float_Bits (B, Y), A, X);
      end if;
      declare Left : constant E.Bytes := Integer_Magnitude (A, X);
              Right : constant E.Bytes := Integer_Magnitude (B, Y);
              LL : E.Count := Left'Length;
              RL : E.Count := Right'Length; begin
         while LL > 0 and then Left (Left'First + LL - 1) = 0 loop
            pragma Loop_Invariant (LL <= Left'Length);
            pragma Loop_Variant (Decreases => LL);
            LL := LL - 1;
         end loop;
         while RL > 0 and then Right (Right'First + RL - 1) = 0 loop
            pragma Loop_Invariant (RL <= Right'Length);
            pragma Loop_Variant (Decreases => RL);
            RL := RL - 1;
         end loop;
         if LL /= RL then return False; end if;
         if LL = 0 then return True; end if;
         return (V.Is_Integer (A, X) and then V.Negative (A, X)) =
           (V.Is_Integer (B, Y) and then V.Negative (B, Y)) and then
           (for all I in E.Count range 0 .. LL - 1 => Left (Left'First + I) = Right (Right'First + I));
      end;
   end Numeric_Equal;
   function Semantic_Same (A, B : E.Bytes; X, Y : E.Span) return Boolean
     with Subprogram_Variant => (Decreases => X.Length);
   function Semantic_Same (A, B : E.Bytes; X, Y : E.Span) return Boolean is
   begin
      if not S.Valid (A, X) or else not S.Valid (B, Y) then return False; end if;
      if Number (A, X) and then Number (B, Y) then return Numeric_Equal (A, B, X, Y); end if;
      if V.Type_Is (A, X, "dict") then
         if not V.Type_Is (B, Y, "dict") or else S.Member_Count (A, X) /= S.Member_Count (B, Y) then return False; end if;
         declare XO : constant E.View := E.Decode (A, S.A.Field (A, X, "fields"), E.Operation);
                 YO : constant E.View := E.Decode (B, S.A.Field (B, Y, "fields"), E.Operation); begin
            if XO.Form /= E.Object_Value or else YO.Form /= E.Object_Value then return False; end if;
            for I in E.Count range 1 .. E.Array_Length (A, XO.Children) loop
               declare XP : constant E.View := E.Decode (A, E.Array_Element (A, XO.Children, I - 1), E.Finalization);
                       Found : E.Count := 0; begin
                  if XP.Form /= E.List_Value or else E.Array_Length (A, XP.Children) /= 2 then return False; end if;
                  for K in E.Count range 1 .. E.Array_Length (B, YO.Children) loop
                     pragma Loop_Invariant (Found < K);
                     declare YP : constant E.View := E.Decode (B, E.Array_Element (B, YO.Children, K - 1), E.Finalization); begin
                        if YP.Form /= E.List_Value or else E.Array_Length (B, YP.Children) /= 2 then return False; end if;
                        if Cross (A, B, E.Array_Element (A, XP.Children, 0), E.Array_Element (B, YP.Children, 0)) then
                           if not Semantic_Same (A, B, E.Array_Element (A, XP.Children, 1), E.Array_Element (B, YP.Children, 1)) then return False; end if;
                           Found := Found + 1;
                        end if;
                     end;
                  end loop;
                  if Found /= 1 then return False; end if;
               end;
            end loop;
            return True;
         end;
      elsif V.Type_Is (A, X, "list") or else V.Type_Is (A, X, "tuple") then
         if not Cross (A, B, S.A.Field (A, X, "type"), S.A.Field (B, Y, "type")) or else V.Count (A, X) /= V.Count (B, Y) then return False; end if;
         for I in E.Count range 1 .. V.Count (A, X) loop
            if not Semantic_Same (A, B, V.Element (A, X, I - 1), V.Element (B, Y, I - 1)) then return False; end if;
         end loop;
         return True;
      end if;
      return Cross (A, B, X, Y);
   end Semantic_Same;
   function Stable_Database_Identity (A, B : E.Bytes; X, Y : E.Span) return Boolean is
   begin
      for I in 1 .. 6 loop
         declare Name : constant String := (case I is when 1 => "device", when 2 => "inode",
           when 3 => "uid", when 4 => "gid", when 5 => "mode", when others => "nlink");
                 Left : constant E.Span := F (A, X, Name);
                 Right : constant E.Span := F (B, Y, Name); begin
            if I < 6 or else Left.Length > 0 or else Right.Length > 0 then
               if not Cross (A, B, Left, Right) then return False; end if;
            end if;
         end;
      end loop;
      return True;
   end Stable_Database_Identity;
   function Raw (D : E.Bytes; X : E.Span) return E.Bytes is
     (if V.Valid_Bytes (D, X) then V.Bytes_Value (D, X) else E.Bytes'(1 .. 0 => 0));
   function JSON_Matches (D : E.Bytes; Bytes, Value : E.Span) return Boolean is
   begin
      if not V.Valid_Bytes (D, Bytes) then return False; end if;
      declare B : constant E.Bytes := V.Bytes_Value (D, Bytes); begin
         return J.Scoped_Archive_JSON_Matches (B, D, (B'First, B'Length), Value) =
           J.Typed_Tree_Matches_Source_Custody_Open;
      end;
   end JSON_Matches;
   function Hash_Matches (D : E.Bytes; Text : E.Span; B : E.Bytes) return Boolean is
      Context : H.SHA.Context := H.SHA.Initial;
      Hex_Digits : constant String := "0123456789abcdef";
   begin
      if not V.Valid_Text (D, Text) then return False; end if;
      for Byte of B loop H.SHA.Update (Context, Attest.Byte_Array'(0 => Byte)); end loop;
      declare Sum : constant H.SHA.Digest := H.SHA.Final (Context);
              T : constant E.Bytes := V.Text_Value (D, Text); begin
         return T'Length = Sum'Length * 2 and then
           (for all I in Sum'Range =>
             T (T'First + E.Count (I - Sum'First) * 2) =
               Character'Pos (Hex_Digits (Integer (Sum (I) / 16) + 1)) and then
             T (T'First + E.Count (I - Sum'First) * 2 + 1) =
               Character'Pos (Hex_Digits (Integer (Sum (I) mod 16) + 1)));
      end;
   end Hash_Matches;
   function Joined (D : E.Bytes; Word, Base : E.Span; Suffix : String) return Boolean
     renames Install.Joined_Path;
   function Path (D : E.Bytes; Paths, Word : E.Span) return E.Span is
      Result : E.Span := (1, 0);
   begin
      for I in E.Count range 1 .. V.Count (D, Paths) loop
         declare Item : constant E.Span := V.Element (D, Paths, I - 1); begin
            if Install.Path_Equivalent (D, F (D, Item, "path"), Word) then
               if Result.Length > 0 then return (1, 0); end if;
               Result := Item;
            end if;
         end;
      end loop;
      return Result;
   end Path;
   function Suffix_Path (D : E.Bytes; Paths, Base : E.Span; Suffix : String) return E.Span is
      Result : E.Span := (1, 0);
   begin
      for I in E.Count range 1 .. V.Count (D, Paths) loop
         declare Item : constant E.Span := V.Element (D, Paths, I - 1); begin
            if Joined (D, F (D, Item, "path"), Base, Suffix) then
               if Result.Length > 0 then return (1, 0); end if;
               Result := Item;
            end if;
         end;
      end loop;
      return Result;
   end Suffix_Path;
   function Table (D : E.Bytes; DB : E.Span; Name : String) return E.Span is
      Tables : constant E.Span := F (D, DB, "tables");
      Result : E.Span := (1, 0);
   begin
      for I in E.Count range 1 .. V.Count (D, Tables) loop
         declare Item : constant E.Span := V.Element (D, Tables, I - 1); begin
            if S.Text_Is (D, F (D, Item, "name"), Name) then
               if Result.Length > 0 then return (1, 0); end if;
               Result := Item;
            end if;
         end;
      end loop;
      return Result;
   end Table;
   function Columns (D : E.Bytes; T : E.Span; Names : String; Count : E.Count) return Boolean is
      C : constant E.Span := F (D, T, "columns");
      Start : Positive := Names'First;
      Index : E.Count := 0;
   begin
      if V.Count (D, C) /= Count then return False; end if;
      for I in Names'Range loop
         if Names (I) = ',' then
            if not S.Text_Is (D, V.Element (D, V.Element (D, C, Index), 1), Names (Start .. I - 1)) then return False; end if;
            Index := Index + 1; Start := I + 1;
         end if;
      end loop;
      return S.Text_Is (D, V.Element (D, V.Element (D, C, Index), 1), Names (Start .. Names'Last));
   end Columns;
   function Singleton (D : E.Bytes; X : E.Span; Text : String) return Boolean is
     (V.Count (D, X) = 1 and then V.Count (D, V.Element (D, X, 0)) = 1 and then
      S.Text_Is (D, V.Element (D, V.Element (D, X, 0), 0), Text));
   function Cell_Matches (D : E.Bytes; SQL, Snapshot : E.Span) return Boolean is
      Kind : constant E.Span := F (D, Snapshot, "type");
      Value : constant E.Span := F (D, Snapshot, "value");
   begin
      if V.Valid_Bytes (D, SQL) then
         return V.Valid_Text (D, F (D, Snapshot, "blob")) and then
           V.Text_Value (D, F (D, Snapshot, "blob")) = V.Hex_Text (D, SQL, "value");
      end if;
      return Same (D, SQL, Value) and then
        ((V.Is_Integer (D, SQL) and then S.Text_Is (D, Kind, "int")) or else
         (V.Valid_Text (D, SQL) and then S.Text_Is (D, Kind, "str")) or else
         (V.Is_Null (D, SQL) and then S.Text_Is (D, Kind, "NoneType")) or else
         (V.Type_Is (D, SQL, "float") and then S.Text_Is (D, Kind, "float")));
   end Cell_Matches;
   function Row_Matches (D : E.Bytes; SQL, Snapshot : E.Span) return Boolean is
   begin
      if not V.Is_Sequence (D, SQL) or else not V.Is_Sequence (D, Snapshot) or else
         V.Count (D, SQL) = 0 or else V.Count (D, SQL) - 1 /= V.Count (D, Snapshot) then return False; end if;
      for I in E.Count range 1 .. V.Count (D, Snapshot) loop
         if not Cell_Matches (D, V.Element (D, SQL, I), V.Element (D, Snapshot, I - 1)) then return False; end if;
      end loop;
      return True;
   end Row_Matches;
   function SQLite_Excluded (D : E.Bytes; Name : E.Span) return Boolean is
      Prefix : constant String := "sqlite";
   begin
      if not V.Valid_Text (D, Name) then return False; end if;
      declare N : constant E.Bytes := V.Text_Value (D, Name); begin
         if N'Length < 7 then return False; end if;
         for K in Prefix'Range loop
            declare Byte : E.Q.Byte := N (N'First + E.Count (K - Prefix'First)); begin
               if Byte in Character'Pos ('A') .. Character'Pos ('Z') then Byte := Byte + 32; end if;
               if Byte /= Character'Pos (Prefix (K)) then return False; end if;
            end;
         end loop;
         return True;
      end;
   end SQLite_Excluded;
   function Non_Internal_Tables (D : E.Bytes; DB : E.Span) return E.Count is
      Result : E.Count := 0;
      Tables : constant E.Span := F (D, DB, "tables");
   begin
      for K in E.Count range 1 .. V.Count (D, Tables) loop
         if not SQLite_Excluded (D, F (D, V.Element (D, Tables, K - 1), "name")) then Result := Result + 1; end if;
      end loop;
      return Result;
   end Non_Internal_Tables;
   function Store_Matches (D : E.Bytes; DB, Snapshot : E.Span) return Boolean is
      Schema : constant E.Span := F (D, DB, "schema");
      Snap_Schema : constant E.Span := F (D, Snapshot, "schema");
      Tables : constant E.Span := F (D, DB, "tables");
      Snap_Tables : constant E.Span := F (D, Snapshot, "tables");
      Seen : E.Count := 0;
   begin
      if not V.Is_Sequence (D, Schema) or else not V.Is_Sequence (D, Snap_Schema) or else
         not Same (D, V.Element (D, V.Element (D, F (D, DB, "user_version"), 0), 0), F (D, Snapshot, "version")) then return False; end if;
      for I in E.Count range 1 .. V.Count (D, Schema) loop
         declare R : constant E.Span := V.Element (D, Schema, I - 1);
                 Name : constant E.Span := V.Element (D, R, 1);
                 Found : E.Count := 0; begin
            if not SQLite_Excluded (D, Name) then
               Seen := Seen + 1;
               for K in E.Count range 1 .. V.Count (D, Snap_Schema) loop
                  declare R2 : constant E.Span := V.Element (D, Snap_Schema, K - 1); begin
                     if V.Count (D, R) = 5 and then V.Count (D, R2) = 4 and then
                        Same (D, V.Element (D, R, 0), V.Element (D, R2, 0)) and then
                        Same (D, Name, V.Element (D, R2, 1)) and then
                        Same (D, V.Element (D, R, 2), V.Element (D, R2, 2)) and then
                        Same (D, V.Element (D, R, 4), V.Element (D, R2, 3)) then Found := Found + 1; end if;
                  end;
               end loop;
               if Found /= 1 then return False; end if;
            end if;
         end;
      end loop;
      if Seen /= V.Count (D, Snap_Schema) then return False; end if;
      Seen := 0;
      for I in E.Count range 1 .. V.Count (D, Tables) loop
         declare T : constant E.Span := V.Element (D, Tables, I - 1);
                 Name : constant E.Span := F (D, T, "name");
                 Rows : constant E.Span := F (D, T, "rows");
                 N : constant E.Bytes := (if V.Valid_Text (D, Name) then V.Text_Value (D, Name) else E.Bytes'(1 .. 0 => 0)); begin
            if not SQLite_Excluded (D, Name) then
               Seen := Seen + 1;
               declare Text : String (1 .. Integer (N'Length)); begin
                  for K in Text'Range loop Text (K) := Character'Val (N (N'First + E.Count (K - 1))); end loop;
                  declare Snap_Rows : constant E.Span := F (D, Snap_Tables, Text); begin
                     if not V.Is_Sequence (D, Snap_Rows) or else V.Count (D, Rows) /= V.Count (D, Snap_Rows) then return False; end if;
                     for K in E.Count range 1 .. V.Count (D, Rows) loop
                        declare R : constant E.Span := V.Element (D, Rows, K - 1);
                                Actual, Expected : E.Count := 0; begin
                           -- SQL rowid is not part of the original store_snapshot.
                           for M in E.Count range 1 .. V.Count (D, Rows) loop
                              declare R2 : constant E.Span := V.Element (D, Rows, M - 1);
                                      Equal : Boolean := V.Count (D, R) = V.Count (D, R2); begin
                                 for C in E.Count range 1 .. V.Count (D, R) - 1 loop
                                    Equal := Equal and then Same (D, V.Element (D, R, C), V.Element (D, R2, C));
                                 end loop;
                                 if Equal then Actual := Actual + 1; end if;
                              end;
                           end loop;
                           for M in E.Count range 1 .. V.Count (D, Snap_Rows) loop
                              if Row_Matches (D, R, V.Element (D, Snap_Rows, M - 1)) then Expected := Expected + 1; end if;
                           end loop;
                           if Actual /= Expected then return False; end if;
                        end;
                     end loop;
                  end;
               end;
            end if;
         end;
      end loop;
      return V.Type_Is (D, Snap_Tables, "dict") and then S.Member_Count (D, Snap_Tables) = Seen;
   end Store_Matches;
   function Ledger_Valid (D : E.Bytes; DB, Spec, Genesis : E.Span) return Boolean is
      Identity : constant E.Span := Table (D, DB, "bootstrap_identity");
      Intents : constant E.Span := Table (D, DB, "journal_intents");
      History : constant E.Span := Table (D, DB, "journal_history");
      Rows : constant E.Span := F (D, Intents, "rows");
      Events : constant E.Span := F (D, History, "rows");
      Origin : constant E.Span := F (D, Genesis, "journals");
      Total : E.Count := 0;
   begin
      if Non_Internal_Tables (D, DB) /= 3 or else
         not Singleton (D, F (D, DB, "integrity"), "ok") or else
         not Singleton (D, F (D, DB, "journal_mode"), "wal") or else
         not Columns (D, Identity, "installation_id,genesis_sha256", 2) or else
         not Columns (D, Intents, "name,path,initial_envelope,state", 4) or else
         not Columns (D, History, "ordinal,name,prior,state,envelope_sha256", 5) or else
         V.Count (D, F (D, Identity, "rows")) /= 1 or else V.Count (D, Rows) /= 2 then return False; end if;
      for I in E.Count range 1 .. V.Count (D, F (D, DB, "schema")) loop
         declare R : constant E.Span := V.Element (D, F (D, DB, "schema"), I - 1); begin
            if S.Text_Is (D, V.Element (D, R, 0), "trigger") or else S.Text_Is (D, V.Element (D, R, 0), "view") then return False; end if;
         end;
      end loop;
      if not Same (D, V.Element (D, V.Element (D, F (D, Identity, "rows"), 0), 1), F (D, Spec, "installation_id")) then return False; end if;
      for I in E.Count range 1 .. 2 loop
         declare Name : constant String := (if I = 1 then "recovery-full-journal" else "full-use-reservations");
                 Record_Value : constant E.Span := F (D, Origin, Name);
                 Found : E.Count := 0; begin
            for K in E.Count range 1 .. V.Count (D, Rows) loop
               declare R : constant E.Span := V.Element (D, Rows, K - 1);
                       State : constant E.Span := V.Element (D, R, 4);
                       Initial : constant E.Span := V.Element (D, R, 3);
                       Matched : E.Count := 0; begin
                  if S.Text_Is (D, V.Element (D, R, 1), Name) then
                     Found := Found + 1;
                     if V.Count (D, R) /= 5 or else not Install.Path_Equivalent (D, V.Element (D, R, 2), F (D, Record_Value, "path")) or else
                        not JSON_Matches (D, Initial, F (D, Record_Value, "initial_envelope")) or else
                        not V.Valid_Bytes (D, Initial) then return False; end if;
                     declare B : constant E.Bytes := V.Bytes_Value (D, Initial); begin
                        if B'Length = 0 or else B (B'Last) /= Character'Pos (Ada.Characters.Latin_1.LF) then return False; end if;
                        for M in E.Count range 1 .. V.Count (D, Events) loop
                           declare Event : constant E.Span := V.Element (D, Events, M - 1); begin
                              if S.Text_Is (D, V.Element (D, Event, 2), Name) then
                                 Matched := Matched + 1; Total := Total + 1;
                                 if V.Count (D, Event) /= 6 or else not Same (D, V.Element (D, Event, 0), V.Element (D, Event, 1)) or else
                                    not Hash_Matches (D, V.Element (D, Event, 5), B) or else
                                    (Matched = 1 and then (not S.Text_Is (D, V.Element (D, Event, 3), "UNUSED") or else not S.Text_Is (D, V.Element (D, Event, 4), "INTENT"))) or else
                                    (Matched = 2 and then (not S.Text_Is (D, V.Element (D, Event, 3), "INTENT") or else not S.Text_Is (D, V.Element (D, Event, 4), "CONSUMED"))) or else Matched > 2 then return False; end if;
                              end if;
                           end;
                        end loop;
                     end;
                     if not ((S.Text_Is (D, State, "UNUSED") and then Matched = 0) or else
                             (S.Text_Is (D, State, "INTENT") and then Matched = 1) or else
                             (S.Text_Is (D, State, "CONSUMED") and then Matched = 2)) then return False; end if;
                  end if;
               end;
            end loop;
            if Found /= 1 then return False; end if;
         end;
      end loop;
      return Total = V.Count (D, Events);
   end Ledger_Valid;
   function Original_Current_Valid
     (D : E.Bytes; Roster : E.Span; Mutable_Target : E.Span := (1, 0)) return Boolean is
      Before : constant E.Span := F (D, Roster, "before");
      Current : constant E.Span := F (D, Roster, "current");
      Spec : constant E.Span := F (D, Current, "installation");
      Paths : constant E.Span := F (D, Current, "paths");
      Old_Paths : constant E.Span := F (D, Before, "paths");
      Selected : constant E.Span := F (D, Spec, "provisioned_state");
      Locks : constant E.Span := F (D, Current, "held_locks");
      Source : constant E.Span := F (D, Current, "source");
      Authority : constant E.Span := F (D, F (D, Spec, "paths"), "authority_root");
      State : constant E.Span := F (D, F (D, Spec, "paths"), "state");
      Transactions : constant E.Span := F (D, Spec, "actuator_transactions");
      function Has (Base : E.Span; Suffix : String) return Boolean is
        (Suffix_Path (D, Paths, Base, Suffix).Length > 0);
      function Held (Base : E.Span; Suffix : String) return Boolean is
         Found : E.Count := 0;
      begin
         for I in E.Count range 1 .. V.Count (D, Locks) loop
            if Joined (D, F (D, V.Element (D, Locks, I - 1), "path"), Base, Suffix)
            then Found := Found + 1; end if;
         end loop;
         return Found = 1;
      end Held;
   begin
      if not S.Valid (D, Roster) or else
         not Same (D, F (D, Before, "installation"), Spec) or else
         not Same (D, F (D, Before, "descriptor_raw"), F (D, Current, "descriptor_raw")) or else
         not Same (D, F (D, Before, "source"), Source) or else
         not Same (D, F (D, Before, "held_locks"), Locks) or else
         not V.Is_Sequence (D, Paths) or else not V.Type_Is (D, Selected, "list") or else V.Count (D, Selected) = 0 or else
         V.Count (D, Paths) /= V.Count (D, Old_Paths) or else
         not S.Text_Is (D, F (D, Source, "schema"), "worldline.approved-executed-code-observation-v1") or else
         not V.Valid_Text (D, F (D, Source, "envelope_bytes_hex")) or else
         not Install.Path_Equivalent (D, F (D, Source, "interpreter"), F (D, F (D, Spec, "runtime"), "interpreter")) or else
         not V.Is_Sequence (D, F (D, Source, "events")) or else V.Count (D, F (D, Source, "events")) = 0 or else
         not Held (State, "/worldline-store.lock") or else
         not Held (Authority, "/authority/gate/state/gate.lock") or else
         not Held (Authority, "/authority/state/broker.lock") or else
         not Held (Authority, "/authority/issuer/state/issuer.lock") or else
         not Has (State, "/worldline.sqlite3") or else
         not Has (State, "/worldline-store.lock") or else
         not Has (State, "/evaluation-pending.db") or else
         not Has (State, "/evaluation-pending-target.db") or else
         not Has (State, "/evaluation-terminal.db") or else
         not Has (State, "/evaluation-terminal-target.db") or else
         not Has (State, "/evaluation-finalization.db") or else
         not Has (F (D, F (D, Spec, "paths"), "runtime"), "/admission-ledger.json") or else
         not Has (F (D, F (D, Spec, "paths"), "runtime"), "/admission.lock") or else
         not Has (F (D, F (D, Spec, "paths"), "config"), "/config.json") or else
         not Has (Authority, "/authority/gate/config.json") or else
         not Has (Authority, "/authority/gate/state/journal.json") or else
         not Has (Authority, "/authority/state/authority.json") or else
         not Has (Authority, "/canonical/state.json") or else
         not Has (Authority, "/authority/issuer/state/issuer-key.bin") or else
         not Has (Authority, "/authority/issuer/state/policy.json") or else
         not Has (Authority, "/authority/issuer/state/head.json") or else
         not Has (Authority, "/authority/issuer/state/capabilities.sqlite") or else
         not Has (Authority, "/authority/universe/root/universe-key.bin") or else
         not Has (Authority, "/authority/universe/root/genesis.json") or else
         not Has (Authority, "/authority/universe/root/registry.json") or else
         not Has (Authority, "/authority/universe/root/universes.sqlite") or else
         not Has (Authority, "/authority/evidence/state/evidence.lock") or else
         not Has (Authority, "/authority/evidence/state/key.bin") or else
         not Has (Authority, "/authority/evidence/state/policy.json") or else
         not Has (Authority, "/authority/evidence/state/head.json") or else
         not Has (Authority, "/authority/evidence/state/evidence.sqlite") then return False; end if;
      for I in E.Count range 1 .. V.Count (D, Paths) loop
         declare Item : constant E.Span := V.Element (D, Paths, I - 1);
                 Word : constant E.Span := F (D, Item, "path");
                 Found : E.Count := 0; begin
            declare Old : constant E.Span := V.Element (D, Old_Paths, I - 1);
                    Before_DB : constant E.Span := F (D, Old, "logical_database");
                    Current_DB : constant E.Span := F (D, Item, "logical_database"); begin
               if not Same (D, F (D, Old, "path"), Word) then return False; end if;
               if Mutable_Target.Length = 0 or else not Install.Path_Equivalent (D, Word, Mutable_Target) then
                  if not V.Valid_Bytes (D, F (D, Item, "raw")) then return False; end if;
                  if Before_DB.Length > 0 or else Current_DB.Length > 0 then
                     if not Stable_Database_Identity (D, D, F (D, Old, "identity"), F (D, Item, "identity")) then return False; end if;
                  elsif not Same (D, F (D, Old, "identity"), F (D, Item, "identity")) then return False;
                  end if;
                  if Before_DB.Length > 0 or else Current_DB.Length > 0 then
                     if not Same (D, Before_DB, Current_DB) then return False; end if;
                  elsif not Same (D, F (D, Old, "raw"), F (D, Item, "raw")) then return False;
                  end if;
               end if;
            end;
            for K in E.Count range 1 .. V.Count (D, Selected) loop
               if Install.Path_Equivalent (D, Word, V.Element (D, Selected, K - 1)) then Found := Found + 1; end if;
            end loop;
            if (Found = 0 and then
               not Install.Path_Equivalent (D, Word, F (D, Spec, "bootstrap_ledger")) and then
               not Install.Path_Equivalent (D, Word, F (D, Spec, "genesis")) and then
               not Install.Path_Equivalent (D, Word, F (D, Current, "descriptor_path"))) or else
               Path (D, Paths, Word).Length = 0 then return False; end if;
         end;
      end loop;
      for I in E.Count range 1 .. V.Count (D, Selected) loop
         if Path (D, Paths, V.Element (D, Selected, I - 1)).Length = 0 then return False; end if;
      end loop;
      for I in E.Count range 1 .. V.Count (D, Locks) loop
         declare Lock : constant E.Span := V.Element (D, Locks, I - 1);
                 Named : constant E.Span := Path (D, Paths, F (D, Lock, "path")); begin
            if Named.Length = 0 then return False; end if;
            for K in 1 .. 4 loop
               declare Field_Name : constant String :=
                 (case K is when 1 => "device", when 2 => "inode", when 3 => "uid", when 4 => "gid"); begin
                  if not Same (D, F (D, F (D, Lock, "identity"), Field_Name),
                     F (D, F (D, Named, "identity"), Field_Name)) then return False; end if;
               end;
            end loop;
            for K in E.Count range 1 .. I - 1 loop
               if Same (D, F (D, Lock, "path"), F (D, V.Element (D, Locks, K - 1), "path")) then return False; end if;
            end loop;
         end;
      end loop;
      if not V.Is_Sequence (D, Transactions) then return False; end if;
      for I in E.Count range 1 .. V.Count (D, Transactions) loop
         declare Name : constant E.Span := V.Element (D, Transactions, I - 1); begin
            if not V.Valid_Text (D, Name) then return False; end if;
            declare N : constant E.Bytes := V.Text_Value (D, Name);
                    Text : String (1 .. Integer (N'Length)); begin
               if N'Length = 0 then return False; end if;
               for K in Text'Range loop Text (K) := Character'Val (N (N'First + E.Count (K - 1))); end loop;
               if Text = "." or else Text = ".." or else (for some C of Text => C = '/') or else
                  not Held (Authority, "/canonical/actuator/" & Text & "/service.lock") then return False; end if;
               for K in E.Count range 1 .. I - 1 loop
                  if Same (D, Name, V.Element (D, Transactions, K - 1)) then return False; end if;
               end loop;
            end;
         end;
      end loop;
      return True;
   end Original_Current_Valid;
   function Store_Identity (D : E.Bytes; DB, Genesis : E.Span) return Boolean is
      Rows : constant E.Span := F (D, Table (D, DB, "meta"), "rows");
      Identity, Finalization : E.Count := 0;
   begin
      if not Columns (D, Table (D, DB, "meta"), "key,value", 2) then return False; end if;
      for I in E.Count range 1 .. V.Count (D, Rows) loop
         declare Row : constant E.Span := V.Element (D, Rows, I - 1);
                 Cell : constant E.Span := V.Element (D, Row, 2); begin
            if S.Text_Is (D, V.Element (D, Row, 1), "protectedStoreGenesis") or else
               S.Text_Is (D, V.Element (D, Row, 1), "finalizationStoreId") then
               if not V.Valid_Bytes (D, Cell) and then not V.Valid_Text (D, Cell) then return False; end if;
               declare B : constant E.Bytes :=
                 (if V.Valid_Bytes (D, Cell) then V.Bytes_Value (D, Cell) else V.Text_Value (D, Cell)); begin
                  if S.Text_Is (D, V.Element (D, Row, 1), "protectedStoreGenesis") then
                     Identity := Identity + 1;
                     if J.Scoped_Archive_JSON_Matches (B, D, (B'First, B'Length),
                       F (D, F (D, Genesis, "store"), "identity")) /= J.Typed_Tree_Matches_Source_Custody_Open then return False; end if;
                  else
                     Finalization := Finalization + 1;
                     if not J.Canonical_JSON_Valid (B, (B'First, B'Length)) or else
                        J.JSON_Prefix (B, (B'First, B'Length), 0).Form /= J.String_JSON_Value then return False; end if;
                  end if;
               end;
            end if;
         end;
      end loop;
      return Identity = 1 and then Finalization = 1;
   end Store_Identity;
   function Object_Has (D : E.Bytes; Item : E.Span; Names : String; Count : E.Count) return Boolean is
      Start : Positive := Names'First;
   begin
      if not V.Type_Is (D, Item, "dict") or else S.Member_Count (D, Item) /= Count then return False; end if;
      for I in Names'Range loop
         if Names (I) = ',' then
            if I = Start or else F (D, Item, Names (Start .. I - 1)).Length = 0 then return False; end if;
            Start := I + 1;
         end if;
      end loop;
      return Start <= Names'Last and then F (D, Item, Names (Start .. Names'Last)).Length > 0;
   end Object_Has;
   function Kernel_Identity (D : E.Bytes; Item : E.Span) return Boolean is
      Value : constant V.Count_Result := V.Nonnegative_Count (D, Item);
   begin
      return V.Is_Integer (D, Item) and then Value.Present and then
        Value.Value <= E.Count (Interfaces.Unsigned_32'Last);
   end Kernel_Identity;
   function Protected_Identity (D : E.Bytes; Identity : E.Span; Private_File : Boolean) return Boolean is
      UID : constant V.Count_Result := V.Nonnegative_Count (D, F (D, Identity, "uid"));
      Mode : constant V.Count_Result := V.Nonnegative_Count (D, F (D, Identity, "mode"));
      Links : constant V.Count_Result := V.Nonnegative_Count (D, F (D, Identity, "nlink"));
   begin
      return UID.Present and then UID.Value = 0 and then Mode.Present and then
        (if Private_File then Mode.Value mod 64 = 0 and then Links.Present and then Links.Value = 1
         else (Mode.Value / 8) mod 8 not in 2 | 3 | 6 | 7 and then Mode.Value mod 8 not in 2 | 3 | 6 | 7);
   end Protected_Identity;
   function Common_Source_Corresponds
     (D : E.Bytes; Roster, Profile, Ctx : E.Span; Mutable_Target : E.Span := (1, 0)) return Boolean is
      Current : constant E.Span := F (D, Roster, "current");
      Spec : constant E.Span := F (D, Current, "installation");
      Paths : constant E.Span := F (D, Current, "paths");
      Authority : constant E.Span := F (D, F (D, Spec, "paths"), "authority_root");
      Genesis : constant E.Span := F (D, Ctx, "lease_genesis");
      DB : constant E.Span := F (D, Path (D, Paths, F (D, Spec, "bootstrap_ledger")), "logical_database");
      Gate_Config : constant E.Span := F (D, Suffix_Path (D, Paths, Authority, "/authority/gate/config.json"), "raw");
      Gate_Journal : constant E.Span := F (D, Suffix_Path (D, Paths, Authority, "/authority/gate/state/journal.json"), "raw");
      Store : constant E.Span := Suffix_Path (D, Paths, F (D, F (D, Spec, "paths"), "state"), "/worldline.sqlite3");
      Lease_Raw : constant E.Span := F (D, Ctx, "lease_genesis_raw");
   begin
      if
         not Original_Current_Valid (D, Roster, Mutable_Target) or else
         not Worldline.Startup_Source_Custody.Corresponds (D, F (D, Current, "source"), Spec) or else
         not JSON_Matches (D, F (D, Current, "descriptor_raw"), Spec) or else
         not Worldline.Startup_Source_Custody.File_Corresponds (D, F (D, Current, "source"),
           F (D, Profile, "descriptor_path"), F (D, Current, "descriptor_raw")) or else
         not Worldline.Startup_Source_Custody.File_Corresponds (D, F (D, Current, "source"),
           F (D, Spec, "genesis"), Lease_Raw) or else
         not S.Text_Is (D, F (D, Spec, "schema"), "worldline.protected-startup-v1") or else
         not (Object_Has (D, Spec, "schema,installation_id,trees,files,runtime,paths,genesis,bootstrap_ledger,provisioned_state,actuator_transactions,endpoint", 11) or else
           (Object_Has (D, Spec, "schema,installation_id,trees,files,runtime,paths,genesis,bootstrap_ledger,provisioned_state,actuator_transactions,endpoint,root_worker", 12) and then
            Object_Has (D, F (D, Spec, "root_worker"), "owner_plan", 1) and then
            V.Valid_Text (D, F (D, F (D, Spec, "root_worker"), "owner_plan")) and then
            Worldline.Startup_Source_Custody.File_Corresponds (D, F (D, Current, "source"),
              F (D, F (D, Spec, "root_worker"), "owner_plan"), F (D, Profile, "owner_plan_raw")))) or else
         not V.Valid_Text (D, F (D, Spec, "installation_id")) or else
         V.Text_Value (D, F (D, Spec, "installation_id"))'Length = 0 or else
         not Object_Has (D, Genesis, "schema,installation_id,owner_authorization,store,gate_config,gate_head,issuer_head,journals", 8) or else
         not Object_Has (D, F (D, Genesis, "store"), "identity,schema,version,initial_head", 4) or else
         not V.Valid_Text (D, F (D, F (D, Genesis, "store"), "identity")) or else
         V.Text_Value (D, F (D, F (D, Genesis, "store"), "identity"))'Length = 0 or else
         not Object_Has (D, F (D, Genesis, "journals"), "recovery-full-journal,full-use-reservations", 2) or else
         not Object_Has (D, F (D, F (D, Genesis, "journals"), "recovery-full-journal"), "path,initial_envelope", 2) or else
         not Object_Has (D, F (D, F (D, Genesis, "journals"), "full-use-reservations"), "path,initial_envelope", 2) or else
         not V.Type_Is (D, F (D, F (D, F (D, Genesis, "journals"), "recovery-full-journal"), "initial_envelope"), "dict") or else
         not V.Type_Is (D, F (D, F (D, F (D, Genesis, "journals"), "full-use-reservations"), "initial_envelope"), "dict") or else
         not Object_Has (D, F (D, Spec, "endpoint"), "path,requester_uid,requester_gid", 3) or else
         not Kernel_Identity (D, F (D, F (D, Spec, "endpoint"), "requester_uid")) or else
         not Kernel_Identity (D, F (D, F (D, Spec, "endpoint"), "requester_gid")) or else
         not Joined (D, F (D, F (D, Spec, "endpoint"), "path"), Authority, "/authority/protected-runtime/intent.sock") or else
         not Joined (D, F (D, F (D, F (D, Genesis, "journals"), "recovery-full-journal"), "path"),
           Authority, "/authority/gate/state/recovery-full-journal.json") or else
         not Joined (D, F (D, F (D, F (D, Genesis, "journals"), "full-use-reservations"), "path"),
           Authority, "/authority/issuer/state/full-use-reservations.json") or else
         (Path (D, Paths, F (D, Spec, "genesis")).Length > 0 and then
          not Same (D, Lease_Raw, F (D, Path (D, Paths, F (D, Spec, "genesis")), "raw"))) or else
         not JSON_Matches (D, Lease_Raw, Genesis) or else
         not S.Text_Is (D, F (D, Genesis, "schema"), "worldline.owner-provisioned-genesis-v1") or else
         not Same (D, F (D, Genesis, "installation_id"), F (D, Spec, "installation_id")) or else
         not V.Valid_Text (D, F (D, Genesis, "owner_authorization")) or else V.Text_Value (D, F (D, Genesis, "owner_authorization"))'Length = 0 or else
         not Install.Corresponds (D, Current, Profile) or else not Ledger_Valid (D, DB, Spec, Genesis) or else
         not Hash_Matches (D, V.Element (D, V.Element (D, F (D, Table (D, DB, "bootstrap_identity"), "rows"), 0), 2), Raw (D, Lease_Raw)) or else
         not Same (D, Gate_Config, F (D, Profile, "gate_config_raw")) or else
         not JSON_Matches (D, Gate_Journal, F (D, Profile, "gate_journal")) or else
         not JSON_Matches (D, F (D, Profile, "gate_journal_raw"), F (D, Profile, "gate_journal")) or else
         not JSON_Matches (D, F (D, Profile, "store_snapshot_raw"), F (D, Profile, "store_snapshot")) or else
         not Store_Matches (D, F (D, Store, "logical_database"), F (D, Profile, "store_snapshot")) or else
         not Store_Identity (D, F (D, Store, "logical_database"), Genesis) or else
         not Same (D, F (D, F (D, Profile, "store_snapshot"), "schema"), F (D, F (D, Genesis, "store"), "schema")) or else
         not Semantic_Same (D, D, F (D, F (D, Profile, "store_snapshot"), "version"), F (D, F (D, Genesis, "store"), "version")) then return False; end if;
      if not Worldline.Startup_Issuer_Source.Corresponds (D, Roster, Profile) or else
         not JSON_Matches (D, F (D, Profile, "issuer_head_raw"), F (D, Profile, "issuer_head"))
      then return False; end if;
      return True;
   end Common_Source_Corresponds;
   function Operation_Source_Corresponds
     (Data : L.E.Bytes; Roster, Profile, Target : L.E.Span) return Boolean is
      Current : constant E.Span := F (Data, Roster, "current");
      Spec : constant E.Span := F (Data, Current, "installation");
      Selected : constant E.Span := F (Data, Spec, "provisioned_state");
      Found : E.Count := 0;
      Context : constant E.Span := F (Data, Roster, "operation_context");
   begin
      if not Joined (Data, Target, F (Data, F (Data, Spec, "paths"), "authority_root"),
        "/authority/issuer/state/worldline-operation-head.sqlite") then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Selected) loop
         if Install.Path_Equivalent (Data, Target, V.Element (Data, Selected, I - 1)) then Found := Found + 1; end if;
      end loop;
      return Found > 0 and then Common_Source_Corresponds (Data, Roster, Profile,
        (if F (Data, Context, "lease_genesis_raw").Length > 0 then Context else Profile), Target);
   end Operation_Source_Corresponds;
   function Observe_Source
     (D : E.Bytes; Roster : E.Span; Journal_Name : String; Offline : Boolean;
      Selected_Profile : E.Span := (1, 0)) return Decision is
      Current : constant E.Span := F (D, Roster, "current");
      Spec : constant E.Span := F (D, Current, "installation");
      Paths : constant E.Span := F (D, Current, "paths");
      Authority : constant E.Span := F (D, F (D, Spec, "paths"), "authority_root");
      Profile : constant E.Span := (if Selected_Profile.Length > 0 then Selected_Profile else F (D, Roster, "startup_admission"));
      Ctx : constant E.Span := (if Offline then Profile else F (D, Roster, "operation_context"));
      Genesis : constant E.Span := F (D, Ctx, "lease_genesis");
      Record_Value : constant E.Span := F (D, F (D, Genesis, "journals"), Journal_Name);
      DB : constant E.Span := F (D, Path (D, Paths, F (D, Spec, "bootstrap_ledger")), "logical_database");
      Present : constant E.Span := F (D, Profile, "observed_journal");
      Rows : constant E.Span := F (D, Table (D, DB, "journal_intents"), "rows");
      Gate_Config : constant E.Span := F (D, Suffix_Path (D, Paths, Authority, "/authority/gate/config.json"), "raw");
   begin
      if Journal_Name not in "recovery-full-journal" | "full-use-reservations" or else
         not Common_Source_Corresponds (D, Roster, Profile, Ctx) or else
         not S.Text_Is (D, F (D, Profile, "name"), Journal_Name) or else
         not Install.Path_Equivalent (D, F (D, Profile, "path"), F (D, Record_Value, "path")) or else
         not Joined (D, F (D, Record_Value, "path"), Authority,
            (if Journal_Name = "recovery-full-journal" then "/authority/gate/state/recovery-full-journal.json" else "/authority/issuer/state/full-use-reservations.json")) or else
         not Install.Path_Equivalent (D, F (D, Present, "path"), F (D, Record_Value, "path")) or else
         not (S.Text_Is (D, F (D, Present, "presence"), "PRESENT") or else
              S.Text_Is (D, F (D, Present, "presence"), "ABSENT")) or else
         (S.Text_Is (D, F (D, Present, "presence"), "PRESENT") and then not V.Valid_Bytes (D, F (D, Present, "raw"))) or else
         (S.Text_Is (D, F (D, Present, "presence"), "PRESENT") and then
          not Protected_Identity (D, F (D, Present, "identity"), True)) or else
         (S.Text_Is (D, F (D, Present, "presence"), "ABSENT") and then
          (not V.Is_Null (D, F (D, Present, "raw")) or else not V.Is_Null (D, F (D, Present, "identity")))) or else
         not Protected_Identity (D, F (D, Present, "parent_identity"), False) or else
         not Joined (D, F (D, Present, "parent_path"), Authority,
           (if Journal_Name = "recovery-full-journal" then "/authority/gate/state" else "/authority/issuer/state")) or else
         (Path (D, Paths, F (D, Record_Value, "path")).Length > 0 and then
          not Same (D, F (D, Present, "raw"), F (D, Path (D, Paths, F (D, Record_Value, "path")), "raw"))) then return (Refused, 0); end if;
      for I in E.Count range 1 .. V.Count (D, Rows) loop
         declare Row : constant E.Span := V.Element (D, Rows, I - 1);
                 State : constant E.Span := V.Element (D, Row, 4); begin
            if S.Text_Is (D, V.Element (D, Row, 1), Journal_Name) then
               if S.Text_Is (D, State, "CONSUMED") then
                  if S.Text_Is (D, F (D, Present, "presence"), "PRESENT") then
                     return (Already_Consumed, 0);
                  else
                     return (Refused, 1);
                  end if;
               end if;
               if not Semantic_Same (D, D, F (D, Profile, "initial_envelope"), F (D, Record_Value, "initial_envelope")) or else
                  not Same (D, F (D, Profile, "initial_envelope_raw"), V.Element (D, Row, 3)) then return (Refused, 5); end if;
               if not JSON_Matches (D, F (D, Profile, "store_initial_snapshot_raw"), F (D, Profile, "store_initial_snapshot")) or else
                  not Hash_Matches (D, F (D, Profile, "store_initial_head"), Raw (D, F (D, Profile, "store_initial_snapshot_raw"))) then return (Refused, 0); end if;
               if not Hash_Matches (D, F (D, Genesis, "gate_config"), Raw (D, Gate_Config)) or else
                  not Hash_Matches (D, F (D, Genesis, "gate_head"), Raw (D, F (D, Profile, "gate_journal_raw"))) or else
                  not Semantic_Same (D, D, F (D, Genesis, "issuer_head"), F (D, Profile, "issuer_head")) or else
                  not Same (D, F (D, F (D, Genesis, "store"), "initial_head"), F (D, Profile, "store_initial_head")) then return (Refused, 6); end if;
               if S.Text_Is (D, F (D, Present, "presence"), "ABSENT") then
                  if S.Text_Is (D, State, "INTENT") then return (Refused, 2); end if;
                  if Offline then
                     return (Create_Unused_Offline, 0);
                  else
                     return (Refused, 0);
                  end if;
               end if;
               if not Same (D, F (D, Present, "raw"), V.Element (D, Row, 3)) then
                  if S.Text_Is (D, State, "INTENT") then
                     return (Refused, 3);
                  else
                     return (Refused, 4);
                  end if;
               end if;
               if S.Text_Is (D, State, "UNUSED") then
                  return (Consume_Unused_Existing, 0);
               else
                  return (Complete_Intent_Existing, 0);
               end if;
            end if;
         end;
      end loop;
      return (Refused, 0);
   end Observe_Source;
   function Observe (Value : L.Parsed_Input; Journal_Name : String) return Decision is
   begin
      if Value.Status /= L.Parsed or else
         not Worldline.Custody_V2_Owner_Correspondence.Owner_Corresponds (Value) then return (Refused, 0); end if;
      return Observe_Source (Value.Arena, Value.Owner_Roster, Journal_Name, False);
   end Observe;
   function Decide (Value : L.Parsed_Input; Journal_Name : String) return Action is
     (Observe (Value, Journal_Name).Status);
   function Observe_Owner
     (Data : L.E.Bytes; Roster : L.E.Span; Journal_Name : String) return Decision is
   begin
      if not S.Text_Is (Data, F (Data, Roster, "schema"), "worldline.original-startup-admission-v1")
      then return (Refused, 0); end if;
      return Observe_Source (Data, Roster, Journal_Name, True);
   end Observe_Owner;
   function Decide_Owner
     (Data : L.E.Bytes; Roster : L.E.Span; Journal_Name : String) return Action is
     (Observe_Owner (Data, Roster, Journal_Name).Status);
   function All_Required_Admissions_Consumed (Value : L.Parsed_Input) return Boolean is
      D : E.Bytes renames Value.Arena;
      Profiles : constant E.Span := F (D, Value.Owner_Roster, "startup_admissions");
   begin
      if Value.Status /= L.Parsed or else
         not Worldline.Custody_V2_Owner_Correspondence.Owner_Corresponds (Value) or else
         not V.Is_Sequence (D, Profiles) or else V.Count (D, Profiles) /= 2 then return False; end if;
      for I in 1 .. 2 loop
         declare Name : constant String := (if I = 1 then "recovery-full-journal" else "full-use-reservations");
                 Found : E.Count := 0; begin
            for K in E.Count range 1 .. V.Count (D, Profiles) loop
               declare Profile : constant E.Span := V.Element (D, Profiles, K - 1); begin
                  if S.Text_Is (D, F (D, Profile, "name"), Name) then
                     Found := Found + 1;
                     if Observe_Source (D, Value.Owner_Roster, Name, False, Profile).Status /= Already_Consumed then return False; end if;
                  end if;
               end;
            end loop;
            if Found /= 1 then return False; end if;
         end;
      end loop;
      return True;
   end All_Required_Admissions_Consumed;
   function Profile_Matches_Except_Journal
     (B, A : E.Bytes; Old_Profile, New_Profile : E.Span; Except_Journal : Boolean) return Boolean is
      Old_Object : constant E.View := E.Decode (B, S.A.Field (B, Old_Profile, "fields"), E.Operation);
      New_Object : constant E.View := E.Decode (A, S.A.Field (A, New_Profile, "fields"), E.Operation);
      Name : constant String := "observed_journal";
   begin
      if Old_Object.Form /= E.Object_Value or else New_Object.Form /= E.Object_Value or else
         E.Array_Length (B, Old_Object.Children) /= E.Array_Length (A, New_Object.Children) then return False; end if;
      for I in E.Count range 1 .. E.Array_Length (B, Old_Object.Children) loop
         declare Old : constant E.Span := E.Array_Element (B, Old_Object.Children, I - 1);
                 New_Value : constant E.Span := E.Array_Element (A, New_Object.Children, I - 1);
                 OV : constant E.View := E.Decode (B, Old, E.Finalization);
                 NV : constant E.View := E.Decode (A, New_Value, E.Finalization);
                 Key : constant E.Span := E.Array_Element (B, OV.Children, 0);
                 KV : constant E.View := E.Decode (B, Key, E.Operation); begin
            if OV.Form /= E.List_Value or else NV.Form /= E.List_Value or else
               E.Array_Length (B, OV.Children) /= 2 or else E.Array_Length (A, NV.Children) /= 2 or else
               not Cross (B, A, Key, E.Array_Element (A, NV.Children, 0)) then return False; end if;
            if not E.Text_Is (B, KV, "installation_inventory") and then
              not (Except_Journal and then E.Text_Is (B, KV, Name)) then
               if not Cross (B, A, Old, New_Value) then return False; end if;
            end if;
         end;
      end loop;
      return True;
   end Profile_Matches_Except_Journal;
   function Transition_Source
     (B, A : E.Bytes; Before_Roster, After_Roster : E.Span; Journal_Name : String;
      Before_Action, After_Action : Action; Offline : Boolean) return Boolean is
      BC : constant E.Span := F (B, Before_Roster, "current");
      AC : constant E.Span := F (A, After_Roster, "current");
      BP : constant E.Span := F (B, BC, "paths");
      AP : constant E.Span := F (A, AC, "paths");
      Ledger_Path : constant E.Span := F (B, F (B, BC, "installation"), "bootstrap_ledger");
      Stable : constant Boolean := Before_Action = Complete_Intent_Existing and then After_Action = Complete_Intent_Existing;
      Created : constant Boolean := Offline and then Before_Action = Refused and then After_Action = Complete_Intent_Existing;
      Before_Profile : constant E.Span := F (B, Before_Roster, "startup_admission");
      After_Profile : constant E.Span := F (A, After_Roster, "startup_admission");
      Before_Decision, After_Decision : Decision;
   begin
      if not ((Before_Action = Consume_Unused_Existing and then After_Action = Complete_Intent_Existing) or else
              (Before_Action = Complete_Intent_Existing and then After_Action = Already_Consumed) or else
              (Offline and then Before_Action = Create_Unused_Offline and then After_Action = Refused) or else Stable or else Created)
      then return False; end if;
      Before_Decision := Observe_Source (B, Before_Roster, Journal_Name, Offline);
      After_Decision := Observe_Source (A, After_Roster, Journal_Name, Offline);
      if Before_Decision.Status /= Before_Action or else After_Decision.Status /= After_Action or else
         (Before_Action = Create_Unused_Offline and then After_Decision.Position /= 2) or else
         (Created and then Before_Decision.Position /= 2) or else
         V.Count (B, BP) /= V.Count (A, AP) or else
         not Cross (B, A, F (B, BC, "installation"), F (A, AC, "installation")) or else
         not Cross (B, A, F (B, BC, "source"), F (A, AC, "source")) or else
         not Cross (B, A, F (B, BC, "held_locks"), F (A, AC, "held_locks")) or else
         not Cross (B, A, F (B, BC, "descriptor_raw"), F (A, AC, "descriptor_raw")) or else
         not Profile_Matches_Except_Journal (B, A, Before_Profile, After_Profile, Created) or else
         not Install.Stable (B, A, Before_Profile, After_Profile) then return False; end if;
      if Created then
         declare Before_Journal : constant E.Span := F (B, Before_Profile, "observed_journal");
                 After_Journal : constant E.Span := F (A, After_Profile, "observed_journal"); begin
            if not Cross (B, A, F (B, Before_Journal, "path"), F (A, After_Journal, "path")) or else
               not Cross (B, A, F (B, Before_Journal, "parent_path"), F (A, After_Journal, "parent_path")) then return False; end if;
            for K in 1 .. 5 loop
               declare Field_Name : constant String := (case K is when 1 => "device", when 2 => "inode",
                 when 3 => "uid", when 4 => "gid", when 5 => "mode"); begin
                  if not Cross (B, A, F (B, F (B, Before_Journal, "parent_identity"), Field_Name),
                     F (A, F (A, After_Journal, "parent_identity"), Field_Name)) then return False; end if;
               end;
            end loop;
         end;
      end if;
      for I in E.Count range 1 .. V.Count (B, BP) loop
         declare Old : constant E.Span := V.Element (B, BP, I - 1);
                 New_Value : constant E.Span := V.Element (A, AP, I - 1); begin
            if not Cross (B, A, F (B, Old, "path"), F (A, New_Value, "path")) then return False; end if;
            if F (B, Old, "logical_database").Length > 0 or else F (A, New_Value, "logical_database").Length > 0 then
               if not Stable_Database_Identity (B, A, F (B, Old, "identity"), F (A, New_Value, "identity")) then return False; end if;
            elsif not Cross (B, A, F (B, Old, "identity"), F (A, New_Value, "identity")) then return False;
            end if;
            if not Same (B, F (B, Old, "path"), Ledger_Path) then
               if F (B, Old, "logical_database").Length > 0 or else F (A, New_Value, "logical_database").Length > 0 then
                  if not Cross (B, A, F (B, Old, "logical_database"), F (A, New_Value, "logical_database")) then return False; end if;
               elsif not Cross (B, A, F (B, Old, "raw"), F (A, New_Value, "raw")) then return False;
               end if;
            else
               declare BD : constant E.Span := F (B, Old, "logical_database");
                       AD : constant E.Span := F (A, New_Value, "logical_database");
                       BI : constant E.Span := F (B, Table (B, BD, "journal_intents"), "rows");
                       AI : constant E.Span := F (A, Table (A, AD, "journal_intents"), "rows");
                       BH : constant E.Span := F (B, Table (B, BD, "journal_history"), "rows");
                       AH : constant E.Span := F (A, Table (A, AD, "journal_history"), "rows"); begin
                  if not Cross (B, A, F (B, BD, "schema"), F (A, AD, "schema")) or else
                     not Cross (B, A, Table (B, BD, "bootstrap_identity"), Table (A, AD, "bootstrap_identity")) or else
                     V.Count (B, BI) /= V.Count (A, AI) or else V.Count (A, AH) /= V.Count (B, BH) +
                       (if Stable or else Created then 0 else 1) then return False; end if;
                  if (Stable or else Created) and then not Cross (B, A, BD, AD) then return False; end if;
                  for Field_Index in 1 .. 8 loop
                     declare Field_Name : constant String :=
                       (case Field_Index is when 1 => "encoding", when 2 => "user_version",
                        when 3 => "application_id", when 4 => "integrity", when 5 => "foreign_keys",
                        when 6 => "journal_mode", when 7 => "foreign_key_check", when 8 => "schema"); begin
                        if not Cross (B, A, F (B, BD, Field_Name), F (A, AD, Field_Name)) then return False; end if;
                     end;
                  end loop;
                  for Table_Index in 1 .. 3 loop
                     declare Name : constant String := (case Table_Index is when 1 => "bootstrap_identity",
                        when 2 => "journal_intents", when 3 => "journal_history");
                             BT : constant E.Span := Table (B, BD, Name);
                             After_Table : constant E.Span := Table (A, AD, Name); begin
                        for Field_Index in 1 .. 3 loop
                           declare Field_Name : constant String := (case Field_Index is when 1 => "columns",
                             when 2 => "query", when 3 => "foreign_key_list"); begin
                              if not Cross (B, A, F (B, BT, Field_Name), F (A, After_Table, Field_Name)) then return False; end if;
                           end;
                        end loop;
                     end;
                  end loop;
                  for K in E.Count range 1 .. V.Count (B, BH) loop
                     if not Cross (B, A, V.Element (B, BH, K - 1), V.Element (A, AH, K - 1)) then return False; end if;
                  end loop;
                  for K in E.Count range 1 .. V.Count (B, BI) loop
                     declare O : constant E.Span := V.Element (B, BI, K - 1);
                             N : constant E.Span := V.Element (A, AI, K - 1); begin
                        for C in E.Count range 0 .. 3 loop
                           if not Cross (B, A, V.Element (B, O, C), V.Element (A, N, C)) then return False; end if;
                        end loop;
                        if not S.Text_Is (B, V.Element (B, O, 1), Journal_Name) and then
                           not Cross (B, A, V.Element (B, O, 4), V.Element (A, N, 4)) then return False; end if;
                     end;
                  end loop;
               end;
            end if;
         end;
      end loop;
      return True;
   end Transition_Source;
   function Transition_Matches
     (Before, After : L.Parsed_Input; Journal_Name : String;
      Before_Action, After_Action : Action) return Boolean is
   begin
      return Before.Status = L.Parsed and then After.Status = L.Parsed and then
        Worldline.Custody_V2_Owner_Correspondence.Owner_Corresponds (Before) and then
        Worldline.Custody_V2_Owner_Correspondence.Owner_Corresponds (After) and then
        Transition_Source (Before.Arena, After.Arena, Before.Owner_Roster, After.Owner_Roster,
          Journal_Name, Before_Action, After_Action, False);
   end Transition_Matches;
   function Owner_Transition_Matches
     (Before, After : L.E.Bytes; Before_Roster, After_Roster : L.E.Span;
      Journal_Name : String; Before_Action, After_Action : Action) return Boolean is
   begin
      return Transition_Source (Before, After, Before_Roster, After_Roster,
        Journal_Name, Before_Action, After_Action, True);
   end Owner_Transition_Matches;
end Worldline.Startup_Admission;
