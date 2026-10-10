with Interfaces;
with Cosmogony.Genesis;
with Cosmogony.Universes;
with Cosmogony.Capabilities;
with Cosmogony.Revocable_Capabilities;
with Cosmogony.Use_Reservations;
procedure Use_Reservation_Tests is
   use Cosmogony.Genesis;
   use Cosmogony.Universes;
   use Cosmogony.Capabilities;
   use Cosmogony.Revocable_Capabilities;
   use type Interfaces.Unsigned_64;
   package L renames Cosmogony.Use_Reservations;
   use type L.Status;
   subtype Digest is Cosmogony.Genesis.Digest;
   Zero_Digest : constant Digest := Cosmogony.Genesis.Zero_Digest;
   function Tag (N : Interfaces.Unsigned_64) return Digest is
     (1 => N, others => 0);

   Policy : constant Policy_Bindings :=
     (Mission_Id => Tag (2), Authority_Id => Tag (3),
      Resource_Id => Tag (4), Network_Id => Tag (5),
      Provider_Id => Tag (6), Evaluator_Id => Tag (7),
      Root_Set_Id => Tag (8), Evidence_Id => Tag (9),
      Roster_Id => Tag (10), Worldline_Set_Id => Tag (11));
   U : Universe_Record :=
     (Universe_Id => Tag (1), Parent_Id => Zero_Digest,
      Policy_Epoch => 1, Policy => Policy,
      Prime_Worldline_Id => Tag (12), Prime_Id => Tag (13),
      Prime_Generation => 0, Receipt_Head_Id => Tag (14),
      Life => Active, Running_Worlds => 0,
      Outstanding_Reservations => 0, Unresolved_Transactions => 0,
      Evidence_Snapshot_Id => Zero_Digest,
      Snapshot_Complete => False);
   G : Universe_State :=
     (Universe_Id => U.Universe_Id, Mission_Id => Policy.Mission_Id,
      Policy_Id => Policy.Authority_Id,
      Policy_Owner_Mission => Policy.Mission_Id,
      Worldline_Instance_Id => U.Prime_Worldline_Id,
      Root_Set_Id => Policy.Root_Set_Id, Prime_Id => U.Prime_Id,
      Policy_Epoch => U.Policy_Epoch,
      Budget => (World_Limit => 2, Worlds_Reserved => 0,
                 Evaluation_Limit => 2, Evaluations_Reserved => 0),
      Roster_Count => 3,
      Roster =>
        (1 => (Tag (21), Builder, True),
         2 => (Tag (22), Reviewer, True),
         3 => (Tag (23), Observer, True),
         others => (Zero_Digest, Observer, False)));
   Root : constant Capability :=
     (Capability_Id => Tag (24), Parent_Id => Zero_Digest,
      Universe_Id => G.Universe_Id, Mission_Id => G.Mission_Id,
      Policy_Id => G.Policy_Id, Authority_Id => Policy.Authority_Id,
      Worldline_Instance_Id => G.Worldline_Instance_Id,
      Root_Set_Id => G.Root_Set_Id, Prime_Id => G.Prime_Id,
      Subject_Id => Tag (21), Issuer_Id => Policy.Authority_Id,
      Policy_Epoch => G.Policy_Epoch, Issued_At => 10,
      Expires_At => 100, Terminal => False,
      Granted => (Observe | Evaluate_World => True, others => False),
      Applies_To => Entire_Universe, Ceiling => (1, 2));
   Child_Proposal : constant Grant_Proposal :=
     (Capability_Id => Tag (25), Subject_Id => Tag (22),
      Granted => (Observe | Evaluate_World => True, others => False),
      Applies_To => (World_Scope, Tag (26)),
      Ceiling => (0, 1), Expires_At => 80);
   Grandchild_Proposal : constant Grant_Proposal :=
     (Capability_Id => Tag (27), Subject_Id => Tag (23),
      Granted => (Observe => True, others => False),
      Applies_To => (World_Scope, Tag (26)),
      Ceiling => (0, 0), Expires_At => 60);
   Links : Lineage :=
     (others => (Grant => Null_Capability, Revoked => False));
   Child, Grandchild : Grant_Decision;
   Reused_Proposal : Grant_Proposal;
   Q : Scoped_Request :=
     (Ask => (Request_Id => Tag (28), Universe_Id => G.Universe_Id,
              Mission_Id => G.Mission_Id, Policy_Id => G.Policy_Id,
              Worldline_Instance_Id => G.Worldline_Instance_Id,
              Root_Set_Id => G.Root_Set_Id, Prime_Id => G.Prime_Id,
              Policy_Epoch => G.Policy_Epoch,
              Actor_Id => Tag (23), Action => Observe),
      Target_World_Id => Tag (26));

   B : L.Binding;
   Empty : L.Rows (1 .. 0);
   Held : L.Rows (1 .. 1);
   Pair : L.Rows (1 .. 2);
   Grants : L.Grant_Rows (1 .. 4);
   Sibling, Third : Capability;
   Other : L.Binding;
   Other_Links : Lineage;
   Other_Q : Scoped_Request;
   procedure Expect (Actual, Expected : L.Status) is
   begin
      pragma Assert (Actual = Expected);
   end Expect;
