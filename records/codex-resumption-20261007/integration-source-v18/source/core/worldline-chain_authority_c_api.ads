with Interfaces;
with Interfaces.C;
with System;
package Worldline.Chain_Authority_C_API with SPARK_Mode => On is
   function Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_chain_authority_version_v1";
   function Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long
     with Export, Convention => C, External_Name => "wl_chain_authority_layout_v1";
   function Replay
     (Anchors : System.Address; Anchors_Length : Interfaces.C.size_t;
      Rows : System.Address; Rows_Count, Rows_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_chain_authority_replay_v1";
end Worldline.Chain_Authority_C_API;
