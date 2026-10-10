with SPARK.Big_Integers;
with Worldline.Custody_V2_Requester_Join;
with Worldline.Custody_V2_Root_Evidence;
with Worldline.Custody_V2_Archive_Projection;
with Worldline.Retained_Evidence_Replay;
with Worldline.Scoped_Capture_Projection;
with Worldline.Custody_V2_Operation_Journal;
with Worldline.Scoped_Capture_Evolution_Projection;
package body Worldline.Custody_V2_Subject_Evidence with SPARK_Mode is
   package V renames L.V;
   package S renames V.S;
   package E renames V.E;
   package C renames L.C;
   package J renames Worldline.Custody_V2_Requester_Join;
   package RE renames Worldline.Custody_V2_Root_Evidence;
   package R renames Worldline.Retained_Evidence_Replay;
   package AP renames Worldline.Custody_V2_Archive_Projection;
   package CP renames Worldline.Scoped_Capture_Projection;
   package Evolution renames Worldline.Scoped_Capture_Evolution_Projection;
   use type Q.Byte_Count;
   use type Q.Byte;
   use type E.Bytes;
   use type E.Value_Kind;
   use type D.Decode_Status;
   use type L.Decode_Status;
   use type L.Original_Format;
   use type M.Event_Kind;
   use type M.Subject_Kind;
   use type M.Actor;
   use type M.Request_Phase;
   use type M.Digest;
   use type M.Transfer_Mode;
   use type Q.Ordering;
   use type L.S.SQL_Class;
   use type R.Replay_State;
   use type R.J.Status;
   use type R.J.Admission_Mode;
   use type SPARK.Big_Integers.Big_Integer;
   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span is
     (S.Field (Data, Item, Name));
   function Archive_Number (Data : E.Bytes; Item : E.Span)
      return SPARK.Big_Integers.Big_Integer is
      Value : SPARK.Big_Integers.Big_Integer := SPARK.Big_Integers.To_Big_Integer (0);
      Place : SPARK.Big_Integers.Big_Integer := SPARK.Big_Integers.To_Big_Integer (1);
   begin
      if not R.Archive_Integer_Valid (Data, Item) then return Value; end if;
      for B of R.Archive_Integer_Magnitude (Data, Item) loop
         Value := Value + SPARK.Big_Integers.To_Big_Integer (Integer (B)) * Place;
         Place := Place * 256;
      end loop;
      return (if R.Archive_Integer_Negative (Data, Item) then -Value else Value);
   end Archive_Number;
   function Text_Extends (Data : E.Bytes; Actual, Base : E.Span; Suffix : String)
      return Boolean is
   begin
      if not V.Valid_Text (Data, Actual) or else not V.Valid_Text (Data, Base) then return False; end if;
      declare
         Left : constant E.Bytes := V.Text_Value (Data, Actual);
         Right : constant E.Bytes := V.Text_Value (Data, Base);
      begin
         return Left'Length >= Right'Length and then Left'Length - Right'Length = Suffix'Length and then
           (for all I in Right'Range => Left (Left'First + (I - Right'First)) = Right (I)) and then
           (for all I in Suffix'Range =>
              Left (Left'First + (Right'Length + Q.Byte_Count (I - Suffix'First))) = Character'Pos (Suffix (I)));
      end;
   end Text_Extends;
   function Actor_Identity (Data : E.Bytes; Left, Right : E.Span) return Boolean is
      function Genuine (Actor : E.Span) return Boolean is
        (V.Is_Integer (Data, F (Data, Actor, "pid")) and then
         V.Is_Integer (Data, F (Data, Actor, "start_tick")) and then
         RE.Number (Data, F (Data, Actor, "pid")) > 0 and then
         RE.Number (Data, F (Data, Actor, "start_tick")) >= 0 and then
         RE.Stat_Field (Data, F (Data, Actor, "stat"), 1) = RE.Number (Data, F (Data, Actor, "pid")) and then
         RE.Stat_Field (Data, F (Data, Actor, "stat"), 22) = RE.Number (Data, F (Data, Actor, "start_tick")));
   begin
      return Genuine (Left) and then Genuine (Right) and then
        J.Same (Data, F (Data, Left, "boot"), F (Data, Right, "boot")) and then
        J.Same (Data, F (Data, Left, "pid"), F (Data, Right, "pid")) and then
        J.Same (Data, F (Data, Left, "start_tick"), F (Data, Right, "start_tick"));
   end Actor_Identity;
   function Raw_Same (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (E.C.P.Valid (Data, Left) and then E.C.P.Valid (Data, Right) and then
      Left.Length = Right.Length and then
      (if Left.Length > 0 then
         (for all I in Q.Byte_Count range 0 .. Left.Length - 1 =>
            Data (Left.First + I) = Data (Right.First + I))));
   function Bytes_Span (Data : E.Bytes; Encoded, Raw : E.Span) return Boolean is
   begin
      if not V.Valid_Bytes (Data, Encoded) or else not E.C.P.Valid (Data, Raw) then
         return False;
      end if;
      declare
         Bytes : constant E.Bytes := V.Bytes_Value (Data, Encoded);
      begin
         return Bytes'Length = Raw.Length and then
           (if Raw.Length > 0 then
              (for all I in Q.Byte_Count range 0 .. Raw.Length - 1 =>
                 Bytes (Bytes'First + I) = Data (Raw.First + I)));
      end;
   end Bytes_Span;
   function Cell_Count (Data : E.Bytes; Cell : L.S.SQL_Cell; Count : Q.Byte_Count)
      return Boolean
   is
      Rest : Q.Byte_Count := Count;
   begin
      if Cell.Kind /= L.S.SQL_Blob or else not L.S.Span_Valid (Data, Cell.Bytes) then return False; end if;
      if Cell.Bytes.Length > 0 then
         for I in Q.Byte_Count range 0 .. Cell.Bytes.Length - 1 loop
            pragma Loop_Variant (Increases => I);
            if Data (Cell.Bytes.First + I) /= Q.Byte (Rest mod 256) then return False; end if;
            Rest := Rest / 256;
         end loop;
      end if;
      return Rest = 0;
   end Cell_Count;
   function Decimal_Matches (Data : E.Bytes; Encoded : E.Span; Quantity : Q.Quantity)
      return Boolean
   is
   begin
      if not V.Valid_Text (Data, Encoded) or else not Q.Span_Valid (Data, Quantity) or else
         Q.Is_Negative (Data, Quantity) then return False; end if;
      declare
         Text : constant E.Bytes := V.Text_Value (Data, Encoded);
         Magnitude : E.Bytes (1 .. Text'Length) := (others => 0);
         Used : Q.Byte_Count := 0;
         Carry, Digit : Natural;
      begin
         if Text'Length = 0 or else
            (Text'Length > 1 and then Text (Text'First) = Character'Pos ('0')) then return False; end if;
         for I in Text'Range loop
            pragma Loop_Variant (Increases => I);
            pragma Loop_Invariant (Used <= I - Text'First);
            if Text (I) not in Character'Pos ('0') .. Character'Pos ('9') then return False; end if;
            Carry := Natural (Text (I) - Character'Pos ('0'));
            for K in Q.Byte_Count range 1 .. Used loop
               pragma Loop_Variant (Increases => K);
               pragma Loop_Invariant (Carry <= 9);
               Digit := Natural (Magnitude (K)) * 10 + Carry;
               Magnitude (K) := Q.Byte (Digit mod 256);
               Carry := Digit / 256;
            end loop;
            if Carry > 0 then
               if Used = Magnitude'Length then return False; end if;
               Used := Used + 1; Magnitude (Used) := Q.Byte (Carry);
            end if;
         end loop;
         if Quantity.Length > 0 then
            for I in Q.Byte_Count range 0 .. Quantity.Length - 1 loop
               pragma Loop_Variant (Increases => I);
               if Data (Quantity.First + I) /=
                  (if I < Used then Magnitude (I + 1) else 0) then return False; end if;
            end loop;
         end if;
         return Used <= Quantity.Length;
      end;
   end Decimal_Matches;
   function Archive_Quantity_Matches
     (Data, Archive_Data : E.Bytes; Node : E.Span; Quantity : Q.Quantity)
      return Boolean is
   begin
      if not Q.Span_Valid (Data, Quantity) or else Q.Is_Negative (Data, Quantity) or else
         not R.Archive_Bytes_Valid (Archive_Data, Node) then return False; end if;
      declare
         Bytes : constant E.Bytes := R.Archive_Bytes (Archive_Data, Node);
         Extent : constant E.Count := E.Count'Max (Bytes'Length, Quantity.Length);
      begin
         if Extent > 0 then
            for I in E.Count range 0 .. Extent - 1 loop
               pragma Loop_Variant (Increases => I);
               if (if I < Bytes'Length then Bytes (Bytes'First + I) else 0) /=
                  (if I < Quantity.Length then Data (Quantity.First + I) else 0)
               then return False; end if;
            end loop;
         end if;
         return True;
      end;
   end Archive_Quantity_Matches;
   function Archive_Text_Matches
     (Data, Archive_Data : E.Bytes; Raw_Text, Node : E.Span)
      return Boolean is
      View : constant E.View := E.Decode (Archive_Data, Node, E.Operation);
   begin
      if not E.C.P.Valid (Data, Raw_Text) or else View.Form /= E.Text_Value or else
         not E.Bytes_Valid (Archive_Data, View.Payload) then return False; end if;
      declare Bytes : constant E.Bytes := E.Materialize (Archive_Data, View.Payload); begin
         return Bytes'Length = Raw_Text.Length and then
           (if Raw_Text.Length > 0 then
              (for all I in E.Count range 0 .. Raw_Text.Length - 1 =>
                 Bytes (Bytes'First + I) = Data (Raw_Text.First + I)));
      end;
   end Archive_Text_Matches;
   function Decimal_Value (Data : E.Bytes; Item : E.Span)
      return SPARK.Big_Integers.Valid_Big_Integer
   is
      Result : SPARK.Big_Integers.Valid_Big_Integer := SPARK.Big_Integers.To_Big_Integer (0);
   begin
      if not V.Valid_Text (Data, Item) then return SPARK.Big_Integers.To_Big_Integer (-1); end if;
      declare Text : constant E.Bytes := V.Text_Value (Data, Item); begin
         if Text'Length = 0 or else
            (Text'Length > 1 and then Text (Text'First) = Character'Pos ('0'))
         then return SPARK.Big_Integers.To_Big_Integer (-1); end if;
         for I in Text'Range loop
            pragma Loop_Variant (Increases => I);
            if Text (I) not in Character'Pos ('0') .. Character'Pos ('9') then
               return SPARK.Big_Integers.To_Big_Integer (-1);
            end if;
            Result := Result * 10 + SPARK.Big_Integers.To_Big_Integer
              (Integer (Text (I) - Character'Pos ('0')));
         end loop;
         return Result;
      end;
   end Decimal_Value;
   function Nonce_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
   begin
      if not V.Valid_Text (Data, Item) then return False; end if;
      declare Text : constant E.Bytes := V.Text_Value (Data, Item); begin
         return Text'Length = 64 and then
           (for all I in Text'Range => Text (I) in Character'Pos ('0') .. Character'Pos ('9') |
              Character'Pos ('a') .. Character'Pos ('f'));
      end;
   end Nonce_Valid;
   function Syscall (Data : E.Bytes; Item, Source : E.Span; Name : String)
      return Boolean is
     (S.Text_Is (Data, F (Data, Item, "call"), Name) and then
      J.Integer_Is (Data, F (Data, Item, "result"), 0) and then
      J.Integer_Is (Data, F (Data, Item, "errno"), 0) and then
      J.Same (Data, F (Data, Item, "source"), Source));
   function Identity (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (J.Same (Data, F (Data, Left, "device"), F (Data, Right, "device")) and then
      J.Same (Data, F (Data, Left, "inode"), F (Data, Right, "inode")) and then
      J.Same (Data, F (Data, Left, "mode"), F (Data, Right, "mode")) and then
      J.Same (Data, F (Data, Left, "uid"), F (Data, Right, "uid")) and then
      J.Same (Data, F (Data, Left, "gid"), F (Data, Right, "gid")) and then
      V.Valid_Bytes (Data, F (Data, Left, "fdinfo")) and then
      V.Valid_Bytes (Data, F (Data, Right, "fdinfo")));
   function Socket_Source (Data : E.Bytes; Socket, Source : E.Span) return Boolean is
     (J.Same (Data, F (Data, Socket, "source"), Source) and then
      J.Same (Data, F (Data, F (Data, Socket, "fstat"), "source"), Source) and then
      J.Same (Data, F (Data, F (Data, Socket, "peercred"), "source"), Source) and then
      J.Same (Data, F (Data, F (Data, Socket, "domain"), "source"), Source) and then
      J.Same (Data, F (Data, F (Data, Socket, "type"), "source"), Source) and then
      J.Same (Data, F (Data, F (Data, Socket, "peername"), "source"), Source));
   function Kcmp_Pids (Data : E.Bytes; Args, Front_Actor, Worker_Pidfd : E.Span)
      return Boolean
   is
   begin
      return V.Is_Integer (Data, F (Data, Args, "pid1")) and then
        V.Is_Integer (Data, F (Data, Args, "pid2")) and then
        RE.Number (Data, F (Data, Args, "pid1")) > 0 and then
        RE.Number (Data, F (Data, Args, "pid2")) > 0 and then
        RE.Stat_Field (Data, F (Data, Front_Actor, "stat"), 1) = RE.Number (Data, F (Data, Args, "pid1")) and then
        RE.Pidfd_Pid (Data, F (Data, Worker_Pidfd, "fdinfo")) = RE.Number (Data, F (Data, Args, "pid2"));
   end Kcmp_Pids;
   function Role_Socket
     (Data : E.Bytes; Socket, Document, Source : E.Span) return Boolean
   is
      Original : constant E.Span := F (Data, Document, "socket");
      function Call_Joined (Name : String; Option, Size : Long_Long_Integer) return Boolean is
         Now : constant E.Span := F (Data, Socket, Name);
         Old : constant E.Span := F (Data, Original, Name);
         Result : constant E.Span := F (Data, Now, "result");
         Errno : constant E.Span := F (Data, Now, "errno");
      begin
         if not V.Is_Integer (Data, Result) or else not V.Is_Integer (Data, Errno) or else
            not S.Text_Is (Data, F (Data, Now, "call"), (if Option = 0 then "getpeername" else "getsockopt")) or else
            not S.Text_Is (Data, F (Data, Old, "call"), (if Option = 0 then "getpeername" else "getsockopt")) or else
            not J.Same (Data, F (Data, Now, "fd"), F (Data, Socket, "fd")) or else
            not J.Same (Data, F (Data, Now, "source"), Source) or else
            not J.Same (Data, Result, F (Data, Old, "result")) or else
            not J.Same (Data, Errno, F (Data, Old, "errno"))
         then return False; end if;
         if Option /= 0 and then
            (not J.Integer_Is (Data, F (Data, Now, "level"), 1) or else
             not J.Integer_Is (Data, F (Data, Now, "option"), Option) or else
             not J.Integer_Is (Data, F (Data, Now, "requested"), Size) or else
             not J.Integer_Is (Data, F (Data, Old, "level"), 1) or else
             not J.Integer_Is (Data, F (Data, Old, "option"), Option) or else
             not J.Integer_Is (Data, F (Data, Old, "requested"), Size))
         then return False; end if;
         if J.Integer_Is (Data, Result, -1) then
            return RE.Number (Data, Errno) > 0 and then
              ((V.Is_Null (Data, F (Data, Now, "raw")) and then V.Is_Null (Data, F (Data, Old, "raw"))) or else
               (V.Valid_Bytes (Data, F (Data, Now, "raw")) and then
                V.Valid_Bytes (Data, F (Data, Old, "raw")) and then
                J.Same_Bytes (Data, F (Data, Now, "raw"), F (Data, Old, "raw"))));
         end if;
         if not J.Integer_Is (Data, Result, 0) or else not J.Integer_Is (Data, Errno, 0) or else
            not V.Valid_Bytes (Data, F (Data, Now, "raw")) or else not V.Valid_Bytes (Data, F (Data, Old, "raw"))
         then return False; end if;
         if Name /= "peercred" then
            return J.Same_Bytes (Data, F (Data, Now, "raw"), F (Data, Old, "raw"));
         end if;
         declare
            Actual : constant E.Bytes := V.Bytes_Value (Data, F (Data, Now, "raw"));
            Prior : constant E.Bytes := V.Bytes_Value (Data, F (Data, Old, "raw"));
         begin
            return Actual'Length = 12 and then Prior'Length = 12 and then
              (for all I in E.Count range 4 .. 11 => Actual (Actual'First + I) = Prior (Prior'First + I));
         end;
      end Call_Joined;
   begin
      return S.Text_Is (Data, F (Data, Document, "schema"), "worldline.custody-role-socket-v1") and then
        Identity (Data, F (Data, F (Data, Socket, "fstat"), "identity"), F (Data, F (Data, Original, "fstat"), "identity")) and then
        J.Same (Data, F (Data, F (Data, Socket, "fstat"), "fd"), F (Data, Socket, "fd")) and then
        J.Integer_Is (Data, F (Data, F (Data, Socket, "fstat"), "result"), 0) and then
        J.Integer_Is (Data, F (Data, F (Data, Socket, "fstat"), "errno"), 0) and then
        J.Same (Data, F (Data, F (Data, Socket, "fstat"), "source"), Source) and then
        Call_Joined ("peercred", 17, 12) and then Call_Joined ("domain", 39, 4) and then
        Call_Joined ("type", 3, 4) and then Call_Joined ("peername", 0, 0);
   end Role_Socket;
   function Roles_Joined
     (Data : E.Bytes; Actual, Original, Source, KCMP_Source : E.Span; Received : Boolean)
      return Boolean
   is
      Count : constant E.Count := V.Count (Data, Original);
   begin
      if not V.Is_Sequence (Data, Actual) or else not V.Is_Sequence (Data, Original) or else
         Count = 0 or else V.Count (Data, Actual) /= Count then return False; end if;
      for I in E.Count range 0 .. Count - 1 loop
         pragma Loop_Variant (Increases => I);
         declare
            A : constant E.Span := V.Element (Data, Actual, I);
            O : constant E.Span := V.Element (Data, Original, I);
            K : constant E.Span := F (Data, A, "kcmp");
            Lock : constant E.Span := F (Data, A, "flock");
            Args : constant E.Span := F (Data, K, "args");
         begin
            if not J.Same (Data, F (Data, A, "role"), F (Data, O, "role")) or else
               not Identity (Data, F (Data, A, "origin"), F (Data, O, "identity")) or else
               not J.Same (Data, F (Data, A, "front_fd"), F (Data, O, "fd")) then return False; end if;
            if not Syscall (Data, F (Data, A, "fstat"), Source, "fstat") or else
               not J.Same (Data, F (Data, F (Data, F (Data, A, "fstat"), "args"), "fd"),
                 F (Data, A, (if Received then "worker_fd" else "front_fd"))) or else
               not Identity (Data, F (Data, F (Data, A, "fstat"), "identity"),
                 F (Data, A, (if Received then "current" else "origin")))
            then return False; end if;
            declare
               Mode : constant V.Count_Result := V.Nonnegative_Count (Data, F (Data, F (Data, A, "origin"), "mode"));
            begin
               if not Mode.Present then return False; end if;
               if Mode.Value / 4_096 mod 16 = 12 then
                  if not Role_Socket (Data, F (Data, A, "socket"), F (Data, O, "socket_document"), Source) or else
                     not J.Same (Data, F (Data, F (Data, A, "socket"), "fd"),
                       F (Data, A, (if Received then "worker_fd" else "front_fd")))
                  then return False; end if;
               elsif not V.Is_Null (Data, F (Data, A, "socket")) or else
                     not V.Is_Null (Data, F (Data, O, "socket_document"))
               then return False;
               end if;
            end;
            for Previous in E.Count range 0 .. I - 1 loop
               pragma Loop_Variant (Increases => Previous);
               if J.Same (Data, F (Data, A, "role"), F (Data, V.Element (Data, Actual, Previous), "role")) or else
                  J.Same (Data, F (Data, A, "front_fd"), F (Data, V.Element (Data, Actual, Previous), "front_fd")) or else
                  (Received and then J.Same (Data, F (Data, A, "worker_fd"),
                    F (Data, V.Element (Data, Actual, Previous), "worker_fd")))
               then return False; end if;
            end loop;
            if Received and then
               (not Identity (Data, F (Data, A, "origin"), F (Data, A, "current")) or else
                not Syscall (Data, K, KCMP_Source, "kcmp") or else
                not J.Same (Data, F (Data, A, "kcmp_source"), KCMP_Source) or else
                not Actor_Identity (Data, F (Data, A, "kcmp_actor"), F (Data, O, "front_actor")) or else
                not J.Integer_Is (Data, F (Data, Args, "type"), 0) or else
                not J.Same (Data, F (Data, Args, "idx1"), F (Data, A, "front_fd")) or else
                not J.Same (Data, F (Data, Args, "idx2"), F (Data, A, "worker_fd")) or else
                not J.Same (Data, F (Data, A, "front_actor"), F (Data, O, "front_actor")) or else
                not Identity (Data, F (Data, A, "worker_pidfd"), F (Data, O, "worker_pidfd")) or else
                not Kcmp_Pids (Data, Args, F (Data, A, "kcmp_actor"), F (Data, O, "worker_pidfd")))
            then return False; end if;
            if not J.Same (Data, F (Data, A, "lock_path"), F (Data, O, "lock_path")) or else
               (Received and then not V.Is_Null (Data, F (Data, O, "lock_path")) and then V.Is_Null (Data, Lock))
            then return False; end if;
            if not V.Is_Null (Data, Lock) and then
               (not Syscall (Data, Lock, Source, "flock") or else
                not J.Integer_Is (Data, F (Data, F (Data, Lock, "args"), "operation"), 6) or else
                not J.Same (Data, F (Data, F (Data, Lock, "args"), "fd"),
                  F (Data, A, (if Received then "worker_fd" else "front_fd"))))
            then return False; end if;
            if not S.Valid (Data, Lock) then return False; end if;
         end;
      end loop;
      return True;
   end Roles_Joined;
   function Spool_Write
     (Data : E.Bytes; Call, Source : E.Span; Whole : E.Bytes; Start : Q.Byte_Count)
      return Boolean
   is
      Parts : constant E.Span := F (Data, Call, "parts");
      Written : Q.Byte_Count := 0;
   begin
      if not S.Valid (Data, Parts) or else Start > Q.Byte_Count'Last - Whole'Length then return False; end if;
      if V.Is_Null (Data, Parts) then return True; end if;
      if not V.Is_Sequence (Data, Parts) or else V.Count (Data, Parts) = 0 then return False; end if;
      for I in E.Count range 0 .. V.Count (Data, Parts) - 1 loop
         pragma Loop_Variant (Increases => I);
         pragma Loop_Invariant (Written <= Whole'Length);
         declare
            Part : constant E.Span := V.Element (Data, Parts, I);
            Result : constant V.Count_Result := V.Nonnegative_Count (Data, F (Data, Part, "result"));
         begin
            if not Result.Present or else Result.Value = 0 or else Result.Value > Whole'Length - Written or else
               not S.Text_Is (Data, F (Data, Part, "call"), "pwrite") or else
               not J.Unsigned_Is (Data, F (Data, Part, "offset"), Start + Written) or else
               not J.Same (Data, F (Data, Part, "fd"), F (Data, Call, "fd")) or else
               not J.Integer_Is (Data, F (Data, Part, "errno"), 0) or else
               not J.Same (Data, F (Data, Part, "source"), Source) or else
               not V.Valid_Bytes (Data, F (Data, Part, "data"))
            then return False; end if;
            declare
               Offered : constant E.Bytes := V.Bytes_Value (Data, F (Data, Part, "data"));
            begin
               if Offered'Length < Result.Value or else Offered'Length > Whole'Length - Written or else
                  (for some K in E.Count range 0 .. Offered'Length - 1 =>
                     Offered (Offered'First + K) /= Whole (Whole'First + Written + K))
               then return False; end if;
            end;
            Written := Written + Result.Value;
         end;
      end loop;
      return Written = Whole'Length;
   end Spool_Write;
   type Spool_Result is record
      Joined : Boolean := False;
      Position : Q.Byte_Count := 0;
   end record;
   function Spool
     (Data : E.Bytes; Item, Source, Owner : E.Span; Closed : Boolean)
      return Spool_Result
   is
      Records : constant E.Span := F (Data, Item, "records");
      Raw : constant E.Span := F (Data, Item, "raw");
      FD : constant E.Span := F (Data, Item, "fd");
      Open : Boolean := False;
      Interval_Owner : E.Span := (1, 0);
      Interval_Source : E.Span := (1, 0);
      P : Q.Byte_Count := 0;
      Count : constant E.Count := V.Count (Data, Records);
      Write_Mode : constant Boolean := S.Text_Is (Data, F (Data, Item, "direction"), "write");
   begin
      if not V.Is_Sequence (Data, Records) or else Count = 0 or else
         not V.Valid_Bytes (Data, Raw) or else
         not (Write_Mode or else S.Text_Is (Data, F (Data, Item, "direction"), "read"))
      then return (False, 0); end if;
      declare
         Bytes : constant E.Bytes := V.Bytes_Value (Data, Raw);
      begin
         for I in E.Count range 0 .. Count - 1 loop
            pragma Loop_Variant (Increases => I);
            pragma Loop_Invariant (P <= Bytes'Length);
            declare
               Row : constant E.Span := V.Element (Data, Records, I);
               Kind : constant E.Span := F (Data, Row, "kind");
               Sync : constant E.Span := F (Data, Row, "fsync");
               Call : constant E.Span := F (Data, Row, "write");
               IO : constant E.Span := F (Data, Row, "io");
               Row_Source : constant E.Span := F (Data, Row, "source");
               function Marker return Boolean is
                 (J.Integer_Is (Data, F (Data, Row, "length"), 0) and then
                  V.Valid_Bytes (Data, F (Data, Row, "data")) and then
                  V.Bytes_Value (Data, F (Data, Row, "data"))'Length = 0 and then
                  J.Digest_Matches (Data, F (Data, Row, "data"), F (Data, Row, "sha256")) and then
                  V.Is_Null (Data, Call) and then V.Is_Null (Data, IO));
            begin
               if not Actor_Identity (Data, F (Data, Row, "owner"), F (Data, Row, "owner")) or else
                  not S.Valid (Data, Row_Source) or else
                  not S.Text_Is (Data, F (Data, Sync, "call"), "fsync") or else
                  not J.Unsigned_Is (Data, F (Data, Row, "position"), P) or else
                  not J.Same (Data, F (Data, Sync, "fd"), F (Data, Row, "spool_fd")) or else
                  not J.Integer_Is (Data, F (Data, Sync, "result"), 0) or else
                  not J.Integer_Is (Data, F (Data, Sync, "errno"), 0) or else
                  not J.Same (Data, F (Data, Sync, "source"), Row_Source)
               then return (False, 0); end if;
               if S.Text_Is (Data, Kind, (if Write_Mode then "WRITE_ARMED" else "ARMED")) then
                  if Open or else not Marker then return (False, 0); end if;
                  Open := True;
                  Interval_Owner := F (Data, Row, "owner");
                  Interval_Source := Row_Source;
               elsif S.Text_Is (Data, Kind, "CHUNK") then
                  if not Open or else not Actor_Identity (Data, F (Data, Row, "owner"), Interval_Owner) or else
                     not J.Same (Data, Row_Source, Interval_Source) or else
                     not V.Valid_Bytes (Data, F (Data, Row, "data")) or else
                     not J.Digest_Matches (Data, F (Data, Row, "data"), F (Data, Row, "sha256"))
                  then return (False, 0); end if;
                  declare
                     Chunk : constant E.Bytes := V.Bytes_Value (Data, F (Data, Row, "data"));
                  begin
                     if Chunk'Length > Bytes'Length - P or else
                        Chunk'Length = 0 or else
                        not S.Text_Is (Data, F (Data, IO, "call"), (if Write_Mode then "write" else "read")) or else
                        not S.Text_Is (Data, F (Data, Call, "call"),
                          (if V.Is_Null (Data, F (Data, Call, "parts")) then "pwrite" else "pwrite-stream")) or else
                        not J.Unsigned_Is (Data, F (Data, Row, "length"), Chunk'Length) or else
                        not J.Same (Data, F (Data, Call, "fd"), F (Data, Row, "spool_fd")) or else
                        not J.Unsigned_Is (Data, F (Data, Call, "offset"), P) or else
                        not J.Unsigned_Is (Data, F (Data, Call, "result"), Chunk'Length) or else
                        not J.Integer_Is (Data, F (Data, Call, "errno"), 0) or else
                        not J.Same (Data, F (Data, Call, "source"), Row_Source) or else
                        not J.Same_Bytes (Data, F (Data, Call, "data"), F (Data, Row, "data")) or else
                        not Spool_Write (Data, Call, Row_Source, Chunk, P) or else
                        not J.Same (Data, F (Data, IO, "fd"), F (Data, Row, "descriptor_fd")) or else
                        not Identity (Data, F (Data, IO, "identity"), F (Data, Item, "descriptor_identity")) or else
                        not J.Unsigned_Is (Data, F (Data, IO, "result"), Chunk'Length) or else
                        not J.Integer_Is (Data, F (Data, IO, "errno"), 0) or else
                        not J.Same (Data, F (Data, IO, "source"), Row_Source) or else
                        not J.Same_Bytes (Data, F (Data, IO, "raw"), F (Data, Row, "data")) or else
                        (Chunk'Length > 0 and then
                         (for some K in Q.Byte_Count range 0 .. Chunk'Length - 1 =>
                            Bytes (Bytes'First + P + K) /= Chunk (Chunk'First + K)))
                     then return (False, 0); end if;
                     P := P + Chunk'Length;
                  end;
               elsif S.Text_Is (Data, Kind, (if Write_Mode then "W_DONE" else "DISARMED")) then
                  if not Open or else not Marker or else
                     not J.Same (Data, Row_Source, Interval_Source) or else
                     not Actor_Identity (Data, F (Data, Row, "owner"), Interval_Owner) then
                     return (False, 0);
                  end if;
                  Open := False;
               else return (False, 0);
               end if;
            end;
         end loop;
         if Open = Closed or else not Actor_Identity (Data, Interval_Owner, Owner) or else
            not J.Same (Data, Interval_Source, Source) or else
            (not Write_Mode and then P /= Bytes'Length) or else
            not J.Unsigned_Is (Data, F (Data, Item, "position"), P) or else
            not J.Unsigned_Is (Data, F (Data, F (Data, Item, "identity"), "size"), Bytes'Length) or else
            not J.Same (Data, F (Data, F (Data, Item, "fsync"), "fd"), FD) or else
            not J.Integer_Is (Data, F (Data, F (Data, Item, "fsync"), "result"), 0) or else
            not J.Integer_Is (Data, F (Data, F (Data, Item, "fsync"), "errno"), 0) or else
            not J.Same (Data, F (Data, F (Data, Item, "fsync"), "source"), Source)
         then return (False, 0); end if;
         return (True, P);
      end;
   end Spool;
   function Primitive_Joined
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Require_Worker_Gone : Boolean; Serving_Query : Boolean := False;
      Output_Query : Boolean := False; Output_Context_Only : Boolean := False)
      return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      function Prior (Reference : E.Span; Head : M.Digest; Root : Boolean) return Q.Byte_Count is
      begin
         if Index not in Value.Events'Range or else not V.Valid_Text (Data, Reference) then return 0; end if;
         for I in Value.Events'First .. Index - 1 loop
            pragma Loop_Variant (Increases => I);
            declare
               Event : constant D.Decoded_Event := D.Decode (Data, Value.Events (I));
            begin
               if Event.Status = D.Decoded and then Event.Value.Event_Id = Head and then
                  S.Text_Matches (Data, Reference, Value.Events (I).Event_Id) and then
                  Q.Compare (Data, Event.Value.Generation, Before.Generation) = Q.Equal and then
                  (if Root then Event.Value.Kind_Of_Subject = M.Root
                   else Subject.Present and then Event.Value.Kind_Of_Subject = Subject.Value.Kind and then
                     M.L.Same (Data, Event.Value.Subject, Subject.Value.Subject) and then
                     Raw_Same (Data, Value.Events (I).Operation, Value.Events (Index).Operation))
               then return I; end if;
            end;
         end loop;
         return 0;
      end Prior;
   begin
      if Value.Status /= L.Parsed or else Index not in Value.Events'Range or else
         not L.Parsed_Spans_Valid (Value) then return False; end if;
      declare
         Raw : C.Event_Row renames Value.Events (Index);
         Decoded : constant D.Decoded_Event := D.Decode (Data, Raw);
         Original : constant E.Span := Value.Extras (Index).Original_Payload;
         X5 : constant E.Span := F (Data, Raw.Record_Archive, "x5");
         Facts : constant E.Span := F (Data, X5, "subject_evidence");
         Binding : constant E.Span := F (Data, Facts, "binding");
         Source : constant E.Span := F (Data, X5, "source_identity");
         Actor : constant E.Span := F (Data, X5, "actor_identity");
         Request : constant E.Span := F (Data, Facts, "request");
         Front : constant E.Span := F (Data, Facts, "front_socket");
         Worker : constant E.Span := F (Data, Facts, "worker_socket");
         Transfer : constant E.Span := F (Data, Facts, "transfer");
         Relay : constant E.Span := F (Data, Facts, "relay");
         Descriptor : constant E.Span := F (Data, Facts, "descriptor");
         Drain : constant E.Span := F (Data, Facts, "spool");
         Root_Index : Q.Byte_Count;
         Subject_Index : Q.Byte_Count := 0;
         function Root_Starter_Operation return E.Span is
         begin
            if not Before.Operation.Present then return (1, 0); end if;
            for I in Value.Events'First .. Index - 1 loop
               pragma Loop_Variant (Increases => I);
               declare Event : constant D.Decoded_Event := D.Decode (Data, Value.Events (I)); begin
                  if Event.Status = D.Decoded and then Event.Value.Kind_Of_Subject = M.Root and then
                     Q.Compare (Data, Event.Value.Generation, Before.Generation) = Q.Equal and then
                     M.L.Optional_Same (Data, Event.Value.Operation, Before.Operation)
                  then return Value.Events (I).Operation; end if;
               end;
            end loop;
            return (1, 0);
         end Root_Starter_Operation;
         Root_Starter_Reference : constant E.Span := Root_Starter_Operation;
         function Original_Field (Event_Index : Q.Byte_Count; Name : String) return E.Span is
         begin
            if Event_Index not in Value.Extras'Range then
               return (1, 0);
            elsif Value.Extras (Event_Index).Original_Encoding = L.Operation_Original then
               return S.A.Field (Data, Value.Extras (Event_Index).Original_Payload, Name);
            elsif Value.Extras (Event_Index).Original_Encoding = L.Scoped_Original then
               return F (Data, Value.Extras (Event_Index).Original_Payload, Name);
            else
               return (1, 0);
            end if;
         end Original_Field;
         function Original_Matches
           (Scoped : E.Span; Event_Index : Q.Byte_Count; Name : String;
            Profile : AP.Projection_Profile := AP.Scoped_Tree) return Boolean is
           (Event_Index in Value.Extras'Range and then
            (if Value.Extras (Event_Index).Original_Encoding = L.Operation_Original then
               AP.Scoped_Archive_Operation_Matches (Data, Data, Scoped, Original_Field (Event_Index, Name), Profile)
             elsif Value.Extras (Event_Index).Original_Encoding = L.Scoped_Original then
               J.Same (Data, Scoped, Original_Field (Event_Index, Name))
             else False));
         function Original_Image_Joined return Boolean is
           (if Value.Extras (Index).Original_Encoding = L.Operation_Original then
               AP.Scoped_Archive_Operation_Matches
                 (Data, Data, F (Data, Binding, "original"), Original, AP.Original_Image)
            elsif Value.Extras (Index).Original_Encoding = L.Scoped_Original then
               J.Same (Data, F (Data, Binding, "original"), Original)
            else False);
         function Field_Bound (Name : String) return Boolean is
           (J.Same (Data, F (Data, Binding, Name), F (Data, Raw.Base_Archive, Name)));
         function Original_Request return Boolean is
           (Original_Matches (Request, Index, "original_request") and then
            S.Text_Matches (Data, F (Data, Request, "observationId"), Raw.Subject) and then
            V.Valid_Hex_Field (Data, F (Data, Request, "rawRequest"), "value"));
         function Earlier_Facts return E.Span is
         begin
            if Subject_Index in Value.Events'Range then
               return F (Data, F (Data, Value.Events (Subject_Index).Record_Archive, "x5"), "subject_evidence");
            else
               return (1, 0);
            end if;
         end Earlier_Facts;
         function Same_Initial_Request return Boolean is
           (Original_Request and then Subject_Index in Value.Events'Range and then
            J.Same (Data, Request, F (Data, Earlier_Facts, "request")));
         function Live_Descriptor return Boolean is
           (Original_Matches (F (Data, Descriptor, "roster"), Index, "live_roster") and then
            V.Is_Sequence (Data, F (Data, Descriptor, "roster")) and then
            (for some I in E.Count range 0 .. V.Count (Data, F (Data, Descriptor, "roster")) - 1 =>
               J.Same (Data, F (Data, V.Element (Data, F (Data, Descriptor, "roster"), I), "role"), F (Data, Descriptor, "role")) and then
               J.Same (Data, F (Data, V.Element (Data, F (Data, Descriptor, "roster"), I), "fd"), F (Data, Descriptor, "fd")) and then
               Identity (Data, F (Data, V.Element (Data, F (Data, Descriptor, "roster"), I), "identity"), F (Data, Descriptor, "identity"))) and then
            S.Text_Matches (Data, F (Data, Descriptor, "role"), Raw.Subject));
         function Same_Initial_Descriptor return Boolean is
           (Subject_Index in Value.Events'Range and then
            J.Same (Data, F (Data, Descriptor, "role"), F (Data, F (Data, Earlier_Facts, "descriptor"), "role")) and then
            Identity (Data, F (Data, Descriptor, "identity"), F (Data, F (Data, Earlier_Facts, "descriptor"), "identity")));
         function Acquisitions_Joined return Boolean is
            Acquisitions : constant E.Span := Original_Field (Index, "acquisitions");
            Records : constant E.Span := F (Data, Drain, "records");
            Cursor : E.Count := 0;
         begin
            if E.Decode (Data, Acquisitions, E.Operation).Form /= E.List_Value or else
               not V.Is_Sequence (Data, Records) then return False; end if;
            if R.Archive_Length (Data, Acquisitions) > 0 then
               for I in E.Count range 0 .. R.Archive_Length (Data, Acquisitions) - 1 loop
                  pragma Loop_Variant (Increases => I);
                  declare
                     IO : constant E.Span := R.Archive_Index (Data, Acquisitions, I);
                     Result : constant E.Span := R.Archive_Field (Data, IO, "result");
                     Errno : constant E.Span := R.Archive_Field (Data, IO, "errno");
                     Raw_IO : constant E.Span := R.Archive_Field (Data, IO, "raw");
                     Matched : Boolean := False;
                  begin
                     if not R.Archive_Text_Is (Data, R.Archive_Field (Data, IO, "call"),
                          (if S.Text_Is (Data, F (Data, Drain, "direction"), "write") then "write" else "read")) or else
                        not R.Archive_Integer_Valid (Data, Result) or else
                        not R.Archive_Integer_Valid (Data, Errno)
                     then return False; end if;
                     if Archive_Number (Data, Result) > 0 then
                        while Cursor < V.Count (Data, Records) loop
                           pragma Loop_Variant (Increases => Cursor);
                           declare Row : constant E.Span := V.Element (Data, Records, Cursor); begin
                              Cursor := Cursor + 1;
                              if S.Text_Is (Data, F (Data, Row, "kind"), "CHUNK") then
                                 Matched := AP.Scoped_Archive_Operation_Matches
                                   (Data, Data, F (Data, Row, "io"), IO);
                                 exit;
                              end if;
                           end;
                        end loop;
                        if not Matched then return False; end if;
                     elsif Archive_Number (Data, Result) = 0 then
                        if Archive_Number (Data, Errno) /= 0 or else
                           not R.Archive_Bytes_Valid (Data, Raw_IO) or else
                           R.Archive_Bytes (Data, Raw_IO)'Length /= 0
                        then return False; end if;
                     elsif Archive_Number (Data, Result) /= -1 or else
                           Archive_Number (Data, Errno) <= 0 or else not R.Archive_Is_None (Data, Raw_IO)
                     then return False; end if;
                     if V.Count (Data, Records) = 0 or else
                        not (for some K in E.Count range 0 .. V.Count (Data, Records) - 1 =>
                          AP.Scoped_Archive_Operation_Matches
                            (Data, Data, F (Data, V.Element (Data, Records, K), "source"),
                              R.Archive_Field (Data, IO, "source")) and then
                          AP.Scoped_Archive_Operation_Matches
                            (Data, Data, F (Data, V.Element (Data, Records, K), "descriptor_fd"),
                              R.Archive_Field (Data, IO, "fd")))
                     then return False; end if;
                  end;
               end loop;
            end if;
            while Cursor < V.Count (Data, Records) loop
               pragma Loop_Variant (Increases => Cursor);
               if S.Text_Is (Data, F (Data, V.Element (Data, Records, Cursor), "kind"), "CHUNK") then
                  return False;
               end if;
               Cursor := Cursor + 1;
            end loop;
            return True;
         end Acquisitions_Joined;
         function Spool_Prefix_Joined return Boolean is
            Prior_Drain : constant E.Span := F (Data, Earlier_Facts, "spool");
            Prior_Records : constant E.Span := F (Data, Prior_Drain, "records");
            Records : constant E.Span := F (Data, Drain, "records");
         begin
            if not V.Is_Sequence (Data, Prior_Records) or else
               not V.Is_Sequence (Data, Records) or else
               V.Count (Data, Records) < V.Count (Data, Prior_Records)
            then return False; end if;
            if V.Count (Data, Prior_Records) > 0 and then
               (for some I in E.Count range 0 .. V.Count (Data, Prior_Records) - 1 =>
                  not J.Same (Data, V.Element (Data, Records, I), V.Element (Data, Prior_Records, I)))
            then return False; end if;
            return True;
         end Spool_Prefix_Joined;
         function Front_Source return E.Span is
            Found : E.Span := (1, 0);
         begin
            for I in Value.Events'First .. Index - 1 loop
               pragma Loop_Variant (Increases => I);
               declare Event : constant D.Decoded_Event := D.Decode (Data, Value.Events (I)); begin
                  if Event.Status = D.Decoded and then Event.Value.Appending_Actor = M.Front and then
                     Event.Value.Kind_Of_Subject = Decoded.Value.Kind_Of_Subject and then
                     Q.Compare (Data, Event.Value.Generation, Decoded.Value.Generation) = Q.Equal and then
                     Q.Compare (Data, Event.Value.Subgeneration, Decoded.Value.Subgeneration) = Q.Equal and then
                     M.L.Same (Data, Event.Value.Subject, Decoded.Value.Subject) and then
                     Raw_Same (Data, Value.Events (I).Operation, Raw.Operation)
                  then Found := F (Data, F (Data, Value.Events (I).Record_Archive, "x5"), "source_identity"); end if;
               end;
            end loop;
            return Found;
         end Front_Source;
         function Root_Custody_ACK return Boolean is
         begin
            for I in Value.Events'First .. Index - 1 loop
               pragma Loop_Variant (Increases => I);
               declare
                  Event : constant D.Decoded_Event := D.Decode (Data, Value.Events (I));
               begin
                  if Event.Status = D.Decoded and then
                     Event.Value.Kind = M.Custody_Ack_Event and then
                     Event.Value.Kind_Of_Subject = M.Root and then
                     Q.Compare (Data, Event.Value.Generation, Before.Generation) = Q.Equal and then
                     M.L.Optional_Same (Data, Event.Value.Operation, Before.Operation)
                  then return True; end if;
               end;
            end loop;
            return False;
         end Root_Custody_ACK;
         function Rights_Match (Rights : E.Span; Field_Name : String) return Boolean is
            Rows : constant E.Span := F (Data, Transfer, "roles");
            N : constant E.Count := V.Count (Data, Rows);
         begin
            if not V.Is_Sequence (Data, Rows) or else not V.Valid_Bytes (Data, Rights) then return False; end if;
            declare
               Raw_Rights : constant E.Bytes := V.Bytes_Value (Data, Rights);
               FD : Q.Byte_Count;
            begin
               if Raw_Rights'Length mod 4 /= 0 or else Raw_Rights'Length / 4 /= N then return False; end if;
               for I in E.Count range 0 .. N - 1 loop
                  pragma Loop_Variant (Increases => I);
                  if Raw_Rights (Raw_Rights'First + I * 4 + 3) >= 128 then return False; end if;
                  FD := 0;
                  for K in reverse E.Count range 0 .. 3 loop
                     pragma Loop_Variant (Decreases => K);
                     FD := FD * 256 + Q.Byte_Count (Raw_Rights (Raw_Rights'First + I * 4 + K));
                  end loop;
                  if not J.Unsigned_Is (Data, F (Data, V.Element (Data, Rows, I), Field_Name), FD) then return False; end if;
               end loop;
               return N > 0;
            end;
         end Rights_Match;
         function Receive_Source return E.Span is
         begin
            if Decoded.Value.Kind = M.Drain_Ofd_Evidence_Event then
               return F (Data, F (Data, Facts, "ofd"), "worker_report_source");
            else
               return Source;
            end if;
         end Receive_Source;
         function Single_Right (Rights, Expected : E.Span) return Boolean is
         begin
            if not V.Valid_Bytes (Data, Rights) then return False; end if;
            declare
               Raw : constant E.Bytes := V.Bytes_Value (Data, Rights);
               Number : Q.Byte_Count := 0;
            begin
               if Raw'Length /= 4 or else Raw (Raw'First + 3) >= 128 then return False; end if;
               for I in reverse E.Count range 0 .. 3 loop
                  pragma Loop_Variant (Decreases => I);
                  Number := Number * 256 + Q.Byte_Count (Raw (Raw'First + I));
               end loop;
               return J.Unsigned_Is (Data, Expected, Number);
            end;
         end Single_Right;
         function Transfer_Calls return Boolean is
            Rows : constant E.Span := F (Data, Transfer, "roles");
            Sent : constant E.Span := F (Data, F (Data, Transfer, "send"), "parts");
            Received : constant E.Span := F (Data, F (Data, Transfer, "receive"), "parts");
            N : constant E.Count := V.Count (Data, Rows);
            Send_Channel : constant E.Span := F (Data, Transfer, "send_channel");
            Receive_Channel : constant E.Span := F (Data, Transfer, "receive_channel");
            function Carrier_Call
              (Call, Channel, Expected_Source : E.Span; Sending : Boolean) return Boolean is
               Args : constant E.Span := F (Data, Call, "args");
               Rights : constant E.Span := F (Data, Args, "rights");
            begin
               return J.Same (Data, F (Data, Call, "fd"), F (Data, Channel, "fd")) and then
                 J.Same (Data, F (Data, Call, "source"), Expected_Source) and then
                 J.Integer_Is (Data, F (Data, Call, "errno"), 0) and then
                 J.Integer_Is (Data, F (Data, Args, "flags"), (if Sending then 16_384 else 1_073_741_824)) and then
                 J.Same_Bytes (Data, F (Data, Args, "body"), F (Data, Call, "frame")) and then
                 Identity (Data, F (Data, Args, "channel"), F (Data, F (Data, Channel, "fstat"), "identity")) and then
                 J.Same_Bytes (Data, F (Data, Args, "peer"), F (Data, F (Data, Channel, "peercred"), "raw")) and then
                 V.Is_Sequence (Data, Rights) and then V.Count (Data, Rights) = 1 and then
                 Single_Right (F (Data, Call, "rights"), V.Element (Data, Rights, 0));
            end Carrier_Call;
            function Send_Controls (Call : E.Span) return Boolean is
               Controls : constant E.Span := F (Data, Call, "controls");
               Rights_Found, Credentials_Found : Boolean := False;
            begin
               if not V.Is_Sequence (Data, Controls) or else V.Count (Data, Controls) /= 2 then return False; end if;
               for C in E.Count range 0 .. 1 loop
                  pragma Loop_Variant (Increases => C);
                  declare Control : constant E.Span := V.Element (Data, Controls, C); begin
                     if not V.Is_Sequence (Data, Control) or else V.Count (Data, Control) /= 3 or else
                        not J.Integer_Is (Data, V.Element (Data, Control, 0), 1)
                     then return False; end if;
                     if J.Integer_Is (Data, V.Element (Data, Control, 1), 1) then
                        if Rights_Found or else not J.Same_Bytes
                          (Data, V.Element (Data, Control, 2), F (Data, Call, "rights"))
                        then return False; end if;
                        Rights_Found := True;
                     elsif J.Integer_Is (Data, V.Element (Data, Control, 1), 2) then
                        if Credentials_Found or else not J.Same_Bytes
                          (Data, V.Element (Data, Control, 2), F (Data, Call, "sender"))
                        then return False; end if;
                        Credentials_Found := True;
                     else return False; end if;
                  end;
               end loop;
               return Rights_Found and then Credentials_Found;
            end Send_Controls;
         begin
            if not Socket_Source (Data, Send_Channel, Front_Source) or else
               not Role_Socket (Data, Send_Channel, F (Data, Transfer, "send_channel_document"), Front_Source) or else
               not Socket_Source (Data, Receive_Channel, Receive_Source) or else
               not Role_Socket (Data, Receive_Channel, F (Data, Transfer, "receive_channel_document"), Receive_Source) or else
               not V.Is_Sequence (Data, Sent) or else not V.Is_Sequence (Data, Received) or else
               V.Count (Data, Sent) /= N or else V.Count (Data, Received) /= N or else N = 0
            then return False; end if;
            for I in E.Count range 0 .. N - 1 loop
               pragma Loop_Variant (Increases => I);
               declare
                  Row : constant E.Span := V.Element (Data, Rows, I);
                  Send : constant E.Span := V.Element (Data, Sent, I);
                  Receive : constant E.Span := V.Element (Data, Received, I);
                  Controls : constant E.Span := F (Data, Receive, "controls");
                  Flags : constant V.Count_Result := V.Nonnegative_Count (Data, F (Data, Receive, "flags"));
                  Input_Flags : constant V.Count_Result := V.Nonnegative_Count (Data, F (Data, Receive, "input_flags"));
                  Rights_Found, Credentials_Found : Boolean := False;
               begin
                  if not S.Text_Is (Data, F (Data, Send, "call"), "sendmsg") or else
                     not S.Text_Is (Data, F (Data, Receive, "call"), "recvmsg") or else
                     not Carrier_Call (Send, Send_Channel, Front_Source, True) or else
                     not Send_Controls (Send) or else
                     not Carrier_Call (Receive, Receive_Channel, Receive_Source, False) or else
                     not J.Integer_Is (Data, F (Data, Send, "flags"), 16_384) or else
                     not J.Same (Data, F (Data, Receive, "msg_flags"), F (Data, Receive, "flags")) or else
                     not J.Same_Bytes (Data, F (Data, Receive, "sender_credentials"), F (Data, Receive, "sender")) or else
                     not J.Integer_Is (Data, F (Data, Send, "result"), 1) or else
                     not J.Integer_Is (Data, F (Data, Receive, "result"), 1) or else
                     not Single_Right (F (Data, Send, "rights"), F (Data, Row, "front_fd")) or else
                     not Single_Right (F (Data, Receive, "rights"), F (Data, Row, "worker_fd")) or else
                     not J.Same_Bytes (Data, F (Data, Send, "sender"), F (Data, Transfer, "sender")) or else
                     not J.Same_Bytes (Data, F (Data, Receive, "sender"), F (Data, Transfer, "received_sender")) or else
                     not J.Same_Bytes (Data, F (Data, Send, "frame"), F (Data, Send, "raw")) or else
                     not J.Same_Bytes (Data, F (Data, Receive, "frame"), F (Data, Receive, "raw")) or else
                     not V.Valid_Bytes (Data, F (Data, Send, "frame")) or else
                     V.Bytes_Value (Data, F (Data, Send, "frame")) /= E.Bytes'(1 => Character'Pos ('F')) or else
                     not V.Valid_Bytes (Data, F (Data, Receive, "frame")) or else
                     V.Bytes_Value (Data, F (Data, Receive, "frame")) /= E.Bytes'(1 => Character'Pos ('F')) or else
                     not Flags.Present or else Flags.Value / 8 mod 2 /= 0 or else Flags.Value / 32 mod 2 /= 0 or else
                     not Input_Flags.Present or else Input_Flags.Value / 1_073_741_824 mod 2 /= 1 or else
                     not V.Is_Sequence (Data, Controls) or else V.Count (Data, Controls) /= 2
                  then return False; end if;
                  for K in E.Count range 0 .. 1 loop
                     pragma Loop_Variant (Increases => K);
                     declare Control : constant E.Span := V.Element (Data, Controls, K); begin
                        if not V.Is_Sequence (Data, Control) or else V.Count (Data, Control) /= 3 or else
                           not J.Integer_Is (Data, V.Element (Data, Control, 0), 1)
                        then return False; end if;
                        if J.Integer_Is (Data, V.Element (Data, Control, 1), 1) then
                           if Rights_Found or else not J.Same_Bytes
                             (Data, V.Element (Data, Control, 2), F (Data, Receive, "rights"))
                           then return False; end if;
                           Rights_Found := True;
                        elsif J.Integer_Is (Data, V.Element (Data, Control, 1), 2) then
                           if Credentials_Found or else not J.Same_Bytes
                             (Data, V.Element (Data, Control, 2), F (Data, Transfer, "received_sender"))
                           then return False; end if;
                           Credentials_Found := True;
                        else return False; end if;
                     end;
                  end loop;
                  if not (Rights_Found and then Credentials_Found) then return False; end if;
               end;
            end loop;
            return True;
         end Transfer_Calls;
         function Stream_Complete (Stream, Expected_Source : E.Span) return Boolean is
            Parts : constant E.Span := F (Data, Stream, "parts");
         begin
            if not V.Valid_Bytes (Data, F (Data, Transfer, "frame")) or else not S.Valid (Data, Parts) then return False; end if;
            declare
               Frame : constant E.Bytes := V.Bytes_Value (Data, F (Data, Transfer, "frame"));
               Position : E.Count := 0;
            begin
               if not J.Unsigned_Is (Data, F (Data, Stream, "result"), Frame'Length) or else
                  not J.Integer_Is (Data, F (Data, Stream, "errno"), 0) or else
                  not J.Same (Data, F (Data, Stream, "source"), Expected_Source)
               then return False; end if;
               if V.Is_Null (Data, Parts) then return True; end if;
               if not V.Is_Sequence (Data, Parts) then return False; end if;
               for I in E.Count range 0 .. V.Count (Data, Parts) - 1 loop
                  pragma Loop_Variant (Increases => I);
                  pragma Loop_Invariant (Position <= Frame'Length);
                  declare
                     Part : constant E.Span := V.Element (Data, Parts, I);
                  begin
                     if not V.Valid_Bytes (Data, F (Data, Part, "raw")) or else
                        not J.Same (Data, F (Data, Part, "fd"), F (Data, Stream, "fd")) or else
                        not J.Integer_Is (Data, F (Data, Part, "errno"), 0) or else
                        not J.Same (Data, F (Data, Part, "source"), Expected_Source)
                     then return False; end if;
                     declare
                        Chunk : constant E.Bytes := V.Bytes_Value (Data, F (Data, Part, "raw"));
                     begin
                        if Chunk'Length = 0 or else Chunk'Length > Frame'Length - Position or else
                           not J.Unsigned_Is (Data, F (Data, Part, "result"), Chunk'Length) or else
                           (for some K in E.Count range 0 .. Chunk'Length - 1 =>
                              Frame (Frame'First + Position + K) /= Chunk (Chunk'First + K))
                        then return False; end if;
                        Position := Position + Chunk'Length;
                     end;
                  end;
               end loop;
               return Position = Frame'Length;
            end;
         end Stream_Complete;
         function Sender_Domain return Boolean is
         begin
            if not V.Valid_Bytes (Data, F (Data, Transfer, "sender")) or else
               not V.Valid_Bytes (Data, F (Data, Transfer, "received_sender"))
            then return False; end if;
            declare
               Sent : constant E.Bytes := V.Bytes_Value (Data, F (Data, Transfer, "sender"));
               Received : constant E.Bytes := V.Bytes_Value (Data, F (Data, Transfer, "received_sender"));
            begin
               return Sent'Length = 12 and then Received'Length = 12 and then
                 (for all I in E.Count range 4 .. 11 =>
                    Sent (Sent'First + I) = Received (Received'First + I));
            end;
         end Sender_Domain;
         function Transfer_Sent return Boolean is
         begin
            if not V.Valid_Bytes (Data, F (Data, Transfer, "frame")) or else
               not Sender_Domain or else
               not J.Same_Bytes (Data, F (Data, F (Data, Transfer, "send"), "frame"), F (Data, Transfer, "frame")) or else
               not J.Same_Bytes (Data, F (Data, F (Data, Transfer, "receive"), "frame"), F (Data, Transfer, "frame")) or else
               not Rights_Match (F (Data, F (Data, Transfer, "send"), "rights"), "front_fd") or else
               not Rights_Match (F (Data, F (Data, Transfer, "receive"), "rights"), "worker_fd") or else
               not Transfer_Calls
            then return False; end if;
            declare
               Frame : constant E.Bytes := V.Bytes_Value (Data, F (Data, Transfer, "frame"));
               Sent : constant E.Span := F (Data, Transfer, "send");
               Received : constant E.Span := F (Data, Transfer, "receive");
               Flags : constant V.Count_Result := V.Nonnegative_Count (Data, F (Data, Received, "flags"));
               Input_Flags : constant V.Count_Result := V.Nonnegative_Count (Data, F (Data, Received, "input_flags"));
            begin
               return Frame'Length > 0 and then
                 Stream_Complete (Sent, Front_Source) and then
                 Stream_Complete (Received, Receive_Source) and then
                 J.Same_Bytes (Data, F (Data, Transfer, "sender"),
                   F (Data, F (Data, Earlier_Facts, "binding"), "sender_credentials")) and then
                 Flags.Present and then Flags.Value / 8 mod 2 = 0 and then
                 Flags.Value / 32 mod 2 = 0 and then
                 Input_Flags.Present and then Input_Flags.Value / 1_073_741_824 mod 2 = 1;
            end;
         end Transfer_Sent;
         function Native_Gates
           (Require_Ready : Boolean := True; Require_Root : Boolean := True)
            return Boolean is
            List : constant E.Span := Value.Extras (Index).Native_Observations_Payload;
            Count : constant E.Count := R.Archive_Length (Data, List);
            Operation_Found : Boolean := False;
            Root_Found : Boolean := False;
            type Operation_Join is (Unjoined_Operation, Other_Operation, Own_Operation);
            function Original_Operation (Obs, Material : E.Span) return Operation_Join is
               Operations : constant E.Span := F (Data, X5, "operation_authority_observations");
               Journal : constant E.Span := F (Data, X5, "operation_journal_events");
               N : constant E.Count := V.Count (Data, Operations);
               Joined : Operation_Join := Unjoined_Operation;
            begin
               if not V.Is_Sequence (Data, Operations) or else not V.Is_Sequence (Data, Journal) then
                  return Unjoined_Operation;
               end if;
               for K in E.Count range 0 .. N - 1 loop
                  pragma Loop_Variant (Increases => K);
                  declare
                     Item : constant E.Span := V.Element (Data, Operations, K);
                     Event : constant E.Span := F (Data, Item, "event");
                  begin
                     if AP.Scoped_Archive_Operation_Matches
                          (Data, Data, F (Data, Item, "observation"), Obs) and then
                        AP.Scoped_Archive_Operation_Matches
                          (Data, Data, F (Data, Item, "material"), Material) and then
                        (for some N in E.Count range 0 .. V.Count (Data, Journal) - 1 =>
                           J.Same (Data, Event, V.Element (Data, Journal, N))) and then
                        R.Operation_Capture_Matches (Data, F (Data, Item, "observation"),
                          F (Data, Item, "material"), Event) and then
                        V.Valid_Hex_Field (Data, F (Data, Event, "capture"), "value")
                     then
                        declare
                           Capture : constant E.Bytes := V.Hex_Value (Data, F (Data, Event, "capture"), "value");
                           Request_Node : constant E.Span := S.A.Field
                             (Capture, (Capture'First, Capture'Length), "request");
                        begin
                           if S.Text_Matches (Data, F (Data, Event, "operation"), Raw.Operation) then
                              if Decoded.Value.Kind_Of_Subject = M.Descriptor or else
                                 J.Request_Archive_Matches (Data, Capture, Request, Request_Node)
                              then return Own_Operation; end if;
                              return Unjoined_Operation;
                           end if;
                           Joined := Other_Operation;
                        end;
                     end if;
                  end;
               end loop;
               return Joined;
            end Original_Operation;
         begin
            if Value.Extras (Index).Native_Observations_Encoding /= L.Operation_Original or else
               not S.A.Valid (Data, List) or else
               E.Decode (Data, List, E.Operation).Form /= E.Tuple_Value or else Count = 0
            then return False; end if;
            for I in E.Count range 0 .. Count - 1 loop
               pragma Loop_Variant (Increases => I);
               declare
                  Native_Item : constant E.Span := R.Archive_Index (Data, List, I);
                  Role : constant E.Span := R.Archive_Field (Data, Native_Item, "role");
                  Obs : constant E.Span := R.Archive_Field (Data, Native_Item, "observation");
                  Material : constant E.Span := R.Archive_Field (Data, Native_Item, "material");
                  Provenance : constant E.Span := R.Archive_Field (Data, Native_Item, "provenance");
               begin
                  if R.Archive_Text_Is (Data, Role, "operation") then
                     declare
                        Joined : constant Operation_Join := Original_Operation (Obs, Material);
                     begin
                        if not R.Operation_Material_Matches (Data, Obs, Material) or else
                           R.Reestablish_Operation_Observation (Data, Obs).State /= R.Native_Redecided or else
                           Joined = Unjoined_Operation
                        then return False; end if;
                        Operation_Found := Operation_Found or else Joined = Own_Operation;
                     end;
                  elsif R.Archive_Text_Is (Data, Role, "root-admission") or else
                        R.Archive_Text_Is (Data, Role, "root-execution") then
                     declare
                        Native : constant R.Root_Replay_Result := R.Reestablish_Root_Observation (Data, Obs);
                     begin
                        if Native.State /= R.Native_Redecided or else
                           Native.Mode /= R.J.Root_Controller_Admission or else
                           (Require_Ready and then Native.Native_Status /= R.J.Root_Ready_Conjunction) or else
                           not R.Root_Material_Matches (Data, Obs, Material) or else
                           not R.Root_Capture_Matches (Data, Obs, Provenance) or else
                           not CP.Scoped_Capture_Matches (Data, Obs, Provenance) or else
                           not Native.Id (R.A.Operation_Id).Present or else
                           not C.G.Origin_Matches (Data, Root_Starter_Reference,
                             Native.Id (R.A.Operation_Id).Value)
                        then return False; end if;
                        Root_Found := Root_Found or else R.Archive_Text_Is (Data, Role, "root-admission");
                     end;
                  elsif R.Archive_Text_Is (Data, Role, "scoped-classify") or else
                        R.Archive_Text_Is (Data, Role, "scoped-check") or else
                        R.Archive_Text_Is (Data, Role, "scoped-validate") then
                     if not (if R.Archive_Text_Is (Data, Role, "scoped-check") then
                               RE.Native_Capture_Joined (Data, Obs, Material, Provenance, "scoped-check")
                             elsif R.Archive_Text_Is (Data, Role, "scoped-validate") then
                               RE.Native_Capture_Joined (Data, Obs, Material, Provenance, "scoped-validate")
                             else RE.Native_Capture_Joined (Data, Obs, Material, Provenance, "scoped-classify"))
                     then return False; end if;
                  else return False;
                  end if;
               end;
            end loop;
            return Operation_Found and then (not Require_Root or else Root_Found);
         end Native_Gates;
         function Worker_Report_Joined return Boolean is
            Ofd : constant E.Span := F (Data, Facts, "ofd");
            Report : constant E.Span := Original_Field (Index, "worker_report");
            Ofd_Transfer : constant E.Span :=
              (if Decoded.Value.Kind = M.Drain_Intake_Event then F (Data, Earlier_Facts, "transfer")
               else Transfer);
            Rows : constant E.Span := F (Data, Ofd, "roles");
            Old_Rows : constant E.Span := R.Archive_Field (Data, Report, "roles");
            KCMP : constant E.Span := F (Data, Ofd, "kcmp");
            Locks : constant E.Span := F (Data, Ofd, "locks");
            Native_List : constant E.Span := R.Archive_Field (Data, Report, "native_observations");
            N : constant E.Count := V.Count (Data, Rows);
            Root_Found, Descriptor_Found, Spool_Found : Boolean := False;
            function Field_Joined (Name : String; Captured : E.Span) return Boolean is
              (AP.Scoped_Archive_Operation_Matches
                (Data, Data, Captured, R.Archive_Field (Data, Report, Name)));
         begin
            if not Original_Matches (F (Data, Ofd, "worker_report"), Index, "worker_report", AP.Original_Image) or else
               not Field_Joined ("source", F (Data, Ofd, "worker_report_source")) or else
               not Field_Joined ("actor", F (Data, Ofd, "worker_report_actor")) or else
               not Actor_Identity (Data, F (Data, Ofd, "worker_report_actor"), F (Data, Ofd, "worker_report_actor")) or else
               not AP.Scoped_Archive_Operation_Matches
                 (Data, Data, F (Data, Ofd, "worker_report_native_observations"), Native_List, AP.Original_Image) or else
               not J.Same (Data, Rows, F (Data, Ofd_Transfer, "roles")) or else
               not J.Same (Data, F (Data, Ofd, "send"), F (Data, Ofd_Transfer, "send")) or else
               not V.Is_Sequence (Data, Rows) or else N = 0 or else
               not R.Archive_Is_Sequence (Data, Old_Rows) or else R.Archive_Length (Data, Old_Rows) /= N or else
               not V.Is_Sequence (Data, KCMP) or else V.Count (Data, KCMP) /= N or else
               not V.Is_Sequence (Data, Locks) or else V.Count (Data, Locks) /= N or else
               not S.A.Valid (Data, Native_List) or else
               E.Decode (Data, Native_List, E.Operation).Form /= E.Tuple_Value
            then return False; end if;
            for I in E.Count range 0 .. N - 1 loop
               pragma Loop_Variant (Increases => I);
               declare
                  Row : constant E.Span := V.Element (Data, Rows, I);
                  Old : constant E.Span := R.Archive_Index (Data, Old_Rows, I);
                  function Same_Field (Name : String) return Boolean is
                    (AP.Scoped_Archive_Operation_Matches
                      (Data, Data, F (Data, Row, Name), R.Archive_Field (Data, Old, Name)));
               begin
                  if not (Same_Field ("role") and then Same_Field ("front_fd") and then
                          Same_Field ("worker_fd") and then Same_Field ("origin") and then
                          Same_Field ("current") and then Same_Field ("fstat") and then
                          Same_Field ("socket") and then Same_Field ("flock") and then
                          Same_Field ("front_actor") and then Same_Field ("worker_pidfd") and then
                          Same_Field ("lock_path")) or else
                     not AP.Scoped_Archive_Operation_Matches
                       (Data, Data, F (Data, Row, "worker_kcmp"), R.Archive_Field (Data, Old, "kcmp")) or else
                     not J.Same (Data, V.Element (Data, KCMP, I), F (Data, Row, "kcmp")) or else
                     not J.Same (Data, V.Element (Data, Locks, I), F (Data, Row, "flock"))
                  then return False; end if;
                  if J.Same (Data, F (Data, Row, "role"), F (Data, Descriptor, "role")) then
                     if Descriptor_Found or else not Field_Joined ("role", F (Data, Row, "role")) or else
                        not Field_Joined ("fd", F (Data, Row, "worker_fd"))
                     then return False; end if;
                     Descriptor_Found := True;
                  end if;
                  if Text_Extends (Data, F (Data, Row, "role"), F (Data, Descriptor, "role"), "/spool") then
                     if Spool_Found or else not Field_Joined ("spool_fd", F (Data, Row, "worker_fd")) then
                        return False;
                     end if;
                     Spool_Found := True;
                  end if;
               end;
            end loop;
            for I in E.Count range 1 .. R.Archive_Length (Data, Native_List) loop
               pragma Loop_Variant (Increases => I);
               declare
                  Item : constant E.Span := R.Archive_Index (Data, Native_List, I - 1);
                  Obs : constant E.Span := R.Archive_Field (Data, Item, "observation");
                  Material : constant E.Span := R.Archive_Field (Data, Item, "material");
                  Provenance : constant E.Span := R.Archive_Field (Data, Item, "provenance");
                  Native : constant R.Root_Replay_Result := R.Reestablish_Root_Observation (Data, Obs);
               begin
                  if not R.Archive_Text_Is (Data, R.Archive_Field (Data, Item, "role"), "root-admission") or else
                     Native.State /= R.Native_Redecided or else
                     Native.Mode /= R.J.Root_Controller_Admission or else
                     Native.Native_Status /= R.J.Root_Ready_Conjunction or else
                     not R.Root_Material_Matches (Data, Obs, Material) or else
                     not R.Root_Capture_Matches (Data, Obs, Provenance) or else
                     not CP.Scoped_Capture_Matches (Data, Obs, Provenance) or else
                     not Native.Id (R.A.Operation_Id).Present or else
                     not C.G.Origin_Matches (Data, Root_Starter_Reference, Native.Id (R.A.Operation_Id).Value)
                  then return False; end if;
                  Root_Found := True;
               end;
            end loop;
            return Root_Found and then Descriptor_Found and then Spool_Found;
         end Worker_Report_Joined;
         use type E.C.Genesis_Correspondence;
         function Frame_Valid
           (Frame_Node, Payload_Body, Metadata : E.Span; Expected_Type : String)
            return Boolean
         is
         begin
            if not V.Valid_Bytes (Data, Frame_Node) or else not S.Valid (Data, Payload_Body) or else
               not E.C.P.Valid (Data, Value.Key) or else
               not S.Text_Is (Data, F (Data, Payload_Body, "type"), Expected_Type) or else
               not Decimal_Matches (Data, F (Data, Payload_Body, "generation"), Before.Generation) or else
               not Decimal_Matches (Data, F (Data, Payload_Body, "reattach_epoch"), Before.Reattach_Epoch) or else
               not Decimal_Matches (Data, F (Data, Payload_Body, "subgeneration"), Decoded.Value.Subgeneration) or else
               not S.Text_Matches (Data, F (Data, Payload_Body, "operation"), Raw.Operation) or else
               not S.Text_Matches (Data, F (Data, Payload_Body, "request"), Raw.Subject) or else
               not J.Same (Data, F (Data, Payload_Body, "sequence"), F (Data, Metadata, "sequence")) or else
               not J.Same (Data, F (Data, Payload_Body, "nonce"), F (Data, Metadata, "nonce")) or else
               (if Expected_Type in "GATE_REQUEST" | "GATE_RESPONSE" then
                  Decimal_Value (Data, F (Data, Payload_Body, "sequence")) < 1
                else Decimal_Value (Data, F (Data, Payload_Body, "sequence")) < 0) or else
               not Nonce_Valid (Data, F (Data, Payload_Body, "nonce")) or else
               Subject_Index = 0 or else
               not S.Text_Matches (Data, F (Data, Payload_Body, "admission_head"), Value.Events (Subject_Index).Event_Id)
            then return False; end if;
            declare
               Frame : constant E.Bytes := V.Bytes_Value (Data, Frame_Node);
               Length : Q.Byte_Count := 0;
            begin
               if Frame'Length < 40 or else
                  Frame (Frame'First) /= Character'Pos ('W') or else
                  Frame (Frame'First + 1) /= Character'Pos ('L') or else
                  Frame (Frame'First + 2) /= Character'Pos ('R') or else
                  Frame (Frame'First + 3) /= Character'Pos ('Y')
               then return False; end if;
               for I in Q.Byte_Count range 4 .. 7 loop
                  pragma Loop_Variant (Increases => I);
                  Length := Length * 256 + Q.Byte_Count (Frame (Frame'First + I));
               end loop;
               if Length /= Frame'Length - 40 or else
                  not AP.Scoped_Archive_Operation_Matches
                    (Data, Frame, Payload_Body, (Frame'First + 8, Length), AP.Relay_Frame)
               then return False; end if;
               return J.Frame_Mac_Matches (Data, Frame, Value.Key,
                 (Frame'First, Frame'Length),
                 "worldline.root-worker-relay-v1" & Character'Val (0));
            end;
         end Frame_Valid;
         function Frame_Stream_Joined
           (Frame_Node, Stream, Expected_Source, Channel : E.Span; Sending : Boolean)
            return Boolean
         is
            Parts : constant E.Span := F (Data, Stream, "parts");
         begin
            if not V.Valid_Bytes (Data, Frame_Node) or else
               not J.Same_Bytes (Data, Frame_Node, F (Data, Stream, "frame")) or else
               not V.Is_Sequence (Data, Parts) or else V.Count (Data, Parts) = 0 or else
               not J.Same (Data, F (Data, Stream, "fd"), F (Data, Channel, "fd")) or else
               not J.Same (Data, F (Data, Stream, "source"), Expected_Source) or else
               not J.Integer_Is (Data, F (Data, Stream, "errno"), 0)
            then return False; end if;
            declare
               Frame : constant E.Bytes := V.Bytes_Value (Data, Frame_Node);
               Position : E.Count := 0;
            begin
               if not J.Unsigned_Is (Data, F (Data, Stream, "result"), Frame'Length) then return False; end if;
               for I in E.Count range 0 .. V.Count (Data, Parts) - 1 loop
                  pragma Loop_Variant (Increases => I);
                  pragma Loop_Invariant (Position <= Frame'Length);
                  declare
                     Part : constant E.Span := V.Element (Data, Parts, I);
                     Args : constant E.Span := F (Data, Part, "args");
                  begin
                     if not S.Text_Is (Data, F (Data, Part, "call"), (if Sending then "send" else "recv")) or else
                        not J.Same (Data, F (Data, Part, "fd"), F (Data, Channel, "fd")) or else
                        not J.Same (Data, F (Data, Args, "fd"), F (Data, Channel, "fd")) or else
                        not J.Integer_Is (Data, F (Data, Args, "flags"), (if Sending then 16_384 else 0)) or else
                        not J.Same (Data, F (Data, Part, "source"), Expected_Source) or else
                        not J.Integer_Is (Data, F (Data, Part, "errno"), 0) or else
                        not V.Valid_Bytes (Data, F (Data, Part, "raw"))
                     then return False; end if;
                     declare Chunk : constant E.Bytes := V.Bytes_Value (Data, F (Data, Part, "raw")); begin
                        if Chunk'Length = 0 or else Chunk'Length > Frame'Length - Position or else
                           not J.Unsigned_Is (Data, F (Data, Part, "result"), Chunk'Length) or else
                           (for some K in E.Count range 0 .. Chunk'Length - 1 =>
                              Chunk (Chunk'First + K) /= Frame (Frame'First + Position + K))
                        then return False; end if;
                        if Sending then
                           if not V.Valid_Bytes (Data, F (Data, Args, "body")) then return False; end if;
                           declare Offered : constant E.Bytes := V.Bytes_Value (Data, F (Data, Args, "body")); begin
                              if Offered'Length < Chunk'Length or else Offered'Length > Frame'Length - Position or else
                                 (for some K in E.Count range 0 .. Offered'Length - 1 =>
                                    Offered (Offered'First + K) /= Frame (Frame'First + Position + K))
                              then return False; end if;
                           end;
                        else
                           declare Maximum : constant V.Count_Result := V.Nonnegative_Count (Data, F (Data, Args, "maximum")); begin
                              if not Maximum.Present or else Maximum.Value < Chunk'Length then return False; end if;
                           end;
                        end if;
                        Position := Position + Chunk'Length;
                     end;
                  end;
               end loop;
               return Position = Frame'Length;
            end;
         end Frame_Stream_Joined;
         function Relay_Admission_Joined return Boolean is
         begin
            return Socket_Source (Data, F (Data, Relay, "channel"), Source) and then
              Role_Socket (Data, F (Data, Relay, "channel"), F (Data, Relay, "channel_document"), Source) and then
              Decimal_Matches (Data, F (Data, Relay, "reattach_epoch"), Before.Reattach_Epoch) and then
              J.Same (Data, F (Data, Relay, "front_reread"), Request) and then
              J.Socket_Matches (Data, Front, F (Data, Relay, "front_reread")) and then
              Socket_Source (Data, Front,
                (if Decoded.Value.Kind = M.Request_Intake_Event then Front_Source else Source)) and then
              V.Is_Null (Data, F (Data, Transfer, "send")) and then
              V.Is_Null (Data, F (Data, Transfer, "receive")) and then
              (if Decoded.Value.Kind = M.Request_Intake_Event then
                 Subject_Index in Value.Events'Range and then
                 S.Text_Matches (Data, F (Data, Relay, "transfer_head"), Value.Events (Subject_Index).Event_Id)
               else V.Is_Null (Data, F (Data, Relay, "transfer_head")));
         end Relay_Admission_Joined;
         function Read_Failure_Joined
           (Failure, Encoded_Error, Initial_Socket, Expected_Source : E.Span) return Boolean is
            Traces : constant E.Span := F (Data, Failure, "calls");
         begin
            if not V.Valid_Bytes (Data, Encoded_Error) or else
               not J.Same (Data, F (Data, Failure, "source"), Expected_Source) or else
               not V.Is_Sequence (Data, Traces)
            then return False; end if;
            declare
               Error_Data : constant E.Bytes := V.Bytes_Value (Data, Encoded_Error);
               Error : constant E.Span := (Error_Data'First, Error_Data'Length);
               Code : constant E.Span := R.Archive_Field (Error_Data, Error, "code");
               FD : constant E.Span := F (Data, Initial_Socket, "fd");
               Initial_Identity : constant E.Span := F (Data, F (Data, Initial_Socket, "fstat"), "identity");
               function Trace_Joined (Trace : E.Span; Last : Boolean) return Boolean is
                  N : constant E.Count := V.Count (Data, Trace);
               begin
                  if not V.Is_Sequence (Data, Trace) or else N not in 1 .. 2 then return False; end if;
                  declare
                     Stat : constant E.Span := V.Element (Data, Trace, 0);
                     Read : constant E.Span := V.Element (Data, Trace, N - 1);
                     Args : constant E.Span := F (Data, Read, "args");
                  begin
                     if not S.Text_Is (Data, F (Data, Stat, "call"), "fstat") or else
                        not J.Same (Data, F (Data, Stat, "fd"), FD) or else
                        not J.Same (Data, F (Data, F (Data, Stat, "args"), "fd"), FD) or else
                        not J.Same (Data, F (Data, Stat, "source"), Expected_Source)
                     then return False; end if;
                     if N = 2 and then
                       (not Syscall (Data, Stat, Expected_Source, "fstat") or else
                        not S.Text_Is (Data, F (Data, Read, "call"), "getsockopt") or else
                        not J.Same (Data, F (Data, Read, "fd"), FD) or else
                        not J.Same (Data, F (Data, Args, "fd"), FD) or else
                        not J.Integer_Is (Data, F (Data, Args, "level"), 1) or else
                        not J.Integer_Is (Data, F (Data, Args, "option"), 17) or else
                        not J.Integer_Is (Data, F (Data, Args, "length"), 12) or else
                        not J.Same (Data, F (Data, Read, "source"), Expected_Source))
                     then return False; end if;
                     if not Last then return N = 2 and then Syscall (Data, Read, Expected_Source, "getsockopt"); end if;
                     if R.Archive_Text_Is (Error_Data, R.Archive_Field (Error_Data, Error, "class"), "OSError") then
                        return J.Integer_Is (Data, F (Data, Read, "result"), -1) and then
                          V.Is_Integer (Data, F (Data, Read, "errno")) and then
                          RE.Number (Data, F (Data, Read, "errno")) > 0 and then
                          R.Archive_Integer_Valid (Error_Data, Code) and then
                          RE.Number (Data, F (Data, Read, "errno")) = Archive_Number (Error_Data, Code);
                     end if;
                     if not R.Archive_Text_Is (Error_Data, R.Archive_Field (Error_Data, Error, "class"), "WorldlineError") or else
                        not Syscall (Data, Read, Expected_Source, (if N = 1 then "fstat" else "getsockopt"))
                     then return False; end if;
                     if R.Archive_Text_Is (Error_Data, Code, "PEER_TRANSPORT_INVALID") then
                        declare Mode : constant V.Count_Result := V.Nonnegative_Count (Data, F (Data, F (Data, Stat, "identity"), "mode")); begin
                           return N = 1 and then Mode.Present and then Mode.Value / 4_096 mod 16 /= 12;
                        end;
                     end if;
                     return N = 2 and then
                       (R.Archive_Text_Is (Error_Data, Code, "PEER_TRANSPORT_CHANGED") or else
                        R.Archive_Text_Is (Error_Data, Code, "PEER_REQUEST_MISMATCH")) and then
                       V.Valid_Bytes (Data, F (Data, Read, "raw")) and then
                       V.Bytes_Value (Data, F (Data, Read, "raw"))'Length = 12 and then
                       (not J.Same (Data, F (Data, F (Data, Stat, "identity"), "device"), F (Data, Initial_Identity, "device")) or else
                        not J.Same (Data, F (Data, F (Data, Stat, "identity"), "inode"), F (Data, Initial_Identity, "inode")) or else
                        not J.Same (Data, F (Data, F (Data, Stat, "identity"), "mode"), F (Data, Initial_Identity, "mode")) or else
                        not J.Same_Bytes (Data, F (Data, Read, "raw"), F (Data, F (Data, Initial_Socket, "peercred"), "raw")));
                  end;
               end Trace_Joined;
            begin
               if V.Count (Data, Traces) = 0 then
                  declare
                     Close : constant E.Span := F (Data, Failure, "close");
                     Readback : constant E.Span := F (Data, Close, "readback");
                  begin
                     return R.Archive_Text_Is (Error_Data, R.Archive_Field (Error_Data, Error, "class"), "WorldlineError") and then
                       R.Archive_Text_Is (Error_Data, Code, "PEER_TRANSPORT_CLOSED") and then
                       Syscall (Data, Close, Expected_Source, "close") and then
                       J.Same (Data, F (Data, Close, "fd"), FD) and then
                       J.Same (Data, F (Data, F (Data, Close, "args"), "fd"), FD) and then
                       S.Text_Is (Data, F (Data, Readback, "call"), "fstat") and then
                       J.Same (Data, F (Data, Readback, "fd"), FD) and then
                       J.Integer_Is (Data, F (Data, Readback, "result"), -1) and then
                       J.Integer_Is (Data, F (Data, Readback, "errno"), 9) and then
                       J.Same (Data, F (Data, Readback, "source"), Expected_Source);
                  end;
               end if;
               for I in E.Count range 0 .. V.Count (Data, Traces) - 1 loop
                  pragma Loop_Variant (Increases => I);
                  if not Trace_Joined (V.Element (Data, Traces, I), I = V.Count (Data, Traces) - 1) then return False; end if;
               end loop;
               return True;
            end;
         end Read_Failure_Joined;
         function Relay_Gate_Joined (Gate : E.Span; Allow_Error : Boolean) return Boolean is
            Request_Body : constant E.Span := F (Data, Gate, "request_body");
            Response_Body : constant E.Span := F (Data, Gate, "response_body");
            function Echo (Name : String) return Boolean is
              (J.Same (Data, F (Data, Request_Body, Name), F (Data, Response_Body, Name)));
            function Empty_Gate_Request return Boolean is
               Payload : constant E.Span := F (Data, Request_Body, "payload");
            begin
               if not V.Valid_Bytes (Data, Payload) then return False; end if;
               declare
                  Image : constant E.Bytes := V.Bytes_Value (Data, Payload);
                  Node : constant E.View := E.Decode (Image, (Image'First, Image'Length), E.Operation);
               begin
                  return Node.Form = E.Object_Value and then E.Array_Length (Image, Node.Children) = 0;
               end;
            end Empty_Gate_Request;
            function Observation_Joined return Boolean is
            begin
               if not V.Valid_Bytes (Data, F (Data, Response_Body, "payload")) then return False; end if;
               declare
                  Payload : constant E.Bytes := V.Bytes_Value (Data, F (Data, Response_Body, "payload"));
                  Image : constant E.Span := (Payload'First, Payload'Length);
                  Observed : constant E.View := E.Decode (Payload, S.A.Field (Payload, Image, "observation"), E.Operation);
                  Error : constant E.Span := S.A.Field (Payload, Image, "error");
               begin
                  if Observed.Form = E.Bytes_Value and then E.Bytes_Valid (Payload, Observed.Payload) then
                     declare Observation : constant E.Bytes := E.Materialize (Payload, Observed.Payload); begin
                        return E.C.Scoped_Archive_JSON_Matches
                          (Observation, Data, (Observation'First, Observation'Length), Request) =
                            E.C.Typed_Tree_Matches_Source_Custody_Open and then
                          J.Same (Data, F (Data, Gate, "front_reread"), Request) and then
                          J.Socket_Matches (Data, F (Data, Gate, "front_socket"), Request) and then
                          Socket_Source (Data, F (Data, Gate, "front_socket"), Front_Source);
                     end;
                  end if;
                  if not Allow_Error or else not S.A.Valid (Payload, Error) or else
                     not AP.Scoped_Archive_Operation_Matches
                       (Data, Payload, F (Data, Gate, "reread_error"), Error, AP.Original_Image)
                  then return False; end if;
                  return Read_Failure_Joined
                    (F (Data, Gate, "reread_failure"), F (Data, Gate, "reread_error"),
                     F (Data, Earlier_Facts, "front_socket"), Front_Source);
               end;
            end Observation_Joined;
         begin
            if not Socket_Source (Data, F (Data, Gate, "channel"), Source) or else
               not Role_Socket (Data, F (Data, Gate, "channel"), F (Data, Gate, "channel_document"), Source) or else
               not Socket_Source (Data, F (Data, Gate, "front_channel"), Front_Source) or else
               not Role_Socket (Data, F (Data, Gate, "front_channel"),
                 F (Data, Gate, "front_channel_document"), Front_Source) or else
               not Frame_Stream_Joined (F (Data, Gate, "request_frame"), F (Data, Gate, "request_send"),
                 Source, F (Data, Gate, "channel"), True) or else
               not Frame_Stream_Joined (F (Data, Gate, "request_frame"), F (Data, Gate, "request_receive"),
                 Front_Source, F (Data, Gate, "front_channel"), False) or else
               not Frame_Stream_Joined (F (Data, Gate, "response_frame"), F (Data, Gate, "response_send"),
                 Front_Source, F (Data, Gate, "front_channel"), True) or else
               not Frame_Stream_Joined (F (Data, Gate, "response_frame"), F (Data, Gate, "response_receive"),
                 Source, F (Data, Gate, "channel"), False) or else
               not Frame_Valid (F (Data, Gate, "request_frame"), Request_Body, Gate, "GATE_REQUEST") or else
               not Frame_Valid (F (Data, Gate, "response_frame"), Response_Body, Gate, "GATE_RESPONSE") or else
               not (Echo ("generation") and then Echo ("reattach_epoch") and then Echo ("request") and then
                    Echo ("subgeneration") and then Echo ("operation") and then Echo ("gate") and then
                    Echo ("sequence") and then Echo ("nonce") and then Echo ("admission_head")) or else
               not Empty_Gate_Request or else
               not V.Valid_Text (Data, F (Data, Request_Body, "gate")) or else
               V.Text_Value (Data, F (Data, Request_Body, "gate"))'Length = 0 or else
               not Observation_Joined
            then return False; end if;
            return True;
         end Relay_Gate_Joined;
         function Relay_Transcript_Joined
           (Gates : E.Span; Current : E.Span; Has_Current : Boolean;
            Allow_Error : Boolean) return Boolean
         is
            Sequence : SPARK.Big_Integers.Big_Integer := SPARK.Big_Integers.To_Big_Integer (1);
         begin
            if not V.Is_Sequence (Data, Gates) then return False; end if;
            if V.Count (Data, Gates) > 0 then
               for I in E.Count range 0 .. V.Count (Data, Gates) - 1 loop
                  pragma Loop_Variant (Increases => I);
                  declare Gate : constant E.Span := V.Element (Data, Gates, I); begin
                     if not Relay_Gate_Joined (Gate, Allow_Error) or else
                        Decimal_Value (Data, F (Data, Gate, "sequence")) /= Sequence
                     then return False; end if;
                     if I > 0 and then (for some K in E.Count range 0 .. I - 1 =>
                        J.Same (Data, F (Data, Gate, "nonce"),
                          F (Data, V.Element (Data, Gates, K), "nonce")))
                     then return False; end if;
                     Sequence := Sequence + 1;
                  end;
               end loop;
            end if;
            if not Has_Current then return True; end if;
            if not Relay_Gate_Joined (Current, Allow_Error) or else
               Decimal_Value (Data, F (Data, Current, "sequence")) /= Sequence
            then return False; end if;
            if V.Count (Data, Gates) > 0 and then
               (for some I in E.Count range 0 .. V.Count (Data, Gates) - 1 =>
                  J.Same (Data, F (Data, Current, "nonce"),
                    F (Data, V.Element (Data, Gates, I), "nonce")))
            then return False; end if;
            return True;
         end Relay_Transcript_Joined;
         function Fresh_Roles_Joined (Scoped_Transfer : E.Span; Gate : E.Span := (1, 0))
            return Boolean
         is
            Raw_Evidence : constant E.Span := Value.Extras (Index).Subject_Evidence_Payload;
            Raw_Transfer : E.Span;
            List : constant E.Span := Value.Extras (Index).Native_Observations_Payload;
            function PF (Item : E.Span; Name : String) return E.Span is
              (CP.Raw_Source_Field (Data, Item, Name));
         begin
            if Value.Extras (Index).Subject_Evidence_Encoding /= L.Operation_Original or else
               not CP.Source_Record_Matches (Data, Facts, Raw_Evidence, True, False) then return False; end if;
            if Gate.Length = 0 then
               Raw_Transfer := PF (Raw_Evidence, "transfer");
            else
               declare Raw_Gate : E.Span := PF (Raw_Evidence, "serving_gate"); begin
                  if not CP.Source_Record_Matches (Data, Gate, Raw_Gate, True, False) then
                     Raw_Gate := (1, 0);
                     declare
                        Gates : constant E.Span := PF (PF (Raw_Evidence, "response"), "gates");
                        View : constant E.View := E.Decode (Data, Gates, E.Operation);
                     begin
                        if View.Form not in E.List_Value | E.Tuple_Value then return False; end if;
                        for N in E.Count range 1 .. E.Array_Length (Data, View.Children) loop
                           pragma Loop_Variant (Increases => N);
                           declare Item : constant E.Span := E.Array_Element (Data, View.Children, N - 1); begin
                              if CP.Source_Record_Matches (Data, Gate, Item, True, False) then
                                 if Raw_Gate.Length > 0 then return False; end if;
                                 Raw_Gate := Item;
                              end if;
                           end;
                        end loop;
                     end;
                  end if;
                  Raw_Transfer := PF (Raw_Gate, "transfer");
               end;
            end if;
            if not CP.Source_Record_Matches (Data, Scoped_Transfer, Raw_Transfer, True, False) or else
               Value.Extras (Index).Native_Observations_Encoding /= L.Operation_Original then return False; end if;
            for N in E.Count range 1 .. R.Archive_Length (Data, List) loop
               pragma Loop_Variant (Increases => N);
               declare
                  Item : constant E.Span := R.Archive_Index (Data, List, N - 1);
                  Role : constant E.Span := R.Archive_Field (Data, Item, "role");
                  Obs : constant E.Span := R.Archive_Field (Data, Item, "observation");
                  Material : constant E.Span := R.Archive_Field (Data, Item, "material");
                  Provenance : constant E.Span := R.Archive_Field (Data, Item, "provenance");
                  Subject_Capture : constant E.Span := PF (Provenance, "subject_capture");
                  Capture : E.Span := PF (Provenance, "owned_descriptor_roster");
               begin
                  if R.Archive_Text_Is (Data, Role, "root-admission") or else
                     R.Archive_Text_Is (Data, Role, "root-execution") then
                     if Capture.Length = 0 then Capture := PF (Provenance, "complete_scoped_capture"); end if;
                     if Capture.Length = 0 and then PF (Provenance, "packet").Length > 0 then Capture := Provenance; end if;
                     if Subject_Capture.Length > 0 and then
                        R.Root_Material_Matches (Data, Obs, Material) and then
                        R.Root_Capture_Matches (Data, Obs, Provenance) and then
                        CP.Scoped_Capture_Matches (Data, Obs, Provenance) and then
                        CP.Subject_Capture_Matches (Data, Subject_Capture,
                          PF (Capture, "inventory"), PF (Capture, "packet")) and then
                        Evolution.Subject_Roles_Match (Data, Data, Raw_Transfer,
                          PF (Subject_Capture, "inventory"))
                     then return True; end if;
                  end if;
               end;
            end loop;
            return False;
         end Fresh_Roles_Joined;
         function Fresh_Gate_Joined (Gate : E.Span; Allow_Error : Boolean := False) return Boolean is
         begin
            if not S.Text_Is (Data, F (Data, Gate, "mode"), "FRESH") or else
               not Socket_Source (Data, F (Data, Gate, "front_socket"), Front_Source)
            then return False; end if;
            if not Fresh_Roles_Joined (F (Data, Gate, "transfer"), Gate) then return False; end if;
            if Allow_Error and then V.Valid_Bytes (Data, F (Data, Gate, "reread_error")) then
               return J.Same (Data, F (Data, Gate, "transfer"), F (Data, Earlier_Facts, "transfer")) and then
                 Read_Failure_Joined (F (Data, Gate, "reread_failure"), F (Data, Gate, "reread_error"),
                   F (Data, Earlier_Facts, "worker_socket"), Source);
            end if;
            return Socket_Source (Data, F (Data, Gate, "worker_socket"), Source) and then
              J.Fresh_Matches (Data, Request, F (Data, Gate, "front_socket"),
                F (Data, Gate, "worker_socket"), F (Data, Gate, "transfer"));
         end Fresh_Gate_Joined;
         function Front_Gate_Joined (Gate : E.Span; Allow_Error : Boolean := True) return Boolean is
         begin
            if not S.Text_Is (Data, F (Data, Gate, "mode"), "FRONT") or else
               not V.Is_Null (Data, F (Data, Gate, "worker_socket")) or else
               not V.Is_Null (Data, F (Data, Gate, "transfer"))
            then return False; end if;
            if V.Valid_Bytes (Data, F (Data, Gate, "reread_error")) then
               return Allow_Error and then Read_Failure_Joined (F (Data, Gate, "reread_failure"), F (Data, Gate, "reread_error"),
                 F (Data, Earlier_Facts, "front_socket"), Source);
            end if;
            return J.Same (Data, F (Data, Gate, "front_reread"), Request) and then
              Socket_Source (Data, F (Data, Gate, "front_socket"), Source) and then
              J.Socket_Matches (Data, F (Data, Gate, "front_socket"), Request);
         end Front_Gate_Joined;
         function Response_Joined return Boolean is
            Response : constant E.Span := F (Data, Facts, "response");
            Bytes : constant E.Span := F (Data, Response, "bytes");
            Digest : constant E.Span := F (Data, Response, "sha256");
            Blob_Found : Boolean := False;
            function Response_Field (Name : String; Expected : E.Span) return Boolean is
               Body_Metadata : constant E.Span := F (Data, Response, "relay_body");
            begin
               if not V.Valid_Bytes (Data, F (Data, Body_Metadata, "payload")) then return False; end if;
               declare
                  Payload : constant E.Bytes := V.Bytes_Value (Data, F (Data, Body_Metadata, "payload"));
               begin
                  return AP.Scoped_Archive_Operation_Matches
                    (Data, Payload, Expected, S.A.Field (Payload, (Payload'First, Payload'Length), Name));
               end;
            end Response_Field;
         begin
            if not J.Digest_Matches (Data, Bytes, Digest) or else
               not Original_Matches (F (Data, Response, "original"), Index, "response") or else
               not Native_Gates (False, Decoded.Value.Appending_Actor = M.Worker) then return False; end if;
            for I in Value.Blob_SQL'Range (1) loop
               pragma Loop_Variant (Increases => I);
               if Value.Blob_SQL (I, 1).Kind = L.S.SQL_Text and then
                  S.Text_Matches (Data, Digest,
                    (Value.Blob_SQL (I, 1).Bytes.First, Value.Blob_SQL (I, 1).Bytes.Length)) and then
                  Value.Blob_SQL (I, 2).Kind = L.S.SQL_Text and then
                  Value.Blob_SQL (I, 3).Kind = L.S.SQL_Blob and then
                  Bytes_Span (Data, Bytes,
                    (Value.Blob_SQL (I, 3).Bytes.First, Value.Blob_SQL (I, 3).Bytes.Length))
               then
                  if L.S.Text_Is (Data, Value.Blob_SQL (I, 2), "RESPONSE") then Blob_Found := True; end if;
               end if;
            end loop;
            if not Blob_Found or else not J.Same_Bytes (Data, Bytes, F (Data, Response, "blob")) then return False; end if;
            declare
               Line : constant E.Bytes := V.Bytes_Value (Data, Bytes);
            begin
               if Line'Length = 0 or else Line (Line'Last) /= 10 or else
                  E.C.Scoped_Archive_JSON_Matches (Line, Data,
                    (Line'First, Line'Length - 1), F (Data, Response, "original")) /=
                      E.C.Typed_Tree_Matches_Source_Custody_Open
               then return False; end if;
            end;
            if Subject.Present and then Subject.Value.Mode = M.Relay then
               return Relay_Transcript_Joined (F (Data, Response, "gates"), (1, 0), False, True) and then
                 Frame_Valid (F (Data, Response, "relay"), F (Data, Response, "relay_body"),
                   F (Data, Response, "relay_body"), "RESPONSE_BYTES") and then
                 Response_Field ("line", Bytes) and then Response_Field ("sha256", Digest) and then
                 Response_Field ("out_seq", F (Data, F (Data, Response, "relay_body"), "sequence"));
            end if;
            declare Gates : constant E.Span := F (Data, Response, "gates"); begin
               if not V.Is_Sequence (Data, Gates) then return False; end if;
               if V.Count (Data, Gates) > 0 and then
                  (for some I in E.Count range 0 .. V.Count (Data, Gates) - 1 =>
                     not (if Decoded.Value.Appending_Actor = M.Front then
                            Front_Gate_Joined (V.Element (Data, Gates, I))
                          else Fresh_Gate_Joined (V.Element (Data, Gates, I), True)))
               then return False; end if;
               return V.Is_Null (Data, F (Data, Response, "relay"));
            end;
         end Response_Joined;
      begin
         if Decoded.Status /= D.Decoded or else
            Decoded.Value.Kind_Of_Subject not in M.Request | M.Descriptor or else
            Value.Extras (Index).Original_Encoding = L.No_Original or else not S.Valid (Data, Facts) or else
            not S.Text_Is (Data, F (Data, X5, "schema"), "worldline.custody-x5-event-v2") or else
            not S.Text_Is (Data, F (Data, Facts, "schema"), "worldline.custody-subject-raw-v1") or else
            not (Field_Bound ("generation") and then Field_Bound ("operation") and then
                 Field_Bound ("subject") and then Field_Bound ("subgeneration")) or else
            not J.Same (Data, F (Data, Binding, "source"), Source) or else
            not J.Same (Data, F (Data, Binding, "actor"), Actor) or else
            not V.Is_Integer (Data, F (Data, Actor, "pid")) or else
            not V.Is_Integer (Data, F (Data, Actor, "start_tick")) or else
            RE.Number (Data, F (Data, Actor, "pid")) <= 0 or else
            RE.Number (Data, F (Data, Actor, "start_tick")) < 0 or else
            RE.Stat_Field (Data, F (Data, Actor, "stat"), 1) /= RE.Number (Data, F (Data, Actor, "pid")) or else
            RE.Stat_Field (Data, F (Data, Actor, "stat"), 22) /= RE.Number (Data, F (Data, Actor, "start_tick")) or else
            not J.Same_Bytes (Data, F (Data, Binding, "sender_credentials"), F (Data, Actor, "credentials")) or else
            not Original_Image_Joined
         then return False; end if;
         Root_Index := Prior (F (Data, Binding, "root_head"), Before.Head, True);
         if Root_Index = 0 then return False; end if;
         if Subject.Present then
            Subject_Index := Prior (F (Data, Binding, "subject_head"), Subject.Value.Head, False);
            if Subject_Index = 0 or else not
               (for some I in Subjects'Range =>
                  Subjects (I).Kind = Subject.Value.Kind and then
                  M.L.Same (Data, Subjects (I).Subject, Subject.Value.Subject) and then
                  Q.Compare (Data, Subjects (I).Generation, Subject.Value.Generation) = Q.Equal and then
                  Subjects (I).Head = Subject.Value.Head and then
                  (for all K in Subjects'Range =>
                     (if K /= I then not (Subjects (K).Kind = Subjects (I).Kind and then
                      M.L.Same (Data, Subjects (K).Subject, Subjects (I).Subject) and then
                      Q.Compare (Data, Subjects (K).Generation, Subjects (I).Generation) = Q.Equal))))
            then return False; end if;
         elsif not V.Is_Null (Data, F (Data, Binding, "subject_head")) then return False;
         end if;
         if Output_Query then
            declare
               Emitter : constant E.Span := F (Data, X5, "emitter");
            begin
               -- Allocation observes authentic production context only. No
               -- proposed-kind/from-phase clause or RootReady consequence is
               -- inferred from it; append and original serving gates remain
               -- separate. The same full private proof binds native current
               -- source/root/subject histories, including Before's epoch.
               if not Subject.Present or else Subject.Value.Kind /= M.Request or else
                  Decoded.Value.Kind_Of_Subject /= M.Request or else
                  Decoded.Value.Appending_Actor not in M.Front | M.Worker or else
                  not M.L.Same (Data, Decoded.Value.Subject, Subject.Value.Subject) or else
                  Q.Compare (Data, Decoded.Value.Generation, Before.Generation) /= Q.Equal or else
                  Q.Compare (Data, Decoded.Value.Generation, Subject.Value.Generation) /= Q.Equal or else
                  Q.Compare (Data, Decoded.Value.Subgeneration, Subject.Value.Subgeneration) /= Q.Equal or else
                  not Same_Initial_Request or else not Native_Gates (False, False)
               then return False; end if;
               if Output_Context_Only then return True; end if;
               if not V.Valid_Hex_Field (Data, Emitter, "records") or else
                  not V.Valid_Hex_Field (Data, Emitter, "candidate")
               then return False; end if;
               declare
                  Records : constant E.Bytes := V.Hex_Value (Data, Emitter, "records");
                  Candidate : constant E.Bytes := V.Hex_Value (Data, Emitter, "candidate");
                  Records_Image : constant E.Span := (Records'First, Records'Length);
                  Candidate_Image : constant E.Span := (Candidate'First, Candidate'Length);
                  Scope : constant E.Span := R.Archive_Field (Candidate, Candidate_Image, "scope");
                  Admission : constant E.Span := R.Archive_Field (Candidate, Candidate_Image, "admission_head");
                  Scope_View : constant E.View := E.Decode (Candidate, Scope, E.Operation);
                  function Admission_Joined return Boolean is
                     Found : Boolean := False;
                  begin
                     for I in Value.Events'First .. Index - 1 loop
                        pragma Loop_Variant (Increases => I);
                        declare Admitted : constant D.Decoded_Event := D.Decode (Data, Value.Events (I)); begin
                           if Admitted.Status = D.Decoded and then Admitted.Value.Kind_Of_Subject = M.Request and then
                              Admitted.Value.Kind =
                                (if Decoded.Value.Appending_Actor = M.Front then M.Request_Queued_Event else M.Request_Intake_Event) and then
                              Q.Compare (Data, Admitted.Value.Generation, Subject.Value.Generation) = Q.Equal and then
                              Q.Compare (Data, Admitted.Value.Subgeneration, Subject.Value.Subgeneration) = Q.Equal and then
                              M.L.Same (Data, Admitted.Value.Subject, Subject.Value.Subject) and then
                              Raw_Same (Data, Value.Events (I).Operation, Raw.Operation) and then
                              Archive_Text_Matches (Data, Candidate, Value.Events (I).Event_Id, Admission)
                           then
                              if Found then return False; end if;
                              Found := True;
                           end if;
                        end;
                     end loop;
                     return Found;
                  end Admission_Joined;
               begin
                  return S.A.Valid (Records, Records_Image) and then
                    E.Decode (Records, Records_Image, E.Operation).Form = E.Tuple_Value and then
                    S.A.Valid (Candidate, Candidate_Image) and then
                    Scope_View.Form = E.Object_Value and then E.Array_Length (Candidate, Scope_View.Children) = 6 and then
                    Archive_Quantity_Matches (Data, Candidate,
                      R.Archive_Field (Candidate, Scope, "generation"), Before.Generation) and then
                    Archive_Quantity_Matches (Data, Candidate,
                      R.Archive_Field (Candidate, Scope, "subgeneration"), Subject.Value.Subgeneration) and then
                    Archive_Quantity_Matches (Data, Candidate,
                      R.Archive_Field (Candidate, Scope, "reattach_epoch"), Before.Reattach_Epoch) and then
                    (if Before.Operation.Present then
                       Archive_Text_Matches (Data, Candidate, Value.Events (Root_Index).Operation,
                         R.Archive_Field (Candidate, Scope, "root_operation"))
                     else R.Archive_Is_None (Candidate, R.Archive_Field (Candidate, Scope, "root_operation"))) and then
                    Archive_Text_Matches (Data, Candidate, Raw.Operation,
                      R.Archive_Field (Candidate, Scope, "operation")) and then
                    Archive_Text_Matches (Data, Candidate, Raw.Subject,
                      R.Archive_Field (Candidate, Scope, "request")) and then Admission_Joined and then
                    AP.Scoped_Archive_Operation_Matches (Data, Candidate, Source,
                      R.Archive_Field (Candidate, Candidate_Image, "source")) and then
                    AP.Scoped_Archive_Operation_Matches (Data, Candidate,
                      F (Data, Request, "observationId"),
                      R.Archive_Field (Candidate, Candidate_Image, "request"));
               end;
            end;
         end if;
         if Serving_Query then
            declare Gate : constant E.Span := F (Data, Facts, "serving_gate"); begin
               if not Subject.Present or else Subject.Value.Kind /= M.Request or else
                  Decoded.Value.Kind /= M.Request_Responded_Event or else
                  Q.Compare (Data, Decoded.Value.Generation, Subject.Value.Generation) /= Q.Equal or else
                  Q.Compare (Data, Decoded.Value.Subgeneration, Subject.Value.Subgeneration) /= Q.Equal or else
                  not Same_Initial_Request
               then return False; end if;
               if Decoded.Value.Appending_Actor = M.Front then
                  return Subject.Value.Request = M.Queued and then
                    Native_Gates (False, False) and then Front_Gate_Joined (Gate, False);
               end if;
               if Decoded.Value.Appending_Actor /= M.Worker or else
                  Subject.Value.Request /= M.Intake or else
                  not P.Transfer_Root_Clause (Before) or else not Root_Custody_ACK or else
                  not Native_Gates
               then return False; end if;
               if Subject.Value.Mode = M.Relay then
                  return S.Text_Is (Data, F (Data, Gate, "mode"), "RELAY") and then
                    Relay_Transcript_Joined (F (Data, Gate, "history"), Gate, True, False);
               elsif Subject.Value.Mode = M.Fresh then
                  return Fresh_Gate_Joined (Gate);
               end if;
               return False;
            end;
         end if;
         case Decoded.Value.Kind is
            when M.Request_Queued_Event =>
               return Original_Request and then J.Socket_Matches (Data, Front, Request) and then
                 Socket_Source (Data, Front, Source) and then V.Is_Null (Data, Worker);
            when M.Request_Transfer_Intent_Event =>
               if not Same_Initial_Request or else not J.Socket_Matches (Data, Front, Request) or else
                  not Socket_Source (Data, Front, Source) or else Value.Extras (Index).Transfer_Mode.Kind /= L.S.SQL_Text or else
                  not S.Text_Matches (Data, F (Data, Transfer, "mode"),
                    (Value.Extras (Index).Transfer_Mode.Bytes.First, Value.Extras (Index).Transfer_Mode.Bytes.Length))
               then return False; end if;
               if S.Text_Is (Data, F (Data, Transfer, "mode"), "FRESH") then
                  return Original_Matches (F (Data, Transfer, "roster"), Index, "socket_roster") and then
                    Roles_Joined (Data, F (Data, Transfer, "roles"), F (Data, Transfer, "roster"), Source, Source, False) and then
                    V.Is_Null (Data, Relay);
               elsif S.Text_Is (Data, F (Data, Transfer, "mode"), "RELAY") then
                  return V.Is_Null (Data, Worker) and then Relay_Admission_Joined;
               end if;
               return False;
            when M.Request_Intake_Event =>
               if not Same_Initial_Request or else not Root_Custody_ACK or else not Native_Gates or else
                  D.Decode (Data, Value.Events (Subject_Index)).Value.Kind /= M.Request_Transfer_Intent_Event or else
                  not J.Same (Data, F (Data, Transfer, "mode"), F (Data, F (Data, Earlier_Facts, "transfer"), "mode"))
               then return False; end if;
               if S.Text_Is (Data, F (Data, Transfer, "mode"), "FRESH") then
                  return J.Fresh_Matches (Data, Request, Front, Worker, Transfer) and then
                    Socket_Source (Data, Front, Front_Source) and then Socket_Source (Data, Worker, Source) and then
                    Transfer_Sent and then Original_Matches (F (Data, Transfer, "roster"), Index, "socket_roster") and then
                    Fresh_Roles_Joined (Transfer);
               elsif S.Text_Is (Data, F (Data, Transfer, "mode"), "RELAY") then
                  return V.Is_Null (Data, Worker) and then Relay_Admission_Joined;
               end if;
               return False;
            when M.Request_Abandon_Event =>
               return Same_Initial_Request and then
                 Original_Matches (F (Data, Transfer, "roster"), Index, "socket_roster") and then
                 Original_Matches (F (Data, Transfer, "roster"), Subject_Index, "socket_roster") and then
                 J.Same (Data, Transfer, F (Data, Earlier_Facts, "transfer"));
            when M.Request_Responded_Event =>
               return Same_Initial_Request and then Response_Joined;
            when M.Request_Lost_Event =>
               return Same_Initial_Request and then
                 (not Require_Worker_Gone or else RE.Worker_Gone (Value, Index, Before));
            when M.Drain_Stop_Intent_Event =>
               return Live_Descriptor and then Acquisitions_Joined and then
                 Identity (Data, F (Data, Drain, "descriptor_identity"), F (Data, Descriptor, "identity")) and then
                 Spool (Data, Drain, Source, Actor, False).Joined;
            when M.Drain_Freeze_Event =>
               declare
                  Frozen : constant Spool_Result := Spool (Data, Drain, Source, Actor, True);
               begin
                  return Same_Initial_Descriptor and then Frozen.Joined and then
                    Acquisitions_Joined and then Spool_Prefix_Joined and then
                    Identity (Data, F (Data, Drain, "descriptor_identity"), F (Data, Descriptor, "identity")) and then
                    Cell_Count (Data, Value.Extras (Index).Position, Frozen.Position);
               end;
            when M.Drain_Ofd_Evidence_Event =>
               return Same_Initial_Descriptor and then Transfer_Sent and then Worker_Report_Joined and then
                 Roles_Joined (Data, F (Data, F (Data, Facts, "ofd"), "roles"),
                   F (Data, Descriptor, "roster"), Receive_Source, Front_Source, True) and then
                 Original_Matches (F (Data, Descriptor, "roster"), Index, "live_roster") and then
                 Original_Matches (F (Data, F (Data, Facts, "ofd"), "worker_report"), Index, "worker_report", AP.Original_Image);
            when M.Drain_Intake_Event =>
               return Same_Initial_Descriptor and then Root_Custody_ACK and then
                 D.Decode (Data, Value.Events (Subject_Index)).Value.Kind = M.Drain_Ofd_Evidence_Event and then
                 J.Same (Data, F (Data, Facts, "ofd"), F (Data, Earlier_Facts, "ofd")) and then
                 Original_Matches (F (Data, F (Data, Facts, "ofd"), "worker_report"), Index, "worker_report", AP.Original_Image) and then
                 Original_Matches (F (Data, F (Data, Facts, "ofd"), "worker_report"), Subject_Index, "worker_report", AP.Original_Image) and then
                 Worker_Report_Joined and then Native_Gates;
            when M.Drain_Abandon_Event =>
               return Same_Initial_Descriptor and then Subject.Present and then
                 Value.Extras (Index).Next_Subgeneration.Kind = L.S.SQL_Blob and then
                 M.L.T.Is_Successor (Data, Subject.Value.Subgeneration,
                   (Negative => False, First => Value.Extras (Index).Next_Subgeneration.Bytes.First,
                    Length => Value.Extras (Index).Next_Subgeneration.Bytes.Length));
            when M.Drain_Released_Event =>
               declare
                  Close : constant E.Span := F (Data, Facts, "close");
                  Readback : constant E.Span := F (Data, Close, "readback");
               begin
                  return Same_Initial_Descriptor and then
                    S.Text_Is (Data, F (Data, Close, "call"), "close") and then
                    S.Text_Is (Data, F (Data, Readback, "call"), "fstat") and then
                    J.Same (Data, F (Data, Close, "fd"), F (Data, Descriptor, "fd")) and then
                    J.Integer_Is (Data, F (Data, Close, "result"), 0) and then
                    J.Integer_Is (Data, F (Data, Close, "errno"), 0) and then
                    J.Same (Data, F (Data, Close, "source"), Source) and then
                    J.Same (Data, F (Data, Readback, "fd"), F (Data, Close, "fd")) and then
                    J.Integer_Is (Data, F (Data, Readback, "result"), -1) and then
                    J.Integer_Is (Data, F (Data, Readback, "errno"), 9) and then
                    J.Same (Data, F (Data, Readback, "source"), Source);
               end;
            when M.Drain_Reclaimed_Event =>
               return Same_Initial_Descriptor and then
                 (not Require_Worker_Gone or else RE.Worker_Gone (Value, Index, Before));
            when others => return False;
         end case;
      end;
   end Primitive_Joined;
   function Primitive_Reference
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject)
      return Boolean is
     (Primitive_Joined (Value, Index, Before, Subjects, Subject, True));
   function Serving_Reference
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject)
      return Boolean is
     (Primitive_Joined (Value, Index, Before, Subjects, Subject, True, True));
   function Serving_Join
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof)
      return Join_Status is
     (if Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Index, Proof) and then
         Serving_Reference (Value, Index, Before, Subjects, Subject)
      then Evidence_Joined else Evidence_Refused);
   function Output_Reference
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof)
      return Boolean is
     (Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Index, Proof) and then
      Primitive_Joined (Value, Index, Before, Subjects, Subject, True, False, True));
   function Output_Context_Reference
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof)
      return Boolean is
     (Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Index, Proof) and then
      Primitive_Joined (Value, Index, Before, Subjects, Subject, True, False, True, True));
   function Cleanup_Kind_Of
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subject : P.Optional_Subject;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof)
      return Cleanup_Kind
   is
   begin
      if not Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Index, Proof) then
         return Retain_Unknown;
      end if;
      if not Subject.Present then return No_Event; end if;
      declare
         Candidate : constant D.Decoded_Event := D.Decode (Value.Arena, Value.Events (Index));
         Kind : constant M.Event_Kind :=
           (if Subject.Value.Kind = M.Request then M.Request_Lost_Event
            else M.Drain_Reclaimed_Event);
      begin
         if Candidate.Status /= D.Decoded or else Subject.Value.Kind = M.Root or else
            Candidate.Value.Kind /= Kind or else
            Candidate.Value.Kind_Of_Subject /= Subject.Value.Kind or else
            not M.L.Same (Value.Arena, Candidate.Value.Subject, Subject.Value.Subject) or else
            Q.Compare (Value.Arena, Candidate.Value.Generation, Subject.Value.Generation) /= Q.Equal or else
            Q.Compare (Value.Arena, Candidate.Value.Subgeneration, Subject.Value.Subgeneration) /= Q.Equal or else
            not (if Subject.Value.Kind = M.Request then
                   P.Request_Fixed_Actor_Clause (Subject, Kind, Candidate.Value.Appending_Actor)
                 else P.Descriptor_Fixed_Actor_Clause (Kind, Candidate.Value.Appending_Actor)) or else
            not Primitive_Joined (Value, Index, Before, (1 => Subject.Value), Subject, False)
         then return Retain_Unknown; end if;
         if not (if Subject.Value.Kind = M.Request then P.Request_From_Clause (Subject, Kind)
                 else P.Descriptor_From_Clause (Subject, Kind))
         then return No_Event; end if;
         case RE.Worker_Liveness_Of (Value, Index, Before) is
            when RE.Known_Live => return No_Event;
            when RE.Uncertain => return Retain_Unknown;
            when RE.Known_Gone => null;
         end case;
         return (if Subject.Value.Kind = M.Request then Request_Lost else Drain_Reclaimed);
      end;
   end Cleanup_Kind_Of;
   function Join
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject)
      return Join_Status is
     (if Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Index) and then
         Primitive_Reference (Value, Index, Before, Subjects, Subject)
      then Evidence_Joined else Evidence_Refused);
   function Join
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof)
      return Join_Status is
     (if Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Index, Proof) and then
         Primitive_Reference (Value, Index, Before, Subjects, Subject)
      then Evidence_Joined else Evidence_Refused);
end Worldline.Custody_V2_Subject_Evidence;
