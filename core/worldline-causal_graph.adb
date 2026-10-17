with Attest;
with Attest.SHA256;

package body Worldline.Causal_Graph with SPARK_Mode is


   function New_Chain (Initial_Head : Hash) return Chain is
     (Current => Initial_Head, Valid => True);


   procedure Append
     (State             : in out Chain;
      Supplied_Previous : Hash;
      Event_Root        : Hash)
   is
   begin
      if State.Valid then
         if Supplied_Previous = State.Current then
            State.Current := Link (Supplied_Previous, Event_Root);
         else
            State.Valid := False;
         end if;
      end if;
   end Append;

end Worldline.Causal_Graph;
