with Interfaces;
with Worldline.Ordinary_Reservation_Lifecycle;

--  Unintegrated checked ghost result replay. No invocation of Plan, Python
--  acquisition, resource arithmetic or output publication occurs here.
package Worldline.Ordinary_Reservation_Replay with SPARK_Mode, Ghost is
   --  Full original input domain: no new Pre or input/row limit. Expected
   --  output is derived from captured input, never from the supplied Mask.
   --  Equality to the earlier declarative Plan_Conforms and establishment by
   --  the production Plan are explicit UNPROVED obligations, not assumptions.
   function Conforms
     (Data : String;
      Mask : Worldline.Ordinary_Reservation_Lifecycle.Mask_Array;
      Code : Interfaces.Unsigned_32; Position : Natural) return Boolean
   with Global => null;
end Worldline.Ordinary_Reservation_Replay;
