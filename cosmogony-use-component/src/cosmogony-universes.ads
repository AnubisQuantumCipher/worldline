with Interfaces;
with Cosmogony.Genesis;

package Cosmogony.Universes with SPARK_Mode => On is
   subtype Digest is Cosmogony.Genesis.Digest;
   Zero_Digest : Digest renames Cosmogony.Genesis.Zero_Digest;
   use type Digest;
   use type Cosmogony.Genesis.Decision_Kind;
   use type Interfaces.Unsigned_64;
   use type Interfaces.Unsigned_32;

   --  These digests name canonical, retained descriptors. The boundary that
   --  computes/authenticates a digest is outside this SPARK package.
   type Policy_Bindings is record
      Mission_Id : Digest;
      Authority_Id : Digest;
      Resource_Id : Digest;
      Network_Id : Digest;
      Provider_Id : Digest;
      Evaluator_Id : Digest;
      Root_Set_Id : Digest;
      Evidence_Id : Digest;
      Roster_Id : Digest;
      Worldline_Set_Id : Digest;
   end record;

   type Lifecycle_State is (Genesis, Active, Suspended, Sealed, Archived);

   type Universe_Record is record
      Universe_Id : Digest;
      Parent_Id : Digest;  --  Zero only for a root universe.
      Policy_Epoch : Interfaces.Unsigned_64;
      Policy : Policy_Bindings;
      Prime_Worldline_Id : Digest;
      Prime_Id : Digest;
      Prime_Generation : Interfaces.Unsigned_64;
      Receipt_Head_Id : Digest;
      Life : Lifecycle_State;
      Running_Worlds : Interfaces.Unsigned_32;
      Outstanding_Reservations : Interfaces.Unsigned_32;
      Unresolved_Transactions : Interfaces.Unsigned_32;
      Evidence_Snapshot_Id : Digest;
      Snapshot_Complete : Boolean;
   end record;

   type Evolution_Result is record
      Applied : Boolean;
      Value : Universe_Record;
   end record;

   type Evidence_Binding is record
      Universe_Id : Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Policy : Policy_Bindings;
      Prime_Worldline_Id : Digest;
      Prime_Id : Digest;
      Prime_Generation : Interfaces.Unsigned_64;
   end record;

   type Governance_Stage is
     (Invalid_Universe, Inactive_Universe, Unbound_Genesis,
      Genesis_Decision);
   type Governed_Result is record
      Stage : Governance_Stage;
      Decision : Cosmogony.Genesis.Decision;
   end record;

   function Valid_Policy (P : Policy_Bindings) return Boolean is
     (P.Mission_Id /= Zero_Digest
      and then P.Authority_Id /= Zero_Digest
      and then P.Resource_Id /= Zero_Digest
      and then P.Network_Id /= Zero_Digest
      and then P.Provider_Id /= Zero_Digest
      and then P.Evaluator_Id /= Zero_Digest
      and then P.Root_Set_Id /= Zero_Digest
      and then P.Evidence_Id /= Zero_Digest
      and then P.Roster_Id /= Zero_Digest
      and then P.Worldline_Set_Id /= Zero_Digest);

   function Quiet (U : Universe_Record) return Boolean is
     (U.Running_Worlds = 0
      and then U.Outstanding_Reservations = 0
      and then U.Unresolved_Transactions = 0);

   function Snapshot_Ready (U : Universe_Record) return Boolean is
     (U.Snapshot_Complete and then U.Evidence_Snapshot_Id /= Zero_Digest);

   function Valid (U : Universe_Record) return Boolean is
     (U.Universe_Id /= Zero_Digest
      and then U.Universe_Id /= U.Parent_Id
      and then U.Policy_Epoch /= 0
      and then Valid_Policy (U.Policy)
      and then U.Prime_Worldline_Id /= Zero_Digest
      and then U.Prime_Id /= Zero_Digest
      and then U.Receipt_Head_Id /= Zero_Digest
      and then (not U.Snapshot_Complete
                or else U.Evidence_Snapshot_Id /= Zero_Digest)
      and then (if U.Life = Genesis then
                  U.Policy_Epoch = 1 and then Quiet (U)
                  and then not U.Snapshot_Complete
                  and then U.Evidence_Snapshot_Id = Zero_Digest)
      and then (if U.Life = Suspended then Quiet (U))
      and then (if U.Life in Sealed | Archived
                then Quiet (U) and then Snapshot_Ready (U)));

   function Can_Transition
     (U : Universe_Record; Target : Lifecycle_State) return Boolean is
     (Valid (U)
      and then
        (case U.Life is
            when Genesis   => Target = Active and then Quiet (U),
            when Active    =>
              (Target = Suspended and then Quiet (U))
              or else (Target = Sealed and then Quiet (U)
                       and then Snapshot_Ready (U)),
            when Suspended => Target = Active and then Quiet (U),
            when Sealed    => Target = Archived,
            when Archived  => False));

   function Same_Except_Life
     (Left, Right : Universe_Record) return Boolean is
     (Left.Universe_Id = Right.Universe_Id
      and then Left.Parent_Id = Right.Parent_Id
      and then Left.Policy_Epoch = Right.Policy_Epoch
      and then Left.Policy = Right.Policy
      and then Left.Prime_Worldline_Id = Right.Prime_Worldline_Id
      and then Left.Prime_Id = Right.Prime_Id
      and then Left.Prime_Generation = Right.Prime_Generation
      and then Left.Receipt_Head_Id = Right.Receipt_Head_Id
      and then Left.Running_Worlds = Right.Running_Worlds
      and then Left.Outstanding_Reservations = Right.Outstanding_Reservations
      and then Left.Unresolved_Transactions = Right.Unresolved_Transactions
      and then Left.Evidence_Snapshot_Id = Right.Evidence_Snapshot_Id
      and then Left.Snapshot_Complete = Right.Snapshot_Complete);

   function Transition
     (U : Universe_Record; Target : Lifecycle_State) return Evolution_Result
     with Post =>
       Transition'Result.Applied = Can_Transition (U, Target)
       and then
         (if Transition'Result.Applied then
             Valid (Transition'Result.Value)
             and then Transition'Result.Value.Life = Target
             and then Same_Except_Life (Transition'Result.Value, U)
          else Transition'Result.Value = U);

   --  A security-relevant policy edit is a new immutable epoch. The stable
   --  Universe_Id/Parent_Id survive; old evidence remains bound to its epoch.
   function Can_Revise
     (U : Universe_Record; Proposed : Policy_Bindings) return Boolean is
     (Valid (U)
      and then U.Life = Suspended
      and then Quiet (U)
      and then Valid_Policy (Proposed)
      and then Proposed /= U.Policy
      and then U.Policy_Epoch < Interfaces.Unsigned_64'Last);

   function Same_Except_Revision
     (Left, Right : Universe_Record) return Boolean is
     (Left.Universe_Id = Right.Universe_Id
      and then Left.Parent_Id = Right.Parent_Id
      and then Left.Prime_Worldline_Id = Right.Prime_Worldline_Id
      and then Left.Prime_Id = Right.Prime_Id
      and then Left.Prime_Generation = Right.Prime_Generation
      and then Left.Receipt_Head_Id = Right.Receipt_Head_Id
      and then Left.Life = Right.Life
      and then Left.Running_Worlds = Right.Running_Worlds
      and then Left.Outstanding_Reservations = Right.Outstanding_Reservations
      and then Left.Unresolved_Transactions = Right.Unresolved_Transactions);

   function Revise
     (U : Universe_Record; Proposed : Policy_Bindings) return Evolution_Result
     with Post =>
       Revise'Result.Applied = Can_Revise (U, Proposed)
       and then
         (if Revise'Result.Applied then
             Valid (Revise'Result.Value)
             and then Same_Except_Revision (Revise'Result.Value, U)
             and then Revise'Result.Value.Policy = Proposed
             and then Revise'Result.Value.Policy_Epoch = U.Policy_Epoch + 1
             and then Revise'Result.Value.Evidence_Snapshot_Id = Zero_Digest
             and then not Revise'Result.Value.Snapshot_Complete
          else Revise'Result.Value = U);

   function Can_Capture_Snapshot
     (U : Universe_Record; Snapshot_Id : Digest) return Boolean is
     (Valid (U) and then U.Life = Active and then Quiet (U)
      and then Snapshot_Id /= Zero_Digest);

   function Capture_Snapshot
     (U : Universe_Record; Snapshot_Id : Digest) return Evolution_Result
     with Post =>
       Capture_Snapshot'Result.Applied =
         Can_Capture_Snapshot (U, Snapshot_Id)
       and then
         (if Capture_Snapshot'Result.Applied then
             Valid (Capture_Snapshot'Result.Value)
             and then Capture_Snapshot'Result.Value.Evidence_Snapshot_Id =
               Snapshot_Id
             and then Capture_Snapshot'Result.Value.Snapshot_Complete
             and then Same_Except_Revision
               (Capture_Snapshot'Result.Value, U)
             and then Capture_Snapshot'Result.Value.Policy = U.Policy
             and then Capture_Snapshot'Result.Value.Policy_Epoch =
               U.Policy_Epoch
          else Capture_Snapshot'Result.Value = U);

   --  This records a new observed PRIME after an independent WORLDLINE
   --  authorization/actuation receipt. Authenticating that receipt is external.
   function Can_Advance_Prime
     (U : Universe_Record; Prime_Id : Digest;
      Generation : Interfaces.Unsigned_64; Receipt_Id : Digest)
      return Boolean is
     (Valid (U) and then U.Life = Active and then Quiet (U)
      and then Prime_Id /= Zero_Digest and then Prime_Id /= U.Prime_Id
      and then Generation > U.Prime_Generation
      and then Receipt_Id /= Zero_Digest
      and then Receipt_Id /= U.Receipt_Head_Id);

   function Advance_Prime
     (U : Universe_Record; Prime_Id : Digest;
      Generation : Interfaces.Unsigned_64; Receipt_Id : Digest)
      return Evolution_Result
     with Post =>
       Advance_Prime'Result.Applied =
         Can_Advance_Prime (U, Prime_Id, Generation, Receipt_Id)
       and then
         (if Advance_Prime'Result.Applied then
             Valid (Advance_Prime'Result.Value)
             and then Advance_Prime'Result.Value.Universe_Id = U.Universe_Id
             and then Advance_Prime'Result.Value.Parent_Id = U.Parent_Id
             and then Advance_Prime'Result.Value.Policy = U.Policy
             and then Advance_Prime'Result.Value.Policy_Epoch = U.Policy_Epoch
             and then Advance_Prime'Result.Value.Prime_Worldline_Id =
               U.Prime_Worldline_Id
             and then Advance_Prime'Result.Value.Prime_Id = Prime_Id
             and then Advance_Prime'Result.Value.Prime_Generation = Generation
             and then Advance_Prime'Result.Value.Receipt_Head_Id = Receipt_Id
             and then Advance_Prime'Result.Value.Life = U.Life
             and then Quiet (Advance_Prime'Result.Value)
             and then not Advance_Prime'Result.Value.Snapshot_Complete
             and then Advance_Prime'Result.Value.Evidence_Snapshot_Id =
               Zero_Digest
          else Advance_Prime'Result.Value = U);

   function Bind_Evidence (U : Universe_Record) return Evidence_Binding is
     (Universe_Id => U.Universe_Id,
      Policy_Epoch => U.Policy_Epoch,
      Policy => U.Policy,
      Prime_Worldline_Id => U.Prime_Worldline_Id,
      Prime_Id => U.Prime_Id,
      Prime_Generation => U.Prime_Generation);

   function Evidence_Current
     (U : Universe_Record; B : Evidence_Binding) return Boolean is
     (Valid (U) and then B = Bind_Evidence (U));

   --  In the single-instance genesis topology Prime_Worldline_Id is the
   --  WORLDLINE instance identity supplied to Genesis. Multi-instance
   --  membership and descriptor authenticity remain boundary obligations.
   function Genesis_Binds
     (U : Universe_Record; G : Cosmogony.Genesis.Universe_State)
      return Boolean is
     (G.Universe_Id = U.Universe_Id
      and then G.Mission_Id = U.Policy.Mission_Id
      and then G.Policy_Id = U.Policy.Authority_Id
      and then G.Policy_Owner_Mission = U.Policy.Mission_Id
      and then G.Worldline_Instance_Id = U.Prime_Worldline_Id
      and then G.Root_Set_Id = U.Policy.Root_Set_Id
      and then G.Prime_Id = U.Prime_Id
      and then G.Policy_Epoch = U.Policy_Epoch);

   function Governed_Decide
     (U : Universe_Record; G : Cosmogony.Genesis.Universe_State;
      R : Cosmogony.Genesis.Request) return Governed_Result
     with Post =>
       ((Governed_Decide'Result.Decision.Kind =
           Cosmogony.Genesis.Forward_Worldline)
        =
        (Valid (U) and then U.Life = Active
         and then Genesis_Binds (U, G)
         and then Cosmogony.Genesis.Eligible (G, R)
         and then Cosmogony.Genesis.Is_Forwardable (R.Action)))
       and then
         (if Governed_Decide'Result.Stage /= Genesis_Decision then
             Governed_Decide'Result.Decision.Kind =
               Cosmogony.Genesis.Denied);
end Cosmogony.Universes;
