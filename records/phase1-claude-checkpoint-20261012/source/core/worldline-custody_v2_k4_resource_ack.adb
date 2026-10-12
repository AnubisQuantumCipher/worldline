with Interfaces;
with Ada.Characters.Latin_1;
with Canonical_Artifacts;
with Resource_Run_Ledger_Wire;
with Worldline.Custody_V2_Domain_Hmac;
with Worldline.Custody_V2_Owner_Correspondence;
with Worldline.Retained_Evidence_Replay;
package body Worldline.Custody_V2_K4_Resource_Ack with SPARK_Mode is
   package V renames L.V;
   package S renames V.S;
   package OA renames S.A;
   package R renames Worldline.Retained_Evidence_Replay;
   package J renames Canonical_Artifacts;
   package W renames Resource_Run_Ledger_Wire;
   package H renames Worldline.Custody_V2_Domain_Hmac;
   package OC renames Worldline.Custody_V2_Owner_Correspondence;
   use type E.Count;
   use type E.Value_Kind;
   use type E.Bytes;
   use type H.C.SHA.Digest;
   use type E.Q.Byte;
   use type J.JSON_Kind;
   use type J.Genesis_Correspondence;
   use type W.U8;
   use type W.U32;
   use type W.I64;
   use type R.Replay_State;
   use type R.Scoped_Entry;
   use type Interfaces.Unsigned_32;
   function Sum (Data : E.Bytes) return H.SHA.Digest is
     (H.C.G.Hash (Data, (Data'First, Data'Length)));
   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span
     renames R.Archive_Field;
   function JF (Data : E.Bytes; Item : E.Span; Name : String) return E.Span
     renames J.Canonical_JSON_Field;
   function Text (Data : E.Bytes; Item : E.Span; Word : String) return Boolean is
     (if S.Valid (Data, Item) then S.Text_Is (Data, Item, Word)
      else OA.Valid (Data, Item) and then
         E.Text_Is (Data, E.Decode (Data, Item, E.Operation), Word));
   function JT (Data : E.Bytes; Item : E.Span; Word : String) return Boolean is
     (J.String_Is (Data, Item, J.Prefix (Data, Item, 0), Word));
   function Count (Data : E.Bytes; Item : E.Span) return E.Count is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if S.Valid (Data, Item) then return V.Count (Data, Item);
      elsif OA.Valid (Data, Item) and then View.Form in E.List_Value | E.Tuple_Value then
         return E.Array_Length (Data, View.Children);
      else return 0; end if;
   end Count;
   function Element (Data : E.Bytes; Item : E.Span; I : E.Count) return E.Span is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if S.Valid (Data, Item) then return V.Element (Data, Item, I);
      elsif OA.Valid (Data, Item) and then View.Form in E.List_Value | E.Tuple_Value then
         return E.Array_Element (Data, View.Children, I);
      else return (1, 0); end if;
   end Element;
   function JC (Data : E.Bytes; Item : E.Span) return E.Count is
      Root : constant J.JSON_Node := J.JSON_Prefix (Data, Item, 0);
      Offset : E.Count := 1;
      Found : E.Count := 0;
   begin
      if not Root.Valid or else Root.Form not in J.Array_JSON_Value | J.Object_JSON_Value then return 0; end if;
      while Offset < Root.After - 1 loop
         pragma Loop_Variant (Increases => Offset);
         declare Child : constant J.JSON_Node := J.JSON_Prefix (Data, Item, Offset); begin
            if not Child.Valid then return 0; end if;
            Offset := Child.After;
            if Root.Form = J.Object_JSON_Value then
               if Offset >= Root.After or else Data (Item.First + Offset) /= Character'Pos (':') then return 0; end if;
               declare Value : constant J.JSON_Node := J.JSON_Prefix (Data, Item, Offset + 1); begin
                  if not Value.Valid then return 0; end if;
                  Offset := Value.After;
               end;
            end if;
            Found := Found + 1;
            if Offset < Root.After - 1 then Offset := Offset + 1; end if;
         end;
      end loop;
      return Found;
   end JC;
   function JA (Data : E.Bytes; Item : E.Span; I : E.Count) return E.Span is
      Root : constant J.JSON_Node := J.JSON_Prefix (Data, Item, 0);
      Offset : E.Count := 1;
      Ordinal : E.Count := 0;
   begin
      if not Root.Valid or else Root.Form /= J.Array_JSON_Value then return (1, 0); end if;
      while Offset < Root.After - 1 loop
         pragma Loop_Variant (Increases => Offset);
         declare Child : constant J.JSON_Node := J.JSON_Prefix (Data, Item, Offset); begin
            if not Child.Valid then return (1, 0); end if;
            if Ordinal = I then return J.Part (Item, Child.First, Child.After); end if;
            Ordinal := Ordinal + 1; Offset := Child.After;
            if Offset < Root.After - 1 then Offset := Offset + 1; end if;
         end;
      end loop;
      return (1, 0);
   end JA;
   function Raw_Same (A, B : E.Bytes; X, Y : E.Span) return Boolean is
     (J.P.Valid (A, X) and then J.P.Valid (B, Y) and then X.Length > 0 and then
      X.Length = Y.Length and then
      (for all I in E.Count range 1 .. X.Length => A (X.First + I - 1) = B (Y.First + I - 1)));
   function Match (JSON_Data, Archive_Data : E.Bytes; Raw, Encoded : E.Span) return Boolean is
     (J.Operation_Archive_JSON_Matches (JSON_Data, Archive_Data, Raw, Encoded));
   function Scoped_Match (JSON_Data, Archive_Data : E.Bytes; Raw, Encoded : E.Span) return Boolean is
     (J.Scoped_Archive_JSON_Matches (JSON_Data, Archive_Data, Raw, Encoded) =
         J.Typed_Tree_Matches_Source_Custody_Open);
   function Bytes_OK (Data : E.Bytes; Item : E.Span) return Boolean is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      return (S.Valid (Data, Item) and then V.Valid_Bytes (Data, Item)) or else
        (OA.Valid (Data, Item) and then View.Form = E.Bytes_Value and then E.Bytes_Valid (Data, View.Payload));
   end Bytes_OK;
   function Bytes_Of (Data : E.Bytes; Item : E.Span) return E.Bytes
     with Pre => Bytes_OK (Data, Item)
   is
   begin
      if S.Valid (Data, Item) then return V.Bytes_Value (Data, Item);
      else return E.Materialize (Data, E.Decode (Data, Item, E.Operation).Payload); end if;
   end Bytes_Of;
   function Nibble (B : E.Q.Byte) return E.Q.Byte is
     (if B in Character'Pos ('0') .. Character'Pos ('9') then B - Character'Pos ('0') else B - Character'Pos ('a') + 10);
   function Hex_OK (Data : E.Bytes; Item : E.Span) return Boolean is
   begin
      if not J.P.Valid (Data, Item) or else Item.Length < 2 or else
         Data (Item.First) /= Character'Pos ('"') or else Data (Item.First + Item.Length - 1) /= Character'Pos ('"') or else
         (Item.Length - 2) mod 2 /= 0 then return False; end if;
      return (for all I in E.Count range 1 .. Item.Length - 2 =>
         Data (Item.First + I) in Character'Pos ('0') .. Character'Pos ('9') | Character'Pos ('a') .. Character'Pos ('f'));
   end Hex_OK;
   function Hex (Data : E.Bytes; Item : E.Span) return E.Bytes
     with Pre => Hex_OK (Data, Item)
   is
      Answer : E.Bytes (1 .. (Item.Length - 2) / 2);
   begin
      for I in Answer'Range loop
         Answer (I) := Nibble (Data (Item.First + 1 + (I - 1) * 2)) * 16 +
                       Nibble (Data (Item.First + 2 + (I - 1) * 2));
      end loop;
      return Answer;
   end Hex;
   function Digest_Matches (Data : E.Bytes; Item : E.Span; Sum : H.SHA.Digest) return Boolean is
      Hex_Digits : constant String := "0123456789abcdef";
   begin
      return J.P.Valid (Data, Item) and then Item.Length = Sum'Length * 2 + 2 and then
         Data (Item.First) = Character'Pos ('"') and then Data (Item.First + Item.Length - 1) = Character'Pos ('"') and then
         (for all I in Sum'Range =>
            Data (Item.First + 1 + E.Count (I - Sum'First) * 2) = Character'Pos (Hex_Digits (Integer (Sum (I) / 16) + 1)) and then
            Data (Item.First + 2 + E.Count (I - Sum'First) * 2) = Character'Pos (Hex_Digits (Integer (Sum (I) mod 16) + 1)));
   end Digest_Matches;
   function Ordinal_Is (Data : E.Bytes; Item : E.Span; I : E.Count) return Boolean is
      N : constant V.Count_Result := V.Nonnegative_Count (Data, Item);
   begin return N.Present and then N.Value = I; end Ordinal_Is;
   function Joined (Data : E.Bytes; Word, Base : E.Span; Suffix : String) return Boolean is
   begin
      if not V.Valid_Text (Data, Word) or else not V.Valid_Text (Data, Base) then return False; end if;
      declare A : constant E.Bytes := V.Text_Value (Data, Word); B : constant E.Bytes := V.Text_Value (Data, Base); begin
         return A'Length >= B'Length and then A'Length - B'Length = Suffix'Length and then
            (for all I in B'Range => A (A'First + I - B'First) = B (I)) and then
            (for all I in Suffix'Range => A (A'First + B'Length + E.Count (I - Suffix'First)) = Character'Pos (Suffix (I)));
      end;
   end Joined;
   function Path (Data : E.Bytes; Roster : E.Span; Suffix : String) return E.Span is
      Current : constant E.Span := F (Data, Roster, "current");
      Paths : constant E.Span := F (Data, Current, "paths");
      Base : constant E.Span := F (Data, F (Data, F (Data, Current, "installation"), "paths"), "authority_root");
      Found : E.Span := (1, 0);
   begin
      for I in E.Count range 1 .. Count (Data, Paths) loop
         declare Item : constant E.Span := Element (Data, Paths, I - 1); begin
            if Joined (Data, F (Data, Item, "path"), Base, Suffix) then
               if Found.Length > 0 then return (1, 0); end if;
               Found := Item;
            end if;
         end;
      end loop;
      return Found;
   end Path;
   -- Immutable configurations belong to the actual early approved DATA
   -- envelope, not necessarily the mutable provisioned-state path roster.
   -- Parse original FILE/TAB framing; compare the COMPLETE selected raw bytes.
   function Plain_Is (Data : E.Bytes; Item : E.Span; Word : String) return Boolean is
     (J.P.Valid (Data, Item) and then Item.Length = Word'Length and then
      (for all I in Word'Range => Data (Item.First + E.Count (I - Word'First)) = Character'Pos (Word (I))));
   function Plain_Hex (Data : E.Bytes; Item : E.Span) return Boolean is
     (J.P.Valid (Data,Item) and then Item.Length mod 2 = 0 and then
      (for all I in E.Count range 1 .. Item.Length => Data(Item.First+I-1) in Character'Pos('0') .. Character'Pos('9') | Character'Pos('a') .. Character'Pos('f')));
   function Plain_Hex_Matches (Data, Value : E.Bytes; Item : E.Span) return Boolean is
     (Plain_Hex(Data,Item) and then Item.Length/2=Value'Length and then
      (for all I in Value'Range => Value(I)=Nibble(Data(Item.First+(I-Value'First)*2))*16+Nibble(Data(Item.First+(I-Value'First)*2+1))));
   function Selected_Config (Data : E.Bytes; Roster, Config : E.Span; Suffix : String) return Boolean is
      Current : constant E.Span := F(Data,Roster,"current");
      Source : constant E.Span := F(Data,Current,"source");
      Envelope : constant E.Span := F(Data,Source,"envelope_bytes_hex");
      Base : constant E.Span := F(Data,F(Data,F(Data,Current,"installation"),"paths"),"authority_root");
      Mutable_Path : constant E.Span := Path(Data,Roster,Suffix);
      Found : E.Count := 0;
   begin
      if not Bytes_OK(Data,Config) then return False; end if;
      if Mutable_Path.Length > 0 then
         return Bytes_OK(Data,F(Data,Mutable_Path,"raw")) and then Bytes_Of(Data,Config)=Bytes_Of(Data,F(Data,Mutable_Path,"raw"));
      end if;
      if not V.Valid_Hex_Field(Data,Envelope,"value") or else not V.Valid_Text(Data,Base) then return False; end if;
      declare Raw : constant E.Bytes := V.Hex_Value(Data,Envelope,"value");
              Authority : constant E.Bytes := V.Text_Value(Data,Base);
              Config_Raw : constant E.Bytes := Bytes_Of(Data,Config);
              Start : E.Count := 1;
              type File_Fields is array (E.Count range 1 .. 5) of E.Span;
              Fields : File_Fields := (others => (1, 0));
              Field_Count : E.Count;
              First : E.Count;
              Last : E.Count;
      begin
         while Start <= Raw'Length loop
            pragma Loop_Variant (Increases => Start);
            Last:=Start;
            while Last < Raw'Length and then Raw(Last)/=Character'Pos(Ada.Characters.Latin_1.LF) loop
               pragma Loop_Variant (Increases => Last);
               Last:=Last+1;
            end loop;
            if Raw(Last)/=Character'Pos(Ada.Characters.Latin_1.LF) then return False; end if;
            Field_Count:=0; First:=Start;
            for I in Start .. Last loop
               if I=Last or else Raw(I)=Character'Pos(Ada.Characters.Latin_1.HT) then
                  if Field_Count<5 then Field_Count:=Field_Count+1; Fields(Field_Count):=(First,I-First); else Field_Count:=6; exit; end if;
                  if I<Last then First:=I+1; end if;
               end if;
            end loop;
            if Field_Count=5 and then Plain_Is(Raw,Fields(1),"FILE") and then Plain_Is(Raw,Fields(2),"DATA") and then Plain_Hex(Raw,Fields(3)) then
               if Fields(3).Length/2 >= Authority'Length and then Fields(3).Length/2-Authority'Length=Suffix'Length and then
                  (for all I in Authority'Range => Authority(I)=Nibble(Raw(Fields(3).First+(I-Authority'First)*2))*16+Nibble(Raw(Fields(3).First+(I-Authority'First)*2+1))) and then
                  (for all I in Suffix'Range => Character'Pos(Suffix(I))=Integer(Nibble(Raw(Fields(3).First+(Authority'Length+E.Count(I-Suffix'First))*2))*16+Nibble(Raw(Fields(3).First+(Authority'Length+E.Count(I-Suffix'First))*2+1)))) then
                  if not Plain_Hex_Matches(Raw,Config_Raw,Fields(5)) then return False; end if;
                  Found:=Found+1;
               end if;
            end if;
            if Last=Raw'Length then exit; end if;
            Start:=Last+1;
         end loop;
      end;
      return Found=1;
   end Selected_Config;
   function Table (Data : E.Bytes; Database : E.Span; Name, Columns : String; Width : E.Count) return E.Span is
      Tables : constant E.Span := F (Data, Database, "tables");
      Found : E.Span := (1, 0);
      Start : Positive;
      Ordinal : E.Count;
   begin
      for I in E.Count range 1 .. Count (Data, Tables) loop
         declare Item : constant E.Span := Element (Data, Tables, I - 1);
                 Cols : constant E.Span := F (Data, Item, "columns"); begin
            if Text (Data, F (Data, Item, "name"), Name) then
               if Found.Length > 0 or else Count (Data, Cols) /= Width then return (1, 0); end if;
               Start := Columns'First; Ordinal := 0;
               for K in Columns'Range loop
                  if Columns (K) = ',' then
                     if not Text (Data, Element (Data, Element (Data, Cols, Ordinal), 1), Columns (Start .. K - 1)) then return (1, 0); end if;
                     Start := K + 1; Ordinal := Ordinal + 1;
                  end if;
               end loop;
               if not Text (Data, Element (Data, Element (Data, Cols, Ordinal), 1), Columns (Start .. Columns'Last)) then return (1, 0); end if;
               Found := F (Data, Item, "rows");
            end if;
         end;
      end loop;
      return Found;
   end Table;
   function Rows_Match (Data : E.Bytes; Actual, Profile : E.Span; Width : E.Count) return Boolean is
   begin
      if not V.Is_Sequence (Data, Actual) or else not V.Is_Sequence (Data, Profile) or else Count (Data, Actual) /= Count (Data, Profile) then return False; end if;
      for I in E.Count range 1 .. Count (Data, Actual) loop
         declare A : constant E.Span := Element (Data, Actual, I - 1); B : constant E.Span := Element (Data, Profile, I - 1); begin
            if Count (Data, A) /= Width + 1 or else Count (Data, B) /= Width then return False; end if;
            for K in E.Count range 0 .. Width - 1 loop
               if not OA.Same_Encoding (Data, Element (Data, A, K + 1), Element (Data, B, K)) then return False; end if;
            end loop;
         end;
      end loop;
      return True;
   end Rows_Match;
   -- Complete original DTO decoding feeds the unchanged whole-ledger native
   -- policy. Magnitudes/epochs remain arbitrary-length little-endian bytes.
   function Original_Ready (Data : E.Bytes; Event : E.Span) return Boolean is
      Arena : E.Bytes (1 .. Event.Length) := (others => 0);
      Used : E.Count := 0;
      Good : Boolean := J.Canonical_JSON_Valid (Data, Event);
      function Null_Is (Item : E.Span) return Boolean is
        (J.JSON_Prefix (Data, Item, 0).Form = J.Null_JSON_Value);
      function Shape (Item : E.Span; Name : String; Fields : E.Count) return Boolean is
        (JC (Data, Item) = Fields + 2 and then JT (Data, JF (Data, Item, "type"), Name) and then
         JF (Data, Item, "schema_version").Length = 1 and then
         Data (JF (Data, Item, "schema_version").First) = Character'Pos ('1'));
      procedure Append (Item : E.Span; Answer : out E.Span) is
      begin
         Answer := (1,0);
         if not Good or else not Hex_OK (Data, Item) then Good := False; return; end if;
         declare Length : constant E.Count := (Item.Length - 2) / 2; begin
            if Length > Arena'Length - Used then Good := False; return; end if;
            Answer := (if Length = 0 then (1, 0) else (Used + 1, Length));
            for I in E.Count range 1 .. Length loop
               Used := Used + 1;
               Arena (Used) := Nibble (Data (Item.First + 1 + (I - 1) * 2)) * 16 +
                               Nibble (Data (Item.First + 2 + (I - 1) * 2));
            end loop;
         end;
      end Append;
      procedure Id (Item : E.Span; Answer : out W.Raw_Id) is
         Encoded : E.Span;
      begin
         if Null_Is (Item) then Answer := (0,1,0); return; end if;
         if JC (Data, Item) /= 1 then Good := False; end if;
         Append (JF (Data, Item, "bytes"), Encoded);
         Answer := (1, W.I64 (Encoded.First), W.I64 (Encoded.Length));
      end Id;
      procedure Quantity (Item : E.Span; Answer : out W.Raw_Quantity) is
         Encoded : E.Span;
         Negative : W.U8 := 0;
         Sign : constant E.Span := JF (Data, Item, "negative");
      begin
         if JC (Data, Item) /= 2 or else J.JSON_Prefix (Data, Sign, 0).Form /= J.Boolean_JSON_Value then Good := False; end if;
         if Sign.Length = 4 then Negative := 1; end if;
         Append (JF (Data, Item, "magnitude"), Encoded);
         if Encoded.Length = 0 then
            if Negative = 1 then Good := False; end if;
         elsif Arena (Encoded.First + Encoded.Length - 1) = 0 then Good := False;
         end if;
         Answer := (Negative, W.I64 (Encoded.First), W.I64 (Encoded.Length));
      end Quantity;
      procedure Epoch (Item : E.Span; Answer : out W.Raw_Epoch) is
      begin
         if Null_Is (Item) then Answer := (0,(0,1,0)); return; end if;
         Answer.Present := 1; Quantity (Item, Answer.Value);
      end Epoch;
      procedure Charge_Kind (Item : E.Span; Answer : out W.U8) is
      begin
         for Value in W.L.Charge_Kind loop
            if JT (Data, Item, W.L.Charge_Kind'Image (Value)) then Answer := W.U8 (W.L.Charge_Kind'Pos (Value)); return; end if;
         end loop;
         Good := False; Answer := 0;
      end Charge_Kind;
      procedure Phase (Item : E.Span; Answer : out W.U8) is
      begin
         for Value in W.L.Phase loop
            if JT (Data, Item, W.L.Phase'Image (Value)) then Answer := W.U8 (W.L.Phase'Pos (Value)); return; end if;
         end loop;
         Good := False; Answer := 0;
      end Phase;
      procedure Liveness (Item : E.Span; Answer : out W.U8) is
      begin
         for Value in W.L.Liveness loop
            if JT (Data, Item, W.L.Liveness'Image (Value)) then Answer := W.U8 (W.L.Liveness'Pos (Value)); return; end if;
         end loop;
         Good := False; Answer := 0;
      end Liveness;
      procedure Operation (Item : E.Span; Answer : out W.U8) is
      begin
         for Value in W.L.Operation loop
            if JT (Data, Item, W.L.Operation'Image (Value)) then Answer := W.U8 (W.L.Operation'Pos (Value)); return; end if;
         end loop;
         Good := False; Answer := 0;
      end Operation;
      procedure Context (Item : E.Span; Answer : out W.Raw_Context) is
      begin
         if not Shape (Item, "RunContext", 9) then Good := False; end if;
         Id (JF (Data, Item, "universe"), Answer.universe);
         Id (JF (Data, Item, "policy"), Answer.policy);
         Id (JF (Data, Item, "resource"), Answer.resource);
         Id (JF (Data, Item, "unit"), Answer.unit);
         Id (JF (Data, Item, "instance"), Answer.instance);
         Id (JF (Data, Item, "host"), Answer.host);
         Id (JF (Data, Item, "boot"), Answer.boot);
         Id (JF (Data, Item, "authority"), Answer.authority);
         Epoch (JF (Data, Item, "policy_epoch"), Answer.policy_epoch);
      end Context;
      procedure Binding (Item : E.Span; Answer : out W.Raw_Binding) is
      begin
         if not Shape (Item, "RunBinding", 10) then Good := False; end if;
         Id (JF (Data, Item, "reservation"), Answer.reservation);
         Id (JF (Data, Item, "operation"), Answer.operation);
         Id (JF (Data, Item, "owner"), Answer.owner);
         Id (JF (Data, Item, "workload"), Answer.workload);
         Id (JF (Data, Item, "universe_head"), Answer.universe_head);
         Id (JF (Data, Item, "capability"), Answer.capability);
         Id (JF (Data, Item, "grant_use"), Answer.grant_use);
         Id (JF (Data, Item, "payload"), Answer.payload);
         Id (JF (Data, Item, "provenance"), Answer.provenance);
         Epoch (JF (Data, Item, "resource_epoch"), Answer.resource_epoch);
      end Binding;
      procedure Row (Item : E.Span; Answer : out W.Raw_Row) is
      begin
         if Null_Is (Item) then
            Answer :=
              (Scope => ((0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,(0,1,0))),
               Bound => ((0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,(0,1,0))),
               Parent => (0,1,0), Kind => 0, State => 0, Amount => (0,1,0), Observed_Usage => (0,(0,1,0)),
               Planned_Unit => (0,1,0), Actual_Unit => (0,1,0), Cgroup => (0,1,0), Invocation => (0,1,0));
            return;
         end if;
         if not Shape (Item, "RunRow", 11) then Good := False; end if;
         Context (JF (Data, Item, "scope"), Answer.scope);
         Binding (JF (Data, Item, "bound"), Answer.bound);
         Id (JF (Data, Item, "parent"), Answer.parent);
         Charge_Kind (JF (Data, Item, "kind"), Answer.kind);
         Phase (JF (Data, Item, "state"), Answer.state);
         Quantity (JF (Data, Item, "amount"), Answer.amount);
         Epoch (JF (Data, Item, "observed_usage"), Answer.observed_usage);
         Id (JF (Data, Item, "planned_unit"), Answer.planned_unit);
         Id (JF (Data, Item, "actual_unit"), Answer.actual_unit);
         Id (JF (Data, Item, "cgroup"), Answer.cgroup);
         Id (JF (Data, Item, "invocation"), Answer.invocation);
      end Row;
      procedure State (Item : E.Span; Answer : out W.Raw_State) is
      begin
         if not Shape (Item, "RunState", 7) then Good := False; end if;
         Context (JF (Data, Item, "scope"), Answer.scope);
         Epoch (JF (Data, Item, "resource_epoch"), Answer.resource_epoch);
         Id (JF (Data, Item, "universe_head"), Answer.universe_head);
         Id (JF (Data, Item, "ledger_head"), Answer.ledger_head);
         Quantity (JF (Data, Item, "capacity"), Answer.capacity);
         Quantity (JF (Data, Item, "held_total"), Answer.held_total);
         Quantity (JF (Data, Item, "charged_total"), Answer.charged_total);
      end State;
      procedure Native (Item : E.Span; Answer : out W.Raw_Native) is
      begin
         if not Shape (Item, "RunObservation", 8) then Good := False; end if;
         Context (JF (Data, Item, "scope"), Answer.scope);
         Epoch (JF (Data, Item, "resource_epoch"), Answer.resource_epoch);
         Binding (JF (Data, Item, "bound"), Answer.bound);
         Id (JF (Data, Item, "actual_unit"), Answer.actual_unit);
         Id (JF (Data, Item, "cgroup"), Answer.cgroup);
         Id (JF (Data, Item, "invocation"), Answer.invocation);
         Id (JF (Data, Item, "observation_head"), Answer.observation_head);
         Liveness (JF (Data, Item, "observed"), Answer.observed);
      end Native;
      procedure Request (Item : E.Span; Answer : out W.Raw_Request) is
      begin
         if not Shape (Item, "RunRequest", 10) then Good := False; end if;
         Operation (JF (Data, Item, "kind"), Answer.kind);
         Context (JF (Data, Item, "scope"), Answer.scope);
         Epoch (JF (Data, Item, "expected_epoch"), Answer.expected_epoch);
         Id (JF (Data, Item, "expected_ledger_head"), Answer.expected_ledger_head);
         Id (JF (Data, Item, "request_id"), Answer.request_id);
         Id (JF (Data, Item, "reservation"), Answer.reservation);
         Id (JF (Data, Item, "operation_id"), Answer.operation_id);
         Id (JF (Data, Item, "requester"), Answer.requester);
         Binding (JF (Data, Item, "bound"), Answer.bound);
         Row (JF (Data, Item, "new_row"), Answer.new_row);
      end Request;
      Before_JSON : constant E.Span := JF (Data, Event, "before_rows");
      After_JSON : constant E.Span := JF (Data, Event, "proposed_rows");
      Native_JSON : constant E.Span := JF (Data, Event, "observed");
      Before_Rows : W.Raw_Row_Array (1 .. JC (Data, Before_JSON)) with Relaxed_Initialization;
      After_Rows : W.Raw_Row_Array (1 .. JC (Data, After_JSON)) with Relaxed_Initialization;
      Native_Rows : W.Raw_Native_Array (1 .. JC (Data, Native_JSON)) with Relaxed_Initialization;
      Packet : W.Raw_Packet;
   begin
      Packet.Schema_Version := 1;
      State (JF (Data, Event, "before"), Packet.Before_State);
      State (JF (Data, Event, "proposed"), Packet.Proposed_State);
      Request (JF (Data, Event, "request"), Packet.Intent);
      for I in Before_Rows'Range loop
         pragma Loop_Invariant (for all J in Before_Rows'First .. I - 1 => Before_Rows (J)'Initialized);
         Row (JA (Data, Before_JSON, I - 1), Before_Rows (I));
      end loop;
      for I in After_Rows'Range loop
         pragma Loop_Invariant (for all J in After_Rows'First .. I - 1 => After_Rows (J)'Initialized);
         Row (JA (Data, After_JSON, I - 1), After_Rows (I));
      end loop;
      for I in Native_Rows'Range loop
         pragma Loop_Invariant (for all J in Native_Rows'First .. I - 1 => Native_Rows (J)'Initialized);
         Native (JA (Data, Native_JSON, I - 1), Native_Rows (I));
      end loop;
      return Good and then
         J.JSON_Prefix (Data, Before_JSON, 0).Form = J.Array_JSON_Value and then
         J.JSON_Prefix (Data, After_JSON, 0).Form = J.Array_JSON_Value and then
         J.JSON_Prefix (Data, Native_JSON, 0).Form = J.Array_JSON_Value and then
         W.Well_Formed (Arena (1 .. Used), Packet, Before_Rows, After_Rows, Native_Rows) and then
         W.Decide (Arena (1 .. Used), Packet, Before_Rows, After_Rows, Native_Rows).Status = W.L.Status'Pos (W.L.Ready);
   end Original_Ready;
   function Payload_OK (Data : E.Bytes; Item : E.Span; Kind : E.Value_Kind) return Boolean is
      X : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      return OA.Valid (Data, Item) and then X.Form = Kind and then E.Bytes_Valid (Data, X.Payload);
   end Payload_OK;
   function Record_Name_Is (Data : E.Bytes; Item : E.Byte_View; Name : String) return Boolean is
   begin
      if not E.Bytes_Valid (Data, Item) then return False; end if;
      declare Raw : constant E.Bytes := E.Materialize (Data, Item); begin
         return Raw'Length = Name'Length and then
            (for all I in Name'Range => Raw (Raw'First + E.Count (I - Name'First)) = Character'Pos (Name (I)));
      end;
   end Record_Name_Is;
   function Original_Record (Data : E.Bytes; Item : E.Span; Name : String) return Boolean is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      return OA.Valid (Data, Item) and then View.Form = E.Record_Value and then
         Record_Name_Is (Data, View.Module_Name, "worldline.resource_run_ledger") and then
         Record_Name_Is (Data, View.Record_Name, Name) and then OA.Record_Fields (Data, View);
   end Original_Record;
   function Typed_Record (Data : E.Bytes; Item : E.Span; Name : String) return Boolean is
     (if S.Valid (Data, Item) then V.Type_Is (Data, Item, Name)
      else Original_Record (Data, Item, Name));
   function DTO_Matches (JSON_Data, Archive_Data : E.Bytes; Item, Encoded : E.Span; Kind : String) return Boolean
     with Global => null,
       Subprogram_Variant => (Decreases => Item.Length, Decreases => 0);
   function Scalar_Matches (JSON_Data, Archive_Data : E.Bytes; Item, Encoded : E.Span; Kind : String) return Boolean
     with Global => null,
       Subprogram_Variant => (Decreases => Item.Length, Decreases => 1)
   is
      Node : constant J.JSON_Node := J.JSON_Prefix (JSON_Data, Item, 0);
      View : constant E.View := E.Decode (Archive_Data, Encoded, E.Operation);
   begin
      if Node.Form = J.Null_JSON_Value then
         return (OA.Valid (Archive_Data, Encoded) and then View.Form = E.Null_Value) or else
            (S.Valid (Archive_Data, Encoded) and then V.Is_Null (Archive_Data, Encoded));
      end if;
      if Kind = "Id" then
         if JC (JSON_Data, Item) /= 1 or else not Hex_OK (JSON_Data, JF (JSON_Data, Item, "bytes")) or else not Bytes_OK (Archive_Data, Encoded) then return False; end if;
         return Hex (JSON_Data, JF (JSON_Data, Item, "bytes")) = Bytes_Of (Archive_Data, Encoded);
      elsif Kind = "Quantity" or else Kind = "Epoch" then
         if JC (JSON_Data, Item) /= 2 or else not Hex_OK (JSON_Data, JF (JSON_Data, Item, "magnitude")) then return False; end if;
         declare Sign : constant E.Span := JF (JSON_Data, Item, "negative");
                 Magnitude : constant E.Bytes := Hex (JSON_Data, JF (JSON_Data, Item, "magnitude"));
                 Negative : constant Boolean := Sign.Length = 4; begin
            if J.JSON_Prefix (JSON_Data, Sign, 0).Form /= J.Boolean_JSON_Value then return False; end if;
            if S.Valid (Archive_Data, Encoded) and then V.Is_Integer (Archive_Data, Encoded) then
               return Negative = V.Negative (Archive_Data, Encoded) and then Magnitude = V.Magnitude_Value (Archive_Data, Encoded);
            else return Payload_OK (Archive_Data, Encoded, E.Integer_Value) and then View.Sign = Negative and then
               Magnitude = E.Materialize (Archive_Data, View.Payload);
            end if;
         end;
      elsif Kind in "Context" | "Binding" | "Row" | "State" | "Native" | "Request" then
         return DTO_Matches (JSON_Data, Archive_Data, Item, Encoded, Kind);
      else
         return Match (JSON_Data, Archive_Data, Item, Encoded) or else Scoped_Match (JSON_Data, Archive_Data, Item, Encoded);
      end if;
   end Scalar_Matches;
   function DTO_Matches (JSON_Data, Archive_Data : E.Bytes; Item, Encoded : E.Span; Kind : String) return Boolean is
   begin
      if not Typed_Record (Archive_Data, Encoded,
         (if Kind = "Context" then "RunContext" elsif Kind = "Binding" then "RunBinding"
          elsif Kind = "Row" then "RunRow" elsif Kind = "State" then "RunState"
          elsif Kind = "Native" then "RunObservation" else "RunRequest")) then return False; end if;
      if Kind = "Context" then
         return JC (JSON_Data, Item) = 11 and then JT (JSON_Data, JF (JSON_Data, Item, "type"), "RunContext")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "universe"), F (Archive_Data, Encoded, "universe"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "policy"), F (Archive_Data, Encoded, "policy"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "resource"), F (Archive_Data, Encoded, "resource"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "unit"), F (Archive_Data, Encoded, "unit"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "instance"), F (Archive_Data, Encoded, "instance"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "host"), F (Archive_Data, Encoded, "host"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "boot"), F (Archive_Data, Encoded, "boot"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "authority"), F (Archive_Data, Encoded, "authority"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "policy_epoch"), F (Archive_Data, Encoded, "policy_epoch"), "Epoch")
           ;
      end if;
      if Kind = "Binding" then
         return JC (JSON_Data, Item) = 12 and then JT (JSON_Data, JF (JSON_Data, Item, "type"), "RunBinding")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "reservation"), F (Archive_Data, Encoded, "reservation"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "operation"), F (Archive_Data, Encoded, "operation"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "owner"), F (Archive_Data, Encoded, "owner"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "workload"), F (Archive_Data, Encoded, "workload"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "universe_head"), F (Archive_Data, Encoded, "universe_head"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "capability"), F (Archive_Data, Encoded, "capability"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "grant_use"), F (Archive_Data, Encoded, "grant_use"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "payload"), F (Archive_Data, Encoded, "payload"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "provenance"), F (Archive_Data, Encoded, "provenance"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "resource_epoch"), F (Archive_Data, Encoded, "resource_epoch"), "Epoch")
           ;
      end if;
      if Kind = "Row" then
         return JC (JSON_Data, Item) = 13 and then JT (JSON_Data, JF (JSON_Data, Item, "type"), "RunRow")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "scope"), F (Archive_Data, Encoded, "scope"), "Context")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "bound"), F (Archive_Data, Encoded, "bound"), "Binding")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "parent"), F (Archive_Data, Encoded, "parent"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "kind"), F (Archive_Data, Encoded, "kind"), "Charge_Kind")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "state"), F (Archive_Data, Encoded, "state"), "Phase")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "amount"), F (Archive_Data, Encoded, "amount"), "Quantity")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "observed_usage"), F (Archive_Data, Encoded, "observed_usage"), "Epoch")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "planned_unit"), F (Archive_Data, Encoded, "planned_unit"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "actual_unit"), F (Archive_Data, Encoded, "actual_unit"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "cgroup"), F (Archive_Data, Encoded, "cgroup"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "invocation"), F (Archive_Data, Encoded, "invocation"), "Id")
           ;
      end if;
      if Kind = "State" then
         return JC (JSON_Data, Item) = 9 and then JT (JSON_Data, JF (JSON_Data, Item, "type"), "RunState")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "scope"), F (Archive_Data, Encoded, "scope"), "Context")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "resource_epoch"), F (Archive_Data, Encoded, "resource_epoch"), "Epoch")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "universe_head"), F (Archive_Data, Encoded, "universe_head"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "ledger_head"), F (Archive_Data, Encoded, "ledger_head"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "capacity"), F (Archive_Data, Encoded, "capacity"), "Quantity")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "held_total"), F (Archive_Data, Encoded, "held_total"), "Quantity")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "charged_total"), F (Archive_Data, Encoded, "charged_total"), "Quantity")
           ;
      end if;
      if Kind = "Native" then
         return JC (JSON_Data, Item) = 10 and then JT (JSON_Data, JF (JSON_Data, Item, "type"), "RunObservation")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "scope"), F (Archive_Data, Encoded, "scope"), "Context")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "resource_epoch"), F (Archive_Data, Encoded, "resource_epoch"), "Epoch")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "bound"), F (Archive_Data, Encoded, "bound"), "Binding")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "actual_unit"), F (Archive_Data, Encoded, "actual_unit"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "cgroup"), F (Archive_Data, Encoded, "cgroup"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "invocation"), F (Archive_Data, Encoded, "invocation"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "observation_head"), F (Archive_Data, Encoded, "observation_head"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "observed"), F (Archive_Data, Encoded, "observed"), "Liveness")
           ;
      end if;
      if Kind = "Request" then
         return JC (JSON_Data, Item) = 12 and then JT (JSON_Data, JF (JSON_Data, Item, "type"), "RunRequest")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "kind"), F (Archive_Data, Encoded, "kind"), "Operation")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "scope"), F (Archive_Data, Encoded, "scope"), "Context")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "expected_epoch"), F (Archive_Data, Encoded, "expected_epoch"), "Epoch")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "expected_ledger_head"), F (Archive_Data, Encoded, "expected_ledger_head"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "request_id"), F (Archive_Data, Encoded, "request_id"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "reservation"), F (Archive_Data, Encoded, "reservation"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "operation_id"), F (Archive_Data, Encoded, "operation_id"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "requester"), F (Archive_Data, Encoded, "requester"), "Id")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "bound"), F (Archive_Data, Encoded, "bound"), "Binding")
           and then Scalar_Matches (JSON_Data, Archive_Data, JF (JSON_Data, Item, "new_row"), F (Archive_Data, Encoded, "new_row"), "Row")
           ;
      end if;
      return False;
   end DTO_Matches;
   function Operation_Matches (JSON_Data, Archive_Data : E.Bytes; Item, Operation : E.Span) return Boolean is
      View : constant E.View := E.Decode (Archive_Data, Operation, E.Operation);
   begin
      if not Hex_OK (JSON_Data, JF (JSON_Data, Item, "bytes")) or else not Payload_OK (Archive_Data, Operation, E.Text_Value) then return False; end if;
      declare Word : constant E.Bytes := E.Materialize (Archive_Data, View.Payload);
              Value : constant E.Bytes := Hex (JSON_Data, JF (JSON_Data, Item, "bytes")); begin
         return V.Hex_Domain (Word) and then Word'Length = Value'Length * 2 and then
            (for all I in Value'Range => Value (I) = Nibble (Word (Word'First + (I - Value'First) * 2)) * 16 +
               Nibble (Word (Word'First + (I - Value'First) * 2 + 1)));
      end;
   end Operation_Matches;
   function Original_Terminal_Matches (Data, Input_Data : E.Bytes; Request, Capture : E.Span) return Boolean is
      Intent : constant E.Span := F (Input_Data, Capture, "resource_intent");
   begin
      if not Original_Record (Input_Data, Intent, "RunRequest") or else
         not Original_Record (Input_Data, F (Input_Data, Intent, "bound"), "RunBinding") or else
         not Original_Record (Input_Data, F (Input_Data, Intent, "scope"), "RunContext") then return False; end if;
      return (JT (Data, JF (Data, Request, "kind"), "RELEASE_HOLD") or else JT (Data, JF (Data, Request, "kind"), "CHARGE_BUDGET")) and then
         DTO_Matches (Data, Input_Data, JF (Data, Request, "bound"), F (Input_Data, Intent, "bound"), "Binding") and then
         DTO_Matches (Data, Input_Data, JF (Data, Request, "scope"), F (Input_Data, Intent, "scope"), "Context") and then
         Scalar_Matches (Data, Input_Data, JF (Data, Request, "reservation"), F (Input_Data, Intent, "reservation"), "Id") and then
         Operation_Matches (Data, Input_Data, JF (Data, Request, "operation_id"), F (Input_Data, Capture, "operation"));
   end Original_Terminal_Matches;
   function Dictionary_Count (Data : E.Bytes; Item : E.Span) return E.Count is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if S.Valid (Data, Item) then return S.Member_Count (Data, Item);
      elsif OA.Valid (Data, Item) and then View.Form = E.Object_Value then return E.Array_Length (Data, View.Children);
      else return 0; end if;
   end Dictionary_Count;
   function Text_Digest (Data : E.Bytes; Item : E.Span; Sum : H.SHA.Digest) return Boolean is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if not V.Valid_Text (Data, Item) and then not Payload_OK (Data, Item, E.Text_Value) then return False; end if;
      declare Actual : constant E.Bytes := (if V.Valid_Text (Data, Item) then V.Text_Value (Data, Item) else E.Materialize (Data, View.Payload));
              Encoded : E.Bytes (1 .. Actual'Length + 2) := (others => 0); begin
         Encoded (1) := Character'Pos ('"'); Encoded (Encoded'Last) := Character'Pos ('"');
         Encoded (2 .. Encoded'Last - 1) := Actual;
         return Digest_Matches (Encoded, (1, Encoded'Length), Sum);
      end;
   end Text_Digest;
   function Reply_Matches (Raw, Input_Data : E.Bytes; Event, Reply : E.Span; Scoped : Boolean) return Boolean is
      Reply_JSON : constant E.Span := JF (Raw, Event, "reply");
   begin
      if not Text (Input_Data, F (Input_Data, Reply, "status"), "READY") or else
         not Text_Digest (Input_Data, F (Input_Data, Reply, "event_sha256"), Sum (Raw)) then return False; end if;
      if Scoped then
         return Dictionary_Count (Input_Data, Reply) = 7 and then
            (for all K in E.Count range 0 .. 5 => Scoped_Match (Raw, Input_Data,
               JF (Raw, Reply_JSON, (case K is when 0 => "schema", when 1 => "status", when 2 => "request_id", when 3 => "snapshot", when 4 => "native", when others => "prior")),
               F (Input_Data, Reply, (case K is when 0 => "schema", when 1 => "status", when 2 => "request_id", when 3 => "snapshot", when 4 => "native", when others => "prior"))));
      else
         return Dictionary_Count (Input_Data, Reply) = 5 and then
            Match (Raw, Input_Data, JF (Raw, Event, "proposed"), F (Input_Data, Reply, "state")) and then
            Match (Raw, Input_Data, JF (Raw, Event, "proposed_rows"), F (Input_Data, Reply, "rows")) and then
            Match (Raw, Input_Data, JF (Raw, JF (Raw, JF (Raw, Event, "request"), "request_id"), "bytes"), F (Input_Data, Reply, "request_id"));
      end if;
   end Reply_Matches;
   function Original_History
     (Data : E.Bytes; Roster, Context, Profile : E.Span) return Boolean is
      Config_Item : constant E.Span := F (Data, Profile, "config_raw");
      Database : constant E.Span := F (Data, Path (Data, Roster, "/authority/resource/run-state-v1/ledger.sqlite"), "logical_database");
      Meta : constant E.Span := F (Data, Profile, "meta");
      Rows : constant E.Span := F (Data, Profile, "rows");
      Events : constant E.Span := F (Data, Profile, "events");
      Context_Events : constant E.Span := F (Data, Context, "resource_events");
   begin
      if not Text (Data, F (Data, Profile, "family"), "ORIGINAL") or else
         not Selected_Config (Data, Roster, Config_Item, "/authority/resource/run-config-v1.json") or else
         not Rows_Match (Data, Table (Data, Database, "run_meta", "config_sha,genesis,head", 3), Meta, 3) or else
         not Rows_Match (Data, Table (Data, Database, "run_rows", "ordinal,record", 2), Rows, 2) or else
         not Rows_Match (Data, Table (Data, Database, "run_events", "ordinal,request_id,record", 3), Events, 3) or else
         Count (Data, Meta) /= 1 or else Count (Data, Context_Events) /= Count (Data, Events) then return False; end if;
      declare Config : constant E.Bytes := Bytes_Of (Data, Config_Item);
              Config_JSON : constant E.Span := (1, Config'Length);
              Meta_Row : constant E.Span := Element (Data, Meta, 0);
              Genesis_Item : constant E.Span := Element (Data, Meta_Row, 1);
              Head_Item : constant E.Span := Element (Data, Meta_Row, 2); begin
         if not J.Canonical_JSON_Valid (Config, Config_JSON) or else
            not JT (Config, JF (Config, Config_JSON, "schema"), "worldline.protected-resource-config-v1") or else
            not Text_Digest (Data, Element (Data, Meta_Row, 0), Sum (Config)) or else
            not Scoped_Match (Config, Data, JF (Config, Config_JSON, "genesis"), F (Data, Profile, "genesis")) or else
            not Scoped_Match (Config, Data, JF (Config, Config_JSON, "genesis"), F (Data, Context, "resource_genesis")) or else
            not Bytes_OK (Data, Genesis_Item) or else not Bytes_OK (Data, Head_Item) then return False; end if;
         declare Genesis : constant E.Bytes := Bytes_Of (Data, Genesis_Item);
                 Head : constant E.Bytes := Bytes_Of (Data, Head_Item); begin
            if not Raw_Same (Config, Genesis, JF (Config, Config_JSON, "genesis"), (1, Genesis'Length)) then return False; end if;
            for I in E.Count range 1 .. Count (Data, Events) loop
               declare Row : constant E.Span := Element (Data, Events, I - 1);
                       Raw_Item : constant E.Span := Element (Data, Row, 2);
                       RID : constant E.Span := Element (Data, Row, 1);
                       Context_Item : constant E.Span := Element (Data, Context_Events, I - 1); begin
                  if Count (Data, Row) /= 3 or else not Ordinal_Is (Data, Element (Data, Row, 0), I - 1) or else
                     not Bytes_OK (Data, Raw_Item) or else not Bytes_OK (Data, RID) or else
                     not V.Valid_Text (Data, Context_Item) or else not V.Valid_Hex_Field (Data, Context_Item, "value") or else
                     V.Hex_Value (Data, Context_Item, "value") /= Bytes_Of (Data, Raw_Item) then return False; end if;
                  for K in E.Count range 1 .. I - 1 loop
                     if Bytes_Of (Data, RID) = Bytes_Of (Data, Element (Data, Element (Data, Events, K - 1), 1)) then return False; end if;
                  end loop;
                  declare Raw : constant E.Bytes := Bytes_Of (Data, Raw_Item);
                          Event : constant E.Span := (1, Raw'Length);
                          Request : constant E.Span := JF (Raw, Event, "request");
                          Request_ID : constant E.Span := JF (Raw, JF (Raw, Request, "request_id"), "bytes"); begin
                     if not Original_Ready (Raw, Event) or else JC (Raw, Event) not in 6 | 10 or else
                        not Hex_OK (Raw, Request_ID) or else Hex (Raw, Request_ID) /= Bytes_Of (Data, RID) then return False; end if;
                     if JC (Raw, Event) = 10 then
                        if not JT (Raw, JF (Raw, Event, "schema"), "worldline.protected-resource-event-v2") or else
                           JF (Raw, Event, "owner_uid").Length /= 1 or else Raw (JF (Raw, Event, "owner_uid").First) /= Character'Pos ('0') or else
                           not JT (Raw, JF (Raw, JF (Raw, Event, "packet"), "schema"), "worldline.protected-resource-request-v1") or else
                           JC (Raw, JF (Raw, Event, "packet")) /= 4 or else
                           not Raw_Same (Raw, Raw, JF (Raw, JF (Raw, Event, "packet"), "proposed"), JF (Raw, Event, "proposed")) or else
                           not Raw_Same (Raw, Raw, JF (Raw, JF (Raw, Event, "packet"), "rows"), JF (Raw, Event, "proposed_rows")) or else
                           not Raw_Same (Raw, Raw, JF (Raw, JF (Raw, Event, "packet"), "request"), Request) or else
                           JC (Raw, JF (Raw, Event, "result")) /= 4 or else
                           not JT (Raw, JF (Raw, JF (Raw, Event, "result"), "status"), "READY") or else
                           not Raw_Same (Raw, Raw, JF (Raw, JF (Raw, Event, "result"), "state"), JF (Raw, Event, "proposed")) or else
                           not Raw_Same (Raw, Raw, JF (Raw, JF (Raw, Event, "result"), "rows"), JF (Raw, Event, "proposed_rows")) or else
                           not Raw_Same (Raw, Raw, JF (Raw, JF (Raw, Event, "result"), "request_id"), Request_ID) then return False; end if;
                     end if;
                     if I = 1 then
                        if not Raw_Same (Raw, Genesis, JF (Raw, Event, "before"), (1, Genesis'Length)) or else JC (Raw, JF (Raw, Event, "before_rows")) /= 0 then return False; end if;
                     else
                        declare Prev : constant E.Bytes := Bytes_Of (Data, Element (Data, Element (Data, Events, I - 2), 2)); begin
                           if not Raw_Same (Raw, Prev, JF (Raw, Event, "before"), JF (Prev, (1, Prev'Length), "proposed")) or else
                              not Raw_Same (Raw, Prev, JF (Raw, Event, "before_rows"), JF (Prev, (1, Prev'Length), "proposed_rows")) then return False; end if;
                        end;
                     end if;
                     if I = Count (Data, Events) then
                        if not Raw_Same (Raw, Head, JF (Raw, Event, "proposed"), (1, Head'Length)) or else Count (Data, Rows) /= JC (Raw, JF (Raw, Event, "proposed_rows")) then return False; end if;
                        for K in E.Count range 1 .. Count (Data, Rows) loop
                           declare Current_Row : constant E.Span := Element (Data, Rows, K - 1); begin
                              if Count (Data, Current_Row) /= 2 or else not Ordinal_Is (Data, Element (Data, Current_Row, 0), K - 1) or else
                                 not Bytes_OK (Data, Element (Data, Current_Row, 1)) then return False; end if;
                              declare Current_Raw : constant E.Bytes := Bytes_Of (Data, Element (Data, Current_Row, 1)); begin
                                 if not Raw_Same (Raw, Current_Raw, JA (Raw, JF (Raw, Event, "proposed_rows"), K - 1), (1, Current_Raw'Length)) then return False; end if;
                              end;
                           end;
                        end loop;
                     end if;
                  end;
               end;
            end loop;
            if Count (Data, Events) = 0 and then (Count (Data, Rows) /= 0 or else not Raw_Same (Genesis, Head, (1, Genesis'Length), (1, Head'Length))) then return False; end if;
         end;
      end;
      return True;
   end Original_History;
   function Equal_Value (A, B : E.Bytes; X, Y : E.Span; Kind : String) return Boolean is
      VX : constant E.View := E.Decode (A, X, E.Operation);
      VY : constant E.View := E.Decode (B, Y, E.Operation);
   begin
      if Bytes_OK (A, X) and then Bytes_OK (B, Y) then return Bytes_Of (A, X) = Bytes_Of (B, Y); end if;
      if Kind = "Epoch" then
         if V.Is_Null (A, X) or else VX.Form = E.Null_Value then return V.Is_Null (B, Y) or else VY.Form = E.Null_Value; end if;
         if V.Is_Integer (A, X) and then Payload_OK (B, Y, E.Integer_Value) then
            return V.Negative (A, X) = VY.Sign and then V.Magnitude_Value (A, X) = E.Materialize (B, VY.Payload);
         end if;
      end if;
      return False;
   end Equal_Value;
   function Equal_Record (A, B : E.Bytes; X, Y : E.Span; Binding : Boolean) return Boolean is
   begin
      if not Typed_Record (A, X, (if Binding then "RunBinding" else "RunContext")) or else
         not Original_Record (B, Y, (if Binding then "RunBinding" else "RunContext")) then return False; end if;
      if Binding then
         return
            Equal_Value (A, B, F (A, X, "reservation"), F (B, Y, "reservation"), "Id")
            and then Equal_Value (A, B, F (A, X, "operation"), F (B, Y, "operation"), "Id")
            and then Equal_Value (A, B, F (A, X, "owner"), F (B, Y, "owner"), "Id")
            and then Equal_Value (A, B, F (A, X, "workload"), F (B, Y, "workload"), "Id")
            and then Equal_Value (A, B, F (A, X, "universe_head"), F (B, Y, "universe_head"), "Id")
            and then Equal_Value (A, B, F (A, X, "capability"), F (B, Y, "capability"), "Id")
            and then Equal_Value (A, B, F (A, X, "grant_use"), F (B, Y, "grant_use"), "Id")
            and then Equal_Value (A, B, F (A, X, "payload"), F (B, Y, "payload"), "Id")
            and then Equal_Value (A, B, F (A, X, "provenance"), F (B, Y, "provenance"), "Id")
            and then Equal_Value (A, B, F (A, X, "resource_epoch"), F (B, Y, "resource_epoch"), "Epoch")
            ;
      else
         return
            Equal_Value (A, B, F (A, X, "universe"), F (B, Y, "universe"), "Id")
            and then Equal_Value (A, B, F (A, X, "policy"), F (B, Y, "policy"), "Id")
            and then Equal_Value (A, B, F (A, X, "resource"), F (B, Y, "resource"), "Id")
            and then Equal_Value (A, B, F (A, X, "unit"), F (B, Y, "unit"), "Id")
            and then Equal_Value (A, B, F (A, X, "instance"), F (B, Y, "instance"), "Id")
            and then Equal_Value (A, B, F (A, X, "host"), F (B, Y, "host"), "Id")
            and then Equal_Value (A, B, F (A, X, "boot"), F (B, Y, "boot"), "Id")
            and then Equal_Value (A, B, F (A, X, "authority"), F (B, Y, "authority"), "Id")
            and then Equal_Value (A, B, F (A, X, "policy_epoch"), F (B, Y, "policy_epoch"), "Epoch")
            ;
      end if;
   end Equal_Record;
   function Scoped_Terminal_Matches (Data, Input_Data : E.Bytes; Request, Capture : E.Span) return Boolean is
      Intent : constant E.Span := F (Input_Data, Capture, "resource_intent");
      Operation : constant E.Span := F (Input_Data, Capture, "operation");
      ID : constant E.Span := F (Data, Request, "operation_id");
      View : constant E.View := E.Decode (Input_Data, Operation, E.Operation);
   begin
      if not Original_Record (Input_Data, Intent, "RunRequest") then return False; end if;
      if not (Text (Data, F (Data, Request, "kind"), "RELEASE_HOLD") or else Text (Data, F (Data, Request, "kind"), "CHARGE_BUDGET")) or else
         not Equal_Record (Data, Input_Data, F (Data, Request, "scope"), F (Input_Data, Intent, "scope"), False) or else
         not Equal_Record (Data, Input_Data, F (Data, Request, "bound"), F (Input_Data, Intent, "bound"), True) or else
         not Equal_Value (Data, Input_Data, F (Data, Request, "reservation"), F (Input_Data, Intent, "reservation"), "Id") or else
         not Bytes_OK (Data, ID) or else not Payload_OK (Input_Data, Operation, E.Text_Value) then return False; end if;
      declare Word : constant E.Bytes := E.Materialize (Input_Data, View.Payload);
              Value : constant E.Bytes := Bytes_Of (Data, ID); begin
         return V.Hex_Domain (Word) and then Word'Length = Value'Length * 2 and then
            (for all I in Value'Range => Value (I) = Nibble (Word (Word'First + (I - Value'First) * 2)) * 16 +
               Nibble (Word (Word'First + (I - Value'First) * 2 + 1)));
      end;
   end Scoped_Terminal_Matches;
   function SF (Data : E.Bytes; Item : E.Span; Name : String) return E.Span is
     (JF (Data, JF (Data, Item, "fields"), Name));
   function Snapshot_Matches (A, B : E.Bytes; Packet, Snapshot : E.Span; After : Boolean) return Boolean is
   begin
      return JC (B, JF (B, Snapshot, "fields")) = 5 and then
         (for all I in E.Count range 0 .. 4 =>
            Raw_Same (A, B, SF (A, Packet,
               (case I is when 0 => (if After then "proposed" else "before"),
                when 1 => (if After then "proposed_history" else "history"),
                when 2 => (if After then "proposed_rows" else "rows"),
                when 3 => (if After then "proposed_projection" else "projection"),
                when others => (if After then "proposed_buckets" else "buckets"))),
               SF (B, Snapshot, (case I is when 0 => "state", when 1 => "history", when 2 => "rows", when 3 => "projection", when others => "buckets"))));
   end Snapshot_Matches;
   function Scoped_History
     (Data : E.Bytes; Roster, Context, Profile : E.Span) return Boolean is
      Original : constant E.Span := F (Data, Profile, "original");
      Config_Item : constant E.Span := F (Data, Profile, "config_raw");
      Database : constant E.Span := F (Data, Path (Data, Roster, "/authority/resource/run-scoped-state-v1/ledger.sqlite"), "logical_database");
      Key_Item : constant E.Span := F (Data, Path (Data, Roster, "/authority/issuer/state/issuer-key.bin"), "raw");
      Meta : constant E.Span := F (Data, Profile, "meta");
      Events : constant E.Span := F (Data, Profile, "events");
      Replays : constant E.Span := F (Data, Profile, "replay_archives");
      Genesis_Anchor : constant E.Span := F (Data, Profile, "genesis_anchor_raw");
      Head_Anchor : constant E.Span := F (Data, Profile, "head_anchor_raw");
      Genesis_Archive : constant E.Span := F (Data, Profile, "genesis_archive_raw");
      History_Raw : constant E.Span := F (Data, Context, "resource_ack_history_raw");
      Domain : constant String := "WORLDLINE-protected-scoped-resource-journal-v1" & Ada.Characters.Latin_1.NUL;
   begin
      if not Original_History (Data, Roster, Context, Original) or else
         not Selected_Config (Data, Roster, Config_Item, "/authority/resource/run-scoped-config-v1.json") or else
         not Bytes_OK (Data, Key_Item) or else not Bytes_OK (Data, Genesis_Anchor) or else not Bytes_OK (Data, Head_Anchor) or else
         not Bytes_OK (Data, Genesis_Archive) or else not Bytes_OK (Data, History_Raw) or else
         not Rows_Match (Data, Table (Data, Database, "scoped_meta", "binding,genesis,original_prefix,snapshot,head,mac", 6), Meta, 6) or else
         not Rows_Match (Data, Table (Data, Database, "scoped_events", "ordinal,request_id,record,mac", 4), Events, 4) or else
         Count (Data, Meta) /= 1 or else Count (Data, Events) /= Count (Data, Replays) then return False; end if;
      declare Config : constant E.Bytes := Bytes_Of (Data, Config_Item);
              Key : constant E.Bytes := Bytes_Of (Data, Key_Item);
              GA : constant E.Bytes := Bytes_Of (Data, Genesis_Anchor);
              HA : constant E.Bytes := Bytes_Of (Data, Head_Anchor);
              Genesis_Data : constant E.Bytes := Bytes_Of (Data, Genesis_Archive);
              History_Data : constant E.Bytes := Bytes_Of (Data, History_Raw);
              Original_Config : constant E.Bytes := Bytes_Of (Data, F (Data, Original, "config_raw"));
              MR : constant E.Span := Element (Data, Meta, 0); begin
         for K in E.Count range 0 .. 3 loop if not Bytes_OK (Data, Element (Data, MR, K)) then return False; end if; end loop;
         declare Binding : constant E.Bytes := Bytes_Of (Data, Element (Data, MR, 0));
                 Genesis : constant E.Bytes := Bytes_Of (Data, Element (Data, MR, 1));
                 Prefix : constant E.Bytes := Bytes_Of (Data, Element (Data, MR, 2));
                 Snapshot : constant E.Bytes := Bytes_Of (Data, Element (Data, MR, 3));
                 Config_JSON : constant E.Span := (1, Config'Length); begin
            if not OA.Valid (History_Data, (1, History_Data'Length)) or else
               Count (History_Data, (1, History_Data'Length)) /= Count (Data, Events) or else
               not Match (Genesis, Genesis_Data, (1, Genesis'Length), (1, Genesis_Data'Length)) or else
               not S.Valid (Genesis_Data, (1, Genesis_Data'Length)) then return False; end if;
            if not J.Canonical_JSON_Valid (Config, Config_JSON) or else
               not JT (Config, JF (Config, Config_JSON, "schema"), "worldline.protected-scoped-resource-config-v1") or else
               JC (Binding, (1,Binding'Length)) /= 8 or else
               not Raw_Same (Binding, Config, JF (Binding,(1,Binding'Length),"installation_id"), JF (Config,Config_JSON,"installation_id")) or else
               not Scoped_Match (Config, Data, JF (Config,Config_JSON,"installation_id"), F (Data,F (Data,F (Data,Roster,"current"),"installation"),"installation_id")) or else
               not Raw_Same (Binding, Config, JF (Binding,(1,Binding'Length),"gate_config_sha256"), JF (Config,Config_JSON,"gate_config_sha256")) or else
               not Raw_Same (Binding, Original_Config, JF (Binding,(1,Binding'Length),"gate_config_sha256"), JF (Original_Config,(1,Original_Config'Length),"gate_config_sha256")) or else
               not Raw_Same (Binding, Config, JF (Binding,(1,Binding'Length),"native_sha256"), JF (Config,Config_JSON,"native_sha256")) or else
               not Raw_Same (Binding, Config, JF (Binding,(1,Binding'Length),"sources"), JF (Config,Config_JSON,"sources")) or else
               not Digest_Matches (Binding, JF (Binding,(1,Binding'Length),"original_config_sha256"), Sum (Original_Config)) or else
               not Raw_Same (Config, Genesis, JF (Config, Config_JSON, "genesis"), (1, Genesis'Length)) or else
               not Raw_Same (Config, Prefix, JF (Config, Config_JSON, "original_prefix"), (1, Prefix'Length)) or else
               not Scoped_Match (Binding, Data, (1, Binding'Length), F (Data, Profile, "binding")) or else
               not Scoped_Match (Genesis, Data, (1, Genesis'Length), F (Data, Profile, "genesis")) or else
               not Scoped_Match (Prefix, Data, (1, Prefix'Length), F (Data, Profile, "original_prefix")) or else
               not Digest_Matches (Binding, JF (Binding, (1,Binding'Length), "config_sha256"), Sum (Config)) or else
               not Digest_Matches (Binding, JF (Binding, (1,Binding'Length), "key_sha256"), Sum (Key)) or else
               JC (GA, (1,GA'Length)) /= 3 or else JC (HA, (1,HA'Length)) /= 5 or else
               not J.Canonical_JSON_Valid (GA, (1,GA'Length)) or else not J.Canonical_JSON_Valid (HA, (1,HA'Length)) or else
               not Raw_Same (GA, Binding, JF (GA, (1,GA'Length), "binding"), (1,Binding'Length)) or else
               not Raw_Same (GA, Genesis, JF (GA, (1,GA'Length), "genesis"), (1,Genesis'Length)) or else
               not Raw_Same (GA, Prefix, JF (GA, (1,GA'Length), "original_prefix"), (1,Prefix'Length)) or else
               not Raw_Same (HA, Binding, JF (HA, (1,HA'Length), "binding"), (1,Binding'Length)) or else
               not Raw_Same (HA, Genesis, JF (HA, (1,HA'Length), "genesis"), (1,Genesis'Length)) or else
               not Raw_Same (HA, Prefix, JF (HA, (1,HA'Length), "original_prefix"), (1,Prefix'Length)) or else
               not Raw_Same (HA, Snapshot, JF (HA, (1,HA'Length), "snapshot"), (1,Snapshot'Length)) or else
               not Match (HA, Data, JF (HA, (1,HA'Length), "head"), Element (Data, MR, 4)) or else
               not Text_Digest (Data, Element (Data, MR, 5), H.Mac (Key, HA, (1,Key'Length), (1,HA'Length), Domain & "head" & Ada.Characters.Latin_1.NUL)) then return False; end if;
            -- The scoped origin freezes the COMPLETE native original history,
            -- not a projected row or a synthetic genesis masquerading as source.
            declare OM : constant E.Span := Element (Data, F (Data, Original, "meta"), 0);
                    OE : constant E.Span := F (Data, Original, "events");
                    ORows : constant E.Span := F (Data, Original, "rows");
                    Old_Head : constant E.Bytes := Bytes_Of (Data, Element (Data, OM, 2)); begin
               if not Raw_Same (Prefix, Old_Head, JF (Prefix,(1,Prefix'Length),"state"),(1,Old_Head'Length)) or else
                  not Scoped_Match (Prefix, Data, JF (Prefix,(1,Prefix'Length),"genesis"), F (Data, Original,"genesis")) or else
                  JC (Prefix, JF (Prefix,(1,Prefix'Length),"rows")) /= Count (Data, ORows) or else
                  JC (Prefix, JF (Prefix,(1,Prefix'Length),"events")) /= Count (Data, OE) then return False; end if;
               if Count (Genesis_Data, F (Genesis_Data,(1,Genesis_Data'Length),"rows")) /= Count (Data,ORows) then return False; end if;
               for I in E.Count range 1 .. Count (Data, ORows) loop
                  declare Old_Row : constant E.Bytes := Bytes_Of (Data, Element (Data, Element (Data, ORows,I-1),1)); begin
                     if not Raw_Same (Prefix, Old_Row, JA (Prefix,JF(Prefix,(1,Prefix'Length),"rows"),I-1),(1,Old_Row'Length)) then return False; end if;
                     if not DTO_Matches (Old_Row, Genesis_Data, (1,Old_Row'Length),
                        Element (Genesis_Data,F (Genesis_Data,(1,Genesis_Data'Length),"rows"),I-1), "Row") then return False; end if;
                  end;
               end loop;
               for I in E.Count range 1 .. Count (Data, OE) loop
                  declare Word : constant E.Span := JA (Prefix, JF(Prefix,(1,Prefix'Length),"events"),I-1); begin
                     if not Hex_OK (Prefix,Word) or else Hex (Prefix,Word) /= Bytes_Of (Data,Element (Data,Element (Data,OE,I-1),2)) then return False; end if;
                  end;
               end loop;
            end;
            for I in E.Count range 1 .. Count (Data, Events) loop
               declare Row : constant E.Span := Element (Data, Events, I-1);
                       Replay : constant E.Span := Element (Data, Replays, I-1); begin
                  if Count (Data, Row) /= 4 or else not Ordinal_Is (Data, Element(Data,Row,0), I-1) or else
                     not Bytes_OK(Data,Element(Data,Row,1)) or else not Bytes_OK(Data,Element(Data,Row,2)) or else not Bytes_OK(Data,Replay) then return False; end if;
                  for K in E.Count range 1 .. I-1 loop
                     if Bytes_Of(Data,Element(Data,Row,1)) = Bytes_Of(Data,Element(Data,Element(Data,Events,K-1),1)) then return False; end if;
                  end loop;
                  declare Raw : constant E.Bytes := Bytes_Of(Data,Element(Data,Row,2));
                          Archive : constant E.Bytes := Bytes_Of(Data,Replay);
                          Event : constant E.Span := (1,Raw'Length);
                          Packet : constant E.Span := JF(Raw,Event,"packet");
                          AP : constant E.Span := F(Archive,(1,Archive'Length),"packet");
                          AN : constant E.Span := F(Archive,(1,Archive'Length),"native");
                          Native : constant R.Scoped_Replay_Result := R.Reestablish_Scoped_Observation(Archive,AN);
                          Reply : constant E.Span := JF(Raw,Event,"reply");
                          RID : constant E.Span := JF(Raw,SF(Raw,SF(Raw,Packet,"request"),"request_id"),"value"); begin
                     if not J.Canonical_JSON_Valid(Raw,Event) or else JC(Raw,Event)/=7 or else
                        not Match (Raw,History_Data,Event,Element (History_Data,(1,History_Data'Length),I-1)) or else
                        not JT(Raw,JF(Raw,Event,"schema"),"worldline.protected-scoped-resource-event-v1") or else
                        not Text_Digest(Data,Element(Data,Row,3),H.Mac(Key,Raw,(1,Key'Length),Event,Domain & "event" & Ada.Characters.Latin_1.NUL)) or else
                        not Raw_Same(Raw,Binding,JF(Raw,Event,"principal"),(1,Binding'Length)) or else
                        not Match(Raw,Archive,Packet,AP) or else not Match(Raw,Archive,JF(Raw,Event,"native"),AN) or else
                        Native.State/=R.Native_Redecided or else Native.Roster_Entry/=R.Check_Entry or else Native.Native_Status/=0 or else
                        not R.Scoped_Material_Matches(Archive,AN,AP) or else not Hex_OK(Raw,RID) or else
                        Hex(Raw,RID)/=Bytes_Of(Data,Element(Data,Row,1)) or else
                        JC(Raw,Reply)/=6 or else not JT(Raw,JF(Raw,Reply,"schema"),"worldline.protected-scoped-resource-reply-v1") or else
                        not JT(Raw,JF(Raw,Reply,"status"),"READY") or else
                        not Raw_Same(Raw,Raw,JF(Raw,Reply,"request_id"),RID) or else
                        not Raw_Same(Raw,Raw,JF(Raw,Reply,"native"),JF(Raw,Event,"native")) or else
                        not Raw_Same(Raw,Raw,JF(Raw,Reply,"prior"),JF(Raw,Event,"prior")) or else
                        not Snapshot_Matches(Raw,Raw,Packet,JF(Raw,Reply,"snapshot"),True) then return False; end if;
                     if I=1 then
                        if not Digest_Matches(Raw,JF(Raw,Event,"prior"),Sum(GA)) or else
                           not Snapshot_Matches(Raw,Genesis,Packet,(1,Genesis'Length),False) then return False; end if;
                     else
                        declare Previous : constant E.Bytes := Bytes_Of(Data,Element(Data,Element(Data,Events,I-2),2)); begin
                           if not Digest_Matches(Raw,JF(Raw,Event,"prior"),Sum(Previous)) or else
                              not Snapshot_Matches(Raw,Previous,Packet,JF(Previous,JF(Previous,(1,Previous'Length),"reply"),"snapshot"),False) then return False; end if;
                        end;
                     end if;
                     if I=Count(Data,Events) and then
                        (not Text_Digest(Data,Element(Data,MR,4),Sum(Raw)) or else not Snapshot_Matches(Raw,Snapshot,Packet,(1,Snapshot'Length),True)) then return False; end if;
                  end;
               end;
            end loop;
            if Count(Data,Events)=0 and then (not Raw_Same(Genesis,Snapshot,(1,Genesis'Length),(1,Snapshot'Length)) or else
               not Text_Digest(Data,Element(Data,MR,4),Sum(GA))) then return False; end if;
         end;
      end;
      return True;
   end Scoped_History;
   -- Selection consumes only the committed bytes already authenticated by
   -- Establish_History. It does not decide a fresh transition or trust an ACK
   -- flag, external roster, or caller-supplied current-data substitution.
   function Original_Ack_Matches
     (Data, Capture_Data, Ack_Data : E.Bytes;
      Events, Capture, Ack : E.Span) return Boolean is
      Complete : constant E.Span := F (Ack_Data, Ack, "complete");
      Packet : constant E.Span := F (Ack_Data, Complete, "packet");
      Selected : E.Count := 0;
   begin
      for I in E.Count range 1 .. Count (Data, Events) loop
         declare
            Raw : constant E.Bytes :=
              Bytes_Of (Data, Element (Data, Element (Data, Events, I - 1), 2));
            Event : constant E.Span := (1, Raw'Length);
            Request : constant E.Span := JF (Raw, Event, "request");
         begin
            if Match (Raw, Ack_Data, JF (Raw, Event, "proposed"), F (Ack_Data, Packet, "proposed")) and then
               Match (Raw, Ack_Data, JF (Raw, Event, "proposed_rows"), F (Ack_Data, Packet, "rows")) and then
               Match (Raw, Ack_Data, Request, F (Ack_Data, Packet, "request")) then
               if Dictionary_Count (Ack_Data, Packet) /= 4 or else
                  not Text (Ack_Data, F (Ack_Data, Packet, "schema"), "worldline.protected-resource-request-v1") or else
                  not Original_Terminal_Matches (Raw, Capture_Data, Request, Capture) or else
                  not Reply_Matches (Raw, Ack_Data, Event, F (Ack_Data, Complete, "reply"), False) then return False; end if;
               Selected := Selected + 1;
            end if;
         end;
      end loop;
      return Selected = 1;
   end Original_Ack_Matches;
   function Scoped_Ack_Matches
     (Data, Capture_Data, Ack_Data : E.Bytes;
      Events, Replays, Capture, Ack : E.Span) return Boolean is
      Complete : constant E.Span := F (Ack_Data, Ack, "complete");
      Acknowledged_Packet : constant E.Span := F (Ack_Data, Complete, "packet");
      Selected : E.Count := 0;
   begin
      for I in E.Count range 1 .. Count (Data, Events) loop
         declare
            Raw : constant E.Bytes :=
              Bytes_Of (Data, Element (Data, Element (Data, Events, I - 1), 2));
            Event : constant E.Span := (1, Raw'Length);
            Packet : constant E.Span := JF (Raw, Event, "packet");
         begin
            if Match (Raw, Ack_Data, Packet, Acknowledged_Packet) then
               declare
                  Archive : constant E.Bytes :=
                    Bytes_Of (Data, Element (Data, Replays, I - 1));
                  AP : constant E.Span := F (Archive, (1, Archive'Length), "packet");
               begin
                  if not Scoped_Terminal_Matches
                    (Archive, Capture_Data, F (Archive, F (Archive, AP, "request"), "original"), Capture) or else
                     not Reply_Matches (Raw, Ack_Data, Event, F (Ack_Data, Complete, "reply"), True) then return False; end if;
               end;
               Selected := Selected + 1;
            end if;
         end;
      end loop;
      return Selected = 1;
   end Scoped_Ack_Matches;
   procedure Establish_From_Data
     (Data : E.Bytes; Roster : E.Span; State : out History_State;
      History_Roster, Events, Replays : out E.Span)
      with Global => null, Always_Terminates
   is
   begin
      State := Unestablished;
      History_Roster := (1, 0);
      Events := (1, 0);
      Replays := (1, 0);
      declare
         Owner_Context : constant E.Span := F (Data, Roster, "operation_context");
         Profile : constant E.Span := F (Data, Owner_Context, "resource_ack_history");
      begin
         if Text (Data, F (Data, Profile, "family"), "ORIGINAL") then
            if not Original_History (Data, Roster, Owner_Context, Profile) then return; end if;
            Events := F (Data, Profile, "events");
            History_Roster := Roster;
            State := Original_Verified;
         elsif Text (Data, F (Data, Profile, "family"), "SCOPED") then
            if not Scoped_History (Data, Roster, Owner_Context, Profile) then return; end if;
            Events := F (Data, Profile, "events");
            Replays := F (Data, Profile, "replay_archives");
            History_Roster := Roster;
            State := Scoped_Verified;
         end if;
      end;
   end Establish_From_Data;
   procedure Establish_History
     (Context : out Prepared_History; Data : E.Bytes; Roster : E.Span) is
   begin
      -- The observer binds to this exact arena: extent and whole-bytes digest.
      -- Only disjoint scalar metadata is mutable beside the observed source.
      Context.Arena_First := Data'First;
      Context.Arena_Length := Data'Length;
      Context.Arena_Digest := H.C.G.Hash (Data, (Data'First, Data'Length));
      Establish_From_Data
        (Data, Roster, Context.State, Context.Roster, Context.Events, Context.Replays);
   end Establish_History;
   function Bound (Context : Prepared_History; Data : E.Bytes) return Boolean is
     (Context.Arena_First = Data'First and then Context.Arena_Length = Data'Length);
   function Current_Matches (Context : Prepared_History) return Boolean is
     (Context.State /= Unestablished);
   function Source_Matches
     (Context : Prepared_History; Data : E.Bytes; Roster : E.Span)
      return Boolean is
     (Current_Matches (Context) and then
      Context.Roster.First = Roster.First and then
      Context.Roster.Length = Roster.Length and then
      Bound (Context, Data) and then
      Context.Arena_Digest = H.C.G.Hash (Data, (Data'First, Data'Length)));
   function Dispatch
     (Context : Prepared_History; Data, Capture_Data, Ack_Data : E.Bytes;
      Capture, Ack : E.Span) return Boolean is
   begin
      if not Current_Matches (Context) or else
         not OA.Valid (Capture_Data, Capture) or else not OA.Valid (Ack_Data, Ack) or else
         Dictionary_Count (Ack_Data, Ack) /= 3 or else
         not Text (Ack_Data, F (Ack_Data, Ack, "schema"), "worldline.canonical-k4-resource-ack-v1") then return False; end if;
      case Context.State is
         when Original_Verified =>
            return Text (Ack_Data, F (Ack_Data, Ack, "family"), "ORIGINAL") and then
              Original_Ack_Matches (Data, Capture_Data, Ack_Data, Context.Events, Capture, Ack);
         when Scoped_Verified =>
            return Text (Ack_Data, F (Ack_Data, Ack, "family"), "SCOPED") and then
              Scoped_Ack_Matches (Data, Capture_Data, Ack_Data, Context.Events, Context.Replays, Capture, Ack);
         when Unestablished => return False;
      end case;
   end Dispatch;
   function Current_Authenticated (Value : L.Parsed_Input) return Boolean is
   begin
      if not OC.Owner_Corresponds (Value) then return False; end if;
      declare Context : Prepared_History; begin
         Establish_History (Context, Value.Arena, Value.Owner_Roster);
         return Current_Matches (Context);
      end;
   end Current_Authenticated;
   function Direct_Authenticated
     (Context : Prepared_History; Data, Input_Data : E.Bytes;
      Capture, Acknowledgement : E.Span) return Boolean is
   begin
      if not Current_Matches (Context) or else not Bound (Context, Data) then return False; end if;
      return Dispatch (Context, Data, Input_Data, Input_Data, Capture, Acknowledgement);
   end Direct_Authenticated;
   function Direct_Authenticated
     (Value : L.Parsed_Input; Input_Data : E.Bytes;
      Capture, Acknowledgement : E.Span) return Boolean is
   begin
      if not OC.Owner_Corresponds (Value) then return False; end if;
      declare Context : Prepared_History; begin
         Establish_History (Context, Value.Arena, Value.Owner_Roster);
         return Direct_Authenticated (Context, Value.Arena, Input_Data, Capture, Acknowledgement);
      end;
   end Direct_Authenticated;
   function Authenticated_From_Data
     (Context : Prepared_History; Data : E.Bytes;
      Event, Prior_Event : E.Span) return Boolean
      with Global => null
   is
   begin
      if not Current_Matches (Context) then return False; end if;
      declare
      Snapshot_Item : constant E.Span := F (Data, Event, "snapshot");
      Capture_Item : constant E.Span := F (Data, Event, "capture");
      Prior_Boundaries : constant E.Span := F (Data, Prior_Event, "boundaries");
      Boundaries : constant E.Span := F (Data, Event, "boundaries");
      Ack_Item : E.Span := (1, 0);
      Ack_Count, Intent_Count : E.Count := 0;
   begin
      if not V.Valid_Hex_Field (Data, Snapshot_Item, "value") or else
         not V.Valid_Hex_Field (Data, Capture_Item, "value") or else
         not S.Valid (Data, Event) or else not S.Valid (Data, Prior_Event) or else
         not OA.Same_Encoding (Data, Capture_Item, F (Data, Prior_Event, "capture")) or else
         not OA.Same_Encoding (Data, F (Data, Event, "operation"), F (Data, Prior_Event, "operation")) then return False; end if;
      declare Snapshot : constant E.Bytes := V.Hex_Value (Data, Snapshot_Item, "value");
              Capture : constant E.Bytes := V.Hex_Value (Data, Capture_Item, "value");
              Proof : constant E.Span := F (Snapshot, (1,Snapshot'Length), "owner_completion"); begin
         if not OA.Valid (Snapshot, (1,Snapshot'Length)) or else not OA.Valid (Snapshot, Proof) then return False; end if;
         for I in E.Count range 1 .. Count (Data, Prior_Boundaries) loop
            declare Boundary : constant E.Span := Element (Data, Prior_Boundaries, I-1);
                    Word : constant E.Span := F (Data, Boundary, "value"); begin
               if Text (Data, F (Data, Boundary, "name"), "FULL_BROKER_OWNER_DISPOSITION") then
                  if not V.Valid_Hex_Field (Data, Word, "value") then return False; end if;
                  declare Original : constant E.Bytes := V.Hex_Value (Data, Word, "value"); begin
                     if not Raw_Same (Snapshot, Original, Proof, (1,Original'Length)) then return False; end if;
                  end;
                  Intent_Count := Intent_Count + 1;
               end if;
            end;
         end loop;
         if Intent_Count = 0 then return False; end if;
         for I in E.Count range 1 .. Count (Data, Boundaries) loop
            declare Boundary : constant E.Span := Element (Data, Boundaries, I-1); begin
               if Text (Data, F (Data, Boundary, "name"), "FULL_BROKER_K4_RESOURCE_ACK") then
                  Ack_Item := F (Data, Boundary, "value"); Ack_Count := Ack_Count + 1;
               end if;
            end;
         end loop;
         if Ack_Count /= 1 or else not V.Valid_Hex_Field (Data, Ack_Item, "value") then return False; end if;
         declare Ack : constant E.Bytes := V.Hex_Value (Data, Ack_Item, "value"); begin
            return Dispatch (Context, Data, Capture, Ack, (1,Capture'Length), (1,Ack'Length));
         end;
      end;
      end;
   end Authenticated_From_Data;
   function Authenticated
     (Context : Prepared_History; Data : E.Bytes; Event, Prior_Event : E.Span)
      return Boolean is
   begin
      if not Bound (Context, Data) then return False; end if;
      return Authenticated_From_Data (Context, Data, Event, Prior_Event);
   end Authenticated;
   function Authenticated
     (Value : L.Parsed_Input; Event, Prior_Event : E.Span) return Boolean is
   begin
      if not OC.Owner_Corresponds (Value) then return False; end if;
      declare Context : Prepared_History; begin
         Establish_History (Context, Value.Arena, Value.Owner_Roster);
         return Authenticated (Context, Value.Arena, Event, Prior_Event);
      end;
   end Authenticated;
end Worldline.Custody_V2_K4_Resource_Ack;
