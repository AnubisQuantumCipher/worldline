package body Worldline.Root_Custody_Replay with SPARK_Mode is
   function Resolve
     (Data : Q.Byte_Array; Events : Retained_Events; Wanted : M.Replay_Identity)
      return Replay_Result
   is
      Result : Replay_Result := (Status => No_Replay);
   begin
      if not Inputs_Valid (Data, Events, Wanted) then
         return (Status => Invalid_Operands);
      end if;
      for I in Events'Range loop
         if Matches (Data, Events (I), Wanted) then
            if Result.Status = Found then
               return (Status => Ambiguous_History);
            end if;
            Result := (Status => Found, Position => I);
         end if;
         pragma Loop_Invariant
           (Result.Status in No_Replay | Found);
         pragma Loop_Invariant
           (if Result.Status = Found then
               Result.Position in Events'First .. I and then
               Matches (Data, Events (Result.Position), Wanted) and then
               (for all J in Events'First .. I =>
                  (if J /= Result.Position then
                     not Matches (Data, Events (J), Wanted)))
            else (for all J in Events'First .. I =>
                     not Matches (Data, Events (J), Wanted)));
      end loop;
      return Result;
   end Resolve;
end Worldline.Root_Custody_Replay;
