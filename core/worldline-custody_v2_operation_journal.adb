with Ada.Characters.Latin_1;
with Attest;
with Canonical_Artifacts;
with Worldline.Custody_V2_Domain_Hmac;
with Worldline.Custody_V2_Owner_Correspondence;
with Worldline.Chain_Authority;
with Worldline.Custody_V2_Owner_Canonical;
with Worldline.Custody_V2_K4_Resource_Ack;
with Worldline.Actor_Archive_Replay;
with Worldline.Custody_V2_Archive_Projection;
with Interfaces;
with Worldline.Startup_Admission;
with Worldline.Startup_Source_Custody;
with Worldline.Startup_Installation;
with Worldline.Archive_Base64;
package body Worldline.Custody_V2_Operation_Journal with SPARK_Mode is
   package V renames L.V;
   package S renames V.S;
   package OA renames S.A;
   package J renames Canonical_Artifacts;
   package H renames Worldline.Custody_V2_Domain_Hmac;
   package C renames Worldline.Chain_Authority;
   use type E.Count;
   use type E.Span;
   use type E.Value_Kind;
   use type E.Encoding_Level;
   use type Q.Byte;
   use type Q.Byte_Array;
   use type J.Kind;
   use type J.JSON_Kind;
   use type J.Genesis_Correspondence;
   use type R.Replay_State;
   use type R.Operation_Entry;
   use type A.Command;
   use type A.Decision;
   use type R.H.Decision;
   use type C.Reason;
   use type C.Optional_Digest;
   use type Worldline.Hash;
   use type Interfaces.Unsigned_64;
   use type Interfaces.Unsigned_32;
   Domain : constant String := "worldline-protected-canonical-operations-v1" &
      Ada.Characters.Latin_1.NUL;
   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span
     renames R.Archive_Field;
   function Same (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (S.Valid (Data, Left) and then S.Valid (Data, Right) and then
      OA.Same_Encoding (Data, Left, Right));
   function Raw_Same (Left_Data, Right_Data : E.Bytes; Left, Right : E.Span)
      return Boolean is
     (J.P.Valid (Left_Data, Left) and then J.P.Valid (Right_Data, Right) and then
      Left.Length = Right.Length and then
      (for all I in E.Count range 1 .. Left.Length =>
         Left_Data (Left.First + I - 1) = Right_Data (Right.First + I - 1)));
   function JF (Data : E.Bytes; Item : E.Span; Name : String) return E.Span is
     (J.Canonical_JSON_Field (Data, Item, Name));
   function JSON (Data : E.Bytes; Item : E.Span) return E.Span is
   begin
      if not J.P.Valid (Data, Item) or else Item.Length = 0 then return (1, 0); end if;
      if Data (Item.First + Item.Length - 1) = Character'Pos (Ada.Characters.Latin_1.LF)
      then return J.Part (Item, 0, Item.Length - 1); end if;
      return Item;
   end JSON;
   function JSON_Count (Data : E.Bytes; Item : E.Span) return E.Count is
      Node : constant J.JSON_Node := J.JSON_Prefix (Data, Item, 0);
      Offset : E.Count := 1;
      Found : E.Count := 0;
      Key, Child : J.JSON_Node;
   begin
      if not Node.Valid or else Node.After /= Item.Length or else
         Node.Form not in J.Object_JSON_Value | J.Array_JSON_Value then return 0; end if;
      while Offset < Item.Length - 1 loop
         pragma Loop_Variant (Decreases => Item.Length - Offset);
         if Node.Form = J.Object_JSON_Value then
            Key := J.JSON_Prefix (Data, Item, Offset);
            if not Key.Valid or else Key.After >= Item.Length then return 0; end if;
            Offset := Key.After + 1;
         end if;
         Child := J.JSON_Prefix (Data, Item, Offset);
         if not Child.Valid or else Child.After <= Offset then return 0; end if;
         Found := Found + 1;
         Offset := Child.After;
         if Offset < Item.Length - 1 then Offset := Offset + 1; end if;
      end loop;
      return Found;
   end JSON_Count;
   function JA (Data : E.Bytes; Item : E.Span; Ordinal : E.Count) return E.Span is
      Node : constant J.JSON_Node := J.JSON_Prefix (Data, Item, 0);
      Offset : E.Count := 1;
      Index : E.Count := 0;
      Child : J.JSON_Node;
   begin
      if not Node.Valid or else Node.After /= Item.Length or else
         Node.Form /= J.Array_JSON_Value then return (1, 0); end if;
      while Offset < Item.Length - 1 loop
         pragma Loop_Variant (Decreases => Item.Length - Offset);
         Child := J.JSON_Prefix (Data, Item, Offset);
         if not Child.Valid or else Child.After <= Offset then return (1, 0); end if;
         if Index = Ordinal then return J.Part (Item, Child.First, Child.After); end if;
         Index := Index + 1;
         Offset := Child.After;
         if Offset < Item.Length - 1 then Offset := Offset + 1; end if;
      end loop;
      return (1, 0);
   end JA;
   function JSON_Keys (Data : E.Bytes; Item : E.Span; Names : String;
                       Count : E.Count) return Boolean is
      Start : Positive := Names'First;
   begin
      if not J.Canonical_JSON_Valid (Data, Item) or else JSON_Count (Data, Item) /= Count or else
         J.JSON_Prefix (Data, Item, 0).Form /= J.Object_JSON_Value then return False; end if;
      for I in Names'Range loop
         pragma Loop_Variant (Increases => I);
         if Names (I) = ',' then
            if I = Start or else JF (Data, Item, Names (Start .. I - 1)).Length = 0 then return False; end if;
            Start := I + 1;
         end if;
      end loop;
      return Start <= Names'Last and then JF (Data, Item, Names (Start .. Names'Last)).Length > 0;
   end JSON_Keys;
   function JSON_Is (Data : E.Bytes; Item : E.Span; Text : String) return Boolean is
     (J.String_Is (Data, Item, J.Prefix (Data, Item, 0), Text));
   function JSON_Matches (JSON_Data, Archive_Data : E.Bytes;
                         JSON_Value, Encoded : E.Span) return Boolean is
     (J.Scoped_Archive_JSON_Matches (JSON_Data, Archive_Data, JSON_Value, Encoded) =
         J.Typed_Tree_Matches_Source_Custody_Open);
   function Hex_Matches (Text : E.Bytes; Sum : H.SHA.Digest) return Boolean is
      Hex_Digits : constant String := "0123456789abcdef";
   begin
      return Text'Length = Sum'Length * 2 and then
        (for all I in Sum'Range =>
          Text (Text'First + E.Count (I - Sum'First) * 2) =
             Character'Pos (Hex_Digits (Integer (Sum (I) / 16) + 1)) and then
          Text (Text'First + E.Count (I - Sum'First) * 2 + 1) =
             Character'Pos (Hex_Digits (Integer (Sum (I) mod 16) + 1)));
   end Hex_Matches;
   function Digest_Text (Data : E.Bytes; Item : E.Span; Sum : H.SHA.Digest)
      return Boolean is
     (V.Valid_Text (Data, Item) and then Hex_Matches (V.Text_Value (Data, Item), Sum));
   function Digest_JSON (Data : E.Bytes; Item : E.Span; Sum : H.SHA.Digest)
      return Boolean is
   begin
      if not J.P.Valid (Data, Item) or else Item.Length /= Sum'Length * 2 + 2 or else
         Data (Item.First) /= Character'Pos ('"') or else
         Data (Item.First + Item.Length - 1) /= Character'Pos ('"') then return False; end if;
      return Hex_Matches (Data (Item.First + 1 .. Item.First + Item.Length - 2), Sum);
   end Digest_JSON;
   function Envelope_Authenticated
     (Key_Data, JSON_Data : E.Bytes; Key, Envelope : E.Span;
      Domain : String) return Boolean is
      Encoded : constant E.Span := JSON (JSON_Data, Envelope);
   begin
      return J.P.Valid (Key_Data, Key) and then
         JSON_Keys (JSON_Data, Encoded, "body,mac", 2) and then
         Digest_JSON (JSON_Data, JF (JSON_Data, Encoded, "mac"),
            H.Mac (Key_Data, JSON_Data, Key, JF (JSON_Data, Encoded, "body"), Domain));
   end Envelope_Authenticated;
   function Transition_Allowed
     (Before, After : Journal_State; Command : A.Command;
      Decision : A.Decision; Historical : R.H.Decision;
      Historical_Entry : Boolean := False) return Boolean is
   begin
      if Historical_Entry then
         return Before = Quarantined and then
           ((After = Resolved_Effect and then Historical = R.H.Resolve_Effect) or else
            (After = Resolved_No_Effect and then Historical = R.H.Resolve_No_Effect));
      end if;
      case After is
         when Reserved => return Before = Absent and then Command = A.Reserve_Use and then Decision = A.Reserved_New;
         when Effect_Intent => return Before = Reserved and then Command = A.Reserve_Use and then Decision = A.Reserved_Replay;
         when Effect_Observed => return Before = Effect_Intent and then Command = A.Observe_Effect and then Decision = A.Effect_Accepted;
         when Settled => return Before in Effect_Observed | Resolved_Effect and then Command = A.Settle_Use and then Decision = A.Settled_New;
         when Released => return Before in Reserved | Effect_Intent and then Command = A.Release_Use and then Decision = A.Released_New;
         when Quarantined => return Before in Reserved | Effect_Intent | Effect_Observed | Quarantined and then Command = A.Quarantine_Use and then Decision = A.Quarantined_New;
         when Resolved_Effect => return Before = Quarantined and then Command = A.Resolve_Effect and then Decision = A.Resolved_Effect;
         when Resolved_No_Effect => return Before = Quarantined and then Command = A.Resolve_No_Effect and then Decision = A.Resolved_No_Effect;
         when Absent => return False;
      end case;
   end Transition_Allowed;
   function Cause (Data : E.Bytes; Event : E.Span) return Journal_State is
      Name : constant E.Span := F (Data, Event, "cause");
   begin
      for State in Reserved .. Resolved_No_Effect loop
         pragma Loop_Variant (Increases => Journal_State'Pos (State));
         if S.Text_Is (Data, Name, Journal_State'Image (State)) then return State; end if;
      end loop;
      return Absent;
   end Cause;
   function State_Is (Data : E.Bytes; Item : E.Span; State : Journal_State) return Boolean is
     (case State is
         when Reserved | Effect_Intent => E.Text_Is (Data, E.Decode (Data, Item, E.Operation), "RESERVED"),
         when Effect_Observed | Resolved_Effect => E.Text_Is (Data, E.Decode (Data, Item, E.Operation), "EFFECT_OBSERVED"),
         when Settled => E.Text_Is (Data, E.Decode (Data, Item, E.Operation), "SETTLED"),
         when Released | Resolved_No_Effect => E.Text_Is (Data, E.Decode (Data, Item, E.Operation), "RELEASED"),
         when Quarantined => E.Text_Is (Data, E.Decode (Data, Item, E.Operation), "QUARANTINED"),
         when Absent => False);
   function Raw_Hex (Data : E.Bytes; Item : E.Span) return E.Bytes is
     (V.Hex_Value (Data, Item, "value"))
     with Pre => V.Valid_Text (Data, Item) and then V.Valid_Hex_Field (Data, Item, "value");
   function Sequence_Count (Data : E.Bytes; Item : E.Span) return E.Count is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if S.Valid (Data, Item) then return V.Count (Data, Item); end if;
      if OA.Valid (Data, Item) and then View.Form in E.List_Value | E.Tuple_Value then
         return E.Array_Length (Data, View.Children); end if;
      return 0;
   end Sequence_Count;
   function Element (Data : E.Bytes; Item : E.Span; Ordinal : E.Count) return E.Span is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if S.Valid (Data, Item) then return V.Element (Data, Item, Ordinal); end if;
      if OA.Valid (Data, Item) and then View.Form in E.List_Value | E.Tuple_Value then
         return E.Array_Element (Data, View.Children, Ordinal); end if;
      return (1, 0);
   end Element;
   function Path_Entry (Data : E.Bytes; Paths, Word : E.Span) return E.Span is
      Found : E.Span := (1, 0);
   begin
      for I in E.Count range 1 .. V.Count (Data, Paths) loop
         pragma Loop_Variant (Increases => I);
         declare Item : constant E.Span := V.Element (Data, Paths, I - 1); begin
            if Same (Data, F (Data, Item, "path"), Word) then
               if Found.Length > 0 then return (1, 0); end if;
               Found := Item;
            end if;
         end;
      end loop;
      return Found;
   end Path_Entry;
   function Joined (Data : E.Bytes; Word, Base : E.Span; Suffix : String) return Boolean is
   begin
      if not V.Valid_Text (Data, Word) or else not V.Valid_Text (Data, Base) then return False; end if;
      declare W : constant E.Bytes := V.Text_Value (Data, Word);
              B : constant E.Bytes := V.Text_Value (Data, Base); begin
         return W'Length >= B'Length and then W'Length - B'Length = Suffix'Length and then
           (for all I in E.Count range 1 .. B'Length => W (W'First + I - 1) = B (B'First + I - 1)) and then
           (for all I in Suffix'Range => W (W'First + B'Length + E.Count (I - Suffix'First)) = Character'Pos (Suffix (I)));
      end;
   end Joined;
   function Suffix_Entry (Data : E.Bytes; Paths, Base : E.Span; Suffix : String) return E.Span is
      Found : E.Span := (1, 0);
   begin
      for I in E.Count range 1 .. V.Count (Data, Paths) loop
         pragma Loop_Variant (Increases => I);
         declare Item : constant E.Span := V.Element (Data, Paths, I - 1); begin
            if Joined (Data, F (Data, Item, "path"), Base, Suffix) then
               if Found.Length > 0 then return (1, 0); end if;
               Found := Item;
            end if;
         end;
      end loop;
      return Found;
   end Suffix_Entry;
   function Internal_Table_Name (Data : E.Bytes; Item : E.Span) return Boolean;
   type Column_Visibility is (Malformed_Column, Visible_Column, Hidden_Column);
   function Visibility (Data : E.Bytes; Column : E.Span) return Column_Visibility;
   function Row_Value (Data : E.Bytes; Row : E.Span; Ordinal, Width : E.Count) return E.Span is
   begin
      if V.Is_Sequence (Data, Row) and then V.Count (Data, Row) = Width - 1 and then
         Ordinal in 2 .. Width
      then
         return V.Element (Data, Row, Ordinal - 2);
      else
         return (1, 0);
      end if;
   end Row_Value;
   function Table_Row (Data : E.Bytes; Database : E.Span; Name, Columns : String;
                       Column_Count : E.Count) return E.Span is
      Tables : constant E.Span := F (Data, Database, "tables");
      Selection : constant E.Span := F (Data, F (Data, Database, "operation_named_rows"),
         (if Name = "canonical_operation_head" then "head" else "admission"));
      Selected : constant E.Span := F (Data, Selection, "row");
      Arguments : constant E.Span := F (Data, Selection, "args");
      SQL : constant String := (if Name = "canonical_operation_head" then
         "SELECT installation,genesis,head,state,prior_envelope,next_envelope FROM canonical_operation_head WHERE name=?"
         else "SELECT installation,genesis,owner_envelope,initial_envelope,state FROM canonical_operation_admission WHERE name=?");
      Found : E.Span := (1, 0);
      Table_Found, Head_Found, Admission_Found : Boolean := False;
      type Column_Map is array (E.Count range 1 .. Column_Count) of E.Count;
      Positions : Column_Map := (others => 0);
      Start : Positive;
      Visible : E.Count;
   begin
      if not V.Is_Sequence (Data, Tables) or else not V.Is_Sequence (Data, Selected) or else
         V.Count (Data, Selected) /= Column_Count - 1 or else not V.Is_Null (Data, F (Data, Selection, "error")) or else
         not S.Text_Is (Data, F (Data, Selection, "sql"), SQL) or else
         not V.Is_Sequence (Data, Arguments) or else V.Count (Data, Arguments) /= 1 or else
         not S.Text_Is (Data, V.Element (Data, Arguments, 0), "worldline-operations") then return (1, 0); end if;
      for I in E.Count range 1 .. V.Count (Data, Tables) loop
         declare Item : constant E.Span := V.Element (Data, Tables, I - 1);
                 Cols : constant E.Span := F (Data, Item, "columns");
                 Rows : constant E.Span := F (Data, Item, "rows"); begin
            if S.Text_Is (Data, F (Data, Item, "name"), "canonical_operation_head") then
               if Head_Found then return (1, 0); end if; Head_Found := True;
            elsif S.Text_Is (Data, F (Data, Item, "name"), "canonical_operation_admission") then
               if Admission_Found then return (1, 0); end if; Admission_Found := True;
            elsif not Internal_Table_Name (Data, F (Data, Item, "name")) then return (1, 0); end if;
            if S.Text_Is (Data, F (Data, Item, "name"), Name) then
               if Table_Found or else not V.Is_Sequence (Data, Cols) or else
                  not V.Is_Sequence (Data, Rows) then return (1, 0); end if;
               Table_Found := True; Visible := 0;
               for K in E.Count range 1 .. V.Count (Data, Cols) loop
                  case Visibility (Data, V.Element (Data, Cols, K - 1)) is
                     when Malformed_Column => return (1, 0);
                     when Hidden_Column => null;
                     when Visible_Column =>
                        if Visible = Column_Count then return (1, 0); end if;
                        Visible := Visible + 1; Positions (Visible) := K - 1;
                  end case;
               end loop;
               if Visible /= Column_Count then return (1, 0); end if;
               Start := Columns'First; Visible := 1;
               for K in Columns'Range loop
                  if Columns (K) = ',' then
                     if not S.Text_Is (Data, V.Element (Data, V.Element (Data, Cols, Positions (Visible)), 1),
                        Columns (Start .. K - 1)) then return (1, 0); end if;
                     Start := K + 1; Visible := Visible + 1;
                  end if;
               end loop;
               if not S.Text_Is (Data, V.Element (Data, V.Element (Data, Cols, Positions (Visible)), 1),
                  Columns (Start .. Columns'Last)) then return (1, 0); end if;
               -- The original table_info excludes generated/hidden columns.
               -- Keep every table_xinfo column and full SELECT * row, but join
               -- the actual named fetchone through its visible column positions.
               -- Rowid, WITHOUT ROWID, internal tables and other names remain.
               -- SQL performs WHERE name=? with the actual column affinity and
               -- collation; do not replace that recorded query by byte equality.
               -- Its exact projected result must occur in the full source rows.
               for K in E.Count range 1 .. V.Count (Data, Rows) loop
                  declare
                     Row : constant E.Span := V.Element (Data, Rows, K - 1);
                     Width : constant E.Count := V.Count (Data, Cols);
                     Offset : constant E.Count := (if V.Count (Data, Row) = Width + 1 then 1 else 0);
                  begin
                     if not V.Is_Sequence (Data, Row) or else V.Count (Data, Row) not in Width | Width + 1 then return (1, 0); end if;
                     if Found.Length = 0 and then
                        (for all C in E.Count range 2 .. Column_Count =>
                           Same (Data, V.Element (Data, Row, Positions (C) + Offset), V.Element (Data, Selected, C - 2))) then
                        Found := Selected;
                     end if;
                  end;
               end loop;
            end if;
         end;
      end loop;
      if Head_Found and then Admission_Found then
         return Found;
      else
         return (1, 0);
      end if;
   end Table_Row;
   function Row_Bytes (Data : E.Bytes; Row : E.Span; Ordinal, Width : E.Count;
                       Raw : E.Bytes) return Boolean is
      Item : constant E.Span := Row_Value (Data, Row, Ordinal, Width);
   begin
      return V.Valid_Bytes (Data, Item) and then V.Bytes_Value (Data, Item) = Raw;
   end Row_Bytes;
   function Head_Corresponds (Data, Key, Current_Raw, Owner_Raw : E.Bytes;
                             Database, Installation, Policy, Context : E.Span) return Boolean is
      Head : constant E.Span := Table_Row (Data, Database, "canonical_operation_head",
         "name,installation,genesis,head,state,prior_envelope,next_envelope", 7);
      Admission : constant E.Span := Table_Row (Data, Database, "canonical_operation_admission",
         "name,installation,genesis,owner_envelope,initial_envelope,state", 6);
      Genesis : constant E.Span := F (Data, Policy, "genesis");
      Initial : constant E.Span := F (Data, Context, "owner_initial_archive");
   begin
      if Head.Length = 0 or else Admission.Length = 0 or else
         not Same (Data, Row_Value (Data, Head, 2, 7), Installation) or else
         not Same (Data, Row_Value (Data, Admission, 2, 6), Installation) or else
         not Same (Data, Row_Value (Data, Head, 3, 7), Genesis) or else
         not Same (Data, Row_Value (Data, Admission, 3, 6), Genesis) or else
         not S.Text_Is (Data, Row_Value (Data, Admission, 6, 6), "CONSUMED") or else
         not Row_Bytes (Data, Admission, 4, 6, Owner_Raw) or else not V.Valid_Bytes (Data, Initial) or else
         not V.Valid_Hex_Field (Data, Row_Value (Data, Admission, 5, 6), "value")
      then return False; end if;
      declare
         Original_Initial : constant E.Bytes := V.Bytes_Value (Data, Initial);
         Owner_Body : constant E.Span := JF (Owner_Raw, JSON (Owner_Raw, (Owner_Raw'First, Owner_Raw'Length)), "body");
      begin
         if Raw_Hex (Data, Row_Value (Data, Admission, 5, 6)) /= Original_Initial or else
            not J.Operation_Archive_JSON_Matches (Owner_Raw, Original_Initial,
               JF (Owner_Raw, Owner_Body, "initial_envelope"),
               (Original_Initial'First, Original_Initial'Length)) then return False; end if;
      end;
      if S.Text_Is (Data, Row_Value (Data, Head, 5, 7), "STABLE") then
         return Digest_Text (Data, Row_Value (Data, Head, 4, 7),
            H.C.G.Hash (Current_Raw, (Current_Raw'First, Current_Raw'Length)));
      elsif S.Text_Is (Data, Row_Value (Data, Head, 5, 7), "INTENT") and then
         V.Valid_Bytes (Data, Row_Value (Data, Head, 6, 7)) and then
         Row_Bytes (Data, Head, 7, 7, Current_Raw) then
         declare Prior : constant E.Bytes := V.Bytes_Value (Data, Row_Value (Data, Head, 6, 7)); begin
            -- The exact surviving NEXT file is the original lost-ACK case.
            -- The retained PRIOR is authenticated; nothing regenerates a file.
            return Envelope_Authenticated (Key, Prior, (Key'First, Key'Length),
                       (Prior'First, Prior'Length), Domain) and then
               Envelope_Authenticated (Key, Current_Raw, (Key'First, Key'Length),
                       (Current_Raw'First, Current_Raw'Length), Domain) and then
               Digest_Text (Data, Row_Value (Data, Head, 4, 7),
                            H.C.G.Hash (Prior, (Prior'First, Prior'Length)));
         end;
      end if;
      return False;
   end Head_Corresponds;
   function Native_Item (Data : E.Bytes; Items, Event : E.Span) return E.Span is
      Found : E.Span := (1, 0);
   begin
      for I in E.Count range 1 .. V.Count (Data, Items) loop
         pragma Loop_Variant (Increases => I);
         declare Item : constant E.Span := V.Element (Data, Items, I - 1); begin
            if Same (Data, F (Data, Item, "event"), Event) then
               if Found.Length > 0 then return (1, 0); end if;
               Found := Item;
            end if;
         end;
      end loop;
      return Found;
   end Native_Item;
   type Index_Array is array (Q.Byte_Index range <>) of E.Count;
   type State_Array is array (Q.Byte_Index range <>) of Journal_State;
   function Native_Identity_Corresponds (Data : E.Bytes; Capture : E.Span) return Boolean is
      Native : constant E.Span := F (Data, Capture, "native");
      Id : constant E.Span := F (Data, F (Data, Capture, "binding"), "id");
      function Digest_Field (Name : String; Sum : H.SHA.Digest) return Boolean is
         Word : constant E.View := E.Decode (Data, F (Data, Id, Name), E.Operation);
      begin
         return Word.Form = E.Text_Value and then E.Bytes_Valid (Data, Word.Payload) and then
            Hex_Matches (E.Materialize (Data, Word.Payload), Sum);
      end Digest_Field;
      function Payload_Digest (Field, Identity : String) return Boolean is
         View : constant E.View := E.Decode (Data, F (Data, Native, Field), E.Operation);
      begin
         if View.Form /= E.Bytes_Value or else not E.Bytes_Valid (Data, View.Payload) then return False; end if;
         declare Raw : constant E.Bytes := E.Materialize (Data, View.Payload); begin
            return Digest_Field (Identity, H.C.G.Hash (Raw, (Raw'First, Raw'Length)));
         end;
      end Payload_Digest;
   begin
      return OA.Valid (Data, Native) and then
         Payload_Digest ("build_bytes", "kernel_build") and then
         Payload_Digest ("library_bytes", "kernel_library") and then
         Digest_Field ("kernel_mapping", H.C.G.Hash (Data, Native));
   end Native_Identity_Corresponds;
   function History_Corresponds (Data, Raw : E.Bytes; Body_JSON, Events, Items,
                                Current_Events, Context, Policy : E.Span;
                                Owner_Context : O.Prepared_History;
                                Resource_Context : K.Prepared_History;
                                Already_Through : E.Count := 0) return Boolean is
      Extent : constant E.Count := V.Count (Data, Events);
      Latest : Index_Array (1 .. Extent) := (others => 0);
      States : State_Array (1 .. Extent) := (others => Absent);
      Used, Native_Count : E.Count := 0;
      Prior_JSON : E.Span := (1, 0);
      JSON_Events : constant E.Span := JF (Raw, Body_JSON, "events");
      JSON_Grants : constant E.Span := JF (Raw, Body_JSON, "grants");
   begin
      if not V.Is_Sequence (Data, Events) or else not V.Is_Sequence (Data, Items) or else
         Extent > V.Count (Data, Current_Events) or else
         not JSON_Matches (Raw, Data, JSON_Events, Events) then return False; end if;
      for I in E.Count range 1 .. Extent loop
         pragma Loop_Variant (Increases => I);
         declare
            Event : constant E.Span := V.Element (Data, Events, I - 1);
            Event_JSON : constant E.Span := JA (Raw, JSON_Events, I - 1);
            Before : Journal_State := Absent;
            Position : E.Count := 0;
            Old_Event : E.Span := (1, 0);
            Native : R.Operation_Replay_Result;
            Item, Observation, Material : E.Span;
            After : constant Journal_State := Cause (Data, Event);
         begin
            if not Same (Data, Event, V.Element (Data, Current_Events, I - 1)) or else
               not JSON_Keys (Raw, Event_JSON, "prior,operation,cause,capture,snapshot,native,boundaries", 7) then return False; end if;
            if I = 1 then
               if not JSON_Matches (Raw, Data, JF (Raw, Event_JSON, "prior"), F (Data, Policy, "genesis")) then return False; end if;
            elsif not Digest_JSON (Raw, JF (Raw, Event_JSON, "prior"), H.C.G.Hash (Raw, Prior_JSON)) then return False;
            end if;
            Prior_JSON := Event_JSON;
            for K in E.Count range 1 .. Used loop
               pragma Loop_Variant (Increases => K);
               if Same (Data, F (Data, Event, "operation"),
                        F (Data, V.Element (Data, Events, Latest (K) - 1), "operation")) then
                  Position := K; Before := States (K);
                  Old_Event := V.Element (Data, Events, Latest (K) - 1);
               end if;
            end loop;
            if I <= Already_Through then
               -- This exact prefix already passed Current_Authenticated in the
               -- same caller; only retain its derived row state for the new step.
               if not S.Text_Is (Data, F (Data, Event, "cause"), "PREPARATION") and then
                  not S.Text_Is (Data, F (Data, Event, "cause"), "OWNER_CANONICAL") then
                  Native_Count := Native_Count + 1;
                  if Position = 0 then Used := Used + 1; Position := Used; end if;
                  Latest (Position) := I;
                  States (Position) := (if S.Text_Is (Data, F (Data, Event, "cause"), "ACK") then Before else After);
               end if;
            elsif S.Text_Is (Data, F (Data, Event, "cause"), "PREPARATION") then
               if Position /= 0 or else not V.Is_Null (Data, F (Data, Event, "native")) or else
                  not V.Is_Null (Data, F (Data, Event, "snapshot")) then return False; end if;
               if not V.Valid_Hex_Field (Data, F (Data, Event, "capture"), "value") then return False; end if;
               declare
                  Capture_Data : constant E.Bytes := Raw_Hex (Data, F (Data, Event, "capture"));
               begin
                  if not OA.Valid (Capture_Data, (Capture_Data'First, Capture_Data'Length)) or else
                     not Worldline.Custody_V2_Archive_Projection.Scoped_Archive_Operation_Matches
                       (Data, Capture_Data, F (Data, Event, "operation"),
                        F (Capture_Data, (Capture_Data'First, Capture_Data'Length), "operation")) then return False; end if;
               end;
            elsif S.Text_Is (Data, F (Data, Event, "cause"), "OWNER_CANONICAL") then
               if not V.Is_Null (Data, F (Data, Event, "native")) or else
                  not V.Is_Null (Data, F (Data, Event, "snapshot")) or else
                  not V.Valid_Hex_Field (Data, F (Data, Event, "capture"), "value") then return False; end if;
               declare Capture_Data : constant E.Bytes := Raw_Hex (Data, F (Data, Event, "capture")); begin
                  if not OA.Valid (Capture_Data, (Capture_Data'First, Capture_Data'Length)) or else
                     not Worldline.Custody_V2_Archive_Projection.Scoped_Archive_Operation_Matches
                       (Data, Capture_Data, F (Data, Event, "operation"),
                        F (Capture_Data, (Capture_Data'First, Capture_Data'Length), "operation")) then return False; end if;
                  if not O.Authenticated
                    (Owner_Context, Data, Capture_Data, (Capture_Data'First, Capture_Data'Length)) then return False; end if;
               end;
            else
               Item := Native_Item (Data, Items, Event);
               Observation := F (Data, Item, "observation");
               Material := F (Data, Item, "material");
               Native := R.Reestablish_Operation_Observation (Data, Observation);
               Native_Count := Native_Count + 1;
               if Item.Length = 0 or else Native.State /= R.Native_Redecided or else
                  (Native.Roster_Entry = R.Authority_Entry and then Native.Native_Status = A.Refused) or else
                  (Native.Roster_Entry = R.Historical_Completion_Entry and then Native.Historical_Status = R.H.Refused) or else
                  not R.Operation_Capture_Matches (Data, Observation, Material, Event) or else
                  not V.Valid_Hex_Field (Data, F (Data, Event, "snapshot"), "value") or else
                  not V.Valid_Hex_Field (Data, F (Data, Event, "capture"), "value") then return False; end if;
               if Position > 0 then
                  if not Same (Data, F (Data, Event, "capture"), F (Data, Old_Event, "capture")) or else
                     V.Count (Data, F (Data, Event, "boundaries")) < V.Count (Data, F (Data, Old_Event, "boundaries")) then return False; end if;
                  for K in E.Count range 1 .. V.Count (Data, F (Data, Old_Event, "boundaries")) loop
                     pragma Loop_Variant (Increases => K);
                     if not Same (Data, V.Element (Data, F (Data, Event, "boundaries"), K - 1),
                                  V.Element (Data, F (Data, Old_Event, "boundaries"), K - 1)) then return False; end if;
                  end loop;
               end if;
               declare
                  Snapshot_Data : constant E.Bytes := Raw_Hex (Data, F (Data, Event, "snapshot"));
                  Snapshot : constant E.Span := (Snapshot_Data'First, Snapshot_Data'Length);
                  Uses : constant E.Span := F (Snapshot_Data, Snapshot, "uses");
                  Is_ACK : constant Boolean := S.Text_Is (Data, F (Data, Event, "cause"), "ACK");
               begin
                  if not OA.Valid (Snapshot_Data, Snapshot) then return False; end if;
                  if Is_ACK and then not S.Text_Is (Data,
                     F (Data, F (Data, Event, "native"), "command"), "RESOLVE_RECOVERY") then
                     if Position = 0 or else not Same (Data, F (Data, Event, "snapshot"), F (Data, Old_Event, "snapshot")) or else
                        not Same (Data, F (Data, Event, "native"), F (Data, Old_Event, "native")) then return False; end if;
                  else
                     if Sequence_Count (Snapshot_Data, Uses) /= Used then return False; end if;
                     for K in E.Count range 1 .. Used loop
                        pragma Loop_Variant (Increases => K);
                        declare
                           Old : constant E.Span := V.Element (Data, Events, Latest (K) - 1);
                           Capture_Data : constant E.Bytes := Raw_Hex (Data, F (Data, Old, "capture"));
                           Use_Row : constant E.Span := Element (Snapshot_Data, Uses, K - 1);
                        begin
                           if not State_Is (Snapshot_Data, F (Snapshot_Data, Use_Row, "state"), States (K)) or else
                              not Raw_Same (Snapshot_Data, Capture_Data, F (Snapshot_Data, Use_Row, "bound"),
                                 F (Capture_Data, (Capture_Data'First, Capture_Data'Length), "binding")) then return False; end if;
                        end;
                     end loop;
                     if Is_ACK then
                        if Position = 0 or else Before /= Effect_Intent or else Native.Roster_Entry /= R.Authority_Entry or else
                           Native.Command /= A.Resolve_Recovery or else Native.Native_Status not in A.Owner_Abort | A.Owner_Settle then return False; end if;
                     elsif not J.Operation_Archive_JSON_Matches (Raw, Snapshot_Data, JSON_Grants,
                                F (Snapshot_Data, Snapshot, "grants")) or else
                           not Transition_Allowed (Before, After, Native.Command, Native.Native_Status,
                              Native.Historical_Status, Native.Roster_Entry = R.Historical_Completion_Entry) then return False;
                     end if;
                     if Native.Roster_Entry = R.Historical_Completion_Entry and then
                        not K.Authenticated (Resource_Context, Data, Event, Old_Event) then return False; end if;
                  end if;
                  if not Is_ACK then
                     declare
                        Capture_Data : constant E.Bytes := Raw_Hex (Data, F (Data, Event, "capture"));
                        Actual_Native : constant E.Span := F (Data, Context, "native_context");
                     begin
                        if not V.Valid_Bytes (Data, Actual_Native) then return False; end if;
                        declare
                           Native_Data : constant E.Bytes := V.Bytes_Value (Data, Actual_Native);
                           Captured : constant E.Span := F (Capture_Data, (Capture_Data'First, Capture_Data'Length), "native");
                        begin
                           -- Historical addresses/process identities are retained,
                           -- not replaced by a fresh map. Immutable selected build
                           -- and library bytes must still be the actual source.
                           if not OA.Valid (Native_Data, (Native_Data'First, Native_Data'Length)) or else
                              not Raw_Same (Capture_Data, Native_Data, F (Capture_Data, Captured, "build_bytes"),
                                 F (Native_Data, (Native_Data'First, Native_Data'Length), "build_bytes")) or else
                              not Raw_Same (Capture_Data, Native_Data, F (Capture_Data, Captured, "library_bytes"),
                                 F (Native_Data, (Native_Data'First, Native_Data'Length), "library_bytes")) then return False; end if;
                           if not Native_Identity_Corresponds (Capture_Data, (Capture_Data'First, Capture_Data'Length)) or else
                              not Raw_Same (Capture_Data, Native_Data, F (Capture_Data, Captured, "library_path"),
                                 F (Native_Data, (Native_Data'First, Native_Data'Length), "library_path")) then return False; end if;
                        end;
                     end;
                  end if;
                  if Position = 0 then Used := Used + 1; Position := Used; end if;
                  Latest (Position) := I;
                  States (Position) := (if Is_ACK then Before else After);
               end;
            end if;
         end;
      end loop;
      return Native_Count = V.Count (Data, Items);
   end History_Corresponds;
   function Hash_Value (Sum : H.SHA.Digest) return Worldline.Hash is
      Result : Worldline.Hash;
   begin
      for I in Result'Range loop
         pragma Loop_Variant (Increases => I);
         Result (I) := Sum (Sum'First + Integer (I - Result'First));
      end loop;
      return Result;
   end Hash_Value;
   function Original_Text (Data : E.Bytes; Item : E.Span) return E.Bytes is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if V.Valid_Text (Data, Item) then return V.Text_Value (Data, Item); end if;
      if View.Form = E.Text_Value and then E.Bytes_Valid (Data, View.Payload) then
         return E.Materialize (Data, View.Payload); end if;
      return E.Bytes'(1 .. 0 => 0);
   end Original_Text;
   function Nibble (Byte : Q.Byte) return Q.Byte is
     (if Byte in Character'Pos ('0') .. Character'Pos ('9') then Byte - Character'Pos ('0')
      else Byte - Character'Pos ('a') + 10)
     with Pre => Byte in Character'Pos ('0') .. Character'Pos ('9') |
                         Character'Pos ('a') .. Character'Pos ('f');
   function Hex_Id (Data : E.Bytes; Item : E.Span; Prefixed : Boolean := False)
      return C.Optional_Digest is
      Raw : constant E.Bytes := Original_Text (Data, Item);
      Offset : constant E.Count := (if Prefixed then 7 else 0);
      Prefix : constant String := "sha256:";
      Result : C.Optional_Digest := (Present => False, Value => Worldline.Zero_Hash);
   begin
      if Raw'Length /= Offset + Result.Value'Length * 2 then return Result; end if;
      if Prefixed and then (for some I in Prefix'Range =>
         Raw (Raw'First + E.Count (I - Prefix'First)) /= Character'Pos (Prefix (I))) then return Result; end if;
      if not V.Hex_Domain (Raw (Raw'First + Offset .. Raw'Last)) then return Result; end if;
      Result.Present := True;
      for I in Result.Value'Range loop
         pragma Loop_Variant (Increases => I);
         Result.Value (I) := Nibble (Raw (Raw'First + Offset + E.Count (I - Result.Value'First) * 2)) * 16 +
                            Nibble (Raw (Raw'First + Offset + E.Count (I - Result.Value'First) * 2 + 1));
      end loop;
      return Result;
   end Hex_Id;
   function Domain_Hash (Data : E.Bytes; Item : E.Span; Domain : String) return Worldline.Hash is
      Context : H.SHA.Context := H.SHA.Initial;
   begin
      for B of Domain loop H.SHA.Update (Context, Attest.Byte_Array'(0 => Character'Pos (B))); end loop;
      if J.P.Valid (Data, Item) then
         for I in E.Count range 1 .. Item.Length loop
            pragma Loop_Variant (Increases => I);
            H.SHA.Update (Context, Attest.Byte_Array'(0 => Data (Item.First + I - 1)));
         end loop;
      end if;
      return Hash_Value (H.SHA.Final (Context));
   end Domain_Hash;
   function Boundaries_Correspond (Data : E.Bytes; Events, Context : E.Span) return Boolean is
      package B renames Worldline.Actor_Archive_Replay;
   begin
      for I in E.Count range 1 .. V.Count (Data, Events) loop
         pragma Loop_Variant (Increases => I);
         declare Event : constant E.Span := V.Element (Data, Events, I - 1);
                 Boundaries : constant E.Span := F (Data, Event, "boundaries"); begin
            if not V.Is_Sequence (Data, Boundaries) then return False; end if;
            for K in E.Count range 1 .. V.Count (Data, Boundaries) loop
               pragma Loop_Variant (Increases => K);
               declare Boundary : constant E.Span := V.Element (Data, Boundaries, K - 1);
                       Name : constant E.Span := F (Data, Boundary, "name"); begin
                  if S.Text_Is (Data, Name, "FOLLOWUP_NATIVE") then
                     if not B.Operation_Boundary_Matches (Data, F (Data, Boundary, "material"), Event, Context, B.Followup) then return False; end if;
                  elsif S.Text_Is (Data, Name, "ACTOR_EXECUTION_NATIVE") then
                     if not B.Operation_Boundary_Matches (Data, F (Data, Boundary, "material"), Event, Context, B.Actor_Execution) then return False; end if;
                  elsif S.Text_Is (Data, Name, "FULL_BROKER_NATIVE") then
                     if not B.Operation_Boundary_Matches (Data, F (Data, Boundary, "value"), Event, Context, B.Full_Broker) then return False; end if;
                  end if;
               end;
            end loop;
         end;
      end loop;
      return True;
   end Boundaries_Correspond;
   function Original_Bytes (Data : E.Bytes; Item : E.Span) return E.Bytes is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if View.Form /= E.Bytes_Value or else not E.Bytes_Valid (Data, View.Payload) then
         return E.Bytes'(1 .. 0 => 0); end if;
      return E.Materialize (Data, View.Payload);
   end Original_Bytes;
   function Source_Canonical_Rows (Data, Material_Data : E.Bytes; Context, Material : E.Span;
                                  Receipts : Boolean; Complete : Boolean := True) return Boolean is
      package P renames Worldline.Custody_V2_Archive_Projection;
      Current : constant E.Span := F (Data, Context, "current");
      State : constant E.Span := F (Data, F (Data, F (Data, Current, "installation"), "paths"), "state");
      Store : constant E.Span := Suffix_Entry (Data, F (Data, Current, "paths"), State, "/worldline.sqlite3");
      Tables : constant E.Span := F (Data, F (Data, Store, "logical_database"), "tables");
      Files : constant E.Span := F (Data, F (Data, Context, "operation_context"), "canonical_files");
      Name : constant String := (if Receipts then "receipts" else "causal_events");
      Kind : constant String := (if Receipts then "receipts" else "events");
      Rows : constant E.Span := F (Material_Data, Material, Kind);
      Table : E.Span := (1, 0);
   begin
      for I in E.Count range 1 .. V.Count (Data, Tables) loop
         pragma Loop_Variant (Increases => I);
         declare Item : constant E.Span := V.Element (Data, Tables, I - 1); begin
            if S.Text_Is (Data, F (Data, Item, "name"), Name) then
               if Table.Length > 0 then return False; end if;
               Table := Item;
            end if;
         end;
      end loop;
      if Table.Length = 0 or else not V.Is_Sequence (Data, Files) or else
         (if Complete then Sequence_Count (Material_Data, Rows) /= V.Count (Data, F (Data, Table, "rows"))
          else Sequence_Count (Material_Data, Rows) > V.Count (Data, F (Data, Table, "rows"))) then return False; end if;
      for I in E.Count range 1 .. Sequence_Count (Material_Data, Rows) loop
         pragma Loop_Variant (Increases => I);
         declare
            Pair : constant E.Span := Element (Material_Data, Rows, I - 1);
            SQL : constant E.Span := Element (Material_Data, Pair, 0);
            SQL_View : constant E.View := E.Decode (Material_Data, SQL, E.Operation);
            Actual : constant E.Span := V.Element (Data, F (Data, Table, "rows"), I - 1);
            Columns : constant E.Span := F (Data, Table, "columns");
            Found : E.Count := 0;
            Hash_Text : constant E.Bytes := Original_Text (Material_Data, F (Material_Data, SQL, "chain_hash"));
         begin
            if Sequence_Count (Material_Data, Pair) /= 2 or else SQL_View.Form /= E.Object_Value or else
               E.Array_Length (Material_Data, SQL_View.Children) /= V.Count (Data, Columns) or else
               V.Count (Data, Actual) /= V.Count (Data, Columns) + 1 or else
               not Hex_Id (Material_Data, F (Material_Data, SQL, "chain_hash"), True).Present then return False; end if;
            for K in E.Count range 1 .. V.Count (Data, Columns) loop
               pragma Loop_Variant (Increases => K);
               declare KV : constant E.View := E.Decode (Material_Data,
                          E.Array_Element (Material_Data, SQL_View.Children, K - 1), E.Finalization); begin
                  if KV.Form /= E.List_Value or else E.Array_Length (Material_Data, KV.Children) /= 2 or else
                     not P.Scoped_Archive_Operation_Matches (Data, Material_Data,
                        V.Element (Data, V.Element (Data, Columns, K - 1), 1), E.Array_Element (Material_Data, KV.Children, 0)) or else
                     not P.Scoped_Archive_Operation_Matches (Data, Material_Data,
                        V.Element (Data, Actual, K), E.Array_Element (Material_Data, KV.Children, 1)) then return False; end if;
               end;
            end loop;
            for K in E.Count range 1 .. V.Count (Data, Files) loop
               pragma Loop_Variant (Increases => K);
               declare File : constant E.Span := V.Element (Data, Files, K - 1);
                       Identity : constant E.Span := F (Data, File, "identity"); begin
                  if S.Text_Is (Data, F (Data, File, "kind"), Kind) and then
                     P.Scoped_Archive_Operation_Matches (Data, Material_Data,
                        F (Data, File, "canonical_path"), F (Material_Data, SQL, "canonical_path")) then
                     Found := Found + 1;
                     if not V.Valid_Bytes (Data, F (Data, File, "raw")) or else
                        V.Bytes_Value (Data, F (Data, File, "raw")) /= Original_Bytes (Material_Data, Element (Material_Data, Pair, 1)) or else
                        not Same (Data, F (Data, File, "path"), F (Data, File, "canonical_path")) or else
                        not V.Is_Integer (Data, F (Data, Identity, "device")) or else
                        not V.Is_Integer (Data, F (Data, Identity, "inode")) or else
                        not V.Is_Integer (Data, F (Data, Identity, "uid")) or else
                        not V.Is_Integer (Data, F (Data, Identity, "gid")) or else
                        not V.Is_Integer (Data, F (Data, Identity, "mode")) then return False; end if;
                     declare Hex : String (1 .. 64); begin
                        for L in Hex'Range loop Hex (L) := Character'Val (Hash_Text (Hash_Text'First + 7 + E.Count (L - Hex'First))); end loop;
                        if not Joined (Data, F (Data, File, "path"), State, "/" & Kind & "/" & Hex & ".json") then return False; end if;
                     end;
                  end if;
               end;
            end loop;
            if Found /= 1 then return False; end if;
         end;
      end loop;
      return True;
   end Source_Canonical_Rows;
   function Canonical_Chain_Corresponds (Data : E.Bytes; Context : E.Span; Receipts : Boolean;
                                        Genesis, Witness : C.Optional_Digest;
                                        Appending : Boolean := False;
                                        Added : C.Chain_Row := (others => (False, Worldline.Zero_Hash)))
      return Boolean is
      Raw_Item : constant E.Span := F (Data, F (Data, Context, "operation_context"), "current_chain_material");
   begin
      if not V.Valid_Bytes (Data, Raw_Item) or else not Genesis.Present or else not Witness.Present then return False; end if;
      declare
         Raw : constant E.Bytes := V.Bytes_Value (Data, Raw_Item);
         Material : constant E.Span := (Raw'First, Raw'Length);
         Items : constant E.Span := F (Raw, Material, (if Receipts then "receipts" else "events"));
         Extent : constant E.Count := Sequence_Count (Raw, Items);
         Capacity : constant E.Count := (if Extent < E.Count'Last then Extent + 1 else 0);
         Rows : C.Retained_Rows (1 .. Capacity);
         Count : E.Count := 0;
         Found : Boolean := Witness.Value = Worldline.Zero_Hash;
         Previous : C.Optional_Digest;
         Chain : constant C.Chain_Kind := (if Receipts then C.Receipt_Chain else C.Causal_Chain);
      begin
         if Capacity = 0 or else not OA.Valid (Raw, Material) or else
            not Source_Canonical_Rows (Data, Raw, Context, Material, Receipts) then return False; end if;
         for I in E.Count range 1 .. Extent loop
            pragma Loop_Variant (Increases => I);
            declare Pair : constant E.Span := Element (Raw, Items, I - 1);
                    SQL : constant E.Span := Element (Raw, Pair, 0);
                    Payload : constant E.Bytes := Original_Bytes (Raw, Element (Raw, Pair, 1));
                    Root : constant Worldline.Hash := Domain_Hash (Payload, (Payload'First, Payload'Length),
                       (if Receipts then "worldline-receipt-record-v1" else "worldline-event-v1")); begin
               if Receipts then
                  if E.Decode (Raw, F (Raw, SQL, "previous_receipt"), E.Operation).Form = E.Null_Value then
                     Previous := (True, Worldline.Zero_Hash);
                  else
                     Previous := (False, Worldline.Zero_Hash);
                     for K in E.Count range 1 .. Sequence_Count (Raw, Items) loop
                        pragma Loop_Variant (Increases => K);
                        declare Other : constant E.Span := Element (Raw, Element (Raw, Items, K - 1), 0); begin
                           if Raw_Same (Raw, Raw, F (Raw, Other, "receipt_id"), F (Raw, SQL, "previous_receipt")) then
                              if Previous.Present then return False; end if;
                              Previous := Hex_Id (Raw, F (Raw, Other, "chain_hash"), True);
                           end if;
                        end;
                     end loop;
                  end if;
               else Previous := Hex_Id (Raw, F (Raw, SQL, "predecessor"), True);
               end if;
               Rows (I) := (Previous, (True, Root),
                  Hex_Id (Raw, F (Raw, SQL, (if Receipts then "receipt_root" else "event_root")), True),
                  Hex_Id (Raw, F (Raw, SQL, "chain_hash"), True));
               if not Found then
                  Count := I;
                  if Rows (I).Stored_Head.Present and then Rows (I).Stored_Head.Value = Witness.Value then Found := True; end if;
               end if;
            end;
         end loop;
         -- Both entire actual current histories and the exact authentic old
         -- prefix are native Append replays, not an indexed tail assertion.
         if not Found or else C.Replay (Chain, Rows (1 .. Extent), (True, Worldline.Zero_Hash), Genesis,
            (if Extent = 0 then (True, Worldline.Zero_Hash) else Rows (Extent).Stored_Head)).Disposition /= C.Ready or else
            C.Replay (Chain, Rows (1 .. Count), (True, Worldline.Zero_Hash), Genesis, Witness).Disposition /= C.Ready then return False; end if;
         if Appending then
            Rows (Count + 1) := Added;
            return C.Replay (Chain, Rows (1 .. Count + 1), (True, Worldline.Zero_Hash), Genesis,
               Added.Stored_Head).Disposition = C.Ready;
         end if;
         return True;
      end;
   end Canonical_Chain_Corresponds;
   function Chain_Witness_Matches
     (Data, Raw : E.Bytes; Chain_JSON, Initial, Witness : E.Span) return Boolean is
      Fields : constant E.Span := S.A.Field (Data, Initial, "fields");
      View : constant E.View := E.Decode (Data, Fields, E.Operation);
      Offset : E.Count := 1;
      Key, Child : J.JSON_Node;
      Found : Boolean;
   begin
      if not S.Valid (Data, Initial) or else View.Form /= E.Object_Value or else
         J.JSON_Prefix (Raw, Chain_JSON, 0).Form /= J.Object_JSON_Value or else
         JSON_Count (Raw, Chain_JSON) /= E.Array_Length (Data, View.Children) then return False; end if;
      while Offset < Chain_JSON.Length - 1 loop
         pragma Loop_Variant (Decreases => Chain_JSON.Length - Offset);
         Key := J.JSON_Prefix (Raw, Chain_JSON, Offset);
         if not Key.Valid or else Key.After >= Chain_JSON.Length then return False; end if;
         Child := J.JSON_Prefix (Raw, Chain_JSON, Key.After + 1);
         if not Child.Valid or else Child.After <= Offset then return False; end if;
         Found := False;
         for I in E.Count range 1 .. E.Array_Length (Data, View.Children) loop
            pragma Loop_Variant (Increases => I);
            declare
               Pair : constant E.View := E.Decode
                 (Data, E.Array_Element (Data, View.Children, I - 1), E.Finalization);
               Original_Key : constant E.Span := E.Array_Element (Data, Pair.Children, 0);
            begin
               if Pair.Form /= E.List_Value or else E.Array_Length (Data, Pair.Children) /= 2 then return False; end if;
               if J.Operation_Archive_JSON_Matches (Raw, Data, J.Part (Chain_JSON, Key.First, Key.After), Original_Key) then
                  if Found or else not JSON_Matches (Raw, Data, J.Part (Chain_JSON, Child.First, Child.After),
                     (if E.Text_Is (Data, E.Decode (Data, Original_Key, E.Operation), "head") then Witness else E.Array_Element (Data, Pair.Children, 1))) then return False; end if;
                  Found := True;
               end if;
            end;
         end loop;
         if not Found then return False; end if;
         Offset := Child.After;
         if Offset < Chain_JSON.Length - 1 then Offset := Offset + 1; end if;
      end loop;
      return True;
   end Chain_Witness_Matches;
   function Prefix_Chains_Correspond
     (Data, Raw : E.Bytes; Body_JSON, Events, Policy, Archives : E.Span) return Boolean is
      Chains_JSON : constant E.Span := JF (Raw, Body_JSON, "chains");
      type Chain_Name is (Receipts, Events_Chain, Operation_Receipts, Operation_Events);
      function Name (Kind : Chain_Name) return String is
        (case Kind is when Receipts => "receipts", when Events_Chain => "events",
         when Operation_Receipts => "operation_receipts", when Operation_Events => "operation_events");
      function Unique (Event_Ordinal, Boundary_Ordinal : E.Count; Archive : E.Span) return Boolean is
      begin
         for I in E.Count range 1 .. Event_Ordinal loop
            pragma Loop_Variant (Increases => I);
            declare Group : constant E.Span := V.Element (Data, Archives, I - 1);
                    Last : constant E.Count := (if I = Event_Ordinal then Boundary_Ordinal - 1 else V.Count (Data, Group)); begin
               for K in E.Count range 1 .. Last loop
                  pragma Loop_Variant (Increases => K);
                  if Same (Data, Archive, V.Element (Data, Group, K - 1)) then return False; end if;
               end loop;
            end;
         end loop;
         return True;
      end Unique;
   begin
      -- The private current proof already replays every original chain,
      -- source row, intent and ACK. Events here are its exact immutable prefix;
      -- reconstruct their four witnesses, never repeat those native decisions.
      if not JSON_Keys (Raw, Chains_JSON, "receipts,events,operation_receipts,operation_events", 4) then return False; end if;
      for Kind in Chain_Name loop
         pragma Loop_Variant (Increases => Chain_Name'Pos (Kind));
         declare Initial : constant E.Span := F (Data, F (Data, Policy, "chains"), Name (Kind));
                 Witness : E.Span := F (Data, Initial, "head"); begin
            for I in E.Count range 1 .. V.Count (Data, Events) loop
               pragma Loop_Variant (Increases => I);
               declare Bounds : constant E.Span := F (Data, V.Element (Data, Events, I - 1), "boundaries");
                       Group : constant E.Span := V.Element (Data, Archives, I - 1); begin
                  for K in E.Count range 1 .. V.Count (Data, Bounds) loop
                     pragma Loop_Variant (Increases => K);
                     declare Bound : constant E.Span := V.Element (Data, Bounds, K - 1); begin
                        if Unique (I, K, V.Element (Data, Group, K - 1)) and then
                           S.Text_Is (Data, F (Data, Bound, "kind"), Name (Kind)) and then
                           (S.Text_Is (Data, F (Data, Bound, "name"), "CANONICAL_ACK") or else
                            S.Text_Is (Data, F (Data, Bound, "name"), "OPERATION_CHAIN_ACK")) then
                           Witness := F (Data, Bound, "head");
                        end if;
                     end;
                  end loop;
               end;
            end loop;
            if not Chain_Witness_Matches (Data, Raw, JF (Raw, Chains_JSON, Name (Kind)), Initial, Witness) then return False; end if;
         end;
      end loop;
      return True;
   end Prefix_Chains_Correspond;
   function Chains_Correspond
     (Data, Raw : E.Bytes; Body_JSON, Events, Context, Policy, Archives : E.Span)
      return Boolean is
      Policies : constant E.Span := F (Data, Policy, "chains");
      Chains_JSON : constant E.Span := JF (Raw, Body_JSON, "chains");
      JSON_Events : constant E.Span := JF (Raw, Body_JSON, "events");
      type Chain_Name is (Receipts, Events_Chain, Operation_Receipts, Operation_Events);
      function Name (Kind : Chain_Name) return String is
        (case Kind is when Receipts => "receipts", when Events_Chain => "events",
         when Operation_Receipts => "operation_receipts", when Operation_Events => "operation_events");
      function Unique (Event_Ordinal, Boundary_Ordinal : E.Count; Archive : E.Span) return Boolean is
      begin
         for I in E.Count range 1 .. Event_Ordinal loop
            pragma Loop_Variant (Increases => I);
            declare Group : constant E.Span := V.Element (Data, Archives, I - 1);
                    Last : constant E.Count := (if I = Event_Ordinal then Boundary_Ordinal - 1 else V.Count (Data, Group)); begin
               for K in E.Count range 1 .. Last loop
                  pragma Loop_Variant (Increases => K);
                  if Same (Data, Archive, V.Element (Data, Group, K - 1)) then return False; end if;
               end loop;
            end;
         end loop;
         return True;
      end Unique;
      function Canonical_Intent_Valid (Intent : E.Span; Kind : Chain_Name) return Boolean is
         Initial : constant E.Span := F (Data, Policies, Name (Kind));
         Genesis : constant C.Optional_Digest := Hex_Id (Data, F (Data, Initial, "genesis"));
      begin
         if Kind not in Receipts | Events_Chain or else
            not V.Valid_Hex_Field (Data, F (Data, Intent, "old_material"), "value") or else
            not V.Valid_Hex_Field (Data, F (Data, Intent, "payload"), "value") then return False; end if;
         declare
            Old : constant E.Bytes := Raw_Hex (Data, F (Data, Intent, "old_material"));
            Payload : constant E.Bytes := Raw_Hex (Data, F (Data, Intent, "payload"));
            Root : constant Worldline.Hash := Domain_Hash (Payload, (Payload'First, Payload'Length),
               (if Kind = Receipts then "worldline-receipt-record-v1" else "worldline-event-v1"));
            Row : constant C.Chain_Row := (Hex_Id (Data, F (Data, Intent, "previous")),
               (True, Root), Hex_Id (Data, F (Data, Intent, "root")), Hex_Id (Data, F (Data, Intent, "head")));
         begin
            return J.Canonical_JSON_Valid (Payload, (Payload'First, Payload'Length)) and then
               OA.Valid (Old, (Old'First, Old'Length)) and then
               (if Sequence_Count (Old, F (Old, (Old'First, Old'Length), Name (Kind))) = 0 then
                   Row.Previous = C.Optional_Digest'(True, Worldline.Zero_Hash)
                else Hex_Id (Old, F (Old, Element (Old, Element (Old, F (Old, (Old'First, Old'Length), Name (Kind)),
                   Sequence_Count (Old, F (Old, (Old'First, Old'Length), Name (Kind))) - 1), 0), "chain_hash"), True) = Row.Previous) and then
               Source_Canonical_Rows (Data, Old, Context, (Old'First, Old'Length), Kind = Receipts, False) and then
               Canonical_Chain_Corresponds (Data, Context, Kind = Receipts, Genesis, Row.Previous, True, Row);
         end;
      end Canonical_Intent_Valid;
      function Ack_Intent (Event_Ordinal, Boundary_Ordinal : E.Count;
                           Ack : E.Span; Kind : Chain_Name) return Boolean is
         Found : E.Span := (1, 0);
         Operation : constant E.Span := F (Data, V.Element (Data, Events, Event_Ordinal - 1), "operation");
      begin
         for I in E.Count range 1 .. Event_Ordinal loop
            pragma Loop_Variant (Increases => I);
            declare Bounds : constant E.Span := F (Data, V.Element (Data, Events, I - 1), "boundaries");
                    Group : constant E.Span := V.Element (Data, Archives, I - 1);
                    Last : constant E.Count := (if I = Event_Ordinal then Boundary_Ordinal - 1 else V.Count (Data, Bounds)); begin
               if Same (Data, Operation, F (Data, V.Element (Data, Events, I - 1), "operation")) then
                  for K in E.Count range 1 .. Last loop
                     pragma Loop_Variant (Increases => K);
                     declare Bound : constant E.Span := V.Element (Data, Bounds, K - 1);
                             Archive : constant E.Span := V.Element (Data, Group, K - 1); begin
                        if Unique (I, K, Archive) and then S.Text_Is (Data, F (Data, Bound, "kind"), Name (Kind)) and then
                           (S.Text_Is (Data, F (Data, Bound, "name"), "CANONICAL_INTENT") or else
                            S.Text_Is (Data, F (Data, Bound, "name"), "OWNER_CANONICAL_INTENT") or else
                            S.Text_Is (Data, F (Data, Bound, "name"), "OPERATION_CHAIN_INTENT")) then
                           declare Original : constant E.Bytes := V.Bytes_Value (Data, Archive); begin
                              if Digest_Text (Data, F (Data, Ack, "intent"), H.C.G.Hash (Original, (Original'First, Original'Length))) then
                                 if Found.Length > 0 then return False; end if;
                                 Found := Bound;
                              end if;
                           end;
                        end if;
                     end;
                  end loop;
               end if;
            end;
         end loop;
         if Found.Length = 0 or else not Same (Data, F (Data, Ack, "head"), F (Data, Found, "head")) then return False; end if;
         if Kind in Operation_Receipts | Operation_Events then
            return S.Text_Is (Data, F (Data, Found, "name"), "OPERATION_CHAIN_INTENT") and then
               Same (Data, F (Data, Ack, "operation"), Operation) and then
               Same (Data, F (Data, Ack, "operation"), F (Data, Found, "operation")) and then
               Same (Data, F (Data, Ack, "payload"), F (Data, Found, "payload")) and then
               Same (Data, F (Data, Ack, "previous"), F (Data, Found, "previous")) and then
               Same (Data, F (Data, Ack, "root"), F (Data, Found, "root"));
         end if;
         if not Canonical_Intent_Valid (Found, Kind) or else
            not V.Valid_Hex_Field (Data, F (Data, Ack, "full_material"), "value") then return False; end if;
         declare
            Before : constant E.Bytes := Raw_Hex (Data, F (Data, Found, "old_material"));
            Actual : constant E.Bytes := Raw_Hex (Data, F (Data, Ack, "full_material"));
            Old_Rows : constant E.Span := F (Before, (Before'First, Before'Length), Name (Kind));
            Rows : constant E.Span := F (Actual, (Actual'First, Actual'Length), Name (Kind));
            Extent : constant E.Count := Sequence_Count (Actual, Rows);
         begin
            if not OA.Valid (Actual, (Actual'First, Actual'Length)) or else Extent = 0 or else
               Extent - 1 /= Sequence_Count (Before, Old_Rows) or else
               not Source_Canonical_Rows (Data, Actual, Context, (Actual'First, Actual'Length), Kind = Receipts, False) then return False; end if;
            for I in E.Count range 1 .. Extent - 1 loop
               pragma Loop_Variant (Increases => I);
               if not Raw_Same (Before, Actual, Element (Before, Old_Rows, I - 1), Element (Actual, Rows, I - 1)) then return False; end if;
            end loop;
            return Original_Bytes (Actual, Element (Actual, Element (Actual, Rows, Extent - 1), 1)) =
               Raw_Hex (Data, F (Data, Found, "payload")) and then
               Hex_Id (Actual, F (Actual, Element (Actual, Element (Actual, Rows, Extent - 1), 0), "chain_hash"), True) =
               Hex_Id (Data, F (Data, Ack, "head"));
         end;
      end Ack_Intent;
      Total : E.Count := 0;
   begin
      if V.Count (Data, Archives) < V.Count (Data, Events) or else
         not JSON_Keys (Raw, Chains_JSON, "receipts,events,operation_receipts,operation_events", 4) then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Events) loop
         pragma Loop_Variant (Increases => I);
         declare Bounds : constant E.Span := F (Data, V.Element (Data, Events, I - 1), "boundaries");
                 Group : constant E.Span := V.Element (Data, Archives, I - 1);
                 JSON_Bounds : constant E.Span := JF (Raw, JA (Raw, JSON_Events, I - 1), "boundaries"); begin
            if not V.Is_Sequence (Data, Group) or else V.Count (Data, Group) /= V.Count (Data, Bounds) or else
               V.Count (Data, Bounds) > E.Count'Last - Total then return False; end if;
            Total := Total + V.Count (Data, Bounds);
            for K in E.Count range 1 .. V.Count (Data, Group) loop
               pragma Loop_Variant (Increases => K);
               declare Archive : constant E.Span := V.Element (Data, Group, K - 1); begin
                  if not V.Valid_Bytes (Data, Archive) then return False; end if;
                  declare Original : constant E.Bytes := V.Bytes_Value (Data, Archive); begin
                     if not J.Operation_Archive_JSON_Matches (Raw, Original, JA (Raw, JSON_Bounds, K - 1),
                        (Original'First, Original'Length)) then return False; end if;
                  end;
               end;
            end loop;
         end;
      end loop;
      for Kind in Chain_Name loop
         pragma Loop_Variant (Increases => Chain_Name'Pos (Kind));
         declare
            Initial : constant E.Span := F (Data, Policies, Name (Kind));
            Genesis : constant C.Optional_Digest := Hex_Id (Data, F (Data, Initial, "genesis"));
            Witness : E.Span := F (Data, Initial, "head");
            Final_Total : constant E.Count := Total;
            Rows : C.Retained_Rows (1 .. Final_Total);
            Count : E.Count := 0;
            Chain : constant C.Chain_Kind := (if Kind in Receipts | Operation_Receipts then C.Receipt_Chain else C.Causal_Chain);
         begin
            for I in E.Count range 1 .. V.Count (Data, Events) loop
               pragma Loop_Variant (Increases => I);
               declare Bounds : constant E.Span := F (Data, V.Element (Data, Events, I - 1), "boundaries");
                       Group : constant E.Span := V.Element (Data, Archives, I - 1); begin
                  for K in E.Count range 1 .. V.Count (Data, Bounds) loop
                     pragma Loop_Variant (Increases => K);
                     declare Bound : constant E.Span := V.Element (Data, Bounds, K - 1);
                             Archive : constant E.Span := V.Element (Data, Group, K - 1); begin
                        if Unique (I, K, Archive) and then S.Text_Is (Data, F (Data, Bound, "kind"), Name (Kind)) then
                           if S.Text_Is (Data, F (Data, Bound, "name"), "CANONICAL_INTENT") or else
                              S.Text_Is (Data, F (Data, Bound, "name"), "OWNER_CANONICAL_INTENT") then
                              if not Canonical_Intent_Valid (Bound, Kind) then return False; end if;
                           elsif S.Text_Is (Data, F (Data, Bound, "name"), "CANONICAL_ACK") then
                              if not Ack_Intent (I, K, Bound, Kind) then return False; end if;
                              Witness := F (Data, Bound, "head");
                           elsif S.Text_Is (Data, F (Data, Bound, "name"), "OPERATION_CHAIN_INTENT") then
                              if Kind not in Operation_Receipts | Operation_Events or else
                                 not V.Valid_Hex_Field (Data, F (Data, Bound, "payload"), "value") then return False; end if;
                              declare
                                 Payload : constant E.Bytes := Raw_Hex (Data, F (Data, Bound, "payload"));
                                 Root : constant Worldline.Hash := Domain_Hash (Payload, (Payload'First, Payload'Length),
                                    (if Kind = Operation_Receipts then "worldline-operation-use-receipt-v1" else "worldline-operation-causal-v1") & Ada.Characters.Latin_1.NUL);
                              begin
                                 if not J.Canonical_JSON_Valid (Payload, (Payload'First, Payload'Length)) or else
                                    Hex_Id (Data, F (Data, Bound, "root")) /= C.Optional_Digest'(True, Root) then return False; end if;
                                 Rows (Count + 1) := (Hex_Id (Data, F (Data, Bound, "previous")),
                                    (True, Root), Hex_Id (Data, F (Data, Bound, "root")), Hex_Id (Data, F (Data, Bound, "head")));
                                 if C.Replay (Chain, Rows (1 .. Count + 1), Genesis, Genesis,
                                    Hex_Id (Data, F (Data, Bound, "head"))).Disposition /= C.Ready then return False; end if;
                              end;
                           elsif S.Text_Is (Data, F (Data, Bound, "name"), "OPERATION_CHAIN_ACK") then
                              if not Ack_Intent (I, K, Bound, Kind) then return False; end if;
                              if Kind not in Operation_Receipts | Operation_Events or else
                                 not V.Valid_Hex_Field (Data, F (Data, Bound, "payload"), "value") then return False; end if;
                              declare
                                 Payload : constant E.Bytes := Raw_Hex (Data, F (Data, Bound, "payload"));
                                 Root : constant Worldline.Hash := Domain_Hash (Payload, (Payload'First, Payload'Length),
                                    (if Kind = Operation_Receipts then "worldline-operation-use-receipt-v1" else "worldline-operation-causal-v1") & Ada.Characters.Latin_1.NUL);
                              begin
                                 if not J.Canonical_JSON_Valid (Payload, (Payload'First, Payload'Length)) or else
                                    Hex_Id (Data, F (Data, Bound, "root")) /= C.Optional_Digest'(True, Root)
                                 then return False; end if;
                                 Count := Count + 1;
                                 Rows (Count) := (Hex_Id (Data, F (Data, Bound, "previous")),
                                    (True, Root), Hex_Id (Data, F (Data, Bound, "root")), Hex_Id (Data, F (Data, Bound, "head")));
                                 Witness := F (Data, Bound, "head");
                              end;
                           end if;
                        end if;
                     end;
                  end loop;
               end;
            end loop;
            if not Genesis.Present or else
               not Chain_Witness_Matches (Data, Raw, JF (Raw, Chains_JSON, Name (Kind)), Initial, Witness) then return False; end if;
            if Kind in Operation_Receipts | Operation_Events then
               if C.Replay (Chain, Rows (1 .. Count), Genesis, Genesis, Hex_Id (Data, Witness)).Disposition /= C.Ready then return False; end if;
            else
               if not Canonical_Chain_Corresponds (Data, Context, Kind = Receipts, Genesis, Hex_Id (Data, Witness)) then return False; end if;
            end if;
         end;
      end loop;
      return True;
   end Chains_Correspond;
   function Context (Value : L.Parsed_Input) return E.Span is
     (F (Value.Arena, Value.Owner_Roster, "operation_context"));
   function Issuer_Key (Data : E.Bytes; Roster : E.Span) return E.Span is
      Current : constant E.Span := F (Data, Roster, "current");
      Authority : constant E.Span := F (Data, F (Data, F (Data, Current, "installation"), "paths"), "authority_root");
   begin
      return F (Data, Suffix_Entry (Data, F (Data, Current, "paths"), Authority,
         "/authority/issuer/state/issuer-key.bin"), "raw");
   end Issuer_Key;
   function Issuer_Key (Value : L.Parsed_Input) return E.Span is
     (Issuer_Key (Value.Arena, Value.Owner_Roster));
   function Store_Identity_Corresponds (Data : E.Bytes; Roster, Expected : E.Span) return Boolean is
      Current : constant E.Span := F (Data, Roster, "current");
      State : constant E.Span := F (Data, F (Data, F (Data, Current, "installation"), "paths"), "state");
      Store : constant E.Span := Suffix_Entry (Data, F (Data, Current, "paths"), State, "/worldline.sqlite3");
      Tables : constant E.Span := F (Data, F (Data, Store, "logical_database"), "tables");
      Found : E.Count := 0;
   begin
      for I in E.Count range 1 .. V.Count (Data, Tables) loop
         pragma Loop_Variant (Increases => I);
         declare Table : constant E.Span := V.Element (Data, Tables, I - 1);
                 Rows : constant E.Span := F (Data, Table, "rows"); begin
            if S.Text_Is (Data, F (Data, Table, "name"), "meta") then
               for K in E.Count range 1 .. V.Count (Data, Rows) loop
                  pragma Loop_Variant (Increases => K);
                  declare Row : constant E.Span := V.Element (Data, Rows, K - 1); begin
                     if S.Text_Is (Data, V.Element (Data, Row, 1), "protectedStoreGenesis") then
                        Found := Found + 1;
                        if not V.Valid_Bytes (Data, V.Element (Data, Row, 2)) then return False; end if;
                        declare Raw : constant E.Bytes := V.Bytes_Value (Data, V.Element (Data, Row, 2)); begin
                           if not JSON_Matches (Raw, Data, (Raw'First, Raw'Length), Expected) then return False; end if;
                        end;
                     end if;
                  end;
               end loop;
            end if;
         end;
      end loop;
      return Found = 1;
   end Store_Identity_Corresponds;
   function Profile_Authenticated
     (Data : E.Bytes; Roster : E.Span; Owner_Context : O.Prepared_History;
      Resource_Context : K.Prepared_History; Require_Head : Boolean) return Boolean is
      Ctx : constant E.Span := F (Data, Roster, "operation_context");
      Current : constant E.Span := F (Data, Roster, "current");
      Installation : constant E.Span := F (Data, Current, "installation");
      Paths : constant E.Span := F (Data, Current, "paths");
      Authority : constant E.Span := F (Data, F (Data, Installation, "paths"), "authority_root");
      Policy : constant E.Span := F (Data, Ctx, "policy");
      Binding : constant E.Span := F (Data, Ctx, "binding");
      Owner : constant E.Span := F (Data, Ctx, "owner_genesis");
      Lease : constant E.Span := F (Data, Ctx, "lease_genesis");
      Key_Item : constant E.Span := Issuer_Key (Data, Roster);
      Policy_Item : constant E.Span := F (Data, Suffix_Entry (Data, Paths, Authority,
         "/authority/issuer/state/worldline-operation-policy.json"), "raw");
      Owner_Item : constant E.Span := F (Data, Path_Entry (Data, Paths, F (Data, Policy, "genesis_file")), "raw");
      Lease_Item : constant E.Span := F (Data, Path_Entry (Data, Paths, F (Data, Installation, "genesis")), "raw");
      Journal_Item : constant E.Span := F (Data, Path_Entry (Data, Paths, F (Data, Policy, "journal")), "raw");
      Head_DB : constant E.Span := F (Data, Path_Entry (Data, Paths, F (Data, Policy, "head_database")), "logical_database");
      Universe_Item : constant E.Span := F (Data, Path_Entry (Data, Paths, F (Data, Ctx, "universe_genesis_path")), "raw");
      Integrity : constant E.Span := F (Data, Head_DB, "integrity");
      Mode : constant E.Span := F (Data, Ctx, "head_database_journal_mode");
   begin
      if not O.Current_Matches (Owner_Context) or else
         not K.Current_Matches (Resource_Context) or else
         not V.Valid_Bytes (Data, Key_Item) or else not V.Valid_Bytes (Data, Policy_Item) or else
         not V.Valid_Bytes (Data, Owner_Item) or else not V.Valid_Bytes (Data, Lease_Item) or else
         not V.Valid_Bytes (Data, Journal_Item) or else not V.Valid_Bytes (Data, Universe_Item) or else
         not Same (Data, Lease_Item, F (Data, Ctx, "lease_genesis_raw")) or else
         not Same (Data, Universe_Item, F (Data, Ctx, "universe_genesis_raw")) or else
         not Joined (Data, F (Data, Policy, "journal"), Authority, "/authority/issuer/state/worldline-operations.json") or else
         not Joined (Data, F (Data, Policy, "head_database"), Authority, "/authority/issuer/state/worldline-operation-head.sqlite") or else
         (Require_Head and then
           (V.Count (Data, Integrity) /= 1 or else V.Count (Data, V.Element (Data, Integrity, 0)) /= 1 or else
            not S.Text_Is (Data, V.Element (Data, V.Element (Data, Integrity, 0), 0), "ok") or else
            V.Count (Data, Mode) /= 1 or else V.Count (Data, V.Element (Data, Mode, 0)) /= 1 or else
            not S.Text_Is (Data, V.Element (Data, V.Element (Data, Mode, 0), 0), "wal"))) then return False; end if;
      declare
         Key : constant E.Bytes := V.Bytes_Value (Data, Key_Item);
         Policy_Raw : constant E.Bytes := V.Bytes_Value (Data, Policy_Item);
         Owner_Raw : constant E.Bytes := V.Bytes_Value (Data, Owner_Item);
         Lease_Raw : constant E.Bytes := V.Bytes_Value (Data, Lease_Item);
         Journal_Raw : constant E.Bytes := V.Bytes_Value (Data, Journal_Item);
         Universe_Raw : constant E.Bytes := V.Bytes_Value (Data, Universe_Item);
         Policy_JSON : constant E.Span := JSON (Policy_Raw, (Policy_Raw'First, Policy_Raw'Length));
         Owner_JSON : constant E.Span := JF (Owner_Raw, JSON (Owner_Raw, (Owner_Raw'First, Owner_Raw'Length)), "body");
         Journal_JSON : constant E.Span := JF (Journal_Raw, JSON (Journal_Raw, (Journal_Raw'First, Journal_Raw'Length)), "body");
         Initial_Grants : constant E.Span := JF (Owner_Raw, JF (Owner_Raw, JF (Owner_Raw, Owner_JSON, "initial_envelope"), "body"), "grants");
         Prefix : constant E.Span := F (Data, F (Data, Owner, "resource"), "events");
         Resource_Events : constant E.Span := F (Data, Ctx, "resource_events");
      begin
         if not JSON_Keys (Policy_Raw, Policy_JSON,
             "schema,installation,owner_uid,issuer,genesis,journal,selection,chains,issuer_policy,store_genesis,source_inventory,resource_descriptor,plans,broker,head_database,genesis_file", 16) or else
            not JSON_Matches (Policy_Raw, Data, Policy_JSON, Policy) or else
            not S.Text_Is (Data, F (Data, Policy, "schema"), "worldline.operation-policy-v1") or else
            not Same (Data, F (Data, Policy, "owner_uid"), F (Data, F (Data, Ctx, "owner_binding"), "owner_uid")) or else
            not Same (Data, F (Data, Policy, "issuer_policy"), F (Data, F (Data, Ctx, "owner_binding"), "issuer_policy_sha256")) or else
            not Same (Data, F (Data, Policy, "installation"), F (Data, Installation, "installation_id")) or else
            not Same (Data, F (Data, Binding, "installation"), F (Data, Installation, "installation_id")) or else
            not Same (Data, F (Data, Binding, "genesis"), F (Data, Policy, "genesis")) or else
            not Same (Data, F (Data, Binding, "store_genesis"), F (Data, Policy, "store_genesis")) or else
            not Same (Data, F (Data, Policy, "store_genesis"), F (Data, F (Data, Lease, "store"), "identity")) or else
            not Store_Identity_Corresponds (Data, Roster, F (Data, Policy, "store_genesis")) or else
            not V.Valid_Hex_Field (Data, F (Data, Binding, "policy_bytes"), "value") or else
            Raw_Hex (Data, F (Data, Binding, "policy_bytes")) /= Policy_Raw or else
            not Digest_Text (Data, F (Data, Binding, "issuer_key"), H.C.G.Hash (Key, (Key'First, Key'Length))) or else
            not JSON_Matches (Lease_Raw, Data, (Lease_Raw'First, Lease_Raw'Length), Lease) or else
            not Envelope_Authenticated (Key, Owner_Raw, (Key'First, Key'Length), (Owner_Raw'First, Owner_Raw'Length),
               Domain & "owner-genesis" & Ada.Characters.Latin_1.NUL) or else
            not JSON_Keys (Owner_Raw, Owner_JSON, "schema,installation,installation_genesis,binding,gate_head,issuer_head,universe,store,resource,owner,initial_envelope", 11) or else
            not JSON_Matches (Owner_Raw, Data, Owner_JSON, Owner) or else
            not V.Valid_Bytes (Data, F (Data, Ctx, "owner_genesis_raw")) or else
            not J.Operation_Archive_JSON_Matches (Owner_Raw, V.Bytes_Value (Data, F (Data, Ctx, "owner_genesis_raw")),
               Owner_JSON, (1, V.Bytes_Value (Data, F (Data, Ctx, "owner_genesis_raw"))'Length)) or else
            not S.Text_Is (Data, F (Data, Owner, "schema"), "worldline.operation-owner-genesis-v1") or else
            not Same (Data, F (Data, Owner, "installation"), F (Data, Installation, "installation_id")) or else
            not Same (Data, F (Data, Owner, "binding"), Binding) or else
            not Same (Data, F (Data, Owner, "owner"), F (Data, Ctx, "owner_binding")) or else
            not Digest_Text (Data, F (Data, Owner, "installation_genesis"), H.C.G.Hash (Lease_Raw, (Lease_Raw'First, Lease_Raw'Length))) or else
            not Same (Data, F (Data, Owner, "gate_head"), F (Data, Lease, "gate_head")) or else
            not Same (Data, F (Data, Owner, "issuer_head"), F (Data, Lease, "issuer_head")) or else
            not Same (Data, F (Data, Owner, "store"), F (Data, Lease, "store")) or else
            not Same (Data, F (Data, F (Data, Owner, "resource"), "genesis"), F (Data, Ctx, "resource_genesis")) or else
            not Digest_Text (Data, F (Data, Ctx, "universe_genesis_sha256"), H.C.G.Hash (Universe_Raw, (Universe_Raw'First, Universe_Raw'Length))) or else
            not Same (Data, F (Data, F (Data, Owner, "universe"), "genesis_sha256"), F (Data, Ctx, "universe_genesis_sha256")) or else
            not V.Is_Sequence (Data, Prefix) or else not V.Is_Sequence (Data, Resource_Events) or else
            V.Count (Data, Prefix) > V.Count (Data, Resource_Events) or else
            not Envelope_Authenticated (Key, Journal_Raw, (Key'First, Key'Length), (Journal_Raw'First, Journal_Raw'Length), Domain) or else
            not JSON_Keys (Journal_Raw, Journal_JSON, "schema,binding,grants,events,chains", 5) or else
            J.JSON_Prefix (Journal_Raw, JF (Journal_Raw, Journal_JSON, "grants"),
               0).Form /= J.Array_JSON_Value or else
            not JSON_Matches (Journal_Raw, Data, Journal_JSON, F (Data, Ctx, "journal")) or else
            not JSON_Is (Journal_Raw, JF (Journal_Raw, Journal_JSON, "schema"), "worldline.canonical-operation-journal-v1") or else
            not JSON_Matches (Journal_Raw, Data, JF (Journal_Raw, Journal_JSON, "binding"), Binding) or else
            not Raw_Same (Journal_Raw, Owner_Raw, JF (Journal_Raw, Journal_JSON, "grants"), Initial_Grants) or else
            (Require_Head and then not Head_Corresponds (Data, Key, Journal_Raw, Owner_Raw, Head_DB,
               F (Data, Installation, "installation_id"), Policy, Ctx)) then return False; end if;
         for I in E.Count range 1 .. V.Count (Data, Prefix) loop
            pragma Loop_Variant (Increases => I);
            if not Same (Data, V.Element (Data, Prefix, I - 1), V.Element (Data, Resource_Events, I - 1)) then return False; end if;
         end loop;
      end;
      return True;
   end Profile_Authenticated;
   function Raw_Current_Authenticated
     (Data : E.Bytes; Roster : E.Span; Owner_Context : O.Prepared_History;
      Resource_Context : K.Prepared_History; Require_Head : Boolean) return Boolean is
      Ctx : constant E.Span := F (Data, Roster, "operation_context");
      Current : constant E.Span := F (Data, Roster, "current");
      Policy : constant E.Span := F (Data, Ctx, "policy");
      Journal : constant E.Span := F (Data, Ctx, "journal");
      Events : constant E.Span := F (Data, Journal, "events");
      Raw_Item : constant E.Span := F (Data, Path_Entry (Data, F (Data, Current, "paths"), F (Data, Policy, "journal")), "raw");
   begin
      if not Profile_Authenticated (Data, Roster, Owner_Context, Resource_Context, Require_Head) then return False; end if;
      declare Raw : constant E.Bytes := V.Bytes_Value (Data, Raw_Item);
              Body_JSON : constant E.Span := JF (Raw, JSON (Raw, (Raw'First, Raw'Length)), "body"); begin
         return History_Corresponds (Data, Raw, Body_JSON, Events,
            F (Data, Ctx, "operation_authority_observations"), Events, Ctx, Policy, Owner_Context, Resource_Context) and then
            Boundaries_Correspond (Data, Events, Ctx) and then
            Chains_Correspond (Data, Raw, Body_JSON, Events, Roster, Policy, F (Data, Ctx, "boundary_archives"));
      end;
   end Raw_Current_Authenticated;
   function Current_Authenticated
     (Value : L.Parsed_Input; Owner_Context : O.Prepared_History;
      Resource_Context : K.Prepared_History) return Boolean is
     (Value.Status = L.Parsed and then
      Worldline.Custody_V2_Owner_Correspondence.Owner_Corresponds (Value) and then
      O.Source_Matches (Owner_Context, Value.Arena, Value.Owner_Roster) and then
      K.Source_Matches (Resource_Context, Value.Arena, Value.Owner_Roster) and then
      Raw_Current_Authenticated (Value.Arena, Value.Owner_Roster,
         Owner_Context, Resource_Context, Require_Head => True));
   function Current_Authenticated (Value : L.Parsed_Input) return Boolean is
      Facts : constant E.Bytes := O.Extract_Replay_Capsules (Value.Arena, Value.Owner_Roster);
      Owner_Context : O.Prepared_History;
      Resource_Context : K.Prepared_History;
   begin
      if Value.Status /= L.Parsed then return False; end if;
      O.Establish_History (Owner_Context, Value.Arena, Facts, Value.Owner_Roster);
      K.Establish_History (Resource_Context, Value.Arena, Value.Owner_Roster);
      return Current_Authenticated (Value, Owner_Context, Resource_Context);
   end Current_Authenticated;
   function Head_Fact (Value : L.Parsed_Input) return Head_Disposition is
      Data : E.Bytes renames Value.Arena;
      Current : constant E.Span := F (Data, Value.Owner_Roster, "current");
      Policy : constant E.Span := F (Data, Context (Value), "policy");
      DB : constant E.Span := F (Data, Path_Entry (Data, F (Data, Current, "paths"), F (Data, Policy, "head_database")), "logical_database");
      Head : constant E.Span := Table_Row (Data, DB, "canonical_operation_head",
         "name,installation,genesis,head,state,prior_envelope,next_envelope", 7);
   begin
      if S.Text_Is (Data, Row_Value (Data, Head, 5, 7), "STABLE") then return Stable; end if;
      return Finalize_Surviving_Next;
   end Head_Fact;
   function Preparations_Fact (Value : L.Parsed_Input) return Boolean is
      Data : E.Bytes renames Value.Arena;
      Events : constant E.Span := F (Data, F (Data, Context (Value), "journal"), "events");
      Found : Boolean;
   begin
      for I in E.Count range 1 .. V.Count (Data, Events) loop
         pragma Loop_Variant (Increases => I);
         declare Event : constant E.Span := V.Element (Data, Events, I - 1); begin
            if S.Text_Is (Data, F (Data, Event, "cause"), "PREPARATION") then
               Found := False;
               if I < V.Count (Data, Events) then
                  for K in E.Count range I + 1 .. V.Count (Data, Events) loop
                     pragma Loop_Variant (Increases => K);
                     declare Other : constant E.Span := V.Element (Data, Events, K - 1); begin
                        if Cause (Data, Other) /= Absent and then Same (Data, F (Data, Event, "operation"), F (Data, Other, "operation")) then Found := True; end if;
                     end;
                  end loop;
               end if;
               if not Found then return False; end if;
            end if;
         end;
      end loop;
      return True;
   end Preparations_Fact;
   -- Cache identity covers the entire owned arena AND every decoded operand.
   -- It serializes field values, never record padding, addresses or a producer
   -- verdict. Mutating a decoded span/row without changing bytes invalidates it.
   function Operand_Digest (Value : L.Parsed_Input) return Worldline.Hash is
      package RS renames L.S;
      package M renames L.N.M;
      Ctx : H.SHA.Context := H.SHA.Initial;
      procedure Number (N : E.Count) is
         X : Interfaces.Unsigned_64 := Interfaces.Unsigned_64 (N);
         Encoded : Attest.Byte_Array (0 .. 7);
      begin
         for I in Encoded'Range loop
            pragma Loop_Variant (Increases => I);
            Encoded (I) := Q.Byte (X mod 256);
            X := X / 256;
         end loop;
         H.SHA.Update (Ctx, Encoded);
      end Number;
      procedure Bit (B : Boolean) is
      begin
         H.SHA.Update (Ctx, Attest.Byte_Array'(0 => (if B then 1 else 0)));
      end Bit;
      procedure Span (Item : E.Span) is
      begin
         Number (Item.First); Number (Item.Length);
      end Span;
      procedure Quantity (Item : Q.Quantity) is
      begin
         Bit (Item.Negative); Number (Item.First); Number (Item.Length);
      end Quantity;
      procedure Identity (Item : M.Identity) is
      begin
         Bit (Item.Present);
         if Item.Present then Number (Item.Value.First); Number (Item.Value.Length); end if;
      end Identity;
      procedure Cell (Item : RS.SQL_Cell) is
      begin
         Number (RS.SQL_Class'Pos (Item.Kind));
         case Item.Kind is
            when RS.SQL_Null => null;
            when RS.SQL_Integer => Quantity (Item.Integer_Value);
            when RS.SQL_Text | RS.SQL_Blob | RS.SQL_Real =>
               Number (Item.Bytes.First); Number (Item.Bytes.Length);
         end case;
      end Cell;
      procedure SQL (Rows : L.SQL_Rows) is
      begin
         for I in Rows'Range (1) loop
            pragma Loop_Variant (Increases => I);
            for K in Rows'Range (2) loop
               pragma Loop_Variant (Increases => K);
               Cell (Rows (I, K));
            end loop;
         end loop;
      end SQL;
      procedure Spans (Items : L.Span_Array) is
      begin
         for I in Items'Range loop
            pragma Loop_Variant (Increases => I);
            Span (Items (I));
         end loop;
      end Spans;
   begin
      for I in Value.Events'Range loop
         pragma Loop_Variant (Increases => I);
         declare Row : L.C.Event_Row renames Value.Events (I);
                 Extra : L.Event_Extra renames Value.Extras (I); begin
            Span (Row.Event_Id);
            Span (Row.Previous);
            Span (Row.Generation);
            Span (Row.Operation);
            Span (Row.Subject_Kind);
            Span (Row.Subject);
            Span (Row.Subgeneration);
            Span (Row.Kind);
            Span (Row.Actor);
            Span (Row.Record_Archive);
            Span (Row.Base_Archive);
            Span (Row.Mac);
            Cell (Extra.Reattach_Epoch);
            Cell (Extra.Position);
            Cell (Extra.Next_Subgeneration);
            Cell (Extra.Transfer_Mode);
            Cell (Extra.Abort_Class);
            Cell (Extra.Unknown_Cause);
            Span (Extra.Cause_Archive);
            Span (Extra.Original_Payload);
            Span (Extra.Root_Evidence_Payload);
            Span (Extra.Native_Observations_Payload);
            Span (Extra.Subject_Evidence_Payload);
            Number (L.Original_Format'Pos (Extra.Original_Encoding));
            Number (L.Original_Format'Pos (Extra.Root_Evidence_Encoding));
            Number (L.Original_Format'Pos (Extra.Native_Observations_Encoding));
            Number (L.Original_Format'Pos (Extra.Subject_Evidence_Encoding));
         end;
      end loop;
      for I in Value.Heads'Range loop
         pragma Loop_Variant (Increases => I);
         declare Row : L.C.Head_Row renames Value.Heads (I); begin
            Span (Row.Name); Span (Row.Kind); Span (Row.Mac); Span (Row.Message);
            Bit (Row.Event_Id.Present);
            if Row.Event_Id.Present then Span (Row.Event_Id.Value); end if;
            Bit (Row.Origin.Present);
            if Row.Origin.Present then Span (Row.Origin.Value); end if;
         end;
      end loop;
      for I in Value.Roots'Range loop
         pragma Loop_Variant (Increases => I);
         Bit (Value.Roots (I).Present);
         if Value.Roots (I).Present then
            declare Row : RS.Root_Columns renames Value.Roots (I).Columns; begin
               Cell (Row.Generation);
               Cell (Row.Operation);
               Cell (Row.Phase);
               Cell (Row.Before_Unknown);
               Cell (Row.Owners_Open);
               Cell (Row.Abort_Kind);
               Cell (Row.Launched);
               Cell (Row.Closure_NS);
               Cell (Row.Closure_Outer);
               Cell (Row.Closure_Raw);
               Cell (Row.Witness);
               Cell (Row.Settled);
               Cell (Row.Released_Unlaunched);
               Cell (Row.Unknown_Cause);
               Cell (Row.Reattach_Epoch);
               Cell (Row.Head_Event);
            end;
         end if;
      end loop;
      for I in Value.Subjects'Range loop
         pragma Loop_Variant (Increases => I);
         Bit (Value.Subjects (I).Present);
         if Value.Subjects (I).Present then
            declare Row : RS.Subject_Columns renames Value.Subjects (I).Columns; begin
               Cell (Row.Generation);
               Cell (Row.Kind_Of_Subject);
               Cell (Row.Subject);
               Cell (Row.Subgeneration);
               Cell (Row.Phase);
               Cell (Row.Mode);
               Cell (Row.Position);
               Cell (Row.Carried_From);
               Cell (Row.Head_Event);
            end;
         end if;
      end loop;
      for I in Value.Alternatives'Range loop
         pragma Loop_Variant (Increases => I);
         declare Row : L.A.Alternative_Row renames Value.Alternatives (I); begin
            Quantity (Row.Generation); Identity (Row.Operation);
            Number (M.Subject_Kind'Pos (Row.Kind_Of_Subject)); Identity (Row.Subject);
            Quantity (Row.Subgeneration); Number (L.A.Alternative_Set'Pos (Row.Set));
            for B of Row.Event_Id loop H.SHA.Update (Ctx, Attest.Byte_Array'(0 => B)); end loop;
         end;
      end loop;
      Span (Value.Source_Input);
      Span (Value.Startup_Capture_Payload);
      Number (L.Original_Format'Pos (Value.Startup_Capture_Encoding));
      SQL (Value.Event_SQL); SQL (Value.Head_SQL); SQL (Value.Root_SQL);
      SQL (Value.Subject_SQL); SQL (Value.Alternative_SQL); SQL (Value.Blob_SQL);
      Spans (Value.Event_Encoded); Spans (Value.Head_Encoded); Spans (Value.Root_Encoded);
      Spans (Value.Subject_Encoded); Spans (Value.Alternative_Encoded); Spans (Value.Blob_Encoded);
      for P in M.Root_Phase loop Cell (Value.Symbols.Root (P)); end loop;
      for P in M.Request_Phase loop Cell (Value.Symbols.Request (P)); end loop;
      for P in M.Descriptor_Phase loop Cell (Value.Symbols.Descriptor (P)); end loop;
      for P in M.Abort_Class loop Cell (Value.Symbols.Abort_Name (P)); end loop;
      for P in M.Transfer_Mode loop Cell (Value.Symbols.Mode (P)); end loop;
      Cell (Value.Symbols.Zero); Cell (Value.Symbols.One);
      Cell (Value.Symbols.Zero_Magnitude); Cell (Value.Symbols.Empty_Text);
      return Hash_Value (H.SHA.Final (Ctx));
   end Operand_Digest;
   procedure Establish
     (Value : L.Parsed_Input; Owner_Context : O.Prepared_History;
      Resource_Context : K.Prepared_History; Proof : out Journal_Proof) is
   begin
      Proof := (others => <>);
      if not Current_Authenticated (Value, Owner_Context, Resource_Context) then return; end if;
      Proof.Arena_Count := Value.Arena_Count; Proof.Arena_Used := Value.Arena_Used;
      Proof.Decoded_Events := Value.Decoded_Event_Count;
      Proof.Events := Value.Event_Count; Proof.Heads := Value.Head_Count;
      Proof.Roots := Value.Root_Count; Proof.Subjects := Value.Subject_Count;
      Proof.Alternatives := Value.Alternative_Count; Proof.Blobs := Value.Blob_Count;
      Proof.Owner_Roster := Value.Owner_Roster; Proof.Input := Value.Input;
      Proof.Source_Input := Value.Source_Input;
      Proof.Key := Value.Key; Proof.Genesis_File := Value.Genesis_File;
      Proof.Genesis_Row := Value.Genesis_Row; Proof.Genesis_Message := Value.Genesis_Message;
      Proof.Genesis_Mac := Value.Genesis_Mac;
      Proof.Arena_Digest := H.C.G.Hash (Value.Arena, (Value.Arena'First, Value.Arena_Count));
      Proof.Operand_Digest := Operand_Digest (Value);
      Proof.Head := Head_Fact (Value);
      Proof.Preparations := (if Preparations_Fact (Value) then Complete else Pending);
      Proof.State := Original_Current_Replayed;
   end Establish;
   procedure Establish (Value : L.Parsed_Input; Proof : out Journal_Proof) is
      Facts : constant E.Bytes := O.Extract_Replay_Capsules (Value.Arena, Value.Owner_Roster);
      Owner_Context : O.Prepared_History;
      Resource_Context : K.Prepared_History;
   begin
      Proof := (others => <>);
      if Value.Status /= L.Parsed then return; end if;
      O.Establish_History (Owner_Context, Value.Arena, Facts, Value.Owner_Roster);
      K.Establish_History (Resource_Context, Value.Arena, Value.Owner_Roster);
      Establish (Value, Owner_Context, Resource_Context, Proof);
   end Establish;
   function Established (Value : L.Parsed_Input; Proof : Journal_Proof) return Boolean is
     (Value.Status = L.Parsed and then Proof.State = Original_Current_Replayed and then
      Proof.Arena_Count = Value.Arena_Count and then Proof.Arena_Used = Value.Arena_Used and then
      Proof.Decoded_Events = Value.Decoded_Event_Count and then
      Proof.Events = Value.Event_Count and then Proof.Heads = Value.Head_Count and then
      Proof.Roots = Value.Root_Count and then Proof.Subjects = Value.Subject_Count and then
      Proof.Alternatives = Value.Alternative_Count and then Proof.Blobs = Value.Blob_Count and then
      Proof.Owner_Roster = Value.Owner_Roster and then Proof.Input = Value.Input and then
      Proof.Source_Input = Value.Source_Input and then
      Proof.Key = Value.Key and then Proof.Genesis_File = Value.Genesis_File and then
      Proof.Genesis_Row = Value.Genesis_Row and then Proof.Genesis_Message = Value.Genesis_Message and then
      Proof.Genesis_Mac = Value.Genesis_Mac and then
      Proof.Arena_Digest = H.C.G.Hash (Value.Arena, (Value.Arena'First, Value.Arena_Count)) and then
      Proof.Operand_Digest = Operand_Digest (Value));
   procedure Startup_Decide
     (Value : L.Parsed_Input; Proof : Journal_Proof; Current_Matches : out Boolean;
      Head : out Head_Disposition; Preparations_Done : out Boolean) is
   begin
      Current_Matches := Established (Value, Proof);
      Head := Refused; Preparations_Done := False;
      if Current_Matches then
         Head := Proof.Head; Preparations_Done := Proof.Preparations = Complete;
      end if;
   end Startup_Decide;
   procedure Startup_Decide
     (Value : L.Parsed_Input; Current_Matches : out Boolean;
      Head : out Head_Disposition; Preparations_Done : out Boolean) is
   begin
      Current_Matches := Current_Authenticated (Value);
      Head := Refused; Preparations_Done := False;
      if Current_Matches then
         Head := Head_Fact (Value);
         Preparations_Done := Preparations_Fact (Value);
      end if;
   end Startup_Decide;
   function Head_Action (Value : L.Parsed_Input) return Head_Disposition is
   begin
      if not Current_Authenticated (Value) then return Refused; end if;
      return Head_Fact (Value);
   end Head_Action;
   function Preparations_Complete (Value : L.Parsed_Input) return Boolean is
     (Current_Authenticated (Value) and then Preparations_Fact (Value));
   function Candidate_History (Value : L.Parsed_Input; Candidate : E.Span) return Boolean is
      Data : E.Bytes renames Value.Arena;
      Ctx : constant E.Span := Context (Value);
      Before : constant E.Span := F (Data, Ctx, "journal");
      Events : constant E.Span := F (Data, F (Data, Candidate, "body"), "events");
      Current_Events : constant E.Span := F (Data, Before, "events");
      Key_Item : constant E.Span := Issuer_Key (Value);
      Raw_Item : constant E.Span := F (Data, Candidate, "raw");
      Facts : constant E.Bytes := O.Extract_Replay_Capsules (Data, Value.Owner_Roster);
      Owner_Context : O.Prepared_History;
      Resource_Context : K.Prepared_History;
   begin
      if Value.Status /= L.Parsed then return False; end if;
      O.Establish_History (Owner_Context, Value.Arena, Facts, Value.Owner_Roster);
      K.Establish_History (Resource_Context, Value.Arena, Value.Owner_Roster);
      if not Current_Authenticated (Value, Owner_Context, Resource_Context) or else not V.Valid_Bytes (Data, Raw_Item) or else
         not V.Is_Sequence (Data, Events) or else
         V.Count (Data, Events) = 0 or else V.Count (Data, Events) - 1 /= V.Count (Data, Current_Events) then return False; end if;
      declare
         Key : constant E.Bytes := V.Bytes_Value (Data, Key_Item);
         Raw : constant E.Bytes := V.Bytes_Value (Data, Raw_Item);
         Body_JSON : constant E.Span := JF (Raw, JSON (Raw, (Raw'First, Raw'Length)), "body");
      begin
         if not Envelope_Authenticated (Key, Raw, (Key'First, Key'Length), (Raw'First, Raw'Length), Domain) or else
            not JSON_Keys (Raw, Body_JSON, "schema,binding,grants,events,chains", 5) or else
            not JSON_Matches (Raw, Data, Body_JSON, F (Data, Candidate, "body")) or else
            not Same (Data, F (Data, F (Data, Candidate, "body"), "schema"), F (Data, Before, "schema")) or else
            not Same (Data, F (Data, F (Data, Candidate, "body"), "binding"), F (Data, Before, "binding")) or else
            not Same (Data, F (Data, F (Data, Candidate, "body"), "grants"), F (Data, Before, "grants")) then return False; end if;
            for I in E.Count range 1 .. V.Count (Data, Current_Events) loop
               pragma Loop_Variant (Increases => I);
               if not Same (Data, V.Element (Data, Events, I - 1), V.Element (Data, Current_Events, I - 1)) then return False; end if;
               if Cause (Data, V.Element (Data, Current_Events, I - 1)) /= Absent or else
                  S.Text_Is (Data, F (Data, V.Element (Data, Current_Events, I - 1), "cause"), "ACK") then
                  if not Same (Data, Native_Item (Data, F (Data, Candidate, "operation_authority_observations"), V.Element (Data, Current_Events, I - 1)),
                     Native_Item (Data, F (Data, Ctx, "operation_authority_observations"), V.Element (Data, Current_Events, I - 1))) then return False; end if;
               end if;
            end loop;
            return History_Corresponds (Data, Raw, Body_JSON, Events,
               F (Data, Candidate, "operation_authority_observations"), Events, Ctx, F (Data, Ctx, "policy"), Owner_Context, Resource_Context, V.Count (Data, Current_Events)) and then
               Boundaries_Correspond (Data, Events, Ctx) and then
               Chains_Correspond (Data, Raw, Body_JSON, Events, Value.Owner_Roster, F (Data, Ctx, "policy"), F (Data, Candidate, "boundary_archives"));
      end;
   end Candidate_History;
   function Append_Allowed (Value : L.Parsed_Input; Candidate : E.Span) return Boolean is
     (Candidate_History (Value, Candidate));
   function Authenticated (Value : L.Parsed_Input; Index : Q.Byte_Count) return Boolean is
      Proof : Journal_Proof;
   begin
      if Value.Status /= L.Parsed or else Index not in Value.Events'Range then return False; end if;
      Establish (Value, Proof);
      return Authenticated (Value, Index, Proof);
   end Authenticated;
   function Authenticated (Value : L.Parsed_Input; Index : Q.Byte_Count; Proof : Journal_Proof) return Boolean is
      Data : E.Bytes renames Value.Arena;
      X5 : E.Span;
      Raw_Item, Events, Ctx, Current, Policy : E.Span;
   begin
      if Value.Status /= L.Parsed or else Index not in Value.Events'Range or else
         not Established (Value, Proof) then return False; end if;
      X5 := F (Data, Value.Events (Index).Record_Archive, "x5");
      Ctx := Context (Value); Current := F (Data, Value.Owner_Roster, "current");
      Policy := F (Data, Ctx, "policy");
      Raw_Item := F (Data, X5, "operation_journal");
      Events := F (Data, X5, "operation_journal_events");
      if not V.Valid_Bytes (Data, Raw_Item) or else not V.Is_Sequence (Data, Events) or else
         V.Count (Data, Events) > V.Count (Data, F (Data, F (Data, Ctx, "journal"), "events")) or else
         not Same (Data, F (Data, X5, "source_identity"), F (Data, Current, "source")) then return False; end if;
      declare
         Key : constant E.Bytes := V.Bytes_Value (Data, Issuer_Key (Value));
         Raw : constant E.Bytes := V.Bytes_Value (Data, Raw_Item);
         Body_JSON : constant E.Span := JF (Raw, JSON (Raw, (Raw'First, Raw'Length)), "body");
         Journal : constant E.Span := F (Data, Ctx, "journal");
         Actual_Events : constant E.Span := F (Data, Journal, "events");
         Items : constant E.Span := F (Data, X5, "operation_authority_observations");
         Found : E.Count := 0;
      begin
         if not Envelope_Authenticated (Key, Raw, (Key'First, Key'Length), (Raw'First, Raw'Length), Domain) or else
            not JSON_Keys (Raw, Body_JSON, "schema,binding,grants,events,chains", 5) or else
            not JSON_Is (Raw, JF (Raw, Body_JSON, "schema"), "worldline.canonical-operation-journal-v1") or else
            not JSON_Matches (Raw, Data, JF (Raw, Body_JSON, "binding"), F (Data, Journal, "binding")) or else
            not JSON_Matches (Raw, Data, JF (Raw, Body_JSON, "grants"), F (Data, Journal, "grants")) or else
            not JSON_Matches (Raw, Data, JF (Raw, Body_JSON, "events"), Events) then return False; end if;
         for I in E.Count range 1 .. V.Count (Data, Events) loop
            pragma Loop_Variant (Increases => I);
            declare Event : constant E.Span := V.Element (Data, Events, I - 1); begin
               if not Same (Data, Event, V.Element (Data, Actual_Events, I - 1)) then return False; end if;
               if not S.Text_Is (Data, F (Data, Event, "cause"), "PREPARATION") and then
                  not S.Text_Is (Data, F (Data, Event, "cause"), "OWNER_CANONICAL") then
                  Found := Found + 1;
                  if not Same (Data, Native_Item (Data, Items, Event),
                     Native_Item (Data, F (Data, Ctx, "operation_authority_observations"), Event)) then return False; end if;
               end if;
            end;
         end loop;
         return Found = V.Count (Data, Items) and then
            Prefix_Chains_Correspond (Data, Raw, Body_JSON, Events, Policy, F (Data, Ctx, "boundary_archives"));
      end;
   end Authenticated;
   function Recovery_Decide
     (Value : L.Parsed_Input; Operation : E.Span; Proof : Journal_Proof)
      return Recovery_Action
   is
      Data : E.Bytes renames Value.Arena;
      Events : constant E.Span := F (Data, F (Data, Context (Value), "journal"), "events");
      Latest : E.Span := (1, 0);
      State : Journal_State := Absent;
      Prepared : Boolean := False;
      function Has_Boundary (Name : String) return Boolean is
         Bounds : constant E.Span := F (Data, Latest, "boundaries");
      begin
         for I in E.Count range 1 .. V.Count (Data, Bounds) loop
            pragma Loop_Variant (Increases => I);
            if S.Text_Is (Data, F (Data, V.Element (Data, Bounds, I - 1), "name"), Name) then
               return True;
            end if;
         end loop;
         return False;
      end Has_Boundary;
   begin
      -- The proof includes fresh complete owner/source/current physical/native
      -- capture, all original history, independent head and full native material.
      -- No route is synthesized from a matching DTO, an old RESERVE result or
      -- a caller's latest-state label. Authentic incomplete preparations stay
      -- unresolved for diagnosis, never become RESERVED or native authority.
      if not Established (Value, Proof) or else
         Proof.Head /= Stable or else not V.Valid_Text (Data, Operation) then
         return Recovery_Refused;
      end if;
      for I in E.Count range 1 .. V.Count (Data, Events) loop
         pragma Loop_Variant (Increases => I);
         declare Event : constant E.Span := V.Element (Data, Events, I - 1); begin
            if Same (Data, Operation, F (Data, Event, "operation")) then
               if S.Text_Is (Data, F (Data, Event, "cause"), "PREPARATION") then
                  Prepared := True;
               elsif not S.Text_Is (Data, F (Data, Event, "cause"), "OWNER_CANONICAL") then
                  Latest := Event;
                  if not S.Text_Is (Data, F (Data, Event, "cause"), "ACK") then
                     State := Cause (Data, Event);
                  end if;
               end if;
            end if;
         end;
      end loop;
      -- These are precisely the original routes and precedence. A missing
      -- ordinary row is not a completed/no-action operation.
      case State is
         when Absent => return (if Prepared then Retain_Unresolved else Recovery_Refused);
         when Released => return No_Recovery;
         when Resolved_Effect | Resolved_No_Effect => return Recover_Owner_Resolution;
         when Effect_Observed | Settled => return Recover_Committed;
         when Effect_Intent =>
            if Has_Boundary ("RESULT_CAPTURE") then return Recover_Committed;
            elsif Has_Boundary ("FULL_BROKER_PREPARED") then return Recover_Full_Broker;
            else return Retain_Unresolved;
            end if;
         when Quarantined =>
            if Has_Boundary ("FULL_BROKER_OWNER_DISPOSITION") then return Recover_K4;
            else return Retain_Unresolved;
            end if;
         when Reserved => return Retain_Unresolved;
      end case;
   end Recovery_Decide;
   function Recovery_Decide
     (Value : L.Parsed_Input; Operation : E.Span) return Recovery_Action
   is
      Proof : Journal_Proof;
   begin
      Establish (Value, Proof);
      return Recovery_Decide (Value, Operation, Proof);
   end Recovery_Decide;
   -- The fixed archive composition is projected without materializing each
   -- proc image, path or fdinfo into another byte array. This is syntax only.
   package B64 renames Worldline.Archive_Base64;
   package Install renames Worldline.Startup_Installation;
   subtype U64 is Interfaces.Unsigned_64;
   type Scalar_Bytes is record
      Valid, Hex : Boolean := False;
      Payload : E.Byte_View;
      Length : E.Count := 0;
   end record;
   function View_Length (Data : E.Bytes; Item : E.Byte_View) return E.Count
     with Global => null, Subprogram_Variant => (Decreases => Item.Level);
   function View_Byte (Data : E.Bytes; Item : E.Byte_View; Offset : E.Count) return Q.Byte
     with Global => null, Subprogram_Variant => (Decreases => Item.Level);
   function View_Length (Data : E.Bytes; Item : E.Byte_View) return E.Count is
      Prior : E.Byte_View;
      Size, Padding : E.Count;
   begin
      if Item.Level = 0 then return Item.Encoded.Length; end if;
      Prior := (Item.Encoded, Item.Level - 1); Size := View_Length (Data, Prior);
      if Size = 0 then return 0; end if;
      if View_Byte (Data, Prior, Size - 1) /= Character'Pos ('=') then Padding := 0;
      elsif View_Byte (Data, Prior, Size - 2) = Character'Pos ('=') then Padding := 2;
      else Padding := 1; end if;
      return (Size / 4) * 3 - Padding;
   end View_Length;
   function View_Byte (Data : E.Bytes; Item : E.Byte_View; Offset : E.Count) return Q.Byte is
      Prior : E.Byte_View;
      Quartet : E.Count;
   begin
      if Item.Level = 0 then return Data (Item.Encoded.First + Offset); end if;
      Prior := (Item.Encoded, Item.Level - 1); Quartet := (Offset / 3) * 4;
      case Offset mod 3 is
         when 0 => return B64.Digit (View_Byte (Data, Prior, Quartet)) * 4 +
            B64.Digit (View_Byte (Data, Prior, Quartet + 1)) / 16;
         when 1 => return (B64.Digit (View_Byte (Data, Prior, Quartet + 1)) mod 16) * 16 +
            B64.Digit (View_Byte (Data, Prior, Quartet + 2)) / 4;
         when others => return (B64.Digit (View_Byte (Data, Prior, Quartet + 2)) mod 4) * 64 +
            B64.Digit (View_Byte (Data, Prior, Quartet + 3));
      end case;
   end View_Byte;
   function Scalar (Data : E.Bytes; Item : E.Span; Field : String := "value") return Scalar_Bytes is
      Result : Scalar_Bytes;
      Value : constant E.View := E.Decode (Data, F (Data, Item, Field), E.Operation);
   begin
      if not E.Bytes_Valid (Data, Value.Payload) then return Result; end if;
      Result.Payload := Value.Payload;
      Result.Length := View_Length (Data, Value.Payload);
      Result.Hex := V.Type_Is (Data, Item, "bytes") or else Field = "magnitude";
      if Result.Hex then
         if Result.Length mod 2 /= 0 or else
            (for some I in E.Count range 1 .. Result.Length =>
               View_Byte (Data, Result.Payload, I - 1) not in Character'Pos ('0') .. Character'Pos ('9') |
                  Character'Pos ('a') .. Character'Pos ('f')) then return (others => <>); end if;
         Result.Length := Result.Length / 2;
      elsif not V.Valid_Text (Data, Item) then return (others => <>); end if;
      Result.Valid := True; return Result;
   end Scalar;
   function Byte_At (Data : E.Bytes; Item : Scalar_Bytes; Offset : E.Count) return Q.Byte is
     (if Item.Hex then Nibble (View_Byte (Data, Item.Payload, Offset * 2)) * 16 +
         Nibble (View_Byte (Data, Item.Payload, Offset * 2 + 1))
      else View_Byte (Data, Item.Payload, Offset));
   function Internal_Table_Name (Data : E.Bytes; Item : E.Span) return Boolean is
      Value : constant Scalar_Bytes := Scalar (Data, Item);
      Prefix : constant String := "sqlite";
   begin
      if not V.Valid_Text (Data, Item) or else not Value.Valid or else Value.Length < 7 then return False; end if;
      -- Original SQLite LIKE 'sqlite_%': ASCII case-insensitive prefix, then
      -- one wildcard character. This is not a new restriction on user tables.
      for I in Prefix'Range loop
         declare Byte : Q.Byte := Byte_At (Data, Value, E.Count (I - Prefix'First)); begin
            if Byte in Character'Pos ('A') .. Character'Pos ('Z') then Byte := Byte + 32; end if;
            if Byte /= Character'Pos (Prefix (I)) then return False; end if;
         end;
      end loop;
      return True;
   end Internal_Table_Name;
   type Native_Number is record
      Present : Boolean := False;
      Value : U64 := 0;
   end record;
   function Number (Data : E.Bytes; Item : E.Span) return Native_Number is
      Result : U64 := 0;
   begin
      if not V.Type_Is (Data, Item, "integer") or else V.Negative (Data, Item) then return (others => <>); end if;
      declare Raw : constant Scalar_Bytes := Scalar (Data, Item, "magnitude"); begin
         if not Raw.Valid then return (others => <>); end if;
         for I in reverse E.Count range 1 .. Raw.Length loop
            declare Digit : constant U64 := U64 (Byte_At (Data, Raw, I - 1)); begin
               if Result > (U64'Last - Digit) / 256 then return (others => <>); end if;
               Result := Result * 256 + Digit;
            end;
         end loop;
      end;
      return (True, Result);
   end Number;
   function Visibility (Data : E.Bytes; Column : E.Span) return Column_Visibility is
   begin
      if not V.Is_Sequence (Data, Column) or else V.Count (Data, Column) not in 6 | 7 then
         return Malformed_Column;
      end if;
      if V.Count (Data, Column) = 6 then return Visible_Column; end if;
      declare Flag : constant Native_Number := Number (Data, V.Element (Data, Column, 6)); begin
         if not Flag.Present or else Flag.Value > 3 then return Malformed_Column; end if;
         return (if Flag.Value = 0 then Visible_Column else Hidden_Column);
      end;
   end Visibility;
   function Is_Number (Data : E.Bytes; Item : E.Span; Expected : U64) return Boolean is
      Value : constant Native_Number := Number (Data, Item);
   begin return Value.Present and then Value.Value = Expected; end Is_Number;
   function Is_Minus_One (Data : E.Bytes; Item : E.Span) return Boolean is
   begin
      if not V.Type_Is (Data, Item, "integer") or else not V.Negative (Data, Item) then return False; end if;
      declare Value : constant Scalar_Bytes := Scalar (Data, Item, "magnitude"); begin
         return Value.Valid and then Value.Length > 0 and then Byte_At (Data, Value, 0) = 1 and then
            (for all I in E.Count range 1 .. Value.Length - 1 => Byte_At (Data, Value, I) = 0);
      end;
   end Is_Minus_One;
   function Space (Value : Q.Byte) return Boolean is
     (Value in 9 .. 13 or else Value = 32);
   function Decimal (Data : E.Bytes; Value : Scalar_Bytes; First, Last : E.Count;
                     Radix : U64 := 10) return Native_Number is
      Result : U64 := 0;
   begin
      if not Value.Valid or else First >= Last or else Last > Value.Length then return (others => <>); end if;
      for I in E.Count range First .. Last - 1 loop
         declare Byte : constant Q.Byte := Byte_At (Data, Value, I); Digit : U64; begin
            if Byte not in Character'Pos ('0') .. Character'Pos ('9') then return (others => <>); end if;
            Digit := U64 (Byte - Character'Pos ('0'));
            if Digit >= Radix or else Result > (U64'Last - Digit) / Radix then return (others => <>); end if;
            Result := Result * Radix + Digit;
         end;
      end loop;
      return (True, Result);
   end Decimal;
   function Proc_Word (Data : E.Bytes; Blob : E.Span; Name : String; Part : Positive;
                       Radix : U64 := 10) return Native_Number is
      Value : constant Scalar_Bytes := Scalar (Data, Blob);
      Offset : E.Count := 0;
      Start, Stop, Word : E.Count;
      Found : Boolean := False;
      Result : Native_Number;
   begin
      if not V.Type_Is (Data, Blob, "bytes") or else not Value.Valid then return Result; end if;
      while Offset < Value.Length loop
         pragma Loop_Variant (Increases => Offset);
         Start := Offset;
         while Offset < Value.Length and then Byte_At (Data, Value, Offset) /= 10 loop
            pragma Loop_Invariant (Offset >= Start and then Offset <= Value.Length);
            pragma Loop_Variant (Increases => Offset);
            Offset := Offset + 1;
         end loop;
         Stop := Offset;
         if E.Count (Name'Length) + 1 <= Stop - Start and then
            (for all I in Name'Range => Byte_At (Data, Value, Start + E.Count (I - Name'First)) = Character'Pos (Name (I))) and then
            Byte_At (Data, Value, Start + E.Count (Name'Length)) = Character'Pos (':') then
            if Found then return (others => <>); end if;
            Found := True; Start := Start + E.Count (Name'Length) + 1; Word := 0;
            while Start < Stop loop
               pragma Loop_Variant (Increases => Start);
               while Start < Stop and then Space (Byte_At (Data, Value, Start)) loop
                  pragma Loop_Invariant (Start >= Start'Loop_Entry and then Start <= Stop);
                  pragma Loop_Variant (Increases => Start);
                  Start := Start + 1;
               end loop;
               Offset := Start;
               while Start < Stop and then not Space (Byte_At (Data, Value, Start)) loop
                  pragma Loop_Invariant (Start >= Offset and then Start <= Stop);
                  pragma Loop_Variant (Increases => Start);
                  Start := Start + 1;
               end loop;
               if Start > Offset then Word := Word + 1; end if;
               if Word = E.Count (Part) and then Start > Offset then Result := Decimal (Data, Value, Offset, Start, Radix); end if;
            end loop;
         end if;
         Offset := Stop;
         if Offset < Value.Length then Offset := Offset + 1; end if;
      end loop;
      return Result;
   end Proc_Word;
   function Stat_PID (Data : E.Bytes; Blob : E.Span) return Native_Number is
      Value : constant Scalar_Bytes := Scalar (Data, Blob);
      Stop : E.Count := 0;
   begin
      if not V.Type_Is (Data, Blob, "bytes") or else not Value.Valid then return (others => <>); end if;
      while Stop < Value.Length and then not Space (Byte_At (Data, Value, Stop)) loop
         pragma Loop_Variant (Increases => Stop);
         Stop := Stop + 1;
      end loop;
      return Decimal (Data, Value, 0, Stop);
   end Stat_PID;
   function Bytes_Text (Data : E.Bytes; Bytes_Item, Text_Item : E.Span) return Boolean is
      Left : constant Scalar_Bytes := Scalar (Data, Bytes_Item);
      Right : constant Scalar_Bytes := Scalar (Data, Text_Item);
   begin
      return V.Type_Is (Data, Bytes_Item, "bytes") and then V.Valid_Text (Data, Text_Item) and then
         Left.Valid and then Right.Valid and then Left.Length = Right.Length and then
         (for all I in E.Count range 1 .. Left.Length => Byte_At (Data, Left, I - 1) = Byte_At (Data, Right, I - 1));
   end Bytes_Text;
   function Private_Identity (Data : E.Bytes; Identity : E.Span; Directory : Boolean) return Boolean is
      Mode : constant Native_Number := Number (Data, F (Data, Identity, "mode"));
   begin
      return Is_Number (Data, F (Data, Identity, "uid"), 0) and then Mode.Present and then
         Mode.Value / 4096 mod 16 = (if Directory then 4 else 8) and then
         (if Directory then (Mode.Value / 16) mod 2 = 0 and then (Mode.Value / 2) mod 2 = 0
          else Mode.Value mod 64 = 0);
   end Private_Identity;
   function Identity_Same (Data : E.Bytes; Left, Right : E.Span) return Boolean is
   begin
      for I in 1 .. 5 loop
         declare Name : constant String := (case I is when 1 => "device", when 2 => "inode",
                 when 3 => "mode", when 4 => "uid", when others => "gid"); begin
            if not V.Is_Integer (Data, F (Data, Left, Name)) or else
               not Same (Data, F (Data, Left, Name), F (Data, Right, Name)) then return False; end if;
         end;
      end loop;
      return True;
   end Identity_Same;
   -- Linux aarch64 UAPI: asm/fcntl.h and asm-generic/fcntl.h. O_LARGEFILE
   -- is the kernel's optional normalization, not a requested extra authority.
   Read_Flags : constant U64 := 16#88000#;
   Exclusive_Flags : constant U64 := 16#880C2#;
   Directory_Flags : constant U64 := 16#8C000#;
   Largefile_Flag : constant U64 := 16#20000#;
   function FD_Matches (Data : E.Bytes; Identity, Info : E.Span; Flags : U64) return Boolean is
      Inode : constant Native_Number := Proc_Word (Data, Info, "ino", 1);
      Actual : constant Native_Number := Proc_Word (Data, Info, "flags", 1, 8);
      Expected : constant Native_Number := Number (Data, F (Data, Identity, "inode"));
   begin
      return Inode.Present and then Expected.Present and then Inode.Value = Expected.Value and then
         Actual.Present and then (Actual.Value and not Largefile_Flag) = Flags and then
         Same (Data, Info, F (Data, Identity, "fdinfo"));
   end FD_Matches;
   function Receipt (Data : E.Bytes; Item, Source : E.Span; Call : String;
                     Errno : U64 := 0) return Boolean is
   begin
      return S.Text_Is (Data, F (Data, Item, "call"), Call) and then
         Same (Data, F (Data, Item, "source"), Source) and then
         Is_Number (Data, F (Data, Item, "errno"), Errno) and then
         (if Errno = 0 then (if Call = "lstat" or else Call = "fsync" then
             Is_Number (Data, F (Data, Item, "result"), 0)
          else Number (Data, F (Data, Item, "result")).Present)
          else Is_Minus_One (Data, F (Data, Item, "result")));
   end Receipt;
   function Parent_Path_Matches (Data : E.Bytes; Target, Parent : E.Span) return Boolean is
      Name : constant String := "worldline-operation-head.sqlite";
      Full : constant Scalar_Bytes := Scalar (Data, Target);
      Dir : constant Scalar_Bytes := Scalar (Data, Parent);
   begin
      return Full.Valid and then Dir.Valid and then Full.Length > E.Count (Name'Length) + 1 and then
         Dir.Length = Full.Length - E.Count (Name'Length) - 1 and then
         Byte_At (Data, Full, Dir.Length) = Character'Pos ('/') and then
         (for all I in E.Count range 1 .. Dir.Length => Byte_At (Data, Full, I - 1) = Byte_At (Data, Dir, I - 1)) and then
         (for all I in Name'Range => Byte_At (Data, Full, Dir.Length + 1 + E.Count (I - Name'First)) = Character'Pos (Name (I)));
   end Parent_Path_Matches;
   function Parent_Matches (Data : E.Bytes; Artifact : E.Span) return Boolean is
      Held : constant E.Span := F (Data, Artifact, "parent_held_identity");
      Named : constant E.Span := F (Data, Artifact, "parent_named_identity");
   begin
      return Number (Data, F (Data, Artifact, "parent_fd")).Present and then
         Parent_Path_Matches (Data, F (Data, Artifact, "path"), F (Data, Artifact, "parent_path")) and then
         Private_Identity (Data, Held, True) and then Private_Identity (Data, Named, True) and then
         Identity_Same (Data, Held, Named) and then
         FD_Matches (Data, Held, F (Data, Held, "fdinfo"), Directory_Flags);
   end Parent_Matches;
   function Artifact_Absent (Data : E.Bytes; Artifact, Source : E.Span) return Boolean is
      Named : constant E.Span := F (Data, Artifact, "named");
      Probe : constant E.Span := F (Data, Artifact, "probe");
   begin
      return Parent_Matches (Data, Artifact) and then Receipt (Data, Named, Source, "lstat", 2) and then
         Receipt (Data, Probe, Source, "open", 2) and then
         Same (Data, F (Data, F (Data, Named, "args"), "path"), F (Data, Artifact, "path")) and then
         Same (Data, F (Data, F (Data, Probe, "args"), "path"), F (Data, Artifact, "path")) and then
         Is_Number (Data, F (Data, F (Data, Probe, "args"), "flags"), Read_Flags) and then
         V.Is_Null (Data, F (Data, Artifact, "raw")) and then V.Is_Null (Data, F (Data, Artifact, "logical_database"));
   end Artifact_Absent;
   function Artifact_Present (Data : E.Bytes; Artifact, Source : E.Span) return Boolean is
      Named : constant E.Span := F (Data, Artifact, "named");
      Later : constant E.Span := F (Data, Artifact, "named_after");
      Probe : constant E.Span := F (Data, Artifact, "probe");
      Held : constant E.Span := F (Data, Artifact, "probe_held_identity");
      After_Held : constant E.Span := F (Data, Artifact, "probe_held_identity_after");
      Identity : constant E.Span := F (Data, Named, "api_result");
   begin
      return Parent_Matches (Data, Artifact) and then Receipt (Data, Named, Source, "lstat") and then
         Receipt (Data, Later, Source, "lstat") and then Receipt (Data, Probe, Source, "open") and then
         Same (Data, F (Data, Probe, "result"), F (Data, Probe, "api_result")) and then
         Same (Data, F (Data, F (Data, Probe, "args"), "path"), F (Data, Artifact, "path")) and then
         Same (Data, F (Data, F (Data, Named, "args"), "path"), F (Data, Artifact, "path")) and then
         Same (Data, F (Data, F (Data, Later, "args"), "path"), F (Data, Artifact, "path")) and then
         Is_Number (Data, F (Data, F (Data, Probe, "args"), "flags"), Read_Flags) and then
         Private_Identity (Data, Identity, False) and then Is_Number (Data, F (Data, Identity, "links"), 1) and then
         Identity_Same (Data, Held, Identity) and then Identity_Same (Data, Held, After_Held) and then
         Identity_Same (Data, Held, F (Data, Later, "api_result")) and then
         Same (Data, F (Data, Identity, "size"), F (Data, After_Held, "size")) and then
         FD_Matches (Data, Held, F (Data, Artifact, "probe_fdinfo"), Read_Flags) and then
         Same (Data, F (Data, Artifact, "probe_link"), F (Data, Artifact, "path")) and then
         V.Valid_Bytes (Data, F (Data, Artifact, "raw")) and then
         Same (Data, F (Data, Artifact, "raw"), F (Data, Artifact, "raw_after")) and then
         V.Is_Null (Data, F (Data, Artifact, "read_error")) and then V.Is_Null (Data, F (Data, Artifact, "database_error"));
   end Artifact_Present;
   function Bootstrap_Frame_Corresponds
     (Data : E.Bytes; Frame : E.Span; Caller_PID, Caller_EUID : Interfaces.Unsigned_32) return Boolean is
      Roster : constant E.Span := F (Data, Frame, "owner_roster");
      Boot : constant E.Span := F (Data, Frame, "bootstrap");
      Current : constant E.Span := F (Data, Roster, "current");
      Installation : constant E.Span := F (Data, Current, "installation");
      Source : constant E.Span := F (Data, Current, "source");
      Entry_Value : constant E.Span := F (Data, Boot, "entry");
      Arguments : constant E.Span := F (Data, Boot, "arguments");
      Actor : constant E.Span := F (Data, Boot, "actor");
      Pid : constant Native_Number := Proc_Word (Data, F (Data, Actor, "status"), "Pid", 1);
      Euid : constant Native_Number := Proc_Word (Data, F (Data, Actor, "status"), "Uid", 2);
      Stat : constant Native_Number := Stat_PID (Data, F (Data, Actor, "stat"));
      Facts : constant E.Bytes := O.Extract_Replay_Capsules (Data, Roster);
      Owner_Context : O.Prepared_History;
      Resource_Context : K.Prepared_History;
      Compiled : Boolean := False;
   begin
      if not S.Valid (Data, Frame) or else not S.Text_Is (Data, F (Data, Frame, "schema"), "worldline.operation-head-bootstrap-v1") or else
         Caller_PID = 0 or else Caller_EUID /= 0 or else not Pid.Present or else not Euid.Present or else not Stat.Present or else
         Pid.Value /= U64 (Caller_PID) or else Stat.Value /= U64 (Caller_PID) or else Euid.Value /= U64 (Caller_EUID) or else
         not Worldline.Startup_Admission.Operation_Source_Corresponds
            (Data, Roster, F (Data, Boot, "source_profile"), F (Data, Boot, "path")) or else
         not Bytes_Text (Data, F (Data, F (Data, Boot, "artifact"), "path"), F (Data, Boot, "path")) or else
         not Install.Joined_Path (Data, Entry_Value, F (Data, F (Data, Installation, "runtime"), "worldline_source"),
            "/protected-canonical/provision_operation_head.py") or else
         not V.Is_Sequence (Data, Arguments) or else V.Count (Data, Arguments) = 0 or else
         not Install.Path_Equivalent (Data, V.Element (Data, Arguments, 0), Entry_Value) or else
         not Bytes_Text (Data, F (Data, Actor, "exe"), F (Data, Source, "interpreter")) or else
         not Worldline.Startup_Source_Custody.Unselected_Path (Data, Source, F (Data, Boot, "path")) then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, F (Data, Source, "events")) loop
         declare Event : constant E.Span := V.Element (Data, F (Data, Source, "events"), I - 1); begin
            if S.Text_Is (Data, F (Data, Event, "kind"), "ENTRY_COMPILED_BEFORE_EXEC") and then
               Install.Path_Equivalent (Data, F (Data, Event, "path"), Entry_Value) then Compiled := True; end if;
         end;
      end loop;
      if not Compiled then return False; end if;
      O.Establish_History (Owner_Context, Data, Facts, Roster); K.Establish_History (Resource_Context, Data, Roster);
      return Raw_Current_Authenticated (Data, Roster, Owner_Context, Resource_Context, Require_Head => False);
   end Bootstrap_Frame_Corresponds;
   function Bootstrap_Path (Data : E.Bytes; Paths, Target : E.Span) return E.Span is
      Found : E.Span := (1, 0);
   begin
      for I in E.Count range 1 .. V.Count (Data, Paths) loop
         declare Entry_Value : constant E.Span := V.Element (Data, Paths, I - 1); begin
            if Install.Path_Equivalent (Data, F (Data, Entry_Value, "path"), Target) then
               if Found.Length > 0 then return (1, 0); end if; Found := Entry_Value;
            end if;
         end;
      end loop;
      return Found;
   end Bootstrap_Path;
   function Slot_Metadata_Matches (Data : E.Bytes; Frame : E.Span; Present : Boolean) return Boolean is
      Roster : constant E.Span := F (Data, Frame, "owner_roster");
      Boot : constant E.Span := F (Data, Frame, "bootstrap");
      Artifact : constant E.Span := F (Data, Boot, "artifact");
      Entry_Value : constant E.Span := Bootstrap_Path (Data, F (Data, F (Data, Roster, "current"), "paths"), F (Data, Boot, "path"));
      Named : constant E.Span := F (Data, F (Data, Artifact, "named"), "api_result");
   begin
      if Entry_Value.Length = 0 or else not Same (Data, F (Data, Entry_Value, "raw"), F (Data, Artifact, "raw")) or else
         not Same (Data, F (Data, Entry_Value, "logical_database"), F (Data, Artifact, "logical_database")) then return False; end if;
      if not Present then return V.Is_Null (Data, F (Data, Entry_Value, "identity")); end if;
      for I in 1 .. 4 loop
         declare Name : constant String := (case I is when 1 => "device", when 2 => "inode", when 3 => "uid", when others => "gid"); begin
            if not Same (Data, F (Data, F (Data, Entry_Value, "identity"), Name), F (Data, Named, Name)) then return False; end if;
         end;
      end loop;
      declare Left : constant Native_Number := Number (Data, F (Data, F (Data, Entry_Value, "identity"), "mode"));
              Right : constant Native_Number := Number (Data, F (Data, Named, "mode")); begin
         return Left.Present and then Right.Present and then Left.Value mod 4096 = Right.Value mod 4096;
      end;
   end Slot_Metadata_Matches;
   function Database_Mode (Data : E.Bytes; Database : E.Span; WAL : Boolean) return Boolean is
      Integrity : constant E.Span := F (Data, Database, "integrity");
      Mode : constant E.Span := F (Data, Database, "journal_mode");
   begin
      return V.Is_Sequence (Data, Integrity) and then V.Count (Data, Integrity) = 1 and then
         V.Count (Data, V.Element (Data, Integrity, 0)) = 1 and then
         S.Text_Is (Data, V.Element (Data, V.Element (Data, Integrity, 0), 0), "ok") and then
         (not WAL or else (V.Count (Data, Mode) = 1 and then V.Count (Data, V.Element (Data, Mode, 0)) = 1 and then
            S.Text_Is (Data, V.Element (Data, V.Element (Data, Mode, 0), 0), "wal")));
   end Database_Mode;
   function SQL_Files_Match (Data : E.Bytes; Artifact, Creation : E.Span) return Boolean is
      Files : constant E.Span := F (Data, Artifact, "database_files");
      List : constant E.Span := F (Data, Artifact, "database_list");
      Before : constant E.Span := F (Data, Artifact, "fd_before_sql");
      Target : constant E.Span := F (Data, Artifact, "path");
      Probe : constant E.Span := F (Data, Artifact, "probe_held_identity");
      Database_Found : Boolean := False;
   begin
      if not V.Is_Sequence (Data, Files) or else not V.Is_Sequence (Data, List) or else
         not V.Is_Sequence (Data, Before) then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, List) loop
         declare Row : constant E.Span := V.Element (Data, List, I - 1); begin
            if V.Count (Data, Row) = 3 and then S.Text_Is (Data, V.Element (Data, Row, 1), "main") and then
               Bytes_Text (Data, Target, V.Element (Data, Row, 2)) then Database_Found := True; end if;
         end;
      end loop;
      if not Database_Found then return False; end if;
      Database_Found := False;
      for I in E.Count range 1 .. V.Count (Data, Files) loop
         declare Item : constant E.Span := V.Element (Data, Files, I - 1);
                 FD : constant E.Span := F (Data, Item, "fd");
                 Identity : constant E.Span := F (Data, Item, "identity"); begin
            if not Number (Data, FD).Present or else not Private_Identity (Data, Identity, False) or else
               not Identity_Same (Data, Identity, F (Data, Item, "named")) or else
               not Same (Data, F (Data, Item, "fdinfo"), F (Data, Identity, "fdinfo")) then return False; end if;
            -- The factual live SQL path and full descriptor roster designate
            -- the same inode as the nofollow probe. Role labels and an FD's
            -- earlier number cannot authorize or identify a SQLite handle:
            -- descriptor-number reuse is an ordinary kernel outcome.
            if not Same (Data, FD, F (Data, F (Data, Artifact, "probe"), "result")) and then
               (V.Is_Null (Data, Creation) or else not Same (Data, FD, F (Data, Creation, "fd"))) and then
               Same (Data, F (Data, Item, "link"), Target) and then Identity_Same (Data, Identity, Probe) then
               declare Flags : constant Native_Number := Proc_Word (Data, F (Data, Item, "fdinfo"), "flags", 1, 8);
                       Inode : constant Native_Number := Proc_Word (Data, F (Data, Item, "fdinfo"), "ino", 1);
                       Expected : constant Native_Number := Number (Data, F (Data, Probe, "inode")); begin
                  if Flags.Present and then Flags.Value mod 4 in 0 | 2 and then Inode.Present and then
                     Expected.Present and then Inode.Value = Expected.Value then Database_Found := True; end if;
               end;
            end if;
         end;
      end loop;
      return Database_Found;
   end SQL_Files_Match;
   function Empty_Created_File (Data : E.Bytes; Artifact : E.Span) return Boolean is
      Raw : constant Scalar_Bytes := Scalar (Data, F (Data, Artifact, "raw"));
      DB : constant E.Span := F (Data, Artifact, "logical_database");
   begin
      return Raw.Valid and then Raw.Length = 0 and then Database_Mode (Data, DB, False) and then
         V.Is_Sequence (Data, F (Data, DB, "tables")) and then V.Count (Data, F (Data, DB, "tables")) = 0 and then
         V.Is_Sequence (Data, F (Data, DB, "schema")) and then V.Count (Data, F (Data, DB, "schema")) = 0;
   end Empty_Created_File;
   function Empty_Created_Schema (Data : E.Bytes; DB : E.Span) return Boolean is
      Tables : constant E.Span := F (Data, DB, "tables");
      Head_Found, Admission_Found : Boolean := False;
   begin
      if not Database_Mode (Data, DB, True) or else not V.Is_Sequence (Data, Tables) then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Tables) loop
         declare Table : constant E.Span := V.Element (Data, Tables, I - 1);
                 Cols : constant E.Span := F (Data, Table, "columns");
                 Head : constant Boolean := S.Text_Is (Data, F (Data, Table, "name"), "canonical_operation_head");
                 Admission : constant Boolean := S.Text_Is (Data, F (Data, Table, "name"), "canonical_operation_admission");
                 Names : constant String := (if Head then "name,installation,genesis,head,state,prior_envelope,next_envelope"
                    else "name,installation,genesis,owner_envelope,initial_envelope,state");
                 Offset : Positive := Names'First; Ordinal : E.Count := 0; begin
            if not Head and then not Admission then return False; end if;
            if (Head and then Head_Found) or else (Admission and then Admission_Found) or else
               V.Count (Data, Cols) /= (if Head then 7 else 6) or else
               not V.Is_Sequence (Data, F (Data, Table, "rows")) or else V.Count (Data, F (Data, Table, "rows")) /= 0 then return False; end if;
            for K in Names'Range loop
               if Names (K) = ',' then
                  if not S.Text_Is (Data, V.Element (Data, V.Element (Data, Cols, Ordinal), 1), Names (Offset .. K - 1)) then return False; end if;
                  Offset := K + 1; Ordinal := Ordinal + 1;
               end if;
            end loop;
            if not S.Text_Is (Data, V.Element (Data, V.Element (Data, Cols, Ordinal), 1), Names (Offset .. Names'Last)) then return False; end if;
            if Head then Head_Found := True; else Admission_Found := True; end if;
         end;
      end loop;
      return Head_Found and then Admission_Found;
   end Empty_Created_Schema;
   function Bootstrap_Head_Matches (Data : E.Bytes; Frame : E.Span; Fresh : Boolean) return Boolean is
      Roster : constant E.Span := F (Data, Frame, "owner_roster");
      Current : constant E.Span := F (Data, Roster, "current");
      Ctx : constant E.Span := F (Data, Roster, "operation_context");
      Policy : constant E.Span := F (Data, Ctx, "policy");
      Paths : constant E.Span := F (Data, Current, "paths");
      DB : constant E.Span := F (Data, F (Data, F (Data, Frame, "bootstrap"), "artifact"), "logical_database");
      Journal_Item : constant E.Span := F (Data, Path_Entry (Data, Paths, F (Data, Policy, "journal")), "raw");
      Owner_Item : constant E.Span := F (Data, Path_Entry (Data, Paths, F (Data, Policy, "genesis_file")), "raw");
   begin
      if not Database_Mode (Data, DB, True) or else not V.Valid_Bytes (Data, Journal_Item) or else
         not V.Valid_Bytes (Data, Owner_Item) or else not V.Valid_Bytes (Data, Issuer_Key (Data, Roster)) then return False; end if;
      declare Key : constant E.Bytes := V.Bytes_Value (Data, Issuer_Key (Data, Roster));
              Journal : constant E.Bytes := V.Bytes_Value (Data, Journal_Item);
              Owner : constant E.Bytes := V.Bytes_Value (Data, Owner_Item); begin
         if not Head_Corresponds (Data, Key, Journal, Owner, DB, F (Data, F (Data, Current, "installation"), "installation_id"), Policy, Ctx) then return False; end if;
      end;
      if Fresh then
         declare Head : constant E.Span := Table_Row (Data, DB, "canonical_operation_head",
            "name,installation,genesis,head,state,prior_envelope,next_envelope", 7); begin
            return S.Text_Is (Data, Row_Value (Data, Head, 5, 7), "STABLE") and then
               V.Is_Null (Data, Row_Value (Data, Head, 6, 7)) and then V.Is_Null (Data, Row_Value (Data, Head, 7, 7));
         end;
      end if;
      return True;
   end Bootstrap_Head_Matches;
   function Other_Sources_Unchanged (Data, Before_Data : E.Bytes; Frame, Before_Frame : E.Span) return Boolean is
      Current : constant E.Span := F (Data, F (Data, Frame, "owner_roster"), "current");
      Old : constant E.Span := F (Before_Data, F (Before_Data, Before_Frame, "owner_roster"), "current");
      Paths : constant E.Span := F (Data, Current, "paths");
      Old_Paths : constant E.Span := F (Before_Data, Old, "paths");
      Target : constant E.Span := F (Data, F (Data, Frame, "bootstrap"), "path");
   begin
      if not Raw_Same (Data, Before_Data, F (Data, Current, "installation"), F (Before_Data, Old, "installation")) or else
         not Raw_Same (Data, Before_Data, F (Data, Current, "descriptor_raw"), F (Before_Data, Old, "descriptor_raw")) or else
         not Raw_Same (Data, Before_Data, F (Data, F (Data, Current, "source"), "envelope_bytes_hex"),
            F (Before_Data, F (Before_Data, Old, "source"), "envelope_bytes_hex")) or else
         not Raw_Same (Data, Before_Data, F (Data, Current, "held_locks"), F (Before_Data, Old, "held_locks")) or else
         not V.Is_Sequence (Data, Paths) or else V.Count (Data, Paths) /= V.Count (Before_Data, Old_Paths) then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Paths) loop
         declare New_Entry : constant E.Span := V.Element (Data, Paths, I - 1);
                 Old_Entry : constant E.Span := V.Element (Before_Data, Old_Paths, I - 1);
                 New_DB : constant E.Span := F (Data, New_Entry, "logical_database");
                 Old_DB : constant E.Span := F (Before_Data, Old_Entry, "logical_database"); begin
            if not Raw_Same (Data, Before_Data, F (Data, New_Entry, "path"), F (Before_Data, Old_Entry, "path")) then return False; end if;
            if not Install.Path_Equivalent (Data, F (Data, New_Entry, "path"), Target) then
               if not Raw_Same (Data, Before_Data, F (Data, New_Entry, "identity"), F (Before_Data, Old_Entry, "identity")) then return False; end if;
               if New_DB.Length > 0 and then not V.Is_Null (Data, New_DB) then
                  if not Raw_Same (Data, Before_Data, New_DB, Old_DB) then return False; end if;
               elsif not Raw_Same (Data, Before_Data, F (Data, New_Entry, "raw"), F (Before_Data, Old_Entry, "raw")) then return False; end if;
            end if;
         end;
      end loop;
      return True;
   end Other_Sources_Unchanged;
   function Creation_Matches (Data, Before_Data : E.Bytes; Frame, Before_Frame : E.Span) return Boolean is
      Boot : constant E.Span := F (Data, Frame, "bootstrap");
      Before_Boot : constant E.Span := F (Before_Data, Before_Frame, "bootstrap");
      Creation : constant E.Span := F (Data, Boot, "creation");
      Open : constant E.Span := F (Data, Creation, "open");
      Artifact : constant E.Span := F (Data, Boot, "artifact");
      Old_Artifact : constant E.Span := F (Before_Data, Before_Boot, "artifact");
      Held : constant E.Span := F (Data, Creation, "held_identity");
      Source : constant E.Span := F (Data, F (Data, F (Data, Frame, "owner_roster"), "current"), "source");
   begin
      return Other_Sources_Unchanged (Data, Before_Data, Frame, Before_Frame) and then
         V.Is_Null (Before_Data, F (Before_Data, Before_Boot, "creation")) and then
         V.Is_Null (Before_Data, F (Before_Data, Before_Boot, "sync")) and then
         Receipt (Data, Open, Source, "open") and then
         Same (Data, F (Data, F (Data, Open, "args"), "path"), F (Data, Artifact, "path")) and then
         Is_Number (Data, F (Data, F (Data, Open, "args"), "flags"), Exclusive_Flags) and then
         Is_Number (Data, F (Data, F (Data, Open, "args"), "mode"), 384) and then
         Same (Data, F (Data, Open, "result"), F (Data, Creation, "fd")) and then
         Same (Data, F (Data, Open, "api_result"), F (Data, Creation, "fd")) and then
         Private_Identity (Data, Held, False) and then
         Identity_Same (Data, Held, F (Data, F (Data, Artifact, "named"), "api_result")) and then
         FD_Matches (Data, Held, F (Data, Creation, "fdinfo"), Read_Flags + 2) and then
         Same (Data, F (Data, Creation, "link"), F (Data, Artifact, "path")) and then
         Raw_Same (Data, Before_Data, F (Data, Artifact, "path"), F (Before_Data, Old_Artifact, "path")) and then
         Raw_Same (Data, Before_Data, F (Data, Artifact, "parent_fd"), F (Before_Data, Old_Artifact, "parent_fd")) and then
         (for all I in 1 .. 5 => Raw_Same (Data, Before_Data,
            F (Data, F (Data, Artifact, "parent_held_identity"),
               (case I is when 1 => "device", when 2 => "inode", when 3 => "mode", when 4 => "uid", when others => "gid")),
            F (Before_Data, F (Before_Data, Old_Artifact, "parent_held_identity"),
               (case I is when 1 => "device", when 2 => "inode", when 3 => "mode", when 4 => "uid", when others => "gid")))) and then
         Raw_Same (Data, Before_Data, F (Data, Boot, "entry"), F (Before_Data, Before_Boot, "entry")) and then
         Raw_Same (Data, Before_Data, F (Data, Boot, "arguments"), F (Before_Data, Before_Boot, "arguments")) and then
         Install.Stable (Before_Data, Data, F (Before_Data, Before_Boot, "source_profile"), F (Data, Boot, "source_profile"));
   end Creation_Matches;
   function Sync_Matches (Data : E.Bytes; Frame : E.Span) return Boolean is
      Boot : constant E.Span := F (Data, Frame, "bootstrap");
      Sync : constant E.Span := F (Data, Boot, "sync");
      Artifact : constant E.Span := F (Data, Boot, "artifact");
      Creation : constant E.Span := F (Data, Boot, "creation");
      Source : constant E.Span := F (Data, F (Data, F (Data, Frame, "owner_roster"), "current"), "source");
      File : constant E.Span := F (Data, Sync, "file");
      Parent : constant E.Span := F (Data, Sync, "parent");
      Held : constant E.Span := F (Data, Creation, "held_identity");
   begin
      return Receipt (Data, File, Source, "fsync") and then Receipt (Data, Parent, Source, "fsync") and then
         Is_Number (Data, F (Data, File, "result"), 0) and then Is_Number (Data, F (Data, Parent, "result"), 0) and then
         V.Is_Null (Data, F (Data, File, "api_result")) and then V.Is_Null (Data, F (Data, Parent, "api_result")) and then
         Same (Data, F (Data, F (Data, File, "args"), "fd"), F (Data, Creation, "fd")) and then
         Same (Data, F (Data, F (Data, Parent, "args"), "fd"), F (Data, Artifact, "parent_fd")) and then
         Identity_Same (Data, Held, F (Data, Sync, "file_before")) and then
         Identity_Same (Data, Held, F (Data, Sync, "file_after")) and then
         Identity_Same (Data, Held, F (Data, Sync, "file_named_after")) and then
         Identity_Same (Data, F (Data, Artifact, "parent_held_identity"), F (Data, Sync, "parent_after")) and then
         FD_Matches (Data, F (Data, Sync, "file_after"), F (Data, F (Data, Sync, "file_after"), "fdinfo"), Read_Flags + 2) and then
         Same (Data, F (Data, F (Data, Sync, "file_after"), "size"), F (Data, F (Data, Artifact, "probe_held_identity"), "size")) and then
         Same (Data, F (Data, F (Data, Sync, "file_named_after"), "size"), F (Data, F (Data, F (Data, Artifact, "named"), "api_result"), "size")) and then
         Same (Data, F (Data, F (Data, Sync, "file_before"), "size"), F (Data, F (Data, Sync, "file_after"), "size"));
   end Sync_Matches;
   function Bootstrap_Decide
     (Data : aliased E.Bytes; Envelope : E.Span;
      Caller_PID, Caller_EUID : Interfaces.Unsigned_32) return Bootstrap_Decision is
      Roster : constant E.Span := F (Data, Envelope, "owner_roster");
      Boot : constant E.Span := F (Data, Envelope, "bootstrap");
      Artifact : constant E.Span := F (Data, Boot, "artifact");
      Creation : constant E.Span := F (Data, Boot, "creation");
      Source : constant E.Span := F (Data, F (Data, Roster, "current"), "source");
   begin
      if not Bootstrap_Frame_Corresponds (Data, Envelope, Caller_PID, Caller_EUID) then return (others => <>); end if;
      if Artifact_Absent (Data, Artifact, Source) then
         if V.Is_Null (Data, Creation) and then V.Is_Null (Data, F (Data, Boot, "sync")) and then
            Slot_Metadata_Matches (Data, Envelope, False) then return (Create_Fresh, 0); end if;
         return (others => <>);
      end if;
      if not Artifact_Present (Data, Artifact, Source) or else not Slot_Metadata_Matches (Data, Envelope, True) or else
         not SQL_Files_Match (Data, Artifact, Creation) then return (others => <>); end if;
      if V.Is_Null (Data, Creation) then
         if V.Is_Null (Data, F (Data, Boot, "sync")) and then Bootstrap_Head_Matches (Data, Envelope, False) then
            return (Reuse_Authentic, 4);
         end if;
         return (others => <>);
      end if;
      if not V.Valid_Bytes (Data, F (Data, Creation, "before")) then return (others => <>); end if;
      declare
         Before_Data : aliased constant E.Bytes := V.Bytes_Value (Data, F (Data, Creation, "before"));
         Before_Frame : constant E.Span := (Before_Data'First, Before_Data'Length);
         Before_Boot : constant E.Span := F (Before_Data, Before_Frame, "bootstrap");
         Before_Artifact : constant E.Span := F (Before_Data, Before_Boot, "artifact");
         Before_Source : constant E.Span := F (Before_Data, F (Before_Data, F (Before_Data, Before_Frame, "owner_roster"), "current"), "source");
      begin
         -- The saved image is producer-constructible bytes, never a permission
         -- token: authenticate the complete original before frame independently.
         -- Both frames borrow their own immutable arenas/native capsules once.
         if not Bootstrap_Frame_Corresponds (Before_Data, Before_Frame, Caller_PID, Caller_EUID) or else
            not Artifact_Absent (Before_Data, Before_Artifact, Before_Source) or else
            not Slot_Metadata_Matches (Before_Data, Before_Frame, False) or else
            not Creation_Matches (Data, Before_Data, Envelope, Before_Frame) then return (others => <>); end if;
      end;
      if Empty_Created_File (Data, Artifact) then
         if V.Is_Null (Data, F (Data, Boot, "sync")) then return (Create_Fresh, 1); end if;
      elsif Empty_Created_Schema (Data, F (Data, Artifact, "logical_database")) then
         if V.Is_Null (Data, F (Data, Boot, "sync")) then return (Create_Fresh, 2); end if;
      elsif Bootstrap_Head_Matches (Data, Envelope, True) then
         if V.Is_Null (Data, F (Data, Boot, "sync")) then return (Create_Fresh, 3);
         elsif Sync_Matches (Data, Envelope) then return (Reuse_Authentic, 4); end if;
      end if;
      return (others => <>);
   end Bootstrap_Decide;
end Worldline.Custody_V2_Operation_Journal;
