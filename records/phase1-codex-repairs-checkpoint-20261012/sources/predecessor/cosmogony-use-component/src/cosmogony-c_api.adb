with Cosmogony.Genesis;

package body Cosmogony.C_API with SPARK_Mode => Off is
   use Cosmogony.Genesis;
   use type Interfaces.C.int;

   function To_Digest (Value : C_Digest) return Digest is
     (1 => Value (0), 2 => Value (1), 3 => Value (2), 4 => Value (3));

   function Canonical_U (U : C_Universe) return Boolean is
   begin
      if U.Roster_Count < 0 or else U.Roster_Count > 8 then
         return False;
      end if;
      for I in U.Roster'Range loop
         if U.Roster (I).Role < 0
           or else U.Roster (I).Role > Agent_Role'Pos (Agent_Role'Last)
           or else U.Roster (I).Enabled not in 0 .. 1
         then
            return False;
         end if;
      end loop;
      return True;
   end Canonical_U;

   function Canonical_R (R : C_Request) return Boolean is
     (R.Action >= 0 and then R.Action <= Operation'Pos (Operation'Last));

   function To_State (U : C_Universe) return Universe_State is
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

   function To_Request (R : C_Request) return Request is
     (Request_Id => To_Digest (R.Request_Id),
      Universe_Id => To_Digest (R.Universe_Id),
      Mission_Id => To_Digest (R.Mission_Id),
      Policy_Id => To_Digest (R.Policy_Id),
      Worldline_Instance_Id => To_Digest (R.Worldline_Instance_Id),
      Root_Set_Id => To_Digest (R.Root_Set_Id),
      Prime_Id => To_Digest (R.Prime_Id),
      Policy_Epoch => R.Policy_Epoch,
      Actor_Id => To_Digest (R.Actor_Id),
      Action => Operation'Val (R.Action));

   function ABI_Version return Interfaces.C.int is (1);

   function Decide_C
     (U : access constant C_Universe;
      R : access constant C_Request;
      D : access C_Decision) return Interfaces.C.int
   is
      Result : Decision;
   begin
      if D = null then
         return -1;
      end if;
      D.all := (Kind => Decision_Kind'Pos (Denied),
                Reason => Decision_Reason'Pos (Invalid_Genesis));
      if U = null or else R = null then
         return -1;
      end if;
      if not Canonical_U (U.all) or else not Canonical_R (R.all) then
         return -1;
      end if;
      Result := Cosmogony.Genesis.Decide
        (To_State (U.all), To_Request (R.all));
      D.all := (Kind => Decision_Kind'Pos (Result.Kind),
                Reason => Decision_Reason'Pos (Result.Reason));
      return 0;
   end Decide_C;
end Cosmogony.C_API;
