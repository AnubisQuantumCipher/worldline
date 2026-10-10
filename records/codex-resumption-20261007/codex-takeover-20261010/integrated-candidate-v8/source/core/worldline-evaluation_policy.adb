with Worldline.Policy_Source;
with Worldline.Raw_JSON;
package body Worldline.Evaluation_Policy with SPARK_Mode is
   use type V.Value_Kind;
   use type Worldline.Policy_Source.Relation;
   function Policy (R : String) return String is
     (V.Field (R, "policy"));
   function Canonical (R : String) return String is
     (V.Field (Policy (R), "canonical"));
   function Checks (R : String) return String is
     (V.Field (Canonical (R), "checks"));
   function Has_Protected (R : String) return Boolean is
     (V.Truth (V.Field (Canonical (R), "protected")));
   function Required_Source (R : String) return String is
     (V.Field (Policy (R), "requiredChecks"));
   function Source_Name (R : String; I : Natural) return String is
     (V.Python_String (V.Element (Required_Source (R), I)));
   function Source_Has (R, Name : String) return Boolean is
   begin
      for I in 1 .. V.Count (Required_Source (R)) loop
         if Source_Name (R, I - 1) = Name then return True; end if;
      end loop;
      return False;
   end Source_Has;
   function Unique_Source (R : String; I : Natural) return Boolean is
   begin
      for J in 1 .. I loop
         if Source_Name (R, J - 1) = Source_Name (R, I) then
            return False;
         end if;
      end loop;
      return True;
   end Unique_Source;
   function Required_Count (Requirement : String) return Natural is
      N : Natural := 0;
   begin
      if V.Kind (Policy (Requirement)) /= V.Object_Value then return 0; end if;
      for I in 1 .. V.Count (Required_Source (Requirement)) loop
         if Unique_Source (Requirement, I - 1) then N := N + 1; end if;
      end loop;
      if Has_Protected (Requirement) and then
        not Source_Has (Requirement, "protected-paths")
      then N := N + 1; end if;
      return N;
   end Required_Count;
   function Required (Requirement : String; Ordinal : Natural) return String is
      Rank : Natural;
      N : Natural := 0;
   begin
      for I in 1 .. V.Count (Required_Source (Requirement)) loop
         if Unique_Source (Requirement, I - 1) then
            N := N + 1;
            Rank := 0;
            for J in 1 .. V.Count (Required_Source (Requirement)) loop
               if Unique_Source (Requirement, J - 1) and then
                 Source_Name (Requirement, J - 1) < Source_Name (Requirement, I - 1)
               then Rank := Rank + 1; end if;
            end loop;
            if Rank = Ordinal then return Source_Name (Requirement, I - 1); end if;
         end if;
      end loop;
      if Ordinal = N and then Has_Protected (Requirement) and then
        not Source_Has (Requirement, "protected-paths")
      then return "protected-paths"; end if;
      return "";
   end Required;
   function Empty_Declared (Requirement : String) return Boolean is
      Source : constant String := V.Field (Policy (Requirement), "sourceSha256");
   begin
      return V.Kind (Source) = V.String_Value and then V.Text (Source)'Length > 0;
   end Empty_Declared;
   function Valid_Check (C : String) return Boolean is
     (V.Kind (C) = V.Object_Value and then
      V.Kind (V.Field (C, "id")) = V.String_Value and then
      V.Text (V.Field (C, "id"))'Length > 0 and then
      V.Kind (V.Field (C, "format")) = V.String_Value and then
      V.Kind (V.Field (C, "profile")) = V.String_Value);
   function Check_Name (R : String; I : Natural) return String is
     (V.Text (V.Field (V.Element (Checks (R), I), "id")));
   function Unique_Check (R : String; I : Natural) return Boolean is
   begin
      for J in 1 .. I loop
         if Valid_Check (V.Element (Checks (R), J - 1)) and then
           Check_Name (R, J - 1) = Check_Name (R, I)
         then return False; end if;
      end loop;
      return True;
   end Unique_Check;
   function Declared_Has (R, Name : String) return Boolean is
   begin
      for I in 1 .. V.Count (Checks (R)) loop
         if Valid_Check (V.Element (Checks (R), I - 1)) and then
           Check_Name (R, I - 1) = Name
         then return True; end if;
      end loop;
      return False;
   end Declared_Has;
   function Declaration_Count (Requirement : String) return Natural is
      N : Natural := 0;
   begin
      for I in 1 .. V.Count (Checks (Requirement)) loop
         if Valid_Check (V.Element (Checks (Requirement), I - 1)) and then
           Unique_Check (Requirement, I - 1)
         then N := N + 1; end if;
      end loop;
      if Has_Protected (Requirement) and then
        not Declared_Has (Requirement, "protected-paths")
      then N := N + 1; end if;
      return N;
   end Declaration_Count;
   function Declaration_Name (Requirement : String; Ordinal : Natural)
      return String is
      N : Natural := 0;
   begin
      for I in 1 .. V.Count (Checks (Requirement)) loop
         if Valid_Check (V.Element (Checks (Requirement), I - 1)) and then
           Unique_Check (Requirement, I - 1)
         then
            if N = Ordinal then return Check_Name (Requirement, I - 1); end if;
            N := N + 1;
         end if;
      end loop;
      if N = Ordinal and then Has_Protected (Requirement) and then
        not Declared_Has (Requirement, "protected-paths")
      then return "protected-paths"; end if;
      return "";
   end Declaration_Name;
   function Engine (Agent : Boolean) return String is
     ("{""format"":" & V.Quote ((if Agent then "exit" else "engine")) &
      ",""profile"":null,""bundle_declared"":false,""origin"":" &
      V.Quote ((if Agent then "agent" else "engine")) & "}");
   function Bundle_Declared (R, Name : String) return Boolean is
      Entries : constant String := V.Field (R, "verifiers");
   begin
      for I in 1 .. V.Count (Entries) loop
         declare
            Member : constant String := V.Element (Entries, I - 1);
            Id : constant String := V.Field (Member, "checkId");
         begin
            if V.Kind (Member) = V.Object_Value and then
              V.Kind (Id) not in V.Missing | V.Null_Value and then
              V.Python_String (Id) = Name
            then return True; end if;
         end;
      end loop;
      return False;
   end Bundle_Declared;
   function Declaration (Requirement, Check : String) return String is
      Selected : Natural := 0;
      Found : Boolean := False;
   begin
      if Check = "protected-paths" and then Has_Protected (Requirement) then
         return Engine (False);
      end if;
      for I in 1 .. V.Count (Checks (Requirement)) loop
         if Valid_Check (V.Element (Checks (Requirement), I - 1)) and then
           Check_Name (Requirement, I - 1) = Check
         then Found := True; Selected := I - 1; end if;
      end loop;
      if not Found then return "null"; end if;
      declare
         C : constant String := V.Element (Checks (Requirement), Selected);
      begin
         return "{""format"":" & V.Field (C, "format") &
           ",""profile"":" & V.Field (C, "profile") &
           ",""bundle_declared"":" &
           (if Bundle_Declared (Requirement, Check) then "true" else "false") &
           ",""origin"":null}";
      end;
   end Declaration;
   function Additional_Unique (R, A : String; I : Natural) return Boolean is
      Name : constant String := V.Text (V.Element (A, I));
   begin
      for J in 1 .. Required_Count (R) loop
         if Required (R, J - 1) = Name then return False; end if;
      end loop;
      for J in 1 .. I loop
         if V.Text (V.Element (A, J - 1)) = Name then return False; end if;
      end loop;
      return True;
   end Additional_Unique;
   function Required_JSON (R, A : String; I : Natural) return String
     with Subprogram_Variant => (Decreases =>
       Required_Count (R) + V.Count (A) - Natural'Min (I, Required_Count (R) + V.Count (A))) is
      Base : constant Natural := Required_Count (R);
   begin
      if I >= Base + V.Count (A) then return ""; end if;
      declare
         Rest : constant String := Required_JSON (R, A, I + 1);
      begin
         if I < Base then
            return V.Quote (Required (R, I)) &
              (if Rest'Length > 0 then "," & Rest else "");
         elsif Additional_Unique (R, A, I - Base) then
            return V.Quote (V.Text (V.Element (A, I - Base))) &
              (if Rest'Length > 0 then "," & Rest else "");
         end if;
         return Rest;
      end;
   end Required_JSON;
   function Declarations_JSON (R : String; I : Natural) return String
     with Subprogram_Variant => (Decreases =>
       Declaration_Count (R) - Natural'Min (I, Declaration_Count (R))) is
   begin
      if I >= Declaration_Count (R) then return ""; end if;
      return V.Quote (Declaration_Name (R, I)) & ":" &
        Declaration (R, Declaration_Name (R, I)) &
        (if I + 1 < Declaration_Count (R) then "," else "") &
        Declarations_JSON (R, I + 1);
   end Declarations_JSON;
   function Additional_JSON (A : String; I : Natural) return String
     with Subprogram_Variant => (Decreases => V.Count (A) - Natural'Min (I, V.Count (A))) is
   begin
      if I >= V.Count (A) then return ""; end if;
      return V.Quote (V.Text (V.Element (A, I))) &
        (if I + 1 < V.Count (A) then "," else "") & Additional_JSON (A, I + 1);
   end Additional_JSON;
   function Project (Requirement, Additional : String; Finalization : Boolean)
      return String is
      Extra : constant String :=
        "[" & Additional_JSON (Additional, 0) &
        (if Finalization then
          (if V.Count (Additional) > 0 then "," else "") &
          """verifiers-modified""" else "") & "]";
   begin
      if Worldline.Policy_Source.Observe (Requirement) = Worldline.Policy_Source.Source_Conflicts then
         return "{""status"":""EVALUATION_POLICY_SOURCE_CONFLICT""}";
      end if;
      return "{""status"":""COMPLETE"",""required"":" &
        "[" & Required_JSON (Requirement, Extra, 0) & "]," &
        """empty"":" & (if Empty_Declared (Requirement) then "true" else "false") &
        ",""declarations"":{" & Declarations_JSON (Requirement, 0) &
        (if Finalization then
          (if Declaration_Count (Requirement) > 0 then "," else "") &
          """agent"":" & Engine (True) & ",""verifiers-modified"":" & Engine (False) &
          ",""evaluation-complete"":" & Engine (False)
         else "") & "}}";
   end Project;
   function Policy_Same (Expected, Observed : String) return Boolean is
     (V.Equal (Expected, Observed));
   function Same_Key (L, R : String) return Boolean is
     (V.Equal (V.Field (L, "rootKey"), V.Field (R, "rootKey")) and then
      V.Equal (V.Field (L, "path"), V.Field (R, "path")));
   function Last_Member (Rows : String; I : Natural) return Boolean is
   begin
      for J in I + 1 .. V.Count (Rows) - (if V.Count (Rows) > 0 then 1 else 0) loop
         if Same_Key (V.Element (Rows, I), V.Element (Rows, J)) then return False; end if;
      end loop;
      return True;
   end Last_Member;
   function Match_Member (Member, Rows : String) return Boolean is
   begin
      for I in reverse 1 .. V.Count (Rows) loop
         declare
            Item : constant String := V.Element (Rows, I - 1);
         begin
            if Same_Key (Member, Item) then
               return V.Equal (V.Field (Member, "sha256"), V.Field (Item, "sha256"));
            end if;
         end;
      end loop;
      return False;
   end Match_Member;
   function Verifiers_Modified (Expected_Requirement, Returned_Context : String)
      return Boolean is
      Expected : constant String := V.Field (Expected_Requirement, "verifiers");
      Observed : constant String := V.Field (Returned_Context, "candidateVerifiers");
   begin
      for I in 1 .. V.Count (Expected) loop
         if Last_Member (Expected, I - 1) and then
           not Match_Member (V.Element (Expected, I - 1), Observed)
         then return True; end if;
      end loop;
      for I in 1 .. V.Count (Observed) loop
         if Last_Member (Observed, I - 1) and then
           not Match_Member (V.Element (Observed, I - 1), Expected)
         then return True; end if;
      end loop;
      return False;
   end Verifiers_Modified;
   function Returned (Returns, Invocation : String) return String is
     (V.Field (Returns, Invocation));
   function Started (Invocations : String; I : Natural) return String is
     (V.Element (V.Element (Invocations, I), 1));
   function Invocation_Id (Invocations : String; I : Natural) return String is
     (V.Text (V.Element (V.Element (Invocations, I), 0)));
   function Original_Prefix (Row, Original : String) return Boolean is
      Root : constant V.Node := V.Parse (Original);
   begin
      if Root.Form /= V.Object_Value then return False; end if;
      for I in 1 .. V.Count (Original, Root) loop
         declare
            Name : constant String := V.Member_Name (Original, Root, I);
         begin
            if Name /= "executionBinding" and then Name /= "evaluation" and then
              not Worldline.Raw_JSON.Python_JSON_Equal
                (V.Field (Row, Name), V.Field (Original, Name))
            then return False; end if;
         end;
      end loop;
      return True;
   end Original_Prefix;
   function Prefix (Rows, Invocations, Returns : String) return Prefix_Status is
      Next : Natural := 0;
   begin
      for I in 1 .. V.Count (Rows) loop
         if Next < V.Count (Invocations) then
            declare
               Start : constant String := Started (Invocations, Next);
               Return_Value : constant String := Returned (Returns, Invocation_Id (Invocations, Next));
               Row : constant String := V.Element (Rows, I - 1);
            begin
               if V.Kind (Return_Value) /= V.Missing and then
                 V.Equal (V.Field (Row, "id"), V.Field (Start, "checkId"))
               then
                  if not Original_Prefix (Row, V.Field (Return_Value, "result")) then
                     return Prefix_Changed;
                  end if;
                  Next := Next + 1;
               end if;
            end;
         end if;
      end loop;
      return (if Next = V.Count (Invocations) then Prefix_Complete else Return_Missing);
   end Prefix;
   function Return_Row (Rows, Invocations, Returns : String; Ordinal : Natural)
      return Natural is
      Next : Natural := 0;
   begin
      for I in 1 .. V.Count (Rows) loop
         if Next < V.Count (Invocations) and then
           V.Kind (Returned (Returns, Invocation_Id (Invocations, Next))) /= V.Missing and then
           V.Equal (V.Field (V.Element (Rows, I - 1), "id"),
                    V.Field (Started (Invocations, Next), "checkId"))
         then
            if Next = Ordinal then return I; end if;
            Next := Next + 1;
         end if;
      end loop;
      return 0;
   end Return_Row;
   function Return_Rows_JSON (Rows, Invocations, Returns : String; I : Natural)
      return String with Subprogram_Variant => (Decreases =>
        V.Count (Invocations) - Natural'Min (I, V.Count (Invocations))) is
   begin
      if I >= V.Count (Invocations) then return ""; end if;
      return Natural'Image (Return_Row (Rows, Invocations, Returns, I)) &
        (if I + 1 < V.Count (Invocations) then "," else "") &
        Return_Rows_JSON (Rows, Invocations, Returns, I + 1);
   end Return_Rows_JSON;
   function Capture_Plan
     (Rows, Invocations, Returns, Expected_Requirement, Returned_Context : String)
      return String is
      State : constant Prefix_Status := Prefix (Rows, Invocations, Returns);
   begin
      return "{""status"":" & V.Quote
        ((case State is when Prefix_Complete => "COMPLETE",
          when Prefix_Changed => "FINALIZATION_RETURN_PREFIX_CHANGED",
          when Return_Missing => "FINALIZATION_INVOCATION_HAS_NO_RETURN")) &
        ",""returnRows"": [" & Return_Rows_JSON (Rows, Invocations, Returns, 0) &
        "],""verifiersModified"":" &
        (if Verifiers_Modified (Expected_Requirement, Returned_Context) then "true" else "false") & "}";
   end Capture_Plan;
end Worldline.Evaluation_Policy;
