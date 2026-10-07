with Interfaces;
with Interfaces.C;
with System;
package Resource_Run_Ledger_C_API with SPARK_Mode => On is
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
end Resource_Run_Ledger_C_API;
