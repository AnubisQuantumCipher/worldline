with Interfaces;
with Worldline.Resource_Child_Execution;
with Worldline.Resource_Actor_Execution_Wire;
package Worldline.Resource_Child_Execution_Wire with SPARK_Mode is
   package J renames Worldline.Resource_Child_Execution;
   package X renames Worldline.Resource_Actor_Execution_Wire;
   package W renames X.W; package Q renames X.Q;
   use type Interfaces.Unsigned_8; use type Q.Byte_Count;
   use type J.Process_Observation; use type J.Task_Origin; use type J.Namespace_Observation;
   type Raw_Process is record
      raw_status : W.Raw_Id;
      raw_stat : W.Raw_Id;
      raw_cgroup : W.Raw_Id;
      raw_maps : W.Raw_Id;
      raw_cmdline : W.Raw_Id;
      raw_pidfd_info : W.Raw_Id;
      namespace : W.Raw_Id;
      cgroup : W.Raw_Id;
      actual_unit : W.Raw_Id;
      invocation : W.Raw_Id;
      source_lease : W.Raw_Id;
      pidfd_wait : W.Raw_Id;
      host_pid : W.Raw_Quantity;
      start_tick : W.Raw_Quantity;
      parent_pid : W.Raw_Quantity;
      parent_start_tick : W.Raw_Quantity;
      real_uid : W.Raw_Quantity;
      effective_uid : W.Raw_Quantity;
      saved_uid : W.Raw_Quantity;
      real_gid : W.Raw_Quantity;
      effective_gid : W.Raw_Quantity;
      saved_gid : W.Raw_Quantity;
   end record with Convention => C;
   type Raw_Process_Array is array (Q.Byte_Index range <>) of Raw_Process;
   type Raw_Controller is record
      Bound : W.Raw_Binding;
      Process : Raw_Process;
      Requester_Uid, Requester_Gid : W.Raw_Quantity;
      raw_manager : W.Raw_Id;
      raw_channel : W.Raw_Id;
      owner_endpoint : W.Raw_Id;
      expected_owner_endpoint : W.Raw_Id;
      source_lease : W.Raw_Id;
      expected_source_lease : W.Raw_Id;
      worker_image : W.Raw_Id;
      expected_worker_image : W.Raw_Id;
      handler_plan : W.Raw_Id;
      expected_handler_plan : W.Raw_Id;
      raw_request : W.Raw_Id;
      requester : W.Raw_Id;
      dispatch : W.Raw_Id;
      running_event : W.Raw_Id;
      expected_running_event : W.Raw_Id;
      store_genesis : W.Raw_Id;
      expected_store_genesis : W.Raw_Id;
      current_source : W.Raw_Id;
   end record with Convention => C;
   type Raw_Task is record
      Action : Interfaces.Unsigned_8;
      Root, Child : W.Raw_Binding;
      task_id : W.Raw_Id;
      root_world : W.Raw_Id;
      child_world : W.Raw_Id;
      root_instance : W.Raw_Id;
      child_instance : W.Raw_Id;
      world_store : W.Raw_Id;
      full_world_ancestry : W.Raw_Id;
      original_workload : W.Raw_Id;
      sandbox : W.Raw_Id;
      adapter : W.Raw_Id;
      context : W.Raw_Id;
      mission : W.Raw_Id;
      stdin : W.Raw_Id;
      credential_source : W.Raw_Id;
      executable_source : W.Raw_Id;
      configuration : W.Raw_Id;
      owner_plan : W.Raw_Id;
      native_cost_input : W.Raw_Id;
      raw_request : W.Raw_Id;
      requester : W.Raw_Id;
      cause : W.Raw_Id;
      root_dispatch : W.Raw_Id;
      root_running_event : W.Raw_Id;
      task_journal : W.Raw_Id;
      task_intent : W.Raw_Id;
      task_reservation_event : W.Raw_Id;
      task_launch_event : W.Raw_Id;
      parent_namespace_source : W.Raw_Id;
      fd_lineage : W.Raw_Id;
      source_lease : W.Raw_Id;
   end record with Convention => C;
   type Raw_Task_Array is array (Q.Byte_Index range <>) of Raw_Task;
   type Raw_Namespace is record
      identity : W.Raw_Id;
      parent : W.Raw_Id;
      raw_nsfs : W.Raw_Id;
      raw_get_parent : W.Raw_Id;
      source_lease : W.Raw_Id;
   end record with Convention => C;
   type Raw_Namespace_Array is array (Q.Byte_Index range <>) of Raw_Namespace;
   type Raw_Input is record
      Mode : Interfaces.Unsigned_8;
      Controller : Raw_Controller;
      Child_Task : Raw_Task;
   end record with Convention => C;
   function Well_Formed (Data : Q.Byte_Array; V : Raw_Process) return Boolean is
     (W.Well_Formed (Data, V.raw_status)
      and then W.Well_Formed (Data, V.raw_stat)
      and then W.Well_Formed (Data, V.raw_cgroup)
      and then W.Well_Formed (Data, V.raw_maps)
      and then W.Well_Formed (Data, V.raw_cmdline)
      and then W.Well_Formed (Data, V.raw_pidfd_info)
      and then W.Well_Formed (Data, V.namespace)
      and then W.Well_Formed (Data, V.cgroup)
      and then W.Well_Formed (Data, V.actual_unit)
      and then W.Well_Formed (Data, V.invocation)
      and then W.Well_Formed (Data, V.source_lease)
      and then W.Well_Formed (Data, V.pidfd_wait)
      and then W.Well_Formed (Data, V.host_pid)
      and then W.Well_Formed (Data, V.start_tick)
      and then W.Well_Formed (Data, V.parent_pid)
      and then W.Well_Formed (Data, V.parent_start_tick)
      and then W.Well_Formed (Data, V.real_uid)
      and then W.Well_Formed (Data, V.effective_uid)
      and then W.Well_Formed (Data, V.saved_uid)
      and then W.Well_Formed (Data, V.real_gid)
      and then W.Well_Formed (Data, V.effective_gid)
      and then W.Well_Formed (Data, V.saved_gid)) with Global => null;
   function Decode (Data : Q.Byte_Array; V : Raw_Process) return J.Process_Observation is
     (Id => (J.P_raw_status => W.Decode (Data, V.raw_status),
        J.P_raw_stat => W.Decode (Data, V.raw_stat),
        J.P_raw_cgroup => W.Decode (Data, V.raw_cgroup),
        J.P_raw_maps => W.Decode (Data, V.raw_maps),
        J.P_raw_cmdline => W.Decode (Data, V.raw_cmdline),
        J.P_raw_pidfd_info => W.Decode (Data, V.raw_pidfd_info),
        J.P_namespace => W.Decode (Data, V.namespace),
        J.P_cgroup => W.Decode (Data, V.cgroup),
        J.P_actual_unit => W.Decode (Data, V.actual_unit),
        J.P_invocation => W.Decode (Data, V.invocation),
        J.P_source_lease => W.Decode (Data, V.source_lease),
        J.P_pidfd_wait => W.Decode (Data, V.pidfd_wait)),
      Number => (J.P_host_pid => W.Decode (Data, V.host_pid),
        J.P_start_tick => W.Decode (Data, V.start_tick),
        J.P_parent_pid => W.Decode (Data, V.parent_pid),
        J.P_parent_start_tick => W.Decode (Data, V.parent_start_tick),
        J.P_real_uid => W.Decode (Data, V.real_uid),
        J.P_effective_uid => W.Decode (Data, V.effective_uid),
        J.P_saved_uid => W.Decode (Data, V.saved_uid),
        J.P_real_gid => W.Decode (Data, V.real_gid),
        J.P_effective_gid => W.Decode (Data, V.effective_gid),
        J.P_saved_gid => W.Decode (Data, V.saved_gid))) with Global => null, Pre => Well_Formed (Data, V);
   function Well_Formed (Data : Q.Byte_Array; V : Raw_Controller) return Boolean is
     (W.Well_Formed (Data, V.Bound)
      and then Well_Formed (Data, V.Process)
      and then W.Well_Formed (Data, V.Requester_Uid) and then W.Well_Formed (Data, V.Requester_Gid)
      and then W.Well_Formed (Data, V.raw_manager)
      and then W.Well_Formed (Data, V.raw_channel)
      and then W.Well_Formed (Data, V.owner_endpoint)
      and then W.Well_Formed (Data, V.expected_owner_endpoint)
      and then W.Well_Formed (Data, V.source_lease)
      and then W.Well_Formed (Data, V.expected_source_lease)
      and then W.Well_Formed (Data, V.worker_image)
      and then W.Well_Formed (Data, V.expected_worker_image)
      and then W.Well_Formed (Data, V.handler_plan)
      and then W.Well_Formed (Data, V.expected_handler_plan)
      and then W.Well_Formed (Data, V.raw_request)
      and then W.Well_Formed (Data, V.requester)
      and then W.Well_Formed (Data, V.dispatch)
      and then W.Well_Formed (Data, V.running_event)
      and then W.Well_Formed (Data, V.expected_running_event)
      and then W.Well_Formed (Data, V.store_genesis)
      and then W.Well_Formed (Data, V.expected_store_genesis)
      and then W.Well_Formed (Data, V.current_source)) with Global => null;
   function Decode (Data : Q.Byte_Array; V : Raw_Controller) return J.Root_Controller is
     (Bound => W.Decode (Data, V.Bound),
      Process => Decode (Data, V.Process),
      Requester_Uid => W.Decode (Data, V.Requester_Uid), Requester_Gid => W.Decode (Data, V.Requester_Gid),
      Id => (J.R_raw_manager => W.Decode (Data, V.raw_manager),
        J.R_raw_channel => W.Decode (Data, V.raw_channel),
        J.R_owner_endpoint => W.Decode (Data, V.owner_endpoint),
        J.R_expected_owner_endpoint => W.Decode (Data, V.expected_owner_endpoint),
        J.R_source_lease => W.Decode (Data, V.source_lease),
        J.R_expected_source_lease => W.Decode (Data, V.expected_source_lease),
        J.R_worker_image => W.Decode (Data, V.worker_image),
        J.R_expected_worker_image => W.Decode (Data, V.expected_worker_image),
        J.R_handler_plan => W.Decode (Data, V.handler_plan),
        J.R_expected_handler_plan => W.Decode (Data, V.expected_handler_plan),
        J.R_raw_request => W.Decode (Data, V.raw_request),
        J.R_requester => W.Decode (Data, V.requester),
        J.R_dispatch => W.Decode (Data, V.dispatch),
        J.R_running_event => W.Decode (Data, V.running_event),
        J.R_expected_running_event => W.Decode (Data, V.expected_running_event),
        J.R_store_genesis => W.Decode (Data, V.store_genesis),
        J.R_expected_store_genesis => W.Decode (Data, V.expected_store_genesis),
        J.R_current_source => W.Decode (Data, V.current_source))) with Global => null, Pre => Well_Formed (Data, V);
   function Well_Formed (Data : Q.Byte_Array; V : Raw_Task) return Boolean is
     (V.Action <= J.A.Operation'Pos (J.A.Operation'Last)
      and then W.Well_Formed (Data, V.Root)
      and then W.Well_Formed (Data, V.Child)
      and then W.Well_Formed (Data, V.task_id)
      and then W.Well_Formed (Data, V.root_world)
      and then W.Well_Formed (Data, V.child_world)
      and then W.Well_Formed (Data, V.root_instance)
      and then W.Well_Formed (Data, V.child_instance)
      and then W.Well_Formed (Data, V.world_store)
      and then W.Well_Formed (Data, V.full_world_ancestry)
      and then W.Well_Formed (Data, V.original_workload)
      and then W.Well_Formed (Data, V.sandbox)
      and then W.Well_Formed (Data, V.adapter)
      and then W.Well_Formed (Data, V.context)
      and then W.Well_Formed (Data, V.mission)
      and then W.Well_Formed (Data, V.stdin)
      and then W.Well_Formed (Data, V.credential_source)
      and then W.Well_Formed (Data, V.executable_source)
      and then W.Well_Formed (Data, V.configuration)
      and then W.Well_Formed (Data, V.owner_plan)
      and then W.Well_Formed (Data, V.native_cost_input)
      and then W.Well_Formed (Data, V.raw_request)
      and then W.Well_Formed (Data, V.requester)
      and then W.Well_Formed (Data, V.cause)
      and then W.Well_Formed (Data, V.root_dispatch)
      and then W.Well_Formed (Data, V.root_running_event)
      and then W.Well_Formed (Data, V.task_journal)
      and then W.Well_Formed (Data, V.task_intent)
      and then W.Well_Formed (Data, V.task_reservation_event)
      and then W.Well_Formed (Data, V.task_launch_event)
      and then W.Well_Formed (Data, V.parent_namespace_source)
      and then W.Well_Formed (Data, V.fd_lineage)
      and then W.Well_Formed (Data, V.source_lease)) with Global => null;
   function Decode (Data : Q.Byte_Array; V : Raw_Task) return J.Task_Origin is
     (Action => J.A.Operation'Val (V.Action),
      Root => W.Decode (Data, V.Root),
      Child => W.Decode (Data, V.Child),
      Id => (J.T_task_id => W.Decode (Data, V.task_id),
        J.T_root_world => W.Decode (Data, V.root_world),
        J.T_child_world => W.Decode (Data, V.child_world),
        J.T_root_instance => W.Decode (Data, V.root_instance),
        J.T_child_instance => W.Decode (Data, V.child_instance),
        J.T_world_store => W.Decode (Data, V.world_store),
        J.T_full_world_ancestry => W.Decode (Data, V.full_world_ancestry),
        J.T_original_workload => W.Decode (Data, V.original_workload),
        J.T_sandbox => W.Decode (Data, V.sandbox),
        J.T_adapter => W.Decode (Data, V.adapter),
        J.T_context => W.Decode (Data, V.context),
        J.T_mission => W.Decode (Data, V.mission),
        J.T_stdin => W.Decode (Data, V.stdin),
        J.T_credential_source => W.Decode (Data, V.credential_source),
        J.T_executable_source => W.Decode (Data, V.executable_source),
        J.T_configuration => W.Decode (Data, V.configuration),
        J.T_owner_plan => W.Decode (Data, V.owner_plan),
        J.T_native_cost_input => W.Decode (Data, V.native_cost_input),
        J.T_raw_request => W.Decode (Data, V.raw_request),
        J.T_requester => W.Decode (Data, V.requester),
        J.T_cause => W.Decode (Data, V.cause),
        J.T_root_dispatch => W.Decode (Data, V.root_dispatch),
        J.T_root_running_event => W.Decode (Data, V.root_running_event),
        J.T_task_journal => W.Decode (Data, V.task_journal),
        J.T_task_intent => W.Decode (Data, V.task_intent),
        J.T_task_reservation_event => W.Decode (Data, V.task_reservation_event),
        J.T_task_launch_event => W.Decode (Data, V.task_launch_event),
        J.T_parent_namespace_source => W.Decode (Data, V.parent_namespace_source),
        J.T_fd_lineage => W.Decode (Data, V.fd_lineage),
        J.T_source_lease => W.Decode (Data, V.source_lease))) with Global => null, Pre => Well_Formed (Data, V);
   function Well_Formed (Data : Q.Byte_Array; V : Raw_Namespace) return Boolean is
     (W.Well_Formed (Data, V.identity)
      and then W.Well_Formed (Data, V.parent)
      and then W.Well_Formed (Data, V.raw_nsfs)
      and then W.Well_Formed (Data, V.raw_get_parent)
      and then W.Well_Formed (Data, V.source_lease)) with Global => null;
   function Decode (Data : Q.Byte_Array; V : Raw_Namespace) return J.Namespace_Observation is
     (Id => (J.N_identity => W.Decode (Data, V.identity),
        J.N_parent => W.Decode (Data, V.parent),
        J.N_raw_nsfs => W.Decode (Data, V.raw_nsfs),
        J.N_raw_get_parent => W.Decode (Data, V.raw_get_parent),
        J.N_source_lease => W.Decode (Data, V.source_lease))) with Global => null, Pre => Well_Formed (Data, V);
   function Well_Formed (Data : Q.Byte_Array; V : Raw_Input) return Boolean is
     (V.Mode <= J.Admission_Mode'Pos (J.Admission_Mode'Last)
      and then Well_Formed (Data, V.Controller)
      and then (if V.Mode /= J.Admission_Mode'Pos (J.Root_Controller_Admission) then Well_Formed (Data, V.Child_Task))) with Global => null;
   function Decode_Process (Data : Q.Byte_Array; V : Raw_Process_Array) return J.Process_Array
     with Global => null, Pre => (for all I in V'Range => Well_Formed (Data, V (I))),
     Post => Decode_Process'Result'First = V'First and then Decode_Process'Result'Last = V'Last
       and then (for all I in V'Range => Decode_Process'Result (I) = Decode (Data, V (I)));
   function Decode_Task (Data : Q.Byte_Array; V : Raw_Task_Array) return J.Task_Array
     with Global => null, Pre => (for all I in V'Range => Well_Formed (Data, V (I))),
     Post => Decode_Task'Result'First = V'First and then Decode_Task'Result'Last = V'Last
       and then (for all I in V'Range => Decode_Task'Result (I) = Decode (Data, V (I)));
   function Decode_Namespace (Data : Q.Byte_Array; V : Raw_Namespace_Array) return J.Namespace_Array
     with Global => null, Pre => (for all I in V'Range => Well_Formed (Data, V (I))),
     Post => Decode_Namespace'Result'First = V'First and then Decode_Namespace'Result'Last = V'Last
       and then (for all I in V'Range => Decode_Namespace'Result (I) = Decode (Data, V (I)));
end Worldline.Resource_Child_Execution_Wire;
