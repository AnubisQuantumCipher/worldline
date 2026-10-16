with Worldline.Producer_Bytes;
with Worldline.Producer_Values;
with Worldline.Report_Parser;
with Worldline.Source_Audit_Native;
with Worldline.Evaluation_Policy;
with Worldline.Protected_Paths;
with Worldline.Report_Custody_Native;
with Worldline.Native_Lifetime_Observation;
with Worldline.Raw_JSON;
with Worldline.Evaluation_Agent_Native;
with Worldline.Evaluation_Role_Native;

package body Worldline.Evaluation_Producer with SPARK_Mode is
   package V renames Worldline.Producer_Values;
   package P renames Worldline.Report_Parser;
   use type V.Value_Kind;
   use type W.Byte;
   use type P.Report_Status;
   use type E.Count;

   function Bit (Value : Boolean) return W.Byte is (if Value then 1 else 0);
   subtype Decoded is Worldline.Producer_Bytes.Decoded;
   function Base64 (Encoded : String) return Decoded renames Worldline.Producer_Bytes.Base64;
   function Digest (Data : String) return String renames Worldline.Producer_Bytes.Digest;
   function Identity_Value (Data : String; Item : V.Node) return Boolean is
     (V.Nonempty_Text (Data, Item) and then
      (for all C of V.Text (Data, Item) => C /= Character'Val (0)));



   function Bytes (Data : String; Item : V.Node) return Decoded is
   begin
      if Item.Form /= V.Object_Value or else
         not V.Is_Text (Data, V.Field (Data, Item, "encoding"), "base64") or else
         V.Field (Data, Item, "payload").Form /= V.String_Value then
         return (0, False, "");
      end if;
      return Base64 (V.Text (Data, V.Field (Data, Item, "payload")));
   end Bytes;


   function Image (Value : Natural) return String is
      Raw : constant String := Natural'Image (Value);
   begin
      return Raw (Raw'First + 1 .. Raw'Last);
   end Image;


   function Project_Original
     (Result_Record, Declared : String;
      Result, Declaration : V.Node;
      Parser_Declaration, Raw_Capsule : String)
      return Produced_Record
   is
      function F (Item : V.Node; Name : String) return V.Node is
        (V.Field (Result_Record, Item, Name));
      function S (Item : V.Node; Name : String) return String is
        (V.Text (Result_Record, F (Item, Name)));
      function D (Name : String) return V.Node is
        (V.Field (Declared, Declaration, Name));
      function Absent (Item : V.Node) return Boolean is
        (Item.Form in V.Missing | V.Null_Value);
      function Equal (Left, Right : V.Node) return Boolean is
        ((Absent (Left) and then Absent (Right)) or else
         Worldline.Raw_JSON.Python_JSON_Equal
           (V.Slice (Result_Record, Left), V.Slice (Result_Record, Right)));
      function Field_Is (Item : V.Node; Name, Text : String) return Boolean is
        (V.Is_Text (Result_Record, F (Item, Name), Text));
      function Identified (Item : V.Node) return Boolean is
        (Item.Form = V.String_Value and then V.Text (Result_Record, Item)'Length > 0);
      function Identity (Item : V.Node) return Boolean is
        (Identified (Item) and then
         (for all C of V.Text (Result_Record, Item) => C /= Character'Val (0)));
      Executed : constant V.Node := F (Result, "executedVerifierSet");
      Status : constant V.Node := F (Result, "status");
      Channel : constant V.Node := F (Result, "resultChannel");
      Stage : constant V.Node := F (Channel, "stage");
      Exit_Code : constant V.Node := F (Result, "exitCode");
      Supervisor : constant V.Node := F (Result, "supervision");
      Supervisor_Kind : constant V.Node := F (Supervisor, "kind");
      Boundary : constant V.Node := F (Result, "evaluatorBoundary");
      Report : constant V.Node := F (Result, "privateReport");
      Snapshot : constant V.Node := F (Result, "candidateSnapshot");
      Resource : constant V.Node := F (Result, "resources");
      Original : constant V.Node := F (Result, "rawRunnerResult");
      Payload : constant Decoded :=
        (if F (Report, "payloadB64").Form = V.String_Value and then
            V.Text (Result_Record, F (Report, "payloadB64"))'Length <= 13_333_336
         then Base64 (S (Report, "payloadB64")) else (0, False, ""));
      Full_Payload : constant Boolean := Payload.Valid and then Payload.Length <= 10_000_000;
      Nonnegative_Exit : constant Boolean :=
        Exit_Code.Form = V.Integer_Value and then V.Nonnegative (Result_Record, Exit_Code);
      Produced : Produced_Record;
      Facts : W.R.Raw_Facts := (others => 0);
      function Fact (Value : Boolean) return W.Byte is (if Value then 1 else 0);
      function Integer_Matches (Item : V.Node) return Boolean is
        (Item.Form = V.Integer_Value and then Equal (Item, Exit_Code));
      Audit : constant Boolean :=
        (if Parser_Declaration'Length > 0 or else Raw_Capsule'Length > 0 then
           Worldline.Source_Audit_Native.Clean
             ((if Original.Form = V.Object_Value then V.Slice (Result_Record, Original)
               else Result_Record), Parser_Declaration, Raw_Capsule)
         else Worldline.Source_Audit_Native.Clean
           (if Original.Form = V.Object_Value then V.Slice (Result_Record, Original)
            else Result_Record));
   begin
      if Result.Form /= V.Object_Value then return Produced; end if;
      Produced.Raw.Observations :=
        ((if Field_Is (Result, "origin", "engine") then 0
          elsif Field_Is (Result, "origin", "agent") then 1 else 2),
         (if V.Is_Text (Result_Record, Status, "PASS") then 1
          elsif V.Is_Text (Result_Record, Status, "FAIL") then 2
          elsif V.Is_Text (Result_Record, Status, "UNASSESSED") then 3
          elsif Absent (Status) then 0 else 4),
         (if Absent (Channel) then 0
          elsif Channel.Form /= V.Object_Value then 5
          elsif V.Count (Result_Record, Channel) = 0 then 1
          elsif V.Is_True (Result_Record, F (Channel, "accepted")) then 2
          elsif V.Is_False (Result_Record, F (Channel, "accepted")) then 3 else 4),
         (if V.Is_Text (Result_Record, Stage, "SANDBOX_NEVER_STARTED") then 1
          elsif V.Is_Text (Result_Record, Stage, "STOPPED_BY_MANAGER") then 2
          elsif V.Is_Text (Result_Record, Stage, "HARNESS_SIGNALLED") then 3
          elsif Absent (Stage) then 0 else 4),
         Fact (not Absent (Exit_Code)), Fact (Exit_Code.Form = V.Integer_Value),
         (if V.Is_Text (Result_Record, Supervisor_Kind, "SUPERVISED") then 1
          elsif V.Is_Text (Result_Record, Supervisor_Kind, "STOPPED") then 2
          elsif Absent (Supervisor_Kind) then 0 else 3),
         Fact (V.Truth (Result_Record, F (Supervisor, "stoppedByManager")) or else
           Field_Is (Supervisor, "result", "stopped")),
         Fact (not Absent (Executed)), Fact (Executed.Form = V.Object_Value),
         Fact (Executed.Form = V.Object_Value and then V.Is_True (Result_Record, F (Executed, "stable"))),
         Fact (Executed.Form = V.Object_Value and then V.Truth (Result_Record, F (Executed, "changedDuringExecution"))),
         Fact (Executed.Form = V.Object_Value and then V.Truth (Result_Record, F (Executed, "unsatisfiedImports"))),
         Fact (Field_Is (Result, "profile", "private-evaluator-v1") and then Boundary.Form = V.Object_Value));
      if Field_Is (Result, "origin", "agent") then
         if V.Is_True (Result_Record, F (Resource, "ceilingFired")) then
            Produced.Raw.Observations (W.Supervisor_Stopped_Field) := 1;
         elsif not Absent (F (Resource, "ceilingFired"))
           and then not V.Is_False (Result_Record, F (Resource, "ceilingFired")) then
            Produced.Raw.Observations (W.Supervisor_Field) := 3;
         end if;
      end if;
      Produced.Raw.Report_Based :=
        Fact (S (Result, "format") in "junit" | "gnatprove" | "worldline-benchmark-v1");
      Facts (W.R.Private_Profile_Fact) := Fact (Field_Is (Result, "profile", "private-evaluator-v1") and then Field_Is (Result, "origin", "supervisor"));
      Facts (W.R.Exit_Integer_Nonnegative_Fact) := Fact (Nonnegative_Exit);
      Facts (W.R.Records_Present_Fact) := Fact
        (Channel.Form = V.Object_Value and then Supervisor.Form = V.Object_Value and then
         Boundary.Form = V.Object_Value and then Report.Form = V.Object_Value and then
         Snapshot.Form = V.Object_Value and then Executed.Form = V.Object_Value);
      if Facts (W.R.Records_Present_Fact) = 1 then
         Facts (W.R.Channel_Daemon_Accepted_Fact) := Fact (V.Is_True (Result_Record, F (Channel, "accepted")) and then
           Field_Is (Channel, "recordProducer", "daemon-outside-sandbox"));
         Facts (W.R.Supervision_Clean_Fact) := Fact
           (Nonnegative_Exit and then Field_Is (Supervisor, "kind", "SUPERVISED") and then
            V.Is_True (Result_Record, F (Supervisor, "started")) and then
            V.Is_False (Result_Record, F (Supervisor, "stoppedByManager")) and then
            Field_Is (Supervisor, "result", (if V.Decimal (Result_Record, Exit_Code) in "0" | "-0" then "success" else "failure")) and then
            Integer_Matches (F (Supervisor, "launcherExit")) and then
            (Absent (F (Supervisor, "exitCode")) or else Field_Is (Supervisor, "exitCode", "exited")) and then
            (Absent (F (Supervisor, "exitStatus")) or else Integer_Matches (F (Supervisor, "exitStatus"))));
         Facts (W.R.Boundary_Consistent_Fact) := Fact
           (Equal (F (Boundary, "profileId"), F (Result, "profile")) and then
            Absent (F (Boundary, "error")) and then Integer_Matches (F (Boundary, "examinerReturnCode")) and then
            Integer_Matches (F (Boundary, "bootstrapExitCode")) and then
            F (Boundary, "managerBootstrapProperties").Form = V.Object_Value and then
            Field_Is (F (Boundary, "managerBootstrapProperties"), "NoNewPrivileges", "no") and then
            V.Is_True (Result_Record, F (Boundary, "rolesCompleted")));
         Facts (W.R.Report_Mount_Exclusive_Fact) := Fact (V.Is_True (Result_Record, F (Boundary, "reportMountExclusive")));
         Facts (W.R.Collected_Privately_Fact) := Fact (Field_Is (Report, "collection", "private-directory"));
         Facts (W.R.Identities_Match_Fact) := Fact
           (Identity (F (Boundary, "runId")) and then Identity (F (Result, "id")) and then
            Identity (F (Snapshot, "rootSetHash")) and then Identity (F (Executed, "identity")) and then
            Equal (F (Report, "runId"), F (Boundary, "runId")) and then
            Equal (F (Report, "checkId"), F (Result, "id")) and then
            Equal (F (Report, "candidateIdentity"), F (Snapshot, "rootSetHash")) and then
            Equal (F (Report, "verifierIdentity"), F (Executed, "identity")));
         Facts (W.R.Digest_Matches_Fact) := Fact
           (Full_Payload and then F (Report, "sizeBytes").Form = V.Integer_Value and then
            Payload.Length > 0 and then V.Decimal (Result_Record, F (Report, "sizeBytes")) = Image (Payload.Length) and then
            S (Report, "sha256") = Digest (Payload.Data));
         Facts (W.R.Examiner_Observed_Fact) := Fact (Worldline.Evaluation_Role_Native.Original_Observed (Result_Record, "examiner"));
         Facts (W.R.Workers_Separated_Fact) := Fact (Worldline.Evaluation_Role_Native.Original_Workers_Separated (Result_Record));
         if Exit_Code.Form = V.Integer_Value and then Full_Payload and then Produced.Raw.Report_Based = 1 then
            declare
               Parsed : constant P.Parsed_Report := P.Parse
                 (S (Result, "format"), S (Result, "profile"), V.Decimal (Result_Record, Exit_Code),
                  Payload.Data, "", Payload.Data, True);
            begin
               Facts (W.R.Status_Rederived_Fact) := Fact
                 ((Parsed.Status = P.Pass and then Field_Is (Result, "status", "PASS")) or else
                  (Parsed.Status = P.Fail and then Field_Is (Result, "status", "FAIL")));
            end;
         end if;
         Facts (W.R.Examiner_Audit_Clean_Fact) := Fact (Audit and then V.Is_True (Result_Record, F (Executed, "stable")) and then
           Equal (F (Executed, "identity"), F (Executed, "identityAfterExecution")));
      end if;
      Produced.Raw.Report_Facts := Facts;
      Produced.Raw.Presence :=
        (Fact (Identified (F (Result, "id"))), Fact (Status.Form = V.String_Value),
         Fact (Absent (Executed) or else
           (Executed.Form = V.Object_Value and then V.Is_True (Result_Record, F (Executed, "stable")) and then
            not V.Truth (Result_Record, F (Executed, "changedDuringExecution")))),
         Fact (Declaration.Form = V.Object_Value and then not Absent (D ("format")) and then
           Worldline.Raw_JSON.Python_JSON_Equal (V.Slice (Declared, D ("format")), V.Slice (Result_Record, F (Result, "format"))) and then
           (if not Absent (D ("origin")) then
              Worldline.Raw_JSON.Python_JSON_Equal (V.Slice (Declared, D ("origin")), V.Slice (Result_Record, F (Result, "origin"))) and then
              F (Result, "profile").Form = V.Missing
            else F (Result, "profile").Form = V.String_Value and then
              Worldline.Raw_JSON.Python_JSON_Equal (V.Slice (Declared, D ("profile")), V.Slice (Result_Record, F (Result, "profile"))))),
         Fact (Declaration.Form = V.Object_Value and then
           (not V.Truth (Declared, D ("bundle_declared")) or else Identified (F (Executed, "identity")))));
      Produced.Confinement := R.Confinement_Unmeasured;
      Produced.Gap := No_Provider_Gap;
      return Produced;
   end Project_Original;

   function Original_Projection
     (Result_Record, Declared : String;
      Parser_Declaration : String := ""; Raw_Capsule : String := "")
      return Produced_Record is
   begin
      return Project_Original
        (Result_Record, Declared, V.Parse (Result_Record), V.Parse (Declared),
         Parser_Declaration, Raw_Capsule);
   end Original_Projection;

   procedure Recheck_Engine_Inputs
     (Result_Record : String; Result : V.Node; Produced : in out Produced_Record)
     with Global => null, Always_Terminates
   is
      function F (Item : V.Node; Name : String) return V.Node is
        (V.Field (Result_Record, Item, Name));
      function S (Item : V.Node; Name : String) return String is
        (V.Text (Result_Record, F (Item, Name)));
   begin
      if S (Result, "id") = "verifiers-modified" and then
        F (Result, "nativeVerifierInputs").Form = V.Object_Value then
         declare
            Inputs : constant V.Node := F (Result, "nativeVerifierInputs");
            Modified : constant Boolean := Worldline.Evaluation_Policy.Verifiers_Modified
              (V.Slice (Result_Record, F (Inputs, "expectedRequirement")),
               V.Slice (Result_Record, F (Inputs, "returnedContext")));
         begin
            Produced.Raw.Observations (W.Source_Field) := 0;
            Produced.Raw.Observations (W.Status_Field) := (if Modified then 2 else 1);
            Produced.Raw.Observations (W.Channel_Field) := 0;
         end;
      elsif S (Result, "id") = "protected-paths" and then
        F (Result, "nativeProtectedInputs").Form = V.Object_Value then
         declare
            Inputs : constant V.Node := F (Result, "nativeProtectedInputs");
            Touched : constant Boolean := Worldline.Protected_Paths.Touched
              (V.Slice (Result_Record, F (Inputs, "expectedRequirement")),
               V.Slice (Result_Record, F (Inputs, "delta")));
         begin
            Produced.Raw.Observations (W.Source_Field) := 0;
            Produced.Raw.Observations (W.Status_Field) := (if Touched then 2 else 1);
            Produced.Raw.Observations (W.Channel_Field) := 0;
         end;
      end if;
   end Recheck_Engine_Inputs;

   function Project_Acquired
     (Expected, Observed, Result_Record, Declared : String;
      Start, Acquired, Result, Declaration : V.Node;
      Parser_Declaration, Raw_Capsule : String;
      Agent_Data : E.Bytes; Agent_Capture : E.Span)
      return Produced_Record is
      Produced : Produced_Record;
      function F (Parent : V.Node; Name : String) return V.Node is
        (V.Field (Result_Record, Parent, Name));
      function O (Parent : V.Node; Name : String) return V.Node is
        (V.Field (Observed, Parent, Name));
      function E (Name : String) return V.Node is (V.Field (Expected, Start, Name));
      function S (Parent : V.Node; Name : String) return String is
        (V.Text (Result_Record, F (Parent, Name)));
      function OS (Parent : V.Node; Name : String) return String is
        (V.Text (Observed, O (Parent, Name)));
      function Acquisition (Name : String) return V.Node is
         Found : V.Node := V.No_Node;
         Row : V.Node;
      begin
         if Acquired.Form /= V.Array_Value then return Found; end if;
         for I in 1 .. V.Count (Observed, Acquired) loop
            Row := V.Element (Observed, Acquired, I);
            if V.Is_Text (Observed, O (Row, "kind"), Name) then
               if V.Present (Found) then return V.No_Node; end if;
               Found := O (Row, "observation");
            end if;
         end loop;
         return Found;
      end Acquisition;
      Private_Return : constant V.Node := Acquisition ("private-process-return");
      Private_Launch : constant V.Node := Acquisition ("private-launch-association");
      Communication : constant V.Node := Acquisition ("private-communicate-acquisition");
      Boundary_Read : constant V.Node := Acquisition ("private-boundary-acquisition");
      Report_Read : constant V.Node := Acquisition ("private-report");
      Report_Binding : constant V.Node := Acquisition ("private-report-binding");
      Agent_Wait : constant V.Node := Acquisition ("agent-launcher-wait");
      Boundary : constant V.Node := F (Result, "evaluatorBoundary");
      Report : constant V.Node := F (Result, "privateReport");
      Snapshot : constant V.Node := F (Result, "candidateSnapshot");
      Executed : constant V.Node := F (Result, "executedVerifierSet");
      Supervisor : constant V.Node := F (Result, "supervision");
      Original : constant V.Node := F (Result, "rawRunnerResult");
      Raw_Payload : constant Decoded :=
        (if F (Report, "payloadB64").Form = V.String_Value
         then Base64 (S (Report, "payloadB64")) else (0, False, ""));
      Acquired_Report : constant Decoded := Bytes (Observed, O (Report_Read, "bytes"));
      Acquired_Binding : constant Decoded := Bytes (Observed, O (Report_Binding, "bytes"));
      Acquired_Boundary : constant Decoded := Bytes (Observed, O (Boundary_Read, "bytes"));
      Boundary_Node : constant V.Node := V.Parse (Acquired_Boundary.Data);
      Wait_Code : V.Node := V.No_Node;
      Wait_Source_Agent : Boolean := False;
      Private_Supervisor : constant Worldline.Evaluation_Agent_Native.Supervisor_Facts :=
        (if Private_Launch.Form = V.Object_Value and then Private_Return.Form = V.Object_Value then
           Worldline.Evaluation_Agent_Native.Supervisor_Decide
             (Observed, "private-supervision-acquisition", OS (Private_Launch, "unit"),
              V.Slice (Observed, O (Private_Launch, "launchedAtUs")),
              V.Slice (Observed, O (Private_Return, "exitCode")),
              V.Slice (Observed, O (Private_Return, "supervision")), False)
         else (others => <>));
      Status : W.Byte := 0;
      Boundary_Joined, Report_Joined, Invocation_Joined : Boolean := False;
      Original_Joined : Boolean := Original.Form = V.Object_Value;
      Role_Integrity : constant Boolean :=
        Worldline.Evaluation_Role_Native.Valid (Expected, Observed, Result_Record);
      Agent_Invocation : constant Boolean := S (Result, "origin") = "agent";
      Agent_Facts : constant Worldline.Evaluation_Agent_Native.Facts :=
        (if Agent_Invocation then
           Worldline.Evaluation_Agent_Native.Decide
             (Expected, Observed, Result_Record, Agent_Data, Agent_Capture)
         else (others => <>));
      Audit_Redecided : constant Boolean :=
        (if Parser_Declaration'Length > 0 or else Raw_Capsule'Length > 0 then
           Worldline.Source_Audit_Native.Clean
             ((if Original.Form = V.Object_Value then V.Slice (Result_Record, Original)
               else Result_Record), Parser_Declaration, Raw_Capsule)
         else Worldline.Source_Audit_Native.Clean
           (if Original.Form = V.Object_Value then V.Slice (Result_Record, Original)
            else Result_Record));
      function Null_Or_Absent (Item : V.Node) return Boolean is
        (not V.Present (Item) or else V.Is_Null (Item));
      function Clean (Item : V.Node) return Boolean is
        (O (Item, "exception").Form = V.Null_Value);
      function Length_Matches (Data : String; Size : V.Node; Length : Natural) return Boolean is
        (V.Decimal (Data, Size) = Image (Length));
      function Boundary_Source_Joins return Boolean is
      begin
         if Boundary_Node.Form /= V.Object_Value then return False; end if;
         for I in 1 .. V.Count (Acquired_Boundary.Data, Boundary_Node) loop
            declare
               Name : constant String := V.Member_Name (Acquired_Boundary.Data, Boundary_Node, I);
            begin
               if not V.Equal (Acquired_Boundary.Data,
                 V.Field (Acquired_Boundary.Data, Boundary_Node, Name),
                 Result_Record, F (Boundary, Name)) then return False; end if;
            end;
         end loop;
         return True;
      end Boundary_Source_Joins;
   begin
      Invocation_Joined := Start.Form = V.Object_Value and then
        V.Nonempty_Text (Expected, E ("invocationId")) and then
        V.Equal (Expected, E ("checkId"), Result_Record, F (Result, "id")) and then
        V.Equal (Expected, E ("candidateSnapshot"), Result_Record, Snapshot);
      if V.Present (Original) and then Original.Form /= V.Null_Value then
         -- Every original field remains independently retained; the parent
         -- ordered-return relation handles the two permitted derived fields.
         for I in 1 .. V.Count (Result_Record, Original) loop
            declare
               Name : constant String := V.Member_Name (Result_Record, Original, I);
            begin
               if Name not in "executionBinding" | "evaluation" and then
                  not Worldline.Raw_JSON.Python_JSON_Equal
                    (V.Slice (Result_Record, F (Original, Name)),
                     V.Slice (Result_Record, F (Result, Name))) then
                  Invocation_Joined := False;
                  Original_Joined := False;
               end if;
            end;
         end loop;
      end if;
      --  An actual in-process engine return has no child wait/report channel.
      --  Preserve its original operand domain without discarding the retained
      --  invocation/acquisition fields or treating a Python verdict as native
      --  completion. Its complete original return must match every carried
      --  field (apart from the two original derived fields above), and the
      --  separate retained start must name this check and this exact start.
      --  External/report/agent inputs keep the acquisition relation below.
      if Start.Form = V.Object_Value and then Acquired.Form = V.Array_Value
        --  Full-array emptiness is the original in-process no-acquisition
        --  domain, not a named lookup: duplicate/conflicting/malformed private,
        --  report, agent or unknown rows never masquerade as absent sources.
        and then V.Count (Observed, Acquired) = 0
        and then Original_Joined
        and then E ("invocationId").Form = V.String_Value
        and then E ("evaluationRun").Form = V.String_Value
        and then E ("worldInstance").Form = V.String_Value
        and then V.Equal (Expected, E ("checkId"), Result_Record, F (Result, "id"))
        and then V.Equal (Expected, Start, Result_Record,
          F (Result, "engineInvocationObservation"))
        and then ((E ("candidateSnapshot").Form in V.Missing | V.Null_Value
          and then F (Original, "candidateSnapshot").Form in V.Missing | V.Null_Value)
          or else V.Equal (Expected, E ("candidateSnapshot"),
            Result_Record, F (Original, "candidateSnapshot")))
        and then V.Is_Text (Result_Record, F (Original, "origin"), "engine")
        and then V.Is_Text (Result_Record, F (Result, "origin"), "engine")
        and then V.Is_Text (Result_Record, F (Original, "format"), "engine")
        and then V.Is_Text (Result_Record, F (Result, "format"), "engine")
        and then V.Is_Text (Declared, V.Field (Declared, Declaration, "origin"), "engine")
        and then V.Is_Text (Declared, V.Field (Declared, Declaration, "format"), "engine")
        and then Private_Return.Form = V.Missing
        and then Private_Launch.Form = V.Missing
        and then Agent_Wait.Form = V.Missing
        and then F (Result, "protectedProviderCapture").Form in V.Missing | V.Null_Value
        and then Boundary.Form in V.Missing | V.Null_Value
        and then Report.Form in V.Missing | V.Null_Value
        and then Agent_Data'Length = 0 and then Agent_Capture.Length = 0
      then
         --  Native original facts still enforce engine shape, malformed values,
         --  status, declaration and full presence. In particular exit/bundle/
         --  nonempty accepted channels cannot create an engine completion.
         Produced := Project_Original
           (Result_Record, Declared, Result, Declaration,
            Parser_Declaration, Raw_Capsule);
         Recheck_Engine_Inputs (Result_Record, Result, Produced);
         return Produced;
      end if;
      if V.Is_True (Observed, O (Agent_Wait, "waitReturnObserved")) then
         Wait_Code := O (Agent_Wait, "returncode"); Wait_Source_Agent := True;
      elsif Private_Return.Form = V.Object_Value then Wait_Code := O (Private_Return, "exitCode");
      end if;
      -- No caller result/status authorizes a completed report. Actual wait
      -- bytes and the original native report parser supply those operands.
      Produced.Raw.Observations (W.Source_Field) := (if Wait_Source_Agent then 1 else 2);
      Produced.Raw.Observations (W.Exit_Present_Field) := Bit (V.Present (Wait_Code) and then not V.Is_Null (Wait_Code));
      Produced.Raw.Observations (W.Exit_Integer_Field) := Bit (Wait_Code.Form = V.Integer_Value);
      Produced.Raw.Report_Based := Bit (S (Result, "format") in "junit" | "gnatprove" | "worldline-benchmark-v1");
      if Produced.Raw.Report_Based = 1 and then Wait_Code.Form = V.Integer_Value then
         declare
            Parsed : constant P.Parsed_Report := P.Parse
              (S (Result, "format"), S (Result, "profile"), V.Decimal (Observed, Wait_Code),
               Raw_Payload.Data, "", Raw_Payload.Data, Raw_Payload.Valid);
         begin
            Status := (if Parsed.Status = P.Pass then 1 elsif Parsed.Status = P.Fail then 2 else 4);
         end;
      elsif Agent_Invocation then
         Status := (if Agent_Facts.Valid then Agent_Facts.Status else 4);
      elsif not V.Present (F (Result, "status")) or else V.Is_Null (F (Result, "status")) then Status := 0;
      elsif S (Result, "status") = "UNASSESSED" then Status := 3;
      else Status := 4;
      end if;
      Produced.Raw.Observations (W.Status_Field) := Status;
      Boundary_Joined := Acquired_Boundary.Valid and then
        V.Is_True (Observed, O (Boundary_Read, "readReturned")) and then
        V.Is_True (Observed, O (Boundary_Read, "readReachedEof")) and then Clean (Boundary_Read) and then
        Boundary_Source_Joins and then
        V.Equal (Observed, O (Private_Return, "boundary"), Result_Record, Boundary);
      Report_Joined := Acquired_Report.Valid and then Raw_Payload.Valid and then
        Acquired_Report.Data = Raw_Payload.Data and then
        V.Is_True (Observed, O (Report_Read, "readReturned")) and then
        V.Is_True (Observed, O (Report_Read, "readReachedEof")) and then
        V.Equal (Observed, O (O (Report_Read, "details"), "binding"),
          Acquired_Binding.Data, V.Parse (Acquired_Binding.Data));
      Produced.Raw.Observations (W.Supervisor_Field) :=
        (if Private_Supervisor.Valid then Private_Supervisor.Kind
         elsif Null_Or_Absent (F (Supervisor, "kind")) then 0 else 3);
      Produced.Raw.Observations (W.Supervisor_Stopped_Field) :=
        Bit (Private_Supervisor.Valid and then Private_Supervisor.Stopped);
      Produced.Raw.Observations (W.Channel_Field) :=
        (if Report_Joined and then Boundary_Joined and then Private_Return.Form = V.Object_Value then 2
         elsif V.Present (Acquisition ("private-collection-exception")) then 3
         elsif F (Result, "resultChannel").Form not in V.Object_Value | V.Null_Value | V.Missing then 5
         elsif not V.Present (F (Result, "resultChannel")) or else V.Is_Null (F (Result, "resultChannel")) then 0
         else 4);
      if Private_Supervisor.Valid and then Private_Supervisor.Stopped then
         Produced.Raw.Observations (W.Stage_Field) := 2;
      elsif Wait_Code.Form = V.Integer_Value and then not V.Nonnegative (Observed, Wait_Code) then
         Produced.Raw.Observations (W.Stage_Field) := 3;
      end if;
      Produced.Raw.Observations (W.Bundle_Present_Field) := Bit (V.Present (Executed) and then not V.Is_Null (Executed));
      Produced.Raw.Observations (W.Bundle_Is_Mapping_Field) := Bit (Executed.Form = V.Object_Value);
      -- Preserve the original stable predicate and additionally require native
      -- identity correspondence; an explicit false fact is never upgraded.
      Produced.Raw.Observations (W.Bundle_Stable_Field) := Bit
        (Executed.Form = V.Object_Value and then V.Is_True (Result_Record, F (Executed, "stable")) and then
         V.Nonempty_Text (Result_Record, F (Executed, "identity")) and then
         V.Equal (Result_Record, F (Executed, "identity"), Result_Record, F (Executed, "identityAfterExecution")) and then
         not V.Truth (Result_Record, F (Executed, "changedDuringExecution")));
      Produced.Raw.Observations (W.Bundle_Changed_Field) := Bit
        (Executed.Form = V.Object_Value and then V.Truth (Result_Record, F (Executed, "changedDuringExecution")));
      Produced.Raw.Observations (W.Unsatisfied_Imports_Field) := Bit
        (Executed.Form = V.Object_Value and then V.Truth (Result_Record, F (Executed, "unsatisfiedImports")));
      Produced.Raw.Observations (W.Isolation_Field) := Bit (Role_Integrity);
      Produced.Raw.Report_Facts :=
        (Bit (S (Result, "profile") = "private-evaluator-v1" and then S (Result, "origin") = "supervisor" and then
           Private_Return.Form = V.Object_Value),
         Bit (Wait_Code.Form = V.Integer_Value and then V.Nonnegative (Observed, Wait_Code) and then
           V.Equal (Observed, Wait_Code, Result_Record, F (Result, "exitCode"))),
         Bit (Boundary.Form = V.Object_Value and then Report.Form = V.Object_Value and then
           Snapshot.Form = V.Object_Value and then Executed.Form = V.Object_Value and then
           Supervisor.Form = V.Object_Value and then F (Result, "resultChannel").Form = V.Object_Value),
         Bit (Report_Joined and then Boundary_Joined and then
           V.Is_True (Result_Record, F (F (Result, "resultChannel"), "accepted")) and then
           S (F (Result, "resultChannel"), "recordProducer") = "daemon-outside-sandbox"),
         Bit (Private_Supervisor.Valid and then Private_Supervisor.Kind = 1 and then
           not Private_Supervisor.Stopped and then
           V.Equal (Observed, O (Private_Return, "supervision"), Result_Record, Supervisor) and then
           V.Is_True (Result_Record, F (Supervisor, "started")) and then
           V.Is_False (Result_Record, F (Supervisor, "stoppedByManager")) and then
           V.Is_Text (Result_Record, F (Supervisor, "result"),
             (if V.Decimal (Observed, Wait_Code) in "0" | "-0" then "success" else "failure")) and then
           F (Supervisor, "launcherExit").Form = V.Integer_Value and then
           V.Equal (Result_Record, F (Supervisor, "launcherExit"), Observed, Wait_Code) and then
           (Null_Or_Absent (F (Supervisor, "exitCode")) or else
            V.Is_Text (Result_Record, F (Supervisor, "exitCode"), "exited")) and then
           (Null_Or_Absent (F (Supervisor, "exitStatus")) or else
            (F (Supervisor, "exitStatus").Form = V.Integer_Value and then
             V.Equal (Result_Record, F (Supervisor, "exitStatus"), Observed, Wait_Code))) and then
           V.Is_True (Observed, O (Communication, "communicateReturned")) and then Clean (Communication) and then
           V.Equal (Observed, O (Communication, "launcherReturncode"), Observed, Wait_Code) and then
           Worldline.Native_Lifetime_Observation.Clean
             (Observed, Result_Record, V.Decimal (Observed, Wait_Code))),
         Bit (Boundary_Joined and then Null_Or_Absent (F (Boundary, "error")) and then
           V.Equal (Result_Record, F (Boundary, "examinerReturnCode"), Observed, Wait_Code) and then
           V.Equal (Result_Record, F (Boundary, "bootstrapExitCode"), Observed, Wait_Code) and then
           V.Equal (Result_Record, F (Boundary, "profileId"), Result_Record, F (Result, "profile")) and then
           F (Boundary, "managerBootstrapProperties").Form = V.Object_Value and then
           S (F (Boundary, "managerBootstrapProperties"), "NoNewPrivileges") = "no" and then
           V.Is_True (Result_Record, F (Boundary, "rolesCompleted"))),
         Bit (Role_Integrity and then V.Is_True (Result_Record, F (Boundary, "reportMountExclusive"))),
         Bit (Report_Joined and then S (Report, "collection") = "private-directory"),
         Bit (Invocation_Joined and then Identity_Value (Result_Record, F (Report, "runId")) and then
           Identity_Value (Result_Record, F (Boundary, "runId")) and then
           Identity_Value (Result_Record, F (Result, "id")) and then
           Identity_Value (Result_Record, F (Snapshot, "rootSetHash")) and then
           Identity_Value (Result_Record, F (Executed, "identity")) and then
           V.Equal (Result_Record, F (Report, "checkId"), Result_Record, F (Result, "id")) and then
           V.Equal (Result_Record, F (Report, "runId"), Result_Record, F (Boundary, "runId")) and then
           V.Equal (Result_Record, F (Report, "checkId"), Expected, E ("checkId")) and then
           V.Equal (Result_Record, F (Report, "candidateIdentity"), Expected, V.Field (Expected, E ("candidateSnapshot"), "rootSetHash")) and then
           V.Equal (Result_Record, F (Report, "verifierIdentity"), Result_Record, F (Executed, "identity"))),
         Bit (Raw_Payload.Valid and then Raw_Payload.Length > 0 and then Raw_Payload.Length <= 10_000_000 and then
           Length_Matches (Result_Record, F (Report, "sizeBytes"), Raw_Payload.Length) and then
           S (Report, "sha256") = Digest (Raw_Payload.Data)),
         Bit (Role_Integrity), Bit (Role_Integrity),
         Bit ((Status = 1 and then S (Result, "status") = "PASS") or else (Status = 2 and then S (Result, "status") = "FAIL")),
         Bit (Audit_Redecided and then V.Is_True (Result_Record, F (Executed, "stable")) and then
           Worldline.Raw_JSON.Python_JSON_Equal
             (V.Slice (Result_Record, F (Executed, "identity")),
              V.Slice (Result_Record, F (Executed, "identityAfterExecution")))));
      Produced.Raw.Presence :=
        (Bit (V.Nonempty_Text (Result_Record, F (Result, "id"))),
         Bit (F (Result, "status").Form = V.String_Value),
         Bit ((Executed.Form in V.Missing | V.Null_Value) or else
           (Produced.Raw.Observations (W.Bundle_Stable_Field) = 1 and then
            Produced.Raw.Observations (W.Bundle_Changed_Field) = 0)),
         Bit (Declaration.Form = V.Object_Value and then
           not Null_Or_Absent (V.Field (Declared, Declaration, "format")) and then
           Worldline.Raw_JSON.Python_JSON_Equal
             (V.Slice (Declared, V.Field (Declared, Declaration, "format")), V.Slice (Result_Record, F (Result, "format"))) and then
           (if not Null_Or_Absent (V.Field (Declared, Declaration, "origin")) then
              Worldline.Raw_JSON.Python_JSON_Equal
                (V.Slice (Declared, V.Field (Declared, Declaration, "origin")), V.Slice (Result_Record, F (Result, "origin"))) and then
              not V.Present (F (Result, "profile"))
            else F (Result, "profile").Form = V.String_Value and then
              Worldline.Raw_JSON.Python_JSON_Equal
                (V.Slice (Declared, V.Field (Declared, Declaration, "profile")), V.Slice (Result_Record, F (Result, "profile"))))),
         Bit (Declaration.Form = V.Object_Value and then
           (not V.Truth (Declared, V.Field (Declared, Declaration, "bundle_declared")) or else
             V.Nonempty_Text (Result_Record, F (Executed, "identity")))));
      Recheck_Engine_Inputs (Result_Record, Result, Produced);
      if Agent_Invocation then
         Produced.Raw.Observations (W.Status_Field) := Status;
         Produced.Raw.Observations (W.Supervisor_Field) :=
           (if Agent_Facts.Valid then Agent_Facts.Supervisor else 3);
         Produced.Raw.Observations (W.Supervisor_Stopped_Field) :=
           Bit (Agent_Facts.Valid and then Agent_Facts.Stopped);
         Produced.Raw.Observations (W.Stage_Field) :=
           (if Agent_Facts.Valid then Agent_Facts.Stage else 0);
      end if;
      Produced.Confinement := Worldline.Report_Custody_Native.Observe
        (Expected, Observed, Result_Record, Produced.Raw);
      Produced.Gap :=
        (if F (Result, "protectedProviderCapture").Form in V.Missing | V.Null_Value
         then Protected_Custody_Unavailable else No_Provider_Gap);
      return Produced;
   end Project_Acquired;

   function Derive
     (Expected, Observed, Result_Record, Declared : String;
      Parser_Declaration : String := ""; Raw_Capsule : String := "";
      Agent_Data : E.Bytes := (1 .. 0 => 0);
      Agent_Capture : E.Span := (1, 0))
      return Produced_Record is
      Start : constant V.Node := V.Parse (Expected);
      Acquired : constant V.Node := V.Parse (Observed);
      Result : constant V.Node := V.Parse (Result_Record);
      Declaration : constant V.Node := V.Parse (Declared);
      Produced : Produced_Record;
      function F (Name : String) return V.Node is
        (V.Field (Result_Record, Result, Name));
      -- This is an operand-domain choice, before any acquisition-only work
      -- or classification. Present empty/malformed sources are not absence.
      -- Full original report fields never establish observed confinement.
      -- Object native control operands retain their original engine role.
      Record_Only : constant Boolean :=
        Start.Form = V.Null_Value and then Acquired.Form = V.Null_Value
        and then Result.Form = V.Object_Value
        and then Agent_Data'Length = 0 and then Agent_Capture.Length = 0
        and then F ("engineInvocationObservation").Form in V.Missing | V.Null_Value
        and then F ("engineRawObservations").Form in V.Missing | V.Null_Value
        and then F ("rawRunnerResult").Form in V.Missing | V.Null_Value
        and then F ("protectedProviderCapture").Form in V.Missing | V.Null_Value
        and then F ("nativeVerifierInputs").Form in V.Missing | V.Null_Value | V.Object_Value
        and then
          ((F ("nativeVerifierInputs").Form /= V.Object_Value
            and then F ("nativeProtectedInputs").Form /= V.Object_Value)
           or else V.Is_Text (Result_Record, F ("origin"), "engine"))
        and then F ("nativeProtectedInputs").Form in V.Missing | V.Null_Value | V.Object_Value;
   begin
      if Result.Form /= V.Object_Value or else Declaration.Form not in V.Object_Value | V.Null_Value or else
         Start.Form not in V.Object_Value | V.Null_Value or else Acquired.Form not in V.Array_Value | V.Null_Value then
         Produced.Raw.Observations (W.Channel_Field) := 5;
         return Produced;
      end if;
      if Record_Only then
         Produced := Project_Original
           (Result_Record, Declared, Result, Declaration, Parser_Declaration, Raw_Capsule);
         Recheck_Engine_Inputs (Result_Record, Result, Produced);
         return Produced;
      end if;
      return Project_Acquired
        (Expected, Observed, Result_Record, Declared, Start, Acquired, Result, Declaration,
         Parser_Declaration, Raw_Capsule, Agent_Data, Agent_Capture);
   end Derive;
end Worldline.Evaluation_Producer;
