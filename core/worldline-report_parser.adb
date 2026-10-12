with SPARK.Big_Integers;
with Evaluation_Pending;
with Exact_Decimal;
with Decimal_Binary64;

package body Worldline.Report_Parser with SPARK_Mode is
   use SPARK.Big_Integers;
   package P renames Evaluation_Pending;
   use type P.Count;
   subtype CP is Natural range 0 .. 16#10FFFF#;
   type Code_Array is array (Positive range <>) of CP;
   type Decoded_Text (Capacity : Natural) is record
      Valid : Boolean := True;
      Length : Natural := 0;
      Data : Code_Array (1 .. Capacity);
   end record;

   function Decode (Bytes : String; Replace : Boolean := False) return Decoded_Text
     with Global => null,
       Post => Decode'Result.Capacity = Bytes'Length and then Decode'Result.Length <= Bytes'Length
   is
      R : Decoded_Text (Bytes'Length) := (Bytes'Length, True, 0, (others => 0));
      O : Natural := 0;
      C, Width, Minimum : Natural;
      Valid : Boolean;
      function Byte (At_Offset : Natural) return Natural is
        (Character'Pos (Bytes (Bytes'First + At_Offset)))
        with Pre => At_Offset < Bytes'Length;
   begin
      while O < Bytes'Length loop
         pragma Loop_Invariant (R.Length <= O);
         pragma Loop_Variant (Decreases => Bytes'Length - O);
         C := Byte (O); Width := 1; Minimum := 0;
         if C < 128 then null;
         elsif C in 16#C2# .. 16#DF# then Width := 2; C := C mod 32; Minimum := 128;
         elsif C in 16#E0# .. 16#EF# then Width := 3; C := C mod 16; Minimum := 2048;
         elsif C in 16#F0# .. 16#F4# then Width := 4; C := C mod 8; Minimum := 65536;
         else Width := 0;
         end if;
         Valid := Width > 0 and then Width <= Bytes'Length - O;
         if Valid and then Width > 1 then
            for K in 1 .. Width - 1 loop
               pragma Loop_Invariant (C < (if K = 1 then 32 elsif K = 2 then 2048 elsif K = 3 then 131072 else 8388608));
               if Byte (O + K) not in 128 .. 191 then Valid := False; exit; end if;
               C := C * 64 + Byte (O + K) mod 64;
            end loop;
         end if;
         Valid := Valid and then C >= Minimum and then C <= 16#10FFFF#
           and then C not in 16#D800# .. 16#DFFF#;
         if not Valid then
            if not Replace then R.Valid := False; return R; end if;
            C := 16#FFFD#; Width := 1;
            -- Python's replacement codec consumes a valid incomplete prefix,
            -- but leaves an offending non-continuation for the next iteration.
            if Byte (O) in 16#C2# .. 16#F4# then
               while Width < Bytes'Length - O and then Width < 4
                 and then Byte (O + Width) in 128 .. 191
               loop
                  pragma Loop_Invariant (Width in 1 .. 3 and then Width <= Bytes'Length - O);
                  pragma Loop_Variant (Increases => Width);
                  Width := Width + 1;
               end loop;
            end if;
         end if;
         R.Length := R.Length + 1; R.Data (R.Length) := C; O := O + Width;
      end loop;
      return R;
   end Decode;

   function Is_White (C : CP) return Boolean is
     (C in 9 .. 13 or else C in 16#1C# .. 16#20# or else C = 16#85#
      or else C = 16#A0# or else C = 16#1680# or else C in 16#2000# .. 16#200A#
      or else C = 16#2028# or else C = 16#2029# or else C = 16#202F#
      or else C = 16#205F# or else C = 16#3000#);
   function XML_White (C : CP) return Boolean is (C = 32 or else C = 9 or else C = 10 or else C = 13);
   function XML_Char (C : CP) return Boolean is
     (C = 9 or else C = 10 or else C = 13 or else C in 32 .. 16#D7FF#
      or else C in 16#E000# .. 16#FFFD# or else C in 16#10000# .. 16#10FFFF#);
   function Line_End (C : CP) return Boolean is
     (C in 10 .. 13 or else C in 16#1C# .. 16#1E# or else C = 16#85#
      or else C = 16#2028# or else C = 16#2029#);

   function Decimal_Digit (C : CP) return Integer is
      -- Unicode16 extracted/DerivedNumericType.txt, Decimal ranges (2024-04-30).
      Zeros : constant Code_Array :=
        (16#30#,16#660#,16#6F0#,16#7C0#,16#966#,16#9E6#,16#A66#,16#AE6#,
         16#B66#,16#BE6#,16#C66#,16#CE6#,16#D66#,16#DE6#,16#E50#,16#ED0#,
         16#F20#,16#1040#,16#1090#,16#17E0#,16#1810#,16#1946#,16#19D0#,
         16#1A80#,16#1A90#,16#1B50#,16#1BB0#,16#1C40#,16#1C50#,16#A620#,
         16#A8D0#,16#A900#,16#A9D0#,16#A9F0#,16#AA50#,16#ABF0#,16#FF10#,
         16#104A0#,16#10D30#,16#10D40#,16#11066#,16#110F0#,16#11136#,
         16#111D0#,16#112F0#,16#11450#,16#114D0#,16#11650#,16#116C0#,
         16#116D0#,16#116DA#,16#11730#,16#118E0#,16#11950#,16#11BF0#,
         16#11C50#,16#11D50#,16#11DA0#,16#11F50#,16#16130#,
         16#16A60#,16#16AC0#,16#16B50#,16#16D70#,16#1CCF0#,16#1D7CE#,16#1D7D8#,16#1D7E2#,
         16#1D7EC#,16#1D7F6#,16#1E140#,16#1E2F0#,16#1E4F0#,16#1E5F1#,16#1E950#,16#1FBF0#);
   begin
      for Z of Zeros loop
         if C >= Z and then C - Z <= 9 then return Integer (C - Z); end if;
      end loop;
      return -1;
   end Decimal_Digit;

   type Integer_Result is record
      Valid : Boolean := False;
      Value : Big_Integer := To_Big_Integer (0);
   end record;
   function Py_Integer (D : Code_Array; First, Last : Natural) return Integer_Result
     with Pre => Last < Natural'Last
   is
      R : Integer_Result;
      A : Natural := First;
      B : Natural := Last;
      Negative, Had_Digit, Underscore : Boolean := False;
      Digit : Integer;
   begin
      if A = 0 or else A > B or else A not in D'Range or else B not in D'Range then return R; end if;
      while A <= B and then Is_White (D (A)) loop
         pragma Loop_Invariant (A >= D'First);
         pragma Loop_Variant (Increases => A);
         A := A + 1;
      end loop;
      while B >= A and then Is_White (D (B)) loop
         pragma Loop_Invariant (B <= Last);
         pragma Loop_Variant (Decreases => B);
         B := B - 1;
      end loop;
      if A > B then return R; end if;
      if D (A) = 43 or else D (A) = 45 then Negative := D (A) = 45; A := A + 1; end if;
      while A <= B loop
         pragma Loop_Invariant (A >= D'First);
         pragma Loop_Variant (Decreases => B - A + 1);
         Digit := Decimal_Digit (D (A));
         if Digit >= 0 then
            R.Value := R.Value * To_Big_Integer (10) + To_Big_Integer (Digit);
            Had_Digit := True; Underscore := False;
         elsif D (A) = 95 and then Had_Digit and then not Underscore then Underscore := True;
         else return R;
         end if;
         A := A + 1;
      end loop;
      R.Valid := Had_Digit and then not Underscore;
      if Negative then R.Value := -R.Value; end if;
      return R;
   end Py_Integer;

   function Image (N : Big_Integer) return String
     with Post => Image'Result'First = 1
   is
      S : constant String := To_String (N);
   begin
      for First in S'Range loop
         if S (First) /= ' ' then
            declare
               R : constant String (1 .. S'Last - First + 1) := S (First .. S'Last);
            begin
               return R;
            end;
         end if;
      end loop;
      return "";
   end Image;
   function Status_JSON (Good : Boolean) return String is
     (if Good then "PASS" else "FAIL");
   function Answer (Good : Boolean; Class : Classification; Fields : String := "") return Parsed_Report
     with Pre => Fields'Length <= Natural'Last - 17,
       Post => Answer'Result.Status = (if Good then Pass else Fail) and then Answer'Result.Class = Class
   is
      S : constant String := "{""status"":""" & Status_JSON (Good) & """" & Fields & "}";
   begin
      return (S'Length, (if Good then Pass else Fail), Class, S);
   end Answer;
   function Reject (Class : Classification; Reason : String; Null_Field : String := "") return Parsed_Report
     with Pre => Reason'Length <= Natural'Last / 4 and then Null_Field'Length <= Natural'Last / 4,
       Post => Reject'Result.Status = Fail and then Reject'Result.Class = Class
   is
   begin
      return Answer (False, Class, ",""reason"":""" & Reason & """" &
        (if Null_Field = "" then "" else ",""" & Null_Field & """:null"));
   end Reject;

   function GNAT_Report (Payload : String; Exit_Zero : Boolean) return Parsed_Report
     with Post => GNAT_Report'Result.Status /= Unsupported
   is
      T : constant Decoded_Text := Decode (Payload, True);
      Clean : Code_Array (1 .. T.Length) := (others => 0);
      Start, Stop : Natural := 1;
      O, K, Used : Natural;
      Found : Boolean := False;
      type Count_Array is array (1 .. 5) of Big_Integer;
      Counts : Count_Array := (others => To_Big_Integer (0));
      Fields : Natural := 0;
      type Token_Bounds is array (1 .. 6) of Natural;
      Starts, Stops : Token_Bounds := (others => 0);
   begin
      while Start <= T.Length loop
         pragma Loop_Invariant (Start >= 1);
         pragma Loop_Variant (Increases => Start);
         Stop := Start;
         while Stop <= T.Length and then not Line_End (T.Data (Stop)) loop
            pragma Loop_Invariant (Stop in Start .. T.Length);
            pragma Loop_Variant (Increases => Stop);
            Stop := Stop + 1;
         end loop;
         if Stop - Start >= 5 and then T.Data (Start .. Start + 4) = Code_Array'(84,111,116,97,108) then Found := True; exit; end if;
         Start := Stop + 1;
         if Stop < T.Length and then T.Data (Stop) = 13 and then T.Data (Stop + 1) = 10 then Start := Start + 1; end if;
      end loop;
      if not Found then return Reject (Missing_Total, "gnatprove Total row is missing", "total"); end if;
      O := Start; Used := 0;
      while O < Stop loop
         pragma Loop_Invariant (O in Start .. Stop and then Used <= O - Start);
         pragma Loop_Variant (Decreases => Stop - O);
         if T.Data (O) = 40 then
            K := O + 1;
            while K < Stop and then T.Data (K) in 48 .. 57 loop
               pragma Loop_Invariant (K in O + 1 .. Stop);
               pragma Loop_Variant (Increases => K);
               K := K + 1;
            end loop;
            if K > O + 1 and then K < Stop - 1 and then T.Data (K) = 37 and then T.Data (K + 1) = 41 then
               O := K + 2;
            else Used := Used + 1; Clean (Used) := T.Data (O); O := O + 1;
            end if;
         else Used := Used + 1; Clean (Used) := T.Data (O); O := O + 1;
         end if;
      end loop;
      O := 1;
      while O <= Used loop
         pragma Loop_Invariant (O >= 1 and then Fields <= 6);
         pragma Loop_Invariant (for all F in 1 .. Fields => Starts (F) in 1 .. Used and then Stops (F) in Starts (F) .. Used);
         pragma Loop_Variant (Increases => O);
         while O <= Used and then Is_White (Clean (O)) loop
            pragma Loop_Invariant (O >= O'Loop_Entry);
            pragma Loop_Variant (Increases => O);
            O := O + 1;
         end loop;
         exit when O > Used;
         K := O;
         while K <= Used and then not Is_White (Clean (K)) loop
            pragma Loop_Invariant (K in O .. Used);
            pragma Loop_Variant (Increases => K);
            K := K + 1;
         end loop;
         Fields := Fields + 1;
         if Fields > 6 then return Reject (Invalid_Total_Row, "gnatprove Total row is invalid", "total"); end if;
         Starts (Fields) := O; Stops (Fields) := K - 1;
         O := K;
      end loop;
      if Fields /= 6 then return Reject (Invalid_Total_Row, "gnatprove Total row is invalid", "total"); end if;
      for Field in 2 .. 6 loop
         O := Starts (Field); K := Stops (Field);
         if K = O and then Clean (O) = 46 then Counts (Field - 1) := To_Big_Integer (0);
         else
            declare N : constant Integer_Result := Py_Integer (Clean,O,K); begin
               if not N.Valid then return Reject (Invalid_Total_Counts,"gnatprove Total counts are invalid","total"); end if;
               Counts (Field - 1) := N.Value;
            end;
         end if;
      end loop;
      if Counts (1) <= 0 or else (for some N of Counts => N < 0)
        or else Counts (2) + Counts (3) + Counts (4) + Counts (5) /= Counts (1)
      then return Reject (Inconsistent_Counts, "gnatprove Total counts are empty or inconsistent", "total"); end if;
      return Answer (Exit_Zero and then Counts (4) = 0 and then Counts (5) = 0, Parsed,
        ",""total"":" & Image (Counts (1)) & ",""justified"":" & Image (Counts (4)) & ",""unproved"":" & Image (Counts (5)));
   end GNAT_Report;

   function Decode_XML (Bytes : String) return Decoded_Text
     with Post => Decode_XML'Result.Capacity = Bytes'Length and then Decode_XML'Result.Length <= Bytes'Length
   is
      R : Decoded_Text (Bytes'Length) := (Bytes'Length,True,0,(others => 0));
      Little, UTF16, Latin, ASCII_Only : Boolean := False;
      Offset : Natural := 0;
      C, Second : Natural;
      function Byte (At_Offset : Natural) return Natural is
        (Character'Pos (Bytes (Bytes'First + At_Offset)))
        with Pre => At_Offset < Bytes'Length;
      function Unit (At_Offset : Natural) return Natural is
        (if Little then Byte (At_Offset) + 256 * Byte (At_Offset + 1)
         else 256 * Byte (At_Offset) + Byte (At_Offset + 1))
        with Pre => At_Offset < Bytes'Length - 1;
   begin
      if Bytes'Length >= 2 then
         if Byte (0) = 255 and then Byte (1) = 254 then UTF16 := True; Little := True; Offset := 2;
         elsif Byte (0) = 254 and then Byte (1) = 255 then UTF16 := True; Offset := 2;
         elsif Bytes'Length >= 4 then
            if Byte (0) = 60 and then Byte (1) = 0 then UTF16 := True; Little := True;
            elsif Byte (0) = 0 and then Byte (1) = 60 then UTF16 := True;
            end if;
         end if;
      end if;
      if UTF16 then
         while Offset < Bytes'Length loop
            pragma Loop_Invariant (R.Length <= Offset / 2);
            pragma Loop_Variant (Increases => Offset);
            if Bytes'Length - Offset < 2 then R.Valid := False; return R; end if;
            C := Unit (Offset); Offset := Offset + 2;
            if C in 16#D800# .. 16#DBFF# then
               if Bytes'Length - Offset < 2 then R.Valid := False; return R; end if;
               Second := Unit (Offset); Offset := Offset + 2;
               if Second not in 16#DC00# .. 16#DFFF# then R.Valid := False; return R; end if;
               C := 65536 + (C - 16#D800#) * 1024 + Second - 16#DC00#;
            elsif C in 16#DC00# .. 16#DFFF# then R.Valid := False; return R;
            end if;
            R.Length := R.Length + 1; R.Data (R.Length) := C;
         end loop;
         return R;
      end if;
      -- Encoding declaration selection precedes Unicode decoding. The ordinary
      -- owned report lane is UTF-8; XML's original Latin-1/ASCII declarations
      -- also retain their actual byte interpretation, not merely a label.
      if Bytes'Length >= 5 and then Bytes (Bytes'First .. Bytes'First + 4) = "<?xml" then
         Offset := 5;
         while Offset < Bytes'Length and then Byte (Offset) /= 62 loop
            pragma Loop_Variant (Increases => Offset);
            if Bytes'Length - Offset >= 8 and then Bytes (Bytes'First + Offset .. Bytes'First + Offset + 7) = "encoding" then
               Offset := Offset + 8;
               while Offset < Bytes'Length and then Byte (Offset) in 9 .. 13 | 32 loop
                  pragma Loop_Variant (Increases => Offset);
                  Offset := Offset + 1;
               end loop;
               if Offset < Bytes'Length and then Byte (Offset) = 61 then
                  Offset := Offset + 1;
                  while Offset < Bytes'Length and then Byte (Offset) in 9 .. 13 | 32 loop
                     pragma Loop_Variant (Increases => Offset);
                     Offset := Offset + 1;
                  end loop;
                  if Offset < Bytes'Length and then Byte (Offset) in 34 | 39 then
                     declare
                        Q : constant Natural := Byte (Offset);
                        First : constant Natural := Offset + 1;
                     begin
                        Offset := First;
                        while Offset < Bytes'Length and then Byte (Offset) /= Q loop
                           pragma Loop_Invariant (Offset >= First);
                           pragma Loop_Variant (Increases => Offset);
                           Offset := Offset + 1;
                        end loop;
                        declare
                           Name : String := (if Offset > First then Bytes (Bytes'First + First .. Bytes'First + (Offset - 1)) else "");
                        begin
                           for K in Name'Range loop
                              if Name (K) in 'A' .. 'Z' then Name (K) := Character'Val (Character'Pos (Name (K)) + 32); end if;
                           end loop;
                           Latin := Name = "iso-8859-1" or else Name = "iso8859-1" or else Name = "latin1" or else Name = "latin-1";
                           ASCII_Only := Name = "ascii" or else Name = "us-ascii";
                           if Name = "utf-16" or else Name = "utf-16le" or else Name = "utf-16be" then R.Valid := False; return R; end if;
                        end;
                     end;
                  end if;
               end if;
               exit;
            end if;
            Offset := Offset + 1;
         end loop;
      end if;
      if Latin then
         for K in Bytes'Range loop
            pragma Loop_Invariant (R.Length = K - Bytes'First);
            R.Length := R.Length + 1; R.Data (R.Length) := Character'Pos (Bytes (K));
         end loop;
         return R;
      end if;
      if ASCII_Only and then (for some B of Bytes => Character'Pos (B) > 127) then R.Valid := False; return R; end if;
      return Decode (Bytes);
   end Decode_XML;

   function JUnit_Report (Payload : String; Exit_Zero : Boolean) return Parsed_Report
     with Post => JUnit_Report'Result.Status /= Unsupported
   is
      T : constant Decoded_Text := Decode_XML (Payload);
      O : Natural := 1;
      Depth, Attributes, Values_Used : Natural := 0;
      Root_Seen, Root_Done, Root_Single : Boolean := False;
      Suite_Count : Natural := 0;
      type Totals_Array is array (1 .. 4) of Big_Integer;
      Totals : Totals_Array := (others => To_Big_Integer (0));
      type Element is record
         First, Last, Attr_Base : Natural := 0;
      end record;
      type Attribute is record
         First, Last, Value_First, Value_Last : Natural := 0;
         Namespace : Boolean := False;
      end record;
      type Element_Array is array (Positive range <>) of Element;
      type Attribute_Array is array (Positive range <>) of Attribute;
      Stack : Element_Array (1 .. T.Length) := (others => (others => 0));
      Attr : Attribute_Array (1 .. T.Length) := (others => (0,0,0,0,False));
      Values : Code_Array (1 .. T.Length) := (others => 0);
      Bad : Boolean := False;

      -- Proof-only descriptions of the parsed element stack and attribute table.
      function Stack_OK (Count : Natural) return Boolean is
        (Count <= T.Length and then
         (for all I in 1 .. Count =>
            Stack (I).First >= 1 and then Stack (I).Last >= Stack (I).First and then Stack (I).Last < O
            and then Stack (I).Attr_Base <= Attributes
            and then (for all J in I .. Count => Stack (I).Attr_Base <= Stack (J).Attr_Base)))
        with Ghost;
      function Attrs_OK (Count : Natural) return Boolean is
        (Count <= T.Length and then Values_Used <= T.Length and then
         (for all I in 1 .. Count =>
            Attr (I).First >= 1 and then Attr (I).Last >= Attr (I).First and then Attr (I).Last <= T.Length
            and then Attr (I).Value_First >= 1 and then Attr (I).Value_Last <= Values_Used
            and then Attr (I).Value_Last >= Attr (I).Value_First - 1))
        with Ghost;

      function Match (At_Offset : Natural; Text : String; Casefold : Boolean := False) return Boolean
        with Post => (if Match'Result then At_Offset in 1 .. T.Length and then Text'Length <= T.Length - At_Offset + 1)
      is
         C, Expected : Natural;
      begin
         if At_Offset = 0 or else At_Offset > T.Length or else Text'Length > T.Length - At_Offset + 1 then return False; end if;
         for K in 0 .. Text'Length - 1 loop
            C := T.Data (At_Offset + K); Expected := Character'Pos (Text (Text'First + K));
            if Casefold then
               if C in 97 .. 122 then C := C - 32; end if;
               if Expected in 97 .. 122 then Expected := Expected - 32; end if;
            end if;
            if C /= Expected then return False; end if;
         end loop;
         return True;
      end Match;
      function Name_Start (C : CP) return Boolean is
        (C = 58 or else C = 95 or else C in 65 .. 90 or else C in 97 .. 122
         or else C in 16#C0# .. 16#D6# or else C in 16#D8# .. 16#F6#
         or else C in 16#F8# .. 16#2FF# or else C in 16#370# .. 16#37D#
         or else C in 16#37F# .. 16#1FFF# or else C in 16#200C# .. 16#200D#
         or else C in 16#2070# .. 16#218F# or else C in 16#2C00# .. 16#2FEF#
         or else C in 16#3001# .. 16#D7FF# or else C in 16#F900# .. 16#FDCF#
         or else C in 16#FDF0# .. 16#FFFD# or else C in 16#10000# .. 16#EFFFF#);
      function Name_Char (C : CP) return Boolean is
        (Name_Start (C) or else C in 48 .. 57 or else C = 45 or else C = 46
         or else C = 16#B7# or else C in 16#300# .. 16#36F# or else C in 16#203F# .. 16#2040#);
      procedure White
        with Pre => O >= 1 and then O - 1 <= T.Length,
          Post => O >= O'Old and then O - 1 <= T.Length
      is
      begin
         while O <= T.Length and then XML_White (T.Data (O)) loop
            pragma Loop_Invariant (O >= O'Loop_Entry and then O <= T.Length);
            pragma Loop_Variant (Increases => O);
            O := O + 1;
         end loop;
      end White;
      procedure Name (First, Last : out Natural)
        with Pre => O >= 1 and then O - 1 <= T.Length,
          Post => O >= O'Old and then O - 1 <= T.Length
            and then (if not Bad then First = O'Old and then Last = O - 1 and then Last >= First)
      is
      begin
         First := O; Last := O;
         if O > T.Length or else not Name_Start (T.Data (O)) then Bad := True; return; end if;
         O := O + 1;
         while O <= T.Length and then Name_Char (T.Data (O)) loop
            pragma Loop_Invariant (O > First and then O <= T.Length);
            pragma Loop_Variant (Increases => O);
            O := O + 1;
         end loop;
         Last := O - 1;
      end Name;
      function Equal_Name (F, L, G, H : Natural) return Boolean is
        (L >= F and then H >= G and then L - F = H - G and then T.Data (F .. L) = T.Data (G .. H))
        with Pre => (if L >= F and then H >= G then F >= 1 and then L <= T.Length and then G >= 1 and then H <= T.Length);
      function Exact_Name (F, L : Natural; Text : String) return Boolean is
        (L >= F and then L - F + 1 = Text'Length and then Match (F, Text))
        with Pre => F >= 1;
      procedure Entity (Value : out CP)
        with Pre => O >= 1 and then O <= T.Length,
          Post => O > O'Old and then O - 1 <= T.Length
      is
         Start : Natural;
         C : Natural := 0;
         Base, Digit : Natural;
      begin
         Value := 0; O := O + 1; Start := O;
         if O <= T.Length and then T.Data (O) = 35 then
            O := O + 1; Base := 10;
            if O <= T.Length and then T.Data (O) = 120 then Base := 16; O := O + 1; end if;
            Start := O;
            while O <= T.Length and then T.Data (O) /= 59 loop
               pragma Loop_Invariant (O >= Start and then O <= T.Length and then C <= CP'Last);
               pragma Loop_Variant (Increases => O);
               if T.Data (O) in 48 .. 57 then Digit := T.Data (O) - 48;
               elsif Base = 16 and then T.Data (O) in 65 .. 70 then Digit := T.Data (O) - 65 + 10;
               elsif Base = 16 and then T.Data (O) in 97 .. 102 then Digit := T.Data (O) - 97 + 10;
               else Bad := True; return;
               end if;
               if C > (CP'Last - Digit) / Base then Bad := True; return; end if;
               C := C * Base + Digit; O := O + 1;
            end loop;
            if O = Start or else O > T.Length or else not XML_Char (C) then Bad := True; return; end if;
            Value := C;
         else
            while O <= T.Length and then T.Data (O) /= 59 loop
               pragma Loop_Invariant (O >= Start and then O <= T.Length);
               pragma Loop_Variant (Increases => O);
               O := O + 1;
            end loop;
            if O > T.Length then Bad := True; return; end if;
            if Exact_Name (Start, O - 1, "amp") then Value := 38;
            elsif Exact_Name (Start, O - 1, "lt") then Value := 60;
            elsif Exact_Name (Start, O - 1, "gt") then Value := 62;
            elsif Exact_Name (Start, O - 1, "apos") then Value := 39;
            elsif Exact_Name (Start, O - 1, "quot") then Value := 34;
            else Bad := True; return;
            end if;
         end if;
         O := O + 1;
      end Entity;
      function Colon (F, L : Natural) return Natural
        with Pre => (if F <= L then F >= 1 and then L <= T.Length),
          Post => Colon'Result = 0 or else Colon'Result = Natural'Last
            or else (Colon'Result > F and then Colon'Result < L)
      is
         R : Natural := 0;
      begin
         for K in F .. L loop
            pragma Loop_Invariant (R = 0 or else (R > F and then R < L));
            if T.Data (K) = 58 then
               if R /= 0 or else K = F or else K = L then return Natural'Last; end if;
               R := K;
            end if;
         end loop;
         return R;
      end Colon;
      -- Namespace lookup uses the actual active declarations, including those
      -- on this start tag; a namespace-qualified testsuite is not testsuite.
      function Namespace_Of (F, L : Natural; Is_Attribute : Boolean) return Natural
        with Pre => (if F <= L then F >= 1 and then L <= T.Length) and then Attrs_OK (Attributes),
          Post => Namespace_Of'Result = 0 or else Namespace_Of'Result >= Natural'Last - 1
            or else Namespace_Of'Result in 1 .. Attributes
      is
         C : constant Natural := Colon (F, L);
         A, N : Natural;
      begin
         if C = Natural'Last then return Natural'Last; end if;
         if C = 0 and then Is_Attribute then return 0; end if;
         if C /= 0 and then Exact_Name (F, C - 1, "xml") then return Natural'Last - 1; end if;
         A := Attributes;
         while A > 0 loop
            pragma Loop_Invariant (A <= Attributes);
            pragma Loop_Variant (Decreases => A);
            if Attr (A).Namespace then
               N := Colon (Attr (A).First, Attr (A).Last);
               if (C = 0 and then N = 0) or else
                 (C /= 0 and then N /= 0 and then N /= Natural'Last
                  and then Equal_Name (F, C - 1, N + 1, Attr (A).Last))
               then
                  if Attr (A).Value_Last < Attr (A).Value_First then
                     return (if C = 0 then 0 else Natural'Last);
                  end if;
                  return A;
               end if;
            end if;
            A := A - 1;
         end loop;
         return (if C = 0 then 0 else Natural'Last);
      end Namespace_Of;
      function URI_Equal (A, B : Natural) return Boolean
        with Pre => (A = 0 or else A >= Natural'Last - 1 or else A in 1 .. Attributes)
          and then (B = 0 or else B >= Natural'Last - 1 or else B in 1 .. Attributes)
          and then Attrs_OK (Attributes)
      is
      begin
         if A = B then return True; end if;
         if A = 0 or else B = 0 or else A >= Natural'Last - 1 or else B >= Natural'Last - 1 then return False; end if;
         return Values (Attr (A).Value_First .. Attr (A).Value_Last) = Values (Attr (B).Value_First .. Attr (B).Value_Last);
      end URI_Equal;
      function Value_Is (A : Natural; Text : String) return Boolean
        with Pre => A in 1 .. Attributes and then Attrs_OK (Attributes)
      is
      begin
         if Attr (A).Value_Last < Attr (A).Value_First
           or else Attr (A).Value_Last - Attr (A).Value_First + 1 /= Text'Length then return False; end if;
         for K in 0 .. Text'Length - 1 loop
            if Values (Attr (A).Value_First + K) /= Character'Pos (Text (Text'First + K)) then return False; end if;
         end loop;
         return True;
      end Value_Is;
      function Local_First (F, L : Natural) return Natural
        with Pre => (if F <= L then F >= 1 and then L <= T.Length),
          Post => Local_First'Result >= F and then (if F <= L then Local_First'Result <= L)
      is
         C : constant Natural := Colon (F, L);
      begin return (if C = 0 or else C = Natural'Last then F else C + 1); end Local_First;
      procedure Skip_Until (Terminator : String; Comment : Boolean := False)
        with Pre => O >= 1 and then O - 1 <= T.Length,
          Post => O >= O'Old and then O - 1 <= T.Length
      is
      begin
         while O <= T.Length and then not Match (O, Terminator) loop
            pragma Loop_Invariant (O >= O'Loop_Entry and then O <= T.Length);
            pragma Loop_Variant (Increases => O);
            if Comment and then Match (O, "--") then Bad := True; return; end if;
            O := O + 1;
         end loop;
         if O > T.Length then Bad := True; else O := O + Terminator'Length; end if;
      end Skip_Until;
      procedure Declaration
        with Pre => O >= 1 and then O - 1 <= T.Length,
          Post => O >= O'Old and then O - 1 <= T.Length
      is
         F, L, V, Stop, Q, Before : Natural;
         Stage : Natural := 0;
      begin
         loop
            pragma Loop_Invariant (O >= O'Loop_Entry and then O - 1 <= T.Length);
            pragma Loop_Variant (Increases => O);
            Before := O; White;
            if Match (O,"?>") then
               if Stage = 0 then Bad := True; else O := O + 2; end if;
               return;
            end if;
            if O = Before then Bad := True; return; end if;
            Name (F,L); White;
            if Bad or else O > T.Length or else T.Data (O) /= 61 then Bad := True; return; end if;
            O := O + 1; White;
            if O > T.Length or else (T.Data (O) /= 34 and then T.Data (O) /= 39) then Bad := True; return; end if;
            Q := T.Data (O); O := O + 1; V := O;
            while O <= T.Length and then T.Data (O) /= Q loop
               pragma Loop_Invariant (O >= V and then O <= T.Length);
               pragma Loop_Variant (Increases => O);
               O := O + 1;
            end loop;
            if O > T.Length then Bad := True; return; end if;
            Stop := O - 1; O := O + 1;
            if Exact_Name (F,L,"version") and then Stage = 0 then
               if Stop < V or else Stop - V < 2 or else not Match (V,"1.") then Bad := True; return; end if;
               for K in V + 2 .. Stop loop
                  if T.Data (K) not in 48 .. 57 then Bad := True; return; end if;
               end loop;
               Stage := 1;
            elsif Exact_Name (F,L,"encoding") and then Stage = 1 then
               if Stop < V or else (T.Data (V) not in 65 .. 90 and then T.Data (V) not in 97 .. 122) then Bad := True; return; end if;
               for K in V + 1 .. Stop loop
                  if not (T.Data (K) in 65 .. 90 or else T.Data (K) in 97 .. 122
                    or else T.Data (K) in 48 .. 57 or else T.Data (K) = 46 or else T.Data (K) = 45 or else T.Data (K) = 95)
                  then Bad := True; return; end if;
               end loop;
               Stage := 2;
            elsif Exact_Name (F,L,"standalone") and then Stage in 1 .. 2 then
               if not Exact_Name (V,Stop,"yes") and then not Exact_Name (V,Stop,"no") then Bad := True; return; end if;
               Stage := 3;
            else Bad := True; return;
            end if;
         end loop;
      end Declaration;
   begin
      -- DTD rejection precedes XML parsing, as in the original byte producer.
      for K in Payload'Range loop
         if Payload'Last - K + 1 >= 9 then
            declare S : String (1 .. 9); begin
               for J in S'Range loop
                  S (J) := (if Payload (K + (J - 1)) in 'a' .. 'z'
                            then Character'Val (Character'Pos (Payload (K + (J - 1))) - 32) else Payload (K + (J - 1)));
               end loop;
               if S = "<!DOCTYPE" then return Reject (DTD_Forbidden, "JUnit DTD is not allowed", "tests"); end if;
            end;
         end if;
      end loop;
      if not T.Valid or else (for some C of T.Data (1 .. T.Length) => not XML_Char (C)) then
         return Reject (Invalid_XML, "invalid JUnit XML: invalid character or encoding", "tests");
      end if;
      if T.Length > 0 and then T.Data (1) = 16#FEFF# then O := 2; end if;
      while O <= T.Length and then not Bad loop
         pragma Loop_Invariant (O >= 1 and then O <= T.Length);
         pragma Loop_Invariant (Depth < O and then Attributes < O and then Values_Used < O and then Suite_Count < O);
         pragma Loop_Invariant (Stack_OK (Depth));
         pragma Loop_Invariant (Attrs_OK (Attributes));
         pragma Loop_Variant (Decreases => T.Length - O + 1);
         if T.Data (O) /= 60 then
            if Depth = 0 then if not XML_White (T.Data (O)) then Bad := True; end if; O := O + 1;
            elsif T.Data (O) = 38 then declare C : CP; begin Entity (C); end;
            elsif Match (O, "]]>") then Bad := True;
            else O := O + 1;
            end if;
         elsif Match (O, "<!--") then O := O + 4; Skip_Until ("-->", True);
         elsif Match (O, "<?") then
            O := O + 2;
            declare F, L : Natural; begin
               Name (F, L);
               if not Bad then
                  if Exact_Name (F, L, "xml") then
                     if Root_Seen or else not (F = 3 or else (F = 4 and then T.Data (1) = 16#FEFF#)) then Bad := True;
                     else Declaration; end if;
                  elsif L - F = 2 and then Match (F, "xml", True) then Bad := True;
                  elsif O <= T.Length and then (XML_White (T.Data (O)) or else Match (O,"?>")) then Skip_Until ("?>");
                  else Bad := True;
                  end if;
               end if;
            end;
         elsif Match (O, "<![CDATA[") then
            if Depth = 0 then Bad := True; else O := O + 9; Skip_Until ("]]>"); end if;
         elsif Match (O, "</") then
            O := O + 2;
            declare F, L : Natural; begin
               Name (F, L); White;
               if Bad or else Depth = 0 or else O > T.Length or else T.Data (O) /= 62
                 or else not Equal_Name (F, L, Stack (Depth).First, Stack (Depth).Last)
               then Bad := True;
               else Attributes := Stack (Depth).Attr_Base; Depth := Depth - 1; O := O + 1; if Depth = 0 then Root_Done := True; end if;
               end if;
            end;
         elsif Match (O, "<!") then Bad := True;
         else
            if Root_Done then Bad := True; exit; end if;
            O := O + 1;
            declare
               F, L, Base, AF, AL, VF, VL, Q, Before, NS, Other_NS : Natural;
               Empty : Boolean := False;
               Suite : Boolean;
            begin
               Name (F, L); Base := Attributes;
               while not Bad and then O <= T.Length loop
                  pragma Loop_Invariant (O >= 1 and then F >= 1 and then L >= F and then L < O);
                  pragma Loop_Invariant (Attributes >= Base and then Attributes < O and then Values_Used < O);
                  pragma Loop_Invariant (Stack_OK (Depth));
                  pragma Loop_Invariant (Attrs_OK (Attributes));
                  pragma Loop_Variant (Increases => O);
                  Before := O; White;
                  exit when O > T.Length or else T.Data (O) = 62 or else T.Data (O) = 47;
                  if Before = O then Bad := True; exit; end if;
                  Name (AF, AL); White;
                  if Bad or else O > T.Length or else T.Data (O) /= 61 then Bad := True; exit; end if;
                  O := O + 1; White;
                  if O > T.Length or else (T.Data (O) /= 34 and then T.Data (O) /= 39) then Bad := True; exit; end if;
                  Q := T.Data (O); O := O + 1; VF := Values_Used + 1;
                  while O <= T.Length and then T.Data (O) /= Q and then not Bad loop
                     pragma Loop_Invariant (O >= O'Loop_Entry and then Values_Used < O and then Values_Used >= VF - 1);
                     pragma Loop_Invariant (Stack_OK (Depth));
                     pragma Loop_Invariant (Attrs_OK (Attributes));
                     pragma Loop_Variant (Increases => O);
                     declare C : CP; begin
                        if T.Data (O) = 38 then Entity (C);
                        elsif T.Data (O) = 60 then Bad := True; C := 0;
                        else
                           C := T.Data (O); O := O + 1;
                           if C = 13 then
                              if O <= T.Length and then T.Data (O) = 10 then O := O + 1; end if;
                              C := 32;
                           elsif C = 10 or else C = 9 then C := 32;
                           end if;
                        end if;
                        if not Bad then Values_Used := Values_Used + 1; Values (Values_Used) := C; end if;
                     end;
                  end loop;
                  if Bad or else O > T.Length then Bad := True; exit; end if;
                  VL := Values_Used; O := O + 1;
                  for A in Base + 1 .. Attributes loop
                     if Equal_Name (AF, AL, Attr (A).First, Attr (A).Last) then Bad := True; end if;
                  end loop;
                  Attributes := Attributes + 1;
                  Attr (Attributes) := (AF, AL, VF, VL,
                    Exact_Name (AF, AL, "xmlns") or else (AL - AF >= 6 and then Match (AF, "xmlns:")));
                  if Attr (Attributes).Namespace then
                     declare
                        C : constant Natural := Colon (AF,AL);
                        XML_Prefix : constant Boolean := C /= 0 and then C /= Natural'Last
                          and then Exact_Name (C + 1,AL,"xml");
                        XML_URI : constant Boolean := Value_Is (Attributes,"http://www.w3.org/XML/1998/namespace");
                     begin
                        if C = Natural'Last or else
                          (C /= 0 and then (VL < VF or else Exact_Name (C + 1,AL,"xmlns")))
                          or else XML_Prefix /= XML_URI
                          or else Value_Is (Attributes,"http://www.w3.org/2000/xmlns/")
                        then Bad := True; end if;
                     end;
                  end if;
               end loop;
               if not Bad then
                  if O <= T.Length and then T.Data (O) = 47 then Empty := True; O := O + 1; end if;
                  if O > T.Length or else T.Data (O) /= 62 then Bad := True;
                  else O := O + 1; end if;
               end if;
               if not Bad then
                  NS := Namespace_Of (F, L, False);
                  if NS = Natural'Last then Bad := True; end if;
                  for A in Base + 1 .. Attributes loop
                     if not Attr (A).Namespace then
                        Other_NS := Namespace_Of (Attr (A).First, Attr (A).Last, True);
                        if Other_NS = Natural'Last then Bad := True; end if;
                        for B in Base + 1 .. A - 1 loop
                           if not Attr (B).Namespace and then
                             Equal_Name (Local_First (Attr (A).First, Attr (A).Last), Attr (A).Last,
                                         Local_First (Attr (B).First, Attr (B).Last), Attr (B).Last)
                             and then URI_Equal (Other_NS, Namespace_Of (Attr (B).First, Attr (B).Last, True))
                           then Bad := True; end if;
                        end loop;
                     end if;
                  end loop;
                  Suite := NS = 0 and then Exact_Name (F, L, "testsuite");
                  if not Root_Seen then
                     Root_Single := Suite; Root_Seen := True;
                     if not Suite and then not (NS = 0 and then Exact_Name (F, L, "testsuites")) then Bad := True; end if;
                  end if;
                  if Suite and then (not Root_Single or else Depth = 0) then
                     Suite_Count := Suite_Count + 1;
                     for A in Base + 1 .. Attributes loop
                        declare Index : Natural := 0; N : Integer_Result; begin
                           if Exact_Name (Attr (A).First, Attr (A).Last, "tests") then Index := 1;
                           elsif Exact_Name (Attr (A).First, Attr (A).Last, "failures") then Index := 2;
                           elsif Exact_Name (Attr (A).First, Attr (A).Last, "errors") then Index := 3;
                           elsif Exact_Name (Attr (A).First, Attr (A).Last, "skipped") then Index := 4;
                           end if;
                           if Index > 0 then
                              N := Py_Integer (Values, Attr (A).Value_First, Attr (A).Value_Last);
                              if not N.Valid then Bad := True; else Totals (Index) := Totals (Index) + N.Value; end if;
                           end if;
                        end;
                     end loop;
                  end if;
                  if Empty then Attributes := Base; if Depth = 0 then Root_Done := True; end if;
                  else Depth := Depth + 1; Stack (Depth) := (F, L, Base); end if;
               end if;
            end;
         end if;
      end loop;
      if Bad or else not Root_Seen or else not Root_Done or else Depth /= 0 then
         return Reject (Invalid_XML, "invalid JUnit XML: malformed XML or invalid integer", "tests");
      end if;
      if Suite_Count = 0 then return Reject (No_Suites, "invalid JUnit XML: no testsuite elements", "tests"); end if;
      if Totals (1) <= 0 or else (for some N of Totals => N < 0)
        or else Totals (2) + Totals (3) + Totals (4) > Totals (1)
      then return Reject (Inconsistent_Counts, "invalid JUnit XML: test counts are empty or inconsistent", "tests"); end if;
      -- The controlling parser uses aggregate attributes, not testcase content.
      -- A skipped-only suite is accepted; hidden failures retain original semantics.
      return Answer (Exit_Zero and then Totals (2) = 0 and then Totals (3) = 0, Parsed,
        ",""tests"":" & Image (Totals (1)) & ",""failures"":" & Image (Totals (2)) &
        ",""errors"":" & Image (Totals (3)) & ",""skipped"":" & Image (Totals (4)));
   end JUnit_Report;

   function Quote (D : Code_Array; First, Last : Natural) return String
     with Pre => D'First = 1 and then First >= 1 and then Last <= D'Last,
       Post => Quote'Result'First = 1
   is
      Hex : constant String := "0123456789abcdef";
      Buffer : String (1 .. (if Last < First then 2 else (Last - First + 1) * 12 + 2)) := (others => Character'Val (0));
      Used : Natural := 1;
      procedure Unit (C : Natural)
        with Pre => Used <= Buffer'Last - 6, Post => Used = Used'Old + 6
      is
      begin
         Buffer (Used + 1 .. Used + 2) := "\u";
         Buffer (Used + 3) := Hex (C / 4096 mod 16 + 1);
         Buffer (Used + 4) := Hex (C / 256 mod 16 + 1);
         Buffer (Used + 5) := Hex (C / 16 mod 16 + 1);
         Buffer (Used + 6) := Hex (C mod 16 + 1);
         Used := Used + 6;
      end Unit;
   begin
      Buffer (1) := '"';
      for K in First .. Last loop
         pragma Loop_Invariant (Used <= (K - First) * 12 + 1);
         if D (K) in 32 .. 126 and then D (K) /= 34 and then D (K) /= 92 then
            Used := Used + 1; Buffer (Used) := Character'Val (D (K));
         elsif D (K) > 65535 then
            Unit (16#D800# + (D (K) - 65536) / 1024);
            Unit (16#DC00# + (D (K) - 65536) mod 1024);
         else Unit (D (K));
         end if;
      end loop;
      Used := Used + 1; Buffer (Used) := '"';
      return Buffer (1 .. Used);
   end Quote;
   function Quote (S : String) return String
     with Post => Quote'Result'First = 1
   is
      D : Code_Array (1 .. S'Length);
   begin
      for K in D'Range loop D (K) := Character'Pos (S (S'First + (K - 1))); end loop;
      return Quote (D, 1, D'Length);
   end Quote;

   function Number_From_ASCII (S : String) return Exact_Decimal.Number is
      A : P.Bytes (1 .. P.Count (S'Length)) := (others => 0);
   begin
      for K in S'Range loop A (P.Count (K - S'First + 1)) := P.Byte (Character'Pos (S (K))); end loop;
      return Exact_Decimal.Parse (A, (1, P.Count (S'Length)), 0);
   end Number_From_ASCII;

   type Decimal_Result is record
      Valid, Finite : Boolean := False;
      Value : Exact_Decimal.Number := Exact_Decimal.No_Number;
   end record;
   -- Decimal(str(value)) admits signed, Unicode decimal digits and underscores
   -- in JSON strings, as well as JSON int and rounded binary64 values.
   function Decimal_String (D : Code_Array; First, Last : Natural) return Decimal_Result
     with Pre => D'First = 1 and then Last < D'Last
   is
      R : Decimal_Result;
      A : Natural := First;
      B : Natural := Last;
      Dot, Exponent, Had_Digits, Exponent_Digits : Boolean := False;
      Exponent_Negative : Boolean := False;
      Fraction, Power : Big_Integer := To_Big_Integer (0);
      Digit : Integer;
      function Word (Text : String; Payload : Boolean := False) return Boolean
        with Pre => D'First = 1 and then A >= 1 and then B < D'Last
      is
         J : Natural := A;
         C, E : Natural;
      begin
         for K in Text'Range loop
            pragma Loop_Invariant (J >= A);
            while J <= B and then D (J) = 95 loop
               pragma Loop_Invariant (J >= A);
               pragma Loop_Variant (Increases => J);
               J := J + 1;
            end loop;
            if J > B then return False; end if;
            C := D (J); E := Character'Pos (Text (K));
            if C in 65 .. 90 then C := C + 32; end if;
            if C /= E then return False; end if;
            J := J + 1;
         end loop;
         while J <= B loop
            pragma Loop_Invariant (J >= A);
            pragma Loop_Variant (Increases => J);
            if D (J) /= 95 and then (not Payload or else Decimal_Digit (D (J)) < 0) then return False; end if;
            J := J + 1;
         end loop;
         return True;
      end Word;
   begin
      if A = 0 or else A > B then return R; end if;
      while A <= B and then (Is_White (D (A)) or else D (A) = 95) loop
         pragma Loop_Invariant (A >= 1);
         pragma Loop_Variant (Increases => A);
         A := A + 1;
      end loop;
      while B >= A and then (Is_White (D (B)) or else D (B) = 95) loop
         pragma Loop_Invariant (B <= Last);
         pragma Loop_Variant (Decreases => B);
         B := B - 1;
      end loop;
      if A > B then return R; end if;
      if D (A) = 43 or else D (A) = 45 then R.Value.Negative := D (A) = 45; A := A + 1; end if;
      if Word ("inf") or else Word ("infinity") or else Word ("nan",True) or else Word ("snan",True) then
         R.Valid := True; return R;
      end if;
      while A <= B loop
         pragma Loop_Invariant (A >= 1);
         pragma Loop_Variant (Decreases => B - A + 1);
         Digit := Decimal_Digit (D (A));
         if D (A) = 95 then null;
         elsif Digit >= 0 then
            if Exponent then Power := Power * To_Big_Integer (10) + To_Big_Integer (Digit); Exponent_Digits := True;
            else
               R.Value.Coefficient := R.Value.Coefficient * To_Big_Integer (10) + To_Big_Integer (Digit);
               Had_Digits := True;
               if Dot then Fraction := Fraction + To_Big_Integer (1); end if;
            end if;
         elsif D (A) = 46 and then not Dot and then not Exponent then Dot := True;
         elsif (D (A) = 69 or else D (A) = 101) and then Had_Digits and then not Exponent then
            Exponent := True; A := A + 1;
            while A <= B and then D (A) = 95 loop
               pragma Loop_Invariant (A >= A'Loop_Entry);
               pragma Loop_Variant (Increases => A);
               A := A + 1;
            end loop;
            if A <= B and then (D (A) = 43 or else D (A) = 45) then Exponent_Negative := D (A) = 45;
            else A := A - 1; end if;
         else return R;
         end if;
         A := A + 1;
      end loop;
      R.Valid := Had_Digits and then (not Exponent or else Exponent_Digits);
      R.Finite := R.Valid;
      R.Value.Valid := R.Valid;
      R.Value.Exponent := (if Exponent_Negative then -Power else Power) - Fraction;
      if R.Value.Coefficient > 0 then
         R.Value.Significant_Digits := To_Big_Integer (Image (R.Value.Coefficient)'Length);
      end if;
      return R;
   end Decimal_String;

   function Decimal_Less (L, R : Exact_Decimal.Number) return Boolean is
      LC : Big_Integer := L.Coefficient;
      RC : Big_Integer := R.Coefficient;
      L_Order, R_Order : Big_Integer := To_Big_Integer (0);
      Less_Magnitude : Boolean;
   begin
      if LC = 0 and then RC = 0 then return False; end if;
      if L.Negative /= R.Negative then return L.Negative; end if;
      if LC = 0 then Less_Magnitude := True;
      elsif RC = 0 then Less_Magnitude := False;
      else
         L_Order := To_Big_Integer (Image (LC)'Length) + L.Exponent;
         R_Order := To_Big_Integer (Image (RC)'Length) + R.Exponent;
         if L_Order /= R_Order then Less_Magnitude := L_Order < R_Order;
         else
            if L.Exponent > R.Exponent then LC := LC * Exact_Decimal.Power (10, L.Exponent - R.Exponent);
            elsif R.Exponent > L.Exponent then RC := RC * Exact_Decimal.Power (10, R.Exponent - L.Exponent);
            end if;
            Less_Magnitude := LC < RC;
         end if;
      end if;
      if L.Negative then
         if LC = 0 and then RC = 0 then return False; end if;
         if L.Coefficient = 0 then return False; end if;
         if R.Coefficient = 0 then return True; end if;
         return not Less_Magnitude and then
           (L_Order /= R_Order or else LC /= RC);
      end if;
      return Less_Magnitude;
   end Decimal_Less;

   function Round_28 (N : Exact_Decimal.Number) return Exact_Decimal.Number is
      R : Exact_Decimal.Number := N;
      Digit_Count : constant Natural := Image (R.Coefficient)'Length;
      Power, Q, Remnant : Big_Integer;
   begin
      if R.Coefficient = 0 then R.Exponent := To_Big_Integer (0); return R; end if;
      if Digit_Count > 28 then
         Power := Exact_Decimal.Power (10, To_Big_Integer (Digit_Count - 28));
         Q := R.Coefficient / Power; Remnant := R.Coefficient rem Power;
         if Remnant * To_Big_Integer (2) > Power or else
           (Remnant * To_Big_Integer (2) = Power and then Q rem To_Big_Integer (2) /= 0)
         then Q := Q + To_Big_Integer (1); end if;
         R.Coefficient := Q; R.Exponent := R.Exponent + To_Big_Integer (Digit_Count - 28);
      end if;
      return R;
   end Round_28;

   function Decimal_Image (N : Exact_Decimal.Number) return String is
      C : Big_Integer := N.Coefficient;
      E : Big_Integer := N.Exponent;
   begin
      if C = 0 then return (if N.Negative then "-0" else "0"); end if;
      -- A nonzero coefficient has fewer trailing zeros than digits, so the
      -- decimal image bounds the stripping (GNAT's runtime Loop_Variant
      -- cannot carry a Big_Integer measure).
      for Zeros in 1 .. Image (C)'Length loop
         exit when C rem To_Big_Integer (10) /= 0;
         C := C / To_Big_Integer (10); E := E + To_Big_Integer (1);
      end loop;
      declare
         S : constant String := Image (C);
         Adjusted : constant Big_Integer := E + To_Big_Integer (S'Length - 1);
         Sign : constant String := (if N.Negative then "-" else "");
         Position : Integer;
      begin
         if E > 0 or else Adjusted < -6 then
            return Sign & (if S'Length > 0 then S (1 .. 1) else "") & (if S'Length > 1 then "." & S (2 .. S'Last) else "") &
              "E" & (if Adjusted >= 0 then "+" else "") & Image (Adjusted);
         end if;
         Position := To_Integer (E + To_Big_Integer (S'Length));
         if Position <= 0 then return Sign & "0." & String'(1 .. -Position => '0') & S;
         elsif Position >= S'Length then return Sign & S & String'(1 .. Position - S'Length => '0');
         else return Sign & S (1 .. Position) & "." & S (Position + 1 .. S'Last);
         end if;
      end;
   end Decimal_Image;

   function Percentage (Baseline, Candidate : Exact_Decimal.Number) return String is
      Common : constant Big_Integer := (if Baseline.Exponent < Candidate.Exponent then Baseline.Exponent else Candidate.Exponent);
      Left : Big_Integer := Candidate.Coefficient * Exact_Decimal.Power (10, Candidate.Exponent - Common);
      Right : Big_Integer := Baseline.Coefficient * Exact_Decimal.Power (10, Baseline.Exponent - Common);
      -- Decimal.__abs__ applies the original context before division too.
      Absolute_Baseline : constant Exact_Decimal.Number := Round_28 (Baseline);
      N : Exact_Decimal.Number := Exact_Decimal.No_Number;
      Denominator, Numerator, Q, Remainder, Scale : Big_Integer;
      Order : Integer;
   begin
      if Baseline.Coefficient = 0 then return "null"; end if;
      if Candidate.Negative then Left := -Left; end if;
      if Baseline.Negative then Right := -Right; end if;
      Left := Left - Right;
      N.Valid := True; N.Negative := Left < 0 or else
        (Left = 0 and then Candidate.Negative and then not Baseline.Negative);
      N.Coefficient := abs Left; N.Exponent := Common;
      N := Round_28 (N);
      if N.Coefficient = 0 then return Quote (Decimal_Image (N)); end if;
      Numerator := N.Coefficient; Denominator := Absolute_Baseline.Coefficient;
      Order := Image (Numerator)'Length - Image (Denominator)'Length;
      if Order >= 0 then
         if Numerator < Denominator * Exact_Decimal.Power (10, To_Big_Integer (Order)) then Order := Order - 1; end if;
      elsif Numerator * Exact_Decimal.Power (10, To_Big_Integer (-Order)) < Denominator then Order := Order - 1;
      end if;
      Scale := To_Big_Integer (27) - To_Big_Integer (Order);
      if Scale >= 0 then Numerator := Numerator * Exact_Decimal.Power (10, Scale);
      else Denominator := Denominator * Exact_Decimal.Power (10, -Scale);
      end if;
      Q := Numerator / Denominator; Remainder := Numerator rem Denominator;
      if Remainder * To_Big_Integer (2) > Denominator or else
        (Remainder * To_Big_Integer (2) = Denominator and then Q rem To_Big_Integer (2) /= 0)
      then Q := Q + To_Big_Integer (1); end if;
      N.Coefficient := Q; N.Exponent := N.Exponent - Absolute_Baseline.Exponent - Scale + To_Big_Integer (2);
      N := Round_28 (N);
      return Quote (Decimal_Image (N));
   end Percentage;

   function Benchmark_Report (Payload : String; Exit_Zero : Boolean) return Parsed_Report
     with Post => Benchmark_Report'Result.Status /= Unsupported
   is
      T : constant Decoded_Text := Decode (Payload);
      Values : Code_Array (1 .. T.Length) := (others => 0);
      Used, O : Natural := 0;
      Bad : Boolean := False;
      type JSON_Kind is (J_Invalid, J_String, J_Integer, J_Float, J_Nonfinite, J_Other);
      type JSON_Node is record
         Kind : JSON_Kind := J_Invalid;
         First, Last : Natural := 0;
      end record;
      type Field_Array is array (1 .. 5) of JSON_Node;
      Fields : Field_Array := (others => (J_Invalid, 0, 0));
      Unknown : Boolean := False;
      -- Proof-only description of a lexed node: string spans index Values,
      -- numeric spans index the ASCII source text.
      function Node_OK (N : JSON_Node) return Boolean is
        ((if N.Kind = J_String then N.First >= 1 and then N.Last <= Used) and then
         (if N.Kind in J_Integer | J_Float then N.First >= 1 and then N.Last <= T.Length
            and then (for all I in N.First .. N.Last => T.Data (I) < 128)))
        with Ghost;
      procedure White
        with Post => O >= O'Old and then O <= Natural'Max (O'Old, T.Length)
      is
      begin
         while O < T.Length and then (T.Data (O + 1) = 32 or else T.Data (O + 1) = 9
           or else T.Data (O + 1) = 10 or else T.Data (O + 1) = 13) loop
            pragma Loop_Invariant (O >= O'Loop_Entry and then O < T.Length);
            pragma Loop_Variant (Increases => O);
            O := O + 1;
         end loop;
      end White;
      function Match (S : String) return Boolean
        with Post => (if Match'Result then S'Length <= T.Length - O)
      is
      begin
         if S'Length > T.Length - O then return False; end if;
         for K in 0 .. S'Length - 1 loop
            if T.Data (O + K + 1) /= Character'Pos (S (S'First + K)) then return False; end if;
         end loop;
         return True;
      end Match;
      function Hex (C : CP) return Integer is
        (if C in 48 .. 57 then Integer (C - 48)
         elsif C in 65 .. 70 then Integer (C - 65 + 10)
         elsif C in 97 .. 102 then Integer (C - 97 + 10) else -1);
      procedure Escaped_Unit (C : out CP)
        with Post => O >= O'Old and then O <= Natural'Max (O'Old, T.Length) and then C <= 16#FFFF#
      is
         H : Integer;
      begin
         C := 0;
         if T.Length - O < 4 then Bad := True; return; end if;
         for K in 1 .. 4 loop
            H := Hex (T.Data (O + K));
            if H < 0 then Bad := True; return; end if;
            C := C * 16 + Natural (H);
         end loop;
         O := O + 4;
      end Escaped_Unit;
      procedure JSON_String (R : out JSON_Node)
        with Pre => Used < T.Length and then Used <= O and then O <= T.Length,
          Post => O >= O'Old and then O <= T.Length and then Used >= Used'Old and then Used <= O
            and then Used - O <= Used'Old - O'Old and then (if not Bad then Used < O)
            and then R.Kind = J_String and then R.First = Used'Old + 1 and then R.Last <= Used
      is
         C, Second : CP;
         Save : Natural;
      begin
         R := (J_String, Used + 1, Used);
         if O >= T.Length or else T.Data (O + 1) /= 34 then Bad := True; return; end if;
         O := O + 1;
         while O < T.Length loop
            pragma Loop_Invariant (O >= O'Loop_Entry and then Used < O and then Used >= Used'Loop_Entry);
            pragma Loop_Invariant (Used - O <= Used'Loop_Entry - O'Loop_Entry);
            pragma Loop_Variant (Increases => O);
            C := T.Data (O + 1); O := O + 1;
            if C = 34 then R.Last := Used; return; end if;
            if C < 32 then Bad := True; return; end if;
            if C = 92 then
               if O >= T.Length then Bad := True; return; end if;
               C := T.Data (O + 1); O := O + 1;
               case C is
                  when 34 | 92 | 47 => null;
                  when 98 => C := 8;
                  when 102 => C := 12;
                  when 110 => C := 10;
                  when 114 => C := 13;
                  when 116 => C := 9;
                  when 117 =>
                     Escaped_Unit (C);
                     if Bad then return; end if;
                     if C in 16#D800# .. 16#DBFF# and then Match ("\u") then
                        Save := O; O := O + 2; Escaped_Unit (Second);
                        if not Bad and then Second in 16#DC00# .. 16#DFFF# then
                           C := 65536 + (C - 16#D800#) * 1024 + Second - 16#DC00#;
                        else O := Save; Bad := False;
                        end if;
                     end if;
                  when others => Bad := True; return;
               end case;
            end if;
            Used := Used + 1; Values (Used) := C;
         end loop;
         Bad := True;
      end JSON_String;
      function ASCII (F, L : Natural) return String
        with Pre => F >= 1 and then L <= T.Length and then (for all I in F .. L => T.Data (I) < 128)
      is
         S : String (1 .. (if L < F then 0 else L - F + 1));
      begin
         for K in S'Range loop S (K) := Character'Val (T.Data (F + (K - 1))); end loop;
         return S;
      end ASCII;
      procedure Value (R : out JSON_Node)
        with Subprogram_Variant => (Decreases => T.Length - O),
          Pre => Used <= O and then O <= T.Length,
          Post => O >= O'Old and then O <= T.Length and then Used >= Used'Old
            and then Used - O <= Used'Old - O'Old and then Node_OK (R);
      procedure Value (R : out JSON_Node) is
         Close : CP;
         Object : Boolean;
         Child : JSON_Node;
      begin
         R := (J_Invalid,0,0);
         White;
         if O >= T.Length then Bad := True; return; end if;
         if T.Data (O + 1) = 34 then JSON_String (R); return; end if;
         if T.Data (O + 1) = 123 or else T.Data (O + 1) = 91 then
            Object := T.Data (O + 1) = 123; Close := (if Object then 125 else 93); O := O + 1;
            White;
            if O < T.Length and then T.Data (O + 1) = Close then O := O + 1; R := (J_Other,0,0); return; end if;
            loop
               pragma Loop_Invariant (O >= O'Loop_Entry and then O <= T.Length and then Used < O);
               pragma Loop_Invariant (Used >= Used'Loop_Entry and then Used - O <= Used'Loop_Entry - O'Loop_Entry);
               pragma Loop_Variant (Increases => O);
               if Object then
                  JSON_String (Child); White;
                  if Bad or else O >= T.Length or else T.Data (O + 1) /= 58 then Bad := True; exit; end if;
                  O := O + 1;
               end if;
               Value (Child); White;
               if Bad or else O >= T.Length then Bad := True; exit; end if;
               if T.Data (O + 1) = Close then O := O + 1; exit; end if;
               if T.Data (O + 1) /= 44 then Bad := True; exit; end if;
               O := O + 1; White;
            end loop;
            R := (J_Other,0,0); return;
         end if;
         for K in 1 .. 6 loop
            declare
               Token : constant String :=
                 (case K is when 1 => "null", when 2 => "true", when 3 => "false",
                   when 4 => "NaN", when 5 => "Infinity", when others => "-Infinity");
            begin
               if Match (Token) then
                  R := ((if K <= 3 then J_Other else J_Nonfinite), O + 1, O + Token'Length);
                  O := O + Token'Length; return;
               end if;
            end;
         end loop;
         R.First := O + 1;
         if T.Data (O + 1) = 45 then O := O + 1; end if;
         if O >= T.Length or else T.Data (O + 1) not in 48 .. 57 then Bad := True; return; end if;
         if T.Data (O + 1) = 48 then O := O + 1;
         else
            while O < T.Length and then T.Data (O + 1) in 48 .. 57 loop
               pragma Loop_Invariant (O in R.First - 1 .. T.Length and then (for all I in R.First .. O => T.Data (I) < 128));
               pragma Loop_Variant (Increases => O);
               O := O + 1;
            end loop;
         end if;
         R.Kind := J_Integer;
         pragma Assert (for all I in R.First .. O => T.Data (I) < 128);
         if O < T.Length and then T.Data (O + 1) = 46 then
            R.Kind := J_Float; O := O + 1;
            if O >= T.Length or else T.Data (O + 1) not in 48 .. 57 then Bad := True; return; end if;
            while O < T.Length and then T.Data (O + 1) in 48 .. 57 loop
               pragma Loop_Invariant (O in R.First - 1 .. T.Length and then (for all I in R.First .. O => T.Data (I) < 128));
               pragma Loop_Variant (Increases => O);
               O := O + 1;
            end loop;
         end if;
         pragma Assert (for all I in R.First .. O => T.Data (I) < 128);
         if O < T.Length and then (T.Data (O + 1) = 101 or else T.Data (O + 1) = 69) then
            R.Kind := J_Float; O := O + 1;
            if O < T.Length and then (T.Data (O + 1) = 43 or else T.Data (O + 1) = 45) then O := O + 1; end if;
            if O >= T.Length or else T.Data (O + 1) not in 48 .. 57 then Bad := True; return; end if;
            while O < T.Length and then T.Data (O + 1) in 48 .. 57 loop
               pragma Loop_Invariant (O in R.First - 1 .. T.Length and then (for all I in R.First .. O => T.Data (I) < 128));
               pragma Loop_Variant (Increases => O);
               O := O + 1;
            end loop;
         end if;
         R.Last := O;
      end Value;
      function String_Is (N : JSON_Node; S : String) return Boolean
        with Pre => (if N.Kind = J_String then N.First >= 1 and then N.Last <= T.Length),
          Post => (if String_Is'Result then N.Kind = J_String and then N.Last >= N.First)
      is
      begin
         if N.Kind /= J_String or else N.Last < N.First or else N.Last - N.First + 1 /= S'Length then return False; end if;
         for K in 0 .. S'Length - 1 loop
            if Values (N.First + K) /= Character'Pos (S (S'First + K)) then return False; end if;
         end loop;
         return True;
      end String_Is;
      type Numeric (Length : Natural) is record
         Class : Classification;
         N : Exact_Decimal.Number;
         Spelling : String (1 .. Length);
      end record;
      function Number (Node : JSON_Node) return Numeric
        with Pre => Node_OK (Node) and then Used < T.Length
      is
         N : Exact_Decimal.Number;
         D : Decimal_Result;
         Conversion : Decimal_Binary64.Conversion;
      begin
         if Node.Kind = J_Nonfinite then return (0,Non_Finite,Exact_Decimal.No_Number,""); end if;
         if Node.Kind = J_String then
            D := Decimal_String (Values, Node.First, Node.Last);
            if not D.Valid then return (0,Non_Numeric,D.Value,""); end if;
            if not D.Finite then return (0,Non_Finite,D.Value,""); end if;
            declare S : constant String := Quote (Values, Node.First, Node.Last); begin
               return (S'Length,Parsed,D.Value,S);
            end;
         end if;
         if Node.Kind /= J_Integer and then Node.Kind /= J_Float then return (0,Non_Numeric,Exact_Decimal.No_Number,""); end if;
         N := Number_From_ASCII (ASCII (Node.First, Node.Last));
         if Node.Kind = J_Float then
            Conversion := Decimal_Binary64.Convert (N);
            if not Conversion.Valid then return (0,Non_Finite,N,""); end if;
            declare S : constant String := Decimal_Binary64.Repr (Conversion.Encoding); Q : constant String := Quote (S); begin
               N := Number_From_ASCII (S);
               return (Q'Length,Parsed,N,Q);
            end;
         else
            declare S : constant String := Image ((if N.Negative then -N.Coefficient else N.Coefficient)); Q : constant String := Quote (S); begin
               return (Q'Length,Parsed,N,Q);
            end;
         end if;
      end Number;
   begin
      if not T.Valid then return Reject (Invalid_JSON, "invalid benchmark JSON: invalid UTF-8"); end if;
      White;
      if O >= T.Length or else T.Data (O + 1) /= 123 then
         declare Root : JSON_Node; begin
            Value (Root); White;
            if Bad or else O /= T.Length then return Reject (Invalid_JSON, "invalid benchmark JSON: malformed JSON"); end if;
            return Reject (Invalid_Schema, "benchmark schema is invalid");
         end;
      end if;
      O := O + 1; White;
      if O < T.Length and then T.Data (O + 1) = 125 then O := O + 1;
      else
         loop
            pragma Loop_Invariant (Used < O and then O <= T.Length);
            pragma Loop_Invariant (for all I in 1 .. 5 => Node_OK (Fields (I)));
            pragma Loop_Variant (Increases => O);
            declare Key : JSON_Node; Item : JSON_Node; Index : Natural := 0; begin
               JSON_String (Key); White;
               if Bad or else O >= T.Length or else T.Data (O + 1) /= 58 then Bad := True; exit; end if;
               O := O + 1; Value (Item);
               if String_Is (Key,"metric") then Index := 1;
               elsif String_Is (Key,"unit") then Index := 2;
               elsif String_Is (Key,"baseline") then Index := 3;
               elsif String_Is (Key,"candidate") then Index := 4;
               elsif String_Is (Key,"direction") then Index := 5;
               else Unknown := True;
               end if;
               if Index > 0 then Fields (Index) := Item; end if;
            end;
            White;
            if Bad or else O >= T.Length then Bad := True; exit; end if;
            if T.Data (O + 1) = 125 then O := O + 1; exit; end if;
            if T.Data (O + 1) /= 44 then Bad := True; exit; end if;
            O := O + 1; White;
         end loop;
      end if;
      White;
      if Bad or else O /= T.Length then return Reject (Invalid_JSON, "invalid benchmark JSON: malformed JSON"); end if;
      if Unknown or else (for some F of Fields => F.Kind = J_Invalid)
        or else Fields (1).Kind /= J_String or else Fields (1).Last < Fields (1).First
        or else Fields (2).Kind /= J_String or else Fields (2).Last < Fields (2).First
        or else not (String_Is (Fields (5),"higher-is-better") or else String_Is (Fields (5),"lower-is-better"))
      then return Reject (Invalid_Schema, "benchmark schema is invalid"); end if;
      declare
         Baseline : constant Numeric := Number (Fields (3));
         Candidate : constant Numeric := Number (Fields (4));
         Improved : Boolean;
      begin
         if Baseline.Class = Non_Numeric or else Candidate.Class = Non_Numeric then return Reject (Non_Numeric, "benchmark values are not numeric"); end if;
         if Baseline.Class = Non_Finite or else Candidate.Class = Non_Finite then return Reject (Non_Finite, "benchmark values are not finite"); end if;
         Improved := (if String_Is (Fields (5),"higher-is-better") then Decimal_Less (Baseline.N, Candidate.N) else Decimal_Less (Candidate.N, Baseline.N));
         return Answer (Exit_Zero, Parsed,
           ",""metric"":" & Quote (Values, Fields (1).First, Fields (1).Last) &
           ",""unit"":" & Quote (Values, Fields (2).First, Fields (2).Last) &
           ",""baseline"":" & Baseline.Spelling & ",""candidate"":" & Candidate.Spelling &
           ",""direction"":" & Quote (Values, Fields (5).First, Fields (5).Last) &
           ",""improved"":" & (if Improved then "true" else "false") &
           ",""percentage"":" & Percentage (Baseline.N, Candidate.N));
      end;
   end Benchmark_Report;

   function Decimal_Exit_Zero (Bytes : String) return Boolean is
      Offset : Natural := 0;
   begin
      if Bytes'Length = 0 then return False; end if;
      if Bytes (Bytes'First) = '-' or else Bytes (Bytes'First) = '+' then Offset := 1; end if;
      if Offset = Bytes'Length then return False; end if;
      while Offset < Bytes'Length loop
         pragma Loop_Variant (Decreases => Bytes'Length - Offset);
         if Bytes (Bytes'First + Offset) /= '0' then return False; end if;
         Offset := Offset + 1;
      end loop;
      return True;
   end Decimal_Exit_Zero;

   function Parse
     (Format, Profile, Exit_Code : String;
      Stdout, Stderr, Result : String; Result_Present : Boolean)
      return Parsed_Report
   is
      -- Only zero is required; do not allocate an arbitrary-magnitude exit
      -- integer merely to compare it with zero. The transport is decimal ASCII.
      Exit_Zero : constant Boolean := Decimal_Exit_Zero (Exit_Code);
   begin
      if Format = "exit" then return Answer (Exit_Zero, Parsed);
      elsif Format = "junit" then
         if not Result_Present then return Reject (Missing_Report, "JUnit result file is missing", "tests"); end if;
         return JUnit_Report (Result, Exit_Zero);
      elsif Format = "gnatprove" then
         if Profile = "private-evaluator-v1" and then not Result_Present then
            return Reject (Missing_Report, "private GNATprove report is missing", "total");
         end if;
         return GNAT_Report ((if Result_Present then Result else Stdout), Exit_Zero);
      elsif Format = "worldline-benchmark-v1" then
         if not Result_Present then return Reject (Missing_Report, "benchmark result file is missing"); end if;
         return Benchmark_Report (Result, Exit_Zero);
      else
         return (2, Unsupported, Unsupported_Format, "{}");
      end if;
   end Parse;
end Worldline.Report_Parser;
