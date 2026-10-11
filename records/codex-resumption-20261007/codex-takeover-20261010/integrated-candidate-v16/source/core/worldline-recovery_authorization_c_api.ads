with Worldline.Recovery_Authorization_Wire;
with Interfaces;
with Interfaces.C;
with System;

package Worldline.Recovery_Authorization_C_API with SPARK_Mode => On is
   function Version return Interfaces.Unsigned_32
     with Export, Convention => C,
       External_Name => "wl_recovery_authorization_version_v2";
   function Layout
     (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long
     with Export, Convention => C,
       External_Name => "wl_recovery_authorization_layout_v2";
   --  Both fixed-size records are copied before any pure decision. Malformed
   --  representations return transport refusal; no weaker recovery fallback.
   function Transport_Valid
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Boolean;

   function Decide
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t;
      Input_View : access constant Worldline.Recovery_Authorization_Wire.Raw_Request;
      Output_View : access Worldline.Recovery_Authorization_Wire.Raw_Result)
      return Interfaces.C.int
     with Side_Effects;
end Worldline.Recovery_Authorization_C_API;
