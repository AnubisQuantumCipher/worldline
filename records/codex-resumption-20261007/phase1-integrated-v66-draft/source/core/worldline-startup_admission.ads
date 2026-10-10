with Worldline.Custody_V2_Load_Input;
package Worldline.Startup_Admission with SPARK_Mode is
   package L renames Worldline.Custody_V2_Load_Input;
   type Action is (Refused, Already_Consumed, Consume_Unused_Existing,
                   Complete_Intent_Existing, Create_Unused_Offline);
   for Action use (Refused => 0, Already_Consumed => 1,
                   Consume_Unused_Existing => 2, Complete_Intent_Existing => 3,
                   Create_Unused_Offline => 4);
   type Decision is record
      Status : Action := Refused;
      Position : L.E.Count := 0;
   end record;
   function Observe (Value : L.Parsed_Input; Journal_Name : String) return Decision
     with Global => null;
   function Observe_Owner
     (Data : L.E.Bytes; Roster : L.E.Span; Journal_Name : String) return Decision
     with Global => null;
   -- Complete original bootstrap authorization, independent of operation-head
   -- admission. Present CONSUMED journals may legitimately have progressed.
   -- A missing journal is never creation permission at this runtime boundary.
   function Decide (Value : L.Parsed_Input; Journal_Name : String) return Action
     with Global => null;
   -- The separate original owner API admits creation, without requiring a
   -- custody-v2 root/principal to exist. This is not selectable by runtime
   -- input labels: the owned owner boundary is a distinct exported function.
   function Decide_Owner
     (Data : L.E.Bytes; Roster : L.E.Span; Journal_Name : String) return Action
     with Global => null;
   -- Shared original facts only. The independently authored operation action
   -- owns absence/exclusive creation/grant/ENTRY authorization. Target is the
   -- exact mutable original operation-head artifact, never a permission flag.
   function Operation_Source_Corresponds
     (Data : L.E.Bytes; Roster, Profile, Target : L.E.Span) return Boolean
     with Global => null;
   function All_Required_Admissions_Consumed (Value : L.Parsed_Input) return Boolean
     with Global => null;
   -- Exact durable post-state correspondence. The before/after captures retain
   -- every original file, SQL cell, source lease and held lock. Only the selected
   -- bootstrap CAS plus one original history row may differ.
   function Transition_Matches
     (Before, After : L.Parsed_Input; Journal_Name : String;
      Before_Action, After_Action : Action) return Boolean
     with Global => null;
   function Owner_Transition_Matches
     (Before, After : L.E.Bytes; Before_Roster, After_Roster : L.E.Span;
      Journal_Name : String; Before_Action, After_Action : Action) return Boolean
     with Global => null;
end Worldline.Startup_Admission;
