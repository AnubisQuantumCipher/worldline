with Worldline.Archive_Base64;
with Worldline.Recovery_Archive;
with Worldline.Scoped_Capture_Projection;
with Worldline.Scoped_Capture_Namespace_Projection;

package body Worldline.Scoped_Capture_Evolution_Projection with SPARK_Mode is
   package RA renames Worldline.Recovery_Archive;
   package B64 renames Worldline.Archive_Base64;
   package P renames Worldline.Scoped_Capture_Projection;
   package N renames Worldline.Scoped_Capture_Namespace_Projection;
   use type E.Count;
   use type E.Span;
   use type E.Value_Kind;
   use type E.Q.Byte;
   use type E.Encoding_Level;
   Empty : constant E.Span := (1, 0);
   function Valid (Data : E.Bytes; Item : E.Span) return Boolean is
     (RA.Source_Valid (Data, Item, False));
   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span renames P.Raw_Source_Field;
   function Same (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (RA.Ordered_Source_Value_Matches (Data, Data, Left, Right, False, False));
   function SF (Data : E.Bytes; Left, Right : E.Span; Name : String) return Boolean is
     (Same (Data, F (Data, Left, Name), F (Data, Right, Name)));
   function Bytes_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      return Valid (Data, Item) and then View.Form = E.Bytes_Value and then View.Payload.Level = 1
        and then B64.Canonical (Data, (View.Payload.Encoded.First, View.Payload.Encoded.Length));
   end Bytes_Valid;
   function Byte_Count (Data : E.Bytes; Item : E.Span) return E.Count is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      return (if Bytes_Valid (Data, Item) then
        E.Count (B64.Decoded_Length (Data, (View.Payload.Encoded.First, View.Payload.Encoded.Length))) else 0);
   end Byte_Count;
   function Source_Bytes (Data : E.Bytes; Item : E.Span) return E.Bytes is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
      Result : E.Bytes (1 .. Byte_Count (Data, Item));
   begin
      for I in Result'Range loop
         Result (I) := B64.Decoded_Byte (Data, (View.Payload.Encoded.First, View.Payload.Encoded.Length), I - 1);
      end loop;
      return Result;
   end Source_Bytes;
   function Image_Matches (Data : E.Bytes; Image, Value : E.Span) return Boolean is
   begin
      if not Bytes_Valid (Data, Image) then return False; end if;
      declare Raw : constant E.Bytes := Source_Bytes (Data, Image); begin
         return RA.Ordered_Source_Value_Matches (Raw, Data, (Raw'First, Raw'Length), Value, False, False);
      end;
   end Image_Matches;
   function Text (Data : E.Bytes; Item : E.Span; Word : String) return Boolean is
     (Valid (Data, Item) and then E.Text_Is (Data, E.Decode (Data, Item, E.Operation), Word));
   function Is_None (Data : E.Bytes; Item : E.Span) return Boolean is
     (Valid (Data, Item) and then E.Decode (Data, Item, E.Operation).Form = E.Null_Value);
   function Seq (Data : E.Bytes; Item : E.Span) return Boolean is
     (Valid (Data, Item) and then E.Decode (Data, Item, E.Operation).Form in E.Tuple_Value | E.List_Value);
   function Len (Data : E.Bytes; Item : E.Span) return E.Count is
     (if Seq (Data, Item) then E.Array_Length (Data, E.Decode (Data, Item, E.Operation).Children) else 0);
   function Item (Data : E.Bytes; Items : E.Span; Index : E.Count) return E.Span is
     (if Seq (Data, Items) then E.Array_Element (Data, E.Decode (Data, Items, E.Operation).Children, Index) else Empty);
   function Members (Data : E.Bytes; Object : E.Span) return E.Span is
     (if Valid (Data, Object) and then E.Decode (Data, Object, E.Operation).Form = E.Object_Value
      then E.Decode (Data, Object, E.Operation).Children else Empty);
   function Width (Data : E.Bytes; Object : E.Span; Count : E.Count) return Boolean is
     (Valid (Data, Object) and then E.Decode (Data, Object, E.Operation).Form = E.Object_Value
      and then E.Array_Length (Data, Members (Data, Object)) = Count);
   function Key (Data : E.Bytes; Object : E.Span; Index : E.Count) return E.Span is
     (E.Array_Element (Data, E.Decode (Data, E.Array_Element (Data, Members (Data, Object), Index), E.Finalization).Children, 0));
   function Value (Data : E.Bytes; Object : E.Span; Index : E.Count) return E.Span is
     (E.Array_Element (Data, E.Decode (Data, E.Array_Element (Data, Members (Data, Object), Index), E.Finalization).Children, 1));
   function Lookup (Data : E.Bytes; Object, Name : E.Span) return E.Span is
      Found : E.Span := Empty;
   begin
      for I in E.Count range 1 .. E.Array_Length (Data, Members (Data, Object)) loop
         if Same (Data, Key (Data, Object, I - 1), Name) then
            if Found.Length > 0 then return Empty; end if;
            Found := Value (Data, Object, I - 1);
         end if;
      end loop;
      return Found;
   end Lookup;
   --  All callers compare actual syscall constants, not bounded input values.
   function Number_Is (Data : E.Bytes; Number : E.Span; Expected : Integer) return Boolean is
      View : constant E.View := E.Decode (Data, Number, E.Operation);
      Encoded : constant B64.Span := (View.Payload.Encoded.First, View.Payload.Encoded.Length);
   begin
      if not Valid (Data, Number) or else View.Form /= E.Integer_Value
        or else View.Sign /= (Expected < 0) or else View.Payload.Level /= 1
        or else not B64.Canonical (Data, Encoded) then return False; end if;
      --  Integer payloads in all three original archive layers are canonical
      --  base64 magnitudes. Compare syscall literals without copying them.
      case Expected is
         when 0 => return B64.Decoded_Length (Data, Encoded) = 0;
         when -1 | 6 | 9 | 15 =>
            return B64.Decoded_Length (Data, Encoded) = 1
              and then Integer (B64.Decoded_Byte (Data, Encoded, 0)) = abs Expected;
         when others => return False;
      end case;
   end Number_Is;
   function FD (Data : E.Bytes; Number : E.Span) return Boolean is
     (Valid (Data, Number) and then E.Decode (Data, Number, E.Operation).Form = E.Integer_Value
      and then not E.Decode (Data, Number, E.Operation).Sign);
   function Identity (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (SF (Data, Left, Right, "device") and then SF (Data, Left, Right, "inode")
      and then SF (Data, Left, Right, "mode") and then SF (Data, Left, Right, "uid") and then SF (Data, Left, Right, "gid"));
   --  fdinfo/position may change; the original custody identity is precisely
   --  these five fields. Complete current fdinfo remains available to kernels.
   function Descriptor_Maps_Match (Data : E.Bytes; Left, Right : E.Span) return Boolean is
   begin
      if E.Decode (Data, Left, E.Operation).Form /= E.Object_Value
        or else E.Decode (Data, Right, E.Operation).Form /= E.Object_Value
        or else E.Array_Length (Data, Members (Data, Left)) /= E.Array_Length (Data, Members (Data, Right)) then return False; end if;
      for I in E.Count range 1 .. E.Array_Length (Data, Members (Data, Left)) loop
         if not Identity (Data, Value (Data, Left, I - 1), Lookup (Data, Right, Key (Data, Left, I - 1))) then return False; end if;
      end loop;
      return True;
   end Descriptor_Maps_Match;
   function Role_Name (Index : Positive) return String is
     (case Index is when 1 => "listener", when 2 => "supervisor_channel", when 3 => "worker_namespace",
      when 4 => "namespace_pidfd", when 5 => "helper_pidfd", when 6 => "worker_pidfd", when 7 => "actor_pidfd",
      when 8 => "credential_receiver", when 9 => "custody_channel", when 10 => "stdout_fd",
      when 11 => "stderr_fd", when 12 => "stdin_fd", when 13 => "retained_peer",
      when 14 => "helper_namespace", when others => "cgroup");
   function Find (Data : E.Bytes; Items : E.Span; Field : String; Wanted : E.Span) return E.Span is
      Found : E.Span := Empty;
   begin
      for I in E.Count range 1 .. Len (Data, Items) loop
         declare Candidate : constant E.Span := Item (Data, Items, I - 1); begin
            if Same (Data, F (Data, Candidate, Field), Wanted) then
               if Found.Length > 0 then return Empty; end if;
               Found := Candidate;
            end if;
         end;
      end loop;
      return Found;
   end Find;
   function Find_Row (Data : E.Bytes; Rows, Bound : E.Span) return E.Span is
      Found : E.Span := Empty;
   begin
      for I in E.Count range 1 .. Len (Data, Rows) loop
         declare Candidate : constant E.Span := Item (Data, Rows, I - 1); begin
            if Same (Data, F (Data, F (Data, Candidate, "row"), "bound"), Bound) then
               if Found.Length > 0 then return Empty; end if;
               Found := Candidate;
            end if;
         end;
      end loop;
      return Found;
   end Find_Row;
   function Locks_Match (Data : E.Bytes; Left, Right : E.Span) return Boolean is
   begin
      if not Seq (Data, Left) or else not Seq (Data, Right) or else Len (Data, Left) /= Len (Data, Right) then return False; end if;
      for I in E.Count range 1 .. Len (Data, Left) loop
         declare Old : constant E.Span := Item (Data, Left, I - 1);
           Current : constant E.Span := Find (Data, Right, "descriptor", F (Data, Old, "descriptor")); begin
            if not Same (Data, Old, Find (Data, Left, "descriptor", F (Data, Old, "descriptor")))
              or else not SF (Data, Old, Current, "path") or else not Identity (Data, F (Data, Old, "identity"), F (Data, Current, "identity")) then return False; end if;
         end;
      end loop;
      return True;
   end Locks_Match;
   function Physical_Roles_Match (Data : E.Bytes; Left, Right : E.Span) return Boolean is
   begin
      if not Seq (Data, Left) or else not Seq (Data, Right) or else Len (Data, Left) /= Len (Data, Right) then return False; end if;
      for I in E.Count range 1 .. Len (Data, Left) loop
         declare
            L : constant E.Span := Item (Data, Left, I - 1);
            R : constant E.Span := Item (Data, Right, I - 1);
         begin
            if not SF (Data, L, R, "role") or else not SF (Data, L, R, "front_fd")
              or else not SF (Data, L, R, "worker_fd") or else not SF (Data, L, R, "origin")
              or else not SF (Data, L, R, "front_actor") or else not SF (Data, L, R, "worker_pidfd")
              or else not SF (Data, L, R, "lock_path")
              or else not Identity (Data, F (Data, L, "current"), F (Data, R, "current"))
              or else not SF (Data, F (Data, L, "fstat"), F (Data, R, "fstat"), "fd")
              or else not SF (Data, F (Data, L, "fstat"), F (Data, R, "fstat"), "args")
              or else not SF (Data, F (Data, L, "fstat"), F (Data, R, "fstat"), "call")
              or else not SF (Data, F (Data, L, "fstat"), F (Data, R, "fstat"), "result")
              or else not SF (Data, F (Data, L, "fstat"), F (Data, R, "fstat"), "errno")
              or else not SF (Data, F (Data, L, "fstat"), F (Data, R, "fstat"), "source") then return False; end if;
         end;
      end loop;
      return True;
   end Physical_Roles_Match;
   function Scoped_Name (Left_Data, Right_Data : E.Bytes; Root_Name, Scoped : E.Span) return Boolean is
      Left : constant E.View := E.Decode (Left_Data, Root_Name, E.Operation);
      Right : constant E.View := E.Decode (Right_Data, Scoped, E.Operation);
      Prefix : constant String := "scoped/";
      L : constant B64.Span := (Left.Payload.Encoded.First, Left.Payload.Encoded.Length);
      R : constant B64.Span := (Right.Payload.Encoded.First, Right.Payload.Encoded.Length);
   begin
      if not Valid (Left_Data, Root_Name) or else not Valid (Right_Data, Scoped)
        or else Left.Form /= E.Text_Value or else Right.Form /= E.Text_Value
        or else Left.Payload.Level /= 1 or else Right.Payload.Level /= 1
        or else not B64.Canonical (Left_Data, L) or else not B64.Canonical (Right_Data, R)
        or else B64.Decoded_Length (Left_Data, L) /= Prefix'Length + B64.Decoded_Length (Right_Data, R)
      then return False; end if;
      for I in E.Count range 0 .. Prefix'Length - 1 loop
         if B64.Decoded_Byte (Left_Data, L, I) /= E.Q.Byte (Character'Pos (Prefix (Prefix'First + Natural (I)))) then return False; end if;
      end loop;
      for I in E.Count range 1 .. E.Count (B64.Decoded_Length (Right_Data, R)) loop
         if B64.Decoded_Byte (Left_Data, L, Prefix'Length + I - 1) /= B64.Decoded_Byte (Right_Data, R, I - 1) then return False; end if;
      end loop;
      return True;
   end Scoped_Name;
   function Receipt_Part_Matches (Data : E.Bytes; Part, Receipt : E.Span) return Boolean is
   begin
      if not Valid (Data, Receipt) or else not Width (Data, Part, E.Array_Length (Data, Members (Data, Receipt)) + 1)
        or else not Same (Data, F (Data, Part, "raw"), F (Data, Receipt, "frame")) then return False; end if;
      for I in E.Count range 1 .. E.Array_Length (Data, Members (Data, Receipt)) loop
         if not Same (Data, Value (Data, Receipt, I - 1), Lookup (Data, Part, Key (Data, Receipt, I - 1))) then return False; end if;
      end loop;
      return True;
   end Receipt_Part_Matches;
   function Count_Is (Data : E.Bytes; Number : E.Span; Expected : E.Count) return Boolean is
      View : constant E.View := E.Decode (Data, Number, E.Operation);
      Encoded : constant B64.Span := (View.Payload.Encoded.First, View.Payload.Encoded.Length);
      Remaining : E.Count := Expected;
   begin
      if not Valid (Data, Number) or else View.Form /= E.Integer_Value or else View.Sign
        or else View.Payload.Level /= 1 or else not B64.Canonical (Data, Encoded) then return False; end if;
      for I in reverse E.Count range 1 .. E.Count (B64.Decoded_Length (Data, Encoded)) loop
         if E.Count (B64.Decoded_Byte (Data, Encoded, I - 1)) /= Remaining mod 256 then return False; end if;
         Remaining := Remaining / 256;
      end loop;
      return Remaining = 0;
   end Count_Is;
   function Joined_Bytes (Data : E.Bytes; Joined, Parts : E.Span; Field : String) return Boolean is
      View : constant E.View := E.Decode (Data, Joined, E.Operation);
      Encoded : constant B64.Span := (View.Payload.Encoded.First, View.Payload.Encoded.Length);
      Position : E.Count := 0;
      Total : constant E.Count := Byte_Count (Data, Joined);
   begin
      if not Bytes_Valid (Data, Joined) or else not Seq (Data, Parts) then return False; end if;
      for I in E.Count range 1 .. Len (Data, Parts) loop
         declare
            Part : constant E.Span := F (Data, Item (Data, Parts, I - 1), Field);
            V : constant E.View := E.Decode (Data, Part, E.Operation);
            Payload : constant B64.Span := (V.Payload.Encoded.First, V.Payload.Encoded.Length);
            Size : constant E.Count := Byte_Count (Data, Part);
         begin
            if not Bytes_Valid (Data, Part) or else Size > Total - Position then return False; end if;
            for J in E.Count range 1 .. Size loop
               if B64.Decoded_Byte (Data, Encoded, Position + J - 1) /= B64.Decoded_Byte (Data, Payload, J - 1) then return False; end if;
            end loop;
            Position := Position + Size;
         end;
      end loop;
      return Position = Total;
   end Joined_Bytes;
   function Flags_Match (Data : E.Bytes; Stream, Parts : E.Span; Field : String) return Boolean is
      Number : constant E.Span := F (Data, Stream, Field);
      View : constant E.View := E.Decode (Data, Number, E.Operation);
      Encoded : constant B64.Span := (View.Payload.Encoded.First, View.Payload.Encoded.Length);
      Maximum : E.Count := 0;
      Present : Boolean := False;
   begin
      for I in E.Count range 1 .. Len (Data, Parts) loop
         declare Flag : constant E.Span := F (Data, Item (Data, Parts, I - 1), Field);
           V : constant E.View := E.Decode (Data, Flag, E.Operation); begin
            if Flag.Length > 0 then
               if not Valid (Data, Flag) or else V.Form /= E.Integer_Value or else V.Sign
                 or else V.Payload.Level /= 1 then return False; end if;
               Present := True;
               Maximum := E.Count'Max (Maximum, E.Count (B64.Decoded_Length (Data, (V.Payload.Encoded.First, V.Payload.Encoded.Length))));
            end if;
         end;
      end loop;
      if not Present then return Is_None (Data, Number); end if;
      if not Valid (Data, Number) or else View.Form /= E.Integer_Value or else View.Sign
        or else View.Payload.Level /= 1 or else E.Count (B64.Decoded_Length (Data, Encoded)) /= Maximum then return False; end if;
      for I in E.Count range 1 .. Maximum loop
         declare Combined : E.Count := 0; begin
            for J in E.Count range 1 .. Len (Data, Parts) loop
               declare
                  Flag : constant E.Span := F (Data, Item (Data, Parts, J - 1), Field);
                  V : constant E.View := E.Decode (Data, Flag, E.Operation);
                  Payload : constant B64.Span := (V.Payload.Encoded.First, V.Payload.Encoded.Length);
                  Size : constant E.Count := (if Flag.Length = 0 then 0 else E.Count (B64.Decoded_Length (Data, Payload)));
                  Left : E.Count := Combined;
                  Right : E.Count := (if I <= Maximum - Size then 0 else E.Count (B64.Decoded_Byte (Data, Payload, I - (Maximum - Size) - 1)));
                  Place : E.Count := 1;
               begin
                  Combined := 0;
                  for Bit in E.Count range 1 .. 8 loop
                     if Left mod 2 = 1 or else Right mod 2 = 1 then Combined := Combined + Place; end if;
                     Left := Left / 2; Right := Right / 2; Place := Place * 2;
                  end loop;
               end;
            end loop;
            if E.Count (B64.Decoded_Byte (Data, Encoded, I - 1)) /= Combined then return False; end if;
         end;
      end loop;
      return True;
   end Flags_Match;
   function Stream_Matches (Data : E.Bytes; Stream : E.Span) return Boolean is
      Parts : constant E.Span := F (Data, Stream, "parts");
   begin
      if not Width (Data, Stream, 9) or else not Seq (Data, Parts) or else Len (Data, Parts) = 0
        or else not SF (Data, Stream, Item (Data, Parts, 0), "fd")
        or else not SF (Data, Stream, Item (Data, Parts, 0), "source")
        or else not Joined_Bytes (Data, F (Data, Stream, "frame"), Parts, "frame")
        or else not Joined_Bytes (Data, F (Data, Stream, "rights"), Parts, "rights")
        or else not Flags_Match (Data, Stream, Parts, "flags")
        or else not Flags_Match (Data, Stream, Parts, "input_flags")
        or else not Count_Is (Data, F (Data, Stream, "result"), Len (Data, Parts))
        or else not Number_Is (Data, F (Data, Stream, "errno"), 0) then return False; end if;
      for I in E.Count range 1 .. Len (Data, Parts) loop
         if not SF (Data, Item (Data, Parts, I - 1), Item (Data, Parts, 0), "fd")
           or else not SF (Data, Item (Data, Parts, I - 1), Item (Data, Parts, 0), "source")
           or else not Same (Data, F (Data, Item (Data, Parts, I - 1), "raw"), F (Data, Item (Data, Parts, I - 1), "frame"))
         then return False; end if;
      end loop;
      return True;
   end Stream_Matches;
   function Initial_Root_Transport_Matches (Data : E.Bytes; Inventory : E.Span) return Boolean is
      Transport : constant E.Span := F (Data, Inventory, "initial_root_transport");
      Root_Frame : constant E.Span := F (Data, Transport, "frame");
      Trailer : constant E.Span := F (Data, Transport, "trailer");
      Transfer : constant E.Span := F (Data, Transport, "transfer");
      Broker : constant E.Span := F (Data, Transport, "ofd_broker");
      Profile : constant E.Span := F (Data, Transport, "sender_role_roster");
      Original_Roles : constant E.Span := F (Data, F (Data, Root_Frame, "subject_custody"), "roles");
      Received_Roles : constant E.Span := F (Data, Transfer, "roles");
      Broker_Roles : constant E.Span := F (Data, Profile, "roles");
      Current_Roles : constant E.Span := F (Data, Transport, "current_roles");
      Current_Actor : constant E.Span := F (Data, Transport, "current_actor");
      Current_Source : constant E.Span := F (Data, Transport, "current_source");
      Native : constant E.Span := F (Data, Root_Frame, "root_native");
      Material : constant E.Span := F (Data, Native, "material");
      Observation : constant E.Span := F (Data, Native, "observation");
      Provenance : constant E.Span := F (Data, Native, "provenance");
      Controller : constant E.Span := F (Data, Material, "controller");
      Send : constant E.Span := F (Data, Trailer, "send");
      Send_Parts : constant E.Span := F (Data, F (Data, Transfer, "send"), "parts");
      Receive_Parts : constant E.Span := F (Data, F (Data, Transfer, "receive"), "parts");
      Closed : constant E.Span := F (Data, F (Data, Inventory, "frame"), "closed_roles");
      function Baseline (Here : E.Span) return E.Span
        with Subprogram_Variant => (Decreases => Here.Length)
      is
         Frame : constant E.Span := F (Data, Here, "frame");
         Prior : E.Span := F (Data, F (Data, Here, "reconstruction"), "original_inventory");
         Found : E.Span;
         Closures : constant E.Span := F (Data, Frame, "closed_roles");
      begin
         if Same (Data, Frame, F (Data, Root_Frame, "owned_descriptor_roster")) then return Here; end if;
         if Prior.Length > 0 and then Prior.Length < Here.Length then
            Found := Baseline (Prior); if Found.Length > 0 then return Found; end if;
         end if;
         Prior := F (Data, F (Data, Frame, "evolution"), "original_inventory");
         if Prior.Length > 0 and then Prior.Length < Here.Length then
            Found := Baseline (Prior); if Found.Length > 0 then return Found; end if;
         end if;
         for I in E.Count range 1 .. E.Array_Length (Data, Members (Data, Closures)) loop
            Prior := F (Data, Value (Data, Closures, I - 1), "before_inventory");
            if Prior.Length > 0 and then Prior.Length < Here.Length then
               Found := Baseline (Prior); if Found.Length > 0 then return Found; end if;
            end if;
         end loop;
         return Empty;
      end Baseline;
      function Received_Before (Here, Name, Received : E.Span) return Boolean
        with Subprogram_Variant => (Decreases => Here.Length)
      is
         Frame : constant E.Span := F (Data, Here, "frame");
         Roles : constant E.Span := F (Data, Here, "roles");
      begin
         for I in E.Count range 1 .. Len (Data, Roles) loop
            declare
               Role : constant E.Span := Item (Data, Roles, I - 1);
               Stat : constant E.Span := F (Data, Role, "fstat");
            begin
               if Same (Data, Name, F (Data, Role, "role"))
                 and then Same (Data, F (Data, Stat, "fd"), F (Data, Received, "worker_fd"))
                 and then Same (Data, F (Data, Stat, "fd"), F (Data, F (Data, Stat, "args"), "fd"))
                 and then Same (Data, F (Data, Stat, "source"), F (Data, Here, "current_source"))
                 and then Number_Is (Data, F (Data, Stat, "result"), 0)
                 and then Number_Is (Data, F (Data, Stat, "errno"), 0)
                 and then Identity (Data, F (Data, Stat, "identity"), F (Data, Received, "current"))
                 and then Identity (Data, F (Data, Role, "current"), F (Data, Received, "current"))
                 and then Same (Data, F (Data, Role, "origin"), F (Data, Received, "origin"))
                 and then SF (Data, Role, Received, "front_fd")
                 and then SF (Data, Role, Received, "front_actor")
                 and then SF (Data, Role, Received, "worker_pidfd")
               then return True; end if;
            end;
         end loop;
         for I in Positive range 1 .. 2 loop
            declare
               Prior : constant E.Span := F (Data,
                 F (Data, Frame, (if I = 1 then "reconstruction" else "evolution")), "original_inventory");
            begin
               if Prior.Length > 0 and then Prior.Length < Here.Length
                 and then Received_Before (Prior, Name, Received) then return True; end if;
            end;
         end loop;
         return False;
      end Received_Before;
      Before : E.Span;
   begin
      if Transport.Length = 0 then return True; end if;
      Before := Baseline (Inventory);
      if F (Data, Inventory, "subject_transport").Length > 0
        or else not Width (Data, Transport, 9)
        or else not Text (Data, F (Data, Transport, "schema"), "worldline.initial-root-subject-transport-source-v1")
        or else not Width (Data, Root_Frame, 18)
        or else not Text (Data, F (Data, Root_Frame, "schema"), "worldline.root-worker-custody-v1")
        or else not R.Root_Material_Matches (Data, Observation, Material)
        or else not R.Root_Capture_Matches (Data, Observation, Provenance)
        or else not P.Id_Hex (Data, F (Data, F (Data, Controller, "bound"), "operation"), F (Data, Root_Frame, "operation"))
        or else Before.Length = 0 or else not Width (Data, Trailer, 6)
        or else not Text (Data, F (Data, Trailer, "schema"), "worldline.root-custody-actual-send-transcript-v1")
        or else not Width (Data, Broker, 3)
        or else not Text (Data, F (Data, Broker, "schema"), "worldline.actual-root-ofd-broker-v1")
        or else not Width (Data, Profile, 5)
        or else not Same (Data, F (Data, Broker, "sender_role_roster"), Profile)
        or else not Same (Data, F (Data, F (Data, Broker, "transfer"), "roles"), Broker_Roles)
        or else not Physical_Roles_Match (Data, Received_Roles, Broker_Roles)
        or else not Same (Data, F (Data, Trailer, "roles"), Original_Roles)
        or else not Same (Data, F (Data, Transfer, "roster"), Original_Roles)
        or else not Seq (Data, Original_Roles) or else not Seq (Data, Current_Roles)
        or else Len (Data, Original_Roles) /= Len (Data, Current_Roles)
        or else Len (Data, Original_Roles) /= Len (Data, Received_Roles)
        or else Len (Data, Original_Roles) /= Len (Data, Send)
        or else Len (Data, Original_Roles) /= Len (Data, Send_Parts)
        or else Len (Data, Original_Roles) /= Len (Data, Receive_Parts)
        or else not Stream_Matches (Data, F (Data, Transfer, "send"))
        or else not Stream_Matches (Data, F (Data, Transfer, "receive"))
        or else not Same (Data, F (Data, Transfer, "frame"), F (Data, F (Data, Transfer, "send"), "frame"))
        or else not Same (Data, Current_Source, F (Data, Inventory, "current_source"))
        or else not SF (Data, Current_Actor, F (Data, Inventory, "current_actor"), "pid")
        or else not SF (Data, Current_Actor, F (Data, Inventory, "current_actor"), "boot")
        or else not SF (Data, Current_Actor, F (Data, Inventory, "current_actor"), "start_tick")
        or else not SF (Data, Current_Actor, F (Data, Inventory, "current_actor"), "credentials")
        or else not Closed_Roles_Match (Data, Inventory) then return False; end if;
      for I in E.Count range 1 .. E.Array_Length (Data, Members (Data, Transfer)) loop
         declare Name : constant E.Span := Key (Data, Transfer, I - 1); begin
            if not Text (Data, Name, "roles")
              and then not Same (Data, Value (Data, Transfer, I - 1), Lookup (Data, F (Data, Broker, "transfer"), Name))
            then return False; end if;
         end;
      end loop;
      if not Width (Data, F (Data, Broker, "transfer"), E.Array_Length (Data, Members (Data, Transfer))) then return False; end if;
      for I in E.Count range 1 .. Len (Data, Original_Roles) loop
         declare
            Original : constant E.Span := Item (Data, Original_Roles, I - 1);
            Received : constant E.Span := Item (Data, Received_Roles, I - 1);
            Current : constant E.Span := Item (Data, Current_Roles, I - 1);
            Sender_Role : constant E.Span := Item (Data, Broker_Roles, I - 1);
            Name : constant E.Span := F (Data, Original, "role");
            Sent : constant E.Span := Item (Data, Send, I - 1);
            Recv : constant E.Span := Item (Data, Receive_Parts, I - 1);
            Stat : constant E.Span := F (Data, Current, "fstat");
            Kcmp : constant E.Span := F (Data, Sender_Role, "kcmp");
            Args : constant E.Span := F (Data, Kcmp, "args");
            Closure : E.Span := Empty;
            Scoped_Role : E.Span := Empty;
            Scoped_Original : E.Span := Empty;
            Scoped_Key : E.Span := Empty;
         begin
            if not Same (Data, Name, F (Data, Received, "role"))
              or else not Same (Data, Name, F (Data, Current, "role"))
              or else not Same (Data, F (Data, Original, "fd"), F (Data, Received, "front_fd"))
              or else not Same (Data, F (Data, Original, "identity"), F (Data, Received, "origin"))
              or else not Receipt_Part_Matches (Data, Item (Data, Send_Parts, I - 1), Sent)
              or else not N.FD_Receipt_Matches (Data, Sent, F (Data, Original, "fd"), F (Data, Transfer, "sender"), True)
              or else not N.FD_Receipt_Matches (Data, Recv, F (Data, Received, "worker_fd"), F (Data, Transfer, "received_sender"), False)
              or else not N.SCM_Credentials_Match (Data, Sent, Recv, F (Data, Original, "front_actor"),
                F (Data, Before, "current_actor"), F (Data, Before, "namespace_source"))
              or else not Width (Data, Kcmp, 5) or else not Width (Data, Args, 5)
              or else not Text (Data, F (Data, Kcmp, "call"), "kcmp")
              or else not Number_Is (Data, F (Data, Kcmp, "result"), 0)
              or else not Number_Is (Data, F (Data, Kcmp, "errno"), 0)
              or else not Same (Data, F (Data, Kcmp, "source"), F (Data, Profile, "source"))
              or else not Same (Data, F (Data, Args, "pid1"), F (Data, F (Data, Profile, "actor"), "pid"))
              or else not Same (Data, F (Data, Args, "pid2"), F (Data, Profile, "worker_host_pid"))
              or else not Number_Is (Data, F (Data, Args, "type"), 0)
              or else not Same (Data, F (Data, Args, "idx1"), F (Data, Original, "fd"))
              or else not Same (Data, F (Data, Args, "idx2"), F (Data, Received, "worker_fd"))
              or else not Text (Data, F (Data, Stat, "call"), "fstat")
              or else not Same (Data, F (Data, Stat, "fd"), F (Data, F (Data, Stat, "args"), "fd"))
              or else not Same (Data, F (Data, Stat, "source"), Current_Source) then return False; end if;
            declare Scoped_Originals : constant E.Span := F (Data, F (Data, Before, "frame"), "original_roles"); begin
               for J in E.Count range 1 .. Len (Data, Scoped_Originals) loop
                  declare Candidate : constant E.Span := Item (Data, Scoped_Originals, J - 1); begin
                     if Scoped_Name (Data, Data, Name, F (Data, Candidate, "role")) then
                        if Scoped_Original.Length > 0 then return False; end if;
                        Scoped_Original := Candidate; Scoped_Key := F (Data, Candidate, "role");
                     end if;
                  end;
               end loop;
            end;
            if Scoped_Original.Length > 0 then
               if not Width (Data, Original, 7) or else not Width (Data, Scoped_Original, 7)
                 or else not SF (Data, Original, Scoped_Original, "fd")
                 or else not SF (Data, Original, Scoped_Original, "identity")
                 or else not SF (Data, Original, Scoped_Original, "front_actor")
                 or else not SF (Data, Original, Scoped_Original, "worker_pidfd")
                 or else not SF (Data, Original, Scoped_Original, "lock_path")
                 or else not SF (Data, Original, Scoped_Original, "socket_document")
                 or else not Same (Data, Sent, Lookup (Data, F (Data, Trailer, "owned_roster_send"), Scoped_Key))
                 or else not Same (Data, Sent, Lookup (Data, F (Data, Before, "sender_receipts"), Scoped_Key))
                 or else not Receipt_Part_Matches (Data, Recv, Item (Data, Lookup (Data, F (Data, Before, "receive_receipts"), Scoped_Key), 0))
               then return False; end if;
               for J in E.Count range 1 .. Len (Data, F (Data, Inventory, "roles")) loop
                  declare Candidate : constant E.Span := Item (Data, F (Data, Inventory, "roles"), J - 1); begin
                     if Same (Data, Scoped_Key, F (Data, Candidate, "role")) then
                        if Scoped_Role.Length > 0 then return False; end if;
                        Scoped_Role := Candidate;
                     end if;
                  end;
               end loop;
            end if;
            if Width (Data, Current, 3) then
               for J in E.Count range 1 .. E.Array_Length (Data, Members (Data, Closed)) loop
                  if Scoped_Name (Data, Data, Name, Key (Data, Closed, J - 1)) then
                     if Closure.Length > 0 then return False; end if;
                     Closure := Value (Data, Closed, J - 1);
                  end if;
               end loop;
               if Closure.Length = 0 or else not Number_Is (Data, F (Data, Stat, "result"), -1)
                 or else not Number_Is (Data, F (Data, Stat, "errno"), 9)
                 or else not Same (Data, F (Data, Current, "fd"), F (Data, Stat, "fd"))
                 or else not Same (Data, F (Data, Current, "fd"), F (Data, Received, "worker_fd"))
                 or else not Identity (Data, F (Data, F (Data, Closure, "alias"), "identity"), F (Data, Received, "current"))
                 or else F (Data, Closure, "before_inventory").Length = 0
                 or else F (Data, Closure, "before_inventory").Length >= Inventory.Length
                 or else not Received_Before (F (Data, Closure, "before_inventory"), Scoped_Key, Received)
               then return False; end if;
            elsif not Width (Data, Current, 12)
              or else not Same (Data, F (Data, Current, "front_fd"), F (Data, Original, "fd"))
              or else not Same (Data, F (Data, Current, "origin"), F (Data, Original, "identity"))
              or else not SF (Data, Current, Original, "front_actor")
              or else not SF (Data, Current, Original, "worker_pidfd")
              or else not SF (Data, Current, Original, "lock_path")
              or else not Width (Data, Stat, 7)
              or else not Width (Data, F (Data, Stat, "args"), 1)
              or else not Number_Is (Data, F (Data, Stat, "result"), 0)
              or else not Number_Is (Data, F (Data, Stat, "errno"), 0)
              or else not Same (Data, F (Data, Stat, "fd"), F (Data, Current, "worker_fd"))
              or else not Same (Data, F (Data, Current, "current"), F (Data, Stat, "identity"))
              or else not Identity (Data, F (Data, Current, "current"), F (Data, Received, "current"))
            then return False; end if;
            if Width (Data, Current, 12) then
               declare
                  Observed_Kcmp : constant E.Span := F (Data, Current, "kcmp");
                  Kargs : constant E.Span := F (Data, Observed_Kcmp, "args");
                  Lock : constant E.Span := F (Data, Current, "flock");
                  Socket : constant E.Span := F (Data, Current, "socket");
               begin
                  if not Width (Data, Observed_Kcmp, 5) or else not Width (Data, Kargs, 5)
                    or else not Text (Data, F (Data, Observed_Kcmp, "call"), "kcmp")
                    or else not Same (Data, F (Data, Observed_Kcmp, "source"), Current_Source)
                    or else not Same (Data, F (Data, Kargs, "pid1"), F (Data, F (Data, Original, "front_actor"), "pid"))
                    or else not Same (Data, F (Data, Kargs, "pid2"), F (Data, Current_Actor, "pid"))
                    or else not Number_Is (Data, F (Data, Kargs, "type"), 0)
                    or else not Same (Data, F (Data, Kargs, "idx1"), F (Data, Original, "fd"))
                    or else not Same (Data, F (Data, Kargs, "idx2"), F (Data, Current, "worker_fd"))
                    or else E.Decode (Data, F (Data, Observed_Kcmp, "result"), E.Operation).Form /= E.Integer_Value
                    or else E.Decode (Data, F (Data, Observed_Kcmp, "errno"), E.Operation).Form /= E.Integer_Value
                  then return False; end if;
                  -- The actual receiver-side namespace query is not broker
                  -- permission: preserve its real error, while the authentic
                  -- sender-side broker above must still report KCMP success.
                  if E.Decode (Data, F (Data, Observed_Kcmp, "result"), E.Operation).Sign then
                     if not Number_Is (Data, F (Data, Observed_Kcmp, "result"), -1)
                       or else E.Decode (Data, F (Data, Observed_Kcmp, "errno"), E.Operation).Sign
                       or else Number_Is (Data, F (Data, Observed_Kcmp, "errno"), 0) then return False; end if;
                  elsif not Number_Is (Data, F (Data, Observed_Kcmp, "errno"), 0) then return False; end if;
                  if Is_None (Data, F (Data, Original, "lock_path")) then
                     if not Is_None (Data, Lock) then return False; end if;
                  elsif not Width (Data, Lock, 5) or else not Width (Data, F (Data, Lock, "args"), 2)
                    or else not Text (Data, F (Data, Lock, "call"), "flock")
                    or else not Same (Data, F (Data, Lock, "source"), Current_Source)
                    or else not Same (Data, F (Data, F (Data, Lock, "args"), "fd"), F (Data, Current, "worker_fd"))
                    or else not Number_Is (Data, F (Data, F (Data, Lock, "args"), "operation"), 6)
                    or else not Number_Is (Data, F (Data, Lock, "result"), 0)
                    or else not Number_Is (Data, F (Data, Lock, "errno"), 0) then return False; end if;
                  if Is_None (Data, F (Data, Original, "socket_document")) then
                     if not Is_None (Data, Socket) then return False; end if;
                  else
                     if not Width (Data, Socket, 7)
                       or else not Same (Data, F (Data, Socket, "fd"), F (Data, Current, "worker_fd"))
                       or else not Same (Data, F (Data, Socket, "source"), Current_Source)
                       or else not Width (Data, F (Data, Socket, "fstat"), 7)
                       or else not Same (Data, F (Data, F (Data, Socket, "fstat"), "fd"), F (Data, Current, "worker_fd"))
                       or else not Same (Data, F (Data, F (Data, Socket, "fstat"), "source"), Current_Source)
                       or else not Identity (Data, F (Data, F (Data, Socket, "fstat"), "identity"), F (Data, Current, "current"))
                     then return False; end if;
                     for J in Positive range 1 .. 4 loop
                        declare
                           Call : constant E.Span := F (Data, Socket,
                             (case J is when 1 => "peercred", when 2 => "domain", when 3 => "type", when 4 => "peername"));
                        begin
                           if not Width (Data, Call, (if J = 4 then 6 else 10))
                             or else not Text (Data, F (Data, Call, "call"), (if J = 4 then "getpeername" else "getsockopt"))
                             or else not Same (Data, F (Data, Call, "fd"), F (Data, Current, "worker_fd"))
                             or else not Same (Data, F (Data, Call, "source"), Current_Source)
                             or else not Bytes_Valid (Data, F (Data, Call, "raw"))
                           then return False; end if;
                        end;
                     end loop;
                  end if;
               end;
               if Scoped_Original.Length > 0 then
                  if Scoped_Role.Length = 0 or else not SF (Data, Current, Scoped_Role, "worker_fd")
                    or else not Identity (Data, F (Data, Current, "current"), F (Data, Scoped_Role, "current"))
                  then return False; end if;
               elsif not SF (Data, Current, Received, "worker_fd") then return False; end if;
            end if;
         end;
      end loop;
      return True;
   end Initial_Root_Transport_Matches;
   function Subject_Transport_Matches (Data : E.Bytes; Inventory : E.Span) return Boolean is
      Transport : constant E.Span := F (Data, Inventory, "subject_transport");
      Original_Image : constant E.Span := F (Data, Transport, "original_frame");
      Header : constant E.Span := F (Data, Transport, "header_sender");
      Transcript : constant E.Span := F (Data, Transport, "original_transcript");
      Sent : constant E.Span := F (Data, Transcript, "send");
      Preclose : constant E.Span := F (Data, Transport, "preclose_join");
      Binding : constant E.Span := F (Data, Transport, "root_binding");
      Sender_Roles : constant E.Span := F (Data, Transport, "original_sender_roles");
      Original_Receipts : constant E.Span := F (Data, Transport, "original_receive_receipts");
   begin
      if Transport.Length = 0 then return True; end if;
      if not Valid (Data, Transport) or else not Bytes_Valid (Data, Original_Image)
        or else not Bytes_Valid (Data, Header) or else Byte_Count (Data, Header) /= 12
        or else not Text (Data, F (Data, Transcript, "kind"), "SEND_TRANSCRIPT")
        or else not Seq (Data, Sent) or else not Seq (Data, Sender_Roles)
        or else not Width (Data, Binding, 2) then return False; end if;
      declare
         Original : constant E.Bytes := Source_Bytes (Data, Original_Image);
         Original_Span : constant E.Span := (Original'First, Original'Length);
         function Baseline (Here : E.Span) return E.Span
           with Subprogram_Variant => (Decreases => Here.Length)
         is
            Frame : constant E.Span := F (Data, Here, "frame");
            Reconstruction : constant E.Span := F (Data, F (Data, Here, "reconstruction"), "original_inventory");
            Evolution : constant E.Span := F (Data, F (Data, Frame, "evolution"), "original_inventory");
            Closed : constant E.Span := F (Data, Frame, "closed_roles");
            Found : E.Span;
         begin
            if RA.Ordered_Source_Value_Matches (Original, Data, Original_Span, Frame, False, False) then return Here; end if;
            if Reconstruction.Length > 0 and then Reconstruction.Length < Here.Length then
               Found := Baseline (Reconstruction); if Found.Length > 0 then return Found; end if;
            end if;
            if Evolution.Length > 0 and then Evolution.Length < Here.Length then
               Found := Baseline (Evolution); if Found.Length > 0 then return Found; end if;
            end if;
            for I in E.Count range 1 .. E.Array_Length (Data, Members (Data, Closed)) loop
               declare Previous : constant E.Span := F (Data, Value (Data, Closed, I - 1), "before_inventory"); begin
                  if Previous.Length > 0 and then Previous.Length < Here.Length then
                     Found := Baseline (Previous); if Found.Length > 0 then return Found; end if;
                  end if;
               end;
            end loop;
            return Empty;
         end Baseline;
         Before : constant E.Span := Baseline (Inventory);
         Frame : constant E.Span := F (Data, Before, "frame");
         Originals : constant E.Span := F (Data, Frame, "original_roles");
         Roles : constant E.Span := F (Data, Before, "roles");
      begin
         if Before.Length = 0 or else not Seq (Data, Originals) or else not Seq (Data, Roles)
           or else Len (Data, Originals) /= Len (Data, Sent)
           or else Len (Data, Roles) /= Len (Data, Originals)
           or else Len (Data, Sender_Roles) /= Len (Data, Originals)
           or else not Width (Data, Original_Receipts, Len (Data, Originals)) then return False; end if;
         for I in E.Count range 1 .. Len (Data, Originals) loop
            declare
               Captured : constant E.Span := Item (Data, Originals, I - 1);
               Name : constant E.Span := F (Data, Captured, "role");
               Role : constant E.Span := Find (Data, Roles, "role", Name);
               Send : constant E.Span := Item (Data, Sent, I - 1);
               Received : constant E.Span := Lookup (Data, F (Data, Before, "receive_receipts"), Name);
               Receive : constant E.Span := Item (Data, Received, 0);
               Sender_Role : constant E.Span := Find (Data, Sender_Roles, "role", Name);
               Sender_Stat : constant E.Span := F (Data, Sender_Role, "fstat");
               Sender_Actor : constant E.Span := F (Data, Sender_Role, "front_actor");
               Original_Actor : constant E.Span := F (Data, Captured, "front_actor");
            begin
               if not Width (Data, Sender_Role, 12)
                 or else not Same (Data, Name, F (Data, Sender_Role, "role"))
                 or else not Same (Data, F (Data, Captured, "fd"), F (Data, Sender_Role, "front_fd"))
                 or else not Identity (Data, F (Data, Captured, "identity"), F (Data, Sender_Role, "origin"))
                 or else not Identity (Data, F (Data, Captured, "identity"), F (Data, Sender_Role, "current"))
                 or else not SF (Data, Sender_Role, Captured, "lock_path")
                 or else not
                   ((Is_None (Data, F (Data, Sender_Role, "worker_pidfd"))
                     and then Is_None (Data, F (Data, Captured, "worker_pidfd")))
                    or else Identity (Data, F (Data, Sender_Role, "worker_pidfd"), F (Data, Captured, "worker_pidfd")))
                 or else not SF (Data, Sender_Actor, Original_Actor, "boot")
                 or else not SF (Data, Sender_Actor, Original_Actor, "pid")
                 or else not SF (Data, Sender_Actor, Original_Actor, "start_tick")
                 or else not SF (Data, Sender_Actor, Original_Actor, "credentials")
                 or else not Is_None (Data, F (Data, Sender_Role, "worker_fd"))
                 or else not Is_None (Data, F (Data, Sender_Role, "flock"))
                 or else not Is_None (Data, F (Data, Sender_Role, "kcmp"))
                 or else not Width (Data, Sender_Stat, 7)
                 or else not Width (Data, F (Data, Sender_Stat, "args"), 1)
                 or else not Text (Data, F (Data, Sender_Stat, "call"), "fstat")
                 or else not Same (Data, F (Data, Sender_Stat, "fd"), F (Data, Captured, "fd"))
                 or else not Same (Data, F (Data, F (Data, Sender_Stat, "args"), "fd"), F (Data, Captured, "fd"))
                 or else not Number_Is (Data, F (Data, Sender_Stat, "result"), 0)
                 or else not Number_Is (Data, F (Data, Sender_Stat, "errno"), 0)
                 or else not Same (Data, F (Data, Sender_Stat, "source"), F (Data, Frame, "source"))
                 or else not Same (Data, F (Data, Sender_Stat, "identity"), F (Data, Sender_Role, "current"))
                 or else not Same (Data, Lookup (Data, Original_Receipts, Name), Receive)
                 or else not Same (Data, Send, Lookup (Data, F (Data, Before, "sender_receipts"), Name))
                 or else Len (Data, Received) /= 1 or else not Same (Data, F (Data, Receive, "sender"), Header)
                 or else not N.FD_Receipt_Matches (Data, Send, F (Data, Captured, "fd"),
                   F (Data, F (Data, Captured, "front_actor"), "credentials"), True)
                 or else not N.FD_Receipt_Matches (Data, Receive, F (Data, Role, "worker_fd"), Header, False)
                 or else not N.SCM_Credentials_Match (Data, Send, Receive, F (Data, Captured, "front_actor"),
                   F (Data, Before, "current_actor"), F (Data, Before, "namespace_source")) then return False; end if;
            end;
         end loop;
         if Preclose.Length = 0 then
            if Binding.Length > 0 then
               if not Width (Data, Binding, 2) or else not Bytes_Valid (Data, F (Data, Binding, "frame")) then return False; end if;
               declare
                  Root : constant E.Bytes := Source_Bytes (Data, F (Data, Binding, "frame"));
                  Root_Span : constant E.Span := (Root'First, Root'Length);
                  Operation : constant E.Span := F (Root, Root_Span, "operation");
                  Controller : constant E.Span := F (Root, F (Root, F (Root, Root_Span, "root_native"), "material"), "controller");
               begin
                  if not Valid (Root, Root_Span)
                    or else not RA.Ordered_Source_Value_Matches (Root, Data, Operation, F (Data, Binding, "operation"), False, False)
                    or else not P.Id_Hex (Root, F (Root, F (Root, Controller, "bound"), "operation"), Operation)
                  then return False; end if;
               end;
            end if;
            return Width (Data, Transport, 6);
         end if;
         declare
            Capture : constant E.Span := F (Data, Preclose, "capture");
            Joined : constant E.Span := F (Data, Preclose, "joined");
            Profile : constant E.Span := F (Data, Joined, "profile");
            Current_Inventory : constant E.Span := F (Data, Capture, "current_inventory");
            Root_Transport : constant E.Span := F (Data, Preclose, "transport");
            Root_Image : constant E.Span := F (Data, Root_Transport, "raw");
            Root_Frame_Image : constant E.Span := F (Data, Binding, "frame");
            function Preclose_Baseline (Here : E.Span) return E.Span
              with Subprogram_Variant => (Decreases => Here.Length)
            is
               Here_Frame : constant E.Span := F (Data, Here, "frame");
               Closed_Roles : constant E.Span := F (Data, Here_Frame, "closed_roles");
               Prior : E.Span := F (Data, F (Data, Here, "reconstruction"), "original_inventory");
               Found : E.Span;
            begin
               if Same (Data, Here_Frame, F (Data, Current_Inventory, "frame"))
                 and then Physical_Roles_Match (Data, F (Data, Here, "roles"), F (Data, Capture, "roles"))
                 and then SF (Data, F (Data, Here, "current_actor"), F (Data, Current_Inventory, "current_actor"), "pid")
                 and then SF (Data, F (Data, Here, "current_actor"), F (Data, Current_Inventory, "current_actor"), "boot")
                 and then SF (Data, F (Data, Here, "current_actor"), F (Data, Current_Inventory, "current_actor"), "start_tick")
                 and then SF (Data, F (Data, Here, "current_actor"), F (Data, Current_Inventory, "current_actor"), "credentials")
                 and then Same (Data, F (Data, Here, "current_source"), F (Data, Current_Inventory, "current_source"))
                 and then Same (Data, F (Data, Here, "sender_role_roster"), Profile) then return Here; end if;
               if Prior.Length > 0 and then Prior.Length < Here.Length then
                  Found := Preclose_Baseline (Prior); if Found.Length > 0 then return Found; end if;
               end if;
               Prior := F (Data, F (Data, Here_Frame, "evolution"), "original_inventory");
               if Prior.Length > 0 and then Prior.Length < Here.Length then
                  Found := Preclose_Baseline (Prior); if Found.Length > 0 then return Found; end if;
               end if;
               for I in E.Count range 1 .. E.Array_Length (Data, Members (Data, Closed_Roles)) loop
                  Prior := F (Data, Value (Data, Closed_Roles, I - 1), "before_inventory");
                  if Prior.Length > 0 and then Prior.Length < Here.Length then
                     Found := Preclose_Baseline (Prior); if Found.Length > 0 then return Found; end if;
                  end if;
               end loop;
               return Empty;
            end Preclose_Baseline;
            Preclose_Before : constant E.Span := Preclose_Baseline (Inventory);
            Header_Receipts : constant E.Span := F (Data, Capture, "header_receive");
            Transcript_Receipts : constant E.Span := F (Data, Capture, "transcript_receipts");
         begin
            if not Width (Data, Transport, 7) or else not Width (Data, Preclose, 3) or else not Width (Data, Capture, 12)
              or else not Width (Data, Joined, 3) or else not Width (Data, Profile, 5)
              or else not Width (Data, Binding, 2) or else not Width (Data, Root_Transport, 5)
              or else not Same (Data, F (Data, Joined, "received"), Capture)
              or else not SF (Data, Capture, Transport, "original_frame")
              or else not SF (Data, Capture, Transport, "header_sender")
              or else not Same (Data, F (Data, Capture, "transcript"), Transcript)
              or else not Image_Matches (Data, F (Data, Capture, "raw"), F (Data, Capture, "message"))
              or else not Image_Matches (Data, F (Data, Capture, "transcript_raw"), Transcript)
              or else not Same (Data, Original_Image,
                F (Data, F (Data, F (Data, F (Data, Capture, "message"), "packet"), "transfer"), "original_frame"))
              or else not Same (Data, Sender_Roles,
                F (Data, F (Data, F (Data, F (Data, Capture, "message"), "packet"), "transfer"), "roles"))
              or else not Same (Data, F (Data, Profile, "roles"), F (Data, Joined, "roles"))
              or else Preclose_Before.Length = 0
              or else not Same (Data, F (Data, Capture, "roles"), F (Data, Current_Inventory, "roles"))
              or else not Physical_Roles_Match (Data, F (Data, Preclose_Before, "roles"), F (Data, Capture, "roles"))
              or else not Physical_Roles_Match (Data, F (Data, Capture, "original_received_roles"), Roles)
              or else not Same (Data, F (Data, Capture, "receipts"), Original_Receipts)
              or else not Bytes_Valid (Data, Root_Image) or else not Bytes_Valid (Data, Root_Frame_Image)
              or else not Same (Data, F (Data, Root_Transport, "sender_credentials"), Header) then return False; end if;
            for Receipt_Index in E.Count range 0 .. 1 loop
               declare
                  Receipt : constant E.Span :=
                    (if Receipt_Index = 0 then Header_Receipts else Item (Data, Transcript_Receipts, 0));
                  Rights : constant E.Span := F (Data, F (Data, Receipt, "args"), "rights");
               begin
                  if (if Receipt_Index = 0
                      then not Valid (Data, Header_Receipts)
                        or else E.Decode (Data, Header_Receipts, E.Operation).Form /= E.Object_Value
                      else not Seq (Data, Transcript_Receipts) or else Len (Data, Transcript_Receipts) /= 1)
                    or else not Seq (Data, Rights) or else Len (Data, Rights) /= 1
                    or else not FD (Data, Item (Data, Rights, 0))
                    or else not N.FD_Receipt_Matches (Data, Receipt, Item (Data, Rights, 0), Header, False)
                    or else not Same (Data, F (Data, Receipt, "source"), F (Data, Before, "current_source"))
                  then return False; end if;
               end;
            end loop;
            declare
               Reply : constant E.Bytes := Source_Bytes (Data, Root_Image);
               Root : constant E.Bytes := Source_Bytes (Data, Root_Frame_Image);
               Reply_Span : constant E.Span := (Reply'First, Reply'Length);
               Root_Span : constant E.Span := (Root'First, Root'Length);
               Record_Value : constant E.Span := F (Reply, Reply_Span, "record");
               Received : constant E.Span := F (Reply, Record_Value, "received");
               Joined_Values : constant E.Span := F (Reply, Record_Value, "joined");
               Root_Operation : constant E.Span := F (Root, Root_Span, "operation");
               Controller : constant E.Span := F (Root, F (Root, F (Root, Root_Span, "root_native"), "material"), "controller");
               Root_Receive : constant E.Span := F (Data, Root_Transport, "receive");
               Memfd : constant E.Span := F (Data, Root_Transport, "sealed_memfd");
               Channel : constant E.Span := F (Data, Root_Transport, "channel_source");
               Root_Receipt : constant E.Span := Item (Data, Root_Receive, 0);
               Root_Args : constant E.Span := F (Data, Root_Receipt, "args");
               Found : Boolean := False;
            begin
               if not Valid (Reply, Reply_Span) or else not Valid (Root, Root_Span)
                 or else not Text (Reply, F (Reply, Reply_Span, "kind"), "INPUT_EOF_RECEIVED_ACK")
                 or else not RA.Ordered_Source_Value_Matches (Root, Data, Root_Operation, F (Data, Binding, "operation"), False, False)
                 or else not RA.Ordered_Source_Value_Matches (Root, Reply, Root_Operation, F (Reply, Reply_Span, "operation"), False, False)
                 or else not P.Id_Hex (Root, F (Root, F (Root, Controller, "bound"), "operation"), Root_Operation)
                 or else not Seq (Reply, Received) or else not Seq (Reply, Joined_Values)
                 or else Len (Reply, Received) /= Len (Reply, Joined_Values)
                 or else Len (Data, Root_Receive) /= 1
                 or else not N.FD_Receipt_Matches (Data, Item (Data, Root_Receive, 0), F (Data, Memfd, "fd"), Header, False)
                 or else not Number_Is (Data, F (Data, Memfd, "seals"), 15) then return False; end if;
               if not Width (Data, Memfd, 3) or else not Width (Data, F (Data, Memfd, "identity"), 6)
                 or else not Width (Data, Channel, 2)
                 or else not Identity (Data, F (Data, Channel, "identity"), F (Data, Root_Args, "channel"))
                 or else not SF (Data, Channel, Root_Args, "peer")
                 or else not Same (Data, F (Data, Root_Receipt, "source"), F (Data, Preclose_Before, "current_source"))
               then return False; end if;
               for I in E.Count range 1 .. Len (Reply, Received) loop
                  if RA.Ordered_Source_Value_Matches (Reply, Data, Item (Reply, Received, I - 1), Capture, False, False) then
                     if Found or else not RA.Ordered_Source_Value_Matches
                       (Reply, Data, Item (Reply, Joined_Values, I - 1), Joined, False, False) then return False; end if;
                     Found := True;
                  end if;
               end loop;
               if not Found then return False; end if;
            end;
         end;
      end;
      return True;
   end Subject_Transport_Matches;
   function Closed_Roles_Match (Data : E.Bytes; Inventory : E.Span) return Boolean is
      Frame : constant E.Span := F (Data, Inventory, "frame");
      Closed : constant E.Span := F (Data, Frame, "closed_roles");
      function Actor_Matches (Left, Right : E.Span) return Boolean is
        (SF (Data, Left, Right, "pid") and then SF (Data, Left, Right, "boot")
         and then SF (Data, Left, Right, "start_tick") and then SF (Data, Left, Right, "credentials"));
      function Close_Matches (Receipt, Descriptor, Source, Actor : E.Span) return Boolean is
         Args : constant E.Span := F (Data, Receipt, "args");
         Receipt_Actor : constant E.Span := F (Data, Receipt, "actor");
         Receipt_FD : constant E.Span := F (Data, Receipt, "fd");
      begin
         return Valid (Data, Receipt) and then E.Decode (Data, Receipt, E.Operation).Form = E.Object_Value
           and then Valid (Data, Args) and then E.Decode (Data, Args, E.Operation).Form = E.Object_Value
           and then Text (Data, F (Data, Receipt, "call"), "close")
           --  The real syscall wrapper retains both kernel success and the
           --  actual Python API return; neither is inferred from the other.
           and then Number_Is (Data, F (Data, Receipt, "result"), 0)
           and then Is_None (Data, F (Data, Receipt, "api_result"))
           and then Number_Is (Data, F (Data, Receipt, "errno"), 0)
           and then Same (Data, F (Data, Args, "fd"), Descriptor)
           and then Same (Data, F (Data, Receipt, "source"), Source)
           and then (Receipt_FD.Length = 0 or else Same (Data, Receipt_FD, Descriptor))
           and then (Receipt_Actor.Length = 0 or else Actor_Matches (Receipt_Actor, Actor));
      end Close_Matches;
      function Writer_Lineage_Matches (Here, Name, Writer : E.Span) return Boolean
        with Subprogram_Variant => (Decreases => Here.Length)
      is
         Here_Frame : constant E.Span := F (Data, Here, "frame");
         Current : constant E.Span := Find (Data, F (Data, Here, "roles"), "role", Name);
         Captured : constant E.Span := Find (Data, F (Data, Here_Frame, "original_roles"), "role", Name);
         Prior : E.Span := F (Data, F (Data, Here, "reconstruction"), "original_inventory");
      begin
         if Current.Length > 0 and then Actor_Matches (F (Data, Here, "current_actor"), F (Data, Writer, "actor"))
           and then Same (Data, F (Data, Here, "current_source"), F (Data, Writer, "source"))
           and then Identity (Data, F (Data, Current, "current"), F (Data, Writer, "identity")) then return True; end if;
         if Captured.Length > 0 and then Actor_Matches (F (Data, Captured, "front_actor"), F (Data, Writer, "actor"))
           and then Same (Data, F (Data, Here_Frame, "source"), F (Data, Writer, "source"))
           and then Identity (Data, F (Data, Captured, "identity"), F (Data, Writer, "identity")) then return True; end if;
         if Prior.Length = 0 then Prior := F (Data, F (Data, Here_Frame, "evolution"), "original_inventory"); end if;
         return Prior.Length > 0 and then Prior.Length < Here.Length
           and then Writer_Lineage_Matches (Prior, Name, Writer);
      end Writer_Lineage_Matches;
      function Role_Lineage_Matches (Here, Before, Name : E.Span) return Boolean
        with Subprogram_Variant => (Decreases => Here.Length)
      is
         Here_Frame : constant E.Span := F (Data, Here, "frame");
         Current : constant E.Span := Find (Data, F (Data, Here, "roles"), "role", Name);
         Old : constant E.Span := Find (Data, F (Data, Before, "roles"), "role", Name);
         Captured : constant E.Span := Find (Data, F (Data, Here_Frame, "original_roles"), "role", Name);
         Old_Captured : constant E.Span := Find (Data, F (Data, F (Data, Before, "frame"), "original_roles"), "role", Name);
         Current_FD : constant E.Span := F (Data, Current,
           (if Is_None (Data, F (Data, Current, "worker_fd")) then "front_fd" else "worker_fd"));
         Old_FD : constant E.Span := F (Data, Old,
           (if Is_None (Data, F (Data, Old, "worker_fd")) then "front_fd" else "worker_fd"));
         Reconstruction : constant E.Span := F (Data, Here, "reconstruction");
         Evolution : constant E.Span := F (Data, Here_Frame, "evolution");
         Reconstructed : constant Boolean := F (Data, Reconstruction, "original_inventory").Length > 0;
         Step : constant E.Span := (if Reconstructed then Reconstruction else Evolution);
         Prior : constant E.Span := F (Data, Step, "original_inventory");
         Here_Closed : constant E.Span := F (Data, Here_Frame, "closed_roles");
         Stat : constant E.Span := F (Data, Current, "fstat");
      begin
         if Current.Length = 0 or else Old.Length = 0 or else Captured.Length = 0 or else Old_Captured.Length = 0
           or else not FD (Data, Current_FD) or else not FD (Data, Old_FD)
           or else not Text (Data, F (Data, Stat, "call"), "fstat")
           or else not Number_Is (Data, F (Data, Stat, "result"), 0)
           or else not Number_Is (Data, F (Data, Stat, "errno"), 0)
           or else not Same (Data, F (Data, Stat, "fd"), Current_FD)
           or else not Same (Data, F (Data, F (Data, Stat, "args"), "fd"), Current_FD)
           or else not Same (Data, F (Data, Stat, "source"), F (Data, Here, "current_source"))
           or else not Same (Data, F (Data, Stat, "identity"), F (Data, Current, "current"))
           or else not Same (Data, F (Data, Captured, "fd"), F (Data, Current, "front_fd"))
           or else not Same (Data, F (Data, Captured, "identity"), F (Data, Current, "origin"))
           or else not SF (Data, Captured, Current, "front_actor")
           or else not SF (Data, Captured, Current, "worker_pidfd")
           or else not SF (Data, Captured, Current, "lock_path")
           or else not Identity (Data, F (Data, Current, "current"), F (Data, Old, "current"))
           or else not Identity (Data, F (Data, Captured, "identity"), F (Data, Current, "current"))
           or else not Identity (Data, F (Data, Current, "current"), Lookup (Data, F (Data, Here, "current_descriptors"), Name))
           or else not Same (Data, F (Data, Here, "current_source"), F (Data, Before, "current_source")) then return False; end if;
         --  An unchanged local/received import retains its full original
         --  custody metadata and, for SCM, the exact send/receive receipts.
         --  FD equality alone never establishes historical OFD continuity.
         if Actor_Matches (F (Data, Here, "current_actor"), F (Data, Before, "current_actor"))
           and then Same (Data, Current_FD, Old_FD) and then Same (Data, Captured, Old_Captured)
           and then SF (Data, Current, Old, "front_fd") and then SF (Data, Current, Old, "worker_fd")
           and then SF (Data, Current, Old, "origin") and then SF (Data, Current, Old, "front_actor")
           and then SF (Data, Current, Old, "worker_pidfd") and then SF (Data, Current, Old, "lock_path")
           and then (Is_None (Data, F (Data, Current, "worker_fd")) or else
             (Same (Data, Lookup (Data, F (Data, Here, "sender_receipts"), Name),
               Lookup (Data, F (Data, Before, "sender_receipts"), Name))
              and then Same (Data, Lookup (Data, F (Data, Here, "receive_receipts"), Name),
                Lookup (Data, F (Data, Before, "receive_receipts"), Name)))) then return True; end if;
         --  Actual refresh/reconstruction receipts authorize different FDs.
         --  The caller validates every intermediate full native roster, not
         --  only the identity or numeric endpoint examined by this relation.
         if Prior.Length > 0 and then Prior.Length < Here.Length then
            declare
               Copy : constant E.Span := Find (Data, F (Data, Step,
                 (if Reconstructed then "duplicates" else "copies")), "role", Name);
               Prior_Role : constant E.Span := Find (Data, F (Data, Prior, "roles"), "role", Name);
               Origin_FD : constant E.Span := F (Data, F (Data, Prior_Role, "fstat"), "fd");
               Destination_FD : constant E.Span := F (Data, Captured, "fd");
               Kcmp : constant E.Span := F (Data, Copy, "kcmp");
               Args : constant E.Span := F (Data, Kcmp, "args");
               Dup : constant E.Span := F (Data, Copy, "dup");
               Rebind : constant E.Span := (if Reconstructed then
                 Find (Data, F (Data, Step, "extension_rebinds"), "role", Name) else Empty);
               Dup_Source_FD : constant E.Span := (if Rebind.Length = 0 then Origin_FD else F (Data, Rebind, "registry_fd"));
               Rebind_Kcmp : constant E.Span := F (Data, Rebind, "kcmp");
               Rebind_Args : constant E.Span := F (Data, Rebind_Kcmp, "args");
               Rebind_Matches : constant Boolean := Rebind.Length = 0 or else
                 (Width (Data, Rebind, 6) and then Same (Data, F (Data, Rebind, "original_fd"), Origin_FD)
                  and then FD (Data, Dup_Source_FD)
                  and then Identity (Data, F (Data, Rebind, "original_identity"), F (Data, Prior_Role, "current"))
                  and then Identity (Data, F (Data, Rebind, "registry_identity"), F (Data, Copy, "origin"))
                  and then Width (Data, Rebind_Kcmp, 5) and then Width (Data, Rebind_Args, 5)
                  and then Text (Data, F (Data, Rebind_Kcmp, "call"), "kcmp")
                  and then Number_Is (Data, F (Data, Rebind_Kcmp, "result"), 0)
                  and then Number_Is (Data, F (Data, Rebind_Kcmp, "errno"), 0)
                  and then Same (Data, F (Data, Rebind_Kcmp, "source"), F (Data, Step, "source"))
                  and then Same (Data, F (Data, Rebind_Args, "pid1"), F (Data, F (Data, Prior, "current_actor"), "pid"))
                  and then Same (Data, F (Data, Rebind_Args, "pid2"), F (Data, F (Data, Prior, "current_actor"), "pid"))
                  and then Number_Is (Data, F (Data, Rebind_Args, "type"), 0)
                  and then Same (Data, F (Data, Rebind_Args, "idx1"), Origin_FD)
                  and then Same (Data, F (Data, Rebind_Args, "idx2"), Dup_Source_FD));
               Receipt_FDs_Match : constant Boolean :=
                 (if Reconstructed then Text (Data, F (Data, Dup, "call"), "dup")
                   and then Number_Is (Data, F (Data, Dup, "errno"), 0)
                   and then Same (Data, F (Data, Dup, "source"), F (Data, Step, "source"))
                   and then Same (Data, F (Data, Dup, "result"), Destination_FD)
                   and then Same (Data, F (Data, F (Data, Dup, "args"), "fd"), Dup_Source_FD)
                   and then Same (Data, F (Data, F (Data, Dup, "args"), "role"), Name)
                 else Width (Data, Copy, 6)
                   and then Same (Data, F (Data, Copy, "origin_fd"), Origin_FD)
                   and then Same (Data, F (Data, Copy, "current_fd"), Destination_FD));
            begin
               if Copy.Length > 0 and then Prior_Role.Length > 0 and then FD (Data, Destination_FD)
                 and then Receipt_FDs_Match and then Rebind_Matches
                 and then Identity (Data, F (Data, Copy, "origin"), F (Data, Prior_Role, "current"))
                 and then Identity (Data, F (Data, Copy, "current"), F (Data, Captured, "identity"))
                 and then Width (Data, Kcmp, 5) and then Width (Data, Args, 5)
                 and then Text (Data, F (Data, Kcmp, "call"), "kcmp")
                 and then Number_Is (Data, F (Data, Kcmp, "result"), 0)
                 and then Number_Is (Data, F (Data, Kcmp, "errno"), 0)
                 and then Same (Data, F (Data, Kcmp, "source"), F (Data, Step, "source"))
                 and then Same (Data, F (Data, Args, "pid1"), F (Data, F (Data, Prior, "current_actor"), "pid"))
                 and then Same (Data, F (Data, Args, "pid2"), F (Data, F (Data, Captured, "front_actor"), "pid"))
                 and then Number_Is (Data, F (Data, Args, "type"), 0)
                 and then Same (Data, F (Data, Args, "idx1"), Dup_Source_FD)
                 and then Same (Data, F (Data, Args, "idx2"), Destination_FD)
                 and then Role_Lineage_Matches (Prior, Before, Name) then return True; end if;
            end;
         end if;
         for I in E.Count range 1 .. E.Array_Length (Data, Members (Data, Here_Closed)) loop
            declare
               Old_Inventory : constant E.Span := F (Data, Value (Data, Here_Closed, I - 1), "before_inventory");
               Previous : constant E.Span := Find (Data, F (Data, Old_Inventory, "roles"), "role", Name);
               Previous_Captured : constant E.Span := Find (Data, F (Data, F (Data, Old_Inventory, "frame"), "original_roles"), "role", Name);
            begin
               if Old_Inventory.Length > 0 and then Old_Inventory.Length < Here.Length and then Previous.Length > 0
                 and then Actor_Matches (F (Data, Here, "current_actor"), F (Data, Old_Inventory, "current_actor"))
                 and then Same (Data, Current_FD, F (Data, F (Data, Previous, "fstat"), "fd"))
                 and then Same (Data, Captured, Previous_Captured)
                 and then SF (Data, Current, Previous, "front_fd") and then SF (Data, Current, Previous, "worker_fd")
                 and then SF (Data, Current, Previous, "origin") and then SF (Data, Current, Previous, "front_actor")
                 and then SF (Data, Current, Previous, "worker_pidfd") and then SF (Data, Current, Previous, "lock_path")
                 and then (Is_None (Data, F (Data, Current, "worker_fd")) or else
                   (Same (Data, Lookup (Data, F (Data, Here, "sender_receipts"), Name),
                     Lookup (Data, F (Data, Old_Inventory, "sender_receipts"), Name))
                    and then Same (Data, Lookup (Data, F (Data, Here, "receive_receipts"), Name),
                      Lookup (Data, F (Data, Old_Inventory, "receive_receipts"), Name))))
                 and then Role_Lineage_Matches (Old_Inventory, Before, Name) then return True; end if;
            end;
         end loop;
         return False;
      end Role_Lineage_Matches;
      function Writer_Alias_Acquisition_Matches (Here, Name, Declaration : E.Span) return Boolean
        with Subprogram_Variant => (Decreases => Here.Length)
      is
         Here_Frame : constant E.Span := F (Data, Here, "frame");
         Reconstruction : constant E.Span := F (Data, Here, "reconstruction");
         Prior : constant E.Span := F (Data, Reconstruction, "original_inventory");
         Source_Name : constant E.Span := F (Data, Declaration, "source_descriptor");
         Source_Role : constant E.Span := Find (Data, F (Data, Prior, "roles"), "role", Source_Name);
         Source_Row : constant E.Span := Find_Row (Data, F (Data, F (Data, Prior, "frame"), "rows"), F (Data, Declaration, "bound"));
         Extension : constant E.Span := Find (Data, F (Data, Here_Frame, "extensions"), "descriptor", Name);
         Captured : constant E.Span := Find (Data, F (Data, Here_Frame, "original_roles"), "role", Name);
         Copy : constant E.Span := Find (Data, F (Data, Reconstruction, "duplicates"), "role", Name);
         Dup : constant E.Span := F (Data, Copy, "dup");
         Kcmp : constant E.Span := F (Data, Declaration, "kcmp");
         Args : constant E.Span := F (Data, Kcmp, "args");
         Copy_Kcmp : constant E.Span := F (Data, Copy, "kcmp");
         Copy_Args : constant E.Span := F (Data, Copy_Kcmp, "args");
         Source_FD : constant E.Span := F (Data, Declaration, "source_fd");
         Alias_Source_FD : constant E.Span := F (Data, Declaration, "alias_source_fd");
         Actor : constant E.Span := F (Data, Captured, "front_actor");
         Source : constant E.Span := F (Data, Reconstruction, "source");
         Evolution_Prior : constant E.Span := F (Data, F (Data, Here_Frame, "evolution"), "original_inventory");
         Here_Closed : constant E.Span := F (Data, Here_Frame, "closed_roles");
      begin
         if Same (Data, Declaration, Lookup (Data, F (Data, Here_Frame, "writer_aliases"), Name))
           and then Prior.Length > 0 and then Source_Role.Length > 0 and then Source_Row.Length > 0
           and then Captured.Length > 0 and then Extension.Length > 0 and then Copy.Length > 0
           and then Same (Data, Source_Name, F (Data, F (Data, Source_Row, "roles"), "stdin_fd"))
           and then Same (Data, F (Data, Declaration, "scope"), F (Data, F (Data, Source_Row, "row"), "scope"))
           and then Same (Data, Source_FD, F (Data, F (Data, Source_Role, "fstat"), "fd"))
           and then Same (Data, Alias_Source_FD, F (Data, Extension, "source_fd"))
           and then Identity (Data, F (Data, Declaration, "identity"), F (Data, Extension, "identity"))
           and then Identity (Data, F (Data, Declaration, "identity"), F (Data, Source_Role, "current"))
           and then Identity (Data, F (Data, Declaration, "identity"), F (Data, Copy, "origin"))
           and then Identity (Data, F (Data, Copy, "current"), F (Data, Captured, "identity"))
           and then Width (Data, Kcmp, 5) and then Width (Data, Args, 5)
           and then Text (Data, F (Data, Kcmp, "call"), "kcmp")
           and then Number_Is (Data, F (Data, Kcmp, "result"), 0) and then Number_Is (Data, F (Data, Kcmp, "errno"), 0)
           and then Same (Data, F (Data, Kcmp, "source"), Source)
           and then Same (Data, F (Data, Args, "pid1"), F (Data, Actor, "pid"))
           and then Same (Data, F (Data, Args, "pid2"), F (Data, Actor, "pid"))
           and then Number_Is (Data, F (Data, Args, "type"), 0)
           and then Same (Data, F (Data, Args, "idx1"), Source_FD)
           and then Same (Data, F (Data, Args, "idx2"), Alias_Source_FD)
           and then Text (Data, F (Data, Dup, "call"), "dup") and then Number_Is (Data, F (Data, Dup, "errno"), 0)
           and then Same (Data, F (Data, Dup, "source"), Source)
           and then Same (Data, F (Data, Dup, "result"), F (Data, Captured, "fd"))
           and then Same (Data, F (Data, F (Data, Dup, "args"), "fd"), Alias_Source_FD)
           and then Same (Data, F (Data, F (Data, Dup, "args"), "role"), Name)
           and then Width (Data, Copy_Kcmp, 5) and then Width (Data, Copy_Args, 5)
           and then Text (Data, F (Data, Copy_Kcmp, "call"), "kcmp")
           and then Number_Is (Data, F (Data, Copy_Kcmp, "result"), 0) and then Number_Is (Data, F (Data, Copy_Kcmp, "errno"), 0)
           and then Same (Data, F (Data, Copy_Kcmp, "source"), Source)
           and then Same (Data, F (Data, Copy_Args, "pid1"), F (Data, Actor, "pid"))
           and then Same (Data, F (Data, Copy_Args, "pid2"), F (Data, Actor, "pid"))
           and then Number_Is (Data, F (Data, Copy_Args, "type"), 0)
           and then Same (Data, F (Data, Copy_Args, "idx1"), Alias_Source_FD)
           and then Same (Data, F (Data, Copy_Args, "idx2"), F (Data, Captured, "fd")) then return True; end if;
         if Prior.Length > 0 and then Prior.Length < Here.Length
           and then Writer_Alias_Acquisition_Matches (Prior, Name, Declaration) then return True; end if;
         if Evolution_Prior.Length > 0 and then Evolution_Prior.Length < Here.Length
           and then Writer_Alias_Acquisition_Matches (Evolution_Prior, Name, Declaration) then return True; end if;
         for I in E.Count range 1 .. E.Array_Length (Data, Members (Data, Here_Closed)) loop
            declare Previous : constant E.Span := F (Data, Value (Data, Here_Closed, I - 1), "before_inventory"); begin
               if Previous.Length > 0 and then Previous.Length < Here.Length
                 and then Writer_Alias_Acquisition_Matches (Previous, Name, Declaration) then return True; end if;
            end;
         end loop;
         return False;
      end Writer_Alias_Acquisition_Matches;
   begin
      if Closed.Length = 0 then return True; end if;
      if not Valid (Data, Inventory) or else not Valid (Data, Closed)
        or else E.Decode (Data, Closed, E.Operation).Form /= E.Object_Value then return False; end if;
      for I in E.Count range 1 .. E.Array_Length (Data, Members (Data, Closed)) loop
         declare
            Name : constant E.Span := Key (Data, Closed, I - 1);
            Closure : constant E.Span := Value (Data, Closed, I - 1);
            Before : constant E.Span := F (Data, Closure, "before_inventory");
            Before_Frame : constant E.Span := F (Data, Before, "frame");
            Bound : constant E.Span := F (Data, Closure, "bound");
            Old_Row : constant E.Span := Find_Row (Data, F (Data, Before_Frame, "rows"), Bound);
            Row : constant E.Span := Find_Row (Data, F (Data, Frame, "rows"), Bound);
            Old_Role : constant E.Span := Find (Data, F (Data, Before, "roles"), "role", Name);
            Original : constant E.Span := Find (Data, F (Data, Before_Frame, "original_roles"), "role", Name);
            Alias : constant E.Span := F (Data, Closure, "alias");
            Alias_FD : constant E.Span := F (Data, Alias, "fd");
            Writer : constant E.Span := F (Data, Closure, "original_writer");
            Writer_FD : constant E.Span := F (Data, Writer, "fd");
            Actor : constant E.Span := F (Data, Closure, "actor");
            Source : constant E.Span := F (Data, Closure, "source");
            Kcmp : constant E.Span := F (Data, Alias, "kcmp");
            Args : constant E.Span := F (Data, Kcmp, "args");
            Stat : constant E.Span := F (Data, Old_Role, "fstat");
            Received : constant Boolean := not Is_None (Data, F (Data, Old_Role, "worker_fd"));
            Local_Writer : constant Boolean := Actor_Matches (Actor, F (Data, Writer, "actor"));
            Alias_Declaration : constant E.Span := Lookup (Data, F (Data, Before_Frame, "writer_aliases"), Name);
            Service_Alias : constant Boolean := Alias_Declaration.Length > 0;
            Source_Name : constant E.Span := (if Service_Alias then F (Data, Alias_Declaration, "source_descriptor") else Name);
         begin
            if not Width (Data, Closure, 10) or else not Width (Data, Writer, 4)
              or else not (Width (Data, Alias, 3) or else Width (Data, Alias, 4))
              or else (F (Data, Alias, "descriptor").Length > 0 and then not Same (Data, F (Data, Alias, "descriptor"), Name))
              or else not Same (Data, Closure, Lookup (Data, Closed, Name))
              or else Before.Length = 0 or else Before.Length >= Inventory.Length
              or else not Text (Data, F (Data, Before_Frame, "schema"), "worldline.complete-owned-scoped-descriptor-roster-v1")
              or else not Text (Data, F (Data, Closure, "role"), "stdin_fd")
              or else Old_Row.Length = 0 or else Row.Length = 0 or else Old_Role.Length = 0 or else Original.Length = 0
              or else not Same (Data, F (Data, Closure, "scope"), F (Data, F (Data, Old_Row, "row"), "scope"))
              or else not Same (Data, F (Data, Closure, "scope"), F (Data, F (Data, Row, "row"), "scope"))
              or else not Same (Data, Source_Name, F (Data, F (Data, Old_Row, "roles"), "stdin_fd"))
              or else not Is_None (Data, F (Data, F (Data, Row, "roles"), "stdin_fd"))
              or else Lookup (Data, F (Data, Frame, "retained_roles"), Name).Length > 0
              or else Lookup (Data, F (Data, Frame, "descriptors"), Name).Length > 0
              or else Lookup (Data, F (Data, Inventory, "current_descriptors"), Name).Length > 0
              or else Find (Data, F (Data, Frame, "original_roles"), "role", Name).Length > 0
              or else Find (Data, F (Data, Inventory, "roles"), "role", Name).Length > 0
              or else not FD (Data, Alias_FD) or else not FD (Data, Writer_FD)
              or else not Same (Data, Alias_FD, F (Data, Old_Role, (if Received then "worker_fd" else "front_fd")))
              or else not Same (Data, Alias_FD, F (Data, Stat, "fd"))
              or else not Same (Data, Alias_FD, F (Data, F (Data, Stat, "args"), "fd"))
              or else not Text (Data, F (Data, Stat, "call"), "fstat")
              or else not Number_Is (Data, F (Data, Stat, "result"), 0)
              or else not Number_Is (Data, F (Data, Stat, "errno"), 0)
              or else not Same (Data, F (Data, Stat, "source"), Source)
              or else not Identity (Data, F (Data, Alias, "identity"), F (Data, Stat, "identity"))
              or else not Identity (Data, F (Data, Alias, "identity"), F (Data, Old_Role, "current"))
              or else not Identity (Data, F (Data, Alias, "identity"), Lookup (Data, F (Data, Before, "current_descriptors"), Name))
              or else not Identity (Data, F (Data, Alias, "identity"), F (Data, Original, "identity"))
              or else not Identity (Data, F (Data, Alias, "identity"), F (Data, Writer, "identity"))
              or else not Actor_Matches (Actor, F (Data, Before, "current_actor"))
              or else not Writer_Lineage_Matches (Before, Source_Name, Writer)
              or else not Same (Data, Source, F (Data, Before, "current_source"))
              or else not Same (Data, Source, F (Data, Inventory, "current_source"))
              or else not Close_Matches (F (Data, Closure, "close"), Alias_FD, Source, Actor)
              or else not Close_Matches (F (Data, Closure, "original_close"), Writer_FD,
                F (Data, Writer, "source"), F (Data, Writer, "actor")) then return False; end if;
            if Service_Alias then
               if not Width (Data, Alias_Declaration, 8) or else not Width (Data, Alias, 4)
                 or else not Same (Data, F (Data, Alias, "descriptor"), Name)
                 or else not Text (Data, F (Data, Alias_Declaration, "role"), "stdin_fd")
                 or else not SF (Data, Alias_Declaration, Closure, "bound")
                 or else not SF (Data, Alias_Declaration, Closure, "scope")
                 or else not Identity (Data, F (Data, Alias_Declaration, "identity"), F (Data, Alias, "identity"))
                 or else Lookup (Data, F (Data, Frame, "writer_aliases"), Name).Length > 0
                 or else Lookup (Data, Closed, Source_Name).Length = 0
                 or else not Writer_Alias_Acquisition_Matches (Before, Name, Alias_Declaration) then return False; end if;
            end if;
            if not Local_Writer then
               --  The caller validates the complete preclose SCM/namespace/
               --  broker native roster. A remote observation does not invent
               --  a local comparison syscall against the original writer.
               if not Is_None (Data, Kcmp) then return False; end if;
            elsif not Same (Data, Source, F (Data, Writer, "source"))
              or else not Width (Data, Kcmp, 5) or else not Width (Data, Args, 5)
              or else not Text (Data, F (Data, Kcmp, "call"), "kcmp")
              or else not Number_Is (Data, F (Data, Kcmp, "result"), 0)
              or else not Number_Is (Data, F (Data, Kcmp, "errno"), 0)
              or else not Same (Data, F (Data, Kcmp, "source"), Source)
              or else not Same (Data, F (Data, Args, "pid1"), F (Data, Actor, "pid"))
              or else not Same (Data, F (Data, Args, "pid2"), F (Data, Actor, "pid"))
              or else not Number_Is (Data, F (Data, Args, "type"), 0)
              or else not Same (Data, F (Data, Args, "idx1"), Writer_FD)
              or else not Same (Data, F (Data, Args, "idx2"), Alias_FD) then return False; end if;
            if not SF (Data, Before_Frame, Frame, "schema")
              or else not SF (Data, Before_Frame, Frame, "installation")
              or else not SF (Data, Before_Frame, Frame, "resource_config")
              or else not SF (Data, Before_Frame, Frame, "source")
              or else not SF (Data, Before_Frame, Frame, "source_files")
              or else not Locks_Match (Data, F (Data, Before_Frame, "lease_locks"), F (Data, Frame, "lease_locks"))
              or else not Seq (Data, F (Data, Before, "roles"))
              or else not Seq (Data, F (Data, Before_Frame, "rows")) then return False; end if;
            for J in E.Count range 1 .. Len (Data, F (Data, Before_Frame, "rows")) loop
               declare
                  Previous_Row : constant E.Span := Item (Data, F (Data, Before_Frame, "rows"), J - 1);
                  Current_Row : constant E.Span := Find_Row (Data, F (Data, Frame, "rows"), F (Data, F (Data, Previous_Row, "row"), "bound"));
               begin
                  if Current_Row.Length = 0 or else not SF (Data, Previous_Row, Current_Row, "kind")
                    or else not SF (Data, F (Data, Previous_Row, "row"), F (Data, Current_Row, "row"), "scope") then return False; end if;
               end;
            end loop;
            for J in E.Count range 1 .. Len (Data, F (Data, Before, "roles")) loop
               declare
                  Previous_Role : constant E.Span := Item (Data, F (Data, Before, "roles"), J - 1);
                  Role_Name_Value : constant E.Span := F (Data, Previous_Role, "role");
               begin
                  --  Sequential EOFs may retire different writers. Each is
                  --  validated by its own authentic preclose record above.
                  if Lookup (Data, Closed, Role_Name_Value).Length = 0
                    and then not Role_Lineage_Matches (Inventory, Before, Role_Name_Value) then return False; end if;
               end;
            end loop;
            for J in E.Count range 1 .. E.Array_Length (Data, Members (Data, F (Data, Before_Frame, "writer_aliases"))) loop
               declare
                  Alias_Name : constant E.Span := Key (Data, F (Data, Before_Frame, "writer_aliases"), J - 1);
                  Declaration : constant E.Span := Value (Data, F (Data, Before_Frame, "writer_aliases"), J - 1);
               begin
                  if Lookup (Data, Closed, F (Data, Declaration, "source_descriptor")).Length > 0
                    and then Lookup (Data, Closed, Alias_Name).Length = 0 then return False; end if;
               end;
            end loop;
         end;
      end loop;
      return True;
   end Closed_Roles_Match;
   function Initial_Roles_Match (Data, Inventory_Data : E.Bytes; Transport, Inventory : E.Span) return Boolean is
      Initial : constant E.Span := F (Inventory_Data, Inventory, "initial_root_transport");
      Broker_Transfer : constant E.Span := F (Inventory_Data, F (Inventory_Data, Initial, "ofd_broker"), "transfer");
      Originals : constant E.Span := F (Inventory_Data, F (Inventory_Data, F (Inventory_Data, Initial, "frame"), "subject_custody"), "roles");
      Original_Roles : constant E.Span := F (Inventory_Data, Broker_Transfer, "roles");
      Roles : constant E.Span := F (Data, Transport, "roles");
      Current : constant E.Span := F (Inventory_Data, Inventory, "roles");
      Current_Root : constant E.Span := F (Inventory_Data, Initial, "current_roles");
      Closed : constant E.Span := F (Inventory_Data, F (Inventory_Data, Inventory, "frame"), "closed_roles");
      Image : constant E.Span := F (Data, Transport, "current_inventory");
      function Cross (Left, Right : E.Span) return Boolean is
        (RA.Ordered_Source_Value_Matches (Data, Inventory_Data, Left, Right, False, False));
   begin
      if not Initial_Root_Transport_Matches (Inventory_Data, Inventory)
        or else not Evolution_Matches (Inventory_Data, Inventory)
        or else not Bytes_Valid (Data, Image)
        or else not Width (Data, Transport, E.Array_Length (Inventory_Data, Members (Inventory_Data, Broker_Transfer)) + 1)
        or else not Seq (Data, Roles) or else Len (Data, Roles) /= Len (Inventory_Data, Original_Roles)
      then return False; end if;
      declare Raw : constant E.Bytes := Source_Bytes (Data, Image); begin
         if not RA.Ordered_Source_Value_Matches
           (Raw, Inventory_Data, (Raw'First, Raw'Length), Inventory, False, False) then return False; end if;
      end;
      for I in E.Count range 1 .. E.Array_Length (Inventory_Data, Members (Inventory_Data, Broker_Transfer)) loop
         declare
            Name : constant E.Span := Key (Inventory_Data, Broker_Transfer, I - 1);
            Found : Boolean := False;
         begin
            for J in E.Count range 1 .. E.Array_Length (Data, Members (Data, Transport)) loop
               if Cross (Key (Data, Transport, J - 1), Name) then
                  if Found or else not Cross (Value (Data, Transport, J - 1), Value (Inventory_Data, Broker_Transfer, I - 1)) then return False; end if;
                  Found := True;
               end if;
            end loop;
            if not Found then return False; end if;
         end;
      end loop;
      for I in E.Count range 1 .. Len (Data, Roles) loop
         declare
            Role : constant E.Span := Item (Data, Roles, I - 1);
            Name : constant E.Span := F (Data, Role, "role");
            Original : constant E.Span := Item (Inventory_Data, Originals, I - 1);
            Root_Current : constant E.Span := Item (Inventory_Data, Current_Root, I - 1);
            Match_Name, Before : E.Span := Empty;
            Live, Retired : Boolean := False;
            Scoped : Boolean := False;
         begin
            if not Cross (Name, F (Inventory_Data, Original, "role"))
              or else not Cross (F (Data, Role, "front_fd"), F (Inventory_Data, Original, "fd")) then return False; end if;
            declare
               Scoped_Originals : constant E.Span := F (Inventory_Data,
                 F (Inventory_Data, F (Inventory_Data, Initial, "frame"), "owned_descriptor_roster"), "original_roles");
            begin
               for J in E.Count range 1 .. Len (Inventory_Data, Scoped_Originals) loop
                  if Scoped_Name (Data, Inventory_Data, Name, F (Inventory_Data, Item (Inventory_Data, Scoped_Originals, J - 1), "role")) then
                     if Scoped then return False; end if;
                     Scoped := True;
                  end if;
               end loop;
            end;
            for J in E.Count range 1 .. Len (Inventory_Data, Current) loop
               declare Present : constant E.Span := Item (Inventory_Data, Current, J - 1); begin
                  if Scoped_Name (Data, Inventory_Data, Name, F (Inventory_Data, Present, "role")) then
                     if Live then return False; end if;
                     Match_Name := F (Inventory_Data, Present, "role"); Live := True;
                  end if;
               end;
            end loop;
            for J in E.Count range 1 .. E.Array_Length (Inventory_Data, Members (Inventory_Data, Closed)) loop
               declare Closed_Name : constant E.Span := Key (Inventory_Data, Closed, J - 1); begin
                  if Scoped_Name (Data, Inventory_Data, Name, Closed_Name) then
                     if Retired then return False; end if;
                     Before := F (Inventory_Data, Value (Inventory_Data, Closed, J - 1), "before_inventory");
                     Match_Name := Closed_Name; Retired := True;
                  end if;
               end;
            end loop;
            if Scoped /= (Live or else Retired) then return False; end if;
            if Live or else Retired then
               if Live = Retired or else not P.Scoped_Descriptor_Alias_Matches
                 (Inventory_Data, Data, (if Retired then Before else Inventory), Match_Name,
                  F (Data, Role, "worker_fd"), F (Data, Role, "current")) then return False; end if;
            elsif not Width (Inventory_Data, Root_Current, 12)
              or else not Cross (F (Data, Role, "worker_fd"), F (Inventory_Data, Root_Current, "worker_fd"))
              or else not Cross (F (Data, Role, "current"), F (Inventory_Data, Item (Inventory_Data, Original_Roles, I - 1), "current"))
            then return False; end if;
         end;
      end loop;
      return True;
   end Initial_Roles_Match;
   function Subject_Roles_Match (Data, Inventory_Data : E.Bytes;
     Transport, Inventory : E.Span) return Boolean
   is
      Roles : constant E.Span := F (Data, Transport, "roles");
      Frame : constant E.Span := F (Inventory_Data, Inventory, "frame");
      Current : constant E.Span := F (Inventory_Data, Inventory, "roles");
      Closed : constant E.Span := F (Inventory_Data, Frame, "closed_roles");
      Subject : constant E.Span := F (Inventory_Data, Inventory, "subject_transport");
      Original_Image : constant E.Span := F (Inventory_Data, Subject, "original_frame");
      Current_Image : constant E.Span := F (Data, Transport, "current_inventory");
      function Cross (Left, Right : E.Span) return Boolean is
        (RA.Ordered_Source_Value_Matches (Data, Inventory_Data, Left, Right, False, False));
   begin
      if F (Inventory_Data, Inventory, "initial_root_transport").Length > 0 then
         return Valid (Data, Transport) and then Valid (Inventory_Data, Inventory)
           and then Subject.Length = 0 and then Initial_Roles_Match (Data, Inventory_Data, Transport, Inventory);
      end if;
      if not Valid (Data, Transport) or else not Valid (Inventory_Data, Inventory)
        or else not Seq (Data, Roles) or else not Seq (Inventory_Data, Current)
        or else not Bytes_Valid (Data, Current_Image)
        or else not Bytes_Valid (Inventory_Data, Original_Image)
        or else not Cross (F (Data, Transport, "original_frame"), Original_Image)
        or else not Cross (F (Data, Transport, "received_sender"), F (Inventory_Data, Subject, "header_sender"))
        or else not Subject_Transport_Matches (Inventory_Data, Inventory)
        or else not Closed_Roles_Match (Inventory_Data, Inventory)
        or else not Evolution_Matches (Inventory_Data, Inventory) then return False; end if;
      declare
         Image : constant E.Bytes := Source_Bytes (Data, Current_Image);
         Original : constant E.Bytes := Source_Bytes (Inventory_Data, Original_Image);
         Original_Span : constant E.Span := (Original'First, Original'Length);
         Original_Roles : constant E.Span := F (Original, Original_Span, "original_roles");
      begin
         if not RA.Ordered_Source_Value_Matches
           (Image, Inventory_Data, (Image'First, Image'Length), Inventory, False, False)
           or else not Valid (Original, Original_Span) or else not Seq (Original, Original_Roles)
           or else Len (Data, Roles) /= Len (Original, Original_Roles) then return False; end if;
         for I in E.Count range 1 .. Len (Data, Roles) loop
            declare
               Role : constant E.Span := Item (Data, Roles, I - 1);
               Name : constant E.Span := F (Data, Role, "role");
               Original_Role : constant E.Span := Item (Original, Original_Roles, I - 1);
               Role_FD : constant E.Span := F (Data, Role,
                 (if Is_None (Data, F (Data, Role, "worker_fd")) then "front_fd" else "worker_fd"));
               Match_Name, Before : E.Span := Empty;
               Live, Retired : Boolean := False;
            begin
               if not RA.Ordered_Source_Value_Matches
                 (Data, Original, Name, F (Original, Original_Role, "role"), False, False)
                 or else not RA.Ordered_Source_Value_Matches
                   (Data, Original, F (Data, Role, "front_fd"), F (Original, Original_Role, "fd"), False, False)
                 or else not FD (Data, Role_FD) then return False; end if;
               for J in E.Count range 1 .. Len (Inventory_Data, Current) loop
                  declare Present : constant E.Span := Item (Inventory_Data, Current, J - 1); begin
                     if Cross (Name, F (Inventory_Data, Present, "role")) then
                        if Live then return False; end if;
                        Match_Name := F (Inventory_Data, Present, "role"); Live := True;
                     end if;
                  end;
               end loop;
               for J in E.Count range 1 .. E.Array_Length (Inventory_Data, Members (Inventory_Data, Closed)) loop
                  declare Closed_Name : constant E.Span := Key (Inventory_Data, Closed, J - 1); begin
                     if Cross (Name, Closed_Name) then
                        if Retired then return False; end if;
                        Before := F (Inventory_Data, Value (Inventory_Data, Closed, J - 1), "before_inventory");
                        Match_Name := Closed_Name; Retired := True;
                     end if;
                  end;
               end loop;
               if Live = Retired or else not P.Scoped_Descriptor_Alias_Matches
                 (Inventory_Data, Data, (if Retired then Before else Inventory), Match_Name,
                  Role_FD, F (Data, Role, "current")) then return False; end if;
            end;
         end loop;
      end;
      return True;
   end Subject_Roles_Match;
   function Subject_Roles_Match (Data : E.Bytes; Transport, Inventory : E.Span) return Boolean is
     (Subject_Roles_Match (Data, Data, Transport, Inventory));
   function Evolution_Matches (Data : E.Bytes; Inventory : E.Span) return Boolean is
      Frame : constant E.Span := F (Data, Inventory, "frame");
      Evolution : constant E.Span := F (Data, Frame, "evolution");
      Original : constant E.Span := F (Data, Evolution, "original_inventory");
      Before : constant E.Span := F (Data, Original, "frame");
      Copies : constant E.Span := F (Data, Evolution, "copies");
      Registry : constant E.Span := F (Data, Evolution, "local_registry");
      Old_Roles : constant E.Span := F (Data, Original, "roles");
      Roles : constant E.Span := F (Data, Inventory, "roles");
      Old_Originals : constant E.Span := F (Data, Before, "original_roles");
      Originals : constant E.Span := F (Data, Frame, "original_roles");
      Rows : constant E.Span := F (Data, Frame, "rows");
      Old_Rows : constant E.Span := F (Data, Before, "rows");
      Retained : constant E.Span := F (Data, Frame, "retained_roles");
      Old_Retained : constant E.Span := F (Data, Before, "retained_roles");
      Descriptors : constant E.Span := F (Data, Inventory, "current_descriptors");
      Old_Descriptors : constant E.Span := F (Data, Original, "current_descriptors");
      Source : constant E.Span := F (Data, Evolution, "source");
      Actor : constant E.Span := F (Data, Inventory, "current_actor");
      Origin_Actor : constant E.Span := F (Data, Original, "current_actor");
      PID : constant E.Span := F (Data, Origin_Actor, "pid");
      function Kcmp (Receipt, Origin_FD, Current_FD : E.Span) return Boolean is
         Args : constant E.Span := F (Data, Receipt, "args");
      begin
         return Width (Data, Receipt, 5) and then Width (Data, Args, 5)
           and then Text (Data, F (Data, Receipt, "call"), "kcmp")
           and then Number_Is (Data, F (Data, Receipt, "result"), 0)
           and then Number_Is (Data, F (Data, Receipt, "errno"), 0)
           and then Same (Data, F (Data, Receipt, "source"), Source)
           and then Same (Data, F (Data, Args, "pid1"), PID) and then Same (Data, F (Data, Args, "pid2"), PID)
           and then Number_Is (Data, F (Data, Args, "type"), 0)
           and then Same (Data, F (Data, Args, "idx1"), Origin_FD) and then Same (Data, F (Data, Args, "idx2"), Current_FD);
      end Kcmp;
      function Import_Matches (Role, Name, Identity_Value, Descriptor_Map : E.Span) return Boolean is
         Stat : constant E.Span := F (Data, Role, "fstat");
      begin
         return Role.Length > 0 and then FD (Data, F (Data, Stat, "fd"))
           and then Width (Data, Stat, 7) and then Width (Data, F (Data, Stat, "args"), 1)
           and then Same (Data, F (Data, Role, "role"), Name)
           and then Number_Is (Data, F (Data, Stat, "result"), 0) and then Number_Is (Data, F (Data, Stat, "errno"), 0)
           and then Text (Data, F (Data, Stat, "call"), "fstat")
           and then Same (Data, F (Data, Stat, "fd"), F (Data, F (Data, Stat, "args"), "fd"))
           and then Same (Data, F (Data, Stat, "fd"),
             (if Is_None (Data, F (Data, Role, "worker_fd")) then F (Data, Role, "front_fd")
              else F (Data, Role, "worker_fd")))
           and then Identity (Data, Identity_Value, F (Data, Role, "current"))
           and then Same (Data, F (Data, Stat, "identity"), F (Data, Role, "current"))
           and then Identity (Data, Identity_Value, Lookup (Data, Descriptor_Map, Name));
      end Import_Matches;
      function Original_Matches (Role, Captured : E.Span) return Boolean is
      begin
         return Captured.Length > 0 and then SF (Data, Role, Captured, "role")
           and then Same (Data, F (Data, Role, "front_fd"), F (Data, Captured, "fd"))
           and then Same (Data, F (Data, Role, "origin"), F (Data, Captured, "identity"))
           and then SF (Data, Role, Captured, "front_actor")
           and then SF (Data, Role, Captured, "worker_pidfd")
           and then SF (Data, Role, Captured, "lock_path");
      end Original_Matches;
      function Actor_Matches (Left, Right : E.Span) return Boolean is
        (SF (Data, Left, Right, "pid") and then SF (Data, Left, Right, "boot")
         and then SF (Data, Left, Right, "start_tick") and then SF (Data, Left, Right, "credentials"));
      function Fresh_Actor_Matches (Role, Captured : E.Span) return Boolean is
         Args : constant E.Span := F (Data, F (Data, Role, "kcmp"), "args");
      begin
         if not Actor_Matches (F (Data, Captured, "front_actor"), Origin_Actor) then return False; end if;
         if Is_None (Data, F (Data, Role, "worker_fd")) then
            return Actor_Matches (Actor, Origin_Actor);
         end if;
         --  Copy/local receipts are from the refresh process. A later genuine
         --  SCM receiver has different current FDs; original native custody
         --  establishes those cross-PID aliases, not this same-PID projection.
         return Same (Data, F (Data, Args, "pid1"), PID)
           and then Same (Data, F (Data, Args, "pid2"), F (Data, Actor, "pid"))
           and then Number_Is (Data, F (Data, Args, "type"), 0)
           and then Same (Data, F (Data, Args, "idx1"), F (Data, Role, "front_fd"))
           and then Same (Data, F (Data, Args, "idx2"), F (Data, Role, "worker_fd"));
      end Fresh_Actor_Matches;
   begin
      --  Initial capture has no predecessor. The caller still requires the
      --  original full source, role roster, custody and physical predicates.
      if Evolution.Length = 0 then
         return Valid (Data, Inventory)
           and then Text (Data, F (Data, Frame, "schema"), "worldline.complete-owned-scoped-descriptor-roster-v1");
      end if;
      if not Valid (Data, Inventory) or else not Width (Data, Evolution, 4)
        or else not Text (Data, F (Data, Frame, "schema"), "worldline.complete-owned-scoped-descriptor-roster-v1")
        or else not SF (Data, Before, Frame, "schema")
        or else not SF (Data, Before, Frame, "closed_roles")
        or else not Seq (Data, Copies) or else not Seq (Data, Registry) or else not Seq (Data, Old_Roles)
        or else not Seq (Data, Roles) or else not Seq (Data, Rows) or else not Seq (Data, Old_Rows)
        or else not Seq (Data, Old_Originals) or else not Seq (Data, Originals)
        or else Len (Data, Old_Originals) /= Len (Data, Old_Roles) or else Len (Data, Originals) /= Len (Data, Roles)
        or else (Retained.Length > 0 and then
          (not Valid (Data, Retained) or else E.Decode (Data, Retained, E.Operation).Form /= E.Object_Value))
        or else not Same (Data, Source, F (Data, Inventory, "current_source"))
        or else not Same (Data, Source, F (Data, Frame, "source"))
        or else not SF (Data, Original, Inventory, "current_source")
        or else not SF (Data, Before, Frame, "installation") or else not SF (Data, Before, Frame, "resource_config")
        or else not SF (Data, Before, Frame, "source_files")
        or else not Locks_Match (Data, F (Data, Before, "lease_locks"), F (Data, Frame, "lease_locks"))
        or else not FD (Data, PID) or else Number_Is (Data, PID, 0)
        or else not FD (Data, F (Data, Actor, "pid")) or else Number_Is (Data, F (Data, Actor, "pid"), 0)
        or else Len (Data, Copies) /= Len (Data, Old_Roles)
        or else E.Array_Length (Data, Members (Data, Old_Descriptors)) /= Len (Data, Old_Roles)
        or else E.Array_Length (Data, Members (Data, Descriptors)) /= Len (Data, Roles)
        or else not Descriptor_Maps_Match (Data, Descriptors, F (Data, Frame, "descriptors"))
        or else not Descriptor_Maps_Match (Data, Old_Descriptors, F (Data, Before, "descriptors")) then return False; end if;
      for I in E.Count range 1 .. Len (Data, Copies) loop
         declare
            Copy : constant E.Span := Item (Data, Copies, I - 1);
            Name : constant E.Span := F (Data, Copy, "role");
            Old_Role : constant E.Span := Find (Data, Old_Roles, "role", Name);
            Current_Role : constant E.Span := Find (Data, Roles, "role", Name);
         begin
            if not Width (Data, Copy, 6) or else Old_Role.Length = 0 or else Current_Role.Length = 0
              or else not Same (Data, Copy, Find (Data, Copies, "role", Name))
              or else not Import_Matches (Old_Role, Name, F (Data, Copy, "origin"), Old_Descriptors)
              or else not Original_Matches (Old_Role, Find (Data, Old_Originals, "role", Name))
              or else not Import_Matches (Current_Role, Name, F (Data, Copy, "current"), Descriptors)
              or else not Same (Data, F (Data, Copy, "origin_fd"), F (Data, F (Data, Old_Role, "fstat"), "fd"))
              or else not Same (Data, F (Data, Copy, "current_fd"), F (Data, Find (Data, Originals, "role", Name), "fd"))
              or else not Identity (Data, F (Data, Copy, "origin"), F (Data, Copy, "current"))
              or else not Kcmp (F (Data, Copy, "kcmp"), F (Data, Copy, "origin_fd"), F (Data, Copy, "current_fd")) then return False; end if;
         end;
      end loop;
      for I in E.Count range 1 .. Len (Data, Roles) loop
         declare Role : constant E.Span := Item (Data, Roles, I - 1); Name : constant E.Span := F (Data, Role, "role"); begin
            if not Same (Data, Role, Find (Data, Roles, "role", Name)) or else
              not Import_Matches (Role, Name, Lookup (Data, Descriptors, Name), Descriptors)
              or else not Original_Matches (Role, Find (Data, Originals, "role", Name))
              or else not Fresh_Actor_Matches (Role, Find (Data, Originals, "role", Name))
              or else not Same (Data, F (Data, F (Data, Role, "fstat"), "source"), Source) then return False; end if;
         end;
      end loop;
      for I in E.Count range 1 .. Len (Data, Old_Rows) loop
         declare Old_Row : constant E.Span := Item (Data, Old_Rows, I - 1);
           Current_Row : constant E.Span := Find_Row (Data, Rows, F (Data, F (Data, Old_Row, "row"), "bound")); begin
            if Current_Row.Length = 0
              or else not Same (Data, Old_Row, Find_Row (Data, Old_Rows, F (Data, F (Data, Old_Row, "row"), "bound")))
              or else not SF (Data, F (Data, Old_Row, "row"), F (Data, Current_Row, "row"), "scope") then return False; end if;
            for K in 1 .. 15 loop
               declare
                  Role : constant String := Role_Name (K);
                  Old_Value : constant E.Span := F (Data, F (Data, Old_Row, "roles"), Role);
                  Current_Value : constant E.Span := F (Data, F (Data, Current_Row, "roles"), Role);
                  Name : constant E.Span := (if K = 15 then F (Data, Old_Value, "descriptor") else Old_Value);
                  Declaration : constant E.Span := Lookup (Data, Retained, Name);
               begin
                  if Name.Length > 0 and then not Is_None (Data, Name)
                    and then Is_None (Data, Current_Value) then
                     if not Width (Data, Declaration, 3)
                       or else not Same (Data, F (Data, Declaration, "bound"), F (Data, F (Data, Old_Row, "row"), "bound"))
                       or else not Text (Data, F (Data, Declaration, "role"), Role) then return False; end if;
                  end if;
               end;
            end loop;
         end;
      end loop;
      --  A retained-only acquisition has current physical custody but is not
      --  an acquisition of the now-expired live row. Copies above still join
      --  every old/current FD and identity; this declaration supplies its
      --  original bound/scope lineage without replaying a current acquisition.
      for I in E.Count range 1 .. E.Array_Length (Data, Members (Data, Retained)) loop
         declare
            Name : constant E.Span := Key (Data, Retained, I - 1);
            Declaration : constant E.Span := Value (Data, Retained, I - 1);
            Bound : constant E.Span := F (Data, Declaration, "bound");
            Old_Row : constant E.Span := Find_Row (Data, Old_Rows, Bound);
            Row : constant E.Span := Find_Row (Data, Rows, Bound);
            Prior : constant E.Span := Lookup (Data, Old_Retained, Name);
            Kind_Matches : Boolean := False;
         begin
            if not Width (Data, Declaration, 3) or else Old_Row.Length = 0 or else Row.Length = 0
              or else not Same (Data, Declaration, Lookup (Data, Retained, Name))
              or else not Same (Data, F (Data, Declaration, "scope"), F (Data, F (Data, Old_Row, "row"), "scope"))
              or else not Same (Data, F (Data, Declaration, "scope"), F (Data, F (Data, Row, "row"), "scope"))
              or else Find (Data, Copies, "role", Name).Length = 0
              or else Find (Data, Old_Originals, "role", Name).Length = 0
              or else Find (Data, Originals, "role", Name).Length = 0
              or else Find (Data, Roles, "role", Name).Length = 0 then return False; end if;
            for K in 1 .. 15 loop
               declare
                  Role : constant String := Role_Name (K);
                  Old_Value : constant E.Span := F (Data, F (Data, Old_Row, "roles"), Role);
                  Current_Value : constant E.Span := F (Data, F (Data, Row, "roles"), Role);
               begin
                  if Text (Data, F (Data, Declaration, "role"), Role) then
                     Kind_Matches := Is_None (Data, Current_Value)
                       and then (Same (Data, Name,
                         (if K = 15 then F (Data, Old_Value, "descriptor") else Old_Value))
                         or else Same (Data, Declaration, Prior));
                  end if;
               end;
            end loop;
            if not Kind_Matches then return False; end if;
         end;
      end loop;
      for I in E.Count range 1 .. E.Array_Length (Data, Members (Data, Old_Retained)) loop
         declare
            Name : constant E.Span := Key (Data, Old_Retained, I - 1);
            Declaration : constant E.Span := Value (Data, Old_Retained, I - 1);
            Row : constant E.Span := Find_Row (Data, Rows, F (Data, Declaration, "bound"));
         begin
            for K in 1 .. 15 loop
               if Text (Data, F (Data, Declaration, "role"), Role_Name (K))
                 and then Is_None (Data, F (Data, F (Data, Row, "roles"), Role_Name (K)))
                 and then not Same (Data, Declaration, Lookup (Data, Retained, Name)) then return False; end if;
            end loop;
         end;
      end loop;
      for I in E.Count range 1 .. Len (Data, Registry) loop
         declare Roster_Entry : constant E.Span := Item (Data, Registry, I - 1);
           Row : constant E.Span := Find_Row (Data, Rows, F (Data, Roster_Entry, "bound"));
           Local : constant E.Span := F (Data, Roster_Entry, "descriptors");
           Row_Roles : constant E.Span := F (Data, Row, "roles"); begin
            if not Width (Data, Roster_Entry, 3) or else not Width (Data, Local, 13) or else Row.Length = 0
              or else not Same (Data, Roster_Entry, Find (Data, Registry, "bound", F (Data, Roster_Entry, "bound")))
              or else not SF (Data, Roster_Entry, Row, "kind") or else
              not (Text (Data, F (Data, Roster_Entry, "kind"), "ROOT") or else Text (Data, F (Data, Roster_Entry, "kind"), "ACTOR_V3")
                or else Text (Data, F (Data, Roster_Entry, "kind"), "SUPERVISOR_V1")) then return False; end if;
            for K in 1 .. 13 loop
               declare Role : constant String := Role_Name (K); Receipt : constant E.Span := F (Data, Local, Role);
                 Name : constant E.Span := F (Data, Row_Roles, Role); Absent : constant E.Span := F (Data, Receipt, "absence"); begin
                  if Is_None (Data, Receipt) then
                     if not Is_None (Data, Name) then return False; end if;
                  elsif Absent.Length > 0 then
                     if not Width (Data, Receipt, 2) or else not Width (Data, Absent, 5) or else not FD (Data, F (Data, Receipt, "fd"))
                       or else not Is_None (Data, Name) or else not Text (Data, F (Data, Absent, "call"), "dup")
                       or else not Number_Is (Data, F (Data, Absent, "result"), -1) or else not Number_Is (Data, F (Data, Absent, "errno"), 9)
                       or else not Same (Data, F (Data, Receipt, "fd"), F (Data, Absent, "fd"))
                       or else not Same (Data, Absent, F (Data, F (Data, F (Data, Row, "source"), "descriptor_absence"), Role)) then return False; end if;
                  else
                     declare Current : constant E.Span := Find (Data, Roles, "role", Name); begin
                        if not Width (Data, Receipt, 5) or else not FD (Data, F (Data, Receipt, "fd"))
                          or else not Same (Data, Name, F (Data, Receipt, "descriptor")) or else Current.Length = 0
                          or else not Import_Matches (Current, Name, F (Data, Receipt, "identity"), Descriptors)
                          or else not Same (Data, F (Data, Receipt, "current_fd"), F (Data, Find (Data, Originals, "role", Name), "fd"))
                          or else not Kcmp (F (Data, Receipt, "kcmp"), F (Data, Receipt, "fd"), F (Data, Receipt, "current_fd")) then return False; end if;
                     end;
                  end if;
               end;
            end loop;
         end;
      end loop;
      for I in E.Count range 1 .. Len (Data, Rows) loop
         declare Row : constant E.Span := Item (Data, Rows, I - 1); Bound : constant E.Span := F (Data, F (Data, Row, "row"), "bound");
           Old_Row : constant E.Span := Find_Row (Data, Old_Rows, Bound);
           Local : constant E.Span := Find (Data, Registry, "bound", Bound); begin
            if not Same (Data, Row, Find_Row (Data, Rows, Bound)) then return False; end if;
            if Local.Length = 0 then
               if Old_Row.Length > 0 and then not Is_None (Data, F (Data, Row, "kind")) then
                  if not SF (Data, Old_Row, Row, "kind") or else not SF (Data, Old_Row, Row, "roles") then return False; end if;
               elsif not Is_None (Data, F (Data, Row, "kind")) or else not Is_None (Data, F (Data, Row, "roles")) then return False; end if;
            end if;
         end;
      end loop;
      return True;
   end Evolution_Matches;
end Worldline.Scoped_Capture_Evolution_Projection;
