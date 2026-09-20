with Ada.Text_IO;
with Attest;
with Attest.SHA256;
with Interfaces;
with Worldline;
with Worldline.Ancestry;
with Worldline.C_API;
with Worldline.Causal_Graph;
with Worldline.Collapse;
with Worldline.Receipts;
with Worldline.Transitions;
with Worldline.World;

procedure Worldline_Core_Tests is
   use type Worldline.Hash;
   use type Worldline.Collapse.Decision;
   use type Worldline.Transitions.Transaction_State;
   use type Interfaces.Unsigned_8;

   procedure Check (Condition : Boolean; Message : String) is
   begin
      if not Condition then
         raise Program_Error with Message;
      end if;
   end Check;

   function Filled (Value : Attest.Byte) return Worldline.Hash is
     [others => Value];

   H0 : constant Worldline.Hash := Filled (0);
   H1 : constant Worldline.Hash := Filled (1);
   H2 : constant Worldline.Hash := Filled (2);
   H3 : constant Worldline.Hash := Filled (3);
   H4 : constant Worldline.Hash := Filled (4);
   H5 : constant Worldline.Hash := Filled (5);
   H6 : constant Worldline.Hash := Filled (6);
   H7 : constant Worldline.Hash := Filled (7);

   Empty : constant Attest.Byte_Array (1 .. 0) := [others => 0];
   Empty_SHA256 : constant Worldline.Hash :=
     [16#e3#, 16#b0#, 16#c4#, 16#42#, 16#98#, 16#fc#, 16#1c#, 16#14#,
      16#9a#, 16#fb#, 16#f4#, 16#c8#, 16#99#, 16#6f#, 16#b9#, 16#24#,
      16#27#, 16#ae#, 16#41#, 16#e4#, 16#64#, 16#9b#, 16#93#, 16#4c#,
      16#a4#, 16#95#, 16#99#, 16#1b#, 16#78#, 16#52#, 16#b8#, 16#55#];

   Request : Worldline.Collapse.Collapse_Request :=
     (Candidate_State => Worldline.Transitions.Valid,
      Has_Conflicts => False,
      Has_Foreign_Managed_Writes => False,
      Expected_Parent => H1,
      Candidate_Parent => H1,
      Expected_Owner => H2,
      Candidate_Owner => H2,
      Expected_Base => H3,
      Candidate_Base => H3,
      Expected_Delta => H4,
      Candidate_Delta => H4,
      Expected_Root_Set => H5,
      Candidate_Root_Set => H5,
      Expected_Staged_Root => H6,
      Actual_Staged_Root => H6);

   Parent : Worldline.Ancestry.Parent_Guard :=
     Worldline.Ancestry.New_Parent_Guard (H1);
   Owner : Worldline.Ancestry.Owner_Guard :=
     Worldline.Ancestry.New_Owner_Guard (H2);
   Causal : Worldline.Causal_Graph.Chain :=
     Worldline.Causal_Graph.New_Chain (H0);
   Receipt : Worldline.Receipts.Chain :=
     Worldline.Receipts.New_Chain (H0);
   Transaction : Worldline.Transitions.Transaction_State :=
     Worldline.Transitions.Prepared;
   Linked : Worldline.Hash;
   Identity_One : Worldline.Hash;
   Identity_Two : Worldline.Hash;
begin
   Check
     (Attest.SHA256.Hash (Empty) = Empty_SHA256,
      "published empty SHA-256 vector failed");

   Identity_One := Worldline.World.Identity (H0, H1, H2, H3, H4, H5);
   Identity_Two := Worldline.World.Identity (H0, H1, H2, H3, H4, H5);
   Check (Identity_One = Identity_Two, "world identity is not deterministic");
   Check
     (Identity_One /= Worldline.World.Identity (H0, H1, H2, H3, H4, H6),
      "evidence root omitted from world identity");

   Worldline.Ancestry.Claim (Parent, H1, H1);
   Check (Worldline.Ancestry.Accepted (Parent), "valid parent rejected");
   Worldline.Ancestry.Claim (Parent, H1, H2);
   Check (not Worldline.Ancestry.Accepted (Parent), "bad claim accepted");
   Worldline.Ancestry.Claim (Parent, H1, H1);
   Check (not Worldline.Ancestry.Accepted (Parent), "parent denial unstuck");

   Worldline.Ancestry.Check_Owner (Owner, H3);
   Check
     (not Worldline.Ancestry.Owner_Accepted (Owner),
      "owner mismatch accepted");
   Worldline.Ancestry.Check_Owner (Owner, H2);
   Check
     (not Worldline.Ancestry.Owner_Accepted (Owner),
      "owner denial unstuck");

   Check
     (Worldline.Transitions.Allowed
        (Worldline.Transitions.Mutable, Worldline.Transitions.Finalizing),
      "mutable to finalizing denied");
   Check
     (not Worldline.Transitions.Allowed
        (Worldline.Transitions.Dead, Worldline.Transitions.Valid),
      "dead world became valid");
   Check
     (not Worldline.Transitions.Allowed
        (Worldline.Transitions.Degraded, Worldline.Transitions.Collapsed),
      "degraded world became collapsible");

   Worldline.Transitions.Advance
     (Transaction, Worldline.Transitions.Denied);
   Worldline.Transitions.Advance
     (Transaction, Worldline.Transitions.Committed);
   Check
     (Transaction = Worldline.Transitions.Denied,
      "denied transaction committed");

   --  The C export must agree with the proved unit for every pair, and
   --  refuse every out-of-range code, so the Python runtime that consults
   --  wl_transaction_transition_allowed sees exactly the proved lifecycle.
   for From in Worldline.Transitions.Transaction_State loop
      for To in Worldline.Transitions.Transaction_State loop
         Check
           (Worldline.C_API.Transaction_Transition_Allowed
              (Interfaces.Unsigned_8
                 (Worldline.Transitions.Transaction_State'Pos (From)),
               Interfaces.Unsigned_8
                 (Worldline.Transitions.Transaction_State'Pos (To))) =
            (if Worldline.Transitions.Transaction_Allowed (From, To)
             then 1 else 0),
            "C transaction lifecycle export disagrees with proved unit");
      end loop;
   end loop;
   Check
     (Worldline.C_API.Transaction_Transition_Allowed (5, 0) = 0
      and then Worldline.C_API.Transaction_Transition_Allowed (0, 255) = 0,
      "out-of-range transaction code accepted");
   Check
     (Worldline.C_API.Transaction_Transition_Allowed (2, 3) = 0,
      "C export let a denied transaction commit");

   Check
     (Worldline.Collapse.Decide (Request) = Worldline.Collapse.Authorized,
      "valid collapse denied");
   Request.Candidate_State := Worldline.Transitions.Dead;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Invalid_Candidate,
      "dead candidate authorized");
   Request.Candidate_State := Worldline.Transitions.Valid;
   Request.Candidate_Parent := H7;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Parent_Mismatch,
      "parent mismatch missed");
   Request.Candidate_Parent := H1;
   Request.Candidate_Owner := H7;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Owner_Mismatch,
      "owner mismatch missed");
   Request.Candidate_Owner := H2;
   Request.Candidate_Base := H7;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Base_Mismatch,
      "base mismatch missed");
   Request.Candidate_Base := H3;
   Request.Candidate_Delta := H7;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Delta_Mismatch,
      "delta mismatch missed");
   Request.Candidate_Delta := H4;
   Request.Candidate_Root_Set := H7;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Root_Set_Mismatch,
      "root-set mismatch missed");
   Request.Candidate_Root_Set := H5;
   Request.Actual_Staged_Root := H7;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Staged_Root_Mismatch,
      "staged-root mismatch missed");
   Request.Actual_Staged_Root := H6;
   Request.Has_Conflicts := True;
   Check
     (Worldline.Collapse.Decide (Request) = Worldline.Collapse.Conflict,
      "conflict missed");
   Request.Has_Conflicts := False;
   Request.Has_Foreign_Managed_Writes := True;
   Check
     (Worldline.Collapse.Decide (Request) =
        Worldline.Collapse.Foreign_Managed_Write,
      "foreign write missed");

   Linked := Worldline.Causal_Graph.Link (H0, H1);
   Worldline.Causal_Graph.Append (Causal, H0, H1);
   Check
     (Worldline.Causal_Graph.Accepted (Causal)
      and then Worldline.Causal_Graph.Head (Causal) = Linked,
      "valid causal link rejected");
   Worldline.Causal_Graph.Append (Causal, H7, H2);
   Check
     (not Worldline.Causal_Graph.Accepted (Causal),
      "causal predecessor mismatch accepted");
   Worldline.Causal_Graph.Append (Causal, Linked, H2);
   Check
     (not Worldline.Causal_Graph.Accepted (Causal),
      "causal rejection unstuck");

   Linked := Worldline.Receipts.Link (H0, H1);
   Worldline.Receipts.Append (Receipt, H0, H1);
   Check
     (Worldline.Receipts.Accepted (Receipt)
      and then Worldline.Receipts.Head (Receipt) = Linked,
      "valid receipt link rejected");
   Worldline.Receipts.Append (Receipt, H7, H2);
   Check
     (not Worldline.Receipts.Accepted (Receipt),
      "receipt predecessor mismatch accepted");
   Worldline.Receipts.Append (Receipt, Linked, H2);
   Check
     (not Worldline.Receipts.Accepted (Receipt),
      "receipt rejection unstuck");

   Ada.Text_IO.Put_Line ("worldline_core_tests: PASS");
end Worldline_Core_Tests;
