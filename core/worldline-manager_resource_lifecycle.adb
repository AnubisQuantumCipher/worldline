with Worldline.Producer_Values;
package body Worldline.Manager_Resource_Lifecycle with SPARK_Mode is
   package V renames Worldline.Producer_Values;
   use type V.Value_Kind;
   function Hex (C : Character) return Boolean is
     (C in '0' .. '9' or else C in 'a' .. 'f');
   function Unit_Valid (Unit : String) return Boolean is
   begin
      if Unit'Length /= 54 then return False; end if;
      if Unit (Unit'First .. Unit'First + 9) /= "worldline-"
        or else Unit (Unit'Last - 7 .. Unit'Last) /= ".service"
      then return False; end if;
      for K in 0 .. 35 loop
         if K in 8 | 13 | 18 | 23 then
            if Unit (Unit'First + 10 + K) /= '-' then return False; end if;
         elsif not Hex (Unit (Unit'First + 10 + K)) then return False;
         end if;
      end loop;
      return True;
   end Unit_Valid;
   function Identity_Valid (Unit, Invocation, Group : String) return Boolean is
      Nonzero : Boolean := False;
      Start : Natural;
   begin
      if not Unit_Valid (Unit) or else Invocation'Length /= 32 then return False; end if;
      for C of Invocation loop
         if not Hex (C) then return False; end if;
         Nonzero := Nonzero or else C /= '0';
      end loop;
      if not Nonzero or else Group'Length <= Unit'Length or else Group (Group'First) /= '/'
        or else Group (Group'Last - Unit'Length + 1 .. Group'Last) /= Unit
        or else Group (Group'Last - Unit'Length) /= '/' then return False; end if;
      -- POSIX pathlib preserves exactly two initial slashes, but normalizes
      -- three or more, interior repeated slashes, dot and trailing slash.
      Start := Group'First + 1;
      if Start <= Group'Last and then Group (Start) = '/' then Start := Start + 1; end if;
      if Start > Group'Last then return False; end if;
      declare
         Component : Natural := Start;
      begin
         for K in Start .. Group'Last loop
            pragma Loop_Invariant (Component in Start .. K);
            if Group (K) = '/' then
               if K = Component or else Group (Component .. K - 1) = "." or else Group (Component .. K - 1) = ".." then return False; end if;
               Component := K + 1;
            end if;
         end loop;
         return Component <= Group'Last and then Group (Component .. Group'Last) /= "." and then Group (Component .. Group'Last) /= "..";
      end;
   end Identity_Valid;
   function Space (C : Character) return Boolean is
     (Character'Pos (C) in 9 .. 13 | 28 .. 32);
   function Break (C : Character) return Boolean is
     (Character'Pos (C) in 10 .. 13 | 28 .. 30);
   function Events_State (Events : String) return Natural is
      -- Total for an empty Events of any bounds; equal to Events'First otherwise.
      P : Natural := Natural'Max (1, Events'First);
      Populated : Boolean := False;
      Empty_Group : Boolean := False;
   begin
      -- read_text(encoding="ascii") admitted domain and Python splitlines/split.
      for C of Events loop
         if Character'Pos (C) > 127 then return 0; end if;
      end loop;
      -- The original raised Constraint_Error (P + 1) on every such text that reached
      -- its last line; every other such text already returned 0. Refuse exactly those.
      if Events'Last = Natural'Last then return 0; end if;
      while P <= Events'Last loop
         pragma Loop_Variant (Increases => P);
         pragma Loop_Invariant (P >= Events'First);
         declare
            Line_Start : constant Natural := P;
            Line_End, Key_Start, Key_End, Value_Start, Value_End : Natural;
         begin
            while P <= Events'Last and then not Break (Events (P)) loop
               pragma Loop_Invariant (P in Line_Start .. Events'Last); pragma Loop_Variant (Increases => P);
               P := P + 1;
            end loop;
            Line_End := P;
            if P <= Events'Last then
               P := P + 1;
               if Events (P - 1) = Character'Val (13) and then P <= Events'Last
                 and then Events (P) = Character'Val (10) then P := P + 1; end if;
            end if;
            Key_Start := Line_Start;
            while Key_Start < Line_End and then Space (Events (Key_Start)) loop
               pragma Loop_Invariant (Key_Start in Line_Start .. Line_End); pragma Loop_Variant (Increases => Key_Start);
               Key_Start := Key_Start + 1;
            end loop;
            Key_End := Key_Start;
            while Key_End < Line_End and then not Space (Events (Key_End)) loop
               pragma Loop_Invariant (Key_End in Key_Start .. Line_End); pragma Loop_Variant (Increases => Key_End);
               Key_End := Key_End + 1;
            end loop;
            Value_Start := Key_End;
            while Value_Start < Line_End and then Space (Events (Value_Start)) loop
               pragma Loop_Invariant (Value_Start in Key_End .. Line_End); pragma Loop_Variant (Increases => Value_Start);
               Value_Start := Value_Start + 1;
            end loop;
            Value_End := Value_Start;
            while Value_End < Line_End and then not Space (Events (Value_End)) loop
               pragma Loop_Invariant (Value_End in Value_Start .. Line_End); pragma Loop_Variant (Increases => Value_End);
               if Events (Value_End) not in '0' .. '9' then return 0; end if;
               Value_End := Value_End + 1;
            end loop;
            if Key_Start = Key_End or else Value_Start = Value_End then return 0; end if;
            declare
               Q : Natural := Value_End;
            begin
               while Q < Line_End and then Space (Events (Q)) loop
                  pragma Loop_Invariant (Q in Value_End .. Line_End); pragma Loop_Variant (Increases => Q);
                  Q := Q + 1;
               end loop;
               if Q /= Line_End then return 0; end if;
            end;
            -- Compare keys against earlier complete lines, not a bounded map.
            declare
               Q : Natural := Events'First;
            begin
               while Q < Line_Start loop
                  pragma Loop_Variant (Increases => Q);
                  pragma Loop_Invariant (Q in Events'First .. Line_Start);
                  while Q < Line_Start and then Space (Events (Q)) loop
                     pragma Loop_Invariant (Q in Q'Loop_Entry .. Line_Start); pragma Loop_Variant (Increases => Q);
                     Q := Q + 1;
                  end loop;
                  declare
                     A : constant Natural := Q;
                  begin
                     while Q < Line_Start and then not Space (Events (Q)) loop
                        pragma Loop_Invariant (Q in A .. Line_Start); pragma Loop_Variant (Increases => Q);
                        Q := Q + 1;
                     end loop;
                     if Q > A and then Events (A .. Q - 1) = Events (Key_Start .. Key_End - 1) then return 0; end if;
                  end;
                  while Q < Line_Start and then not Break (Events (Q)) loop
                     pragma Loop_Invariant (Q in Q'Loop_Entry .. Line_Start); pragma Loop_Variant (Increases => Q);
                     Q := Q + 1;
                  end loop;
                  if Q < Line_Start then Q := Q + 1; end if;
               end loop;
            end;
            if Events (Key_Start .. Key_End - 1) = "populated" then
               Populated := True;
               Empty_Group := Events (Value_Start .. Value_End - 1) = "0";
            end if;
         end;
      end loop;
      return (if Populated and then Empty_Group then 2 else 1);
   end Events_State;
   function Decide (Capture : String) return String is
      Root : constant V.Node := V.Parse (Capture);
      function F (Name : String) return V.Node is (V.Field (Capture, Root, Name));
      function T (Name : String) return String is (V.Text (Capture, F (Name)));
      function S (Parent : V.Node; Name : String) return String is
        (V.Text (Capture, V.Field (Capture, Parent, Name)));
      function E (Parent : V.Node; Name, Expected : String) return Boolean is
        (V.Is_Text (Capture, V.Field (Capture, Parent, Name), Expected));
      function Identity (N : V.Node; Exact : Boolean := True) return Boolean is
        (N.Form = V.Object_Value and then (not Exact or else V.Count (Capture, N) = 3)
         and then E (N, "unit", T ("unit"))
         and then Identity_Valid (T ("unit"), S (N, "invocationId"), S (N, "controlGroup")));
      function Result (State : String := "UNKNOWN"; Reason : String := "";
                       Action : String := "done"; Accepted : Boolean := False;
                       Value : String := "null"; Live : String := "null") return String is
        ("{""action"":" & V.Quote (Action) & ",""state"":" & V.Quote (State)
         & ",""reason"":" & (if Reason = "" then "null" else V.Quote (Reason))
         & ",""accepted"":" & (if Accepted or else State in "NORMAL_PIPE_COMPLETION" | "MANAGER_CGROUP_EMPTY" | "MANAGER_CGROUP_REMOVED" then "true" else "false")
         & ",""value"":" & Value & ",""live"":" & Live & "}");
      function Positive (N : V.Node) return Boolean is
         Token : constant String := V.Slice (Capture, N);
      begin
         if N.Form = V.Boolean_Value then return V.Is_True (Capture, N); end if;
         if N.Form = V.Object_Value then
            declare
               H : constant String := S (N, "hex");
            begin
               if E (N, "pythonType", "builtins.int") then
                  return H'Length > 0 and then H (H'First) /= '-' and then H /= "0x0";
               elsif E (N, "pythonType", "builtins.float") then
                  if H in "inf" | "nan" then return True; end if;
                  if H'Length = 0 or else H (H'First) = '-' then return False; end if;
                  for C of H loop
                     exit when C = 'p';
                     if C in '1' .. '9' | 'a' .. 'f' then return True; end if;
                  end loop;
               end if;
               return False;
            end;
         end if;
         return N.Form in V.Integer_Value | V.Number_Value and then Token'Length > 0
           and then Token (Token'First) /= '-' and then V.Truth (Capture, N);
      end Positive;
      function Zero (N : V.Node) return Boolean is
        ((N.Form = V.Integer_Value and then V.Decimal (Capture, N) = "0") or else
         (E (N, "pythonType", "builtins.int") and then E (N, "hex", "0x0")));
      function Pipe_Action return String is
         Protocols : constant V.Node := F ("launcherProtocols");
         function P (Name : String) return V.Node is (V.Field (Capture, Protocols, Name));
         function Gate (Name, Action : String; Expected : Boolean) return String is
         begin
            if not V.Present (P (Name)) then return Action; end if;
            if P (Name).Form /= V.Boolean_Value or else V.Is_True (Capture, P (Name)) /= Expected then return "unowned"; end if;
            return "continue";
         end Gate;
         function One_Gate (Name, Action : String) return String
           with Pre => Name'Length <= Natural'Last - 9 and then Action'Length <= Natural'Last - 8 is
            N : constant V.Node := P (Name);
         begin
            if not V.Present (N) then return Action; end if;
            if E (N, "pythonType", "builtins.int") then
               return (if E (N, "hex", "0x1") then "continue" else "unowned");
            elsif E (N, "pythonType", "builtins.float") then
               return (if E (N, "hex", "0x1.0000000000000p+0") then "continue" else "unowned");
            elsif N.Form = V.Boolean_Value then
               return (if V.Is_True (Capture, N) then "continue" else "unowned");
            elsif N.Form = V.Object_Value and then V.Present (V.Field (Capture, N, "reference")) then
               return Gate (Name & "EqualsOne", Action & "_compare", True);
            end if;
            return "unowned";
         end One_Gate;
         G : constant String := Gate ("nonempty", "pipe_nonempty", True);
      begin
         if not V.Is_True (Capture, F ("managerSame")) then return "unowned"; end if;
         if F ("unit").Form /= V.String_Value then return "pipe_unit_type"; end if;
         if not Unit_Valid (T ("unit")) then return "unowned"; end if;
         if not V.Present (F ("argsKind")) then return "pipe_argv"; end if;
         if T ("argsKind") not in "list" | "tuple" then return "unowned"; end if;
         if G /= "continue" then return G; end if;
         declare First : constant String := Gate ("firstDiffers", "pipe_first", False);
         begin if First /= "continue" then return First; end if; end;
         declare Time : constant String := Gate ("timeLeZero", "pipe_time", False);
         begin if Time /= "continue" then return Time; end if; end;
         if (E (F ("launchedAtUs"), "pythonType", "builtins.int") or else
             E (F ("launchedAtUs"), "pythonType", "builtins.float") or else
             F ("launchedAtUs").Form = V.Boolean_Value) and then not Positive (F ("launchedAtUs")) then return "unowned"; end if;
         if not V.Present (P ("separator")) then return "pipe_separator"; end if;
         if not V.Present (P ("options")) then return "pipe_slice"; end if;
         declare Count : constant String := One_Gate ("unitCount", "pipe_unit_count");
         begin if Count /= "continue" then return Count; end if; end;
         declare Prefixes : constant String := One_Gate ("prefixSum", "pipe_prefix_sum");
         begin if Prefixes /= "continue" then return Prefixes; end if; end;
         declare Pipes : constant String := One_Gate ("pipeCount", "pipe_pipe_count");
         begin if Pipes /= "continue" then return Pipes; end if; end;
         declare Pty : constant String := Gate ("ptyAbsent", "pipe_pty", True);
         begin if Pty /= "continue" then return Pty; end if; end;
         declare User : constant String := Gate ("userPresent", "pipe_user", True);
         begin if User /= "continue" then return User; end if; end;
         declare Exec : constant String := Gate ("execPresent", "pipe_exec", True);
         begin if Exec /= "continue" then return Exec; end if; end;
         declare Kill : constant String := Gate ("killPresent", "pipe_kill", True);
         begin if Kill /= "continue" then return Kill; end if; end;
         -- Exact builtin sequences/string operands have no foreign protocols:
         -- bind their observed operations back to the raw argv/options, rather
         -- than granting ownership from a supplied sequence of success labels.
         if V.Is_True (Capture, F ("argsExactBuiltin")) and then V.Is_True (Capture, P ("optionsExactBuiltin")) then
            declare
               Args : constant V.Node := F ("args");
               Options : constant V.Node := P ("options");
               N : constant Natural := V.Count (Capture, Args);
               Stop : Natural := N;
               Strings : Boolean := F ("systemdRun").Form = V.String_Value;
               Units, Prefixes, Pipes : Natural := 0;
               User, Exec, Kill, Pty : Boolean := False;
            begin
               if N = 0 or else Options.Form /= V.Array_Value then return "unowned"; end if;
               Strings := Strings and then V.Element (Capture, Args, 1).Form = V.String_Value;
               for K in 2 .. N loop
                  if V.Is_Text (Capture, V.Element (Capture, Args, K), "--") then Stop := K - 1; exit; end if;
               end loop;
               for K in 1 .. V.Count (Capture, Options) loop
                  Strings := Strings and then V.Element (Capture, Options, K).Form = V.String_Value;
               end loop;
               if Strings then
                  if not V.Equal (Capture, V.Element (Capture, Args, 1), Capture, F ("systemdRun"))
                    or else V.Count (Capture, Options) /= Stop - 1 then return "unowned"; end if;
                  for K in 1 .. V.Count (Capture, Options) loop
                     pragma Loop_Invariant (Units < K and then Prefixes < K and then Pipes < K);
                     if not V.Equal (Capture, V.Element (Capture, Args, K + 1), Capture, V.Element (Capture, Options, K)) then return "unowned"; end if;
                     declare A : constant String := V.Text (Capture, V.Element (Capture, Options, K));
                     begin
                        if A = S (Protocols, "unitOption") then Units := Units + 1; end if;
                        if A'Length >= 7 and then A (A'First .. A'First + 6) = "--unit=" then Prefixes := Prefixes + 1; end if;
                        if A = "--pipe" then Pipes := Pipes + 1; end if;
                        Pty := Pty or else A = "--pty";
                        User := User or else A = "--user";
                        Exec := Exec or else A = "--service-type=exec";
                        Kill := Kill or else A = "--property=KillMode=control-group";
                     end;
                  end loop;
                  if Units /= 1 or else Prefixes /= 1 or else Pipes /= 1 or else Pty or else not User or else not Exec or else not Kill then return "unowned"; end if;
               end if;
            end;
         end if;
         return "owned";
      end Pipe_Action;
      Op : constant String := T ("op");
      Id : constant V.Node := F ("identity");
      Shown : constant V.Node := F ("shown");
      Reading : constant V.Node := F ("reading");
      Workload : constant String := T ("workload");
      Check : constant Boolean := Workload'Length >= 6
        and then Workload (Workload'First .. Workload'First + 5) = "check:";
   begin
      if Root.Form /= V.Object_Value then return Result (Reason => "invalid manager capture"); end if;
      if Op in "owned" | "identity" | "terminal" then
         declare Ownership : constant String := Pipe_Action;
         begin
            if Ownership = "unowned" then
               return Result (Reason => "owned pipe launcher identity was not established");
            elsif Ownership /= "owned" then
               return Result (Action => Ownership);
            end if;
         end;
      end if;
      if Op = "terminal" then
         if not V.Present (F ("afterFailureTruth")) then return Result (Action => "truth_after_failure"); end if;
         if F ("afterFailureTruth").Form /= V.Boolean_Value then return Result (Reason => "after-failure truth observation is malformed"); end if;
         if V.Is_False (Capture, F ("afterFailureTruth")) and then T ("returncodeKind") = "exact-int"
           and then Zero (F ("returncode")) then return Result ("NORMAL_PIPE_COMPLETION"); end if;
         if V.Is_Null (F ("returncode")) then return Result (Reason => "launcher has no terminal wait result"); end if;
         if not V.Present (F ("identityObject")) then return Result (Action => "identity_object"); end if;
         if V.Is_Null (F ("identityObject")) then return Result (Reason => "no captured manager invocation/cgroup identity"); end if;
         if not V.Present (F ("identityUnitObserved")) then return Result (Action => "identity_unit"); end if;
         if not V.Is_Text (Capture, F ("identityUnitObserved"), T ("unit")) then
            return Result (Reason => "no captured manager invocation/cgroup identity"); end if;
         if not V.Present (Shown) then return Result (Action => "query_manager"); end if;
      end if;
      if Op = "owned" then return Result (Accepted => True); end if;
      if Op = "route" then
         return Result (Action => (if not V.Truth (Capture, F ("unit")) then "no_unit" elsif Check then "check" else "ordinary"));
      elsif Op = "persisted" then
         return Result (Accepted => Identity (Id) and then
           (not V.Present (F ("identityKeyCount")) or else V.Decimal (Capture, F ("identityKeyCount")) = "3"));
      elsif Op = "identity" then
         if not V.Present (Shown) then return Result (Action => "query_manager"); end if;
         return Result (Accepted => E (Shown, "Id", T ("unit")) and then E (Shown, "LoadState", "loaded")
           and then Identity_Valid (T ("unit"), S (Shown, "InvocationID"), S (Shown, "ControlGroup")));
      elsif Op in "manager" | "terminal" then
         if Shown.Form = V.Null_Value then return Result (Reason => "manager terminal observation is unavailable"); end if;
         if not V.Present (V.Field (Capture, Id, "unit")) then return Result (Action => "manager_identity_unit"); end if;
         if not E (Shown, "Id", S (Id, "unit")) then return Result ("CONFLICT", "manager workload identity differs"); end if;
         if not V.Present (V.Field (Capture, Id, "invocationId")) then return Result (Action => "manager_identity_invocation"); end if;
         if not E (Shown, "InvocationID", S (Id, "invocationId")) then return Result ("CONFLICT", "manager workload identity differs"); end if;
         if not V.Present (V.Field (Capture, Id, "controlGroup")) then return Result (Action => "manager_identity_group"); end if;
         if not (E (Shown, "ControlGroup", "") or else E (Shown, "ControlGroup", S (Id, "controlGroup"))) then
            return Result ("CONFLICT", "manager workload identity differs"); end if;
         if E (Shown, "LoadState", "loaded") and then E (Shown, "ControlGroup", S (Id, "controlGroup"))
           and then S (Shown, "ActiveState") in "active" | "activating" | "reloading" | "deactivating" then
            return Result ("MANAGER_WORKLOAD_LIVE"); end if;
         if not E (Shown, "LoadState", "loaded") or else S (Shown, "ActiveState") not in "inactive" | "failed"
           or else S (Shown, "SubState") not in "dead" | "failed" or else not E (Shown, "MainPID", "0") then
            return Result (Reason => "manager has not observed terminal workload state"); end if;
         if not V.Present (F ("events")) then return Result (Action => "read_events"); end if;
         if F ("events").Form = V.Null_Value then
            if not V.Present (F ("directory")) then return Result (Action => "lstat_directory"); end if;
            if T ("directory") = "missing" then return Result ("MANAGER_CGROUP_REMOVED"); end if;
            return Result (Reason => "cgroup events are missing");
         end if;
         case Events_State (T ("events")) is
            when 0 => return Result (Reason => "cgroup events are malformed");
            when 1 => return Result (Reason => "owned cgroup is populated or unknown");
            when others => return Result ("MANAGER_CGROUP_EMPTY");
         end case;
      elsif Op = "usage" then
         if not V.Truth (Capture, F ("unit")) then return Result; end if;
         if Check and then (not Identity (Id) or else not V.Equal (Capture, Id, Capture, V.Field (Capture, Reading, "workloadIdentity"))) then return Result; end if;
         if E (Reading, "state", "OBSERVED") then
            declare
               Value : constant V.Node := V.Field (Capture, Reading, "currentMemoryBytes");
            begin
               return Result (Action => "select_current_memory",
                              Value => (if V.Present (Value) then V.Slice (Capture, Value) else "null"));
            end;
         end if;
         return Result;
      elsif Op = "live" then
         if not V.Truth (Capture, F ("unit")) then return Result (Live => "true"); end if;
         if Check then
            if not V.Is_True (Capture, F ("observationType")) or else not E (Reading, "unit", T ("unit")) then return Result; end if;
            declare
               Terminal : constant V.Node := F ("terminalCapture");
               Observed_Id : constant V.Node := V.Field (Capture, Reading, "identity");
               Nested : constant String := V.Slice (Capture, Terminal);
            begin
               if Terminal.Form /= V.Object_Value or else Nested'Length >= Capture'Length
                 or else not (E (Terminal, "op", "manager") or else E (Terminal, "op", "terminal"))
                 or else not Identity (Id) or else not E (Terminal, "unit", T ("unit"))
                 or else not V.Equal (Capture, V.Field (Capture, Terminal, "identity"), Capture, Id)
                 or else not V.Equal (Capture, Observed_Id, Capture, Id) then return Result; end if;
               declare
                  Derived : constant String := Decide (Nested);
                  D_Root : constant V.Node := V.Parse (Derived);
                  D_State : constant String := V.Text (Derived, V.Field (Derived, D_Root, "state"));
               begin
                  if not E (Reading, "state", D_State) or else
                    not V.Is_Text (Derived, V.Field (Derived, D_Root, "action"), "done") then return Result; end if;
                  if D_State = "MANAGER_WORKLOAD_LIVE" then return Result (Live => "true"); end if;
                  if D_State in "MANAGER_CGROUP_EMPTY" | "MANAGER_CGROUP_REMOVED"
                    and then V.Is_True (Derived, V.Field (Derived, D_Root, "accepted")) then
                     return Result (Live => "false");
                  end if;
               end;
            end;
         elsif E (Reading, "state", "CAPTURED") and then V.Truth (Capture, V.Field (Capture, Reading, "ActiveState")) then
            return Result (Live => (if S (Reading, "ActiveState") in "active" | "activating" | "reloading" | "deactivating" then "true" else "false"));
         end if;
         return Result;
      end if;
      return Result (Reason => "unknown manager capture operation");
   end Decide;
end Worldline.Manager_Resource_Lifecycle;
