with Interfaces;
with Interfaces.C;
with Cosmogony.C_API;
with Cosmogony.Universe_C_API;
with Cosmogony.Capability_C_API;

package Cosmogony.Hierarchy_C_API with SPARK_Mode => Off is
   type C_Resources is record
      Worlds : Interfaces.Unsigned_32;
      Evaluations : Interfaces.Unsigned_32;
      Memory_MiB : Interfaces.Unsigned_32;
      Threads : Interfaces.Unsigned_32;
   end record with Convention => C;
   type C_Allocation is record
      Child_Id : Cosmogony.C_API.C_Digest;
      Grant : C_Resources;
   end record with Convention => C;
   type C_Allocation_Table is array (Interfaces.C.int range 0 .. 7)
     of C_Allocation with Convention => C;
   type C_Hierarchy is record
      Universe : Cosmogony.Universe_C_API.C_Record;
      Limit : C_Resources;
      Local_Reserved : C_Resources;
      Child_Allocated : C_Resources;
      Count : Interfaces.C.int;
      Allocations : C_Allocation_Table;
   end record with Convention => C;
   type C_Create_Input is record
      Parent_State : C_Hierarchy;
      Parent_Genesis : Cosmogony.C_API.C_Universe;
      Child_Universe : Cosmogony.Universe_C_API.C_Record;
      Child_Genesis : Cosmogony.C_API.C_Universe;
      Parent_Capability : Cosmogony.Capability_C_API.C_Capability;
      Child_Capability : Cosmogony.Capability_C_API.C_Capability;
      Grant : C_Resources;
      Caller_Id : Cosmogony.C_API.C_Digest;
      Now_Tick : Interfaces.Unsigned_64;
   end record with Convention => C;
   type C_Create_Output is record
      Created : Interfaces.C.int;
      Parent_State : C_Hierarchy;
      Child_State : C_Hierarchy;
      Child_Capability : Cosmogony.Capability_C_API.C_Capability;
   end record with Convention => C;

   function Create_C
     (Input : access constant C_Create_Input;
      Output : access C_Create_Output) return Interfaces.C.int
     with Export, Convention => C,
          External_Name => "cosmogony_hierarchy_create";
   function Valid_C
     (H : access constant C_Hierarchy) return Interfaces.C.int
     with Export, Convention => C,
          External_Name => "cosmogony_hierarchy_valid";
   function Parent_Ready_C
     (Parent : access constant Cosmogony.Universe_C_API.C_Record)
      return Interfaces.C.int
     with Export, Convention => C,
          External_Name => "cosmogony_hierarchy_parent_ready";
   function ABI_Version return Interfaces.C.int
     with Export, Convention => C,
          External_Name => "cosmogony_hierarchy_abi_version";
end Cosmogony.Hierarchy_C_API;
