package body Worldline.Chain_Authority with SPARK_Mode is
   procedure Link_Bytes
     (Kind : Chain_Kind; Left, Right, Payload : Hash)
   with Ghost, Global => null, Always_Terminates,
     Pre => Left = Right,
     Post => Link (Kind, Left, Payload) = Link (Kind, Right, Payload)
   is
   begin
      pragma Assert (Hash_Eq (Left, Right));
      pragma Assert (Hash_Eq (Payload, Payload));
   end Link_Bytes;

   procedure Receipt_At_Head
     (Previous, Head, Payload, Current : Hash)
   with Ghost, Global => null, Always_Terminates,
     Pre => Previous = Head
       and then Current = Receipts.Link (Previous, Payload),
     Post => Current = Link (Receipt_Chain, Head, Payload)
   is
   begin
      pragma Assert (Hash_Eq (Previous, Head));
      pragma Assert (Hash_Eq (Payload, Payload));
   end Receipt_At_Head;

   procedure Causal_At_Head
     (Previous, Head, Payload, Current : Hash)
   with Ghost, Global => null, Always_Terminates,
     Pre => Previous = Head
       and then Current = Causal_Graph.Link (Previous, Payload),
     Post => Current = Link (Causal_Chain, Head, Payload)
   is
   begin
      pragma Assert (Hash_Eq (Previous, Head));
      pragma Assert (Hash_Eq (Payload, Payload));
   end Causal_At_Head;

   procedure Step_Image
     (Kind : Chain_Kind; Rows : Retained_Rows; Genesis : Hash;
      Count : Q.Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Count < Rows'Length,
     Post => Prefix_Reference (Kind, Rows, Genesis, Count + 1) =
       Prefix_Step
         (Kind, Rows (Rows'First + Count),
          Prefix_Reference (Kind, Rows, Genesis, Count), Count + 1)
   is
   begin
      null;
   end Step_Image;

   procedure Step_Same
     (Kind : Chain_Kind; Row : Chain_Row; Left, Right : Result;
      Count : Q.Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Left = Right and then
       (case Kind is
          when Receipt_Chain | Causal_Chain => Count >= Q.Byte_Count'First) and then
       (Row.Previous.Present or else not Row.Previous.Present),
     Post => Prefix_Step (Kind, Row, Left, Count) =
       Prefix_Step (Kind, Row, Right, Count)
   is
   begin
      pragma Assert (Left.Disposition = Right.Disposition);
      pragma Assert (Left.Head = Right.Head);
      pragma Assert (Left.Accepted_Count = Right.Accepted_Count);
      if Left.Disposition /= Ready then
         pragma Assert (Prefix_Step (Kind, Row, Left, Count) = Left);
         pragma Assert (Prefix_Step (Kind, Row, Right, Count) = Right);
      elsif not Present (Row) then
         pragma Assert
           (Prefix_Step (Kind, Row, Left, Count) =
              (Disposition => Row_Absent, Head => Left.Head,
               Accepted_Count => Left.Accepted_Count));
         pragma Assert
           (Prefix_Step (Kind, Row, Right, Count) =
              (Disposition => Row_Absent, Head => Right.Head,
               Accepted_Count => Right.Accepted_Count));
      elsif not R.Same (Row.Actual_Payload_Root, Row.Stored_Payload_Root) then
         pragma Assert
           (Prefix_Step (Kind, Row, Left, Count) =
              (Disposition => Payload_Mismatch, Head => Left.Head,
               Accepted_Count => Left.Accepted_Count));
         pragma Assert
           (Prefix_Step (Kind, Row, Right, Count) =
              (Disposition => Payload_Mismatch, Head => Right.Head,
               Accepted_Count => Right.Accepted_Count));
      elsif Row.Previous.Value /= Left.Head then
         pragma Assert
           (Prefix_Step (Kind, Row, Left, Count) =
              (Disposition => Predecessor_Mismatch, Head => Left.Head,
               Accepted_Count => Left.Accepted_Count));
         pragma Assert
           (Prefix_Step (Kind, Row, Right, Count) =
              (Disposition => Predecessor_Mismatch, Head => Right.Head,
               Accepted_Count => Right.Accepted_Count));
      elsif Row.Stored_Head.Value /=
        Link (Kind, Left.Head, Row.Actual_Payload_Root.Value)
      then
         Link_Bytes
           (Kind, Left.Head, Right.Head, Row.Actual_Payload_Root.Value);
         pragma Assert
           (Row.Stored_Head.Value /=
              Link (Kind, Right.Head, Row.Actual_Payload_Root.Value));
         pragma Assert
           (Prefix_Step (Kind, Row, Left, Count) =
              (Disposition => Stored_Head_Mismatch, Head => Left.Head,
               Accepted_Count => Left.Accepted_Count));
         pragma Assert
           (Prefix_Step (Kind, Row, Right, Count) =
              (Disposition => Stored_Head_Mismatch, Head => Right.Head,
               Accepted_Count => Right.Accepted_Count));
      else
         Link_Bytes
           (Kind, Left.Head, Right.Head, Row.Actual_Payload_Root.Value);
         pragma Assert
           (Row.Stored_Head.Value =
              Link (Kind, Right.Head, Row.Actual_Payload_Root.Value));
         pragma Assert
           (Prefix_Step (Kind, Row, Left, Count) =
              (Disposition => Ready, Head => Row.Stored_Head.Value,
               Accepted_Count => Count));
         pragma Assert
           (Prefix_Step (Kind, Row, Right, Count) =
              (Disposition => Ready, Head => Row.Stored_Head.Value,
               Accepted_Count => Count));
      end if;
   end Step_Same;

   procedure Step_Row
     (Kind : Chain_Kind; Left, Right : Chain_Row; Before : Result;
      Count : Q.Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Left = Right,
     Post => Prefix_Step (Kind, Left, Before, Count) =
       Prefix_Step (Kind, Right, Before, Count)
   is
   begin
      pragma Assert (Hash_Eq (Left.Previous.Value, Right.Previous.Value));
      pragma Assert
        (Hash_Eq (Left.Actual_Payload_Root.Value, Right.Actual_Payload_Root.Value));
      pragma Assert
        (Hash_Eq (Left.Stored_Payload_Root.Value, Right.Stored_Payload_Root.Value));
      pragma Assert (Hash_Eq (Left.Stored_Head.Value, Right.Stored_Head.Value));
   end Step_Row;

   procedure Prove_Predecessor
     (Kind : Chain_Kind; Row : Chain_Row; Expected : Result;
      Count : Q.Byte_Count; Head : Hash)
   with Ghost, Global => null, Always_Terminates,
     Pre => Count < Q.Byte_Count'Last and then
       Expected.Disposition = Ready and then Expected.Head = Head
       and then Expected.Accepted_Count = Count and then Present (Row)
       and then R.Same (Row.Actual_Payload_Root, Row.Stored_Payload_Root)
       and then Row.Previous.Value /= Head,
     Post => Prefix_Step (Kind, Row, Expected, Count + 1) =
       (Disposition => Predecessor_Mismatch, Head => Head, Accepted_Count => Count)
   is
   begin
      null;
   end Prove_Predecessor;

   procedure Prove_Stored
     (Kind : Chain_Kind; Row : Chain_Row; Expected : Result;
      Count : Q.Byte_Count; Head : Hash)
   with Ghost, Global => null, Always_Terminates,
     Pre => Count < Q.Byte_Count'Last and then
       Expected.Disposition = Ready and then Expected.Head = Head
       and then Expected.Accepted_Count = Count and then Present (Row)
       and then R.Same (Row.Actual_Payload_Root, Row.Stored_Payload_Root)
       and then Row.Previous.Value = Head
       and then Row.Stored_Head.Value /=
         Link (Kind, Head, Row.Actual_Payload_Root.Value),
     Post => Prefix_Step (Kind, Row, Expected, Count + 1) =
       (Disposition => Stored_Head_Mismatch, Head => Head, Accepted_Count => Count)
   is
   begin
      Link_Bytes
        (Kind, Expected.Head, Head, Row.Actual_Payload_Root.Value);
   end Prove_Stored;

   procedure Prove_Ready
     (Kind : Chain_Kind; Row : Chain_Row; Expected : Result; Count : Q.Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Count < Q.Byte_Count'Last and then
       Expected.Disposition = Ready and then Expected.Accepted_Count = Count
       and then Present (Row)
       and then R.Same (Row.Actual_Payload_Root, Row.Stored_Payload_Root)
       and then Row.Previous.Value = Expected.Head
       and then Row.Stored_Head.Value =
         Link (Kind, Expected.Head, Row.Actual_Payload_Root.Value),
     Post => Prefix_Step (Kind, Row, Expected, Count + 1) =
       (Disposition => Ready, Head => Row.Stored_Head.Value,
        Accepted_Count => Count + 1)
   is
   begin
      null;
   end Prove_Ready;

   procedure Prefix_Stays
     (Kind : Chain_Kind; Rows : Retained_Rows; Genesis : Hash;
      From, To : Q.Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => From <= To and then To <= Rows'Length and then
       Prefix_Reference (Kind, Rows, Genesis, From).Disposition /= Ready,
     Post => Prefix_Reference (Kind, Rows, Genesis, To) =
       Prefix_Reference (Kind, Rows, Genesis, From),
     Subprogram_Variant => (Decreases => To - From)
   is
      pragma Annotate (GNATprove, Hide_Info, "Expression_Function_Body", Prefix_Reference);
   begin
      if To > From then
         Prefix_Stays (Kind, Rows, Genesis, From, To - 1);
         Step_Image (Kind, Rows, Genesis, To - 1);
         Step_Same
           (Kind, Rows (Rows'First + (To - 1)),
            Prefix_Reference (Kind, Rows, Genesis, To - 1),
            Prefix_Reference (Kind, Rows, Genesis, From), To);
         pragma Assert
           (Prefix_Step
              (Kind, Rows (Rows'First + (To - 1)),
               Prefix_Reference (Kind, Rows, Genesis, To - 1), To) =
            Prefix_Reference (Kind, Rows, Genesis, To - 1));
      end if;
   end Prefix_Stays;

   procedure Note_Base
     (Kind : Chain_Kind; Rows : Retained_Rows; Genesis : Hash; Expected : Result)
   with Ghost, Global => null, Always_Terminates,
     Pre => Expected = (Disposition => Ready, Head => Genesis, Accepted_Count => 0),
     Post => Expected = Prefix_Reference (Kind, Rows, Genesis, 0)
   is
   begin
      null;
   end Note_Base;

   procedure Close_Stopped
     (Kind : Chain_Kind; Rows : Retained_Rows; Genesis : Hash;
      Observed_Genesis, Witnessed_Genesis, Witnessed_Head : Optional_Digest;
      Count : Q.Byte_Count; Expected : Result; Row : Chain_Row; Stopped : Result)
   with Ghost, Global => null, Always_Terminates,
     Pre => Observed_Genesis.Present and then Witnessed_Genesis.Present
       and then Witnessed_Head.Present and then
       R.Same (Observed_Genesis, Witnessed_Genesis) and then
       Count < Rows'Length and then
       Row = Rows (Rows'First + Count) and then
       Expected = Prefix_Reference (Kind, Rows, Genesis, Count) and then
       Expected.Disposition = Ready and then
       Stopped = Prefix_Step (Kind, Row, Expected, Count + 1) and then
       Stopped.Disposition /= Ready and then
       Genesis = Observed_Genesis.Value,
     Post => Replay_Reference
       (Kind, Rows, Observed_Genesis, Witnessed_Genesis, Witnessed_Head) = Stopped
   is
      pragma Annotate (GNATprove, Hide_Info, "Expression_Function_Body", Prefix_Reference);
      pragma Annotate (GNATprove, Hide_Info, "Expression_Function_Body", Prefix_Step);
      pragma Annotate (GNATprove, Hide_Info, "Expression_Function_Body", Replay_Reference);
   begin
      Step_Image (Kind, Rows, Genesis, Count);
      Step_Same
        (Kind, Row, Expected, Prefix_Reference (Kind, Rows, Genesis, Count), Count + 1);
      Step_Row
        (Kind, Row, Rows (Rows'First + Count),
         Prefix_Reference (Kind, Rows, Genesis, Count), Count + 1);
      pragma Assert
        (Prefix_Reference (Kind, Rows, Genesis, Count + 1) = Stopped);
      Prefix_Stays (Kind, Rows, Genesis, Count + 1, Rows'Length);
      pragma Assert (Hash_Eq (Genesis, Observed_Genesis.Value));
      pragma Assert
        (Finish_Reference
           (Prefix_Reference (Kind, Rows, Genesis, Rows'Length),
            Witnessed_Head.Value) = Stopped);
      pragma Assert
        (Replay_Reference
           (Kind, Rows, Observed_Genesis, Witnessed_Genesis, Witnessed_Head) =
         Finish_Reference
           (Prefix_Reference
              (Kind, Rows, Observed_Genesis.Value, Rows'Length),
            Witnessed_Head.Value));
   end Close_Stopped;

   procedure Advance
     (Kind : Chain_Kind; Rows : Retained_Rows; Genesis : Hash;
      Count : Q.Byte_Count; Row : Chain_Row; Expected : in out Result)
   with Ghost, Global => null, Always_Terminates,
     Pre => Count < Rows'Length and then
       Row = Rows (Rows'First + Count) and then
       Expected = Prefix_Reference (Kind, Rows, Genesis, Count) and then
       Prefix_Step (Kind, Row, Expected, Count + 1) =
         (Disposition => Ready, Head => Row.Stored_Head.Value,
          Accepted_Count => Count + 1),
     Post => Expected = Prefix_Reference (Kind, Rows, Genesis, Count + 1) and then
       Expected = (Disposition => Ready, Head => Row.Stored_Head.Value,
                   Accepted_Count => Count + 1)
   is
      pragma Annotate (GNATprove, Hide_Info, "Expression_Function_Body", Prefix_Reference);
      pragma Annotate (GNATprove, Hide_Info, "Expression_Function_Body", Prefix_Step);
      Previous : constant Result := Expected;
   begin
      Step_Image (Kind, Rows, Genesis, Count);
      Step_Same
        (Kind, Row, Previous, Prefix_Reference (Kind, Rows, Genesis, Count), Count + 1);
      Step_Row
        (Kind, Row, Rows (Rows'First + Count),
         Prefix_Reference (Kind, Rows, Genesis, Count), Count + 1);
      Expected :=
        (Disposition => Ready, Head => Row.Stored_Head.Value,
         Accepted_Count => Count + 1);
   end Advance;

   procedure Close_Finished
     (Kind : Chain_Kind; Rows : Retained_Rows;
      Observed_Genesis, Witnessed_Genesis, Witnessed_Head : Optional_Digest;
      Expected : Result; Current : Hash; Count : Q.Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Observed_Genesis.Present and then Witnessed_Genesis.Present
       and then Witnessed_Head.Present and then
       R.Same (Observed_Genesis, Witnessed_Genesis) and then
       Count = Rows'Length and then
       Expected = Prefix_Reference (Kind, Rows, Observed_Genesis.Value, Count)
       and then Expected.Disposition = Ready and then Expected.Head = Current
       and then Expected.Accepted_Count = Count,
     Post => Replay_Reference
       (Kind, Rows, Observed_Genesis, Witnessed_Genesis, Witnessed_Head) =
       Finish_Reference (Expected, Witnessed_Head.Value)
   is
      pragma Annotate (GNATprove, Hide_Info, "Expression_Function_Body", Prefix_Reference);
   begin
      null;
   end Close_Finished;

   function Replay
     (Kind : Chain_Kind; Rows : Retained_Rows;
      Observed_Genesis, Witnessed_Genesis, Witnessed_Head : Optional_Digest)
      return Result
   is
      pragma Annotate (GNATprove, Hide_Info, "Expression_Function_Body", Prefix_Reference);
      Receipt : Receipts.Chain := Receipts.New_Chain (Observed_Genesis.Value);
      Causal : Causal_Graph.Chain := Causal_Graph.New_Chain (Observed_Genesis.Value);
      Current : Hash := Observed_Genesis.Value;
      Count : Q.Byte_Count := 0;
      Expected : Result :=
        (Disposition => Ready, Head => Observed_Genesis.Value, Accepted_Count => 0)
        with Ghost;
   begin
      if not Observed_Genesis.Present or else not Witnessed_Genesis.Present
        or else not Witnessed_Head.Present
      then
         return (Disposition => Anchor_Absent, Head => [others => 0],
                 Accepted_Count => 0);
      elsif not R.Same (Observed_Genesis, Witnessed_Genesis) then
         return (Disposition => Genesis_Mismatch, Head => Current,
                 Accepted_Count => 0);
      end if;
      Note_Base (Kind, Rows, Observed_Genesis.Value, Expected);
      for I in Rows'Range loop
         pragma Loop_Invariant (Count = I - Rows'First);
         pragma Loop_Invariant (Count < Q.Byte_Count'Last);
         pragma Loop_Invariant (Count <= Rows'Length);
         pragma Loop_Invariant (Expected.Disposition = Ready);
         pragma Loop_Invariant (Expected.Head = Current);
         pragma Loop_Invariant (Expected.Accepted_Count = Count);
         pragma Loop_Invariant
           (Expected = Prefix_Reference
              (Kind, Rows, Observed_Genesis.Value, Count));
         pragma Loop_Invariant
           (if Kind = Receipt_Chain then
              Receipts.Accepted (Receipt) and then Receipts.Head (Receipt) = Current
            else Causal_Graph.Accepted (Causal) and then Causal_Graph.Head (Causal) = Current);
         declare
            Row : constant Chain_Row := Rows (I);
            Before : constant Hash := Current;
         begin
            if not Present (Row) then
               Close_Stopped
                 (Kind, Rows, Observed_Genesis.Value,
                  Observed_Genesis, Witnessed_Genesis, Witnessed_Head,
                  Count, Expected, Row,
                  (Disposition => Row_Absent, Head => Current, Accepted_Count => Count));
               return (Disposition => Row_Absent, Head => Current,
                       Accepted_Count => Count);
            elsif not R.Same (Row.Actual_Payload_Root, Row.Stored_Payload_Root) then
               Close_Stopped
                 (Kind, Rows, Observed_Genesis.Value,
                  Observed_Genesis, Witnessed_Genesis, Witnessed_Head,
                  Count, Expected, Row,
                  (Disposition => Payload_Mismatch, Head => Current,
                   Accepted_Count => Count));
               return (Disposition => Payload_Mismatch, Head => Current,
                       Accepted_Count => Count);
            end if;
            case Kind is
               when Receipt_Chain =>
                  Receipts.Append (Receipt, Row.Previous.Value,
                                   Row.Actual_Payload_Root.Value);
                  if not Receipts.Accepted (Receipt) then
                     Prove_Predecessor (Kind, Row, Expected, Count, Current);
                     Close_Stopped
                       (Kind, Rows, Observed_Genesis.Value,
                        Observed_Genesis, Witnessed_Genesis, Witnessed_Head,
                        Count, Expected, Row,
                        (Disposition => Predecessor_Mismatch, Head => Current,
                         Accepted_Count => Count));
                     return (Disposition => Predecessor_Mismatch, Head => Current,
                             Accepted_Count => Count);
                  end if;
                  Current := Receipts.Head (Receipt);
                  pragma Assert
                    (Current = Receipts.Link
                       (Row.Previous.Value, Row.Actual_Payload_Root.Value));
                  pragma Assert (Before = Expected.Head);
                  pragma Assert (Row.Previous.Value = Before);
                  Receipt_At_Head
                    (Row.Previous.Value, Before,
                     Row.Actual_Payload_Root.Value, Current);
                  if Current /= Row.Stored_Head.Value then
                     Prove_Stored (Kind, Row, Expected, Count, Before);
                     Close_Stopped
                       (Kind, Rows, Observed_Genesis.Value,
                        Observed_Genesis, Witnessed_Genesis, Witnessed_Head,
                        Count, Expected, Row,
                        (Disposition => Stored_Head_Mismatch, Head => Before,
                         Accepted_Count => Count));
                     return (Disposition => Stored_Head_Mismatch, Head => Before,
                             Accepted_Count => Count);
                  end if;
                  pragma Assert (Current = Row.Stored_Head.Value);
                  pragma Assert
                    (Current = Link
                       (Kind, Before, Row.Actual_Payload_Root.Value));
                  Link_Bytes
                    (Kind, Before, Expected.Head, Row.Actual_Payload_Root.Value);
                  Prove_Ready (Kind, Row, Expected, Count);
                  Advance
                    (Kind, Rows, Observed_Genesis.Value, Count, Row, Expected);
                  Count := Count + 1;
               when Causal_Chain =>
                  Causal_Graph.Append (Causal, Row.Previous.Value,
                                       Row.Actual_Payload_Root.Value);
                  if not Causal_Graph.Accepted (Causal) then
                     Prove_Predecessor (Kind, Row, Expected, Count, Current);
                     Close_Stopped
                       (Kind, Rows, Observed_Genesis.Value,
                        Observed_Genesis, Witnessed_Genesis, Witnessed_Head,
                        Count, Expected, Row,
                        (Disposition => Predecessor_Mismatch, Head => Current,
                         Accepted_Count => Count));
                     return (Disposition => Predecessor_Mismatch, Head => Current,
                             Accepted_Count => Count);
                  end if;
                  Current := Causal_Graph.Head (Causal);
                  pragma Assert
                    (Current = Causal_Graph.Link
                       (Row.Previous.Value, Row.Actual_Payload_Root.Value));
                  pragma Assert (Before = Expected.Head);
                  pragma Assert (Row.Previous.Value = Before);
                  Causal_At_Head
                    (Row.Previous.Value, Before,
                     Row.Actual_Payload_Root.Value, Current);
                  if Current /= Row.Stored_Head.Value then
                     Prove_Stored (Kind, Row, Expected, Count, Before);
                     Close_Stopped
                       (Kind, Rows, Observed_Genesis.Value,
                        Observed_Genesis, Witnessed_Genesis, Witnessed_Head,
                        Count, Expected, Row,
                        (Disposition => Stored_Head_Mismatch, Head => Before,
                         Accepted_Count => Count));
                     return (Disposition => Stored_Head_Mismatch, Head => Before,
                             Accepted_Count => Count);
                  end if;
                  pragma Assert (Current = Row.Stored_Head.Value);
                  pragma Assert
                    (Current = Link
                       (Kind, Before, Row.Actual_Payload_Root.Value));
                  Link_Bytes
                    (Kind, Before, Expected.Head, Row.Actual_Payload_Root.Value);
                  Prove_Ready (Kind, Row, Expected, Count);
                  Advance
                    (Kind, Rows, Observed_Genesis.Value, Count, Row, Expected);
                  Count := Count + 1;
            end case;
         end;
      end loop;
      Close_Finished
        (Kind, Rows, Observed_Genesis, Witnessed_Genesis, Witnessed_Head,
         Expected, Current, Count);
      if Current /= Witnessed_Head.Value then
         return (Disposition => Tail_Mismatch, Head => Current,
                 Accepted_Count => Count);
      end if;
      return (Disposition => Ready, Head => Current, Accepted_Count => Count);
   end Replay;
end Worldline.Chain_Authority;
