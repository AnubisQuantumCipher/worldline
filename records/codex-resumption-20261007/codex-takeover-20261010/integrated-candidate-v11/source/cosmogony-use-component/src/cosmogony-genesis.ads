with Interfaces;

package Cosmogony.Genesis with SPARK_Mode => On is
   use type Interfaces.Unsigned_64;
   use type Interfaces.Unsigned_32;
   --  Full identities are supplied by the observation boundary. This kernel compares
   --  all digest words; it does not calculate or authenticate a digest.
   type Digest is array (Positive range 1 .. 4) of Interfaces.Unsigned_64;
   Zero_Digest : constant Digest := (others => 0);

   type Agent_Role is (Builder, Adversary, Reviewer, Synthesizer,
                       Held_Out_Evaluator, Observer);
   type Agent_Index is range 1 .. 8;
   type Agent_Count is range 0 .. 8;
   type Agent_Entry is record
      Identity : Digest;
      Role : Agent_Role;
      Enabled : Boolean;
   end record;
   type Agent_Roster is array (Agent_Index) of Agent_Entry;

   type Resource_Budget is record
      World_Limit : Interfaces.Unsigned_32;
      Worlds_Reserved : Interfaces.Unsigned_32;
      Evaluation_Limit : Interfaces.Unsigned_32;
      Evaluations_Reserved : Interfaces.Unsigned_32;
   end record;

   type Universe_State is record
      Universe_Id : Digest;
      Mission_Id : Digest;
      Policy_Id : Digest;
      Policy_Owner_Mission : Digest;
      Worldline_Instance_Id : Digest;
      Root_Set_Id : Digest;
      Prime_Id : Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Budget : Resource_Budget;
      Roster_Count : Agent_Count;
      Roster : Agent_Roster;
   end record;

   type Operation is (Observe, Propose, Create_World, Evaluate_World,
                      Request_Promotion, Authorize_Promotion,
                      Mutate_Prime, Mint_Authority);

   type Request is record
      Request_Id : Digest;
      Universe_Id : Digest;
      Mission_Id : Digest;
      Policy_Id : Digest;
      Worldline_Instance_Id : Digest;
      Root_Set_Id : Digest;
      Prime_Id : Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Actor_Id : Digest;
      Action : Operation;
   end record;

   type Decision_Kind is (Denied, Allowed_Local, Forward_Worldline);
   type Decision_Reason is
     (Invalid_Genesis, Missing_Request_Identity, Foreign_Universe,
      Foreign_Mission, Foreign_Policy, Stale_Epoch, Foreign_Instance,
      Foreign_Root_Set, Stale_Prime, Privileged_Action, Unknown_Or_Disallowed_Agent,
      Resource_Exhausted, Local_Request_Allowed, Worldline_Request_Eligible);
   type Decision is record
      Kind : Decision_Kind;
      Reason : Decision_Reason;
   end record;

   function Valid_Genesis (U : Universe_State) return Boolean;
   function Role_Allows
     (U : Universe_State; Actor : Digest; Action : Operation) return Boolean;
   function Has_Capacity
     (U : Universe_State; Action : Operation) return Boolean;
   function Is_Forwardable (Action : Operation) return Boolean is
     (Action in Create_World | Evaluate_World | Request_Promotion);
   function Is_Privileged (Action : Operation) return Boolean is
     (Action in Authorize_Promotion | Mutate_Prime | Mint_Authority);
   function Bindings_Match (U : Universe_State; R : Request) return Boolean is
     (R.Request_Id /= Zero_Digest
      and then R.Universe_Id = U.Universe_Id
      and then R.Mission_Id = U.Mission_Id
      and then R.Policy_Id = U.Policy_Id
      and then R.Policy_Epoch = U.Policy_Epoch
      and then R.Worldline_Instance_Id = U.Worldline_Instance_Id
      and then R.Root_Set_Id = U.Root_Set_Id
      and then R.Prime_Id = U.Prime_Id);

   function Eligible (U : Universe_State; R : Request) return Boolean is
     (Valid_Genesis (U)
      and then Bindings_Match (U, R)
      and then not Is_Privileged (R.Action)
      and then Role_Allows (U, R.Actor_Id, R.Action)
      and then Has_Capacity (U, R.Action));

   function Decide (U : Universe_State; R : Request) return Decision
     with Post =>
       ((Decide'Result.Kind = Forward_Worldline) =
          (Eligible (U, R) and Is_Forwardable (R.Action)))
       and then
       ((Decide'Result.Kind = Allowed_Local) =
          (Eligible (U, R) and not Is_Forwardable (R.Action)))
       and then
       (if Is_Privileged (R.Action) then Decide'Result.Kind = Denied);
end Cosmogony.Genesis;
