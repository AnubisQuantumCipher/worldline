with Interfaces;
with Cosmogony.Genesis;
with Cosmogony.Universes;

package Cosmogony.Capsules with SPARK_Mode => On is
   subtype Digest is Cosmogony.Genesis.Digest;
   Zero_Digest : Digest renames Cosmogony.Genesis.Zero_Digest;
   use type Digest;
   use type Interfaces.Unsigned_64;
   use type Cosmogony.Universes.Lifecycle_State;

   --  These are value bindings. Authenticity of records, digests, candidate
   --  bytes, and WORLDLINE evaluation receipts belongs to a protected boundary.
   type Capsule is record
      Capsule_Id : Digest;
      Source_Universe_Id : Digest;
      Source_Generation : Interfaces.Unsigned_64;
      Source_Prime_Id : Digest;
      Source_Receipt_Id : Digest;
      Candidate_Root_Id : Digest;
      Mission_Id : Digest;
      Policy_Id : Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Lineage_Root_Id : Digest;
      Evidence_Root_Id : Digest;
      Verifier_Root_Id : Digest;
      Assumptions_Id : Digest;
      Nonclaims_Id : Digest;
   end record;

   type Observation_Source is (Unspecified, Child_Evidence,
                               Parent_Worldline);
   type Parent_Evaluation is record
      Evaluation_Id : Digest;
      Source : Observation_Source;
      Parent_Universe_Id : Digest;
      Parent_Mission_Id : Digest;
      Parent_Policy_Id : Digest;
      Parent_Policy_Epoch : Interfaces.Unsigned_64;
      Parent_Prime_Id : Digest;
      Parent_Generation : Interfaces.Unsigned_64;
      Capsule_Id : Digest;
      Candidate_Root_Id : Digest;
      Evidence_Root_Id : Digest;
      Verifier_Root_Id : Digest;
      Performed : Boolean;
      Passed : Boolean;
      Complete : Boolean;
   end record;

   type Import_Stage is (Refused, Candidate_Only,
                         Eligible_For_Worldline);
   type Import_Decision is record
      Stage : Import_Stage;
   end record;

   function Source_Ready (Child : Cosmogony.Universes.Universe_Record)
     return Boolean is
     (Cosmogony.Universes.Valid (Child)
      and then Child.Life in Cosmogony.Universes.Active |
                             Cosmogony.Universes.Sealed
      and then Cosmogony.Universes.Quiet (Child)
      and then Cosmogony.Universes.Snapshot_Ready (Child));

   function Capsule_Binds_Source
     (C : Capsule; Child : Cosmogony.Universes.Universe_Record)
      return Boolean is
     (C.Capsule_Id /= Zero_Digest
      and then C.Source_Universe_Id = Child.Universe_Id
      and then C.Source_Generation = Child.Prime_Generation
      and then C.Source_Prime_Id = Child.Prime_Id
      and then C.Source_Receipt_Id = Child.Receipt_Head_Id
      and then C.Candidate_Root_Id /= Zero_Digest
      and then C.Mission_Id = Child.Policy.Mission_Id
      and then C.Policy_Id = Child.Policy.Authority_Id
      and then C.Policy_Epoch = Child.Policy_Epoch
      and then C.Lineage_Root_Id /= Zero_Digest
      and then C.Evidence_Root_Id = Child.Evidence_Snapshot_Id
      and then C.Verifier_Root_Id /= Zero_Digest
      and then C.Assumptions_Id /= Zero_Digest
      and then C.Nonclaims_Id /= Zero_Digest);

   function Can_Stage
     (Parent, Child : Cosmogony.Universes.Universe_Record;
      C : Capsule) return Boolean is
     (Cosmogony.Universes.Valid (Parent)
      and then Parent.Life = Cosmogony.Universes.Active
      and then Source_Ready (Child)
      and then Child.Parent_Id = Parent.Universe_Id
      and then Child.Universe_Id /= Parent.Universe_Id
      and then Capsule_Binds_Source (C, Child));

   --  A source-universe report, even a passing one, cannot serve as the
   --  parent's evaluation. The parent must observe the same candidate after
   --  import under its own current mission, policy epoch, and PRIME.
   function Evaluation_Binds_Parent
     (Parent : Cosmogony.Universes.Universe_Record;
      C : Capsule; E : Parent_Evaluation) return Boolean is
     (E.Evaluation_Id /= Zero_Digest
      and then E.Evaluation_Id /= C.Capsule_Id
      and then E.Source = Parent_Worldline
      and then E.Parent_Universe_Id = Parent.Universe_Id
      and then E.Parent_Mission_Id = Parent.Policy.Mission_Id
      and then E.Parent_Policy_Id = Parent.Policy.Authority_Id
      and then E.Parent_Policy_Epoch = Parent.Policy_Epoch
      and then E.Parent_Prime_Id = Parent.Prime_Id
      and then E.Parent_Generation = Parent.Prime_Generation
      and then E.Capsule_Id = C.Capsule_Id
      and then E.Candidate_Root_Id = C.Candidate_Root_Id
      and then E.Evidence_Root_Id /= Zero_Digest
      and then E.Evidence_Root_Id /= C.Evidence_Root_Id
      and then E.Verifier_Root_Id /= Zero_Digest
      and then E.Performed and then E.Passed and then E.Complete);

   function Can_Forward
     (Parent, Child : Cosmogony.Universes.Universe_Record;
      C : Capsule; E : Parent_Evaluation) return Boolean is
     (Can_Stage (Parent, Child, C)
      and then Evaluation_Binds_Parent (Parent, C, E));

   function Stage
     (Parent, Child : Cosmogony.Universes.Universe_Record;
      C : Capsule) return Import_Decision
   with Post =>
     ((Stage'Result.Stage = Candidate_Only) = Can_Stage (Parent, Child, C))
     and then Stage'Result.Stage /= Eligible_For_Worldline;

   function Judge
     (Parent, Child : Cosmogony.Universes.Universe_Record;
      C : Capsule; E : Parent_Evaluation) return Import_Decision
   with Post =>
     ((Judge'Result.Stage = Eligible_For_Worldline) =
        Can_Forward (Parent, Child, C, E))
     and then
       ((Judge'Result.Stage = Candidate_Only) =
         (Can_Stage (Parent, Child, C)
          and then not Evaluation_Binds_Parent (Parent, C, E)));
end Cosmogony.Capsules;
