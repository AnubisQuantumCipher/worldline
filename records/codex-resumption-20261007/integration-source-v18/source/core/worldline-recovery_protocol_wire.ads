with Interfaces;
with Worldline.Recovery_Protocol;
package Worldline.Recovery_Protocol_Wire with SPARK_Mode is
   use type Interfaces.Unsigned_8;
   package P renames Worldline.Recovery_Protocol;
   type Raw_Request is record
      Before, Cause : Interfaces.Unsigned_8;
   end record with Convention => C;
   type Raw_Result is record
      After : Interfaces.Unsigned_8;
   end record with Convention => C;
   function Well_Formed (Raw : Raw_Request) return Boolean is
     (Raw.Before <= P.State'Pos (P.State'Last)
      and then Raw.Cause <= P.Event'Pos (P.Event'Last)) with Global => null;
   function Decide (Raw : Raw_Request) return Raw_Result
     with Global => null, Pre => Well_Formed (Raw),
       Post => Decide'Result.After =
         P.State'Pos (P.Advance (P.State'Val (Raw.Before), P.Event'Val (Raw.Cause)));
end Worldline.Recovery_Protocol_Wire;
