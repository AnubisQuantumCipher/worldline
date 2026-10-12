package body Cosmogony.Capsules with SPARK_Mode => On is

   function Stage
     (Parent, Child : Cosmogony.Universes.Universe_Record;
      C : Capsule) return Import_Decision is
   begin
      if Can_Stage (Parent, Child, C) then
         return (Stage => Candidate_Only);
      else
         return (Stage => Refused);
      end if;
   end Stage;

   function Judge
     (Parent, Child : Cosmogony.Universes.Universe_Record;
      C : Capsule; E : Parent_Evaluation) return Import_Decision is
   begin
      if not Can_Stage (Parent, Child, C) then
         return (Stage => Refused);
      elsif Evaluation_Binds_Parent (Parent, C, E) then
         return (Stage => Eligible_For_Worldline);
      else
         return (Stage => Candidate_Only);
      end if;
   end Judge;

end Cosmogony.Capsules;
