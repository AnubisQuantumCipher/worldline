with Worldline.Evaluation_Agent_Native;
with Worldline.Evaluation_Wire;

-- Fixed ordinary raw fixtures. These are not protected-host evidence.
procedure Native_Supervisor_Controls is
   package N renames Worldline.Evaluation_Agent_Native;
   use type Worldline.Evaluation_Wire.Byte;
   Unit_Name : constant String := "worldline-11111111-2222-3333-4444-555555555555.service";
   Acquisition_Kind : constant String := "agent-supervision-acquisition";

   procedure Case_1 is
      Observed : constant String :=
         "[{""kind"":""agent-supervision-acquisition"",""occurrence"":0,""observation"":{""unit" &
         """:""worldline-11111111-2222-3333-4444-555555555555.service"",""sinceUs"":0,""site" &
         """:""journal-tool-unavailable"",""journalctl"":null}}]";
      Supervisor : constant String :=
         "{""events"":[],""kind"":""INDETERMINATE"",""unit"":""worldline-11111111-2222-3333-444" &
         "4-555555555555.service"",""source"":""journal-unavailable"",""launcherExit"":1,""sta" &
         "rted"":false,""stoppedByManager"":false,""supervisionEvidence"":null,""exitCode"":n" &
         "ull,""exitStatus"":null,""result"":null,""windowMilliseconds"":10000,""launcherStde" &
         "rr"":""""}";
      Facts : constant N.Supervisor_Facts := N.Supervisor_Decide
        (Observed, Acquisition_Kind, Unit_Name, "0", "1", Supervisor, False);
   begin
      if Facts.Valid /= True or else Facts.Kind /= 3 or else Facts.Stopped then
         raise Program_Error with "unavailable observation remains valid";
      end if;
   end Case_1;

   procedure Case_2 is
      Observed : constant String :=
         "[{""kind"":""agent-supervision-acquisition"",""occurrence"":0,""observation"":{""unit" &
         """:""worldline-11111111-2222-3333-4444-555555555555.service"",""sinceUs"":0,""site" &
         """:""journal-tool-unavailable""}}]";
      Supervisor : constant String :=
         "{""events"":[],""kind"":""INDETERMINATE"",""unit"":""worldline-11111111-2222-3333-444" &
         "4-555555555555.service"",""source"":""journal-unavailable"",""launcherExit"":1,""sta" &
         "rted"":false,""stoppedByManager"":false,""supervisionEvidence"":null,""exitCode"":n" &
         "ull,""exitStatus"":null,""result"":null,""windowMilliseconds"":10000,""launcherStde" &
         "rr"":""""}";
      Facts : constant N.Supervisor_Facts := N.Supervisor_Decide
        (Observed, Acquisition_Kind, Unit_Name, "0", "1", Supervisor, False);
   begin
      if Facts.Valid /= False then
         raise Program_Error with "missing unavailable witness rejected";
      end if;
   end Case_2;

   procedure Case_3 is
      Observed : constant String :=
         "[{""kind"":""agent-supervision-acquisition"",""occurrence"":0,""observation"":{""unit" &
         """:""worldline-11111111-2222-3333-4444-555555555555.service"",""sinceUs"":0,""site" &
         """:""journal-tool-unavailable"",""journalctl"":null}},{""kind"":""agent-supervision-" &
         "acquisition"",""occurrence"":1,""observation"":{""unit"":""worldline-11111111-2222-3" &
         "333-4444-555555555555.service"",""sinceUs"":0,""site"":""journal-poll"",""readerUid""" &
         ":1000,""argv"":[""journalctl"",""--user"",""-u"",""worldline-11111111-2222-3333-4444-" &
         "555555555555.service"",""-o"",""json"",""--no-pager"",""--since=@0""],""stdout"":{""enco" &
         "ding"":""base64"",""payload"":""""},""processReturnObserved"":true,""processWaitReturn" &
         "Observed"":true,""stdoutReachedEof"":true,""stderrReachedEof"":true,""exception"":n" &
         "ull,""returncode"":0,""processWaitReturncode"":0}}]";
      Supervisor : constant String :=
         "{""events"":[],""kind"":""INDETERMINATE"",""unit"":""worldline-11111111-2222-3333-444" &
         "4-555555555555.service"",""source"":""journal-unavailable"",""launcherExit"":1,""sta" &
         "rted"":false,""stoppedByManager"":false,""supervisionEvidence"":null,""exitCode"":n" &
         "ull,""exitStatus"":null,""result"":null,""windowMilliseconds"":10000,""launcherStde" &
         "rr"":""""}";
      Facts : constant N.Supervisor_Facts := N.Supervisor_Decide
        (Observed, Acquisition_Kind, Unit_Name, "0", "1", Supervisor, False);
   begin
      if Facts.Valid /= False then
         raise Program_Error with "poll after unavailable terminal rejected";
      end if;
   end Case_3;

   procedure Case_4 is
      Observed : constant String :=
         "[{""kind"":""agent-supervision-acquisition"",""occurrence"":0,""observation"":{""unit" &
         """:""worldline-11111111-2222-3333-4444-555555555555.service"",""sinceUs"":0,""site" &
         """:""journal-poll"",""readerUid"":1000,""argv"":[""journalctl"",""--user"",""-u"",""worldl" &
         "ine-11111111-2222-3333-4444-555555555555.service"",""-o"",""json"",""--no-pager"",""" &
         "--since=@0""],""stdout"":{""encoding"":""base64"",""payload"":""eyJfU1lTVEVNRF9VTklUIj" &
         "oidXNlckAxMDAwLnNlcnZpY2UiLCJfQ09NTSI6InN5c3RlbWQiLCJVU0VSX1VOSVQiOiJ3b3JsZG" &
         "xpbmUtMTExMTExMTEtMjIyMi0zMzMzLTQ0NDQtNTU1NTU1NTU1NTU1LnNlcnZpY2UiLCJfX1JFQU" &
         "xUSU1FX1RJTUVTVEFNUCI6MSwiTUVTU0FHRV9JRCI6IjM5ZjUzNDc5ZDNhMDQ1YWM4ZTExNzg2Mj" &
         "Q4MjMxZmJmIiwiRVhJVF9DT0RFIjpudWxsLCJFWElUX1NUQVRVUyI6bnVsbH0=""},""processRet" &
         "urnObserved"":true,""processWaitReturnObserved"":true,""stdoutReachedEof"":true,""" &
         "stderrReachedEof"":true,""exception"":null,""returncode"":0,""processWaitReturncod" &
         "e"":0}},{""kind"":""agent-supervision-acquisition"",""occurrence"":1,""observation"":" &
         "{""unit"":""worldline-11111111-2222-3333-4444-555555555555.service"",""sinceUs"":0" &
         ",""site"":""journal-poll"",""readerUid"":1000,""argv"":[""journalctl"",""--user"",""-u"",""" &
         "worldline-11111111-2222-3333-4444-555555555555.service"",""-o"",""json"",""--no-pa" &
         "ger"",""--since=@0""],""stdout"":{""encoding"":""base64"",""payload"":""""},""processRetur" &
         "nObserved"":true,""processWaitReturnObserved"":true,""stdoutReachedEof"":true,""st" &
         "derrReachedEof"":true,""exception"":null,""returncode"":0,""processWaitReturncode""" &
         ":0}}]";
      Supervisor : constant String :=
         "{""events"":[],""kind"":""LAUNCH_FAILED"",""unit"":""worldline-11111111-2222-3333-444" &
         "4-555555555555.service"",""source"":""journal"",""launcherExit"":1,""started"":false," &
         """stoppedByManager"":false,""supervisionEvidence"":null,""exitCode"":null,""exitSta" &
         "tus"":null,""result"":null,""windowMilliseconds"":10000,""launcherStderr"":""""}";
      Facts : constant N.Supervisor_Facts := N.Supervisor_Decide
        (Observed, Acquisition_Kind, Unit_Name, "0", "1", Supervisor, False);
   begin
      if Facts.Valid /= True or else Facts.Kind /= 3 or else Facts.Stopped then
         raise Program_Error with "started state cannot leak into later empty poll";
      end if;
   end Case_4;

   procedure Case_5 is
      Observed : constant String :=
         "[{""kind"":""agent-supervision-acquisition"",""occurrence"":0,""observation"":{""unit" &
         """:""worldline-11111111-2222-3333-4444-555555555555.service"",""sinceUs"":0,""site" &
         """:""journal-poll"",""readerUid"":1000,""argv"":[""journalctl"",""--user"",""-u"",""worldl" &
         "ine-11111111-2222-3333-4444-555555555555.service"",""-o"",""json"",""--no-pager"",""" &
         "--since=@0""],""stdout"":{""encoding"":""base64"",""payload"":""eyJfU1lTVEVNRF9VTklUIj" &
         "oidXNlckAxMDAwLnNlcnZpY2UiLCJfQ09NTSI6InN5c3RlbWQiLCJVU0VSX1VOSVQiOiJ3b3JsZG" &
         "xpbmUtMTExMTExMTEtMjIyMi0zMzMzLTQ0NDQtNTU1NTU1NTU1NTU1LnNlcnZpY2UiLCJfX1JFQU" &
         "xUSU1FX1RJTUVTVEFNUCI6MSwiTUVTU0FHRV9JRCI6IjdkNDk1OGU4NDJkYTRhNzU4ZjZjMWNkYz" &
         "diMzZkY2M1IiwiRVhJVF9DT0RFIjpudWxsLCJFWElUX1NUQVRVUyI6bnVsbH0=""},""processRet" &
         "urnObserved"":true,""processWaitReturnObserved"":true,""stdoutReachedEof"":true,""" &
         "stderrReachedEof"":true,""exception"":null,""returncode"":0,""processWaitReturncod" &
         "e"":0}},{""kind"":""agent-supervision-acquisition"",""occurrence"":1,""observation"":" &
         "{""unit"":""worldline-11111111-2222-3333-4444-555555555555.service"",""sinceUs"":0" &
         ",""site"":""journal-poll"",""readerUid"":1000,""argv"":[""journalctl"",""--user"",""-u"",""" &
         "worldline-11111111-2222-3333-4444-555555555555.service"",""-o"",""json"",""--no-pa" &
         "ger"",""--since=@0""],""stdout"":{""encoding"":""base64"",""payload"":""""},""processRetur" &
         "nObserved"":true,""processWaitReturnObserved"":true,""stdoutReachedEof"":true,""st" &
         "derrReachedEof"":true,""exception"":null,""returncode"":0,""processWaitReturncode""" &
         ":0}}]";
      Supervisor : constant String :=
         "{""events"":[],""kind"":""LAUNCH_FAILED"",""unit"":""worldline-11111111-2222-3333-444" &
         "4-555555555555.service"",""source"":""journal"",""launcherExit"":1,""started"":false," &
         """stoppedByManager"":false,""supervisionEvidence"":null,""exitCode"":null,""exitSta" &
         "tus"":null,""result"":null,""windowMilliseconds"":10000,""launcherStderr"":""""}";
      Facts : constant N.Supervisor_Facts := N.Supervisor_Decide
        (Observed, Acquisition_Kind, Unit_Name, "0", "1", Supervisor, False);
   begin
      if Facts.Valid /= True or else Facts.Kind /= 3 or else Facts.Stopped then
         raise Program_Error with "launched state cannot leak into later empty poll";
      end if;
   end Case_5;

   procedure Case_6 is
      Observed : constant String :=
         "[{""kind"":""agent-supervision-acquisition"",""occurrence"":0,""observation"":{""unit" &
         """:""worldline-11111111-2222-3333-4444-555555555555.service"",""sinceUs"":0,""site" &
         """:""journal-poll"",""readerUid"":1000,""argv"":[""journalctl"",""--user"",""-u"",""worldl" &
         "ine-11111111-2222-3333-4444-555555555555.service"",""-o"",""json"",""--no-pager"",""" &
         "--since=@0""],""stdout"":{""encoding"":""base64"",""payload"":""eyJfU1lTVEVNRF9VTklUIj" &
         "oidXNlckAxMDAwLnNlcnZpY2UiLCJfQ09NTSI6InN5c3RlbWQiLCJVU0VSX1VOSVQiOiJ3b3JsZG" &
         "xpbmUtMTExMTExMTEtMjIyMi0zMzMzLTQ0NDQtNTU1NTU1NTU1NTU1LnNlcnZpY2UiLCJfX1JFQU" &
         "xUSU1FX1RJTUVTVEFNUCI6MSwiTUVTU0FHRV9JRCI6IjM5ZjUzNDc5ZDNhMDQ1YWM4ZTExNzg2Mj" &
         "Q4MjMxZmJmIiwiRVhJVF9DT0RFIjpudWxsLCJFWElUX1NUQVRVUyI6bnVsbH0KeyJfU1lTVEVNRF" &
         "9VTklUIjoidXNlckAxMDAwLnNlcnZpY2UiLCJfQ09NTSI6InN5c3RlbWQiLCJVU0VSX1VOSVQiOi" &
         "J3b3JsZGxpbmUtMTExMTExMTEtMjIyMi0zMzMzLTQ0NDQtNTU1NTU1NTU1NTU1LnNlcnZpY2UiLC" &
         "JfX1JFQUxUSU1FX1RJTUVTVEFNUCI6MSwiTUVTU0FHRV9JRCI6Ijk4ZTMyMjIwM2Y3YTRlZDI5MG" &
         "QwOWZlMDNjMDlmZTE1IiwiRVhJVF9DT0RFIjoiZXhpdGVkIiwiRVhJVF9TVEFUVVMiOjB9CnsiX1" &
         "NZU1RFTURfVU5JVCI6InVzZXJAMTAwMC5zZXJ2aWNlIiwiX0NPTU0iOiJzeXN0ZW1kIiwiVVNFUl" &
         "9VTklUIjoid29ybGRsaW5lLTExMTExMTExLTIyMjItMzMzMy00NDQ0LTU1NTU1NTU1NTU1NS5zZX" &
         "J2aWNlIiwiX19SRUFMVElNRV9USU1FU1RBTVAiOjEsIk1FU1NBR0VfSUQiOiI5OGUzMjIyMDNmN2" &
         "E0ZWQyOTBkMDlmZTAzYzA5ZmUxNSIsIkVYSVRfQ09ERSI6ImV4aXRlZCIsIkVYSVRfU1RBVFVTIj" &
         "o3fQ==""},""processReturnObserved"":true,""processWaitReturnObserved"":true,""stdo" &
         "utReachedEof"":true,""stderrReachedEof"":true,""exception"":null,""returncode"":0,""" &
         "processWaitReturncode"":0}}]";
      Supervisor : constant String :=
         "{""events"":[{""messageId"":""39f53479d3a045ac8e11786248231fbf"",""message"":"""",""job" &
         "Type"":null,""jobResult"":null,""exitCode"":null,""exitStatus"":null,""managerPid"":n" &
         "ull,""realtimeUs"":1},{""messageId"":""98e322203f7a4ed290d09fe03c09fe15"",""message" &
         """:"""",""jobType"":null,""jobResult"":null,""exitCode"":""exited"",""exitStatus"":0,""man" &
         "agerPid"":null,""realtimeUs"":1},{""messageId"":""98e322203f7a4ed290d09fe03c09fe15" &
         """,""message"":"""",""jobType"":null,""jobResult"":null,""exitCode"":""exited"",""exitStat" &
         "us"":7,""managerPid"":null,""realtimeUs"":1}],""kind"":""SUPERVISED"",""unit"":""worldli" &
         "ne-11111111-2222-3333-4444-555555555555.service"",""source"":""journal"",""launche" &
         "rExit"":0,""started"":true,""stoppedByManager"":false,""supervisionEvidence"":""star" &
         "ted-entry"",""exitCode"":""exited"",""exitStatus"":0,""result"":""success"",""windowMill" &
         "iseconds"":10000,""launcherStderr"":""""}";
      Facts : constant N.Supervisor_Facts := N.Supervisor_Decide
        (Observed, Acquisition_Kind, Unit_Name, "0", "0", Supervisor, False);
   begin
      if Facts.Valid /= True or else Facts.Kind /= 1 or else Facts.Stopped then
         raise Program_Error with "first exit selected instead of last exit";
      end if;
   end Case_6;

   procedure Case_7 is
      Observed : constant String :=
         "[{""kind"":""agent-supervision-acquisition"",""occurrence"":0,""observation"":{""unit" &
         """:""worldline-11111111-2222-3333-4444-555555555555.service"",""sinceUs"":0,""site" &
         """:""journal-poll"",""readerUid"":1000,""argv"":[""journalctl"",""--user"",""-u"",""worldl" &
         "ine-11111111-2222-3333-4444-555555555555.service"",""-o"",""json"",""--no-pager"",""" &
         "--since=@0""],""stdout"":{""encoding"":""base64"",""payload"":""eyJfU1lTVEVNRF9VTklUIj" &
         "oidXNlckAxMDAwLnNlcnZpY2UiLCJfQ09NTSI6InN5c3RlbWQiLCJVU0VSX1VOSVQiOiJ3b3JsZG" &
         "xpbmUtMTExMTExMTEtMjIyMi0zMzMzLTQ0NDQtNTU1NTU1NTU1NTU1LnNlcnZpY2UiLCJfX1JFQU" &
         "xUSU1FX1RJTUVTVEFNUCI6MSwiTUVTU0FHRV9JRCI6IjM5ZjUzNDc5ZDNhMDQ1YWM4ZTExNzg2Mj" &
         "Q4MjMxZmJmIiwiRVhJVF9DT0RFIjpudWxsLCJFWElUX1NUQVRVUyI6bnVsbH0KeyJfU1lTVEVNRF" &
         "9VTklUIjoidXNlckAxMDAwLnNlcnZpY2UiLCJfQ09NTSI6InN5c3RlbWQiLCJVU0VSX1VOSVQiOi" &
         "J3b3JsZGxpbmUtMTExMTExMTEtMjIyMi0zMzMzLTQ0NDQtNTU1NTU1NTU1NTU1LnNlcnZpY2UiLC" &
         "JfX1JFQUxUSU1FX1RJTUVTVEFNUCI6MSwiTUVTU0FHRV9JRCI6Ijk4ZTMyMjIwM2Y3YTRlZDI5MG" &
         "QwOWZlMDNjMDlmZTE1IiwiRVhJVF9DT0RFIjoiZXhpdGVkIiwiRVhJVF9TVEFUVVMiOjB9CnsiX1" &
         "NZU1RFTURfVU5JVCI6InVzZXJAMTAwMC5zZXJ2aWNlIiwiX0NPTU0iOiJzeXN0ZW1kIiwiVVNFUl" &
         "9VTklUIjoid29ybGRsaW5lLTExMTExMTExLTIyMjItMzMzMy00NDQ0LTU1NTU1NTU1NTU1NS5zZX" &
         "J2aWNlIiwiX19SRUFMVElNRV9USU1FU1RBTVAiOjEsIk1FU1NBR0VfSUQiOiI5OGUzMjIyMDNmN2" &
         "E0ZWQyOTBkMDlmZTAzYzA5ZmUxNSIsIkVYSVRfQ09ERSI6ImV4aXRlZCIsIkVYSVRfU1RBVFVTIj" &
         "o3fQ==""},""processReturnObserved"":true,""processWaitReturnObserved"":true,""stdo" &
         "utReachedEof"":true,""stderrReachedEof"":true,""exception"":null,""returncode"":0,""" &
         "processWaitReturncode"":0}}]";
      Supervisor : constant String :=
         "{""events"":[{""messageId"":""39f53479d3a045ac8e11786248231fbf"",""message"":"""",""job" &
         "Type"":null,""jobResult"":null,""exitCode"":null,""exitStatus"":null,""managerPid"":n" &
         "ull,""realtimeUs"":1},{""messageId"":""98e322203f7a4ed290d09fe03c09fe15"",""message" &
         """:"""",""jobType"":null,""jobResult"":null,""exitCode"":""exited"",""exitStatus"":9,""man" &
         "agerPid"":null,""realtimeUs"":1},{""messageId"":""98e322203f7a4ed290d09fe03c09fe15" &
         """,""message"":"""",""jobType"":null,""jobResult"":null,""exitCode"":""exited"",""exitStat" &
         "us"":7,""managerPid"":null,""realtimeUs"":1}],""kind"":""SUPERVISED"",""unit"":""worldli" &
         "ne-11111111-2222-3333-4444-555555555555.service"",""source"":""journal"",""launche" &
         "rExit"":0,""started"":true,""stoppedByManager"":false,""supervisionEvidence"":""star" &
         "ted-entry"",""exitCode"":""exited"",""exitStatus"":0,""result"":""success"",""windowMill" &
         "iseconds"":10000,""launcherStderr"":""""}";
      Facts : constant N.Supervisor_Facts := N.Supervisor_Decide
        (Observed, Acquisition_Kind, Unit_Name, "0", "0", Supervisor, False);
   begin
      if Facts.Valid /= False then
         raise Program_Error with "retained event mismatch rejected";
      end if;
   end Case_7;
begin
   Case_1;
   Case_2;
   Case_3;
   Case_4;
   Case_5;
   Case_6;
   Case_7;
end Native_Supervisor_Controls;
