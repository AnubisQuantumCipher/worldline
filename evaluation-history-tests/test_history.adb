with Evaluation_History;
with Resource_Quantities;

procedure Test_History is
   package H renames Evaluation_History;
   use H;
   A : constant Resource_Quantities.Byte_Array (5 .. 8) :=
     [Character'Pos ('s'), Character'Pos ('r'), Character'Pos ('r'), 1];
   F : constant Optional_Record :=
     (Present => True, Value =>
        (Subject => (True, (5, 1)), Content => (True, (5, 1)),
         Requirement => (True, (5, 1)), Run => (True, (5, 1)),
         Sequence => (True, (5, 0)), State => Completed, Outcome => Passed));
   R : constant Evaluation_Record :=
     (Subject => (True, (5, 1)), Content => (True, (5, 1)),
      Requirement => (True, (5, 1)), Run => (True, (6, 1)),
      Sequence => (True, (8, 1)), State => Completed, Outcome => Passed);
   Rows : History (9 .. 9) := [9 => R];
   Q : Query :=
     (Subject => (True, (5, 1)), Content => (True, (5, 1)),
      Requirement => (True, (5, 1)),
      Current_Head => (True, ((True, (8, 1)), (7, 1))),
      Prepared_Evidence => (True, ((True, (8, 1)), (7, 1))));
   S : Selection;
   Empty : constant History (9 .. 8) := [others => R];
   Zero_Bytes : constant Resource_Quantities.Byte_Array (13 .. 14) := [0, 0];
   Counts : constant Resource_Quantities.Byte_Array (17 .. 19) := [1, 0, 2];
   -- Ordinary connected carry chain and padded representation, based on
   -- retained JACKAL status=exact expressions; not a formal code oracle.
   Carry_Bytes : constant Resource_Quantities.Byte_Array (21 .. 33) :=
     [255, 255, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1];
begin
   -- Epoch padding has numeric meaning, separate from full string identity.
   -- Successor fixture uses retained JACKAL status=exact parsed=1+1 exact=2.
   pragma Assert (Same_Epoch (Zero_Bytes, (13, 0), (13, 2)));
   pragma Assert (Epoch_Zero (Zero_Bytes, (13, 2)));
   pragma Assert (Epoch_One (Counts, (17, 2)));
   pragma Assert (Next_Epoch (Counts, (17, 2), (19, 1)));
   pragma Assert (not Next_Epoch (Counts, (19, 1), (17, 2)));
   --  [255,255] -> [0,0,1] -> [1,0,1], with an equivalent padded head.
   pragma Assert (Next_Epoch (Carry_Bytes, (21, 2), (23, 3)));
   pragma Assert (Next_Epoch (Carry_Bytes, (21, 2), (26, 5)));
   pragma Assert (Same_Epoch (Carry_Bytes, (23, 3), (26, 5)));
   pragma Assert (Next_Epoch (Carry_Bytes, (26, 5), (31, 3)));
   pragma Assert (not Next_Epoch (Carry_Bytes, (21, 2), (23, 2)));
   pragma Assert (not Next_Epoch (Carry_Bytes, (21, 2), (31, 3)));
   pragma Assert (not Next_Epoch (Carry_Bytes, (31, 3), (26, 5)));
   -- Equal full run bytes at distinct offsets; arbitrary non-one input bounds.
   S := Select_Evidence (A, Rows, F, Q);
   pragma Assert (S.Reason = Ready and then S.Head = (History_Entry, 9));
   pragma Assert (S.Completed_Failure.Kind = Absent);
   Rows (9).Outcome := Failed;
   S := Select_Evidence (A, Rows, F, Q);
   pragma Assert (S.Reason = Evidence_Fail_Terminal);
   pragma Assert (S.Completed_Failure = (History_Entry, 9));
   Rows (9).Sequence := (Present => False);
   S := Select_Evidence (A, Rows, F, Q);
   pragma Assert (S.Reason = History_Invalid and then S.Head.Kind = Absent);
   Q.Current_Head := (True, ((True, (5, 0)), (5, 1)));
   Q.Prepared_Evidence := Q.Current_Head;
   S := Select_Evidence (A, Empty, F, Q);
   pragma Assert (S.Reason = Ready and then S.Head.Kind = Finalization);
   Q.Subject := (True, (8, 2));
   S := Select_Evidence (A, Empty, F, Q);
   pragma Assert (S.Reason = Input_Invalid);
   Q.Current_Head := (True, ((Present => False), (5, 1)));
   S := Select_Evidence (A, Empty, F, Q);
   pragma Assert (S.Reason = Input_Absent);
end Test_History;
