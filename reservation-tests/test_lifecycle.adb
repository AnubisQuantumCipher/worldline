with Ada.Text_IO;
with Resource_Reservation_Lifecycle;
with Worldline.Resources;
procedure Test_Lifecycle is
   package L renames Resource_Reservation_Lifecycle;
   package R renames Worldline.Resources;
   use type L.Removal_Array;
   use type L.Result_Status;
   Data : constant R.Byte_Array (5 .. 6) :=
     [R.Byte (Character'Pos ('a')), R.Byte (Character'Pos ('b'))];
   Rows : constant L.Entry_Array (8 .. 9) :=
     [((5, 1), L.Unknown), ((6, 1), L.Gone)];
   Mask : L.Removal_Array (21 .. 22) := [True, True];
   Status : L.Result_Status;
begin
   L.Plan (Data, Rows, (True, (6, 1)), L.Release_Exact, Mask, Status);
   pragma Assert (Status = L.Removal_Planned and Mask = [False, True]);
   L.Plan (Data, Rows, (Present => False), L.Reconcile_Observed, Mask, Status);
   pragma Assert (Status = L.Removal_Planned and Mask = [False, True]);
   L.Plan (Data, Rows, (True, (7, 1)), L.Release_Exact, Mask, Status);
   pragma Assert (Status = L.Invalid_Input and Mask = [False, True]);
   L.Plan (Data, Rows, (Present => False), L.Unknown_Operation, Mask, Status);
   pragma Assert (Status = L.Invalid_Input and Mask = [False, True]);
   declare
      Short : L.Removal_Array (4 .. 4) := [True];
   begin
      L.Plan (Data, Rows, (Present => False), L.Reconcile_Observed, Short, Status);
      pragma Assert (Status = L.Invalid_Output_Layout and Short = [True]);
   end;
   declare
      Empty_Data : R.Byte_Array (3 .. 2);
      Empty_Rows : L.Entry_Array (8 .. 7);
      Empty_Mask : L.Removal_Array (21 .. 20);
   begin
      L.Plan (Empty_Data, Empty_Rows, (Present => False),
              L.Reconcile_Observed, Empty_Mask, Status);
      pragma Assert (Status = L.No_Change);
   end;
   Ada.Text_IO.Put_Line ("PASS ordinary typed arbitrary-bound and refusal-preservation controls");
end Test_Lifecycle;
