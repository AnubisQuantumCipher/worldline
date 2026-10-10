package body Worldline.Root_Custody_Mutation_Roles with SPARK_Mode is
   function M3_Store_Role
     (Data : Q.Byte_Array; Roots : M.Root_State_Array;
      Current : C.Root_Reference; Caller : M.Actor) return Boolean
   is
      Projected : constant C.Store_Owner_Result :=
        C.Current_Store_Owner (Data, Roots, Current);
   begin
      return Projected.Status = C.Projected and then
        Projected.Value in M.Front | M.Worker and then
        Projected.Value = M.Actor_Owner (Caller);
   end M3_Store_Role;

   function M6_Descriptor_Role
     (Data : Q.Byte_Array; Roots : M.Root_State_Array;
      Subjects : M.Subject_State_Array; Reference : D.Descriptor_Reference;
      Caller : M.Actor) return Boolean
   is
      Projected : constant D.Descriptor_Projection :=
        D.Project_Descriptor (Data, Roots, Subjects, Reference);
   begin
      if Projected.Status /= D.Projected then
         return False;
      end if;
      return
        (case Projected.Read_Actor is
           when D.Front_Reader => Caller = M.Front,
           when D.Worker_Reader => Caller = M.Worker,
           when D.Collector_Or_Reconciler_Reader =>
             Caller in M.Collector | M.Reconciler,
           when D.No_Reader => False);
   end M6_Descriptor_Role;

   function M10_Reset_Role_And_Witness
     (Data : Q.Byte_Array; Roots : M.Root_State_Array;
      Original : C.Root_Reference; Caller : M.Actor) return Boolean
   is
      Projected : constant C.Physical_Actor_Result :=
        C.Physical_Actor (Data, Roots, Original);
   begin
      return Caller = M.Collector and then
        Projected.Status = C.Physical_Projected and then
        Roots (Projected.Index).Physical.Witness;
   end M10_Reset_Role_And_Witness;

   function M11_Escrow_Role_And_Phase
     (Data : Q.Byte_Array; Roots : M.Root_State_Array;
      Current : C.Root_Reference; Caller : M.Actor) return Boolean
   is
      Projected : constant C.Store_Owner_Result :=
        C.Current_Store_Owner (Data, Roots, Current);
   begin
      return Caller = M.Collector and then Projected.Status = C.Projected
        and then Roots (Projected.Index).Phase = M.Front_Reconstruction;
   end M11_Escrow_Role_And_Phase;
end Worldline.Root_Custody_Mutation_Roles;
