with Interfaces;
package body Worldline.Retained_Source_Layout with SPARK_Mode is
   use type Q.Byte_Count;
   use type Interfaces.Integer_64;
   use type Interfaces.Unsigned_8;
   use type Interfaces.Unsigned_32;
   function Start (Extent : Q.Byte_Count) return Cursor is ((Extent, 0, True));
   function Complete (Position : Cursor) return Boolean is (Position.Good and then Position.Consumed = Position.Extent);
   procedure Span (First, Length : Interfaces.Integer_64; Empty_At_One : Boolean; Position : in out Cursor) is
   begin
      if not Position.Good then return; end if;
      if Length < 0 or else First < 1 or else Position.Consumed > Position.Extent or else Q.Byte_Count (Length) > Position.Extent - Position.Consumed then Position.Good := False; return; end if;
      if Length = 0 and then Empty_At_One then
         if First /= 1 then Position.Good := False; end if;
      elsif Position.Consumed = Q.Byte_Count'Last or else First /= Interfaces.Integer_64 (Position.Consumed) + 1 then Position.Good := False; end if;
      if Position.Good then Position.Consumed := Position.Consumed + Q.Byte_Count (Length); end if;
   end Span;
   procedure Append (Raw : CO.Raw_Input; Position : in out Cursor) is
   begin
      Append (Raw.Authority, Position);
      Append (Raw.State, Position);
      Append (Raw.Bound, Position);
      Append (Raw.Requester, Position);
   end Append;
   procedure Append (Raw : CX.Raw_Input; Position : in out Cursor) is
   begin
      Append (Raw.Operation_Input, Position);
      Append (Raw.Material, Position);
   end Append;
   procedure Append (Raw : CX.Raw_Material; Position : in out Cursor) is
   begin
      Append (Raw.Worker_Issued, Position);
      Append (Raw.Worker_Recovered, Position);
      Append (Raw.Canonical_Issued, Position);
      Append (Raw.Canonical_Recovered, Position);
   end Append;
   procedure Append (Raw : D.Raw_Capability; Position : in out Cursor) is
   begin
      Append (Raw.Index, Position);
      Append (Raw.Bounding, Position);
      Append (Raw.Ambient, Position);
   end Append;
   procedure Append (Raw : D.Raw_Observation; Position : in out Cursor) is
   begin
      Append (Raw.Bound, Position);
      Append (Raw.Raw_Frame, Position);
      Append (Raw.Raw_Sender, Position);
      Append (Raw.Ticket, Position);
      Append (Raw.Raw_Proc_Status, Position);
      Append (Raw.Raw_Proc_Cgroup, Position);
      Append (Raw.Raw_Proc_Maps, Position);
      Append (Raw.Raw_Proc_Cmdline, Position);
      Append (Raw.Raw_Pidfd_Info, Position);
      Append (Raw.Namespace, Position);
      Append (Raw.Held_Namespace, Position);
      Append (Raw.Helper_Image, Position);
      Append (Raw.Expected_Helper_Image, Position);
      Append (Raw.Executable_Plan, Position);
      Append (Raw.Expected_Executable_Plan, Position);
      Append (Raw.Original_Requester, Position);
      Append (Raw.Requester_Credentials, Position);
      Append (Raw.Expected_Requester_Credentials, Position);
      Append (Raw.Dispatch, Position);
      Append (Raw.Running_Event, Position);
      Append (Raw.Expected_Running_Event, Position);
      Append (Raw.Canonical_Use_Event, Position);
      Append (Raw.Expected_Canonical_Use_Event, Position);
      Append (Raw.Store_Genesis, Position);
      Append (Raw.Expected_Store_Genesis, Position);
      Append (Raw.Source_Lease, Position);
      Append (Raw.Expected_Source_Lease, Position);
      Append (Raw.Actor_Wait, Position);
      Append (Raw.Helper_Wait, Position);
      Append (Raw.Namespace_Wait, Position);
      Append (Raw.Host_Pid, Position);
      Append (Raw.Namespace_Pid, Position);
      Append (Raw.Sender_Uid, Position);
      Append (Raw.Sender_Gid, Position);
      Append (Raw.Real_Uid, Position);
      Append (Raw.Effective_Uid, Position);
      Append (Raw.Saved_Uid, Position);
      Append (Raw.Real_Gid, Position);
      Append (Raw.Effective_Gid, Position);
      Append (Raw.Saved_Gid, Position);
      Append (Raw.Capability_Version, Position);
      Append (Raw.Effective_Low, Position);
      Append (Raw.Permitted_Low, Position);
      Append (Raw.Inheritable_Low, Position);
      Append (Raw.Effective_High, Position);
      Append (Raw.Permitted_High, Position);
      Append (Raw.Inheritable_High, Position);
      Append (Raw.Securebits, Position);
      Append (Raw.No_New_Privs, Position);
      Append (Raw.Requester_Uid, Position);
      Append (Raw.Requester_Gid, Position);
      Append (Raw.Configured_Requester_Uid, Position);
      Append (Raw.Workload_Uid, Position);
      Append (Raw.Workload_Gid, Position);
      Append (Raw.Proc_Host_Pid, Position);
      Append (Raw.Proc_Namespace_Pid, Position);
      Append (Raw.Proc_Real_Uid, Position);
      Append (Raw.Proc_Effective_Uid, Position);
      Append (Raw.Proc_Saved_Uid, Position);
      Append (Raw.Proc_Real_Gid, Position);
      Append (Raw.Proc_Effective_Gid, Position);
      Append (Raw.Proc_Saved_Gid, Position);
      Append (Raw.Proc_Effective, Position);
      Append (Raw.Proc_Permitted, Position);
      Append (Raw.Proc_Inheritable, Position);
      Append (Raw.Proc_Bounding, Position);
      Append (Raw.Proc_Ambient, Position);
      Append (Raw.Proc_No_New_Privs, Position);
      Append (Raw.Proc_Fs_Uid, Position);
      Append (Raw.Proc_Fs_Gid, Position);
   end Append;
   procedure Append (Raw : D.Raw_Packet; Position : in out Cursor) is
   begin
      Append (Raw.Ledger, Position);
      Append (Raw.Captured, Position);
   end Append;
   procedure Append (Raw : HC.Raw_Input; Position : in out Cursor) is
   begin
      Append (Raw.Historical, Position);
      Append (Raw.Current, Position);
   end Append;
   procedure Append (Raw : N.Raw_Bucket; Position : in out Cursor) is
   begin
      Append (Raw.Key, Position);
      Append (Raw.Capacity, Position);
      Append (Raw.Held_Total, Position);
      Append (Raw.Charged_Total, Position);
      Append (Raw.Capacity_Source, Position);
      Append (Raw.Catalogue_Head, Position);
      Append (Raw.Observation_Head, Position);
   end Append;
   procedure Append (Raw : N.Raw_Current_Observation; Position : in out Cursor) is
   begin
      Append (Raw.Scope, Position);
      Append (Raw.Resource_Epoch, Position);
      Append (Raw.Universe_Head, Position);
      Append (Raw.Ledger_Head, Position);
      Append (Raw.History_Head, Position);
      Append (Raw.Physical_Head, Position);
      Append (Raw.Store_Genesis, Position);
      Append (Raw.Store_Id, Position);
      Append (Raw.Root_Head, Position);
      Append (Raw.Prime, Position);
      Append (Raw.Root_Count, Position);
      Append (Raw.Cause, Position);
      Append (Raw.Requester, Position);
      Append (Raw.Receipt, Position);
      Append (Raw.Catalogue_Head, Position);
      Append (Raw.Observation_Head, Position);
   end Append;
   procedure Append (Raw : N.Raw_Intent; Position : in out Cursor) is
   begin
      Append (Raw.Original, Position);
      Append (Raw.Expected_Epoch, Position);
      Append (Raw.Expected_Ledger_Head, Position);
      Append (Raw.Request_Id, Position);
      Append (Raw.Cause, Position);
      Append (Raw.Requester, Position);
      Append (Raw.Receipt, Position);
   end Append;
   procedure Append (Raw : N.Raw_Packet; Position : in out Cursor) is
   begin
      Append (Raw.Before_State, Position);
      Append (Raw.Proposed_State, Position);
      Append (Raw.Current, Position);
      Append (Raw.Request, Position);
   end Append;
   procedure Append (Raw : N.Raw_Physical_Key; Position : in out Cursor) is
   begin
      Append (Raw.Machine, Position);
      Append (Raw.Resource, Position);
      Append (Raw.Unit, Position);
   end Append;
   procedure Append (Raw : N.Raw_Projection; Position : in out Cursor) is
   begin
      Append (Raw.Key, Position);
      Append (Raw.Bound, Position);
      Append (Raw.Origin, Position);
      Append (Raw.Catalogue_Head, Position);
      Append (Raw.Numerator, Position);
      Append (Raw.Denominator, Position);
      Append (Raw.Amount, Position);
   end Append;
   procedure Append (Raw : N.Raw_Scope_Frame; Position : in out Cursor) is
   begin
      Append (Raw.Scope, Position);
      Append (Raw.First_Epoch, Position);
      Append (Raw.Universe_Head, Position);
      Append (Raw.Frame_Head, Position);
      Append (Raw.Prior_Frame, Position);
      Append (Raw.Store_Genesis, Position);
      Append (Raw.Store_Id, Position);
      Append (Raw.Root_Head, Position);
      Append (Raw.Prime, Position);
      Append (Raw.Root_Count, Position);
      Append (Raw.Cause, Position);
      Append (Raw.Requester, Position);
      Append (Raw.Receipt, Position);
      Append (Raw.Catalogue_Head, Position);
      Append (Raw.Observation_Head, Position);
   end Append;
   procedure Append (Raw : N.Raw_State; Position : in out Cursor) is
   begin
      Append (Raw.Current, Position);
      Append (Raw.Resource_Epoch, Position);
      Append (Raw.Universe_Head, Position);
      Append (Raw.Ledger_Head, Position);
      Append (Raw.History_Head, Position);
      Append (Raw.Physical_Head, Position);
   end Append;
   procedure Append (Raw : O.Raw_Facts; Position : in out Cursor) is
   begin
      Append (Raw.Current, Position);
      Append (Raw.Current_Epoch, Position);
      Append (Raw.Retained, Position);
      Append (Raw.Current_Universe_Head, Position);
      Append (Raw.Current_Ledger_Head, Position);
      Append (Raw.Intent, Position);
      Append (Raw.Dispatch, Position);
      Append (Raw.Observation_Head, Position);
      Append (Raw.Actual_Unit, Position);
      Append (Raw.Cgroup, Position);
      Append (Raw.Invocation, Position);
      Append (Raw.Namespace, Position);
      Append (Raw.Held_Namespace, Position);
      Append (Raw.Peer, Position);
      Append (Raw.Held_Peer, Position);
      Append (Raw.Helper_Image, Position);
      Append (Raw.Expected_Helper_Image, Position);
      Append (Raw.Challenge, Position);
      Append (Raw.Held_Challenge, Position);
      Append (Raw.Protocol, Position);
      Append (Raw.Closed_Event, Position);
      Append (Raw.Namespace_Wait, Position);
      Append (Raw.Helper_Wait, Position);
      Append (Raw.Cgroup_Events, Position);
      Append (Raw.Cgroup_Type, Position);
      Append (Raw.Manager_Delegate, Position);
      Append (Raw.Cgroup_Owner, Position);
      Append (Raw.Cgroup_Group_Write, Position);
      Append (Raw.Cgroup_Other_Write, Position);
      Append (Raw.Actual_Store_Genesis, Position);
      Append (Raw.Actual_Store_Id, Position);
      Append (Raw.Owner_Store_Genesis, Position);
      Append (Raw.Owner_Store_Id, Position);
      Append (Raw.Genesis_Universe, Position);
      Append (Raw.Genesis_Instance, Position);
      Append (Raw.Genesis_Context_Head, Position);
      Append (Raw.Genesis_Prime, Position);
      Append (Raw.Genesis_Root_Count, Position);
   end Append;
   procedure Append (Raw : O.Raw_Input; Position : in out Cursor) is
   begin
      Append (Raw.State, Position);
      Append (Raw.Item, Position);
      Append (Raw.Captured, Position);
   end Append;
   procedure Append (Raw : RW.Raw_Binding; Position : in out Cursor) is
   begin
      Append (Raw.Policy_Epoch, Position);
      Append (Raw.Resource_Epoch, Position);
   end Append;
   procedure Append (Raw : RW.Raw_Epoch; Position : in out Cursor) is
   begin
      if Raw.Present > 1 or else (Raw.Present = 0 and then Raw.Length /= 0) then Position.Good := False; return; end if;
      Span (Raw.First, Raw.Length, True, Position);
   end Append;
   procedure Append (Raw : RW.Raw_Request; Position : in out Cursor) is
   begin
      Append (Raw.Issued_Binding, Position);
      Append (Raw.Recovered_Binding, Position);
   end Append;
   procedure Append (Raw : T.Raw_Binding; Position : in out Cursor) is
   begin
      Append (Raw.Policy_Epoch, Position);
      Append (Raw.Resource_Epoch, Position);
   end Append;
   procedure Append (Raw : T.Raw_Evidence; Position : in out Cursor) is
   begin
      Append (Raw.Recovery, Position);
      Append (Raw.Effect_Binding, Position);
      Append (Raw.No_Effect_Binding, Position);
      Append (Raw.Owner_Resolution, Position);
      Span (Raw.Effect_Material_First, Raw.Effect_Material_Length, True, Position);
   end Append;
   procedure Append (Raw : T.Raw_Grant; Position : in out Cursor) is
   begin
      Append (Raw.Epoch, Position);
      Append (Raw.Ceiling, Position);
      Append (Raw.Issued_At, Position);
      Append (Raw.Expires_At, Position);
   end Append;
   procedure Append (Raw : T.Raw_Input; Position : in out Cursor) is
   begin
      Append (Raw.Bound, Position);
      Append (Raw.Facts, Position);
      Append (Raw.Now, Position);
   end Append;
   procedure Append (Raw : T.Raw_Quantity; Position : in out Cursor) is
   begin
      if Raw.Present > 1 or else Raw.Negative > 1 then Position.Good := False; return; end if;
      if Raw.Present = 0 then
         if Raw.First /= 1 or else Raw.Length /= 0 or else Raw.Negative /= 0 then Position.Good := False; end if;
      else Span (Raw.First, Raw.Length, False, Position); end if;
   end Append;
   procedure Append (Raw : T.Raw_Use; Position : in out Cursor) is
   begin
      Append (Raw.Bound, Position);
   end Append;
   procedure Append (Raw : W.Raw_Binding; Position : in out Cursor) is
   begin
      Append (Raw.Reservation, Position);
      Append (Raw.Operation, Position);
      Append (Raw.Owner, Position);
      Append (Raw.Workload, Position);
      Append (Raw.Universe_Head, Position);
      Append (Raw.Capability, Position);
      Append (Raw.Grant_Use, Position);
      Append (Raw.Payload, Position);
      Append (Raw.Provenance, Position);
      Append (Raw.Resource_Epoch, Position);
   end Append;
   procedure Append (Raw : W.Raw_Context; Position : in out Cursor) is
   begin
      Append (Raw.Universe, Position);
      Append (Raw.Policy, Position);
      Append (Raw.Resource, Position);
      Append (Raw.Unit, Position);
      Append (Raw.Instance, Position);
      Append (Raw.Host, Position);
      Append (Raw.Boot, Position);
      Append (Raw.Authority, Position);
      Append (Raw.Policy_Epoch, Position);
   end Append;
   procedure Append (Raw : W.Raw_Epoch; Position : in out Cursor) is
   begin
      if Raw.Present > 1 or else (Raw.Present = 0 and then (Raw.Value.Length /= 0 or else Raw.Value.Negative /= 0)) then Position.Good := False; return; end if;
      Append (Raw.Value, Position);
   end Append;
   procedure Append (Raw : W.Raw_Id; Position : in out Cursor) is
   begin
      if Raw.Present > 1 or else (Raw.Present = 0 and then Raw.Length /= 0) then Position.Good := False; return; end if;
      Span (Raw.First, Raw.Length, True, Position);
   end Append;
   procedure Append (Raw : W.Raw_Native; Position : in out Cursor) is
   begin
      Append (Raw.Scope, Position);
      Append (Raw.Resource_Epoch, Position);
      Append (Raw.Bound, Position);
      Append (Raw.Actual_Unit, Position);
      Append (Raw.Cgroup, Position);
      Append (Raw.Invocation, Position);
      Append (Raw.Observation_Head, Position);
   end Append;
   procedure Append (Raw : W.Raw_Packet; Position : in out Cursor) is
   begin
      Append (Raw.Before_State, Position);
      Append (Raw.Proposed_State, Position);
      Append (Raw.Intent, Position);
   end Append;
   procedure Append (Raw : W.Raw_Quantity; Position : in out Cursor) is
   begin
      if Raw.Negative > 1 then Position.Good := False; return; end if;
      Span (Raw.First, Raw.Length, True, Position);
   end Append;
   procedure Append (Raw : W.Raw_Request; Position : in out Cursor) is
   begin
      Append (Raw.Scope, Position);
      Append (Raw.Expected_Epoch, Position);
      Append (Raw.Expected_Ledger_Head, Position);
      Append (Raw.Request_Id, Position);
      Append (Raw.Reservation, Position);
      Append (Raw.Operation_Id, Position);
      Append (Raw.Requester, Position);
      Append (Raw.Bound, Position);
      Append (Raw.New_Row, Position);
   end Append;
   procedure Append (Raw : W.Raw_Row; Position : in out Cursor) is
   begin
      Append (Raw.Scope, Position);
      Append (Raw.Bound, Position);
      Append (Raw.Parent, Position);
      Append (Raw.Amount, Position);
      Append (Raw.Observed_Usage, Position);
      Append (Raw.Planned_Unit, Position);
      Append (Raw.Actual_Unit, Position);
      Append (Raw.Cgroup, Position);
      Append (Raw.Invocation, Position);
   end Append;
   procedure Append (Raw : W.Raw_State; Position : in out Cursor) is
   begin
      Append (Raw.Scope, Position);
      Append (Raw.Resource_Epoch, Position);
      Append (Raw.Universe_Head, Position);
      Append (Raw.Ledger_Head, Position);
      Append (Raw.Capacity, Position);
      Append (Raw.Held_Total, Position);
      Append (Raw.Charged_Total, Position);
   end Append;
   procedure Append (Raw : X.Raw_Crosswalk; Position : in out Cursor) is
   begin
      Append (Raw.Resource_Current, Position);
      Append (Raw.Owner_Genesis, Position);
      Append (Raw.Installation, Position);
      Append (Raw.Gate_Config, Position);
      Append (Raw.Managed_Observation, Position);
      Append (Raw.Original_Grant, Position);
      Append (Raw.Complete_Crosswalk, Position);
      Append (Raw.Current_Source, Position);
      Append (Raw.Original_Request, Position);
      Append (Raw.Original_Requester, Position);
      Append (Raw.Original_Transaction, Position);
      Append (Raw.Preparer, Position);
      Append (Raw.Selected_Plan, Position);
   end Append;
   procedure Append (Raw : Y.Raw_Controller; Position : in out Cursor) is
   begin
      Append (Raw.Bound, Position);
      Append (Raw.Process, Position);
      Append (Raw.Requester_Uid, Position);
      Append (Raw.Requester_Gid, Position);
      Append (Raw.raw_manager, Position);
      Append (Raw.raw_channel, Position);
      Append (Raw.owner_endpoint, Position);
      Append (Raw.expected_owner_endpoint, Position);
      Append (Raw.source_lease, Position);
      Append (Raw.expected_source_lease, Position);
      Append (Raw.worker_image, Position);
      Append (Raw.expected_worker_image, Position);
      Append (Raw.handler_plan, Position);
      Append (Raw.expected_handler_plan, Position);
      Append (Raw.raw_request, Position);
      Append (Raw.requester, Position);
      Append (Raw.dispatch, Position);
      Append (Raw.running_event, Position);
      Append (Raw.expected_running_event, Position);
      Append (Raw.store_genesis, Position);
      Append (Raw.expected_store_genesis, Position);
      Append (Raw.current_source, Position);
   end Append;
   procedure Append (Raw : Y.Raw_Input; Position : in out Cursor) is
   begin
      Append (Raw.Controller, Position);
      Append (Raw.Child_Task, Position);
   end Append;
   procedure Append (Raw : Y.Raw_Namespace; Position : in out Cursor) is
   begin
      Append (Raw.identity, Position);
      Append (Raw.parent, Position);
      Append (Raw.raw_nsfs, Position);
      Append (Raw.raw_get_parent, Position);
      Append (Raw.source_lease, Position);
   end Append;
   procedure Append (Raw : Y.Raw_Process; Position : in out Cursor) is
   begin
      Append (Raw.raw_status, Position);
      Append (Raw.raw_stat, Position);
      Append (Raw.raw_cgroup, Position);
      Append (Raw.raw_maps, Position);
      Append (Raw.raw_cmdline, Position);
      Append (Raw.raw_pidfd_info, Position);
      Append (Raw.namespace, Position);
      Append (Raw.cgroup, Position);
      Append (Raw.actual_unit, Position);
      Append (Raw.invocation, Position);
      Append (Raw.source_lease, Position);
      Append (Raw.pidfd_wait, Position);
      Append (Raw.host_pid, Position);
      Append (Raw.start_tick, Position);
      Append (Raw.parent_pid, Position);
      Append (Raw.parent_start_tick, Position);
      Append (Raw.real_uid, Position);
      Append (Raw.effective_uid, Position);
      Append (Raw.saved_uid, Position);
      Append (Raw.real_gid, Position);
      Append (Raw.effective_gid, Position);
      Append (Raw.saved_gid, Position);
   end Append;
   procedure Append (Raw : Y.Raw_Task; Position : in out Cursor) is
   begin
      Append (Raw.Root, Position);
      Append (Raw.Child, Position);
      Append (Raw.task_id, Position);
      Append (Raw.root_world, Position);
      Append (Raw.child_world, Position);
      Append (Raw.root_instance, Position);
      Append (Raw.child_instance, Position);
      Append (Raw.world_store, Position);
      Append (Raw.full_world_ancestry, Position);
      Append (Raw.original_workload, Position);
      Append (Raw.sandbox, Position);
      Append (Raw.adapter, Position);
      Append (Raw.context, Position);
      Append (Raw.mission, Position);
      Append (Raw.stdin, Position);
      Append (Raw.credential_source, Position);
      Append (Raw.executable_source, Position);
      Append (Raw.configuration, Position);
      Append (Raw.owner_plan, Position);
      Append (Raw.native_cost_input, Position);
      Append (Raw.raw_request, Position);
      Append (Raw.requester, Position);
      Append (Raw.cause, Position);
      Append (Raw.root_dispatch, Position);
      Append (Raw.root_running_event, Position);
      Append (Raw.task_journal, Position);
      Append (Raw.task_intent, Position);
      Append (Raw.task_reservation_event, Position);
      Append (Raw.task_launch_event, Position);
      Append (Raw.parent_namespace_source, Position);
      Append (Raw.fd_lineage, Position);
      Append (Raw.source_lease, Position);
   end Append;
   function Empty (Raw : W.Raw_Id) return Boolean is
     (Raw.Present = 0
      and then Raw.First = 1
      and then Raw.Length = 0);
   function Empty (Raw : W.Raw_Quantity) return Boolean is
     (Raw.Negative = 0
      and then Raw.First = 1
      and then Raw.Length = 0);
   function Empty (Raw : W.Raw_Epoch) return Boolean is
     (Raw.Present = 0
      and then Empty (Raw.Value));
   function Empty (Raw : W.Raw_Context) return Boolean is
     (Empty (Raw.Universe)
      and then Empty (Raw.Policy)
      and then Empty (Raw.Resource)
      and then Empty (Raw.Unit)
      and then Empty (Raw.Instance)
      and then Empty (Raw.Host)
      and then Empty (Raw.Boot)
      and then Empty (Raw.Authority)
      and then Empty (Raw.Policy_Epoch));
   function Empty (Raw : W.Raw_Binding) return Boolean is
     (Empty (Raw.Reservation)
      and then Empty (Raw.Operation)
      and then Empty (Raw.Owner)
      and then Empty (Raw.Workload)
      and then Empty (Raw.Universe_Head)
      and then Empty (Raw.Capability)
      and then Empty (Raw.Grant_Use)
      and then Empty (Raw.Payload)
      and then Empty (Raw.Provenance)
      and then Empty (Raw.Resource_Epoch));
   function Unused_Row (Raw : W.Raw_Row) return Boolean is
     (Empty (Raw.Scope)
      and then Empty (Raw.Bound)
      and then Empty (Raw.Parent)
      and then Raw.Kind = 0
      and then Raw.State = 0
      and then Empty (Raw.Amount)
      and then Empty (Raw.Observed_Usage)
      and then Empty (Raw.Planned_Unit)
      and then Empty (Raw.Actual_Unit)
      and then Empty (Raw.Cgroup)
      and then Empty (Raw.Invocation));
end Worldline.Retained_Source_Layout;
