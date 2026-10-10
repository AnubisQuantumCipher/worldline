with Interfaces;
with Worldline.Producer_Values;
with Worldline.Producer_Bytes;
with Worldline.Lifetime_Values;
package body Worldline.Native_Lifetime_Observation with SPARK_Mode is
   package J renames Worldline.Producer_Values;
   package B renames Worldline.Producer_Bytes;
   package N renames Worldline.Lifetime_Values;
   use type J.Value_Kind;
   use type N.Value_Kind;
   use type N.U64;
   function Image (Value : N.U64) return String is
      S : constant String := N.U64'Image (Value);
   begin return S (S'First + 1 .. S'Last); end Image;
   function Clean (Raw_Acquisitions, Result_Record, Actual_Wait : String) return Boolean is
      JSON : String renames Raw_Acquisitions;
      Acquired : constant J.Node := J.Parse (JSON);
      function F (P : J.Node; K : String) return J.Node is (J.Field (JSON, P, K));
      function S (P : J.Node; K : String) return String is (J.Text (JSON, F (P, K)));
      function E (P : J.Node; I : Positive) return J.Node is (J.Element (JSON, P, I));
      function Number (P : J.Node; K : String) return String is (J.Decimal (JSON, F (P, K)));
      function Leaf (P : J.Node) return String is
        (if J.Is_Text (JSON, F (P, "encoding"), "base64") then S (P, "payload") else "!");
      function Is_Event (P : J.Node) return Boolean is
        (S (P, "kind") in "native-lifetime-receive" | "native-lifetime-terminal");
      function Record_Bytes (P : J.Node) return String is
        (Leaf (F (E (F (P, "transferObjects"), 1), "bytes")));
      function Count_Events return Natural is
         Count : Natural := 0;
      begin
         for I in 1 .. J.Count (JSON, Acquired) loop
            declare Row : constant J.Node := E (Acquired, I);
            begin if S (Row, "kind") = "private-kernel-role-observation" and then Is_Event (F (Row, "observation")) then Count := Count + 1; end if; end;
         end loop;
         return Count;
      end Count_Events;
      Event_Count : constant Natural := Count_Events;
      Rows : array (Positive range 1 .. Event_Count) of J.Node := (others => J.No_Node);
      Total : Natural := 0;
      Ready, Startup : J.Node := J.No_Node;
      Cursor : Natural := 0;
      Result_Root : constant J.Node := J.Parse (Result_Record);
      Result_Boundary : constant J.Node := J.Field (Result_Record, Result_Root, "evaluatorBoundary");
   begin
      if Acquired.Form /= J.Array_Value or else Event_Count = 0 then return False; end if;
      for I in 1 .. J.Count (JSON, Acquired) loop
         declare Row : constant J.Node := E (Acquired, I); Item : constant J.Node := F (Row, "observation"); Kind : constant String := S (Item, "kind");
         begin
            if S (Row, "kind") = "private-kernel-role-observation" then
               if Kind'Length >= 15 and then Kind (Kind'First .. Kind'First + 14) = "native-lifetime" and then
                 F (Item, "exception").Form /= J.Null_Value then return False; end if;
               if Kind = "native-lifetime-open" then
                  if Ready.Form /= J.Missing then return False; end if; Ready := Item;
               elsif Kind = "role-startup" and then S (Item, "roleClaim") = "examiner" then
                  if Startup.Form /= J.Missing then return False; end if; Startup := Item;
               elsif Is_Event (Item) then
                  declare Size : constant B.Extent := B.Base64_Extent (Record_Bytes (Item));
                  begin
                     if not Size.Valid or else Size.Length > JSON'Length - Total then return False; end if;
                     Total := Total + Size.Length; Cursor := Cursor + 1; Rows (Cursor) := Item;
                  end;
               end if;
            end if;
         end;
      end loop;
      if Ready.Form /= J.Object_Value or else Startup.Form /= J.Object_Value or else Total = 0 or else
        not J.Equal (JSON, F (Startup, "runId"), Result_Record, J.Field (Result_Record, Result_Boundary, "runId")) then return False; end if;
      declare
         Data : String (1 .. Total);
         Docs : array (Rows'Range) of N.Node := (others => N.No_Node);
         Kinds : array (Rows'Range) of Natural := (others => 0);
         Pending : array (Rows'Range) of Boolean := (others => False);
         Attempts : array (Rows'Range) of N.Node := (others => N.No_Node);
         Offset : Natural := 0;
         Valid : Boolean;
         Codes : N.Node := N.No_Node;
         Phase : Natural := 0;
         Has_Phase, Activated, Sticky, Incomplete : Boolean := False;
         First_Failure, Workload_Binding, Entry_Result, Workload_Outcome, Workload_Result, Process_Exit : N.Node := N.No_Node;
         Workload_Id, Entry_Id : Natural := 0;
         function A (P : N.Node; I : Positive) return N.Node is (N.Element (Data, P, I));
         function T (P : N.Node; I : Positive) return String is (N.Text (Data, A (P, I)));
         function Same (L, R : N.Node) return Boolean is (N.Equal (Data, L, R));
         function Tuple (P : N.Node; Count : Natural) return Boolean is (P.Kind = N.Tuple_Value and then P.Count = Count);
         function Bool (P : N.Node) return Boolean is (P.Kind in N.True_Value | N.False_Value);
         function Is_Null (P : N.Node) return Boolean is (P.Kind = N.Null_Value);
         function Positive_Id (P : N.Node) return Boolean is (N.Positive_Integer (Data, P));
         function Nonnegative_Id (P : N.Node) return Boolean is (N.Nonnegative (Data, P));
         function Bounded_Code (P, Bound : N.Node) return Boolean is
           (Positive_Id (P) and then Bound.Kind = N.Integer_Value and then N.Compare (Data, P, Bound) <= 0);
         function Optional (P : N.Node) return Boolean is
           (Tuple (P, 2) and then Bool (A (P, 1)) and then (A (P, 1).Kind = N.True_Value or else Is_Null (A (P, 2))));
         function Exception_Shape (P : N.Node; Complete : Boolean) return Boolean is
            Base : constant N.Node := A (P, 3);
            Detail : constant N.Node := A (P, 4);
            Expected_Size : Natural := 0;
         begin
            if not Tuple (P, 4) or else A (P, 1).Kind /= N.Bytes_Value or else N.Bytes (Data, A (P, 1))'Length = 0 or else
              T (P, 2) /= "native-boundary-before-return" or else not Tuple (Base, 7) or else not Bool (A (Base, 7)) then return False; end if;
            for I in 1 .. 6 loop if not Optional (A (Base, I)) then return False; end if; end loop;
            if Complete and then (A (A (Base, 1), 1).Kind /= N.True_Value or else A (A (Base, 1), 2).Kind /= N.Tuple_Value) then return False; end if;
            if Detail.Kind = N.Text_Value and then N.Text (Data, Detail) = "base-fields-only-not-a-subclass-object-snapshot" then return not Complete; end if;
            if Detail.Kind /= N.Tuple_Value or else Detail.Count = 0 then return False; end if;
            if T (Detail, 1) = "ImportError" then Expected_Size := 5;
            elsif T (Detail, 1) = "SyntaxError" then Expected_Size := 10;
            elsif T (Detail, 1) = "OSError" then Expected_Size := 6;
            elsif T (Detail, 1) = "SystemExit" then Expected_Size := 2;
            else return False; end if;
            if Detail.Count /= Expected_Size then return False; end if;
            for I in 2 .. Expected_Size loop
               if T (Detail, 1) = "OSError" and then I = Expected_Size then
                  if A (Detail, I).Kind /= N.Integer_Value then return False; end if;
               elsif not Optional (A (Detail, I)) then return False; end if;
            end loop;
            return not Complete or else N.Complete (Data, P);
         end Exception_Shape;
         function Cached (P, Bound : N.Node) return Boolean is
           (Is_Null (P) or else (Tuple (P, 7) and then T (P, 1) = "held-cached-origin" and then
            A (P, 2).Kind = N.Text_Value and then A (P, 3).Kind = N.Text_Value and then
            Bounded_Code (A (P, 4), Bound) and then Positive_Id (A (P, 5)) and then Positive_Id (A (P, 6)) and then Positive_Id (A (P, 7))));
         function Tree (P, Bound : N.Node) return Boolean is
            Nodes : constant N.Node := A (P, 3);
            Marks : array (Positive range 1 .. Nodes.Count) of Boolean := (others => False);
            Changed : Boolean;
         begin
            if not Tuple (P, 3) or else T (P, 1) /= "owned-code-tree" or else not Bounded_Code (A (P, 2), Bound) or else
              Nodes.Kind /= N.Tuple_Value or else Nodes.Count = 0 then return False; end if;
            for I in 1 .. Nodes.Count loop
               declare Item : constant N.Node := A (Nodes, I); Edges : constant N.Node := A (Item, 6); Last : N.Node := N.No_Node;
               begin
                  if not Tuple (Item, 6) or else not Bounded_Code (A (Item, 1), Bound) or else
                    A (Item, 2).Kind /= N.Text_Value or else not Cached (A (Item, 3), Bound) or else
                    A (Item, 4).Kind /= N.Text_Value or else not Nonnegative_Id (A (Item, 5)) or else Edges.Kind /= N.Tuple_Value then return False; end if;
                  for J in 1 .. I - 1 loop if Same (A (A (Nodes, J), 1), A (Item, 1)) then return False; end if; end loop;
                  Marks (I) := Same (A (Item, 1), A (P, 2));
                  for J in 1 .. Edges.Count loop
                     declare Edge : constant N.Node := A (Edges, J);
                     begin
                        if not Tuple (Edge, 2) or else not Nonnegative_Id (A (Edge, 1)) or else
                          N.Compare (Data, A (Edge, 1), A (Item, 5)) >= 0 or else
                          (Last.Kind /= N.Invalid and then N.Compare (Data, A (Edge, 1), Last) <= 0) or else
                          not Bounded_Code (A (Edge, 2), Bound) then return False; end if;
                        Last := A (Edge, 1);
                     end;
                  end loop;
               end;
            end loop;
            loop
               Changed := False;
               for I in 1 .. Nodes.Count loop
                  if Marks (I) then
                     declare Edges : constant N.Node := A (A (Nodes, I), 6);
                     begin
                        for J in 1 .. Edges.Count loop
                           declare Found : Boolean := False; Id : constant N.Node := A (A (Edges, J), 2);
                           begin
                              for K in 1 .. Nodes.Count loop
                                 if Same (A (A (Nodes, K), 1), Id) then Found := True; Changed := Changed or not Marks (K); Marks (K) := True; end if;
                              end loop;
                              if not Found then return False; end if;
                           end;
                        end loop;
                     end;
                  end if;
               end loop;
               exit when not Changed;
            end loop;
            return (for all Mark of Marks => Mark);
         end Tree;
         function Route (P, Bound : N.Node) return Boolean is
            Cache : constant N.Node := A (P, 6); Code : constant N.Node := A (P, 7);
         begin
            return Tuple (P, 7) and then T (P, 1) = "held-generator-binding" and then
              A (P, 2).Kind = N.Text_Value and then A (P, 3).Kind = N.Text_Value and then
              A (P, 4).Kind = N.Bytes_Value and then Positive_Id (A (P, 5)) and then
              Cached (Cache, Bound) and then Tree (Code, Bound) and then
              (Is_Null (Cache) or else (Same (A (Cache, 2), A (P, 2)) and then Same (A (Cache, 3), A (P, 3)) and then
                Same (A (Cache, 4), A (Code, 2)) and then Same (A (Cache, 6), A (P, 5))));
         end Route;
         function Code_Source (Identity : N.Node; Before : Natural) return N.Node is
         begin
            for I in 1 .. Before loop
               if Kinds (I) = 3 and then A (Docs (I), 2).Kind = N.True_Value then
                  declare Result : constant N.Node := A (Docs (I), 5);
                  begin
                     if T (Result, 1) = "owned-code-tree" then
                        for J in 1 .. A (Result, 3).Count loop
                           declare Node : constant N.Node := A (A (Result, 3), J);
                           begin if Same (A (Node, 1), Identity) then return Node; end if; end;
                        end loop;
                     end if;
                  end;
               end if;
            end loop;
            return N.No_Node;
         end Code_Source;
         function Workload_Shape (P : N.Node; Before : Natural) return Boolean is
            Function_Info : constant N.Node := A (P, 1);
            Helper : constant N.Node := Code_Source (A (Function_Info, 2), Before);
            Entry_Node : constant N.Node := Code_Source (A (P, 2), Before);
         begin
            return Tuple (P, 5) and then Tuple (Function_Info, 3) and then
              T (Function_Info, 1) = "function-code-and-globals-observation" and then
              Positive_Id (A (Function_Info, 2)) and then Positive_Id (A (Function_Info, 3)) and then
              Positive_Id (A (P, 2)) and then A (P, 3).Kind = N.Text_Value and then Positive_Id (A (P, 4)) and then Positive_Id (A (P, 5)) and then
              T (Helper, 2) = "/run/worldline-examiner-loader.py" and then T (Helper, 4) = "_native_workload" and then
              Same (A (Entry_Node, 2), A (P, 3)) and then T (Entry_Node, 4) = "<module>";
         end Workload_Shape;
         function Pending_Id (Id : N.Node) return Natural is
         begin
            for I in Pending'Range loop if Pending (I) and then N.Matches (Data, Id, N.U64 (I - 1)) then return I; end if; end loop;
            return 0;
         end Pending_Id;
         function Pending_Count return Natural is
            Count : Natural := 0;
         begin for P of Pending loop if P then Count := Count + 1; end if; end loop; return Count; end Pending_Count;
         function Phase_Of (P : N.Node) return Natural is
         begin for I in 0 .. 4 loop if N.Matches (Data, P, N.U64 (I)) then return I; end if; end loop; return 5; end Phase_Of;
         function Nonempty (P : N.Node) return Boolean is (P.Kind = N.Text_Value and then N.Text (Data, P)'Length > 0);
         function Sticky_Matches (Violation, First : N.Node) return Boolean is
           (Bool (Violation) and then First.Kind in N.Null_Value | N.Text_Value and then
            (Violation.Kind = N.True_Value) = Nonempty (First) and then
            (not Sticky or else Violation.Kind = N.True_Value) and then
            (First_Failure.Kind = N.Invalid or else Same (First_Failure, First)));
         function JSON_U64 (P : J.Node; Value : N.U64) return Boolean is (J.Decimal (JSON, P) = Image (Value));
         function Modulo (Value : String; Divisor : Positive) return Natural is
            Result : Natural := 0;
         begin
            if Value'Length = 0 then return Divisor; end if;
            for C of Value loop if C not in '0' .. '9' then return Divisor; end if; Result := (Result * 10 + Character'Pos (C) - 48) mod Divisor; end loop;
            return Result;
         end Modulo;
         function Close_Events (P : J.Node) return Boolean is
            Events : constant J.Node := F (P, "descriptorCloses");
         begin
            if Events.Form /= J.Array_Value or else J.Count (JSON, Events) /= 1 then return False; end if;
            for I in 1 .. J.Count (JSON, Events) loop
               declare Item : constant J.Node := E (Events, I);
               begin
                  if not J.Nonnegative (JSON, F (Item, "descriptor")) or else
                    not J.Is_True (JSON, F (Item, "closed")) or else F (Item, "exception").Form /= J.Null_Value then return False; end if;
                  declare Ancillary : constant J.Node := F (E (F (P, "packets"), 1), "ancillary"); Found : Boolean := False;
                  begin
                     for K in 1 .. J.Count (JSON, Ancillary) loop
                        declare Row : constant J.Node := E (Ancillary, K); Bytes : constant B.Decoded := B.Base64 (Leaf (F (Row, "bytes")));
                        begin
                           if Number (Row, "level") = "1" and then Number (Row, "kind") = "1" then
                              if Found or else not Bytes.Valid or else Bytes.Length /= 4 or else
                                not JSON_U64 (F (Item, "descriptor"), N.Word (Bytes.Data, 1, 4)) then return False; end if;
                              Found := True;
                           end if;
                        end;
                     end loop;
                     if not Found then return False; end if;
                  end;
               end;
            end loop;
            return True;
         end Close_Events;
         function Credential_Packet (P : J.Node; Rights : Boolean) return Boolean is
            Items : constant J.Node := F (P, "ancillary");
            Credentials, Descriptors : Natural := 0;
            Flags : constant String := Number (P, "flags");
         begin
            if P.Form /= J.Object_Value or else F (P, "exception").Form /= J.Null_Value or else
              Items.Form /= J.Array_Value or else Flags not in "0" | "128" | "1073741824" | "1073741952" then return False; end if;
            for I in 1 .. J.Count (JSON, Items) loop
               declare Item : constant J.Node := E (Items, I); Bytes : constant B.Decoded := B.Base64 (Leaf (F (Item, "bytes")));
               begin
                  if Number (Item, "level") /= "1" or else not Bytes.Valid then return False; end if;
                  if Number (Item, "kind") = "1" then
                     Descriptors := Descriptors + 1;
                     if not Rights or else Bytes.Length /= 4 then return False; end if;
                  elsif Number (Item, "kind") = "2" then
                     Credentials := Credentials + 1;
                     if Bytes.Length /= 12 or else
                       not JSON_U64 (F (F (Startup, "peerCredentials"), "pid"), N.Word (Bytes.Data, 1, 4)) or else
                       not JSON_U64 (F (F (Startup, "peerCredentials"), "uid"), N.Word (Bytes.Data, 5, 4)) or else
                       not JSON_U64 (F (F (Startup, "peerCredentials"), "gid"), N.Word (Bytes.Data, 9, 4)) then return False; end if;
                  else return False; end if;
               end;
            end loop;
            return Credentials = 1 and then Descriptors = (if Rights then 1 else 0);
         end Credential_Packet;
         function Acknowledged (Retained : J.Node; Expected_Bytes : String; Ready_Ack : Boolean := False) return Boolean is
            Seen : Boolean := False;
         begin
            for I in 1 .. J.Count (JSON, Acquired) loop
               declare Row : constant J.Node := E (Acquired, I); Item : constant J.Node := F (Row, "observation");
               begin
                  if S (Row, "kind") = "private-kernel-role-observation" and then
                    S (Item, "kind") = (if Ready_Ack then "native-lifetime-ready-sent" else "native-lifetime-acknowledgement") and then
                    J.Equal (JSON, F (Item, "retainedRecordId"), JSON, F (Retained, "recordId")) then
                     declare Actual : constant B.Decoded := B.Base64 (Leaf (F (Item, "bytes")));
                     begin
                        if Seen or else not J.Is_True (JSON, F (Item, "sent")) or else not Actual.Valid or else Actual.Data /= Expected_Bytes or else
                          (not Ready_Ack and then not J.Equal (JSON, F (Item, "startupRecordId"), JSON, F (Startup, "recordId"))) then return False; end if;
                        Seen := True;
                     end;
                  end if;
               end;
            end loop;
            return Seen;
         end Acknowledged;
         function Receipt (Before, Header, Record_Data, Record_Id : String) return String is
            Hex : constant String := B.Digest (Before & Header & Record_Data & Record_Id);
            Bytes : String (1 .. 32);
            function Digit (C : Character) return Natural is
              (if C in '0' .. '9' then Character'Pos (C) - 48 else Character'Pos (C) - Character'Pos ('a') + 10);
         begin
            for I in Bytes'Range loop Bytes (I) := Character'Val (Digit (Hex (2 * I - 1)) * 16 + Digit (Hex (2 * I))); end loop;
            return Bytes;
         end Receipt;
         Previous : String (1 .. 32) := (others => Character'Val (0));
         Ready_Bytes : constant B.Decoded := B.Base64 (Leaf (F (Ready, "acknowledgementBytes")));
         Ready_Data : String renames Ready_Bytes.Data;
         Ready_Root : constant J.Node := J.Parse (Ready_Data);
         Deadline : N.U64 := 0;
      begin
         if not Ready_Bytes.Valid or else Ready_Root.Form /= J.Object_Value or else
           not J.Equal (JSON, F (Ready, "startupRecordId"), JSON, F (Startup, "recordId")) or else
           not J.Equal (JSON, F (Ready, "identity"), JSON, F (Startup, "identity")) or else
           not J.Equal (JSON, F (Ready, "nativeKernelFilter"), JSON, F (Startup, "nativeKernelFilter")) or else
           not J.Equal (Ready_Data, J.Field (Ready_Data, Ready_Root, "runId"), JSON, F (Startup, "runId")) or else
           not J.Equal (Ready_Data, J.Field (Ready_Data, Ready_Root, "nativeGuard"), JSON, F (Ready, "nativeGuard")) or else
           not J.Equal (Ready_Data, J.Field (Ready_Data, Ready_Root, "startupRecordId"), JSON, F (Startup, "recordId")) or else
           not J.Equal (Ready_Data, J.Field (Ready_Data, Ready_Root, "recordId"), JSON, F (Ready, "recordId")) then return False; end if;
         for I in Rows'Range loop
            declare
               Row : constant J.Node := Rows (I);
               Size : constant B.Extent := B.Base64_Extent (Record_Bytes (Row));
               Packet : constant J.Node := E (F (Row, "packets"), 1);
               Header : constant B.Decoded := B.Base64 (Leaf (F (Packet, "bytes")));
               Object : constant J.Node := E (F (Row, "transferObjects"), 1);
               Ack : constant B.Decoded := B.Base64 (Leaf (F (Row, "acknowledgementBytes")));
            begin
               if not Header.Valid or else Header.Length /= 64 or else Header.Data (1 .. 8) /= "WLNLv001" or else
                 not Ack.Valid or else Ack.Length /= 96 or else Ack.Data (1 .. 8) /= "WLAKv001" or else
                 N.Word (Header.Data, 9, 8) not in 1 .. 7 or else
                 N.Word (Header.Data, 17, 8) /= N.U64 (I - 1) or else
                 N.Word (Header.Data, 25, 8) /= N.U64 (Size.Length) or else Header.Data (33 .. 64) /= Previous or else
                 not Credential_Packet (Packet, True) or else not Close_Events (Row) or else
                 not J.Equal (JSON, F (Row, "startupRecordId"), JSON, F (Startup, "recordId")) or else
                 F (Row, "exception").Form /= J.Null_Value or else
                 J.Count (JSON, F (Row, "transferObjects")) /= 1 or else S (Object, "name") /= "native-record" or else
                 not J.Is_True (JSON, F (Object, "returned")) or else not J.Is_True (JSON, F (Object, "eof")) or else
                 F (Object, "exception").Form /= J.Null_Value or else
                 Modulo (Number (Object, "sealsBefore"), 16) /= 15 or else
                 not J.Equal (JSON, F (Object, "sealsBefore"), JSON, F (Object, "sealsAfter")) or else
                 not J.Equal (JSON, F (Object, "before"), JSON, F (Object, "after")) or else
                 Modulo (Number (F (Object, "before"), "mode"), 65_536) / 4096 /= 8 or else
                 not JSON_U64 (F (F (Object, "before"), "size"), N.U64 (Size.Length)) or else
                 not JSON_U64 (F (Object, "announcedBytes"), N.U64 (Size.Length)) then return False; end if;
               Kinds (I) := Natural (N.Word (Header.Data, 9, 8));
               B.Decode_Base64 (Record_Bytes (Row), Data (Offset + 1 .. Offset + Size.Length), Valid);
               if not Valid then return False; end if;
               Docs (I) := N.Parse (Data, Offset + 1, Offset + Size.Length);
               if Docs (I).Kind = N.Invalid then return False; end if;
               declare Token : constant String := Receipt (Previous, Header.Data, Data (Offset + 1 .. Offset + Size.Length), S (Row, "recordId"));
               begin
                  if not J.Nonempty_Text (JSON, F (Row, "recordId")) or else
                    N.Word (Ack.Data, 9, 8) /= N.Word (Header.Data, 9, 8) or else
                    N.Word (Ack.Data, 17, 8) /= N.Word (Header.Data, 17, 8) or else
                    Ack.Data (33 .. 64) /= Previous or else Ack.Data (65 .. 96) /= Token then return False; end if;
                  if not Acknowledged (Row, Ack.Data) then return False; end if;
                  if I = 1 then Deadline := N.Word (Ack.Data, 25, 8);
                  elsif N.Word (Ack.Data, 25, 8) /= Deadline then return False; end if;
                  Previous := Token;
               end;
               Offset := Offset + Size.Length;
               if Kinds (I) = 5 then
                  declare EOF : constant J.Node := E (F (Row, "packets"), 2); End_Bytes : constant B.Decoded := B.Base64 (Leaf (F (EOF, "bytes")));
                  begin
                     if I /= Event_Count or else J.Count (JSON, F (Row, "packets")) /= 2 or else
                       not End_Bytes.Valid or else End_Bytes.Length /= 0 or else
                       J.Count (JSON, F (EOF, "ancillary")) /= 0 or else F (EOF, "exception").Form /= J.Null_Value or else
                       Number (EOF, "flags") not in "0" | "128" | "1073741824" | "1073741952" then return False; end if;
                  end;
               elsif J.Count (JSON, F (Row, "packets")) /= 1 then return False; end if;
            end;
         end loop;
         if not Acknowledged (Ready, Ready_Data, True) then return False; end if;
         if J.Decimal (Ready_Data, J.Field (Ready_Data, Ready_Root, "deadlineNs")) /= Image (Deadline) then return False; end if;
         declare Hello : constant N.Node := Docs (1); Context : constant N.Node := A (Hello, 2); Guard : constant N.Node := A (Context, 3); Peer : constant N.Node := A (Hello, 3);
         begin
            if Kinds (1) /= 1 or else not Tuple (Hello, 3) or else T (Hello, 1) /= "native-lifetime-open" or else
              not Tuple (Context, 5) or else T (Context, 1) /= S (Startup, "runId") or else T (Context, 2) /= S (Startup, "recordId") or else
              T (Context, 4) /= S (Ready, "recordId") or else not N.Matches (Data, A (Context, 5), Deadline) or else
              not Tuple (Guard, 7) or else not Tuple (Peer, 3) then return False; end if;
            for I in 1 .. 3 loop if not Nonnegative_Id (A (Peer, I)) then return False; end if; end loop;
            for I in 1 .. 7 loop
               declare Key : constant String := (case I is when 1 => "schema", when 2 => "runId", when 3 => "path", when 4 => "byteCount", when 5 => "sha256", when 6 => "sourceRecordId", when others => "buildReceiptSha256");
               begin
                  if I = 4 then
                     if A (Guard, I).Kind /= N.Integer_Value or else N.Bytes (Data, A (Guard, I))'Length > 8 then return False; end if;
                     if Number (F (Ready, "nativeGuard"), Key) /= Image (N.Word (Data, A (Guard, I).First + 9, Positive (A (Guard, I).Last - A (Guard, I).First - 8))) then return False; end if;
                  elsif N.Text (Data, A (Guard, I)) /= S (F (Ready, "nativeGuard"), Key) then return False; end if;
               end;
            end loop;
         end;
         for I in 2 .. Event_Count loop
            declare
               Value : constant N.Node := Docs (I);
               Kind : constant Natural := Kinds (I);
            begin
               if Process_Exit.Kind /= N.Invalid and then Kind /= 5 then return False; end if;
               if Kind = 2 then
                  declare
                     Name : constant String := T (Value, 1);
                     Thread : constant N.Node := A (Value, 3);
                     Parent : constant N.Node := A (Value, 4);
                     Inputs : constant N.Node := A (Value, 5);
                     Path : constant N.Node := A (Value, 6);
                     Source : constant N.Node := A (Value, 7);
                     Options : constant N.Node := A (Value, 8);
                     Count : constant N.Node := A (Value, 9);
                     Began_Phase : constant Natural := Phase_Of (A (Value, 2));
                     Input_Count, Option_Count : Natural := 0;
                     Top : Natural := 0;
                  begin
                     if not Tuple (Value, 9) or else Name not in "source-compile" | "frozen-metadata" | "frozen-code" | "ast-parse" | "ast-compiler" | "bind-generator" | "bind-cached-generator" | "validated-generator-source" | "activate" | "bind-workload" | "workload" | "workload-entry" or else
                       Began_Phase = 5 or else not Positive_Id (Thread) or else Parent.Kind not in N.Null_Value | N.Integer_Value or else
                       Inputs.Kind /= N.Tuple_Value or else Options.Kind /= N.Tuple_Value or else Path.Kind not in N.Null_Value | N.Text_Value or else
                       Source.Kind not in N.Null_Value | N.Bytes_Value or else Is_Null (Path) /= Is_Null (Source) or else
                       not Nonnegative_Id (Count) or else (Codes.Kind /= N.Invalid and then N.Compare (Data, Count, Codes) < 0) then return False; end if;
                     if Name in "source-compile" | "ast-compiler" then Option_Count := 4;
                     elsif Name = "validated-generator-source" then Input_Count := 2; Option_Count := 1;
                     elsif Name = "ast-parse" then Input_Count := 2;
                     elsif Name /= "activate" then Input_Count := 1; end if;
                     if Inputs.Count /= Input_Count or else Options.Count /= Option_Count then return False; end if;
                     for J in 1 .. Options.Count loop if A (Options, J).Kind /= N.Integer_Value then return False; end if; end loop;
                     if Name in "source-compile" | "ast-compiler" | "validated-generator-source" and then (Path.Kind /= N.Text_Value or else Source.Kind /= N.Bytes_Value) then return False; end if;
                     if Name = "validated-generator-source" and then
                       (A (Inputs, 1).Kind /= N.Text_Value or else not Route (A (Inputs, 2), Count) or else not Same (A (A (Inputs, 2), 3), Path) or else not Same (A (A (Inputs, 2), 4), Source)) then return False; end if;
                     if Name = "ast-compiler" then
                        declare P : constant Natural := Pending_Id (Parent);
                        begin if P = 0 or else T (Attempts (P), 1) /= "ast-parse" then return False; end if; end;
                     end if;
                     if Name in "bind-workload" | "workload" then
                        if not Workload_Shape (A (Inputs, 1), I - 1) or else N.Text (Data, Path) /= "/run/worldline-examiner-loader.py" or else Source.Kind /= N.Bytes_Value then return False; end if;
                        if Name = "bind-workload" then
                           if Workload_Binding.Kind /= N.Invalid or else Workload_Id /= 0 then return False; end if;
                        else
                           if Workload_Binding.Kind = N.Invalid or else Workload_Id /= 0 or else not Same (A (Inputs, 1), Workload_Binding) or else not Is_Null (Parent) then return False; end if;
                           Workload_Id := I;
                        end if;
                     elsif Name = "workload-entry" then
                        declare Entry_Node : constant N.Node := A (Inputs, 1);
                        begin
                           if Workload_Binding.Kind = N.Invalid or else Entry_Id /= 0 or else Workload_Id = 0 or else
                             not Pending (Workload_Id) or else not N.Matches (Data, Parent, N.U64 (Workload_Id - 1)) or else
                             not Tuple (Entry_Node, 4) or else not Same (A (Entry_Node, 1), A (Workload_Binding, 2)) or else
                             not Same (A (Entry_Node, 4), A (Workload_Binding, 4)) or else not Same (Path, A (Workload_Binding, 3)) or else
                             Source.Kind /= N.Bytes_Value then return False; end if;
                           for J in 1 .. 4 loop if not Positive_Id (A (Entry_Node, J)) then return False; end if; end loop;
                           Entry_Id := I;
                        end;
                     end if;
                     for J in 1 .. I - 1 loop if Pending (J) and then Same (A (Attempts (J), 3), Thread) then Top := J; end if; end loop;
                     if (Has_Phase and then Began_Phase /= Phase) or else (if Top = 0 then not Is_Null (Parent) else not N.Matches (Data, Parent, N.U64 (Top - 1))) then return False; end if;
                     Pending (I) := True; Attempts (I) := Value; Codes := Count; Phase := Began_Phase; Has_Phase := True;
                     Incomplete := Incomplete or not N.Complete (Data, Inputs);
                  end;
               elsif Kind = 3 then
                  declare
                     Identity : constant Natural := Pending_Id (A (Value, 1));
                     Returned : constant Boolean := A (Value, 2).Kind = N.True_Value;
                     Current_Phase : constant Natural := Phase_Of (A (Value, 3));
                     Count : constant N.Node := A (Value, 4);
                     Output : constant N.Node := A (Value, 5);
                     Primary : constant N.Node := A (Value, 6);
                     Complete : constant Boolean := A (Value, 7).Kind = N.True_Value;
                     Violated : constant N.Node := A (Value, 8);
                     First : constant N.Node := A (Value, 9);
                  begin
                     if Value.Kind /= N.Tuple_Value or else Value.Count not in 9 | 10 or else Identity = 0 or else
                       not Bool (A (Value, 2)) or else not Bool (A (Value, 7)) or else Current_Phase = 5 or else
                       not Nonnegative_Id (Count) or else N.Compare (Data, Count, Codes) < 0 or else not Sticky_Matches (Violated, First) or else
                       (if Returned then not Is_Null (Primary) else not Exception_Shape (Primary, Complete)) then return False; end if;
                     declare
                        Attempt : constant N.Node := Attempts (Identity);
                        Name : constant String := T (Attempt, 1);
                        Inputs : constant N.Node := A (Attempt, 5);
                        Began : constant Natural := Phase_Of (A (Attempt, 2));
                        Workload : constant Boolean := Name in "workload" | "workload-entry";
                     begin
                        if Value.Count /= (if Workload then 10 else 9) then return False; end if;
                        if Workload then
                           declare Held : constant N.Node := A (Value, 10);
                           begin
                              if not Tuple (Held, 2) or else T (Held, 1) /= "native-held-primary-at-result" or else
                                (if Is_Null (Primary) then not Is_Null (A (Held, 2)) else not Positive_Id (A (Held, 2))) then return False; end if;
                           end;
                        end if;
                        if Returned then
                           if (if Name in "bind-generator" | "bind-cached-generator" | "activate" | "bind-workload" | "workload" then Began /= 2 else Began not in 2 | 3) or else
                             Current_Phase /= (if Name in "activate" | "workload" then 3 else Began) or else
                             Violated.Kind /= N.False_Value or else Sticky or else not Complete then return False; end if;
                           if Name in "source-compile" | "frozen-code" | "validated-generator-source" then
                              if not Tree (Output, Count) then return False; end if;
                              for J in 1 .. A (Output, 3).Count loop
                                 declare Node : constant N.Node := A (A (Output, 3), J); Old : constant N.Node := Code_Source (A (Node, 1), I - 1);
                                 begin if Old.Kind /= N.Invalid and then (not Same (A (Old, 2), A (Node, 2)) or else not Same (A (Old, 4), A (Node, 4))) then return False; end if; end;
                              end loop;
                           elsif Name in "bind-generator" | "bind-cached-generator" then
                              if not Route (Output, Count) or else
                                (Name = "bind-cached-generator" and then Is_Null (A (Output, 6))) then return False; end if;
                              declare Label : constant N.Node := (if Name = "bind-generator" and then A (Inputs, 1).Kind = N.Tuple_Value and then A (Inputs, 1).Count > 0 then A (A (Inputs, 1), 1) else A (Inputs, 1));
                              begin if Label.Kind /= N.Text_Value or else not Same (A (Output, 2), Label) then return False; end if; end;
                           elsif Name = "frozen-metadata" and then not Is_Null (Output) then
                              declare Entries : constant N.Node := A (Output, 2); Has_Name, Has_Package, Has_Original : Boolean := False;
                              begin
                                 if not Tuple (Output, 2) or else T (Output, 1) /= "exact-dict-entries" or else not Tuple (Entries, 3) then return False; end if;
                                 for J in 1 .. 3 loop
                                    declare Row : constant N.Node := A (Entries, J); Key : constant String := T (Row, 1);
                                    begin
                                       if not Tuple (Row, 2) then return False; end if;
                                       if Key = "name" then if Has_Name or else A (Inputs, 1).Kind /= N.Text_Value or else not Same (A (Row, 2), A (Inputs, 1)) then return False; end if; Has_Name := True;
                                       elsif Key = "isPackage" then if Has_Package or else not Bool (A (Row, 2)) then return False; end if; Has_Package := True;
                                       elsif Key = "originalName" then if Has_Original or else A (Row, 2).Kind not in N.Null_Value | N.Text_Value then return False; end if; Has_Original := True;
                                       else return False; end if;
                                    end;
                                 end loop;
                                 if not Has_Name or else not Has_Package or else not Has_Original then return False; end if;
                              end;
                           elsif Name in "ast-parse" | "ast-compiler" then
                              if not Tuple (Output, 2) or else T (Output, 1) /= "non-executable-result-not-snapshotted" or else A (Output, 2).Kind /= N.Bytes_Value or else N.Bytes (Data, A (Output, 2))'Length = 0 then return False; end if;
                           elsif not Is_Null (Output) then return False; end if;
                        elsif not Is_Null (Output) or else (Current_Phase /= Began and then not (Name = "workload" and then Began = 2 and then Current_Phase = 3)) then return False; end if;
                        if Name = "bind-workload" and then Returned then
                           if Workload_Binding.Kind /= N.Invalid then return False; end if; Workload_Binding := A (Inputs, 1);
                        elsif Name = "workload-entry" then
                           if Entry_Result.Kind /= N.Invalid or else Identity /= Entry_Id then return False; end if; Entry_Result := Value;
                        elsif Name = "workload" then
                           if Workload_Outcome.Kind = N.Invalid or else Identity /= Workload_Id then return False; end if;
                           declare Selected : constant N.Node := A (A (Workload_Outcome, 11), 3);
                           begin
                              if (Returned and then (A (Workload_Outcome, 7).Kind /= N.True_Value or else not Is_Null (Selected))) or else
                                (if not Is_Null (Selected) then not Same (A (A (Value, 10), 2), Selected) else not Returned and then Violated.Kind /= N.True_Value) then return False; end if;
                           end;
                           Workload_Result := Value;
                        end if;
                        for J in Identity + 1 .. I - 1 loop if Pending (J) and then Same (A (Attempts (J), 3), A (Attempt, 3)) then return False; end if; end loop;
                        Pending (Identity) := False; Codes := Count; Sticky := Sticky or Violated.Kind = N.True_Value;
                        if Violated.Kind = N.True_Value then First_Failure := First; end if;
                        Phase := Current_Phase; Incomplete := Incomplete or (not Is_Null (Primary) and then not Complete);
                        if Name = "activate" and then Returned then if Activated then return False; end if; Activated := True; end if;
                     end;
                  end;
               elsif Kind = 6 then
                  declare
                     Invoked : constant N.Node := A (Value, 4); Returned : constant N.Node := A (Value, 5);
                     Primary : constant N.Node := A (Value, 6); Helper_Returned : constant N.Node := A (Value, 7);
                     Secondary : constant N.Node := A (Value, 8); Selected : constant String := T (Value, 9);
                     Complete : constant Boolean := A (Value, 10).Kind = N.True_Value; Identities : constant N.Node := A (Value, 11);
                  begin
                     if not Tuple (Value, 11) or else T (Value, 1) /= "native-workload-outcome-after-helper-cleanup" or else
                       Workload_Id = 0 or else not Pending (Workload_Id) or else Pending_Count /= 1 or else Workload_Outcome.Kind /= N.Invalid or else
                       not N.Matches (Data, A (Value, 2), N.U64 (Workload_Id - 1)) or else
                       not Bool (Invoked) or else not Bool (Returned) or else not Bool (Helper_Returned) or else not Bool (A (Value, 10)) or else
                       Selected not in "entry" | "helper" | "none" or else not Tuple (Identities, 3) then return False; end if;
                     for J in 1 .. 3 loop if not Is_Null (A (Identities, J)) and then not Positive_Id (A (Identities, J)) then return False; end if; end loop;
                     if Is_Null (A (Identities, 1)) /= Is_Null (Primary) or else Is_Null (A (Identities, 2)) /= Is_Null (Secondary) or else
                       (if Selected = "entry" then not Same (A (Identities, 3), A (Identities, 1)) elsif Selected = "helper" then not Same (A (Identities, 3), A (Identities, 2)) else not Is_Null (A (Identities, 3))) then return False; end if;
                     if Invoked.Kind = N.True_Value then
                        if Entry_Id = 0 or else Entry_Result.Kind = N.Invalid or else not N.Matches (Data, A (Value, 3), N.U64 (Entry_Id - 1)) or else
                          not Same (Returned, A (Entry_Result, 2)) or else not Same (A (Identities, 1), A (A (Entry_Result, 10), 2)) then return False; end if;
                     elsif not Is_Null (A (Value, 3)) or else Returned.Kind /= N.False_Value or else not Is_Null (Primary) or else Entry_Id /= 0 then return False; end if;
                     if (not Is_Null (Primary) and then not Exception_Shape (Primary, Complete)) or else
                       (if Helper_Returned.Kind = N.True_Value then not Is_Null (Secondary) else not Exception_Shape (Secondary, Complete)) or else
                       Selected /= (if not Is_Null (Primary) then "entry" elsif not Is_Null (Secondary) then "helper" else "none") then return False; end if;
                     Workload_Outcome := Value; Incomplete := Incomplete or not Complete;
                  end;
               elsif Kind = 7 then
                  if not Tuple (Value, 6) or else T (Value, 1) /= "native-interpreter-exit" or else
                    T (Value, 2) not in "Py_BytesMain-return" | "libc-exit-after-python-finalization" or else
                    A (Value, 3).Kind /= N.Integer_Value or else A (Value, 3).Last - A (Value, 3).First - 8 > 4 or else
                    A (Value, 4).Kind /= N.True_Value or else Process_Exit.Kind /= N.Invalid then return False; end if;
                  for J in 5 .. 6 loop
                     declare Path : constant String := T (Value, J);
                     begin if Path'Length = 0 or else Path (Path'First) /= '/' then return False; end if; end;
                  end loop;
                  Process_Exit := Value;
               elsif Kind = 5 then
                  if not Tuple (Value, 7) or else T (Value, 1) /= "native-finalized" or else Phase_Of (A (Value, 2)) = 5 or else
                    not Sticky_Matches (A (Value, 3), A (Value, 4)) or else
                    not N.Matches (Data, A (Value, 5), N.U64 (Pending_Count)) or else not Same (A (Value, 6), Codes) or else
                    not N.Matches (Data, A (Value, 7), N.U64 (I - 1)) or else (Has_Phase and then Phase_Of (A (Value, 2)) /= Phase) or else
                    Workload_Outcome.Kind = N.Invalid or else Workload_Result.Kind = N.Invalid or else Process_Exit.Kind = N.Invalid or else Pending_Count /= 0 then return False; end if;
                  if not Activated or else Phase /= 3 or else A (Value, 3).Kind /= N.False_Value or else Sticky or else Incomplete or else
                    Actual_Wait /= Image (N.U64 (N.Mod_256 (Data, A (Process_Exit, 3)))) then return False; end if;
               else return False;
               end if;
            end;
         end loop;
         return Kinds (Event_Count) = 5;
      end;
   end Clean;
end Worldline.Native_Lifetime_Observation;
