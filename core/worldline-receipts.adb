with Attest;
with Attest.SHA256;

package body Worldline.Receipts with SPARK_Mode is

   Domain : constant Attest.Byte_Array :=
     [Attest.Byte (Character'Pos ('w')),
      Attest.Byte (Character'Pos ('o')),
      Attest.Byte (Character'Pos ('r')),
      Attest.Byte (Character'Pos ('l')),
      Attest.Byte (Character'Pos ('d')),
      Attest.Byte (Character'Pos ('l')),
      Attest.Byte (Character'Pos ('i')),
      Attest.Byte (Character'Pos ('n')),
      Attest.Byte (Character'Pos ('e')),
      Attest.Byte (Character'Pos ('-')),
      Attest.Byte (Character'Pos ('r')),
      Attest.Byte (Character'Pos ('e')),
      Attest.Byte (Character'Pos ('c')),
      Attest.Byte (Character'Pos ('e')),
      Attest.Byte (Character'Pos ('i')),
      Attest.Byte (Character'Pos ('p')),
      Attest.Byte (Character'Pos ('t')),
      Attest.Byte (Character'Pos ('-')),
      Attest.Byte (Character'Pos ('v')),
      Attest.Byte (Character'Pos ('1'))];

   function New_Chain (Initial_Head : Hash) return Chain is
     (Current => Initial_Head, Valid => True);

   function Link (Previous, Receipt_Root : Hash) return Hash is
      C : Attest.SHA256.Context := Attest.SHA256.Initial;
   begin
      Attest.SHA256.Update (C, Domain);
      Attest.SHA256.Update (C, Previous);
      Attest.SHA256.Update (C, Receipt_Root);
      return Attest.SHA256.Final (C);
   end Link;

   procedure Append
     (State             : in out Chain;
      Supplied_Previous : Hash;
      Receipt_Root      : Hash)
   is
   begin
      if State.Valid then
         if Supplied_Previous = State.Current then
            State.Current := Link (Supplied_Previous, Receipt_Root);
         else
            State.Valid := False;
         end if;
      end if;
   end Append;

end Worldline.Receipts;
