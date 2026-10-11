with Cosmogony.Genesis;

package body Cosmogony.Evidence_Court_C_API with SPARK_Mode => Off is
   use Cosmogony.Evidence_Court;
   use type Interfaces.C.int;

   function To_Digest (Value : C_Digest) return Digest is
     (1 => Value (0), 2 => Value (1), 3 => Value (2), 4 => Value (3));

   function From_Digest (Value : Digest) return C_Digest is
     (0 => Value (1), 1 => Value (2), 2 => Value (3), 3 => Value (4));

   function Canonical_Facts
     (Facts : C_Facts; Count : Interfaces.C.int) return Boolean
   is
   begin
      if Count < 0 or else Count > 8 then
         return False;
      end if;
      for I in Facts'Range loop
         if I < Count
           and then
             (Facts (I).Source < 0
              or else Facts (I).Source > Observation_Source'Pos
                (Observation_Source'Last)
              or else Facts (I).Execution < 0
              or else Facts (I).Execution > Execution_State'Pos
                (Execution_State'Last)
              or else Facts (I).Result < 0
              or else Facts (I).Result > Outcome'Pos (Outcome'Last)
              or else Facts (I).Complete not in 0 .. 1)
         then
            return False;
         end if;
      end loop;
      return True;
   end Canonical_Facts;

   function Canonical_Context (Context : C_Context) return Boolean is
     (Context.Seal_Observed_Before_Final in 0 .. 1
      and then Context.Campaign_Performed in 0 .. 1);

   function To_Fact (Fact : C_Fact) return Evidence_Fact is
     (Evidence_Id => To_Digest (Fact.Evidence_Id),
      Requirement_Id => To_Digest (Fact.Requirement_Id),
      Evaluation_Id => To_Digest (Fact.Evaluation_Id),
      Universe_Id => To_Digest (Fact.Universe_Id),
      World_Id => To_Digest (Fact.World_Id),
      Candidate_Id => To_Digest (Fact.Candidate_Id),
      Policy_Id => To_Digest (Fact.Policy_Id),
      Policy_Epoch => Fact.Policy_Epoch,
      Verifier_Id => To_Digest (Fact.Verifier_Id),
      Execution_Id => To_Digest (Fact.Execution_Id),
      Source => Observation_Source'Val (Fact.Source),
      Execution => Execution_State'Val (Fact.Execution),
      Result => Outcome'Val (Fact.Result),
      Complete => Fact.Complete = 1,
      Assumptions_Id => To_Digest (Fact.Assumptions_Id),
      Non_Claims_Id => To_Digest (Fact.Non_Claims_Id));

   function To_Context (Context : C_Context) return Court_Context is
     (Requirement_Id => To_Digest (Context.Requirement_Id),
      Evaluation_Id => To_Digest (Context.Evaluation_Id),
      Universe_Id => To_Digest (Context.Universe_Id),
      World_Id => To_Digest (Context.World_Id),
      Candidate_Id => To_Digest (Context.Candidate_Id),
      Policy_Id => To_Digest (Context.Policy_Id),
      Policy_Epoch => Context.Policy_Epoch,
      Builder_Id => To_Digest (Context.Builder_Id),
      Reviewer_Id => To_Digest (Context.Reviewer_Id),
      Final_Evaluator_Id => To_Digest (Context.Final_Evaluator_Id),
      Sealed_Candidate_Id => To_Digest (Context.Sealed_Candidate_Id),
      Seal_Observed_Before_Final => Context.Seal_Observed_Before_Final = 1,
      Campaign_Performed => Context.Campaign_Performed = 1,
      Attacker_Before_Id => To_Digest (Context.Attacker_Before_Id),
      Attacker_After_Id => To_Digest (Context.Attacker_After_Id),
      Target_Commit_Id => To_Digest (Context.Target_Commit_Id),
      Controller_Contract_Id => To_Digest (Context.Controller_Contract_Id),
      Campaign_Result_Id => To_Digest (Context.Campaign_Result_Id));

   function ABI_Version return Interfaces.C.int is (1);

   function Adjudicate_C
     (Universe : access constant C_Universe;
      Facts : access constant C_Facts;
      Count : Interfaces.C.int;
      Context : access constant C_Context;
      Decision : access C_Decision) return Interfaces.C.int
   is
      Native_Facts : Fact_Array;
      Empty_Fact : constant Evidence_Fact :=
        (Evidence_Id => Zero_Digest,
         Requirement_Id => Zero_Digest,
         Evaluation_Id => Zero_Digest,
         Universe_Id => Zero_Digest,
         World_Id => Zero_Digest,
         Candidate_Id => Zero_Digest,
         Policy_Id => Zero_Digest,
         Policy_Epoch => 0,
         Verifier_Id => Zero_Digest,
         Execution_Id => Zero_Digest,
         Source => Candidate,
         Execution => Not_Performed,
         Result => Unknown_Outcome,
         Complete => False,
         Assumptions_Id => Zero_Digest,
         Non_Claims_Id => Zero_Digest);
      Result : Court_Decision;
   begin
      if Decision = null then
         return -1;
      end if;
      Decision.all := (Kind => Decision_Kind'Pos (Refused),
                       Effective_Evaluation_Id => (others => 0));
      if Universe = null or else Facts = null or else Context = null then
         return -1;
      end if;
      if not Cosmogony.C_API.Canonical_U (Universe.all)
        or else not Canonical_Facts (Facts.all, Count)
        or else not Canonical_Context (Context.all)
      then
         return -1;
      end if;
      Native_Facts := (others => Empty_Fact);
      for I in 0 .. Count - 1 loop
         Native_Facts (Fact_Index (I + 1)) := To_Fact (Facts (I));
      end loop;
      Result := Adjudicate
        (Cosmogony.C_API.To_State (Universe.all),
         Native_Facts, Fact_Count (Count), To_Context (Context.all));
      Decision.all :=
        (Kind => Decision_Kind'Pos (Result.Kind),
         Effective_Evaluation_Id =>
           From_Digest (Result.Effective_Evaluation_Id));
      return 0;
   end Adjudicate_C;
end Cosmogony.Evidence_Court_C_API;
