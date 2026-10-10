with Worldline.Root_Custody_Context;

--  M6 and the PHASE component of M7 only. These are value projections,
--  not Mutation_Allowed: M7 still needs the authentic write interval fold,
--  actual stop flag and actor-gone evidence. No synthetic Ready inputs.
--  Termination remains REQUIRED for every precondition-satisfying input:
--  these ordinary side-effect-free SPARK functions have the intrinsic
--  termination obligation documented by this toolchain's E0016. Explicit
--  per-function Always_Terminates is illegal here; no obligation is waived.
package Worldline.Root_Custody_Descriptor with SPARK_Mode is
   package C renames Worldline.Root_Custody_Context;
   package M renames C.M;
   package Q renames M.Q;
   package L renames M.L;
   use type C.Physical_Status;
   use type Q.Ordering;
   use type Q.Byte_Count;
   use type M.Subject_Kind;
   use type M.Descriptor_Phase;
   use type Worldline.Hash;

   type Descriptor_Reference is record
      Original_Root : C.Root_Reference;
      Subject       : M.Identity;
      Subgeneration : Q.Quantity;
      Head          : M.Digest;
   end record;
   type Reader_Projection is
     (No_Reader, Front_Reader, Worker_Reader, Collector_Or_Reconciler_Reader);
   type Writer_Phase_Projection is (No_Writer, Front_Writer, Worker_Writer);
   type Projection_Status is (Projected, Binding_Not_Established);
   type Descriptor_Projection
     (Status : Projection_Status := Binding_Not_Established)
   is record
      case Status is
         when Projected =>
            Index        : Q.Byte_Index;
            Read_Actor   : Reader_Projection;
            Write_Phase  : Writer_Phase_Projection;
         when Binding_Not_Established => null;
      end case;
   end record;

   function Subject_Key_Joined
     (Data : Q.Byte_Array; State : M.Subject_State;
      Reference : Descriptor_Reference) return Boolean is
     (State.Kind = M.Descriptor and then
      C.Generation_Valid (Data, State.Generation) and then
      C.Generation_Valid (Data, Reference.Original_Root.Generation) and then
      Q.Compare (Data, State.Generation,
                 Reference.Original_Root.Generation) = Q.Equal and then
      L.Same (Data, State.Subject, Reference.Subject))
   with Global => null;

   function Subject_Joined
     (Data : Q.Byte_Array; State : M.Subject_State;
      Reference : Descriptor_Reference) return Boolean is
     (State.Kind = M.Descriptor and then
      C.Generation_Valid (Data, State.Generation) and then
      C.Generation_Valid (Data, Reference.Original_Root.Generation) and then
      Q.Compare (Data, State.Generation,
                 Reference.Original_Root.Generation) = Q.Equal and then
      L.Same (Data, State.Subject, Reference.Subject) and then
      Q.Span_Valid (Data, State.Subgeneration) and then
      not Q.Is_Negative (Data, State.Subgeneration) and then
      Q.Span_Valid (Data, Reference.Subgeneration) and then
      not Q.Is_Negative (Data, Reference.Subgeneration) and then
      Q.Compare (Data, State.Subgeneration, Reference.Subgeneration) = Q.Equal
      and then State.Head = Reference.Head)
   with Global => null;

   --  Bind against the original root (possibly Ended) and precisely one
   --  subject row; do not use the current root's store owner for descriptors.
   --  Complete/authentic fold remains a consuming native decision obligation.
   function Project_Descriptor
     (Data : Q.Byte_Array; Roots : M.Root_State_Array;
      Subjects : M.Subject_State_Array; Reference : Descriptor_Reference)
      return Descriptor_Projection
   with Global => null,
     Post =>
       (if C.Physical_Actor (Data, Roots, Reference.Original_Root).Status =
           C.Physical_Projected and then
           (for some I in Subjects'Range =>
              Subject_Joined (Data, Subjects (I), Reference) and then
              (for all J in Subjects'Range =>
                 (if J /= I then
                    not Subject_Key_Joined (Data, Subjects (J), Reference))))
        then Project_Descriptor'Result.Status = Projected and then
          Project_Descriptor'Result.Index in Subjects'Range and then
          Subject_Joined
            (Data, Subjects (Project_Descriptor'Result.Index), Reference)
          and then Project_Descriptor'Result.Read_Actor =
            (case Subjects (Project_Descriptor'Result.Index).Descriptor is
               when M.Front_Held | M.Stop_Intent => Front_Reader,
               when M.Intake | M.Released => Worker_Reader,
               when M.Reclaimed => Collector_Or_Reconciler_Reader,
               when M.Frozen | M.Ofd_Evidence | M.Abandoned => No_Reader)
          and then Project_Descriptor'Result.Write_Phase =
            (case Subjects (Project_Descriptor'Result.Index).Descriptor is
               when M.Front_Held => Front_Writer,
               when M.Intake | M.Released => Worker_Writer,
               when M.Stop_Intent | M.Frozen | M.Ofd_Evidence |
                    M.Abandoned | M.Reclaimed => No_Writer)
        else Project_Descriptor'Result.Status = Binding_Not_Established);
end Worldline.Root_Custody_Descriptor;
