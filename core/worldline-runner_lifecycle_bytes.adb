with Canonical_Artifacts;
with Worldline.Archive_Base64;
package body Worldline.Runner_Lifecycle_Bytes with SPARK_Mode is
   package C renames Canonical_Artifacts;
   use type E.Count;
   use type E.Q.Byte;
   use type C.JSON_Kind;
   use type E.Value_Kind;
   use type E.Layer;
   use type E.Encoding_Level;
   package B renames Worldline.Archive_Base64;
   package Canonical_View is
      function Quiescent (Data : E.Bytes; Owner : E.Span) return Boolean;
   end Canonical_View;
   package body Canonical_View is
   function Field (Data : E.Bytes; Owner : E.Span; Name : String) return E.Span is
     (C.Canonical_JSON_Field (Data, Owner, Name));
   function Is_Text (Data : E.Bytes; Item : E.Span; Text : String) return Boolean is
   begin
      if not C.P.Valid (Data, Item) or else Item.Length /= E.Count (Text'Length) then return False; end if;
      for I in Text'Range loop
         if Data (Item.First + E.Count (I - Text'First)) /= E.Q.Byte (Character'Pos (Text (I))) then
            return False;
         end if;
      end loop;
      return True;
   end Is_Text;
   function Yes (Data : E.Bytes; Owner : E.Span; Name : String) return Boolean is
     (Is_Text (Data, Field (Data, Owner, Name), "true"));
   function No (Data : E.Bytes; Owner : E.Span; Name : String) return Boolean is
     (Is_Text (Data, Field (Data, Owner, Name), "false"));
   function Command_Ended (Data : E.Bytes; Item : E.Span) return Boolean is
     (No (Data, Item, "processCreatedObserved") or else
      (Yes (Data, Item, "processCreatedObserved") and then
       Yes (Data, Item, "processWaitReturnObserved") and then
       Yes (Data, Item, "stdoutReachedEof") and then Yes (Data, Item, "stderrReachedEof")));
   type Row_Kind is (Thread_Row, Command_Row, Socket_Row, Stream_Row);
   function Rows_Ended (Data : E.Bytes; Rows : E.Span; Kind : Row_Kind) return Boolean is
      Root : constant C.JSON_Node := C.JSON_Prefix (Data, Rows, 0);
      Offset : E.Count := 1;
   begin
      if not Root.Valid or else Root.Form /= C.Array_JSON_Value or else Root.After /= Rows.Length then return False; end if;
      if Rows.Length = 2 then return True; end if;
      while Offset < Rows.Length loop
         pragma Loop_Invariant (Offset <= Rows.Length);
         pragma Loop_Variant (Decreases => Rows.Length - Offset);
         declare
            Node : constant C.JSON_Node := C.JSON_Prefix (Data, Rows, Offset);
            Item : constant E.Span := C.Part (Rows, Node.First, Node.After);
            Good : Boolean;
         begin
            if not Node.Valid or else Node.After <= Offset or else Node.After >= Rows.Length then return False; end if;
            case Kind is
               when Thread_Row => Good := No (Data, Item, "alive");
               when Command_Row => Good := Command_Ended (Data, Item);
               when Socket_Row => Good := Is_Text (Data, Field (Data, Item, "fileno"), "-1");
               when Stream_Row =>
                  Good := No (Data, Item, "present") or else
                    (Yes (Data, Item, "present") and then Yes (Data, Item, "closed"));
            end case;
            if not Good then return False; end if;
            if Data (Rows.First + Node.After) = Character'Pos (']') then
               return Node.After = Rows.Length - 1;
            elsif Data (Rows.First + Node.After) /= Character'Pos (',') then return False;
            end if;
            Offset := Node.After + 1;
         end;
      end loop;
      return False;
   end Rows_Ended;
   function Eof_Complete (Data : E.Bytes; Item : E.Span) return Boolean is
      Root : constant C.JSON_Node := C.JSON_Prefix (Data, Item, 0);
      Offset : E.Count := 1;
   begin
      if Is_Text (Data, Item, "null") then return True; end if;
      if not Root.Valid or else Root.Form /= C.Object_JSON_Value or else Root.After /= Item.Length then return False; end if;
      if Item.Length = 2 then return True; end if;
      while Offset < Item.Length loop
         pragma Loop_Invariant (Offset <= Item.Length);
         pragma Loop_Variant (Decreases => Item.Length - Offset);
         declare
            Name : constant C.JSON_Node := C.JSON_Prefix (Data, Item, Offset);
            Value : C.JSON_Node;
         begin
            if not Name.Valid or else Name.Form /= C.String_JSON_Value or else
              Name.After <= Offset or else Name.After >= Item.Length - 1 or else
              Data (Item.First + Name.After) /= Character'Pos (':') then return False; end if;
            Value := C.JSON_Prefix (Data, Item, Name.After + 1);
            if not Value.Valid or else Value.After <= Name.After or else Value.After >= Item.Length or else
              not Is_Text (Data, C.Part (Item, Value.First, Value.After), "true") then return False; end if;
            if Data (Item.First + Value.After) = Character'Pos ('}') then
               return Value.After = Item.Length - 1;
            elsif Data (Item.First + Value.After) /= Character'Pos (',') then return False;
            end if;
            Offset := Value.After + 1;
         end;
      end loop;
      return False;
   end Eof_Complete;
   function Proxy_Ended (Data : E.Bytes; Item : E.Span) return Boolean is
     (Is_Text (Data, Item, "null") or else
      (Yes (Data, Item, "stopping") and then No (Data, Item, "listenerAlive") and then
       Rows_Ended (Data, Field (Data, Item, "handlers"), Thread_Row) and then
       Rows_Ended (Data, Field (Data, Item, "sockets"), Socket_Row)));
   function Quiescent (Data : E.Bytes; Owner : E.Span) return Boolean is
   begin
      if not C.Canonical_JSON_Valid (Data, Owner) or else
        not Yes (Data, Owner, "cleanupStarted") or else
        not Rows_Ended (Data, Field (Data, Owner, "unclosedCommands"), Command_Row) or else
        not Is_Text (Data, Field (Data, Owner, "activeControllerCalls"), "[]") or else
        not No (Data, Owner, "timerAlive") or else not No (Data, Owner, "samplerAlive") or else
        not Rows_Ended (Data, Field (Data, Owner, "streams"), Thread_Row) or else
        not Rows_Ended (Data, Field (Data, Owner, "tailDrains"), Thread_Row) or else
        not Eof_Complete (Data, Field (Data, Owner, "streamEofObserved")) then return False; end if;
      if not No (Data, Owner, "launcherPresent") and then
        not (Yes (Data, Owner, "launcherPresent") and then Yes (Data, Owner, "launcherWaitObserved") and then
             Yes (Data, Owner, "launcherStreamsClosed") and then
             Rows_Ended (Data, Field (Data, Owner, "launcherStreams"), Stream_Row)) then return False; end if;
      if not No (Data, Owner, "proxyPresent") and then
        not (Yes (Data, Owner, "proxyPresent") and then Yes (Data, Owner, "proxyClosed") and then
             Proxy_Ended (Data, Field (Data, Owner, "proxy"))) then return False; end if;
      return True;
   end Quiescent;
   end Canonical_View;
   function Quiescent (Data : E.Bytes; Owner : E.Span) return Boolean is
     (Canonical_View.Quiescent (Data, Owner));
   --  Finalization object pairs are Terminal arrays; their VALUES are already
   --  Finalization subtrees. Never decode them at Operation or rebuild JSON.
   function Text_View_Is (Data : E.Bytes; Value : E.View; Text : String) return Boolean;
   function Field (Data : E.Bytes; Owner : E.Span; Name : String) return E.Span is
      Root : constant E.View := E.Decode (Data, Owner, E.Finalization);
      Size : constant E.Count := E.Array_Length (Data, Root.Children);
      Found : E.Span := (1, 0);
   begin
      if Root.Form /= E.Object_Value then return Found; end if;
      if Size > 0 then
         for I in E.Count range 0 .. Size - 1 loop
            declare
               Pair : constant E.View := E.Decode
                 (Data, E.Array_Element (Data, Root.Children, I), E.Terminal);
            begin
               if Pair.Form /= E.List_Value or else
                 E.Array_Length (Data, Pair.Children) /= 2 then return (1, 0); end if;
               if Text_View_Is (Data, E.Decode (Data,
                 E.Array_Element (Data, Pair.Children, 0), E.Terminal), Name) then
                  if Found.Length /= 0 then return (1, 0); end if;
                  Found := E.Array_Element (Data, Pair.Children, 1);
               end if;
            end;
         end loop;
      end if;
      return Found;
   end Field;
   function Leaf_Length (Data : E.Bytes; Item : E.View) return E.Count is
      S : constant B.Span := (Item.Payload.Encoded.First, Item.Payload.Encoded.Length);
   begin
      if Item.Payload.Level = 0 then
         return (if C.P.Valid (Data, Item.Payload.Encoded) then Item.Payload.Encoded.Length else 0);
      end if;
      if not B.Canonical (Data, S) or else S.Length = 0 then return 0; end if;
      --  Canonicality is established once for this scan. Do not invoke
      --  Decoded_Length's whole-leaf Canonical precondition again.
      return (S.Length / 4) * 3 - B.Padding (Data, S);
   end Leaf_Length;
   function Leaf_Byte (Data : E.Bytes; Item : E.View; Offset : E.Count) return E.Q.Byte is
      S : constant E.Span := Item.Payload.Encoded;
      Group, Padding : E.Count;
      First, Second : E.Q.Byte;
   begin
      --  E.Decode and the caller's Leaf_Length establish the original leaf
      --  grammar before scanning. This accessor still checks its actual
      --  extent and selected digits, without a whole-leaf body or precondition
      --  scan at every byte. No caller validation flag or new input cap.
      if not C.P.Valid (Data, S) then return 0; end if;
      if Item.Payload.Level = 0 then
         return (if Offset < S.Length then Data (S.First + Offset) else 0);
      end if;
      if Item.Payload.Level /= 1 or else S.Length < 4 or else S.Length mod 4 /= 0 then return 0; end if;
      Padding := (if Data (S.First + (S.Length - 1)) /= Character'Pos ('=') then 0
                  elsif Data (S.First + (S.Length - 2)) = Character'Pos ('=') then 2 else 1);
      if Offset >= (S.Length / 4) * 3 - Padding then return 0; end if;
      Group := (Offset / 3) * 4;
      case Offset mod 3 is
         when 0 =>
            First := Data (S.First + Group);
            Second := Data (S.First + (Group + 1));
         when 1 =>
            First := Data (S.First + (Group + 1));
            Second := Data (S.First + (Group + 2));
         when others =>
            First := Data (S.First + (Group + 2));
            Second := Data (S.First + (Group + 3));
      end case;
      if not B.Is_Digit (First) or else not B.Is_Digit (Second) then return 0; end if;
      --  Digit's inherited preconditions are constant-time Is_Digit checks,
      --  unlike Decoded_Byte's automatic whole-leaf Canonical precondition.
      case Offset mod 3 is
         when 0 => return B.Digit (First) * 4 + B.Digit (Second) / 16;
         when 1 => return (B.Digit (First) mod 16) * 16 + B.Digit (Second) / 4;
         when others => return (B.Digit (First) mod 4) * 64 + B.Digit (Second);
      end case;
   end Leaf_Byte;
   function Text_View_Is (Data : E.Bytes; Value : E.View; Text : String) return Boolean is
   begin
      if Value.Form /= E.Text_Value or else Leaf_Length (Data, Value) /= E.Count (Text'Length)
      then return False; end if;
      for I in Text'Range loop
         if Leaf_Byte (Data, Value, E.Count (I - Text'First)) /= Character'Pos (Text (I))
         then return False; end if;
      end loop;
      return True;
   end Text_View_Is;
   function Text_Is (Data : E.Bytes; Item : E.Span; Text : String) return Boolean is
     (Text_View_Is (Data, E.Decode (Data, Item, E.Finalization), Text));
   function Is_True (Data : E.Bytes; Owner : E.Span; Name : String) return Boolean is
      Value : constant E.View := E.Decode (Data, Field (Data, Owner, Name), E.Finalization);
   begin
      return Value.Form = E.Boolean_Value and then Value.Boolean_Bit;
   end Is_True;
   function Is_False (Data : E.Bytes; Owner : E.Span; Name : String) return Boolean is
      Value : constant E.View := E.Decode (Data, Field (Data, Owner, Name), E.Finalization);
   begin
      return Value.Form = E.Boolean_Value and then not Value.Boolean_Bit;
   end Is_False;
   function Truth (Data : E.Bytes; Item : E.Span) return Boolean is
      Value : constant E.View := E.Decode (Data, Item, E.Finalization);
   begin
      case Value.Form is
         when E.Boolean_Value => return Value.Boolean_Bit;
         when E.Integer_Value | E.Text_Value | E.Bytes_Value =>
            --  Bytes has one additional base64 layer, but its inner spelling is
            --  empty exactly when the original bytes are empty.
            return Leaf_Length (Data, Value) > 0;
         when E.Float_Value =>
            if Leaf_Length (Data, Value) /= 8 then return False; end if;
            if Leaf_Byte (Data, Value, 0) mod 128 /= 0 then return True; end if;
            for I in E.Count range 1 .. 7 loop
               if Leaf_Byte (Data, Value, I) /= 0 then return True; end if;
            end loop;
            return False;
         when E.List_Value | E.Tuple_Value | E.Object_Value =>
            return E.Array_Length (Data, Value.Children) > 0;
         when others => return False;
      end case;
   end Truth;
   function Same_Span (Left_Data, Right_Data : E.Bytes; Left, Right : E.Span) return Boolean is
   begin
      if not C.P.Valid (Left_Data, Left) or else not C.P.Valid (Right_Data, Right) or else
        Left.Length /= Right.Length then return False; end if;
      if Left.Length > 0 then
         for I in E.Count range 0 .. Left.Length - 1 loop
            if Left_Data (Left.First + I) /= Right_Data (Right.First + I) then return False; end if;
         end loop;
      end if;
      return True;
   end Same_Span;
   function Equal (Left_Data, Right_Data : E.Bytes; Left, Right : E.Span) return Boolean is
      L : constant E.View := E.Decode (Left_Data, Left, E.Finalization);
      R : constant E.View := E.Decode (Right_Data, Right, E.Finalization);
      Size : constant E.Count := E.Array_Length (Left_Data, L.Children);
   begin
      if L.Form = E.Invalid or else L.Form /= R.Form then return False; end if;
      case L.Form is
         when E.Null_Value => return True;
         when E.Boolean_Value => return L.Boolean_Bit = R.Boolean_Bit;
         when E.Integer_Value | E.Float_Value | E.Text_Value | E.Bytes_Value =>
            return L.Sign = R.Sign and then L.Payload.Level = R.Payload.Level and then
              Same_Span (Left_Data, Right_Data, L.Payload.Encoded, R.Payload.Encoded);
         when E.List_Value | E.Tuple_Value =>
            if Size /= E.Array_Length (Right_Data, R.Children) then return False; end if;
            if Size > 0 then
               for I in E.Count range 0 .. Size - 1 loop
                  if not Equal (Left_Data, Right_Data, E.Array_Element (Left_Data, L.Children, I),
                    E.Array_Element (Right_Data, R.Children, I)) then return False; end if;
               end loop;
            end if;
            return True;
         when E.Object_Value =>
            if Size /= E.Array_Length (Right_Data, R.Children) then return False; end if;
            if Size > 0 then
               for I in E.Count range 0 .. Size - 1 loop
                  declare
                     Pair : constant E.View := E.Decode
                       (Left_Data, E.Array_Element (Left_Data, L.Children, I), E.Terminal);
                     Matches : E.Count := 0;
                  begin
                     if Pair.Form /= E.List_Value or else E.Array_Length (Left_Data, Pair.Children) /= 2
                     then return False; end if;
                     for J in E.Count range 0 .. Size - 1 loop
                        declare
                           Other : constant E.View := E.Decode
                             (Right_Data, E.Array_Element (Right_Data, R.Children, J), E.Terminal);
                           Key : constant E.View := E.Decode
                             (Left_Data, E.Array_Element (Left_Data, Pair.Children, 0), E.Terminal);
                           Other_Key : constant E.View := E.Decode
                             (Right_Data, E.Array_Element (Right_Data, Other.Children, 0), E.Terminal);
                        begin
                           if Other.Form /= E.List_Value or else
                             E.Array_Length (Right_Data, Other.Children) /= 2 or else
                             Key.Form /= E.Text_Value or else Other_Key.Form /= E.Text_Value
                           then return False; end if;
                           if Same_Span (Left_Data, Right_Data, Key.Payload.Encoded, Other_Key.Payload.Encoded) then
                              if not Equal (Left_Data, Right_Data, E.Array_Element (Left_Data, Pair.Children, 1),
                                E.Array_Element (Right_Data, Other.Children, 1)) then return False; end if;
                              Matches := Matches + 1;
                           end if;
                        end;
                     end loop;
                     if Matches /= 1 then return False; end if;
                  end;
               end loop;
            end if;
            return True;
         when others => return False;
      end case;
   end Equal;
   function Equal (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (Equal (Data, Data, Left, Right));
   function Empty_List (Data : E.Bytes; Item : E.Span) return Boolean is
      Value : constant E.View := E.Decode (Data, Item, E.Finalization);
   begin
      return Value.Form = E.List_Value and then E.Array_Length (Data, Value.Children) = 0;
   end Empty_List;
   function Command_Ended (Data : E.Bytes; Item : E.Span) return Boolean is
     (Is_False (Data, Item, "processCreatedObserved") or else
      (Is_True (Data, Item, "processCreatedObserved") and then
       Is_True (Data, Item, "processWaitReturnObserved") and then
       Is_True (Data, Item, "stdoutReachedEof") and then Is_True (Data, Item, "stderrReachedEof")));
   type Rows_Kind is (Threads, Commands, Sockets, Streams);
   function Rows_Ended (Data : E.Bytes; Rows : E.Span; Kind : Rows_Kind) return Boolean is
      Root : constant E.View := E.Decode (Data, Rows, E.Finalization);
      Size : constant E.Count := E.Array_Length (Data, Root.Children);
   begin
      if Root.Form /= E.List_Value then return False; end if;
      if Size > 0 then
         for I in E.Count range 0 .. Size - 1 loop
            declare Item : constant E.Span := E.Array_Element (Data, Root.Children, I);
            begin
               case Kind is
                  when Threads => if not Is_False (Data, Item, "alive") then return False; end if;
                  when Commands => if not Command_Ended (Data, Item) then return False; end if;
                  when Streams =>
                     if not Is_False (Data, Item, "present") and then
                       not (Is_True (Data, Item, "present") and then Is_True (Data, Item, "closed"))
                     then return False; end if;
                  when Sockets =>
                     declare N : constant E.View := E.Decode
                       (Data, Field (Data, Item, "fileno"), E.Finalization);
                     begin
                        if N.Form /= E.Integer_Value or else not N.Sign or else
                          Leaf_Length (Data, N) /= 1 or else Leaf_Byte (Data, N, 0) /= 1
                        then return False; end if;
                     end;
               end case;
            end;
         end loop;
      end if;
      return True;
   end Rows_Ended;
   function Ended (Data : E.Bytes; Rows : E.Span) return Boolean is
     (Rows_Ended (Data, Rows, Threads));
   function Commands_Ended (Data : E.Bytes; Rows : E.Span) return Boolean is
     (Rows_Ended (Data, Rows, Commands));
   function Eof_Complete (Data : E.Bytes; Item : E.Span) return Boolean is
      Root : constant E.View := E.Decode (Data, Item, E.Finalization);
      Size : constant E.Count := E.Array_Length (Data, Root.Children);
   begin
      if Root.Form = E.Null_Value then return True; end if;
      if Root.Form /= E.Object_Value then return False; end if;
      if Size > 0 then
         for I in E.Count range 0 .. Size - 1 loop
            declare
               Pair : constant E.View := E.Decode
                 (Data, E.Array_Element (Data, Root.Children, I), E.Terminal);
               Key : constant E.View := E.Decode
                 (Data, E.Array_Element (Data, Pair.Children, 0), E.Terminal);
               Value : constant E.View := E.Decode
                 (Data, E.Array_Element (Data, Pair.Children, 1), E.Finalization);
            begin
               if Pair.Form /= E.List_Value or else E.Array_Length (Data, Pair.Children) /= 2 or else
                 Key.Form /= E.Text_Value or else Value.Form /= E.Boolean_Value or else
                 not Value.Boolean_Bit then return False; end if;
            end;
         end loop;
      end if;
      return True;
   end Eof_Complete;
   function Proxy_Ended (Data : E.Bytes; Item : E.Span) return Boolean is
      Root : constant E.View := E.Decode (Data, Item, E.Finalization);
   begin
      return Root.Form = E.Null_Value or else
        (Is_True (Data, Item, "stopping") and then Is_False (Data, Item, "listenerAlive") and then
         Ended (Data, Field (Data, Item, "handlers")) and then
         Rows_Ended (Data, Field (Data, Item, "sockets"), Sockets));
   end Proxy_Ended;
   function Quiescent (Data : E.Bytes; Owner : E.View) return Boolean is
      Item : constant E.Span := Owner.Raw;
   begin
      if Owner.At_Layer /= E.Finalization or else Owner.Form /= E.Object_Value or else
        not Is_True (Data, Item, "cleanupStarted") or else
        not Commands_Ended (Data, Field (Data, Item, "unclosedCommands")) or else
        not Empty_List (Data, Field (Data, Item, "activeControllerCalls")) or else
        not Is_False (Data, Item, "timerAlive") or else not Is_False (Data, Item, "samplerAlive") or else
        not Ended (Data, Field (Data, Item, "streams")) or else
        not Ended (Data, Field (Data, Item, "tailDrains")) or else
        not Eof_Complete (Data, Field (Data, Item, "streamEofObserved"))
      then return False; end if;
      if not Is_False (Data, Item, "launcherPresent") and then
        not (Is_True (Data, Item, "launcherPresent") and then Is_True (Data, Item, "launcherWaitObserved") and then
             Is_True (Data, Item, "launcherStreamsClosed") and then
             Rows_Ended (Data, Field (Data, Item, "launcherStreams"), Streams))
      then return False; end if;
      if not Is_False (Data, Item, "proxyPresent") and then
        not (Is_True (Data, Item, "proxyPresent") and then Is_True (Data, Item, "proxyClosed") and then
             Proxy_Ended (Data, Field (Data, Item, "proxy")))
      then return False; end if;
      return True;
   end Quiescent;
   function Finalization_Quiescent (Data : E.Bytes; Owner : E.Span) return Boolean is
     (Quiescent (Data, E.Decode (Data, Owner, E.Finalization)));
   function Generation_Stable (Data : E.Bytes; Owner : E.Span) return Boolean is
     (Empty_List (Data, Field (Data, Owner, "controllerCallsAfterClosure")));
   function Guard_Released (Data : E.Bytes; Owner : E.Span) return Boolean is
     (Is_True (Data, Owner, "guardReleaseReturnObserved") and then
      (Is_False (Data, Owner, "guardOwned") or else
       (Is_True (Data, Owner, "guardOwned") and then Is_False (Data, Owner, "guardDecisionPresent"))));
   function Finished (Data : E.Bytes; Owner : E.Span) return Boolean is
     (Finalization_Quiescent (Data, Owner) and then
      (Is_False (Data, Owner, "guardPresent") or else
       (Is_True (Data, Owner, "guardPresent") and then Is_True (Data, Owner, "guardReleased") and then
        Guard_Released (Data, Owner))));
   function Reference_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
      Ref : constant E.View := E.Decode (Data, Field (Data, Item, "reference"), E.Finalization);
      Typ : constant E.View := E.Decode (Data, Field (Data, Item, "typeReference"), E.Finalization);
   begin
      return Ref.Form = E.Integer_Value and then not Ref.Sign and then Truth (Data, Ref.Raw) and then
        Typ.Form = E.Integer_Value and then not Typ.Sign and then Truth (Data, Typ.Raw);
   end Reference_Valid;
   function Cancellation_Membership_Valid (Data : E.Bytes; Capture : E.Span) return Boolean is
      Rows : constant E.View := E.Decode (Data, Field (Data, Capture, "roster"), E.Finalization);
      Requested : constant E.Span := Field (Data, Capture, "requested");
      Observation : constant E.Span := Field (Data, Capture, "protocolObservation");
      Size : constant E.Count := E.Array_Length (Data, Rows.Children);
      Builtin : constant Boolean := Text_Is (Data, Field (Data, Capture, "profile"), "builtin-set-string-v1");
      Actual : constant Boolean := Text_Is (Data, Field (Data, Capture, "profile"), "python-actual-protocol-v1");
      Answer : constant E.View := E.Decode (Data, Field (Data, Observation, "returnedTruth"), E.Finalization);
   begin
      if Rows.Form /= E.List_Value then return False; end if;
      if Builtin then
         if E.Decode (Data, Requested, E.Finalization).Form /= E.Text_Value then return False; end if;
      elsif Actual then
         if not Reference_Valid (Data, Requested) or else
           not Reference_Valid (Data, Field (Data, Capture, "rosterType")) or else
           not Text_Is (Data, Field (Data, Observation, "operator"), "contains") or else
           Answer.Form /= E.Boolean_Value then return False; end if;
      else return False;
      end if;
      if Size > 0 then
         for I in E.Count range 0 .. Size - 1 loop
            declare Item : constant E.Span := E.Array_Element (Data, Rows.Children, I);
            begin
               if (Builtin and then E.Decode (Data, Item, E.Finalization).Form /= E.Text_Value) or else
                 (Actual and then not Reference_Valid (Data, Item)) then return False; end if;
            end;
         end loop;
      end if;
      return True;
   end Cancellation_Membership_Valid;
   function Cancellation_Membership (Data : E.Bytes; Capture : E.Span) return Boolean is
      Rows : constant E.View := E.Decode (Data, Field (Data, Capture, "roster"), E.Finalization);
      Size : constant E.Count := E.Array_Length (Data, Rows.Children);
   begin
      if not Cancellation_Membership_Valid (Data, Capture) then return False; end if;
      if Text_Is (Data, Field (Data, Capture, "profile"), "python-actual-protocol-v1") then
         return Is_True (Data, Field (Data, Capture, "protocolObservation"), "returnedTruth");
      end if;
      if Size > 0 then
         for I in E.Count range 0 .. Size - 1 loop
            if Equal (Data, E.Array_Element (Data, Rows.Children, I), Field (Data, Capture, "requested"))
            then return True; end if;
         end loop;
      end if;
      return False;
   end Cancellation_Membership;
   function Hex_Digit (Value : E.Q.Byte) return Integer is
     (if Value in Character'Pos ('0') .. Character'Pos ('9') then Integer (Value) - Character'Pos ('0')
      elsif Value in Character'Pos ('a') .. Character'Pos ('f') then Integer (Value) - Character'Pos ('a') + 10
      else -1);
   function Positive_Integer_Hex (Data : E.Bytes; Item : E.Span) return Boolean is
      Value : constant E.View := E.Decode (Data, Item, E.Finalization);
      Size : constant E.Count := Leaf_Length (Data, Value);
   begin
      if Value.Form /= E.Text_Value or else Size < 3 or else
        Leaf_Byte (Data, Value, 0) /= Character'Pos ('0') or else
        Leaf_Byte (Data, Value, 1) /= Character'Pos ('x') or else
        Hex_Digit (Leaf_Byte (Data, Value, 2)) <= 0 then return False; end if;
      for I in E.Count range 2 .. Size - 1 loop
         if Hex_Digit (Leaf_Byte (Data, Value, I)) < 0 then return False; end if;
      end loop;
      return True;
   end Positive_Integer_Hex;
   function Positive_Float_Bits (Data : E.Bytes; Item : E.Span) return Boolean is
      Value : constant E.View := E.Decode (Data, Item, E.Finalization);
      D : array (E.Count range 0 .. 15) of Integer;
      Nonzero, Fraction : Boolean := False;
   begin
      if Value.Form /= E.Text_Value or else Leaf_Length (Data, Value) /= 16 then return False; end if;
      for I in D'Range loop
         D (I) := Hex_Digit (Leaf_Byte (Data, Value, I));
         if D (I) < 0 then return False; end if;
         if D (I) /= 0 then Nonzero := True; end if;
         if I >= 3 and then D (I) /= 0 then Fraction := True; end if;
      end loop;
      --  Binary64 big-endian hex: digit 0 is the sign and the top three
      --  exponent bits, digits 1 and 2 the remaining eight exponent bits, and
      --  digits 3 .. 15 the whole 52-bit fraction. An all-ones exponent is
      --  exactly D (0) = 7 (positive), D (1) = 15 and D (2) = 15; with a zero
      --  fraction it is +inf, otherwise NaN. Positive infinity and every
      --  positive finite value pass, either signed zero, every negative value
      --  and every NaN payload fail, exactly Python > 0. The earlier text took
      --  the lowest exponent bit for a fraction bit and admitted exponent 7fe,
      --  so +inf was refused and the largest finite positives were called NaN.
      return D (0) < 8 and then Nonzero and then
        not (D (0) = 7 and then D (1) = 15 and then D (2) = 15 and then Fraction);
   end Positive_Float_Bits;
   function Positive_Float_Hex (Data : E.Bytes; Item : E.Span) return Boolean is
      Value : constant E.View := E.Decode (Data, Item, E.Finalization);
      Size : constant E.Count := Leaf_Length (Data, Value);
      Nonzero : Boolean := False;
      Exponent : Natural := 0;
      Negative_Exponent : Boolean;
   begin
      if Text_Is (Data, Item, "inf") then return True; end if;
      --  Exact positive finite float.hex(): one leading 0/1, thirteen
      --  fractional nibbles and the bounded binary64 exponent spelling.
      --  Canonical +/-zero and nan are false without requesting a comparator.
      if Value.Form /= E.Text_Value or else Size < 20 or else Size > 23 or else
        Leaf_Byte (Data, Value, 0) /= Character'Pos ('0') or else
        Leaf_Byte (Data, Value, 1) /= Character'Pos ('x') or else
        Leaf_Byte (Data, Value, 2) not in Character'Pos ('0') .. Character'Pos ('1') or else
        Leaf_Byte (Data, Value, 3) /= Character'Pos ('.') or else
        Leaf_Byte (Data, Value, 17) /= Character'Pos ('p') or else
        (Leaf_Byte (Data, Value, 18) /= Character'Pos ('+') and then
         Leaf_Byte (Data, Value, 18) /= Character'Pos ('-')) then return False; end if;
      Nonzero := Leaf_Byte (Data, Value, 2) = Character'Pos ('1');
      for I in E.Count range 4 .. 16 loop
         if Hex_Digit (Leaf_Byte (Data, Value, I)) < 0 then return False; end if;
         Nonzero := Nonzero or else Hex_Digit (Leaf_Byte (Data, Value, I)) > 0;
      end loop;
      if Size > 20 and then Leaf_Byte (Data, Value, 19) = Character'Pos ('0')
      then return False; end if;
      for I in E.Count range 19 .. Size - 1 loop
         if Leaf_Byte (Data, Value, I) not in Character'Pos ('0') .. Character'Pos ('9')
         then return False; end if;
         Exponent := Exponent * 10 + Natural (Leaf_Byte (Data, Value, I) - Character'Pos ('0'));
      end loop;
      Negative_Exponent := Leaf_Byte (Data, Value, 18) = Character'Pos ('-');
      if Negative_Exponent and then (Exponent = 0 or else Exponent > 1022)
      then return False; end if;
      if not Negative_Exponent and then Exponent > 1023 then return False; end if;
      if Leaf_Byte (Data, Value, 2) = Character'Pos ('0') and then
        (not Negative_Exponent or else Exponent /= 1022) then return False; end if;
      return Nonzero;
   end Positive_Float_Hex;
   function Timer_Active (Data : E.Bytes; Owner : E.Span) return Boolean is
      Kind : constant E.Span := Field (Data, Owner, "timeoutType");
      Protocol : constant E.Span := Field (Data, Owner, "timeoutProtocol");
      Operand : constant E.View := E.Decode (Data, Field (Data, Protocol, "operand"), E.Finalization);
   begin
      if Text_Is (Data, Kind, "int") then
         return Positive_Integer_Hex (Data, Field (Data, Owner, "timeoutIntegerHex"));
      elsif Text_Is (Data, Kind, "bool") then return Is_True (Data, Owner, "timeoutValue");
      elsif Text_Is (Data, Kind, "float") then
         if Field (Data, Owner, "timeoutFloatBits").Length /= 0 then
            return Positive_Float_Bits (Data, Field (Data, Owner, "timeoutFloatBits"));
         end if;
         return Positive_Float_Hex (Data, Field (Data, Owner, "timeoutFloatHex"));
      elsif Text_Is (Data, Kind, "python-actual-protocol-v1") then
         return Text_Is (Data, Field (Data, Protocol, "operator"), "gt") and then
           Operand.Form = E.Integer_Value and then not Operand.Sign and then
           not Truth (Data, Operand.Raw) and then Is_True (Data, Protocol, "returnedTruth");
      end if;
      return False;
   end Timer_Active;
   function Type_Id (Data : E.Bytes; Owner : E.Span; Name : String) return Boolean is
      Value : constant E.View := E.Decode (Data, Field (Data, Owner, Name), E.Finalization);
   begin
      return Value.Form = E.Integer_Value and then not Value.Sign and then Truth (Data, Value.Raw);
   end Type_Id;
   function Controller_Stopped (Data : E.Bytes; Owner : E.Span) return Boolean is
      Unit : constant E.Span := Field (Data, Owner, "controllerUnit");
      Kind : constant E.Span := Field (Data, Unit, "type");
      Value : constant E.View := E.Decode (Data, Field (Data, Unit, "value"), E.Finalization);
      Protocol : constant E.Span := Field (Data, Owner, "controllerUnitProtocol");
   begin
      if Text_Is (Data, Kind, "python-actual-reference-v1") then
         return Reference_Valid (Data, Unit) and then
           Text_Is (Data, Field (Data, Protocol, "operator"), "truth") and then
           Is_True (Data, Protocol, "returnedTruth");
      end if;
      if (Text_Is (Data, Kind, "NoneType") and then Value.Form = E.Null_Value) or else
        (Text_Is (Data, Kind, "bool") and then Value.Form = E.Boolean_Value) or else
        (Text_Is (Data, Kind, "int") and then Value.Form = E.Integer_Value) or else
        (Text_Is (Data, Kind, "float") and then Value.Form = E.Float_Value) or else
        (Text_Is (Data, Kind, "str") and then Value.Form = E.Text_Value) or else
        (Text_Is (Data, Kind, "bytes") and then Value.Form = E.Bytes_Value)
      then return Truth (Data, Value.Raw); end if;
      return False;
   end Controller_Stopped;
   function Allowed
     (Data : E.Bytes; Owner : E.Span; Requested : Runner_Lifecycle.Action) return Boolean is
      use Runner_Lifecycle;
      Errors : constant E.View := E.Decode (Data, Field (Data, Owner, "threadErrors"), E.Finalization);
   begin
      case Requested is
         when Observe_Quiescence => return Finalization_Quiescent (Data, Owner);
         when Observe_Finished | Forget_Owner => return Finished (Data, Owner);
         when Drain_Tails =>
            return Is_True (Data, Owner, "launcherPresent") and then Is_True (Data, Owner, "launcherWaitObserved") and then
              Ended (Data, Field (Data, Owner, "streams"));
         when Close_Streams =>
            return Is_True (Data, Owner, "launcherPresent") and then Is_True (Data, Owner, "launcherWaitObserved") and then
              Ended (Data, Field (Data, Owner, "streams")) and then
              Eof_Complete (Data, Field (Data, Owner, "streamEofObserved")) and then
              Ended (Data, Field (Data, Owner, "tailDrains"));
         when Release_Guard =>
            return Finalization_Quiescent (Data, Owner) and then Is_True (Data, Owner, "guardPresent") and then
              Is_False (Data, Owner, "guardReleased") and then Is_False (Data, Owner, "guardReleaseAttempted");
         when Stop_Launcher =>
            return Is_True (Data, Owner, "launcherPresent") and then Is_False (Data, Owner, "launcherWaitObserved") and then
              Is_False (Data, Owner, "launcherCleanupAttempted");
         when Observe_Manager =>
            return Is_True (Data, Owner, "launcherPresent") and then Is_True (Data, Owner, "launcherWaitObserved") and then
              Is_False (Data, Owner, "managerAttempted");
         when Observe_Proxy => return Proxy_Ended (Data, Owner);
         when Observe_Command => return Command_Ended (Data, Owner);
         when Observe_Streams_Closed => return Rows_Ended (Data, Field (Data, Owner, "launcherStreams"), Streams);
         when Observe_Guard_Released => return Guard_Released (Data, Owner);
         when Observe_Cancellation_Complete =>
            return Is_True (Data, Owner, "processWaitReturnObserved") and then
              Is_True (Data, Owner, "stdoutReachedEof") and then Is_True (Data, Owner, "stderrReachedEof");
         when Query_Publication =>
            return Text_Is (Data, Field (Data, Owner, "worldState"), "VALID") or else
              Text_Is (Data, Field (Data, Owner, "worldState"), "DEGRADED");
         when Recover_Run =>
            return Text_Is (Data, Field (Data, Owner, "worldState"), "FINALIZING") or else
              ((Text_Is (Data, Field (Data, Owner, "worldState"), "VALID") or else
                Text_Is (Data, Field (Data, Owner, "worldState"), "DEGRADED")) and then
               Truth (Data, Field (Data, Owner, "publicationPending")));
         when Start_Run => return Text_Is (Data, Field (Data, Owner, "worldState"), "MUTABLE");
         when Mark_World_Dead =>
            return Text_Is (Data, Field (Data, Owner, "worldState"), "MUTABLE") and then
              Errors.Form = E.List_Value and then E.Array_Length (Data, Errors.Children) > 0;
         when Mark_Job_Dead => return Errors.Form = E.List_Value and then E.Array_Length (Data, Errors.Children) > 0;
         when Run_Stopped =>
            declare Stop : constant E.Span := Field (Data, Owner, "stopMembership");
            begin
               return Cancellation_Membership (Data, Field (Data, Stop, "cancelled")) or else
                 Cancellation_Membership (Data, Field (Data, Stop, "timedOut"));
            end;
         when Observe_Membership => return Cancellation_Membership (Data, Owner);
         when Capture_Membership_Protocol =>
            return Text_Is (Data, Field (Data, Owner, "profile"), "python-actual-protocol-v1") and then
              Field (Data, Owner, "protocolObservation").Length = 0;
         when Route_Controller =>
            return Is_True (Data, Owner, "ownerPresent") and then
              Type_Id (Data, Owner, "ownerUnitType") and then Type_Id (Data, Owner, "systemdProcessType") and then
              Type_Id (Data, Owner, "requestedType") and then Type_Id (Data, Owner, "stringType") and then
              Type_Id (Data, Owner, "ownerUnitNameType") and then
              Equal (Data, Field (Data, Owner, "ownerUnitType"), Field (Data, Owner, "systemdProcessType")) and then
              Equal (Data, Field (Data, Owner, "requestedType"), Field (Data, Owner, "stringType")) and then
              Equal (Data, Field (Data, Owner, "ownerUnitNameType"), Field (Data, Owner, "stringType")) and then
              E.Decode (Data, Field (Data, Owner, "ownerUnitName"), E.Finalization).Form = E.Text_Value and then
              E.Decode (Data, Field (Data, Owner, "requestedUnit"), E.Finalization).Form = E.Text_Value and then
              Equal (Data, Field (Data, Owner, "ownerUnitName"), Field (Data, Owner, "requestedUnit"));
         when Activate_Timer => return Timer_Active (Data, Owner);
         when Capture_Timer_Protocol =>
            return Text_Is (Data, Field (Data, Owner, "timeoutType"), "python-actual-protocol-v1") and then
              Field (Data, Owner, "timeoutProtocol").Length = 0;
         when Stop_Controller => return Controller_Stopped (Data, Owner);
         when Capture_Controller_Stop_Protocol =>
            declare Unit : constant E.Span := Field (Data, Owner, "controllerUnit");
            begin
               return Text_Is (Data, Field (Data, Unit, "type"), "python-actual-reference-v1") and then
                 Reference_Valid (Data, Unit) and then Field (Data, Owner, "controllerUnitProtocol").Length = 0;
            end;
      end case;
   end Allowed;
   function Text_Is (Data : E.Bytes; Item : E.View; Text : String) return Boolean is
     (Text_View_Is (Data, Item, Text));
   function Text_Equal (Left_Data, Right_Data : E.Bytes; Left, Right : E.View) return Boolean is
     (Left.Form = E.Text_Value and then Right.Form = E.Text_Value and then
      Left.Payload.Level = Right.Payload.Level and then
      Same_Span (Left_Data, Right_Data, Left.Payload.Encoded, Right.Payload.Encoded));
end Worldline.Runner_Lifecycle_Bytes;
