with Ada.Text_IO;
with Worldline.Root_Custody_Mutation_Roles;

--  UNEXECUTED source controls against shared-model-v2. No proof claim.
procedure Root_Custody_Context_Controls is
   package R renames Worldline.Root_Custody_Mutation_Roles;
   package D renames R.D;
   package C renames R.C;
   package M renames R.M;
   package Q renames R.Q;
   use type Q.Byte_Count;
   use type C.Context_Status;
   use type C.Physical_Status;
   use type D.Projection_Status;
   use type D.Reader_Projection;
   use type D.Writer_Phase_Projection;
   use type M.Owner;
   use type M.Actor;

   procedure Check (Condition : Boolean; Label : String) is
   begin
      --  Always active, independently of assertion policy.
      if not Condition then
         raise Program_Error with Label;
      end if;
   end Check;

   procedure Run (Width : Q.Byte_Index) is
      --  Finite fixture storage, NOT an accepted-domain or public value cap.
      --  The long invocation places its nonzero digit beyond machine words.
      Data : Q.Byte_Array (1 .. Width * 2 + 5) := (others => 0);
      Old_Gen : constant Q.Quantity :=
        (Negative => False, First => 1, Length => Width);
      New_Gen : constant Q.Quantity :=
        (Negative => False, First => Width + 1, Length => Width);
      Zero : constant Q.Quantity :=
        (Negative => False, First => 1, Length => 0);
      Other_Subgen : constant Q.Quantity :=
        (Negative => False, First => Width, Length => 1);
      function Id (Offset : Q.Byte_Index) return M.Identity is
        ((Present => True, Value => (First => Width * 2 + Offset, Length => 1)));
      Op : constant M.Identity := Id (1);
      Op_Alias : constant M.Identity := Id (2);
      Other_Op : constant M.Identity := Id (3);
      Desc : constant M.Identity := Id (4);
      Other_Desc : constant M.Identity := Id (5);
      Old_Head : constant M.Digest := (others => 1);
      New_Head : constant M.Digest := (others => 2);
      Desc_Head : constant M.Digest := (others => 3);
      Other_Head : constant M.Digest := (others => 4);
      Old_Row : M.Root_State :=
        (Generation => Old_Gen, Operation => Op, Phase => M.Ended,
         Before_Unknown => M.Front_Owned, Owners_Open => False,
         Abort_Kind => M.Dispatched,
         Physical => (Launched => True, Witness => True, others => False),
         Unknown_Cause => (Present => False), Reattach_Epoch => Zero,
         Head => Old_Head);
      New_Row : M.Root_State := Old_Row;
      Old_Ref : constant C.Root_Reference :=
        (Generation => Old_Gen, Operation => Op, Head => Old_Head);
      New_Ref : constant C.Root_Reference :=
        (Generation => New_Gen, Operation => Op, Head => New_Head);
      Roots : M.Root_State_Array (1 .. 2);
      Reference : C.Root_Reference;
      Owner : C.Store_Owner_Result;
      Physical : C.Physical_Actor_Result;
      Subject : M.Subject_State :=
        (Kind => M.Descriptor, Generation => Old_Gen, Subject => Desc,
         Subgeneration => Zero, Request => M.Queued, Descriptor => M.Released,
         Mode => M.None, Position => (Present => True, Value => Zero),
         Carried_From => (Present => False), Head => Desc_Head);
      Desc_Ref : constant D.Descriptor_Reference :=
        (Original_Root => Old_Ref, Subject => Desc,
         Subgeneration => Zero, Head => Desc_Head);
      Mutated_Desc_Ref : D.Descriptor_Reference;
      Subjects : M.Subject_State_Array (1 .. 1);
      Projection : D.Descriptor_Projection;

      procedure Reject_Descriptor
        (Value : D.Descriptor_Reference; Label : String) is
      begin
         Check (D.Project_Descriptor (Data, Roots, Subjects, Value).Status =
                  D.Binding_Not_Established, Label);
      end Reject_Descriptor;
   begin
      Data (Width) := 1;
      Data (Width * 2) := 2;
      Data (Width * 2 + 1) := Character'Pos ('o');
      Data (Width * 2 + 2) := Character'Pos ('o');
      Data (Width * 2 + 3) := Character'Pos ('x');
      Data (Width * 2 + 4) := Character'Pos ('d');
      Data (Width * 2 + 5) := Character'Pos ('e');
      New_Row.Generation := New_Gen;
      New_Row.Head := New_Head;
      New_Row.Phase := M.Prepared;
      New_Row.Owners_Open := True;
      New_Row.Physical := (others => False);
      Roots := (Old_Row, New_Row);
      Subjects := (1 => Subject);

      Owner := C.Current_Store_Owner (Data, Roots, New_Ref);
      Check (Owner.Status = C.Projected and then Owner.Index = 2 and then
               Owner.Value = M.Front, "CURRENT_WITH_REPEATED_OPERATION");
      Check (C.Current_Store_Owner (Data, Roots, Old_Ref).Status =
               C.Binding_Not_Established, "ENDED_IS_NOT_CURRENT_STORE");
      Physical := C.Physical_Actor (Data, Roots, Old_Ref);
      Check (Physical.Status = C.Physical_Projected and then
               Physical.Index = 1 and then Physical.Value = M.Collector,
             "ENDED_PHYSICAL_COLLECTOR_POSITIVE");
      Check (R.M10_Reset_Role_And_Witness (Data, Roots, Old_Ref, M.Collector),
             "ENDED_WITNESSED_COLLECTOR_RESET_ROLE");
      Roots (1).Owners_Open := True;
      Physical := C.Physical_Actor (Data, Roots, Old_Ref);
      Check (Physical.Status = C.Physical_Projected and then
               Physical.Value = M.Front, "ENDED_OWNERS_OPEN_PHYSICAL_FRONT");
      Roots (1) := Old_Row;

      Reference := New_Ref;
      Reference.Operation := Op_Alias;
      Check (C.Current_Store_Owner (Data, Roots, Reference).Status = C.Projected,
             "OPERATION_BYTES_EQUAL_AT_DISTINCT_STORAGE");
      Reference.Operation := Other_Op;
      Check (C.Current_Store_Owner (Data, Roots, Reference).Status =
               C.Binding_Not_Established, "CURRENT_OPERATION_MISMATCH");
      Reference := Old_Ref;
      Reference.Operation := Other_Op;
      Check (C.Physical_Actor (Data, Roots, Reference).Status =
               C.Physical_Binding_Not_Established, "PHYSICAL_OPERATION_MISMATCH");
      Reference := Old_Ref;
      Reference.Head := New_Head;
      Check (C.Physical_Actor (Data, Roots, Reference).Status =
               C.Physical_Binding_Not_Established, "CROSS_GENERATION_HEAD_SWAP");
      Reference := New_Ref;
      Reference.Head := Old_Head;
      Check (C.Current_Store_Owner (Data, Roots, Reference).Status =
               C.Binding_Not_Established, "CURRENT_HEAD_MISMATCH");
      Roots (1).Generation := New_Gen;
      Check (not C.Root_Roster_Consistent (Data, Roots), "DUPLICATE_GENERATION");
      Check (C.Current_Store_Owner (Data, Roots, New_Ref).Status =
               C.Binding_Not_Established, "DUPLICATE_GENERATION_NO_SELECTION");
      Roots (1) := Old_Row;
      Roots (2).Generation.Negative := True;
      Check (not C.Root_Roster_Consistent (Data, Roots), "NEGATIVE_GENERATION");
      Roots (2) := New_Row;
      Roots (2).Generation := Zero;
      Check (not C.Root_Roster_Consistent (Data, Roots), "ZERO_GENERATION");
      Roots (2) := New_Row;
      Roots (2).Generation :=
        (Negative => False, First => Data'Last, Length => 2);
      Check (not C.Root_Roster_Consistent (Data, Roots), "INVALID_SPAN_GENERATION");
      Roots (2) := New_Row;

      Projection := D.Project_Descriptor (Data, Roots, Subjects, Desc_Ref);
      Check (Projection.Status = D.Projected and then
               Projection.Read_Actor = D.Worker_Reader and then
               Projection.Write_Phase = D.Worker_Writer,
             "RELEASED_WORKER_POSITIVE");
      Check (R.M6_Descriptor_Role (Data, Roots, Subjects, Desc_Ref, M.Worker),
             "RELEASED_M6_WORKER");
      Check (not R.M6_Descriptor_Role (Data, Roots, Subjects, Desc_Ref, M.Front),
             "CURRENT_FRONT_CANNOT_READ_OLD_RELEASED_DESCRIPTOR");
      Mutated_Desc_Ref := Desc_Ref;
      Mutated_Desc_Ref.Original_Root := New_Ref;
      Reject_Descriptor (Mutated_Desc_Ref, "DESCRIPTOR_GENERATION_SPLICE");
      Mutated_Desc_Ref := Desc_Ref;
      Mutated_Desc_Ref.Original_Root.Operation := Other_Op;
      Reject_Descriptor (Mutated_Desc_Ref, "DESCRIPTOR_ROOT_OPERATION_SPLICE");
      Mutated_Desc_Ref := Desc_Ref;
      Mutated_Desc_Ref.Original_Root.Head := Other_Head;
      Reject_Descriptor (Mutated_Desc_Ref, "DESCRIPTOR_ROOT_HEAD_SPLICE");
      Mutated_Desc_Ref := Desc_Ref;
      Mutated_Desc_Ref.Subject := Other_Desc;
      Reject_Descriptor (Mutated_Desc_Ref, "DESCRIPTOR_SUBJECT_SPLICE");
      Mutated_Desc_Ref := Desc_Ref;
      Mutated_Desc_Ref.Subgeneration := Other_Subgen;
      Reject_Descriptor (Mutated_Desc_Ref, "DESCRIPTOR_SUBGENERATION_SPLICE");
      Mutated_Desc_Ref := Desc_Ref;
      Mutated_Desc_Ref.Head := Other_Head;
      Reject_Descriptor (Mutated_Desc_Ref, "DESCRIPTOR_HEAD_SPLICE");
      Subjects (1).Kind := M.Request;
      Reject_Descriptor (Desc_Ref, "SAME_ID_REQUEST_IS_NOT_DESCRIPTOR");
      Subjects (1) := Subject;

      Subjects (1).Descriptor := M.Front_Held;
      Check (R.M6_Descriptor_Role (Data, Roots, Subjects, Desc_Ref, M.Front),
             "FRONT_HELD_READER");
      Subjects (1).Descriptor := M.Stop_Intent;
      Check (R.M6_Descriptor_Role (Data, Roots, Subjects, Desc_Ref, M.Front),
             "STOP_INTENT_FRONT_READER_BEFORE_FREEZE");
      Subjects (1).Descriptor := M.Frozen;
      for Caller in M.Actor loop
         Check (not R.M6_Descriptor_Role
                  (Data, Roots, Subjects, Desc_Ref, Caller),
                "FROZEN_HAS_NO_READER");
      end loop;
      Subjects (1).Descriptor := M.Reclaimed;
      Check (R.M6_Descriptor_Role (Data, Roots, Subjects, Desc_Ref, M.Collector),
             "RECLAIMED_COLLECTOR_READER");
      Check (R.M6_Descriptor_Role (Data, Roots, Subjects, Desc_Ref, M.Reconciler),
             "RECLAIMED_RECONCILER_READER");
      Subjects (1) := Subject;

      declare
         Duplicate : M.Subject_State_Array := (Subject, Subject);
      begin
         Check (D.Project_Descriptor (Data, Roots, Duplicate, Desc_Ref).Status =
                  D.Binding_Not_Established, "DUPLICATE_SUBJECT_PRIMARY_KEY");
         Duplicate (2).Subgeneration := Other_Subgen;
         Duplicate (2).Head := Other_Head;
         Check (D.Project_Descriptor (Data, Roots, Duplicate, Desc_Ref).Status =
                  D.Binding_Not_Established,
                "DUPLICATE_KEY_DIFFERENT_SUBGENERATION_HEAD");
         Duplicate (2).Generation := New_Gen;
         Check (D.Project_Descriptor (Data, Roots, Duplicate, Desc_Ref).Status =
                  D.Projected, "SAME_SUBJECT_ID_IN_DIFFERENT_GENERATION");
      end;
      declare
         Reversed : constant M.Root_State_Array := (New_Row, Old_Row);
      begin
         Owner := C.Current_Store_Owner (Data, Reversed, New_Ref);
         Check (Owner.Status = C.Projected and then Owner.Index = 1,
                "CURRENT_SELECTION_NOT_ARRAY_POSITION");
         Check (D.Project_Descriptor (Data, Reversed, Subjects, Desc_Ref).Status =
                  D.Projected, "ORIGINAL_ROOT_SELECTION_NOT_ARRAY_POSITION");
      end;
   end Run;
begin
   Run (1);
   Run (Q.Byte_Index (Long_Long_Integer'Size));
   Ada.Text_IO.Put_Line ("ROOT_CUSTODY_CONTEXT_CONTROLS_PASS");
end Root_Custody_Context_Controls;
