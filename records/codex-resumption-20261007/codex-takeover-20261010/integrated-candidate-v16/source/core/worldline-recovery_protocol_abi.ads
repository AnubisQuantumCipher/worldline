with Interfaces.C;
with Worldline.Recovery_Protocol_Wire;

package Worldline.Recovery_Protocol_ABI with SPARK_Mode is
   package W renames Worldline.Recovery_Protocol_Wire;
   use type Interfaces.C.int;
   use type W.Raw_Result;

   Success : constant Interfaces.C.int := 0;
   Refused : constant Interfaces.C.int := -1;

   --  Total value adapter. Physical foreign memory is not modeled here.
   --  No precondition excludes malformed raw fields or prior output values.
   procedure Apply
     (Request : W.Raw_Request;
      Output : in out W.Raw_Result;
      Status : out Interfaces.C.int)
     with Global => null,
       Depends => (Output => (Request, Output), Status => Request),
       Post =>
         (if W.Well_Formed (Request) then
             Status = Success and then Output = W.Decide (Request)
          else
             Status = Refused and then Output = Output'Old);
end Worldline.Recovery_Protocol_ABI;
