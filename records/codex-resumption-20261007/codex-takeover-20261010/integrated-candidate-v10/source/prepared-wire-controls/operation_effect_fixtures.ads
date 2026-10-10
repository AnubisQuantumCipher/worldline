with Worldline.Operation_Authority;
package Operation_Effect_Fixtures is
   package A renames Worldline.Operation_Authority;
   package Q renames A.Q;
   type Fixture (Arena_Count, Grant_Count, Use_Count, Receipt_Count, Event_Count : Q.Byte_Count) is record
      Arena : Q.Byte_Array (1 .. Arena_Count);
      Grants : A.Grants (1 .. Grant_Count);
      Uses : A.Uses (1 .. Use_Count);
      Receipts : A.C.Retained_Rows (1 .. Receipt_Count);
      Events : A.C.Retained_Rows (1 .. Event_Count);
      Bound : A.Binding;
      Facts : A.Evidence;
      Now : Q.Quantity;
   end record;
   -- Fixture bytes are emitted from the genuine complete accepted runtime
   -- observation, never from hard-coded equal payload roots or saved status.
   function Load (Path : String) return Fixture;
end Operation_Effect_Fixtures;
