with Ada.Assertions;
with Fixture_Results;
with GNATCOLL.Email.Mailboxes;
with Input_Buffers;

package body Mailbox_Cases is
   procedure Run_D01 is
      use GNATCOLL.Email.Mailboxes;
      State_1, State_2, State_3 : Boolean;
   begin
      Ada.Assertions.Assert
        (Input_Buffers.D01'First = 1 and then Input_Buffers.D01'Length = 47);
      declare
         Box : Mbox;
      begin
         Open (Box, Input_Buffers.D01'Access, On_Close => null);
         declare
            Position : Cursor'Class := First (Box);
         begin
            State_1 := Has_Element (Position);
            Next (Position, Box);
            State_2 := Has_Element (Position);
            Next (Position, Box);
            State_3 := Has_Element (Position);
         end;
      end;
      --  Cursor and Box have left scope before reporting completion.
      Fixture_Results.Consumer_D01 (State_1, State_2, State_3);
      Ada.Assertions.Assert (State_1 and then State_2 and then not State_3);
   end Run_D01;

   procedure Run_D02 is
      use GNATCOLL.Email.Mailboxes;
      State_1, State_2 : Boolean;
   begin
      Ada.Assertions.Assert
        (Input_Buffers.D02'First = 1 and then Input_Buffers.D02'Length = 23);
      declare
         Box : Mbox;
      begin
         Open (Box, Input_Buffers.D02'Access, On_Close => null);
         declare
            Position : Cursor'Class := First (Box);
         begin
            State_1 := Has_Element (Position);
            Next (Position, Box);
            State_2 := Has_Element (Position);
         end;
      end;
      Fixture_Results.Consumer_D02 (State_1, State_2);
      Ada.Assertions.Assert (State_1 and then not State_2);
   end Run_D02;

   procedure Run is
   begin
      Run_D01;
      Run_D02;
   end Run;
end Mailbox_Cases;
