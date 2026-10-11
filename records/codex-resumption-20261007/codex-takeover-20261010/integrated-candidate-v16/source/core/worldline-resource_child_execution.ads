with SPARK.Big_Integers;
with Worldline.Resource_Actor_Execution;
package Worldline.Resource_Child_Execution with SPARK_Mode is
   package E renames Worldline.Resource_Actor_Execution;
   package A renames E.A; package K renames E.K; package S renames E.S;
   package L renames E.L; package Q renames E.Q;
   use SPARK.Big_Integers;
   use type Q.Byte_Count; use type Q.Ordering; use type L.Phase;
   use type L.Liveness; use type A.Operation; use type A.Decision; use type K.Status; use type S.Action; use type S.Status; use type L.Operation;
   type Admission_Mode is (Root_Controller_Admission, Child_Admission, Task_Reservation_Admission);
   type Status is (Root_Ready_Conjunction, Child_Ready_Conjunction,
      Ledger_Refused, Authority_Refused, Current_Refused, Controller_Refused,
      Actor_Refused, Task_Refused, Parent_Refused, Process_Ancestry_Refused,
      Namespace_Ancestry_Refused, Task_Ready_Conjunction, Task_Transition_Refused);
   -- Full factual inputs do not authenticate themselves. Actual protected
   -- producer/source correspondence and physical custody remain required.
   type Process_Id_Field is (P_raw_status, P_raw_stat, P_raw_cgroup, P_raw_maps, P_raw_cmdline, P_raw_pidfd_info, P_namespace, P_cgroup, P_actual_unit, P_invocation, P_source_lease, P_pidfd_wait);
   type Process_Number_Field is (P_host_pid, P_start_tick, P_parent_pid, P_parent_start_tick, P_real_uid, P_effective_uid, P_saved_uid, P_real_gid, P_effective_gid, P_saved_gid);
   type Controller_Field is (R_raw_manager, R_raw_channel, R_owner_endpoint, R_expected_owner_endpoint, R_source_lease, R_expected_source_lease, R_worker_image, R_expected_worker_image, R_handler_plan, R_expected_handler_plan, R_raw_request, R_requester, R_dispatch, R_running_event, R_expected_running_event, R_store_genesis, R_expected_store_genesis, R_current_source);
   type Task_Field is (T_task_id, T_root_world, T_child_world, T_root_instance, T_child_instance, T_world_store, T_full_world_ancestry, T_original_workload, T_sandbox, T_adapter, T_context, T_mission, T_stdin, T_credential_source, T_executable_source, T_configuration, T_owner_plan, T_native_cost_input, T_raw_request, T_requester, T_cause, T_root_dispatch, T_root_running_event, T_task_journal, T_task_intent, T_task_reservation_event, T_task_launch_event, T_parent_namespace_source, T_fd_lineage, T_source_lease);
   type Namespace_Field is (N_identity, N_parent, N_raw_nsfs, N_raw_get_parent, N_source_lease);
   type Process_Ids is array (Process_Id_Field) of L.Identity;
   type Process_Numbers is array (Process_Number_Field) of Q.Quantity;
   type Process_Observation is record Id : Process_Ids; Number : Process_Numbers; end record;
   type Process_Array is array (Q.Byte_Index range <>) of Process_Observation;
   type Controller_Ids is array (Controller_Field) of L.Identity;
   type Root_Controller is record Bound : L.Binding; Process : Process_Observation; Requester_Uid, Requester_Gid : Q.Quantity; Id : Controller_Ids; end record;
   type Task_Ids is array (Task_Field) of L.Identity;
   type Task_Origin is record Action : A.Operation; Root, Child : L.Binding; Id : Task_Ids; end record;
   type Task_Array is array (Q.Byte_Index range <>) of Task_Origin;
   type Namespace_Ids is array (Namespace_Field) of L.Identity;
   type Namespace_Observation is record Id : Namespace_Ids; end record;
   type Namespace_Array is array (Q.Byte_Index range <>) of Namespace_Observation;
   function Number_Valid (Data : Q.Byte_Array; V : Q.Quantity) return Boolean is
     (L.T.Nonnegative_Valid (Data, V)) with Global => null;
   function Number_Same (Data : Q.Byte_Array; X, Y : Q.Quantity) return Boolean is
     (Number_Valid (Data, X) and then Number_Valid (Data, Y)
      and then Q.Compare (Data, X, Y) = Q.Equal) with Global => null;
   function Process_Valid (Data : Q.Byte_Array; P : Process_Observation) return Boolean is
     ((for all F in Process_Id_Field => L.Id_Valid (Data, P.Id (F)))
      and then (for all F in Process_Number_Field => Number_Valid (Data, P.Number (F)))
      and then L.Exact_Value (Data, P.Number (P_host_pid)) > To_Big_Integer (0)
      and then S.K.Text (Data, P.Id (P_pidfd_wait), "PIDFD_LIVE")) with Global => null;
   function Same_Process (Data : Q.Byte_Array; X, Y : Process_Observation) return Boolean is
     (Process_Valid (Data, X) and then Process_Valid (Data, Y)
      and then (for all F in Process_Id_Field => L.Same (Data, X.Id (F), Y.Id (F)))
      and then (for all F in Process_Number_Field => Number_Same (Data, X.Number (F), Y.Number (F)))) with Global => null;
   function Controller_Valid (Data : Q.Byte_Array; R : Root_Controller) return Boolean is
     (L.Binding_Valid (Data, R.Bound) and then Process_Valid (Data, R.Process)
      and then Number_Valid (Data, R.Requester_Uid) and then Number_Valid (Data, R.Requester_Gid)
      and then L.Exact_Value (Data, R.Process.Number (P_effective_uid)) = To_Big_Integer (0)
      and then (for all F in Controller_Field => L.Id_Valid (Data, R.Id (F)))
      and then L.Same (Data, R.Id (R_owner_endpoint), R.Id (R_expected_owner_endpoint))
      and then L.Same (Data, R.Id (R_source_lease), R.Id (R_expected_source_lease))
      and then L.Same (Data, R.Id (R_worker_image), R.Id (R_expected_worker_image))
      and then L.Same (Data, R.Id (R_handler_plan), R.Id (R_expected_handler_plan))
      and then L.Same (Data, R.Id (R_running_event), R.Id (R_expected_running_event))
      and then L.Same (Data, R.Id (R_store_genesis), R.Id (R_expected_store_genesis))
      and then L.Same (Data, R.Id (R_source_lease), R.Process.Id (P_source_lease))) with Global => null;
   function Original_Root_Holds (Resource_Data, Authority_Data : Q.Byte_Array;
      Original : A.Binding; R : Root_Controller) return Boolean is
     (A.Valid (Authority_Data, Original) and then L.Binding_Valid (Resource_Data, R.Bound)
      and then E.Digest_Matches (Resource_Data, R.Bound.Operation, Original.Id (A.Operation_Id))
      and then E.Digest_Matches (Resource_Data, R.Bound.Reservation, Original.Id (A.Reservation))
      and then E.Digest_Matches (Resource_Data, R.Bound.Capability, Original.Id (A.Grant_Id))
      and then E.Digest_Matches (Resource_Data, R.Bound.Grant_Use, Original.Id (A.Use_Id))
      and then E.Digest_Matches (Resource_Data, R.Bound.Workload, Original.Id (A.Target))
      and then E.Digest_Matches (Resource_Data, R.Bound.Provenance, Original.Id (A.Provenance))
      and then E.Digest_Matches (Resource_Data, R.Bound.Universe_Head, Original.Id (A.Universe_Head))
      and then E.Epoch_Matches (Resource_Data, Authority_Data, R.Bound.Resource_Epoch, Original.Resource_Epoch)) with Global => null;
   function Root_Controller_Holds (Data : Q.Byte_Array; State : S.State;
      History : S.History_Array; Rows : L.Row_Array; Observed : L.Native_Array;
      Facts : S.Facts_Array; Current : S.Current_Observation; R : Root_Controller) return Boolean is
     (Controller_Valid (Data, R) and then Rows'Length = Observed'Length and then Rows'Length = Facts'Length
      and then (for some I in Rows'Range => S.Retained_Origin (Data, State, History, Rows (I))
        and then L.Same_Binding (Data, Rows (I).Bound, R.Bound)
        and then Rows (I).State = L.Running and then L.Counted (Rows (I)) and then L.Has_Effect (Rows (I))
        and then Observed (Observed'First + (I - Rows'First)).Observed = L.Live
        and then L.Same_Binding (Data, R.Bound, Observed (Observed'First + (I - Rows'First)).Bound)
        and then L.Same (Data, Rows (I).Scope.Host, Current.Scope.Host)
        and then L.Same (Data, Rows (I).Scope.Boot, Current.Scope.Boot)
        and then L.Same (Data, Rows (I).Cgroup, R.Process.Id (P_cgroup))
        and then L.Same (Data, Rows (I).Invocation, R.Process.Id (P_invocation))
        and then L.Same (Data, Rows (I).Actual_Unit, R.Process.Id (P_actual_unit))
        and then L.Same (Data, R.Id (R_dispatch), Facts (Facts'First + (I - Rows'First)).Dispatch)
        and then L.Same (Data, R.Process.Id (P_namespace), Facts (Facts'First + (I - Rows'First)).Namespace)
        and then L.Same (Data, R.Id (R_worker_image), Facts (Facts'First + (I - Rows'First)).Helper_Image))) with Global => null;
   function Task_Valid (Data : Q.Byte_Array; T : Task_Origin) return Boolean is
     (L.Binding_Valid (Data, T.Root) and then L.Binding_Valid (Data, T.Child)
      and then (for all F in Task_Field =>
        (if F in T_root_world | T_child_world | T_task_reservation_event | T_task_launch_event then (if T.Id (F).Present then L.Id_Valid (Data, T.Id (F)))
         else L.Id_Valid (Data, T.Id (F))))) with Global => null;
   function Same_Task (Data : Q.Byte_Array; X, Y : Task_Origin) return Boolean is
     (Task_Valid (Data, X) and then Task_Valid (Data, Y) and then X.Action = Y.Action
      and then L.Same_Binding (Data, X.Root, Y.Root) and then L.Same_Binding (Data, X.Child, Y.Child)
      and then (for all F in Task_Field => L.Optional_Same (Data, X.Id (F), Y.Id (F)))) with Global => null;
   function Task_Roster_Valid (Data : Q.Byte_Array; T : Task_Array) return Boolean is
     ((for all I in T'Range => Task_Valid (Data, T (I)))
      and then (for all I in T'Range => (for all J in T'Range => (if I < J then
        not L.Same (Data, T (I).Id (T_task_id), T (J).Id (T_task_id))
        and then not L.Same (Data, T (I).Child.Operation, T (J).Child.Operation)
        and then not L.Same (Data, T (I).Child.Reservation, T (J).Child.Reservation))))) with Global => null;
   function Child_Holds (Data : Q.Byte_Array; Original : A.Binding; R : Root_Controller;
      Actor : K.Observation; T : Task_Origin; Tasks : Task_Array) return Boolean is
     (Task_Valid (Data, T)
      and then L.Id_Valid (Data, T.Id (T_task_reservation_event))
      and then L.Id_Valid (Data, T.Id (T_task_launch_event))
      and then Task_Roster_Valid (Data, Tasks)
      and then (for some I in Tasks'Range => Same_Task (Data, T, Tasks (I)))
      and then T.Action = Original.Action and then L.Same_Binding (Data, T.Root, R.Bound)
      and then L.Same_Binding (Data, T.Child, Actor.Bound)
      and then not L.Same (Data, T.Child.Operation, T.Root.Operation)
      and then not L.Same (Data, T.Child.Reservation, T.Root.Reservation)
      and then L.Same (Data, T.Child.Capability, T.Root.Capability)
      and then L.Same (Data, T.Child.Grant_Use, T.Root.Grant_Use)
      and then L.Same (Data, T.Child.Owner, T.Root.Owner)
      and then L.Same (Data, T.Child.Provenance, T.Root.Provenance)
      and then L.Same (Data, T.Child.Operation, T.Id (T_task_id))
      and then L.Same (Data, T.Child.Workload, T.Id (T_original_workload))
      and then L.Same (Data, T.Id (T_requester), Actor.Original_Requester)
      and then L.Same (Data, T.Id (T_requester), R.Id (R_requester))
      and then L.Same (Data, T.Id (T_raw_request), R.Id (R_raw_request))
      and then L.Same (Data, T.Id (T_source_lease), R.Id (R_source_lease))
      and then L.Same (Data, T.Id (T_owner_plan), Actor.Executable_Plan)
      and then L.Same (Data, T.Id (T_root_dispatch), R.Id (R_dispatch))
      and then L.Same (Data, T.Id (T_root_running_event), R.Id (R_running_event))) with Global => null;
   function Parent_Holds (Data : Q.Byte_Array; Rows : L.Row_Array; R : Root_Controller; T : Task_Origin) return Boolean is
     ((for some I in Rows'Range => L.Same_Binding (Data, Rows (I).Bound, R.Bound)
       and then (for some J in Rows'Range => I < J and then L.Same_Binding (Data, Rows (J).Bound, T.Child)
         and then Rows (I).State = L.Running and then Rows (J).State = L.Running
         and then L.Counted (Rows (I)) and then L.Counted (Rows (J))
         and then L.Has_Effect (Rows (I)) and then L.Has_Effect (Rows (J))
         and then L.Parent_Supports (Data, Rows (I), Rows (J))))) with Global => null;
   function Process_Ancestry (Data : Q.Byte_Array; R : Root_Controller; Actor : K.Observation; P : Process_Array) return Boolean is
     (P'Length > 0 and then (for all I in P'Range => Process_Valid (Data, P (I)))
      and then Same_Process (Data, P (P'First), R.Process)
      and then Number_Same (Data, P (P'Last).Number (P_host_pid), Actor.Host_Pid)
      and then L.Same (Data, P (P'Last).Id (P_namespace), Actor.Namespace)
      and then L.Same (Data, P (P'Last).Id (P_raw_status), Actor.Raw_Proc_Status)
      and then L.Same (Data, P (P'Last).Id (P_raw_cgroup), Actor.Raw_Proc_Cgroup)
      and then L.Same (Data, P (P'Last).Id (P_raw_maps), Actor.Raw_Proc_Maps)
      and then L.Same (Data, P (P'Last).Id (P_raw_cmdline), Actor.Raw_Proc_Cmdline)
      and then L.Same (Data, P (P'Last).Id (P_raw_pidfd_info), Actor.Raw_Pidfd_Info)
      and then Number_Same (Data, P (P'Last).Number (P_real_uid), Actor.Real_Uid)
      and then Number_Same (Data, P (P'Last).Number (P_effective_uid), Actor.Effective_Uid)
      and then Number_Same (Data, P (P'Last).Number (P_saved_uid), Actor.Saved_Uid)
      and then Number_Same (Data, P (P'Last).Number (P_real_gid), Actor.Real_Gid)
      and then Number_Same (Data, P (P'Last).Number (P_effective_gid), Actor.Effective_Gid)
      and then Number_Same (Data, P (P'Last).Number (P_saved_gid), Actor.Saved_Gid)
      and then (for all I in P'Range => L.Same (Data, P (I).Id (P_source_lease), R.Id (R_source_lease)))
      and then (for all I in P'Range => (if I > P'First then
        Number_Same (Data, P (I).Number (P_parent_pid), P (I - 1).Number (P_host_pid))
        and then Number_Same (Data, P (I).Number (P_parent_start_tick), P (I - 1).Number (P_start_tick))))
      and then (for all I in P'Range => (for all J in P'Range => (if I < J then
        not Number_Same (Data, P (I).Number (P_host_pid), P (J).Number (P_host_pid)))))) with Global => null;
   function Namespace_Ancestry (Data : Q.Byte_Array; R : Root_Controller; Actor : K.Observation; N : Namespace_Array) return Boolean is
     (N'Length > 0 and then (for all I in N'Range => L.Id_Valid (Data, N (I).Id (N_identity))
        and then L.Id_Valid (Data, N (I).Id (N_raw_nsfs)) and then L.Id_Valid (Data, N (I).Id (N_raw_get_parent))
        and then L.Same (Data, N (I).Id (N_source_lease), R.Id (R_source_lease)))
      and then L.Same (Data, N (N'First).Id (N_identity), R.Process.Id (P_namespace))
      and then L.Same (Data, N (N'Last).Id (N_identity), Actor.Namespace)
      and then (for all I in N'Range => (if I > N'First then L.Same (Data, N (I).Id (N_parent), N (I - 1).Id (N_identity))))
      and then (for all I in N'Range => (for all J in N'Range => (if I < J then
        not L.Same (Data, N (I).Id (N_identity), N (J).Id (N_identity)))))) with Global => null;
   function Root_Admission_Reference (Resource_Data, Authority_Data : Q.Byte_Array;
      State : S.State; History : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      W : E.Crosswalk; Grants : A.Grants; Uses : A.Uses; Original : A.Binding;
      Now : Q.Quantity; Evidence : A.Evidence; Receipts, Events : A.C.Retained_Rows;
      Controller : Root_Controller) return Status with Ghost, Global => null;
   function Root_Admission (Resource_Data, Authority_Data : Q.Byte_Array;
      State : S.State; History : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      W : E.Crosswalk; Grants : A.Grants; Uses : A.Uses; Original : A.Binding;
      Now : Q.Quantity; Evidence : A.Evidence; Receipts, Events : A.C.Retained_Rows;
      Controller : Root_Controller) return Status with Global => null, Post => Root_Admission'Result = Root_Admission_Reference (Resource_Data, Authority_Data, State, History, Rows, Projection, Buckets, Observed, Facts, Current, W, Grants, Uses, Original, Now, Evidence, Receipts, Events, Controller)
       and then (if Root_Admission'Result = Root_Ready_Conjunction then
         Original_Root_Holds (Resource_Data, Authority_Data, Original, Controller)
         and then Root_Controller_Holds (Resource_Data, State, History, Rows, Observed, Facts, Current, Controller)
         and then A.Decide (Authority_Data, Grants, Uses, Original, Now, A.Authorize_Execution, Evidence, Receipts, Events) = A.Execution_Ready
         and then S.Valid (Resource_Data, State, History, Rows, Projection, Buckets, Current)
         and then S.Native_Valid (Resource_Data, State, History, Rows, Observed, Facts));
   function Reference (Resource_Data, Authority_Data : Q.Byte_Array;
      State : S.State; History : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      W : E.Crosswalk; Grants : A.Grants; Uses : A.Uses; Original : A.Binding;
      Now : Q.Quantity; Evidence : A.Evidence; Receipts, Events : A.C.Retained_Rows;
      Controller : Root_Controller; Actor : K.Observation; Capabilities : K.Capability_Array;
      Groups, Proc_Groups : K.Group_Array; Child_Task : Task_Origin; Tasks : Task_Array;
      Processes : Process_Array; Namespaces : Namespace_Array) return Status with Ghost, Global => null;
   function Decide (Resource_Data, Authority_Data : Q.Byte_Array;
      State : S.State; History : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      W : E.Crosswalk; Grants : A.Grants; Uses : A.Uses; Original : A.Binding;
      Now : Q.Quantity; Evidence : A.Evidence; Receipts, Events : A.C.Retained_Rows;
      Controller : Root_Controller; Actor : K.Observation; Capabilities : K.Capability_Array;
      Groups, Proc_Groups : K.Group_Array; Child_Task : Task_Origin; Tasks : Task_Array;
      Processes : Process_Array; Namespaces : Namespace_Array) return Status with Global => null, Post => Decide'Result = Reference (Resource_Data, Authority_Data, State, History, Rows, Projection, Buckets, Observed, Facts, Current, W, Grants, Uses, Original, Now, Evidence, Receipts, Events, Controller, Actor, Capabilities, Groups, Proc_Groups, Child_Task, Tasks, Processes, Namespaces)
       and then (if Decide'Result = Child_Ready_Conjunction then
         K.Check (Resource_Data, State, History, Rows, Projection, Buckets, Observed, Facts, Current, Actor, Capabilities, Groups, Proc_Groups) = K.Ready_Conjunct
         and then Parent_Holds (Resource_Data, Rows, Controller, Child_Task)
         and then Child_Holds (Resource_Data, Original, Controller, Actor, Child_Task, Tasks)
         and then Process_Ancestry (Resource_Data, Controller, Actor, Processes)
         and then Namespace_Ancestry (Resource_Data, Controller, Actor, Namespaces));
   function Task_Request_Holds (Data : Q.Byte_Array; Original : A.Binding;
      R : Root_Controller; T : Task_Origin; Tasks : Task_Array; Request : S.Intent) return Boolean is
     (Task_Valid (Data, T) and then Task_Roster_Valid (Data, Tasks)
      and then (for some I in Tasks'Range => Same_Task (Data, T, Tasks (I)))
      and then T.Action = Original.Action and then L.Same_Binding (Data, T.Root, R.Bound)
      and then L.Same_Binding (Data, T.Child, Request.Original.Bound)
      and then not L.Same (Data, T.Child.Operation, T.Root.Operation)
      and then not L.Same (Data, T.Child.Reservation, T.Root.Reservation)
      and then L.Same (Data, T.Child.Operation, T.Id (T_task_id))
      and then L.Same (Data, T.Child.Capability, T.Root.Capability)
      and then L.Same (Data, T.Child.Grant_Use, T.Root.Grant_Use)
      and then L.Same (Data, T.Child.Owner, T.Root.Owner)
      and then L.Same (Data, T.Child.Provenance, T.Root.Provenance)
      and then L.Same (Data, T.Child.Workload, T.Id (T_original_workload))
      and then L.Same (Data, Request.Original.New_Row.Parent, T.Root.Reservation)
      and then L.Same (Data, T.Id (T_cause), Request.Cause)
      and then L.Same (Data, T.Id (T_requester), Request.Requester)
      and then L.Same (Data, T.Id (T_requester), R.Id (R_requester))
      and then L.Same (Data, T.Id (T_raw_request), R.Id (R_raw_request))
      and then L.Same (Data, T.Id (T_source_lease), R.Id (R_source_lease))
      and then L.Same (Data, T.Id (T_root_dispatch), R.Id (R_dispatch))
      and then L.Same (Data, T.Id (T_root_running_event), R.Id (R_running_event))) with Global => null;
   -- A transparent checked equivalence, not an imported/assumed theorem.
   procedure Root_Refines_Original (Resource_Data, Authority_Data : Q.Byte_Array;
      Original : A.Binding; R : Root_Controller; Actor : K.Observation)
   with Ghost, Global => null, Always_Terminates,
     Post => (if L.Same_Binding (Resource_Data, R.Bound, Actor.Bound) then
       Original_Root_Holds (Resource_Data, Authority_Data, Original, R) =
       E.Original_Holds (Resource_Data, Authority_Data, Original, Actor));
   function Task_Admission_Reference (Resource_Data, Authority_Data : Q.Byte_Array;
      State : S.State; History : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      W : E.Crosswalk; Grants : A.Grants; Uses : A.Uses; Original : A.Binding;
      Now : Q.Quantity; Evidence : A.Evidence; Receipts, Events : A.C.Retained_Rows;
      Controller : Root_Controller; Proposed : S.State; Proposed_History : S.History_Array;
      Proposed_Rows : L.Row_Array; Proposed_Projection : S.Projection_Array;
      Proposed_Buckets, Actual_Buckets : S.Bucket_Array; Request : S.Intent;
      Child_Task : Task_Origin; Tasks : Task_Array) return Status with Ghost, Global => null;
   function Task_Admission (Resource_Data, Authority_Data : Q.Byte_Array;
      State : S.State; History : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      W : E.Crosswalk; Grants : A.Grants; Uses : A.Uses; Original : A.Binding;
      Now : Q.Quantity; Evidence : A.Evidence; Receipts, Events : A.C.Retained_Rows;
      Controller : Root_Controller; Proposed : S.State; Proposed_History : S.History_Array;
      Proposed_Rows : L.Row_Array; Proposed_Projection : S.Projection_Array;
      Proposed_Buckets, Actual_Buckets : S.Bucket_Array; Request : S.Intent;
      Child_Task : Task_Origin; Tasks : Task_Array) return Status with Global => null, Post => Task_Admission'Result = Task_Admission_Reference (Resource_Data, Authority_Data, State, History, Rows, Projection, Buckets, Observed, Facts, Current, W, Grants, Uses, Original, Now, Evidence, Receipts, Events, Controller, Proposed, Proposed_History, Proposed_Rows, Proposed_Projection, Proposed_Buckets, Actual_Buckets, Request, Child_Task, Tasks);
end Worldline.Resource_Child_Execution;
