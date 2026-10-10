with Interfaces;
with Interfaces.C;
with Cosmogony.C_API;
with Cosmogony.Capabilities;

package Cosmogony.Capability_C_API with SPARK_Mode => Off is
   use Cosmogony.C_API;
   type C_Action_Set is array (Interfaces.C.int range 0 .. 7)
     of Interfaces.C.int with Convention => C;
   type C_Scope is record
      Kind : Interfaces.C.int;
      World_Id : C_Digest;
   end record with Convention => C;
   type C_Ceiling is record
      Worlds : Interfaces.Unsigned_32;
      Evaluations : Interfaces.Unsigned_32;
   end record with Convention => C;
   type C_Usage is record
      Worlds : Interfaces.Unsigned_32;
      Evaluations : Interfaces.Unsigned_32;
   end record with Convention => C;
   type C_Capability is record
      Capability_Id : C_Digest;
      Parent_Id : C_Digest;
      Universe_Id : C_Digest;
      Mission_Id : C_Digest;
      Policy_Id : C_Digest;
      Authority_Id : C_Digest;
      Worldline_Instance_Id : C_Digest;
      Root_Set_Id : C_Digest;
      Prime_Id : C_Digest;
      Subject_Id : C_Digest;
      Issuer_Id : C_Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Issued_At : Interfaces.Unsigned_64;
      Expires_At : Interfaces.Unsigned_64;
      Terminal : Interfaces.C.int;
      Granted : C_Action_Set;
      Applies_To : C_Scope;
      Ceiling : C_Ceiling;
   end record with Convention => C;
   type C_Check_Input is record
      Authority_Id : C_Digest;
      Grant : C_Capability;
      Ask : C_Request;
      Target_World_Id : C_Digest;
      Usage : C_Usage;
      Now_Tick : Interfaces.Unsigned_64;
   end record with Convention => C;
   type C_Check_Decision is record
      Kind : Interfaces.C.int;
      Reason : Interfaces.C.int;
   end record with Convention => C;

   function Canonical_C (C : C_Capability) return Boolean;
   function To_Capability
     (C : C_Capability) return Cosmogony.Capabilities.Capability;
   function From_Capability
     (C : Cosmogony.Capabilities.Capability) return C_Capability;

   function Check_C
     (U : access constant C_Universe;
      Input : access constant C_Check_Input;
      D : access C_Check_Decision) return Interfaces.C.int
     with Export, Convention => C,
          External_Name => "cosmogony_capability_check";
   function ABI_Version return Interfaces.C.int
     with Export, Convention => C,
          External_Name => "cosmogony_capability_abi_version";
end Cosmogony.Capability_C_API;
