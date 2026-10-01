with Interfaces;
with Interfaces.C;
with System;

--  Copying adapter only; selection is in Worldline.Recovery (SPARK).
--  Each present pointer names readable storage of the exact declared extent,
--  live and unchanged for the call. Shape checks do not prove that premise.
package Worldline.Recovery_C_API with SPARK_Mode => Off is
   function ABI_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_recovery_abi_version";

   --  Returns declaration-order Recovery_Action (0/1/2), or 255 for an invalid
   --  transport shape or caught exception. An absent marker's pointer/length
   --  is ignored. Empty expected/present identities remain legal and distinct
   --  from absence. Never interpret 255 as an action.
   function Select_Action
     (Expected : System.Address; Expected_Length : Interfaces.C.size_t;
      Live_Present : Interfaces.Unsigned_8;
      Live : System.Address; Live_Length : Interfaces.C.size_t;
      Prepared_Present : Interfaces.Unsigned_8;
      Prepared : System.Address; Prepared_Length : Interfaces.C.size_t)
      return Interfaces.Unsigned_8
     with Export, Convention => C, External_Name => "wl_recovery_select";
end Worldline.Recovery_C_API;
