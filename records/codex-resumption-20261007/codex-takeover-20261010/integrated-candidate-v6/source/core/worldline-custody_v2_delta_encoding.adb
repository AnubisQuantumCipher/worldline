package body Worldline.Custody_V2_Delta_Encoding with SPARK_Mode is
   use type Q.Byte;
   use type SQL.SQL_Class;
   Hex : constant String := "0123456789abcdef";
   Alphabet : constant String :=
     "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
   -- These fixed fragments expand the original three codec layers, not a
   -- replacement archive grammar. Dynamic UTF8 is terminal base64, never JSON
   -- escaping. A node's encoded subtree is identical at the root or in a pair.
   List_Open : constant String := "[""array"",[[""str"",""bGlzdA==""],[""array"",[";
   List_Close : constant String := "]]]]";
   Object_Open : constant String := "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""b2JqZWN0""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[";
   Object_Close : constant String := "]]]]]]]]";
   Dictionary_Open : constant String := "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""b2JqZWN0""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""dHlwZQ==""]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""ZGljdA==""]]]]]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""ZmllbGRz""]]]]]]],";
   Dictionary_Close : constant String := "]]]]]]]]]]]]";
   Text_Open : constant String := "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""";
   Text_Close : constant String := """]]]]]]]";
   Null_Atom : constant String := "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]]]]";

   function Valid (Data : E.Bytes; Item : E.Span) return Boolean is
     (E.C.P.Valid (Data, Item));

   -- Reserve operates on the actual host extent, not the integer value or an
   -- archive nesting/count limit. Once invalid, emission remains invalid.
   procedure Reserve (State : in out Length_Result; N : E.Count;
                      Start : out E.Count)
   with Global => null,
     Post => Start = State'Old.Needed and then
       (if State'Old.Valid and then N <= E.Count'Last - State'Old.Needed then
          State.Valid and then State.Needed = State'Old.Needed + N
        else not State.Valid and then State.Needed = State'Old.Needed)
   is
   begin
      Start := State.Needed;
      if not State.Valid or else N > E.Count'Last - State.Needed then
         State.Valid := False;
      else
         State.Needed := State.Needed + N;
      end if;
   end Reserve;

   procedure Put (Output : in out E.Bytes; State : in out Length_Result;
                  Text : String) with Global => null is
      Start : E.Count;
      N : constant E.Count := Text'Length;
   begin
      Reserve (State, N, Start);
      if State.Valid and then Start < Output'Length and then N > 0 then
         for I in E.Count range 0 .. E.Count'Min (N, Output'Length - Start) - 1 loop
            pragma Loop_Invariant (Start < Output'Length);
            Output (Output'First + Start + I) :=
              Character'Pos (Text (Text'First + Natural (I)));
         end loop;
      end if;
   end Put;

   procedure Raw (Data : E.Bytes; Item : E.Span;
                  Output : in out E.Bytes; State : in out Length_Result)
   with Global => null is
      Start : E.Count;
   begin
      if not Valid (Data, Item) then State.Valid := False; return; end if;
      Reserve (State, Item.Length, Start);
      if State.Valid and then Start < Output'Length and then Item.Length > 0 then
         for I in E.Count range 0 ..
           E.Count'Min (Item.Length, Output'Length - Start) - 1 loop
            pragma Loop_Invariant (Valid (Data, Item));
            Output (Output'First + Start + I) := Data (Item.First + I);
         end loop;
      end if;
   end Raw;

   function Hex_Byte (Data : E.Bytes; Item : E.Span; Offset : E.Count)
      return Q.Byte
   with Global => null, Pre => Valid (Data, Item) and then
     Offset / 2 < Item.Length
   is
      B : constant Q.Byte := Data (Item.First + Offset / 2);
   begin
      return Character'Pos (Hex
        (Natural (if Offset mod 2 = 0 then B / 16 else B mod 16) + 1));
   end Hex_Byte;

   procedure Put_Hex (Data : E.Bytes; Item : E.Span;
                      Output : in out E.Bytes; State : in out Length_Result)
   with Global => null is
      Start, N : E.Count;
   begin
      if not Valid (Data, Item) or else Item.Length > E.Count'Last / 2 then
         State.Valid := False; return;
      end if;
      N := Item.Length * 2;
      Reserve (State, N, Start);
      if State.Valid and then Start < Output'Length and then N > 0 then
         for I in E.Count range 0 .. E.Count'Min (N, Output'Length - Start) - 1 loop
            pragma Loop_Invariant (Valid (Data, Item));
            Output (Output'First + Start + I) := Hex_Byte (Data, Item, I);
         end loop;
      end if;
   end Put_Hex;

   -- Virtual hex characters feed terminal base64 directly. Neither text bytes
   -- nor byte-value hexadecimal text require a temporary array or a copy.
   procedure Put_Base64 (Data : E.Bytes; Item : E.Span; Hexed : Boolean;
                         Output : in out E.Bytes; State : in out Length_Result)
   with Global => null is
      N, Encoded, Start : E.Count;
      function Byte_At
        (Source : E.Bytes; Part : E.Span; As_Hex : Boolean; Offset : E.Count)
         return Natural
      is
        (Natural (if As_Hex then Hex_Byte (Source, Part, Offset)
                  else Source (Part.First + Offset)))
      with Global => null,
        Pre => Valid (Source, Part) and then
          (if As_Hex then Offset / 2 < Part.Length else Offset < Part.Length),
        Post => Byte_At'Result <= 255;
   begin
      if not Valid (Data, Item) or else
        (Hexed and then Item.Length > E.Count'Last / 2) then
         State.Valid := False; return;
      end if;
      N := (if Hexed then Item.Length * 2 else Item.Length);
      if N / 3 > E.Count'Last / 4 then State.Valid := False; return; end if;
      Encoded := (N / 3) * 4;
      if N mod 3 /= 0 then
         if Encoded > E.Count'Last - 4 then State.Valid := False; return; end if;
         Encoded := Encoded + 4;
      end if;
      Reserve (State, Encoded, Start);
      if State.Valid and then Start < Output'Length and then Encoded > 0 then
         for I in E.Count range 0 ..
           E.Count'Min (Encoded, Output'Length - Start) - 1 loop
            pragma Loop_Invariant (Valid (Data, Item));
            pragma Loop_Invariant
              (if Hexed then N = Item.Length * 2 else N = Item.Length);
            declare
               P : constant E.Count := (I / 4) * 3;
               Digit : Natural range 0 .. 63 := 0;
               Padding : Boolean := False;
            begin
               case I mod 4 is
                  when 0 => Digit := Byte_At (Data, Item, Hexed, P) / 4;
                  when 1 =>
                     Digit := (Byte_At (Data, Item, Hexed, P) mod 4) * 16;
                     if N - P > 1 then
                        Digit := Digit + Byte_At (Data, Item, Hexed, P + 1) / 16;
                     end if;
                  when 2 =>
                     if N - P > 1 then
                        Digit := (Byte_At (Data, Item, Hexed, P + 1) mod 16) * 4;
                        if N - P > 2 then
                           Digit := Digit + Byte_At (Data, Item, Hexed, P + 2) / 64;
                        end if;
                     else Padding := True; end if;
                  when others =>
                     if N - P > 2 then Digit := Byte_At (Data, Item, Hexed, P + 2) mod 64;
                     else Padding := True; end if;
               end case;
               Output (Output'First + Start + I) := Character'Pos
                 (if Padding then '=' else Alphabet (Digit + 1));
            end;
         end loop;
      end if;
   end Put_Base64;

   procedure Atom_Text (Data : E.Bytes; Item : E.Span; Hexed : Boolean;
                        Output : in out E.Bytes; State : in out Length_Result)
   with Global => null is
   begin
      Put (Output, State, Text_Open);
      Put_Base64 (Data, Item, Hexed, Output, State);
      Put (Output, State, Text_Close);
   end Atom_Text;

   procedure Pair_Open (Data : E.Bytes; Name : E.Span;
                        Output : in out E.Bytes; State : in out Length_Result)
   with Global => null is
   begin
      Put (Output, State, List_Open);
      Atom_Text (Data, Name, False, Output, State);
      Put (Output, State, ",");
   end Pair_Open;

   procedure Literal_Pair_Open (Name : String; Output : in out E.Bytes;
                                State : in out Length_Result)
   with Global => null is
   begin
      Put (Output, State, List_Open);
      if Name = "type" then
         Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""dHlwZQ==""]]]]]]]");
      elsif Name = "value" then
         Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""dmFsdWU=""]]]]]]]");
      elsif Name = "previous" then
         Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""cHJldmlvdXM=""]]]]]]]");
      elsif Name = "generation" then
         Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Z2VuZXJhdGlvbg==""]]]]]]]");
      elsif Name = "operation" then
         Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""b3BlcmF0aW9u""]]]]]]]");
      elsif Name = "subject_kind" then
         Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""c3ViamVjdF9raW5k""]]]]]]]");
      elsif Name = "subject" then
         Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""c3ViamVjdA==""]]]]]]]");
      elsif Name = "subgeneration" then
         Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""c3ViZ2VuZXJhdGlvbg==""]]]]]]]");
      elsif Name = "kind" then
         Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""a2luZA==""]]]]]]]");
      elsif Name = "actor" then
         Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""YWN0b3I=""]]]]]]]");
      elsif Name = "record" then
         Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""cmVjb3Jk""]]]]]]]");
      elsif Name = "head_kind" then
         Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""aGVhZF9raW5k""]]]]]]]");
      elsif Name = "head" then
         Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""aGVhZA==""]]]]]]]");
      elsif Name = "genesis" then
         Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Z2VuZXNpcw==""]]]]]]]");
      else State.Valid := False;
      end if;
      Put (Output, State, ",");
   end Literal_Pair_Open;

   procedure Emit_Node (Data : E.Bytes; Value : Node;
                        Output : in out E.Bytes; State : in out Length_Result)
   with Global => null is
   begin
      if Value.Kind = Copy_Archive then
         Raw (Data, Value.Payload, Output, State);
         return;
      end if;
      Put (Output, State, Object_Open);
      Literal_Pair_Open ("type", Output, State);
      case Value.Kind is
         when Text_Node => Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""c3Ry""]]]]]]]");
         when Bytes_Node => Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Ynl0ZXM=""]]]]]]]");
         when Null_Node => Put (Output, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Tm9uZVR5cGU=""]]]]]]]");
         when Copy_Archive => null;
      end case;
      Put (Output, State, List_Close & ",");
      Literal_Pair_Open ("value", Output, State);
      if Value.Kind = Null_Node then Put (Output, State, Null_Atom);
      else Atom_Text (Data, Value.Payload, Value.Kind = Bytes_Node, Output, State);
      end if;
      Put (Output, State, List_Close & Object_Close);
   end Emit_Node;

   procedure Finish (State : in out Length_Result; Capacity : E.Count;
                     Complete : out Boolean) with Global => null is
   begin
      if not State.Valid then State.Needed := 0; end if;
      Complete := State.Valid and then State.Needed <= Capacity;
   end Finish;

   procedure Render_Dictionary
     (Data : E.Bytes; Fields : Members; Output : out E.Bytes;
      Length : out Length_Result; Complete : out Boolean)
   is
   begin
      Output := (others => 0);
      Length := (True, 0);
      Put (Output, Length, Dictionary_Open & Object_Open);
      for I in Fields'Range loop
         if I /= Fields'First then Put (Output, Length, ","); end if;
         Pair_Open (Data, Fields (I).Name, Output, Length);
         Emit_Node (Data, Fields (I).Value, Output, Length);
         Put (Output, Length, List_Close);
      end loop;
      Put (Output, Length, Object_Close & Dictionary_Close);
      Finish (Length, Output'Length, Complete);
   end Render_Dictionary;

   function Dictionary_Length (Data : E.Bytes; Fields : Members)
      return Length_Result
   is
      Empty : E.Bytes (1 .. 0);
      Result : Length_Result;
      Complete : Boolean;
   begin
      Render_Dictionary (Data, Fields, Empty, Result, Complete);
      return Result;
   end Dictionary_Length;

   procedure Base_Field (Name : String; Data : E.Bytes; Value : Node;
                         Output : in out E.Bytes; State : in out Length_Result)
   with Global => null is
   begin
      Literal_Pair_Open (Name, Output, State);
      Emit_Node (Data, Value, Output, State);
      Put (Output, State, List_Close);
   end Base_Field;

   procedure Render_Base
     (Data : E.Bytes; Row : C.Event_Row; Output : out E.Bytes;
      Length : out Length_Result; Complete : out Boolean)
   is
   begin
      Output := (others => 0);
      Length := (True, 0);
      Put (Output, Length, Dictionary_Open & Object_Open);
      Base_Field ("previous", Data, (Text_Node, Row.Previous), Output, Length);
      Put (Output, Length, ",");
      Base_Field ("generation", Data, (Bytes_Node, Row.Generation), Output, Length);
      Put (Output, Length, ",");
      Base_Field ("operation", Data, (Text_Node, Row.Operation), Output, Length);
      Put (Output, Length, ",");
      Base_Field ("subject_kind", Data, (Text_Node, Row.Subject_Kind), Output, Length);
      Put (Output, Length, ",");
      Base_Field ("subject", Data, (Text_Node, Row.Subject), Output, Length);
      Put (Output, Length, ",");
      Base_Field ("subgeneration", Data, (Bytes_Node, Row.Subgeneration), Output, Length);
      Put (Output, Length, ",");
      Base_Field ("kind", Data, (Text_Node, Row.Kind), Output, Length);
      Put (Output, Length, ",");
      Base_Field ("actor", Data, (Text_Node, Row.Actor), Output, Length);
      Put (Output, Length, ",");
      Base_Field ("record", Data, (Copy_Archive, Row.Record_Archive), Output, Length);
      Put (Output, Length, Object_Close & Dictionary_Close);
      Finish (Length, Output'Length, Complete);
   end Render_Base;

   function Base_Length (Data : E.Bytes; Row : C.Event_Row)
      return Length_Result
   is
      Empty : E.Bytes (1 .. 0);
      Result : Length_Result;
      Complete : Boolean;
   begin
      Render_Base (Data, Row, Empty, Result, Complete);
      return Result;
   end Base_Length;

   procedure Render_Event_Head
     (Data : E.Bytes; Event_Id, Genesis_Row : E.Span; Output : out E.Bytes;
      Length : out Length_Result; Complete : out Boolean)
   is
      Event_Name : constant E.Bytes :=
        (Character'Pos ('E'), Character'Pos ('V'), Character'Pos ('E'),
         Character'Pos ('N'), Character'Pos ('T'));
   begin
      Output := (others => 0);
      Length := (True, 0);
      Put (Output, Length, Dictionary_Open & Object_Open);
      Base_Field ("head_kind", Event_Name, (Text_Node, (1, 5)), Output, Length);
      Put (Output, Length, ",");
      Base_Field ("head", Data, (Text_Node, Event_Id), Output, Length);
      Put (Output, Length, ",");
      Base_Field ("genesis", Data, (Copy_Archive, Genesis_Row), Output, Length);
      Put (Output, Length, Object_Close & Dictionary_Close);
      Finish (Length, Output'Length, Complete);
   end Render_Event_Head;

   function Head_Length (Data : E.Bytes; Event_Id, Genesis_Row : E.Span)
      return Length_Result
   is
      Empty : E.Bytes (1 .. 0);
      Result : Length_Result;
      Complete : Boolean;
   begin
      Render_Event_Head (Data, Event_Id, Genesis_Row, Empty, Result, Complete);
      return Result;
   end Head_Length;

   procedure Cell (Data : E.Bytes; Value : Raw_Cell;
                   Output : in out E.Bytes; State : in out Length_Result)
   with Global => null is
      Code : String (1 .. 1);
   begin
      Code (1) := Character'Val (Character'Pos ('0') + SQL.SQL_Class'Pos (Value.Kind));
      Put (Output, State, "[" & Code & ",");
      if Value.Kind = SQL.SQL_Integer and then Value.Negative then
         Put (Output, State, "true");
      else Put (Output, State, "false"); end if;
      Put (Output, State, ",""");
      if Value.Kind /= SQL.SQL_Null then Put_Hex (Data, Value.Payload, Output, State); end if;
      Put (Output, State, """" & "]");
   end Cell;

   procedure Row (Data : E.Bytes; Values : Cells;
                  Output : in out E.Bytes; State : in out Length_Result)
   with Global => null is
   begin
      Put (Output, State, "[");
      for I in Values'Range loop
         if I /= Values'First then Put (Output, State, ","); end if;
         Cell (Data, Values (I), Output, State);
      end loop;
      Put (Output, State, "]");
   end Row;

   procedure Table (Data : E.Bytes; Values : Cells; Width : Positive;
                    Output : in out E.Bytes; State : in out Length_Result)
   with Global => null is
      W : constant E.Count := E.Count (Width);
      Offset : E.Count := 0;
   begin
      if Values'Length mod W /= 0 then State.Valid := False; return; end if;
      Put (Output, State, "[");
      while Offset < Values'Length loop
         pragma Loop_Invariant (Offset <= Values'Length and then Offset mod W = 0);
         pragma Loop_Variant (Decreases => Values'Length - Offset);
         if Offset > 0 then Put (Output, State, ","); end if;
         Put (Output, State, "[");
         for J in E.Count range 0 .. W - 1 loop
            if J > 0 then Put (Output, State, ","); end if;
            Cell (Data, Values (Values'First + Offset + J), Output, State);
         end loop;
         Put (Output, State, "]");
         Offset := Offset + W;
      end loop;
      Put (Output, State, "]");
   end Table;

   procedure Render_Delta
     (Data : E.Bytes; Event : Event_Columns; Roots, Subjects, Alternatives,
      Blobs : Cells; Head : Head_Columns; Head_Message : E.Span;
      Output : out E.Bytes; Length : out Length_Result; Complete : out Boolean)
   is
   begin
      Output := (others => 0);
      Length := (True, 0);
      -- Original canonical JSON lexically sorts keys. SQL row order is never
      -- sorted or projected; nullable values retain their original cell class.
      Put (Output, Length, "{""alternatives"":");
      Table (Data, Alternatives, 7, Output, Length);
      Put (Output, Length, ",""blobs"":");
      Table (Data, Blobs, 3, Output, Length);
      Put (Output, Length, ",""event"":");
      Row (Data, Event, Output, Length);
      Put (Output, Length, ",""head"":");
      Row (Data, Head, Output, Length);
      Put (Output, Length, ",""head_message"":""");
      Put_Hex (Data, Head_Message, Output, Length);
      Put (Output, Length, """,""roots"":");
      Table (Data, Roots, 16, Output, Length);
      Put (Output, Length, ",""schema"":""worldline.custody-native-delta-v2"",""subjects"":");
      Table (Data, Subjects, 9, Output, Length);
      Put (Output, Length, "}");
      Finish (Length, Output'Length, Complete);
   end Render_Delta;

   function Delta_Length
     (Data : E.Bytes; Event : Event_Columns; Roots, Subjects, Alternatives,
      Blobs : Cells; Head : Head_Columns; Head_Message : E.Span)
      return Length_Result
   is
      Empty : E.Bytes (1 .. 0);
      Result : Length_Result;
      Complete : Boolean;
   begin
      Render_Delta (Data, Event, Roots, Subjects, Alternatives, Blobs,
                    Head, Head_Message, Empty, Result, Complete);
      return Result;
   end Delta_Length;
   procedure Encode_Dictionary
     (Data : E.Bytes; Fields : Members; Output : out E.Bytes;
      Length : out Length_Result; Complete : out Boolean) is
   begin
      Render_Dictionary (Data, Fields, Output, Length, Complete);
   end Encode_Dictionary;

   procedure Encode_Base
     (Data : E.Bytes; Row : C.Event_Row; Output : out E.Bytes;
      Length : out Length_Result; Complete : out Boolean) is
   begin
      Render_Base (Data, Row, Output, Length, Complete);
   end Encode_Base;

   procedure Encode_Event_Head
     (Data : E.Bytes; Event_Id, Genesis_Row : E.Span; Output : out E.Bytes;
      Length : out Length_Result; Complete : out Boolean) is
   begin
      Render_Event_Head (Data, Event_Id, Genesis_Row, Output, Length, Complete);
   end Encode_Event_Head;

   procedure Encode_Delta
     (Data : E.Bytes; Event : Event_Columns; Roots, Subjects, Alternatives,
      Blobs : Cells; Head : Head_Columns; Head_Message : E.Span;
      Output : out E.Bytes; Length : out Length_Result; Complete : out Boolean) is
   begin
      Render_Delta (Data, Event, Roots, Subjects, Alternatives, Blobs,
                    Head, Head_Message, Output, Length, Complete);
   end Encode_Delta;
   function Event_Digests (Data : E.Bytes; Key, Base_Archive : E.Span)
      return Event_Digest_Result
   is
   begin
      if not Valid (Data, Key) or else not Valid (Data, Base_Archive) then
         return (Present => False);
      end if;
      return (Present => True, Event_Id => C.G.Hash (Data, Base_Archive),
              Mac => C.G.Mac (Data, Key, Base_Archive));
   end Event_Digests;

   function In_Prefix (Arena : E.Bytes; Item : E.Span; Used : E.Count)
      return Boolean is
     (Used <= Arena'Length and then Valid (Arena, Item) and then
      (Item.Length = 0 or else
       (Item.First - Arena'First < Used and then
        Item.Length <= Used - (Item.First - Arena'First))))
     with Global => null;

   function Base_In_Prefix
     (Arena : E.Bytes; Row : C.Event_Row; Used : E.Count) return Boolean is
     (In_Prefix (Arena, Row.Previous, Used) and then
      In_Prefix (Arena, Row.Generation, Used) and then
      In_Prefix (Arena, Row.Operation, Used) and then
      In_Prefix (Arena, Row.Subject_Kind, Used) and then
      In_Prefix (Arena, Row.Subject, Used) and then
      In_Prefix (Arena, Row.Subgeneration, Used) and then
      In_Prefix (Arena, Row.Kind, Used) and then
      In_Prefix (Arena, Row.Actor, Used) and then
      In_Prefix (Arena, Row.Record_Archive, Used));

   function Head_In_Prefix
     (Arena : E.Bytes; Event_Id, Genesis_Row : E.Span; Used : E.Count)
      return Boolean is
     (In_Prefix (Arena, Event_Id, Used) and then
      In_Prefix (Arena, Genesis_Row, Used));

   -- Direct single-object copying. Every source byte is in the prefix that
   -- precedes Start; each destination is in the disjoint newly reserved suffix.
   procedure Append_Raw
     (Arena : in out E.Bytes; Item : E.Span; State : in out Length_Result)
   with Global => null,
     Pre => State.Valid and then In_Prefix (Arena, Item, State.Needed) and then
       Item.Length <= Arena'Length - State.Needed,
     Post => State.Valid and then State.Needed = State'Old.Needed + Item.Length
   is
      Start : E.Count;
   begin
      Reserve (State, Item.Length, Start);
      if Item.Length > 0 then
         for I in E.Count range 0 .. Item.Length - 1 loop
            pragma Loop_Invariant (State.Valid);
            pragma Loop_Invariant (State.Needed = Start + Item.Length);
            pragma Loop_Invariant (In_Prefix (Arena, Item, Start));
            Arena (Arena'First + Start + I) := Arena (Item.First + I);
         end loop;
      end if;
   end Append_Raw;

   procedure Append_Base64
     (Arena : in out E.Bytes; Item : E.Span; Hexed : Boolean;
      State : in out Length_Result)
   with Global => null is
      N, Encoded, Start : E.Count;
      function Byte_At
        (Source : E.Bytes; Part : E.Span; As_Hex : Boolean; Offset : E.Count)
         return Natural
      is
        (Natural (if As_Hex then Hex_Byte (Source, Part, Offset)
                  else Source (Part.First + Offset)))
      with Global => null,
        Pre => Valid (Source, Part) and then
          (if As_Hex then Offset / 2 < Part.Length else Offset < Part.Length),
        Post => Byte_At'Result <= 255;
   begin
      if not State.Valid or else not In_Prefix (Arena, Item, State.Needed) or else
        (Hexed and then Item.Length > E.Count'Last / 2) then
         State.Valid := False; return;
      end if;
      N := (if Hexed then Item.Length * 2 else Item.Length);
      if N / 3 > E.Count'Last / 4 then State.Valid := False; return; end if;
      Encoded := (N / 3) * 4;
      if N mod 3 /= 0 then
         if Encoded > E.Count'Last - 4 then State.Valid := False; return; end if;
         Encoded := Encoded + 4;
      end if;
      if Encoded > Arena'Length - State.Needed then State.Valid := False; return; end if;
      Reserve (State, Encoded, Start);
      if Encoded > 0 then
         for I in E.Count range 0 .. Encoded - 1 loop
            pragma Loop_Invariant (State.Valid);
            pragma Loop_Invariant (In_Prefix (Arena, Item, Start));
            pragma Loop_Invariant (State.Needed = Start + Encoded);
            pragma Loop_Invariant
              (if Hexed then N = Item.Length * 2 else N = Item.Length);
            declare
               P : constant E.Count := (I / 4) * 3;
               Digit : Natural range 0 .. 63 := 0;
               Padding : Boolean := False;
            begin
               case I mod 4 is
                  when 0 => Digit := Byte_At (Arena, Item, Hexed, P) / 4;
                  when 1 =>
                     Digit := (Byte_At (Arena, Item, Hexed, P) mod 4) * 16;
                     if N - P > 1 then
                        Digit := Digit + Byte_At (Arena, Item, Hexed, P + 1) / 16;
                     end if;
                  when 2 =>
                     if N - P > 1 then
                        Digit := (Byte_At (Arena, Item, Hexed, P + 1) mod 16) * 4;
                        if N - P > 2 then
                           Digit := Digit + Byte_At (Arena, Item, Hexed, P + 2) / 64;
                        end if;
                     else Padding := True; end if;
                  when others =>
                     if N - P > 2 then Digit := Byte_At (Arena, Item, Hexed, P + 2) mod 64;
                     else Padding := True; end if;
               end case;
               Arena (Arena'First + Start + I) := Character'Pos
                 (if Padding then '=' else Alphabet (Digit + 1));
            end;
         end loop;
      end if;
   end Append_Base64;

   procedure Append_Node
     (Arena : in out E.Bytes; Value : Node; State : in out Length_Result)
   with Global => null is
   begin
      if Value.Kind = Copy_Archive then
         Append_Raw (Arena, Value.Payload, State);
         return;
      end if;
      Put (Arena, State, Object_Open);
      Literal_Pair_Open ("type", Arena, State);
      case Value.Kind is
         when Text_Node => Put (Arena, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""c3Ry""]]]]]]]");
         when Bytes_Node => Put (Arena, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Ynl0ZXM=""]]]]]]]");
         when Null_Node => Put (Arena, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Tm9uZVR5cGU=""]]]]]]]");
         when Copy_Archive => null;
      end case;
      Put (Arena, State, List_Close & ",");
      Literal_Pair_Open ("value", Arena, State);
      if Value.Kind = Null_Node then
         Put (Arena, State, Null_Atom);
      else
         Put (Arena, State, Text_Open);
         Append_Base64 (Arena, Value.Payload, Value.Kind = Bytes_Node, State);
         Put (Arena, State, Text_Close);
      end if;
      Put (Arena, State, List_Close & Object_Close);
   end Append_Node;

   procedure Append_Field
     (Arena : in out E.Bytes; Name : String; Value : Node;
      State : in out Length_Result)
   with Global => null is
   begin
      Literal_Pair_Open (Name, Arena, State);
      Append_Node (Arena, Value, State);
      Put (Arena, State, List_Close);
   end Append_Field;

   procedure Append_Base
     (Arena : in out E.Bytes; Row : C.Event_Row; Used : in out E.Count;
      Length : out Length_Result; Complete : out Boolean)
   is
      Before : constant E.Count := Used;
      State : Length_Result;
   begin
      Length := (False, 0); Complete := False;
      if not Base_In_Prefix (Arena, Row, Used) then return; end if;
      Length := Base_Length (Arena, Row);
      if not Length.Valid or else Length.Needed > Arena'Length - Used then return; end if;
      State := (True, Used);
      Put (Arena, State, Dictionary_Open & Object_Open);
      Append_Field (Arena, "previous", (Text_Node, Row.Previous), State);
      Put (Arena, State, ",");
      Append_Field (Arena, "generation", (Bytes_Node, Row.Generation), State);
      Put (Arena, State, ",");
      Append_Field (Arena, "operation", (Text_Node, Row.Operation), State);
      Put (Arena, State, ",");
      Append_Field (Arena, "subject_kind", (Text_Node, Row.Subject_Kind), State);
      Put (Arena, State, ",");
      Append_Field (Arena, "subject", (Text_Node, Row.Subject), State);
      Put (Arena, State, ",");
      Append_Field (Arena, "subgeneration", (Bytes_Node, Row.Subgeneration), State);
      Put (Arena, State, ",");
      Append_Field (Arena, "kind", (Text_Node, Row.Kind), State);
      Put (Arena, State, ",");
      Append_Field (Arena, "actor", (Text_Node, Row.Actor), State);
      Put (Arena, State, ",");
      Append_Field (Arena, "record", (Copy_Archive, Row.Record_Archive), State);
      Put (Arena, State, Object_Close & Dictionary_Close);
      pragma Assert (State.Valid and then State.Needed = Before + Length.Needed);
      Used := State.Needed;
      Complete := True;
   end Append_Base;

   procedure Append_Event_Head
     (Arena : in out E.Bytes; Event_Id, Genesis_Row : E.Span;
      Used : in out E.Count; Length : out Length_Result; Complete : out Boolean)
   is
      Before : constant E.Count := Used;
      State : Length_Result;
   begin
      Length := (False, 0); Complete := False;
      if not Head_In_Prefix (Arena, Event_Id, Genesis_Row, Used) then return; end if;
      Length := Head_Length (Arena, Event_Id, Genesis_Row);
      if not Length.Valid or else Length.Needed > Arena'Length - Used then return; end if;
      State := (True, Used);
      Put (Arena, State, Dictionary_Open & Object_Open);
      Literal_Pair_Open ("head_kind", Arena, State);
      Put (Arena, State, "[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""b2JqZWN0""]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""dHlwZQ==""]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""c3Ry""]]]]]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""dmFsdWU=""]]]]]]],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""c2NhbGFy""],[""str"",""YXRvbQ==""]]],[""array"",[[""str"",""c2NhbGFy""],[""str"",""RVZFTlQ=""]]]]]]]]]]]]]]]]]]]");
      Put (Arena, State, List_Close & ",");
      Append_Field (Arena, "head", (Text_Node, Event_Id), State);
      Put (Arena, State, ",");
      Append_Field (Arena, "genesis", (Copy_Archive, Genesis_Row), State);
      Put (Arena, State, Object_Close & Dictionary_Close);
      pragma Assert (State.Valid and then State.Needed = Before + Length.Needed);
      Used := State.Needed;
      Complete := True;
   end Append_Event_Head;

end Worldline.Custody_V2_Delta_Encoding;
