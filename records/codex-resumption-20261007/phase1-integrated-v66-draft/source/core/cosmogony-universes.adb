package body Cosmogony.Universes with SPARK_Mode => On is
   function Transition
     (U : Universe_Record; Target : Lifecycle_State) return Evolution_Result
   is
      Next : Universe_Record := U;
   begin
      if not Can_Transition (U, Target) then
         return (Applied => False, Value => U);
      end if;
      Next.Life := Target;
      return (Applied => True, Value => Next);
   end Transition;

   function Revise
     (U : Universe_Record; Proposed : Policy_Bindings) return Evolution_Result
   is
      Next : Universe_Record := U;
   begin
      if not Can_Revise (U, Proposed) then
         return (Applied => False, Value => U);
      end if;
      Next.Policy := Proposed;
      Next.Policy_Epoch := U.Policy_Epoch + 1;
      Next.Evidence_Snapshot_Id := Zero_Digest;
      Next.Snapshot_Complete := False;
      return (Applied => True, Value => Next);
   end Revise;

   function Capture_Snapshot
     (U : Universe_Record; Snapshot_Id : Digest) return Evolution_Result
   is
      Next : Universe_Record := U;
   begin
      if not Can_Capture_Snapshot (U, Snapshot_Id) then
         return (Applied => False, Value => U);
      end if;
      Next.Evidence_Snapshot_Id := Snapshot_Id;
      Next.Snapshot_Complete := True;
      return (Applied => True, Value => Next);
   end Capture_Snapshot;

   function Advance_Prime
     (U : Universe_Record; Prime_Id : Digest;
      Generation : Interfaces.Unsigned_64; Receipt_Id : Digest)
      return Evolution_Result
   is
      Next : Universe_Record := U;
   begin
      if not Can_Advance_Prime (U, Prime_Id, Generation, Receipt_Id) then
         return (Applied => False, Value => U);
      end if;
      Next.Prime_Id := Prime_Id;
      Next.Prime_Generation := Generation;
      Next.Receipt_Head_Id := Receipt_Id;
      Next.Evidence_Snapshot_Id := Zero_Digest;
      Next.Snapshot_Complete := False;
      return (Applied => True, Value => Next);
   end Advance_Prime;

   function Governed_Decide
     (U : Universe_Record; G : Cosmogony.Genesis.Universe_State;
      R : Cosmogony.Genesis.Request) return Governed_Result
   is
      Denial : constant Cosmogony.Genesis.Decision :=
        (Kind => Cosmogony.Genesis.Denied,
         Reason => Cosmogony.Genesis.Invalid_Genesis);
   begin
      if not Valid (U) then
         return (Stage => Invalid_Universe, Decision => Denial);
      elsif U.Life /= Active then
         return (Stage => Inactive_Universe, Decision => Denial);
      elsif not Genesis_Binds (U, G) then
         return (Stage => Unbound_Genesis, Decision => Denial);
      else
         return (Stage => Genesis_Decision,
                 Decision => Cosmogony.Genesis.Decide (G, R));
      end if;
   end Governed_Decide;
end Cosmogony.Universes;
