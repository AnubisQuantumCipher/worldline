with Interfaces;
with Interfaces.C;
with Worldline.Recovery_Protocol_ABI;
with Worldline.Recovery_Protocol_Wire;

procedure Test_Protocol_Adapter with SPARK_Mode is
   package A renames Worldline.Recovery_Protocol_ABI;
   package W renames Worldline.Recovery_Protocol_Wire;
   use type Interfaces.C.int;
   use type W.Raw_Result;
   Output : W.Raw_Result;
   Status : Interfaces.C.int;
   Previous : constant W.Raw_Result := (After => Interfaces.Unsigned_8'Last);
begin
   --  Includes every raw field value, even values outside the native enums.
   for Before in Interfaces.Unsigned_8 loop
      for Cause in Interfaces.Unsigned_8 loop
         declare
            Request : constant W.Raw_Request := (Before, Cause);
         begin
            Output := Previous;
            A.Apply (Request, Output, Status);
            if W.Well_Formed (Request) then
               pragma Assert (Status = A.Success);
               pragma Assert (Output = W.Decide (Request));
            else
               pragma Assert (Status = A.Refused);
               pragma Assert (Output = Previous);
            end if;
         end;
      end loop;
   end loop;
end Test_Protocol_Adapter;
