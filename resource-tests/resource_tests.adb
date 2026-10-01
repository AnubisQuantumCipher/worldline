with Ada.Text_IO;
with Worldline.Resources;

procedure Resource_Tests is
   use Worldline.Resources;
   use type Byte;
   Zero : constant Byte_Array := [0];
   Empty : constant Byte_Array (1 .. 0) := [];
   Large : Byte_Array (1 .. 33) := [others => 0];
   Smaller : Byte_Array (1 .. 32) := [others => 0];

   procedure Check (Name : String; Condition : Boolean) is
   begin
      if not Condition then
         raise Program_Error with Name;
      end if;
      Ada.Text_IO.Put_Line ("PASS " & Name);
   end Check;
begin
   Check ("empty amounts denote zero",
          Can_Reserve (Empty, Empty, Empty, Empty));
   Check ("inclusive exact sum",
          Can_Reserve ([10], [2], [3], [5]));
   Check ("insufficient headroom",
          not Can_Reserve ([10], [2], [3], [6]));
   Check ("unmetered request retains floor",
          not Can_Reserve ([2], Zero, [3], Zero));
   Check ("carry across byte at equality",
          Can_Reserve ([0, 1], [255], Zero, [1]));
   Check ("carry above available",
          not Can_Reserve ([0, 1], [255], Zero, [2]));
   Check ("sum exceeds all represented available digits",
          not Can_Reserve ([255], [255], [255], [255]));
   Check ("leading zeroes preserve equality",
          Can_Reserve ([10], [2, 0, 0], [3, 0], [5, 0]));
   Check ("arbitrary array lower bounds",
          Can_Reserve ([9 => 10], [4 => 2], [8 => 3], [12 => 5]));
   Large (Large'Last) := 1;
   Smaller (Smaller'Last) := 1;
   Check ("quantity beyond machine word accepts smaller",
          Can_Reserve (Large, Zero, Zero, Smaller));
   Check ("quantity beyond machine word refuses larger",
          not Can_Reserve (Smaller, Zero, Zero, Large));
   Check ("large equality remains inclusive",
          Can_Reserve (Large, Zero, Zero, Large));
   declare
      Column : constant Column_Result := Subtract_Column (0, 255, 255, 255, 3);
   begin
      Check ("maximal column debit conservation",
             Column.Remainder = 0 and Column.Next = 3);
   end;
   declare
      State : Reservation_State (2) :=
        (Capacity => 2, Available => [10, 0], Floor => [3, 0],
         Outstanding => [2, 0]);
      Accepted : Boolean;
   begin
      Try_Reserve (State, [5], Accepted);
      Check ("reserve exact outstanding sum",
             Accepted and State.Outstanding = Byte_Array'[7, 0]);
      declare
         Before : constant Reservation_State := State;
      begin
         Try_Reserve (State, [1], Accepted);
         Check ("refusal preserves whole state",
                not Accepted and State = Before);
      end;
   end;
   declare
      State : Reservation_State (2) :=
        (Capacity => 2, Available => [0, 1], Floor => [0, 0],
         Outstanding => [255, 0]);
      Accepted : Boolean;
   begin
      Try_Reserve (State, [1, 0, 0], Accepted);
      Check ("reserve carry and redundant request storage",
             Accepted and State.Outstanding = Byte_Array'[0, 1]);
   end;
   Ada.Text_IO.Put_Line ("ALL ORDINARY RESOURCE CASES PASSED");
end Resource_Tests;
