package body Worldline.Retained_Raw_Decode with SPARK_Mode is
   use type Interfaces.Unsigned_64;
   use type Interfaces.Integer_64;
   use type Q.Byte;
   function Little_Endian (Data : Q.Byte_Array) return Interfaces.Unsigned_64
     with Global => null,
       Pre => Data'Length <= Interfaces.Unsigned_64'Size / System.Storage_Unit,
       Post => (Data'Length = Interfaces.Unsigned_64'Size / System.Storage_Unit
         or else Little_Endian'Result < 2 ** (Natural (Data'Length) * System.Storage_Unit))
   is
      Result : Interfaces.Unsigned_64 := 0;
   begin
      for I in reverse 0 .. Interfaces.Unsigned_64'Size / System.Storage_Unit - 1 loop
         if I < Data'Length then
            Result := Interfaces.Shift_Left (Result, System.Storage_Unit)
              or Interfaces.Unsigned_64 (Data (Data'First + Q.Byte_Count (I)));
         end if;
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
   --  One total predicate for every field; retain the original comparison
   --  as its contract so callers keep the exact padding semantics.
   function In_Field (Offset, Position, Width : Q.Byte_Count) return Boolean
     with Global => null,
       Post => In_Field'Result =
         (Offset >= Position and then Offset - Position < Width)
   is
   begin
      if Offset < Position then
         return False;
      end if;
      return Offset - Position < Width;
   end In_Field;
   function Load (Data : Q.Byte_Array) return D.Raw_Packet is
      Layout : D.Raw_Packet;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Ledger => Load (Data (Data'First + Layout.Ledger'Position .. Data'First + (Layout.Ledger'Position + Layout.Ledger'Size / System.Storage_Unit - 1))),
         Captured => Load (Data (Data'First + Layout.Captured'Position .. Data'First + (Layout.Captured'Position + Layout.Captured'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Packet is
      Layout : N.Raw_Packet;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Schema_Version => Interfaces.Unsigned_32 (Little_Endian (Data (Data'First + Layout.Schema_Version'Position .. Data'First + (Layout.Schema_Version'Position + Layout.Schema_Version'Size / System.Storage_Unit - 1)))),
         Before_State => Load (Data (Data'First + Layout.Before_State'Position .. Data'First + (Layout.Before_State'Position + Layout.Before_State'Size / System.Storage_Unit - 1))),
         Proposed_State => Load (Data (Data'First + Layout.Proposed_State'Position .. Data'First + (Layout.Proposed_State'Position + Layout.Proposed_State'Size / System.Storage_Unit - 1))),
         Current => Load (Data (Data'First + Layout.Current'Position .. Data'First + (Layout.Current'Position + Layout.Current'Size / System.Storage_Unit - 1))),
         Request => Load (Data (Data'First + Layout.Request'Position .. Data'First + (Layout.Request'Position + Layout.Request'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_State is
      Layout : N.Raw_State;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Current => Load (Data (Data'First + Layout.Current'Position .. Data'First + (Layout.Current'Position + Layout.Current'Size / System.Storage_Unit - 1))),
         Resource_Epoch => Load (Data (Data'First + Layout.Resource_Epoch'Position .. Data'First + (Layout.Resource_Epoch'Position + Layout.Resource_Epoch'Size / System.Storage_Unit - 1))),
         Universe_Head => Load (Data (Data'First + Layout.Universe_Head'Position .. Data'First + (Layout.Universe_Head'Position + Layout.Universe_Head'Size / System.Storage_Unit - 1))),
         Ledger_Head => Load (Data (Data'First + Layout.Ledger_Head'Position .. Data'First + (Layout.Ledger_Head'Position + Layout.Ledger_Head'Size / System.Storage_Unit - 1))),
         History_Head => Load (Data (Data'First + Layout.History_Head'Position .. Data'First + (Layout.History_Head'Position + Layout.History_Head'Size / System.Storage_Unit - 1))),
         Physical_Head => Load (Data (Data'First + Layout.Physical_Head'Position .. Data'First + (Layout.Physical_Head'Position + Layout.Physical_Head'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Context is
      Layout : W.Raw_Context;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Universe => Load (Data (Data'First + Layout.Universe'Position .. Data'First + (Layout.Universe'Position + Layout.Universe'Size / System.Storage_Unit - 1))),
         Policy => Load (Data (Data'First + Layout.Policy'Position .. Data'First + (Layout.Policy'Position + Layout.Policy'Size / System.Storage_Unit - 1))),
         Resource => Load (Data (Data'First + Layout.Resource'Position .. Data'First + (Layout.Resource'Position + Layout.Resource'Size / System.Storage_Unit - 1))),
         Unit => Load (Data (Data'First + Layout.Unit'Position .. Data'First + (Layout.Unit'Position + Layout.Unit'Size / System.Storage_Unit - 1))),
         Instance => Load (Data (Data'First + Layout.Instance'Position .. Data'First + (Layout.Instance'Position + Layout.Instance'Size / System.Storage_Unit - 1))),
         Host => Load (Data (Data'First + Layout.Host'Position .. Data'First + (Layout.Host'Position + Layout.Host'Size / System.Storage_Unit - 1))),
         Boot => Load (Data (Data'First + Layout.Boot'Position .. Data'First + (Layout.Boot'Position + Layout.Boot'Size / System.Storage_Unit - 1))),
         Authority => Load (Data (Data'First + Layout.Authority'Position .. Data'First + (Layout.Authority'Position + Layout.Authority'Size / System.Storage_Unit - 1))),
         Policy_Epoch => Load (Data (Data'First + Layout.Policy_Epoch'Position .. Data'First + (Layout.Policy_Epoch'Position + Layout.Policy_Epoch'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Id is
      Layout : W.Raw_Id;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Present'Position .. Data'First + (Layout.Present'Position + Layout.Present'Size / System.Storage_Unit - 1)))),
         First => Signed (Data (Data'First + Layout.First'Position .. Data'First + (Layout.First'Position + Layout.First'Size / System.Storage_Unit - 1))),
         Length => Signed (Data (Data'First + Layout.Length'Position .. Data'First + (Layout.Length'Position + Layout.Length'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Epoch is
      Layout : W.Raw_Epoch;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Present'Position .. Data'First + (Layout.Present'Position + Layout.Present'Size / System.Storage_Unit - 1)))),
         Value => Load (Data (Data'First + Layout.Value'Position .. Data'First + (Layout.Value'Position + Layout.Value'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Quantity is
      Layout : W.Raw_Quantity;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Negative => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Negative'Position .. Data'First + (Layout.Negative'Position + Layout.Negative'Size / System.Storage_Unit - 1)))),
         First => Signed (Data (Data'First + Layout.First'Position .. Data'First + (Layout.First'Position + Layout.First'Size / System.Storage_Unit - 1))),
         Length => Signed (Data (Data'First + Layout.Length'Position .. Data'First + (Layout.Length'Position + Layout.Length'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Current_Observation is
      Layout : N.Raw_Current_Observation;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Scope => Load (Data (Data'First + Layout.Scope'Position .. Data'First + (Layout.Scope'Position + Layout.Scope'Size / System.Storage_Unit - 1))),
         Resource_Epoch => Load (Data (Data'First + Layout.Resource_Epoch'Position .. Data'First + (Layout.Resource_Epoch'Position + Layout.Resource_Epoch'Size / System.Storage_Unit - 1))),
         Universe_Head => Load (Data (Data'First + Layout.Universe_Head'Position .. Data'First + (Layout.Universe_Head'Position + Layout.Universe_Head'Size / System.Storage_Unit - 1))),
         Ledger_Head => Load (Data (Data'First + Layout.Ledger_Head'Position .. Data'First + (Layout.Ledger_Head'Position + Layout.Ledger_Head'Size / System.Storage_Unit - 1))),
         History_Head => Load (Data (Data'First + Layout.History_Head'Position .. Data'First + (Layout.History_Head'Position + Layout.History_Head'Size / System.Storage_Unit - 1))),
         Physical_Head => Load (Data (Data'First + Layout.Physical_Head'Position .. Data'First + (Layout.Physical_Head'Position + Layout.Physical_Head'Size / System.Storage_Unit - 1))),
         Store_Genesis => Load (Data (Data'First + Layout.Store_Genesis'Position .. Data'First + (Layout.Store_Genesis'Position + Layout.Store_Genesis'Size / System.Storage_Unit - 1))),
         Store_Id => Load (Data (Data'First + Layout.Store_Id'Position .. Data'First + (Layout.Store_Id'Position + Layout.Store_Id'Size / System.Storage_Unit - 1))),
         Root_Head => Load (Data (Data'First + Layout.Root_Head'Position .. Data'First + (Layout.Root_Head'Position + Layout.Root_Head'Size / System.Storage_Unit - 1))),
         Prime => Load (Data (Data'First + Layout.Prime'Position .. Data'First + (Layout.Prime'Position + Layout.Prime'Size / System.Storage_Unit - 1))),
         Root_Count => Load (Data (Data'First + Layout.Root_Count'Position .. Data'First + (Layout.Root_Count'Position + Layout.Root_Count'Size / System.Storage_Unit - 1))),
         Cause => Load (Data (Data'First + Layout.Cause'Position .. Data'First + (Layout.Cause'Position + Layout.Cause'Size / System.Storage_Unit - 1))),
         Requester => Load (Data (Data'First + Layout.Requester'Position .. Data'First + (Layout.Requester'Position + Layout.Requester'Size / System.Storage_Unit - 1))),
         Receipt => Load (Data (Data'First + Layout.Receipt'Position .. Data'First + (Layout.Receipt'Position + Layout.Receipt'Size / System.Storage_Unit - 1))),
         Catalogue_Head => Load (Data (Data'First + Layout.Catalogue_Head'Position .. Data'First + (Layout.Catalogue_Head'Position + Layout.Catalogue_Head'Size / System.Storage_Unit - 1))),
         Observation_Head => Load (Data (Data'First + Layout.Observation_Head'Position .. Data'First + (Layout.Observation_Head'Position + Layout.Observation_Head'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Intent is
      Layout : N.Raw_Intent;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Kind => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Kind'Position .. Data'First + (Layout.Kind'Position + Layout.Kind'Size / System.Storage_Unit - 1)))),
         Original => Load (Data (Data'First + Layout.Original'Position .. Data'First + (Layout.Original'Position + Layout.Original'Size / System.Storage_Unit - 1))),
         Expected_Epoch => Load (Data (Data'First + Layout.Expected_Epoch'Position .. Data'First + (Layout.Expected_Epoch'Position + Layout.Expected_Epoch'Size / System.Storage_Unit - 1))),
         Expected_Ledger_Head => Load (Data (Data'First + Layout.Expected_Ledger_Head'Position .. Data'First + (Layout.Expected_Ledger_Head'Position + Layout.Expected_Ledger_Head'Size / System.Storage_Unit - 1))),
         Request_Id => Load (Data (Data'First + Layout.Request_Id'Position .. Data'First + (Layout.Request_Id'Position + Layout.Request_Id'Size / System.Storage_Unit - 1))),
         Cause => Load (Data (Data'First + Layout.Cause'Position .. Data'First + (Layout.Cause'Position + Layout.Cause'Size / System.Storage_Unit - 1))),
         Requester => Load (Data (Data'First + Layout.Requester'Position .. Data'First + (Layout.Requester'Position + Layout.Requester'Size / System.Storage_Unit - 1))),
         Receipt => Load (Data (Data'First + Layout.Receipt'Position .. Data'First + (Layout.Receipt'Position + Layout.Receipt'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Request is
      Layout : W.Raw_Request;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Kind => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Kind'Position .. Data'First + (Layout.Kind'Position + Layout.Kind'Size / System.Storage_Unit - 1)))),
         Scope => Load (Data (Data'First + Layout.Scope'Position .. Data'First + (Layout.Scope'Position + Layout.Scope'Size / System.Storage_Unit - 1))),
         Expected_Epoch => Load (Data (Data'First + Layout.Expected_Epoch'Position .. Data'First + (Layout.Expected_Epoch'Position + Layout.Expected_Epoch'Size / System.Storage_Unit - 1))),
         Expected_Ledger_Head => Load (Data (Data'First + Layout.Expected_Ledger_Head'Position .. Data'First + (Layout.Expected_Ledger_Head'Position + Layout.Expected_Ledger_Head'Size / System.Storage_Unit - 1))),
         Request_Id => Load (Data (Data'First + Layout.Request_Id'Position .. Data'First + (Layout.Request_Id'Position + Layout.Request_Id'Size / System.Storage_Unit - 1))),
         Reservation => Load (Data (Data'First + Layout.Reservation'Position .. Data'First + (Layout.Reservation'Position + Layout.Reservation'Size / System.Storage_Unit - 1))),
         Operation_Id => Load (Data (Data'First + Layout.Operation_Id'Position .. Data'First + (Layout.Operation_Id'Position + Layout.Operation_Id'Size / System.Storage_Unit - 1))),
         Requester => Load (Data (Data'First + Layout.Requester'Position .. Data'First + (Layout.Requester'Position + Layout.Requester'Size / System.Storage_Unit - 1))),
         Bound => Load (Data (Data'First + Layout.Bound'Position .. Data'First + (Layout.Bound'Position + Layout.Bound'Size / System.Storage_Unit - 1))),
         New_Row => Load (Data (Data'First + Layout.New_Row'Position .. Data'First + (Layout.New_Row'Position + Layout.New_Row'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Binding is
      Layout : W.Raw_Binding;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Reservation => Load (Data (Data'First + Layout.Reservation'Position .. Data'First + (Layout.Reservation'Position + Layout.Reservation'Size / System.Storage_Unit - 1))),
         Operation => Load (Data (Data'First + Layout.Operation'Position .. Data'First + (Layout.Operation'Position + Layout.Operation'Size / System.Storage_Unit - 1))),
         Owner => Load (Data (Data'First + Layout.Owner'Position .. Data'First + (Layout.Owner'Position + Layout.Owner'Size / System.Storage_Unit - 1))),
         Workload => Load (Data (Data'First + Layout.Workload'Position .. Data'First + (Layout.Workload'Position + Layout.Workload'Size / System.Storage_Unit - 1))),
         Universe_Head => Load (Data (Data'First + Layout.Universe_Head'Position .. Data'First + (Layout.Universe_Head'Position + Layout.Universe_Head'Size / System.Storage_Unit - 1))),
         Capability => Load (Data (Data'First + Layout.Capability'Position .. Data'First + (Layout.Capability'Position + Layout.Capability'Size / System.Storage_Unit - 1))),
         Grant_Use => Load (Data (Data'First + Layout.Grant_Use'Position .. Data'First + (Layout.Grant_Use'Position + Layout.Grant_Use'Size / System.Storage_Unit - 1))),
         Payload => Load (Data (Data'First + Layout.Payload'Position .. Data'First + (Layout.Payload'Position + Layout.Payload'Size / System.Storage_Unit - 1))),
         Provenance => Load (Data (Data'First + Layout.Provenance'Position .. Data'First + (Layout.Provenance'Position + Layout.Provenance'Size / System.Storage_Unit - 1))),
         Resource_Epoch => Load (Data (Data'First + Layout.Resource_Epoch'Position .. Data'First + (Layout.Resource_Epoch'Position + Layout.Resource_Epoch'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Row is
      Layout : W.Raw_Row;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Scope => Load (Data (Data'First + Layout.Scope'Position .. Data'First + (Layout.Scope'Position + Layout.Scope'Size / System.Storage_Unit - 1))),
         Bound => Load (Data (Data'First + Layout.Bound'Position .. Data'First + (Layout.Bound'Position + Layout.Bound'Size / System.Storage_Unit - 1))),
         Parent => Load (Data (Data'First + Layout.Parent'Position .. Data'First + (Layout.Parent'Position + Layout.Parent'Size / System.Storage_Unit - 1))),
         Kind => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Kind'Position .. Data'First + (Layout.Kind'Position + Layout.Kind'Size / System.Storage_Unit - 1)))),
         State => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.State'Position .. Data'First + (Layout.State'Position + Layout.State'Size / System.Storage_Unit - 1)))),
         Amount => Load (Data (Data'First + Layout.Amount'Position .. Data'First + (Layout.Amount'Position + Layout.Amount'Size / System.Storage_Unit - 1))),
         Observed_Usage => Load (Data (Data'First + Layout.Observed_Usage'Position .. Data'First + (Layout.Observed_Usage'Position + Layout.Observed_Usage'Size / System.Storage_Unit - 1))),
         Planned_Unit => Load (Data (Data'First + Layout.Planned_Unit'Position .. Data'First + (Layout.Planned_Unit'Position + Layout.Planned_Unit'Size / System.Storage_Unit - 1))),
         Actual_Unit => Load (Data (Data'First + Layout.Actual_Unit'Position .. Data'First + (Layout.Actual_Unit'Position + Layout.Actual_Unit'Size / System.Storage_Unit - 1))),
         Cgroup => Load (Data (Data'First + Layout.Cgroup'Position .. Data'First + (Layout.Cgroup'Position + Layout.Cgroup'Size / System.Storage_Unit - 1))),
         Invocation => Load (Data (Data'First + Layout.Invocation'Position .. Data'First + (Layout.Invocation'Position + Layout.Invocation'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return D.Raw_Observation is
      Layout : D.Raw_Observation;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Bound => Load (Data (Data'First + Layout.Bound'Position .. Data'First + (Layout.Bound'Position + Layout.Bound'Size / System.Storage_Unit - 1))),
         Raw_Frame => Load (Data (Data'First + Layout.Raw_Frame'Position .. Data'First + (Layout.Raw_Frame'Position + Layout.Raw_Frame'Size / System.Storage_Unit - 1))),
         Raw_Sender => Load (Data (Data'First + Layout.Raw_Sender'Position .. Data'First + (Layout.Raw_Sender'Position + Layout.Raw_Sender'Size / System.Storage_Unit - 1))),
         Ticket => Load (Data (Data'First + Layout.Ticket'Position .. Data'First + (Layout.Ticket'Position + Layout.Ticket'Size / System.Storage_Unit - 1))),
         Raw_Proc_Status => Load (Data (Data'First + Layout.Raw_Proc_Status'Position .. Data'First + (Layout.Raw_Proc_Status'Position + Layout.Raw_Proc_Status'Size / System.Storage_Unit - 1))),
         Raw_Proc_Cgroup => Load (Data (Data'First + Layout.Raw_Proc_Cgroup'Position .. Data'First + (Layout.Raw_Proc_Cgroup'Position + Layout.Raw_Proc_Cgroup'Size / System.Storage_Unit - 1))),
         Raw_Proc_Maps => Load (Data (Data'First + Layout.Raw_Proc_Maps'Position .. Data'First + (Layout.Raw_Proc_Maps'Position + Layout.Raw_Proc_Maps'Size / System.Storage_Unit - 1))),
         Raw_Proc_Cmdline => Load (Data (Data'First + Layout.Raw_Proc_Cmdline'Position .. Data'First + (Layout.Raw_Proc_Cmdline'Position + Layout.Raw_Proc_Cmdline'Size / System.Storage_Unit - 1))),
         Raw_Pidfd_Info => Load (Data (Data'First + Layout.Raw_Pidfd_Info'Position .. Data'First + (Layout.Raw_Pidfd_Info'Position + Layout.Raw_Pidfd_Info'Size / System.Storage_Unit - 1))),
         Namespace => Load (Data (Data'First + Layout.Namespace'Position .. Data'First + (Layout.Namespace'Position + Layout.Namespace'Size / System.Storage_Unit - 1))),
         Held_Namespace => Load (Data (Data'First + Layout.Held_Namespace'Position .. Data'First + (Layout.Held_Namespace'Position + Layout.Held_Namespace'Size / System.Storage_Unit - 1))),
         Helper_Image => Load (Data (Data'First + Layout.Helper_Image'Position .. Data'First + (Layout.Helper_Image'Position + Layout.Helper_Image'Size / System.Storage_Unit - 1))),
         Expected_Helper_Image => Load (Data (Data'First + Layout.Expected_Helper_Image'Position .. Data'First + (Layout.Expected_Helper_Image'Position + Layout.Expected_Helper_Image'Size / System.Storage_Unit - 1))),
         Executable_Plan => Load (Data (Data'First + Layout.Executable_Plan'Position .. Data'First + (Layout.Executable_Plan'Position + Layout.Executable_Plan'Size / System.Storage_Unit - 1))),
         Expected_Executable_Plan => Load (Data (Data'First + Layout.Expected_Executable_Plan'Position .. Data'First + (Layout.Expected_Executable_Plan'Position + Layout.Expected_Executable_Plan'Size / System.Storage_Unit - 1))),
         Original_Requester => Load (Data (Data'First + Layout.Original_Requester'Position .. Data'First + (Layout.Original_Requester'Position + Layout.Original_Requester'Size / System.Storage_Unit - 1))),
         Requester_Credentials => Load (Data (Data'First + Layout.Requester_Credentials'Position .. Data'First + (Layout.Requester_Credentials'Position + Layout.Requester_Credentials'Size / System.Storage_Unit - 1))),
         Expected_Requester_Credentials => Load (Data (Data'First + Layout.Expected_Requester_Credentials'Position .. Data'First + (Layout.Expected_Requester_Credentials'Position + Layout.Expected_Requester_Credentials'Size / System.Storage_Unit - 1))),
         Dispatch => Load (Data (Data'First + Layout.Dispatch'Position .. Data'First + (Layout.Dispatch'Position + Layout.Dispatch'Size / System.Storage_Unit - 1))),
         Running_Event => Load (Data (Data'First + Layout.Running_Event'Position .. Data'First + (Layout.Running_Event'Position + Layout.Running_Event'Size / System.Storage_Unit - 1))),
         Expected_Running_Event => Load (Data (Data'First + Layout.Expected_Running_Event'Position .. Data'First + (Layout.Expected_Running_Event'Position + Layout.Expected_Running_Event'Size / System.Storage_Unit - 1))),
         Canonical_Use_Event => Load (Data (Data'First + Layout.Canonical_Use_Event'Position .. Data'First + (Layout.Canonical_Use_Event'Position + Layout.Canonical_Use_Event'Size / System.Storage_Unit - 1))),
         Expected_Canonical_Use_Event => Load (Data (Data'First + Layout.Expected_Canonical_Use_Event'Position .. Data'First + (Layout.Expected_Canonical_Use_Event'Position + Layout.Expected_Canonical_Use_Event'Size / System.Storage_Unit - 1))),
         Store_Genesis => Load (Data (Data'First + Layout.Store_Genesis'Position .. Data'First + (Layout.Store_Genesis'Position + Layout.Store_Genesis'Size / System.Storage_Unit - 1))),
         Expected_Store_Genesis => Load (Data (Data'First + Layout.Expected_Store_Genesis'Position .. Data'First + (Layout.Expected_Store_Genesis'Position + Layout.Expected_Store_Genesis'Size / System.Storage_Unit - 1))),
         Source_Lease => Load (Data (Data'First + Layout.Source_Lease'Position .. Data'First + (Layout.Source_Lease'Position + Layout.Source_Lease'Size / System.Storage_Unit - 1))),
         Expected_Source_Lease => Load (Data (Data'First + Layout.Expected_Source_Lease'Position .. Data'First + (Layout.Expected_Source_Lease'Position + Layout.Expected_Source_Lease'Size / System.Storage_Unit - 1))),
         Actor_Wait => Load (Data (Data'First + Layout.Actor_Wait'Position .. Data'First + (Layout.Actor_Wait'Position + Layout.Actor_Wait'Size / System.Storage_Unit - 1))),
         Helper_Wait => Load (Data (Data'First + Layout.Helper_Wait'Position .. Data'First + (Layout.Helper_Wait'Position + Layout.Helper_Wait'Size / System.Storage_Unit - 1))),
         Namespace_Wait => Load (Data (Data'First + Layout.Namespace_Wait'Position .. Data'First + (Layout.Namespace_Wait'Position + Layout.Namespace_Wait'Size / System.Storage_Unit - 1))),
         Host_Pid => Load (Data (Data'First + Layout.Host_Pid'Position .. Data'First + (Layout.Host_Pid'Position + Layout.Host_Pid'Size / System.Storage_Unit - 1))),
         Namespace_Pid => Load (Data (Data'First + Layout.Namespace_Pid'Position .. Data'First + (Layout.Namespace_Pid'Position + Layout.Namespace_Pid'Size / System.Storage_Unit - 1))),
         Sender_Uid => Load (Data (Data'First + Layout.Sender_Uid'Position .. Data'First + (Layout.Sender_Uid'Position + Layout.Sender_Uid'Size / System.Storage_Unit - 1))),
         Sender_Gid => Load (Data (Data'First + Layout.Sender_Gid'Position .. Data'First + (Layout.Sender_Gid'Position + Layout.Sender_Gid'Size / System.Storage_Unit - 1))),
         Real_Uid => Load (Data (Data'First + Layout.Real_Uid'Position .. Data'First + (Layout.Real_Uid'Position + Layout.Real_Uid'Size / System.Storage_Unit - 1))),
         Effective_Uid => Load (Data (Data'First + Layout.Effective_Uid'Position .. Data'First + (Layout.Effective_Uid'Position + Layout.Effective_Uid'Size / System.Storage_Unit - 1))),
         Saved_Uid => Load (Data (Data'First + Layout.Saved_Uid'Position .. Data'First + (Layout.Saved_Uid'Position + Layout.Saved_Uid'Size / System.Storage_Unit - 1))),
         Real_Gid => Load (Data (Data'First + Layout.Real_Gid'Position .. Data'First + (Layout.Real_Gid'Position + Layout.Real_Gid'Size / System.Storage_Unit - 1))),
         Effective_Gid => Load (Data (Data'First + Layout.Effective_Gid'Position .. Data'First + (Layout.Effective_Gid'Position + Layout.Effective_Gid'Size / System.Storage_Unit - 1))),
         Saved_Gid => Load (Data (Data'First + Layout.Saved_Gid'Position .. Data'First + (Layout.Saved_Gid'Position + Layout.Saved_Gid'Size / System.Storage_Unit - 1))),
         Capability_Version => Load (Data (Data'First + Layout.Capability_Version'Position .. Data'First + (Layout.Capability_Version'Position + Layout.Capability_Version'Size / System.Storage_Unit - 1))),
         Effective_Low => Load (Data (Data'First + Layout.Effective_Low'Position .. Data'First + (Layout.Effective_Low'Position + Layout.Effective_Low'Size / System.Storage_Unit - 1))),
         Permitted_Low => Load (Data (Data'First + Layout.Permitted_Low'Position .. Data'First + (Layout.Permitted_Low'Position + Layout.Permitted_Low'Size / System.Storage_Unit - 1))),
         Inheritable_Low => Load (Data (Data'First + Layout.Inheritable_Low'Position .. Data'First + (Layout.Inheritable_Low'Position + Layout.Inheritable_Low'Size / System.Storage_Unit - 1))),
         Effective_High => Load (Data (Data'First + Layout.Effective_High'Position .. Data'First + (Layout.Effective_High'Position + Layout.Effective_High'Size / System.Storage_Unit - 1))),
         Permitted_High => Load (Data (Data'First + Layout.Permitted_High'Position .. Data'First + (Layout.Permitted_High'Position + Layout.Permitted_High'Size / System.Storage_Unit - 1))),
         Inheritable_High => Load (Data (Data'First + Layout.Inheritable_High'Position .. Data'First + (Layout.Inheritable_High'Position + Layout.Inheritable_High'Size / System.Storage_Unit - 1))),
         Securebits => Load (Data (Data'First + Layout.Securebits'Position .. Data'First + (Layout.Securebits'Position + Layout.Securebits'Size / System.Storage_Unit - 1))),
         No_New_Privs => Load (Data (Data'First + Layout.No_New_Privs'Position .. Data'First + (Layout.No_New_Privs'Position + Layout.No_New_Privs'Size / System.Storage_Unit - 1))),
         Requester_Uid => Load (Data (Data'First + Layout.Requester_Uid'Position .. Data'First + (Layout.Requester_Uid'Position + Layout.Requester_Uid'Size / System.Storage_Unit - 1))),
         Requester_Gid => Load (Data (Data'First + Layout.Requester_Gid'Position .. Data'First + (Layout.Requester_Gid'Position + Layout.Requester_Gid'Size / System.Storage_Unit - 1))),
         Configured_Requester_Uid => Load (Data (Data'First + Layout.Configured_Requester_Uid'Position .. Data'First + (Layout.Configured_Requester_Uid'Position + Layout.Configured_Requester_Uid'Size / System.Storage_Unit - 1))),
         Workload_Uid => Load (Data (Data'First + Layout.Workload_Uid'Position .. Data'First + (Layout.Workload_Uid'Position + Layout.Workload_Uid'Size / System.Storage_Unit - 1))),
         Workload_Gid => Load (Data (Data'First + Layout.Workload_Gid'Position .. Data'First + (Layout.Workload_Gid'Position + Layout.Workload_Gid'Size / System.Storage_Unit - 1))),
         Proc_Host_Pid => Load (Data (Data'First + Layout.Proc_Host_Pid'Position .. Data'First + (Layout.Proc_Host_Pid'Position + Layout.Proc_Host_Pid'Size / System.Storage_Unit - 1))),
         Proc_Namespace_Pid => Load (Data (Data'First + Layout.Proc_Namespace_Pid'Position .. Data'First + (Layout.Proc_Namespace_Pid'Position + Layout.Proc_Namespace_Pid'Size / System.Storage_Unit - 1))),
         Proc_Real_Uid => Load (Data (Data'First + Layout.Proc_Real_Uid'Position .. Data'First + (Layout.Proc_Real_Uid'Position + Layout.Proc_Real_Uid'Size / System.Storage_Unit - 1))),
         Proc_Effective_Uid => Load (Data (Data'First + Layout.Proc_Effective_Uid'Position .. Data'First + (Layout.Proc_Effective_Uid'Position + Layout.Proc_Effective_Uid'Size / System.Storage_Unit - 1))),
         Proc_Saved_Uid => Load (Data (Data'First + Layout.Proc_Saved_Uid'Position .. Data'First + (Layout.Proc_Saved_Uid'Position + Layout.Proc_Saved_Uid'Size / System.Storage_Unit - 1))),
         Proc_Real_Gid => Load (Data (Data'First + Layout.Proc_Real_Gid'Position .. Data'First + (Layout.Proc_Real_Gid'Position + Layout.Proc_Real_Gid'Size / System.Storage_Unit - 1))),
         Proc_Effective_Gid => Load (Data (Data'First + Layout.Proc_Effective_Gid'Position .. Data'First + (Layout.Proc_Effective_Gid'Position + Layout.Proc_Effective_Gid'Size / System.Storage_Unit - 1))),
         Proc_Saved_Gid => Load (Data (Data'First + Layout.Proc_Saved_Gid'Position .. Data'First + (Layout.Proc_Saved_Gid'Position + Layout.Proc_Saved_Gid'Size / System.Storage_Unit - 1))),
         Proc_Effective => Load (Data (Data'First + Layout.Proc_Effective'Position .. Data'First + (Layout.Proc_Effective'Position + Layout.Proc_Effective'Size / System.Storage_Unit - 1))),
         Proc_Permitted => Load (Data (Data'First + Layout.Proc_Permitted'Position .. Data'First + (Layout.Proc_Permitted'Position + Layout.Proc_Permitted'Size / System.Storage_Unit - 1))),
         Proc_Inheritable => Load (Data (Data'First + Layout.Proc_Inheritable'Position .. Data'First + (Layout.Proc_Inheritable'Position + Layout.Proc_Inheritable'Size / System.Storage_Unit - 1))),
         Proc_Bounding => Load (Data (Data'First + Layout.Proc_Bounding'Position .. Data'First + (Layout.Proc_Bounding'Position + Layout.Proc_Bounding'Size / System.Storage_Unit - 1))),
         Proc_Ambient => Load (Data (Data'First + Layout.Proc_Ambient'Position .. Data'First + (Layout.Proc_Ambient'Position + Layout.Proc_Ambient'Size / System.Storage_Unit - 1))),
         Proc_No_New_Privs => Load (Data (Data'First + Layout.Proc_No_New_Privs'Position .. Data'First + (Layout.Proc_No_New_Privs'Position + Layout.Proc_No_New_Privs'Size / System.Storage_Unit - 1))),
         Proc_Fs_Uid => Load (Data (Data'First + Layout.Proc_Fs_Uid'Position .. Data'First + (Layout.Proc_Fs_Uid'Position + Layout.Proc_Fs_Uid'Size / System.Storage_Unit - 1))),
         Proc_Fs_Gid => Load (Data (Data'First + Layout.Proc_Fs_Gid'Position .. Data'First + (Layout.Proc_Fs_Gid'Position + Layout.Proc_Fs_Gid'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return X.Raw_Crosswalk is
      Layout : X.Raw_Crosswalk;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Resource_Current => Load (Data (Data'First + Layout.Resource_Current'Position .. Data'First + (Layout.Resource_Current'Position + Layout.Resource_Current'Size / System.Storage_Unit - 1))),
         Operation_Policy => Load (Data (Data'First + Layout.Operation_Policy'Position .. Data'First + (Layout.Operation_Policy'Position + Layout.Operation_Policy'Size / System.Storage_Unit - 1))),
         Operation_Root_Set => Load (Data (Data'First + Layout.Operation_Root_Set'Position .. Data'First + (Layout.Operation_Root_Set'Position + Layout.Operation_Root_Set'Size / System.Storage_Unit - 1))),
         Owner_Genesis => Load (Data (Data'First + Layout.Owner_Genesis'Position .. Data'First + (Layout.Owner_Genesis'Position + Layout.Owner_Genesis'Size / System.Storage_Unit - 1))),
         Installation => Load (Data (Data'First + Layout.Installation'Position .. Data'First + (Layout.Installation'Position + Layout.Installation'Size / System.Storage_Unit - 1))),
         Gate_Config => Load (Data (Data'First + Layout.Gate_Config'Position .. Data'First + (Layout.Gate_Config'Position + Layout.Gate_Config'Size / System.Storage_Unit - 1))),
         Managed_Observation => Load (Data (Data'First + Layout.Managed_Observation'Position .. Data'First + (Layout.Managed_Observation'Position + Layout.Managed_Observation'Size / System.Storage_Unit - 1))),
         Original_Grant => Load (Data (Data'First + Layout.Original_Grant'Position .. Data'First + (Layout.Original_Grant'Position + Layout.Original_Grant'Size / System.Storage_Unit - 1))),
         Complete_Crosswalk => Load (Data (Data'First + Layout.Complete_Crosswalk'Position .. Data'First + (Layout.Complete_Crosswalk'Position + Layout.Complete_Crosswalk'Size / System.Storage_Unit - 1))),
         Current_Source => Load (Data (Data'First + Layout.Current_Source'Position .. Data'First + (Layout.Current_Source'Position + Layout.Current_Source'Size / System.Storage_Unit - 1))),
         Original_Request => Load (Data (Data'First + Layout.Original_Request'Position .. Data'First + (Layout.Original_Request'Position + Layout.Original_Request'Size / System.Storage_Unit - 1))),
         Original_Requester => Load (Data (Data'First + Layout.Original_Requester'Position .. Data'First + (Layout.Original_Requester'Position + Layout.Original_Requester'Size / System.Storage_Unit - 1))),
         Original_Transaction => Load (Data (Data'First + Layout.Original_Transaction'Position .. Data'First + (Layout.Original_Transaction'Position + Layout.Original_Transaction'Size / System.Storage_Unit - 1))),
         Preparer => Load (Data (Data'First + Layout.Preparer'Position .. Data'First + (Layout.Preparer'Position + Layout.Preparer'Size / System.Storage_Unit - 1))),
         Selected_Plan => Load (Data (Data'First + Layout.Selected_Plan'Position .. Data'First + (Layout.Selected_Plan'Position + Layout.Selected_Plan'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return C.Raw_Digest is
      Layout : C.Raw_Digest;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Present'Position .. Data'First + (Layout.Present'Position + Layout.Present'Size / System.Storage_Unit - 1)))),
         Value => Load (Data (Data'First + Layout.Value'Position .. Data'First + (Layout.Value'Position + Layout.Value'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return C.Raw_Hash is
      Result : C.Raw_Hash;
   begin
      for I in Result'Range loop
         Result (I) := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Q.Byte_Count (I - Result'First) * Interfaces.Unsigned_8'Size / System.Storage_Unit .. Data'First + (Q.Byte_Count (I - Result'First) * Interfaces.Unsigned_8'Size / System.Storage_Unit + Interfaces.Unsigned_8'Size / System.Storage_Unit - 1))));
      end loop;
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return Y.Raw_Input is
      Layout : Y.Raw_Input;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Mode => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Mode'Position .. Data'First + (Layout.Mode'Position + Layout.Mode'Size / System.Storage_Unit - 1)))),
         Controller => Load (Data (Data'First + Layout.Controller'Position .. Data'First + (Layout.Controller'Position + Layout.Controller'Size / System.Storage_Unit - 1))),
         Child_Task => Load (Data (Data'First + Layout.Child_Task'Position .. Data'First + (Layout.Child_Task'Position + Layout.Child_Task'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return Y.Raw_Controller is
      Layout : Y.Raw_Controller;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Bound => Load (Data (Data'First + Layout.Bound'Position .. Data'First + (Layout.Bound'Position + Layout.Bound'Size / System.Storage_Unit - 1))),
         Process => Load (Data (Data'First + Layout.Process'Position .. Data'First + (Layout.Process'Position + Layout.Process'Size / System.Storage_Unit - 1))),
         Requester_Uid => Load (Data (Data'First + Layout.Requester_Uid'Position .. Data'First + (Layout.Requester_Uid'Position + Layout.Requester_Uid'Size / System.Storage_Unit - 1))),
         Requester_Gid => Load (Data (Data'First + Layout.Requester_Gid'Position .. Data'First + (Layout.Requester_Gid'Position + Layout.Requester_Gid'Size / System.Storage_Unit - 1))),
         raw_manager => Load (Data (Data'First + Layout.raw_manager'Position .. Data'First + (Layout.raw_manager'Position + Layout.raw_manager'Size / System.Storage_Unit - 1))),
         raw_channel => Load (Data (Data'First + Layout.raw_channel'Position .. Data'First + (Layout.raw_channel'Position + Layout.raw_channel'Size / System.Storage_Unit - 1))),
         owner_endpoint => Load (Data (Data'First + Layout.owner_endpoint'Position .. Data'First + (Layout.owner_endpoint'Position + Layout.owner_endpoint'Size / System.Storage_Unit - 1))),
         expected_owner_endpoint => Load (Data (Data'First + Layout.expected_owner_endpoint'Position .. Data'First + (Layout.expected_owner_endpoint'Position + Layout.expected_owner_endpoint'Size / System.Storage_Unit - 1))),
         source_lease => Load (Data (Data'First + Layout.source_lease'Position .. Data'First + (Layout.source_lease'Position + Layout.source_lease'Size / System.Storage_Unit - 1))),
         expected_source_lease => Load (Data (Data'First + Layout.expected_source_lease'Position .. Data'First + (Layout.expected_source_lease'Position + Layout.expected_source_lease'Size / System.Storage_Unit - 1))),
         worker_image => Load (Data (Data'First + Layout.worker_image'Position .. Data'First + (Layout.worker_image'Position + Layout.worker_image'Size / System.Storage_Unit - 1))),
         expected_worker_image => Load (Data (Data'First + Layout.expected_worker_image'Position .. Data'First + (Layout.expected_worker_image'Position + Layout.expected_worker_image'Size / System.Storage_Unit - 1))),
         handler_plan => Load (Data (Data'First + Layout.handler_plan'Position .. Data'First + (Layout.handler_plan'Position + Layout.handler_plan'Size / System.Storage_Unit - 1))),
         expected_handler_plan => Load (Data (Data'First + Layout.expected_handler_plan'Position .. Data'First + (Layout.expected_handler_plan'Position + Layout.expected_handler_plan'Size / System.Storage_Unit - 1))),
         raw_request => Load (Data (Data'First + Layout.raw_request'Position .. Data'First + (Layout.raw_request'Position + Layout.raw_request'Size / System.Storage_Unit - 1))),
         requester => Load (Data (Data'First + Layout.requester'Position .. Data'First + (Layout.requester'Position + Layout.requester'Size / System.Storage_Unit - 1))),
         dispatch => Load (Data (Data'First + Layout.dispatch'Position .. Data'First + (Layout.dispatch'Position + Layout.dispatch'Size / System.Storage_Unit - 1))),
         running_event => Load (Data (Data'First + Layout.running_event'Position .. Data'First + (Layout.running_event'Position + Layout.running_event'Size / System.Storage_Unit - 1))),
         expected_running_event => Load (Data (Data'First + Layout.expected_running_event'Position .. Data'First + (Layout.expected_running_event'Position + Layout.expected_running_event'Size / System.Storage_Unit - 1))),
         store_genesis => Load (Data (Data'First + Layout.store_genesis'Position .. Data'First + (Layout.store_genesis'Position + Layout.store_genesis'Size / System.Storage_Unit - 1))),
         expected_store_genesis => Load (Data (Data'First + Layout.expected_store_genesis'Position .. Data'First + (Layout.expected_store_genesis'Position + Layout.expected_store_genesis'Size / System.Storage_Unit - 1))),
         current_source => Load (Data (Data'First + Layout.current_source'Position .. Data'First + (Layout.current_source'Position + Layout.current_source'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return Y.Raw_Process is
      Layout : Y.Raw_Process;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (raw_status => Load (Data (Data'First + Layout.raw_status'Position .. Data'First + (Layout.raw_status'Position + Layout.raw_status'Size / System.Storage_Unit - 1))),
         raw_stat => Load (Data (Data'First + Layout.raw_stat'Position .. Data'First + (Layout.raw_stat'Position + Layout.raw_stat'Size / System.Storage_Unit - 1))),
         raw_cgroup => Load (Data (Data'First + Layout.raw_cgroup'Position .. Data'First + (Layout.raw_cgroup'Position + Layout.raw_cgroup'Size / System.Storage_Unit - 1))),
         raw_maps => Load (Data (Data'First + Layout.raw_maps'Position .. Data'First + (Layout.raw_maps'Position + Layout.raw_maps'Size / System.Storage_Unit - 1))),
         raw_cmdline => Load (Data (Data'First + Layout.raw_cmdline'Position .. Data'First + (Layout.raw_cmdline'Position + Layout.raw_cmdline'Size / System.Storage_Unit - 1))),
         raw_pidfd_info => Load (Data (Data'First + Layout.raw_pidfd_info'Position .. Data'First + (Layout.raw_pidfd_info'Position + Layout.raw_pidfd_info'Size / System.Storage_Unit - 1))),
         namespace => Load (Data (Data'First + Layout.namespace'Position .. Data'First + (Layout.namespace'Position + Layout.namespace'Size / System.Storage_Unit - 1))),
         cgroup => Load (Data (Data'First + Layout.cgroup'Position .. Data'First + (Layout.cgroup'Position + Layout.cgroup'Size / System.Storage_Unit - 1))),
         actual_unit => Load (Data (Data'First + Layout.actual_unit'Position .. Data'First + (Layout.actual_unit'Position + Layout.actual_unit'Size / System.Storage_Unit - 1))),
         invocation => Load (Data (Data'First + Layout.invocation'Position .. Data'First + (Layout.invocation'Position + Layout.invocation'Size / System.Storage_Unit - 1))),
         source_lease => Load (Data (Data'First + Layout.source_lease'Position .. Data'First + (Layout.source_lease'Position + Layout.source_lease'Size / System.Storage_Unit - 1))),
         pidfd_wait => Load (Data (Data'First + Layout.pidfd_wait'Position .. Data'First + (Layout.pidfd_wait'Position + Layout.pidfd_wait'Size / System.Storage_Unit - 1))),
         host_pid => Load (Data (Data'First + Layout.host_pid'Position .. Data'First + (Layout.host_pid'Position + Layout.host_pid'Size / System.Storage_Unit - 1))),
         start_tick => Load (Data (Data'First + Layout.start_tick'Position .. Data'First + (Layout.start_tick'Position + Layout.start_tick'Size / System.Storage_Unit - 1))),
         parent_pid => Load (Data (Data'First + Layout.parent_pid'Position .. Data'First + (Layout.parent_pid'Position + Layout.parent_pid'Size / System.Storage_Unit - 1))),
         parent_start_tick => Load (Data (Data'First + Layout.parent_start_tick'Position .. Data'First + (Layout.parent_start_tick'Position + Layout.parent_start_tick'Size / System.Storage_Unit - 1))),
         real_uid => Load (Data (Data'First + Layout.real_uid'Position .. Data'First + (Layout.real_uid'Position + Layout.real_uid'Size / System.Storage_Unit - 1))),
         effective_uid => Load (Data (Data'First + Layout.effective_uid'Position .. Data'First + (Layout.effective_uid'Position + Layout.effective_uid'Size / System.Storage_Unit - 1))),
         saved_uid => Load (Data (Data'First + Layout.saved_uid'Position .. Data'First + (Layout.saved_uid'Position + Layout.saved_uid'Size / System.Storage_Unit - 1))),
         real_gid => Load (Data (Data'First + Layout.real_gid'Position .. Data'First + (Layout.real_gid'Position + Layout.real_gid'Size / System.Storage_Unit - 1))),
         effective_gid => Load (Data (Data'First + Layout.effective_gid'Position .. Data'First + (Layout.effective_gid'Position + Layout.effective_gid'Size / System.Storage_Unit - 1))),
         saved_gid => Load (Data (Data'First + Layout.saved_gid'Position .. Data'First + (Layout.saved_gid'Position + Layout.saved_gid'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return Y.Raw_Task is
      Layout : Y.Raw_Task;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Action => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Action'Position .. Data'First + (Layout.Action'Position + Layout.Action'Size / System.Storage_Unit - 1)))),
         Root => Load (Data (Data'First + Layout.Root'Position .. Data'First + (Layout.Root'Position + Layout.Root'Size / System.Storage_Unit - 1))),
         Child => Load (Data (Data'First + Layout.Child'Position .. Data'First + (Layout.Child'Position + Layout.Child'Size / System.Storage_Unit - 1))),
         task_id => Load (Data (Data'First + Layout.task_id'Position .. Data'First + (Layout.task_id'Position + Layout.task_id'Size / System.Storage_Unit - 1))),
         root_world => Load (Data (Data'First + Layout.root_world'Position .. Data'First + (Layout.root_world'Position + Layout.root_world'Size / System.Storage_Unit - 1))),
         child_world => Load (Data (Data'First + Layout.child_world'Position .. Data'First + (Layout.child_world'Position + Layout.child_world'Size / System.Storage_Unit - 1))),
         root_instance => Load (Data (Data'First + Layout.root_instance'Position .. Data'First + (Layout.root_instance'Position + Layout.root_instance'Size / System.Storage_Unit - 1))),
         child_instance => Load (Data (Data'First + Layout.child_instance'Position .. Data'First + (Layout.child_instance'Position + Layout.child_instance'Size / System.Storage_Unit - 1))),
         world_store => Load (Data (Data'First + Layout.world_store'Position .. Data'First + (Layout.world_store'Position + Layout.world_store'Size / System.Storage_Unit - 1))),
         full_world_ancestry => Load (Data (Data'First + Layout.full_world_ancestry'Position .. Data'First + (Layout.full_world_ancestry'Position + Layout.full_world_ancestry'Size / System.Storage_Unit - 1))),
         original_workload => Load (Data (Data'First + Layout.original_workload'Position .. Data'First + (Layout.original_workload'Position + Layout.original_workload'Size / System.Storage_Unit - 1))),
         sandbox => Load (Data (Data'First + Layout.sandbox'Position .. Data'First + (Layout.sandbox'Position + Layout.sandbox'Size / System.Storage_Unit - 1))),
         adapter => Load (Data (Data'First + Layout.adapter'Position .. Data'First + (Layout.adapter'Position + Layout.adapter'Size / System.Storage_Unit - 1))),
         context => Load (Data (Data'First + Layout.context'Position .. Data'First + (Layout.context'Position + Layout.context'Size / System.Storage_Unit - 1))),
         mission => Load (Data (Data'First + Layout.mission'Position .. Data'First + (Layout.mission'Position + Layout.mission'Size / System.Storage_Unit - 1))),
         stdin => Load (Data (Data'First + Layout.stdin'Position .. Data'First + (Layout.stdin'Position + Layout.stdin'Size / System.Storage_Unit - 1))),
         credential_source => Load (Data (Data'First + Layout.credential_source'Position .. Data'First + (Layout.credential_source'Position + Layout.credential_source'Size / System.Storage_Unit - 1))),
         executable_source => Load (Data (Data'First + Layout.executable_source'Position .. Data'First + (Layout.executable_source'Position + Layout.executable_source'Size / System.Storage_Unit - 1))),
         configuration => Load (Data (Data'First + Layout.configuration'Position .. Data'First + (Layout.configuration'Position + Layout.configuration'Size / System.Storage_Unit - 1))),
         owner_plan => Load (Data (Data'First + Layout.owner_plan'Position .. Data'First + (Layout.owner_plan'Position + Layout.owner_plan'Size / System.Storage_Unit - 1))),
         native_cost_input => Load (Data (Data'First + Layout.native_cost_input'Position .. Data'First + (Layout.native_cost_input'Position + Layout.native_cost_input'Size / System.Storage_Unit - 1))),
         raw_request => Load (Data (Data'First + Layout.raw_request'Position .. Data'First + (Layout.raw_request'Position + Layout.raw_request'Size / System.Storage_Unit - 1))),
         requester => Load (Data (Data'First + Layout.requester'Position .. Data'First + (Layout.requester'Position + Layout.requester'Size / System.Storage_Unit - 1))),
         cause => Load (Data (Data'First + Layout.cause'Position .. Data'First + (Layout.cause'Position + Layout.cause'Size / System.Storage_Unit - 1))),
         root_dispatch => Load (Data (Data'First + Layout.root_dispatch'Position .. Data'First + (Layout.root_dispatch'Position + Layout.root_dispatch'Size / System.Storage_Unit - 1))),
         root_running_event => Load (Data (Data'First + Layout.root_running_event'Position .. Data'First + (Layout.root_running_event'Position + Layout.root_running_event'Size / System.Storage_Unit - 1))),
         task_journal => Load (Data (Data'First + Layout.task_journal'Position .. Data'First + (Layout.task_journal'Position + Layout.task_journal'Size / System.Storage_Unit - 1))),
         task_intent => Load (Data (Data'First + Layout.task_intent'Position .. Data'First + (Layout.task_intent'Position + Layout.task_intent'Size / System.Storage_Unit - 1))),
         task_reservation_event => Load (Data (Data'First + Layout.task_reservation_event'Position .. Data'First + (Layout.task_reservation_event'Position + Layout.task_reservation_event'Size / System.Storage_Unit - 1))),
         task_launch_event => Load (Data (Data'First + Layout.task_launch_event'Position .. Data'First + (Layout.task_launch_event'Position + Layout.task_launch_event'Size / System.Storage_Unit - 1))),
         parent_namespace_source => Load (Data (Data'First + Layout.parent_namespace_source'Position .. Data'First + (Layout.parent_namespace_source'Position + Layout.parent_namespace_source'Size / System.Storage_Unit - 1))),
         fd_lineage => Load (Data (Data'First + Layout.fd_lineage'Position .. Data'First + (Layout.fd_lineage'Position + Layout.fd_lineage'Size / System.Storage_Unit - 1))),
         source_lease => Load (Data (Data'First + Layout.source_lease'Position .. Data'First + (Layout.source_lease'Position + Layout.source_lease'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return Y.Raw_Namespace is
      Layout : Y.Raw_Namespace;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (identity => Load (Data (Data'First + Layout.identity'Position .. Data'First + (Layout.identity'Position + Layout.identity'Size / System.Storage_Unit - 1))),
         parent => Load (Data (Data'First + Layout.parent'Position .. Data'First + (Layout.parent'Position + Layout.parent'Size / System.Storage_Unit - 1))),
         raw_nsfs => Load (Data (Data'First + Layout.raw_nsfs'Position .. Data'First + (Layout.raw_nsfs'Position + Layout.raw_nsfs'Size / System.Storage_Unit - 1))),
         raw_get_parent => Load (Data (Data'First + Layout.raw_get_parent'Position .. Data'First + (Layout.raw_get_parent'Position + Layout.raw_get_parent'Size / System.Storage_Unit - 1))),
         source_lease => Load (Data (Data'First + Layout.source_lease'Position .. Data'First + (Layout.source_lease'Position + Layout.source_lease'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Input is
      Layout : T.Raw_Input;
   begin
      return
        (Schema => Interfaces.Unsigned_32 (Little_Endian (Data (Data'First + Layout.Schema'Position .. Data'First + (Layout.Schema'Position + Layout.Schema'Size / System.Storage_Unit - 1)))),
         Mode => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Mode'Position .. Data'First + (Layout.Mode'Position + Layout.Mode'Size / System.Storage_Unit - 1)))),
         Bound => Load (Data (Data'First + Layout.Bound'Position .. Data'First + (Layout.Bound'Position + Layout.Bound'Size / System.Storage_Unit - 1))),
         Now => Load (Data (Data'First + Layout.Now'Position .. Data'First + (Layout.Now'Position + Layout.Now'Size / System.Storage_Unit - 1))),
         Facts => Load (Data (Data'First + Layout.Facts'Position .. Data'First + (Layout.Facts'Position + Layout.Facts'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Binding is
      Layout : T.Raw_Binding;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Action => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Action'Position .. Data'First + (Layout.Action'Position + Layout.Action'Size / System.Storage_Unit - 1)))),
         Id => Load (Data (Data'First + Layout.Id'Position .. Data'First + (Layout.Id'Position + Layout.Id'Size / System.Storage_Unit - 1))),
         Peer => Load (Data (Data'First + Layout.Peer'Position .. Data'First + (Layout.Peer'Position + Layout.Peer'Size / System.Storage_Unit - 1))),
         Preparer => Load (Data (Data'First + Layout.Preparer'Position .. Data'First + (Layout.Preparer'Position + Layout.Preparer'Size / System.Storage_Unit - 1))),
         Owner => Load (Data (Data'First + Layout.Owner'Position .. Data'First + (Layout.Owner'Position + Layout.Owner'Size / System.Storage_Unit - 1))),
         Target_Owner => Load (Data (Data'First + Layout.Target_Owner'Position .. Data'First + (Layout.Target_Owner'Position + Layout.Target_Owner'Size / System.Storage_Unit - 1))),
         Policy_Epoch => Load (Data (Data'First + Layout.Policy_Epoch'Position .. Data'First + (Layout.Policy_Epoch'Position + Layout.Policy_Epoch'Size / System.Storage_Unit - 1))),
         Resource_Epoch => Load (Data (Data'First + Layout.Resource_Epoch'Position .. Data'First + (Layout.Resource_Epoch'Position + Layout.Resource_Epoch'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Ids is
      Result : T.Raw_Ids;
   begin
      for I in Result'Range loop
         Result (I) := Load (Data (Data'First + Q.Byte_Count (T.A.Identity_Field'Pos (I) - T.A.Identity_Field'Pos (Result'First)) * C.Raw_Digest'Size / System.Storage_Unit .. Data'First + (Q.Byte_Count (T.A.Identity_Field'Pos (I) - T.A.Identity_Field'Pos (Result'First)) * C.Raw_Digest'Size / System.Storage_Unit + C.Raw_Digest'Size / System.Storage_Unit - 1)));
      end loop;
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_UID is
      Layout : T.Raw_UID;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Present'Position .. Data'First + (Layout.Present'Position + Layout.Present'Size / System.Storage_Unit - 1)))),
         Value => Interfaces.Unsigned_32 (Little_Endian (Data (Data'First + Layout.Value'Position .. Data'First + (Layout.Value'Position + Layout.Value'Size / System.Storage_Unit - 1)))));
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Quantity is
      Layout : T.Raw_Quantity;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Present'Position .. Data'First + (Layout.Present'Position + Layout.Present'Size / System.Storage_Unit - 1)))),
         Negative => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Negative'Position .. Data'First + (Layout.Negative'Position + Layout.Negative'Size / System.Storage_Unit - 1)))),
         First => Signed (Data (Data'First + Layout.First'Position .. Data'First + (Layout.First'Position + Layout.First'Size / System.Storage_Unit - 1))),
         Length => Signed (Data (Data'First + Layout.Length'Position .. Data'First + (Layout.Length'Position + Layout.Length'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Evidence is
      Layout : T.Raw_Evidence;
   begin
      return
        (Effect_Binding => Load (Data (Data'First + Layout.Effect_Binding'Position .. Data'First + (Layout.Effect_Binding'Position + Layout.Effect_Binding'Size / System.Storage_Unit - 1))),
         Actual_Receipt_Root => Load (Data (Data'First + Layout.Actual_Receipt_Root'Position .. Data'First + (Layout.Actual_Receipt_Root'Position + Layout.Actual_Receipt_Root'Size / System.Storage_Unit - 1))),
         Actual_Causal_Root => Load (Data (Data'First + Layout.Actual_Causal_Root'Position .. Data'First + (Layout.Actual_Causal_Root'Position + Layout.Actual_Causal_Root'Size / System.Storage_Unit - 1))),
         No_Effect_Binding => Load (Data (Data'First + Layout.No_Effect_Binding'Position .. Data'First + (Layout.No_Effect_Binding'Position + Layout.No_Effect_Binding'Size / System.Storage_Unit - 1))),
         Owner_Resolution => Load (Data (Data'First + Layout.Owner_Resolution'Position .. Data'First + (Layout.Owner_Resolution'Position + Layout.Owner_Resolution'Size / System.Storage_Unit - 1))),
         Quarantine_Head => Load (Data (Data'First + Layout.Quarantine_Head'Position .. Data'First + (Layout.Quarantine_Head'Position + Layout.Quarantine_Head'Size / System.Storage_Unit - 1))),
         Witnessed_Receipt_Head => Load (Data (Data'First + Layout.Witnessed_Receipt_Head'Position .. Data'First + (Layout.Witnessed_Receipt_Head'Position + Layout.Witnessed_Receipt_Head'Size / System.Storage_Unit - 1))),
         Witnessed_Causal_Head => Load (Data (Data'First + Layout.Witnessed_Causal_Head'Position .. Data'First + (Layout.Witnessed_Causal_Head'Position + Layout.Witnessed_Causal_Head'Size / System.Storage_Unit - 1))),
         Recovery => Load (Data (Data'First + Layout.Recovery'Position .. Data'First + (Layout.Recovery'Position + Layout.Recovery'Size / System.Storage_Unit - 1))),
         Original_Use => Load (Data (Data'First + Layout.Original_Use'Position .. Data'First + (Layout.Original_Use'Position + Layout.Original_Use'Size / System.Storage_Unit - 1))),
         Effect_Material_First => Signed (Data (Data'First + Layout.Effect_Material_First'Position .. Data'First + (Layout.Effect_Material_First'Position + Layout.Effect_Material_First'Size / System.Storage_Unit - 1))),
         Effect_Material_Length => Signed (Data (Data'First + Layout.Effect_Material_Length'Position .. Data'First + (Layout.Effect_Material_Length'Position + Layout.Effect_Material_Length'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return RW.Raw_Request is
      Layout : RW.Raw_Request;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Schema_Version => Interfaces.Unsigned_32 (Little_Endian (Data (Data'First + Layout.Schema_Version'Position .. Data'First + (Layout.Schema_Version'Position + Layout.Schema_Version'Size / System.Storage_Unit - 1)))),
         State => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.State'Position .. Data'First + (Layout.State'Position + Layout.State'Size / System.Storage_Unit - 1)))),
         Fresh => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Fresh'Position .. Data'First + (Layout.Fresh'Position + Layout.Fresh'Size / System.Storage_Unit - 1)))),
         Historical => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Historical'Position .. Data'First + (Layout.Historical'Position + Layout.Historical'Size / System.Storage_Unit - 1)))),
         Grant_Eligible => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Grant_Eligible'Position .. Data'First + (Layout.Grant_Eligible'Position + Layout.Grant_Eligible'Size / System.Storage_Unit - 1)))),
         Issued_Binding => Load (Data (Data'First + Layout.Issued_Binding'Position .. Data'First + (Layout.Issued_Binding'Position + Layout.Issued_Binding'Size / System.Storage_Unit - 1))),
         Recovered_Binding => Load (Data (Data'First + Layout.Recovered_Binding'Position .. Data'First + (Layout.Recovered_Binding'Position + Layout.Recovered_Binding'Size / System.Storage_Unit - 1))),
         Native => Load (Data (Data'First + Layout.Native'Position .. Data'First + (Layout.Native'Position + Layout.Native'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return RW.Raw_Binding is
      Layout : RW.Raw_Binding;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Mode => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Mode'Position .. Data'First + (Layout.Mode'Position + Layout.Mode'Size / System.Storage_Unit - 1)))),
         Operation => Load (Data (Data'First + Layout.Operation'Position .. Data'First + (Layout.Operation'Position + Layout.Operation'Size / System.Storage_Unit - 1))),
         Transaction => Load (Data (Data'First + Layout.Transaction'Position .. Data'First + (Layout.Transaction'Position + Layout.Transaction'Size / System.Storage_Unit - 1))),
         Capability => Load (Data (Data'First + Layout.Capability'Position .. Data'First + (Layout.Capability'Position + Layout.Capability'Size / System.Storage_Unit - 1))),
         Universe_Head => Load (Data (Data'First + Layout.Universe_Head'Position .. Data'First + (Layout.Universe_Head'Position + Layout.Universe_Head'Size / System.Storage_Unit - 1))),
         Instance => Load (Data (Data'First + Layout.Instance'Position .. Data'First + (Layout.Instance'Position + Layout.Instance'Size / System.Storage_Unit - 1))),
         Subject => Load (Data (Data'First + Layout.Subject'Position .. Data'First + (Layout.Subject'Position + Layout.Subject'Size / System.Storage_Unit - 1))),
         Staged_Root => Load (Data (Data'First + Layout.Staged_Root'Position .. Data'First + (Layout.Staged_Root'Position + Layout.Staged_Root'Size / System.Storage_Unit - 1))),
         Current_Requirement => Load (Data (Data'First + Layout.Current_Requirement'Position .. Data'First + (Layout.Current_Requirement'Position + Layout.Current_Requirement'Size / System.Storage_Unit - 1))),
         Resulting_Requirement => Load (Data (Data'First + Layout.Resulting_Requirement'Position .. Data'First + (Layout.Resulting_Requirement'Position + Layout.Resulting_Requirement'Size / System.Storage_Unit - 1))),
         Requester => Load (Data (Data'First + Layout.Requester'Position .. Data'First + (Layout.Requester'Position + Layout.Requester'Size / System.Storage_Unit - 1))),
         Grant_Use => Load (Data (Data'First + Layout.Grant_Use'Position .. Data'First + (Layout.Grant_Use'Position + Layout.Grant_Use'Size / System.Storage_Unit - 1))),
         Policy_Identity => Load (Data (Data'First + Layout.Policy_Identity'Position .. Data'First + (Layout.Policy_Identity'Position + Layout.Policy_Identity'Size / System.Storage_Unit - 1))),
         Selected_Evaluation => Load (Data (Data'First + Layout.Selected_Evaluation'Position .. Data'First + (Layout.Selected_Evaluation'Position + Layout.Selected_Evaluation'Size / System.Storage_Unit - 1))),
         History_Head => Load (Data (Data'First + Layout.History_Head'Position .. Data'First + (Layout.History_Head'Position + Layout.History_Head'Size / System.Storage_Unit - 1))),
         Reservation => Load (Data (Data'First + Layout.Reservation'Position .. Data'First + (Layout.Reservation'Position + Layout.Reservation'Size / System.Storage_Unit - 1))),
         Host => Load (Data (Data'First + Layout.Host'Position .. Data'First + (Layout.Host'Position + Layout.Host'Size / System.Storage_Unit - 1))),
         Before_Prime => Load (Data (Data'First + Layout.Before_Prime'Position .. Data'First + (Layout.Before_Prime'Position + Layout.Before_Prime'Size / System.Storage_Unit - 1))),
         Before_Root => Load (Data (Data'First + Layout.Before_Root'Position .. Data'First + (Layout.Before_Root'Position + Layout.Before_Root'Size / System.Storage_Unit - 1))),
         Before_Mapping => Load (Data (Data'First + Layout.Before_Mapping'Position .. Data'First + (Layout.Before_Mapping'Position + Layout.Before_Mapping'Size / System.Storage_Unit - 1))),
         Staged_Mapping => Load (Data (Data'First + Layout.Staged_Mapping'Position .. Data'First + (Layout.Staged_Mapping'Position + Layout.Staged_Mapping'Size / System.Storage_Unit - 1))),
         Input_Snapshot => Load (Data (Data'First + Layout.Input_Snapshot'Position .. Data'First + (Layout.Input_Snapshot'Position + Layout.Input_Snapshot'Size / System.Storage_Unit - 1))),
         Kernel_Build => Load (Data (Data'First + Layout.Kernel_Build'Position .. Data'First + (Layout.Kernel_Build'Position + Layout.Kernel_Build'Size / System.Storage_Unit - 1))),
         Kernel_Library => Load (Data (Data'First + Layout.Kernel_Library'Position .. Data'First + (Layout.Kernel_Library'Position + Layout.Kernel_Library'Size / System.Storage_Unit - 1))),
         Kernel_Mapping => Load (Data (Data'First + Layout.Kernel_Mapping'Position .. Data'First + (Layout.Kernel_Mapping'Position + Layout.Kernel_Mapping'Size / System.Storage_Unit - 1))),
         Issuer_Head => Load (Data (Data'First + Layout.Issuer_Head'Position .. Data'First + (Layout.Issuer_Head'Position + Layout.Issuer_Head'Size / System.Storage_Unit - 1))),
         Receipt_Head => Load (Data (Data'First + Layout.Receipt_Head'Position .. Data'First + (Layout.Receipt_Head'Position + Layout.Receipt_Head'Size / System.Storage_Unit - 1))),
         Causal_Head => Load (Data (Data'First + Layout.Causal_Head'Position .. Data'First + (Layout.Causal_Head'Position + Layout.Causal_Head'Size / System.Storage_Unit - 1))),
         Policy_Epoch => Load (Data (Data'First + Layout.Policy_Epoch'Position .. Data'First + (Layout.Policy_Epoch'Position + Layout.Policy_Epoch'Size / System.Storage_Unit - 1))),
         Resource_Epoch => Load (Data (Data'First + Layout.Resource_Epoch'Position .. Data'First + (Layout.Resource_Epoch'Position + Layout.Resource_Epoch'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return RW.Raw_Digest is
      Layout : RW.Raw_Digest;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Present'Position .. Data'First + (Layout.Present'Position + Layout.Present'Size / System.Storage_Unit - 1)))),
         Value => Load (Data (Data'First + Layout.Value'Position .. Data'First + (Layout.Value'Position + Layout.Value'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return RW.Raw_Hash is
      Result : RW.Raw_Hash;
   begin
      for I in Result'Range loop
         Result (I) := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Q.Byte_Count (I - Result'First) * Interfaces.Unsigned_8'Size / System.Storage_Unit .. Data'First + (Q.Byte_Count (I - Result'First) * Interfaces.Unsigned_8'Size / System.Storage_Unit + Interfaces.Unsigned_8'Size / System.Storage_Unit - 1))));
      end loop;
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return RW.Raw_Epoch is
      Layout : RW.Raw_Epoch;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Present'Position .. Data'First + (Layout.Present'Position + Layout.Present'Size / System.Storage_Unit - 1)))),
         Negative => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Negative'Position .. Data'First + (Layout.Negative'Position + Layout.Negative'Size / System.Storage_Unit - 1)))),
         First => Signed (Data (Data'First + Layout.First'Position .. Data'First + (Layout.First'Position + Layout.First'Size / System.Storage_Unit - 1))),
         Length => Signed (Data (Data'First + Layout.Length'Position .. Data'First + (Layout.Length'Position + Layout.Length'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return RW.Raw_Native is
      Layout : RW.Raw_Native;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Live_Mapping => Load (Data (Data'First + Layout.Live_Mapping'Position .. Data'First + (Layout.Live_Mapping'Position + Layout.Live_Mapping'Size / System.Storage_Unit - 1))),
         Live_Root => Load (Data (Data'First + Layout.Live_Root'Position .. Data'First + (Layout.Live_Root'Position + Layout.Live_Root'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Grant is
      Layout : T.Raw_Grant;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Id => Load (Data (Data'First + Layout.Id'Position .. Data'First + (Layout.Id'Position + Layout.Id'Size / System.Storage_Unit - 1))),
         Parent => Load (Data (Data'First + Layout.Parent'Position .. Data'First + (Layout.Parent'Position + Layout.Parent'Size / System.Storage_Unit - 1))),
         Issuer => Load (Data (Data'First + Layout.Issuer'Position .. Data'First + (Layout.Issuer'Position + Layout.Issuer'Size / System.Storage_Unit - 1))),
         Instance => Load (Data (Data'First + Layout.Instance'Position .. Data'First + (Layout.Instance'Position + Layout.Instance'Size / System.Storage_Unit - 1))),
         Root_Set => Load (Data (Data'First + Layout.Root_Set'Position .. Data'First + (Layout.Root_Set'Position + Layout.Root_Set'Size / System.Storage_Unit - 1))),
         Policy => Load (Data (Data'First + Layout.Policy'Position .. Data'First + (Layout.Policy'Position + Layout.Policy'Size / System.Storage_Unit - 1))),
         Subject => Load (Data (Data'First + Layout.Subject'Position .. Data'First + (Layout.Subject'Position + Layout.Subject'Size / System.Storage_Unit - 1))),
         Owner => Load (Data (Data'First + Layout.Owner'Position .. Data'First + (Layout.Owner'Position + Layout.Owner'Size / System.Storage_Unit - 1))),
         Allowed => Load (Data (Data'First + Layout.Allowed'Position .. Data'First + (Layout.Allowed'Position + Layout.Allowed'Size / System.Storage_Unit - 1))),
         State => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.State'Position .. Data'First + (Layout.State'Position + Layout.State'Size / System.Storage_Unit - 1)))),
         Epoch => Load (Data (Data'First + Layout.Epoch'Position .. Data'First + (Layout.Epoch'Position + Layout.Epoch'Size / System.Storage_Unit - 1))),
         Ceiling => Load (Data (Data'First + Layout.Ceiling'Position .. Data'First + (Layout.Ceiling'Position + Layout.Ceiling'Size / System.Storage_Unit - 1))),
         Issued_At => Load (Data (Data'First + Layout.Issued_At'Position .. Data'First + (Layout.Issued_At'Position + Layout.Issued_At'Size / System.Storage_Unit - 1))),
         Expires_At => Load (Data (Data'First + Layout.Expires_At'Position .. Data'First + (Layout.Expires_At'Position + Layout.Expires_At'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Rights is
      Result : T.Raw_Rights;
   begin
      for I in Result'Range loop
         Result (I) := Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Q.Byte_Count (T.A.Operation'Pos (I) - T.A.Operation'Pos (Result'First)) * Interfaces.Unsigned_8'Size / System.Storage_Unit .. Data'First + (Q.Byte_Count (T.A.Operation'Pos (I) - T.A.Operation'Pos (Result'First)) * Interfaces.Unsigned_8'Size / System.Storage_Unit + Interfaces.Unsigned_8'Size / System.Storage_Unit - 1))));
      end loop;
      return Result;
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Use is
      Layout : T.Raw_Use;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Bound => Load (Data (Data'First + Layout.Bound'Position .. Data'First + (Layout.Bound'Position + Layout.Bound'Size / System.Storage_Unit - 1))),
         State => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.State'Position .. Data'First + (Layout.State'Position + Layout.State'Size / System.Storage_Unit - 1)))));
   end Load;
   function Load (Data : Q.Byte_Array) return C.Raw_Row is
      Layout : C.Raw_Row;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Previous => Load (Data (Data'First + Layout.Previous'Position .. Data'First + (Layout.Previous'Position + Layout.Previous'Size / System.Storage_Unit - 1))),
         Actual_Payload_Root => Load (Data (Data'First + Layout.Actual_Payload_Root'Position .. Data'First + (Layout.Actual_Payload_Root'Position + Layout.Actual_Payload_Root'Size / System.Storage_Unit - 1))),
         Stored_Payload_Root => Load (Data (Data'First + Layout.Stored_Payload_Root'Position .. Data'First + (Layout.Stored_Payload_Root'Position + Layout.Stored_Payload_Root'Size / System.Storage_Unit - 1))),
         Stored_Head => Load (Data (Data'First + Layout.Stored_Head'Position .. Data'First + (Layout.Stored_Head'Position + Layout.Stored_Head'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return D.Raw_Capability is
      Layout : D.Raw_Capability;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Index => Load (Data (Data'First + Layout.Index'Position .. Data'First + (Layout.Index'Position + Layout.Index'Size / System.Storage_Unit - 1))),
         Bounding => Load (Data (Data'First + Layout.Bounding'Position .. Data'First + (Layout.Bounding'Position + Layout.Bounding'Size / System.Storage_Unit - 1))),
         Ambient => Load (Data (Data'First + Layout.Ambient'Position .. Data'First + (Layout.Ambient'Position + Layout.Ambient'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Scope_Frame is
      Layout : N.Raw_Scope_Frame;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Scope => Load (Data (Data'First + Layout.Scope'Position .. Data'First + (Layout.Scope'Position + Layout.Scope'Size / System.Storage_Unit - 1))),
         First_Epoch => Load (Data (Data'First + Layout.First_Epoch'Position .. Data'First + (Layout.First_Epoch'Position + Layout.First_Epoch'Size / System.Storage_Unit - 1))),
         Universe_Head => Load (Data (Data'First + Layout.Universe_Head'Position .. Data'First + (Layout.Universe_Head'Position + Layout.Universe_Head'Size / System.Storage_Unit - 1))),
         Frame_Head => Load (Data (Data'First + Layout.Frame_Head'Position .. Data'First + (Layout.Frame_Head'Position + Layout.Frame_Head'Size / System.Storage_Unit - 1))),
         Prior_Frame => Load (Data (Data'First + Layout.Prior_Frame'Position .. Data'First + (Layout.Prior_Frame'Position + Layout.Prior_Frame'Size / System.Storage_Unit - 1))),
         Store_Genesis => Load (Data (Data'First + Layout.Store_Genesis'Position .. Data'First + (Layout.Store_Genesis'Position + Layout.Store_Genesis'Size / System.Storage_Unit - 1))),
         Store_Id => Load (Data (Data'First + Layout.Store_Id'Position .. Data'First + (Layout.Store_Id'Position + Layout.Store_Id'Size / System.Storage_Unit - 1))),
         Root_Head => Load (Data (Data'First + Layout.Root_Head'Position .. Data'First + (Layout.Root_Head'Position + Layout.Root_Head'Size / System.Storage_Unit - 1))),
         Prime => Load (Data (Data'First + Layout.Prime'Position .. Data'First + (Layout.Prime'Position + Layout.Prime'Size / System.Storage_Unit - 1))),
         Root_Count => Load (Data (Data'First + Layout.Root_Count'Position .. Data'First + (Layout.Root_Count'Position + Layout.Root_Count'Size / System.Storage_Unit - 1))),
         Cause => Load (Data (Data'First + Layout.Cause'Position .. Data'First + (Layout.Cause'Position + Layout.Cause'Size / System.Storage_Unit - 1))),
         Requester => Load (Data (Data'First + Layout.Requester'Position .. Data'First + (Layout.Requester'Position + Layout.Requester'Size / System.Storage_Unit - 1))),
         Receipt => Load (Data (Data'First + Layout.Receipt'Position .. Data'First + (Layout.Receipt'Position + Layout.Receipt'Size / System.Storage_Unit - 1))),
         Catalogue_Head => Load (Data (Data'First + Layout.Catalogue_Head'Position .. Data'First + (Layout.Catalogue_Head'Position + Layout.Catalogue_Head'Size / System.Storage_Unit - 1))),
         Observation_Head => Load (Data (Data'First + Layout.Observation_Head'Position .. Data'First + (Layout.Observation_Head'Position + Layout.Observation_Head'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Projection is
      Layout : N.Raw_Projection;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Key => Load (Data (Data'First + Layout.Key'Position .. Data'First + (Layout.Key'Position + Layout.Key'Size / System.Storage_Unit - 1))),
         Bound => Load (Data (Data'First + Layout.Bound'Position .. Data'First + (Layout.Bound'Position + Layout.Bound'Size / System.Storage_Unit - 1))),
         Origin => Load (Data (Data'First + Layout.Origin'Position .. Data'First + (Layout.Origin'Position + Layout.Origin'Size / System.Storage_Unit - 1))),
         Catalogue_Head => Load (Data (Data'First + Layout.Catalogue_Head'Position .. Data'First + (Layout.Catalogue_Head'Position + Layout.Catalogue_Head'Size / System.Storage_Unit - 1))),
         Numerator => Load (Data (Data'First + Layout.Numerator'Position .. Data'First + (Layout.Numerator'Position + Layout.Numerator'Size / System.Storage_Unit - 1))),
         Denominator => Load (Data (Data'First + Layout.Denominator'Position .. Data'First + (Layout.Denominator'Position + Layout.Denominator'Size / System.Storage_Unit - 1))),
         Amount => Load (Data (Data'First + Layout.Amount'Position .. Data'First + (Layout.Amount'Position + Layout.Amount'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Physical_Key is
      Layout : N.Raw_Physical_Key;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Machine => Load (Data (Data'First + Layout.Machine'Position .. Data'First + (Layout.Machine'Position + Layout.Machine'Size / System.Storage_Unit - 1))),
         Resource => Load (Data (Data'First + Layout.Resource'Position .. Data'First + (Layout.Resource'Position + Layout.Resource'Size / System.Storage_Unit - 1))),
         Unit => Load (Data (Data'First + Layout.Unit'Position .. Data'First + (Layout.Unit'Position + Layout.Unit'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Bucket is
      Layout : N.Raw_Bucket;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Key => Load (Data (Data'First + Layout.Key'Position .. Data'First + (Layout.Key'Position + Layout.Key'Size / System.Storage_Unit - 1))),
         Capacity => Load (Data (Data'First + Layout.Capacity'Position .. Data'First + (Layout.Capacity'Position + Layout.Capacity'Size / System.Storage_Unit - 1))),
         Held_Total => Load (Data (Data'First + Layout.Held_Total'Position .. Data'First + (Layout.Held_Total'Position + Layout.Held_Total'Size / System.Storage_Unit - 1))),
         Charged_Total => Load (Data (Data'First + Layout.Charged_Total'Position .. Data'First + (Layout.Charged_Total'Position + Layout.Charged_Total'Size / System.Storage_Unit - 1))),
         Capacity_Source => Load (Data (Data'First + Layout.Capacity_Source'Position .. Data'First + (Layout.Capacity_Source'Position + Layout.Capacity_Source'Size / System.Storage_Unit - 1))),
         Catalogue_Head => Load (Data (Data'First + Layout.Catalogue_Head'Position .. Data'First + (Layout.Catalogue_Head'Position + Layout.Catalogue_Head'Size / System.Storage_Unit - 1))),
         Observation_Head => Load (Data (Data'First + Layout.Observation_Head'Position .. Data'First + (Layout.Observation_Head'Position + Layout.Observation_Head'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Native is
      Layout : W.Raw_Native;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Scope => Load (Data (Data'First + Layout.Scope'Position .. Data'First + (Layout.Scope'Position + Layout.Scope'Size / System.Storage_Unit - 1))),
         Resource_Epoch => Load (Data (Data'First + Layout.Resource_Epoch'Position .. Data'First + (Layout.Resource_Epoch'Position + Layout.Resource_Epoch'Size / System.Storage_Unit - 1))),
         Bound => Load (Data (Data'First + Layout.Bound'Position .. Data'First + (Layout.Bound'Position + Layout.Bound'Size / System.Storage_Unit - 1))),
         Actual_Unit => Load (Data (Data'First + Layout.Actual_Unit'Position .. Data'First + (Layout.Actual_Unit'Position + Layout.Actual_Unit'Size / System.Storage_Unit - 1))),
         Cgroup => Load (Data (Data'First + Layout.Cgroup'Position .. Data'First + (Layout.Cgroup'Position + Layout.Cgroup'Size / System.Storage_Unit - 1))),
         Invocation => Load (Data (Data'First + Layout.Invocation'Position .. Data'First + (Layout.Invocation'Position + Layout.Invocation'Size / System.Storage_Unit - 1))),
         Observation_Head => Load (Data (Data'First + Layout.Observation_Head'Position .. Data'First + (Layout.Observation_Head'Position + Layout.Observation_Head'Size / System.Storage_Unit - 1))),
         Observed => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Observed'Position .. Data'First + (Layout.Observed'Position + Layout.Observed'Size / System.Storage_Unit - 1)))));
   end Load;
   function Load (Data : Q.Byte_Array) return O.Raw_Facts is
      Layout : O.Raw_Facts;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Current => Load (Data (Data'First + Layout.Current'Position .. Data'First + (Layout.Current'Position + Layout.Current'Size / System.Storage_Unit - 1))),
         Current_Epoch => Load (Data (Data'First + Layout.Current_Epoch'Position .. Data'First + (Layout.Current_Epoch'Position + Layout.Current_Epoch'Size / System.Storage_Unit - 1))),
         Retained => Load (Data (Data'First + Layout.Retained'Position .. Data'First + (Layout.Retained'Position + Layout.Retained'Size / System.Storage_Unit - 1))),
         Current_Universe_Head => Load (Data (Data'First + Layout.Current_Universe_Head'Position .. Data'First + (Layout.Current_Universe_Head'Position + Layout.Current_Universe_Head'Size / System.Storage_Unit - 1))),
         Current_Ledger_Head => Load (Data (Data'First + Layout.Current_Ledger_Head'Position .. Data'First + (Layout.Current_Ledger_Head'Position + Layout.Current_Ledger_Head'Size / System.Storage_Unit - 1))),
         Intent => Load (Data (Data'First + Layout.Intent'Position .. Data'First + (Layout.Intent'Position + Layout.Intent'Size / System.Storage_Unit - 1))),
         Dispatch => Load (Data (Data'First + Layout.Dispatch'Position .. Data'First + (Layout.Dispatch'Position + Layout.Dispatch'Size / System.Storage_Unit - 1))),
         Observation_Head => Load (Data (Data'First + Layout.Observation_Head'Position .. Data'First + (Layout.Observation_Head'Position + Layout.Observation_Head'Size / System.Storage_Unit - 1))),
         Actual_Unit => Load (Data (Data'First + Layout.Actual_Unit'Position .. Data'First + (Layout.Actual_Unit'Position + Layout.Actual_Unit'Size / System.Storage_Unit - 1))),
         Cgroup => Load (Data (Data'First + Layout.Cgroup'Position .. Data'First + (Layout.Cgroup'Position + Layout.Cgroup'Size / System.Storage_Unit - 1))),
         Invocation => Load (Data (Data'First + Layout.Invocation'Position .. Data'First + (Layout.Invocation'Position + Layout.Invocation'Size / System.Storage_Unit - 1))),
         Namespace => Load (Data (Data'First + Layout.Namespace'Position .. Data'First + (Layout.Namespace'Position + Layout.Namespace'Size / System.Storage_Unit - 1))),
         Held_Namespace => Load (Data (Data'First + Layout.Held_Namespace'Position .. Data'First + (Layout.Held_Namespace'Position + Layout.Held_Namespace'Size / System.Storage_Unit - 1))),
         Peer => Load (Data (Data'First + Layout.Peer'Position .. Data'First + (Layout.Peer'Position + Layout.Peer'Size / System.Storage_Unit - 1))),
         Held_Peer => Load (Data (Data'First + Layout.Held_Peer'Position .. Data'First + (Layout.Held_Peer'Position + Layout.Held_Peer'Size / System.Storage_Unit - 1))),
         Helper_Image => Load (Data (Data'First + Layout.Helper_Image'Position .. Data'First + (Layout.Helper_Image'Position + Layout.Helper_Image'Size / System.Storage_Unit - 1))),
         Expected_Helper_Image => Load (Data (Data'First + Layout.Expected_Helper_Image'Position .. Data'First + (Layout.Expected_Helper_Image'Position + Layout.Expected_Helper_Image'Size / System.Storage_Unit - 1))),
         Challenge => Load (Data (Data'First + Layout.Challenge'Position .. Data'First + (Layout.Challenge'Position + Layout.Challenge'Size / System.Storage_Unit - 1))),
         Held_Challenge => Load (Data (Data'First + Layout.Held_Challenge'Position .. Data'First + (Layout.Held_Challenge'Position + Layout.Held_Challenge'Size / System.Storage_Unit - 1))),
         Protocol => Load (Data (Data'First + Layout.Protocol'Position .. Data'First + (Layout.Protocol'Position + Layout.Protocol'Size / System.Storage_Unit - 1))),
         Closed_Event => Load (Data (Data'First + Layout.Closed_Event'Position .. Data'First + (Layout.Closed_Event'Position + Layout.Closed_Event'Size / System.Storage_Unit - 1))),
         Namespace_Wait => Load (Data (Data'First + Layout.Namespace_Wait'Position .. Data'First + (Layout.Namespace_Wait'Position + Layout.Namespace_Wait'Size / System.Storage_Unit - 1))),
         Helper_Wait => Load (Data (Data'First + Layout.Helper_Wait'Position .. Data'First + (Layout.Helper_Wait'Position + Layout.Helper_Wait'Size / System.Storage_Unit - 1))),
         Cgroup_Events => Load (Data (Data'First + Layout.Cgroup_Events'Position .. Data'First + (Layout.Cgroup_Events'Position + Layout.Cgroup_Events'Size / System.Storage_Unit - 1))),
         Cgroup_Type => Load (Data (Data'First + Layout.Cgroup_Type'Position .. Data'First + (Layout.Cgroup_Type'Position + Layout.Cgroup_Type'Size / System.Storage_Unit - 1))),
         Manager_Delegate => Load (Data (Data'First + Layout.Manager_Delegate'Position .. Data'First + (Layout.Manager_Delegate'Position + Layout.Manager_Delegate'Size / System.Storage_Unit - 1))),
         Cgroup_Owner => Load (Data (Data'First + Layout.Cgroup_Owner'Position .. Data'First + (Layout.Cgroup_Owner'Position + Layout.Cgroup_Owner'Size / System.Storage_Unit - 1))),
         Cgroup_Group_Write => Load (Data (Data'First + Layout.Cgroup_Group_Write'Position .. Data'First + (Layout.Cgroup_Group_Write'Position + Layout.Cgroup_Group_Write'Size / System.Storage_Unit - 1))),
         Cgroup_Other_Write => Load (Data (Data'First + Layout.Cgroup_Other_Write'Position .. Data'First + (Layout.Cgroup_Other_Write'Position + Layout.Cgroup_Other_Write'Size / System.Storage_Unit - 1))),
         Actual_Store_Genesis => Load (Data (Data'First + Layout.Actual_Store_Genesis'Position .. Data'First + (Layout.Actual_Store_Genesis'Position + Layout.Actual_Store_Genesis'Size / System.Storage_Unit - 1))),
         Actual_Store_Id => Load (Data (Data'First + Layout.Actual_Store_Id'Position .. Data'First + (Layout.Actual_Store_Id'Position + Layout.Actual_Store_Id'Size / System.Storage_Unit - 1))),
         Owner_Store_Genesis => Load (Data (Data'First + Layout.Owner_Store_Genesis'Position .. Data'First + (Layout.Owner_Store_Genesis'Position + Layout.Owner_Store_Genesis'Size / System.Storage_Unit - 1))),
         Owner_Store_Id => Load (Data (Data'First + Layout.Owner_Store_Id'Position .. Data'First + (Layout.Owner_Store_Id'Position + Layout.Owner_Store_Id'Size / System.Storage_Unit - 1))),
         Genesis_Universe => Load (Data (Data'First + Layout.Genesis_Universe'Position .. Data'First + (Layout.Genesis_Universe'Position + Layout.Genesis_Universe'Size / System.Storage_Unit - 1))),
         Genesis_Instance => Load (Data (Data'First + Layout.Genesis_Instance'Position .. Data'First + (Layout.Genesis_Instance'Position + Layout.Genesis_Instance'Size / System.Storage_Unit - 1))),
         Genesis_Context_Head => Load (Data (Data'First + Layout.Genesis_Context_Head'Position .. Data'First + (Layout.Genesis_Context_Head'Position + Layout.Genesis_Context_Head'Size / System.Storage_Unit - 1))),
         Genesis_Prime => Load (Data (Data'First + Layout.Genesis_Prime'Position .. Data'First + (Layout.Genesis_Prime'Position + Layout.Genesis_Prime'Size / System.Storage_Unit - 1))),
         Genesis_Root_Count => Load (Data (Data'First + Layout.Genesis_Root_Count'Position .. Data'First + (Layout.Genesis_Root_Count'Position + Layout.Genesis_Root_Count'Size / System.Storage_Unit - 1))),
         Phase => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Phase'Position .. Data'First + (Layout.Phase'Position + Layout.Phase'Size / System.Storage_Unit - 1)))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Result is
      Layout : W.Raw_Result;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Status => Interfaces.Unsigned_32 (Little_Endian (Data (Data'First + Layout.Status'Position .. Data'First + (Layout.Status'Position + Layout.Status'Size / System.Storage_Unit - 1)))));
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Result is
      Layout : T.Raw_Result;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Disposition => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Disposition'Position .. Data'First + (Layout.Disposition'Position + Layout.Disposition'Size / System.Storage_Unit - 1)))));
   end Load;
   function Load (Data : Q.Byte_Array) return HC.Raw_Input is
      Layout : HC.Raw_Input;
   begin
      return
        (Historical => Load (Data (Data'First + Layout.Historical'Position .. Data'First + (Layout.Historical'Position + Layout.Historical'Size / System.Storage_Unit - 1))),
         Current => Load (Data (Data'First + Layout.Current'Position .. Data'First + (Layout.Current'Position + Layout.Current'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return CX.Raw_Input is
      Layout : CX.Raw_Input;
   begin
      return
        (Operation_Input => Load (Data (Data'First + Layout.Operation_Input'Position .. Data'First + (Layout.Operation_Input'Position + Layout.Operation_Input'Size / System.Storage_Unit - 1))),
         Material => Load (Data (Data'First + Layout.Material'Position .. Data'First + (Layout.Material'Position + Layout.Material'Size / System.Storage_Unit - 1))),
         Before => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Before'Position .. Data'First + (Layout.Before'Position + Layout.Before'Size / System.Storage_Unit - 1)))),
         Mode => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Mode'Position .. Data'First + (Layout.Mode'Position + Layout.Mode'Size / System.Storage_Unit - 1)))));
   end Load;
   function Load (Data : Q.Byte_Array) return CO.Raw_Input is
      Layout : CO.Raw_Input;
   begin
      return
        (Authority => Load (Data (Data'First + Layout.Authority'Position .. Data'First + (Layout.Authority'Position + Layout.Authority'Size / System.Storage_Unit - 1))),
         State => Load (Data (Data'First + Layout.State'Position .. Data'First + (Layout.State'Position + Layout.State'Size / System.Storage_Unit - 1))),
         Bound => Load (Data (Data'First + Layout.Bound'Position .. Data'First + (Layout.Bound'Position + Layout.Bound'Size / System.Storage_Unit - 1))),
         Requester => Load (Data (Data'First + Layout.Requester'Position .. Data'First + (Layout.Requester'Position + Layout.Requester'Size / System.Storage_Unit - 1))),
         Peer => Load (Data (Data'First + Layout.Peer'Position .. Data'First + (Layout.Peer'Position + Layout.Peer'Size / System.Storage_Unit - 1))),
         Collapse => Load (Data (Data'First + Layout.Collapse'Position .. Data'First + (Layout.Collapse'Position + Layout.Collapse'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_State is
      Layout : W.Raw_State;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Scope => Load (Data (Data'First + Layout.Scope'Position .. Data'First + (Layout.Scope'Position + Layout.Scope'Size / System.Storage_Unit - 1))),
         Resource_Epoch => Load (Data (Data'First + Layout.Resource_Epoch'Position .. Data'First + (Layout.Resource_Epoch'Position + Layout.Resource_Epoch'Size / System.Storage_Unit - 1))),
         Universe_Head => Load (Data (Data'First + Layout.Universe_Head'Position .. Data'First + (Layout.Universe_Head'Position + Layout.Universe_Head'Size / System.Storage_Unit - 1))),
         Ledger_Head => Load (Data (Data'First + Layout.Ledger_Head'Position .. Data'First + (Layout.Ledger_Head'Position + Layout.Ledger_Head'Size / System.Storage_Unit - 1))),
         Capacity => Load (Data (Data'First + Layout.Capacity'Position .. Data'First + (Layout.Capacity'Position + Layout.Capacity'Size / System.Storage_Unit - 1))),
         Held_Total => Load (Data (Data'First + Layout.Held_Total'Position .. Data'First + (Layout.Held_Total'Position + Layout.Held_Total'Size / System.Storage_Unit - 1))),
         Charged_Total => Load (Data (Data'First + Layout.Charged_Total'Position .. Data'First + (Layout.Charged_Total'Position + Layout.Charged_Total'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return CW.Raw_Request is
      Layout : CW.Raw_Request;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Candidate_State => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Candidate_State'Position .. Data'First + (Layout.Candidate_State'Position + Layout.Candidate_State'Size / System.Storage_Unit - 1)))),
         Phase => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Phase'Position .. Data'First + (Layout.Phase'Position + Layout.Phase'Size / System.Storage_Unit - 1)))),
         Evaluation_Mode => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Evaluation_Mode'Position .. Data'First + (Layout.Evaluation_Mode'Position + Layout.Evaluation_Mode'Size / System.Storage_Unit - 1)))),
         Conflicts => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Conflicts'Position .. Data'First + (Layout.Conflicts'Position + Layout.Conflicts'Size / System.Storage_Unit - 1)))),
         Foreign_Writes => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Foreign_Writes'Position .. Data'First + (Layout.Foreign_Writes'Position + Layout.Foreign_Writes'Size / System.Storage_Unit - 1)))),
         Roster_Complete => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Roster_Complete'Position .. Data'First + (Layout.Roster_Complete'Position + Layout.Roster_Complete'Size / System.Storage_Unit - 1)))),
         Staged_Roster_Complete => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Staged_Roster_Complete'Position .. Data'First + (Layout.Staged_Roster_Complete'Position + Layout.Staged_Roster_Complete'Size / System.Storage_Unit - 1)))),
         Expected_Parent => Load (Data (Data'First + Layout.Expected_Parent'Position .. Data'First + (Layout.Expected_Parent'Position + Layout.Expected_Parent'Size / System.Storage_Unit - 1))),
         Candidate_Parent => Load (Data (Data'First + Layout.Candidate_Parent'Position .. Data'First + (Layout.Candidate_Parent'Position + Layout.Candidate_Parent'Size / System.Storage_Unit - 1))),
         Expected_Subject => Load (Data (Data'First + Layout.Expected_Subject'Position .. Data'First + (Layout.Expected_Subject'Position + Layout.Expected_Subject'Size / System.Storage_Unit - 1))),
         Evidence_Subject => Load (Data (Data'First + Layout.Evidence_Subject'Position .. Data'First + (Layout.Evidence_Subject'Position + Layout.Evidence_Subject'Size / System.Storage_Unit - 1))),
         Expected_Base => Load (Data (Data'First + Layout.Expected_Base'Position .. Data'First + (Layout.Expected_Base'Position + Layout.Expected_Base'Size / System.Storage_Unit - 1))),
         Candidate_Base => Load (Data (Data'First + Layout.Candidate_Base'Position .. Data'First + (Layout.Candidate_Base'Position + Layout.Candidate_Base'Size / System.Storage_Unit - 1))),
         Expected_Delta => Load (Data (Data'First + Layout.Expected_Delta'Position .. Data'First + (Layout.Expected_Delta'Position + Layout.Expected_Delta'Size / System.Storage_Unit - 1))),
         Candidate_Delta => Load (Data (Data'First + Layout.Candidate_Delta'Position .. Data'First + (Layout.Candidate_Delta'Position + Layout.Candidate_Delta'Size / System.Storage_Unit - 1))),
         Expected_Root_Set => Load (Data (Data'First + Layout.Expected_Root_Set'Position .. Data'First + (Layout.Expected_Root_Set'Position + Layout.Expected_Root_Set'Size / System.Storage_Unit - 1))),
         Candidate_Root_Set => Load (Data (Data'First + Layout.Candidate_Root_Set'Position .. Data'First + (Layout.Candidate_Root_Set'Position + Layout.Candidate_Root_Set'Size / System.Storage_Unit - 1))),
         Expected_Staged_Root => Load (Data (Data'First + Layout.Expected_Staged_Root'Position .. Data'First + (Layout.Expected_Staged_Root'Position + Layout.Expected_Staged_Root'Size / System.Storage_Unit - 1))),
         Actual_Staged_Root => Load (Data (Data'First + Layout.Actual_Staged_Root'Position .. Data'First + (Layout.Actual_Staged_Root'Position + Layout.Actual_Staged_Root'Size / System.Storage_Unit - 1))),
         Staged_Content_Root => Load (Data (Data'First + Layout.Staged_Content_Root'Position .. Data'First + (Layout.Staged_Content_Root'Position + Layout.Staged_Content_Root'Size / System.Storage_Unit - 1))),
         Tested_Root => Load (Data (Data'First + Layout.Tested_Root'Position .. Data'First + (Layout.Tested_Root'Position + Layout.Tested_Root'Size / System.Storage_Unit - 1))),
         Current_Requirement => Load (Data (Data'First + Layout.Current_Requirement'Position .. Data'First + (Layout.Current_Requirement'Position + Layout.Current_Requirement'Size / System.Storage_Unit - 1))),
         Resulting_Requirement => Load (Data (Data'First + Layout.Resulting_Requirement'Position .. Data'First + (Layout.Resulting_Requirement'Position + Layout.Resulting_Requirement'Size / System.Storage_Unit - 1))),
         Evaluated_Requirement => Load (Data (Data'First + Layout.Evaluated_Requirement'Position .. Data'First + (Layout.Evaluated_Requirement'Position + Layout.Evaluated_Requirement'Size / System.Storage_Unit - 1))),
         Declared_Verifiers => Load (Data (Data'First + Layout.Declared_Verifiers'Position .. Data'First + (Layout.Declared_Verifiers'Position + Layout.Declared_Verifiers'Size / System.Storage_Unit - 1))),
         Executed_Verifiers => Load (Data (Data'First + Layout.Executed_Verifiers'Position .. Data'First + (Layout.Executed_Verifiers'Position + Layout.Executed_Verifiers'Size / System.Storage_Unit - 1))),
         Staged_Evaluated_Requirement => Load (Data (Data'First + Layout.Staged_Evaluated_Requirement'Position .. Data'First + (Layout.Staged_Evaluated_Requirement'Position + Layout.Staged_Evaluated_Requirement'Size / System.Storage_Unit - 1))),
         Staged_Executed_Verifiers => Load (Data (Data'First + Layout.Staged_Executed_Verifiers'Position .. Data'First + (Layout.Staged_Executed_Verifiers'Position + Layout.Staged_Executed_Verifiers'Size / System.Storage_Unit - 1))),
         Staged_Examined_Root => Load (Data (Data'First + Layout.Staged_Examined_Root'Position .. Data'First + (Layout.Staged_Examined_Root'Position + Layout.Staged_Examined_Root'Size / System.Storage_Unit - 1))),
         Expected_Checkpoint => Load (Data (Data'First + Layout.Expected_Checkpoint'Position .. Data'First + (Layout.Expected_Checkpoint'Position + Layout.Expected_Checkpoint'Size / System.Storage_Unit - 1))),
         Witnessed_Checkpoint => Load (Data (Data'First + Layout.Witnessed_Checkpoint'Position .. Data'First + (Layout.Witnessed_Checkpoint'Position + Layout.Witnessed_Checkpoint'Size / System.Storage_Unit - 1))),
         Registered_Watch_Set => Load (Data (Data'First + Layout.Registered_Watch_Set'Position .. Data'First + (Layout.Registered_Watch_Set'Position + Layout.Registered_Watch_Set'Size / System.Storage_Unit - 1))),
         Watched_Set => Load (Data (Data'First + Layout.Watched_Set'Position .. Data'First + (Layout.Watched_Set'Position + Layout.Watched_Set'Size / System.Storage_Unit - 1))),
         Generation_Before => Load (Data (Data'First + Layout.Generation_Before'Position .. Data'First + (Layout.Generation_Before'Position + Layout.Generation_Before'Size / System.Storage_Unit - 1))),
         Generation_After => Load (Data (Data'First + Layout.Generation_After'Position .. Data'First + (Layout.Generation_After'Position + Layout.Generation_After'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return CW.Raw_Optional_Hash is
      Layout : CW.Raw_Optional_Hash;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Present'Position .. Data'First + (Layout.Present'Position + Layout.Present'Size / System.Storage_Unit - 1)))),
         Value => Load (Data (Data'First + Layout.Value'Position .. Data'First + (Layout.Value'Position + Layout.Value'Size / System.Storage_Unit - 1))));
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
      Layout : CW.Raw_Optional_Counter;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Present'Position .. Data'First + (Layout.Present'Position + Layout.Present'Size / System.Storage_Unit - 1)))),
         Value_LE => Load (Data (Data'First + Layout.Value_LE'Position .. Data'First + (Layout.Value_LE'Position + Layout.Value_LE'Size / System.Storage_Unit - 1))));
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
      Layout : CX.Raw_Material;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Worker_Issued => Load (Data (Data'First + Layout.Worker_Issued'Position .. Data'First + (Layout.Worker_Issued'Position + Layout.Worker_Issued'Size / System.Storage_Unit - 1))),
         Worker_Recovered => Load (Data (Data'First + Layout.Worker_Recovered'Position .. Data'First + (Layout.Worker_Recovered'Position + Layout.Worker_Recovered'Size / System.Storage_Unit - 1))),
         Canonical_Issued => Load (Data (Data'First + Layout.Canonical_Issued'Position .. Data'First + (Layout.Canonical_Issued'Position + Layout.Canonical_Issued'Size / System.Storage_Unit - 1))),
         Canonical_Recovered => Load (Data (Data'First + Layout.Canonical_Recovered'Position .. Data'First + (Layout.Canonical_Recovered'Position + Layout.Canonical_Recovered'Size / System.Storage_Unit - 1))),
         Worker_Native => Load (Data (Data'First + Layout.Worker_Native'Position .. Data'First + (Layout.Worker_Native'Position + Layout.Worker_Native'Size / System.Storage_Unit - 1))),
         Canonical_Native => Load (Data (Data'First + Layout.Canonical_Native'Position .. Data'First + (Layout.Canonical_Native'Position + Layout.Canonical_Native'Size / System.Storage_Unit - 1))),
         Worker_Receipt_Genesis => Load (Data (Data'First + Layout.Worker_Receipt_Genesis'Position .. Data'First + (Layout.Worker_Receipt_Genesis'Position + Layout.Worker_Receipt_Genesis'Size / System.Storage_Unit - 1))),
         Owner_Receipt_Genesis => Load (Data (Data'First + Layout.Owner_Receipt_Genesis'Position .. Data'First + (Layout.Owner_Receipt_Genesis'Position + Layout.Owner_Receipt_Genesis'Size / System.Storage_Unit - 1))),
         Worker_Receipt_Head => Load (Data (Data'First + Layout.Worker_Receipt_Head'Position .. Data'First + (Layout.Worker_Receipt_Head'Position + Layout.Worker_Receipt_Head'Size / System.Storage_Unit - 1))),
         Worker_Causal_Genesis => Load (Data (Data'First + Layout.Worker_Causal_Genesis'Position .. Data'First + (Layout.Worker_Causal_Genesis'Position + Layout.Worker_Causal_Genesis'Size / System.Storage_Unit - 1))),
         Owner_Causal_Genesis => Load (Data (Data'First + Layout.Owner_Causal_Genesis'Position .. Data'First + (Layout.Owner_Causal_Genesis'Position + Layout.Owner_Causal_Genesis'Size / System.Storage_Unit - 1))),
         Worker_Causal_Head => Load (Data (Data'First + Layout.Worker_Causal_Head'Position .. Data'First + (Layout.Worker_Causal_Head'Position + Layout.Worker_Causal_Head'Size / System.Storage_Unit - 1))),
         Quarantine_Head => Load (Data (Data'First + Layout.Quarantine_Head'Position .. Data'First + (Layout.Quarantine_Head'Position + Layout.Quarantine_Head'Size / System.Storage_Unit - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return HC.Raw_Result is
      Layout : HC.Raw_Result;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Disposition => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Disposition'Position .. Data'First + (Layout.Disposition'Position + Layout.Disposition'Size / System.Storage_Unit - 1)))));
   end Load;
   function Load (Data : Q.Byte_Array) return CX.Raw_Result is
      Layout : CX.Raw_Result;
      pragma Unused (Layout); --  Static layout witness; no value is read.
   begin
      return
        (Disposition => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + Layout.Disposition'Position .. Data'First + (Layout.Disposition'Position + Layout.Disposition'Size / System.Storage_Unit - 1)))));
   end Load;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : D.Raw_Packet) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Ledger'Position .. Data'First + (Raw.Ledger'Position + Raw.Ledger'Size / System.Storage_Unit - 1)), Raw.Ledger)
        and then Source_Padding_Valid (Data (Data'First + Raw.Captured'Position .. Data'First + (Raw.Captured'Position + Raw.Captured'Size / System.Storage_Unit - 1)), Raw.Captured);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Packet) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Schema_Version'Position, Raw.Schema_Version'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Before_State'Position, Raw.Before_State'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Proposed_State'Position, Raw.Proposed_State'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Current'Position, Raw.Current'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Request'Position, Raw.Request'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Before_State'Position .. Data'First + (Raw.Before_State'Position + Raw.Before_State'Size / System.Storage_Unit - 1)), Raw.Before_State)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proposed_State'Position .. Data'First + (Raw.Proposed_State'Position + Raw.Proposed_State'Size / System.Storage_Unit - 1)), Raw.Proposed_State)
        and then Source_Padding_Valid (Data (Data'First + Raw.Current'Position .. Data'First + (Raw.Current'Position + Raw.Current'Size / System.Storage_Unit - 1)), Raw.Current)
        and then Source_Padding_Valid (Data (Data'First + Raw.Request'Position .. Data'First + (Raw.Request'Position + Raw.Request'Size / System.Storage_Unit - 1)), Raw.Request);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_State) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Current'Position .. Data'First + (Raw.Current'Position + Raw.Current'Size / System.Storage_Unit - 1)), Raw.Current)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource_Epoch'Position .. Data'First + (Raw.Resource_Epoch'Position + Raw.Resource_Epoch'Size / System.Storage_Unit - 1)), Raw.Resource_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Universe_Head'Position .. Data'First + (Raw.Universe_Head'Position + Raw.Universe_Head'Size / System.Storage_Unit - 1)), Raw.Universe_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Ledger_Head'Position .. Data'First + (Raw.Ledger_Head'Position + Raw.Ledger_Head'Size / System.Storage_Unit - 1)), Raw.Ledger_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.History_Head'Position .. Data'First + (Raw.History_Head'Position + Raw.History_Head'Size / System.Storage_Unit - 1)), Raw.History_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Physical_Head'Position .. Data'First + (Raw.Physical_Head'Position + Raw.Physical_Head'Size / System.Storage_Unit - 1)), Raw.Physical_Head);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Context) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Universe'Position .. Data'First + (Raw.Universe'Position + Raw.Universe'Size / System.Storage_Unit - 1)), Raw.Universe)
        and then Source_Padding_Valid (Data (Data'First + Raw.Policy'Position .. Data'First + (Raw.Policy'Position + Raw.Policy'Size / System.Storage_Unit - 1)), Raw.Policy)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource'Position .. Data'First + (Raw.Resource'Position + Raw.Resource'Size / System.Storage_Unit - 1)), Raw.Resource)
        and then Source_Padding_Valid (Data (Data'First + Raw.Unit'Position .. Data'First + (Raw.Unit'Position + Raw.Unit'Size / System.Storage_Unit - 1)), Raw.Unit)
        and then Source_Padding_Valid (Data (Data'First + Raw.Instance'Position .. Data'First + (Raw.Instance'Position + Raw.Instance'Size / System.Storage_Unit - 1)), Raw.Instance)
        and then Source_Padding_Valid (Data (Data'First + Raw.Host'Position .. Data'First + (Raw.Host'Position + Raw.Host'Size / System.Storage_Unit - 1)), Raw.Host)
        and then Source_Padding_Valid (Data (Data'First + Raw.Boot'Position .. Data'First + (Raw.Boot'Position + Raw.Boot'Size / System.Storage_Unit - 1)), Raw.Boot)
        and then Source_Padding_Valid (Data (Data'First + Raw.Authority'Position .. Data'First + (Raw.Authority'Position + Raw.Authority'Size / System.Storage_Unit - 1)), Raw.Authority)
        and then Source_Padding_Valid (Data (Data'First + Raw.Policy_Epoch'Position .. Data'First + (Raw.Policy_Epoch'Position + Raw.Policy_Epoch'Size / System.Storage_Unit - 1)), Raw.Policy_Epoch);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Id) return Boolean is
      pragma Unreferenced (Raw);
      Layout : constant W.Raw_Id := (Present => 0, First => 0, Length => 0);
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Layout.Present'Position, Layout.Present'Size / System.Storage_Unit) or else In_Field (Offset, Layout.First'Position, Layout.First'Size / System.Storage_Unit) or else In_Field (Offset, Layout.Length'Position, Layout.Length'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
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
            if not (In_Field (Offset, Raw.Present'Position, Raw.Present'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Value'Position, Raw.Value'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Value'Position .. Data'First + (Raw.Value'Position + Raw.Value'Size / System.Storage_Unit - 1)), Raw.Value);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Quantity) return Boolean is
      pragma Unreferenced (Raw);
      Layout : constant W.Raw_Quantity := (Negative => 0, First => 0, Length => 0);
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Layout.Negative'Position, Layout.Negative'Size / System.Storage_Unit) or else In_Field (Offset, Layout.First'Position, Layout.First'Size / System.Storage_Unit) or else In_Field (Offset, Layout.Length'Position, Layout.Length'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Current_Observation) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Scope'Position .. Data'First + (Raw.Scope'Position + Raw.Scope'Size / System.Storage_Unit - 1)), Raw.Scope)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource_Epoch'Position .. Data'First + (Raw.Resource_Epoch'Position + Raw.Resource_Epoch'Size / System.Storage_Unit - 1)), Raw.Resource_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Universe_Head'Position .. Data'First + (Raw.Universe_Head'Position + Raw.Universe_Head'Size / System.Storage_Unit - 1)), Raw.Universe_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Ledger_Head'Position .. Data'First + (Raw.Ledger_Head'Position + Raw.Ledger_Head'Size / System.Storage_Unit - 1)), Raw.Ledger_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.History_Head'Position .. Data'First + (Raw.History_Head'Position + Raw.History_Head'Size / System.Storage_Unit - 1)), Raw.History_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Physical_Head'Position .. Data'First + (Raw.Physical_Head'Position + Raw.Physical_Head'Size / System.Storage_Unit - 1)), Raw.Physical_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Store_Genesis'Position .. Data'First + (Raw.Store_Genesis'Position + Raw.Store_Genesis'Size / System.Storage_Unit - 1)), Raw.Store_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Store_Id'Position .. Data'First + (Raw.Store_Id'Position + Raw.Store_Id'Size / System.Storage_Unit - 1)), Raw.Store_Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Root_Head'Position .. Data'First + (Raw.Root_Head'Position + Raw.Root_Head'Size / System.Storage_Unit - 1)), Raw.Root_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Prime'Position .. Data'First + (Raw.Prime'Position + Raw.Prime'Size / System.Storage_Unit - 1)), Raw.Prime)
        and then Source_Padding_Valid (Data (Data'First + Raw.Root_Count'Position .. Data'First + (Raw.Root_Count'Position + Raw.Root_Count'Size / System.Storage_Unit - 1)), Raw.Root_Count)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cause'Position .. Data'First + (Raw.Cause'Position + Raw.Cause'Size / System.Storage_Unit - 1)), Raw.Cause)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester'Position .. Data'First + (Raw.Requester'Position + Raw.Requester'Size / System.Storage_Unit - 1)), Raw.Requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.Receipt'Position .. Data'First + (Raw.Receipt'Position + Raw.Receipt'Size / System.Storage_Unit - 1)), Raw.Receipt)
        and then Source_Padding_Valid (Data (Data'First + Raw.Catalogue_Head'Position .. Data'First + (Raw.Catalogue_Head'Position + Raw.Catalogue_Head'Size / System.Storage_Unit - 1)), Raw.Catalogue_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Observation_Head'Position .. Data'First + (Raw.Observation_Head'Position + Raw.Observation_Head'Size / System.Storage_Unit - 1)), Raw.Observation_Head);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Intent) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Kind'Position, Raw.Kind'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Original'Position, Raw.Original'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Expected_Epoch'Position, Raw.Expected_Epoch'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Expected_Ledger_Head'Position, Raw.Expected_Ledger_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Request_Id'Position, Raw.Request_Id'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Cause'Position, Raw.Cause'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Requester'Position, Raw.Requester'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Receipt'Position, Raw.Receipt'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Original'Position .. Data'First + (Raw.Original'Position + Raw.Original'Size / System.Storage_Unit - 1)), Raw.Original)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Epoch'Position .. Data'First + (Raw.Expected_Epoch'Position + Raw.Expected_Epoch'Size / System.Storage_Unit - 1)), Raw.Expected_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Ledger_Head'Position .. Data'First + (Raw.Expected_Ledger_Head'Position + Raw.Expected_Ledger_Head'Size / System.Storage_Unit - 1)), Raw.Expected_Ledger_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Request_Id'Position .. Data'First + (Raw.Request_Id'Position + Raw.Request_Id'Size / System.Storage_Unit - 1)), Raw.Request_Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cause'Position .. Data'First + (Raw.Cause'Position + Raw.Cause'Size / System.Storage_Unit - 1)), Raw.Cause)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester'Position .. Data'First + (Raw.Requester'Position + Raw.Requester'Size / System.Storage_Unit - 1)), Raw.Requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.Receipt'Position .. Data'First + (Raw.Receipt'Position + Raw.Receipt'Size / System.Storage_Unit - 1)), Raw.Receipt);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Request) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Kind'Position, Raw.Kind'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Scope'Position, Raw.Scope'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Expected_Epoch'Position, Raw.Expected_Epoch'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Expected_Ledger_Head'Position, Raw.Expected_Ledger_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Request_Id'Position, Raw.Request_Id'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Reservation'Position, Raw.Reservation'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Operation_Id'Position, Raw.Operation_Id'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Requester'Position, Raw.Requester'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Bound'Position, Raw.Bound'Size / System.Storage_Unit) or else In_Field (Offset, Raw.New_Row'Position, Raw.New_Row'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Scope'Position .. Data'First + (Raw.Scope'Position + Raw.Scope'Size / System.Storage_Unit - 1)), Raw.Scope)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Epoch'Position .. Data'First + (Raw.Expected_Epoch'Position + Raw.Expected_Epoch'Size / System.Storage_Unit - 1)), Raw.Expected_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Ledger_Head'Position .. Data'First + (Raw.Expected_Ledger_Head'Position + Raw.Expected_Ledger_Head'Size / System.Storage_Unit - 1)), Raw.Expected_Ledger_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Request_Id'Position .. Data'First + (Raw.Request_Id'Position + Raw.Request_Id'Size / System.Storage_Unit - 1)), Raw.Request_Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Reservation'Position .. Data'First + (Raw.Reservation'Position + Raw.Reservation'Size / System.Storage_Unit - 1)), Raw.Reservation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Operation_Id'Position .. Data'First + (Raw.Operation_Id'Position + Raw.Operation_Id'Size / System.Storage_Unit - 1)), Raw.Operation_Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester'Position .. Data'First + (Raw.Requester'Position + Raw.Requester'Size / System.Storage_Unit - 1)), Raw.Requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + (Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1)), Raw.Bound)
        and then Source_Padding_Valid (Data (Data'First + Raw.New_Row'Position .. Data'First + (Raw.New_Row'Position + Raw.New_Row'Size / System.Storage_Unit - 1)), Raw.New_Row);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Binding) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Reservation'Position .. Data'First + (Raw.Reservation'Position + Raw.Reservation'Size / System.Storage_Unit - 1)), Raw.Reservation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Operation'Position .. Data'First + (Raw.Operation'Position + Raw.Operation'Size / System.Storage_Unit - 1)), Raw.Operation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner'Position .. Data'First + (Raw.Owner'Position + Raw.Owner'Size / System.Storage_Unit - 1)), Raw.Owner)
        and then Source_Padding_Valid (Data (Data'First + Raw.Workload'Position .. Data'First + (Raw.Workload'Position + Raw.Workload'Size / System.Storage_Unit - 1)), Raw.Workload)
        and then Source_Padding_Valid (Data (Data'First + Raw.Universe_Head'Position .. Data'First + (Raw.Universe_Head'Position + Raw.Universe_Head'Size / System.Storage_Unit - 1)), Raw.Universe_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Capability'Position .. Data'First + (Raw.Capability'Position + Raw.Capability'Size / System.Storage_Unit - 1)), Raw.Capability)
        and then Source_Padding_Valid (Data (Data'First + Raw.Grant_Use'Position .. Data'First + (Raw.Grant_Use'Position + Raw.Grant_Use'Size / System.Storage_Unit - 1)), Raw.Grant_Use)
        and then Source_Padding_Valid (Data (Data'First + Raw.Payload'Position .. Data'First + (Raw.Payload'Position + Raw.Payload'Size / System.Storage_Unit - 1)), Raw.Payload)
        and then Source_Padding_Valid (Data (Data'First + Raw.Provenance'Position .. Data'First + (Raw.Provenance'Position + Raw.Provenance'Size / System.Storage_Unit - 1)), Raw.Provenance)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource_Epoch'Position .. Data'First + (Raw.Resource_Epoch'Position + Raw.Resource_Epoch'Size / System.Storage_Unit - 1)), Raw.Resource_Epoch);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Row) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Scope'Position, Raw.Scope'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Bound'Position, Raw.Bound'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Parent'Position, Raw.Parent'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Kind'Position, Raw.Kind'Size / System.Storage_Unit) or else In_Field (Offset, Raw.State'Position, Raw.State'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Amount'Position, Raw.Amount'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Observed_Usage'Position, Raw.Observed_Usage'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Planned_Unit'Position, Raw.Planned_Unit'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Actual_Unit'Position, Raw.Actual_Unit'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Cgroup'Position, Raw.Cgroup'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Invocation'Position, Raw.Invocation'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Scope'Position .. Data'First + (Raw.Scope'Position + Raw.Scope'Size / System.Storage_Unit - 1)), Raw.Scope)
        and then Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + (Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1)), Raw.Bound)
        and then Source_Padding_Valid (Data (Data'First + Raw.Parent'Position .. Data'First + (Raw.Parent'Position + Raw.Parent'Size / System.Storage_Unit - 1)), Raw.Parent)
        and then Source_Padding_Valid (Data (Data'First + Raw.Amount'Position .. Data'First + (Raw.Amount'Position + Raw.Amount'Size / System.Storage_Unit - 1)), Raw.Amount)
        and then Source_Padding_Valid (Data (Data'First + Raw.Observed_Usage'Position .. Data'First + (Raw.Observed_Usage'Position + Raw.Observed_Usage'Size / System.Storage_Unit - 1)), Raw.Observed_Usage)
        and then Source_Padding_Valid (Data (Data'First + Raw.Planned_Unit'Position .. Data'First + (Raw.Planned_Unit'Position + Raw.Planned_Unit'Size / System.Storage_Unit - 1)), Raw.Planned_Unit)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Unit'Position .. Data'First + (Raw.Actual_Unit'Position + Raw.Actual_Unit'Size / System.Storage_Unit - 1)), Raw.Actual_Unit)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cgroup'Position .. Data'First + (Raw.Cgroup'Position + Raw.Cgroup'Size / System.Storage_Unit - 1)), Raw.Cgroup)
        and then Source_Padding_Valid (Data (Data'First + Raw.Invocation'Position .. Data'First + (Raw.Invocation'Position + Raw.Invocation'Size / System.Storage_Unit - 1)), Raw.Invocation);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : D.Raw_Observation) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + (Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1)), Raw.Bound)
        and then Source_Padding_Valid (Data (Data'First + Raw.Raw_Frame'Position .. Data'First + (Raw.Raw_Frame'Position + Raw.Raw_Frame'Size / System.Storage_Unit - 1)), Raw.Raw_Frame)
        and then Source_Padding_Valid (Data (Data'First + Raw.Raw_Sender'Position .. Data'First + (Raw.Raw_Sender'Position + Raw.Raw_Sender'Size / System.Storage_Unit - 1)), Raw.Raw_Sender)
        and then Source_Padding_Valid (Data (Data'First + Raw.Ticket'Position .. Data'First + (Raw.Ticket'Position + Raw.Ticket'Size / System.Storage_Unit - 1)), Raw.Ticket)
        and then Source_Padding_Valid (Data (Data'First + Raw.Raw_Proc_Status'Position .. Data'First + (Raw.Raw_Proc_Status'Position + Raw.Raw_Proc_Status'Size / System.Storage_Unit - 1)), Raw.Raw_Proc_Status)
        and then Source_Padding_Valid (Data (Data'First + Raw.Raw_Proc_Cgroup'Position .. Data'First + (Raw.Raw_Proc_Cgroup'Position + Raw.Raw_Proc_Cgroup'Size / System.Storage_Unit - 1)), Raw.Raw_Proc_Cgroup)
        and then Source_Padding_Valid (Data (Data'First + Raw.Raw_Proc_Maps'Position .. Data'First + (Raw.Raw_Proc_Maps'Position + Raw.Raw_Proc_Maps'Size / System.Storage_Unit - 1)), Raw.Raw_Proc_Maps)
        and then Source_Padding_Valid (Data (Data'First + Raw.Raw_Proc_Cmdline'Position .. Data'First + (Raw.Raw_Proc_Cmdline'Position + Raw.Raw_Proc_Cmdline'Size / System.Storage_Unit - 1)), Raw.Raw_Proc_Cmdline)
        and then Source_Padding_Valid (Data (Data'First + Raw.Raw_Pidfd_Info'Position .. Data'First + (Raw.Raw_Pidfd_Info'Position + Raw.Raw_Pidfd_Info'Size / System.Storage_Unit - 1)), Raw.Raw_Pidfd_Info)
        and then Source_Padding_Valid (Data (Data'First + Raw.Namespace'Position .. Data'First + (Raw.Namespace'Position + Raw.Namespace'Size / System.Storage_Unit - 1)), Raw.Namespace)
        and then Source_Padding_Valid (Data (Data'First + Raw.Held_Namespace'Position .. Data'First + (Raw.Held_Namespace'Position + Raw.Held_Namespace'Size / System.Storage_Unit - 1)), Raw.Held_Namespace)
        and then Source_Padding_Valid (Data (Data'First + Raw.Helper_Image'Position .. Data'First + (Raw.Helper_Image'Position + Raw.Helper_Image'Size / System.Storage_Unit - 1)), Raw.Helper_Image)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Helper_Image'Position .. Data'First + (Raw.Expected_Helper_Image'Position + Raw.Expected_Helper_Image'Size / System.Storage_Unit - 1)), Raw.Expected_Helper_Image)
        and then Source_Padding_Valid (Data (Data'First + Raw.Executable_Plan'Position .. Data'First + (Raw.Executable_Plan'Position + Raw.Executable_Plan'Size / System.Storage_Unit - 1)), Raw.Executable_Plan)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Executable_Plan'Position .. Data'First + (Raw.Expected_Executable_Plan'Position + Raw.Expected_Executable_Plan'Size / System.Storage_Unit - 1)), Raw.Expected_Executable_Plan)
        and then Source_Padding_Valid (Data (Data'First + Raw.Original_Requester'Position .. Data'First + (Raw.Original_Requester'Position + Raw.Original_Requester'Size / System.Storage_Unit - 1)), Raw.Original_Requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester_Credentials'Position .. Data'First + (Raw.Requester_Credentials'Position + Raw.Requester_Credentials'Size / System.Storage_Unit - 1)), Raw.Requester_Credentials)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Requester_Credentials'Position .. Data'First + (Raw.Expected_Requester_Credentials'Position + Raw.Expected_Requester_Credentials'Size / System.Storage_Unit - 1)), Raw.Expected_Requester_Credentials)
        and then Source_Padding_Valid (Data (Data'First + Raw.Dispatch'Position .. Data'First + (Raw.Dispatch'Position + Raw.Dispatch'Size / System.Storage_Unit - 1)), Raw.Dispatch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Running_Event'Position .. Data'First + (Raw.Running_Event'Position + Raw.Running_Event'Size / System.Storage_Unit - 1)), Raw.Running_Event)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Running_Event'Position .. Data'First + (Raw.Expected_Running_Event'Position + Raw.Expected_Running_Event'Size / System.Storage_Unit - 1)), Raw.Expected_Running_Event)
        and then Source_Padding_Valid (Data (Data'First + Raw.Canonical_Use_Event'Position .. Data'First + (Raw.Canonical_Use_Event'Position + Raw.Canonical_Use_Event'Size / System.Storage_Unit - 1)), Raw.Canonical_Use_Event)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Canonical_Use_Event'Position .. Data'First + (Raw.Expected_Canonical_Use_Event'Position + Raw.Expected_Canonical_Use_Event'Size / System.Storage_Unit - 1)), Raw.Expected_Canonical_Use_Event)
        and then Source_Padding_Valid (Data (Data'First + Raw.Store_Genesis'Position .. Data'First + (Raw.Store_Genesis'Position + Raw.Store_Genesis'Size / System.Storage_Unit - 1)), Raw.Store_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Store_Genesis'Position .. Data'First + (Raw.Expected_Store_Genesis'Position + Raw.Expected_Store_Genesis'Size / System.Storage_Unit - 1)), Raw.Expected_Store_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Source_Lease'Position .. Data'First + (Raw.Source_Lease'Position + Raw.Source_Lease'Size / System.Storage_Unit - 1)), Raw.Source_Lease)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Source_Lease'Position .. Data'First + (Raw.Expected_Source_Lease'Position + Raw.Expected_Source_Lease'Size / System.Storage_Unit - 1)), Raw.Expected_Source_Lease)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actor_Wait'Position .. Data'First + (Raw.Actor_Wait'Position + Raw.Actor_Wait'Size / System.Storage_Unit - 1)), Raw.Actor_Wait)
        and then Source_Padding_Valid (Data (Data'First + Raw.Helper_Wait'Position .. Data'First + (Raw.Helper_Wait'Position + Raw.Helper_Wait'Size / System.Storage_Unit - 1)), Raw.Helper_Wait)
        and then Source_Padding_Valid (Data (Data'First + Raw.Namespace_Wait'Position .. Data'First + (Raw.Namespace_Wait'Position + Raw.Namespace_Wait'Size / System.Storage_Unit - 1)), Raw.Namespace_Wait)
        and then Source_Padding_Valid (Data (Data'First + Raw.Host_Pid'Position .. Data'First + (Raw.Host_Pid'Position + Raw.Host_Pid'Size / System.Storage_Unit - 1)), Raw.Host_Pid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Namespace_Pid'Position .. Data'First + (Raw.Namespace_Pid'Position + Raw.Namespace_Pid'Size / System.Storage_Unit - 1)), Raw.Namespace_Pid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Sender_Uid'Position .. Data'First + (Raw.Sender_Uid'Position + Raw.Sender_Uid'Size / System.Storage_Unit - 1)), Raw.Sender_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Sender_Gid'Position .. Data'First + (Raw.Sender_Gid'Position + Raw.Sender_Gid'Size / System.Storage_Unit - 1)), Raw.Sender_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Real_Uid'Position .. Data'First + (Raw.Real_Uid'Position + Raw.Real_Uid'Size / System.Storage_Unit - 1)), Raw.Real_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Effective_Uid'Position .. Data'First + (Raw.Effective_Uid'Position + Raw.Effective_Uid'Size / System.Storage_Unit - 1)), Raw.Effective_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Saved_Uid'Position .. Data'First + (Raw.Saved_Uid'Position + Raw.Saved_Uid'Size / System.Storage_Unit - 1)), Raw.Saved_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Real_Gid'Position .. Data'First + (Raw.Real_Gid'Position + Raw.Real_Gid'Size / System.Storage_Unit - 1)), Raw.Real_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Effective_Gid'Position .. Data'First + (Raw.Effective_Gid'Position + Raw.Effective_Gid'Size / System.Storage_Unit - 1)), Raw.Effective_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Saved_Gid'Position .. Data'First + (Raw.Saved_Gid'Position + Raw.Saved_Gid'Size / System.Storage_Unit - 1)), Raw.Saved_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Capability_Version'Position .. Data'First + (Raw.Capability_Version'Position + Raw.Capability_Version'Size / System.Storage_Unit - 1)), Raw.Capability_Version)
        and then Source_Padding_Valid (Data (Data'First + Raw.Effective_Low'Position .. Data'First + (Raw.Effective_Low'Position + Raw.Effective_Low'Size / System.Storage_Unit - 1)), Raw.Effective_Low)
        and then Source_Padding_Valid (Data (Data'First + Raw.Permitted_Low'Position .. Data'First + (Raw.Permitted_Low'Position + Raw.Permitted_Low'Size / System.Storage_Unit - 1)), Raw.Permitted_Low)
        and then Source_Padding_Valid (Data (Data'First + Raw.Inheritable_Low'Position .. Data'First + (Raw.Inheritable_Low'Position + Raw.Inheritable_Low'Size / System.Storage_Unit - 1)), Raw.Inheritable_Low)
        and then Source_Padding_Valid (Data (Data'First + Raw.Effective_High'Position .. Data'First + (Raw.Effective_High'Position + Raw.Effective_High'Size / System.Storage_Unit - 1)), Raw.Effective_High)
        and then Source_Padding_Valid (Data (Data'First + Raw.Permitted_High'Position .. Data'First + (Raw.Permitted_High'Position + Raw.Permitted_High'Size / System.Storage_Unit - 1)), Raw.Permitted_High)
        and then Source_Padding_Valid (Data (Data'First + Raw.Inheritable_High'Position .. Data'First + (Raw.Inheritable_High'Position + Raw.Inheritable_High'Size / System.Storage_Unit - 1)), Raw.Inheritable_High)
        and then Source_Padding_Valid (Data (Data'First + Raw.Securebits'Position .. Data'First + (Raw.Securebits'Position + Raw.Securebits'Size / System.Storage_Unit - 1)), Raw.Securebits)
        and then Source_Padding_Valid (Data (Data'First + Raw.No_New_Privs'Position .. Data'First + (Raw.No_New_Privs'Position + Raw.No_New_Privs'Size / System.Storage_Unit - 1)), Raw.No_New_Privs)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester_Uid'Position .. Data'First + (Raw.Requester_Uid'Position + Raw.Requester_Uid'Size / System.Storage_Unit - 1)), Raw.Requester_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester_Gid'Position .. Data'First + (Raw.Requester_Gid'Position + Raw.Requester_Gid'Size / System.Storage_Unit - 1)), Raw.Requester_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Configured_Requester_Uid'Position .. Data'First + (Raw.Configured_Requester_Uid'Position + Raw.Configured_Requester_Uid'Size / System.Storage_Unit - 1)), Raw.Configured_Requester_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Workload_Uid'Position .. Data'First + (Raw.Workload_Uid'Position + Raw.Workload_Uid'Size / System.Storage_Unit - 1)), Raw.Workload_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Workload_Gid'Position .. Data'First + (Raw.Workload_Gid'Position + Raw.Workload_Gid'Size / System.Storage_Unit - 1)), Raw.Workload_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Host_Pid'Position .. Data'First + (Raw.Proc_Host_Pid'Position + Raw.Proc_Host_Pid'Size / System.Storage_Unit - 1)), Raw.Proc_Host_Pid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Namespace_Pid'Position .. Data'First + (Raw.Proc_Namespace_Pid'Position + Raw.Proc_Namespace_Pid'Size / System.Storage_Unit - 1)), Raw.Proc_Namespace_Pid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Real_Uid'Position .. Data'First + (Raw.Proc_Real_Uid'Position + Raw.Proc_Real_Uid'Size / System.Storage_Unit - 1)), Raw.Proc_Real_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Effective_Uid'Position .. Data'First + (Raw.Proc_Effective_Uid'Position + Raw.Proc_Effective_Uid'Size / System.Storage_Unit - 1)), Raw.Proc_Effective_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Saved_Uid'Position .. Data'First + (Raw.Proc_Saved_Uid'Position + Raw.Proc_Saved_Uid'Size / System.Storage_Unit - 1)), Raw.Proc_Saved_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Real_Gid'Position .. Data'First + (Raw.Proc_Real_Gid'Position + Raw.Proc_Real_Gid'Size / System.Storage_Unit - 1)), Raw.Proc_Real_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Effective_Gid'Position .. Data'First + (Raw.Proc_Effective_Gid'Position + Raw.Proc_Effective_Gid'Size / System.Storage_Unit - 1)), Raw.Proc_Effective_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Saved_Gid'Position .. Data'First + (Raw.Proc_Saved_Gid'Position + Raw.Proc_Saved_Gid'Size / System.Storage_Unit - 1)), Raw.Proc_Saved_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Effective'Position .. Data'First + (Raw.Proc_Effective'Position + Raw.Proc_Effective'Size / System.Storage_Unit - 1)), Raw.Proc_Effective)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Permitted'Position .. Data'First + (Raw.Proc_Permitted'Position + Raw.Proc_Permitted'Size / System.Storage_Unit - 1)), Raw.Proc_Permitted)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Inheritable'Position .. Data'First + (Raw.Proc_Inheritable'Position + Raw.Proc_Inheritable'Size / System.Storage_Unit - 1)), Raw.Proc_Inheritable)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Bounding'Position .. Data'First + (Raw.Proc_Bounding'Position + Raw.Proc_Bounding'Size / System.Storage_Unit - 1)), Raw.Proc_Bounding)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Ambient'Position .. Data'First + (Raw.Proc_Ambient'Position + Raw.Proc_Ambient'Size / System.Storage_Unit - 1)), Raw.Proc_Ambient)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_No_New_Privs'Position .. Data'First + (Raw.Proc_No_New_Privs'Position + Raw.Proc_No_New_Privs'Size / System.Storage_Unit - 1)), Raw.Proc_No_New_Privs)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Fs_Uid'Position .. Data'First + (Raw.Proc_Fs_Uid'Position + Raw.Proc_Fs_Uid'Size / System.Storage_Unit - 1)), Raw.Proc_Fs_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Proc_Fs_Gid'Position .. Data'First + (Raw.Proc_Fs_Gid'Position + Raw.Proc_Fs_Gid'Size / System.Storage_Unit - 1)), Raw.Proc_Fs_Gid);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : X.Raw_Crosswalk) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Resource_Current'Position, Raw.Resource_Current'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Operation_Policy'Position, Raw.Operation_Policy'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Operation_Root_Set'Position, Raw.Operation_Root_Set'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Owner_Genesis'Position, Raw.Owner_Genesis'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Installation'Position, Raw.Installation'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Gate_Config'Position, Raw.Gate_Config'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Managed_Observation'Position, Raw.Managed_Observation'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Original_Grant'Position, Raw.Original_Grant'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Complete_Crosswalk'Position, Raw.Complete_Crosswalk'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Current_Source'Position, Raw.Current_Source'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Original_Request'Position, Raw.Original_Request'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Original_Requester'Position, Raw.Original_Requester'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Original_Transaction'Position, Raw.Original_Transaction'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Preparer'Position, Raw.Preparer'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Selected_Plan'Position, Raw.Selected_Plan'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Resource_Current'Position .. Data'First + (Raw.Resource_Current'Position + Raw.Resource_Current'Size / System.Storage_Unit - 1)), Raw.Resource_Current)
        and then Source_Padding_Valid (Data (Data'First + Raw.Operation_Policy'Position .. Data'First + (Raw.Operation_Policy'Position + Raw.Operation_Policy'Size / System.Storage_Unit - 1)), Raw.Operation_Policy)
        and then Source_Padding_Valid (Data (Data'First + Raw.Operation_Root_Set'Position .. Data'First + (Raw.Operation_Root_Set'Position + Raw.Operation_Root_Set'Size / System.Storage_Unit - 1)), Raw.Operation_Root_Set)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner_Genesis'Position .. Data'First + (Raw.Owner_Genesis'Position + Raw.Owner_Genesis'Size / System.Storage_Unit - 1)), Raw.Owner_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Installation'Position .. Data'First + (Raw.Installation'Position + Raw.Installation'Size / System.Storage_Unit - 1)), Raw.Installation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Gate_Config'Position .. Data'First + (Raw.Gate_Config'Position + Raw.Gate_Config'Size / System.Storage_Unit - 1)), Raw.Gate_Config)
        and then Source_Padding_Valid (Data (Data'First + Raw.Managed_Observation'Position .. Data'First + (Raw.Managed_Observation'Position + Raw.Managed_Observation'Size / System.Storage_Unit - 1)), Raw.Managed_Observation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Original_Grant'Position .. Data'First + (Raw.Original_Grant'Position + Raw.Original_Grant'Size / System.Storage_Unit - 1)), Raw.Original_Grant)
        and then Source_Padding_Valid (Data (Data'First + Raw.Complete_Crosswalk'Position .. Data'First + (Raw.Complete_Crosswalk'Position + Raw.Complete_Crosswalk'Size / System.Storage_Unit - 1)), Raw.Complete_Crosswalk)
        and then Source_Padding_Valid (Data (Data'First + Raw.Current_Source'Position .. Data'First + (Raw.Current_Source'Position + Raw.Current_Source'Size / System.Storage_Unit - 1)), Raw.Current_Source)
        and then Source_Padding_Valid (Data (Data'First + Raw.Original_Request'Position .. Data'First + (Raw.Original_Request'Position + Raw.Original_Request'Size / System.Storage_Unit - 1)), Raw.Original_Request)
        and then Source_Padding_Valid (Data (Data'First + Raw.Original_Requester'Position .. Data'First + (Raw.Original_Requester'Position + Raw.Original_Requester'Size / System.Storage_Unit - 1)), Raw.Original_Requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.Original_Transaction'Position .. Data'First + (Raw.Original_Transaction'Position + Raw.Original_Transaction'Size / System.Storage_Unit - 1)), Raw.Original_Transaction)
        and then Source_Padding_Valid (Data (Data'First + Raw.Preparer'Position .. Data'First + (Raw.Preparer'Position + Raw.Preparer'Size / System.Storage_Unit - 1)), Raw.Preparer)
        and then Source_Padding_Valid (Data (Data'First + Raw.Selected_Plan'Position .. Data'First + (Raw.Selected_Plan'Position + Raw.Selected_Plan'Size / System.Storage_Unit - 1)), Raw.Selected_Plan);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : C.Raw_Digest) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Value'Position .. Data'First + (Raw.Value'Position + Raw.Value'Size / System.Storage_Unit - 1)), Raw.Value);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : C.Raw_Hash) return Boolean is
      pragma Unreferenced (Raw);
   begin
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : Y.Raw_Input) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Mode'Position, Raw.Mode'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Controller'Position, Raw.Controller'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Child_Task'Position, Raw.Child_Task'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Controller'Position .. Data'First + (Raw.Controller'Position + Raw.Controller'Size / System.Storage_Unit - 1)), Raw.Controller)
        and then Source_Padding_Valid (Data (Data'First + Raw.Child_Task'Position .. Data'First + (Raw.Child_Task'Position + Raw.Child_Task'Size / System.Storage_Unit - 1)), Raw.Child_Task);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : Y.Raw_Controller) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + (Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1)), Raw.Bound)
        and then Source_Padding_Valid (Data (Data'First + Raw.Process'Position .. Data'First + (Raw.Process'Position + Raw.Process'Size / System.Storage_Unit - 1)), Raw.Process)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester_Uid'Position .. Data'First + (Raw.Requester_Uid'Position + Raw.Requester_Uid'Size / System.Storage_Unit - 1)), Raw.Requester_Uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester_Gid'Position .. Data'First + (Raw.Requester_Gid'Position + Raw.Requester_Gid'Size / System.Storage_Unit - 1)), Raw.Requester_Gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_manager'Position .. Data'First + (Raw.raw_manager'Position + Raw.raw_manager'Size / System.Storage_Unit - 1)), Raw.raw_manager)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_channel'Position .. Data'First + (Raw.raw_channel'Position + Raw.raw_channel'Size / System.Storage_Unit - 1)), Raw.raw_channel)
        and then Source_Padding_Valid (Data (Data'First + Raw.owner_endpoint'Position .. Data'First + (Raw.owner_endpoint'Position + Raw.owner_endpoint'Size / System.Storage_Unit - 1)), Raw.owner_endpoint)
        and then Source_Padding_Valid (Data (Data'First + Raw.expected_owner_endpoint'Position .. Data'First + (Raw.expected_owner_endpoint'Position + Raw.expected_owner_endpoint'Size / System.Storage_Unit - 1)), Raw.expected_owner_endpoint)
        and then Source_Padding_Valid (Data (Data'First + Raw.source_lease'Position .. Data'First + (Raw.source_lease'Position + Raw.source_lease'Size / System.Storage_Unit - 1)), Raw.source_lease)
        and then Source_Padding_Valid (Data (Data'First + Raw.expected_source_lease'Position .. Data'First + (Raw.expected_source_lease'Position + Raw.expected_source_lease'Size / System.Storage_Unit - 1)), Raw.expected_source_lease)
        and then Source_Padding_Valid (Data (Data'First + Raw.worker_image'Position .. Data'First + (Raw.worker_image'Position + Raw.worker_image'Size / System.Storage_Unit - 1)), Raw.worker_image)
        and then Source_Padding_Valid (Data (Data'First + Raw.expected_worker_image'Position .. Data'First + (Raw.expected_worker_image'Position + Raw.expected_worker_image'Size / System.Storage_Unit - 1)), Raw.expected_worker_image)
        and then Source_Padding_Valid (Data (Data'First + Raw.handler_plan'Position .. Data'First + (Raw.handler_plan'Position + Raw.handler_plan'Size / System.Storage_Unit - 1)), Raw.handler_plan)
        and then Source_Padding_Valid (Data (Data'First + Raw.expected_handler_plan'Position .. Data'First + (Raw.expected_handler_plan'Position + Raw.expected_handler_plan'Size / System.Storage_Unit - 1)), Raw.expected_handler_plan)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_request'Position .. Data'First + (Raw.raw_request'Position + Raw.raw_request'Size / System.Storage_Unit - 1)), Raw.raw_request)
        and then Source_Padding_Valid (Data (Data'First + Raw.requester'Position .. Data'First + (Raw.requester'Position + Raw.requester'Size / System.Storage_Unit - 1)), Raw.requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.dispatch'Position .. Data'First + (Raw.dispatch'Position + Raw.dispatch'Size / System.Storage_Unit - 1)), Raw.dispatch)
        and then Source_Padding_Valid (Data (Data'First + Raw.running_event'Position .. Data'First + (Raw.running_event'Position + Raw.running_event'Size / System.Storage_Unit - 1)), Raw.running_event)
        and then Source_Padding_Valid (Data (Data'First + Raw.expected_running_event'Position .. Data'First + (Raw.expected_running_event'Position + Raw.expected_running_event'Size / System.Storage_Unit - 1)), Raw.expected_running_event)
        and then Source_Padding_Valid (Data (Data'First + Raw.store_genesis'Position .. Data'First + (Raw.store_genesis'Position + Raw.store_genesis'Size / System.Storage_Unit - 1)), Raw.store_genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.expected_store_genesis'Position .. Data'First + (Raw.expected_store_genesis'Position + Raw.expected_store_genesis'Size / System.Storage_Unit - 1)), Raw.expected_store_genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.current_source'Position .. Data'First + (Raw.current_source'Position + Raw.current_source'Size / System.Storage_Unit - 1)), Raw.current_source);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : Y.Raw_Process) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.raw_status'Position .. Data'First + (Raw.raw_status'Position + Raw.raw_status'Size / System.Storage_Unit - 1)), Raw.raw_status)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_stat'Position .. Data'First + (Raw.raw_stat'Position + Raw.raw_stat'Size / System.Storage_Unit - 1)), Raw.raw_stat)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_cgroup'Position .. Data'First + (Raw.raw_cgroup'Position + Raw.raw_cgroup'Size / System.Storage_Unit - 1)), Raw.raw_cgroup)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_maps'Position .. Data'First + (Raw.raw_maps'Position + Raw.raw_maps'Size / System.Storage_Unit - 1)), Raw.raw_maps)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_cmdline'Position .. Data'First + (Raw.raw_cmdline'Position + Raw.raw_cmdline'Size / System.Storage_Unit - 1)), Raw.raw_cmdline)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_pidfd_info'Position .. Data'First + (Raw.raw_pidfd_info'Position + Raw.raw_pidfd_info'Size / System.Storage_Unit - 1)), Raw.raw_pidfd_info)
        and then Source_Padding_Valid (Data (Data'First + Raw.namespace'Position .. Data'First + (Raw.namespace'Position + Raw.namespace'Size / System.Storage_Unit - 1)), Raw.namespace)
        and then Source_Padding_Valid (Data (Data'First + Raw.cgroup'Position .. Data'First + (Raw.cgroup'Position + Raw.cgroup'Size / System.Storage_Unit - 1)), Raw.cgroup)
        and then Source_Padding_Valid (Data (Data'First + Raw.actual_unit'Position .. Data'First + (Raw.actual_unit'Position + Raw.actual_unit'Size / System.Storage_Unit - 1)), Raw.actual_unit)
        and then Source_Padding_Valid (Data (Data'First + Raw.invocation'Position .. Data'First + (Raw.invocation'Position + Raw.invocation'Size / System.Storage_Unit - 1)), Raw.invocation)
        and then Source_Padding_Valid (Data (Data'First + Raw.source_lease'Position .. Data'First + (Raw.source_lease'Position + Raw.source_lease'Size / System.Storage_Unit - 1)), Raw.source_lease)
        and then Source_Padding_Valid (Data (Data'First + Raw.pidfd_wait'Position .. Data'First + (Raw.pidfd_wait'Position + Raw.pidfd_wait'Size / System.Storage_Unit - 1)), Raw.pidfd_wait)
        and then Source_Padding_Valid (Data (Data'First + Raw.host_pid'Position .. Data'First + (Raw.host_pid'Position + Raw.host_pid'Size / System.Storage_Unit - 1)), Raw.host_pid)
        and then Source_Padding_Valid (Data (Data'First + Raw.start_tick'Position .. Data'First + (Raw.start_tick'Position + Raw.start_tick'Size / System.Storage_Unit - 1)), Raw.start_tick)
        and then Source_Padding_Valid (Data (Data'First + Raw.parent_pid'Position .. Data'First + (Raw.parent_pid'Position + Raw.parent_pid'Size / System.Storage_Unit - 1)), Raw.parent_pid)
        and then Source_Padding_Valid (Data (Data'First + Raw.parent_start_tick'Position .. Data'First + (Raw.parent_start_tick'Position + Raw.parent_start_tick'Size / System.Storage_Unit - 1)), Raw.parent_start_tick)
        and then Source_Padding_Valid (Data (Data'First + Raw.real_uid'Position .. Data'First + (Raw.real_uid'Position + Raw.real_uid'Size / System.Storage_Unit - 1)), Raw.real_uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.effective_uid'Position .. Data'First + (Raw.effective_uid'Position + Raw.effective_uid'Size / System.Storage_Unit - 1)), Raw.effective_uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.saved_uid'Position .. Data'First + (Raw.saved_uid'Position + Raw.saved_uid'Size / System.Storage_Unit - 1)), Raw.saved_uid)
        and then Source_Padding_Valid (Data (Data'First + Raw.real_gid'Position .. Data'First + (Raw.real_gid'Position + Raw.real_gid'Size / System.Storage_Unit - 1)), Raw.real_gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.effective_gid'Position .. Data'First + (Raw.effective_gid'Position + Raw.effective_gid'Size / System.Storage_Unit - 1)), Raw.effective_gid)
        and then Source_Padding_Valid (Data (Data'First + Raw.saved_gid'Position .. Data'First + (Raw.saved_gid'Position + Raw.saved_gid'Size / System.Storage_Unit - 1)), Raw.saved_gid);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : Y.Raw_Task) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Action'Position, Raw.Action'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Root'Position, Raw.Root'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Child'Position, Raw.Child'Size / System.Storage_Unit) or else In_Field (Offset, Raw.task_id'Position, Raw.task_id'Size / System.Storage_Unit) or else In_Field (Offset, Raw.root_world'Position, Raw.root_world'Size / System.Storage_Unit) or else In_Field (Offset, Raw.child_world'Position, Raw.child_world'Size / System.Storage_Unit) or else In_Field (Offset, Raw.root_instance'Position, Raw.root_instance'Size / System.Storage_Unit) or else In_Field (Offset, Raw.child_instance'Position, Raw.child_instance'Size / System.Storage_Unit) or else In_Field (Offset, Raw.world_store'Position, Raw.world_store'Size / System.Storage_Unit) or else In_Field (Offset, Raw.full_world_ancestry'Position, Raw.full_world_ancestry'Size / System.Storage_Unit) or else In_Field (Offset, Raw.original_workload'Position, Raw.original_workload'Size / System.Storage_Unit) or else In_Field (Offset, Raw.sandbox'Position, Raw.sandbox'Size / System.Storage_Unit) or else In_Field (Offset, Raw.adapter'Position, Raw.adapter'Size / System.Storage_Unit) or else In_Field (Offset, Raw.context'Position, Raw.context'Size / System.Storage_Unit) or else In_Field (Offset, Raw.mission'Position, Raw.mission'Size / System.Storage_Unit) or else In_Field (Offset, Raw.stdin'Position, Raw.stdin'Size / System.Storage_Unit) or else In_Field (Offset, Raw.credential_source'Position, Raw.credential_source'Size / System.Storage_Unit) or else In_Field (Offset, Raw.executable_source'Position, Raw.executable_source'Size / System.Storage_Unit) or else In_Field (Offset, Raw.configuration'Position, Raw.configuration'Size / System.Storage_Unit) or else In_Field (Offset, Raw.owner_plan'Position, Raw.owner_plan'Size / System.Storage_Unit) or else In_Field (Offset, Raw.native_cost_input'Position, Raw.native_cost_input'Size / System.Storage_Unit) or else In_Field (Offset, Raw.raw_request'Position, Raw.raw_request'Size / System.Storage_Unit) or else In_Field (Offset, Raw.requester'Position, Raw.requester'Size / System.Storage_Unit) or else In_Field (Offset, Raw.cause'Position, Raw.cause'Size / System.Storage_Unit) or else In_Field (Offset, Raw.root_dispatch'Position, Raw.root_dispatch'Size / System.Storage_Unit) or else In_Field (Offset, Raw.root_running_event'Position, Raw.root_running_event'Size / System.Storage_Unit) or else In_Field (Offset, Raw.task_journal'Position, Raw.task_journal'Size / System.Storage_Unit) or else In_Field (Offset, Raw.task_intent'Position, Raw.task_intent'Size / System.Storage_Unit) or else In_Field (Offset, Raw.task_reservation_event'Position, Raw.task_reservation_event'Size / System.Storage_Unit) or else In_Field (Offset, Raw.task_launch_event'Position, Raw.task_launch_event'Size / System.Storage_Unit) or else In_Field (Offset, Raw.parent_namespace_source'Position, Raw.parent_namespace_source'Size / System.Storage_Unit) or else In_Field (Offset, Raw.fd_lineage'Position, Raw.fd_lineage'Size / System.Storage_Unit) or else In_Field (Offset, Raw.source_lease'Position, Raw.source_lease'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Root'Position .. Data'First + (Raw.Root'Position + Raw.Root'Size / System.Storage_Unit - 1)), Raw.Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Child'Position .. Data'First + (Raw.Child'Position + Raw.Child'Size / System.Storage_Unit - 1)), Raw.Child)
        and then Source_Padding_Valid (Data (Data'First + Raw.task_id'Position .. Data'First + (Raw.task_id'Position + Raw.task_id'Size / System.Storage_Unit - 1)), Raw.task_id)
        and then Source_Padding_Valid (Data (Data'First + Raw.root_world'Position .. Data'First + (Raw.root_world'Position + Raw.root_world'Size / System.Storage_Unit - 1)), Raw.root_world)
        and then Source_Padding_Valid (Data (Data'First + Raw.child_world'Position .. Data'First + (Raw.child_world'Position + Raw.child_world'Size / System.Storage_Unit - 1)), Raw.child_world)
        and then Source_Padding_Valid (Data (Data'First + Raw.root_instance'Position .. Data'First + (Raw.root_instance'Position + Raw.root_instance'Size / System.Storage_Unit - 1)), Raw.root_instance)
        and then Source_Padding_Valid (Data (Data'First + Raw.child_instance'Position .. Data'First + (Raw.child_instance'Position + Raw.child_instance'Size / System.Storage_Unit - 1)), Raw.child_instance)
        and then Source_Padding_Valid (Data (Data'First + Raw.world_store'Position .. Data'First + (Raw.world_store'Position + Raw.world_store'Size / System.Storage_Unit - 1)), Raw.world_store)
        and then Source_Padding_Valid (Data (Data'First + Raw.full_world_ancestry'Position .. Data'First + (Raw.full_world_ancestry'Position + Raw.full_world_ancestry'Size / System.Storage_Unit - 1)), Raw.full_world_ancestry)
        and then Source_Padding_Valid (Data (Data'First + Raw.original_workload'Position .. Data'First + (Raw.original_workload'Position + Raw.original_workload'Size / System.Storage_Unit - 1)), Raw.original_workload)
        and then Source_Padding_Valid (Data (Data'First + Raw.sandbox'Position .. Data'First + (Raw.sandbox'Position + Raw.sandbox'Size / System.Storage_Unit - 1)), Raw.sandbox)
        and then Source_Padding_Valid (Data (Data'First + Raw.adapter'Position .. Data'First + (Raw.adapter'Position + Raw.adapter'Size / System.Storage_Unit - 1)), Raw.adapter)
        and then Source_Padding_Valid (Data (Data'First + Raw.context'Position .. Data'First + (Raw.context'Position + Raw.context'Size / System.Storage_Unit - 1)), Raw.context)
        and then Source_Padding_Valid (Data (Data'First + Raw.mission'Position .. Data'First + (Raw.mission'Position + Raw.mission'Size / System.Storage_Unit - 1)), Raw.mission)
        and then Source_Padding_Valid (Data (Data'First + Raw.stdin'Position .. Data'First + (Raw.stdin'Position + Raw.stdin'Size / System.Storage_Unit - 1)), Raw.stdin)
        and then Source_Padding_Valid (Data (Data'First + Raw.credential_source'Position .. Data'First + (Raw.credential_source'Position + Raw.credential_source'Size / System.Storage_Unit - 1)), Raw.credential_source)
        and then Source_Padding_Valid (Data (Data'First + Raw.executable_source'Position .. Data'First + (Raw.executable_source'Position + Raw.executable_source'Size / System.Storage_Unit - 1)), Raw.executable_source)
        and then Source_Padding_Valid (Data (Data'First + Raw.configuration'Position .. Data'First + (Raw.configuration'Position + Raw.configuration'Size / System.Storage_Unit - 1)), Raw.configuration)
        and then Source_Padding_Valid (Data (Data'First + Raw.owner_plan'Position .. Data'First + (Raw.owner_plan'Position + Raw.owner_plan'Size / System.Storage_Unit - 1)), Raw.owner_plan)
        and then Source_Padding_Valid (Data (Data'First + Raw.native_cost_input'Position .. Data'First + (Raw.native_cost_input'Position + Raw.native_cost_input'Size / System.Storage_Unit - 1)), Raw.native_cost_input)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_request'Position .. Data'First + (Raw.raw_request'Position + Raw.raw_request'Size / System.Storage_Unit - 1)), Raw.raw_request)
        and then Source_Padding_Valid (Data (Data'First + Raw.requester'Position .. Data'First + (Raw.requester'Position + Raw.requester'Size / System.Storage_Unit - 1)), Raw.requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.cause'Position .. Data'First + (Raw.cause'Position + Raw.cause'Size / System.Storage_Unit - 1)), Raw.cause)
        and then Source_Padding_Valid (Data (Data'First + Raw.root_dispatch'Position .. Data'First + (Raw.root_dispatch'Position + Raw.root_dispatch'Size / System.Storage_Unit - 1)), Raw.root_dispatch)
        and then Source_Padding_Valid (Data (Data'First + Raw.root_running_event'Position .. Data'First + (Raw.root_running_event'Position + Raw.root_running_event'Size / System.Storage_Unit - 1)), Raw.root_running_event)
        and then Source_Padding_Valid (Data (Data'First + Raw.task_journal'Position .. Data'First + (Raw.task_journal'Position + Raw.task_journal'Size / System.Storage_Unit - 1)), Raw.task_journal)
        and then Source_Padding_Valid (Data (Data'First + Raw.task_intent'Position .. Data'First + (Raw.task_intent'Position + Raw.task_intent'Size / System.Storage_Unit - 1)), Raw.task_intent)
        and then Source_Padding_Valid (Data (Data'First + Raw.task_reservation_event'Position .. Data'First + (Raw.task_reservation_event'Position + Raw.task_reservation_event'Size / System.Storage_Unit - 1)), Raw.task_reservation_event)
        and then Source_Padding_Valid (Data (Data'First + Raw.task_launch_event'Position .. Data'First + (Raw.task_launch_event'Position + Raw.task_launch_event'Size / System.Storage_Unit - 1)), Raw.task_launch_event)
        and then Source_Padding_Valid (Data (Data'First + Raw.parent_namespace_source'Position .. Data'First + (Raw.parent_namespace_source'Position + Raw.parent_namespace_source'Size / System.Storage_Unit - 1)), Raw.parent_namespace_source)
        and then Source_Padding_Valid (Data (Data'First + Raw.fd_lineage'Position .. Data'First + (Raw.fd_lineage'Position + Raw.fd_lineage'Size / System.Storage_Unit - 1)), Raw.fd_lineage)
        and then Source_Padding_Valid (Data (Data'First + Raw.source_lease'Position .. Data'First + (Raw.source_lease'Position + Raw.source_lease'Size / System.Storage_Unit - 1)), Raw.source_lease);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : Y.Raw_Namespace) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.identity'Position .. Data'First + (Raw.identity'Position + Raw.identity'Size / System.Storage_Unit - 1)), Raw.identity)
        and then Source_Padding_Valid (Data (Data'First + Raw.parent'Position .. Data'First + (Raw.parent'Position + Raw.parent'Size / System.Storage_Unit - 1)), Raw.parent)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_nsfs'Position .. Data'First + (Raw.raw_nsfs'Position + Raw.raw_nsfs'Size / System.Storage_Unit - 1)), Raw.raw_nsfs)
        and then Source_Padding_Valid (Data (Data'First + Raw.raw_get_parent'Position .. Data'First + (Raw.raw_get_parent'Position + Raw.raw_get_parent'Size / System.Storage_Unit - 1)), Raw.raw_get_parent)
        and then Source_Padding_Valid (Data (Data'First + Raw.source_lease'Position .. Data'First + (Raw.source_lease'Position + Raw.source_lease'Size / System.Storage_Unit - 1)), Raw.source_lease);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Input) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Schema'Position, Raw.Schema'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Mode'Position, Raw.Mode'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Bound'Position, Raw.Bound'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Now'Position, Raw.Now'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Facts'Position, Raw.Facts'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + (Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1)), Raw.Bound)
        and then Source_Padding_Valid (Data (Data'First + Raw.Now'Position .. Data'First + (Raw.Now'Position + Raw.Now'Size / System.Storage_Unit - 1)), Raw.Now)
        and then Source_Padding_Valid (Data (Data'First + Raw.Facts'Position .. Data'First + (Raw.Facts'Position + Raw.Facts'Size / System.Storage_Unit - 1)), Raw.Facts);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Binding) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Action'Position, Raw.Action'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Id'Position, Raw.Id'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Peer'Position, Raw.Peer'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Preparer'Position, Raw.Preparer'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Owner'Position, Raw.Owner'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Target_Owner'Position, Raw.Target_Owner'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Policy_Epoch'Position, Raw.Policy_Epoch'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Resource_Epoch'Position, Raw.Resource_Epoch'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Id'Position .. Data'First + (Raw.Id'Position + Raw.Id'Size / System.Storage_Unit - 1)), Raw.Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Peer'Position .. Data'First + (Raw.Peer'Position + Raw.Peer'Size / System.Storage_Unit - 1)), Raw.Peer)
        and then Source_Padding_Valid (Data (Data'First + Raw.Preparer'Position .. Data'First + (Raw.Preparer'Position + Raw.Preparer'Size / System.Storage_Unit - 1)), Raw.Preparer)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner'Position .. Data'First + (Raw.Owner'Position + Raw.Owner'Size / System.Storage_Unit - 1)), Raw.Owner)
        and then Source_Padding_Valid (Data (Data'First + Raw.Target_Owner'Position .. Data'First + (Raw.Target_Owner'Position + Raw.Target_Owner'Size / System.Storage_Unit - 1)), Raw.Target_Owner)
        and then Source_Padding_Valid (Data (Data'First + Raw.Policy_Epoch'Position .. Data'First + (Raw.Policy_Epoch'Position + Raw.Policy_Epoch'Size / System.Storage_Unit - 1)), Raw.Policy_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource_Epoch'Position .. Data'First + (Raw.Resource_Epoch'Position + Raw.Resource_Epoch'Size / System.Storage_Unit - 1)), Raw.Resource_Epoch);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Ids) return Boolean is
   begin
      for I in Raw'Range loop
         if not Source_Padding_Valid (Data (Data'First + Q.Byte_Count (T.A.Identity_Field'Pos (I) - T.A.Identity_Field'Pos (Raw'First)) * C.Raw_Digest'Size / System.Storage_Unit .. Data'First + (Q.Byte_Count (T.A.Identity_Field'Pos (I) - T.A.Identity_Field'Pos (Raw'First)) * C.Raw_Digest'Size / System.Storage_Unit + C.Raw_Digest'Size / System.Storage_Unit - 1)), Raw (I)) then return False; end if;
      end loop;
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_UID) return Boolean is
      pragma Unreferenced (Raw);
      Layout : constant T.Raw_UID := (Present => 0, Value => 0);
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Layout.Present'Position, Layout.Present'Size / System.Storage_Unit) or else In_Field (Offset, Layout.Value'Position, Layout.Value'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Quantity) return Boolean is
      pragma Unreferenced (Raw);
      Layout : constant T.Raw_Quantity := (Present => 0, Negative => 0, First => 0, Length => 0);
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Layout.Present'Position, Layout.Present'Size / System.Storage_Unit) or else In_Field (Offset, Layout.Negative'Position, Layout.Negative'Size / System.Storage_Unit) or else In_Field (Offset, Layout.First'Position, Layout.First'Size / System.Storage_Unit) or else In_Field (Offset, Layout.Length'Position, Layout.Length'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
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
            if In_Field (Offset, Raw.Effect_Material_First'Position, Raw.Effect_Material_First'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Effect_Material_Length'Position, Raw.Effect_Material_Length'Size / System.Storage_Unit) then
               null;
            else
            if not (In_Field (Offset, Raw.Effect_Binding'Position, Raw.Effect_Binding'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Actual_Receipt_Root'Position, Raw.Actual_Receipt_Root'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Actual_Causal_Root'Position, Raw.Actual_Causal_Root'Size / System.Storage_Unit) or else In_Field (Offset, Raw.No_Effect_Binding'Position, Raw.No_Effect_Binding'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Owner_Resolution'Position, Raw.Owner_Resolution'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Quarantine_Head'Position, Raw.Quarantine_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Witnessed_Receipt_Head'Position, Raw.Witnessed_Receipt_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Witnessed_Causal_Head'Position, Raw.Witnessed_Causal_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Recovery'Position, Raw.Recovery'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Original_Use'Position, Raw.Original_Use'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
            end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Effect_Binding'Position .. Data'First + (Raw.Effect_Binding'Position + Raw.Effect_Binding'Size / System.Storage_Unit - 1)), Raw.Effect_Binding)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Receipt_Root'Position .. Data'First + (Raw.Actual_Receipt_Root'Position + Raw.Actual_Receipt_Root'Size / System.Storage_Unit - 1)), Raw.Actual_Receipt_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Causal_Root'Position .. Data'First + (Raw.Actual_Causal_Root'Position + Raw.Actual_Causal_Root'Size / System.Storage_Unit - 1)), Raw.Actual_Causal_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.No_Effect_Binding'Position .. Data'First + (Raw.No_Effect_Binding'Position + Raw.No_Effect_Binding'Size / System.Storage_Unit - 1)), Raw.No_Effect_Binding)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner_Resolution'Position .. Data'First + (Raw.Owner_Resolution'Position + Raw.Owner_Resolution'Size / System.Storage_Unit - 1)), Raw.Owner_Resolution)
        and then Source_Padding_Valid (Data (Data'First + Raw.Quarantine_Head'Position .. Data'First + (Raw.Quarantine_Head'Position + Raw.Quarantine_Head'Size / System.Storage_Unit - 1)), Raw.Quarantine_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Witnessed_Receipt_Head'Position .. Data'First + (Raw.Witnessed_Receipt_Head'Position + Raw.Witnessed_Receipt_Head'Size / System.Storage_Unit - 1)), Raw.Witnessed_Receipt_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Witnessed_Causal_Head'Position .. Data'First + (Raw.Witnessed_Causal_Head'Position + Raw.Witnessed_Causal_Head'Size / System.Storage_Unit - 1)), Raw.Witnessed_Causal_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Recovery'Position .. Data'First + (Raw.Recovery'Position + Raw.Recovery'Size / System.Storage_Unit - 1)), Raw.Recovery)
        and then Source_Padding_Valid (Data (Data'First + Raw.Original_Use'Position .. Data'First + (Raw.Original_Use'Position + Raw.Original_Use'Size / System.Storage_Unit - 1)), Raw.Original_Use);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Request) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Schema_Version'Position, Raw.Schema_Version'Size / System.Storage_Unit) or else In_Field (Offset, Raw.State'Position, Raw.State'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Fresh'Position, Raw.Fresh'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Historical'Position, Raw.Historical'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Grant_Eligible'Position, Raw.Grant_Eligible'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Issued_Binding'Position, Raw.Issued_Binding'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Recovered_Binding'Position, Raw.Recovered_Binding'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Native'Position, Raw.Native'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Issued_Binding'Position .. Data'First + (Raw.Issued_Binding'Position + Raw.Issued_Binding'Size / System.Storage_Unit - 1)), Raw.Issued_Binding)
        and then Source_Padding_Valid (Data (Data'First + Raw.Recovered_Binding'Position .. Data'First + (Raw.Recovered_Binding'Position + Raw.Recovered_Binding'Size / System.Storage_Unit - 1)), Raw.Recovered_Binding)
        and then Source_Padding_Valid (Data (Data'First + Raw.Native'Position .. Data'First + (Raw.Native'Position + Raw.Native'Size / System.Storage_Unit - 1)), Raw.Native);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Binding) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Mode'Position, Raw.Mode'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Operation'Position, Raw.Operation'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Transaction'Position, Raw.Transaction'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Capability'Position, Raw.Capability'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Universe_Head'Position, Raw.Universe_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Instance'Position, Raw.Instance'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Subject'Position, Raw.Subject'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Staged_Root'Position, Raw.Staged_Root'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Current_Requirement'Position, Raw.Current_Requirement'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Resulting_Requirement'Position, Raw.Resulting_Requirement'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Requester'Position, Raw.Requester'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Grant_Use'Position, Raw.Grant_Use'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Policy_Identity'Position, Raw.Policy_Identity'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Selected_Evaluation'Position, Raw.Selected_Evaluation'Size / System.Storage_Unit) or else In_Field (Offset, Raw.History_Head'Position, Raw.History_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Reservation'Position, Raw.Reservation'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Host'Position, Raw.Host'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Before_Prime'Position, Raw.Before_Prime'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Before_Root'Position, Raw.Before_Root'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Before_Mapping'Position, Raw.Before_Mapping'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Staged_Mapping'Position, Raw.Staged_Mapping'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Input_Snapshot'Position, Raw.Input_Snapshot'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Kernel_Build'Position, Raw.Kernel_Build'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Kernel_Library'Position, Raw.Kernel_Library'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Kernel_Mapping'Position, Raw.Kernel_Mapping'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Issuer_Head'Position, Raw.Issuer_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Receipt_Head'Position, Raw.Receipt_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Causal_Head'Position, Raw.Causal_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Policy_Epoch'Position, Raw.Policy_Epoch'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Resource_Epoch'Position, Raw.Resource_Epoch'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Operation'Position .. Data'First + (Raw.Operation'Position + Raw.Operation'Size / System.Storage_Unit - 1)), Raw.Operation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Transaction'Position .. Data'First + (Raw.Transaction'Position + Raw.Transaction'Size / System.Storage_Unit - 1)), Raw.Transaction)
        and then Source_Padding_Valid (Data (Data'First + Raw.Capability'Position .. Data'First + (Raw.Capability'Position + Raw.Capability'Size / System.Storage_Unit - 1)), Raw.Capability)
        and then Source_Padding_Valid (Data (Data'First + Raw.Universe_Head'Position .. Data'First + (Raw.Universe_Head'Position + Raw.Universe_Head'Size / System.Storage_Unit - 1)), Raw.Universe_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Instance'Position .. Data'First + (Raw.Instance'Position + Raw.Instance'Size / System.Storage_Unit - 1)), Raw.Instance)
        and then Source_Padding_Valid (Data (Data'First + Raw.Subject'Position .. Data'First + (Raw.Subject'Position + Raw.Subject'Size / System.Storage_Unit - 1)), Raw.Subject)
        and then Source_Padding_Valid (Data (Data'First + Raw.Staged_Root'Position .. Data'First + (Raw.Staged_Root'Position + Raw.Staged_Root'Size / System.Storage_Unit - 1)), Raw.Staged_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Current_Requirement'Position .. Data'First + (Raw.Current_Requirement'Position + Raw.Current_Requirement'Size / System.Storage_Unit - 1)), Raw.Current_Requirement)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resulting_Requirement'Position .. Data'First + (Raw.Resulting_Requirement'Position + Raw.Resulting_Requirement'Size / System.Storage_Unit - 1)), Raw.Resulting_Requirement)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester'Position .. Data'First + (Raw.Requester'Position + Raw.Requester'Size / System.Storage_Unit - 1)), Raw.Requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.Grant_Use'Position .. Data'First + (Raw.Grant_Use'Position + Raw.Grant_Use'Size / System.Storage_Unit - 1)), Raw.Grant_Use)
        and then Source_Padding_Valid (Data (Data'First + Raw.Policy_Identity'Position .. Data'First + (Raw.Policy_Identity'Position + Raw.Policy_Identity'Size / System.Storage_Unit - 1)), Raw.Policy_Identity)
        and then Source_Padding_Valid (Data (Data'First + Raw.Selected_Evaluation'Position .. Data'First + (Raw.Selected_Evaluation'Position + Raw.Selected_Evaluation'Size / System.Storage_Unit - 1)), Raw.Selected_Evaluation)
        and then Source_Padding_Valid (Data (Data'First + Raw.History_Head'Position .. Data'First + (Raw.History_Head'Position + Raw.History_Head'Size / System.Storage_Unit - 1)), Raw.History_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Reservation'Position .. Data'First + (Raw.Reservation'Position + Raw.Reservation'Size / System.Storage_Unit - 1)), Raw.Reservation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Host'Position .. Data'First + (Raw.Host'Position + Raw.Host'Size / System.Storage_Unit - 1)), Raw.Host)
        and then Source_Padding_Valid (Data (Data'First + Raw.Before_Prime'Position .. Data'First + (Raw.Before_Prime'Position + Raw.Before_Prime'Size / System.Storage_Unit - 1)), Raw.Before_Prime)
        and then Source_Padding_Valid (Data (Data'First + Raw.Before_Root'Position .. Data'First + (Raw.Before_Root'Position + Raw.Before_Root'Size / System.Storage_Unit - 1)), Raw.Before_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Before_Mapping'Position .. Data'First + (Raw.Before_Mapping'Position + Raw.Before_Mapping'Size / System.Storage_Unit - 1)), Raw.Before_Mapping)
        and then Source_Padding_Valid (Data (Data'First + Raw.Staged_Mapping'Position .. Data'First + (Raw.Staged_Mapping'Position + Raw.Staged_Mapping'Size / System.Storage_Unit - 1)), Raw.Staged_Mapping)
        and then Source_Padding_Valid (Data (Data'First + Raw.Input_Snapshot'Position .. Data'First + (Raw.Input_Snapshot'Position + Raw.Input_Snapshot'Size / System.Storage_Unit - 1)), Raw.Input_Snapshot)
        and then Source_Padding_Valid (Data (Data'First + Raw.Kernel_Build'Position .. Data'First + (Raw.Kernel_Build'Position + Raw.Kernel_Build'Size / System.Storage_Unit - 1)), Raw.Kernel_Build)
        and then Source_Padding_Valid (Data (Data'First + Raw.Kernel_Library'Position .. Data'First + (Raw.Kernel_Library'Position + Raw.Kernel_Library'Size / System.Storage_Unit - 1)), Raw.Kernel_Library)
        and then Source_Padding_Valid (Data (Data'First + Raw.Kernel_Mapping'Position .. Data'First + (Raw.Kernel_Mapping'Position + Raw.Kernel_Mapping'Size / System.Storage_Unit - 1)), Raw.Kernel_Mapping)
        and then Source_Padding_Valid (Data (Data'First + Raw.Issuer_Head'Position .. Data'First + (Raw.Issuer_Head'Position + Raw.Issuer_Head'Size / System.Storage_Unit - 1)), Raw.Issuer_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Receipt_Head'Position .. Data'First + (Raw.Receipt_Head'Position + Raw.Receipt_Head'Size / System.Storage_Unit - 1)), Raw.Receipt_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Causal_Head'Position .. Data'First + (Raw.Causal_Head'Position + Raw.Causal_Head'Size / System.Storage_Unit - 1)), Raw.Causal_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Policy_Epoch'Position .. Data'First + (Raw.Policy_Epoch'Position + Raw.Policy_Epoch'Size / System.Storage_Unit - 1)), Raw.Policy_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource_Epoch'Position .. Data'First + (Raw.Resource_Epoch'Position + Raw.Resource_Epoch'Size / System.Storage_Unit - 1)), Raw.Resource_Epoch);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Digest) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Value'Position .. Data'First + (Raw.Value'Position + Raw.Value'Size / System.Storage_Unit - 1)), Raw.Value);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Hash) return Boolean is
      pragma Unreferenced (Raw);
   begin
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Epoch) return Boolean is
      pragma Unreferenced (Raw);
      Layout : constant RW.Raw_Epoch := (Present => 0, Negative => 0, First => 0, Length => 0);
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Layout.Present'Position, Layout.Present'Size / System.Storage_Unit) or else In_Field (Offset, Layout.Negative'Position, Layout.Negative'Size / System.Storage_Unit) or else In_Field (Offset, Layout.First'Position, Layout.First'Size / System.Storage_Unit) or else In_Field (Offset, Layout.Length'Position, Layout.Length'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Native) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Live_Mapping'Position .. Data'First + (Raw.Live_Mapping'Position + Raw.Live_Mapping'Size / System.Storage_Unit - 1)), Raw.Live_Mapping)
        and then Source_Padding_Valid (Data (Data'First + Raw.Live_Root'Position .. Data'First + (Raw.Live_Root'Position + Raw.Live_Root'Size / System.Storage_Unit - 1)), Raw.Live_Root);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Grant) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Id'Position, Raw.Id'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Parent'Position, Raw.Parent'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Issuer'Position, Raw.Issuer'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Instance'Position, Raw.Instance'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Root_Set'Position, Raw.Root_Set'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Policy'Position, Raw.Policy'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Subject'Position, Raw.Subject'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Owner'Position, Raw.Owner'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Allowed'Position, Raw.Allowed'Size / System.Storage_Unit) or else In_Field (Offset, Raw.State'Position, Raw.State'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Epoch'Position, Raw.Epoch'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Ceiling'Position, Raw.Ceiling'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Issued_At'Position, Raw.Issued_At'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Expires_At'Position, Raw.Expires_At'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Id'Position .. Data'First + (Raw.Id'Position + Raw.Id'Size / System.Storage_Unit - 1)), Raw.Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Parent'Position .. Data'First + (Raw.Parent'Position + Raw.Parent'Size / System.Storage_Unit - 1)), Raw.Parent)
        and then Source_Padding_Valid (Data (Data'First + Raw.Issuer'Position .. Data'First + (Raw.Issuer'Position + Raw.Issuer'Size / System.Storage_Unit - 1)), Raw.Issuer)
        and then Source_Padding_Valid (Data (Data'First + Raw.Instance'Position .. Data'First + (Raw.Instance'Position + Raw.Instance'Size / System.Storage_Unit - 1)), Raw.Instance)
        and then Source_Padding_Valid (Data (Data'First + Raw.Root_Set'Position .. Data'First + (Raw.Root_Set'Position + Raw.Root_Set'Size / System.Storage_Unit - 1)), Raw.Root_Set)
        and then Source_Padding_Valid (Data (Data'First + Raw.Policy'Position .. Data'First + (Raw.Policy'Position + Raw.Policy'Size / System.Storage_Unit - 1)), Raw.Policy)
        and then Source_Padding_Valid (Data (Data'First + Raw.Subject'Position .. Data'First + (Raw.Subject'Position + Raw.Subject'Size / System.Storage_Unit - 1)), Raw.Subject)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner'Position .. Data'First + (Raw.Owner'Position + Raw.Owner'Size / System.Storage_Unit - 1)), Raw.Owner)
        and then Source_Padding_Valid (Data (Data'First + Raw.Allowed'Position .. Data'First + (Raw.Allowed'Position + Raw.Allowed'Size / System.Storage_Unit - 1)), Raw.Allowed)
        and then Source_Padding_Valid (Data (Data'First + Raw.Epoch'Position .. Data'First + (Raw.Epoch'Position + Raw.Epoch'Size / System.Storage_Unit - 1)), Raw.Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Ceiling'Position .. Data'First + (Raw.Ceiling'Position + Raw.Ceiling'Size / System.Storage_Unit - 1)), Raw.Ceiling)
        and then Source_Padding_Valid (Data (Data'First + Raw.Issued_At'Position .. Data'First + (Raw.Issued_At'Position + Raw.Issued_At'Size / System.Storage_Unit - 1)), Raw.Issued_At)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expires_At'Position .. Data'First + (Raw.Expires_At'Position + Raw.Expires_At'Size / System.Storage_Unit - 1)), Raw.Expires_At);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Rights) return Boolean is
      pragma Unreferenced (Raw);
   begin
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Use) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Bound'Position, Raw.Bound'Size / System.Storage_Unit) or else In_Field (Offset, Raw.State'Position, Raw.State'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + (Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1)), Raw.Bound);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : C.Raw_Row) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Previous'Position .. Data'First + (Raw.Previous'Position + Raw.Previous'Size / System.Storage_Unit - 1)), Raw.Previous)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Payload_Root'Position .. Data'First + (Raw.Actual_Payload_Root'Position + Raw.Actual_Payload_Root'Size / System.Storage_Unit - 1)), Raw.Actual_Payload_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Stored_Payload_Root'Position .. Data'First + (Raw.Stored_Payload_Root'Position + Raw.Stored_Payload_Root'Size / System.Storage_Unit - 1)), Raw.Stored_Payload_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Stored_Head'Position .. Data'First + (Raw.Stored_Head'Position + Raw.Stored_Head'Size / System.Storage_Unit - 1)), Raw.Stored_Head);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : D.Raw_Capability) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Index'Position .. Data'First + (Raw.Index'Position + Raw.Index'Size / System.Storage_Unit - 1)), Raw.Index)
        and then Source_Padding_Valid (Data (Data'First + Raw.Bounding'Position .. Data'First + (Raw.Bounding'Position + Raw.Bounding'Size / System.Storage_Unit - 1)), Raw.Bounding)
        and then Source_Padding_Valid (Data (Data'First + Raw.Ambient'Position .. Data'First + (Raw.Ambient'Position + Raw.Ambient'Size / System.Storage_Unit - 1)), Raw.Ambient);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Scope_Frame) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Scope'Position .. Data'First + (Raw.Scope'Position + Raw.Scope'Size / System.Storage_Unit - 1)), Raw.Scope)
        and then Source_Padding_Valid (Data (Data'First + Raw.First_Epoch'Position .. Data'First + (Raw.First_Epoch'Position + Raw.First_Epoch'Size / System.Storage_Unit - 1)), Raw.First_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Universe_Head'Position .. Data'First + (Raw.Universe_Head'Position + Raw.Universe_Head'Size / System.Storage_Unit - 1)), Raw.Universe_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Frame_Head'Position .. Data'First + (Raw.Frame_Head'Position + Raw.Frame_Head'Size / System.Storage_Unit - 1)), Raw.Frame_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Prior_Frame'Position .. Data'First + (Raw.Prior_Frame'Position + Raw.Prior_Frame'Size / System.Storage_Unit - 1)), Raw.Prior_Frame)
        and then Source_Padding_Valid (Data (Data'First + Raw.Store_Genesis'Position .. Data'First + (Raw.Store_Genesis'Position + Raw.Store_Genesis'Size / System.Storage_Unit - 1)), Raw.Store_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Store_Id'Position .. Data'First + (Raw.Store_Id'Position + Raw.Store_Id'Size / System.Storage_Unit - 1)), Raw.Store_Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Root_Head'Position .. Data'First + (Raw.Root_Head'Position + Raw.Root_Head'Size / System.Storage_Unit - 1)), Raw.Root_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Prime'Position .. Data'First + (Raw.Prime'Position + Raw.Prime'Size / System.Storage_Unit - 1)), Raw.Prime)
        and then Source_Padding_Valid (Data (Data'First + Raw.Root_Count'Position .. Data'First + (Raw.Root_Count'Position + Raw.Root_Count'Size / System.Storage_Unit - 1)), Raw.Root_Count)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cause'Position .. Data'First + (Raw.Cause'Position + Raw.Cause'Size / System.Storage_Unit - 1)), Raw.Cause)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester'Position .. Data'First + (Raw.Requester'Position + Raw.Requester'Size / System.Storage_Unit - 1)), Raw.Requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.Receipt'Position .. Data'First + (Raw.Receipt'Position + Raw.Receipt'Size / System.Storage_Unit - 1)), Raw.Receipt)
        and then Source_Padding_Valid (Data (Data'First + Raw.Catalogue_Head'Position .. Data'First + (Raw.Catalogue_Head'Position + Raw.Catalogue_Head'Size / System.Storage_Unit - 1)), Raw.Catalogue_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Observation_Head'Position .. Data'First + (Raw.Observation_Head'Position + Raw.Observation_Head'Size / System.Storage_Unit - 1)), Raw.Observation_Head);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Projection) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Key'Position .. Data'First + (Raw.Key'Position + Raw.Key'Size / System.Storage_Unit - 1)), Raw.Key)
        and then Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + (Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1)), Raw.Bound)
        and then Source_Padding_Valid (Data (Data'First + Raw.Origin'Position .. Data'First + (Raw.Origin'Position + Raw.Origin'Size / System.Storage_Unit - 1)), Raw.Origin)
        and then Source_Padding_Valid (Data (Data'First + Raw.Catalogue_Head'Position .. Data'First + (Raw.Catalogue_Head'Position + Raw.Catalogue_Head'Size / System.Storage_Unit - 1)), Raw.Catalogue_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Numerator'Position .. Data'First + (Raw.Numerator'Position + Raw.Numerator'Size / System.Storage_Unit - 1)), Raw.Numerator)
        and then Source_Padding_Valid (Data (Data'First + Raw.Denominator'Position .. Data'First + (Raw.Denominator'Position + Raw.Denominator'Size / System.Storage_Unit - 1)), Raw.Denominator)
        and then Source_Padding_Valid (Data (Data'First + Raw.Amount'Position .. Data'First + (Raw.Amount'Position + Raw.Amount'Size / System.Storage_Unit - 1)), Raw.Amount);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Physical_Key) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Machine'Position .. Data'First + (Raw.Machine'Position + Raw.Machine'Size / System.Storage_Unit - 1)), Raw.Machine)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource'Position .. Data'First + (Raw.Resource'Position + Raw.Resource'Size / System.Storage_Unit - 1)), Raw.Resource)
        and then Source_Padding_Valid (Data (Data'First + Raw.Unit'Position .. Data'First + (Raw.Unit'Position + Raw.Unit'Size / System.Storage_Unit - 1)), Raw.Unit);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Bucket) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Key'Position .. Data'First + (Raw.Key'Position + Raw.Key'Size / System.Storage_Unit - 1)), Raw.Key)
        and then Source_Padding_Valid (Data (Data'First + Raw.Capacity'Position .. Data'First + (Raw.Capacity'Position + Raw.Capacity'Size / System.Storage_Unit - 1)), Raw.Capacity)
        and then Source_Padding_Valid (Data (Data'First + Raw.Held_Total'Position .. Data'First + (Raw.Held_Total'Position + Raw.Held_Total'Size / System.Storage_Unit - 1)), Raw.Held_Total)
        and then Source_Padding_Valid (Data (Data'First + Raw.Charged_Total'Position .. Data'First + (Raw.Charged_Total'Position + Raw.Charged_Total'Size / System.Storage_Unit - 1)), Raw.Charged_Total)
        and then Source_Padding_Valid (Data (Data'First + Raw.Capacity_Source'Position .. Data'First + (Raw.Capacity_Source'Position + Raw.Capacity_Source'Size / System.Storage_Unit - 1)), Raw.Capacity_Source)
        and then Source_Padding_Valid (Data (Data'First + Raw.Catalogue_Head'Position .. Data'First + (Raw.Catalogue_Head'Position + Raw.Catalogue_Head'Size / System.Storage_Unit - 1)), Raw.Catalogue_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Observation_Head'Position .. Data'First + (Raw.Observation_Head'Position + Raw.Observation_Head'Size / System.Storage_Unit - 1)), Raw.Observation_Head);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Native) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Scope'Position, Raw.Scope'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Resource_Epoch'Position, Raw.Resource_Epoch'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Bound'Position, Raw.Bound'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Actual_Unit'Position, Raw.Actual_Unit'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Cgroup'Position, Raw.Cgroup'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Invocation'Position, Raw.Invocation'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Observation_Head'Position, Raw.Observation_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Observed'Position, Raw.Observed'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Scope'Position .. Data'First + (Raw.Scope'Position + Raw.Scope'Size / System.Storage_Unit - 1)), Raw.Scope)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource_Epoch'Position .. Data'First + (Raw.Resource_Epoch'Position + Raw.Resource_Epoch'Size / System.Storage_Unit - 1)), Raw.Resource_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + (Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1)), Raw.Bound)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Unit'Position .. Data'First + (Raw.Actual_Unit'Position + Raw.Actual_Unit'Size / System.Storage_Unit - 1)), Raw.Actual_Unit)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cgroup'Position .. Data'First + (Raw.Cgroup'Position + Raw.Cgroup'Size / System.Storage_Unit - 1)), Raw.Cgroup)
        and then Source_Padding_Valid (Data (Data'First + Raw.Invocation'Position .. Data'First + (Raw.Invocation'Position + Raw.Invocation'Size / System.Storage_Unit - 1)), Raw.Invocation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Observation_Head'Position .. Data'First + (Raw.Observation_Head'Position + Raw.Observation_Head'Size / System.Storage_Unit - 1)), Raw.Observation_Head);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : O.Raw_Facts) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Current'Position, Raw.Current'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Current_Epoch'Position, Raw.Current_Epoch'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Retained'Position, Raw.Retained'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Current_Universe_Head'Position, Raw.Current_Universe_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Current_Ledger_Head'Position, Raw.Current_Ledger_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Intent'Position, Raw.Intent'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Dispatch'Position, Raw.Dispatch'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Observation_Head'Position, Raw.Observation_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Actual_Unit'Position, Raw.Actual_Unit'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Cgroup'Position, Raw.Cgroup'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Invocation'Position, Raw.Invocation'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Namespace'Position, Raw.Namespace'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Held_Namespace'Position, Raw.Held_Namespace'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Peer'Position, Raw.Peer'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Held_Peer'Position, Raw.Held_Peer'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Helper_Image'Position, Raw.Helper_Image'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Expected_Helper_Image'Position, Raw.Expected_Helper_Image'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Challenge'Position, Raw.Challenge'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Held_Challenge'Position, Raw.Held_Challenge'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Protocol'Position, Raw.Protocol'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Closed_Event'Position, Raw.Closed_Event'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Namespace_Wait'Position, Raw.Namespace_Wait'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Helper_Wait'Position, Raw.Helper_Wait'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Cgroup_Events'Position, Raw.Cgroup_Events'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Cgroup_Type'Position, Raw.Cgroup_Type'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Manager_Delegate'Position, Raw.Manager_Delegate'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Cgroup_Owner'Position, Raw.Cgroup_Owner'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Cgroup_Group_Write'Position, Raw.Cgroup_Group_Write'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Cgroup_Other_Write'Position, Raw.Cgroup_Other_Write'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Actual_Store_Genesis'Position, Raw.Actual_Store_Genesis'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Actual_Store_Id'Position, Raw.Actual_Store_Id'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Owner_Store_Genesis'Position, Raw.Owner_Store_Genesis'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Owner_Store_Id'Position, Raw.Owner_Store_Id'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Genesis_Universe'Position, Raw.Genesis_Universe'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Genesis_Instance'Position, Raw.Genesis_Instance'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Genesis_Context_Head'Position, Raw.Genesis_Context_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Genesis_Prime'Position, Raw.Genesis_Prime'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Genesis_Root_Count'Position, Raw.Genesis_Root_Count'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Phase'Position, Raw.Phase'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Current'Position .. Data'First + (Raw.Current'Position + Raw.Current'Size / System.Storage_Unit - 1)), Raw.Current)
        and then Source_Padding_Valid (Data (Data'First + Raw.Current_Epoch'Position .. Data'First + (Raw.Current_Epoch'Position + Raw.Current_Epoch'Size / System.Storage_Unit - 1)), Raw.Current_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Retained'Position .. Data'First + (Raw.Retained'Position + Raw.Retained'Size / System.Storage_Unit - 1)), Raw.Retained)
        and then Source_Padding_Valid (Data (Data'First + Raw.Current_Universe_Head'Position .. Data'First + (Raw.Current_Universe_Head'Position + Raw.Current_Universe_Head'Size / System.Storage_Unit - 1)), Raw.Current_Universe_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Current_Ledger_Head'Position .. Data'First + (Raw.Current_Ledger_Head'Position + Raw.Current_Ledger_Head'Size / System.Storage_Unit - 1)), Raw.Current_Ledger_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Intent'Position .. Data'First + (Raw.Intent'Position + Raw.Intent'Size / System.Storage_Unit - 1)), Raw.Intent)
        and then Source_Padding_Valid (Data (Data'First + Raw.Dispatch'Position .. Data'First + (Raw.Dispatch'Position + Raw.Dispatch'Size / System.Storage_Unit - 1)), Raw.Dispatch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Observation_Head'Position .. Data'First + (Raw.Observation_Head'Position + Raw.Observation_Head'Size / System.Storage_Unit - 1)), Raw.Observation_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Unit'Position .. Data'First + (Raw.Actual_Unit'Position + Raw.Actual_Unit'Size / System.Storage_Unit - 1)), Raw.Actual_Unit)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cgroup'Position .. Data'First + (Raw.Cgroup'Position + Raw.Cgroup'Size / System.Storage_Unit - 1)), Raw.Cgroup)
        and then Source_Padding_Valid (Data (Data'First + Raw.Invocation'Position .. Data'First + (Raw.Invocation'Position + Raw.Invocation'Size / System.Storage_Unit - 1)), Raw.Invocation)
        and then Source_Padding_Valid (Data (Data'First + Raw.Namespace'Position .. Data'First + (Raw.Namespace'Position + Raw.Namespace'Size / System.Storage_Unit - 1)), Raw.Namespace)
        and then Source_Padding_Valid (Data (Data'First + Raw.Held_Namespace'Position .. Data'First + (Raw.Held_Namespace'Position + Raw.Held_Namespace'Size / System.Storage_Unit - 1)), Raw.Held_Namespace)
        and then Source_Padding_Valid (Data (Data'First + Raw.Peer'Position .. Data'First + (Raw.Peer'Position + Raw.Peer'Size / System.Storage_Unit - 1)), Raw.Peer)
        and then Source_Padding_Valid (Data (Data'First + Raw.Held_Peer'Position .. Data'First + (Raw.Held_Peer'Position + Raw.Held_Peer'Size / System.Storage_Unit - 1)), Raw.Held_Peer)
        and then Source_Padding_Valid (Data (Data'First + Raw.Helper_Image'Position .. Data'First + (Raw.Helper_Image'Position + Raw.Helper_Image'Size / System.Storage_Unit - 1)), Raw.Helper_Image)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Helper_Image'Position .. Data'First + (Raw.Expected_Helper_Image'Position + Raw.Expected_Helper_Image'Size / System.Storage_Unit - 1)), Raw.Expected_Helper_Image)
        and then Source_Padding_Valid (Data (Data'First + Raw.Challenge'Position .. Data'First + (Raw.Challenge'Position + Raw.Challenge'Size / System.Storage_Unit - 1)), Raw.Challenge)
        and then Source_Padding_Valid (Data (Data'First + Raw.Held_Challenge'Position .. Data'First + (Raw.Held_Challenge'Position + Raw.Held_Challenge'Size / System.Storage_Unit - 1)), Raw.Held_Challenge)
        and then Source_Padding_Valid (Data (Data'First + Raw.Protocol'Position .. Data'First + (Raw.Protocol'Position + Raw.Protocol'Size / System.Storage_Unit - 1)), Raw.Protocol)
        and then Source_Padding_Valid (Data (Data'First + Raw.Closed_Event'Position .. Data'First + (Raw.Closed_Event'Position + Raw.Closed_Event'Size / System.Storage_Unit - 1)), Raw.Closed_Event)
        and then Source_Padding_Valid (Data (Data'First + Raw.Namespace_Wait'Position .. Data'First + (Raw.Namespace_Wait'Position + Raw.Namespace_Wait'Size / System.Storage_Unit - 1)), Raw.Namespace_Wait)
        and then Source_Padding_Valid (Data (Data'First + Raw.Helper_Wait'Position .. Data'First + (Raw.Helper_Wait'Position + Raw.Helper_Wait'Size / System.Storage_Unit - 1)), Raw.Helper_Wait)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cgroup_Events'Position .. Data'First + (Raw.Cgroup_Events'Position + Raw.Cgroup_Events'Size / System.Storage_Unit - 1)), Raw.Cgroup_Events)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cgroup_Type'Position .. Data'First + (Raw.Cgroup_Type'Position + Raw.Cgroup_Type'Size / System.Storage_Unit - 1)), Raw.Cgroup_Type)
        and then Source_Padding_Valid (Data (Data'First + Raw.Manager_Delegate'Position .. Data'First + (Raw.Manager_Delegate'Position + Raw.Manager_Delegate'Size / System.Storage_Unit - 1)), Raw.Manager_Delegate)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cgroup_Owner'Position .. Data'First + (Raw.Cgroup_Owner'Position + Raw.Cgroup_Owner'Size / System.Storage_Unit - 1)), Raw.Cgroup_Owner)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cgroup_Group_Write'Position .. Data'First + (Raw.Cgroup_Group_Write'Position + Raw.Cgroup_Group_Write'Size / System.Storage_Unit - 1)), Raw.Cgroup_Group_Write)
        and then Source_Padding_Valid (Data (Data'First + Raw.Cgroup_Other_Write'Position .. Data'First + (Raw.Cgroup_Other_Write'Position + Raw.Cgroup_Other_Write'Size / System.Storage_Unit - 1)), Raw.Cgroup_Other_Write)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Store_Genesis'Position .. Data'First + (Raw.Actual_Store_Genesis'Position + Raw.Actual_Store_Genesis'Size / System.Storage_Unit - 1)), Raw.Actual_Store_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Store_Id'Position .. Data'First + (Raw.Actual_Store_Id'Position + Raw.Actual_Store_Id'Size / System.Storage_Unit - 1)), Raw.Actual_Store_Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner_Store_Genesis'Position .. Data'First + (Raw.Owner_Store_Genesis'Position + Raw.Owner_Store_Genesis'Size / System.Storage_Unit - 1)), Raw.Owner_Store_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner_Store_Id'Position .. Data'First + (Raw.Owner_Store_Id'Position + Raw.Owner_Store_Id'Size / System.Storage_Unit - 1)), Raw.Owner_Store_Id)
        and then Source_Padding_Valid (Data (Data'First + Raw.Genesis_Universe'Position .. Data'First + (Raw.Genesis_Universe'Position + Raw.Genesis_Universe'Size / System.Storage_Unit - 1)), Raw.Genesis_Universe)
        and then Source_Padding_Valid (Data (Data'First + Raw.Genesis_Instance'Position .. Data'First + (Raw.Genesis_Instance'Position + Raw.Genesis_Instance'Size / System.Storage_Unit - 1)), Raw.Genesis_Instance)
        and then Source_Padding_Valid (Data (Data'First + Raw.Genesis_Context_Head'Position .. Data'First + (Raw.Genesis_Context_Head'Position + Raw.Genesis_Context_Head'Size / System.Storage_Unit - 1)), Raw.Genesis_Context_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Genesis_Prime'Position .. Data'First + (Raw.Genesis_Prime'Position + Raw.Genesis_Prime'Size / System.Storage_Unit - 1)), Raw.Genesis_Prime)
        and then Source_Padding_Valid (Data (Data'First + Raw.Genesis_Root_Count'Position .. Data'First + (Raw.Genesis_Root_Count'Position + Raw.Genesis_Root_Count'Size / System.Storage_Unit - 1)), Raw.Genesis_Root_Count);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Result) return Boolean is
      pragma Unreferenced (Raw);
   begin
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Result) return Boolean is
      pragma Unreferenced (Raw);
   begin
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : HC.Raw_Input) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Historical'Position .. Data'First + (Raw.Historical'Position + Raw.Historical'Size / System.Storage_Unit - 1)), Raw.Historical)
        and then Source_Padding_Valid (Data (Data'First + Raw.Current'Position .. Data'First + (Raw.Current'Position + Raw.Current'Size / System.Storage_Unit - 1)), Raw.Current);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CX.Raw_Input) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Operation_Input'Position, Raw.Operation_Input'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Material'Position, Raw.Material'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Before'Position, Raw.Before'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Mode'Position, Raw.Mode'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Operation_Input'Position .. Data'First + (Raw.Operation_Input'Position + Raw.Operation_Input'Size / System.Storage_Unit - 1)), Raw.Operation_Input)
        and then Source_Padding_Valid (Data (Data'First + Raw.Material'Position .. Data'First + (Raw.Material'Position + Raw.Material'Size / System.Storage_Unit - 1)), Raw.Material);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CO.Raw_Input) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Authority'Position, Raw.Authority'Size / System.Storage_Unit) or else In_Field (Offset, Raw.State'Position, Raw.State'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Bound'Position, Raw.Bound'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Requester'Position, Raw.Requester'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Peer'Position, Raw.Peer'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Collapse'Position, Raw.Collapse'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Authority'Position .. Data'First + (Raw.Authority'Position + Raw.Authority'Size / System.Storage_Unit - 1)), Raw.Authority)
        and then Source_Padding_Valid (Data (Data'First + Raw.State'Position .. Data'First + (Raw.State'Position + Raw.State'Size / System.Storage_Unit - 1)), Raw.State)
        and then Source_Padding_Valid (Data (Data'First + Raw.Bound'Position .. Data'First + (Raw.Bound'Position + Raw.Bound'Size / System.Storage_Unit - 1)), Raw.Bound)
        and then Source_Padding_Valid (Data (Data'First + Raw.Requester'Position .. Data'First + (Raw.Requester'Position + Raw.Requester'Size / System.Storage_Unit - 1)), Raw.Requester)
        and then Source_Padding_Valid (Data (Data'First + Raw.Peer'Position .. Data'First + (Raw.Peer'Position + Raw.Peer'Size / System.Storage_Unit - 1)), Raw.Peer)
        and then Source_Padding_Valid (Data (Data'First + Raw.Collapse'Position .. Data'First + (Raw.Collapse'Position + Raw.Collapse'Size / System.Storage_Unit - 1)), Raw.Collapse);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_State) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Scope'Position .. Data'First + (Raw.Scope'Position + Raw.Scope'Size / System.Storage_Unit - 1)), Raw.Scope)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resource_Epoch'Position .. Data'First + (Raw.Resource_Epoch'Position + Raw.Resource_Epoch'Size / System.Storage_Unit - 1)), Raw.Resource_Epoch)
        and then Source_Padding_Valid (Data (Data'First + Raw.Universe_Head'Position .. Data'First + (Raw.Universe_Head'Position + Raw.Universe_Head'Size / System.Storage_Unit - 1)), Raw.Universe_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Ledger_Head'Position .. Data'First + (Raw.Ledger_Head'Position + Raw.Ledger_Head'Size / System.Storage_Unit - 1)), Raw.Ledger_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Capacity'Position .. Data'First + (Raw.Capacity'Position + Raw.Capacity'Size / System.Storage_Unit - 1)), Raw.Capacity)
        and then Source_Padding_Valid (Data (Data'First + Raw.Held_Total'Position .. Data'First + (Raw.Held_Total'Position + Raw.Held_Total'Size / System.Storage_Unit - 1)), Raw.Held_Total)
        and then Source_Padding_Valid (Data (Data'First + Raw.Charged_Total'Position .. Data'First + (Raw.Charged_Total'Position + Raw.Charged_Total'Size / System.Storage_Unit - 1)), Raw.Charged_Total);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CW.Raw_Request) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Expected_Parent'Position .. Data'First + (Raw.Expected_Parent'Position + Raw.Expected_Parent'Size / System.Storage_Unit - 1)), Raw.Expected_Parent)
        and then Source_Padding_Valid (Data (Data'First + Raw.Candidate_Parent'Position .. Data'First + (Raw.Candidate_Parent'Position + Raw.Candidate_Parent'Size / System.Storage_Unit - 1)), Raw.Candidate_Parent)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Subject'Position .. Data'First + (Raw.Expected_Subject'Position + Raw.Expected_Subject'Size / System.Storage_Unit - 1)), Raw.Expected_Subject)
        and then Source_Padding_Valid (Data (Data'First + Raw.Evidence_Subject'Position .. Data'First + (Raw.Evidence_Subject'Position + Raw.Evidence_Subject'Size / System.Storage_Unit - 1)), Raw.Evidence_Subject)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Base'Position .. Data'First + (Raw.Expected_Base'Position + Raw.Expected_Base'Size / System.Storage_Unit - 1)), Raw.Expected_Base)
        and then Source_Padding_Valid (Data (Data'First + Raw.Candidate_Base'Position .. Data'First + (Raw.Candidate_Base'Position + Raw.Candidate_Base'Size / System.Storage_Unit - 1)), Raw.Candidate_Base)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Delta'Position .. Data'First + (Raw.Expected_Delta'Position + Raw.Expected_Delta'Size / System.Storage_Unit - 1)), Raw.Expected_Delta)
        and then Source_Padding_Valid (Data (Data'First + Raw.Candidate_Delta'Position .. Data'First + (Raw.Candidate_Delta'Position + Raw.Candidate_Delta'Size / System.Storage_Unit - 1)), Raw.Candidate_Delta)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Root_Set'Position .. Data'First + (Raw.Expected_Root_Set'Position + Raw.Expected_Root_Set'Size / System.Storage_Unit - 1)), Raw.Expected_Root_Set)
        and then Source_Padding_Valid (Data (Data'First + Raw.Candidate_Root_Set'Position .. Data'First + (Raw.Candidate_Root_Set'Position + Raw.Candidate_Root_Set'Size / System.Storage_Unit - 1)), Raw.Candidate_Root_Set)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Staged_Root'Position .. Data'First + (Raw.Expected_Staged_Root'Position + Raw.Expected_Staged_Root'Size / System.Storage_Unit - 1)), Raw.Expected_Staged_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Actual_Staged_Root'Position .. Data'First + (Raw.Actual_Staged_Root'Position + Raw.Actual_Staged_Root'Size / System.Storage_Unit - 1)), Raw.Actual_Staged_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Staged_Content_Root'Position .. Data'First + (Raw.Staged_Content_Root'Position + Raw.Staged_Content_Root'Size / System.Storage_Unit - 1)), Raw.Staged_Content_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Tested_Root'Position .. Data'First + (Raw.Tested_Root'Position + Raw.Tested_Root'Size / System.Storage_Unit - 1)), Raw.Tested_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Current_Requirement'Position .. Data'First + (Raw.Current_Requirement'Position + Raw.Current_Requirement'Size / System.Storage_Unit - 1)), Raw.Current_Requirement)
        and then Source_Padding_Valid (Data (Data'First + Raw.Resulting_Requirement'Position .. Data'First + (Raw.Resulting_Requirement'Position + Raw.Resulting_Requirement'Size / System.Storage_Unit - 1)), Raw.Resulting_Requirement)
        and then Source_Padding_Valid (Data (Data'First + Raw.Evaluated_Requirement'Position .. Data'First + (Raw.Evaluated_Requirement'Position + Raw.Evaluated_Requirement'Size / System.Storage_Unit - 1)), Raw.Evaluated_Requirement)
        and then Source_Padding_Valid (Data (Data'First + Raw.Declared_Verifiers'Position .. Data'First + (Raw.Declared_Verifiers'Position + Raw.Declared_Verifiers'Size / System.Storage_Unit - 1)), Raw.Declared_Verifiers)
        and then Source_Padding_Valid (Data (Data'First + Raw.Executed_Verifiers'Position .. Data'First + (Raw.Executed_Verifiers'Position + Raw.Executed_Verifiers'Size / System.Storage_Unit - 1)), Raw.Executed_Verifiers)
        and then Source_Padding_Valid (Data (Data'First + Raw.Staged_Evaluated_Requirement'Position .. Data'First + (Raw.Staged_Evaluated_Requirement'Position + Raw.Staged_Evaluated_Requirement'Size / System.Storage_Unit - 1)), Raw.Staged_Evaluated_Requirement)
        and then Source_Padding_Valid (Data (Data'First + Raw.Staged_Executed_Verifiers'Position .. Data'First + (Raw.Staged_Executed_Verifiers'Position + Raw.Staged_Executed_Verifiers'Size / System.Storage_Unit - 1)), Raw.Staged_Executed_Verifiers)
        and then Source_Padding_Valid (Data (Data'First + Raw.Staged_Examined_Root'Position .. Data'First + (Raw.Staged_Examined_Root'Position + Raw.Staged_Examined_Root'Size / System.Storage_Unit - 1)), Raw.Staged_Examined_Root)
        and then Source_Padding_Valid (Data (Data'First + Raw.Expected_Checkpoint'Position .. Data'First + (Raw.Expected_Checkpoint'Position + Raw.Expected_Checkpoint'Size / System.Storage_Unit - 1)), Raw.Expected_Checkpoint)
        and then Source_Padding_Valid (Data (Data'First + Raw.Witnessed_Checkpoint'Position .. Data'First + (Raw.Witnessed_Checkpoint'Position + Raw.Witnessed_Checkpoint'Size / System.Storage_Unit - 1)), Raw.Witnessed_Checkpoint)
        and then Source_Padding_Valid (Data (Data'First + Raw.Registered_Watch_Set'Position .. Data'First + (Raw.Registered_Watch_Set'Position + Raw.Registered_Watch_Set'Size / System.Storage_Unit - 1)), Raw.Registered_Watch_Set)
        and then Source_Padding_Valid (Data (Data'First + Raw.Watched_Set'Position .. Data'First + (Raw.Watched_Set'Position + Raw.Watched_Set'Size / System.Storage_Unit - 1)), Raw.Watched_Set)
        and then Source_Padding_Valid (Data (Data'First + Raw.Generation_Before'Position .. Data'First + (Raw.Generation_Before'Position + Raw.Generation_Before'Size / System.Storage_Unit - 1)), Raw.Generation_Before)
        and then Source_Padding_Valid (Data (Data'First + Raw.Generation_After'Position .. Data'First + (Raw.Generation_After'Position + Raw.Generation_After'Size / System.Storage_Unit - 1)), Raw.Generation_After);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CW.Raw_Optional_Hash) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Value'Position .. Data'First + (Raw.Value'Position + Raw.Value'Size / System.Storage_Unit - 1)), Raw.Value);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CW.Raw_Bytes_32) return Boolean is
      pragma Unreferenced (Raw);
   begin
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CW.Raw_Optional_Counter) return Boolean is
   begin
      return Source_Padding_Valid (Data (Data'First + Raw.Value_LE'Position .. Data'First + (Raw.Value_LE'Position + Raw.Value_LE'Size / System.Storage_Unit - 1)), Raw.Value_LE);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CW.Raw_Bytes_8) return Boolean is
      pragma Unreferenced (Raw);
   begin
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CX.Raw_Material) return Boolean is
   begin
      for I in Data'Range loop
         declare
            Offset : constant Q.Byte_Count := I - Data'First;
         begin
            if not (In_Field (Offset, Raw.Worker_Issued'Position, Raw.Worker_Issued'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Worker_Recovered'Position, Raw.Worker_Recovered'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Canonical_Issued'Position, Raw.Canonical_Issued'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Canonical_Recovered'Position, Raw.Canonical_Recovered'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Worker_Native'Position, Raw.Worker_Native'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Canonical_Native'Position, Raw.Canonical_Native'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Worker_Receipt_Genesis'Position, Raw.Worker_Receipt_Genesis'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Owner_Receipt_Genesis'Position, Raw.Owner_Receipt_Genesis'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Worker_Receipt_Head'Position, Raw.Worker_Receipt_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Worker_Causal_Genesis'Position, Raw.Worker_Causal_Genesis'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Owner_Causal_Genesis'Position, Raw.Owner_Causal_Genesis'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Worker_Causal_Head'Position, Raw.Worker_Causal_Head'Size / System.Storage_Unit) or else In_Field (Offset, Raw.Quarantine_Head'Position, Raw.Quarantine_Head'Size / System.Storage_Unit)) and then Data (I) /= 0 then return False; end if;
         end;
      end loop;
      return Source_Padding_Valid (Data (Data'First + Raw.Worker_Issued'Position .. Data'First + (Raw.Worker_Issued'Position + Raw.Worker_Issued'Size / System.Storage_Unit - 1)), Raw.Worker_Issued)
        and then Source_Padding_Valid (Data (Data'First + Raw.Worker_Recovered'Position .. Data'First + (Raw.Worker_Recovered'Position + Raw.Worker_Recovered'Size / System.Storage_Unit - 1)), Raw.Worker_Recovered)
        and then Source_Padding_Valid (Data (Data'First + Raw.Canonical_Issued'Position .. Data'First + (Raw.Canonical_Issued'Position + Raw.Canonical_Issued'Size / System.Storage_Unit - 1)), Raw.Canonical_Issued)
        and then Source_Padding_Valid (Data (Data'First + Raw.Canonical_Recovered'Position .. Data'First + (Raw.Canonical_Recovered'Position + Raw.Canonical_Recovered'Size / System.Storage_Unit - 1)), Raw.Canonical_Recovered)
        and then Source_Padding_Valid (Data (Data'First + Raw.Worker_Native'Position .. Data'First + (Raw.Worker_Native'Position + Raw.Worker_Native'Size / System.Storage_Unit - 1)), Raw.Worker_Native)
        and then Source_Padding_Valid (Data (Data'First + Raw.Canonical_Native'Position .. Data'First + (Raw.Canonical_Native'Position + Raw.Canonical_Native'Size / System.Storage_Unit - 1)), Raw.Canonical_Native)
        and then Source_Padding_Valid (Data (Data'First + Raw.Worker_Receipt_Genesis'Position .. Data'First + (Raw.Worker_Receipt_Genesis'Position + Raw.Worker_Receipt_Genesis'Size / System.Storage_Unit - 1)), Raw.Worker_Receipt_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner_Receipt_Genesis'Position .. Data'First + (Raw.Owner_Receipt_Genesis'Position + Raw.Owner_Receipt_Genesis'Size / System.Storage_Unit - 1)), Raw.Owner_Receipt_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Worker_Receipt_Head'Position .. Data'First + (Raw.Worker_Receipt_Head'Position + Raw.Worker_Receipt_Head'Size / System.Storage_Unit - 1)), Raw.Worker_Receipt_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Worker_Causal_Genesis'Position .. Data'First + (Raw.Worker_Causal_Genesis'Position + Raw.Worker_Causal_Genesis'Size / System.Storage_Unit - 1)), Raw.Worker_Causal_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Owner_Causal_Genesis'Position .. Data'First + (Raw.Owner_Causal_Genesis'Position + Raw.Owner_Causal_Genesis'Size / System.Storage_Unit - 1)), Raw.Owner_Causal_Genesis)
        and then Source_Padding_Valid (Data (Data'First + Raw.Worker_Causal_Head'Position .. Data'First + (Raw.Worker_Causal_Head'Position + Raw.Worker_Causal_Head'Size / System.Storage_Unit - 1)), Raw.Worker_Causal_Head)
        and then Source_Padding_Valid (Data (Data'First + Raw.Quarantine_Head'Position .. Data'First + (Raw.Quarantine_Head'Position + Raw.Quarantine_Head'Size / System.Storage_Unit - 1)), Raw.Quarantine_Head);
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : HC.Raw_Result) return Boolean is
      pragma Unreferenced (Raw);
   begin
      return True;
   end Source_Padding_Valid;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CX.Raw_Result) return Boolean is
      pragma Unreferenced (Raw);
   begin
      return True;
   end Source_Padding_Valid;
end Worldline.Retained_Raw_Decode;
