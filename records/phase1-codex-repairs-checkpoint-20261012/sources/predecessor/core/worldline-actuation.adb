package body Worldline.Actuation with SPARK_Mode is

   function Decide (Facts : Request) return Decision is
   begin
      if Collapse.Decide (Facts.Collapse_Facts) /= Collapse.Authorized then
         return Collapse_Denied;
      elsif not Same_Entry (Facts.Expected_Live, Facts.Observed_Live) then
         return Live_Changed;
      elsif not Same_Entry (Facts.Expected_Stage, Facts.Observed_Stage) then
         return Stage_Changed;
      elsif Same_Entry (Facts.Observed_Live, Facts.Observed_Stage) then
         return Same_Entry_Refused;
      elsif Facts.Expected_Marker_Digest = Zero_Hash
        or else Facts.Expected_Marker_Digest /= Facts.Observed_Marker_Digest
      then
         return Marker_Mismatch;
      elsif not Facts.Payload_Durable then
         return Payload_Not_Durable;
      elsif not Facts.Recovery_Clean then
         return Recovery_Unclean;
      else
         return Authorized;
      end if;
   end Decide;

end Worldline.Actuation;
