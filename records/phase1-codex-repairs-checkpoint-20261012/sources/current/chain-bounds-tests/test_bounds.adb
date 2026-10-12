-- Additive original-domain range control, unrun until controlled actual build.
with Ada.Assertions;
with Resource_Quantities;
with Worldline;
with Worldline.Chain_Authority;
procedure Test_Bounds is
   package Q renames Resource_Quantities;
   package A renames Worldline.Chain_Authority;
   use type Q.Byte_Count;
   use type A.Reason;
   use type A.Result;
   use type Worldline.Hash;
   Genesis : constant Worldline.Hash := [others => 0];
   Payload : constant Worldline.Hash := [others => 1];
   function Present_Digest (H : Worldline.Hash) return A.Optional_Digest is
     ((Present => True, Value => H));
begin
   for Kind in A.Chain_Kind loop
      declare
         Head : constant Worldline.Hash := A.Link (Kind, Genesis, Payload);
         Last_Row : constant A.Chain_Row :=
           (Previous => Present_Digest (Genesis), Actual_Payload_Root => Present_Digest (Payload),
            Stored_Payload_Root => Present_Digest (Payload), Stored_Head => Present_Digest (Head));
         Singleton : constant A.Retained_Rows (Q.Byte_Index'Last .. Q.Byte_Index'Last) :=
           [others => Last_Row];
         R : constant A.Result := A.Replay
           (Kind, Singleton, Present_Digest (Genesis), Present_Digest (Genesis), Present_Digest (Head));
      begin
         Ada.Assertions.Assert (R.Disposition = A.Ready);
         Ada.Assertions.Assert (R.Head = Head and then R.Accepted_Count = Singleton'Length);
         pragma Assert (A.Prefix_Reference (Kind, Singleton, Genesis, Singleton'Length) = R);
      end;
      declare
         Rows : A.Retained_Rows (Q.Byte_Index'Last - 1 .. Q.Byte_Index'Last);
         Head : Worldline.Hash := Genesis;
         R : A.Result;
      begin
         for I in Rows'Range loop
            Rows (I) :=
              (Previous => Present_Digest (Head), Actual_Payload_Root => Present_Digest (Payload),
               Stored_Payload_Root => Present_Digest (Payload),
               Stored_Head => Present_Digest (A.Link (Kind, Head, Payload)));
            Head := Rows (I).Stored_Head.Value;
         end loop;
         R := A.Replay (Kind, Rows, Present_Digest (Genesis), Present_Digest (Genesis), Present_Digest (Head));
         Ada.Assertions.Assert (R.Disposition = A.Ready);
         Ada.Assertions.Assert (R.Head = Head and then R.Accepted_Count = Rows'Length);
         pragma Assert (A.Prefix_Reference (Kind, Rows, Genesis, Rows'Length) = R);
         Rows (Rows'Last).Stored_Head := Present_Digest (Genesis);
         R := A.Replay (Kind, Rows, Present_Digest (Genesis), Present_Digest (Genesis), Present_Digest (Head));
         Ada.Assertions.Assert (R.Disposition = A.Stored_Head_Mismatch);
         Ada.Assertions.Assert (R.Head = Rows (Rows'First).Stored_Head.Value);
         Ada.Assertions.Assert (R.Accepted_Count = Rows'Length - 1);
      end;
   end loop;
end Test_Bounds;
