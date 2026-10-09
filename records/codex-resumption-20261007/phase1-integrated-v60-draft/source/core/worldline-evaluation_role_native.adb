with Interfaces;
with Evaluation_Pending;
with Worldline.Producer_Values;
with Worldline.Producer_Bytes;
with Worldline.Raw_JSON;
with Worldline.Lifetime_Values;
with Worldline.Confinement_Filter;
with Worldline.Native_Lifetime_Observation;
package body Worldline.Evaluation_Role_Native with SPARK_Mode is
   package J renames Worldline.Producer_Values;
   package B renames Worldline.Producer_Bytes;
   package L renames Worldline.Lifetime_Values;
   package P renames Evaluation_Pending;
   subtype U64 is Interfaces.Unsigned_64;
   use type U64;
   use type J.Value_Kind;
   use type L.Value_Kind;
   type Number is record
      Valid : Boolean := False;
      Value : U64 := 0;
   end record;
   function Image (Value : U64) return String is
      S : constant String := U64'Image (Value);
   begin return S (S'First + 1 .. S'Last); end Image;
   function White (C : Character) return Boolean is
     (C in ' ' | Character'Val (9) | Character'Val (10) | Character'Val (11) |
       Character'Val (12) | Character'Val (13));
   function Strip (S : String) return String is
      A : Natural := 0;
      Z : Natural := S'Length;
   begin
      while A < Z and then White (S (S'First + A)) loop A := A + 1; end loop;
      while Z > A and then White (S (S'First + Z - 1)) loop Z := Z - 1; end loop;
      return S (S'First + A .. S'First + Z - 1);
   end Strip;
   function Parse_Number (S : String; Base : Positive := 10) return Number is
      Value : U64 := 0;
      Digit : Natural;
   begin
      if S'Length = 0 or else Base not in 10 | 16 then return (False, 0); end if;
      for C of S loop
         if C in '0' .. '9' then Digit := Character'Pos (C) - Character'Pos ('0');
         elsif Base = 16 and then C in 'a' .. 'f' then Digit := Character'Pos (C) - Character'Pos ('a') + 10;
         elsif Base = 16 and then C in 'A' .. 'F' then Digit := Character'Pos (C) - Character'Pos ('A') + 10;
         else return (False, 0); end if;
         if Digit >= Base or else Value > (U64'Last - U64 (Digit)) / U64 (Base) then return (False, 0); end if;
         Value := Value * U64 (Base) + U64 (Digit);
      end loop;
      return (True, Value);
   end Parse_Number;
   function Word (S : String; Index : Positive) return String is
      A, Z, Count : Natural := 0;
   begin
      while A < S'Length loop
         while A < S'Length and then White (S (S'First + A)) loop A := A + 1; end loop;
         Z := A;
         while Z < S'Length and then not White (S (S'First + Z)) loop Z := Z + 1; end loop;
         if Z > A then
            Count := Count + 1;
            if Count = Index then return S (S'First + A .. S'First + Z - 1); end if;
         end if;
         A := Z;
      end loop;
      return "";
   end Word;
   function Word_Count (S : String) return Natural is
      Count : Natural := 0;
      Inside : Boolean := False;
   begin
      for C of S loop
         if White (C) then Inside := False;
         elsif not Inside then Count := Count + 1; Inside := True; end if;
      end loop;
      return Count;
   end Word_Count;
   function Raw (Data : String; Item : J.Node) return B.Decoded is
   begin
      if Item.Form /= J.Object_Value or else J.Count (Data, Item) /= 2 or else
        not J.Is_Text (Data, J.Field (Data, Item, "encoding"), "base64") or else
        J.Field (Data, Item, "payload").Form /= J.String_Value then return (0, False, ""); end if;
      return B.Base64 (J.Text (Data, J.Field (Data, Item, "payload")));
   end Raw;
   function JSON (Bytes : String) return Worldline.Raw_JSON.Decoded_JSON is
      Data : P.Bytes (1 .. P.Count (Bytes'Length));
   begin
      for I in Bytes'Range loop Data (P.Index (I - Bytes'First + 1)) := P.Byte (Character'Pos (Bytes (I))); end loop;
      return Worldline.Raw_JSON.Decode_JSON (Data, (1, P.Count (Data'Length)));
   end JSON;
   function Fields_Valid (Data : String) return Boolean is
      A, Z, Colon : Natural := 0;
   begin
      while A < Data'Length loop
         Z := A;
         while Z < Data'Length and then Data (Data'First + Z) not in Character'Val (10) | Character'Val (13) loop Z := Z + 1; end loop;
         Colon := A;
         while Colon < Z and then Data (Data'First + Colon) /= ':' loop Colon := Colon + 1; end loop;
         if Colon = A or else Colon = Z then return False; end if;
         declare
            Key : constant String := Data (Data'First + A .. Data'First + Colon - 1);
            Previous : Natural := 0;
            End_Previous : Natural;
         begin
            while Previous < A loop
               End_Previous := Previous;
               while End_Previous < A and then Data (Data'First + End_Previous) not in ':' | Character'Val (10) | Character'Val (13) loop End_Previous := End_Previous + 1; end loop;
               if Data (Data'First + Previous .. Data'First + End_Previous - 1) = Key then return False; end if;
               while End_Previous < A and then Data (Data'First + End_Previous) not in Character'Val (10) | Character'Val (13) loop End_Previous := End_Previous + 1; end loop;
               Previous := End_Previous + 1;
               if Previous < A and then Data (Data'First + End_Previous) = Character'Val (13) and then Data (Data'First + Previous) = Character'Val (10) then Previous := Previous + 1; end if;
            end loop;
         end;
         A := Z + 1;
         if A < Data'Length and then Data (Data'First + Z) = Character'Val (13) and then Data (Data'First + A) = Character'Val (10) then A := A + 1; end if;
      end loop;
      return Data'Length > 0;
   end Fields_Valid;
   function Field (Data, Name : String) return String is
      A, Z, Colon : Natural := 0;
   begin
      while A < Data'Length loop
         Z := A;
         while Z < Data'Length and then Data (Data'First + Z) not in Character'Val (10) | Character'Val (13) loop Z := Z + 1; end loop;
         Colon := A;
         while Colon < Z and then Data (Data'First + Colon) /= ':' loop Colon := Colon + 1; end loop;
         if Data (Data'First + A .. Data'First + Colon - 1) = Name and then Colon < Z then return Strip (Data (Data'First + Colon + 1 .. Data'First + Z - 1)); end if;
         A := Z + 1;
         if A < Data'Length and then Data (Data'First + Z) = Character'Val (13) and then Data (Data'First + A) = Character'Val (10) then A := A + 1; end if;
      end loop;
      return "";
   end Field;
   function Has_Field (Data, Name : String) return Boolean is
      A, Z : Natural := 0;
   begin
      while A < Data'Length loop
         Z := A;
         while Z < Data'Length and then Data (Data'First + Z) not in ':' | Character'Val (10) | Character'Val (13) loop Z := Z + 1; end loop;
         if Z < Data'Length and then Data (Data'First + Z) = ':' and then Data (Data'First + A .. Data'First + Z - 1) = Name then return True; end if;
         while Z < Data'Length and then Data (Data'First + Z) not in Character'Val (10) | Character'Val (13) loop Z := Z + 1; end loop;
         A := Z + 1;
         if A < Data'Length and then Data (Data'First + Z) = Character'Val (13) and then Data (Data'First + A) = Character'Val (10) then A := A + 1; end if;
      end loop;
      return False;
   end Has_Field;
   function Four (S, ID : String) return Boolean is
     (Word_Count (S) = 4 and then (for all I in 1 .. 4 => Word (S, I) = ID));
   function Zero_Hex (S : String) return Boolean is
     (S'Length > 0 and then (for all C of S => C = '0'));
   function DAC_Capability (Text : String) return Boolean is
     (Text'Length > 0 and then (for all C of Text => C in '0' .. '9' | 'a' .. 'f' | 'A' .. 'F') and then
      Text (Text'Last) in '4' .. '7' | 'c' .. 'f' | 'C' .. 'F');
   function Cap_Name (Index : Positive) return String is
     (case Index is when 1 => "CapInh", when 2 => "CapPrm", when 3 => "CapEff", when 4 => "CapBnd", when others => "CapAmb");
   function NS_Name (Index : Positive) return String is
     (case Index is when 1 => "user", when 2 => "pid", when 3 => "mnt", when 4 => "net", when 5 => "ipc", when others => "uts");
   type Identity is record
      Valid : Boolean := False;
      PID, PPID, Start : U64 := 0;
   end record;
   function Process (S : String) return Identity is
      Closing, Opening : Natural := 0;
      Found : Boolean := False;
   begin
      if S'Length < 4 then return (False, 0, 0, 0); end if;
      for I in 0 .. S'Length - 2 loop
         if S (S'First + I) = ')' and then S (S'First + I + 1) = ' ' then Closing := I; Found := True; end if;
      end loop;
      if not Found then return (False, 0, 0, 0); end if;
      while Opening < Closing and then S (S'First + Opening) /= ' ' loop Opening := Opening + 1; end loop;
      if Opening + 1 >= Closing or else S (S'First + Opening + 1) /= '(' then return (False, 0, 0, 0); end if;
      declare
         Tail : constant String := S (S'First + Closing + 2 .. S'Last);
         PID : constant Number := Parse_Number (S (S'First .. S'First + Opening - 1));
         PPID : constant Number := Parse_Number (Word (Tail, 2));
         Start : constant Number := Parse_Number (Word (Tail, 20));
      begin
         return (PID.Valid and PPID.Valid and Start.Valid and Word_Count (Tail) >= 20, PID.Value, PPID.Value, Start.Value);
      end;
   end Process;
   type Map_Row is record
      Inside, Outside, Count : U64 := 0;
   end record;
   type Map_Rows is array (Positive range <>) of Map_Row;
   type Map_Result (Count : Natural) is record
      Valid : Boolean := False;
      Rows : Map_Rows (1 .. Count);
   end record;
   function Lines (S : String) return Natural is
      Count : Natural := 0;
      A : Natural := 0;
   begin
      while A < S'Length loop
         Count := Count + 1;
         while A < S'Length and then S (S'First + A) not in Character'Val (10) | Character'Val (13) loop A := A + 1; end loop;
         if A < S'Length then
            if S (S'First + A) = Character'Val (13) and then A + 1 < S'Length and then S (S'First + A + 1) = Character'Val (10) then A := A + 1; end if;
            A := A + 1;
         end if;
      end loop;
      return Count;
   end Lines;
   function Line (S : String; Index : Positive) return String is
      A, Z, Count : Natural := 0;
   begin
      while A < S'Length loop
         Z := A;
         while Z < S'Length and then S (S'First + Z) not in Character'Val (10) | Character'Val (13) loop Z := Z + 1; end loop;
         Count := Count + 1;
         if Count = Index then return S (S'First + A .. S'First + Z - 1); end if;
         A := Z;
         if A < S'Length then
            if S (S'First + A) = Character'Val (13) and then A + 1 < S'Length and then S (S'First + A + 1) = Character'Val (10) then A := A + 1; end if;
            A := A + 1;
         end if;
      end loop;
      return "";
   end Line;
   function Map (S : String) return Map_Result is
      Result : Map_Result (Lines (S));
      Limit : constant U64 := 16#1_0000_0000#;
   begin
      for I in Result.Rows'Range loop
         declare
            Row : constant String := Line (S, I);
            A : constant Number := Parse_Number (Word (Row, 1));
            B : constant Number := Parse_Number (Word (Row, 2));
            C : constant Number := Parse_Number (Word (Row, 3));
         begin
            if Word_Count (Row) /= 3 or else not A.Valid or else not B.Valid or else not C.Valid or else
              C.Value = 0 or else A.Value >= Limit or else B.Value >= Limit or else
              C.Value > Limit - A.Value or else C.Value > Limit - B.Value then return Result; end if;
            for K in Result.Rows'First .. I - 1 loop
               if not (A.Value + C.Value <= Result.Rows (K).Inside or else Result.Rows (K).Inside + Result.Rows (K).Count <= A.Value) or else
                 not (B.Value + C.Value <= Result.Rows (K).Outside or else Result.Rows (K).Outside + Result.Rows (K).Count <= B.Value) then return Result; end if;
            end loop;
            Result.Rows (I) := (A.Value, B.Value, C.Value);
         end;
      end loop;
      Result.Valid := Result.Count > 0;
      return Result;
   end Map;
   function Mapped (M : Map_Result; Inside : U64) return Number is
      Result : Number;
   begin
      if not M.Valid then return Result; end if;
      for Row of M.Rows loop
         if Inside >= Row.Inside and then Inside - Row.Inside < Row.Count then
            if Result.Valid then return (False, 0); end if;
            Result := (True, Row.Outside + Inside - Row.Inside);
         end if;
      end loop;
      return Result;
   end Mapped;
   function Nul_Word (S : String; Index : Positive) return String is
      A, Z, Count : Natural := 0;
   begin
      loop
         Z := A;
         while Z < S'Length and then S (S'First + Z) /= Character'Val (0) loop Z := Z + 1; end loop;
         Count := Count + 1;
         if Count = Index then return S (S'First + A .. S'First + Z - 1); end if;
         exit when Z = S'Length;
         A := Z + 1;
      end loop;
      return "";
   end Nul_Word;
   function Nul_Count (S : String) return Natural is
      Count : Natural := 1;
   begin for C of S loop if C = Character'Val (0) then Count := Count + 1; end if; end loop; return Count; end Nul_Count;
   function Mount_Path (S : String) return B.Decoded is
      Data : String (1 .. S'Length);
      Used, I : Natural := 0;
      C : Character;
   begin
      while I < S'Length loop
         C := S (S'First + I);
         if C = '\' then
            if S'Length - I < 4 then return (0, False, ""); end if;
            declare Escape : constant String := S (S'First + I + 1 .. S'First + I + 3);
            begin
               if Escape = "040" then C := ' ';
               elsif Escape = "011" then C := Character'Val (9);
               elsif Escape = "012" then C := Character'Val (10);
               elsif Escape = "134" then C := '\';
               else return (0, False, ""); end if;
            end;
            I := I + 3;
         end if;
         Used := Used + 1; Data (Used) := C; I := I + 1;
      end loop;
      return (Used, True, Data (1 .. Used));
   end Mount_Path;
   function Namespace_Link (S : String; Name : String := "") return Boolean is
      Colon : Natural := 0;
   begin
      while Colon < S'Length and then S (S'First + Colon) /= ':' loop Colon := Colon + 1; end loop;
      if Colon = S'Length or else S'Length - Colon < 4 or else
        S (S'First + Colon + 1) /= '[' or else S (S'Last) /= ']' then return False; end if;
      declare
         Prefix : constant String := S (S'First .. S'First + Colon - 1);
         Link_Digits : constant String := S (S'First + Colon + 2 .. S'Last - 1);
      begin
         return (if Name'Length > 0 then Prefix = Name else Prefix in "user" | "pid" | "mnt" | "net" | "ipc" | "uts" | "cgroup" | "time") and then
           Link_Digits'Length > 0 and then (for all C of Link_Digits => C in '0' .. '9');
      end;
   end Namespace_Link;
   --  Python str.split whitespace, unlike proc bytes.split's ASCII whitespace.
   --  This distinction preserves the complete original compatibility domain.
   function Unicode_White_Width (Text : String; Offset : Natural) return Natural is
      Width : constant Natural := J.UTF8_Width (Text, Offset);
      Code : Natural;
   begin
      if Width = 0 then return 0; end if;
      if Width = 1 then Code := Character'Pos (Text (Text'First + Offset));
      elsif Width = 2 then
         Code := (Character'Pos (Text (Text'First + Offset)) - 192) * 64 + Character'Pos (Text (Text'First + Offset + 1)) - 128;
      elsif Width = 3 then
         Code := (Character'Pos (Text (Text'First + Offset)) - 224) * 4096 +
           (Character'Pos (Text (Text'First + Offset + 1)) - 128) * 64 + Character'Pos (Text (Text'First + Offset + 2)) - 128;
      else return 0; end if;
      return (if Code in 9 .. 13 | 28 .. 32 | 16#85# | 16#A0# | 16#1680# |
        16#2000# .. 16#200A# | 16#2028# .. 16#2029# | 16#202F# | 16#205F# | 16#3000# then Width else 0);
   end Unicode_White_Width;
   function Python_Four (Text, ID : String) return Boolean is
      Offset, First, Count : Natural := 0;
      Width : Natural;
   begin
      while Offset < Text'Length loop
         Width := Unicode_White_Width (Text, Offset);
         while Width > 0 loop
            Offset := Offset + Width;
            exit when Offset = Text'Length;
            Width := Unicode_White_Width (Text, Offset);
         end loop;
         exit when Offset = Text'Length;
         First := Offset;
         while Offset < Text'Length and then Unicode_White_Width (Text, Offset) = 0 loop
            Width := J.UTF8_Width (Text, Offset);
            if Width = 0 then return False; end if;
            Offset := Offset + Width;
         end loop;
         Count := Count + 1;
         if Count > 4 or else Text (Text'First + First .. Text'First + Offset - 1) /= ID then return False; end if;
      end loop;
      return Count = 4;
   end Python_Four;
   function Observed_Role (Data : String; Item : J.Node; Name : String) return Boolean is
      function F (Parent : J.Node; Key : String) return J.Node is (J.Field (Data, Parent, Key));
      Status : constant J.Node := F (Item, "status");
      NS : constant J.Node := F (Item, "namespaces");
      Inside : constant String := (if Name = "examiner" then "0" elsif Name = "worker" then "1" else "2");
   begin
      if Name not in "examiner" | "worker" | "candidate" or else Item.Form /= J.Object_Value or else
        Status.Form /= J.Object_Value or else NS.Form /= J.Object_Value or else not J.Is_Text (Data, F (Item, "role"), Name) or else
        F (Item, "uid").Form /= J.Integer_Value or else J.Decimal (Data, F (Item, "uid")) /= Inside or else
        F (Item, "gid").Form /= J.Integer_Value or else J.Decimal (Data, F (Item, "gid")) /= Inside or else
        not J.Is_Text (Data, F (Status, "NoNewPrivs"), "1") or else not J.Is_Text (Data, F (Status, "Groups"), "") or else
        (if Name = "examiner" then not J.Is_True (Data, F (Item, "reportMounted")) or else not J.Is_True (Data, F (Item, "brokerMounted"))
         else not J.Is_False (Data, F (Item, "reportMounted")) or else not J.Is_False (Data, F (Item, "brokerMounted"))) or else
        (if Name = "worker" then not J.Is_True (Data, F (Item, "workerBrokerMounted")) else not J.Is_False (Data, F (Item, "workerBrokerMounted"))) then return False; end if;
      for I in 2 .. 5 loop
         if F (Status, Cap_Name (I)).Form /= J.String_Value or else not Zero_Hex (J.Text (Data, F (Status, Cap_Name (I)))) then return False; end if;
      end loop;
      for I in 1 .. 2 loop
         declare Key : constant String := (if I = 1 then "Uid" else "Gid"); Value : constant J.Node := F (Status, Key);
         begin if Value.Form /= J.String_Value or else not Python_Four (J.Text (Data, Value), Inside) then return False; end if; end;
      end loop;
      for I in 1 .. 3 loop
         declare Key : constant String := NS_Name (I); Value : constant J.Node := F (NS, Key);
         begin if Value.Form /= J.String_Value or else not Namespace_Link (J.Text (Data, Value), Key) then return False; end if; end;
      end loop;
      return True;
   end Observed_Role;
   function Original_Observed (Result_Record, Role_Name : String) return Boolean is
      Root : constant J.Node := J.Parse (Result_Record);
      Boundary : constant J.Node := J.Field (Result_Record, Root, "evaluatorBoundary");
   begin
      return Observed_Role (Result_Record, J.Field (Result_Record, Boundary, "examiner"), Role_Name);
   end Original_Observed;
   function Original_Workers_Separated (Result_Record : String) return Boolean is
      function F (Item : J.Node; Key : String) return J.Node is (J.Field (Result_Record, Item, Key));
      function A (Item : J.Node; Index : Positive) return J.Node is (J.Element (Result_Record, Item, Index));
      function Equal (Left, Right : J.Node) return Boolean is (J.Equal (Result_Record, Left, Result_Record, Right));
      function Same_Get (Left, Right : J.Node) return Boolean is
        (if Left.Form in J.Missing | J.Null_Value and then Right.Form in J.Missing | J.Null_Value then True
         else Worldline.Raw_JSON.Python_JSON_Equal
           ((if Left.Form = J.Missing then "null" else J.Slice (Result_Record, Left)),
            (if Right.Form = J.Missing then "null" else J.Slice (Result_Record, Right))));
      Root : constant J.Node := J.Parse (Result_Record);
      Boundary : constant J.Node := F (Root, "evaluatorBoundary");
      Examiner : constant J.Node := F (Boundary, "examiner");
      Workers : constant J.Node := F (Boundary, "workers");
   begin
      if not Observed_Role (Result_Record, Examiner, "examiner") or else Workers.Form /= J.Array_Value then return False; end if;
      for I in 1 .. J.Count (Result_Record, Workers) loop
         declare
            Worker : constant J.Node := A (Workers, I);
            Item : constant J.Node := F (Worker, "observation");
            Principal : constant J.Node := F (Worker, "principal");
            Name : constant String := (if Principal.Form = J.Missing then "worker" else J.Text (Result_Record, Principal));
         begin
            if Worker.Form /= J.Object_Value or else F (Worker, "returncode").Form /= J.Integer_Value or else Name not in "worker" | "candidate" or else
              not Observed_Role (Result_Record, Item, Name) or else
              not Equal (F (F (Item, "namespaces"), "user"), F (F (Examiner, "namespaces"), "user")) or else
              Equal (F (F (Item, "namespaces"), "pid"), F (F (Examiner, "namespaces"), "pid")) or else
              Equal (F (F (Item, "namespaces"), "mnt"), F (F (Examiner, "namespaces"), "mnt")) or else
              not Same_Get (F (Item, "uidMap"), F (Examiner, "uidMap")) or else not Same_Get (F (Item, "gidMap"), F (Examiner, "gidMap")) then return False; end if;
            for K in 1 .. I - 1 loop
               declare Previous : constant J.Node := F (A (Workers, K), "observation");
               begin
                  if not J.Is_Text (Result_Record, F (Previous, "role"), Name) and then
                    (Equal (F (Previous, "uid"), F (Item, "uid")) or else Equal (F (Previous, "gid"), F (Item, "gid"))) then return False; end if;
               end;
            end loop;
         end;
      end loop;
      return True;
   end Original_Workers_Separated;

   function Valid (Expected, Observed, Result_Record : String) return Boolean is
      Root : constant J.Node := J.Parse (Observed);
      Result : constant J.Node := J.Parse (Result_Record);
      Invocation : constant J.Node := J.Parse (Expected);
      function F (Item : J.Node; Key : String) return J.Node is (J.Field (Observed, Item, Key));
      function S (Item : J.Node; Key : String) return String is (J.Text (Observed, F (Item, Key)));
      function N (Item : J.Node; Key : String) return String is (J.Decimal (Observed, F (Item, Key)));
      function A (Item : J.Node; Index : Positive) return J.Node is (J.Element (Observed, Item, Index));
      function R (Item : J.Node; Key : String) return J.Node is (J.Field (Result_Record, Item, Key));
      function Equal (Left, Right : J.Node) return Boolean is (J.Equal (Observed, Left, Observed, Right));
      function Clean (Item : J.Node) return Boolean is (Item.Form = J.Object_Value and then F (Item, "exception").Form = J.Null_Value);
      function Integer_Is (Item : J.Node; Value : U64) return Boolean is
        (Item.Form = J.Integer_Value and then J.Decimal (Observed, Item) = Image (Value));
      function Acquisition (Kind : String) return J.Node is
         Found : J.Node := J.No_Node;
      begin
         for I in 1 .. J.Count (Observed, Root) loop
            declare Row : constant J.Node := A (Root, I);
            begin
               if S (Row, "kind") = Kind then
                  if J.Present (Found) then return J.No_Node; end if;
                  Found := F (Row, "observation");
               end if;
            end;
         end loop;
         return Found;
      end Acquisition;
      Plan : constant J.Node := Acquisition ("private-role-plan");
      Sources : constant J.Node := Acquisition ("private-role-source-objects");
      Returned : constant J.Node := Acquisition ("private-process-return");
      Boundary : constant J.Node := F (Returned, "boundary");
      Roles : constant J.Node := F (Boundary, "daemonRoleObservations");
      Result_Boundary : constant J.Node := R (Result, "evaluatorBoundary");
      Bootstrap, Examiner : J.Node := J.No_Node;
      function Same_Object (Left, Right : J.Node) return Boolean is
         LM : constant Number := Parse_Number (N (Left, "mode"));
         RM : constant Number := Parse_Number (N (Right, "mode"));
      begin
         return Left.Form = J.Object_Value and then Right.Form = J.Object_Value and then
           F (Left, "device").Form = J.Integer_Value and then F (Left, "inode").Form = J.Integer_Value and then
           Equal (F (Left, "device"), F (Right, "device")) and then Equal (F (Left, "inode"), F (Right, "inode")) and then
           LM.Valid and then RM.Valid and then (LM.Value and 16#F000#) = (RM.Value and 16#F000#);
      end Same_Object;
      function Identity_Matches (Actual : Identity; Item : J.Node) return Boolean is
        (Actual.Valid and then Integer_Is (F (Item, "pid"), Actual.PID) and then
         Integer_Is (F (Item, "ppid"), Actual.PPID) and then Integer_Is (F (Item, "starttime"), Actual.Start));
      function Read_Bytes (Record_Node : J.Node; Name : String; Subject : String := ""; Last : Boolean := False) return B.Decoded is
         Reads : constant J.Node := F (Record_Node, "reads");
         Found : J.Node := J.No_Node;
      begin
         for I in 1 .. J.Count (Observed, Reads) loop
            declare Row : constant J.Node := A (Reads, I);
            begin
               if S (Row, "name") = Name and then (Subject'Length = 0 or else N (Row, "subject") = Subject or else S (Row, "subject") = Subject) then
                  if not Clean (Row) or else not J.Is_True (Observed, F (Row, "returned")) or else not J.Is_True (Observed, F (Row, "eof")) then return (0, False, ""); end if;
                  if not J.Present (Found) or else Last then Found := F (Row, "bytes"); end if;
               end if;
            end;
         end loop;
         return Raw (Observed, Found);
      end Read_Bytes;
      function Namespace (Record_Node : J.Node; Name, PID : String) return J.Node is
         Found : J.Node := J.No_Node;
         Rows : constant J.Node := F (Record_Node, "namespaces");
      begin
         for I in 1 .. J.Count (Observed, Rows) loop
            declare Row : constant J.Node := A (Rows, I);
            begin
               if S (Row, "name") = Name and then N (Row, "subject") = PID then
                  if J.Present (Found) or else not Clean (Row) or else not J.Is_True (Observed, F (Row, "returned")) then return J.No_Node; end if;
                  Found := Row;
               end if;
            end;
         end loop;
         return Found;
      end Namespace;
      function Mount_Table_Valid (Text : String; Handles : J.Node) return Boolean;
      function Subject_Valid (Record_Node, Identity_Node : J.Node) return Boolean is
         PID : constant String := N (Identity_Node, "pid");
         Status : constant B.Decoded := Read_Bytes (Record_Node, "status", PID);
         Mounts : constant B.Decoded := Read_Bytes (Record_Node, "mountinfo", PID);
         Count : Natural := 0;
         Reads : constant J.Node := F (Record_Node, "reads");
         Live : constant J.Node := F (Record_Node, "liveness");
      begin
         if not Status.Valid or else not Fields_Valid (Status.Data) or else Field (Status.Data, "Pid") /= PID or else Field (Status.Data, "Tgid") /= PID then return False; end if;
         if not Mounts.Valid or else not Mount_Table_Valid (Mounts.Data, J.No_Node) or else
           not Read_Bytes (Record_Node, "cmdline", PID).Valid or else not Read_Bytes (Record_Node, "cgroup", PID).Valid then return False; end if;
         for I in 1 .. J.Count (Observed, Reads) loop
            declare Row : constant J.Node := A (Reads, I);
            begin
               if N (Row, "subject") = PID and then S (Row, "name") = "stat" then
                  declare Bytes : constant B.Decoded := Raw (Observed, F (Row, "bytes"));
                  begin
                     if not Clean (Row) or else not J.Is_True (Observed, F (Row, "returned")) or else not J.Is_True (Observed, F (Row, "eof")) or else
                       not Bytes.Valid or else not Identity_Matches (Process (Bytes.Data), Identity_Node) then return False; end if;
                     Count := Count + 1;
                  end;
               end if;
            end;
         end loop;
         if Count < 2 or else Live.Form /= J.Array_Value then return False; end if;
         Count := 0;
         for I in 1 .. J.Count (Observed, Live) loop
            declare Row : constant J.Node := A (Live, I);
            begin
               if N (Row, "pid") = PID then
                  if not J.Is_False (Observed, F (Row, "pidfdReady")) then return False; end if;
                  Count := Count + 1;
               end if;
            end;
         end loop;
         if Count < 2 then return False; end if;
         Count := 0;
         for I in 1 .. J.Count (Observed, Reads) loop
            declare Row : constant J.Node := A (Reads, I);
            begin
               if S (Row, "subject") = "receiver-pidfd" then
                  declare Bytes : constant B.Decoded := Raw (Observed, F (Row, "bytes"));
                  begin
                     if not Bytes.Valid or else not Clean (Row) or else not J.Is_True (Observed, F (Row, "returned")) or else
                       not J.Is_True (Observed, F (Row, "eof")) or else not Fields_Valid (Bytes.Data) then return False; end if;
                     if Field (Bytes.Data, "Pid") = PID then
                        if Word (Field (Bytes.Data, "NSpid"), 1) /= PID then return False; end if;
                        Count := Count + 1;
                     end if;
                  end;
               end if;
            end;
         end loop;
         if Count < 2 then return False; end if;
         for I in 1 .. 6 loop
            declare
               NS : constant J.Node := Namespace (Record_Node, NS_Name (I), PID);
               Rechecks : constant J.Node := F (Record_Node, "namespaceRechecks");
               Seen : Natural := 0;
            begin
               if NS.Form /= J.Object_Value then return False; end if;
               for K in 1 .. J.Count (Observed, Rechecks) loop
                  declare Row : constant J.Node := A (Rechecks, K);
                  begin
                     if N (Row, "pid") = PID and then S (Row, "name") = NS_Name (I) then
                        if not Same_Object (F (Row, "object"), F (NS, "object")) then return False; end if;
                        Seen := Seen + 1;
                     end if;
                  end;
               end loop;
               if Seen = 0 then return False; end if;
            end;
         end loop;
         return True;
      end Subject_Valid;
      function Raw_Maps_Equal (Left, Right : String) return Boolean is
         LM : constant Map_Result := Map (Left);
         RM : constant Map_Result := Map (Right);
      begin return LM.Valid and then RM.Valid and then LM.Rows = RM.Rows; end Raw_Maps_Equal;
      function Source (Path : String) return J.Node is
        (F (Sources, Path));
      function Record_Bound (Record_Node : J.Node; Position : Positive) return Boolean is
         Seen : Natural := 0;
      begin
         for I in 1 .. J.Count (Observed, Root) loop
            declare Row : constant J.Node := A (Root, I);
            begin
               if S (Row, "kind") = "private-kernel-role-observation" then
                  Seen := Seen + 1;
                  if Seen = Position then return Equal (F (Row, "observation"), Record_Node); end if;
               end if;
            end;
         end loop;
         return False;
      end Record_Bound;
      function Canonical_Group (Text : String) return Boolean is
         Offset, Finish : Natural := 0;
      begin
         if Text'Length = 0 or else Text (Text'First) /= '/' or else (for some C of Text => C = Character'Val (10)) then return False; end if;
         while Offset < Text'Length and then Text (Text'First + Offset) = '/' loop Offset := Offset + 1; end loop;
         if Offset > 2 then return False; end if;
         if Offset = Text'Length then return True; end if;
         while Offset < Text'Length loop
            Finish := Offset;
            while Finish < Text'Length and then Text (Text'First + Finish) /= '/' loop Finish := Finish + 1; end loop;
            if Finish = Offset or else Text (Text'First + Offset .. Text'First + Finish - 1) in "." | ".." then return False; end if;
            if Finish = Text'Length then return True; end if;
            Offset := Finish + 1;
         end loop;
         return False;
      end Canonical_Group;
      function Bootstrap_Valid return Boolean is
         ID : constant J.Node := F (Bootstrap, "identity");
         PID : constant String := N (ID, "pid");
         UID : constant B.Decoded := Read_Bytes (Bootstrap, "uid_map", PID);
         GID : constant B.Decoded := Read_Bytes (Bootstrap, "gid_map", PID);
         CG : constant B.Decoded := Read_Bytes (Bootstrap, "cgroup", PID);
         Manager : constant J.Node := F (Bootstrap, "manager");
         User : constant J.Node := Namespace (Bootstrap, "user", PID);
         Child : constant J.Node := F (Bootstrap, "roleNamespace");
         Ready : constant B.Decoded := Read_Bytes (Bootstrap, S (Plan, "runtime") & "/namespace-ready.json", "bootstrap-namespace-locator");
         function Separated (M : Map_Result; Key : String) return Boolean is
            Zero : constant Number := Mapped (M, 0);
            One : constant Number := Mapped (M, 1);
            Two : constant Number := Mapped (M, 2);
         begin
            return Zero.Valid and then One.Valid and then Two.Valid and then Integer_Is (F (Plan, Key), Zero.Value) and then
              Zero.Value /= One.Value and then Zero.Value /= Two.Value and then One.Value /= Two.Value and then One.Value /= 0 and then Two.Value /= 0;
         end Separated;
      begin
         if not Clean (Bootstrap) or else not Subject_Valid (Bootstrap, ID) or else
           not UID.Valid or else not GID.Valid or else not CG.Valid or else not Ready.Valid or else
           S (Manager, "MainPID") /= PID or else not Canonical_Group (S (Manager, "ControlGroup")) or else
           CG.Data /= "0::" & S (Manager, "ControlGroup") & Character'Val (10) or else
           not Same_Object (F (User, "parent"), F (Bootstrap, "readerUserNamespace")) or else
           not Same_Object (F (User, "parent"), F (Plan, "daemonUserNamespace")) or else
           not Equal (F (User, "ownerUid"), F (Bootstrap, "readerUid")) or else
           not Same_Object (F (Child, "parent"), F (User, "object")) or else
           Same_Object (F (Child, "object"), F (User, "object")) or else
           not Equal (F (Child, "ownerUid"), F (Plan, "operatorUid")) or else
           not Integer_Is (F (Child, "type"), 16#1000_0000#) then return False; end if;
         declare
            UM : constant Map_Result := Map (UID.Data);
            GM : constant Map_Result := Map (GID.Data);
            Decoded : constant Worldline.Raw_JSON.Decoded_JSON := JSON (Ready.Data);
            Ready_Root : constant J.Node := J.Parse (Decoded.Data);
         begin
            if not Decoded.Valid or else not J.Duplicate_Free (Decoded.Data) or else Ready_Root.Form /= J.Object_Value or else J.Count (Decoded.Data, Ready_Root) /= 4 or else
              J.Decimal (Decoded.Data, J.Field (Decoded.Data, Ready_Root, "schemaVersion")) /= "1" or else
              J.Field (Decoded.Data, Ready_Root, "schemaVersion").Form /= J.Integer_Value or else
              not J.Equal (Decoded.Data, J.Field (Decoded.Data, Ready_Root, "runId"), Observed, F (Plan, "runId")) or else
              not J.Equal (Decoded.Data, J.Field (Decoded.Data, Ready_Root, "descriptor"), Observed, F (Child, "bootstrapDescriptorNumber")) or else
              not J.Present (J.Field (Decoded.Data, Ready_Root, "setup")) then return False; end if;
            declare Descriptor : constant Number := Parse_Number (N (Child, "bootstrapDescriptorNumber"));
            begin if not Descriptor.Valid or else Descriptor.Value <= 2 then return False; end if; end;
            if not Separated (UM, "operatorUid") or else not Separated (GM, "operatorGid") then return False; end if;
         end;
         return True;
      end Bootstrap_Valid;
      function Packet_Valid (Packet, Peer : J.Node; Rights : Natural; Payload : String := "") return Boolean is
         Bytes : constant B.Decoded := Raw (Observed, F (Packet, "bytes"));
         Ancillary : constant J.Node := F (Packet, "ancillary");
         Flags : constant Number := Parse_Number (N (Packet, "flags"));
         Credentials, Descriptors : Natural := 0;
      begin
         if not Clean (Packet) or else not Bytes.Valid or else not Flags.Valid or else
           (Flags.Value and not U64 (16#4000_0080#)) /= 0 or else Bytes.Length = 0 or else Bytes.Length > 65_536 or else
           (Payload'Length > 0 and then Bytes.Data /= Payload) or else Ancillary.Form /= J.Array_Value then return False; end if;
         for I in 1 .. J.Count (Observed, Ancillary) loop
            declare
               Row : constant J.Node := A (Ancillary, I);
               Content : constant B.Decoded := Raw (Observed, F (Row, "bytes"));
            begin
               if not Integer_Is (F (Row, "level"), 1) or else not Content.Valid then return False; end if;
               if Integer_Is (F (Row, "kind"), 2) then
                  if Content.Length /= 12 or else not Integer_Is (F (Peer, "pid"), L.Word (Content.Data, 1, 4)) or else
                    not Integer_Is (F (Peer, "uid"), L.Word (Content.Data, 5, 4)) or else not Integer_Is (F (Peer, "gid"), L.Word (Content.Data, 9, 4)) then return False; end if;
                  Credentials := Credentials + 1;
               elsif Integer_Is (F (Row, "kind"), 1) then
                  if Content.Length mod 4 /= 0 then return False; end if;
                  Descriptors := Descriptors + Content.Length / 4;
               else return False; end if;
            end;
         end loop;
         return Credentials = 1 and then Descriptors = Rights;
      end Packet_Valid;
      function Command_Valid (Record_Node : J.Node; Name : String) return Boolean is
         Command : constant B.Decoded := Read_Bytes (Record_Node, "cmdline", N (F (Record_Node, "identity"), "pid"));
      begin
         if not Command.Valid or else Nul_Count (Command.Data) /= 10 or else
           Nul_Word (Command.Data, 1) /= S (Plan, "trustedInterpreter") or else
           Nul_Word (Command.Data, 2) /= "-I" or else Nul_Word (Command.Data, 3) /= "-S" or else
           Nul_Word (Command.Data, 4) /= "/run/worldline-evaluator.py" or else
           Nul_Word (Command.Data, 5) /= "--role" or else Nul_Word (Command.Data, 6) /= Name or else
           Nul_Word (Command.Data, 8) /= S (Plan, "runId") or else
           Nul_Word (Command.Data, 9) /= N (F (Bootstrap, "roleNamespace"), "bootstrapDescriptorNumber") or else
           Nul_Word (Command.Data, 10) /= "" then return False; end if;
         declare
            Payload : constant Worldline.Raw_JSON.Decoded_JSON := JSON (Nul_Word (Command.Data, 7));
            Values : constant J.Node := J.Parse (Payload.Data);
         begin
            if not Payload.Valid or else Values.Form /= J.Array_Value or else J.Count (Payload.Data, Values) = 0 then return False; end if;
            for I in 1 .. J.Count (Payload.Data, Values) loop if J.Element (Payload.Data, Values, I).Form /= J.String_Value then return False; end if; end loop;
            return Name /= "examiner" or else J.Equal (Payload.Data, Values, Observed, F (Plan, "argv"));
         end;
      end Command_Valid;
      function Ancestry_Valid (Record_Node : J.Node) return Boolean is
         Chain : constant J.Node := F (Record_Node, "ancestry");
         Reads : constant J.Node := F (Record_Node, "reads");
      begin
         if Chain.Form /= J.Array_Value or else J.Count (Observed, Chain) < 2 or else
           not Equal (A (Chain, 1), F (Record_Node, "identity")) or else
           not Equal (A (Chain, J.Count (Observed, Chain)), F (Bootstrap, "identity")) then return False; end if;
         for I in 1 .. J.Count (Observed, Chain) loop
            declare ID : constant J.Node := A (Chain, I); Count : Natural := 0;
            begin
               if I < J.Count (Observed, Chain) and then not Equal (F (ID, "ppid"), F (A (Chain, I + 1), "pid")) then return False; end if;
               for K in 1 .. I - 1 loop if Equal (F (A (Chain, K), "pid"), F (ID, "pid")) then return False; end if; end loop;
               for K in 1 .. J.Count (Observed, Reads) loop
                  declare Row : constant J.Node := A (Reads, K);
                  begin
                     if S (Row, "name") = "stat" and then Equal (F (Row, "subject"), F (ID, "pid")) then
                        declare Bytes : constant B.Decoded := Raw (Observed, F (Row, "bytes"));
                        begin
                           if not Clean (Row) or else not J.Is_True (Observed, F (Row, "returned")) or else not J.Is_True (Observed, F (Row, "eof")) or else not Bytes.Valid or else
                             not Identity_Matches (Process (Bytes.Data), ID) then return False; end if;
                           Count := Count + 1;
                        end;
                     end if;
                  end;
               end loop;
               if Count < 2 then return False; end if;
            end;
         end loop;
         return True;
      end Ancestry_Valid;
      function Filesystem_Equals (Bytes, Text : String) return Boolean is
         BI, TI : Natural := 0;
         Width : Natural;
      begin
         while TI < Text'Length loop
            Width := J.UTF8_Width (Text, TI);
            if Width = 0 or else BI >= Bytes'Length then return False; end if;
            if Width = 3 and then Character'Pos (Text (Text'First + TI)) = 16#ED# and then
              Character'Pos (Text (Text'First + TI + 1)) in 16#B2# .. 16#B3# then
               if Character'Pos (Bytes (Bytes'First + BI)) /=
                 (Character'Pos (Text (Text'First + TI + 1)) - 16#B0#) * 64 +
                   Character'Pos (Text (Text'First + TI + 2)) - 16#80# then return False; end if;
               BI := BI + 1;
            else
               if Width > Bytes'Length - BI or else
                 Bytes (Bytes'First + BI .. Bytes'First + BI + Width - 1) /=
                   Text (Text'First + TI .. Text'First + TI + Width - 1) then return False; end if;
               BI := BI + Width;
            end if;
            TI := TI + Width;
         end loop;
         return BI = Bytes'Length;
      end Filesystem_Equals;
      function Array_Words (Item : J.Node; Text : String; First : Positive := 1) return Boolean is
      begin
         if Item.Form /= J.Array_Value or else J.Count (Observed, Item) /= Word_Count (Text) - (First - 1) then return False; end if;
         for I in 1 .. J.Count (Observed, Item) loop
            if not J.Is_Text (Observed, A (Item, I), Word (Text, I + First - 1)) then return False; end if;
         end loop;
         return True;
      end Array_Words;
      function Array_Commas (Item : J.Node; Text : String) return Boolean is
         Start, Finish, Index : Natural := 0;
      begin
         if Item.Form /= J.Array_Value then return False; end if;
         loop
            Finish := Start;
            while Finish < Text'Length and then Text (Text'First + Finish) /= ',' loop Finish := Finish + 1; end loop;
            Index := Index + 1;
            if not J.Is_Text (Observed, A (Item, Index), Text (Text'First + Start .. Text'First + Finish - 1)) then return False; end if;
            exit when Finish = Text'Length;
            Start := Finish + 1;
         end loop;
         return J.Count (Observed, Item) = Index;
      end Array_Commas;
      function Mount_Marker (Text : String) return Natural is
      begin
         if Text'Length >= 3 then
            for I in 0 .. Text'Length - 3 loop
               if Text (Text'First + I .. Text'First + I + 2) = " - " then return I + 1; end if;
            end loop;
         end if;
         return 0;
      end Mount_Marker;
      function Device_Pair (Text : String; Base : Positive := 10) return Boolean is
         Colon : Natural := 0;
      begin
         while Colon < Text'Length and then Text (Text'First + Colon) /= ':' loop Colon := Colon + 1; end loop;
         return Colon < Text'Length and then Parse_Number (Text (Text'First .. Text'First + Colon - 1), Base).Valid and then
           Parse_Number (Text (Text'First + Colon + 1 .. Text'Last), Base).Valid;
      end Device_Pair;
      function Mount_Row_Valid (Text : String; Row : J.Node := J.No_Node) return Boolean is
         Marker : constant Natural := Mount_Marker (Text);
      begin
         if Marker = 0 then return False; end if;
         declare
            Before : constant String := Text (Text'First .. Text'First + Marker - 2);
            After : constant String := Text (Text'First + Marker + 2 .. Text'Last);
            ID : constant Number := Parse_Number (Word (Before, 1));
            Parent : constant Number := Parse_Number (Word (Before, 2));
            Root_Path : constant B.Decoded := Mount_Path (Word (Before, 4));
            Target : constant B.Decoded := Mount_Path (Word (Before, 5));
            Source_Path : constant B.Decoded := Mount_Path (Word (After, 2));
         begin
            if Word_Count (Before) < 6 or else Word_Count (After) /= 3 or else
              not ID.Valid or else not Parent.Valid or else not Device_Pair (Word (Before, 3)) or else
              not Root_Path.Valid or else not Target.Valid or else not Source_Path.Valid then return False; end if;
            for I in 1 .. Word_Count (Before) loop
               if I = 3 or else I = 6 or else I > 6 then
                  declare Token : constant String := Word (Before, I);
                  begin if (for some C of Token => Character'Pos (C) > 127) then return False; end if; end;
               end if;
            end loop;
            for I in 1 .. 3 loop
               if I /= 2 then
                  declare Token : constant String := Word (After, I);
                  begin if (for some C of Token => Character'Pos (C) > 127) then return False; end if; end;
               end if;
            end loop;
            if not J.Present (Row) then return True; end if;
            return Row.Form = J.Object_Value and then Integer_Is (F (Row, "id"), ID.Value) and then
              Integer_Is (F (Row, "parent"), Parent.Value) and then S (Row, "device") = Word (Before, 3) and then
              Filesystem_Equals (Root_Path.Data, S (Row, "root")) and then Filesystem_Equals (Target.Data, S (Row, "target")) and then
              Array_Commas (F (Row, "options"), Word (Before, 6)) and then Array_Words (F (Row, "optional"), Before, 7) and then
              S (Row, "filesystem") = Word (After, 1) and then Filesystem_Equals (Source_Path.Data, S (Row, "source")) and then
              Array_Commas (F (Row, "superOptions"), Word (After, 3));
         end;
      end Mount_Row_Valid;
      function Mount_Table_Valid (Text : String; Handles : J.Node) return Boolean is
      begin
         if Lines (Text) = 0 or else (J.Present (Handles) and then J.Count (Observed, Handles) /= Lines (Text)) then return False; end if;
         for I in 1 .. Lines (Text) loop
            declare
               Row : constant String := Line (Text, I);
               Marker : constant Natural := Mount_Marker (Row);
            begin
               if not Mount_Row_Valid (Row, (if J.Present (Handles) then F (A (Handles, I), "mount") else J.No_Node)) or else Marker = 0 then return False; end if;
               for K in 1 .. I - 1 loop
                  if Parse_Number (Word (Line (Text, K), 1)).Value = Parse_Number (Word (Row, 1)).Value then return False; end if;
               end loop;
            end;
         end loop;
         return True;
      end Mount_Table_Valid;
      function Linux_Major (Device : U64) return U64 is
        (((Device and 16#0000_0000_000F_FF00#) / 256) or ((Device and 16#FFFF_F000_0000_0000#) / 16#1_0000_0000#));
      function Linux_Minor (Device : U64) return U64 is
        ((Device and 16#FF#) or ((Device and 16#0000_0FFF_FFF0_0000#) / 4096));
      function Handle_Valid (Record_Node, Handle, Packet, Peer : J.Node; Index : Positive) return Boolean is
         SX : constant J.Node := F (Handle, "statx");
         Object : constant J.Node := F (Handle, "effective");
         Encoded : constant B.Decoded := Raw (Observed, F (SX, "bytes"));
         Flags : constant Number := Parse_Number (N (Handle, "descriptorFlags"));
         Device : constant Number := Parse_Number (N (Object, "device"));
         FD : Number;
         FDinfo : J.Node := J.No_Node;
         Seen : Natural := 0;
      begin
         if not Clean (Handle) or else not Flags.Valid or else (Flags.Value and 16#20_0000#) = 0 or else
           not Encoded.Valid or else Encoded.Length /= 256 or else not Device.Valid or else
           not Packet_Valid (Packet, Peer, 1, "MOUNT" & Character'Val (10)) or else
           not Integer_Is (F (SX, "return"), 0) or else not Integer_Is (F (SX, "errno"), 0) or else
           not Equal (F (Handle, "fdinfoMountId"), F (F (Handle, "mount"), "id")) then return False; end if;
         for I in 1 .. J.Count (Observed, F (Packet, "ancillary")) loop
            declare Row : constant J.Node := A (F (Packet, "ancillary"), I);
            begin
               if Integer_Is (F (Row, "kind"), 1) then
                  declare Bytes : constant B.Decoded := Raw (Observed, F (Row, "bytes"));
                  begin
                     if not Bytes.Valid or else Bytes.Length /= 4 then return False; end if;
                     FD := (True, L.Word (Bytes.Data, 1, 4));
                  end;
               end if;
            end;
         end loop;
         for I in 1 .. J.Count (Observed, F (Record_Node, "reads")) loop
            declare Row : constant J.Node := A (F (Record_Node, "reads"), I);
            begin
               if S (Row, "subject") = "receiver-mount-handle" then
                  Seen := Seen + 1;
                  if Seen = Index then FDinfo := Row; end if;
               end if;
            end;
         end loop;
         declare Bytes : constant B.Decoded := Raw (Observed, F (FDinfo, "bytes"));
         begin
            if not FD.Valid or else FD.Value >= 2 ** 31 or else not Clean (FDinfo) or else
              not J.Is_True (Observed, F (FDinfo, "returned")) or else not J.Is_True (Observed, F (FDinfo, "eof")) or else
              S (FDinfo, "name") /= "/proc/self/fdinfo/" & Image (FD.Value) or else not Bytes.Valid or else not Fields_Valid (Bytes.Data) or else
              not Integer_Is (F (Handle, "fdinfoMountId"), Parse_Number (Field (Bytes.Data, "mnt_id")).Value) or else
              not Parse_Number (Field (Bytes.Data, "mnt_id")).Valid or else not Raw (Observed, F (Handle, "fdLinkBytes")).Valid then return False; end if;
         end;
         declare
            Mask : constant U64 := L.Word (Encoded.Data, 1, 4);
            Attributes : constant U64 := L.Word (Encoded.Data, 9, 8);
            Attribute_Mask : constant U64 := L.Word (Encoded.Data, 57, 8);
            Mode : constant U64 := L.Word (Encoded.Data, 29, 2);
            Inode : constant U64 := L.Word (Encoded.Data, 33, 8);
            Major : constant U64 := L.Word (Encoded.Data, 137, 4);
            Minor : constant U64 := L.Word (Encoded.Data, 141, 4);
            Mount_ID : constant U64 := L.Word (Encoded.Data, 145, 8);
         begin
            return (Mask and 16#1103#) = 16#1103# and then (Attributes and 16#2000#) /= 0 and then (Attribute_Mask and 16#2000#) /= 0 and then
              Integer_Is (F (SX, "mask"), Mask) and then Integer_Is (F (SX, "attributes"), Attributes) and then
              Integer_Is (F (SX, "attributesMask"), Attribute_Mask) and then Integer_Is (F (SX, "mountId"), Mount_ID) and then
              Integer_Is (F (SX, "inode"), Inode) and then Integer_Is (F (SX, "mode"), Mode) and then
              Integer_Is (F (SX, "deviceMajor"), Major) and then Integer_Is (F (SX, "deviceMinor"), Minor) and then
              Integer_Is (F (Handle, "fdinfoMountId"), Mount_ID) and then Integer_Is (F (Object, "inode"), Inode) and then
              Integer_Is (F (Object, "mode"), Mode) and then Major = Linux_Major (Device.Value) and then Minor = Linux_Minor (Device.Value);
         end;
      end Handle_Valid;
      function Expected_Source (Target, Name : String) return String is
      begin
         if Target = "/run/worldline-evaluator.py" then return S (Plan, "helper");
         elsif Target = "/run/trusted.py" then return S (Plan, "startupPolicy");
         elsif Target = "/run/namespace_lifetime.py" then return S (Plan, "namespacePolicy");
         elsif Target = "/run/worldline-role-observer.sock" then return S (Plan, "runtime") & "/role-observer.sock";
         elsif Name = "examiner" then
            if Target = "/run/worldline-verifiers" then return S (Plan, "verifier");
            elsif Target = "/run/worldline-report" then return S (Plan, "report");
            elsif Target = "/run/worldline-broker.sock" then return S (Plan, "runtime") & "/broker.sock";
            elsif Target = "/run/worldline-loader-policy.json" then return S (Plan, "loaderPolicy");
            elsif Target = "/run/worldline-examiner-loader.py" then return S (Plan, "loaderHelper");
            elsif Target = "/run/worldline-examiner-guard.so" then return S (Plan, "nativeGuard");
            elsif Target = "/run/worldline-native-preparation.sock" then return S (Plan, "nativePreparationSocket");
            elsif Target = "/run/worldline-native-lifetime.sock" then return S (Plan, "nativeLifetimeSocket");
            elsif Target = "/opt/worldline-gnat" then return S (F (Plan, "toolchain"), "source");
            elsif Target = "/run/worldline-protected-report.sock" then return S (Plan, "protectedReportSocket");
            end if;
            for I in 1 .. J.Count (Observed, F (Plan, "roots")) loop
               declare Row : constant J.Node := A (F (Plan, "roots"), I);
               begin if S (Row, "target") = Target then return S (Row, "frozen"); end if; end;
            end loop;
            for I in 1 .. J.Count (Observed, F (Plan, "protectedSourceMounts")) loop
               declare Row : constant J.Node := A (F (Plan, "protectedSourceMounts"), I);
               begin if S (Row, "target") = Target then return S (Row, "source"); end if; end;
            end loop;
         elsif Name = "worker" and then Target = "/run/worldline-worker-broker.sock" then
            return S (Plan, "runtime") & "/worker-broker.sock";
         end if;
         return "";
      end Expected_Source;
      type Mount_Kind is (No_Mount, Helper_Mount, Startup_Mount, Namespace_Mount, Observer_Mount,
         Verifier_Mount, Report_Mount, Broker_Mount, Root_Mount, Protected_Source_Mount, Protected_Socket_Mount,
         Loader_Policy_Mount, Loader_Helper_Mount, Native_Mount, Preparation_Mount, Lifetime_Mount, Toolchain_Mount, Worker_Mount);
      type Mount_Slot is record
         Kind : Mount_Kind;
         Index : Natural := 0;
      end record;
      function Slot (Name : String; Index : Positive) return Mount_Slot is
         Offset : Natural := Index;
         Roots_Count : constant Natural := J.Count (Observed, F (Plan, "roots"));
         Protected_Count : constant Natural := J.Count (Observed, F (Plan, "protectedSourceMounts"));
      begin
         if Index <= 4 then
            return (case Index is when 1 => (Helper_Mount, 0), when 2 => (Startup_Mount, 0),
              when 3 => (Namespace_Mount, 0), when others => (Observer_Mount, 0));
         end if;
         if Name = "worker" then return (if Index = 5 then (Worker_Mount, 0) else (No_Mount, 0)); end if;
         if Name /= "examiner" then return (No_Mount, 0); end if;
         if Index <= 7 then return (case Index is when 5 => (Verifier_Mount, 0), when 6 => (Report_Mount, 0), when others => (Broker_Mount, 0)); end if;
         Offset := Offset - 7;
         if Offset <= Roots_Count then return (Root_Mount, Offset); end if;
         Offset := Offset - Roots_Count;
         if Offset <= Protected_Count then return (Protected_Source_Mount, Offset); end if;
         Offset := Offset - Protected_Count;
         if J.Present (F (Plan, "protectedReportSocket")) then
            if Offset = 1 then return (Protected_Socket_Mount, 0); end if;
            Offset := Offset - 1;
         end if;
         if J.Present (F (Plan, "loaderPolicy")) then
            if Offset <= 2 then return (if Offset = 1 then (Loader_Policy_Mount, 0) else (Loader_Helper_Mount, 0)); end if;
            Offset := Offset - 2;
         end if;
         if J.Present (F (Plan, "nativeGuard")) then
            if Offset <= 3 then return (case Offset is when 1 => (Native_Mount, 0), when 2 => (Preparation_Mount, 0), when others => (Lifetime_Mount, 0)); end if;
            Offset := Offset - 3;
         end if;
         return (if Offset = 1 and then J.Truth (Observed, F (Plan, "toolchain")) then (Toolchain_Mount, 0) else (No_Mount, 0));
      end Slot;
      function Slot_Target (Item : Mount_Slot) return String is
        (case Item.Kind is when Helper_Mount => "/run/worldline-evaluator.py", when Startup_Mount => "/run/trusted.py",
         when Namespace_Mount => "/run/namespace_lifetime.py", when Observer_Mount => "/run/worldline-role-observer.sock",
         when Verifier_Mount => "/run/worldline-verifiers", when Report_Mount => "/run/worldline-report",
         when Broker_Mount => "/run/worldline-broker.sock", when Worker_Mount => "/run/worldline-worker-broker.sock",
         when Root_Mount => S (A (F (Plan, "roots"), Item.Index), "target"),
         when Protected_Source_Mount => S (A (F (Plan, "protectedSourceMounts"), Item.Index), "target"),
         when Protected_Socket_Mount => "/run/worldline-protected-report.sock",
         when Loader_Policy_Mount => "/run/worldline-loader-policy.json", when Loader_Helper_Mount => "/run/worldline-examiner-loader.py",
         when Native_Mount => "/run/worldline-examiner-guard.so", when Preparation_Mount => "/run/worldline-native-preparation.sock",
         when Lifetime_Mount => "/run/worldline-native-lifetime.sock", when Toolchain_Mount => "/opt/worldline-gnat", when No_Mount => "");
      function Slot_Source (Item : Mount_Slot) return String is
        (case Item.Kind is when Helper_Mount => S (Plan, "helper"), when Startup_Mount => S (Plan, "startupPolicy"),
         when Namespace_Mount => S (Plan, "namespacePolicy"), when Observer_Mount => S (Plan, "runtime") & "/role-observer.sock",
         when Verifier_Mount => S (Plan, "verifier"), when Report_Mount => S (Plan, "report"),
         when Broker_Mount => S (Plan, "runtime") & "/broker.sock", when Worker_Mount => S (Plan, "runtime") & "/worker-broker.sock",
         when Root_Mount => S (A (F (Plan, "roots"), Item.Index), "frozen"),
         when Protected_Source_Mount => S (A (F (Plan, "protectedSourceMounts"), Item.Index), "source"),
         when Protected_Socket_Mount => S (Plan, "protectedReportSocket"),
         when Loader_Policy_Mount => S (Plan, "loaderPolicy"), when Loader_Helper_Mount => S (Plan, "loaderHelper"),
         when Native_Mount => S (Plan, "nativeGuard"), when Preparation_Mount => S (Plan, "nativePreparationSocket"),
         when Lifetime_Mount => S (Plan, "nativeLifetimeSocket"), when Toolchain_Mount => S (F (Plan, "toolchain"), "source"), when No_Mount => "");
      function Reserved (I : Positive) return String is
        (case I is when 1 => "/run/worldline-report", when 2 => "/run/worldline-broker.sock",
         when 3 => "/run/worldline-worker-broker.sock", when 4 => "/run/worldline-verifiers",
         when 5 => "/opt/worldline-gnat", when 6 => "/run/worldline-loader-policy.json",
         when 7 => "/run/worldline-examiner-loader.py", when 8 => "/run/worldline-examiner-guard.so",
         when 9 => "/run/worldline-native-preparation.sock", when 10 => "/run/worldline-native-lifetime.sock",
         when others => "/run/worldline-protected-report.sock");
      function Mounts_Valid (Record_Node : J.Node; Name : String) return Boolean is
         PID : constant String := N (F (Record_Node, "identity"), "pid");
         Before : constant B.Decoded := Read_Bytes (Record_Node, "mountinfo", PID);
         After : constant B.Decoded := Read_Bytes (Record_Node, "mountinfo", PID, True);
         Handles : constant J.Node := F (Record_Node, "mountHandles");
         Objects : constant J.Node := F (Record_Node, "mountObjects");
         Packets : constant J.Node := F (Record_Node, "packets");
         Absent : constant J.Node := F (Record_Node, "absentPaths");
         Aliases : constant J.Node := F (Record_Node, "reportDirectoryMountRootsAtStartup");
         Expected_Count : Natural := 4;
         Absent_Count : Natural := 0;
         Alias_Count : Natural := 0;
         function Aliases_Valid (Path, Target : String; Projection : J.Node) return Boolean is
            Count : Natural := 0;
         begin
            for K in 1 .. J.Count (Observed, Handles) loop
               declare Handle : constant J.Node := A (Handles, K);
               begin
                  if Same_Object (Source (Path), F (Handle, "effective")) then
                     Count := Count + 1;
                     if Name /= "examiner" or else S (F (Handle, "mount"), "target") /= Target then return False; end if;
                  end if;
               end;
            end loop;
            return Count = (if Name = "examiner" then 1 else 0) and then Projection.Form = J.Array_Value and then
              J.Count (Observed, Projection) = Count and then (Count = 0 or else J.Is_Text (Observed, A (Projection, 1), Target));
         end Aliases_Valid;
      begin
         if Name = "examiner" then
            Expected_Count := Expected_Count + 3 + J.Count (Observed, F (Plan, "roots"));
            Expected_Count := Expected_Count + J.Count (Observed, F (Plan, "protectedSourceMounts"));
            if J.Present (F (Plan, "protectedReportSocket")) then Expected_Count := Expected_Count + 1; end if;
            if J.Present (F (Plan, "loaderPolicy")) then Expected_Count := Expected_Count + 2; end if;
            if J.Present (F (Plan, "nativeGuard")) then Expected_Count := Expected_Count + 3; end if;
            if J.Truth (Observed, F (Plan, "toolchain")) then Expected_Count := Expected_Count + 1; end if;
         elsif Name = "worker" then Expected_Count := Expected_Count + 1; end if;
         if not Before.Valid or else not After.Valid or else not Mount_Table_Valid (Before.Data, Handles) or else
           not Mount_Table_Valid (After.Data, Handles) or else Objects.Form /= J.Array_Value or else
           J.Count (Observed, Objects) /= Expected_Count or else J.Count (Observed, Packets) < J.Count (Observed, Handles) + 1 then return False; end if;
         for I in 1 .. J.Count (Observed, Handles) loop
            declare Handle : constant J.Node := A (Handles, I);
            begin
               if not Handle_Valid (Record_Node, Handle, A (Packets, I + 1), F (Record_Node, "peerCredentials"), I) then return False; end if;
               if Same_Object (Source (S (Plan, "report")), F (Handle, "effective")) then
                  Alias_Count := Alias_Count + 1;
                  if Name /= "examiner" or else S (F (Handle, "mount"), "target") /= "/run/worldline-report" then return False; end if;
               end if;
            end;
         end loop;
         if Alias_Count /= (if Name = "examiner" then 1 else 0) or else Aliases.Form /= J.Array_Value or else J.Count (Observed, Aliases) /= Alias_Count or else
           (Alias_Count = 1 and then not J.Is_Text (Observed, A (Aliases, 1), "/run/worldline-report")) then return False; end if;
         if J.Count (Observed, F (Record_Node, "protectedSourceMountRootsAtStartup")) /= J.Count (Observed, F (Plan, "protectedSourceMounts")) then return False; end if;
         for I in 1 .. J.Count (Observed, F (Plan, "protectedSourceMounts")) loop
            declare
               Mount : constant J.Node := A (F (Plan, "protectedSourceMounts"), I);
               Projection : constant J.Node := A (F (Record_Node, "protectedSourceMountRootsAtStartup"), I);
            begin
               if not Equal (F (Projection, "source"), Source (S (Mount, "source"))) or else
                 not Aliases_Valid (S (Mount, "source"), S (Mount, "target"), F (Projection, "mountRoots")) then return False; end if;
            end;
         end loop;
         if J.Present (F (Plan, "protectedReportSocket")) and then
           not Aliases_Valid (S (Plan, "protectedReportSocket"), "/run/worldline-protected-report.sock", F (Record_Node, "protectedReportSocketMountRootsAtStartup")) then return False; end if;
         for I in 1 .. J.Count (Observed, Objects) loop
            declare
               Object : constant J.Node := A (Objects, I);
               Expected_Slot : constant Mount_Slot := Slot (Name, I);
               Target : constant String := Slot_Target (Expected_Slot);
               Planned_Source : constant String := Slot_Source (Expected_Slot);
               Read_Only : constant Boolean := Expected_Slot.Kind not in Report_Mount | Broker_Mount | Worker_Mount;
               Held : constant J.Node := Source (Planned_Source);
               Match_Count : Natural := 0;
            begin
               if S (Object, "target") /= Target or else Planned_Source'Length = 0 or else not Same_Object (F (Object, "source"), F (Object, "effective")) then return False; end if;
               if Expected_Slot.Kind not in Broker_Mount | Worker_Mount then
                  if not Same_Object (Held, F (Object, "source")) or else not Equal (Held, F (Object, "sourceBeforeLaunch")) then return False; end if;
                  declare Mode : constant Number := Parse_Number (N (Held, "mode"));
                  begin
                     if not Mode.Valid or else ((Mode.Value and 16#F000#) = 16#8000# and then not Equal (Held, F (Object, "source"))) then return False; end if;
                  end;
               end if;
               for K in 1 .. J.Count (Observed, Handles) loop
                  declare Handle : constant J.Node := A (Handles, K);
                  begin
                     if S (F (Handle, "mount"), "target") = Target then
                        Match_Count := Match_Count + 1;
                        if not Equal (F (Object, "effective"), F (Handle, "effective")) or else not Equal (F (Object, "mount"), F (Handle, "mount")) then return False; end if;
                        declare
                           Options : constant J.Node := F (F (Handle, "mount"), "options");
                           RO, RW : Boolean := False;
                        begin
                           for X in 1 .. J.Count (Observed, Options) loop
                              RO := RO or J.Is_Text (Observed, A (Options, X), "ro");
                              RW := RW or J.Is_Text (Observed, A (Options, X), "rw");
                           end loop;
                           if RO /= Read_Only or else RW = Read_Only then return False; end if;
                        end;
                     end if;
                  end;
               end loop;
               if Match_Count /= 1 then return False; end if;
            end;
         end loop;
         for I in 1 .. (if J.Present (F (Plan, "protectedReportSocket")) then 11 else 10) loop
            declare
               Target : constant String := Reserved (I);
               Required : constant Boolean := Expected_Source (Target, Name)'Length > 0;
               Count : Natural := 0;
            begin
               for K in 1 .. J.Count (Observed, Absent) loop
                  declare Item : constant J.Node := A (Absent, K);
                  begin
                     if S (Item, "target") = Target then
                        Count := Count + 1;
                        if not Integer_Is (F (Item, "observedErrno"), 2) then return False; end if;
                     end if;
                  end;
               end loop;
               if Count /= (if Required then 0 else 1) then return False; end if;
               Absent_Count := Absent_Count + Count;
            end;
         end loop;
         return Absent.Form = J.Array_Value and then J.Count (Observed, Absent) = Absent_Count;
      end Mounts_Valid;
      function Completion_Valid (Record_Node : J.Node) return Boolean is
         Rows : constant J.Node := F (Record_Node, "processCleanup");
      begin
         if Rows.Form /= J.Array_Value or else J.Count (Observed, Rows) /= 1 then return False; end if;
         declare
            Row : constant J.Node := A (Rows, 1);
            Attempts : constant J.Node := F (Row, "attempts");
            Attempt : constant J.Node := A (Attempts, 1);
            Stdout : constant B.Decoded := Raw (Observed, F (Attempt, "stdout"));
            Stderr : constant B.Decoded := Raw (Observed, F (Attempt, "stderr"));
            Maximum_Output : constant Number := Parse_Number (N (Plan, "maximumOutputBytes"));
         begin
            return J.Is_False (Observed, F (Row, "killed")) and then Integer_Is (F (Row, "returncode"), 0) and then
              Attempts.Form = J.Array_Value and then J.Count (Observed, Attempts) = 1 and then Clean (Attempt) and then
              J.Is_True (Observed, F (Attempt, "waitReturned")) and then J.Is_True (Observed, F (Attempt, "eof")) and then
              Integer_Is (F (Attempt, "returncode"), 0) and then
              F (Plan, "maximumOutputBytes").Form = J.Integer_Value and then Maximum_Output.Valid and then
              Stdout.Valid and then Stderr.Valid and then
              U64 (Stdout.Length) <= Maximum_Output.Value and then U64 (Stderr.Length) <= Maximum_Output.Value;
         end;
      end Completion_Valid;
      function Completion (Kind : String; ID : J.Node) return J.Node is
         Found : J.Node := J.No_Node;
      begin
         for I in 1 .. J.Count (Observed, Roles) loop
            declare Row : constant J.Node := A (Roles, I);
            begin
               if S (Row, "kind") = Kind and then Equal (F (Row, "recordId"), ID) then
                  if J.Present (Found) then return J.No_Node; end if;
                  Found := Row;
               end if;
            end;
         end loop;
         return Found;
      end Completion;
      function Helper_Command (Record_Node : J.Node; Kind : String; Identity_Node : J.Node) return Boolean is
         Command : constant B.Decoded := Read_Bytes (Record_Node, "cmdline", N (Identity_Node, "pid"));
         Arguments : constant J.Node := F (Record_Node, "command");
      begin
         if not Command.Valid or else Arguments.Form /= J.Array_Value or else
           J.Count (Observed, Arguments) < 5 or else Nul_Count (Command.Data) /= J.Count (Observed, Arguments) + 1 or else
           not J.Is_Text (Observed, A (Arguments, 1), S (Plan, "trustedInterpreter")) or else
           not J.Is_Text (Observed, A (Arguments, 2), "-I") or else not J.Is_Text (Observed, A (Arguments, 3), "-S") or else
           not J.Is_Text (Observed, A (Arguments, 4), S (Plan, "namespacePolicy")) or else
           not J.Is_Text (Observed, A (Arguments, 5), Kind) then return False; end if;
         for I in 1 .. J.Count (Observed, Arguments) loop
            if A (Arguments, I).Form /= J.String_Value or else not Filesystem_Equals (Nul_Word (Command.Data, I), J.Text (Observed, A (Arguments, I))) then return False; end if;
         end loop;
         return Nul_Word (Command.Data, J.Count (Observed, Arguments) + 1) = "";
      end Helper_Command;
      function Retained_Control (Packet : J.Node) return Boolean is
         Bytes : constant B.Decoded := Raw (Observed, F (Packet, "bytes"));
         Decoded : constant Worldline.Raw_JSON.Decoded_JSON := JSON (Bytes.Data);
         Document : constant J.Node := J.Parse (Decoded.Data);
      begin
         return Clean (Packet) and then S (Packet, "direction") = "send" and then Bytes.Valid and then Bytes.Length <= 65_536 and then
           Integer_Is (F (Packet, "return"), U64 (Bytes.Length)) and then Decoded.Valid and then Document.Form = J.Object_Value and then
           J.Count (Decoded.Data, Document) = 1 and then J.Is_Text (Decoded.Data, J.Field (Decoded.Data, Document, "state"), "retained");
      end Retained_Control;
      function Descriptor_Valid (Record_Node : J.Node) return Boolean is
         Reader : constant J.Node := F (Record_Node, "descriptorReader");
         First : constant J.Node := F (Reader, "beginObservation");
         Final : constant J.Node := F (Reader, "observation");
         Inventory : constant J.Node := F (Record_Node, "inheritedDescriptorInventory");
         Reads : constant J.Node := F (Final, "reads");
         Packets : constant J.Node := F (Reader, "packets");
         ID : constant J.Node := F (Record_Node, "identity");
         Reader_ID : constant J.Node := F (Reader, "readerIdentity");
         Role_NS : constant J.Node := F (F (Bootstrap, "roleNamespace"), "object");
         Count : constant Natural := J.Count (Observed, Inventory);
         Used : U64 := 0;
         Previous : U64 := 0;
         Source_Bytes : constant B.Decoded := Read_Bytes (Reader, S (Plan, "namespacePolicy"), "descriptor-reader-source");
         Done : constant J.Node := Completion ("role-descriptor-reader-completion", F (Reader, "recordId"));
      begin
         if not Clean (Reader) or else not Clean (First) or else not Clean (Final) or else
           not Source_Bytes.Valid or else B.Digest (Source_Bytes.Data) /= S (Plan, "namespacePolicySha256") or else
           not Subject_Valid (Reader, Reader_ID) or else not Helper_Command (Reader, "--descriptor-reader", Reader_ID) or else
           not Equal (F (Reader_ID, "ppid"), F (Reader, "readerPid")) or else
           not Equal (F (Reader, "targetIdentity"), ID) or else not Equal (F (Final, "subjectIdentity"), ID) or else
           not Equal (F (Final, "subjectIdentityAfter"), ID) or else
           not Same_Object (F (Final, "subjectProc"), F (Record_Node, "procDirectory")) or else
           not Same_Object (F (Final, "subjectPidfd"), F (Reader, "subjectPidfdObject")) or else
           not Same_Object (F (Final, "beforeNamespace"), F (Reader, "readerUserNamespace")) or else
           not Integer_Is (F (Final, "entryCount"), U64 (Count)) or else
           not J.Is_True (Observed, F (First, "enumerationReturned")) or else not J.Is_True (Observed, F (Final, "enumerationReturned")) or else
           Inventory.Form /= J.Array_Value or else Reads.Form /= J.Array_Value or else J.Count (Observed, Reads) /= 5 or else
           not Completion_Valid (Done) then return False; end if;
         for I in 1 .. J.Count (Observed, Reader) loop
            declare Key : constant String := J.Member_Name (Observed, Reader, I);
            begin if Key /= "kind" and then not Equal (F (Reader, Key), F (Done, Key)) then return False; end if; end;
         end loop;
         for I in 1 .. J.Count (Observed, First) loop
            declare Key : constant String := J.Member_Name (Observed, First, I);
            begin
               if Key not in "reads" | "subjectLiveness" and then not Equal (F (First, Key), F (Final, Key)) then return False; end if;
            end;
         end loop;
         for I in 1 .. 3 loop
            declare Key : constant String := (if I = 1 then "requestedNamespace" elsif I = 2 then "readerNamespace" else "afterNamespace");
            begin if not Same_Object (F (Final, Key), Role_NS) then return False; end if; end;
         end loop;
         if not Same_Object (F (Namespace (Reader, "user", N (Reader_ID, "pid")), "object"), Role_NS) then return False; end if;
         for I in 1 .. 2 loop
            declare
               Name : constant String := (if I = 1 then "uid_map" else "gid_map");
               RM : constant B.Decoded := Read_Bytes (Reader, Name, N (Reader_ID, "pid"));
               SM : constant B.Decoded := Read_Bytes (Record_Node, Name, N (ID, "pid"));
            begin if not RM.Valid or else not SM.Valid or else not Raw_Maps_Equal (RM.Data, SM.Data) then return False; end if; end;
         end loop;
         declare
            Status : constant B.Decoded := Read_Bytes (Reader, "status", N (Reader_ID, "pid"));
            CG : constant B.Decoded := Read_Bytes (Reader, "cgroup", N (Reader_ID, "pid"));
            Parent_CG : constant B.Decoded := Read_Bytes (Reader, "/proc/self/cgroup", "descriptor-reader-parent");
            Caps : constant String := Field (Status.Data, "CapEff");
         begin
            if not Status.Valid or else not CG.Valid or else not Parent_CG.Valid or else CG.Data /= Parent_CG.Data or else
              not Four (Field (Status.Data, "Uid"), N (Plan, "operatorUid")) or else
              not Four (Field (Status.Data, "Gid"), N (Plan, "operatorGid")) or else not DAC_Capability (Caps) then return False; end if;
         end;
         for I in 1 .. 5 loop
            declare
               Row : constant J.Node := A (Reads, I);
               Bytes : constant B.Decoded := Raw (Observed, F (Row, "bytes"));
               Path : constant String := (if I = 1 then "/proc/self/status" elsif I in 2 | 4 then "stat"
                 else "/proc/self/fdinfo/" & N (Reader, "subjectPidfdNumber"));
            begin
               if not Clean (Row) or else not J.Is_True (Observed, F (Row, "returned")) or else not J.Is_True (Observed, F (Row, "eof")) or else
                 S (Row, "path") /= Path or else not Bytes.Valid then return False; end if;
               if I <= 3 and then not Equal (A (F (First, "reads"), I), Row) then return False; end if;
               if I in 2 | 4 then
                  if not Identity_Matches (Process (Bytes.Data), ID) then return False; end if;
               elsif not Fields_Valid (Bytes.Data) then return False;
               elsif I = 1 then
                  if not DAC_Capability (Field (Bytes.Data, "CapEff")) then return False; end if;
               elsif Field (Bytes.Data, "Pid") /= N (ID, "pid") then return False;
               end if;
               if U64 (Bytes.Length) > U64'Last - Used then return False; end if;
               Used := Used + U64 (Bytes.Length);
            end;
         end loop;
         if J.Count (Observed, F (First, "reads")) /= 3 or else
           J.Count (Observed, F (First, "subjectLiveness")) /= 1 or else J.Count (Observed, F (Final, "subjectLiveness")) /= 2 then return False; end if;
         for I in 1 .. 2 loop
            declare Row : constant J.Node := A (F (Final, "subjectLiveness"), I);
            begin
               if S (Row, "phase") /= (if I = 1 then "before" else "after") or else not J.Is_False (Observed, F (Row, "pidfdReady")) or else
                 (I = 1 and then not Equal (Row, A (F (First, "subjectLiveness"), 1))) then return False; end if;
            end;
         end loop;
         -- Packets are redecoded rather than accepting enumerationComplete.
         if Packets.Form /= J.Array_Value or else J.Count (Observed, Packets) /= Count + 3 then return False; end if;
         for I in 1 .. Count + 2 loop
            declare
               Packet : constant J.Node := A (Packets, I);
               Bytes : constant B.Decoded := Raw (Observed, F (Packet, "bytes"));
               Decoded : constant Worldline.Raw_JSON.Decoded_JSON := JSON (Bytes.Data);
               Document : constant J.Node := J.Parse (Decoded.Data);
               Flags : constant Number := Parse_Number (N (Packet, "flags"));
            begin
               if not Clean (Packet) or else S (Packet, "direction") /= "receive" or else not Bytes.Valid or else
                 Bytes.Length = 0 or else Bytes.Length > 65_536 or else
                 not Decoded.Valid or else not Flags.Valid or else (Flags.Value and not U64 (16#80#)) /= 0 then return False; end if;
               if I in 1 | Count + 2 then
                  if Document.Form /= J.Object_Value or else J.Count (Decoded.Data, Document) /= 2 or else
                    not J.Is_Text (Decoded.Data, J.Field (Decoded.Data, Document, "state"), (if I = 1 then "begin" else "observed")) or else
                    not J.Equal (Decoded.Data, J.Field (Decoded.Data, Document, "observation"), Observed, (if I = 1 then First else Final)) then return False; end if;
               else
                  declare
                     Descriptor_Entry : constant J.Node := A (Inventory, I - 1);
                     Number_Text : constant String := S (Descriptor_Entry, "number");
                     Number_Value : constant Number := Parse_Number (Number_Text);
                     Link : constant B.Decoded := Raw (Observed, F (Descriptor_Entry, "linkBytes"));
                  begin
                     if Document.Form /= J.Object_Value or else J.Count (Decoded.Data, Document) /= 4 or else
                       not J.Is_Text (Decoded.Data, J.Field (Decoded.Data, Document, "state"), "entry") or else
                       J.Field (Decoded.Data, Document, "index").Form /= J.Integer_Value or else
                       J.Decimal (Decoded.Data, J.Field (Decoded.Data, Document, "index")) /= Image (U64 (I - 2)) or else
                       not J.Equal (Decoded.Data, J.Field (Decoded.Data, Document, "number"), Observed, F (Descriptor_Entry, "number")) or else
                       not J.Equal (Decoded.Data, J.Field (Decoded.Data, Document, "linkBytes"), Observed, F (Descriptor_Entry, "linkBytes")) or else
                       F (Descriptor_Entry, "number").Form /= J.String_Value or else not Number_Value.Valid or else Number_Text /= Image (Number_Value.Value) or else
                       (I > 2 and then Number_Value.Value <= Previous) or else not Link.Valid or else Link.Length = 0 or else
                       (for some C of Link.Data => C = Character'Val (0)) or else Namespace_Link (Link.Data) then return False; end if;
                     Previous := Number_Value.Value;
                     if U64 (Number_Text'Length) > U64'Last - Used or else U64 (Link.Length) > U64'Last - Used - U64 (Number_Text'Length) then return False; end if;
                     Used := Used + U64 (Number_Text'Length) + U64 (Link.Length);
                  end;
               end if;
            end;
         end loop;
         declare
            Budget : constant Number := Parse_Number (J.Text (Observed, A (F (Reader, "command"), 12)));
         begin
            if not Retained_Control (A (Packets, Count + 3)) or else not Budget.Valid or else Used > Budget.Value or else
              J.Count (Observed, F (Reader, "command")) /= 12 then return False; end if;
         end;
         return Integer_Is (F (Final, "rawBytesUsed"), Used) and then
           J.Is_Text (Observed, A (F (Reader, "command"), 9), N (Reader, "subjectPidfdNumber"));
      end Descriptor_Valid;
      function Native_Mapping_Valid (Record_Node : J.Node) return Boolean is
         Mapping : constant J.Node := F (Record_Node, "nativeArtifactMapping");
         Held : constant J.Node := Source (S (Plan, "nativeGuard"));
         Device : constant Number := Parse_Number (N (Held, "device"));
         Bytes : constant B.Decoded := Read_Bytes (Record_Node, "maps", N (F (Record_Node, "identity"), "pid"));
         Selected : constant J.Node := F (Mapping, "mappings");
         Count : Natural := 0;
         Executable : Boolean := False;
      begin
         if not Device.Valid or else not Bytes.Valid or else Lines (Bytes.Data) = 0 or else Selected.Form /= J.Array_Value or else
           not Equal (Held, F (Mapping, "heldSource")) or else not Equal (Held, F (Record_Node, "nativeSourceCurrent")) or else
           not Equal (F (Mapping, "binding"), F (Plan, "nativeGuardBinding")) then return False; end if;
         for I in 1 .. Lines (Bytes.Data) loop
            declare
               Text : constant String := Line (Bytes.Data, I);
               Range_Text : constant String := Word (Text, 1);
               Permissions : constant String := Word (Text, 2);
               Device_Text : constant String := Word (Text, 4);
               Dash, Colon : Natural := 0;
            begin
               while Dash < Range_Text'Length and then Range_Text (Range_Text'First + Dash) /= '-' loop Dash := Dash + 1; end loop;
               while Colon < Device_Text'Length and then Device_Text (Device_Text'First + Colon) /= ':' loop Colon := Colon + 1; end loop;
               if Word_Count (Text) < 5 or else Dash = Range_Text'Length or else Colon = Device_Text'Length or else Permissions'Length /= 4 or else
                 Permissions (Permissions'First) not in 'r' | '-' or else Permissions (Permissions'First + 1) not in 'w' | '-' or else
                 Permissions (Permissions'First + 2) not in 'x' | '-' or else Permissions (Permissions'First + 3) not in 'p' | 's' then return False; end if;
               declare
                  Start : constant Number := Parse_Number (Range_Text (Range_Text'First .. Range_Text'First + Dash - 1), 16);
                  Finish : constant Number := Parse_Number (Range_Text (Range_Text'First + Dash + 1 .. Range_Text'Last), 16);
                  Offset : constant Number := Parse_Number (Word (Text, 3), 16);
                  Major : constant Number := Parse_Number (Device_Text (Device_Text'First .. Device_Text'First + Colon - 1), 16);
                  Minor : constant Number := Parse_Number (Device_Text (Device_Text'First + Colon + 1 .. Device_Text'Last), 16);
                  Inode : constant Number := Parse_Number (Word (Text, 5));
                  A_Offset, End_Offset, Words : Natural := 0;
               begin
                  if not Start.Valid or else not Finish.Valid or else Start.Value >= Finish.Value or else not Offset.Valid or else
                    not Major.Valid or else not Minor.Valid or else not Inode.Valid or else
                    (for some C of Range_Text => C in 'A' .. 'F') or else
                    (for some C of Device_Text => C in 'A' .. 'F') or else
                    (for some C of Word (Text, 3) => C in 'A' .. 'F') then return False; end if;
                  if Integer_Is (F (Held, "inode"), Inode.Value) and then Major.Value = Linux_Major (Device.Value) and then Minor.Value = Linux_Minor (Device.Value) then
                     Count := Count + 1;
                     declare Row : constant J.Node := A (Selected, Count);
                     begin
                        if not Integer_Is (F (Row, "start"), Start.Value) or else not Integer_Is (F (Row, "end"), Finish.Value) or else
                          S (Row, "permissions") /= Permissions or else not Integer_Is (F (Row, "offset"), Offset.Value) or else
                          not Integer_Is (F (Row, "deviceMajor"), Major.Value) or else not Integer_Is (F (Row, "deviceMinor"), Minor.Value) or else
                          not Integer_Is (F (Row, "inode"), Inode.Value) then return False; end if;
                        Executable := Executable or Permissions (Permissions'First + 2) = 'x';
                        if Permissions (Permissions'First + 1) = 'w' and then Permissions (Permissions'First + 2) = 'x' then return False; end if;
                        while Words < 5 loop
                           while A_Offset < Text'Length and then White (Text (Text'First + A_Offset)) loop A_Offset := A_Offset + 1; end loop;
                           End_Offset := A_Offset;
                           while End_Offset < Text'Length and then not White (Text (Text'First + End_Offset)) loop End_Offset := End_Offset + 1; end loop;
                           Words := Words + 1; A_Offset := End_Offset;
                        end loop;
                        while A_Offset < Text'Length and then White (Text (Text'First + A_Offset)) loop A_Offset := A_Offset + 1; end loop;
                        if A_Offset = Text'Length then
                           if F (Row, "pathBytes").Form /= J.Null_Value then return False; end if;
                        else
                           declare Path : constant B.Decoded := Raw (Observed, F (Row, "pathBytes"));
                           begin if not Path.Valid or else Path.Data /= Text (Text'First + A_Offset .. Text'Last) then return False; end if; end;
                        end if;
                     end;
                  end if;
               end;
            end;
         end loop;
         return Count > 0 and then Executable and then J.Count (Observed, Selected) = Count;
      end Native_Mapping_Valid;
      function Capture_Budget (Record_Node : J.Node; Descriptor_Reader : Boolean := False) return Boolean is
         function Read_Charge (Item : J.Node) return Number is
            Used : U64 := 0;
         begin
            if F (Item, "reads").Form /= J.Array_Value then return (False, 0); end if;
            for I in 1 .. J.Count (Observed, F (Item, "reads")) loop
               declare Bytes : constant B.Decoded := Raw (Observed, F (A (F (Item, "reads"), I), "bytes"));
               begin
                  if not Bytes.Valid or else not Clean (A (F (Item, "reads"), I)) or else
                    not J.Is_True (Observed, F (A (F (Item, "reads"), I), "returned")) or else
                    not J.Is_True (Observed, F (A (F (Item, "reads"), I), "eof")) or else
                    U64 (Bytes.Length) > 268_435_456 - Used then return (False, 0); end if;
                  Used := Used + U64 (Bytes.Length);
               end;
            end loop;
            return (True, Used);
         end Read_Charge;
         Main_Reads : constant Number := Read_Charge (Record_Node);
      begin
         if not Main_Reads.Valid then return False; end if;
         if Descriptor_Reader then
            declare
               Helper_Reads : constant Number := Read_Charge (F (Record_Node, "descriptorReader"));
               Count : constant Number := Parse_Number (N (F (F (Record_Node, "descriptorReader"), "observation"), "rawBytesUsed"));
            begin
               if not Helper_Reads.Valid or else Helper_Reads.Value > 268_435_456 - Main_Reads.Value or else
                 not Count.Valid or else Count.Value > 268_435_456 - Main_Reads.Value - Helper_Reads.Value then return False; end if;
            end;
         end if;
         return True;
      end Capture_Budget;
      function Role_Valid (Record_Node : J.Node; Name : String) return Boolean is
         ID : constant J.Node := F (Record_Node, "identity");
         PID : constant String := N (ID, "pid");
         Peer : constant J.Node := F (Record_Node, "peerCredentials");
         Peer_Raw : constant B.Decoded := Raw (Observed, F (Record_Node, "peerCredentialsBytes"));
         Proc : constant B.Decoded := Read_Bytes (Record_Node, "status", PID);
         UID : constant B.Decoded := Read_Bytes (Record_Node, "uid_map", PID);
         GID : constant B.Decoded := Read_Bytes (Record_Node, "gid_map", PID);
         Bootstrap_PID : constant String := N (F (Bootstrap, "identity"), "pid");
         Bootstrap_UID : constant B.Decoded := Read_Bytes (Bootstrap, "uid_map", Bootstrap_PID);
         Bootstrap_GID : constant B.Decoded := Read_Bytes (Bootstrap, "gid_map", Bootstrap_PID);
         CG : constant B.Decoded := Read_Bytes (Record_Node, "cgroup", PID);
         Bootstrap_CG : constant B.Decoded := Read_Bytes (Bootstrap, "cgroup", Bootstrap_PID);
         User : constant J.Node := Namespace (Record_Node, "user", PID);
         Bootstrap_User : constant J.Node := Namespace (Bootstrap, "user", Bootstrap_PID);
         Request : constant B.Decoded := Raw (Observed, F (Record_Node, "requestBytes"));
         Inside : constant U64 := (if Name = "examiner" then 0 elsif Name = "worker" then 1 else 2);
      begin
         if Name not in "examiner" | "worker" | "candidate" or else S (Record_Node, "roleClaim") /= Name or else
           not Clean (Record_Node) or else not Subject_Valid (Record_Node, ID) or else
           not Proc.Valid or else not Fields_Valid (Proc.Data) or else not UID.Valid or else not GID.Valid or else not Bootstrap_UID.Valid or else not Bootstrap_GID.Valid or else
           not Raw_Maps_Equal (UID.Data, Bootstrap_UID.Data) or else not Raw_Maps_Equal (GID.Data, Bootstrap_GID.Data) or else
           not CG.Valid or else not Bootstrap_CG.Valid or else CG.Data /= Bootstrap_CG.Data or else not Peer_Raw.Valid or else Peer_Raw.Length /= 12 or else
           not Integer_Is (F (Peer, "pid"), L.Word (Peer_Raw.Data, 1, 4)) or else
           not Integer_Is (F (Peer, "uid"), L.Word (Peer_Raw.Data, 5, 4)) or else not Integer_Is (F (Peer, "gid"), L.Word (Peer_Raw.Data, 9, 4)) or else
           not Equal (F (ID, "pid"), F (Peer, "pid")) or else not Request.Valid or else
           not Packet_Valid (A (F (Record_Node, "packets"), 1), Peer, 0, Request.Data) or else
           Field (Proc.Data, "NoNewPrivs") /= "1" or else not Has_Field (Proc.Data, "Groups") or else Field (Proc.Data, "Groups") /= "" or else
           not Four (Field (Proc.Data, "Uid"), N (Peer, "uid")) or else not Four (Field (Proc.Data, "Gid"), N (Peer, "gid")) or else
           not Same_Object (F (User, "object"), F (F (Bootstrap, "roleNamespace"), "object")) or else
           not Same_Object (F (User, "parent"), F (Bootstrap_User, "object")) or else
           not Equal (F (User, "ownerUid"), F (Record_Node, "readerUid")) or else
           not Command_Valid (Record_Node, Name) or else not Ancestry_Valid (Record_Node) or else
           not Descriptor_Valid (Record_Node) or else not Mounts_Valid (Record_Node, Name) then return False; end if;
         declare
            UM : constant Map_Result := Map (UID.Data);
            GM : constant Map_Result := Map (GID.Data);
            U : constant Number := Mapped (UM, Inside);
            G : constant Number := Mapped (GM, Inside);
            Decoded : constant Worldline.Raw_JSON.Decoded_JSON := JSON (Request.Data);
            Doc : constant J.Node := J.Parse (Decoded.Data);
         begin
            if not U.Valid or else not G.Valid or else not Integer_Is (F (Peer, "uid"), U.Value) or else not Integer_Is (F (Peer, "gid"), G.Value) or else
              not Decoded.Valid or else not J.Duplicate_Free (Decoded.Data) or else Doc.Form /= J.Object_Value or else J.Count (Decoded.Data, Doc) /= 3 or else
              J.Field (Decoded.Data, Doc, "schemaVersion").Form /= J.Integer_Value or else J.Decimal (Decoded.Data, J.Field (Decoded.Data, Doc, "schemaVersion")) /= "1" or else
              not J.Equal (Decoded.Data, J.Field (Decoded.Data, Doc, "runId"), Observed, F (Plan, "runId")) or else
              not J.Is_Text (Decoded.Data, J.Field (Decoded.Data, Doc, "role"), Name) then return False; end if;
         end;
         for I in 1 .. 5 loop if not Zero_Hex (Field (Proc.Data, Cap_Name (I))) then return False; end if; end loop;
         for I in 2 .. 6 loop
            declare
               Child : constant J.Node := Namespace (Record_Node, NS_Name (I), PID);
               Parent : constant J.Node := Namespace (Bootstrap, NS_Name (I), Bootstrap_PID);
            begin
               if not Same_Object (F (Child, "owner"), F (User, "object")) or else Same_Object (F (Child, "object"), F (Parent, "object")) then return False; end if;
            end;
         end loop;
         if Name = "examiner" and then J.Present (F (Plan, "nativeGuard")) then
            declare
               Filters : constant String := Field (Proc.Data, "Seccomp_filters");
            begin
               if Field (Proc.Data, "Seccomp") /= "2" or else Filters'Length = 0 or else
                 Filters (Filters'First) not in '1' .. '9' or else (for some C of Filters => C not in '0' .. '9') or else
                 not Native_Mapping_Valid (Record_Node) then return False; end if;
            end;
         end if;
         return True;
      end Role_Valid;
      function Compatibility (Item, Record_Node : J.Node; Name : String) return Boolean is
         NS : constant J.Node := F (Item, "namespaces");
         PID : constant String := N (F (Record_Node, "identity"), "pid");
      begin
         if not Observed_Role (Observed, Item, Name) or else
           not Equal (F (Item, "kernelObservationId"), F (Record_Node, "recordId")) then return False; end if;
         for I in 1 .. 3 loop
            declare
               Name_NS : constant String := NS_Name (I);
               View : constant String := S (NS, Name_NS);
               Object : constant J.Node := F (Namespace (Record_Node, Name_NS, PID), "object");
            begin
               if not Namespace_Link (View, Name_NS) or else View /= Name_NS & ":[" & N (Object, "inode") & "]" then return False; end if;
            end;
         end loop;
         for I in 1 .. 2 loop
            declare
               Name_Map : constant String := (if I = 1 then "uidMap" else "gidMap");
               Raw_Name : constant String := (if I = 1 then "uid_map" else "gid_map");
               Bytes : constant B.Decoded := Read_Bytes (Record_Node, Raw_Name, PID);
               Self_Map : constant Map_Result := Map (S (Item, Name_Map));
               Global_Map : constant Map_Result := Map (Bytes.Data);
            begin
               if not Bytes.Valid or else not Self_Map.Valid or else not Global_Map.Valid or else Self_Map.Count /= Global_Map.Count then return False; end if;
               for K in Self_Map.Rows'Range loop
                  if Self_Map.Rows (K).Inside /= Global_Map.Rows (K).Inside or else Self_Map.Rows (K).Outside /= Global_Map.Rows (K).Inside or else
                    Self_Map.Rows (K).Count /= Global_Map.Rows (K).Count then return False; end if;
               end loop;
            end;
         end loop;
         return True;
      end Compatibility;
      function Find_Role (ID : J.Node) return J.Node is
         Found : J.Node := J.No_Node;
      begin
         for I in 1 .. J.Count (Observed, Roles) loop
            declare Row : constant J.Node := A (Roles, I);
            begin
               if S (Row, "kind") = "role-startup" and then Equal (F (Row, "recordId"), ID) then
                  if J.Present (Found) then return J.No_Node; end if;
                  Found := Row;
               end if;
            end;
         end loop;
         return Found;
      end Find_Role;
      function Quota_Valid return Boolean is
         Reader, Done : J.Node := J.No_Node;
      begin
         for I in 1 .. J.Count (Observed, Roles) loop
            declare Row : constant J.Node := A (Roles, I);
            begin
               if S (Row, "kind") = "namespace-quota-reader" then
                  if J.Present (Reader) then return False; end if; Reader := Row;
               end if;
            end;
         end loop;
         Done := Completion ("namespace-quota-reader-completion", F (Reader, "recordId"));
         if not Clean (Reader) or else not Completion_Valid (Done) then return False; end if;
         for I in 1 .. J.Count (Observed, Reader) loop
            declare Key : constant String := J.Member_Name (Observed, Reader, I);
            begin if Key not in "kind" | "packets" and then not Equal (F (Reader, Key), F (Done, Key)) then return False; end if; end;
         end loop;
         declare
            ID : constant J.Node := F (Reader, "identity");
            PID : constant String := N (ID, "pid");
            User : constant J.Node := F (Namespace (Bootstrap, "user", N (F (Bootstrap, "identity"), "pid")), "object");
            Observation : constant J.Node := F (Reader, "observation");
            Reads : constant J.Node := F (Observation, "reads");
            Quota : constant B.Decoded := Raw (Observed, F (Observation, "quotaBytes"));
            Source_Bytes : constant B.Decoded := Read_Bytes (Reader, S (Plan, "namespacePolicy"), "quota-reader-source");
            Status : constant B.Decoded := Read_Bytes (Reader, "status", PID);
            CG : constant B.Decoded := Read_Bytes (Reader, "cgroup", PID);
            Parent_CG : constant B.Decoded := Read_Bytes (Reader, "/proc/self/cgroup", "quota-reader-parent");
            Packets : constant J.Node := F (Done, "packets");
            Quota_Count : Natural := 0;
         begin
            if not Subject_Valid (Reader, ID) or else not Capture_Budget (Reader) or else not Helper_Command (Reader, "--quota-reader", ID) or else
              J.Count (Observed, F (Reader, "command")) /= 10 or else not Equal (F (ID, "ppid"), F (Reader, "readerPid")) or else
              not Same_Object (F (Namespace (Reader, "user", PID), "object"), User) or else
              not Source_Bytes.Valid or else B.Digest (Source_Bytes.Data) /= S (Plan, "namespacePolicySha256") or else
              not Status.Valid or else not Four (Field (Status.Data, "Uid"), N (Plan, "operatorUid")) or else
              not Four (Field (Status.Data, "Gid"), N (Plan, "operatorGid")) or else
              not CG.Valid or else not Parent_CG.Valid or else CG.Data /= Parent_CG.Data or else
              not Clean (Observation) or else S (Observation, "producer") /= "daemon-owned-namespace-quota-reader" or else
              not Quota.Valid or else Strip (Quota.Data) /= "0" or else Reads.Form /= J.Array_Value or else J.Count (Observed, Reads) = 0 then return False; end if;
            for I in 1 .. 2 loop
               declare
                  Name_Map : constant String := (if I = 1 then "uid_map" else "gid_map");
                  Bytes : constant B.Decoded := Read_Bytes (Reader, Name_Map, PID);
               begin
                  if not Bytes.Valid or else not Map (Bytes.Data).Valid then return False; end if;
               end;
            end loop;
            for I in 1 .. 3 loop
               declare Key : constant String := (if I = 1 then "readerNamespace" elsif I = 2 then "requestedNamespace" else "afterNamespace");
               begin if not Same_Object (F (Observation, Key), User) then return False; end if; end;
            end loop;
            for I in 1 .. J.Count (Observed, Reads) loop
               declare Row : constant J.Node := A (Reads, I);
               begin
                  if not Clean (Row) or else not J.Is_True (Observed, F (Row, "returned")) or else not J.Is_True (Observed, F (Row, "eof")) or else
                    not Raw (Observed, F (Row, "bytes")).Valid then return False; end if;
                  if S (Row, "path") = "/proc/sys/user/max_user_namespaces" and then Equal (F (Row, "bytes"), F (Observation, "quotaBytes")) then Quota_Count := Quota_Count + 1; end if;
               end;
            end loop;
            if Quota_Count /= 1 or else J.Count (Observed, Packets) /= 2 or else not Retained_Control (A (Packets, 2)) then return False; end if;
            declare
               Receive : constant J.Node := A (Packets, 1);
               Bytes : constant B.Decoded := Raw (Observed, F (Receive, "bytes"));
               Decoded : constant Worldline.Raw_JSON.Decoded_JSON := JSON (Bytes.Data);
               Document : constant J.Node := J.Parse (Decoded.Data);
               Flags : constant Number := Parse_Number (N (Receive, "flags"));
            begin
               if not Clean (Receive) or else S (Receive, "direction") /= "receive" or else not Bytes.Valid or else Bytes.Length > 65_536 or else
                 not Flags.Valid or else (Flags.Value and not U64 (16#80#)) /= 0 or else not Decoded.Valid or else Document.Form /= J.Object_Value or else
                 J.Count (Decoded.Data, Document) /= 2 or else not J.Is_Text (Decoded.Data, J.Field (Decoded.Data, Document, "state"), "observed") or else
                 not J.Equal (Decoded.Data, J.Field (Decoded.Data, Document, "observation"), Observed, Observation) then return False; end if;
            end;
         end;
         return True;
      end Quota_Valid;
      function Acknowledged (Record_Node : J.Node; Name : String) return Boolean is
         Ack : constant J.Node := Completion ("role-startup-acknowledgement", F (Record_Node, "recordId"));
         Bytes : constant B.Decoded := Raw (Observed, F (Ack, "bytes"));
         Decoded : constant Worldline.Raw_JSON.Decoded_JSON := JSON (Bytes.Data);
         Document : constant J.Node := J.Parse (Decoded.Data);
         Count : Natural := 1;
      begin
         if not J.Is_True (Observed, F (Ack, "sent")) or else not J.Is_False (Observed, F (Ack, "preSendPidfdReady")) or else
           not Bytes.Valid or else Bytes.Length > 65_536 or else not Decoded.Valid or else
           not J.Equal (Decoded.Data, J.Field (Decoded.Data, Document, "recordId"), Observed, F (Record_Node, "recordId")) then return False; end if;
         if Name = "examiner" then
            Count := Count + 1;
            if not Equal (F (Record_Node, "examinerEntryBinding"), F (Plan, "examinerEntryBinding")) or else
              not J.Equal (Decoded.Data, J.Field (Decoded.Data, Document, "entrySource"), Observed, F (Plan, "examinerEntryBinding")) then return False; end if;
            if J.Present (F (Plan, "loaderPolicy")) then
               Count := Count + 1;
               if not Equal (F (Record_Node, "examinerLoaderBinding"), F (Plan, "examinerLoaderBinding")) or else
                 not J.Equal (Decoded.Data, J.Field (Decoded.Data, Document, "loaderPolicy"), Observed, F (Plan, "examinerLoaderBinding")) then return False; end if;
            end if;
            if J.Present (F (Plan, "nativeGuard")) then
               Count := Count + 1;
               if not Equal (F (Record_Node, "examinerNativeBinding"), F (Plan, "nativeGuardBinding")) or else
                 not J.Equal (Decoded.Data, J.Field (Decoded.Data, Document, "nativeGuard"), Observed, F (Plan, "nativeGuardBinding")) then return False; end if;
            end if;
         end if;
         return Document.Form = J.Object_Value and then J.Count (Decoded.Data, Document) = Count;
      end Acknowledged;
      function Cleanup_Valid return Boolean is
         Joined : array (1 .. 3) of Boolean := (others => False);
         Stack_Closed : Boolean := False;
      begin
         for I in 1 .. J.Count (Observed, Roles) loop
            declare Startup : constant J.Node := A (Roles, I); Count : Natural := 0;
            begin
               if S (Startup, "kind") = "role-startup" then
                  for K in 1 .. J.Count (Observed, Roles) loop
                     declare Row : constant J.Node := A (Roles, K);
                     begin
                        if S (Row, "kind") = "role-held-descriptor-cleanup" and then Equal (F (Row, "startupRecordId"), F (Startup, "recordId")) then Count := Count + 1; end if;
                     end;
                  end loop;
                  if Count /= 1 then return False; end if;
               end if;
            end;
         end loop;
         for I in 1 .. J.Count (Observed, Roles) loop
            declare Row : constant J.Node := A (Roles, I); Kind : constant String := S (Row, "kind");
            begin
               if Kind = "observer-channel-cleanup" then
                  if F (Row, "closes").Form /= J.Array_Value or else F (Row, "joins").Form /= J.Array_Value then return False; end if;
                  for K in 1 .. J.Count (Observed, F (Row, "closes")) loop
                     declare Close : constant J.Node := A (F (Row, "closes"), K);
                     begin if not Clean (Close) or else not J.Is_True (Observed, F (Close, "returned")) then return False; end if; end;
                  end loop;
                  for K in 1 .. J.Count (Observed, F (Row, "joins")) loop
                     declare Join : constant J.Node := A (F (Row, "joins"), K); Service : constant String := S (Join, "service");
                     begin
                        if F (Join, "joinException").Form /= J.Null_Value or else F (Join, "aliveException").Form /= J.Null_Value or else
                          not J.Is_True (Observed, F (Join, "joinReturned")) or else not J.Is_False (Observed, F (Join, "alive")) then return False; end if;
                        if Service = "role" then Joined (1) := True;
                        elsif Service = "native" then Joined (2) := True;
                        elsif Service = "lifetime" then Joined (3) := True;
                        else return False; end if;
                     end;
                  end loop;
               elsif Kind = "observer-cleanup" then
                  if not Clean (Row) or else not J.Is_True (Observed, F (Row, "returned")) then return False; end if;
                  Stack_Closed := True;
               elsif Kind = "role-held-descriptor-cleanup" then
                  declare
                     Startup : constant J.Node := Find_Role (F (Row, "startupRecordId"));
                     Closes : constant J.Node := F (Row, "descriptorCloses");
                  begin
                     if Startup.Form /= J.Object_Value or else Closes.Form /= J.Array_Value or else
                       J.Count (Observed, Closes) /= J.Count (Observed, F (Startup, "ancestry")) + 7 then return False; end if;
                     for K in 1 .. J.Count (Observed, Closes) loop
                        declare Close : constant J.Node := A (Closes, K);
                        begin
                           if not Clean (Close) or else not J.Is_True (Observed, F (Close, "closed")) or else F (Close, "descriptor").Form /= J.Integer_Value then return False; end if;
                           for X in 1 .. K - 1 loop if Equal (F (A (Closes, X), "descriptor"), F (Close, "descriptor")) then return False; end if; end loop;
                        end;
                     end loop;
                  end;
               end if;
            end;
         end loop;
         return Stack_Closed and then Joined (1) and then
           (not J.Present (F (Plan, "nativeGuard")) or else (Joined (2) and then Joined (3)));
      end Cleanup_Valid;
      function Native_Outcome_Valid return Boolean is
         Outcome, Terminal : J.Node := J.No_Node;
         Exit_Count : Natural := 0;
      begin
         if not Worldline.Native_Lifetime_Observation.Clean (Observed, Result_Record, J.Decimal (Result_Record, R (Result, "exitCode"))) then return False; end if;
         for I in 1 .. J.Count (Observed, Roles) loop
            declare Row : constant J.Node := A (Roles, I); Kind : constant String := S (Row, "kind");
            begin
               if Kind = "native-lifetime-process-outcome" then
                  if J.Present (Outcome) then return False; end if; Outcome := Row;
               elsif Kind = "native-lifetime-terminal" then
                  if J.Present (Terminal) then return False; end if; Terminal := Row;
               end if;
            end;
         end loop;
         if not Clean (Outcome) or else not Equal (F (Outcome, "startupRecordId"), F (Examiner, "recordId")) or else
           F (Boundary, "examinerReturnCode").Form /= J.Integer_Value or else F (Boundary, "bootstrapExitCode").Form /= J.Integer_Value or else
           not J.Nonnegative (Observed, F (Boundary, "examinerReturnCode")) or else
           not Equal (F (Boundary, "examinerReturnCode"), F (Boundary, "bootstrapExitCode")) or else
           not J.Equal (Observed, F (Boundary, "bootstrapExitCode"), Result_Record, R (Result, "exitCode")) or else
           not Equal (F (Outcome, "fixedBootstrapExaminerWait"), F (Boundary, "examinerReturnCode")) or else
           not Equal (F (Outcome, "actualBootstrapWait"), F (Boundary, "bootstrapExitCode")) or else
           not Equal (F (F (Outcome, "nativeTerminal"), "recordId"), F (Terminal, "recordId")) then return False; end if;
         for I in 1 .. J.Count (Observed, F (Terminal, "terminal")) loop
            declare Key : constant String := J.Member_Name (Observed, F (Terminal, "terminal"), I);
            begin if not Equal (F (F (Terminal, "terminal"), Key), F (F (Outcome, "nativeTerminal"), Key)) then return False; end if; end;
         end loop;
         -- Recover the signed C interpreter status from its ORIGINAL typed bytes.
         -- JSON terminal flags and normalized-status projections never decide it.
         for I in 1 .. J.Count (Observed, Roles) loop
            declare Row : constant J.Node := A (Roles, I);
            begin
               if S (Row, "kind") in "native-lifetime-receive" | "native-lifetime-terminal" then
                  declare
                     Bytes : constant B.Decoded := Raw (Observed, F (A (F (Row, "transferObjects"), 1), "bytes"));
                     Value : constant L.Node := L.Parse (Bytes.Data, 1, Bytes.Length);
                  begin
                     if Bytes.Valid and then Value.Kind = L.Tuple_Value and then L.Text (Bytes.Data, L.Element (Bytes.Data, Value, 1)) = "native-interpreter-exit" then
                        declare
                           Status : constant L.Node := L.Element (Bytes.Data, Value, 3);
                           Width : constant Natural := (if Status.Last >= Status.First + 8 then Status.Last - Status.First - 8 else 0);
                        begin
                           Exit_Count := Exit_Count + 1;
                           if Status.Kind /= L.Integer_Value or else Width not in 1 .. 4 then return False; end if;
                           declare
                              Number_Value : constant U64 := L.Word (Bytes.Data, Status.First + 9, Width);
                              Negative : constant Boolean := Character'Pos (Bytes.Data (Status.Last)) >= 128;
                              Text : constant String := (if Negative then "-" & Image (2 ** (8 * Width) - Number_Value) else Image (Number_Value));
                           begin
                              if F (Outcome, "interpreterOriginalStatus").Form /= J.Integer_Value or else N (Outcome, "interpreterOriginalStatus") /= Text or else
                                N (F (Outcome, "nativeTerminal"), "interpreterOriginalStatus") /= Text or else
                                not Integer_Is (F (Boundary, "examinerReturnCode"), U64 (L.Mod_256 (Bytes.Data, Status))) then return False; end if;
                           end;
                        end;
                     end if;
                  end;
               end if;
            end;
         end loop;
         return Exit_Count = 1;
      end Native_Outcome_Valid;
      Workers : constant J.Node := F (Boundary, "workers");
      Role_Count : Natural := 0;
      Acquired_Role_Count : Natural := 0;
   begin
      if Root.Form /= J.Array_Value or else Invocation.Form /= J.Object_Value or else Result.Form /= J.Object_Value or else
        Plan.Form /= J.Object_Value or else Sources.Form /= J.Object_Value or else Roles.Form /= J.Array_Value or else
        Boundary.Form /= J.Object_Value or else Result_Boundary.Form /= J.Object_Value or else Workers.Form /= J.Array_Value or else
        S (Plan, "trustedInterpreter") /= "/usr/bin/python3" or else
        not J.Equal (Observed, F (Plan, "runId"), Expected, J.Field (Expected, Invocation, "runId")) or else
        not Equal (F (Plan, "runId"), F (Boundary, "runId")) then return False; end if;
      for I in 1 .. J.Count (Observed, Root) loop
         if S (A (Root, I), "kind") = "private-kernel-role-observation" then Acquired_Role_Count := Acquired_Role_Count + 1; end if;
      end loop;
      if Acquired_Role_Count /= J.Count (Observed, Roles) then return False; end if;
      for I in 1 .. J.Count (Observed, Roles) loop
         declare Row : constant J.Node := A (Roles, I); Kind : constant String := S (Row, "kind");
         begin
            if not Record_Bound (Row, I) or else not Integer_Is (F (Row, "schemaVersion"), 1) or else
              not Equal (F (Row, "runId"), F (Plan, "runId")) then return False; end if;
            if Kind = "bootstrap-anchor" then
               if J.Present (Bootstrap) then return False; end if;
               Bootstrap := Row;
            elsif Kind = "role-startup" then
               Role_Count := Role_Count + 1;
               if S (Row, "roleClaim") = "examiner" then
                  if J.Present (Examiner) then return False; end if;
                  Examiner := Row;
               end if;
               for K in 1 .. I - 1 loop
                  declare Old : constant J.Node := A (Roles, K);
                  begin
                     if S (Old, "kind") = "role-startup" and then
                       (Equal (F (Old, "recordId"), F (Row, "recordId")) or else
                        (Equal (F (F (Old, "identity"), "pid"), F (F (Row, "identity"), "pid")) and then
                         Equal (F (F (Old, "identity"), "starttime"), F (F (Row, "identity"), "starttime")))) then return False; end if;
                  end;
               end loop;
            elsif Kind = "observer-join-incomplete" then return False;
            end if;
         end;
      end loop;
      if Bootstrap.Form /= J.Object_Value or else Examiner.Form /= J.Object_Value or else not Bootstrap_Valid or else
        not Capture_Budget (Bootstrap) or else not Quota_Valid or else not Cleanup_Valid or else
        Role_Count /= J.Count (Observed, Workers) + 1 or else not Role_Valid (Examiner, "examiner") or else
        not Acknowledged (Examiner, "examiner") or else not Capture_Budget (Examiner, True) or else
        not Compatibility (F (Boundary, "examiner"), Examiner, "examiner") then return False; end if;
      for I in 1 .. J.Count (Observed, Workers) loop
         declare
            Worker : constant J.Node := A (Workers, I);
            Item : constant J.Node := F (Worker, "observation");
            Name : constant String := (if J.Present (F (Worker, "principal")) then S (Worker, "principal") else "worker");
            Role : constant J.Node := Find_Role (F (Item, "kernelObservationId"));
         begin
            if Worker.Form /= J.Object_Value or else F (Worker, "returncode").Form /= J.Integer_Value or else Name not in "worker" | "candidate" or else
              not Role_Valid (Role, Name) or else not Acknowledged (Role, Name) or else not Capture_Budget (Role, True) or else not Compatibility (Item, Role, Name) or else
              not Equal (F (F (Item, "namespaces"), "user"), F (F (F (Boundary, "examiner"), "namespaces"), "user")) or else
              Equal (F (F (Item, "namespaces"), "pid"), F (F (F (Boundary, "examiner"), "namespaces"), "pid")) or else
              Equal (F (F (Item, "namespaces"), "mnt"), F (F (F (Boundary, "examiner"), "namespaces"), "mnt")) or else
              not Equal (F (Item, "uidMap"), F (F (Boundary, "examiner"), "uidMap")) or else
              not Equal (F (Item, "gidMap"), F (F (Boundary, "examiner"), "gidMap")) then return False; end if;
            for K in 1 .. I - 1 loop
               declare Old : constant J.Node := F (A (Workers, K), "observation");
               begin
                  if Equal (F (Old, "kernelObservationId"), F (Item, "kernelObservationId")) or else
                    (S (Old, "role") /= Name and then (Equal (F (Old, "uid"), F (Item, "uid")) or else Equal (F (Old, "gid"), F (Item, "gid")))) then return False; end if;
               end;
            end loop;
         end;
      end loop;
      -- The compatibility boundary must correspond to the complete acquisition,
      -- not to a previously copied acceptance or reportMountExclusive bit.
      for I in 1 .. J.Count (Observed, Boundary) loop
         declare Key : constant String := J.Member_Name (Observed, Boundary, I);
         begin
            if not J.Equal (Observed, F (Boundary, Key), Result_Record, R (Result_Boundary, Key)) then return False; end if;
         end;
      end loop;
      if J.Present (F (Plan, "nativeGuard")) then
         declare
            Capture : constant J.Node := R (R (Result, "protectedProviderCapture"), "observed");
            Filter : constant String := J.Text (Result_Record, R (Capture, "filterProgramB64"));
         begin
            if not Worldline.Confinement_Filter.Establishes (Filter) or else
              not Native_Outcome_Valid then return False; end if;
         end;
      end if;
      return True;
   end Valid;
end Worldline.Evaluation_Role_Native;
