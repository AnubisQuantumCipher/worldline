package Worldline.Transitions with SPARK_Mode is

   type World_State is
     (Mutable, Finalizing, Valid, Degraded, Dead, Archived, Collapsed);

   function Allowed (From_State, To_State : World_State) return Boolean
     with Global => null;

   type Transaction_State is
     (Prepared, Authorized, Denied, Committed, Aborted);

   function Transaction_Allowed
     (From_State, To_State : Transaction_State) return Boolean
     with Global => null,
          Post =>
            (if From_State = Denied then
                not Transaction_Allowed'Result
                or else To_State = Aborted);

   procedure Advance
     (State     : in out Transaction_State;
      Requested : Transaction_State)
     with Post =>
       State =
         (if Transaction_Allowed (State'Old, Requested)
          then Requested
          else State'Old)
       and then (if State'Old = Denied then State /= Committed);

end Worldline.Transitions;
