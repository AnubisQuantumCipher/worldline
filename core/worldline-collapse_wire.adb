package body Worldline.Collapse_Wire with SPARK_Mode is

   function Decide_Wire (R : Raw_Request) return Byte is
   begin
      if not Well_Formed (R) then
         return Invalid_Request;
      end if;
      return Byte (Collapse.Decision'Pos (Collapse.Decide (Decode (R))));
   end Decide_Wire;

end Worldline.Collapse_Wire;
