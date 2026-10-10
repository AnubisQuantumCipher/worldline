package Worldline.Native_Lifetime_Observation with SPARK_Mode is
   -- Re-decode the original complete C records, packets, acknowledgements,
   -- identity, EOF and descriptor cleanup. No saved terminal/status decision.
   function Clean (Raw_Acquisitions, Result_Record, Actual_Wait : String)
      return Boolean with Global => null;
end Worldline.Native_Lifetime_Observation;
