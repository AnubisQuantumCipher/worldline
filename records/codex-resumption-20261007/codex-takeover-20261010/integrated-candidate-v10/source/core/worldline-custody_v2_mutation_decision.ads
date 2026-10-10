with Worldline.Root_Output_Sequence;
with Worldline.Custody_V2_Fold_Engine;
with Worldline.Custody_V2_Delta_Encoding;
with Worldline.Custody_V2_Subject_Evidence;
-- Pure F.6 composition. Ready_Apply authorizes the returned SQL delta only;
-- it is never fresh-front admission, physical permission, or an effect.
package Worldline.Custody_V2_Mutation_Decision with SPARK_Mode is
   package F renames Worldline.Custody_V2_Fold_Engine;
   package I renames F.I;
   package E renames I.E;
   package Q renames E.Q;
   package D renames Worldline.Custody_V2_Delta_Encoding;
   package SE renames Worldline.Custody_V2_Subject_Evidence;
   package OS renames Worldline.Root_Output_Sequence;
   use type E.Count;
   use type Q.Byte;
   use type F.Fold_Status;
   use type OS.Allocation_Status;
   type Action is (Ready_Apply, Replay_Unchanged, Retain_Unknown, Refused);
   type Observation is record
      State : Action := Refused;
      Reason : F.Status := F.Input_Malformed;
      Position, Needed, Written : E.Count := 0;
   end record;
   function Status_Code (Result : Observation) return Natural is
     (case Result.State is
        when Ready_Apply => 0, when Replay_Unchanged => 1,
        when Retain_Unknown => 2, when Refused => F.Status'Pos (Result.Reason))
     with Global => null;
   -- Encoding-only producer for actual generation/epoch/transfer packets.
   -- Every unsigned LE operand is admitted, including zero/leading-zero input;
   -- output is minimal. The original Is_Successor is checked natively before
   -- exposing bytes. This never authenticates a counter or grants permission.
   procedure Successor_LE
     (Data : E.Bytes; Output : out E.Bytes; Needed : out E.Count;
      Complete : out Boolean)
     with Global => null, Always_Terminates,
       Post => Complete = (Needed > 0 and then Needed <= Output'Length) and then
         (if Complete then Output (Output'First + (Needed - 1)) /= 0);
   type Context_Observation is record
      State : F.Fold_Status := F.Fold_Refused;
      Reason : F.Status := F.Input_Malformed;
      Position, Needed, Written : E.Count := 0;
   end record;
   -- Existing mutation-envelope selectors only; X5 is not a query permission.
   -- Authenticated current/root/subject operands and proposed counter bytes
   -- precede actual packet construction. The returned load action is read-only;
   -- full mutation Legal MUST redecide the eventual complete actual capture.
   procedure Context_View (Data : E.Bytes; Output : out E.Bytes;
                           Result : out Context_Observation)
     with Global => null, Always_Terminates,
       Post => Result.Written <= Output'Length and then
         (if Result.State = F.Fold_Refused then
            Result.Needed = 0 and then Result.Written = 0) and then
         (if Result.State = F.History_Folded then Result.Needed > 0 and then
            Result.Written = (if Result.Needed <= Output'Length then Result.Needed else 0));
   type Cleanup_Observation is record
      State : F.Fold_Status := F.Fold_Refused;
      Reason : F.Status := F.Input_Malformed;
      Kind : SE.Cleanup_Kind := SE.Retain_Unknown;
      Position : E.Count := 0;
   end record;
   -- Same complete mutation envelope, but no Next, SQL delta or side effect.
   -- A fixed family proposal is factual input, not the cleanup decision.
   -- Commit still requires a fresh full Decide of the actual chosen event.
   function Cleanup_Status_Code (Result : Cleanup_Observation) return Natural is
     (if Result.State = F.History_Folded then SE.Cleanup_Kind'Pos (Result.Kind)
      else 4 + F.Status'Pos (Result.Reason))
      with Global => null;
   procedure Cleanup_Decide (Data : E.Bytes; Result : out Cleanup_Observation)
      with Global => null, Always_Terminates,
      Post => (if Result.State = F.Fold_Refused then F.Status'Pos (Result.Reason) >= 3);
   -- Reconciled append-retry redecides the actual smaller retained native
   -- mutation input and exact returned delta, never a copied status claim.
   function Attempt_Matches
     (Data : E.Bytes; Attempt, Containing_Input : E.Span) return Boolean
      with Global => null,
        Subprogram_Variant => (Decreases => Containing_Input.Length, Decreases => 1);
   type Serving_Observation is record
      Kind : SE.Join_Status := SE.Evidence_Refused;
      Reason : F.Status := F.Input_Malformed;
      Position : E.Count := 0;
   end record;
   -- Before-effect original serving admission; no response/blob or Next.
   procedure Serving_Decide (Data : E.Bytes; Result : out Serving_Observation)
      with Global => null, Always_Terminates;
   -- Complete original PRECONSTRUCTOR closed-owner eligibility, read-only.
   -- Same held mutation-v2 factual CLOSED_WITNESS proposal; no Legal/Next,
   -- physical claim, dup, constructor, row delta or source-role relabeling.
   procedure Closed_Decide (Data : E.Bytes; Result : out Serving_Observation)
      with Global => null, Always_Terminates,
        Subprogram_Variant => (Decreases => Data'Length, Decreases => 14);
   -- The complete before envelope is a view into Data. Its owner/SQL/X4/X5
   -- correspondence is decided before exact FULL-record retry, then CAS/Legal.
   -- Output(1..0) obtains Needed; a short buffer never advertises Written.
   procedure Decide (Data : E.Bytes; Output : out E.Bytes;
                     Result : out Observation)
     with Global => null, Always_Terminates,
       Subprogram_Variant => (Decreases => Data'Length, Decreases => 14),
       Post => Result.Written <= Output'Length and then
         (if Result.State /= Ready_Apply then
            Result.Needed = 0 and then Result.Written = 0) and then
         (if Result.Written > 0 then
            Result.State = Ready_Apply and then
            Result.Written = Result.Needed) and then
         (if Result.State = Ready_Apply then Result.Needed > 0 and then
            Result.Written = (if Result.Needed <= Output'Length then Result.Needed else 0)) and then
         (if Result.State = Replay_Unchanged then Result.Position > 0) and then
         (if Result.State = Refused then F.Status'Pos (Result.Reason) >= 3);
   -- Same complete mutation envelope plus retry_attempt=BYTES(saved original
   -- uncertainty); fresh native X5 never transplants the failed old X5.
   procedure Retry_Decide (Data : E.Bytes; Output : out E.Bytes;
                           Result : out Observation)
     with Global => null, Always_Terminates,
       Subprogram_Variant => (Decreases => Data'Length, Decreases => 14),
       Post => Result.Written <= Output'Length and then
         (if Result.Written > 0 then Result.State = Ready_Apply and then
            Result.Written = Result.Needed) and then
         (if Result.State = Replay_Unchanged then
            Result.Position > 0 and then Result.Needed = 0 and then Result.Written = 0);
   procedure Output_Next (Data : E.Bytes; Output : out E.Bytes;
                          Result : out OS.Output_Observation)
     with Global => null, Always_Terminates,
       Post => Result.Written <= Output'Length and then
         (if Result.Kind = OS.Refused then Result.Needed = 0 and then Result.Written = 0) and then
         (if Result.Kind /= OS.Refused then Result.Needed > 0 and then
            Result.Written = (if Result.Needed <= Output'Length then Result.Needed else 0));
   procedure Output_Replay (Data : E.Bytes; Output : out E.Bytes;
                            Result : out OS.Output_Observation)
     with Global => null, Always_Terminates,
       Post => Result.Written <= Output'Length and then
         (if Result.Kind = OS.Refused then Result.Needed = 0 and then Result.Written = 0) and then
         (if Result.Kind /= OS.Refused then Result.Needed > 0 and then
            Result.Written = (if Result.Needed <= Output'Length then Result.Needed else 0));
   procedure Output_Written (Data : E.Bytes; Output : out E.Bytes;
                             Result : out OS.Output_Observation)
     with Global => null, Always_Terminates,
       Post => Result.Written <= Output'Length and then
         (if Result.Kind = OS.Refused then Result.Needed = 0 and then Result.Written = 0) and then
         (if Result.Kind /= OS.Refused then Result.Needed > 0 and then
            Result.Written = (if Result.Needed <= Output'Length then Result.Needed else 0));
   -- Actual retained Front ACK prefix before PEER_STATUS signing; not an
   -- allocator, proposed sequence, Python cursor or serving permission.
   procedure Output_Prefix (Data : E.Bytes; Output : out E.Bytes;
                            Result : out OS.Output_Observation)
     with Global => null, Always_Terminates,
       Post => Result.Written <= Output'Length and then
         (if Result.Kind = OS.Refused then Result.Needed = 0 and then Result.Written = 0) and then
         (if Result.Kind /= OS.Refused then Result.Needed > 0 and then
            Result.Written = (if Result.Needed <= Output'Length then Result.Needed else 0));
end Worldline.Custody_V2_Mutation_Decision;
