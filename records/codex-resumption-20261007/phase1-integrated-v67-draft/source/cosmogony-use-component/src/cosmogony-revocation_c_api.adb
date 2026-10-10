with Cosmogony.Capabilities;
with Cosmogony.Genesis;
with Cosmogony.Revocable_Capabilities;
with System;

package body Cosmogony.Revocation_C_API with SPARK_Mode => Off is
   use Cosmogony.Capabilities;
   use Cosmogony.Genesis;
   use Cosmogony.Revocable_Capabilities;
   use type Interfaces.C.int;
   use type Interfaces.Unsigned_64;
   use type Cosmogony.C_API.C_Digest;
   use type Cosmogony.Capability_C_API.C_Capability;

   function To_Digest (D : Cosmogony.C_API.C_Digest) return Digest is
     (1 => D (0), 2 => D (1), 3 => D (2), 4 => D (3));

   function To_State (U : Cosmogony.C_API.C_Universe)
      return Universe_State
   is
      State : Universe_State;
   begin
      State.Universe_Id := To_Digest (U.Universe_Id);
      State.Mission_Id := To_Digest (U.Mission_Id);
      State.Policy_Id := To_Digest (U.Policy_Id);
      State.Policy_Owner_Mission := To_Digest (U.Policy_Owner_Mission);
      State.Worldline_Instance_Id := To_Digest (U.Worldline_Instance_Id);
      State.Root_Set_Id := To_Digest (U.Root_Set_Id);
      State.Prime_Id := To_Digest (U.Prime_Id);
      State.Policy_Epoch := U.Policy_Epoch;
      State.Budget :=
        (World_Limit => U.World_Limit,
         Worlds_Reserved => U.Worlds_Reserved,
         Evaluation_Limit => U.Evaluation_Limit,
         Evaluations_Reserved => U.Evaluations_Reserved);
      State.Roster_Count := Agent_Count (U.Roster_Count);
      for I in State.Roster'Range loop
         State.Roster (I) :=
           (Identity => To_Digest (U.Roster (Interfaces.C.int (I) - 1).Identity),
            Role => Agent_Role'Val (U.Roster (Interfaces.C.int (I) - 1).Role),
            Enabled => U.Roster (Interfaces.C.int (I) - 1).Enabled = 1);
      end loop;
      return State;
   end To_State;

   function To_Capability
     (Input : Cosmogony.Capability_C_API.C_Capability) return Capability
   is
      Cap : Capability := Null_Capability;
   begin
      Cap.Capability_Id := To_Digest (Input.Capability_Id);
      Cap.Parent_Id := To_Digest (Input.Parent_Id);
      Cap.Universe_Id := To_Digest (Input.Universe_Id);
      Cap.Mission_Id := To_Digest (Input.Mission_Id);
      Cap.Policy_Id := To_Digest (Input.Policy_Id);
      Cap.Authority_Id := To_Digest (Input.Authority_Id);
      Cap.Worldline_Instance_Id := To_Digest (Input.Worldline_Instance_Id);
      Cap.Root_Set_Id := To_Digest (Input.Root_Set_Id);
      Cap.Prime_Id := To_Digest (Input.Prime_Id);
      Cap.Subject_Id := To_Digest (Input.Subject_Id);
      Cap.Issuer_Id := To_Digest (Input.Issuer_Id);
      Cap.Policy_Epoch := Input.Policy_Epoch;
      Cap.Issued_At := Input.Issued_At;
      Cap.Expires_At := Input.Expires_At;
      Cap.Terminal := Input.Terminal = 1;
      for I in Cap.Granted'Range loop
         Cap.Granted (I) :=
           Input.Granted (Interfaces.C.int (Operation'Pos (I))) = 1;
      end loop;
      Cap.Applies_To :=
        (Kind => Scope_Kind'Val (Input.Applies_To.Kind),
         World_Id => To_Digest (Input.Applies_To.World_Id));
      Cap.Ceiling :=
        (Worlds => Input.Ceiling.Worlds,
         Evaluations => Input.Ceiling.Evaluations);
      return Cap;
   end To_Capability;

   function To_Request
     (Input : Cosmogony.Capability_C_API.C_Check_Input)
      return Scoped_Request
   is
   begin
      return
        (Ask =>
           (Request_Id => To_Digest (Input.Ask.Request_Id),
            Universe_Id => To_Digest (Input.Ask.Universe_Id),
            Mission_Id => To_Digest (Input.Ask.Mission_Id),
            Policy_Id => To_Digest (Input.Ask.Policy_Id),
            Worldline_Instance_Id =>
              To_Digest (Input.Ask.Worldline_Instance_Id),
            Root_Set_Id => To_Digest (Input.Ask.Root_Set_Id),
            Prime_Id => To_Digest (Input.Ask.Prime_Id),
            Policy_Epoch => Input.Ask.Policy_Epoch,
            Actor_Id => To_Digest (Input.Ask.Actor_Id),
            Action => Operation'Val (Input.Ask.Action)),
         Target_World_Id => To_Digest (Input.Target_World_Id));
   end To_Request;

   function Canonical_Grant
     (Input : Cosmogony.Capability_C_API.C_Capability) return Boolean
   is
   begin
      if Input.Terminal not in 0 .. 1
        or else Input.Applies_To.Kind not in 0 .. 1
      then
         return False;
      end if;
      for I in Input.Granted'Range loop
         if Input.Granted (I) not in 0 .. 1 then
            return False;
         end if;
      end loop;
      return True;
   end Canonical_Grant;

   function ABI_Version return Interfaces.C.int is (1);
   function Link_Bytes return Interfaces.C.int is
     (C_Link'Object_Size / System.Storage_Unit);
   function Lineage_Bytes return Interfaces.C.int is
     (C_Lineage'Object_Size / System.Storage_Unit);

   function Check_C
     (U : access constant Cosmogony.Universe_C_API.C_Record;
      G : access constant Cosmogony.C_API.C_Universe;
      Input : access constant Cosmogony.Capability_C_API.C_Check_Input;
      Chain : access constant C_Lineage;
      D : access Cosmogony.Capability_C_API.C_Check_Decision)
      return Interfaces.C.int
   is
      Links : Lineage :=
        (others => (Grant => Null_Capability, Revoked => False));
      Result : Check_Decision;
   begin
      if D = null then
         return -1;
      end if;
      D.all := (Kind => Check_Kind'Pos (Refused),
                Reason => Check_Reason'Pos (Invalid_Ancestry));
      if U = null or else G = null or else Input = null or else Chain = null
        or else Chain.Count not in 1 .. 8
        or else G.Roster_Count not in 0 .. 8
        or else Input.Ask.Action not in 0 .. Operation'Pos (Operation'Last)
        or else U.Life not in 0 .. 4
        or else U.Snapshot_Complete not in 0 .. 1
      then
         return -1;
      end if;
      for I in G.Roster'Range loop
         if G.Roster (I).Role not in 0 .. Agent_Role'Pos (Agent_Role'Last)
           or else G.Roster (I).Enabled not in 0 .. 1
         then
            return -1;
         end if;
      end loop;
      for I in 1 .. Chain.Count loop
         if Chain.Links (I - 1).Revoked not in 0 .. 1
           or else not Canonical_Grant (Chain.Links (I - 1).Grant)
         then
            return -1;
         end if;
         Links (Link_Index (I)) :=
           (Grant => To_Capability (Chain.Links (I - 1).Grant),
            Revoked => Chain.Links (I - 1).Revoked = 1);
      end loop;
      if not Canonical_Grant (Input.Grant)
        or else Input.Authority_Id (0) /= U.Policy.Authority_Id (0)
        or else Input.Authority_Id (1) /= U.Policy.Authority_Id (1)
        or else Input.Authority_Id (2) /= U.Policy.Authority_Id (2)
        or else Input.Authority_Id (3) /= U.Policy.Authority_Id (3)
        or else Input.Grant /= Chain.Links (Chain.Count - 1).Grant
      then
         return -1;
      end if;
      Result := Cosmogony.Revocable_Capabilities.Check_Request
        (Cosmogony.Universe_C_API.To_Record (U.all), To_State (G.all),
         Links, Link_Count (Chain.Count), To_Request (Input.all),
         (Worlds => Input.Usage.Worlds,
          Evaluations => Input.Usage.Evaluations), Input.Now_Tick);
      D.all := (Kind => Check_Kind'Pos (Result.Kind),
                Reason => Check_Reason'Pos (Result.Reason));
      return 0;
   end Check_C;
end Cosmogony.Revocation_C_API;
