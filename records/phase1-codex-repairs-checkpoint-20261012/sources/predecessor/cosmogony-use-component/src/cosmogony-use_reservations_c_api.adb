with Ada.Unchecked_Conversion;
with System.Storage_Elements;
with Cosmogony.Genesis;
with Cosmogony.Capabilities;
with Cosmogony.Revocable_Capabilities;
with Cosmogony.Use_Reservations;
package body Cosmogony.Use_Reservations_C_API with SPARK_Mode => Off is
   use System.Storage_Elements;
   use Cosmogony.Genesis;
   use Cosmogony.Capabilities;
   use type System.Address;
   use type Interfaces.C.int;
   use type Interfaces.C.long;
   use type Interfaces.C.size_t;
   use type Cosmogony.C_API.C_Digest;
   use type Cosmogony.Capability_C_API.C_Capability;
   package L renames Cosmogony.Use_Reservations;
   package R renames Cosmogony.Revocable_Capabilities;
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


   function To_Binding (Raw : C_Binding) return L.Binding is
     (Capability_Id => To_Digest (Raw.Capability_Id), Operation_Id => To_Digest (Raw.Operation_Id),
      Transaction_Id => To_Digest (Raw.Transaction_Id), Requester_Id => To_Digest (Raw.Requester_Id),
      Universe_Head => To_Digest (Raw.Universe_Head), Request_Identity => To_Digest (Raw.Request_Identity),
      Grant_Use_Identity => To_Digest (Raw.Grant_Use_Identity),
      Recovery_Binding_Identity => To_Digest (Raw.Recovery_Binding_Identity),
      Policy_Epoch => Raw.Policy_Epoch, Action => Operation'Val (Raw.Action));
   function Canonical (Raw : C_Binding) return Boolean is
     (Raw.Action in 0 .. Operation'Pos (Operation'Last));
   function Canonical (Raw : Cosmogony.Revocation_C_API.C_Lineage) return Boolean is
   begin
      if Raw.Count not in 1 .. Interfaces.C.int (R.Link_Index'Last) then return False; end if;
      for I in 0 .. Raw.Count - 1 loop
         if Raw.Links (I).Revoked not in 0 .. 1
           or else not Cosmogony.Capability_C_API.Canonical_C (Raw.Links (I).Grant)
         then return False; end if;
      end loop;
      return True;
   end Canonical;
   function To_Links (Raw : Cosmogony.Revocation_C_API.C_Lineage) return R.Lineage is
      Result : R.Lineage := (others => (Grant => Null_Capability, Revoked => False));
   begin
      for I in 1 .. Raw.Count loop
         Result (R.Link_Index (I)) :=
           (Grant => To_Capability (Raw.Links (I - 1).Grant), Revoked => Raw.Links (I - 1).Revoked = 1);
      end loop;
      return Result;
   end To_Links;
   type Input_Access is access all C_Input;
   type Row_Access is access all C_Row;
   type Grant_Access is access all Cosmogony.Capability_C_API.C_Capability;
   type Output_Access is access all C_Result;
   function Input_At is new Ada.Unchecked_Conversion (System.Address, Input_Access);
   function Row_At is new Ada.Unchecked_Conversion (System.Address, Row_Access);
   function Grant_At is new Ada.Unchecked_Conversion (System.Address, Grant_Access);
   function Output_At is new Ada.Unchecked_Conversion (System.Address, Output_Access);
   function Shape (Address : System.Address; Length : Interfaces.C.size_t) return Boolean is
     (if Length = 0 then True else Address /= System.Null_Address
      and then Length <= Interfaces.C.size_t (Storage_Offset'Last)
      and then Integer_Address (Length - 1) <= Integer_Address'Last - To_Integer (Address));
   function ABI_Version return Interfaces.C.int is (1);
   function Decide
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Rows : System.Address; Row_Count, Rows_Length : Interfaces.C.size_t;
      Grants : System.Address; Grant_Count, Grants_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t) return Interfaces.C.int
   is
      Row_Bytes : constant Interfaces.C.size_t := C_Row'Object_Size / System.Storage_Unit;
      Grant_Bytes : constant Interfaces.C.size_t := Cosmogony.Capability_C_API.C_Capability'Object_Size / System.Storage_Unit;
   begin
      if Input_Length /= C_Input'Object_Size / System.Storage_Unit
        or else Output_Length /= C_Result'Object_Size / System.Storage_Unit
        or else Row_Count > Interfaces.C.size_t (Natural'Last)
        or else Grant_Count > Interfaces.C.size_t (Natural'Last)
        or else Row_Count > Interfaces.C.size_t'Last / Row_Bytes
        or else Grant_Count > Interfaces.C.size_t'Last / Grant_Bytes
        or else Rows_Length /= Row_Count * Row_Bytes
        or else Grants_Length /= Grant_Count * Grant_Bytes
        or else not Shape (Input, Input_Length) or else not Shape (Output, Output_Length)
        or else not Shape (Rows, Rows_Length) or else not Shape (Grants, Grants_Length)
        or else To_Integer (Input) mod C_Input'Alignment /= 0
        or else To_Integer (Output) mod C_Result'Alignment /= 0
        or else (Row_Count > 0 and then To_Integer (Rows) mod C_Row'Alignment /= 0)
        or else (Grant_Count > 0 and then To_Integer (Grants) mod Cosmogony.Capability_C_API.C_Capability'Alignment /= 0)
      then return -1; end if;
      declare
         Raw : constant C_Input := Input_At (Input).all;
         Data : L.Rows (1 .. Natural (Row_Count));
         All_Grants : L.Grant_Rows (1 .. Natural (Grant_Count));
         Answer : L.Status;
      begin
         if Raw.Mode not in 0 .. L.Command'Pos (L.Command'Last)
           or else not Canonical (Raw.Bound) or else not Canonical (Raw.Chain)
           or else not Cosmogony.Universe_C_API.Canonical_C (Raw.U)
           or else Raw.G.Roster_Count not in 0 .. Interfaces.C.int (Agent_Count'Last)
           or else Raw.Ask.Ask.Action not in 0 .. Operation'Pos (Operation'Last)
           or else not Cosmogony.Capability_C_API.Canonical_C (Raw.Ask.Grant)
           or else Raw.Ask.Grant /= Raw.Chain.Links (Raw.Chain.Count - 1).Grant
           or else Raw.Ask.Authority_Id /= Cosmogony.C_API.C_Digest (Raw.U.Policy.Authority_Id)
         then return -1; end if;
         for I in Raw.G.Roster'Range loop
            if Raw.G.Roster (I).Role not in 0 .. Agent_Role'Pos (Agent_Role'Last)
              or else Raw.G.Roster (I).Enabled not in 0 .. 1 then return -1; end if;
         end loop;
         for I in Data'Range loop
            declare
               Item : constant C_Row := Row_At
                 (Rows + Storage_Offset (Interfaces.C.size_t (I - 1) * Row_Bytes)).all;
            begin
               if Item.Kind not in 0 .. L.Row_Kind'Pos (L.Row_Kind'Last)
                 or else Item.State not in 0 .. L.Use_State'Pos (L.Use_State'Last)
                 or else not Canonical (Item.Bound) or else not Canonical (Item.Chain)
               then return -1; end if;
               Data (I) := (Kind => L.Row_Kind'Val (Item.Kind), State => L.Use_State'Val (Item.State),
                  Bound => To_Binding (Item.Bound), Links => To_Links (Item.Chain), Link_Count => R.Link_Count (Item.Chain.Count));
            end;
         end loop;
         for I in All_Grants'Range loop
            declare
               Item : constant Cosmogony.Capability_C_API.C_Capability := Grant_At
                 (Grants + Storage_Offset (Interfaces.C.size_t (I - 1) * Grant_Bytes)).all;
            begin
               if not Cosmogony.Capability_C_API.Canonical_C (Item) then return -1; end if;
               All_Grants (I) := To_Capability (Item);
            end;
         end loop;
         -- Complete copied arenas remain live until the pure full-roster call;
         -- only then may output overlap input/row/grant storage safely.
         Answer := L.Check (Data, All_Grants, Cosmogony.Universe_C_API.To_Record (Raw.U),
           To_State (Raw.G), To_Links (Raw.Chain), R.Link_Count (Raw.Chain.Count), To_Request (Raw.Ask),
           (Raw.Ask.Usage.Worlds, Raw.Ask.Usage.Evaluations), Raw.Ask.Now_Tick,
           To_Binding (Raw.Bound), L.Command'Val (Raw.Mode));
         Output_At (Output).all := (Status => L.Status'Pos (Answer));
      end;
      return 0;
   exception
      when others => return -1;
   end Decide;
   function Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long is
      V1 : C_Binding;
      V2 : C_Row;
      V3 : C_Input;
      V4 : C_Result;
      V5 : Cosmogony.Capability_C_API.C_Capability;
      V6 : Cosmogony.Capability_C_API.C_Check_Input;
      V7 : Cosmogony.Revocation_C_API.C_Lineage;
      V8 : Cosmogony.Revocation_C_API.C_Link;
      V9 : Cosmogony.Universe_C_API.C_Record;
      V10 : Cosmogony.C_API.C_Universe;
      V11 : Cosmogony.C_API.C_Request;
      V12 : Cosmogony.Universe_C_API.C_Policy;
      V13 : Cosmogony.C_API.C_Agent;
      V14 : Cosmogony.Capability_C_API.C_Scope;
      V15 : Cosmogony.Capability_C_API.C_Ceiling;
      V16 : Cosmogony.Capability_C_API.C_Usage;
   begin
      case Kind is
         when 1 =>
            case Field is
               when 0 => return C_Binding'Object_Size / System.Storage_Unit;
               when 1 => return C_Binding'Alignment;
               when 2 => return V1.Capability_Id'Position;
               when 3 => return V1.Operation_Id'Position;
               when 4 => return V1.Transaction_Id'Position;
               when 5 => return V1.Requester_Id'Position;
               when 6 => return V1.Universe_Head'Position;
               when 7 => return V1.Request_Identity'Position;
               when 8 => return V1.Grant_Use_Identity'Position;
               when 9 => return V1.Recovery_Binding_Identity'Position;
               when 10 => return V1.Policy_Epoch'Position;
               when 11 => return V1.Action'Position;
               when others => return -1;
            end case;
         when 2 =>
            case Field is
               when 0 => return C_Row'Object_Size / System.Storage_Unit;
               when 1 => return C_Row'Alignment;
               when 2 => return V2.Kind'Position;
               when 3 => return V2.State'Position;
               when 4 => return V2.Bound'Position;
               when 5 => return V2.Chain'Position;
               when others => return -1;
            end case;
         when 3 =>
            case Field is
               when 0 => return C_Input'Object_Size / System.Storage_Unit;
               when 1 => return C_Input'Alignment;
               when 2 => return V3.U'Position;
               when 3 => return V3.G'Position;
               when 4 => return V3.Ask'Position;
               when 5 => return V3.Chain'Position;
               when 6 => return V3.Bound'Position;
               when 7 => return V3.Mode'Position;
               when others => return -1;
            end case;
         when 4 =>
            case Field is
               when 0 => return C_Result'Object_Size / System.Storage_Unit;
               when 1 => return C_Result'Alignment;
               when 2 => return V4.Status'Position;
               when others => return -1;
            end case;
         when 5 =>
            case Field is
               when 0 => return Cosmogony.Capability_C_API.C_Capability'Object_Size / System.Storage_Unit;
               when 1 => return Cosmogony.Capability_C_API.C_Capability'Alignment;
               when 2 => return V5.Capability_Id'Position;
               when 3 => return V5.Parent_Id'Position;
               when 4 => return V5.Universe_Id'Position;
               when 5 => return V5.Mission_Id'Position;
               when 6 => return V5.Policy_Id'Position;
               when 7 => return V5.Authority_Id'Position;
               when 8 => return V5.Worldline_Instance_Id'Position;
               when 9 => return V5.Root_Set_Id'Position;
               when 10 => return V5.Prime_Id'Position;
               when 11 => return V5.Subject_Id'Position;
               when 12 => return V5.Issuer_Id'Position;
               when 13 => return V5.Policy_Epoch'Position;
               when 14 => return V5.Issued_At'Position;
               when 15 => return V5.Expires_At'Position;
               when 16 => return V5.Terminal'Position;
               when 17 => return V5.Granted'Position;
               when 18 => return V5.Applies_To'Position;
               when 19 => return V5.Ceiling'Position;
               when others => return -1;
            end case;
         when 6 =>
            case Field is
               when 0 => return Cosmogony.Capability_C_API.C_Check_Input'Object_Size / System.Storage_Unit;
               when 1 => return Cosmogony.Capability_C_API.C_Check_Input'Alignment;
               when 2 => return V6.Authority_Id'Position;
               when 3 => return V6.Grant'Position;
               when 4 => return V6.Ask'Position;
               when 5 => return V6.Target_World_Id'Position;
               when 6 => return V6.Usage'Position;
               when 7 => return V6.Now_Tick'Position;
               when others => return -1;
            end case;
         when 7 =>
            case Field is
               when 0 => return Cosmogony.Revocation_C_API.C_Lineage'Object_Size / System.Storage_Unit;
               when 1 => return Cosmogony.Revocation_C_API.C_Lineage'Alignment;
               when 2 => return V7.Count'Position;
               when 3 => return V7.Links'Position;
               when others => return -1;
            end case;
         when 8 =>
            case Field is
               when 0 => return Cosmogony.Revocation_C_API.C_Link'Object_Size / System.Storage_Unit;
               when 1 => return Cosmogony.Revocation_C_API.C_Link'Alignment;
               when 2 => return V8.Grant'Position;
               when 3 => return V8.Revoked'Position;
               when others => return -1;
            end case;
         when 9 =>
            case Field is
               when 0 => return Cosmogony.Universe_C_API.C_Record'Object_Size / System.Storage_Unit;
               when 1 => return Cosmogony.Universe_C_API.C_Record'Alignment;
               when 2 => return V9.Universe_Id'Position;
               when 3 => return V9.Parent_Id'Position;
               when 4 => return V9.Policy_Epoch'Position;
               when 5 => return V9.Policy'Position;
               when 6 => return V9.Prime_Worldline_Id'Position;
               when 7 => return V9.Prime_Id'Position;
               when 8 => return V9.Prime_Generation'Position;
               when 9 => return V9.Receipt_Head_Id'Position;
               when 10 => return V9.Life'Position;
               when 11 => return V9.Running_Worlds'Position;
               when 12 => return V9.Outstanding_Reservations'Position;
               when 13 => return V9.Unresolved_Transactions'Position;
               when 14 => return V9.Evidence_Snapshot_Id'Position;
               when 15 => return V9.Snapshot_Complete'Position;
               when others => return -1;
            end case;
         when 10 =>
            case Field is
               when 0 => return Cosmogony.C_API.C_Universe'Object_Size / System.Storage_Unit;
               when 1 => return Cosmogony.C_API.C_Universe'Alignment;
               when 2 => return V10.Universe_Id'Position;
               when 3 => return V10.Mission_Id'Position;
               when 4 => return V10.Policy_Id'Position;
               when 5 => return V10.Policy_Owner_Mission'Position;
               when 6 => return V10.Worldline_Instance_Id'Position;
               when 7 => return V10.Root_Set_Id'Position;
               when 8 => return V10.Prime_Id'Position;
               when 9 => return V10.Policy_Epoch'Position;
               when 10 => return V10.World_Limit'Position;
               when 11 => return V10.Worlds_Reserved'Position;
               when 12 => return V10.Evaluation_Limit'Position;
               when 13 => return V10.Evaluations_Reserved'Position;
               when 14 => return V10.Roster_Count'Position;
               when 15 => return V10.Roster'Position;
               when others => return -1;
            end case;
         when 11 =>
            case Field is
               when 0 => return Cosmogony.C_API.C_Request'Object_Size / System.Storage_Unit;
               when 1 => return Cosmogony.C_API.C_Request'Alignment;
               when 2 => return V11.Request_Id'Position;
               when 3 => return V11.Universe_Id'Position;
               when 4 => return V11.Mission_Id'Position;
               when 5 => return V11.Policy_Id'Position;
               when 6 => return V11.Worldline_Instance_Id'Position;
               when 7 => return V11.Root_Set_Id'Position;
               when 8 => return V11.Prime_Id'Position;
               when 9 => return V11.Policy_Epoch'Position;
               when 10 => return V11.Actor_Id'Position;
               when 11 => return V11.Action'Position;
               when others => return -1;
            end case;
         when 12 =>
            case Field is
               when 0 => return Cosmogony.Universe_C_API.C_Policy'Object_Size / System.Storage_Unit;
               when 1 => return Cosmogony.Universe_C_API.C_Policy'Alignment;
               when 2 => return V12.Mission_Id'Position;
               when 3 => return V12.Authority_Id'Position;
               when 4 => return V12.Resource_Id'Position;
               when 5 => return V12.Network_Id'Position;
               when 6 => return V12.Provider_Id'Position;
               when 7 => return V12.Evaluator_Id'Position;
               when 8 => return V12.Root_Set_Id'Position;
               when 9 => return V12.Evidence_Id'Position;
               when 10 => return V12.Roster_Id'Position;
               when 11 => return V12.Worldline_Set_Id'Position;
               when others => return -1;
            end case;
         when 13 =>
            case Field is
               when 0 => return Cosmogony.C_API.C_Agent'Object_Size / System.Storage_Unit;
               when 1 => return Cosmogony.C_API.C_Agent'Alignment;
               when 2 => return V13.Identity'Position;
               when 3 => return V13.Role'Position;
               when 4 => return V13.Enabled'Position;
               when others => return -1;
            end case;
         when 14 =>
            case Field is
               when 0 => return Cosmogony.Capability_C_API.C_Scope'Object_Size / System.Storage_Unit;
               when 1 => return Cosmogony.Capability_C_API.C_Scope'Alignment;
               when 2 => return V14.Kind'Position;
               when 3 => return V14.World_Id'Position;
               when others => return -1;
            end case;
         when 15 =>
            case Field is
               when 0 => return Cosmogony.Capability_C_API.C_Ceiling'Object_Size / System.Storage_Unit;
               when 1 => return Cosmogony.Capability_C_API.C_Ceiling'Alignment;
               when 2 => return V15.Worlds'Position;
               when 3 => return V15.Evaluations'Position;
               when others => return -1;
            end case;
         when 16 =>
            case Field is
               when 0 => return Cosmogony.Capability_C_API.C_Usage'Object_Size / System.Storage_Unit;
               when 1 => return Cosmogony.Capability_C_API.C_Usage'Alignment;
               when 2 => return V16.Worlds'Position;
               when 3 => return V16.Evaluations'Position;
               when others => return -1;
            end case;
         when 17 =>
            case Field is
               when 0 => return Cosmogony.C_API.C_Digest'Object_Size / System.Storage_Unit;
               when 1 => return Cosmogony.C_API.C_Digest'Alignment;
               when 2 => return 0;
               when others => return -1;
            end case;
         when 18 =>
            case Field is
               when 0 => return Cosmogony.Capability_C_API.C_Action_Set'Object_Size / System.Storage_Unit;
               when 1 => return Cosmogony.Capability_C_API.C_Action_Set'Alignment;
               when 2 => return 0;
               when others => return -1;
            end case;
         when others => return -1;
      end case;
   end Layout;
end Cosmogony.Use_Reservations_C_API;
