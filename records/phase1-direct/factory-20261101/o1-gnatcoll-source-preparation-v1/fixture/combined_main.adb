with Ada.Command_Line;
with Ada.Exceptions;
with Ada.Text_IO;
with Fixture_Results;
with Lifecycle_Cases;
with Mailbox_Cases;

procedure Combined_Main is
begin
   Lifecycle_Cases.Run;
   Mailbox_Cases.Run;
   Fixture_Results.Complete;
   Ada.Command_Line.Set_Exit_Status (Ada.Command_Line.Success);
exception
   when Failure : others =>
      Ada.Command_Line.Set_Exit_Status (Ada.Command_Line.Failure);
      declare
         Name : constant String := Ada.Exceptions.Exception_Name (Failure);
      begin
         if Name'Length <= 128 then
            Ada.Text_IO.Put_Line
              (Ada.Text_IO.Standard_Error, "FAIL FIXTURE " & Name);
         else
            Ada.Text_IO.Put_Line
              (Ada.Text_IO.Standard_Error, "FAIL FIXTURE EXCEPTION_NAME_EXCESS");
         end if;
      end;
end Combined_Main;
