with Ada.Characters.Latin_1;
with Canonical_Artifacts;
with Evaluation_History;
with Worldline.Archive_Base64;
with Worldline.Raw_JSON;
with Worldline.Producer_Values;
with Worldline.Operation_Archive;
with Worldline.Recovery_Archive;
with Worldline.Recovery_Material_Replay;
with Worldline.Recovery_Owner_Replay;
with Worldline.Recovery_Syntax;
with Worldline.Owner_Transitions;
with Worldline.Owner_Retry_Audit;
with Worldline.Owner_Conjunction;
with Worldline.Collapse_Wire;
with Worldline.Retained_Evidence_Replay;
with Worldline.Custody_V2_Domain_Hmac;
with Worldline.Custody_V2_Owner_Correspondence;
with Worldline.Custody_V2_Archive_Projection;
package body Worldline.Custody_V2_Owner_Canonical with SPARK_Mode is
   package V renames L.V;
   package S renames V.S;
   package OA renames Worldline.Operation_Archive;
   package RA renames Worldline.Recovery_Archive;
   package P renames Worldline.Producer_Values;
   package RJ renames Worldline.Raw_JSON;
   package B renames Worldline.Archive_Base64;
   package M renames Worldline.Recovery_Material_Replay;
   package O renames Worldline.Recovery_Owner_Replay;
   package X renames Worldline.Recovery_Syntax;
   package K renames Worldline.Owner_Transitions;
   package A renames Worldline.Owner_Retry_Audit;
   package C renames Worldline.Owner_Conjunction;
   package CW renames Worldline.Collapse_Wire;
   package J renames Canonical_Artifacts;
   package H renames Worldline.Custody_V2_Domain_Hmac;
   package EH renames Evaluation_History;
   package R renames Worldline.Retained_Evidence_Replay;
   use type E.Count;
   use type E.Value_Kind;
   use type E.Q.Byte;
   use type E.Bytes;
   use type H.C.SHA.Digest;
   use type P.Value_Kind;
   use type K.Decision;
   use type C.Decision;
   Domain : constant String := "worldline-protected-owner-transitions-v1" &
      Ada.Characters.Latin_1.NUL;
   Empty : constant E.Span := (1, 0);
   -- Literal fragments shared by a concatenation and its exact length guard.
   Gate_State : constant String := "/authority/gate/state/";
   UID_Open : constant String := "{""domain"":""linux.uid.v1"",""uid"":";
   UID_Close : constant String := "}";
   function Bytes (Text : String) return E.Bytes
     with Global => null,
       Post => Bytes'Result'First = 1 and then Bytes'Result'Length = E.Count (Text'Length)
   is
      Result : E.Bytes (1 .. Text'Length) := (others => 0);
   begin
      for I in Text'Range loop
         Result (E.Count (I - Text'First + 1)) := Character'Pos (Text (I));
      end loop;
      return Result;
   end Bytes;
   -- A String cannot hold more than Natural'Last characters; every caller
   -- refuses (or cannot reach) a larger operand where the original raised.
   function Text (Data : E.Bytes) return String
     with Global => null, Pre => Data'Length <= E.Count (Natural'Last),
       Post => Text'Result'First = 1 and then E.Count (Text'Result'Length) = Data'Length
   is
      Result : String (1 .. Data'Length) := (others => ' ');
   begin
      for I in Data'Range loop
         Result (Integer (I - Data'First + 1)) := Character'Val (Data (I));
      end loop;
      return Result;
   end Text;
   -- Identical for every arena whose lower bound is an index; an empty array
   -- whose lower bound lies below the index subtype (where the original
   -- aggregate raised) yields the empty span.
   function Whole (Data : E.Bytes) return E.Span is
     (if Data'First >= 1 then (Data'First, Data'Length) else Empty);
   function Raw_Same (LD, RD : E.Bytes; Left, Right : E.Span) return Boolean is
     (J.P.Valid (LD, Left) and then J.P.Valid (RD, Right) and then
      Left.Length = Right.Length and then
      (for all I in E.Count range 1 .. Left.Length =>
         LD (Left.First + (I - 1)) = RD (Right.First + (I - 1))));
   function Part (Data : E.Bytes; Item : P.Node) return E.Span
     with Global => null, Pre => Data'Length <= E.Count (Natural'Last),
       Post => J.P.Valid (Data, Part'Result)
   is
   begin
      if not P.Present (Item) or else Item.First < 1 or else
         Item.Last < Item.First or else Item.Last > Data'Length then return Empty; end if;
      return (Data'First + E.Count (Item.First - 1), E.Count (Item.Last - Item.First + 1));
   end Part;
   function JF (Raw : String; Parent : P.Node; Name : String) return P.Node is
     (P.Field (Raw, Parent, Name));
   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span
     renames RA.Field;
   function SF (Data : E.Bytes; Item : E.Span; Name : String) return E.Span
     renames S.Field;
   function Is_Text (Data : E.Bytes; Item : E.Span; Expected : String;
                     Layer : E.Layer := E.Recovery) return Boolean is
     (E.Text_Is (Data, E.Decode (Data, Item, Layer), Expected));
   function Text_Valid (Data : E.Bytes; Item : E.Span;
                        Layer : E.Layer := E.Recovery) return Boolean is
     (E.Decode (Data, Item, Layer).Form = E.Text_Value and then
      E.Bytes_Valid (Data, E.Decode (Data, Item, Layer).Payload));
   function Archive_Fits (Data : E.Bytes; Item : E.Span;
                          Layer : E.Layer := E.Recovery) return Boolean is
     (not Text_Valid (Data, Item, Layer) or else
      E.Materialize (Data, E.Decode (Data, Item, Layer).Payload)'Length <= E.Count (Natural'Last));
   function Archive_Text (Data : E.Bytes; Item : E.Span;
                          Layer : E.Layer := E.Recovery) return String
     with Global => null, Pre => Archive_Fits (Data, Item, Layer)
   is
   begin
      if not Text_Valid (Data, Item, Layer) then return ""; end if;
      return Text (E.Materialize (Data, E.Decode (Data, Item, Layer).Payload));
   end Archive_Text;
   function Hex (Sum : H.SHA.Digest) return E.Bytes
     with Global => null,
       Post => Hex'Result'First = 1 and then Hex'Result'Length = Sum'Length * 2
   is
      Hex_Digits : constant String := "0123456789abcdef";
      Result : E.Bytes (1 .. Sum'Length * 2) := (others => 0);
   begin
      for I in Sum'Range loop
         Result (E.Count (I - Sum'First) * 2 + 1) := Character'Pos (Hex_Digits (Integer (Sum (I) / 16) + 1));
         Result (E.Count (I - Sum'First) * 2 + 2) := Character'Pos (Hex_Digits (Integer (Sum (I) mod 16) + 1));
      end loop;
      return Result;
   end Hex;
   function Digest (Raw : E.Bytes; Item : E.Span) return E.Bytes is
     (Hex (H.C.G.Hash (Raw, Item)))
     with Pre => J.P.Valid (Raw, Item);
   function Digest_Is (Raw : String; Item : P.Node; Expected : E.Bytes) return Boolean is
     (P.Is_Text (Raw, Item, Text (Expected)))
     with Pre => Expected'Length <= E.Count (Natural'Last);
   function Object_Keys (Raw : String; Item : P.Node; Names : String;
                         Count : Natural) return Boolean
     with Global => null, Pre => Names'First >= 1 and then Names'Last < Positive'Last
   is
      Start : Positive := Names'First;
   begin
      if Item.Form /= P.Object_Value or else P.Count (Raw, Item) /= Count then return False; end if;
      for I in Names'Range loop
         pragma Loop_Invariant (Start in Names'First .. I);
         if Names (I) = ',' then
            if I = Start or else not P.Present (JF (Raw, Item, Names (Start .. I - 1))) then return False; end if;
            Start := I + 1;
         end if;
      end loop;
      return Start <= Names'Last and then P.Present (JF (Raw, Item, Names (Start .. Names'Last)));
   end Object_Keys;
   function Envelope (Key_Data, Raw : E.Bytes; Key : E.Span; Raw_Text : String;
                      Suffix : String := ""; Exact_Keys : Boolean := True) return Boolean
     with Global => null, Pre => Raw'Length <= E.Count (Natural'Last)
   is
      Root : constant P.Node := P.Parse (Raw_Text);
      Body_Node : constant P.Node := JF (Raw_Text, Root, "body");
   begin
      return J.P.Valid (Key_Data, Key) and then
         RJ.Canonical_ASCII_Valid (Raw_Text) and then
         (if Exact_Keys then Object_Keys (Raw_Text, Root, "body,mac", 2)
          else Root.Form = P.Object_Value and then P.Present (Body_Node) and then
             JF (Raw_Text, Root, "mac").Form = P.String_Value) and then
         J.P.Valid (Raw, Part (Raw, Body_Node)) and then
         Suffix'Length <= Natural'Last - Domain'Length and then
         Digest_Is (Raw_Text, JF (Raw_Text, Root, "mac"),
            Hex (H.Mac (Key_Data, Raw, Key, Part (Raw, Body_Node), Domain & Suffix)));
   end Envelope;
   function Decode_Record (Raw : String; Event : P.Node) return E.Bytes is
      Encoded : constant E.Bytes := Bytes (P.Text (Raw, JF (Raw, Event, "record")));
      Item : constant B.Span := (Encoded'First, Encoded'Length);
   begin
      if JF (Raw, Event, "record").Form /= P.String_Value or else
         not B.Canonical (Encoded, Item) then return E.Bytes'(1 .. 0 => 0); end if;
      declare Result : E.Bytes (1 .. B.Decoded_Length (Encoded, Item)); begin
         B.Decode (Encoded, Item, Result);
         return Result;
      end;
   end Decode_Record;
   function Record_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
      View : constant E.View := E.Decode (Data, Item, E.Recovery);
   begin
      return RA.Valid (Data, Item) and then View.Form = E.Object_Value and then
         E.Array_Length (Data, View.Children) = 3 and then
         E.Decode (Data, F (Data, Item, "base"), E.Recovery).Form = E.Object_Value and then
         RA.Record_Is (Data, F (Data, Item, "request"), "worldline.owner_transitions", "OwnerRequest") and then
         E.Decode (Data, F (Data, Item, "boundaries"), E.Recovery).Form = E.List_Value;
   end Record_Valid;
   function Request_Same_Except_State
     (LD, RD : E.Bytes; Left, Right : E.Span) return Boolean is
   begin
      return RA.Record_Is (LD, Left, "worldline.owner_transitions", "OwnerRequest") and then
         RA.Record_Is (RD, Right, "worldline.owner_transitions", "OwnerRequest") and then
         RA.Equal (LD, RD, F (LD, Left, "action"), F (RD, Right, "action")) and then
         RA.Equal (LD, RD, F (LD, Left, "peer"), F (RD, Right, "peer")) and then
         RA.Equal (LD, RD, F (LD, Left, "owner"), F (RD, Right, "owner")) and then
         RA.Equal (LD, RD, F (LD, Left, "trusted_issuer"), F (RD, Right, "trusted_issuer")) and then
         RA.Equal (LD, RD, F (LD, Left, "subject"), F (RD, Right, "subject")) and then
         RA.Equal (LD, RD, F (LD, Left, "content"), F (RD, Right, "content")) and then
         RA.Equal (LD, RD, F (LD, Left, "transaction"), F (RD, Right, "transaction")) and then
         RA.Equal (LD, RD, F (LD, Left, "current_requirement"), F (RD, Right, "current_requirement")) and then
         RA.Equal (LD, RD, F (LD, Left, "resulting_requirement"), F (RD, Right, "resulting_requirement")) and then
         RA.Equal (LD, RD, F (LD, Left, "current_head"), F (RD, Right, "current_head")) and then
         RA.Equal (LD, RD, F (LD, Left, "attempt"), F (RD, Right, "attempt")) and then
         RA.Equal (LD, RD, F (LD, Left, "current_epoch"), F (RD, Right, "current_epoch")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "action"),
            F (RD, F (RD, Right, "grant"), "action")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "grant"),
            F (RD, F (RD, Right, "grant"), "grant")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "use_id"),
            F (RD, F (RD, Right, "grant"), "use_id")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "issuer"),
            F (RD, F (RD, Right, "grant"), "issuer")) and then
                  RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "principal"),
            F (RD, F (RD, Right, "grant"), "principal")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "subject"),
            F (RD, F (RD, Right, "grant"), "subject")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "content"),
            F (RD, F (RD, Right, "grant"), "content")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "transaction"),
            F (RD, F (RD, Right, "grant"), "transaction")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "current_requirement"),
            F (RD, F (RD, Right, "grant"), "current_requirement")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "expected_requirement"),
            F (RD, F (RD, Right, "grant"), "expected_requirement")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "reason"),
            F (RD, F (RD, Right, "grant"), "reason")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "issued_grant"),
            F (RD, F (RD, Right, "grant"), "issued_grant")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "reserved_grant"),
            F (RD, F (RD, Right, "grant"), "reserved_grant")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "reserved_use"),
            F (RD, F (RD, Right, "grant"), "reserved_use")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "failed_run"),
            F (RD, F (RD, Right, "grant"), "failed_run")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "prior_head"),
            F (RD, F (RD, Right, "grant"), "prior_head")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "next_run"),
            F (RD, F (RD, Right, "grant"), "next_run")) and then
         RA.Equal (LD, RD, F (LD, F (LD, Left, "grant"), "epoch"),
            F (RD, F (RD, Right, "grant"), "epoch"));
   end Request_Same_Except_State;
   function Arena_Last (Data : E.Bytes; Size : E.Count; Extra : E.Count := 0) return E.Count is
   begin
      if Size = 0 or else Size < Data'Length or else Extra > E.Count'Last - Data'First or else
         Size - 1 > E.Count'Last - Data'First - Extra then return Data'First - 1; end if;
      return Data'First + (Size - 1) + Extra;
   end Arena_Last;
   function Reserved_Redecided
     (Data : E.Bytes; Record_Value : E.Span; Facts_Data : E.Bytes; Capsules : E.Span)
      return Boolean is
   begin
      -- An empty arena whose lower bound is not an index cannot bound the
      -- private arena below; the original raised in its elaboration.
      if Data'First < 1 then return False; end if;
      declare
      Base : constant E.Span := F (Data, Record_Value, "base");
      Material : constant E.Span := F (Data, Base, "before_material");
      Requirement : constant E.Span := F (Data, F (Data, Base, "current_requirement"), "requirementHash");
      Arena_Size : constant E.Count := M.Arena_Length (Data, Material);
      Arena : E.Bytes (Data'First .. Arena_Last (Data, Arena_Size)) := (others => 0);
      Rows : EH.History (1 .. M.Row_Count (Data, Material));
      Finalization : EH.Optional_Record;
      Current : EH.Optional_Cursor;
      Request : K.Request;
      Valid : Boolean;
      begin
      if not Record_Valid (Data, Record_Value) or else Arena_Size = 0 or else Arena'Length < Arena_Size then
         return False;
      end if;
      M.Classify_All (Data, Material, F (Data, Base, "world"), Requirement,
         Arena, Rows, Finalization, Current, Valid,
         Facts_Data => Facts_Data, Capsules => Capsules);
      O.Decode_Request (Data, F (Data, Record_Value, "request"), Arena, Valid, Request);
      return Valid and then K.Authorize (Arena, Rows, Finalization, Request) = K.Ready;
      end;
   end Reserved_Redecided;
   type Cause is (Invalid, Issued, Reserved, Dispatch_Intent, Observed,
      Consumed, Quarantine, Collapse_Intent, Collapse_Observed, Settled);
   function Event_Cause (Raw : String; Event : P.Node) return Cause is
      Word : constant String := P.Text (Raw, JF (Raw, Event, "cause"));
   begin
      for State in Issued .. Settled loop
         if Word = Cause'Image (State) then return State; end if;
      end loop;
      return Invalid;
   end Event_Cause;
   function Transition (Before, After : Cause) return Boolean is
     (case Before is
        when Issued => After in Reserved | Quarantine,
        when Reserved => After in Dispatch_Intent | Collapse_Intent | Quarantine,
        when Dispatch_Intent => After in Observed | Quarantine,
        when Observed => After in Consumed | Quarantine,
        when Quarantine => After in Observed | Quarantine,
        when Consumed => After = Collapse_Intent,
        when Collapse_Intent => After = Collapse_Observed,
        when Collapse_Observed => After = Settled,
        when Settled | Invalid => False);
   function Sequence (Data : E.Bytes; Item : E.Span) return Boolean is
     (E.Decode (Data, Item, E.Recovery).Form in E.List_Value | E.Tuple_Value);
   function Length (Data : E.Bytes; Item : E.Span) return E.Count is
     (E.Array_Length (Data, E.Decode (Data, Item, E.Recovery).Children));
   function Element (Data : E.Bytes; Item : E.Span; Ordinal : E.Count) return E.Span is
     (E.Array_Element (Data, E.Decode (Data, Item, E.Recovery).Children, Ordinal));
   function Boundary_Prefix (LD, RD : E.Bytes; Left, Right : E.Span)
      return Boolean is
   begin
      if not Sequence (LD, Left) or else not Sequence (RD, Right) or else
         Length (LD, Left) > Length (RD, Right) then return False; end if;
      for I in E.Count range 1 .. Length (LD, Left) loop
         if not RA.Equal (LD, RD, Element (LD, Left, I - 1), Element (RD, Right, I - 1)) then
            return False;
         end if;
      end loop;
      return True;
   end Boundary_Prefix;
   function Next_Record (LD, RD : E.Bytes; Old_Record, New_Record : E.Span;
                         After : Cause) return Boolean is
      Old_Request : constant E.Span := F (LD, Old_Record, "request");
      New_Request : constant E.Span := F (RD, New_Record, "request");
      Old_State : constant E.Span := F (LD, F (LD, Old_Request, "grant"), "state");
      New_State : constant E.Span := F (RD, F (RD, New_Request, "grant"), "state");
   begin
      return Raw_Same (LD, RD, F (LD, Old_Record, "base"), F (RD, New_Record, "base")) and then
         Boundary_Prefix (LD, RD, F (LD, Old_Record, "boundaries"), F (RD, New_Record, "boundaries")) and then
         Request_Same_Except_State (LD, RD, Old_Request, New_Request) and then
         (if After in Quarantine | Collapse_Intent | Collapse_Observed then
             RA.Equal (LD, RD, Old_State, New_State)
          elsif After in Reserved | Dispatch_Intent | Observed then
             Is_Text (RD, New_State, "RESERVED")
          else Is_Text (RD, New_State, "CONSUMED"));
   end Next_Record;
   function Context (Data : E.Bytes; Roster : E.Span) return E.Span is
     (SF (Data, Roster, "operation_context"));
   function Owner_Context (Data : E.Bytes; Roster : E.Span) return E.Span is
     (SF (Data, Context (Data, Roster), "owner_context"));
   function Extract_Replay_Capsules
     (Data : E.Bytes; Owner_Roster : E.Span) return E.Bytes is
      Item : constant E.Span := SF (Data, Owner_Context (Data, Owner_Roster), "native_replay_capsules_raw");
   begin
      if not V.Valid_Bytes (Data, Item) then
         return E.Bytes'(1 .. 0 => 0);
      end if;
      return V.Bytes_Value (Data, Item);
   end Extract_Replay_Capsules;
   function Replay_Capsules_Match
     (Data : E.Bytes; Roster : E.Span; Facts_Data : E.Bytes) return Boolean is
      Item : constant E.Span := SF (Data, Owner_Context (Data, Roster), "native_replay_capsules_raw");
   begin
      -- The existing original-image relation borrows the complete scoped
      -- hex-text/base64 leaf and raw operation archive without materializing
      -- another facts arena or revalidating base64 separately for every byte.
      return Worldline.Custody_V2_Archive_Projection.Scoped_Archive_Operation_Matches
        (Data, Facts_Data, Item, Whole (Facts_Data),
         Worldline.Custody_V2_Archive_Projection.Original_Image);
   end Replay_Capsules_Match;
   function Current (Data : E.Bytes; Roster : E.Span) return E.Span is
     (SF (Data, Roster, "current"));
   function Paths (Data : E.Bytes; Roster : E.Span) return E.Span is
     (SF (Data, Current (Data, Roster), "paths"));
   function Authority (Data : E.Bytes; Roster : E.Span) return E.Span is
     (SF (Data, SF (Data,
        SF (Data, Current (Data, Roster), "installation"), "paths"), "authority_root"));
   function Joined (Data : E.Bytes; Word, Root : E.Span; Suffix : String) return Boolean is
   begin
      if not V.Valid_Text (Data, Word) or else not V.Valid_Text (Data, Root) then return False; end if;
      declare W : constant E.Bytes := V.Text_Value (Data, Word);
              B : constant E.Bytes := V.Text_Value (Data, Root); begin
         return W'Length >= B'Length and then W'Length - B'Length = Suffix'Length and then
            (for all I in E.Count range 1 .. B'Length => W (W'First + (I - 1)) = B (B'First + (I - 1))) and then
            (for all I in Suffix'Range => W (W'First + B'Length + E.Count (I - Suffix'First)) =
               Character'Pos (Suffix (I)));
      end;
   end Joined;
   function Owned_File (Data : E.Bytes; Roster : E.Span; Suffix : String) return E.Span is
      Found : E.Span := Empty;
   begin
      for I in E.Count range 1 .. V.Count (Data, Paths (Data, Roster)) loop
         declare Path_Item : constant E.Span := V.Element (Data, Paths (Data, Roster), I - 1); begin
            if Joined (Data, SF (Data, Path_Item, "path"), Authority (Data, Roster), Suffix) then
               if Found.Length > 0 then return Empty; end if;
               Found := SF (Data, Path_Item, "raw");
            end if;
         end;
      end loop;
      return Found;
   end Owned_File;
   function Owner_File (Data : E.Bytes; Roster : E.Span; Name : String) return E.Span is
     (Owned_File (Data, Roster, Gate_State & Name))
     with Pre => Name'Length <= Natural'Last - Gate_State'Length;
   function Context_File_Matches (Data : E.Bytes; Roster : E.Span; Field, Name : String) return Boolean
     with Global => null, Pre => Name'Length <= Natural'Last - Gate_State'Length,
       Post => (if Context_File_Matches'Result then V.Valid_Bytes (Data, Owner_File (Data, Roster, Name)))
   is
      Supplied : constant E.Span := SF (Data, Owner_Context (Data, Roster), Field);
      Actual : constant E.Span := Owner_File (Data, Roster, Name);
   begin
      return V.Valid_Bytes (Data, Supplied) and then V.Valid_Bytes (Data, Actual) and then
         V.Bytes_Value (Data, Supplied) = V.Bytes_Value (Data, Actual);
   end Context_File_Matches;
   function Raw_File (Data : E.Bytes; Roster : E.Span; Name : String) return E.Bytes
     with Global => null, Pre => Name'Length <= Natural'Last - Gate_State'Length
   is
      Item : constant E.Span := Owner_File (Data, Roster, Name);
   begin
      if not V.Valid_Bytes (Data, Item) then return E.Bytes'(1 .. 0 => 0); end if;
      return V.Bytes_Value (Data, Item);
   end Raw_File;
   function Source_Raw (Data : E.Bytes; Roster : E.Span; Word : String) return E.Span is
      Sources : constant E.Span := SF (Data, Owner_Context (Data, Roster), "source_files");
      Found : E.Span := Empty;
   begin
      for I in E.Count range 1 .. V.Count (Data, Sources) loop
         declare Item : constant E.Span := V.Element (Data, Sources, I - 1); begin
            if S.Text_Is (Data, SF (Data, Item, "path"), Word) then
               if Found.Length > 0 then return Empty; end if;
               Found := SF (Data, Item, "raw");
            end if;
         end;
      end loop;
      return Found;
   end Source_Raw;
   function Source_Bytes_Match (Data : E.Bytes; Encoded : E.Span; Raw : E.Bytes) return Boolean is
      Hex_Digits : constant String := "0123456789abcdef";
   begin
      if not V.Valid_Text (Data, Encoded) or else Raw'Length > E.Count'Last / 2 then return False; end if;
      declare Word : constant E.Bytes := V.Text_Value (Data, Encoded); begin
         if Word'Length /= Raw'Length * 2 then return False; end if;
         for I in E.Count range 1 .. Raw'Length loop
            if Word (Word'First + (I - 1) * 2) /=
                 Character'Pos (Hex_Digits (Natural (Raw (Raw'First + (I - 1)) / 16) + 1)) or else
               Word (Word'First + (I - 1) * 2 + 1) /=
                 Character'Pos (Hex_Digits (Natural (Raw (Raw'First + (I - 1)) mod 16) + 1)) then return False; end if;
         end loop;
         return True;
      end;
   end Source_Bytes_Match;
   function Run_Service_Source (Data : E.Bytes; Roster : E.Span) return E.Span is
      Events : constant E.Span := SF (Data, SF (Data, Current (Data, Roster), "source"), "events");
      Found : E.Span := Empty;
   begin
      if not V.Is_Sequence (Data, Events) then return Empty; end if;
      for I in E.Count range 1 .. V.Count (Data, Events) loop
         declare
            Event : constant E.Span := V.Element (Data, Events, I - 1);
            Path : constant E.Span := SF (Data, Event, "path");
         begin
            if S.Text_Is (Data, SF (Data, Event, "module"), "run_service") then
               if not V.Valid_Text (Data, Path) or else
                  not (S.Text_Is (Data, SF (Data, Event, "kind"), "SOURCE_COMPILED_BEFORE_EXEC") or else
                       S.Text_Is (Data, SF (Data, Event, "kind"), "INITIAL_SOURCE_CANDIDATES")) or else
                  (Found.Length > 0 and then not S.A.Same_Encoding (Data, Found, Path)) or else
                  V.Text_Value (Data, Path)'Length > E.Count (Natural'Last) then return Empty; end if;
               declare
                  Owned : constant E.Span := Source_Raw (Data, Roster, Text (V.Text_Value (Data, Path)));
               begin
                  if not V.Valid_Bytes (Data, Owned) then return Empty; end if;
                  declare Raw : constant E.Bytes := V.Bytes_Value (Data, Owned); begin
                     if not Source_Bytes_Match (Data, SF (Data, Event, "source_bytes_hex"), Raw) then
                        return Empty;
                     end if;
                  end;
               end;
               Found := Path;
            end if;
         end;
      end loop;
      return Found;
   end Run_Service_Source;
   function Policy_Sources (Data : E.Bytes; Roster : E.Span; Raw : String; Policy : P.Node) return Boolean is
      Sources : constant P.Node := JF (Raw, Policy, "sources");
      Native : constant E.Span := SF (Data, Owner_Context (Data, Roster), "native_path");
      Installation : constant E.Span := SF (Data, Current (Data, Roster), "installation");
      Runtime : constant E.Span := SF (Data, Installation, "runtime");
      Source_Root : constant E.Span := SF (Data, Runtime, "worldline_source");
      Gate_Source : constant E.Span := SF (Data, Runtime, "gate_source");
      Required : constant String := "protected_owner.py,owner_retry_audit.py,owner_transitions.py,owner_collapse_data.py,owner_intent_endpoint.py,transaction.py,evaluation_authority.py,evaluation_writer.py,revalidate.py,recovery_observation.py,protected_recovery_capture.py,protected_owner_bootstrap.py";
      Start : Positive := Required'First;
      Run_Service : constant E.Span := Run_Service_Source (Data, Roster);
      Runtime_Tree : constant String := "/runtime/worldline/";
      -- Refuses exactly the operands whose path the original could not build.
      function Required_Source (Leaf : String) return Boolean is
        (Leaf'Length <= Natural'Last - Runtime_Tree'Length and then
         V.Text_Value (Data, Source_Root)'Length <=
           E.Count (Natural'Last - Runtime_Tree'Length - Leaf'Length) and then
         P.Present (JF (Raw, Sources, Text (V.Text_Value (Data, Source_Root)) &
           Runtime_Tree & Leaf)))
        with Pre => V.Valid_Text (Data, Source_Root);
   begin
      if Sources.Form /= P.Object_Value or else P.Count (Raw, Sources) = 0 or else
         not V.Valid_Text (Data, Native) or else
         not V.Valid_Text (Data, Source_Root) or else not V.Valid_Text (Data, Gate_Source) or else
         not V.Valid_Text (Data, Run_Service) or else
         not S.A.Same_Encoding (Data, Native, SF (Data, Runtime, "native_library")) or else
         V.Text_Value (Data, Gate_Source)'Length > E.Count (Natural'Last) or else
         not P.Present (JF (Raw, Sources, Text (V.Text_Value (Data, Gate_Source)))) or else
         V.Text_Value (Data, Run_Service)'Length > E.Count (Natural'Last) or else
         not P.Present (JF (Raw, Sources, Text (V.Text_Value (Data, Run_Service)))) then return False; end if;
      for I in Required'Range loop
         if Required (I) = ',' then
            if not Required_Source (Required (Start .. I - 1)) then return False; end if;
            Start := I + 1;
         end if;
      end loop;
      if not Required_Source (Required (Start .. Required'Last)) then return False; end if;
      if V.Text_Value (Data, Native)'Length > E.Count (Natural'Last) then return False; end if;
      for I in 1 .. P.Count (Raw, Sources) loop
         declare
            Word : constant String := P.Member_Name (Raw, Sources, I);
            Owned : constant E.Span := Source_Raw (Data, Roster, Word);
         begin
            if not V.Valid_Bytes (Data, Owned) then return False; end if;
            declare Bytes : constant E.Bytes := V.Bytes_Value (Data, Owned); begin
               if not Digest_Is (Raw, JF (Raw, Sources, Word), Digest (Bytes, Whole (Bytes))) then return False; end if;
            end;
         end;
      end loop;
      declare Owned : constant E.Span := Source_Raw (Data, Roster, Text (V.Text_Value (Data, Native))); begin
         if not V.Valid_Bytes (Data, Owned) then return False; end if;
         declare Bytes : constant E.Bytes := V.Bytes_Value (Data, Owned); begin
            return Digest_Is (Raw, JF (Raw, Policy, "native_sha256"), Digest (Bytes, Whole (Bytes)));
         end;
      end;
   end Policy_Sources;
   function Policy_Binding_Matches
     (Raw : E.Bytes; Raw_Text : String; Policy : P.Node; Data : E.Bytes; Binding : E.Span;
      Scoped : Boolean) return Boolean
     with Global => null, Pre => Raw'Length <= E.Count (Natural'Last)
   is
      Names : constant String := "installation_id,owner_issuer_id,owner_uid,gate_config_sha256,issuer_policy_sha256,issuer_key_sha256,store_genesis,native_sha256";
      Start : Positive := Names'First;
      function Field (Name : String) return E.Span is
      begin
         if Scoped then
            return SF (Data, Binding, Name);
         else
            return OA.Field (Data, Binding, Name);
         end if;
      end Field;
      function Matches (Name : String) return Boolean is
        (if Scoped then RJ.Raw_JSON_Scoped_Equal (Raw, Data, Part (Raw, JF (Raw_Text, Policy, Name)), Field (Name))
         else RJ.Raw_JSON_Operation_Equal (Raw, Data, Part (Raw, JF (Raw_Text, Policy, Name)), Field (Name)))
        with Pre => Raw'Length <= E.Count (Natural'Last);
   begin
      if (if Scoped then not S.Valid (Data, Binding) or else S.Member_Count (Data, Binding) /= 9
          else not OA.Valid (Data, Binding) or else
             E.Decode (Data, Binding, E.Operation).Form /= E.Object_Value or else
             E.Array_Length (Data, E.Decode (Data, Binding, E.Operation).Children) /= 9) then return False; end if;
      for I in Names'Range loop
         if Names (I) = ',' then
            if not Matches (Names (Start .. I - 1)) then return False; end if;
            Start := I + 1;
         end if;
      end loop;
      if not Matches (Names (Start .. Names'Last)) then return False; end if;
      return (if Scoped then S.Text_Is (Data, Field ("policy_sha256"), Text (Digest (Raw, Whole (Raw))))
              else Is_Text (Data, Field ("policy_sha256"), Text (Digest (Raw, Whole (Raw))), E.Operation));
   end Policy_Binding_Matches;
   function Head_Matches (Key, Raw_Journal, Raw_Head : E.Bytes; Binding_Data : E.Bytes;
                          Binding : E.Span; Last : E.Bytes;
                          Exact_Keys : Boolean := True) return Boolean
     with Global => null,
       Pre => Raw_Head'Length <= E.Count (Natural'Last) and then Last'Length <= E.Count (Natural'Last)
   is
      Head_Text : constant String := Text (Raw_Head);
      Root : constant P.Node := P.Parse (Head_Text);
      Body_Node : constant P.Node := JF (Head_Text, Root, "body");
   begin
      return Envelope (Key, Raw_Head, Whole (Key), Head_Text, Exact_Keys => Exact_Keys) and then
         Object_Keys (Head_Text, Body_Node, "schema,binding,event_head,journal_sha256", 4) and then
         P.Is_Text (Head_Text, JF (Head_Text, Body_Node, "schema"), "worldline.protected-owner-head-v1") and then
         RJ.Raw_JSON_Scoped_Equal (Raw_Head, Binding_Data, Part (Raw_Head, JF (Head_Text, Body_Node, "binding")), Binding) and then
         Digest_Is (Head_Text, JF (Head_Text, Body_Node, "event_head"), Last) and then
         Digest_Is (Head_Text, JF (Head_Text, Body_Node, "journal_sha256"), Digest (Raw_Journal, Whole (Raw_Journal)));
   end Head_Matches;
   function History
     (Raw : E.Bytes; Raw_Text, Owner, Issuer : String; Facts_Data : E.Bytes;
      Capsules : E.Span) return Boolean
     with Global => null, Pre => Raw'Length <= E.Count (Natural'Last)
   is
      Root : constant P.Node := P.Parse (Raw_Text);
      Body_Node : constant P.Node := JF (Raw_Text, Root, "body");
      Events : constant P.Node := JF (Raw_Text, Body_Node, "events");
      Prior : E.Bytes (1 .. 64) := (others => 0);
   begin
      if not Object_Keys (Raw_Text, Body_Node, "schema,binding,events", 3) or else
         not P.Is_Text (Raw_Text, JF (Raw_Text, Body_Node, "schema"), "worldline.protected-owner-journal-v1") or else
         Events.Form /= P.Array_Value then return False; end if;
      for I in 1 .. P.Count (Raw_Text, Events) loop
         declare
            Event : constant P.Node := P.Element (Raw_Text, Events, I);
            State : constant Cause := Event_Cause (Raw_Text, Event);
            Record_Data : constant E.Bytes := Decode_Record (Raw_Text, Event);
            Record_Value : constant E.Span := Whole (Record_Data);
            Base : constant E.Span := F (Record_Data, Record_Value, "base");
            Request : constant E.Span := F (Record_Data, Record_Value, "request");
            Bounds : constant E.Span := F (Record_Data, Record_Value, "boundaries");
            Intent : constant E.Span := F (Record_Data, Base, "intent");
            Old : P.Node := P.No_Node;
         begin
            if not Object_Keys (Raw_Text, Event, "prior,cause,intent,record", 4) or else State = Invalid or else
               (if I = 1 then not P.Is_Text (Raw_Text, JF (Raw_Text, Event, "prior"), "GENESIS")
                else not Digest_Is (Raw_Text, JF (Raw_Text, Event, "prior"), Prior)) or else
               not Record_Valid (Record_Data, Record_Value) or else
               not Text_Valid (Record_Data, Intent) or else not Archive_Fits (Record_Data, Intent) or else
               not P.Is_Text (Raw_Text, JF (Raw_Text, Event, "intent"), Archive_Text (Record_Data, Intent)) or else
               not RA.Record_Is (Record_Data, Request, "worldline.owner_transitions", "OwnerRequest") or else
               not RA.Equal (Record_Data, Record_Data, F (Record_Data, Request, "peer"), F (Record_Data, Base, "principal")) or else
               not Is_Text (Record_Data, F (Record_Data, Request, "owner"), Owner) or else
               not Is_Text (Record_Data, F (Record_Data, Request, "trusted_issuer"), Issuer) then return False; end if;
            for J in reverse 1 .. I - 1 loop
               declare Candidate : constant P.Node := P.Element (Raw_Text, Events, J); begin
                  if P.Equal (Raw_Text, JF (Raw_Text, Candidate, "intent"), Raw_Text, JF (Raw_Text, Event, "intent")) then
                     Old := Candidate; exit;
                  end if;
               end;
            end loop;
            if not P.Present (Old) then
               if State /= Issued or else not Is_Text (Record_Data, F (Record_Data,
                  F (Record_Data, Request, "grant"), "state"), "ISSUED") or else
                  E.Decode (Record_Data, Bounds, E.Recovery).Form /= E.List_Value or else Length (Record_Data, Bounds) /= 0 then return False; end if;
            else
               declare Old_Data : constant E.Bytes := Decode_Record (Raw_Text, Old); begin
                  if not Transition (Event_Cause (Raw_Text, Old), State) or else
                     not Next_Record (Old_Data, Record_Data, Whole (Old_Data), Record_Value, State) then return False; end if;
               end;
            end if;
            if State = Reserved and then
               not Reserved_Redecided (Record_Data, Record_Value, Facts_Data, Capsules) then return False; end if;
            Prior := Digest (Raw, Part (Raw, Event));
            if State = Settled and then Is_Text (Record_Data, F (Record_Data, Request, "action"), "ADOPT_REQUIREMENT") and then
               not Adopt_Settled_Redecided (Record_Data, Record_Value, Prior, Facts_Data, Capsules) then return False; end if;
         end;
      end loop;
      return True;
   end History;
   function Adopt_Settled_Redecided
     (Data : E.Bytes; Record_Value : E.Span; Event_Digest, Facts_Data : E.Bytes;
      Capsules : E.Span)
      return Boolean is
      Base : constant E.Span := F (Data, Record_Value, "base");
      Bounds : constant E.Span := F (Data, Record_Value, "boundaries");
      Effect : E.Span := Empty;
      Effect_Count : E.Count := 0;
   begin
      -- Data'First < 1: the original raised at the private arena's bounds.
      if not Record_Valid (Data, Record_Value) or else not Sequence (Data, Bounds) or else
         Length (Data, Bounds) = 0 or else Event_Digest'Length /= 64 or else Data'First < 1 then return False; end if;
      declare Boundary : constant E.Span := Element (Data, Bounds, Length (Data, Bounds) - 1); begin
         if not Is_Text (Data, F (Data, Boundary, "name"), "OWNER_ADOPT_USE_CONSUMED") then return False; end if;
         for I in E.Count range 1 .. Length (Data, Bounds) loop
            pragma Loop_Invariant (Effect_Count < I);
            declare Item : constant E.Span := Element (Data, Bounds, I - 1); begin
               if Is_Text (Data, F (Data, Item, "name"), "OWNER_COLLAPSE_EFFECT_INTENT") then
                  Effect_Count := Effect_Count + 1;
                  Effect := F (Data, Item, "capture");
               end if;
            end;
         end loop;
         if Effect_Count /= 1 then return False; end if;
         declare
            Binding : constant E.Span := F (Data, Effect, "owner_binding");
            Owner : constant E.Span := F (Data, Binding, "owner");
            Events : constant E.Span := F (Data, Binding, "events");
            Issued_Event, Reserved_Event : E.Span := Empty;
            Packet_Field : constant E.Span := F (Data, Effect, "packet");
         begin
            if E.Decode (Data, Effect, E.Recovery).Form /= E.Object_Value or else
               E.Decode (Data, Binding, E.Recovery).Form /= E.Object_Value or else
               not RA.Record_Is (Data, Owner, "worldline.owner_collapse_data", "OwnerCollapseData") or else
               not Sequence (Data, Events) or else not RA.Stored_Bytes_Valid (Data, Packet_Field) then return False; end if;
            -- Original next(...cause...) picks the first retained issue/reserve.
            -- Do not replace this complete archive with current policy material.
            for I in E.Count range 1 .. Length (Data, Events) loop
               declare Item : constant E.Span := Element (Data, Events, I - 1); begin
                  if Issued_Event.Length = 0 and then Is_Text (Data, F (Data, Item, "cause"), "ISSUED") then
                     Issued_Event := Item;
                  end if;
                  if Reserved_Event.Length = 0 and then Is_Text (Data, F (Data, Item, "cause"), "RESERVED") then
                     Reserved_Event := Item;
                  end if;
               end;
            end loop;
            if Issued_Event.Length = 0 or else Reserved_Event.Length = 0 or else
               not M.JSON_Valid (Data, Issued_Event, E.Recovery, True) or else
               not M.JSON_Valid (Data, Reserved_Event, E.Recovery, True) then return False; end if;
            declare
               Issue_JSON : constant E.Bytes := Bytes (M.JSON (Data, Issued_Event, E.Recovery, True));
               Reserve_JSON : constant E.Bytes := Bytes (M.JSON (Data, Reserved_Event, E.Recovery, True));
               Issue_Id : constant E.Bytes := Digest (Issue_JSON, Whole (Issue_JSON));
               Reserve_Id : constant E.Bytes := Digest (Reserve_JSON, Whole (Reserve_JSON));
               Packet : constant E.Bytes := RA.Stored_Bytes (Data, Packet_Field);
               Values : constant R.Collapse_Values_Result := R.Decode_Recovery_Collapse_Values
                  (Packet, RA.Field (Packet, Whole (Packet), "values"));
               Material : constant E.Span := F (Data, Base, "before_material");
               Requirement : constant E.Span := F (Data, F (Data, Base, "current_requirement"), "requirementHash");
               Arena_Size : constant E.Count := M.Arena_Length (Data, Material);
               Rows : EH.History (1 .. M.Row_Count (Data, Material));
               Finalization : EH.Optional_Record;
               Current : EH.Optional_Cursor;
               Arena : E.Bytes (Data'First .. Arena_Last (Data, Arena_Size, 192)) := (others => 0);
               Before, Consumed_Request : K.Request;
               Scope : C.Full_Scope;
               Resulting : CW.Raw_Optional_Hash;
               Epoch : EH.Optional_Epoch;
               Consumed_Issue, Consumed_Reservation : K.Optional_Identity;
               Valid : Boolean;
            begin
               if not RA.Valid (Packet, Whole (Packet)) or else not Values.Present or else Arena_Size = 0 or else
                  Arena'Length < Arena_Size or else Arena'Length - Arena_Size /= 192 then return False; end if;
               M.Classify_All (Data, Material, F (Data, Base, "world"), Requirement,
                  Arena, Rows, Finalization, Current, Valid,
                  Facts_Data => Facts_Data, Capsules => Capsules);
               O.Decode_Request (Data, F (Data, Owner, "request"), Arena, Valid, Before);
               O.Decode_Request (Data, F (Data, Record_Value, "request"), Arena, Valid, Consumed_Request);
               O.Decode_Scope (Data, F (Data, Owner, "scope"), Arena, Valid, Scope);
               O.Decode_Epoch (Data, F (Data, Owner, "current_epoch"), Arena, Valid, Epoch);
               O.Decode_Hash (Data, F (Data, Owner, "resulting"), Valid, Resulting);
               O.Decode_Identity (Data, F (Data, Boundary, "issued_event"), Arena, Valid, Consumed_Issue);
               O.Decode_Identity (Data, F (Data, Boundary, "reserved_event"), Arena, Valid, Consumed_Reservation);
               -- Decode's precondition was an unguarded raise in the original.
               if not Valid or else not CW.Well_Formed (Values.Raw) then return False; end if;
               declare
                  First : constant E.Count := Data'First + Arena_Size;
                  Audit : constant A.Audit :=
                    (Before_Request => Before,
                     Receipt => (Consumed => Consumed_Request.Grant,
                        Issued_Event => (True, (First, 64)),
                        Reserved_Event => (True, (First + 64, 64)),
                        Consumed_Event => (True, (First + 128, 64)),
                        Consumed_Issue => Consumed_Issue,
                        Consumed_Reservation => Consumed_Reservation),
                     Current_Head => (Present => False),
                     Prepared_Evidence => (Present => False), Current_Epoch => Epoch);
               begin
                  Arena (First .. First + 63) := Issue_Id;
                  Arena (First + 64 .. First + 127) := Reserve_Id;
                  Arena (First + 128 .. First + 191) := Event_Digest;
                  return C.Authorize_Adopt_Receipt (Arena, Rows, Finalization,
                     CW.Decode (Values.Raw), CW.Requirement (Resulting), Scope, Audit) = C.Ready;
               end;
            end;
         end;
      end;
   end Adopt_Settled_Redecided;
   function Genesis_Matches
     (Data : E.Bytes; Roster : E.Span; Key, Raw, Policy_Raw : E.Bytes;
      Policy_Text : String; Policy : P.Node) return Boolean
     with Global => null, Pre => Raw'Length <= E.Count (Natural'Last)
   is
      Raw_Text : constant String := Text (Raw);
      Root : constant P.Node := P.Parse (Raw_Text);
      Body_Node : constant P.Node := JF (Raw_Text, Root, "body");
      Binding : constant E.Span := SF (Data, Context (Data, Roster), "owner_binding");
      Lease_Raw : constant E.Span := SF (Data, Context (Data, Roster), "lease_genesis_raw");
      Lease : constant E.Span := SF (Data, Context (Data, Roster), "lease_genesis");
   begin
      if not Envelope (Key, Raw, Whole (Key), Raw_Text, "genesis" & Ada.Characters.Latin_1.NUL) or else
         not Object_Keys (Raw_Text, Body_Node,
            "schema,binding,installation_genesis_sha256,gate_head,issuer_head,store_head,resource_genesis,journal_sha256,head_sha256", 9) or else
         not P.Is_Text (Raw_Text, JF (Raw_Text, Body_Node, "schema"), "worldline.protected-owner-genesis-v1") or else
         not RJ.Raw_JSON_Scoped_Equal (Raw, Data, Part (Raw, JF (Raw_Text, Body_Node, "binding")), Binding) or else
         not V.Valid_Bytes (Data, Lease_Raw) then return False; end if;
      declare Lease_Bytes : constant E.Bytes := V.Bytes_Value (Data, Lease_Raw); begin
         if not Digest_Is (Raw_Text, JF (Raw_Text, Body_Node, "installation_genesis_sha256"), Digest (Lease_Bytes, Whole (Lease_Bytes))) or else
            not RJ.Raw_JSON_Scoped_Matches (Lease_Bytes, Data, Whole (Lease_Bytes), Lease) or else
            not RJ.Raw_JSON_Scoped_Equal (Raw, Data, Part (Raw, JF (Raw_Text, Body_Node, "gate_head")), SF (Data, Lease, "gate_head")) or else
            not RJ.Raw_JSON_Scoped_Equal (Raw, Data, Part (Raw, JF (Raw_Text, Body_Node, "issuer_head")), SF (Data, Lease, "issuer_head")) or else
            not RJ.Raw_JSON_Scoped_Equal (Raw, Data, Part (Raw, JF (Raw_Text, Body_Node, "store_head")), SF (Data, SF (Data, Lease, "store"), "initial_head")) or else
            not RJ.Raw_JSON_Scoped_Equal (Raw, Data, Part (Raw, JF (Raw_Text, Body_Node, "resource_genesis")), SF (Data, Context (Data, Roster), "resource_genesis")) then return False; end if;
      end;
      declare
         -- Initial bytes are constructed from the actual policy-derived
         -- binding, not the semantically equal genesis JSON spelling.
         -- Operands and literal fragments are hoisted unchanged, so that the
         -- construction and its exact length guard share the same terms.
         Gate_Config : constant String := P.Slice (Policy_Text, JF (Policy_Text, Policy, "gate_config_sha256"));
         Installation_Id : constant String := P.Slice (Policy_Text, JF (Policy_Text, Policy, "installation_id"));
         Issuer_Key : constant String := P.Slice (Policy_Text, JF (Policy_Text, Policy, "issuer_key_sha256"));
         Issuer_Policy : constant String := P.Slice (Policy_Text, JF (Policy_Text, Policy, "issuer_policy_sha256"));
         Native_Sum : constant String := P.Slice (Policy_Text, JF (Policy_Text, Policy, "native_sha256"));
         Owner_Issuer : constant String := P.Slice (Policy_Text, JF (Policy_Text, Policy, "owner_issuer_id"));
         Owner_UID : constant String := P.Slice (Policy_Text, JF (Policy_Text, Policy, "owner_uid"));
         Policy_Sum : constant String := Text (Digest (Policy_Raw, Whole (Policy_Raw)));
         Store_Genesis : constant String := P.Slice (Policy_Text, JF (Policy_Text, Policy, "store_genesis"));
         K_Gate : constant String := "{""gate_config_sha256"":";
         K_Installation : constant String := ",""installation_id"":";
         K_Issuer_Key : constant String := ",""issuer_key_sha256"":";
         K_Issuer_Policy : constant String := ",""issuer_policy_sha256"":";
         K_Native : constant String := ",""native_sha256"":";
         K_Owner_Issuer : constant String := ",""owner_issuer_id"":";
         K_Owner_UID : constant String := ",""owner_uid"":";
         K_Policy : constant String := ",""policy_sha256"":""";
         K_Store : constant String := """,""store_genesis"":";
         K_Close : constant String := "}";
         K_Binding : constant String := "{""binding"":";
         K_Journal : constant String := ",""events"":[],""schema"":""worldline.protected-owner-journal-v1""}";
         K_Head : constant String := ",""event_head"":""GENESIS"",""journal_sha256"":""";
         K_Head_Schema : constant String := """,""schema"":""worldline.protected-owner-head-v1""}";
         K_Body : constant String := "{""body"":";
         K_Mac : constant String := ",""mac"":""";
         K_End : constant String := """}" & Ada.Characters.Latin_1.LF;
         Binding_Length : constant E.Count :=
            E.Count (K_Gate'Length) + E.Count (Gate_Config'Length) +
            E.Count (K_Installation'Length) + E.Count (Installation_Id'Length) +
            E.Count (K_Issuer_Key'Length) + E.Count (Issuer_Key'Length) +
            E.Count (K_Issuer_Policy'Length) + E.Count (Issuer_Policy'Length) +
            E.Count (K_Native'Length) + E.Count (Native_Sum'Length) +
            E.Count (K_Owner_Issuer'Length) + E.Count (Owner_Issuer'Length) +
            E.Count (K_Owner_UID'Length) + E.Count (Owner_UID'Length) +
            E.Count (K_Policy'Length) + E.Count (Policy_Sum'Length) +
            E.Count (K_Store'Length) + E.Count (Store_Genesis'Length) + E.Count (K_Close'Length);
         Hex_Length : constant E.Count := E.Count (H.SHA.Digest'Length) * 2;
         -- Every other concatenation below is a prefix of one of these two.
         Initial_Length : constant E.Count :=
            E.Count (K_Body'Length) + E.Count (K_Binding'Length) + Binding_Length +
            E.Count (K_Journal'Length) + E.Count (K_Mac'Length) + Hex_Length + E.Count (K_End'Length);
         Head_Length : constant E.Count :=
            E.Count (K_Body'Length) + E.Count (K_Binding'Length) + Binding_Length +
            E.Count (K_Head'Length) + Hex_Length + E.Count (K_Head_Schema'Length) +
            E.Count (K_Mac'Length) + Hex_Length + E.Count (K_End'Length);
         Bootstrap : constant E.Bytes := Raw_File (Data, Roster, "owner-bootstrap.json");
      begin
         -- Exactly the operands on which the original construction raised.
         if Initial_Length > E.Count (Natural'Last) or else Head_Length > E.Count (Natural'Last) or else
            Bootstrap'Length > E.Count (Natural'Last) then return False; end if;
      declare
         Binding_JSON : constant String := K_Gate & Gate_Config &
            K_Installation & Installation_Id & K_Issuer_Key & Issuer_Key &
            K_Issuer_Policy & Issuer_Policy & K_Native & Native_Sum &
            K_Owner_Issuer & Owner_Issuer & K_Owner_UID & Owner_UID &
            K_Policy & Policy_Sum & K_Store & Store_Genesis & K_Close;
         Initial_Body : constant E.Bytes := Bytes (K_Binding & Binding_JSON & K_Journal);
         Initial : constant E.Bytes := Bytes (K_Body & Text (Initial_Body) & K_Mac &
            Text (Hex (H.Mac (Key, Initial_Body, Whole (Key), Whole (Initial_Body), Domain))) & K_End);
         Head_Body : constant E.Bytes := Bytes (K_Binding & Binding_JSON &
            K_Head & Text (Digest (Initial, Whole (Initial))) & K_Head_Schema);
         Initial_Head : constant E.Bytes := Bytes (K_Body & Text (Head_Body) & K_Mac &
            Text (Hex (H.Mac (Key, Head_Body, Whole (Key), Whole (Head_Body), Domain))) & K_End);
         Bootstrap_Text : constant String := Text (Bootstrap);
         Admission : constant P.Node := JF (Bootstrap_Text, P.Parse (Bootstrap_Text), "body");
         Events : constant P.Node := JF (Bootstrap_Text, Admission, "events");
         Event : constant P.Node := P.Element (Bootstrap_Text, Events, 1);
         Genesis_Id : constant E.Bytes := Digest (Raw, Whole (Raw));
      begin
         return Digest_Is (Raw_Text, JF (Raw_Text, Body_Node, "journal_sha256"), Digest (Initial, Whole (Initial))) and then
            Digest_Is (Raw_Text, JF (Raw_Text, Body_Node, "head_sha256"), Digest (Initial_Head, Whole (Initial_Head))) and then
                        Envelope (Key, Bootstrap, Whole (Key), Bootstrap_Text, "bootstrap" & Ada.Characters.Latin_1.NUL) and then
            Object_Keys (Bootstrap_Text, Admission, "schema,genesis_sha256,binding,state,events", 5) and then
            P.Is_Text (Bootstrap_Text, JF (Bootstrap_Text, Admission, "schema"), "worldline.owner-bootstrap-admission-v1") and then
            Digest_Is (Bootstrap_Text, JF (Bootstrap_Text, Admission, "genesis_sha256"), Genesis_Id) and then
            RJ.Raw_JSON_Scoped_Equal (Bootstrap, Data, Part (Bootstrap, JF (Bootstrap_Text, Admission, "binding")), Binding) and then
            P.Is_Text (Bootstrap_Text, JF (Bootstrap_Text, Admission, "state"), "CONSUMED") and then
            Events.Form = P.Array_Value and then P.Count (Bootstrap_Text, Events) = 1 and then
            Object_Keys (Bootstrap_Text, Event, "cause,genesis_sha256,journal_sha256,head_sha256", 4) and then
            P.Is_Text (Bootstrap_Text, JF (Bootstrap_Text, Event, "cause"), "OWNER_GENESIS_PROVISIONED") and then
            Digest_Is (Bootstrap_Text, JF (Bootstrap_Text, Event, "genesis_sha256"), Genesis_Id) and then
            Digest_Is (Bootstrap_Text, JF (Bootstrap_Text, Event, "journal_sha256"), Digest (Initial, Whole (Initial))) and then
            Digest_Is (Bootstrap_Text, JF (Bootstrap_Text, Event, "head_sha256"), Digest (Initial_Head, Whole (Initial_Head)));
      end;
      end;
   end Genesis_Matches;
   function Current_History_Core
     (Data : E.Bytes; Roster : E.Span; Facts_Data : E.Bytes; Capsules : E.Span)
      return Current_View is
      Key_Field : constant E.Span := Owned_File (Data, Roster, "/authority/issuer/state/issuer-key.bin");
      -- One name object per owner file read twice (guard and use).
      Policy_Name : constant String := "owner-policy.json";
      Journal_Name : constant String := "owner-transitions.json";
   begin
      if not V.Valid_Bytes (Data, Key_Field) or else
         not Replay_Capsules_Match (Data, Roster, Facts_Data) or else not X.Valid (Facts_Data, Capsules) or else
         not S.Text_Is (Data, SF (Data, Owner_Context (Data, Roster), "schema"), "worldline.owner-current-context-v1") or else
         not V.Type_Is (Data, SF (Data, Owner_Context (Data, Roster), "mutation_intent_present"), "bool") or else
         E.Decode (Data, OA.Field (Data,
            SF (Data, Owner_Context (Data, Roster), "mutation_intent_present"), "value"), E.Operation).Form /= E.Boolean_Value or else
         E.Decode (Data, OA.Field (Data,
            SF (Data, Owner_Context (Data, Roster), "mutation_intent_present"), "value"), E.Operation).Boolean_Bit then
         return (State => Rejected, others => <>);
      end if;
      if not Context_File_Matches (Data, Roster, "policy_raw", Policy_Name) or else
         not Context_File_Matches (Data, Roster, "genesis_raw", "owner-genesis.json") or else
         not Context_File_Matches (Data, Roster, "bootstrap_raw", "owner-bootstrap.json") or else
         not Context_File_Matches (Data, Roster, "journal_raw", Journal_Name) or else
         not Context_File_Matches (Data, Roster, "head_raw", "owner-head.json") then return (State => Rejected, others => <>); end if;
      -- The original raised converting a policy or journal beyond Natural'Last.
      if V.Bytes_Value (Data, Owner_File (Data, Roster, Policy_Name))'Length > E.Count (Natural'Last) or else
         V.Bytes_Value (Data, Owner_File (Data, Roster, Journal_Name))'Length > E.Count (Natural'Last)
      then return (State => Rejected, others => <>); end if;
      declare
         Key : constant E.Bytes := V.Bytes_Value (Data, Key_Field);
         Policy_Field : constant E.Span := Owner_File (Data, Roster, Policy_Name);
         Policy_Raw : constant E.Bytes := V.Bytes_Value (Data, Policy_Field);
         Policy_Text : constant String := Text (Policy_Raw);
         Policy : constant P.Node := P.Parse (Policy_Text);
         UID_Node : constant P.Node := JF (Policy_Text, Policy, "owner_uid");
         Binding : constant E.Span := SF (Data, Context (Data, Roster), "owner_binding");
         Journal_Field : constant E.Span := Owner_File (Data, Roster, Journal_Name);
         Journal : constant E.Bytes := V.Bytes_Value (Data, Journal_Field);
         Head : constant E.Bytes := Raw_File (Data, Roster, "owner-head.json");
         Journal_Text : constant String := Text (Journal);
         Body_Node : constant P.Node := JF (Journal_Text, P.Parse (Journal_Text), "body");
         Events : constant P.Node := JF (Journal_Text, Body_Node, "events");
         Gate_Raw : constant E.Span := Owned_File (Data, Roster, "/authority/gate/config.json");
         Issuer_Raw : constant E.Span := Owned_File (Data, Roster, "/authority/issuer/state/policy.json");
         Installation : constant E.Span := SF (Data, Current (Data, Roster), "installation");
      begin
         if not RJ.Canonical_ASCII_Valid (Policy_Text) or else
            not Object_Keys (Policy_Text, Policy,
               "schema,installation_id,owner_uid,owner_gid,owner_issuer_id,gate_config_sha256,issuer_policy_sha256,issuer_key_sha256,store_genesis,native_sha256,sources", 11) or else
            not P.Is_Text (Policy_Text, JF (Policy_Text, Policy, "schema"), "worldline.protected-owner-policy-v1") or else
            JF (Policy_Text, Policy, "owner_uid").Form /= P.Integer_Value or else
            not P.Nonnegative (Policy_Text, JF (Policy_Text, Policy, "owner_uid")) or else
            JF (Policy_Text, Policy, "owner_gid").Form /= P.Integer_Value or else
            not P.Nonnegative (Policy_Text, JF (Policy_Text, Policy, "owner_gid")) or else
            not P.Nonempty_Text (Policy_Text, JF (Policy_Text, Policy, "owner_issuer_id")) or else
            not Policy_Binding_Matches (Policy_Raw, Policy_Text, Policy, Data, Binding, True) or else
            not RJ.Raw_JSON_Scoped_Matches (Policy_Raw, Data, Part (Policy_Raw, JF (Policy_Text, Policy, "installation_id")),
               SF (Data, Installation, "installation_id")) or else
            not Digest_Is (Policy_Text, JF (Policy_Text, Policy, "issuer_key_sha256"), Digest (Key, Whole (Key))) or else
            not RJ.Raw_JSON_Scoped_Matches (Policy_Raw, Data,
               Part (Policy_Raw, JF (Policy_Text, Policy, "store_genesis")),
               SF (Data, SF (Data, SF (Data, Context (Data, Roster), "lease_genesis"), "store"), "identity")) or else
            not V.Valid_Bytes (Data, Gate_Raw) or else not V.Valid_Bytes (Data, Issuer_Raw) or else
            not Policy_Sources (Data, Roster, Policy_Text, Policy) or else
            P.Slice (Policy_Text, UID_Node)'Length > Natural'Last - UID_Open'Length - UID_Close'Length
         then return (State => Rejected, others => <>); end if;
         declare
            Gate : constant E.Bytes := V.Bytes_Value (Data, Gate_Raw);
            Issuer : constant E.Bytes := V.Bytes_Value (Data, Issuer_Raw);
            Genesis : constant E.Bytes := Raw_File (Data, Roster, "owner-genesis.json");
            Principal : constant String := UID_Open & P.Slice (Policy_Text, UID_Node) & UID_Close;
            Last : constant E.Bytes := (if P.Count (Journal_Text, Events) = 0 then Bytes ("GENESIS")
               else Digest (Journal, Part (Journal, P.Element (Journal_Text, Events, P.Count (Journal_Text, Events)))));
         begin
            if not (Digest_Is (Policy_Text, JF (Policy_Text, Policy, "gate_config_sha256"), Digest (Gate, Whole (Gate))) and then
               Digest_Is (Policy_Text, JF (Policy_Text, Policy, "issuer_policy_sha256"), Digest (Issuer, Whole (Issuer))) and then
               Genesis'Length <= E.Count (Natural'Last) and then
               Genesis_Matches (Data, Roster, Key, Genesis, Policy_Raw, Policy_Text, Policy) and then
               Envelope (Key, Journal, Whole (Key), Journal_Text) and then
               RJ.Raw_JSON_Scoped_Equal (Journal, Data, Part (Journal, JF (Journal_Text, Body_Node, "binding")), Binding) and then
               History (Journal, Journal_Text, Principal, P.Text (Policy_Text, JF (Policy_Text, Policy, "owner_issuer_id")),
                  Facts_Data, Capsules) and then
               Head'Length <= E.Count (Natural'Last) and then
               Head_Matches (Key, Journal, Head, Data, Binding, Last)) then
               return (State => Rejected, others => <>);
            end if;
            return (State => Verified, Roster => Roster, Key_Field => Key_Field,
               Policy_Field => Policy_Field, Binding => Binding, Journal_Field => Journal_Field,
               Event_Count => P.Count (Journal_Text, Events));
         end;
      end;
   end Current_History_Core;
   procedure Establish_History
     (Context : in out Prepared_History; Data, Facts_Data : E.Bytes; Roster : E.Span) is
   begin
      if Context.View.State /= Unestablished then return; end if;
      -- An empty arena whose lower bound is not an index: the original raised
      -- recording or spanning it. Refused, never verified.
      if Data'First < 1 or else Facts_Data'First < 1 then
         Context.View := (State => Rejected, others => <>);
         return;
      end if;
      -- The observer binds to this exact arena: extent and whole-bytes digest.
      Context.Arena_First := Data'First;
      Context.Arena_Length := Data'Length;
      Context.Arena_Digest := H.C.G.Hash (Data, Whole (Data));
      Context.View := Current_History_Core (Data, Roster, Facts_Data, Whole (Facts_Data));
   end Establish_History;
   function Bound (Context : Prepared_History; Data : E.Bytes) return Boolean is
     (Context.Arena_First = Data'First and then Context.Arena_Length = Data'Length);
   function Current_Matches (Context : Prepared_History) return Boolean is
     (Context.View.State = Verified);
   function Source_Matches
     (Context : Prepared_History; Data : E.Bytes; Roster : E.Span) return Boolean is
     (Current_Matches (Context) and then
      Context.View.Roster.First = Roster.First and then
      Context.View.Roster.Length = Roster.Length and then
      Bound (Context, Data) and then
      Context.Arena_Digest = H.C.G.Hash (Data, Whole (Data)));
   function Current_History_Authenticated (Value : L.Parsed_Input) return Boolean is
   begin
      if Value.Status /= L.Parsed or else
         not Worldline.Custody_V2_Owner_Correspondence.Owner_Corresponds (Value) then return False; end if;
      declare
         RawFacts : constant E.Bytes := Extract_Replay_Capsules (Value.Arena, Value.Owner_Roster);
         Context : Prepared_History;
      begin
         Establish_History (Context, Value.Arena, RawFacts, Value.Owner_Roster);
         return Current_Matches (Context);
      end;
   end Current_History_Authenticated;
   function From_Hex (Value : String) return E.Bytes
     with Global => null,
       Post => From_Hex'Result'First = 1 and then From_Hex'Result'Length <= E.Count (Value'Length)
   is
      function Space (C : Character) return Boolean is
        (C in ' ' | Character'Val (9) | Character'Val (10) | Character'Val (11) |
              Character'Val (12) | Character'Val (13));
      function Hex_Digit (C : Character) return Boolean is
        (C in '0' .. '9' | 'a' .. 'f' | 'A' .. 'F');
      function Nibble (C : Character) return E.Q.Byte is
        (if C in '0' .. '9' then Character'Pos (C) - Character'Pos ('0')
         elsif C in 'a' .. 'f' then Character'Pos (C) - Character'Pos ('a') + 10
         else Character'Pos (C) - Character'Pos ('A') + 10);
      -- Ghost models of the scan from Offset: whether every remaining
      -- non-space starts a hex pair, and how many pairs remain.
      function Pairs_Valid (From : Natural) return Boolean is
        (if From >= Value'Length then True
         elsif Space (Value (Value'First + From)) then Pairs_Valid (From + 1)
         else Value'Length - From >= 2 and then Hex_Digit (Value (Value'First + From)) and then
            Hex_Digit (Value (Value'First + From + 1)) and then Pairs_Valid (From + 2))
        with Ghost, Subprogram_Variant => (Decreases => Value'Length - From);
      function Pairs (From : Natural) return Natural is
        (if From >= Value'Length then 0
         elsif Space (Value (Value'First + From)) then Pairs (From + 1)
         elsif Value'Length - From >= 2 then Pairs (From + 2) + 1
         else 0)
        with Ghost, Subprogram_Variant => (Decreases => Value'Length - From),
          Post => Pairs'Result <= (if From >= Value'Length then 0 else Value'Length - From);
      Count : E.Count := 0;
      Offset : Natural := 0;
   begin
      while Offset < Value'Length loop
         pragma Loop_Invariant (Offset <= Value'Length);
         pragma Loop_Invariant (Count + E.Count (Pairs (Offset)) = E.Count (Pairs (0)));
         pragma Loop_Invariant (Pairs_Valid (0) = Pairs_Valid (Offset));
         pragma Loop_Variant (Decreases => Value'Length - Offset);
         if Space (Value (Value'First + Offset)) then Offset := Offset + 1;
         else
            if Value'Length - Offset < 2 or else not Hex_Digit (Value (Value'First + Offset)) or else
               not Hex_Digit (Value (Value'First + Offset + 1)) then return E.Bytes'(1 .. 0 => 0); end if;
            Count := Count + 1; Offset := Offset + 2;
         end if;
      end loop;
      declare Final_Count : constant E.Count := Count;
              Result : E.Bytes (1 .. Final_Count) := (others => 0); Index : E.Count := 0; begin
         Offset := 0;
         while Offset < Value'Length loop
            pragma Loop_Invariant (Offset <= Value'Length);
            pragma Loop_Invariant (Pairs_Valid (Offset));
            pragma Loop_Invariant (Index + E.Count (Pairs (Offset)) = Final_Count);
            pragma Loop_Variant (Decreases => Value'Length - Offset);
            if Space (Value (Value'First + Offset)) then Offset := Offset + 1;
            else
               Index := Index + 1;
               Result (Index) := Nibble (Value (Value'First + Offset)) * 16 +
                  Nibble (Value (Value'First + Offset + 1));
               Offset := Offset + 2;
            end if;
         end loop;
         return Result;
      end;
   end From_Hex;
   function From_Base64 (Value : String) return E.Bytes is
      Encoded : constant E.Bytes := Bytes (Value);
      Item : constant B.Span := (Encoded'First, Encoded'Length);
   begin
      if not B.Canonical (Encoded, Item) then return E.Bytes'(1 .. 0 => 0); end if;
      declare Result : E.Bytes (1 .. B.Decoded_Length (Encoded, Item)); begin
         B.Decode (Encoded, Item, Result); return Result;
      end;
   end From_Base64;
   function Authenticated_From_Data
     (Context : Prepared_History; Data, Capture_Data : E.Bytes; Witness : E.Span)
      return Boolean
      with Global => null, Pre => Current_Matches (Context)
   is
      function WF (Name : String) return E.Span is
        (OA.Field (Capture_Data, Witness, Name));
      -- Field spans read by both a guard and a use are one object each.
      Journal_W : constant E.Span := WF ("owner_journal");
      Head_W : constant E.Span := WF ("owner_head");
      Record_W : constant E.Span := WF ("owner_record");
      Operation_W : constant E.Span := WF ("operation");
   begin
      if not OA.Valid (Capture_Data, Witness) or else E.Decode (Capture_Data, Witness, E.Operation).Form /= E.Object_Value or else
         not Is_Text (Capture_Data, WF ("schema"), "worldline.owner-canonical-binding-v1", E.Operation) or else
         not Text_Valid (Capture_Data, Journal_W, E.Operation) or else
         not Text_Valid (Capture_Data, Head_W, E.Operation) or else
         not Text_Valid (Capture_Data, Record_W, E.Operation) or else
         not Text_Valid (Capture_Data, WF ("owner_event"), E.Operation) then return False; end if;
      -- The observer is bound by extent; these are the original's unguarded
      -- precondition and conversion failure points, refused explicitly.
      if not V.Valid_Bytes (Data, Context.View.Key_Field) or else
         not V.Valid_Bytes (Data, Context.View.Policy_Field) or else
         not V.Valid_Bytes (Data, Context.View.Journal_Field) or else
         V.Bytes_Value (Data, Context.View.Policy_Field)'Length > E.Count (Natural'Last) or else
         V.Bytes_Value (Data, Context.View.Journal_Field)'Length > E.Count (Natural'Last) or else
         not Archive_Fits (Capture_Data, Journal_W, E.Operation) or else
         not Archive_Fits (Capture_Data, Head_W, E.Operation) or else
         not Archive_Fits (Capture_Data, Record_W, E.Operation) then return False; end if;
      declare
         Key : constant E.Bytes := V.Bytes_Value (Data, Context.View.Key_Field);
         Policy_Raw : constant E.Bytes := V.Bytes_Value (Data, Context.View.Policy_Field);
         Policy_Text : constant String := Text (Policy_Raw);
         Policy : constant P.Node := P.Parse (Policy_Text);
         UID_Node : constant P.Node := JF (Policy_Text, Policy, "owner_uid");
         Binding : constant E.Span := Context.View.Binding;
         Current_Journal : constant E.Bytes := V.Bytes_Value (Data, Context.View.Journal_Field);
         Current_Text : constant String := Text (Current_Journal);
         Current_Body : constant P.Node := JF (Current_Text, P.Parse (Current_Text), "body");
         Actual : constant P.Node := JF (Current_Text, Current_Body, "events");
         Retained : constant E.Bytes := From_Hex (Archive_Text (Capture_Data, Journal_W, E.Operation));
         Retained_Head : constant E.Bytes := From_Hex (Archive_Text (Capture_Data, Head_W, E.Operation));
         Retained_Text : constant String := Text (Retained);
         Retained_Body : constant P.Node := JF (Retained_Text, P.Parse (Retained_Text), "body");
         Events : constant P.Node := JF (Retained_Text, Retained_Body, "events");
         Record_Data : constant E.Bytes := From_Base64 (Archive_Text (Capture_Data, Record_W, E.Operation));
         Record_Value : constant E.Span := Whole (Record_Data);
         Base : constant E.Span := F (Record_Data, Record_Value, "base");
         Request : constant E.Span := F (Record_Data, Record_Value, "request");
         Reserved_Event : P.Node := P.No_Node;
         Reserved_Count : Natural := 0;
         Selected : Boolean := False;
      begin
         if not Policy_Binding_Matches (Policy_Raw, Policy_Text, Policy, Capture_Data, WF ("owner_binding"), False) or else
            not Envelope (Key, Retained, Whole (Key), Retained_Text, Exact_Keys => False) or else
            not RJ.Raw_JSON_Scoped_Equal (Retained, Data, Part (Retained, JF (Retained_Text, Retained_Body, "binding")), Binding) or else
            Events.Form /= P.Array_Value or else P.Count (Retained_Text, Events) = 0 or else
            P.Count (Retained_Text, Events) > Context.View.Event_Count or else
            not Record_Valid (Record_Data, Record_Value) or else
            not Text_Valid (Capture_Data, Operation_W, E.Operation) or else
            not Archive_Fits (Capture_Data, Operation_W, E.Operation) or else
            not Is_Text (Record_Data, F (Record_Data, Base, "intent"), Archive_Text (Capture_Data, Operation_W, E.Operation)) then return False; end if;
         for I in 1 .. P.Count (Retained_Text, Events) loop
            pragma Loop_Invariant (Reserved_Count < I);
            declare Event : constant P.Node := P.Element (Retained_Text, Events, I); begin
               if not P.Equal (Retained_Text, Event, Current_Text,
                  P.Element (Current_Text, Actual, I)) then return False; end if;
               if Digest_Is (Retained_Text, JF (Retained_Text, Event, "record"),
                  Bytes (Archive_Text (Capture_Data, Record_W, E.Operation))) and then
                  Is_Text (Capture_Data, WF ("owner_event"), Text (Digest (Retained, Part (Retained, Event))), E.Operation) then
                  Selected := True;
               end if;
               if P.Is_Text (Retained_Text, JF (Retained_Text, Event, "intent"), Archive_Text (Capture_Data, Operation_W, E.Operation)) and then
                  Event_Cause (Retained_Text, Event) = Reserved then
                  Reserved_Count := Reserved_Count + 1;
                  Reserved_Event := Event;
               end if;
            end;
         end loop;
         if not Selected or else Reserved_Count /= 1 or else
            not Head_Matches (Key, Retained, Retained_Head, Data, Binding,
               Digest (Retained, Part (Retained, P.Element (Retained_Text, Events, P.Count (Retained_Text, Events)))),
               Exact_Keys => False) or else
            P.Slice (Policy_Text, UID_Node)'Length > Natural'Last - UID_Open'Length - UID_Close'Length
         then return False; end if;
         declare
            Original : constant E.Bytes := Decode_Record (Retained_Text, Reserved_Event);
            Original_Request : constant E.Span := F (Original, Whole (Original), "request");
            Peer : constant E.Span := OA.Field (Capture_Data, WF ("original_request"), "peer");
            UID : constant E.Span := OA.Field (Capture_Data, Peer, "uid");
            Principal : constant String := UID_Open & P.Slice (Policy_Text, UID_Node) & UID_Close;
         begin
            -- Every retained event equals the corresponding verified current
            -- event, including its complete original record bytes. The unique
            -- RESERVED native redecision was therefore performed by History
            -- during Establish_History; do not replay current material here.
            return Request_Same_Except_State (Record_Data, Original, Request, Original_Request) and then
               RJ.Raw_JSON_Operation_Matches (Policy_Raw, Capture_Data,
                  Part (Policy_Raw, JF (Policy_Text, Policy, "owner_uid")), UID) and then
               Is_Text (Record_Data, F (Record_Data, Request, "peer"), Principal);
         end;
      end;
   end Authenticated_From_Data;
   function Authenticated
     (Context : Prepared_History; Data, Capture_Data : E.Bytes; Witness : E.Span)
      return Boolean is
   begin
      if not Current_Matches (Context) or else not Bound (Context, Data) then return False; end if;
      return Authenticated_From_Data (Context, Data, Capture_Data, Witness);
   end Authenticated;
   function Authenticated
     (Value : L.Parsed_Input; Capture_Data : E.Bytes; Witness : E.Span)
      return Boolean is
   begin
      if Value.Status /= L.Parsed or else
         not Worldline.Custody_V2_Owner_Correspondence.Owner_Corresponds (Value) then return False; end if;
      declare
         RawFacts : constant E.Bytes := Extract_Replay_Capsules (Value.Arena, Value.Owner_Roster);
         Context : Prepared_History;
      begin
         Establish_History (Context, Value.Arena, RawFacts, Value.Owner_Roster);
         return Authenticated (Context, Value.Arena, Capture_Data, Witness);
      end;
   end Authenticated;
end Worldline.Custody_V2_Owner_Canonical;
