with Interfaces;
with Worldline.Producer_Values;
with Worldline.Producer_Bytes;
with Worldline.Confinement_Filter;
package body Worldline.Report_Custody_Native with SPARK_Mode is
   package V renames Worldline.Producer_Values;
   package B renames Worldline.Producer_Bytes;
   package W renames Worldline.Evaluation_Wire;
   package R renames Worldline.Evaluation_Report_Facts;
   subtype U64 is Interfaces.Unsigned_64;
   subtype I64 is Interfaces.Integer_64;
   use type V.Value_Kind;
   use type W.Byte;
   use type R.Confinement_Observation;
   use type U64;
   use type I64;
   function Complete_Observation (Expected, Acquired, Result_Record : String; Data_Artifact : Boolean)
      return R.Confinement_Observation is
      Data : String renames Result_Record;
      Root : constant V.Node := V.Parse (Data);
      Start : constant V.Node := V.Parse (Expected);
      Acquisitions : constant V.Node := V.Parse (Acquired);
      function F (Item : V.Node; Name : String) return V.Node is (V.Field (Data, Item, Name));
      function S (Item : V.Node; Name : String) return String is (V.Text (Data, F (Item, Name)));
      function N (Item : V.Node; Name : String) return String is (V.Decimal (Data, F (Item, Name)));
      function E (Item : V.Node; Index : Positive) return V.Node is (V.Element (Data, Item, Index));
      function Same (L, Right : V.Node) return Boolean is (V.Equal (Data, L, Data, Right));
      function True_Field (Item : V.Node; Name : String) return Boolean is (V.Is_True (Data, F (Item, Name)));
      function Positive_Integer (Item : V.Node) return Boolean is
        (V.Nonnegative (Data, Item) and then V.Decimal (Data, Item) not in "0" | "-0");
      function FD (Item : V.Node) return Boolean is (V.Nonnegative (Data, Item));
      function Image (Value : Natural) return String is
         Text : constant String := Natural'Image (Value);
      begin return Text (Text'First + 1 .. Text'Last); end Image;
      function Unsigned_Image (Value : U64) return String is
         Text : constant String := U64'Image (Value);
      begin return Text (Text'First + 1 .. Text'Last); end Unsigned_Image;
      function Signed_Image (Value : U64) return String is
         Signed : constant I64 := (if Value < 2 ** 63 then I64 (Value)
                                  else I64 (Value - 2 ** 63) + I64'First);
         Text : constant String := I64'Image (Signed);
      begin return (if Text (Text'First) = ' ' then Text (Text'First + 1 .. Text'Last) else Text); end Signed_Image;
      function Modulo (Value : String; Modulus : Positive) return Natural is
         Remainder : Natural := 0;
      begin
         for C of Value loop
            if C not in '0' .. '9' then return Modulus; end if;
            Remainder := (Remainder * 10 + Character'Pos (C) - 48) mod Modulus;
         end loop;
         return Remainder;
      end Modulo;
      function Byte_Leaf (Item : V.Node) return B.Decoded is
      begin
         if not V.Is_Text (Data, F (Item, "encoding"), "base64") or else
           F (Item, "payload").Form /= V.String_Value then return (0, False, ""); end if;
         return B.Base64 (S (Item, "payload"));
      end Byte_Leaf;
      function Object (Item : V.Node; File_Type : Natural) return Boolean is
        (Item.Form = V.Object_Value and then V.Nonnegative (Data, F (Item, "device")) and then
         Positive_Integer (F (Item, "inode")) and then V.Nonnegative (Data, F (Item, "mode")) and then
         Modulo (N (Item, "mode"), 65_536) / 4096 = File_Type and then
         V.Nonnegative (Data, F (Item, "uid")) and then V.Nonnegative (Data, F (Item, "gid")));
      function Stable (Before, After : V.Node; Count : Positive := 9) return Boolean is
      begin
         if Before.Form /= V.Object_Value or else After.Form /= V.Object_Value then return False; end if;
         for I in 1 .. Count loop
            declare
               Key : constant String := (case I is when 1 => "device", when 2 => "inode", when 3 => "mode",
                 when 4 => "uid", when 5 => "gid", when 6 => "size", when 7 => "mtime_ns", when 8 => "ctime_ns", when others => "nlink");
            begin
               if F (Before, Key).Form /= V.Integer_Value or else
                 not Same (F (Before, Key), F (After, Key)) then return False; end if;
            end;
         end loop;
         return True;
      end Stable;
      Capture : constant V.Node := F (Root, "protectedProviderCapture");
      Planned : constant V.Node := F (Capture, "expected");
      Actual : constant V.Node := F (Capture, "observed");
      Report : constant V.Node := F (Capture, "report");
      Sealed : constant V.Node := F (Report, "sealed");
      Transfer : constant V.Node := F (Capture, "reportTransfer");
      Roles : constant V.Node := F (Capture, "roles");
      Lifetime : constant V.Node := F (Capture, "lifetime");
      Operations : constant V.Node := F (Capture, "operations");
      Leases : constant V.Node := F (Capture, "sourceLeases");
      Directories : constant V.Node := F (Capture, "sourceDirectories");
      Boundary : constant V.Node := F (Root, (if Data_Artifact then "boundary" else "evaluatorBoundary"));
      Starts : constant V.Node := F (Boundary, "daemonRoleObservations");
      function Returned (Item : V.Node) return Boolean is (N (Item, "return") = "0" and then N (Item, "errno") = "0");
      function Empty_Array (Item : V.Node) return Boolean is (Item.Form = V.Array_Value and then V.Count (Data, Item) = 0);
      function Closed (Descriptor : V.Node) return Boolean is
         Seen : Boolean := False;
         Rows : constant V.Node := F (Lifetime, "closes");
      begin
         if not FD (Descriptor) or else Rows.Form /= V.Array_Value then return False; end if;
         for I in 1 .. V.Count (Data, Rows) loop
            declare Item : constant V.Node := E (Rows, I);
            begin
               if Same (F (Item, "fd"), Descriptor) then
                  if Seen or else not Returned (Item) then return False; end if;
                  Seen := True;
               end if;
            end;
         end loop;
         return Seen;
      end Closed;
      function Operation (Name : String; Descriptor : V.Node; Opened : Boolean := False;
                          Waited : Boolean := False) return Boolean is
         Seen : Boolean := False;
      begin
         if not FD (Descriptor) or else Operations.Form /= V.Array_Value then return False; end if;
         for I in 1 .. V.Count (Data, Operations) loop
            declare Item : constant V.Node := E (Operations, I);
            begin
               if S (Item, "operation") = Name and then Same (F (Item, "fd"), Descriptor) then
                  if Seen or else N (Item, "errno") /= "0" or else
                    (if Waited then not Positive_Integer (F (Item, "return"))
                     elsif Opened then not Same (F (Item, "return"), Descriptor)
                     else N (Item, "return") /= "0") then return False; end if;
                  Seen := True;
               end if;
            end;
         end loop;
         return Seen;
      end Operation;
      function Stat_Seen (Descriptor, Snapshot : V.Node; Minimum : Positive := 1;
                          Edge : Boolean := False) return Boolean is
         Count : Natural := 0;
      begin
         if not FD (Descriptor) or else Snapshot.Form /= V.Object_Value or else Operations.Form /= V.Array_Value then return False; end if;
         for I in 1 .. V.Count (Data, Operations) loop
            declare Item : constant V.Node := E (Operations, I);
            begin
               if S (Item, "operation") = (if Edge then "statEdge" else "fstat") and then
                 Same (F (Item, "fd"), Descriptor) and then Returned (Item) and then
                 Same (F (Item, "apiReturn"), Snapshot) then Count := Count + 1; end if;
            end;
         end loop;
         return Count >= Minimum;
      end Stat_Seen;
      function Reads_Match (Reads, Descriptor : V.Node; Content : B.Decoded) return Boolean is
         Offset : Natural := 0;
         EOF : Boolean := False;
      begin
         if not FD (Descriptor) or else not Content.Valid or else Reads.Form /= V.Array_Value or else V.Count (Data, Reads) = 0 then return False; end if;
         for I in 1 .. V.Count (Data, Reads) loop
            declare Item : constant V.Node := E (Reads, I); Chunk : constant B.Decoded := Byte_Leaf (F (Item, "bytes"));
            begin
               if EOF or else not Same (F (Item, "fd"), Descriptor) or else not Chunk.Valid or else N (Item, "errno") /= "0" or else
                 N (Item, "offset") /= Image (Offset) or else N (Item, "return") /= Image (Chunk.Length) or else
                 Chunk.Length > Content.Length - Offset or else
                 Chunk.Data /= Content.Data (Offset + 1 .. Offset + Chunk.Length) then return False; end if;
               Offset := Offset + Chunk.Length;
               EOF := Chunk.Length = 0;
            end;
         end loop;
         return EOF and then Offset = Content.Length;
      end Reads_Match;
      function Lease_Metadata (Item : V.Node; Length : Natural) return Boolean is
      begin
         return Item.Form = V.Object_Value and then Object (F (Item, "before"), 8) and then
           N (F (Item, "before"), "nlink") = "1" and then
           Stable (F (Item, "before"), F (Item, "after")) and then
           Stable (F (Item, "before"), F (Item, "edgeAfter")) and then
           N (Item, "acquireReturn") = "0" and then N (Item, "acquireErrno") = "0" and then
           N (Item, "getReturn") = "0" and then N (Item, "getErrno") = "0" and then
           N (Item, "releaseReturn") = "0" and then N (Item, "releaseErrno") = "0" and then
           N (F (Item, "before"), "size") = Image (Length) and then
           Stat_Seen (F (Item, "fd"), F (Item, "before"), Minimum => 2) and then
           Stat_Seen (F (Item, "parentFd"), F (Item, "edgeAfter"), Edge => True) and then
           Closed (F (Item, "fd"));
      end Lease_Metadata;
      function Lease (Item : V.Node) return Boolean is
         Bytes : constant B.Decoded := Byte_Leaf (F (Item, "bytes"));
      begin
         return Bytes.Valid and then Lease_Metadata (Item, Bytes.Length) and then
           Reads_Match (F (Item, "reads"), F (Item, "fd"), Bytes);
      end Lease;
      function Pidfd_Matches (Role : V.Node) return Boolean is
         Info : constant V.Node := F (Role, "pidfdInfo");
         Content : constant B.Decoded := Byte_Leaf (F (Info, "bytes"));
         PID : constant String := N (F (Role, "identity"), "pid");
         function Line (Name : String; More : Boolean) return Boolean is
            Prefix : constant String := Name & Character'Val (9) & PID;
         begin
            if not Content.Valid or else Content.Length < Prefix'Length + 1 then return False; end if;
            for I in 1 .. Content.Length - Prefix'Length loop
               if (I = 1 or else Content.Data (I - 1) = Character'Val (10)) and then
                 Content.Data (I .. I + Prefix'Length - 1) = Prefix and then
                 (Content.Data (I + Prefix'Length) = Character'Val (10) or else
                  (More and then Content.Data (I + Prefix'Length) = Character'Val (9))) then
                  return True;
               end if;
            end loop;
            return False;
         end Line;
      begin
         return Positive_Integer (F (F (Role, "identity"), "pid")) and then
           Stable (F (Role, "pidfdSourceObject"), F (Role, "pidfdObject")) and then
           Stat_Seen (F (Role, "pidfdSource"), F (Role, "pidfdSourceObject")) and then
           Stat_Seen (F (Role, "pidfd"), F (Role, "pidfdObject")) and then
           Same (F (Info, "subjectFd"), F (Role, "pidfd")) and then
           Operation ("duplicateRolePidfd", F (Role, "pidfd"), Opened => True) and then
           Operation ("openRolePidfdInfo", F (Info, "fd"), Opened => True) and then
           Reads_Match (F (Info, "reads"), F (Info, "fd"), Content) and then Closed (F (Info, "fd")) and then
           Line ("Pid:", False) and then Line ("NSpid:", True);
      end Pidfd_Matches;
      function Peer_Matches (Peer, Role : V.Node) return Boolean is
         Original : constant V.Node := F (Role, "peerCredentials");
      begin
         if Peer.Form = V.Object_Value then return Same (Peer, Original); end if;
         return Peer.Form = V.Array_Value and then V.Count (Data, Peer) = 3 and then
           Same (E (Peer, 1), F (Original, "pid")) and then Same (E (Peer, 2), F (Original, "uid")) and then
           Same (E (Peer, 3), F (Original, "gid"));
      end Peer_Matches;
      function Startup_Matches (Role : V.Node) return Boolean is
         Found : Boolean := False;
      begin
         if Starts.Form /= V.Array_Value or else not V.Nonempty_Text (Data, F (Role, "recordId")) then return False; end if;
         for I in 1 .. V.Count (Data, Starts) loop
            declare Item : constant V.Node := E (Starts, I);
            begin
               if Same (F (Item, "recordId"), F (Role, "recordId")) then
                  if Found or else not Same (F (Role, "startup"), Item) then return False; end if;
                  Found := True;
               end if;
            end;
         end loop;
         return Found;
      end Startup_Matches;
      function Death (Descriptor : V.Node) return Boolean is
         Rows : constant V.Node := F (Lifetime, "deathPolls");
         Found : Boolean := False;
      begin
         if Rows.Form /= V.Array_Value then return False; end if;
         for I in 1 .. V.Count (Data, Rows) loop
            declare Item : constant V.Node := E (Rows, I); Events : constant V.Node := F (Item, "events");
            begin
               if Same (F (Item, "pidfd"), Descriptor) then
                  if Found or else N (Item, "errno") /= "0" or else N (Item, "return") /= "1" or else
                    Events.Form /= V.Array_Value or else V.Count (Data, Events) /= 1 or else
                    not Same (F (E (Events, 1), "fd"), Descriptor) or else
                    Modulo (N (E (Events, 1), "revents"), 2) /= 1 then return False; end if;
                  Found := True;
               end if;
            end;
         end loop;
         return Found;
      end Death;
      function Original_Wait (Item, Role : V.Node) return Boolean is
         Borrows : constant V.Node := F (F (Boundary, "namespaceLifetimeSetup"), "roleBorrows");
         Found : Boolean := False;
      begin
         if Borrows.Form /= V.Array_Value then return False; end if;
         for I in 1 .. V.Count (Data, Borrows) loop
            declare Borrow : constant V.Node := E (Borrows, I);
            begin
               if Same (F (Borrow, "kernelObservationId"), F (Role, "recordId")) then
                  if Found or else not Same (Borrow, F (Item, "originalBorrow")) then return False; end if;
                  Found := True;
               end if;
            end;
         end loop;
         return Found;
      end Original_Wait;
      function Wait_Matches (Role : V.Node) return Boolean is
         Rows : constant V.Node := F (Lifetime, "waits");
         Found : Boolean := False;
      begin
         if Rows.Form /= V.Array_Value then return False; end if;
         for I in 1 .. V.Count (Data, Rows) loop
            declare Item : constant V.Node := E (Rows, I); Attempts : constant V.Node := F (Item, "waitAttempts"); Seen : Boolean := False;
            begin
               if Same (F (Item, "pidfd"), F (Role, "pidfd")) then
                  if Found or else not Same (F (Item, "kernelObservationId"), F (Role, "recordId")) or else
                    S (Item, "waitScope") /= "owned-role-launcher-child" or else not True_Field (Item, "waitReturned") or else
                    not Positive_Integer (F (Item, "pid")) or else not Same (F (Item, "return"), F (Item, "pid")) or else
                    N (Item, "errno") /= "0" or else not V.Nonnegative (Data, F (Item, "rawWaitStatus")) or else
                    Modulo (N (Item, "rawWaitStatus"), 256) /= 0 or else Attempts.Form /= V.Array_Value then return False; end if;
                  if not Original_Wait (Item, Role) then return False; end if;
                  for J in 1 .. V.Count (Data, Attempts) loop
                     declare Attempt : constant V.Node := E (Attempts, J);
                     begin
                        if True_Field (Attempt, "returned") and then Same (F (Attempt, "returnedPid"), F (Item, "pid")) and then
                          Same (F (Attempt, "rawStatus"), F (Item, "rawWaitStatus")) and then
                          (F (Attempt, "errno").Form = V.Null_Value or else N (Attempt, "errno") = "0") then Seen := True; end if;
                     end;
                  end loop;
                  if not Seen then return False; end if;
                  Found := True;
               end if;
            end;
         end loop;
         return Found and then Death (F (Role, "pidfd")) and then Closed (F (Role, "pidfd"));
      end Wait_Matches;
      function Namespace_Matches (Role : V.Node) return Boolean is
         Held : constant V.Node := F (Role, "namespaceFds");
         Observed : constant V.Node := F (Role, "namespaces");
      begin
         if Held.Form /= V.Array_Value or else V.Count (Data, Held) /= 6 or else Observed.Form /= V.Array_Value then return False; end if;
         for I in 1 .. 6 loop
            declare Item : constant V.Node := E (Held, I); Found : Boolean := False;
            begin
               if not Stable (F (Item, "before"), F (Item, "after")) or else
                 not Stat_Seen (F (Item, "fd"), F (Item, "before"), Minimum => 2) or else
                 not Operation ("duplicateRoleNamespace", F (Item, "fd"), Opened => True) or else
                 N (Item, "closeReturn") /= "0" or else N (Item, "closeErrno") /= "0" or else
                 not Closed (F (Item, "fd")) then return False; end if;
               for J in 1 .. V.Count (Data, Observed) loop
                  declare Row : constant V.Node := E (Observed, J);
                  begin
                     if S (Item, "name") = S (Row, "name") and then
                       Same (F (Row, "subject"), F (F (Role, "identity"), "pid")) then
                        if Found or else not Stable (F (Item, "before"), F (Row, "object"), 8) or else
                          not True_Field (Row, "returned") then return False; end if;
                        Found := True;
                     end if;
                  end;
               end loop;
               if not Found then return False; end if;
               for J in 1 .. I - 1 loop
                  if S (E (Held, J), "name") = S (Item, "name") or else
                    Same (F (E (Held, J), "fd"), F (Item, "fd")) then return False; end if;
               end loop;
            end;
         end loop;
         return True;
      end Namespace_Matches;
      function Word (Payload : String; Offset : Natural) return U64 is
         Value : U64 := 0;
      begin
         if Offset > Payload'Length or else Payload'Length - Offset < 8 then return 0; end if;
         for I in 0 .. 7 loop Value := Value or Interfaces.Shift_Left (U64 (Character'Pos (Payload (Payload'First + Offset + I))), I * 8); end loop;
         return Value;
      end Word;
      function Time_Image (Seconds, Nanoseconds : U64) return String is
         Negative : constant Boolean := Seconds >= 2 ** 63;
         Absolute : constant U64 := (if Negative then 0 - Seconds else Seconds);
         Upper : constant U64 := (if Negative and Nanoseconds /= 0 then Absolute - 1 else Absolute);
         Lower : constant U64 := (if Negative and Nanoseconds /= 0 then 1_000_000_000 - Nanoseconds else Nanoseconds);
         Lower_Text : constant String := Unsigned_Image (Lower);
         Padding : String (1 .. 9) := (others => '0');
      begin
         if Nanoseconds >= 1_000_000_000 or else Lower_Text'Length > 9 then return ""; end if;
         Padding (10 - Lower_Text'Length .. 9) := Lower_Text;
         if Upper /= 0 then return (if Negative then "-" else "") & Unsigned_Image (Upper) & Padding; end if;
         for I in Padding'Range loop
            if Padding (I) /= '0' then return (if Negative then "-" else "") & Padding (I .. Padding'Last); end if;
         end loop;
         return "0";
      end Time_Image;
      function Native_Transfer (Examiner : V.Node) return Boolean is
         Payload : constant B.Decoded := Byte_Leaf (F (Transfer, "payload"));
         Native : constant V.Node := F (Transfer, "nativeBefore");
         Daemon : constant V.Node := F (Transfer, "daemonBefore");
         Closing : constant B.Decoded := Byte_Leaf (F (F (Transfer, "nativeClose"), "bytes"));
         Reads : constant V.Node := F (Lifetime, "channelReads");
         Count : Natural := 0;
      begin
         if S (Transfer, "schema") /= "worldline-native-report-fd-transfer-v1" or else
           not Payload.Valid or else Payload.Length /= 128 or else Payload.Data (1 .. 8) /= "WLPRv001" or else
           not Same (F (Transfer, "fd"), F (Report, "fd")) or else
           not Peer_Matches (F (Transfer, "peerCredentials"), Examiner) or else
           not Closed (F (Transfer, "peerPidfd")) or else not True_Field (Transfer, "readEOF") or else
           F (Transfer, "exception").Form /= V.Null_Value or else
           not Returned (F (Transfer, "nativeClose")) or else
           N (Transfer, "nativeOpenReturn") /= Signed_Image (Word (Payload.Data, 96)) or else
           not FD (F (Transfer, "nativeOpenReturn")) or else
           N (Transfer, "nativeOpenErrno") /= "0" or else Word (Payload.Data, 104) /= 0 or else
           N (Transfer, "nativeFstatReturn") /= "0" or else Word (Payload.Data, 112) /= 0 or else
           N (Transfer, "nativeFstatErrno") /= "0" or else Word (Payload.Data, 120) /= 0 or else
           N (F (Transfer, "ack"), "return") /= "4" or else N (F (Transfer, "ack"), "errno") /= "0" then return False; end if;
         declare Ack : constant B.Decoded := Byte_Leaf (F (F (Transfer, "ack"), "bytes"));
         begin if not Ack.Valid or else Ack.Data /= "WLPA" then return False; end if; end;
         if not Closing.Valid or else Closing.Length /= 24 or else Closing.Data (1 .. 8) /= "WLPCv001" or else
           Word (Closing.Data, 8) /= 0 or else Word (Closing.Data, 16) /= 0 or else
           S (Transfer, "channelId") = "" or else Reads.Form /= V.Array_Value then return False; end if;
         for I in 1 .. V.Count (Data, Reads) loop
            declare Item : constant V.Node := E (Reads, I);
               Bytes : constant B.Decoded := Byte_Leaf (F (Item, "bytes"));
            begin
               if Same (F (Item, "channelId"), F (Transfer, "channelId")) then
                  Count := Count + 1;
                  if not Bytes.Valid or else not Peer_Matches (F (Item, "peerCredentials"), Examiner) or else
                    S (Item, "scope") /= "native-original-report-transfer" or else
                    N (Item, "errno") /= "0" or else N (Item, "return") /= Image (Bytes.Length) or else
                    (case Count is when 1 => Bytes.Data /= Payload.Data,
                     when 2 => Bytes.Data /= Closing.Data, when 3 => Bytes.Length /= 0, when others => True) then
                     return False;
                  end if;
               end if;
            end;
         end loop;
         if Count /= 3 then return False; end if;
         for I in 0 .. 5 loop
            declare Key : constant String := (case I is when 0 => "device", when 1 => "inode", when 2 => "mode",
                                              when 3 => "uid", when 4 => "gid", when others => "size");
            begin
               if N (Native, Key) /= Unsigned_Image (Word (Payload.Data, 8 + I * 8)) then return False; end if;
            end;
         end loop;
         if Word (Payload.Data, 64) >= 1_000_000_000 or else Word (Payload.Data, 80) >= 1_000_000_000 or else
           N (Native, "mtime_ns") /= Time_Image (Word (Payload.Data, 56), Word (Payload.Data, 64)) or else
           N (Native, "ctime_ns") /= Time_Image (Word (Payload.Data, 72), Word (Payload.Data, 80)) or else
           N (Native, "nlink") /= Unsigned_Image (Word (Payload.Data, 88)) or else
           N (Native, "uid") /= "0" or else N (Native, "gid") /= "0" or else
           not Same (F (Daemon, "uid"), F (F (Examiner, "peerCredentials"), "uid")) or else
           not Same (F (Daemon, "gid"), F (F (Examiner, "peerCredentials"), "gid")) or else
           not Stable (Daemon, F (Report, "before")) then return False; end if;
         for I in 1 .. 7 loop
            declare Key : constant String := (case I is when 1 => "device", when 2 => "inode", when 3 => "mode",
                                              when 4 => "size", when 5 => "mtime_ns", when 6 => "ctime_ns", when others => "nlink");
            begin if not Same (F (Native, Key), F (Daemon, Key)) then return False; end if; end;
         end loop;
         return True;
      end Native_Transfer;
      function Channels_Match (Examiner : V.Node) return Boolean is
         Rows : constant V.Node := F (Lifetime, "channelReads");
         Shutdowns : constant V.Node := F (Lifetime, "shutdowns");
         Closes : constant V.Node := F (Lifetime, "channelCloses");
         Saw_Examiner : Boolean := False;
      begin
         if Rows.Form /= V.Array_Value or else V.Count (Data, Rows) = 0 or else Shutdowns.Form /= V.Array_Value or else
           Closes.Form /= V.Array_Value then return False; end if;
         for I in 1 .. V.Count (Data, Rows) loop
            declare Item : constant V.Node := E (Rows, I); Bytes : constant B.Decoded := Byte_Leaf (F (Item, "bytes"));
                    EOF : Boolean := False; Shut : Boolean := False; Close : Boolean := False; Duplicated : Boolean := False;
            begin
               if not FD (F (Item, "fd")) or else not Bytes.Valid or else N (Item, "errno") /= "0" or else
                 N (Item, "return") /= Image (Bytes.Length) or else not V.Nonempty_Text (Data, F (Item, "channelId")) then return False; end if;
               for J in 1 .. I - 1 loop
                  declare Before : constant V.Node := E (Rows, J);
                  begin
                     if Same (F (Before, "channelId"), F (Item, "channelId")) and then N (Before, "return") = "0" then return False; end if;
                  end;
               end loop;
               for J in I .. V.Count (Data, Rows) loop
                  declare Later : constant V.Node := E (Rows, J);
                  begin
                     if Same (F (Later, "channelId"), F (Item, "channelId")) then
                        if not Same (F (Later, "fd"), F (Item, "fd")) or else
                          not Same (F (Later, "originalFd"), F (Item, "originalFd")) then return False; end if;
                        if N (Later, "return") = "0" then EOF := True; end if;
                     end if;
                  end;
               end loop;
               for J in 1 .. V.Count (Data, Operations) loop
                  declare Op : constant V.Node := E (Operations, J);
                  begin
                     if S (Op, "operation") = "duplicateChannel" and then Same (F (Op, "channelId"), F (Item, "channelId")) then
                        if Duplicated or else N (Op, "errno") /= "0" or else not Same (F (Op, "return"), F (Item, "fd")) or else
                          not Same (F (Op, "originalFd"), F (Item, "originalFd")) then return False; end if;
                        Duplicated := True;
                     end if;
                  end;
               end loop;
               for J in 1 .. V.Count (Data, Closes) loop
                  declare Op : constant V.Node := E (Closes, J);
                  begin
                     if Same (F (Op, "channelId"), F (Item, "channelId")) then
                        if Close or else not Returned (Op) or else not Same (F (Op, "fd"), F (Item, "fd")) then return False; end if;
                        Close := True;
                     end if;
                  end;
               end loop;
               if not EOF or else not Close or else not Duplicated or else not Closed (F (Item, "fd")) then return False; end if;
               if Same (F (Item, "startupRecordId"), F (Examiner, "recordId")) then
                  if not Peer_Matches (F (Item, "peerCredentials"), Examiner) then return False; end if;
                  for J in 1 .. V.Count (Data, Shutdowns) loop
                     declare Op : constant V.Node := E (Shutdowns, J);
                     begin
                        if Same (F (Op, "channelId"), F (Item, "channelId")) then
                           if Shut or else not Returned (Op) or else not Same (F (Op, "fd"), F (Item, "fd")) then return False; end if;
                           Shut := True;
                        end if;
                     end;
                  end loop;
                  if not Shut then return False; end if;
                  Saw_Examiner := True;
               end if;
            end;
         end loop;
         return Saw_Examiner;
      end Channels_Match;
      Report_Bytes : constant B.Decoded := (if Data_Artifact then Byte_Leaf (F (Sealed, "bytes")) else
        B.Base64 (S (F (Root, "privateReport"), "payloadB64")));
      Sealed_Bytes : constant B.Decoded := (if Data_Artifact then B.Base64 ("") else Byte_Leaf (F (Sealed, "bytes")));
      Examiner : V.Node := V.No_Node;
      Examiner_Count : Natural := 0;
   begin
      if Capture.Form in V.Missing | V.Null_Value then return R.Confinement_Unmeasured; end if;
      if Capture.Form /= V.Object_Value or else S (Capture, "schema") /= "worldline-protected-report-capture-v1" or else
        Planned.Form /= V.Object_Value or else Actual.Form /= V.Object_Value or else Start.Form /= V.Object_Value or else
        (not Data_Artifact and then Report_Bytes.Length > 10_000_000) then
         return R.Confinement_Not_Established;
      end if;
      declare
         Captured : Boolean := False;
         Returned_Capture : Boolean := False;
      begin
         if Acquisitions.Form /= V.Array_Value then return R.Confinement_Not_Established; end if;
         for I in 1 .. V.Count (Acquired, Acquisitions) loop
            declare
               Item : constant V.Node := V.Element (Acquired, Acquisitions, I);
               Kind : constant String := V.Text (Acquired, V.Field (Acquired, Item, "kind"));
               Observation : constant V.Node := V.Field (Acquired, Item, "observation");
            begin
               if Kind = "private-protected-provider-capture" then
                  if Captured or else not V.Equal (Acquired, Observation, Data, Capture) then return R.Confinement_Not_Established; end if;
                  Captured := True;
               elsif Kind = "private-process-return" then
                  if Returned_Capture or else not V.Equal (Acquired,
                    V.Field (Acquired, Observation, "protectedProviderCapture"), Data, Capture) then return R.Confinement_Not_Established; end if;
                  Returned_Capture := True;
               end if;
            end;
         end loop;
         if not Captured or else not Returned_Capture then return R.Confinement_Not_Established; end if;
      end;
      if not V.Equal (Expected, Start, Data, F (Planned, "invocation")) or else
        not Same (F (Planned, "invocation"), F (Actual, "invocation")) or else
        not Same (F (Planned, "sourceRoster"), F (Actual, "sourceRoster")) or else
        not Same (F (Planned, "sourceRoster"), F (F (F (Root, "examinerAudit"), "before"), "files")) or else
        not Same (F (Actual, "sourceRoster"), F (F (F (Root, "examinerAudit"), "after"), "files")) or else
        not Same (F (Planned, "filterProgramB64"), F (Actual, "filterProgramB64")) or else
        not Worldline.Confinement_Filter.Establishes (S (Actual, "filterProgramB64")) or else
        not Same (F (F (Capture, "filterInstallation"), "programB64"), F (Actual, "filterProgramB64")) or else
        N (F (Capture, "filterInstallation"), "seccompResult") /= "0" or else
        N (F (Capture, "filterInstallation"), "seccompErrno") /= "0" or else
        N (F (Capture, "filterInstallation"), "seccompOperation") /= "1" or else
        N (F (Capture, "filterInstallation"), "seccompFlags") /= "1" or else
        N (F (Capture, "filterInstallation"), "noNewPrivs") /= "1" or else
        N (F (Capture, "filterInstallation"), "noNewPrivsErrno") /= "0" or else
        not Object (F (Planned, "reportDirectory"), 4) or else
        not Same (F (Planned, "reportDirectory"), F (Actual, "reportDirectory")) or else
        Modulo (N (F (Actual, "reportDirectory"), "mode"), 512) mod 64 /= 0 or else
        not Object (F (Report, "before"), 8) or else N (F (Report, "before"), "nlink") /= "1" or else
        not Stable (F (Report, "before"), F (Report, "after")) or else
        not Stable (F (Report, "before"), F (Report, "edgeAfter")) or else
        not Object (F (Sealed, "before"), 8) or else not Stable (F (Sealed, "before"), F (Sealed, "after")) or else
        not Report_Bytes.Valid or else (not Data_Artifact and then
          (not Sealed_Bytes.Valid or else Report_Bytes.Data /= Sealed_Bytes.Data)) or else
        N (F (Report, "after"), "size") /= Image (Report_Bytes.Length) or else
        N (F (Sealed, "after"), "size") /= Image (Report_Bytes.Length) or else
        N (Sealed, "addSealReturn") /= "0" or else N (Sealed, "addSealErrno") /= "0" or else
        N (Sealed, "sealErrno") /= "0" or else Modulo (N (Sealed, "sealGetReturn"), 16) /= 15 or else
        not Reads_Match (F (Report, "reads"), F (Report, "fd"), Report_Bytes) or else
        not Reads_Match (F (Sealed, "reads"), F (Sealed, "fd"), Report_Bytes) or else
        not Lease_Metadata (F (Report, "writerLease"), Report_Bytes.Length) or else
        not Same (F (F (Report, "writerLease"), "reads"), F (Report, "reads")) or else
        not Same (F (F (Report, "writerLease"), "fd"), F (Report, "fd")) or else
        not Same (F (F (Report, "writerLease"), "bytes"), F (Sealed, "bytes")) or else
        not Empty_Array (F (Lifetime, "pendingOperations")) or else not Empty_Array (F (Lifetime, "failures")) or else
        not Empty_Array (F (Capture, "sourceLeaseBreaks")) or else Roles.Form /= V.Array_Value or else V.Count (Data, Roles) = 0 or else
        Leases.Form /= V.Array_Value or else V.Count (Data, Leases) = 0 or else Directories.Form /= V.Array_Value or else
        V.Count (Data, Directories) = 0 then return R.Confinement_Not_Established; end if;
      for I in 1 .. V.Count (Data, Roles) loop
         declare Role : constant V.Node := E (Roles, I);
         begin
            if not Startup_Matches (Role) or else not Pidfd_Matches (Role) or else
              not Wait_Matches (Role) or else not Namespace_Matches (Role) then return R.Confinement_Not_Established; end if;
            if S (Role, "roleClaim") = "examiner" then Examiner := Role; Examiner_Count := Examiner_Count + 1;
            elsif S (Role, "roleClaim") not in "worker" | "candidate" then return R.Confinement_Not_Established; end if;
            for J in 1 .. I - 1 loop
               if Same (F (E (Roles, J), "recordId"), F (Role, "recordId")) or else
                 Same (F (E (Roles, J), "pidfd"), F (Role, "pidfd")) then return R.Confinement_Not_Established; end if;
            end loop;
         end;
      end loop;
      declare Count : Natural := 0;
      begin
         for I in 1 .. V.Count (Data, Starts) loop
            if S (E (Starts, I), "kind") = "role-startup" then Count := Count + 1; end if;
         end loop;
         if Count /= V.Count (Data, Roles) then return R.Confinement_Not_Established; end if;
      end;
      if Examiner_Count /= 1 or else not Native_Transfer (Examiner) or else not Channels_Match (Examiner) or else
        not Operation ("installFilter", F (Examiner, "pidfd")) or else
        not Operation ("waitWriter", F (Examiner, "pidfd"), Waited => True) or else
        not Operation ("openReportDirectory", F (Report, "directoryFd"), Opened => True) or else
        not Stat_Seen (F (Report, "directoryFd"), F (Planned, "reportDirectory"), Minimum => 2) or else
        not Stat_Seen (F (Report, "fd"), F (Report, "before"), Minimum => 2) or else
        not Stat_Seen (F (Sealed, "fd"), F (Sealed, "before"), Minimum => 2) or else
        not Operation ("acquireLease", F (Report, "directoryFd")) or else
        not Operation ("acquireWriterLease", F (Report, "fd")) or else
        not Operation ("sealReport", F (Sealed, "fd")) or else
        not Closed (F (Report, "directoryFd")) or else not Closed (F (Report, "fd")) or else
        not Closed (F (Sealed, "fd")) then return R.Confinement_Not_Established; end if;
      declare Mounts : constant V.Node := F (Examiner, "mountObjects"); Seen : Boolean := False;
      begin
         if Mounts.Form /= V.Array_Value then return R.Confinement_Not_Established; end if;
         for I in 1 .. V.Count (Data, Mounts) loop
            declare Item : constant V.Node := E (Mounts, I);
            begin
               if S (Item, "target") = "/run/worldline-report" then
                  if Seen or else not Stable (F (Planned, "reportDirectory"), F (Item, "source"), 5) or else
                    not Stable (F (Planned, "reportDirectory"), F (Item, "effective"), 5) then
                     return R.Confinement_Not_Established;
                  end if;
                  Seen := True;
               end if;
            end;
         end loop;
         if not Seen then return R.Confinement_Not_Established; end if;
      end;
      for I in 1 .. V.Count (Data, Directories) loop
         declare Item : constant V.Node := E (Directories, I);
         begin
            if not FD (F (Item, "fd")) or else not Same (F (Item, "openReturn"), F (Item, "fd")) or else
              N (Item, "openErrno") /= "0" or else not Object (F (Item, "before"), 4) or else
              not Stable (F (Item, "before"), F (Item, "after"), 5) or else
              (F (Item, "parentFd").Form = V.Null_Value and then
               (S (Item, "component") /= "/" or else F (Item, "edgeAfter").Form /= V.Null_Value)) or else
              (F (Item, "parentFd").Form /= V.Null_Value and then
               (not Stable (F (Item, "before"), F (Item, "edgeAfter"), 5) or else
                not (for some J in 1 .. I - 1 => Same (F (E (Directories, J), "fd"), F (Item, "parentFd"))))) or else
              not Closed (F (Item, "fd")) then return R.Confinement_Not_Established; end if;
         end;
      end loop;
      for I in 1 .. V.Count (Data, Leases) loop
         declare Item : constant V.Node := E (Leases, I);
         begin
            if not Lease (Item) or else not Same (F (Item, "openReturn"), F (Item, "fd")) or else
              N (Item, "openErrno") /= "0" or else not Operation ("openSource", F (Item, "fd"), Opened => True) or else
              not (for some J in 1 .. V.Count (Data, Directories) =>
                Same (F (E (Directories, J), "fd"), F (Item, "parentFd"))) then
               return R.Confinement_Not_Established;
            end if;
         end;
      end loop;
      declare Members : constant V.Node := F (Planned, "sourceRoster");
      begin
         if Members.Form /= V.Array_Value then return R.Confinement_Not_Established; end if;
         for I in 1 .. V.Count (Data, Members) loop
            declare Item : constant V.Node := E (Members, I); Found : Boolean := False;
                    Content : constant B.Decoded := B.Base64 (S (Item, "payloadB64"));
            begin
               if not Content.Valid then return R.Confinement_Not_Established; end if;
               for J in 1 .. V.Count (Data, Leases) loop
                  declare Source : constant V.Node := E (Leases, J); Bytes : constant B.Decoded := Byte_Leaf (F (Source, "bytes"));
                  begin
                     if S (Source, "member") = S (Item, "path") then
                        if Found or else not Bytes.Valid or else Bytes.Data /= Content.Data then return R.Confinement_Not_Established; end if;
                        Found := True;
                     end if;
                  end;
               end loop;
               if not Found then return R.Confinement_Not_Established; end if;
            end;
         end loop;
      end;
      declare Planned_Roster : constant V.Node := F (Planned, "executedSourceRoster");
              Actual_Roster : constant V.Node := F (Actual, "executedSourceRoster");
      begin
         if Planned_Roster.Form /= V.Array_Value or else Actual_Roster.Form /= V.Array_Value or else
           V.Count (Data, Planned_Roster) /= V.Count (Data, Actual_Roster) or else V.Count (Data, Planned_Roster) = 0 then return R.Confinement_Not_Established; end if;
         for I in 1 .. V.Count (Data, Planned_Roster) loop
            declare Planned_Row : constant V.Node := E (Planned_Roster, I); Row : constant V.Node := E (Actual_Roster, I);
                    Binding : constant V.Node := F (Planned_Row, "binding");
                    Content : constant B.Decoded := Byte_Leaf (F (Row, "bytes")); Found : Boolean := False;
            begin
               if S (Planned_Row, "kind") /= S (Row, "kind") or else S (Binding, "path") /= S (Row, "logicalPath") or else
                 not Content.Valid or else N (Binding, "byteCount") /= Image (Content.Length) or else
                 S (Binding, "sha256") /= B.Digest (Content.Data) then return R.Confinement_Not_Established; end if;
               for J in 1 .. V.Count (Data, Leases) loop
                  declare Source : constant V.Node := E (Leases, J); Bytes : constant B.Decoded := Byte_Leaf (F (Source, "bytes"));
                  begin
                     if Same (F (Source, "binding"), Binding) then
                        if Found or else not Bytes.Valid or else Bytes.Data /= Content.Data then return R.Confinement_Not_Established; end if;
                        Found := True;
                     end if;
                  end;
               end loop;
               if not Found then return R.Confinement_Not_Established; end if;
            end;
         end loop;
      end;
      return R.Confinement_Established;
   end Complete_Observation;

   function Observe (Expected, Acquired, Result_Record : String; Raw : W.Raw_Record)
      return R.Confinement_Observation is
      Root : constant V.Node := V.Parse (Result_Record);
      Capture : constant V.Node := V.Field (Result_Record, Root, "protectedProviderCapture");
   begin
      if Capture.Form in V.Missing | V.Null_Value then return R.Confinement_Unmeasured; end if;
      if not W.Well_Formed (Raw) or else
        not (for all I in Raw.Report_Facts'Range => Raw.Report_Facts (I) = 1) then
         return R.Confinement_Not_Established;
      end if;
      return Complete_Observation (Expected, Acquired, Result_Record, False);
   end Observe;

   function Captured (Expected, Acquired, Result_Record : String) return Boolean is
     (Complete_Observation (Expected, Acquired, Result_Record, True) = R.Confinement_Established);
end Worldline.Report_Custody_Native;
