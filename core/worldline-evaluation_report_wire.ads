with Interfaces;
with System;
with Worldline.Evaluation;
with Worldline.Evaluation_Report_Facts;

--  Isolated report-fact representation. This is NOT the complete D30 raw
--  evaluation/roster ABI. A future Evaluation_Wire must derive classification
--  itself and bind all observations to its measured run before using this
--  dependency; Python-supplied classification is not a migrated authority path.
package Worldline.Evaluation_Report_Wire with SPARK_Mode is
   package E renames Worldline.Evaluation;
   package F renames Worldline.Evaluation_Report_Facts;
   subtype Byte is Interfaces.Unsigned_8;
   use type Byte;
   use type E.Execution_State;
   use type E.Outcome;
   use type F.Bundle_Observation;
   use type F.Confinement_Observation;

   type Fact_Index is
     (Private_Profile_Fact, Exit_Integer_Nonnegative_Fact,
      Records_Present_Fact, Channel_Daemon_Accepted_Fact,
      Supervision_Clean_Fact, Boundary_Consistent_Fact,
      Report_Mount_Exclusive_Fact, Collected_Privately_Fact,
      Identities_Match_Fact, Digest_Matches_Fact, Examiner_Observed_Fact,
      Workers_Separated_Fact, Status_Rederived_Fact,
      Examiner_Audit_Clean_Fact);

   type Raw_Facts is array (Fact_Index) of Byte
     with Convention => C, Component_Size => 8, Size => 112,
          Object_Size => 112, Alignment => 1;

   type Raw_Record is record
      Report_Based : Byte;
      Execution    : Byte;
      Result       : Byte;
      Bundle       : Byte;
      Facts        : Raw_Facts;
      Confinement  : Byte;
   end record
     with Convention => C, Size => 152, Object_Size => 152, Alignment => 1;

   for Raw_Record use record
      Report_Based at 0 range 0 .. Byte'Size - 1;
      Execution    at 1 range 0 .. Byte'Size - 1;
      Result       at 2 range 0 .. Byte'Size - 1;
      Bundle       at 3 range 0 .. Byte'Size - 1;
      --  Array Size is not a static integer expression in this clause.
      --  Keep the declared 112-bit extent and the unchanged compile-time size
      --  checks; this literal static expression expresses the same layout.
      Facts        at 4 range 0 .. 112 - 1;
      Confinement  at 18 range 0 .. Byte'Size - 1;
   end record;

   pragma Compile_Time_Error
     (System.Storage_Unit /= 8 or else Byte'Size /= 8,
      "report wire requires octet storage");
   pragma Compile_Time_Error
     (Raw_Facts'Size /= 112 or else Raw_Facts'Object_Size /= 112,
      "report fact array must occupy exactly fourteen octets");
   pragma Compile_Time_Error
     (Raw_Record'Size /= 152 or else Raw_Record'Object_Size /= 152
      or else Raw_Record'Alignment /= 1,
      "report dependency wire must occupy exactly nineteen octets");

   Invalid_Record : constant Byte := 255;

   function Well_Formed (Raw : Raw_Record) return Boolean is
     (Raw.Report_Based <= 1
      and then Raw.Execution <= E.Execution_State'Pos (E.Execution_State'Last)
      and then Raw.Result <= E.Outcome'Pos (E.Outcome'Last)
      and then Raw.Bundle <= F.Bundle_Observation'Pos (F.Bundle_Observation'Last)
      and then Raw.Confinement <=
        F.Confinement_Observation'Pos (F.Confinement_Observation'Last)
      and then (for all I in Fact_Index => Raw.Facts (I) <= 1))
     with Global => null;

   type Decoded_Record is record
      Report_Based : Boolean;
      Value        : F.Classified_Value;
      Facts        : F.Report_Facts;
      Confinement  : F.Confinement_Observation;
   end record;

   type Decode_Result (Valid : Boolean := False) is record
      case Valid is
         when False => null;
         when True  => Value : Decoded_Record;
      end case;
   end record;

   --  Total correspondence over every raw byte and every variant. No decoder
   --  Pre excludes malformed input, and the absent variant has no payload.
   function Decode_Conforms
     (Raw : Raw_Record; Decoded : Decode_Result) return Boolean is
     (Decoded.Valid = Well_Formed (Raw)
      and then
        (if Decoded.Valid then
           Decoded.Value.Report_Based = (Raw.Report_Based = 1)
           and then E.Execution_State'Pos (Decoded.Value.Value.Execution) =
             Integer (Raw.Execution)
           and then E.Outcome'Pos (Decoded.Value.Value.Result) =
             Integer (Raw.Result)
           and then F.Bundle_Observation'Pos (Decoded.Value.Value.Bundle) =
             Integer (Raw.Bundle)
           and then F.Confinement_Observation'Pos (Decoded.Value.Confinement) =
             Integer (Raw.Confinement)
           and then Decoded.Value.Facts.Private_Profile =
             (Raw.Facts (Private_Profile_Fact) = 1)
           and then Decoded.Value.Facts.Exit_Integer_Nonnegative =
             (Raw.Facts (Exit_Integer_Nonnegative_Fact) = 1)
           and then Decoded.Value.Facts.Records_Present =
             (Raw.Facts (Records_Present_Fact) = 1)
           and then Decoded.Value.Facts.Channel_Daemon_Accepted =
             (Raw.Facts (Channel_Daemon_Accepted_Fact) = 1)
           and then Decoded.Value.Facts.Supervision_Clean =
             (Raw.Facts (Supervision_Clean_Fact) = 1)
           and then Decoded.Value.Facts.Boundary_Consistent =
             (Raw.Facts (Boundary_Consistent_Fact) = 1)
           and then Decoded.Value.Facts.Report_Mount_Exclusive =
             (Raw.Facts (Report_Mount_Exclusive_Fact) = 1)
           and then Decoded.Value.Facts.Collected_Privately =
             (Raw.Facts (Collected_Privately_Fact) = 1)
           and then Decoded.Value.Facts.Identities_Match =
             (Raw.Facts (Identities_Match_Fact) = 1)
           and then Decoded.Value.Facts.Digest_Matches =
             (Raw.Facts (Digest_Matches_Fact) = 1)
           and then Decoded.Value.Facts.Examiner_Observed =
             (Raw.Facts (Examiner_Observed_Fact) = 1)
           and then Decoded.Value.Facts.Workers_Separated =
             (Raw.Facts (Workers_Separated_Fact) = 1)
           and then Decoded.Value.Facts.Status_Rederived =
             (Raw.Facts (Status_Rederived_Fact) = 1)
           and then Decoded.Value.Facts.Examiner_Audit_Clean =
             (Raw.Facts (Examiner_Audit_Clean_Fact) = 1)))
     with Global => null;

   function Decode (Raw : Raw_Record) return Decode_Result
     with Global => null,
          Post => Decode_Conforms (Raw, Decode'Result);

   function Integrity_Wire (Raw : Raw_Record) return Byte
     with Global => null,
          Post =>
            (if not Well_Formed (Raw) then
               Integrity_Wire'Result = Invalid_Record
             else Decode (Raw).Valid
               and then Integrity_Wire'Result =
                 E.Report_Integrity'Pos
                   (F.Expected_Integrity
                      (Decode (Raw).Value.Report_Based,
                       Decode (Raw).Value.Value,
                       Decode (Raw).Value.Facts)));

   function Confined_Integrity_Wire (Raw : Raw_Record) return Byte
     with Global => null,
          Post =>
            (if not Well_Formed (Raw) then
               Confined_Integrity_Wire'Result = Invalid_Record
             else Decode (Raw).Valid
               and then Confined_Integrity_Wire'Result =
                 E.Report_Integrity'Pos
                   (F.Expected_Confined_Integrity
                      (Decode (Raw).Value.Report_Based,
                       Decode (Raw).Value.Value,
                       Decode (Raw).Value.Facts,
                       Decode (Raw).Value.Confinement)));
end Worldline.Evaluation_Report_Wire;
