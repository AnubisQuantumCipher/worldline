with Resource_Scoped_Run_Ledger;
with Resource_Run_Ledger;
with Resource_Quantities;
with SPARK.Big_Integers;
package Resource_Actor_Admission with SPARK_Mode is
   package S renames Resource_Scoped_Run_Ledger;
   package L renames Resource_Run_Ledger;
   package Q renames Resource_Quantities;
   use SPARK.Big_Integers;
   package Count_Values is new SPARK.Big_Integers.Signed_Conversions (Q.Byte_Count);
   use type Q.Byte_Count;
   use type Q.Ordering;
   use type L.Phase;
   use type L.Liveness;
   type Observation is record
      Bound : L.Binding;
      Raw_Frame : L.Identity;
      Raw_Sender : L.Identity;
      Ticket : L.Identity;
      Raw_Proc_Status : L.Identity;
      Raw_Proc_Cgroup : L.Identity;
      Raw_Proc_Maps : L.Identity;
      Raw_Proc_Cmdline : L.Identity;
      Raw_Pidfd_Info : L.Identity;
      Namespace : L.Identity;
      Held_Namespace : L.Identity;
      Helper_Image : L.Identity;
      Expected_Helper_Image : L.Identity;
      Executable_Plan : L.Identity;
      Expected_Executable_Plan : L.Identity;
      Original_Requester : L.Identity;
      Requester_Credentials : L.Identity;
      Expected_Requester_Credentials : L.Identity;
      Dispatch : L.Identity;
      Running_Event : L.Identity;
      Expected_Running_Event : L.Identity;
      Canonical_Use_Event : L.Identity;
      Expected_Canonical_Use_Event : L.Identity;
      Store_Genesis : L.Identity;
      Expected_Store_Genesis : L.Identity;
      Source_Lease : L.Identity;
      Expected_Source_Lease : L.Identity;
      Actor_Wait : L.Identity;
      Helper_Wait : L.Identity;
      Namespace_Wait : L.Identity;
      Host_Pid : Q.Quantity;
      Namespace_Pid : Q.Quantity;
      Sender_Uid : Q.Quantity;
      Sender_Gid : Q.Quantity;
      Real_Uid : Q.Quantity;
      Effective_Uid : Q.Quantity;
      Saved_Uid : Q.Quantity;
      Real_Gid : Q.Quantity;
      Effective_Gid : Q.Quantity;
      Saved_Gid : Q.Quantity;
      Capability_Version : Q.Quantity;
      Effective_Low : Q.Quantity;
      Permitted_Low : Q.Quantity;
      Inheritable_Low : Q.Quantity;
      Effective_High : Q.Quantity;
      Permitted_High : Q.Quantity;
      Inheritable_High : Q.Quantity;
      Securebits : Q.Quantity;
      No_New_Privs : Q.Quantity;
      Requester_Uid : Q.Quantity;
      Requester_Gid : Q.Quantity;
      Configured_Requester_Uid : Q.Quantity;
      Workload_Uid : Q.Quantity;
      Workload_Gid : Q.Quantity;
      Proc_Host_Pid : Q.Quantity;
      Proc_Namespace_Pid : Q.Quantity;
      Proc_Real_Uid : Q.Quantity;
      Proc_Effective_Uid : Q.Quantity;
      Proc_Saved_Uid : Q.Quantity;
      Proc_Real_Gid : Q.Quantity;
      Proc_Effective_Gid : Q.Quantity;
      Proc_Saved_Gid : Q.Quantity;
      Proc_Effective : Q.Quantity;
      Proc_Permitted : Q.Quantity;
      Proc_Inheritable : Q.Quantity;
      Proc_Bounding : Q.Quantity;
      Proc_Ambient : Q.Quantity;
      Proc_No_New_Privs : Q.Quantity;
      Proc_Fs_Uid : Q.Quantity;
      Proc_Fs_Gid : Q.Quantity;
   end record;
   type Capability is record
      Index, Bounding, Ambient : Q.Quantity;
   end record;
   type Capability_Array is array (Q.Byte_Index range <>) of Capability;
   type Group_Array is array (Q.Byte_Index range <>) of Q.Quantity;
   type Status is (Ready_Conjunct, Invalid_Ledger, Invalid_Native_Roster,
      Running_Row_Absent, Binding_Mismatch, Requester_Mismatch,
      Source_Mismatch, Credential_Invalid, Isolation_Not_Established);
   function Number (Data : Q.Byte_Array; Item : Q.Quantity) return Boolean is
     (L.T.Nonnegative_Valid (Data, Item)) with Global => null;
   function Eq (Data : Q.Byte_Array; A, B : Q.Quantity) return Boolean is
     (Number (Data, A) and then Number (Data, B)
      and then Q.Compare (Data, A, B) = Q.Equal) with Global => null;
   function Is_Number (Data : Q.Byte_Array; A : Q.Quantity; V : Integer) return Boolean is
     (Number (Data, A) and then L.Exact_Value (Data, A) = To_Big_Integer (V)) with Global => null;
   function Complete (Data : Q.Byte_Array; O : Observation) return Boolean is
     (L.Binding_Valid (Data, O.Bound)
      and then L.Id_Valid (Data, O.Raw_Frame)
      and then L.Id_Valid (Data, O.Raw_Sender)
      and then L.Id_Valid (Data, O.Ticket)
      and then L.Id_Valid (Data, O.Raw_Proc_Status)
      and then L.Id_Valid (Data, O.Raw_Proc_Cgroup)
      and then L.Id_Valid (Data, O.Raw_Proc_Maps)
      and then L.Id_Valid (Data, O.Raw_Proc_Cmdline)
      and then L.Id_Valid (Data, O.Raw_Pidfd_Info)
      and then L.Id_Valid (Data, O.Namespace)
      and then L.Id_Valid (Data, O.Held_Namespace)
      and then L.Id_Valid (Data, O.Helper_Image)
      and then L.Id_Valid (Data, O.Expected_Helper_Image)
      and then L.Id_Valid (Data, O.Executable_Plan)
      and then L.Id_Valid (Data, O.Expected_Executable_Plan)
      and then L.Id_Valid (Data, O.Original_Requester)
      and then L.Id_Valid (Data, O.Requester_Credentials)
      and then L.Id_Valid (Data, O.Expected_Requester_Credentials)
      and then L.Id_Valid (Data, O.Dispatch)
      and then L.Id_Valid (Data, O.Running_Event)
      and then L.Id_Valid (Data, O.Expected_Running_Event)
      and then L.Id_Valid (Data, O.Canonical_Use_Event)
      and then L.Id_Valid (Data, O.Expected_Canonical_Use_Event)
      and then L.Id_Valid (Data, O.Store_Genesis)
      and then L.Id_Valid (Data, O.Expected_Store_Genesis)
      and then L.Id_Valid (Data, O.Source_Lease)
      and then L.Id_Valid (Data, O.Expected_Source_Lease)
      and then L.Id_Valid (Data, O.Actor_Wait)
      and then L.Id_Valid (Data, O.Helper_Wait)
      and then L.Id_Valid (Data, O.Namespace_Wait)
      and then Number (Data, O.Host_Pid)
      and then Number (Data, O.Namespace_Pid)
      and then Number (Data, O.Sender_Uid)
      and then Number (Data, O.Sender_Gid)
      and then Number (Data, O.Real_Uid)
      and then Number (Data, O.Effective_Uid)
      and then Number (Data, O.Saved_Uid)
      and then Number (Data, O.Real_Gid)
      and then Number (Data, O.Effective_Gid)
      and then Number (Data, O.Saved_Gid)
      and then Number (Data, O.Capability_Version)
      and then Number (Data, O.Effective_Low)
      and then Number (Data, O.Permitted_Low)
      and then Number (Data, O.Inheritable_Low)
      and then Number (Data, O.Effective_High)
      and then Number (Data, O.Permitted_High)
      and then Number (Data, O.Inheritable_High)
      and then Number (Data, O.Securebits)
      and then Number (Data, O.No_New_Privs)
      and then Number (Data, O.Requester_Uid)
      and then Number (Data, O.Requester_Gid)
      and then Number (Data, O.Configured_Requester_Uid)
      and then Number (Data, O.Workload_Uid)
      and then Number (Data, O.Workload_Gid)
      and then Number (Data, O.Proc_Host_Pid)
      and then Number (Data, O.Proc_Namespace_Pid)
      and then Number (Data, O.Proc_Real_Uid)
      and then Number (Data, O.Proc_Effective_Uid)
      and then Number (Data, O.Proc_Saved_Uid)
      and then Number (Data, O.Proc_Real_Gid)
      and then Number (Data, O.Proc_Effective_Gid)
      and then Number (Data, O.Proc_Saved_Gid)
      and then Number (Data, O.Proc_Effective)
      and then Number (Data, O.Proc_Permitted)
      and then Number (Data, O.Proc_Inheritable)
      and then Number (Data, O.Proc_Bounding)
      and then Number (Data, O.Proc_Ambient)
      and then Number (Data, O.Proc_No_New_Privs)
      and then Number (Data, O.Proc_Fs_Uid)
      and then Number (Data, O.Proc_Fs_Gid)
     ) with Global => null;
   function Requester_Holds (Data : Q.Byte_Array; O : Observation) return Boolean is
     (Complete (Data, O)
      and then L.Same (Data, O.Original_Requester, O.Bound.Owner)
      and then L.Same (Data, O.Requester_Credentials, O.Expected_Requester_Credentials)
      and then Eq (Data, O.Requester_Uid, O.Configured_Requester_Uid)) with Global => null;
   function Source_Holds (Data : Q.Byte_Array; O : Observation) return Boolean is
     (Complete (Data, O)
      and then L.Same (Data, O.Running_Event, O.Expected_Running_Event)
      and then L.Same (Data, O.Canonical_Use_Event, O.Expected_Canonical_Use_Event)
      and then L.Same (Data, O.Store_Genesis, O.Expected_Store_Genesis)
      and then L.Same (Data, O.Source_Lease, O.Expected_Source_Lease)
      and then L.Same (Data, O.Helper_Image, O.Expected_Helper_Image)
      and then L.Same (Data, O.Executable_Plan, O.Expected_Executable_Plan)
      and then L.Same (Data, O.Namespace, O.Held_Namespace)) with Global => null;
   function Credential_Holds (Data : Q.Byte_Array; O : Observation) return Boolean is
     (Complete (Data, O)
      and then L.Exact_Value (Data, O.Host_Pid) > To_Big_Integer (0)
      and then L.Exact_Value (Data, O.Namespace_Pid) > To_Big_Integer (1)
      and then Eq (Data, O.Host_Pid, O.Proc_Host_Pid)
      and then Eq (Data, O.Namespace_Pid, O.Proc_Namespace_Pid)
      and then L.Exact_Value (Data, O.Workload_Uid) > To_Big_Integer (0)
      and then Eq (Data, O.Sender_Uid, O.Workload_Uid)
      and then Eq (Data, O.Sender_Gid, O.Workload_Gid)
      and then Eq (Data, O.Proc_Fs_Uid, O.Workload_Uid)
      and then Eq (Data, O.Proc_Fs_Gid, O.Workload_Gid)
      and then S.K.Text (Data, O.Actor_Wait, "PIDFD_LIVE")
      and then S.K.Text (Data, O.Helper_Wait, "PIDFD_LIVE")
      and then S.K.Text (Data, O.Namespace_Wait, "PIDFD_LIVE")
      and then Eq (Data, O.Real_Uid, O.Workload_Uid)
      and then Eq (Data, O.Proc_Real_Uid, O.Real_Uid)
      and then Eq (Data, O.Effective_Uid, O.Workload_Uid)
      and then Eq (Data, O.Proc_Effective_Uid, O.Effective_Uid)
      and then Eq (Data, O.Saved_Uid, O.Workload_Uid)
      and then Eq (Data, O.Proc_Saved_Uid, O.Saved_Uid)
      and then Eq (Data, O.Real_Gid, O.Workload_Gid)
      and then Eq (Data, O.Proc_Real_Gid, O.Real_Gid)
      and then Eq (Data, O.Effective_Gid, O.Workload_Gid)
      and then Eq (Data, O.Proc_Effective_Gid, O.Effective_Gid)
      and then Eq (Data, O.Saved_Gid, O.Workload_Gid)
      and then Eq (Data, O.Proc_Saved_Gid, O.Saved_Gid)
      and then Is_Number (Data, O.Effective_Low, 0)
      and then Is_Number (Data, O.Permitted_Low, 0)
      and then Is_Number (Data, O.Inheritable_Low, 0)
      and then Is_Number (Data, O.Effective_High, 0)
      and then Is_Number (Data, O.Permitted_High, 0)
      and then Is_Number (Data, O.Inheritable_High, 0)
      and then Is_Number (Data, O.Proc_Effective, 0)
      and then Is_Number (Data, O.Proc_Permitted, 0)
      and then Is_Number (Data, O.Proc_Inheritable, 0)
      and then Is_Number (Data, O.Proc_Bounding, 0)
      and then Is_Number (Data, O.Proc_Ambient, 0)
      -- Values read from the installed Linux capability/securebits headers;
      -- securebits mask arithmetic is retained in the separate JACKAL receipt.
      and then Is_Number (Data, O.Capability_Version, 16#20080522#)
      and then Is_Number (Data, O.Securebits, 15)
      and then Is_Number (Data, O.No_New_Privs, 1)
      and then Is_Number (Data, O.Proc_No_New_Privs, 1)) with Global => null;
   function Isolation_Reference (Data : Q.Byte_Array; C : Capability_Array;
                                G, Proc_G : Group_Array) return Boolean is
     (G'Length = 0 and then Proc_G'Length = 0 and then C'Length > 0
      and then (for all I in C'Range => Number (Data, C (I).Index)
        and then L.Exact_Value (Data, C (I).Index) = Count_Values.To_Big_Integer (I - C'First)
        and then Is_Number (Data, C (I).Bounding, 0)
        and then Is_Number (Data, C (I).Ambient, 0))) with Ghost, Global => null;
   function Isolation (Data : Q.Byte_Array; C : Capability_Array;
                       G, Proc_G : Group_Array) return Boolean
   with Global => null, Post => Isolation'Result = Isolation_Reference (Data, C, G, Proc_G);
   function Running_Holds (Data : Q.Byte_Array; State : S.State; H : S.History_Array;
                          Rows : L.Row_Array; N : L.Native_Array; F : S.Facts_Array; O : Observation) return Boolean is
     (N'Length = Rows'Length and then F'Length = Rows'Length and then (for some I in Rows'Range =>
        S.Retained_Origin (Data, State, H, Rows (I))
        and then L.Same_Binding (Data, Rows (I).Bound, O.Bound)
        -- An immutable original row need not acquire the current policy scope.
        -- Fresh permission comes from the closed canonical/scoped composite;
        -- this conjunct retains and validates the genuine original scope.
        and then L.Same (Data, O.Dispatch, F (F'First + (I - Rows'First)).Dispatch)
        and then L.Same (Data, O.Namespace, F (F'First + (I - Rows'First)).Namespace)
        and then L.Same (Data, O.Helper_Image, F (F'First + (I - Rows'First)).Helper_Image)
        and then Rows (I).State = L.Running
        and then N (N'First + (I - Rows'First)).Observed = L.Live)) with Global => null;
   function Reference (Data : Q.Byte_Array; State : S.State; H : S.History_Array;
                       Rows : L.Row_Array; P : S.Projection_Array; B : S.Bucket_Array;
                       N : L.Native_Array; F : S.Facts_Array; Current : S.Current_Observation;
                       O : Observation; C : Capability_Array; G, Proc_G : Group_Array) return Status is
     (if not S.Valid_Reference (Data, State, H, Rows, P, B, Current) then Invalid_Ledger
      elsif not S.Native_Valid (Data, State, H, Rows, N, F) then Invalid_Native_Roster
      elsif not Complete (Data, O) then Credential_Invalid
      elsif not Running_Holds (Data, State, H, Rows, N, F, O) then Running_Row_Absent
      elsif not Requester_Holds (Data, O) then Requester_Mismatch
      elsif not Source_Holds (Data, O) then Source_Mismatch
      elsif not Credential_Holds (Data, O) then Credential_Invalid
      elsif not Isolation_Reference (Data, C, G, Proc_G) then Isolation_Not_Established
      else Ready_Conjunct) with Ghost, Global => null;
   function Check (Data : Q.Byte_Array; State : S.State; H : S.History_Array;
                   Rows : L.Row_Array; P : S.Projection_Array; B : S.Bucket_Array;
                   N : L.Native_Array; F : S.Facts_Array; Current : S.Current_Observation;
                   O : Observation; C : Capability_Array; G, Proc_G : Group_Array) return Status
   with Global => null,
     Post => Check'Result = Reference (Data, State, H, Rows, P, B, N, F, Current, O, C, G, Proc_G);
end Resource_Actor_Admission;
