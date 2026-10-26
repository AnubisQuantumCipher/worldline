--  OUTSIDE PRODUCTION. SOURCE PROPOSAL ONLY; UNCOMPILED / UNPROVED / UNRUN.
with Worldline.Producer_Bytes;
package UTF8_Coordinator_Proposal with SPARK_Mode is
   function UTF8 (Bytes : String; Replace_Errors : Boolean)
      return Worldline.Producer_Bytes.Decoded
     with Global => null,
       Post => (if not UTF8'Result.Valid then UTF8'Result.Length = 0) and then
         (if Bytes'Length = 0 then
            UTF8'Result.Valid and then UTF8'Result.Length = 0);
end UTF8_Coordinator_Proposal;
