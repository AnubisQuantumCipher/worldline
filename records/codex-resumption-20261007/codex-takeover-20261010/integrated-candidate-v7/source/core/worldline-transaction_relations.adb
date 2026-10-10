with Attest.SHA256;
with Interfaces;
with Worldline.Archive_Base64;
with Canonical_Artifacts;
with Worldline.Operation_Archive;
with Worldline.Producer_Values;
with Worldline.Evaluation_Policy;
with Worldline.Evaluation_Producer;
with Worldline.Evaluation_Wire;
with Worldline.Transaction_Archive_JSON;
with Worldline.Recovery_Packet;
with Worldline.Raw_JSON;
with Worldline.Recovery_Archive;

package body Worldline.Transaction_Relations with SPARK_Mode is
   package A renames Worldline.Operation_Archive;
   package C renames Canonical_Artifacts;
   package P renames Worldline.Producer_Values;
   package Policy renames Worldline.Evaluation_Policy;
   package Producer renames Worldline.Evaluation_Producer;
   package W renames Worldline.Evaluation_Wire;
   package SHA renames Attest.SHA256;
   package J renames Worldline.Transaction_Archive_JSON;
   package Packet renames Worldline.Recovery_Packet;
   package R renames Worldline.Recovery_Archive;
   use type Packet.Status;
   use type E.Count;
   use type E.Value_Kind;
   use type C.Kind;
   use type E.Q.Byte;
   use type E.Span;
   use type E.Bytes;
   use type E.Layer;
   use type P.Value_Kind;
   use type Interfaces.Unsigned_64;
   use type W.Byte;
   use type Worldline.Hash;

   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span is
      V : constant E.View := E.Decode (Data, Item, E.Operation);
      N : E.Count;
   begin
      if V.Form = E.Object_Value then return A.Field (Data, Item, Name); end if;
      if V.Form /= E.Record_Value or else not A.Valid (Data, Item) then return (1, 0); end if;
      N := E.Array_Length (Data, V.Children);
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               Pair : constant E.View := E.Decode
                 (Data, E.Array_Element (Data, V.Children, I), E.Finalization);
            begin
               if Pair.Form = E.List_Value and then E.Array_Length (Data, Pair.Children) = 2
                 and then E.Text_Is (Data, E.Decode
                   (Data, E.Array_Element (Data, Pair.Children, 0), E.Finalization), Name)
               then return E.Array_Element (Data, Pair.Children, 1); end if;
            end;
         end loop;
      end if;
      return (1, 0);
   end F;

   function Text (Data : E.Bytes; Item : E.Span) return String is
      V : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if V.Form /= E.Text_Value or else not E.Bytes_Valid (Data, V.Payload) then return ""; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, V.Payload);
         Result : String (1 .. Raw'Length);
      begin
         for I in Result'Range loop Result (I) := Character'Val (Raw (Raw'First + E.Count (I - 1))); end loop;
         return Result;
      end;
   end Text;

   function Byte_String (Data : E.Bytes; Item : E.Span) return String is
      V : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if V.Form /= E.Bytes_Value or else not E.Bytes_Valid (Data, V.Payload) then return ""; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, V.Payload);
         Result : String (1 .. Raw'Length);
      begin
         for I in Result'Range loop Result (I) := Character'Val (Raw (Raw'First + E.Count (I - 1))); end loop;
         return Result;
      end;
   end Byte_String;

   function Is_Text (Data : E.Bytes; Item : E.Span; Value : String) return Boolean is
     (E.Text_Is (Data, E.Decode (Data, Item, E.Operation), Value));
   function Object (Data : E.Bytes; Item : E.Span) return Boolean is
     (A.Valid (Data, Item) and then E.Decode (Data, Item, E.Operation).Form = E.Object_Value);
   function Null_Or_Missing (Data : E.Bytes; Item : E.Span) return Boolean is
     (Item.Length = 0 or else E.Decode (Data, Item, E.Operation).Form = E.Null_Value);
   function List_Length (Data : E.Bytes; Item : E.Span) return E.Count is
      V : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if V.Form not in E.List_Value | E.Tuple_Value then return 0; end if;
      return E.Array_Length (Data, V.Children);
   end List_Length;
   function Element (Data : E.Bytes; Item : E.Span; I : E.Count) return E.Span is
      V : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if V.Form not in E.List_Value | E.Tuple_Value then return (1, 0); end if;
      return E.Array_Element (Data, V.Children, I);
   end Element;
   function Schema_One (Data : E.Bytes; Item : E.Span) return Boolean is
      V : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if V.Form = E.Boolean_Value then return V.Boolean_Bit; end if;
      if V.Form = E.Float_Value and then E.Bytes_Valid (Data, V.Payload) then
         declare
            Raw : constant E.Bytes := E.Materialize (Data, V.Payload);
         begin
            return Raw'Length = 8 and then Raw (Raw'First) = 16#3F#
              and then Raw (Raw'First + 1) = 16#F0#
              and then (for all I in E.Count range 2 .. 7 => Raw (Raw'First + I) = 0);
         end;
      end if;
      if V.Form /= E.Integer_Value or else V.Sign or else not E.Bytes_Valid (Data, V.Payload) then return False; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, V.Payload);
      begin
         return Raw'Length = 1 and then Raw (Raw'First) = 1;
      end;
   end Schema_One;

   --  Canonical bytes are independently matched to their complete ORIGINAL
   --  archive tree, including binary64 values and every nested field.
   function JSON_Matches (Data : E.Bytes; JSON, Value : E.Span) return Boolean is
      V : constant E.View := E.Decode (Data, JSON, E.Operation);
   begin
      if V.Form not in E.Bytes_Value | E.Text_Value or else not E.Bytes_Valid (Data, V.Payload) then return False; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, V.Payload);
      begin
         --  canonical_bytes sorts object keys, while the original operation
         --  archive retains insertion order. Match keys independently of that
         --  order, retaining exact primitive types, array order and full trees.
         --  Canonical=False preserves the UTF-8 canonical_bytes domain; the
         --  shared Canonical=True option denotes a different ASCII-only codec.
         return Worldline.Raw_JSON.JSON_Source_Value_Matches
           (Raw, Data, (Raw'First, Raw'Length), Value,
            Canonical => False, Scoped => False);
      end;
   end JSON_Matches;

   type Projection is (Context_Body, Requirement_Body, Policy_Body);
   function Omitted (Name : String; Mode : Projection) return Boolean is
     (case Mode is
         when Context_Body => Name = "contextHash",
         when Requirement_Body => Name = "requirementHash",
         when Policy_Body => Name in "sourceSha256" | "warnings" | "sourceObservation");

   --  requirement_hash uses dict(policy or {}), not a map-only coercion.
   --  The shared value parser supplies syntax; no second JSON grammar lives here.
   function Policy_Coercion (Data : E.Bytes; Original, Reduced : E.Span) return Boolean is
      Source : constant String := J.Render (Data, Original);
      Target : constant String := J.Render (Data, Reduced);
      Root : constant P.Node := P.Parse (Source);
      Result : constant P.Node := P.Parse (Target);
      function Pair_Key (Index : Positive) return String is
         Pair : constant P.Node := P.Element (Source, Root, Index);
      begin
         if Pair.Form = P.Array_Value and then P.Count (Source, Pair) = 2 then
            return P.Text (Source, P.Element (Source, Pair, 1));
         elsif Pair.Form = P.String_Value then
            declare Value : constant String := P.Text (Source, Pair);
               Width : constant Natural := P.UTF8_Width (Value, 0);
            begin
               if Width > 0 and then Width < Value'Length then
                  return Value (Value'First .. Value'First + Width - 1);
               end if;
            end;
         end if;
         return "";
      end Pair_Key;
      function Pair_Value (Index : Positive) return String is
         Pair : constant P.Node := P.Element (Source, Root, Index);
      begin
         if Pair.Form = P.Array_Value and then P.Count (Source, Pair) = 2 then
            return P.Slice (Source, P.Element (Source, Pair, 2));
         elsif Pair.Form = P.String_Value then
            declare Value : constant String := P.Text (Source, Pair);
               Width : constant Natural := P.UTF8_Width (Value, 0);
            begin
               if Width > 0 and then Width < Value'Length
                 and then P.UTF8_Width (Value, Width) = Value'Length - Width
               then return P.Quote (Value (Value'First + Width .. Value'Last)); end if;
            end;
         end if;
         return "";
      end Pair_Value;
      function Last_Value (Name : String) return String is
         Last : Natural := 0;
      begin
         for I in 1 .. P.Count (Source, Root) loop
            if Pair_Key (I) = Name then Last := I; end if;
         end loop;
         return (if Last = 0 then "" else Pair_Value (Last));
      end Last_Value;
   begin
      if Result.Form /= P.Object_Value then return False; end if;
      if not P.Truth (Source, Root)
        or else (E.Decode (Data, Original, E.Operation).Form = E.Bytes_Value
          and then E.Decode (Data, Original, E.Operation).Payload.Encoded.Length = 0)
      then return P.Count (Target, Result) = 0; end if;
      if Root.Form = P.Object_Value then
         for I in 1 .. P.Count (Source, Root) loop
            declare Name : constant String := P.Member_Name (Source, Root, I); begin
               if not Omitted (Name, Policy_Body) and then
                 not P.Equal (Source, P.Field (Source, Root, Name), Target, P.Field (Target, Result, Name))
               then return False; end if;
            end;
         end loop;
         for I in 1 .. P.Count (Target, Result) loop
            declare Name : constant String := P.Member_Name (Target, Result, I); begin
               if Omitted (Name, Policy_Body) or else not P.Present (P.Field (Source, Root, Name)) then return False; end if;
            end;
         end loop;
         return True;
      end if;
      if Root.Form /= P.Array_Value then return False; end if;
      for I in 1 .. P.Count (Source, Root) loop
         declare Pair : constant P.Node := P.Element (Source, Root, I);
            Name : constant String := Pair_Key (I);
         begin
            if Pair_Value (I) = "" or else
              (Pair.Form = P.Array_Value and then P.Element (Source, Pair, 1).Form /= P.String_Value)
            then return False; end if;
            if not Omitted (Name, Policy_Body) and then
              not P.Equal (Last_Value (Name), P.Slice (Target, P.Field (Target, Result, Name)))
            then return False; end if;
         end;
      end loop;
      for I in 1 .. P.Count (Target, Result) loop
         declare Name : constant String := P.Member_Name (Target, Result, I); begin
            if Omitted (Name, Policy_Body) or else Last_Value (Name) = "" then return False; end if;
         end;
      end loop;
      return True;
   end Policy_Coercion;

   function Projected (Data : E.Bytes; Original, Reduced : E.Span; Mode : Projection)
      return Boolean with Global => null,
        Subprogram_Variant => (Decreases => Original.Length);
   function Projected (Data : E.Bytes; Original, Reduced : E.Span; Mode : Projection)
      return Boolean
   is
      V : constant E.View := E.Decode (Data, Original, E.Operation);
      R : constant E.View := E.Decode (Data, Reduced, E.Operation);
      Offset : E.Count := 1;
      Child : C.Node;
      Kept : E.Count := 0;
   begin
      if not Object (Data, Original) or else not Object (Data, Reduced) then return False; end if;
      --  Both complete objects, including every unrequested field and key,
      --  have passed the original validation above. Keep selection local to
      --  that guard: repeating F for each name would validate all of Reduced
      --  again. This cursor returns the same first text-key match and original
      --  value span as A.Field; byte keys remain distinct from text keys.
      declare
         function Reduced_Field (Name : String) return E.Span is
            At_Child : E.Count := 1;
            Entry_Node : C.Node;
         begin
            if R.Children.Length < 2 then return (1, 0); end if;
            while At_Child < R.Children.Length - 1 loop
               pragma Loop_Invariant (At_Child in 1 .. R.Children.Length);
               pragma Loop_Variant (Decreases => R.Children.Length - At_Child);
               Entry_Node := C.Prefix (Data, R.Children, At_Child);
               if not Entry_Node.Valid then return (1, 0); end if;
               declare
                  Pair : constant E.View := E.Decode
                    (Data, C.Part (R.Children, Entry_Node.First, Entry_Node.After),
                     E.Finalization);
                  Key : constant E.View := E.Decode
                    (Data, E.Array_Element (Data, Pair.Children, 0), E.Operation);
               begin
                  if E.Text_Is (Data, Key, Name) then
                     return E.Array_Element (Data, Pair.Children, 1);
                  end if;
               end;
               At_Child := Entry_Node.After;
               if At_Child < R.Children.Length - 1 then At_Child := At_Child + 1; end if;
            end loop;
            return (1, 0);
         end Reduced_Field;
      begin
         if V.Children.Length < 2 then return False; end if;
         --  Advance through Original once instead of locating every ordinal
         --  by rescanning the entire child array and all preceding entries.
         while Offset < V.Children.Length - 1 loop
            pragma Loop_Invariant (Offset in 1 .. V.Children.Length);
            pragma Loop_Invariant (Kept < Offset);
            pragma Loop_Variant (Decreases => V.Children.Length - Offset);
            Child := C.Prefix (Data, V.Children, Offset);
            if not Child.Valid then return False; end if;
            declare
               Pair : constant E.View := E.Decode
                 (Data, C.Part (V.Children, Child.First, Child.After), E.Finalization);
               Key : constant E.Span := E.Array_Element (Data, Pair.Children, 0);
               Name : constant String := Text (Data, Key);
               Value : constant E.Span := E.Array_Element (Data, Pair.Children, 1);
               Other : constant E.Span := Reduced_Field (Name);
            begin
               if not Omitted (Name, Mode) then
                  if Mode = Requirement_Body and then Name = "policy" then
                     if not Policy_Coercion (Data, Value, Other) then return False; end if;
                  elsif not A.Same_Encoding (Data, Value, Other) then return False;
                  end if;
                  Kept := Kept + 1;
               end if;
            end;
            Offset := Child.After;
            if Offset < V.Children.Length - 1 then Offset := Offset + 1; end if;
         end loop;
         --  requirement_hash supplies policy={} even when the original omitted it.
         if Mode = Requirement_Body and then F (Data, Original, "policy").Length = 0 then
            declare
               Policy_Value : constant E.Span := Reduced_Field ("policy");
            begin
               if not Object (Data, Policy_Value) or else
                 E.Array_Length (Data, E.Decode (Data, Policy_Value, E.Operation).Children) /= 0
               then return False; end if;
            end;
            Kept := Kept + 1;
         end if;
      end;
      return E.Array_Length (Data, R.Children) = Kept;
   end Projected;

   function Hash_Matches (Data : E.Bytes; JSON, Claimed : E.Span; Domain : String) return Boolean is
      V : constant E.View := E.Decode (Data, JSON, E.Operation);
      State : SHA.Context := SHA.Initial;
      Buffer : Attest.Byte_Array (0 .. SHA.Block_Bytes - 1) := (others => 0);
      Fill : Natural := 0;
      Digest : Worldline.Hash;
      Hexes : constant String := "0123456789abcdef";
      Identity : String (1 .. 71) := "sha256:" & String'(1 .. 64 => '0');
      procedure Feed (Value : Natural) is
      begin
         pragma Assert (Fill < Buffer'Length);
         pragma Assert (Value <= Natural (Attest.Byte'Last));
         Buffer (Fill) := Attest.Byte (Value);
         Fill := Fill + 1;
         if Fill = Buffer'Length then
            pragma Assert (SHA.Absorbed (State) <= SHA.Max_Message_Bytes -
              Interfaces.Unsigned_64 (Buffer'Length));
            SHA.Update (State, Buffer);
            Fill := 0;
         end if;
      end Feed;
   begin
      if V.Form not in E.Bytes_Value | E.Text_Value or else not E.Bytes_Valid (Data, V.Payload) then return False; end if;
      for Ch of Domain loop Feed (Character'Pos (Ch)); end loop;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, V.Payload);
      begin
         for B of Raw loop Feed (Natural (B)); end loop;
      end;
      pragma Assert (SHA.Absorbed (State) <= SHA.Max_Message_Bytes -
        Interfaces.Unsigned_64 (Fill));
      if Fill > 0 then SHA.Update (State, Buffer (0 .. Fill - 1)); end if;
      Digest := SHA.Final (State);
      for I in Digest'Range loop
         Identity (8 + (I - Digest'First) * 2) := Hexes (Integer (Digest (I)) / 16 + 1);
         Identity (9 + (I - Digest'First) * 2) := Hexes (Integer (Digest (I)) mod 16 + 1);
      end loop;
      return Is_Text (Data, Claimed, Identity);
   end Hash_Matches;

   function Requirement_Valid (Data : E.Bytes; Value, Reduced, JSON : E.Span) return Boolean is
     (Projected (Data, Value, Reduced, Requirement_Body)
      and then JSON_Matches (Data, JSON, Reduced)
      and then Hash_Matches (Data, JSON, F (Data, Value, "requirementHash"), "worldline-validation-v1"));

   function Last_Verifier (Data : E.Bytes; Items, Target : E.Span) return E.Span is
      Result : E.Span := (1, 0);
      N : constant E.Count := List_Length (Data, Items);
   begin
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               Item : constant E.Span := Element (Data, Items, I);
            begin
               if A.Same_Encoding (Data, F (Data, Item, "rootKey"), F (Data, Target, "rootKey"))
                 and then A.Same_Encoding (Data, F (Data, Item, "path"), F (Data, Target, "path"))
               then Result := Item; end if;
            end;
         end loop;
      end if;
      return Result;
   end Last_Verifier;

   function Verifiers_Unchanged (Data : E.Bytes; Context : E.Span) return Boolean is
      Requirement : constant E.Span := F (Data, Context, "requirement");
      Expected : constant E.Span := F (Data, Requirement, "verifiers");
      Actual : constant E.Span := F (Data, Context, "candidateVerifiers");
      N : E.Count := List_Length (Data, Expected);
   begin
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               Item : constant E.Span := Element (Data, Expected, I);
               E_Last : constant E.Span := Last_Verifier (Data, Expected, Item);
               A_Last : constant E.Span := Last_Verifier (Data, Actual, Item);
            begin
               if not A.Same_Encoding (Data, F (Data, E_Last, "sha256"), F (Data, A_Last, "sha256"))
               then return False; end if;
            end;
         end loop;
      end if;
      N := List_Length (Data, Actual);
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            if Last_Verifier (Data, Expected, Element (Data, Actual, I)).Length = 0 then return False; end if;
         end loop;
      end if;
      return True;
   end Verifiers_Unchanged;

   --  This is the existing freshness query roster, not an archive/tree limit.
   --  Validate the complete request once, including every unrequested field,
   --  then select the same original spans in one forward child walk.
   type Freshness_Request_Field is
     (Context_Field, Current_Field, Context_Body_Field, Requirement_Body_Field,
      Current_Body_Field, Context_JSON_Field, Requirement_JSON_Field,
      Current_JSON_Field);
   type Freshness_Request_Fields is
     array (Freshness_Request_Field) of E.Span;

   procedure Read_Freshness_Request
     (Data : E.Bytes; Request : E.Span; Result : out Freshness_Request_Fields)
     with Global => null, Depends => (Result => (Data, Request));
   procedure Read_Freshness_Request
     (Data : E.Bytes; Request : E.Span; Result : out Freshness_Request_Fields)
   is
      V : constant E.View := E.Decode (Data, Request, E.Operation);
      Offset : E.Count := 1;
      Whole, Child : C.Node;
   begin
      Result := (others => (1, 0));
      if V.Form not in E.Object_Value | E.Record_Value or else
        not A.Valid (Data, Request) then return; end if;
      Whole := C.Prefix (Data, V.Children, 0);
      if not Whole.Valid or else Whole.Form /= C.Array_Value or else
        Whole.After /= V.Children.Length or else V.Children.Length < 2
      then return; end if;
      while Offset < V.Children.Length - 1 loop
         pragma Loop_Invariant (Offset in 1 .. V.Children.Length);
         pragma Loop_Variant (Decreases => V.Children.Length - Offset);
         Child := C.Prefix (Data, V.Children, Offset);
         if not Child.Valid then
            Result := (others => (1, 0));
            return;
         end if;
         declare
            Pair : constant E.View := E.Decode
              (Data, C.Part (V.Children, Child.First, Child.After), E.Finalization);
            Key : E.View;
            Value : E.Span;
            Matches : Boolean;
         begin
            if Pair.Form /= E.List_Value or else
              E.Array_Length (Data, Pair.Children) /= 2 then
               Result := (others => (1, 0));
               return;
            end if;
            --  F uses finalization keys for records; A.Field uses operation
            --  keys for objects. In both cases Text_Is rejects byte keys.
            if V.Form = E.Record_Value then
               Key := E.Decode
                 (Data, E.Array_Element (Data, Pair.Children, 0), E.Finalization);
            else
               Key := E.Decode
                 (Data, E.Array_Element (Data, Pair.Children, 0), E.Operation);
            end if;
            Value := E.Array_Element (Data, Pair.Children, 1);
            for Field in Freshness_Request_Field loop
               if Result (Field).Length = 0 then
                  case Field is
                     when Context_Field =>
                        Matches := E.Text_Is (Data, Key, "context");
                     when Current_Field =>
                        Matches := E.Text_Is (Data, Key, "current");
                     when Context_Body_Field =>
                        Matches := E.Text_Is (Data, Key, "contextBody");
                     when Requirement_Body_Field =>
                        Matches := E.Text_Is (Data, Key, "requirementBody");
                     when Current_Body_Field =>
                        Matches := E.Text_Is (Data, Key, "currentBody");
                     when Context_JSON_Field =>
                        Matches := E.Text_Is (Data, Key, "contextJSON");
                     when Requirement_JSON_Field =>
                        Matches := E.Text_Is (Data, Key, "requirementJSON");
                     when Current_JSON_Field =>
                        Matches := E.Text_Is (Data, Key, "currentJSON");
                  end case;
                  if Matches then Result (Field) := Value; end if;
               end if;
            end loop;
         end;
         Offset := Child.After;
         if Offset < V.Children.Length - 1 then Offset := Offset + 1; end if;
      end loop;
   end Read_Freshness_Request;

   function Freshness (Data : E.Bytes; Request : E.Span) return Code is
      Fields : Freshness_Request_Fields;
   begin
      Read_Freshness_Request (Data, Request, Fields);
      declare
         Context : constant E.Span := Fields (Context_Field);
         Current : constant E.Span := Fields (Current_Field);
         Reduced : constant E.Span := Fields (Context_Body_Field);
         Requirement : constant E.Span := F (Data, Context, "requirement");
         Expected : constant E.Span := Fields (Requirement_Body_Field);
         Actual : constant E.Span := Fields (Current_Body_Field);
      begin
         if Null_Or_Missing (Data, Context) then return Context_Missing; end if;
         if not Object (Data, Context) or else not Schema_One (Data, F (Data, Context, "schemaVersion"))
           or else not Projected (Data, Context, Reduced, Context_Body)
           or else not JSON_Matches (Data, Fields (Context_JSON_Field), Reduced)
           or else not Hash_Matches (Data, Fields (Context_JSON_Field), F (Data, Context, "contextHash"), "worldline-validation-v1")
           or else not Requirement_Valid (Data, Requirement, Expected, Fields (Requirement_JSON_Field))
           or else not A.Same_Encoding (Data, F (Data, Context, "requirementHash"), F (Data, Requirement, "requirementHash"))
         then return Context_Invalid; end if;
         --  Recompute both verifier maps. The saved modified list is diagnostic.
         if not Verifiers_Unchanged (Data, Context) then return Verifier_Modified; end if;
         if not Requirement_Valid (Data, Current, Actual, Fields (Current_JSON_Field)) then return Context_Invalid; end if;
         if not A.Same_Encoding (Data, F (Data, Requirement, "requirementHash"), F (Data, Current, "requirementHash"))
         then return Evidence_Stale; end if;
         return Accepted;
      end;
   end Freshness;

   function Payload_Same (Left_Data : E.Bytes; Left : E.Byte_View;
                          Right_Data : E.Bytes; Right : E.Byte_View) return Boolean is
   begin
      if not E.Bytes_Valid (Left_Data, Left) or else not E.Bytes_Valid (Right_Data, Right) then return False; end if;
      return E.Materialize (Left_Data, Left) = E.Materialize (Right_Data, Right);
   end Payload_Same;

   function View_Text (Data : E.Bytes; Item : E.View) return String is
   begin
      if Item.Form /= E.Text_Value or else not E.Bytes_Valid (Data, Item.Payload) then return ""; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, Item.Payload);
         Result : String (1 .. Raw'Length);
      begin
         for I in Result'Range loop Result (I) := Character'Val (Raw (Raw'First + E.Count (I - 1))); end loop;
         return Result;
      end;
   end View_Text;

   --  Exact producer JSON lifting: byte leaves are canonical base64 envelopes,
   --  tuple/list children remain ordered, and every object field is retained.
   function Lift_Matches (Source_Data : E.Bytes; Source : E.Span; Layer : E.Layer;
                          Data : E.Bytes; Normal : E.Span; Legacy : Boolean := False)
      return Boolean with Global => null,
        Subprogram_Variant => (Decreases => Source.Length);
   function Lift_Matches (Source_Data : E.Bytes; Source : E.Span; Layer : E.Layer;
                          Data : E.Bytes; Normal : E.Span; Legacy : Boolean := False)
      return Boolean
   is
      V : constant E.View := E.Decode (Source_Data, Source, Layer);
      R : constant E.View := E.Decode (Data, Normal, E.Operation);
      N : E.Count;
   begin
      if V.Form = E.Invalid or else R.Form = E.Invalid then return False; end if;
      if V.Form = E.Bytes_Value then
         if R.Form /= E.Object_Value or else E.Array_Length (Data, R.Children) /= 2
           or else not Is_Text (Data, F (Data, Normal, "encoding"), "base64")
         then return False; end if;
         declare
            B64 : constant E.View := E.Decode (Data, F (Data, Normal, "payload"), E.Operation);
         begin
            if B64.Form /= E.Text_Value or else not E.Bytes_Valid (Data, B64.Payload)
              or else not E.Bytes_Valid (Source_Data, V.Payload) then return False; end if;
            declare
               Encoded : constant E.Bytes := E.Materialize (Data, B64.Payload);
               Raw : constant E.Bytes := E.Materialize (Source_Data, V.Payload);
               S : constant Worldline.Archive_Base64.Span := (Encoded'First, Encoded'Length);
            begin
               return Worldline.Archive_Base64.Canonical (Encoded, S)
                 and then Worldline.Archive_Base64.Decoded_Length (Encoded, S) = Raw'Length
                 and then (for all I in Raw'Range =>
                   Raw (I) = Worldline.Archive_Base64.Decoded_Byte (Encoded, S, I - Raw'First));
            end;
         end;
      elsif V.Form in E.List_Value | E.Tuple_Value then
         if R.Form /= E.List_Value then return False; end if;
         N := E.Array_Length (Source_Data, V.Children);
         if E.Array_Length (Data, R.Children) /= N then return False; end if;
         if N > 0 then
            for I in E.Count range 0 .. N - 1 loop
               declare
                  Child : constant E.Span := E.Array_Element (Source_Data, V.Children, I);
               begin
                  if Child.Length >= Source.Length or else not Lift_Matches
                    (Source_Data, Child, Layer, Data, E.Array_Element (Data, R.Children, I))
                  then return False; end if;
               end;
            end loop;
         end if;
         return True;
      elsif V.Form = E.Object_Value then
         if R.Form /= E.Object_Value or else Layer = E.Terminal then return False; end if;
         N := E.Array_Length (Source_Data, V.Children);
         if E.Array_Length (Data, R.Children) /= N + (if Legacy then 1 else 0) then return False; end if;
         if N > 0 then
            for I in E.Count range 0 .. N - 1 loop
               declare
                  Pair : constant E.View := E.Decode
                    (Source_Data, E.Array_Element (Source_Data, V.Children, I), E.Layer'Pred (Layer));
                  Key : constant E.View := E.Decode (Source_Data,
                    E.Array_Element (Source_Data, Pair.Children, 0),
                    (if Layer = E.Operation then E.Operation else E.Terminal));
                  Child : constant E.Span := E.Array_Element (Source_Data, Pair.Children, 1);
               begin
                  if Key.Form /= E.Text_Value or else Child.Length >= Source.Length
                    or else not Lift_Matches (Source_Data, Child, Layer, Data, F (Data, Normal, View_Text (Source_Data, Key)))
                  then return False; end if;
               end;
            end loop;
         end if;
         return not Legacy or else Is_Text (Data, F (Data, Normal, "origin"), "agent");
      elsif V.Form /= R.Form then return False;
      elsif V.Form = E.Null_Value then return True;
      elsif V.Form = E.Boolean_Value then return V.Boolean_Bit = R.Boolean_Bit;
      elsif V.Form in E.Text_Value | E.Integer_Value | E.Float_Value then
         return V.Sign = R.Sign and then Payload_Same (Source_Data, V.Payload, Data, R.Payload);
      end if;
      return False;
   end Lift_Matches;

   function Acquisitions_Match (Data : E.Bytes; Original, Normal : E.Span) return Boolean is
      V : constant E.View := E.Decode (Data, Original, E.Operation);
   begin
      if Original.Length = 0 or else V.Form = E.Null_Value then return Null_Or_Missing (Data, Normal); end if;
      if V.Form = E.List_Value then return Lift_Matches (Data, Original, E.Operation, Data, Normal); end if;
      if not Object (Data, Original) or else E.Array_Length (Data, V.Children) /= 2
        or else not Is_Text (Data, F (Data, Original, "encoding"), "worldline-finalization-acquisitions-v1")
      then return False; end if;
      declare
         Payload : constant E.View := E.Decode (Data, F (Data, Original, "payload"), E.Operation);
      begin
         if Payload.Form /= E.Text_Value or else not E.Bytes_Valid (Data, Payload.Payload) then return False; end if;
         declare
            Encoded : constant E.Bytes := E.Materialize (Data, Payload.Payload);
            S : constant Worldline.Archive_Base64.Span := (Encoded'First, Encoded'Length);
         begin
            if not Worldline.Archive_Base64.Canonical (Encoded, S) then return False; end if;
            declare
               Raw : E.Bytes (1 .. Worldline.Archive_Base64.Decoded_Length (Encoded, S));
            begin
               Worldline.Archive_Base64.Decode (Encoded, S, Raw);
               return E.Decode (Raw, (Raw'First, Raw'Length), E.Finalization).Form = E.List_Value
                 and then Lift_Matches (Raw, (Raw'First, Raw'Length), E.Finalization, Data, Normal);
            end;
         end;
      end;
   end Acquisitions_Match;

   function Legacy_Agent (Data : E.Bytes; Row : E.Span) return Boolean is
     (Object (Data, Row) and then Is_Text (Data, F (Data, Row, "id"), "agent")
      and then F (Data, Row, "origin").Length = 0
      and then Is_Text (Data, F (Data, Row, "kind"), "build")
      and then Is_Text (Data, F (Data, Row, "format"), "exit")
      and then F (Data, Row, "resultChannel").Length = 0
      and then F (Data, Row, "executedVerifierSet").Length = 0
      and then Object (Data, F (Data, Row, "supervision"))
      and then F (Data, Row, "rawEventHash").Length /= 0);

   function Native_Row (Data : E.Bytes; Row : E.Span; Declaration : String;
                        Agent : Boolean := False) return Boolean
   is
      Source : constant E.Span := F (Data, Row, "source");
      Normal : constant E.Span := F (Data, Row, "normal");
      Expected : constant E.Span := F (Data, Row, "expected");
      Observed : constant E.Span := F (Data, Row, "observed");
   begin
      if not Lift_Matches (Data, Source, E.Operation, Data, Normal, Agent and then Legacy_Agent (Data, Source))
        or else not JSON_Matches (Data, F (Data, Row, "recordJSON"), Normal)
        or else (if F (Data, Source, "engineInvocationObservation").Length = 0
                 then not Null_Or_Missing (Data, Expected)
                 else not Lift_Matches (Data, F (Data, Source, "engineInvocationObservation"), E.Operation, Data, Expected))
        or else not Acquisitions_Match (Data, F (Data, Source, "engineRawObservations"), Observed)
        or else not JSON_Matches (Data, F (Data, Row, "expectedJSON"), Expected)
        or else not JSON_Matches (Data, F (Data, Row, "observedJSON"), Observed)
      then return False; end if;
      declare
         Derived : constant Producer.Produced_Record := Producer.Derive
           (Byte_String (Data, F (Data, Row, "expectedJSON")),
            Byte_String (Data, F (Data, Row, "observedJSON")),
            Byte_String (Data, F (Data, Row, "recordJSON")), Declaration);
      begin
         return W.Confined_Admit_Wire (Derived.Raw, W.Byte (Producer.R.Confinement_Observation'Pos (Derived.Confinement))) = 1;
      end;
   end Native_Row;

   function Last_Row (Data : E.Bytes; Rows : E.Span; Check : String) return E.Span is
      N : constant E.Count := List_Length (Data, Rows);
      Result : E.Span := (1, 0);
   begin
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               Row : constant E.Span := Element (Data, Rows, I);
            begin
               if Is_Text (Data, F (Data, F (Data, Row, "source"), "id"), Check) then Result := Row; end if;
            end;
         end loop;
      end if;
      return Result;
   end Last_Row;

   function Bundle_Matches (Data : E.Bytes; Requirement, Row : E.Span; Check : String) return Boolean is
      Expected : constant E.Span := F (Data, Requirement, "verifiers");
      Actual : constant E.Span := F (Data, F (Data, Row, "executedVerifierSet"), "members");
      N : constant E.Count := List_Length (Data, Expected);
      Counted : E.Count := 0;
   begin
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               Item : constant E.Span := Element (Data, Expected, I);
               Found : Boolean := False;
               M : constant E.Count := List_Length (Data, Actual);
            begin
               if Is_Text (Data, F (Data, Item, "checkId"), Check) then
                  Counted := Counted + 1;
                  if M > 0 then
                     for J in E.Count range 0 .. M - 1 loop
                        declare
                           Member : constant E.Span := Element (Data, Actual, J);
                        begin
                           if A.Same_Encoding (Data, F (Data, Item, "rootKey"), F (Data, Member, "rootKey"))
                             and then A.Same_Encoding (Data, F (Data, Item, "path"), F (Data, Member, "path"))
                             and then A.Same_Encoding (Data, F (Data, Item, "sha256"), F (Data, Member, "sha256"))
                           then Found := True; end if;
                        end;
                     end loop;
                  end if;
                  if not Found then return False; end if;
               end if;
            end;
         end loop;
      end if;
      return List_Length (Data, Actual) = Counted;
   end Bundle_Matches;

   function Execution (Data : E.Bytes; Request : E.Span) return Code is
      Requirement : constant E.Span := F (Data, Request, "current");
      JSON : constant E.Span := F (Data, Request, "currentJSON");
      Rows : constant E.Span := F (Data, Request, "rows");
      Agent : constant E.Span := F (Data, Request, "agent");
      --  Execution consumes full finalization evidence. Subject/root identities
      --  remain operands of the original history, context and collapse joins.
      Evidence : constant E.Span := F (Data, Request, "finalizationEvidence");
      Finalization : constant E.Span := F (Data, Evidence, "checks");
      N : constant E.Count := List_Length (Data, Finalization);
      First_Agent : E.Span := (1, 0);
   begin
      if not JSON_Matches (Data, JSON, Requirement) then return Invalid_Request; end if;
      declare
         Selected : constant E.Span := F (Data, Request, "selectedRows");
         M : constant E.Count := List_Length (Data, Selected);
      begin
         if List_Length (Data, Rows) /= M then return Invalid_Request; end if;
         if M > 0 then
            for I in E.Count range 0 .. M - 1 loop
               if not A.Same_Encoding (Data, Element (Data, Selected, I),
                 F (Data, Element (Data, Rows, I), "source")) then return Invalid_Request; end if;
            end loop;
         end if;
      end;
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               Row : constant E.Span := Element (Data, Finalization, I);
            begin
               if Is_Text (Data, F (Data, Row, "id"), "agent") then First_Agent := Row; exit; end if;
            end;
         end loop;
      end if;
      if not A.Same_Encoding (Data, First_Agent, F (Data, Agent, "source"))
        or else not Native_Row (Data, Agent, "{""format"":""exit"",""profile"":null,""bundle_declared"":false,""origin"":""agent""}", True)
      then return Roster_Incomplete; end if;
      declare
         Policy_JSON : constant String := Byte_String (Data, JSON);
         Required : constant Natural := Policy.Required_Count (Policy_JSON);
      begin
         if Required = 0 and then not Policy.Empty_Declared (Policy_JSON) then return Roster_Incomplete; end if;
         if Required > 0 then
            for I in Natural range 0 .. Required - 1 loop
               declare
                  Check : constant String := Policy.Required (Policy_JSON, I);
                  Row : constant E.Span := Last_Row (Data, Rows, Check);
               begin
                  if Row.Length = 0 or else not Native_Row (Data, Row, Policy.Declaration (Policy_JSON, Check))
                    or else not Bundle_Matches (Data, Requirement, F (Data, Row, "source"), Check)
                  then return Roster_Incomplete; end if;
               end;
            end loop;
         end if;
      end;
      return Accepted;
   end Execution;

   function Record_Matches (Data : E.Bytes; Request : E.Span) return Code is
      Row : constant E.Span := F (Data, Request, "row");
      Value : constant E.Span := F (Data, Request, "record");
      Expected : constant E.Span := F (Data, Request, "expected");
   begin
      if not Object (Data, Value) or else not Schema_One (Data, F (Data, Value, "schemaVersion"))
        or else not A.Same_Encoding (Data, F (Data, Value, "transactionId"), Expected)
      then return Record_Invalid; end if;
      if Is_Text (Data, F (Data, Request, "relation"), "record-identity") then return Accepted; end if;
      if not A.Same_Encoding (Data, F (Data, Row, "state"), F (Data, Value, "state")) then return Record_Invalid; end if;
      --  Constructor fixtures with the original two-column profile still work;
      --  a real SQLite row independently binds every column it actually carries.
      declare
         Names : constant array (Positive range 1 .. 11) of E.Span :=
           [F (Data, Row, "transaction_id"), F (Data, Row, "kind"),
            F (Data, Row, "candidate_world"), F (Data, Row, "before_root"),
            F (Data, Row, "base_root"), F (Data, Row, "candidate_root"),
            F (Data, Row, "delta_hash"), F (Data, Row, "root_set_hash"),
            F (Data, Row, "generation_marker"), F (Data, Row, "created_at"),
            F (Data, Row, "prepared_path")];
         Other : constant array (Positive range 1 .. 11) of E.Span :=
           [F (Data, Value, "transactionId"), F (Data, Value, "kind"),
            F (Data, Value, "candidateWorld"), F (Data, Value, "beforeRoot"),
            F (Data, Value, "baseRoot"), F (Data, Value, "candidateRoot"),
            F (Data, Value, "deltaHash"), F (Data, Value, "rootSetHash"),
            F (Data, Value, "generationMarker"), F (Data, Value, "createdAt"),
            F (Data, Value, "preparedPath")];
      begin
         for I in Names'Range loop
            if Names (I).Length /= 0 and then not A.Same_Encoding (Data, Names (I), Other (I)) then return Record_Invalid; end if;
         end loop;
      end;
      if F (Data, Row, "staged_root").Length /= 0 then
         if Null_Or_Missing (Data, F (Data, Value, "stagedRoot")) then
            if not Is_Text (Data, F (Data, Row, "staged_root"), "absent") then return Record_Invalid; end if;
         elsif not A.Same_Encoding (Data, F (Data, Row, "staged_root"), F (Data, Value, "stagedRoot")) then return Record_Invalid;
         end if;
      end if;
      return Accepted;
   end Record_Matches;

   function Manifest_Set (Data : E.Bytes; Items, Root_Set, Root_JSON, Expected : E.Span)
      return Boolean
   is
      N : constant E.Count := List_Length (Data, Items);
   begin
      if List_Length (Data, Root_Set) /= N or else not JSON_Matches (Data, Root_JSON, Root_Set) then return False; end if;
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               Item : constant E.Span := Element (Data, Items, I);
               Value : constant E.Span := F (Data, Item, "value");
               Root : constant E.Span := F (Data, Item, "rootHash");
               Member : constant E.Span := Element (Data, Root_Set, I);
            begin
               if not JSON_Matches (Data, F (Data, Item, "canonical"), Value)
                 or else not Hash_Matches (Data, F (Data, Item, "canonical"), Root, "worldline-manifest-v1")
                 or else not A.Same_Encoding (Data, F (Data, Item, "rootKey"), F (Data, Value, "rootKey"))
                 or else not A.Same_Encoding (Data, F (Data, Member, "rootKey"), F (Data, Value, "rootKey"))
                 or else not A.Same_Encoding (Data, F (Data, Member, "manifestRoot"), Root)
               then return False; end if;
               if I > 0 and then Text (Data, F (Data, Element (Data, Root_Set, I - 1), "rootKey")) >=
                 Text (Data, F (Data, Member, "rootKey")) then return False; end if;
            end;
         end loop;
      end if;
      return Hash_Matches (Data, Root_JSON, Expected, "worldline-root-manifests-v1");
   end Manifest_Set;

   function Historical_Match (Data : E.Bytes; Saved, Current : E.Span) return Boolean is
      N : constant E.Count := List_Length (Data, Saved);
   begin
      if Null_Or_Missing (Data, Saved) then return True; end if;
      if List_Length (Data, Current) /= N then return False; end if;
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               Before : constant E.Span := Element (Data, Saved, I);
               After : constant E.Span := Element (Data, Current, I);
            begin
               if not A.Same_Encoding (Data, F (Data, Before, "rootKey"), F (Data, After, "rootKey"))
                 or else not A.Same_Encoding (Data, F (Data, Before, "rootHash"), F (Data, After, "rootHash"))
                 or else not A.Same_Encoding (Data, F (Data, Before, "canonical"), F (Data, After, "canonical"))
                 or else not JSON_Matches (Data, F (Data, Before, "canonical"), F (Data, Before, "value"))
                 or else not JSON_Matches (Data, F (Data, After, "canonical"), F (Data, After, "value"))
               then return False; end if;
            end;
         end loop;
      end if;
      return True;
   end Historical_Match;

   function Manifests (Data : E.Bytes; Request : E.Span) return Code is
      Record_Value : constant E.Span := F (Data, Request, "record");
      Expected : constant E.Span := F (Data, Record_Value, "stagedRoot");
      Live : constant E.Span := F (Data, Request, "live");
      Retained : constant E.Span := F (Data, Request, "retained");
   begin
      if Manifest_Set (Data, Live, F (Data, Request, "liveRootSet"), F (Data, Request, "liveRootJSON"), Expected)
      then return Live_Manifests; end if;
      if Null_Or_Missing (Data, Retained) then return Staged_Mismatch; end if;
      if Manifest_Set (Data, Retained, F (Data, Request, "retainedRootSet"), F (Data, Request, "retainedRootJSON"), Expected)
        and then Historical_Match (Data, F (Data, Record_Value, "stagedManifestRecords"), F (Data, Request, "retainedFrozen"))
      then return Historical_Manifests; end if;
      return Staged_Mismatch;
   end Manifests;

   function Marker_State (Data : E.Bytes; Request : E.Span) return Code is
      Expected : constant E.Span := F (Data, Request, "expected");
      Live : constant E.Span := F (Data, Request, "live");
      Prepared : constant E.Span := F (Data, Request, "prepared");
   begin
      if A.Same_Encoding (Data, Expected, Live) and then not A.Same_Encoding (Data, Expected, Prepared) then return Finish_Committed; end if;
      if not A.Same_Encoding (Data, Expected, Live) and then A.Same_Encoding (Data, Expected, Prepared) then return Abort_Prepared; end if;
      return Ambiguous;
   end Marker_State;

   function Decide (Data : E.Bytes; Request : E.Span) return Code is
   begin
      if not Object (Data, Request) then return Invalid_Request; end if;
      if Is_Text (Data, F (Data, Request, "relation"), "freshness") then return Freshness (Data, Request);
      elsif Is_Text (Data, F (Data, Request, "relation"), "execution") then return Execution (Data, Request);
      elsif Is_Text (Data, F (Data, Request, "relation"), "record") or else
        Is_Text (Data, F (Data, Request, "relation"), "record-identity") then return Record_Matches (Data, Request);
      elsif Is_Text (Data, F (Data, Request, "relation"), "manifests") then return Manifests (Data, Request);
      elsif Is_Text (Data, F (Data, Request, "relation"), "marker") then return Marker_State (Data, Request);
      elsif Is_Text (Data, F (Data, Request, "relation"), "committed") then
         return (if Committed_Result_Matches (Data, F (Data, Request, "original"),
           F (Data, Request, "actual"), F (Data, Request, "result"),
           F (Data, Request, "chains"), F (Data, Request, "authority")) then Accepted else Record_Invalid);
      elsif Is_Text (Data, F (Data, Request, "relation"), "verifiers") then
         return (if Verifiers_Unchanged (Data, F (Data, Request, "context")) then Accepted else Verifier_Modified);
      elsif Is_Text (Data, F (Data, Request, "relation"), "marker-value") then
         declare
            Marker : constant E.Span := F (Data, Request, "marker");
         begin
            return (if Object (Data, Marker) and then Schema_One (Data, F (Data, Marker, "schemaVersion"))
              and then E.Decode (Data, F (Data, Marker, "transactionId"), E.Operation).Form = E.Text_Value
              then Accepted else Record_Invalid);
         end;
      end if;
      return Invalid_Request;
   end Decide;
   function Hash_Text (Value, Domain : String; Prefix : String := "sha256:") return String is
      State : SHA.Context := SHA.Initial;
      Buffer : Attest.Byte_Array (0 .. SHA.Block_Bytes - 1) := (others => 0);
      Fill : Natural := 0;
      Hexes : constant String := "0123456789abcdef";
      Digest : Worldline.Hash;
      Answer : String (1 .. Prefix'Length + 64);
      procedure Feed (Ch : Character) is
      begin
         Buffer (Fill) := Character'Pos (Ch); Fill := Fill + 1;
         if Fill = Buffer'Length then SHA.Update (State, Buffer); Fill := 0; end if;
      end Feed;
   begin
      for Ch of Domain loop Feed (Ch); end loop;
      for Ch of Value loop Feed (Ch); end loop;
      if Fill > 0 then SHA.Update (State, Buffer (0 .. Fill - 1)); end if;
      Digest := SHA.Final (State);
      Answer (1 .. Prefix'Length) := Prefix;
      for X in Digest'Range loop
         Answer (Prefix'Length + 1 + (X - Digest'First) * 2) := Hexes (Natural (Digest (X)) / 16 + 1);
         Answer (Prefix'Length + 2 + (X - Digest'First) * 2) := Hexes (Natural (Digest (X)) mod 16 + 1);
      end loop;
      return Answer;
   end Hash_Text;

   function Same_Value (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (Left.Length > 0 and then Right.Length > 0
      and then A.Same_Encoding (Data, Left, Right));
   function Get_Same (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     ((Null_Or_Missing (Data, Left) and then Null_Or_Missing (Data, Right))
      or else Same_Value (Data, Left, Right));
   function Nibble (Ch : Character) return Integer is
     (if Ch in '0' .. '9' then Character'Pos (Ch) - Character'Pos ('0')
      elsif Ch in 'a' .. 'f' then Character'Pos (Ch) - Character'Pos ('a') + 10 else -1);
   function Hex_Valid (Value : String) return Boolean is
     (Value'Length > 0 and then Value'Length mod 2 = 0 and then
      (for all Ch of Value => Nibble (Ch) >= 0));
   function Hex_Bytes (Value : String) return E.Bytes is
      Answer : E.Bytes (1 .. E.Count (Value'Length / 2));
   begin
      if not Hex_Valid (Value) then return (1 .. 0 => 0); end if;
      for X in Answer'Range loop
         Answer (X) := E.Q.Byte (Nibble (Value (Value'First + Natural (X - 1) * 2)) * 16
           + Nibble (Value (Value'First + Natural (X - 1) * 2 + 1)));
      end loop;
      return Answer;
   end Hex_Bytes;
   -- Exact retained archive correspondence is not Python object equality.
   -- Binary64 bits do not recreate historical NaN object identity.
   function Cross_Value (Left_Data, Right_Data : E.Bytes; Left, Right : E.Span;
                         Left_Layer : E.Layer := E.Operation) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Left.Length);
   function Cross_Value (Left_Data, Right_Data : E.Bytes; Left, Right : E.Span;
                         Left_Layer : E.Layer := E.Operation) return Boolean is
      L : constant E.View := E.Decode (Left_Data, Left, Left_Layer);
      V : constant E.View := E.Decode (Right_Data, Right, E.Operation);
      Count : constant E.Count := E.Array_Length (Left_Data, L.Children);
   begin
      if Left.Length = 0 or else Right.Length = 0 or else L.Form = E.Invalid or else L.Form /= V.Form then return False; end if;
      case L.Form is
         when E.Null_Value => return True;
         when E.Boolean_Value => return L.Boolean_Bit = V.Boolean_Bit;
         when E.Text_Value | E.Bytes_Value | E.Integer_Value | E.Float_Value | E.World_State_Value =>
            return L.Sign = V.Sign and then Payload_Same (Left_Data, L.Payload, Right_Data, V.Payload);
         when E.List_Value | E.Tuple_Value =>
            if Count /= E.Array_Length (Right_Data, V.Children) then return False; end if;
            for I in E.Count range 1 .. Count loop
               declare Child : constant E.Span := E.Array_Element (Left_Data, L.Children, I - 1); begin
                  if Child.Length >= Left.Length or else not Cross_Value (Left_Data, Right_Data, Child,
                    E.Array_Element (Right_Data, V.Children, I - 1), Left_Layer) then return False; end if;
               end;
            end loop;
            return True;
         when E.Object_Value | E.Record_Value =>
            if Count /= E.Array_Length (Right_Data, V.Children) then return False; end if;
            if L.Form = E.Record_Value and then
              (not Payload_Same (Left_Data, L.Module_Name, Right_Data, V.Module_Name)
               or else not Payload_Same (Left_Data, L.Record_Name, Right_Data, V.Record_Name)) then return False; end if;
            for I in E.Count range 1 .. Count loop
               declare Pair : constant E.View := E.Decode (Left_Data, E.Array_Element (Left_Data, L.Children, I - 1), E.Finalization);
                  Key : constant E.View := E.Decode (Left_Data, E.Array_Element (Left_Data, Pair.Children, 0),
                    (if L.Form = E.Record_Value then E.Finalization else Left_Layer));
                  Child : constant E.Span := E.Array_Element (Left_Data, Pair.Children, 1);
               begin
                  if Key.Form /= E.Text_Value or else Child.Length >= Left.Length or else
                    not Cross_Value (Left_Data, Right_Data, Child, F (Right_Data, Right, View_Text (Left_Data, Key)), Left_Layer)
                  then return False; end if;
               end;
            end loop;
            return True;
         when others => return False;
      end case;
   end Cross_Value;
   function Packet_Hash (Packet_Data, Data : E.Bytes; Raw, Identity : E.Span) return Boolean is
      V : constant E.View := E.Decode (Packet_Data, Raw, E.Recovery);
      Id : constant String := Text (Data, Identity);
   begin
      if Null_Or_Missing (Data, Identity) then return V.Form = E.Null_Value; end if;
      if V.Form /= E.Bytes_Value or else not E.Bytes_Valid (Packet_Data, V.Payload)
        or else Id'Length /= 71 or else Id (Id'First .. Id'First + 6) /= "sha256:"
      then return False; end if;
      declare B : constant E.Bytes := E.Materialize (Packet_Data, V.Payload); begin
         return B'Length = 32 and then (for all X in B'Range =>
           Nibble (Id (Id'First + 7 + Natural (X - B'First) * 2)) >= 0
           and then Nibble (Id (Id'First + 8 + Natural (X - B'First) * 2)) >= 0
           and then Natural (B (X)) = Nibble (Id (Id'First + 7 + Natural (X - B'First) * 2)) * 16
             + Nibble (Id (Id'First + 8 + Natural (X - B'First) * 2)));
      end;
   end Packet_Hash;

   function Frozen_Manifests (Data : E.Bytes; Record_Value : E.Span) return Boolean is
      Items : constant E.Span := F (Data, Record_Value, "stagedManifestRecords");
      Count : constant E.Count := List_Length (Data, Items);
   begin
      -- Original historical records have no added manifest field. Their
      -- live/retained full manifest selection remains the Manifests relation.
      if Items.Length = 0 then return True; end if;
      if E.Decode (Data, Items, E.Operation).Form /= E.List_Value then return False; end if;
      if Count > 0 then
         for X in E.Count range 0 .. Count - 1 loop
            declare
               Item : constant E.Span := Element (Data, Items, X);
               Encoded : constant E.View := E.Decode (Data, F (Data, Item, "canonical"), E.Operation);
            begin
               if Encoded.Form /= E.Text_Value or else not E.Bytes_Valid (Data, Encoded.Payload)
                 or else not Same_Value (Data, F (Data, Item, "rootKey"), F (Data, F (Data, Item, "value"), "rootKey"))
                 or else not Hash_Matches (Data, F (Data, Item, "canonical"), F (Data, Item, "rootHash"), "worldline-manifest-v1")
               then return False; end if;
               declare Raw : constant E.Bytes := E.Materialize (Data, Encoded.Payload); begin
                  if not C.Operation_Archive_JSON_Matches (Raw, Data, (Raw'First, Raw'Length), F (Data, Item, "value")) then return False; end if;
               end;
               if X > 0 and then Text (Data, F (Data, Element (Data, Items, X - 1), "rootKey")) >= Text (Data, F (Data, Item, "rootKey")) then return False; end if;
            end;
         end loop;
      end if;
      return Is_Text (Data, F (Data, Record_Value, "stagedRoot"),
        Hash_Text (J.Render (Data, Items, Mode => J.Root_Set), "worldline-root-manifests-v1"));
   end Frozen_Manifests;

   function Immutable_Transaction (Data : E.Bytes; Original, Actual : E.Span) return Boolean is
      Before : constant E.View := E.Decode (Data, Original, E.Operation);
      After : constant E.View := E.Decode (Data, Actual, E.Operation);
      function Added (Name : String) return Boolean is
        (Name in "state" | "error" | "committerPeer" | "decisionInputsAtCommit" | "commitRequirementHash" | "commitIntent" | "postFlushPacket");
   begin
      if not Object (Data, Original) or else not Object (Data, Actual)
        or else not Schema_One (Data, F (Data, Original, "schemaVersion"))
        or else not Is_Text (Data, F (Data, Actual, "state"), "COMMITTED")
        or else not Null_Or_Missing (Data, F (Data, Actual, "error"))
        or else not (Is_Text (Data, F (Data, Original, "state"), "PREPARED")
          or else Is_Text (Data, F (Data, Original, "state"), "AUTHORIZED")
          or else Is_Text (Data, F (Data, Original, "state"), "COMMITTED"))
      then return False; end if;
      for X in E.Count range 1 .. E.Array_Length (Data, Before.Children) loop
         declare Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, Before.Children, X - 1), E.Finalization);
            Name : constant String := Text (Data, E.Array_Element (Data, Pair.Children, 0));
         begin
            if not Added (Name) and then not Same_Value (Data, E.Array_Element (Data, Pair.Children, 1), F (Data, Actual, Name)) then return False; end if;
            if Added (Name) and then Name not in "state" | "error"
              and then not Null_Or_Missing (Data, F (Data, Original, Name))
              and then not Same_Value (Data, F (Data, Original, Name), F (Data, Actual, Name))
            then return False; end if;
         end;
      end loop;
      for X in E.Count range 1 .. E.Array_Length (Data, After.Children) loop
         declare Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, After.Children, X - 1), E.Finalization);
            Name : constant String := Text (Data, E.Array_Element (Data, Pair.Children, 0));
         begin
            if not Added (Name) and then F (Data, Original, Name).Length = 0 then return False; end if;
         end;
      end loop;
      declare Intent : constant E.Span := F (Data, Actual, "commitIntent"); begin
         if Null_Or_Missing (Data, Intent) then
            if Is_Text (Data, F (Data, Original, "state"), "PREPARED") then return False; end if;
         elsif not Object (Data, Intent) or else E.Array_Length (Data, E.Decode (Data, Intent, E.Operation).Children) /= 3
           or else not Is_Text (Data, F (Data, Intent, "state"), "COMMITTING")
           or else not Same_Value (Data, F (Data, Intent, "transactionId"), F (Data, Actual, "transactionId"))
           or else not Same_Value (Data, F (Data, Intent, "stagedRoot"), F (Data, Actual, "stagedRoot"))
         then return False; end if;
      end;
      if F (Data, F (Data, Original, "preparerPeer"), "requester").Length > 0
        and then not Same_Value (Data, F (Data, Actual, "committerPeer"), F (Data, F (Data, Original, "preparerPeer"), "requester"))
      then return False; end if;
      return Frozen_Manifests (Data, Actual);
   end Immutable_Transaction;

   function Saved_Roots_Match (Packet_Data, Data : E.Bytes; Roots, Saved : E.Span) return Boolean is
      Count : constant E.Count := E.Array_Length (Packet_Data, E.Decode (Packet_Data, Roots, E.Recovery).Children);
   begin
      if Saved.Length = 0 then return True; end if;
      if E.Decode (Data, Saved, E.Operation).Form /= E.List_Value or else List_Length (Data, Saved) /= Count then return False; end if;
      for I in E.Count range 1 .. Count loop
         declare
            Root : constant E.Span := E.Array_Element (Packet_Data, E.Decode (Packet_Data, Roots, E.Recovery).Children, I - 1);
            Frozen : constant E.Span := Element (Data, Saved, I - 1);
            Fields : constant E.Span := F (Data, Frozen, "record");
            Members : constant E.View := E.Decode (Data, Fields, E.Operation);
         begin
            if not Object (Data, Fields) or else
              J.Render (Packet_Data, R.Field (Packet_Data, Root, "path"), E.Recovery) /=
                "{""encoding"":""base64"",""payload"":" & P.Quote (Text (Data, F (Data, Frozen, "pathB64"))) & "}"
            then return False; end if;
            if E.Array_Length (Packet_Data, E.Decode (Packet_Data, Root, E.Recovery).Children) /=
              E.Array_Length (Data, Members.Children) + 1 then return False; end if;
            for X in E.Count range 1 .. E.Array_Length (Data, Members.Children) loop
               declare Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, Members.Children, X - 1), E.Finalization);
                  Name : constant String := Text (Data, E.Array_Element (Data, Pair.Children, 0));
               begin
                  -- update_root_generation changes these two observations,
                  -- not the root registration. Both complete values stay in
                  -- their independently authenticated historical packets.
                  if R.Field (Packet_Data, Root, Name).Length = 0 or else
                    (Name not in "generation_id" | "manifest_root" and then
                     not Cross_Value (Packet_Data, Data, R.Field (Packet_Data, Root, Name),
                       E.Array_Element (Data, Pair.Children, 1), E.Recovery))
                  then return False; end if;
               end;
            end loop;
         end;
      end loop;
      return True;
   end Saved_Roots_Match;

   function Input_Continuity (Packet_Data, Data : E.Bytes; Inputs, Record_Value : E.Span) return Boolean is
      Saved : constant E.Span := F (Data, Record_Value, "decisionInputs");
      Before : constant E.View := E.Decode (Data, Saved, E.Operation);
      function Refreshed (Name : String) return Boolean is
        (Name in "resultingRequirement" | "expectedSubject" | "foreignWrites" | "watchSets" | "generations" | "absent" | "primary");
   begin
      if not Object (Data, Saved) then return False; end if;
      for I in E.Count range 1 .. E.Array_Length (Data, Before.Children) loop
         declare Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, Before.Children, I - 1), E.Finalization);
            Name : constant String := Text (Data, E.Array_Element (Data, Pair.Children, 0));
            Value : constant E.Span := E.Array_Element (Data, Pair.Children, 1);
            Current : constant E.Span := R.Field (Packet_Data, Inputs, Name);
         begin
            if Name = "primary" and then Object (Data, Value) then
               for X in E.Count range 1 .. E.Array_Length (Data, E.Decode (Data, Value, E.Operation).Children) loop
                  declare Member : constant E.View := E.Decode (Data, E.Array_Element (Data, E.Decode (Data, Value, E.Operation).Children, X - 1), E.Finalization);
                     Key : constant String := Text (Data, E.Array_Element (Data, Member.Children, 0));
                  begin
                     if Key /= "declaredVerifiers" and then not Cross_Value (Packet_Data, Data,
                       R.Field (Packet_Data, Current, Key), E.Array_Element (Data, Member.Children, 1), E.Recovery)
                     then return False; end if;
                  end;
               end loop;
            elsif not Refreshed (Name) and then not Cross_Value (Packet_Data, Data, Current, Value, E.Recovery)
            then return False; end if;
         end;
      end loop;
      return True;
   end Input_Continuity;

   function Packet_Ready
     (Packet_Data, Data : E.Bytes; Actual, Authority : E.Span) return Boolean is
      Seen : Boolean := False;
      function Known_Packet (Source : E.Bytes) return Boolean is
         Post : constant String := Text (Data, F (Data, Actual, "postFlushPacket"));
      begin
         if Hex_Valid (Post) and then Hex_Bytes (Post) = Source then return True; end if;
         for I in E.Count range 1 .. List_Length (Data, Authority) loop
            declare Item : constant E.Span := Element (Data, Authority, I - 1); begin
               if Is_Text (Data, F (Data, Item, "name"), "FULL_PRE_EFFECT_BOUNDARY") then
                  declare Raw : constant String := Text (Data, F (Data, Item, "collapse_packet")); begin
                     if Hex_Valid (Raw) and then Hex_Bytes (Raw) = Source then return True; end if;
                  end;
               end if;
            end;
         end loop;
         return False;
      end Known_Packet;
   begin
      for I in E.Count range 1 .. List_Length (Data, Authority) loop
         declare Item : constant E.Span := Element (Data, Authority, I - 1); begin
            if Is_Text (Data, F (Data, Item, "name"), "RECOVERY_SYNTAX_FACTS_V1") then
               if not Hex_Valid (Text (Data, F (Data, Item, "value"))) then return False; end if;
               declare
                  Facts : constant E.Bytes := Hex_Bytes (Text (Data, F (Data, Item, "value")));
                  Whole : constant E.Span := (Facts'First, Facts'Length);
                  Original : constant E.View := E.Decode (Facts, F (Facts, Whole, "packet"), E.Operation);
                  Capsules : constant E.Span := F (Facts, Whole, "capsules");
               begin
                  if not Object (Facts, Whole) or else E.Array_Length (Facts, E.Decode (Facts, Whole, E.Operation).Children) /= 2
                    or else Original.Form /= E.Bytes_Value or else not E.Bytes_Valid (Facts, Original.Payload)
                    or else E.Decode (Facts, Capsules, E.Operation).Form /= E.List_Value
                  then return False; end if;
                  declare Raw : constant E.Bytes := E.Materialize (Facts, Original.Payload); begin
                     if not Known_Packet (Raw) then return False; end if;
                     if Raw = Packet_Data then
                        Seen := True;
                        -- Complete owns original source/context/role/custody,
                        -- helper/parser/input/output joins. This carrier grants
                        -- nothing and never changes the original packet bytes.
                        if Packet.Complete (Packet_Data, (Packet_Data'First, Packet_Data'Length), Facts, Capsules) /= Packet.Ready
                        then return False; end if;
                     end if;
                  end;
               end;
            end if;
         end;
      end loop;
      -- Both overloads apply the same complete native policy. Live packets
      -- carrying their original primitive facts need no historical adjunct.
      return Seen or else Packet.Complete (Packet_Data, (Packet_Data'First, Packet_Data'Length)) = Packet.Ready;
   end Packet_Ready;

   function Packet_Transaction (Packet_Data, Data : E.Bytes; Original, Actual, Authority : E.Span) return Boolean is
      Whole : constant E.Span := (Packet_Data'First, Packet_Data'Length);
      View : constant Packet.Packet_View := Packet.Decode (Packet_Data, Whole);
      function PF (Item : E.Span; Name : String) return E.Span is (R.Field (Packet_Data, Item, Name));
      function Bind (Field, Identity : String) return Boolean is
        (Packet_Hash (Packet_Data, Data, PF (View.Values, Field), F (Data, Actual, Identity)));
   begin
      if not View.Valid or else not Packet_Ready (Packet_Data, Data, Actual, Authority)
        or else not R.Text_Is (Packet_Data, PF (View.Values, "phase"), "COMMIT")
        or else not Cross_Value (Packet_Data, Data, PF (View.Candidate, "instance_id"), F (Data, Original, "candidateWorld"), E.Recovery)
        or else not Cross_Value (Packet_Data, Data, PF (View.Candidate, "alias"), F (Data, Original, "candidateAlias"), E.Recovery)
        or else not Cross_Value (Packet_Data, Data, PF (View.Candidate, "content_id"), F (Data, Original, "candidateContent"), E.Recovery)
        or else not Cross_Value (Packet_Data, Data, PF (View.Candidate, "parent_content"), F (Data, Original, "parentWorld"), E.Recovery)
        -- Independent pre-effect and post-flush captures retain their full
        -- inputs; only consequential original identities are joined here.
        or else not Cross_Value (Packet_Data, Data, PF (View.Authoritative_Requirement, "requirementHash"), F (Data, Actual, "commitRequirementHash"), E.Recovery)
        or else not Bind ("expected_parent", "parentContentExpected")
        or else not Bind ("expected_base", "baseRoot") or else not Bind ("candidate_base", "baseRoot")
        or else not Bind ("expected_delta", "deltaHash") or else not Bind ("candidate_delta", "deltaHash")
        or else not Bind ("expected_root_set", "rootSetHash") or else not Bind ("candidate_root_set", "rootSetHash")
        or else not Bind ("expected_staged_root", "stagedRoot") or else not Bind ("actual_staged_root", "stagedRoot")
        or else not Bind ("staged_content_root", "stagedContentRoot")
        or else not Saved_Roots_Match (Packet_Data, Data, View.Roots, F (Data, Original, "stagedRootRecords"))
        or else not Input_Continuity (Packet_Data, Data, View.Inputs, Original)
      then return False; end if;
      return R.Text_Is (Packet_Data, PF (View.Values, "mode"),
        (if Is_Text (Data, F (Data, F (Data, Original, "validation"), "mode"), "checkpoint-return")
         then "CHECKPOINT_RETURN" else "CANDIDATE_EVALUATION"));
   end Packet_Transaction;

   function Chain_Prefix (Prefix_Data, Full_Data : E.Bytes; Prefix, Full : E.Span) return Boolean is
      Count : constant E.Count := List_Length (Prefix_Data, Prefix);
   begin
      if E.Decode (Prefix_Data, Prefix, E.Operation).Form not in E.List_Value | E.Tuple_Value
        or else E.Decode (Full_Data, Full, E.Operation).Form not in E.List_Value | E.Tuple_Value
        or else Count > List_Length (Full_Data, Full) then return False; end if;
      if Count > 0 then for X in E.Count range 0 .. Count - 1 loop
         if not Cross_Value (Prefix_Data, Full_Data, Element (Prefix_Data, Prefix, X), Element (Full_Data, Full, X)) then return False; end if;
      end loop; end if;
      return True;
   end Chain_Prefix;
   function Authority_Matches (Data : E.Bytes; Original, Actual, Chains, Authority : E.Span) return Boolean is
      Boundary, Prepared, Intent : E.Span := (1, 0);
      Native_Count : E.Count := 0;
   begin
      if E.Decode (Data, Authority, E.Operation).Form /= E.List_Value then return False; end if;
      for X in E.Count range 1 .. List_Length (Data, Authority) loop
         declare Item : constant E.Span := Element (Data, Authority, X - 1); begin
            if Is_Text (Data, F (Data, Item, "name"), "FULL_PRE_EFFECT_BOUNDARY") then
               if Boundary.Length /= 0 then return False; end if; Boundary := Item;
            elsif Is_Text (Data, F (Data, Item, "name"), "FULL_BROKER_PREPARED") then
               if Prepared.Length /= 0 then return False; end if; Prepared := Item;
            elsif Is_Text (Data, F (Data, Item, "name"), "FULL_BROKER_CANONICAL_INTENT") then
               if Intent.Length /= 0 then return False; end if; Intent := Item;
            elsif Is_Text (Data, F (Data, Item, "name"), "FULL_BROKER_NATIVE") then Native_Count := Native_Count + 1;
            elsif not Is_Text (Data, F (Data, Item, "name"), "FULL_BROKER_OWNER_DISPOSITION")
              and then not Is_Text (Data, F (Data, Item, "name"), "RECOVERY_SYNTAX_FACTS_V1")
              and then not Is_Text (Data, F (Data, Item, "name"), "FULL_BROKER_WORKER_RESULT")
              and then not Is_Text (Data, F (Data, Item, "name"), "FULL_BROKER_COMMITTED")
            then return False; end if;
         end;
      end loop;
      if Boundary.Length = 0 or else Prepared.Length = 0 or else Intent.Length = 0 or else Native_Count = 0
        or else not Hex_Valid (Text (Data, F (Data, Boundary, "collapse_packet")))
        or else not Hex_Valid (Text (Data, F (Data, Prepared, "value"))) then return False; end if;
      declare
         Packet_Data : constant E.Bytes := Hex_Bytes (Text (Data, F (Data, Boundary, "collapse_packet")));
         Prepared_Data : constant E.Bytes := Hex_Bytes (Text (Data, F (Data, Prepared, "value")));
         Prepared_Value : constant E.Span := (Prepared_Data'First, Prepared_Data'Length);
         Values : constant Packet.Packet_View := Packet.Decode (Packet_Data, (Packet_Data'First, Packet_Data'Length));
         Packet_Bytes : constant E.View := E.Decode (Prepared_Data, F (Prepared_Data, Prepared_Value, "packet"), E.Operation);
      begin
         if not A.Valid (Prepared_Data, Prepared_Value) or else not Packet_Transaction (Packet_Data, Data, Original, Actual, Authority)
           or else Packet_Bytes.Form /= E.Bytes_Value or else not E.Bytes_Valid (Prepared_Data, Packet_Bytes.Payload)
           or else E.Materialize (Prepared_Data, Packet_Bytes.Payload) /= Packet_Data
           or else not Cross_Value (Packet_Data, Prepared_Data, Values.Values, F (Prepared_Data, Prepared_Value, "values"), E.Recovery)
         then return False; end if;
         for X in E.Count range 1 .. List_Length (Data, Authority) loop
            declare Item : constant E.Span := Element (Data, Authority, X - 1); begin
               if Is_Text (Data, F (Data, Item, "name"), "FULL_BROKER_NATIVE")
                 or else Is_Text (Data, F (Data, Item, "name"), "FULL_BROKER_CANONICAL_INTENT")
                 or else Is_Text (Data, F (Data, Item, "name"), "FULL_BROKER_OWNER_DISPOSITION")
               then
                  if not Hex_Valid (Text (Data, F (Data, Item, "value"))) then return False; end if;
                  declare
                     Source : constant E.Bytes := Hex_Bytes (Text (Data, F (Data, Item, "value")));
                     Whole_Source : constant E.Span := (Source'First, Source'Length);
                     Arguments : constant E.Span := F (Source, Whole_Source, "arguments");
                     Material : constant E.Span := Element (Source, Arguments, 7);
                  begin
                     if not A.Valid (Source, Whole_Source) or else List_Length (Source, Arguments) /= 12
                       or else not Cross_Value (Source, Prepared_Data, Element (Source, Arguments, 6), F (Prepared_Data, Prepared_Value, "values"))
                       or else not Cross_Value (Source, Prepared_Data, F (Source, Material, "worker_issued"), F (Prepared_Data, Prepared_Value, "worker"))
                       or else not Cross_Value (Source, Prepared_Data, F (Source, Material, "worker_recovered"), F (Prepared_Data, Prepared_Value, "worker"))
                       or else not Cross_Value (Source, Prepared_Data, F (Source, Material, "canonical_issued"), F (Prepared_Data, Prepared_Value, "canonical"))
                       or else not Cross_Value (Source, Prepared_Data, F (Source, Material, "canonical_recovered"), F (Prepared_Data, Prepared_Value, "canonical"))
                     then return False; end if;
                     if Is_Text (Data, F (Data, Item, "name"), "FULL_BROKER_NATIVE") then
                        declare
                           Observed : constant E.Span := F (Source, F (Source, Whole_Source, "facts"), "worldline_chains");
                        begin
                           if not Chain_Prefix (Source, Data, F (Source, Observed, "receipts"), F (Data, Chains, "receipts"))
                             or else not Chain_Prefix (Source, Data, F (Source, Observed, "events"), F (Data, Chains, "events"))
                           then return False; end if;
                        end;
                     end if;
                  end;
               end if;
            end;
         end loop;
      end;
      return True;
   end Authority_Matches;

   function Historical_Commit_Matches
     (Data : E.Bytes; Actual, Result, Chains, Authority : E.Span) return Boolean is
      Seen : Boolean := False;
   begin
      -- Original worker and completed broker observations retain the entire
      -- actual record/result/chains, including independently acquired commit
      -- inputs. They are not reconstructed from a pre-effect input projection.
      for I in E.Count range 1 .. List_Length (Data, Authority) loop
         declare Item : constant E.Span := Element (Data, Authority, I - 1);
            Worker : constant Boolean := Is_Text (Data, F (Data, Item, "name"), "FULL_BROKER_WORKER_RESULT");
         begin
            if Worker or else Is_Text (Data, F (Data, Item, "name"), "FULL_BROKER_COMMITTED") then
               if not Hex_Valid (Text (Data, F (Data, Item, "value"))) then return False; end if;
               declare
                  Source : constant E.Bytes := Hex_Bytes (Text (Data, F (Data, Item, "value")));
                  Whole : constant E.Span := (Source'First, Source'Length);
                  Record_Value : constant E.Span := F (Source, Whole, (if Worker then "record" else "actual_worker"));
                  Observed : constant E.Span := F (Source, Whole, (if Worker then "chains" else "actual_chains"));
               begin
                  if not Object (Source, Whole)
                    or else not Cross_Value (Source, Data, Record_Value, Actual)
                    or else not Cross_Value (Source, Data, F (Source, Whole, "result"), Result)
                    or else not Chain_Prefix (Source, Data, F (Source, Observed, "receipts"), F (Data, Chains, "receipts"))
                    or else not Chain_Prefix (Source, Data, F (Source, Observed, "events"), F (Data, Chains, "events"))
                  then return False; end if;
                  Seen := True;
               end;
            end if;
         end;
      end loop;
      return Seen;
   end Historical_Commit_Matches;

   function Post_Flush_Matches (Data : E.Bytes; Original, Actual, Result, Chains, Authority : E.Span) return Boolean is
      Encoded : constant E.Span := F (Data, Actual, "postFlushPacket");
   begin
      -- Historical absence uses genuine retained actual worker records, never
      -- an invented historical packet or an unjoined commit-input success.
      if Encoded.Length = 0 then return Historical_Commit_Matches (Data, Actual, Result, Chains, Authority); end if;
      if not Hex_Valid (Text (Data, Encoded)) then return False; end if;
      declare
         Source : constant E.Bytes := Hex_Bytes (Text (Data, Encoded));
         View : constant Packet.Packet_View := Packet.Decode (Source, (Source'First, Source'Length));
      begin
         return Packet_Transaction (Source, Data, Original, Actual, Authority)
           and then Cross_Value (Source, Data, View.Inputs, F (Data, Actual, "decisionInputsAtCommit"), E.Recovery);
      end;
   end Post_Flush_Matches;

   function Evidence_Binding (Data : E.Bytes; Record_Value, Binding : E.Span) return Boolean is
      Validation : constant E.Span := F (Data, Record_Value, "validation");
      Stage : constant E.Span := F (Data, Record_Value, "stagedValidation");
      Bound_Stage : constant E.Span := F (Data, Binding, "stagedValidation");
      Left : constant array (Positive range 1 .. 9) of E.Span :=
        [F (Data, Binding, "mode"), F (Data, Binding, "evidenceSource"), F (Data, Binding, "candidateContextHash"),
         F (Data, Binding, "candidateRequirementHash"), F (Data, Binding, "prepareRequirementHash"), F (Data, Binding, "commitRequirementHash"),
         F (Data, Binding, "policySourceSha256"), F (Data, Binding, "testedRoot"), F (Data, Binding, "stagedContentRoot")];
      Right : constant array (Positive range 1 .. 9) of E.Span :=
        [F (Data, Validation, "mode"), F (Data, Validation, "source"), F (Data, Validation, "contextHash"),
         F (Data, Validation, "candidateRequirementHash"), F (Data, Validation, "requirementHash"), F (Data, Record_Value, "commitRequirementHash"),
         F (Data, Validation, "policySourceSha256"), F (Data, Record_Value, "testedRoot"), F (Data, Record_Value, "stagedContentRoot")];
   begin
      if not Object (Data, Validation) then return Null_Or_Missing (Data, Binding); end if;
      if not Object (Data, Binding) or else E.Array_Length (Data, E.Decode (Data, Binding, E.Operation).Children) /= 12
        or else not Schema_One (Data, F (Data, Binding, "schemaVersion")) then return False; end if;
      for X in Left'Range loop if not Get_Same (Data, Left (X), Right (X)) then return False; end if; end loop;
      if not Object (Data, Stage) then
         if not Null_Or_Missing (Data, Bound_Stage) then return False; end if;
      else
         if not Object (Data, Bound_Stage) or else E.Array_Length (Data, E.Decode (Data, Bound_Stage, E.Operation).Children) /= 7 then return False; end if;
         declare Names : constant array (Positive range 1 .. 7) of E.Span :=
           [F (Data, Stage, "validationId"), F (Data, Stage, "outcome"), F (Data, Stage, "summary"), F (Data, Stage, "requirementHash"),
            F (Data, Stage, "contextHash"), F (Data, Stage, "evaluatedAt"), F (Data, Stage, "examinedContentRoot")];
           Other : constant array (Positive range 1 .. 7) of E.Span :=
           [F (Data, Bound_Stage, "validationId"), F (Data, Bound_Stage, "outcome"), F (Data, Bound_Stage, "summary"), F (Data, Bound_Stage, "requirementHash"),
            F (Data, Bound_Stage, "contextHash"), F (Data, Bound_Stage, "evaluatedAt"), F (Data, Bound_Stage, "examinedContentRoot")];
         begin for X in Names'Range loop if not Get_Same (Data, Names (X), Other (X)) then return False; end if; end loop; end;
      end if;
      declare
         Untested : constant E.Span := F (Data, Record_Value, "untestedPaths");
         Count : constant String := P.Decimal (J.Render (Data, F (Data, Binding, "untestedPathCount")), P.Parse (J.Render (Data, F (Data, Binding, "untestedPathCount"))));
      begin
         return Count = P.Decimal (E.Count'Image (List_Length (Data, Untested)), P.Parse (E.Count'Image (List_Length (Data, Untested))));
      end;
   end Evidence_Binding;

   function List_Copy (Data : E.Bytes; Source, Copy : E.Span) return Boolean is
      V : constant E.View := E.Decode (Data, Source, E.Operation);
      Count : constant E.Count := List_Length (Data, Source);
   begin
      if E.Decode (Data, Copy, E.Operation).Form /= E.List_Value then return False; end if;
      if V.Form in E.List_Value | E.Tuple_Value then
         if List_Length (Data, Copy) /= Count then return False; end if;
         for I in E.Count range 1 .. Count loop
            if not Same_Value (Data, Element (Data, Source, I - 1), Element (Data, Copy, I - 1)) then return False; end if;
         end loop;
         return True;
      end if;
      -- list(empty iterable) preserves the original empty constructor domain.
      return List_Length (Data, Copy) = 0 and then
        ((V.Form = E.Object_Value and then E.Array_Length (Data, V.Children) = 0)
         or else (V.Form in E.Text_Value | E.Bytes_Value and then V.Payload.Encoded.Length = 0));
   end List_Copy;

   function Receipt_Projection (Data : E.Bytes; Record_Value, Receipt : E.Span) return Boolean is
      Commit : constant E.Span := F (Data, Record_Value, "decisionInputsAtCommit");
      Inputs : constant E.Span := (if P.Truth (J.Render (Data, Commit)) then Commit else F (Data, Record_Value, "decisionInputs"));
      Foreign : constant E.Span := F (Data, Inputs, "foreignWrites");
      Contamination : constant E.Span := F (Data, Record_Value, "contamination");
      Projection : constant E.Span := F (Data, Receipt, "foreignWorldContamination");
      Unrelated : constant E.Span := F (Data, F (Data, Receipt, "mergeSet"), "unrelatedConfigurationMutations");
      Kept : E.Count := 0;
   begin
      if not Object (Data, Projection)
        or else E.Decode (Data, Unrelated, E.Operation).Form /= E.List_Value
        or else E.Array_Length (Data, E.Decode (Data, Projection, E.Operation).Children) /=
          (if P.Truth (J.Render (Data, Foreign)) then 4 else 2)
      then return False; end if;
      if not Is_Text (Data, F (Data, Projection, "state"),
        (if List_Length (Data, Contamination) = 0 and then not Is_Text (Data, F (Data, Foreign, "state"), "FOUND")
         then "NONE" else "DETECTED")) then return False; end if;
      if P.Truth (J.Render (Data, Foreign)) then
         if not Get_Same (Data, F (Data, Projection, "measuredBy"), F (Data, Foreign, "measuredBy"))
           or else not Get_Same (Data, F (Data, Projection, "measurement"), F (Data, Foreign, "state"))
         then return False; end if;
      elsif F (Data, Projection, "measuredBy").Length /= 0 or else F (Data, Projection, "measurement").Length /= 0
      then return False; end if;
      for I in E.Count range 1 .. List_Length (Data, Contamination) loop
         declare Item : constant E.Span := Element (Data, Contamination, I - 1); begin
            if not Object (Data, Item) then return False; end if;
            if Is_Text (Data, F (Data, Item, "scope"), "outside-registered-roots") then
               if not Same_Value (Data, Item, Element (Data, Unrelated, Kept)) then return False; end if;
               Kept := Kept + 1;
            end if;
         end;
      end loop;
      return List_Length (Data, Unrelated) = Kept;
   end Receipt_Projection;

   function Causal_Correspondence (Data : E.Bytes; Record_Value, Receipt, Chains, Authority : E.Span) return Boolean is
      Receipts : constant E.Span := F (Data, Chains, "receipts");
      Events : constant E.Span := F (Data, Chains, "events");
      Initial : E.Span := (1, 0);
      function Event_Matches (Archive_Entry : E.Span) return Boolean is
         SQL : constant E.Span := Element (Data, Archive_Entry, 0);
         Raw : constant E.Span := Element (Data, Archive_Entry, 1);
         JSON : constant String := Byte_String (Data, Raw);
         Root : constant P.Node := P.Parse (JSON);
         function Bound (Name : String; Value : E.Span) return Boolean is
           (P.Equal (P.Slice (JSON, P.Field (JSON, Root, Name)), J.Render (Data, Value)));
      begin
         return List_Length (Data, Archive_Entry) = 2 and then Root.Form = P.Object_Value
           and then P.Is_Text (JSON, P.Field (JSON, Root, "kind"), "collapse-receipt")
           and then P.Is_Text (JSON, P.Field (JSON, Root, "actor"), "worldline")
           and then P.Is_Text (JSON, P.Field (JSON, Root, "origin"), "worldline")
           and then P.Equal (P.Slice (JSON, P.Field (JSON, Root, "schemaVersion")), "1")
           and then P.Is_Null (P.Field (JSON, Root, "reason"))
           and then Bound ("transactionId", F (Data, Record_Value, "transactionId"))
           and then Bound ("worldInstance", F (Data, Record_Value, "candidateWorld"))
           and then Bound ("receiptId", F (Data, Receipt, "receiptId"))
           and then Bound ("receiptRoot", F (Data, Receipt, "receiptRoot"))
           and then (if F (Data, Receipt, "requesterBinding").Length > 0 then
              Bound ("requesterBinding", F (Data, Receipt, "requesterBinding")) and then P.Count (JSON, Root) = 10
             else not P.Present (P.Field (JSON, Root, "requesterBinding")) and then P.Count (JSON, Root) = 9)
           and then Same_Value (Data, F (Data, SQL, "world_instance"), F (Data, Record_Value, "candidateWorld"))
           and then Is_Text (Data, F (Data, SQL, "kind"), "collapse-receipt")
           and then Is_Text (Data, F (Data, SQL, "actor"), "worldline")
           and then Null_Or_Missing (Data, F (Data, SQL, "reason"))
           and then Hash_Matches (Data, Raw, F (Data, SQL, "event_root"), "worldline-event-v1")
           and then Same_Value (Data, F (Data, SQL, "event_id"), F (Data, SQL, "chain_hash"));
      end Event_Matches;
   begin
      -- Select the actual initial broker observation by original phase, not
      -- authority list order or the last retained native frame.
      for I in E.Count range 1 .. List_Length (Data, Authority) loop
         declare Item : constant E.Span := Element (Data, Authority, I - 1); begin
            if Is_Text (Data, F (Data, Item, "name"), "FULL_BROKER_NATIVE") then
               if not Hex_Valid (Text (Data, F (Data, Item, "value"))) then return False; end if;
               declare Source : constant E.Bytes := Hex_Bytes (Text (Data, F (Data, Item, "value")));
                  Whole : constant E.Span := (Source'First, Source'Length);
               begin
                  if Is_Text (Source, F (Source, Whole, "phase"), "ISSUED") then
                     if Initial.Length > 0 then return False; end if;
                     Initial := Item;
                  end if;
               end;
            end if;
         end;
      end loop;
      if Initial.Length = 0 then return False; end if;
      declare
         Source : constant E.Bytes := Hex_Bytes (Text (Data, F (Data, Initial, "value")));
         Before : constant E.Span := F (Source, F (Source, (Source'First, Source'Length), "facts"), "worldline_chains");
         Old_Receipts : constant E.Span := F (Source, Before, "receipts");
         Old_Events : constant E.Span := F (Source, Before, "events");
         Existing : E.Count := 0;
         Appended : E.Count := 0;
      begin
         if not Chain_Prefix (Source, Data, Old_Receipts, Receipts) or else not Chain_Prefix (Source, Data, Old_Events, Events) then return False; end if;
         for I in E.Count range 1 .. List_Length (Source, Old_Receipts) loop
            if Cross_Value (Source, Data, F (Source, Element (Source, Element (Source, Old_Receipts, I - 1), 0), "transaction_id"),
              F (Data, Record_Value, "transactionId")) then Existing := Existing + 1; end if;
         end loop;
         if Existing > 1 or else List_Length (Data, Receipts) /=
           List_Length (Source, Old_Receipts) + (if Existing = 0 then 1 else 0) then return False; end if;
         for I in E.Count range 1 .. List_Length (Data, Events) loop
            declare Archive_Entry : constant E.Span := Element (Data, Events, I - 1);
               Raw : constant String := Byte_String (Data, Element (Data, Archive_Entry, 1));
               Root : constant P.Node := P.Parse (Raw);
            begin
               if I > List_Length (Source, Old_Events)
                 and then P.Is_Text (Raw, P.Field (Raw, Root, "kind"), "collapse-receipt")
                 and then P.Equal (P.Slice (Raw, P.Field (Raw, Root, "transactionId")), J.Render (Data, F (Data, Record_Value, "transactionId")))
               then
                  if not Event_Matches (Archive_Entry) then return False; end if;
                  Appended := Appended + 1;
               end if;
            end;
         end loop;
         -- Existing receipt replay returns its exact persisted row and appends
         -- no collapse event, even if an old crash left that event absent.
         return Appended = (if Existing = 0 then 1 else 0);
      end;
   end Causal_Correspondence;

   function Committed_Result_Matches
     (Data : E.Bytes; Original, Actual, Result, Chains, Authority : E.Span) return Boolean
   is
      Receipt : constant E.Span := F (Data, Result, "receipt");
      Receipts : constant E.Span := F (Data, Chains, "receipts");
      Found : E.Count := 0;
      Transaction : constant E.Span := F (Data, Actual, "transactionId");
      Delta_Value : constant E.Span := F (Data, Actual, "delta");
      Merge : constant E.Span := F (Data, Receipt, "mergeSet");
   begin
      if not Immutable_Transaction (Data, Original, Actual) or else not Object (Data, Result)
        or else not Object (Data, Receipt) or else not Authority_Matches (Data, Original, Actual, Chains, Authority)
        or else not Post_Flush_Matches (Data, Original, Actual, Result, Chains, Authority)
        or else not Same_Value (Data, F (Data, Result, "transactionId"), Transaction)
        or else not Is_Text (Data, F (Data, Result, "state"), "COMMITTED")
        or else not Same_Value (Data, F (Data, Result, "candidate"), F (Data, Actual, "candidateAlias"))
        or else not Same_Value (Data, F (Data, Result, "beforeRoot"), F (Data, Actual, "beforeRoot"))
        or else not Same_Value (Data, F (Data, Result, "afterRoot"), F (Data, Actual, "stagedRoot"))
        or else not Same_Value (Data, F (Data, Receipt, "transactionId"), Transaction)
        or else not Same_Value (Data, F (Data, Receipt, "parentWorld"), F (Data, Actual, "parentWorld"))
        or else not Same_Value (Data, F (Data, Receipt, "candidateWorld"), F (Data, Actual, "candidateContent"))
        or else not Same_Value (Data, F (Data, Receipt, "beforeRoot"), F (Data, Actual, "beforeRoot"))
        or else not Same_Value (Data, F (Data, Receipt, "afterRoot"), F (Data, Actual, "stagedRoot"))
        or else not Same_Value (Data, F (Data, F (Data, Receipt, "baseState"), "root"), F (Data, Delta_Value, "baseRoot"))
        or else not Same_Value (Data, F (Data, F (Data, Receipt, "candidateDelta"), "hash"), F (Data, Delta_Value, "deltaHash"))
        or else not Same_Value (Data, F (Data, F (Data, Receipt, "candidateDelta"), "summary"), F (Data, Delta_Value, "summary"))
        or else not List_Copy (Data, F (Data, Actual, "contamination"), F (Data, F (Data, Receipt, "foreignWorldContamination"), "writes"))
        or else not Schema_One (Data, F (Data, Receipt, "schemaVersion"))
        or else not Is_Text (Data, F (Data, F (Data, Receipt, "baseState"), "state"), "VERIFIED")
        or else not Is_Text (Data, F (Data, F (Data, Receipt, "atomicCollapse"), "state"), "COMMITTED")
        or else not Is_Text (Data, F (Data, F (Data, Receipt, "atomicCollapse"), "mechanism"), "renameat2(RENAME_EXCHANGE)")
      then return False; end if;
      if not Evidence_Binding (Data, Actual, F (Data, Receipt, "evidenceBinding"))
        and then not (F (Data, Receipt, "evidenceBinding").Length = 0 and then Is_Text (Data, F (Data, Original, "state"), "COMMITTED")) then return False; end if;
      if List_Length (Data, F (Data, Merge, "files")) /= List_Length (Data, F (Data, Delta_Value, "operations")) then return False; end if;
      for X in E.Count range 1 .. List_Length (Data, F (Data, Merge, "files")) loop
         declare
            File : constant E.Span := Element (Data, F (Data, Merge, "files"), X - 1);
            Operation : constant E.Span := Element (Data, F (Data, Delta_Value, "operations"), X - 1);
         begin
            if not Object (Data, File) or else E.Array_Length (Data, E.Decode (Data, File, E.Operation).Children) /= 4 then return False; end if;
            if not Same_Value (Data, F (Data, File, "rootKey"), F (Data, Operation, "rootKey"))
              or else not Same_Value (Data, F (Data, File, "pathB64"), F (Data, Operation, "pathB64"))
              or else not Same_Value (Data, F (Data, File, "path"), F (Data, Operation, "pathDisplay"))
              or else not Same_Value (Data, F (Data, File, "op"), F (Data, Operation, "op")) then return False; end if;
         end;
      end loop;
      if F (Data, Actual, "dependencyChanges").Length > 0 then
         if not List_Copy (Data, F (Data, Actual, "dependencyChanges"), F (Data, Merge, "dependencyChanges")) then return False; end if;
      elsif E.Decode (Data, F (Data, Merge, "dependencyChanges"), E.Operation).Form /= E.List_Value
        or else List_Length (Data, F (Data, Merge, "dependencyChanges")) /= 0 then return False; end if;
      if not Is_Text (Data, F (Data, Receipt, "receiptId"), Hash_Text (J.Render (Data, Receipt, Mode => J.Receipt_Id_Body), "worldline-receipt-id-v1", "WL:")) then return False; end if;
      for X in E.Count range 1 .. List_Length (Data, Receipts) loop
         declare
            Archive_Entry : constant E.Span := Element (Data, Receipts, X - 1);
            SQL : constant E.Span := Element (Data, Archive_Entry, 0);
            Raw : constant E.Span := Element (Data, Archive_Entry, 1);
         begin
            if Same_Value (Data, F (Data, SQL, "transaction_id"), Transaction) then
               Found := Found + 1;
               if List_Length (Data, Archive_Entry) /= 2
                 or else Byte_String (Data, Raw) /= J.Render (Data, Receipt, Mode => J.Receipt_Body)
                 or else not Same_Value (Data, F (Data, SQL, "receipt_id"), F (Data, Receipt, "receiptId"))
                 or else not Get_Same (Data, F (Data, SQL, "previous_receipt"), F (Data, Receipt, "previousReceipt"))
                 or else not Same_Value (Data, F (Data, SQL, "receipt_root"), F (Data, Receipt, "receiptRoot"))
                 or else not Same_Value (Data, F (Data, SQL, "chain_hash"), F (Data, Receipt, "chainHash"))
                 or else not Hash_Matches (Data, Raw, F (Data, Receipt, "receiptRoot"), "worldline-receipt-record-v1")
               then return False; end if;
            end if;
         end;
      end loop;
      return Found = 1 and then Receipt_Projection (Data, Actual, Receipt)
        and then Causal_Correspondence (Data, Actual, Receipt, Chains, Authority);
   end Committed_Result_Matches;

end Worldline.Transaction_Relations;
