with Worldline.Custody_V2_Load_Input;
--  Fresh protected-issuer startup correspondence. The protected acquisition
--  roster remains an independent prerequisite; authority is metadata only.
package Worldline.Startup_Issuer_Source with SPARK_Mode is
   package L renames Worldline.Custody_V2_Load_Input;
   package E renames L.E;
   function Corresponds (Data : E.Bytes; Roster, Profile : E.Span)
      return Boolean with Global => null;
end Worldline.Startup_Issuer_Source;
