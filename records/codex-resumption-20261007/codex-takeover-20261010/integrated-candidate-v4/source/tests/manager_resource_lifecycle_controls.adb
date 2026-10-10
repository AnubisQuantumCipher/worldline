with Worldline.Manager_Resource_Lifecycle;
with Worldline.Producer_Values;
procedure Manager_Resource_Lifecycle_Controls with SPARK_Mode is
   package M renames Worldline.Manager_Resource_Lifecycle;
   package V renames Worldline.Producer_Values;
   Unit : constant String := "worldline-00000000-0000-4000-8000-000000000000.service";
   Invocation : constant String := "11111111111141118111111111111111";
   LF : constant String := (1 => Character'Val (10));
   Identity : constant String := "{""unit"":" & V.Quote (Unit)
     & ",""invocationId"":" & V.Quote (Invocation)
     & ",""controlGroup"":" & V.Quote ("/fixture/" & Unit) & "}";
   function State (Raw : String) return String is
     (V.Text (V.Field (M.Decide (Raw), "state")));
   function Usage (Observed : String) return String is
     (V.Field (M.Decide ("{""op"":""usage"",""unit"":" & V.Quote (Unit)
      & ",""workload"":""check:ordinary"",""identity"":" & Identity
      & ",""reading"":" & Observed & "}"), "value"));
   function Hex_Int (H : String) return String is
     ("{""pythonType"":""builtins.int"",""hex"":" & V.Quote (H) & "}");
   Options : constant String := "[" & V.Quote ("--user") & "," & V.Quote ("--unit=" & Unit)
     & "," & V.Quote ("--pipe") & "," & V.Quote ("--service-type=exec")
     & "," & V.Quote ("--property=KillMode=control-group") & "]";
   Prefix_Pending : constant String :=
     "{""nonempty"":true,""firstDiffers"":false,""timeLeZero"":false,""separatorContains"":true,"
     & """separator"":" & Hex_Int ("0x6") & ",""options"":" & Options
     & ",""optionsExactBuiltin"":true,""unitOption"":" & V.Quote ("--unit=" & Unit)
     & ",""unitCount"":" & Hex_Int ("0x1");
   Protocols : constant String := Prefix_Pending & ",""prefixSum"":" & Hex_Int ("0x1")
     & ",""pipeCount"":" & Hex_Int ("0x1")
     & ",""ptyAbsent"":true,""userPresent"":true,""execPresent"":true,""killPresent"":true}";
   function Launcher (Launch_Hex, Code_Hex : String; Captured : String := Protocols) return String is
     ("{""op"":""terminal"",""unit"":" & V.Quote (Unit)
      & ",""managerSame"":true,""systemdRun"":""/usr/bin/systemd-run"",""argsKind"":""list"",""argsExactBuiltin"":true,"
      & """args"":[""/usr/bin/systemd-run""," & Options (2 .. Options'Last - 1)
      & "," & V.Quote ("--") & "," & V.Quote ("/fixture/check") & "]"
      & ",""launchedAtUs"":" & Hex_Int (Launch_Hex) & ",""returncode"":" & Hex_Int (Code_Hex)
      & ",""returncodeKind"":""exact-int"",""afterFailure"":false,""afterFailureTruth"":false,"
      & """identity"":" & Identity & ",""launcherProtocols"":" & Captured & "}");
   function Restart (Terminal, Label : String) return String is
     (V.Field (M.Decide ("{""op"":""live"",""unit"":" & V.Quote (Unit)
      & ",""workload"":""check:ordinary"",""identity"":" & Identity
      & ",""observationType"":true,""reading"":{""unit"":" & V.Quote (Unit)
      & ",""identity"":" & Identity & ",""state"":" & V.Quote (Label)
      & "},""terminalCapture"":" & Terminal & "}"), "live"));
   Huge_Decimal : constant String := "1" & (1 .. 5000 => '0');
begin
   pragma Assert (M.Unit_Valid (Unit));
   pragma Assert (M.Identity_Valid (Unit, Invocation, "/fixture/" & Unit));
   pragma Assert (M.Identity_Valid (Unit, Invocation, "//fixture/" & Unit));
   pragma Assert (not M.Identity_Valid (Unit, Invocation, "///fixture/" & Unit));
   pragma Assert (not M.Identity_Valid (Unit, Invocation, "/fixture/../" & Unit));
   pragma Assert (not M.Identity_Valid (Unit, Invocation, "/fixture//" & Unit));
   pragma Assert (not M.Identity_Valid (Unit, Invocation, "/fixture/" & Unit & "/"));
   pragma Assert (not M.Identity_Valid (Unit, (1 .. 32 => '0'), "/fixture/" & Unit));
   pragma Assert (M.Events_State ("populated 0" & LF & "frozen 0" & LF) = 2);
   pragma Assert (M.Events_State ("populated 00" & LF) = 1);
   pragma Assert (M.Events_State ("populated 1" & LF) = 1);
   pragma Assert (M.Events_State ("frozen 0" & LF) = 1);
   pragma Assert (M.Events_State ("populated 0" & LF & "populated 0" & LF) = 0);
   pragma Assert (M.Events_State (LF) = 0);
   pragma Assert (M.Events_State ("populated +0" & LF) = 0);
   pragma Assert (M.Events_State ("populated 0 extra" & LF) = 0);
   for C in 9 .. 32 loop
      if C in 9 .. 13 | 28 .. 32 then
         pragma Assert (M.Events_State ("populated" & Character'Val (C) & "0" & LF) =
           (if C in 10 .. 13 | 28 .. 30 then 0 else 2));
      end if;
   end loop;
   pragma Assert (Usage ("{""state"":""OBSERVED"",""currentMemoryBytes"":13,""workloadIdentity"":" & Identity & "}") = "13");
   pragma Assert (Usage ("{""state"":""OBSERVED"",""currentMemoryBytes"":" & Huge_Decimal
      & ",""unrelated"":" & Huge_Decimal & ",""workloadIdentity"":" & Identity & "}") = Huge_Decimal);
   pragma Assert (State (Launcher ("0x" & (1 .. 5000 => 'a'), "0x0")) = "NORMAL_PIPE_COMPLETION");
   pragma Assert (V.Text (V.Field (M.Decide (Launcher ("0x1", "0x0", Prefix_Pending & "}")), "action")) = "pipe_prefix_sum");
   pragma Assert (Restart ("{""op"":""manager"",""unit"":" & V.Quote (Unit)
      & ",""identity"":" & Identity & ",""shown"":null}", "MANAGER_CGROUP_EMPTY") = "null");
   pragma Assert (Restart ("null", "MANAGER_CGROUP_REMOVED") = "null");
   pragma Assert (Usage ("{""state"":""OBSERVED"",""currentMemoryBytes"":13,""workloadIdentity"":null}") = "null");
   pragma Assert (State ("{""op"":""manager"",""unit"":" & V.Quote (Unit)
     & ",""identity"":" & Identity & ",""shown"":null}") = "UNKNOWN");
end Manager_Resource_Lifecycle_Controls;
