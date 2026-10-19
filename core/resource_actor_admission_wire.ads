with Resource_Actor_Admission;
with Resource_Scoped_Run_Ledger_Wire;
package Resource_Actor_Admission_Wire with SPARK_Mode is
   package A renames Resource_Actor_Admission;
   package N renames Resource_Scoped_Run_Ledger_Wire;
   package W renames N.W;
   package Q renames N.Q;
   use type A.Capability;
   use type Q.Quantity;
   use type Q.Byte_Count;
   type Raw_Observation is record
      Bound : W.Raw_Binding;
      Raw_Frame : W.Raw_Id;
      Raw_Sender : W.Raw_Id;
      Ticket : W.Raw_Id;
      Raw_Proc_Status : W.Raw_Id;
      Raw_Proc_Cgroup : W.Raw_Id;
      Raw_Proc_Maps : W.Raw_Id;
      Raw_Proc_Cmdline : W.Raw_Id;
      Raw_Pidfd_Info : W.Raw_Id;
      Namespace : W.Raw_Id;
      Held_Namespace : W.Raw_Id;
      Helper_Image : W.Raw_Id;
      Expected_Helper_Image : W.Raw_Id;
      Executable_Plan : W.Raw_Id;
      Expected_Executable_Plan : W.Raw_Id;
      Original_Requester : W.Raw_Id;
      Requester_Credentials : W.Raw_Id;
      Expected_Requester_Credentials : W.Raw_Id;
      Dispatch : W.Raw_Id;
      Running_Event : W.Raw_Id;
      Expected_Running_Event : W.Raw_Id;
      Canonical_Use_Event : W.Raw_Id;
      Expected_Canonical_Use_Event : W.Raw_Id;
      Store_Genesis : W.Raw_Id;
      Expected_Store_Genesis : W.Raw_Id;
      Source_Lease : W.Raw_Id;
      Expected_Source_Lease : W.Raw_Id;
      Actor_Wait : W.Raw_Id;
      Helper_Wait : W.Raw_Id;
      Namespace_Wait : W.Raw_Id;
      Host_Pid : W.Raw_Quantity;
      Namespace_Pid : W.Raw_Quantity;
      Sender_Uid : W.Raw_Quantity;
      Sender_Gid : W.Raw_Quantity;
      Real_Uid : W.Raw_Quantity;
      Effective_Uid : W.Raw_Quantity;
      Saved_Uid : W.Raw_Quantity;
      Real_Gid : W.Raw_Quantity;
      Effective_Gid : W.Raw_Quantity;
      Saved_Gid : W.Raw_Quantity;
      Capability_Version : W.Raw_Quantity;
      Effective_Low : W.Raw_Quantity;
      Permitted_Low : W.Raw_Quantity;
      Inheritable_Low : W.Raw_Quantity;
      Effective_High : W.Raw_Quantity;
      Permitted_High : W.Raw_Quantity;
      Inheritable_High : W.Raw_Quantity;
      Securebits : W.Raw_Quantity;
      No_New_Privs : W.Raw_Quantity;
      Requester_Uid : W.Raw_Quantity;
      Requester_Gid : W.Raw_Quantity;
      Configured_Requester_Uid : W.Raw_Quantity;
      Workload_Uid : W.Raw_Quantity;
      Workload_Gid : W.Raw_Quantity;
      Proc_Host_Pid : W.Raw_Quantity;
      Proc_Namespace_Pid : W.Raw_Quantity;
      Proc_Real_Uid : W.Raw_Quantity;
      Proc_Effective_Uid : W.Raw_Quantity;
      Proc_Saved_Uid : W.Raw_Quantity;
      Proc_Real_Gid : W.Raw_Quantity;
      Proc_Effective_Gid : W.Raw_Quantity;
      Proc_Saved_Gid : W.Raw_Quantity;
      Proc_Effective : W.Raw_Quantity;
      Proc_Permitted : W.Raw_Quantity;
      Proc_Inheritable : W.Raw_Quantity;
      Proc_Bounding : W.Raw_Quantity;
      Proc_Ambient : W.Raw_Quantity;
      Proc_No_New_Privs : W.Raw_Quantity;
      Proc_Fs_Uid : W.Raw_Quantity;
      Proc_Fs_Gid : W.Raw_Quantity;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Observation use record
      Bound at 0 range 0 .. 1983;
      Raw_Frame at 248 range 0 .. 191;
      Raw_Sender at 272 range 0 .. 191;
      Ticket at 296 range 0 .. 191;
      Raw_Proc_Status at 320 range 0 .. 191;
      Raw_Proc_Cgroup at 344 range 0 .. 191;
      Raw_Proc_Maps at 368 range 0 .. 191;
      Raw_Proc_Cmdline at 392 range 0 .. 191;
      Raw_Pidfd_Info at 416 range 0 .. 191;
      Namespace at 440 range 0 .. 191;
      Held_Namespace at 464 range 0 .. 191;
      Helper_Image at 488 range 0 .. 191;
      Expected_Helper_Image at 512 range 0 .. 191;
      Executable_Plan at 536 range 0 .. 191;
      Expected_Executable_Plan at 560 range 0 .. 191;
      Original_Requester at 584 range 0 .. 191;
      Requester_Credentials at 608 range 0 .. 191;
      Expected_Requester_Credentials at 632 range 0 .. 191;
      Dispatch at 656 range 0 .. 191;
      Running_Event at 680 range 0 .. 191;
      Expected_Running_Event at 704 range 0 .. 191;
      Canonical_Use_Event at 728 range 0 .. 191;
      Expected_Canonical_Use_Event at 752 range 0 .. 191;
      Store_Genesis at 776 range 0 .. 191;
      Expected_Store_Genesis at 800 range 0 .. 191;
      Source_Lease at 824 range 0 .. 191;
      Expected_Source_Lease at 848 range 0 .. 191;
      Actor_Wait at 872 range 0 .. 191;
      Helper_Wait at 896 range 0 .. 191;
      Namespace_Wait at 920 range 0 .. 191;
      Host_Pid at 944 range 0 .. 191;
      Namespace_Pid at 968 range 0 .. 191;
      Sender_Uid at 992 range 0 .. 191;
      Sender_Gid at 1016 range 0 .. 191;
      Real_Uid at 1040 range 0 .. 191;
      Effective_Uid at 1064 range 0 .. 191;
      Saved_Uid at 1088 range 0 .. 191;
      Real_Gid at 1112 range 0 .. 191;
      Effective_Gid at 1136 range 0 .. 191;
      Saved_Gid at 1160 range 0 .. 191;
      Capability_Version at 1184 range 0 .. 191;
      Effective_Low at 1208 range 0 .. 191;
      Permitted_Low at 1232 range 0 .. 191;
      Inheritable_Low at 1256 range 0 .. 191;
      Effective_High at 1280 range 0 .. 191;
      Permitted_High at 1304 range 0 .. 191;
      Inheritable_High at 1328 range 0 .. 191;
      Securebits at 1352 range 0 .. 191;
      No_New_Privs at 1376 range 0 .. 191;
      Requester_Uid at 1400 range 0 .. 191;
      Requester_Gid at 1424 range 0 .. 191;
      Configured_Requester_Uid at 1448 range 0 .. 191;
      Workload_Uid at 1472 range 0 .. 191;
      Workload_Gid at 1496 range 0 .. 191;
      Proc_Host_Pid at 1520 range 0 .. 191;
      Proc_Namespace_Pid at 1544 range 0 .. 191;
      Proc_Real_Uid at 1568 range 0 .. 191;
      Proc_Effective_Uid at 1592 range 0 .. 191;
      Proc_Saved_Uid at 1616 range 0 .. 191;
      Proc_Real_Gid at 1640 range 0 .. 191;
      Proc_Effective_Gid at 1664 range 0 .. 191;
      Proc_Saved_Gid at 1688 range 0 .. 191;
      Proc_Effective at 1712 range 0 .. 191;
      Proc_Permitted at 1736 range 0 .. 191;
      Proc_Inheritable at 1760 range 0 .. 191;
      Proc_Bounding at 1784 range 0 .. 191;
      Proc_Ambient at 1808 range 0 .. 191;
      Proc_No_New_Privs at 1832 range 0 .. 191;
      Proc_Fs_Uid at 1856 range 0 .. 191;
      Proc_Fs_Gid at 1880 range 0 .. 191;
   end record;
   for Raw_Observation'Size use 15232;
   for Raw_Observation'Object_Size use 15232;
   for Raw_Observation'Alignment use 8;
   type Raw_Capability is record
      Index, Bounding, Ambient : W.Raw_Quantity;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Capability use record
      Index at 0 range 0 .. 191;
      Bounding at 24 range 0 .. 191;
      Ambient at 48 range 0 .. 191;
   end record;
   for Raw_Capability'Size use 576;
   for Raw_Capability'Object_Size use 576;
   for Raw_Capability'Alignment use 8;
   type Raw_Capability_Array is array (Q.Byte_Index range <>) of Raw_Capability;
   type Raw_Group_Array is array (Q.Byte_Index range <>) of W.Raw_Quantity;
   type Raw_Packet is record
      Ledger : N.Raw_Packet;
      Captured : Raw_Observation;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Packet use record
      Ledger at 0 range 0 .. 22015;
      Captured at 2752 range 0 .. 15231;
   end record;
   for Raw_Packet'Size use 37248;
   for Raw_Packet'Object_Size use 37248;
   for Raw_Packet'Alignment use 8;
   function Well_Formed (Data : Q.Byte_Array; V : Raw_Observation) return Boolean is
     (W.Well_Formed (Data, V.Bound)
      and then W.Well_Formed (Data, V.Raw_Frame)
      and then W.Well_Formed (Data, V.Raw_Sender)
      and then W.Well_Formed (Data, V.Ticket)
      and then W.Well_Formed (Data, V.Raw_Proc_Status)
      and then W.Well_Formed (Data, V.Raw_Proc_Cgroup)
      and then W.Well_Formed (Data, V.Raw_Proc_Maps)
      and then W.Well_Formed (Data, V.Raw_Proc_Cmdline)
      and then W.Well_Formed (Data, V.Raw_Pidfd_Info)
      and then W.Well_Formed (Data, V.Namespace)
      and then W.Well_Formed (Data, V.Held_Namespace)
      and then W.Well_Formed (Data, V.Helper_Image)
      and then W.Well_Formed (Data, V.Expected_Helper_Image)
      and then W.Well_Formed (Data, V.Executable_Plan)
      and then W.Well_Formed (Data, V.Expected_Executable_Plan)
      and then W.Well_Formed (Data, V.Original_Requester)
      and then W.Well_Formed (Data, V.Requester_Credentials)
      and then W.Well_Formed (Data, V.Expected_Requester_Credentials)
      and then W.Well_Formed (Data, V.Dispatch)
      and then W.Well_Formed (Data, V.Running_Event)
      and then W.Well_Formed (Data, V.Expected_Running_Event)
      and then W.Well_Formed (Data, V.Canonical_Use_Event)
      and then W.Well_Formed (Data, V.Expected_Canonical_Use_Event)
      and then W.Well_Formed (Data, V.Store_Genesis)
      and then W.Well_Formed (Data, V.Expected_Store_Genesis)
      and then W.Well_Formed (Data, V.Source_Lease)
      and then W.Well_Formed (Data, V.Expected_Source_Lease)
      and then W.Well_Formed (Data, V.Actor_Wait)
      and then W.Well_Formed (Data, V.Helper_Wait)
      and then W.Well_Formed (Data, V.Namespace_Wait)
      and then W.Well_Formed (Data, V.Host_Pid)
      and then W.Well_Formed (Data, V.Namespace_Pid)
      and then W.Well_Formed (Data, V.Sender_Uid)
      and then W.Well_Formed (Data, V.Sender_Gid)
      and then W.Well_Formed (Data, V.Real_Uid)
      and then W.Well_Formed (Data, V.Effective_Uid)
      and then W.Well_Formed (Data, V.Saved_Uid)
      and then W.Well_Formed (Data, V.Real_Gid)
      and then W.Well_Formed (Data, V.Effective_Gid)
      and then W.Well_Formed (Data, V.Saved_Gid)
      and then W.Well_Formed (Data, V.Capability_Version)
      and then W.Well_Formed (Data, V.Effective_Low)
      and then W.Well_Formed (Data, V.Permitted_Low)
      and then W.Well_Formed (Data, V.Inheritable_Low)
      and then W.Well_Formed (Data, V.Effective_High)
      and then W.Well_Formed (Data, V.Permitted_High)
      and then W.Well_Formed (Data, V.Inheritable_High)
      and then W.Well_Formed (Data, V.Securebits)
      and then W.Well_Formed (Data, V.No_New_Privs)
      and then W.Well_Formed (Data, V.Requester_Uid)
      and then W.Well_Formed (Data, V.Requester_Gid)
      and then W.Well_Formed (Data, V.Configured_Requester_Uid)
      and then W.Well_Formed (Data, V.Workload_Uid)
      and then W.Well_Formed (Data, V.Workload_Gid)
      and then W.Well_Formed (Data, V.Proc_Host_Pid)
      and then W.Well_Formed (Data, V.Proc_Namespace_Pid)
      and then W.Well_Formed (Data, V.Proc_Real_Uid)
      and then W.Well_Formed (Data, V.Proc_Effective_Uid)
      and then W.Well_Formed (Data, V.Proc_Saved_Uid)
      and then W.Well_Formed (Data, V.Proc_Real_Gid)
      and then W.Well_Formed (Data, V.Proc_Effective_Gid)
      and then W.Well_Formed (Data, V.Proc_Saved_Gid)
      and then W.Well_Formed (Data, V.Proc_Effective)
      and then W.Well_Formed (Data, V.Proc_Permitted)
      and then W.Well_Formed (Data, V.Proc_Inheritable)
      and then W.Well_Formed (Data, V.Proc_Bounding)
      and then W.Well_Formed (Data, V.Proc_Ambient)
      and then W.Well_Formed (Data, V.Proc_No_New_Privs)
      and then W.Well_Formed (Data, V.Proc_Fs_Uid)
      and then W.Well_Formed (Data, V.Proc_Fs_Gid)
     ) with Global => null;
   function Decode (Data : Q.Byte_Array; V : Raw_Observation) return A.Observation is
     (Bound => W.Decode (Data, V.Bound),
      Raw_Frame => W.Decode (Data, V.Raw_Frame),
      Raw_Sender => W.Decode (Data, V.Raw_Sender),
      Ticket => W.Decode (Data, V.Ticket),
      Raw_Proc_Status => W.Decode (Data, V.Raw_Proc_Status),
      Raw_Proc_Cgroup => W.Decode (Data, V.Raw_Proc_Cgroup),
      Raw_Proc_Maps => W.Decode (Data, V.Raw_Proc_Maps),
      Raw_Proc_Cmdline => W.Decode (Data, V.Raw_Proc_Cmdline),
      Raw_Pidfd_Info => W.Decode (Data, V.Raw_Pidfd_Info),
      Namespace => W.Decode (Data, V.Namespace),
      Held_Namespace => W.Decode (Data, V.Held_Namespace),
      Helper_Image => W.Decode (Data, V.Helper_Image),
      Expected_Helper_Image => W.Decode (Data, V.Expected_Helper_Image),
      Executable_Plan => W.Decode (Data, V.Executable_Plan),
      Expected_Executable_Plan => W.Decode (Data, V.Expected_Executable_Plan),
      Original_Requester => W.Decode (Data, V.Original_Requester),
      Requester_Credentials => W.Decode (Data, V.Requester_Credentials),
      Expected_Requester_Credentials => W.Decode (Data, V.Expected_Requester_Credentials),
      Dispatch => W.Decode (Data, V.Dispatch),
      Running_Event => W.Decode (Data, V.Running_Event),
      Expected_Running_Event => W.Decode (Data, V.Expected_Running_Event),
      Canonical_Use_Event => W.Decode (Data, V.Canonical_Use_Event),
      Expected_Canonical_Use_Event => W.Decode (Data, V.Expected_Canonical_Use_Event),
      Store_Genesis => W.Decode (Data, V.Store_Genesis),
      Expected_Store_Genesis => W.Decode (Data, V.Expected_Store_Genesis),
      Source_Lease => W.Decode (Data, V.Source_Lease),
      Expected_Source_Lease => W.Decode (Data, V.Expected_Source_Lease),
      Actor_Wait => W.Decode (Data, V.Actor_Wait),
      Helper_Wait => W.Decode (Data, V.Helper_Wait),
      Namespace_Wait => W.Decode (Data, V.Namespace_Wait),
      Host_Pid => W.Decode (Data, V.Host_Pid),
      Namespace_Pid => W.Decode (Data, V.Namespace_Pid),
      Sender_Uid => W.Decode (Data, V.Sender_Uid),
      Sender_Gid => W.Decode (Data, V.Sender_Gid),
      Real_Uid => W.Decode (Data, V.Real_Uid),
      Effective_Uid => W.Decode (Data, V.Effective_Uid),
      Saved_Uid => W.Decode (Data, V.Saved_Uid),
      Real_Gid => W.Decode (Data, V.Real_Gid),
      Effective_Gid => W.Decode (Data, V.Effective_Gid),
      Saved_Gid => W.Decode (Data, V.Saved_Gid),
      Capability_Version => W.Decode (Data, V.Capability_Version),
      Effective_Low => W.Decode (Data, V.Effective_Low),
      Permitted_Low => W.Decode (Data, V.Permitted_Low),
      Inheritable_Low => W.Decode (Data, V.Inheritable_Low),
      Effective_High => W.Decode (Data, V.Effective_High),
      Permitted_High => W.Decode (Data, V.Permitted_High),
      Inheritable_High => W.Decode (Data, V.Inheritable_High),
      Securebits => W.Decode (Data, V.Securebits),
      No_New_Privs => W.Decode (Data, V.No_New_Privs),
      Requester_Uid => W.Decode (Data, V.Requester_Uid),
      Requester_Gid => W.Decode (Data, V.Requester_Gid),
      Configured_Requester_Uid => W.Decode (Data, V.Configured_Requester_Uid),
      Workload_Uid => W.Decode (Data, V.Workload_Uid),
      Workload_Gid => W.Decode (Data, V.Workload_Gid),
      Proc_Host_Pid => W.Decode (Data, V.Proc_Host_Pid),
      Proc_Namespace_Pid => W.Decode (Data, V.Proc_Namespace_Pid),
      Proc_Real_Uid => W.Decode (Data, V.Proc_Real_Uid),
      Proc_Effective_Uid => W.Decode (Data, V.Proc_Effective_Uid),
      Proc_Saved_Uid => W.Decode (Data, V.Proc_Saved_Uid),
      Proc_Real_Gid => W.Decode (Data, V.Proc_Real_Gid),
      Proc_Effective_Gid => W.Decode (Data, V.Proc_Effective_Gid),
      Proc_Saved_Gid => W.Decode (Data, V.Proc_Saved_Gid),
      Proc_Effective => W.Decode (Data, V.Proc_Effective),
      Proc_Permitted => W.Decode (Data, V.Proc_Permitted),
      Proc_Inheritable => W.Decode (Data, V.Proc_Inheritable),
      Proc_Bounding => W.Decode (Data, V.Proc_Bounding),
      Proc_Ambient => W.Decode (Data, V.Proc_Ambient),
      Proc_No_New_Privs => W.Decode (Data, V.Proc_No_New_Privs),
      Proc_Fs_Uid => W.Decode (Data, V.Proc_Fs_Uid),
      Proc_Fs_Gid => W.Decode (Data, V.Proc_Fs_Gid)
     ) with Global => null, Pre => Well_Formed (Data, V);
   function Well_Formed (Data : Q.Byte_Array; V : Raw_Capability) return Boolean is
     (W.Well_Formed (Data, V.Index) and then W.Well_Formed (Data, V.Bounding)
      and then W.Well_Formed (Data, V.Ambient)) with Global => null;
   function Decode (Data : Q.Byte_Array; V : Raw_Capability) return A.Capability is
     (Index => W.Decode (Data, V.Index), Bounding => W.Decode (Data, V.Bounding),
      Ambient => W.Decode (Data, V.Ambient)) with Global => null, Pre => Well_Formed (Data, V);
   function Decode_Capabilities (Data : Q.Byte_Array; V : Raw_Capability_Array) return A.Capability_Array
   with Global => null, Pre => (for all I in V'Range => Well_Formed (Data, V (I))),
     Post => Decode_Capabilities'Result'First = V'First and then Decode_Capabilities'Result'Length = V'Length
       and then (for all I in V'Range => Decode_Capabilities'Result (I) = Decode (Data, V (I)));
   function Decode_Groups (Data : Q.Byte_Array; V : Raw_Group_Array) return A.Group_Array
   with Global => null, Pre => (for all I in V'Range => W.Well_Formed (Data, V (I))),
     Post => Decode_Groups'Result'First = V'First and then Decode_Groups'Result'Length = V'Length
       and then (for all I in V'Range => Decode_Groups'Result (I) = W.Decode (Data, V (I)));
end Resource_Actor_Admission_Wire;
