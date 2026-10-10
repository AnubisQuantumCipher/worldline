with Ada.Strings.Fixed;
with SPARK.Big_Integers;
with Interfaces;
with Attest.SHA256;
with Worldline.Recovery_Archive;
with Worldline.Operation_Archive;
with Worldline.Producer_Values;
with Worldline.Evaluation_Policy;
with Worldline.Evaluation_Producer;
with Worldline.Recovery_Syntax;
with Worldline.Source_Syntax_Provider;
with Worldline.Policy_Source;
with Decimal_Binary64;
with Worldline.Raw_JSON;
with Worldline.Archive_Base64;
with Worldline.Evaluation_Report_Facts;
with Worldline.Archive_Text;
with Worldline.Retained_Evidence_Replay;
with Worldline.Evaluation_Authority;
with Worldline.Evaluation_Wire;
with Worldline.Collapse_Wire;
with Evaluation_Completion;
with Evaluation_Raw_Roster;
with Evaluation_Finalization;
with Evaluation_Pending_V2;
package body Worldline.Recovery_Material_Replay with SPARK_Mode is
   package RA renames Worldline.Recovery_Archive;
   package OA renames Worldline.Operation_Archive;
   package V renames Worldline.Producer_Values;
   package P renames Worldline.Evaluation_Policy;
   package EP renames Worldline.Evaluation_Producer;
   package W renames Worldline.Evaluation_Wire;
   package T renames Evaluation_Completion;
   package R renames Evaluation_Raw_Roster;
   package FZ renames Evaluation_Finalization;
   package A renames Worldline.Evaluation_Authority;
   package SHA renames Attest.SHA256;
   use type E.Count; use type E.Span; use type E.Value_Kind;
   use type E.Bytes; use type Worldline.Hash;
   use type E.Layer; use type V.Value_Kind; use type W.Byte;
   use type W.Raw_Record; use type W.E.Execution_State; use type W.E.Outcome;
   use type T.E.Execution_State; use type T.E.Outcome;
   use type T.Decision; use type H.Decision; use type H.Source_Kind;
   use type H.Lifecycle; use type H.Verdict; use type FZ.Seal_Decision;
   use type FZ.Write_Decision; use type R.Declaration;
   use type Interfaces.Unsigned_64;
   Empty : constant E.Span := (1, 0);
   function Field (Data : E.Bytes; Item : E.Span; Name : String;
                   L : E.Layer := E.Recovery) return E.Span;
   function Child (Data : E.Bytes; Item : E.Span; I : E.Count;
                   L : E.Layer := E.Recovery) return E.Span is
     (E.Array_Element (Data, E.Decode (Data, Item, L).Children, I));
   function Count (Data : E.Bytes; Item : E.Span;
                   L : E.Layer := E.Recovery) return E.Count is
     (E.Array_Length (Data, E.Decode (Data, Item, L).Children));
   function Is_Null (Data : E.Bytes; Item : E.Span;
                     L : E.Layer := E.Recovery) return Boolean is
     (E.Decode (Data, Item, L).Form = E.Null_Value);
   function Raw_String (Data : E.Bytes) return String is
      Result : String (1 .. Natural (Data'Length));
   begin
      for I in Result'Range loop
         Result (I) := Character'Val (Data (Data'First + E.Count (I - 1)));
      end loop;
      return Result;
   end Raw_String;
   function Bytes (Text : String) return E.Bytes is
      Result : E.Bytes (1 .. E.Count (Text'Length));
   begin
      for I in Text'Range loop
         Result (1 + E.Count (I - Text'First)) := Character'Pos (Text (I));
      end loop;
      return Result;
   end Bytes;
   function Scalar (Data : E.Bytes; Item : E.Span;
                    L : E.Layer := E.Recovery) return String is
      N : constant E.View := E.Decode (Data, Item, L);
   begin
      if N.Form not in E.Text_Value | E.Bytes_Value | E.World_State_Value
        or else not E.Bytes_Valid (Data, N.Payload) then return ""; end if;
      return Raw_String (E.Materialize (Data, N.Payload));
   end Scalar;
   function Field (Data : E.Bytes; Item : E.Span; Name : String;
                   L : E.Layer := E.Recovery) return E.Span is
      N : constant E.View := E.Decode (Data, Item, L);
   begin
      if L = E.Recovery then return RA.Field (Data, Item, Name);
      elsif L = E.Operation then return OA.Field (Data, Item, Name);
      elsif L = E.Finalization_Record then return RA.Finalization_Record_Field (Data, Item, Name); end if;
      if N.Form /= E.Object_Value then return Empty; end if;
      for I in E.Count range 0 .. E.Array_Length (Data, N.Children) - 1 loop
         declare
            Pair : constant E.Span := E.Array_Element (Data, N.Children, I);
            K : constant E.Span := (if L = E.Terminal then E.Array_Element (Data, Pair, 0)
              else Child (Data, Pair, 0, E.Terminal));
            Val : constant E.Span := (if L = E.Terminal then E.Array_Element (Data, Pair, 1)
              else Child (Data, Pair, 1, E.Terminal));
         begin
            if L = E.Terminal then
               if K.Length >= 2 and then E.Bytes_Valid (Data, ((K.First + 1, K.Length - 2), 1))
                 and then Raw_String (E.Materialize (Data, ((K.First + 1, K.Length - 2), 1))) = Name
               then return Val; end if;
            elsif Scalar (Data, K, E.Terminal) = Name then return Val; end if;
         end;
      end loop;
      return Empty;
   end Field;
   function Base64 (Raw : E.Bytes) return String is
      Alphabet : constant String := "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
      Result : String (1 .. Natural (((Raw'Length + 2) / 3) * 4)) := (others => '=');
      I : E.Count := 0;
      O : Natural := 1;
      A, B, C : Natural;
   begin
      while I < Raw'Length loop
         A := Natural (Raw (Raw'First + I));
         B := (if I + 1 < Raw'Length then Natural (Raw (Raw'First + I + 1)) else 0);
         C := (if I + 2 < Raw'Length then Natural (Raw (Raw'First + I + 2)) else 0);
         Result (O) := Alphabet (1 + A / 4);
         Result (O + 1) := Alphabet (1 + (A mod 4) * 16 + B / 16);
         if I + 1 < Raw'Length then Result (O + 2) := Alphabet (1 + (B mod 16) * 4 + C / 64); end if;
         if I + 2 < Raw'Length then Result (O + 3) := Alphabet (1 + C mod 64); end if;
         I := I + 3; O := O + 4;
      end loop;
      return Result;
   end Base64;
   function Text_Is (Data : E.Bytes; Item : E.Span; Text : String;
                     L : E.Layer := E.Recovery) return Boolean is
     (E.Text_Is (Data, E.Decode (Data, Item, L), Text));
   function Same (Data : E.Bytes; Left, Right : E.Span;
                  L : E.Layer := E.Recovery) return Boolean is
     (if L = E.Recovery then RA.Same_Encoding (Data, Left, Right)
      else OA.Same_Encoding (Data, Left, Right));
   -- The only JSON parser is Producer_Values. This is a typed archive renderer,
   -- not a second parser; its leaf spelling uses the shared binary64 renderer.
   function Decimal (Data : E.Bytes; N : E.View) return String is
      use SPARK.Big_Integers;
      Value : Valid_Big_Integer := To_Big_Integer (0);
      Raw : constant E.Bytes := E.Materialize (Data, N.Payload);
   begin
      for I in reverse Raw'Range loop
         Value := Value * To_Big_Integer (256) + To_Big_Integer (Integer (Raw (I)));
      end loop;
      if N.Sign then Value := -Value; end if;
      return Ada.Strings.Fixed.Trim (To_String (Value), Ada.Strings.Both);
   end Decimal;
   function JSON (Data : E.Bytes; Item : E.Span;
                  At_Layer : E.Layer := E.Recovery; Ensure_ASCII : Boolean := False;
                  Preserve_Bytes : Boolean := False) return String is
      N : constant E.View := E.Decode (Data, Item, At_Layer);
      Length : constant E.Count := E.Array_Length (Data, N.Children);
      type Order_Array is array (E.Count range <>) of E.Count;
      Order : Order_Array (0 .. Length - 1);
      function Quote (Text : String) return String is
        (if Ensure_ASCII then Worldline.Raw_JSON.Canonical_ASCII_Quote (Text) else V.Quote (Text));
      function Key (I : E.Count) return String is
         Pair : constant E.Span := E.Array_Element (Data, N.Children, I);
      begin
         if At_Layer = E.Terminal then
            declare
               Enc : constant E.Span := E.Array_Element (Data, Pair, 0);
            begin
               if Enc.Length < 2 then return ""; end if;
               return Raw_String (E.Materialize (Data, ((Enc.First + 1, Enc.Length - 2), 1)));
            end;
         end if;
         return Scalar (Data, Child (Data, Pair, 0,
           (if At_Layer = E.Finalization then E.Terminal else E.Finalization)),
           (if At_Layer = E.Finalization then E.Terminal
            elsif At_Layer = E.Finalization_Record or else N.Form = E.Record_Value
            then E.Finalization else At_Layer));
      end Key;
      function Value (I : E.Count) return E.Span is
         Pair : constant E.Span := E.Array_Element (Data, N.Children, I);
      begin
         if At_Layer = E.Terminal then return E.Array_Element (Data, Pair, 1); end if;
         return Child (Data, Pair, 1,
           (if At_Layer = E.Finalization then E.Terminal else E.Finalization));
      end Value;
      function Sequence (I : E.Count) return String is
      begin
         if I = Length then return ""; end if;
         return (if I = 0 then "" else ",") &
           (if N.Form in E.Object_Value | E.Record_Value then Quote (Key (Order (I))) & ":" &
                JSON (Data, Value (Order (I)), At_Layer, Ensure_ASCII, Preserve_Bytes)
            else JSON (Data, E.Array_Element (Data, N.Children, I), At_Layer, Ensure_ASCII, Preserve_Bytes)) &
           Sequence (I + 1);
      end Sequence;
   begin
      case N.Form is
         when E.Null_Value => return "null";
         when E.Boolean_Value => return (if N.Boolean_Bit then "true" else "false");
         when E.Text_Value | E.World_State_Value => return Quote (Scalar (Data, Item, At_Layer));
         when E.Integer_Value => return Decimal (Data, N);
         when E.Float_Value =>
            declare
               Raw : constant E.Bytes := E.Materialize (Data, N.Payload);
               Bits : Interfaces.Unsigned_64 := 0;
            begin
               for I in Raw'Range loop Bits := Bits * 256 + Interfaces.Unsigned_64 (Raw (I)); end loop;
               if not Decimal_Binary64.Finite (Bits) then
                  if not Preserve_Bytes then return ""; end if;
                  return (if Decimal_Binary64.Magnitude (Bits) > Decimal_Binary64.Infinity then "NaN"
                    elsif Bits >= Decimal_Binary64.Sign_Bit then "-Infinity" else "Infinity");
               end if;
               return Decimal_Binary64.Repr (Bits);
            end;
         when E.Bytes_Value =>
            if not Preserve_Bytes then return ""; end if;
            return "{""encoding"":""base64"",""payload"":" &
              Quote (Base64 (E.Materialize (Data, N.Payload))) & "}";
         when E.List_Value | E.Tuple_Value | E.Object_Value | E.Record_Value =>
            if N.Form = E.Record_Value and then not Preserve_Bytes then return ""; end if;
            for I in Order'Range loop Order (I) := I; end loop;
            if N.Form in E.Object_Value | E.Record_Value then
               for I in Order'Range loop
                  for J in Order'Range loop
                     if J > I and then Key (Order (J)) < Key (Order (I)) then
                        declare Temp : constant E.Count := Order (I); begin
                           Order (I) := Order (J); Order (J) := Temp;
                        end;
                     end if;
                  end loop;
               end loop;
            end if;
            return (if N.Form in E.Object_Value | E.Record_Value then "{" else "[") & Sequence (0) &
              (if N.Form in E.Object_Value | E.Record_Value then "}" else "]");
         when others => return "";
      end case;
   end JSON;
   function JSON_Valid (Data : E.Bytes; Item : E.Span;
      At_Layer : E.Layer := E.Recovery; Ensure_ASCII : Boolean := False;
      Preserve_Bytes : Boolean := False) return Boolean is
     (V.Kind (JSON (Data, Item, At_Layer, Ensure_ASCII, Preserve_Bytes)) /= V.Missing);
   function Agent_Record_JSON (Value : String) return String;
   function Syntax_Inputs
     (Data : E.Bytes; Whole : E.Span; At_Layer : E.Layer := E.Recovery) return String is
      function Merge (Left, Right : String) return String is
        (if Left'Length = 0 then Right elsif Right'Length = 0 then Left else Left & "," & Right);
      function Walk (Source : E.Bytes; Item : E.Span; L : E.Layer;
         Decode_Payload : Boolean := False; Journal : Boolean := False) return String;
      function Journal_Inputs (Source : E.Bytes; Item : E.Span; L : E.Layer) return String is
         N : constant E.View := E.Decode (Source, Item, L);
      begin
         if N.Form /= E.Bytes_Value or else not E.Bytes_Valid (Source, N.Payload) then return ""; end if;
         declare
            Raw : constant E.Bytes := E.Materialize (Source, N.Payload);
            Parsed : constant Worldline.Raw_JSON.Decoded_JSON :=
              Worldline.Raw_JSON.Decode_JSON (Raw, (Raw'First, Raw'Length));
            Events : constant String := V.Field (V.Field (Parsed.Data, "body"), "events");
            function Event_Inputs (I : Natural) return String is
            begin
               if not Parsed.Valid or else I >= V.Count (Events) then return ""; end if;
               declare
                  Record_JSON : constant String := V.Field (V.Element (Events, I), "record");
                  Encoded : constant E.Bytes := Bytes (V.Text (Record_JSON));
                  Encoded_Span : constant Worldline.Archive_Base64.Span := (Encoded'First, Encoded'Length);
               begin
                  if V.Kind (Record_JSON) /= V.String_Value or else
                    not Worldline.Archive_Base64.Canonical (Encoded, Encoded_Span)
                  then return Event_Inputs (I + 1); end if;
                  declare Record_Data : E.Bytes (1 .. Worldline.Archive_Base64.Decoded_Length (Encoded, Encoded_Span)); begin
                     Worldline.Archive_Base64.Decode (Encoded, Encoded_Span, Record_Data);
                     return Merge ((if RA.Valid (Record_Data, (Record_Data'First, Record_Data'Length)) then
                       Walk (Record_Data, (Record_Data'First, Record_Data'Length), E.Recovery) else ""),
                       Event_Inputs (I + 1));
                  end;
               end;
            end Event_Inputs;
         begin return Event_Inputs (0); end;
      end Journal_Inputs;
      function Walk (Source : E.Bytes; Item : E.Span; L : E.Layer;
         Decode_Payload : Boolean := False; Journal : Boolean := False) return String is
         N : constant E.View := E.Decode (Source, Item, L);
         Length : constant E.Count := E.Array_Length (Source, N.Children);
         function Value (I : E.Count) return E.Span is
            Pair : constant E.Span := E.Array_Element (Source, N.Children, I);
         begin
            if L = E.Terminal then return E.Array_Element (Source, Pair, 1); end if;
            return Child (Source, Pair, 1, (if L = E.Finalization then E.Terminal else E.Finalization));
         end Value;
         function Name (I : E.Count) return String is
            Pair : constant E.Span := E.Array_Element (Source, N.Children, I);
         begin
            if L = E.Terminal then
               declare Key : constant E.Span := E.Array_Element (Source, Pair, 0); begin
                  if Key.Length < 2 or else not E.Bytes_Valid (Source, ((Key.First + 1, Key.Length - 2), 1))
                  then return ""; end if;
                  return Raw_String (E.Materialize (Source, ((Key.First + 1, Key.Length - 2), 1)));
               end;
            end if;
            return Scalar (Source, Child (Source, Pair, 0,
              (if L = E.Finalization then E.Terminal else E.Finalization)),
              (if L = E.Finalization then E.Terminal
               elsif L = E.Finalization_Record or else N.Form = E.Record_Value then E.Finalization else L));
         end Name;
         function Members (I : E.Count) return String is
         begin
            if I = Length then return ""; end if;
            if N.Form in E.Object_Value | E.Record_Value then
               declare Key : constant String := Name (I); begin
                  return Merge (Walk (Source, Value (I), L, Key = "payload", Key = "journal_raw"), Members (I + 1));
               end;
            end if;
            return Merge (Walk (Source, E.Array_Element (Source, N.Children, I), L,
              Length = 2 and then I = 1 and then Text_Is
                (Source, E.Array_Element (Source, N.Children, 0), "payload", L)),
              Members (I + 1));
         end Members;
      begin
         if Journal then return Journal_Inputs (Source, Item, L); end if;
         if N.Form = E.Bytes_Value and then Decode_Payload and then E.Bytes_Valid (Source, N.Payload) then
            declare
               Raw : constant E.Bytes := E.Materialize (Source, N.Payload);
               Root : constant E.Span := (Raw'First, Raw'Length);
               Plain : constant E.View := E.Decode (Raw, Root, E.Terminal);
               Packed : constant E.View := E.Decode (Raw, Root, E.Finalization);
            begin
               if E.Decode (Raw, Root, E.Finalization_Record).Form = E.Record_Value
                 and then RA.Valid_Finalization_Record (Raw, Root)
               then return Walk (Raw, Root, E.Finalization_Record); end if;
               if Plain.Form = E.Object_Value then return Walk (Raw, Root, E.Terminal);
               elsif Packed.Form /= E.Invalid then return Walk (Raw, Root, E.Finalization);
               elsif Plain.Form /= E.Invalid then return Walk (Raw, Root, E.Terminal); end if;
            end;
            return "";
         end if;
         if N.Form not in E.Object_Value | E.Record_Value | E.List_Value | E.Tuple_Value then return ""; end if;
         if N.Form = E.Object_Value and then Field (Source, Item, "examinerAudit", L).Length /= 0 then
            declare
               Original : constant String := JSON (Source, Item, L, True, True);
               Mapped : constant String := Agent_Record_JSON (Original);
            begin
               return Merge (Merge
                 ((if Worldline.Source_Syntax_Provider.Authentic (Original) then "" else V.Quote (Original)),
                  (if Mapped = Original or else Worldline.Source_Syntax_Provider.Authentic (Mapped)
                   then "" else V.Quote (Mapped))), Members (0));
            end;
         end if;
         return Members (0);
      end Walk;
   begin return "[" & Walk (Data, Whole, At_Layer) & "]"; end Syntax_Inputs;
   function Acquisition_Data (Data : E.Bytes; Row : E.Span; Finalization : Boolean) return E.Bytes is
      Item : constant E.Span := Field (Data, Row, "engineRawObservations");
      N : constant E.View := E.Decode (Data, Item, E.Recovery);
   begin
      if Item.Length = 0 or else N.Form = E.Null_Value then return E.Bytes'(1 .. 0 => 0); end if;
      if not Finalization or else N.Form = E.List_Value then return Data (Item.First .. Item.First + Item.Length - 1); end if;
      if N.Form /= E.Object_Value or else Count (Data, Item) /= 2 or else
        not Text_Is (Data, Field (Data, Item, "encoding"), "worldline-finalization-acquisitions-v1") or else
        E.Decode (Data, Field (Data, Item, "payload"), E.Recovery).Form /= E.Text_Value
      then return E.Bytes'(1 .. 0 => 0); end if;
      declare
         Enc : constant E.Bytes := E.Materialize (Data, E.Decode (Data, Field (Data, Item, "payload"), E.Recovery).Payload);
         Span : constant Worldline.Archive_Base64.Span := (Enc'First, Enc'Length);
      begin
         if not Worldline.Archive_Base64.Canonical (Enc, Span) then return E.Bytes'(1 .. 0 => 0); end if;
         declare Raw : E.Bytes (1 .. Worldline.Archive_Base64.Decoded_Length (Enc, Span)); begin
            Worldline.Archive_Base64.Decode (Enc, Span, Raw);
            if E.Decode (Raw, (Raw'First, Raw'Length), E.Finalization).Form /= E.List_Value
            then return E.Bytes'(1 .. 0 => 0); end if;
            return Raw;
         end;
      end;
   end Acquisition_Data;
   function Acquisition_Layer (Data : E.Bytes; Row : E.Span; Finalization : Boolean) return E.Layer is
     (if Finalization and then E.Decode (Data, Field (Data, Row, "engineRawObservations"), E.Recovery).Form = E.Object_Value
      then E.Finalization else E.Recovery);
   function Acquisitions (Value : String) return String is
      Payload : constant String := V.Text (V.Field (Value, "payload"));
      Enc : constant E.Bytes := Bytes (Payload);
      B64 : constant Worldline.Archive_Base64.Span := (Enc'First, Enc'Length);
   begin
      if V.Kind (Value) in V.Array_Value | V.Null_Value then return Value; end if;
      if V.Text (V.Field (Value, "encoding")) /= "worldline-finalization-acquisitions-v1"
        or else not Worldline.Archive_Base64.Canonical (Enc, B64) then return ""; end if;
      declare
         Raw : E.Bytes (1 .. Worldline.Archive_Base64.Decoded_Length (Enc, B64));
      begin
         Worldline.Archive_Base64.Decode (Enc, B64, Raw);
         return JSON (Raw, (Raw'First, Raw'Length), E.Finalization, True, True);
      end;
   end Acquisitions;
   function Stored_JSON (Data : E.Bytes; Item : E.Span;
                         L : E.Layer := E.Recovery; Inner_Layer : E.Layer := E.Terminal) return String is
      N : constant E.View := E.Decode (Data, Item, L);
   begin
      if N.Form /= E.Bytes_Value or else not E.Bytes_Valid (Data, N.Payload) then return ""; end if;
      declare Raw : constant E.Bytes := E.Materialize (Data, N.Payload); begin
         return JSON (Raw, (Raw'First, Raw'Length), Inner_Layer, True, True);
      end;
   end Stored_JSON;
   function Stored_Encoding (Data : E.Bytes; Item : E.Span;
                            L : E.Layer := E.Recovery) return E.Bytes is
      N : constant E.View := E.Decode (Data, Item, L);
   begin
      if N.Form /= E.Bytes_Value or else not E.Bytes_Valid (Data, N.Payload)
      then return E.Bytes'(1 .. 0 => 0); end if;
      return E.Materialize (Data, N.Payload);
   end Stored_Encoding;
   function Digest (Text : String) return Worldline.Hash is
      Context : SHA.Context := SHA.Initial;
      Buffer : Attest.Byte_Array (0 .. SHA.Block_Bytes - 1) := (others => 0);
      Used : Natural := 0;
   begin
      for I in Text'Range loop
         Buffer (Used) := Character'Pos (Text (I)); Used := Used + 1;
         if Used = Buffer'Length then SHA.Update (Context, Buffer); Used := 0; end if;
      end loop;
      if Used > 0 then SHA.Update (Context, Buffer (0 .. Used - 1)); end if;
      return SHA.Final (Context);
   end Digest;
   function Hex (Hash : Worldline.Hash) return String is
      Hex_Digits : constant String := "0123456789abcdef";
      Result : String (1 .. Hash'Length * 2);
   begin
      for I in Hash'Range loop
         Result (1 + (I - Hash'First) * 2) := Hex_Digits (1 + Integer (Hash (I)) / 16);
         Result (2 + (I - Hash'First) * 2) := Hex_Digits (1 + Integer (Hash (I)) mod 16);
      end loop;
      return Result;
   end Hex;
   function Hash_Id (Text : String) return String is ("sha256:" & Hex (Digest (Text)));
   function Get (Data, Name : String) return String is
     (if V.Kind (V.Field (Data, Name)) = V.Missing then "null" else V.Field (Data, Name));
   function Canonical_JSON (Value : String; Drop : String := "") return String is
      Root : constant V.Node := V.Parse (Value);
      N : constant Natural := V.Count (Value, Root);
      type Order_Array is array (Positive range <>) of Positive;
      Order : Order_Array (1 .. N);
      function Member (I : Positive) return String is
        (V.Member_Name (Value, Root, I));
      function Rest (I : Positive; First : Boolean) return String is
      begin
         if I > N then return ""; end if;
         if Root.Form = V.Object_Value and then Member (Order (I)) = Drop then
            return Rest (I + 1, First);
         end if;
         return (if First then "" else ",") &
           (if Root.Form = V.Object_Value then V.Quote (Member (Order (I))) & ":" &
              Canonical_JSON (V.Slice (Value, V.Field (Value, Root, Member (Order (I)))))
            else Canonical_JSON (V.Slice (Value, V.Element (Value, Root, I)))) & Rest (I + 1, False);
      end Rest;
   begin
      case Root.Form is
         when V.String_Value => return V.Quote (V.Text (Value, Root));
         when V.Integer_Value => return V.Python_String (Value);
         when V.Number_Value => return V.Python_String (Value);
         when V.Null_Value | V.Boolean_Value => return V.Slice (Value, Root);
         when V.Array_Value | V.Object_Value =>
            for I in Order'Range loop Order (I) := I; end loop;
            if Root.Form = V.Object_Value then
               for I in Order'Range loop
                  for J in Order'Range loop
                     if J > I and then Member (Order (J)) < Member (Order (I)) then
                        declare Temp : constant Positive := Order (I); begin Order (I) := Order (J); Order (J) := Temp; end;
                     end if;
                  end loop;
               end loop;
            end if;
            return (if Root.Form = V.Object_Value then "{" else "[") & Rest (1, True) &
                   (if Root.Form = V.Object_Value then "}" else "]");
         when others => return "";
      end case;
   end Canonical_JSON;
   function Policy_Value (Requirement : String) return String is
      Root : constant V.Node := V.Parse (Requirement);
      function Members (I : Positive; First : Boolean) return String is
      begin
         if I > V.Count (Requirement, Root) then return ""; end if;
         declare Name : constant String := V.Member_Name (Requirement, Root, I); begin
            if Name = "requirementHash" then return Members (I + 1, First); end if;
            return (if First then "" else ",") & V.Quote (Name) & ":" &
              (if Name = "policy" then Canonical_JSON
                (Canonical_JSON (Get (Requirement, Name), "sourceSha256"), "warnings")
               else Canonical_JSON (Get (Requirement, Name))) & Members (I + 1, False);
         end;
      end Members;
      Temp : constant String := "{" & Members (1, True) & "}";
   begin return Canonical_JSON (Temp); end Policy_Value;
   function Context_Valid (Context, Subject : String) return Boolean is
      Requirement : constant String := V.Field (Context, "requirement");
      Expected : constant String := Hash_Id ("worldline-validation-v1" & Canonical_JSON (Context, "contextHash"));
      Req : constant String := Hash_Id ("worldline-validation-v1" & Policy_Value (Requirement));
   begin
      return V.Kind (Context) = V.Object_Value
        and then (V.Decimal (Context, V.Field (Context, V.Parse (Context), "schemaVersion")) = "1"
          or else (V.Kind (V.Field (Context, "schemaVersion")) = V.Boolean_Value
            and then V.Truth (V.Field (Context, "schemaVersion")))
          or else (V.Kind (V.Field (Context, "schemaVersion")) = V.Number_Value
            and then V.Number_Image (Context, V.Field (Context, V.Parse (Context), "schemaVersion")) = "1.0"))
        and then V.Text (V.Field (Context, "contextHash")) = Expected
        and then V.Kind (Requirement) = V.Object_Value
        and then V.Text (V.Field (Requirement, "requirementHash")) = Req
        and then V.Text (V.Field (Context, "requirementHash")) = Req
        and then V.Text (V.Field (V.Field (Context, "candidate"), "instanceId")) = Subject;
   end Context_Valid;
   procedure Put (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
                  Result : out T.Span; Valid : in out Boolean;
                  L : E.Layer := E.Recovery; Integer_Allowed : Boolean := False;
                  Expected_Form : E.Value_Kind := E.Bytes_Value) is
      N : constant E.View := E.Decode (Data, Item, L);
   begin
      Result := (Item.First, 0);
      if (N.Form /= Expected_Form
        and then not (Integer_Allowed and then N.Form = E.Integer_Value and then not N.Sign))
        or else (N.Form = E.Integer_Value and then N.Sign)
      then Valid := False; return; end if;
      if not E.Bytes_Valid (Data, N.Payload) then Valid := False; return; end if;
      declare Raw : constant E.Bytes := E.Materialize (Data, N.Payload); begin
         if Item.First not in Arena'Range or else Raw'Length > Arena'Last - Item.First + 1
         then Valid := False; return; end if;
         Result := (Item.First, Raw'Length);
         for I in Raw'Range loop Arena (Item.First + I - Raw'First) := Raw (I); end loop;
      end;
   end Put;
   procedure Read_Requirement (Data : E.Bytes; Item : E.Span;
      Arena : in out E.Bytes; Valid : in out Boolean;
      Result : out T.Optional_Requirement; L : E.Layer := E.Recovery;
      Expected_Form : E.Value_Kind := E.Bytes_Value) is
      S : T.Span;
   begin
      if Is_Null (Data, Item, L) then Result := (Present => False); return; end if;
      Put (Data, Item, Arena, S, Valid, L, Expected_Form => Expected_Form);
      Result := (True, T.R.Requirement_Id (S));
   end Read_Requirement;
   procedure Read_Binding (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Result : out T.Attempt_Binding;
      L : E.Layer := E.Recovery) is
      Store, Subject, Content, Run, Epoch : T.Span;
      Req : T.Optional_Requirement;
   begin
      Put (Data, Field (Data, Item, "store_id", L), Arena, Store, Valid, L);
      Put (Data, Field (Data, Item, "subject", L), Arena, Subject, Valid, L);
      Put (Data, Field (Data, Item, "content", L), Arena, Content, Valid, L);
      Put (Data, Field (Data, Item, "run", L), Arena, Run, Valid, L);
      Put (Data, Field (Data, Item, "epoch", L), Arena, Epoch, Valid, L);
      Read_Requirement (Data, Field (Data, Item, "requirement", L), Arena, Valid, Req, L);
      Result := (T.Store_Identity (Store), T.Subject_Identity (Subject),
                 T.Content_Identity (Content), T.Run_Identity (Run), T.Epoch (Epoch), Req);
   end Read_Binding;
   procedure Read_Cursor (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Result : out T.Cursor;
      L : E.Layer := E.Recovery; Record_Form : Boolean := False) is
      Epoch, Run : T.Span;
   begin
      if Is_Null (Data, Item, L) then Result := (Present => False); return; end if;
      if Record_Form then
         if E.Decode (Data, Item, L).Form /= E.Object_Value or else Count (Data, Item, L) /= 2 then
            Valid := False;
         end if;
         Put (Data, Field (Data, Item, "epoch", L), Arena, Epoch, Valid, L, True, E.Integer_Value);
         Put (Data, Field (Data, Item, "run", L), Arena, Run, Valid, L, Expected_Form => E.Text_Value);
      else
         if Count (Data, Item, L) /= 2 then Valid := False; end if;
         Put (Data, Child (Data, Item, 0, L), Arena, Epoch, Valid, L);
         Put (Data, Child (Data, Item, 1, L), Arena, Run, Valid, L);
      end if;
      Result := (True, T.Run_Identity (Run), T.Epoch (Epoch));
   end Read_Cursor;
   function History_Cursor (C : T.Cursor) return H.Optional_Cursor is
   begin
      if not C.Present then
         return (Present => False);
      else
         return (True, ((True, H.Epoch_Id'(C.Sequence.First, C.Sequence.Length)),
                        H.Evaluation_Id'(C.Run.First, C.Run.Length)));
      end if;
   end History_Cursor;
   function Outcome (Data : E.Bytes; Item : E.Span; L : E.Layer := E.Recovery)
                     return T.E.Outcome is
     (if Text_Is (Data, Item, "PASS", L) then T.E.Passed
      elsif Text_Is (Data, Item, "FAIL", L) then T.E.Failed else T.E.No_Outcome);
   function Outcome_Valid (Data : E.Bytes; Item : E.Span; L : E.Layer) return Boolean is
     (Is_Null (Data, Item, L) or else Text_Is (Data, Item, "PASS", L) or else Text_Is (Data, Item, "FAIL", L));
   function State_Name (S : T.E.Execution_State) return String is
     (case S is when T.E.Not_Attempted => "Not_Attempted", when T.E.Prepared => "Prepared",
      when T.E.Started => "Started", when T.E.Interrupted => "Interrupted",
      when T.E.Error_Before_Examiner => "Error_Before_Examiner",
      when T.E.Incomplete_Unknown => "Incomplete_Unknown", when T.E.Evaluator_Incomplete => "Evaluator_Incomplete",
      when T.E.Unclassified => "Unclassified", when T.E.Completed => "Completed");
   function State_Valid (Data : E.Bytes; Item : E.Span; L : E.Layer) return Boolean is
   begin
      for S in T.E.Execution_State loop
         if Text_Is (Data, Field (Data, Item, "state", L), State_Name (S), L) then return True; end if;
      end loop;
      return False;
   end State_Valid;
   function Carried_State (Data : E.Bytes; Item : E.Span;
      L : E.Layer := E.Recovery) return T.E.Execution_State;
   function Record_Is (Data : E.Bytes; Item : E.Span; Name : String;
      L : E.Layer := E.Recovery) return Boolean is
      N : constant E.View := E.Decode (Data, Item, L);
   begin
      return N.Form = E.Record_Value and then E.Bytes_Valid (Data, N.Record_Name)
        and then Raw_String (E.Materialize (Data, N.Record_Name)) = Name;
   end Record_Is;
   procedure Read_Terminal (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Result : out T.Terminal_Record;
      L : E.Layer := E.Recovery) is
      B : T.Attempt_Binding;
      Source, Context : T.Span;
   begin
      if not Record_Is (Data, Item, "CaptureValue", L) or else not State_Valid (Data, Item, L)
        or else not Outcome_Valid (Data, Field (Data, Item, "outcome", L), L) then Valid := False; end if;
      Read_Binding (Data, Field (Data, Item, "bound", L), Arena, Valid, B, L);
      Put (Data, Field (Data, Item, "source", L), Arena, Source, Valid, L);
      Put (Data, Field (Data, Item, "context", L), Arena, Context, Valid, L);
      Result := (B, T.Source_Identity (Source), T.Captured_Bytes (Context),
        Carried_State (Data, Item, L),
        Outcome (Data, Field (Data, Item, "outcome", L), L));
   end Read_Terminal;
   procedure Read_Summary (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Result : out H.Evaluation_Record;
      L : E.Layer := E.Recovery) is
      Subject, Content, Run, Epoch : T.Span;
      Req : T.Optional_Requirement;
      Native_Requirement : H.Optional_Requirement;
      O : constant T.E.Outcome := Outcome (Data, Field (Data, Item, "outcome", L), L);
   begin
      if not Record_Is (Data, Item, "HistoryValue", L)
        or else not (Text_Is (Data, Field (Data, Item, "state", L), "PENDING", L) or else
          Text_Is (Data, Field (Data, Item, "state", L), "COMPLETED", L) or else
          Text_Is (Data, Field (Data, Item, "state", L), "ERROR", L))
        or else not Outcome_Valid (Data, Field (Data, Item, "outcome", L), L) then Valid := False; end if;
      Put (Data, Field (Data, Item, "subject", L), Arena, Subject, Valid, L);
      Put (Data, Field (Data, Item, "content", L), Arena, Content, Valid, L);
      Put (Data, Field (Data, Item, "run", L), Arena, Run, Valid, L);
      Put (Data, Field (Data, Item, "epoch", L), Arena, Epoch, Valid, L);
      Read_Requirement (Data, Field (Data, Item, "requirement", L), Arena, Valid, Req, L);
      if Req.Present then
         Native_Requirement := (True, H.Requirement_Id'(Req.Value.First, Req.Value.Length));
      else
         Native_Requirement := (Present => False);
      end if;
      Result := (Subject => (True, H.Subject_Id'(Subject.First, Subject.Length)),
        Content => (True, H.Content_Id'(Content.First, Content.Length)),
        Requirement => Native_Requirement,
        Run => (True, H.Evaluation_Id'(Run.First, Run.Length)),
        Sequence => (True, H.Epoch_Id'(Epoch.First, Epoch.Length)),
        State => (if Text_Is (Data, Field (Data, Item, "state", L), "COMPLETED", L)
                  then H.Completed elsif Text_Is (Data, Field (Data, Item, "state", L), "PENDING", L)
                  then H.Pending else H.Error),
        Outcome => (if O = T.E.Passed then H.Passed elsif O = T.E.Failed then H.Failed else H.No_Verdict));
   end Read_Summary;
   function Raw_Equal (Data : E.Bytes; Item : E.Span; Raw : W.Raw_Record;
                       L : E.Layer := E.Recovery) return Boolean is
      B : constant E.Bytes := Stored_Encoding (Data, Field (Data, Item, "raw", L), L);
   begin
      if B'Length /= 34 then return False; end if;
      for K in W.Observation_Field loop
         if B (B'First + W.Observation_Field'Pos (K)) /= Raw.Observations (K) then return False; end if;
      end loop;
      if B (B'First + 14) /= Raw.Report_Based then return False; end if;
      for K in W.R.Fact_Index loop
         if B (B'First + 15 + E.Count (W.R.Fact_Index'Pos (K))) /= Raw.Report_Facts (K)
         then return False; end if;
      end loop;
      for K in W.Presence_Field loop
         if B (B'First + 29 + W.Presence_Field'Pos (K)) /= Raw.Presence (K) then return False; end if;
      end loop;
      return True;
   end Raw_Equal;
   function Stream_For (Data : E.Bytes; Streams, Run : E.Span;
                        L : E.Layer := E.Recovery) return E.Span is
      N : constant E.View := E.Decode (Data, Streams, L);
   begin
      for I in E.Count range 0 .. E.Array_Length (Data, N.Children) - 1 loop
         declare
            Pair : constant E.Span := E.Array_Element (Data, N.Children, I);
            Key : constant E.Span := Child (Data, Pair, 0, E.Finalization);
            Value : constant E.Span := Child (Data, Pair, 1, E.Finalization);
         begin
            if Same (Data, Key, Run, L) then return Value; end if;
         end;
      end loop;
      return Empty;
   end Stream_For;
   function Terminal_Encoding (Data : E.Bytes; Item : E.Span;
      L : E.Layer := E.Recovery) return String;
   function String_Encoding (Value : String) return String;
   function Lifted (Tag, Value : String) return String;
   function Terminal_Value_Valid (Data : E.Bytes; Item : E.Span) return Boolean
     with Subprogram_Variant => (Decreases => Item.Length);
   function Terminal_Value_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
      N : constant E.View := E.Decode (Data, Item, E.Terminal);
      function Text_Valid (Value : E.Byte_View) return Boolean is
      begin
         if not E.Bytes_Valid (Data, Value) then return False; end if;
         declare
            Raw : constant E.Bytes := E.Materialize (Data, Value);
         begin
            return Worldline.Archive_Text.Text_Valid (Raw, (Raw'First, Raw'Length));
         end;
      end Text_Valid;
   begin
      case N.Form is
         when E.Null_Value | E.Boolean_Value => return True;
         when E.Text_Value => return Text_Valid (N.Payload);
         when E.Integer_Value =>
            if not E.Bytes_Valid (Data, N.Payload) then return False; end if;
            declare
               Raw : constant E.Bytes := E.Materialize (Data, N.Payload);
            begin
               return (Raw'Length = 0 or else Raw (Raw'Last) /= 0)
                 and then (not N.Sign or else Raw'Length > 0);
            end;
         when E.Float_Value =>
            return E.Bytes_Valid (Data, N.Payload)
              and then E.Materialize (Data, N.Payload)'Length = 8;
         when E.List_Value =>
            if not E.Is_Array (Data, N.Children) then return False; end if;
            for I in E.Count range 0 .. E.Array_Length (Data, N.Children) - 1 loop
               if not Terminal_Value_Valid (Data, E.Array_Element (Data, N.Children, I))
               then return False; end if;
            end loop;
            return True;
         when E.Object_Value =>
            if not E.Is_Array (Data, N.Children) then return False; end if;
            for I in E.Count range 0 .. E.Array_Length (Data, N.Children) - 1 loop
               declare
                  Pair : constant E.Span := E.Array_Element (Data, N.Children, I);
                  Key : constant E.Span := E.Array_Element (Data, Pair, 0);
               begin
                  if not E.Is_Array (Data, Pair) or else E.Array_Length (Data, Pair) /= 2
                    or else Key.Length < 2
                    or else Data (Key.First) /= E.Q.Byte (Character'Pos ('"'))
                    or else Data (Key.First + Key.Length - 1) /= E.Q.Byte (Character'Pos ('"'))
                    or else not Text_Valid (((Key.First + 1, Key.Length - 2), 1))
                    or else not Terminal_Value_Valid (Data, E.Array_Element (Data, Pair, 1))
                  then return False; end if;
                  -- Canonical base64 is injective. Compare the full original
                  -- key tokens without allocating decoded copies per join.
                  for J in E.Count range 0 .. I - 1 loop
                     declare
                        Prior : constant E.Span := E.Array_Element
                          (Data, E.Array_Element (Data, N.Children, J), 0);
                     begin
                        if Key.Length = Prior.Length
                          and then (for all K in E.Count range 0 .. Key.Length - 1 =>
                            Data (Key.First + K) = Data (Prior.First + K))
                        then return False; end if;
                     end;
                  end loop;
               end;
            end loop;
            return True;
         when others => return False;
      end case;
   end Terminal_Value_Valid;
   function Check_Metadata (Data : E.Bytes; Item : E.Span; Payload : String;
                            Capture_Source, Invocation : E.Span;
                            L : E.Layer := E.Recovery) return Boolean is
      pragma Unreferenced (Payload);
      Raw : constant E.Bytes := Stored_Encoding (Data, Field (Data, Item, "payload", L), L);
      Root : constant E.Span := (Raw'First, Raw'Length);
      Interrupted : constant Boolean := Invocation.Length /= 0 and then
        Is_Null (Data, Child (Data, Invocation, 2, L), L);
      Started : constant E.Span := Child (Data, Invocation, 1, L);
      Check : constant E.Span := Field (Raw, Root, "id", E.Terminal);
      Source : constant E.Span := Field (Data, Item, "source", L);
      Execution : constant E.Span := Field (Data, Item, "execution", L);
      Verifier : constant E.Span := Field (Data, Item, "verifier", L);
      Start : constant E.Span := Field (Raw, Root, "engineInvocationObservation", E.Terminal);
      Boundary : constant E.Span := Field (Raw, Root, "evaluatorBoundary", E.Terminal);
      Executed : constant E.Span := Field (Raw, Root, "executedVerifierSet", E.Terminal);
   begin
      if E.Decode (Raw, Root, E.Terminal).Form /= E.Object_Value then return False; end if;
      if Interrupted then
         return E.Decode (Data, Field (Data, Started, "checkId", L), L).Form = E.Text_Value
           and then E.Decode (Data, Child (Data, Invocation, 0, L), L).Form = E.Text_Value
           and then Scalar (Data, Field (Data, Item, "check", L), L) =
             Scalar (Data, Field (Data, Started, "checkId", L), L)
           and then Same (Data, Source, Capture_Source, L)
           and then Scalar (Data, Execution, L) = Scalar (Data, Child (Data, Invocation, 0, L), L)
           and then Is_Null (Data, Verifier, L);
      end if;
      if (if E.Decode (Raw, Check, E.Terminal).Form = E.Text_Value then
            Scalar (Data, Field (Data, Item, "check", L), L) /= Scalar (Raw, Check, E.Terminal)
          else Raw_String (Stored_Encoding (Data, Field (Data, Item, "check", L), L)) /=
            Terminal_Encoding (Raw, Check, E.Terminal))
        or else Raw_String (Stored_Encoding (Data, Source, L)) /=
          Terminal_Encoding (Raw, Field (Raw, Root, "origin", E.Terminal), E.Terminal)
      then return False; end if;
      if (Start.Length = 0 or else Is_Null (Raw, Start, E.Terminal))
        and then (Boundary.Length = 0 or else Is_Null (Raw, Boundary, E.Terminal))
      then
         if not Is_Null (Data, Execution, L) then return False; end if;
      elsif Raw_String (Stored_Encoding (Data, Execution, L)) /=
        "[""object"",[[" & V.Quote (Base64 (Bytes ("engineInvocation"))) & "," &
        Terminal_Encoding (Raw, Start, E.Terminal) & "],[" &
        V.Quote (Base64 (Bytes ("evaluatorBoundary"))) & "," &
        Terminal_Encoding (Raw, Boundary, E.Terminal) & "]]]"
      then return False; end if;
      return (if Executed.Length = 0 or else Is_Null (Raw, Executed, E.Terminal) then
        Is_Null (Data, Verifier, L) else Raw_String (Stored_Encoding (Data, Verifier, L)) =
          Terminal_Encoding (Raw, Executed, E.Terminal));
   end Check_Metadata;
   function Carried_Extras_Valid (Data : E.Bytes; Item : E.Span;
                                 L : E.Layer := E.Recovery) return Boolean is
      Observations : constant E.Span := Field (Data, Item, "observations", L);
      Evidence : constant E.Span := Field (Data, Item, "evidence", L);
      Raw : W.Raw_Record := W.Zero_Record;
      type Small_Value is record Valid : Boolean; Value : W.Byte; end record;
      function Small (Part : E.Span; Max : Natural) return Small_Value is
         N : constant E.View := E.Decode (Data, Part, L);
      begin
         if N.Form /= E.Integer_Value or else N.Sign then return (False, 0); end if;
         declare B : constant E.Bytes := E.Materialize (Data, N.Payload); begin
            if B'Length > 1 then return (False, 0); end if;
            return (B'Length = 0 or else Natural (B (B'First)) <= Max,
                    (if B'Length = 0 then 0 else B (B'First)));
         end;
      end Small;
      B : Small_Value;
   begin
      if not Is_Null (Data, Observations, L) then
         if Count (Data, Observations, L) /= 13 then return False; end if;
         for K in W.Observation_Field range W.Source_Field .. W.Unsatisfied_Imports_Field loop
            B := Small (Child (Data, Observations, W.Observation_Field'Pos (K), L), 255);
            if not B.Valid then return False; end if;
            Raw.Observations (K) := B.Value;
         end loop;
      end if;
      if not Is_Null (Data, Evidence, L) then
         if Count (Data, Evidence, L) /= 5 then return False; end if;
         for K in W.Presence_Field loop
            declare N : constant E.View := E.Decode (Data, Child (Data, Evidence, W.Presence_Field'Pos (K), L), L); begin
               if N.Form /= E.Boolean_Value then return False; end if;
               Raw.Presence (K) := (if N.Boolean_Bit then 1 else 0);
            end;
         end loop;
      end if;
      return W.Well_Formed (Raw)
        and then Raw.Observations (W.Bundle_Stable_Field) <= Raw.Observations (W.Bundle_Is_Mapping_Field)
        and then Raw.Observations (W.Bundle_Changed_Field) <= Raw.Observations (W.Bundle_Is_Mapping_Field)
        and then (Text_Is (Data, Field (Data, Item, "report", L), "NOT_APPLICABLE", L)
          or else Text_Is (Data, Field (Data, Item, "report", L), "VERIFIED", L)
          or else Text_Is (Data, Field (Data, Item, "report", L), "UNTRUSTED", L));
   end Carried_Extras_Valid;
   function Derive_Original
     (Result_Record, Declared : String;
      Facts_Data : E.Bytes; Capsules : E.Span) return EP.Produced_Record is
      Inner : constant String := V.Field (Result_Record, "rawRunnerResult");
      Selected : constant String := (if V.Kind (Inner) = V.Object_Value then Inner else Result_Record);
      Operands : constant Worldline.Recovery_Syntax.Capsule_Operands :=
        Worldline.Recovery_Syntax.Find (Selected, Facts_Data, Capsules);
   begin
      if Operands.Present then
         return EP.Original_Projection (Result_Record, Declared,
           Worldline.Recovery_Syntax.Operand_Text (Facts_Data, Operands.Declaration),
           Worldline.Recovery_Syntax.Operand_Text (Facts_Data, Operands.Capture));
      end if;
      return EP.Original_Projection (Result_Record, Declared);
   end Derive_Original;
   function Owned_Matches (Data : E.Bytes; Owned : E.Span;
                           Produced : EP.Produced_Record;
                           L : E.Layer := E.Recovery) return Boolean;
   procedure Read_Result (Data : E.Bytes; Item, Capture_Source, Invocation : E.Span;
      Arena : in out E.Bytes; Valid : in out Boolean; Result : out R.Measured_Result;
      L : E.Layer := E.Recovery; Finalization : Boolean := False;
      Final_Binding : T.Attempt_Binding :=
        ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (Present => False));
      Facts_Data : E.Bytes; Capsules : E.Span) is
      Payload : constant String := Stored_JSON (Data, Field (Data, Item, "payload", L), L);
      Declared : constant String := Stored_JSON (Data, Field (Data, Item, "declared", L), L);
      Produced : constant EP.Produced_Record :=
        Derive_Original (Payload, Declared, Facts_Data, Capsules);
      B : T.Attempt_Binding;
      Check, Source, Payload_Span, Declared_Span, Execution, Verifier : T.Span;
      EX : T.Optional_Execution := (Present => False);
      VE : T.Optional_Verifier := (Present => False);
      C : W.E.Classification;
   begin
      if not Record_Is (Data, Item, (if Finalization then "UnsealedResult" else "CheckValue"), L)
        or else not State_Valid (Data, Item, L)
        or else not Outcome_Valid (Data, Field (Data, Item, "outcome", L), L)
        or else (V.Kind (Declared) /= V.Null_Value and then
          (V.Kind (Declared) /= V.Object_Value
           or else V.Kind (V.Field (Declared, "format")) = V.Missing
           or else V.Kind (V.Field (Declared, "profile")) = V.Missing
           or else V.Kind (V.Field (Declared, "bundle_declared")) = V.Missing))
      then Valid := False; end if;
      if V.Kind (Declared) = V.Object_Value then
         for I in 1 .. V.Count (Declared, V.Parse (Declared)) loop
            declare Name : constant String := V.Member_Name (Declared, V.Parse (Declared), I); begin
               if Name not in "format" | "profile" | "bundle_declared" | "origin" then Valid := False; end if;
            end;
         end loop;
      end if;
      if Finalization then B := Final_Binding;
      else Read_Binding (Data, Field (Data, Item, "bound", L), Arena, Valid, B, L); end if;
      Put (Data, Field (Data, Item, "check", L), Arena, Check, Valid, L);
      Put (Data, Field (Data, Item, "source", L), Arena, Source, Valid, L);
      Put (Data, Field (Data, Item, "payload", L), Arena, Payload_Span, Valid, L);
      Put (Data, Field (Data, Item, "declared", L), Arena, Declared_Span, Valid, L);
      if not Is_Null (Data, Field (Data, Item, "execution", L), L) then
         Put (Data, Field (Data, Item, "execution", L), Arena, Execution, Valid, L);
         EX := (True, T.Execution_Identity (Execution));
      end if;
      if not Is_Null (Data, Field (Data, Item, "verifier", L), L) then
         Put (Data, Field (Data, Item, "verifier", L), Arena, Verifier, Valid, L);
         VE := (True, T.Verifier_Identity (Verifier));
      end if;
      if V.Kind (Payload) /= V.Object_Value or else not W.Well_Formed (Produced.Raw)
        or else not Check_Metadata (Data, Item, Payload, Capture_Source, Invocation, L)
        or else (if Finalization then not Owned_Matches (Data, Field (Data, Item, "wire", L), Produced, L)
                 else not Carried_Extras_Valid (Data, Item, L))
      then Valid := False; end if;
      if W.Well_Formed (Produced.Raw) then
         C := W.E.Expected_Classification (W.Decode (Produced.Raw).Value.Facts);
      else C := (Execution => W.E.Incomplete_Unknown, Result => W.E.No_Outcome, Bundle => W.E.Unknown_Integrity); end if;
      Result := (Item => (B, T.Check_Identity (Check), T.Source_Identity (Source), EX, VE,
        T.E.Execution_State'Val (W.E.Execution_State'Pos (C.Execution)),
        T.E.Outcome'Val (W.E.Outcome'Pos (C.Result)), T.Captured_Bytes (Payload_Span)),
        Raw => Produced.Raw,
        Confinement => W.Byte (Worldline.Evaluation_Report_Facts.Confinement_Observation'Pos (Produced.Confinement)),
        Declared => T.Captured_Bytes (Declared_Span));
   end Read_Result;
   function Additional (Data : E.Bytes; Typed : E.Span;
                        L : E.Layer := E.Recovery) return String is
   begin
      for I in E.Count range 0 .. Count (Data, Typed, L) - 1 loop
         declare Payload : constant String := Stored_JSON
           (Data, Field (Data, Child (Data, Typed, I, L), "payload", L), L); begin
            if V.Text (V.Field (Payload, "id")) = "verifiers-modified"
              and then V.Text (V.Field (Payload, "origin")) = "engine"
            then return "[" & V.Quote ("verifiers-modified") & "]"; end if;
         end;
      end loop;
      return "[]";
   end Additional;
   function Roster_Policy (Plan : String) return R.Declaration is
     (if V.Count (V.Field (Plan, "required")) > 0 then R.Old.Required_Checks
      elsif V.Truth (V.Field (Plan, "empty")) then R.Old.Explicit_Empty
      else R.Old.Missing_Declaration);
   function Engine_Declaration (Agent : Boolean := False) return String is
     ("{""bundle_declared"":false,""format"":" & V.Quote (if Agent then "exit" else "engine") &
       ",""origin"":" & V.Quote (if Agent then "agent" else "engine") & ",""profile"":null}");
   function Declaration_Encoding (Value : String) return String;
   function Plan_Declaration (Plan, Name : String) return String is
     (if Name = "evaluation-complete" or else
        (Name = "verifiers-modified" and then V.Truth (Get (Plan, "engineModified")))
      then Engine_Declaration
      elsif Name = "agent" and then V.Truth (Get (Plan, "engineAgent")) then Engine_Declaration (True)
      else V.Field (V.Field (Plan, "declarations"), Name));
   function Policy_Plan (Requirement, Additional : String; Agent_Required : Boolean := False) return String is
      Base : constant String := P.Project (Requirement, "[]", False);
      Required : constant String := Get (Base, "required");
      function Has_Agent return Boolean is
      begin
         for I in 1 .. V.Count (Required) loop
            if V.Text (V.Element (Required, I - 1)) = "agent" then return True; end if;
         end loop;
         return False;
      end Has_Agent;
      function Names (I : Natural) return String is
        (if I = V.Count (Required) then "" else (if I = 0 then "" else ",") &
         V.Element (Required, I) & Names (I + 1));
      Add_Agent : constant Boolean := Agent_Required and then not Has_Agent;
      Modified : constant Boolean := V.Count (Additional) > 0;
   begin
      return "{""status"":" & Get (Base, "status") & ",""required"":[" & Names (0) &
        (if Add_Agent then (if V.Count (Required) > 0 then "," else "") & """agent""" else "") &
        (if Modified then (if V.Count (Required) > 0 or else Add_Agent then "," else "") &
          """verifiers-modified""" else "") & "],""empty"":" & Get (Base, "empty") &
        ",""declarations"":" & Get (Base, "declarations") &
        ",""engineAgent"":" & (if Agent_Required then "true" else "false") &
        ",""engineModified"":" & (if Modified then "true" else "false") & "}";
   end Policy_Plan;
   function Plan_Length (Plan : String; Completion : Boolean := True) return E.Count is
      Required : constant String := V.Field (Plan, "required");
      Size : E.Count := 0;
      procedure Add (Name : String) is
         D : constant String := Declaration_Encoding (Plan_Declaration (Plan, Name));
      begin
         if E.Count (Name'Length) > E.Count'Last - Size then Size := E.Count'Last; return; end if;
         Size := Size + E.Count (Name'Length);
         if E.Count (D'Length) > E.Count'Last - Size then Size := E.Count'Last; return; end if;
         Size := Size + E.Count (D'Length);
      end Add;
   begin
      for I in 1 .. V.Count (Required) loop Add (V.Text (V.Element (Required, I - 1))); end loop;
      if Completion then Add ("evaluation-complete"); end if;
      return Size;
   end Plan_Length;
   procedure Append (Arena : in out E.Bytes; Position : in out E.Count;
      Value : String; Result : out T.Span; Valid : in out Boolean) is
   begin
      Result := (Position, E.Count (Value'Length));
      if Position not in Arena'Range or else Result.Length > Arena'Last - Position + 1
        or else Result.Length > E.Count'Last - Position
      then Valid := False; return; end if;
      for I in Value'Range loop Arena (Position + E.Count (I - Value'First)) := Character'Pos (Value (I)); end loop;
      Position := Position + Result.Length;
   end Append;
   function Measured_Epoch (Data : E.Bytes; Payload : E.Span; L : E.Layer) return E.Bytes is
      N : constant E.View := E.Decode (Data, Payload, L);
   begin
      if N.Form /= E.Bytes_Value or else not E.Bytes_Valid (Data, N.Payload) then return (1 .. 0 => 0); end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, N.Payload);
         Root : constant E.Span := (Raw'First, Raw'Length);
         Initial : constant E.Span := Field (Raw, Field (Raw, Root, "captureObservation", E.Terminal), "captureContext", E.Terminal);
         Epoch : constant E.View := E.Decode (Raw, Field (Raw, Initial, "evaluationEpoch", E.Terminal), E.Terminal);
      begin
         if Epoch.Form /= E.Integer_Value or else Epoch.Sign or else not E.Bytes_Valid (Raw, Epoch.Payload)
         then return (1 .. 0 => 0); end if;
         return E.Materialize (Raw, Epoch.Payload);
      end;
   end Measured_Epoch;
   function Start_Plan (Data : E.Bytes; Start : E.Span; L : E.Layer) return String is
      Requirement : constant String := Stored_JSON (Data, Field (Data, Start, "policy", L), L);
      Native : constant String := P.Project (Requirement, "[]", False);
      Required : constant E.Span := Field (Data, Start, "required", L);
      function Names (I : E.Count) return String is
        (if I = Count (Data, Required, L) then "" else (if I = 0 then "" else ",") &
         V.Quote (Scalar (Data, Child (Data, Child (Data, Required, I, L), 0, L), L)) & Names (I + 1));
   begin
      return "{""status"":" & Get (Native, "status") & ",""required"":[" & Names (0) &
        "],""empty"":" & Get (Native, "empty") & ",""declarations"":" &
        Get (Native, "declarations") & ",""engineAgent"":true,""engineModified"":true}";
   end Start_Plan;
   function Arena_Length (Data : E.Bytes; Material : E.Span; At_Layer : E.Layer := E.Recovery) return E.Count is
      Term : constant E.Span := Field (Data, Material, "terminal", At_Layer);
      Material_Rows : constant E.Span := Child (Data, Term, 2, At_Layer);
      Found : constant E.Span := Field (Data, Material, "finalization", At_Layer);
      Size : E.Count := Data'Length;
      Valid : Boolean := True;
      procedure Add (Length : E.Count) is
      begin
         if Length > E.Count'Last - Size then Valid := False; else Size := Size + Length; end if;
      end Add;
   begin
      for I in E.Count range 0 .. Count (Data, Material_Rows, At_Layer) - 1 loop
         declare
            Retained : constant E.Span := Child (Data, Child (Data, Material_Rows, I, At_Layer), 1, At_Layer);
            Typed : constant E.Span := Child (Data, Retained, 2, At_Layer);
            Payload_Span : constant E.Span := (if Count (Data, Typed, At_Layer) = 0 then (1, 0)
              else Field (Data, Child (Data, Typed, Count (Data, Typed, At_Layer) - 1, At_Layer), "payload", At_Layer));
            Payload : constant String := Stored_JSON (Data, Payload_Span, At_Layer);
            Observed : constant String := V.Field (Payload, "captureObservation");
            Initial : constant String := V.Field (Observed, "captureContext");
            Measurement : constant String := V.Field (Initial, "measurement");
         begin
            if not Is_Null (Data, Retained, At_Layer)
              and then V.Text (V.Field (Payload, "id")) = "evaluation-complete"
              and then V.Text (V.Field (Payload, "origin")) = "engine"
              and then V.Kind (Observed) = V.Object_Value
            then
               Add (Plan_Length (Policy_Plan (V.Field (Initial, "requirement"), Additional (Data, Typed, At_Layer))));
               Add (E.Count (V.Text (V.Field (Initial, "storeId"))'Length));
               Add (E.Count (V.Text (V.Field (Initial, "run"))'Length));
               Add (E.Count (V.Text (V.Field (Measurement, "worldInstance"))'Length));
               Add (E.Count (V.Text (V.Field (Measurement, "contentId"))'Length));
               Add (E.Count (V.Text (V.Field (V.Field (Initial, "requirement"), "requirementHash"))'Length));
               Add (E.Count (Measured_Epoch (Data, Payload_Span, At_Layer)'Length));
               Add (E.Count (V.Text (V.Field (Measurement, "observedContentRoot"))'Length));
               Add (E.Count (V.Text (V.Field (V.Field (Observed, "postMeasurement"), "observedContentRoot"))'Length));
            end if;
         end;
      end loop;
      if not Is_Null (Data, Found, At_Layer) then
         declare
            Start : constant E.Span := Child (Data, Found, 0, At_Layer);
         begin
            Add (Plan_Length (Start_Plan (Data, Start, At_Layer), False));
            if not Is_Null (Data, Child (Data, Found, 1, At_Layer), At_Layer) then
               Add (Plan_Length ("{""required"":[]}", True));
            end if;
         end;
      end if;
      if not Valid or else Size = 0 or else Size - 1 > E.Count'Last - Data'First then return 0; end if;
      return Size;
   end Arena_Length;
   function Arena_Last (Data : E.Bytes; Material : E.Span) return E.Count is
      Size : constant E.Count := Arena_Length (Data, Material);
   begin return (if Size = 0 then Data'Last else Data'First + Size - 1); end Arena_Last;
   procedure Plan_Checks (Plan : String; Arena : in out E.Bytes;
      Position : in out E.Count; Checks : out R.Check_Array;
      Completion : out R.Required_Check; Valid : in out Boolean;
      Include_Completion : Boolean := True) is
      Required : constant String := V.Field (Plan, "required");
      procedure Build (Name : String; Result : out R.Required_Check) is
         Name_Span, Declared : T.Span;
      begin
         Append (Arena, Position, Name, Name_Span, Valid);
         Append (Arena, Position, Declaration_Encoding (Plan_Declaration (Plan, Name)), Declared, Valid);
         Result := (T.Check_Identity (Name_Span), T.Captured_Bytes (Declared));
      end Build;
   begin
      if Checks'Length /= V.Count (Required) then Valid := False; return; end if;
      for I in Checks'Range loop Build (V.Text (V.Element (Required, Natural (I - Checks'First))), Checks (I)); end loop;
      if Include_Completion then Build ("evaluation-complete", Completion);
      else Completion := ((1, 0), (1, 0)); end if;
   end Plan_Checks;
   procedure Classify_Terminal (Data : E.Bytes; Capture, Typed, Stream : E.Span;
      Arena : in out E.Bytes; Position : in out E.Count; Valid : in out Boolean;
      Classification : out R.Classification; Saved_Capture : T.Terminal_Record;
      Measured : R.Measured_Array;
      L : E.Layer := E.Recovery) is
      Rows : R.Measured_Array renames Measured;
      Payload : constant String := (if Rows'Length = 0 then "null" else Stored_JSON
        (Data, Field (Data, Child (Data, Typed, Rows'Length - 1, L), "payload", L), L));
      Observed : constant String := V.Field (Payload, "captureObservation");
      Initial : constant String := V.Field (Observed, "captureContext");
      Requirement : constant String := V.Field (Initial, "requirement");
      Plan : constant String := Policy_Plan (Requirement, Additional (Data, Typed, L));
      Checks : R.Check_Array (1 .. E.Count (V.Count (V.Field (Plan, "required"))));
      Completion : R.Required_Check;
      Context_Binding : T.Attempt_Binding;
      Before, After : T.Span;
      Has_Final : constant Boolean := V.Text (V.Field (Payload, "id")) = "evaluation-complete"
        and then V.Text (V.Field (Payload, "origin")) = "engine"
        and then V.Kind (Observed) = V.Object_Value;
   begin
      Classification := (W.E.Incomplete_Unknown, W.E.No_Outcome, False);
      -- Original bytes_value validates the complete canonical Terminal codec
      -- even for an ERROR prefix; valid scalar contexts remain admitted.
      declare
         Raw : constant E.Bytes := Stored_Encoding (Data, Field (Data, Capture, "context", L), L);
         Root : constant E.Span := (Raw'First, Raw'Length);
      begin
         if not Terminal_Value_Valid (Raw, Root)
           or else Terminal_Encoding (Raw, Root, E.Terminal) /= Raw_String (Raw)
         then Valid := False; return; end if;
      end;
      if not Has_Final then
         if Saved_Capture.State = T.E.Completed then Valid := False; end if;
         return;
      end if;
      if not Context_Valid (V.Field (Observed, "returnedContext"),
          Scalar (Data, Field (Data, Field (Data, Capture, "bound", L), "subject", L), L))
        or else V.Kind (Initial) /= V.Object_Value
        or else V.Kind (V.Field (Observed, "postMeasurement")) /= V.Object_Value
        or else V.Text (V.Field (V.Field (Observed, "returnedContext"), "requirementHash")) /=
          Scalar (Data, Field (Data, Field (Data, Capture, "bound", L), "requirement", L), L)
      then Valid := False; return; end if;
      if V.Kind (V.Field (Initial, "evaluationEpoch")) /= V.Integer_Value
        or else V.Decimal (Initial, V.Field (Initial, V.Parse (Initial), "evaluationEpoch"))'Length = 0
        or else V.Decimal (Initial, V.Field (Initial, V.Parse (Initial), "evaluationEpoch")) (1) = '-'
        or else V.Kind (V.Field (Initial, "storeId")) /= V.String_Value
        or else V.Kind (V.Field (Initial, "run")) /= V.String_Value
        or else V.Kind (V.Field (V.Field (Initial, "measurement"), "worldInstance")) /= V.String_Value
        or else V.Kind (V.Field (V.Field (Initial, "measurement"), "contentId")) /= V.String_Value
        or else V.Kind (V.Field (V.Field (Initial, "measurement"), "observedContentRoot")) /= V.String_Value
        or else V.Kind (V.Field (V.Field (Observed, "postMeasurement"), "observedContentRoot")) /= V.String_Value
      then Valid := False; return; end if;
      declare
         Store, Subject_Id, Content, Run, Epoch, Requirement_Id : T.Span;
         Epoch_Bytes : constant E.Bytes := Measured_Epoch
           (Data, Field (Data, Child (Data, Typed, Rows'Length - 1, L), "payload", L), L);
         Epoch_Text : String (1 .. Epoch_Bytes'Length);
      begin
         for I in Epoch_Bytes'Range loop Epoch_Text (Integer (I - Epoch_Bytes'First) + 1) := Character'Val (Epoch_Bytes (I)); end loop;
         Append (Arena, Position, V.Text (V.Field (Initial, "storeId")), Store, Valid);
         Append (Arena, Position, V.Text (V.Field (V.Field (Initial, "measurement"), "worldInstance")), Subject_Id, Valid);
         Append (Arena, Position, V.Text (V.Field (V.Field (Initial, "measurement"), "contentId")), Content, Valid);
         Append (Arena, Position, V.Text (V.Field (Initial, "run")), Run, Valid);
         Append (Arena, Position, Epoch_Text, Epoch, Valid);
         Append (Arena, Position, V.Text (V.Field (Requirement, "requirementHash")), Requirement_Id, Valid);
         Context_Binding := (T.Store_Identity (Store), T.Subject_Identity (Subject_Id),
           T.Content_Identity (Content), T.Run_Identity (Run), T.Epoch (Epoch),
           (True, T.R.Requirement_Id (Requirement_Id)));
         Append (Arena, Position, V.Text (V.Field (V.Field (Initial, "measurement"), "observedContentRoot")), Before, Valid);
         Append (Arena, Position, V.Text (V.Field (V.Field (Observed, "postMeasurement"), "observedContentRoot")), After, Valid);
      end;
      Plan_Checks (Plan, Arena, Position, Checks, Completion, Valid);
      if not Valid then return; end if;
      Classification := R.Classify (Arena, Saved_Capture.Binding, Rows, Checks, Roster_Policy (Plan),
        (Context_Binding, T.Captured_Bytes (Before), T.Captured_Bytes (After)), Completion);
   end Classify_Terminal;
   function Carried_State (Data : E.Bytes; Item : E.Span;
                           L : E.Layer := E.Recovery) return T.E.Execution_State is
   begin
      for S in T.E.Execution_State loop
         if Text_Is (Data, Field (Data, Item, "state", L), State_Name (S), L)
         then return S; end if;
      end loop;
      return T.E.Incomplete_Unknown;
   end Carried_State;
   procedure Read_Hash (Data : E.Bytes; Item : E.Span; Result : out Worldline.Hash;
                        Valid : in out Boolean; L : E.Layer := E.Recovery) is
      Raw : constant E.Bytes := Stored_Encoding (Data, Item, L);
   begin
      Result := Worldline.Zero_Hash;
      if Raw'Length /= Result'Length then Valid := False; return; end if;
      for I in Result'Range loop Result (I) := Raw (Raw'First + E.Count (I - Result'First)); end loop;
   end Read_Hash;
   --  Python constructor, including the module where names are shared.
   function Material_Record_Is (Data : E.Bytes; Item : E.Span;
      Module_Name, Record_Name : String; L : E.Layer) return Boolean is
      N : constant E.View := E.Decode (Data, Item, L);
   begin
      return N.Form = E.Record_Value
        and then E.Bytes_Valid (Data, N.Module_Name)
        and then E.Bytes_Valid (Data, N.Record_Name)
        and then Raw_String (E.Materialize (Data, N.Module_Name)) = Module_Name
        and then Raw_String (E.Materialize (Data, N.Record_Name)) = Record_Name;
   end Material_Record_Is;

   function Material_Cursor_Shape (Data : E.Bytes; Item : E.Span;
      L : E.Layer) return Boolean is
   begin
      return Is_Null (Data, Item, L) or else
        (E.Decode (Data, Item, L).Form = E.Tuple_Value
         and then Count (Data, Item, L) = 2
         and then E.Decode (Data, Child (Data, Item, 0, L), L).Form = E.Bytes_Value
         and then E.Decode (Data, Child (Data, Item, 1, L), L).Form = E.Bytes_Value);
   end Material_Cursor_Shape;

   --  Python's producer gate compares the five retained byte fields exactly,
   --  before the native epoch-aware binding relation is consulted.
   function Material_Identity_Matches (Data : E.Bytes; Left, Right : E.Span;
      L : E.Layer) return Boolean is
   begin
      return Same (Data, Field (Data, Left, "subject", L), Field (Data, Right, "subject", L), L)
        and then Same (Data, Field (Data, Left, "content", L), Field (Data, Right, "content", L), L)
        and then Same (Data, Field (Data, Left, "requirement", L), Field (Data, Right, "requirement", L), L)
        and then Same (Data, Field (Data, Left, "run", L), Field (Data, Right, "run", L), L)
        and then Same (Data, Field (Data, Left, "epoch", L), Field (Data, Right, "epoch", L), L);
   end Material_Identity_Matches;

   function Material_Stream_Domain (Data : E.Bytes; Streams, Material_Rows : E.Span;
      L : E.Layer) return Boolean is
      N : constant E.View := E.Decode (Data, Streams, L);
   begin
      if N.Form /= E.Object_Value then return False; end if;
      --  Every stored key must name a retained run. A null VALUE is still a
      --  present key and remains distinct from an absent invocation stream.
      for I in E.Count range 0 .. E.Array_Length (Data, N.Children) - 1 loop
         declare
            Pair : constant E.Span := E.Array_Element (Data, N.Children, I);
            Key : constant E.Span := Child (Data, Pair, 0, E.Finalization);
            Found : Boolean := False;
         begin
            if E.Decode (Data, Key, L).Form /= E.Bytes_Value then return False; end if;
            for J in E.Count range 0 .. Count (Data, Material_Rows, L) - 1 loop
               declare Row : constant E.Span := Child (Data, Material_Rows, J, L); begin
                  if not Is_Null (Data, Child (Data, Row, 1, L), L)
                    and then Same (Data, Key,
                      Field (Data, Child (Data, Row, 0, L), "run", L), L)
                  then Found := True; exit; end if;
               end;
            end loop;
            if not Found then return False; end if;
         end;
      end loop;
      --  And every retained run must have a key, even when its value is null.
      for I in E.Count range 0 .. Count (Data, Material_Rows, L) - 1 loop
         declare
            Row : constant E.Span := Child (Data, Material_Rows, I, L);
            Run : constant E.Span := Field (Data, Child (Data, Row, 0, L), "run", L);
            Found : Boolean := False;
         begin
            if not Is_Null (Data, Child (Data, Row, 1, L), L) then
               for J in E.Count range 0 .. E.Array_Length (Data, N.Children) - 1 loop
                  declare Pair : constant E.Span := E.Array_Element (Data, N.Children, J); begin
                     if Same (Data, Run, Child (Data, Pair, 0, E.Finalization), L)
                     then Found := True; exit; end if;
                  end;
               end loop;
               if not Found then return False; end if;
            end if;
         end;
      end loop;
      return True;
   end Material_Stream_Domain;

   function Material_Promotion_Matches (Data : E.Bytes; Item : E.Span;
      Promotion : Boolean; L : E.Layer) return Boolean is
      --  This is the unchanged finalization.encode(archive(atom(bool)))
      --  grammar, shared by Recovery and Operation for Boolean atoms. Use
      --  the one typed equality engine: original dataclass equality admits
      --  0/1 integers and finite 0.0/1.0 as equal to Boolean fields.
      Expected : constant E.Bytes := Bytes (Lifted ("list",
        "[""array"",[" & Lifted ("scalar", String_Encoding ("atom")) & "," &
        Lifted ("scalar", "[""bool""," & (if Promotion then "true" else "false") & "]") & "]]"));
   begin
      return (if L = E.Recovery then
        RA.Equal (Data, Expected, Item, (Expected'First, Expected'Length))
        else RA.Equal_Operation (Data, Expected, Item, (Expected'First, Expected'Length)));
   end Material_Promotion_Matches;
   procedure Read_Start (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Position : in out E.Count; Plans : out R.Check_Array;
      Start : out FZ.Start_Record; Valid : in out Boolean;
      L : E.Layer := E.Recovery) is
      pragma Unreferenced (Position);
      Store, Subject, Run, Epoch, Policy, Verifiers, Context : T.Span;
      Req : T.Optional_Requirement;
      Parent, Config, Repository : Worldline.Hash;
      Required : constant E.Span := Field (Data, Item, "required", L);
      Declaration : R.Declaration := R.Old.Missing_Declaration;
   begin
      if not Material_Record_Is (Data, Item, "worldline.finalization_values", "StartValue", L)
        or else E.Decode (Data, Required, L).Form /= E.Tuple_Value
        or else Plans'Length /= Count (Data, Required, L)
      then Valid := False; end if;
      Put (Data, Field (Data, Item, "store_id", L), Arena, Store, Valid, L);
      Put (Data, Field (Data, Item, "subject", L), Arena, Subject, Valid, L);
      Put (Data, Field (Data, Item, "run", L), Arena, Run, Valid, L);
      Put (Data, Field (Data, Item, "epoch", L), Arena, Epoch, Valid, L);
      Put (Data, Field (Data, Item, "policy", L), Arena, Policy, Valid, L);
      Put (Data, Field (Data, Item, "verifier_plan", L), Arena, Verifiers, Valid, L);
      Put (Data, Field (Data, Item, "base_context", L), Arena, Context, Valid, L);
      Read_Requirement (Data, Field (Data, Item, "requirement", L), Arena, Valid, Req, L);
      Read_Hash (Data, Field (Data, Item, "parent", L), Parent, Valid, L);
      Read_Hash (Data, Field (Data, Item, "config", L), Config, Valid, L);
      Read_Hash (Data, Field (Data, Item, "repository", L), Repository, Valid, L);
      --  FZ.Start_Valid treats policy/verifiers/base_context as opaque retained
      --  bytes. Native requirements are the actual retained byte pairs, not a
      --  second policy projection. This preserves opaque unsealed starts and
      --  independently uses exactly the original native plan at seal time.
      for I in Plans'Range loop
         declare
            Pair : constant E.Span := Child (Data, Required, I - Plans'First, L);
            Name, Declared : T.Span;
         begin
            if E.Decode (Data, Pair, L).Form /= E.Tuple_Value or else Count (Data, Pair, L) /= 2
            then Valid := False; end if;
            Put (Data, Child (Data, Pair, 0, L), Arena, Name, Valid, L);
            Put (Data, Child (Data, Pair, 1, L), Arena, Declared, Valid, L);
            Plans (I) := (T.Check_Identity (Name), T.Captured_Bytes (Declared));
         end;
      end loop;
      if Text_Is (Data, Field (Data, Item, "declaration", L), "Required_Checks", L) then
         Declaration := R.Old.Required_Checks;
      elsif Text_Is (Data, Field (Data, Item, "declaration", L), "Explicit_Empty", L) then
         Declaration := R.Old.Explicit_Empty;
      elsif not Text_Is (Data, Field (Data, Item, "declaration", L), "Missing_Declaration", L) then
         Valid := False;
      end if;
      Start := (T.Store_Identity (Store), T.Subject_Identity (Subject), T.Run_Identity (Run), T.Epoch (Epoch),
        Req, T.Captured_Bytes (Policy), T.Captured_Bytes (Verifiers), T.Captured_Bytes (Context),
        Parent, Config, Repository, (1, Plans'Length), Declaration);
      if FZ.Record_Start (Arena, Start, Plans, (Present => False)).Decision /= FZ.Insert
      then Valid := False; end if;
   end Read_Start;
   function Tree_Equal (Left_Data : E.Bytes; Left : E.Span; LL : E.Layer;
      Right_Data : E.Bytes; Right : E.Span; RL : E.Layer) return Boolean;
   function Event_Start (Data : E.Bytes; Events : E.Span; Invocation : String;
      Before : E.Count; L : E.Layer) return E.Span is
   begin
      for I in E.Count range 0 .. Before - 1 loop
         declare Event : constant E.Span := Child (Data, Events, I, L); begin
            if Text_Is (Data, Field (Data, Event, "phase", L), "invocation-start", L)
              and then Scalar (Data, Field (Data, Event, "invocation", L), L) = Invocation
            then return Field (Data, Event, "payload", L); end if;
         end;
      end loop;
      return Empty;
   end Event_Start;
   procedure Classify_Finalization (Data : E.Bytes; Found, World : E.Span;
      Arena : in out E.Bytes; Position : in out E.Count; Finalization : out H.Optional_Record;
      Current : out T.Cursor; Valid : in out Boolean;
      Promotion : out Boolean; L : E.Layer := E.Recovery;
      Facts_Data : E.Bytes; Capsules : E.Span) is
      Start_Item : constant E.Span := Child (Data, Found, 0, L);
      Sealed : constant E.Span := Child (Data, Found, 1, L);
      Events : constant E.Span := Child (Data, Found, 2, L);
      Value : constant E.Span := Field (Data, Sealed, "value", L);
      Capture : constant E.Span := Field (Data, Value, "capture", L);
      Typed : constant E.Span := Field (Data, Capture, "results", L);
      Plans : R.Check_Array (1 .. Count (Data, Field (Data, Start_Item, "required", L), L));
      Start : FZ.Start_Record;
      Input : FZ.Input_Record;
      Rows : FZ.Start_Rows (1 .. Count (Data, Typed, L));
      Content, Post_Root, Post_Manifests, Context, Source, Evidence, Environment : T.Span;
      Completion : R.Required_Check;
      Components : FZ.Final_Components;
      Result : FZ.Seal_Result;
      Header : E.Span := Empty;
      Headers, Starts, Returns, Result_Events : E.Count := 0;
   begin
      Finalization := (Present => False); Current := (Present => False); Promotion := False;
      if Is_Null (Data, Found, L) then return; end if;
      if E.Decode (Data, Found, L).Form /= E.Tuple_Value or else Count (Data, Found, L) /= 3
        or else E.Decode (Data, Events, L).Form /= E.Tuple_Value
      then Valid := False; return; end if;
      Read_Start (Data, Start_Item, Arena, Position, Plans, Start, Valid, L);
      if Scalar (Data, Field (Data, Start_Item, "subject", L), L) /=
        Scalar (Data, Field (Data, World, "instance_id", L), L) then Valid := False; end if;
      Current := (True, Start.Run, Start.Sequence);
      if Is_Null (Data, Sealed, L) then return; end if;
      if not Material_Record_Is (Data, Sealed, "worldline.finalization_values", "SealedValue", L)
        or else not Material_Record_Is (Data, Value, "worldline.finalization_values", "SealValue", L)
        or else not Material_Record_Is (Data, Capture, "worldline.finalization_values", "CaptureValue", L)
        or else not Material_Record_Is (Data, Field (Data, Capture, "input", L),
          "worldline.finalization_values", "InputValue", L)
        or else not Material_Record_Is (Data, Field (Data, Value, "components", L),
          "worldline.finalization_values", "ComponentsValue", L)
        or else E.Decode (Data, Typed, L).Form /= E.Tuple_Value
      then Valid := False; return; end if;
      --  Replay every result event as the original record_bytes(UnsealedResult),
      --  independently of raw-row verdict or eventual head selection. The four
      --  source phases retain their original path; truly ignored phases remain
      --  untouched. Unsealed starts above do not interpret ANY event payload.
      for I in E.Count range 0 .. Count (Data, Events, L) - 1 loop
         declare Event : constant E.Span := Child (Data, Events, I, L);
            Phase : constant E.Span := Field (Data, Event, "phase", L);
         begin
            if E.Decode (Data, Event, L).Form /= E.Object_Value or else Phase.Length = 0
            then Valid := False; return; end if;
            if Text_Is (Data, Phase, "result", L) then
               if Result_Events >= Rows'Length
                 or else E.Decode (Data, Field (Data, Event, "payload", L), L).Form /= E.Bytes_Value
               then Valid := False; return; end if;
               declare
                  Raw : constant E.Bytes := Stored_Encoding (Data, Field (Data, Event, "payload", L), L);
                  Root : constant E.Span := (Raw'First, Raw'Length);
               begin
                  if not RA.Valid_Finalization_Record (Raw, Root)
                    or else not Record_Is (Raw, Root, "UnsealedResult", E.Finalization_Record)
                    or else not RA.Equal_Finalization_Record (Raw, Data, Root,
                      Child (Data, Typed, Result_Events, L), L)
                  then Valid := False; return; end if;
               end;
               Result_Events := Result_Events + 1;
            elsif Text_Is (Data, Phase, "input-header", L) or else
              Text_Is (Data, Phase, "invocation-start", L) or else
              Text_Is (Data, Phase, "invocation-return", L) or else
              Text_Is (Data, Phase, "raw-acquisition", L)
            then
               declare
                  Raw : constant E.Bytes := Stored_Encoding (Data, Field (Data, Event, "payload", L), L);
                  Root : constant E.Span := (Raw'First, Raw'Length);
                  Id : constant String := Scalar (Data, Field (Data, Event, "invocation", L), L);
                  Prior : constant E.Span := Event_Start (Data, Events, Id, I, L);
               begin
                  if E.Decode (Raw, Root, E.Finalization).Form = E.Invalid or else
                    E.Decode (Data, Field (Data, Event, "invocation", L), L).Form /= E.Bytes_Value
                  then Valid := False; return; end if;
                  if Text_Is (Data, Phase, "input-header", L) then
                     Headers := Headers + 1; Header := Field (Data, Event, "payload", L);
                  elsif Text_Is (Data, Phase, "invocation-start", L) then
                     if Prior.Length /= 0 then Valid := False; end if;
                     Starts := Starts + 1;
                  elsif Text_Is (Data, Phase, "invocation-return", L) then
                     if Prior.Length = 0 then Valid := False;
                     else
                        declare Started : constant E.Bytes := Stored_Encoding (Data, Prior, L); begin
                           if not Tree_Equal (Started, (Started'First, Started'Length), E.Finalization,
                             Raw, Field (Raw, Root, "started", E.Finalization), E.Finalization)
                           then Valid := False; end if;
                        end;
                     end if;
                     for J in E.Count range 0 .. I - 1 loop
                        declare Earlier : constant E.Span := Child (Data, Events, J, L); begin
                           if Text_Is (Data, Field (Data, Earlier, "phase", L), "invocation-return", L)
                             and then Scalar (Data, Field (Data, Earlier, "invocation", L), L) = Id
                           then Valid := False; end if;
                        end;
                     end loop;
                     Returns := Returns + 1;
                  elsif Field (Raw, Root, "kind", E.Finalization).Length = 0 or else
                    Field (Raw, Root, "observation", E.Finalization).Length = 0
                  then Valid := False; end if;
               end;
            end if;
         end;
      end loop;
      if Result_Events /= Rows'Length or else Headers /= 1 or else Starts /= Returns
      then Valid := False; end if;
      if not Same (Data, Field (Data, Capture, "start", L), Start_Item, L)
        or else not Same (Data, Field (Data, Field (Data, Capture, "input", L), "start", L), Start_Item, L)
      then Valid := False; end if;
      declare I : constant E.Span := Field (Data, Capture, "input", L);
         Root, Manifests : T.Span;
         Filesystem, Config, Repository : Worldline.Hash;
      begin
         Put (Data, Field (Data, I, "root", L), Arena, Root, Valid, L);
         Put (Data, Field (Data, I, "manifests", L), Arena, Manifests, Valid, L);
         Read_Hash (Data, Field (Data, I, "filesystem", L), Filesystem, Valid, L);
         Read_Hash (Data, Field (Data, I, "config", L), Config, Valid, L);
         Read_Hash (Data, Field (Data, I, "repository", L), Repository, Valid, L);
         Input := (Start, T.Captured_Bytes (Root), T.Captured_Bytes (Manifests), Filesystem, Config, Repository);
         if FZ.Record_Input (Arena, Start, Input, Plans, (Present => False)).Decision /= FZ.Insert then Valid := False; end if;
      end;
      Put (Data, Field (Data, Value, "content", L), Arena, Content, Valid, L);
      Put (Data, Field (Data, Capture, "post_root", L), Arena, Post_Root, Valid, L);
      Put (Data, Field (Data, Capture, "post_manifests", L), Arena, Post_Manifests, Valid, L);
      Put (Data, Field (Data, Capture, "context", L), Arena, Context, Valid, L);
      Put (Data, Field (Data, Capture, "source", L), Arena, Source, Valid, L);
      Put (Data, Field (Data, Value, "evidence", L), Arena, Evidence, Valid, L);
      Put (Data, Field (Data, Value, "environment", L), Arena, Environment, Valid, L);
      Read_Hash (Data, Field (Data, Field (Data, Value, "components", L), "environment", L), Components.Environment, Valid, L);
      Read_Hash (Data, Field (Data, Field (Data, Value, "components", L), "evidence", L), Components.Evidence, Valid, L);
      declare
         Pair : constant E.Span := Field (Data, Capture, "completion", L);
         Name, Declared : T.Span;
      begin
         if E.Decode (Data, Pair, L).Form /= E.Tuple_Value or else Count (Data, Pair, L) /= 2
         then Valid := False; end if;
         Put (Data, Child (Data, Pair, 0, L), Arena, Name, Valid, L);
         Put (Data, Child (Data, Pair, 1, L), Arena, Declared, Valid, L);
         Completion := (T.Check_Identity (Name), T.Captured_Bytes (Declared));
      end;
      for I in Rows'Range loop
         declare Measured : R.Measured_Result;
            Item : constant E.Span := Child (Data, Typed, I - 1, L);
            Payload : constant String := Stored_JSON (Data, Field (Data, Item, "payload", L), L);
            Invocation : constant String := V.Text (V.Field (V.Field (Payload, "engineInvocationObservation"), "invocationId"));
            Started : constant E.Span := Event_Start (Data, Events, Invocation, Count (Data, Events, L), L);
         begin
            if not Material_Record_Is (Data, Item, "worldline.finalization_values", "UnsealedResult", L)
              or else not Material_Record_Is (Data, Field (Data, Item, "wire", L),
                "worldline.evaluation_wire", "OwnedRecord", L)
              or else not Same (Data, Field (Data, Item, "start", L), Start_Item, L)
            then Valid := False; end if;
            Read_Result (Data, Item, Field (Data, Capture, "source", L), Empty,
              Arena, Valid, Measured, L, True,
              FZ.Bound_To (Start, T.Content_Identity (Content)), Facts_Data, Capsules);
            Rows (I) := (Start, Measured.Item.Check, Measured.Item.Source,
              Measured.Item.Execution, Measured.Item.Verifier,
              Carried_State (Data, Item, L), Outcome (Data, Field (Data, Item, "outcome", L), L),
              Measured.Item.Payload, Measured.Declared, Measured.Raw, Measured.Confinement);
         end;
      end loop;
      declare
         Returned : constant String := Stored_JSON (Data, Field (Data, Capture, "context", L), L);
         Last_Row : constant E.Span := (if Rows'Length = 0 then Empty else Child (Data, Typed, Rows'Length - 1, L));
         Last_Payload : constant E.Bytes := Stored_Encoding (Data, Field (Data, Last_Row, "payload", L), L);
         Last_Tree : constant E.Span := (Last_Payload'First, Last_Payload'Length);
         Observed : constant E.Span := Field (Last_Payload, Last_Tree, "captureObservation", E.Terminal);
         Header_Bytes : constant E.Bytes := Stored_Encoding (Data, Header, L);
      begin
         if not Context_Valid (Returned, Scalar (Data, Field (Data, World, "instance_id", L), L))
           or else Get (Returned, "requirementHash") /=
             (if Is_Null (Data, Field (Data, Start_Item, "requirement", L), L) then "null"
              else V.Quote (Scalar (Data, Field (Data, Start_Item, "requirement", L), L)))
         then Valid := False; end if;
         if Text_Is (Data, Field (Data, Sealed, "finalization_state", L), "COMPLETED", L) then
            if not Text_Is (Last_Payload, Field (Last_Payload, Last_Tree, "id", E.Terminal), "evaluation-complete", E.Terminal)
              or else E.Decode (Last_Payload, Observed, E.Terminal).Form /= E.Object_Value
              or else not Tree_Equal (Header_Bytes, (Header_Bytes'First, Header_Bytes'Length), E.Finalization,
                Last_Payload, Field (Last_Payload, Observed, "captureContext", E.Terminal), E.Terminal)
              or else Terminal_Encoding (Last_Payload, Field (Last_Payload, Observed, "returnedContext", E.Terminal), E.Terminal) /=
                Raw_String (Stored_Encoding (Data, Field (Data, Capture, "context", L), L))
            then Valid := False; end if;
         end if;
      end;
      Result := FZ.Seal (Arena, Start, Input, T.Captured_Bytes (Post_Root),
        T.Captured_Bytes (Post_Manifests), Rows, Plans, Completion, T.Content_Identity (Content), Components,
        (T.Captured_Bytes (Context), T.Captured_Bytes (Source), T.Captured_Bytes (Evidence), T.Captured_Bytes (Environment)));
      if Result.Reason /= FZ.Seal_Observed then Valid := False; return; end if;
      Finalization := Result.Finalization; Promotion := Result.Classification.Promotion_Ready;
      declare Identity : Worldline.Hash; begin
         Read_Hash (Data, Field (Data, Sealed, "identity", L), Identity, Valid, L);
         if Identity /= Result.Identity then Valid := False; end if;
      end;
      declare C : constant E.Span := Field (Data, Sealed, "classification", L); begin
         if not Material_Record_Is (Data, C, "worldline.finalization_values", "ClassifiedValue", L)
           or else not Outcome_Valid (Data, Field (Data, C, "outcome", L), L)
           or else not Outcome_Valid (Data, Field (Data, Sealed, "finalization_outcome", L), L)
           or else not Text_Is (Data, Field (Data, C, "state", L),
           (if Result.Classification.State = W.E.Completed then "Completed" else "Incomplete_Unknown"), L)
           or else Outcome (Data, Field (Data, C, "outcome", L), L) /=
             T.E.Outcome'Val (W.E.Outcome'Pos (Result.Classification.Outcome))
           or else not Material_Promotion_Matches (Data, Field (Data, C, "promotion", L), Promotion, L)
           or else not Text_Is (Data, Field (Data, Sealed, "finalization_state", L),
             (if Finalization.Value.State = H.Completed then "COMPLETED" else "ERROR"), L)
           or else Outcome (Data, Field (Data, Sealed, "finalization_outcome", L), L) /=
             T.E.Outcome'Val (W.E.Outcome'Pos (Result.Classification.Outcome))
         then Valid := False; end if;
      end;
   end Classify_Finalization;
   type Boolean_Array is array (E.Count range <>) of Boolean;
   function Row_Count (Data : E.Bytes; Material : E.Span;
                       At_Layer : E.Layer := E.Recovery) return E.Count is
     (Count (Data, Child (Data, Field (Data, Material, "terminal", At_Layer), 2, At_Layer), At_Layer));
   procedure Collect (Data : E.Bytes; Material, World, Requirement : E.Span;
      Arena : in out E.Bytes; Rows : out H.History;
      Finalization : out H.Optional_Record; Current : out H.Optional_Cursor;
      Valid : out Boolean; Promotions : out Boolean_Array;
      Final_Promotion : out Boolean; L : E.Layer := E.Recovery;
      Facts_Data : E.Bytes; Capsules : E.Span) is
      Terminal_Material : constant E.Span := Field (Data, Material, "terminal", L);
      Intents : constant E.Span := Child (Data, Terminal_Material, 0, L);
      Material_Rows : constant E.Span := Child (Data, Terminal_Material, 2, L);
      Streams : constant E.Span := Child (Data, Terminal_Material, 3, L);
      Pending : constant E.Span := Field (Data, Material, "pending_store", L);
      Journal : T.R.Journal (1 .. Count (Data, Intents, L)) with Relaxed_Initialization;
      Stored_Rows : H.History (Rows'Range);
      TC, FC : T.Cursor;
      Retained_Count : E.Count := 0;
      Position : E.Count := (if Data'Last = E.Count'Last then Data'Last else Data'Last + 1);
      Needed : constant E.Count := Arena_Length (Data, Material, L);
   begin
      Valid := Needed > 0 and then Arena'First = Data'First and then Arena'Length >= Needed
        and then Rows'Length = Row_Count (Data, Material, L)
        and then Material_Record_Is (Data, Material, "worldline.evaluation_authority", "AuthorityMaterial", L)
        and then E.Decode (Data, Terminal_Material, L).Form = E.Tuple_Value
        and then Count (Data, Terminal_Material, L) = 4
        and then E.Decode (Data, Intents, L).Form = E.Tuple_Value
        and then E.Decode (Data, Material_Rows, L).Form = E.Tuple_Value
        and then E.Decode (Data, Streams, L).Form = E.Object_Value
        and then Material_Cursor_Shape (Data, Child (Data, Terminal_Material, 1, L), L)
        and then Journal'Length = Rows'Length
        and then (Journal'Length = 0 or else E.Decode (Data, Pending, L).Form = E.Bytes_Value)
        and then (if L = E.Recovery then RA.Valid (Data, Material) else OA.Valid (Data, Material));
      Finalization := (Present => False); Current := (Present => False);
      Promotions := (others => False); Final_Promotion := False;
      Rows := (others => ((Present => False), (Present => False), (Present => False),
        (Present => False), (Present => False), H.Pending, H.No_Verdict));
      if not Valid then return; end if;
      Read_Cursor (Data, Child (Data, Terminal_Material, 1, L), Arena, Valid, TC, L);
      --  Count only to determine whether the original native producer is
      --  invoked. Stream domain equality below is a key relation, not a count.
      for I in Rows'Range loop
         declare Row : constant E.Span := Child (Data, Material_Rows, I - Rows'First, L); begin
            if E.Decode (Data, Row, L).Form /= E.Tuple_Value or else Count (Data, Row, L) /= 2
              or else not Material_Record_Is (Data, Child (Data, Row, 0, L),
                "worldline.completion_kernel", "HistoryValue", L)
            then Valid := False; return; end if;
            if not Is_Null (Data, Child (Data, Row, 1, L), L) then
               Retained_Count := Retained_Count + 1;
            end if;
         end;
      end loop;
      for I in Journal'Range loop
         declare
            Intent : constant E.Span := Child (Data, Intents, I - Journal'First, L);
            Row : constant E.Span := Child (Data, Material_Rows, I - Journal'First, L);
            Summary : constant E.Span := Child (Data, Row, 0, L);
         begin
            if not Material_Record_Is (Data, Intent, "worldline.pending_kernel_v2", "Intent", L)
              or else E.Decode (Data, Field (Data, Intent, "linked", L), L).Form /= E.Boolean_Value
              or else not E.Decode (Data, Field (Data, Intent, "linked", L), L).Boolean_Bit
              or else not Same (Data, Field (Data, Intent, "store_id", L), Pending, L)
              or else not Material_Identity_Matches (Data, Summary, Intent, L)
            then Valid := False; return; end if;
            Read_Summary (Data, Summary, Arena, Valid, Stored_Rows (I), L);
            if Is_Null (Data, Child (Data, Row, 1, L), L) then
               if Stored_Rows (I).State /= H.Pending or else Stored_Rows (I).Outcome /= H.No_Verdict
               then Valid := False; return; end if;
               Rows (I) := Stored_Rows (I);
            end if;
            --  The original producer calls Completion.Decide only when there
            --  is a retained capture. A wholly pending journal does not acquire
            --  a new native journal/head predicate through this replay reader.
            if Retained_Count > 0 then
               declare
                  B : T.Attempt_Binding;
                  Previous : T.Cursor;
                  Prior : constant E.Span := Field (Data, Intent, "previous", L);
                  Epoch, Run : T.Span;
               begin
                  Read_Binding (Data, Intent, Arena, Valid, B, L);
                  if Is_Null (Data, Prior, L) then Previous := (Present => False);
                  else
                     --  Original CompletionKernel.cursor indexes the first two
                     --  values; unlike actual_current it has no exact tuple/length
                     --  gate. Preserve that constructor domain here.
                     if E.Decode (Data, Prior, L).Form not in E.Tuple_Value | E.List_Value
                       or else Count (Data, Prior, L) < 2
                     then Valid := False; return; end if;
                     Put (Data, Child (Data, Prior, 0, L), Arena, Epoch, Valid, L);
                     Put (Data, Child (Data, Prior, 1, L), Arena, Run, Valid, L);
                     Previous := (True, T.Run_Identity (Run), T.Epoch (Epoch));
                  end if;
                  Journal (I) := (Base => (Store_Id => T.Span (B.Store), Subject => T.Span (B.Subject),
                    Content => T.Span (B.Content), Run => T.Span (B.Run), Sequence => T.Span (B.Sequence),
                    Previous => (if Previous.Present then
                      (True, T.Span (Previous.Sequence), T.Span (Previous.Run)) else (Present => False)),
                    State => T.P.Linked), Requirement => B.Requirement);
               end;
            end if;
         end;
         pragma Loop_Invariant (if Retained_Count > 0 then
           (for all K in Journal'First .. I => Journal (K)'Initialized));
      end loop;
      if not Valid or else not Material_Stream_Domain (Data, Streams, Material_Rows, L)
      then Valid := False; return; end if;
      if Retained_Count > 0 then
         pragma Assert (Journal'Initialized);
         for I in Rows'Range loop
            declare
               Row : constant E.Span := Child (Data, Material_Rows, I - Rows'First, L);
               Summary : constant E.Span := Child (Data, Row, 0, L);
               Retained : constant E.Span := Child (Data, Row, 1, L);
            begin
               if not Is_Null (Data, Retained, L) then
                  if E.Decode (Data, Retained, L).Form /= E.Tuple_Value
                    or else Count (Data, Retained, L) /= 3
                    or else not Same (Data, Child (Data, Retained, 0, L), Summary, L)
                  then Valid := False; return; end if;
                  declare
                     Capture : constant E.Span := Child (Data, Retained, 1, L);
                     Typed : constant E.Span := Child (Data, Retained, 2, L);
                     Stream : constant E.Span := Stream_For (Data, Streams, Field (Data, Summary, "run", L), L);
                     Measured : R.Measured_Array (1 .. Count (Data, Typed, L));
                     Saved_Results : T.Result_Array (Measured'Range);
                     Invocations : constant E.Span := Child (Data, Child (Data, Stream, 0, L), 1, L);
                     Captured : T.Terminal_Record;
                     Classified : R.Classification;
                     Decision : T.Decision;
                     Selected : E.Count;
                  begin
                     if not Material_Record_Is (Data, Capture, "worldline.completion_kernel", "CaptureValue", L)
                       or else E.Decode (Data, Typed, L).Form /= E.Tuple_Value
                       or else not State_Valid (Data, Capture, L)
                       or else Carried_State (Data, Capture, L) not in T.E.Terminal_State
                       or else not Material_Identity_Matches (Data, Summary, Field (Data, Capture, "bound", L), L)
                       or else not Text_Is (Data, Field (Data, Summary, "state", L),
                         (if Text_Is (Data, Field (Data, Capture, "state", L), "Completed", L)
                          then "COMPLETED" else "ERROR"), L)
                       or else not Same (Data, Field (Data, Summary, "outcome", L), Field (Data, Capture, "outcome", L), L)
                     then Valid := False; return; end if;
                     Read_Terminal (Data, Capture, Arena, Valid, Captured, L);
                     for J in Measured'Range loop
                        declare Item : constant E.Span := Child (Data, Typed, J - Measured'First, L); begin
                           if not Material_Record_Is (Data, Item, "worldline.completion_kernel", "CheckValue", L)
                           then Valid := False; return; end if;
                           Read_Result (Data, Item, Field (Data, Capture, "source", L),
                             Child (Data, Invocations, J - Measured'First, L), Arena, Valid, Measured (J), L,
                             Facts_Data => Facts_Data, Capsules => Capsules);
                           Saved_Results (J) := (Measured (J).Item with delta
                             State => Carried_State (Data, Item, L),
                             Outcome => Outcome (Data, Field (Data, Item, "outcome", L), L));
                        end;
                     end loop;
                     if not Valid then return; end if;
                     Decision := T.History_Update_Check (Arena, Journal, Stored_Rows, Captured.Binding.Run,
                       (True, Captured), T.Decide (Arena, Journal, TC, Captured, Saved_Results,
                                                  (True, Captured), Saved_Results));
                     Selected := T.Find_Run (Arena, Journal, Captured.Binding.Run);
                     if Decision not in T.Retain_Terminal | T.Already_Retained
                       or else Selected not in Journal'Range
                       or else not T.P.Same (Arena, Journal (Selected).Base.Run,
                         T.Span (Captured.Binding.Run))
                       or else not T.Retained_Summary_Matches (Arena, Stored_Rows (I), (True, Captured))
                     then Valid := False; return; end if;
                     Classify_Terminal (Data, Capture, Typed, Stream, Arena, Position, Valid,
                       Classified, Captured, Measured, L);
                     Rows (I) := (Stored_Rows (I) with delta
                       State => (if Classified.State = W.E.Completed then H.Completed else H.Error),
                       Outcome => (if Classified.Outcome = W.E.Passed then H.Passed
                         elsif Classified.Outcome = W.E.Failed then H.Failed else H.No_Verdict));
                     Promotions (I) := Classified.Promotion_Ready;
                  end;
               end if;
            end;
         end loop;
      end if;
      Classify_Finalization (Data, Field (Data, Material, "finalization", L), World,
        Arena, Position, Finalization, FC, Valid, Final_Promotion, L, Facts_Data, Capsules);
      Current := History_Cursor (if TC.Present then TC else FC);
   end Collect;
   procedure Classify_All
     (Data : E.Bytes; Material, World, Requirement : E.Span;
      Arena : in out E.Bytes; Rows : out H.History;
      Finalization : out H.Optional_Record; Current : out H.Optional_Cursor;
      Valid : out Boolean; At_Layer : E.Layer := E.Recovery;
      Facts_Data : E.Bytes; Capsules : E.Span) is
      Promotions : Boolean_Array (Rows'Range);
      Final_Promotion : Boolean;
   begin
      Collect (Data, Material, World, Requirement, Arena, Rows, Finalization, Current,
        Valid, Promotions, Final_Promotion, At_Layer, Facts_Data, Capsules);
   end Classify_All;
   function Tree_Equal (Left_Data : E.Bytes; Left : E.Span; LL : E.Layer;
                        Right_Data : E.Bytes; Right : E.Span; RL : E.Layer) return Boolean is
      L : constant E.View := E.Decode (Left_Data, Left, LL);
      Rv : constant E.View := E.Decode (Right_Data, Right, RL);
      function Pair_Key (Data : E.Bytes; Pair : E.Span; Layer : E.Layer) return String is
      begin
         if Layer = E.Terminal then
            declare Enc : constant E.Span := E.Array_Element (Data, Pair, 0); begin
               if Enc.Length < 2 then return ""; end if;
               return Raw_String (E.Materialize (Data, ((Enc.First + 1, Enc.Length - 2), 1)));
            end;
         elsif Layer = E.Finalization then return Scalar (Data, Child (Data, Pair, 0, E.Terminal), E.Terminal);
         else return Scalar (Data, Child (Data, Pair, 0, E.Finalization), Layer); end if;
      end Pair_Key;
      function Pair_Value (Data : E.Bytes; Pair : E.Span; Layer : E.Layer) return E.Span is
      begin
         if Layer = E.Terminal then
            return E.Array_Element (Data, Pair, 1);
         else
            return Child (Data, Pair, 1, (if Layer = E.Finalization then E.Terminal else E.Finalization));
         end if;
      end Pair_Value;
   begin
      if L.Form = E.Invalid or else L.Form /= Rv.Form then return False; end if;
      case L.Form is
         when E.Null_Value => return True;
         when E.Boolean_Value => return L.Boolean_Bit = Rv.Boolean_Bit;
         when E.Integer_Value | E.Float_Value | E.Text_Value | E.Bytes_Value | E.World_State_Value =>
            return L.Sign = Rv.Sign and then E.Bytes_Valid (Left_Data, L.Payload)
              and then E.Bytes_Valid (Right_Data, Rv.Payload)
              and then E.Materialize (Left_Data, L.Payload) = E.Materialize (Right_Data, Rv.Payload);
         when E.List_Value | E.Tuple_Value | E.Object_Value =>
            if E.Array_Length (Left_Data, L.Children) /= E.Array_Length (Right_Data, Rv.Children) then return False; end if;
            for I in E.Count range 0 .. E.Array_Length (Left_Data, L.Children) - 1 loop
               declare
                  LC : constant E.Span := E.Array_Element (Left_Data, L.Children, I);
                  RC : constant E.Span := E.Array_Element (Right_Data, Rv.Children, I);
               begin
                  if L.Form = E.Object_Value then
                     if Pair_Key (Left_Data, LC, LL) /= Pair_Key (Right_Data, RC, RL)
                       or else not Tree_Equal (Left_Data, Pair_Value (Left_Data, LC, LL), LL,
                                              Right_Data, Pair_Value (Right_Data, RC, RL), RL) then return False; end if;
                  elsif not Tree_Equal (Left_Data, LC, LL, Right_Data, RC, RL) then return False; end if;
               end;
            end loop;
            return True;
         when E.Record_Value =>
            return LL = RL and then Left_Data'First = Right_Data'First and then
              Left_Data'Last = Right_Data'Last and then Same (Left_Data, Left, Right, LL);
         when others => return False;
      end case;
   end Tree_Equal;
   function Stored_Matches (Data : E.Bytes; Saved, Stored : E.Span;
                            L : E.Layer := E.Recovery) return Boolean is
      Raw : constant E.Bytes := Stored_Encoding (Data, Stored, L);
   begin return Tree_Equal (Data, Saved, L, Raw, (Raw'First, Raw'Length), E.Terminal); end Stored_Matches;
   function Terminal_Field (Raw : E.Bytes; Item : E.Span; Name : String) return E.Span is
     (Field (Raw, Item, Name, E.Terminal));
   function Final_Stream_Matches (Data : E.Bytes; Stream, Found, Observed : E.Span;
                                  L : E.Layer := E.Recovery) return Boolean is
      Events : constant E.Span := Child (Data, Found, 2, L);
      Header : constant E.Span := Child (Data, Child (Data, Stream, 0, L), 0, L);
      Invocations : constant E.Span := Child (Data, Child (Data, Stream, 0, L), 1, L);
      Acquired : constant E.Span := Child (Data, Stream, 1, L);
      Headers, Starts, Returns, Acquisitions_Count : E.Count := 0;
   begin
      if Count (Data, Stream, L) /= 2 or else Count (Data, Child (Data, Stream, 0, L), L) /= 2 then return False; end if;
      for I in E.Count range 0 .. Count (Data, Events, L) - 1 loop
         declare
            Event : constant E.Span := Child (Data, Events, I, L);
            Phase : constant String := Scalar (Data, Field (Data, Event, "phase", L), L);
            Raw : constant E.Bytes := Stored_Encoding (Data, Field (Data, Event, "payload", L), L);
            Root : constant E.Span := (Raw'First, Raw'Length);
            Invocation : constant String := Scalar (Data, Field (Data, Event, "invocation", L), L);
         begin
            if Phase = "input-header" then
               Headers := Headers + 1;
               if not Tree_Equal (Data, Header, L, Raw, Root, E.Finalization) then return False; end if;
            elsif Phase = "invocation-start" then
               if Starts >= Count (Data, Invocations, L) then return False; end if;
               declare Saved : constant E.Span := Child (Data, Invocations, Starts, L); begin
                  if Count (Data, Saved, L) /= 3 or else Scalar (Data, Child (Data, Saved, 0, L), L) /= Invocation
                    or else not Tree_Equal (Data, Child (Data, Saved, 1, L), L, Raw, Root, E.Finalization)
                  then return False; end if;
                  for J in E.Count range 0 .. Starts - 1 loop
                     if Scalar (Data, Child (Data, Child (Data, Invocations, J, L), 0, L), L) = Invocation then return False; end if;
                  end loop;
               end;
               Starts := Starts + 1;
            elsif Phase = "invocation-return" then
               declare Found_Start : Boolean := False; begin
                  for J in E.Count range 0 .. Starts - 1 loop
                     declare Saved : constant E.Span := Child (Data, Invocations, J, L); begin
                        if Scalar (Data, Child (Data, Saved, 0, L), L) = Invocation then
                           if not Tree_Equal (Data, Child (Data, Saved, 2, L), L, Raw, Root, E.Finalization)
                             or else not Tree_Equal (Data, Child (Data, Saved, 1, L), L, Raw,
                               Field (Raw, Root, "started", E.Finalization), E.Finalization)
                           then return False; end if;
                           Found_Start := True;
                        end if;
                     end;
                  end loop;
                  if not Found_Start then return False; end if;
               end;
               -- A second return with the same identity was originally refused.
               for J in E.Count range 0 .. I - 1 loop
                  declare Prior : constant E.Span := Child (Data, Events, J, L); begin
                     if Text_Is (Data, Field (Data, Prior, "phase", L), "invocation-return", L)
                       and then Scalar (Data, Field (Data, Prior, "invocation", L), L) = Invocation then return False; end if;
                  end;
               end loop;
               Returns := Returns + 1;
            elsif Phase = "raw-acquisition" then
               if Acquisitions_Count >= Count (Data, Acquired, L) then return False; end if;
               declare Saved : constant E.Span := Child (Data, Acquired, Acquisitions_Count, L); begin
                  if Count (Data, Saved, L) /= 4 or else Scalar (Data, Child (Data, Saved, 0, L), L) /= Invocation
                    or else not Tree_Equal (Data, Child (Data, Saved, 1, L), L, Raw,
                      Field (Raw, Root, "kind", E.Finalization), E.Finalization)
                    or else not Tree_Equal (Data, Child (Data, Saved, 3, L), L, Raw,
                      Field (Raw, Root, "observation", E.Finalization), E.Finalization)
                  then return False; end if;
                  declare Occ : constant E.Span := Field (Raw, Root, "occurrence", E.Finalization); begin
                     if Occ.Length = 0 then
                        if not Is_Null (Data, Child (Data, Saved, 2, L), L) then return False; end if;
                     elsif not Tree_Equal (Data, Child (Data, Saved, 2, L), L, Raw, Occ, E.Finalization) then return False; end if;
                  end;
               end;
               Acquisitions_Count := Acquisitions_Count + 1;
            end if;
         end;
      end loop;
      return Headers = 1 and then Starts = Returns
        and then Starts = Count (Data, Invocations, L)
        and then Acquisitions_Count = Count (Data, Acquired, L);
   end Final_Stream_Matches;
   --  Cursor decoding mutates the caller's arena even when a later match fails.
   --  Keep that effect explicit instead of hiding it in a SPARK function.
   procedure Selected_Matches (Data : E.Bytes; Saved, Material : E.Span;
      Reference : H.Record_Reference; Current : H.Optional_Cursor; Arena : in out E.Bytes;
      Promotion : Boolean; Result : out Replay_Result; Owner_Retry : Boolean := False)
     with Global => null, Always_Terminates,
       Depends => (Arena => (Arena, Data, Saved, Material, Reference, Current),
                   Result => (Data, Saved, Material, Reference, Current, Arena,
                              Promotion, Owner_Retry))
   is
      Terminal_Material : constant E.Span := Field (Data, Material, "terminal");
      Material_Rows : constant E.Span := Child (Data, Terminal_Material, 2);
      Found : constant E.Span := Field (Data, Material, "finalization");
      Capture, Typed, Stream : E.Span;
      Finalization : constant Boolean := Reference.Kind = H.Finalization;
   begin
      Result := (Reference => Reference, Promotion => Promotion, others => <>);
      if not Current.Present or else Reference.Kind = H.Absent then return; end if;
      if E.Decode (Data, Saved, E.Recovery).Form /= E.Object_Value
        or else Count (Data, Saved) /= 9 or else not RA.Valid (Data, Saved) then return; end if;
      if Finalization then
         Capture := Field (Data, Field (Data, Child (Data, Found, 1), "value"), "capture");
         Typed := Field (Data, Capture, "results");
         Stream := Field (Data, Saved, "retainedStream");
      else
         if Reference.Index = 0 or else Reference.Index > Count (Data, Material_Rows) then return; end if;
         declare Retained : constant E.Span := Child (Data, Child (Data, Material_Rows, Reference.Index - 1), 1); begin
            if Is_Null (Data, Retained) then return; end if;
            Capture := Child (Data, Retained, 1); Typed := Child (Data, Retained, 2);
            Stream := Stream_For (Data, Child (Data, Terminal_Material, 3),
              Field (Data, Child (Data, Child (Data, Material_Rows, Reference.Index - 1), 0), "run"));
         end;
      end if;
      Result.Capture := Capture; Result.Typed_Rows := Typed; Result.Retained_Stream := Stream;
      Result.Context := Field (Data, Saved, "context"); Result.Observed := Field (Data, Saved, "observed");
      if not Same (Data, Field (Data, Saved, "authorityMaterial"), Material)
        or else not Same (Data, Field (Data, Saved, "capture"), Capture)
        or else not Same (Data, Field (Data, Saved, "typedRows"), Typed)
        or else Count (Data, Field (Data, Saved, "results")) /= Count (Data, Typed)
      then return; end if;
      declare
         Cursor_Item : constant E.Span := Field (Data, Saved, "cursor");
         C : T.Cursor;
         Valid : Boolean := True;
      begin
         Read_Cursor (Data, Cursor_Item, Arena, Valid, C, E.Recovery, True);
         if not Valid or else not C.Present
           or else not H.Same_Epoch (Arena, Current.Value.Sequence.Value,
                H.Epoch_Id'(C.Sequence.First, C.Sequence.Length))
           or else not H.Same_Identity (Arena, H.Identity_Span (Current.Value.Run),
                (C.Run.First, C.Run.Length)) then return; end if;
      end;
      for I in E.Count range 0 .. Count (Data, Typed) - 1 loop
         if not Stored_Matches (Data, Child (Data, Field (Data, Saved, "results"), I),
           Field (Data, Child (Data, Typed, I), "payload")) then return; end if;
      end loop;
      if Count (Data, Typed) = 0 then return; end if;
      declare
         Payload : constant E.Bytes := Stored_Encoding (Data,
           Field (Data, Child (Data, Typed, Count (Data, Typed) - 1), "payload"));
         Root : constant E.Span := (Payload'First, Payload'Length);
         Observed : constant E.Span := Field (Payload, Root, "captureObservation", E.Terminal);
         Returned : constant E.Span := Field (Payload, Observed, "returnedContext", E.Terminal);
         Initial : constant E.Span := Field (Payload, Observed, "captureContext", E.Terminal);
         Run : constant String := (if Finalization then Scalar (Data, Field (Data, Child (Data, Found, 0), "run"))
           else Scalar (Data, Field (Data, Field (Data, Capture, "bound"), "run")));
         Source : constant String := (if Owner_Retry then "owner-retry:" & Run
           elsif Finalization then "finalization" else "revalidation:" & Run);
      begin
         if E.Decode (Payload, Observed, E.Terminal).Form /= E.Object_Value
           or else not Tree_Equal (Data, Result.Observed, E.Recovery, Payload, Observed, E.Terminal)
           or else not Tree_Equal (Data, Result.Context, E.Recovery, Payload, Returned, E.Terminal)
           or else not Text_Is (Data, Field (Data, Saved, "source"), Source)
         then return; end if;
         if Finalization then
            if not Stored_Matches (Data, Result.Context, Field (Data, Capture, "context"))
              or else not Tree_Equal (Data, Child (Data, Child (Data, Stream, 0), 0), E.Recovery,
                 Payload, Initial, E.Terminal)
              or else not Final_Stream_Matches (Data, Stream, Found, Result.Observed) then return; end if;
         elsif not Same (Data, Field (Data, Saved, "retainedStream"), Stream) then return; end if;
      end;
      Result.Valid := True;
   end Selected_Matches;
   function Rebuild
     (Data : E.Bytes; Saved, Subject, Current_Requirement, Prepared : E.Span;
      Facts_Data : E.Bytes; Capsules : E.Span)
      return Replay_Result is
      Material : constant E.Span := Field (Data, Saved, "authorityMaterial");
      Arena : E.Bytes (Data'First .. Arena_Last (Data, Material)) := (others => 0);
      Rows : H.History (1 .. Row_Count (Data, Material));
      Promotions : Boolean_Array (Rows'Range);
      Finalization : H.Optional_Record;
      Current : H.Optional_Cursor;
      Prior : T.Cursor;
      Subject_Id, Content_Id, Requirement : T.Span;
      Query : H.Query;
      Selection : H.Selection;
      Valid, Final_Promotion : Boolean;
      Result : Replay_Result;
   begin
      Collect (Data, Material, Subject, Current_Requirement, Arena, Rows, Finalization,
        Current, Valid, Promotions, Final_Promotion, Facts_Data => Facts_Data, Capsules => Capsules);
      Put (Data, Field (Data, Subject, "instance_id"), Arena, Subject_Id, Valid, Expected_Form => E.Text_Value);
      Put (Data, Field (Data, Subject, "content_id"), Arena, Content_Id, Valid, Expected_Form => E.Text_Value);
      Put (Data, Current_Requirement, Arena, Requirement, Valid, Expected_Form => E.Text_Value);
      Read_Cursor (Data, Prepared, Arena, Valid, Prior, E.Recovery, True);
      Query := ((True, H.Subject_Id'(Subject_Id.First, Subject_Id.Length)),
        (True, H.Content_Id'(Content_Id.First, Content_Id.Length)),
        (True, H.Requirement_Id'(Requirement.First, Requirement.Length)),
        Current, History_Cursor (Prior));
      if not Valid then return (others => <>); end if;
      Selection := H.Select_Evidence (Arena, Rows, Finalization, Query);
      if Selection.Reason /= H.Ready then return (others => <>); end if;
      Selected_Matches (Data, Saved, Material, Selection.Head, Current, Arena,
        (if Selection.Head.Kind = H.Finalization then Final_Promotion
         elsif Selection.Head.Kind = H.History_Entry then Promotions (Selection.Head.Index) else False),
        Result);
      return Result;
   end Rebuild;
   function Owner_Promotion
     (Data : E.Bytes; Owner : E.Span; Facts_Data : E.Bytes;
      Capsules : E.Span) return Boolean is
      Material : constant E.Span := Field (Data, Owner, "after_material");
      Arena : E.Bytes (Data'First .. Arena_Last (Data, Material)) := (others => 0);
      Rows : H.History (1 .. Row_Count (Data, Material));
      Promotions : Boolean_Array (Rows'Range);
      Finalization : H.Optional_Record; Current : H.Optional_Cursor;
      Valid, Final_Promotion : Boolean;
   begin
      Collect (Data, Material, Field (Data, Owner, "world"), Field (Data, Owner, "requirement"),
        Arena, Rows, Finalization, Current, Valid, Promotions, Final_Promotion, Facts_Data => Facts_Data, Capsules => Capsules);
      return Valid and then Rows'Length > 0 and then Promotions (Rows'Last);
   end Owner_Promotion;
   function Owner_Selected
     (Data : E.Bytes; Saved, Owner : E.Span; Facts_Data : E.Bytes;
      Capsules : E.Span) return Replay_Result is
      Material : constant E.Span := Field (Data, Owner, "after_material");
      Arena : E.Bytes (Data'First .. Arena_Last (Data, Material)) := (others => 0);
      Rows : H.History (1 .. Row_Count (Data, Material));
      Promotions : Boolean_Array (Rows'Range);
      Finalization : H.Optional_Record; Current : H.Optional_Cursor;
      Valid, Final_Promotion : Boolean;
      Result : Replay_Result;
   begin
      Collect (Data, Material, Field (Data, Owner, "world"), Field (Data, Owner, "requirement"),
        Arena, Rows, Finalization, Current, Valid, Promotions, Final_Promotion, Facts_Data => Facts_Data, Capsules => Capsules);
      if not Valid or else Rows'Length = 0 then return (others => <>); end if;
      Selected_Matches (Data, Saved, Material, (H.History_Entry, Rows'Last),
        Current, Arena, Promotions (Rows'Last), Result, True);
      return Result;
   end Owner_Selected;
   function Agent_Record_JSON (Value : String) return String is
      Root : constant V.Node := V.Parse (Value);
      Legacy : constant Boolean := Root.Form = V.Object_Value
        and then V.Text (V.Field (Value, "id")) = "agent"
        and then V.Kind (V.Field (Value, "origin")) = V.Missing
        and then V.Text (V.Field (Value, "kind")) = "build"
        and then V.Text (V.Field (Value, "format")) = "exit"
        and then V.Kind (V.Field (Value, "resultChannel")) = V.Missing
        and then V.Kind (V.Field (Value, "executedVerifierSet")) = V.Missing
        and then V.Kind (V.Field (Value, "supervision")) = V.Object_Value
        and then V.Kind (V.Field (Value, "rawEventHash")) /= V.Missing;
   begin
      if not Legacy then return Value; end if;
      return Value (Value'First .. Value'Last - 1) & ",""origin"":""agent""}";
   end Agent_Record_JSON;
   function Find_Agent (Data : E.Bytes; Subject : E.Span) return E.Span is
      Checks : constant E.Span := Field (Data, Field (Data, Subject, "evidence"), "checks");
   begin
      for I in E.Count range 0 .. Count (Data, Checks) - 1 loop
         declare Item : constant E.Span := Child (Data, Checks, I); begin
            if Text_Is (Data, Field (Data, Item, "id"), "agent") then return Item; end if;
         end;
      end loop;
      return Empty;
   end Find_Agent;
   function Owned_Matches (Data : E.Bytes; Owned : E.Span;
                           Produced : EP.Produced_Record;
                           L : E.Layer := E.Recovery) return Boolean is
      N : constant E.View := E.Decode (Data, Owned, L);
      Confinement : constant String := JSON (Data, Field (Data, Owned, "confinement", L), L);
   begin
      return Record_Is (Data, Owned, "OwnedRecord", L)
        and then E.Bytes_Valid (Data, N.Module_Name)
        and then Raw_String (E.Materialize (Data, N.Module_Name)) = "worldline.evaluation_wire"
        and then Raw_Equal (Data, Owned, Produced.Raw, L)
        and then Confinement = Ada.Strings.Fixed.Trim
          (Natural'Image (Worldline.Evaluation_Report_Facts.Confinement_Observation'Pos (Produced.Confinement)), Ada.Strings.Both);
   end Owned_Matches;
   function Agent_Matches
     (Data : E.Bytes; Subject, Agent, Agent_Record : E.Span; Required : Boolean;
      Facts_Data : E.Bytes; Capsules : E.Span)
      return Boolean is
      Original : constant E.Span := Find_Agent (Data, Subject);
      Payload : constant String := (if Original.Length = 0 then "null" else Agent_Record_JSON (JSON (Data, Original, E.Recovery, True, True)));
      Actual : constant String := JSON (Data, Agent_Record, E.Recovery, True, True);
      Present : constant Boolean := V.Kind (Payload) = V.Object_Value and then V.Text (V.Field (Payload, "origin")) = "agent";
   begin
      if not Required then return Is_Null (Data, Agent) and then Is_Null (Data, Agent_Record); end if;
      if not Present then return Is_Null (Data, Agent)
        and then (if Original.Length = 0 then Is_Null (Data, Agent_Record)
                  else Same (Data, Original, Agent_Record)); end if;
      if not V.Equal (Payload, Actual) then return False; end if;
      -- Exact mapped record order/field count remains the original archive
      -- correspondence, including the legacy appended origin field.
      if JSON (Data, Original, E.Recovery, True, True) = Payload then
         if not Same (Data, Original, Agent_Record) then return False; end if;
      elsif Count (Data, Agent_Record) /= Count (Data, Original) + 1 then return False;
      else
         declare N : constant E.View := E.Decode (Data, Original, E.Recovery); begin
            for I in E.Count range 0 .. E.Array_Length (Data, N.Children) - 1 loop
               declare Pair : constant E.Span := E.Array_Element (Data, N.Children, I);
                  Saved : constant E.View := E.Decode (Data, Agent_Record, E.Recovery);
                  Saved_Pair : constant E.Span := E.Array_Element (Data, Saved.Children, I);
               begin
                  if not Same (Data, Child (Data, Pair, 0, E.Finalization),
                               Child (Data, Saved_Pair, 0, E.Finalization))
                    or else not Same (Data, Child (Data, Pair, 1, E.Finalization),
                                      Child (Data, Saved_Pair, 1, E.Finalization))
                  then return False; end if;
               end;
            end loop;
         end;
         declare
            Saved : constant E.View := E.Decode (Data, Agent_Record, E.Recovery);
            Last : constant E.Span := E.Array_Element (Data, Saved.Children, Count (Data, Original));
         begin
            if not Text_Is (Data, Child (Data, Last, 0, E.Finalization), "origin")
              or else not Text_Is (Data, Child (Data, Last, 1, E.Finalization), "agent")
            then return False; end if;
         end;
      end if;
      return Owned_Matches (Data, Agent,
        Derive_Original (Payload, Engine_Declaration (True), Facts_Data, Capsules));
   end Agent_Matches;
   function Agent_Admitted (Data : E.Bytes; Agent : E.Span) return Boolean is
      Raw : W.Raw_Record := W.Zero_Record;
      Enc : constant E.Bytes := Stored_Encoding (Data, Field (Data, Agent, "raw"));
      C : constant String := JSON (Data, Field (Data, Agent, "confinement"));
      Confinement : W.Byte;
   begin
      if Enc'Length /= 34 then return False; end if;
      for K in W.Observation_Field loop Raw.Observations (K) := Enc (Enc'First + W.Observation_Field'Pos (K)); end loop;
      Raw.Report_Based := Enc (Enc'First + 14);
      for K in W.R.Fact_Index loop Raw.Report_Facts (K) := Enc (Enc'First + 15 + E.Count (W.R.Fact_Index'Pos (K))); end loop;
      for K in W.Presence_Field loop Raw.Presence (K) := Enc (Enc'First + 29 + W.Presence_Field'Pos (K)); end loop;
      if C = "0" then Confinement := 0; elsif C = "1" then Confinement := 1; elsif C = "2" then Confinement := 2; else return False; end if;
      return W.Confined_Admit_Wire (Raw, Confinement) = 1;
   end Agent_Admitted;
   function Content_Root (Manifests : String) return String is
      M : constant V.Node := V.Parse (Manifests);
      function Entries (Rows : String; I : Natural) return String is
         function Project (Row : String; K : Positive; First : Boolean) return String is
            function Name (J : Positive) return String is
              (case J is when 1 => "acls", when 2 => "contentHash", when 3 => "mode",
               when 4 => "pathB64", when 5 => "size", when 6 => "targetB64",
               when 7 => "type", when others => "xattrs");
         begin
            if K > 8 then return ""; end if;
            if V.Kind (V.Field (Row, Name (K))) = V.Missing then return Project (Row, K + 1, First); end if;
            return (if First then "" else ",") & V.Quote (Name (K)) & ":" &
              Canonical_JSON (V.Field (Row, Name (K))) & Project (Row, K + 1, False);
         end Project;
      begin
         if I = V.Count (Rows) then return ""; end if;
         return (if I = 0 then "" else ",") & "{" & Project (V.Element (Rows, I), 1, True) & "}" & Entries (Rows, I + 1);
      end Entries;
      function Roots (I : Positive) return String is
      begin
         if I > V.Count (Manifests, M) then return ""; end if;
         declare Name : constant String := V.Member_Name (Manifests, M, I);
            Manifest : constant String := V.Field (Manifests, Name);
         begin
            return (if I = 1 then "" else ",") & V.Quote (Name) & ":[" &
              Entries (V.Field (Manifest, "entries"), 0) & "]" & Roots (I + 1);
         end;
      end Roots;
   begin
      if M.Form /= V.Object_Value then return ""; end if;
      return Hash_Id ("worldline-content-root-set-v2" & Canonical_JSON ("{" & Roots (1) & "}"));
   end Content_Root;
   function Hex_Bytes (Value : String; Default_Zero : Boolean := True) return String is
      Start : Natural := (if Value'Length >= 7 and then Value (Value'First .. Value'First + 6) = "sha256:" then 7 else 0);
      function Digit (C : Character) return Integer is
        (if C in '0' .. '9' then Character'Pos (C) - Character'Pos ('0')
         elsif C in 'a' .. 'f' then 10 + Character'Pos (C) - Character'Pos ('a')
         elsif C in 'A' .. 'F' then 10 + Character'Pos (C) - Character'Pos ('A') else -1);
      function Part (I : Natural) return String is
         J : Natural := I;
      begin
         while J < Value'Length and then Value (Value'First + J) in ' ' | Character'Val (9) | Character'Val (10) |
           Character'Val (11) | Character'Val (12) | Character'Val (13) loop J := J + 1; end loop;
         if J = Value'Length then return ""; end if;
         if J + 1 >= Value'Length or else Digit (Value (Value'First + J)) < 0
           or else Digit (Value (Value'First + J + 1)) < 0 then return ""; end if;
         return Character'Val (16 * Digit (Value (Value'First + J)) + Digit (Value (Value'First + J + 1))) & Part (J + 2);
      end Part;
   begin
      if Value'Length = 0 and then Default_Zero then return String'(1 .. 32 => Character'Val (0)); end if;
      return Part (Start);
   end Hex_Bytes;
   function Triples (Entries : String; Check : String := ""; Filter : Boolean := False;
                     Normalize : Boolean := True) return String is
      N : constant Natural := V.Count (Entries);
      type Order_Array is array (Natural range <>) of Natural;
      Order : Order_Array (0 .. N - 1);
      function Included (I : Natural) return Boolean is
        (not Filter or else V.Python_String (Get (V.Element (Entries, I), "checkId")) = Check);
      function Component (I : Natural; Name : String) return String is
        (V.Python_String (Get (V.Element (Entries, I), Name)));
      function Less (I, J : Natural) return Boolean is
        (Component (I, "rootKey") < Component (J, "rootKey") or else
         (Component (I, "rootKey") = Component (J, "rootKey") and then
          (Component (I, "path") < Component (J, "path") or else
           (Component (I, "path") = Component (J, "path") and then Component (I, "sha256") < Component (J, "sha256")))));
      function Part (I : Natural; First : Boolean) return String is
      begin
         if I = N then return ""; end if;
         if not Included (Order (I)) then return Part (I + 1, First); end if;
         declare Content : constant String := Component (Order (I), "sha256");
            Raw : constant String := Hex_Bytes (Content, False);
            Hex_Digits : constant String := "0123456789abcdef";
            Hexed : String (1 .. Raw'Length * 2);
         begin
            for K in Raw'Range loop
               Hexed (1 + (K - Raw'First) * 2) := Hex_Digits (1 + Character'Pos (Raw (K)) / 16);
               Hexed (2 + (K - Raw'First) * 2) := Hex_Digits (1 + Character'Pos (Raw (K)) mod 16);
            end loop;
            return (if First then "" else ",") & "[" & V.Quote (Component (Order (I), "rootKey")) & "," &
              V.Quote (Component (Order (I), "path")) & "," & V.Quote
                (if Normalize then (if Content'Length = 0 then "" else "sha256:" & Hexed) else Content) & "]" & Part (I + 1, False);
         end;
      end Part;
   begin
      for I in Order'Range loop Order (I) := I; end loop;
      for I in Order'Range loop
         for J in Order'Range loop
            if J > I and then Less (Order (J), Order (I)) then
               declare Temp : constant Natural := Order (I); begin Order (I) := Order (J); Order (J) := Temp; end;
            end if;
         end loop;
      end loop;
      return "[" & Part (0, True) & "]";
   end Triples;
   function Bundle (Triples_Value : String) return String is
      N : constant Natural := V.Count (Triples_Value);
      type Order_Array is array (Natural range <>) of Natural;
      Order : Order_Array (0 .. N - 1);
      function Component (I, K : Natural) return String is
        (V.Text (V.Element (V.Element (Triples_Value, I), K)));
      function Less (I, J : Natural) return Boolean is
        (Component (I, 0) < Component (J, 0) or else
         (Component (I, 0) = Component (J, 0) and then
          (Component (I, 1) < Component (J, 1) or else
           (Component (I, 1) = Component (J, 1) and then
            Component (I, 2) < Component (J, 2)))));
      function Parts (I : Natural) return String is
      begin
         if I = N then return ""; end if;
         return Component (Order (I), 0) & Character'Val (0) &
           Component (Order (I), 1) & Character'Val (0) &
           Hex_Bytes (Component (Order (I), 2)) & Character'Val (0) & Parts (I + 1);
      end Parts;
   begin
      for I in Order'Range loop Order (I) := I; end loop;
      for I in Order'Range loop
         for J in Order'Range loop
            if J > I and then Less (Order (J), Order (I)) then
               declare Saved : constant Natural := Order (I); begin
                  Order (I) := Order (J); Order (J) := Saved;
               end;
            end if;
         end loop;
      end loop;
      return Hash_Id ("worldline-execution-verifier-set-v1" & Character'Val (0) & Parts (0));
   end Bundle;
   function FS_Path (Raw : E.Bytes) return String is
      package TX renames Worldline.Archive_Text;
      Hex_Digits : constant String := "0123456789abcdef";
      function Part (I : E.Count) return String is
         Width : E.Count;
      begin
         if I = Raw'Length then return ""; end if;
         Width := TX.Unit_Width (Raw, (Raw'First, Raw'Length), I);
         if Width > 0 and then TX.Value_At (Raw, (Raw'First, Raw'Length), I) in 16#D800# .. 16#DFFF# then Width := 0; end if;
         if Width = 0 then
            return "\udc" & Hex_Digits (1 + Natural (Raw (Raw'First + I)) / 16) &
              Hex_Digits (1 + Natural (Raw (Raw'First + I)) mod 16) & Part (I + 1);
         end if;
         declare Text : constant String := V.Quote (Raw_String (Raw (Raw'First + I .. Raw'First + I + Width - 1))); begin
            return Text (Text'First + 1 .. Text'Last - 1) & Part (I + Width);
         end;
      end Part;
   begin return '"' & Part (0) & '"'; end FS_Path;
   function Roots_JSON (Data : E.Bytes; Roots : E.Span; Identity : Boolean) return String is
      N : constant E.Count := Count (Data, Roots);
      type Order_Array is array (E.Count range <>) of E.Count;
      Order : Order_Array (0 .. N - 1);
      function Name (I : E.Count) return String is (Scalar (Data, Field (Data, Child (Data, Roots, I), "root_key")));
      function Parts (I : E.Count) return String is
      begin
         if I = N then return ""; end if;
         declare Row : constant E.Span := Child (Data, Roots, Order (I));
            Raw : constant E.Bytes := Stored_Encoding (Data, Field (Data, Row, "path"));
         begin
            return (if I = 0 then "" else ",") & "{""kind"":" & JSON (Data, Field (Data, Row, "kind")) &
              (if Identity then ",""pathB64"":" & V.Quote (Base64 (Raw))
               else ",""path"":" & FS_Path (Raw)) & ",""rootKey"":" & V.Quote (Name (Order (I))) & "}" & Parts (I + 1);
         end;
      end Parts;
   begin
      for I in Order'Range loop Order (I) := I; end loop;
      for I in Order'Range loop for J in Order'Range loop
         if J > I and then Name (Order (J)) < Name (Order (I)) then
            declare Temp : constant E.Count := Order (I); begin Order (I) := Order (J); Order (J) := Temp; end;
         end if;
      end loop; end loop;
      return "[" & Parts (0) & "]";
   end Roots_JSON;
   function Manifests_Match (Data : E.Bytes; Stored, Manifests : E.Span) return Boolean is
      Raw : constant E.Bytes := Stored_Encoding (Data, Stored);
      Root : constant E.Span := (Raw'First, Raw'Length);
      Acquired : constant E.View := E.Decode (Data, Manifests, E.Recovery);
   begin
      if E.Decode (Raw, Root, E.Finalization).Form /= E.Tuple_Value
        or else Acquired.Form /= E.Object_Value
        or else Count (Raw, Root, E.Finalization) /=
          E.Array_Length (Data, Acquired.Children) then return False; end if;
      for I in E.Count range 0 .. Count (Raw, Root, E.Finalization) - 1 loop
         declare Pair : constant E.Span := Child (Raw, Root, I, E.Finalization);
            Member : constant E.Span := E.Array_Element (Data, Acquired.Children, I);
            Actual_Key : constant E.Span := Child (Data, Member, 0, E.Finalization);
            Actual_Value : constant E.Span := Child (Data, Member, 1, E.Finalization);
            Key : constant String := Scalar (Raw, Child (Raw, Pair, 0, E.Finalization), E.Finalization);
            Manifest : constant String := Scalar (Raw, Child (Raw, Pair, 1, E.Finalization), E.Finalization);
         begin
            if Key /= Scalar (Data, Actual_Key, E.Recovery)
              or else Manifest /= Canonical_JSON (JSON (Data, Actual_Value)) then return False; end if;
         end;
      end loop;
      return True;
   end Manifests_Match;
   function Full_Stream (Data : E.Bytes; Saved : E.Span) return Boolean is
      Stream : constant E.Span := Field (Data, Saved, "retainedStream");
      Invocations : constant E.Span := Child (Data, Child (Data, Stream, 0), 1);
      Acquired : constant E.Span := Child (Data, Stream, 1);
      Rows : constant E.Span := Field (Data, Saved, "results");
      Cursor_Run : constant String := Scalar (Data, Field (Data, Field (Data, Saved, "cursor"), "run"));
      Projected_Count : E.Count := 0;
      function Row_Acquisitions (Row : E.Span) return String is
        (Acquisitions (Get (JSON (Data, Row, E.Recovery, True, True), "engineRawObservations")));
   begin
      if Count (Data, Stream) /= 2 or else Count (Data, Child (Data, Stream, 0)) /= 2 then return False; end if;
      for I in E.Count range 0 .. Count (Data, Rows) - 1 loop
         declare
            Row : constant E.Span := Child (Data, Rows, I);
            Start : constant E.Span := Field (Data, Row, "engineInvocationObservation");
            Returned : constant E.Span := Field (Data, Row, "rawRunnerResult");
            Acquisitions_Value : constant String := Row_Acquisitions (Row);
         begin
            if I < Count (Data, Invocations) then
               declare
                  Expected : constant E.Span := Child (Data, Invocations, I);
                  Expected_Start : constant E.Span := Child (Data, Expected, 1);
                  Expected_Return : constant E.Span := Child (Data, Expected, 2);
                  Id : constant String := Scalar (Data, Child (Data, Expected, 0));
                  Row_Name : constant String := V.Python_String (Get (JSON (Data, Row), "id"));
                  Acquired_Count : Natural := 0;
               begin
                  if Is_Null (Data, Expected_Return) or else Count (Data, Expected) /= 3
                    or else not Same (Data, Expected_Start, Start)
                    or else not Same (Data, Field (Data, Expected_Return, "started"), Expected_Start)
                    or else not Same (Data, Field (Data, Expected_Return, "result"), Returned)
                    or else Scalar (Data, Field (Data, Expected_Start, "evaluationRun")) /= Cursor_Run
                    or else Scalar (Data, Field (Data, Expected_Start, "checkId")) /= Row_Name
                    or else Scalar (Data, Field (Data, Expected_Start, "invocationId")) /= Id
                    or else Scalar (Data, Field (Data, Expected_Start, "worldInstance")) /= Scalar (Data, Field (Data, Start, "worldInstance"))
                    or else not Same (Data, Field (Data, Expected_Start, "candidateSnapshot"),
                       Field (Data, Field (Data, Expected_Return, "result"), "candidateSnapshot"))
                  then return False; end if;
                  for J in E.Count range 0 .. Count (Data, Acquired) - 1 loop
                     declare Event : constant E.Span := Child (Data, Acquired, J); begin
                        if Scalar (Data, Child (Data, Event, 0)) = Id then
                           declare Actual : constant String := V.Element (Acquisitions_Value, Acquired_Count);
                              Kind : constant String := JSON (Data, Child (Data, Event, 1), E.Recovery, True, True);
                              Observation : constant String := JSON (Data, Child (Data, Event, 3), E.Recovery, True, True);
                              Occurrence : constant E.Span := Child (Data, Event, 2);
                              Expected_Event : constant String := "{""kind"":" & Kind & ",""observation"":" & Observation &
                                (if Is_Null (Data, Occurrence) then "" else ",""occurrence"":" & JSON (Data, Occurrence, E.Recovery, True, True)) & "}";
                           begin
                              if not V.Equal (Expected_Event, Actual) then return False; end if;
                           end;
                           Acquired_Count := Acquired_Count + 1;
                        end if;
                     end;
                  end loop;
                  if Acquired_Count /= V.Count (Acquisitions_Value) then return False; end if;
               end;
            else
               if (Start.Length /= 0 and then not Is_Null (Data, Start))
                 or else (Returned.Length /= 0 and then not Is_Null (Data, Returned))
                 or else V.Kind (Acquisitions_Value) not in V.Null_Value | V.Missing then return False; end if;
            end if;
            if Start.Length /= 0 and then not Is_Null (Data, Start) then Projected_Count := Projected_Count + 1; end if;
         end;
      end loop;
      if Projected_Count /= Count (Data, Invocations) then return False; end if;
      for I in E.Count range 0 .. Count (Data, Acquired) - 1 loop
         declare Id : constant String := Scalar (Data, Child (Data, Child (Data, Acquired, I), 0));
            Found : Boolean := False;
         begin
            for J in E.Count range 0 .. Count (Data, Invocations) - 1 loop
               if Id = Scalar (Data, Child (Data, Child (Data, Invocations, J), 0)) then Found := True; end if;
            end loop;
            if not Found then return False; end if;
         end;
      end loop;
      return True;
   end Full_Stream;
   function Terminal_Encoding (Data : E.Bytes; Item : E.Span;
                               L : E.Layer := E.Recovery) return String is
      N : constant E.View := E.Decode (Data, Item, L);
      function Parts (I : E.Count) return String is
      begin
         if I = E.Array_Length (Data, N.Children) then return ""; end if;
         declare Child_Item : constant E.Span := E.Array_Element (Data, N.Children, I); begin
            if N.Form = E.Object_Value then
               declare
                  Key : constant E.Span := (if L = E.Terminal then E.Array_Element (Data, Child_Item, 0)
                    else Child (Data, Child_Item, 0, (if L = E.Finalization then E.Terminal else E.Finalization)));
                  Val : constant E.Span := (if L = E.Terminal then E.Array_Element (Data, Child_Item, 1)
                    else Child (Data, Child_Item, 1, (if L = E.Finalization then E.Terminal else E.Finalization)));
                  Encoded_Key : constant String := (if L = E.Terminal then Raw_String (Data (Key.First .. Key.First + Key.Length - 1))
                    else V.Quote (Base64 (E.Materialize (Data, E.Decode (Data, Key, L).Payload))));
               begin
                  return (if I = 0 then "" else ",") & "[" & Encoded_Key & "," &
                    Terminal_Encoding (Data, Val, L) & "]" & Parts (I + 1);
               end;
            end if;
            return (if I = 0 then "" else ",") & Terminal_Encoding (Data, Child_Item, L) & Parts (I + 1);
         end;
      end Parts;
   begin
      case N.Form is
         when E.Invalid => return (if Item.Length = 0 then "[""null""]" else "");
         when E.Null_Value => return "[""null""]";
         when E.Boolean_Value => return "[""bool""," & (if N.Boolean_Bit then "true" else "false") & "]";
         when E.Text_Value | E.World_State_Value => return "[""str""," & V.Quote (Base64 (E.Materialize (Data, N.Payload))) & "]";
         when E.Integer_Value => return "[""int""," & (if N.Sign then "true" else "false") & "," & V.Quote (Base64 (E.Materialize (Data, N.Payload))) & "]";
         when E.Float_Value => return "[""float""," & V.Quote (Base64 (E.Materialize (Data, N.Payload))) & "]";
         when E.List_Value | E.Tuple_Value => return "[""array"",[" & Parts (0) & "]]";
         when E.Object_Value => return "[""object"",[" & Parts (0) & "]]";
         when others => return "";
      end case;
   end Terminal_Encoding;
   function String_Encoding (Value : String) return String is
     ("[""str""," & V.Quote (Base64 (Bytes (Value))) & "]");
   function Lifted (Tag, Value : String) return String is
     ("[""array"",[" & String_Encoding (Tag) & "," & Value & "]]");
   function Lift_Encoding (Data : E.Bytes; Item : E.Span; L : E.Layer := E.Recovery) return String is
      N : constant E.View := E.Decode (Data, Item, L);
      function Parts (I : E.Count) return String is
      begin
         if I = E.Array_Length (Data, N.Children) then return ""; end if;
         declare C : constant E.Span := E.Array_Element (Data, N.Children, I); begin
            if N.Form = E.Object_Value then
               declare
                  Key : constant E.Span := (if L = E.Terminal then E.Array_Element (Data, C, 0)
                    else Child (Data, C, 0, (if L = E.Finalization then E.Terminal else E.Finalization)));
                  Value : constant E.Span := (if L = E.Terminal then E.Array_Element (Data, C, 1)
                    else Child (Data, C, 1, (if L = E.Finalization then E.Terminal else E.Finalization)));
                  Encoded_Key : constant String := (if L = E.Terminal then
                    String_Encoding (Raw_String (E.Materialize (Data, ((Key.First + 1, Key.Length - 2), 1))))
                    else Terminal_Encoding (Data, Key,
                      (if L = E.Finalization then E.Terminal else L)));
               begin
                  return (if I = 0 then "" else ",") & "[""array"",[" &
                    Encoded_Key & "," & Lift_Encoding (Data, Value, L) & "]]" & Parts (I + 1);
               end;
            end if;
            return (if I = 0 then "" else ",") & Lift_Encoding (Data, C, L) & Parts (I + 1);
         end;
      end Parts;
   begin
      case N.Form is
         when E.Bytes_Value => return Lifted ("bytes", String_Encoding (Base64 (E.Materialize (Data, N.Payload))));
         when E.List_Value | E.Tuple_Value | E.Object_Value =>
            return Lifted ((if N.Form = E.List_Value then "list" elsif N.Form = E.Tuple_Value then "tuple" else "object"),
              "[""array"",[" & Parts (0) & "]]");
         when others => return Lifted ("scalar", Terminal_Encoding (Data, Item, L));
      end case;
   end Lift_Encoding;
   function Declaration_Encoding (Value : String) return String is
      function Scalar_Tag (Name : String) return String is
         Item : constant String := Get (Value, Name);
      begin
         if V.Kind (Item) = V.Null_Value then return "[""null""]";
         elsif V.Kind (Item) = V.Boolean_Value then return "[""bool""," & Item & "]";
         elsif V.Kind (Item) = V.String_Value then return "[""str""," & V.Quote (Base64 (Bytes (V.Text (Item)))) & "]";
         else return ""; end if;
      end Scalar_Tag;
      function Pair (Name : String) return String is
        ("[" & V.Quote (Base64 (Bytes (Name))) & "," & Scalar_Tag (Name) & "]");
   begin
      if V.Kind (Value) = V.Null_Value then return "[""null""]"; end if;
      return "[""object"",[" & Pair ("format") & "," & Pair ("profile") & "," & Pair ("bundle_declared") & "," & Pair ("origin") & "]]";
   end Declaration_Encoding;
   function Agent_Context_Matches (Data : E.Bytes; Saved, Subject, Agent_Record : E.Span) return Boolean is
      Material : constant E.Span := Field (Data, Saved, "authorityMaterial");
      Found : constant E.Span := Field (Data, Material, "finalization");
      Sealed : constant E.Span := Child (Data, Found, 1);
   begin
      if Is_Null (Data, Found) or else Is_Null (Data, Sealed) then return True; end if;
      declare
         Start : constant E.Span := Child (Data, Found, 0);
         Value : constant E.Span := Field (Data, Sealed, "value");
         Evidence : constant String := Scalar (Data, Field (Data, Value, "evidence"));
         Raw : constant E.Bytes := Bytes (Evidence);
         Decoded : constant Worldline.Raw_JSON.Decoded_JSON := Worldline.Raw_JSON.Decode_JSON (Raw, (Raw'First, Raw'Length));
         Subject_Evidence : constant String := JSON (Data, Field (Data, Subject, "evidence"));
      begin
         if not Decoded.Valid or else Evidence /= Canonical_JSON (Subject_Evidence)
           or else Scalar (Data, Field (Data, Start, "subject")) /= Scalar (Data, Field (Data, Subject, "instance_id"))
           or else Scalar (Data, Field (Data, Value, "content")) /= Scalar (Data, Field (Data, Subject, "content_id")) then return False; end if;
         declare Checks : constant String := V.Field (Decoded.Data, "checks"); begin
            for I in 1 .. V.Count (Checks) loop
               declare Row : constant String := V.Element (Checks, I - 1); begin
                  if V.Kind (Row) = V.Object_Value and then V.Text (V.Field (Row, "id")) = "agent" then
                     declare Mapped : constant String := Agent_Record_JSON (Row); begin
                        return (if V.Text (V.Field (Mapped, "origin")) = "agent" then
                          V.Equal (Mapped, JSON (Data, Agent_Record)) else Is_Null (Data, Agent_Record));
                     end;
                  end if;
               end;
            end loop;
         end;
         return Is_Null (Data, Agent_Record);
      end;
   end Agent_Context_Matches;
   function Agent_Context_Value
     (Data : E.Bytes; Saved, Subject : E.Span; Actual : Boolean) return String is
      Material : constant E.Span := Field (Data, Saved, "authorityMaterial");
      Found : constant E.Span := Field (Data, Material, "finalization");
      Sealed : constant E.Span := Child (Data, Found, 1);
      Start : constant E.Span := Child (Data, Found, 0);
      Value : constant E.Span := Field (Data, Sealed, "value");
      function Mapped (Row : String) return String is
         Original : constant String := Agent_Record_JSON (Row);
      begin
         return (if V.Kind (Original) = V.Object_Value
           and then V.Text (V.Field (Original, "origin")) = "agent"
           then Canonical_JSON (Original) else "null");
      end Mapped;
      function Present_Agent return String is
         Row : constant E.Span := Find_Agent (Data, Subject);
      begin
         return (if Row.Length = 0 then "null" else Mapped (JSON (Data, Row)));
      end Present_Agent;
      function Retained_Agent (Evidence : String) return String is
         Rows : constant String := V.Field (Evidence, "checks");
      begin
         for I in 1 .. V.Count (Rows) loop
            declare Row : constant String := V.Element (Rows, I - 1); begin
               if V.Kind (Row) = V.Object_Value
                 and then V.Text (V.Field (Row, "id")) = "agent"
               then return Mapped (Row); end if;
            end;
         end loop;
         return "null";
      end Retained_Agent;
      function Byte_Value (Text : String) return String is
        ("[""bytes""," & V.Quote (Base64 (Bytes (Text))) & "]");
   begin
      if Is_Null (Data, Found) or else Is_Null (Data, Sealed) then
         -- The original unsealed pair uses the current full agent observation
         -- twice. Derive it from the retained World, never a carried coordinate.
         return Present_Agent;
      end if;
      declare
         Evidence : constant String := Scalar (Data, Field (Data, Value, "evidence"));
         Raw : constant E.Bytes := Bytes (Evidence);
         Decoded : constant Worldline.Raw_JSON.Decoded_JSON :=
           Worldline.Raw_JSON.Decode_JSON (Raw, (Raw'First, Raw'Length));
      begin
         if not Decoded.Valid then return ""; end if;
         return "[" & Byte_Value (Scalar (Data, Field (Data,
           (if Actual then Subject else Start),
           (if Actual then "instance_id" else "subject")))) & "," &
           Byte_Value (Scalar (Data, Field (Data,
             (if Actual then Subject else Value),
             (if Actual then "content_id" else "content")))) & "," &
           Byte_Value (if Actual then Canonical_JSON
             (JSON (Data, Field (Data, Subject, "evidence"))) else Evidence) & "," &
           (if Actual then Present_Agent else Retained_Agent (Decoded.Data)) & "]";
      end;
   end Agent_Context_Value;
   function Bind
     (Data : E.Bytes; Saved, Values, Subject, Candidate,
      Authoritative_Requirement, Resulting_Requirement, Roots, Agent,
      Agent_Record, Prepared : E.Span; Staged : Boolean;
      Facts_Data : E.Bytes; Capsules : E.Span) return Boolean is
      package CW renames Worldline.Collapse_Wire;
      package AR renames Worldline.Retained_Evidence_Replay;
      use type CW.Raw_Request; use type CW.Raw_Optional_Hash;
      Material : constant E.Span := Field (Data, Saved, "authorityMaterial");
      Capture : constant E.Span := Field (Data, Saved, "capture");
      Typed : constant E.Span := Field (Data, Saved, "typedRows");
      Results : constant E.Span := Field (Data, Saved, "results");
      Stream : constant E.Span := Field (Data, Saved, "retainedStream");
      Header : constant E.Span := Child (Data, Child (Data, Stream, 0), 0);
      Invocations : constant E.Span := Child (Data, Child (Data, Stream, 0), 1);
      Acquired : constant E.Span := Child (Data, Stream, 1);
      Observed : constant E.Span := Field (Data, Saved, "observed");
      Initial : constant E.Span := Field (Data, Observed, "captureContext");
      Context : constant E.Span := Field (Data, Saved, "context");
      Requirement_JSON : constant String := JSON (Data, Authoritative_Requirement);
      Captured_Requirement : constant String := JSON (Data, Field (Data, Initial, "requirement"));
      Context_JSON : constant String := JSON (Data, Context);
      Measurement_JSON : constant String := JSON (Data, Field (Data, Initial, "measurement"));
      Post_JSON : constant String := JSON (Data, Field (Data, Observed, "postMeasurement"));
      Initial_Manifests : constant String := V.Field (Measurement_JSON, "manifests");
      Post_Manifests : constant String := V.Field (Post_JSON, "manifests");
      Root : constant String := Content_Root (Initial_Manifests);
      Post_Root : constant String := Content_Root (Post_Manifests);
      Finalization : constant Boolean := E.Decode (Data, Capture, E.Recovery).Record_Name.Encoded.Length /= 0
        and then Field (Data, Capture, "input").Length /= 0;
      Input : constant E.Span := Field (Data, Capture, "input");
      Full_Root : constant String := (if Finalization then Scalar (Data, Field (Data, Input, "root")) else Root);
      Current_Plan : constant String := Policy_Plan (Requirement_JSON, Additional (Data, Typed), Finalization);
      Captured_Plan : constant String := Policy_Plan (Captured_Requirement, Additional (Data, Typed), Finalization);
      Actual_Plan : constant String := (if Finalization then Start_Plan
        (Data, Child (Data, Field (Data, Material, "finalization"), 0), E.Recovery) else Captured_Plan);
      Decoded : constant AR.Collapse_Values_Result := AR.Decode_Recovery_Collapse_Values (Data, Values);
      function Native_Arena_Last return E.Count is
         Need : E.Count := Data'Length;
         Size : constant E.Count := Arena_Length (Data, Material);
         Extra : constant E.Count := E.Count (Root'Length + Post_Root'Length);
         Plans : constant E.Count := Plan_Length (Actual_Plan, False);
      begin
         if Extra > E.Count'Last - Need then return Data'Last; end if;
         Need := Need + Extra;
         if Plans > E.Count'Last - Need then return Data'Last; end if;
         Need := E.Count'Max (Need + Plans, Size);
         if Need = 0 or else Need - 1 > E.Count'Last - Data'First then return Data'Last; end if;
         return Data'First + Need - 1;
      end Native_Arena_Last;
      Arena : E.Bytes (Data'First .. Native_Arena_Last);
      Policy_Position : E.Count :=
        (if E.Count (Root'Length + Post_Root'Length) >= E.Count'Last - Data'Last
         then Data'Last else Data'Last + 1 + E.Count (Root'Length + Post_Root'Length));
      Captured_Required : R.Check_Array (1 .. E.Count (V.Count (V.Field (Actual_Plan, "required"))));
      Native_Completion : R.Required_Check;
      Rows : R.Measured_Array (1 .. Count (Data, Typed));
      History : H.History (1 .. Row_Count (Data, Material));
      Promotions : Boolean_Array (History'Range);
      Final_Record : H.Optional_Record; Native_Current : H.Optional_Cursor;
      Saved_Current, Prior : T.Cursor;
      Captured : T.Terminal_Record;
      Source_Valid, Final_Promotion : Boolean;
      Before, After : T.Span;
      function Effective (Name : String) return E.Span is
      begin
         for I in reverse E.Count range 0 .. Count (Data, Results) - 1 loop
            declare Row : constant E.Span := Child (Data, Results, I); begin
               if V.Python_String (Get (JSON (Data, Row), "id")) = Name then return Row; end if;
            end;
         end loop;
         return Empty;
      end Effective;
      function Members (Actual : Boolean) return String is
         function Part (I : Natural) return String is
         begin
            if I = P.Required_Count (Requirement_JSON) then return ""; end if;
            declare Name : constant String := P.Required (Requirement_JSON, I);
               Row : constant E.Span := Effective (Name);
               Exec : constant E.Span := Field (Data, Row, "executedVerifierSet");
               Identity : constant String := (if not Actual then Bundle (Triples (V.Field (Requirement_JSON, "verifiers"), Name, True, False))
                 elsif E.Decode (Data, Exec, E.Recovery).Form = E.Object_Value then Bundle (Triples (JSON (Data, Field (Data, Exec, "members")), Normalize => False))
                 else Bundle ("[]"));
            begin
               if Actual and then (Row.Length = 0 or else
                 (Exec.Length = 0 and then not Text_Is (Data, Field (Data, Row, "origin"), "engine"))) then return ""; end if;
               return (if I = 0 then "" else ",") & "[""""," & V.Quote (Name) & "," & V.Quote (Identity) & "]" & Part (I + 1);
            end;
         end Part;
      begin return "[" & Part (0) & "]"; end Members;
      Expected_Members : constant String := Members (False);
      Actual_Members : constant String := Members (True);
      Declared_Bundle : constant String := Bundle (Expected_Members);
      function Execution_Complete return Boolean is
      begin
         for I in 1 .. P.Required_Count (Requirement_JSON) loop
            declare Row : constant E.Span := Effective (P.Required (Requirement_JSON, I - 1));
               Exec : constant E.Span := Field (Data, Row, "executedVerifierSet");
            begin
               if Row.Length = 0 or else (Exec.Length = 0 and then not Text_Is (Data, Field (Data, Row, "origin"), "engine")) then return False; end if;
            end;
         end loop;
         return True;
      end Execution_Complete;
      Executed_Bundle : constant String := (if Execution_Complete then Bundle (Actual_Members) else "");
      function Raw_Hash (Value : String) return CW.Raw_Optional_Hash is
         Bytes_Value : constant String := Hex_Bytes (Value, False);
         Result : CW.Raw_Optional_Hash := (0, (others => 0));
      begin
         if Value'Length = 0 then return Result; end if;
         if Bytes_Value'Length /= 32 then return Result; end if;
         Result.Present := 1;
         for I in Result.Value'Range loop Result.Value (I) := Character'Pos (Bytes_Value (Bytes_Value'First + I)); end loop;
         return Result;
      end Raw_Hash;
      function Project_Request return CW.Raw_Request is
         Result : CW.Raw_Request := Decoded.Raw;
         Instance : constant String := Scalar (Data, Field (Data, Subject, "instance_id"));
         Candidate_Instance : constant String := Scalar (Data, Field (Data, Candidate, "instance_id"));
         Binding : constant String := (if Instance = Candidate_Instance then "" else Hash_Id ("worldline-return-v1" & Instance));
         Claimed : constant String := (if Instance = Candidate_Instance then "" else Scalar (Data, Field (Data, Candidate, "mission_hash")));
         Context_Instance : constant String := V.Text (V.Field (V.Field (Context_JSON, "candidate"), "instanceId"));
      begin
         Result.Expected_Subject := Raw_Hash (if Instance'Length = 0 then "" else Hash_Id
           ("worldline-subject-v1[" & V.Quote (Instance) & "," & V.Quote (Binding) & "]"));
         Result.Evidence_Subject := Raw_Hash (if Context_Instance'Length = 0 then "" else Hash_Id
           ("worldline-subject-v1[" & V.Quote (Context_Instance) & "," & V.Quote (Claimed) & "]"));
         Result.Current_Requirement := Raw_Hash (V.Text (V.Field (Requirement_JSON, "requirementHash")));
         Result.Resulting_Requirement := (if Result.Evaluation_Mode = 1 then (0, (others => 0))
           else Raw_Hash (V.Text (V.Field (JSON (Data, Resulting_Requirement), "requirementHash"))));
         Result.Declared_Verifiers := Raw_Hash (Declared_Bundle);
         Result.Expected_Root_Set := Raw_Hash (Hash_Id ("worldline-root-set-v1" & Roots_JSON (Data, Roots, True)));
         if Staged then
            Result.Staged_Evaluated_Requirement := Raw_Hash (V.Text (V.Field (Context_JSON, "requirementHash")));
            Result.Staged_Executed_Verifiers := Raw_Hash (Executed_Bundle);
            Result.Staged_Examined_Root := Raw_Hash (Root);
         else
            Result.Evaluated_Requirement := Raw_Hash (V.Text (V.Field (Context_JSON, "requirementHash")));
            Result.Executed_Verifiers := Raw_Hash (Executed_Bundle);
            Result.Tested_Root := Raw_Hash (Root);
         end if;
         return Result;
      end Project_Request;
      function Root_Coordinates (Actual : Boolean) return String is
         Normal : constant String := "[" & (if Actual then V.Field (Context_JSON, "roots") else Roots_JSON (Data, Roots, False)) & "," &
           (if Actual then V.Field (Measurement_JSON, "storedRootSetHash") else JSON (Data, Field (Data, Subject, "root_set_hash"))) & "," &
           V.Quote (Root) & "," & V.Quote (if Actual then Post_Root else Root) & "," & V.Quote (Root);
      begin
         if not Finalization then
            return "[" & (if Actual then V.Field (Context_JSON, "roots") else Roots_JSON (Data, Roots, False)) & "," &
              (if Actual then V.Field (Measurement_JSON, "storedRootSetHash") else JSON (Data, Field (Data, Subject, "root_set_hash"))) & "," &
              (if Actual then V.Field (Measurement_JSON, "observedContentRoot") else V.Quote (Root)) & "," &
              (if Actual then V.Field (Post_JSON, "observedContentRoot") else V.Quote (Root)) & "," &
              (if Actual then Get (Context_JSON, "examinedContentRoot") else V.Quote (Root)) & "]";
         end if;
         return Normal & "," & (if Actual then V.Field (Measurement_JSON, "observedContentRoot") else V.Quote (Full_Root)) & "," &
           (if Actual then V.Field (Post_JSON, "observedContentRoot") else V.Quote (Full_Root)) & "," &
           (if Actual then Get (Context_JSON, "examinedContentRoot") else V.Quote (Full_Root)) & "," &
           Canonical_JSON (Initial_Manifests) & "," & (if Actual then Canonical_JSON (Post_Manifests) else Canonical_JSON (Initial_Manifests)) & "]";
      end Root_Coordinates;
      function Join_Parts (Left, Right : String) return String is
        (Left & (if Left'Length /= 0 and then Right'Length /= 0 then "," else "") & Right);
      function Projected_Invocations (Returns_Only : Boolean) return String is
         function Parts (I : E.Count) return String is
         begin
            if I = Count (Data, Results) then return ""; end if;
            declare Row : constant E.Span := Child (Data, Results, I);
               Start : constant E.Span := Field (Data, Row, "engineInvocationObservation");
               Returned : constant E.Span := Field (Data, Row, "rawRunnerResult");
            begin
               if Start.Length = 0 or else Is_Null (Data, Start) then return Parts (I + 1); end if;
               return Join_Parts ((if Returns_Only then Terminal_Encoding (Data, Returned) else
                 "[""array"",[" & Terminal_Encoding (Data, Field (Data, Start, "invocationId")) & "," &
                   Terminal_Encoding (Data, Start) & ",[""object"",[[" &
                   V.Quote (Base64 (Bytes ("started"))) & "," & Terminal_Encoding (Data, Start) & "],[" &
                   V.Quote (Base64 (Bytes ("result"))) & "," & Terminal_Encoding (Data, Returned) & "]]]]]"),
                 Parts (I + 1));
            end;
         end Parts;
      begin return "[""array"",[" & Parts (0) & "]]"; end Projected_Invocations;
      function Acquisition_Stream_Value (Actual : Boolean) return String is
         function Encode (D : E.Bytes; Span : E.Span; Layer : E.Layer) return String is
           (if Finalization then Lift_Encoding (D, Span, Layer) else Terminal_Encoding (D, Span, Layer));
         function Tuple_Value (Id, Kind, Occurrence, Observation : String) return String is
           (if Finalization then Lifted ("tuple", "[""array"",[" & Id & "," & Kind & "," & Occurrence & "," & Observation & "]]")
            else "[""array"",[" & Id & "," & Kind & "," & Occurrence & "," & Observation & "]]");
         function Actual_Parts (I : E.Count) return String is
         begin
            if I = Count (Data, Results) then return ""; end if;
            declare Row : constant E.Span := Child (Data, Results, I);
               Start : constant E.Span := Field (Data, Row, "engineInvocationObservation");
               Raw : constant E.Bytes := Acquisition_Data (Data, Row, Finalization);
               Layer : constant E.Layer := Acquisition_Layer (Data, Row, Finalization);
               Root : constant E.Span := (Raw'First, Raw'Length);
               function Events (J : E.Count) return String is
               begin
                  if J = Count (Raw, Root, Layer) then return ""; end if;
                  declare Event : constant E.Span := Child (Raw, Root, J, Layer); begin
                     return Join_Parts (Tuple_Value (
                       Encode (Data, Field (Data, Start, "invocationId"), E.Recovery),
                       Encode (Raw, Field (Raw, Event, "kind", Layer), Layer),
                       Encode (Raw, Field (Raw, Event, "occurrence", Layer), Layer),
                       Encode (Raw, Field (Raw, Event, "observation", Layer), Layer)), Events (J + 1));
                  end;
               end Events;
            begin
               if Start.Length = 0 or else Is_Null (Data, Start) then return Actual_Parts (I + 1); end if;
               return Join_Parts (Events (0), Actual_Parts (I + 1));
            end;
         end Actual_Parts;
         function Expected_Parts (I : E.Count) return String is
            function Events (J : E.Count) return String is
            begin
               if J = Count (Data, Acquired) then return ""; end if;
               declare Event : constant E.Span := Child (Data, Acquired, J);
                  Id : constant String := Scalar (Data, Child (Data, Event, 0));
                  Include : Boolean := False;
               begin
                  if I < Count (Data, Invocations) then
                     Include := Id = Scalar (Data, Child (Data, Child (Data, Invocations, I), 0));
                  else
                     Include := True;
                     for K in E.Count range 0 .. Count (Data, Invocations) - 1 loop
                        if Id = Scalar (Data, Child (Data, Child (Data, Invocations, K), 0)) then Include := False; end if;
                     end loop;
                  end if;
                  return Join_Parts ((if Include then Encode (Data, Event, E.Recovery) else ""), Events (J + 1));
               end;
            end Events;
         begin
            if I > Count (Data, Invocations) then return ""; end if;
            return Join_Parts (Events (0), Expected_Parts (I + 1));
         end Expected_Parts;
         Parts : constant String := (if Actual then Actual_Parts (0) else Expected_Parts (0));
      begin
         return (if Finalization then Lifted ("tuple", "[""array"",[" & Parts & "]]")
           else "[""array"",[" & Parts & "]]");
      end Acquisition_Stream_Value;
      function Context_Field_Value (K : A.Context_Field; Actual : Boolean) return String is
      begin
         case K is
            when A.Capture_Header => return Terminal_Encoding (Data, (if Actual then Initial else Header));
            when A.Returned_Context => return (if Actual then Terminal_Encoding (Data, Field (Data, Observed, "returnedContext"))
              else Scalar (Data, Field (Data, Capture, "context")));
            when A.Full_Policy => return Policy_Value (if Actual then Captured_Requirement else Requirement_JSON);
            when A.Candidate_Record => return Terminal_Encoding (Data, (if Actual then Field (Data, Context, "candidate") else Field (Data, Header, "subject")));
            when A.Root_Manifests => return Root_Coordinates (Actual);
            when A.Effective_Roster => return Canonical_JSON (if Actual then Captured_Plan else Current_Plan);
            when A.Declared_Verifiers => return Canonical_JSON (Get ((if Actual then Captured_Requirement else Requirement_JSON), "verifiers"));
            when A.Executed_Verifiers => return (if Actual then Actual_Members else Expected_Members);
            when A.Agent_Record => return Agent_Context_Value (Data, Saved, Subject, Actual);
            when A.Source_Id => return Scalar (Data, (if Actual then Field (Data, Header, "source") else Field (Data, Capture, "source")));
            when A.Examined_Root => return (if Actual then V.Text (V.Field (Measurement_JSON, "observedContentRoot")) else Full_Root);
            when A.Invocation_Stream => return (if Actual then Projected_Invocations (False) else Terminal_Encoding (Data, Invocations));
            when A.Acquisition_Stream => return Acquisition_Stream_Value (Actual);
            when A.Returned_Rows => return (if Actual then Projected_Invocations (True) else Terminal_Encoding (Data, Field (Data, Observed, "runnerResults")));
         end case;
      end Context_Field_Value;
      function Row_Field_Value (I : E.Count; K : A.Row_Field; Actual : Boolean) return String is
         Row : constant E.Span := Child (Data, Results, I - 1);
         Item : constant E.Span := Child (Data, Invocations, I - 1);
         Started : constant E.Span := Child (Data, Item, 1);
         Returned : constant E.Span := Child (Data, Item, 2);
         Row_JSON : constant String := JSON (Data, Row, E.Recovery, True, True);
         Name : constant String := V.Python_String (Get (Row_JSON, "id"));
         Executed : constant String := Get (Row_JSON, "executedVerifierSet");
         Members : constant String := Get (Executed, "members");
         Has_Invocation : constant Boolean := I - 1 < Count (Data, Invocations);
         function Optional_JSON (Part : E.Span) return String is
           (if Part.Length = 0 or else Is_Null (Data, Part) then "" else JSON (Data, Part, E.Recovery, True, True));
         function Row_Acquisition_Value return String is
            function Pair (Key : String; Value : E.Span) return String is
              (if Finalization then "[""array"",[" & String_Encoding (Key) & "," & Lift_Encoding (Data, Value) & "]]"
               else "[" & V.Quote (Base64 (Bytes (Key))) & "," & Terminal_Encoding (Data, Value) & "]");
            function Expected_Parts (J : E.Count) return String is
            begin
               if J = Count (Data, Acquired) then return ""; end if;
               declare Event : constant E.Span := Child (Data, Acquired, J);
                  Occurrence : constant E.Span := Child (Data, Event, 2);
                  Pairs : constant String := Pair ("kind", Child (Data, Event, 1)) & "," &
                    Pair ("observation", Child (Data, Event, 3)) &
                    (if Is_Null (Data, Occurrence) then "" else "," & Pair ("occurrence", Occurrence));
                  Value : constant String := (if Finalization then Lifted ("object", "[""array"",[" & Pairs & "]]")
                    else "[""object"",[" & Pairs & "]]");
               begin
                  return Join_Parts ((if Scalar (Data, Child (Data, Event, 0)) = Scalar (Data, Child (Data, Item, 0))
                    then Value else ""), Expected_Parts (J + 1));
               end;
            end Expected_Parts;
         begin
            if Actual then
               declare
                  Raw : constant E.Bytes := Acquisition_Data (Data, Row, Finalization);
                  Layer : constant E.Layer := Acquisition_Layer (Data, Row, Finalization);
               begin
                  if Raw'Length = 0 then return ""; end if;
                  return (if Finalization then Lift_Encoding (Raw, (Raw'First, Raw'Length), Layer)
                    else Terminal_Encoding (Raw, (Raw'First, Raw'Length), Layer));
               end;
            end if;
            if not Has_Invocation then return ""; end if;
            return (if Finalization then Lifted ("list", "[""array"",[" & Expected_Parts (0) & "]]")
              else "[""array"",[" & Expected_Parts (0) & "]]");
         end Row_Acquisition_Value;
      begin
         case K is
            when A.Invocation_Start => return Optional_JSON (if Actual then Field (Data, Row, "engineInvocationObservation") else Started);
            when A.Invocation_Return => return Optional_JSON (if Actual then Field (Data, Row, "rawRunnerResult") else Field (Data, Returned, "result"));
            when A.Raw_Acquisitions => return Row_Acquisition_Value;
            when A.Invocation_Binding => return (if not Has_Invocation then "" else "[" & V.Quote
              (if Actual then Scalar (Data, Field (Data, Started, "evaluationRun")) else Scalar (Data, Field (Data, Field (Data, Saved, "cursor"), "run"))) & "," &
              V.Quote (if Actual then Scalar (Data, Field (Data, Started, "checkId")) else Name) & "," &
              V.Quote (if Actual then Scalar (Data, Field (Data, Started, "invocationId")) else Scalar (Data, Child (Data, Item, 0))) & "," &
              V.Quote (Scalar (Data, Field (Data, (if Actual then Field (Data, Row, "engineInvocationObservation") else Started), "worldInstance"))) & "]");
            when A.Candidate_Snapshot => return Optional_JSON (if not Has_Invocation then Empty
              elsif Actual then Field (Data, Field (Data, Row, "rawRunnerResult"), "candidateSnapshot") else Field (Data, Started, "candidateSnapshot"));
            when A.Invocation_Verifiers => return (if Actual then (if Has_Invocation then Triples (JSON (Data, Field (Data, Started, "verifierEntries"))) else "[]")
              else Triples (Get (Requirement_JSON, "verifiers"), Name, True));
            when A.Verifier_Members => return (if Actual then Triples (Members) else Triples (Get (Requirement_JSON, "verifiers"), Name, True));
            when A.Verifier_Identity => return (if Actual then (if V.Kind (Executed) = V.Object_Value then V.Text (Get (Executed, "identity")) else Bundle ("[]"))
              else Bundle (if V.Kind (Executed) = V.Object_Value then Triples (Members, Normalize => False) else "[]"));
         end case;
      end Row_Field_Value;
      function Metadata_Field (I : E.Count; K : Positive) return String is
         Row : constant E.Span := Child (Data, Results, I - 1);
         Check : constant E.Span := Field (Data, Row, "id");
         Start : constant E.Span := Field (Data, Row, "engineInvocationObservation");
         Boundary : constant E.Span := Field (Data, Row, "evaluatorBoundary");
         Verifier : constant E.Span := Field (Data, Row, "executedVerifierSet");
      begin
         case K is
            when 1 => return (if E.Decode (Data, Check, E.Recovery).Form = E.Text_Value then Scalar (Data, Check) else Terminal_Encoding (Data, Check));
            when 2 => return Terminal_Encoding (Data, Field (Data, Row, "origin"));
            when 3 => return Terminal_Encoding (Data, Row);
            when 4 => return (if (Start.Length = 0 or else Is_Null (Data, Start)) and then
              (Boundary.Length = 0 or else Is_Null (Data, Boundary)) then "" else
              "[""object"",[[" & V.Quote (Base64 (Bytes ("engineInvocation"))) & "," & Terminal_Encoding (Data, Start) & "],[" &
              V.Quote (Base64 (Bytes ("evaluatorBoundary"))) & "," & Terminal_Encoding (Data, Boundary) & "]]]");
            when others => return (if Verifier.Length = 0 or else Is_Null (Data, Verifier) then "" else Terminal_Encoding (Data, Verifier));
         end case;
      end Metadata_Field;
      function Buffer_Length return E.Count is
         Length : E.Count := Data'Length;
      begin
         for K in A.Context_Field loop
            Length := Length + E.Count (Context_Field_Value (K, False)'Length + Context_Field_Value (K, True)'Length);
         end loop;
         for I in Rows'Range loop
            for K in A.Row_Field loop Length := Length + E.Count (Row_Field_Value (I, K, False)'Length + Row_Field_Value (I, K, True)'Length); end loop;
            for K in 1 .. 5 loop Length := Length + E.Count (Metadata_Field (I, K)'Length); end loop;
         end loop;
         return Length + Plan_Length (Current_Plan, False);
      end Buffer_Length;
   begin
      Arena (Data'Range) := (others => 0);
      Collect (Data, Material, Subject, Field (Data, Authoritative_Requirement, "requirementHash"),
        Arena, History, Final_Record, Native_Current, Source_Valid, Promotions, Final_Promotion,
        Facts_Data => Facts_Data, Capsules => Capsules);
      if not Source_Valid or else not Decoded.Present or else not Full_Stream (Data, Saved)
        or else not Same (Data, Header, Initial)
        or else not Same (Data, Field (Data, Header, "subject"), Field (Data, Context, "candidate"))
        or else not Agent_Context_Matches (Data, Saved, Subject, Agent_Record)
        or else not Agent_Matches (Data, Subject, Agent, Agent_Record, True, Facts_Data, Capsules)
        or else not Context_Valid (Context_JSON, Scalar (Data, Field (Data, Subject, "instance_id")))
      then return False; end if;
      Read_Cursor (Data, Field (Data, Saved, "cursor"), Arena, Source_Valid, Saved_Current, E.Recovery, True);
      Read_Cursor (Data, Prepared, Arena, Source_Valid, Prior, E.Recovery, True);
      if Finalization then
         declare Found : constant E.Span := Field (Data, Material, "finalization");
            Start : FZ.Start_Record;
            Plans : R.Check_Array (1 .. Count (Data, Field (Data, Child (Data, Found, 0), "required")));
            Content, Source, Context_Span : T.Span;
         begin
            Read_Start (Data, Child (Data, Found, 0), Arena, Policy_Position, Plans, Start, Source_Valid);
            Put (Data, Field (Data, Subject, "content_id"), Arena, Content, Source_Valid, Expected_Form => E.Text_Value);
            Put (Data, Field (Data, Capture, "source"), Arena, Source, Source_Valid);
            Put (Data, Field (Data, Capture, "context"), Arena, Context_Span, Source_Valid);
            Captured_Required := Plans;
            Captured := (FZ.Bound_To (Start, T.Content_Identity (Content)), T.Source_Identity (Source),
              T.Captured_Bytes (Context_Span), T.E.Incomplete_Unknown, T.E.No_Outcome);
            Put (Data, Field (Data, Input, "root"), Arena, Before, Source_Valid);
            Put (Data, Field (Data, Capture, "post_root"), Arena, After, Source_Valid);
            if not Manifests_Match (Data, Field (Data, Input, "manifests"),
                Field (Data, Field (Data, Initial, "measurement"), "manifests"))
              or else not Manifests_Match (Data, Field (Data, Capture, "post_manifests"),
                Field (Data, Field (Data, Observed, "postMeasurement"), "manifests"))
            then return False; end if;
         end;
      else
         Read_Terminal (Data, Capture, Arena, Source_Valid, Captured);
         Before := (Data'Last + 1, E.Count (Root'Length)); After := (Before.First + Before.Length, E.Count (Post_Root'Length));
         for I in Root'Range loop Arena (Before.First + E.Count (I - Root'First)) := Character'Pos (Root (I)); end loop;
         for I in Post_Root'Range loop Arena (After.First + E.Count (I - Post_Root'First)) := Character'Pos (Post_Root (I)); end loop;
         Plan_Checks (Captured_Plan, Arena, Policy_Position, Captured_Required, Native_Completion, Source_Valid, False);
      end if;
      for I in Rows'Range loop
         Read_Result (Data, Child (Data, Typed, I - 1), Field (Data, Capture, "source"),
           Child (Data, Invocations, I - 1), Arena, Source_Valid, Rows (I), E.Recovery,
           Finalization, Captured.Binding, Facts_Data, Capsules);
      end loop;
      if not Source_Valid or else not Saved_Current.Present or else not Prior.Present then return False; end if;
      declare
         B : E.Bytes (Data'First .. Data'First + Buffer_Length - 1);
         Position : E.Count := Data'Last + 1;
         Expected, Actual : A.Context_Fields;
         Joined : A.Context_Rows (Rows'Range);
         Metadata : A.Row_Metadata_Array (Rows'Range);
         Required : R.Check_Array (1 .. E.Count (V.Count (V.Field (Current_Plan, "required"))));
         Completion : R.Required_Check;
         Expected_Binding : T.Attempt_Binding;
         Store_Id, Subject_Id, Content_Id, Run, Epoch : T.Span;
         Req : T.Optional_Requirement;
         procedure Pack (Text : String; Result : out E.Span) is
         begin
            Result := (Position, E.Count (Text'Length));
            for I in Text'Range loop B (Position + E.Count (I - Text'First)) := Character'Pos (Text (I)); end loop;
            Position := Position + Result.Length;
         end Pack;
         procedure Optional (Text : String; Result : out A.Optional_Bytes) is
            Span : E.Span;
         begin
            if Text'Length = 0 then Result := (Present => False); return; end if;
            Pack (Text, Span); Result := (True, Span);
         end Optional;
         Span : E.Span;
         Check_Span, Source_Span, Payload_Span : E.Span;
         Execution_Span, Verifier_Span : A.Optional_Bytes;
      begin
         B (Data'Range) := Arena (Data'Range);
         for K in A.Context_Field loop
            Pack (Context_Field_Value (K, False), Span); Expected (K) := (True, Span);
            Pack (Context_Field_Value (K, True), Span); Actual (K) := (True, Span);
         end loop;
         for I in Rows'Range loop
            Joined (I).Item := Rows (I).Item;
            Joined (I).Declared := Rows (I).Declared;
            -- ContextRow owns the complete rebuilt typed declaration; a current
            -- policy substitution would wrongly discard unrelated ERROR rows.
            Joined (I).Actual_Declared := Rows (I).Declared;
            for K in A.Row_Field loop
               Optional (Row_Field_Value (I, K, False), Joined (I).Expected (K));
               Optional (Row_Field_Value (I, K, True), Joined (I).Observed (K));
            end loop;
            Pack (Metadata_Field (I, 1), Check_Span);
            Pack (Metadata_Field (I, 2), Source_Span);
            Pack (Metadata_Field (I, 3), Payload_Span);
            Optional (Metadata_Field (I, 4), Execution_Span);
            Optional (Metadata_Field (I, 5), Verifier_Span);
            Metadata (I) := (Check_Span, Source_Span, Payload_Span, Execution_Span, Verifier_Span);
         end loop;
         Plan_Checks (Current_Plan, B, Position, Required, Completion, Source_Valid, False);
         Put (Data, (if Finalization then Field (Data, Child (Data, Field (Data, Material, "finalization"), 0), "store_id")
                    else Field (Data, Material, "pending_store")), B, Store_Id, Source_Valid);
         Put (Data, Field (Data, Subject, "instance_id"), B, Subject_Id, Source_Valid, Expected_Form => E.Text_Value);
         Put (Data, Field (Data, Subject, "content_id"), B, Content_Id, Source_Valid, Expected_Form => E.Text_Value);
         Put (Data, Field (Data, Field (Data, Saved, "cursor"), "run"), B, Run, Source_Valid, Expected_Form => E.Text_Value);
         Put (Data, Field (Data, Field (Data, Saved, "cursor"), "epoch"), B, Epoch, Source_Valid, E.Recovery, True, E.Integer_Value);
         Read_Requirement (Data, Field (Data, Authoritative_Requirement, "requirementHash"), B, Source_Valid, Req, Expected_Form => E.Text_Value);
         Expected_Binding := (T.Store_Identity (Store_Id), T.Subject_Identity (Subject_Id), T.Content_Identity (Content_Id),
                              T.Run_Identity (Run), T.Epoch (Epoch), Req);
         return Source_Valid and then A.Join_Metadata (Arena, B,
           T.Result_Array'(for I in Rows'Range => Rows (I).Item), Metadata)
           and then A.Join_Context (Arena, B, Captured,
             (if Native_Current.Present then (True, T.Run_Identity (T.Span'(Native_Current.Value.Run.First, Native_Current.Value.Run.Length)),
               T.Epoch (T.Span'(Native_Current.Value.Sequence.Value.First, Native_Current.Value.Sequence.Value.Length))) else (Present => False)),
             Expected_Binding, Saved_Current, Prior, Expected, Actual, Before, After,
             Roster_Policy (Actual_Plan), Roster_Policy (Current_Plan),
             T.Result_Array'(for I in Rows'Range => Rows (I).Item), Joined,
             Captured_Required, Required, Decoded.Raw, Project_Request);
      end;
   end Bind;
end Worldline.Recovery_Material_Replay;
