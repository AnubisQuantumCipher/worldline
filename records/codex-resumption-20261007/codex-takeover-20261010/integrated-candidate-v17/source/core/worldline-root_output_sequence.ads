with Worldline.Custody_V2_Subject_Evidence;
with Worldline.Custody_V2_Operation_Journal;
package Worldline.Root_Output_Sequence with SPARK_Mode is
   package SE renames Worldline.Custody_V2_Subject_Evidence;
   package I renames SE.L;
   package E renames I.E;
   package Q renames E.Q;
   package M renames SE.M;
   package P renames SE.P;
   package J renames Worldline.Custody_V2_Operation_Journal;
   use type E.Count;
   type Allocation_Status is
     (Refused, Allocated, Already_Written, Predecessor_Pending);
   -- Wire status is the ordinal position: 0 refuses; 1 returns the native
   -- selected quantity; replay alone uses 2 already-written drop / 3 hold.
   -- A relay worker's 1 authorizes protocol delivery, never client writing.
   type Query_Kind is (Allocate, Replay, Confirm_Written, Observe_Written);
   type Output_Observation is record
      Kind : Allocation_Status := Refused;
      Position, Needed, Written : E.Count := 0;
   end record;
   -- Query names select a native entry, never a caller permission or counter.
   -- The complete original prefix is authenticated before its emission order
   -- is replayed. Epoch authenticates the current channel; it does not reset
   -- the output sequence of an existing generation/request/subgeneration.
   procedure Evaluate
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Proof : J.Journal_Proof; Query : Query_Kind; Output : out E.Bytes;
      Result : out Output_Observation)
     with Global => null, Always_Terminates,
       Post => Result.Written <= Output'Length and then
         (if Result.Kind = Refused then Result.Needed = 0 and then Result.Written = 0) and then
         (if Result.Kind /= Refused then Result.Needed > 0 and then
            Result.Written = (if Result.Needed <= Output'Length then Result.Needed else 0));
   procedure Next_Output (Data : E.Bytes; Output : out E.Bytes;
                          Result : out Output_Observation)
     with Global => null, Always_Terminates,
       Post => Result.Written <= Output'Length and then
         (if Result.Kind = Refused then Result.Needed = 0 and then Result.Written = 0) and then
         (if Result.Kind /= Refused then Result.Needed > 0 and then
            Result.Written = (if Result.Needed <= Output'Length then Result.Needed else 0));
   procedure Replay_Output (Data : E.Bytes; Output : out E.Bytes;
                            Result : out Output_Observation)
     with Global => null, Always_Terminates,
       Post => Result.Written <= Output'Length and then
         (if Result.Kind = Refused then Result.Needed = 0 and then Result.Written = 0) and then
         (if Result.Kind /= Refused then Result.Needed > 0 and then
            Result.Written = (if Result.Needed <= Output'Length then Result.Needed else 0));
   procedure Written_Output (Data : E.Bytes; Output : out E.Bytes;
                             Result : out Output_Observation)
     with Global => null, Always_Terminates,
       Post => Result.Written <= Output'Length and then
         (if Result.Kind = Refused then Result.Needed = 0 and then Result.Written = 0) and then
         (if Result.Kind /= Refused then Result.Needed > 0 and then
            Result.Written = (if Result.Needed <= Output'Length then Result.Needed else 0));
   -- Pure full-prefix observation before a Front signs PEER_STATUS. No
   -- production allocation, append or serving/write permission is implied.
   procedure Prefix_Output (Data : E.Bytes; Output : out E.Bytes;
                            Result : out Output_Observation)
     with Global => null, Always_Terminates,
       Post => Result.Written <= Output'Length and then
         (if Result.Kind = Refused then Result.Needed = 0 and then Result.Written = 0) and then
         (if Result.Kind /= Refused then Result.Needed > 0 and then
            Result.Written = (if Result.Needed <= Output'Length then Result.Needed else 0));
end Worldline.Root_Output_Sequence;
