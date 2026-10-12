with Worldline.Producer_Values;
with Worldline.Producer_Bytes;
with Exact_Decimal;
with Decimal_Binary64;
with Evaluation_Pending;
with Worldline.Policy_Syntax;
package body Worldline.Policy_Source with SPARK_Mode is
   package V renames Worldline.Producer_Values;
   package B renames Worldline.Producer_Bytes;
   use type V.Value_Kind;
   use type Evaluation_Pending.Count;
   function Schema_One (Value : String) return Boolean is
      package P renames Evaluation_Pending;
   begin
      if Value = "1" or else Value = "true" then return True; end if;
      if V.Kind (Value) /= V.Number_Value then return False; end if;
      declare
         Data : constant P.Bytes := (for I in 1 .. P.Count (Value'Length) =>
           P.Byte (Character'Pos (Value (Value'First + Natural (I - 1)))));
         N : constant Exact_Decimal.Number := Exact_Decimal.Parse (Data, (1, Data'Length), 0);
         Converted : constant Decimal_Binary64.Conversion := Decimal_Binary64.Convert (N);
      begin
         return N.Valid and then N.After = Data'Length and then Converted.Valid and then
           Decimal_Binary64.Repr (Converted.Encoding) = "1.0";
      end;
   end Schema_One;
   function Defaulted (Value, Name, Default : String) return String is
      Item : constant String := V.Field (Value, Name);
   begin
      return (if V.Kind (Item) = V.Missing then Default else Item);
   end Defaulted;
   function Occurrences (Array_Value, Item : String) return Natural is
      N : Natural := 0;
   begin
      for I in 1 .. V.Count (Array_Value) loop
         if V.Equal (V.Element (Array_Value, I - 1), Item) then N := N + 1; end if;
      end loop;
      return N;
   end Occurrences;
   function Sorted_Same (Raw, Sorted : String) return Boolean is
   begin
      if V.Count (Raw) /= V.Count (Sorted) then return False; end if;
      for I in 1 .. V.Count (Raw) loop
         declare Item : constant String := V.Element (Raw, I - 1);
         begin
            if Occurrences (Raw, Item) /= Occurrences (Sorted, Item) then return False; end if;
         end;
         if I > 1 and then V.Text (V.Element (Sorted, I - 2)) > V.Text (V.Element (Sorted, I - 1)) then
            return False;
         end if;
      end loop;
      return True;
   end Sorted_Same;
   function Check_Matches (Raw, Projected : String) return Boolean is
      type Key is (Id_Key, Kind_Key, Argv_Key, Cwd_Key, Required_Key,
                   Format_Key, Result_Key, Covers_Key, Verifiers_Key, Profile_Key);
   begin
      for K in Key loop
         declare
            Name : constant String := (case K is
              when Id_Key => "id", when Kind_Key => "kind", when Argv_Key => "argv",
              when Cwd_Key => "cwd", when Required_Key => "required", when Format_Key => "format",
              when Result_Key => "result", when Covers_Key => "covers", when Verifiers_Key => "verifiers",
              when Profile_Key => "profile");
            Default : constant String := (case K is
              when Cwd_Key | Result_Key => "null", when Covers_Key | Verifiers_Key => "[]",
              when Profile_Key => """legacy""", when others => "");
            Source : constant String := Defaulted (Raw, Name, Default);
            Actual : constant String := V.Field (Projected, Name);
         begin
            if K in Covers_Key | Verifiers_Key then
               if not Sorted_Same (Source, Actual) then return False; end if;
            elsif not V.Equal (Source, Actual) then return False;
            end if;
         end;
      end loop;
      return V.Kind (Raw) = V.Object_Value and then V.Kind (Projected) = V.Object_Value;
   end Check_Matches;
   function Roster_Matches (Raw_Checks, Required : String) return Boolean is
      N : Natural := 0;
   begin
      for I in 1 .. V.Count (Raw_Checks) loop
         declare C : constant String := V.Element (Raw_Checks, I - 1);
         begin
            if V.Truth (V.Field (C, "required")) then
               N := N + 1;
               if Occurrences (Required, V.Field (C, "id")) /= 1 then return False; end if;
            end if;
         end;
      end loop;
      if V.Count (Required) /= N then return False; end if;
      for I in 2 .. V.Count (Required) loop
         if V.Text (V.Element (Required, I - 2)) > V.Text (V.Element (Required, I - 1)) then return False; end if;
      end loop;
      return True;
   end Roster_Matches;
   function Named_Array_Matches (Raw, Projected, Name : String) return Boolean is
      Found : Boolean;
   begin
      if V.Count (Raw) /= V.Count (Projected) then return False; end if;
      for I in 1 .. V.Count (Raw) loop
         Found := False;
         for J in 1 .. V.Count (Projected) loop
            if V.Equal (V.Field (V.Element (Raw, I - 1), Name),
                        V.Field (V.Element (Projected, J - 1), Name)) and then
              V.Equal (V.Element (Raw, I - 1), V.Element (Projected, J - 1))
            then Found := True; end if;
         end loop;
         if not Found then return False; end if;
      end loop;
      for I in 2 .. V.Count (Projected) loop
         if V.Text (V.Field (V.Element (Projected, I - 2), Name)) >
           V.Text (V.Field (V.Element (Projected, I - 1), Name))
         then return False; end if;
      end loop;
      return True;
   end Named_Array_Matches;
   function Root_Key (Raw_Root, Roots : String) return String is
   begin
      for I in reverse 1 .. V.Count (Roots) loop
         declare Root : constant String := V.Element (Roots, I - 1);
         begin
            if V.Equal (Raw_Root, V.Field (Root, "root_key")) or else
              V.Equal (Raw_Root, V.Field (Root, "display_path"))
            then return V.Field (Root, "root_key"); end if;
         end;
      end loop;
      return "";
   end Root_Key;
   function Generated_Occurrences (Raw, Item, Roots : String) return Natural is
      N : Natural := 0;
   begin
      for I in 1 .. V.Count (Raw) loop
         declare Source : constant String := V.Element (Raw, I - 1);
         begin
            if V.Equal (Root_Key (V.Field (Source, "root"), Roots), V.Field (Item, "root")) and then
              V.Equal (V.Field (Source, "glob"), V.Field (Item, "glob"))
            then N := N + 1; end if;
         end;
      end loop;
      return N;
   end Generated_Occurrences;
   function Generated_Matches (Raw, Projected, Roots : String) return Boolean is
   begin
      if V.Kind (Raw) /= V.Array_Value or else V.Kind (Projected) /= V.Array_Value or else
        V.Count (Raw) /= V.Count (Projected)
      then return False; end if;
      for I in 1 .. V.Count (Projected) loop
         declare Item : constant String := V.Element (Projected, I - 1);
         begin
            if V.Kind (Item) /= V.Object_Value or else V.Count (Item) /= 2 or else
              Generated_Occurrences (Raw, Item, Roots) /= Occurrences (Projected, Item)
            then return False; end if;
         end;
      end loop;
      return True;
   end Generated_Matches;
   function Observe (Requirement : String) return Relation is
      Policy : constant String := V.Field (Requirement, "policy");
      Observation : constant String := V.Field (Policy, "sourceObservation");
      Canonical : constant String := V.Field (Policy, "canonical");
   begin
      if V.Kind (Observation) = V.Missing then return Historical_No_Source; end if;
      if V.Kind (Observation) /= V.Object_Value then return Source_Conflicts; end if;
      if V.Kind (V.Field (Observation, "payloadB64")) = V.Null_Value then
         return (if V.Kind (V.Field (Policy, "sourceSha256")) = V.Null_Value and then
           V.Count (V.Field (Canonical, "checks")) = 0 and then
           V.Count (V.Field (Canonical, "protected")) = 0 and then
           V.Count (V.Field (Canonical, "generated")) = 0 and then
           V.Count (V.Field (Canonical, "services")) = 0
           then Historical_No_Source else Source_Conflicts);
      end if;
      if V.Kind (V.Field (Observation, "payloadB64")) /= V.String_Value then return Source_Conflicts; end if;
      declare
         Raw : constant B.Decoded := B.Base64 (V.Text (V.Field (Observation, "payloadB64")));
         Digest : constant String := (if Raw.Valid then B.Digest (Raw.Data) else "");
      begin
         if not Raw.Valid or else
           Digest /= V.Text (V.Field (Policy, "sourceSha256")) or else
           Digest /= V.Text (V.Field (Observation, "expectedSourceSha256")) or else
           V.Kind (Raw.Data) /= V.Object_Value or else
           not Worldline.Policy_Syntax.Valid (Raw.Data) or else
           not Schema_One (V.Field (Raw.Data, "schemaVersion")) or else
           V.Kind (Canonical) /= V.Object_Value or else V.Count (Canonical) /= 5 or else
           V.Field (Canonical, "schemaVersion") /= "1" or else
           V.Kind (V.Field (Canonical, "checks")) /= V.Array_Value or else
           V.Kind (V.Field (Canonical, "protected")) /= V.Array_Value or else
           V.Kind (V.Field (Canonical, "generated")) /= V.Array_Value or else
           V.Kind (V.Field (Canonical, "services")) /= V.Array_Value
         then return Source_Conflicts; end if;
         declare
            Raw_Checks : constant String := V.Field (Raw.Data, "checks");
            Projected_Checks : constant String := V.Field (Canonical, "checks");
         begin
            if V.Count (Raw_Checks) /= V.Count (Projected_Checks) or else
              not Roster_Matches (Raw_Checks, V.Field (Policy, "requiredChecks"))
            then return Source_Conflicts; end if;
            for I in 1 .. V.Count (Raw_Checks) loop
               if not Check_Matches (V.Element (Raw_Checks, I - 1), V.Element (Projected_Checks, I - 1)) then
                  return Source_Conflicts;
               end if;
            end loop;
         end;
         if not Sorted_Same (Defaulted (Raw.Data, "protected", "[]"), V.Field (Canonical, "protected")) or else
           not Named_Array_Matches (V.Field (Raw.Data, "services"), V.Field (Canonical, "services"), "id") or else
           not Generated_Matches (V.Field (Raw.Data, "generated"), V.Field (Canonical, "generated"), V.Field (Observation, "rawRoots"))
         then return Source_Conflicts; end if;
         return Source_Matches;
      end;
   end Observe;
   function Current_Matches (Expected, Observed : String) return Boolean is
     (Observe (Expected) = Source_Matches and then Observe (Observed) = Source_Matches and then
      V.Equal (V.Field (V.Field (Expected, "policy"), "canonical"),
               V.Field (V.Field (Observed, "policy"), "canonical")) and then
      V.Equal (V.Field (V.Field (Expected, "policy"), "requiredChecks"),
               V.Field (V.Field (Observed, "policy"), "requiredChecks")));
end Worldline.Policy_Source;
