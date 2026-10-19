with Worldline.Archive_Base64;
with Worldline.Runner_Lifecycle;
with Worldline.Runner_Lifecycle_Bytes;
package body Worldline.Runner_Outcome_Bytes with SPARK_Mode is
   package B renames Worldline.Runner_Lifecycle_Bytes;
   package A renames Worldline.Archive_Base64;
   use type E.Encoding_Level;
   use type E.Q.Byte;
   use type E.Value_Kind;
   use type E.Count;
   Invalid : constant String := "{""status"":""INVALID_CAPTURE""}";
   function Need (Name : String) return String is
     ("{""status"":""CAPTURE_REQUIRED"",""operation"":""" & Name & """}");
   function Bit (Value : Boolean) return String is
     (if Value then "true" else "false");

   function Decide (Data : E.Bytes; Capture : E.Span) return String is
      function F (Item : E.Span; Name : String) return E.Span is
        (B.Field (Data, Item, Name));
      function T (Item : E.Span; Text : String) return Boolean is
        (B.Text_Is (Data, Item, Text));
      function Form (Item : E.Span) return E.Value_Kind is
        (E.Decode (Data, Item, E.Finalization).Form);
      --  Reference spelling is factual, not a bound on original operand size.
      --  Stream the original finalization text leaf; no String conversion.
      function Reference (Item : E.Span) return Boolean is
         Value : constant E.View := E.Decode (Data, Item, E.Finalization);
         Leaf : constant A.Span := (Value.Payload.Encoded.First, Value.Payload.Encoded.Length);
         Size : E.Count;
      begin
         if Value.Form /= E.Text_Value or else Value.Payload.Level /= 1 or else
           not A.Canonical (Data, Leaf) then return False; end if;
         Size := A.Decoded_Length (Data, Leaf);
         if Size = 0 or else A.Decoded_Byte (Data, Leaf, 0) not in
           Character'Pos ('1') .. Character'Pos ('9') then return False; end if;
         for I in E.Count range 1 .. Size - 1 loop
            if A.Decoded_Byte (Data, Leaf, I) not in
              Character'Pos ('0') .. Character'Pos ('9') then return False; end if;
         end loop;
         return True;
      end Reference;
      function Builtin (Item : E.Span) return Boolean is
        (Form (Item) = E.Object_Value and then T (F (Item, "profile"), "builtin-v1")
         and then Form (F (Item, "value")) /= E.Invalid);
      function Foreign (Item : E.Span) return Boolean is
        (Form (Item) = E.Object_Value and then
         T (F (Item, "profile"), "python-actual-protocol-v1") and then
         Reference (F (Item, "reference")) and then
         Reference (F (Item, "typeReference")));
      Membership : constant E.Span := F (Capture, "stopMembership");
      Resources : constant E.Span := F (Capture, "resourceObservation");
      Resource_Container : constant E.Span := F (Capture, "resourceContainer");
      Manager : constant E.Span := F (Capture, "managerResult");
      Kind : constant E.Span := F (Capture, "supervisionKind");
      Exit_Code : constant E.Span := F (Capture, "exitCode");
      Cancelled, Timed_Out, Stopped : Boolean;
      Fired : Boolean;
      Unknown, Evidence_Hit, Evidence_Manager : Boolean := False;
      Evidence_Unknown, Reason_Ceiling : Boolean := False;
      Launch_Failed : Boolean;
      Not_Supervised, Exit_Zero, Indeterminate : Boolean := False;
      Ready : Boolean := True;
      Capture_Required : Boolean := False;
      --  A stage is resolved from complete exact builtin facts OR the actual
      --  native-requested observation. Never cache two original getter/eq calls.
      procedure Stage
        (Name : String; Left : E.Span; Operator : String; Operand : String;
         Result : out Boolean; Key : String := ""; Kind_Lookup : Boolean := False)
      is
         Observation : constant E.Span := F (Capture, Name);
         Value : E.Span := F (Left, "value");
         Valid : Boolean;
         function Operand_Matches return Boolean is
            O : constant E.Span := F (Observation, "operand");
         begin
            return (if Operand = "0" then
              Form (O) = E.Integer_Value and then not B.Truth (Data, O)
              else T (O, Operand));
         end Operand_Matches;
      begin
         Result := False;
         if not Ready then return; end if;
         if Builtin (Left) and then not Kind_Lookup then
            Ready := Key = "" or else Form (Value) = E.Object_Value;
            Value := (if Ready and then Key /= "" then F (Value, Key) else Value);
            --  Preserve the original lazy branches, including bool/int/float
            --  comparison with zero and the two distinct getter observations.
            Result := Ready and then
              (if Operator = "get_truth" then B.Truth (Data, Value)
               elsif Operand = "0" then
                 Form (Value) in E.Boolean_Value | E.Integer_Value | E.Float_Value
                   and then not B.Truth (Data, Value)
               elsif Operator = "ne" or else Operator = "get_ne" then
                 not T (Value, Operand)
               else T (Value, Operand));
            return;
         end if;
         if not Foreign (Left) then Ready := False; return; end if;
         if Observation.Length = 0 then
            Capture_Required := True;
            Ready := False;
            return;
         end if;
         Valid := Form (Observation) = E.Object_Value and then
           T (F (Observation, "profile"), "python-actual-protocol-v1") and then
           T (F (Observation, "operation"), Operator) and then
           (if Operator = "getitem_is_none" then
              Builtin (F (Observation, "lookupValue")) or else
              Foreign (F (Observation, "lookupValue"))
            else Form (F (Observation, "returnedTruth")) = E.Boolean_Value) and then
           Reference (F (Observation, "returnedReference")) and then
           Reference (F (Observation, "returnedTypeReference")) and then
           Reference (F (Observation, "leftReference")) and then
           Reference (F (Observation, "leftTypeReference"));
         Valid := Valid and then
           (if Kind_Lookup then T (F (Left, "lookup"), "getitem") and then
              T (F (Left, "key"), "kind") and then
              T (F (Observation, "sourceOperation"), "getitem") and then
              T (F (Observation, "sourceKey"), "kind") and then
              B.Equal (Data, F (Observation, "sourceReference"), F (Left, "reference")) and then
              Reference (F (Observation, "sourceTypeReference"))
            else B.Equal (Data, F (Observation, "leftReference"), F (Left, "reference")));
         Valid := Valid and then (Key = "" or else T (F (Observation, "key"), Key));
         Valid := Valid and then
           (Operator = "get_truth" or else Operator = "getitem_is_none" or else
              Operand_Matches);
         Ready := Valid;
         Result := Valid and then
           (if Operator = "getitem_is_none" then
              Builtin (F (Observation, "lookupValue")) and then
                Form (F (F (Observation, "lookupValue"), "value")) = E.Null_Value
            else B.Is_True (Data, Observation, "returnedTruth"));
      end Stage;
      function Failure (Name : String) return String is
        (if Capture_Required then Need (Name) else Invalid);
      function Fired_JSON return String is
        (if Fired then "true" elsif Unknown then "null" else "false");
      function Evidence_Text return String is
        (if Evidence_Hit then "cgroup memory.events sampled during the run"
         elsif Evidence_Manager then "the service manager recorded Result=oom-kill"
         elsif Evidence_Unknown then "nothing was measured" else "no ceiling event was recorded");
      function Publication (Name, Key : String) return String is
         Observation : constant E.Span := F (Capture, Name);
         Operand : constant E.Span := F (Observation, "operand");
         Value : constant String := (if Key = "ceilingFired" then Fired_JSON
                                     else """" & Evidence_Text & """");
         Valid : Boolean;
      begin
         if Observation.Length = 0 then
            return "{""status"":""CAPTURE_REQUIRED"",""operation"":""" & Name &
              """,""value"":" & Value & "}";
         end if;
         Valid := Form (Observation) = E.Object_Value and then
           T (F (Observation, "profile"), "python-actual-protocol-v1") and then
           T (F (Observation, "operation"), "setitem") and then
           T (F (Observation, "key"), Key) and then
           B.Equal (Data, F (Observation, "leftReference"), F (Resource_Container, "reference")) and then
           Reference (F (Observation, "leftTypeReference"));
         if Key = "ceilingFired" then
            Valid := Valid and then
              (if Unknown and then not Fired then Form (Operand) = E.Null_Value
               else Form (Operand) = E.Boolean_Value and then
                 E.Decode (Data, Operand, E.Finalization).Boolean_Bit = Fired);
         else Valid := Valid and then T (Operand, Evidence_Text);
         end if;
         return (if Valid then "" else Invalid);
      end Publication;
      function Ceiling return String is
        ("""ceilingFired"":" & Fired_JSON & ",""ceilingEvidence"":""" & Evidence_Text & """");
      function Agent_Status return String is
        (if not Stopped and then not Not_Supervised and then Exit_Zero then "PASS" else "FAIL");
      function Prefix_Materialization return String is
         Observation : constant E.Span := F (Capture, "prepareAgentPrefix");
      begin
         if Observation.Length = 0 then
            if T (F (Capture, "mode"), "policy-only-v1") then return ""; end if;
            return Need ("prepareAgentPrefix");
         end if;
         if Form (Observation) /= E.Object_Value or else
           not T (F (Observation, "profile"), "python-actual-protocol-v1") or else
           not T (F (Observation, "operation"), "prefix-materialization") or else
           not Reference (F (Observation, "reference")) or else
           not Reference (F (Observation, "typeReference"))
         then return Invalid; end if;
         return "";
      end Prefix_Materialization;
      function Materialization return String is
         Observation : constant E.Span := F (Capture, "prepareAgentResult");
      begin
         if Observation.Length = 0 then
            if T (F (Capture, "mode"), "policy-only-v1") then return ""; end if;
            return "{""status"":""CAPTURE_REQUIRED"",""operation"":""prepareAgentResult"",""agentStatus"":""" &
              Agent_Status & """}";
         end if;
         if Form (Observation) /= E.Object_Value or else
           not T (F (Observation, "profile"), "python-actual-protocol-v1") or else
           not T (F (Observation, "operation"), "result-materialization") or else
           not Reference (F (Observation, "reference")) or else
           not Reference (F (Observation, "typeReference")) or else
           not T (F (Observation, "nativeStatus"), Agent_Status)
         then return Invalid; end if;
         return "";
      end Materialization;
   begin
      if Form (Capture) /= E.Object_Value or else
        not T (F (Capture, "schema"), "worldline.runner-terminal-v2") or else
        (not T (F (Capture, "mode"), "policy-only-v1") and then
         not T (F (Capture, "mode"), "runner-owner-v1")) or else
        not (Builtin (Resources) or else Foreign (Resources)) or else
        not Foreign (Resource_Container) or else
        not (Builtin (Manager) or else Foreign (Manager)) or else
        not Foreign (Kind) or else
        not T (F (Kind, "lookup"), "getitem") or else
        not T (F (Kind, "key"), "kind") or else
        not (Builtin (Exit_Code) or else Foreign (Exit_Code)) or else
        not B.Cancellation_Membership_Valid (Data, F (Membership, "cancelled")) or else
        not B.Cancellation_Membership_Valid (Data, F (Membership, "timedOut"))
      then return Invalid; end if;
      Cancelled := Worldline.Runner_Lifecycle.Cancellation_Membership (Data, F (Membership, "cancelled"));
      Timed_Out := Worldline.Runner_Lifecycle.Cancellation_Membership (Data, F (Membership, "timedOut"));
      Stopped := Cancelled or else Timed_Out;
      Stage ("ceilingHitLookup1", Resources, "get_truth", "", Fired, "hitMemoryCeiling");
      if not Ready then return Failure ("ceilingHitLookup1"); end if;
      if not Fired then
         Stage ("ceilingOomLookup1", Resources, "get_truth", "", Fired, "oomKilled");
         if not Ready then return Failure ("ceilingOomLookup1"); end if;
      end if;
      if not Fired then
         Stage ("managerOomComparison1", Manager, "eq", "oom-kill", Fired);
         if not Ready then return Failure ("managerOomComparison1"); end if;
      end if;
      if not Fired then
         Stage ("observedStateComparison", Resources, "get_ne", "OBSERVED", Unknown, "state");
         if not Ready then return Failure ("observedStateComparison"); end if;
         Unknown := Unknown and then Builtin (Manager) and then Form (F (Manager, "value")) = E.Null_Value;
      end if;
      declare Result : constant String := Publication ("publishCeilingFired", "ceilingFired"); begin
         if Result'Length > 0 then return Result; end if;
      end;
      Stage ("ceilingHitLookup2", Resources, "get_truth", "", Evidence_Hit, "hitMemoryCeiling");
      if not Ready then return Failure ("ceilingHitLookup2"); end if;
      if not Evidence_Hit then
         Stage ("managerOomComparison2", Manager, "eq", "oom-kill", Evidence_Manager);
         if not Ready then return Failure ("managerOomComparison2"); end if;
      end if;
      if not Evidence_Hit and then not Evidence_Manager then
         Stage ("ceilingEvidenceNoneLookup", Resource_Container, "getitem_is_none", "",
                Evidence_Unknown, "ceilingFired");
         if not Ready then return Failure ("ceilingEvidenceNoneLookup"); end if;
      end if;
      declare Result : constant String := Publication ("publishCeilingEvidence", "ceilingEvidence"); begin
         if Result'Length > 0 then return Result; end if;
      end;
      Stage ("launchComparison", Kind, "eq", "LAUNCH_FAILED", Launch_Failed, Kind_Lookup => True);
      if not Ready then return Failure ("launchComparison"); end if;
      if Launch_Failed then return "{""status"":""COMPLETE"",""launchFailed"":true," & Ceiling & "}"; end if;
      declare Result : constant String := Prefix_Materialization; begin
         if Result'Length > 0 then return Result; end if;
      end;
      if not Stopped then
         Stage ("supervisedComparison", Kind, "ne", "SUPERVISED", Not_Supervised, Kind_Lookup => True);
         if not Ready then return Failure ("supervisedComparison"); end if;
         if not Not_Supervised then
            Stage ("exitComparison", Exit_Code, "eq", "0", Exit_Zero);
            if not Ready then return Failure ("exitComparison"); end if;
         end if;
      end if;
      declare Result : constant String := Materialization; begin
         if Result'Length > 0 then return Result; end if;
      end;
      if not Cancelled and then not Timed_Out then
         Stage ("ceilingReasonLookup", Resource_Container, "get_truth", "", Reason_Ceiling, "ceilingFired");
         if not Ready then return Failure ("ceilingReasonLookup"); end if;
         if not Reason_Ceiling then
            Stage ("indeterminateComparison", Kind, "eq", "INDETERMINATE", Indeterminate, Kind_Lookup => True);
            if not Ready then return Failure ("indeterminateComparison"); end if;
         end if;
      end if;
      return "{""status"":""COMPLETE"",""launchFailed"":false,""stopped"":" & Bit (Stopped) &
        ",""agentStatus"":""" & Agent_Status &
        """," & Ceiling & ",""reason"":""" &
        (if Cancelled then "USER_CANCELLED" elsif Timed_Out then "TIMEOUT"
         elsif Reason_Ceiling then "RESOURCE_LIMIT_EXCEEDED" elsif Indeterminate then "SUPERVISION_INDETERMINATE"
         else "NONE") & """}";
   end Decide;
end Worldline.Runner_Outcome_Bytes;
