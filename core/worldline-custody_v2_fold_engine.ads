with Canonical_Artifacts;
with Worldline.Custody_V2_Load_Input;
with Worldline.Custody_V2_Event_Joins;
with Worldline.Custody_V2_History;
with Worldline.Custody_V2_Operation_Journal;
package Worldline.Custody_V2_Fold_Engine with SPARK_Mode is
   package I renames Worldline.Custody_V2_Load_Input;
   package J renames Worldline.Custody_V2_Event_Joins;
   package H renames Worldline.Custody_V2_History;
   package D renames H.D;
   package C renames D.C;
   package F renames D.F;
   package S renames F.S;
   package M renames D.M;
   package Q renames D.Q;
   package A renames D.A;
   package P renames A.P;
   package OJ renames Worldline.Custody_V2_Operation_Journal;
   use type Q.Byte_Count;
   use type I.Decode_Status;
   use type C.Status;
   use type Canonical_Artifacts.Genesis_Correspondence;
   type Status is (Front_Startup, Recover_Retained, Retain_Unknown,
      Input_Malformed, Genesis_Correspondence, Archive_Chain_Refused,
      Stored_Rows_Differ, Owner_Roster_Refused, Schema_Refused,
      Foreign_Key_Refused, Wrong_Generation, Wrong_Actor,
      Illegal_Root_Transition, Illegal_Request_Transition,
      Illegal_Descriptor_Transition, Cross_Condition, Alternative_Taken,
      Evidence_Missing, Join_Not_Ready, Subject_Unknown,
      Barrier_Subjects_Open, CAS_Stale, Ambiguous_History);
   type Fold_Status is (Fold_Refused, History_Folded);
   type Observation is record
      State : Fold_Status := Fold_Refused;
      Reason : Status := Input_Malformed;
      Position : Q.Byte_Count := 0;
   end record;
   type Fold_State (Root_Capacity, Subject_Capacity : Q.Byte_Count) is record
      Roots : M.Root_State_Array (1 .. Root_Capacity);
      Subjects : M.Subject_State_Array (1 .. Subject_Capacity);
      Raw_Roots : S.Root_Rows (1 .. Root_Capacity);
      Raw_Subjects : S.Subject_Rows (1 .. Subject_Capacity);
      Root_Count, Subject_Count : Q.Byte_Count := 0;
      Current : Q.Byte_Count := 0;
      Logical_S0 : Boolean := True;
   end record;
   function Archive_Authenticated (Value : I.Parsed_Input) return Boolean is
     (Value.Status = I.Parsed and then
      Value.Decoded_Event_Count <= Value.Event_Count and then
      Canonical_Artifacts.Genesis_Archive_Matches
        (Value.Arena, Value.Genesis_File, Value.Genesis_Row) =
          Canonical_Artifacts.Typed_Tree_Matches_Source_Custody_Open and then
      C.Verify (Value.Arena, Value.Key, Value.Genesis_Row, Value.Genesis_Message,
        Value.Genesis_Mac, Value.Events (1 .. Value.Decoded_Event_Count), Value.Heads).State =
          C.Archive_Chain_Matches_Genesis_JSON_And_Fold_Open)
     with Ghost, Global => null;
   function Rows_Match (Value : I.Parsed_Input; State : Fold_State) return Boolean
      with Global => null;
   function Root_Index (Value : I.Parsed_Input; State : Fold_State;
                        Event : M.Event_Record) return Q.Byte_Count
      with Global => null,
      Post => Root_Index'Result = 0 or else Root_Index'Result = State.Current or else
         Root_Index'Result in 1 .. State.Root_Count;
   function Subject_Index (Value : I.Parsed_Input; State : Fold_State;
                           Event : M.Event_Record) return Q.Byte_Count
      with Global => null,
      Post => Subject_Index'Result <= State.Subject_Count and then
         Subject_Index'Result <= State.Subject_Capacity;
   -- Authentic prefix hook for event controls/decision composition. Full X4
   -- and native genesis correspondence precede every prefix, including S0.
   -- Prefix success is not a final stored-row or startup permission claim.
   procedure Fold_Prefix
     (Value : I.Parsed_Input; Through : Q.Byte_Count; State : out Fold_State;
      Result : out Observation)
      with Global => null, Always_Terminates,
      Subprogram_Variant => (Decreases => Value.Source_Input.Length, Decreases => 9),
      Post => (if Result.State = History_Folded then
         Archive_Authenticated (Value) and then
         Through <= Value.Decoded_Event_Count and then
         State.Root_Count <= State.Root_Capacity and then
         State.Subject_Count <= State.Subject_Capacity);
   procedure Fold_Prefix
     (Value : I.Parsed_Input; Through : Q.Byte_Count; State : out Fold_State;
      History : in out A.R.Retained_Events; Proof : out OJ.Journal_Proof;
      Result : out Observation)
      with Global => null, Always_Terminates,
      Subprogram_Variant => (Decreases => Value.Source_Input.Length, Decreases => 8),
      Post => (if Result.State = History_Folded then
         Archive_Authenticated (Value) and then
         Through <= Value.Decoded_Event_Count and then
         History'First = 1 and then History'Length = Value.Decoded_Event_Count and then
         State.Root_Count <= State.Root_Capacity and then
         State.Subject_Count <= State.Subject_Capacity and then
         State.Current in 1 .. State.Root_Capacity and then
         (if Through = Value.Decoded_Event_Count then
            Rows_Match (Value, State) and then
            State.Root_Count = Value.Root_Count and then
            State.Subject_Count = Value.Subject_Count));
   -- No stored S0 row is manufactured. A logical S0 model is kept internally
   -- until an actual authentic transition creates the first durable row.
   procedure Fold (Value : I.Parsed_Input; State : out Fold_State;
                   Proof : out OJ.Journal_Proof; Result : out Observation)
      with Global => null, Always_Terminates,
      Subprogram_Variant => (Decreases => Value.Source_Input.Length, Decreases => 11),
      Post => (if Result.State = History_Folded then
         Archive_Authenticated (Value) and then
         Rows_Match (Value, State) and then
         State.Root_Count = Value.Root_Count and then
         State.Subject_Count = Value.Subject_Count and then
         State.Current in 1 .. State.Root_Capacity);
   procedure Fold (Value : I.Parsed_Input; State : out Fold_State;
                   History : in out A.R.Retained_Events; Proof : out OJ.Journal_Proof;
                   Result : out Observation)
      with Global => null, Always_Terminates,
      Subprogram_Variant => (Decreases => Value.Source_Input.Length, Decreases => 10),
      Post => (if Result.State = History_Folded then
         Archive_Authenticated (Value) and then
         Rows_Match (Value, State) and then
         State.Root_Count = Value.Root_Count and then
         State.Subject_Count = Value.Subject_Count);
   -- This is an event-level Legal decision over an already-authenticated full
   -- prefix; it never accepts an input Ready/allowed flag as native evidence.
   function Legal
     (Value : I.Parsed_Input; Index : Q.Byte_Count; State : Fold_State;
      History : A.R.Retained_Events; Alternatives : A.Alternative_Rows;
      Proof : OJ.Journal_Proof)
      return Status with Global => null,
      Subprogram_Variant => (Decreases => Value.Source_Input.Length, Decreases => 8);
   -- Only used after Legal = Front_Startup (internal successful-step code).
   -- Complete typed images reuse original transition contracts; raw images
   -- preserve every SQL nullable/inactive field rather than model defaults.
   procedure Next
     (Value : I.Parsed_Input; Index : Q.Byte_Count; State : in out Fold_State;
      Applied : out Boolean)
      with Global => null, Always_Terminates,
      Post => (if Applied then State.Root_Count <= State.Root_Capacity and then
         State.Subject_Count <= State.Subject_Capacity);
   -- Atomic pure decision/image entry: decode the authentic candidate once,
   -- decide every original Legal clause, and only then derive original Next.
   procedure Apply_Legal
     (Value : I.Parsed_Input; Index : Q.Byte_Count; State : in out Fold_State;
      History : A.R.Retained_Events; Alternatives : A.Alternative_Rows;
      Proof : OJ.Journal_Proof; Reason : out Status; Applied : out Boolean)
      with Global => null, Always_Terminates,
      Subprogram_Variant => (Decreases => Value.Source_Input.Length, Decreases => 8),
      Post => (if Applied then
         Reason = Front_Startup and then Value.Status = I.Parsed and then
         Index in Value.Events'Range and then OJ.Established (Value, Proof) and then
         State.Root_Count <= State.Root_Capacity and then
         State.Subject_Count <= State.Subject_Capacity
         else Reason /= Front_Startup);
   function Load_Decide (Value : I.Parsed_Input) return Observation
      with Global => null,
      Subprogram_Variant => (Decreases => Value.Source_Input.Length, Decreases => 12);
   -- Same complete X4/X5/genesis/raw-row fold, sharing genuine readonly
   -- original owner/resource histories established by the lexical caller.
   function Load_Decide
     (Value : I.Parsed_Input; Owner_Context : OJ.O.Prepared_History;
      Resource_Context : OJ.K.Prepared_History) return Observation
      with Global => null,
      Subprogram_Variant => (Decreases => Value.Source_Input.Length, Decreases => 12);
end Worldline.Custody_V2_Fold_Engine;
