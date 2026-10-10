package body Resource_Scoped_Run_Ledger with SPARK_Mode is
   use type L.Status;
   function Charge (Data : Q.Byte_Array; Rows : L.Row_Array; P : Projection_Array;
                    Key : Physical_Key; Kind : L.Charge_Kind; Parent : L.Identity) return Valid_Big_Integer is
      Count : Q.Byte_Count := 0;
      Result : Valid_Big_Integer := To_Big_Integer (0);
   begin
      while Count < Rows'Length loop
         pragma Loop_Invariant (Count <= Rows'Length);
         pragma Loop_Invariant (Result = Charge_Reference (Data, Rows, P, Count, Key, Kind, Parent));
         pragma Loop_Variant (Decreases => Q.Byte_Count (Rows'Length) - Count);
         if Count < P'Length and then L.Included (Data, Rows (Rows'First + Count), Parent, Kind)
           and then Same_Key (Data, Key, P (P'First + Count).Key) then
            Result := Result + L.Exact_Value (Data, P (P'First + Count).Amount);
         end if;
         Count := Count + 1;
      end loop;
      return Result;
   end Charge;
   function Physical (Data : Q.Byte_Array; S : State; H : History_Array;
                      Rows : L.Row_Array; P : Projection_Array; B : Bucket_Array) return Boolean is
   begin
      if not Physical_Roster (Data, S, H, Rows, P) then return False; end if;
      for I in B'Range loop
         pragma Loop_Invariant (for all J in B'Range => (if J < I then Bucket_Valid (Data, B (J))
           and then Q.Value (Data, B (J).Held_Total) = Charge_Reference (Data, Rows, P, Rows'Length, B (J).Key, L.Held_Capacity, (Present => False))
           and then Q.Value (Data, B (J).Charged_Total) = Charge_Reference (Data, Rows, P, Rows'Length, B (J).Key, L.Irreversible_Budget, (Present => False))));
         if not Bucket_Valid (Data, B (I))
           or else L.Exact_Value (Data, B (I).Held_Total) /= Charge (Data, Rows, P, B (I).Key, L.Held_Capacity, (Present => False))
           or else L.Exact_Value (Data, B (I).Charged_Total) /= Charge (Data, Rows, P, B (I).Key, L.Irreversible_Budget, (Present => False)) then return False; end if;
      end loop;
      return (for all I in B'Range => (for all J in B'Range => (if I < J then not Same_Key (Data, B (I).Key, B (J).Key))))
        and then (for all I in P'Range => (for some J in B'Range => Same_Key (Data, P (I).Key, B (J).Key)));
   end Physical;
   function Contained (Data : Q.Byte_Array; Rows : L.Row_Array; P : Projection_Array) return Boolean is
   begin
      if Rows'Length /= P'Length or else not (for all I in Rows'Range => L.Row_Valid (Data, Rows (I)))
        or else not (for all I in P'Range => L.T.Nonnegative_Valid (Data, P (I).Numerator)
          and then L.T.Nonnegative_Valid (Data, P (I).Denominator)
          and then L.T.Nonnegative_Valid (Data, P (I).Amount)
          and then L.Exact_Value (Data, P (I).Numerator) > To_Big_Integer (0)
          and then L.Exact_Value (Data, P (I).Denominator) > To_Big_Integer (0)) then return False; end if;
      for I in Rows'Range loop
         pragma Loop_Invariant (for all V in Rows'Range => (if V < I then
           (if Rows (V).Parent.Present then (for some J in Rows'Range => J < V
             and then L.Parent_Supports (Data, Rows (J), Rows (V))
             and then Same_Key (Data, P (P'First + (J - Rows'First)).Key, P (P'First + (V - Rows'First)).Key)))
           and then Charge_Reference (Data, Rows, P, Rows'Length, P (P'First + (V - Rows'First)).Key, L.Held_Capacity, Rows (V).Bound.Reservation)
             + Charge_Reference (Data, Rows, P, Rows'Length, P (P'First + (V - Rows'First)).Key, L.Irreversible_Budget, Rows (V).Bound.Reservation)
             <= (Q.Value (Data, Rows (V).Amount) * Q.Value (Data, P (P'First + (V - Rows'First)).Numerator)) /
                      Q.Value (Data, P (P'First + (V - Rows'First)).Denominator)));
         if Rows (I).Parent.Present and then not (for some J in Rows'Range => J < I
           and then L.Parent_Supports (Data, Rows (J), Rows (I))
           and then Same_Key (Data, P (P'First + (J - Rows'First)).Key, P (P'First + (I - Rows'First)).Key)) then return False; end if;
         if Charge (Data, Rows, P, P (P'First + (I - Rows'First)).Key, L.Held_Capacity, Rows (I).Bound.Reservation)
           + Charge (Data, Rows, P, P (P'First + (I - Rows'First)).Key, L.Irreversible_Budget, Rows (I).Bound.Reservation)
           > (L.Exact_Value (Data, Rows (I).Amount) * L.Exact_Value (Data, P (P'First + (I - Rows'First)).Numerator)) /
                    L.Exact_Value (Data, P (P'First + (I - Rows'First)).Denominator) then return False; end if;
      end loop;
      return True;
   end Contained;
   function Classify (Data : Q.Byte_Array; S : State; H : History_Array;
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
      elsif K.Reaped_Holds (Data, Item, F) then L.Reaped else L.Unknown);
   function Valid (Data : Q.Byte_Array; S : State; H : History_Array;
      Rows : L.Row_Array; P : Projection_Array; B : Bucket_Array;
      C : Current_Observation) return Boolean is
     (Shape (Data, S, H, Rows) and then Physical (Data, S, H, Rows, P, B)
      and then Contained (Data, Rows, P) and then Current_Valid (Data, S, H, C));
   function Ordinary_Relation (Data : Q.Byte_Array; Before : State; H : History_Array;
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
      else L.Ready);
   function Check (Data : Q.Byte_Array;
      Before : State; H : History_Array; Rows : L.Row_Array; P : Projection_Array; B : Bucket_Array;
      Proposed : State; PH : History_Array; PR : L.Row_Array; PP : Projection_Array; PB : Bucket_Array;
      Observed : L.Native_Array; F : Facts_Array; Actual : Bucket_Array;
      C : Current_Observation; R : Intent) return Status is
     (if not Shape (Data, Before, H, Rows) then Invalid_Before
      elsif not Shape (Data, Proposed, PH, PR) then Invalid_Proposed
      elsif not Physical (Data, Before, H, Rows, P, B)
        or else not Physical (Data, Proposed, PH, PR, PP, PB) then Physical_Projection_Invalid
      elsif not Bucket_Retained (Data, B, PB) or else not Buckets_Observed (Data, PB, Actual) then Physical_Roster_Invalid
      elsif not Projection_Prefix (Data, P, PP) then Immutable_Origin_Changed
      elsif not Contained (Data, Rows, P) or else not Contained (Data, PR, PP) then Parent_Invalid
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
      else Ready);
end Resource_Scoped_Run_Ledger;
