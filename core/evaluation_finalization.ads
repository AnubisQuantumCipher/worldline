with Canonical_Artifacts;
with Evaluation_Completion;
with Evaluation_Raw_Roster;
with Evaluation_History;
with Worldline.World;

--  Additive epoch-zero dependency. Stored observations do not authenticate
--  themselves. Durable pre-effect ordering, actual capture, canonical payload
--  projection, hash preimages, custody and default wiring are producer duties.
--  The original pending/revalidation APIs are not used or changed here.
package Evaluation_Finalization with SPARK_Mode is
   package T renames Evaluation_Completion;
   package P renames T.P;
   package H renames Evaluation_History;
   package R renames Evaluation_Raw_Roster;
   package W renames R.W;
   package E renames R.E;
   use type T.Count;
   use type P.Byte;
   use type P.Span;
   use type Worldline.Hash;
   use type W.Raw_Record;
   use type T.E.Execution_State;
   use type T.E.Outcome;
   use type E.Execution_State;
   use type E.Outcome;
   use type R.Classification;
   use type H.Optional_Record;
   use type H.Evaluation_Record;
   use type R.Measured_Result;
   use type R.Declaration;

   --  Content is deliberately absent, rather than empty or provisional.
   type Start_Record is record
      Store : T.Store_Identity;
      Subject : T.Subject_Identity;
      Run : T.Run_Identity;
      Sequence : T.Epoch;
      Requirement : T.Optional_Requirement;
      Policy, Verifier_Plan, Base_Context : T.Captured_Bytes;
      Parent, Config, Repository : Worldline.Hash;
      Required : R.Check_Span;
      Declaration : R.Declaration;
   end record;
   type Optional_Start (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : Start_Record;
      end case;
   end record;
   type Input_Record is record
      Start : Start_Record;
      Root, Manifests : T.Captured_Bytes;
      Filesystem, Config, Repository : Worldline.Hash;
   end record;
   type Optional_Input (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : Input_Record;
      end case;
   end record;
   type Start_Row is record
      Start : Start_Record;
      Check : T.Check_Identity;
      Source : T.Source_Identity;
      Execution : T.Optional_Execution;
      Verifier : T.Optional_Verifier;
      State : T.E.Execution_State;
      Outcome : T.E.Outcome;
      Payload, Declared : T.Captured_Bytes;
      Raw : W.Raw_Record;
      Confinement : W.Byte;
   end record;
   type Start_Rows is array (T.Index range <>) of Start_Row;

   function Plan_Valid
     (A : T.Bytes; Plans : R.Check_Array; Part : R.Check_Span) return Boolean is
     (R.Valid_Checks (Plans, Part) and then
       (for all K in T.Count range 0 .. Part.Length - 1 =>
         P.Valid (A, T.Span (Plans (Part.First + K).Check)) and then
         P.Valid (A, T.Span (Plans (Part.First + K).Declared)))) with Global => null;
   function Same_Plan
     (A : T.Bytes; Plans : R.Check_Array; L, Rt : R.Check_Span) return Boolean is
     (Plan_Valid (A, Plans, L) and then Plan_Valid (A, Plans, Rt)
      and then L.Length = Rt.Length and then
       (for all K in T.Count range 0 .. L.Length - 1 =>
         P.Same (A, T.Span (Plans (L.First + K).Check),
                    T.Span (Plans (Rt.First + K).Check)) and then
         P.Same (A, T.Span (Plans (L.First + K).Declared),
                    T.Span (Plans (Rt.First + K).Declared)))) with Global => null;
   function Requirements (S : Start_Record; Plans : R.Check_Array)
      return R.Check_Array is
     (if not R.Valid_Checks (Plans, S.Required) or else S.Required.Length = 0
      then R.Check_Array'(1 .. 0 => ((1, 0), (1, 0)))
      else Plans (S.Required.First .. S.Required.First + (S.Required.Length - 1)))
     with Global => null;
   function Start_Valid (A : T.Bytes; S : Start_Record; Plans : R.Check_Array)
      return Boolean is
     (P.Valid (A, T.Span (S.Store))
      and then P.Valid (A, T.Span (S.Subject))
      and then P.Valid (A, T.Span (S.Run))
      and then H.Epoch_Zero (A, H.Epoch_Id'(First => S.Sequence.First, Length => S.Sequence.Length))
      and then (not S.Requirement.Present or else
        P.Valid (A, T.Span (S.Requirement.Value)))
      and then P.Valid (A, T.Span (S.Policy))
      and then P.Valid (A, T.Span (S.Verifier_Plan))
      and then P.Valid (A, T.Span (S.Base_Context))
      and then Plan_Valid (A, Plans, S.Required)) with Global => null;
   function Same_Start (A : T.Bytes; L, Rt : Start_Record; Plans : R.Check_Array) return Boolean is
     (Start_Valid (A, L, Plans) and then Start_Valid (A, Rt, Plans)
      and then P.Same (A, T.Span (L.Store), T.Span (Rt.Store))
      and then P.Same (A, T.Span (L.Subject), T.Span (Rt.Subject))
      and then P.Same (A, T.Span (L.Run), T.Span (Rt.Run))
      and then P.Epoch_Same (A, T.Span (L.Sequence), T.Span (Rt.Sequence))
      and then T.Same_Requirement (A, L.Requirement, Rt.Requirement)
      and then P.Same (A, T.Span (L.Policy), T.Span (Rt.Policy))
      and then P.Same (A, T.Span (L.Verifier_Plan), T.Span (Rt.Verifier_Plan))
      and then P.Same (A, T.Span (L.Base_Context), T.Span (Rt.Base_Context))
      and then L.Parent = Rt.Parent and then L.Config = Rt.Config
      and then L.Repository = Rt.Repository
      and then L.Declaration = Rt.Declaration
      and then Same_Plan (A, Plans, L.Required, Rt.Required)) with Global => null;
   function Input_Valid (A : T.Bytes; S : Start_Record; I : Input_Record; Plans : R.Check_Array)
      return Boolean is
     (Same_Start (A, S, I.Start, Plans)
      and then P.Valid (A, T.Span (I.Root))
      and then P.Valid (A, T.Span (I.Manifests))) with Global => null;
   function Same_Input (A : T.Bytes; L, Rt : Input_Record; Plans : R.Check_Array) return Boolean is
     (Input_Valid (A, L.Start, L, Plans) and then Input_Valid (A, Rt.Start, Rt, Plans)
      and then Same_Start (A, L.Start, Rt.Start, Plans)
      and then P.Same (A, T.Span (L.Root), T.Span (Rt.Root))
      and then P.Same (A, T.Span (L.Manifests), T.Span (Rt.Manifests))
      and then L.Filesystem = Rt.Filesystem
      and then L.Config = Rt.Config and then L.Repository = Rt.Repository) with Global => null;

   type Write_Decision is (Invalid, Insert, Already_Present, Conflict);
   function Start_Reference
     (A : T.Bytes; S : Start_Record; Plans : R.Check_Array; Before : Optional_Start)
      return Write_Decision is
     (if not Start_Valid (A, S, Plans) then Invalid
      elsif not Before.Present then Insert
      elsif Same_Start (A, S, Before.Value, Plans) then Already_Present
      else Conflict) with Global => null;
   procedure Record_Start
     (A : T.Bytes; S : Start_Record; Plans : R.Check_Array; Current : in out Optional_Start;
      Decision : out Write_Decision)
     with Global => null,
       Post => Decision = Start_Reference (A, S, Plans, Current'Old)
         and then (if Decision = Insert then Current = (True, S)
                   else Current = Current'Old);
   function Input_Reference
     (A : T.Bytes; S : Start_Record; I : Input_Record; Plans : R.Check_Array; Before : Optional_Input)
      return Write_Decision is
     (if not Input_Valid (A, S, I, Plans) then Invalid
      elsif not Before.Present then Insert
      elsif Same_Input (A, I, Before.Value, Plans) then Already_Present
      else Conflict) with Global => null;
   procedure Record_Input
     (A : T.Bytes; S : Start_Record; I : Input_Record; Plans : R.Check_Array;
      Current : in out Optional_Input; Decision : out Write_Decision)
     with Global => null,
       Post => Decision = Input_Reference (A, S, I, Plans, Current'Old)
         and then (if Decision = Insert then Current = (True, I)
                   else Current = Current'Old);

   --  No carried State/Outcome authorizes completion. Even contradictory
   --  projections and malformed raw siblings remain available to the total
   --  raw D2 relation and separate promotion gate. Whole raw validity is not
   --  a prerequisite for retaining an independently genuine required FAIL.
   function Row_Valid (A : T.Bytes; S : Start_Record; Row : Start_Row; Plans : R.Check_Array)
      return Boolean is
     (Same_Start (A, S, Row.Start, Plans)
      and then P.Valid (A, T.Span (Row.Check))
      and then P.Valid (A, T.Span (Row.Source))
      and then (not Row.Execution.Present or else
        P.Valid (A, T.Span (Row.Execution.Value)))
      and then (not Row.Verifier.Present or else
        P.Valid (A, T.Span (Row.Verifier.Value)))
      and then P.Valid (A, T.Span (Row.Payload))
      and then P.Valid (A, T.Span (Row.Declared)))
     with Global => null;
   function Capture_Valid
     (A : T.Bytes; S : Start_Record; I : Input_Record;
      Post_Root, Post_Manifests : T.Captured_Bytes; Rows : Start_Rows;
      Plans : R.Check_Array; Completion : R.Required_Check) return Boolean is
     (Input_Valid (A, S, I, Plans)
      and then P.Valid (A, T.Span (Post_Root))
      and then P.Valid (A, T.Span (Post_Manifests))
      and then (for all K in Rows'Range => Row_Valid (A, S, Rows (K), Plans))
      and then P.Valid (A, T.Span (Completion.Check))
      and then P.Valid (A, T.Span (Completion.Declared))) with Global => null;

   -- A changed recapture cannot complete, but its raw observations must still
   -- be retainable as ERROR without a D15 row. It is not malformed transport.
   function Input_Unchanged
     (A : T.Bytes; I : Input_Record; Post_Root, Post_Manifests : T.Captured_Bytes)
      return Boolean is
     (P.Same (A, T.Span (I.Root), T.Span (Post_Root))
      and then P.Same (A, T.Span (I.Manifests), T.Span (Post_Manifests)))
     with Global => null;

   function Bound_To (S : Start_Record; Content : T.Content_Identity)
      return T.Attempt_Binding is
     (Store => S.Store, Subject => S.Subject, Content => Content, Run => S.Run,
      Sequence => S.Sequence, Requirement => S.Requirement) with Global => null;
   function Bind_Row (S : Start_Record; Content : T.Content_Identity;
                      Row : Start_Row) return R.Measured_Result is
     (Item => (Binding => Bound_To (S, Content), Check => Row.Check,
       Source => Row.Source, Execution => Row.Execution, Verifier => Row.Verifier,
       State => Row.State, Outcome => Row.Outcome, Payload => Row.Payload),
      Raw => Row.Raw, Confinement => Row.Confinement, Declared => Row.Declared)
     with Global => null;
   --  Whole positional equation: only the separate final binding is added.
   --  Raw records, order, multiplicity and every original payload are retained.
   function Bind_Rows (S : Start_Record; Content : T.Content_Identity;
                       Rows : Start_Rows) return R.Measured_Array
     with Global => null,
       Post => Bind_Rows'Result'First = Rows'First
         and then Bind_Rows'Result'Last = Rows'Last
         and then (for all K in Rows'Range =>
           Bind_Rows'Result (K) = Bind_Row (S, Content, Rows (K)));

   type Capture_Decision is (Capture_Invalid, Capture_Observed);
   type Capture_Result is record
      Reason : Capture_Decision;
      Classification : R.Classification;
   end record;
   No_Classification : constant R.Classification :=
     (E.Incomplete_Unknown, E.No_Outcome, False);
   --  The empty local Content coordinate is an erased classifier argument,
   --  never a stored binding or identity claim. This operation returns no
   --  content identity and cannot populate a History finalization slot.
   function Capture_Reference
     (A : T.Bytes; S : Start_Record; I : Input_Record;
      Post_Root, Post_Manifests : T.Captured_Bytes; Rows : Start_Rows;
      Plans : R.Check_Array;
      Completion : R.Required_Check) return Capture_Result is
     (if not Capture_Valid
       (A, S, I, Post_Root, Post_Manifests, Rows, Plans, Completion)
      then (Capture_Invalid, No_Classification)
      elsif not Input_Unchanged (A, I, Post_Root, Post_Manifests)
      then (Capture_Observed, No_Classification)
      else (Capture_Observed, R.Reference
        (A, Bound_To (S, (1, 0)), Bind_Rows (S, (1, 0), Rows), Requirements (S, Plans),
         S.Declaration, (Bound_To (S, (1, 0)), I.Root, Post_Root), Completion)))
     with Global => null;
   function Classify_Capture
     (A : T.Bytes; S : Start_Record; I : Input_Record;
      Post_Root, Post_Manifests : T.Captured_Bytes; Rows : Start_Rows;
      Plans : R.Check_Array;
      Completion : R.Required_Check) return Capture_Result
     with Global => null,
       Post => Classify_Capture'Result = Capture_Reference
         (A, S, I, Post_Root, Post_Manifests, Rows, Plans, Completion);

   type Final_Components is record
      Environment, Evidence : Worldline.Hash;
   end record;
   function Final_Identity (S : Start_Record; I : Input_Record;
                            Components : Final_Components) return Worldline.Hash is
     (Worldline.World.Identity
       (S.Parent, I.Filesystem, I.Config, I.Repository,
        Components.Environment, Components.Evidence)) with Global => null;
   Hash_Prefix : constant String := "sha256:";
   Hex_Digits : constant String := "0123456789abcdef";
   function Content_Reference
     (A : T.Bytes; Content : T.Content_Identity; Digest : Worldline.Hash)
      return Boolean is
     (P.Valid (A, T.Span (Content))
      and then Content.Length = Hash_Prefix'Length + Digest'Length * 2
      and then (for all K in Hash_Prefix'Range =>
        A (Content.First + T.Count (K - Hash_Prefix'First)) =
          P.Byte (Character'Pos (Hash_Prefix (K))))
      and then (for all K in Digest'Range =>
        A (Content.First + Hash_Prefix'Length + T.Count (K - Digest'First) * 2) =
          P.Byte (Character'Pos (Hex_Digits (Integer (Digest (K)) / 16 + Hex_Digits'First)))
        and then A (Content.First + Hash_Prefix'Length + T.Count (K - Digest'First) * 2 + 1) =
          P.Byte (Character'Pos (Hex_Digits (Integer (Digest (K)) mod 16 + Hex_Digits'First)))))
     with Global => null;
   function Content_Matches
     (A : T.Bytes; Content : T.Content_Identity; Digest : Worldline.Hash)
      return Boolean with Global => null,
        Post => Content_Matches'Result = Content_Reference (A, Content, Digest);
   type Artifact_References is record
      Context, Source, Evidence, Environment : T.Captured_Bytes;
   end record;
   function Artifacts_Valid (A : T.Bytes; Artifacts : Artifact_References)
      return Boolean is
     (P.Valid (A, T.Span (Artifacts.Context))
      and then P.Valid (A, T.Span (Artifacts.Source))
      and then P.Valid (A, T.Span (Artifacts.Evidence))
      and then P.Valid (A, T.Span (Artifacts.Environment))) with Global => null;
   type Seal_Decision is (Seal_Invalid, Content_Mismatch, Seal_Observed);
   type Seal_Result is record
      Reason : Seal_Decision;
      Identity : Worldline.Hash;
      Classification : R.Classification;
      Finalization : H.Optional_Record;
   end record;
   function History_Projection
     (S : Start_Record; Content : T.Content_Identity;
      Classification : R.Classification) return H.Evaluation_Record is
     (Subject => (True, H.Subject_Id'(First => S.Subject.First, Length => S.Subject.Length)),
      Content => (True, H.Content_Id'(First => Content.First, Length => Content.Length)),
      Requirement => (if S.Requirement.Present then
        (True, H.Requirement_Id'(First => S.Requirement.Value.First,
                                 Length => S.Requirement.Value.Length)) else (Present => False)),
      Run => (True, H.Evaluation_Id'(First => S.Run.First, Length => S.Run.Length)),
      Sequence => (True, H.Epoch_Id'(First => S.Sequence.First, Length => S.Sequence.Length)),
      State => (if Classification.State = E.Completed then H.Completed else H.Error),
      Outcome => (if Classification.Outcome = E.Passed then H.Passed
                  elsif Classification.Outcome = E.Failed then H.Failed
                  else H.No_Verdict)) with Global => null;
   function Payload_Spans (Rows : Start_Rows) return Canonical_Artifacts.Span_Array
     with Global => null,
       Post => Payload_Spans'Result'First = Rows'First
         and then Payload_Spans'Result'Last = Rows'Last
         and then (for all K in Rows'Range =>
           Payload_Spans'Result (K) = P.Span (Rows (K).Payload));
   function Artifact_Binding
     (A : T.Bytes; Rows : Start_Rows; Components : Final_Components;
      Artifacts : Artifact_References) return Boolean is
     (Artifacts_Valid (A, Artifacts)
      and then Canonical_Artifacts.Bindings
        (A, P.Span (Artifacts.Evidence), P.Span (Artifacts.Environment),
         P.Span (Artifacts.Context), Payload_Spans (Rows),
         Components.Evidence, Components.Environment)) with Global => null;

   function Seal_Reference
     (A : T.Bytes; S : Start_Record; I : Input_Record;
      Post_Root, Post_Manifests : T.Captured_Bytes; Rows : Start_Rows;
      Plans : R.Check_Array;
      Completion : R.Required_Check; Content : T.Content_Identity;
      Components : Final_Components; Artifacts : Artifact_References) return Seal_Result
     with Global => null;
   function Seal
     (A : T.Bytes; S : Start_Record; I : Input_Record;
      Post_Root, Post_Manifests : T.Captured_Bytes; Rows : Start_Rows;
      Plans : R.Check_Array;
      Completion : R.Required_Check; Content : T.Content_Identity;
      Components : Final_Components; Artifacts : Artifact_References) return Seal_Result
     with Global => null,
       Post => (if Seal'Result.Reason = Seal_Observed then
         Artifact_Binding (A, Rows, Components, Artifacts))
       and then Seal'Result = Seal_Reference
         (A, S, I, Post_Root, Post_Manifests, Rows, Plans,
          Completion, Content, Components, Artifacts)
         and then (if Seal'Result.Reason /= Seal_Observed then
           not Seal'Result.Finalization.Present
           and then Seal'Result.Classification = No_Classification
          else Seal'Result.Identity = Final_Identity (S, I, Components)
           and then Seal'Result.Classification = Capture_Reference
             (A, S, I, Post_Root, Post_Manifests, Rows, Plans, Completion).Classification
           and then Seal'Result.Finalization.Present
           and then Seal'Result.Finalization.Value = History_Projection
             (S, Content, Seal'Result.Classification));
end Evaluation_Finalization;
