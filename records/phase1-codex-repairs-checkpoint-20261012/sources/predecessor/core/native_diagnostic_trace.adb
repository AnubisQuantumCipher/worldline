with Ada.Unchecked_Deallocation;
package body Native_Diagnostic_Trace
  with SPARK_Mode, Refined_State => (Pending => Head)
is
   Head : Line_Access := null;
   procedure Free is new Ada.Unchecked_Deallocation (Line, Line_Access);

   function Pending_Contents return Line_Sequences.Sequence is
     (Stack_Contents (Head));

   function Empty return Boolean is (Head = null);

   procedure Push (Text : String) is
   begin
      --  Ownership moves into the new node; only the new complete Text is
      --  copied into owned storage. Every earlier node remains untouched.
      Head := new Line'(Length => Text'Length, Text => Text, Next => Head);
   end Push;

   procedure Take_All (Items : aliased out Line_Access) is
      Original : constant Line_Sequences.Sequence := Pending_Contents
        with Ghost;
   begin
      Items := null;
      --  Reverse the owned stack without copying any runtime message or
      --  allocating another runtime buffer. The length variant proves
      --  progress only; the invariant below independently conserves the
      --  complete chronological sequence across both disjoint owning chains.
      while Head /= null loop
         pragma Loop_Invariant
           (Split_Contents
              (Original, Stack_Contents (Head), Contents (Items)));
         pragma Loop_Variant
           (Decreases => Line_Sequences.Length (Stack_Contents (Head)));
         pragma Assert
           (Stack_Contents (Head)
              = Line_Sequences.Add (Stack_Contents (Head.Next), Head.Text));
         declare
            --  Value snapshots precede moves: no observer survives a move or
            --  mutation. These are specification values, not pointer aliases.
            Remaining : constant Line_Sequences.Sequence :=
              Stack_Contents (Head.Next) with Ghost;
            Returned : constant Line_Sequences.Sequence := Contents (Items)
              with Ghost;
            Text : constant String := Head.Text with Ghost;
            Item : Line_Access := Head;
         begin
            pragma Assert
              (Split_Contents
                 (Original, Line_Sequences.Add (Remaining, Text), Returned));
            Head := Item.Next;
            Item.Next := Items;
            Items := Item;
            pragma Assert (Stack_Contents (Head) = Remaining);
            pragma Assert
              (Contents (Items) = Line_Sequences.Add (Returned, 1, Text));
            --  Step the conservation relation across the one moved node: the
            --  moved Text is the next original line after the remaining prefix,
            --  and every already returned line shifts by one position.
            pragma Assert
              (Line_Sequences.Length (Original)
                 = Line_Sequences.Length (Remaining)
                   + Line_Sequences.Length (Returned) + 1);
            pragma Assert (Remaining <= Original);
            pragma Assert
              (Line_Sequences.Length (Line_Sequences.Add (Remaining, Text))
                 = Line_Sequences.Length (Remaining) + 1);
            pragma Assert
              (Line_Sequences.Get
                 (Line_Sequences.Add (Remaining, Text),
                  Line_Sequences.Length (Remaining) + 1) = Text);
            pragma Assert (Line_Sequences.Add (Remaining, Text) <= Original);
            pragma Assert
              (Line_Sequences.Get
                 (Original, Line_Sequences.Length (Remaining) + 1) = Text);
            pragma Assert
              (for all J in Returned =>
                 Line_Sequences.Get (Returned, J)
                   = Line_Sequences.Get
                       (Original, Line_Sequences.Length (Remaining) + 1 + J));
            declare
               --  Bound once: checked builds evaluate these quantifiers.
               Now : constant Line_Sequences.Sequence := Contents (Items)
                 with Ghost;
            begin
               pragma Assert (Line_Sequences.Get (Now, 1) = Text);
               pragma Assert
                 (for all J in Now =>
                    (if J >= 2 then
                       Line_Sequences.Get (Now, J)
                         = Line_Sequences.Get (Returned, J - 1)));
               pragma Assert
                 (for all J in Now =>
                    Line_Sequences.Get (Now, J)
                      = Line_Sequences.Get
                          (Original, Line_Sequences.Length (Remaining) + J));
            end;
            pragma Assert
              (Split_Contents
                 (Original, Stack_Contents (Head), Contents (Items)));
         end;
      end loop;
      pragma Assert (Line_Sequences.Length (Stack_Contents (Head)) = 0);
      declare
         Final : constant Line_Sequences.Sequence := Contents (Items)
           with Ghost;
      begin
         pragma Assert
           (Line_Sequences.Length (Final) = Line_Sequences.Length (Original));
         pragma Assert
           (for all J in Final =>
              Line_Sequences.Get (Final, J) = Line_Sequences.Get (Original, J));
      end;
      pragma Assert (Contents (Items) = Original);
   end Take_All;

   procedure Release (Item : in out Line_Access) is
   begin
      --  Pool-specific owner and a null tail: supported deallocation cannot
      --  silently abandon a nested owning allocation.
      Free (Item);
   end Release;
end Native_Diagnostic_Trace;
