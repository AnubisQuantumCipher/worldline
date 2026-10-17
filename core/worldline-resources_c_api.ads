--  Typed observer entry points retain the original complete snapshot/decoder bodies.
--  The unchanged C exports are enrolled in the existing sole Off Worldline.C_API.
--  C_API maps constrained views only after numeric transport validation; the
--  original loops below take the single snapshot before any foreign output write.
with Worldline.Resources;
with Interfaces;

--  Pointer marshalling remains an explicit C boundary. The actual arithmetic
--  decision belongs to Resource_Wire/Resources, including signed availability.
package Worldline.Resources_C_API with SPARK_Mode => On is
   function ABI_Version return Interfaces.Unsigned_32;

   --  Return 1 for admissible arithmetic, 0 for insufficient capacity and 255
   --  for a checked shape error. Storage or contract exceptions propagate to
   --  the existing Off Worldline.C_API transport, which returns 255. Input
   --  storage is caller-owned, readable for the stated extent, and must remain
   --  live and unchanged throughout the call; raw-pointer readability is not
   --  proved. A null pointer denotes zero only when its length is zero.
   function Can_Reserve
     (Available_Negative : Interfaces.Unsigned_8;
      Available, Withheld, Floor, Requested : not null access constant Resources.Byte_Array)
      return Interfaces.Unsigned_8;
end Worldline.Resources_C_API;
