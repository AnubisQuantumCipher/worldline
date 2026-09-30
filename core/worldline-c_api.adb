with Ada.Streams;
with Ada.Streams.Stream_IO;
with Attest;
with Attest.SHA256;
with System.Address_To_Access_Conversions;
with System.Storage_Elements;
with Worldline.Causal_Graph;
with Worldline.Evaluation;
with Worldline.Receipts;
with Worldline.Transitions;
with Worldline.World;

package body Worldline.C_API with SPARK_Mode => Off is

   use type Interfaces.C.size_t;
   use type Interfaces.Unsigned_8;
   use type Ada.Streams.Stream_Element_Offset;
   use type Interfaces.Unsigned_64;
   use type System.Address;

   package Byte_Pointers is new System.Address_To_Access_Conversions
     (Interfaces.Unsigned_8);

   Error_OK               : constant Interfaces.C.int := 0;
   Error_Invalid_Argument : constant Interfaces.C.int := 1;
   Error_IO               : constant Interfaces.C.int := 2;
   Error_Too_Large        : constant Interfaces.C.int := 3;
   Error_Internal         : constant Interfaces.C.int := 4;

   Chunk_Length : constant Positive :=
     Attest.SHA256.Block_Bytes * Attest.SHA256.Block_Bytes;

   function Get_Byte
     (Base   : System.Address;
      Offset : System.Storage_Elements.Storage_Offset)
      return Interfaces.Unsigned_8
   is
      use System.Storage_Elements;
   begin
      return Byte_Pointers.To_Pointer (Base + Offset).all;
   end Get_Byte;

   procedure Put_Byte
     (Base   : System.Address;
      Offset : System.Storage_Elements.Storage_Offset;
      Value  : Interfaces.Unsigned_8)
   is
      use System.Storage_Elements;
   begin
      Byte_Pointers.To_Pointer (Base + Offset).all := Value;
   end Put_Byte;

   function Read_Hash (Base : System.Address) return Hash is
      Result : Hash;
   begin
      for I in Result'Range loop
         Result (I) :=
           Get_Byte
             (Base,
              System.Storage_Elements.Storage_Offset (I - Result'First));
      end loop;
      return Result;
   end Read_Hash;

   procedure Write_Hash (Base : System.Address; Value : Hash) is
   begin
      for I in Value'Range loop
         Put_Byte
           (Base,
            System.Storage_Elements.Storage_Offset (I - Value'First),
            Value (I));
      end loop;
   end Write_Hash;

   function Hash_File
     (Path       : System.Address;
      Path_Len   : Interfaces.C.size_t;
      Out_Digest : System.Address) return Interfaces.C.int
   is
      package SIO renames Ada.Streams.Stream_IO;
      File       : SIO.File_Type;
      Raw        : Ada.Streams.Stream_Element_Array
        (1 .. Ada.Streams.Stream_Element_Offset (Chunk_Length));
      Last       : Ada.Streams.Stream_Element_Offset;
      Buffer     : Attest.Byte_Array (0 .. Chunk_Length - 1);
      C          : Attest.SHA256.Context := Attest.SHA256.Initial;
   begin
      if Path = System.Null_Address
        or else Out_Digest = System.Null_Address
        or else Path_Len = 0
        or else Path_Len > Interfaces.C.size_t (Natural'Last)
      then
         return Error_Invalid_Argument;
      end if;

      declare
         Native_Path : String (1 .. Natural (Path_Len));
      begin
         for I in Native_Path'Range loop
            declare
               B : constant Interfaces.Unsigned_8 :=
                 Get_Byte
                   (Path,
                    System.Storage_Elements.Storage_Offset
                      (I - Native_Path'First));
            begin
               if B = 0 then
                  return Error_Invalid_Argument;
               end if;
               Native_Path (I) := Character'Val (Integer (B));
            end;
         end loop;

         SIO.Open (File, SIO.In_File, Native_Path);
      end;

      while not SIO.End_Of_File (File) loop
         SIO.Read (File, Raw, Last);
         declare
            Count : constant Natural :=
              Natural (Last - Raw'First + 1);
         begin
            if Attest.SHA256.Absorbed (C) >
              Attest.SHA256.Max_Message_Bytes -
                Interfaces.Unsigned_64 (Count)
            then
               SIO.Close (File);
               return Error_Too_Large;
            end if;

            for I in 0 .. Count - 1 loop
               Buffer (I) :=
                 Attest.Byte
                   (Raw (Raw'First + Ada.Streams.Stream_Element_Offset (I)));
            end loop;
            Attest.SHA256.Update (C, Buffer (0 .. Count - 1));
         end;
      end loop;

      SIO.Close (File);
      Write_Hash (Out_Digest, Attest.SHA256.Final (C));
      return Error_OK;
   exception
      when others =>
         if SIO.Is_Open (File) then
            SIO.Close (File);
         end if;
         return Error_IO;
   end Hash_File;

   function Hash_Bytes
     (Data       : System.Address;
      Data_Len   : Interfaces.C.size_t;
      Out_Digest : System.Address) return Interfaces.C.int
   is
      Buffer : Attest.Byte_Array (0 .. Chunk_Length - 1);
      C      : Attest.SHA256.Context := Attest.SHA256.Initial;
      Offset : Interfaces.C.size_t := 0;
   begin
      if Out_Digest = System.Null_Address
        or else (Data_Len > 0 and then Data = System.Null_Address)
      then
         return Error_Invalid_Argument;
      elsif Data_Len >
        Interfaces.C.size_t (Attest.SHA256.Max_Message_Bytes)
      then
         return Error_Too_Large;
      end if;

      while Offset < Data_Len loop
         declare
            Remaining : constant Interfaces.C.size_t := Data_Len - Offset;
            Count     : constant Natural :=
              (if Remaining > Interfaces.C.size_t (Buffer'Length)
               then Buffer'Length
               else Natural (Remaining));
         begin
            for I in 0 .. Count - 1 loop
               Buffer (I) :=
                 Get_Byte
                   (Data,
                    System.Storage_Elements.Storage_Offset
                      (Offset + Interfaces.C.size_t (I)));
            end loop;
            Attest.SHA256.Update (C, Buffer (0 .. Count - 1));
            Offset := Offset + Interfaces.C.size_t (Count);
         end;
      end loop;

      Write_Hash (Out_Digest, Attest.SHA256.Final (C));
      return Error_OK;
   exception
      when others =>
         return Error_Internal;
   end Hash_Bytes;

   function World_ID
     (Parent_ID        : System.Address;
      Filesystem_Root  : System.Address;
      Config_Root      : System.Address;
      Repository_Root  : System.Address;
      Environment_Root : System.Address;
      Evidence_Root    : System.Address;
      Out_Digest       : System.Address) return Interfaces.C.int
   is
   begin
      if Parent_ID = System.Null_Address
        or else Filesystem_Root = System.Null_Address
        or else Config_Root = System.Null_Address
        or else Repository_Root = System.Null_Address
        or else Environment_Root = System.Null_Address
        or else Evidence_Root = System.Null_Address
        or else Out_Digest = System.Null_Address
      then
         return Error_Invalid_Argument;
      end if;

      Write_Hash
        (Out_Digest,
         Worldline.World.Identity
           (Read_Hash (Parent_ID),
            Read_Hash (Filesystem_Root),
            Read_Hash (Config_Root),
            Read_Hash (Repository_Root),
            Read_Hash (Environment_Root),
            Read_Hash (Evidence_Root)));
      return Error_OK;
   exception
      when others =>
         return Error_Internal;
   end World_ID;

   function Causal_Link
     (Previous   : System.Address;
      Event_Root : System.Address;
      Out_Digest : System.Address) return Interfaces.C.int
   is
   begin
      if Previous = System.Null_Address
        or else Event_Root = System.Null_Address
        or else Out_Digest = System.Null_Address
      then
         return Error_Invalid_Argument;
      end if;
      Write_Hash
        (Out_Digest,
         Worldline.Causal_Graph.Link
           (Read_Hash (Previous), Read_Hash (Event_Root)));
      return Error_OK;
   exception
      when others =>
         return Error_Internal;
   end Causal_Link;

   function Receipt_Link
     (Previous     : System.Address;
      Receipt_Root : System.Address;
      Out_Digest   : System.Address) return Interfaces.C.int
   is
   begin
      if Previous = System.Null_Address
        or else Receipt_Root = System.Null_Address
        or else Out_Digest = System.Null_Address
      then
         return Error_Invalid_Argument;
      end if;
      Write_Hash
        (Out_Digest,
         Worldline.Receipts.Link
           (Read_Hash (Previous), Read_Hash (Receipt_Root)));
      return Error_OK;
   exception
      when others =>
         return Error_Internal;
   end Receipt_Link;

   function Transition_Allowed
     (From_State : Interfaces.Unsigned_8;
      To_State   : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
   is
      Last : constant Interfaces.Unsigned_8 :=
        Interfaces.Unsigned_8
          (Transitions.World_State'Pos (Transitions.World_State'Last));
   begin
      if From_State > Last or else To_State > Last then
         return 0;
      elsif Transitions.Allowed
        (Transitions.World_State'Val (Integer (From_State)),
         Transitions.World_State'Val (Integer (To_State)))
      then
         return 1;
      else
         return 0;
      end if;
   end Transition_Allowed;

   function Transaction_Transition_Allowed
     (From_State : Interfaces.Unsigned_8;
      To_State   : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
   is
      Last : constant Interfaces.Unsigned_8 :=
        Interfaces.Unsigned_8
          (Transitions.Transaction_State'Pos
             (Transitions.Transaction_State'Last));
   begin
      if From_State > Last or else To_State > Last then
         return 0;
      elsif Transitions.Transaction_Allowed
        (Transitions.Transaction_State'Val (Integer (From_State)),
         Transitions.Transaction_State'Val (Integer (To_State)))
      then
         return 1;
      else
         return 0;
      end if;
   end Transaction_Transition_Allowed;

   function Collapse_Decide
     (Request : C_Collapse_Request_Access) return Interfaces.Unsigned_8
   is
   begin
      if Request = null then
         return Collapse_Wire.Invalid_Request;
      end if;
      return Collapse_Wire.Decide_Wire (Request.all);
   exception
      when others =>
         return Collapse_Wire.Invalid_Request;
   end Collapse_Decide;

   function Evaluation_Classify
     (Facts : C_Evaluation_Observations_Access;
      Result : C_Evaluation_Classification_Access)
      return Interfaces.Unsigned_8
   is
   begin
      if Facts = null or else Result = null
        or else Facts.Source > Evaluation.Origin'Pos (Evaluation.Origin'Last)
        or else Facts.Status > Evaluation.Raw_Status'Pos (Evaluation.Raw_Status'Last)
        or else Facts.Channel > Evaluation.Channel_State'Pos (Evaluation.Channel_State'Last)
        or else Facts.Stage > Evaluation.Rejection_Stage'Pos (Evaluation.Rejection_Stage'Last)
        or else Facts.Supervisor > Evaluation.Supervision_State'Pos (Evaluation.Supervision_State'Last)
        or else Facts.Exit_Present > 1
        or else Facts.Exit_Integer > 1
        or else Facts.Supervisor_Stopped > 1
        or else Facts.Bundle_Present > 1
        or else Facts.Bundle_Is_Mapping > 1
        or else Facts.Bundle_Stable > 1
        or else Facts.Bundle_Changed > 1
        or else Facts.Unsatisfied_Imports > 1
        or else Facts.Exit_Integer > Facts.Exit_Present
        or else Facts.Bundle_Stable > Facts.Bundle_Present
        or else Facts.Bundle_Changed > Facts.Bundle_Present
        or else Facts.Bundle_Stable > Facts.Bundle_Is_Mapping
        or else Facts.Bundle_Changed > Facts.Bundle_Is_Mapping
      then
         return 255;
      end if;

      declare
         Value : constant Evaluation.Classification := Evaluation.Classify
           ((Source => Evaluation.Origin'Val (Integer (Facts.Source)),
             Status => Evaluation.Raw_Status'Val (Integer (Facts.Status)),
             Channel => Evaluation.Channel_State'Val (Integer (Facts.Channel)),
             Stage => Evaluation.Rejection_Stage'Val (Integer (Facts.Stage)),
             Exit_Present => Facts.Exit_Present = 1,
             Exit_Integer => Facts.Exit_Integer = 1,
             Supervisor => Evaluation.Supervision_State'Val
               (Integer (Facts.Supervisor)),
             Supervisor_Stopped => Facts.Supervisor_Stopped = 1,
             Bundle_Present => Facts.Bundle_Present = 1,
             Bundle_Is_Mapping => Facts.Bundle_Is_Mapping = 1,
             Bundle_Stable => Facts.Bundle_Stable = 1,
             Bundle_Changed => Facts.Bundle_Changed = 1,
             Unsatisfied_Imports => Facts.Unsatisfied_Imports = 1));
      begin
         Result.Execution := Interfaces.Unsigned_8
           (Evaluation.Execution_State'Pos (Value.Execution));
         Result.Outcome := Interfaces.Unsigned_8
           (Evaluation.Outcome'Pos (Value.Result));
         Result.Bundle := Interfaces.Unsigned_8
           (Evaluation.Bundle_Integrity'Pos (Value.Bundle));
         return 0;
      end;
   exception
      when others =>
         return 255;
   end Evaluation_Classify;

   function Evaluation_Admissible
     (Value    : C_Evaluation_Classification_Read_Access;
      Report   : Interfaces.Unsigned_8;
      Presence : C_Evidence_Presence_Access)
      return Interfaces.Unsigned_8
   is
      Completed_Code : constant Interfaces.Unsigned_8 :=
        Evaluation.Execution_State'Pos (Evaluation.Completed);
      No_Outcome_Code : constant Interfaces.Unsigned_8 :=
        Evaluation.Outcome'Pos (Evaluation.No_Outcome);
   begin
      if Value = null or else Presence = null
        or else Value.Execution >
          Evaluation.Execution_State'Pos (Evaluation.Execution_State'Last)
        or else Value.Outcome > Evaluation.Outcome'Pos (Evaluation.Outcome'Last)
        or else Value.Bundle >
          Evaluation.Bundle_Integrity'Pos (Evaluation.Bundle_Integrity'Last)
        or else Report >
          Evaluation.Report_Integrity'Pos (Evaluation.Report_Integrity'Last)
        or else (Value.Execution = Completed_Code) =
                (Value.Outcome = No_Outcome_Code)
        --  Classify never produces an in-flight state.
        or else Value.Execution in
          Evaluation.Execution_State'Pos (Evaluation.Prepared) ..
          Evaluation.Execution_State'Pos (Evaluation.Started)
        or else Presence.Record_Identified > 1
        or else Presence.Verdict_Recorded > 1
        or else Presence.Binding_Established > 1
        or else Presence.Declaration_Matches > 1
        or else Presence.Bundle_Identified > 1
      then
         return 255;
      end if;

      return
        (if Evaluation.Admissible
          ((Execution => Evaluation.Execution_State'Val
              (Integer (Value.Execution)),
            Result => Evaluation.Outcome'Val (Integer (Value.Outcome)),
            Bundle => Evaluation.Bundle_Integrity'Val
              (Integer (Value.Bundle))),
           Evaluation.Report_Integrity'Val (Integer (Report)),
           (Record_Identified   => Presence.Record_Identified = 1,
            Verdict_Recorded    => Presence.Verdict_Recorded = 1,
            Binding_Established => Presence.Binding_Established = 1,
            Declaration_Matches => Presence.Declaration_Matches = 1,
            Bundle_Identified   => Presence.Bundle_Identified = 1))
         then 1 else 0);
   exception
      when others =>
         return 255;
   end Evaluation_Admissible;

   Last_Execution_Code : constant Interfaces.Unsigned_8 :=
     Evaluation.Execution_State'Pos (Evaluation.Execution_State'Last);

   function Evaluation_Transition_Allowed
     (From_State : Interfaces.Unsigned_8;
      To_State   : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
   is
   begin
      if From_State > Last_Execution_Code or else To_State > Last_Execution_Code then
         return 255;
      end if;
      return
        (if Evaluation.Transition_Allowed
           (Evaluation.Execution_State'Val (Integer (From_State)),
            Evaluation.Execution_State'Val (Integer (To_State)))
         then 1 else 0);
   exception
      when others =>
         return 255;
   end Evaluation_Transition_Allowed;

   function Evaluation_Advance
     (State     : C_State_Access;
      Requested : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
   is
   begin
      if State = null
        or else State.all > Last_Execution_Code
        or else Requested > Last_Execution_Code
      then
         return 255;
      end if;
      declare
         Current : Evaluation.Execution_State :=
           Evaluation.Execution_State'Val (Integer (State.all));
      begin
         Evaluation.Advance
           (Current, Evaluation.Execution_State'Val (Integer (Requested)));
         State.all := Interfaces.Unsigned_8
           (Evaluation.Execution_State'Pos (Current));
      end;
      return 0;
   exception
      when others =>
         return 255;
   end Evaluation_Advance;

   function Evaluation_Roster_Complete
     (Admitted       : System.Address;
      Count          : Interfaces.C.size_t;
      Empty_Declared : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
   is
      use System.Storage_Elements;
   begin
      if Empty_Declared > 1
        or else Count > Interfaces.C.size_t (Evaluation.Roster_Index'Last)
        or else (Count > 0 and then Admitted = System.Null_Address)
      then
         return 255;
      end if;
      declare
         Length : constant Natural := Natural (Count);
         Values : Evaluation.Admissions (1 .. Length);
      begin
         for I in Values'Range loop
            declare
               Byte : constant Interfaces.Unsigned_8 :=
                 Get_Byte (Admitted, Storage_Offset (I - 1));
            begin
               if Byte > 1 then
                  return 255;
               end if;
               Values (I) := Byte = 1;
            end;
         end loop;
         return
           (if Evaluation.Roster_Complete (Values, Empty_Declared = 1)
            then 1 else 0);
      end;
   exception
      when others =>
         return 255;
   end Evaluation_Roster_Complete;

   function ABI_Generation return Interfaces.Unsigned_32 is
   begin
      return ABI_Version;
   end ABI_Generation;

   function Layout_Size
     (Selector : Interfaces.Unsigned_8) return Interfaces.C.size_t
   is
   begin
      case Selector is
         when 0 => return C_Collapse_Request'Size / 8;
         when 1 => return C_Evaluation_Observations'Size / 8;
         when 2 => return C_Evaluation_Classification'Size / 8;
         when 3 => return C_Evidence_Presence'Size / 8;
         when 4 => return Collapse_Wire.Raw_Optional_Hash'Size / 8;
         when 5 => return Collapse_Wire.Raw_Optional_Counter'Size / 8;
         when others => return 0;
      end case;
   end Layout_Size;

   function Layout_Offset
     (Selector : Interfaces.Unsigned_8;
      Name     : System.Address;
      Name_Len : Interfaces.C.size_t) return Interfaces.C.size_t
   is
      use System.Storage_Elements;
      Unknown : constant Interfaces.C.size_t := Interfaces.C.size_t'Last;
      Collapse_Probe    : Collapse_Wire.Raw_Request;
      Observation_Probe : C_Evaluation_Observations;
      Class_Probe       : C_Evaluation_Classification;
      Presence_Probe    : C_Evidence_Presence;
      Hash_Probe        : Collapse_Wire.Raw_Optional_Hash;
      Counter_Probe     : Collapse_Wire.Raw_Optional_Counter;
      --  Only the components' 'Position is read; no value is.
      pragma Warnings (Off, Collapse_Probe);
      pragma Warnings (Off, Observation_Probe);
      pragma Warnings (Off, Class_Probe);
      pragma Warnings (Off, Presence_Probe);
      pragma Warnings (Off, Hash_Probe);
      pragma Warnings (Off, Counter_Probe);
   begin
      if Name = System.Null_Address or else Name_Len = 0 or else Name_Len > 64 then
         return Unknown;
      end if;
      declare
         Text : String (1 .. Natural (Name_Len));
      begin
         for I in Text'Range loop
            Text (I) := Character'Val (Integer (Get_Byte (Name, Storage_Offset (I - 1))));
         end loop;
         case Selector is
            when 0 =>
               if Text = "candidate_state" then return Interfaces.C.size_t (Collapse_Probe.Candidate_State'Position);
               elsif Text = "phase" then return Interfaces.C.size_t (Collapse_Probe.Phase'Position);
               elsif Text = "evaluation_mode" then return Interfaces.C.size_t (Collapse_Probe.Evaluation_Mode'Position);
               elsif Text = "conflicts" then return Interfaces.C.size_t (Collapse_Probe.Conflicts'Position);
               elsif Text = "foreign_writes" then return Interfaces.C.size_t (Collapse_Probe.Foreign_Writes'Position);
               elsif Text = "roster_complete" then return Interfaces.C.size_t (Collapse_Probe.Roster_Complete'Position);
               elsif Text = "staged_roster_complete" then return Interfaces.C.size_t (Collapse_Probe.Staged_Roster_Complete'Position);
               elsif Text = "expected_parent" then return Interfaces.C.size_t (Collapse_Probe.Expected_Parent'Position);
               elsif Text = "candidate_parent" then return Interfaces.C.size_t (Collapse_Probe.Candidate_Parent'Position);
               elsif Text = "expected_subject" then return Interfaces.C.size_t (Collapse_Probe.Expected_Subject'Position);
               elsif Text = "evidence_subject" then return Interfaces.C.size_t (Collapse_Probe.Evidence_Subject'Position);
               elsif Text = "expected_base" then return Interfaces.C.size_t (Collapse_Probe.Expected_Base'Position);
               elsif Text = "candidate_base" then return Interfaces.C.size_t (Collapse_Probe.Candidate_Base'Position);
               elsif Text = "expected_delta" then return Interfaces.C.size_t (Collapse_Probe.Expected_Delta'Position);
               elsif Text = "candidate_delta" then return Interfaces.C.size_t (Collapse_Probe.Candidate_Delta'Position);
               elsif Text = "expected_root_set" then return Interfaces.C.size_t (Collapse_Probe.Expected_Root_Set'Position);
               elsif Text = "candidate_root_set" then return Interfaces.C.size_t (Collapse_Probe.Candidate_Root_Set'Position);
               elsif Text = "expected_staged_root" then return Interfaces.C.size_t (Collapse_Probe.Expected_Staged_Root'Position);
               elsif Text = "actual_staged_root" then return Interfaces.C.size_t (Collapse_Probe.Actual_Staged_Root'Position);
               elsif Text = "staged_content_root" then return Interfaces.C.size_t (Collapse_Probe.Staged_Content_Root'Position);
               elsif Text = "tested_root" then return Interfaces.C.size_t (Collapse_Probe.Tested_Root'Position);
               elsif Text = "current_requirement" then return Interfaces.C.size_t (Collapse_Probe.Current_Requirement'Position);
               elsif Text = "evaluated_requirement" then return Interfaces.C.size_t (Collapse_Probe.Evaluated_Requirement'Position);
               elsif Text = "declared_verifiers" then return Interfaces.C.size_t (Collapse_Probe.Declared_Verifiers'Position);
               elsif Text = "executed_verifiers" then return Interfaces.C.size_t (Collapse_Probe.Executed_Verifiers'Position);
               elsif Text = "staged_evaluated_requirement" then return Interfaces.C.size_t (Collapse_Probe.Staged_Evaluated_Requirement'Position);
               elsif Text = "staged_executed_verifiers" then return Interfaces.C.size_t (Collapse_Probe.Staged_Executed_Verifiers'Position);
               elsif Text = "staged_examined_root" then return Interfaces.C.size_t (Collapse_Probe.Staged_Examined_Root'Position);
               elsif Text = "expected_checkpoint" then return Interfaces.C.size_t (Collapse_Probe.Expected_Checkpoint'Position);
               elsif Text = "witnessed_checkpoint" then return Interfaces.C.size_t (Collapse_Probe.Witnessed_Checkpoint'Position);
               elsif Text = "registered_watch_set" then return Interfaces.C.size_t (Collapse_Probe.Registered_Watch_Set'Position);
               elsif Text = "watched_set" then return Interfaces.C.size_t (Collapse_Probe.Watched_Set'Position);
               elsif Text = "generation_before" then return Interfaces.C.size_t (Collapse_Probe.Generation_Before'Position);
               elsif Text = "generation_after" then return Interfaces.C.size_t (Collapse_Probe.Generation_After'Position);
               end if;
            when 1 =>
               if Text = "source" then return Interfaces.C.size_t (Observation_Probe.Source'Position);
               elsif Text = "status" then return Interfaces.C.size_t (Observation_Probe.Status'Position);
               elsif Text = "channel" then return Interfaces.C.size_t (Observation_Probe.Channel'Position);
               elsif Text = "stage" then return Interfaces.C.size_t (Observation_Probe.Stage'Position);
               elsif Text = "exit_present" then return Interfaces.C.size_t (Observation_Probe.Exit_Present'Position);
               elsif Text = "exit_integer" then return Interfaces.C.size_t (Observation_Probe.Exit_Integer'Position);
               elsif Text = "supervisor" then return Interfaces.C.size_t (Observation_Probe.Supervisor'Position);
               elsif Text = "supervisor_stopped" then return Interfaces.C.size_t (Observation_Probe.Supervisor_Stopped'Position);
               elsif Text = "bundle_present" then return Interfaces.C.size_t (Observation_Probe.Bundle_Present'Position);
               elsif Text = "bundle_is_mapping" then return Interfaces.C.size_t (Observation_Probe.Bundle_Is_Mapping'Position);
               elsif Text = "bundle_stable" then return Interfaces.C.size_t (Observation_Probe.Bundle_Stable'Position);
               elsif Text = "bundle_changed" then return Interfaces.C.size_t (Observation_Probe.Bundle_Changed'Position);
               elsif Text = "unsatisfied_imports" then return Interfaces.C.size_t (Observation_Probe.Unsatisfied_Imports'Position);
               end if;
            when 2 =>
               if Text = "execution" then return Interfaces.C.size_t (Class_Probe.Execution'Position);
               elsif Text = "outcome" then return Interfaces.C.size_t (Class_Probe.Outcome'Position);
               elsif Text = "bundle" then return Interfaces.C.size_t (Class_Probe.Bundle'Position);
               end if;
            when 3 =>
               if Text = "record_identified" then return Interfaces.C.size_t (Presence_Probe.Record_Identified'Position);
               elsif Text = "verdict_recorded" then return Interfaces.C.size_t (Presence_Probe.Verdict_Recorded'Position);
               elsif Text = "binding_established" then return Interfaces.C.size_t (Presence_Probe.Binding_Established'Position);
               elsif Text = "declaration_matches" then return Interfaces.C.size_t (Presence_Probe.Declaration_Matches'Position);
               elsif Text = "bundle_identified" then return Interfaces.C.size_t (Presence_Probe.Bundle_Identified'Position);
               end if;
            when 4 =>
               if Text = "present" then return Interfaces.C.size_t (Hash_Probe.Present'Position);
               elsif Text = "value" then return Interfaces.C.size_t (Hash_Probe.Value'Position);
               end if;
            when 5 =>
               if Text = "present" then return Interfaces.C.size_t (Counter_Probe.Present'Position);
               elsif Text = "value_le" then return Interfaces.C.size_t (Counter_Probe.Value_LE'Position);
               end if;
            when others => null;
         end case;
      end;
      return Unknown;
   end Layout_Offset;



end Worldline.C_API;
