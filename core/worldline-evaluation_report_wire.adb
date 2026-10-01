package body Worldline.Evaluation_Report_Wire with SPARK_Mode is
   function Decode (Raw : Raw_Record) return Decode_Result is
   begin
      if not Well_Formed (Raw) then
         return (Valid => False);
      end if;
      return
        (Valid => True,
         Value =>
           (Report_Based => Raw.Report_Based = 1,
            Value =>
              (Execution => E.Execution_State'Val (Raw.Execution),
               Result    => E.Outcome'Val (Raw.Result),
               Bundle    => F.Bundle_Observation'Val (Raw.Bundle)),
            Facts =>
              (Private_Profile => Raw.Facts (Private_Profile_Fact) = 1,
               Exit_Integer_Nonnegative =>
                 Raw.Facts (Exit_Integer_Nonnegative_Fact) = 1,
               Records_Present => Raw.Facts (Records_Present_Fact) = 1,
               Channel_Daemon_Accepted =>
                 Raw.Facts (Channel_Daemon_Accepted_Fact) = 1,
               Supervision_Clean => Raw.Facts (Supervision_Clean_Fact) = 1,
               Boundary_Consistent => Raw.Facts (Boundary_Consistent_Fact) = 1,
               Report_Mount_Exclusive =>
                 Raw.Facts (Report_Mount_Exclusive_Fact) = 1,
               Collected_Privately => Raw.Facts (Collected_Privately_Fact) = 1,
               Identities_Match => Raw.Facts (Identities_Match_Fact) = 1,
               Digest_Matches => Raw.Facts (Digest_Matches_Fact) = 1,
               Examiner_Observed => Raw.Facts (Examiner_Observed_Fact) = 1,
               Workers_Separated => Raw.Facts (Workers_Separated_Fact) = 1,
               Status_Rederived => Raw.Facts (Status_Rederived_Fact) = 1,
               Examiner_Audit_Clean => Raw.Facts (Examiner_Audit_Clean_Fact) = 1),
            Confinement => F.Confinement_Observation'Val (Raw.Confinement)));
   end Decode;

   function Integrity_Wire (Raw : Raw_Record) return Byte is
      Decoded : constant Decode_Result := Decode (Raw);
   begin
      if not Decoded.Valid then
         return Invalid_Record;
      end if;
      return E.Report_Integrity'Pos
        (F.Report_Integrity_Of
           (Decoded.Value.Report_Based, Decoded.Value.Value,
            Decoded.Value.Facts));
   end Integrity_Wire;

   function Confined_Integrity_Wire (Raw : Raw_Record) return Byte is
      Decoded : constant Decode_Result := Decode (Raw);
   begin
      if not Decoded.Valid then
         return Invalid_Record;
      end if;
      return E.Report_Integrity'Pos
        (F.Confined_Report_Integrity_Of
           (Decoded.Value.Report_Based, Decoded.Value.Value,
            Decoded.Value.Facts, Decoded.Value.Confinement));
   end Confined_Integrity_Wire;
end Worldline.Evaluation_Report_Wire;
