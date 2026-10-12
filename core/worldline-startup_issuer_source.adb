with Interfaces;
with Attest;
with Worldline.Producer_Values;
with Worldline.Raw_JSON;
with Worldline.Custody_V2_Domain_Hmac;
with Cosmogony.Genesis;
with Cosmogony.Capabilities;
with Cosmogony.Universes;
with Cosmogony.Revocable_Capabilities;
package body Worldline.Startup_Issuer_Source with SPARK_Mode is
   package V renames L.V;
   package S renames V.S;
   package P renames Worldline.Producer_Values;
   package J renames Worldline.Raw_JSON;
   package H renames Worldline.Custody_V2_Domain_Hmac;
   package G renames Cosmogony.Genesis;
   package C renames Cosmogony.Capabilities;
   package U renames Cosmogony.Universes;
   package R renames Cosmogony.Revocable_Capabilities;
   subtype U64 is Interfaces.Unsigned_64;
   subtype U32 is Interfaces.Unsigned_32;
   use type U64;
   use type Interfaces.Unsigned_8;
   use type E.Count;
   use type E.Bytes;
   use type P.Value_Kind;
   use type G.Digest;
   use type C.Check_Reason;
   Zero : constant String (1 .. 64) := (others => '0');
   Authority : constant String := "LOCAL_ROOT_ANCHORED_CAPABILITY_VALUE_ONLY";
   function F (D : E.Bytes; X : E.Span; Name : String) return E.Span renames S.Field;
   function Text (B : E.Bytes) return String is
      Result : String (1 .. Natural (B'Length));
   begin
      for I in Result'Range loop Result (I) := Character'Val (B (B'First + E.Count (I - 1))); end loop;
      return Result;
   end Text;
   function Bytes (T : String) return E.Bytes is
      Result : E.Bytes (1 .. E.Count (T'Length)) with Relaxed_Initialization;
   begin
      for I in T'Range loop
         pragma Loop_Invariant (for all K in E.Count range 1 .. E.Count (I - T'First) => Result (K)'Initialized);
         Result (1 + E.Count (I - T'First)) := Character'Pos (T (I));
      end loop;
      return Result;
   end Bytes;
   function Word (D : E.Bytes; X : E.Span) return String is
     (if V.Valid_Text (D, X) then Text (V.Text_Value (D, X)) else "");
   function Raw (D : E.Bytes; X : E.Span) return E.Bytes is
     (if V.Valid_Bytes (D, X) then V.Bytes_Value (D, X) else E.Bytes'(1 .. 0 => 0));
   function PF (D : String; X : P.Node; Name : String) return P.Node renames P.Field;
   -- Exact keys, not merely the presence of a favorable subset.
   function Keys (D : String; X : P.Node; Names : String; Count : Natural) return Boolean is
      Start : Positive := Names'First;
   begin
      if X.Form /= P.Object_Value or else P.Count (D, X) /= Count then return False; end if;
      for I in Names'Range loop
         if Names (I) = ',' then
            if not P.Present (PF (D, X, Names (Start .. I - 1))) then return False; end if;
            Start := I + 1;
         end if;
      end loop;
      return P.Present (PF (D, X, Names (Start .. Names'Last)));
   end Keys;
   function Number (D : String; X : P.Node) return U64 is
      Result : U64 := 0;
      T : constant String := P.Slice (D, X);
   begin
      if X.Form /= P.Integer_Value or else T'Length = 0 then return 0; end if;
      for Ch of T loop
         if Ch not in '0' .. '9' or else Result > (U64'Last - U64 (Character'Pos (Ch) - 48)) / 10 then return 0; end if;
         Result := Result * 10 + U64 (Character'Pos (Ch) - 48);
      end loop;
      return Result;
   end Number;
   function Integer_Valid (D : String; X : P.Node; Maximum : U64 := U64'Last) return Boolean is
      Result : U64 := 0;
      T : constant String := P.Slice (D, X);
   begin
      if X.Form /= P.Integer_Value or else T'Length = 0 then return False; end if;
      if T = "-0" then return True; end if;
      for Ch of T loop
         if Ch not in '0' .. '9' or else Result > (U64'Last - U64 (Character'Pos (Ch) - 48)) / 10 then return False; end if;
         Result := Result * 10 + U64 (Character'Pos (Ch) - 48);
      end loop;
      return Result <= Maximum;
   end Integer_Valid;
   function Hex (T : String) return Boolean is
     (T'Length = 64 and then (for all Ch of T => Ch in '0' .. '9' | 'a' .. 'f'));
   function Digest_Valid (D : String; X : P.Node) return Boolean is
     (X.Form = P.String_Value and then Hex (P.Text (D, X)));
   function Nibble (Ch : Character) return U64 is
     (if Ch in '0' .. '9' then U64 (Character'Pos (Ch) - 48) else U64 (Character'Pos (Ch) - 87));
   function Digest (D : String; X : P.Node) return G.Digest is
      T : constant String := P.Text (D, X);
      Result : G.Digest := G.Zero_Digest;
   begin
      if not Hex (T) then return Result; end if;
      for I in 0 .. 31 loop
         Result (I / 8 + 1) := Result (I / 8 + 1) +
           (Nibble (T (T'First + I * 2)) * 16 + Nibble (T (T'First + I * 2 + 1))) * 2 ** (8 * (I mod 8));
      end loop;
      return Result;
   end Digest;
   function Digests (D : String; X : P.Node; Names : String) return Boolean is
      Start : Positive := Names'First;
   begin
      for I in Names'Range loop
         if Names (I) = ',' then
            if not Digest_Valid (D, PF (D, X, Names (Start .. I - 1))) then return False; end if;
            Start := I + 1;
         end if;
      end loop;
      return Digest_Valid (D, PF (D, X, Names (Start .. Names'Last)));
   end Digests;
   function Action_Name (A : G.Operation) return String is
     (case A is when G.Observe => "observe", when G.Propose => "propose",
       when G.Create_World => "create_world", when G.Evaluate_World => "evaluate_world",
       when G.Request_Promotion => "request_promotion", when G.Authorize_Promotion => "authorize_promotion",
       when G.Mutate_Prime => "mutate_prime", when G.Mint_Authority => "mint_authority");
   function Role_Name (A : G.Agent_Role) return String is
     (case A is when G.Builder => "builder", when G.Adversary => "adversary",
       when G.Reviewer => "reviewer", when G.Synthesizer => "synthesizer",
       when G.Held_Out_Evaluator => "held_out_evaluator", when G.Observer => "observer");
   function Life_Name (A : U.Lifecycle_State) return String is
     (case A is when U.Genesis => "genesis", when U.Active => "active",
       when U.Suspended => "suspended", when U.Sealed => "sealed", when U.Archived => "archived");
   function Action_Valid (D : String; X : P.Node) return Boolean is
     (for some A in G.Operation => P.Is_Text (D, X, Action_Name (A)));
   function Counter_Valid (D : String; X : P.Node; Maximum : U64) return Boolean is
     (Keys (D, X, "worlds,evaluations", 2) and then
      Integer_Valid (D, PF (D, X, "worlds"), Maximum) and then
      Integer_Valid (D, PF (D, X, "evaluations"), Maximum));
   function Capability_Valid (D : String; X : P.Node) return Boolean is
      Actions : constant P.Node := PF (D, X, "granted");
      Scope : constant P.Node := PF (D, X, "applies_to");
   begin
      if not Keys (D, X, "capability_id,parent_id,universe_id,mission_id,policy_id,authority_id,worldline_instance_id,root_set_id,prime_id,subject_id,issuer_id,policy_epoch,issued_at,expires_at,terminal,granted,applies_to,ceiling", 18) or else
         not Digests (D, X, "capability_id,parent_id,universe_id,mission_id,policy_id,authority_id,worldline_instance_id,root_set_id,prime_id,subject_id,issuer_id") or else
         not Integer_Valid (D, PF (D, X, "policy_epoch")) or else
         not Integer_Valid (D, PF (D, X, "issued_at")) or else
         not Integer_Valid (D, PF (D, X, "expires_at")) or else
         PF (D, X, "terminal").Form /= P.Boolean_Value or else Actions.Form /= P.Array_Value or else
         not Keys (D, Scope, "kind,world_id", 2) or else
         not (P.Is_Text (D, PF (D, Scope, "kind"), "universe") or else P.Is_Text (D, PF (D, Scope, "kind"), "world")) or else
         not Digest_Valid (D, PF (D, Scope, "world_id")) or else
         not Counter_Valid (D, PF (D, X, "ceiling"), U64 (U32'Last)) then return False; end if;
      for I in 1 .. P.Count (D, Actions) loop
         if not Action_Valid (D, P.Element (D, Actions, I)) then return False; end if;
         for K in 1 .. I - 1 loop
            if P.Equal (D, P.Element (D, Actions, I), D, P.Element (D, Actions, K)) then return False; end if;
         end loop;
      end loop;
      return True;
   end Capability_Valid;
   function Capability (D : String; X : P.Node) return C.Capability is
      Result : C.Capability := C.Null_Capability;
      Actions : constant P.Node := PF (D, X, "granted");
      Scope : constant P.Node := PF (D, X, "applies_to");
      Ceiling : constant P.Node := PF (D, X, "ceiling");
   begin
      Result.Capability_Id := Digest (D, PF (D, X, "capability_id"));
      Result.Parent_Id := Digest (D, PF (D, X, "parent_id"));
      Result.Universe_Id := Digest (D, PF (D, X, "universe_id"));
      Result.Mission_Id := Digest (D, PF (D, X, "mission_id"));
      Result.Policy_Id := Digest (D, PF (D, X, "policy_id"));
      Result.Authority_Id := Digest (D, PF (D, X, "authority_id"));
      Result.Worldline_Instance_Id := Digest (D, PF (D, X, "worldline_instance_id"));
      Result.Root_Set_Id := Digest (D, PF (D, X, "root_set_id"));
      Result.Prime_Id := Digest (D, PF (D, X, "prime_id"));
      Result.Subject_Id := Digest (D, PF (D, X, "subject_id"));
      Result.Issuer_Id := Digest (D, PF (D, X, "issuer_id"));
      Result.Policy_Epoch := Number (D, PF (D, X, "policy_epoch"));
      Result.Issued_At := Number (D, PF (D, X, "issued_at"));
      Result.Expires_At := Number (D, PF (D, X, "expires_at"));
      Result.Terminal := P.Is_True (D, PF (D, X, "terminal"));
      for I in 1 .. P.Count (D, Actions) loop
         for A in G.Operation loop
            if P.Is_Text (D, P.Element (D, Actions, I), Action_Name (A)) then Result.Granted (A) := True; end if;
         end loop;
      end loop;
      Result.Applies_To := (Kind => (if P.Is_Text (D, PF (D, Scope, "kind"), "universe") then C.Universe_Scope else C.World_Scope), World_Id => Digest (D, PF (D, Scope, "world_id")));
      Result.Ceiling := (Worlds => U32 (Number (D, PF (D, Ceiling, "worlds"))), Evaluations => U32 (Number (D, PF (D, Ceiling, "evaluations"))));
      return Result;
   end Capability;
   function Genesis_Valid (D : String; X : P.Node) return Boolean is
      Budget : constant P.Node := PF (D, X, "budget");
      Agents : constant P.Node := PF (D, X, "agents");
   begin
      if not Keys (D, X, "universe_id,mission_id,policy_id,policy_owner_mission,worldline_instance_id,root_set_id,prime_id,policy_epoch,budget,agents", 10) or else
         not Digests (D, X, "universe_id,mission_id,policy_id,policy_owner_mission,worldline_instance_id,root_set_id,prime_id") or else
         not Integer_Valid (D, PF (D, X, "policy_epoch")) or else
         not Keys (D, Budget, "world_limit,worlds_reserved,evaluation_limit,evaluations_reserved", 4) or else
         not Integer_Valid (D, PF (D, Budget, "world_limit"), U64 (U32'Last)) or else
         not Integer_Valid (D, PF (D, Budget, "worlds_reserved"), U64 (U32'Last)) or else
         not Integer_Valid (D, PF (D, Budget, "evaluation_limit"), U64 (U32'Last)) or else
         not Integer_Valid (D, PF (D, Budget, "evaluations_reserved"), U64 (U32'Last)) or else
         Agents.Form /= P.Array_Value or else P.Count (D, Agents) > 8 then return False; end if;
      for I in 1 .. P.Count (D, Agents) loop
         declare A : constant P.Node := P.Element (D, Agents, I); begin
            if not Keys (D, A, "identity,role", 2) or else not Digest_Valid (D, PF (D, A, "identity")) or else
               not (for some Role in G.Agent_Role => P.Is_Text (D, PF (D, A, "role"), Role_Name (Role))) then return False; end if;
         end;
      end loop;
      return True;
   end Genesis_Valid;
   function Genesis (D : String; X : P.Node) return G.Universe_State is
      Agents : constant P.Node := PF (D, X, "agents");
      Budget : constant P.Node := PF (D, X, "budget");
      Result : G.Universe_State;
   begin
      Result.Universe_Id := Digest (D, PF (D, X, "universe_id"));
      Result.Mission_Id := Digest (D, PF (D, X, "mission_id"));
      Result.Policy_Id := Digest (D, PF (D, X, "policy_id"));
      Result.Policy_Owner_Mission := Digest (D, PF (D, X, "policy_owner_mission"));
      Result.Worldline_Instance_Id := Digest (D, PF (D, X, "worldline_instance_id"));
      Result.Root_Set_Id := Digest (D, PF (D, X, "root_set_id"));
      Result.Prime_Id := Digest (D, PF (D, X, "prime_id"));
      Result.Policy_Epoch := Number (D, PF (D, X, "policy_epoch"));
      Result.Budget := (World_Limit => U32 (Number (D, PF (D, Budget, "world_limit"))), Worlds_Reserved => U32 (Number (D, PF (D, Budget, "worlds_reserved"))), Evaluation_Limit => U32 (Number (D, PF (D, Budget, "evaluation_limit"))), Evaluations_Reserved => U32 (Number (D, PF (D, Budget, "evaluations_reserved"))));
      Result.Roster_Count := G.Agent_Count (P.Count (D, Agents));
      Result.Roster := (others => (Identity => G.Zero_Digest, Role => G.Builder, Enabled => False));
      for I in 1 .. P.Count (D, Agents) loop
         declare A : constant P.Node := P.Element (D, Agents, I); begin
            Result.Roster (G.Agent_Index (I)).Identity := Digest (D, PF (D, A, "identity"));
            Result.Roster (G.Agent_Index (I)).Enabled := True;
            for Role in G.Agent_Role loop
               if P.Is_Text (D, PF (D, A, "role"), Role_Name (Role)) then Result.Roster (G.Agent_Index (I)).Role := Role; end if;
            end loop;
         end;
      end loop;
      return Result;
   end Genesis;
   function Record_Valid (D : String; X : P.Node) return Boolean is
      Policy : constant P.Node := PF (D, X, "policy");
   begin
      return Keys (D, X, "universe_id,parent_id,policy_epoch,policy,prime_worldline_id,prime_id,prime_generation,receipt_head_id,life,running_worlds,outstanding_reservations,unresolved_transactions,evidence_snapshot_id,snapshot_complete", 14) and then
        Digests (D, X, "universe_id,parent_id,prime_worldline_id,prime_id,receipt_head_id,evidence_snapshot_id") and then
        Keys (D, Policy, "mission_id,authority_id,resource_id,network_id,provider_id,evaluator_id,root_set_id,evidence_id,roster_id,worldline_set_id", 10) and then
        Digests (D, Policy, "mission_id,authority_id,resource_id,network_id,provider_id,evaluator_id,root_set_id,evidence_id,roster_id,worldline_set_id") and then
        Integer_Valid (D, PF (D, X, "policy_epoch")) and then Integer_Valid (D, PF (D, X, "prime_generation")) and then
        Integer_Valid (D, PF (D, X, "running_worlds"), U64 (U32'Last)) and then
        Integer_Valid (D, PF (D, X, "outstanding_reservations"), U64 (U32'Last)) and then
        Integer_Valid (D, PF (D, X, "unresolved_transactions"), U64 (U32'Last)) and then
        PF (D, X, "snapshot_complete").Form = P.Boolean_Value and then
        (for some Life in U.Lifecycle_State => P.Is_Text (D, PF (D, X, "life"), Life_Name (Life)));
   end Record_Valid;
   function Universe_Record (D : String; X : P.Node) return U.Universe_Record is
      Policy : constant P.Node := PF (D, X, "policy");
      Result : U.Universe_Record;
   begin
      Result.Universe_Id := Digest (D, PF (D, X, "universe_id"));
      Result.Parent_Id := Digest (D, PF (D, X, "parent_id"));
      Result.Policy_Epoch := Number (D, PF (D, X, "policy_epoch"));
      Result.Policy := (Mission_Id => Digest (D, PF (D, Policy, "mission_id")), Authority_Id => Digest (D, PF (D, Policy, "authority_id")), Resource_Id => Digest (D, PF (D, Policy, "resource_id")), Network_Id => Digest (D, PF (D, Policy, "network_id")), Provider_Id => Digest (D, PF (D, Policy, "provider_id")), Evaluator_Id => Digest (D, PF (D, Policy, "evaluator_id")), Root_Set_Id => Digest (D, PF (D, Policy, "root_set_id")), Evidence_Id => Digest (D, PF (D, Policy, "evidence_id")), Roster_Id => Digest (D, PF (D, Policy, "roster_id")), Worldline_Set_Id => Digest (D, PF (D, Policy, "worldline_set_id")));
      Result.Prime_Worldline_Id := Digest (D, PF (D, X, "prime_worldline_id"));
      Result.Prime_Id := Digest (D, PF (D, X, "prime_id"));
      Result.Prime_Generation := Number (D, PF (D, X, "prime_generation"));
      Result.Receipt_Head_Id := Digest (D, PF (D, X, "receipt_head_id"));
      Result.Life := U.Genesis;
      for Life in U.Lifecycle_State loop
         if P.Is_Text (D, PF (D, X, "life"), Life_Name (Life)) then Result.Life := Life; end if;
      end loop;
      Result.Running_Worlds := U32 (Number (D, PF (D, X, "running_worlds")));
      Result.Outstanding_Reservations := U32 (Number (D, PF (D, X, "outstanding_reservations")));
      Result.Unresolved_Transactions := U32 (Number (D, PF (D, X, "unresolved_transactions")));
      Result.Evidence_Snapshot_Id := Digest (D, PF (D, X, "evidence_snapshot_id"));
      Result.Snapshot_Complete := P.Is_True (D, PF (D, X, "snapshot_complete"));
      return Result;
   end Universe_Record;
   function Hex_Image (Sum : H.SHA.Digest) return String is
      Hex_Characters : constant String := "0123456789abcdef";
      Result : String (1 .. 64) := (others => '0');
   begin
      for I in Sum'Range loop
         Result (1 + (I - Sum'First) * 2) := Hex_Characters (Integer (Sum (I) / 16) + 1);
         Result (2 + (I - Sum'First) * 2) := Hex_Characters (Integer (Sum (I) mod 16) + 1);
      end loop;
      return Result;
   end Hex_Image;
   function Hash (B : E.Bytes) return String is
      Context : H.SHA.Context := H.SHA.Initial;
   begin
      for Byte of B loop H.SHA.Update (Context, Attest.Byte_Array'(0 => Byte)); end loop;
      return Hex_Image (H.SHA.Final (Context));
   end Hash;
   function Event_Hash (Previous, Event_JSON : String) return String is
      Context : H.SHA.Context := H.SHA.Initial;
      Domain : constant String := "COSMOGONY-CAPABILITY-EVENT-v1" & Character'Val (0);
   begin
      for Ch of Domain loop H.SHA.Update (Context, Attest.Byte_Array'(0 => Character'Pos (Ch))); end loop;
      for I in 0 .. 31 loop H.SHA.Update (Context, Attest.Byte_Array'(0 => Attest.Byte (Nibble (Previous (Previous'First + I * 2)) * 16 + Nibble (Previous (Previous'First + I * 2 + 1))))); end loop;
      for Ch of Event_JSON loop H.SHA.Update (Context, Attest.Byte_Array'(0 => Character'Pos (Ch))); end loop;
      return Hex_Image (H.SHA.Final (Context));
   end Event_Hash;
   function Canonical (D : String) return Boolean is
     (J.Canonical_ASCII_Valid (D) and then P.Parse (D).Last = D'Length);
   function Selected_Path (D : E.Bytes; Paths : E.Span; Name : String) return E.Span is
      Result : E.Span := (1, 0);
   begin
      for I in E.Count range 1 .. V.Count (D, Paths) loop
         declare Item : constant E.Span := V.Element (D, Paths, I - 1); begin
            if Word (D, F (D, Item, "path")) = Name then
               if Result.Length /= 0 then return (1, 0); end if;
               Result := Item;
            end if;
         end;
      end loop;
      return Result;
   end Selected_Path;
   function Events_Table (D : E.Bytes; DB : E.Span) return E.Span is
      Tables : constant E.Span := F (D, DB, "tables");
      Result : E.Span := (1, 0);
   begin
      for I in E.Count range 1 .. V.Count (D, Tables) loop
         declare T : constant E.Span := V.Element (D, Tables, I - 1); begin
            if S.Text_Is (D, F (D, T, "name"), "events") then
               if Result.Length /= 0 then return (1, 0); end if;
               Result := T;
            end if;
         end;
      end loop;
      return Result;
   end Events_Table;
   function Replay (D : E.Bytes; Rows : E.Span; Sequence : U64; Head : String) return Boolean is
      type Grant_Array is array (E.Count range <>) of C.Capability;
      Grants : Grant_Array (1 .. V.Count (D, Rows)) := (others => C.Null_Capability);
      Revoked : array (E.Count range 1 .. V.Count (D, Rows)) of Boolean := (others => False);
      Grant_Count : E.Count := 0;
      Uses : array (E.Count range 1 .. V.Count (D, Rows)) of G.Digest := (others => G.Zero_Digest);
      Use_Count : E.Count := 0;
      Previous : String (1 .. 64) := Zero;
      function Find (Identity : G.Digest) return E.Count is
      begin
         for I in E.Count range 1 .. Grant_Count loop
            if Grants (I).Capability_Id = Identity then return I; end if;
         end loop;
         return 0;
      end Find;
   begin
      if not V.Is_Sequence (D, Rows) or else Sequence /= U64 (V.Count (D, Rows)) or else not Hex (Head) then return False; end if;
      for Position in E.Count range 1 .. V.Count (D, Rows) loop
         declare Row : constant E.Span := V.Element (D, Rows, Position - 1);
                 Seq : constant V.Count_Result := V.Nonnegative_Count (D, V.Element (D, Row, 1));
                 Event_JSON : constant String := Word (D, V.Element (D, Row, 3));
                 Root : constant P.Node := P.Parse (Event_JSON);
                 Kind : constant P.Node := PF (Event_JSON, Root, "kind");
                 Stored : constant String := Word (D, V.Element (D, Row, 4)); begin
            -- Roster SQL rows retain rowid before the complete four original cells.
            if not V.Is_Sequence (D, Row) or else V.Count (D, Row) /= 5 or else
               not Seq.Present or else Seq.Value /= Position - 1 or else
               not V.Valid_Text (D, V.Element (D, Row, 2)) or else
               Word (D, V.Element (D, Row, 2)) /= Previous or else
               not V.Valid_Text (D, V.Element (D, Row, 3)) or else
               Event_JSON'Length > 1024 * 1024 or else not Canonical (Event_JSON) or else
               not V.Valid_Text (D, V.Element (D, Row, 4)) or else Stored /= Event_Hash (Previous, Event_JSON) then return False; end if;
            if P.Is_Text (Event_JSON, Kind, "grant") then
               declare Grant_Node : constant P.Node := PF (Event_JSON, Root, "grant");
                       Validation : constant P.Node := PF (Event_JSON, Root, "validation");
                       Record_Node : constant P.Node := PF (Event_JSON, Validation, "record");
                       Genesis_Node : constant P.Node := PF (Event_JSON, Validation, "genesis_universe");
                       Links : R.Lineage := (others => (Grant => C.Null_Capability, Revoked => False));
                       Count : R.Link_Count := 0;
                       Index, Parent : E.Count;
               begin
                  if not Keys (Event_JSON, Root, "kind,grant,validation", 3) or else
                     not Keys (Event_JSON, Validation, "record,genesis_universe,now_tick", 3) or else
                     not Record_Valid (Event_JSON, Record_Node) or else not Genesis_Valid (Event_JSON, Genesis_Node) or else
                     not Integer_Valid (Event_JSON, PF (Event_JSON, Validation, "now_tick")) or else
                     not Capability_Valid (Event_JSON, Grant_Node) then return False; end if;
                  declare Grant : constant C.Capability := Capability (Event_JSON, Grant_Node); begin
                     if Grant.Capability_Id = G.Zero_Digest or else Find (Grant.Capability_Id) /= 0 then return False; end if;
                     Parent := Find (Grant.Parent_Id);
                     if Grant.Parent_Id /= G.Zero_Digest and then (Parent = 0 or else Revoked (Parent)) then return False; end if;
                     Grant_Count := Grant_Count + 1;
                     Grants (Grant_Count) := Grant;
                     Index := Grant_Count;
                     while Index /= 0 loop
                        pragma Loop_Variant (Increases => Count);
                        if Count = 8 then return False; end if;
                        Count := Count + 1;
                        Links (Count) := (Grant => Grants (Index), Revoked => Revoked (Index));
                        if Grants (Index).Parent_Id = G.Zero_Digest then Index := 0;
                        else Index := Find (Grants (Index).Parent_Id); if Index = 0 then return False; end if; end if;
                     end loop;
                     for I in 1 .. Count / 2 loop
                        declare Temporary : constant R.Link := Links (I); begin Links (I) := Links (Count - I + 1); Links (Count - I + 1) := Temporary; end;
                     end loop;
                     declare State : constant G.Universe_State := Genesis (Event_JSON, Genesis_Node);
                             Record_Value : constant U.Universe_Record := Universe_Record (Event_JSON, Record_Node);
                             Ask : constant C.Scoped_Request :=
                               (Ask => (Request_Id => Grant.Capability_Id, Universe_Id => State.Universe_Id,
                                Mission_Id => State.Mission_Id, Policy_Id => State.Policy_Id,
                                Worldline_Instance_Id => State.Worldline_Instance_Id, Root_Set_Id => State.Root_Set_Id,
                                Prime_Id => State.Prime_Id, Policy_Epoch => State.Policy_Epoch,
                                Actor_Id => Grant.Subject_Id, Action => G.Observe), Target_World_Id => G.Zero_Digest);
                             Decision : constant C.Check_Decision := R.Check_Request
                               (Record_Value, State, Links, Count, Ask, (Worlds => 0, Evaluations => 0), Number (Event_JSON, PF (Event_JSON, Validation, "now_tick"))); begin
                        -- The original replay rejects these four reasons only;
                        -- an observe right refusal is NOT a malformed lineage.
                        if Decision.Reason in C.Invalid_Universe_State | C.Stale_Lifecycle_Epoch | C.Revoked_Ancestry | C.Invalid_Ancestry then return False; end if;
                     end;
                  end;
               end;
            elsif P.Is_Text (Event_JSON, Kind, "revoke") then
               if not Keys (Event_JSON, Root, "kind,capability_id,policy_epoch", 3) or else
                  not Digest_Valid (Event_JSON, PF (Event_JSON, Root, "capability_id")) or else
                  not Integer_Valid (Event_JSON, PF (Event_JSON, Root, "policy_epoch")) then return False; end if;
               declare Index : constant E.Count := Find (Digest (Event_JSON, PF (Event_JSON, Root, "capability_id"))); begin
                  if Index = 0 or else Revoked (Index) or else Number (Event_JSON, PF (Event_JSON, Root, "policy_epoch")) /= Grants (Index).Policy_Epoch then return False; end if;
                  Revoked (Index) := True;
               end;
            elsif P.Is_Text (Event_JSON, Kind, "use") then
               if not Keys (Event_JSON, Root, "kind,capability_id,operation_id,transaction_id,action,universe_head,policy_epoch,grant_state", 8) or else
                  not Digests (Event_JSON, Root, "capability_id,operation_id,universe_head") or else
                  not Integer_Valid (Event_JSON, PF (Event_JSON, Root, "policy_epoch")) or else
                  not P.Nonempty_Text (Event_JSON, PF (Event_JSON, Root, "transaction_id")) or else
                  not Action_Valid (Event_JSON, PF (Event_JSON, Root, "action")) then return False; end if;
               declare Index : constant E.Count := Find (Digest (Event_JSON, PF (Event_JSON, Root, "capability_id"))); begin
                  if Index = 0 or else Number (Event_JSON, PF (Event_JSON, Root, "policy_epoch")) /= Grants (Index).Policy_Epoch or else
                     not P.Is_Text (Event_JSON, PF (Event_JSON, Root, "grant_state"), (if Revoked (Index) then "REVOKED" else "CURRENT")) then return False; end if;
                  for A in G.Operation loop
                     if P.Is_Text (Event_JSON, PF (Event_JSON, Root, "action"), Action_Name (A)) and then not Grants (Index).Granted (A) then return False; end if;
                  end loop;
                  declare Operation_Id : constant G.Digest := Digest (Event_JSON, PF (Event_JSON, Root, "operation_id")); begin
                     for Earlier in E.Count range 1 .. Use_Count loop
                        if Uses (Earlier) = Operation_Id then return False; end if;
                     end loop;
                     Use_Count := Use_Count + 1;
                     Uses (Use_Count) := Operation_Id;
                  end;
               end;
            else return False;
            end if;
            Previous := Stored;
         end;
      end loop;
      return Previous = Head;
   end Replay;
   function Corresponds (Data : E.Bytes; Roster, Profile : E.Span) return Boolean is
      Current : constant E.Span := F (Data, Roster, "current");
      Paths : constant E.Span := F (Data, Current, "paths");
      Spec : constant E.Span := F (Data, Current, "installation");
      Root_Path : constant String := Word (Data, F (Data, F (Data, Spec, "paths"), "authority_root"));
      State_Path : constant String := Root_Path & "/authority/issuer/state/";
      Key_Field : constant E.Span := F (Data, Selected_Path (Data, Paths, State_Path & "issuer-key.bin"), "raw");
      Policy_Field : constant E.Span := F (Data, Selected_Path (Data, Paths, State_Path & "policy.json"), "raw");
      Head_Field : constant E.Span := F (Data, Selected_Path (Data, Paths, State_Path & "head.json"), "raw");
      Table : constant E.Span := Events_Table (Data, F (Data, Selected_Path (Data, Paths, State_Path & "capabilities.sqlite"), "logical_database"));
      Intent : constant E.Span := F (Data, Profile, "issuer_intent");
      Temporaries : constant E.Span := F (Data, Profile, "issuer_head_temporaries");
      Projected : constant E.Span := F (Data, Profile, "issuer_head");
      Projection_Field : constant E.Span := F (Data, Profile, "issuer_head_raw");
   begin
      if Data'Length > E.Count (Natural'Last) or else Root_Path'Length = 0 or else
         not V.Is_Sequence (Data, Paths) or else not V.Valid_Bytes (Data, Key_Field) or else
         not V.Valid_Bytes (Data, Policy_Field) or else not V.Valid_Bytes (Data, Head_Field) or else
         not V.Valid_Bytes (Data, Projection_Field) or else
         Word (Data, F (Data, Intent, "path")) /= State_Path & "intent.json" or else
         not S.Text_Is (Data, F (Data, Intent, "presence"), "ABSENT") or else
         not V.Is_Sequence (Data, Temporaries) or else V.Count (Data, Temporaries) /= 0 or else Table.Length = 0 then return False; end if;
      declare Key : constant E.Bytes := Raw (Data, Key_Field);
              Policy_Bytes : constant E.Bytes := Raw (Data, Policy_Field);
              Head_Bytes : constant E.Bytes := Raw (Data, Head_Field);
              Policy : constant String := Text (Policy_Bytes);
              Head : constant String := Text (Head_Bytes);
              Policy_Node : constant P.Node := P.Parse (Policy);
              Head_Node : constant P.Node := P.Parse (Head);
              Grant_Node : constant P.Node := PF (Policy, Policy_Node, "root_grant");
              Record_Node : constant P.Node := PF (Policy, Policy_Node, "record");
              Seq_Node : constant P.Node := PF (Head, Head_Node, "sequence");
              Event_Node : constant P.Node := PF (Head, Head_Node, "event_head");
              Schema_Node : constant P.Node := PF (Head, Head_Node, "schema");
              Hash_Node : constant P.Node := PF (Head, Head_Node, "policy_sha256");
              Mac_Node : constant P.Node := PF (Head, Head_Node, "mac");
              Columns : constant E.Span := F (Data, Table, "columns"); begin
         if Key'Length /= 32 or else Policy_Bytes'Length > 1024 * 1024 or else Head_Bytes'Length > 4096 or else
            (for some B of Policy_Bytes => B > 127) or else (for some B of Head_Bytes => B > 127) or else
            not Canonical (Policy) or else not P.Original_Exact_JSON (Head) or else
            not Keys (Policy, Policy_Node, "record,genesis_universe,root_grant,issuer_id,now_tick,usage", 6) or else
            not Record_Valid (Policy, Record_Node) or else
            not Genesis_Valid (Policy, PF (Policy, Policy_Node, "genesis_universe")) or else
            not Capability_Valid (Policy, Grant_Node) or else
            not Digest_Valid (Policy, PF (Policy, Policy_Node, "issuer_id")) or else
            not Integer_Valid (Policy, PF (Policy, Policy_Node, "now_tick")) or else
            not Counter_Valid (Policy, PF (Policy, Policy_Node, "usage"), U64'Last) or else
            not Keys (Head, Head_Node, "schema,sequence,event_head,policy_sha256,mac", 5) or else
            not (P.Is_True (Head, Schema_Node) or else
              (Schema_Node.Form = P.Integer_Value and then Integer_Valid (Head, Schema_Node) and then Number (Head, Schema_Node) = 1)) or else
            not Integer_Valid (Head, Seq_Node) or else not Digest_Valid (Head, Event_Node) or else
            not Digest_Valid (Head, Hash_Node) or else not Digest_Valid (Head, Mac_Node) or else
            P.Text (Head, Hash_Node) /= Hash (Policy_Bytes) or else
            not V.Is_Sequence (Data, Columns) or else V.Count (Data, Columns) /= 4 then return False; end if;
         for I in E.Count range 0 .. 3 loop
            if not S.Text_Is (Data, V.Element (Data, V.Element (Data, Columns, I), 1),
              (case I is when 0 => "seq", when 1 => "previous_hash", when 2 => "body_json", when others => "event_hash")) then return False; end if;
         end loop;
         declare Grant : constant C.Capability := Capability (Policy, Grant_Node);
                 Issuer : constant G.Digest := Digest (Policy, PF (Policy, Policy_Node, "issuer_id"));
                 Record_Value : constant U.Universe_Record := Universe_Record (Policy, Record_Node); begin
            if Issuer /= Record_Value.Policy.Authority_Id or else Issuer /= Grant.Issuer_Id or else
               Issuer /= Grant.Authority_Id or else Grant.Parent_Id /= G.Zero_Digest then return False; end if;
         end;
         declare Schema : constant String := (if Schema_Node.Form = P.Boolean_Value then "true" else P.Number_Image (Head, Schema_Node));
                 Base : constant E.Bytes := Bytes
                   ("{""event_head"":" & J.Canonical_ASCII_Quote (P.Text (Head, Event_Node)) &
                    ",""policy_sha256"":" & J.Canonical_ASCII_Quote (P.Text (Head, Hash_Node)) &
                    ",""schema"":" & Schema & ",""sequence"":" & P.Number_Image (Head, Seq_Node) & "}");
                 Projected_JSON : constant E.Bytes := Bytes
                   ("{""authority"":" & J.Canonical_ASCII_Quote (Authority) &
                    ",""event_head"":" & J.Canonical_ASCII_Quote (P.Text (Head, Event_Node)) &
                    ",""head_mac"":" & J.Canonical_ASCII_Quote (P.Text (Head, Mac_Node)) &
                    ",""sequence"":" & P.Number_Image (Head, Seq_Node) & "}");
                 Captured : constant E.Bytes := Raw (Data, Projection_Field); begin
            return P.Text (Head, Mac_Node) = Hex_Image (H.Mac (Key, Base, (Key'First, Key'Length), (Base'First, Base'Length), "COSMOGONY-PROTECTED-ISSUER-HEAD-v1" & Character'Val (0))) and then
              Captured = Projected_JSON and then
              S.Member_Count (Data, Projected) = 4 and then
              V.Is_Integer (Data, F (Data, Projected, "sequence")) and then
              V.Valid_Text (Data, F (Data, Projected, "event_head")) and then
              V.Valid_Text (Data, F (Data, Projected, "head_mac")) and then
              V.Valid_Text (Data, F (Data, Projected, "authority")) and then
              J.Raw_JSON_Scoped_Equal (Projected_JSON, Data, (Projected_JSON'First, Projected_JSON'Length), Projected) and then
              Replay (Data, F (Data, Table, "rows"), Number (Head, Seq_Node), P.Text (Head, Event_Node));
         end;
      end;
   end Corresponds;
end Worldline.Startup_Issuer_Source;
