with Native_Diagnostic_Trace;
with GNAT.Current_Exception;
with Worldline.Evaluation_Authority;
with Evaluation_Pending;
with Evaluation_Pending_V2;
with Evaluation_Completion;
with Evaluation_Completion_Roster;
with Evaluation_Raw_Roster;
with Worldline.Evaluation_Wire;
with Evaluation_History;
with Worldline.Evaluation;
with System.Storage_Elements;
package body Evaluation_Completion_C with SPARK_Mode => On is
   package P renames Evaluation_Pending;
   package V renames Evaluation_Pending_V2;
   package T renames Evaluation_Completion;
   package H renames Evaluation_History;
   package E renames Worldline.Evaluation;
   package Roster renames Evaluation_Completion_Roster;
   package Raw_Roster renames Evaluation_Raw_Roster;
   package W renames Worldline.Evaluation_Wire;
   use type P.Byte;
   use type System.Address;
   use type I64;
   use type U32;
   use type P.Count;
   use type H.Byte_Count;
   use type T.Decision;
   use System.Storage_Elements;
   --  Capture text in owned SPARK memory. Peripheral output happens only
   --  after the typed decision returns to the original C boundary; no sink
   --  termination or foreign I/O purity is assumed by authority code.
   Diagnostic_Active : Boolean := False with Atomic;
   Diagnostic_Failed : Boolean := False with Atomic;

   procedure Diagnostic_Mark (Site : String) is
      Active : constant Boolean := Diagnostic_Active;
      Prefix : constant String := "WORLDLINE_NATIVE_DIAGNOSTIC ";
   begin
      if Active then
         --  Overflow sets Diagnostic_Failed and stays inside this procedure.
         if Site'Length <= Natural'Last - Prefix'Length then
            Native_Diagnostic_Trace.Push (Prefix & Site);
         else
            Diagnostic_Failed := True;
         end if;
      end if;
   exception
      when others => Diagnostic_Failed := True;
   end Diagnostic_Mark;

   procedure Diagnostic_Value (Site : String; Value : I64) is
      Active : constant Boolean := Diagnostic_Active;
   begin
      if Active then
         declare
            Image : constant String := I64'Image (Value);
         begin
            --  Explicit 1-based bounds. Concatenation would also depend on
            --  Site'First, which a length test does not determine.
            if Image'Length <= Natural'Last - 1
              and then Site'Length <= Natural'Last - 1 - Image'Length
            then
               declare
                  Head : constant Natural := Site'Length + 1;
                  Text : String (1 .. Head + Image'Length) := (others => ' ');
               begin
                  Text (1 .. Site'Length) := Site;
                  Text (Head) := '=';
                  if Image'Length > 0 then
                     Text (Head + 1 .. Head + Image'Length) := Image;
                  end if;
                  Diagnostic_Mark (Text);
               end;
            else
               Diagnostic_Failed := True;
            end if;
         end;
      end if;
   exception
      when others => Diagnostic_Failed := True;
   end Diagnostic_Value;

   function Diagnostic_Enabled return Boolean is
      Active : constant Boolean := Diagnostic_Active;
   begin
      return Active;
   end Diagnostic_Enabled;

   function Diagnostic_Retention_Failed return Boolean is
      Failed : constant Boolean := Diagnostic_Failed;
   begin
      return Failed;
   end Diagnostic_Retention_Failed;

   procedure Diagnostic_Capture_Failed is
   begin
      --  No formatting or I/O here: observer failure cannot replace the
      --  primary handler's existing result.
      Diagnostic_Failed := True;
   end Diagnostic_Capture_Failed;

   procedure Diagnostic_Exception (Site, Information : String) is
      Active : constant Boolean := Diagnostic_Active;
      Separator : constant String := " exception=";
   begin
      if Active then
         --  Concatenation retains the first non-null operand's lower bound.
         --  A non-null Site may start above one; use its last index rather
         --  than just its length. A null Site takes Separator's lower bound.
         declare
            Capacity : constant Natural :=
              (if Site'Length = 0 then Natural'Last
               else Natural'Last - Site'Last);
         begin
            if Separator'Length <= Capacity and then
              Information'Length <= Capacity - Separator'Length
            then
               --  Preserve every original byte and the original output path.
               Diagnostic_Mark (Site & Separator & Information);
            else
               --  The original concatenation would raise Constraint_Error,
               --  caught by the same observer-failure policy below.
               Diagnostic_Failed := True;
            end if;
         end;
      end if;
   exception
      when others => Diagnostic_Failed := True;
   end Diagnostic_Exception;

   function Diagnostic_Control (Enable : U32) return U32 is
   begin
      if Enable = 1 then
         declare
            Active : constant Boolean := Diagnostic_Active;
         begin
            if Active then return 1; end if;
         end;
         Diagnostic_Failed := False;
         Diagnostic_Active := True;
         Diagnostic_Mark ("trace.begin");
         return 0;
      elsif Enable = 0 then
         Diagnostic_Mark ("trace.end");
         Diagnostic_Active := False;
         declare
            Failed : constant Boolean := Diagnostic_Failed;
         begin
            return (if Failed then 1 else 0);
         end;
      else
         return 2;
      end if;
   end Diagnostic_Control;

   function ABI_Version return U32 is (1);
   function Layout_Size (Kind : U32) return I64 is
     (case Kind is
        when 1 => Span'Object_Size / System.Storage_Unit,
        when 2 => Optional_Span'Object_Size / System.Storage_Unit,
        when 3 => Cursor'Object_Size / System.Storage_Unit,
        when 4 => Binding'Object_Size / System.Storage_Unit,
        when 5 => Journal_Row'Object_Size / System.Storage_Unit,
        when 6 => Capture'Object_Size / System.Storage_Unit,
        when 7 => Facts'Object_Size / System.Storage_Unit,
        when 8 => Presence'Object_Size / System.Storage_Unit,
        when 9 => Required_Row'Object_Size / System.Storage_Unit,
        when 10 => Check_Row'Object_Size / System.Storage_Unit,
        when 11 => History_Row'Object_Size / System.Storage_Unit,
        when 12 => Request'Object_Size / System.Storage_Unit,
        when 13 => Result'Object_Size / System.Storage_Unit,
        when others => I64'Last);
   function Layout_Alignment (Kind : U32) return I64 is
     (case Kind is
        when 1 => Span'Alignment,
        when 2 => Optional_Span'Alignment,
        when 3 => Cursor'Alignment,
        when 4 => Binding'Alignment,
        when 5 => Journal_Row'Alignment,
        when 6 => Capture'Alignment,
        when 7 => Facts'Alignment,
        when 8 => Presence'Alignment,
        when 9 => Required_Row'Alignment,
        when 10 => Check_Row'Alignment,
        when 11 => History_Row'Alignment,
        when 12 => Request'Alignment,
        when 13 => Result'Alignment,
        when others => I64'Last);
   Zero_Span : constant Span := (First => 0, Length => 0);
   Zero_Optional : constant Optional_Span := (Present => 0, Value => Zero_Span);
   Zero_Cursor : constant Cursor :=
     (Present => 0, Sequence => Zero_Span, Run => Zero_Span);
   Zero_Binding : constant Binding :=
     (Store_Id | Subject | Content | Run | Sequence => Zero_Span,
      Requirement => Zero_Optional);
   Zero_Journal : constant Journal_Row :=
     (Bound => Zero_Binding, Previous => Zero_Cursor, Linked => 0);
   Zero_Capture : constant Capture :=
     (Bound => Zero_Binding, Source_Id => Zero_Span, Context => Zero_Span,
      State => 0, Outcome => 0);
   Zero_Facts : constant Facts := (others => 0);
   Zero_Presence : constant Presence := (others => 0);
   Zero_Required : constant Required_Row :=
     (Check_Id => Zero_Span, Declared => Zero_Span);
   Zero_Check : constant Check_Row :=
     (Bound => Zero_Binding, Check_Id => Zero_Span, Source_Id => Zero_Span,
      Execution => Zero_Optional, Verifier => Zero_Optional,
      State => 0, Outcome => 0, Payload => Zero_Span, Observed => Zero_Facts,
      Report => 0, Evidence => Zero_Presence, Declared => Zero_Span);
   Zero_History : constant History_Row :=
     (Subject | Content | Requirement | Run | Sequence => Zero_Optional,
      State => 0, Outcome => 0);
   Zero_Request : constant Request :=
     (Version => 0, Operation => 0,
      Data => System.Null_Address, Data_Length => 0,
      Journal => System.Null_Address, Journal_Count => 0,
      Current => Zero_Cursor, Captured => Zero_Capture,
      Captured_Results => System.Null_Address, Captured_Count => 0,
      Retained_Present => 0, Retained => Zero_Capture,
      Retained_Results => System.Null_Address, Retained_Count => 0,
      History => System.Null_Address, History_Count => 0,
      Required => System.Null_Address, Required_Count => 0,
      Policy => 0, Before_Root => Zero_Span, After_Root => Zero_Span,
      Completion => Zero_Required, Observed_Binding => Zero_Binding);
   Zero_Result : constant Result :=
     (Reason => 0, Selected => 0, Summary_Present => 0, Summary => Zero_History,
      Execution_State => 0, Outcome => 0, Promotion => 0);
   pragma Compile_Time_Error
     (I64 (Storage_Offset'Last) /= I64'Last, "layout sentinel must stay I64'Last");

   function Offset_Span (Field : U32) return I64 is
   begin
      pragma Compile_Time_Error (Zero_Span.First'Position /= 0, "Span.First");
      pragma Compile_Time_Error (Zero_Span.Length'Position /= 8, "Span.Length");
      return (case Field is when 1 => 0, when 2 => 8, when others => I64'Last);
   end Offset_Span;
   function Offset_Optional_Span (Field : U32) return I64 is
   begin
      pragma Compile_Time_Error (Zero_Optional.Present'Position /= 0, "Optional.Present");
      pragma Compile_Time_Error (Zero_Optional.Value'Position /= 8, "Optional.Value");
      return (case Field is when 1 => 0, when 2 => 8, when others => I64'Last);
   end Offset_Optional_Span;
   function Offset_Cursor (Field : U32) return I64 is
   begin
      pragma Compile_Time_Error (Zero_Cursor.Present'Position /= 0, "Cursor.Present");
      pragma Compile_Time_Error (Zero_Cursor.Sequence'Position /= 8, "Cursor.Sequence");
      pragma Compile_Time_Error (Zero_Cursor.Run'Position /= 24, "Cursor.Run");
      return (case Field is
        when 1 => 0, when 2 => 8, when 3 => 24, when others => I64'Last);
   end Offset_Cursor;
   function Offset_Binding (Field : U32) return I64 is
   begin
      pragma Compile_Time_Error (Zero_Binding.Store_Id'Position /= 0, "Binding.Store");
      pragma Compile_Time_Error (Zero_Binding.Subject'Position /= 16, "Binding.Subject");
      pragma Compile_Time_Error (Zero_Binding.Content'Position /= 32, "Binding.Content");
      pragma Compile_Time_Error (Zero_Binding.Run'Position /= 48, "Binding.Run");
      pragma Compile_Time_Error (Zero_Binding.Sequence'Position /= 64, "Binding.Sequence");
      pragma Compile_Time_Error (Zero_Binding.Requirement'Position /= 80, "Binding.Requirement");
      return (case Field is
        when 1 => 0, when 2 => 16, when 3 => 32, when 4 => 48,
        when 5 => 64, when 6 => 80, when others => I64'Last);
   end Offset_Binding;
   function Offset_Journal (Field : U32) return I64 is
   begin
      pragma Compile_Time_Error (Zero_Journal.Bound'Position /= 0, "Journal.Bound");
      pragma Compile_Time_Error (Zero_Journal.Previous'Position /= 104, "Journal.Previous");
      pragma Compile_Time_Error (Zero_Journal.Linked'Position /= 144, "Journal.Linked");
      return (case Field is
        when 1 => 0, when 2 => 104, when 3 => 144, when others => I64'Last);
   end Offset_Journal;
   function Offset_Capture (Field : U32) return I64 is
   begin
      pragma Compile_Time_Error (Zero_Capture.Bound'Position /= 0, "Capture.Bound");
      pragma Compile_Time_Error (Zero_Capture.Source_Id'Position /= 104, "Capture.Source");
      pragma Compile_Time_Error (Zero_Capture.Context'Position /= 120, "Capture.Context");
      pragma Compile_Time_Error (Zero_Capture.State'Position /= 136, "Capture.State");
      pragma Compile_Time_Error (Zero_Capture.Outcome'Position /= 140, "Capture.Outcome");
      return (case Field is
        when 1 => 0, when 2 => 104, when 3 => 120, when 4 => 136,
        when 5 => 140, when others => I64'Last);
   end Offset_Capture;
   function Offset_Facts (Field : U32) return I64 is
   begin
      pragma Compile_Time_Error (Zero_Facts.Source'Position /= 0, "Facts.Source");
      pragma Compile_Time_Error (Zero_Facts.Status'Position /= 4, "Facts.Status");
      pragma Compile_Time_Error (Zero_Facts.Channel'Position /= 8, "Facts.Channel");
      pragma Compile_Time_Error (Zero_Facts.Stage'Position /= 12, "Facts.Stage");
      pragma Compile_Time_Error (Zero_Facts.Exit_Present'Position /= 16, "Facts.Exit_Present");
      pragma Compile_Time_Error (Zero_Facts.Exit_Integer'Position /= 20, "Facts.Exit_Integer");
      pragma Compile_Time_Error (Zero_Facts.Supervisor'Position /= 24, "Facts.Supervisor");
      pragma Compile_Time_Error (Zero_Facts.Supervisor_Stopped'Position /= 28, "Facts.Stopped");
      pragma Compile_Time_Error (Zero_Facts.Bundle_Present'Position /= 32, "Facts.Bundle_Present");
      pragma Compile_Time_Error (Zero_Facts.Bundle_Is_Mapping'Position /= 36, "Facts.Mapping");
      pragma Compile_Time_Error (Zero_Facts.Bundle_Stable'Position /= 40, "Facts.Stable");
      pragma Compile_Time_Error (Zero_Facts.Bundle_Changed'Position /= 44, "Facts.Changed");
      pragma Compile_Time_Error (Zero_Facts.Unsatisfied_Imports'Position /= 48, "Facts.Imports");
      return (case Field is
        when 1 => 0, when 2 => 4, when 3 => 8, when 4 => 12, when 5 => 16,
        when 6 => 20, when 7 => 24, when 8 => 28, when 9 => 32, when 10 => 36,
        when 11 => 40, when 12 => 44, when 13 => 48, when others => I64'Last);
   end Offset_Facts;
   function Offset_Presence (Field : U32) return I64 is
   begin
      pragma Compile_Time_Error (Zero_Presence.Record_Identified'Position /= 0, "Presence.Record");
      pragma Compile_Time_Error (Zero_Presence.Verdict_Recorded'Position /= 4, "Presence.Verdict");
      pragma Compile_Time_Error (Zero_Presence.Binding_Established'Position /= 8, "Presence.Binding");
      pragma Compile_Time_Error (Zero_Presence.Declaration_Matches'Position /= 12, "Presence.Declaration");
      pragma Compile_Time_Error (Zero_Presence.Bundle_Identified'Position /= 16, "Presence.Bundle");
      return (case Field is
        when 1 => 0, when 2 => 4, when 3 => 8, when 4 => 12,
        when 5 => 16, when others => I64'Last);
   end Offset_Presence;
   function Offset_Required (Field : U32) return I64 is
   begin
      pragma Compile_Time_Error (Zero_Required.Check_Id'Position /= 0, "Required.Check");
      pragma Compile_Time_Error (Zero_Required.Declared'Position /= 16, "Required.Declared");
      return (case Field is when 1 => 0, when 2 => 16, when others => I64'Last);
   end Offset_Required;
   function Offset_Check (Field : U32) return I64 is
   begin
      pragma Compile_Time_Error (Zero_Check.Bound'Position /= 0, "Check.Bound");
      pragma Compile_Time_Error (Zero_Check.Check_Id'Position /= 104, "Check.Check");
      pragma Compile_Time_Error (Zero_Check.Source_Id'Position /= 120, "Check.Source");
      pragma Compile_Time_Error (Zero_Check.Execution'Position /= 136, "Check.Execution");
      pragma Compile_Time_Error (Zero_Check.Verifier'Position /= 160, "Check.Verifier");
      pragma Compile_Time_Error (Zero_Check.State'Position /= 184, "Check.State");
      pragma Compile_Time_Error (Zero_Check.Outcome'Position /= 188, "Check.Outcome");
      pragma Compile_Time_Error (Zero_Check.Payload'Position /= 192, "Check.Payload");
      pragma Compile_Time_Error (Zero_Check.Observed'Position /= 208, "Check.Observed");
      pragma Compile_Time_Error (Zero_Check.Report'Position /= 260, "Check.Report");
      pragma Compile_Time_Error (Zero_Check.Evidence'Position /= 264, "Check.Evidence");
      pragma Compile_Time_Error (Zero_Check.Declared'Position /= 288, "Check.Declared");
      return (case Field is
        when 1 => 0, when 2 => 104, when 3 => 120, when 4 => 136, when 5 => 160,
        when 6 => 184, when 7 => 188, when 8 => 192, when 9 => 208, when 10 => 260,
        when 11 => 264, when 12 => 288, when others => I64'Last);
   end Offset_Check;
   function Offset_History (Field : U32) return I64 is
   begin
      pragma Compile_Time_Error (Zero_History.Subject'Position /= 0, "History.Subject");
      pragma Compile_Time_Error (Zero_History.Content'Position /= 24, "History.Content");
      pragma Compile_Time_Error (Zero_History.Requirement'Position /= 48, "History.Requirement");
      pragma Compile_Time_Error (Zero_History.Run'Position /= 72, "History.Run");
      pragma Compile_Time_Error (Zero_History.Sequence'Position /= 96, "History.Sequence");
      pragma Compile_Time_Error (Zero_History.State'Position /= 120, "History.State");
      pragma Compile_Time_Error (Zero_History.Outcome'Position /= 124, "History.Outcome");
      return (case Field is
        when 1 => 0, when 2 => 24, when 3 => 48, when 4 => 72,
        when 5 => 96, when 6 => 120, when 7 => 124, when others => I64'Last);
   end Offset_History;
   function Offset_Request (Field : U32) return I64 is
   begin
      pragma Compile_Time_Error (Zero_Request.Version'Position /= 0, "Request.Version");
      pragma Compile_Time_Error (Zero_Request.Operation'Position /= 4, "Request.Operation");
      pragma Compile_Time_Error (Zero_Request.Data'Position /= 8, "Request.Data");
      pragma Compile_Time_Error (Zero_Request.Data_Length'Position /= 16, "Request.Data_Length");
      pragma Compile_Time_Error (Zero_Request.Journal'Position /= 24, "Request.Journal");
      pragma Compile_Time_Error (Zero_Request.Journal_Count'Position /= 32, "Request.Journal_Count");
      pragma Compile_Time_Error (Zero_Request.Current'Position /= 40, "Request.Current");
      pragma Compile_Time_Error (Zero_Request.Captured'Position /= 80, "Request.Captured");
      pragma Compile_Time_Error (Zero_Request.Captured_Results'Position /= 224, "Request.Captured_Results");
      pragma Compile_Time_Error (Zero_Request.Captured_Count'Position /= 232, "Request.Captured_Count");
      pragma Compile_Time_Error (Zero_Request.Retained_Present'Position /= 240, "Request.Retained_Present");
      pragma Compile_Time_Error (Zero_Request.Retained'Position /= 248, "Request.Retained");
      pragma Compile_Time_Error (Zero_Request.Retained_Results'Position /= 392, "Request.Retained_Results");
      pragma Compile_Time_Error (Zero_Request.Retained_Count'Position /= 400, "Request.Retained_Count");
      pragma Compile_Time_Error (Zero_Request.History'Position /= 408, "Request.History");
      pragma Compile_Time_Error (Zero_Request.History_Count'Position /= 416, "Request.History_Count");
      pragma Compile_Time_Error (Zero_Request.Required'Position /= 424, "Request.Required");
      pragma Compile_Time_Error (Zero_Request.Required_Count'Position /= 432, "Request.Required_Count");
      pragma Compile_Time_Error (Zero_Request.Policy'Position /= 440, "Request.Policy");
      pragma Compile_Time_Error (Zero_Request.Before_Root'Position /= 448, "Request.Before_Root");
      pragma Compile_Time_Error (Zero_Request.After_Root'Position /= 464, "Request.After_Root");
      pragma Compile_Time_Error (Zero_Request.Completion'Position /= 480, "Request.Completion");
      pragma Compile_Time_Error (Zero_Request.Observed_Binding'Position /= 512, "Request.Observed");
      return (case Field is
        when 1 => 0, when 2 => 4, when 3 => 8, when 4 => 16, when 5 => 24,
        when 6 => 32, when 7 => 40, when 8 => 80, when 9 => 224, when 10 => 232,
        when 11 => 240, when 12 => 248, when 13 => 392, when 14 => 400, when 15 => 408,
        when 16 => 416, when 17 => 424, when 18 => 432, when 19 => 440, when 20 => 448,
        when 21 => 464, when 22 => 480, when 23 => 512, when others => I64'Last);
   end Offset_Request;
   function Offset_Result (Field : U32) return I64 is
   begin
      pragma Compile_Time_Error (Zero_Result.Reason'Position /= 0, "Result.Reason");
      pragma Compile_Time_Error (Zero_Result.Selected'Position /= 8, "Result.Selected");
      pragma Compile_Time_Error (Zero_Result.Summary_Present'Position /= 16, "Result.Summary_Present");
      pragma Compile_Time_Error (Zero_Result.Summary'Position /= 24, "Result.Summary");
      pragma Compile_Time_Error (Zero_Result.Execution_State'Position /= 152, "Result.Execution");
      pragma Compile_Time_Error (Zero_Result.Outcome'Position /= 156, "Result.Outcome");
      pragma Compile_Time_Error (Zero_Result.Promotion'Position /= 160, "Result.Promotion");
      return (case Field is
        when 1 => 0, when 2 => 8, when 3 => 16, when 4 => 24,
        when 5 => 152, when 6 => 156, when 7 => 160, when others => I64'Last);
   end Offset_Result;
   function Layout_Offset (Kind, Field : U32) return I64 is
     (case Kind is
        when 1 => Offset_Span (Field),
        when 2 => Offset_Optional_Span (Field),
        when 3 => Offset_Cursor (Field),
        when 4 => Offset_Binding (Field),
        when 5 => Offset_Journal (Field),
        when 6 => Offset_Capture (Field),
        when 7 => Offset_Facts (Field),
        when 8 => Offset_Presence (Field),
        when 9 => Offset_Required (Field),
        when 10 => Offset_Check (Field),
        when 11 => Offset_History (Field),
        when 12 => Offset_Request (Field),
        when 13 => Offset_Result (Field),
        when others => I64'Last);
   function Extent_Valid (A : System.Address; Length, Alignment : I64)
      return Boolean is
     (Length >= 0 and then Alignment > 0
      and then Length <= I64 (Storage_Offset'Last)
      and then (Length = 0 or else
        (A /= System.Null_Address
         and then To_Integer (A) mod Integer_Address (Alignment) = 0
         and then Integer_Address (Length - 1) <= Integer_Address'Last - To_Integer (A))));
   function Disjoint (L : System.Address; LL : I64; R : System.Address; RL : I64)
      return Boolean is
     (LL = 0 or else RL = 0 or else
       (if To_Integer (L) <= To_Integer (R) then
          Integer_Address (LL) <= To_Integer (R) - To_Integer (L)
        else Integer_Address (RL) <= To_Integer (L) - To_Integer (R)))
   with Pre => LL >= 0 and then RL >= 0;
   function Array_Extent (A : System.Address; N, Stride, Alignment : I64)
      return Boolean is
     (N >= 0 and then Stride > 0
      and then N <= I64 (Storage_Offset'Last) / Stride
      and then Extent_Valid (A, N * Stride, Alignment));
   function Array_Valid (A : System.Address; N, Stride, Alignment : I64;
                         Output : System.Address; Output_Length : I64)
      return Boolean is
     (Array_Extent (A, N, Stride, Alignment)
      and then Disjoint (A, N * Stride, Output, Output_Length))
   with Pre => Output_Length >= 0;
   function Valid (S : Span) return Boolean is (S.First >= 1 and then S.Length >= 0);
   function Valid (S : Optional_Span) return Boolean is
     (S.Present <= 1 and then (S.Present = 0 or else Valid (S.Value)));
   function Valid (C : Cursor) return Boolean is
     (C.Present <= 1 and then
        (C.Present = 0 or else (Valid (C.Sequence) and then Valid (C.Run))));
   function Valid (B : Binding) return Boolean is
     (Valid (B.Store_Id) and then Valid (B.Subject) and then Valid (B.Content)
      and then Valid (B.Run) and then Valid (B.Sequence) and then Valid (B.Requirement));
   function Convert (S : Span) return P.Span is
     (P.Index (S.First), P.Count (S.Length))
   with Pre => Valid (S);
   function Convert (S : Optional_Span) return V.Optional_Requirement
     with Pre => Valid (S)
   is
   begin
      if S.Present = 0 then
         return (Present => False);
      else
         return (True, V.Requirement_Id (Convert (S.Value)));
      end if;
   end Convert;
   function Convert (B : Binding) return T.Attempt_Binding is
     (T.Store_Identity (Convert (B.Store_Id)), T.Subject_Identity (Convert (B.Subject)),
      T.Content_Identity (Convert (B.Content)), T.Run_Identity (Convert (B.Run)),
      T.Epoch (Convert (B.Sequence)), Convert (B.Requirement))
   with Pre => Valid (B);
   function Convert (C : Cursor) return T.Cursor
     with Pre => Valid (C)
   is
   begin
      if C.Present = 0 then
         return (Present => False);
      else
         return (True, T.Run_Identity (Convert (C.Run)), T.Epoch (Convert (C.Sequence)));
      end if;
   end Convert;
   function Previous (C : Cursor) return P.Cursor
     with Pre => Valid (C)
   is
   begin
      if C.Present = 0 then
         return (Present => False);
      else
         return (True, Convert (C.Sequence), Convert (C.Run));
      end if;
   end Previous;
   function Valid (C : Capture) return Boolean is
     (Valid (C.Bound) and then Valid (C.Source_Id) and then Valid (C.Context)
      and then C.State in U32 (E.Terminal_State'Pos (E.Terminal_State'First)) ..
                          U32 (E.Terminal_State'Pos (E.Terminal_State'Last))
      and then C.Outcome <= U32 (E.Outcome'Pos (E.Outcome'Last)));
   function Convert (C : Capture) return T.Terminal_Record is
     (Convert (C.Bound), T.Source_Identity (Convert (C.Source_Id)),
      T.Captured_Bytes (Convert (C.Context)), E.Terminal_State'Val (C.State),
      E.Outcome'Val (C.Outcome))
   with Pre => Valid (C);
   function Valid (F : Facts) return Boolean is
     (F.Source <= U32 (E.Origin'Pos (E.Origin'Last))
      and then F.Status <= U32 (E.Raw_Status'Pos (E.Raw_Status'Last))
      and then F.Channel <= U32 (E.Channel_State'Pos (E.Channel_State'Last))
      and then F.Stage <= U32 (E.Rejection_Stage'Pos (E.Rejection_Stage'Last))
      and then F.Supervisor <= U32 (E.Supervision_State'Pos (E.Supervision_State'Last))
      and then F.Exit_Present <= 1 and then F.Exit_Integer <= 1
      and then F.Supervisor_Stopped <= 1 and then F.Bundle_Present <= 1
      and then F.Bundle_Is_Mapping <= 1 and then F.Bundle_Stable <= 1
      and then F.Bundle_Changed <= 1 and then F.Unsatisfied_Imports <= 1
      --  Preserve the original Evaluation_Classify dependent encoding guards.
      --  These guards reject malformed transport, not an ordinary negative fact.
      and then F.Exit_Integer <= F.Exit_Present
      and then F.Bundle_Stable <= F.Bundle_Present
      and then F.Bundle_Stable <= F.Bundle_Is_Mapping
      and then F.Bundle_Changed <= F.Bundle_Present
      and then F.Bundle_Changed <= F.Bundle_Is_Mapping);
   function Convert (F : Facts) return E.Observations is
     (E.Origin'Val (F.Source), E.Raw_Status'Val (F.Status),
      E.Channel_State'Val (F.Channel), E.Rejection_Stage'Val (F.Stage),
      F.Exit_Present = 1, F.Exit_Integer = 1, E.Supervision_State'Val (F.Supervisor),
      F.Supervisor_Stopped = 1, F.Bundle_Present = 1, F.Bundle_Is_Mapping = 1,
      F.Bundle_Stable = 1, F.Bundle_Changed = 1, F.Unsatisfied_Imports = 1)
   with Pre => Valid (F);
   function Valid (F : Presence) return Boolean is
     (F.Record_Identified <= 1 and then F.Verdict_Recorded <= 1
      and then F.Binding_Established <= 1 and then F.Declaration_Matches <= 1
      and then F.Bundle_Identified <= 1);
   function Convert (F : Presence) return E.Evidence_Presence is
     (F.Record_Identified = 1, F.Verdict_Recorded = 1, F.Binding_Established = 1,
      F.Declaration_Matches = 1, F.Bundle_Identified = 1);
   function Valid (C : Check_Row) return Boolean is
     (Valid (C.Bound) and then Valid (C.Check_Id) and then Valid (C.Source_Id)
      and then Valid (C.Execution) and then Valid (C.Verifier) and then Valid (C.Payload)
      and then Valid (C.Observed) and then Valid (C.Evidence) and then Valid (C.Declared)
      and then C.Report <= U32 (E.Report_Integrity'Pos (E.Report_Integrity'Last))
      and then C.State <= U32 (E.Execution_State'Pos (E.Execution_State'Last))
      and then C.Outcome <= U32 (E.Outcome'Pos (E.Outcome'Last)));
   function Convert (C : Check_Row) return T.Result_Record is
     (Convert (C.Bound), T.Check_Identity (Convert (C.Check_Id)),
      T.Source_Identity (Convert (C.Source_Id)),
      (if C.Execution.Present = 0 then (Present => False)
       else (True, T.Execution_Identity (Convert (C.Execution.Value)))),
      (if C.Verifier.Present = 0 then (Present => False)
       else (True, T.Verifier_Identity (Convert (C.Verifier.Value)))),
      E.Execution_State'Val (C.State), E.Outcome'Val (C.Outcome),
      T.Captured_Bytes (Convert (C.Payload)))
   with Pre => Valid (C);
   function Valid (C : History_Row) return Boolean is
     (Valid (C.Subject) and then Valid (C.Content) and then Valid (C.Requirement)
      and then Valid (C.Run) and then Valid (C.Sequence)
      and then C.State <= U32 (H.Lifecycle'Pos (H.Lifecycle'Last))
      and then C.Outcome <= U32 (H.Verdict'Pos (H.Verdict'Last)));
   function H_Span (S : Span) return H.Identity_Span is
     (H.Byte_Index (S.First), H.Byte_Count (S.Length))
   with Pre => Valid (S);
   function Convert (C : History_Row) return H.Evaluation_Record is
     ((if C.Subject.Present = 0 then (Present => False)
       else (True, H.Subject_Id (H_Span (C.Subject.Value)))),
      (if C.Content.Present = 0 then (Present => False)
       else (True, H.Content_Id (H_Span (C.Content.Value)))),
      (if C.Requirement.Present = 0 then (Present => False)
       else (True, H.Requirement_Id (H_Span (C.Requirement.Value)))),
      (if C.Run.Present = 0 then (Present => False)
       else (True, H.Evaluation_Id (H_Span (C.Run.Value)))),
      (if C.Sequence.Present = 0 then (Present => False)
       else (True, H.Epoch_Id (H_Span (C.Sequence.Value)))),
      H.Lifecycle'Val (C.State), H.Verdict'Val (C.Outcome))
   with Pre => Valid (C);
   function Export_Span (S : H.Identity_Span) return Span is
     (I64 (S.First), I64 (S.Length));
   function Export_Row (C : H.Evaluation_Record) return History_Row is
     ((if C.Subject.Present then (1, Export_Span (H.Identity_Span (C.Subject.Value))) else (0, (1, 0))),
      (if C.Content.Present then (1, Export_Span (H.Identity_Span (C.Content.Value))) else (0, (1, 0))),
      (if C.Requirement.Present then (1, Export_Span (H.Identity_Span (C.Requirement.Value))) else (0, (1, 0))),
      (if C.Run.Present then (1, Export_Span (H.Identity_Span (C.Run.Value))) else (0, (1, 0))),
      (if C.Sequence.Present then (1, Export_Span (H.Identity_Span (C.Sequence.Value))) else (0, (1, 0))),
      U32 (H.Lifecycle'Pos (C.State)), U32 (H.Verdict'Pos (C.Outcome)));
   Empty_Span : constant P.Span := (First => 1, Length => 0);
   Blank_Journal : constant V.Intent :=
     (Base =>
        (Store_Id | Subject | Content | Run | Sequence => Empty_Span,
         Previous => (Present => False),
         State => P.Reserved),
      Requirement => (Present => False));
   Blank_Result : constant T.Result_Record :=
     (Binding =>
        (Store => T.Store_Identity (Empty_Span),
         Subject => T.Subject_Identity (Empty_Span),
         Content => T.Content_Identity (Empty_Span),
         Run => T.Run_Identity (Empty_Span),
         Sequence => T.Epoch (Empty_Span),
         Requirement => (Present => False)),
      Check => T.Check_Identity (Empty_Span),
      Source => T.Source_Identity (Empty_Span),
      Execution => (Present => False),
      Verifier => (Present => False),
      State => E.Execution_State'First,
      Outcome => E.Outcome'First,
      Payload => T.Captured_Bytes (Empty_Span));
   Blank_Measured : constant Roster.Measured_Result :=
     (Item => Blank_Result,
      Facts =>
        (Source => E.Origin'First,
         Status => E.Raw_Status'First,
         Channel => E.Channel_State'First,
         Stage => E.Rejection_Stage'First,
         Exit_Present => False,
         Exit_Integer => False,
         Supervisor => E.Supervision_State'First,
         Supervisor_Stopped => False,
         Bundle_Present => False,
         Bundle_Is_Mapping => False,
         Bundle_Stable => False,
         Bundle_Changed => False,
         Unsatisfied_Imports => False),
      Report => E.Report_Integrity'First,
      Presence => (others => False),
      Declared => T.Captured_Bytes (Empty_Span));
   Blank_Raw : constant Raw_Roster.Measured_Result :=
     (Item => Blank_Result,
      Raw => W.Zero_Record,
      Confinement => 0,
      Declared => T.Captured_Bytes (Empty_Span));
   Blank_History : constant H.Evaluation_Record :=
     (Subject => (Present => False),
      Content => (Present => False),
      Requirement => (Present => False),
      Run => (Present => False),
      Sequence => (Present => False),
      State => H.Lifecycle'First,
      Outcome => H.Verdict'First);
   Blank_Required : constant Roster.Required_Check :=
     (Check => T.Check_Identity (Empty_Span),
      Declared => T.Captured_Bytes (Empty_Span));
   Blank_Joined : constant Worldline.Evaluation_Authority.Context_Row :=
     (Item => Blank_Result,
      Declared => T.Captured_Bytes (Empty_Span),
      Actual_Declared => T.Captured_Bytes (Empty_Span),
      Expected => (others => (Present => False)),
      Observed => (others => (Present => False)));
   Blank_Meta : constant Worldline.Evaluation_Authority.Row_Metadata :=
     (Check => Empty_Span,
      Source => Empty_Span,
      Payload => Empty_Span,
      Execution => (Present => False),
      Verifier => (Present => False));

   function Rows_Fit (Count, First, Last : I64) return Boolean is
     (Count >= 0 and then First = 1
      and then (if Count = 0 then Last < First else Last = Count));
   function Fits (Data : Bytes_Observer; Count : I64) return Boolean is
     (Count >= 0 and then (if Count = 0 then True else
       Data /= null and then Data.all'First = 1 and then I64 (Data.all'Last) = Count));
   function Fits (Data : Journal_Row_Observer; Count : I64) return Boolean is
     (Count >= 0 and then (if Count = 0 then True else
       Data /= null and then Rows_Fit (Count, Data.all'First, Data.all'Last)));
   function Fits (Data : Check_Row_Observer; Count : I64) return Boolean is
     (Count >= 0 and then (if Count = 0 then True else
       Data /= null and then Rows_Fit (Count, Data.all'First, Data.all'Last)));
   function Fits (Data : History_Row_Observer; Count : I64) return Boolean is
     (Count >= 0 and then (if Count = 0 then True else
       Data /= null and then Rows_Fit (Count, Data.all'First, Data.all'Last)));
   function Fits (Data : Required_Row_Observer; Count : I64) return Boolean is
     (Count >= 0 and then (if Count = 0 then True else
       Data /= null and then Rows_Fit (Count, Data.all'First, Data.all'Last)));
   function Fits (Data : Raw_Row_Observer; Count : I64) return Boolean is
     (Count >= 0 and then (if Count = 0 then True else
       Data /= null and then Rows_Fit (Count, Data.all'First, Data.all'Last)));
   function Fits (Data : Context_Row_Observer; Count : I64) return Boolean is
     (Count >= 0 and then (if Count = 0 then True else
       Data /= null and then Rows_Fit (Count, Data.all'First, Data.all'Last)));
   function Fits (Data : Row_Metadata_Observer; Count : I64) return Boolean is
     (Count >= 0 and then (if Count = 0 then True else
       Data /= null and then Rows_Fit (Count, Data.all'First, Data.all'Last)));

   procedure Read_Request (Value : Request_View; Item : out Request) is
   begin
      Item := Value.Descriptor;
   end Read_Request;

   procedure Read_Journal (Value : Journal_Row; Item : out Journal_Row) is
   begin
      Item := Value;
   end Read_Journal;

   procedure Read_Check (Value : Check_Row; Item : out Check_Row) is
   begin
      Item := Value;
   end Read_Check;

   procedure Read_History (Value : History_Row; Item : out History_Row) is
   begin
      Item := Value;
   end Read_History;

   procedure Read_Required (Value : Required_Row; Item : out Required_Row) is
   begin
      Item := Value;
   end Read_Required;

   procedure Read_Raw (Value : W.Raw_Record; Item : out W.Raw_Record) is
   begin
      Item := Value;
   end Read_Raw;

   procedure Read_Octet (Value : P.Byte; Item : out P.Byte) is
   begin
      Item := Value;
   end Read_Octet;

   procedure Write_Result (Value : Result; Item : in out Result) is
   begin
      Item := Value;
   end Write_Result;

   procedure Copy_Data
     (Source : Bytes_Observer; Length : I64; Data : out P.Bytes)
     with Pre => Length >= 0 and then Data'First = 1
       and then I64 (Data'Length) = Length
       and then (Length = 0 or else
         (Source /= null and then Source.all'First = 1
          and then I64 (Source.all'Length) = Length))
   is
   begin
      for I in Data'Range loop
         Read_Octet (Source.all (I), Data (I));
      end loop;
   end Copy_Data;
   function Decide (Input : Request_View; Output : System.Address;
                    Observed : in out Result) return Interfaces.C.int is
      Input_Size : constant I64 := Request'Object_Size / System.Storage_Unit;
      Output_Size : constant I64 := Result'Object_Size / System.Storage_Unit;
      J_Stride : constant I64 := Journal_Row'Object_Size / System.Storage_Unit;
      C_Stride : constant I64 := Check_Row'Object_Size / System.Storage_Unit;
      H_Stride : constant I64 := History_Row'Object_Size / System.Storage_Unit;
      S_Stride : constant I64 := Required_Row'Object_Size / System.Storage_Unit;
   begin
      if not (Fits (Input.Data, Input.Descriptor.Data_Length)
        and then Fits (Input.Journal, Input.Descriptor.Journal_Count)
        and then Fits (Input.Captured, Input.Descriptor.Captured_Count)
        and then Fits (Input.Retained, Input.Descriptor.Retained_Count)
        and then Fits (Input.History, Input.Descriptor.History_Count)
        and then Fits (Input.Required, Input.Descriptor.Required_Count)) then return 255; end if;
      if not Extent_Valid (Input.Address, Input_Size, Request'Alignment)
        or else not Extent_Valid (Output, Output_Size, Result'Alignment)
        or else not Disjoint (Input.Address, Input_Size, Output, Output_Size)
      then
         return 255;
      end if;
      declare
         Raw_R : Request;
      begin
         Read_Request (Input, Raw_R);
         declare
            R : constant Request := Raw_R;
            Data_Length : constant I64 := R.Data_Length;
            Journal_Count : constant I64 := R.Journal_Count;
            Captured_Count : constant I64 := R.Captured_Count;
            Retained_Count : constant I64 := R.Retained_Count;
            History_Count : constant I64 := R.History_Count;
            Required_Count : constant I64 := R.Required_Count;
         begin
            if R.Version /= 1 or else R.Operation > 2
              or else R.Policy > U32 (Roster.Declaration'Pos (Roster.Declaration'Last))
              or else R.Retained_Present > 1
              or else Data_Length < 0 or else Journal_Count < 0
              or else Captured_Count < 0 or else Retained_Count < 0
              or else History_Count < 0 or else Required_Count < 0
              or else not Extent_Valid (R.Data, Data_Length, P.Byte'Alignment)
              or else not Disjoint (R.Data, Data_Length, Output, Output_Size)
              or else not Array_Valid
                (R.Journal, Journal_Count, J_Stride, Journal_Row'Alignment,
                 Output, Output_Size)
              or else not Array_Valid
                (R.Captured_Results, Captured_Count, C_Stride, Check_Row'Alignment,
                 Output, Output_Size)
              or else not Array_Valid
                (R.Retained_Results, Retained_Count, C_Stride, Check_Row'Alignment,
                 Output, Output_Size)
              or else not Array_Valid
                (R.History, History_Count, H_Stride, History_Row'Alignment,
                 Output, Output_Size)
              or else not Array_Valid
                (R.Required, Required_Count, S_Stride, Required_Row'Alignment,
                 Output, Output_Size)
              or else not Valid (R.Observed_Binding)
              or else not Valid (R.Before_Root) or else not Valid (R.After_Root)
              or else not Valid (R.Completion.Check_Id)
              or else not Valid (R.Completion.Declared)
              or else not Valid (R.Current) or else not Valid (R.Captured)
              or else (R.Retained_Present = 1 and then not Valid (R.Retained))
            then
               return 255;
            end if;
            declare
               A : P.Bytes (1 .. P.Count (Data_Length));
               J : V.Journal (1 .. P.Count (Journal_Count)) :=
                 (others => Blank_Journal);
               Measures : Roster.Measured_Array (1 .. P.Count (Captured_Count)) :=
                 (others => Blank_Measured);
               Captured : T.Result_Array (1 .. P.Count (Captured_Count)) :=
                 (others => Blank_Result);
               Retained_Results : T.Result_Array (1 .. P.Count (Retained_Count)) :=
                 (others => Blank_Result);
               History : H.History (1 .. H.Byte_Count (History_Count)) :=
                 (others => Blank_History);
               Required : Roster.Check_Array (1 .. P.Count (Required_Count)) :=
                 (others => Blank_Required);
               Classified : Roster.Classification;
               Retained : constant T.Optional_Terminal :=
                 (if R.Retained_Present = 0 then (Present => False)
                  else (True, Convert (R.Retained)));
               Reason : T.Decision;
               Selected : P.Count;
               Response : Result := (Reason => 0, Selected => 0,
                 Summary_Present => 0, Summary =>
                   (Subject | Content | Requirement | Run | Sequence => (0, (1, 0)),
                    State | Outcome => 0),
                 Execution_State => 0, Outcome => 0, Promotion => 0);
            begin
               Copy_Data (Input.Data, Data_Length, A);
               for I in J'Range loop
                  declare
                     X : Journal_Row;
                  begin
                     Read_Journal
                       (Input.Journal.all (I64 (I)), X);
                     if not Valid (X.Bound) or else not Valid (X.Previous)
                       or else X.Linked > 1
                     then
                        return 255;
                     end if;
                     J (I) := (Base =>
                       (Convert (X.Bound.Store_Id), Convert (X.Bound.Subject),
                        Convert (X.Bound.Content), Convert (X.Bound.Run),
                        Convert (X.Bound.Sequence), Previous (X.Previous),
                        (if X.Linked = 0 then P.Reserved else P.Linked)),
                       Requirement => Convert (X.Bound.Requirement));
                  end;
               end loop;
               for I in Captured'Range loop
                  declare
                     X : Check_Row;
                  begin
                     Read_Check
                       (Input.Captured.all (I64 (I)), X);
                     if not Valid (X) then
                        return 255;
                     end if;
                     Captured (I) := Convert (X);
                     Measures (I) := (Captured (I), Convert (X.Observed),
                       E.Report_Integrity'Val (X.Report), Convert (X.Evidence),
                       T.Captured_Bytes (Convert (X.Declared)));
                  end;
               end loop;
               for I in Retained_Results'Range loop
                  declare
                     X : Check_Row;
                  begin
                     Read_Check
                       (Input.Retained.all (I64 (I)), X);
                     if not Valid (X) then
                        return 255;
                     end if;
                     Retained_Results (I) := Convert (X);
                  end;
               end loop;
               for I in History'Range loop
                  declare
                     X : History_Row;
                  begin
                     Read_History
                       (Input.History.all (I64 (I)), X);
                     if not Valid (X) then
                        return 255;
                     end if;
                     History (I) := Convert (X);
                  end;
               end loop;
               for I in Required'Range loop
                  declare
                     X : Required_Row;
                  begin
                     Read_Required
                       (Input.Required.all (I64 (I)), X);
                     if not Valid (X.Check_Id) or else not Valid (X.Declared) then
                        return 255;
                     end if;
                     Required (I) :=
                       (T.Check_Identity (Convert (X.Check_Id)),
                        T.Captured_Bytes (Convert (X.Declared)));
                  end;
               end loop;
               if R.Operation /= 1 then
                  Reason := T.Decide (A, J, Convert (R.Current), Convert (R.Captured),
                                      Captured, Retained, Retained_Results);
               else
                  T.Apply (A, J, Convert (R.Current), Convert (R.Captured), Captured,
                           Retained, Retained_Results, History, Reason);
               end if;
               Response.Reason := U32 (T.Decision'Pos (Reason));
               if Reason in T.Retain_Terminal | T.Already_Retained then
                  Selected := T.Find_Run
                    (A, J, T.Run_Identity (Convert (R.Captured.Bound.Run)));
                  Response.Selected := I64 (Selected);
                  if R.Operation = 2 then
                     Classified := Roster.Classify (A, Convert (R.Captured.Bound),
                       Measures, Required, Roster.Declaration'Val (R.Policy),
                       (Convert (R.Observed_Binding),
                        T.Captured_Bytes (Convert (R.Before_Root)),
                        T.Captured_Bytes (Convert (R.After_Root))),
                       (T.Check_Identity (Convert (R.Completion.Check_Id)),
                        T.Captured_Bytes (Convert (R.Completion.Declared))));
                     Response.Execution_State :=
                       U32 (E.Execution_State'Pos (Classified.State));
                     Response.Outcome := U32 (E.Outcome'Pos (Classified.Outcome));
                     Response.Promotion := Boolean'Pos (Classified.Promotion_Ready);
                  end if;
                  if R.Operation = 1 then
                     Response.Summary_Present := 1;
                     Response.Summary := Export_Row (History (H.Byte_Index (Selected)));
                  end if;
               end if;
               Write_Result (Response, Observed);
               return 0;
            end;
         end;
      end;
   exception
      when others =>
         return 255;
   end Decide;
   function Raw_Decide_Common
     (Input : Request_View; Raw : Raw_View; Output : System.Address;
      Have_Output : Boolean;
      Observed : in out Result) return Interfaces.C.int
     with Side_Effects is
      Input_Size : constant I64 := Request'Object_Size / System.Storage_Unit;
      Output_Size : constant I64 := Result'Object_Size / System.Storage_Unit;
      Raw_Stride : constant I64 := W.Raw_Record'Object_Size / System.Storage_Unit;
      J_Stride : constant I64 := Journal_Row'Object_Size / System.Storage_Unit;
      C_Stride : constant I64 := Check_Row'Object_Size / System.Storage_Unit;
      H_Stride : constant I64 := History_Row'Object_Size / System.Storage_Unit;
      S_Stride : constant I64 := Required_Row'Object_Size / System.Storage_Unit;
      function Output_Separated
        (A : System.Address; N, Stride, Alignment : I64) return Boolean is
        (Array_Extent (A, N, Stride, Alignment)
         and then (not Have_Output
                   or else Disjoint (A, N * Stride, Output, Output_Size)));
   begin
      if not (Fits (Input.Data, Input.Descriptor.Data_Length)
        and then Fits (Input.Journal, Input.Descriptor.Journal_Count)
        and then Fits (Input.Captured, Input.Descriptor.Captured_Count)
        and then Fits (Input.Retained, Input.Descriptor.Retained_Count)
        and then Fits (Input.History, Input.Descriptor.History_Count)
        and then Fits (Input.Required, Input.Descriptor.Required_Count)
        and then Fits (Raw.Rows, Input.Descriptor.Captured_Count)
        and then Fits (Raw.Confinements, Input.Descriptor.Captured_Count)) then return 255; end if;
      if not Extent_Valid (Input.Address, Input_Size, Request'Alignment)
        or else (Have_Output and then
                 (not Extent_Valid (Output, Output_Size, Result'Alignment)
                  or else not Disjoint (Input.Address, Input_Size, Output, Output_Size)))
      then return 255; end if;
      declare
         Raw_R : Request;
      begin
         Read_Request (Input, Raw_R);
         declare
            R : constant Request := Raw_R;
            Data_Length : constant I64 := R.Data_Length;
            Journal_Count : constant I64 := R.Journal_Count;
            Captured_Count : constant I64 := R.Captured_Count;
            Retained_Count : constant I64 := R.Retained_Count;
            History_Count : constant I64 := R.History_Count;
            Required_Count : constant I64 := R.Required_Count;
         begin
         if R.Version /= 1 or else R.Operation /= 2
           or else R.Policy > U32 (Roster.Declaration'Pos (Roster.Declaration'Last))
           or else R.Retained_Present > 1
           or else Data_Length < 0 or else Journal_Count < 0
           or else Captured_Count < 0 or else Retained_Count < 0
           or else History_Count < 0 or else Required_Count < 0
           or else not Extent_Valid (R.Data, Data_Length, P.Byte'Alignment)
           or else (Have_Output and then
                    not Disjoint (R.Data, Data_Length, Output, Output_Size))
           or else not Output_Separated
             (R.Journal, Journal_Count, J_Stride, Journal_Row'Alignment)
           or else not Output_Separated
             (R.Captured_Results, Captured_Count, C_Stride, Check_Row'Alignment)
           or else not Output_Separated
             (R.Retained_Results, Retained_Count, C_Stride, Check_Row'Alignment)
           or else not Output_Separated
             (R.History, History_Count, H_Stride, History_Row'Alignment)
           or else not Output_Separated
             (R.Required, Required_Count, S_Stride, Required_Row'Alignment)
           or else not Output_Separated
             (Raw.Rows_Address, Captured_Count, Raw_Stride, W.Raw_Record'Alignment)
           or else not Output_Separated (Raw.Confinements_Address, Captured_Count, 1, P.Byte'Alignment)
           or else not Valid (R.Observed_Binding)
           or else not Valid (R.Before_Root) or else not Valid (R.After_Root)
           or else not Valid (R.Completion.Check_Id) or else not Valid (R.Completion.Declared)
           or else not Valid (R.Current) or else not Valid (R.Captured)
           or else (R.Retained_Present = 1 and then not Valid (R.Retained))
         then return 255; end if;
         declare
            A : P.Bytes (1 .. P.Count (Data_Length));
            J : V.Journal (1 .. P.Count (Journal_Count)) := (others => Blank_Journal);
            Measures : Raw_Roster.Measured_Array (1 .. P.Count (Captured_Count)) :=
              (others => Blank_Raw);
            Captured : T.Result_Array (1 .. P.Count (Captured_Count)) :=
              (others => Blank_Result);
            Retained_Results : T.Result_Array (1 .. P.Count (Retained_Count)) :=
              (others => Blank_Result);
            History : H.History (1 .. H.Byte_Count (History_Count)) :=
              (others => Blank_History);
            Required : Roster.Check_Array (1 .. P.Count (Required_Count)) :=
              (others => Blank_Required);
            Classified : Raw_Roster.Classification;
            Retained : constant T.Optional_Terminal :=
              (if R.Retained_Present = 0 then (Present => False)
               else (True, Convert (R.Retained)));
            Reason : T.Decision;
            Selected : P.Count;
            Response : Result := (Reason => 0, Selected => 0,
              Summary_Present => 0, Summary =>
                (Subject | Content | Requirement | Run | Sequence => (0, (1, 0)),
                 State | Outcome => 0), Execution_State => 0, Outcome => 0, Promotion => 0);
         begin
            Copy_Data (Input.Data, Data_Length, A);
            for I in J'Range loop
               declare
                  X : Journal_Row;
               begin
                  Read_Journal
                    (Input.Journal.all (I64 (I)), X);
                  if not Valid (X.Bound) or else not Valid (X.Previous) or else X.Linked > 1
                  then return 255; end if;
                  J (I) := (Base =>
                    (Convert (X.Bound.Store_Id), Convert (X.Bound.Subject),
                     Convert (X.Bound.Content), Convert (X.Bound.Run),
                     Convert (X.Bound.Sequence), Previous (X.Previous),
                     (if X.Linked = 0 then P.Reserved else P.Linked)),
                    Requirement => Convert (X.Bound.Requirement));
               end;
            end loop;
            for I in Captured'Range loop
               declare
                  X : Check_Row;
                  Wire : W.Raw_Record;
                  Confined : P.Byte;
               begin
                  Read_Check
                    (Input.Captured.all (I64 (I)), X);
                  if not Valid (X) then return 255; end if;
                  Captured (I) := Convert (X);
                  Read_Raw
                    (Raw.Rows.all (I64 (I)), Wire);
                  Read_Octet (Raw.Confinements.all (I), Confined);
                  if not W.Well_Formed (Wire)
                    or else Confined > W.E.Confinement_Observation'Pos (W.E.Confinement_Observation'Last)
                  then return 255; end if;
                  Measures (I) := (Captured (I), Wire, Confined,
                    T.Captured_Bytes (Convert (X.Declared)));
               end;
            end loop;
            for I in Retained_Results'Range loop
               declare
                  X : Check_Row;
               begin
                  Read_Check
                    (Input.Retained.all (I64 (I)), X);
                  if not Valid (X) then return 255; end if;
                  Retained_Results (I) := Convert (X);
               end;
            end loop;
            for I in History'Range loop
               declare
                  X : History_Row;
               begin
                  Read_History
                    (Input.History.all (I64 (I)), X);
                  if not Valid (X) then return 255; end if;
                  History (I) := Convert (X);
               end;
            end loop;
            for I in Required'Range loop
               declare
                  X : Required_Row;
               begin
                  Read_Required
                    (Input.Required.all (I64 (I)), X);
                  if not Valid (X.Check_Id) or else not Valid (X.Declared) then return 255; end if;
                  Required (I) := (T.Check_Identity (Convert (X.Check_Id)), T.Captured_Bytes (Convert (X.Declared)));
               end;
            end loop;
            if R.Operation /= 1 then
               Reason := Worldline.Evaluation_Authority.Decide_Envelope
                 (A, J, Convert (R.Current), Convert (R.Captured),
                                   Captured, Retained, Retained_Results);
            else
               T.Apply (A, J, Convert (R.Current), Convert (R.Captured), Captured,
                        Retained, Retained_Results, History, Reason);
            end if;
            Response.Reason := U32 (T.Decision'Pos (Reason));
            if Reason in T.Retain_Terminal | T.Already_Retained then
               Selected := T.Find_Run (A, J, T.Run_Identity (Convert (R.Captured.Bound.Run)));
               Response.Selected := I64 (Selected);
               if R.Operation = 2 then
                  -- Malformed spans and inconsistent bindings are refused
                  -- before any False failure predicate can be mistaken for PASS.
                  if not T.Valid_Binding (A, Convert (R.Captured.Bound))
                    or else not T.Same_Binding (A, Convert (R.Captured.Bound), Convert (R.Observed_Binding))
                    or else not P.Valid (A, Convert (R.Before_Root))
                    or else not P.Valid (A, Convert (R.After_Root))
                    or else not P.Valid (A, Convert (R.Completion.Check_Id))
                    or else not P.Valid (A, Convert (R.Completion.Declared))
                    or else (for some M in Measures'Range =>
                      not Raw_Roster.Row_Bound (A, Measures (M), Convert (R.Captured.Bound)))
                    or else (for some Q in Required'Range =>
                      not P.Valid (A, T.Span (Required (Q).Check))
                      or else not P.Valid (A, T.Span (Required (Q).Declared)))
                  then return 255; end if;
                  Classified := Raw_Roster.Classify (A, Convert (R.Captured.Bound),
                    Measures, Required, Roster.Declaration'Val (R.Policy),
                    (Convert (R.Observed_Binding), T.Captured_Bytes (Convert (R.Before_Root)),
                     T.Captured_Bytes (Convert (R.After_Root))),
                    (T.Check_Identity (Convert (R.Completion.Check_Id)),
                     T.Captured_Bytes (Convert (R.Completion.Declared))));
                  Response.Execution_State := U32 (W.E.Execution_State'Pos (Classified.State));
                  Response.Outcome := U32 (W.E.Outcome'Pos (Classified.Outcome));
                  Response.Promotion := Boolean'Pos (Classified.Promotion_Ready);
               end if;
               if R.Operation = 1 then
                  Response.Summary_Present := 1;
                  Response.Summary := Export_Row (History (H.Byte_Index (Selected)));
               end if;
            end if;
            Observed := Response;
            if Have_Output then
               Write_Result (Response, Observed);
            end if;
            return 0;
         end;
         end;
      end;
   exception
      when others => return 255;
   end Raw_Decide_Common;

   function Raw_Decide
     (Input : Request_View; Raw : Raw_View; Output : System.Address;
      Observed : in out Result) return Interfaces.C.int is
      Status : Interfaces.C.int;
   begin
      Status := Raw_Decide_Common
        (Input, Raw, Output, True, Observed);
      return Status;
   end Raw_Decide;

   function Raw_Decide_Observed
     (Input : Request_View; Raw : Raw_View;
      Observed : in out Result) return Interfaces.C.int is
      Status : Interfaces.C.int;
   begin
      Status := Raw_Decide_Common
        (Input, Raw, System.Null_Address, False, Observed);
      return Status;
   end Raw_Decide_Observed;

   Zero_Row_Fields : constant Row_Fields := (others => Zero_Optional);
   Zero_Context_Fields : constant Context_Fields := (others => Zero_Optional);
   Zero_Context_Row : constant Context_Row :=
     (Item => Zero_Check,
      Expected => Zero_Row_Fields,
      Observed => Zero_Row_Fields);
   Zero_Hash : constant Worldline.Collapse_Wire.Raw_Optional_Hash :=
     (Present => 0, Value => (others => 0));
   Zero_Counter : constant Worldline.Collapse_Wire.Raw_Optional_Counter :=
     (Present => 0, Value_LE => (others => 0));
   Zero_Projection : constant Worldline.Collapse_Wire.Raw_Request :=
     (Candidate_State | Phase | Evaluation_Mode | Conflicts | Foreign_Writes
        | Roster_Complete | Staged_Roster_Complete => 0,
      Expected_Parent | Candidate_Parent | Expected_Subject | Evidence_Subject
        | Expected_Base | Candidate_Base | Expected_Delta | Candidate_Delta
        | Expected_Root_Set | Candidate_Root_Set | Expected_Staged_Root
        | Actual_Staged_Root | Staged_Content_Root | Tested_Root
        | Current_Requirement | Resulting_Requirement | Evaluated_Requirement
        | Declared_Verifiers | Executed_Verifiers
        | Staged_Evaluated_Requirement | Staged_Executed_Verifiers
        | Staged_Examined_Root | Expected_Checkpoint | Witnessed_Checkpoint
        | Registered_Watch_Set | Watched_Set => Zero_Hash,
      Generation_Before | Generation_After => Zero_Counter);
   Zero_Context : constant Context_Input :=
     (Version => 0, Data => System.Null_Address, Data_Length => 0,
      Expected_Binding => Zero_Binding,
      Expected_Current => Zero_Cursor,
      Prepared_Current => Zero_Cursor,
      Expected => Zero_Context_Fields,
      Observed => Zero_Context_Fields,
      Rows => System.Null_Address, Row_Count => 0,
      Required => System.Null_Address, Required_Count => 0,
      Policy => 0, Projection => Zero_Projection,
      Agent => W.Zero_Record, Agent_Confinement => 0);
   function Layout_Context_Input (Field : U32) return I64 is
      Units : constant I64 := Context_Input'Object_Size / System.Storage_Unit;
   begin
      pragma Compile_Time_Error (Zero_Context.Version'Position /= 0, "Context.Version");
      pragma Compile_Time_Error (Zero_Context.Data'Position /= 8, "Context.Data");
      pragma Compile_Time_Error (Zero_Context.Data_Length'Position /= 16, "Context.Data_Length");
      pragma Compile_Time_Error (Zero_Context.Expected_Binding'Position /= 24, "Context.Expected_Binding");
      pragma Compile_Time_Error (Zero_Context.Expected_Current'Position /= 128, "Context.Expected_Current");
      pragma Compile_Time_Error (Zero_Context.Prepared_Current'Position /= 168, "Context.Prepared_Current");
      pragma Compile_Time_Error (Zero_Context.Expected'Position /= 208, "Context.Expected");
      pragma Compile_Time_Error (Zero_Context.Observed'Position /= 544, "Context.Observed");
      pragma Compile_Time_Error (Zero_Context.Rows'Position /= 880, "Context.Rows");
      pragma Compile_Time_Error (Zero_Context.Row_Count'Position /= 888, "Context.Row_Count");
      pragma Compile_Time_Error (Zero_Context.Required'Position /= 896, "Context.Required");
      pragma Compile_Time_Error (Zero_Context.Required_Count'Position /= 904, "Context.Required_Count");
      pragma Compile_Time_Error (Zero_Context.Policy'Position /= 912, "Context.Policy");
      pragma Compile_Time_Error (Zero_Context.Projection'Position /= 916, "Context.Projection");
      pragma Compile_Time_Error (Zero_Context.Agent'Position /= 1799, "Context.Agent");
      pragma Compile_Time_Error (Zero_Context.Agent_Confinement'Position /= 1833, "Context.Agent_Confinement");
      return (case Field is
        when 0 => Units, when 1 => Context_Input'Alignment,
        when 2 => 0, when 3 => 8, when 4 => 16, when 5 => 24, when 6 => 128,
        when 7 => 168, when 8 => 208, when 9 => 544, when 10 => 880,
        when 11 => 888, when 12 => 896, when 13 => 904, when 14 => 912,
        when 15 => 916, when 16 => 1799, when 17 => 1833, when others => I64'Last);
   end Layout_Context_Input;
   function Layout_Context_Row (Field : U32) return I64 is
      Units : constant I64 := Context_Row'Object_Size / System.Storage_Unit;
   begin
      pragma Compile_Time_Error (Zero_Context_Row.Item'Position /= 0, "Context_Row.Item");
      pragma Compile_Time_Error (Zero_Context_Row.Expected'Position /= 304, "Context_Row.Expected");
      pragma Compile_Time_Error (Zero_Context_Row.Observed'Position /= 496, "Context_Row.Observed");
      return (case Field is
        when 0 => Units, when 1 => Context_Row'Alignment,
        when 2 => 0, when 3 => 304, when 4 => 496, when others => I64'Last);
   end Layout_Context_Row;
   function Context_Layout (Kind, Field : U32) return I64 is
     (case Kind is
        when 1 => Layout_Context_Input (Field),
        when 2 => Layout_Context_Row (Field),
        when others => I64'Last);

   function Context_Matches
     (Input : Request_View; Context : Context_View; Evidence : Evidence_View;
      Agent_Confinement : Interfaces.Unsigned_8) return Interfaces.C.int is
      package CA renames Worldline.Evaluation_Authority;
      package CW renames Worldline.Collapse_Wire;
      use type W.Raw_Record;
      CS : constant I64 := Context_Input'Object_Size / System.Storage_Unit;
      RS : constant I64 := Context_Row'Object_Size / System.Storage_Unit;
      ISz : constant I64 := Check_Row'Object_Size / System.Storage_Unit;
      QS : constant I64 := Required_Row'Object_Size / System.Storage_Unit;
      function Convert_Optional (X : Optional_Span) return CA.Optional_Bytes
        with Pre => Valid (X)
      is
      begin
         if X.Present = 0 then
            return (Present => False);
         else
            return (True, Convert (X.Value));
         end if;
      end Convert_Optional;
      procedure Read_Context (Value : Context_View; Item : out Context_Input) is
      begin
         Item := Value.Descriptor;
      end Read_Context;
      procedure Read_Context_Row (Value : Context_Row; Item : out Context_Row) is
      begin
         Item := Value;
      end Read_Context_Row;
      procedure Read_Collapse (Value : CW.Raw_Request; Item : out CW.Raw_Request) is
      begin
         Item := Value;
      end Read_Collapse;
   begin
      if not (Fits (Input.Data, Input.Descriptor.Data_Length)
        and then Fits (Input.Captured, Input.Descriptor.Captured_Count)
        and then Fits (Input.Required, Input.Descriptor.Required_Count)
        and then Fits (Context.Data, Context.Descriptor.Data_Length)
        and then Fits (Context.Rows, Context.Descriptor.Row_Count)
        and then Fits (Context.Required, Context.Descriptor.Required_Count)) then return 255; end if;
      Diagnostic_Mark ("completion.context.enter");
      if not Extent_Valid (Input.Address, Request'Object_Size / System.Storage_Unit, Request'Alignment)
        or else not Extent_Valid (Context.Address, CS, Context_Input'Alignment)
        or else not Extent_Valid (Evidence.Collapse_Address, CW.Raw_Request'Object_Size / System.Storage_Unit, CW.Raw_Request'Alignment)
        or else not Extent_Valid (Evidence.Agent_Address, W.Raw_Record'Object_Size / System.Storage_Unit, W.Raw_Record'Alignment)
      then
         Diagnostic_Mark ("completion.context.input-extents-rejected");
         return 255;
      end if;
      declare
         Held_R : Request;
         Held_X : Context_Input;
         Held_Collapse : CW.Raw_Request;
         Held_Agent : W.Raw_Record;
      begin
         Read_Request (Input, Held_R);
         Read_Context (Context, Held_X);
         Read_Collapse (Evidence.Collapse, Held_Collapse);
         Read_Raw (Evidence.Agent, Held_Agent);
         declare
            R : constant Request := Held_R;
            X : constant Context_Input := Held_X;
            Raw_Collapse : constant CW.Raw_Request := Held_Collapse;
            Raw_Agent : constant W.Raw_Record := Held_Agent;
            Data_Length : constant I64 := R.Data_Length;
            Context_Length : constant I64 := X.Data_Length;
            Captured_Count : constant I64 := R.Captured_Count;
            Required_Count : constant I64 := R.Required_Count;
            Row_Count : constant I64 := X.Row_Count;
            X_Required_Count : constant I64 := X.Required_Count;
         begin
         if X.Version /= 1 or else R.Version /= 1 or else R.Operation /= 2
           or else Data_Length < 0 or else Context_Length < 0
           or else Captured_Count < 0 or else Required_Count < 0
           or else Row_Count < 0 or else X_Required_Count < 0
           or else not Extent_Valid (X.Data, Context_Length, P.Byte'Alignment)
           or else Row_Count /= Captured_Count
           or else X_Required_Count /= Required_Count
           or else X.Policy > U32 (Roster.Declaration'Pos (Roster.Declaration'Last))
           or else R.Policy > U32 (Roster.Declaration'Pos (Roster.Declaration'Last))
           or else not Valid (R.Before_Root) or else not Valid (R.After_Root)
           or else not Valid (R.Captured) or else not Valid (R.Current)
           or else not Valid (X.Expected_Binding) or else not Valid (X.Expected_Current)
           or else not Valid (X.Prepared_Current)
           or else not Extent_Valid (R.Data, Data_Length, P.Byte'Alignment)
           or else not Array_Valid (X.Rows, Row_Count, RS, Context_Row'Alignment, Context.Address, CS)
           or else not Array_Valid (R.Captured_Results, Captured_Count, ISz, Check_Row'Alignment, Context.Address, CS)
           or else not Array_Valid (R.Required, Required_Count, QS, Required_Row'Alignment, Context.Address, CS)
           or else not Array_Valid (X.Required, X_Required_Count, QS, Required_Row'Alignment, Context.Address, CS)
           or else X.Agent /= Raw_Agent or else X.Agent_Confinement /= Agent_Confinement
         then
            Diagnostic_Mark ("completion.context.transport-guard-rejected");
            return 255;
         end if;
         Diagnostic_Mark ("completion.context.copy-arenas");
         declare
            Data : P.Bytes (1 .. P.Count (Data_Length));
            Context_Data : P.Bytes (1 .. P.Count (Context_Length));
            Expected, Observed : CA.Context_Fields := (others => (Present => False));
            Rows : T.Result_Array (1 .. P.Count (Captured_Count)) :=
              (others => Blank_Result);
            Joined : CA.Context_Rows (Rows'Range) := (others => Blank_Joined);
            Required, Expected_Required :
              Roster.Check_Array (1 .. P.Count (Required_Count)) :=
                (others => Blank_Required);
         begin
            Copy_Data (Input.Data, Data_Length, Data);
            Copy_Data (Context.Data, Context_Length, Context_Data);
            Diagnostic_Mark ("completion.context.arenas-copied");
            for K in CA.Context_Field loop
               if not Valid (X.Expected (K)) or else not Valid (X.Observed (K))
               then
                  Diagnostic_Value
                    ("completion.context.field-rejected", I64 (CA.Context_Field'Pos (K)));
                  return 255;
               end if;
               Expected (K) := Convert_Optional (X.Expected (K));
               Observed (K) := Convert_Optional (X.Observed (K));
            end loop;
            for I in Rows'Range loop
               declare
                  Original : Check_Row;
                  Owned : Context_Row;
               begin
                  Read_Check
                    (Input.Captured.all (I64 (I)), Original);
                  Read_Context_Row
                    (Context.Rows.all (I64 (I)), Owned);
                  if not Valid (Original) or else not Valid (Owned.Item) then
                     Diagnostic_Value ("completion.context.row-rejected", I64 (I));
                     return 255;
                  end if;
                  Rows (I) := Convert (Original);
                  Joined (I).Item := Convert (Owned.Item);
                  Joined (I).Declared := T.Captured_Bytes (Convert (Owned.Item.Declared));
                  Joined (I).Actual_Declared := T.Captured_Bytes (Convert (Original.Declared));
                  for Field in CA.Row_Field loop
                     if not Valid (Owned.Expected (Field)) or else not Valid (Owned.Observed (Field)) then
                        Diagnostic_Value ("completion.context.row-field-row", I64 (I));
                        Diagnostic_Value
                          ("completion.context.row-field-rejected", I64 (CA.Row_Field'Pos (Field)));
                        return 255;
                     end if;
                     Joined (I).Expected (Field) := Convert_Optional (Owned.Expected (Field));
                     Joined (I).Observed (Field) := Convert_Optional (Owned.Observed (Field));
                  end loop;
               end;
            end loop;
            for I in Required'Range loop
               declare
                  Original, Owned : Required_Row;
               begin
                  Read_Required
                    (Input.Required.all (I64 (I)), Original);
                  Read_Required
                    (Context.Required.all (I64 (I)), Owned);
                  if not Valid (Original.Check_Id) or else not Valid (Original.Declared)
                    or else not Valid (Owned.Check_Id) or else not Valid (Owned.Declared)
                  then
                     Diagnostic_Value ("completion.context.required-rejected", I64 (I));
                     return 255;
                  end if;
                  Required (I) := (T.Check_Identity (Convert (Original.Check_Id)), T.Captured_Bytes (Convert (Original.Declared)));
                  Expected_Required (I) := (T.Check_Identity (Convert (Owned.Check_Id)), T.Captured_Bytes (Convert (Owned.Declared)));
               end;
            end loop;
            Diagnostic_Mark ("completion.context.join");
            declare
               Joined_Context : constant Boolean := CA.Join_Context
              (Data, Context_Data, Convert (R.Captured), Convert (R.Current),
               Convert (X.Expected_Binding), Convert (X.Expected_Current), Convert (X.Prepared_Current),
               Expected, Observed, Convert (R.Before_Root), Convert (R.After_Root),
               Roster.Declaration'Val (R.Policy), Roster.Declaration'Val (X.Policy),
               Rows, Joined, Required, Expected_Required,
               Raw_Collapse, X.Projection);
            begin
               Diagnostic_Value
                 ("completion.context.join-result", Boolean'Pos (Joined_Context));
               return (if Joined_Context then 1 else 0);
            end;
         end;
         end;
      end;
   exception
      when others =>
         declare
            Handler_Diagnostic_Enabled : Boolean := False;
         begin
            Handler_Diagnostic_Enabled := Diagnostic_Enabled;
            if Handler_Diagnostic_Enabled then
               begin
                  Diagnostic_Exception
                    ("completion.context",
                     GNAT.Current_Exception.Exception_Information);
               exception
                  when others => Diagnostic_Capture_Failed;
               end;
            end if;
         end;
         return 255;
   end Context_Matches;

   Zero_Row_Meta : constant Row_Metadata :=
     (Check_Id => Zero_Span, Source_Id => Zero_Span, Payload => Zero_Span,
      Execution => Zero_Optional, Verifier => Zero_Optional);
   Zero_Metadata : constant Metadata_Context :=
     (Version => 0, Base => System.Null_Address, Data => System.Null_Address,
      Data_Length => 0, Rows => System.Null_Address, Row_Count => 0);
   function Layout_Metadata_Context (Field : U32) return I64 is
      Units : constant I64 := Metadata_Context'Object_Size / System.Storage_Unit;
   begin
      pragma Compile_Time_Error (Zero_Metadata.Version'Position /= 0, "Metadata.Version");
      pragma Compile_Time_Error (Zero_Metadata.Base'Position /= 8, "Metadata.Base");
      pragma Compile_Time_Error (Zero_Metadata.Data'Position /= 16, "Metadata.Data");
      pragma Compile_Time_Error (Zero_Metadata.Data_Length'Position /= 24, "Metadata.Data_Length");
      pragma Compile_Time_Error (Zero_Metadata.Rows'Position /= 32, "Metadata.Rows");
      pragma Compile_Time_Error (Zero_Metadata.Row_Count'Position /= 40, "Metadata.Row_Count");
      return (case Field is
        when 0 => Units, when 1 => Metadata_Context'Alignment,
        when 2 => 0, when 3 => 8, when 4 => 16, when 5 => 24,
        when 6 => 32, when 7 => 40, when others => I64'Last);
   end Layout_Metadata_Context;
   function Layout_Row_Metadata (Field : U32) return I64 is
      Units : constant I64 := Row_Metadata'Object_Size / System.Storage_Unit;
   begin
      pragma Compile_Time_Error (Zero_Row_Meta.Check_Id'Position /= 0, "Row_Meta.Check");
      pragma Compile_Time_Error (Zero_Row_Meta.Source_Id'Position /= 16, "Row_Meta.Source");
      pragma Compile_Time_Error (Zero_Row_Meta.Payload'Position /= 32, "Row_Meta.Payload");
      pragma Compile_Time_Error (Zero_Row_Meta.Execution'Position /= 48, "Row_Meta.Execution");
      pragma Compile_Time_Error (Zero_Row_Meta.Verifier'Position /= 72, "Row_Meta.Verifier");
      return (case Field is
        when 0 => Units, when 1 => Row_Metadata'Alignment,
        when 2 => 0, when 3 => 16, when 4 => 32, when 5 => 48,
        when 6 => 72, when others => I64'Last);
   end Layout_Row_Metadata;
   function Metadata_Layout (Kind, Field : U32) return I64 is
     (case Kind is
        when 1 => Layout_Metadata_Context (Field),
        when 2 => Layout_Row_Metadata (Field),
        when others => I64'Last);

   function Metadata_Base (Context : Metadata_View) return System.Address is
      procedure Read_Metadata (Value : Metadata_View; Item : out Metadata_Context) is
      begin
         Item := Value.Descriptor;
      end Read_Metadata;
   begin
      if not Extent_Valid (Context.Address, Metadata_Context'Object_Size / System.Storage_Unit,
                           Metadata_Context'Alignment)
      then return System.Null_Address; end if;
      declare
         Held : Metadata_Context;
      begin
         Read_Metadata (Context, Held);
         declare
            X : constant Metadata_Context := Held;
         begin
            if X.Version /= 1 or else not Extent_Valid
              (X.Base, Context_Input'Object_Size / System.Storage_Unit, Context_Input'Alignment)
            then return System.Null_Address; end if;
            return X.Base;
         end;
      end;
   exception when others => return System.Null_Address;
   end Metadata_Base;

   function Metadata_Matches (Input : Request_View; Context : Metadata_View)
      return Interfaces.C.int is
      package CA renames Worldline.Evaluation_Authority;
      CS : constant I64 := Metadata_Context'Object_Size / System.Storage_Unit;
      RS : constant I64 := Row_Metadata'Object_Size / System.Storage_Unit;
      ISz : constant I64 := Check_Row'Object_Size / System.Storage_Unit;
      function Optional (X : Optional_Span) return CA.Optional_Bytes
        with Pre => Valid (X)
      is
      begin
         if X.Present = 0 then
            return (Present => False);
         else
            return (Present => True, Value => Convert (X.Value));
         end if;
      end Optional;
      procedure Read_Metadata (Value : Metadata_View; Item : out Metadata_Context) is
      begin
         Item := Value.Descriptor;
      end Read_Metadata;
      procedure Read_Metadata_Row (Value : Row_Metadata; Item : out Row_Metadata) is
      begin
         Item := Value;
      end Read_Metadata_Row;
   begin
      if not (Fits (Input.Data, Input.Descriptor.Data_Length)
        and then Fits (Input.Captured, Input.Descriptor.Captured_Count)
        and then Fits (Context.Data, Context.Descriptor.Data_Length)
        and then Fits (Context.Rows, Context.Descriptor.Row_Count)) then return 255; end if;
      Diagnostic_Mark ("completion.metadata.enter");
      if not Extent_Valid (Input.Address, Request'Object_Size / System.Storage_Unit, Request'Alignment)
        or else not Extent_Valid (Context.Address, CS, Metadata_Context'Alignment)
      then
         Diagnostic_Mark ("completion.metadata.input-extents-rejected");
         return 255;
      end if;
      declare
         Held_R : Request;
         Held_X : Metadata_Context;
      begin
         Read_Request (Input, Held_R);
         Read_Metadata (Context, Held_X);
         declare
            R : constant Request := Held_R;
            X : constant Metadata_Context := Held_X;
            Data_Length : constant I64 := R.Data_Length;
            Projected_Length : constant I64 := X.Data_Length;
            Captured_Count : constant I64 := R.Captured_Count;
            Row_Count : constant I64 := X.Row_Count;
         begin
         if X.Version /= 1 or else R.Version /= 1 or else R.Operation > 2
           or else Data_Length < 0 or else Projected_Length < 0
           or else Captured_Count < 0 or else Row_Count < 0
           or else Row_Count /= Captured_Count
           or else not Extent_Valid (X.Data, Projected_Length, P.Byte'Alignment)
           or else not Extent_Valid (R.Data, Data_Length, P.Byte'Alignment)
           or else not Array_Valid (X.Rows, Row_Count, RS, Row_Metadata'Alignment, Context.Address, CS)
           or else not Array_Valid (R.Captured_Results, Captured_Count, ISz,
                                   Check_Row'Alignment, Context.Address, CS)
         then
            Diagnostic_Mark ("completion.metadata.transport-guard-rejected");
            return 255;
         end if;
         Diagnostic_Mark ("completion.metadata.copy-arenas");
         declare
            Data : P.Bytes (1 .. P.Count (Data_Length));
            Projected_Data : P.Bytes (1 .. P.Count (Projected_Length));
            Rows : T.Result_Array (1 .. P.Count (Captured_Count)) :=
              (others => Blank_Result);
            Projected : CA.Row_Metadata_Array (Rows'Range) := (others => Blank_Meta);
         begin
            Copy_Data (Input.Data, Data_Length, Data);
            Copy_Data (Context.Data, Projected_Length, Projected_Data);
            Diagnostic_Mark ("completion.metadata.arenas-copied");
            for I in Rows'Range loop
               declare
                  Original : Check_Row;
                  Owned : Row_Metadata;
               begin
                  Read_Check
                    (Input.Captured.all (I64 (I)), Original);
                  Read_Metadata_Row
                    (Context.Rows.all (I64 (I)), Owned);
                  if not Valid (Original) or else not Valid (Owned.Check_Id)
                    or else not Valid (Owned.Source_Id) or else not Valid (Owned.Payload)
                    or else not Valid (Owned.Execution) or else not Valid (Owned.Verifier)
                  then
                     Diagnostic_Value ("completion.metadata.row-rejected", I64 (I));
                     return 255;
                  end if;
                  Rows (I) := Convert (Original);
                  Projected (I) := (Check => Convert (Owned.Check_Id),
                    Source => Convert (Owned.Source_Id), Payload => Convert (Owned.Payload),
                    Execution => Optional (Owned.Execution), Verifier => Optional (Owned.Verifier));
               end;
            end loop;
            Diagnostic_Mark ("completion.metadata.join");
            declare
               Joined_Metadata : constant Boolean :=
                 CA.Join_Metadata (Data, Projected_Data, Rows, Projected);
            begin
               Diagnostic_Value
                 ("completion.metadata.join-result", Boolean'Pos (Joined_Metadata));
               return (if Joined_Metadata then 1 else 0);
            end;
         end;
         end;
      end;
   exception
      when others =>
         declare
            Handler_Diagnostic_Enabled : Boolean := False;
         begin
            Handler_Diagnostic_Enabled := Diagnostic_Enabled;
            if Handler_Diagnostic_Enabled then
               begin
                  Diagnostic_Exception
                    ("completion.metadata",
                     GNAT.Current_Exception.Exception_Information);
               exception
                  when others => Diagnostic_Capture_Failed;
               end;
            end if;
         end;
         return 255;
   end Metadata_Matches;


   function Context_Matches_Projected
     (Input : Request_View;
      Projected_Rows : Check_Row_Array;
      Projected_Plans : Required_Row_Array;
      Context : Context_View; Evidence : Evidence_View;
      Agent_Confinement : Interfaces.Unsigned_8) return Interfaces.C.int is
      R : constant Request := Input.Descriptor;
      package CA renames Worldline.Evaluation_Authority;
      package CW renames Worldline.Collapse_Wire;
      use type W.Raw_Record;
      CS : constant I64 := Context_Input'Object_Size / System.Storage_Unit;
      RS : constant I64 := Context_Row'Object_Size / System.Storage_Unit;
      QS : constant I64 := Required_Row'Object_Size / System.Storage_Unit;
      function Convert_Optional (X : Optional_Span) return CA.Optional_Bytes
        with Pre => Valid (X)
      is
      begin
         if X.Present = 0 then
            return (Present => False);
         else
            return (True, Convert (X.Value));
         end if;
      end Convert_Optional;
      procedure Read_Context (Value : Context_View; Item : out Context_Input) is
      begin
         Item := Value.Descriptor;
      end Read_Context;
      procedure Read_Context_Row (Value : Context_Row; Item : out Context_Row) is
      begin
         Item := Value;
      end Read_Context_Row;
      procedure Read_Collapse (Value : CW.Raw_Request; Item : out CW.Raw_Request) is
      begin
         Item := Value;
      end Read_Collapse;
   begin
      if not (Fits (Input.Data, Input.Descriptor.Data_Length)
        and then Fits (Context.Data, Context.Descriptor.Data_Length)
        and then Fits (Context.Rows, Context.Descriptor.Row_Count)
        and then Fits (Context.Required, Context.Descriptor.Required_Count)) then return 255; end if;
      Diagnostic_Mark ("completion.context.enter");
      if not Rows_Fit (R.Captured_Count, Projected_Rows'First, Projected_Rows'Last)
        or else not Rows_Fit (R.Required_Count, Projected_Plans'First, Projected_Plans'Last)
        or else R.Data_Length < 0
        or else not Extent_Valid (Context.Address, CS, Context_Input'Alignment)
        or else not Extent_Valid (Evidence.Collapse_Address, CW.Raw_Request'Object_Size / System.Storage_Unit, CW.Raw_Request'Alignment)
        or else not Extent_Valid (Evidence.Agent_Address, W.Raw_Record'Object_Size / System.Storage_Unit, W.Raw_Record'Alignment)
      then
         Diagnostic_Mark ("completion.context.input-extents-rejected");
         return 255;
      end if;
      declare
         Held_X : Context_Input;
         Held_Collapse : CW.Raw_Request;
         Held_Agent : W.Raw_Record;
      begin
         Read_Context (Context, Held_X);
         Read_Collapse (Evidence.Collapse, Held_Collapse);
         Read_Raw (Evidence.Agent, Held_Agent);
         declare
            X : constant Context_Input := Held_X;
            Raw_Collapse : constant CW.Raw_Request := Held_Collapse;
            Raw_Agent : constant W.Raw_Record := Held_Agent;
            Context_Length : constant I64 := X.Data_Length;
            Row_Count : constant I64 := X.Row_Count;
            X_Required_Count : constant I64 := X.Required_Count;
         begin
         if X.Version /= 1 or else R.Version /= 1 or else R.Operation /= 2
           or else Context_Length < 0 or else Row_Count < 0 or else X_Required_Count < 0
           or else not Extent_Valid (X.Data, Context_Length, P.Byte'Alignment)
           or else Row_Count /= R.Captured_Count
           or else X_Required_Count /= R.Required_Count
           or else X.Policy > U32 (Roster.Declaration'Pos (Roster.Declaration'Last))
           or else R.Policy > U32 (Roster.Declaration'Pos (Roster.Declaration'Last))
           or else not Valid (R.Before_Root) or else not Valid (R.After_Root)
           or else not Valid (R.Captured) or else not Valid (R.Current)
           or else not Valid (X.Expected_Binding) or else not Valid (X.Expected_Current)
           or else not Valid (X.Prepared_Current)
           or else not Extent_Valid (R.Data, R.Data_Length, P.Byte'Alignment)
           or else not Array_Valid (X.Rows, Row_Count, RS, Context_Row'Alignment, Context.Address, CS)
           or else not Array_Valid (X.Required, X_Required_Count, QS, Required_Row'Alignment, Context.Address, CS)
           or else X.Agent /= Raw_Agent or else X.Agent_Confinement /= Agent_Confinement
         then
            Diagnostic_Mark ("completion.context.transport-guard-rejected");
            return 255;
         end if;
         Diagnostic_Mark ("completion.context.copy-arenas");
         declare
            Data : P.Bytes (1 .. P.Count (R.Data_Length));
            Context_Data : P.Bytes (1 .. P.Count (Context_Length));
            Expected, Observed : CA.Context_Fields := (others => (Present => False));
            Rows : T.Result_Array (1 .. P.Count (R.Captured_Count)) :=
              (others => Blank_Result);
            Joined : CA.Context_Rows (Rows'Range) := (others => Blank_Joined);
            Required, Expected_Required :
              Roster.Check_Array (1 .. P.Count (R.Required_Count)) :=
                (others => Blank_Required);
         begin
            Copy_Data (Input.Data, R.Data_Length, Data);
            Copy_Data (Context.Data, Context_Length, Context_Data);
            Diagnostic_Mark ("completion.context.arenas-copied");
            for K in CA.Context_Field loop
               if not Valid (X.Expected (K)) or else not Valid (X.Observed (K))
               then
                  Diagnostic_Value
                    ("completion.context.field-rejected", I64 (CA.Context_Field'Pos (K)));
                  return 255;
               end if;
               Expected (K) := Convert_Optional (X.Expected (K));
               Observed (K) := Convert_Optional (X.Observed (K));
            end loop;
            for I in Rows'Range loop
               declare
                  Original : constant Check_Row := Projected_Rows (I64 (I));
                  Owned : Context_Row;
               begin
                  Read_Context_Row
                    (Context.Rows.all (I64 (I)), Owned);
                  if not Valid (Original) or else not Valid (Owned.Item) then
                     Diagnostic_Value ("completion.context.row-rejected", I64 (I));
                     return 255;
                  end if;
                  Rows (I) := Convert (Original);
                  Joined (I).Item := Convert (Owned.Item);
                  Joined (I).Declared := T.Captured_Bytes (Convert (Owned.Item.Declared));
                  Joined (I).Actual_Declared := T.Captured_Bytes (Convert (Original.Declared));
                  for Field in CA.Row_Field loop
                     if not Valid (Owned.Expected (Field)) or else not Valid (Owned.Observed (Field)) then
                        Diagnostic_Value ("completion.context.row-field-row", I64 (I));
                        Diagnostic_Value
                          ("completion.context.row-field-rejected", I64 (CA.Row_Field'Pos (Field)));
                        return 255;
                     end if;
                     Joined (I).Expected (Field) := Convert_Optional (Owned.Expected (Field));
                     Joined (I).Observed (Field) := Convert_Optional (Owned.Observed (Field));
                  end loop;
               end;
            end loop;
            for I in Required'Range loop
               declare
                  Original : constant Required_Row := Projected_Plans (I64 (I));
                  Owned : Required_Row;
               begin
                  Read_Required
                    (Context.Required.all (I64 (I)), Owned);
                  if not Valid (Original.Check_Id) or else not Valid (Original.Declared)
                    or else not Valid (Owned.Check_Id) or else not Valid (Owned.Declared)
                  then
                     Diagnostic_Value ("completion.context.required-rejected", I64 (I));
                     return 255;
                  end if;
                  Required (I) := (T.Check_Identity (Convert (Original.Check_Id)),
                    T.Captured_Bytes (Convert (Original.Declared)));
                  Expected_Required (I) := (T.Check_Identity (Convert (Owned.Check_Id)),
                    T.Captured_Bytes (Convert (Owned.Declared)));
               end;
            end loop;
            Diagnostic_Mark ("completion.context.join");
            declare
               Joined_Context : constant Boolean := CA.Join_Context
                 (Data, Context_Data, Convert (R.Captured), Convert (R.Current),
                  Convert (X.Expected_Binding), Convert (X.Expected_Current), Convert (X.Prepared_Current),
                  Expected, Observed, Convert (R.Before_Root), Convert (R.After_Root),
                  Roster.Declaration'Val (R.Policy), Roster.Declaration'Val (X.Policy),
                  Rows, Joined, Required, Expected_Required,
                  Raw_Collapse, X.Projection);
            begin
               Diagnostic_Value
                 ("completion.context.join-result", Boolean'Pos (Joined_Context));
               return (if Joined_Context then 1 else 0);
            end;
         end;
         end;
      end;
   exception
      when others =>
         declare
            Handler_Diagnostic_Enabled : Boolean := False;
         begin
            Handler_Diagnostic_Enabled := Diagnostic_Enabled;
            if Handler_Diagnostic_Enabled then
               begin
                  Diagnostic_Exception
                    ("completion.context",
                     GNAT.Current_Exception.Exception_Information);
               exception
                  when others => Diagnostic_Capture_Failed;
               end;
            end if;
         end;
         return 255;
   end Context_Matches_Projected;

   function Metadata_Matches_Projected
     (Input : Request_View;
      Projected_Rows : Check_Row_Array;
      Context : Metadata_View) return Interfaces.C.int is
      R : constant Request := Input.Descriptor;
      package CA renames Worldline.Evaluation_Authority;
      CS : constant I64 := Metadata_Context'Object_Size / System.Storage_Unit;
      RS : constant I64 := Row_Metadata'Object_Size / System.Storage_Unit;
      function Optional (X : Optional_Span) return CA.Optional_Bytes
        with Pre => Valid (X)
      is
      begin
         if X.Present = 0 then
            return (Present => False);
         else
            return (Present => True, Value => Convert (X.Value));
         end if;
      end Optional;
      procedure Read_Metadata (Value : Metadata_View; Item : out Metadata_Context) is
      begin
         Item := Value.Descriptor;
      end Read_Metadata;
      procedure Read_Metadata_Row (Value : Row_Metadata; Item : out Row_Metadata) is
      begin
         Item := Value;
      end Read_Metadata_Row;
   begin
      if not (Fits (Input.Data, Input.Descriptor.Data_Length)
        and then Fits (Context.Data, Context.Descriptor.Data_Length)
        and then Fits (Context.Rows, Context.Descriptor.Row_Count)) then return 255; end if;
      Diagnostic_Mark ("completion.metadata.enter");
      if not Rows_Fit (R.Captured_Count, Projected_Rows'First, Projected_Rows'Last)
        or else R.Data_Length < 0
        or else not Extent_Valid (Context.Address, CS, Metadata_Context'Alignment)
      then
         Diagnostic_Mark ("completion.metadata.input-extents-rejected");
         return 255;
      end if;
      declare
         Held_X : Metadata_Context;
      begin
         Read_Metadata (Context, Held_X);
         declare
            X : constant Metadata_Context := Held_X;
            Projected_Length : constant I64 := X.Data_Length;
            Row_Count : constant I64 := X.Row_Count;
         begin
         if X.Version /= 1 or else R.Version /= 1 or else R.Operation > 2
           or else Projected_Length < 0 or else Row_Count < 0
           or else Row_Count /= R.Captured_Count
           or else not Extent_Valid (X.Data, Projected_Length, P.Byte'Alignment)
           or else not Extent_Valid (R.Data, R.Data_Length, P.Byte'Alignment)
           or else not Array_Valid (X.Rows, Row_Count, RS, Row_Metadata'Alignment, Context.Address, CS)
         then
            Diagnostic_Mark ("completion.metadata.transport-guard-rejected");
            return 255;
         end if;
         Diagnostic_Mark ("completion.metadata.copy-arenas");
         declare
            Data : P.Bytes (1 .. P.Count (R.Data_Length));
            Projected_Data : P.Bytes (1 .. P.Count (Projected_Length));
            Rows : T.Result_Array (1 .. P.Count (R.Captured_Count)) :=
              (others => Blank_Result);
            Projected : CA.Row_Metadata_Array (Rows'Range) := (others => Blank_Meta);
         begin
            Copy_Data (Input.Data, R.Data_Length, Data);
            Copy_Data (Context.Data, Projected_Length, Projected_Data);
            Diagnostic_Mark ("completion.metadata.arenas-copied");
            for I in Rows'Range loop
               declare
                  Original : constant Check_Row := Projected_Rows (I64 (I));
                  Owned : Row_Metadata;
               begin
                  Read_Metadata_Row
                    (Context.Rows.all (I64 (I)), Owned);
                  if not Valid (Original) or else not Valid (Owned.Check_Id)
                    or else not Valid (Owned.Source_Id) or else not Valid (Owned.Payload)
                    or else not Valid (Owned.Execution) or else not Valid (Owned.Verifier)
                  then
                     Diagnostic_Value ("completion.metadata.row-rejected", I64 (I));
                     return 255;
                  end if;
                  Rows (I) := Convert (Original);
                  Projected (I) := (Check => Convert (Owned.Check_Id),
                    Source => Convert (Owned.Source_Id), Payload => Convert (Owned.Payload),
                    Execution => Optional (Owned.Execution), Verifier => Optional (Owned.Verifier));
               end;
            end loop;
            Diagnostic_Mark ("completion.metadata.join");
            declare
               Joined_Metadata : constant Boolean :=
                 CA.Join_Metadata (Data, Projected_Data, Rows, Projected);
            begin
               Diagnostic_Value
                 ("completion.metadata.join-result", Boolean'Pos (Joined_Metadata));
               return (if Joined_Metadata then 1 else 0);
            end;
         end;
         end;
      end;
   exception
      when others =>
         declare
            Handler_Diagnostic_Enabled : Boolean := False;
         begin
            Handler_Diagnostic_Enabled := Diagnostic_Enabled;
            if Handler_Diagnostic_Enabled then
               begin
                  Diagnostic_Exception
                    ("completion.metadata",
                     GNAT.Current_Exception.Exception_Information);
               exception
                  when others => Diagnostic_Capture_Failed;
               end;
            end if;
         end;
         return 255;
   end Metadata_Matches_Projected;
end Evaluation_Completion_C;
