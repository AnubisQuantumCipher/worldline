with Ada.Text_IO;
with Worldline.Evaluation;
with Worldline.Evaluation_Report_Facts;
with Worldline.Evaluation_Report_Wire;

--  Ordinary, finite TEST_ONLY controls. Expected labels are stated directly
--  from D26 and the separate v6 confinement gate, not computed by the model.
--  This driver is outside SPARK proof and cannot establish the complete domain.
procedure Test_Report_Facts is
   package E renames Worldline.Evaluation;
   package F renames Worldline.Evaluation_Report_Facts;
   package W renames Worldline.Evaluation_Report_Wire;
   use type W.Byte;
   use type E.Execution_State;
   use type E.Report_Integrity;
   use type F.Bundle_Observation;
   use type F.Confinement_Observation;

   All_Present : constant W.Raw_Record :=
     (Report_Based => 1,
      Execution => E.Execution_State'Pos (E.Completed),
      Result => E.Outcome'Pos (E.Passed),
      Bundle => F.Bundle_Observation'Pos (F.Bundle_Verified),
      Facts => (others => 1),
      Confinement => F.Confinement_Observation'Pos (F.Confinement_Established));
   Raw : W.Raw_Record := All_Present;

   procedure Check
     (Input : W.Raw_Record;
      Expected, Confined_Expected : E.Report_Integrity)
   is
      Decoded : constant W.Decode_Result := W.Decode (Input);
   begin
      pragma Assert (Decoded.Valid);
      pragma Assert (W.Decode_Conforms (Input, Decoded));
      pragma Assert (W.Integrity_Wire (Input) = E.Report_Integrity'Pos (Expected));
      pragma Assert
        (W.Confined_Integrity_Wire (Input) =
           E.Report_Integrity'Pos (Confined_Expected));
   end Check;

   procedure Reject (Input : W.Raw_Record) is
      Decoded : constant W.Decode_Result := W.Decode (Input);
   begin
      pragma Assert (not W.Well_Formed (Input));
      pragma Assert (not Decoded.Valid);
      pragma Assert (W.Decode_Conforms (Input, Decoded));
      pragma Assert (W.Integrity_Wire (Input) = W.Invalid_Record);
      pragma Assert (W.Confined_Integrity_Wire (Input) = W.Invalid_Record);
   end Reject;
begin
   pragma Assert (Raw'Size = 152);
   pragma Assert (Raw'Alignment = 1);
   pragma Assert (Raw.Report_Based'Position = 0);
   pragma Assert (Raw.Execution'Position = 1);
   pragma Assert (Raw.Result'Position = 2);
   pragma Assert (Raw.Bundle'Position = 3);
   pragma Assert (Raw.Facts'Position = 4);
   pragma Assert (Raw.Confinement'Position = 18);
   pragma Assert (Raw.Report_Based'First_Bit = 0);
   pragma Assert (Raw.Execution'First_Bit = 0);
   pragma Assert (Raw.Result'First_Bit = 0);
   pragma Assert (Raw.Bundle'First_Bit = 0);
   pragma Assert (Raw.Facts'First_Bit = 0);
   pragma Assert (Raw.Confinement'First_Bit = 0);
   Ada.Text_IO.Put_Line ("PASS explicit report dependency layout");

   --  All declared classification values remain inputs, including Unbound and
   --  Completed/No_Outcome. The report predicate does not reclassify outcome.
   for Execution in E.Execution_State loop
      for Result in E.Outcome loop
         for Bundle in F.Bundle_Observation loop
            for Confinement in F.Confinement_Observation loop
               Raw := All_Present;
               Raw.Execution := E.Execution_State'Pos (Execution);
               Raw.Result := E.Outcome'Pos (Result);
               Raw.Bundle := F.Bundle_Observation'Pos (Bundle);
               Raw.Confinement := F.Confinement_Observation'Pos (Confinement);
               if Execution = E.Completed and then Bundle = F.Bundle_Verified then
                  if Confinement = F.Confinement_Established then
                     Check (Raw, E.Verified_Report, E.Verified_Report);
                  else
                     Check (Raw, E.Verified_Report, E.Untrusted_Report);
                  end if;
               else
                  Check (Raw, E.Untrusted_Report, E.Untrusted_Report);
               end if;
               Raw.Report_Based := 0;
               Check (Raw, E.Not_Applicable, E.Not_Applicable);
            end loop;
         end loop;
      end loop;
   end loop;
   Ada.Text_IO.Put_Line ("PASS classification and confinement domains with all facts");

   for I in W.Fact_Index loop
      Raw := All_Present;
      Raw.Facts (I) := 0;
      Check (Raw, E.Untrusted_Report, E.Untrusted_Report);
      Raw.Report_Based := 0;
      Check (Raw, E.Not_Applicable, E.Not_Applicable);
   end loop;
   Raw := All_Present;
   Raw.Facts := (others => 0);
   Check (Raw, E.Untrusted_Report, E.Untrusted_Report);
   Ada.Text_IO.Put_Line ("PASS each required fact and absent fact set");

   --  Ordinary declared raw-domain controls; all-byte malformed input remains
   --  a proof obligation, not a conclusion drawn from these finite examples.
   Raw := All_Present;
   Raw.Report_Based := W.Invalid_Record;
   Reject (Raw);
   Raw := All_Present;
   Raw.Execution := W.Invalid_Record;
   Reject (Raw);
   Raw := All_Present;
   Raw.Result := W.Invalid_Record;
   Reject (Raw);
   Raw := All_Present;
   Raw.Bundle := W.Invalid_Record;
   Reject (Raw);
   Raw := All_Present;
   Raw.Confinement := W.Invalid_Record;
   Reject (Raw);
   for I in W.Fact_Index loop
      Raw := All_Present;
      Raw.Facts (I) := W.Invalid_Record;
      Reject (Raw);
      Raw.Report_Based := 0;
      Reject (Raw);
   end loop;
   Ada.Text_IO.Put_Line ("PASS malformed raw fields refuse without a typed payload");
   Ada.Text_IO.Put_Line ("PASS all named ReportFacts controls");
end Test_Report_Facts;
