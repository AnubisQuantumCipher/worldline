with Worldline.Operation_Authority;
with Worldline.Collapse;
with Worldline.Collapse_Wire;
with Resource_Run_Ledger;
package Worldline.Canonical_Operation with SPARK_Mode is
   package A renames Worldline.Operation_Authority;
   package L renames Resource_Run_Ledger;
   package C renames Worldline.Collapse_Wire;
   use type A.Decision; use type A.Q.Byte_Count; use type L.Phase;
   use type Worldline.Collapse.Decision; use type Worldline.Collapse.Phase;
   use type A.Q.Byte; use type C.Byte;
   type Decision is (Authority_Refused, Resource_Refused, Binding_Mismatch,
                     Collapse_Refused, Ready);
   function Digest_Matches(Data : A.Q.Byte_Array; Item : L.Identity;
                           Expected : A.R.Optional_Digest) return Boolean is
     (L.Id_Valid(Data,Item) and then Expected.Present and then Item.Value.Length=Hash'Length
      and then (for all I in Hash'Range => Data(Item.Value.First+A.Q.Byte_Count(I-Hash'First))=Expected.Value(I)))
     with Global=>null;
   -- Two complete native models are conjuncts, not copied success flags.
   -- Actual protected producers supply the peer/source correspondence and full
   -- selected raw evaluation packet. This package does not attest custody.
   function Reference(Data : A.Q.Byte_Array; G : A.Grants; H : A.Uses;
      B : A.Binding; Now : A.Q.Quantity; E : A.Evidence;
      State : L.Ledger_State; Rows : L.Row_Array; Observed : L.Native_Array;
      Bound : L.Binding; Requester : L.Identity; Peer : A.Optional_UID;
      Collapse : C.Raw_Request) return Decision with Global=>null;
   function Decide(Data : A.Q.Byte_Array; G : A.Grants; H : A.Uses;
      B : A.Binding; Now : A.Q.Quantity; E : A.Evidence;
      State : L.Ledger_State; Rows : L.Row_Array; Observed : L.Native_Array;
      Bound : L.Binding; Requester : L.Identity; Peer : A.Optional_UID;
      Collapse : C.Raw_Request) return Decision with Global=>null,
      Post=>Decide'Result=Reference(Data,G,H,B,Now,E,State,Rows,Observed,Bound,Requester,Peer,Collapse);
end Worldline.Canonical_Operation;
