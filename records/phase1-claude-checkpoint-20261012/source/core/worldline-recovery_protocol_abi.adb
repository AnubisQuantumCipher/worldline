package body Worldline.Recovery_Protocol_ABI with SPARK_Mode is
   procedure Apply
     (Request : W.Raw_Request;
      Output : in out W.Raw_Result;
      Status : out Interfaces.C.int)
   is
   begin
      if W.Well_Formed (Request) then
         Output := W.Decide (Request);
         Status := Success;
      else
         Status := Refused;
      end if;
   end Apply;
end Worldline.Recovery_Protocol_ABI;
