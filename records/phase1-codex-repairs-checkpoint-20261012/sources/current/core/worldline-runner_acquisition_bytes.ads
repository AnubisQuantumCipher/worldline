with Worldline.Archive_Envelope;
--  Complete original raw-wait/EOF/control and owner-generation closure over
--  independently owned lossless Finalization allocations. No joined arena,
--  serialization, filtered roster, integer-only wait or caller completion bit.
package Worldline.Runner_Acquisition_Bytes with SPARK_Mode is
   package E renames Worldline.Archive_Envelope;
   function Closed
     (Subject_Data, Owners_Data, Acquisition_Data : E.Bytes;
      Subject, Owners, Raw_Acquisitions : E.Span) return Boolean
     with Global => null;
end Worldline.Runner_Acquisition_Bytes;
