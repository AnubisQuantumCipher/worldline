package body Cosmogony.Capabilities with SPARK_Mode => On is

   function Derive
     (U : Universe_State; Authority_Id, Caller_Id : Digest;
      Parent : Capability; Proposal : Grant_Proposal;
      Now_Tick : Interfaces.Unsigned_64) return Grant_Decision
   is
      Child : Capability;
   begin
      if not Valid_Genesis (U) then
         return (False, Invalid_Universe, Null_Capability);
      elsif Authority_Id = Zero_Digest or else Caller_Id /= U.Mission_Id then
         return (False, Wrong_Issuer_Identity, Null_Capability);
      elsif not Well_Formed (Parent)
        or else Parent.Terminal
        or else not Bound_To (U, Authority_Id, Parent)
        or else not Role_Bounds_Grant
          (U, Parent.Subject_Id, Parent.Granted)
        or else Parent.Issued_At > Now_Tick
        or else Now_Tick >= Parent.Expires_At
      then
         return (False, Invalid_Parent, Null_Capability);
      elsif Proposal.Capability_Id = Zero_Digest
        or else Proposal.Capability_Id = Parent.Capability_Id
        or else Proposal.Subject_Id = Zero_Digest
        or else Proposal.Subject_Id = U.Mission_Id
        or else Now_Tick >= Proposal.Expires_At
      then
         return (False, Invalid_Proposal, Null_Capability);
      elsif Proposal.Expires_At > Parent.Expires_At
        or else not Rights_Within (Proposal.Granted, Parent.Granted)
        or else not Role_Bounds_Grant
          (U, Proposal.Subject_Id, Proposal.Granted)
        or else not Scope_Within (Proposal.Applies_To, Parent.Applies_To)
        or else Proposal.Ceiling.Worlds > Parent.Ceiling.Worlds
        or else Proposal.Ceiling.Evaluations > Parent.Ceiling.Evaluations
      then
         return (False, Amplifies_Authority, Null_Capability);
      end if;

      Child :=
        (Capability_Id => Proposal.Capability_Id,
         Parent_Id => Parent.Capability_Id,
         Universe_Id => Parent.Universe_Id,
         Mission_Id => Parent.Mission_Id,
         Policy_Id => Parent.Policy_Id,
         Authority_Id => Parent.Authority_Id,
         Worldline_Instance_Id => Parent.Worldline_Instance_Id,
         Root_Set_Id => Parent.Root_Set_Id,
         Prime_Id => Parent.Prime_Id,
         Subject_Id => Proposal.Subject_Id,
         Issuer_Id => Parent.Issuer_Id,
         Policy_Epoch => Parent.Policy_Epoch,
         Issued_At => Now_Tick,
         Expires_At => Proposal.Expires_At,
         Terminal => False,
         Granted => Proposal.Granted,
         Applies_To => Proposal.Applies_To,
         Ceiling => Proposal.Ceiling);
      return (True, Grant_Allowed, Child);
   end Derive;

   function Check_Request
     (U : Universe_State; Authority_Id : Digest; C : Capability;
      Q : Scoped_Request; Usage : Resource_Usage;
      Now_Tick : Interfaces.Unsigned_64) return Check_Decision
   is
   begin
      if not Valid_Genesis (U) then
         return (Refused, Invalid_Universe_State);
      elsif not Well_Formed (C) then
         return (Refused, Malformed_Capability);
      elsif Authority_Id = Zero_Digest
        or else not Bound_To (U, Authority_Id, C)
      then
         return (Refused, Foreign_Capability_Binding);
      elsif C.Terminal
        or else C.Issued_At > Now_Tick
        or else Now_Tick >= C.Expires_At
      then
         return (Refused, Expired_Or_Terminal);
      elsif Q.Ask.Actor_Id /= C.Subject_Id
        or else not Role_Allows (U, Q.Ask.Actor_Id, Q.Ask.Action)
      then
         return (Refused, Wrong_Subject_Or_Role);
      elsif not C.Granted (Q.Ask.Action) then
         return (Refused, Right_Not_Granted);
      elsif not Scope_Allows (C, Q) then
         return (Refused, Scope_Refused);
      elsif not Usage_Valid (C, Usage) then
         return (Refused, Invalid_Usage);
      elsif not Has_Grant_Capacity (C, Usage, Q.Ask.Action) then
         return (Refused, Ceiling_Exhausted);
      elsif not Cosmogony.Genesis.Eligible (U, Q.Ask) then
         return (Refused, Genesis_Refused);
      elsif Is_Forwardable (Q.Ask.Action) then
         return (Eligible_Worldline, Worldline_Request_Eligible);
      else
         return (Eligible_Local, Local_Request_Eligible);
      end if;
   end Check_Request;
end Cosmogony.Capabilities;
