with Cosmogony.Universes;
with System;

package body Cosmogony.Universe_C_API with SPARK_Mode => Off is
   use Cosmogony.Universes;
   use type Interfaces.C.int;

   function To_Digest (D : C_Digest) return Digest is
     (1 => D (0), 2 => D (1), 3 => D (2), 4 => D (3));

   function From_Digest (D : Digest) return C_Digest is
     (0 => D (1), 1 => D (2), 2 => D (3), 3 => D (4));

   function To_Policy (P : C_Policy) return Policy_Bindings is
     (Mission_Id => To_Digest (P.Mission_Id),
      Authority_Id => To_Digest (P.Authority_Id),
      Resource_Id => To_Digest (P.Resource_Id),
      Network_Id => To_Digest (P.Network_Id),
      Provider_Id => To_Digest (P.Provider_Id),
      Evaluator_Id => To_Digest (P.Evaluator_Id),
      Root_Set_Id => To_Digest (P.Root_Set_Id),
      Evidence_Id => To_Digest (P.Evidence_Id),
      Roster_Id => To_Digest (P.Roster_Id),
      Worldline_Set_Id => To_Digest (P.Worldline_Set_Id));

   function From_Policy (P : Policy_Bindings) return C_Policy is
     (Mission_Id => From_Digest (P.Mission_Id),
      Authority_Id => From_Digest (P.Authority_Id),
      Resource_Id => From_Digest (P.Resource_Id),
      Network_Id => From_Digest (P.Network_Id),
      Provider_Id => From_Digest (P.Provider_Id),
      Evaluator_Id => From_Digest (P.Evaluator_Id),
      Root_Set_Id => From_Digest (P.Root_Set_Id),
      Evidence_Id => From_Digest (P.Evidence_Id),
      Roster_Id => From_Digest (P.Roster_Id),
      Worldline_Set_Id => From_Digest (P.Worldline_Set_Id));

   function To_Record (U : C_Record) return Universe_Record is
     (Universe_Id => To_Digest (U.Universe_Id),
      Parent_Id => To_Digest (U.Parent_Id),
      Policy_Epoch => U.Policy_Epoch,
      Policy => To_Policy (U.Policy),
      Prime_Worldline_Id => To_Digest (U.Prime_Worldline_Id),
      Prime_Id => To_Digest (U.Prime_Id),
      Prime_Generation => U.Prime_Generation,
      Receipt_Head_Id => To_Digest (U.Receipt_Head_Id),
      Life => Lifecycle_State'Val (U.Life),
      Running_Worlds => U.Running_Worlds,
      Outstanding_Reservations => U.Outstanding_Reservations,
      Unresolved_Transactions => U.Unresolved_Transactions,
      Evidence_Snapshot_Id => To_Digest (U.Evidence_Snapshot_Id),
      Snapshot_Complete => U.Snapshot_Complete = 1);

   function From_Record (U : Universe_Record) return C_Record is
     (Universe_Id => From_Digest (U.Universe_Id),
      Parent_Id => From_Digest (U.Parent_Id),
      Policy_Epoch => U.Policy_Epoch,
      Policy => From_Policy (U.Policy),
      Prime_Worldline_Id => From_Digest (U.Prime_Worldline_Id),
      Prime_Id => From_Digest (U.Prime_Id),
      Prime_Generation => U.Prime_Generation,
      Receipt_Head_Id => From_Digest (U.Receipt_Head_Id),
      Life => Lifecycle_State'Pos (U.Life),
      Running_Worlds => U.Running_Worlds,
      Outstanding_Reservations => U.Outstanding_Reservations,
      Unresolved_Transactions => U.Unresolved_Transactions,
      Evidence_Snapshot_Id => From_Digest (U.Evidence_Snapshot_Id),
      Snapshot_Complete => (if U.Snapshot_Complete then 1 else 0));

   function From_Evolution (E : Evolution_Result) return C_Evolution is
     (Applied => (if E.Applied then 1 else 0),
      Value => From_Record (E.Value));

   function From_Evidence (E : Evidence_Binding) return C_Evidence is
     (Universe_Id => From_Digest (E.Universe_Id),
      Policy_Epoch => E.Policy_Epoch,
      Policy => From_Policy (E.Policy),
      Prime_Worldline_Id => From_Digest (E.Prime_Worldline_Id),
      Prime_Id => From_Digest (E.Prime_Id),
      Prime_Generation => E.Prime_Generation);

   function To_Evidence (E : C_Evidence) return Evidence_Binding is
     (Universe_Id => To_Digest (E.Universe_Id),
      Policy_Epoch => E.Policy_Epoch,
      Policy => To_Policy (E.Policy),
      Prime_Worldline_Id => To_Digest (E.Prime_Worldline_Id),
      Prime_Id => To_Digest (E.Prime_Id),
      Prime_Generation => E.Prime_Generation);

   function Canonical_C (U : C_Record) return Boolean is
     (U.Life in 0 .. Lifecycle_State'Pos (Lifecycle_State'Last)
      and then U.Snapshot_Complete in 0 .. 1);

   function ABI_Version return Interfaces.C.int is (1);
   function Record_Bytes return Interfaces.C.int is
     (C_Record'Object_Size / System.Storage_Unit);
   function Policy_Bytes return Interfaces.C.int is
     (C_Policy'Object_Size / System.Storage_Unit);
   function Evolution_Bytes return Interfaces.C.int is
     (C_Evolution'Object_Size / System.Storage_Unit);
   function Evidence_Bytes return Interfaces.C.int is
     (C_Evidence'Object_Size / System.Storage_Unit);

   function Valid_C (U : access constant C_Record) return Interfaces.C.int is
   begin
      if U = null or else not Canonical_C (U.all) then
         return -1;
      end if;
      return (if Valid (To_Record (U.all)) then 1 else 0);
   end Valid_C;

   function Transition_C
     (U : access constant C_Record; Target : Interfaces.C.int;
      Result : access C_Evolution) return Interfaces.C.int
   is
   begin
      if U = null or else Result = null or else not Canonical_C (U.all)
        or else Target not in 0 .. Lifecycle_State'Pos (Lifecycle_State'Last)
      then
         return -1;
      end if;
      Result.all := From_Evolution
        (Transition (To_Record (U.all), Lifecycle_State'Val (Target)));
      return 0;
   end Transition_C;

   function Revise_C
     (U : access constant C_Record; Proposed : access constant C_Policy;
      Result : access C_Evolution) return Interfaces.C.int
   is
   begin
      if U = null or else Proposed = null or else Result = null
        or else not Canonical_C (U.all)
      then
         return -1;
      end if;
      Result.all := From_Evolution
        (Revise (To_Record (U.all), To_Policy (Proposed.all)));
      return 0;
   end Revise_C;

   function Capture_Snapshot_C
     (U : access constant C_Record; Snapshot_Id : access constant C_Digest;
      Result : access C_Evolution) return Interfaces.C.int
   is
   begin
      if U = null or else Snapshot_Id = null or else Result = null
        or else not Canonical_C (U.all)
      then
         return -1;
      end if;
      Result.all := From_Evolution
        (Capture_Snapshot (To_Record (U.all), To_Digest (Snapshot_Id.all)));
      return 0;
   end Capture_Snapshot_C;

   function Advance_Prime_C
     (U : access constant C_Record; Prime_Id : access constant C_Digest;
      Generation : Interfaces.Unsigned_64;
      Receipt_Id : access constant C_Digest;
      Result : access C_Evolution) return Interfaces.C.int
   is
   begin
      if U = null or else Prime_Id = null or else Receipt_Id = null
        or else Result = null or else not Canonical_C (U.all)
      then
         return -1;
      end if;
      Result.all := From_Evolution
        (Advance_Prime (To_Record (U.all), To_Digest (Prime_Id.all),
                        Generation, To_Digest (Receipt_Id.all)));
      return 0;
   end Advance_Prime_C;

   function Bind_Evidence_C
     (U : access constant C_Record; Bound : access C_Evidence)
      return Interfaces.C.int
   is
   begin
      if U = null or else Bound = null or else not Canonical_C (U.all) then
         return -1;
      end if;
      Bound.all := From_Evidence (Bind_Evidence (To_Record (U.all)));
      return 0;
   end Bind_Evidence_C;

   function Evidence_Current_C
     (U : access constant C_Record; Bound : access constant C_Evidence)
      return Interfaces.C.int
   is
   begin
      if U = null or else Bound = null or else not Canonical_C (U.all) then
         return -1;
      end if;
      return (if Evidence_Current
        (To_Record (U.all), To_Evidence (Bound.all)) then 1 else 0);
   end Evidence_Current_C;
end Cosmogony.Universe_C_API;
