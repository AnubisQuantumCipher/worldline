package body Worldline.Chain_Authority with SPARK_Mode is
   function Prefix_Reference
     (Kind : Chain_Kind; Rows : Retained_Rows; Genesis : Hash;
      Count : Q.Byte_Count) return Result
   is
   begin
      if Count = 0 then
         return (Disposition => Ready, Head => Genesis, Accepted_Count => 0);
      end if;
      declare
         Before : constant Result :=
           Prefix_Reference (Kind, Rows, Genesis, Count - 1);
         Row : constant Chain_Row := Rows (Rows'First + (Count - 1));
      begin
         if Before.Disposition /= Ready then
            return Before;
         elsif not Present (Row) then
            return (Disposition => Row_Absent, Head => Before.Head,
                    Accepted_Count => Before.Accepted_Count);
         elsif not R.Same (Row.Actual_Payload_Root, Row.Stored_Payload_Root) then
            return (Disposition => Payload_Mismatch, Head => Before.Head,
                    Accepted_Count => Before.Accepted_Count);
         elsif Row.Previous.Value /= Before.Head then
            return (Disposition => Predecessor_Mismatch, Head => Before.Head,
                    Accepted_Count => Before.Accepted_Count);
         elsif Row.Stored_Head.Value /=
            Link (Kind, Before.Head, Row.Actual_Payload_Root.Value)
         then
            return (Disposition => Stored_Head_Mismatch, Head => Before.Head,
                    Accepted_Count => Before.Accepted_Count);
         else
            return (Disposition => Ready, Head => Row.Stored_Head.Value,
                    Accepted_Count => Count);
         end if;
      end;
   end Prefix_Reference;

   function Replay_Reference
     (Kind : Chain_Kind; Rows : Retained_Rows;
      Observed_Genesis, Witnessed_Genesis, Witnessed_Head : Optional_Digest)
      return Result
   is
   begin
      if not Observed_Genesis.Present or else not Witnessed_Genesis.Present
        or else not Witnessed_Head.Present
      then
         return (Disposition => Anchor_Absent, Head => [others => 0],
                 Accepted_Count => 0);
      elsif not R.Same (Observed_Genesis, Witnessed_Genesis) then
         return (Disposition => Genesis_Mismatch, Head => Observed_Genesis.Value,
                 Accepted_Count => 0);
      end if;
      declare
         Prefix : constant Result := Prefix_Reference
           (Kind, Rows, Observed_Genesis.Value, Rows'Length);
      begin
         if Prefix.Disposition /= Ready then
            return Prefix;
         elsif Prefix.Head /= Witnessed_Head.Value then
            return (Disposition => Tail_Mismatch, Head => Prefix.Head,
                    Accepted_Count => Prefix.Accepted_Count);
         else
            return Prefix;
         end if;
      end;
   end Replay_Reference;

   --  Packet 14 (additive induction lemma; ruling 7b): Prefix_Step returns a
   --  non-Ready Before unchanged, so once a prefix result is not Ready every
   --  longer prefix of the unchanged reference equals it. Total, conditional
   --  Post; the reference equations and variants are unchanged.
   procedure Prefix_Settled
     (Kind : Chain_Kind; Rows : Retained_Rows; Genesis : Hash;
      From, To : Q.Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Subprogram_Variant => (Decreases => To),
     Post => (if From <= To and then To <= Rows'Length
                and then Prefix_Reference (Kind, Rows, Genesis, From).Disposition
                  /= Ready
              then Prefix_Reference (Kind, Rows, Genesis, To) =
                Prefix_Reference (Kind, Rows, Genesis, From))
   is
   begin
      if From < To and then To <= Rows'Length then
         Prefix_Settled (Kind, Rows, Genesis, From, To - 1);
      end if;
   end Prefix_Settled;

   function Replay
     (Kind : Chain_Kind; Rows : Retained_Rows;
      Observed_Genesis, Witnessed_Genesis, Witnessed_Head : Optional_Digest)
      return Result
   is
      Receipt : Receipts.Chain := Receipts.New_Chain (Observed_Genesis.Value);
      Causal : Causal_Graph.Chain := Causal_Graph.New_Chain (Observed_Genesis.Value);
      Current : Hash := Observed_Genesis.Value;
      Count : Q.Byte_Count := 0;
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
      for I in Rows'Range loop
         pragma Loop_Invariant (Count = I - Rows'First);
         pragma Loop_Invariant (Count <= Rows'Length);
         pragma Loop_Invariant
           (Prefix_Reference (Kind, Rows, Observed_Genesis.Value, Count) =
             (Disposition => Ready, Head => Current, Accepted_Count => Count));
         pragma Loop_Invariant
           (if Kind = Receipt_Chain then
              Receipts.Accepted (Receipt) and then Receipts.Head (Receipt) = Current
            else Causal_Graph.Accepted (Causal) and then Causal_Graph.Head (Causal) = Current);
         declare
            Row : constant Chain_Row := Rows (I);
            Before : constant Hash := Current;
         begin
            if not Present (Row) then
               pragma Assert                                                --  packet 14
                 (Prefix_Reference (Kind, Rows, Observed_Genesis.Value, Count + 1) =
                    (Disposition => Row_Absent, Head => Current, Accepted_Count => Count));
               Prefix_Settled                                               --  packet 14
                 (Kind, Rows, Observed_Genesis.Value, Count + 1, Rows'Length);
               return (Disposition => Row_Absent, Head => Current,
                       Accepted_Count => Count);
            elsif not R.Same (Row.Actual_Payload_Root, Row.Stored_Payload_Root) then
               pragma Assert                                                --  packet 14
                 (Prefix_Reference (Kind, Rows, Observed_Genesis.Value, Count + 1) =
                    (Disposition => Payload_Mismatch, Head => Current, Accepted_Count => Count));
               Prefix_Settled                                               --  packet 14
                 (Kind, Rows, Observed_Genesis.Value, Count + 1, Rows'Length);
               return (Disposition => Payload_Mismatch, Head => Current,
                       Accepted_Count => Count);
            end if;
            case Kind is
               when Receipt_Chain =>
                  Receipts.Append (Receipt, Row.Previous.Value,
                                   Row.Actual_Payload_Root.Value);
                  if not Receipts.Accepted (Receipt) then
                     pragma Assert                                                --  packet 14
                       (Prefix_Reference (Kind, Rows, Observed_Genesis.Value, Count + 1) =
                          (Disposition => Predecessor_Mismatch, Head => Current, Accepted_Count => Count));
                     Prefix_Settled                                               --  packet 14
                       (Kind, Rows, Observed_Genesis.Value, Count + 1, Rows'Length);
                     return (Disposition => Predecessor_Mismatch, Head => Current,
                             Accepted_Count => Count);
                  end if;
                  Current := Receipts.Head (Receipt);
               when Causal_Chain =>
                  Causal_Graph.Append (Causal, Row.Previous.Value,
                                       Row.Actual_Payload_Root.Value);
                  if not Causal_Graph.Accepted (Causal) then
                     pragma Assert                                                --  packet 14
                       (Prefix_Reference (Kind, Rows, Observed_Genesis.Value, Count + 1) =
                          (Disposition => Predecessor_Mismatch, Head => Current, Accepted_Count => Count));
                     Prefix_Settled                                               --  packet 14
                       (Kind, Rows, Observed_Genesis.Value, Count + 1, Rows'Length);
                     return (Disposition => Predecessor_Mismatch, Head => Current,
                             Accepted_Count => Count);
                  end if;
                  Current := Causal_Graph.Head (Causal);
            end case;
            pragma Assert                                                 --  packet 14
              (Row.Previous.Value = Before
               and then Current = Link (Kind, Before, Row.Actual_Payload_Root.Value));
            if Current /= Row.Stored_Head.Value then
               pragma Assert                                                --  packet 14
                 (Prefix_Reference (Kind, Rows, Observed_Genesis.Value, Count + 1) =
                    (Disposition => Stored_Head_Mismatch, Head => Before, Accepted_Count => Count));
               Prefix_Settled                                               --  packet 14
                 (Kind, Rows, Observed_Genesis.Value, Count + 1, Rows'Length);
               return (Disposition => Stored_Head_Mismatch, Head => Before,
                       Accepted_Count => Count);
            end if;
            pragma Assert                                                 --  packet 14
              (Prefix_Reference (Kind, Rows, Observed_Genesis.Value, Count + 1) =
                 (Disposition => Ready, Head => Current, Accepted_Count => Count + 1));
            Count := Count + 1;
         end;
      end loop;
      if Current /= Witnessed_Head.Value then
         return (Disposition => Tail_Mismatch, Head => Current,
                 Accepted_Count => Count);
      end if;
      return (Disposition => Ready, Head => Current, Accepted_Count => Count);
   end Replay;
end Worldline.Chain_Authority;
