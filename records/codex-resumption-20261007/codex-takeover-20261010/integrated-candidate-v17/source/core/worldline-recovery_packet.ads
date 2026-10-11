with Worldline.Recovery_Archive;
with Worldline.Collapse_Wire;
with Interfaces;
package Worldline.Recovery_Packet with SPARK_Mode is
   package A renames Worldline.Recovery_Archive;
   package E renames A.E;
   package C renames Worldline.Collapse_Wire;
   type Status is
     (Malformed, Source_Conflict, Selection_Conflict, Agent_Conflict,
      Owner_Conflict, Native_Refused, Ready);
   -- Pointer-free references into the unchanged complete owned packet arena.
   -- Decode success is grammar only; it never grants historical custody.
   type Packet_View is record
      Valid, Has_Owner : Boolean := False;
      Values, Primary, Staged, Agent, Agent_Record, Inputs, Candidate,
        Subject, Witness, Authoritative_Requirement, Current_Requirement,
        Resulting_Requirement, Roots, Owner : E.Span := (1, 0);
   end record;
   type Result is record
      State : Status := Malformed;
      Collapse_Code : C.Byte := C.Invalid_Request;
      Owner_Code : Interfaces.Unsigned_32 := Interfaces.Unsigned_32'Last;
   end record;
   function Decode (Data : E.Bytes; Packet : E.Span) return Packet_View
     with Global => null;
   function Inspect (Data : E.Bytes; Packet : E.Span) return Result
     with Global => null;
   function Inspect
     (Data : E.Bytes; Packet : E.Span; Facts_Data : E.Bytes;
      Capsules : E.Span) return Result with Global => null;
   function Projection_Matches
     (Data : E.Bytes; Packet : E.Span; Expected_Data : E.Bytes;
      Expected_Values : E.Span) return Boolean with Global => null;
   -- Receipt material and runtime recovery call this exact same relation.
   -- Ready means native original collapse/owner conjunction and full packet
   -- source/rebuilt correspondence, never a protected-source custody claim.
   function Complete (Data : E.Bytes; Packet : E.Span) return Status
     with Global => null,
       Post => Complete'Result = Inspect (Data, Packet).State;
   -- Explicit private facts arena: no change to original raw packet framing.
   function Complete
     (Data : E.Bytes; Packet : E.Span; Facts_Data : E.Bytes;
      Capsules : E.Span) return Status
     with Global => null,
       Post => Complete'Result = Inspect (Data, Packet, Facts_Data, Capsules).State;
end Worldline.Recovery_Packet;
