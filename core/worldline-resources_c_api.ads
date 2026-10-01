with Interfaces;
with Interfaces.C;
with System;

--  Pointer marshalling remains an explicit C boundary. The actual arithmetic
--  decision belongs to Resource_Wire/Resources, including signed availability.
package Worldline.Resources_C_API with SPARK_Mode => Off is
   function ABI_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_resources_abi_version";

   --  Return 1 for admissible arithmetic, 0 for insufficient capacity and 255
   --  for a checked shape error or caught exception. Input storage is
   --  caller-owned, readable for the stated extent, and must remain live and
   --  unchanged throughout the call; raw-pointer readability is not proved.
   --  A null pointer
   --  denotes zero only when its length is zero.
   function Can_Reserve
     (Available_Negative : Interfaces.Unsigned_8;
      Available : System.Address; Available_Length : Interfaces.C.size_t;
      Withheld : System.Address; Withheld_Length : Interfaces.C.size_t;
      Floor : System.Address; Floor_Length : Interfaces.C.size_t;
      Requested : System.Address; Requested_Length : Interfaces.C.size_t)
      return Interfaces.Unsigned_8
     with Export, Convention => C, External_Name => "wl_resources_can_reserve";
end Worldline.Resources_C_API;
