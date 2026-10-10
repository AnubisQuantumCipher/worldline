with Worldline.Custody_V2_Typed_Step;
package Worldline.Custody_V2_History with SPARK_Mode is
   package D renames Worldline.Custody_V2_Typed_Step;
   package C renames D.C;
   package R renames D.A.R;
   package M renames D.M;
   package Q renames D.Q;
   use type Q.Byte_Count;
   use type C.Status;
   use type D.Decode_Status;
   use type M.Event_Record;
   use type M.Identity;
   use type M.Digest;
   use type R.Retained_Events;

   type Status is (Archive_Chain_Refused, Semantic_Event_Refused,
                  Authenticated_History_Genesis_JSON_And_Fold_Open);
   type Observation is record
      State : Status := Archive_Chain_Refused;
      Position : Q.Byte_Count := 0;
   end record;

   function Row_Matches
     (Data : C.E.Bytes; Key : C.E.Span; Raw : C.Event_Row;
      Previous : M.Digest; Item : R.Retained_Event) return Boolean is
     (D.Decode (Data, Raw).Status = D.Decoded and then
      Item.Event = D.Decode (Data, Raw).Value and then
      Item.Previous = Previous and then
      Item.Mac = C.G.Mac (Data, Key, Raw.Base_Archive) and then
      Item.Record_Bytes = M.Identity'(Present => True,
        Value => (Raw.Record_Archive.First, Raw.Record_Archive.Length)) and then
      Item.Base_Archive = M.Identity'(Present => True,
        Value => (Raw.Base_Archive.First, Raw.Base_Archive.Length)))
   with Global => null,
     Pre => C.E.C.P.Valid (Data, Key) and then
            C.E.C.P.Valid (Data, Raw.Base_Archive);

   -- Output storage bounds correspond exactly to the full raw event array.
   -- No authentication/readiness Boolean; the real archive verifier is called.
   -- Failure never exposes a partially decoded history to a Legal caller.
   procedure Materialize
     (Data : C.E.Bytes; Key, Genesis_Row, Genesis_Message,
      Genesis_Mac_Text : C.E.Span; Raw : C.Event_Rows; Heads : C.Head_Rows;
      History : in out R.Retained_Events; Result : out Observation)
   with Global => null, Always_Terminates,
     Pre => History'First = Raw'First and then History'Last = Raw'Last,
     Post =>
       (if Result.State /= Authenticated_History_Genesis_JSON_And_Fold_Open
        then History = History'Old
        else Result.Position = 0 and then
          C.Verify (Data, Key, Genesis_Row, Genesis_Message,
                    Genesis_Mac_Text, Raw, Heads).State =
            C.Archive_Chain_Matches_Genesis_JSON_And_Fold_Open and then
          (for all I in Raw'Range =>
            C.E.C.P.Valid (Data, Key) and then
            C.E.C.P.Valid (Data, Raw (I).Base_Archive) and then
            Row_Matches (Data, Key, Raw (I),
              (if I = Raw'First then C.G.Hash (Data, Genesis_Row)
               else History (I - 1).Event.Event_Id), History (I))));
end Worldline.Custody_V2_History;
