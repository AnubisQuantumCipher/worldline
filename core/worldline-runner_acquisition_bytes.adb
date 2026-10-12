with Worldline.Archive_Base64;
with Worldline.Runner_Lifecycle;
with Worldline.Runner_Lifecycle_Bytes;
package body Worldline.Runner_Acquisition_Bytes with SPARK_Mode is
   package L renames Worldline.Runner_Lifecycle;
   package V renames Worldline.Runner_Lifecycle_Bytes;
   use type E.Value_Kind;
   use type E.Count;
   use type E.Q.Byte;
   function Empty_Bytes (Data : E.Bytes; Item : E.Span) return Boolean is
      Value : constant E.View := E.Decode (Data, Item, E.Finalization);
   begin
      return (Value.Form = E.Bytes_Value and then not V.Truth (Data, Item)) or else
        (Value.Form = E.Object_Value and then
         V.Text_Is (Data, V.Field (Data, Item, "encoding"), "base64") and then
         V.Text_Is (Data, V.Field (Data, Item, "payload"), ""));
   end Empty_Bytes;
   function Capture_Same (Left_Data, Right_Data : E.Bytes; Left, Right : E.Span) return Boolean is
      Reference : constant E.View := E.Decode (Left_Data,
        V.Field (Left_Data, Left, "reference"), E.Finalization);
   begin
      if V.Text_Is (Left_Data, V.Field (Left_Data, Left, "type"), "python-actual-reference-v1") then
         --  Object identity is the source join. An intervening actual __class__
         --  change is not an authorization refusal absent from original wait.
         return Reference.Form = E.Integer_Value and then not Reference.Sign and then
           V.Truth (Left_Data, Reference.Raw) and then
           V.Text_Is (Right_Data, V.Field (Right_Data, Right, "type"), "python-actual-reference-v1") and then
           V.Equal (Left_Data, Right_Data, Reference.Raw, V.Field (Right_Data, Right, "reference"));
      end if;
      return V.Equal (Left_Data, Right_Data, Left, Right);
   end Capture_Same;
   function Raw_Wait
     (Owner_Data, Data : E.Bytes; Owner, Unit_Name : E.Span;
      Acquisitions : E.View) return Boolean is
      Size : constant E.Count := E.Array_Length (Data, Acquisitions.Children);
      Expected : constant E.Span := V.Field (Owner_Data, Owner, "launcherReturncode");
      Capture : constant E.Span := V.Field (Owner_Data, Owner, "launcherReturncodeCapture");
   begin
      if Size > 0 then
         for I in E.Count range 0 .. Size - 1 loop
            declare
               Item : constant E.Span := E.Array_Element (Data, Acquisitions.Children, I);
               Value : constant E.Span := V.Field (Data, Item, "observation");
               Actual : constant E.Span := V.Field (Data, Value, "returncode");
               Actual_Capture : constant E.Span := V.Field (Data, Value, "returncodeCapture");
            begin
               if V.Text_Is (Data, V.Field (Data, Item, "kind"), "agent-launcher-wait") and then
                 V.Equal (Owner_Data, Data, Unit_Name, V.Field (Data, Value, "unit")) and then
                 V.Is_True (Data, Value, "waitReturnObserved") and then
                 E.Decode (Data, Actual, E.Finalization).Form /= E.Invalid and then
                 E.Decode (Owner_Data, Expected, E.Finalization).Form /= E.Invalid and then
                 (if Capture.Length /= 0 and then Actual_Capture.Length /= 0 then
                     Capture_Same (Owner_Data, Data, Capture, Actual_Capture) and then
                     (V.Text_Is (Owner_Data, V.Field (Owner_Data, Capture, "type"), "python-actual-reference-v1") or else
                      (V.Equal (Owner_Data, Expected, V.Field (Owner_Data, Capture, "value")) and then
                       V.Equal (Data, Actual, V.Field (Data, Actual_Capture, "value"))))
                  else V.Equal (Owner_Data, Data, Expected, Actual))
               then return True; end if;
            end;
         end loop;
      end if;
      return False;
   end Raw_Wait;
   function Raw_Eof
     (Owner_Data, Data : E.Bytes; Unit_Name : E.Span; Name : E.View;
      Acquisitions : E.View) return Boolean is
      Size : constant E.Count := E.Array_Length (Data, Acquisitions.Children);
      function Name_Is (Text : String) return Boolean is
        (V.Text_Is (Owner_Data, Name, Text));
      function Same_Name (Item : E.Span) return Boolean is
         Actual : constant E.View := E.Decode (Data, Item, E.Finalization);
      begin
         return V.Text_Equal (Owner_Data, Data, Name, Actual);
      end Same_Name;
   begin
      if Size > 0 then
         for I in E.Count range 0 .. Size - 1 loop
            declare
               Item : constant E.Span := E.Array_Element (Data, Acquisitions.Children, I);
               Kind : constant E.Span := V.Field (Data, Item, "kind");
               Value : constant E.Span := V.Field (Data, Item, "observation");
            begin
               if V.Text_Is (Data, Kind, "agent-stream-tail-read") and then
                 Same_Name (V.Field (Data, Value, "stream")) and then
                 V.Is_True (Data, Value, "readReturned") and then V.Is_True (Data, Value, "readReachedEof") and then
                 E.Decode (Data, V.Field (Data, Value, "exception"), E.Finalization).Form = E.Null_Value and then
                 Empty_Bytes (Data, V.Field (Data, Value, "bytes")) then return True;
               elsif V.Equal (Owner_Data, Data, Unit_Name, V.Field (Data, Value, "unit")) then
                  if Name_Is ("stdout") and then V.Text_Is (Data, Kind, "agent-stdout-iterator-return") and then
                    V.Is_True (Data, Value, "endOfIteratorObserved") then return True;
                  elsif Name_Is ("stderr") and then V.Text_Is (Data, Kind, "agent-stderr-read") and then
                    Empty_Bytes (Data, V.Field (Data, Value, "bytes")) then return True;
                  end if;
               end if;
            end;
         end loop;
      end if;
      return False;
   end Raw_Eof;
   function Owner_Closed
     (Subject_Data, Data, Acquisition_Data : E.Bytes;
      Subject, Owner : E.Span; Acquisitions : E.View) return Boolean is
      Eof : constant E.View := E.Decode (Data, V.Field (Data, Owner, "streamEofObserved"), E.Finalization);
      Unit_Name : constant E.Span := V.Field (Data, Owner, "actualUnit");
      Guard : constant E.View := E.Decode (Data, V.Field (Data, Owner, "guardPresent"), E.Finalization);
      Size : constant E.Count := E.Array_Length (Data, Eof.Children);
   begin
      if not L.Finished (Data, Owner) or else not L.Generation_Stable (Data, Owner) or else
        Guard.Form /= E.Boolean_Value or else
        (E.Decode (Subject_Data, Subject, E.Finalization).Form /= E.Null_Value and then
         not V.Equal (Subject_Data, Data, Subject, V.Field (Data, Owner, "subject")))
      then return False; end if;
      if V.Is_True (Data, Owner, "launcherPresent") and then
        (not V.Is_True (Data, Owner, "launcherWaitObserved") or else
         not V.Is_True (Data, Owner, "launcherStreamsClosed") or else
         not Raw_Wait (Data, Acquisition_Data, Owner, Unit_Name, Acquisitions))
      then return False; end if;
      if Eof.Form = E.Object_Value then
         if Size > 0 then
            for I in E.Count range 0 .. Size - 1 loop
               declare
                  Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, Eof.Children, I), E.Terminal);
                  Name : constant E.View := E.Decode (Data, E.Array_Element (Data, Pair.Children, 0), E.Terminal);
                  Value : constant E.View := E.Decode (Data, E.Array_Element (Data, Pair.Children, 1), E.Finalization);
               begin
                  if Pair.Form /= E.List_Value or else E.Array_Length (Data, Pair.Children) /= 2 or else
                    Name.Form /= E.Text_Value or else Value.Form /= E.Boolean_Value or else not Value.Boolean_Bit or else
                    not Raw_Eof (Data, Acquisition_Data, Unit_Name, Name, Acquisitions) then return False; end if;
               end;
            end loop;
         end if;
      elsif Eof.Form /= E.Null_Value then return False;
      end if;
      return True;
   end Owner_Closed;
   function Controls_Ended (Data : E.Bytes; Acquisitions : E.View) return Boolean is
      Size : constant E.Count := E.Array_Length (Data, Acquisitions.Children);
      --  A cgroup file read is the synchronous Path.read_bytes callback inside
      --  the original _cgroup_value producer. Its context manager closes the
      --  handle whether the read returned a payload or raised, so BOTH complete
      --  original record shapes are ENDED acquisitions with nothing left to
      --  clean up: the successful read (readReturned true, canonical bytes,
      --  null exception) and the failed read (readReturned false, null bytes,
      --  the complete exception-observation object the producer retains, for
      --  example ENOENT when the unit's cgroup was removed between
      --  `systemctl show` and the read). The agent-native producer already
      --  reads the failed shape as honest absence; refusing it here left a
      --  finished workload permanently non-quiescent (the Source20 first
      --  original error, observed operands retained). Anything else -- a
      --  missing or extra field, bytes beside a failure, an exception beside
      --  a success, a partial exception object -- stays refused, and extra
      --  process fields still never route around the unchanged wait/EOF
      --  predicate.
      function Small_Integer_Is (Item : E.Span; Zero : Boolean) return Boolean is
         Value : constant E.View := E.Decode (Data, Item, E.Finalization);
      begin
         if Value.Form /= E.Integer_Value or else Value.Sign or else
           not E.Bytes_Valid (Data, Value.Payload) then return False; end if;
         declare
            Magnitude : constant E.Bytes := E.Materialize (Data, Value.Payload);
         begin
            --  Little-endian magnitude without trailing zero: 0 is empty and 1
            --  is the single byte 1.
            if Zero then return Magnitude'Length = 0; end if;
            return Magnitude'Length = 1 and then Magnitude (Magnitude'First) = 1;
         end;
      end Small_Integer_Is;
      function Cgroup_Read_Shape (Value : E.Span) return Boolean is
         Root : constant E.View := E.Decode (Data, Value, E.Finalization);
         Fields : constant E.Count := E.Array_Length (Data, Root.Children);
         Group : constant E.View := E.Decode
           (Data, V.Field (Data, Value, "controlGroup"), E.Finalization);
         Name : constant E.View := E.Decode
           (Data, V.Field (Data, Value, "name"), E.Finalization);
         Path : constant E.View := E.Decode
           (Data, V.Field (Data, Value, "path"), E.Finalization);
      begin
         --  The complete original shape shared by both read outcomes. Every
         --  one of the eight original fields is required and no other field
         --  is admitted, so a process record relabelled "cgroup-read" or a
         --  record carrying an unrecognized resource is refused.
         if Root.Form /= E.Object_Value or else
           not Small_Integer_Is (V.Field (Data, Value, "schemaVersion"), Zero => False) or else
           not V.Text_Is (Data, V.Field (Data, Value, "site"), "cgroup-read") or else
           Group.Form /= E.Text_Value or else not V.Truth (Data, Group.Raw) or else
           Name.Form /= E.Text_Value or else not V.Truth (Data, Name.Raw) or else
           Path.Form /= E.Bytes_Value or else not V.Truth (Data, Path.Raw) or else
           V.Field (Data, Value, "readReturned").Length = 0 or else
           V.Field (Data, Value, "bytes").Length = 0 or else
           V.Field (Data, Value, "exception").Length = 0
         then return False; end if;
         if Fields > 0 then
            for J in E.Count range 0 .. Fields - 1 loop
               declare
                  Pair : constant E.View := E.Decode
                    (Data, E.Array_Element (Data, Root.Children, J), E.Terminal);
                  Key : constant E.View := E.Decode
                    (Data, E.Array_Element (Data, Pair.Children, 0), E.Terminal);
               begin
                  if Pair.Form /= E.List_Value or else E.Array_Length (Data, Pair.Children) /= 2 or else
                    not (V.Text_Is (Data, Key, "schemaVersion") or else V.Text_Is (Data, Key, "site") or else
                         V.Text_Is (Data, Key, "controlGroup") or else V.Text_Is (Data, Key, "name") or else
                         V.Text_Is (Data, Key, "path") or else V.Text_Is (Data, Key, "readReturned") or else
                         V.Text_Is (Data, Key, "bytes") or else V.Text_Is (Data, Key, "exception"))
                  then return False; end if;
               end;
            end loop;
         end if;
         return True;
      end Cgroup_Read_Shape;
      function Successful_Cgroup_Read (Value : E.Span) return Boolean is
         Raw : constant E.Span := V.Field (Data, Value, "bytes");
         Bytes : constant E.View := E.Decode (Data, Raw, E.Finalization);
         Payload : constant E.View := E.Decode
           (Data, V.Field (Data, Raw, "payload"), E.Finalization);
      begin
         --  The read returned a payload: canonical base64 bytes, no exception.
         if not V.Is_True (Data, Value, "readReturned") or else
           E.Decode (Data, V.Field (Data, Value, "exception"), E.Finalization).Form /= E.Null_Value or else
           Bytes.Form /= E.Object_Value or else E.Array_Length (Data, Bytes.Children) /= 2 or else
           not V.Text_Is (Data, V.Field (Data, Raw, "encoding"), "base64") or else
           Payload.Form /= E.Text_Value or else not E.Bytes_Valid (Data, Payload.Payload)
         then return False; end if;
         declare
            Encoded : constant E.Bytes := E.Materialize (Data, Payload.Payload);
            --  Slide the materialized leaf to a known lower bound so the span
            --  (1, Length) is in range by construction; the bytes are the same.
            Window : constant E.Bytes (1 .. Encoded'Length) := Encoded;
         begin
            return Worldline.Archive_Base64.Canonical (Window, (1, Window'Length));
         end;
      end Successful_Cgroup_Read;
      function Exception_Observation (Item : E.Span) return Boolean is
         Root : constant E.View := E.Decode (Data, Item, E.Finalization);
         Fields : constant E.Count := E.Array_Length (Data, Root.Children);
         Kind_Text : constant E.View := E.Decode
           (Data, V.Field (Data, Item, "exceptionType"), E.Finalization);
         Message : constant E.View := E.Decode
           (Data, V.Field (Data, Item, "exception"), E.Finalization);
         Graph : constant E.View := E.Decode
           (Data, V.Field (Data, Item, "exceptionGraph"), E.Finalization);
      begin
         --  The complete original exception_observation record: schema 1, its
         --  own kind, a named exception type, the message text, a non-empty
         --  causal graph and root 0. A bare type/message pair or a partial
         --  object is not that record.
         if Root.Form /= E.Object_Value or else
           not Small_Integer_Is (V.Field (Data, Item, "schemaVersion"), Zero => False) or else
           not V.Text_Is (Data, V.Field (Data, Item, "kind"), "exception-observation") or else
           Kind_Text.Form /= E.Text_Value or else not V.Truth (Data, Kind_Text.Raw) or else
           Message.Form /= E.Text_Value or else
           Graph.Form /= E.List_Value or else E.Array_Length (Data, Graph.Children) = 0 or else
           not Small_Integer_Is (V.Field (Data, Item, "root"), Zero => True)
         then return False; end if;
         if Fields > 0 then
            for J in E.Count range 0 .. Fields - 1 loop
               declare
                  Pair : constant E.View := E.Decode
                    (Data, E.Array_Element (Data, Root.Children, J), E.Terminal);
                  Key : constant E.View := E.Decode
                    (Data, E.Array_Element (Data, Pair.Children, 0), E.Terminal);
               begin
                  if Pair.Form /= E.List_Value or else E.Array_Length (Data, Pair.Children) /= 2 or else
                    not (V.Text_Is (Data, Key, "schemaVersion") or else V.Text_Is (Data, Key, "kind") or else
                         V.Text_Is (Data, Key, "exceptionType") or else V.Text_Is (Data, Key, "exception") or else
                         V.Text_Is (Data, Key, "exceptionGraph") or else V.Text_Is (Data, Key, "root"))
                  then return False; end if;
               end;
            end loop;
         end if;
         return True;
      end Exception_Observation;
      function Failed_Cgroup_Read (Value : E.Span) return Boolean is
        --  The read returned by raising: no bytes, the complete retained
        --  exception observation. The handle is closed; nothing remains live.
        (V.Is_False (Data, Value, "readReturned") and then
         E.Decode (Data, V.Field (Data, Value, "bytes"), E.Finalization).Form = E.Null_Value and then
         Exception_Observation (V.Field (Data, Value, "exception")));
      function Cgroup_Read_Ended (Value : E.Span) return Boolean is
        (Cgroup_Read_Shape (Value) and then
         (Successful_Cgroup_Read (Value) or else Failed_Cgroup_Read (Value)));
   begin
      if Size > 0 then
         for I in E.Count range 0 .. Size - 1 loop
            declare
               Item : constant E.Span := E.Array_Element (Data, Acquisitions.Children, I);
               Value : constant E.Span := V.Field (Data, Item, "observation");
               Created : constant E.View := E.Decode (Data, V.Field (Data, Value, "processCreatedObserved"), E.Finalization);
            begin
               if V.Text_Is (Data, V.Field (Data, Item, "kind"), "agent-control-acquisition") then
                  if V.Text_Is (Data, V.Field (Data, Value, "site"), "cgroup-read") then
                     if not Cgroup_Read_Ended (Value) then return False; end if;
                  else
                  if Created.Form /= E.Boolean_Value then return False; end if;
                  --  An observed wait carries the actual integer return of
                  --  process.wait(). A null or absent returncode beside a
                  --  claimed wait is absence, never an observed exit.
                  if Created.Boolean_Bit and then
                    (not V.Is_True (Data, Value, "processWaitReturnObserved") or else
                     E.Decode (Data, V.Field (Data, Value, "processWaitReturncode"), E.Finalization).Form /= E.Integer_Value or else
                     not V.Is_True (Data, Value, "stdoutReachedEof") or else
                     not V.Is_True (Data, Value, "stderrReachedEof")) then return False; end if;
                  end if;
               end if;
            end;
         end loop;
      end if;
      return True;
   end Controls_Ended;
   function Closed
     (Subject_Data, Owners_Data, Acquisition_Data : E.Bytes;
      Subject, Owners, Raw_Acquisitions : E.Span) return Boolean is
      Owner_List : constant E.View := E.Decode (Owners_Data, Owners, E.Finalization);
      Acquisitions : constant E.View := E.Decode (Acquisition_Data, Raw_Acquisitions, E.Finalization);
      Size : constant E.Count := E.Array_Length (Owners_Data, Owner_List.Children);
   begin
      if E.Decode (Subject_Data, Subject, E.Finalization).Form = E.Invalid or else
        Owner_List.Form /= E.List_Value or else Acquisitions.Form /= E.List_Value or else
        not Controls_Ended (Acquisition_Data, Acquisitions) then return False; end if;
      if Size > 0 then
         for I in E.Count range 0 .. Size - 1 loop
            if not Owner_Closed (Subject_Data, Owners_Data, Acquisition_Data, Subject,
              E.Array_Element (Owners_Data, Owner_List.Children, I), Acquisitions) then return False; end if;
         end loop;
      end if;
      return True;
   end Closed;
end Worldline.Runner_Acquisition_Bytes;
