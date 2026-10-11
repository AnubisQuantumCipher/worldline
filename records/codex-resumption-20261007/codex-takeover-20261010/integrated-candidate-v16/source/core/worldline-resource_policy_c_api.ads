--  Typed observer entry points retain the original complete snapshot/decoder bodies.
--  The unchanged C exports are enrolled in the existing sole Off Worldline.C_API.
--  C_API maps constrained views only after numeric transport validation; the
--  original loops below take the single snapshot before any foreign output write.
with Resource_Quantities;
with Interfaces;
with Interfaces.C;

--  ABI marshalling only. Numeric policy is in Resource_Admission (SPARK).
--  Every pointer names caller-owned, suitably aligned, readable/writable storage
--  of the declared extent, live and unchanged for the whole call. Checked address
--  arithmetic does not establish OS readability, provenance, or snapshot truth.
package Worldline.Resource_Policy_C_API with SPARK_Mode => On is
   subtype U8 is Interfaces.Unsigned_8;
   subtype Size is Interfaces.C.size_t;
   type Quantity_C is record
      First    : Size;
      Length   : Size;
      Negative : U8;
   end record with Convention => C;
   type Optional_C is record
      Present : U8;
      Value   : Quantity_C;
   end record with Convention => C;
   type Input_C is record
      Outstanding_Count      : Quantity_C;
      Concurrency_Limit      : Optional_C;
      Memory_Pressure         : Optional_C;
      Memory_Pressure_Ceiling : Quantity_C;
      Disk_Byte_Floor         : Quantity_C;
      Disk_Inode_Floor        : Quantity_C;
      Available_Memory       : Quantity_C;
      Withheld_Memory         : Quantity_C;
      Memory_Floor           : Quantity_C;
      Requested_Memory       : Quantity_C;
   end record with Convention => C;
   type Disk_C is record
      Free_Bytes  : Quantity_C;
      Free_Inodes : Quantity_C;
   end record with Convention => C;
   type Result_C is record
      Status       : U8;
      Failed_Gate  : U8;
      Field        : U8;
      Disk_Present : U8;
      Disk_Index   : Size;
   end record with Convention => C;

   type Disk_Array is array (Resource_Quantities.Byte_Index range <>) of aliased Disk_C;
   pragma Compile_Time_Error (Disk_Array'Component_Size /= Disk_C'Object_Size,
                              "owned input array stride");

   function ABI_Version return Interfaces.Unsigned_32;
   function Layout_Size (Selector : U8) return Size;
   function Layout_Offset (Selector, Field : U8) return Size;

   --  Transport returns 0 only for a complete Result, 255 on checked wire shape
   --  or caught exception. Never interpret Result after a nonzero transport code.
   --  Input/result point to their exact C records; Disks has Disk_Count records.
   --  First indexes the byte arena from 1. Empty magnitude is integer zero.
   --  Result codes are documented in worldline_core.h and independently checked
   --  by the Python decoder. Optional absent payload is ignored during decoding.
   function Admit
     (Data : not null access constant Resource_Quantities.Byte_Array;
      Input : not null access constant Input_C;
      Disks : not null access constant Disk_Array;
      Result : out Result_C) return U8
     with Side_Effects;
end Worldline.Resource_Policy_C_API;
