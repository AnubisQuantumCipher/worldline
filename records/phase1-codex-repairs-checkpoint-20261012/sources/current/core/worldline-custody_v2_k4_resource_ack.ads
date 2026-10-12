with Worldline.Custody_V2_Load_Input;
private with Attest.Custody_SHA256;
package Worldline.Custody_V2_K4_Resource_Ack with SPARK_Mode is
   package L renames Worldline.Custody_V2_Load_Input;
   package E renames L.E;
   -- Native lexical observer of the same immutable actual scoped arena.
   -- Default state is invalid; callers cannot construct authenticated facts.
   -- The observer holds no reference (SPARK admits no access discriminant):
   -- every operation receives the arena it was established on, and the
   -- observer records that arena's exact extent and whole-bytes digest and
   -- refuses any arena whose extent differs. It is never stored or exported.
   type Prepared_History is limited private;
   procedure Establish_History
     (Context : out Prepared_History; Data : E.Bytes; Roster : E.Span)
     with Global => null, Always_Terminates;
   -- Factual history closure only, not installation/source/issuer admission.
   function Current_Matches (Context : Prepared_History) return Boolean
     with Global => null;
   -- Once at frame handoff, bind the observer to exact full bytes (extent and
   -- whole-bytes digest recorded at establishment) and original
   -- first-index/roster coordinates; not a per-event test.
   function Source_Matches
     (Context : Prepared_History; Data : E.Bytes; Roster : E.Span)
      return Boolean
     with Global => null;
   -- Data is the established arena; a different extent is refused.
   function Authenticated
     (Context : Prepared_History; Data : E.Bytes; Event, Prior_Event : E.Span)
      return Boolean
     with Global => null;
   function Direct_Authenticated
     (Context : Prepared_History; Data, Input_Data : E.Bytes;
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
   type Prepared_History is limited record
      State : History_State := Unestablished;
      Roster : E.Span := (1, 0);
      Events : E.Span := (1, 0);
      Replays : E.Span := (1, 0);
      Arena_First : E.Count := 1;
      Arena_Length : E.Count := 0;
      Arena_Digest : Attest.Custody_SHA256.Digest := (others => 0);
   end record;
end Worldline.Custody_V2_K4_Resource_Ack;
