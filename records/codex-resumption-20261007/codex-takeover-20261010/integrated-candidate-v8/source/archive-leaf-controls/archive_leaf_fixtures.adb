with Resource_Quantities;
with Worldline.Archive_Base64;
with Worldline.Archive_Text;

package body Archive_Leaf_Fixtures is
   package Q renames Resource_Quantities;
   package B renames Worldline.Archive_Base64;
   package T renames Worldline.Archive_Text;
   use type Q.Byte;
   use type Q.Byte_Count;
   use type Q.Byte_Array;
   use type T.Decode_Status;
   use type T.Code_Point;
   use type T.Span;

   procedure Check (Condition : Boolean; Label : String) is
   begin
      if not Condition then
         raise Program_Error with Label;
      end if;
   end Check;

   procedure Base64_Valid
     (Label : String; Encoded, Expected : Q.Byte_Array;
      Padding_Text : String)
   is
      Item : constant B.Span :=
        (First => Encoded'First, Length => Encoded'Length);
      Output_First : constant Q.Byte_Index := 7;
      Output : Q.Byte_Array
        (Output_First .. Output_First - 1 + Expected'Length) := (others => 16#A5#);
      Wrapped : constant Q.Byte_Array :=
        Q.Byte_Array'(1 => 16#FF#) & Encoded & Q.Byte_Array'(1 => 16#FF#);
      Interior : constant B.Span :=
        (First => Wrapped'First + 1, Length => Encoded'Length);
   begin
      Check (B.Canonical (Encoded, Item), Label & ": canonical");
      Check (B.Decoded_Length (Encoded, Item) = Expected'Length,
             Label & ": output length");
      if Item.Length >= 4 then
         Check (B.Padding (Encoded, Item) = Padding_Text'Length,
                Label & ": original encoded padding");
      end if;
      B.Decode (Encoded, Item, Output);
      Check (Output = Expected, Label & ": exact lossless output bytes");
      for I in Expected'Range loop
         Check (B.Decoded_Byte (Encoded, Item, I - Expected'First) = Expected (I),
                Label & ": every projected byte");
      end loop;
      Check (B.Canonical (Wrapped, Interior), Label & ": exact interior span");
      B.Decode (Wrapped, Interior, Output);
      Check (Output = Expected, Label & ": interior output bytes");
   end Base64_Valid;

   procedure Base64_Invalid (Label : String; Encoded : Q.Byte_Array) is
      Item : constant B.Span :=
        (First => Encoded'First, Length => Encoded'Length);
   begin
      Check (not B.Canonical (Encoded, Item), Label & ": noncanonical rejected");
      --  Do not call Decode outside its original canonicality precondition.
   end Base64_Invalid;

   procedure Cursor
     (Label : String; Data : Q.Byte_Array; Item : T.Span;
      Offset : Q.Byte_Count; Status : T.Decode_Status;
      Value : T.Code_Point := 0; Width : Q.Byte_Count := 0;
      Next_Offset : Q.Byte_Count := 0)
   is
      Result : constant T.Scalar_Result := T.Read (Data, Item, Offset);
   begin
      Check (Result.Raw = Item and then Result.Start = Offset,
             Label & ": lossless raw span and original cursor");
      Check (Result.Status = Status, Label & ": exact cursor status");
      if Status = T.Decoded then
         Check (Result.Value = Value and then Result.Width = Width and then
                  Result.Next_Offset = Next_Offset,
                Label & ": observed codepoint width and JACKAL next cursor");
         Check (T.Unit_Width (Data, Item, Offset) = Width,
                Label & ": exact unit width");
         Check (T.Value_At (Data, Item, Offset) = Value,
                Label & ": exact observed codepoint projection");
      else
         Check (T.Unit_Width (Data, Item, Offset) = 0,
                Label & ": no decoded unit at rejected/end cursor");
      end if;
   end Cursor;

   procedure Span_Boundaries is
      Empty : constant Q.Byte_Array (1 .. 0) := (others => 0);
      Empty_Output : Q.Byte_Array (1 .. 0);
      Last_Text : constant Q.Byte_Array (Q.Byte_Index'Last .. Q.Byte_Index'Last) :=
        (others => Character'Pos ('A'));
      Encoded : constant Q.Byte_Array :=
        (Character'Pos ('A'), Character'Pos ('A'), Character'Pos ('='), Character'Pos ('='));
      Last_Base64 : constant Q.Byte_Array
        (Q.Byte_Index'Last - Encoded'Length + 1 .. Q.Byte_Index'Last) := Encoded;
      Byte_Output : Q.Byte_Array (Q.Byte_Index'Last .. Q.Byte_Index'Last);
      B_Empty : constant B.Span := (First => Q.Byte_Index'Last, Length => 0);
      T_Empty : constant T.Span := (First => Q.Byte_Index'Last, Length => 0);
      B_Last : constant B.Span := (First => Last_Base64'First, Length => Last_Base64'Length);
      T_Last : constant T.Span := (First => Last_Text'First, Length => Last_Text'Length);
      B_Invalid : constant B.Span := (First => 1, Length => Q.Byte_Count'Last);
      T_Invalid : constant T.Span := (First => 1, Length => Q.Byte_Count'Last);
   begin
      Check (B.Canonical (Empty, B_Empty), "empty base64 arbitrary first");
      Check (B.Decoded_Length (Empty, B_Empty) = 0, "empty base64 length");
      B.Decode (Empty, B_Empty, Empty_Output);
      Check (T.Text_Valid (Empty, T_Empty), "empty text arbitrary first");
      Cursor ("empty end", Empty, T_Empty, 0, T.End_Of_Text);
      Cursor ("empty out of range", Empty, T_Empty, 1, T.Invalid_Position);
      Check (B.Canonical (Last_Base64, B_Last), "base64 last-index span");
      B.Decode (Last_Base64, B_Last, Byte_Output);
      Check (Byte_Output = Q.Byte_Array'(1 => 0), "last-index output exact NUL");
      Check (T.Text_Valid (Last_Text, T_Last), "text last-index span");
      Cursor ("last-index text", Last_Text, T_Last, 0, T.Decoded,
              Character'Pos ('A'), 1, 1);
      Cursor ("last-index text end", Last_Text, T_Last, 1, T.End_Of_Text);
      Check (not B.Span_Valid (Last_Base64, B_Invalid), "invalid base64 extent");
      Check (not B.Canonical (Last_Base64, B_Invalid), "invalid base64 span rejected");
      Check (not T.Span_Valid (Last_Text, T_Invalid), "invalid text extent");
      Check (not T.Text_Valid (Last_Text, T_Invalid), "invalid whole text span");
      Cursor ("invalid span", Last_Text, T_Invalid, 0, T.Invalid_Position);
      Check (not T.Text_Valid
        (Last_Text, (First => Last_Text'First, Length => Last_Text'Length + 1)),
        "valid first but overlong span");
      Check (not B.Canonical
        (Last_Base64, (First => Last_Base64'First, Length => Last_Base64'Length + 1)),
        "valid base64 first but overlong span");
   end Span_Boundaries;

   procedure Run is
   begin
      Base64_Valid ("base64 empty",
         Q.Byte_Array'(1 .. 0 => 0),
         Q.Byte_Array'(1 .. 0 => 0), "");
      Base64_Valid ("base64 f",
         Q.Byte_Array'(1 => 16#5A#, 2 => 16#67#, 3 => 16#3D#, 4 => 16#3D#),
         Q.Byte_Array'(1 => 16#66#), "==");
      Base64_Valid ("base64 fo",
         Q.Byte_Array'(1 => 16#5A#, 2 => 16#6D#, 3 => 16#38#, 4 => 16#3D#),
         Q.Byte_Array'(1 => 16#66#, 2 => 16#6F#), "=");
      Base64_Valid ("base64 foo",
         Q.Byte_Array'(1 => 16#5A#, 2 => 16#6D#, 3 => 16#39#, 4 => 16#76#),
         Q.Byte_Array'(1 => 16#66#, 2 => 16#6F#, 3 => 16#6F#), "");
      Base64_Valid ("base64 foob",
         Q.Byte_Array'(1 => 16#5A#, 2 => 16#6D#, 3 => 16#39#, 4 => 16#76#, 5 => 16#59#, 6 => 16#67#, 7 => 16#3D#, 8 => 16#3D#),
         Q.Byte_Array'(1 => 16#66#, 2 => 16#6F#, 3 => 16#6F#, 4 => 16#62#), "==");
      Base64_Valid ("base64 fooba",
         Q.Byte_Array'(1 => 16#5A#, 2 => 16#6D#, 3 => 16#39#, 4 => 16#76#, 5 => 16#59#, 6 => 16#6D#, 7 => 16#45#, 8 => 16#3D#),
         Q.Byte_Array'(1 => 16#66#, 2 => 16#6F#, 3 => 16#6F#, 4 => 16#62#, 5 => 16#61#), "=");
      Base64_Valid ("base64 foobar",
         Q.Byte_Array'(1 => 16#5A#, 2 => 16#6D#, 3 => 16#39#, 4 => 16#76#, 5 => 16#59#, 6 => 16#6D#, 7 => 16#46#, 8 => 16#79#),
         Q.Byte_Array'(1 => 16#66#, 2 => 16#6F#, 3 => 16#6F#, 4 => 16#62#, 5 => 16#61#, 6 => 16#72#), "");
      Base64_Valid ("base64 nul",
         Q.Byte_Array'(1 => 16#41#, 2 => 16#41#, 3 => 16#3D#, 4 => 16#3D#),
         Q.Byte_Array'(1 => 16#00#), "==");
      Base64_Valid ("base64 ff",
         Q.Byte_Array'(1 => 16#2F#, 2 => 16#77#, 3 => 16#3D#, 4 => 16#3D#),
         Q.Byte_Array'(1 => 16#FF#), "==");
      Base64_Valid ("base64 plus_slash",
         Q.Byte_Array'(1 => 16#2B#, 2 => 16#2F#, 3 => 16#38#, 4 => 16#3D#),
         Q.Byte_Array'(1 => 16#FB#, 2 => 16#FF#), "=");
      Base64_Valid ("base64 binary",
         Q.Byte_Array'(1 => 16#41#, 2 => 16#41#, 3 => 16#45#, 4 => 16#43#, 5 => 16#66#, 6 => 16#34#, 7 => 16#44#, 8 => 16#2B#, 9 => 16#2F#, 10 => 16#77#, 11 => 16#3D#, 12 => 16#3D#),
         Q.Byte_Array'(1 => 16#00#, 2 => 16#01#, 3 => 16#02#, 4 => 16#7F#, 5 => 16#80#, 6 => 16#FE#, 7 => 16#FF#), "==");
      Base64_Invalid ("base64 invalid_41",
         Q.Byte_Array'(1 => 16#41#));
      Base64_Invalid ("base64 invalid_4141",
         Q.Byte_Array'(1 => 16#41#, 2 => 16#41#));
      Base64_Invalid ("base64 invalid_414141",
         Q.Byte_Array'(1 => 16#41#, 2 => 16#41#, 3 => 16#41#));
      Base64_Invalid ("base64 invalid_414141413d",
         Q.Byte_Array'(1 => 16#41#, 2 => 16#41#, 3 => 16#41#, 4 => 16#41#, 5 => 16#3D#));
      Base64_Invalid ("base64 invalid_3d414141",
         Q.Byte_Array'(1 => 16#3D#, 2 => 16#41#, 3 => 16#41#, 4 => 16#41#));
      Base64_Invalid ("base64 invalid_413d4141",
         Q.Byte_Array'(1 => 16#41#, 2 => 16#3D#, 3 => 16#41#, 4 => 16#41#));
      Base64_Invalid ("base64 invalid_41413d41",
         Q.Byte_Array'(1 => 16#41#, 2 => 16#41#, 3 => 16#3D#, 4 => 16#41#));
      Base64_Invalid ("base64 invalid_3d3d3d3d",
         Q.Byte_Array'(1 => 16#3D#, 2 => 16#3D#, 3 => 16#3D#, 4 => 16#3D#));
      Base64_Invalid ("base64 invalid_413d3d3d",
         Q.Byte_Array'(1 => 16#41#, 2 => 16#3D#, 3 => 16#3D#, 4 => 16#3D#));
      Base64_Invalid ("base64 invalid_4141413d3d3d",
         Q.Byte_Array'(1 => 16#41#, 2 => 16#41#, 3 => 16#41#, 4 => 16#3D#, 5 => 16#3D#, 6 => 16#3D#));
      Base64_Invalid ("base64 invalid_41413d3d41413d3d",
         Q.Byte_Array'(1 => 16#41#, 2 => 16#41#, 3 => 16#3D#, 4 => 16#3D#, 5 => 16#41#, 6 => 16#41#, 7 => 16#3D#, 8 => 16#3D#));
      Base64_Invalid ("base64 invalid_4141413d41414141",
         Q.Byte_Array'(1 => 16#41#, 2 => 16#41#, 3 => 16#41#, 4 => 16#3D#, 5 => 16#41#, 6 => 16#41#, 7 => 16#41#, 8 => 16#41#));
      Base64_Invalid ("base64 invalid_41413d3d0a",
         Q.Byte_Array'(1 => 16#41#, 2 => 16#41#, 3 => 16#3D#, 4 => 16#3D#, 5 => 16#0A#));
      Base64_Invalid ("base64 invalid_2041413d3d",
         Q.Byte_Array'(1 => 16#20#, 2 => 16#41#, 3 => 16#41#, 4 => 16#3D#, 5 => 16#3D#));
      Base64_Invalid ("base64 invalid_41412d5f",
         Q.Byte_Array'(1 => 16#41#, 2 => 16#41#, 3 => 16#2D#, 4 => 16#5F#));
      Base64_Invalid ("base64 invalid_41412a3d",
         Q.Byte_Array'(1 => 16#41#, 2 => 16#41#, 3 => 16#2A#, 4 => 16#3D#));
      Base64_Invalid ("base64 invalid_41423d3d",
         Q.Byte_Array'(1 => 16#41#, 2 => 16#42#, 3 => 16#3D#, 4 => 16#3D#));
      Base64_Invalid ("base64 invalid_4141423d",
         Q.Byte_Array'(1 => 16#41#, 2 => 16#41#, 3 => 16#42#, 4 => 16#3D#));
      Base64_Invalid ("base64 invalid_2f783d3d",
         Q.Byte_Array'(1 => 16#2F#, 2 => 16#78#, 3 => 16#3D#, 4 => 16#3D#));
      Base64_Invalid ("base64 invalid_2f2f393d",
         Q.Byte_Array'(1 => 16#2F#, 2 => 16#2F#, 3 => 16#39#, 4 => 16#3D#));
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 .. 0 => 0);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = True, "text empty whole Data");
         Cursor ("text empty Data cursor 0", Data, Item, 0, T.End_Of_Text);
         Cursor ("text empty Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = True, "text empty whole Wrapped");
         Cursor ("text empty Wrapped cursor 0", Wrapped, Interior, 0, T.End_Of_Text);
         Cursor ("text empty Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#00#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = True, "text nul whole Data");
         Cursor ("text nul Data cursor 0", Data, Item, 0, T.Decoded, 0, 1, 1);
         Cursor ("text nul Data cursor 1", Data, Item, 1, T.End_Of_Text);
         Cursor ("text nul Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = True, "text nul whole Wrapped");
         Cursor ("text nul Wrapped cursor 0", Wrapped, Interior, 0, T.Decoded, 0, 1, 1);
         Cursor ("text nul Wrapped cursor 1", Wrapped, Interior, 1, T.End_Of_Text);
         Cursor ("text nul Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#41#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = True, "text ascii whole Data");
         Cursor ("text ascii Data cursor 0", Data, Item, 0, T.Decoded, 65, 1, 1);
         Cursor ("text ascii Data cursor 1", Data, Item, 1, T.End_Of_Text);
         Cursor ("text ascii Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = True, "text ascii whole Wrapped");
         Cursor ("text ascii Wrapped cursor 0", Wrapped, Interior, 0, T.Decoded, 65, 1, 1);
         Cursor ("text ascii Wrapped cursor 1", Wrapped, Interior, 1, T.End_Of_Text);
         Cursor ("text ascii Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#C2#, 2 => 16#A2#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = True, "text two_byte whole Data");
         Cursor ("text two_byte Data cursor 0", Data, Item, 0, T.Decoded, 162, 2, 2);
         Cursor ("text two_byte Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text two_byte Data cursor 2", Data, Item, 2, T.End_Of_Text);
         Cursor ("text two_byte Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = True, "text two_byte whole Wrapped");
         Cursor ("text two_byte Wrapped cursor 0", Wrapped, Interior, 0, T.Decoded, 162, 2, 2);
         Cursor ("text two_byte Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text two_byte Wrapped cursor 2", Wrapped, Interior, 2, T.End_Of_Text);
         Cursor ("text two_byte Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#E2#, 2 => 16#82#, 3 => 16#AC#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = True, "text three_byte whole Data");
         Cursor ("text three_byte Data cursor 0", Data, Item, 0, T.Decoded, 8364, 3, 3);
         Cursor ("text three_byte Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text three_byte Data cursor 2", Data, Item, 2, T.Invalid_Sequence);
         Cursor ("text three_byte Data cursor 3", Data, Item, 3, T.End_Of_Text);
         Cursor ("text three_byte Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = True, "text three_byte whole Wrapped");
         Cursor ("text three_byte Wrapped cursor 0", Wrapped, Interior, 0, T.Decoded, 8364, 3, 3);
         Cursor ("text three_byte Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text three_byte Wrapped cursor 2", Wrapped, Interior, 2, T.Invalid_Sequence);
         Cursor ("text three_byte Wrapped cursor 3", Wrapped, Interior, 3, T.End_Of_Text);
         Cursor ("text three_byte Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#ED#, 2 => 16#A0#, 3 => 16#80#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = True, "text high_surrogate whole Data");
         Cursor ("text high_surrogate Data cursor 0", Data, Item, 0, T.Decoded, 55296, 3, 3);
         Cursor ("text high_surrogate Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text high_surrogate Data cursor 2", Data, Item, 2, T.Invalid_Sequence);
         Cursor ("text high_surrogate Data cursor 3", Data, Item, 3, T.End_Of_Text);
         Cursor ("text high_surrogate Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = True, "text high_surrogate whole Wrapped");
         Cursor ("text high_surrogate Wrapped cursor 0", Wrapped, Interior, 0, T.Decoded, 55296, 3, 3);
         Cursor ("text high_surrogate Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text high_surrogate Wrapped cursor 2", Wrapped, Interior, 2, T.Invalid_Sequence);
         Cursor ("text high_surrogate Wrapped cursor 3", Wrapped, Interior, 3, T.End_Of_Text);
         Cursor ("text high_surrogate Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#ED#, 2 => 16#BF#, 3 => 16#BF#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = True, "text low_surrogate whole Data");
         Cursor ("text low_surrogate Data cursor 0", Data, Item, 0, T.Decoded, 57343, 3, 3);
         Cursor ("text low_surrogate Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text low_surrogate Data cursor 2", Data, Item, 2, T.Invalid_Sequence);
         Cursor ("text low_surrogate Data cursor 3", Data, Item, 3, T.End_Of_Text);
         Cursor ("text low_surrogate Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = True, "text low_surrogate whole Wrapped");
         Cursor ("text low_surrogate Wrapped cursor 0", Wrapped, Interior, 0, T.Decoded, 57343, 3, 3);
         Cursor ("text low_surrogate Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text low_surrogate Wrapped cursor 2", Wrapped, Interior, 2, T.Invalid_Sequence);
         Cursor ("text low_surrogate Wrapped cursor 3", Wrapped, Interior, 3, T.End_Of_Text);
         Cursor ("text low_surrogate Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#ED#, 2 => 16#A0#, 3 => 16#80#, 4 => 16#ED#, 5 => 16#B0#, 6 => 16#80#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = True, "text surrogate_pair_uncombined whole Data");
         Cursor ("text surrogate_pair_uncombined Data cursor 0", Data, Item, 0, T.Decoded, 55296, 3, 3);
         Cursor ("text surrogate_pair_uncombined Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text surrogate_pair_uncombined Data cursor 2", Data, Item, 2, T.Invalid_Sequence);
         Cursor ("text surrogate_pair_uncombined Data cursor 3", Data, Item, 3, T.Decoded, 56320, 3, 6);
         Cursor ("text surrogate_pair_uncombined Data cursor 4", Data, Item, 4, T.Invalid_Sequence);
         Cursor ("text surrogate_pair_uncombined Data cursor 5", Data, Item, 5, T.Invalid_Sequence);
         Cursor ("text surrogate_pair_uncombined Data cursor 6", Data, Item, 6, T.End_Of_Text);
         Cursor ("text surrogate_pair_uncombined Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = True, "text surrogate_pair_uncombined whole Wrapped");
         Cursor ("text surrogate_pair_uncombined Wrapped cursor 0", Wrapped, Interior, 0, T.Decoded, 55296, 3, 3);
         Cursor ("text surrogate_pair_uncombined Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text surrogate_pair_uncombined Wrapped cursor 2", Wrapped, Interior, 2, T.Invalid_Sequence);
         Cursor ("text surrogate_pair_uncombined Wrapped cursor 3", Wrapped, Interior, 3, T.Decoded, 56320, 3, 6);
         Cursor ("text surrogate_pair_uncombined Wrapped cursor 4", Wrapped, Interior, 4, T.Invalid_Sequence);
         Cursor ("text surrogate_pair_uncombined Wrapped cursor 5", Wrapped, Interior, 5, T.Invalid_Sequence);
         Cursor ("text surrogate_pair_uncombined Wrapped cursor 6", Wrapped, Interior, 6, T.End_Of_Text);
         Cursor ("text surrogate_pair_uncombined Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#F0#, 2 => 16#9F#, 3 => 16#98#, 4 => 16#80#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = True, "text non_bmp whole Data");
         Cursor ("text non_bmp Data cursor 0", Data, Item, 0, T.Decoded, 128512, 4, 4);
         Cursor ("text non_bmp Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text non_bmp Data cursor 2", Data, Item, 2, T.Invalid_Sequence);
         Cursor ("text non_bmp Data cursor 3", Data, Item, 3, T.Invalid_Sequence);
         Cursor ("text non_bmp Data cursor 4", Data, Item, 4, T.End_Of_Text);
         Cursor ("text non_bmp Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = True, "text non_bmp whole Wrapped");
         Cursor ("text non_bmp Wrapped cursor 0", Wrapped, Interior, 0, T.Decoded, 128512, 4, 4);
         Cursor ("text non_bmp Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text non_bmp Wrapped cursor 2", Wrapped, Interior, 2, T.Invalid_Sequence);
         Cursor ("text non_bmp Wrapped cursor 3", Wrapped, Interior, 3, T.Invalid_Sequence);
         Cursor ("text non_bmp Wrapped cursor 4", Wrapped, Interior, 4, T.End_Of_Text);
         Cursor ("text non_bmp Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#F4#, 2 => 16#8F#, 3 => 16#BF#, 4 => 16#BF#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = True, "text maximum_codepoint whole Data");
         Cursor ("text maximum_codepoint Data cursor 0", Data, Item, 0, T.Decoded, 1114111, 4, 4);
         Cursor ("text maximum_codepoint Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text maximum_codepoint Data cursor 2", Data, Item, 2, T.Invalid_Sequence);
         Cursor ("text maximum_codepoint Data cursor 3", Data, Item, 3, T.Invalid_Sequence);
         Cursor ("text maximum_codepoint Data cursor 4", Data, Item, 4, T.End_Of_Text);
         Cursor ("text maximum_codepoint Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = True, "text maximum_codepoint whole Wrapped");
         Cursor ("text maximum_codepoint Wrapped cursor 0", Wrapped, Interior, 0, T.Decoded, 1114111, 4, 4);
         Cursor ("text maximum_codepoint Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text maximum_codepoint Wrapped cursor 2", Wrapped, Interior, 2, T.Invalid_Sequence);
         Cursor ("text maximum_codepoint Wrapped cursor 3", Wrapped, Interior, 3, T.Invalid_Sequence);
         Cursor ("text maximum_codepoint Wrapped cursor 4", Wrapped, Interior, 4, T.End_Of_Text);
         Cursor ("text maximum_codepoint Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#EF#, 2 => 16#BB#, 3 => 16#BF#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = True, "text bom whole Data");
         Cursor ("text bom Data cursor 0", Data, Item, 0, T.Decoded, 65279, 3, 3);
         Cursor ("text bom Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text bom Data cursor 2", Data, Item, 2, T.Invalid_Sequence);
         Cursor ("text bom Data cursor 3", Data, Item, 3, T.End_Of_Text);
         Cursor ("text bom Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = True, "text bom whole Wrapped");
         Cursor ("text bom Wrapped cursor 0", Wrapped, Interior, 0, T.Decoded, 65279, 3, 3);
         Cursor ("text bom Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text bom Wrapped cursor 2", Wrapped, Interior, 2, T.Invalid_Sequence);
         Cursor ("text bom Wrapped cursor 3", Wrapped, Interior, 3, T.End_Of_Text);
         Cursor ("text bom Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#EF#, 2 => 16#BF#, 3 => 16#BF#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = True, "text noncharacter whole Data");
         Cursor ("text noncharacter Data cursor 0", Data, Item, 0, T.Decoded, 65535, 3, 3);
         Cursor ("text noncharacter Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text noncharacter Data cursor 2", Data, Item, 2, T.Invalid_Sequence);
         Cursor ("text noncharacter Data cursor 3", Data, Item, 3, T.End_Of_Text);
         Cursor ("text noncharacter Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = True, "text noncharacter whole Wrapped");
         Cursor ("text noncharacter Wrapped cursor 0", Wrapped, Interior, 0, T.Decoded, 65535, 3, 3);
         Cursor ("text noncharacter Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text noncharacter Wrapped cursor 2", Wrapped, Interior, 2, T.Invalid_Sequence);
         Cursor ("text noncharacter Wrapped cursor 3", Wrapped, Interior, 3, T.End_Of_Text);
         Cursor ("text noncharacter Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#65#, 2 => 16#CC#, 3 => 16#81#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = True, "text combining whole Data");
         Cursor ("text combining Data cursor 0", Data, Item, 0, T.Decoded, 101, 1, 1);
         Cursor ("text combining Data cursor 1", Data, Item, 1, T.Decoded, 769, 2, 3);
         Cursor ("text combining Data cursor 2", Data, Item, 2, T.Invalid_Sequence);
         Cursor ("text combining Data cursor 3", Data, Item, 3, T.End_Of_Text);
         Cursor ("text combining Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = True, "text combining whole Wrapped");
         Cursor ("text combining Wrapped cursor 0", Wrapped, Interior, 0, T.Decoded, 101, 1, 1);
         Cursor ("text combining Wrapped cursor 1", Wrapped, Interior, 1, T.Decoded, 769, 2, 3);
         Cursor ("text combining Wrapped cursor 2", Wrapped, Interior, 2, T.Invalid_Sequence);
         Cursor ("text combining Wrapped cursor 3", Wrapped, Interior, 3, T.End_Of_Text);
         Cursor ("text combining Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#41#, 2 => 16#00#, 3 => 16#ED#, 4 => 16#A0#, 5 => 16#80#, 6 => 16#F0#, 7 => 16#9F#, 8 => 16#98#, 9 => 16#80#, 10 => 16#5A#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = True, "text mixed whole Data");
         Cursor ("text mixed Data cursor 0", Data, Item, 0, T.Decoded, 65, 1, 1);
         Cursor ("text mixed Data cursor 1", Data, Item, 1, T.Decoded, 0, 1, 2);
         Cursor ("text mixed Data cursor 2", Data, Item, 2, T.Decoded, 55296, 3, 5);
         Cursor ("text mixed Data cursor 3", Data, Item, 3, T.Invalid_Sequence);
         Cursor ("text mixed Data cursor 4", Data, Item, 4, T.Invalid_Sequence);
         Cursor ("text mixed Data cursor 5", Data, Item, 5, T.Decoded, 128512, 4, 9);
         Cursor ("text mixed Data cursor 6", Data, Item, 6, T.Invalid_Sequence);
         Cursor ("text mixed Data cursor 7", Data, Item, 7, T.Invalid_Sequence);
         Cursor ("text mixed Data cursor 8", Data, Item, 8, T.Invalid_Sequence);
         Cursor ("text mixed Data cursor 9", Data, Item, 9, T.Decoded, 90, 1, 10);
         Cursor ("text mixed Data cursor 10", Data, Item, 10, T.End_Of_Text);
         Cursor ("text mixed Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = True, "text mixed whole Wrapped");
         Cursor ("text mixed Wrapped cursor 0", Wrapped, Interior, 0, T.Decoded, 65, 1, 1);
         Cursor ("text mixed Wrapped cursor 1", Wrapped, Interior, 1, T.Decoded, 0, 1, 2);
         Cursor ("text mixed Wrapped cursor 2", Wrapped, Interior, 2, T.Decoded, 55296, 3, 5);
         Cursor ("text mixed Wrapped cursor 3", Wrapped, Interior, 3, T.Invalid_Sequence);
         Cursor ("text mixed Wrapped cursor 4", Wrapped, Interior, 4, T.Invalid_Sequence);
         Cursor ("text mixed Wrapped cursor 5", Wrapped, Interior, 5, T.Decoded, 128512, 4, 9);
         Cursor ("text mixed Wrapped cursor 6", Wrapped, Interior, 6, T.Invalid_Sequence);
         Cursor ("text mixed Wrapped cursor 7", Wrapped, Interior, 7, T.Invalid_Sequence);
         Cursor ("text mixed Wrapped cursor 8", Wrapped, Interior, 8, T.Invalid_Sequence);
         Cursor ("text mixed Wrapped cursor 9", Wrapped, Interior, 9, T.Decoded, 90, 1, 10);
         Cursor ("text mixed Wrapped cursor 10", Wrapped, Interior, 10, T.End_Of_Text);
         Cursor ("text mixed Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#C0#, 2 => 16#80#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = False, "text overlong_two whole Data");
         Cursor ("text overlong_two Data cursor 0", Data, Item, 0, T.Invalid_Sequence);
         Cursor ("text overlong_two Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text overlong_two Data cursor 2", Data, Item, 2, T.End_Of_Text);
         Cursor ("text overlong_two Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = False, "text overlong_two whole Wrapped");
         Cursor ("text overlong_two Wrapped cursor 0", Wrapped, Interior, 0, T.Invalid_Sequence);
         Cursor ("text overlong_two Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text overlong_two Wrapped cursor 2", Wrapped, Interior, 2, T.End_Of_Text);
         Cursor ("text overlong_two Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#E0#, 2 => 16#80#, 3 => 16#80#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = False, "text overlong_three whole Data");
         Cursor ("text overlong_three Data cursor 0", Data, Item, 0, T.Invalid_Sequence);
         Cursor ("text overlong_three Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text overlong_three Data cursor 2", Data, Item, 2, T.Invalid_Sequence);
         Cursor ("text overlong_three Data cursor 3", Data, Item, 3, T.End_Of_Text);
         Cursor ("text overlong_three Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = False, "text overlong_three whole Wrapped");
         Cursor ("text overlong_three Wrapped cursor 0", Wrapped, Interior, 0, T.Invalid_Sequence);
         Cursor ("text overlong_three Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text overlong_three Wrapped cursor 2", Wrapped, Interior, 2, T.Invalid_Sequence);
         Cursor ("text overlong_three Wrapped cursor 3", Wrapped, Interior, 3, T.End_Of_Text);
         Cursor ("text overlong_three Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#F0#, 2 => 16#80#, 3 => 16#80#, 4 => 16#80#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = False, "text overlong_four whole Data");
         Cursor ("text overlong_four Data cursor 0", Data, Item, 0, T.Invalid_Sequence);
         Cursor ("text overlong_four Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text overlong_four Data cursor 2", Data, Item, 2, T.Invalid_Sequence);
         Cursor ("text overlong_four Data cursor 3", Data, Item, 3, T.Invalid_Sequence);
         Cursor ("text overlong_four Data cursor 4", Data, Item, 4, T.End_Of_Text);
         Cursor ("text overlong_four Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = False, "text overlong_four whole Wrapped");
         Cursor ("text overlong_four Wrapped cursor 0", Wrapped, Interior, 0, T.Invalid_Sequence);
         Cursor ("text overlong_four Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text overlong_four Wrapped cursor 2", Wrapped, Interior, 2, T.Invalid_Sequence);
         Cursor ("text overlong_four Wrapped cursor 3", Wrapped, Interior, 3, T.Invalid_Sequence);
         Cursor ("text overlong_four Wrapped cursor 4", Wrapped, Interior, 4, T.End_Of_Text);
         Cursor ("text overlong_four Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#C2#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = False, "text truncated_two whole Data");
         Cursor ("text truncated_two Data cursor 0", Data, Item, 0, T.Invalid_Sequence);
         Cursor ("text truncated_two Data cursor 1", Data, Item, 1, T.End_Of_Text);
         Cursor ("text truncated_two Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = False, "text truncated_two whole Wrapped");
         Cursor ("text truncated_two Wrapped cursor 0", Wrapped, Interior, 0, T.Invalid_Sequence);
         Cursor ("text truncated_two Wrapped cursor 1", Wrapped, Interior, 1, T.End_Of_Text);
         Cursor ("text truncated_two Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#E2#, 2 => 16#82#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = False, "text truncated_three whole Data");
         Cursor ("text truncated_three Data cursor 0", Data, Item, 0, T.Invalid_Sequence);
         Cursor ("text truncated_three Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text truncated_three Data cursor 2", Data, Item, 2, T.End_Of_Text);
         Cursor ("text truncated_three Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = False, "text truncated_three whole Wrapped");
         Cursor ("text truncated_three Wrapped cursor 0", Wrapped, Interior, 0, T.Invalid_Sequence);
         Cursor ("text truncated_three Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text truncated_three Wrapped cursor 2", Wrapped, Interior, 2, T.End_Of_Text);
         Cursor ("text truncated_three Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#F0#, 2 => 16#9F#, 3 => 16#98#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = False, "text truncated_four whole Data");
         Cursor ("text truncated_four Data cursor 0", Data, Item, 0, T.Invalid_Sequence);
         Cursor ("text truncated_four Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text truncated_four Data cursor 2", Data, Item, 2, T.Invalid_Sequence);
         Cursor ("text truncated_four Data cursor 3", Data, Item, 3, T.End_Of_Text);
         Cursor ("text truncated_four Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = False, "text truncated_four whole Wrapped");
         Cursor ("text truncated_four Wrapped cursor 0", Wrapped, Interior, 0, T.Invalid_Sequence);
         Cursor ("text truncated_four Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text truncated_four Wrapped cursor 2", Wrapped, Interior, 2, T.Invalid_Sequence);
         Cursor ("text truncated_four Wrapped cursor 3", Wrapped, Interior, 3, T.End_Of_Text);
         Cursor ("text truncated_four Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#80#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = False, "text isolated_continuation whole Data");
         Cursor ("text isolated_continuation Data cursor 0", Data, Item, 0, T.Invalid_Sequence);
         Cursor ("text isolated_continuation Data cursor 1", Data, Item, 1, T.End_Of_Text);
         Cursor ("text isolated_continuation Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = False, "text isolated_continuation whole Wrapped");
         Cursor ("text isolated_continuation Wrapped cursor 0", Wrapped, Interior, 0, T.Invalid_Sequence);
         Cursor ("text isolated_continuation Wrapped cursor 1", Wrapped, Interior, 1, T.End_Of_Text);
         Cursor ("text isolated_continuation Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#FF#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = False, "text illegal_lead whole Data");
         Cursor ("text illegal_lead Data cursor 0", Data, Item, 0, T.Invalid_Sequence);
         Cursor ("text illegal_lead Data cursor 1", Data, Item, 1, T.End_Of_Text);
         Cursor ("text illegal_lead Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = False, "text illegal_lead whole Wrapped");
         Cursor ("text illegal_lead Wrapped cursor 0", Wrapped, Interior, 0, T.Invalid_Sequence);
         Cursor ("text illegal_lead Wrapped cursor 1", Wrapped, Interior, 1, T.End_Of_Text);
         Cursor ("text illegal_lead Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#F4#, 2 => 16#90#, 3 => 16#80#, 4 => 16#80#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = False, "text above_codepoint_domain whole Data");
         Cursor ("text above_codepoint_domain Data cursor 0", Data, Item, 0, T.Invalid_Sequence);
         Cursor ("text above_codepoint_domain Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text above_codepoint_domain Data cursor 2", Data, Item, 2, T.Invalid_Sequence);
         Cursor ("text above_codepoint_domain Data cursor 3", Data, Item, 3, T.Invalid_Sequence);
         Cursor ("text above_codepoint_domain Data cursor 4", Data, Item, 4, T.End_Of_Text);
         Cursor ("text above_codepoint_domain Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = False, "text above_codepoint_domain whole Wrapped");
         Cursor ("text above_codepoint_domain Wrapped cursor 0", Wrapped, Interior, 0, T.Invalid_Sequence);
         Cursor ("text above_codepoint_domain Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text above_codepoint_domain Wrapped cursor 2", Wrapped, Interior, 2, T.Invalid_Sequence);
         Cursor ("text above_codepoint_domain Wrapped cursor 3", Wrapped, Interior, 3, T.Invalid_Sequence);
         Cursor ("text above_codepoint_domain Wrapped cursor 4", Wrapped, Interior, 4, T.End_Of_Text);
         Cursor ("text above_codepoint_domain Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#F8#, 2 => 16#88#, 3 => 16#80#, 4 => 16#80#, 5 => 16#80#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = False, "text illegal_five_lead whole Data");
         Cursor ("text illegal_five_lead Data cursor 0", Data, Item, 0, T.Invalid_Sequence);
         Cursor ("text illegal_five_lead Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text illegal_five_lead Data cursor 2", Data, Item, 2, T.Invalid_Sequence);
         Cursor ("text illegal_five_lead Data cursor 3", Data, Item, 3, T.Invalid_Sequence);
         Cursor ("text illegal_five_lead Data cursor 4", Data, Item, 4, T.Invalid_Sequence);
         Cursor ("text illegal_five_lead Data cursor 5", Data, Item, 5, T.End_Of_Text);
         Cursor ("text illegal_five_lead Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = False, "text illegal_five_lead whole Wrapped");
         Cursor ("text illegal_five_lead Wrapped cursor 0", Wrapped, Interior, 0, T.Invalid_Sequence);
         Cursor ("text illegal_five_lead Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text illegal_five_lead Wrapped cursor 2", Wrapped, Interior, 2, T.Invalid_Sequence);
         Cursor ("text illegal_five_lead Wrapped cursor 3", Wrapped, Interior, 3, T.Invalid_Sequence);
         Cursor ("text illegal_five_lead Wrapped cursor 4", Wrapped, Interior, 4, T.Invalid_Sequence);
         Cursor ("text illegal_five_lead Wrapped cursor 5", Wrapped, Interior, 5, T.End_Of_Text);
         Cursor ("text illegal_five_lead Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#E2#, 2 => 16#28#, 3 => 16#A1#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = False, "text bad_tail whole Data");
         Cursor ("text bad_tail Data cursor 0", Data, Item, 0, T.Invalid_Sequence);
         Cursor ("text bad_tail Data cursor 1", Data, Item, 1, T.Decoded, 40, 1, 2);
         Cursor ("text bad_tail Data cursor 2", Data, Item, 2, T.Invalid_Sequence);
         Cursor ("text bad_tail Data cursor 3", Data, Item, 3, T.End_Of_Text);
         Cursor ("text bad_tail Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = False, "text bad_tail whole Wrapped");
         Cursor ("text bad_tail Wrapped cursor 0", Wrapped, Interior, 0, T.Invalid_Sequence);
         Cursor ("text bad_tail Wrapped cursor 1", Wrapped, Interior, 1, T.Decoded, 40, 1, 2);
         Cursor ("text bad_tail Wrapped cursor 2", Wrapped, Interior, 2, T.Invalid_Sequence);
         Cursor ("text bad_tail Wrapped cursor 3", Wrapped, Interior, 3, T.End_Of_Text);
         Cursor ("text bad_tail Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#41#, 2 => 16#80#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = False, "text valid_then_invalid whole Data");
         Cursor ("text valid_then_invalid Data cursor 0", Data, Item, 0, T.Decoded, 65, 1, 1);
         Cursor ("text valid_then_invalid Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text valid_then_invalid Data cursor 2", Data, Item, 2, T.End_Of_Text);
         Cursor ("text valid_then_invalid Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = False, "text valid_then_invalid whole Wrapped");
         Cursor ("text valid_then_invalid Wrapped cursor 0", Wrapped, Interior, 0, T.Decoded, 65, 1, 1);
         Cursor ("text valid_then_invalid Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text valid_then_invalid Wrapped cursor 2", Wrapped, Interior, 2, T.End_Of_Text);
         Cursor ("text valid_then_invalid Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#80#, 2 => 16#41#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = False, "text invalid_then_valid whole Data");
         Cursor ("text invalid_then_valid Data cursor 0", Data, Item, 0, T.Invalid_Sequence);
         Cursor ("text invalid_then_valid Data cursor 1", Data, Item, 1, T.Decoded, 65, 1, 2);
         Cursor ("text invalid_then_valid Data cursor 2", Data, Item, 2, T.End_Of_Text);
         Cursor ("text invalid_then_valid Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = False, "text invalid_then_valid whole Wrapped");
         Cursor ("text invalid_then_valid Wrapped cursor 0", Wrapped, Interior, 0, T.Invalid_Sequence);
         Cursor ("text invalid_then_valid Wrapped cursor 1", Wrapped, Interior, 1, T.Decoded, 65, 1, 2);
         Cursor ("text invalid_then_valid Wrapped cursor 2", Wrapped, Interior, 2, T.End_Of_Text);
         Cursor ("text invalid_then_valid Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      declare
         Data : constant Q.Byte_Array := Q.Byte_Array'(1 => 16#00#, 2 => 16#E2#);
         Item : constant T.Span := (First => Data'First, Length => Data'Length);
         Wrapped : constant Q.Byte_Array :=
           Q.Byte_Array'(1 => 16#FF#) & Data & Q.Byte_Array'(1 => 16#FF#);
         Interior : constant T.Span :=
           (First => Wrapped'First + 1, Length => Data'Length);
      begin
         Check (T.Text_Valid (Data, Item) = False, "text nul_then_truncated whole Data");
         Cursor ("text nul_then_truncated Data cursor 0", Data, Item, 0, T.Decoded, 0, 1, 1);
         Cursor ("text nul_then_truncated Data cursor 1", Data, Item, 1, T.Invalid_Sequence);
         Cursor ("text nul_then_truncated Data cursor 2", Data, Item, 2, T.End_Of_Text);
         Cursor ("text nul_then_truncated Data beyond", Data, Item,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
         Check (T.Text_Valid (Wrapped, Interior) = False, "text nul_then_truncated whole Wrapped");
         Cursor ("text nul_then_truncated Wrapped cursor 0", Wrapped, Interior, 0, T.Decoded, 0, 1, 1);
         Cursor ("text nul_then_truncated Wrapped cursor 1", Wrapped, Interior, 1, T.Invalid_Sequence);
         Cursor ("text nul_then_truncated Wrapped cursor 2", Wrapped, Interior, 2, T.End_Of_Text);
         Cursor ("text nul_then_truncated Wrapped beyond", Wrapped, Interior,
                 Q.Byte_Count (Data'Length) + 1, T.Invalid_Position);
      end;
      Span_Boundaries;
   end Run;
end Archive_Leaf_Fixtures;
