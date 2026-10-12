with Interfaces;
with Cosmogony.Genesis;

package Cosmogony.Evidence_Court with SPARK_Mode => On is
   subtype Digest is Cosmogony.Genesis.Digest;
   Zero_Digest : Digest renames Cosmogony.Genesis.Zero_Digest;
   use type Digest;
   use type Interfaces.Unsigned_64;
   use type Cosmogony.Genesis.Agent_Role;

   type Execution_State is (Not_Performed, Performed, Interrupted, Unknown);
   type Outcome is (Pass, Fail, Inconclusive, Unknown_Outcome);
   type Observation_Source is (Candidate, Examiner, Worldline, Provider);
   type Decision_Kind is (Refused, Admissible);

   type Evidence_Fact is record
      Evidence_Id : Digest;
      Requirement_Id : Digest;
      Evaluation_Id : Digest;
      Universe_Id : Digest;
      World_Id : Digest;
      Candidate_Id : Digest;
      Policy_Id : Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Verifier_Id : Digest;
      Execution_Id : Digest;
      Source : Observation_Source;
      Execution : Execution_State;
      Result : Outcome;
      Complete : Boolean;
      Assumptions_Id : Digest;
      Non_Claims_Id : Digest;
   end record;

   type Fact_Index is range 1 .. 8;
   type Fact_Count is range 0 .. 8;
   type Fact_Array is array (Fact_Index) of Evidence_Fact;

   type Court_Context is record
      Requirement_Id : Digest;
      Evaluation_Id : Digest;
      Universe_Id : Digest;
      World_Id : Digest;
      Candidate_Id : Digest;
      Policy_Id : Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Builder_Id : Digest;
      Reviewer_Id : Digest;
      Final_Evaluator_Id : Digest;
      Sealed_Candidate_Id : Digest;
      Seal_Observed_Before_Final : Boolean;
      Campaign_Performed : Boolean;
      Attacker_Before_Id : Digest;
      Attacker_After_Id : Digest;
      Target_Commit_Id : Digest;
      Controller_Contract_Id : Digest;
      Campaign_Result_Id : Digest;
   end record;

   type Court_Decision is record
      Kind : Decision_Kind;
      Effective_Evaluation_Id : Digest;
   end record;

   function Has_Role
     (U : Cosmogony.Genesis.Universe_State;
      Actor : Digest;
      Role : Cosmogony.Genesis.Agent_Role) return Boolean;

   function Independent_Roles
     (U : Cosmogony.Genesis.Universe_State;
      C : Court_Context) return Boolean is
     (C.Builder_Id /= Zero_Digest
      and then C.Reviewer_Id /= Zero_Digest
      and then C.Final_Evaluator_Id /= Zero_Digest
      and then C.Builder_Id /= C.Reviewer_Id
      and then C.Builder_Id /= C.Final_Evaluator_Id
      and then C.Reviewer_Id /= C.Final_Evaluator_Id
      and then Has_Role (U, C.Builder_Id, Cosmogony.Genesis.Builder)
      and then Has_Role (U, C.Reviewer_Id, Cosmogony.Genesis.Reviewer)
      and then Has_Role
        (U, C.Final_Evaluator_Id, Cosmogony.Genesis.Held_Out_Evaluator));

   function Bound_Context
     (U : Cosmogony.Genesis.Universe_State;
      C : Court_Context) return Boolean is
     (Cosmogony.Genesis.Valid_Genesis (U)
      and then C.Requirement_Id /= Zero_Digest
      and then C.Evaluation_Id /= Zero_Digest
      and then C.World_Id /= Zero_Digest
      and then C.Candidate_Id /= Zero_Digest
      and then C.Universe_Id = U.Universe_Id
      and then C.Policy_Id = U.Policy_Id
      and then C.Policy_Epoch = U.Policy_Epoch
      and then C.Sealed_Candidate_Id = C.Candidate_Id
      and then C.Seal_Observed_Before_Final
      and then Independent_Roles (U, C));

   function Campaign_Intact (C : Court_Context) return Boolean is
     (C.Campaign_Performed
      and then C.Attacker_Before_Id /= Zero_Digest
      and then C.Attacker_Before_Id = C.Attacker_After_Id
      and then C.Target_Commit_Id /= Zero_Digest
      and then C.Controller_Contract_Id /= Zero_Digest
      and then C.Campaign_Result_Id /= Zero_Digest);

   function Facts_Admissible
     (Facts : Fact_Array; Count : Fact_Count;
      C : Court_Context) return Boolean;

   function Eligible
     (U : Cosmogony.Genesis.Universe_State;
      Facts : Fact_Array; Count : Fact_Count;
      C : Court_Context) return Boolean is
     (Bound_Context (U, C)
      and then Campaign_Intact (C)
      and then Facts_Admissible (Facts, Count, C));

   function Adjudicate
     (U : Cosmogony.Genesis.Universe_State;
      Facts : Fact_Array; Count : Fact_Count;
      C : Court_Context) return Court_Decision
   with Post =>
     (Adjudicate'Result.Kind = Admissible) = Eligible (U, Facts, Count, C)
     and then
       (if Adjudicate'Result.Kind = Admissible then
          Adjudicate'Result.Effective_Evaluation_Id = C.Evaluation_Id
        else Adjudicate'Result.Effective_Evaluation_Id = Zero_Digest);

end Cosmogony.Evidence_Court;
