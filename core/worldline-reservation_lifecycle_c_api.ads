with Interfaces;
with Interfaces.C;
with System;

--  Owned-buffer transport. Inputs must name aligned, readable, live and
--  unchanged storage for their entire declared extents. Output is disjoint
--  writable live storage, not aliased with any input. These custody premises
--  are not established by address arithmetic or the SPARK plan.
package Worldline.Reservation_Lifecycle_C_API with SPARK_Mode => Off is
   subtype U8 is Interfaces.Unsigned_8;
   subtype Size is Interfaces.C.size_t;
   type Row_C is record
      First : Size;
      Length : Size;
      Observed : U8;
   end record with Convention => C;

   function ABI_Version return Interfaces.Unsigned_32
     with Export, Convention => C,
       External_Name => "wl_reservation_lifecycle_abi_version";
   function Layout_Size return Size
     with Export, Convention => C,
       External_Name => "wl_reservation_lifecycle_row_size";
   function Layout_Offset (Field : U8) return Size
     with Export, Convention => C,
       External_Name => "wl_reservation_lifecycle_row_offset";

   --  Mode 1 = exact release; 2 = observed reconciliation. Observation values
   --  are 0 unknown, 1 live, 2 gone. Present is a real Boolean; absent identity
   --  ignores its First/Length fields. Empty present identity remains distinct.
   --  Return: 0 invalid input, 1 invalid layout, 2 no change, 3 removal planned.
   --  Typed refusal leaves every output byte unchanged. Transport 255 requires
   --  ignoring outputs. No raw pointer safety proof is claimed.
   function Plan
     (Data : System.Address; Data_Length : Size;
      Rows : System.Address; Row_Count : Size;
      Mode, Present : U8; Requested_First, Requested_Length : Size;
      Removed : System.Address; Removed_Length : Size) return U8
     with Export, Convention => C,
       External_Name => "wl_reservation_lifecycle_plan";
end Worldline.Reservation_Lifecycle_C_API;
