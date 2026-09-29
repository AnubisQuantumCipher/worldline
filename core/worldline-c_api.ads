with Interfaces;
with Interfaces.C;
with System;

package Worldline.C_API with SPARK_Mode => Off is

   subtype C_Hash_Index is Natural range 0 .. 31;
   type C_Hash is array (C_Hash_Index) of Interfaces.Unsigned_8
     with Convention => C;

   type C_Collapse_Request is record
      Candidate_State            : Interfaces.Unsigned_8;
      Has_Conflicts              : Interfaces.Unsigned_8;
      Has_Foreign_Managed_Writes : Interfaces.Unsigned_8;
      Reserved                   : Interfaces.Unsigned_8;
      Expected_Parent            : C_Hash;
      Candidate_Parent           : C_Hash;
      Expected_Owner             : C_Hash;
      Candidate_Owner            : C_Hash;
      Expected_Base              : C_Hash;
      Candidate_Base             : C_Hash;
      Expected_Delta             : C_Hash;
      Candidate_Delta            : C_Hash;
      Expected_Root_Set          : C_Hash;
      Candidate_Root_Set         : C_Hash;
      Expected_Staged_Root       : C_Hash;
      Actual_Staged_Root         : C_Hash;
      Expected_Validation_Context  : C_Hash;
      Candidate_Validation_Context : C_Hash;
      Tested_Root                  : C_Hash;
      Staged_Content_Root          : C_Hash;
      --  Appended for 1.5.0. Existing field offsets are unchanged.
      Execution_Evidence_Complete  : Interfaces.Unsigned_8;
      Reserved_2                   : Interfaces.Unsigned_8;
      Reserved_3                   : Interfaces.Unsigned_8;
      Reserved_4                   : Interfaces.Unsigned_8;
      Expected_Executed_Verifier   : C_Hash;
      Actual_Executed_Verifier     : C_Hash;
      --  Appended for 1.8.0 (request layout 4). Existing offsets unchanged.
      Evaluation_Mode              : Interfaces.Unsigned_8;
      Checkpoint_Witnessed         : Interfaces.Unsigned_8;
      Reserved_5                   : Interfaces.Unsigned_8;
      Reserved_6                   : Interfaces.Unsigned_8;
      Expected_Checkpoint          : C_Hash;
      Witnessed_Checkpoint         : C_Hash;
   end record
     with Convention => C;

   --  The ABI generation of this library: request layouts, record layouts and
   --  the meaning of every exported code. The runtime refuses to load a
   --  library that reports a different generation.
   ABI_Version : constant Interfaces.Unsigned_32 := 4;

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
   --  classification, 3 evidence presence. 0 for an unknown selector.
   function Layout_Size
     (Selector : Interfaces.Unsigned_8) return Interfaces.C.size_t
     with Export, Convention => C, External_Name => "wl_layout_size";

end Worldline.C_API;
