with Interfaces;
with Cosmogony.Genesis;

package Cosmogony.Capabilities with SPARK_Mode => On is
   use Cosmogony.Genesis;
   use type Interfaces.Unsigned_32;
   use type Interfaces.Unsigned_64;

   --  These are value rules. The caller must authenticate the canonical
   --  Universe, issuer, capability lineage, usage counters and clock.
   type Action_Set is array (Operation) of Boolean;
   No_Actions : constant Action_Set := (others => False);

   type Scope_Kind is (Universe_Scope, World_Scope);
   type Scope is record
      Kind : Scope_Kind;
      World_Id : Digest;
   end record;
   Entire_Universe : constant Scope :=
     (Kind => Universe_Scope, World_Id => Zero_Digest);

   type Resource_Ceiling is record
      Worlds : Interfaces.Unsigned_32;
      Evaluations : Interfaces.Unsigned_32;
   end record;
   type Resource_Usage is record
      Worlds : Interfaces.Unsigned_32;
      Evaluations : Interfaces.Unsigned_32;
   end record;

   type Capability is record
      Capability_Id : Digest;
      Parent_Id : Digest;
      Universe_Id : Digest;
      Mission_Id : Digest;
      Policy_Id : Digest;
      Authority_Id : Digest;
      Worldline_Instance_Id : Digest;
      Root_Set_Id : Digest;
      Prime_Id : Digest;
      Subject_Id : Digest;
      Issuer_Id : Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Issued_At : Interfaces.Unsigned_64;
      Expires_At : Interfaces.Unsigned_64;
      Terminal : Boolean;
      Granted : Action_Set;
      Applies_To : Scope;
      Ceiling : Resource_Ceiling;
   end record;

   Null_Capability : constant Capability :=
     (Capability_Id => Zero_Digest, Parent_Id => Zero_Digest,
      Universe_Id => Zero_Digest, Mission_Id => Zero_Digest,
      Policy_Id => Zero_Digest, Authority_Id => Zero_Digest,
      Worldline_Instance_Id => Zero_Digest,
      Root_Set_Id => Zero_Digest, Prime_Id => Zero_Digest,
      Subject_Id => Zero_Digest, Issuer_Id => Zero_Digest,
      Policy_Epoch => 0, Issued_At => 0, Expires_At => 0,
      Terminal => True, Granted => No_Actions,
      Applies_To => Entire_Universe, Ceiling => (0, 0));

   type Grant_Proposal is record
      Capability_Id : Digest;
      Subject_Id : Digest;
      Granted : Action_Set;
      Applies_To : Scope;
      Ceiling : Resource_Ceiling;
      Expires_At : Interfaces.Unsigned_64;
   end record;

   type Grant_Reason is
     (Grant_Allowed, Invalid_Universe, Invalid_Parent,
      Wrong_Issuer_Identity, Invalid_Proposal, Amplifies_Authority,
      Revoked_Ancestor, Invalid_Grant_Ancestry, Stale_Grant_Lifecycle);
   type Grant_Decision is record
      Granted : Boolean;
      Reason : Grant_Reason;
      Child : Capability;
   end record;

   type Scoped_Request is record
      Ask : Request;
      Target_World_Id : Digest;
   end record;
   type Check_Kind is (Refused, Eligible_Local, Eligible_Worldline);
   type Check_Reason is
     (Invalid_Universe_State, Malformed_Capability,
      Foreign_Capability_Binding, Expired_Or_Terminal,
      Wrong_Subject_Or_Role, Right_Not_Granted, Scope_Refused,
     Invalid_Usage, Ceiling_Exhausted, Genesis_Refused,
      Local_Request_Eligible, Worldline_Request_Eligible,
      Revoked_Ancestry, Invalid_Ancestry, Stale_Lifecycle_Epoch);
   type Check_Decision is record
      Kind : Check_Kind;
      Reason : Check_Reason;
   end record;

   function Well_Formed (C : Capability) return Boolean is
     (C.Capability_Id /= Zero_Digest
      and then C.Universe_Id /= Zero_Digest
      and then C.Mission_Id /= Zero_Digest
      and then C.Policy_Id /= Zero_Digest
      and then C.Authority_Id /= Zero_Digest
      and then C.Worldline_Instance_Id /= Zero_Digest
      and then C.Root_Set_Id /= Zero_Digest
      and then C.Prime_Id /= Zero_Digest
      and then C.Subject_Id /= Zero_Digest
      and then C.Issuer_Id = C.Authority_Id
      and then C.Policy_Epoch /= 0
      and then C.Issued_At < C.Expires_At
      and then (if C.Applies_To.Kind = Universe_Scope
                then C.Applies_To.World_Id = Zero_Digest
                else C.Applies_To.World_Id /= Zero_Digest)
      and then (for all A in Operation =>
                  (if Is_Privileged (A) then not C.Granted (A))));

   function Rights_Within (Child, Parent : Action_Set) return Boolean is
     (for all A in Operation => (not Child (A) or else Parent (A)));

   function Scope_Within (Child, Parent : Scope) return Boolean is
     (if Parent.Kind = Universe_Scope
      then Parent.World_Id = Zero_Digest
           and then (if Child.Kind = Universe_Scope
                     then Child.World_Id = Zero_Digest
                     else Child.World_Id /= Zero_Digest)
      else Child.Kind = World_Scope
           and then Parent.World_Id /= Zero_Digest
           and then Child.World_Id = Parent.World_Id);

   function Attenuates (Parent, Child : Capability) return Boolean is
     (Well_Formed (Parent) and then Well_Formed (Child)
      and then Child.Parent_Id = Parent.Capability_Id
      and then Child.Capability_Id /= Parent.Capability_Id
      and then Child.Universe_Id = Parent.Universe_Id
      and then Child.Mission_Id = Parent.Mission_Id
      and then Child.Policy_Id = Parent.Policy_Id
      and then Child.Authority_Id = Parent.Authority_Id
      and then Child.Worldline_Instance_Id = Parent.Worldline_Instance_Id
      and then Child.Root_Set_Id = Parent.Root_Set_Id
      and then Child.Prime_Id = Parent.Prime_Id
      and then Child.Issuer_Id = Parent.Issuer_Id
      and then Child.Policy_Epoch = Parent.Policy_Epoch
      and then Child.Issued_At >= Parent.Issued_At
      and then Child.Expires_At <= Parent.Expires_At
      and then Rights_Within (Child.Granted, Parent.Granted)
      and then Scope_Within (Child.Applies_To, Parent.Applies_To)
      and then Child.Ceiling.Worlds <= Parent.Ceiling.Worlds
      and then Child.Ceiling.Evaluations <= Parent.Ceiling.Evaluations);

   function Bound_To
     (U : Universe_State; Authority_Id : Digest; C : Capability)
      return Boolean is
     (C.Universe_Id = U.Universe_Id
      and then C.Mission_Id = U.Mission_Id
      and then C.Policy_Id = U.Policy_Id
      and then C.Authority_Id = Authority_Id
      and then C.Worldline_Instance_Id = U.Worldline_Instance_Id
      and then C.Root_Set_Id = U.Root_Set_Id
      and then C.Prime_Id = U.Prime_Id
      and then C.Policy_Epoch = U.Policy_Epoch);

   function Role_Bounds_Grant
     (U : Universe_State; Subject : Digest; Granted : Action_Set)
      return Boolean is
     (for all A in Operation =>
        (not Granted (A) or else Role_Allows (U, Subject, A)));

   function Can_Derive
     (U : Universe_State; Authority_Id, Caller_Id : Digest;
      Parent : Capability; Proposal : Grant_Proposal;
      Now_Tick : Interfaces.Unsigned_64) return Boolean is
     (Valid_Genesis (U)
      and then Authority_Id /= Zero_Digest
      and then Caller_Id = U.Mission_Id
      and then Well_Formed (Parent)
      and then not Parent.Terminal
      and then Bound_To (U, Authority_Id, Parent)
      and then Role_Bounds_Grant
        (U, Parent.Subject_Id, Parent.Granted)
      and then Parent.Issued_At <= Now_Tick
      and then Now_Tick < Parent.Expires_At
      and then Proposal.Capability_Id /= Zero_Digest
      and then Proposal.Capability_Id /= Parent.Capability_Id
      and then Proposal.Subject_Id /= Zero_Digest
      and then Proposal.Subject_Id /= U.Mission_Id
      and then Now_Tick < Proposal.Expires_At
      and then Proposal.Expires_At <= Parent.Expires_At
      and then Rights_Within (Proposal.Granted, Parent.Granted)
      and then Role_Bounds_Grant (U, Proposal.Subject_Id, Proposal.Granted)
      and then Scope_Within (Proposal.Applies_To, Parent.Applies_To)
      and then Proposal.Ceiling.Worlds <= Parent.Ceiling.Worlds
      and then Proposal.Ceiling.Evaluations <= Parent.Ceiling.Evaluations);

   function Derive
     (U : Universe_State; Authority_Id, Caller_Id : Digest;
      Parent : Capability; Proposal : Grant_Proposal;
      Now_Tick : Interfaces.Unsigned_64) return Grant_Decision
   with Post =>
     Derive'Result.Granted =
       Can_Derive (U, Authority_Id, Caller_Id, Parent, Proposal, Now_Tick)
     and then
     (if Derive'Result.Granted then
        Derive'Result.Reason = Grant_Allowed
        and then Attenuates (Parent, Derive'Result.Child)
        and then Derive'Result.Child.Subject_Id = Proposal.Subject_Id
        and then Derive'Result.Child.Issued_At = Now_Tick
      else Derive'Result.Child = Null_Capability);

   function Scope_Allows
     (C : Capability; Q : Scoped_Request) return Boolean is
     (if C.Applies_To.Kind = Universe_Scope then True
      else Q.Ask.Action /= Create_World
           and then Q.Target_World_Id = C.Applies_To.World_Id);

   function Usage_Valid
     (C : Capability; Usage : Resource_Usage) return Boolean is
     (Usage.Worlds <= C.Ceiling.Worlds
      and then Usage.Evaluations <= C.Ceiling.Evaluations);

   function Has_Grant_Capacity
     (C : Capability; Usage : Resource_Usage; Action : Operation)
      return Boolean is
     (if Action = Create_World then Usage.Worlds < C.Ceiling.Worlds
      elsif Action = Evaluate_World then
         Usage.Evaluations < C.Ceiling.Evaluations
      else True);

   function Eligible
     (U : Universe_State; Authority_Id : Digest; C : Capability;
      Q : Scoped_Request; Usage : Resource_Usage;
      Now_Tick : Interfaces.Unsigned_64) return Boolean is
     (Valid_Genesis (U)
      and then Authority_Id /= Zero_Digest
      and then Well_Formed (C)
      and then Bound_To (U, Authority_Id, C)
      and then not C.Terminal
      and then C.Issued_At <= Now_Tick
      and then Now_Tick < C.Expires_At
      and then Q.Ask.Actor_Id = C.Subject_Id
      and then C.Granted (Q.Ask.Action)
      and then Scope_Allows (C, Q)
      and then Usage_Valid (C, Usage)
      and then Has_Grant_Capacity (C, Usage, Q.Ask.Action)
      and then Cosmogony.Genesis.Eligible (U, Q.Ask));

   function Check_Request
     (U : Universe_State; Authority_Id : Digest; C : Capability;
      Q : Scoped_Request; Usage : Resource_Usage;
      Now_Tick : Interfaces.Unsigned_64) return Check_Decision
   with Post =>
     ((Check_Request'Result.Kind = Eligible_Worldline) =
        (Eligible (U, Authority_Id, C, Q, Usage, Now_Tick)
         and Is_Forwardable (Q.Ask.Action)))
     and then
     ((Check_Request'Result.Kind = Eligible_Local) =
        (Eligible (U, Authority_Id, C, Q, Usage, Now_Tick)
         and not Is_Forwardable (Q.Ask.Action)))
     and then
     (if Is_Privileged (Q.Ask.Action) then
        Check_Request'Result.Kind = Refused);
end Cosmogony.Capabilities;
