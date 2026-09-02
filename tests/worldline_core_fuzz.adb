with Ada.Numerics.Discrete_Random;
with Ada.Text_IO;
with Interfaces;
with Worldline;
with Worldline.Collapse;
with Worldline.Transitions;

procedure Worldline_Core_Fuzz is
   use type Interfaces.Unsigned_8;
   use type Worldline.Collapse.Decision;
   use type Worldline.Transitions.Transaction_State;

   subtype Selector is Natural range 0 .. 9;
   package Selector_Random is new Ada.Numerics.Discrete_Random (Selector);
   package Byte_Random is new Ada.Numerics.Discrete_Random
     (Interfaces.Unsigned_8);

   Select_Generator : Selector_Random.Generator;
   Byte_Generator   : Byte_Random.Generator;

   function Random_Hash return Worldline.Hash is
      Result : Worldline.Hash;
   begin
      for I in Result'Range loop
         Result (I) := Byte_Random.Random (Byte_Generator);
      end loop;
      return Result;
   end Random_Hash;

   procedure Check (Condition : Boolean; Message : String) is
   begin
      if not Condition then
         raise Program_Error with Message;
      end if;
   end Check;

   Request     : Worldline.Collapse.Collapse_Request;
   Expected    : Worldline.Collapse.Decision;
   Good        : Worldline.Hash;
   Bad         : Worldline.Hash;
   Transaction : Worldline.Transitions.Transaction_State;
begin
   Selector_Random.Reset (Select_Generator, 16#574C#);
   Byte_Random.Reset (Byte_Generator, 16#434F5245#);

   for Iteration in 1 .. 10_000 loop
      Good := Random_Hash;
      Bad := Good;
      Bad (Bad'First) := Bad (Bad'First) xor 1;
      Request :=
        (Candidate_State => Worldline.Transitions.Valid,
         Has_Conflicts => False,
         Has_Foreign_Managed_Writes => False,
         Expected_Parent => Good,
         Candidate_Parent => Good,
         Expected_Owner => Good,
         Candidate_Owner => Good,
         Expected_Base => Good,
         Candidate_Base => Good,
         Expected_Delta => Good,
         Candidate_Delta => Good,
         Expected_Root_Set => Good,
         Candidate_Root_Set => Good,
         Expected_Staged_Root => Good,
         Actual_Staged_Root => Good);

      case Selector_Random.Random (Select_Generator) is
         when 0 =>
            Expected := Worldline.Collapse.Authorized;
         when 1 =>
            Request.Candidate_State := Worldline.Transitions.Dead;
            Expected := Worldline.Collapse.Invalid_Candidate;
         when 2 =>
            Request.Candidate_Parent := Bad;
            Expected := Worldline.Collapse.Parent_Mismatch;
         when 3 =>
            Request.Candidate_Owner := Bad;
            Expected := Worldline.Collapse.Owner_Mismatch;
         when 4 =>
            Request.Candidate_Base := Bad;
            Expected := Worldline.Collapse.Base_Mismatch;
         when 5 =>
            Request.Candidate_Delta := Bad;
            Expected := Worldline.Collapse.Delta_Mismatch;
         when 6 =>
            Request.Candidate_Root_Set := Bad;
            Expected := Worldline.Collapse.Root_Set_Mismatch;
         when 7 =>
            Request.Actual_Staged_Root := Bad;
            Expected := Worldline.Collapse.Staged_Root_Mismatch;
         when 8 =>
            Request.Has_Conflicts := True;
            Expected := Worldline.Collapse.Conflict;
         when 9 =>
            Request.Has_Foreign_Managed_Writes := True;
            Expected := Worldline.Collapse.Foreign_Managed_Write;
      end case;

      Check
        (Worldline.Collapse.Decide (Request) = Expected,
         "collapse decision mismatch at iteration" &
           Positive'Image (Iteration));

      Transaction := Worldline.Transitions.Prepared;
      Worldline.Transitions.Advance
        (Transaction, Worldline.Transitions.Denied);
      Worldline.Transitions.Advance
        (Transaction, Worldline.Transitions.Committed);
      Check
        (Transaction = Worldline.Transitions.Denied,
         "denied transaction escaped at iteration" &
           Positive'Image (Iteration));
   end loop;

   Ada.Text_IO.Put_Line ("worldline_core_fuzz: PASS");
end Worldline_Core_Fuzz;
