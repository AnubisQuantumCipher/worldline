package Worldline.Transitions with SPARK_Mode is

   type World_State is
     (Mutable, Finalizing, Valid, Degraded, Dead, Archived, Collapsed);

   function Allowed (From_State, To_State : World_State) return Boolean
     with Global => null,
          Post => Allowed'Result =
            (case From_State is
                when Mutable => To_State in Finalizing | Dead,
                when Finalizing => To_State in Valid | Degraded | Dead,
                when Valid => To_State in Collapsed | Archived,
                when Degraded => To_State in Dead | Archived,
                when Dead | Collapsed => To_State = Archived,
                when Archived => False);

   type Transaction_State is
     (Prepared, Authorized, Denied, Committed, Aborted);

   function Transaction_Allowed
     (From_State, To_State : Transaction_State) return Boolean
     with Global => null,
          Post =>
            Transaction_Allowed'Result =
              (case From_State is
                  when Prepared => To_State in Authorized | Denied | Aborted,
                  when Authorized => To_State in Committed | Aborted,
                  when Denied => To_State = Aborted,
                  when Committed | Aborted => False)
            and then (if From_State = Denied then
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
