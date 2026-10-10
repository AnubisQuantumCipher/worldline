with Worldline.Custody_V2_Load_Input;
package Worldline.Custody_V2_K4_Resource_Ack with SPARK_Mode is
   package L renames Worldline.Custody_V2_Load_Input;
   package E renames L.E;
   -- Native lexical observer of the same immutable actual scoped arena.
   -- Default state is invalid; callers cannot construct authenticated facts.
   -- The observer must not outlive Data and is never stored or exported.
   type Prepared_History
     (Data : access constant E.Bytes;
      Parsed_Data : access constant L.Parsed_Input) is limited private;
   procedure Establish_History
     (Context : in out Prepared_History; Roster : E.Span)
     with Global => null, Always_Terminates;
   -- Factual history closure only, not installation/source/issuer admission.
   function Current_Matches (Context : Prepared_History) return Boolean
     with Global => null;
   -- Once at frame handoff, bind the observer to exact full bytes and original
   -- first-index/roster coordinates; not a per-event hash or pointer test.
   function Source_Matches
     (Context : Prepared_History; Data : E.Bytes; Roster : E.Span)
      return Boolean
     with Global => null;
   function Authenticated
     (Context : Prepared_History; Event, Prior_Event : E.Span) return Boolean
     with Global => null;
   function Direct_Authenticated
     (Context : Prepared_History; Input_Data : E.Bytes;
      Capture, Acknowledgement : E.Span) return Boolean
     with Global => null;
   -- Shared full factual history authentication, without requiring a terminal
   -- ACK. This is not authorization and makes no resource or journal mutation.
   function Current_Authenticated (Value : L.Parsed_Input) return Boolean
     with Global => null;
   -- Event and Prior_Event are original complete operation-event views in the
   -- owned arena. Exact retained owner intent precedes full committed replay.
   function Authenticated
     (Value : L.Parsed_Input; Event, Prior_Event : E.Span) return Boolean
     with Global => null;
   -- The raw runtime boundary retains operation_capture.archive's capture and
   -- complete ORIGINAL or SCOPED ACK, without projecting either protocol.
   -- A complete authentic load remains required; this never authorizes an
   -- effect, appends a resource event, or substitutes a fresh eligibility test.
   function Direct_Authenticated
     (Value : L.Parsed_Input; Input_Data : E.Bytes;
      Capture, Acknowledgement : E.Span) return Boolean
     with Global => null;
private
   type History_State is (Unestablished, Original_Verified, Scoped_Verified);
   type Prepared_History
     (Data : access constant E.Bytes;
      Parsed_Data : access constant L.Parsed_Input) is limited record
      State : History_State := Unestablished;
      Roster : E.Span := (1, 0);
      Events : E.Span := (1, 0);
      Replays : E.Span := (1, 0);
   end record;
end Worldline.Custody_V2_K4_Resource_Ack;
