with Interfaces;
with Interfaces.C;
with System;
with Worldline.Resource_Policy_C_API;

--  Owned-buffer transport only. Every pointer must name aligned live storage
--  of its declared extent for this call. Address checks do not prove custody,
--  OS readability or producer truth. Mutable output extents are mutually
--  disjoint and do not alias inputs. The numeric decision is Resource_Ledger.
package Worldline.Resource_Ledger_C_API with SPARK_Mode => Off is
   subtype U8 is Interfaces.Unsigned_8;
   subtype Size is Interfaces.C.size_t;
   subtype Quantity_C is Worldline.Resource_Policy_C_API.Quantity_C;
   subtype Optional_C is Worldline.Resource_Policy_C_API.Optional_C;
   type Row_C is record
      Reserved      : Quantity_C;
      Used          : Optional_C;
      Output_First  : Size;
      Output_Length : Size;
   end record with Convention => C;
   type Result_C is record
      Status : U8;
      Total  : Quantity_C;
   end record with Convention => C;

   function ABI_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_resource_ledger_abi_version";
   function Layout_Size (Selector : U8) return Size
     with Export, Convention => C, External_Name => "wl_resource_ledger_layout_size";
   function Layout_Offset (Selector, Field : U8) return Size
     with Export, Convention => C, External_Name => "wl_resource_ledger_layout_offset";

   --  Transport 0 means a complete typed result; 255 means do not read outputs.
   --  Status order: Computed, Invalid_Input, Invalid_Output_Layout,
   --  Insufficient_Storage. Only Computed supplies a usable numeric projection.
   --  Details has Row_Count Quantity_C records. First is a one-based arena index.
   --  Absent usage is distinct from present zero; absent payload is ignored.
   function Compute
     (Data : System.Address; Data_Length : Size;
      Rows : System.Address; Row_Count : Size;
      Detail_Data : System.Address; Detail_Length : Size;
      Total_Data : System.Address; Total_Length : Size;
      Details : System.Address; Result : System.Address) return U8
     with Export, Convention => C, External_Name => "wl_resource_ledger_compute";
   --  Additive signed headroom projection with the same owned-pointer
   --  premises. Available, Withheld and Floor name Quantity_C records.
   --  Output and Result are mutually disjoint and do not alias any input.
   --  Result.Total holds the canonical headroom only when Status is Computed.
   --  A typed refusal zeros Output and returns an empty result descriptor;
   --  transport 255 still requires ignoring every output.
   function Headroom
     (Data : System.Address; Data_Length : Size;
      Available, Withheld, Floor : System.Address;
      Output : System.Address; Output_Length : Size;
      Result : System.Address) return U8
     with Export, Convention => C,
       External_Name => "wl_resource_ledger_headroom";
end Worldline.Resource_Ledger_C_API;
