with Interfaces;
with Worldline.Operation_Archive;
with Worldline.Chain_Authority;

-- Complete original ordinary append semantics; source custody stays with the
-- acquiring store/principal, never with an archive's matching digest.
package Worldline.Ordinary_Receipt_Policy with SPARK_Mode is
   package A renames Worldline.Operation_Archive;
   package E renames A.E;
   package H renames Worldline.Chain_Authority;
   type Action is (Owner_Request, Reserved_Claim, Event_Schema, Receipt_Schema,
                   Append_Preflight, Append_Postflight, History_Predecessor,
                   Route_Mutation, Verify_Retained_Columns, Append_Source_Postflight,
                   Receipt_Predecessor);
   type Reason is (Ready, Malformed_Input, Needs_Daemon_Account,
                   Reserved_Actor, Reserved_Kind, Invalid_Schema,
                   Invalid_Receipt, Requester_Mismatch, Receipt_Predecessor_Mismatch,
                   History_Invalid, Complete_Prefix_Changed, Actual_Write_Mismatch,
                   Peer_Observation_Required, Claim_Observation_Required,
                   Kind_Observation_Required, Captured_Predecessor_Mismatch,
                   Captured_Head_Mismatch, Ready_Mutating,
                   Truth_Observation_Required, Route_Observation_Mismatch,
                   Row_Columns_Mismatch, Schema_Observation_Required,
                   Ready_Authored, Receipt_Key_Observation_Required,
                   Receipt_Allowed_Keys_Required, Receipt_Keys_Required,
                   Receipt_Predecessor_Observation_Required);
   -- Original ordinary registration metadata is NOT the protected grant policy.
   -- The entire actual route roster and original field observations are decoded
   -- before either owner or mutation selection. Protocol truth is observed only
   -- at the original live __bool__/__len__ boundary, never in archived history.
   type Truth_Value is (Truth_Missing, Truth_False, Truth_True, Truth_Invalid);
   type Route_Observation is record
      Valid : Boolean := False;
      Name, Identity, Handler, Owner_Metadata, Mutation_Metadata : E.Span;
   end record;
   function Metadata_Truth (Data : E.Bytes; Value : E.Span) return Truth_Value
     with Global => null;
   function Schema_Status (Data : E.Bytes; Value : E.Span) return Reason
     with Global => null;
   type Requester_Source is (Ordinary_Source, Operation_Source, Owner_Source, Invalid_Source);
   function Requester_Profile (Data : E.Bytes; Value : E.Span)
      return Requester_Source with Global => null;
   function Receipt_Predecessor_Status (Data : E.Bytes; Source, Row : E.Span)
      return Reason with Global => null;
   function Receipt_Name_Status (Data : E.Bytes; Keys, Set_Observation : E.Span;
                                 Allow_Requester : Boolean) return Reason
     with Global => null;
   function Effect_Table_Schema (Data : E.Bytes; Source : E.Span; Kind : H.Chain_Kind)
      return Boolean with Global => null;
   function Native_Write_Matches (Data : E.Bytes; Packet, Current : E.Span;
                                   Kind : H.Chain_Kind) return Boolean
     with Global => null;
   function Actual_Route (Data : E.Bytes; Packet : E.Span)
      return Route_Observation with Global => null;
   type Verified_Column is (Event_Id_Column, World_Instance_Column, Kind_Column,
      Actor_Column, Tool_Column, Reason_Column, Path_B64_Column,
      Path_Display_Column, Line_Start_Column, Line_End_Column,
      Receipt_Id_Column, Transaction_Id_Column, Previous_Receipt_Column);
   function Column_Name (Column : Verified_Column) return String
     with Global => null;
   type Column_Result is record
      Status : Reason := Malformed_Input;
      Differences : Interfaces.Unsigned_32 := 0;
   end record;
   function Verify_History (Data : E.Bytes; Packet : E.Span)
      return Column_Result with Global => null;
   function Schema_One (Data : E.Bytes; Value : E.Span) return Boolean
     with Global => null;
   function Reserved_Actor_Name (Data : E.Bytes; Value : E.Span) return Boolean
     with Global => null;
   function Reserved_Kind_Name (Data : E.Bytes; Value : E.Span) return Boolean
     with Global => null;
   function Receipt_Fields (Data : E.Bytes; Value : E.Span;
                            Allow_Requester : Boolean) return Boolean
     with Global => null;
   function History (Data : E.Bytes; Rows : E.Span; Kind : H.Chain_Kind)
      return Boolean with Global => null;
   function Reference (Data : E.Bytes; Packet : E.Span; Mode : Action)
      return Reason with Global => null;
   function Decide (Data : E.Bytes; Packet : E.Span; Mode : Action)
      return Reason with Global => null,
       Post => Decide'Result = Reference (Data, Packet, Mode);
end Worldline.Ordinary_Receipt_Policy;
