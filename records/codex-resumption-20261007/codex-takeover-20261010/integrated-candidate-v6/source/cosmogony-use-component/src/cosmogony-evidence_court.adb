package body Cosmogony.Evidence_Court with SPARK_Mode => On is

   function Has_Role
     (U : Cosmogony.Genesis.Universe_State;
      Actor : Digest;
      Role : Cosmogony.Genesis.Agent_Role) return Boolean
   is
   begin
      if Actor = Zero_Digest then
         return False;
      end if;
      for I in U.Roster'Range loop
         if Natural (I) <= Natural (U.Roster_Count)
           and then U.Roster (I).Enabled
           and then U.Roster (I).Identity = Actor
           and then U.Roster (I).Role = Role
         then
            return True;
         end if;
      end loop;
      return False;
   end Has_Role;

   function Facts_Admissible
     (Facts : Fact_Array; Count : Fact_Count;
      C : Court_Context) return Boolean
   is
   begin
      if Count = 0 then
         return False;
      end if;

      for I in Facts'Range loop
         if Integer (I) <= Integer (Count) then
            declare
               F : Evidence_Fact renames Facts (I);
            begin
               if F.Evidence_Id = Zero_Digest
                 or else F.Requirement_Id /= C.Requirement_Id
                 or else F.Evaluation_Id /= C.Evaluation_Id
                 or else F.Universe_Id /= C.Universe_Id
                 or else F.World_Id /= C.World_Id
                 or else F.Candidate_Id /= C.Candidate_Id
                 or else F.Policy_Id /= C.Policy_Id
                 or else F.Policy_Epoch /= C.Policy_Epoch
                 or else F.Verifier_Id = Zero_Digest
                 or else F.Execution_Id = Zero_Digest
                 or else F.Assumptions_Id = Zero_Digest
                 or else F.Non_Claims_Id = Zero_Digest
                 or else F.Source not in Examiner | Worldline
                 or else F.Execution /= Performed
                 or else F.Result /= Pass
                 or else not F.Complete
               then
                  return False;
               end if;
               for J in Facts'Range loop
                  if J < I
                    and then Integer (J) <= Integer (Count)
                    and then
                      (Facts (J).Evidence_Id = F.Evidence_Id
                       or else Facts (J).Verifier_Id = F.Verifier_Id
                       or else Facts (J).Execution_Id = F.Execution_Id)
                  then
                     return False;
                  end if;
               end loop;
            end;
         end if;
      end loop;
      return True;
   end Facts_Admissible;

   function Adjudicate
     (U : Cosmogony.Genesis.Universe_State;
      Facts : Fact_Array; Count : Fact_Count;
      C : Court_Context) return Court_Decision
   is
   begin
      if Eligible (U, Facts, Count, C) then
         return (Kind => Admissible,
                 Effective_Evaluation_Id => C.Evaluation_Id);
      end if;
      return (Kind => Refused,
              Effective_Evaluation_Id => Zero_Digest);
   end Adjudicate;

end Cosmogony.Evidence_Court;
