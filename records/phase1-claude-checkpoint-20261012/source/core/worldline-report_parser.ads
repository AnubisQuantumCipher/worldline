package Worldline.Report_Parser with SPARK_Mode is
   type Report_Status is (Pass, Fail, Unsupported);
   type Classification is
     (Parsed, Missing_Report, DTD_Forbidden, Invalid_XML, No_Suites,
      Inconsistent_Counts, Missing_Total, Invalid_Total_Row,
      Invalid_Total_Counts, Invalid_JSON, Invalid_Schema, Non_Numeric,
      Non_Finite, Unsupported_Format);
   type Parsed_Report (Diagnostic_Length : Natural) is record
      Status : Report_Status;
      Class : Classification;
      Diagnostic : String (1 .. Diagnostic_Length);
   end record;
   -- Original byte strings, not normalized text or caller classifications.
   -- Exit_Code is the original integer's unbounded signed decimal ASCII
   -- transport. Native zero recognition does not construct its magnitude.
   -- Presence distinguishes a missing file from an acquired empty file.
   -- Diagnostic is the native JSON _parse result; no Python policy.
   function Parse
     (Format, Profile, Exit_Code : String;
      Stdout, Stderr, Result : String; Result_Present : Boolean)
      return Parsed_Report
     with Global => null,
       Post => (if Parse'Result.Status = Unsupported then
                  Parse'Result.Class = Unsupported_Format) and then
               Parse'Result.Diagnostic'First = 1;
end Worldline.Report_Parser;
