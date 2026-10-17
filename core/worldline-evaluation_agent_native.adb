with Evaluation_Pending;
with Exact_Decimal;
with Decimal_Binary64;
with SPARK.Big_Integers;
with Worldline.Producer_Values;
with Worldline.Producer_Render;
with Worldline.Producer_Bytes;
with Worldline.Raw_JSON;
with Worldline.Runner_Outcome;
with Worldline.Runner_Lifecycle_Bytes;
with Worldline.Manager_Resource_Lifecycle;

package body Worldline.Evaluation_Agent_Native with SPARK_Mode is
   package V renames Worldline.Producer_Values;
   package JSON_Render renames Worldline.Producer_Render;
   package B renames Worldline.Producer_Bytes;
   package L renames Worldline.Runner_Lifecycle_Bytes;
   package P renames Evaluation_Pending;
   use SPARK.Big_Integers;
   use type V.Value_Kind;
   use type E.Value_Kind;
   use type E.Count;
   use type E.Q.Byte;
   use type P.Count;
   use type Decimal_Binary64.Bits;
   use type W.Byte;

   function JSON_Bytes (Text : String) return P.Bytes is
      Result : P.Bytes (1 .. P.Count (Text'Length)) := [others => 0];
   begin
      for I in Text'Range loop
         Result (P.Count (I - Text'First + 1)) := P.Byte (Character'Pos (Text (I)));
      end loop;
      return Result;
   end JSON_Bytes;
   function Raw_Bytes (Text : String; Item : V.Node) return B.Decoded is
   begin
      if Item.Form /= V.Object_Value or else
        not V.Is_Text (Text, V.Field (Text, Item, "encoding"), "base64") or else
        V.Field (Text, Item, "payload").Form /= V.String_Value then
         return (0, False, "");
      end if;
      return B.Base64 (V.Text (Text, V.Field (Text, Item, "payload")));
   end Raw_Bytes;

   function Character_At (Text : String; Offset : Natural) return Character
     with Pre => Offset < Text'Length
   is
   begin
      pragma Assert (Offset <= Text'Last - Text'First);
      return Text (Text'First + Offset);
   end Character_At;

   function Text_Slice (Text : String; First, After : Natural) return String
     with Pre => First <= After and then After <= Text'Length,
          Post => Text_Slice'Result'Length = After - First
   is
   begin
      if First = After then return ""; end if;
      return Text (Text'First + First .. Text'First + (After - 1));
   end Text_Slice;

   --  Decode exactly one Unicode scalar (surrogates remain representable in
   --  decoded JSON text but are not admitted by UTF8 strict/replace byte reads).
   function Code (Text : String; Offset : Natural; Width : Positive) return Natural
     with Pre => Width <= 4
            and then Offset < Text'Length
            and then Width <= Text'Length - Offset
   is
      Lead : constant Natural := Character'Pos (Text (Text'First + Offset));
   begin
      case Width is
         when 1 =>
            return Lead;
         when 2 =>
            return (Lead mod 32) * 64
              + Character'Pos (Text (Text'First + Offset + 1)) mod 64;
         when 3 =>
            return ((Lead mod 16) * 64
              + Character'Pos (Text (Text'First + Offset + 1)) mod 64) * 64
              + Character'Pos (Text (Text'First + Offset + 2)) mod 64;
         when others =>
            return (((Lead mod 8) * 64
              + Character'Pos (Text (Text'First + Offset + 1)) mod 64) * 64
              + Character'Pos (Text (Text'First + Offset + 2)) mod 64) * 64
              + Character'Pos (Text (Text'First + Offset + 3)) mod 64;
      end case;
   end Code;
   function White (C : Natural) return Boolean is
     (C in 9 .. 13 | 16#20# | 16#85# | 16#A0# | 16#1680# |
       16#2000# .. 16#200A# | 16#2028# .. 16#2029# | 16#202F# |
       16#205F# | 16#3000#);
   function Digit (C : Natural) return Integer
     with Post => Digit'Result in -1 .. 9
   is
      type Starts_Array is array (Positive range <>) of Natural;
      Starts : constant Starts_Array := (16#30#, 16#660#, 16#6F0#, 16#7C0#, 16#966#, 16#9E6#, 16#A66#, 16#AE6#, 16#B66#, 16#BE6#, 16#C66#, 16#CE6#, 16#D66#, 16#DE6#, 16#E50#, 16#ED0#, 16#F20#, 16#1040#, 16#1090#, 16#17E0#, 16#1810#, 16#1946#, 16#19D0#, 16#1A80#, 16#1A90#, 16#1B50#, 16#1BB0#, 16#1C40#, 16#1C50#, 16#A620#, 16#A8D0#, 16#A900#, 16#A9D0#, 16#A9F0#, 16#AA50#, 16#ABF0#, 16#FF10#, 16#104A0#, 16#10D30#, 16#10D40#, 16#11066#, 16#110F0#, 16#11136#, 16#111D0#, 16#112F0#, 16#11450#, 16#114D0#, 16#11650#, 16#116C0#, 16#116D0#, 16#116DA#, 16#11730#, 16#118E0#, 16#11950#, 16#11BF0#, 16#11C50#, 16#11D50#, 16#11DA0#, 16#11F50#, 16#16130#, 16#16A60#, 16#16AC0#, 16#16B50#, 16#16D70#, 16#1CCF0#, 16#1D7CE#, 16#1D7D8#, 16#1D7E2#, 16#1D7EC#, 16#1D7F6#, 16#1E140#, 16#1E2F0#, 16#1E4F0#, 16#1E5F1#, 16#1E950#, 16#1FBF0#);
   begin
      for First of Starts loop
         if C >= First and then C - First < 10 then return Integer (C - First); end if;
      end loop;
      return -1;
   end Digit;
   type Integer_Result is record
      Valid : Boolean := False;
      Value : Big_Integer := To_Big_Integer (0);
   end record;
   --  Python int(string), including Unicode decimal digits, sign, surrounding
   --  whitespace and a single underscore between digits; no machine-int cap.
   function String_Integer (Text : String; Digits_Only : Boolean := False)
      return Integer_Result
   is
      Offset : Natural := 0;
      Width : Natural;
      C : Natural;
      Seen, Negative, Need_Digit, Trailing : Boolean := False;
      Result : Integer_Result;
   begin
      while Offset < Text'Length loop
         pragma Loop_Variant (Increases => Offset);
         Width := V.UTF8_Width (Text, Offset);
         if Width = 0 then return Result; end if;
         C := Code (Text, Offset, Width);
         if Digit (C) >= 0 and then not Trailing then
            Result.Value := Result.Value * To_Big_Integer (10) + To_Big_Integer (Digit (C));
            Seen := True; Need_Digit := False;
         elsif not Digits_Only and then White (C) and then not Need_Digit then
            if Seen then Trailing := True; end if;
         elsif not Digits_Only and then not Seen and then not Need_Digit and then
           C in Character'Pos ('+') | Character'Pos ('-') then
            Negative := C = Character'Pos ('-'); Need_Digit := True;
         elsif not Digits_Only and then C = Character'Pos ('_') and then Seen and then
           not Need_Digit and then not Trailing then
            Need_Digit := True;
         else
            return (False, To_Big_Integer (0));
         end if;
         pragma Assert (Width >= 1 and then Width <= Text'Length - Offset);
         Offset := Offset + Width;
      end loop;
      Result.Valid := Seen and then not Need_Digit;
      if Negative then Result.Value := -Result.Value; end if;
      return Result;
   end String_Integer;
   function Integer_Value (Text : String; Item : V.Node) return Integer_Result is
   begin
      if Item.Form = V.String_Value then return String_Integer (V.Text (Text, Item));
      elsif Item.Form = V.Integer_Value then return String_Integer (V.Decimal (Text, Item));
      elsif Item.Form = V.Boolean_Value then
         return (True, To_Big_Integer (if V.Is_True (Text, Item) then 1 else 0));
      elsif Item.Form = V.Number_Value then
         declare
            Token : constant P.Bytes := JSON_Bytes (V.Slice (Text, Item));
            Number : constant Exact_Decimal.Number := Exact_Decimal.Parse (Token, (1, Token'Length), 0);
            Converted : constant Decimal_Binary64.Conversion := Decimal_Binary64.Convert (Number);
         begin
            if not Converted.Valid then return (False, To_Big_Integer (0)); end if;
            declare
               Ratio : constant Decimal_Binary64.Rational :=
                 Decimal_Binary64.Value (Decimal_Binary64.Magnitude (Converted.Encoding));
               Value : constant Big_Integer := Ratio.Numerator / Ratio.Denominator;
            begin
               return (True, (if Converted.Encoding >= Decimal_Binary64.Sign_Bit then -Value else Value));
            end;
         end;
      end if;
      return (False, To_Big_Integer (0));
   end Integer_Value;
   function Image (Value : Big_Integer) return String is
      Text : constant String := To_String (Value);
   begin
      return (if Text'Length > 0 and then Character_At (Text, 0) = ' '
              then Text_Slice (Text, 1, Text'Length) else Text);
   end Image;

   function Image_Matches
     (Text, Prefix, Suffix : String; Value : Big_Integer) return Boolean is
     (Text'Length >= Prefix'Length
      and then Suffix'Length <= Text'Length - Prefix'Length
      and then Text_Slice (Text, 0, Prefix'Length) = Prefix
      and then Text_Slice (Text, Text'Length - Suffix'Length, Text'Length) = Suffix
      and then Text_Slice (Text, Prefix'Length, Text'Length - Suffix'Length) = Image (Value));
   function Str (Text : String; Item : V.Node; Default : String := "None") return String is
     (if Item.Form = V.Missing then Default else V.Python_String (V.Slice (Text, Item)));
   function Bit (Value : Boolean) return String is (if Value then "true" else "false");
   function Null_Or_Missing (Item : V.Node) return Boolean is
     (Item.Form in V.Missing | V.Null_Value);
   function Get (Text : String; Item : V.Node) return String is
     (if Item.Form = V.Missing then "null" else V.Slice (Text, Item));

   function UTF8 (Bytes : String; Replace_Errors : Boolean) return B.Decoded is
      procedure Step (Position : Natural; Advance, Width : out Natural)
        with Pre => Position < Bytes'Length,
             Post => Advance >= 1 and then Advance <= 4 and then Width <= 4
      is
         Lead, Next, Wanted : Natural;
      begin
         Width := V.UTF8_Width (Bytes, Position);
         if Width > 0 and then Code (Bytes, Position, Width) not in 16#D800# .. 16#DFFF# then
            Advance := Width; return;
         end if;
         Width := 0; Advance := 1;
         Lead := Character'Pos (Character_At (Bytes, Position));
         Wanted := (if Lead in 16#C2# .. 16#DF# then 2 elsif Lead in 16#E0# .. 16#EF# then 3
                    elsif Lead in 16#F0# .. 16#F4# then 4 else 1);
         while Advance < Wanted and then Advance < Bytes'Length - Position loop
            pragma Loop_Invariant (Advance >= 1 and then Advance <= 4);
            pragma Loop_Variant (Increases => Advance);
            Next := Character'Pos (Character_At (Bytes, Position + Advance));
            exit when Next not in 16#80# .. 16#BF# or else
              (Advance = 1 and then ((Lead = 16#E0# and then Next < 16#A0#) or else
               (Lead = 16#ED# and then Next >= 16#A0#) or else
               (Lead = 16#F0# and then Next < 16#90#) or else
               (Lead = 16#F4# and then Next >= 16#90#)));
            Advance := Advance + 1;
         end loop;
      end Step;
      Position, Width, Advance, Length : Natural := 0;
      function Add_For (W : Natural) return Natural is (if W = 0 then 3 else W);
   begin
      while Position < Bytes'Length loop
         pragma Loop_Invariant (Position <= Bytes'Length);
         pragma Loop_Variant (Increases => Position);
         Step (Position, Advance, Width);
         if Width = 0 and then not Replace_Errors then return (0, False, ""); end if;
         if Advance = 0 or else Advance > Bytes'Length - Position or else
           Add_For (Width) > Natural'Last - Length then
            return (0, False, "");
         end if;
         Length := Length + Add_For (Width);
         Position := Position + Advance;
      end loop;
      --  The same immutable source has already passed validation and sizing.
      --  A disagreement while writing is an invariant failure, not absence.
      return Result : B.Decoded (Length) with Relaxed_Initialization do
         declare
            Used : Natural := 0;
         begin
            Result.Valid := True;
            Position := 0;
            while Position < Bytes'Length loop
               pragma Loop_Invariant (Position <= Bytes'Length);
               pragma Loop_Invariant (Used <= Result.Length);
               pragma Loop_Invariant (Result.Valid'Initialized);
               pragma Loop_Invariant
                 (if Used > 0 then Result.Data (1 .. Used)'Initialized);
               pragma Loop_Variant (Increases => Position);
               Step (Position, Advance, Width);
               if Advance = 0 or else Advance > Bytes'Length - Position or else
                 (Width = 0 and then not Replace_Errors)
               then
                  raise Program_Error with "UTF8 decode extent mismatch";
               end if;
               if Width > 0 then
                  if Width > Result.Length - Used or else Width > Bytes'Length - Position then
                     raise Program_Error with "UTF8 decode extent mismatch";
                  end if;
                  Result.Data (Used + 1 .. Used + Width) :=
                    Text_Slice (Bytes, Position, Position + Width);
                  Used := Used + Width;
               else
                  if 3 > Result.Length - Used then
                     raise Program_Error with "UTF8 decode extent mismatch";
                  end if;
                  Result.Data (Used + 1 .. Used + 3) :=
                    Character'Val (16#EF#) & Character'Val (16#BF#) & Character'Val (16#BD#);
                  Used := Used + 3;
               end if;
               Position := Position + Advance;
            end loop;
            if Used /= Result.Length then
               raise Program_Error with "UTF8 decode extent mismatch";
            end if;
            pragma Assert (Result'Initialized);
         end;
      end return;
   end UTF8;
   function Strip (Text : String) return String is
      First, Last, Position, Width : Natural := 0;
      Start_Found : Boolean := False;
   begin
      while Position < Text'Length loop
         pragma Loop_Invariant (Position <= Text'Length);
         pragma Loop_Invariant
           (if Start_Found then First < Last and then Last <= Position
            else Last = 0 and then First = 0);
         pragma Loop_Variant (Increases => Position);
         Width := V.UTF8_Width (Text, Position);
         if Width = 0 then return ""; end if;
         if not White (Code (Text, Position, Width)) and then
           Code (Text, Position, Width) not in 28 .. 31 then
            if not Start_Found then First := Position; Start_Found := True; end if;
            pragma Assert (Width >= 1 and then Width <= Text'Length - Position);
            Last := Position + Width;
         end if;
         pragma Assert (Width >= 1 and then Width <= Text'Length - Position);
         Position := Position + Width;
      end loop;
      if not Start_Found then return ""; end if;
      return Text_Slice (Text, First, Last);
   end Strip;
   function Prefix (Text : String; Limit : Natural) return String is
      Position, Width, Seen : Natural := 0;
   begin
      while Position < Text'Length and then Seen < Limit loop
         pragma Loop_Invariant (Position <= Text'Length);
         pragma Loop_Variant (Increases => Position);
         Width := V.UTF8_Width (Text, Position);
         if Width = 0 then return ""; end if;
         pragma Assert (Width >= 1 and then Width <= Text'Length - Position);
         Position := Position + Width;
         Seen := Seen + 1;
      end loop;
      if Position = 0 then return ""; end if;
      return Text_Slice (Text, 0, Position);
   end Prefix;
   function Line_End (Text : String; First : Natural) return Natural
     with Post => Line_End'Result >= First
            and then (if First <= Text'Length then Line_End'Result <= Text'Length)
   is
      Position : Natural := First;
      Width : Natural;
   begin
      while Position < Text'Length loop
         pragma Loop_Invariant (Position >= First and then Position <= Text'Length);
         pragma Loop_Variant (Increases => Position);
         Width := V.UTF8_Width (Text, Position);
         exit when Width = 0 or else Code (Text, Position, Width) in
           10 .. 13 | 28 .. 30 | 16#85# | 16#2028# .. 16#2029#;
         pragma Assert (Width >= 1 and then Width <= Text'Length - Position);
         Position := Position + Width;
      end loop;
      return Position;
   end Line_End;
   function Next_Line (Text : String; Last : Natural) return Natural
     with Post => Next_Line'Result <= Text'Length
            and then (if Last < Text'Length then Next_Line'Result > Last
                      else Next_Line'Result = Text'Length)
   is
      Width : Natural;
   begin
      if Last >= Text'Length then return Text'Length; end if;
      Width := V.UTF8_Width (Text, Last);
      if Width = 0 then return Text'Length; end if;
      if Character_At (Text, Last) = Character'Val (13) and then Last + 1 < Text'Length and then
        Character_At (Text, Last + 1) = Character'Val (10) then return Last + 2; end if;
      pragma Assert (Width <= Text'Length - Last);
      return Last + Width;
   end Next_Line;

   function Is_Digits (Text : String) return Boolean is
      Position, Width : Natural := 0;
      C : Natural;
      type Interval is record First, Last : Natural; end record;
      type Interval_Array is array (Positive range <>) of Interval;
      Ranges : constant Interval_Array := ((16#30#, 16#39#), (16#B2#, 16#B3#), (16#B9#, 16#B9#), (16#660#, 16#669#), (16#6F0#, 16#6F9#), (16#7C0#, 16#7C9#), (16#966#, 16#96F#), (16#9E6#, 16#9EF#), (16#A66#, 16#A6F#), (16#AE6#, 16#AEF#), (16#B66#, 16#B6F#), (16#BE6#, 16#BEF#), (16#C66#, 16#C6F#), (16#CE6#, 16#CEF#), (16#D66#, 16#D6F#), (16#DE6#, 16#DEF#), (16#E50#, 16#E59#), (16#ED0#, 16#ED9#), (16#F20#, 16#F29#), (16#1040#, 16#1049#), (16#1090#, 16#1099#), (16#1369#, 16#1371#), (16#17E0#, 16#17E9#), (16#1810#, 16#1819#), (16#1946#, 16#194F#), (16#19D0#, 16#19DA#), (16#1A80#, 16#1A89#), (16#1A90#, 16#1A99#), (16#1B50#, 16#1B59#), (16#1BB0#, 16#1BB9#), (16#1C40#, 16#1C49#), (16#1C50#, 16#1C59#), (16#2070#, 16#2070#), (16#2074#, 16#2079#), (16#2080#, 16#2089#), (16#2460#, 16#2468#), (16#2474#, 16#247C#), (16#2488#, 16#2490#), (16#24EA#, 16#24EA#), (16#24F5#, 16#24FD#), (16#24FF#, 16#24FF#), (16#2776#, 16#277E#), (16#2780#, 16#2788#), (16#278A#, 16#2792#), (16#A620#, 16#A629#), (16#A8D0#, 16#A8D9#), (16#A900#, 16#A909#), (16#A9D0#, 16#A9D9#), (16#A9F0#, 16#A9F9#), (16#AA50#, 16#AA59#), (16#ABF0#, 16#ABF9#), (16#FF10#, 16#FF19#), (16#104A0#, 16#104A9#), (16#10A40#, 16#10A43#), (16#10D30#, 16#10D39#), (16#10D40#, 16#10D49#), (16#10E60#, 16#10E68#), (16#11052#, 16#1105A#), (16#11066#, 16#1106F#), (16#110F0#, 16#110F9#), (16#11136#, 16#1113F#), (16#111D0#, 16#111D9#), (16#112F0#, 16#112F9#), (16#11450#, 16#11459#), (16#114D0#, 16#114D9#), (16#11650#, 16#11659#), (16#116C0#, 16#116C9#), (16#116D0#, 16#116E3#), (16#11730#, 16#11739#), (16#118E0#, 16#118E9#), (16#11950#, 16#11959#), (16#11BF0#, 16#11BF9#), (16#11C50#, 16#11C59#), (16#11D50#, 16#11D59#), (16#11DA0#, 16#11DA9#), (16#11F50#, 16#11F59#), (16#16130#, 16#16139#), (16#16A60#, 16#16A69#), (16#16AC0#, 16#16AC9#), (16#16B50#, 16#16B59#), (16#16D70#, 16#16D79#), (16#1CCF0#, 16#1CCF9#), (16#1D7CE#, 16#1D7FF#), (16#1E140#, 16#1E149#), (16#1E2F0#, 16#1E2F9#), (16#1E4F0#, 16#1E4F9#), (16#1E5F1#, 16#1E5FA#), (16#1E950#, 16#1E959#), (16#1F100#, 16#1F10A#), (16#1FBF0#, 16#1FBF9#));
   begin
      if Text'Length = 0 then return False; end if;
      while Position < Text'Length loop
         pragma Loop_Variant (Increases => Position);
         Width := V.UTF8_Width (Text, Position);
         if Width = 0 then return False; end if;
         C := Code (Text, Position, Width);
         if not (for some R of Ranges => C >= R.First and then C <= R.Last) then
            return False;
         end if;
         pragma Assert (Width >= 1 and then Width <= Text'Length - Position);
         Position := Position + Width;
      end loop;
      return True;
   end Is_Digits;
   function Supervisor_Decide
     (Observed, Acquisition_Kind, Unit, Since_Us, Launcher_Exit,
      Supervisor_Record : String; Stopped : Boolean;
      Reader_UID : String := "") return Supervisor_Facts
   is
      Rows : constant V.Node := V.Parse (Observed);
      Super : constant V.Node := V.Parse (Supervisor_Record);
      Since : constant Integer_Result := Integer_Value (Since_Us, V.Parse (Since_Us));
      function O (Item : V.Node; Name : String) return V.Node is (V.Field (Observed, Item, Name));
      function S (Name : String) return V.Node is (V.Field (Supervisor_Record, Super, Name));
      function Row (Index : Positive) return V.Node is (V.Element (Observed, Rows, Index));
      function Clean (Item : V.Node) return Boolean is
        (V.Is_True (Observed, O (Item, "processReturnObserved")) and then
         V.Is_True (Observed, O (Item, "processWaitReturnObserved")) and then
         V.Is_True (Observed, O (Item, "stdoutReachedEof")) and then
         V.Is_True (Observed, O (Item, "stderrReachedEof")) and then
         O (Item, "exception").Form = V.Null_Value and then
         V.Equal (Observed, O (Item, "returncode"), Observed, O (Item, "processWaitReturncode")));
      function Accepted (Line : String; Journal_Row : V.Node; Reader : Big_Integer) return Boolean is
         function J (Name : String) return V.Node is (V.Field (Line, Journal_Row, Name));
         Stamp : constant Integer_Result :=
           (if J ("__REALTIME_TIMESTAMP").Form = V.Missing then (True, To_Big_Integer (0))
            else Integer_Value (Line, J ("__REALTIME_TIMESTAMP")));
      begin
         return Journal_Row.Form = V.Object_Value and then
           J ("_SYSTEMD_UNIT").Form = V.String_Value and then
           Image_Matches (V.Text (Line, J ("_SYSTEMD_UNIT")), "user@", ".service", Reader) and then
           V.Is_Text (Line, J ("_COMM"), "systemd") and then
           (Null_Or_Missing (J ("USER_UNIT")) or else V.Is_Text (Line, J ("USER_UNIT"), Unit) or else
            Null_Or_Missing (J ("UNIT")) or else V.Is_Text (Line, J ("UNIT"), Unit)) and then
           Stamp.Valid and then Stamp.Value >= Since.Value;
      end Accepted;
      function Event (Line : String; Journal_Row : V.Node; Stamp : Big_Integer) return String is
         function J (Name : String) return V.Node is (V.Field (Line, Journal_Row, Name));
      begin
         return "{""messageId"":" & Get (Line, J ("MESSAGE_ID")) &
           ",""message"":" & V.Quote (Prefix (Str (Line, J ("MESSAGE"), ""), 200)) &
           ",""jobType"":" & Get (Line, J ("JOB_TYPE")) & ",""jobResult"":" & Get (Line, J ("JOB_RESULT")) &
           ",""exitCode"":" & Get (Line, J ("EXIT_CODE")) & ",""exitStatus"":" & Get (Line, J ("EXIT_STATUS")) &
           ",""managerPid"":" & Get (Line, J ("_PID")) & ",""realtimeUs"":" & Image (Stamp) & "}";
      end Event;
      STARTING : constant String := "7d4958e842da4a758f6c1cdc7b36dcc5";
      STARTED_ID : constant String := "39f53479d3a045ac8e11786248231fbf";
      STOPPING : constant String := "de5b426a63be47a7b6ac3eaac82e2f6f";
      STOPPED_ID : constant String := "9d1aaa27d60140bd96365438aad20286";
      EXIT_ID : constant String := "98e322203f7a4ed290d09fe03c09fe15";
      FAILURE_ID : constant String := "d9b373ed55a64feb8242e02dbe79a49c";
      Poll_Count, Final_Poll, Ordinal : Natural := 0;
      Readable : Boolean := True;
      Break_Reached, Started, Started_Entry, Launched, Manager_Stopped, Failure, Exit_Seen : Boolean := False;
      Exit_Ordinal : Natural := 0;
      Reread : V.Node := V.No_Node;
      Result : Supervisor_Facts;
      Events : constant V.Node := S ("events");
      Wait_Zero : constant Boolean := Worldline.Raw_JSON.Python_JSON_Equal (Launcher_Exit, "0");
      function Query_Valid (Item : V.Node) return Boolean is
         Args : constant V.Node := O (Item, "argv");
         Seconds : Big_Integer := Since.Value / To_Big_Integer (1_000_000);
      begin
         if Since.Value < To_Big_Integer (0) and then Since.Value rem To_Big_Integer (1_000_000) /= To_Big_Integer (0) then
            Seconds := Seconds - To_Big_Integer (1);
         end if;
         Seconds := Seconds - To_Big_Integer (2);
         if Seconds < To_Big_Integer (0) then Seconds := To_Big_Integer (0); end if;
         return Args.Form = V.Array_Value and then V.Count (Observed, Args) = 8 and then
           V.Nonempty_Text (Observed, V.Element (Observed, Args, 1)) and then
           V.Is_Text (Observed, V.Element (Observed, Args, 2), "--user") and then
           V.Is_Text (Observed, V.Element (Observed, Args, 3), "-u") and then
           V.Is_Text (Observed, V.Element (Observed, Args, 4), Unit) and then
           V.Is_Text (Observed, V.Element (Observed, Args, 5), "-o") and then
           V.Is_Text (Observed, V.Element (Observed, Args, 6), "json") and then
           V.Is_Text (Observed, V.Element (Observed, Args, 7), "--no-pager") and then
           V.Element (Observed, Args, 8).Form = V.String_Value and then
           Image_Matches (V.Text (Observed, V.Element (Observed, Args, 8)), "--since=@", "", Seconds);
      end Query_Valid;
      procedure Parse_Poll (Index : Positive; Match_Events : Boolean; Valid : out Boolean) is
         Item : constant V.Node := O (Row (Index), "observation");
         Reader : constant Integer_Result :=
           (if O (Item, "readerUid").Form /= V.Missing then Integer_Value (Observed, O (Item, "readerUid"))
            else Integer_Value (Reader_UID, V.Parse (Reader_UID)));
         Raw : constant B.Decoded := Raw_Bytes (Observed, O (Item, "stdout"));
         Text : constant B.Decoded := UTF8 (Raw.Data, True);
         First, Last, Count : Natural := 0;
         Ended : Boolean := False;
      begin
         Valid := False;
         Started := False; Started_Entry := False; Launched := False;
         Manager_Stopped := False; Failure := False; Exit_Seen := False;
         if V.Is_Text (Observed, O (Item, "site"), "journal-tool-unavailable") then
            if O (Item, "journalctl").Form /= V.Null_Value then return; end if;
            if Match_Events and then V.Count (Supervisor_Record, Events) /= 0 then return; end if;
            Readable := False; Break_Reached := True; Valid := True; return;
         end if;
         if not Clean (Item) or else not Query_Valid (Item) then return; end if;
         if not Worldline.Raw_JSON.Python_JSON_Equal (V.Slice (Observed, O (Item, "processWaitReturncode")), "0") then
            if Match_Events and then V.Count (Supervisor_Record, Events) /= 0 then return; end if;
            Readable := False; Break_Reached := True; Valid := True; return;
         end if;
         if not Reader.Valid or else
           (if O (Item, "readerUid").Form /= V.Missing then O (Item, "readerUid").Form /= V.Integer_Value
            else V.Parse (Reader_UID).Form /= V.Integer_Value) or else
           not Raw.Valid or else not Text.Valid then return; end if;
         while First < Text.Length loop
            pragma Loop_Invariant (First <= Text.Length);
            pragma Loop_Variant (Increases => First);
            Last := Line_End (Text.Data, First);
            pragma Assert (First < Text.Length and then Last <= Text.Length and then Last >= First);
            declare
               Line : constant String := Text.Data (First + 1 .. Last);
               Journal_Row : constant V.Node := V.Parse (Line);
               function J (Name : String) return V.Node is (V.Field (Line, Journal_Row, Name));
               ID : constant String := V.Text (Line, J ("MESSAGE_ID"));
            begin
               if Journal_Row.Form = V.Object_Value and then
                 J ("_SYSTEMD_UNIT").Form = V.String_Value and then
                 Image_Matches (V.Text (Line, J ("_SYSTEMD_UNIT")), "user@", ".service", Reader.Value) and then
                 V.Is_Text (Line, J ("_COMM"), "systemd") and then
                 (Null_Or_Missing (J ("USER_UNIT")) or else V.Is_Text (Line, J ("USER_UNIT"), Unit) or else
                  Null_Or_Missing (J ("UNIT")) or else V.Is_Text (Line, J ("UNIT"), Unit)) and then
                 J ("__REALTIME_TIMESTAMP").Form = V.Number_Value and then
                 V.Number_Image (Line, J ("__REALTIME_TIMESTAMP")) in "inf" | "-inf" then
                  return;
               end if;
               if Accepted (Line, Journal_Row, Reader.Value) then
                  if J ("MESSAGE_ID").Form in V.Array_Value | V.Object_Value then return; end if;
                  if Count = Natural'Last then return; end if;
                  Count := Count + 1;
                  if Match_Events then
                     declare
                        Stamp : constant Integer_Result :=
                          (if J ("__REALTIME_TIMESTAMP").Form = V.Missing then (True, To_Big_Integer (0))
                           else Integer_Value (Line, J ("__REALTIME_TIMESTAMP")));
                     begin
                        if not Worldline.Raw_JSON.Python_JSON_Equal (Event (Line, Journal_Row, Stamp.Value),
                          V.Slice (Supervisor_Record, V.Element (Supervisor_Record, Events, Count))) then return; end if;
                     end;
                  end if;
                  if ID = STARTED_ID then Started_Entry := True; end if;
                  if ID = EXIT_ID then
                     if not Exit_Seen then Exit_Ordinal := Count; end if;
                     Exit_Seen := True;
                  end if;
                  Failure := Failure or else ID = FAILURE_ID;
                  Launched := Launched or else ID = STARTING;
                  Manager_Stopped := Manager_Stopped or else ID in STOPPING | STOPPED_ID;
                  Ended := Ended or else ID in EXIT_ID | FAILURE_ID | STOPPED_ID;
               end if;
            end;
            declare
               Next : constant Natural := Next_Line (Text.Data, Last);
            begin
               pragma Assert (Next > First and then Next <= Text.Length);
               First := Next;
            end;
         end loop;
         Started := Started_Entry or else Exit_Seen;
         Break_Reached := (Started and then (Ended or else Wait_Zero or else Stopped)) or else not Readable;
         if Match_Events and then Count /= V.Count (Supervisor_Record, Events) then return; end if;
         Valid := True;
      end Parse_Poll;
   begin
      if Rows.Form /= V.Array_Value or else Super.Form /= V.Object_Value or else
        not Since.Valid or else not Worldline.Manager_Resource_Lifecycle.Unit_Valid (Unit) or else
        Events.Form /= V.Array_Value then return Result; end if;
      for I in 1 .. V.Count (Observed, Rows) loop
         if V.Is_Text (Observed, O (Row (I), "kind"), Acquisition_Kind) then
            declare
               Item : constant V.Node := O (Row (I), "observation");
               Actual_Ordinal : constant Integer_Result := Integer_Value (Observed, O (Row (I), "occurrence"));
               Valid : Boolean;
            begin
               if not Actual_Ordinal.Valid or else Actual_Ordinal.Value /= To_Big_Integer (Ordinal) or else
                 not V.Is_Text (Observed, O (Item, "unit"), Unit) then return Result; end if;
               Ordinal := Ordinal + 1;
               if V.Is_Text (Observed, O (Item, "site"), "journal-poll") or else
                 V.Is_Text (Observed, O (Item, "site"), "journal-tool-unavailable") then
                  if Break_Reached or else Reread.Form /= V.Missing or else
                    not Worldline.Raw_JSON.Python_JSON_Equal
                      (V.Slice (Observed, O (Item, "sinceUs")), Since_Us) then return Result; end if;
                  Parse_Poll (I, False, Valid);
                  if not Valid then return Result; end if;
                  Final_Poll := I; Poll_Count := Poll_Count + 1;
               elsif V.Is_Text (Observed, O (Item, "site"), "launcher-stderr-reread") then
                  if Reread.Form /= V.Missing then return Result; end if;
                  Reread := Item;
               else return Result;
               end if;
            end;
         end if;
      end loop;
      if Poll_Count = 0 then return Result; end if;
      declare Valid : Boolean; begin
         Parse_Poll (Final_Poll, True, Valid);
         if not Valid then return Result; end if;
      end;
      Result.Kind := (if Started then 1 else 3);
      Result.Stopped := Manager_Stopped;
      declare
         Kind : constant String := (if Started then "SUPERVISED" elsif not Readable then "INDETERMINATE"
           elsif not Wait_Zero and then not Launched then "LAUNCH_FAILED" else "INDETERMINATE");
         First_Exit : constant V.Node :=
           (if Exit_Seen then V.Element (Supervisor_Record, Events, Exit_Ordinal) else V.No_Node);
         Raw_Status : constant V.Node := V.Field (Supervisor_Record, First_Exit, "exitStatus");
         Status_Text : constant String := Str (Supervisor_Record, Raw_Status);
         Parsed_Status : constant Integer_Result := String_Integer (Status_Text, True);
         Actual_Status : constant String :=
           (if not Exit_Seen or else Null_Or_Missing (Raw_Status) then "null"
            elsif Is_Digits (Status_Text) and then Parsed_Status.Valid then Image (Parsed_Status.Value)
            else Get (Supervisor_Record, Raw_Status));
         Result_Value : constant String :=
           (if Manager_Stopped then "stopped" elsif Failure or else (Exit_Seen and then Status_Text not in "0" | "None")
            then "failure" elsif Started and then Wait_Zero then "success" else "");
      begin
         if Is_Digits (Status_Text) and then not Parsed_Status.Valid then return Result; end if;
         if not V.Is_Text (Supervisor_Record, S ("kind"), Kind) or else
           not V.Is_Text (Supervisor_Record, S ("unit"), Unit) or else
           not V.Is_Text (Supervisor_Record, S ("source"), (if Readable then "journal" else "journal-unavailable")) or else
           not V.Equal (Supervisor_Record, S ("launcherExit"), Launcher_Exit, V.Parse (Launcher_Exit)) or else
           not Worldline.Raw_JSON.Python_JSON_Equal (V.Slice (Supervisor_Record, S ("started")), Bit (Started)) or else
           not Worldline.Raw_JSON.Python_JSON_Equal (V.Slice (Supervisor_Record, S ("stoppedByManager")), Bit (Manager_Stopped)) or else
           not Worldline.Raw_JSON.Python_JSON_Equal (V.Slice (Supervisor_Record, S ("supervisionEvidence")),
             (if Started_Entry then V.Quote ("started-entry") elsif Exit_Seen then V.Quote ("process-exit-entry") else "null")) or else
           not Worldline.Raw_JSON.Python_JSON_Equal (V.Slice (Supervisor_Record, S ("exitCode")),
             Get (Supervisor_Record, V.Field (Supervisor_Record, First_Exit, "exitCode"))) or else
           not Worldline.Raw_JSON.Python_JSON_Equal (V.Slice (Supervisor_Record, S ("exitStatus")), Actual_Status) or else
           not Worldline.Raw_JSON.Python_JSON_Equal (V.Slice (Supervisor_Record, S ("result")),
             (if Result_Value = "" then "null" else V.Quote (Result_Value))) or else
           not Worldline.Raw_JSON.Python_JSON_Equal (V.Slice (Supervisor_Record, S ("windowMilliseconds")), "10000") then return Result; end if;
         if Started and then Reread.Form /= V.Missing then return Result; end if;
         if Reread.Form = V.Missing then
            if not V.Is_Text (Supervisor_Record, S ("launcherStderr"), "") then return Result; end if;
         elsif V.Is_False (Observed, O (Reread, "readReturned")) then
            if O (Reread, "exception").Form /= V.Object_Value or else
              not V.Is_Text (Supervisor_Record, S ("launcherStderr"), "") then return Result; end if;
         elsif V.Is_True (Observed, O (Reread, "readReturned")) and then
           O (Reread, "exception").Form = V.Null_Value then
            declare
               Bytes : constant B.Decoded := Raw_Bytes (Observed, O (Reread, "stderr"));
               Text : constant B.Decoded := UTF8 (Bytes.Data, True);
            begin
               if not Bytes.Valid or else not Text.Valid or else
                 not V.Is_Text (Supervisor_Record, S ("launcherStderr"), Prefix (Text.Data, 400)) then return Result; end if;
            end;
         else return Result;
         end if;
      end;
      Result.Valid := True;
      return Result;
   end Supervisor_Decide;

   function Decide
     (Expected, Observed, Result_Record : String;
      Data : E.Bytes; Capture : E.Span) return Facts
   is
      Start : constant V.Node := V.Parse (Expected);
      Rows : constant V.Node := V.Parse (Observed);
      Returned : constant V.Node := V.Parse (Result_Record);
      Result : constant V.Node :=
        (if V.Field (Result_Record, Returned, "rawRunnerResult").Form = V.Object_Value
         then V.Field (Result_Record, Returned, "rawRunnerResult") else Returned);
      function O (Item : V.Node; Name : String) return V.Node is (V.Field (Observed, Item, Name));
      function R (Item : V.Node; Name : String) return V.Node is (V.Field (Result_Record, Item, Name));
      function X (Name : String) return V.Node is (V.Field (Expected, Start, Name));
      function F (Item : E.Span; Name : String) return E.Span is (L.Field (Data, Item, Name));
      function T (Item : E.Span; Value : String) return Boolean is (L.Text_Is (Data, Item, Value));
      function Form (Item : E.Span) return E.Value_Kind is (E.Decode (Data, Item, E.Finalization).Form);
      function Row (Index : Positive) return V.Node is (V.Element (Observed, Rows, Index));
      function Kind (Index : Positive; Name : String) return Boolean is
        (V.Is_Text (Observed, O (Row (Index), "kind"), Name));
      function Acquisition (Name : String) return V.Node is
         Found : V.Node := V.No_Node;
      begin
         for I in 1 .. V.Count (Observed, Rows) loop
            if Kind (I, Name) then
               if Found.Form /= V.Missing then return V.No_Node; end if;
               Found := O (Row (I), "observation");
            end if;
         end loop;
         return Found;
      end Acquisition;
      function Protocol_Source (Name : String) return V.Node is
         Found : V.Node := V.No_Node;
      begin
         for I in 1 .. V.Count (Observed, Rows) loop
            if Kind (I, "agent-terminal-protocol-source") then
               declare
                  Item : constant V.Node := O (Row (I), "observation");
               begin
                  if V.Is_Text (Observed, O (Item, "stage"), Name) then
                     if Found.Form /= V.Missing then return V.No_Node; end if;
                     Found := Item;
                  end if;
               end;
            end if;
         end loop;
         return Found;
      end Protocol_Source;
      Wait : constant V.Node := Acquisition ("agent-launcher-wait");
      Membership : constant V.Node := Acquisition ("agent-stop-membership-observation");
      Manager : constant V.Node := Acquisition ("manager-return");
      Source_Objects : constant V.Node := Acquisition ("agent-terminal-source-objects");
      Created : constant V.Node := Acquisition ("agent-job-created");
      Association : constant V.Node := Acquisition ("agent-job-launch-association");
      Unit : constant String :=
        (if V.Nonempty_Text (Observed, O (Association, "unit")) then V.Text (Observed, O (Association, "unit"))
         else V.Text (Observed, O (Wait, "unit")));
      Supervisor : constant V.Node := O (Manager, "supervision");
      Resources : constant V.Node := O (Manager, "resources");
      Source_Supervisor : constant V.Node :=
        (if O (Source_Objects, "supervisionValue").Form = V.Object_Value
         then O (Source_Objects, "supervisionValue") else Supervisor);
      Native : constant String := Worldline.Runner_Outcome.Decide (Data, Capture);
      Decision : constant V.Node := V.Parse (Native);
      JSON_Arena : constant P.Bytes := JSON_Bytes (Observed);
      Output : Facts;
      Joined : Boolean := True;
      function Match (Item : V.Node; Encoded : E.Span) return Boolean is
        (Item.Form /= V.Missing and then Worldline.Raw_JSON.Ordinary_JSON_Finalization_Matches
          (JSON_Arena, Data, (P.Count (Item.First), P.Count (Item.Last - Item.First + 1)), Encoded));
      function Identity (Name : String; Encoded : E.Span) return Boolean is
        (Match (O (Source_Objects, Name), Encoded));
      function Clean_Process (Observation : V.Node) return Boolean is
        (V.Is_True (Observed, O (Observation, "processReturnObserved")) and then
         V.Is_True (Observed, O (Observation, "processWaitReturnObserved")) and then
         V.Is_True (Observed, O (Observation, "stdoutReachedEof")) and then
         V.Is_True (Observed, O (Observation, "stderrReachedEof")) and then
         O (Observation, "exception").Form = V.Null_Value and then
         V.Equal (Observed, O (Observation, "returncode"), Observed, O (Observation, "processWaitReturncode")));
      function Same_Unit (Observation : V.Node) return Boolean is
        (V.Is_Text (Observed, O (Observation, "unit"), Unit));
      function Retained_Since return String is
      begin
         if O (Association, "launchedAtUs").Form /= V.Missing then
            return V.Slice (Observed, O (Association, "launchedAtUs"));
         end if;
         --  Genuine historical query arguments remain usable for independent
         --  poll replay; missing launch correspondence is separately isolated.
         for I in 1 .. V.Count (Observed, Rows) loop
            if Kind (I, "agent-supervision-acquisition") then
               declare Item : constant V.Node := O (Row (I), "observation"); begin
                  if V.Is_Text (Observed, O (Item, "site"), "journal-poll") and then
                    O (Item, "sinceUs").Form /= V.Missing then return V.Slice (Observed, O (Item, "sinceUs")); end if;
               end;
            end if;
         end loop;
         return "";
      end Retained_Since;
      function Wait_Zero return Boolean is
        (Worldline.Raw_JSON.Python_JSON_Equal (V.Slice (Observed, O (Wait, "returncode")), "0"));
      function Ref_Profile (Encoded : E.Span; Reference, Type_Reference : String) return Boolean is
        (T (F (Encoded, "profile"), "python-actual-protocol-v1") and then
         Identity (Reference, F (Encoded, "reference")) and then
         Identity (Type_Reference, F (Encoded, "typeReference")));

      function Process_Text (Observation : V.Node; Replace_Errors : Boolean := True) return B.Decoded is
         Raw : constant B.Decoded := Raw_Bytes (Observed, O (Observation, "stdout"));
      begin
         if not Raw.Valid then return Raw; end if;
         return UTF8 (Raw.Data, Replace_Errors);
      end Process_Text;
      function Show_Values (Text : String) return String is
         --  Retain every partition in order, including duplicate keys: the
         --  object selectors retain first-key order and last-key values.
         procedure Scan (Render : Boolean; Output : out String; Size : out Natural)
           with Pre => Render or else Output'Length = 0,
                Relaxed_Initialization => Output,
                Post => Output'Initialized and then
                  (if Render then Size = Output'Length)
         is
            Used, First : Natural := 0;
            Comma : Boolean := False;
            function Ready return Boolean is
              (not Render or else
                 (Used <= Output'Length and then
                    (Used = 0 or else
                       Output (Output'First .. Output'First + (Used - 1))'Initialized)))
              with Ghost;
            procedure Put (Piece : String)
              with Pre => Ready,
                   Post => Ready and then Used >= Used'Old and then
                     Used - Used'Old = Piece'Length
            is
            begin
               if Piece'Length > Natural'Last - Used then
                  raise Constraint_Error with "show values exceed String capacity";
               end if;
               if Render and then Piece'Length > Output'Length - Used then
                  raise Program_Error with "show values extent mismatch";
               end if;
               declare
                  Next : constant Natural := Used + Piece'Length;
               begin
                  if Render and then Piece'Length > 0 then
                     Output (Output'First + Used .. Output'First + (Next - 1)) := Piece;
                  end if;
                  Used := Next;
               end;
            end Put;
            procedure Put_Quoted (Piece : String)
              with Pre => Ready,
                   Post => Ready and then Used >= Used'Old and then
                     Used - Used'Old >= 2
            is
               Extent : constant Natural := JSON_Render.Quote_Size (Piece);
            begin
               if Extent > Natural'Last - Used then
                  raise Constraint_Error with "show values exceed String capacity";
               end if;
               if Render and then Extent > Output'Length - Used then
                  raise Program_Error with "show values extent mismatch";
               end if;
               declare
                  Next : constant Natural := Used + Extent;
               begin
                  if Render then
                     JSON_Render.Write_Quote
                       (Piece, Output (Output'First + Used .. Output'First + (Next - 1)));
                  end if;
                  Used := Next;
               end;
            end Put_Quoted;
         begin
            Put ("{");
            while First < Text'Length loop
               pragma Loop_Invariant (Ready);
               pragma Loop_Invariant (First <= Text'Length);
               pragma Loop_Variant (Increases => First);
               declare
                  Last : constant Natural := Line_End (Text, First);
                  Following : constant Natural := Next_Line (Text, Last);
                  Separator : Natural := First;
               begin
                  while Separator < Last loop
                     pragma Loop_Invariant (Separator >= First and then Separator <= Last);
                     pragma Loop_Variant (Increases => Separator);
                     pragma Assert (Separator < Text'Length);
                     exit when Character_At (Text, Separator) = '=';
                     Separator := Separator + 1;
                  end loop;
                  if Separator < Last then
                     if Comma then Put (","); end if;
                     if First = Separator then
                        Put_Quoted ("");
                     else
                        Put_Quoted
                          (Text (Text'First + First .. Text'First + (Separator - 1)));
                     end if;
                     Put (":");
                     if Separator + 1 = Last then
                        Put_Quoted ("");
                     else
                        Put_Quoted
                          (Text (Text'First + (Separator + 1) .. Text'First + (Last - 1)));
                     end if;
                     Comma := True;
                  end if;
                  pragma Assert (Following > First and then Following <= Text'Length);
                  First := Following;
               end;
            end loop;
            Put ("}");
            if Render and then Used /= Output'Length then
               raise Program_Error with "show values extent mismatch";
            end if;
            Size := Used;
            pragma Assert (Output'Initialized);
         end Scan;
         Empty : String (1 .. 0);
         Size : Natural;
      begin
         Scan (False, Empty, Size);
         return Result : String (1 .. Size) do
            declare
               Written : Natural;
            begin
               Scan (True, Result, Written);
               pragma Assert (Written = Size);
            end;
         end return;
      end Show_Values;
      function Telemetry_Show (Observation : V.Node) return Boolean is
         Args : constant V.Node := O (Observation, "argv");
         --  Compare actual argv values without an access/allocated table.
         function Property (Index : Positive) return String is
           (case Index is when 1 => "Id", when 2 => "InvocationID", when 3 => "MemoryPeak",
            when 4 => "MemoryCurrent", when 5 => "MemorySwapPeak", when 6 => "CPUUsageNSec",
            when 7 => "TasksCurrent", when 8 => "Result", when 9 => "ActiveState",
            when 10 => "ExecMainStatus", when others => "ControlGroup");
      begin
         if not V.Is_Text (Observed, O (Observation, "site"), "systemd-show") or else
           not Same_Unit (Observation) or else Args.Form /= V.Array_Value or else
           V.Count (Observed, Args) /= 15 then return False; end if;
         for I in 1 .. 11 loop
            if not V.Is_Text (Observed, V.Element (Observed, Args, I + 4),
              "--property=" & Property (I)) then return False; end if;
         end loop;
         return V.Is_Text (Observed, V.Element (Observed, Args, 2), "--user") and then
           V.Is_Text (Observed, V.Element (Observed, Args, 3), "show") and then
           V.Is_Text (Observed, V.Element (Observed, Args, 4), Unit);
      end Telemetry_Show;
      function Limits_Show (Observation : V.Node) return Boolean is
         Args : constant V.Node := O (Observation, "argv");
         function Property (Index : Positive) return String is
           (case Index is when 1 => "MemoryMax", when 2 => "MemoryHigh", when 3 => "MemorySwapMax",
            when 4 => "CPUQuotaPerSecUSec", when 5 => "CPUWeight", when 6 => "TasksMax",
            when 7 => "MemoryAccounting", when 8 => "CPUAccounting", when 9 => "TasksAccounting",
            when others => "ControlGroup");
      begin
         if not V.Is_Text (Observed, O (Observation, "site"), "systemd-show") or else
           not Same_Unit (Observation) or else Args.Form /= V.Array_Value or else
           V.Count (Observed, Args) /= 14 then return False; end if;
         for I in 1 .. 10 loop
            if not V.Is_Text (Observed, V.Element (Observed, Args, I + 4),
              "--property=" & Property (I)) then return False; end if;
         end loop;
         return V.Is_Text (Observed, V.Element (Observed, Args, 2), "--user") and then
           V.Is_Text (Observed, V.Element (Observed, Args, 3), "show") and then
           V.Is_Text (Observed, V.Element (Observed, Args, 4), Unit);
      end Limits_Show;
      function Find_Show (Before : Positive; Telemetry : Boolean) return Natural is
         Found : Natural := 0;
      begin
         for I in 1 .. Before - 1 loop
            if Kind (I, "agent-control-acquisition") and then
              (if Telemetry then Telemetry_Show (O (Row (I), "observation"))
               else Limits_Show (O (Row (I), "observation"))) then Found := I;
            elsif Kind (I, (if Telemetry then "agent-resource-telemetry-acquisition"
                           else "agent-resource-limits-acquisition")) then
               Found := 0;
            end if;
         end loop;
         return Found;
      end Find_Show;
      function Cgroup_Path (Group, Name : String) return String is
         procedure Scan (Render : Boolean; Output : out String; Size : out Natural)
           with Pre => Render or else Output'Length = 0,
                Relaxed_Initialization => Output,
                Post => Output'Initialized and then
                  (if Render then Size = Output'Length)
         is
            Used, Normalized, Position, First : Natural := 0;
            function Ready return Boolean is
              (not Render or else
                 (Used <= Output'Length and then
                    (Used = 0 or else
                       Output (Output'First .. Output'First + (Used - 1))'Initialized)))
              with Ghost;
            procedure Put (Piece : String)
              with Pre => Ready,
                   Post => Ready and then Used >= Used'Old and then
                     Used - Used'Old = Piece'Length
            is
            begin
               if Piece'Length > Natural'Last - Used then
                  raise Constraint_Error with "cgroup path exceeds String capacity";
               end if;
               if Render and then Piece'Length > Output'Length - Used then
                  raise Program_Error with "cgroup path extent mismatch";
               end if;
               declare
                  Next : constant Natural := Used + Piece'Length;
               begin
                  if Render and then Piece'Length > 0 then
                     Output (Output'First + Used .. Output'First + (Next - 1)) := Piece;
                  end if;
                  Used := Next;
               end;
            end Put;
         begin
            Put ("/sys/fs/cgroup/");
            while Position < Group'Length loop
               pragma Loop_Invariant (Ready);
               pragma Loop_Invariant (Position <= Group'Length);
               pragma Loop_Invariant (Normalized <= Position);
               pragma Loop_Invariant
                 (if Normalized > 0 and then Position < Group'Length and then
                     Character_At (Group, Position) /= '/'
                  then Normalized < Position);
               pragma Loop_Variant (Increases => Position);
               if Character_At (Group, Position) = '/' then
                  Position := Position + 1;
               else
                  First := Position;
                  while Position < Group'Length and then Character_At (Group, Position) /= '/' loop
                     pragma Loop_Invariant (Position >= First and then Position <= Group'Length);
                     pragma Loop_Variant (Increases => Position);
                     Position := Position + 1;
                  end loop;
                  if First < Position and then
                    not (Position - First = 1 and then Character_At (Group, First) = '.') then
                     declare
                        Piece : constant Natural := Position - First;
                        Extra : constant Natural := (if Normalized > 0 then 1 else 0);
                     begin
                        if Extra > Group'Length - Normalized or else
                          Piece > Group'Length - Normalized - Extra then
                           raise Constraint_Error with "normalized cgroup path exceeds input extent";
                        end if;
                        if Extra = 1 then Put ("/"); end if;
                        if Piece > Natural'Last - Used then
                           raise Constraint_Error with "cgroup path exceeds String extent";
                        end if;
                        if Render then
                           if Piece > Output'Length - Used then
                              raise Program_Error with "cgroup path extent mismatch";
                           end if;
                           Output (Output'First + Used ..
                             Output'First + (Used + Piece - 1)) :=
                               Group (Group'First + First ..
                                 Group'First + (Position - 1));
                        end if;
                        Used := Used + Piece;
                        Normalized := Normalized + Extra + Piece;
                     end;
                  end if;
               end if;
            end loop;
            if Normalized > 0 then Put ("/"); end if;
            Put (Name);
            if Render and then Used /= Output'Length then
               raise Program_Error with "cgroup path extent mismatch";
            end if;
            Size := Used;
            pragma Assert (Output'Initialized);
         end Scan;
         Empty : String (1 .. 0);
         Size : Natural;
      begin
         Scan (False, Empty, Size);
         return Result : String (1 .. Size) do
            declare
               Written : Natural;
            begin
               Scan (True, Result, Written);
               pragma Assert (Written = Size);
            end;
         end return;
      end Cgroup_Path;
      function Cgroup (From, Before : Natural; Group, Name : String) return String is
         Found : V.Node := V.No_Node;
      begin
         if Group = "" then return "null"; end if;
         for I in From + 1 .. Before - 1 loop
            declare Item : constant V.Node := O (Row (I), "observation"); begin
               if Kind (I, "agent-control-acquisition") and then
                 V.Is_Text (Observed, O (Item, "site"), "cgroup-read") and then
                 V.Is_Text (Observed, O (Item, "name"), Name) then
                  if Found.Form /= V.Missing or else
                    not V.Is_Text (Observed, O (Item, "controlGroup"), Group) then return ""; end if;
                  Found := Item;
               end if;
            end;
         end loop;
         if Found.Form /= V.Object_Value then return ""; end if;
         declare
            Actual_Path : constant B.Decoded := Raw_Bytes (Observed, O (Found, "path"));
         begin
            if not Actual_Path.Valid or else Actual_Path.Data /= Cgroup_Path (Group, Name) then return ""; end if;
         end;
         if V.Is_False (Observed, O (Found, "readReturned")) and then
           O (Found, "exception").Form = V.Object_Value and then
           O (Found, "bytes").Form = V.Null_Value then return "null"; end if;
         if not V.Is_True (Observed, O (Found, "readReturned")) or else
           O (Found, "exception").Form /= V.Null_Value then return ""; end if;
         declare
            Raw : constant B.Decoded := Raw_Bytes (Observed, O (Found, "bytes"));
         begin
            if not Raw.Valid then return ""; end if;
            declare Decoded : constant B.Decoded := UTF8 (Raw.Data, False); begin
               if not Decoded.Valid then return ""; end if;
               --  Universal newlines are equivalent to ordinary whitespace for
               --  memory.events and limits values; preserve internal newlines.
               declare
                  Text : String (1 .. Decoded.Length) with Relaxed_Initialization;
                  Used : Natural := 0;
                  Position : Natural := 0;
                  function Ready return Boolean is
                    (Used = 0 or else Text (1 .. Used)'Initialized)
                    with Ghost;
               begin
                  while Position < Decoded.Length loop
                     pragma Loop_Invariant (Position <= Decoded.Length);
                     pragma Loop_Invariant (Used <= Position);
                     pragma Loop_Invariant (Ready);
                     pragma Loop_Variant (Increases => Position);
                     Used := Used + 1;
                     if Character_At (Decoded.Data, Position) = Character'Val (13) then
                        Text (Used) := Character'Val (10);
                        if Position + 1 < Decoded.Length and then
                          Character_At (Decoded.Data, Position + 1) = Character'Val (10) then
                           Position := Position + 1;
                        end if;
                     else Text (Used) := Character_At (Decoded.Data, Position);
                     end if;
                     Position := Position + 1;
                  end loop;
                  return V.Quote (Strip (Text (1 .. Used)));
               end;
            end;
         end;
      end Cgroup;
      function Counters (Text : String) return String is
         procedure Scan (Render : Boolean; Output : out String; Size : out Natural)
           with Pre => Render or else Output'Length = 0,
                Relaxed_Initialization => Output,
                Post => Output'Initialized and then
                  (if Render then Size = Output'Length)
         is
            Used, First : Natural := 0;
            Comma : Boolean := False;
            function Ready return Boolean is
              (not Render or else
                 (Used <= Output'Length and then
                    (Used = 0 or else
                       Output (Output'First .. Output'First + (Used - 1))'Initialized)))
              with Ghost;
            procedure Put (Piece : String)
              with Pre => Ready,
                   Post => Ready and then Used >= Used'Old and then
                     Used - Used'Old = Piece'Length
            is
            begin
               if Piece'Length > Natural'Last - Used then
                  raise Constraint_Error with "counter values exceed String capacity";
               end if;
               if Render and then Piece'Length > Output'Length - Used then
                  raise Program_Error with "counter values extent mismatch";
               end if;
               declare
                  Next : constant Natural := Used + Piece'Length;
               begin
                  if Render and then Piece'Length > 0 then
                     Output (Output'First + Used .. Output'First + (Next - 1)) := Piece;
                  end if;
                  Used := Next;
               end;
            end Put;
            procedure Put_Quoted (Piece : String)
              with Pre => Ready,
                   Post => Ready and then Used >= Used'Old and then
                     Used - Used'Old >= 2
            is
               Extent : constant Natural := JSON_Render.Quote_Size (Piece);
            begin
               if Extent > Natural'Last - Used then
                  raise Constraint_Error with "counter values exceed String capacity";
               end if;
               if Render and then Extent > Output'Length - Used then
                  raise Program_Error with "counter values extent mismatch";
               end if;
               declare
                  Next : constant Natural := Used + Extent;
               begin
                  if Render then
                     JSON_Render.Write_Quote
                       (Piece, Output (Output'First + Used .. Output'First + (Next - 1)));
                  end if;
                  Used := Next;
               end;
            end Put_Quoted;
            procedure Put_Decimal (From, After : Natural; Extent : Positive)
              with Pre => Ready and then From < After and then After <= Text'Length,
                   Post => Ready and then Used >= Used'Old and then
                     Used - Used'Old = Extent
            is
            begin
               if Extent > Natural'Last - Used then
                  raise Constraint_Error with "counter values exceed String capacity";
               end if;
               if Render and then Extent > Output'Length - Used then
                  raise Program_Error with "counter values extent mismatch";
               end if;
               declare
                  Next : constant Natural := Used + Extent;
                  Position : Natural := From;
                  Written, Width : Natural := 0;
                  Value : Integer;
               begin
                  if Render then
                     while Position < After loop
                        pragma Loop_Invariant (Position >= From and then Position <= After);
                        pragma Loop_Invariant (Written <= Extent);
                        pragma Loop_Invariant (Used <= Output'Length);
                        pragma Loop_Invariant (Extent <= Output'Length - Used);
                        pragma Loop_Invariant
                          (if Used + Written > 0 then
                             Output (Output'First ..
                                       Output'First + (Used + Written - 1))'Initialized);
                        pragma Loop_Variant (Increases => Position);
                        Width := V.UTF8_Width (Text, Position);
                        if Width = 0 or else Width > After - Position or else Written = Extent then
                           raise Program_Error with "counter decimal extent mismatch";
                        end if;
                        Value := Digit (Code (Text, Position, Width));
                        if Value < 0 then
                           raise Program_Error with "counter decimal extent mismatch";
                        end if;
                        Output (Output'First + (Used + Written)) :=
                          Character'Val (Character'Pos ('0') + Value);
                        Written := Written + 1;
                        Position := Position + Width;
                     end loop;
                     if Written /= Extent then
                        raise Program_Error with "counter decimal extent mismatch";
                     end if;
                  end if;
                  Used := Next;
               end;
            end Put_Decimal;
         begin
            Put ("{");
            while First < Text'Length loop
               pragma Loop_Invariant (Ready);
               pragma Loop_Invariant (First <= Text'Length);
               pragma Loop_Variant (Increases => First);
               declare
                  Last : constant Natural := Line_End (Text, First);
                  Following : constant Natural := Next_Line (Text, Last);
                  Offset : Natural := First;
                  Key_First, Key_Last, Value_First, Value_Last : Natural := 0;
                  function Space_At (Pos : Natural) return Boolean is
                     W : constant Natural := V.UTF8_Width (Text, Pos);
                  begin
                     return W > 0 and then Pos < Text'Length and then W <= Text'Length - Pos
                       and then (White (Code (Text, Pos, W)) or else Code (Text, Pos, W) in 28 .. 31);
                  end Space_At;
                  function Advance (From : Natural; Want_Space : Boolean) return Natural
                    with Pre => From <= Text'Length,
                         Post => Advance'Result >= From and then Advance'Result <= Text'Length
                  is
                     Pos : Natural := From;
                     W : Natural;
                  begin
                     while Pos < Last and then Pos < Text'Length loop
                        pragma Loop_Invariant (Pos >= From and then Pos <= Text'Length);
                        pragma Loop_Variant (Increases => Pos);
                        W := V.UTF8_Width (Text, Pos);
                        exit when W = 0 or else W > Text'Length - Pos
                          or else (if Want_Space then not Space_At (Pos) else Space_At (Pos));
                        Pos := Pos + W;
                     end loop;
                     return Pos;
                  end Advance;
               begin
                  Offset := Advance (Offset, True);
                  Key_First := Offset;
                  Offset := Advance (Offset, False);
                  Key_Last := Offset;
                  Offset := Advance (Offset, True);
                  Value_First := Offset;
                  Offset := Advance (Offset, False);
                  Value_Last := Offset;
                  Offset := Advance (Offset, True);
                  pragma Assert (Following > First and then Following <= Text'Length);
                  if Key_First < Key_Last and then Value_First < Value_Last and then Offset = Last then
                     declare
                        Position : Natural := Value_First;
                        Significant_First : Natural := Value_Last;
                        Extent, Width : Natural := 0;
                        Value : Integer;
                        Valid : Boolean := True;
                     begin
                        --  String_Integer(..., True) admits exactly the decimal
                        --  scalars recognized by Digit. Count its canonical
                        --  image without constructing either a big integer or
                        --  an image; leading zeroes vanish and zero stays "0".
                        while Position < Value_Last loop
                           pragma Loop_Invariant
                             (Position >= Value_First and then Position <= Value_Last);
                           pragma Loop_Invariant
                             (Significant_First >= Value_First and then
                                Significant_First <= Value_Last);
                           pragma Loop_Invariant (Extent <= Position - Value_First);
                           pragma Loop_Variant (Increases => Position);
                           Width := V.UTF8_Width (Text, Position);
                           if Width = 0 or else Width > Value_Last - Position then
                              Valid := False; exit;
                           end if;
                           Value := Digit (Code (Text, Position, Width));
                           if Value < 0 then Valid := False; exit; end if;
                           if Value > 0 and then Significant_First = Value_Last then
                              Significant_First := Position;
                           end if;
                           if Significant_First < Value_Last then Extent := Extent + 1; end if;
                           Position := Position + Width;
                        end loop;
                        if not Valid and then Is_Digits
                          (Text (Text'First + Value_First .. Text'First + (Value_Last - 1)))
                        then
                           --  The old fold stopped here without a comma before
                           --  this marker, even after earlier valid counters.
                           Put ("INVALID_INTEGER");
                           exit;
                        end if;
                        if Valid then
                           if Comma then Put (","); end if;
                           Put_Quoted
                             (Text (Text'First + Key_First .. Text'First + (Key_Last - 1)));
                           Put (":");
                           if Extent = 0 then
                              Put ("0");
                           else
                              Put_Decimal (Significant_First, Value_Last, Extent);
                           end if;
                           Comma := True;
                        end if;
                     end;
                  end if;
                  First := Following;
               end;
            end loop;
            Put ("}");
            if Render and then Used /= Output'Length then
               raise Program_Error with "counter values extent mismatch";
            end if;
            Size := Used;
            pragma Assert (Output'Initialized);
         end Scan;
         Empty : String (1 .. 0);
         Size : Natural;
      begin
         Scan (False, Empty, Size);
         return Result : String (1 .. Size) do
            declare
               Written : Natural;
            begin
               Scan (True, Result, Written);
               pragma Assert (Written = Size);
            end;
         end return;
      end Counters;
      function Derive_Reading (Index : Positive; Telemetry : Boolean) return String is
         Source_Index : constant Natural := Find_Show (Index, Telemetry);
         Source : constant V.Node :=
           (if Source_Index = 0 then V.No_Node else O (Row (Source_Index), "observation"));
         function Unavailable return String is
           (if Telemetry then "{""state"":""UNAVAILABLE"",""reason"":""the unit is gone or the manager did not answer""}"
            else "{""state"":""UNAVAILABLE"",""reason"":""the user manager did not answer for this unit""}");
      begin
         if Source_Index = 0 or else not Clean_Process (Source) then return ""; end if;
         if not Worldline.Raw_JSON.Python_JSON_Equal
           (V.Slice (Observed, O (Source, "processWaitReturncode")), "0") then return Unavailable; end if;
         declare
            Text : constant B.Decoded := Process_Text (Source);
            Shown : constant String := Show_Values (Text.Data);
            Root : constant V.Node := V.Parse (Shown);
            function S (Name : String) return V.Node is (V.Field (Shown, Root, Name));
            Group : constant String := V.Text (Shown, S ("ControlGroup"));
            function Nullable (Name : String) return String is
              (if S (Name).Form = V.Missing then "null" else V.Slice (Shown, S (Name)));
            function Number (Name : String) return String is
               Parsed : constant Integer_Result := String_Integer (V.Text (Shown, S (Name)), True);
            begin
               if Is_Digits (V.Text (Shown, S (Name))) and then not Parsed.Valid then return ""; end if;
               return (if Parsed.Valid and then Parsed.Value <
                 Exact_Decimal.Power (2, To_Big_Integer (64)) - To_Big_Integer (1)
                 then Image (Parsed.Value) else "null");
            end Number;
         begin
            if not Text.Valid then return ""; end if;
            if Telemetry then
               if Group = "" and then (S ("ActiveState").Form = V.Missing or else
                 V.Is_Text (Shown, S ("ActiveState"), "") or else
                 V.Is_Text (Shown, S ("ActiveState"), "inactive")) then
                  return "{""state"":""UNAVAILABLE"",""reason"":""the manager holds no record of this unit; it was never started or has already been collected, so nothing was measured""}";
               end if;
               declare
                  Encoded : constant String := Cgroup (Source_Index, Index, Group, "memory.events");
                  Events : constant String := V.Text (Encoded);
                  Values : constant String := Counters (Events);
                  Map : constant V.Node := V.Parse (Values);
                  function Hit (Name : String) return Boolean is
                    (V.Truth (Values, V.Field (Values, Map, Name)));
                  Read : constant Boolean := Strip (Events)'Length > 0;
                  Oom : constant Boolean := V.Is_Text (Shown, S ("Result"), "oom-kill");
               begin
                  if Encoded = "" or else Map.Form /= V.Object_Value then return ""; end if;
                  return "{""state"":""OBSERVED"",""workloadIdentity"":{""unit"":" & Nullable ("Id") &
                    ",""invocationId"":" & Nullable ("InvocationID") & ",""controlGroup"":" &
                    (if Group = "" then "null" else V.Quote (Group)) & "},""peakMemoryBytes"":" & Number ("MemoryPeak") &
                    ",""currentMemoryBytes"":" & Number ("MemoryCurrent") & ",""peakSwapBytes"":" & Number ("MemorySwapPeak") &
                    ",""cpuTimeNanoseconds"":" & Number ("CPUUsageNSec") & ",""tasksCurrent"":" & Number ("TasksCurrent") &
                    ",""result"":" & Nullable ("Result") & ",""activeState"":" & Nullable ("ActiveState") &
                    ",""memoryEvents"":" & (if V.Count (Values, Map) = 0 then "null" else Values) &
                    ",""hitMemoryCeiling"":" & (if Read then Bit (Hit ("max") or else Hit ("oom") or else Hit ("oom_kill")) else "null") &
                    ",""oomKilled"":" & (if Read then Bit (Hit ("oom_kill") or else Oom) elsif Oom then "true" else "null") & "}";
               end;
            else
               declare
                  function Kernel (Name : String) return String is (Cgroup (Source_Index, Index, Group, Name));
                  Memory_Max : constant String := Kernel ("memory.max");
                  Memory_High : constant String := Kernel ("memory.high");
                  Swap_Max : constant String := Kernel ("memory.swap.max");
                  CPU_Max : constant String := Kernel ("cpu.max");
                  Pids_Max : constant String := Kernel ("pids.max");
               begin
                  if Memory_Max = "" or else Memory_High = "" or else Swap_Max = "" or else
                    CPU_Max = "" or else Pids_Max = "" then return ""; end if;
                  return "{""state"":" & V.Quote (if Group /= "" then "OBSERVED" else "UNIT_GONE") &
                    ",""controlGroup"":" & (if Group = "" then "null" else V.Quote (Group)) &
                    ",""systemd"":{""MemoryMax"":" & Nullable ("MemoryMax") & ",""MemoryHigh"":" & Nullable ("MemoryHigh") &
                    ",""MemorySwapMax"":" & Nullable ("MemorySwapMax") & ",""CPUQuotaPerSecUSec"":" & Nullable ("CPUQuotaPerSecUSec") &
                    ",""CPUWeight"":" & Nullable ("CPUWeight") & ",""TasksMax"":" & Nullable ("TasksMax") &
                    ",""MemoryAccounting"":" & Nullable ("MemoryAccounting") & ",""CPUAccounting"":" & Nullable ("CPUAccounting") &
                    ",""TasksAccounting"":" & Nullable ("TasksAccounting") & "},""kernel"":{""memory.max"":" & Memory_Max &
                    ",""memory.high"":" & Memory_High & ",""memory.swap.max"":" & Swap_Max & ",""cpu.max"":" & CPU_Max &
                    ",""pids.max"":" & Pids_Max & "},""cgroupReadable"":" &
                    Bit (Memory_Max /= "null" or else Memory_High /= "null" or else Swap_Max /= "null" or else
                         CPU_Max /= "null" or else Pids_Max /= "null") & "}";
               end;
            end if;
         end;
      end Derive_Reading;
      function Source_Archive_Matches
        (JSON, Name : String; Field_Name : String := "") return Boolean
      is
         Captured : constant B.Decoded := Raw_Bytes (Observed, O (Source_Objects, Name));
         Original : constant E.Bytes := JSON_Bytes (Captured.Data);
         Expected_Data : constant P.Bytes := JSON_Bytes (JSON);
         Root : constant E.Span := (1, Original'Length);
         Item : constant E.Span :=
           (if Field_Name = "" then Root else L.Field (Original, Root, Field_Name));
      begin
         return Captured.Valid and then Worldline.Raw_JSON.Ordinary_JSON_Finalization_Matches
           (Expected_Data, Original, (1, Expected_Data'Length), Item);
      end Source_Archive_Matches;
      function Resource_Join return Boolean is
         Last_Telemetry, Effective : V.Node := V.No_Node;
         type Maximum_Array is array (Positive range 1 .. 4) of V.Node;
         Maximum : Maximum_Array := (others => V.No_Node);
         Hit, Oom : Boolean := False;
         Limits_Ordinal : Natural := 0;
         Telemetry_Ordinal : Natural := 0;
         Effective_Complete : Boolean := False;
         Last_State : Boolean := False;
         function Maximum_Name (Index : Positive) return String is
           (case Index is when 1 => "peakMemoryBytes", when 2 => "peakSwapBytes",
            when 3 => "cpuTimeNanoseconds", when others => "tasksCurrent");
      begin
         for I in 1 .. V.Count (Observed, Rows) loop
            pragma Loop_Invariant
              (if Last_State then
                 Last_Telemetry.Form = V.Object_Value and then Last_Telemetry.First > 0
                 and then Last_Telemetry.First < Last_Telemetry.Last
                 and then Last_Telemetry.Last <= Observed'Length);
            if Kind (I, "agent-resource-limits-acquisition") or else
              Kind (I, "agent-resource-telemetry-acquisition") then
               declare
                  Telemetry : constant Boolean := Kind (I, "agent-resource-telemetry-acquisition");
                  Observation : constant V.Node := O (Row (I), "observation");
                  Reading : constant V.Node := O (Observation, "reading");
                  Derived : constant String := Derive_Reading (I, Telemetry);
                  Ordinal : constant Integer_Result := Integer_Value (Observed, O (Row (I), "occurrence"));
               begin
                  if not Same_Unit (Observation) or else not Ordinal.Valid or else
                    Ordinal.Value /= To_Big_Integer (Limits_Ordinal + Telemetry_Ordinal) or else
                    Derived = "" or else not Worldline.Raw_JSON.Python_JSON_Equal
                      (Derived, V.Slice (Observed, Reading)) then return False; end if;
                  if not Telemetry then
                     if Effective_Complete or else Telemetry_Ordinal /= 0 then return False; end if;
                     Limits_Ordinal := Limits_Ordinal + 1;
                     if V.Truth (Observed, O (Reading, "cgroupReadable")) then
                        Effective := Reading; Effective_Complete := True;
                     end if;
                  else
                     Telemetry_Ordinal := Telemetry_Ordinal + 1;
                     if V.Is_Text (Observed, O (Reading, "state"), "OBSERVED") then
                        Last_Telemetry := Reading; Last_State := True;
                        for K in Maximum'Range loop
                           declare
                              Value : constant V.Node := O (Reading, Maximum_Name (K));
                              Parsed : constant Integer_Result := Integer_Value (Observed, Value);
                              Old : constant Integer_Result := Integer_Value (Observed, Maximum (K));
                           begin
                              if not Old.Valid or else
                                Old.Value <= (if Parsed.Valid then Parsed.Value else To_Big_Integer (0)) then
                                 Maximum (K) := Value;
                              end if;
                           end;
                        end loop;
                        Hit := Hit or else V.Truth (Observed, O (Reading, "hitMemoryCeiling"));
                        Oom := Oom or else V.Truth (Observed, O (Reading, "oomKilled"));
                     end if;
                  end if;
               end;
            end if;
         end loop;
         if Effective.Form = V.Missing then
            if not Source_Archive_Matches ("{""state"":""UNAVAILABLE"",""reason"":""not sampled""}",
              "resourceContainerArchive", "effective") then return False; end if;
         elsif not Source_Archive_Matches (V.Slice (Observed, Effective), "resourceContainerArchive", "effective") then
            return False;
         end if;
         if not Last_State then
            return Source_Archive_Matches ("{""state"":""UNAVAILABLE"",""reason"":""not sampled""}",
              "resourceObservationArchive");
         end if;
         declare
            function Fields return String is
               Members : constant V.Member_Index := V.Members (Observed, Last_Telemetry);
               procedure Scan (Render : Boolean; Output : out String; Size : out Natural)
                 with Pre => Render or else Output'Length = 0,
                      Relaxed_Initialization => Output,
                      Post => Output'Initialized and then
                        (if Render then Size = Output'Length)
               is
                  Used : Natural := 0;
                  function Ready return Boolean is
                    (not Render or else
                       (Used <= Output'Length and then
                          (Used = 0 or else
                             Output (Output'First .. Output'First + (Used - 1))'Initialized)))
                    with Ghost;
                  procedure Put (Piece : String)
                    with Pre => Ready,
                         Post => Ready and then Used >= Used'Old and then
                           Used - Used'Old = Piece'Length
                  is
                  begin
                     if Piece'Length > Natural'Last - Used then
                        raise Constraint_Error with "telemetry fields exceed String capacity";
                     end if;
                     if Render and then Piece'Length > Output'Length - Used then
                        raise Program_Error with "telemetry fields extent mismatch";
                     end if;
                     declare
                        Next : constant Natural := Used + Piece'Length;
                     begin
                        if Render and then Piece'Length > 0 then
                           Output (Output'First + Used .. Output'First + (Next - 1)) := Piece;
                        end if;
                        Used := Next;
                     end;
                  end Put;
                  procedure Put_Quoted (Item : V.Node)
                    with Pre => Ready and then Item.Form = V.String_Value
                           and then Item.First > 0 and then Item.First < Item.Last
                           and then Item.Last <= Observed'Length,
                         Post => Ready and then Used >= Used'Old and then
                           Used - Used'Old >= 2
                  is
                     Extent : constant Natural := JSON_Render.Quote_Size (Observed, Item);
                  begin
                     if Extent > Natural'Last - Used then
                        raise Constraint_Error with "telemetry fields exceed String capacity";
                     end if;
                     if Render and then Extent > Output'Length - Used then
                        raise Program_Error with "telemetry fields extent mismatch";
                     end if;
                     declare
                        Next : constant Natural := Used + Extent;
                     begin
                        if Render then
                           JSON_Render.Write_Quote
                             (Observed, Item,
                              Output (Output'First + Used .. Output'First + (Next - 1)));
                        end if;
                        Used := Next;
                     end;
                  end Put_Quoted;
                  procedure Put_Raw (Item : V.Node)
                    with Pre => Ready,
                         Post => Ready and then Used >= Used'Old
                  is
                  begin
                     if Item.Form = V.Missing then
                        Put ("null");
                     elsif Item.First > 0 and then Item.First <= Item.Last
                       and then Item.Last <= Observed'Length
                     then
                        declare
                           Extent : constant Natural := Item.Last - Item.First + 1;
                        begin
                           if Extent > Natural'Last - Used then
                              raise Constraint_Error with "telemetry fields exceed String capacity";
                           end if;
                           if Render and then Extent > Output'Length - Used then
                              raise Program_Error with "telemetry fields extent mismatch";
                           end if;
                           declare
                              Next : constant Natural := Used + Extent;
                           begin
                              if Render then
                                 Output (Output'First + Used .. Output'First + (Next - 1)) :=
                                   Observed (Observed'First + (Item.First - 1) ..
                                             Observed'First + (Item.Last - 1));
                              end if;
                              Used := Next;
                           end;
                        end;
                     end if;
                  end Put_Raw;
               begin
                  Put ("{");
                  for Index in 1 .. Members.Length loop
                     pragma Loop_Invariant (Ready);
                     declare
                        Member : constant V.Member_Entry := Members.Entries (Index);
                        Expected_Value : V.Node := Member.Item;
                     begin
                        for K in Maximum'Range loop
                           if V.Is_Text (Observed, Member.Key, Maximum_Name (K)) then
                              Expected_Value := Maximum (K);
                           end if;
                        end loop;
                        if Index > 1 then Put (","); end if;
                        Put_Quoted (Member.Key);
                        Put (":");
                        if (Hit and then V.Is_Text (Observed, Member.Key, "hitMemoryCeiling")) or else
                          (Oom and then V.Is_Text (Observed, Member.Key, "oomKilled"))
                        then
                           Put ("true");
                        else
                           Put_Raw (Expected_Value);
                        end if;
                     end;
                  end loop;
                  Put ("}");
                  if Render and then Used /= Output'Length then
                     raise Program_Error with "telemetry fields extent mismatch";
                  end if;
                  Size := Used;
                  pragma Assert (Output'Initialized);
               end Scan;
               Empty : String (1 .. 0);
               Size : Natural;
            begin
               Scan (False, Empty, Size);
               return Result : String (1 .. Size) do
                  declare
                     Written : Natural;
                  begin
                     Scan (True, Result, Written);
                     pragma Assert (Written = Size);
                  end;
               end return;
            end Fields;
         begin
            return Source_Archive_Matches (Fields,
              "resourceObservationArchive");
         end;
      end Resource_Join;

      function Archive_Matches (Item : V.Node; Encoded : E.Span) return Boolean is
         Payload : constant String := V.Text (Observed, O (Item, "payload"));
         Extent : constant B.Extent := B.Base64_Extent (Payload);
         function Digit64 (C : Character) return Natural is
           (if C in 'A' .. 'Z' then Character'Pos (C) - Character'Pos ('A')
            elsif C in 'a' .. 'z' then Character'Pos (C) - Character'Pos ('a') + 26
            elsif C in '0' .. '9' then Character'Pos (C) - Character'Pos ('0') + 52
            elsif C = '+' then 62 elsif C = '/' then 63 else 0)
           with Post => Digit64'Result <= 63;
         function Byte_At (Offset : Natural) return Natural is
            Quartets : constant Natural := Offset / 3;
            Position, A, B1, C, D : Natural;
         begin
            if Quartets > Natural'Last / 4 or else Payload'Length < 4 then
               return Natural'Last;
            end if;
            Position := Quartets * 4;
            if Position > Payload'Length - 4 then return Natural'Last; end if;
            A := Digit64 (Character_At (Payload, Position));
            B1 := Digit64 (Character_At (Payload, Position + 1));
            C := Digit64 (Character_At (Payload, Position + 2));
            D := Digit64 (Character_At (Payload, Position + 3));
            return (case Offset mod 3 is when 0 => A * 4 + B1 / 16,
                    when 1 => (B1 mod 16) * 16 + C / 4,
                    when others => (C mod 4) * 64 + D);
         end Byte_At;
      begin
         if Item.Form /= V.Object_Value or else
           not V.Is_Text (Observed, O (Item, "encoding"), "base64") or else
           not Extent.Valid or else E.Count (Extent.Length) /= Encoded.Length or else
           not P.Valid (Data, Encoded) then return False; end if;
         for I in 1 .. Extent.Length loop
            if Natural (Data (Encoded.First + E.Count (I - 1))) /= Byte_At (I - 1) then return False; end if;
         end loop;
         return True;
      end Archive_Matches;
      function Wait_Join return Boolean is
         Exit_Operand : constant E.Span := F (Capture, "exitCode");
         Snapshot : constant V.Node := O (Wait, "returncodeCapture");
         Type_Name : constant String := V.Text (Observed, O (Snapshot, "type"));
         Actual : constant V.Node := O (Wait, "returncode");
      begin
         if not V.Is_True (Observed, O (Wait, "waitReturnObserved")) or else
           not Same_Unit (Wait) then return False; end if;
         if T (F (Exit_Operand, "profile"), "builtin-v1") then
            if not Archive_Matches (O (Wait, "waitValueArchive"), F (Exit_Operand, "value")) then
               --  Genuine historical primitive JSON is sufficient only when it
               --  actually retains an exact value (not a lossy NaN/byte/object).
               if Actual.Form = V.Missing or else Actual.Form = V.Number_Value or else
                 not Match (Actual, F (Exit_Operand, "value")) then return False; end if;
            end if;
            return Snapshot.Form = V.Object_Value and then
              (case Form (F (Exit_Operand, "value")) is
               when E.Null_Value => Type_Name = "NoneType" and then Actual.Form = V.Null_Value,
               when E.Boolean_Value => Type_Name = "bool" and then Actual.Form = V.Boolean_Value,
               when E.Integer_Value => Type_Name = "int" and then Actual.Form = V.Integer_Value,
               when E.Float_Value => Type_Name = "float",
               when E.Text_Value => Type_Name = "str",
               when E.Bytes_Value => Type_Name = "bytes",
               when others => False) and then
              (Archive_Matches (O (Wait, "waitValueArchive"), F (Exit_Operand, "value")) or else
               Match (O (Snapshot, "value"), F (Exit_Operand, "value")));
         end if;
         if Type_Name /= "python-actual-reference-v1" or else
           not Ref_Profile (Exit_Operand, "launcherExitReference", "launcherExitTypeReference") then return False; end if;
         declare
            Ref : constant Integer_Result := Integer_Value (Observed, O (Snapshot, "reference"));
            Type_Ref : constant Integer_Result := Integer_Value (Observed, O (Snapshot, "typeReference"));
         begin
            return Ref.Valid and then Type_Ref.Valid and then
              T (F (Exit_Operand, "reference"), Image (Ref.Value)) and then
              T (F (Exit_Operand, "typeReference"), Image (Type_Ref.Value));
         end;
      end Wait_Join;
      function Supervisor_Exit_Join return Boolean is
         Captured : constant B.Decoded := Raw_Bytes (Observed, O (Source_Objects, "supervisionArchive"));
         Original : constant E.Bytes := JSON_Bytes (Captured.Data);
         Value : constant E.Span := L.Field (Original, (1, Original'Length), "launcherExit");
         Exit_Operand : constant E.Span := F (F (Capture, "exitCode"), "value");
      begin
         if not Captured.Valid or else not P.Valid (Original, Value) or else
           not P.Valid (Data, Exit_Operand) or else Value.Length /= Exit_Operand.Length then return False; end if;
         if Value.Length > 0 then
            for I in E.Count range 0 .. Value.Length - 1 loop
               if Original (Value.First + I) /= Data (Exit_Operand.First + I) then return False; end if;
            end loop;
         end if;
         return True;
      end Supervisor_Exit_Join;
      function Protocol_Join return Boolean is
         Manager_Result : constant E.Span := F (Capture, "managerResult");
         Observation : constant E.Span := F (Capture, "resourceObservation");
         Container : constant E.Span := F (Capture, "resourceContainer");
         Kind_Source : constant E.Span := F (Capture, "supervisionKind");
         function Exact_Builtin (Type_Node : V.Node) return Boolean is
           (V.Equal (Observed, Type_Node, Observed, O (Source_Objects, "booleanTypeReference")) or else
            V.Equal (Observed, Type_Node, Observed, O (Source_Objects, "integerTypeReference")) or else
            V.Equal (Observed, Type_Node, Observed, O (Source_Objects, "floatTypeReference")) or else
            V.Equal (Observed, Type_Node, Observed, O (Source_Objects, "stringTypeReference")) or else
            V.Equal (Observed, Type_Node, Observed, O (Source_Objects, "bytesTypeReference")) or else
            V.Equal (Observed, Type_Node, Observed, O (Source_Objects, "listTypeReference")) or else
            V.Equal (Observed, Type_Node, Observed, O (Source_Objects, "tupleTypeReference")) or else
            V.Equal (Observed, Type_Node, Observed, O (Source_Objects, "dictionaryTypeReference")) or else
            V.Equal (Observed, Type_Node, Observed, O (Source_Objects, "noneTypeReference")));
         function Archive_Equal (Source : V.Node; Left, Right : String) return Boolean is
            L_Value : constant B.Decoded := Raw_Bytes (Observed, O (Source, Left));
            R_Value : constant B.Decoded := Raw_Bytes (Observed, O (Source, Right));
         begin
            return L_Value.Valid and then R_Value.Valid and then L_Value.Data = R_Value.Data;
         end Archive_Equal;
         function Source_Link (Name : String) return Boolean is
            Stage : constant E.Span := F (Capture, Name);
            Source : constant V.Node := Protocol_Source (Name);
            Is_Lookup : constant Boolean := Name in
              "ceilingHitLookup1" | "ceilingOomLookup1" | "ceilingHitLookup2" |
              "observedStateComparison" | "ceilingEvidenceNoneLookup" | "ceilingReasonLookup";
            Is_Kind : constant Boolean := Name in
              "launchComparison" | "supervisedComparison" | "indeterminateComparison";
            Key_Types : constant V.Node := O (Source, "storageKeyTypeReferences");
            Plain_Keys : Boolean := Key_Types.Form = V.Array_Value;
         begin
            if Stage.Length = 0 then return Source.Form = V.Missing; end if;
            if Source.Form /= V.Object_Value or else
              not Match (O (Source, "leftReference"), F (Stage, "leftReference")) or else
              not Match (O (Source, "leftTypeReference"), F (Stage, "leftTypeReference")) then return False; end if;
            if Is_Kind and then
              (not Match (O (Source, "sourceReference"), F (Stage, "sourceReference")) or else
               not Match (O (Source, "sourceTypeReference"), F (Stage, "sourceTypeReference"))) then return False; end if;
            if Name = "ceilingEvidenceNoneLookup" then
               if not Match (O (Source, "lookupReference"), F (Stage, "returnedReference")) or else
                 not Match (O (Source, "lookupTypeReference"), F (Stage, "returnedTypeReference")) then return False; end if;
            elsif not Match (O (Source, "returnedReference"), F (Stage, "returnedReference")) or else
              not Match (O (Source, "returnedTypeReference"), F (Stage, "returnedTypeReference")) then return False;
            end if;
            if Is_Lookup and then Name not in "observedStateComparison" | "ceilingEvidenceNoneLookup" then
               if not V.Equal (Observed, O (Source, "lookupReference"), Observed, O (Source, "returnedReference")) or else
                 not V.Equal (Observed, O (Source, "lookupTypeReference"), Observed, O (Source, "returnedTypeReference")) or else
                 (Exact_Builtin (O (Source, "lookupTypeReference")) and then
                  not Archive_Equal (Source, "lookupArchive", "returnedArchive")) then return False; end if;
            end if;
            if Name in "observedStateComparison" | "ceilingEvidenceNoneLookup" then
               if T (F (F (Stage, "lookupValue"), "profile"), "builtin-v1") then
                  if not Archive_Matches (O (Source, "lookupArchive"), F (F (Stage, "lookupValue"), "value")) then return False; end if;
               elsif not Match (O (Source, "lookupReference"), F (F (Stage, "lookupValue"), "reference")) or else
                 not Match (O (Source, "lookupTypeReference"), F (F (Stage, "lookupValue"), "typeReference")) then return False;
               end if;
            end if;
            for I in 1 .. V.Count (Observed, Key_Types) loop
               Plain_Keys := Plain_Keys and then V.Equal
                 (Observed, V.Element (Observed, Key_Types, I), Observed, O (Source_Objects, "stringTypeReference"));
            end loop;
            if (Is_Lookup or else Is_Kind) and then Plain_Keys and then
              V.Equal (Observed, O (Source, "sourceTypeReference"), Observed, O (Source_Objects, "dictionaryTypeReference")) then
               if Is_Kind then
                  return V.Equal (Observed, O (Source, "keyStorageReference"), Observed, O (Source, "leftReference")) and then
                    V.Equal (Observed, O (Source, "keyStorageTypeReference"), Observed, O (Source, "leftTypeReference")) and then
                    (not Exact_Builtin (O (Source, "leftTypeReference")) or else
                     Archive_Equal (Source, "keyStorageArchive", "leftBeforeArchive"));
               end if;
               return V.Equal (Observed, O (Source, "keyStorageReference"), Observed, O (Source, "lookupReference")) and then
                 V.Equal (Observed, O (Source, "keyStorageTypeReference"), Observed, O (Source, "lookupTypeReference")) and then
                 (not Exact_Builtin (O (Source, "lookupTypeReference")) or else
                  Archive_Equal (Source, "keyStorageArchive", "lookupArchive"));
            end if;
            return True;
         end Source_Link;
         function Kind_Stage (Name, Operand : String; Not_Equal : Boolean) return Boolean is
            Stage : constant E.Span := F (Capture, Name);
            Source : constant V.Node := Protocol_Source (Name);
            Bytes : constant B.Decoded := Raw_Bytes (Observed, O (Source, "leftBeforeArchive"));
            Original : constant E.Bytes := JSON_Bytes (Bytes.Data);
            Root : constant E.Span := (1, Original'Length);
            Value : constant Boolean :=
              (if Not_Equal then not L.Text_Is (Original, Root, Operand) else L.Text_Is (Original, Root, Operand));
         begin
            if Stage.Length = 0 then return True; end if;
            if not Source_Link (Name) then return False; end if;
            if not Identity ("stringTypeReference", F (Stage, "leftTypeReference")) then
               return True; -- complete original foreign protocol, not builtin eq
            end if;
            return Bytes.Valid and then L.Is_True (Data, Stage, "returnedTruth") = Value;
         end Kind_Stage;
         function Builtin_Dict_Stage (Name, Key : String; Comparison : Boolean := False) return Boolean is
            Stage : constant E.Span := F (Capture, Name);
            Source : constant V.Node := Protocol_Source (Name);
            Bytes : constant B.Decoded := Raw_Bytes (Observed, O (Source, "lookupArchive"));
            Original : constant E.Bytes := JSON_Bytes (Bytes.Data);
            Root : constant E.Span := (1, Original'Length);
            Truth : constant Boolean :=
              (if Comparison then not L.Text_Is (Original, Root, "OBSERVED") else L.Truth (Original, Root));
         begin
            if Stage.Length = 0 then return True; end if;
            if not T (F (Stage, "key"), Key) then return False; end if;
            if not Source_Link (Name) then return False; end if;
            if not Identity ("dictionaryTypeReference", F (Stage, "leftTypeReference")) or else
              not Exact_Builtin (O (Source, "lookupTypeReference")) then
               return True; -- full retained subclass/custom protocol remains factual
            end if;
            if not Bytes.Valid or else L.Is_True (Data, Stage, "returnedTruth") /= Truth then return False; end if;
            if Comparison then
               return Identity ("booleanTypeReference", F (Stage, "returnedTypeReference")) and then
                 Identity ((if Truth then "trueReference" else "falseReference"), F (Stage, "returnedReference"));
            elsif E.Decode (Original, Root, E.Finalization).Form = E.Boolean_Value then
               return Identity ("booleanTypeReference", F (Stage, "returnedTypeReference")) and then
                 Identity ((if Truth then "trueReference" else "falseReference"), F (Stage, "returnedReference"));
            elsif E.Decode (Original, Root, E.Finalization).Form = E.Null_Value then
               return Identity ("noneTypeReference", F (Stage, "returnedTypeReference")) and then
                 Identity ("noneReference", F (Stage, "returnedReference"));
            end if;
            return True;
         end Builtin_Dict_Stage;
      begin
         if Source_Objects.Form /= V.Object_Value or else
           not Ref_Profile (Container, "resourceReference", "resourceTypeReference") or else
           not Ref_Profile (Kind_Source, "supervisionReference", "supervisionTypeReference") then return False; end if;
         if T (F (Observation, "profile"), "builtin-v1") then
            if not Archive_Matches (O (Source_Objects, "resourceObservationArchive"), F (Observation, "value")) then
               return False;
            end if;
         elsif not Ref_Profile (Observation, "resourceObservationReference", "resourceObservationTypeReference") then return False;
         end if;
         if T (F (Manager_Result, "profile"), "builtin-v1") then
            if not Archive_Matches (O (Source_Objects, "managerResultArchive"), F (Manager_Result, "value")) or else
              not Match (O (Source_Supervisor, "result"), F (Manager_Result, "value")) then return False; end if;
         else
            if not Ref_Profile (Manager_Result, "managerResultReference", "managerResultTypeReference") then return False; end if;
         end if;
         --  The full sealed runner decoder checks EACH actual get/eq/truth,
         --  repeated stage, returned object/type and source reference, operand,
         --  boundary publication, and materialization in original order. Kind
         --  is independently derived from raw supervisor events here, so its
         --  builtin string comparisons are also redecided, not copied flags.
         return Source_Link ("managerOomComparison1") and then Source_Link ("managerOomComparison2") and then
           Source_Link ("exitComparison") and then Source_Link ("ceilingEvidenceNoneLookup") and then
           Builtin_Dict_Stage ("ceilingReasonLookup", "ceilingFired") and then
           Builtin_Dict_Stage ("ceilingHitLookup1", "hitMemoryCeiling") and then
           Builtin_Dict_Stage ("ceilingOomLookup1", "oomKilled") and then
           Builtin_Dict_Stage ("ceilingHitLookup2", "hitMemoryCeiling") and then
           Builtin_Dict_Stage ("observedStateComparison", "state", True) and then
           Kind_Stage ("launchComparison", "LAUNCH_FAILED", False) and then
           Kind_Stage ("supervisedComparison", "SUPERVISED", True) and then
           Kind_Stage ("indeterminateComparison", "INDETERMINATE", False);
      end Protocol_Join;
      procedure Missing (Reason : Missing_Fact) is
      begin
         Joined := False;
         if Output.Missing in None | Terminal_Incomplete then Output.Missing := Reason; end if;
      end Missing;
   begin
      if Start.Form /= V.Object_Value or else Rows.Form /= V.Array_Value or else
        Result.Form /= V.Object_Value or else
        not V.Is_Text (Expected, X ("checkId"), "agent") or else
        not V.Nonempty_Text (Expected, X ("invocationId")) or else
        not V.Is_Text (Result_Record, R (Result, "id"), "agent") or else
        not V.Is_Text (Result_Record, R (Result, "origin"), "agent") or else
        not V.Is_Text (Result_Record, R (Result, "kind"), "build") or else
        not V.Is_Text (Result_Record, R (Result, "format"), "exit") or else
        not V.Is_True (Result_Record, R (Result, "required")) or else
        R (Result, "covers").Form /= V.Array_Value or else
        V.Count (Result_Record, R (Result, "covers")) /= 0 or else
        R (Result, "argv").Form /= V.Array_Value then
         Missing (Source_Mismatch); return Output;
      end if;
      if not T (F (Capture, "schema"), "worldline.runner-terminal-v2") or else
        not T (F (Capture, "mode"), "runner-owner-v1") or else
        not V.Is_Text (Native, V.Field (Native, Decision, "status"), "COMPLETE") then
         Missing (Terminal_Incomplete);
      end if;
      --  The typed decision is the only production status/ceiling authority.
      --  Keep independently obtained known negative outcomes even if an old
      --  acquisition lacks one particular raw qualification premise.
      if V.Is_Text (Native, V.Field (Native, Decision, "agentStatus"), "PASS") then Output.Status := 1;
      elsif V.Is_Text (Native, V.Field (Native, Decision, "agentStatus"), "FAIL") then Output.Status := 2;
      end if;
      if Created.Form /= V.Object_Value then Missing (Job_Source);
      elsif not V.Nonempty_Text (Observed, O (Created, "jobId")) or else
        not V.Is_Text (Observed, O (Created, "state"), "STARTING") or else
        not V.Equal (Observed, O (Created, "worldInstance"), Expected, X ("worldInstance")) then Missing (Source_Mismatch);
      end if;
      if Association.Form /= V.Object_Value then Missing (Launch_Source);
      elsif not V.Equal (Observed, O (Created, "jobId"), Observed, O (Association, "jobId")) or else
        not V.Equal (Observed, O (Association, "worldInstance"), Expected, X ("worldInstance")) or else
        not Worldline.Manager_Resource_Lifecycle.Unit_Valid (Unit) or else
        O (Association, "launchedAtUs").Form /= V.Integer_Value then Missing (Source_Mismatch);
      end if;
      if Wait.Form /= V.Object_Value then Missing (Wait_Source);
      elsif not Wait_Join then Missing (Source_Mismatch);
      end if;
      if Membership.Form /= V.Object_Value then Missing (Stop_Membership_Source);
      elsif not Same_Unit (Membership) or else
        not V.Equal (Observed, O (Membership, "job"), Observed, O (Created, "jobId")) or else
        not Match (Membership, F (Capture, "stopMembership")) or else
        not Match (O (Membership, "job"), F (F (F (Capture, "stopMembership"), "cancelled"), "requested")) or else
        not Match (O (Membership, "job"), F (F (F (Capture, "stopMembership"), "timedOut"), "requested")) then
         Missing (Source_Mismatch);
      end if;
      if Manager.Form /= V.Object_Value or else not Same_Unit (Manager) then Missing (Materialization_Source);
      else
         -- Capture is the unchanged complete original archive, whose source
         -- correspondence is authenticated by the enclosing custody owner.
         -- Do not substitute whole projected JSON equality (lossy bytes/NaN).
         if not Archive_Matches (O (Manager, "terminalBytes"), Capture) or else
           not V.Equal (Observed, O (Manager, "exitCode"), Observed, O (Wait, "returncode")) or else
           not V.Equal (Observed, O (Manager, "exitCode"), Result_Record, R (Result, "exitCode")) or else
           not V.Equal (Observed, Supervisor, Result_Record, R (Result, "supervision")) or else
           not V.Equal (Observed, Resources, Result_Record, R (Result, "resources")) then Missing (Source_Mismatch); end if;
         declare
            Raw_Supervisor : constant Supervisor_Facts := Supervisor_Decide
              (Observed, "agent-supervision-acquisition", Unit,
               Retained_Since,
               V.Slice (Observed, O (Wait, "returncode")), V.Slice (Observed, Source_Supervisor),
               Stopped => L.Cancellation_Membership (Data, F (F (Capture, "stopMembership"), "cancelled")) or else
                          L.Cancellation_Membership (Data, F (F (Capture, "stopMembership"), "timedOut")),
               Reader_UID => V.Slice (Expected, X ("readerUid")));
         begin
            Output.Supervisor := Raw_Supervisor.Kind;
            Output.Stopped := Raw_Supervisor.Stopped;
            if Output.Status = 0 and then Raw_Supervisor.Valid and then
              not V.Is_Text (Observed, O (Supervisor, "kind"), "LAUNCH_FAILED") and then
              (Raw_Supervisor.Kind /= 1 or else
               (V.Is_True (Observed, O (Wait, "waitReturnObserved")) and then
                not Wait_Zero)) then
               -- A genuinely retained known failure does not need invented
               -- empty cancellation/timer sets to remain a failure. Missing
               -- exact cause still prevents complete qualification.
               Output.Status := 2;
            end if;
            if not Raw_Supervisor.Valid then Missing (Supervisor_Source); end if;
         end;
         -- D27 uses the actual final resource field, after original callbacks;
         -- native publications are independently checked against their operands.
         if V.Is_True (Observed, O (Resources, "ceilingFired")) then Output.Stopped := True;
         elsif not V.Is_False (Observed, O (Resources, "ceilingFired")) then Output.Supervisor := 3;
         end if;
         declare
            Captured : constant B.Decoded := Raw_Bytes (Observed, O (Manager, "resourceContainerFinalArchive"));
            Final_Arena : constant E.Bytes := JSON_Bytes (Captured.Data);
            Final_Root : constant E.Span := (1, Final_Arena'Length);
            Fired : constant E.Span := L.Field (Final_Arena, Final_Root, "ceilingFired");
            Item : constant V.Node := O (Resources, "ceilingFired");
            Evidence : constant E.Span := L.Field (Final_Arena, Final_Root, "ceilingEvidence");
            Evidence_Item : constant V.Node := O (Resources, "ceilingEvidence");
         begin
            if not Captured.Valid or else Item.Form = V.Missing or else
              not Worldline.Raw_JSON.Ordinary_JSON_Finalization_Matches
                (JSON_Arena, Final_Arena, (P.Count (Item.First), P.Count (Item.Last - Item.First + 1)), Fired) or else
              Evidence_Item.Form = V.Missing or else
              not Worldline.Raw_JSON.Ordinary_JSON_Finalization_Matches
                (JSON_Arena, Final_Arena,
                 (P.Count (Evidence_Item.First), P.Count (Evidence_Item.Last - Evidence_Item.First + 1)), Evidence) then
               Missing (Source_Mismatch);
            end if;
         end;
         if T (F (F (Capture, "exitCode"), "profile"), "builtin-v1") and then
           not Supervisor_Exit_Join then Missing (Supervisor_Source); end if;
         if not Resource_Join then Missing (Resource_Source); end if;
         if not Protocol_Join then Missing (Protocol_Source); end if;
         if not Match (O (Manager, "resultReference"), F (F (Capture, "prepareAgentResult"), "reference")) or else
           not Match (O (Manager, "resultTypeReference"), F (F (Capture, "prepareAgentResult"), "typeReference")) or else
           not Match (O (Manager, "prefixReference"), F (F (Capture, "prepareAgentPrefix"), "reference")) or else
           not Match (O (Manager, "prefixTypeReference"), F (F (Capture, "prepareAgentPrefix"), "typeReference")) then
            Missing (Materialization_Source);
         end if;
      end if;
      if Output.Status /= 0 and then not V.Is_Text (Result_Record, R (Result, "status"),
        (if Output.Status = 1 then "PASS" else "FAIL")) then Missing (Source_Mismatch); end if;
      --  Original agent result construction has no resultChannel. Stage is
      --  ABSENT even for negative waits, cancellation and a manager stop;
      --  resultChannel-derived private harness stages are NOT agent stages.
      if not Null_Or_Missing (R (Result, "resultChannel")) then Missing (Source_Mismatch); end if;
      Output.Stage := 0;
      Output.Valid := Joined;
      return Output;
   end Decide;
end Worldline.Evaluation_Agent_Native;
