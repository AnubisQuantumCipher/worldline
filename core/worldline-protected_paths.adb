with Worldline.Producer_Values;
package body Worldline.Protected_Paths with SPARK_Mode is
   package V renames Worldline.Producer_Values;
   type Scalars is array (Natural range <>) of Natural;
   function Decode (Text : String) return Scalars is
      Buffer : Scalars (0 .. Text'Length) with Relaxed_Initialization;
      Count : Natural := 0;
      I : Natural := 0;
      Width, Code : Natural;
   begin
      while I < Text'Length loop
         pragma Loop_Invariant (Count <= I and then (for all K in 0 .. Count - 1 => Buffer (K)'Initialized));
         pragma Loop_Variant (Increases => I);
         Width := 1;
         Code := Character'Pos (Text (Text'First + I));
         if Code in 16#C2# .. 16#DF# then Code := Code - 16#C0#; Width := 2;
         elsif Code in 16#E0# .. 16#EF# then Code := Code - 16#E0#; Width := 3;
         elsif Code in 16#F0# .. 16#F4# then Code := Code - 16#F0#; Width := 4;
         end if;
         if Width > Text'Length - I then return (1 .. 0 => 0); end if;
         for J in 1 .. Width - 1 loop
            Code := Code * 64 + Character'Pos (Text (Text'First + I + J)) mod 64;
         end loop;
         Buffer (Count) := Code;
         Count := Count + 1;
         I := I + Width;
      end loop;
      if Count = 0 then return (1 .. 0 => 0); end if;
      return Buffer (0 .. Count - 1);
   end Decode;
   function Glob (Pattern, Path : Scalars; P, N : Natural) return Boolean
     with Subprogram_Variant => (Decreases =>
       Pattern'Length - Natural'Min (P, Pattern'Length)) is
      After : Natural;
      First : Natural;
      I : Natural;
      Negated, Included : Boolean;
   begin
      if P >= Pattern'Length then return N = Path'Length; end if;
      if Pattern (P) = 42 then
         for K in N .. Path'Length loop
            if Glob (Pattern, Path, P + 1, K) then return True; end if;
         end loop;
         return False;
      end if;
      if N >= Path'Length then return False; end if;
      if Pattern (P) = 63 then return Glob (Pattern, Path, P + 1, N + 1); end if;
      if Pattern (P) = 91 then
         First := P + 1;
         Negated := First < Pattern'Length and then Pattern (First) = 33;
         if Negated then First := First + 1; end if;
         After := First;
         if After < Pattern'Length and then Pattern (After) = 93 then After := After + 1; end if;
         while After < Pattern'Length and then Pattern (After) /= 93 loop
            pragma Loop_Variant (Increases => After);
            After := After + 1;
         end loop;
         if After < Pattern'Length then
            Included := False;
            I := First;
            while I < After loop
               pragma Loop_Variant (Increases => I);
               if After - I >= 3 and then Pattern (I + 1) = 45 then
                  if Pattern (I) <= Pattern (I + 2) and then
                    Path (N) >= Pattern (I) and then Path (N) <= Pattern (I + 2)
                  then Included := True; end if;
                  I := I + 3;
               else
                  if Path (N) = Pattern (I) then Included := True; end if;
                  I := I + 1;
               end if;
            end loop;
            return (Included /= Negated) and then Glob (Pattern, Path, After + 1, N + 1);
         end if;
      end if;
      return Pattern (P) = Path (N) and then Glob (Pattern, Path, P + 1, N + 1);
   end Glob;
   function Matches (Pattern, Path : String) return Boolean is
      Last : Natural := Pattern'Length;
   begin
      while Last > 0 and then Pattern (Pattern'First + Last - 1) = '/' loop
         pragma Loop_Variant (Decreases => Last);
         Last := Last - 1;
      end loop;
      declare
         Base : constant String := Pattern (Pattern'First .. Pattern'First + Last - 1);
      begin
         return Path = Base or else
           (Path'Length > Last and then Path (Path'First .. Path'First + Last) = Base & "/") or else
           Glob (Decode (Pattern), Decode (Path), 0, 0);
      end;
   end Matches;
   function Touched (Expected_Requirement, Delta_JSON : String) return Boolean is
      Patterns : constant String := V.Field (V.Field
        (V.Field (Expected_Requirement, "policy"), "canonical"), "protected");
      Operations : constant String := V.Field (Delta_JSON, "operations");
   begin
      for I in 1 .. V.Count (Operations) loop
         declare
            Path : constant String := V.Text (V.Field (V.Element (Operations, I - 1), "pathDisplay"));
         begin
            for J in 1 .. V.Count (Patterns) loop
               if Matches (V.Text (V.Element (Patterns, J - 1)), Path) then return True; end if;
            end loop;
         end;
      end loop;
      return False;
   end Touched;
end Worldline.Protected_Paths;
