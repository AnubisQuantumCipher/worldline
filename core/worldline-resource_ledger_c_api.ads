--  Typed observer entry points retain the original complete snapshot/decoder bodies.
--  The unchanged C exports are enrolled in the existing sole Off Worldline.C_API.
--  C_API maps constrained views only after numeric transport validation; the
--  original loops below take the single snapshot before any foreign output write.
with Resource_Quantities;
with Resource_Ledger;
with Interfaces;
with Interfaces.C;
with Worldline.Resource_Policy_C_API;

--  Owned-buffer transport only. Every pointer must name aligned live storage
--  of its declared extent for this call. Address checks do not prove custody,
--  OS readability or producer truth. Mutable output extents are mutually
--  disjoint and do not alias inputs. The numeric decision is Resource_Ledger.
package Worldline.Resource_Ledger_C_API with SPARK_Mode => On is
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

   type Row_Array is array (Resource_Quantities.Byte_Index range <>) of aliased Row_C;
   pragma Compile_Time_Error (Row_Array'Component_Size /= Row_C'Object_Size,
                              "owned input array stride");

   function Encode (V : Resource_Quantities.Quantity) return Quantity_C;

   function ABI_Version return Interfaces.Unsigned_32;
   function Layout_Size (Selector : U8) return Size;
   function Layout_Offset (Selector, Field : U8) return Size;

   --  Transport 0 means a complete typed result; 255 means do not read outputs.
   --  Status order: Computed, Invalid_Input, Invalid_Output_Layout,
   --  Insufficient_Storage. Only Computed supplies a usable numeric projection.
   --  Details has Row_Count Quantity_C records. First is a one-based arena index.
   --  Absent usage is distinct from present zero; absent payload is ignored.
   function Compute
     (Data : not null access constant Resource_Quantities.Byte_Array;
      Rows : not null access constant Row_Array;
      Detail_Arena, Total_Arena : out Resource_Quantities.Byte_Array;
      Typed_Details : out Resource_Ledger.Quantity_Array;
      Total : out Resource_Quantities.Quantity;
      Status : out Resource_Ledger.Result_Status) return U8
     with Side_Effects;
   --  Additive signed headroom projection with the same owned-pointer
   --  premises. Available, Withheld and Floor name Quantity_C records.
   --  Output and Result are mutually disjoint and do not alias any input.
   --  Result.Total holds the canonical headroom only when Status is Computed.
   --  A typed refusal zeros Output and returns an empty result descriptor;
   --  transport 255 still requires ignoring every output.
   function Headroom
     (Data : not null access constant Resource_Quantities.Byte_Array;
      Available, Withheld, Floor : not null access constant Quantity_C;
      Output_Arena : out Resource_Quantities.Byte_Array;
      Typed_Result : out Resource_Quantities.Quantity;
      Status : out Resource_Ledger.Result_Status) return U8
     with Side_Effects;
end Worldline.Resource_Ledger_C_API;
