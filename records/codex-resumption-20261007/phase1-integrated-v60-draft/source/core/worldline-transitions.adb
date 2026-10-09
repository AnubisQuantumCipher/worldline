package body Worldline.Transitions with SPARK_Mode is

   function Allowed (From_State, To_State : World_State) return Boolean is
   begin
      case From_State is
         when Mutable =>
            return To_State in Finalizing | Dead;
         when Finalizing =>
            return To_State in Valid | Degraded | Dead;
         when Valid =>
            return To_State in Collapsed | Archived;
         when Degraded =>
            return To_State in Dead | Archived;
         when Dead | Collapsed =>
            return To_State = Archived;
         when Archived =>
            return False;
      end case;
   end Allowed;

   function Transaction_Allowed
     (From_State, To_State : Transaction_State) return Boolean
   is
   begin
      case From_State is
         when Prepared =>
            return To_State in Authorized | Denied | Aborted;
         when Authorized =>
            return To_State in Committed | Aborted;
         when Denied =>
            return To_State = Aborted;
         when Committed | Aborted =>
            return False;
      end case;
   end Transaction_Allowed;

   procedure Advance
     (State     : in out Transaction_State;
      Requested : Transaction_State)
   is
   begin
      if Transaction_Allowed (State, Requested) then
         State := Requested;
      end if;
   end Advance;

end Worldline.Transitions;
