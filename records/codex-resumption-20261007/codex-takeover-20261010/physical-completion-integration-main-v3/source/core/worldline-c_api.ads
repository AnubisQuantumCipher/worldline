with Interfaces;
with Interfaces.C;
with System;
with Worldline.Collapse_Wire;

package Worldline.C_API with SPARK_Mode => Off is
   --  Diagnostics are peripheral observations under the native call guard.
   function Diagnostic_Control (Enable : Interfaces.Unsigned_32)
     return Interfaces.Unsigned_32
     with Export, Convention => C,
       External_Name => "wl_native_diagnostic_control_v1";


   --  The collapse request (ABI generation 6) is Worldline.Collapse_Wire's
   --  Raw_Request; its decoding is proved there.
   subtype C_Collapse_Request is Collapse_Wire.Raw_Request;

   --  The ABI generation of this library: request layouts, record layouts and
   --  the meaning of every exported code. The runtime refuses to load a
   --  library that reports a different generation.
   ABI_Version : constant Interfaces.Unsigned_32 := 6;

   type C_Collapse_Request_Access is access constant C_Collapse_Request
     with Convention => C;

   --  Phase 1 evaluation lifecycle ABI. All fields are validated before enum
   --  conversion; malformed C input is never interpreted as a completed run.
   type C_Evaluation_Observations is record
      Source              : Interfaces.Unsigned_8;
      Status              : Interfaces.Unsigned_8;
      Channel             : Interfaces.Unsigned_8;
      Stage               : Interfaces.Unsigned_8;
      Exit_Present        : Interfaces.Unsigned_8;
      Exit_Integer        : Interfaces.Unsigned_8;
      Supervisor          : Interfaces.Unsigned_8;
      Supervisor_Stopped  : Interfaces.Unsigned_8;
      Bundle_Present      : Interfaces.Unsigned_8;
      Bundle_Is_Mapping   : Interfaces.Unsigned_8;
      Bundle_Stable       : Interfaces.Unsigned_8;
      Bundle_Changed      : Interfaces.Unsigned_8;
      Unsatisfied_Imports : Interfaces.Unsigned_8;
   end record with Convention => C;

   type C_Evaluation_Observations_Access is
     access constant C_Evaluation_Observations with Convention => C;

   type C_Evaluation_Classification is record
      Execution : Interfaces.Unsigned_8;
      Outcome   : Interfaces.Unsigned_8;
      Bundle    : Interfaces.Unsigned_8;
   end record with Convention => C;

   type C_Evaluation_Classification_Access is
     access all C_Evaluation_Classification with Convention => C;

   type C_Evaluation_Classification_Read_Access is
     access constant C_Evaluation_Classification with Convention => C;

   type C_Evidence_Presence is record
      Record_Identified   : Interfaces.Unsigned_8;
      Verdict_Recorded    : Interfaces.Unsigned_8;
      Binding_Established : Interfaces.Unsigned_8;
      Declaration_Matches : Interfaces.Unsigned_8;
      Bundle_Identified   : Interfaces.Unsigned_8;
   end record with Convention => C;

   type C_Evidence_Presence_Access is
     access constant C_Evidence_Presence with Convention => C;

   type C_State_Access is access all Interfaces.Unsigned_8
     with Convention => C;

   function Hash_File
     (Path       : System.Address;
      Path_Len   : Interfaces.C.size_t;
      Out_Digest : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_hash_file";

   function Hash_Bytes
     (Data       : System.Address;
      Data_Len   : Interfaces.C.size_t;
      Out_Digest : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_hash_bytes";

   function World_ID
     (Parent_ID        : System.Address;
      Filesystem_Root  : System.Address;
      Config_Root      : System.Address;
      Repository_Root  : System.Address;
      Environment_Root : System.Address;
      Evidence_Root    : System.Address;
      Out_Digest       : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_world_id";

   function Causal_Link
     (Previous   : System.Address;
      Event_Root : System.Address;
      Out_Digest : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_causal_link";

   function Receipt_Link
     (Previous     : System.Address;
      Receipt_Root : System.Address;
      Out_Digest   : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_receipt_link";

   function Transition_Allowed
     (From_State : Interfaces.Unsigned_8;
      To_State   : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
     with Export, Convention => C, External_Name => "wl_transition_allowed";

   --  Transaction lifecycle codes follow the declaration order of
   --  Transitions.Transaction_State: Prepared 0, Authorized 1, Denied 2,
   --  Committed 3, Aborted 4. Out-of-range codes are refused (0).
   function Transaction_Transition_Allowed
     (From_State : Interfaces.Unsigned_8;
      To_State   : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
     with Export, Convention => C,
          External_Name => "wl_transaction_transition_allowed";

   function Collapse_Decide
     (Request : C_Collapse_Request_Access) return Interfaces.Unsigned_8
     with Export, Convention => C, External_Name => "wl_collapse_decide";

   --  0 means a valid classification was written; 255 means invalid input.
   function Evaluation_Classify
     (Facts : C_Evaluation_Observations_Access;
      Result : C_Evaluation_Classification_Access)
      return Interfaces.Unsigned_8
     with Export, Convention => C, External_Name => "wl_evaluation_classify";

   --  0 denied, 1 admitted, 255 invalid C encoding. A classification that
   --  Classify could not have produced (an outcome without completion, or
   --  completion without an outcome) is an invalid encoding.
   function Evaluation_Admissible
     (Value    : C_Evaluation_Classification_Read_Access;
      Report   : Interfaces.Unsigned_8;
      Presence : C_Evidence_Presence_Access)
      return Interfaces.Unsigned_8
     with Export, Convention => C,
          External_Name => "wl_evaluation_admissible";

   --  Evaluation lifecycle relation: 0 refused, 1 allowed, 255 invalid code.
   function Evaluation_Transition_Allowed
     (From_State : Interfaces.Unsigned_8;
      To_State   : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
     with Export, Convention => C,
          External_Name => "wl_evaluation_transition_allowed";

   --  Advances State in place when the kernel allows it. 0 on success (the
   --  state may be unchanged when the step is refused), 255 invalid input.
   function Evaluation_Advance
     (State     : C_State_Access;
      Requested : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
     with Export, Convention => C,
          External_Name => "wl_evaluation_advance";

   --  One admission byte (0 or 1) per required check. 0 incomplete,
   --  1 complete, 255 invalid (a byte above 1, a count above 4096, or a null
   --  array with a nonzero count).
   function Evaluation_Roster_Complete
     (Admitted       : System.Address;
      Count          : Interfaces.C.size_t;
      Empty_Declared : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
     with Export, Convention => C,
          External_Name => "wl_evaluation_roster_complete";

   function ABI_Generation return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_abi_version";

   --  Byte size of an exported record as this library lays it out:
   --  0 collapse request, 1 evaluation observations, 2 evaluation
   --  classification, 3 evidence presence, 4 optional hash, 5 optional
   --  counter. 0 for an unknown selector.
   function Layout_Size
     (Selector : Interfaces.Unsigned_8) return Interfaces.C.size_t
     with Export, Convention => C, External_Name => "wl_layout_size";

   --  Byte offset of the field NAMED Name (lower case, as in the C header) of
   --  the record Selector names, as this library lays it out; size_t'Last for
   --  an unknown selector or name. Keyed by name, not position: two
   --  equal-sized fields swapped keep every size and every positional offset.
   function Layout_Offset
     (Selector : Interfaces.Unsigned_8;
      Name     : System.Address;
      Name_Len : Interfaces.C.size_t) return Interfaces.C.size_t
     with Export, Convention => C, External_Name => "wl_layout_offset";

   package Authority_Glue is
   subtype Byte is Interfaces.Unsigned_8;
   function Version return Byte with Export, Convention => C,
     External_Name => "wl_evaluation_wire_version";
   function Layout (Kind, Field : Byte) return Interfaces.C.size_t
     with Export, Convention => C, External_Name => "wl_evaluation_wire_layout";
   function Classify (Raw, Output : System.Address) return Byte
     with Export, Convention => C, External_Name => "wl_evaluation_wire_classify";
   function Admit (Raw : System.Address; Confinement : Byte) return Byte
     with Export, Convention => C, External_Name => "wl_evaluation_wire_admit";
   function Report (Raw : System.Address) return Byte
     with Export, Convention => C, External_Name => "wl_evaluation_wire_report";
   function Dependencies (Request : System.Address) return Byte
     with Export, Convention => C,
       External_Name => "wl_collapse_raw_dependencies_v1";
   function Decide_Raw (Request, Primary, Primary_Raw, Primary_Confinement,
       Staged, Staged_Raw, Staged_Confinement, Agent : System.Address;
       Agent_Confinement : Byte) return Byte
     with Export, Convention => C,
       External_Name => "wl_collapse_decide_raw_evaluation_v1";
      function Decide_Raw_Context
        (Request, Primary, Primary_Raw, Primary_Confinement, Primary_Context,
         Staged, Staged_Raw, Staged_Confinement, Staged_Context, Agent : System.Address;
         Agent_Confinement : Byte) return Byte
        with Export, Convention => C,
          External_Name => "wl_collapse_decide_raw_evaluation_v2";
      function Decide_Raw_Metadata
        (Request, Primary, Primary_Raw, Primary_Confinement, Primary_Context,
         Staged, Staged_Raw, Staged_Confinement, Staged_Context, Agent : System.Address;
         Agent_Confinement : Byte) return Byte
        with Export, Convention => C,
          External_Name => "wl_collapse_decide_raw_evaluation_v3";
   end Authority_Glue;

   --  Additive owner-operation ABI; original library ABI/version remains exact.
   --  Owned readable input extents are required and copied before any output.
   function Owner_ABI_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_owner_transition_version_v1";
   function Owner_Layout (Kind, Field : Interfaces.Unsigned_8)
     return Interfaces.C.size_t
     with Export, Convention => C, External_Name => "wl_owner_transition_layout_v1";
   function Owner_Authorize
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      History : System.Address; Row_Count : Interfaces.C.size_t;
      Final_Present : Interfaces.Unsigned_8; Final_Row, Request, Output : System.Address)
     return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_owner_transition_authorize_v1";
   function Owner_Audit_ABI return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_owner_audit_version_v1";
   function Owner_Audit_Layout (Kind, Field : Interfaces.Unsigned_8) return Interfaces.C.size_t
     with Export, Convention => C, External_Name => "wl_owner_audit_layout_v1";
   function Owner_Audit_Decide
     (Mode : Interfaces.Unsigned_8; Data : System.Address; Data_Length : Interfaces.C.size_t;
      Before : System.Address; Before_Count : Interfaces.C.size_t;
      After : System.Address; After_Count : Interfaces.C.size_t;
      Before_Present : Interfaces.Unsigned_8; Before_Final : System.Address;
      After_Present : Interfaces.Unsigned_8; After_Final : System.Address;
      Audit, Original, Scope, Resulting : System.Address;
      Adopt_Present : Interfaces.Unsigned_8; Adopt, Output : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_owner_audit_decide_v1";
   -- Retained-v1 chain only, not custody-v2 Ready or startup permission.
   function Retained_Chain_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_retained_chain_version_v1";
   function Retained_Chain_Layout (Kind, Field : Interfaces.Unsigned_8)
      return Interfaces.C.size_t
     with Export, Convention => C, External_Name => "wl_retained_chain_layout_v1";
   function Retained_Chain_Verify
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Spans : System.Address; Span_Count, Genesis_Count, Event_Count, Head_Count : Interfaces.C.size_t;
      Output : System.Address; Output_Size : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_retained_chain_verify_v1";
   -- PREPARED value step only; does not authenticate or release startup.
   function Prepared_Step_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_custody_prepared_version_v1";
   function Prepared_Step_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.size_t
     with Export, Convention => C, External_Name => "wl_custody_prepared_layout_v1";
   function Prepared_Step_Decide
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Event, Root, Reserve, Intent : System.Address;
      Event_Size, Root_Size, Reserve_Size, Intent_Size : Interfaces.C.size_t;
      Reserve_Grants : System.Address; Reserve_Grants_Count, Reserve_Grants_Bytes : Interfaces.C.size_t;
      Intent_Grants : System.Address; Intent_Grants_Count, Intent_Grants_Bytes : Interfaces.C.size_t;
      Reserve_Uses : System.Address; Reserve_Uses_Count, Reserve_Uses_Bytes : Interfaces.C.size_t;
      Intent_Uses : System.Address; Intent_Uses_Count, Intent_Uses_Bytes : Interfaces.C.size_t;
      Reserve_Receipts : System.Address; Reserve_Receipts_Count, Reserve_Receipts_Bytes : Interfaces.C.size_t;
      Reserve_Events : System.Address; Reserve_Events_Count, Reserve_Events_Bytes : Interfaces.C.size_t;
      Intent_Receipts : System.Address; Intent_Receipts_Count, Intent_Receipts_Bytes : Interfaces.C.size_t;
      Intent_Events : System.Address; Intent_Events_Count, Intent_Events_Bytes : Interfaces.C.size_t;
      Output : System.Address; Output_Size : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_custody_prepared_decide_v1";
   function Operation_Authority_Version return Interfaces.Unsigned_32
     with Export,Convention=>C,External_Name=>"wl_operation_authority_version_v1";
   function Operation_Authority_Layout(Kind,Field:Interfaces.Unsigned_32) return Interfaces.C.long
     with Export,Convention=>C,External_Name=>"wl_operation_authority_layout_v1";
   function Operation_Authority_Decide(Input:System.Address; Input_Length:Interfaces.C.size_t;
      Arena:System.Address; Arena_Length:Interfaces.C.size_t;
      Grants:System.Address; Grant_Count,Grant_Length:Interfaces.C.size_t;
      Uses:System.Address; Use_Count,Use_Length:Interfaces.C.size_t;
      Receipts:System.Address; Receipt_Count,Receipt_Length:Interfaces.C.size_t;
      Events:System.Address; Event_Count,Event_Length:Interfaces.C.size_t;
      Output:System.Address; Output_Length:Interfaces.C.size_t) return Interfaces.C.int
     with Export,Convention=>C,External_Name=>"wl_operation_authority_decide_v1";
   function Canonical_Operation_Version return Interfaces.Unsigned_32 with Export,Convention=>C,External_Name=>"wl_canonical_operation_version_v1";
   function Canonical_Operation_Layout(Kind,Field:Interfaces.Unsigned_32) return Interfaces.C.long with Export,Convention=>C,External_Name=>"wl_canonical_operation_layout_v1";
   function Canonical_Operation_Decide(Input:System.Address; Input_Length:Interfaces.C.size_t;
      Arena:System.Address; Arena_Length:Interfaces.C.size_t;
      Grants:System.Address; Grant_Count,Grant_Length:Interfaces.C.size_t;
      Uses:System.Address; Use_Count,Use_Length:Interfaces.C.size_t;
      Rows:System.Address; Row_Count,Row_Length:Interfaces.C.size_t;
      Observed:System.Address; Observed_Count,Observed_Length:Interfaces.C.size_t;
      Output:System.Address; Output_Length:Interfaces.C.size_t) return Interfaces.C.int with Export,Convention=>C,External_Name=>"wl_canonical_operation_decide_v1";
   function Completion_ABI_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_completion_abi_version_v1";
   function Completion_Layout_Size (Kind : Interfaces.Unsigned_32) return Interfaces.Integer_64
     with Export, Convention => C, External_Name => "wl_completion_layout_size_v1";
   function Completion_Layout_Alignment (Kind : Interfaces.Unsigned_32) return Interfaces.Integer_64
     with Export, Convention => C, External_Name => "wl_completion_layout_alignment_v1";
   function Completion_Layout_Offset (Kind, Field : Interfaces.Unsigned_32) return Interfaces.Integer_64
     with Export, Convention => C, External_Name => "wl_completion_layout_offset_v1";
   function Completion_Context_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.Integer_64
     with Export, Convention => C, External_Name => "wl_completion_context_layout_v1";
   function Completion_Metadata_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.Integer_64
     with Export, Convention => C, External_Name => "wl_completion_metadata_layout_v1";
   function Completion_Decide (Input, Output : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_completion_decide_v1";
   function Completion_Raw_Decide (Input, Raw_Rows, Confinements, Output : System.Address)
      return Interfaces.C.int with Export, Convention => C,
        External_Name => "wl_completion_raw_decide_v1";
   function Completion_Metadata_Matches (Input, Context : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_completion_metadata_matches_v1";
   function Finalization_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_finalization_version_v1";
   function Finalization_Layout (Kind, Field : Interfaces.Unsigned_32)
      return Interfaces.Integer_64
     with Export, Convention => C, External_Name => "wl_finalization_layout_v1";
   function Finalization_Decide (Input, Output : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_finalization_decide_v1";
   function Finalization_Decide_Mixed
     (Collapse : System.Address; Primary_Kind : Interfaces.Unsigned_32;
      Primary, Primary_Raw, Primary_Confinement, Primary_Context : System.Address;
      Staged_Kind : Interfaces.Unsigned_32;
      Staged, Staged_Raw, Staged_Confinement, Staged_Context, Agent : System.Address;
      Agent_Confinement : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
     with Export, Convention => C, External_Name => "wl_collapse_decide_finalization_v1";

   function Owned_recovery_authorization
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_recovery_authorization_decide_v2";

   function Owned_recovery_authorization_v3
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Arena : System.Address; Arena_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_recovery_authorization_decide_v3";

   function Owned_recovery_protocol
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_recovery_protocol_decide_v1";

   function Owned_Chain_Replay
     (Anchors : System.Address; Anchors_Length : Interfaces.C.size_t;
      Rows : System.Address; Rows_Count, Rows_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_chain_authority_replay_v1";

   function Owned_Recovery_Select
     (Expected : System.Address; Expected_Length : Interfaces.C.size_t;
      Live_Present : Interfaces.Unsigned_8;
      Live : System.Address; Live_Length : Interfaces.C.size_t;
      Prepared_Present : Interfaces.Unsigned_8;
      Prepared : System.Address; Prepared_Length : Interfaces.C.size_t)
      return Interfaces.Unsigned_8
     with Export, Convention => C, External_Name => "wl_recovery_select";

   function Owned_History_Select
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Rows : System.Address; Row_Count : Interfaces.C.size_t;
      Final_Present : Interfaces.Unsigned_8; Final_Row, Query, Output : System.Address) return Interfaces.Unsigned_8
     with Export, Convention => C, External_Name => "wl_evaluation_history_select";
   package Resources_Transport is
      subtype U8 is Interfaces.Unsigned_8;
      subtype Size is Interfaces.C.size_t;
   function ABI_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_resources_abi_version";
   function Can_Reserve
     (Available_Negative : Interfaces.Unsigned_8;
      Available : System.Address; Available_Length : Interfaces.C.size_t;
      Withheld : System.Address; Withheld_Length : Interfaces.C.size_t;
      Floor : System.Address; Floor_Length : Interfaces.C.size_t;
      Requested : System.Address; Requested_Length : Interfaces.C.size_t)
      return Interfaces.Unsigned_8
     with Export, Convention => C, External_Name => "wl_resources_can_reserve";
   end Resources_Transport;

   package Resource_Policy_Transport is
      subtype U8 is Interfaces.Unsigned_8;
      subtype Size is Interfaces.C.size_t;
   function ABI_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_resource_policy_abi_version";
   function Layout_Size (Selector : U8) return Size
     with Export, Convention => C, External_Name => "wl_resource_policy_layout_size";
   function Layout_Offset (Selector, Field : U8) return Size
     with Export, Convention => C, External_Name => "wl_resource_policy_layout_offset";
   function Admit
     (Data : System.Address; Data_Length : Size;
      Input : System.Address; Disks : System.Address; Disk_Count : Size;
      Result : System.Address) return U8
     with Export, Convention => C, External_Name => "wl_resource_policy_admit";
   end Resource_Policy_Transport;

   package Resource_Ledger_Transport is
      subtype U8 is Interfaces.Unsigned_8;
      subtype Size is Interfaces.C.size_t;
   function ABI_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_resource_ledger_abi_version";
   function Layout_Size (Selector : U8) return Size
     with Export, Convention => C, External_Name => "wl_resource_ledger_layout_size";
   function Layout_Offset (Selector, Field : U8) return Size
     with Export, Convention => C, External_Name => "wl_resource_ledger_layout_offset";
   function Compute
     (Data : System.Address; Data_Length : Size;
      Rows : System.Address; Row_Count : Size;
      Detail_Data : System.Address; Detail_Length : Size;
      Total_Data : System.Address; Total_Length : Size;
      Details : System.Address; Result : System.Address) return U8
     with Export, Convention => C, External_Name => "wl_resource_ledger_compute";
   function Headroom
     (Data : System.Address; Data_Length : Size;
      Available, Withheld, Floor : System.Address;
      Output : System.Address; Output_Length : Size;
      Result : System.Address) return U8
     with Export, Convention => C,
       External_Name => "wl_resource_ledger_headroom";
   end Resource_Ledger_Transport;

   package Resource_Run_Ledger_Transport is
      subtype U8 is Interfaces.Unsigned_8;
      subtype Size is Interfaces.C.size_t;
   function Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_resource_run_ledger_version_v1";
   function Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long
     with Export, Convention => C, External_Name => "wl_resource_run_ledger_layout_v1";
   function Check
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Arena : System.Address; Arena_Length : Interfaces.C.size_t;
      Before_Rows : System.Address; Before_Count : Interfaces.C.size_t;
      Proposed_Rows : System.Address; Proposed_Count : Interfaces.C.size_t;
      Native : System.Address; Native_Count : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_resource_run_ledger_check_v1";
   end Resource_Run_Ledger_Transport;

   package Reservation_Lifecycle_Transport is
      subtype U8 is Interfaces.Unsigned_8;
      subtype Size is Interfaces.C.size_t;
   function ABI_Version return Interfaces.Unsigned_32
     with Export, Convention => C,
       External_Name => "wl_reservation_lifecycle_abi_version";
   function Layout_Size return Size
     with Export, Convention => C,
       External_Name => "wl_reservation_lifecycle_row_size";
   function Layout_Offset (Field : U8) return Size
     with Export, Convention => C,
       External_Name => "wl_reservation_lifecycle_row_offset";
   function Plan
     (Data : System.Address; Data_Length : Size;
      Rows : System.Address; Row_Count : Size;
      Mode, Present : U8; Requested_First, Requested_Length : Size;
      Removed : System.Address; Removed_Length : Size) return U8
     with Export, Convention => C,
       External_Name => "wl_reservation_lifecycle_plan";
   end Reservation_Lifecycle_Transport;

   function Pending_Decide_V1 (Input, Output : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_pending_decide_v1";

   function Pending_Decide_V2 (Input, Output : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_pending_decide_v2";

   -- One synchronous immutable owned capture. Numeric extents do not confer
   -- foreign allocation validity; the caller keeps Input and Status live.
   function Excluded_Source_Owner_Decide_V1
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_excluded_source_owner_decide_v1";

   function Startup_Admission_Decide_V1
     (Input : System.Address; Length : Interfaces.C.size_t;
      Name : System.Address; Name_Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_startup_admission_decide_v1";

   function Startup_Owner_Admission_Decide_V1
     (Input : System.Address; Length : Interfaces.C.size_t;
      Name : System.Address; Name_Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_startup_owner_admission_decide_v1";

   function Startup_Admission_Transition_V1
     (Before : System.Address; Before_Length : Interfaces.C.size_t;
      After : System.Address; After_Length : Interfaces.C.size_t;
      Name : System.Address; Name_Length : Interfaces.C.size_t;
      Before_Action, After_Action : Interfaces.Unsigned_64;
      Status, Position : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_startup_admission_transition_v1";

   function Startup_Owner_Admission_Transition_V1
     (Before : System.Address; Before_Length : Interfaces.C.size_t;
      After : System.Address; After_Length : Interfaces.C.size_t;
      Name : System.Address; Name_Length : Interfaces.C.size_t;
      Before_Action, After_Action : Interfaces.Unsigned_64;
      Status, Position : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_startup_owner_admission_transition_v1";


   -- Complete original scoped/observation/actor/child ABI; no prior status inputs.
   function Resource_Scoped_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_resource_scoped_run_ledger_version_v1";
   function Resource_Scoped_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long
     with Export, Convention => C, External_Name => "wl_resource_scoped_run_ledger_layout_v1";
   function Resource_Scoped_Check
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      History : System.Address;
      History_Count : Interfaces.C.size_t;
      Proposed_History : System.Address;
      Proposed_History_Count : Interfaces.C.size_t;
      Rows : System.Address;
      Rows_Count : Interfaces.C.size_t;
      Proposed_Rows : System.Address;
      Proposed_Rows_Count : Interfaces.C.size_t;
      Projection : System.Address;
      Projection_Count : Interfaces.C.size_t;
      Proposed_Projection : System.Address;
      Proposed_Projection_Count : Interfaces.C.size_t;
      Buckets : System.Address;
      Buckets_Count : Interfaces.C.size_t;
      Proposed_Buckets : System.Address;
      Proposed_Buckets_Count : Interfaces.C.size_t;
      Actual_Buckets : System.Address;
      Actual_Buckets_Count : Interfaces.C.size_t;
      Observed : System.Address;
      Observed_Count : Interfaces.C.size_t;
      Facts : System.Address;
      Facts_Count : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_resource_scoped_run_ledger_check_v1";
   function Resource_Scoped_Validate
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      History : System.Address;
      History_Count : Interfaces.C.size_t;
      Proposed_History : System.Address;
      Proposed_History_Count : Interfaces.C.size_t;
      Rows : System.Address;
      Rows_Count : Interfaces.C.size_t;
      Proposed_Rows : System.Address;
      Proposed_Rows_Count : Interfaces.C.size_t;
      Projection : System.Address;
      Projection_Count : Interfaces.C.size_t;
      Proposed_Projection : System.Address;
      Proposed_Projection_Count : Interfaces.C.size_t;
      Buckets : System.Address;
      Buckets_Count : Interfaces.C.size_t;
      Proposed_Buckets : System.Address;
      Proposed_Buckets_Count : Interfaces.C.size_t;
      Actual_Buckets : System.Address;
      Actual_Buckets_Count : Interfaces.C.size_t;
      Observed : System.Address;
      Observed_Count : Interfaces.C.size_t;
      Facts : System.Address;
      Facts_Count : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_resource_scoped_run_ledger_validate_v1";
   function Resource_Scoped_Classify
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      History : System.Address;
      History_Count : Interfaces.C.size_t;
      Proposed_History : System.Address;
      Proposed_History_Count : Interfaces.C.size_t;
      Rows : System.Address;
      Rows_Count : Interfaces.C.size_t;
      Proposed_Rows : System.Address;
      Proposed_Rows_Count : Interfaces.C.size_t;
      Projection : System.Address;
      Projection_Count : Interfaces.C.size_t;
      Proposed_Projection : System.Address;
      Proposed_Projection_Count : Interfaces.C.size_t;
      Buckets : System.Address;
      Buckets_Count : Interfaces.C.size_t;
      Proposed_Buckets : System.Address;
      Proposed_Buckets_Count : Interfaces.C.size_t;
      Actual_Buckets : System.Address;
      Actual_Buckets_Count : Interfaces.C.size_t;
      Observed : System.Address;
      Observed_Count : Interfaces.C.size_t;
      Facts : System.Address;
      Facts_Count : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_resource_scoped_run_ledger_classify_v1";
   function Resource_Observation_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_resource_observation_version_v1";
   function Resource_Observation_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long
     with Export, Convention => C, External_Name => "wl_resource_observation_layout_v1";
   function Resource_Observation_Classify
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_resource_observation_classify_v1";
   function Resource_Observation_Current
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_resource_observation_current_v1";
   function Resource_Observation_Genesis_Current
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_resource_observation_genesis_current_v1";
   function Resource_Actor_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_resource_actor_admission_version_v1";
   function Resource_Actor_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long
     with Export, Convention => C, External_Name => "wl_resource_actor_admission_layout_v1";
   function Resource_Actor_Check
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      History : System.Address;
      History_Count : Interfaces.C.size_t;
      Proposed_History : System.Address;
      Proposed_History_Count : Interfaces.C.size_t;
      Rows : System.Address;
      Rows_Count : Interfaces.C.size_t;
      Proposed_Rows : System.Address;
      Proposed_Rows_Count : Interfaces.C.size_t;
      Projection : System.Address;
      Projection_Count : Interfaces.C.size_t;
      Proposed_Projection : System.Address;
      Proposed_Projection_Count : Interfaces.C.size_t;
      Buckets : System.Address;
      Buckets_Count : Interfaces.C.size_t;
      Proposed_Buckets : System.Address;
      Proposed_Buckets_Count : Interfaces.C.size_t;
      Actual_Buckets : System.Address;
      Actual_Buckets_Count : Interfaces.C.size_t;
      Observed : System.Address;
      Observed_Count : Interfaces.C.size_t;
      Facts : System.Address;
      Facts_Count : Interfaces.C.size_t;
      Capabilities : System.Address;
      Capabilities_Count : Interfaces.C.size_t;
      Groups : System.Address;
      Groups_Count : Interfaces.C.size_t;
      Proc_Groups : System.Address;
      Proc_Groups_Count : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_resource_actor_admission_check_v1";
   function Resource_Actor_Execution_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_resource_actor_execution_version_v1";
   function Resource_Actor_Execution_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long
     with Export, Convention => C, External_Name => "wl_resource_actor_execution_layout_v1";
   function Resource_Actor_Execution_Decide
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      History : System.Address;
      History_Count : Interfaces.C.size_t;
      Proposed_History : System.Address;
      Proposed_History_Count : Interfaces.C.size_t;
      Rows : System.Address;
      Rows_Count : Interfaces.C.size_t;
      Proposed_Rows : System.Address;
      Proposed_Rows_Count : Interfaces.C.size_t;
      Projection : System.Address;
      Projection_Count : Interfaces.C.size_t;
      Proposed_Projection : System.Address;
      Proposed_Projection_Count : Interfaces.C.size_t;
      Buckets : System.Address;
      Buckets_Count : Interfaces.C.size_t;
      Proposed_Buckets : System.Address;
      Proposed_Buckets_Count : Interfaces.C.size_t;
      Actual_Buckets : System.Address;
      Actual_Buckets_Count : Interfaces.C.size_t;
      Observed : System.Address;
      Observed_Count : Interfaces.C.size_t;
      Facts : System.Address;
      Facts_Count : Interfaces.C.size_t;
      Capabilities : System.Address;
      Capabilities_Count : Interfaces.C.size_t;
      Groups : System.Address;
      Groups_Count : Interfaces.C.size_t;
      Proc_Groups : System.Address;
      Proc_Groups_Count : Interfaces.C.size_t;
      Authority_Input : System.Address;
      Authority_Input_Length : Interfaces.C.size_t;
      Authority_Arena : System.Address;
      Authority_Arena_Length : Interfaces.C.size_t;
      Authority_Grants : System.Address;
      Authority_Grants_Count : Interfaces.C.size_t;
      Authority_Uses : System.Address;
      Authority_Uses_Count : Interfaces.C.size_t;
      Authority_Receipts : System.Address;
      Authority_Receipts_Count : Interfaces.C.size_t;
      Authority_Events : System.Address;
      Authority_Events_Count : Interfaces.C.size_t;
      Crosswalk : System.Address;
      Crosswalk_Length : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_resource_actor_execution_decide_v1";
   function Child_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_resource_child_execution_version_v1";
   function Child_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long
     with Export, Convention => C, External_Name => "wl_resource_child_execution_layout_v1";
   function Child_Decide
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      History : System.Address;
      History_Count : Interfaces.C.size_t;
      Proposed_History : System.Address;
      Proposed_History_Count : Interfaces.C.size_t;
      Rows : System.Address;
      Rows_Count : Interfaces.C.size_t;
      Proposed_Rows : System.Address;
      Proposed_Rows_Count : Interfaces.C.size_t;
      Projection : System.Address;
      Projection_Count : Interfaces.C.size_t;
      Proposed_Projection : System.Address;
      Proposed_Projection_Count : Interfaces.C.size_t;
      Buckets : System.Address;
      Buckets_Count : Interfaces.C.size_t;
      Proposed_Buckets : System.Address;
      Proposed_Buckets_Count : Interfaces.C.size_t;
      Actual_Buckets : System.Address;
      Actual_Buckets_Count : Interfaces.C.size_t;
      Observed : System.Address;
      Observed_Count : Interfaces.C.size_t;
      Facts : System.Address;
      Facts_Count : Interfaces.C.size_t;
      Capabilities : System.Address;
      Capabilities_Count : Interfaces.C.size_t;
      Groups : System.Address;
      Groups_Count : Interfaces.C.size_t;
      Proc_Groups : System.Address;
      Proc_Groups_Count : Interfaces.C.size_t;
      Authority_Input : System.Address;
      Authority_Input_Length : Interfaces.C.size_t;
      Authority_Arena : System.Address;
      Authority_Arena_Length : Interfaces.C.size_t;
      Authority_Grants : System.Address;
      Authority_Grants_Count : Interfaces.C.size_t;
      Authority_Uses : System.Address;
      Authority_Uses_Count : Interfaces.C.size_t;
      Authority_Receipts : System.Address;
      Authority_Receipts_Count : Interfaces.C.size_t;
      Authority_Events : System.Address;
      Authority_Events_Count : Interfaces.C.size_t;
      Crosswalk : System.Address;
      Crosswalk_Length : Interfaces.C.size_t;
      Child_Input : System.Address;
      Child_Input_Length : Interfaces.C.size_t;
      Tasks : System.Address;
      Tasks_Count : Interfaces.C.size_t;
      Processes : System.Address;
      Processes_Count : Interfaces.C.size_t;
      Namespaces : System.Address;
      Namespaces_Count : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_resource_child_execution_decide_v1";

   function Operation_Result_Relation
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      Grants : System.Address;
      Grant_Count : Interfaces.C.size_t;
      Grant_Length : Interfaces.C.size_t;
      Uses : System.Address;
      Use_Count : Interfaces.C.size_t;
      Use_Length : Interfaces.C.size_t;
      Receipts : System.Address;
      Receipt_Count : Interfaces.C.size_t;
      Receipt_Length : Interfaces.C.size_t;
      Events : System.Address;
      Event_Count : Interfaces.C.size_t;
      Event_Length : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_operation_result_relation_v1";

   function Ordinary_Receipt_Policy_Version_V35 return Interfaces.Unsigned_32
     with Export, Convention => C,
       External_Name => "wl_ordinary_receipt_policy_version_v35";
   function Ordinary_Receipt_Policy_Decide_V35
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Mode : Interfaces.Unsigned_8) return Interfaces.C.int
     with Export, Convention => C,
       External_Name => "wl_ordinary_receipt_policy_decide_v35";
   function Ordinary_Receipt_Verify_History_V35
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Differences : System.Address) return Interfaces.C.int
     with Export, Convention => C,
       External_Name => "wl_ordinary_receipt_verify_history_v35";

function Transaction_Relation_V1 (Input : System.Address; Length : Interfaces.C.size_t) return Interfaces.Unsigned_8 with Export, Convention => C, External_Name => "wl_transaction_relation_v1";
   --  All spans are one-based positions in a caller-owned stable DATA lease.
   --  Return Genesis_Correspondence'Pos (0..3), or 255 for wire/extent error.
   function Genesis_Archive_Matches_V1
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      File_First, File_Length, Row_First, Row_Length : Interfaces.Integer_64)
      return Interfaces.C.int
     with Export, Convention => C,
       External_Name => "wl_genesis_archive_matches_v1";
   --  Differential control surface: Mode 0 parses any complete JSON float
   --  token; Mode 1 additionally requires the exact Python repr spelling.
   --  Output is eight big-endian binary64 bytes. Codes: 0 conversion, 1
   --  invalid/nonfinite/noncanonical, 255 invalid wire. It does not authorize
   --  custody, startup or any effect. Output and input leases must be disjoint.
   function Decimal_Binary64_V1
     (Mode : Interfaces.Unsigned_8;
      Data : System.Address; Data_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Interfaces.C.int
     with Export, Convention => C,
       External_Name => "wl_decimal_binary64_v1";
   --  Full canonical(S.record(...)) projection against original operation
   --  archive, without scoped unwrap or concatenation. Both leases immutable;
   --  read-only aliasing allowed. Codes: 0 differs, 1 matches, 255 wire invalid.
   function Operation_Archive_JSON_Matches_V1
     (JSON_Data : System.Address; JSON_Length : Interfaces.C.size_t;
      Archive_Data : System.Address; Archive_Length : Interfaces.C.size_t)
      return Interfaces.C.int
     with Export, Convention => C,
       External_Name => "wl_operation_archive_json_matches_v1";
   --  Full typed-scope correspondence to canonical JSON plus optional one LF,
   --  on distinct immutable borrowed arrays. Original enum 0..3; 255 wire.
   function Scoped_Archive_JSON_Matches_V1
     (JSON_Data : System.Address; JSON_Length : Interfaces.C.size_t;
      Archive_Data : System.Address; Archive_Length : Interfaces.C.size_t)
      return Interfaces.C.int
     with Export, Convention => C,
       External_Name => "wl_scoped_archive_json_matches_v1";

   function Journal_Witness_Decide_V1
     (Kind : Interfaces.Unsigned_8;
      Current : System.Address; Current_Length : Interfaces.C.size_t;
      Input : System.Address; Input_Length : Interfaces.C.size_t;
      Decision : access Interfaces.Unsigned_64) return Interfaces.C.int
     with Export, Convention => C,
       External_Name => "wl_journal_witness_decide_v1";


   function Evaluation_Policy_Project_V1
     (      Requirement_Address : System.Address;
      Requirement_Length : Interfaces.C.size_t;
      Additional_Address : System.Address;
      Additional_Length : Interfaces.C.size_t;
      Finalization : Interfaces.Unsigned_8;
      Output : System.Address;
      Capacity : Interfaces.C.size_t)
      return Interfaces.C.size_t
     with Export, Convention => C, External_Name => "wl_evaluation_policy_project_v1";

   function Evaluation_Capture_Plan_V1
     (      Rows_Address : System.Address;
      Rows_Length : Interfaces.C.size_t;
      Invocations_Address : System.Address;
      Invocations_Length : Interfaces.C.size_t;
      Returns_Address : System.Address;
      Returns_Length : Interfaces.C.size_t;
      Expected_Requirement_Address : System.Address;
      Expected_Requirement_Length : Interfaces.C.size_t;
      Returned_Context_Address : System.Address;
      Returned_Context_Length : Interfaces.C.size_t;
      Output : System.Address;
      Capacity : Interfaces.C.size_t)
      return Interfaces.C.size_t
     with Export, Convention => C, External_Name => "wl_evaluation_capture_plan_v1";

   function Report_Parser_ABI return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "worldline_report_parser_abi";
   function Parse_Report
     (Format_Address : System.Address; Format_Length : Interfaces.C.size_t;
      Profile_Address : System.Address; Profile_Length : Interfaces.C.size_t;
      Exit_Address : System.Address; Exit_Length : Interfaces.C.size_t;
      Stdout_Address : System.Address; Stdout_Length : Interfaces.C.size_t;
      Stderr_Address : System.Address; Stderr_Length : Interfaces.C.size_t;
      Result_Address : System.Address; Result_Length : Interfaces.C.size_t;
      Result_Present : Interfaces.C.int;
      Output_Address : System.Address; Output_Capacity : Interfaces.C.size_t;
      Output_Required, Status_Output, Class_Output : System.Address)
      return Interfaces.C.int
     with Export, Convention => C, External_Name => "worldline_parse_report";

   function Protected_Paths_Touched_V1
     (Requirement_Address : System.Address; Requirement_Length : Interfaces.C.size_t;
      Delta_Address : System.Address; Delta_Length : Interfaces.C.size_t)
      return Interfaces.Unsigned_8
     with Export, Convention => C, External_Name => "wl_protected_paths_touched_v1";

   function Evaluation_Acquisitions_Closed_V1
     (Subject_Address : System.Address;
      Subject_Length : Interfaces.C.size_t;
      Owners_Address : System.Address;
      Owners_Length : Interfaces.C.size_t;
      Acquisitions_Address : System.Address;
      Acquisitions_Length : Interfaces.C.size_t)
      return Interfaces.Unsigned_8
     with Export, Convention => C, External_Name => "wl_evaluation_acquisitions_closed_v1";

function Evaluation_Producer_Derive_V1
  (Expected : System.Address; Expected_Length : Interfaces.C.size_t;
   Observed : System.Address; Observed_Length : Interfaces.C.size_t;
   Result_Record : System.Address; Result_Length : Interfaces.C.size_t;
   Declared : System.Address; Declared_Length : Interfaces.C.size_t;
   Agent_Terminal : System.Address; Agent_Terminal_Length : Interfaces.C.size_t;
   Out_Raw, Out_Confinement : System.Address) return Interfaces.Unsigned_8
  with Export, Convention => C, External_Name => "wl_evaluation_producer_derive_v1";

   function Manager_Resource_Lifecycle_V1
     (Capture_Address : System.Address; Capture_Length : Interfaces.C.size_t;
      Output_Address : System.Address; Output_Capacity : Interfaces.C.size_t;
      Output_Required : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_manager_resource_lifecycle_v1";

   function Ordinary_Reservation_ABI return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_ordinary_reservation_lifecycle_abi_version";
   function Ordinary_Reservation_Plan
     (Input_Address : System.Address; Input_Length : Interfaces.C.size_t;
      Mask_Address : System.Address; Mask_Length : Interfaces.C.size_t;
      Code_Address, Position_Address : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_ordinary_reservation_lifecycle_plan";

   function Runner_Lifecycle_Allowed_V1
     (Owner_Address : System.Address;
      Owner_Length : Interfaces.C.size_t;
      Requested : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
     with Export, Convention => C,
       External_Name => "wl_runner_lifecycle_allowed_v1";

   function Runner_Outcome_Decide_V1
     (Capture_Address : System.Address;
      Capture_Length : Interfaces.C.size_t;
      Output : System.Address;
      Capacity : Interfaces.C.size_t) return Interfaces.C.size_t
     with Export, Convention => C,
       External_Name => "wl_runner_outcome_decide_v1";

   function Recovery_Packet_Decide
     (Data : System.Address; Length : Interfaces.C.size_t;
      Collapse_Code, Owner_Code : System.Address) return Interfaces.Unsigned_8
     with Export, Convention => C, External_Name => "wl_recovery_packet_decide_v1";
   function Recovery_Packet_Projection_Matches
     (Data : System.Address; Length : Interfaces.C.size_t;
      Expected : System.Address; Expected_Length : Interfaces.C.size_t)
      return Interfaces.Unsigned_8
     with Export, Convention => C,
       External_Name => "wl_recovery_packet_projection_matches_v1";
   function Recovery_Packet_Decide_With_Facts
     (Data : System.Address; Length : Interfaces.C.size_t;
      Facts : System.Address; Facts_Length : Interfaces.C.size_t;
      Collapse_Code, Owner_Code : System.Address) return Interfaces.Unsigned_8
     with Export, Convention => C,
       External_Name => "wl_recovery_packet_decide_with_facts_v1";
   function Recovery_Syntax_Inputs
     (Data : System.Address; Length : Interfaces.C.size_t;
      Operation_Mode : Interfaces.Unsigned_8; Output : System.Address;
      Capacity : Interfaces.C.size_t) return Interfaces.C.size_t
     with Export, Convention => C,
       External_Name => "wl_recovery_syntax_inputs_v1";

   function Custody_Load_Decide_V2
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_custody_load_decide_v2";
   function Custody_Mutation_Decide_V2
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address; Output : System.Address;
      Capacity : Interfaces.C.size_t; Written : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_custody_mutation_decide_v2";
   function Custody_Cleanup_Decide_V2
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_custody_cleanup_decide_v2";
   function Custody_Closed_Decide_V2
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_custody_closed_decide_v2";
  function Custody_Context_View_V2
    (Input : System.Address; Length : Interfaces.C.size_t;
     Status, Position : System.Address; Output : System.Address;
     Capacity : Interfaces.C.size_t; Written : System.Address) return Interfaces.C.int
    with Export, Convention => C, External_Name => "wl_custody_context_view_v2";
   function Custody_Retry_Decide_V2
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address; Output : System.Address;
      Capacity : Interfaces.C.size_t; Written : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_custody_retry_decide_v2";
   function Custody_Serving_Decide_V2
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_custody_serving_decide_v2";
   function Custody_Successor_LE_V2
     (Input : System.Address; Length : Interfaces.C.size_t;
      Output : System.Address; Capacity : Interfaces.C.size_t;
      Needed : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_custody_successor_le_v2";
   function Custody_Operation_Startup_Decide_V2
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
     with Export, Convention => C,
       External_Name => "wl_custody_operation_startup_decide_v2";
   function Custody_Operation_Append_Decide_V2
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
     with Export, Convention => C,
       External_Name => "wl_custody_operation_append_decide_v2";
   function Custody_Operation_Recovery_Decide_V2
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
     with Export, Convention => C,
       External_Name => "wl_custody_operation_recovery_decide_v2";
   function Custody_Operation_Bootstrap_Decide_V2
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
     with Export, Convention => C,
       External_Name => "wl_custody_operation_bootstrap_decide_v2";

   function Custody_Provision_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_custody_provision_version_v2";
   function Custody_Provision_Layout (Kind, Field : Interfaces.Unsigned_8)
      return Interfaces.C.size_t
     with Export, Convention => C, External_Name => "wl_custody_provision_layout_v2";
   function Custody_Provision_Verify
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Spans : System.Address; Span_Count, Genesis_Count, Event_Count, Head_Count : Interfaces.C.size_t;
      Output : System.Address; Output_Size : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_custody_provision_decide_v2";
   function Root_Worker_Output_Next_V1
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address; Ordinal : System.Address;
      Capacity : Interfaces.C.size_t; Ordinal_Length : System.Address)
      return Interfaces.C.int
     with Export, Convention => C,
       External_Name => "wl_root_worker_output_next_v1";

   function Root_Worker_Output_Replay_V1
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address; Ordinal : System.Address;
      Capacity : Interfaces.C.size_t; Ordinal_Length : System.Address)
      return Interfaces.C.int
     with Export, Convention => C,
       External_Name => "wl_root_worker_output_replay_v1";
   function Root_Worker_Output_Written_V1
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address; Ordinal : System.Address;
      Capacity : Interfaces.C.size_t; Ordinal_Length : System.Address)
      return Interfaces.C.int
     with Export, Convention => C,
       External_Name => "wl_root_worker_output_written_v1";

   function Root_Worker_Output_Prefix_V1
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address; Ordinal : System.Address;
      Capacity : Interfaces.C.size_t; Ordinal_Length : System.Address)
      return Interfaces.C.int
     with Export, Convention => C,
       External_Name => "wl_root_worker_output_prefix_v1";
   function Full_Physical_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_full_physical_version_v1";
   function Full_Physical_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long
     with Export, Convention => C, External_Name => "wl_full_physical_layout_v1";
   function Full_Physical_Exchange (Original_Peer_Fd, Data_Fd, Transaction_Fd, Payload_Fd : Interfaces.C.int;
      Input : System.Address; Input_Length : Interfaces.C.size_t;
      Arena : System.Address; Arena_Length : Interfaces.C.size_t;
      Grants : System.Address; Grant_Count, Grant_Length : Interfaces.C.size_t;
      Uses : System.Address; Use_Count, Use_Length : Interfaces.C.size_t;
      Rows : System.Address; Row_Count, Row_Length : Interfaces.C.size_t;
      Observed : System.Address; Observed_Count, Observed_Length : Interfaces.C.size_t;
      Worker_Receipts : System.Address; Worker_Receipt_Count, Worker_Receipt_Length : Interfaces.C.size_t;
      Worker_Events : System.Address; Worker_Event_Count, Worker_Event_Length : Interfaces.C.size_t;
      Effect_Receipts : System.Address; Effect_Receipt_Count, Effect_Receipt_Length : Interfaces.C.size_t;
      Effect_Events : System.Address; Effect_Event_Count, Effect_Event_Length : Interfaces.C.size_t;
      Actuation : System.Address; Actuation_Length : Interfaces.C.size_t;
      Witness : System.Address; Witness_Length : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_full_physical_exchange_v1";
   function Full_Physical_Recover (Original_Peer_Fd, Data_Fd, Transaction_Fd, Payload_Fd : Interfaces.C.int;
      Input : System.Address; Input_Length : Interfaces.C.size_t;
      Arena : System.Address; Arena_Length : Interfaces.C.size_t;
      Grants : System.Address; Grant_Count, Grant_Length : Interfaces.C.size_t;
      Uses : System.Address; Use_Count, Use_Length : Interfaces.C.size_t;
      Rows : System.Address; Row_Count, Row_Length : Interfaces.C.size_t;
      Observed : System.Address; Observed_Count, Observed_Length : Interfaces.C.size_t;
      Worker_Receipts : System.Address; Worker_Receipt_Count, Worker_Receipt_Length : Interfaces.C.size_t;
      Worker_Events : System.Address; Worker_Event_Count, Worker_Event_Length : Interfaces.C.size_t;
      Effect_Receipts : System.Address; Effect_Receipt_Count, Effect_Receipt_Length : Interfaces.C.size_t;
      Effect_Events : System.Address; Effect_Event_Count, Effect_Event_Length : Interfaces.C.size_t;
      Actuation : System.Address; Actuation_Length : Interfaces.C.size_t;
      Witness : System.Address; Witness_Length : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_full_physical_recover_v1";
   function Actuation_Decide(P : System.Address) return Interfaces.C.unsigned_char
     with Export, Convention => C, External_Name => "wl_actuation_decide";

end Worldline.C_API;
