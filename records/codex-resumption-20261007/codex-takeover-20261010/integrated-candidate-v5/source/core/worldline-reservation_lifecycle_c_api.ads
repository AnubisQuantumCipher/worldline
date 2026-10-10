--  Typed observer entry points retain the original complete snapshot/decoder bodies.
--  The unchanged C exports are enrolled in the existing sole Off Worldline.C_API.
--  C_API maps constrained views only after numeric transport validation; the
--  original loops below take the single snapshot before any foreign output write.
with Worldline.Resources;
with Resource_Reservation_Lifecycle;
with Interfaces;
with Interfaces.C;

--  Owned-buffer transport. Inputs must name aligned, readable, live and
--  unchanged storage for their entire declared extents. Output is disjoint
--  writable live storage, not aliased with any input. These custody premises
--  are not established by address arithmetic or the SPARK plan.
package Worldline.Reservation_Lifecycle_C_API with SPARK_Mode => On is
   subtype U8 is Interfaces.Unsigned_8;
   subtype Size is Interfaces.C.size_t;
   type Row_C is record
      First : Size;
      Length : Size;
      Observed : U8;
   end record with Convention => C;

   type Row_Array is array (Worldline.Resources.Byte_Index range <>) of aliased Row_C;
   pragma Compile_Time_Error (Row_Array'Component_Size /= Row_C'Object_Size,
                              "owned input array stride");

   function ABI_Version return Interfaces.Unsigned_32;
   function Layout_Size return Size;
   function Layout_Offset (Field : U8) return Size;

   --  Mode 1 = exact release; 2 = observed reconciliation. Observation values
   --  are 0 unknown, 1 live, 2 gone. Present is a real Boolean; absent identity
   --  ignores its First/Length fields. Empty present identity remains distinct.
   --  Return: 0 invalid input, 1 invalid layout, 2 no change, 3 removal planned.
   --  Typed refusal leaves every output byte unchanged. Transport 255 requires
   --  ignoring outputs. No raw pointer safety proof is claimed.
   function Plan
     (Data : not null access constant Worldline.Resources.Byte_Array;
      Rows : not null access constant Row_Array;
      Mode, Present : U8; Requested_First, Requested_Length : Size;
      Mask : out Resource_Reservation_Lifecycle.Removal_Array) return U8
     with Side_Effects;
end Worldline.Reservation_Lifecycle_C_API;