begin
   -- Original fixture root/child, created through the actual native derivation.
   Links (1).Grant := Root;
   Child := Derive (U, G, G.Mission_Id, Links, 1, Child_Proposal, 20);
   pragma Assert (Child.Granted);
   Links (2).Grant := Child.Child;
   Q.Ask.Actor_Id := Child.Child.Subject_Id;Q.Ask.Action := Evaluate_World;
   B := (Capability_Id => Child.Child.Capability_Id,Operation_Id => Q.Ask.Request_Id,
      Transaction_Id => Tag (29),Requester_Id => Q.Ask.Actor_Id,Universe_Head => Tag (30),
      Request_Identity => Tag (31),Grant_Use_Identity => Tag (32),Recovery_Binding_Identity => Tag (33),
      Policy_Epoch => Q.Ask.Policy_Epoch,Action => Q.Ask.Action);
   Sibling := Child.Child;Sibling.Capability_Id := Tag (34);
   Third:=Child.Child;Third.Capability_Id:=Tag (38);
   Grants := (Root,Child.Child,Sibling,Third);
   Expect (L.Check (Empty,Grants,U,G,Links,2,Q,(0,0),30,B,L.Reserve_Use),L.Reserved_New);
   Held (1) := (Kind => L.Bound_Reservation,State => L.Reserved,Bound => B,Links => Links,Link_Count => 2);
   Expect (L.Check (Held,Grants,U,G,Links,2,Q,(0,0),30,B,L.Reserve_Use),L.Reserved_Replay);
   Other:=B;Other.Operation_Id:=Tag (35);Other.Transaction_Id:=Tag (36);
   Other_Q:=Q;Other_Q.Ask.Request_Id:=Other.Operation_Id;
   Expect (L.Check (Held,Grants,U,G,Links,2,Other_Q,(0,0),30,Other,L.Reserve_Use),L.Refused);
   -- Revocation/fresh denial cannot erase the authenticated same-operation
   -- reservation after effect. Changed tuple can neither consume nor replay.
   Links (1).Revoked:=True;
   Expect (L.Check (Held,Grants,U,G,Links,2,Q,(0,0),30,B,L.Reserve_Use),L.Refused);
   Expect (L.Check (Held,Grants,U,G,Links,2,Q,(0,0),30,B,L.Consume_Use),L.Consumed_New);
   Other:=B;Other.Transaction_Id:=Tag (36);
   Expect (L.Check (Held,Grants,U,G,Links,2,Q,(0,0),30,Other,L.Consume_Use),L.Refused);
   Held (1).State:=L.Consumed;
   Expect (L.Check (Held,Grants,U,G,Links,2,Q,(0,0),30,B,L.Consume_Use),L.Consumed_Replay);
   Expect (L.Check (Held,Grants,U,G,Links,2,Q,(0,0),30,B,L.Release_Use),L.Refused);
   Held (1).State:=L.Reserved;
   Expect (L.Check (Held,Grants,U,G,Links,2,Q,(0,0),30,B,L.Release_Use),L.Released_New);
   Held (1).State:=L.Released;
   Expect (L.Check (Held,Grants,U,G,Links,2,Q,(0,0),30,B,L.Release_Use),L.Released_Replay);
   Expect (L.Check (Held,Grants,U,G,Links,2,Q,(0,0),30,B,L.Consume_Use),L.Refused);
   Expect (L.Check (Held,Grants,U,G,Links,2,Q,(0,0),30,B,L.Reserve_Use),L.Refused);
   -- Complete aggregate ancestor usage: two distinct held descendants fill the
   -- original root ceiling. A third sibling cannot borrow their outstanding use.
   Links (1).Revoked:=False;Other_Links:=Links;Other_Links (2).Grant:=Sibling;
   Pair (1):=(L.Bound_Reservation,L.Reserved,B,Links,2);
   Other:=B;Other.Capability_Id:=Sibling.Capability_Id;Other.Operation_Id:=Tag (35);
   Pair (2):=(L.Bound_Reservation,L.Reserved,Other,Other_Links,2);
   Other.Operation_Id:=Tag (37);Other.Capability_Id:=Third.Capability_Id;
   Other_Links (2).Grant:=Third;Other_Q:=Q;Other_Q.Ask.Request_Id:=Other.Operation_Id;
   Expect (L.Check (Pair,Grants,U,G,Other_Links,2,Other_Q,(0,0),30,Other,L.Reserve_Use),L.Refused);
   pragma Assert (not L.Count (Pair,Root.Capability_Id,Evaluate_World,Zero_Digest,
                              Interfaces.Unsigned_32'Last).Valid);
end Use_Reservation_Tests;
