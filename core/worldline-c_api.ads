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
   end record
     with Convention => C;

   type C_Collapse_Request_Access is access constant C_Collapse_Request
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

   function Collapse_Decide
     (Request : C_Collapse_Request_Access) return Interfaces.Unsigned_8
     with Export, Convention => C, External_Name => "wl_collapse_decide";

end Worldline.C_API;
