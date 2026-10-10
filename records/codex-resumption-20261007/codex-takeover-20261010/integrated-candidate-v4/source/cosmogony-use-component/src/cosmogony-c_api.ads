with Interfaces;
with Interfaces.C;
with Cosmogony.Genesis;

package Cosmogony.C_API with SPARK_Mode => Off is
   --  Caller owns accessible, correctly aligned storage for all three pointers.
   --  Invalid enum codes and null pointers return -1 and cannot forward a request.
   type C_Digest is array (Interfaces.C.int range 0 .. 3)
     of Interfaces.Unsigned_64 with Convention => C;
   type C_Agent is record
      Identity : C_Digest;
      Role : Interfaces.C.int;
      Enabled : Interfaces.C.int;
   end record with Convention => C;
   type C_Roster is array (Interfaces.C.int range 0 .. 7) of C_Agent
     with Convention => C;
   type C_Universe is record
      Universe_Id : C_Digest;
      Mission_Id : C_Digest;
      Policy_Id : C_Digest;
      Policy_Owner_Mission : C_Digest;
      Worldline_Instance_Id : C_Digest;
      Root_Set_Id : C_Digest;
      Prime_Id : C_Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      World_Limit : Interfaces.Unsigned_32;
      Worlds_Reserved : Interfaces.Unsigned_32;
      Evaluation_Limit : Interfaces.Unsigned_32;
      Evaluations_Reserved : Interfaces.Unsigned_32;
      Roster_Count : Interfaces.C.int;
      Roster : C_Roster;
   end record with Convention => C;
   type C_Request is record
      Request_Id : C_Digest;
      Universe_Id : C_Digest;
      Mission_Id : C_Digest;
      Policy_Id : C_Digest;
      Worldline_Instance_Id : C_Digest;
      Root_Set_Id : C_Digest;
      Prime_Id : C_Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Actor_Id : C_Digest;
      Action : Interfaces.C.int;
   end record with Convention => C;
   type C_Decision is record
      Kind : Interfaces.C.int;
      Reason : Interfaces.C.int;
   end record with Convention => C;

   function Canonical_U (U : C_Universe) return Boolean;
   function Canonical_R (R : C_Request) return Boolean;
   function To_State
     (U : C_Universe) return Cosmogony.Genesis.Universe_State;
   function To_Request
     (R : C_Request) return Cosmogony.Genesis.Request;

   function Decide_C
     (U : access constant C_Universe;
      R : access constant C_Request;
      D : access C_Decision) return Interfaces.C.int
     with Export, Convention => C, External_Name => "cosmogony_genesis_decide";
   function ABI_Version return Interfaces.C.int
     with Export, Convention => C,
          External_Name => "cosmogony_genesis_abi_version";
end Cosmogony.C_API;
