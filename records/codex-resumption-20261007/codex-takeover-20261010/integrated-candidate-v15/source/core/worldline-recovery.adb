package body Worldline.Recovery with SPARK_Mode is
   function Matches
     (Expected : Identity_Bytes; Marker : Optional_Marker) return Boolean is
   begin
      return Marker.Present and then Marker.Value = Expected;
   end Matches;

   function Select_Action
     (Expected : Identity_Bytes; Live, Prepared : Optional_Marker)
      return Recovery_Action
   is
      Live_Matches : constant Boolean := Matches (Expected, Live);
      Prepared_Matches : constant Boolean := Matches (Expected, Prepared);
   begin
      if Live_Matches and then not Prepared_Matches then
         return Finish_Committed;
      elsif Prepared_Matches and then not Live_Matches then
         return Abort_Prepared;
      end if;
      return Ambiguous;
   end Select_Action;
end Worldline.Recovery;
