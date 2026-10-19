with Worldline.Retained_Evidence_Replay;

-- Factual descriptor/row evolution, conditional on actual predecessor presence.
-- Initial/reconstructed frames do not invent current copy receipts. Original
-- native classifiers, source custody, physical roles and authenticated
-- protocol/root history remain separate required conjuncts.
package Worldline.Scoped_Capture_Evolution_Projection with SPARK_Mode is
   package R renames Worldline.Retained_Evidence_Replay;
   package E renames R.E;
   --  Full native roster/SCM/namespace validation of each before_inventory is
   --  a separate caller conjunct, including for remote aliases (kcmp = None).
   function Closed_Roles_Match (Data : E.Bytes; Inventory : E.Span) return Boolean
     with Global => null;
   function Subject_Transport_Matches (Data : E.Bytes; Inventory : E.Span) return Boolean
     with Global => null;
   --  Authentic initial ROOT custody is distinct from a later subject frame.
   function Initial_Root_Transport_Matches (Data : E.Bytes; Inventory : E.Span) return Boolean
     with Global => null, Subprogram_Variant =>
       (Decreases => Inventory.Length, Decreases => Natural'(0));
   --  Both operands are complete original raw archive values (never scoped).
   --  The caller proves whole S.record/raw transfer equality and the complete
   --  native Item.Material.metadata.provenance.subject_capture floor; Inventory
   --  is that capture's actual inventory. This relation decodes the declared
   --  current_inventory image once and matches it to that native operand.
   function Subject_Roles_Match (Data : E.Bytes; Transport, Inventory : E.Span) return Boolean
     with Global => null;
   --  Separate authentic evidence/native arenas; no whole-arena concatenation.
   function Subject_Roles_Match (Data, Inventory_Data : E.Bytes;
     Transport, Inventory : E.Span) return Boolean with Global => null;
   function Evolution_Matches (Data : E.Bytes; Inventory : E.Span) return Boolean
     with Global => null;
end Worldline.Scoped_Capture_Evolution_Projection;
