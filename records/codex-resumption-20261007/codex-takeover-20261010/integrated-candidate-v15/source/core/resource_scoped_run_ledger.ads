with Resource_Run_Ledger;
with Resource_Observation_Classification;
with Resource_Quantities;
with SPARK.Big_Integers;
package Resource_Scoped_Run_Ledger with SPARK_Mode is
   package L renames Resource_Run_Ledger;
   package K renames Resource_Observation_Classification;
   package Q renames Resource_Quantities;
   use L;
   use SPARK.Big_Integers;
   use type Q.Byte_Count;
   use type Q.Ordering;
   type State is record
      Current : L.Context;
      Resource_Epoch : L.Epoch;
      Universe_Head, Ledger_Head, History_Head, Physical_Head : L.Identity;
   end record;
   type Scope_Frame is record
      Scope : L.Context;
      First_Epoch : L.Epoch;
      Universe_Head, Frame_Head, Prior_Frame : L.Identity;
      Store_Genesis, Store_Id, Root_Head, Prime : L.Identity;
      Root_Count : Q.Quantity;
      Cause, Requester, Receipt, Catalogue_Head, Observation_Head : L.Identity;
   end record;
   type History_Array is array (Q.Byte_Index range <>) of Scope_Frame;
   type Physical_Key is record
      Machine, Resource, Unit : L.Identity;
   end record;
   type Bucket is record
      Key : Physical_Key;
      Capacity, Held_Total, Charged_Total : Q.Quantity;
      Capacity_Source, Catalogue_Head, Observation_Head : L.Identity;
   end record;
   type Bucket_Array is array (Q.Byte_Index range <>) of Bucket;
   type Projection is record
      Key : Physical_Key;
      Bound : L.Binding;
      Origin : L.Context;
      Catalogue_Head : L.Identity;
      Numerator, Denominator, Amount : Q.Quantity;
   end record;
   type Projection_Array is array (Q.Byte_Index range <>) of Projection;
   type Facts_Array is array (Q.Byte_Index range <>) of K.Facts;
   type Current_Observation is record
      Scope : L.Context;
      Resource_Epoch : L.Epoch;
      Universe_Head, Ledger_Head, History_Head, Physical_Head : L.Identity;
      Store_Genesis, Store_Id, Root_Head, Prime : L.Identity;
      Root_Count : Q.Quantity;
      Cause, Requester, Receipt, Catalogue_Head, Observation_Head : L.Identity;
   end record;
   type Action is (Ordinary, Advance_Context);
   type Intent is record
      Kind : Action;
      Original : L.Request;
      Expected_Epoch : L.Epoch;
      Expected_Ledger_Head, Request_Id, Cause, Requester, Receipt : L.Identity;
   end record;
   type Status is (Ready, Invalid_Before, Invalid_Proposed, History_Invalid,
      Current_Observation_Invalid, Physical_Roster_Invalid,
      Physical_Projection_Invalid, Physical_Conservation_Mismatch,
      Parent_Invalid, Request_Invalid, Stale_Epoch, Ledger_Head_Mismatch,
      Epoch_Not_Successor, Historical_Row_Removed, Historical_Row_Changed,
      Immutable_Origin_Changed, Native_Roster_Invalid, Illegal_Lifecycle,
      Context_Changed, Capacity_Exceeded, Context_Advance_Invalid);
   function Frame_Valid (Data : Q.Byte_Array; F : Scope_Frame) return Boolean is
     (L.Context_Valid (Data, F.Scope) and then L.T.Epoch_Valid (Data, F.First_Epoch)
      and then L.Id_Valid (Data, F.Universe_Head) and then L.Id_Valid (Data, F.Frame_Head)
      and then L.Id_Valid (Data, F.Store_Genesis) and then L.Id_Valid (Data, F.Store_Id)
      and then L.Id_Valid (Data, F.Root_Head) and then L.T.Nonnegative_Valid (Data, F.Root_Count)
      and then (if F.Prime.Present then L.Id_Valid (Data, F.Prime))
      and then L.Id_Valid (Data, F.Cause) and then L.Id_Valid (Data, F.Requester)
      and then L.Id_Valid (Data, F.Receipt) and then L.Id_Valid (Data, F.Catalogue_Head)
      and then L.Id_Valid (Data, F.Observation_Head)) with Global => null;
   function Same_Frame (Data : Q.Byte_Array; A, B : Scope_Frame) return Boolean is
     (Frame_Valid (Data, A) and then Frame_Valid (Data, B)
      and then L.Same_Context (Data, A.Scope, B.Scope)
      and then L.Same_Epoch (Data, A.First_Epoch, B.First_Epoch)
      and then L.Same (Data, A.Universe_Head, B.Universe_Head)
      and then L.Same (Data, A.Frame_Head, B.Frame_Head)
      and then L.Optional_Same (Data, A.Prior_Frame, B.Prior_Frame)
      and then L.Same (Data, A.Store_Genesis, B.Store_Genesis)
      and then L.Same (Data, A.Store_Id, B.Store_Id)
      and then L.Same (Data, A.Root_Head, B.Root_Head)
      and then L.Optional_Same (Data, A.Prime, B.Prime)
      and then Q.Compare (Data, A.Root_Count, B.Root_Count) = Q.Equal
      and then L.Same (Data, A.Cause, B.Cause) and then L.Same (Data, A.Requester, B.Requester)
      and then L.Same (Data, A.Receipt, B.Receipt)
      and then L.Same (Data, A.Catalogue_Head, B.Catalogue_Head)
      and then L.Same (Data, A.Observation_Head, B.Observation_Head)) with Global => null;
   function History_Valid (Data : Q.Byte_Array; S : State; H : History_Array) return Boolean is
     (L.Context_Valid (Data, S.Current) and then L.T.Epoch_Valid (Data, S.Resource_Epoch)
      and then L.Id_Valid (Data, S.Universe_Head) and then L.Id_Valid (Data, S.Ledger_Head)
      and then L.Id_Valid (Data, S.History_Head) and then L.Id_Valid (Data, S.Physical_Head)
      and then H'Length > 0 and then not H (H'First).Prior_Frame.Present
      and then (for all I in H'Range => Frame_Valid (Data, H (I)))
      and then (for all I in H'Range =>
        Q.Compare (Data, H (I).First_Epoch.Value, S.Resource_Epoch.Value) in Q.Less | Q.Equal
        and then (if I > H'First then
          Q.Compare (Data, H (I - 1).First_Epoch.Value, H (I).First_Epoch.Value) = Q.Less
          and then L.Same (Data, H (I).Prior_Frame, H (I - 1).Frame_Head)
          and then L.Same (Data, H (I).Store_Genesis, H (H'First).Store_Genesis)
          and then L.Same (Data, H (I).Store_Id, H (H'First).Store_Id)))
      and then (for all I in H'Range => (for all J in H'Range =>
        (if I < J then not L.Same (Data, H (I).Frame_Head, H (J).Frame_Head))))
      and then L.Same_Context (Data, S.Current, H (H'Last).Scope)
      and then L.Same (Data, S.Universe_Head, H (H'Last).Universe_Head)
      and then L.Same (Data, S.History_Head, H (H'Last).Frame_Head)) with Global => null;
   function Origin (Data : Q.Byte_Array; Item : L.Row; F : Scope_Frame) return Boolean is
     (L.Row_Valid (Data, Item) and then Frame_Valid (Data, F)
      and then L.Same_Context (Data, Item.Scope, F.Scope)
      and then L.Same (Data, Item.Bound.Universe_Head, F.Universe_Head)
      and then Q.Compare (Data, F.First_Epoch.Value, Item.Bound.Resource_Epoch.Value) in Q.Less | Q.Equal)
   with Global => null;
   function Retained_Origin (Data : Q.Byte_Array; S : State; H : History_Array; Item : L.Row) return Boolean is
     (History_Valid (Data, S, H) and then L.Row_Valid (Data, Item)
      and then Q.Compare (Data, Item.Bound.Resource_Epoch.Value, S.Resource_Epoch.Value) in Q.Less | Q.Equal
      and then (for some I in H'Range => Origin (Data, Item, H (I))
        and then (if I < H'Last then Q.Compare
          (Data, Item.Bound.Resource_Epoch.Value, H (I + 1).First_Epoch.Value) = Q.Less))) with Global => null;
   function Shape (Data : Q.Byte_Array; S : State; H : History_Array; Rows : L.Row_Array) return Boolean is
     (History_Valid (Data, S, H)
      and then (for all I in Rows'Range => Retained_Origin (Data, S, H, Rows (I)))
      and then (for all I in Rows'Range => (for all J in Rows'Range =>
        (if I < J then not L.Same (Data, Rows (I).Bound.Reservation, Rows (J).Bound.Reservation)
         and then not L.Same (Data, Rows (I).Bound.Operation, Rows (J).Bound.Operation))))) with Global => null;
   function Key_Valid (Data : Q.Byte_Array; V : Physical_Key) return Boolean is
     (L.Id_Valid (Data, V.Machine) and then L.Id_Valid (Data, V.Resource)
      and then L.Id_Valid (Data, V.Unit)) with Global => null;
   function Same_Key (Data : Q.Byte_Array; A, B : Physical_Key) return Boolean is
     (Key_Valid (Data, A) and then Key_Valid (Data, B)
      and then L.Same (Data, A.Machine, B.Machine)
      and then L.Same (Data, A.Resource, B.Resource) and then L.Same (Data, A.Unit, B.Unit)) with Global => null;
   function Projection_Valid (Data : Q.Byte_Array; S : State; H : History_Array;
                              Item : L.Row; P : Projection) return Boolean is
     (Retained_Origin (Data, S, H, Item) and then Key_Valid (Data, P.Key)
      and then L.Same (Data, P.Key.Machine, Item.Scope.Host)
      and then L.Same_Binding (Data, Item.Bound, P.Bound)
      and then L.Same_Context (Data, Item.Scope, P.Origin)
      and then L.T.Nonnegative_Valid (Data, P.Numerator)
      and then L.T.Nonnegative_Valid (Data, P.Denominator)
      and then L.T.Nonnegative_Valid (Data, P.Amount)
      and then L.Exact_Value (Data, P.Numerator) > To_Big_Integer (0)
      and then L.Exact_Value (Data, P.Denominator) > To_Big_Integer (0)
      and then (for some I in H'Range => Origin (Data, Item, H (I))
        and then L.Same (Data, P.Catalogue_Head, H (I).Catalogue_Head)
        and then (if I < H'Last then Q.Compare (Data, Item.Bound.Resource_Epoch.Value, H (I + 1).First_Epoch.Value) = Q.Less))
      and then (L.Amount (Data, Item) * L.Exact_Value (Data, P.Numerator)) rem
                  L.Exact_Value (Data, P.Denominator) = To_Big_Integer (0)
      and then L.Exact_Value (Data, P.Amount) =
        (L.Amount (Data, Item) * L.Exact_Value (Data, P.Numerator)) / L.Exact_Value (Data, P.Denominator)) with Global => null;
   function Same_Projection_Origin (Data : Q.Byte_Array; A, B : Projection) return Boolean is
     (Same_Key (Data, A.Key, B.Key) and then L.Same_Binding (Data, A.Bound, B.Bound)
      and then L.Same_Context (Data, A.Origin, B.Origin)
      and then L.Same (Data, A.Catalogue_Head, B.Catalogue_Head)
      and then Q.Compare (Data, A.Numerator, B.Numerator) = Q.Equal
      and then Q.Compare (Data, A.Denominator, B.Denominator) = Q.Equal) with Global => null;
   function Physical_Roster (Data : Q.Byte_Array; S : State; H : History_Array;
                             Rows : L.Row_Array; P : Projection_Array) return Boolean is
     (Rows'Length = P'Length and then (for all I in Rows'Range => Projection_Valid
       (Data, S, H, Rows (I), P (P'First + (I - Rows'First))))) with Global => null;
   function Charge_Reference (Data : Q.Byte_Array; Rows : L.Row_Array; P : Projection_Array;
                              Count : Q.Byte_Count; Key : Physical_Key; Kind : L.Charge_Kind;
                              Parent : L.Identity) return Valid_Big_Integer is
     (if Count = 0 then To_Big_Integer (0)
      else Charge_Reference (Data, Rows, P, Count - 1, Key, Kind, Parent)
        + (if Count <= Rows'Length and then Count <= P'Length
          and then L.Included (Data, Rows (Rows'First + (Count - 1)), Parent, Kind)
          and then Same_Key (Data, Key, P (P'First + (Count - 1)).Key)
           then Q.Value (Data, P (P'First + (Count - 1)).Amount) else To_Big_Integer (0)))
   with Ghost, Global => null, Subprogram_Variant => (Decreases => Count);
   function Charge (Data : Q.Byte_Array; Rows : L.Row_Array; P : Projection_Array;
                    Key : Physical_Key; Kind : L.Charge_Kind; Parent : L.Identity) return Valid_Big_Integer
   with Global => null, Post => Charge'Result = Charge_Reference (Data, Rows, P, Rows'Length, Key, Kind, Parent);
   function Bucket_Valid (Data : Q.Byte_Array; B : Bucket) return Boolean is
     (Key_Valid (Data, B.Key) and then L.T.Nonnegative_Valid (Data, B.Capacity)
      and then L.T.Nonnegative_Valid (Data, B.Held_Total) and then L.T.Nonnegative_Valid (Data, B.Charged_Total)
      and then L.Id_Valid (Data, B.Capacity_Source) and then L.Id_Valid (Data, B.Catalogue_Head)
      and then L.Id_Valid (Data, B.Observation_Head)) with Global => null;
   function Physical_Reference (Data : Q.Byte_Array; S : State; H : History_Array;
                                Rows : L.Row_Array; P : Projection_Array; B : Bucket_Array) return Boolean is
     (Physical_Roster (Data, S, H, Rows, P)
      and then (for all I in B'Range => Bucket_Valid (Data, B (I)))
      and then (for all I in B'Range => (for all J in B'Range =>
        (if I < J then not Same_Key (Data, B (I).Key, B (J).Key))))
      and then (for all I in P'Range => (for some J in B'Range => Same_Key (Data, P (I).Key, B (J).Key)))
      and then (for all I in B'Range =>
        Q.Value (Data, B (I).Held_Total) = Charge_Reference (Data, Rows, P, Rows'Length, B (I).Key, L.Held_Capacity, (Present => False))
        and then Q.Value (Data, B (I).Charged_Total) = Charge_Reference (Data, Rows, P, Rows'Length, B (I).Key, L.Irreversible_Budget, (Present => False))))
   with Ghost, Global => null;
   function Physical (Data : Q.Byte_Array; S : State; H : History_Array;
                      Rows : L.Row_Array; P : Projection_Array; B : Bucket_Array) return Boolean
   with Global => null, Post => Physical'Result = Physical_Reference (Data, S, H, Rows, P, B);
   function Contained_Reference (Data : Q.Byte_Array; Rows : L.Row_Array; P : Projection_Array) return Boolean is
     (Rows'Length = P'Length and then (for all I in P'Range =>
        L.T.Nonnegative_Valid (Data, P (I).Numerator)
        and then L.T.Nonnegative_Valid (Data, P (I).Denominator)
        and then L.T.Nonnegative_Valid (Data, P (I).Amount)
        and then Q.Value (Data, P (I).Numerator) > To_Big_Integer (0)
        and then Q.Value (Data, P (I).Denominator) > To_Big_Integer (0))
      and then (for all I in Rows'Range => L.Row_Valid (Data, Rows (I)))
      and then (for all I in Rows'Range =>
       (if Rows (I).Parent.Present then (for some J in Rows'Range => J < I
         and then L.Parent_Supports (Data, Rows (J), Rows (I))
         and then Same_Key (Data, P (P'First + (J - Rows'First)).Key, P (P'First + (I - Rows'First)).Key))))
      and then (for all I in Rows'Range =>
        Charge_Reference (Data, Rows, P, Rows'Length, P (P'First + (I - Rows'First)).Key, L.Held_Capacity, Rows (I).Bound.Reservation)
        + Charge_Reference (Data, Rows, P, Rows'Length, P (P'First + (I - Rows'First)).Key, L.Irreversible_Budget, Rows (I).Bound.Reservation)
        <= (Q.Value (Data, Rows (I).Amount) * Q.Value (Data, P (P'First + (I - Rows'First)).Numerator)) /
                 Q.Value (Data, P (P'First + (I - Rows'First)).Denominator))) with Ghost, Global => null;
   function Contained (Data : Q.Byte_Array; Rows : L.Row_Array; P : Projection_Array) return Boolean
   with Global => null,
     Post => Contained'Result = Contained_Reference (Data, Rows, P);
   function Current_Valid (Data : Q.Byte_Array; S : State; H : History_Array; C : Current_Observation) return Boolean is
     (History_Valid (Data, S, H) and then L.Same_Context (Data, S.Current, C.Scope)
      and then L.Same_Epoch (Data, S.Resource_Epoch, C.Resource_Epoch)
      and then L.Same (Data, S.Universe_Head, C.Universe_Head)
      and then L.Same (Data, S.Ledger_Head, C.Ledger_Head)
      and then L.Same (Data, S.History_Head, C.History_Head)
      and then L.Same (Data, S.Physical_Head, C.Physical_Head)
      and then L.Same (Data, H (H'Last).Store_Genesis, C.Store_Genesis)
      and then L.Same (Data, H (H'Last).Store_Id, C.Store_Id)
      and then L.Same (Data, H (H'Last).Root_Head, C.Root_Head)
      and then Q.Compare (Data, H (H'Last).Root_Count, C.Root_Count) = Q.Equal
      and then L.Optional_Same (Data, H (H'Last).Prime, C.Prime)
      and then L.Same (Data, H (H'Last).Catalogue_Head, C.Catalogue_Head)
      and then L.Id_Valid (Data, C.Root_Head) and then L.T.Nonnegative_Valid (Data, C.Root_Count)
      and then (if C.Prime.Present then L.Id_Valid (Data, C.Prime))
      and then L.Id_Valid (Data, C.Cause) and then L.Id_Valid (Data, C.Requester)
      and then L.Id_Valid (Data, C.Receipt) and then L.Id_Valid (Data, C.Observation_Head)) with Global => null;
   function Classify_Reference (Data : Q.Byte_Array; S : State; H : History_Array;
                                Item : L.Row; F : K.Facts) return L.Liveness is
     (if not Retained_Origin (Data, S, H, Item)
        or else not L.Same_Context (Data, S.Current, F.Current)
        or else not L.Same_Epoch (Data, S.Resource_Epoch, F.Current_Epoch)
        or else not L.Same (Data, S.Universe_Head, F.Current_Universe_Head)
        or else not L.Same (Data, S.Ledger_Head, F.Current_Ledger_Head)
        or else not L.Same_Binding (Data, Item.Bound, F.Retained)
        or else not L.Id_Valid (Data, F.Intent) or else not L.Id_Valid (Data, F.Observation_Head) then L.Unknown
      elsif K.Never_Holds (Data, Item, F) then L.Never_Launched
      elsif K.Live_Holds (Data, Item, F) then L.Live
      elsif K.Reaped_Holds (Data, Item, F) then L.Reaped else L.Unknown) with Ghost, Global => null;
   function Classify (Data : Q.Byte_Array; S : State; H : History_Array;
                      Item : L.Row; F : K.Facts) return L.Liveness
   with Global => null, Post => Classify'Result = Classify_Reference (Data, S, H, Item, F);
   function Native_Valid (Data : Q.Byte_Array; S : State; H : History_Array;
                          Rows : L.Row_Array; Observed : L.Native_Array; F : Facts_Array) return Boolean is
     (Rows'Length = Observed'Length and then Rows'Length = F'Length
      and then (for all I in Rows'Range =>
        L.Same_Context (Data, Rows (I).Scope, Observed (Observed'First + (I - Rows'First)).Scope)
        and then L.Same_Epoch (Data, S.Resource_Epoch, Observed (Observed'First + (I - Rows'First)).Resource_Epoch)
        and then L.Same_Binding (Data, Rows (I).Bound, Observed (Observed'First + (I - Rows'First)).Bound)
        and then L.Same (Data, Observed (Observed'First + (I - Rows'First)).Observation_Head,
                         F (F'First + (I - Rows'First)).Observation_Head)
        and then Observed (Observed'First + (I - Rows'First)).Observed =
          Classify (Data, S, H, Rows (I), F (F'First + (I - Rows'First)))
        and then (if Observed (Observed'First + (I - Rows'First)).Observed in L.Live | L.Reaped then
          L.Optional_Same (Data, Observed (Observed'First + (I - Rows'First)).Actual_Unit, F (F'First + (I - Rows'First)).Actual_Unit)
          and then L.Optional_Same (Data, Observed (Observed'First + (I - Rows'First)).Cgroup, F (F'First + (I - Rows'First)).Cgroup)
          and then L.Optional_Same (Data, Observed (Observed'First + (I - Rows'First)).Invocation, F (F'First + (I - Rows'First)).Invocation)
        else L.Optional_Same (Data, Observed (Observed'First + (I - Rows'First)).Actual_Unit, Rows (I).Actual_Unit)
          and then L.Optional_Same (Data, Observed (Observed'First + (I - Rows'First)).Cgroup, Rows (I).Cgroup)
          and then L.Optional_Same (Data, Observed (Observed'First + (I - Rows'First)).Invocation, Rows (I).Invocation))
        and then (if L.Has_Effect (Rows (I)) then
          L.Same (Data, Rows (I).Actual_Unit, Observed (Observed'First + (I - Rows'First)).Actual_Unit)
          and then L.Same (Data, Rows (I).Cgroup, Observed (Observed'First + (I - Rows'First)).Cgroup)
          and then L.Same (Data, Rows (I).Invocation, Observed (Observed'First + (I - Rows'First)).Invocation)))) with Global => null;
   function History_Prefix (Data : Q.Byte_Array; A, B : History_Array) return Boolean is
     (A'Length <= B'Length and then (for all I in A'Range => Same_Frame
       (Data, A (I), B (B'First + (I - A'First))))) with Global => null;
   function Projection_Prefix (Data : Q.Byte_Array; A, B : Projection_Array) return Boolean is
     (A'Length <= B'Length and then (for all I in A'Range => Same_Projection_Origin
       (Data, A (I), B (B'First + (I - A'First))))) with Global => null;
   function Bucket_Retained (Data : Q.Byte_Array; A, B : Bucket_Array) return Boolean is
     (for all I in A'Range => (for some J in B'Range => Same_Key (Data, A (I).Key, B (J).Key))) with Global => null;
   function Buckets_Observed (Data : Q.Byte_Array; Proposed, Actual : Bucket_Array) return Boolean is
     (Proposed'Length = Actual'Length and then (for all I in Proposed'Range =>
        Bucket_Valid (Data, Actual (Actual'First + (I - Proposed'First)))
        and then Same_Key (Data, Proposed (I).Key, Actual (Actual'First + (I - Proposed'First)).Key)
        and then Q.Compare (Data, Proposed (I).Capacity, Actual (Actual'First + (I - Proposed'First)).Capacity) = Q.Equal
        and then L.Same (Data, Proposed (I).Capacity_Source, Actual (Actual'First + (I - Proposed'First)).Capacity_Source)
        and then L.Same (Data, Proposed (I).Catalogue_Head, Actual (Actual'First + (I - Proposed'First)).Catalogue_Head)
        and then L.Same (Data, Proposed (I).Observation_Head, Actual (Actual'First + (I - Proposed'First)).Observation_Head))) with Global => null;
   function Within_Capacity (Data : Q.Byte_Array; B : Bucket_Array) return Boolean is
     ((for all I in B'Range => Bucket_Valid (Data, B (I)))
      and then (for all I in B'Range => L.Exact_Value (Data, B (I).Held_Total) + L.Exact_Value (Data, B (I).Charged_Total)
        <= L.Exact_Value (Data, B (I).Capacity))) with Global => null;
   function No_Amplification (Data : Q.Byte_Array; Before, Proposed : Bucket_Array) return Boolean is
     (Bucket_Retained (Data, Before, Proposed)
      and then (for all I in Proposed'Range =>
        (for some J in Before'Range => Same_Key (Data, Proposed (I).Key, Before (J).Key)
          and then L.Exact_Value (Data, Proposed (I).Held_Total) + L.Exact_Value (Data, Proposed (I).Charged_Total)
            <= L.Exact_Value (Data, Before (J).Held_Total) + L.Exact_Value (Data, Before (J).Charged_Total))
        or else L.Exact_Value (Data, Proposed (I).Held_Total) + L.Exact_Value (Data, Proposed (I).Charged_Total) = To_Big_Integer (0))) with Global => null;
   function Current_Facts (Data : Q.Byte_Array; C : Current_Observation; F : Facts_Array) return Boolean is
     (for all I in F'Range => L.Same_Context (Data, C.Scope, F (I).Current)
      and then L.Same_Epoch (Data, C.Resource_Epoch, F (I).Current_Epoch)
      and then L.Same (Data, C.Universe_Head, F (I).Current_Universe_Head)
      and then L.Same (Data, C.Ledger_Head, F (I).Current_Ledger_Head)) with Global => null;
   -- A consistent retained snapshot is data, not permission to reserve/launch.
   -- The complete current protected source and transition Check remain required.
   function Valid_Reference (Data : Q.Byte_Array; S : State; H : History_Array;
      Rows : L.Row_Array; P : Projection_Array; B : Bucket_Array;
      C : Current_Observation) return Boolean is
     (Shape (Data, S, H, Rows) and then Physical_Reference (Data, S, H, Rows, P, B)
      and then Contained_Reference (Data, Rows, P) and then Current_Valid (Data, S, H, C))
   with Ghost, Global => null;
   function Valid (Data : Q.Byte_Array; S : State; H : History_Array;
      Rows : L.Row_Array; P : Projection_Array; B : Bucket_Array;
      C : Current_Observation) return Boolean
   with Global => null, Post => Valid'Result = Valid_Reference (Data, S, H, Rows, P, B, C);
   function Advance_Valid (Data : Q.Byte_Array; Before, Proposed : State;
                           H, PH : History_Array; C : Current_Observation; R : Intent) return Boolean is
     (H'Length < Q.Byte_Count'Last and then PH'Length = H'Length + 1
      and then History_Prefix (Data, H, PH)
      and then L.Same_Epoch (Data, PH (PH'Last).First_Epoch, Proposed.Resource_Epoch)
      and then L.Same_Context (Data, PH (PH'Last).Scope, C.Scope)
      and then L.Same (Data, PH (PH'Last).Universe_Head, C.Universe_Head)
      and then L.Same (Data, PH (PH'Last).Store_Genesis, C.Store_Genesis)
      and then L.Same (Data, PH (PH'Last).Store_Id, C.Store_Id)
      and then L.Same (Data, PH (PH'Last).Root_Head, C.Root_Head)
      and then L.Optional_Same (Data, PH (PH'Last).Prime, C.Prime)
      and then Q.Compare (Data, PH (PH'Last).Root_Count, C.Root_Count) = Q.Equal
      and then L.Same (Data, PH (PH'Last).Catalogue_Head, C.Catalogue_Head)
      and then L.Same (Data, PH (PH'Last).Observation_Head, C.Observation_Head)
      and then L.Same (Data, PH (PH'Last).Cause, C.Cause) and then L.Same (Data, R.Cause, C.Cause)
      and then L.Same (Data, PH (PH'Last).Requester, C.Requester) and then L.Same (Data, R.Requester, C.Requester)
      and then L.Same (Data, PH (PH'Last).Receipt, C.Receipt) and then L.Same (Data, R.Receipt, C.Receipt)
      and then L.Same_Epoch (Data, Before.Resource_Epoch, C.Resource_Epoch)
      and then L.Same (Data, Before.Ledger_Head, C.Ledger_Head)
      and then L.Same (Data, Proposed.History_Head, C.History_Head)
      and then L.Same (Data, Proposed.Physical_Head, C.Physical_Head)
      and then (not L.Same_Context (Data, Before.Current, Proposed.Current)
        or else not L.Same (Data, Before.Universe_Head, Proposed.Universe_Head)
        or else not L.Same (Data, Before.Physical_Head, Proposed.Physical_Head)
        or else not L.Same (Data, H (H'Last).Catalogue_Head, PH (PH'Last).Catalogue_Head)
        or else not L.Same (Data, H (H'Last).Root_Head, PH (PH'Last).Root_Head)
        or else not L.Optional_Same (Data, H (H'Last).Prime, PH (PH'Last).Prime))) with Global => null;
   function Ordinary_Reference (Data : Q.Byte_Array; Before : State; H : History_Array;
      Before_Rows, Proposed_Rows : L.Row_Array; Observed : L.Native_Array; R : L.Request) return L.Status is
     (if R.Kind = L.Unknown_Operation then L.Unknown_Kind
      elsif not L.Context_Valid (Data, R.Scope) or else not L.T.Epoch_Valid (Data, R.Expected_Epoch)
        or else not L.Id_Valid (Data, R.Expected_Ledger_Head) or else not L.Id_Valid (Data, R.Request_Id)
        or else not L.Id_Valid (Data, R.Reservation) or else not L.Id_Valid (Data, R.Operation_Id)
        or else not L.Id_Valid (Data, R.Requester) or else not L.Binding_Valid (Data, R.Bound)
        or else not L.Same (Data, R.Bound.Reservation, R.Reservation)
        or else not L.Same (Data, R.Bound.Operation, R.Operation_Id)
        or else not L.Same (Data, R.Bound.Owner, R.Requester) then L.Request_Invalid
      elsif not L.Same_Epoch (Data, Before.Resource_Epoch, R.Expected_Epoch) then L.Stale_Epoch
      elsif not L.Same (Data, Before.Ledger_Head, R.Expected_Ledger_Head) then L.Ledger_Head_Mismatch
      elsif Observed'Length /= Before_Rows'Length then L.Native_Roster_Invalid
      elsif R.Kind = L.Reserve then
        (if Before_Rows'Length = Q.Byte_Count'Last or else
             Proposed_Rows'Length /= Before_Rows'Length + 1 then L.Historical_Row_Removed
         elsif not (for all I in Before_Rows'Range => Same_Row
           (Data, Before_Rows (I), Proposed_Rows (Proposed_Rows'First + (I - Before_Rows'First))))
           then L.Historical_Row_Changed
         elsif not L.Same_Context (Data, Before.Current, R.New_Row.Scope) then L.Context_Changed
         elsif not Same_Row (Data, R.New_Row, Proposed_Rows (Proposed_Rows'Last))
           or else not Same_Binding (Data, R.Bound, R.New_Row.Bound)
           or else R.New_Row.State /= L.Reserved
           or else not Same (Data, R.New_Row.Bound.Reservation, R.Reservation)
           or else not Same (Data, R.New_Row.Bound.Operation, R.Operation_Id)
           or else not Same_Epoch (Data, R.New_Row.Bound.Resource_Epoch, Before.Resource_Epoch)
           or else not Same (Data, R.New_Row.Bound.Universe_Head, Before.Universe_Head)
           then L.Request_Invalid
         elsif not Same (Data, R.Requester, R.New_Row.Bound.Owner) then L.Wrong_Owner
         else L.Ready)
      elsif Proposed_Rows'Length /= Before_Rows'Length then L.Historical_Row_Removed
      elsif not (for some I in Before_Rows'Range => Same
          (Data, Before_Rows (I).Bound.Reservation, R.Reservation)) then L.Request_Invalid
      elsif not (for all I in Before_Rows'Range =>
        (if Same (Data, Before_Rows (I).Bound.Reservation, R.Reservation) then
          L.Same_Context (Data, Before_Rows (I).Scope, R.Scope))) then L.Context_Changed
      elsif not (for all I in Before_Rows'Range =>
        (if Same (Data, Before_Rows (I).Bound.Reservation, R.Reservation) then
          Same (Data, Before_Rows (I).Bound.Owner, R.Requester))) then L.Wrong_Owner
      elsif not (for all I in Before_Rows'Range =>
        (if Same (Data, Before_Rows (I).Bound.Reservation, R.Reservation) then
          Same (Data, Before_Rows (I).Bound.Operation, R.Operation_Id)
          and then Same_Binding (Data, Before_Rows (I).Bound, R.Bound))) then L.Operation_Mismatch
      elsif not (for all I in Before_Rows'Range =>
        (if not Same (Data, Before_Rows (I).Bound.Reservation, R.Reservation) then
          Same_Row (Data, Before_Rows (I), Proposed_Rows (Proposed_Rows'First + (I - Before_Rows'First)))))
        then L.Historical_Row_Changed
      elsif not (for all I in Before_Rows'Range =>
        (if Same (Data, Before_Rows (I).Bound.Reservation, R.Reservation) then
          Changed_Row_Allowed (Data, Before_Rows (I),
             Proposed_Rows (Proposed_Rows'First + (I - Before_Rows'First)),
             Observed (Observed'First + (I - Before_Rows'First)), R))) then L.Illegal_Lifecycle
      else L.Ready)
   with Ghost, Global => null;
   function Ordinary_Relation (Data : Q.Byte_Array; Before : State; H : History_Array;
      Before_Rows, Proposed_Rows : L.Row_Array; Observed : L.Native_Array; R : L.Request) return L.Status
   with Global => null,
     Post => Ordinary_Relation'Result = Ordinary_Reference (Data, Before, H, Before_Rows, Proposed_Rows, Observed, R);
   function Decision_Reference (Data : Q.Byte_Array;
      Before : State; H : History_Array; Rows : L.Row_Array; P : Projection_Array; B : Bucket_Array;
      Proposed : State; PH : History_Array; PR : L.Row_Array; PP : Projection_Array; PB : Bucket_Array;
      Observed : L.Native_Array; F : Facts_Array; Actual : Bucket_Array;
      C : Current_Observation; R : Intent) return Status is
     (if not Shape (Data, Before, H, Rows) then Invalid_Before
      elsif not Shape (Data, Proposed, PH, PR) then Invalid_Proposed
      elsif not Physical_Reference (Data, Before, H, Rows, P, B)
        or else not Physical_Reference (Data, Proposed, PH, PR, PP, PB) then Physical_Projection_Invalid
      elsif not Bucket_Retained (Data, B, PB) or else not Buckets_Observed (Data, PB, Actual) then Physical_Roster_Invalid
      elsif not Projection_Prefix (Data, P, PP) then Immutable_Origin_Changed
      elsif not Contained_Reference (Data, Rows, P) or else not Contained_Reference (Data, PR, PP) then Parent_Invalid
      elsif not Native_Valid (Data, Before, H, Rows, Observed, F)
        or else not Current_Facts (Data, C, F) then Native_Roster_Invalid
      elsif not L.T.Epoch_Valid (Data, R.Expected_Epoch)
        or else not L.Id_Valid (Data, R.Expected_Ledger_Head) or else not L.Id_Valid (Data, R.Request_Id)
        or else not L.Id_Valid (Data, R.Cause) or else not L.Id_Valid (Data, R.Requester)
        or else not L.Id_Valid (Data, R.Receipt) then Request_Invalid
      elsif not L.Same_Epoch (Data, Before.Resource_Epoch, R.Expected_Epoch) then Stale_Epoch
      elsif not L.Same (Data, Before.Ledger_Head, R.Expected_Ledger_Head) then Ledger_Head_Mismatch
      elsif not L.T.Is_Successor (Data, Before.Resource_Epoch.Value, Proposed.Resource_Epoch.Value) then Epoch_Not_Successor
      elsif L.Same (Data, Before.Ledger_Head, Proposed.Ledger_Head) then Ledger_Head_Mismatch
      elsif R.Kind = Advance_Context then
        (if not Advance_Valid (Data, Before, Proposed, H, PH, C, R) then Context_Advance_Invalid
         elsif PR'Length /= Rows'Length or else not (for all I in Rows'Range => L.Same_Row
           (Data, Rows (I), PR (PR'First + (I - Rows'First)))) then Historical_Row_Changed
         elsif not No_Amplification (Data, B, PB) then Physical_Conservation_Mismatch
         else Ready)
      elsif not Current_Valid (Data, Before, H, C)
        or else not L.Same_Context (Data, Before.Current, Proposed.Current)
        or else not L.Same (Data, Before.Universe_Head, Proposed.Universe_Head)
        or else not L.Same (Data, Before.Physical_Head, Proposed.Physical_Head)
        or else H'Length /= PH'Length or else not History_Prefix (Data, H, PH) then Current_Observation_Invalid
      elsif not L.Same_Epoch (Data, R.Expected_Epoch, R.Original.Expected_Epoch)
        or else not L.Same (Data, R.Expected_Ledger_Head, R.Original.Expected_Ledger_Head)
        or else not L.Same (Data, R.Request_Id, R.Original.Request_Id)
        or else not L.Same (Data, R.Cause, R.Original.Operation_Id)
        or else not L.Same (Data, R.Requester, R.Original.Requester) then Request_Invalid
      elsif R.Original.Kind in L.Reserve | L.Record_Launch_Intent | L.Record_Running
        and then (not L.Same_Context (Data, Before.Current, R.Original.Scope)
          or else not L.Same (Data, R.Original.Bound.Universe_Head, Before.Universe_Head)) then Context_Changed
      elsif R.Original.Kind = L.Reserve and then not Within_Capacity (Data, PB) then Capacity_Exceeded
      elsif R.Original.Kind /= L.Reserve and then not No_Amplification (Data, B, PB) then Physical_Conservation_Mismatch
      elsif Ordinary_Relation (Data, Before, H, Rows, PR, Observed, R.Original) /= L.Ready then Illegal_Lifecycle
      else Ready) with Ghost, Global => null;
   function Check (Data : Q.Byte_Array;
      Before : State; H : History_Array; Rows : L.Row_Array; P : Projection_Array; B : Bucket_Array;
      Proposed : State; PH : History_Array; PR : L.Row_Array; PP : Projection_Array; PB : Bucket_Array;
      Observed : L.Native_Array; F : Facts_Array; Actual : Bucket_Array;
      C : Current_Observation; R : Intent) return Status
   with Global => null,
     Post => Check'Result = Decision_Reference (Data, Before, H, Rows, P, B, Proposed, PH, PR, PP, PB, Observed, F, Actual, C, R)
       and then (if Check'Result = Ready then
         Shape (Data, Proposed, PH, PR) and then Physical_Reference (Data, Proposed, PH, PR, PP, PB)
         and then Contained_Reference (Data, PR, PP) and then History_Prefix (Data, H, PH)
         and then Projection_Prefix (Data, P, PP) and then Bucket_Retained (Data, B, PB)
         and then PR'Length >= Rows'Length
         and then L.Exact_Value (Data, Proposed.Resource_Epoch.Value) = L.Exact_Value (Data, Before.Resource_Epoch.Value) + 1
         and then (if R.Kind /= Advance_Context and then R.Original.Kind = L.Reserve then Within_Capacity (Data, PB)
                   else No_Amplification (Data, B, PB)));
end Resource_Scoped_Run_Ledger;
