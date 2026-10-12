with Interfaces;
with Cosmogony.Genesis;
with Cosmogony.Capabilities;
with Cosmogony.Universes;
with Cosmogony.Revocable_Capabilities;
package Cosmogony.Use_Reservations with SPARK_Mode => On is
   use Cosmogony.Genesis;
   use type Interfaces.Unsigned_32;
   use type Interfaces.Unsigned_64;
   use type Cosmogony.Capabilities.Check_Kind;
   use type Cosmogony.Capabilities.Capability;
   package C renames Cosmogony.Capabilities;
   package R renames Cosmogony.Revocable_Capabilities;
   type Use_State is (Reserved, Consumed, Released);
   type Row_Kind is (Legacy_Charged_Use, Bound_Reservation);
   type Command is (Reserve_Use, Consume_Use, Release_Use);
   type Status is (Refused, Reserved_New, Reserved_Replay,
                   Consumed_New, Consumed_Replay, Released_New, Released_Replay);
   type Binding is record
      Capability_Id, Operation_Id, Transaction_Id, Requester_Id,
        Universe_Head, Request_Identity, Grant_Use_Identity,
        Recovery_Binding_Identity : Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Action : Operation;
   end record;
   function Complete (B : Binding) return Boolean is
     (B.Capability_Id /= Zero_Digest and then B.Operation_Id /= Zero_Digest
      and then B.Transaction_Id /= Zero_Digest and then B.Requester_Id /= Zero_Digest
      and then B.Universe_Head /= Zero_Digest and then B.Request_Identity /= Zero_Digest
      and then B.Grant_Use_Identity /= Zero_Digest
      and then B.Recovery_Binding_Identity /= Zero_Digest and then B.Policy_Epoch /= 0)
     with Global => null;
   type Row is record
      Kind : Row_Kind;
      State : Use_State;
      Bound : Binding;
      Links : R.Lineage;
      Link_Count : R.Link_Count;
   end record;
   type Rows is array (Positive range <>) of Row;
   type Grant_Rows is array (Positive range <>) of C.Capability;
   function Grants_Valid (Grants : Grant_Rows) return Boolean is
     (Grants'First = 1 and then (for all I in Grants'Range =>
        C.Well_Formed (Grants (I))
        and then (for all J in Grants'First .. I - 1 =>
          Grants (J).Capability_Id /= Grants (I).Capability_Id)
        and then (Grants (I).Parent_Id = Zero_Digest
          or else (for some J in Grants'First .. I - 1 =>
            C.Attenuates (Grants (J), Grants (I)))))) with Global => null;
   function Canonical_Roster (Data : Rows; Grants : Grant_Rows;
                             Links : R.Lineage; Link_Count : R.Link_Count)
      return Boolean is
     (Grants_Valid (Grants)
      and then (for all I in Data'Range =>
        (for all J in 1 .. Data (I).Link_Count =>
          (for some K in Grants'Range => Grants (K) = Data (I).Links (J).Grant)))
      and then (for all J in 1 .. Link_Count =>
        (for some K in Grants'Range => Grants (K) = Links (J).Grant))) with Global => null;
   --  All historical uses and all outstanding intents, including released rows,
   --  remain in this roster. No caller-precomputed usage counter is admitted.
   function Row_Valid (Item : Row) return Boolean is
     (Item.Link_Count > 0
      and then Item.Bound.Capability_Id = Item.Links (Item.Link_Count).Grant.Capability_Id
      and then Item.Bound.Operation_Id /= Zero_Digest
      and then Item.Bound.Transaction_Id /= Zero_Digest
      and then Item.Bound.Requester_Id = Item.Links (Item.Link_Count).Grant.Subject_Id
      and then Item.Bound.Universe_Head /= Zero_Digest
      and then Item.Bound.Policy_Epoch = Item.Links (Item.Link_Count).Grant.Policy_Epoch
      and then Item.Links (Item.Link_Count).Grant.Granted (Item.Bound.Action)
      and then Item.Links (1).Grant.Parent_Id = Zero_Digest
      and then R.Distinct_Ids (Item.Links, Item.Link_Count)
      and then (for all I in 1 .. Item.Link_Count => C.Well_Formed (Item.Links (I).Grant)
        and then (if I > 1 then C.Attenuates (Item.Links (I - 1).Grant, Item.Links (I).Grant)))
      and then (if Item.Kind = Legacy_Charged_Use then Item.State = Consumed
                else Complete (Item.Bound))) with Global => null;
   function Roster_Valid (Data : Rows) return Boolean is
     (Data'First = 1 and then (for all I in Data'Range => Row_Valid (Data (I)))
      and then (for all I in Data'Range => (for all J in Data'Range =>
        (if J < I then Data (I).Bound.Operation_Id /= Data (J).Bound.Operation_Id))))
     with Global => null;
   function Charges (Item : Row; Grant_Id : Digest; Purpose : Operation;
                     Exclude_Operation : Digest) return Boolean is
     (Item.State /= Released and then Item.Bound.Operation_Id /= Exclude_Operation
      and then Item.Bound.Action = Purpose
      and then (for some I in 1 .. Item.Link_Count =>
        Item.Links (I).Grant.Capability_Id = Grant_Id)) with Global => null;
   type Counter is record
      Valid : Boolean;
      Value : Interfaces.Unsigned_32;
   end record;
   function Step (Before : Counter; Charged : Boolean) return Counter is
     (if not Charged or else not Before.Valid then Before
      elsif Before.Value = Interfaces.Unsigned_32'Last then (False, Before.Value)
      else (True, Before.Value + 1)) with Global => null;
   function Count_Reference
     (Data : Rows; Prefix : Natural; Grant_Id : Digest; Purpose : Operation;
      Exclude_Operation : Digest; Base : Interfaces.Unsigned_32) return Counter
     with Global => null, Pre => Data'First = 1 and then Prefix <= Data'Length,
       Subprogram_Variant => (Decreases => Prefix);
   function Count
     (Data : Rows; Grant_Id : Digest; Purpose : Operation;
      Exclude_Operation : Digest; Base : Interfaces.Unsigned_32) return Counter
     with Global => null, Pre => Data'First = 1,
       Post => Count'Result = Count_Reference
         (Data, Data'Length, Grant_Id, Purpose, Exclude_Operation, Base);
   function Existing (Data : Rows; Operation_Id : Digest) return Natural
     with Global => null, Pre => Roster_Valid (Data),
       Post => (if Existing'Result = 0 then
         (for all I in Data'Range => Data (I).Bound.Operation_Id /= Operation_Id)
         else Existing'Result in Data'Range
           and then Data (Existing'Result).Bound.Operation_Id = Operation_Id);
   --  Counts every descendant use/held intent against each ancestor ceiling;
   --  attenuation cannot be amplified by concurrent siblings. Original U32
   --  grant ceilings/U64 policy epochs and original lineage domain are retained.
   function Capacity_Reference
     (Data : Rows; Links : R.Lineage; Link_Count : R.Link_Count;
      Exclude_Operation : Digest; Base : C.Resource_Usage; Action : Operation)
      return Boolean is
     (Link_Count > 0 and then (for all I in 1 .. Link_Count =>
        Count_Reference (Data, Data'Length, Links (I).Grant.Capability_Id,
          Create_World, Exclude_Operation, Base.Worlds).Valid
        and then Count_Reference (Data, Data'Length, Links (I).Grant.Capability_Id,
          Evaluate_World, Exclude_Operation, Base.Evaluations).Valid
        and then C.Usage_Valid (Links (I).Grant,
          (Count_Reference (Data, Data'Length, Links (I).Grant.Capability_Id,
             Create_World, Exclude_Operation, Base.Worlds).Value,
           Count_Reference (Data, Data'Length, Links (I).Grant.Capability_Id,
             Evaluate_World, Exclude_Operation, Base.Evaluations).Value))
        and then C.Has_Grant_Capacity (Links (I).Grant,
          (Count_Reference (Data, Data'Length, Links (I).Grant.Capability_Id,
             Create_World, Exclude_Operation, Base.Worlds).Value,
           Count_Reference (Data, Data'Length, Links (I).Grant.Capability_Id,
             Evaluate_World, Exclude_Operation, Base.Evaluations).Value), Action)))
     with Global => null, Pre => Data'First = 1;
   function Capacity
     (Data : Rows; Links : R.Lineage; Link_Count : R.Link_Count;
      Exclude_Operation : Digest; Base : C.Resource_Usage; Action : Operation)
      return Boolean
     with Global => null, Pre => Data'First = 1,
       Post => Capacity'Result = Capacity_Reference
         (Data, Links, Link_Count, Exclude_Operation, Base, Action);
   function Fresh_Eligible_Reference
     (Data : Rows; U : Cosmogony.Universes.Universe_Record; G : Universe_State;
      Links : R.Lineage; Link_Count : R.Link_Count; Q : C.Scoped_Request;
      Base : C.Resource_Usage; Now_Tick : Interfaces.Unsigned_64; Bound : Binding)
      return Boolean is
     (Roster_Valid (Data) and then Complete (Bound) and then Link_Count > 0
      and then Bound.Capability_Id = Links (Link_Count).Grant.Capability_Id
      and then Bound.Operation_Id = Q.Ask.Request_Id
      and then Bound.Requester_Id = Q.Ask.Actor_Id
      and then Bound.Policy_Epoch = Q.Ask.Policy_Epoch
      and then Bound.Action = Q.Ask.Action
      and then Capacity_Reference (Data, Links, Link_Count, Bound.Operation_Id, Base, Q.Ask.Action)
      and then R.Check_Request (U, G, Links, Link_Count, Q,
        (Count_Reference (Data, Data'Length, Bound.Capability_Id,
           Create_World, Bound.Operation_Id, Base.Worlds).Value,
         Count_Reference (Data, Data'Length, Bound.Capability_Id,
           Evaluate_World, Bound.Operation_Id, Base.Evaluations).Value), Now_Tick).Kind
           /= C.Refused) with Global => null;
   function Fresh_Eligible
     (Data : Rows; U : Cosmogony.Universes.Universe_Record; G : Universe_State;
      Links : R.Lineage; Link_Count : R.Link_Count; Q : C.Scoped_Request;
      Base : C.Resource_Usage; Now_Tick : Interfaces.Unsigned_64; Bound : Binding)
      return Boolean
     with Global => null, Post => Fresh_Eligible'Result = Fresh_Eligible_Reference
       (Data, U, G, Links, Link_Count, Q, Base, Now_Tick, Bound);
   function Reference
     (Data : Rows; Grants : Grant_Rows; U : Cosmogony.Universes.Universe_Record; G : Universe_State;
      Links : R.Lineage; Link_Count : R.Link_Count; Q : C.Scoped_Request;
      Base : C.Resource_Usage; Now_Tick : Interfaces.Unsigned_64;
      Bound : Binding; Mode : Command) return Status is
     (if not Roster_Valid (Data) or else not Complete (Bound)
        or else not Canonical_Roster (Data, Grants, Links, Link_Count) then Refused
      elsif Existing (Data, Bound.Operation_Id) /= 0 and then
        (Data (Existing (Data, Bound.Operation_Id)).Kind /= Bound_Reservation
         or else Data (Existing (Data, Bound.Operation_Id)).Bound /= Bound) then Refused
      elsif Mode = Reserve_Use then
        (if (Existing (Data, Bound.Operation_Id) /= 0 and then
             Data (Existing (Data, Bound.Operation_Id)).State /= Reserved)
          or else not Fresh_Eligible_Reference
            (Data, U, G, Links, Link_Count, Q, Base, Now_Tick, Bound) then Refused
         elsif Existing (Data, Bound.Operation_Id) = 0 then Reserved_New else Reserved_Replay)
      elsif Existing (Data, Bound.Operation_Id) = 0 then Refused
      elsif Mode = Consume_Use then
        (if Data (Existing (Data, Bound.Operation_Id)).State = Released then Refused
         elsif Data (Existing (Data, Bound.Operation_Id)).State = Reserved then Consumed_New
         else Consumed_Replay)
      else
        (if Data (Existing (Data, Bound.Operation_Id)).State = Consumed then Refused
         elsif Data (Existing (Data, Bound.Operation_Id)).State = Reserved then Released_New
         else Released_Replay)) with Global => null;
   function Check
     (Data : Rows; Grants : Grant_Rows; U : Cosmogony.Universes.Universe_Record; G : Universe_State;
      Links : R.Lineage; Link_Count : R.Link_Count; Q : C.Scoped_Request;
      Base : C.Resource_Usage; Now_Tick : Interfaces.Unsigned_64;
      Bound : Binding; Mode : Command) return Status
     with Global => null,
       Post => Check'Result = Reference
         (Data, Grants, U, G, Links, Link_Count, Q, Base, Now_Tick, Bound, Mode);
   --  Consume/Release carry no fresh-grant predicate. The protected caller must
   --  establish authenticated historical effect/no-effect using the full native
   --  recovery packet and exact operation before selecting that command.
   --  This pure relation neither authenticates custody nor authorizes exchange.
end Cosmogony.Use_Reservations;
