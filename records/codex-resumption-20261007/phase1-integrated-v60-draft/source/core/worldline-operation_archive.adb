with System;
with Worldline.Evaluation_Wire;
package body Worldline.Operation_Archive with SPARK_Mode is
   use type E.Value_Kind;
   use type E.Bytes;
   use type E.Q.Byte;

   function Payload_Is
     (Data : E.Bytes; Item : E.Byte_View; Text : String) return Boolean is
   begin
      if not E.Bytes_Valid (Data, Item) then return False; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, Item);
      begin
         return Raw'Length = Text'Length and then
           (for all I in Text'Range =>
              Raw (Raw'First + E.Count (I - Text'First)) = Character'Pos (Text (I)));
      end;
   end Payload_Is;

   function Pair (Data : E.Bytes; Item : E.View; Ordinal : E.Count) return E.View is
     (E.Decode (Data, E.Array_Element (Data, Item.Children, Ordinal), E.Finalization));

   function Pair_Value (Data : E.Bytes; Item : E.View; Ordinal : E.Count)
      return E.Span
   is
      P : constant E.View := Pair (Data, Item, Ordinal);
   begin
      if P.Form /= E.List_Value or else E.Array_Length (Data, P.Children) /= 2 then
         return (1, 0);
      end if;
      return E.Array_Element (Data, P.Children, 1);
   end Pair_Value;

   function Field_Name
     (Data : E.Bytes; Item : E.View; Ordinal : E.Count; Name : String)
      return Boolean
   is
      P : constant E.View := Pair (Data, Item, Ordinal);
   begin
      return P.Form = E.List_Value and then E.Array_Length (Data, P.Children) = 2
        and then E.Text_Is (Data,
          E.Decode (Data, E.Array_Element (Data, P.Children, 0), E.Finalization), Name);
   end Field_Name;

   function Owned_Record_Constructor (Data : E.Bytes; Item : E.View) return Boolean is
      Raw_Field : constant E.View := E.Decode (Data, Pair_Value (Data, Item, 0), Item.At_Layer);
      Conf_Field : constant E.View := E.Decode (Data, Pair_Value (Data, Item, 1), Item.At_Layer);
   begin
      --  Only the original Python constructor conditions, not the downstream
      --  native raw-report classifier. Invalid report enum bytes still archive.
      if Raw_Field.Form /= E.Bytes_Value or else Conf_Field.Form /= E.Integer_Value
        or else Conf_Field.Sign then return False; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, Raw_Field.Payload);
         Conf : constant E.Bytes := E.Materialize (Data, Conf_Field.Payload);
      begin
         return Raw'Length = Worldline.Evaluation_Wire.Raw_Record'Size / System.Storage_Unit
           and then (Conf'Length = 0 or else
             (Conf'Length = 1 and then Conf (Conf'First) in 1 .. 2));
      end;
   end Owned_Record_Constructor;
   function Record_Fields (Data : E.Bytes; Item : E.View) return Boolean is
   begin
      if Item.Form /= E.Record_Value then return False; end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.core") and then
        Payload_Is (Data, Item.Record_Name, "CollapseInput") then
         return E.Array_Length (Data, Item.Children) = 35
           and then Field_Name (Data, Item, 0, "candidate_state")
           and then Field_Name (Data, Item, 1, "phase")
           and then Field_Name (Data, Item, 2, "mode")
           and then Field_Name (Data, Item, 3, "conflicts")
           and then Field_Name (Data, Item, 4, "foreign_writes")
           and then Field_Name (Data, Item, 5, "roster_complete")
           and then Field_Name (Data, Item, 6, "staged_roster_complete")
           and then Field_Name (Data, Item, 7, "expected_parent")
           and then Field_Name (Data, Item, 8, "candidate_parent")
           and then Field_Name (Data, Item, 9, "expected_subject")
           and then Field_Name (Data, Item, 10, "evidence_subject")
           and then Field_Name (Data, Item, 11, "expected_base")
           and then Field_Name (Data, Item, 12, "candidate_base")
           and then Field_Name (Data, Item, 13, "expected_delta")
           and then Field_Name (Data, Item, 14, "candidate_delta")
           and then Field_Name (Data, Item, 15, "expected_root_set")
           and then Field_Name (Data, Item, 16, "candidate_root_set")
           and then Field_Name (Data, Item, 17, "expected_staged_root")
           and then Field_Name (Data, Item, 18, "actual_staged_root")
           and then Field_Name (Data, Item, 19, "staged_content_root")
           and then Field_Name (Data, Item, 20, "tested_root")
           and then Field_Name (Data, Item, 21, "current_requirement")
           and then Field_Name (Data, Item, 22, "resulting_requirement")
           and then Field_Name (Data, Item, 23, "evaluated_requirement")
           and then Field_Name (Data, Item, 24, "declared_verifiers")
           and then Field_Name (Data, Item, 25, "executed_verifiers")
           and then Field_Name (Data, Item, 26, "staged_evaluated_requirement")
           and then Field_Name (Data, Item, 27, "staged_executed_verifiers")
           and then Field_Name (Data, Item, 28, "staged_examined_root")
           and then Field_Name (Data, Item, 29, "expected_checkpoint")
           and then Field_Name (Data, Item, 30, "witnessed_checkpoint")
           and then Field_Name (Data, Item, 31, "registered_watch_set")
           and then Field_Name (Data, Item, 32, "watched_set")
           and then Field_Name (Data, Item, 33, "generation_before")
           and then Field_Name (Data, Item, 34, "generation_after");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.evaluation_wire") and then
        Payload_Is (Data, Item.Record_Name, "OwnedRecord") then
         return E.Array_Length (Data, Item.Children) = 2
           and then Field_Name (Data, Item, 0, "raw")
           and then Field_Name (Data, Item, 1, "confinement")
           and then Owned_Record_Constructor (Data, Item);
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.completion_kernel") and then
        Payload_Is (Data, Item.Record_Name, "BoundValue") then
         return E.Array_Length (Data, Item.Children) = 6
           and then Field_Name (Data, Item, 0, "store_id")
           and then Field_Name (Data, Item, 1, "subject")
           and then Field_Name (Data, Item, 2, "content")
           and then Field_Name (Data, Item, 3, "run")
           and then Field_Name (Data, Item, 4, "epoch")
           and then Field_Name (Data, Item, 5, "requirement");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.completion_kernel") and then
        Payload_Is (Data, Item.Record_Name, "CaptureValue") then
         return E.Array_Length (Data, Item.Children) = 5
           and then Field_Name (Data, Item, 0, "bound")
           and then Field_Name (Data, Item, 1, "source")
           and then Field_Name (Data, Item, 2, "context")
           and then Field_Name (Data, Item, 3, "state")
           and then Field_Name (Data, Item, 4, "outcome");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.completion_kernel") and then
        Payload_Is (Data, Item.Record_Name, "CheckValue") then
         return E.Array_Length (Data, Item.Children) = 12
           and then Field_Name (Data, Item, 0, "bound")
           and then Field_Name (Data, Item, 1, "check")
           and then Field_Name (Data, Item, 2, "source")
           and then Field_Name (Data, Item, 3, "execution")
           and then Field_Name (Data, Item, 4, "verifier")
           and then Field_Name (Data, Item, 5, "state")
           and then Field_Name (Data, Item, 6, "outcome")
           and then Field_Name (Data, Item, 7, "payload")
           and then Field_Name (Data, Item, 8, "observations")
           and then Field_Name (Data, Item, 9, "report")
           and then Field_Name (Data, Item, 10, "evidence")
           and then Field_Name (Data, Item, 11, "declared");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.completion_kernel") and then
        Payload_Is (Data, Item.Record_Name, "HistoryValue") then
         return E.Array_Length (Data, Item.Children) = 7
           and then Field_Name (Data, Item, 0, "subject")
           and then Field_Name (Data, Item, 1, "content")
           and then Field_Name (Data, Item, 2, "requirement")
           and then Field_Name (Data, Item, 3, "run")
           and then Field_Name (Data, Item, 4, "epoch")
           and then Field_Name (Data, Item, 5, "state")
           and then Field_Name (Data, Item, 6, "outcome");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.pending_kernel_v2") and then
        Payload_Is (Data, Item.Record_Name, "Intent") then
         return E.Array_Length (Data, Item.Children) = 8
           and then Field_Name (Data, Item, 0, "store_id")
           and then Field_Name (Data, Item, 1, "subject")
           and then Field_Name (Data, Item, 2, "content")
           and then Field_Name (Data, Item, 3, "run")
           and then Field_Name (Data, Item, 4, "epoch")
           and then Field_Name (Data, Item, 5, "previous")
           and then Field_Name (Data, Item, 6, "linked")
           and then Field_Name (Data, Item, 7, "requirement");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.finalization_values") and then
        Payload_Is (Data, Item.Record_Name, "StartValue") then
         return E.Array_Length (Data, Item.Children) = 13
           and then Field_Name (Data, Item, 0, "store_id")
           and then Field_Name (Data, Item, 1, "subject")
           and then Field_Name (Data, Item, 2, "run")
           and then Field_Name (Data, Item, 3, "epoch")
           and then Field_Name (Data, Item, 4, "requirement")
           and then Field_Name (Data, Item, 5, "policy")
           and then Field_Name (Data, Item, 6, "verifier_plan")
           and then Field_Name (Data, Item, 7, "base_context")
           and then Field_Name (Data, Item, 8, "parent")
           and then Field_Name (Data, Item, 9, "config")
           and then Field_Name (Data, Item, 10, "repository")
           and then Field_Name (Data, Item, 11, "required")
           and then Field_Name (Data, Item, 12, "declaration");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.finalization_values") and then
        Payload_Is (Data, Item.Record_Name, "InputValue") then
         return E.Array_Length (Data, Item.Children) = 6
           and then Field_Name (Data, Item, 0, "start")
           and then Field_Name (Data, Item, 1, "root")
           and then Field_Name (Data, Item, 2, "manifests")
           and then Field_Name (Data, Item, 3, "filesystem")
           and then Field_Name (Data, Item, 4, "config")
           and then Field_Name (Data, Item, 5, "repository");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.finalization_values") and then
        Payload_Is (Data, Item.Record_Name, "UnsealedResult") then
         return E.Array_Length (Data, Item.Children) = 10
           and then Field_Name (Data, Item, 0, "start")
           and then Field_Name (Data, Item, 1, "check")
           and then Field_Name (Data, Item, 2, "source")
           and then Field_Name (Data, Item, 3, "execution")
           and then Field_Name (Data, Item, 4, "verifier")
           and then Field_Name (Data, Item, 5, "state")
           and then Field_Name (Data, Item, 6, "outcome")
           and then Field_Name (Data, Item, 7, "payload")
           and then Field_Name (Data, Item, 8, "declared")
           and then Field_Name (Data, Item, 9, "wire");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.finalization_values") and then
        Payload_Is (Data, Item.Record_Name, "CaptureValue") then
         return E.Array_Length (Data, Item.Children) = 8
           and then Field_Name (Data, Item, 0, "start")
           and then Field_Name (Data, Item, 1, "input")
           and then Field_Name (Data, Item, 2, "post_root")
           and then Field_Name (Data, Item, 3, "post_manifests")
           and then Field_Name (Data, Item, 4, "context")
           and then Field_Name (Data, Item, 5, "source")
           and then Field_Name (Data, Item, 6, "results")
           and then Field_Name (Data, Item, 7, "completion");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.finalization_values") and then
        Payload_Is (Data, Item.Record_Name, "ComponentsValue") then
         return E.Array_Length (Data, Item.Children) = 2
           and then Field_Name (Data, Item, 0, "environment")
           and then Field_Name (Data, Item, 1, "evidence");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.finalization_values") and then
        Payload_Is (Data, Item.Record_Name, "SealValue") then
         return E.Array_Length (Data, Item.Children) = 5
           and then Field_Name (Data, Item, 0, "capture")
           and then Field_Name (Data, Item, 1, "content")
           and then Field_Name (Data, Item, 2, "components")
           and then Field_Name (Data, Item, 3, "evidence")
           and then Field_Name (Data, Item, 4, "environment");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.finalization_values") and then
        Payload_Is (Data, Item.Record_Name, "ClassifiedValue") then
         return E.Array_Length (Data, Item.Children) = 3
           and then Field_Name (Data, Item, 0, "state")
           and then Field_Name (Data, Item, 1, "outcome")
           and then Field_Name (Data, Item, 2, "promotion");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.finalization_values") and then
        Payload_Is (Data, Item.Record_Name, "SealedValue") then
         return E.Array_Length (Data, Item.Children) = 5
           and then Field_Name (Data, Item, 0, "value")
           and then Field_Name (Data, Item, 1, "identity")
           and then Field_Name (Data, Item, 2, "classification")
           and then Field_Name (Data, Item, 3, "finalization_state")
           and then Field_Name (Data, Item, 4, "finalization_outcome");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.model") and then
        Payload_Is (Data, Item.Record_Name, "World") then
         return E.Array_Length (Data, Item.Children) = 29
           and then Field_Name (Data, Item, 0, "instance_id")
           and then Field_Name (Data, Item, 1, "alias")
           and then Field_Name (Data, Item, 2, "parent_instance")
           and then Field_Name (Data, Item, 3, "parent_content")
           and then Field_Name (Data, Item, 4, "cause")
           and then Field_Name (Data, Item, 5, "actor")
           and then Field_Name (Data, Item, 6, "born")
           and then Field_Name (Data, Item, 7, "ended")
           and then Field_Name (Data, Item, 8, "state")
           and then Field_Name (Data, Item, 9, "components")
           and then Field_Name (Data, Item, 10, "content_id")
           and then Field_Name (Data, Item, 11, "payload_path")
           and then Field_Name (Data, Item, 12, "mission_hash")
           and then Field_Name (Data, Item, 13, "agent_reference")
           and then Field_Name (Data, Item, 14, "evidence")
           and then Field_Name (Data, Item, 15, "workspace")
           and then Field_Name (Data, Item, 16, "base_payload_path")
           and then Field_Name (Data, Item, 17, "base_root")
           and then Field_Name (Data, Item, 18, "root_set_hash")
           and then Field_Name (Data, Item, 19, "delta_hash")
           and then Field_Name (Data, Item, 20, "delta")
           and then Field_Name (Data, Item, 21, "conflicts")
           and then Field_Name (Data, Item, 22, "contamination")
           and then Field_Name (Data, Item, 23, "world_kind")
           and then Field_Name (Data, Item, 24, "descendants")
           and then Field_Name (Data, Item, 25, "complexity")
           and then Field_Name (Data, Item, 26, "risk")
           and then Field_Name (Data, Item, 27, "payload_pruned")
           and then Field_Name (Data, Item, 28, "pruned_at");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.recovery_material") and then
        Payload_Is (Data, Item.Record_Name, "AuthorityMaterial") then
         return E.Array_Length (Data, Item.Children) = 3
           and then Field_Name (Data, Item, 0, "terminal")
           and then Field_Name (Data, Item, 1, "finalization")
           and then Field_Name (Data, Item, 2, "pending_store");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.evaluation_history") and then
        Payload_Is (Data, Item.Record_Name, "EvaluationRecord") then
         return E.Array_Length (Data, Item.Children) = 7
           and then Field_Name (Data, Item, 0, "subject")
           and then Field_Name (Data, Item, 1, "content")
           and then Field_Name (Data, Item, 2, "requirement")
           and then Field_Name (Data, Item, 3, "run")
           and then Field_Name (Data, Item, 4, "epoch")
           and then Field_Name (Data, Item, 5, "state")
           and then Field_Name (Data, Item, 6, "outcome");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.evaluation_history") and then
        Payload_Is (Data, Item.Record_Name, "EvaluationCursor") then
         return E.Array_Length (Data, Item.Children) = 2
           and then Field_Name (Data, Item, 0, "epoch")
           and then Field_Name (Data, Item, 1, "run");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.owner_transitions") and then
        Payload_Is (Data, Item.Record_Name, "OwnerGrant") then
         return E.Array_Length (Data, Item.Children) = 19
           and then Field_Name (Data, Item, 0, "action")
           and then Field_Name (Data, Item, 1, "state")
           and then Field_Name (Data, Item, 2, "grant")
           and then Field_Name (Data, Item, 3, "use_id")
           and then Field_Name (Data, Item, 4, "issuer")
           and then Field_Name (Data, Item, 5, "principal")
           and then Field_Name (Data, Item, 6, "subject")
           and then Field_Name (Data, Item, 7, "content")
           and then Field_Name (Data, Item, 8, "transaction")
           and then Field_Name (Data, Item, 9, "current_requirement")
           and then Field_Name (Data, Item, 10, "expected_requirement")
           and then Field_Name (Data, Item, 11, "reason")
           and then Field_Name (Data, Item, 12, "issued_grant")
           and then Field_Name (Data, Item, 13, "reserved_grant")
           and then Field_Name (Data, Item, 14, "reserved_use")
           and then Field_Name (Data, Item, 15, "failed_run")
           and then Field_Name (Data, Item, 16, "prior_head")
           and then Field_Name (Data, Item, 17, "next_run")
           and then Field_Name (Data, Item, 18, "epoch");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.owner_transitions") and then
        Payload_Is (Data, Item.Record_Name, "OwnerRequest") then
         return E.Array_Length (Data, Item.Children) = 13
           and then Field_Name (Data, Item, 0, "action")
           and then Field_Name (Data, Item, 1, "peer")
           and then Field_Name (Data, Item, 2, "owner")
           and then Field_Name (Data, Item, 3, "trusted_issuer")
           and then Field_Name (Data, Item, 4, "subject")
           and then Field_Name (Data, Item, 5, "content")
           and then Field_Name (Data, Item, 6, "transaction")
           and then Field_Name (Data, Item, 7, "current_requirement")
           and then Field_Name (Data, Item, 8, "resulting_requirement")
           and then Field_Name (Data, Item, 9, "current_head")
           and then Field_Name (Data, Item, 10, "attempt")
           and then Field_Name (Data, Item, 11, "current_epoch")
           and then Field_Name (Data, Item, 12, "grant");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.owner_retry_audit") and then
        Payload_Is (Data, Item.Record_Name, "UseReceipt") then
         return E.Array_Length (Data, Item.Children) = 6
           and then Field_Name (Data, Item, 0, "consumed")
           and then Field_Name (Data, Item, 1, "issued_event")
           and then Field_Name (Data, Item, 2, "reserved_event")
           and then Field_Name (Data, Item, 3, "consumed_event")
           and then Field_Name (Data, Item, 4, "consumed_issue")
           and then Field_Name (Data, Item, 5, "consumed_reservation");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.owner_retry_audit") and then
        Payload_Is (Data, Item.Record_Name, "RetryAudit") then
         return E.Array_Length (Data, Item.Children) = 5
           and then Field_Name (Data, Item, 0, "before_request")
           and then Field_Name (Data, Item, 1, "receipt")
           and then Field_Name (Data, Item, 2, "current_head")
           and then Field_Name (Data, Item, 3, "prepared_evidence")
           and then Field_Name (Data, Item, 4, "current_epoch");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.owner_retry_audit") and then
        Payload_Is (Data, Item.Record_Name, "FullScope") then
         return E.Array_Length (Data, Item.Children) = 3
           and then Field_Name (Data, Item, 0, "subject")
           and then Field_Name (Data, Item, 1, "content")
           and then Field_Name (Data, Item, 2, "transaction");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.owner_collapse_data") and then
        Payload_Is (Data, Item.Record_Name, "OwnerCollapseData") then
         return E.Array_Length (Data, Item.Children) = 12
           and then Field_Name (Data, Item, 0, "mode")
           and then Field_Name (Data, Item, 1, "scope")
           and then Field_Name (Data, Item, 2, "world")
           and then Field_Name (Data, Item, 3, "requirement")
           and then Field_Name (Data, Item, 4, "before_material")
           and then Field_Name (Data, Item, 5, "after_material")
           and then Field_Name (Data, Item, 6, "request")
           and then Field_Name (Data, Item, 7, "receipt")
           and then Field_Name (Data, Item, 8, "current_epoch")
           and then Field_Name (Data, Item, 9, "prepared")
           and then Field_Name (Data, Item, 10, "resulting")
           and then Field_Name (Data, Item, 11, "event");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.resource_run_ledger") and then
        Payload_Is (Data, Item.Record_Name, "RunContext") then
         return E.Array_Length (Data, Item.Children) = 9
           and then Field_Name (Data, Item, 0, "universe")
           and then Field_Name (Data, Item, 1, "policy")
           and then Field_Name (Data, Item, 2, "resource")
           and then Field_Name (Data, Item, 3, "unit")
           and then Field_Name (Data, Item, 4, "instance")
           and then Field_Name (Data, Item, 5, "host")
           and then Field_Name (Data, Item, 6, "boot")
           and then Field_Name (Data, Item, 7, "authority")
           and then Field_Name (Data, Item, 8, "policy_epoch");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.resource_run_ledger") and then
        Payload_Is (Data, Item.Record_Name, "RunBinding") then
         return E.Array_Length (Data, Item.Children) = 10
           and then Field_Name (Data, Item, 0, "reservation")
           and then Field_Name (Data, Item, 1, "operation")
           and then Field_Name (Data, Item, 2, "owner")
           and then Field_Name (Data, Item, 3, "workload")
           and then Field_Name (Data, Item, 4, "universe_head")
           and then Field_Name (Data, Item, 5, "capability")
           and then Field_Name (Data, Item, 6, "grant_use")
           and then Field_Name (Data, Item, 7, "payload")
           and then Field_Name (Data, Item, 8, "provenance")
           and then Field_Name (Data, Item, 9, "resource_epoch");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.resource_run_ledger") and then
        Payload_Is (Data, Item.Record_Name, "RunState") then
         return E.Array_Length (Data, Item.Children) = 7
           and then Field_Name (Data, Item, 0, "scope")
           and then Field_Name (Data, Item, 1, "resource_epoch")
           and then Field_Name (Data, Item, 2, "universe_head")
           and then Field_Name (Data, Item, 3, "ledger_head")
           and then Field_Name (Data, Item, 4, "capacity")
           and then Field_Name (Data, Item, 5, "held_total")
           and then Field_Name (Data, Item, 6, "charged_total");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.resource_run_ledger") and then
        Payload_Is (Data, Item.Record_Name, "RunRow") then
         return E.Array_Length (Data, Item.Children) = 11
           and then Field_Name (Data, Item, 0, "scope")
           and then Field_Name (Data, Item, 1, "bound")
           and then Field_Name (Data, Item, 2, "parent")
           and then Field_Name (Data, Item, 3, "kind")
           and then Field_Name (Data, Item, 4, "state")
           and then Field_Name (Data, Item, 5, "amount")
           and then Field_Name (Data, Item, 6, "observed_usage")
           and then Field_Name (Data, Item, 7, "planned_unit")
           and then Field_Name (Data, Item, 8, "actual_unit")
           and then Field_Name (Data, Item, 9, "cgroup")
           and then Field_Name (Data, Item, 10, "invocation");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.resource_run_ledger") and then
        Payload_Is (Data, Item.Record_Name, "RunRequest") then
         return E.Array_Length (Data, Item.Children) = 10
           and then Field_Name (Data, Item, 0, "kind")
           and then Field_Name (Data, Item, 1, "scope")
           and then Field_Name (Data, Item, 2, "expected_epoch")
           and then Field_Name (Data, Item, 3, "expected_ledger_head")
           and then Field_Name (Data, Item, 4, "request_id")
           and then Field_Name (Data, Item, 5, "reservation")
           and then Field_Name (Data, Item, 6, "operation_id")
           and then Field_Name (Data, Item, 7, "requester")
           and then Field_Name (Data, Item, 8, "bound")
           and then Field_Name (Data, Item, 9, "new_row");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.resource_run_ledger") and then
        Payload_Is (Data, Item.Record_Name, "RunObservation") then
         return E.Array_Length (Data, Item.Children) = 8
           and then Field_Name (Data, Item, 0, "scope")
           and then Field_Name (Data, Item, 1, "resource_epoch")
           and then Field_Name (Data, Item, 2, "bound")
           and then Field_Name (Data, Item, 3, "actual_unit")
           and then Field_Name (Data, Item, 4, "cgroup")
           and then Field_Name (Data, Item, 5, "invocation")
           and then Field_Name (Data, Item, 6, "observation_head")
           and then Field_Name (Data, Item, 7, "observed");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.recovery_authority_kernel_v3") and then
        Payload_Is (Data, Item.Record_Name, "BoundUse") then
         return E.Array_Length (Data, Item.Children) = 30
           and then Field_Name (Data, Item, 0, "mode")
           and then Field_Name (Data, Item, 1, "operation")
           and then Field_Name (Data, Item, 2, "transaction")
           and then Field_Name (Data, Item, 3, "capability")
           and then Field_Name (Data, Item, 4, "universe_head")
           and then Field_Name (Data, Item, 5, "instance")
           and then Field_Name (Data, Item, 6, "subject")
           and then Field_Name (Data, Item, 7, "staged_root")
           and then Field_Name (Data, Item, 8, "current_requirement")
           and then Field_Name (Data, Item, 9, "resulting_requirement")
           and then Field_Name (Data, Item, 10, "requester")
           and then Field_Name (Data, Item, 11, "grant_use")
           and then Field_Name (Data, Item, 12, "policy_identity")
           and then Field_Name (Data, Item, 13, "selected_evaluation")
           and then Field_Name (Data, Item, 14, "history_head")
           and then Field_Name (Data, Item, 15, "reservation")
           and then Field_Name (Data, Item, 16, "host")
           and then Field_Name (Data, Item, 17, "before_prime")
           and then Field_Name (Data, Item, 18, "before_root")
           and then Field_Name (Data, Item, 19, "before_mapping")
           and then Field_Name (Data, Item, 20, "staged_mapping")
           and then Field_Name (Data, Item, 21, "input_snapshot")
           and then Field_Name (Data, Item, 22, "kernel_build")
           and then Field_Name (Data, Item, 23, "kernel_library")
           and then Field_Name (Data, Item, 24, "kernel_mapping")
           and then Field_Name (Data, Item, 25, "issuer_head")
           and then Field_Name (Data, Item, 26, "receipt_head")
           and then Field_Name (Data, Item, 27, "causal_head")
           and then Field_Name (Data, Item, 28, "policy_epoch")
           and then Field_Name (Data, Item, 29, "resource_epoch");
      end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.recovery_authority_kernel_v3") and then
        Payload_Is (Data, Item.Record_Name, "NativeObservation") then
         return E.Array_Length (Data, Item.Children) = 2
           and then Field_Name (Data, Item, 0, "live_mapping")
           and then Field_Name (Data, Item, 1, "live_root");
      end if;
      return False;
   end Record_Fields;

   function Same_Key (Data : E.Bytes; Left, Right : E.View) return Boolean is
     (Left.Form = Right.Form and then Left.Form in E.Text_Value | E.Bytes_Value
       and then E.Bytes_Valid (Data, Left.Payload) and then E.Bytes_Valid (Data, Right.Payload)
       and then E.Materialize (Data, Left.Payload) = E.Materialize (Data, Right.Payload));

   function Valid (Data : E.Bytes; Encoded : E.Span) return Boolean is
      Item : constant E.View := E.Decode (Data, Encoded, E.Operation);
      N : E.Count;
      Child : E.Span;
   begin
      case Item.Form is
         when E.Invalid => return False;
         when E.Null_Value | E.Boolean_Value | E.Integer_Value | E.Float_Value |
              E.Text_Value | E.Bytes_Value => return True;
         when E.World_State_Value =>
            return Payload_Is (Data, Item.Payload, "MUTABLE") or else
              Payload_Is (Data, Item.Payload, "FINALIZING") or else
              Payload_Is (Data, Item.Payload, "VALID") or else
              Payload_Is (Data, Item.Payload, "DEGRADED") or else
              Payload_Is (Data, Item.Payload, "DEAD") or else
              Payload_Is (Data, Item.Payload, "ARCHIVED") or else
              Payload_Is (Data, Item.Payload, "COLLAPSED");
         when E.Record_Value =>
            if not Record_Fields (Data, Item) then return False; end if;
         when E.List_Value | E.Tuple_Value | E.Object_Value => null;
      end case;
      N := E.Array_Length (Data, Item.Children);
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            if Item.Form in E.List_Value | E.Tuple_Value then
               Child := E.Array_Element (Data, Item.Children, I);
            else
               declare
                  P : constant E.View := Pair (Data, Item, I);
               begin
                  if P.Form /= E.List_Value or else E.Array_Length (Data, P.Children) /= 2 then
                     return False;
                  end if;
                  if Item.Form = E.Object_Value then
                     declare
                        Key : constant E.View := E.Decode
                          (Data, E.Array_Element (Data, P.Children, 0), E.Operation);
                     begin
                        if Key.Form not in E.Text_Value | E.Bytes_Value then return False; end if;
                        if I > 0 then
                           for J in E.Count range 0 .. I - 1 loop
                              declare
                                 Earlier : constant E.View := Pair (Data, Item, J);
                                 Other_Key : constant E.View := E.Decode
                                   (Data, E.Array_Element (Data, Earlier.Children, 0), E.Operation);
                              begin
                                 if Same_Key (Data, Key, Other_Key) then return False; end if;
                              end;
                           end loop;
                        end if;
                     end;
                  end if;
                  Child := E.Array_Element (Data, P.Children, 1);
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
      N : E.Count;
   begin
      if Item.Form /= E.Object_Value or else not Valid (Data, Encoded) then return (1, 0); end if;
      N := E.Array_Length (Data, Item.Children);
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               P : constant E.View := Pair (Data, Item, I);
               Key : constant E.View := E.Decode
                 (Data, E.Array_Element (Data, P.Children, 0), E.Operation);
            begin
               if E.Text_Is (Data, Key, Name) then
                  return E.Array_Element (Data, P.Children, 1);
               end if;
            end;
         end loop;
      end if;
      return (1, 0);
   end Field;

   function Same_Encoding (Data : E.Bytes; Left, Right : E.Span) return Boolean is
   begin
      if not Valid (Data, Left) or else not Valid (Data, Right) or else
        Left.Length /= Right.Length then return False; end if;
      if Left.Length > 0 then
         for I in E.Count range 0 .. Left.Length - 1 loop
            if Data (Left.First + I) /= Data (Right.First + I) then return False; end if;
         end loop;
      end if;
      return True;
   end Same_Encoding;
end Worldline.Operation_Archive;
