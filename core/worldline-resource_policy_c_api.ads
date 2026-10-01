with Interfaces;
with Interfaces.C;
with System;

--  ABI marshalling only. Numeric policy is in Resource_Admission (SPARK).
--  Every pointer names caller-owned, suitably aligned, readable/writable storage
--  of the declared extent, live and unchanged for the whole call. Checked address
--  arithmetic does not establish OS readability, provenance, or snapshot truth.
package Worldline.Resource_Policy_C_API with SPARK_Mode => Off is
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

   function ABI_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_resource_policy_abi_version";
   function Layout_Size (Selector : U8) return Size
     with Export, Convention => C, External_Name => "wl_resource_policy_layout_size";
   function Layout_Offset (Selector, Field : U8) return Size
     with Export, Convention => C, External_Name => "wl_resource_policy_layout_offset";

   --  Transport returns 0 only for a complete Result, 255 on checked wire shape
   --  or caught exception. Never interpret Result after a nonzero transport code.
   --  Input/result point to their exact C records; Disks has Disk_Count records.
   --  First indexes the byte arena from 1. Empty magnitude is integer zero.
   --  Result codes are documented in worldline_core.h and independently checked
   --  by the Python decoder. Optional absent payload is ignored during decoding.
   function Admit
     (Data : System.Address; Data_Length : Size;
      Input : System.Address; Disks : System.Address; Disk_Count : Size;
      Result : System.Address) return U8
     with Export, Convention => C, External_Name => "wl_resource_policy_admit";
end Worldline.Resource_Policy_C_API;
