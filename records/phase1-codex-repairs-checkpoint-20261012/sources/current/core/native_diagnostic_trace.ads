with SPARK.Big_Integers;
with SPARK.Containers.Functional.Infinite_Sequences;

--  Diagnostic text is captured before peripheral output. Neither the queue
--  nor its sink supplies an authority input or changes a primary result.
--  The native caller holds its exclusive process-wide diagnostic guard across
--  Push, Take_All and Release; this pure package does not import a lock or sink.
package Native_Diagnostic_Trace
  with SPARK_Mode, Abstract_State => Pending, Initializes => Pending
is
   type Line (Length : Natural);
   type Line_Access is access Line;
   type Line (Length : Natural) is record
      Text : String (1 .. Length);
      Next : Line_Access := null;
   end record;

   --  Unbounded specification indices, not a new admitted line/count ceiling.
   --  String equality compares every character and the complete line length;
   --  empty lines, duplicate lines and all Character values remain distinct
   --  sequence positions. No checksum stands in for the captured contents.
   package Line_Sequences is new
     SPARK.Containers.Functional.Infinite_Sequences (String);
   use type SPARK.Big_Integers.Big_Integer;
   use type Line_Sequences.Sequence;

   --  Physical Next order, which is the caller's FIFO order after Take_All.
   --  Observations neither take ownership nor retain a borrowed pointer.
   --  SPARK functions must terminate implicitly; structural variants below
   --  preserve the recursive model obligations without illegal function aspects.
   function Contents (Items : access constant Line)
     return Line_Sequences.Sequence
     with Ghost, Global => null,
          Subprogram_Variant => (Structural => Items);

   --  Chronological pending order, independent of the internal stack order.
   function Pending_Contents return Line_Sequences.Sequence
     with Ghost, Global => (Input => Pending);

   function Appended
     (Before, After : Line_Sequences.Sequence; Text : String) return Boolean
   is
     (Line_Sequences.Length (After) = Line_Sequences.Length (Before) + 1
      and then Before <= After
      and then Line_Sequences.Get (After, Line_Sequences.Last (After)) = Text)
     with Ghost, Global => null;

   function Empty return Boolean
     with Global => (Input => Pending),
          Post => Empty'Result = (Line_Sequences.Length (Pending_Contents) = 0);

   --  One owned allocation for the complete original text; no truncation,
   --  fixed message/count ceiling, foreign call, or borrowed text lifetime.
   --  Linking is constant-time: no traversal/copy of earlier runtime lines.
   --  Checked ghost models add traversal/allocation, not owning queue nodes.
   procedure Push (Text : String)
     with Global => (In_Out => Pending), Always_Terminates,
          Post => Appended (Pending_Contents'Old, Pending_Contents, Text)
            and then not Empty;

   --  Transfers the complete queue in chronological order. The caller owns
   --  and releases every returned line even if its physical output fails.
   --  Ownership moves only; no runtime line/text copy or new allocation.
   --  Explicitly aliased forces by-reference handoff: if checked model work
   --  raises after a move, the caller still owns the transferred Items chain
   --  and can release it. A by-copy out formal could suppress copyback on
   --  that exceptional exit and orphan the queue. Actual Items must be aliased.
   procedure Take_All (Items : aliased out Line_Access)
     with Global => (In_Out => Pending), Always_Terminates,
          Post => Contents (Items) = Pending_Contents'Old and then Empty;

   procedure Release (Item : in out Line_Access)
     with Global => null, Always_Terminates,
          Pre => Item = null or else Item.Next = null,
          Post => Item = null;

private
   --  Reverse physical Next order models the owning pending stack.
   function Stack_Contents (Items : access constant Line)
     return Line_Sequences.Sequence
     with Ghost, Global => null,
          Subprogram_Variant => (Structural => Items);

   --  Exactly one recursive tail evaluation per node, and no recursive model
   --  postcondition. Enabling ghost assertions cannot create the exponential
   --  checked recurrence of re-evaluating each tail in recursive postchecks.
   function Contents (Items : access constant Line)
     return Line_Sequences.Sequence
   is
     (if Items = null then Line_Sequences.Empty_Sequence
      else Line_Sequences.Add (Contents (Items.Next), 1, Items.Text));

   function Stack_Contents (Items : access constant Line)
     return Line_Sequences.Sequence
   is
     (if Items = null then Line_Sequences.Empty_Sequence
      else Line_Sequences.Add (Stack_Contents (Items.Next), Items.Text));

   --  Whole = Prefix followed by Suffix, including every original line/byte.
   --  Property-only relation: it does not allocate a concatenated sequence.
   function Split_Contents
     (Whole, Prefix, Suffix : Line_Sequences.Sequence) return Boolean
   is
     (Line_Sequences.Length (Whole)
        = Line_Sequences.Length (Prefix) + Line_Sequences.Length (Suffix)
      and then Prefix <= Whole
      and then
        (for all J in Suffix =>
           Line_Sequences.Get (Suffix, J)
             = Line_Sequences.Get
                 (Whole, Line_Sequences.Length (Prefix) + J)))
     with Ghost, Global => null;
end Native_Diagnostic_Trace;
