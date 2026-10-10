package body Worldline.Retained_Raw_Decode with SPARK_Mode is
   use type Interfaces.Unsigned_64;
   use type Interfaces.Integer_64;
   use type Q.Byte;
   function Little_Endian (Data : Q.Byte_Array) return Interfaces.Unsigned_64
     with Global => null, Pre => Data'Length <= Interfaces.Unsigned_64'Size / System.Storage_Unit
   is
      Result : Interfaces.Unsigned_64 := 0;
   begin
      for I in reverse Data'Range loop
         Result := Interfaces.Shift_Left (Result, System.Storage_Unit) or Interfaces.Unsigned_64 (Data (I));
      end loop;
      return Result;
   end Little_Endian;
   function Signed (Data : Q.Byte_Array) return Interfaces.Integer_64
     with Global => null, Pre => Data'Length = Interfaces.Integer_64'Size / System.Storage_Unit
   is
      V : constant Interfaces.Unsigned_64 := Little_Endian (Data);
   begin
      if V <= Interfaces.Unsigned_64 (Interfaces.Integer_64'Last) then
         return Interfaces.Integer_64 (V);
      else
         return -Interfaces.Integer_64 (Interfaces.Unsigned_64'Last - V) - 1;
      end if;
   end Signed;
   function Load (Data : Q.Byte_Array) return D.Raw_Packet is
      Result : D.Raw_Packet;
   begin
      Result.Ledger := Load (Data (Data'First + Result.Ledger'Position .. Data'First + Result.Ledger'Position + Result.Ledger'Size / System.Storage_Unit - 1));
      Result.Captured := Load (Data (Data'First + Result.Captured'Position .. Data'First + Result.Captured'Position + Result.Captured'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Packet is
      Result : N.Raw_Packet;
   begin
      Result.Schema_Version := Interfaces.Unsigned_32 (Little_Endian (Data (Data'First + Result.Schema_Version'Position .. Data'First + Result.Schema_Version'Position + Result.Schema_Version'Size / System.Storage_Unit - 1)));
      Result.Before_State := Load (Data (Data'First + Result.Before_State'Position .. Data'First + Result.Before_State'Position + Result.Before_State'Size / System.Storage_Unit - 1));
      Result.Proposed_State := Load (Data (Data'First + Result.Proposed_State'Position .. Data'First + Result.Proposed_State'Position + Result.Proposed_State'Size / System.Storage_Unit - 1));
      Result.Current := Load (Data (Data'First + Result.Current'Position .. Data'First + Result.Current'Position + Result.Current'Size / System.Storage_Unit - 1));
      Result.Request := Load (Data (Data'First + Result.Request'Position .. Data'First + Result.Request'Position + Result.Request'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_State is
      Result : N.Raw_State;
   begin
      Result.Current := Load (Data (Data'First + Result.Current'Position .. Data'First + Result.Current'Position + Result.Current'Size / System.Storage_Unit - 1));
      Result.Resource_Epoch := Load (Data (Data'First + Result.Resource_Epoch'Position .. Data'First + Result.Resource_Epoch'Position + Result.Resource_Epoch'Size / System.Storage_Unit - 1));
      Result.Universe_Head := Load (Data (Data'First + Result.Universe_Head'Position .. Data'First + Result.Universe_Head'Position + Result.Universe_Head'Size / System.Storage_Unit - 1));
      Result.Ledger_Head := Load (Data (Data'First + Result.Ledger_Head'Position .. Data'First + Result.Ledger_Head'Position + Result.Ledger_Head'Size / System.Storage_Unit - 1));
      Result.History_Head := Load (Data (Data'First + Result.History_Head'Position .. Data'First + Result.History_Head'Position + Result.History_Head'Size / System.Storage_Unit - 1));
      Result.Physical_Head := Load (Data (Data'First + Result.Physical_Head'Position .. Data'First + Result.Physical_Head'Position + Result.Physical_Head'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Context is
      Result : W.Raw_Context;
   begin
      Result.Universe := Load (Data (Data'First + Result.Universe'Position .. Data'First + Result.Universe'Position + Result.Universe'Size / System.Storage_Unit - 1));
      Result.Policy := Load (Data (Data'First + Result.Policy'Position .. Data'First + Result.Policy'Position + Result.Policy'Size / System.Storage_Unit - 1));
      Result.Resource := Load (Data (Data'First + Result.Resource'Position .. Data'First + Result.Resource'Position + Result.Resource'Size / System.Storage_Unit - 1));
      Result.Unit := Load (Data (Data'First + Result.Unit'Position .. Data'First + Result.Unit'Position + Result.Unit'Size / System.Storage_Unit - 1));
      Result.Instance := Load (Data (Data'First + Result.Instance'Position .. Data'First + Result.Instance'Position + Result.Instance'Size / System.Storage_Unit - 1));
      Result.Host := Load (Data (Data'First + Result.Host'Position .. Data'First + Result.Host'Position + Result.Host'Size / System.Storage_Unit - 1));
      Result.Boot := Load (Data (Data'First + Result.Boot'Position .. Data'First + Result.Boot'Position + Result.Boot'Size / System.Storage_Unit - 1));
      Result.Authority := Load (Data (Data'First + Result.Authority'Position .. Data'First + Result.Authority'Position + Result.Authority'Size / System.Storage_Unit - 1));
      Result.Policy_Epoch := Load (Data (Data'First + Result.Policy_Epoch'Position .. Data'First + Result.Policy_Epoch'Position + Result.Policy_Epoch'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Id is
      Result : W.Raw_Id;
   begin
      Result.Present := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Present'Position .. Data'First + Result.Present'Position + Result.Present'Size / System.Storage_Unit - 1)));
      Result.First := Signed (Data (Data'First + Result.First'Position .. Data'First + Result.First'Position + Result.First'Size / System.Storage_Unit - 1));
      Result.Length := Signed (Data (Data'First + Result.Length'Position .. Data'First + Result.Length'Position + Result.Length'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Epoch is
      Result : W.Raw_Epoch;
   begin
      Result.Present := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Present'Position .. Data'First + Result.Present'Position + Result.Present'Size / System.Storage_Unit - 1)));
      Result.Value := Load (Data (Data'First + Result.Value'Position .. Data'First + Result.Value'Position + Result.Value'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Quantity is
      Result : W.Raw_Quantity;
   begin
      Result.Negative := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Negative'Position .. Data'First + Result.Negative'Position + Result.Negative'Size / System.Storage_Unit - 1)));
      Result.First := Signed (Data (Data'First + Result.First'Position .. Data'First + Result.First'Position + Result.First'Size / System.Storage_Unit - 1));
      Result.Length := Signed (Data (Data'First + Result.Length'Position .. Data'First + Result.Length'Position + Result.Length'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Current_Observation is
      Result : N.Raw_Current_Observation;
   begin
      Result.Scope := Load (Data (Data'First + Result.Scope'Position .. Data'First + Result.Scope'Position + Result.Scope'Size / System.Storage_Unit - 1));
      Result.Resource_Epoch := Load (Data (Data'First + Result.Resource_Epoch'Position .. Data'First + Result.Resource_Epoch'Position + Result.Resource_Epoch'Size / System.Storage_Unit - 1));
      Result.Universe_Head := Load (Data (Data'First + Result.Universe_Head'Position .. Data'First + Result.Universe_Head'Position + Result.Universe_Head'Size / System.Storage_Unit - 1));
      Result.Ledger_Head := Load (Data (Data'First + Result.Ledger_Head'Position .. Data'First + Result.Ledger_Head'Position + Result.Ledger_Head'Size / System.Storage_Unit - 1));
      Result.History_Head := Load (Data (Data'First + Result.History_Head'Position .. Data'First + Result.History_Head'Position + Result.History_Head'Size / System.Storage_Unit - 1));
      Result.Physical_Head := Load (Data (Data'First + Result.Physical_Head'Position .. Data'First + Result.Physical_Head'Position + Result.Physical_Head'Size / System.Storage_Unit - 1));
      Result.Store_Genesis := Load (Data (Data'First + Result.Store_Genesis'Position .. Data'First + Result.Store_Genesis'Position + Result.Store_Genesis'Size / System.Storage_Unit - 1));
      Result.Store_Id := Load (Data (Data'First + Result.Store_Id'Position .. Data'First + Result.Store_Id'Position + Result.Store_Id'Size / System.Storage_Unit - 1));
      Result.Root_Head := Load (Data (Data'First + Result.Root_Head'Position .. Data'First + Result.Root_Head'Position + Result.Root_Head'Size / System.Storage_Unit - 1));
      Result.Prime := Load (Data (Data'First + Result.Prime'Position .. Data'First + Result.Prime'Position + Result.Prime'Size / System.Storage_Unit - 1));
      Result.Root_Count := Load (Data (Data'First + Result.Root_Count'Position .. Data'First + Result.Root_Count'Position + Result.Root_Count'Size / System.Storage_Unit - 1));
      Result.Cause := Load (Data (Data'First + Result.Cause'Position .. Data'First + Result.Cause'Position + Result.Cause'Size / System.Storage_Unit - 1));
      Result.Requester := Load (Data (Data'First + Result.Requester'Position .. Data'First + Result.Requester'Position + Result.Requester'Size / System.Storage_Unit - 1));
      Result.Receipt := Load (Data (Data'First + Result.Receipt'Position .. Data'First + Result.Receipt'Position + Result.Receipt'Size / System.Storage_Unit - 1));
      Result.Catalogue_Head := Load (Data (Data'First + Result.Catalogue_Head'Position .. Data'First + Result.Catalogue_Head'Position + Result.Catalogue_Head'Size / System.Storage_Unit - 1));
      Result.Observation_Head := Load (Data (Data'First + Result.Observation_Head'Position .. Data'First + Result.Observation_Head'Position + Result.Observation_Head'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Intent is
      Result : N.Raw_Intent;
   begin
      Result.Kind := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Kind'Position .. Data'First + Result.Kind'Position + Result.Kind'Size / System.Storage_Unit - 1)));
      Result.Original := Load (Data (Data'First + Result.Original'Position .. Data'First + Result.Original'Position + Result.Original'Size / System.Storage_Unit - 1));
      Result.Expected_Epoch := Load (Data (Data'First + Result.Expected_Epoch'Position .. Data'First + Result.Expected_Epoch'Position + Result.Expected_Epoch'Size / System.Storage_Unit - 1));
      Result.Expected_Ledger_Head := Load (Data (Data'First + Result.Expected_Ledger_Head'Position .. Data'First + Result.Expected_Ledger_Head'Position + Result.Expected_Ledger_Head'Size / System.Storage_Unit - 1));
      Result.Request_Id := Load (Data (Data'First + Result.Request_Id'Position .. Data'First + Result.Request_Id'Position + Result.Request_Id'Size / System.Storage_Unit - 1));
      Result.Cause := Load (Data (Data'First + Result.Cause'Position .. Data'First + Result.Cause'Position + Result.Cause'Size / System.Storage_Unit - 1));
      Result.Requester := Load (Data (Data'First + Result.Requester'Position .. Data'First + Result.Requester'Position + Result.Requester'Size / System.Storage_Unit - 1));
      Result.Receipt := Load (Data (Data'First + Result.Receipt'Position .. Data'First + Result.Receipt'Position + Result.Receipt'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Request is
      Result : W.Raw_Request;
   begin
      Result.Kind := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Kind'Position .. Data'First + Result.Kind'Position + Result.Kind'Size / System.Storage_Unit - 1)));
      Result.Scope := Load (Data (Data'First + Result.Scope'Position .. Data'First + Result.Scope'Position + Result.Scope'Size / System.Storage_Unit - 1));
      Result.Expected_Epoch := Load (Data (Data'First + Result.Expected_Epoch'Position .. Data'First + Result.Expected_Epoch'Position + Result.Expected_Epoch'Size / System.Storage_Unit - 1));
      Result.Expected_Ledger_Head := Load (Data (Data'First + Result.Expected_Ledger_Head'Position .. Data'First + Result.Expected_Ledger_Head'Position + Result.Expected_Ledger_Head'Size / System.Storage_Unit - 1));
      Result.Request_Id := Load (Data (Data'First + Result.Request_Id'Position .. Data'First + Result.Request_Id'Position + Result.Request_Id'Size / System.Storage_Unit - 1));
      Result.Reservation := Load (Data (Data'First + Result.Reservation'Position .. Data'First + Result.Reservation'Position + Result.Reservation'Size / System.Storage_Unit - 1));
      Result.Operation_Id := Load (Data (Data'First + Result.Operation_Id'Position .. Data'First + Result.Operation_Id'Position + Result.Operation_Id'Size / System.Storage_Unit - 1));
      Result.Requester := Load (Data (Data'First + Result.Requester'Position .. Data'First + Result.Requester'Position + Result.Requester'Size / System.Storage_Unit - 1));
      Result.Bound := Load (Data (Data'First + Result.Bound'Position .. Data'First + Result.Bound'Position + Result.Bound'Size / System.Storage_Unit - 1));
      Result.New_Row := Load (Data (Data'First + Result.New_Row'Position .. Data'First + Result.New_Row'Position + Result.New_Row'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Binding is
      Result : W.Raw_Binding;
   begin
      Result.Reservation := Load (Data (Data'First + Result.Reservation'Position .. Data'First + Result.Reservation'Position + Result.Reservation'Size / System.Storage_Unit - 1));
      Result.Operation := Load (Data (Data'First + Result.Operation'Position .. Data'First + Result.Operation'Position + Result.Operation'Size / System.Storage_Unit - 1));
      Result.Owner := Load (Data (Data'First + Result.Owner'Position .. Data'First + Result.Owner'Position + Result.Owner'Size / System.Storage_Unit - 1));
      Result.Workload := Load (Data (Data'First + Result.Workload'Position .. Data'First + Result.Workload'Position + Result.Workload'Size / System.Storage_Unit - 1));
      Result.Universe_Head := Load (Data (Data'First + Result.Universe_Head'Position .. Data'First + Result.Universe_Head'Position + Result.Universe_Head'Size / System.Storage_Unit - 1));
      Result.Capability := Load (Data (Data'First + Result.Capability'Position .. Data'First + Result.Capability'Position + Result.Capability'Size / System.Storage_Unit - 1));
      Result.Grant_Use := Load (Data (Data'First + Result.Grant_Use'Position .. Data'First + Result.Grant_Use'Position + Result.Grant_Use'Size / System.Storage_Unit - 1));
      Result.Payload := Load (Data (Data'First + Result.Payload'Position .. Data'First + Result.Payload'Position + Result.Payload'Size / System.Storage_Unit - 1));
      Result.Provenance := Load (Data (Data'First + Result.Provenance'Position .. Data'First + Result.Provenance'Position + Result.Provenance'Size / System.Storage_Unit - 1));
      Result.Resource_Epoch := Load (Data (Data'First + Result.Resource_Epoch'Position .. Data'First + Result.Resource_Epoch'Position + Result.Resource_Epoch'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Row is
      Result : W.Raw_Row;
   begin
      Result.Scope := Load (Data (Data'First + Result.Scope'Position .. Data'First + Result.Scope'Position + Result.Scope'Size / System.Storage_Unit - 1));
      Result.Bound := Load (Data (Data'First + Result.Bound'Position .. Data'First + Result.Bound'Position + Result.Bound'Size / System.Storage_Unit - 1));
      Result.Parent := Load (Data (Data'First + Result.Parent'Position .. Data'First + Result.Parent'Position + Result.Parent'Size / System.Storage_Unit - 1));
      Result.Kind := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Kind'Position .. Data'First + Result.Kind'Position + Result.Kind'Size / System.Storage_Unit - 1)));
      Result.State := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.State'Position .. Data'First + Result.State'Position + Result.State'Size / System.Storage_Unit - 1)));
      Result.Amount := Load (Data (Data'First + Result.Amount'Position .. Data'First + Result.Amount'Position + Result.Amount'Size / System.Storage_Unit - 1));
      Result.Observed_Usage := Load (Data (Data'First + Result.Observed_Usage'Position .. Data'First + Result.Observed_Usage'Position + Result.Observed_Usage'Size / System.Storage_Unit - 1));
      Result.Planned_Unit := Load (Data (Data'First + Result.Planned_Unit'Position .. Data'First + Result.Planned_Unit'Position + Result.Planned_Unit'Size / System.Storage_Unit - 1));
      Result.Actual_Unit := Load (Data (Data'First + Result.Actual_Unit'Position .. Data'First + Result.Actual_Unit'Position + Result.Actual_Unit'Size / System.Storage_Unit - 1));
      Result.Cgroup := Load (Data (Data'First + Result.Cgroup'Position .. Data'First + Result.Cgroup'Position + Result.Cgroup'Size / System.Storage_Unit - 1));
      Result.Invocation := Load (Data (Data'First + Result.Invocation'Position .. Data'First + Result.Invocation'Position + Result.Invocation'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return D.Raw_Observation is
      Result : D.Raw_Observation;
   begin
      Result.Bound := Load (Data (Data'First + Result.Bound'Position .. Data'First + Result.Bound'Position + Result.Bound'Size / System.Storage_Unit - 1));
      Result.Raw_Frame := Load (Data (Data'First + Result.Raw_Frame'Position .. Data'First + Result.Raw_Frame'Position + Result.Raw_Frame'Size / System.Storage_Unit - 1));
      Result.Raw_Sender := Load (Data (Data'First + Result.Raw_Sender'Position .. Data'First + Result.Raw_Sender'Position + Result.Raw_Sender'Size / System.Storage_Unit - 1));
      Result.Ticket := Load (Data (Data'First + Result.Ticket'Position .. Data'First + Result.Ticket'Position + Result.Ticket'Size / System.Storage_Unit - 1));
      Result.Raw_Proc_Status := Load (Data (Data'First + Result.Raw_Proc_Status'Position .. Data'First + Result.Raw_Proc_Status'Position + Result.Raw_Proc_Status'Size / System.Storage_Unit - 1));
      Result.Raw_Proc_Cgroup := Load (Data (Data'First + Result.Raw_Proc_Cgroup'Position .. Data'First + Result.Raw_Proc_Cgroup'Position + Result.Raw_Proc_Cgroup'Size / System.Storage_Unit - 1));
      Result.Raw_Proc_Maps := Load (Data (Data'First + Result.Raw_Proc_Maps'Position .. Data'First + Result.Raw_Proc_Maps'Position + Result.Raw_Proc_Maps'Size / System.Storage_Unit - 1));
      Result.Raw_Proc_Cmdline := Load (Data (Data'First + Result.Raw_Proc_Cmdline'Position .. Data'First + Result.Raw_Proc_Cmdline'Position + Result.Raw_Proc_Cmdline'Size / System.Storage_Unit - 1));
      Result.Raw_Pidfd_Info := Load (Data (Data'First + Result.Raw_Pidfd_Info'Position .. Data'First + Result.Raw_Pidfd_Info'Position + Result.Raw_Pidfd_Info'Size / System.Storage_Unit - 1));
      Result.Namespace := Load (Data (Data'First + Result.Namespace'Position .. Data'First + Result.Namespace'Position + Result.Namespace'Size / System.Storage_Unit - 1));
      Result.Held_Namespace := Load (Data (Data'First + Result.Held_Namespace'Position .. Data'First + Result.Held_Namespace'Position + Result.Held_Namespace'Size / System.Storage_Unit - 1));
      Result.Helper_Image := Load (Data (Data'First + Result.Helper_Image'Position .. Data'First + Result.Helper_Image'Position + Result.Helper_Image'Size / System.Storage_Unit - 1));
      Result.Expected_Helper_Image := Load (Data (Data'First + Result.Expected_Helper_Image'Position .. Data'First + Result.Expected_Helper_Image'Position + Result.Expected_Helper_Image'Size / System.Storage_Unit - 1));
      Result.Executable_Plan := Load (Data (Data'First + Result.Executable_Plan'Position .. Data'First + Result.Executable_Plan'Position + Result.Executable_Plan'Size / System.Storage_Unit - 1));
      Result.Expected_Executable_Plan := Load (Data (Data'First + Result.Expected_Executable_Plan'Position .. Data'First + Result.Expected_Executable_Plan'Position + Result.Expected_Executable_Plan'Size / System.Storage_Unit - 1));
      Result.Original_Requester := Load (Data (Data'First + Result.Original_Requester'Position .. Data'First + Result.Original_Requester'Position + Result.Original_Requester'Size / System.Storage_Unit - 1));
      Result.Requester_Credentials := Load (Data (Data'First + Result.Requester_Credentials'Position .. Data'First + Result.Requester_Credentials'Position + Result.Requester_Credentials'Size / System.Storage_Unit - 1));
      Result.Expected_Requester_Credentials := Load (Data (Data'First + Result.Expected_Requester_Credentials'Position .. Data'First + Result.Expected_Requester_Credentials'Position + Result.Expected_Requester_Credentials'Size / System.Storage_Unit - 1));
      Result.Dispatch := Load (Data (Data'First + Result.Dispatch'Position .. Data'First + Result.Dispatch'Position + Result.Dispatch'Size / System.Storage_Unit - 1));
      Result.Running_Event := Load (Data (Data'First + Result.Running_Event'Position .. Data'First + Result.Running_Event'Position + Result.Running_Event'Size / System.Storage_Unit - 1));
      Result.Expected_Running_Event := Load (Data (Data'First + Result.Expected_Running_Event'Position .. Data'First + Result.Expected_Running_Event'Position + Result.Expected_Running_Event'Size / System.Storage_Unit - 1));
      Result.Canonical_Use_Event := Load (Data (Data'First + Result.Canonical_Use_Event'Position .. Data'First + Result.Canonical_Use_Event'Position + Result.Canonical_Use_Event'Size / System.Storage_Unit - 1));
      Result.Expected_Canonical_Use_Event := Load (Data (Data'First + Result.Expected_Canonical_Use_Event'Position .. Data'First + Result.Expected_Canonical_Use_Event'Position + Result.Expected_Canonical_Use_Event'Size / System.Storage_Unit - 1));
      Result.Store_Genesis := Load (Data (Data'First + Result.Store_Genesis'Position .. Data'First + Result.Store_Genesis'Position + Result.Store_Genesis'Size / System.Storage_Unit - 1));
      Result.Expected_Store_Genesis := Load (Data (Data'First + Result.Expected_Store_Genesis'Position .. Data'First + Result.Expected_Store_Genesis'Position + Result.Expected_Store_Genesis'Size / System.Storage_Unit - 1));
      Result.Source_Lease := Load (Data (Data'First + Result.Source_Lease'Position .. Data'First + Result.Source_Lease'Position + Result.Source_Lease'Size / System.Storage_Unit - 1));
      Result.Expected_Source_Lease := Load (Data (Data'First + Result.Expected_Source_Lease'Position .. Data'First + Result.Expected_Source_Lease'Position + Result.Expected_Source_Lease'Size / System.Storage_Unit - 1));
      Result.Actor_Wait := Load (Data (Data'First + Result.Actor_Wait'Position .. Data'First + Result.Actor_Wait'Position + Result.Actor_Wait'Size / System.Storage_Unit - 1));
      Result.Helper_Wait := Load (Data (Data'First + Result.Helper_Wait'Position .. Data'First + Result.Helper_Wait'Position + Result.Helper_Wait'Size / System.Storage_Unit - 1));
      Result.Namespace_Wait := Load (Data (Data'First + Result.Namespace_Wait'Position .. Data'First + Result.Namespace_Wait'Position + Result.Namespace_Wait'Size / System.Storage_Unit - 1));
      Result.Host_Pid := Load (Data (Data'First + Result.Host_Pid'Position .. Data'First + Result.Host_Pid'Position + Result.Host_Pid'Size / System.Storage_Unit - 1));
      Result.Namespace_Pid := Load (Data (Data'First + Result.Namespace_Pid'Position .. Data'First + Result.Namespace_Pid'Position + Result.Namespace_Pid'Size / System.Storage_Unit - 1));
      Result.Sender_Uid := Load (Data (Data'First + Result.Sender_Uid'Position .. Data'First + Result.Sender_Uid'Position + Result.Sender_Uid'Size / System.Storage_Unit - 1));
      Result.Sender_Gid := Load (Data (Data'First + Result.Sender_Gid'Position .. Data'First + Result.Sender_Gid'Position + Result.Sender_Gid'Size / System.Storage_Unit - 1));
      Result.Real_Uid := Load (Data (Data'First + Result.Real_Uid'Position .. Data'First + Result.Real_Uid'Position + Result.Real_Uid'Size / System.Storage_Unit - 1));
      Result.Effective_Uid := Load (Data (Data'First + Result.Effective_Uid'Position .. Data'First + Result.Effective_Uid'Position + Result.Effective_Uid'Size / System.Storage_Unit - 1));
      Result.Saved_Uid := Load (Data (Data'First + Result.Saved_Uid'Position .. Data'First + Result.Saved_Uid'Position + Result.Saved_Uid'Size / System.Storage_Unit - 1));
      Result.Real_Gid := Load (Data (Data'First + Result.Real_Gid'Position .. Data'First + Result.Real_Gid'Position + Result.Real_Gid'Size / System.Storage_Unit - 1));
      Result.Effective_Gid := Load (Data (Data'First + Result.Effective_Gid'Position .. Data'First + Result.Effective_Gid'Position + Result.Effective_Gid'Size / System.Storage_Unit - 1));
      Result.Saved_Gid := Load (Data (Data'First + Result.Saved_Gid'Position .. Data'First + Result.Saved_Gid'Position + Result.Saved_Gid'Size / System.Storage_Unit - 1));
      Result.Capability_Version := Load (Data (Data'First + Result.Capability_Version'Position .. Data'First + Result.Capability_Version'Position + Result.Capability_Version'Size / System.Storage_Unit - 1));
      Result.Effective_Low := Load (Data (Data'First + Result.Effective_Low'Position .. Data'First + Result.Effective_Low'Position + Result.Effective_Low'Size / System.Storage_Unit - 1));
      Result.Permitted_Low := Load (Data (Data'First + Result.Permitted_Low'Position .. Data'First + Result.Permitted_Low'Position + Result.Permitted_Low'Size / System.Storage_Unit - 1));
      Result.Inheritable_Low := Load (Data (Data'First + Result.Inheritable_Low'Position .. Data'First + Result.Inheritable_Low'Position + Result.Inheritable_Low'Size / System.Storage_Unit - 1));
      Result.Effective_High := Load (Data (Data'First + Result.Effective_High'Position .. Data'First + Result.Effective_High'Position + Result.Effective_High'Size / System.Storage_Unit - 1));
      Result.Permitted_High := Load (Data (Data'First + Result.Permitted_High'Position .. Data'First + Result.Permitted_High'Position + Result.Permitted_High'Size / System.Storage_Unit - 1));
      Result.Inheritable_High := Load (Data (Data'First + Result.Inheritable_High'Position .. Data'First + Result.Inheritable_High'Position + Result.Inheritable_High'Size / System.Storage_Unit - 1));
      Result.Securebits := Load (Data (Data'First + Result.Securebits'Position .. Data'First + Result.Securebits'Position + Result.Securebits'Size / System.Storage_Unit - 1));
      Result.No_New_Privs := Load (Data (Data'First + Result.No_New_Privs'Position .. Data'First + Result.No_New_Privs'Position + Result.No_New_Privs'Size / System.Storage_Unit - 1));
      Result.Requester_Uid := Load (Data (Data'First + Result.Requester_Uid'Position .. Data'First + Result.Requester_Uid'Position + Result.Requester_Uid'Size / System.Storage_Unit - 1));
      Result.Requester_Gid := Load (Data (Data'First + Result.Requester_Gid'Position .. Data'First + Result.Requester_Gid'Position + Result.Requester_Gid'Size / System.Storage_Unit - 1));
      Result.Configured_Requester_Uid := Load (Data (Data'First + Result.Configured_Requester_Uid'Position .. Data'First + Result.Configured_Requester_Uid'Position + Result.Configured_Requester_Uid'Size / System.Storage_Unit - 1));
      Result.Workload_Uid := Load (Data (Data'First + Result.Workload_Uid'Position .. Data'First + Result.Workload_Uid'Position + Result.Workload_Uid'Size / System.Storage_Unit - 1));
      Result.Workload_Gid := Load (Data (Data'First + Result.Workload_Gid'Position .. Data'First + Result.Workload_Gid'Position + Result.Workload_Gid'Size / System.Storage_Unit - 1));
      Result.Proc_Host_Pid := Load (Data (Data'First + Result.Proc_Host_Pid'Position .. Data'First + Result.Proc_Host_Pid'Position + Result.Proc_Host_Pid'Size / System.Storage_Unit - 1));
      Result.Proc_Namespace_Pid := Load (Data (Data'First + Result.Proc_Namespace_Pid'Position .. Data'First + Result.Proc_Namespace_Pid'Position + Result.Proc_Namespace_Pid'Size / System.Storage_Unit - 1));
      Result.Proc_Real_Uid := Load (Data (Data'First + Result.Proc_Real_Uid'Position .. Data'First + Result.Proc_Real_Uid'Position + Result.Proc_Real_Uid'Size / System.Storage_Unit - 1));
      Result.Proc_Effective_Uid := Load (Data (Data'First + Result.Proc_Effective_Uid'Position .. Data'First + Result.Proc_Effective_Uid'Position + Result.Proc_Effective_Uid'Size / System.Storage_Unit - 1));
      Result.Proc_Saved_Uid := Load (Data (Data'First + Result.Proc_Saved_Uid'Position .. Data'First + Result.Proc_Saved_Uid'Position + Result.Proc_Saved_Uid'Size / System.Storage_Unit - 1));
      Result.Proc_Real_Gid := Load (Data (Data'First + Result.Proc_Real_Gid'Position .. Data'First + Result.Proc_Real_Gid'Position + Result.Proc_Real_Gid'Size / System.Storage_Unit - 1));
      Result.Proc_Effective_Gid := Load (Data (Data'First + Result.Proc_Effective_Gid'Position .. Data'First + Result.Proc_Effective_Gid'Position + Result.Proc_Effective_Gid'Size / System.Storage_Unit - 1));
      Result.Proc_Saved_Gid := Load (Data (Data'First + Result.Proc_Saved_Gid'Position .. Data'First + Result.Proc_Saved_Gid'Position + Result.Proc_Saved_Gid'Size / System.Storage_Unit - 1));
      Result.Proc_Effective := Load (Data (Data'First + Result.Proc_Effective'Position .. Data'First + Result.Proc_Effective'Position + Result.Proc_Effective'Size / System.Storage_Unit - 1));
      Result.Proc_Permitted := Load (Data (Data'First + Result.Proc_Permitted'Position .. Data'First + Result.Proc_Permitted'Position + Result.Proc_Permitted'Size / System.Storage_Unit - 1));
      Result.Proc_Inheritable := Load (Data (Data'First + Result.Proc_Inheritable'Position .. Data'First + Result.Proc_Inheritable'Position + Result.Proc_Inheritable'Size / System.Storage_Unit - 1));
      Result.Proc_Bounding := Load (Data (Data'First + Result.Proc_Bounding'Position .. Data'First + Result.Proc_Bounding'Position + Result.Proc_Bounding'Size / System.Storage_Unit - 1));
      Result.Proc_Ambient := Load (Data (Data'First + Result.Proc_Ambient'Position .. Data'First + Result.Proc_Ambient'Position + Result.Proc_Ambient'Size / System.Storage_Unit - 1));
      Result.Proc_No_New_Privs := Load (Data (Data'First + Result.Proc_No_New_Privs'Position .. Data'First + Result.Proc_No_New_Privs'Position + Result.Proc_No_New_Privs'Size / System.Storage_Unit - 1));
      Result.Proc_Fs_Uid := Load (Data (Data'First + Result.Proc_Fs_Uid'Position .. Data'First + Result.Proc_Fs_Uid'Position + Result.Proc_Fs_Uid'Size / System.Storage_Unit - 1));
      Result.Proc_Fs_Gid := Load (Data (Data'First + Result.Proc_Fs_Gid'Position .. Data'First + Result.Proc_Fs_Gid'Position + Result.Proc_Fs_Gid'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return X.Raw_Crosswalk is
      Result : X.Raw_Crosswalk;
   begin
      Result.Resource_Current := Load (Data (Data'First + Result.Resource_Current'Position .. Data'First + Result.Resource_Current'Position + Result.Resource_Current'Size / System.Storage_Unit - 1));
      Result.Operation_Policy := Load (Data (Data'First + Result.Operation_Policy'Position .. Data'First + Result.Operation_Policy'Position + Result.Operation_Policy'Size / System.Storage_Unit - 1));
      Result.Operation_Root_Set := Load (Data (Data'First + Result.Operation_Root_Set'Position .. Data'First + Result.Operation_Root_Set'Position + Result.Operation_Root_Set'Size / System.Storage_Unit - 1));
      Result.Owner_Genesis := Load (Data (Data'First + Result.Owner_Genesis'Position .. Data'First + Result.Owner_Genesis'Position + Result.Owner_Genesis'Size / System.Storage_Unit - 1));
      Result.Installation := Load (Data (Data'First + Result.Installation'Position .. Data'First + Result.Installation'Position + Result.Installation'Size / System.Storage_Unit - 1));
      Result.Gate_Config := Load (Data (Data'First + Result.Gate_Config'Position .. Data'First + Result.Gate_Config'Position + Result.Gate_Config'Size / System.Storage_Unit - 1));
      Result.Managed_Observation := Load (Data (Data'First + Result.Managed_Observation'Position .. Data'First + Result.Managed_Observation'Position + Result.Managed_Observation'Size / System.Storage_Unit - 1));
      Result.Original_Grant := Load (Data (Data'First + Result.Original_Grant'Position .. Data'First + Result.Original_Grant'Position + Result.Original_Grant'Size / System.Storage_Unit - 1));
      Result.Complete_Crosswalk := Load (Data (Data'First + Result.Complete_Crosswalk'Position .. Data'First + Result.Complete_Crosswalk'Position + Result.Complete_Crosswalk'Size / System.Storage_Unit - 1));
      Result.Current_Source := Load (Data (Data'First + Result.Current_Source'Position .. Data'First + Result.Current_Source'Position + Result.Current_Source'Size / System.Storage_Unit - 1));
      Result.Original_Request := Load (Data (Data'First + Result.Original_Request'Position .. Data'First + Result.Original_Request'Position + Result.Original_Request'Size / System.Storage_Unit - 1));
      Result.Original_Requester := Load (Data (Data'First + Result.Original_Requester'Position .. Data'First + Result.Original_Requester'Position + Result.Original_Requester'Size / System.Storage_Unit - 1));
      Result.Original_Transaction := Load (Data (Data'First + Result.Original_Transaction'Position .. Data'First + Result.Original_Transaction'Position + Result.Original_Transaction'Size / System.Storage_Unit - 1));
      Result.Preparer := Load (Data (Data'First + Result.Preparer'Position .. Data'First + Result.Preparer'Position + Result.Preparer'Size / System.Storage_Unit - 1));
      Result.Selected_Plan := Load (Data (Data'First + Result.Selected_Plan'Position .. Data'First + Result.Selected_Plan'Position + Result.Selected_Plan'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return C.Raw_Digest is
      Result : C.Raw_Digest;
   begin
      Result.Present := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Present'Position .. Data'First + Result.Present'Position + Result.Present'Size / System.Storage_Unit - 1)));
      Result.Value := Load (Data (Data'First + Result.Value'Position .. Data'First + Result.Value'Position + Result.Value'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return C.Raw_Hash is
      Result : C.Raw_Hash;
   begin
      for I in Result'Range loop
         Result (I) := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Q.Byte_Count (I - Result'First) * Interfaces.Unsigned_8'Size / System.Storage_Unit .. Data'First + Q.Byte_Count (I - Result'First) * Interfaces.Unsigned_8'Size / System.Storage_Unit + Interfaces.Unsigned_8'Size / System.Storage_Unit - 1)));
      end loop;
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return Y.Raw_Input is
      Result : Y.Raw_Input;
   begin
      Result.Mode := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Mode'Position .. Data'First + Result.Mode'Position + Result.Mode'Size / System.Storage_Unit - 1)));
      Result.Controller := Load (Data (Data'First + Result.Controller'Position .. Data'First + Result.Controller'Position + Result.Controller'Size / System.Storage_Unit - 1));
      Result.Child_Task := Load (Data (Data'First + Result.Child_Task'Position .. Data'First + Result.Child_Task'Position + Result.Child_Task'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return Y.Raw_Controller is
      Result : Y.Raw_Controller;
   begin
      Result.Bound := Load (Data (Data'First + Result.Bound'Position .. Data'First + Result.Bound'Position + Result.Bound'Size / System.Storage_Unit - 1));
      Result.Process := Load (Data (Data'First + Result.Process'Position .. Data'First + Result.Process'Position + Result.Process'Size / System.Storage_Unit - 1));
      Result.Requester_Uid := Load (Data (Data'First + Result.Requester_Uid'Position .. Data'First + Result.Requester_Uid'Position + Result.Requester_Uid'Size / System.Storage_Unit - 1));
      Result.Requester_Gid := Load (Data (Data'First + Result.Requester_Gid'Position .. Data'First + Result.Requester_Gid'Position + Result.Requester_Gid'Size / System.Storage_Unit - 1));
      Result.raw_manager := Load (Data (Data'First + Result.raw_manager'Position .. Data'First + Result.raw_manager'Position + Result.raw_manager'Size / System.Storage_Unit - 1));
      Result.raw_channel := Load (Data (Data'First + Result.raw_channel'Position .. Data'First + Result.raw_channel'Position + Result.raw_channel'Size / System.Storage_Unit - 1));
      Result.owner_endpoint := Load (Data (Data'First + Result.owner_endpoint'Position .. Data'First + Result.owner_endpoint'Position + Result.owner_endpoint'Size / System.Storage_Unit - 1));
      Result.expected_owner_endpoint := Load (Data (Data'First + Result.expected_owner_endpoint'Position .. Data'First + Result.expected_owner_endpoint'Position + Result.expected_owner_endpoint'Size / System.Storage_Unit - 1));
      Result.source_lease := Load (Data (Data'First + Result.source_lease'Position .. Data'First + Result.source_lease'Position + Result.source_lease'Size / System.Storage_Unit - 1));
      Result.expected_source_lease := Load (Data (Data'First + Result.expected_source_lease'Position .. Data'First + Result.expected_source_lease'Position + Result.expected_source_lease'Size / System.Storage_Unit - 1));
      Result.worker_image := Load (Data (Data'First + Result.worker_image'Position .. Data'First + Result.worker_image'Position + Result.worker_image'Size / System.Storage_Unit - 1));
      Result.expected_worker_image := Load (Data (Data'First + Result.expected_worker_image'Position .. Data'First + Result.expected_worker_image'Position + Result.expected_worker_image'Size / System.Storage_Unit - 1));
      Result.handler_plan := Load (Data (Data'First + Result.handler_plan'Position .. Data'First + Result.handler_plan'Position + Result.handler_plan'Size / System.Storage_Unit - 1));
      Result.expected_handler_plan := Load (Data (Data'First + Result.expected_handler_plan'Position .. Data'First + Result.expected_handler_plan'Position + Result.expected_handler_plan'Size / System.Storage_Unit - 1));
      Result.raw_request := Load (Data (Data'First + Result.raw_request'Position .. Data'First + Result.raw_request'Position + Result.raw_request'Size / System.Storage_Unit - 1));
      Result.requester := Load (Data (Data'First + Result.requester'Position .. Data'First + Result.requester'Position + Result.requester'Size / System.Storage_Unit - 1));
      Result.dispatch := Load (Data (Data'First + Result.dispatch'Position .. Data'First + Result.dispatch'Position + Result.dispatch'Size / System.Storage_Unit - 1));
      Result.running_event := Load (Data (Data'First + Result.running_event'Position .. Data'First + Result.running_event'Position + Result.running_event'Size / System.Storage_Unit - 1));
      Result.expected_running_event := Load (Data (Data'First + Result.expected_running_event'Position .. Data'First + Result.expected_running_event'Position + Result.expected_running_event'Size / System.Storage_Unit - 1));
      Result.store_genesis := Load (Data (Data'First + Result.store_genesis'Position .. Data'First + Result.store_genesis'Position + Result.store_genesis'Size / System.Storage_Unit - 1));
      Result.expected_store_genesis := Load (Data (Data'First + Result.expected_store_genesis'Position .. Data'First + Result.expected_store_genesis'Position + Result.expected_store_genesis'Size / System.Storage_Unit - 1));
      Result.current_source := Load (Data (Data'First + Result.current_source'Position .. Data'First + Result.current_source'Position + Result.current_source'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return Y.Raw_Process is
      Result : Y.Raw_Process;
   begin
      Result.raw_status := Load (Data (Data'First + Result.raw_status'Position .. Data'First + Result.raw_status'Position + Result.raw_status'Size / System.Storage_Unit - 1));
      Result.raw_stat := Load (Data (Data'First + Result.raw_stat'Position .. Data'First + Result.raw_stat'Position + Result.raw_stat'Size / System.Storage_Unit - 1));
      Result.raw_cgroup := Load (Data (Data'First + Result.raw_cgroup'Position .. Data'First + Result.raw_cgroup'Position + Result.raw_cgroup'Size / System.Storage_Unit - 1));
      Result.raw_maps := Load (Data (Data'First + Result.raw_maps'Position .. Data'First + Result.raw_maps'Position + Result.raw_maps'Size / System.Storage_Unit - 1));
      Result.raw_cmdline := Load (Data (Data'First + Result.raw_cmdline'Position .. Data'First + Result.raw_cmdline'Position + Result.raw_cmdline'Size / System.Storage_Unit - 1));
      Result.raw_pidfd_info := Load (Data (Data'First + Result.raw_pidfd_info'Position .. Data'First + Result.raw_pidfd_info'Position + Result.raw_pidfd_info'Size / System.Storage_Unit - 1));
      Result.namespace := Load (Data (Data'First + Result.namespace'Position .. Data'First + Result.namespace'Position + Result.namespace'Size / System.Storage_Unit - 1));
      Result.cgroup := Load (Data (Data'First + Result.cgroup'Position .. Data'First + Result.cgroup'Position + Result.cgroup'Size / System.Storage_Unit - 1));
      Result.actual_unit := Load (Data (Data'First + Result.actual_unit'Position .. Data'First + Result.actual_unit'Position + Result.actual_unit'Size / System.Storage_Unit - 1));
      Result.invocation := Load (Data (Data'First + Result.invocation'Position .. Data'First + Result.invocation'Position + Result.invocation'Size / System.Storage_Unit - 1));
      Result.source_lease := Load (Data (Data'First + Result.source_lease'Position .. Data'First + Result.source_lease'Position + Result.source_lease'Size / System.Storage_Unit - 1));
      Result.pidfd_wait := Load (Data (Data'First + Result.pidfd_wait'Position .. Data'First + Result.pidfd_wait'Position + Result.pidfd_wait'Size / System.Storage_Unit - 1));
      Result.host_pid := Load (Data (Data'First + Result.host_pid'Position .. Data'First + Result.host_pid'Position + Result.host_pid'Size / System.Storage_Unit - 1));
      Result.start_tick := Load (Data (Data'First + Result.start_tick'Position .. Data'First + Result.start_tick'Position + Result.start_tick'Size / System.Storage_Unit - 1));
      Result.parent_pid := Load (Data (Data'First + Result.parent_pid'Position .. Data'First + Result.parent_pid'Position + Result.parent_pid'Size / System.Storage_Unit - 1));
      Result.parent_start_tick := Load (Data (Data'First + Result.parent_start_tick'Position .. Data'First + Result.parent_start_tick'Position + Result.parent_start_tick'Size / System.Storage_Unit - 1));
      Result.real_uid := Load (Data (Data'First + Result.real_uid'Position .. Data'First + Result.real_uid'Position + Result.real_uid'Size / System.Storage_Unit - 1));
      Result.effective_uid := Load (Data (Data'First + Result.effective_uid'Position .. Data'First + Result.effective_uid'Position + Result.effective_uid'Size / System.Storage_Unit - 1));
      Result.saved_uid := Load (Data (Data'First + Result.saved_uid'Position .. Data'First + Result.saved_uid'Position + Result.saved_uid'Size / System.Storage_Unit - 1));
      Result.real_gid := Load (Data (Data'First + Result.real_gid'Position .. Data'First + Result.real_gid'Position + Result.real_gid'Size / System.Storage_Unit - 1));
      Result.effective_gid := Load (Data (Data'First + Result.effective_gid'Position .. Data'First + Result.effective_gid'Position + Result.effective_gid'Size / System.Storage_Unit - 1));
      Result.saved_gid := Load (Data (Data'First + Result.saved_gid'Position .. Data'First + Result.saved_gid'Position + Result.saved_gid'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return Y.Raw_Task is
      Result : Y.Raw_Task;
   begin
      Result.Action := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Action'Position .. Data'First + Result.Action'Position + Result.Action'Size / System.Storage_Unit - 1)));
      Result.Root := Load (Data (Data'First + Result.Root'Position .. Data'First + Result.Root'Position + Result.Root'Size / System.Storage_Unit - 1));
      Result.Child := Load (Data (Data'First + Result.Child'Position .. Data'First + Result.Child'Position + Result.Child'Size / System.Storage_Unit - 1));
      Result.task_id := Load (Data (Data'First + Result.task_id'Position .. Data'First + Result.task_id'Position + Result.task_id'Size / System.Storage_Unit - 1));
      Result.root_world := Load (Data (Data'First + Result.root_world'Position .. Data'First + Result.root_world'Position + Result.root_world'Size / System.Storage_Unit - 1));
      Result.child_world := Load (Data (Data'First + Result.child_world'Position .. Data'First + Result.child_world'Position + Result.child_world'Size / System.Storage_Unit - 1));
      Result.root_instance := Load (Data (Data'First + Result.root_instance'Position .. Data'First + Result.root_instance'Position + Result.root_instance'Size / System.Storage_Unit - 1));
      Result.child_instance := Load (Data (Data'First + Result.child_instance'Position .. Data'First + Result.child_instance'Position + Result.child_instance'Size / System.Storage_Unit - 1));
      Result.world_store := Load (Data (Data'First + Result.world_store'Position .. Data'First + Result.world_store'Position + Result.world_store'Size / System.Storage_Unit - 1));
      Result.full_world_ancestry := Load (Data (Data'First + Result.full_world_ancestry'Position .. Data'First + Result.full_world_ancestry'Position + Result.full_world_ancestry'Size / System.Storage_Unit - 1));
      Result.original_workload := Load (Data (Data'First + Result.original_workload'Position .. Data'First + Result.original_workload'Position + Result.original_workload'Size / System.Storage_Unit - 1));
      Result.sandbox := Load (Data (Data'First + Result.sandbox'Position .. Data'First + Result.sandbox'Position + Result.sandbox'Size / System.Storage_Unit - 1));
      Result.adapter := Load (Data (Data'First + Result.adapter'Position .. Data'First + Result.adapter'Position + Result.adapter'Size / System.Storage_Unit - 1));
      Result.context := Load (Data (Data'First + Result.context'Position .. Data'First + Result.context'Position + Result.context'Size / System.Storage_Unit - 1));
      Result.mission := Load (Data (Data'First + Result.mission'Position .. Data'First + Result.mission'Position + Result.mission'Size / System.Storage_Unit - 1));
      Result.stdin := Load (Data (Data'First + Result.stdin'Position .. Data'First + Result.stdin'Position + Result.stdin'Size / System.Storage_Unit - 1));
      Result.credential_source := Load (Data (Data'First + Result.credential_source'Position .. Data'First + Result.credential_source'Position + Result.credential_source'Size / System.Storage_Unit - 1));
      Result.executable_source := Load (Data (Data'First + Result.executable_source'Position .. Data'First + Result.executable_source'Position + Result.executable_source'Size / System.Storage_Unit - 1));
      Result.configuration := Load (Data (Data'First + Result.configuration'Position .. Data'First + Result.configuration'Position + Result.configuration'Size / System.Storage_Unit - 1));
      Result.owner_plan := Load (Data (Data'First + Result.owner_plan'Position .. Data'First + Result.owner_plan'Position + Result.owner_plan'Size / System.Storage_Unit - 1));
      Result.native_cost_input := Load (Data (Data'First + Result.native_cost_input'Position .. Data'First + Result.native_cost_input'Position + Result.native_cost_input'Size / System.Storage_Unit - 1));
      Result.raw_request := Load (Data (Data'First + Result.raw_request'Position .. Data'First + Result.raw_request'Position + Result.raw_request'Size / System.Storage_Unit - 1));
      Result.requester := Load (Data (Data'First + Result.requester'Position .. Data'First + Result.requester'Position + Result.requester'Size / System.Storage_Unit - 1));
      Result.cause := Load (Data (Data'First + Result.cause'Position .. Data'First + Result.cause'Position + Result.cause'Size / System.Storage_Unit - 1));
      Result.root_dispatch := Load (Data (Data'First + Result.root_dispatch'Position .. Data'First + Result.root_dispatch'Position + Result.root_dispatch'Size / System.Storage_Unit - 1));
      Result.root_running_event := Load (Data (Data'First + Result.root_running_event'Position .. Data'First + Result.root_running_event'Position + Result.root_running_event'Size / System.Storage_Unit - 1));
      Result.task_journal := Load (Data (Data'First + Result.task_journal'Position .. Data'First + Result.task_journal'Position + Result.task_journal'Size / System.Storage_Unit - 1));
      Result.task_intent := Load (Data (Data'First + Result.task_intent'Position .. Data'First + Result.task_intent'Position + Result.task_intent'Size / System.Storage_Unit - 1));
      Result.task_reservation_event := Load (Data (Data'First + Result.task_reservation_event'Position .. Data'First + Result.task_reservation_event'Position + Result.task_reservation_event'Size / System.Storage_Unit - 1));
      Result.task_launch_event := Load (Data (Data'First + Result.task_launch_event'Position .. Data'First + Result.task_launch_event'Position + Result.task_launch_event'Size / System.Storage_Unit - 1));
      Result.parent_namespace_source := Load (Data (Data'First + Result.parent_namespace_source'Position .. Data'First + Result.parent_namespace_source'Position + Result.parent_namespace_source'Size / System.Storage_Unit - 1));
      Result.fd_lineage := Load (Data (Data'First + Result.fd_lineage'Position .. Data'First + Result.fd_lineage'Position + Result.fd_lineage'Size / System.Storage_Unit - 1));
      Result.source_lease := Load (Data (Data'First + Result.source_lease'Position .. Data'First + Result.source_lease'Position + Result.source_lease'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return Y.Raw_Namespace is
      Result : Y.Raw_Namespace;
   begin
      Result.identity := Load (Data (Data'First + Result.identity'Position .. Data'First + Result.identity'Position + Result.identity'Size / System.Storage_Unit - 1));
      Result.parent := Load (Data (Data'First + Result.parent'Position .. Data'First + Result.parent'Position + Result.parent'Size / System.Storage_Unit - 1));
      Result.raw_nsfs := Load (Data (Data'First + Result.raw_nsfs'Position .. Data'First + Result.raw_nsfs'Position + Result.raw_nsfs'Size / System.Storage_Unit - 1));
      Result.raw_get_parent := Load (Data (Data'First + Result.raw_get_parent'Position .. Data'First + Result.raw_get_parent'Position + Result.raw_get_parent'Size / System.Storage_Unit - 1));
      Result.source_lease := Load (Data (Data'First + Result.source_lease'Position .. Data'First + Result.source_lease'Position + Result.source_lease'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Input is
      Result : T.Raw_Input;
   begin
      Result.Schema := Interfaces.Unsigned_32 (Little_Endian (Data (Data'First + Result.Schema'Position .. Data'First + Result.Schema'Position + Result.Schema'Size / System.Storage_Unit - 1)));
      Result.Mode := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Mode'Position .. Data'First + Result.Mode'Position + Result.Mode'Size / System.Storage_Unit - 1)));
      Result.Bound := Load (Data (Data'First + Result.Bound'Position .. Data'First + Result.Bound'Position + Result.Bound'Size / System.Storage_Unit - 1));
      Result.Now := Load (Data (Data'First + Result.Now'Position .. Data'First + Result.Now'Position + Result.Now'Size / System.Storage_Unit - 1));
      Result.Facts := Load (Data (Data'First + Result.Facts'Position .. Data'First + Result.Facts'Position + Result.Facts'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Binding is
      Result : T.Raw_Binding;
   begin
      Result.Action := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Action'Position .. Data'First + Result.Action'Position + Result.Action'Size / System.Storage_Unit - 1)));
      Result.Id := Load (Data (Data'First + Result.Id'Position .. Data'First + Result.Id'Position + Result.Id'Size / System.Storage_Unit - 1));
      Result.Peer := Load (Data (Data'First + Result.Peer'Position .. Data'First + Result.Peer'Position + Result.Peer'Size / System.Storage_Unit - 1));
      Result.Preparer := Load (Data (Data'First + Result.Preparer'Position .. Data'First + Result.Preparer'Position + Result.Preparer'Size / System.Storage_Unit - 1));
      Result.Owner := Load (Data (Data'First + Result.Owner'Position .. Data'First + Result.Owner'Position + Result.Owner'Size / System.Storage_Unit - 1));
      Result.Target_Owner := Load (Data (Data'First + Result.Target_Owner'Position .. Data'First + Result.Target_Owner'Position + Result.Target_Owner'Size / System.Storage_Unit - 1));
      Result.Policy_Epoch := Load (Data (Data'First + Result.Policy_Epoch'Position .. Data'First + Result.Policy_Epoch'Position + Result.Policy_Epoch'Size / System.Storage_Unit - 1));
      Result.Resource_Epoch := Load (Data (Data'First + Result.Resource_Epoch'Position .. Data'First + Result.Resource_Epoch'Position + Result.Resource_Epoch'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Ids is
      Result : T.Raw_Ids;
   begin
      for I in Result'Range loop
         Result (I) := Load (Data (Data'First + Q.Byte_Count (T.A.Identity_Field'Pos (I) - T.A.Identity_Field'Pos (Result'First)) * C.Raw_Digest'Size / System.Storage_Unit .. Data'First + Q.Byte_Count (T.A.Identity_Field'Pos (I) - T.A.Identity_Field'Pos (Result'First)) * C.Raw_Digest'Size / System.Storage_Unit + C.Raw_Digest'Size / System.Storage_Unit - 1));
      end loop;
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_UID is
      Result : T.Raw_UID;
   begin
      Result.Present := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Present'Position .. Data'First + Result.Present'Position + Result.Present'Size / System.Storage_Unit - 1)));
      Result.Value := Interfaces.Unsigned_32 (Little_Endian (Data (Data'First + Result.Value'Position .. Data'First + Result.Value'Position + Result.Value'Size / System.Storage_Unit - 1)));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Quantity is
      Result : T.Raw_Quantity;
   begin
      Result.Present := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Present'Position .. Data'First + Result.Present'Position + Result.Present'Size / System.Storage_Unit - 1)));
      Result.Negative := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Negative'Position .. Data'First + Result.Negative'Position + Result.Negative'Size / System.Storage_Unit - 1)));
      Result.First := Signed (Data (Data'First + Result.First'Position .. Data'First + Result.First'Position + Result.First'Size / System.Storage_Unit - 1));
      Result.Length := Signed (Data (Data'First + Result.Length'Position .. Data'First + Result.Length'Position + Result.Length'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Evidence is
      Result : T.Raw_Evidence;
   begin
      Result.Effect_Binding := Load (Data (Data'First + Result.Effect_Binding'Position .. Data'First + Result.Effect_Binding'Position + Result.Effect_Binding'Size / System.Storage_Unit - 1));
      Result.Actual_Receipt_Root := Load (Data (Data'First + Result.Actual_Receipt_Root'Position .. Data'First + Result.Actual_Receipt_Root'Position + Result.Actual_Receipt_Root'Size / System.Storage_Unit - 1));
      Result.Actual_Causal_Root := Load (Data (Data'First + Result.Actual_Causal_Root'Position .. Data'First + Result.Actual_Causal_Root'Position + Result.Actual_Causal_Root'Size / System.Storage_Unit - 1));
      Result.No_Effect_Binding := Load (Data (Data'First + Result.No_Effect_Binding'Position .. Data'First + Result.No_Effect_Binding'Position + Result.No_Effect_Binding'Size / System.Storage_Unit - 1));
      Result.Owner_Resolution := Load (Data (Data'First + Result.Owner_Resolution'Position .. Data'First + Result.Owner_Resolution'Position + Result.Owner_Resolution'Size / System.Storage_Unit - 1));
      Result.Quarantine_Head := Load (Data (Data'First + Result.Quarantine_Head'Position .. Data'First + Result.Quarantine_Head'Position + Result.Quarantine_Head'Size / System.Storage_Unit - 1));
      Result.Witnessed_Receipt_Head := Load (Data (Data'First + Result.Witnessed_Receipt_Head'Position .. Data'First + Result.Witnessed_Receipt_Head'Position + Result.Witnessed_Receipt_Head'Size / System.Storage_Unit - 1));
      Result.Witnessed_Causal_Head := Load (Data (Data'First + Result.Witnessed_Causal_Head'Position .. Data'First + Result.Witnessed_Causal_Head'Position + Result.Witnessed_Causal_Head'Size / System.Storage_Unit - 1));
      Result.Recovery := Load (Data (Data'First + Result.Recovery'Position .. Data'First + Result.Recovery'Position + Result.Recovery'Size / System.Storage_Unit - 1));
      Result.Original_Use := Load (Data (Data'First + Result.Original_Use'Position .. Data'First + Result.Original_Use'Position + Result.Original_Use'Size / System.Storage_Unit - 1));
      Result.Effect_Material_First := Signed (Data (Data'First + Result.Effect_Material_First'Position .. Data'First + Result.Effect_Material_First'Position + Result.Effect_Material_First'Size / System.Storage_Unit - 1));
      Result.Effect_Material_Length := Signed (Data (Data'First + Result.Effect_Material_Length'Position .. Data'First + Result.Effect_Material_Length'Position + Result.Effect_Material_Length'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return RW.Raw_Request is
      Result : RW.Raw_Request;
   begin
      Result.Schema_Version := Interfaces.Unsigned_32 (Little_Endian (Data (Data'First + Result.Schema_Version'Position .. Data'First + Result.Schema_Version'Position + Result.Schema_Version'Size / System.Storage_Unit - 1)));
      Result.State := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.State'Position .. Data'First + Result.State'Position + Result.State'Size / System.Storage_Unit - 1)));
      Result.Fresh := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Fresh'Position .. Data'First + Result.Fresh'Position + Result.Fresh'Size / System.Storage_Unit - 1)));
      Result.Historical := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Historical'Position .. Data'First + Result.Historical'Position + Result.Historical'Size / System.Storage_Unit - 1)));
      Result.Grant_Eligible := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Grant_Eligible'Position .. Data'First + Result.Grant_Eligible'Position + Result.Grant_Eligible'Size / System.Storage_Unit - 1)));
      Result.Issued_Binding := Load (Data (Data'First + Result.Issued_Binding'Position .. Data'First + Result.Issued_Binding'Position + Result.Issued_Binding'Size / System.Storage_Unit - 1));
      Result.Recovered_Binding := Load (Data (Data'First + Result.Recovered_Binding'Position .. Data'First + Result.Recovered_Binding'Position + Result.Recovered_Binding'Size / System.Storage_Unit - 1));
      Result.Native := Load (Data (Data'First + Result.Native'Position .. Data'First + Result.Native'Position + Result.Native'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return RW.Raw_Binding is
      Result : RW.Raw_Binding;
   begin
      Result.Mode := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Mode'Position .. Data'First + Result.Mode'Position + Result.Mode'Size / System.Storage_Unit - 1)));
      Result.Operation := Load (Data (Data'First + Result.Operation'Position .. Data'First + Result.Operation'Position + Result.Operation'Size / System.Storage_Unit - 1));
      Result.Transaction := Load (Data (Data'First + Result.Transaction'Position .. Data'First + Result.Transaction'Position + Result.Transaction'Size / System.Storage_Unit - 1));
      Result.Capability := Load (Data (Data'First + Result.Capability'Position .. Data'First + Result.Capability'Position + Result.Capability'Size / System.Storage_Unit - 1));
      Result.Universe_Head := Load (Data (Data'First + Result.Universe_Head'Position .. Data'First + Result.Universe_Head'Position + Result.Universe_Head'Size / System.Storage_Unit - 1));
      Result.Instance := Load (Data (Data'First + Result.Instance'Position .. Data'First + Result.Instance'Position + Result.Instance'Size / System.Storage_Unit - 1));
      Result.Subject := Load (Data (Data'First + Result.Subject'Position .. Data'First + Result.Subject'Position + Result.Subject'Size / System.Storage_Unit - 1));
      Result.Staged_Root := Load (Data (Data'First + Result.Staged_Root'Position .. Data'First + Result.Staged_Root'Position + Result.Staged_Root'Size / System.Storage_Unit - 1));
      Result.Current_Requirement := Load (Data (Data'First + Result.Current_Requirement'Position .. Data'First + Result.Current_Requirement'Position + Result.Current_Requirement'Size / System.Storage_Unit - 1));
      Result.Resulting_Requirement := Load (Data (Data'First + Result.Resulting_Requirement'Position .. Data'First + Result.Resulting_Requirement'Position + Result.Resulting_Requirement'Size / System.Storage_Unit - 1));
      Result.Requester := Load (Data (Data'First + Result.Requester'Position .. Data'First + Result.Requester'Position + Result.Requester'Size / System.Storage_Unit - 1));
      Result.Grant_Use := Load (Data (Data'First + Result.Grant_Use'Position .. Data'First + Result.Grant_Use'Position + Result.Grant_Use'Size / System.Storage_Unit - 1));
      Result.Policy_Identity := Load (Data (Data'First + Result.Policy_Identity'Position .. Data'First + Result.Policy_Identity'Position + Result.Policy_Identity'Size / System.Storage_Unit - 1));
      Result.Selected_Evaluation := Load (Data (Data'First + Result.Selected_Evaluation'Position .. Data'First + Result.Selected_Evaluation'Position + Result.Selected_Evaluation'Size / System.Storage_Unit - 1));
      Result.History_Head := Load (Data (Data'First + Result.History_Head'Position .. Data'First + Result.History_Head'Position + Result.History_Head'Size / System.Storage_Unit - 1));
      Result.Reservation := Load (Data (Data'First + Result.Reservation'Position .. Data'First + Result.Reservation'Position + Result.Reservation'Size / System.Storage_Unit - 1));
      Result.Host := Load (Data (Data'First + Result.Host'Position .. Data'First + Result.Host'Position + Result.Host'Size / System.Storage_Unit - 1));
      Result.Before_Prime := Load (Data (Data'First + Result.Before_Prime'Position .. Data'First + Result.Before_Prime'Position + Result.Before_Prime'Size / System.Storage_Unit - 1));
      Result.Before_Root := Load (Data (Data'First + Result.Before_Root'Position .. Data'First + Result.Before_Root'Position + Result.Before_Root'Size / System.Storage_Unit - 1));
      Result.Before_Mapping := Load (Data (Data'First + Result.Before_Mapping'Position .. Data'First + Result.Before_Mapping'Position + Result.Before_Mapping'Size / System.Storage_Unit - 1));
      Result.Staged_Mapping := Load (Data (Data'First + Result.Staged_Mapping'Position .. Data'First + Result.Staged_Mapping'Position + Result.Staged_Mapping'Size / System.Storage_Unit - 1));
      Result.Input_Snapshot := Load (Data (Data'First + Result.Input_Snapshot'Position .. Data'First + Result.Input_Snapshot'Position + Result.Input_Snapshot'Size / System.Storage_Unit - 1));
      Result.Kernel_Build := Load (Data (Data'First + Result.Kernel_Build'Position .. Data'First + Result.Kernel_Build'Position + Result.Kernel_Build'Size / System.Storage_Unit - 1));
      Result.Kernel_Library := Load (Data (Data'First + Result.Kernel_Library'Position .. Data'First + Result.Kernel_Library'Position + Result.Kernel_Library'Size / System.Storage_Unit - 1));
      Result.Kernel_Mapping := Load (Data (Data'First + Result.Kernel_Mapping'Position .. Data'First + Result.Kernel_Mapping'Position + Result.Kernel_Mapping'Size / System.Storage_Unit - 1));
      Result.Issuer_Head := Load (Data (Data'First + Result.Issuer_Head'Position .. Data'First + Result.Issuer_Head'Position + Result.Issuer_Head'Size / System.Storage_Unit - 1));
      Result.Receipt_Head := Load (Data (Data'First + Result.Receipt_Head'Position .. Data'First + Result.Receipt_Head'Position + Result.Receipt_Head'Size / System.Storage_Unit - 1));
      Result.Causal_Head := Load (Data (Data'First + Result.Causal_Head'Position .. Data'First + Result.Causal_Head'Position + Result.Causal_Head'Size / System.Storage_Unit - 1));
      Result.Policy_Epoch := Load (Data (Data'First + Result.Policy_Epoch'Position .. Data'First + Result.Policy_Epoch'Position + Result.Policy_Epoch'Size / System.Storage_Unit - 1));
      Result.Resource_Epoch := Load (Data (Data'First + Result.Resource_Epoch'Position .. Data'First + Result.Resource_Epoch'Position + Result.Resource_Epoch'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return RW.Raw_Digest is
      Result : RW.Raw_Digest;
   begin
      Result.Present := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Present'Position .. Data'First + Result.Present'Position + Result.Present'Size / System.Storage_Unit - 1)));
      Result.Value := Load (Data (Data'First + Result.Value'Position .. Data'First + Result.Value'Position + Result.Value'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return RW.Raw_Hash is
      Result : RW.Raw_Hash;
   begin
      for I in Result'Range loop
         Result (I) := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Q.Byte_Count (I - Result'First) * Interfaces.Unsigned_8'Size / System.Storage_Unit .. Data'First + Q.Byte_Count (I - Result'First) * Interfaces.Unsigned_8'Size / System.Storage_Unit + Interfaces.Unsigned_8'Size / System.Storage_Unit - 1)));
      end loop;
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return RW.Raw_Epoch is
      Result : RW.Raw_Epoch;
   begin
      Result.Present := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Present'Position .. Data'First + Result.Present'Position + Result.Present'Size / System.Storage_Unit - 1)));
      Result.Negative := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Negative'Position .. Data'First + Result.Negative'Position + Result.Negative'Size / System.Storage_Unit - 1)));
      Result.First := Signed (Data (Data'First + Result.First'Position .. Data'First + Result.First'Position + Result.First'Size / System.Storage_Unit - 1));
      Result.Length := Signed (Data (Data'First + Result.Length'Position .. Data'First + Result.Length'Position + Result.Length'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return RW.Raw_Native is
      Result : RW.Raw_Native;
   begin
      Result.Live_Mapping := Load (Data (Data'First + Result.Live_Mapping'Position .. Data'First + Result.Live_Mapping'Position + Result.Live_Mapping'Size / System.Storage_Unit - 1));
      Result.Live_Root := Load (Data (Data'First + Result.Live_Root'Position .. Data'First + Result.Live_Root'Position + Result.Live_Root'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Grant is
      Result : T.Raw_Grant;
   begin
      Result.Id := Load (Data (Data'First + Result.Id'Position .. Data'First + Result.Id'Position + Result.Id'Size / System.Storage_Unit - 1));
      Result.Parent := Load (Data (Data'First + Result.Parent'Position .. Data'First + Result.Parent'Position + Result.Parent'Size / System.Storage_Unit - 1));
      Result.Issuer := Load (Data (Data'First + Result.Issuer'Position .. Data'First + Result.Issuer'Position + Result.Issuer'Size / System.Storage_Unit - 1));
      Result.Instance := Load (Data (Data'First + Result.Instance'Position .. Data'First + Result.Instance'Position + Result.Instance'Size / System.Storage_Unit - 1));
      Result.Root_Set := Load (Data (Data'First + Result.Root_Set'Position .. Data'First + Result.Root_Set'Position + Result.Root_Set'Size / System.Storage_Unit - 1));
      Result.Policy := Load (Data (Data'First + Result.Policy'Position .. Data'First + Result.Policy'Position + Result.Policy'Size / System.Storage_Unit - 1));
      Result.Subject := Load (Data (Data'First + Result.Subject'Position .. Data'First + Result.Subject'Position + Result.Subject'Size / System.Storage_Unit - 1));
      Result.Owner := Load (Data (Data'First + Result.Owner'Position .. Data'First + Result.Owner'Position + Result.Owner'Size / System.Storage_Unit - 1));
      Result.Allowed := Load (Data (Data'First + Result.Allowed'Position .. Data'First + Result.Allowed'Position + Result.Allowed'Size / System.Storage_Unit - 1));
      Result.State := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.State'Position .. Data'First + Result.State'Position + Result.State'Size / System.Storage_Unit - 1)));
      Result.Epoch := Load (Data (Data'First + Result.Epoch'Position .. Data'First + Result.Epoch'Position + Result.Epoch'Size / System.Storage_Unit - 1));
      Result.Ceiling := Load (Data (Data'First + Result.Ceiling'Position .. Data'First + Result.Ceiling'Position + Result.Ceiling'Size / System.Storage_Unit - 1));
      Result.Issued_At := Load (Data (Data'First + Result.Issued_At'Position .. Data'First + Result.Issued_At'Position + Result.Issued_At'Size / System.Storage_Unit - 1));
      Result.Expires_At := Load (Data (Data'First + Result.Expires_At'Position .. Data'First + Result.Expires_At'Position + Result.Expires_At'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Rights is
      Result : T.Raw_Rights;
   begin
      for I in Result'Range loop
         Result (I) := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Q.Byte_Count (T.A.Operation'Pos (I) - T.A.Operation'Pos (Result'First)) * Interfaces.Unsigned_8'Size / System.Storage_Unit .. Data'First + Q.Byte_Count (T.A.Operation'Pos (I) - T.A.Operation'Pos (Result'First)) * Interfaces.Unsigned_8'Size / System.Storage_Unit + Interfaces.Unsigned_8'Size / System.Storage_Unit - 1)));
      end loop;
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Use is
      Result : T.Raw_Use;
   begin
      Result.Bound := Load (Data (Data'First + Result.Bound'Position .. Data'First + Result.Bound'Position + Result.Bound'Size / System.Storage_Unit - 1));
      Result.State := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.State'Position .. Data'First + Result.State'Position + Result.State'Size / System.Storage_Unit - 1)));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return C.Raw_Row is
      Result : C.Raw_Row;
   begin
      Result.Previous := Load (Data (Data'First + Result.Previous'Position .. Data'First + Result.Previous'Position + Result.Previous'Size / System.Storage_Unit - 1));
      Result.Actual_Payload_Root := Load (Data (Data'First + Result.Actual_Payload_Root'Position .. Data'First + Result.Actual_Payload_Root'Position + Result.Actual_Payload_Root'Size / System.Storage_Unit - 1));
      Result.Stored_Payload_Root := Load (Data (Data'First + Result.Stored_Payload_Root'Position .. Data'First + Result.Stored_Payload_Root'Position + Result.Stored_Payload_Root'Size / System.Storage_Unit - 1));
      Result.Stored_Head := Load (Data (Data'First + Result.Stored_Head'Position .. Data'First + Result.Stored_Head'Position + Result.Stored_Head'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return D.Raw_Capability is
      Result : D.Raw_Capability;
   begin
      Result.Index := Load (Data (Data'First + Result.Index'Position .. Data'First + Result.Index'Position + Result.Index'Size / System.Storage_Unit - 1));
      Result.Bounding := Load (Data (Data'First + Result.Bounding'Position .. Data'First + Result.Bounding'Position + Result.Bounding'Size / System.Storage_Unit - 1));
      Result.Ambient := Load (Data (Data'First + Result.Ambient'Position .. Data'First + Result.Ambient'Position + Result.Ambient'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Scope_Frame is
      Result : N.Raw_Scope_Frame;
   begin
      Result.Scope := Load (Data (Data'First + Result.Scope'Position .. Data'First + Result.Scope'Position + Result.Scope'Size / System.Storage_Unit - 1));
      Result.First_Epoch := Load (Data (Data'First + Result.First_Epoch'Position .. Data'First + Result.First_Epoch'Position + Result.First_Epoch'Size / System.Storage_Unit - 1));
      Result.Universe_Head := Load (Data (Data'First + Result.Universe_Head'Position .. Data'First + Result.Universe_Head'Position + Result.Universe_Head'Size / System.Storage_Unit - 1));
      Result.Frame_Head := Load (Data (Data'First + Result.Frame_Head'Position .. Data'First + Result.Frame_Head'Position + Result.Frame_Head'Size / System.Storage_Unit - 1));
      Result.Prior_Frame := Load (Data (Data'First + Result.Prior_Frame'Position .. Data'First + Result.Prior_Frame'Position + Result.Prior_Frame'Size / System.Storage_Unit - 1));
      Result.Store_Genesis := Load (Data (Data'First + Result.Store_Genesis'Position .. Data'First + Result.Store_Genesis'Position + Result.Store_Genesis'Size / System.Storage_Unit - 1));
      Result.Store_Id := Load (Data (Data'First + Result.Store_Id'Position .. Data'First + Result.Store_Id'Position + Result.Store_Id'Size / System.Storage_Unit - 1));
      Result.Root_Head := Load (Data (Data'First + Result.Root_Head'Position .. Data'First + Result.Root_Head'Position + Result.Root_Head'Size / System.Storage_Unit - 1));
      Result.Prime := Load (Data (Data'First + Result.Prime'Position .. Data'First + Result.Prime'Position + Result.Prime'Size / System.Storage_Unit - 1));
      Result.Root_Count := Load (Data (Data'First + Result.Root_Count'Position .. Data'First + Result.Root_Count'Position + Result.Root_Count'Size / System.Storage_Unit - 1));
      Result.Cause := Load (Data (Data'First + Result.Cause'Position .. Data'First + Result.Cause'Position + Result.Cause'Size / System.Storage_Unit - 1));
      Result.Requester := Load (Data (Data'First + Result.Requester'Position .. Data'First + Result.Requester'Position + Result.Requester'Size / System.Storage_Unit - 1));
      Result.Receipt := Load (Data (Data'First + Result.Receipt'Position .. Data'First + Result.Receipt'Position + Result.Receipt'Size / System.Storage_Unit - 1));
      Result.Catalogue_Head := Load (Data (Data'First + Result.Catalogue_Head'Position .. Data'First + Result.Catalogue_Head'Position + Result.Catalogue_Head'Size / System.Storage_Unit - 1));
      Result.Observation_Head := Load (Data (Data'First + Result.Observation_Head'Position .. Data'First + Result.Observation_Head'Position + Result.Observation_Head'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Projection is
      Result : N.Raw_Projection;
   begin
      Result.Key := Load (Data (Data'First + Result.Key'Position .. Data'First + Result.Key'Position + Result.Key'Size / System.Storage_Unit - 1));
      Result.Bound := Load (Data (Data'First + Result.Bound'Position .. Data'First + Result.Bound'Position + Result.Bound'Size / System.Storage_Unit - 1));
      Result.Origin := Load (Data (Data'First + Result.Origin'Position .. Data'First + Result.Origin'Position + Result.Origin'Size / System.Storage_Unit - 1));
      Result.Catalogue_Head := Load (Data (Data'First + Result.Catalogue_Head'Position .. Data'First + Result.Catalogue_Head'Position + Result.Catalogue_Head'Size / System.Storage_Unit - 1));
      Result.Numerator := Load (Data (Data'First + Result.Numerator'Position .. Data'First + Result.Numerator'Position + Result.Numerator'Size / System.Storage_Unit - 1));
      Result.Denominator := Load (Data (Data'First + Result.Denominator'Position .. Data'First + Result.Denominator'Position + Result.Denominator'Size / System.Storage_Unit - 1));
      Result.Amount := Load (Data (Data'First + Result.Amount'Position .. Data'First + Result.Amount'Position + Result.Amount'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Physical_Key is
      Result : N.Raw_Physical_Key;
   begin
      Result.Machine := Load (Data (Data'First + Result.Machine'Position .. Data'First + Result.Machine'Position + Result.Machine'Size / System.Storage_Unit - 1));
      Result.Resource := Load (Data (Data'First + Result.Resource'Position .. Data'First + Result.Resource'Position + Result.Resource'Size / System.Storage_Unit - 1));
      Result.Unit := Load (Data (Data'First + Result.Unit'Position .. Data'First + Result.Unit'Position + Result.Unit'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Bucket is
      Result : N.Raw_Bucket;
   begin
      Result.Key := Load (Data (Data'First + Result.Key'Position .. Data'First + Result.Key'Position + Result.Key'Size / System.Storage_Unit - 1));
      Result.Capacity := Load (Data (Data'First + Result.Capacity'Position .. Data'First + Result.Capacity'Position + Result.Capacity'Size / System.Storage_Unit - 1));
      Result.Held_Total := Load (Data (Data'First + Result.Held_Total'Position .. Data'First + Result.Held_Total'Position + Result.Held_Total'Size / System.Storage_Unit - 1));
      Result.Charged_Total := Load (Data (Data'First + Result.Charged_Total'Position .. Data'First + Result.Charged_Total'Position + Result.Charged_Total'Size / System.Storage_Unit - 1));
      Result.Capacity_Source := Load (Data (Data'First + Result.Capacity_Source'Position .. Data'First + Result.Capacity_Source'Position + Result.Capacity_Source'Size / System.Storage_Unit - 1));
      Result.Catalogue_Head := Load (Data (Data'First + Result.Catalogue_Head'Position .. Data'First + Result.Catalogue_Head'Position + Result.Catalogue_Head'Size / System.Storage_Unit - 1));
      Result.Observation_Head := Load (Data (Data'First + Result.Observation_Head'Position .. Data'First + Result.Observation_Head'Position + Result.Observation_Head'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Native is
      Result : W.Raw_Native;
   begin
      Result.Scope := Load (Data (Data'First + Result.Scope'Position .. Data'First + Result.Scope'Position + Result.Scope'Size / System.Storage_Unit - 1));
      Result.Resource_Epoch := Load (Data (Data'First + Result.Resource_Epoch'Position .. Data'First + Result.Resource_Epoch'Position + Result.Resource_Epoch'Size / System.Storage_Unit - 1));
      Result.Bound := Load (Data (Data'First + Result.Bound'Position .. Data'First + Result.Bound'Position + Result.Bound'Size / System.Storage_Unit - 1));
      Result.Actual_Unit := Load (Data (Data'First + Result.Actual_Unit'Position .. Data'First + Result.Actual_Unit'Position + Result.Actual_Unit'Size / System.Storage_Unit - 1));
      Result.Cgroup := Load (Data (Data'First + Result.Cgroup'Position .. Data'First + Result.Cgroup'Position + Result.Cgroup'Size / System.Storage_Unit - 1));
      Result.Invocation := Load (Data (Data'First + Result.Invocation'Position .. Data'First + Result.Invocation'Position + Result.Invocation'Size / System.Storage_Unit - 1));
      Result.Observation_Head := Load (Data (Data'First + Result.Observation_Head'Position .. Data'First + Result.Observation_Head'Position + Result.Observation_Head'Size / System.Storage_Unit - 1));
      Result.Observed := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Observed'Position .. Data'First + Result.Observed'Position + Result.Observed'Size / System.Storage_Unit - 1)));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return O.Raw_Facts is
      Result : O.Raw_Facts;
   begin
      Result.Current := Load (Data (Data'First + Result.Current'Position .. Data'First + Result.Current'Position + Result.Current'Size / System.Storage_Unit - 1));
      Result.Current_Epoch := Load (Data (Data'First + Result.Current_Epoch'Position .. Data'First + Result.Current_Epoch'Position + Result.Current_Epoch'Size / System.Storage_Unit - 1));
      Result.Retained := Load (Data (Data'First + Result.Retained'Position .. Data'First + Result.Retained'Position + Result.Retained'Size / System.Storage_Unit - 1));
      Result.Current_Universe_Head := Load (Data (Data'First + Result.Current_Universe_Head'Position .. Data'First + Result.Current_Universe_Head'Position + Result.Current_Universe_Head'Size / System.Storage_Unit - 1));
      Result.Current_Ledger_Head := Load (Data (Data'First + Result.Current_Ledger_Head'Position .. Data'First + Result.Current_Ledger_Head'Position + Result.Current_Ledger_Head'Size / System.Storage_Unit - 1));
      Result.Intent := Load (Data (Data'First + Result.Intent'Position .. Data'First + Result.Intent'Position + Result.Intent'Size / System.Storage_Unit - 1));
      Result.Dispatch := Load (Data (Data'First + Result.Dispatch'Position .. Data'First + Result.Dispatch'Position + Result.Dispatch'Size / System.Storage_Unit - 1));
      Result.Observation_Head := Load (Data (Data'First + Result.Observation_Head'Position .. Data'First + Result.Observation_Head'Position + Result.Observation_Head'Size / System.Storage_Unit - 1));
      Result.Actual_Unit := Load (Data (Data'First + Result.Actual_Unit'Position .. Data'First + Result.Actual_Unit'Position + Result.Actual_Unit'Size / System.Storage_Unit - 1));
      Result.Cgroup := Load (Data (Data'First + Result.Cgroup'Position .. Data'First + Result.Cgroup'Position + Result.Cgroup'Size / System.Storage_Unit - 1));
      Result.Invocation := Load (Data (Data'First + Result.Invocation'Position .. Data'First + Result.Invocation'Position + Result.Invocation'Size / System.Storage_Unit - 1));
      Result.Namespace := Load (Data (Data'First + Result.Namespace'Position .. Data'First + Result.Namespace'Position + Result.Namespace'Size / System.Storage_Unit - 1));
      Result.Held_Namespace := Load (Data (Data'First + Result.Held_Namespace'Position .. Data'First + Result.Held_Namespace'Position + Result.Held_Namespace'Size / System.Storage_Unit - 1));
      Result.Peer := Load (Data (Data'First + Result.Peer'Position .. Data'First + Result.Peer'Position + Result.Peer'Size / System.Storage_Unit - 1));
      Result.Held_Peer := Load (Data (Data'First + Result.Held_Peer'Position .. Data'First + Result.Held_Peer'Position + Result.Held_Peer'Size / System.Storage_Unit - 1));
      Result.Helper_Image := Load (Data (Data'First + Result.Helper_Image'Position .. Data'First + Result.Helper_Image'Position + Result.Helper_Image'Size / System.Storage_Unit - 1));
      Result.Expected_Helper_Image := Load (Data (Data'First + Result.Expected_Helper_Image'Position .. Data'First + Result.Expected_Helper_Image'Position + Result.Expected_Helper_Image'Size / System.Storage_Unit - 1));
      Result.Challenge := Load (Data (Data'First + Result.Challenge'Position .. Data'First + Result.Challenge'Position + Result.Challenge'Size / System.Storage_Unit - 1));
      Result.Held_Challenge := Load (Data (Data'First + Result.Held_Challenge'Position .. Data'First + Result.Held_Challenge'Position + Result.Held_Challenge'Size / System.Storage_Unit - 1));
      Result.Protocol := Load (Data (Data'First + Result.Protocol'Position .. Data'First + Result.Protocol'Position + Result.Protocol'Size / System.Storage_Unit - 1));
      Result.Closed_Event := Load (Data (Data'First + Result.Closed_Event'Position .. Data'First + Result.Closed_Event'Position + Result.Closed_Event'Size / System.Storage_Unit - 1));
      Result.Namespace_Wait := Load (Data (Data'First + Result.Namespace_Wait'Position .. Data'First + Result.Namespace_Wait'Position + Result.Namespace_Wait'Size / System.Storage_Unit - 1));
      Result.Helper_Wait := Load (Data (Data'First + Result.Helper_Wait'Position .. Data'First + Result.Helper_Wait'Position + Result.Helper_Wait'Size / System.Storage_Unit - 1));
      Result.Cgroup_Events := Load (Data (Data'First + Result.Cgroup_Events'Position .. Data'First + Result.Cgroup_Events'Position + Result.Cgroup_Events'Size / System.Storage_Unit - 1));
      Result.Cgroup_Type := Load (Data (Data'First + Result.Cgroup_Type'Position .. Data'First + Result.Cgroup_Type'Position + Result.Cgroup_Type'Size / System.Storage_Unit - 1));
      Result.Manager_Delegate := Load (Data (Data'First + Result.Manager_Delegate'Position .. Data'First + Result.Manager_Delegate'Position + Result.Manager_Delegate'Size / System.Storage_Unit - 1));
      Result.Cgroup_Owner := Load (Data (Data'First + Result.Cgroup_Owner'Position .. Data'First + Result.Cgroup_Owner'Position + Result.Cgroup_Owner'Size / System.Storage_Unit - 1));
      Result.Cgroup_Group_Write := Load (Data (Data'First + Result.Cgroup_Group_Write'Position .. Data'First + Result.Cgroup_Group_Write'Position + Result.Cgroup_Group_Write'Size / System.Storage_Unit - 1));
      Result.Cgroup_Other_Write := Load (Data (Data'First + Result.Cgroup_Other_Write'Position .. Data'First + Result.Cgroup_Other_Write'Position + Result.Cgroup_Other_Write'Size / System.Storage_Unit - 1));
      Result.Actual_Store_Genesis := Load (Data (Data'First + Result.Actual_Store_Genesis'Position .. Data'First + Result.Actual_Store_Genesis'Position + Result.Actual_Store_Genesis'Size / System.Storage_Unit - 1));
      Result.Actual_Store_Id := Load (Data (Data'First + Result.Actual_Store_Id'Position .. Data'First + Result.Actual_Store_Id'Position + Result.Actual_Store_Id'Size / System.Storage_Unit - 1));
      Result.Owner_Store_Genesis := Load (Data (Data'First + Result.Owner_Store_Genesis'Position .. Data'First + Result.Owner_Store_Genesis'Position + Result.Owner_Store_Genesis'Size / System.Storage_Unit - 1));
      Result.Owner_Store_Id := Load (Data (Data'First + Result.Owner_Store_Id'Position .. Data'First + Result.Owner_Store_Id'Position + Result.Owner_Store_Id'Size / System.Storage_Unit - 1));
      Result.Genesis_Universe := Load (Data (Data'First + Result.Genesis_Universe'Position .. Data'First + Result.Genesis_Universe'Position + Result.Genesis_Universe'Size / System.Storage_Unit - 1));
      Result.Genesis_Instance := Load (Data (Data'First + Result.Genesis_Instance'Position .. Data'First + Result.Genesis_Instance'Position + Result.Genesis_Instance'Size / System.Storage_Unit - 1));
      Result.Genesis_Context_Head := Load (Data (Data'First + Result.Genesis_Context_Head'Position .. Data'First + Result.Genesis_Context_Head'Position + Result.Genesis_Context_Head'Size / System.Storage_Unit - 1));
      Result.Genesis_Prime := Load (Data (Data'First + Result.Genesis_Prime'Position .. Data'First + Result.Genesis_Prime'Position + Result.Genesis_Prime'Size / System.Storage_Unit - 1));
      Result.Genesis_Root_Count := Load (Data (Data'First + Result.Genesis_Root_Count'Position .. Data'First + Result.Genesis_Root_Count'Position + Result.Genesis_Root_Count'Size / System.Storage_Unit - 1));
      Result.Phase := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Phase'Position .. Data'First + Result.Phase'Position + Result.Phase'Size / System.Storage_Unit - 1)));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Result is
      Result : W.Raw_Result;
   begin
      Result.Status := Interfaces.Unsigned_32 (Little_Endian (Data (Data'First + Result.Status'Position .. Data'First + Result.Status'Position + Result.Status'Size / System.Storage_Unit - 1)));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Result is
      Result : T.Raw_Result;
   begin
      Result.Disposition := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Disposition'Position .. Data'First + Result.Disposition'Position + Result.Disposition'Size / System.Storage_Unit - 1)));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return HC.Raw_Input is
      Result : HC.Raw_Input;
   begin
      Result.Historical := Load (Data (Data'First + Result.Historical'Position .. Data'First + Result.Historical'Position + Result.Historical'Size / System.Storage_Unit - 1));
      Result.Current := Load (Data (Data'First + Result.Current'Position .. Data'First + Result.Current'Position + Result.Current'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return CX.Raw_Input is
      Result : CX.Raw_Input;
   begin
      Result.Operation_Input := Load (Data (Data'First + Result.Operation_Input'Position .. Data'First + Result.Operation_Input'Position + Result.Operation_Input'Size / System.Storage_Unit - 1));
      Result.Material := Load (Data (Data'First + Result.Material'Position .. Data'First + Result.Material'Position + Result.Material'Size / System.Storage_Unit - 1));
      Result.Before := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Before'Position .. Data'First + Result.Before'Position + Result.Before'Size / System.Storage_Unit - 1)));
      Result.Mode := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Mode'Position .. Data'First + Result.Mode'Position + Result.Mode'Size / System.Storage_Unit - 1)));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return CO.Raw_Input is
      Result : CO.Raw_Input;
   begin
      Result.Authority := Load (Data (Data'First + Result.Authority'Position .. Data'First + Result.Authority'Position + Result.Authority'Size / System.Storage_Unit - 1));
      Result.State := Load (Data (Data'First + Result.State'Position .. Data'First + Result.State'Position + Result.State'Size / System.Storage_Unit - 1));
      Result.Bound := Load (Data (Data'First + Result.Bound'Position .. Data'First + Result.Bound'Position + Result.Bound'Size / System.Storage_Unit - 1));
      Result.Requester := Load (Data (Data'First + Result.Requester'Position .. Data'First + Result.Requester'Position + Result.Requester'Size / System.Storage_Unit - 1));
      Result.Peer := Load (Data (Data'First + Result.Peer'Position .. Data'First + Result.Peer'Position + Result.Peer'Size / System.Storage_Unit - 1));
      Result.Collapse := Load (Data (Data'First + Result.Collapse'Position .. Data'First + Result.Collapse'Position + Result.Collapse'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_State is
      Result : W.Raw_State;
   begin
      Result.Scope := Load (Data (Data'First + Result.Scope'Position .. Data'First + Result.Scope'Position + Result.Scope'Size / System.Storage_Unit - 1));
      Result.Resource_Epoch := Load (Data (Data'First + Result.Resource_Epoch'Position .. Data'First + Result.Resource_Epoch'Position + Result.Resource_Epoch'Size / System.Storage_Unit - 1));
      Result.Universe_Head := Load (Data (Data'First + Result.Universe_Head'Position .. Data'First + Result.Universe_Head'Position + Result.Universe_Head'Size / System.Storage_Unit - 1));
      Result.Ledger_Head := Load (Data (Data'First + Result.Ledger_Head'Position .. Data'First + Result.Ledger_Head'Position + Result.Ledger_Head'Size / System.Storage_Unit - 1));
      Result.Capacity := Load (Data (Data'First + Result.Capacity'Position .. Data'First + Result.Capacity'Position + Result.Capacity'Size / System.Storage_Unit - 1));
      Result.Held_Total := Load (Data (Data'First + Result.Held_Total'Position .. Data'First + Result.Held_Total'Position + Result.Held_Total'Size / System.Storage_Unit - 1));
      Result.Charged_Total := Load (Data (Data'First + Result.Charged_Total'Position .. Data'First + Result.Charged_Total'Position + Result.Charged_Total'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return CW.Raw_Request is
      Result : CW.Raw_Request;
   begin
      Result.Candidate_State := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Candidate_State'Position .. Data'First + Result.Candidate_State'Position + Result.Candidate_State'Size / System.Storage_Unit - 1)));
      Result.Phase := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Phase'Position .. Data'First + Result.Phase'Position + Result.Phase'Size / System.Storage_Unit - 1)));
      Result.Evaluation_Mode := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Evaluation_Mode'Position .. Data'First + Result.Evaluation_Mode'Position + Result.Evaluation_Mode'Size / System.Storage_Unit - 1)));
      Result.Conflicts := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Conflicts'Position .. Data'First + Result.Conflicts'Position + Result.Conflicts'Size / System.Storage_Unit - 1)));
      Result.Foreign_Writes := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Foreign_Writes'Position .. Data'First + Result.Foreign_Writes'Position + Result.Foreign_Writes'Size / System.Storage_Unit - 1)));
      Result.Roster_Complete := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Roster_Complete'Position .. Data'First + Result.Roster_Complete'Position + Result.Roster_Complete'Size / System.Storage_Unit - 1)));
      Result.Staged_Roster_Complete := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Staged_Roster_Complete'Position .. Data'First + Result.Staged_Roster_Complete'Position + Result.Staged_Roster_Complete'Size / System.Storage_Unit - 1)));
      Result.Expected_Parent := Load (Data (Data'First + Result.Expected_Parent'Position .. Data'First + Result.Expected_Parent'Position + Result.Expected_Parent'Size / System.Storage_Unit - 1));
      Result.Candidate_Parent := Load (Data (Data'First + Result.Candidate_Parent'Position .. Data'First + Result.Candidate_Parent'Position + Result.Candidate_Parent'Size / System.Storage_Unit - 1));
      Result.Expected_Subject := Load (Data (Data'First + Result.Expected_Subject'Position .. Data'First + Result.Expected_Subject'Position + Result.Expected_Subject'Size / System.Storage_Unit - 1));
      Result.Evidence_Subject := Load (Data (Data'First + Result.Evidence_Subject'Position .. Data'First + Result.Evidence_Subject'Position + Result.Evidence_Subject'Size / System.Storage_Unit - 1));
      Result.Expected_Base := Load (Data (Data'First + Result.Expected_Base'Position .. Data'First + Result.Expected_Base'Position + Result.Expected_Base'Size / System.Storage_Unit - 1));
      Result.Candidate_Base := Load (Data (Data'First + Result.Candidate_Base'Position .. Data'First + Result.Candidate_Base'Position + Result.Candidate_Base'Size / System.Storage_Unit - 1));
      Result.Expected_Delta := Load (Data (Data'First + Result.Expected_Delta'Position .. Data'First + Result.Expected_Delta'Position + Result.Expected_Delta'Size / System.Storage_Unit - 1));
      Result.Candidate_Delta := Load (Data (Data'First + Result.Candidate_Delta'Position .. Data'First + Result.Candidate_Delta'Position + Result.Candidate_Delta'Size / System.Storage_Unit - 1));
      Result.Expected_Root_Set := Load (Data (Data'First + Result.Expected_Root_Set'Position .. Data'First + Result.Expected_Root_Set'Position + Result.Expected_Root_Set'Size / System.Storage_Unit - 1));
      Result.Candidate_Root_Set := Load (Data (Data'First + Result.Candidate_Root_Set'Position .. Data'First + Result.Candidate_Root_Set'Position + Result.Candidate_Root_Set'Size / System.Storage_Unit - 1));
      Result.Expected_Staged_Root := Load (Data (Data'First + Result.Expected_Staged_Root'Position .. Data'First + Result.Expected_Staged_Root'Position + Result.Expected_Staged_Root'Size / System.Storage_Unit - 1));
      Result.Actual_Staged_Root := Load (Data (Data'First + Result.Actual_Staged_Root'Position .. Data'First + Result.Actual_Staged_Root'Position + Result.Actual_Staged_Root'Size / System.Storage_Unit - 1));
      Result.Staged_Content_Root := Load (Data (Data'First + Result.Staged_Content_Root'Position .. Data'First + Result.Staged_Content_Root'Position + Result.Staged_Content_Root'Size / System.Storage_Unit - 1));
      Result.Tested_Root := Load (Data (Data'First + Result.Tested_Root'Position .. Data'First + Result.Tested_Root'Position + Result.Tested_Root'Size / System.Storage_Unit - 1));
      Result.Current_Requirement := Load (Data (Data'First + Result.Current_Requirement'Position .. Data'First + Result.Current_Requirement'Position + Result.Current_Requirement'Size / System.Storage_Unit - 1));
      Result.Resulting_Requirement := Load (Data (Data'First + Result.Resulting_Requirement'Position .. Data'First + Result.Resulting_Requirement'Position + Result.Resulting_Requirement'Size / System.Storage_Unit - 1));
      Result.Evaluated_Requirement := Load (Data (Data'First + Result.Evaluated_Requirement'Position .. Data'First + Result.Evaluated_Requirement'Position + Result.Evaluated_Requirement'Size / System.Storage_Unit - 1));
      Result.Declared_Verifiers := Load (Data (Data'First + Result.Declared_Verifiers'Position .. Data'First + Result.Declared_Verifiers'Position + Result.Declared_Verifiers'Size / System.Storage_Unit - 1));
      Result.Executed_Verifiers := Load (Data (Data'First + Result.Executed_Verifiers'Position .. Data'First + Result.Executed_Verifiers'Position + Result.Executed_Verifiers'Size / System.Storage_Unit - 1));
      Result.Staged_Evaluated_Requirement := Load (Data (Data'First + Result.Staged_Evaluated_Requirement'Position .. Data'First + Result.Staged_Evaluated_Requirement'Position + Result.Staged_Evaluated_Requirement'Size / System.Storage_Unit - 1));
      Result.Staged_Executed_Verifiers := Load (Data (Data'First + Result.Staged_Executed_Verifiers'Position .. Data'First + Result.Staged_Executed_Verifiers'Position + Result.Staged_Executed_Verifiers'Size / System.Storage_Unit - 1));
      Result.Staged_Examined_Root := Load (Data (Data'First + Result.Staged_Examined_Root'Position .. Data'First + Result.Staged_Examined_Root'Position + Result.Staged_Examined_Root'Size / System.Storage_Unit - 1));
      Result.Expected_Checkpoint := Load (Data (Data'First + Result.Expected_Checkpoint'Position .. Data'First + Result.Expected_Checkpoint'Position + Result.Expected_Checkpoint'Size / System.Storage_Unit - 1));
      Result.Witnessed_Checkpoint := Load (Data (Data'First + Result.Witnessed_Checkpoint'Position .. Data'First + Result.Witnessed_Checkpoint'Position + Result.Witnessed_Checkpoint'Size / System.Storage_Unit - 1));
      Result.Registered_Watch_Set := Load (Data (Data'First + Result.Registered_Watch_Set'Position .. Data'First + Result.Registered_Watch_Set'Position + Result.Registered_Watch_Set'Size / System.Storage_Unit - 1));
      Result.Watched_Set := Load (Data (Data'First + Result.Watched_Set'Position .. Data'First + Result.Watched_Set'Position + Result.Watched_Set'Size / System.Storage_Unit - 1));
      Result.Generation_Before := Load (Data (Data'First + Result.Generation_Before'Position .. Data'First + Result.Generation_Before'Position + Result.Generation_Before'Size / System.Storage_Unit - 1));
      Result.Generation_After := Load (Data (Data'First + Result.Generation_After'Position .. Data'First + Result.Generation_After'Position + Result.Generation_After'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return CW.Raw_Optional_Hash is
      Result : CW.Raw_Optional_Hash;
   begin
      Result.Present := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Present'Position .. Data'First + Result.Present'Position + Result.Present'Size / System.Storage_Unit - 1)));
      Result.Value := Load (Data (Data'First + Result.Value'Position .. Data'First + Result.Value'Position + Result.Value'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return CW.Raw_Bytes_32 is
      Result : CW.Raw_Bytes_32;
   begin
      for I in Result'Range loop
         Result (I) := Data (Data'First + Q.Byte_Count (I - Result'First));
      end loop;
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return CW.Raw_Optional_Counter is
      Result : CW.Raw_Optional_Counter;
   begin
      Result.Present := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Present'Position .. Data'First + Result.Present'Position + Result.Present'Size / System.Storage_Unit - 1)));
      Result.Value_LE := Load (Data (Data'First + Result.Value_LE'Position .. Data'First + Result.Value_LE'Position + Result.Value_LE'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return CW.Raw_Bytes_8 is
      Result : CW.Raw_Bytes_8;
   begin
      for I in Result'Range loop
         Result (I) := Data (Data'First + Q.Byte_Count (I - Result'First));
      end loop;
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return CX.Raw_Material is
      Result : CX.Raw_Material;
   begin
      Result.Worker_Issued := Load (Data (Data'First + Result.Worker_Issued'Position .. Data'First + Result.Worker_Issued'Position + Result.Worker_Issued'Size / System.Storage_Unit - 1));
      Result.Worker_Recovered := Load (Data (Data'First + Result.Worker_Recovered'Position .. Data'First + Result.Worker_Recovered'Position + Result.Worker_Recovered'Size / System.Storage_Unit - 1));
      Result.Canonical_Issued := Load (Data (Data'First + Result.Canonical_Issued'Position .. Data'First + Result.Canonical_Issued'Position + Result.Canonical_Issued'Size / System.Storage_Unit - 1));
      Result.Canonical_Recovered := Load (Data (Data'First + Result.Canonical_Recovered'Position .. Data'First + Result.Canonical_Recovered'Position + Result.Canonical_Recovered'Size / System.Storage_Unit - 1));
      Result.Worker_Native := Load (Data (Data'First + Result.Worker_Native'Position .. Data'First + Result.Worker_Native'Position + Result.Worker_Native'Size / System.Storage_Unit - 1));
      Result.Canonical_Native := Load (Data (Data'First + Result.Canonical_Native'Position .. Data'First + Result.Canonical_Native'Position + Result.Canonical_Native'Size / System.Storage_Unit - 1));
      Result.Worker_Receipt_Genesis := Load (Data (Data'First + Result.Worker_Receipt_Genesis'Position .. Data'First + Result.Worker_Receipt_Genesis'Position + Result.Worker_Receipt_Genesis'Size / System.Storage_Unit - 1));
      Result.Owner_Receipt_Genesis := Load (Data (Data'First + Result.Owner_Receipt_Genesis'Position .. Data'First + Result.Owner_Receipt_Genesis'Position + Result.Owner_Receipt_Genesis'Size / System.Storage_Unit - 1));
      Result.Worker_Receipt_Head := Load (Data (Data'First + Result.Worker_Receipt_Head'Position .. Data'First + Result.Worker_Receipt_Head'Position + Result.Worker_Receipt_Head'Size / System.Storage_Unit - 1));
      Result.Worker_Causal_Genesis := Load (Data (Data'First + Result.Worker_Causal_Genesis'Position .. Data'First + Result.Worker_Causal_Genesis'Position + Result.Worker_Causal_Genesis'Size / System.Storage_Unit - 1));
      Result.Owner_Causal_Genesis := Load (Data (Data'First + Result.Owner_Causal_Genesis'Position .. Data'First + Result.Owner_Causal_Genesis'Position + Result.Owner_Causal_Genesis'Size / System.Storage_Unit - 1));
      Result.Worker_Causal_Head := Load (Data (Data'First + Result.Worker_Causal_Head'Position .. Data'First + Result.Worker_Causal_Head'Position + Result.Worker_Causal_Head'Size / System.Storage_Unit - 1));
      Result.Quarantine_Head := Load (Data (Data'First + Result.Quarantine_Head'Position .. Data'First + Result.Quarantine_Head'Position + Result.Quarantine_Head'Size / System.Storage_Unit - 1));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return HC.Raw_Result is
      Result : HC.Raw_Result;
   begin
      Result.Disposition := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Disposition'Position .. Data'First + Result.Disposition'Position + Result.Disposition'Size / System.Storage_Unit - 1)));
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return CX.Raw_Result is
      Result : CX.Raw_Result;
   begin
      Result.Disposition := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Result.Disposition'Position .. Data'First + Result.Disposition'Position + Result.Disposition'Size / System.Storage_Unit - 1)));
      return Result;
   end Load;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : D.Raw_Packet) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Ledger'Position and then Offset - Raw.Ledger'Position < Raw.Ledger'Size / System.Storage_Unit) or else (Offset >= Raw.Captured'Position and then Offset - Raw.Captured'Position < Raw.Captured'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Ledger'Position .. Data'First + Raw.Ledger'Position + Raw.Ledger'Size / System.Storage_Unit - 1), Raw.Ledger)
        and then Source_Padding_Valid (Data (Data'First + Raw.Captured'Position .. Data'First + Raw.Captured'Position + Raw.Captured'Size / System.Storage_Unit - 1), Raw.Captured);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Packet) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Schema_Version'Position and then Offset - Raw.Schema_Version'Position < Raw.Schema_Version'Size / System.Storage_Unit) or else (Offset >= Raw.Before_State'Position and then Offset - Raw.Before_State'Position < Raw.Before_State'Size / System.Storage_Unit) or else (Offset >= Raw.Proposed_State'Position and then Offset - Raw.Proposed_State'Position < Raw.Proposed_State'Size / System.Storage_Unit) or else (Offset >= Raw.Current'Position and then Offset - Raw.Current'Position < Raw.Current'Size / System.Storage_Unit) or else (Offset >= Raw.Request'Position and then Offset - Raw.Request'Position < Raw.Request'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Before_State'Position .. Data'First + Raw.Before_State'Position + Raw.Before_State'Size / System.Storage_Unit - 1), Raw.Before_State)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proposed_State'Position .. Data'First + Raw.Proposed_State'Position + Raw.Proposed_State'Size / System.Storage_Unit - 1), Raw.Proposed_State)
        and then Source_Padding_Valid (Data (Data'First + Raw.Current'Position .. Data'First + Raw.Current'Position + Raw.Current'Size / System.Storage_Unit - 1), Raw.Current)
        and then Source_Padding_Valid (Data (Data'First + Raw.Request'Position .. Data'First + Raw.Request'Position + Raw.Request'Size / System.Storage_Unit - 1), Raw.Request);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_State) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Current'Position and then Offset - Raw.Current'Position < Raw.Current'Size / System.Storage_Unit) or else (Offset >= Raw.Resource_Epoch'Position and then Offset - Raw.Resource_Epoch'Position < Raw.Resource_Epoch'Size / System.Storage_Unit) or else (Offset >= Raw.Universe_Head'Position and then Offset - Raw.Universe_Head'Position < Raw.Universe_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Ledger_Head'Position and then Offset - Raw.Ledger_Head'Position < Raw.Ledger_Head'Size / System.Storage_Unit) or else (Offset >= Raw.History_Head'Position and then Offset - Raw.History_Head'Position < Raw.History_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Physical_Head'Position and then Offset - Raw.Physical_Head'Position < Raw.Physical_Head'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Current'Position .. Data'First + Raw.Current'Position + Raw.Current'Size / System.Storage_Unit - 1), Raw.Current)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource_Epoch'Position .. Data'First + Raw.Resource_Epoch'Position + Raw.Resource_Epoch'Size / System.Storage_Unit - 1), Raw.Resource_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Universe_Head'Position .. Data'First + Raw.Universe_Head'Position + Raw.Universe_Head'Size / System.Storage_Unit - 1), Raw.Universe_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Ledger_Head'Position .. Data'First + Raw.Ledger_Head'Position + Raw.Ledger_Head'Size / System.Storage_Unit - 1), Raw.Ledger_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.History_Head'Position .. Data'First + Raw.History_Head'Position + Raw.History_Head'Size / System.Storage_Unit - 1), Raw.History_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Physical_Head'Position .. Data'First + Raw.Physical_Head'Position + Raw.Physical_Head'Size / System.Storage_Unit - 1), Raw.Physical_Head);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Context) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Universe'Position and then Offset - Raw.Universe'Position < Raw.Universe'Size / System.Storage_Unit) or else (Offset >= Raw.Policy'Position and then Offset - Raw.Policy'Position < Raw.Policy'Size / System.Storage_Unit) or else (Offset >= Raw.Resource'Position and then Offset - Raw.Resource'Position < Raw.Resource'Size / System.Storage_Unit) or else (Offset >= Raw.Unit'Position and then Offset - Raw.Unit'Position < Raw.Unit'Size / System.Storage_Unit) or else (Offset >= Raw.Instance'Position and then Offset - Raw.Instance'Position < Raw.Instance'Size / System.Storage_Unit) or else (Offset >= Raw.Host'Position and then Offset - Raw.Host'Position < Raw.Host'Size / System.Storage_Unit) or else (Offset >= Raw.Boot'Position and then Offset - Raw.Boot'Position < Raw.Boot'Size / System.Storage_Unit) or else (Offset >= Raw.Authority'Position and then Offset - Raw.Authority'Position < Raw.Authority'Size / System.Storage_Unit) or else (Offset >= Raw.Policy_Epoch'Position and then Offset - Raw.Policy_Epoch'Position < Raw.Policy_Epoch'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Universe'Position .. Data'First + Raw.Universe'Position + Raw.Universe'Size / System.Storage_Unit - 1), Raw.Universe)
        and then Source_Padding_Valid (Data (Data'First + Raw.Policy'Position .. Data'First + Raw.Policy'Position + Raw.Policy'Size / System.Storage_Unit - 1), Raw.Policy)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource'Position .. Data'First + Raw.Resource'Position + Raw.Resource'Size / System.Storage_Unit - 1), Raw.Resource)
        and then Source_Padding_Valid (Data (Data'First + Raw.Unit'Position .. Data'First + Raw.Unit'Position + Raw.Unit'Size / System.Storage_Unit - 1), Raw.Unit)
        and then Source_Padding_Valid (Data (Data'First + Raw.Instance'Position .. Data'First + Raw.Instance'Position + Raw.Instance'Size / System.Storage_Unit - 1), Raw.Instance)
        and then Source_Padding_Valid (Data (Data'First + Raw.Host'Position .. Data'First + Raw.Host'Position + Raw.Host'Size / System.Storage_Unit - 1), Raw.Host)
        and then Source_Padding_Valid (Data (Data'First + Raw.Boot'Position .. Data'First + Raw.Boot'Position + Raw.Boot'Size / System.Storage_Unit - 1), Raw.Boot)
        and then Source_Padding_Valid (Data (Data'First + Raw.Authority'Position .. Data'First + Raw.Authority'Position + Raw.Authority'Size / System.Storage_Unit - 1), Raw.Authority)
        and then Source_Padding_Valid (Data (Data'First + Raw.Policy_Epoch'Position .. Data'First + Raw.Policy_Epoch'Position + Raw.Policy_Epoch'Size / System.Storage_Unit - 1), Raw.Policy_Epoch);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Id) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Present'Position and then Offset - Raw.Present'Position < Raw.Present'Size / System.Storage_Unit) or else (Offset >= Raw.First'Position and then Offset - Raw.First'Position < Raw.First'Size / System.Storage_Unit) or else (Offset >= Raw.Length'Position and then Offset - Raw.Length'Position < Raw.Length'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Epoch) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Present'Position and then Offset - Raw.Present'Position < Raw.Present'Size / System.Storage_Unit) or else (Offset >= Raw.Value'Position and then Offset - Raw.Value'Position < Raw.Value'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Value'Position .. Data'First + Raw.Value'Position + Raw.Value'Size / System.Storage_Unit - 1), Raw.Value);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Quantity) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Negative'Position and then Offset - Raw.Negative'Position < Raw.Negative'Size / System.Storage_Unit) or else (Offset >= Raw.First'Position and then Offset - Raw.First'Position < Raw.First'Size / System.Storage_Unit) or else (Offset >= Raw.Length'Position and then Offset - Raw.Length'Position < Raw.Length'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Current_Observation) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Scope'Position and then Offset - Raw.Scope'Position < Raw.Scope'Size / System.Storage_Unit) or else (Offset >= Raw.Resource_Epoch'Position and then Offset - Raw.Resource_Epoch'Position < Raw.Resource_Epoch'Size / System.Storage_Unit) or else (Offset >= Raw.Universe_Head'Position and then Offset - Raw.Universe_Head'Position < Raw.Universe_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Ledger_Head'Position and then Offset - Raw.Ledger_Head'Position < Raw.Ledger_Head'Size / System.Storage_Unit) or else (Offset >= Raw.History_Head'Position and then Offset - Raw.History_Head'Position < Raw.History_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Physical_Head'Position and then Offset - Raw.Physical_Head'Position < Raw.Physical_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Store_Genesis'Position and then Offset - Raw.Store_Genesis'Position < Raw.Store_Genesis'Size / System.Storage_Unit) or else (Offset >= Raw.Store_Id'Position and then Offset - Raw.Store_Id'Position < Raw.Store_Id'Size / System.Storage_Unit) or else (Offset >= Raw.Root_Head'Position and then Offset - Raw.Root_Head'Position < Raw.Root_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Prime'Position and then Offset - Raw.Prime'Position < Raw.Prime'Size / System.Storage_Unit) or else (Offset >= Raw.Root_Count'Position and then Offset - Raw.Root_Count'Position < Raw.Root_Count'Size / System.Storage_Unit) or else (Offset >= Raw.Cause'Position and then Offset - Raw.Cause'Position < Raw.Cause'Size / System.Storage_Unit) or else (Offset >= Raw.Requester'Position and then Offset - Raw.Requester'Position < Raw.Requester'Size / System.Storage_Unit) or else (Offset >= Raw.Receipt'Position and then Offset - Raw.Receipt'Position < Raw.Receipt'Size / System.Storage_Unit) or else (Offset >= Raw.Catalogue_Head'Position and then Offset - Raw.Catalogue_Head'Position < Raw.Catalogue_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Observation_Head'Position and then Offset - Raw.Observation_Head'Position < Raw.Observation_Head'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Scope'Position .. Data'First + Raw.Scope'Position + Raw.Scope'Size / System.Storage_Unit - 1), Raw.Scope)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource_Epoch'Position .. Data'First + Raw.Resource_Epoch'Position + Raw.Resource_Epoch'Size / System.Storage_Unit - 1), Raw.Resource_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Universe_Head'Position .. Data'First + Raw.Universe_Head'Position + Raw.Universe_Head'Size / System.Storage_Unit - 1), Raw.Universe_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Ledger_Head'Position .. Data'First + Raw.Ledger_Head'Position + Raw.Ledger_Head'Size / System.Storage_Unit - 1), Raw.Ledger_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.History_Head'Position .. Data'First + Raw.History_Head'Position + Raw.History_Head'Size / System.Storage_Unit - 1), Raw.History_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Physical_Head'Position .. Data'First + Raw.Physical_Head'Position + Raw.Physical_Head'Size / System.Storage_Unit - 1), Raw.Physical_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Store_Genesis'Position .. Data'First + Raw.Store_Genesis'Position + Raw.Store_Genesis'Size / System.Storage_Unit - 1), Raw.Store_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Store_Id'Position .. Data'First + Raw.Store_Id'Position + Raw.Store_Id'Size / System.Storage_Unit - 1), Raw.Store_Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Root_Head'Position .. Data'First + Raw.Root_Head'Position + Raw.Root_Head'Size / System.Storage_Unit - 1), Raw.Root_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Prime'Position .. Data'First + Raw.Prime'Position + Raw.Prime'Size / System.Storage_Unit - 1), Raw.Prime)
        and then Source_Padding_Valid (Data (Data'First + Raw.Root_Count'Position .. Data'First + Raw.Root_Count'Position + Raw.Root_Count'Size / System.Storage_Unit - 1), Raw.Root_Count)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cause'Position .. Data'First + Raw.Cause'Position + Raw.Cause'Size / System.Storage_Unit - 1), Raw.Cause)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester'Position .. Data'First + Raw.Requester'Position + Raw.Requester'Size / System.Storage_Unit - 1), Raw.Requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.Receipt'Position .. Data'First + Raw.Receipt'Position + Raw.Receipt'Size / System.Storage_Unit - 1), Raw.Receipt)
        and then Source_Padding_Valid (Data (Data'First + Raw.Catalogue_Head'Position .. Data'First + Raw.Catalogue_Head'Position + Raw.Catalogue_Head'Size / System.Storage_Unit - 1), Raw.Catalogue_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Observation_Head'Position .. Data'First + Raw.Observation_Head'Position + Raw.Observation_Head'Size / System.Storage_Unit - 1), Raw.Observation_Head);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Intent) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Kind'Position and then Offset - Raw.Kind'Position < Raw.Kind'Size / System.Storage_Unit) or else (Offset >= Raw.Original'Position and then Offset - Raw.Original'Position < Raw.Original'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Epoch'Position and then Offset - Raw.Expected_Epoch'Position < Raw.Expected_Epoch'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Ledger_Head'Position and then Offset - Raw.Expected_Ledger_Head'Position < Raw.Expected_Ledger_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Request_Id'Position and then Offset - Raw.Request_Id'Position < Raw.Request_Id'Size / System.Storage_Unit) or else (Offset >= Raw.Cause'Position and then Offset - Raw.Cause'Position < Raw.Cause'Size / System.Storage_Unit) or else (Offset >= Raw.Requester'Position and then Offset - Raw.Requester'Position < Raw.Requester'Size / System.Storage_Unit) or else (Offset >= Raw.Receipt'Position and then Offset - Raw.Receipt'Position < Raw.Receipt'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Original'Position .. Data'First + Raw.Original'Position + Raw.Original'Size / System.Storage_Unit - 1), Raw.Original)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Epoch'Position .. Data'First + Raw.Expected_Epoch'Position + Raw.Expected_Epoch'Size / System.Storage_Unit - 1), Raw.Expected_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Ledger_Head'Position .. Data'First + Raw.Expected_Ledger_Head'Position + Raw.Expected_Ledger_Head'Size / System.Storage_Unit - 1), Raw.Expected_Ledger_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Request_Id'Position .. Data'First + Raw.Request_Id'Position + Raw.Request_Id'Size / System.Storage_Unit - 1), Raw.Request_Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cause'Position .. Data'First + Raw.Cause'Position + Raw.Cause'Size / System.Storage_Unit - 1), Raw.Cause)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester'Position .. Data'First + Raw.Requester'Position + Raw.Requester'Size / System.Storage_Unit - 1), Raw.Requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.Receipt'Position .. Data'First + Raw.Receipt'Position + Raw.Receipt'Size / System.Storage_Unit - 1), Raw.Receipt);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Request) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Kind'Position and then Offset - Raw.Kind'Position < Raw.Kind'Size / System.Storage_Unit) or else (Offset >= Raw.Scope'Position and then Offset - Raw.Scope'Position < Raw.Scope'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Epoch'Position and then Offset - Raw.Expected_Epoch'Position < Raw.Expected_Epoch'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Ledger_Head'Position and then Offset - Raw.Expected_Ledger_Head'Position < Raw.Expected_Ledger_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Request_Id'Position and then Offset - Raw.Request_Id'Position < Raw.Request_Id'Size / System.Storage_Unit) or else (Offset >= Raw.Reservation'Position and then Offset - Raw.Reservation'Position < Raw.Reservation'Size / System.Storage_Unit) or else (Offset >= Raw.Operation_Id'Position and then Offset - Raw.Operation_Id'Position < Raw.Operation_Id'Size / System.Storage_Unit) or else (Offset >= Raw.Requester'Position and then Offset - Raw.Requester'Position < Raw.Requester'Size / System.Storage_Unit) or else (Offset >= Raw.Bound'Position and then Offset - Raw.Bound'Position < Raw.Bound'Size / System.Storage_Unit) or else (Offset >= Raw.New_Row'Position and then Offset - Raw.New_Row'Position < Raw.New_Row'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Scope'Position .. Data'First + Raw.Scope'Position + Raw.Scope'Size / System.Storage_Unit - 1), Raw.Scope)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Epoch'Position .. Data'First + Raw.Expected_Epoch'Position + Raw.Expected_Epoch'Size / System.Storage_Unit - 1), Raw.Expected_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Ledger_Head'Position .. Data'First + Raw.Expected_Ledger_Head'Position + Raw.Expected_Ledger_Head'Size / System.Storage_Unit - 1), Raw.Expected_Ledger_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Request_Id'Position .. Data'First + Raw.Request_Id'Position + Raw.Request_Id'Size / System.Storage_Unit - 1), Raw.Request_Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Reservation'Position .. Data'First + Raw.Reservation'Position + Raw.Reservation'Size / System.Storage_Unit - 1), Raw.Reservation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Operation_Id'Position .. Data'First + Raw.Operation_Id'Position + Raw.Operation_Id'Size / System.Storage_Unit - 1), Raw.Operation_Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester'Position .. Data'First + Raw.Requester'Position + Raw.Requester'Size / System.Storage_Unit - 1), Raw.Requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1), Raw.Bound)
        and then Source_Padding_Valid (Data (Data'First + Raw.New_Row'Position .. Data'First + Raw.New_Row'Position + Raw.New_Row'Size / System.Storage_Unit - 1), Raw.New_Row);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Binding) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Reservation'Position and then Offset - Raw.Reservation'Position < Raw.Reservation'Size / System.Storage_Unit) or else (Offset >= Raw.Operation'Position and then Offset - Raw.Operation'Position < Raw.Operation'Size / System.Storage_Unit) or else (Offset >= Raw.Owner'Position and then Offset - Raw.Owner'Position < Raw.Owner'Size / System.Storage_Unit) or else (Offset >= Raw.Workload'Position and then Offset - Raw.Workload'Position < Raw.Workload'Size / System.Storage_Unit) or else (Offset >= Raw.Universe_Head'Position and then Offset - Raw.Universe_Head'Position < Raw.Universe_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Capability'Position and then Offset - Raw.Capability'Position < Raw.Capability'Size / System.Storage_Unit) or else (Offset >= Raw.Grant_Use'Position and then Offset - Raw.Grant_Use'Position < Raw.Grant_Use'Size / System.Storage_Unit) or else (Offset >= Raw.Payload'Position and then Offset - Raw.Payload'Position < Raw.Payload'Size / System.Storage_Unit) or else (Offset >= Raw.Provenance'Position and then Offset - Raw.Provenance'Position < Raw.Provenance'Size / System.Storage_Unit) or else (Offset >= Raw.Resource_Epoch'Position and then Offset - Raw.Resource_Epoch'Position < Raw.Resource_Epoch'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Reservation'Position .. Data'First + Raw.Reservation'Position + Raw.Reservation'Size / System.Storage_Unit - 1), Raw.Reservation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Operation'Position .. Data'First + Raw.Operation'Position + Raw.Operation'Size / System.Storage_Unit - 1), Raw.Operation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner'Position .. Data'First + Raw.Owner'Position + Raw.Owner'Size / System.Storage_Unit - 1), Raw.Owner)
        and then Source_Padding_Valid (Data (Data'First + Raw.Workload'Position .. Data'First + Raw.Workload'Position + Raw.Workload'Size / System.Storage_Unit - 1), Raw.Workload)
        and then Source_Padding_Valid (Data (Data'First + Raw.Universe_Head'Position .. Data'First + Raw.Universe_Head'Position + Raw.Universe_Head'Size / System.Storage_Unit - 1), Raw.Universe_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Capability'Position .. Data'First + Raw.Capability'Position + Raw.Capability'Size / System.Storage_Unit - 1), Raw.Capability)
        and then Source_Padding_Valid (Data (Data'First + Raw.Grant_Use'Position .. Data'First + Raw.Grant_Use'Position + Raw.Grant_Use'Size / System.Storage_Unit - 1), Raw.Grant_Use)
        and then Source_Padding_Valid (Data (Data'First + Raw.Payload'Position .. Data'First + Raw.Payload'Position + Raw.Payload'Size / System.Storage_Unit - 1), Raw.Payload)
        and then Source_Padding_Valid (Data (Data'First + Raw.Provenance'Position .. Data'First + Raw.Provenance'Position + Raw.Provenance'Size / System.Storage_Unit - 1), Raw.Provenance)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource_Epoch'Position .. Data'First + Raw.Resource_Epoch'Position + Raw.Resource_Epoch'Size / System.Storage_Unit - 1), Raw.Resource_Epoch);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Row) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Scope'Position and then Offset - Raw.Scope'Position < Raw.Scope'Size / System.Storage_Unit) or else (Offset >= Raw.Bound'Position and then Offset - Raw.Bound'Position < Raw.Bound'Size / System.Storage_Unit) or else (Offset >= Raw.Parent'Position and then Offset - Raw.Parent'Position < Raw.Parent'Size / System.Storage_Unit) or else (Offset >= Raw.Kind'Position and then Offset - Raw.Kind'Position < Raw.Kind'Size / System.Storage_Unit) or else (Offset >= Raw.State'Position and then Offset - Raw.State'Position < Raw.State'Size / System.Storage_Unit) or else (Offset >= Raw.Amount'Position and then Offset - Raw.Amount'Position < Raw.Amount'Size / System.Storage_Unit) or else (Offset >= Raw.Observed_Usage'Position and then Offset - Raw.Observed_Usage'Position < Raw.Observed_Usage'Size / System.Storage_Unit) or else (Offset >= Raw.Planned_Unit'Position and then Offset - Raw.Planned_Unit'Position < Raw.Planned_Unit'Size / System.Storage_Unit) or else (Offset >= Raw.Actual_Unit'Position and then Offset - Raw.Actual_Unit'Position < Raw.Actual_Unit'Size / System.Storage_Unit) or else (Offset >= Raw.Cgroup'Position and then Offset - Raw.Cgroup'Position < Raw.Cgroup'Size / System.Storage_Unit) or else (Offset >= Raw.Invocation'Position and then Offset - Raw.Invocation'Position < Raw.Invocation'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Scope'Position .. Data'First + Raw.Scope'Position + Raw.Scope'Size / System.Storage_Unit - 1), Raw.Scope)
        and then Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1), Raw.Bound)
        and then Source_Padding_Valid (Data (Data'First + Raw.Parent'Position .. Data'First + Raw.Parent'Position + Raw.Parent'Size / System.Storage_Unit - 1), Raw.Parent)
        and then Source_Padding_Valid (Data (Data'First + Raw.Amount'Position .. Data'First + Raw.Amount'Position + Raw.Amount'Size / System.Storage_Unit - 1), Raw.Amount)
        and then Source_Padding_Valid (Data (Data'First + Raw.Observed_Usage'Position .. Data'First + Raw.Observed_Usage'Position + Raw.Observed_Usage'Size / System.Storage_Unit - 1), Raw.Observed_Usage)
        and then Source_Padding_Valid (Data (Data'First + Raw.Planned_Unit'Position .. Data'First + Raw.Planned_Unit'Position + Raw.Planned_Unit'Size / System.Storage_Unit - 1), Raw.Planned_Unit)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Unit'Position .. Data'First + Raw.Actual_Unit'Position + Raw.Actual_Unit'Size / System.Storage_Unit - 1), Raw.Actual_Unit)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cgroup'Position .. Data'First + Raw.Cgroup'Position + Raw.Cgroup'Size / System.Storage_Unit - 1), Raw.Cgroup)
        and then Source_Padding_Valid (Data (Data'First + Raw.Invocation'Position .. Data'First + Raw.Invocation'Position + Raw.Invocation'Size / System.Storage_Unit - 1), Raw.Invocation);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : D.Raw_Observation) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Bound'Position and then Offset - Raw.Bound'Position < Raw.Bound'Size / System.Storage_Unit) or else (Offset >= Raw.Raw_Frame'Position and then Offset - Raw.Raw_Frame'Position < Raw.Raw_Frame'Size / System.Storage_Unit) or else (Offset >= Raw.Raw_Sender'Position and then Offset - Raw.Raw_Sender'Position < Raw.Raw_Sender'Size / System.Storage_Unit) or else (Offset >= Raw.Ticket'Position and then Offset - Raw.Ticket'Position < Raw.Ticket'Size / System.Storage_Unit) or else (Offset >= Raw.Raw_Proc_Status'Position and then Offset - Raw.Raw_Proc_Status'Position < Raw.Raw_Proc_Status'Size / System.Storage_Unit) or else (Offset >= Raw.Raw_Proc_Cgroup'Position and then Offset - Raw.Raw_Proc_Cgroup'Position < Raw.Raw_Proc_Cgroup'Size / System.Storage_Unit) or else (Offset >= Raw.Raw_Proc_Maps'Position and then Offset - Raw.Raw_Proc_Maps'Position < Raw.Raw_Proc_Maps'Size / System.Storage_Unit) or else (Offset >= Raw.Raw_Proc_Cmdline'Position and then Offset - Raw.Raw_Proc_Cmdline'Position < Raw.Raw_Proc_Cmdline'Size / System.Storage_Unit) or else (Offset >= Raw.Raw_Pidfd_Info'Position and then Offset - Raw.Raw_Pidfd_Info'Position < Raw.Raw_Pidfd_Info'Size / System.Storage_Unit) or else (Offset >= Raw.Namespace'Position and then Offset - Raw.Namespace'Position < Raw.Namespace'Size / System.Storage_Unit) or else (Offset >= Raw.Held_Namespace'Position and then Offset - Raw.Held_Namespace'Position < Raw.Held_Namespace'Size / System.Storage_Unit) or else (Offset >= Raw.Helper_Image'Position and then Offset - Raw.Helper_Image'Position < Raw.Helper_Image'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Helper_Image'Position and then Offset - Raw.Expected_Helper_Image'Position < Raw.Expected_Helper_Image'Size / System.Storage_Unit) or else (Offset >= Raw.Executable_Plan'Position and then Offset - Raw.Executable_Plan'Position < Raw.Executable_Plan'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Executable_Plan'Position and then Offset - Raw.Expected_Executable_Plan'Position < Raw.Expected_Executable_Plan'Size / System.Storage_Unit) or else (Offset >= Raw.Original_Requester'Position and then Offset - Raw.Original_Requester'Position < Raw.Original_Requester'Size / System.Storage_Unit) or else (Offset >= Raw.Requester_Credentials'Position and then Offset - Raw.Requester_Credentials'Position < Raw.Requester_Credentials'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Requester_Credentials'Position and then Offset - Raw.Expected_Requester_Credentials'Position < Raw.Expected_Requester_Credentials'Size / System.Storage_Unit) or else (Offset >= Raw.Dispatch'Position and then Offset - Raw.Dispatch'Position < Raw.Dispatch'Size / System.Storage_Unit) or else (Offset >= Raw.Running_Event'Position and then Offset - Raw.Running_Event'Position < Raw.Running_Event'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Running_Event'Position and then Offset - Raw.Expected_Running_Event'Position < Raw.Expected_Running_Event'Size / System.Storage_Unit) or else (Offset >= Raw.Canonical_Use_Event'Position and then Offset - Raw.Canonical_Use_Event'Position < Raw.Canonical_Use_Event'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Canonical_Use_Event'Position and then Offset - Raw.Expected_Canonical_Use_Event'Position < Raw.Expected_Canonical_Use_Event'Size / System.Storage_Unit) or else (Offset >= Raw.Store_Genesis'Position and then Offset - Raw.Store_Genesis'Position < Raw.Store_Genesis'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Store_Genesis'Position and then Offset - Raw.Expected_Store_Genesis'Position < Raw.Expected_Store_Genesis'Size / System.Storage_Unit) or else (Offset >= Raw.Source_Lease'Position and then Offset - Raw.Source_Lease'Position < Raw.Source_Lease'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Source_Lease'Position and then Offset - Raw.Expected_Source_Lease'Position < Raw.Expected_Source_Lease'Size / System.Storage_Unit) or else (Offset >= Raw.Actor_Wait'Position and then Offset - Raw.Actor_Wait'Position < Raw.Actor_Wait'Size / System.Storage_Unit) or else (Offset >= Raw.Helper_Wait'Position and then Offset - Raw.Helper_Wait'Position < Raw.Helper_Wait'Size / System.Storage_Unit) or else (Offset >= Raw.Namespace_Wait'Position and then Offset - Raw.Namespace_Wait'Position < Raw.Namespace_Wait'Size / System.Storage_Unit) or else (Offset >= Raw.Host_Pid'Position and then Offset - Raw.Host_Pid'Position < Raw.Host_Pid'Size / System.Storage_Unit) or else (Offset >= Raw.Namespace_Pid'Position and then Offset - Raw.Namespace_Pid'Position < Raw.Namespace_Pid'Size / System.Storage_Unit) or else (Offset >= Raw.Sender_Uid'Position and then Offset - Raw.Sender_Uid'Position < Raw.Sender_Uid'Size / System.Storage_Unit) or else (Offset >= Raw.Sender_Gid'Position and then Offset - Raw.Sender_Gid'Position < Raw.Sender_Gid'Size / System.Storage_Unit) or else (Offset >= Raw.Real_Uid'Position and then Offset - Raw.Real_Uid'Position < Raw.Real_Uid'Size / System.Storage_Unit) or else (Offset >= Raw.Effective_Uid'Position and then Offset - Raw.Effective_Uid'Position < Raw.Effective_Uid'Size / System.Storage_Unit) or else (Offset >= Raw.Saved_Uid'Position and then Offset - Raw.Saved_Uid'Position < Raw.Saved_Uid'Size / System.Storage_Unit) or else (Offset >= Raw.Real_Gid'Position and then Offset - Raw.Real_Gid'Position < Raw.Real_Gid'Size / System.Storage_Unit) or else (Offset >= Raw.Effective_Gid'Position and then Offset - Raw.Effective_Gid'Position < Raw.Effective_Gid'Size / System.Storage_Unit) or else (Offset >= Raw.Saved_Gid'Position and then Offset - Raw.Saved_Gid'Position < Raw.Saved_Gid'Size / System.Storage_Unit) or else (Offset >= Raw.Capability_Version'Position and then Offset - Raw.Capability_Version'Position < Raw.Capability_Version'Size / System.Storage_Unit) or else (Offset >= Raw.Effective_Low'Position and then Offset - Raw.Effective_Low'Position < Raw.Effective_Low'Size / System.Storage_Unit) or else (Offset >= Raw.Permitted_Low'Position and then Offset - Raw.Permitted_Low'Position < Raw.Permitted_Low'Size / System.Storage_Unit) or else (Offset >= Raw.Inheritable_Low'Position and then Offset - Raw.Inheritable_Low'Position < Raw.Inheritable_Low'Size / System.Storage_Unit) or else (Offset >= Raw.Effective_High'Position and then Offset - Raw.Effective_High'Position < Raw.Effective_High'Size / System.Storage_Unit) or else (Offset >= Raw.Permitted_High'Position and then Offset - Raw.Permitted_High'Position < Raw.Permitted_High'Size / System.Storage_Unit) or else (Offset >= Raw.Inheritable_High'Position and then Offset - Raw.Inheritable_High'Position < Raw.Inheritable_High'Size / System.Storage_Unit) or else (Offset >= Raw.Securebits'Position and then Offset - Raw.Securebits'Position < Raw.Securebits'Size / System.Storage_Unit) or else (Offset >= Raw.No_New_Privs'Position and then Offset - Raw.No_New_Privs'Position < Raw.No_New_Privs'Size / System.Storage_Unit) or else (Offset >= Raw.Requester_Uid'Position and then Offset - Raw.Requester_Uid'Position < Raw.Requester_Uid'Size / System.Storage_Unit) or else (Offset >= Raw.Requester_Gid'Position and then Offset - Raw.Requester_Gid'Position < Raw.Requester_Gid'Size / System.Storage_Unit) or else (Offset >= Raw.Configured_Requester_Uid'Position and then Offset - Raw.Configured_Requester_Uid'Position < Raw.Configured_Requester_Uid'Size / System.Storage_Unit) or else (Offset >= Raw.Workload_Uid'Position and then Offset - Raw.Workload_Uid'Position < Raw.Workload_Uid'Size / System.Storage_Unit) or else (Offset >= Raw.Workload_Gid'Position and then Offset - Raw.Workload_Gid'Position < Raw.Workload_Gid'Size / System.Storage_Unit) or else (Offset >= Raw.Proc_Host_Pid'Position and then Offset - Raw.Proc_Host_Pid'Position < Raw.Proc_Host_Pid'Size / System.Storage_Unit) or else (Offset >= Raw.Proc_Namespace_Pid'Position and then Offset - Raw.Proc_Namespace_Pid'Position < Raw.Proc_Namespace_Pid'Size / System.Storage_Unit) or else (Offset >= Raw.Proc_Real_Uid'Position and then Offset - Raw.Proc_Real_Uid'Position < Raw.Proc_Real_Uid'Size / System.Storage_Unit) or else (Offset >= Raw.Proc_Effective_Uid'Position and then Offset - Raw.Proc_Effective_Uid'Position < Raw.Proc_Effective_Uid'Size / System.Storage_Unit) or else (Offset >= Raw.Proc_Saved_Uid'Position and then Offset - Raw.Proc_Saved_Uid'Position < Raw.Proc_Saved_Uid'Size / System.Storage_Unit) or else (Offset >= Raw.Proc_Real_Gid'Position and then Offset - Raw.Proc_Real_Gid'Position < Raw.Proc_Real_Gid'Size / System.Storage_Unit) or else (Offset >= Raw.Proc_Effective_Gid'Position and then Offset - Raw.Proc_Effective_Gid'Position < Raw.Proc_Effective_Gid'Size / System.Storage_Unit) or else (Offset >= Raw.Proc_Saved_Gid'Position and then Offset - Raw.Proc_Saved_Gid'Position < Raw.Proc_Saved_Gid'Size / System.Storage_Unit) or else (Offset >= Raw.Proc_Effective'Position and then Offset - Raw.Proc_Effective'Position < Raw.Proc_Effective'Size / System.Storage_Unit) or else (Offset >= Raw.Proc_Permitted'Position and then Offset - Raw.Proc_Permitted'Position < Raw.Proc_Permitted'Size / System.Storage_Unit) or else (Offset >= Raw.Proc_Inheritable'Position and then Offset - Raw.Proc_Inheritable'Position < Raw.Proc_Inheritable'Size / System.Storage_Unit) or else (Offset >= Raw.Proc_Bounding'Position and then Offset - Raw.Proc_Bounding'Position < Raw.Proc_Bounding'Size / System.Storage_Unit) or else (Offset >= Raw.Proc_Ambient'Position and then Offset - Raw.Proc_Ambient'Position < Raw.Proc_Ambient'Size / System.Storage_Unit) or else (Offset >= Raw.Proc_No_New_Privs'Position and then Offset - Raw.Proc_No_New_Privs'Position < Raw.Proc_No_New_Privs'Size / System.Storage_Unit) or else (Offset >= Raw.Proc_Fs_Uid'Position and then Offset - Raw.Proc_Fs_Uid'Position < Raw.Proc_Fs_Uid'Size / System.Storage_Unit) or else (Offset >= Raw.Proc_Fs_Gid'Position and then Offset - Raw.Proc_Fs_Gid'Position < Raw.Proc_Fs_Gid'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1), Raw.Bound)
        and then Source_Padding_Valid (Data (Data'First + Raw.Raw_Frame'Position .. Data'First + Raw.Raw_Frame'Position + Raw.Raw_Frame'Size / System.Storage_Unit - 1), Raw.Raw_Frame)
        and then Source_Padding_Valid (Data (Data'First + Raw.Raw_Sender'Position .. Data'First + Raw.Raw_Sender'Position + Raw.Raw_Sender'Size / System.Storage_Unit - 1), Raw.Raw_Sender)
        and then Source_Padding_Valid (Data (Data'First + Raw.Ticket'Position .. Data'First + Raw.Ticket'Position + Raw.Ticket'Size / System.Storage_Unit - 1), Raw.Ticket)
        and then Source_Padding_Valid (Data (Data'First + Raw.Raw_Proc_Status'Position .. Data'First + Raw.Raw_Proc_Status'Position + Raw.Raw_Proc_Status'Size / System.Storage_Unit - 1), Raw.Raw_Proc_Status)
        and then Source_Padding_Valid (Data (Data'First + Raw.Raw_Proc_Cgroup'Position .. Data'First + Raw.Raw_Proc_Cgroup'Position + Raw.Raw_Proc_Cgroup'Size / System.Storage_Unit - 1), Raw.Raw_Proc_Cgroup)
        and then Source_Padding_Valid (Data (Data'First + Raw.Raw_Proc_Maps'Position .. Data'First + Raw.Raw_Proc_Maps'Position + Raw.Raw_Proc_Maps'Size / System.Storage_Unit - 1), Raw.Raw_Proc_Maps)
        and then Source_Padding_Valid (Data (Data'First + Raw.Raw_Proc_Cmdline'Position .. Data'First + Raw.Raw_Proc_Cmdline'Position + Raw.Raw_Proc_Cmdline'Size / System.Storage_Unit - 1), Raw.Raw_Proc_Cmdline)
        and then Source_Padding_Valid (Data (Data'First + Raw.Raw_Pidfd_Info'Position .. Data'First + Raw.Raw_Pidfd_Info'Position + Raw.Raw_Pidfd_Info'Size / System.Storage_Unit - 1), Raw.Raw_Pidfd_Info)
        and then Source_Padding_Valid (Data (Data'First + Raw.Namespace'Position .. Data'First + Raw.Namespace'Position + Raw.Namespace'Size / System.Storage_Unit - 1), Raw.Namespace)
        and then Source_Padding_Valid (Data (Data'First + Raw.Held_Namespace'Position .. Data'First + Raw.Held_Namespace'Position + Raw.Held_Namespace'Size / System.Storage_Unit - 1), Raw.Held_Namespace)
        and then Source_Padding_Valid (Data (Data'First + Raw.Helper_Image'Position .. Data'First + Raw.Helper_Image'Position + Raw.Helper_Image'Size / System.Storage_Unit - 1), Raw.Helper_Image)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Helper_Image'Position .. Data'First + Raw.Expected_Helper_Image'Position + Raw.Expected_Helper_Image'Size / System.Storage_Unit - 1), Raw.Expected_Helper_Image)
        and then Source_Padding_Valid (Data (Data'First + Raw.Executable_Plan'Position .. Data'First + Raw.Executable_Plan'Position + Raw.Executable_Plan'Size / System.Storage_Unit - 1), Raw.Executable_Plan)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Executable_Plan'Position .. Data'First + Raw.Expected_Executable_Plan'Position + Raw.Expected_Executable_Plan'Size / System.Storage_Unit - 1), Raw.Expected_Executable_Plan)
        and then Source_Padding_Valid (Data (Data'First + Raw.Original_Requester'Position .. Data'First + Raw.Original_Requester'Position + Raw.Original_Requester'Size / System.Storage_Unit - 1), Raw.Original_Requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester_Credentials'Position .. Data'First + Raw.Requester_Credentials'Position + Raw.Requester_Credentials'Size / System.Storage_Unit - 1), Raw.Requester_Credentials)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Requester_Credentials'Position .. Data'First + Raw.Expected_Requester_Credentials'Position + Raw.Expected_Requester_Credentials'Size / System.Storage_Unit - 1), Raw.Expected_Requester_Credentials)
        and then Source_Padding_Valid (Data (Data'First + Raw.Dispatch'Position .. Data'First + Raw.Dispatch'Position + Raw.Dispatch'Size / System.Storage_Unit - 1), Raw.Dispatch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Running_Event'Position .. Data'First + Raw.Running_Event'Position + Raw.Running_Event'Size / System.Storage_Unit - 1), Raw.Running_Event)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Running_Event'Position .. Data'First + Raw.Expected_Running_Event'Position + Raw.Expected_Running_Event'Size / System.Storage_Unit - 1), Raw.Expected_Running_Event)
        and then Source_Padding_Valid (Data (Data'First + Raw.Canonical_Use_Event'Position .. Data'First + Raw.Canonical_Use_Event'Position + Raw.Canonical_Use_Event'Size / System.Storage_Unit - 1), Raw.Canonical_Use_Event)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Canonical_Use_Event'Position .. Data'First + Raw.Expected_Canonical_Use_Event'Position + Raw.Expected_Canonical_Use_Event'Size / System.Storage_Unit - 1), Raw.Expected_Canonical_Use_Event)
        and then Source_Padding_Valid (Data (Data'First + Raw.Store_Genesis'Position .. Data'First + Raw.Store_Genesis'Position + Raw.Store_Genesis'Size / System.Storage_Unit - 1), Raw.Store_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Store_Genesis'Position .. Data'First + Raw.Expected_Store_Genesis'Position + Raw.Expected_Store_Genesis'Size / System.Storage_Unit - 1), Raw.Expected_Store_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Source_Lease'Position .. Data'First + Raw.Source_Lease'Position + Raw.Source_Lease'Size / System.Storage_Unit - 1), Raw.Source_Lease)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Source_Lease'Position .. Data'First + Raw.Expected_Source_Lease'Position + Raw.Expected_Source_Lease'Size / System.Storage_Unit - 1), Raw.Expected_Source_Lease)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actor_Wait'Position .. Data'First + Raw.Actor_Wait'Position + Raw.Actor_Wait'Size / System.Storage_Unit - 1), Raw.Actor_Wait)
        and then Source_Padding_Valid (Data (Data'First + Raw.Helper_Wait'Position .. Data'First + Raw.Helper_Wait'Position + Raw.Helper_Wait'Size / System.Storage_Unit - 1), Raw.Helper_Wait)
        and then Source_Padding_Valid (Data (Data'First + Raw.Namespace_Wait'Position .. Data'First + Raw.Namespace_Wait'Position + Raw.Namespace_Wait'Size / System.Storage_Unit - 1), Raw.Namespace_Wait)
        and then Source_Padding_Valid (Data (Data'First + Raw.Host_Pid'Position .. Data'First + Raw.Host_Pid'Position + Raw.Host_Pid'Size / System.Storage_Unit - 1), Raw.Host_Pid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Namespace_Pid'Position .. Data'First + Raw.Namespace_Pid'Position + Raw.Namespace_Pid'Size / System.Storage_Unit - 1), Raw.Namespace_Pid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Sender_Uid'Position .. Data'First + Raw.Sender_Uid'Position + Raw.Sender_Uid'Size / System.Storage_Unit - 1), Raw.Sender_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Sender_Gid'Position .. Data'First + Raw.Sender_Gid'Position + Raw.Sender_Gid'Size / System.Storage_Unit - 1), Raw.Sender_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Real_Uid'Position .. Data'First + Raw.Real_Uid'Position + Raw.Real_Uid'Size / System.Storage_Unit - 1), Raw.Real_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Effective_Uid'Position .. Data'First + Raw.Effective_Uid'Position + Raw.Effective_Uid'Size / System.Storage_Unit - 1), Raw.Effective_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Saved_Uid'Position .. Data'First + Raw.Saved_Uid'Position + Raw.Saved_Uid'Size / System.Storage_Unit - 1), Raw.Saved_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Real_Gid'Position .. Data'First + Raw.Real_Gid'Position + Raw.Real_Gid'Size / System.Storage_Unit - 1), Raw.Real_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Effective_Gid'Position .. Data'First + Raw.Effective_Gid'Position + Raw.Effective_Gid'Size / System.Storage_Unit - 1), Raw.Effective_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Saved_Gid'Position .. Data'First + Raw.Saved_Gid'Position + Raw.Saved_Gid'Size / System.Storage_Unit - 1), Raw.Saved_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Capability_Version'Position .. Data'First + Raw.Capability_Version'Position + Raw.Capability_Version'Size / System.Storage_Unit - 1), Raw.Capability_Version)
        and then Source_Padding_Valid (Data (Data'First + Raw.Effective_Low'Position .. Data'First + Raw.Effective_Low'Position + Raw.Effective_Low'Size / System.Storage_Unit - 1), Raw.Effective_Low)
        and then Source_Padding_Valid (Data (Data'First + Raw.Permitted_Low'Position .. Data'First + Raw.Permitted_Low'Position + Raw.Permitted_Low'Size / System.Storage_Unit - 1), Raw.Permitted_Low)
        and then Source_Padding_Valid (Data (Data'First + Raw.Inheritable_Low'Position .. Data'First + Raw.Inheritable_Low'Position + Raw.Inheritable_Low'Size / System.Storage_Unit - 1), Raw.Inheritable_Low)
        and then Source_Padding_Valid (Data (Data'First + Raw.Effective_High'Position .. Data'First + Raw.Effective_High'Position + Raw.Effective_High'Size / System.Storage_Unit - 1), Raw.Effective_High)
        and then Source_Padding_Valid (Data (Data'First + Raw.Permitted_High'Position .. Data'First + Raw.Permitted_High'Position + Raw.Permitted_High'Size / System.Storage_Unit - 1), Raw.Permitted_High)
        and then Source_Padding_Valid (Data (Data'First + Raw.Inheritable_High'Position .. Data'First + Raw.Inheritable_High'Position + Raw.Inheritable_High'Size / System.Storage_Unit - 1), Raw.Inheritable_High)
        and then Source_Padding_Valid (Data (Data'First + Raw.Securebits'Position .. Data'First + Raw.Securebits'Position + Raw.Securebits'Size / System.Storage_Unit - 1), Raw.Securebits)
        and then Source_Padding_Valid (Data (Data'First + Raw.No_New_Privs'Position .. Data'First + Raw.No_New_Privs'Position + Raw.No_New_Privs'Size / System.Storage_Unit - 1), Raw.No_New_Privs)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester_Uid'Position .. Data'First + Raw.Requester_Uid'Position + Raw.Requester_Uid'Size / System.Storage_Unit - 1), Raw.Requester_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester_Gid'Position .. Data'First + Raw.Requester_Gid'Position + Raw.Requester_Gid'Size / System.Storage_Unit - 1), Raw.Requester_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Configured_Requester_Uid'Position .. Data'First + Raw.Configured_Requester_Uid'Position + Raw.Configured_Requester_Uid'Size / System.Storage_Unit - 1), Raw.Configured_Requester_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Workload_Uid'Position .. Data'First + Raw.Workload_Uid'Position + Raw.Workload_Uid'Size / System.Storage_Unit - 1), Raw.Workload_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Workload_Gid'Position .. Data'First + Raw.Workload_Gid'Position + Raw.Workload_Gid'Size / System.Storage_Unit - 1), Raw.Workload_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Host_Pid'Position .. Data'First + Raw.Proc_Host_Pid'Position + Raw.Proc_Host_Pid'Size / System.Storage_Unit - 1), Raw.Proc_Host_Pid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Namespace_Pid'Position .. Data'First + Raw.Proc_Namespace_Pid'Position + Raw.Proc_Namespace_Pid'Size / System.Storage_Unit - 1), Raw.Proc_Namespace_Pid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Real_Uid'Position .. Data'First + Raw.Proc_Real_Uid'Position + Raw.Proc_Real_Uid'Size / System.Storage_Unit - 1), Raw.Proc_Real_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Effective_Uid'Position .. Data'First + Raw.Proc_Effective_Uid'Position + Raw.Proc_Effective_Uid'Size / System.Storage_Unit - 1), Raw.Proc_Effective_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Saved_Uid'Position .. Data'First + Raw.Proc_Saved_Uid'Position + Raw.Proc_Saved_Uid'Size / System.Storage_Unit - 1), Raw.Proc_Saved_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Real_Gid'Position .. Data'First + Raw.Proc_Real_Gid'Position + Raw.Proc_Real_Gid'Size / System.Storage_Unit - 1), Raw.Proc_Real_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Effective_Gid'Position .. Data'First + Raw.Proc_Effective_Gid'Position + Raw.Proc_Effective_Gid'Size / System.Storage_Unit - 1), Raw.Proc_Effective_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Saved_Gid'Position .. Data'First + Raw.Proc_Saved_Gid'Position + Raw.Proc_Saved_Gid'Size / System.Storage_Unit - 1), Raw.Proc_Saved_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Effective'Position .. Data'First + Raw.Proc_Effective'Position + Raw.Proc_Effective'Size / System.Storage_Unit - 1), Raw.Proc_Effective)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Permitted'Position .. Data'First + Raw.Proc_Permitted'Position + Raw.Proc_Permitted'Size / System.Storage_Unit - 1), Raw.Proc_Permitted)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Inheritable'Position .. Data'First + Raw.Proc_Inheritable'Position + Raw.Proc_Inheritable'Size / System.Storage_Unit - 1), Raw.Proc_Inheritable)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Bounding'Position .. Data'First + Raw.Proc_Bounding'Position + Raw.Proc_Bounding'Size / System.Storage_Unit - 1), Raw.Proc_Bounding)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Ambient'Position .. Data'First + Raw.Proc_Ambient'Position + Raw.Proc_Ambient'Size / System.Storage_Unit - 1), Raw.Proc_Ambient)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_No_New_Privs'Position .. Data'First + Raw.Proc_No_New_Privs'Position + Raw.Proc_No_New_Privs'Size / System.Storage_Unit - 1), Raw.Proc_No_New_Privs)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Fs_Uid'Position .. Data'First + Raw.Proc_Fs_Uid'Position + Raw.Proc_Fs_Uid'Size / System.Storage_Unit - 1), Raw.Proc_Fs_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Fs_Gid'Position .. Data'First + Raw.Proc_Fs_Gid'Position + Raw.Proc_Fs_Gid'Size / System.Storage_Unit - 1), Raw.Proc_Fs_Gid);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : X.Raw_Crosswalk) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Resource_Current'Position and then Offset - Raw.Resource_Current'Position < Raw.Resource_Current'Size / System.Storage_Unit) or else (Offset >= Raw.Operation_Policy'Position and then Offset - Raw.Operation_Policy'Position < Raw.Operation_Policy'Size / System.Storage_Unit) or else (Offset >= Raw.Operation_Root_Set'Position and then Offset - Raw.Operation_Root_Set'Position < Raw.Operation_Root_Set'Size / System.Storage_Unit) or else (Offset >= Raw.Owner_Genesis'Position and then Offset - Raw.Owner_Genesis'Position < Raw.Owner_Genesis'Size / System.Storage_Unit) or else (Offset >= Raw.Installation'Position and then Offset - Raw.Installation'Position < Raw.Installation'Size / System.Storage_Unit) or else (Offset >= Raw.Gate_Config'Position and then Offset - Raw.Gate_Config'Position < Raw.Gate_Config'Size / System.Storage_Unit) or else (Offset >= Raw.Managed_Observation'Position and then Offset - Raw.Managed_Observation'Position < Raw.Managed_Observation'Size / System.Storage_Unit) or else (Offset >= Raw.Original_Grant'Position and then Offset - Raw.Original_Grant'Position < Raw.Original_Grant'Size / System.Storage_Unit) or else (Offset >= Raw.Complete_Crosswalk'Position and then Offset - Raw.Complete_Crosswalk'Position < Raw.Complete_Crosswalk'Size / System.Storage_Unit) or else (Offset >= Raw.Current_Source'Position and then Offset - Raw.Current_Source'Position < Raw.Current_Source'Size / System.Storage_Unit) or else (Offset >= Raw.Original_Request'Position and then Offset - Raw.Original_Request'Position < Raw.Original_Request'Size / System.Storage_Unit) or else (Offset >= Raw.Original_Requester'Position and then Offset - Raw.Original_Requester'Position < Raw.Original_Requester'Size / System.Storage_Unit) or else (Offset >= Raw.Original_Transaction'Position and then Offset - Raw.Original_Transaction'Position < Raw.Original_Transaction'Size / System.Storage_Unit) or else (Offset >= Raw.Preparer'Position and then Offset - Raw.Preparer'Position < Raw.Preparer'Size / System.Storage_Unit) or else (Offset >= Raw.Selected_Plan'Position and then Offset - Raw.Selected_Plan'Position < Raw.Selected_Plan'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Resource_Current'Position .. Data'First + Raw.Resource_Current'Position + Raw.Resource_Current'Size / System.Storage_Unit - 1), Raw.Resource_Current)
        and then Source_Padding_Valid (Data (Data'First + Raw.Operation_Policy'Position .. Data'First + Raw.Operation_Policy'Position + Raw.Operation_Policy'Size / System.Storage_Unit - 1), Raw.Operation_Policy)
        and then Source_Padding_Valid (Data (Data'First + Raw.Operation_Root_Set'Position .. Data'First + Raw.Operation_Root_Set'Position + Raw.Operation_Root_Set'Size / System.Storage_Unit - 1), Raw.Operation_Root_Set)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner_Genesis'Position .. Data'First + Raw.Owner_Genesis'Position + Raw.Owner_Genesis'Size / System.Storage_Unit - 1), Raw.Owner_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Installation'Position .. Data'First + Raw.Installation'Position + Raw.Installation'Size / System.Storage_Unit - 1), Raw.Installation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Gate_Config'Position .. Data'First + Raw.Gate_Config'Position + Raw.Gate_Config'Size / System.Storage_Unit - 1), Raw.Gate_Config)
        and then Source_Padding_Valid (Data (Data'First + Raw.Managed_Observation'Position .. Data'First + Raw.Managed_Observation'Position + Raw.Managed_Observation'Size / System.Storage_Unit - 1), Raw.Managed_Observation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Original_Grant'Position .. Data'First + Raw.Original_Grant'Position + Raw.Original_Grant'Size / System.Storage_Unit - 1), Raw.Original_Grant)
        and then Source_Padding_Valid (Data (Data'First + Raw.Complete_Crosswalk'Position .. Data'First + Raw.Complete_Crosswalk'Position + Raw.Complete_Crosswalk'Size / System.Storage_Unit - 1), Raw.Complete_Crosswalk)
        and then Source_Padding_Valid (Data (Data'First + Raw.Current_Source'Position .. Data'First + Raw.Current_Source'Position + Raw.Current_Source'Size / System.Storage_Unit - 1), Raw.Current_Source)
        and then Source_Padding_Valid (Data (Data'First + Raw.Original_Request'Position .. Data'First + Raw.Original_Request'Position + Raw.Original_Request'Size / System.Storage_Unit - 1), Raw.Original_Request)
        and then Source_Padding_Valid (Data (Data'First + Raw.Original_Requester'Position .. Data'First + Raw.Original_Requester'Position + Raw.Original_Requester'Size / System.Storage_Unit - 1), Raw.Original_Requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.Original_Transaction'Position .. Data'First + Raw.Original_Transaction'Position + Raw.Original_Transaction'Size / System.Storage_Unit - 1), Raw.Original_Transaction)
        and then Source_Padding_Valid (Data (Data'First + Raw.Preparer'Position .. Data'First + Raw.Preparer'Position + Raw.Preparer'Size / System.Storage_Unit - 1), Raw.Preparer)
        and then Source_Padding_Valid (Data (Data'First + Raw.Selected_Plan'Position .. Data'First + Raw.Selected_Plan'Position + Raw.Selected_Plan'Size / System.Storage_Unit - 1), Raw.Selected_Plan);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : C.Raw_Digest) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Present'Position and then Offset - Raw.Present'Position < Raw.Present'Size / System.Storage_Unit) or else (Offset >= Raw.Value'Position and then Offset - Raw.Value'Position < Raw.Value'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Value'Position .. Data'First + Raw.Value'Position + Raw.Value'Size / System.Storage_Unit - 1), Raw.Value);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : C.Raw_Hash) return Boolean is
   begin
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : Y.Raw_Input) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Mode'Position and then Offset - Raw.Mode'Position < Raw.Mode'Size / System.Storage_Unit) or else (Offset >= Raw.Controller'Position and then Offset - Raw.Controller'Position < Raw.Controller'Size / System.Storage_Unit) or else (Offset >= Raw.Child_Task'Position and then Offset - Raw.Child_Task'Position < Raw.Child_Task'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Controller'Position .. Data'First + Raw.Controller'Position + Raw.Controller'Size / System.Storage_Unit - 1), Raw.Controller)
        and then Source_Padding_Valid (Data (Data'First + Raw.Child_Task'Position .. Data'First + Raw.Child_Task'Position + Raw.Child_Task'Size / System.Storage_Unit - 1), Raw.Child_Task);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : Y.Raw_Controller) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Bound'Position and then Offset - Raw.Bound'Position < Raw.Bound'Size / System.Storage_Unit) or else (Offset >= Raw.Process'Position and then Offset - Raw.Process'Position < Raw.Process'Size / System.Storage_Unit) or else (Offset >= Raw.Requester_Uid'Position and then Offset - Raw.Requester_Uid'Position < Raw.Requester_Uid'Size / System.Storage_Unit) or else (Offset >= Raw.Requester_Gid'Position and then Offset - Raw.Requester_Gid'Position < Raw.Requester_Gid'Size / System.Storage_Unit) or else (Offset >= Raw.raw_manager'Position and then Offset - Raw.raw_manager'Position < Raw.raw_manager'Size / System.Storage_Unit) or else (Offset >= Raw.raw_channel'Position and then Offset - Raw.raw_channel'Position < Raw.raw_channel'Size / System.Storage_Unit) or else (Offset >= Raw.owner_endpoint'Position and then Offset - Raw.owner_endpoint'Position < Raw.owner_endpoint'Size / System.Storage_Unit) or else (Offset >= Raw.expected_owner_endpoint'Position and then Offset - Raw.expected_owner_endpoint'Position < Raw.expected_owner_endpoint'Size / System.Storage_Unit) or else (Offset >= Raw.source_lease'Position and then Offset - Raw.source_lease'Position < Raw.source_lease'Size / System.Storage_Unit) or else (Offset >= Raw.expected_source_lease'Position and then Offset - Raw.expected_source_lease'Position < Raw.expected_source_lease'Size / System.Storage_Unit) or else (Offset >= Raw.worker_image'Position and then Offset - Raw.worker_image'Position < Raw.worker_image'Size / System.Storage_Unit) or else (Offset >= Raw.expected_worker_image'Position and then Offset - Raw.expected_worker_image'Position < Raw.expected_worker_image'Size / System.Storage_Unit) or else (Offset >= Raw.handler_plan'Position and then Offset - Raw.handler_plan'Position < Raw.handler_plan'Size / System.Storage_Unit) or else (Offset >= Raw.expected_handler_plan'Position and then Offset - Raw.expected_handler_plan'Position < Raw.expected_handler_plan'Size / System.Storage_Unit) or else (Offset >= Raw.raw_request'Position and then Offset - Raw.raw_request'Position < Raw.raw_request'Size / System.Storage_Unit) or else (Offset >= Raw.requester'Position and then Offset - Raw.requester'Position < Raw.requester'Size / System.Storage_Unit) or else (Offset >= Raw.dispatch'Position and then Offset - Raw.dispatch'Position < Raw.dispatch'Size / System.Storage_Unit) or else (Offset >= Raw.running_event'Position and then Offset - Raw.running_event'Position < Raw.running_event'Size / System.Storage_Unit) or else (Offset >= Raw.expected_running_event'Position and then Offset - Raw.expected_running_event'Position < Raw.expected_running_event'Size / System.Storage_Unit) or else (Offset >= Raw.store_genesis'Position and then Offset - Raw.store_genesis'Position < Raw.store_genesis'Size / System.Storage_Unit) or else (Offset >= Raw.expected_store_genesis'Position and then Offset - Raw.expected_store_genesis'Position < Raw.expected_store_genesis'Size / System.Storage_Unit) or else (Offset >= Raw.current_source'Position and then Offset - Raw.current_source'Position < Raw.current_source'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1), Raw.Bound)
        and then Source_Padding_Valid (Data (Data'First + Raw.Process'Position .. Data'First + Raw.Process'Position + Raw.Process'Size / System.Storage_Unit - 1), Raw.Process)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester_Uid'Position .. Data'First + Raw.Requester_Uid'Position + Raw.Requester_Uid'Size / System.Storage_Unit - 1), Raw.Requester_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester_Gid'Position .. Data'First + Raw.Requester_Gid'Position + Raw.Requester_Gid'Size / System.Storage_Unit - 1), Raw.Requester_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_manager'Position .. Data'First + Raw.raw_manager'Position + Raw.raw_manager'Size / System.Storage_Unit - 1), Raw.raw_manager)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_channel'Position .. Data'First + Raw.raw_channel'Position + Raw.raw_channel'Size / System.Storage_Unit - 1), Raw.raw_channel)
        and then Source_Padding_Valid (Data (Data'First + Raw.owner_endpoint'Position .. Data'First + Raw.owner_endpoint'Position + Raw.owner_endpoint'Size / System.Storage_Unit - 1), Raw.owner_endpoint)
        and then Source_Padding_Valid (Data (Data'First + Raw.expected_owner_endpoint'Position .. Data'First + Raw.expected_owner_endpoint'Position + Raw.expected_owner_endpoint'Size / System.Storage_Unit - 1), Raw.expected_owner_endpoint)
        and then Source_Padding_Valid (Data (Data'First + Raw.source_lease'Position .. Data'First + Raw.source_lease'Position + Raw.source_lease'Size / System.Storage_Unit - 1), Raw.source_lease)
        and then Source_Padding_Valid (Data (Data'First + Raw.expected_source_lease'Position .. Data'First + Raw.expected_source_lease'Position + Raw.expected_source_lease'Size / System.Storage_Unit - 1), Raw.expected_source_lease)
        and then Source_Padding_Valid (Data (Data'First + Raw.worker_image'Position .. Data'First + Raw.worker_image'Position + Raw.worker_image'Size / System.Storage_Unit - 1), Raw.worker_image)
        and then Source_Padding_Valid (Data (Data'First + Raw.expected_worker_image'Position .. Data'First + Raw.expected_worker_image'Position + Raw.expected_worker_image'Size / System.Storage_Unit - 1), Raw.expected_worker_image)
        and then Source_Padding_Valid (Data (Data'First + Raw.handler_plan'Position .. Data'First + Raw.handler_plan'Position + Raw.handler_plan'Size / System.Storage_Unit - 1), Raw.handler_plan)
        and then Source_Padding_Valid (Data (Data'First + Raw.expected_handler_plan'Position .. Data'First + Raw.expected_handler_plan'Position + Raw.expected_handler_plan'Size / System.Storage_Unit - 1), Raw.expected_handler_plan)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_request'Position .. Data'First + Raw.raw_request'Position + Raw.raw_request'Size / System.Storage_Unit - 1), Raw.raw_request)
        and then Source_Padding_Valid (Data (Data'First + Raw.requester'Position .. Data'First + Raw.requester'Position + Raw.requester'Size / System.Storage_Unit - 1), Raw.requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.dispatch'Position .. Data'First + Raw.dispatch'Position + Raw.dispatch'Size / System.Storage_Unit - 1), Raw.dispatch)
        and then Source_Padding_Valid (Data (Data'First + Raw.running_event'Position .. Data'First + Raw.running_event'Position + Raw.running_event'Size / System.Storage_Unit - 1), Raw.running_event)
        and then Source_Padding_Valid (Data (Data'First + Raw.expected_running_event'Position .. Data'First + Raw.expected_running_event'Position + Raw.expected_running_event'Size / System.Storage_Unit - 1), Raw.expected_running_event)
        and then Source_Padding_Valid (Data (Data'First + Raw.store_genesis'Position .. Data'First + Raw.store_genesis'Position + Raw.store_genesis'Size / System.Storage_Unit - 1), Raw.store_genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.expected_store_genesis'Position .. Data'First + Raw.expected_store_genesis'Position + Raw.expected_store_genesis'Size / System.Storage_Unit - 1), Raw.expected_store_genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.current_source'Position .. Data'First + Raw.current_source'Position + Raw.current_source'Size / System.Storage_Unit - 1), Raw.current_source);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : Y.Raw_Process) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.raw_status'Position and then Offset - Raw.raw_status'Position < Raw.raw_status'Size / System.Storage_Unit) or else (Offset >= Raw.raw_stat'Position and then Offset - Raw.raw_stat'Position < Raw.raw_stat'Size / System.Storage_Unit) or else (Offset >= Raw.raw_cgroup'Position and then Offset - Raw.raw_cgroup'Position < Raw.raw_cgroup'Size / System.Storage_Unit) or else (Offset >= Raw.raw_maps'Position and then Offset - Raw.raw_maps'Position < Raw.raw_maps'Size / System.Storage_Unit) or else (Offset >= Raw.raw_cmdline'Position and then Offset - Raw.raw_cmdline'Position < Raw.raw_cmdline'Size / System.Storage_Unit) or else (Offset >= Raw.raw_pidfd_info'Position and then Offset - Raw.raw_pidfd_info'Position < Raw.raw_pidfd_info'Size / System.Storage_Unit) or else (Offset >= Raw.namespace'Position and then Offset - Raw.namespace'Position < Raw.namespace'Size / System.Storage_Unit) or else (Offset >= Raw.cgroup'Position and then Offset - Raw.cgroup'Position < Raw.cgroup'Size / System.Storage_Unit) or else (Offset >= Raw.actual_unit'Position and then Offset - Raw.actual_unit'Position < Raw.actual_unit'Size / System.Storage_Unit) or else (Offset >= Raw.invocation'Position and then Offset - Raw.invocation'Position < Raw.invocation'Size / System.Storage_Unit) or else (Offset >= Raw.source_lease'Position and then Offset - Raw.source_lease'Position < Raw.source_lease'Size / System.Storage_Unit) or else (Offset >= Raw.pidfd_wait'Position and then Offset - Raw.pidfd_wait'Position < Raw.pidfd_wait'Size / System.Storage_Unit) or else (Offset >= Raw.host_pid'Position and then Offset - Raw.host_pid'Position < Raw.host_pid'Size / System.Storage_Unit) or else (Offset >= Raw.start_tick'Position and then Offset - Raw.start_tick'Position < Raw.start_tick'Size / System.Storage_Unit) or else (Offset >= Raw.parent_pid'Position and then Offset - Raw.parent_pid'Position < Raw.parent_pid'Size / System.Storage_Unit) or else (Offset >= Raw.parent_start_tick'Position and then Offset - Raw.parent_start_tick'Position < Raw.parent_start_tick'Size / System.Storage_Unit) or else (Offset >= Raw.real_uid'Position and then Offset - Raw.real_uid'Position < Raw.real_uid'Size / System.Storage_Unit) or else (Offset >= Raw.effective_uid'Position and then Offset - Raw.effective_uid'Position < Raw.effective_uid'Size / System.Storage_Unit) or else (Offset >= Raw.saved_uid'Position and then Offset - Raw.saved_uid'Position < Raw.saved_uid'Size / System.Storage_Unit) or else (Offset >= Raw.real_gid'Position and then Offset - Raw.real_gid'Position < Raw.real_gid'Size / System.Storage_Unit) or else (Offset >= Raw.effective_gid'Position and then Offset - Raw.effective_gid'Position < Raw.effective_gid'Size / System.Storage_Unit) or else (Offset >= Raw.saved_gid'Position and then Offset - Raw.saved_gid'Position < Raw.saved_gid'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.raw_status'Position .. Data'First + Raw.raw_status'Position + Raw.raw_status'Size / System.Storage_Unit - 1), Raw.raw_status)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_stat'Position .. Data'First + Raw.raw_stat'Position + Raw.raw_stat'Size / System.Storage_Unit - 1), Raw.raw_stat)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_cgroup'Position .. Data'First + Raw.raw_cgroup'Position + Raw.raw_cgroup'Size / System.Storage_Unit - 1), Raw.raw_cgroup)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_maps'Position .. Data'First + Raw.raw_maps'Position + Raw.raw_maps'Size / System.Storage_Unit - 1), Raw.raw_maps)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_cmdline'Position .. Data'First + Raw.raw_cmdline'Position + Raw.raw_cmdline'Size / System.Storage_Unit - 1), Raw.raw_cmdline)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_pidfd_info'Position .. Data'First + Raw.raw_pidfd_info'Position + Raw.raw_pidfd_info'Size / System.Storage_Unit - 1), Raw.raw_pidfd_info)
        and then Source_Padding_Valid (Data (Data'First + Raw.namespace'Position .. Data'First + Raw.namespace'Position + Raw.namespace'Size / System.Storage_Unit - 1), Raw.namespace)
        and then Source_Padding_Valid (Data (Data'First + Raw.cgroup'Position .. Data'First + Raw.cgroup'Position + Raw.cgroup'Size / System.Storage_Unit - 1), Raw.cgroup)
        and then Source_Padding_Valid (Data (Data'First + Raw.actual_unit'Position .. Data'First + Raw.actual_unit'Position + Raw.actual_unit'Size / System.Storage_Unit - 1), Raw.actual_unit)
        and then Source_Padding_Valid (Data (Data'First + Raw.invocation'Position .. Data'First + Raw.invocation'Position + Raw.invocation'Size / System.Storage_Unit - 1), Raw.invocation)
        and then Source_Padding_Valid (Data (Data'First + Raw.source_lease'Position .. Data'First + Raw.source_lease'Position + Raw.source_lease'Size / System.Storage_Unit - 1), Raw.source_lease)
        and then Source_Padding_Valid (Data (Data'First + Raw.pidfd_wait'Position .. Data'First + Raw.pidfd_wait'Position + Raw.pidfd_wait'Size / System.Storage_Unit - 1), Raw.pidfd_wait)
        and then Source_Padding_Valid (Data (Data'First + Raw.host_pid'Position .. Data'First + Raw.host_pid'Position + Raw.host_pid'Size / System.Storage_Unit - 1), Raw.host_pid)
        and then Source_Padding_Valid (Data (Data'First + Raw.start_tick'Position .. Data'First + Raw.start_tick'Position + Raw.start_tick'Size / System.Storage_Unit - 1), Raw.start_tick)
        and then Source_Padding_Valid (Data (Data'First + Raw.parent_pid'Position .. Data'First + Raw.parent_pid'Position + Raw.parent_pid'Size / System.Storage_Unit - 1), Raw.parent_pid)
        and then Source_Padding_Valid (Data (Data'First + Raw.parent_start_tick'Position .. Data'First + Raw.parent_start_tick'Position + Raw.parent_start_tick'Size / System.Storage_Unit - 1), Raw.parent_start_tick)
        and then Source_Padding_Valid (Data (Data'First + Raw.real_uid'Position .. Data'First + Raw.real_uid'Position + Raw.real_uid'Size / System.Storage_Unit - 1), Raw.real_uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.effective_uid'Position .. Data'First + Raw.effective_uid'Position + Raw.effective_uid'Size / System.Storage_Unit - 1), Raw.effective_uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.saved_uid'Position .. Data'First + Raw.saved_uid'Position + Raw.saved_uid'Size / System.Storage_Unit - 1), Raw.saved_uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.real_gid'Position .. Data'First + Raw.real_gid'Position + Raw.real_gid'Size / System.Storage_Unit - 1), Raw.real_gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.effective_gid'Position .. Data'First + Raw.effective_gid'Position + Raw.effective_gid'Size / System.Storage_Unit - 1), Raw.effective_gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.saved_gid'Position .. Data'First + Raw.saved_gid'Position + Raw.saved_gid'Size / System.Storage_Unit - 1), Raw.saved_gid);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : Y.Raw_Task) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Action'Position and then Offset - Raw.Action'Position < Raw.Action'Size / System.Storage_Unit) or else (Offset >= Raw.Root'Position and then Offset - Raw.Root'Position < Raw.Root'Size / System.Storage_Unit) or else (Offset >= Raw.Child'Position and then Offset - Raw.Child'Position < Raw.Child'Size / System.Storage_Unit) or else (Offset >= Raw.task_id'Position and then Offset - Raw.task_id'Position < Raw.task_id'Size / System.Storage_Unit) or else (Offset >= Raw.root_world'Position and then Offset - Raw.root_world'Position < Raw.root_world'Size / System.Storage_Unit) or else (Offset >= Raw.child_world'Position and then Offset - Raw.child_world'Position < Raw.child_world'Size / System.Storage_Unit) or else (Offset >= Raw.root_instance'Position and then Offset - Raw.root_instance'Position < Raw.root_instance'Size / System.Storage_Unit) or else (Offset >= Raw.child_instance'Position and then Offset - Raw.child_instance'Position < Raw.child_instance'Size / System.Storage_Unit) or else (Offset >= Raw.world_store'Position and then Offset - Raw.world_store'Position < Raw.world_store'Size / System.Storage_Unit) or else (Offset >= Raw.full_world_ancestry'Position and then Offset - Raw.full_world_ancestry'Position < Raw.full_world_ancestry'Size / System.Storage_Unit) or else (Offset >= Raw.original_workload'Position and then Offset - Raw.original_workload'Position < Raw.original_workload'Size / System.Storage_Unit) or else (Offset >= Raw.sandbox'Position and then Offset - Raw.sandbox'Position < Raw.sandbox'Size / System.Storage_Unit) or else (Offset >= Raw.adapter'Position and then Offset - Raw.adapter'Position < Raw.adapter'Size / System.Storage_Unit) or else (Offset >= Raw.context'Position and then Offset - Raw.context'Position < Raw.context'Size / System.Storage_Unit) or else (Offset >= Raw.mission'Position and then Offset - Raw.mission'Position < Raw.mission'Size / System.Storage_Unit) or else (Offset >= Raw.stdin'Position and then Offset - Raw.stdin'Position < Raw.stdin'Size / System.Storage_Unit) or else (Offset >= Raw.credential_source'Position and then Offset - Raw.credential_source'Position < Raw.credential_source'Size / System.Storage_Unit) or else (Offset >= Raw.executable_source'Position and then Offset - Raw.executable_source'Position < Raw.executable_source'Size / System.Storage_Unit) or else (Offset >= Raw.configuration'Position and then Offset - Raw.configuration'Position < Raw.configuration'Size / System.Storage_Unit) or else (Offset >= Raw.owner_plan'Position and then Offset - Raw.owner_plan'Position < Raw.owner_plan'Size / System.Storage_Unit) or else (Offset >= Raw.native_cost_input'Position and then Offset - Raw.native_cost_input'Position < Raw.native_cost_input'Size / System.Storage_Unit) or else (Offset >= Raw.raw_request'Position and then Offset - Raw.raw_request'Position < Raw.raw_request'Size / System.Storage_Unit) or else (Offset >= Raw.requester'Position and then Offset - Raw.requester'Position < Raw.requester'Size / System.Storage_Unit) or else (Offset >= Raw.cause'Position and then Offset - Raw.cause'Position < Raw.cause'Size / System.Storage_Unit) or else (Offset >= Raw.root_dispatch'Position and then Offset - Raw.root_dispatch'Position < Raw.root_dispatch'Size / System.Storage_Unit) or else (Offset >= Raw.root_running_event'Position and then Offset - Raw.root_running_event'Position < Raw.root_running_event'Size / System.Storage_Unit) or else (Offset >= Raw.task_journal'Position and then Offset - Raw.task_journal'Position < Raw.task_journal'Size / System.Storage_Unit) or else (Offset >= Raw.task_intent'Position and then Offset - Raw.task_intent'Position < Raw.task_intent'Size / System.Storage_Unit) or else (Offset >= Raw.task_reservation_event'Position and then Offset - Raw.task_reservation_event'Position < Raw.task_reservation_event'Size / System.Storage_Unit) or else (Offset >= Raw.task_launch_event'Position and then Offset - Raw.task_launch_event'Position < Raw.task_launch_event'Size / System.Storage_Unit) or else (Offset >= Raw.parent_namespace_source'Position and then Offset - Raw.parent_namespace_source'Position < Raw.parent_namespace_source'Size / System.Storage_Unit) or else (Offset >= Raw.fd_lineage'Position and then Offset - Raw.fd_lineage'Position < Raw.fd_lineage'Size / System.Storage_Unit) or else (Offset >= Raw.source_lease'Position and then Offset - Raw.source_lease'Position < Raw.source_lease'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Root'Position .. Data'First + Raw.Root'Position + Raw.Root'Size / System.Storage_Unit - 1), Raw.Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Child'Position .. Data'First + Raw.Child'Position + Raw.Child'Size / System.Storage_Unit - 1), Raw.Child)
        and then Source_Padding_Valid (Data (Data'First + Raw.task_id'Position .. Data'First + Raw.task_id'Position + Raw.task_id'Size / System.Storage_Unit - 1), Raw.task_id)
        and then Source_Padding_Valid (Data (Data'First + Raw.root_world'Position .. Data'First + Raw.root_world'Position + Raw.root_world'Size / System.Storage_Unit - 1), Raw.root_world)
        and then Source_Padding_Valid (Data (Data'First + Raw.child_world'Position .. Data'First + Raw.child_world'Position + Raw.child_world'Size / System.Storage_Unit - 1), Raw.child_world)
        and then Source_Padding_Valid (Data (Data'First + Raw.root_instance'Position .. Data'First + Raw.root_instance'Position + Raw.root_instance'Size / System.Storage_Unit - 1), Raw.root_instance)
        and then Source_Padding_Valid (Data (Data'First + Raw.child_instance'Position .. Data'First + Raw.child_instance'Position + Raw.child_instance'Size / System.Storage_Unit - 1), Raw.child_instance)
        and then Source_Padding_Valid (Data (Data'First + Raw.world_store'Position .. Data'First + Raw.world_store'Position + Raw.world_store'Size / System.Storage_Unit - 1), Raw.world_store)
        and then Source_Padding_Valid (Data (Data'First + Raw.full_world_ancestry'Position .. Data'First + Raw.full_world_ancestry'Position + Raw.full_world_ancestry'Size / System.Storage_Unit - 1), Raw.full_world_ancestry)
        and then Source_Padding_Valid (Data (Data'First + Raw.original_workload'Position .. Data'First + Raw.original_workload'Position + Raw.original_workload'Size / System.Storage_Unit - 1), Raw.original_workload)
        and then Source_Padding_Valid (Data (Data'First + Raw.sandbox'Position .. Data'First + Raw.sandbox'Position + Raw.sandbox'Size / System.Storage_Unit - 1), Raw.sandbox)
        and then Source_Padding_Valid (Data (Data'First + Raw.adapter'Position .. Data'First + Raw.adapter'Position + Raw.adapter'Size / System.Storage_Unit - 1), Raw.adapter)
        and then Source_Padding_Valid (Data (Data'First + Raw.context'Position .. Data'First + Raw.context'Position + Raw.context'Size / System.Storage_Unit - 1), Raw.context)
        and then Source_Padding_Valid (Data (Data'First + Raw.mission'Position .. Data'First + Raw.mission'Position + Raw.mission'Size / System.Storage_Unit - 1), Raw.mission)
        and then Source_Padding_Valid (Data (Data'First + Raw.stdin'Position .. Data'First + Raw.stdin'Position + Raw.stdin'Size / System.Storage_Unit - 1), Raw.stdin)
        and then Source_Padding_Valid (Data (Data'First + Raw.credential_source'Position .. Data'First + Raw.credential_source'Position + Raw.credential_source'Size / System.Storage_Unit - 1), Raw.credential_source)
        and then Source_Padding_Valid (Data (Data'First + Raw.executable_source'Position .. Data'First + Raw.executable_source'Position + Raw.executable_source'Size / System.Storage_Unit - 1), Raw.executable_source)
        and then Source_Padding_Valid (Data (Data'First + Raw.configuration'Position .. Data'First + Raw.configuration'Position + Raw.configuration'Size / System.Storage_Unit - 1), Raw.configuration)
        and then Source_Padding_Valid (Data (Data'First + Raw.owner_plan'Position .. Data'First + Raw.owner_plan'Position + Raw.owner_plan'Size / System.Storage_Unit - 1), Raw.owner_plan)
        and then Source_Padding_Valid (Data (Data'First + Raw.native_cost_input'Position .. Data'First + Raw.native_cost_input'Position + Raw.native_cost_input'Size / System.Storage_Unit - 1), Raw.native_cost_input)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_request'Position .. Data'First + Raw.raw_request'Position + Raw.raw_request'Size / System.Storage_Unit - 1), Raw.raw_request)
        and then Source_Padding_Valid (Data (Data'First + Raw.requester'Position .. Data'First + Raw.requester'Position + Raw.requester'Size / System.Storage_Unit - 1), Raw.requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.cause'Position .. Data'First + Raw.cause'Position + Raw.cause'Size / System.Storage_Unit - 1), Raw.cause)
        and then Source_Padding_Valid (Data (Data'First + Raw.root_dispatch'Position .. Data'First + Raw.root_dispatch'Position + Raw.root_dispatch'Size / System.Storage_Unit - 1), Raw.root_dispatch)
        and then Source_Padding_Valid (Data (Data'First + Raw.root_running_event'Position .. Data'First + Raw.root_running_event'Position + Raw.root_running_event'Size / System.Storage_Unit - 1), Raw.root_running_event)
        and then Source_Padding_Valid (Data (Data'First + Raw.task_journal'Position .. Data'First + Raw.task_journal'Position + Raw.task_journal'Size / System.Storage_Unit - 1), Raw.task_journal)
        and then Source_Padding_Valid (Data (Data'First + Raw.task_intent'Position .. Data'First + Raw.task_intent'Position + Raw.task_intent'Size / System.Storage_Unit - 1), Raw.task_intent)
        and then Source_Padding_Valid (Data (Data'First + Raw.task_reservation_event'Position .. Data'First + Raw.task_reservation_event'Position + Raw.task_reservation_event'Size / System.Storage_Unit - 1), Raw.task_reservation_event)
        and then Source_Padding_Valid (Data (Data'First + Raw.task_launch_event'Position .. Data'First + Raw.task_launch_event'Position + Raw.task_launch_event'Size / System.Storage_Unit - 1), Raw.task_launch_event)
        and then Source_Padding_Valid (Data (Data'First + Raw.parent_namespace_source'Position .. Data'First + Raw.parent_namespace_source'Position + Raw.parent_namespace_source'Size / System.Storage_Unit - 1), Raw.parent_namespace_source)
        and then Source_Padding_Valid (Data (Data'First + Raw.fd_lineage'Position .. Data'First + Raw.fd_lineage'Position + Raw.fd_lineage'Size / System.Storage_Unit - 1), Raw.fd_lineage)
        and then Source_Padding_Valid (Data (Data'First + Raw.source_lease'Position .. Data'First + Raw.source_lease'Position + Raw.source_lease'Size / System.Storage_Unit - 1), Raw.source_lease);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : Y.Raw_Namespace) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.identity'Position and then Offset - Raw.identity'Position < Raw.identity'Size / System.Storage_Unit) or else (Offset >= Raw.parent'Position and then Offset - Raw.parent'Position < Raw.parent'Size / System.Storage_Unit) or else (Offset >= Raw.raw_nsfs'Position and then Offset - Raw.raw_nsfs'Position < Raw.raw_nsfs'Size / System.Storage_Unit) or else (Offset >= Raw.raw_get_parent'Position and then Offset - Raw.raw_get_parent'Position < Raw.raw_get_parent'Size / System.Storage_Unit) or else (Offset >= Raw.source_lease'Position and then Offset - Raw.source_lease'Position < Raw.source_lease'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.identity'Position .. Data'First + Raw.identity'Position + Raw.identity'Size / System.Storage_Unit - 1), Raw.identity)
        and then Source_Padding_Valid (Data (Data'First + Raw.parent'Position .. Data'First + Raw.parent'Position + Raw.parent'Size / System.Storage_Unit - 1), Raw.parent)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_nsfs'Position .. Data'First + Raw.raw_nsfs'Position + Raw.raw_nsfs'Size / System.Storage_Unit - 1), Raw.raw_nsfs)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_get_parent'Position .. Data'First + Raw.raw_get_parent'Position + Raw.raw_get_parent'Size / System.Storage_Unit - 1), Raw.raw_get_parent)
        and then Source_Padding_Valid (Data (Data'First + Raw.source_lease'Position .. Data'First + Raw.source_lease'Position + Raw.source_lease'Size / System.Storage_Unit - 1), Raw.source_lease);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Input) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Schema'Position and then Offset - Raw.Schema'Position < Raw.Schema'Size / System.Storage_Unit) or else (Offset >= Raw.Mode'Position and then Offset - Raw.Mode'Position < Raw.Mode'Size / System.Storage_Unit) or else (Offset >= Raw.Bound'Position and then Offset - Raw.Bound'Position < Raw.Bound'Size / System.Storage_Unit) or else (Offset >= Raw.Now'Position and then Offset - Raw.Now'Position < Raw.Now'Size / System.Storage_Unit) or else (Offset >= Raw.Facts'Position and then Offset - Raw.Facts'Position < Raw.Facts'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1), Raw.Bound)
        and then Source_Padding_Valid (Data (Data'First + Raw.Now'Position .. Data'First + Raw.Now'Position + Raw.Now'Size / System.Storage_Unit - 1), Raw.Now)
        and then Source_Padding_Valid (Data (Data'First + Raw.Facts'Position .. Data'First + Raw.Facts'Position + Raw.Facts'Size / System.Storage_Unit - 1), Raw.Facts);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Binding) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Action'Position and then Offset - Raw.Action'Position < Raw.Action'Size / System.Storage_Unit) or else (Offset >= Raw.Id'Position and then Offset - Raw.Id'Position < Raw.Id'Size / System.Storage_Unit) or else (Offset >= Raw.Peer'Position and then Offset - Raw.Peer'Position < Raw.Peer'Size / System.Storage_Unit) or else (Offset >= Raw.Preparer'Position and then Offset - Raw.Preparer'Position < Raw.Preparer'Size / System.Storage_Unit) or else (Offset >= Raw.Owner'Position and then Offset - Raw.Owner'Position < Raw.Owner'Size / System.Storage_Unit) or else (Offset >= Raw.Target_Owner'Position and then Offset - Raw.Target_Owner'Position < Raw.Target_Owner'Size / System.Storage_Unit) or else (Offset >= Raw.Policy_Epoch'Position and then Offset - Raw.Policy_Epoch'Position < Raw.Policy_Epoch'Size / System.Storage_Unit) or else (Offset >= Raw.Resource_Epoch'Position and then Offset - Raw.Resource_Epoch'Position < Raw.Resource_Epoch'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Id'Position .. Data'First + Raw.Id'Position + Raw.Id'Size / System.Storage_Unit - 1), Raw.Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Peer'Position .. Data'First + Raw.Peer'Position + Raw.Peer'Size / System.Storage_Unit - 1), Raw.Peer)
        and then Source_Padding_Valid (Data (Data'First + Raw.Preparer'Position .. Data'First + Raw.Preparer'Position + Raw.Preparer'Size / System.Storage_Unit - 1), Raw.Preparer)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner'Position .. Data'First + Raw.Owner'Position + Raw.Owner'Size / System.Storage_Unit - 1), Raw.Owner)
        and then Source_Padding_Valid (Data (Data'First + Raw.Target_Owner'Position .. Data'First + Raw.Target_Owner'Position + Raw.Target_Owner'Size / System.Storage_Unit - 1), Raw.Target_Owner)
        and then Source_Padding_Valid (Data (Data'First + Raw.Policy_Epoch'Position .. Data'First + Raw.Policy_Epoch'Position + Raw.Policy_Epoch'Size / System.Storage_Unit - 1), Raw.Policy_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource_Epoch'Position .. Data'First + Raw.Resource_Epoch'Position + Raw.Resource_Epoch'Size / System.Storage_Unit - 1), Raw.Resource_Epoch);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Ids) return Boolean is
   begin
      for I in Raw'Range loop
         if not Source_Padding_Valid (Data (Data'First + Q.Byte_Count (T.A.Identity_Field'Pos (I) - T.A.Identity_Field'Pos (Raw'First)) * C.Raw_Digest'Size / System.Storage_Unit .. Data'First + Q.Byte_Count (T.A.Identity_Field'Pos (I) - T.A.Identity_Field'Pos (Raw'First)) * C.Raw_Digest'Size / System.Storage_Unit + C.Raw_Digest'Size / System.Storage_Unit - 1), Raw (I)) then return False; end if;
      end loop;
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_UID) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Present'Position and then Offset - Raw.Present'Position < Raw.Present'Size / System.Storage_Unit) or else (Offset >= Raw.Value'Position and then Offset - Raw.Value'Position < Raw.Value'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Quantity) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Present'Position and then Offset - Raw.Present'Position < Raw.Present'Size / System.Storage_Unit) or else (Offset >= Raw.Negative'Position and then Offset - Raw.Negative'Position < Raw.Negative'Size / System.Storage_Unit) or else (Offset >= Raw.First'Position and then Offset - Raw.First'Position < Raw.First'Size / System.Storage_Unit) or else (Offset >= Raw.Length'Position and then Offset - Raw.Length'Position < Raw.Length'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Evidence) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if (Offset >= Raw.Effect_Material_First'Position and then Offset - Raw.Effect_Material_First'Position < Raw.Effect_Material_First'Size / System.Storage_Unit) or else (Offset >= Raw.Effect_Material_Length'Position and then Offset - Raw.Effect_Material_Length'Position < Raw.Effect_Material_Length'Size / System.Storage_Unit) then
               null;
            else
            if not ((Offset >= Raw.Effect_Binding'Position and then Offset - Raw.Effect_Binding'Position < Raw.Effect_Binding'Size / System.Storage_Unit) or else (Offset >= Raw.Actual_Receipt_Root'Position and then Offset - Raw.Actual_Receipt_Root'Position < Raw.Actual_Receipt_Root'Size / System.Storage_Unit) or else (Offset >= Raw.Actual_Causal_Root'Position and then Offset - Raw.Actual_Causal_Root'Position < Raw.Actual_Causal_Root'Size / System.Storage_Unit) or else (Offset >= Raw.No_Effect_Binding'Position and then Offset - Raw.No_Effect_Binding'Position < Raw.No_Effect_Binding'Size / System.Storage_Unit) or else (Offset >= Raw.Owner_Resolution'Position and then Offset - Raw.Owner_Resolution'Position < Raw.Owner_Resolution'Size / System.Storage_Unit) or else (Offset >= Raw.Quarantine_Head'Position and then Offset - Raw.Quarantine_Head'Position < Raw.Quarantine_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Witnessed_Receipt_Head'Position and then Offset - Raw.Witnessed_Receipt_Head'Position < Raw.Witnessed_Receipt_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Witnessed_Causal_Head'Position and then Offset - Raw.Witnessed_Causal_Head'Position < Raw.Witnessed_Causal_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Recovery'Position and then Offset - Raw.Recovery'Position < Raw.Recovery'Size / System.Storage_Unit) or else (Offset >= Raw.Original_Use'Position and then Offset - Raw.Original_Use'Position < Raw.Original_Use'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
            end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Effect_Binding'Position .. Data'First + Raw.Effect_Binding'Position + Raw.Effect_Binding'Size / System.Storage_Unit - 1), Raw.Effect_Binding)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Receipt_Root'Position .. Data'First + Raw.Actual_Receipt_Root'Position + Raw.Actual_Receipt_Root'Size / System.Storage_Unit - 1), Raw.Actual_Receipt_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Causal_Root'Position .. Data'First + Raw.Actual_Causal_Root'Position + Raw.Actual_Causal_Root'Size / System.Storage_Unit - 1), Raw.Actual_Causal_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.No_Effect_Binding'Position .. Data'First + Raw.No_Effect_Binding'Position + Raw.No_Effect_Binding'Size / System.Storage_Unit - 1), Raw.No_Effect_Binding)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner_Resolution'Position .. Data'First + Raw.Owner_Resolution'Position + Raw.Owner_Resolution'Size / System.Storage_Unit - 1), Raw.Owner_Resolution)
        and then Source_Padding_Valid (Data (Data'First + Raw.Quarantine_Head'Position .. Data'First + Raw.Quarantine_Head'Position + Raw.Quarantine_Head'Size / System.Storage_Unit - 1), Raw.Quarantine_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Witnessed_Receipt_Head'Position .. Data'First + Raw.Witnessed_Receipt_Head'Position + Raw.Witnessed_Receipt_Head'Size / System.Storage_Unit - 1), Raw.Witnessed_Receipt_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Witnessed_Causal_Head'Position .. Data'First + Raw.Witnessed_Causal_Head'Position + Raw.Witnessed_Causal_Head'Size / System.Storage_Unit - 1), Raw.Witnessed_Causal_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Recovery'Position .. Data'First + Raw.Recovery'Position + Raw.Recovery'Size / System.Storage_Unit - 1), Raw.Recovery)
        and then Source_Padding_Valid (Data (Data'First + Raw.Original_Use'Position .. Data'First + Raw.Original_Use'Position + Raw.Original_Use'Size / System.Storage_Unit - 1), Raw.Original_Use);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Request) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Schema_Version'Position and then Offset - Raw.Schema_Version'Position < Raw.Schema_Version'Size / System.Storage_Unit) or else (Offset >= Raw.State'Position and then Offset - Raw.State'Position < Raw.State'Size / System.Storage_Unit) or else (Offset >= Raw.Fresh'Position and then Offset - Raw.Fresh'Position < Raw.Fresh'Size / System.Storage_Unit) or else (Offset >= Raw.Historical'Position and then Offset - Raw.Historical'Position < Raw.Historical'Size / System.Storage_Unit) or else (Offset >= Raw.Grant_Eligible'Position and then Offset - Raw.Grant_Eligible'Position < Raw.Grant_Eligible'Size / System.Storage_Unit) or else (Offset >= Raw.Issued_Binding'Position and then Offset - Raw.Issued_Binding'Position < Raw.Issued_Binding'Size / System.Storage_Unit) or else (Offset >= Raw.Recovered_Binding'Position and then Offset - Raw.Recovered_Binding'Position < Raw.Recovered_Binding'Size / System.Storage_Unit) or else (Offset >= Raw.Native'Position and then Offset - Raw.Native'Position < Raw.Native'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Issued_Binding'Position .. Data'First + Raw.Issued_Binding'Position + Raw.Issued_Binding'Size / System.Storage_Unit - 1), Raw.Issued_Binding)
        and then Source_Padding_Valid (Data (Data'First + Raw.Recovered_Binding'Position .. Data'First + Raw.Recovered_Binding'Position + Raw.Recovered_Binding'Size / System.Storage_Unit - 1), Raw.Recovered_Binding)
        and then Source_Padding_Valid (Data (Data'First + Raw.Native'Position .. Data'First + Raw.Native'Position + Raw.Native'Size / System.Storage_Unit - 1), Raw.Native);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Binding) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Mode'Position and then Offset - Raw.Mode'Position < Raw.Mode'Size / System.Storage_Unit) or else (Offset >= Raw.Operation'Position and then Offset - Raw.Operation'Position < Raw.Operation'Size / System.Storage_Unit) or else (Offset >= Raw.Transaction'Position and then Offset - Raw.Transaction'Position < Raw.Transaction'Size / System.Storage_Unit) or else (Offset >= Raw.Capability'Position and then Offset - Raw.Capability'Position < Raw.Capability'Size / System.Storage_Unit) or else (Offset >= Raw.Universe_Head'Position and then Offset - Raw.Universe_Head'Position < Raw.Universe_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Instance'Position and then Offset - Raw.Instance'Position < Raw.Instance'Size / System.Storage_Unit) or else (Offset >= Raw.Subject'Position and then Offset - Raw.Subject'Position < Raw.Subject'Size / System.Storage_Unit) or else (Offset >= Raw.Staged_Root'Position and then Offset - Raw.Staged_Root'Position < Raw.Staged_Root'Size / System.Storage_Unit) or else (Offset >= Raw.Current_Requirement'Position and then Offset - Raw.Current_Requirement'Position < Raw.Current_Requirement'Size / System.Storage_Unit) or else (Offset >= Raw.Resulting_Requirement'Position and then Offset - Raw.Resulting_Requirement'Position < Raw.Resulting_Requirement'Size / System.Storage_Unit) or else (Offset >= Raw.Requester'Position and then Offset - Raw.Requester'Position < Raw.Requester'Size / System.Storage_Unit) or else (Offset >= Raw.Grant_Use'Position and then Offset - Raw.Grant_Use'Position < Raw.Grant_Use'Size / System.Storage_Unit) or else (Offset >= Raw.Policy_Identity'Position and then Offset - Raw.Policy_Identity'Position < Raw.Policy_Identity'Size / System.Storage_Unit) or else (Offset >= Raw.Selected_Evaluation'Position and then Offset - Raw.Selected_Evaluation'Position < Raw.Selected_Evaluation'Size / System.Storage_Unit) or else (Offset >= Raw.History_Head'Position and then Offset - Raw.History_Head'Position < Raw.History_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Reservation'Position and then Offset - Raw.Reservation'Position < Raw.Reservation'Size / System.Storage_Unit) or else (Offset >= Raw.Host'Position and then Offset - Raw.Host'Position < Raw.Host'Size / System.Storage_Unit) or else (Offset >= Raw.Before_Prime'Position and then Offset - Raw.Before_Prime'Position < Raw.Before_Prime'Size / System.Storage_Unit) or else (Offset >= Raw.Before_Root'Position and then Offset - Raw.Before_Root'Position < Raw.Before_Root'Size / System.Storage_Unit) or else (Offset >= Raw.Before_Mapping'Position and then Offset - Raw.Before_Mapping'Position < Raw.Before_Mapping'Size / System.Storage_Unit) or else (Offset >= Raw.Staged_Mapping'Position and then Offset - Raw.Staged_Mapping'Position < Raw.Staged_Mapping'Size / System.Storage_Unit) or else (Offset >= Raw.Input_Snapshot'Position and then Offset - Raw.Input_Snapshot'Position < Raw.Input_Snapshot'Size / System.Storage_Unit) or else (Offset >= Raw.Kernel_Build'Position and then Offset - Raw.Kernel_Build'Position < Raw.Kernel_Build'Size / System.Storage_Unit) or else (Offset >= Raw.Kernel_Library'Position and then Offset - Raw.Kernel_Library'Position < Raw.Kernel_Library'Size / System.Storage_Unit) or else (Offset >= Raw.Kernel_Mapping'Position and then Offset - Raw.Kernel_Mapping'Position < Raw.Kernel_Mapping'Size / System.Storage_Unit) or else (Offset >= Raw.Issuer_Head'Position and then Offset - Raw.Issuer_Head'Position < Raw.Issuer_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Receipt_Head'Position and then Offset - Raw.Receipt_Head'Position < Raw.Receipt_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Causal_Head'Position and then Offset - Raw.Causal_Head'Position < Raw.Causal_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Policy_Epoch'Position and then Offset - Raw.Policy_Epoch'Position < Raw.Policy_Epoch'Size / System.Storage_Unit) or else (Offset >= Raw.Resource_Epoch'Position and then Offset - Raw.Resource_Epoch'Position < Raw.Resource_Epoch'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Operation'Position .. Data'First + Raw.Operation'Position + Raw.Operation'Size / System.Storage_Unit - 1), Raw.Operation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Transaction'Position .. Data'First + Raw.Transaction'Position + Raw.Transaction'Size / System.Storage_Unit - 1), Raw.Transaction)
        and then Source_Padding_Valid (Data (Data'First + Raw.Capability'Position .. Data'First + Raw.Capability'Position + Raw.Capability'Size / System.Storage_Unit - 1), Raw.Capability)
        and then Source_Padding_Valid (Data (Data'First + Raw.Universe_Head'Position .. Data'First + Raw.Universe_Head'Position + Raw.Universe_Head'Size / System.Storage_Unit - 1), Raw.Universe_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Instance'Position .. Data'First + Raw.Instance'Position + Raw.Instance'Size / System.Storage_Unit - 1), Raw.Instance)
        and then Source_Padding_Valid (Data (Data'First + Raw.Subject'Position .. Data'First + Raw.Subject'Position + Raw.Subject'Size / System.Storage_Unit - 1), Raw.Subject)
        and then Source_Padding_Valid (Data (Data'First + Raw.Staged_Root'Position .. Data'First + Raw.Staged_Root'Position + Raw.Staged_Root'Size / System.Storage_Unit - 1), Raw.Staged_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Current_Requirement'Position .. Data'First + Raw.Current_Requirement'Position + Raw.Current_Requirement'Size / System.Storage_Unit - 1), Raw.Current_Requirement)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resulting_Requirement'Position .. Data'First + Raw.Resulting_Requirement'Position + Raw.Resulting_Requirement'Size / System.Storage_Unit - 1), Raw.Resulting_Requirement)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester'Position .. Data'First + Raw.Requester'Position + Raw.Requester'Size / System.Storage_Unit - 1), Raw.Requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.Grant_Use'Position .. Data'First + Raw.Grant_Use'Position + Raw.Grant_Use'Size / System.Storage_Unit - 1), Raw.Grant_Use)
        and then Source_Padding_Valid (Data (Data'First + Raw.Policy_Identity'Position .. Data'First + Raw.Policy_Identity'Position + Raw.Policy_Identity'Size / System.Storage_Unit - 1), Raw.Policy_Identity)
        and then Source_Padding_Valid (Data (Data'First + Raw.Selected_Evaluation'Position .. Data'First + Raw.Selected_Evaluation'Position + Raw.Selected_Evaluation'Size / System.Storage_Unit - 1), Raw.Selected_Evaluation)
        and then Source_Padding_Valid (Data (Data'First + Raw.History_Head'Position .. Data'First + Raw.History_Head'Position + Raw.History_Head'Size / System.Storage_Unit - 1), Raw.History_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Reservation'Position .. Data'First + Raw.Reservation'Position + Raw.Reservation'Size / System.Storage_Unit - 1), Raw.Reservation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Host'Position .. Data'First + Raw.Host'Position + Raw.Host'Size / System.Storage_Unit - 1), Raw.Host)
        and then Source_Padding_Valid (Data (Data'First + Raw.Before_Prime'Position .. Data'First + Raw.Before_Prime'Position + Raw.Before_Prime'Size / System.Storage_Unit - 1), Raw.Before_Prime)
        and then Source_Padding_Valid (Data (Data'First + Raw.Before_Root'Position .. Data'First + Raw.Before_Root'Position + Raw.Before_Root'Size / System.Storage_Unit - 1), Raw.Before_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Before_Mapping'Position .. Data'First + Raw.Before_Mapping'Position + Raw.Before_Mapping'Size / System.Storage_Unit - 1), Raw.Before_Mapping)
        and then Source_Padding_Valid (Data (Data'First + Raw.Staged_Mapping'Position .. Data'First + Raw.Staged_Mapping'Position + Raw.Staged_Mapping'Size / System.Storage_Unit - 1), Raw.Staged_Mapping)
        and then Source_Padding_Valid (Data (Data'First + Raw.Input_Snapshot'Position .. Data'First + Raw.Input_Snapshot'Position + Raw.Input_Snapshot'Size / System.Storage_Unit - 1), Raw.Input_Snapshot)
        and then Source_Padding_Valid (Data (Data'First + Raw.Kernel_Build'Position .. Data'First + Raw.Kernel_Build'Position + Raw.Kernel_Build'Size / System.Storage_Unit - 1), Raw.Kernel_Build)
        and then Source_Padding_Valid (Data (Data'First + Raw.Kernel_Library'Position .. Data'First + Raw.Kernel_Library'Position + Raw.Kernel_Library'Size / System.Storage_Unit - 1), Raw.Kernel_Library)
        and then Source_Padding_Valid (Data (Data'First + Raw.Kernel_Mapping'Position .. Data'First + Raw.Kernel_Mapping'Position + Raw.Kernel_Mapping'Size / System.Storage_Unit - 1), Raw.Kernel_Mapping)
        and then Source_Padding_Valid (Data (Data'First + Raw.Issuer_Head'Position .. Data'First + Raw.Issuer_Head'Position + Raw.Issuer_Head'Size / System.Storage_Unit - 1), Raw.Issuer_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Receipt_Head'Position .. Data'First + Raw.Receipt_Head'Position + Raw.Receipt_Head'Size / System.Storage_Unit - 1), Raw.Receipt_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Causal_Head'Position .. Data'First + Raw.Causal_Head'Position + Raw.Causal_Head'Size / System.Storage_Unit - 1), Raw.Causal_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Policy_Epoch'Position .. Data'First + Raw.Policy_Epoch'Position + Raw.Policy_Epoch'Size / System.Storage_Unit - 1), Raw.Policy_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource_Epoch'Position .. Data'First + Raw.Resource_Epoch'Position + Raw.Resource_Epoch'Size / System.Storage_Unit - 1), Raw.Resource_Epoch);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Digest) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Present'Position and then Offset - Raw.Present'Position < Raw.Present'Size / System.Storage_Unit) or else (Offset >= Raw.Value'Position and then Offset - Raw.Value'Position < Raw.Value'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Value'Position .. Data'First + Raw.Value'Position + Raw.Value'Size / System.Storage_Unit - 1), Raw.Value);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Hash) return Boolean is
   begin
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Epoch) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Present'Position and then Offset - Raw.Present'Position < Raw.Present'Size / System.Storage_Unit) or else (Offset >= Raw.Negative'Position and then Offset - Raw.Negative'Position < Raw.Negative'Size / System.Storage_Unit) or else (Offset >= Raw.First'Position and then Offset - Raw.First'Position < Raw.First'Size / System.Storage_Unit) or else (Offset >= Raw.Length'Position and then Offset - Raw.Length'Position < Raw.Length'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Native) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Live_Mapping'Position and then Offset - Raw.Live_Mapping'Position < Raw.Live_Mapping'Size / System.Storage_Unit) or else (Offset >= Raw.Live_Root'Position and then Offset - Raw.Live_Root'Position < Raw.Live_Root'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Live_Mapping'Position .. Data'First + Raw.Live_Mapping'Position + Raw.Live_Mapping'Size / System.Storage_Unit - 1), Raw.Live_Mapping)
        and then Source_Padding_Valid (Data (Data'First + Raw.Live_Root'Position .. Data'First + Raw.Live_Root'Position + Raw.Live_Root'Size / System.Storage_Unit - 1), Raw.Live_Root);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Grant) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Id'Position and then Offset - Raw.Id'Position < Raw.Id'Size / System.Storage_Unit) or else (Offset >= Raw.Parent'Position and then Offset - Raw.Parent'Position < Raw.Parent'Size / System.Storage_Unit) or else (Offset >= Raw.Issuer'Position and then Offset - Raw.Issuer'Position < Raw.Issuer'Size / System.Storage_Unit) or else (Offset >= Raw.Instance'Position and then Offset - Raw.Instance'Position < Raw.Instance'Size / System.Storage_Unit) or else (Offset >= Raw.Root_Set'Position and then Offset - Raw.Root_Set'Position < Raw.Root_Set'Size / System.Storage_Unit) or else (Offset >= Raw.Policy'Position and then Offset - Raw.Policy'Position < Raw.Policy'Size / System.Storage_Unit) or else (Offset >= Raw.Subject'Position and then Offset - Raw.Subject'Position < Raw.Subject'Size / System.Storage_Unit) or else (Offset >= Raw.Owner'Position and then Offset - Raw.Owner'Position < Raw.Owner'Size / System.Storage_Unit) or else (Offset >= Raw.Allowed'Position and then Offset - Raw.Allowed'Position < Raw.Allowed'Size / System.Storage_Unit) or else (Offset >= Raw.State'Position and then Offset - Raw.State'Position < Raw.State'Size / System.Storage_Unit) or else (Offset >= Raw.Epoch'Position and then Offset - Raw.Epoch'Position < Raw.Epoch'Size / System.Storage_Unit) or else (Offset >= Raw.Ceiling'Position and then Offset - Raw.Ceiling'Position < Raw.Ceiling'Size / System.Storage_Unit) or else (Offset >= Raw.Issued_At'Position and then Offset - Raw.Issued_At'Position < Raw.Issued_At'Size / System.Storage_Unit) or else (Offset >= Raw.Expires_At'Position and then Offset - Raw.Expires_At'Position < Raw.Expires_At'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Id'Position .. Data'First + Raw.Id'Position + Raw.Id'Size / System.Storage_Unit - 1), Raw.Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Parent'Position .. Data'First + Raw.Parent'Position + Raw.Parent'Size / System.Storage_Unit - 1), Raw.Parent)
        and then Source_Padding_Valid (Data (Data'First + Raw.Issuer'Position .. Data'First + Raw.Issuer'Position + Raw.Issuer'Size / System.Storage_Unit - 1), Raw.Issuer)
        and then Source_Padding_Valid (Data (Data'First + Raw.Instance'Position .. Data'First + Raw.Instance'Position + Raw.Instance'Size / System.Storage_Unit - 1), Raw.Instance)
        and then Source_Padding_Valid (Data (Data'First + Raw.Root_Set'Position .. Data'First + Raw.Root_Set'Position + Raw.Root_Set'Size / System.Storage_Unit - 1), Raw.Root_Set)
        and then Source_Padding_Valid (Data (Data'First + Raw.Policy'Position .. Data'First + Raw.Policy'Position + Raw.Policy'Size / System.Storage_Unit - 1), Raw.Policy)
        and then Source_Padding_Valid (Data (Data'First + Raw.Subject'Position .. Data'First + Raw.Subject'Position + Raw.Subject'Size / System.Storage_Unit - 1), Raw.Subject)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner'Position .. Data'First + Raw.Owner'Position + Raw.Owner'Size / System.Storage_Unit - 1), Raw.Owner)
        and then Source_Padding_Valid (Data (Data'First + Raw.Allowed'Position .. Data'First + Raw.Allowed'Position + Raw.Allowed'Size / System.Storage_Unit - 1), Raw.Allowed)
        and then Source_Padding_Valid (Data (Data'First + Raw.Epoch'Position .. Data'First + Raw.Epoch'Position + Raw.Epoch'Size / System.Storage_Unit - 1), Raw.Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Ceiling'Position .. Data'First + Raw.Ceiling'Position + Raw.Ceiling'Size / System.Storage_Unit - 1), Raw.Ceiling)
        and then Source_Padding_Valid (Data (Data'First + Raw.Issued_At'Position .. Data'First + Raw.Issued_At'Position + Raw.Issued_At'Size / System.Storage_Unit - 1), Raw.Issued_At)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expires_At'Position .. Data'First + Raw.Expires_At'Position + Raw.Expires_At'Size / System.Storage_Unit - 1), Raw.Expires_At);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Rights) return Boolean is
   begin
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Use) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Bound'Position and then Offset - Raw.Bound'Position < Raw.Bound'Size / System.Storage_Unit) or else (Offset >= Raw.State'Position and then Offset - Raw.State'Position < Raw.State'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1), Raw.Bound);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : C.Raw_Row) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Previous'Position and then Offset - Raw.Previous'Position < Raw.Previous'Size / System.Storage_Unit) or else (Offset >= Raw.Actual_Payload_Root'Position and then Offset - Raw.Actual_Payload_Root'Position < Raw.Actual_Payload_Root'Size / System.Storage_Unit) or else (Offset >= Raw.Stored_Payload_Root'Position and then Offset - Raw.Stored_Payload_Root'Position < Raw.Stored_Payload_Root'Size / System.Storage_Unit) or else (Offset >= Raw.Stored_Head'Position and then Offset - Raw.Stored_Head'Position < Raw.Stored_Head'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Previous'Position .. Data'First + Raw.Previous'Position + Raw.Previous'Size / System.Storage_Unit - 1), Raw.Previous)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Payload_Root'Position .. Data'First + Raw.Actual_Payload_Root'Position + Raw.Actual_Payload_Root'Size / System.Storage_Unit - 1), Raw.Actual_Payload_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Stored_Payload_Root'Position .. Data'First + Raw.Stored_Payload_Root'Position + Raw.Stored_Payload_Root'Size / System.Storage_Unit - 1), Raw.Stored_Payload_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Stored_Head'Position .. Data'First + Raw.Stored_Head'Position + Raw.Stored_Head'Size / System.Storage_Unit - 1), Raw.Stored_Head);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : D.Raw_Capability) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Index'Position and then Offset - Raw.Index'Position < Raw.Index'Size / System.Storage_Unit) or else (Offset >= Raw.Bounding'Position and then Offset - Raw.Bounding'Position < Raw.Bounding'Size / System.Storage_Unit) or else (Offset >= Raw.Ambient'Position and then Offset - Raw.Ambient'Position < Raw.Ambient'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Index'Position .. Data'First + Raw.Index'Position + Raw.Index'Size / System.Storage_Unit - 1), Raw.Index)
        and then Source_Padding_Valid (Data (Data'First + Raw.Bounding'Position .. Data'First + Raw.Bounding'Position + Raw.Bounding'Size / System.Storage_Unit - 1), Raw.Bounding)
        and then Source_Padding_Valid (Data (Data'First + Raw.Ambient'Position .. Data'First + Raw.Ambient'Position + Raw.Ambient'Size / System.Storage_Unit - 1), Raw.Ambient);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Scope_Frame) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Scope'Position and then Offset - Raw.Scope'Position < Raw.Scope'Size / System.Storage_Unit) or else (Offset >= Raw.First_Epoch'Position and then Offset - Raw.First_Epoch'Position < Raw.First_Epoch'Size / System.Storage_Unit) or else (Offset >= Raw.Universe_Head'Position and then Offset - Raw.Universe_Head'Position < Raw.Universe_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Frame_Head'Position and then Offset - Raw.Frame_Head'Position < Raw.Frame_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Prior_Frame'Position and then Offset - Raw.Prior_Frame'Position < Raw.Prior_Frame'Size / System.Storage_Unit) or else (Offset >= Raw.Store_Genesis'Position and then Offset - Raw.Store_Genesis'Position < Raw.Store_Genesis'Size / System.Storage_Unit) or else (Offset >= Raw.Store_Id'Position and then Offset - Raw.Store_Id'Position < Raw.Store_Id'Size / System.Storage_Unit) or else (Offset >= Raw.Root_Head'Position and then Offset - Raw.Root_Head'Position < Raw.Root_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Prime'Position and then Offset - Raw.Prime'Position < Raw.Prime'Size / System.Storage_Unit) or else (Offset >= Raw.Root_Count'Position and then Offset - Raw.Root_Count'Position < Raw.Root_Count'Size / System.Storage_Unit) or else (Offset >= Raw.Cause'Position and then Offset - Raw.Cause'Position < Raw.Cause'Size / System.Storage_Unit) or else (Offset >= Raw.Requester'Position and then Offset - Raw.Requester'Position < Raw.Requester'Size / System.Storage_Unit) or else (Offset >= Raw.Receipt'Position and then Offset - Raw.Receipt'Position < Raw.Receipt'Size / System.Storage_Unit) or else (Offset >= Raw.Catalogue_Head'Position and then Offset - Raw.Catalogue_Head'Position < Raw.Catalogue_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Observation_Head'Position and then Offset - Raw.Observation_Head'Position < Raw.Observation_Head'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Scope'Position .. Data'First + Raw.Scope'Position + Raw.Scope'Size / System.Storage_Unit - 1), Raw.Scope)
        and then Source_Padding_Valid (Data (Data'First + Raw.First_Epoch'Position .. Data'First + Raw.First_Epoch'Position + Raw.First_Epoch'Size / System.Storage_Unit - 1), Raw.First_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Universe_Head'Position .. Data'First + Raw.Universe_Head'Position + Raw.Universe_Head'Size / System.Storage_Unit - 1), Raw.Universe_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Frame_Head'Position .. Data'First + Raw.Frame_Head'Position + Raw.Frame_Head'Size / System.Storage_Unit - 1), Raw.Frame_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Prior_Frame'Position .. Data'First + Raw.Prior_Frame'Position + Raw.Prior_Frame'Size / System.Storage_Unit - 1), Raw.Prior_Frame)
        and then Source_Padding_Valid (Data (Data'First + Raw.Store_Genesis'Position .. Data'First + Raw.Store_Genesis'Position + Raw.Store_Genesis'Size / System.Storage_Unit - 1), Raw.Store_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Store_Id'Position .. Data'First + Raw.Store_Id'Position + Raw.Store_Id'Size / System.Storage_Unit - 1), Raw.Store_Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Root_Head'Position .. Data'First + Raw.Root_Head'Position + Raw.Root_Head'Size / System.Storage_Unit - 1), Raw.Root_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Prime'Position .. Data'First + Raw.Prime'Position + Raw.Prime'Size / System.Storage_Unit - 1), Raw.Prime)
        and then Source_Padding_Valid (Data (Data'First + Raw.Root_Count'Position .. Data'First + Raw.Root_Count'Position + Raw.Root_Count'Size / System.Storage_Unit - 1), Raw.Root_Count)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cause'Position .. Data'First + Raw.Cause'Position + Raw.Cause'Size / System.Storage_Unit - 1), Raw.Cause)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester'Position .. Data'First + Raw.Requester'Position + Raw.Requester'Size / System.Storage_Unit - 1), Raw.Requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.Receipt'Position .. Data'First + Raw.Receipt'Position + Raw.Receipt'Size / System.Storage_Unit - 1), Raw.Receipt)
        and then Source_Padding_Valid (Data (Data'First + Raw.Catalogue_Head'Position .. Data'First + Raw.Catalogue_Head'Position + Raw.Catalogue_Head'Size / System.Storage_Unit - 1), Raw.Catalogue_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Observation_Head'Position .. Data'First + Raw.Observation_Head'Position + Raw.Observation_Head'Size / System.Storage_Unit - 1), Raw.Observation_Head);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Projection) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Key'Position and then Offset - Raw.Key'Position < Raw.Key'Size / System.Storage_Unit) or else (Offset >= Raw.Bound'Position and then Offset - Raw.Bound'Position < Raw.Bound'Size / System.Storage_Unit) or else (Offset >= Raw.Origin'Position and then Offset - Raw.Origin'Position < Raw.Origin'Size / System.Storage_Unit) or else (Offset >= Raw.Catalogue_Head'Position and then Offset - Raw.Catalogue_Head'Position < Raw.Catalogue_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Numerator'Position and then Offset - Raw.Numerator'Position < Raw.Numerator'Size / System.Storage_Unit) or else (Offset >= Raw.Denominator'Position and then Offset - Raw.Denominator'Position < Raw.Denominator'Size / System.Storage_Unit) or else (Offset >= Raw.Amount'Position and then Offset - Raw.Amount'Position < Raw.Amount'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Key'Position .. Data'First + Raw.Key'Position + Raw.Key'Size / System.Storage_Unit - 1), Raw.Key)
        and then Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1), Raw.Bound)
        and then Source_Padding_Valid (Data (Data'First + Raw.Origin'Position .. Data'First + Raw.Origin'Position + Raw.Origin'Size / System.Storage_Unit - 1), Raw.Origin)
        and then Source_Padding_Valid (Data (Data'First + Raw.Catalogue_Head'Position .. Data'First + Raw.Catalogue_Head'Position + Raw.Catalogue_Head'Size / System.Storage_Unit - 1), Raw.Catalogue_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Numerator'Position .. Data'First + Raw.Numerator'Position + Raw.Numerator'Size / System.Storage_Unit - 1), Raw.Numerator)
        and then Source_Padding_Valid (Data (Data'First + Raw.Denominator'Position .. Data'First + Raw.Denominator'Position + Raw.Denominator'Size / System.Storage_Unit - 1), Raw.Denominator)
        and then Source_Padding_Valid (Data (Data'First + Raw.Amount'Position .. Data'First + Raw.Amount'Position + Raw.Amount'Size / System.Storage_Unit - 1), Raw.Amount);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Physical_Key) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Machine'Position and then Offset - Raw.Machine'Position < Raw.Machine'Size / System.Storage_Unit) or else (Offset >= Raw.Resource'Position and then Offset - Raw.Resource'Position < Raw.Resource'Size / System.Storage_Unit) or else (Offset >= Raw.Unit'Position and then Offset - Raw.Unit'Position < Raw.Unit'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Machine'Position .. Data'First + Raw.Machine'Position + Raw.Machine'Size / System.Storage_Unit - 1), Raw.Machine)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource'Position .. Data'First + Raw.Resource'Position + Raw.Resource'Size / System.Storage_Unit - 1), Raw.Resource)
        and then Source_Padding_Valid (Data (Data'First + Raw.Unit'Position .. Data'First + Raw.Unit'Position + Raw.Unit'Size / System.Storage_Unit - 1), Raw.Unit);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Bucket) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Key'Position and then Offset - Raw.Key'Position < Raw.Key'Size / System.Storage_Unit) or else (Offset >= Raw.Capacity'Position and then Offset - Raw.Capacity'Position < Raw.Capacity'Size / System.Storage_Unit) or else (Offset >= Raw.Held_Total'Position and then Offset - Raw.Held_Total'Position < Raw.Held_Total'Size / System.Storage_Unit) or else (Offset >= Raw.Charged_Total'Position and then Offset - Raw.Charged_Total'Position < Raw.Charged_Total'Size / System.Storage_Unit) or else (Offset >= Raw.Capacity_Source'Position and then Offset - Raw.Capacity_Source'Position < Raw.Capacity_Source'Size / System.Storage_Unit) or else (Offset >= Raw.Catalogue_Head'Position and then Offset - Raw.Catalogue_Head'Position < Raw.Catalogue_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Observation_Head'Position and then Offset - Raw.Observation_Head'Position < Raw.Observation_Head'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Key'Position .. Data'First + Raw.Key'Position + Raw.Key'Size / System.Storage_Unit - 1), Raw.Key)
        and then Source_Padding_Valid (Data (Data'First + Raw.Capacity'Position .. Data'First + Raw.Capacity'Position + Raw.Capacity'Size / System.Storage_Unit - 1), Raw.Capacity)
        and then Source_Padding_Valid (Data (Data'First + Raw.Held_Total'Position .. Data'First + Raw.Held_Total'Position + Raw.Held_Total'Size / System.Storage_Unit - 1), Raw.Held_Total)
        and then Source_Padding_Valid (Data (Data'First + Raw.Charged_Total'Position .. Data'First + Raw.Charged_Total'Position + Raw.Charged_Total'Size / System.Storage_Unit - 1), Raw.Charged_Total)
        and then Source_Padding_Valid (Data (Data'First + Raw.Capacity_Source'Position .. Data'First + Raw.Capacity_Source'Position + Raw.Capacity_Source'Size / System.Storage_Unit - 1), Raw.Capacity_Source)
        and then Source_Padding_Valid (Data (Data'First + Raw.Catalogue_Head'Position .. Data'First + Raw.Catalogue_Head'Position + Raw.Catalogue_Head'Size / System.Storage_Unit - 1), Raw.Catalogue_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Observation_Head'Position .. Data'First + Raw.Observation_Head'Position + Raw.Observation_Head'Size / System.Storage_Unit - 1), Raw.Observation_Head);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Native) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Scope'Position and then Offset - Raw.Scope'Position < Raw.Scope'Size / System.Storage_Unit) or else (Offset >= Raw.Resource_Epoch'Position and then Offset - Raw.Resource_Epoch'Position < Raw.Resource_Epoch'Size / System.Storage_Unit) or else (Offset >= Raw.Bound'Position and then Offset - Raw.Bound'Position < Raw.Bound'Size / System.Storage_Unit) or else (Offset >= Raw.Actual_Unit'Position and then Offset - Raw.Actual_Unit'Position < Raw.Actual_Unit'Size / System.Storage_Unit) or else (Offset >= Raw.Cgroup'Position and then Offset - Raw.Cgroup'Position < Raw.Cgroup'Size / System.Storage_Unit) or else (Offset >= Raw.Invocation'Position and then Offset - Raw.Invocation'Position < Raw.Invocation'Size / System.Storage_Unit) or else (Offset >= Raw.Observation_Head'Position and then Offset - Raw.Observation_Head'Position < Raw.Observation_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Observed'Position and then Offset - Raw.Observed'Position < Raw.Observed'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Scope'Position .. Data'First + Raw.Scope'Position + Raw.Scope'Size / System.Storage_Unit - 1), Raw.Scope)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource_Epoch'Position .. Data'First + Raw.Resource_Epoch'Position + Raw.Resource_Epoch'Size / System.Storage_Unit - 1), Raw.Resource_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1), Raw.Bound)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Unit'Position .. Data'First + Raw.Actual_Unit'Position + Raw.Actual_Unit'Size / System.Storage_Unit - 1), Raw.Actual_Unit)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cgroup'Position .. Data'First + Raw.Cgroup'Position + Raw.Cgroup'Size / System.Storage_Unit - 1), Raw.Cgroup)
        and then Source_Padding_Valid (Data (Data'First + Raw.Invocation'Position .. Data'First + Raw.Invocation'Position + Raw.Invocation'Size / System.Storage_Unit - 1), Raw.Invocation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Observation_Head'Position .. Data'First + Raw.Observation_Head'Position + Raw.Observation_Head'Size / System.Storage_Unit - 1), Raw.Observation_Head);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : O.Raw_Facts) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Current'Position and then Offset - Raw.Current'Position < Raw.Current'Size / System.Storage_Unit) or else (Offset >= Raw.Current_Epoch'Position and then Offset - Raw.Current_Epoch'Position < Raw.Current_Epoch'Size / System.Storage_Unit) or else (Offset >= Raw.Retained'Position and then Offset - Raw.Retained'Position < Raw.Retained'Size / System.Storage_Unit) or else (Offset >= Raw.Current_Universe_Head'Position and then Offset - Raw.Current_Universe_Head'Position < Raw.Current_Universe_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Current_Ledger_Head'Position and then Offset - Raw.Current_Ledger_Head'Position < Raw.Current_Ledger_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Intent'Position and then Offset - Raw.Intent'Position < Raw.Intent'Size / System.Storage_Unit) or else (Offset >= Raw.Dispatch'Position and then Offset - Raw.Dispatch'Position < Raw.Dispatch'Size / System.Storage_Unit) or else (Offset >= Raw.Observation_Head'Position and then Offset - Raw.Observation_Head'Position < Raw.Observation_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Actual_Unit'Position and then Offset - Raw.Actual_Unit'Position < Raw.Actual_Unit'Size / System.Storage_Unit) or else (Offset >= Raw.Cgroup'Position and then Offset - Raw.Cgroup'Position < Raw.Cgroup'Size / System.Storage_Unit) or else (Offset >= Raw.Invocation'Position and then Offset - Raw.Invocation'Position < Raw.Invocation'Size / System.Storage_Unit) or else (Offset >= Raw.Namespace'Position and then Offset - Raw.Namespace'Position < Raw.Namespace'Size / System.Storage_Unit) or else (Offset >= Raw.Held_Namespace'Position and then Offset - Raw.Held_Namespace'Position < Raw.Held_Namespace'Size / System.Storage_Unit) or else (Offset >= Raw.Peer'Position and then Offset - Raw.Peer'Position < Raw.Peer'Size / System.Storage_Unit) or else (Offset >= Raw.Held_Peer'Position and then Offset - Raw.Held_Peer'Position < Raw.Held_Peer'Size / System.Storage_Unit) or else (Offset >= Raw.Helper_Image'Position and then Offset - Raw.Helper_Image'Position < Raw.Helper_Image'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Helper_Image'Position and then Offset - Raw.Expected_Helper_Image'Position < Raw.Expected_Helper_Image'Size / System.Storage_Unit) or else (Offset >= Raw.Challenge'Position and then Offset - Raw.Challenge'Position < Raw.Challenge'Size / System.Storage_Unit) or else (Offset >= Raw.Held_Challenge'Position and then Offset - Raw.Held_Challenge'Position < Raw.Held_Challenge'Size / System.Storage_Unit) or else (Offset >= Raw.Protocol'Position and then Offset - Raw.Protocol'Position < Raw.Protocol'Size / System.Storage_Unit) or else (Offset >= Raw.Closed_Event'Position and then Offset - Raw.Closed_Event'Position < Raw.Closed_Event'Size / System.Storage_Unit) or else (Offset >= Raw.Namespace_Wait'Position and then Offset - Raw.Namespace_Wait'Position < Raw.Namespace_Wait'Size / System.Storage_Unit) or else (Offset >= Raw.Helper_Wait'Position and then Offset - Raw.Helper_Wait'Position < Raw.Helper_Wait'Size / System.Storage_Unit) or else (Offset >= Raw.Cgroup_Events'Position and then Offset - Raw.Cgroup_Events'Position < Raw.Cgroup_Events'Size / System.Storage_Unit) or else (Offset >= Raw.Cgroup_Type'Position and then Offset - Raw.Cgroup_Type'Position < Raw.Cgroup_Type'Size / System.Storage_Unit) or else (Offset >= Raw.Manager_Delegate'Position and then Offset - Raw.Manager_Delegate'Position < Raw.Manager_Delegate'Size / System.Storage_Unit) or else (Offset >= Raw.Cgroup_Owner'Position and then Offset - Raw.Cgroup_Owner'Position < Raw.Cgroup_Owner'Size / System.Storage_Unit) or else (Offset >= Raw.Cgroup_Group_Write'Position and then Offset - Raw.Cgroup_Group_Write'Position < Raw.Cgroup_Group_Write'Size / System.Storage_Unit) or else (Offset >= Raw.Cgroup_Other_Write'Position and then Offset - Raw.Cgroup_Other_Write'Position < Raw.Cgroup_Other_Write'Size / System.Storage_Unit) or else (Offset >= Raw.Actual_Store_Genesis'Position and then Offset - Raw.Actual_Store_Genesis'Position < Raw.Actual_Store_Genesis'Size / System.Storage_Unit) or else (Offset >= Raw.Actual_Store_Id'Position and then Offset - Raw.Actual_Store_Id'Position < Raw.Actual_Store_Id'Size / System.Storage_Unit) or else (Offset >= Raw.Owner_Store_Genesis'Position and then Offset - Raw.Owner_Store_Genesis'Position < Raw.Owner_Store_Genesis'Size / System.Storage_Unit) or else (Offset >= Raw.Owner_Store_Id'Position and then Offset - Raw.Owner_Store_Id'Position < Raw.Owner_Store_Id'Size / System.Storage_Unit) or else (Offset >= Raw.Genesis_Universe'Position and then Offset - Raw.Genesis_Universe'Position < Raw.Genesis_Universe'Size / System.Storage_Unit) or else (Offset >= Raw.Genesis_Instance'Position and then Offset - Raw.Genesis_Instance'Position < Raw.Genesis_Instance'Size / System.Storage_Unit) or else (Offset >= Raw.Genesis_Context_Head'Position and then Offset - Raw.Genesis_Context_Head'Position < Raw.Genesis_Context_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Genesis_Prime'Position and then Offset - Raw.Genesis_Prime'Position < Raw.Genesis_Prime'Size / System.Storage_Unit) or else (Offset >= Raw.Genesis_Root_Count'Position and then Offset - Raw.Genesis_Root_Count'Position < Raw.Genesis_Root_Count'Size / System.Storage_Unit) or else (Offset >= Raw.Phase'Position and then Offset - Raw.Phase'Position < Raw.Phase'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Current'Position .. Data'First + Raw.Current'Position + Raw.Current'Size / System.Storage_Unit - 1), Raw.Current)
        and then Source_Padding_Valid (Data (Data'First + Raw.Current_Epoch'Position .. Data'First + Raw.Current_Epoch'Position + Raw.Current_Epoch'Size / System.Storage_Unit - 1), Raw.Current_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Retained'Position .. Data'First + Raw.Retained'Position + Raw.Retained'Size / System.Storage_Unit - 1), Raw.Retained)
        and then Source_Padding_Valid (Data (Data'First + Raw.Current_Universe_Head'Position .. Data'First + Raw.Current_Universe_Head'Position + Raw.Current_Universe_Head'Size / System.Storage_Unit - 1), Raw.Current_Universe_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Current_Ledger_Head'Position .. Data'First + Raw.Current_Ledger_Head'Position + Raw.Current_Ledger_Head'Size / System.Storage_Unit - 1), Raw.Current_Ledger_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Intent'Position .. Data'First + Raw.Intent'Position + Raw.Intent'Size / System.Storage_Unit - 1), Raw.Intent)
        and then Source_Padding_Valid (Data (Data'First + Raw.Dispatch'Position .. Data'First + Raw.Dispatch'Position + Raw.Dispatch'Size / System.Storage_Unit - 1), Raw.Dispatch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Observation_Head'Position .. Data'First + Raw.Observation_Head'Position + Raw.Observation_Head'Size / System.Storage_Unit - 1), Raw.Observation_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Unit'Position .. Data'First + Raw.Actual_Unit'Position + Raw.Actual_Unit'Size / System.Storage_Unit - 1), Raw.Actual_Unit)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cgroup'Position .. Data'First + Raw.Cgroup'Position + Raw.Cgroup'Size / System.Storage_Unit - 1), Raw.Cgroup)
        and then Source_Padding_Valid (Data (Data'First + Raw.Invocation'Position .. Data'First + Raw.Invocation'Position + Raw.Invocation'Size / System.Storage_Unit - 1), Raw.Invocation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Namespace'Position .. Data'First + Raw.Namespace'Position + Raw.Namespace'Size / System.Storage_Unit - 1), Raw.Namespace)
        and then Source_Padding_Valid (Data (Data'First + Raw.Held_Namespace'Position .. Data'First + Raw.Held_Namespace'Position + Raw.Held_Namespace'Size / System.Storage_Unit - 1), Raw.Held_Namespace)
        and then Source_Padding_Valid (Data (Data'First + Raw.Peer'Position .. Data'First + Raw.Peer'Position + Raw.Peer'Size / System.Storage_Unit - 1), Raw.Peer)
        and then Source_Padding_Valid (Data (Data'First + Raw.Held_Peer'Position .. Data'First + Raw.Held_Peer'Position + Raw.Held_Peer'Size / System.Storage_Unit - 1), Raw.Held_Peer)
        and then Source_Padding_Valid (Data (Data'First + Raw.Helper_Image'Position .. Data'First + Raw.Helper_Image'Position + Raw.Helper_Image'Size / System.Storage_Unit - 1), Raw.Helper_Image)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Helper_Image'Position .. Data'First + Raw.Expected_Helper_Image'Position + Raw.Expected_Helper_Image'Size / System.Storage_Unit - 1), Raw.Expected_Helper_Image)
        and then Source_Padding_Valid (Data (Data'First + Raw.Challenge'Position .. Data'First + Raw.Challenge'Position + Raw.Challenge'Size / System.Storage_Unit - 1), Raw.Challenge)
        and then Source_Padding_Valid (Data (Data'First + Raw.Held_Challenge'Position .. Data'First + Raw.Held_Challenge'Position + Raw.Held_Challenge'Size / System.Storage_Unit - 1), Raw.Held_Challenge)
        and then Source_Padding_Valid (Data (Data'First + Raw.Protocol'Position .. Data'First + Raw.Protocol'Position + Raw.Protocol'Size / System.Storage_Unit - 1), Raw.Protocol)
        and then Source_Padding_Valid (Data (Data'First + Raw.Closed_Event'Position .. Data'First + Raw.Closed_Event'Position + Raw.Closed_Event'Size / System.Storage_Unit - 1), Raw.Closed_Event)
        and then Source_Padding_Valid (Data (Data'First + Raw.Namespace_Wait'Position .. Data'First + Raw.Namespace_Wait'Position + Raw.Namespace_Wait'Size / System.Storage_Unit - 1), Raw.Namespace_Wait)
        and then Source_Padding_Valid (Data (Data'First + Raw.Helper_Wait'Position .. Data'First + Raw.Helper_Wait'Position + Raw.Helper_Wait'Size / System.Storage_Unit - 1), Raw.Helper_Wait)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cgroup_Events'Position .. Data'First + Raw.Cgroup_Events'Position + Raw.Cgroup_Events'Size / System.Storage_Unit - 1), Raw.Cgroup_Events)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cgroup_Type'Position .. Data'First + Raw.Cgroup_Type'Position + Raw.Cgroup_Type'Size / System.Storage_Unit - 1), Raw.Cgroup_Type)
        and then Source_Padding_Valid (Data (Data'First + Raw.Manager_Delegate'Position .. Data'First + Raw.Manager_Delegate'Position + Raw.Manager_Delegate'Size / System.Storage_Unit - 1), Raw.Manager_Delegate)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cgroup_Owner'Position .. Data'First + Raw.Cgroup_Owner'Position + Raw.Cgroup_Owner'Size / System.Storage_Unit - 1), Raw.Cgroup_Owner)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cgroup_Group_Write'Position .. Data'First + Raw.Cgroup_Group_Write'Position + Raw.Cgroup_Group_Write'Size / System.Storage_Unit - 1), Raw.Cgroup_Group_Write)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cgroup_Other_Write'Position .. Data'First + Raw.Cgroup_Other_Write'Position + Raw.Cgroup_Other_Write'Size / System.Storage_Unit - 1), Raw.Cgroup_Other_Write)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Store_Genesis'Position .. Data'First + Raw.Actual_Store_Genesis'Position + Raw.Actual_Store_Genesis'Size / System.Storage_Unit - 1), Raw.Actual_Store_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Store_Id'Position .. Data'First + Raw.Actual_Store_Id'Position + Raw.Actual_Store_Id'Size / System.Storage_Unit - 1), Raw.Actual_Store_Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner_Store_Genesis'Position .. Data'First + Raw.Owner_Store_Genesis'Position + Raw.Owner_Store_Genesis'Size / System.Storage_Unit - 1), Raw.Owner_Store_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner_Store_Id'Position .. Data'First + Raw.Owner_Store_Id'Position + Raw.Owner_Store_Id'Size / System.Storage_Unit - 1), Raw.Owner_Store_Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Genesis_Universe'Position .. Data'First + Raw.Genesis_Universe'Position + Raw.Genesis_Universe'Size / System.Storage_Unit - 1), Raw.Genesis_Universe)
        and then Source_Padding_Valid (Data (Data'First + Raw.Genesis_Instance'Position .. Data'First + Raw.Genesis_Instance'Position + Raw.Genesis_Instance'Size / System.Storage_Unit - 1), Raw.Genesis_Instance)
        and then Source_Padding_Valid (Data (Data'First + Raw.Genesis_Context_Head'Position .. Data'First + Raw.Genesis_Context_Head'Position + Raw.Genesis_Context_Head'Size / System.Storage_Unit - 1), Raw.Genesis_Context_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Genesis_Prime'Position .. Data'First + Raw.Genesis_Prime'Position + Raw.Genesis_Prime'Size / System.Storage_Unit - 1), Raw.Genesis_Prime)
        and then Source_Padding_Valid (Data (Data'First + Raw.Genesis_Root_Count'Position .. Data'First + Raw.Genesis_Root_Count'Position + Raw.Genesis_Root_Count'Size / System.Storage_Unit - 1), Raw.Genesis_Root_Count);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Result) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Status'Position and then Offset - Raw.Status'Position < Raw.Status'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Result) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Disposition'Position and then Offset - Raw.Disposition'Position < Raw.Disposition'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : HC.Raw_Input) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Historical'Position and then Offset - Raw.Historical'Position < Raw.Historical'Size / System.Storage_Unit) or else (Offset >= Raw.Current'Position and then Offset - Raw.Current'Position < Raw.Current'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Historical'Position .. Data'First + Raw.Historical'Position + Raw.Historical'Size / System.Storage_Unit - 1), Raw.Historical)
        and then Source_Padding_Valid (Data (Data'First + Raw.Current'Position .. Data'First + Raw.Current'Position + Raw.Current'Size / System.Storage_Unit - 1), Raw.Current);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CX.Raw_Input) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Operation_Input'Position and then Offset - Raw.Operation_Input'Position < Raw.Operation_Input'Size / System.Storage_Unit) or else (Offset >= Raw.Material'Position and then Offset - Raw.Material'Position < Raw.Material'Size / System.Storage_Unit) or else (Offset >= Raw.Before'Position and then Offset - Raw.Before'Position < Raw.Before'Size / System.Storage_Unit) or else (Offset >= Raw.Mode'Position and then Offset - Raw.Mode'Position < Raw.Mode'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Operation_Input'Position .. Data'First + Raw.Operation_Input'Position + Raw.Operation_Input'Size / System.Storage_Unit - 1), Raw.Operation_Input)
        and then Source_Padding_Valid (Data (Data'First + Raw.Material'Position .. Data'First + Raw.Material'Position + Raw.Material'Size / System.Storage_Unit - 1), Raw.Material);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CO.Raw_Input) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Authority'Position and then Offset - Raw.Authority'Position < Raw.Authority'Size / System.Storage_Unit) or else (Offset >= Raw.State'Position and then Offset - Raw.State'Position < Raw.State'Size / System.Storage_Unit) or else (Offset >= Raw.Bound'Position and then Offset - Raw.Bound'Position < Raw.Bound'Size / System.Storage_Unit) or else (Offset >= Raw.Requester'Position and then Offset - Raw.Requester'Position < Raw.Requester'Size / System.Storage_Unit) or else (Offset >= Raw.Peer'Position and then Offset - Raw.Peer'Position < Raw.Peer'Size / System.Storage_Unit) or else (Offset >= Raw.Collapse'Position and then Offset - Raw.Collapse'Position < Raw.Collapse'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Authority'Position .. Data'First + Raw.Authority'Position + Raw.Authority'Size / System.Storage_Unit - 1), Raw.Authority)
        and then Source_Padding_Valid (Data (Data'First + Raw.State'Position .. Data'First + Raw.State'Position + Raw.State'Size / System.Storage_Unit - 1), Raw.State)
        and then Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1), Raw.Bound)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester'Position .. Data'First + Raw.Requester'Position + Raw.Requester'Size / System.Storage_Unit - 1), Raw.Requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.Peer'Position .. Data'First + Raw.Peer'Position + Raw.Peer'Size / System.Storage_Unit - 1), Raw.Peer)
        and then Source_Padding_Valid (Data (Data'First + Raw.Collapse'Position .. Data'First + Raw.Collapse'Position + Raw.Collapse'Size / System.Storage_Unit - 1), Raw.Collapse);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_State) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Scope'Position and then Offset - Raw.Scope'Position < Raw.Scope'Size / System.Storage_Unit) or else (Offset >= Raw.Resource_Epoch'Position and then Offset - Raw.Resource_Epoch'Position < Raw.Resource_Epoch'Size / System.Storage_Unit) or else (Offset >= Raw.Universe_Head'Position and then Offset - Raw.Universe_Head'Position < Raw.Universe_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Ledger_Head'Position and then Offset - Raw.Ledger_Head'Position < Raw.Ledger_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Capacity'Position and then Offset - Raw.Capacity'Position < Raw.Capacity'Size / System.Storage_Unit) or else (Offset >= Raw.Held_Total'Position and then Offset - Raw.Held_Total'Position < Raw.Held_Total'Size / System.Storage_Unit) or else (Offset >= Raw.Charged_Total'Position and then Offset - Raw.Charged_Total'Position < Raw.Charged_Total'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Scope'Position .. Data'First + Raw.Scope'Position + Raw.Scope'Size / System.Storage_Unit - 1), Raw.Scope)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource_Epoch'Position .. Data'First + Raw.Resource_Epoch'Position + Raw.Resource_Epoch'Size / System.Storage_Unit - 1), Raw.Resource_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Universe_Head'Position .. Data'First + Raw.Universe_Head'Position + Raw.Universe_Head'Size / System.Storage_Unit - 1), Raw.Universe_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Ledger_Head'Position .. Data'First + Raw.Ledger_Head'Position + Raw.Ledger_Head'Size / System.Storage_Unit - 1), Raw.Ledger_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Capacity'Position .. Data'First + Raw.Capacity'Position + Raw.Capacity'Size / System.Storage_Unit - 1), Raw.Capacity)
        and then Source_Padding_Valid (Data (Data'First + Raw.Held_Total'Position .. Data'First + Raw.Held_Total'Position + Raw.Held_Total'Size / System.Storage_Unit - 1), Raw.Held_Total)
        and then Source_Padding_Valid (Data (Data'First + Raw.Charged_Total'Position .. Data'First + Raw.Charged_Total'Position + Raw.Charged_Total'Size / System.Storage_Unit - 1), Raw.Charged_Total);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CW.Raw_Request) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Candidate_State'Position and then Offset - Raw.Candidate_State'Position < Raw.Candidate_State'Size / System.Storage_Unit) or else (Offset >= Raw.Phase'Position and then Offset - Raw.Phase'Position < Raw.Phase'Size / System.Storage_Unit) or else (Offset >= Raw.Evaluation_Mode'Position and then Offset - Raw.Evaluation_Mode'Position < Raw.Evaluation_Mode'Size / System.Storage_Unit) or else (Offset >= Raw.Conflicts'Position and then Offset - Raw.Conflicts'Position < Raw.Conflicts'Size / System.Storage_Unit) or else (Offset >= Raw.Foreign_Writes'Position and then Offset - Raw.Foreign_Writes'Position < Raw.Foreign_Writes'Size / System.Storage_Unit) or else (Offset >= Raw.Roster_Complete'Position and then Offset - Raw.Roster_Complete'Position < Raw.Roster_Complete'Size / System.Storage_Unit) or else (Offset >= Raw.Staged_Roster_Complete'Position and then Offset - Raw.Staged_Roster_Complete'Position < Raw.Staged_Roster_Complete'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Parent'Position and then Offset - Raw.Expected_Parent'Position < Raw.Expected_Parent'Size / System.Storage_Unit) or else (Offset >= Raw.Candidate_Parent'Position and then Offset - Raw.Candidate_Parent'Position < Raw.Candidate_Parent'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Subject'Position and then Offset - Raw.Expected_Subject'Position < Raw.Expected_Subject'Size / System.Storage_Unit) or else (Offset >= Raw.Evidence_Subject'Position and then Offset - Raw.Evidence_Subject'Position < Raw.Evidence_Subject'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Base'Position and then Offset - Raw.Expected_Base'Position < Raw.Expected_Base'Size / System.Storage_Unit) or else (Offset >= Raw.Candidate_Base'Position and then Offset - Raw.Candidate_Base'Position < Raw.Candidate_Base'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Delta'Position and then Offset - Raw.Expected_Delta'Position < Raw.Expected_Delta'Size / System.Storage_Unit) or else (Offset >= Raw.Candidate_Delta'Position and then Offset - Raw.Candidate_Delta'Position < Raw.Candidate_Delta'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Root_Set'Position and then Offset - Raw.Expected_Root_Set'Position < Raw.Expected_Root_Set'Size / System.Storage_Unit) or else (Offset >= Raw.Candidate_Root_Set'Position and then Offset - Raw.Candidate_Root_Set'Position < Raw.Candidate_Root_Set'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Staged_Root'Position and then Offset - Raw.Expected_Staged_Root'Position < Raw.Expected_Staged_Root'Size / System.Storage_Unit) or else (Offset >= Raw.Actual_Staged_Root'Position and then Offset - Raw.Actual_Staged_Root'Position < Raw.Actual_Staged_Root'Size / System.Storage_Unit) or else (Offset >= Raw.Staged_Content_Root'Position and then Offset - Raw.Staged_Content_Root'Position < Raw.Staged_Content_Root'Size / System.Storage_Unit) or else (Offset >= Raw.Tested_Root'Position and then Offset - Raw.Tested_Root'Position < Raw.Tested_Root'Size / System.Storage_Unit) or else (Offset >= Raw.Current_Requirement'Position and then Offset - Raw.Current_Requirement'Position < Raw.Current_Requirement'Size / System.Storage_Unit) or else (Offset >= Raw.Resulting_Requirement'Position and then Offset - Raw.Resulting_Requirement'Position < Raw.Resulting_Requirement'Size / System.Storage_Unit) or else (Offset >= Raw.Evaluated_Requirement'Position and then Offset - Raw.Evaluated_Requirement'Position < Raw.Evaluated_Requirement'Size / System.Storage_Unit) or else (Offset >= Raw.Declared_Verifiers'Position and then Offset - Raw.Declared_Verifiers'Position < Raw.Declared_Verifiers'Size / System.Storage_Unit) or else (Offset >= Raw.Executed_Verifiers'Position and then Offset - Raw.Executed_Verifiers'Position < Raw.Executed_Verifiers'Size / System.Storage_Unit) or else (Offset >= Raw.Staged_Evaluated_Requirement'Position and then Offset - Raw.Staged_Evaluated_Requirement'Position < Raw.Staged_Evaluated_Requirement'Size / System.Storage_Unit) or else (Offset >= Raw.Staged_Executed_Verifiers'Position and then Offset - Raw.Staged_Executed_Verifiers'Position < Raw.Staged_Executed_Verifiers'Size / System.Storage_Unit) or else (Offset >= Raw.Staged_Examined_Root'Position and then Offset - Raw.Staged_Examined_Root'Position < Raw.Staged_Examined_Root'Size / System.Storage_Unit) or else (Offset >= Raw.Expected_Checkpoint'Position and then Offset - Raw.Expected_Checkpoint'Position < Raw.Expected_Checkpoint'Size / System.Storage_Unit) or else (Offset >= Raw.Witnessed_Checkpoint'Position and then Offset - Raw.Witnessed_Checkpoint'Position < Raw.Witnessed_Checkpoint'Size / System.Storage_Unit) or else (Offset >= Raw.Registered_Watch_Set'Position and then Offset - Raw.Registered_Watch_Set'Position < Raw.Registered_Watch_Set'Size / System.Storage_Unit) or else (Offset >= Raw.Watched_Set'Position and then Offset - Raw.Watched_Set'Position < Raw.Watched_Set'Size / System.Storage_Unit) or else (Offset >= Raw.Generation_Before'Position and then Offset - Raw.Generation_Before'Position < Raw.Generation_Before'Size / System.Storage_Unit) or else (Offset >= Raw.Generation_After'Position and then Offset - Raw.Generation_After'Position < Raw.Generation_After'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Expected_Parent'Position .. Data'First + Raw.Expected_Parent'Position + Raw.Expected_Parent'Size / System.Storage_Unit - 1), Raw.Expected_Parent)
        and then Source_Padding_Valid (Data (Data'First + Raw.Candidate_Parent'Position .. Data'First + Raw.Candidate_Parent'Position + Raw.Candidate_Parent'Size / System.Storage_Unit - 1), Raw.Candidate_Parent)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Subject'Position .. Data'First + Raw.Expected_Subject'Position + Raw.Expected_Subject'Size / System.Storage_Unit - 1), Raw.Expected_Subject)
        and then Source_Padding_Valid (Data (Data'First + Raw.Evidence_Subject'Position .. Data'First + Raw.Evidence_Subject'Position + Raw.Evidence_Subject'Size / System.Storage_Unit - 1), Raw.Evidence_Subject)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Base'Position .. Data'First + Raw.Expected_Base'Position + Raw.Expected_Base'Size / System.Storage_Unit - 1), Raw.Expected_Base)
        and then Source_Padding_Valid (Data (Data'First + Raw.Candidate_Base'Position .. Data'First + Raw.Candidate_Base'Position + Raw.Candidate_Base'Size / System.Storage_Unit - 1), Raw.Candidate_Base)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Delta'Position .. Data'First + Raw.Expected_Delta'Position + Raw.Expected_Delta'Size / System.Storage_Unit - 1), Raw.Expected_Delta)
        and then Source_Padding_Valid (Data (Data'First + Raw.Candidate_Delta'Position .. Data'First + Raw.Candidate_Delta'Position + Raw.Candidate_Delta'Size / System.Storage_Unit - 1), Raw.Candidate_Delta)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Root_Set'Position .. Data'First + Raw.Expected_Root_Set'Position + Raw.Expected_Root_Set'Size / System.Storage_Unit - 1), Raw.Expected_Root_Set)
        and then Source_Padding_Valid (Data (Data'First + Raw.Candidate_Root_Set'Position .. Data'First + Raw.Candidate_Root_Set'Position + Raw.Candidate_Root_Set'Size / System.Storage_Unit - 1), Raw.Candidate_Root_Set)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Staged_Root'Position .. Data'First + Raw.Expected_Staged_Root'Position + Raw.Expected_Staged_Root'Size / System.Storage_Unit - 1), Raw.Expected_Staged_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Staged_Root'Position .. Data'First + Raw.Actual_Staged_Root'Position + Raw.Actual_Staged_Root'Size / System.Storage_Unit - 1), Raw.Actual_Staged_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Staged_Content_Root'Position .. Data'First + Raw.Staged_Content_Root'Position + Raw.Staged_Content_Root'Size / System.Storage_Unit - 1), Raw.Staged_Content_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Tested_Root'Position .. Data'First + Raw.Tested_Root'Position + Raw.Tested_Root'Size / System.Storage_Unit - 1), Raw.Tested_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Current_Requirement'Position .. Data'First + Raw.Current_Requirement'Position + Raw.Current_Requirement'Size / System.Storage_Unit - 1), Raw.Current_Requirement)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resulting_Requirement'Position .. Data'First + Raw.Resulting_Requirement'Position + Raw.Resulting_Requirement'Size / System.Storage_Unit - 1), Raw.Resulting_Requirement)
        and then Source_Padding_Valid (Data (Data'First + Raw.Evaluated_Requirement'Position .. Data'First + Raw.Evaluated_Requirement'Position + Raw.Evaluated_Requirement'Size / System.Storage_Unit - 1), Raw.Evaluated_Requirement)
        and then Source_Padding_Valid (Data (Data'First + Raw.Declared_Verifiers'Position .. Data'First + Raw.Declared_Verifiers'Position + Raw.Declared_Verifiers'Size / System.Storage_Unit - 1), Raw.Declared_Verifiers)
        and then Source_Padding_Valid (Data (Data'First + Raw.Executed_Verifiers'Position .. Data'First + Raw.Executed_Verifiers'Position + Raw.Executed_Verifiers'Size / System.Storage_Unit - 1), Raw.Executed_Verifiers)
        and then Source_Padding_Valid (Data (Data'First + Raw.Staged_Evaluated_Requirement'Position .. Data'First + Raw.Staged_Evaluated_Requirement'Position + Raw.Staged_Evaluated_Requirement'Size / System.Storage_Unit - 1), Raw.Staged_Evaluated_Requirement)
        and then Source_Padding_Valid (Data (Data'First + Raw.Staged_Executed_Verifiers'Position .. Data'First + Raw.Staged_Executed_Verifiers'Position + Raw.Staged_Executed_Verifiers'Size / System.Storage_Unit - 1), Raw.Staged_Executed_Verifiers)
        and then Source_Padding_Valid (Data (Data'First + Raw.Staged_Examined_Root'Position .. Data'First + Raw.Staged_Examined_Root'Position + Raw.Staged_Examined_Root'Size / System.Storage_Unit - 1), Raw.Staged_Examined_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Checkpoint'Position .. Data'First + Raw.Expected_Checkpoint'Position + Raw.Expected_Checkpoint'Size / System.Storage_Unit - 1), Raw.Expected_Checkpoint)
        and then Source_Padding_Valid (Data (Data'First + Raw.Witnessed_Checkpoint'Position .. Data'First + Raw.Witnessed_Checkpoint'Position + Raw.Witnessed_Checkpoint'Size / System.Storage_Unit - 1), Raw.Witnessed_Checkpoint)
        and then Source_Padding_Valid (Data (Data'First + Raw.Registered_Watch_Set'Position .. Data'First + Raw.Registered_Watch_Set'Position + Raw.Registered_Watch_Set'Size / System.Storage_Unit - 1), Raw.Registered_Watch_Set)
        and then Source_Padding_Valid (Data (Data'First + Raw.Watched_Set'Position .. Data'First + Raw.Watched_Set'Position + Raw.Watched_Set'Size / System.Storage_Unit - 1), Raw.Watched_Set)
        and then Source_Padding_Valid (Data (Data'First + Raw.Generation_Before'Position .. Data'First + Raw.Generation_Before'Position + Raw.Generation_Before'Size / System.Storage_Unit - 1), Raw.Generation_Before)
        and then Source_Padding_Valid (Data (Data'First + Raw.Generation_After'Position .. Data'First + Raw.Generation_After'Position + Raw.Generation_After'Size / System.Storage_Unit - 1), Raw.Generation_After);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CW.Raw_Optional_Hash) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Present'Position and then Offset - Raw.Present'Position < Raw.Present'Size / System.Storage_Unit) or else (Offset >= Raw.Value'Position and then Offset - Raw.Value'Position < Raw.Value'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Value'Position .. Data'First + Raw.Value'Position + Raw.Value'Size / System.Storage_Unit - 1), Raw.Value);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CW.Raw_Bytes_32) return Boolean is
   begin
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CW.Raw_Optional_Counter) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Present'Position and then Offset - Raw.Present'Position < Raw.Present'Size / System.Storage_Unit) or else (Offset >= Raw.Value_LE'Position and then Offset - Raw.Value_LE'Position < Raw.Value_LE'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Value_LE'Position .. Data'First + Raw.Value_LE'Position + Raw.Value_LE'Size / System.Storage_Unit - 1), Raw.Value_LE);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CW.Raw_Bytes_8) return Boolean is
   begin
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CX.Raw_Material) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Worker_Issued'Position and then Offset - Raw.Worker_Issued'Position < Raw.Worker_Issued'Size / System.Storage_Unit) or else (Offset >= Raw.Worker_Recovered'Position and then Offset - Raw.Worker_Recovered'Position < Raw.Worker_Recovered'Size / System.Storage_Unit) or else (Offset >= Raw.Canonical_Issued'Position and then Offset - Raw.Canonical_Issued'Position < Raw.Canonical_Issued'Size / System.Storage_Unit) or else (Offset >= Raw.Canonical_Recovered'Position and then Offset - Raw.Canonical_Recovered'Position < Raw.Canonical_Recovered'Size / System.Storage_Unit) or else (Offset >= Raw.Worker_Native'Position and then Offset - Raw.Worker_Native'Position < Raw.Worker_Native'Size / System.Storage_Unit) or else (Offset >= Raw.Canonical_Native'Position and then Offset - Raw.Canonical_Native'Position < Raw.Canonical_Native'Size / System.Storage_Unit) or else (Offset >= Raw.Worker_Receipt_Genesis'Position and then Offset - Raw.Worker_Receipt_Genesis'Position < Raw.Worker_Receipt_Genesis'Size / System.Storage_Unit) or else (Offset >= Raw.Owner_Receipt_Genesis'Position and then Offset - Raw.Owner_Receipt_Genesis'Position < Raw.Owner_Receipt_Genesis'Size / System.Storage_Unit) or else (Offset >= Raw.Worker_Receipt_Head'Position and then Offset - Raw.Worker_Receipt_Head'Position < Raw.Worker_Receipt_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Worker_Causal_Genesis'Position and then Offset - Raw.Worker_Causal_Genesis'Position < Raw.Worker_Causal_Genesis'Size / System.Storage_Unit) or else (Offset >= Raw.Owner_Causal_Genesis'Position and then Offset - Raw.Owner_Causal_Genesis'Position < Raw.Owner_Causal_Genesis'Size / System.Storage_Unit) or else (Offset >= Raw.Worker_Causal_Head'Position and then Offset - Raw.Worker_Causal_Head'Position < Raw.Worker_Causal_Head'Size / System.Storage_Unit) or else (Offset >= Raw.Quarantine_Head'Position and then Offset - Raw.Quarantine_Head'Position < Raw.Quarantine_Head'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Worker_Issued'Position .. Data'First + Raw.Worker_Issued'Position + Raw.Worker_Issued'Size / System.Storage_Unit - 1), Raw.Worker_Issued)
        and then Source_Padding_Valid (Data (Data'First + Raw.Worker_Recovered'Position .. Data'First + Raw.Worker_Recovered'Position + Raw.Worker_Recovered'Size / System.Storage_Unit - 1), Raw.Worker_Recovered)
        and then Source_Padding_Valid (Data (Data'First + Raw.Canonical_Issued'Position .. Data'First + Raw.Canonical_Issued'Position + Raw.Canonical_Issued'Size / System.Storage_Unit - 1), Raw.Canonical_Issued)
        and then Source_Padding_Valid (Data (Data'First + Raw.Canonical_Recovered'Position .. Data'First + Raw.Canonical_Recovered'Position + Raw.Canonical_Recovered'Size / System.Storage_Unit - 1), Raw.Canonical_Recovered)
        and then Source_Padding_Valid (Data (Data'First + Raw.Worker_Native'Position .. Data'First + Raw.Worker_Native'Position + Raw.Worker_Native'Size / System.Storage_Unit - 1), Raw.Worker_Native)
        and then Source_Padding_Valid (Data (Data'First + Raw.Canonical_Native'Position .. Data'First + Raw.Canonical_Native'Position + Raw.Canonical_Native'Size / System.Storage_Unit - 1), Raw.Canonical_Native)
        and then Source_Padding_Valid (Data (Data'First + Raw.Worker_Receipt_Genesis'Position .. Data'First + Raw.Worker_Receipt_Genesis'Position + Raw.Worker_Receipt_Genesis'Size / System.Storage_Unit - 1), Raw.Worker_Receipt_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner_Receipt_Genesis'Position .. Data'First + Raw.Owner_Receipt_Genesis'Position + Raw.Owner_Receipt_Genesis'Size / System.Storage_Unit - 1), Raw.Owner_Receipt_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Worker_Receipt_Head'Position .. Data'First + Raw.Worker_Receipt_Head'Position + Raw.Worker_Receipt_Head'Size / System.Storage_Unit - 1), Raw.Worker_Receipt_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Worker_Causal_Genesis'Position .. Data'First + Raw.Worker_Causal_Genesis'Position + Raw.Worker_Causal_Genesis'Size / System.Storage_Unit - 1), Raw.Worker_Causal_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner_Causal_Genesis'Position .. Data'First + Raw.Owner_Causal_Genesis'Position + Raw.Owner_Causal_Genesis'Size / System.Storage_Unit - 1), Raw.Owner_Causal_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Worker_Causal_Head'Position .. Data'First + Raw.Worker_Causal_Head'Position + Raw.Worker_Causal_Head'Size / System.Storage_Unit - 1), Raw.Worker_Causal_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Quarantine_Head'Position .. Data'First + Raw.Quarantine_Head'Position + Raw.Quarantine_Head'Size / System.Storage_Unit - 1), Raw.Quarantine_Head);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : HC.Raw_Result) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Disposition'Position and then Offset - Raw.Disposition'Position < Raw.Disposition'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CX.Raw_Result) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not ((Offset >= Raw.Disposition'Position and then Offset - Raw.Disposition'Position < Raw.Disposition'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return True;
   end Source_Padding_Valid;
end Worldline.Retained_Raw_Decode;
