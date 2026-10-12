with Interfaces;
with Interfaces.C;
with System;
with Cosmogony.C_API;
with Cosmogony.Capability_C_API;
with Cosmogony.Revocation_C_API;
with Cosmogony.Universe_C_API;
package Cosmogony.Use_Reservations_C_API with SPARK_Mode => Off is
   type C_Binding is record
      Capability_Id, Operation_Id, Transaction_Id, Requester_Id,
        Universe_Head, Request_Identity, Grant_Use_Identity,
        Recovery_Binding_Identity : Cosmogony.C_API.C_Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Action : Interfaces.C.int;
   end record with Convention => C;
   type C_Row is record
      Kind, State : Interfaces.C.int;
      Bound : C_Binding;
      Chain : Cosmogony.Revocation_C_API.C_Lineage;
   end record with Convention => C;
   type C_Input is record
      U : Cosmogony.Universe_C_API.C_Record;
      G : Cosmogony.C_API.C_Universe;
      Ask : Cosmogony.Capability_C_API.C_Check_Input;
      Chain : Cosmogony.Revocation_C_API.C_Lineage;
      Bound : C_Binding;
      Mode : Interfaces.C.int;
   end record with Convention => C;
   type C_Result is record
      Status : Interfaces.C.int;
   end record with Convention => C;
   function ABI_Version return Interfaces.C.int
     with Export, Convention => C, External_Name => "cosmogony_use_reservation_version_v1";
   function Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long
     with Export, Convention => C, External_Name => "cosmogony_use_reservation_layout_v1";
   function Decide
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Rows : System.Address; Row_Count, Rows_Length : Interfaces.C.size_t;
      Grants : System.Address; Grant_Count, Grants_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "cosmogony_use_reservation_decide_v1";
end Cosmogony.Use_Reservations_C_API;
