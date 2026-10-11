package body Worldline.Recovery_Authorization_V3 with SPARK_Mode is
   function Same
     (Data : Q.Byte_Array; Left, Right : Optional_Epoch) return Boolean is
   begin
      return T.Epoch_Valid (Data, Left) and then T.Epoch_Valid (Data, Right)
        and then Q.Compare (Data, Left.Value, Right.Value) = Q.Equal;
   end Same;

   function Classify_Native
     (Authorized_Binding : Binding; Observed : Native_Observation)
      return Native_State
   is
      Before : constant Boolean :=
        Same (Observed.Live_Mapping, Authorized_Binding.Before_Mapping)
        and then Same (Observed.Live_Root, Authorized_Binding.Before_Root);
      After : constant Boolean :=
        Same (Observed.Live_Mapping, Authorized_Binding.Staged_Mapping)
        and then Same (Observed.Live_Root, Authorized_Binding.Staged_Root);
   begin
      if Before and then not After then
         return Before_Effect;
      elsif After and then not Before then
         return After_Effect;
      else
         return Uncertain;
      end if;
   end Classify_Native;

   function Select_Action
     (Data : Q.Byte_Array; State : Use_State;
      Issued_Binding, Recovered_Binding : Binding;
      Fresh : Fresh_Verdict; Historical : Historical_Verdict;
      Grant_Eligible : Boolean; Native : Native_Observation)
      return Recovery_Action
   is
      Observed : constant Native_State := Classify_Native (Issued_Binding, Native);
   begin
      if not Same (Data, Issued_Binding, Recovered_Binding) then
         return Refuse;
      elsif State = Completed and then Observed = After_Effect
        and then Historical = Historically_Authorized
      then
         return Replay;
      elsif State = Claimed and then Observed = After_Effect
        and then Historical = Historically_Authorized
      then
         return Settle;
      elsif Observed = Before_Effect
        and then (State = Issued or else State = Claimed)
      then
         if Fresh = Refused or else not Grant_Eligible then
            return Abort_Use;
         elsif State = Issued then
            return Invoke_Actuator;
         else
            return Reconcile_Actuator;
         end if;
      else
         return Refuse;
      end if;
   end Select_Action;

   function Next_State
     (State : Use_State; Action : Recovery_Action) return Use_State is
     (if State = Issued and then Action = Invoke_Actuator then Claimed
      elsif State = Claimed and then Action = Settle then Completed
      elsif (State = Issued or else State = Claimed)
        and then Action = Abort_Use then Denied
      else State);
end Worldline.Recovery_Authorization_V3;
