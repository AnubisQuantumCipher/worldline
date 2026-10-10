with Cosmogony.Capsules;
with Cosmogony.Genesis;
with System;

package body Cosmogony.Capsule_C_API with SPARK_Mode => Off is
   use type Interfaces.C.int;

   function To_Digest (D : C_Digest) return Cosmogony.Genesis.Digest is
     (1 => D (0), 2 => D (1), 3 => D (2), 4 => D (3));

   function To_Capsule (C : C_Capsule) return Cosmogony.Capsules.Capsule is
     (Capsule_Id => To_Digest (C.Capsule_Id),
      Source_Universe_Id => To_Digest (C.Source_Universe_Id),
      Source_Generation => C.Source_Generation,
      Source_Prime_Id => To_Digest (C.Source_Prime_Id),
      Source_Receipt_Id => To_Digest (C.Source_Receipt_Id),
      Candidate_Root_Id => To_Digest (C.Candidate_Root_Id),
      Mission_Id => To_Digest (C.Mission_Id),
      Policy_Id => To_Digest (C.Policy_Id),
      Policy_Epoch => C.Policy_Epoch,
      Lineage_Root_Id => To_Digest (C.Lineage_Root_Id),
      Evidence_Root_Id => To_Digest (C.Evidence_Root_Id),
      Verifier_Root_Id => To_Digest (C.Verifier_Root_Id),
      Assumptions_Id => To_Digest (C.Assumptions_Id),
      Nonclaims_Id => To_Digest (C.Nonclaims_Id));

   function To_Evaluation
     (E : C_Evaluation) return Cosmogony.Capsules.Parent_Evaluation is
     (Evaluation_Id => To_Digest (E.Evaluation_Id),
      Source => Cosmogony.Capsules.Observation_Source'Val (E.Source),
      Parent_Universe_Id => To_Digest (E.Parent_Universe_Id),
      Parent_Mission_Id => To_Digest (E.Parent_Mission_Id),
      Parent_Policy_Id => To_Digest (E.Parent_Policy_Id),
      Parent_Policy_Epoch => E.Parent_Policy_Epoch,
      Parent_Prime_Id => To_Digest (E.Parent_Prime_Id),
      Parent_Generation => E.Parent_Generation,
      Capsule_Id => To_Digest (E.Capsule_Id),
      Candidate_Root_Id => To_Digest (E.Candidate_Root_Id),
      Evidence_Root_Id => To_Digest (E.Evidence_Root_Id),
      Verifier_Root_Id => To_Digest (E.Verifier_Root_Id),
      Performed => E.Performed = 1,
      Passed => E.Passed = 1,
      Complete => E.Complete = 1);

   function ABI_Version return Interfaces.C.int is (1);
   function Capsule_Bytes return Interfaces.C.int is
     (C_Capsule'Object_Size / System.Storage_Unit);
   function Evaluation_Bytes return Interfaces.C.int is
     (C_Evaluation'Object_Size / System.Storage_Unit);

   function Stage_C
     (Parent, Child : access constant Cosmogony.Universe_C_API.C_Record;
      C : access constant C_Capsule) return Interfaces.C.int
   is
   begin
      if Parent = null or else Child = null or else C = null or else
        not Cosmogony.Universe_C_API.Canonical_C (Parent.all) or else
        not Cosmogony.Universe_C_API.Canonical_C (Child.all)
      then
         return -1;
      end if;
      return Cosmogony.Capsules.Import_Stage'Pos
        (Cosmogony.Capsules.Stage
           (Cosmogony.Universe_C_API.To_Record (Parent.all),
            Cosmogony.Universe_C_API.To_Record (Child.all),
            To_Capsule (C.all)).Stage);
   end Stage_C;

   function Judge_C
     (Parent, Child : access constant Cosmogony.Universe_C_API.C_Record;
      C : access constant C_Capsule;
      E : access constant C_Evaluation) return Interfaces.C.int
   is
   begin
      if Parent = null or else Child = null or else C = null or else E = null
        or else not Cosmogony.Universe_C_API.Canonical_C (Parent.all)
        or else not Cosmogony.Universe_C_API.Canonical_C (Child.all)
        or else E.Source not in 0 .. 2
        or else E.Performed not in 0 .. 1
        or else E.Passed not in 0 .. 1
        or else E.Complete not in 0 .. 1
      then
         return -1;
      end if;
      return Cosmogony.Capsules.Import_Stage'Pos
        (Cosmogony.Capsules.Judge
           (Cosmogony.Universe_C_API.To_Record (Parent.all),
            Cosmogony.Universe_C_API.To_Record (Child.all),
            To_Capsule (C.all), To_Evaluation (E.all)).Stage);
   end Judge_C;
end Cosmogony.Capsule_C_API;
