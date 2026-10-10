with Interfaces.C;
with Cosmogony.Hierarchy_C_API;

package Cosmogony.Resource_C_API with SPARK_Mode => Off is
   subtype C_Resources is Cosmogony.Hierarchy_C_API.C_Resources;

   --  The service owns Used and Limit. Only Extra comes from a requester.
   function Can_Add_C
     (Used, Extra, Limit : access constant C_Resources)
      return Interfaces.C.int
   with Export, Convention => C,
        External_Name => "cosmogony_resource_can_add";

   function ABI_Version return Interfaces.C.int
   with Export, Convention => C,
        External_Name => "cosmogony_resource_abi_version";
end Cosmogony.Resource_C_API;
