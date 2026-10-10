with Interfaces;
with System;
with Worldline.Evaluation_V2;
with Worldline.Evaluation_Report_Wire;

--  Total D30 raw-to-typed dependency. No producer/custody guarantee follows
--  from byte validity, and no classification is accepted from the caller.
package Worldline.Evaluation_Wire with SPARK_Mode is
   package E renames Worldline.Evaluation_V2;
   package R renames Worldline.Evaluation_Report_Wire;
   subtype Byte is Interfaces.Unsigned_8;
   use type Byte;
   use type E.Execution_State;
   use type E.Outcome;
   use type E.Origin;
   use type E.Classification;
   use type E.Confinement_Observation;
   Invalid_Record : constant Byte := 255;
   type Observation_Field is
     (Source_Field, Status_Field, Channel_Field, Stage_Field, Exit_Present_Field, Exit_Integer_Field, Supervisor_Field, Supervisor_Stopped_Field, Bundle_Present_Field, Bundle_Is_Mapping_Field, Bundle_Stable_Field, Bundle_Changed_Field, Unsatisfied_Imports_Field, Isolation_Field);
   type Raw_Observations is array (Observation_Field) of Byte
     with Convention => C, Component_Size => 8, Size => 112,
          Object_Size => 112, Alignment => 1;
   type Presence_Field is
     (Record_Identified_Field, Verdict_Recorded_Field, Binding_Established_Field, Declaration_Matches_Field, Bundle_Identified_Field);
   type Raw_Presence is array (Presence_Field) of Byte
     with Convention => C, Component_Size => 8, Size => 40,
          Object_Size => 40, Alignment => 1;
   type Raw_Record is record
      Observations : Raw_Observations;
      Report_Based : Byte;
      Report_Facts : R.Raw_Facts;
      Presence : Raw_Presence;
   end record with Convention => C, Size => 272, Object_Size => 272, Alignment => 1;
   for Raw_Record use record
      Observations at 0 range 0 .. 112 - 1;
      Report_Based at 14 range 0 .. 8 - 1;
      Report_Facts at 15 range 0 .. 112 - 1;
      Presence at 29 range 0 .. 40 - 1;
   end record;
   pragma Compile_Time_Error
     (System.Storage_Unit /= 8 or else Byte'Size /= 8
      or else Raw_Observations'Size /= 112 or else Raw_Presence'Size /= 40
      or else Raw_Record'Size /= 272 or else Raw_Record'Object_Size /= 272
      or else Raw_Record'Alignment /= 1, "D30 record requires exact octet layout");
   Zero_Record : constant Raw_Record :=
     ((others => 0), 0, (others => 0), (others => 0));

   function Well_Formed (Raw : Raw_Record) return Boolean is
     (Raw.Observations (Source_Field) <= E.Origin'Pos (E.Origin'Last)
      and then Raw.Observations (Status_Field) <= E.Raw_Status'Pos (E.Raw_Status'Last)
      and then Raw.Observations (Channel_Field) <= E.Channel_State'Pos (E.Channel_State'Last)
      and then Raw.Observations (Stage_Field) <= E.Rejection_Stage'Pos (E.Rejection_Stage'Last)
      and then Raw.Observations (Exit_Present_Field) <= 1
      and then Raw.Observations (Exit_Integer_Field) <= 1
      and then Raw.Observations (Supervisor_Field) <= E.Supervision_State'Pos (E.Supervision_State'Last)
      and then Raw.Observations (Supervisor_Stopped_Field) <= 1
      and then Raw.Observations (Bundle_Present_Field) <= 1
      and then Raw.Observations (Bundle_Is_Mapping_Field) <= 1
      and then Raw.Observations (Bundle_Stable_Field) <= 1
      and then Raw.Observations (Bundle_Changed_Field) <= 1
      and then Raw.Observations (Unsatisfied_Imports_Field) <= 1
      and then Raw.Observations (Isolation_Field) <= E.Examiner_Isolation'Pos (E.Examiner_Isolation'Last)
      and then Raw.Report_Based <= 1
      and then (for all I in R.Fact_Index => Raw.Report_Facts (I) <= 1)
      and then (for all I in Presence_Field => Raw.Presence (I) <= 1)
      and then Raw.Observations (Exit_Integer_Field) <= Raw.Observations (Exit_Present_Field)
      and then Raw.Observations (Bundle_Stable_Field) <= Raw.Observations (Bundle_Present_Field)
      and then Raw.Observations (Bundle_Changed_Field) <= Raw.Observations (Bundle_Present_Field)
      and then Raw.Observations (Bundle_Stable_Field) <= Raw.Observations (Bundle_Is_Mapping_Field)
      and then Raw.Observations (Bundle_Changed_Field) <= Raw.Observations (Bundle_Is_Mapping_Field)) with Global => null;

   type Decoded_Record is record
      Facts : E.Observations;
      Report_Based : Boolean;
      Report_Facts : E.Report_Facts;
      Presence : E.Evidence_Presence;
   end record;
   type Decode_Result (Valid : Boolean := False) is record
      case Valid is
         when False => null;
         when True => Value : Decoded_Record;
      end case;
   end record;
   function Decode_Conforms (Raw : Raw_Record; Decoded : Decode_Result)
      return Boolean is
     (Decoded.Valid = Well_Formed (Raw)
      and then (if Decoded.Valid then
         E.Origin'Pos (Decoded.Value.Facts.Source) = Integer (Raw.Observations (Source_Field))
         and then E.Raw_Status'Pos (Decoded.Value.Facts.Status) = Integer (Raw.Observations (Status_Field))
         and then E.Channel_State'Pos (Decoded.Value.Facts.Channel) = Integer (Raw.Observations (Channel_Field))
         and then E.Rejection_Stage'Pos (Decoded.Value.Facts.Stage) = Integer (Raw.Observations (Stage_Field))
         and then Decoded.Value.Facts.Exit_Present = (Raw.Observations (Exit_Present_Field) = 1)
         and then Decoded.Value.Facts.Exit_Integer = (Raw.Observations (Exit_Integer_Field) = 1)
         and then E.Supervision_State'Pos (Decoded.Value.Facts.Supervisor) = Integer (Raw.Observations (Supervisor_Field))
         and then Decoded.Value.Facts.Supervisor_Stopped = (Raw.Observations (Supervisor_Stopped_Field) = 1)
         and then Decoded.Value.Facts.Bundle_Present = (Raw.Observations (Bundle_Present_Field) = 1)
         and then Decoded.Value.Facts.Bundle_Is_Mapping = (Raw.Observations (Bundle_Is_Mapping_Field) = 1)
         and then Decoded.Value.Facts.Bundle_Stable = (Raw.Observations (Bundle_Stable_Field) = 1)
         and then Decoded.Value.Facts.Bundle_Changed = (Raw.Observations (Bundle_Changed_Field) = 1)
         and then Decoded.Value.Facts.Unsatisfied_Imports = (Raw.Observations (Unsatisfied_Imports_Field) = 1)
         and then E.Examiner_Isolation'Pos (Decoded.Value.Facts.Isolation) = Integer (Raw.Observations (Isolation_Field))
         and then Decoded.Value.Report_Based = (Raw.Report_Based = 1)
         and then Decoded.Value.Report_Facts.Private_Profile = (Raw.Report_Facts (R.Private_Profile_Fact) = 1)
         and then Decoded.Value.Report_Facts.Exit_Integer_Nonnegative = (Raw.Report_Facts (R.Exit_Integer_Nonnegative_Fact) = 1)
         and then Decoded.Value.Report_Facts.Records_Present = (Raw.Report_Facts (R.Records_Present_Fact) = 1)
         and then Decoded.Value.Report_Facts.Channel_Daemon_Accepted = (Raw.Report_Facts (R.Channel_Daemon_Accepted_Fact) = 1)
         and then Decoded.Value.Report_Facts.Supervision_Clean = (Raw.Report_Facts (R.Supervision_Clean_Fact) = 1)
         and then Decoded.Value.Report_Facts.Boundary_Consistent = (Raw.Report_Facts (R.Boundary_Consistent_Fact) = 1)
         and then Decoded.Value.Report_Facts.Report_Mount_Exclusive = (Raw.Report_Facts (R.Report_Mount_Exclusive_Fact) = 1)
         and then Decoded.Value.Report_Facts.Collected_Privately = (Raw.Report_Facts (R.Collected_Privately_Fact) = 1)
         and then Decoded.Value.Report_Facts.Identities_Match = (Raw.Report_Facts (R.Identities_Match_Fact) = 1)
         and then Decoded.Value.Report_Facts.Digest_Matches = (Raw.Report_Facts (R.Digest_Matches_Fact) = 1)
         and then Decoded.Value.Report_Facts.Examiner_Observed = (Raw.Report_Facts (R.Examiner_Observed_Fact) = 1)
         and then Decoded.Value.Report_Facts.Workers_Separated = (Raw.Report_Facts (R.Workers_Separated_Fact) = 1)
         and then Decoded.Value.Report_Facts.Status_Rederived = (Raw.Report_Facts (R.Status_Rederived_Fact) = 1)
         and then Decoded.Value.Report_Facts.Examiner_Audit_Clean = (Raw.Report_Facts (R.Examiner_Audit_Clean_Fact) = 1)
         and then Decoded.Value.Presence.Record_Identified = (Raw.Presence (Record_Identified_Field) = 1)
         and then Decoded.Value.Presence.Verdict_Recorded = (Raw.Presence (Verdict_Recorded_Field) = 1)
         and then Decoded.Value.Presence.Binding_Established = (Raw.Presence (Binding_Established_Field) = 1)
         and then Decoded.Value.Presence.Declaration_Matches = (Raw.Presence (Declaration_Matches_Field) = 1)
         and then Decoded.Value.Presence.Bundle_Identified = (Raw.Presence (Bundle_Identified_Field) = 1))) with Global => null;
   function Decode (Raw : Raw_Record) return Decode_Result
     with Global => null, Post => Decode_Conforms (Raw, Decode'Result);

   type Wire_Classification is record
      Status, Execution, Result, Bundle : Byte;
   end record with Convention => C, Size => 32, Object_Size => 32, Alignment => 1;
   for Wire_Classification use record
      Status at 0 range 0 .. 8 - 1;
      Execution at 1 range 0 .. 8 - 1;
      Result at 2 range 0 .. 8 - 1;
      Bundle at 3 range 0 .. 8 - 1;
   end record;
   pragma Compile_Time_Error
     (Wire_Classification'Size /= 32 or else Wire_Classification'Object_Size /= 32,
      "classification output layout differs");
   Invalid_Classification : constant Wire_Classification := (others => Invalid_Record);
   function Classify_Wire (Raw : Raw_Record) return Wire_Classification
     with Global => null,
       Post => (if not Well_Formed (Raw) then Classify_Wire'Result = Invalid_Classification
        else Decode (Raw).Valid and then Classify_Wire'Result =
          (Status => 0,
           Execution => E.Execution_State'Pos (E.Expected_Classification (Decode (Raw).Value.Facts).Execution),
           Result => E.Outcome'Pos (E.Expected_Classification (Decode (Raw).Value.Facts).Result),
           Bundle => E.Bundle_Integrity'Pos (E.Expected_Classification (Decode (Raw).Value.Facts).Bundle)));

   function Admitted (Raw : Raw_Record) return Boolean is
     (Well_Formed (Raw) and then Decode (Raw).Valid and then
       E.Admissible
         (E.Expected_Classification (Decode (Raw).Value.Facts),
          E.Expected_Report (Decode (Raw).Value.Report_Based,
            E.Expected_Classification (Decode (Raw).Value.Facts), Decode (Raw).Value.Report_Facts),
          Decode (Raw).Value.Presence)) with Global => null;
   function Admit_Wire (Raw : Raw_Record) return Byte
     with Global => null,
       Post => Admit_Wire'Result =
         (if not Well_Formed (Raw) then Invalid_Record
          elsif Admitted (Raw) then 1 else 0);
   --  v6's stronger confinement gate is explicit and additional to literal
   --  D26/D30. It never treats the audit observation as confinement.
   function Confined_Admit_Wire (Raw : Raw_Record; Confinement : Byte) return Byte
     with Global => null,
       Post => Confined_Admit_Wire'Result =
         (if not Well_Formed (Raw) or else Confinement > E.Confinement_Observation'Pos
             (E.Confinement_Observation'Last) then Invalid_Record
          elsif Admitted (Raw)
             and then ((not Decode (Raw).Value.Report_Based
                 and then Decode (Raw).Value.Facts.Source /= E.External)
               or else Confinement = E.Confinement_Observation'Pos (E.F.Confinement_Established))
          then 1 else 0);

   type Raw_Array is array (Positive range <>) of Raw_Record;
   function Completion_Admitted (Raw : Raw_Record) return Boolean is
     (Admitted (Raw) and then Decode (Raw).Value.Facts.Source = E.Engine)
     with Global => null;
   function Roster_Well_Formed
     (Rows : Raw_Array; Empty_Declared : Byte; Completion : Raw_Record) return Boolean is
     (Empty_Declared <= 1 and then Well_Formed (Completion)
      and then (for all I in Rows'Range => Well_Formed (Rows (I)))) with Global => null;
   function Roster_Reference
     (Rows : Raw_Array; Empty_Declared : Byte; Completion : Raw_Record) return Boolean is
     (Roster_Well_Formed (Rows, Empty_Declared, Completion)
      and then Completion_Admitted (Completion)
      and then (if Rows'Length = 0 then Empty_Declared = 1
                else (for all I in Rows'Range => Admitted (Rows (I))))) with Global => null;
   function Roster_Wire
     (Rows : Raw_Array; Empty_Declared : Byte; Completion : Raw_Record) return Byte
     with Global => null,
       Post => Roster_Wire'Result =
         (if not Roster_Well_Formed (Rows, Empty_Declared, Completion) then Invalid_Record
          elsif Roster_Reference (Rows, Empty_Declared, Completion) then 1 else 0);

   --  D30 fixed transfer format, separate from unconstrained semantic arrays.
   subtype Slot is Positive range 1 .. 4096;
   type Raw_Slots is array (Slot) of Raw_Record
     with Convention => C, Component_Size => 272, Size => 1114112,
          Object_Size => 1114112, Alignment => 1;
   type Raw_Roster is record
      Count_Low, Count_High, Empty_Declared : Byte;
      Completion : Raw_Record;
      Rows : Raw_Slots;
   end record with Convention => C, Size => 1114408,
     Object_Size => 1114408, Alignment => 1;
   for Raw_Roster use record
      Count_Low at 0 range 0 .. 8 - 1;
      Count_High at 1 range 0 .. 8 - 1;
      Empty_Declared at 2 range 0 .. 8 - 1;
      Completion at 3 range 0 .. 272 - 1;
      Rows at 37 range 0 .. 1114112 - 1;
   end record;
   pragma Compile_Time_Error
     (Raw_Roster'Size /= 1114408 or else Raw_Roster'Object_Size /= 1114408
      or else Raw_Roster'Alignment /= 1, "D30 roster layout differs");
   function Count_Of (Raw : Raw_Roster) return Natural is
     (Natural (Raw.Count_Low) + 256 * Natural (Raw.Count_High))
     with Global => null, Post => Count_Of'Result <= 65535;
   function Well_Formed (Raw : Raw_Roster) return Boolean is
     (Count_Of (Raw) <= Slot'Last and then Raw.Empty_Declared <= 1
      and then Well_Formed (Raw.Completion)
      and then (for all I in Slot =>
        (if I <= Count_Of (Raw) then Well_Formed (Raw.Rows (I))
         else Raw.Rows (I) = Zero_Record))) with Global => null;
   function Roster_Wire (Raw : Raw_Roster) return Byte
     with Global => null,
       Post => Roster_Wire'Result =
         (if not Well_Formed (Raw) then Invalid_Record
          elsif Completion_Admitted (Raw.Completion)
            and then (if Count_Of (Raw) = 0 then Raw.Empty_Declared = 1
              else (for all I in Slot =>
                (if I <= Count_Of (Raw) then Admitted (Raw.Rows (I)))))
          then 1 else 0);
end Worldline.Evaluation_Wire;
