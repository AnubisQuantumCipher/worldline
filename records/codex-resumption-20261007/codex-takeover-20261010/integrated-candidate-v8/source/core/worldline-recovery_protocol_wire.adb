package body Worldline.Recovery_Protocol_Wire with SPARK_Mode is
   function Decide (Raw : Raw_Request) return Raw_Result is
     ((After => P.State'Pos
        (P.Advance (P.State'Val (Raw.Before), P.Event'Val (Raw.Cause)))));
end Worldline.Recovery_Protocol_Wire;
