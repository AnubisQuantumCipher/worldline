package Worldline.Receipts with SPARK_Mode is
   use type Hash;


   type Chain is private;

   function New_Chain (Initial_Head : Hash) return Chain
     with Post => Accepted (New_Chain'Result)
       and then Head (New_Chain'Result) = Initial_Head;

   function Accepted (State : Chain) return Boolean;
   function Head (State : Chain) return Hash;

   function Link (Previous, Receipt_Root : Hash) return Hash
     with Global => null;

   procedure Append
     (State             : in out Chain;
      Supplied_Previous : Hash;
      Receipt_Root      : Hash)
     with Post =>
       (if not Accepted (State'Old) then
           not Accepted (State) and Head (State) = Head (State'Old)
        elsif Supplied_Previous /= Head (State'Old) then
           not Accepted (State) and Head (State) = Head (State'Old)
        else
           Accepted (State)
           and Head (State) = Link (Supplied_Previous, Receipt_Root));

private

   type Chain is record
      Current : Hash;
      Valid   : Boolean;
   end record;

   function Accepted (State : Chain) return Boolean is (State.Valid);
   function Head (State : Chain) return Hash is (State.Current);

end Worldline.Receipts;
