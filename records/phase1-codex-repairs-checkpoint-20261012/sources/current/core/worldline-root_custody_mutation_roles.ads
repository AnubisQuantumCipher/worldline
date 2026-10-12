with Worldline.Root_Custody_Descriptor;

--  Explicit role clauses to be composed with full original operation operands.
--  No function in this unit implements the complete Mutation_Allowed entry.
--  In particular no universal owner test covers M1/M2 historical exceptions,
--  M4 Legal, M5 response correspondence, M7 intervals or M8/M9 protocols.
--  Termination remains REQUIRED for every precondition-satisfying input:
--  these ordinary side-effect-free SPARK functions have the intrinsic
--  termination obligation documented by this toolchain's E0016. Explicit
--  per-function Always_Terminates is illegal here; no obligation is waived.
package Worldline.Root_Custody_Mutation_Roles with SPARK_Mode is
   package D renames Worldline.Root_Custody_Descriptor;
   package C renames D.C;
   package M renames D.M;
   package Q renames D.Q;
   use type C.Context_Status;
   use type C.Physical_Status;
   use type D.Projection_Status;
   use type D.Reader_Projection;
   use type M.Actor;
   use type M.Owner;
   use type M.Root_Phase;

   function M3_Store_Role
     (Data : Q.Byte_Array; Roots : M.Root_State_Array;
      Current : C.Root_Reference; Caller : M.Actor) return Boolean
   with Global => null,
     Post => M3_Store_Role'Result =
       (C.Current_Store_Owner (Data, Roots, Current).Status = C.Projected
        and then C.Current_Store_Owner (Data, Roots, Current).Value in
          M.Front | M.Worker
        and then C.Current_Store_Owner (Data, Roots, Current).Value =
          M.Actor_Owner (Caller));

   function M6_Descriptor_Role
     (Data : Q.Byte_Array; Roots : M.Root_State_Array;
      Subjects : M.Subject_State_Array; Reference : D.Descriptor_Reference;
      Caller : M.Actor) return Boolean
   with Global => null,
     Post => M6_Descriptor_Role'Result =
       (D.Project_Descriptor (Data, Roots, Subjects, Reference).Status =
          D.Projected and then
        (case D.Project_Descriptor
           (Data, Roots, Subjects, Reference).Read_Actor is
           when D.Front_Reader => Caller = M.Front,
           when D.Worker_Reader => Caller = M.Worker,
           when D.Collector_Or_Reconciler_Reader =>
             Caller in M.Collector | M.Reconciler,
           when D.No_Reader => False));

   --  These are ROLE/FLAG clauses only. Original root's unit identity still
   --  must join the supplied M10 unit through authenticated launch evidence.
   function M10_Reset_Role_And_Witness
     (Data : Q.Byte_Array; Roots : M.Root_State_Array;
      Original : C.Root_Reference; Caller : M.Actor) return Boolean
   with Global => null,
     Post => M10_Reset_Role_And_Witness'Result =
       (Caller = M.Collector and then
        C.Physical_Actor (Data, Roots, Original).Status = C.Physical_Projected
        and then Roots (C.Physical_Actor (Data, Roots, Original).Index).
          Physical.Witness);

   function M11_Escrow_Role_And_Phase
     (Data : Q.Byte_Array; Roots : M.Root_State_Array;
      Current : C.Root_Reference; Caller : M.Actor) return Boolean
   with Global => null,
     Post => M11_Escrow_Role_And_Phase'Result =
       (Caller = M.Collector and then
        C.Current_Store_Owner (Data, Roots, Current).Status = C.Projected
        and then Roots (C.Current_Store_Owner (Data, Roots, Current).Index).
          Phase = M.Front_Reconstruction);
end Worldline.Root_Custody_Mutation_Roles;
