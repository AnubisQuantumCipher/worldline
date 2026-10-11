package body Worldline.Evaluation_Wire with SPARK_Mode is
   function Decode (Raw : Raw_Record) return Decode_Result is
   begin
      if not Well_Formed (Raw) then return (Valid => False); end if;
      return (Valid => True, Value =>
        (Facts =>
          (Source => E.Origin'Val (Integer (Raw.Observations (Source_Field))),
           Status => E.Raw_Status'Val (Integer (Raw.Observations (Status_Field))),
           Channel => E.Channel_State'Val (Integer (Raw.Observations (Channel_Field))),
           Stage => E.Rejection_Stage'Val (Integer (Raw.Observations (Stage_Field))),
           Exit_Present => Raw.Observations (Exit_Present_Field) = 1,
           Exit_Integer => Raw.Observations (Exit_Integer_Field) = 1,
           Supervisor => E.Supervision_State'Val (Integer (Raw.Observations (Supervisor_Field))),
           Supervisor_Stopped => Raw.Observations (Supervisor_Stopped_Field) = 1,
           Bundle_Present => Raw.Observations (Bundle_Present_Field) = 1,
           Bundle_Is_Mapping => Raw.Observations (Bundle_Is_Mapping_Field) = 1,
           Bundle_Stable => Raw.Observations (Bundle_Stable_Field) = 1,
           Bundle_Changed => Raw.Observations (Bundle_Changed_Field) = 1,
           Unsatisfied_Imports => Raw.Observations (Unsatisfied_Imports_Field) = 1,
           Isolation => E.Examiner_Isolation'Val (Integer (Raw.Observations (Isolation_Field)))),
         Report_Based => Raw.Report_Based = 1,
         Report_Facts =>
           (Private_Profile => Raw.Report_Facts (R.Private_Profile_Fact) = 1,
            Exit_Integer_Nonnegative => Raw.Report_Facts (R.Exit_Integer_Nonnegative_Fact) = 1,
            Records_Present => Raw.Report_Facts (R.Records_Present_Fact) = 1,
            Channel_Daemon_Accepted => Raw.Report_Facts (R.Channel_Daemon_Accepted_Fact) = 1,
            Supervision_Clean => Raw.Report_Facts (R.Supervision_Clean_Fact) = 1,
            Boundary_Consistent => Raw.Report_Facts (R.Boundary_Consistent_Fact) = 1,
            Report_Mount_Exclusive => Raw.Report_Facts (R.Report_Mount_Exclusive_Fact) = 1,
            Collected_Privately => Raw.Report_Facts (R.Collected_Privately_Fact) = 1,
            Identities_Match => Raw.Report_Facts (R.Identities_Match_Fact) = 1,
            Digest_Matches => Raw.Report_Facts (R.Digest_Matches_Fact) = 1,
            Examiner_Observed => Raw.Report_Facts (R.Examiner_Observed_Fact) = 1,
            Workers_Separated => Raw.Report_Facts (R.Workers_Separated_Fact) = 1,
            Status_Rederived => Raw.Report_Facts (R.Status_Rederived_Fact) = 1,
            Examiner_Audit_Clean => Raw.Report_Facts (R.Examiner_Audit_Clean_Fact) = 1),
         Presence =>
           (Record_Identified => Raw.Presence (Record_Identified_Field) = 1,
            Verdict_Recorded => Raw.Presence (Verdict_Recorded_Field) = 1,
            Binding_Established => Raw.Presence (Binding_Established_Field) = 1,
            Declaration_Matches => Raw.Presence (Declaration_Matches_Field) = 1,
            Bundle_Identified => Raw.Presence (Bundle_Identified_Field) = 1)));
   end Decode;

   function Classify_Wire (Raw : Raw_Record) return Wire_Classification is
      D : constant Decode_Result := Decode (Raw);
   begin
      if not D.Valid then return Invalid_Classification; end if;
      declare
         V : constant E.Classification := E.Classify (D.Value.Facts);
      begin
         return (0, E.Execution_State'Pos (V.Execution),
                 E.Outcome'Pos (V.Result), E.Bundle_Integrity'Pos (V.Bundle));
      end;
   end Classify_Wire;

   function Admit_Wire (Raw : Raw_Record) return Byte is
      D : constant Decode_Result := Decode (Raw);
   begin
      if not D.Valid then return Invalid_Record; end if;
      declare
         V : constant E.Classification := E.Classify (D.Value.Facts);
         Report : constant E.Report_Integrity :=
           E.Report_Integrity_Of (D.Value.Report_Based, V, D.Value.Report_Facts);
      begin
         if E.Admissible (V, Report, D.Value.Presence) then return 1; end if;
         return 0;
      end;
   end Admit_Wire;

   function Confined_Admit_Wire (Raw : Raw_Record; Confinement : Byte) return Byte is
      D : constant Decode_Result := Decode (Raw);
   begin
      if not D.Valid or else Confinement > E.Confinement_Observation'Pos
          (E.Confinement_Observation'Last) then return Invalid_Record; end if;
      if D.Value.Facts.Source = E.External and then Confinement /=
        E.Confinement_Observation'Pos (E.F.Confinement_Established) then return 0; end if;
      declare
         V : constant E.Classification := E.Classify (D.Value.Facts);
         Report : constant E.Report_Integrity := E.Confined_Report_Integrity_Of
           (D.Value.Report_Based, V, D.Value.Report_Facts,
            E.Confinement_Observation'Val (Integer (Confinement)));
      begin
         if E.Admissible (V, Report, D.Value.Presence) then return 1; end if;
         return 0;
      end;
   end Confined_Admit_Wire;

   function Roster_Wire
     (Rows : Raw_Array; Empty_Declared : Byte; Completion : Raw_Record) return Byte is
   begin
      if not Roster_Well_Formed (Rows, Empty_Declared, Completion) then return Invalid_Record; end if;
      if not Completion_Admitted (Completion) then return 0; end if;
      if Rows'Length = 0 then return Empty_Declared; end if;
      for I in Rows'Range loop
         if Admit_Wire (Rows (I)) /= 1 then return 0; end if;
         pragma Loop_Invariant (for all J in Rows'First .. I => Admitted (Rows (J)));
      end loop;
      return 1;
   end Roster_Wire;

   function Roster_Wire (Raw : Raw_Roster) return Byte is
   begin
      if not Well_Formed (Raw) then return Invalid_Record; end if;
      if not Completion_Admitted (Raw.Completion) then return 0; end if;
      if Count_Of (Raw) = 0 then return Raw.Empty_Declared; end if;
      for I in Slot loop
         if I <= Count_Of (Raw) and then Admit_Wire (Raw.Rows (I)) /= 1 then return 0; end if;
         pragma Loop_Invariant (for all J in Slot'First .. I =>
           (if J <= Count_Of (Raw) then Admitted (Raw.Rows (J))));
      end loop;
      return 1;
   end Roster_Wire;
end Worldline.Evaluation_Wire;
