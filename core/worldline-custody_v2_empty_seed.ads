with Worldline.Retained_Custody_Chain;

-- V5-J.3 empty authentication construction ONLY, not X4 Ready/Legal or an
-- owner provision capability. Genesis has no event or stored state rows.
package Worldline.Custody_V2_Empty_Seed with SPARK_Mode is
   package R renames Worldline.Retained_Custody_Chain;
   package S renames R.S;
   package E renames R.E;
   package SHA renames R.SHA;
   use type E.Count;
   use type SHA.Digest;
   type Status is (Invalid_Operands, Nonempty_State, Archive_Mismatch,
                   Origin_Mismatch, Constructed_Empty_Authentication);
   type Result is record
      State : Status := Invalid_Operands;
      Origin, Genesis_Mac, Head_Mac : SHA.Digest := (others => 0);
   end record;
   function Hash (Data : E.Bytes; Item : E.Span) return SHA.Digest
     with Global => null, Pre => E.C.P.Valid (Data, Item);
   -- Whole key and whole Q arena; literal v2 domain including zero byte.
   function Mac (Data : E.Bytes; Key, Message : E.Span) return SHA.Digest
     with Global => null,
       Pre => E.C.P.Valid (Data, Key) and then E.C.P.Valid (Data, Message);
   function Archives_Match
     (Data : E.Bytes; Genesis_Row, Genesis_Message, Head_Message : E.Span)
      return Boolean with Global => null;
   function Origin_Matches
     (Data : E.Bytes; Origin_Text : E.Span; Origin : SHA.Digest)
      return Boolean with Global => null;
   function Construct
     (Data : E.Bytes; Key, Genesis_Row, Genesis_Message,
      Head_Message, Origin_Text : E.Span;
      Event_Count, Alternative_Count, Root_Count, Subject_Count, Blob_Count : E.Count)
      return Result with Global => null,
      Post =>
       (if Construct'Result.State = Constructed_Empty_Authentication then
          E.C.P.Valid (Data, Key) and then E.C.P.Valid (Data, Genesis_Row) and then
          E.C.P.Valid (Data, Genesis_Message) and then E.C.P.Valid (Data, Head_Message) and then
          Event_Count = 0 and then Alternative_Count = 0 and then Root_Count = 0 and then
          Subject_Count = 0 and then Blob_Count = 0 and then
          Archives_Match (Data, Genesis_Row, Genesis_Message, Head_Message) and then
          Origin_Matches (Data, Origin_Text, Construct'Result.Origin) and then
          S.Text_Matches (Data, S.Field (Data, Head_Message, "head"), Origin_Text) and then
          Construct'Result.Origin = Hash (Data, Genesis_Row) and then
          Construct'Result.Genesis_Mac = Mac (Data, Key, Genesis_Message) and then
          Construct'Result.Head_Mac = Mac (Data, Key, Head_Message));
end Worldline.Custody_V2_Empty_Seed;
