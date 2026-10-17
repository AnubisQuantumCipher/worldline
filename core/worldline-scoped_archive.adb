package body Worldline.Scoped_Archive with SPARK_Mode is
   use type E.Value_Kind;
   use type E.Q.Byte;
   function Pair (Data : E.Bytes; Item : E.View; Ordinal : E.Count) return E.View is
     (E.Decode (Data, E.Array_Element (Data, Item.Children, Ordinal), E.Finalization));
   function Key_Is (Data : E.Bytes; Item : E.View; Ordinal : E.Count; Name : String)
      return Boolean
   is
      P : constant E.View := Pair (Data, Item, Ordinal);
   begin
      return P.Form = E.List_Value and then E.Array_Length (Data, P.Children) = 2
        and then E.Text_Is (Data,
          E.Decode (Data, E.Array_Element (Data, P.Children, 0), E.Operation), Name);
   end Key_Is;
   function Pair_Value (Data : E.Bytes; Item : E.View; Ordinal : E.Count) return E.Span is
      P : constant E.View := Pair (Data, Item, Ordinal);
   begin
      if P.Form /= E.List_Value or else E.Array_Length (Data, P.Children) /= 2 then return (1, 0); end if;
      return E.Array_Element (Data, P.Children, 1);
   end Pair_Value;
   function Hex_Valid (Data : E.Bytes; Item : E.View) return Boolean is
   begin
      if Item.Form /= E.Text_Value then return False; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, Item.Payload);
      begin
         return Raw'Length mod 2 = 0 and then
           (for all B of Raw => B in Character'Pos ('0') .. Character'Pos ('9') or else
                                B in Character'Pos ('a') .. Character'Pos ('f'));
      end;
   end Hex_Valid;
   function Record_Fields (Data : E.Bytes; Type_Name : E.View; Fields : E.View) return Boolean is
   begin
      if E.Text_Is (Data, Type_Name, "ScopedState") then
         return E.Array_Length (Data, Fields.Children) = 6
           and then Key_Is (Data, Fields, 0, "current")
           and then Key_Is (Data, Fields, 1, "resource_epoch")
           and then Key_Is (Data, Fields, 2, "universe_head")
           and then Key_Is (Data, Fields, 3, "ledger_head")
           and then Key_Is (Data, Fields, 4, "history_head")
           and then Key_Is (Data, Fields, 5, "physical_head");
      end if;
      if E.Text_Is (Data, Type_Name, "ScopeFrame") then
         return E.Array_Length (Data, Fields.Children) = 15
           and then Key_Is (Data, Fields, 0, "scope")
           and then Key_Is (Data, Fields, 1, "first_epoch")
           and then Key_Is (Data, Fields, 2, "universe_head")
           and then Key_Is (Data, Fields, 3, "frame_head")
           and then Key_Is (Data, Fields, 4, "prior_frame")
           and then Key_Is (Data, Fields, 5, "store_genesis")
           and then Key_Is (Data, Fields, 6, "store_id")
           and then Key_Is (Data, Fields, 7, "root_head")
           and then Key_Is (Data, Fields, 8, "prime")
           and then Key_Is (Data, Fields, 9, "root_count")
           and then Key_Is (Data, Fields, 10, "cause")
           and then Key_Is (Data, Fields, 11, "requester")
           and then Key_Is (Data, Fields, 12, "receipt")
           and then Key_Is (Data, Fields, 13, "catalogue_head")
           and then Key_Is (Data, Fields, 14, "observation_head");
      end if;
      if E.Text_Is (Data, Type_Name, "PhysicalKey") then
         return E.Array_Length (Data, Fields.Children) = 3
           and then Key_Is (Data, Fields, 0, "machine")
           and then Key_Is (Data, Fields, 1, "resource")
           and then Key_Is (Data, Fields, 2, "unit");
      end if;
      if E.Text_Is (Data, Type_Name, "PhysicalBucket") then
         return E.Array_Length (Data, Fields.Children) = 7
           and then Key_Is (Data, Fields, 0, "key")
           and then Key_Is (Data, Fields, 1, "capacity")
           and then Key_Is (Data, Fields, 2, "held_total")
           and then Key_Is (Data, Fields, 3, "charged_total")
           and then Key_Is (Data, Fields, 4, "capacity_source")
           and then Key_Is (Data, Fields, 5, "catalogue_head")
           and then Key_Is (Data, Fields, 6, "observation_head");
      end if;
      if E.Text_Is (Data, Type_Name, "PhysicalProjection") then
         return E.Array_Length (Data, Fields.Children) = 7
           and then Key_Is (Data, Fields, 0, "key")
           and then Key_Is (Data, Fields, 1, "bound")
           and then Key_Is (Data, Fields, 2, "origin")
           and then Key_Is (Data, Fields, 3, "catalogue_head")
           and then Key_Is (Data, Fields, 4, "numerator")
           and then Key_Is (Data, Fields, 5, "denominator")
           and then Key_Is (Data, Fields, 6, "amount");
      end if;
      if E.Text_Is (Data, Type_Name, "CurrentObservation") then
         return E.Array_Length (Data, Fields.Children) = 16
           and then Key_Is (Data, Fields, 0, "scope")
           and then Key_Is (Data, Fields, 1, "resource_epoch")
           and then Key_Is (Data, Fields, 2, "universe_head")
           and then Key_Is (Data, Fields, 3, "ledger_head")
           and then Key_Is (Data, Fields, 4, "history_head")
           and then Key_Is (Data, Fields, 5, "physical_head")
           and then Key_Is (Data, Fields, 6, "store_genesis")
           and then Key_Is (Data, Fields, 7, "store_id")
           and then Key_Is (Data, Fields, 8, "root_head")
           and then Key_Is (Data, Fields, 9, "prime")
           and then Key_Is (Data, Fields, 10, "root_count")
           and then Key_Is (Data, Fields, 11, "cause")
           and then Key_Is (Data, Fields, 12, "requester")
           and then Key_Is (Data, Fields, 13, "receipt")
           and then Key_Is (Data, Fields, 14, "catalogue_head")
           and then Key_Is (Data, Fields, 15, "observation_head");
      end if;
      if E.Text_Is (Data, Type_Name, "ScopedIntent") then
         return E.Array_Length (Data, Fields.Children) = 8
           and then Key_Is (Data, Fields, 0, "kind")
           and then Key_Is (Data, Fields, 1, "original")
           and then Key_Is (Data, Fields, 2, "expected_epoch")
           and then Key_Is (Data, Fields, 3, "expected_ledger_head")
           and then Key_Is (Data, Fields, 4, "request_id")
           and then Key_Is (Data, Fields, 5, "cause")
           and then Key_Is (Data, Fields, 6, "requester")
           and then Key_Is (Data, Fields, 7, "receipt");
      end if;
      if E.Text_Is (Data, Type_Name, "ScopedPacket") then
         return E.Array_Length (Data, Fields.Children) = 15
           and then Key_Is (Data, Fields, 0, "before")
           and then Key_Is (Data, Fields, 1, "history")
           and then Key_Is (Data, Fields, 2, "rows")
           and then Key_Is (Data, Fields, 3, "projection")
           and then Key_Is (Data, Fields, 4, "buckets")
           and then Key_Is (Data, Fields, 5, "proposed")
           and then Key_Is (Data, Fields, 6, "proposed_history")
           and then Key_Is (Data, Fields, 7, "proposed_rows")
           and then Key_Is (Data, Fields, 8, "proposed_projection")
           and then Key_Is (Data, Fields, 9, "proposed_buckets")
           and then Key_Is (Data, Fields, 10, "actual_buckets")
           and then Key_Is (Data, Fields, 11, "observed")
           and then Key_Is (Data, Fields, 12, "facts")
           and then Key_Is (Data, Fields, 13, "current")
           and then Key_Is (Data, Fields, 14, "request");
      end if;
      if E.Text_Is (Data, Type_Name, "ScopedNativeDecision") then
         return E.Array_Length (Data, Fields.Children) = 7
           and then Key_Is (Data, Fields, 0, "entry_point")
           and then Key_Is (Data, Fields, 1, "status")
           and then Key_Is (Data, Fields, 2, "raw_input")
           and then Key_Is (Data, Fields, 3, "raw_arena")
           and then Key_Is (Data, Fields, 4, "raw_rosters")
           and then Key_Is (Data, Fields, 5, "raw_output")
           and then Key_Is (Data, Fields, 6, "transport_status");
      end if;
      if E.Text_Is (Data, Type_Name, "RunContext") then
         return E.Array_Length (Data, Fields.Children) = 9
           and then Key_Is (Data, Fields, 0, "universe")
           and then Key_Is (Data, Fields, 1, "policy")
           and then Key_Is (Data, Fields, 2, "resource")
           and then Key_Is (Data, Fields, 3, "unit")
           and then Key_Is (Data, Fields, 4, "instance")
           and then Key_Is (Data, Fields, 5, "host")
           and then Key_Is (Data, Fields, 6, "boot")
           and then Key_Is (Data, Fields, 7, "authority")
           and then Key_Is (Data, Fields, 8, "policy_epoch");
      end if;
      if E.Text_Is (Data, Type_Name, "RunBinding") then
         return E.Array_Length (Data, Fields.Children) = 10
           and then Key_Is (Data, Fields, 0, "reservation")
           and then Key_Is (Data, Fields, 1, "operation")
           and then Key_Is (Data, Fields, 2, "owner")
           and then Key_Is (Data, Fields, 3, "workload")
           and then Key_Is (Data, Fields, 4, "universe_head")
           and then Key_Is (Data, Fields, 5, "capability")
           and then Key_Is (Data, Fields, 6, "grant_use")
           and then Key_Is (Data, Fields, 7, "payload")
           and then Key_Is (Data, Fields, 8, "provenance")
           and then Key_Is (Data, Fields, 9, "resource_epoch");
      end if;
      if E.Text_Is (Data, Type_Name, "RunRow") then
         return E.Array_Length (Data, Fields.Children) = 11
           and then Key_Is (Data, Fields, 0, "scope")
           and then Key_Is (Data, Fields, 1, "bound")
           and then Key_Is (Data, Fields, 2, "parent")
           and then Key_Is (Data, Fields, 3, "kind")
           and then Key_Is (Data, Fields, 4, "state")
           and then Key_Is (Data, Fields, 5, "amount")
           and then Key_Is (Data, Fields, 6, "observed_usage")
           and then Key_Is (Data, Fields, 7, "planned_unit")
           and then Key_Is (Data, Fields, 8, "actual_unit")
           and then Key_Is (Data, Fields, 9, "cgroup")
           and then Key_Is (Data, Fields, 10, "invocation");
      end if;
      if E.Text_Is (Data, Type_Name, "RunState") then
         return E.Array_Length (Data, Fields.Children) = 7
           and then Key_Is (Data, Fields, 0, "scope")
           and then Key_Is (Data, Fields, 1, "resource_epoch")
           and then Key_Is (Data, Fields, 2, "universe_head")
           and then Key_Is (Data, Fields, 3, "ledger_head")
           and then Key_Is (Data, Fields, 4, "capacity")
           and then Key_Is (Data, Fields, 5, "held_total")
           and then Key_Is (Data, Fields, 6, "charged_total");
      end if;
      if E.Text_Is (Data, Type_Name, "RunObservation") then
         return E.Array_Length (Data, Fields.Children) = 8
           and then Key_Is (Data, Fields, 0, "scope")
           and then Key_Is (Data, Fields, 1, "resource_epoch")
           and then Key_Is (Data, Fields, 2, "bound")
           and then Key_Is (Data, Fields, 3, "actual_unit")
           and then Key_Is (Data, Fields, 4, "cgroup")
           and then Key_Is (Data, Fields, 5, "invocation")
           and then Key_Is (Data, Fields, 6, "observation_head")
           and then Key_Is (Data, Fields, 7, "observed");
      end if;
      if E.Text_Is (Data, Type_Name, "RunRequest") then
         return E.Array_Length (Data, Fields.Children) = 10
           and then Key_Is (Data, Fields, 0, "kind")
           and then Key_Is (Data, Fields, 1, "scope")
           and then Key_Is (Data, Fields, 2, "expected_epoch")
           and then Key_Is (Data, Fields, 3, "expected_ledger_head")
           and then Key_Is (Data, Fields, 4, "request_id")
           and then Key_Is (Data, Fields, 5, "reservation")
           and then Key_Is (Data, Fields, 6, "operation_id")
           and then Key_Is (Data, Fields, 7, "requester")
           and then Key_Is (Data, Fields, 8, "bound")
           and then Key_Is (Data, Fields, 9, "new_row");
      end if;
      if E.Text_Is (Data, Type_Name, "PhysicalFacts") then
         return E.Array_Length (Data, Fields.Children) = 39
           and then Key_Is (Data, Fields, 0, "current")
           and then Key_Is (Data, Fields, 1, "current_epoch")
           and then Key_Is (Data, Fields, 2, "retained")
           and then Key_Is (Data, Fields, 3, "current_universe_head")
           and then Key_Is (Data, Fields, 4, "current_ledger_head")
           and then Key_Is (Data, Fields, 5, "intent")
           and then Key_Is (Data, Fields, 6, "dispatch")
           and then Key_Is (Data, Fields, 7, "observation_head")
           and then Key_Is (Data, Fields, 8, "actual_unit")
           and then Key_Is (Data, Fields, 9, "cgroup")
           and then Key_Is (Data, Fields, 10, "invocation")
           and then Key_Is (Data, Fields, 11, "namespace")
           and then Key_Is (Data, Fields, 12, "held_namespace")
           and then Key_Is (Data, Fields, 13, "peer")
           and then Key_Is (Data, Fields, 14, "held_peer")
           and then Key_Is (Data, Fields, 15, "helper_image")
           and then Key_Is (Data, Fields, 16, "expected_helper_image")
           and then Key_Is (Data, Fields, 17, "challenge")
           and then Key_Is (Data, Fields, 18, "held_challenge")
           and then Key_Is (Data, Fields, 19, "protocol")
           and then Key_Is (Data, Fields, 20, "closed_event")
           and then Key_Is (Data, Fields, 21, "namespace_wait")
           and then Key_Is (Data, Fields, 22, "helper_wait")
           and then Key_Is (Data, Fields, 23, "cgroup_events")
           and then Key_Is (Data, Fields, 24, "cgroup_type")
           and then Key_Is (Data, Fields, 25, "manager_delegate")
           and then Key_Is (Data, Fields, 26, "cgroup_owner")
           and then Key_Is (Data, Fields, 27, "cgroup_group_write")
           and then Key_Is (Data, Fields, 28, "cgroup_other_write")
           and then Key_Is (Data, Fields, 29, "actual_store_genesis")
           and then Key_Is (Data, Fields, 30, "actual_store_id")
           and then Key_Is (Data, Fields, 31, "owner_store_genesis")
           and then Key_Is (Data, Fields, 32, "owner_store_id")
           and then Key_Is (Data, Fields, 33, "genesis_universe")
           and then Key_Is (Data, Fields, 34, "genesis_instance")
           and then Key_Is (Data, Fields, 35, "genesis_context_head")
           and then Key_Is (Data, Fields, 36, "genesis_prime")
           and then Key_Is (Data, Fields, 37, "genesis_root_count")
           and then Key_Is (Data, Fields, 38, "phase");
      end if;
      if E.Text_Is (Data, Type_Name, "ActorNativeObservation") then
         return E.Array_Length (Data, Fields.Children) = 70
           and then Key_Is (Data, Fields, 0, "bound")
           and then Key_Is (Data, Fields, 1, "raw_frame")
           and then Key_Is (Data, Fields, 2, "raw_sender")
           and then Key_Is (Data, Fields, 3, "ticket")
           and then Key_Is (Data, Fields, 4, "raw_proc_status")
           and then Key_Is (Data, Fields, 5, "raw_proc_cgroup")
           and then Key_Is (Data, Fields, 6, "raw_proc_maps")
           and then Key_Is (Data, Fields, 7, "raw_proc_cmdline")
           and then Key_Is (Data, Fields, 8, "raw_pidfd_info")
           and then Key_Is (Data, Fields, 9, "namespace")
           and then Key_Is (Data, Fields, 10, "held_namespace")
           and then Key_Is (Data, Fields, 11, "helper_image")
           and then Key_Is (Data, Fields, 12, "expected_helper_image")
           and then Key_Is (Data, Fields, 13, "executable_plan")
           and then Key_Is (Data, Fields, 14, "expected_executable_plan")
           and then Key_Is (Data, Fields, 15, "original_requester")
           and then Key_Is (Data, Fields, 16, "requester_credentials")
           and then Key_Is (Data, Fields, 17, "expected_requester_credentials")
           and then Key_Is (Data, Fields, 18, "dispatch")
           and then Key_Is (Data, Fields, 19, "running_event")
           and then Key_Is (Data, Fields, 20, "expected_running_event")
           and then Key_Is (Data, Fields, 21, "canonical_use_event")
           and then Key_Is (Data, Fields, 22, "expected_canonical_use_event")
           and then Key_Is (Data, Fields, 23, "store_genesis")
           and then Key_Is (Data, Fields, 24, "expected_store_genesis")
           and then Key_Is (Data, Fields, 25, "source_lease")
           and then Key_Is (Data, Fields, 26, "expected_source_lease")
           and then Key_Is (Data, Fields, 27, "actor_wait")
           and then Key_Is (Data, Fields, 28, "helper_wait")
           and then Key_Is (Data, Fields, 29, "namespace_wait")
           and then Key_Is (Data, Fields, 30, "host_pid")
           and then Key_Is (Data, Fields, 31, "namespace_pid")
           and then Key_Is (Data, Fields, 32, "sender_uid")
           and then Key_Is (Data, Fields, 33, "sender_gid")
           and then Key_Is (Data, Fields, 34, "real_uid")
           and then Key_Is (Data, Fields, 35, "effective_uid")
           and then Key_Is (Data, Fields, 36, "saved_uid")
           and then Key_Is (Data, Fields, 37, "real_gid")
           and then Key_Is (Data, Fields, 38, "effective_gid")
           and then Key_Is (Data, Fields, 39, "saved_gid")
           and then Key_Is (Data, Fields, 40, "capability_version")
           and then Key_Is (Data, Fields, 41, "effective_low")
           and then Key_Is (Data, Fields, 42, "permitted_low")
           and then Key_Is (Data, Fields, 43, "inheritable_low")
           and then Key_Is (Data, Fields, 44, "effective_high")
           and then Key_Is (Data, Fields, 45, "permitted_high")
           and then Key_Is (Data, Fields, 46, "inheritable_high")
           and then Key_Is (Data, Fields, 47, "securebits")
           and then Key_Is (Data, Fields, 48, "no_new_privs")
           and then Key_Is (Data, Fields, 49, "requester_uid")
           and then Key_Is (Data, Fields, 50, "requester_gid")
           and then Key_Is (Data, Fields, 51, "configured_requester_uid")
           and then Key_Is (Data, Fields, 52, "workload_uid")
           and then Key_Is (Data, Fields, 53, "workload_gid")
           and then Key_Is (Data, Fields, 54, "proc_host_pid")
           and then Key_Is (Data, Fields, 55, "proc_namespace_pid")
           and then Key_Is (Data, Fields, 56, "proc_real_uid")
           and then Key_Is (Data, Fields, 57, "proc_effective_uid")
           and then Key_Is (Data, Fields, 58, "proc_saved_uid")
           and then Key_Is (Data, Fields, 59, "proc_real_gid")
           and then Key_Is (Data, Fields, 60, "proc_effective_gid")
           and then Key_Is (Data, Fields, 61, "proc_saved_gid")
           and then Key_Is (Data, Fields, 62, "proc_effective")
           and then Key_Is (Data, Fields, 63, "proc_permitted")
           and then Key_Is (Data, Fields, 64, "proc_inheritable")
           and then Key_Is (Data, Fields, 65, "proc_bounding")
           and then Key_Is (Data, Fields, 66, "proc_ambient")
           and then Key_Is (Data, Fields, 67, "proc_no_new_privs")
           and then Key_Is (Data, Fields, 68, "proc_fs_uid")
           and then Key_Is (Data, Fields, 69, "proc_fs_gid");
      end if;
      if E.Text_Is (Data, Type_Name, "ActorCapability") then
         return E.Array_Length (Data, Fields.Children) = 3
           and then Key_Is (Data, Fields, 0, "index")
           and then Key_Is (Data, Fields, 1, "bounding")
           and then Key_Is (Data, Fields, 2, "ambient");
      end if;
      if E.Text_Is (Data, Type_Name, "ActorExecutionCrosswalk") then
         return E.Array_Length (Data, Fields.Children) = 15
           and then Key_Is (Data, Fields, 0, "resource_current")
           and then Key_Is (Data, Fields, 1, "operation_policy")
           and then Key_Is (Data, Fields, 2, "operation_root_set")
           and then Key_Is (Data, Fields, 3, "owner_genesis")
           and then Key_Is (Data, Fields, 4, "installation")
           and then Key_Is (Data, Fields, 5, "gate_config")
           and then Key_Is (Data, Fields, 6, "managed_observation")
           and then Key_Is (Data, Fields, 7, "original_grant")
           and then Key_Is (Data, Fields, 8, "complete_crosswalk")
           and then Key_Is (Data, Fields, 9, "current_source")
           and then Key_Is (Data, Fields, 10, "original_request")
           and then Key_Is (Data, Fields, 11, "original_requester")
           and then Key_Is (Data, Fields, 12, "original_transaction")
           and then Key_Is (Data, Fields, 13, "preparer")
           and then Key_Is (Data, Fields, 14, "selected_plan");
      end if;
      if E.Text_Is (Data, Type_Name, "ActorExecutionNativeDecision") then
         return E.Array_Length (Data, Fields.Children) = 11
           and then Key_Is (Data, Fields, 0, "entry_point")
           and then Key_Is (Data, Fields, 1, "status")
           and then Key_Is (Data, Fields, 2, "actor_input")
           and then Key_Is (Data, Fields, 3, "actor_arena")
           and then Key_Is (Data, Fields, 4, "actor_rosters")
           and then Key_Is (Data, Fields, 5, "crosswalk")
           and then Key_Is (Data, Fields, 6, "authority_input")
           and then Key_Is (Data, Fields, 7, "authority_arena")
           and then Key_Is (Data, Fields, 8, "authority_rosters")
           and then Key_Is (Data, Fields, 9, "raw_output")
           and then Key_Is (Data, Fields, 10, "transport_status");
      end if;
      if E.Text_Is (Data, Type_Name, "BoundUse") then
         return E.Array_Length (Data, Fields.Children) = 30
           and then Key_Is (Data, Fields, 0, "mode")
           and then Key_Is (Data, Fields, 1, "operation")
           and then Key_Is (Data, Fields, 2, "transaction")
           and then Key_Is (Data, Fields, 3, "capability")
           and then Key_Is (Data, Fields, 4, "universe_head")
           and then Key_Is (Data, Fields, 5, "instance")
           and then Key_Is (Data, Fields, 6, "subject")
           and then Key_Is (Data, Fields, 7, "staged_root")
           and then Key_Is (Data, Fields, 8, "current_requirement")
           and then Key_Is (Data, Fields, 9, "resulting_requirement")
           and then Key_Is (Data, Fields, 10, "requester")
           and then Key_Is (Data, Fields, 11, "grant_use")
           and then Key_Is (Data, Fields, 12, "policy_identity")
           and then Key_Is (Data, Fields, 13, "selected_evaluation")
           and then Key_Is (Data, Fields, 14, "history_head")
           and then Key_Is (Data, Fields, 15, "reservation")
           and then Key_Is (Data, Fields, 16, "host")
           and then Key_Is (Data, Fields, 17, "before_prime")
           and then Key_Is (Data, Fields, 18, "before_root")
           and then Key_Is (Data, Fields, 19, "before_mapping")
           and then Key_Is (Data, Fields, 20, "staged_mapping")
           and then Key_Is (Data, Fields, 21, "input_snapshot")
           and then Key_Is (Data, Fields, 22, "kernel_build")
           and then Key_Is (Data, Fields, 23, "kernel_library")
           and then Key_Is (Data, Fields, 24, "kernel_mapping")
           and then Key_Is (Data, Fields, 25, "issuer_head")
           and then Key_Is (Data, Fields, 26, "receipt_head")
           and then Key_Is (Data, Fields, 27, "causal_head")
           and then Key_Is (Data, Fields, 28, "policy_epoch")
           and then Key_Is (Data, Fields, 29, "resource_epoch");
      end if;
      if E.Text_Is (Data, Type_Name, "NativeObservation") then
         return E.Array_Length (Data, Fields.Children) = 2
           and then Key_Is (Data, Fields, 0, "live_mapping")
           and then Key_Is (Data, Fields, 1, "live_root");
      end if;
      if E.Text_Is (Data, Type_Name, "ProcessObservation") then
         return E.Array_Length (Data, Fields.Children) = 22
           and then Key_Is (Data, Fields, 0, "raw_status")
           and then Key_Is (Data, Fields, 1, "raw_stat")
           and then Key_Is (Data, Fields, 2, "raw_cgroup")
           and then Key_Is (Data, Fields, 3, "raw_maps")
           and then Key_Is (Data, Fields, 4, "raw_cmdline")
           and then Key_Is (Data, Fields, 5, "raw_pidfd_info")
           and then Key_Is (Data, Fields, 6, "namespace")
           and then Key_Is (Data, Fields, 7, "cgroup")
           and then Key_Is (Data, Fields, 8, "actual_unit")
           and then Key_Is (Data, Fields, 9, "invocation")
           and then Key_Is (Data, Fields, 10, "source_lease")
           and then Key_Is (Data, Fields, 11, "pidfd_wait")
           and then Key_Is (Data, Fields, 12, "host_pid")
           and then Key_Is (Data, Fields, 13, "start_tick")
           and then Key_Is (Data, Fields, 14, "parent_pid")
           and then Key_Is (Data, Fields, 15, "parent_start_tick")
           and then Key_Is (Data, Fields, 16, "real_uid")
           and then Key_Is (Data, Fields, 17, "effective_uid")
           and then Key_Is (Data, Fields, 18, "saved_uid")
           and then Key_Is (Data, Fields, 19, "real_gid")
           and then Key_Is (Data, Fields, 20, "effective_gid")
           and then Key_Is (Data, Fields, 21, "saved_gid");
      end if;
      if E.Text_Is (Data, Type_Name, "RootController") then
         return E.Array_Length (Data, Fields.Children) = 22
           and then Key_Is (Data, Fields, 0, "bound")
           and then Key_Is (Data, Fields, 1, "process")
           and then Key_Is (Data, Fields, 2, "requester_uid")
           and then Key_Is (Data, Fields, 3, "requester_gid")
           and then Key_Is (Data, Fields, 4, "raw_manager")
           and then Key_Is (Data, Fields, 5, "raw_channel")
           and then Key_Is (Data, Fields, 6, "owner_endpoint")
           and then Key_Is (Data, Fields, 7, "expected_owner_endpoint")
           and then Key_Is (Data, Fields, 8, "source_lease")
           and then Key_Is (Data, Fields, 9, "expected_source_lease")
           and then Key_Is (Data, Fields, 10, "worker_image")
           and then Key_Is (Data, Fields, 11, "expected_worker_image")
           and then Key_Is (Data, Fields, 12, "handler_plan")
           and then Key_Is (Data, Fields, 13, "expected_handler_plan")
           and then Key_Is (Data, Fields, 14, "raw_request")
           and then Key_Is (Data, Fields, 15, "requester")
           and then Key_Is (Data, Fields, 16, "dispatch")
           and then Key_Is (Data, Fields, 17, "running_event")
           and then Key_Is (Data, Fields, 18, "expected_running_event")
           and then Key_Is (Data, Fields, 19, "store_genesis")
           and then Key_Is (Data, Fields, 20, "expected_store_genesis")
           and then Key_Is (Data, Fields, 21, "current_source");
      end if;
      if E.Text_Is (Data, Type_Name, "TaskOrigin") then
         return E.Array_Length (Data, Fields.Children) = 33
           and then Key_Is (Data, Fields, 0, "action")
           and then Key_Is (Data, Fields, 1, "root")
           and then Key_Is (Data, Fields, 2, "child")
           and then Key_Is (Data, Fields, 3, "task_id")
           and then Key_Is (Data, Fields, 4, "root_world")
           and then Key_Is (Data, Fields, 5, "child_world")
           and then Key_Is (Data, Fields, 6, "root_instance")
           and then Key_Is (Data, Fields, 7, "child_instance")
           and then Key_Is (Data, Fields, 8, "world_store")
           and then Key_Is (Data, Fields, 9, "full_world_ancestry")
           and then Key_Is (Data, Fields, 10, "original_workload")
           and then Key_Is (Data, Fields, 11, "sandbox")
           and then Key_Is (Data, Fields, 12, "adapter")
           and then Key_Is (Data, Fields, 13, "context")
           and then Key_Is (Data, Fields, 14, "mission")
           and then Key_Is (Data, Fields, 15, "stdin")
           and then Key_Is (Data, Fields, 16, "credential_source")
           and then Key_Is (Data, Fields, 17, "executable_source")
           and then Key_Is (Data, Fields, 18, "configuration")
           and then Key_Is (Data, Fields, 19, "owner_plan")
           and then Key_Is (Data, Fields, 20, "native_cost_input")
           and then Key_Is (Data, Fields, 21, "raw_request")
           and then Key_Is (Data, Fields, 22, "requester")
           and then Key_Is (Data, Fields, 23, "cause")
           and then Key_Is (Data, Fields, 24, "root_dispatch")
           and then Key_Is (Data, Fields, 25, "root_running_event")
           and then Key_Is (Data, Fields, 26, "task_journal")
           and then Key_Is (Data, Fields, 27, "task_intent")
           and then Key_Is (Data, Fields, 28, "task_reservation_event")
           and then Key_Is (Data, Fields, 29, "task_launch_event")
           and then Key_Is (Data, Fields, 30, "parent_namespace_source")
           and then Key_Is (Data, Fields, 31, "fd_lineage")
           and then Key_Is (Data, Fields, 32, "source_lease");
      end if;
      if E.Text_Is (Data, Type_Name, "NamespaceObservation") then
         return E.Array_Length (Data, Fields.Children) = 5
           and then Key_Is (Data, Fields, 0, "identity")
           and then Key_Is (Data, Fields, 1, "parent")
           and then Key_Is (Data, Fields, 2, "raw_nsfs")
           and then Key_Is (Data, Fields, 3, "raw_get_parent")
           and then Key_Is (Data, Fields, 4, "source_lease");
      end if;
      if E.Text_Is (Data, Type_Name, "ResourceChildNativeObservation") then
         return E.Array_Length (Data, Fields.Children) = 13
           and then Key_Is (Data, Fields, 0, "entry_point")
           and then Key_Is (Data, Fields, 1, "mode")
           and then Key_Is (Data, Fields, 2, "status")
           and then Key_Is (Data, Fields, 3, "actor_input")
           and then Key_Is (Data, Fields, 4, "resource_arena")
           and then Key_Is (Data, Fields, 5, "resource_rosters")
           and then Key_Is (Data, Fields, 6, "authority_input")
           and then Key_Is (Data, Fields, 7, "authority_arena")
           and then Key_Is (Data, Fields, 8, "authority_rosters")
           and then Key_Is (Data, Fields, 9, "crosswalk")
           and then Key_Is (Data, Fields, 10, "child_input")
           and then Key_Is (Data, Fields, 11, "raw_output")
           and then Key_Is (Data, Fields, 12, "transport_status");
      end if;
      return False;
   end Record_Fields;

   function Valid (Data : E.Bytes; Encoded : E.Span) return Boolean is
      Item : constant E.View := E.Decode (Data, Encoded, E.Operation);
      Type_Name, Payload : E.View;
      Payload_Span, Child : E.Span;
      N : E.Count;
      Sequence : Boolean := False;
   begin
      if not A.Valid (Data, Encoded) or else Item.Form /= E.Object_Value or else
        not Key_Is (Data, Item, 0, "type") then return False; end if;
      Type_Name := E.Decode (Data, Pair_Value (Data, Item, 0), E.Operation);
      if Type_Name.Form /= E.Text_Value then return False; end if;
      if E.Text_Is (Data, Type_Name, "integer") then
         if E.Array_Length (Data, Item.Children) /= 3 or else
           not Key_Is (Data, Item, 1, "negative") or else
           not Key_Is (Data, Item, 2, "magnitude") then return False; end if;
         declare
            Sign : constant E.View := E.Decode (Data, Pair_Value (Data, Item, 1), E.Operation);
            Mag : constant E.View := E.Decode (Data, Pair_Value (Data, Item, 2), E.Operation);
         begin
            if Sign.Form /= E.Boolean_Value or else not Hex_Valid (Data, Mag) then return False; end if;
            declare
               Raw : constant E.Bytes := E.Materialize (Data, Mag.Payload);
            begin
               -- Original record(restore(...)) removes leading magnitude zero
               -- bytes and negative zero, so the enclosing root codec rejects.
               return (if Raw'Length = 0 then not Sign.Boolean_Bit
                       else Raw (Raw'Last) /= Character'Pos ('0') or else
                            Raw (Raw'Last - 1) /= Character'Pos ('0'));
            end;
         end;
      end if;
      if E.Array_Length (Data, Item.Children) /= 2 then return False; end if;
      Payload_Span := Pair_Value (Data, Item, 1);
      Payload := E.Decode (Data, Payload_Span, E.Operation);
      if E.Text_Is (Data, Type_Name, "bytes") then
         return Key_Is (Data, Item, 1, "value") and then Hex_Valid (Data, Payload);
      elsif E.Text_Is (Data, Type_Name, "float") then
         if not Key_Is (Data, Item, 1, "bits") or else not Hex_Valid (Data, Payload) then return False; end if;
         return E.Materialize (Data, Payload.Payload)'Length / 2 = 8;
      elsif E.Text_Is (Data, Type_Name, "str") then
         return Key_Is (Data, Item, 1, "value") and then Payload.Form = E.Text_Value;
      elsif E.Text_Is (Data, Type_Name, "bool") then
         return Key_Is (Data, Item, 1, "value") and then Payload.Form = E.Boolean_Value;
      elsif E.Text_Is (Data, Type_Name, "NoneType") then
         return Key_Is (Data, Item, 1, "value") and then Payload.Form = E.Null_Value;
      elsif E.Text_Is (Data, Type_Name, "list") or else E.Text_Is (Data, Type_Name, "tuple") then
         if not Key_Is (Data, Item, 1, "items") or else Payload.Form /= E.List_Value then return False; end if;
         Sequence := True;
      else
         if not Key_Is (Data, Item, 1, "fields") or else Payload.Form /= E.Object_Value then return False; end if;
         if not E.Text_Is (Data, Type_Name, "dict") and then
           not Record_Fields (Data, Type_Name, Payload) then return False; end if;
      end if;
      N := E.Array_Length (Data, Payload.Children);
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            if Sequence then Child := E.Array_Element (Data, Payload.Children, I);
            else
               declare
                  P : constant E.View := Pair (Data, Payload, I);
                  Key : constant E.View := E.Decode
                    (Data, E.Array_Element (Data, P.Children, 0), E.Operation);
               begin
                  if Key.Form /= E.Text_Value then return False; end if;
                  Child := Pair_Value (Data, Payload, I);
               end;
            end if;
            if Child.Length = 0 or else Child.Length >= Encoded.Length or else
              not Valid (Data, Child) then return False; end if;
         end loop;
      end if;
      return True;
   end Valid;

   function Field (Data : E.Bytes; Encoded : E.Span; Name : String) return E.Span is
      Item : constant E.View := E.Decode (Data, Encoded, E.Operation);
      Type_Name : constant E.View := E.Decode (Data, Pair_Value (Data, Item, 0), E.Operation);
   begin
      if not Valid (Data, Encoded) or else not E.Text_Is (Data, Type_Name, "dict") then return (1, 0); end if;
      return A.Field (Data, Pair_Value (Data, Item, 1), Name);
   end Field;
   function Text_Is (Data : E.Bytes; Encoded : E.Span; Text : String) return Boolean is
      Item : constant E.View := E.Decode (Data, Encoded, E.Operation);
      Type_Name : constant E.View := E.Decode (Data, Pair_Value (Data, Item, 0), E.Operation);
   begin
      return Valid (Data, Encoded) and then E.Text_Is (Data, Type_Name, "str") and then
        E.Text_Is (Data, E.Decode (Data, Pair_Value (Data, Item, 1), E.Operation), Text);
   end Text_Is;
   function Text_Matches (Data : E.Bytes; Encoded, Expected : E.Span) return Boolean is
      Item : constant E.View := E.Decode (Data, Encoded, E.Operation);
      Type_Name : constant E.View := E.Decode (Data, Pair_Value (Data, Item, 0), E.Operation);
      Value : constant E.View := E.Decode (Data, Pair_Value (Data, Item, 1), E.Operation);
   begin
      if not Valid (Data, Encoded) or else not E.Text_Is (Data, Type_Name, "str") or else
        Value.Form /= E.Text_Value or else not E.C.P.Valid (Data, Expected) then return False; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, Value.Payload);
      begin
         return Raw'Length = Expected.Length and then
           (for all I in Raw'Range => Raw (I) = Data (Expected.First + (I - Raw'First)));
      end;
   end Text_Matches;
   function Member_Count (Data : E.Bytes; Encoded : E.Span) return E.Count is
      Item : constant E.View := E.Decode (Data, Encoded, E.Operation);
      Type_Name : constant E.View := E.Decode (Data, Pair_Value (Data, Item, 0), E.Operation);
      Fields : constant E.View := E.Decode (Data, Pair_Value (Data, Item, 1), E.Operation);
   begin
      if not Valid (Data, Encoded) or else not E.Text_Is (Data, Type_Name, "dict") then return 0; end if;
      return E.Array_Length (Data, Fields.Children);
   end Member_Count;
   function Member_Name_Is
     (Data : E.Bytes; Encoded : E.Span; Ordinal : E.Count; Name : String)
      return Boolean
   is
      Item : constant E.View := E.Decode (Data, Encoded, E.Operation);
      Type_Name : constant E.View := E.Decode (Data, Pair_Value (Data, Item, 0), E.Operation);
      Fields : constant E.View := E.Decode (Data, Pair_Value (Data, Item, 1), E.Operation);
   begin
      return Valid (Data, Encoded) and then E.Text_Is (Data, Type_Name, "dict") and then
        Key_Is (Data, Fields, Ordinal, Name);
   end Member_Name_Is;
end Worldline.Scoped_Archive;
