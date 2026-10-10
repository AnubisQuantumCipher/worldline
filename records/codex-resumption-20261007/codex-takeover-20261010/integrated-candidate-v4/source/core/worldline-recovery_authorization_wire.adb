package body Worldline.Recovery_Authorization_Wire with SPARK_Mode is
   function Decide (Raw : Raw_Request) return Raw_Result is
      Action : constant R.Recovery_Action := Selected_Action (Raw);
   begin
      return
        (Action => R.Recovery_Action'Pos (Action),
         State => R.Use_State'Pos
           (R.Next_State (R.Use_State'Val (Raw.State), Action)));
   end Decide;
end Worldline.Recovery_Authorization_Wire;
