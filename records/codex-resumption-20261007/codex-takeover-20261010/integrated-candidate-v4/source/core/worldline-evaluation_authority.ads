with Worldline.Collapse;
with Worldline.Collapse_Wire;
with Evaluation_Completion;
with Evaluation_Completion_Roster;
with Worldline.Evaluation_Wire;
package Worldline.Evaluation_Authority with SPARK_Mode is
   package W renames Worldline.Evaluation_Wire;
   subtype Byte is W.Byte;
   use type Byte;
   function Report_Of (Raw : W.Raw_Record) return Byte
     with Global => null,
       Post => Report_Of'Result =
         (if not W.Well_Formed (Raw) then W.Invalid_Record else
          W.E.Report_Integrity'Pos (W.E.Expected_Report
            (W.Decode (Raw).Value.Report_Based,
             W.E.Expected_Classification (W.Decode (Raw).Value.Facts),
             W.Decode (Raw).Value.Report_Facts)));
   package C renames Worldline.Collapse_Wire;
   type Raw_Dependency is
     (No_Raw_Evidence, Primary_Only, Staged_Only, Primary_And_Staged,
      Invalid_Collapse);
   use type Worldline.Collapse.Evaluation_Mode;
   function Dependencies (Request : C.Raw_Request) return Raw_Dependency is
     (if not C.Well_Formed (Request) then Invalid_Collapse
      elsif C.Decode (Request).Mode = Worldline.Collapse.Checkpoint_Return then
        (if Worldline.Collapse.Primary_Covers (C.Decode (Request))
         then No_Raw_Evidence else Staged_Only)
      elsif Worldline.Collapse.Primary_Covers (C.Decode (Request))
      then Primary_Only else Primary_And_Staged) with Global => null;
   --  These are evidence dependencies only, never an authorization verdict.
   --  Checkpoint return with primary coverage has no raw evaluation/agent
   --  dependency; uncovered staged bytes still need the staged relation.
   function Needs_Primary (D : Raw_Dependency) return Boolean is
     (D in Primary_Only | Primary_And_Staged) with Global => null;
   function Needs_Staged (D : Raw_Dependency) return Boolean is
     (D in Staged_Only | Primary_And_Staged) with Global => null;
   function Needs_Agent (D : Raw_Dependency) return Boolean is
     (Needs_Primary (D) or else Needs_Staged (D)) with Global => null;
   --  A raw envelope validates owned identities, journal ancestry and replay
   --  bytes without treating a carried lifecycle/verdict as classification.
   --  Original records remain unchanged in Raw_Roster's promotion relation.
   package T renames Evaluation_Completion;
   use type T.Count;
   use type T.Decision;
   use type T.E.Execution_State;
   use type T.E.Outcome;
   function Structural_Result (R : T.Result_Record) return T.Result_Record is
     (R with delta State => T.E.Incomplete_Unknown, Outcome => T.E.No_Outcome)
     with Global => null;
   function Structural_Terminal (R : T.Terminal_Record) return T.Terminal_Record is
     (R with delta State => T.E.Incomplete_Unknown, Outcome => T.E.No_Outcome)
     with Global => null;
   function Structural_Optional (R : T.Optional_Terminal) return T.Optional_Terminal is
     (if R.Present then (Present => True, Value => Structural_Terminal (R.Value))
      else (Present => False)) with Global => null;
   function Structural_Results (Rows : T.Result_Array) return T.Result_Array is
     (T.Result_Array'(for I in Rows'Range => Structural_Result (Rows (I))))
     with Global => null;
   function Carried_Results_Equal (L, R : T.Result_Array) return Boolean is
     (L'Length = R'Length and then
      (for all I in L'Range =>
        L (I).State = R (R'First + (I - L'First)).State
        and then L (I).Outcome = R (R'First + (I - L'First)).Outcome))
     with Global => null;
   function Carried_Replay_Equal
     (Capture : T.Terminal_Record; Rows : T.Result_Array;
      Retained : T.Optional_Terminal; Retained_Rows : T.Result_Array) return Boolean is
     (Retained.Present and then Capture.State = Retained.Value.State
      and then Capture.Outcome = Retained.Value.Outcome
      and then Carried_Results_Equal (Rows, Retained_Rows)) with Global => null;
   function Envelope_Reference
     (A : T.Bytes; Journal : T.R.Journal; Current : T.Cursor;
      Capture : T.Terminal_Record; Rows : T.Result_Array;
      Retained : T.Optional_Terminal; Retained_Rows : T.Result_Array)
      return T.Decision is
     (if T.Reference (A, Journal, Current, Structural_Terminal (Capture),
           Structural_Results (Rows), Structural_Optional (Retained),
           Structural_Results (Retained_Rows)) = T.Already_Retained
        and then not Carried_Replay_Equal (Capture, Rows, Retained, Retained_Rows)
      then T.Terminal_Conflict
      else T.Reference (A, Journal, Current, Structural_Terminal (Capture),
           Structural_Results (Rows), Structural_Optional (Retained),
           Structural_Results (Retained_Rows))) with Global => null;
   function Decide_Envelope
     (A : T.Bytes; Journal : T.R.Journal; Current : T.Cursor;
      Capture : T.Terminal_Record; Rows : T.Result_Array;
      Retained : T.Optional_Terminal; Retained_Rows : T.Result_Array)
      return T.Decision with Global => null,
        Post => Decide_Envelope'Result = Envelope_Reference
          (A, Journal, Current, Capture, Rows, Retained, Retained_Rows);

   -- Complete owned context correspondence. The JSON/store producer must
   -- supply each named field from its stated independent source. Full bytes
   -- remain present; legacy digest projection is an additional checked slot,
   -- never a replacement for any identity or context field below.
   type Optional_Bytes (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : T.Span;
      end case;
   end record;
   type Context_Field is
     (Capture_Header, Returned_Context, Full_Policy, Candidate_Record,
      Root_Manifests, Effective_Roster, Declared_Verifiers,
      Executed_Verifiers, Agent_Record, Source_Id, Examined_Root,
      Invocation_Stream, Acquisition_Stream, Returned_Rows);
   type Context_Fields is array (Context_Field) of Optional_Bytes;
   type Row_Field is
     (Invocation_Start, Invocation_Return, Raw_Acquisitions,
      Invocation_Binding, Candidate_Snapshot, Invocation_Verifiers,
      Verifier_Members, Verifier_Identity);
   type Row_Fields is array (Row_Field) of Optional_Bytes;
   type Context_Row is record
      Item : T.Result_Record;
      Declared, Actual_Declared : T.Captured_Bytes;
      Expected, Observed : Row_Fields;
   end record;
   type Context_Rows is array (T.Index range <>) of Context_Row;
   package Roster renames Evaluation_Completion_Roster;
   function Equal_Optional (A : T.Bytes; L, R : Optional_Bytes) return Boolean is
     (L.Present = R.Present and then
        (not L.Present or else T.P.Same (A, L.Value, R.Value)))
     with Global => null;
   function Context_Valid (A : T.Bytes; F : Context_Fields) return Boolean is
     (for all K in Context_Field => F (K).Present
        and then T.P.Valid (A, F (K).Value)) with Global => null;
   function Context_Equal (A : T.Bytes; L, R : Context_Fields) return Boolean is
     (Context_Valid (A, L) and then Context_Valid (A, R)
      and then (for all K in Context_Field => Equal_Optional (A, L (K), R (K))))
     with Global => null;
   function Effective_Row
     (A : T.Bytes; Rows : T.Result_Array; Required : Roster.Check_Array;
      I : T.Count) return Boolean is
     (I in Rows'Range
      and then (for some K in Required'Range =>
        T.P.Same (A, T.Span (Required (K).Check), T.Span (Rows (I).Check)))
      and then (for all J in Rows'Range =>
        (if J > I then not T.P.Same
          (A, T.Span (Rows (J).Check), T.Span (Rows (I).Check)))))
     with Global => null;
   use type T.P.Byte;
   function Across
     (L_Data, R_Data : T.Bytes; L, R : T.Span) return Boolean is
     (T.P.Valid (L_Data, L) and then T.P.Valid (R_Data, R)
      and then L.Length = R.Length and then
        (for all I in T.Count range 0 .. L.Length - 1 =>
          L_Data (L.First + I) = R_Data (R.First + I))) with Global => null;
   function Epoch_Across
     (L_Data, R_Data : T.Bytes; L, R : T.Span) return Boolean is
     (T.P.Valid (L_Data, L) and then T.P.Valid (R_Data, R)
      and then (for all I in T.Count range 0 .. T.Count'Max (L.Length, R.Length) - 1 =>
        (if I < L.Length then L_Data (L.First + I) else 0) =
        (if I < R.Length then R_Data (R.First + I) else 0))) with Global => null;
   function Binding_Across
     (L_Data, R_Data : T.Bytes; L, R : T.Attempt_Binding) return Boolean is
     (T.Valid_Binding (L_Data, L) and then T.Valid_Binding (R_Data, R)
      and then Across (L_Data, R_Data, T.Span (L.Store), T.Span (R.Store))
      and then Across (L_Data, R_Data, T.Span (L.Subject), T.Span (R.Subject))
      and then Across (L_Data, R_Data, T.Span (L.Content), T.Span (R.Content))
      and then Across (L_Data, R_Data, T.Span (L.Run), T.Span (R.Run))
      and then Epoch_Across (L_Data, R_Data, T.Span (L.Sequence), T.Span (R.Sequence))
      and then L.Requirement.Present = R.Requirement.Present
      and then (not L.Requirement.Present or else Across
        (L_Data, R_Data, T.Span (L.Requirement.Value), T.Span (R.Requirement.Value))))
     with Global => null;
   function Cursor_Across
     (L_Data, R_Data : T.Bytes; Current : T.Cursor; Binding : T.Attempt_Binding)
      return Boolean is
     (Current.Present and then T.Valid_Cursor (L_Data, Current)
      and then T.Valid_Binding (R_Data, Binding)
      and then Across (L_Data, R_Data, T.Span (Current.Run), T.Span (Binding.Run))
      and then Epoch_Across (L_Data, R_Data,
        T.Span (Current.Sequence), T.Span (Binding.Sequence))) with Global => null;
   function Required_Equal
     (A, B : T.Bytes; L, R : Roster.Check_Array) return Boolean is
     (L'Length = R'Length and then (for all I in L'Range =>
       Across (A, B, T.Span (L (I).Check),
         T.Span (R (R'First + (I - L'First)).Check)) and then
       Across (A, B, T.Span (L (I).Declared),
         T.Span (R (R'First + (I - L'First)).Declared))))
     with Global => null;
   function Rows_Join
     (A, B : T.Bytes; Rows : T.Result_Array; Joined : Context_Rows;
      Required : Roster.Check_Array) return Boolean is
     (Rows'Length = Joined'Length and then
      (for all I in Rows'Range =>
        T.Same_Result (A, Rows (I), Joined (Joined'First + (I - Rows'First)).Item)
        and then T.P.Same (A, T.Span (Joined (Joined'First + (I - Rows'First)).Declared),
          T.Span (Joined (Joined'First + (I - Rows'First)).Actual_Declared))
        and then (for all K in Row_Field =>
          (if K not in Invocation_Verifiers | Verifier_Members | Verifier_Identity
                or else Effective_Row (A, Rows, Required, I)
           then Equal_Optional (B,
              Joined (Joined'First + (I - Rows'First)).Expected (K),
              Joined (Joined'First + (I - Rows'First)).Observed (K))))))
     with Global => null;
   function Without_Carried_Rosters (R : C.Raw_Request) return C.Raw_Request is
     (R with delta Roster_Complete => 0, Staged_Roster_Complete => 0)
     with Global => null;
   use type C.Raw_Request;
   use type Roster.Declaration;
   -- Projection is recomputed by the owned producer from the complete context,
   -- actual verifier members and existing legacy identity algorithms. Its
   -- correspondence with those algorithms remains an explicit body/producer
   -- obligation; it is not supplied as a success Boolean.
   function Context_Reference
     (A, B : T.Bytes; Capture : T.Terminal_Record; Current : T.Cursor;
      Expected_Binding : T.Attempt_Binding; Expected_Current, Prepared_Current : T.Cursor;
      Expected, Observed : Context_Fields; Before_Root, After_Root : T.Span;
      Policy, Expected_Policy : Roster.Declaration; Rows : T.Result_Array;
      Joined : Context_Rows; Required, Expected_Required : Roster.Check_Array;
      Request, Projection : C.Raw_Request) return Boolean is
     (Binding_Across (A, B, Capture.Binding, Expected_Binding)
      and then Cursor_Across (A, B, Current, Expected_Binding)
      and then T.Cursor_Matches (B, Expected_Current, Expected_Binding)
      and then T.Cursor_Matches (B, Prepared_Current, Expected_Binding)
      and then Context_Equal (B, Expected, Observed)
      and then Across (A, B, T.Span (Capture.Source), Expected (Source_Id).Value)
      and then Across (A, B, T.Span (Capture.Context), Expected (Returned_Context).Value)
      and then Across (A, B, Before_Root, Expected (Examined_Root).Value)
      and then Across (A, B, After_Root, Expected (Examined_Root).Value)
      and then Policy = Expected_Policy
      and then Required_Equal (A, B, Required, Expected_Required)
      and then Rows_Join (A, B, Rows, Joined, Required)
      and then C.Well_Formed (Request) and then C.Well_Formed (Projection)
      and then Without_Carried_Rosters (Request) = Without_Carried_Rosters (Projection))
     with Global => null;
   function Join_Context
     (A, B : T.Bytes; Capture : T.Terminal_Record; Current : T.Cursor;
      Expected_Binding : T.Attempt_Binding; Expected_Current, Prepared_Current : T.Cursor;
      Expected, Observed : Context_Fields; Before_Root, After_Root : T.Span;
      Policy, Expected_Policy : Roster.Declaration; Rows : T.Result_Array;
      Joined : Context_Rows; Required, Expected_Required : Roster.Check_Array;
      Request, Projection : C.Raw_Request) return Boolean
     with Global => null,
       Post => Join_Context'Result = Context_Reference
         (A, B, Capture, Current, Expected_Binding, Expected_Current, Prepared_Current,
          Expected, Observed, Before_Root, After_Root, Policy, Expected_Policy,
          Rows, Joined, Required, Expected_Required,
          Request, Projection);

   -- Independently decoded metadata belongs to a separate owned arena. It is
   -- never copied from Context_Row.Item or trusted as a success flag. All rows,
   -- including duplicates, nonrequired rows and incomplete observations, join.
   type Row_Metadata is record
      Check, Source, Payload : T.Span;
      Execution, Verifier : Optional_Bytes;
   end record;
   type Row_Metadata_Array is array (T.Index range <>) of Row_Metadata;
   function Row_Metadata_Reference
     (A, B : T.Bytes; Item : T.Result_Record; Projected : Row_Metadata)
      return Boolean is
     (Across (A, B, T.Span (Item.Check), Projected.Check)
      and then Across (A, B, T.Span (Item.Source), Projected.Source)
      and then Across (A, B, T.Span (Item.Payload), Projected.Payload)
      and then Item.Execution.Present = Projected.Execution.Present
      and then (not Item.Execution.Present or else Across
        (A, B, T.Span (Item.Execution.Value), Projected.Execution.Value))
      and then Item.Verifier.Present = Projected.Verifier.Present
      and then (not Item.Verifier.Present or else Across
        (A, B, T.Span (Item.Verifier.Value), Projected.Verifier.Value)))
     with Global => null;
   function Metadata_Reference
     (A, B : T.Bytes; Rows : T.Result_Array; Projected : Row_Metadata_Array)
      return Boolean is
     (Rows'Length = Projected'Length and then
      (for all I in Rows'Range => Row_Metadata_Reference
        (A, B, Rows (I), Projected (Projected'First + (I - Rows'First)))))
     with Global => null;
   function Join_Metadata
     (A, B : T.Bytes; Rows : T.Result_Array; Projected : Row_Metadata_Array)
      return Boolean with Global => null,
        Post => Join_Metadata'Result = Metadata_Reference (A, B, Rows, Projected);
   -- The default native v3 boundary requires this relation AND the unchanged
   -- Context_Reference through Join_Context. Legacy v1/v2 entry points alone
   -- do not establish the independent metadata-to-payload correspondence.
end Worldline.Evaluation_Authority;
