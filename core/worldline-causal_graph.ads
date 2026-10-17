with Attest.SHA256;
package Worldline.Causal_Graph with SPARK_Mode is
   use type Hash;


   type Chain is private;

   function New_Chain (Initial_Head : Hash) return Chain
     with Post => Accepted (New_Chain'Result)
       and then Head (New_Chain'Result) = Initial_Head;

   function Accepted (State : Chain) return Boolean;
   function Head (State : Chain) return Hash;

   --  The visible expression is the exact link equation; a matching Post would
   --  hash the same inputs again when assertion checks are enabled.
   function Link (Previous, Event_Root : Hash) return Hash is
     (Attest.SHA256.Causal_Link_Digest
        (Attest.SHA256.To_Digest_Bytes (Previous),
         Attest.SHA256.To_Digest_Bytes (Event_Root)))
     with Global => null;

   procedure Append
     (State             : in out Chain;
      Supplied_Previous : Hash;
      Event_Root        : Hash)
     with Post =>
       (if not Accepted (State'Old) then
           not Accepted (State) and Head (State) = Head (State'Old)
        elsif Supplied_Previous /= Head (State'Old) then
           not Accepted (State) and Head (State) = Head (State'Old)
        else
           Accepted (State)
           and Head (State) = Link (Supplied_Previous, Event_Root));

private

   type Chain is record
      Current : Hash;
      Valid   : Boolean;
   end record;

   function Accepted (State : Chain) return Boolean is (State.Valid);
   function Head (State : Chain) return Hash is (State.Current);

end Worldline.Causal_Graph;
