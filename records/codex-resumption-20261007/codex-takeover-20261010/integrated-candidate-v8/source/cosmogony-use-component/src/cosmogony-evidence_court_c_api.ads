with Interfaces;
with Interfaces.C;
with Cosmogony.C_API;
with Cosmogony.Evidence_Court;

package Cosmogony.Evidence_Court_C_API with SPARK_Mode => Off is
   --  This is an unproved, exact-value ABI to the proved court decision.
   --  Caller storage must be accessible and aligned; malformed codes refuse.
   subtype C_Digest is Cosmogony.C_API.C_Digest;
   subtype C_Universe is Cosmogony.C_API.C_Universe;

   type C_Fact is record
      Evidence_Id : C_Digest;
      Requirement_Id : C_Digest;
      Evaluation_Id : C_Digest;
      Universe_Id : C_Digest;
      World_Id : C_Digest;
      Candidate_Id : C_Digest;
      Policy_Id : C_Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Verifier_Id : C_Digest;
      Execution_Id : C_Digest;
      Source : Interfaces.C.int;
      Execution : Interfaces.C.int;
      Result : Interfaces.C.int;
      Complete : Interfaces.C.int;
      Assumptions_Id : C_Digest;
      Non_Claims_Id : C_Digest;
   end record with Convention => C;
   type C_Facts is array (Interfaces.C.int range 0 .. 7) of C_Fact
     with Convention => C;

   type C_Context is record
      Requirement_Id : C_Digest;
      Evaluation_Id : C_Digest;
      Universe_Id : C_Digest;
      World_Id : C_Digest;
      Candidate_Id : C_Digest;
      Policy_Id : C_Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Builder_Id : C_Digest;
      Reviewer_Id : C_Digest;
      Final_Evaluator_Id : C_Digest;
      Sealed_Candidate_Id : C_Digest;
      Seal_Observed_Before_Final : Interfaces.C.int;
      Campaign_Performed : Interfaces.C.int;
      Attacker_Before_Id : C_Digest;
      Attacker_After_Id : C_Digest;
      Target_Commit_Id : C_Digest;
      Controller_Contract_Id : C_Digest;
      Campaign_Result_Id : C_Digest;
   end record with Convention => C;

   type C_Decision is record
      Kind : Interfaces.C.int;
      Effective_Evaluation_Id : C_Digest;
   end record with Convention => C;

   function Canonical_Facts (Facts : C_Facts; Count : Interfaces.C.int)
     return Boolean;
   function Canonical_Context (Context : C_Context) return Boolean;
   function To_Fact (Fact : C_Fact)
     return Cosmogony.Evidence_Court.Evidence_Fact;
   function To_Context (Context : C_Context)
     return Cosmogony.Evidence_Court.Court_Context;

   function Adjudicate_C
     (Universe : access constant C_Universe;
      Facts : access constant C_Facts;
      Count : Interfaces.C.int;
      Context : access constant C_Context;
      Decision : access C_Decision) return Interfaces.C.int
     with Export, Convention => C,
          External_Name => "cosmogony_evidence_court_adjudicate";
   function ABI_Version return Interfaces.C.int
     with Export, Convention => C,
          External_Name => "cosmogony_evidence_court_abi_version";
end Cosmogony.Evidence_Court_C_API;
