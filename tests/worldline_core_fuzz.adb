with Ada.Numerics.Discrete_Random;
with Ada.Text_IO;
with Interfaces;
with Worldline;
with Worldline.Collapse;
with Worldline.Identities;
with Worldline.Transitions;

--  Randomised check of the collapse decision against an oracle written
--  separately from the kernel (1.9.0): every identity pair -- including the
--  watch sets and each staged-evidence value against the value it must
--  equal -- is drawn as equal, different, one side absent or both absent;
--  modes, phases and measurements vary. Decide must authorize exactly when
--  the oracle does, never return the retired Owner_Mismatch, and report a
--  reason the oracle's own restatement says is the case, for every code.
procedure Worldline_Core_Fuzz is
   use Worldline.Collapse;
   use Worldline.Identities;
   use type Interfaces.Unsigned_8;
   use type Worldline.Transitions.Transaction_State;
   use type Worldline.Transitions.World_State;
   use type Worldline.Hash;
   use type Interfaces.Unsigned_64;

   subtype Pair_Shape is Natural range 0 .. 3;  --  equal, differ, one absent, both absent
   package Shape_Random is new Ada.Numerics.Discrete_Random (Pair_Shape);
   package Byte_Random is new Ada.Numerics.Discrete_Random (Interfaces.Unsigned_8);
   package Bool_Random is new Ada.Numerics.Discrete_Random (Boolean);
   subtype Tri is Natural range 0 .. 2;
   package Tri_Random is new Ada.Numerics.Discrete_Random (Tri);

   Shapes : Shape_Random.Generator;
   Bytes  : Byte_Random.Generator;
   Bools  : Bool_Random.Generator;
   Tris   : Tri_Random.Generator;

   procedure Check (Condition : Boolean; Message : String) is
   begin
      if not Condition then
         raise Program_Error with Message;
      end if;
   end Check;

   --  Mostly "equal", so authorizations are common enough to matter.
   function Shape return Pair_Shape is
     (if Bool_Random.Random (Bools) then 0 else Shape_Random.Random (Shapes));

   function Value return Worldline.Hash is
      V : constant Interfaces.Unsigned_8 := Byte_Random.Random (Bytes) or 1;
   begin
      return [others => V];
   end Value;

   --  Draw an (L, R) pair as raw hashes plus presence.
   procedure Draw (L_Present, R_Present : out Boolean; L, R : out Worldline.Hash) is
      K : constant Pair_Shape := Shape;
   begin
      L := Value;
      R := L;
      L_Present := True;
      R_Present := True;
      case K is
         when 0 => null;
         when 1 => R (R'First) := R (R'First) xor 16#80#;
         when 2 => R_Present := False;
         when 3 => L_Present := False; R_Present := False;
      end case;
   end Draw;

   --  A value drawn relative to another: the same, different, or absent.
   procedure Relative (Base : Worldline.Hash; Present : out Boolean; V : out Worldline.Hash) is
      K : constant Pair_Shape := Shape;
   begin
      V := Base;
      Present := K <= 1;
      if K = 1 then
         V (V'First) := V (V'First) xor 16#40#;
      elsif K >= 2 then
         V := [others => 0];
      end if;
   end Relative;

   --  The oracle: the rule restated from the specification text, not from the
   --  kernel's expression functions.
   function Eq (LP, RP : Boolean; L, R : Worldline.Hash) return Boolean is
     (LP and then RP and then L = R);
   function Ne (LP, RP : Boolean; L, R : Worldline.Hash) return Boolean is
     (LP and then RP and then L /= R);

   Req : Collapse_Request;
   Authorizations : Natural := 0;
   Seen : array (Decision) of Boolean := [others => False];

   type Pair is record
      LP, RP : Boolean;
      L, R   : Worldline.Hash;
   end record;
   P : array (1 .. 13) of Pair;
   SER_P, SEV_P, SXR_P : Boolean;
   SER, SEV, SXR : Worldline.Hash;
   G_Before, G_After : Optional_Generation;
   Transaction : Worldline.Transitions.Transaction_State;
