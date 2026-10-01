package body Evaluation_History with SPARK_Mode is

   use SPARK.Big_Integers;
   use type Resource_Quantities.Ordering;
   function Same_Epoch (A : Byte_Array; L, R : Epoch_Id) return Boolean is
     (Epoch_Valid (A, L) and then Epoch_Valid (A, R) and then
      Resource_Quantities.Compare (A, Epoch_Quantity (L), Epoch_Quantity (R)) =
        Resource_Quantities.Equal);

   function Next_Epoch (A : Byte_Array; Before, After : Epoch_Id) return Boolean is
      package Q renames Resource_Quantities;
      Width : constant Byte_Count := Byte_Count'Max (Before.Length, After.Length);
      Carry : Natural range 0 .. 1 := 1;
      Total : Natural range 0 .. 256;
   begin
      if not Epoch_Valid (A, Before) or else not Epoch_Valid (A, After) then
         return False;
      end if;
      if Width = 0 then
         return False;
      end if;
      for Offset in Byte_Count range 0 .. Width - 1 loop
         pragma Loop_Invariant
           (Q.Prefix_Value (A, Epoch_Quantity (After), Offset) +
              To_Big_Integer (Carry) * Q.Radix_Power (Offset) =
            Q.Prefix_Value (A, Epoch_Quantity (Before), Offset) + 1);
         Total := Q.Digit (A, Epoch_Quantity (Before), Offset) + Carry;
         if Q.Digit (A, Epoch_Quantity (After), Offset) /= Total mod 256 then
            return False;
         end if;
         Carry := Total / 256;
      end loop;
      return Carry = 0;
   end Next_Epoch;

   function Find_Completed_Failure
     (A : Byte_Array; H : History; F : Optional_Record; Q : Query) return Record_Reference is
   begin
      if F.Present and then Is_Current_Failure (A, F.Value, Q) then
         return (Kind => Finalization);
      end if;
      for I in H'Range loop
         if Is_Current_Failure (A, H (I), Q) then
            return (Kind => History_Entry, Index => I);
         end if;
         pragma Loop_Invariant
           (for all J in H'First .. I => not Is_Current_Failure (A, H (J), Q));
      end loop;
      return No_Record;
   end Find_Completed_Failure;

   function Select_Evidence
     (A : Byte_Array; H : History; F : Optional_Record; Q : Query) return Selection is
      Head : Optional_Record;
      Answer : Selection :=
        (Reason => Input_Absent, Head => No_Record,
         Completed_Failure => No_Record);
   begin
      if not Query_Complete (Q) then
         return Answer;
      elsif not Query_Valid (A, Q) then
         Answer.Reason := Input_Invalid;
         return Answer;
      elsif not Finalization_Valid (A, F, Q) then
         Answer.Reason := Finalization_Invalid;
         return Answer;
      elsif not History_Valid (A, H, F, Q) then
         Answer.Reason := History_Invalid;
         return Answer;
      end if;

      --  Head selection never compares outcomes or searches for an older
      --  requirement match.  A retained newer attempt permanently wins this
      --  selection; it may refuse without making any earlier record speak.
      if H'Length /= 0 then
         Head := (Present => True, Value => H (H'Last));
         Answer.Head := (Kind => History_Entry, Index => H'Last);
      else
         Head := F;
         Answer.Head :=
           (if F.Present then (Kind => Finalization) else No_Record);
      end if;
      Answer.Completed_Failure := Find_Completed_Failure (A, H, F, Q);

      if not Head.Present then
         Answer.Reason := Evidence_Absent;
      elsif not Cursor_Matches (A, Q.Current_Head, Head.Value)
        or else not Cursor_Matches (A, Q.Prepared_Evidence, Head.Value)
      then
         Answer.Reason := Evidence_Superseded;
      elsif not Q.Requirement.Present or else
            not Head.Value.Requirement.Present
      then
         Answer.Reason := Requirement_Absent;
      elsif not Same_Identity (A, Identity_Span (Head.Value.Requirement.Value), Identity_Span (Q.Requirement.Value)) then
         Answer.Reason := Requirement_Changed;
      elsif Head.Value.State = Rollback_Fence then
         Answer.Reason := Evidence_Fenced;
      elsif Head.Value.State /= Completed then
         Answer.Reason := Evaluation_Incomplete;
      elsif Answer.Completed_Failure.Kind /= Absent then
         Answer.Reason := Evidence_Fail_Terminal;
      elsif Head.Value.Outcome /= Passed then
         Answer.Reason := Evaluation_Incomplete;
      else
         Answer.Reason := Ready;
      end if;
      return Answer;
   end Select_Evidence;
end Evaluation_History;
