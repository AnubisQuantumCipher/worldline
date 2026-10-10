with Worldline.Custody_V2_Load_Input;
with Worldline.Retained_Evidence_Replay;
package Worldline.Custody_V2_Owner_Correspondence with SPARK_Mode is
   package L renames Worldline.Custody_V2_Load_Input;
   package E renames L.E;
   package R renames Worldline.Retained_Evidence_Replay;
   use type R.Replay_State;
   use type L.Decode_Status;
   -- Original complete source correspondence also serves bootstrap callers
   -- before any operation head or custody row exists. It never grants creation.
   function Current_Capture_Matches
     (Source_Data, Capture_Data : E.Bytes; Roster, Capture : E.Span)
      return Boolean with Global => null;
   -- Complete factual owner/schema/SQL join only, never current packet
   -- reconstruction or permission. Full authority uses Owner_Corresponds.
   function Owner_Rows_Correspond (Value : L.Parsed_Input) return Boolean
     with Global => null,
       Post => (if Owner_Rows_Correspond'Result then Value.Status = L.Parsed);
   function Owner_Corresponds (Value : L.Parsed_Input) return Boolean
     with Global => null,
       Post => (if Owner_Corresponds'Result then Value.Status = L.Parsed);
   function Startup_Native (Value : L.Parsed_Input) return R.Scoped_Replay_Result
     with Global => null,
       Post => (if Startup_Native'Result.State = R.Native_Redecided then
          Owner_Corresponds (Value));
   function Startup_Contains_Unknown (Value : L.Parsed_Input) return Boolean
     with Global => null,
       Post => (if Startup_Contains_Unknown'Result then Owner_Corresponds (Value));
   procedure Context_Decide
     (Value : L.Parsed_Input; Owner_Matches : out Boolean; Native : out R.Scoped_Replay_Result)
     with Global => null, Always_Terminates,
       Post => (if Native.State = R.Native_Redecided then Owner_Matches and then Value.Status = L.Parsed);
   procedure Context_Decide
     (Value : L.Parsed_Input; Owner_Matches : out Boolean; Native : out R.Scoped_Replay_Result;
      Contains_Unknown : out Boolean)
     with Global => null, Always_Terminates,
       Post => (if Native.State = R.Native_Redecided then Owner_Matches and then Value.Status = L.Parsed)
         and then (if Contains_Unknown then Native.State = R.Native_Redecided and then Owner_Matches);
   -- All verdict outputs are derived here. There is no owner/permission input
   -- flag, and each actual classification is reexecuted once per context call.
   -- Complete factual owner/schema/SQL correspondence and genuine redecision
   -- are separate from X4/X5. Neither Parsed nor these inputs claim Ready.
end Worldline.Custody_V2_Owner_Correspondence;