begin
   Shape_Random.Reset (Shapes, 16#574C#);
   Byte_Random.Reset (Bytes, 16#434F5245#);
   Bool_Random.Reset (Bools, 16#1900#);
   Tri_Random.Reset (Tris, 16#0190#);

   for Iteration in 1 .. 20_000 loop
      for I in P'Range loop
         Draw (P (I).LP, P (I).RP, P (I).L, P (I).R);
      end loop;
      Relative (P (8).L, SER_P, SER);   --  staged evaluated requirement vs current
      Relative (P (9).L, SEV_P, SEV);   --  staged executed verifiers vs declared
      Relative (P (7).L, SXR_P, SXR);   --  staged examined root vs staged content
      G_Before := (Present => True, Value => 7);
      G_After := G_Before;
      case Shape is
         when 0 => null;
         when 1 => G_After.Value := 8;
         when 2 => G_After := (others => <>);
         when 3 => G_Before := (others => <>); G_After := (others => <>);
      end case;

      Req :=
        (Candidate_State => (if Shape = 0 then Worldline.Transitions.Valid
                             else Worldline.Transitions.Degraded),
         Request_Phase => (if Bool_Random.Random (Bools) then Commit else Prepare),
         Mode => (if Bool_Random.Random (Bools) then Candidate_Evaluation else Checkpoint_Return),
         Conflicts => (if Shape = 0 then None_Found else Measurement'Val (Tri_Random.Random (Tris))),
         Foreign_Writes => (if Shape = 0 then None_Found else Measurement'Val (Tri_Random.Random (Tris))),
         Roster_Complete => Shape = 0,
         Staged_Roster_Complete => Bool_Random.Random (Bools),
         Expected_Parent => (P (1).LP, Content_Id (P (1).L)),
         Candidate_Parent => (P (1).RP, Content_Id (P (1).R)),
         Expected_Subject => (P (2).LP, Subject_Id (P (2).L)),
         Evidence_Subject => (P (2).RP, Subject_Id (P (2).R)),
         Expected_Base => (P (3).LP, State_Root (P (3).L)),
         Candidate_Base => (P (3).RP, State_Root (P (3).R)),
         Expected_Delta => (P (4).LP, Delta_Id (P (4).L)),
         Candidate_Delta => (P (4).RP, Delta_Id (P (4).R)),
         Expected_Root_Set => (P (5).LP, Root_Set_Id (P (5).L)),
         Candidate_Root_Set => (P (5).RP, Root_Set_Id (P (5).R)),
         Expected_Staged_Root => (P (6).LP, State_Root (P (6).L)),
         Actual_Staged_Root => (P (6).RP, State_Root (P (6).R)),
         Staged_Content_Root => (P (7).LP, Content_Root (P (7).L)),
         Tested_Root => (P (7).RP, Content_Root (P (7).R)),
         Current_Requirement => (P (8).LP, Requirement_Id (P (8).L)),
         Evaluated_Requirement => (P (8).RP, Requirement_Id (P (8).R)),
         Declared_Verifiers => (P (9).LP, Verifier_Set_Id (P (9).L)),
         Executed_Verifiers => (P (9).RP, Verifier_Set_Id (P (9).R)),
         Staged_Evaluated_Requirement => (SER_P, Requirement_Id (SER)),
         Staged_Executed_Verifiers => (SEV_P, Verifier_Set_Id (SEV)),
         Staged_Examined_Root => (SXR_P, Content_Root (SXR)),
         Expected_Checkpoint => (P (12).LP, Content_Id (P (12).L)),
         Witnessed_Checkpoint => (P (12).RP, Content_Id (P (12).R)),
         Registered_Watch_Set => (P (13).LP, Watch_Set_Id (P (13).L)),
         Watched_Set => (P (13).RP, Watch_Set_Id (P (13).R)),
         Generation_Before => G_Before,
         Generation_After => G_After);

      declare
         Staged_Root_OK : constant Boolean :=
           (if Req.Request_Phase = Commit
            then Eq (P (6).LP, P (6).RP, P (6).L, P (6).R)
            else P (6).LP);
         Primary : constant Boolean := Eq (P (7).LP, P (7).RP, P (7).L, P (7).R);
         Staged : constant Boolean :=
           Eq (P (8).LP, SER_P, P (8).L, SER)
           and then Req.Staged_Roster_Complete
           and then Eq (P (9).LP, SEV_P, P (9).L, SEV)
           and then Eq (SXR_P, P (7).LP, SXR, P (7).L);
         Measured_O : constant Boolean :=
           Req.Conflicts /= Unmeasured and then Req.Foreign_Writes /= Unmeasured
           and then G_Before.Present and then G_After.Present
           and then P (13).LP and then P (13).RP;
         Required_O : constant Boolean :=
           (for all I in 1 .. 5 => P (I).LP and then P (I).RP)
           and then P (7).LP and then P (6).LP
           and then (Req.Request_Phase = Prepare or else P (6).RP)
           and then (if Req.Mode = Candidate_Evaluation
                     then P (8).LP and P (8).RP and P (9).LP and P (9).RP
                     else P (12).LP);
         Evidence : constant Boolean :=
           (if Req.Mode = Candidate_Evaluation
            then Eq (P (8).LP, P (8).RP, P (8).L, P (8).R)
                 and then Req.Roster_Complete
                 and then Eq (P (9).LP, P (9).RP, P (9).L, P (9).R)
            else Eq (P (12).LP, P (12).RP, P (12).L, P (12).R))
           and then (Primary or else Staged);
         Expected_Authorized : constant Boolean :=
           Req.Candidate_State = Worldline.Transitions.Valid
           and then Req.Conflicts = None_Found
           and then Req.Foreign_Writes = None_Found
           and then Eq (P (13).LP, P (13).RP, P (13).L, P (13).R)
           and then G_Before.Present and then G_After.Present
           and then G_Before.Value = G_After.Value
           and then (for all I in 1 .. 5 => Eq (P (I).LP, P (I).RP, P (I).L, P (I).R))
           and then Staged_Root_OK
           and then Evidence;
         Got : constant Decision := Decide (Req);
      begin
         Check ((Got = Authorized) = Expected_Authorized,
                "oracle disagrees at iteration" & Positive'Image (Iteration)
                & ": kernel " & Decision'Image (Got));
         Check (Got /= Owner_Mismatch, "retired decision returned");
         Check (Expected_Authorized <= (Required_O and Measured_O), "oracle authorizes something absent");
         --  Every refusal names something the oracle's restatement says is the case.
         Check ((case Got is
                   when Authorized => True,
                   when Owner_Mismatch => False,
                   when Invalid_Candidate => Req.Candidate_State /= Worldline.Transitions.Valid,
                   when Conflict => Req.Conflicts = Found,
                   when Foreign_Managed_Write => Req.Foreign_Writes = Found,
                   when Measurement_Absent => not Measured_O,
                   when Identity_Absent => not Required_O,
                   when Watch_Incomplete => Ne (P (13).LP, P (13).RP, P (13).L, P (13).R),
                   when Prime_Changed =>
                     G_Before.Present and G_After.Present and G_Before.Value /= G_After.Value,
                   when Parent_Mismatch => Ne (P (1).LP, P (1).RP, P (1).L, P (1).R),
                   when Evidence_Subject_Mismatch => Ne (P (2).LP, P (2).RP, P (2).L, P (2).R),
                   when Base_Mismatch => Ne (P (3).LP, P (3).RP, P (3).L, P (3).R),
                   when Delta_Mismatch => Ne (P (4).LP, P (4).RP, P (4).L, P (4).R),
                   when Root_Set_Mismatch => Ne (P (5).LP, P (5).RP, P (5).L, P (5).R),
                   when Staged_Root_Mismatch =>
                     Req.Request_Phase = Commit and Ne (P (6).LP, P (6).RP, P (6).L, P (6).R),
                   when Execution_Evidence_Incomplete =>
                     Req.Mode = Candidate_Evaluation and not Req.Roster_Complete,
                   when Validation_Context_Mismatch =>
                     Req.Mode = Candidate_Evaluation and Ne (P (8).LP, P (8).RP, P (8).L, P (8).R),
                   when Verifier_Execution_Identity_Mismatch =>
                     Req.Mode = Candidate_Evaluation and Ne (P (9).LP, P (9).RP, P (9).L, P (9).R),
                   when Checkpoint_Unwitnessed => Req.Mode = Checkpoint_Return and not P (12).RP,
                   when Checkpoint_Mismatch =>
                     Req.Mode = Checkpoint_Return and Ne (P (12).LP, P (12).RP, P (12).L, P (12).R),
                   when Staged_Untested => not Primary and not Staged),
                "reason " & Decision'Image (Got) & " unsound at iteration" & Positive'Image (Iteration));
         Seen (Got) := True;
         if Got = Authorized then
            Authorizations := Authorizations + 1;
         end if;
      end;

      Transaction := Worldline.Transitions.Prepared;
      Worldline.Transitions.Advance (Transaction, Worldline.Transitions.Denied);
      Worldline.Transitions.Advance (Transaction, Worldline.Transitions.Committed);
      Check (Transaction = Worldline.Transitions.Denied,
             "denied transaction escaped at iteration" & Positive'Image (Iteration));
   end loop;

   Check (Authorizations > 0, "the fuzz never reached an authorization");
   for D in Decision loop
      Check (Seen (D) = (D /= Owner_Mismatch), "decision " & Decision'Image (D) & " never drawn");
   end loop;
   Ada.Text_IO.Put_Line ("worldline_core_fuzz: PASS (" & Natural'Image (Authorizations)
                         & " authorized of 20000)");
end Worldline_Core_Fuzz;
