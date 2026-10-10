with Cosmogony.Capabilities;
with Cosmogony.Genesis;

package body Cosmogony.Capability_C_API with SPARK_Mode => Off is
   use Cosmogony.Capabilities;
   use Cosmogony.Genesis;
   use type Interfaces.C.int;

   function To_Digest (Value : C_Digest) return Digest is
     (1 => Value (0), 2 => Value (1), 3 => Value (2), 4 => Value (3));

   function From_Digest (Value : Digest) return C_Digest is
     (0 => Value (1), 1 => Value (2), 2 => Value (3), 3 => Value (4));

   function Canonical_C (C : C_Capability) return Boolean is
   begin
      if C.Terminal not in 0 .. 1
        or else C.Applies_To.Kind not in 0 .. 1
      then
         return False;
      end if;
      for I in C.Granted'Range loop
         if C.Granted (I) not in 0 .. 1 then
            return False;
         end if;
      end loop;
      return True;
   end Canonical_C;

   function To_Capability (C : C_Capability) return Capability is
      Cap : Capability := Null_Capability;
   begin
      Cap.Capability_Id := To_Digest (C.Capability_Id);
      Cap.Parent_Id := To_Digest (C.Parent_Id);
      Cap.Universe_Id := To_Digest (C.Universe_Id);
      Cap.Mission_Id := To_Digest (C.Mission_Id);
      Cap.Policy_Id := To_Digest (C.Policy_Id);
      Cap.Authority_Id := To_Digest (C.Authority_Id);
      Cap.Worldline_Instance_Id := To_Digest (C.Worldline_Instance_Id);
      Cap.Root_Set_Id := To_Digest (C.Root_Set_Id);
      Cap.Prime_Id := To_Digest (C.Prime_Id);
      Cap.Subject_Id := To_Digest (C.Subject_Id);
      Cap.Issuer_Id := To_Digest (C.Issuer_Id);
      Cap.Policy_Epoch := C.Policy_Epoch;
      Cap.Issued_At := C.Issued_At;
      Cap.Expires_At := C.Expires_At;
      Cap.Terminal := C.Terminal = 1;
      for I in Cap.Granted'Range loop
         Cap.Granted (I) :=
           C.Granted (Interfaces.C.int (Operation'Pos (I))) = 1;
      end loop;
      Cap.Applies_To :=
        (Kind => Scope_Kind'Val (C.Applies_To.Kind),
         World_Id => To_Digest (C.Applies_To.World_Id));
      Cap.Ceiling :=
        (Worlds => C.Ceiling.Worlds,
         Evaluations => C.Ceiling.Evaluations);
      return Cap;
   end To_Capability;

   function From_Capability (C : Capability) return C_Capability is
      Result : C_Capability;
   begin
      Result.Capability_Id := From_Digest (C.Capability_Id);
      Result.Parent_Id := From_Digest (C.Parent_Id);
      Result.Universe_Id := From_Digest (C.Universe_Id);
      Result.Mission_Id := From_Digest (C.Mission_Id);
      Result.Policy_Id := From_Digest (C.Policy_Id);
      Result.Authority_Id := From_Digest (C.Authority_Id);
      Result.Worldline_Instance_Id := From_Digest (C.Worldline_Instance_Id);
      Result.Root_Set_Id := From_Digest (C.Root_Set_Id);
      Result.Prime_Id := From_Digest (C.Prime_Id);
      Result.Subject_Id := From_Digest (C.Subject_Id);
      Result.Issuer_Id := From_Digest (C.Issuer_Id);
      Result.Policy_Epoch := C.Policy_Epoch;
      Result.Issued_At := C.Issued_At;
      Result.Expires_At := C.Expires_At;
      Result.Terminal := (if C.Terminal then 1 else 0);
      for I in C.Granted'Range loop
         Result.Granted (Interfaces.C.int (Operation'Pos (I))) :=
           (if C.Granted (I) then 1 else 0);
      end loop;
      Result.Applies_To :=
        (Kind => Scope_Kind'Pos (C.Applies_To.Kind),
         World_Id => From_Digest (C.Applies_To.World_Id));
      Result.Ceiling :=
        (Worlds => C.Ceiling.Worlds,
         Evaluations => C.Ceiling.Evaluations);
      return Result;
   end From_Capability;

   function ABI_Version return Interfaces.C.int is (1);

   function Check_C
     (U : access constant C_Universe;
      Input : access constant C_Check_Input;
      D : access C_Check_Decision) return Interfaces.C.int
   is
      State : Universe_State;
      Cap : Capability := Null_Capability;
      Q : Scoped_Request;
      Result : Check_Decision;
   begin
      if D = null then
         return -1;
      end if;
      D.all := (Kind => Check_Kind'Pos (Refused),
                Reason => Check_Reason'Pos (Malformed_Capability));
      if U = null or else Input = null then
         return -1;
      end if;
      if U.Roster_Count < 0 or else U.Roster_Count > 8
        or else Input.Ask.Action < 0
        or else Input.Ask.Action > Operation'Pos (Operation'Last)
        or else Input.Grant.Terminal not in 0 .. 1
        or else Input.Grant.Applies_To.Kind not in 0 .. 1
      then
         return -1;
      end if;
      for I in U.Roster'Range loop
         if U.Roster (I).Role < 0
           or else U.Roster (I).Role > Agent_Role'Pos (Agent_Role'Last)
           or else U.Roster (I).Enabled not in 0 .. 1
         then
            return -1;
         end if;
      end loop;
      for I in Input.Grant.Granted'Range loop
         if Input.Grant.Granted (I) not in 0 .. 1 then
            return -1;
         end if;
      end loop;

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

      Cap.Capability_Id := To_Digest (Input.Grant.Capability_Id);
      Cap.Parent_Id := To_Digest (Input.Grant.Parent_Id);
      Cap.Universe_Id := To_Digest (Input.Grant.Universe_Id);
      Cap.Mission_Id := To_Digest (Input.Grant.Mission_Id);
      Cap.Policy_Id := To_Digest (Input.Grant.Policy_Id);
      Cap.Authority_Id := To_Digest (Input.Grant.Authority_Id);
      Cap.Worldline_Instance_Id :=
        To_Digest (Input.Grant.Worldline_Instance_Id);
      Cap.Root_Set_Id := To_Digest (Input.Grant.Root_Set_Id);
      Cap.Prime_Id := To_Digest (Input.Grant.Prime_Id);
      Cap.Subject_Id := To_Digest (Input.Grant.Subject_Id);
      Cap.Issuer_Id := To_Digest (Input.Grant.Issuer_Id);
      Cap.Policy_Epoch := Input.Grant.Policy_Epoch;
      Cap.Issued_At := Input.Grant.Issued_At;
      Cap.Expires_At := Input.Grant.Expires_At;
      Cap.Terminal := Input.Grant.Terminal = 1;
      for I in Cap.Granted'Range loop
         Cap.Granted (I) :=
           Input.Grant.Granted (Interfaces.C.int (Operation'Pos (I))) = 1;
      end loop;
      Cap.Applies_To :=
        (Kind => Scope_Kind'Val (Input.Grant.Applies_To.Kind),
         World_Id => To_Digest (Input.Grant.Applies_To.World_Id));
      Cap.Ceiling :=
        (Worlds => Input.Grant.Ceiling.Worlds,
         Evaluations => Input.Grant.Ceiling.Evaluations);

      Q.Ask :=
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
         Action => Operation'Val (Input.Ask.Action));
      Q.Target_World_Id := To_Digest (Input.Target_World_Id);
      Result := Cosmogony.Capabilities.Check_Request
        (State, To_Digest (Input.Authority_Id), Cap, Q,
         (Worlds => Input.Usage.Worlds,
          Evaluations => Input.Usage.Evaluations),
         Input.Now_Tick);
      D.all := (Kind => Check_Kind'Pos (Result.Kind),
                Reason => Check_Reason'Pos (Result.Reason));
      return 0;
   end Check_C;
end Cosmogony.Capability_C_API;
