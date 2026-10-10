with Interfaces.C;
with Cosmogony.C_API;
with Cosmogony.Capability_C_API;
with Cosmogony.Universe_C_API;

package Cosmogony.Revocation_C_API with SPARK_Mode => Off is
   type C_Link is record
      Grant : Cosmogony.Capability_C_API.C_Capability;
      Revoked : Interfaces.C.int;
   end record with Convention => C;
   type C_Links is array (Interfaces.C.int range 0 .. 7) of C_Link
     with Convention => C;
   type C_Lineage is record
      Count : Interfaces.C.int;
      Links : C_Links;
   end record with Convention => C;

   function Check_C
     (U : access constant Cosmogony.Universe_C_API.C_Record;
      G : access constant Cosmogony.C_API.C_Universe;
      Input : access constant Cosmogony.Capability_C_API.C_Check_Input;
      Chain : access constant C_Lineage;
      D : access Cosmogony.Capability_C_API.C_Check_Decision)
      return Interfaces.C.int
     with Export, Convention => C,
          External_Name => "cosmogony_revocation_check";
   function ABI_Version return Interfaces.C.int
     with Export, Convention => C,
          External_Name => "cosmogony_revocation_abi_version";
   function Link_Bytes return Interfaces.C.int
     with Export, Convention => C,
          External_Name => "cosmogony_revocation_link_bytes";
   function Lineage_Bytes return Interfaces.C.int
     with Export, Convention => C,
          External_Name => "cosmogony_revocation_lineage_bytes";
end Cosmogony.Revocation_C_API;
