with Interfaces;
with SPARK.Big_Integers;
with Worldline.Operation_Authority;
with Resource_Actor_Admission;
-- Pending exact Operation_Authority protocol dependency is separately retained.
-- This complete value conjunction does not attest foreign memory or custody.
package Worldline.Resource_Actor_Execution with SPARK_Mode is
   package A renames Worldline.Operation_Authority;
   package K renames Resource_Actor_Admission;
   package S renames K.S;
   package L renames K.L;
   package Q renames K.Q;
   use SPARK.Big_Integers;
   use type Q.Byte_Count;
   use type Q.Byte;
   use type Q.Ordering;
   use type A.Decision;
   use type K.Status;
   use type L.Phase;
   package UID_Values is new SPARK.Big_Integers.Unsigned_Conversions (Interfaces.Unsigned_32);
   type Crosswalk is record
      Resource_Current : S.Current_Observation;
      Operation_Policy, Operation_Root_Set : A.R.Optional_Digest;
      Owner_Genesis, Installation, Gate_Config, Managed_Observation : L.Identity;
      Original_Grant, Complete_Crosswalk, Current_Source, Original_Request : L.Identity;
      Original_Requester, Original_Transaction, Preparer, Selected_Plan : L.Identity;
   end record;
   type Status is (Ready_Value_Conjunction, Actor_Refused, Authority_Refused,
      Original_Binding_Mismatch, Current_Binding_Mismatch, Crosswalk_Mismatch,
      Requester_Mismatch, Physical_Origin_Mismatch);
   function Digest_Matches (Data : Q.Byte_Array; V : L.Identity;
                            D : A.R.Optional_Digest) return Boolean is
     (L.Id_Valid (Data, V) and then D.Present and then V.Value.Length = Hash'Length
      and then (for all I in Hash'Range =>
        Data (V.Value.First + Q.Byte_Count (I - Hash'First)) = D.Value (I))) with Global => null;
   function Epoch_Matches (Resource_Data, Authority_Data : Q.Byte_Array;
                           V : L.Epoch; E : A.R.Optional_Epoch) return Boolean is
     (L.T.Epoch_Valid (Resource_Data, V) and then A.R.Same (Authority_Data, E, E)
      and then L.Exact_Value (Resource_Data, V.Value) = L.Exact_Value (Authority_Data, E.Value)) with Global => null;
   function Crosswalk_Valid (Data : Q.Byte_Array; W : Crosswalk) return Boolean is
     (W.Operation_Policy.Present and then W.Operation_Root_Set.Present
      and then L.Id_Valid (Data, W.Owner_Genesis) and then L.Id_Valid (Data, W.Installation)
      and then L.Id_Valid (Data, W.Gate_Config) and then L.Id_Valid (Data, W.Managed_Observation)
      and then L.Id_Valid (Data, W.Original_Grant) and then L.Id_Valid (Data, W.Complete_Crosswalk)
      and then L.Id_Valid (Data, W.Current_Source) and then L.Id_Valid (Data, W.Original_Request)
      and then L.Id_Valid (Data, W.Original_Requester) and then L.Id_Valid (Data, W.Selected_Plan)) with Global => null;
   function Same_Current (Data : Q.Byte_Array; A, B : S.Current_Observation) return Boolean is
     (L.Same_Context (Data, A.Scope, B.Scope)
      and then L.Same_Epoch (Data, A.Resource_Epoch, B.Resource_Epoch)
      and then L.Same (Data, A.Universe_Head, B.Universe_Head)
      and then L.Same (Data, A.Ledger_Head, B.Ledger_Head)
      and then L.Same (Data, A.History_Head, B.History_Head)
      and then L.Same (Data, A.Physical_Head, B.Physical_Head)
      and then L.Same (Data, A.Store_Genesis, B.Store_Genesis)
      and then L.Same (Data, A.Store_Id, B.Store_Id)
      and then L.Same (Data, A.Root_Head, B.Root_Head)
      and then L.Optional_Same (Data, A.Prime, B.Prime)
      and then Q.Compare (Data, A.Root_Count, B.Root_Count) = Q.Equal
      and then L.Same (Data, A.Cause, B.Cause)
      and then L.Same (Data, A.Requester, B.Requester)
      and then L.Same (Data, A.Receipt, B.Receipt)
      and then L.Same (Data, A.Catalogue_Head, B.Catalogue_Head)
      and then L.Same (Data, A.Observation_Head, B.Observation_Head)) with Global => null;
   function Original_Holds (Resource_Data, Authority_Data : Q.Byte_Array;
                            B : A.Binding; O : K.Observation) return Boolean is
     (A.Valid (Authority_Data, B) and then L.Binding_Valid (Resource_Data, O.Bound)
      and then Digest_Matches (Resource_Data, O.Bound.Operation, B.Id (A.Operation_Id))
      and then Digest_Matches (Resource_Data, O.Bound.Reservation, B.Id (A.Reservation))
      and then Digest_Matches (Resource_Data, O.Bound.Capability, B.Id (A.Grant_Id))
      and then Digest_Matches (Resource_Data, O.Bound.Grant_Use, B.Id (A.Use_Id))
      and then Digest_Matches (Resource_Data, O.Bound.Workload, B.Id (A.Target))
      and then Digest_Matches (Resource_Data, O.Bound.Provenance, B.Id (A.Provenance))
      and then Digest_Matches (Resource_Data, O.Bound.Universe_Head, B.Id (A.Universe_Head))
      and then Epoch_Matches (Resource_Data, Authority_Data, O.Bound.Resource_Epoch, B.Resource_Epoch)) with Global => null;
   function Current_Holds (Resource_Data, Authority_Data : Q.Byte_Array;
                           B : A.Binding; Current : S.Current_Observation) return Boolean is
     (A.Valid (Authority_Data, B)
      and then Digest_Matches (Resource_Data, Current.Scope.Instance, B.Id (A.Instance))
      and then Digest_Matches (Resource_Data, Current.Universe_Head, B.Id (A.Universe_Head))
      and then Digest_Matches (Resource_Data, Current.Ledger_Head, B.Id (A.Resource_Head))
      and then Epoch_Matches (Resource_Data, Authority_Data, Current.Scope.Policy_Epoch, B.Policy_Epoch)
      and then Epoch_Matches (Resource_Data, Authority_Data, Current.Resource_Epoch, B.Resource_Epoch)) with Global => null;
   -- Crosswalk fields are complete factual inputs from the actual owner journal,
   -- Gate/config/store and resource producer. Unrelated policy/root grammars
   -- remain separate. Source/producer correspondence is a required caller proof.
   function Reference (Resource_Data, Authority_Data : Q.Byte_Array;
      State : S.State; History : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      Actor : K.Observation; Capabilities : K.Capability_Array;
      Groups, Proc_Groups : K.Group_Array; W : Crosswalk;
      Grants : A.Grants; Uses : A.Uses; Original : A.Binding;
      Now : Q.Quantity; Evidence : A.Evidence; Receipts, Events : A.C.Retained_Rows) return Status
   with Ghost, Global => null;
   function Decide (Resource_Data, Authority_Data : Q.Byte_Array;
      State : S.State; History : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      Actor : K.Observation; Capabilities : K.Capability_Array;
      Groups, Proc_Groups : K.Group_Array; W : Crosswalk;
      Grants : A.Grants; Uses : A.Uses; Original : A.Binding;
      Now : Q.Quantity; Evidence : A.Evidence; Receipts, Events : A.C.Retained_Rows) return Status
   with Global => null,
     Post => Decide'Result = Reference (Resource_Data, Authority_Data, State, History,
       Rows, Projection, Buckets, Observed, Facts, Current, Actor, Capabilities,
       Groups, Proc_Groups, W, Grants, Uses, Original, Now, Evidence, Receipts, Events);
end Worldline.Resource_Actor_Execution;
