with Worldline.Archive_Envelope;
with Worldline.Operation_Archive;
procedure Archive_Envelope_Controls is
   package E renames Worldline.Archive_Envelope;
   use type E.Value_Kind;
   use type E.Bytes;
   use type E.Count;
   function Raw (S : String) return E.Bytes is
      R : E.Bytes (1 .. E.Count (S'Length));
   begin
      for I in S'Range loop R (E.Count (I - S'First) + 1) := Character'Pos (S (I)); end loop;
      return R;
   end Raw;
   function Nibble (C : Character) return E.Q.Byte is
     (if C in '0' .. '9' then Character'Pos (C) - Character'Pos ('0')
      else Character'Pos (C) - Character'Pos ('a') + 10);
   function Hex (S : String) return E.Bytes is
      R : E.Bytes (1 .. E.Count (S'Length / 2));
      use type E.Q.Byte;
   begin
      for I in R'Range loop R (I) := Nibble (S (S'First + Integer (I - 1) * 2)) * 16
        + Nibble (S (S'First + Integer (I - 1) * 2 + 1)); end loop;
      return R;
   end Hex;
begin
   -- null
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Null_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
   end;
   -- true
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Boolean_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
      pragma Assert (Item.Boolean = True);
   end;
   -- false
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Boolean_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
      pragma Assert (Item.Boolean = False);
   end;
   -- zero
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""aW50ZWdlci1tYWduaXR1ZGU=""]]],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]],[""array"",[[""str"",""Ynl0ZXM=""],[""str"",""""]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Integer_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
      pragma Assert (E.Materialize (Data, Item.Payload) = Hex (""));
      pragma Assert (Item.Sign = False);
   end;
   -- negative
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""aW50ZWdlci1tYWduaXR1ZGU=""]]],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]],[""array"",[[""str"",""Ynl0ZXM=""],[""str"",""QVE9PQ==""]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Integer_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
      pragma Assert (E.Materialize (Data, Item.Payload) = Hex ("01"));
      pragma Assert (Item.Sign = True);
   end;
   -- positive
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""aW50ZWdlci1tYWduaXR1ZGU=""]]],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]],[""array"",[[""str"",""Ynl0ZXM=""],[""str"",""QVE9PQ==""]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Integer_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
      pragma Assert (E.Materialize (Data, Item.Payload) = Hex ("01"));
      pragma Assert (Item.Sign = False);
   end;
   -- negative_zero
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""float"",""gAAAAAAAAAA=""]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Float_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
      pragma Assert (E.Materialize (Data, Item.Payload) = Hex ("8000000000000000"));
   end;
   -- fraction
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""float"",""P/gAAAAAAAA=""]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Float_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
      pragma Assert (E.Materialize (Data, Item.Payload) = Hex ("3ff8000000000000"));
   end;
   -- empty_text
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""""]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Text_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
      pragma Assert (E.Materialize (Data, Item.Payload) = Hex (""));
   end;
   -- nul_text
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""YQBi""]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Text_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
      pragma Assert (E.Materialize (Data, Item.Payload) = Hex ("610062"));
   end;
   -- surrogate
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""7aCA""]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Text_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
      pragma Assert (E.Materialize (Data, Item.Payload) = Hex ("eda080"));
   end;
   -- nonbmp
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""8J+YgA==""]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Text_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
      pragma Assert (E.Materialize (Data, Item.Payload) = Hex ("f09f9880"));
   end;
   -- empty_bytes
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""Ynl0ZXM=""],[""str"",""""]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Bytes_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
      pragma Assert (E.Materialize (Data, Item.Payload) = Hex (""));
   end;
   -- raw_bytes
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""Ynl0ZXM=""],[""str"",""QVA4PQ==""]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Bytes_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
      pragma Assert (E.Materialize (Data, Item.Payload) = Hex ("00ff"));
   end;
   -- empty_list
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""bGlzdA==""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.List_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
   end;
   -- empty_tuple
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""dHVwbGU=""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Tuple_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
   end;
   -- list
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""bGlzdA==""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""Ynl0ZXM=""],[""str"",""QUE9PQ==""]]]]]]]]]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.List_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
   end;
   -- tuple
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""dHVwbGU=""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""dGV4dA==""]]]]]]]]]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Tuple_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
   end;
   -- object
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""b2JqZWN0""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""aw==""]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""Ynl0ZXM=""],[""str"",""YXc9PQ==""]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]]]]]]]]]]]]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Object_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
   end;
   -- record
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""cmVjb3Jk""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""d29ybGRsaW5lLnJlc291cmNlX3J1bl9sZWRnZXI=""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""UnVuQ29udGV4dA==""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""dW5pdmVyc2U=""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""cG9saWN5""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""cmVzb3VyY2U=""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""dW5pdA==""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""aW5zdGFuY2U=""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""aG9zdA==""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""Ym9vdA==""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXV0aG9yaXR5""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""cG9saWN5X2Vwb2No""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]]]]]]]]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.Record_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
   end;
   -- world_state
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""d29ybGQtc3RhdGU=""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""TVVUQUJMRQ==""]]]]]]]");
      Item : constant E.View := E.Decode (Data, (Data'First, Data'Length), E.Operation);
   begin
      pragma Assert (Item.Form = E.World_State_Value);
      pragma Assert (Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
   end;
   -- original refusal unknown_tag
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""dW5rbm93bg==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]]");
   begin
      pragma Assert (not Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
   end;
   -- original refusal negative_zero
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""aW50ZWdlci1tYWduaXR1ZGU=""]]],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]],[""array"",[[""str"",""Ynl0ZXM=""],[""str"",""""]]]]]]]");
   begin
      pragma Assert (not Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
   end;
   -- original refusal nonminimal
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""aW50ZWdlci1tYWduaXR1ZGU=""]]],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]],[""array"",[[""str"",""Ynl0ZXM=""],[""str"",""QVFBPQ==""]]]]]]]");
   begin
      pragma Assert (not Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
   end;
   -- original refusal atom_integer
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""int"",false,""AQ==""]]]]]]]");
   begin
      pragma Assert (not Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
   end;
   -- original refusal unknown_state
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""d29ybGQtc3RhdGU=""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""bm90LWEtc3RhdGU=""]]]]]]]");
   begin
      pragma Assert (not Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
   end;
   -- original refusal duplicate_keys
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""b2JqZWN0""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""aw==""]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""aw==""]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]]]]]]]]]]]]]]]]]]");
   begin
      pragma Assert (not Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
   end;
   -- original refusal integer_key
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""b2JqZWN0""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""aW50ZWdlci1tYWduaXR1ZGU=""]]],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]],[""array"",[[""str"",""Ynl0ZXM=""],[""str"",""QVE9PQ==""]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]]]]]]]]]]]]]]");
   begin
      pragma Assert (not Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
   end;
   -- original refusal missing_record_fields
   declare
      Data : constant E.Bytes := Raw ("[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""cmVjb3Jk""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""d29ybGRsaW5lLnJlc291cmNlX3J1bl9sZWRnZXI=""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""UnVuQ29udGV4dA==""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]]]]");
   begin
      pragma Assert (not Worldline.Operation_Archive.Valid (Data, (Data'First, Data'Length)));
   end;
end Archive_Envelope_Controls;
