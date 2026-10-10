with Interfaces;
with Interfaces.C;
with Cosmogony.C_API;
with Cosmogony.Universe_C_API;

package Cosmogony.Capsule_C_API with SPARK_Mode => Off is
   subtype C_Digest is Cosmogony.C_API.C_Digest;
   type C_Capsule is record
      Capsule_Id, Source_Universe_Id : C_Digest;
      Source_Generation : Interfaces.Unsigned_64;
      Source_Prime_Id, Source_Receipt_Id, Candidate_Root_Id,
        Mission_Id, Policy_Id : C_Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Lineage_Root_Id, Evidence_Root_Id, Verifier_Root_Id,
        Assumptions_Id, Nonclaims_Id : C_Digest;
   end record with Convention => C;
   type C_Evaluation is record
      Evaluation_Id : C_Digest;
      Source : Interfaces.C.int;
      Parent_Universe_Id, Parent_Mission_Id, Parent_Policy_Id : C_Digest;
      Parent_Policy_Epoch : Interfaces.Unsigned_64;
      Parent_Prime_Id : C_Digest;
      Parent_Generation : Interfaces.Unsigned_64;
      Capsule_Id, Candidate_Root_Id, Evidence_Root_Id,
        Verifier_Root_Id : C_Digest;
      Performed, Passed, Complete : Interfaces.C.int;
   end record with Convention => C;

   function ABI_Version return Interfaces.C.int with
     Export, Convention => C, External_Name => "cosmogony_capsule_abi_version";
   function Capsule_Bytes return Interfaces.C.int with
     Export, Convention => C, External_Name => "cosmogony_capsule_bytes";
   function Evaluation_Bytes return Interfaces.C.int with
     Export, Convention => C, External_Name => "cosmogony_capsule_evaluation_bytes";
   --  Return -1 for malformed boundary values; otherwise return the
   --  Import_Stage ordinal (Refused, Candidate_Only, Eligible_For_Worldline).
   function Stage_C
     (Parent, Child : access constant Cosmogony.Universe_C_API.C_Record;
      C : access constant C_Capsule) return Interfaces.C.int with
     Export, Convention => C, External_Name => "cosmogony_capsule_stage";
   function Judge_C
     (Parent, Child : access constant Cosmogony.Universe_C_API.C_Record;
      C : access constant C_Capsule;
      E : access constant C_Evaluation) return Interfaces.C.int with
     Export, Convention => C, External_Name => "cosmogony_capsule_judge";
end Cosmogony.Capsule_C_API;
