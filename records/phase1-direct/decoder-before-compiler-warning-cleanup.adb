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
   --  Field slice constants match the compiler-verified representation clauses
   --  in the wire packages. The native-layout tests cross-check every schema;
   --  do not change these boundaries independently of the wire ABI.
   function Load (Data : Q.Byte_Array) return D.Raw_Packet is
   begin
      return
        (Ledger => Load (Data (Data'First + 0 .. Data'First + (0 + 2752 - 1))),
         Captured => Load (Data (Data'First + 2752 .. Data'First + (2752 + 1904 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Packet is
   begin
      return
        (Schema_Version => Interfaces.Unsigned_32 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 4 - 1)))),
         Before_State => Load (Data (Data'First + 8 .. Data'First + (8 + 352 - 1))),
         Proposed_State => Load (Data (Data'First + 360 .. Data'First + (360 + 352 - 1))),
         Current => Load (Data (Data'First + 712 .. Data'First + (712 + 592 - 1))),
         Request => Load (Data (Data'First + 1304 .. Data'First + (1304 + 1448 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_State is
   begin
      return
        (Current => Load (Data (Data'First + 0 .. Data'First + (0 + 224 - 1))),
         Resource_Epoch => Load (Data (Data'First + 224 .. Data'First + (224 + 32 - 1))),
         Universe_Head => Load (Data (Data'First + 256 .. Data'First + (256 + 24 - 1))),
         Ledger_Head => Load (Data (Data'First + 280 .. Data'First + (280 + 24 - 1))),
         History_Head => Load (Data (Data'First + 304 .. Data'First + (304 + 24 - 1))),
         Physical_Head => Load (Data (Data'First + 328 .. Data'First + (328 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Context is
   begin
      return
        (Universe => Load (Data (Data'First + 0 .. Data'First + (0 + 24 - 1))),
         Policy => Load (Data (Data'First + 24 .. Data'First + (24 + 24 - 1))),
         Resource => Load (Data (Data'First + 48 .. Data'First + (48 + 24 - 1))),
         Unit => Load (Data (Data'First + 72 .. Data'First + (72 + 24 - 1))),
         Instance => Load (Data (Data'First + 96 .. Data'First + (96 + 24 - 1))),
         Host => Load (Data (Data'First + 120 .. Data'First + (120 + 24 - 1))),
         Boot => Load (Data (Data'First + 144 .. Data'First + (144 + 24 - 1))),
         Authority => Load (Data (Data'First + 168 .. Data'First + (168 + 24 - 1))),
         Policy_Epoch => Load (Data (Data'First + 192 .. Data'First + (192 + 32 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Id is
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         First => Signed (Data (Data'First + 8 .. Data'First + (8 + 8 - 1))),
         Length => Signed (Data (Data'First + 16 .. Data'First + (16 + 8 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Epoch is
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         Value => Load (Data (Data'First + 8 .. Data'First + (8 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Quantity is
   begin
      return
        (Negative => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         First => Signed (Data (Data'First + 8 .. Data'First + (8 + 8 - 1))),
         Length => Signed (Data (Data'First + 16 .. Data'First + (16 + 8 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Current_Observation is
   begin
      return
        (Scope => Load (Data (Data'First + 0 .. Data'First + (0 + 224 - 1))),
         Resource_Epoch => Load (Data (Data'First + 224 .. Data'First + (224 + 32 - 1))),
         Universe_Head => Load (Data (Data'First + 256 .. Data'First + (256 + 24 - 1))),
         Ledger_Head => Load (Data (Data'First + 280 .. Data'First + (280 + 24 - 1))),
         History_Head => Load (Data (Data'First + 304 .. Data'First + (304 + 24 - 1))),
         Physical_Head => Load (Data (Data'First + 328 .. Data'First + (328 + 24 - 1))),
         Store_Genesis => Load (Data (Data'First + 352 .. Data'First + (352 + 24 - 1))),
         Store_Id => Load (Data (Data'First + 376 .. Data'First + (376 + 24 - 1))),
         Root_Head => Load (Data (Data'First + 400 .. Data'First + (400 + 24 - 1))),
         Prime => Load (Data (Data'First + 424 .. Data'First + (424 + 24 - 1))),
         Root_Count => Load (Data (Data'First + 448 .. Data'First + (448 + 24 - 1))),
         Cause => Load (Data (Data'First + 472 .. Data'First + (472 + 24 - 1))),
         Requester => Load (Data (Data'First + 496 .. Data'First + (496 + 24 - 1))),
         Receipt => Load (Data (Data'First + 520 .. Data'First + (520 + 24 - 1))),
         Catalogue_Head => Load (Data (Data'First + 544 .. Data'First + (544 + 24 - 1))),
         Observation_Head => Load (Data (Data'First + 568 .. Data'First + (568 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Intent is
   begin
      return
        (Kind => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         Original => Load (Data (Data'First + 8 .. Data'First + (8 + 1288 - 1))),
         Expected_Epoch => Load (Data (Data'First + 1296 .. Data'First + (1296 + 32 - 1))),
         Expected_Ledger_Head => Load (Data (Data'First + 1328 .. Data'First + (1328 + 24 - 1))),
         Request_Id => Load (Data (Data'First + 1352 .. Data'First + (1352 + 24 - 1))),
         Cause => Load (Data (Data'First + 1376 .. Data'First + (1376 + 24 - 1))),
         Requester => Load (Data (Data'First + 1400 .. Data'First + (1400 + 24 - 1))),
         Receipt => Load (Data (Data'First + 1424 .. Data'First + (1424 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Request is
   begin
      return
        (Kind => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         Scope => Load (Data (Data'First + 8 .. Data'First + (8 + 224 - 1))),
         Expected_Epoch => Load (Data (Data'First + 232 .. Data'First + (232 + 32 - 1))),
         Expected_Ledger_Head => Load (Data (Data'First + 264 .. Data'First + (264 + 24 - 1))),
         Request_Id => Load (Data (Data'First + 288 .. Data'First + (288 + 24 - 1))),
         Reservation => Load (Data (Data'First + 312 .. Data'First + (312 + 24 - 1))),
         Operation_Id => Load (Data (Data'First + 336 .. Data'First + (336 + 24 - 1))),
         Requester => Load (Data (Data'First + 360 .. Data'First + (360 + 24 - 1))),
         Bound => Load (Data (Data'First + 384 .. Data'First + (384 + 248 - 1))),
         New_Row => Load (Data (Data'First + 632 .. Data'First + (632 + 656 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Binding is
   begin
      return
        (Reservation => Load (Data (Data'First + 0 .. Data'First + (0 + 24 - 1))),
         Operation => Load (Data (Data'First + 24 .. Data'First + (24 + 24 - 1))),
         Owner => Load (Data (Data'First + 48 .. Data'First + (48 + 24 - 1))),
         Workload => Load (Data (Data'First + 72 .. Data'First + (72 + 24 - 1))),
         Universe_Head => Load (Data (Data'First + 96 .. Data'First + (96 + 24 - 1))),
         Capability => Load (Data (Data'First + 120 .. Data'First + (120 + 24 - 1))),
         Grant_Use => Load (Data (Data'First + 144 .. Data'First + (144 + 24 - 1))),
         Payload => Load (Data (Data'First + 168 .. Data'First + (168 + 24 - 1))),
         Provenance => Load (Data (Data'First + 192 .. Data'First + (192 + 24 - 1))),
         Resource_Epoch => Load (Data (Data'First + 216 .. Data'First + (216 + 32 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Row is
   begin
      return
        (Scope => Load (Data (Data'First + 0 .. Data'First + (0 + 224 - 1))),
         Bound => Load (Data (Data'First + 224 .. Data'First + (224 + 248 - 1))),
         Parent => Load (Data (Data'First + 472 .. Data'First + (472 + 24 - 1))),
         Kind => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 496 .. Data'First + (496 + 1 - 1)))),
         State => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 497 .. Data'First + (497 + 1 - 1)))),
         Amount => Load (Data (Data'First + 504 .. Data'First + (504 + 24 - 1))),
         Observed_Usage => Load (Data (Data'First + 528 .. Data'First + (528 + 32 - 1))),
         Planned_Unit => Load (Data (Data'First + 560 .. Data'First + (560 + 24 - 1))),
         Actual_Unit => Load (Data (Data'First + 584 .. Data'First + (584 + 24 - 1))),
         Cgroup => Load (Data (Data'First + 608 .. Data'First + (608 + 24 - 1))),
         Invocation => Load (Data (Data'First + 632 .. Data'First + (632 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return D.Raw_Observation is
   begin
      return
        (Bound => Load (Data (Data'First + 0 .. Data'First + (0 + 248 - 1))),
         Raw_Frame => Load (Data (Data'First + 248 .. Data'First + (248 + 24 - 1))),
         Raw_Sender => Load (Data (Data'First + 272 .. Data'First + (272 + 24 - 1))),
         Ticket => Load (Data (Data'First + 296 .. Data'First + (296 + 24 - 1))),
         Raw_Proc_Status => Load (Data (Data'First + 320 .. Data'First + (320 + 24 - 1))),
         Raw_Proc_Cgroup => Load (Data (Data'First + 344 .. Data'First + (344 + 24 - 1))),
         Raw_Proc_Maps => Load (Data (Data'First + 368 .. Data'First + (368 + 24 - 1))),
         Raw_Proc_Cmdline => Load (Data (Data'First + 392 .. Data'First + (392 + 24 - 1))),
         Raw_Pidfd_Info => Load (Data (Data'First + 416 .. Data'First + (416 + 24 - 1))),
         Namespace => Load (Data (Data'First + 440 .. Data'First + (440 + 24 - 1))),
         Held_Namespace => Load (Data (Data'First + 464 .. Data'First + (464 + 24 - 1))),
         Helper_Image => Load (Data (Data'First + 488 .. Data'First + (488 + 24 - 1))),
         Expected_Helper_Image => Load (Data (Data'First + 512 .. Data'First + (512 + 24 - 1))),
         Executable_Plan => Load (Data (Data'First + 536 .. Data'First + (536 + 24 - 1))),
         Expected_Executable_Plan => Load (Data (Data'First + 560 .. Data'First + (560 + 24 - 1))),
         Original_Requester => Load (Data (Data'First + 584 .. Data'First + (584 + 24 - 1))),
         Requester_Credentials => Load (Data (Data'First + 608 .. Data'First + (608 + 24 - 1))),
         Expected_Requester_Credentials => Load (Data (Data'First + 632 .. Data'First + (632 + 24 - 1))),
         Dispatch => Load (Data (Data'First + 656 .. Data'First + (656 + 24 - 1))),
         Running_Event => Load (Data (Data'First + 680 .. Data'First + (680 + 24 - 1))),
         Expected_Running_Event => Load (Data (Data'First + 704 .. Data'First + (704 + 24 - 1))),
         Canonical_Use_Event => Load (Data (Data'First + 728 .. Data'First + (728 + 24 - 1))),
         Expected_Canonical_Use_Event => Load (Data (Data'First + 752 .. Data'First + (752 + 24 - 1))),
         Store_Genesis => Load (Data (Data'First + 776 .. Data'First + (776 + 24 - 1))),
         Expected_Store_Genesis => Load (Data (Data'First + 800 .. Data'First + (800 + 24 - 1))),
         Source_Lease => Load (Data (Data'First + 824 .. Data'First + (824 + 24 - 1))),
         Expected_Source_Lease => Load (Data (Data'First + 848 .. Data'First + (848 + 24 - 1))),
         Actor_Wait => Load (Data (Data'First + 872 .. Data'First + (872 + 24 - 1))),
         Helper_Wait => Load (Data (Data'First + 896 .. Data'First + (896 + 24 - 1))),
         Namespace_Wait => Load (Data (Data'First + 920 .. Data'First + (920 + 24 - 1))),
         Host_Pid => Load (Data (Data'First + 944 .. Data'First + (944 + 24 - 1))),
         Namespace_Pid => Load (Data (Data'First + 968 .. Data'First + (968 + 24 - 1))),
         Sender_Uid => Load (Data (Data'First + 992 .. Data'First + (992 + 24 - 1))),
         Sender_Gid => Load (Data (Data'First + 1016 .. Data'First + (1016 + 24 - 1))),
         Real_Uid => Load (Data (Data'First + 1040 .. Data'First + (1040 + 24 - 1))),
         Effective_Uid => Load (Data (Data'First + 1064 .. Data'First + (1064 + 24 - 1))),
         Saved_Uid => Load (Data (Data'First + 1088 .. Data'First + (1088 + 24 - 1))),
         Real_Gid => Load (Data (Data'First + 1112 .. Data'First + (1112 + 24 - 1))),
         Effective_Gid => Load (Data (Data'First + 1136 .. Data'First + (1136 + 24 - 1))),
         Saved_Gid => Load (Data (Data'First + 1160 .. Data'First + (1160 + 24 - 1))),
         Capability_Version => Load (Data (Data'First + 1184 .. Data'First + (1184 + 24 - 1))),
         Effective_Low => Load (Data (Data'First + 1208 .. Data'First + (1208 + 24 - 1))),
         Permitted_Low => Load (Data (Data'First + 1232 .. Data'First + (1232 + 24 - 1))),
         Inheritable_Low => Load (Data (Data'First + 1256 .. Data'First + (1256 + 24 - 1))),
         Effective_High => Load (Data (Data'First + 1280 .. Data'First + (1280 + 24 - 1))),
         Permitted_High => Load (Data (Data'First + 1304 .. Data'First + (1304 + 24 - 1))),
         Inheritable_High => Load (Data (Data'First + 1328 .. Data'First + (1328 + 24 - 1))),
         Securebits => Load (Data (Data'First + 1352 .. Data'First + (1352 + 24 - 1))),
         No_New_Privs => Load (Data (Data'First + 1376 .. Data'First + (1376 + 24 - 1))),
         Requester_Uid => Load (Data (Data'First + 1400 .. Data'First + (1400 + 24 - 1))),
         Requester_Gid => Load (Data (Data'First + 1424 .. Data'First + (1424 + 24 - 1))),
         Configured_Requester_Uid => Load (Data (Data'First + 1448 .. Data'First + (1448 + 24 - 1))),
         Workload_Uid => Load (Data (Data'First + 1472 .. Data'First + (1472 + 24 - 1))),
         Workload_Gid => Load (Data (Data'First + 1496 .. Data'First + (1496 + 24 - 1))),
         Proc_Host_Pid => Load (Data (Data'First + 1520 .. Data'First + (1520 + 24 - 1))),
         Proc_Namespace_Pid => Load (Data (Data'First + 1544 .. Data'First + (1544 + 24 - 1))),
         Proc_Real_Uid => Load (Data (Data'First + 1568 .. Data'First + (1568 + 24 - 1))),
         Proc_Effective_Uid => Load (Data (Data'First + 1592 .. Data'First + (1592 + 24 - 1))),
         Proc_Saved_Uid => Load (Data (Data'First + 1616 .. Data'First + (1616 + 24 - 1))),
         Proc_Real_Gid => Load (Data (Data'First + 1640 .. Data'First + (1640 + 24 - 1))),
         Proc_Effective_Gid => Load (Data (Data'First + 1664 .. Data'First + (1664 + 24 - 1))),
         Proc_Saved_Gid => Load (Data (Data'First + 1688 .. Data'First + (1688 + 24 - 1))),
         Proc_Effective => Load (Data (Data'First + 1712 .. Data'First + (1712 + 24 - 1))),
         Proc_Permitted => Load (Data (Data'First + 1736 .. Data'First + (1736 + 24 - 1))),
         Proc_Inheritable => Load (Data (Data'First + 1760 .. Data'First + (1760 + 24 - 1))),
         Proc_Bounding => Load (Data (Data'First + 1784 .. Data'First + (1784 + 24 - 1))),
         Proc_Ambient => Load (Data (Data'First + 1808 .. Data'First + (1808 + 24 - 1))),
         Proc_No_New_Privs => Load (Data (Data'First + 1832 .. Data'First + (1832 + 24 - 1))),
         Proc_Fs_Uid => Load (Data (Data'First + 1856 .. Data'First + (1856 + 24 - 1))),
         Proc_Fs_Gid => Load (Data (Data'First + 1880 .. Data'First + (1880 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return X.Raw_Crosswalk is
   begin
      return
        (Resource_Current => Load (Data (Data'First + 0 .. Data'First + (0 + 592 - 1))),
         Operation_Policy => Load (Data (Data'First + 592 .. Data'First + (592 + 33 - 1))),
         Operation_Root_Set => Load (Data (Data'First + 625 .. Data'First + (625 + 33 - 1))),
         Owner_Genesis => Load (Data (Data'First + 664 .. Data'First + (664 + 24 - 1))),
         Installation => Load (Data (Data'First + 688 .. Data'First + (688 + 24 - 1))),
         Gate_Config => Load (Data (Data'First + 712 .. Data'First + (712 + 24 - 1))),
         Managed_Observation => Load (Data (Data'First + 736 .. Data'First + (736 + 24 - 1))),
         Original_Grant => Load (Data (Data'First + 760 .. Data'First + (760 + 24 - 1))),
         Complete_Crosswalk => Load (Data (Data'First + 784 .. Data'First + (784 + 24 - 1))),
         Current_Source => Load (Data (Data'First + 808 .. Data'First + (808 + 24 - 1))),
         Original_Request => Load (Data (Data'First + 832 .. Data'First + (832 + 24 - 1))),
         Original_Requester => Load (Data (Data'First + 856 .. Data'First + (856 + 24 - 1))),
         Original_Transaction => Load (Data (Data'First + 880 .. Data'First + (880 + 24 - 1))),
         Preparer => Load (Data (Data'First + 904 .. Data'First + (904 + 24 - 1))),
         Selected_Plan => Load (Data (Data'First + 928 .. Data'First + (928 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return C.Raw_Digest is
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         Value => Load (Data (Data'First + 1 .. Data'First + (1 + 32 - 1))));
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
   begin
      return
        (Mode => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         Controller => Load (Data (Data'First + 8 .. Data'First + (8 + 1256 - 1))),
         Child_Task => Load (Data (Data'First + 1264 .. Data'First + (1264 + 1224 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return Y.Raw_Controller is
   begin
      return
        (Bound => Load (Data (Data'First + 0 .. Data'First + (0 + 248 - 1))),
         Process => Load (Data (Data'First + 248 .. Data'First + (248 + 528 - 1))),
         Requester_Uid => Load (Data (Data'First + 776 .. Data'First + (776 + 24 - 1))),
         Requester_Gid => Load (Data (Data'First + 800 .. Data'First + (800 + 24 - 1))),
         raw_manager => Load (Data (Data'First + 824 .. Data'First + (824 + 24 - 1))),
         raw_channel => Load (Data (Data'First + 848 .. Data'First + (848 + 24 - 1))),
         owner_endpoint => Load (Data (Data'First + 872 .. Data'First + (872 + 24 - 1))),
         expected_owner_endpoint => Load (Data (Data'First + 896 .. Data'First + (896 + 24 - 1))),
         source_lease => Load (Data (Data'First + 920 .. Data'First + (920 + 24 - 1))),
         expected_source_lease => Load (Data (Data'First + 944 .. Data'First + (944 + 24 - 1))),
         worker_image => Load (Data (Data'First + 968 .. Data'First + (968 + 24 - 1))),
         expected_worker_image => Load (Data (Data'First + 992 .. Data'First + (992 + 24 - 1))),
         handler_plan => Load (Data (Data'First + 1016 .. Data'First + (1016 + 24 - 1))),
         expected_handler_plan => Load (Data (Data'First + 1040 .. Data'First + (1040 + 24 - 1))),
         raw_request => Load (Data (Data'First + 1064 .. Data'First + (1064 + 24 - 1))),
         requester => Load (Data (Data'First + 1088 .. Data'First + (1088 + 24 - 1))),
         dispatch => Load (Data (Data'First + 1112 .. Data'First + (1112 + 24 - 1))),
         running_event => Load (Data (Data'First + 1136 .. Data'First + (1136 + 24 - 1))),
         expected_running_event => Load (Data (Data'First + 1160 .. Data'First + (1160 + 24 - 1))),
         store_genesis => Load (Data (Data'First + 1184 .. Data'First + (1184 + 24 - 1))),
         expected_store_genesis => Load (Data (Data'First + 1208 .. Data'First + (1208 + 24 - 1))),
         current_source => Load (Data (Data'First + 1232 .. Data'First + (1232 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return Y.Raw_Process is
   begin
      return
        (raw_status => Load (Data (Data'First + 0 .. Data'First + (0 + 24 - 1))),
         raw_stat => Load (Data (Data'First + 24 .. Data'First + (24 + 24 - 1))),
         raw_cgroup => Load (Data (Data'First + 48 .. Data'First + (48 + 24 - 1))),
         raw_maps => Load (Data (Data'First + 72 .. Data'First + (72 + 24 - 1))),
         raw_cmdline => Load (Data (Data'First + 96 .. Data'First + (96 + 24 - 1))),
         raw_pidfd_info => Load (Data (Data'First + 120 .. Data'First + (120 + 24 - 1))),
         namespace => Load (Data (Data'First + 144 .. Data'First + (144 + 24 - 1))),
         cgroup => Load (Data (Data'First + 168 .. Data'First + (168 + 24 - 1))),
         actual_unit => Load (Data (Data'First + 192 .. Data'First + (192 + 24 - 1))),
         invocation => Load (Data (Data'First + 216 .. Data'First + (216 + 24 - 1))),
         source_lease => Load (Data (Data'First + 240 .. Data'First + (240 + 24 - 1))),
         pidfd_wait => Load (Data (Data'First + 264 .. Data'First + (264 + 24 - 1))),
         host_pid => Load (Data (Data'First + 288 .. Data'First + (288 + 24 - 1))),
         start_tick => Load (Data (Data'First + 312 .. Data'First + (312 + 24 - 1))),
         parent_pid => Load (Data (Data'First + 336 .. Data'First + (336 + 24 - 1))),
         parent_start_tick => Load (Data (Data'First + 360 .. Data'First + (360 + 24 - 1))),
         real_uid => Load (Data (Data'First + 384 .. Data'First + (384 + 24 - 1))),
         effective_uid => Load (Data (Data'First + 408 .. Data'First + (408 + 24 - 1))),
         saved_uid => Load (Data (Data'First + 432 .. Data'First + (432 + 24 - 1))),
         real_gid => Load (Data (Data'First + 456 .. Data'First + (456 + 24 - 1))),
         effective_gid => Load (Data (Data'First + 480 .. Data'First + (480 + 24 - 1))),
         saved_gid => Load (Data (Data'First + 504 .. Data'First + (504 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return Y.Raw_Task is
   begin
      return
        (Action => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         Root => Load (Data (Data'First + 8 .. Data'First + (8 + 248 - 1))),
         Child => Load (Data (Data'First + 256 .. Data'First + (256 + 248 - 1))),
         task_id => Load (Data (Data'First + 504 .. Data'First + (504 + 24 - 1))),
         root_world => Load (Data (Data'First + 528 .. Data'First + (528 + 24 - 1))),
         child_world => Load (Data (Data'First + 552 .. Data'First + (552 + 24 - 1))),
         root_instance => Load (Data (Data'First + 576 .. Data'First + (576 + 24 - 1))),
         child_instance => Load (Data (Data'First + 600 .. Data'First + (600 + 24 - 1))),
         world_store => Load (Data (Data'First + 624 .. Data'First + (624 + 24 - 1))),
         full_world_ancestry => Load (Data (Data'First + 648 .. Data'First + (648 + 24 - 1))),
         original_workload => Load (Data (Data'First + 672 .. Data'First + (672 + 24 - 1))),
         sandbox => Load (Data (Data'First + 696 .. Data'First + (696 + 24 - 1))),
         adapter => Load (Data (Data'First + 720 .. Data'First + (720 + 24 - 1))),
         context => Load (Data (Data'First + 744 .. Data'First + (744 + 24 - 1))),
         mission => Load (Data (Data'First + 768 .. Data'First + (768 + 24 - 1))),
         stdin => Load (Data (Data'First + 792 .. Data'First + (792 + 24 - 1))),
         credential_source => Load (Data (Data'First + 816 .. Data'First + (816 + 24 - 1))),
         executable_source => Load (Data (Data'First + 840 .. Data'First + (840 + 24 - 1))),
         configuration => Load (Data (Data'First + 864 .. Data'First + (864 + 24 - 1))),
         owner_plan => Load (Data (Data'First + 888 .. Data'First + (888 + 24 - 1))),
         native_cost_input => Load (Data (Data'First + 912 .. Data'First + (912 + 24 - 1))),
         raw_request => Load (Data (Data'First + 936 .. Data'First + (936 + 24 - 1))),
         requester => Load (Data (Data'First + 960 .. Data'First + (960 + 24 - 1))),
         cause => Load (Data (Data'First + 984 .. Data'First + (984 + 24 - 1))),
         root_dispatch => Load (Data (Data'First + 1008 .. Data'First + (1008 + 24 - 1))),
         root_running_event => Load (Data (Data'First + 1032 .. Data'First + (1032 + 24 - 1))),
         task_journal => Load (Data (Data'First + 1056 .. Data'First + (1056 + 24 - 1))),
         task_intent => Load (Data (Data'First + 1080 .. Data'First + (1080 + 24 - 1))),
         task_reservation_event => Load (Data (Data'First + 1104 .. Data'First + (1104 + 24 - 1))),
         task_launch_event => Load (Data (Data'First + 1128 .. Data'First + (1128 + 24 - 1))),
         parent_namespace_source => Load (Data (Data'First + 1152 .. Data'First + (1152 + 24 - 1))),
         fd_lineage => Load (Data (Data'First + 1176 .. Data'First + (1176 + 24 - 1))),
         source_lease => Load (Data (Data'First + 1200 .. Data'First + (1200 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return Y.Raw_Namespace is
   begin
      return
        (identity => Load (Data (Data'First + 0 .. Data'First + (0 + 24 - 1))),
         parent => Load (Data (Data'First + 24 .. Data'First + (24 + 24 - 1))),
         raw_nsfs => Load (Data (Data'First + 48 .. Data'First + (48 + 24 - 1))),
         raw_get_parent => Load (Data (Data'First + 72 .. Data'First + (72 + 24 - 1))),
         source_lease => Load (Data (Data'First + 96 .. Data'First + (96 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Input is
   begin
      return
        (Schema => Interfaces.Unsigned_32 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 4 - 1)))),
         Mode => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 4 .. Data'First + (4 + 1 - 1)))),
         Bound => Load (Data (Data'First + 8 .. Data'First + (8 + 976 - 1))),
         Now => Load (Data (Data'First + 984 .. Data'First + (984 + 24 - 1))),
         Facts => Load (Data (Data'First + 1008 .. Data'First + (1008 + 5128 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Binding is
   begin
      return
        (Action => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         Id => Load (Data (Data'First + 1 .. Data'First + (1 + 891 - 1))),
         Peer => Load (Data (Data'First + 892 .. Data'First + (892 + 8 - 1))),
         Preparer => Load (Data (Data'First + 900 .. Data'First + (900 + 8 - 1))),
         Owner => Load (Data (Data'First + 908 .. Data'First + (908 + 8 - 1))),
         Target_Owner => Load (Data (Data'First + 916 .. Data'First + (916 + 8 - 1))),
         Policy_Epoch => Load (Data (Data'First + 928 .. Data'First + (928 + 24 - 1))),
         Resource_Epoch => Load (Data (Data'First + 952 .. Data'First + (952 + 24 - 1))));
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
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         Value => Interfaces.Unsigned_32 (Little_Endian (Data (Data'First + 4 .. Data'First + (4 + 4 - 1)))));
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Quantity is
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         Negative => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 1 .. Data'First + (1 + 1 - 1)))),
         First => Signed (Data (Data'First + 8 .. Data'First + (8 + 8 - 1))),
         Length => Signed (Data (Data'First + 16 .. Data'First + (16 + 8 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Evidence is
   begin
      return
        (Effect_Binding => Load (Data (Data'First + 0 .. Data'First + (0 + 976 - 1))),
         Actual_Receipt_Root => Load (Data (Data'First + 976 .. Data'First + (976 + 33 - 1))),
         Actual_Causal_Root => Load (Data (Data'First + 1009 .. Data'First + (1009 + 33 - 1))),
         No_Effect_Binding => Load (Data (Data'First + 1048 .. Data'First + (1048 + 976 - 1))),
         Owner_Resolution => Load (Data (Data'First + 2024 .. Data'First + (2024 + 976 - 1))),
         Quarantine_Head => Load (Data (Data'First + 3000 .. Data'First + (3000 + 33 - 1))),
         Witnessed_Receipt_Head => Load (Data (Data'First + 3033 .. Data'First + (3033 + 33 - 1))),
         Witnessed_Causal_Head => Load (Data (Data'First + 3066 .. Data'First + (3066 + 33 - 1))),
         Recovery => Load (Data (Data'First + 3104 .. Data'First + (3104 + 1968 - 1))),
         Original_Use => Load (Data (Data'First + 5072 .. Data'First + (5072 + 33 - 1))),
         Effect_Material_First => Signed (Data (Data'First + 5112 .. Data'First + (5112 + 8 - 1))),
         Effect_Material_Length => Signed (Data (Data'First + 5120 .. Data'First + (5120 + 8 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return RW.Raw_Request is
   begin
      return
        (Schema_Version => Interfaces.Unsigned_32 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 4 - 1)))),
         State => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 4 .. Data'First + (4 + 1 - 1)))),
         Fresh => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 5 .. Data'First + (5 + 1 - 1)))),
         Historical => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 6 .. Data'First + (6 + 1 - 1)))),
         Grant_Eligible => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 7 .. Data'First + (7 + 1 - 1)))),
         Issued_Binding => Load (Data (Data'First + 8 .. Data'First + (8 + 944 - 1))),
         Recovered_Binding => Load (Data (Data'First + 952 .. Data'First + (952 + 944 - 1))),
         Native => Load (Data (Data'First + 1896 .. Data'First + (1896 + 66 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return RW.Raw_Binding is
   begin
      return
        (Mode => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         Operation => Load (Data (Data'First + 1 .. Data'First + (1 + 33 - 1))),
         Transaction => Load (Data (Data'First + 34 .. Data'First + (34 + 33 - 1))),
         Capability => Load (Data (Data'First + 67 .. Data'First + (67 + 33 - 1))),
         Universe_Head => Load (Data (Data'First + 100 .. Data'First + (100 + 33 - 1))),
         Instance => Load (Data (Data'First + 133 .. Data'First + (133 + 33 - 1))),
         Subject => Load (Data (Data'First + 166 .. Data'First + (166 + 33 - 1))),
         Staged_Root => Load (Data (Data'First + 199 .. Data'First + (199 + 33 - 1))),
         Current_Requirement => Load (Data (Data'First + 232 .. Data'First + (232 + 33 - 1))),
         Resulting_Requirement => Load (Data (Data'First + 265 .. Data'First + (265 + 33 - 1))),
         Requester => Load (Data (Data'First + 298 .. Data'First + (298 + 33 - 1))),
         Grant_Use => Load (Data (Data'First + 331 .. Data'First + (331 + 33 - 1))),
         Policy_Identity => Load (Data (Data'First + 364 .. Data'First + (364 + 33 - 1))),
         Selected_Evaluation => Load (Data (Data'First + 397 .. Data'First + (397 + 33 - 1))),
         History_Head => Load (Data (Data'First + 430 .. Data'First + (430 + 33 - 1))),
         Reservation => Load (Data (Data'First + 463 .. Data'First + (463 + 33 - 1))),
         Host => Load (Data (Data'First + 496 .. Data'First + (496 + 33 - 1))),
         Before_Prime => Load (Data (Data'First + 529 .. Data'First + (529 + 33 - 1))),
         Before_Root => Load (Data (Data'First + 562 .. Data'First + (562 + 33 - 1))),
         Before_Mapping => Load (Data (Data'First + 595 .. Data'First + (595 + 33 - 1))),
         Staged_Mapping => Load (Data (Data'First + 628 .. Data'First + (628 + 33 - 1))),
         Input_Snapshot => Load (Data (Data'First + 661 .. Data'First + (661 + 33 - 1))),
         Kernel_Build => Load (Data (Data'First + 694 .. Data'First + (694 + 33 - 1))),
         Kernel_Library => Load (Data (Data'First + 727 .. Data'First + (727 + 33 - 1))),
         Kernel_Mapping => Load (Data (Data'First + 760 .. Data'First + (760 + 33 - 1))),
         Issuer_Head => Load (Data (Data'First + 793 .. Data'First + (793 + 33 - 1))),
         Receipt_Head => Load (Data (Data'First + 826 .. Data'First + (826 + 33 - 1))),
         Causal_Head => Load (Data (Data'First + 859 .. Data'First + (859 + 33 - 1))),
         Policy_Epoch => Load (Data (Data'First + 896 .. Data'First + (896 + 24 - 1))),
         Resource_Epoch => Load (Data (Data'First + 920 .. Data'First + (920 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return RW.Raw_Digest is
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         Value => Load (Data (Data'First + 1 .. Data'First + (1 + 32 - 1))));
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
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         Negative => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 1 .. Data'First + (1 + 1 - 1)))),
         First => Signed (Data (Data'First + 8 .. Data'First + (8 + 8 - 1))),
         Length => Signed (Data (Data'First + 16 .. Data'First + (16 + 8 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return RW.Raw_Native is
   begin
      return
        (Live_Mapping => Load (Data (Data'First + 0 .. Data'First + (0 + 33 - 1))),
         Live_Root => Load (Data (Data'First + 33 .. Data'First + (33 + 33 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Grant is
   begin
      return
        (Id => Load (Data (Data'First + 0 .. Data'First + (0 + 33 - 1))),
         Parent => Load (Data (Data'First + 33 .. Data'First + (33 + 33 - 1))),
         Issuer => Load (Data (Data'First + 66 .. Data'First + (66 + 33 - 1))),
         Instance => Load (Data (Data'First + 99 .. Data'First + (99 + 33 - 1))),
         Root_Set => Load (Data (Data'First + 132 .. Data'First + (132 + 33 - 1))),
         Policy => Load (Data (Data'First + 165 .. Data'First + (165 + 33 - 1))),
         Subject => Load (Data (Data'First + 200 .. Data'First + (200 + 8 - 1))),
         Owner => Load (Data (Data'First + 208 .. Data'First + (208 + 8 - 1))),
         Allowed => Load (Data (Data'First + 216 .. Data'First + (216 + 41 - 1))),
         State => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 257 .. Data'First + (257 + 1 - 1)))),
         Epoch => Load (Data (Data'First + 264 .. Data'First + (264 + 24 - 1))),
         Ceiling => Load (Data (Data'First + 288 .. Data'First + (288 + 24 - 1))),
         Issued_At => Load (Data (Data'First + 312 .. Data'First + (312 + 24 - 1))),
         Expires_At => Load (Data (Data'First + 336 .. Data'First + (336 + 24 - 1))));
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
   begin
      return
        (Bound => Load (Data (Data'First + 0 .. Data'First + (0 + 976 - 1))),
         State => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 976 .. Data'First + (976 + 1 - 1)))));
   end Load;
   function Load (Data : Q.Byte_Array) return C.Raw_Row is
   begin
      return
        (Previous => Load (Data (Data'First + 0 .. Data'First + (0 + 33 - 1))),
         Actual_Payload_Root => Load (Data (Data'First + 33 .. Data'First + (33 + 33 - 1))),
         Stored_Payload_Root => Load (Data (Data'First + 66 .. Data'First + (66 + 33 - 1))),
         Stored_Head => Load (Data (Data'First + 99 .. Data'First + (99 + 33 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return D.Raw_Capability is
   begin
      return
        (Index => Load (Data (Data'First + 0 .. Data'First + (0 + 24 - 1))),
         Bounding => Load (Data (Data'First + 24 .. Data'First + (24 + 24 - 1))),
         Ambient => Load (Data (Data'First + 48 .. Data'First + (48 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Scope_Frame is
   begin
      return
        (Scope => Load (Data (Data'First + 0 .. Data'First + (0 + 224 - 1))),
         First_Epoch => Load (Data (Data'First + 224 .. Data'First + (224 + 32 - 1))),
         Universe_Head => Load (Data (Data'First + 256 .. Data'First + (256 + 24 - 1))),
         Frame_Head => Load (Data (Data'First + 280 .. Data'First + (280 + 24 - 1))),
         Prior_Frame => Load (Data (Data'First + 304 .. Data'First + (304 + 24 - 1))),
         Store_Genesis => Load (Data (Data'First + 328 .. Data'First + (328 + 24 - 1))),
         Store_Id => Load (Data (Data'First + 352 .. Data'First + (352 + 24 - 1))),
         Root_Head => Load (Data (Data'First + 376 .. Data'First + (376 + 24 - 1))),
         Prime => Load (Data (Data'First + 400 .. Data'First + (400 + 24 - 1))),
         Root_Count => Load (Data (Data'First + 424 .. Data'First + (424 + 24 - 1))),
         Cause => Load (Data (Data'First + 448 .. Data'First + (448 + 24 - 1))),
         Requester => Load (Data (Data'First + 472 .. Data'First + (472 + 24 - 1))),
         Receipt => Load (Data (Data'First + 496 .. Data'First + (496 + 24 - 1))),
         Catalogue_Head => Load (Data (Data'First + 520 .. Data'First + (520 + 24 - 1))),
         Observation_Head => Load (Data (Data'First + 544 .. Data'First + (544 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Projection is
   begin
      return
        (Key => Load (Data (Data'First + 0 .. Data'First + (0 + 72 - 1))),
         Bound => Load (Data (Data'First + 72 .. Data'First + (72 + 248 - 1))),
         Origin => Load (Data (Data'First + 320 .. Data'First + (320 + 224 - 1))),
         Catalogue_Head => Load (Data (Data'First + 544 .. Data'First + (544 + 24 - 1))),
         Numerator => Load (Data (Data'First + 568 .. Data'First + (568 + 24 - 1))),
         Denominator => Load (Data (Data'First + 592 .. Data'First + (592 + 24 - 1))),
         Amount => Load (Data (Data'First + 616 .. Data'First + (616 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Physical_Key is
   begin
      return
        (Machine => Load (Data (Data'First + 0 .. Data'First + (0 + 24 - 1))),
         Resource => Load (Data (Data'First + 24 .. Data'First + (24 + 24 - 1))),
         Unit => Load (Data (Data'First + 48 .. Data'First + (48 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return N.Raw_Bucket is
   begin
      return
        (Key => Load (Data (Data'First + 0 .. Data'First + (0 + 72 - 1))),
         Capacity => Load (Data (Data'First + 72 .. Data'First + (72 + 24 - 1))),
         Held_Total => Load (Data (Data'First + 96 .. Data'First + (96 + 24 - 1))),
         Charged_Total => Load (Data (Data'First + 120 .. Data'First + (120 + 24 - 1))),
         Capacity_Source => Load (Data (Data'First + 144 .. Data'First + (144 + 24 - 1))),
         Catalogue_Head => Load (Data (Data'First + 168 .. Data'First + (168 + 24 - 1))),
         Observation_Head => Load (Data (Data'First + 192 .. Data'First + (192 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Native is
   begin
      return
        (Scope => Load (Data (Data'First + 0 .. Data'First + (0 + 224 - 1))),
         Resource_Epoch => Load (Data (Data'First + 224 .. Data'First + (224 + 32 - 1))),
         Bound => Load (Data (Data'First + 256 .. Data'First + (256 + 248 - 1))),
         Actual_Unit => Load (Data (Data'First + 504 .. Data'First + (504 + 24 - 1))),
         Cgroup => Load (Data (Data'First + 528 .. Data'First + (528 + 24 - 1))),
         Invocation => Load (Data (Data'First + 552 .. Data'First + (552 + 24 - 1))),
         Observation_Head => Load (Data (Data'First + 576 .. Data'First + (576 + 24 - 1))),
         Observed => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 600 .. Data'First + (600 + 1 - 1)))));
   end Load;
   function Load (Data : Q.Byte_Array) return O.Raw_Facts is
   begin
      return
        (Current => Load (Data (Data'First + 0 .. Data'First + (0 + 224 - 1))),
         Current_Epoch => Load (Data (Data'First + 224 .. Data'First + (224 + 32 - 1))),
         Retained => Load (Data (Data'First + 256 .. Data'First + (256 + 248 - 1))),
         Current_Universe_Head => Load (Data (Data'First + 504 .. Data'First + (504 + 24 - 1))),
         Current_Ledger_Head => Load (Data (Data'First + 528 .. Data'First + (528 + 24 - 1))),
         Intent => Load (Data (Data'First + 552 .. Data'First + (552 + 24 - 1))),
         Dispatch => Load (Data (Data'First + 576 .. Data'First + (576 + 24 - 1))),
         Observation_Head => Load (Data (Data'First + 600 .. Data'First + (600 + 24 - 1))),
         Actual_Unit => Load (Data (Data'First + 624 .. Data'First + (624 + 24 - 1))),
         Cgroup => Load (Data (Data'First + 648 .. Data'First + (648 + 24 - 1))),
         Invocation => Load (Data (Data'First + 672 .. Data'First + (672 + 24 - 1))),
         Namespace => Load (Data (Data'First + 696 .. Data'First + (696 + 24 - 1))),
         Held_Namespace => Load (Data (Data'First + 720 .. Data'First + (720 + 24 - 1))),
         Peer => Load (Data (Data'First + 744 .. Data'First + (744 + 24 - 1))),
         Held_Peer => Load (Data (Data'First + 768 .. Data'First + (768 + 24 - 1))),
         Helper_Image => Load (Data (Data'First + 792 .. Data'First + (792 + 24 - 1))),
         Expected_Helper_Image => Load (Data (Data'First + 816 .. Data'First + (816 + 24 - 1))),
         Challenge => Load (Data (Data'First + 840 .. Data'First + (840 + 24 - 1))),
         Held_Challenge => Load (Data (Data'First + 864 .. Data'First + (864 + 24 - 1))),
         Protocol => Load (Data (Data'First + 888 .. Data'First + (888 + 24 - 1))),
         Closed_Event => Load (Data (Data'First + 912 .. Data'First + (912 + 24 - 1))),
         Namespace_Wait => Load (Data (Data'First + 936 .. Data'First + (936 + 24 - 1))),
         Helper_Wait => Load (Data (Data'First + 960 .. Data'First + (960 + 24 - 1))),
         Cgroup_Events => Load (Data (Data'First + 984 .. Data'First + (984 + 24 - 1))),
         Cgroup_Type => Load (Data (Data'First + 1008 .. Data'First + (1008 + 24 - 1))),
         Manager_Delegate => Load (Data (Data'First + 1032 .. Data'First + (1032 + 24 - 1))),
         Cgroup_Owner => Load (Data (Data'First + 1056 .. Data'First + (1056 + 32 - 1))),
         Cgroup_Group_Write => Load (Data (Data'First + 1088 .. Data'First + (1088 + 32 - 1))),
         Cgroup_Other_Write => Load (Data (Data'First + 1120 .. Data'First + (1120 + 32 - 1))),
         Actual_Store_Genesis => Load (Data (Data'First + 1152 .. Data'First + (1152 + 24 - 1))),
         Actual_Store_Id => Load (Data (Data'First + 1176 .. Data'First + (1176 + 24 - 1))),
         Owner_Store_Genesis => Load (Data (Data'First + 1200 .. Data'First + (1200 + 24 - 1))),
         Owner_Store_Id => Load (Data (Data'First + 1224 .. Data'First + (1224 + 24 - 1))),
         Genesis_Universe => Load (Data (Data'First + 1248 .. Data'First + (1248 + 24 - 1))),
         Genesis_Instance => Load (Data (Data'First + 1272 .. Data'First + (1272 + 24 - 1))),
         Genesis_Context_Head => Load (Data (Data'First + 1296 .. Data'First + (1296 + 24 - 1))),
         Genesis_Prime => Load (Data (Data'First + 1320 .. Data'First + (1320 + 24 - 1))),
         Genesis_Root_Count => Load (Data (Data'First + 1344 .. Data'First + (1344 + 32 - 1))),
         Phase => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 1376 .. Data'First + (1376 + 1 - 1)))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_Result is
   begin
      return
        (Status => Interfaces.Unsigned_32 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 4 - 1)))));
   end Load;
   function Load (Data : Q.Byte_Array) return T.Raw_Result is
   begin
      return
        (Disposition => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))));
   end Load;
   function Load (Data : Q.Byte_Array) return HC.Raw_Input is
   begin
      return
        (Historical => Load (Data (Data'First + 0 .. Data'First + (0 + 11832 - 1))),
         Current => Load (Data (Data'First + 11832 .. Data'First + (11832 + 6136 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return CX.Raw_Input is
   begin
      return
        (Operation_Input => Load (Data (Data'First + 0 .. Data'First + (0 + 7680 - 1))),
         Material => Load (Data (Data'First + 7680 .. Data'First + (7680 + 4144 - 1))),
         Before => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 11824 .. Data'First + (11824 + 1 - 1)))),
         Mode => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 11825 .. Data'First + (11825 + 1 - 1)))));
   end Load;
   function Load (Data : Q.Byte_Array) return CO.Raw_Input is
   begin
      return
        (Authority => Load (Data (Data'First + 0 .. Data'First + (0 + 6136 - 1))),
         State => Load (Data (Data'First + 6136 .. Data'First + (6136 + 376 - 1))),
         Bound => Load (Data (Data'First + 6512 .. Data'First + (6512 + 248 - 1))),
         Requester => Load (Data (Data'First + 6760 .. Data'First + (6760 + 24 - 1))),
         Peer => Load (Data (Data'First + 6784 .. Data'First + (6784 + 8 - 1))),
         Collapse => Load (Data (Data'First + 6792 .. Data'First + (6792 + 883 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return W.Raw_State is
   begin
      return
        (Scope => Load (Data (Data'First + 0 .. Data'First + (0 + 224 - 1))),
         Resource_Epoch => Load (Data (Data'First + 224 .. Data'First + (224 + 32 - 1))),
         Universe_Head => Load (Data (Data'First + 256 .. Data'First + (256 + 24 - 1))),
         Ledger_Head => Load (Data (Data'First + 280 .. Data'First + (280 + 24 - 1))),
         Capacity => Load (Data (Data'First + 304 .. Data'First + (304 + 24 - 1))),
         Held_Total => Load (Data (Data'First + 328 .. Data'First + (328 + 24 - 1))),
         Charged_Total => Load (Data (Data'First + 352 .. Data'First + (352 + 24 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return CW.Raw_Request is
   begin
      return
        (Candidate_State => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         Phase => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 1 .. Data'First + (1 + 1 - 1)))),
         Evaluation_Mode => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 2 .. Data'First + (2 + 1 - 1)))),
         Conflicts => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 3 .. Data'First + (3 + 1 - 1)))),
         Foreign_Writes => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 4 .. Data'First + (4 + 1 - 1)))),
         Roster_Complete => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 5 .. Data'First + (5 + 1 - 1)))),
         Staged_Roster_Complete => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 6 .. Data'First + (6 + 1 - 1)))),
         Expected_Parent => Load (Data (Data'First + 7 .. Data'First + (7 + 33 - 1))),
         Candidate_Parent => Load (Data (Data'First + 40 .. Data'First + (40 + 33 - 1))),
         Expected_Subject => Load (Data (Data'First + 73 .. Data'First + (73 + 33 - 1))),
         Evidence_Subject => Load (Data (Data'First + 106 .. Data'First + (106 + 33 - 1))),
         Expected_Base => Load (Data (Data'First + 139 .. Data'First + (139 + 33 - 1))),
         Candidate_Base => Load (Data (Data'First + 172 .. Data'First + (172 + 33 - 1))),
         Expected_Delta => Load (Data (Data'First + 205 .. Data'First + (205 + 33 - 1))),
         Candidate_Delta => Load (Data (Data'First + 238 .. Data'First + (238 + 33 - 1))),
         Expected_Root_Set => Load (Data (Data'First + 271 .. Data'First + (271 + 33 - 1))),
         Candidate_Root_Set => Load (Data (Data'First + 304 .. Data'First + (304 + 33 - 1))),
         Expected_Staged_Root => Load (Data (Data'First + 337 .. Data'First + (337 + 33 - 1))),
         Actual_Staged_Root => Load (Data (Data'First + 370 .. Data'First + (370 + 33 - 1))),
         Staged_Content_Root => Load (Data (Data'First + 403 .. Data'First + (403 + 33 - 1))),
         Tested_Root => Load (Data (Data'First + 436 .. Data'First + (436 + 33 - 1))),
         Current_Requirement => Load (Data (Data'First + 469 .. Data'First + (469 + 33 - 1))),
         Resulting_Requirement => Load (Data (Data'First + 502 .. Data'First + (502 + 33 - 1))),
         Evaluated_Requirement => Load (Data (Data'First + 535 .. Data'First + (535 + 33 - 1))),
         Declared_Verifiers => Load (Data (Data'First + 568 .. Data'First + (568 + 33 - 1))),
         Executed_Verifiers => Load (Data (Data'First + 601 .. Data'First + (601 + 33 - 1))),
         Staged_Evaluated_Requirement => Load (Data (Data'First + 634 .. Data'First + (634 + 33 - 1))),
         Staged_Executed_Verifiers => Load (Data (Data'First + 667 .. Data'First + (667 + 33 - 1))),
         Staged_Examined_Root => Load (Data (Data'First + 700 .. Data'First + (700 + 33 - 1))),
         Expected_Checkpoint => Load (Data (Data'First + 733 .. Data'First + (733 + 33 - 1))),
         Witnessed_Checkpoint => Load (Data (Data'First + 766 .. Data'First + (766 + 33 - 1))),
         Registered_Watch_Set => Load (Data (Data'First + 799 .. Data'First + (799 + 33 - 1))),
         Watched_Set => Load (Data (Data'First + 832 .. Data'First + (832 + 33 - 1))),
         Generation_Before => Load (Data (Data'First + 865 .. Data'First + (865 + 9 - 1))),
         Generation_After => Load (Data (Data'First + 874 .. Data'First + (874 + 9 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return CW.Raw_Optional_Hash is
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         Value => Load (Data (Data'First + 1 .. Data'First + (1 + 32 - 1))));
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
   begin
      return
        (Present => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))),
         Value_LE => Load (Data (Data'First + 1 .. Data'First + (1 + 8 - 1))));
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
   begin
      return
        (Worker_Issued => Load (Data (Data'First + 0 .. Data'First + (0 + 944 - 1))),
         Worker_Recovered => Load (Data (Data'First + 944 .. Data'First + (944 + 944 - 1))),
         Canonical_Issued => Load (Data (Data'First + 1888 .. Data'First + (1888 + 944 - 1))),
         Canonical_Recovered => Load (Data (Data'First + 2832 .. Data'First + (2832 + 944 - 1))),
         Worker_Native => Load (Data (Data'First + 3776 .. Data'First + (3776 + 66 - 1))),
         Canonical_Native => Load (Data (Data'First + 3842 .. Data'First + (3842 + 66 - 1))),
         Worker_Receipt_Genesis => Load (Data (Data'First + 3908 .. Data'First + (3908 + 33 - 1))),
         Owner_Receipt_Genesis => Load (Data (Data'First + 3941 .. Data'First + (3941 + 33 - 1))),
         Worker_Receipt_Head => Load (Data (Data'First + 3974 .. Data'First + (3974 + 33 - 1))),
         Worker_Causal_Genesis => Load (Data (Data'First + 4007 .. Data'First + (4007 + 33 - 1))),
         Owner_Causal_Genesis => Load (Data (Data'First + 4040 .. Data'First + (4040 + 33 - 1))),
         Worker_Causal_Head => Load (Data (Data'First + 4073 .. Data'First + (4073 + 33 - 1))),
         Quarantine_Head => Load (Data (Data'First + 4106 .. Data'First + (4106 + 33 - 1))));
   end Load;
   function Load (Data : Q.Byte_Array) return HC.Raw_Result is
   begin
      return
        (Disposition => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))));
   end Load;
   function Load (Data : Q.Byte_Array) return CX.Raw_Result is
   begin
      return
        (Disposition => Interfaces.Unsigned_8 (Little_Endian (Data (Data'First + 0 .. Data'First + (0 + 1 - 1)))));
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
