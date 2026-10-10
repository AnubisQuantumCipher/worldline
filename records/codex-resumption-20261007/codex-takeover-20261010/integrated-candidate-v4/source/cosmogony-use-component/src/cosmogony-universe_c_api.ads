with Interfaces;
with Interfaces.C;
with Cosmogony.Universes;

package Cosmogony.Universe_C_API with SPARK_Mode => Off is
   --  Every pointer must address correctly aligned accessible storage.
   --  An invalid code or null pointer returns -1 and applies no operation.
   type C_Digest is array (Interfaces.C.int range 0 .. 3)
     of Interfaces.Unsigned_64 with Convention => C;
   type C_Policy is record
      Mission_Id, Authority_Id, Resource_Id, Network_Id, Provider_Id,
        Evaluator_Id, Root_Set_Id, Evidence_Id, Roster_Id,
        Worldline_Set_Id : C_Digest;
   end record with Convention => C;
   type C_Record is record
      Universe_Id, Parent_Id : C_Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Policy : C_Policy;
      Prime_Worldline_Id, Prime_Id : C_Digest;
      Prime_Generation : Interfaces.Unsigned_64;
      Receipt_Head_Id : C_Digest;
      Life : Interfaces.C.int;
      Running_Worlds, Outstanding_Reservations,
        Unresolved_Transactions : Interfaces.Unsigned_32;
      Evidence_Snapshot_Id : C_Digest;
      Snapshot_Complete : Interfaces.C.int;
   end record with Convention => C;
   type C_Evolution is record
      Applied : Interfaces.C.int;
      Value : C_Record;
   end record with Convention => C;
   type C_Evidence is record
      Universe_Id : C_Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Policy : C_Policy;
      Prime_Worldline_Id, Prime_Id : C_Digest;
      Prime_Generation : Interfaces.Unsigned_64;
   end record with Convention => C;

   --  Internal Ada conversion for higher-level C entry points. Callers must
   --  check Canonical_C before To_Record; neither authenticates the input.
   function Canonical_C (U : C_Record) return Boolean;
   function To_Record
     (U : C_Record) return Cosmogony.Universes.Universe_Record;
   function From_Record
     (U : Cosmogony.Universes.Universe_Record) return C_Record;

   function ABI_Version return Interfaces.C.int with
     Export, Convention => C,
     External_Name => "cosmogony_universe_abi_version";
   function Record_Bytes return Interfaces.C.int with
     Export, Convention => C,
     External_Name => "cosmogony_universe_record_bytes";
   function Policy_Bytes return Interfaces.C.int with
     Export, Convention => C,
     External_Name => "cosmogony_universe_policy_bytes";
   function Evolution_Bytes return Interfaces.C.int with
     Export, Convention => C,
     External_Name => "cosmogony_universe_evolution_bytes";
   function Evidence_Bytes return Interfaces.C.int with
     Export, Convention => C,
     External_Name => "cosmogony_universe_evidence_bytes";
   function Valid_C (U : access constant C_Record) return Interfaces.C.int with
     Export, Convention => C, External_Name => "cosmogony_universe_valid";
   function Transition_C
     (U : access constant C_Record; Target : Interfaces.C.int;
      Result : access C_Evolution) return Interfaces.C.int with
     Export, Convention => C, External_Name => "cosmogony_universe_transition";
   function Revise_C
     (U : access constant C_Record; Proposed : access constant C_Policy;
      Result : access C_Evolution) return Interfaces.C.int with
     Export, Convention => C, External_Name => "cosmogony_universe_revise";
   function Capture_Snapshot_C
     (U : access constant C_Record; Snapshot_Id : access constant C_Digest;
      Result : access C_Evolution) return Interfaces.C.int with
     Export, Convention => C,
     External_Name => "cosmogony_universe_capture_snapshot";
   function Advance_Prime_C
     (U : access constant C_Record; Prime_Id : access constant C_Digest;
      Generation : Interfaces.Unsigned_64;
      Receipt_Id : access constant C_Digest;
      Result : access C_Evolution) return Interfaces.C.int with
     Export, Convention => C,
     External_Name => "cosmogony_universe_advance_prime";
   function Bind_Evidence_C
     (U : access constant C_Record; Bound : access C_Evidence)
      return Interfaces.C.int with
     Export, Convention => C,
     External_Name => "cosmogony_universe_bind_evidence";
   function Evidence_Current_C
     (U : access constant C_Record; Bound : access constant C_Evidence)
      return Interfaces.C.int with
     Export, Convention => C,
     External_Name => "cosmogony_universe_evidence_current";
end Cosmogony.Universe_C_API;
