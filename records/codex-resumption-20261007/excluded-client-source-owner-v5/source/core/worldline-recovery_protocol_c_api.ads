with Worldline.Recovery_Protocol_Wire;
with Interfaces;
with Interfaces.C;
with System;
package Worldline.Recovery_Protocol_C_API with SPARK_Mode => On is
   function Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_recovery_protocol_version_v1";
   function Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long
     with Export, Convention => C, External_Name => "wl_recovery_protocol_layout_v1";
   function Transport_Valid
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Boolean;

   function Decide
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t;
      Input_View : access constant Worldline.Recovery_Protocol_Wire.Raw_Request;
      Output_View : access Worldline.Recovery_Protocol_Wire.Raw_Result)
      return Interfaces.C.int
     with Side_Effects;
end Worldline.Recovery_Protocol_C_API;
