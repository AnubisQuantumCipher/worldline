with Interfaces;
with Attest;
with Attest.SHA256;
with Decimal_Binary64;
with SPARK.Big_Integers;
with Worldline.Raw_JSON;
package body Worldline.Ordinary_Receipt_Policy with SPARK_Mode is
   use type E.Count;
   use type E.Value_Kind;
   use type E.Bytes;
   use type E.Q.Byte;
   use type H.Reason;
   use type H.Chain_Kind;
   use type Decimal_Binary64.Bits;
   use SPARK.Big_Integers;
   use type Hash;
   use type Interfaces.Unsigned_32;

   function V (Data : E.Bytes; S : E.Span) return E.View is
     (E.Decode (Data, S, E.Operation));
   function F (Data : E.Bytes; S : E.Span; Name : String) return E.Span is
     (A.Field (Data, S, Name));
   function Text (Data : E.Bytes; S : E.Span; Name : String) return Boolean is
     (E.Text_Is (Data, V (Data, S), Name));
   function Is_Null (Data : E.Bytes; S : E.Span) return Boolean is
     (V (Data, S).Form = E.Null_Value);
   function Element (Data : E.Bytes; S : E.Span; I : E.Count) return E.Span is
     (E.Array_Element (Data, V (Data, S).Children, I));
   function Length (Data : E.Bytes; S : E.Span) return E.Count is
     (E.Array_Length (Data, V (Data, S).Children));
   function Metadata_Truth (Data : E.Bytes; Value : E.Span) return Truth_Value is
      Form : constant E.Span := F (Data, Value, "form");
      Original : constant E.View := V (Data, F (Data, Value, "value"));
      Observed : constant E.View := V (Data, F (Data, Value, "truth"));
      Nonzero : Boolean := False;
   begin
      if Text (Data, Form, "protocol") then
         if Is_Null (Data, F (Data, Value, "truth")) then return Truth_Missing; end if;
         return (if Observed.Form /= E.Boolean_Value then Truth_Invalid
                 elsif Observed.Boolean_Bit then Truth_True else Truth_False);
      elsif Text (Data, Form, "extent") then
         if Original.Form /= E.Integer_Value or else Original.Sign
           or else not E.Bytes_Valid (Data, Original.Payload) then return Truth_Invalid; end if;
      elsif not Text (Data, Form, "value") then
         return Truth_Invalid;
      elsif Original.Form = E.Null_Value then
         return Truth_False;
      elsif Original.Form = E.Boolean_Value then
         return (if Original.Boolean_Bit then Truth_True else Truth_False);
      elsif Original.Form in E.Text_Value | E.Bytes_Value then
         if not E.Bytes_Valid (Data, Original.Payload) then return Truth_Invalid; end if;
         return (if E.Materialize (Data, Original.Payload)'Length > 0
                 then Truth_True else Truth_False);
      elsif Original.Form not in E.Integer_Value | E.Float_Value then
         return Truth_Invalid;
      end if;
      if not E.Bytes_Valid (Data, Original.Payload) then return Truth_Invalid; end if;
      declare Raw : constant E.Bytes := E.Materialize (Data, Original.Payload);
      begin
         if Original.Form = E.Float_Value then
            if Raw'Length /= 8 then return Truth_Invalid; end if;
            -- Both signed zeroes are false. Infinity and every NaN are true,
            -- exactly as original Python truth; no float-domain restriction.
            Nonzero := (Raw (Raw'First) mod 128) /= 0;
            for I in E.Count range 1 .. 7 loop
               Nonzero := Nonzero or else Raw (Raw'First + I) /= 0;
            end loop;
         else
            for Octet of Raw loop Nonzero := Nonzero or else Octet /= 0; end loop;
         end if;
      end;
      return (if Nonzero then Truth_True else Truth_False);
   end Metadata_Truth;

   function Actual_Route (Data : E.Bytes; Packet : E.Span)
      return Route_Observation is
      Roster : constant E.Span := F (Data, Packet, "routes");
      Registrations : constant E.Span := F (Data, Packet, "registrations");
      Selected : constant E.Span := F (Data, Packet, "selected");
      Result : Route_Observation := (False, (1, 0), (1, 0), (1, 0), (1, 0), (1, 0));
      N : constant E.Count := Length (Data, Roster);
      Matches : E.Count := 0;
   begin
      if V (Data, Roster).Form /= E.List_Value or else N = 0
        or else V (Data, Registrations).Form /= E.List_Value
        or else Length (Data, Registrations) /= N
        or else V (Data, F (Data, Packet, "operation")).Form /= E.Text_Value
        or else V (Data, Selected).Form /= E.Object_Value
        or else V (Data, F (Data, Selected, "identity")).Form /= E.Integer_Value
        or else V (Data, F (Data, Selected, "handler_identity")).Form /= E.Integer_Value
      then return Result; end if;
      for I in E.Count range 0 .. N - 1 loop
         declare
            Row : constant E.Span := Element (Data, Roster, I);
            Fields : constant E.Span := F (Data, Row, "fields");
            Handler : constant E.Span := F (Data, Fields, "handler");
            Registered : constant E.Span := Element (Data, Registrations, I);
         begin
            if V (Data, Row).Form /= E.Object_Value
              or else V (Data, F (Data, Row, "name")).Form not in E.Text_Value | E.Null_Value
              or else V (Data, F (Data, Row, "key")).Form /= E.Object_Value
              or else V (Data, F (Data, Row, "identity")).Form /= E.Integer_Value
              or else not Text (Data, F (Data, Row, "module"), "worldline.daemon")
              or else not Text (Data, F (Data, Row, "class"), "Operation")
              or else V (Data, Fields).Form /= E.Object_Value
              or else Length (Data, Fields) /= 3
              or else V (Data, Handler).Form /= E.Object_Value
              or else V (Data, F (Data, Handler, "identity")).Form /= E.Integer_Value
              or else V (Data, F (Data, Fields, "owner_only")).Form /= E.Object_Value
              or else V (Data, F (Data, Fields, "mutating")).Form /= E.Object_Value
            then return Result; end if;
            if V (Data, Registered).Form /= E.Object_Value
              or else not A.Same_Encoding (Data, F (Data, Row, "identity"),
                F (Data, Registered, "identity"))
              or else not A.Same_Encoding (Data, F (Data, Handler, "identity"),
                F (Data, Registered, "handler_identity"))
              or else not A.Same_Encoding (Data, F (Data, F (Data, Row, "key"), "identity"),
                F (Data, Registered, "key_identity")) then return Result; end if;
            for J in E.Count range 0 .. I loop
               if J < I and then A.Same_Encoding (Data, F (Data, Row, "identity"),
                 F (Data, Element (Data, Roster, J), "identity")) then return Result; end if;
            end loop;
            if A.Same_Encoding (Data, F (Data, Row, "identity"), F (Data, Selected, "identity")) then
               Matches := Matches + 1;
               if not A.Same_Encoding (Data, F (Data, Handler, "identity"),
                    F (Data, Selected, "handler_identity")) then return Result; end if;
               declare Key : constant E.Span := F (Data, Row, "key");
               begin
                  if Text (Data, F (Data, Key, "form"), "value") then
                     if V (Data, F (Data, Key, "value")).Form /= E.Text_Value or else
                       not A.Same_Encoding (Data, F (Data, Key, "value"),
                         F (Data, Packet, "operation")) then return Result; end if;
                  elsif Text (Data, F (Data, Key, "form"), "extent") then
                     return Result;
                  elsif not Text (Data, F (Data, Key, "form"), "protocol") then
                     return Result;
                  end if;
                  -- Custom key equality is observed only by the actual original
                  -- live dict lookup. Its selected registration identity is not
                  -- reconstructed or asserted equal from archived object bytes.
               end;
               Result.Name := F (Data, Row, "name");
               Result.Identity := F (Data, Row, "identity");
               Result.Handler := Handler;
               Result.Owner_Metadata := F (Data, Fields, "owner_only");
               Result.Mutation_Metadata := F (Data, Fields, "mutating");
            end if;
         end;
      end loop;
      Result.Valid := Matches = 1;
      return Result;
   end Actual_Route;

   function Schema_One (Data : E.Bytes; Value : E.Span) return Boolean is
      Item : constant E.View := V (Data, Value);
   begin
      if Item.Form = E.Boolean_Value then return Item.Boolean_Bit; end if;
      if Item.Form not in E.Integer_Value | E.Float_Value or else
        not E.Bytes_Valid (Data, Item.Payload) then return False; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, Item.Payload);
      begin
         if Item.Form = E.Integer_Value then
            return not Item.Sign and then Raw'Length = 1 and then Raw (Raw'First) = 1;
         end if;
         return Raw'Length = 8 and then Raw (Raw'First) = 16#3F#
           and then Raw (Raw'First + 1) = 16#F0#
           and then (for all I in E.Count range 2 .. 7 => Raw (Raw'First + I) = 0);
      end;
   end Schema_One;
   function Schema_Status (Data : E.Bytes; Value : E.Span) return Reason is
      Form : constant E.Span := F (Data, Value, "form");
      Observed : constant E.View := V (Data, F (Data, Value, "not_one"));
   begin
      if Text (Data, Form, "value") then
         return (if Schema_One (Data, F (Data, Value, "value")) then Ready else Invalid_Schema);
      elsif Text (Data, Form, "extent") then
         -- An exact builtin container never compares equal to integer one.
         return Invalid_Schema;
      elsif not Text (Data, Form, "protocol") then
         return Malformed_Input;
      elsif Is_Null (Data, F (Data, Value, "not_one")) then
         return Schema_Observation_Required;
      elsif Observed.Form /= E.Boolean_Value then
         return Malformed_Input;
      end if;
      return (if Observed.Boolean_Bit then Invalid_Schema else Ready);
   end Schema_Status;
   function Requester_Profile (Data : E.Bytes; Value : E.Span)
      return Requester_Source is
   begin
      if Is_Null (Data, Value) then return Ordinary_Source; end if;
      if V (Data, Value).Form /= E.Object_Value then return Invalid_Source; end if;
      if Text (Data, F (Data, Value, "schema"), "worldline.requester-operation-binding-v1")
        and then Length (Data, Value) = 4
        and then V (Data, F (Data, Value, "binding")).Form = E.Object_Value
        and then V (Data, F (Data, Value, "originalRequest")).Form = E.Object_Value
        and then F (Data, Value, "reservationEvent").Length > 0
      then return Operation_Source; end if;
      if Text (Data, F (Data, Value, "schema"), "worldline.owner-canonical-binding-v1")
        and then Length (Data, Value) = 8
        and then F (Data, Value, "operation").Length > 0
        and then V (Data, F (Data, Value, "owner_binding")).Form = E.Object_Value
        and then V (Data, F (Data, Value, "original_request")).Form = E.Object_Value
        and then V (Data, F (Data, Value, "owner_journal")).Form = E.Text_Value
        and then V (Data, F (Data, Value, "owner_head")).Form = E.Text_Value
        and then F (Data, Value, "owner_event").Length > 0
        and then F (Data, Value, "owner_record").Length > 0
      then return Owner_Source; end if;
      return Invalid_Source;
   end Requester_Profile;



   function Normalized (Data : E.Bytes; S : E.Span; Name : String) return Boolean is
      Item : constant E.View := V (Data, S);
   begin
      if Item.Form /= E.Bytes_Value or else not E.Bytes_Valid (Data, Item.Payload) then return False; end if;
      declare Raw : constant E.Bytes := E.Materialize (Data, Item.Payload);
      begin
         return Raw'Length = Name'Length and then (for all I in Name'Range =>
           Raw (Raw'First + E.Count (I - Name'First)) = Character'Pos (Name (I)));
      end;
   end Normalized;

   function Reserved_Actor_Name (Data : E.Bytes; Value : E.Span) return Boolean is
     (Normalized (Data, Value, "worldline") or else Normalized (Data, Value, "system")
      or else Normalized (Data, Value, "user"));
   function Reserved_Kind_Name (Data : E.Bytes; Value : E.Span) return Boolean is
     (Normalized (Data, Value, "mission") or else Normalized (Data, Value, "agent-invocation")
      or else Normalized (Data, Value, "agent-invocation-result") or else Normalized (Data, Value, "file-delta")
      or else Normalized (Data, Value, "collapse-receipt") or else Normalized (Data, Value, "unaccounted-write")
      or else Normalized (Data, Value, "promotion-refused") or else Normalized (Data, Value, "revalidation")
      or else Normalized (Data, Value, "staged-validation") or else Normalized (Data, Value, "prune")
      or else Normalized (Data, Value, "external") or else Normalized (Data, Value, "agent-claim-refused")
      or else Normalized (Data, Value, "ghost-generation-superseded"));

   function Python_Equal (Data : E.Bytes; Left, Right : E.Span) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Left.Length);
   function Python_Equal (Data : E.Bytes; Left, Right : E.Span) return Boolean is
      X : constant E.View := V (Data, Left);
      Y : constant E.View := V (Data, Right);
      function Numeric (Item : E.View) return Boolean is
        (Item.Form in E.Boolean_Value | E.Integer_Value | E.Float_Value);
      type Number is record
         Valid, Negative : Boolean := False;
         Value : Decimal_Binary64.Rational;
      end record;
      function Denote (Item : E.View) return Number is
         Result : Number;
      begin
         if Item.Form = E.Boolean_Value then
            Result.Valid := True;
            Result.Value.Numerator := To_Big_Integer (Boolean'Pos (Item.Boolean_Bit));
         elsif Item.Form in E.Integer_Value | E.Float_Value and then
           E.Bytes_Valid (Data, Item.Payload) then
            declare Raw : constant E.Bytes := E.Materialize (Data, Item.Payload);
            begin
               if Item.Form = E.Integer_Value then
                  for I in reverse Raw'Range loop
                     Result.Value.Numerator := Result.Value.Numerator * To_Big_Integer (256)
                       + To_Big_Integer (Integer (Raw (I)));
                  end loop;
                  Result.Negative := Item.Sign and then Result.Value.Numerator /= To_Big_Integer (0);
                  Result.Valid := True;
               elsif Raw'Length = 8 then
                  declare B : Decimal_Binary64.Bits := 0;
                  begin
                     for Octet of Raw loop B := B * 256 + Decimal_Binary64.Bits (Octet); end loop;
                     if Decimal_Binary64.Finite (B) then
                        Result.Value := Decimal_Binary64.Value (Decimal_Binary64.Magnitude (B));
                        Result.Negative := B >= Decimal_Binary64.Sign_Bit
                          and then Result.Value.Numerator /= To_Big_Integer (0);
                        Result.Valid := True;
                     end if;
                  end;
               end if;
            end;
         end if;
         return Result;
      end Denote;
      N : constant E.Count := Length (Data, Left);
   begin
      if not A.Valid (Data, Left) or else not A.Valid (Data, Right) then return False; end if;
      if Numeric (X) and then Numeric (Y) then
         declare L : constant Number := Denote (X); R : constant Number := Denote (Y);
         begin return L.Valid and then R.Valid and then L.Negative = R.Negative
           and then Decimal_Binary64.Equal (L.Value, R.Value); end;
      end if;
      if X.Form /= Y.Form then return False; end if;
      if X.Form in E.List_Value | E.Tuple_Value then
         if N /= Length (Data, Right) then return False; end if;
         if N > 0 then
            for I in E.Count range 0 .. N - 1 loop
               if not Python_Equal (Data, Element (Data, Left, I), Element (Data, Right, I)) then return False; end if;
            end loop;
         end if;
         return True;
      elsif X.Form = E.Object_Value then
         if N /= Length (Data, Right) then return False; end if;
         if N > 0 then
            for I in E.Count range 0 .. N - 1 loop
               declare
                  Pair : constant E.View := E.Decode
                    (Data, E.Array_Element (Data, X.Children, I), E.Finalization);
                  Key : constant E.Span := E.Array_Element (Data, Pair.Children, 0);
                  Found : Boolean := False;
               begin
                  for J in E.Count range 0 .. N - 1 loop
                     declare Other : constant E.View := E.Decode
                       (Data, E.Array_Element (Data, Y.Children, J), E.Finalization);
                     begin
                        if A.Same_Encoding (Data, Key, E.Array_Element (Data, Other.Children, 0)) then
                           Found := Python_Equal (Data, E.Array_Element (Data, Pair.Children, 1),
                             E.Array_Element (Data, Other.Children, 1));
                           exit;
                        end if;
                     end;
                  end loop;
                  if not Found then return False; end if;
               end;
            end loop;
         end if;
         return True;
      end if;
      return A.Same_Encoding (Data, Left, Right);
   end Python_Equal;
   function Receipt_Predecessor_Status (Data : E.Bytes; Source, Row : E.Span)
      return Reason is
      Expected : constant E.Span := F (Data, Source, "expected");
      Form : constant E.Span := F (Data, Source, "form");
      Observed : constant E.View := V (Data, F (Data, Source, "not_previous"));
   begin
      if Is_Null (Data, Row) then
         if not Is_Null (Data, Expected) then return Malformed_Input; end if;
      elsif V (Data, Row).Form /= E.Object_Value or else
        not A.Same_Encoding (Data, Expected, F (Data, Row, "receipt_id")) then
         return Malformed_Input;
      end if;
      if Text (Data, Form, "value") then
         return (if Python_Equal (Data, F (Data, Source, "value"), Expected) then Ready
                 else Receipt_Predecessor_Mismatch);
      elsif Text (Data, Form, "extent") then return Receipt_Predecessor_Mismatch;
      elsif not Text (Data, Form, "protocol") then return Malformed_Input;
      elsif Is_Null (Data, F (Data, Source, "not_previous")) then
         return Receipt_Predecessor_Observation_Required;
      elsif Observed.Form /= E.Boolean_Value then return Malformed_Input; end if;
      return (if Observed.Boolean_Bit then Receipt_Predecessor_Mismatch else Ready);
   end Receipt_Predecessor_Status;


   function Ordinal_Is (Data : E.Bytes; S : E.Span; Expected : E.Count) return Boolean is
      Item : constant E.View := V (Data, S);
      Remainder : E.Count := Expected;
   begin
      if Item.Form /= E.Integer_Value or else Item.Sign
        or else not E.Bytes_Valid (Data, Item.Payload) then return False; end if;
      declare Raw : constant E.Bytes := E.Materialize (Data, Item.Payload);
      begin
         for B of Raw loop
            if E.Count (B) /= Remainder mod 256 then return False; end if;
            Remainder := Remainder / 256;
         end loop;
         return Remainder = 0;
      end;
   end Ordinal_Is;

   type Receipt_Name is (Schema_Version, Receipt_Id, Previous_Receipt, Parent_World,
      Candidate_World, Base_State, Candidate_Delta, Foreign_World_Contamination,
      Merge_Set, Invariant_Preservation, Atomic_Collapse, Before_Root, After_Root,
      Transaction_Id, Non_Claims, Evidence_Binding, Requester_Binding);
   function Name (N : Receipt_Name) return String is
     (case N is
      when Schema_Version => "schemaVersion", when Receipt_Id => "receiptId",
      when Previous_Receipt => "previousReceipt", when Parent_World => "parentWorld",
      when Candidate_World => "candidateWorld", when Base_State => "baseState",
      when Candidate_Delta => "candidateDelta", when Foreign_World_Contamination => "foreignWorldContamination",
      when Merge_Set => "mergeSet", when Invariant_Preservation => "invariantPreservation",
      when Atomic_Collapse => "atomicCollapse", when Before_Root => "beforeRoot",
      when After_Root => "afterRoot", when Transaction_Id => "transactionId",
      when Non_Claims => "nonClaims", when Evidence_Binding => "evidenceBinding",
      when Requester_Binding => "requesterBinding");
   function Receipt_Name_Status (Data : E.Bytes; Keys, Set_Observation : E.Span;
                                 Allow_Requester : Boolean) return Reason is
      function Stage (Items, Observation : E.Span; Required : Boolean) return Reason is
         Seen : array (Receipt_Name) of Boolean := (others => False);
         Protocol, Extra : Boolean := False;
         N : constant E.Count := Length (Data, Items);
      begin
         if V (Data, Items).Form /= E.List_Value then return Malformed_Input; end if;
         if N > 0 then
            for I in E.Count range 0 .. N - 1 loop
               declare
                  Key : constant E.Span := Element (Data, Items, I);
                  Original : constant E.Span := F (Data, Key, "value");
                  Known : Boolean := False;
               begin
                  if V (Data, Key).Form /= E.Object_Value then return Malformed_Input; end if;
                  if Text (Data, F (Data, Key, "form"), "protocol") then
                     Protocol := True;
                  elsif Text (Data, F (Data, Key, "form"), "value") then
                     for K in Receipt_Name range Schema_Version .. Evidence_Binding loop
                        if Text (Data, Original, Name (K)) then Seen (K) := True; Known := True; end if;
                     end loop;
                     if Allow_Requester and then Text (Data, Original, "requesterBinding") then
                        Known := True;
                     end if;
                     Extra := Extra or else not Known;
                  elsif Text (Data, F (Data, Key, "form"), "extent") then
                     Extra := True;
                  else return Malformed_Input;
                  end if;
               end;
            end loop;
         end if;
         if Protocol then
            -- Actual live set operators own custom hash/equality observations;
            -- primitive membership remains native, not copied validation flags.
            if Is_Null (Data, Observation) then return Receipt_Key_Observation_Required; end if;
            if V (Data, Observation).Form /= E.Boolean_Value then return Malformed_Input; end if;
            return (if V (Data, Observation).Boolean_Bit then Ready else Invalid_Receipt);
         end if;
         if Required then
            return (if (for some K in Receipt_Name range Schema_Version .. Non_Claims =>
              not Seen (K)) then Invalid_Receipt else Ready);
         end if;
         return (if Extra then Invalid_Receipt else Ready);
      end Stage;
      First : Reason;
      Allowed : constant E.Span := F (Data, Set_Observation, "allowed_keys");
   begin
      if Is_Null (Data, Keys) then return Receipt_Keys_Required; end if;
      First := Stage (Keys, F (Data, Set_Observation, "required_subset"), True);
      if First /= Ready then return First; end if;
      if Is_Null (Data, Allowed) then return Receipt_Allowed_Keys_Required; end if;
      return Stage (Allowed, F (Data, Set_Observation, "allowed_subset"), False);
   end Receipt_Name_Status;

   function Receipt_Fields (Data : E.Bytes; Value : E.Span;
                            Allow_Requester : Boolean) return Boolean is
      Item : constant E.View := V (Data, Value);
      N : constant E.Count := Length (Data, Value);
   begin
      if Item.Form /= E.Object_Value or else not A.Valid (Data, Value) then return False; end if;
      for K in Receipt_Name range Schema_Version .. Non_Claims loop
         if F (Data, Value, Name (K)).Length = 0 then return False; end if;
      end loop;
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               Pair : constant E.View := E.Decode
                 (Data, E.Array_Element (Data, Item.Children, I), E.Finalization);
               Key : constant E.Span := E.Array_Element (Data, Pair.Children, 0);
               Known : Boolean := False;
            begin
               for K in Receipt_Name range Schema_Version .. Evidence_Binding loop
                  Known := Known or else Text (Data, Key, Name (K));
               end loop;
               if Allow_Requester then
                  Known := Known or else Text (Data, Key, "requesterBinding");
               end if;
               if not Known then return False; end if;
            end;
         end loop;
      end if;
      return True;
   end Receipt_Fields;

   function Digest (Data : E.Bytes; S : E.Span) return H.Optional_Digest is
      Item : constant E.View := V (Data, S);
      Result : H.Optional_Digest := (Present => False, Value => Zero_Hash);
      function Hex (B : E.Q.Byte) return Integer is
        (if B in 48 .. 57 then Integer (B) - 48
         elsif B in 97 .. 102 then Integer (B) - 87 else -1);
   begin
      if Item.Form /= E.Text_Value or else not E.Bytes_Valid (Data, Item.Payload) then return Result; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, Item.Payload);
         Prefix : constant String := "sha256:";
      begin
         if Raw'Length /= 71 or else (for some I in Prefix'Range =>
           Raw (Raw'First + E.Count (I - Prefix'First)) /= Character'Pos (Prefix (I))) then return Result; end if;
         for I in Result.Value'Range loop
            declare
               O : constant E.Count := 7 + E.Count (I - Result.Value'First) * 2;
               X : constant Integer := Hex (Raw (Raw'First + O));
               Y : constant Integer := Hex (Raw (Raw'First + O + 1));
            begin
               if X < 0 or else Y < 0 then return Result; end if;
               Result.Value (I) := Attest.Byte (X * 16 + Y);
            end;
         end loop;
      end;
      Result.Present := True;
      return Result;
   end Digest;

   function Payload_Root (Raw : E.Bytes; Kind : H.Chain_Kind) return Hash is
      Ctx : Attest.SHA256.Context := Attest.SHA256.Initial;
      Domain : constant String := (if Kind = H.Receipt_Chain then
        "worldline-receipt-record-v1" else "worldline-event-v1");
   begin
      for Ch of Domain loop
         Attest.SHA256.Update (Ctx, Attest.Byte_Array'(0 => Attest.Byte (Character'Pos (Ch))));
      end loop;
      for B of Raw loop
         Attest.SHA256.Update (Ctx, Attest.Byte_Array'(0 => Attest.Byte (B)));
      end loop;
      return Attest.SHA256.Final (Ctx);
   end Payload_Root;

   function Row_SQL (Data : E.Bytes; Rows : E.Span; I : E.Count) return E.Span is
     (F (Data, Element (Data, Rows, I), "sql"));
   function Captured_Head_Is (Data : E.Bytes; Rows, Expected : E.Span) return Boolean is
      N : constant E.Count := Length (Data, Rows);
      Actual : constant H.Optional_Digest := (if N = 0 then (True, Zero_Hash)
        else Digest (Data, F (Data, Row_SQL (Data, Rows, N - 1), "chain_hash")));
      Item : constant E.View := V (Data, Expected);
   begin
      if not Actual.Present or else Item.Form /= E.Bytes_Value
        or else not E.Bytes_Valid (Data, Item.Payload) then return False; end if;
      declare Raw : constant E.Bytes := E.Materialize (Data, Item.Payload);
      begin
         return Raw'Length = Actual.Value'Length and then (for all I in Actual.Value'Range =>
           Raw (Raw'First + E.Count (I - Actual.Value'First)) = E.Q.Byte (Actual.Value (I)));
      end;
   end Captured_Head_Is;
   function History (Data : E.Bytes; Rows : E.Span; Kind : H.Chain_Kind)
      return Boolean is
      N : constant E.Count := Length (Data, Rows);
      Retained : H.Retained_Rows (1 .. N);
      Genesis : constant H.Optional_Digest := (True, Zero_Hash);
      Head : H.Optional_Digest := Genesis;
   begin
      if V (Data, Rows).Form /= E.List_Value or else not A.Valid (Data, Rows) then return False; end if;
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               Item : constant E.Span := Element (Data, Rows, I);
               SQL : constant E.Span := F (Data, Item, "sql");
               Stored : constant E.View := V (Data, F (Data, Item, "raw"));
               Previous : H.Optional_Digest := (False, Zero_Hash);
            begin
               if Stored.Form /= E.Bytes_Value or else not E.Bytes_Valid (Data, Stored.Payload) then return False; end if;
               if Kind = H.Causal_Chain then
                  Previous := Digest (Data, F (Data, SQL, "predecessor"));
                  if not Ordinal_Is (Data, F (Data, SQL, "ordinal"), I) then return False; end if;
               else
                  -- Original receipt hash/link uses the previous actual head,
                  -- not a reconstructed historical Python receipt-id comparison.
                  Previous := (if I = 0 then Genesis
                    else Digest (Data, F (Data, Row_SQL (Data, Rows, I - 1), "chain_hash")));
               end if;
               declare
                  Raw : constant E.Bytes := E.Materialize (Data, Stored.Payload);
               begin
                  if not Worldline.Raw_JSON.Ordinary_JSON_Operation_Matches (Raw, Data,
                    (Raw'First, Raw'Length), F (Data, Item, "payload")) then return False; end if;
                  -- Original history verification is schema-free. A live
                  -- Python comparison protocol cannot be reconstructed from JSON.
                  Retained (I + 1) := (Previous, (True, Payload_Root (Raw, Kind)),
                    Digest (Data, F (Data, SQL, (if Kind = H.Receipt_Chain then "receipt_root" else "event_root"))),
                    Digest (Data, F (Data, SQL, "chain_hash")));
               end;
            end;
         end loop;
         Head := Retained (N).Stored_Head;
      end if;
      return H.Replay (Kind, Retained, Genesis, Genesis, Head).Disposition = H.Ready;
   end History;

   function Same_Raw (Data : E.Bytes; Left, Right : E.Span) return Boolean is
      X : constant E.View := V (Data, Left);
      Y : constant E.View := V (Data, Right);
   begin
      if X.Form /= E.Bytes_Value or else Y.Form /= E.Bytes_Value
        or else not E.Bytes_Valid (Data, X.Payload) or else not E.Bytes_Valid (Data, Y.Payload) then return False; end if;
      return E.Materialize (Data, X.Payload) = E.Materialize (Data, Y.Payload);
   end Same_Raw;

   function Hash_Observation (Data : E.Bytes; Value : E.Span; Actual : Hash) return Boolean is
      Item : constant E.View := V (Data, Value);
   begin
      if Item.Form /= E.Bytes_Value or else not E.Bytes_Valid (Data, Item.Payload) then return False; end if;
      declare Raw : constant E.Bytes := E.Materialize (Data, Item.Payload);
      begin
         return Raw'Length = Actual'Length and then (for all I in Actual'Range =>
           Raw (Raw'First + E.Count (I - Actual'First)) = E.Q.Byte (Actual (I)));
      end;
   end Hash_Observation;

   function SQL_Column_Count (Kind : H.Chain_Kind) return E.Count is
     (if Kind = H.Receipt_Chain then 7 else 16);
   function SQL_Column_Name (Kind : H.Chain_Kind; I : E.Count) return String is
     (if Kind = H.Receipt_Chain then
        (case I is when 0 => "receipt_id", when 1 => "previous_receipt",
         when 2 => "transaction_id", when 3 => "receipt_root",
         when 4 => "chain_hash", when 5 => "canonical_path", when 6 => "created_at", when others => "")
      else
        (case I is when 0 => "event_id", when 1 => "world_instance", when 2 => "ordinal",
         when 3 => "kind", when 4 => "actor", when 5 => "tool", when 6 => "reason",
         when 7 => "path_b64", when 8 => "path_display", when 9 => "line_start",
         when 10 => "line_end", when 11 => "predecessor", when 12 => "event_root",
         when 13 => "chain_hash", when 14 => "canonical_path", when 15 => "created_at", when others => ""));
   function SQL_Integer (Kind : H.Chain_Kind; I : E.Count) return Boolean is
     (Kind = H.Causal_Chain and then I in 2 | 9 | 10);
   function SQL_Nullable (Kind : H.Chain_Kind; I : E.Count) return Boolean is
     (if Kind = H.Receipt_Chain then I = 1 else I in 4 .. 10);

   function Effect_Table_Schema (Data : E.Bytes; Source : E.Span; Kind : H.Chain_Kind)
      return Boolean is
      Tables : constant E.Span := F (Data, Source, "table_list");
      Columns : constant E.Span := F (Data, Source, "columns");
      N : constant E.Count := SQL_Column_Count (Kind);
      Matches : E.Count := 0;
   begin
      if V (Data, Source).Form /= E.Object_Value
        or else V (Data, Tables).Form /= E.List_Value
        or else V (Data, Columns).Form /= E.List_Value or else Length (Data, Columns) /= N
        or else V (Data, F (Data, Source, "ddl")).Form /= E.Text_Value
        or else not Text (Data, F (Data, Source, "table"),
          (if Kind = H.Receipt_Chain then "receipts" else "causal_events")) then return False; end if;
      if Length (Data, Tables) > 0 then
         for I in E.Count range 0 .. Length (Data, Tables) - 1 loop
            declare Row : constant E.Span := Element (Data, Tables, I);
            begin
               if Text (Data, F (Data, Row, "schema"), "main") and then
                 Text (Data, F (Data, Row, "name"), (if Kind = H.Receipt_Chain then "receipts" else "causal_events")) then
                  Matches := Matches + 1;
                  if not Text (Data, F (Data, Row, "type"), "table")
                    or else not Ordinal_Is (Data, F (Data, Row, "ncol"), N)
                    or else not Ordinal_Is (Data, F (Data, Row, "wr"), 0)
                    or else not Ordinal_Is (Data, F (Data, Row, "strict"), 1) then return False; end if;
               end if;
            end;
         end loop;
      end if;
      if Matches /= 1 then return False; end if;
      for I in E.Count range 0 .. N - 1 loop
         declare Column : constant E.Span := Element (Data, Columns, I);
         begin
            if V (Data, Column).Form /= E.Object_Value
              or else not Ordinal_Is (Data, F (Data, Column, "cid"), I)
              or else not Text (Data, F (Data, Column, "name"), SQL_Column_Name (Kind, I))
              or else not Text (Data, F (Data, Column, "type"), (if SQL_Integer (Kind, I) then "INTEGER" else "TEXT"))
              or else not Ordinal_Is (Data, F (Data, Column, "hidden"), 0)
              or else not Ordinal_Is (Data, F (Data, Column, "pk"), (if I = 0 then 1 else 0))
              or else not Is_Null (Data, F (Data, Column, "dflt_value")) then return False; end if;
            if I = 0 then
               -- SQLite versions may expose implicit STRICT primary-key
               -- not-null as 0 or 1; the actual STRICT PK semantics are fixed.
               if not Ordinal_Is (Data, F (Data, Column, "notnull"), 0) and then
                 not Ordinal_Is (Data, F (Data, Column, "notnull"), 1) then return False; end if;
            elsif not Ordinal_Is (Data, F (Data, Column, "notnull"),
              (if SQL_Nullable (Kind, I) then 0 else 1)) then return False; end if;
         end;
      end loop;
      return True;
   end Effect_Table_Schema;

   function Native_Write_Matches (Data : E.Bytes; Packet, Current : E.Span;
                                   Kind : H.Chain_Kind) return Boolean is
      Source : constant E.Span := F (Data, Packet, "sqlite_write");
      Cursor : constant E.Span := F (Data, Source, "cursor");
      M : constant E.Count := Length (Data, Current);
      Observed : constant E.Span := F (Data, Source, "sql");
      N : constant E.Count := SQL_Column_Count (Kind);
   begin
      if M = 0 or else V (Data, Source).Form /= E.Object_Value
        or else not Text (Data, F (Data, Cursor, "module"), "sqlite3")
        or else not Text (Data, F (Data, Cursor, "class"), "Cursor")
        or else V (Data, F (Data, Cursor, "identity")).Form /= E.Integer_Value
        or else V (Data, F (Data, Source, "lastrowid")).Form /= E.Integer_Value
        or else V (Data, Observed).Form /= E.Object_Value or else Length (Data, Observed) /= N
        or else not A.Same_Encoding (Data, F (Data, Source, "connection_identity"),
          F (Data, Packet, "connection_identity"))
        or else not A.Same_Encoding (Data, F (Data, Source, "store_identity"), F (Data, Packet, "store_identity"))
        or else not A.Same_Encoding (Data, F (Data, Source, "lastrowid"), F (Data, Source, "rowid"))
        or else not A.Same_Encoding (Data, F (Data, Source, "rowid"), F (Data, Element (Data, Current, M - 1), "rowid"))
        or else not A.Same_Encoding (Data, Observed, F (Data, Element (Data, Current, M - 1), "sql"))
        or else not Effect_Table_Schema (Data, F (Data, Source, "schema"), Kind) then return False; end if;
      for I in E.Count range 0 .. N - 1 loop
         declare Cell : constant E.View := V (Data, F (Data, Observed, SQL_Column_Name (Kind, I)));
         begin
            if Cell.Form = E.Null_Value then
               if not SQL_Nullable (Kind, I) then return False; end if;
            elsif Cell.Form /= (if SQL_Integer (Kind, I) then E.Integer_Value else E.Text_Value) then
               return False;
            end if;
         end;
      end loop;
      return True;
   end Native_Write_Matches;

   function Column_Name (Column : Verified_Column) return String is
     (case Column is
       when Event_Id_Column => "event_id",
       when World_Instance_Column => "world_instance",
       when Kind_Column => "kind",
       when Actor_Column => "actor",
       when Tool_Column => "tool",
       when Reason_Column => "reason",
       when Path_B64_Column => "path_b64",
       when Path_Display_Column => "path_display",
       when Line_Start_Column => "line_start",
       when Line_End_Column => "line_end",
       when Receipt_Id_Column => "receipt_id",
       when Transaction_Id_Column => "transaction_id",
       when Previous_Receipt_Column => "previous_receipt");

   function Verify_History (Data : E.Bytes; Packet : E.Span)
      return Column_Result is
      SQL : constant E.Span := F (Data, Packet, "sql");
      Payload : constant E.Span := F (Data, Packet, "payload");
      Columns : constant E.Span := F (Data, Packet, "columns");
      Stored : constant E.View := V (Data, F (Data, Packet, "raw"));
      Kind : constant H.Chain_Kind := (if Text (Data, F (Data, Packet, "kind"), "receipts")
        then H.Receipt_Chain else H.Causal_Chain);
      Previous : constant H.Optional_Digest := Digest (Data, F (Data, Packet, "previous"));
      Result : Column_Result;
      function Payload_Name (Column : Verified_Column) return String is
        (case Column is
          when Actor_Column => "actor", when Tool_Column => "tool",
          when Reason_Column => "reason", when Path_B64_Column => "pathB64",
          when Path_Display_Column => "pathDisplay", when Line_Start_Column => "lineStart",
          when Line_End_Column => "lineEnd", when Receipt_Id_Column => "receiptId",
          when Transaction_Id_Column => "transactionId",
          when Previous_Receipt_Column => "previousReceipt",
          when others => "");
      function Source_Equals (Expected, Source : E.Span) return Boolean is
        (if Source.Length = 0 then Is_Null (Data, Expected)
         else A.Same_Encoding (Data, Expected, Source));
      First : constant Verified_Column := (if Kind = H.Causal_Chain then
        Event_Id_Column else Receipt_Id_Column);
      Last : constant Verified_Column := (if Kind = H.Causal_Chain then
        Line_End_Column else Previous_Receipt_Column);
   begin
      if not A.Valid (Data, Packet) or else V (Data, Packet).Form /= E.Object_Value
        or else (not Text (Data, F (Data, Packet, "kind"), "receipts")
          and then not Text (Data, F (Data, Packet, "kind"), "events"))
        or else V (Data, SQL).Form /= E.Object_Value
        or else V (Data, Columns).Form /= E.Object_Value
        or else Stored.Form /= E.Bytes_Value
        or else not E.Bytes_Valid (Data, Stored.Payload)
        or else not Previous.Present then return Result; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, Stored.Payload);
         Root : constant Hash := Payload_Root (Raw, Kind);
         Head : constant Hash := H.Link (Kind, Previous.Value, Root);
      begin
         if not Worldline.Raw_JSON.Ordinary_JSON_Operation_Matches (Raw, Data,
           (Raw'First, Raw'Length), Payload) then return Result; end if;
         for Column in Verified_Column range First .. Last loop
            declare
               Expected : constant E.Span := F (Data, Columns, Column_Name (Column));
               Actual : constant E.Span := F (Data, SQL, Column_Name (Column));
            begin
               if Expected.Length = 0 or else Actual.Length = 0 then return Result; end if;
               if Column = Event_Id_Column then
                  declare Id : constant H.Optional_Digest := Digest (Data, Expected);
                  begin
                     if not Id.Present or else Id.Value /= Head then return Result; end if;
                  end;
               elsif Column in World_Instance_Column | Kind_Column then
                  -- These are actual original str(field) observations, acquired
                  -- in the unchanged verification body after json.loads.
                  if V (Data, Expected).Form /= E.Text_Value then return Result; end if;
               elsif not Source_Equals (Expected, F (Data, Payload, Payload_Name (Column))) then
                  return Result;
               end if;
               if not Python_Equal (Data, Actual, Expected) then
                  Result.Differences := Result.Differences or
                    Interfaces.Shift_Left (Interfaces.Unsigned_32 (1), Verified_Column'Pos (Column));
               end if;
            end;
         end loop;
      end;
      Result.Status := (if Result.Differences = 0 then Ready else Row_Columns_Mismatch);
      return Result;
   end Verify_History;


   function Reference (Data : E.Bytes; Packet : E.Span; Mode : Action) return Reason is
      Payload : constant E.Span := F (Data, Packet, "payload");
      Requester : constant E.Span := F (Data, Packet, "requester");
   begin
      if not A.Valid (Data, Packet) or else V (Data, Packet).Form /= E.Object_Value then return Malformed_Input; end if;
      case Mode is
         when Verify_Retained_Columns =>
            return Verify_History (Data, Packet).Status;
         when History_Predecessor =>
            declare
               Kind : constant H.Chain_Kind := (if Text (Data, F (Data, Packet, "kind"), "receipts")
                 then H.Receipt_Chain else H.Causal_Chain);
               Old : constant E.Span := F (Data, Packet, "old");
            begin
               if not Text (Data, F (Data, Packet, "kind"), "receipts") and then
                 not Text (Data, F (Data, Packet, "kind"), "events") then return Malformed_Input; end if;
               if not History (Data, Old, Kind) then return History_Invalid; end if;
               if not Captured_Head_Is (Data, Old, F (Data, Packet, "expected_previous")) then
                  return Captured_Predecessor_Mismatch;
               end if;
               return Ready;
            end;
         when Receipt_Predecessor =>
            return Receipt_Predecessor_Status (Data, F (Data, Packet, "predecessor_source"),
              F (Data, Packet, "previous_row"));
         when Owner_Request | Route_Mutation =>
            declare
               Route : constant Route_Observation := Actual_Route (Data, Packet);
               Truth : Truth_Value;
            begin
               if not Route.Valid then return Route_Observation_Mismatch; end if;
               Truth := Metadata_Truth (Data, (if Mode = Owner_Request then
                 Route.Owner_Metadata else Route.Mutation_Metadata));
               if Truth = Truth_Invalid then return Malformed_Input;
               elsif Truth = Truth_Missing then return Truth_Observation_Required; end if;
               if Mode = Route_Mutation then
                  return (if Truth = Truth_True then Ready_Mutating else Ready);
               end if;
               if Truth = Truth_False then return Ready; end if;
               if Is_Null (Data, F (Data, Packet, "peer_uid")) then return Peer_Observation_Required; end if;
               if V (Data, F (Data, Packet, "peer_uid")).Form /= E.Integer_Value
                 or else V (Data, F (Data, Packet, "daemon_uid")).Form /= E.Integer_Value then return Malformed_Input; end if;
               if not Python_Equal (Data, F (Data, Packet, "peer_uid"),
                 F (Data, Packet, "daemon_uid")) then return Needs_Daemon_Account; end if;
               return Ready;
            end;
         when Reserved_Claim =>
            if Reserved_Actor_Name (Data, F (Data, Packet, "actor_normalized")) then return Reserved_Actor; end if;
            if F (Data, Packet, "kind_normalized").Length = 0 then return Kind_Observation_Required; end if;
            if Reserved_Kind_Name (Data, F (Data, Packet, "kind_normalized")) then return Reserved_Kind; end if;
            return Ready;
         when Event_Schema | Receipt_Schema =>
            declare Status : constant Reason := Schema_Status
              (Data, F (Data, Packet, "schema_metadata"));
            begin
               if Status /= Ready then return Status; end if;
            end;
            if Mode = Event_Schema then
               declare Truth : constant Truth_Value :=
                 Metadata_Truth (Data, F (Data, Packet, "authored_metadata"));
               begin
                  if Truth = Truth_Invalid then return Malformed_Input;
                  elsif Truth = Truth_Missing then return Truth_Observation_Required;
                  elsif Truth = Truth_False then
                     if F (Data, Packet, "actor_normalized").Length = 0 then return Claim_Observation_Required; end if;
                     if Reserved_Actor_Name (Data, F (Data, Packet, "actor_normalized")) then return Reserved_Actor; end if;
                     if Reserved_Kind_Name (Data, F (Data, Packet, "kind_normalized")) then return Reserved_Kind; end if;
                  else return Ready_Authored;
                  end if;
               end;
            end if;
            if Mode = Receipt_Schema then
               declare Source : constant Requester_Source := Requester_Profile (Data, Requester);
               begin
                  if Source = Invalid_Source or else (Source /= Ordinary_Source and then not
                    Python_Equal (Data, F (Data, Payload, "requesterBinding"), Requester))
                  then return Requester_Mismatch; end if;
                  return Receipt_Name_Status (Data, F (Data, Packet, "receipt_keys"),
                    F (Data, Packet, "set_observation"), Source /= Ordinary_Source);
               end;
            end if;
            return Ready;
         when Append_Preflight | Append_Postflight | Append_Source_Postflight =>
            declare
               Kind : constant H.Chain_Kind := (if Text (Data, F (Data, Packet, "kind"), "receipts")
                 then H.Receipt_Chain else H.Causal_Chain);
               Old : constant E.Span := F (Data, Packet, "old");
               Current : constant E.Span := F (Data, Packet, "current");
               N : constant E.Count := Length (Data, Old);
               M : constant E.Count := Length (Data, Current);
               Expected : constant E.Span := F (Data, Packet, "expected");
            begin
               if not Text (Data, F (Data, Packet, "kind"), "receipts") and then
                 not Text (Data, F (Data, Packet, "kind"), "events") then return Malformed_Input; end if;
               if not History (Data, Old, Kind) then return History_Invalid; end if;
               if Kind = H.Receipt_Chain and then Mode /= Append_Postflight then
                  declare
                     Row : constant E.Span := F (Data, Packet, "previous_row");
                     Status : constant Reason := Receipt_Predecessor_Status
                       (Data, F (Data, Packet, "predecessor_source"), Row);
                  begin
                     if Status /= Ready then return Status; end if;
                     if (N = 0 and then not Is_Null (Data, Row)) or else
                       (N > 0 and then (not A.Same_Encoding (Data, F (Data, Row, "receipt_id"),
                         F (Data, Row_SQL (Data, Old, N - 1), "receipt_id"))
                         or else not A.Same_Encoding (Data, F (Data, Row, "chain_hash"),
                           F (Data, Row_SQL (Data, Old, N - 1), "chain_hash"))))
                     then return Captured_Predecessor_Mismatch; end if;
                  end;
               end if;
               declare Source : constant Requester_Source := Requester_Profile (Data, Requester);
               begin
                  if Source = Invalid_Source or else (Source /= Ordinary_Source and then not
                    Python_Equal (Data, F (Data, Payload, "requesterBinding"), Requester))
                  then return Requester_Mismatch; end if;
               end;
               if Mode = Append_Preflight then
                  declare
                     Schema : constant Reason := Schema_Status (Data, F (Data, Packet, "live_schema"));
                     View : constant E.View := V (Data, Expected);
                     Previous : constant H.Optional_Digest := (if N = 0 then (True, Zero_Hash)
                       else Digest (Data, F (Data, Row_SQL (Data, Old, N - 1), "chain_hash")));
                  begin
                     if Schema /= Ready then return Schema; end if;
                     if View.Form /= E.Bytes_Value or else not E.Bytes_Valid (Data, View.Payload)
                       or else not Previous.Present then return Malformed_Input; end if;
                     declare Raw : constant E.Bytes := E.Materialize (Data, View.Payload);
                     begin
                        if not Worldline.Raw_JSON.Ordinary_JSON_Operation_Matches (Raw, Data,
                          (Raw'First, Raw'Length), Payload) then return Actual_Write_Mismatch; end if;
                        if not Hash_Observation (Data, F (Data, Packet, "expected_previous"), Previous.Value) then
                           return Captured_Predecessor_Mismatch;
                        end if;
                        if not Hash_Observation (Data, F (Data, Packet, "expected_head"),
                          H.Link (Kind, Previous.Value, Payload_Root (Raw, Kind))) then return Captured_Head_Mismatch; end if;
                     end;
                     return Ready;
                  end;
               end if;
               if M <= N or else M - N /= 1 then return Complete_Prefix_Changed; end if;
               if N > 0 then
                  for I in E.Count range 0 .. N - 1 loop
                     if not A.Same_Encoding (Data, Element (Data, Old, I), Element (Data, Current, I)) then
                        return Complete_Prefix_Changed;
                     end if;
                  end loop;
               end if;
               if not Same_Raw (Data, F (Data, Element (Data, Current, N), "raw"), Expected)
                 or else not A.Same_Encoding (Data, F (Data, Element (Data, Current, N), "payload"), Payload)
               then return Actual_Write_Mismatch; end if;
               if Mode = Append_Source_Postflight and then not Native_Write_Matches (Data, Packet, Current, Kind) then
                  return Actual_Write_Mismatch;
               end if;
               if not History (Data, Current, Kind) then return History_Invalid; end if;
               if F (Data, Packet, "expected_head").Length > 0 and then not
                 Captured_Head_Is (Data, Current, F (Data, Packet, "expected_head")) then return Captured_Head_Mismatch; end if;
               return Ready;
            end;
      end case;
   end Reference;
   function Decide (Data : E.Bytes; Packet : E.Span; Mode : Action) return Reason is
     (Reference (Data, Packet, Mode));
end Worldline.Ordinary_Receipt_Policy;
