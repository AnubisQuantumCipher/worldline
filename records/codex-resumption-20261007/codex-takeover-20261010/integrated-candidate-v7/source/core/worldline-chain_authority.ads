with Resource_Quantities;
with Worldline.Recovery_Authorization_V3;
with Worldline.Receipts;
with Worldline.Causal_Graph;

-- Full retained-chain value rule. Protected producers establish the anchors,
-- canonical payload bytes and transaction/effect/requester facts. This package
-- does not turn an arbitrary pair of matching supplied values into authenticity.
package Worldline.Chain_Authority with SPARK_Mode is
   package Q renames Resource_Quantities;
   package R renames Worldline.Recovery_Authorization_V3;
   use type Q.Byte_Count;
   use type Hash;
   type Chain_Kind is (Receipt_Chain, Causal_Chain);
   subtype Optional_Digest is R.Optional_Digest;
   type Chain_Row is record
      Previous, Actual_Payload_Root, Stored_Payload_Root, Stored_Head : Optional_Digest;
   end record;
   type Retained_Rows is array (Q.Byte_Index range <>) of Chain_Row;
   type Reason is
     (Anchor_Absent, Genesis_Mismatch, Row_Absent, Payload_Mismatch,
      Predecessor_Mismatch, Stored_Head_Mismatch, Tail_Mismatch, Ready);
   type Result is record
      Disposition : Reason;
      Head : Hash;
      Accepted_Count : Q.Byte_Count;
   end record;

   function Link (Kind : Chain_Kind; Previous, Payload_Root : Hash) return Hash is
     (case Kind is
         when Receipt_Chain => Receipts.Link (Previous, Payload_Root),
         when Causal_Chain => Causal_Graph.Link (Previous, Payload_Root))
     with Global => null;

   function Present (Row : Chain_Row) return Boolean is
     (Row.Previous.Present and then Row.Actual_Payload_Root.Present
      and then Row.Stored_Payload_Root.Present and then Row.Stored_Head.Present)
     with Global => null;

   -- Transparent ghost equations expose the original reference decisions.
   -- Their bodies and all callers remain required proof obligations.
   function Prefix_Step
     (Kind : Chain_Kind; Row : Chain_Row; Before : Result;
      Count : Q.Byte_Count) return Result is
     (if Before.Disposition /= Ready then Before
      elsif not Present (Row) then
         (Disposition => Row_Absent, Head => Before.Head,
          Accepted_Count => Before.Accepted_Count)
      elsif not R.Same (Row.Actual_Payload_Root, Row.Stored_Payload_Root) then
         (Disposition => Payload_Mismatch, Head => Before.Head,
          Accepted_Count => Before.Accepted_Count)
      elsif Row.Previous.Value /= Before.Head then
         (Disposition => Predecessor_Mismatch, Head => Before.Head,
          Accepted_Count => Before.Accepted_Count)
      elsif Row.Stored_Head.Value /=
         Link (Kind, Before.Head, Row.Actual_Payload_Root.Value) then
         (Disposition => Stored_Head_Mismatch, Head => Before.Head,
          Accepted_Count => Before.Accepted_Count)
      else (Disposition => Ready, Head => Row.Stored_Head.Value,
            Accepted_Count => Count))
     with Ghost, Global => null;

   function Finish_Reference (Prefix : Result; Witnessed_Head : Hash)
     return Result is
     (if Prefix.Disposition /= Ready then Prefix
      elsif Prefix.Head /= Witnessed_Head then
         (Disposition => Tail_Mismatch, Head => Prefix.Head,
          Accepted_Count => Prefix.Accepted_Count)
      else Prefix)
     with Ghost, Global => null;

   -- This independent reference uses Link and complete row predicates. The
   -- implementation uses the original stateful Append routines instead.
   function Prefix_Reference
     (Kind : Chain_Kind; Rows : Retained_Rows; Genesis : Hash;
      Count : Q.Byte_Count) return Result
   is
     (if Count = 0 then (Disposition => Ready, Head => Genesis, Accepted_Count => 0)
      else Prefix_Step
        (Kind, Rows (Rows'First + (Count - 1)),
         Prefix_Reference (Kind, Rows, Genesis, Count - 1), Count))
   with Ghost, Global => null,
     Pre => Count <= Rows'Length,
     Subprogram_Variant => (Decreases => Count),
     Post => Prefix_Reference'Result.Accepted_Count <= Count and then
       Prefix_Reference'Result =
         (if Count = 0 then
            (Disposition => Ready, Head => Genesis, Accepted_Count => 0)
          else Prefix_Step
            (Kind, Rows (Rows'First + (Count - 1)),
             Prefix_Reference (Kind, Rows, Genesis, Count - 1), Count));

   function Replay_Reference
     (Kind : Chain_Kind; Rows : Retained_Rows;
      Observed_Genesis, Witnessed_Genesis, Witnessed_Head : Optional_Digest)
      return Result
   is
     (if not Observed_Genesis.Present or else not Witnessed_Genesis.Present
         or else not Witnessed_Head.Present then
         (Disposition => Anchor_Absent, Head => [others => 0], Accepted_Count => 0)
      elsif not R.Same (Observed_Genesis, Witnessed_Genesis) then
         (Disposition => Genesis_Mismatch, Head => Observed_Genesis.Value,
          Accepted_Count => 0)
      else Finish_Reference
         (Prefix_Reference (Kind, Rows, Observed_Genesis.Value, Rows'Length),
          Witnessed_Head.Value))
   with Ghost, Global => null,
     Post => Replay_Reference'Result.Accepted_Count <= Rows'Length and then
       Replay_Reference'Result =
         (if not Observed_Genesis.Present or else not Witnessed_Genesis.Present
             or else not Witnessed_Head.Present then
            (Disposition => Anchor_Absent, Head => [others => 0],
             Accepted_Count => 0)
          elsif not R.Same (Observed_Genesis, Witnessed_Genesis) then
            (Disposition => Genesis_Mismatch, Head => Observed_Genesis.Value,
             Accepted_Count => 0)
          else Finish_Reference
            (Prefix_Reference
               (Kind, Rows, Observed_Genesis.Value, Rows'Length),
             Witnessed_Head.Value));

   function Replay
     (Kind : Chain_Kind; Rows : Retained_Rows;
      Observed_Genesis, Witnessed_Genesis, Witnessed_Head : Optional_Digest)
      return Result
   with Global => null,
     Post => Replay'Result = Replay_Reference
       (Kind, Rows, Observed_Genesis, Witnessed_Genesis, Witnessed_Head)
       and then Replay'Result.Accepted_Count <= Rows'Length;

   -- An append is an entire replay with the new row included. The caller must
   -- retain every old row, and must durably advance its independently protected
   -- head only after this verdict. No selected-tail shortcut is provided.
end Worldline.Chain_Authority;
