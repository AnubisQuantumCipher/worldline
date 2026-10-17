with Resource_Quantities;
with Resource_Reservation_Transition;
with SPARK.Big_Integers;

package Worldline.Recovery_Authorization_V3 with SPARK_Mode is
   package Q renames Resource_Quantities;
   package T renames Resource_Reservation_Transition;
   use type Q.Ordering;
   use type SPARK.Big_Integers.Valid_Big_Integer;
   use type Hash;
   --  Pure relation only: protected capture, historical raw-input redecision,
   --  serialization, durability and authentic receipt custody are separate
   --  caller obligations. This package does not authorize a bare exchange.
   type Use_State is (Issued, Claimed, Completed, Denied);
   type Fresh_Verdict is (Authorized, Refused);
   type Historical_Verdict is (Unestablished, Historically_Authorized);
   type Native_State is (Before_Effect, After_Effect, Uncertain);
   type Promotion_Mode is (Candidate, Staged, Checkpoint_Return);
   type Recovery_Action is
     (Refuse, Invoke_Actuator, Reconcile_Actuator, Settle, Replay, Abort_Use);

   type Optional_Digest is record
      Present : Boolean := False;
      Value : Hash := [others => 0];
   end record;
   --  Exactly the persistent reservation epoch domain: typed absence plus
   --  arbitrary little-endian magnitudes. Storage extents do not cap values.
   --  Original leading padding and signed zero retain their original meaning.
   subtype Optional_Epoch is Q.Optional_Quantity;
   function Same (Left, Right : Optional_Digest) return Boolean is
     (Left.Present and then Right.Present and then Left.Value = Right.Value)
     with Global => null;
   function Same_Epoch_Reference
     (Data : Q.Byte_Array; Left, Right : Optional_Epoch) return Boolean is
     (T.Epoch_Valid (Data, Left) and then T.Epoch_Valid (Data, Right)
      and then Q.Value (Data, Left.Value) = Q.Value (Data, Right.Value))
     with Ghost, Global => null;
   function Same
     (Data : Q.Byte_Array; Left, Right : Optional_Epoch) return Boolean
     with Global => null,
       Post => Same'Result = Same_Epoch_Reference (Data, Left, Right);

   --  Absence refuses in every required field, including absent/absent.
   --  A present genesis zero is allowed; zero is not a presence sentinel.
   type Binding is record
      Mode : Promotion_Mode := Candidate;
      Operation : Optional_Digest;
      Transaction : Optional_Digest;
      Capability : Optional_Digest;
      Universe_Head : Optional_Digest;
      Instance : Optional_Digest;
      Subject : Optional_Digest;
      Staged_Root : Optional_Digest;
      Current_Requirement : Optional_Digest;
      Resulting_Requirement : Optional_Digest;
      Requester : Optional_Digest;
      Grant_Use : Optional_Digest;
      Policy_Identity : Optional_Digest;
      Selected_Evaluation : Optional_Digest;
      History_Head : Optional_Digest;
      Reservation : Optional_Digest;
      Host : Optional_Digest;
      Before_Prime : Optional_Digest;
      Before_Root : Optional_Digest;
      Before_Mapping : Optional_Digest;
      Staged_Mapping : Optional_Digest;
      Input_Snapshot : Optional_Digest;
      Kernel_Build : Optional_Digest;
      Kernel_Library : Optional_Digest;
      Kernel_Mapping : Optional_Digest;
      Issuer_Head : Optional_Digest;
      Receipt_Head : Optional_Digest;
      Causal_Head : Optional_Digest;
      Policy_Epoch, Resource_Epoch : Optional_Epoch;
   end record;
   function Same_Binding_Reference
     (Data : Q.Byte_Array; Left, Right : Binding) return Boolean is
     (Left.Mode = Right.Mode
      and then Same (Left.Operation, Right.Operation)
      and then Same (Left.Transaction, Right.Transaction)
      and then Same (Left.Capability, Right.Capability)
      and then Same (Left.Universe_Head, Right.Universe_Head)
      and then Same (Left.Instance, Right.Instance)
      and then Same (Left.Subject, Right.Subject)
      and then Same (Left.Staged_Root, Right.Staged_Root)
      and then Same (Left.Current_Requirement, Right.Current_Requirement)
      and then Same (Left.Resulting_Requirement, Right.Resulting_Requirement)
      and then Same (Left.Requester, Right.Requester)
      and then Same (Left.Grant_Use, Right.Grant_Use)
      and then Same (Left.Policy_Identity, Right.Policy_Identity)
      and then Same (Left.Selected_Evaluation, Right.Selected_Evaluation)
      and then Same (Left.History_Head, Right.History_Head)
      and then Same (Left.Reservation, Right.Reservation)
      and then Same (Left.Host, Right.Host)
      and then Same (Left.Before_Prime, Right.Before_Prime)
      and then Same (Left.Before_Root, Right.Before_Root)
      and then Same (Left.Before_Mapping, Right.Before_Mapping)
      and then Same (Left.Staged_Mapping, Right.Staged_Mapping)
      and then Same (Left.Input_Snapshot, Right.Input_Snapshot)
      and then Same (Left.Kernel_Build, Right.Kernel_Build)
      and then Same (Left.Kernel_Library, Right.Kernel_Library)
      and then Same (Left.Kernel_Mapping, Right.Kernel_Mapping)
      and then Same (Left.Issuer_Head, Right.Issuer_Head)
      and then Same (Left.Receipt_Head, Right.Receipt_Head)
      and then Same (Left.Causal_Head, Right.Causal_Head)
      and then Same_Epoch_Reference (Data, Left.Policy_Epoch, Right.Policy_Epoch)
      and then Same_Epoch_Reference (Data, Left.Resource_Epoch, Right.Resource_Epoch))
     with Ghost, Global => null;

   function Same
     (Data : Q.Byte_Array; Left, Right : Binding) return Boolean is
     (Left.Mode = Right.Mode
      and then Same (Left.Operation, Right.Operation)
      and then Same (Left.Transaction, Right.Transaction)
      and then Same (Left.Capability, Right.Capability)
      and then Same (Left.Universe_Head, Right.Universe_Head)
      and then Same (Left.Instance, Right.Instance)
      and then Same (Left.Subject, Right.Subject)
      and then Same (Left.Staged_Root, Right.Staged_Root)
      and then Same (Left.Current_Requirement, Right.Current_Requirement)
      and then Same (Left.Resulting_Requirement, Right.Resulting_Requirement)
      and then Same (Left.Requester, Right.Requester)
      and then Same (Left.Grant_Use, Right.Grant_Use)
      and then Same (Left.Policy_Identity, Right.Policy_Identity)
      and then Same (Left.Selected_Evaluation, Right.Selected_Evaluation)
      and then Same (Left.History_Head, Right.History_Head)
      and then Same (Left.Reservation, Right.Reservation)
      and then Same (Left.Host, Right.Host)
      and then Same (Left.Before_Prime, Right.Before_Prime)
      and then Same (Left.Before_Root, Right.Before_Root)
      and then Same (Left.Before_Mapping, Right.Before_Mapping)
      and then Same (Left.Staged_Mapping, Right.Staged_Mapping)
      and then Same (Left.Input_Snapshot, Right.Input_Snapshot)
      and then Same (Left.Kernel_Build, Right.Kernel_Build)
      and then Same (Left.Kernel_Library, Right.Kernel_Library)
      and then Same (Left.Kernel_Mapping, Right.Kernel_Mapping)
      and then Same (Left.Issuer_Head, Right.Issuer_Head)
      and then Same (Left.Receipt_Head, Right.Receipt_Head)
      and then Same (Left.Causal_Head, Right.Causal_Head)
      and then Same (Data, Left.Policy_Epoch, Right.Policy_Epoch)
      and then Same (Data, Left.Resource_Epoch, Right.Resource_Epoch))
     with Global => null,
       Post => Same'Result = Same_Binding_Reference (Data, Left, Right);

   --  Actual descriptor/mapping capture and payload recapture supply these
   --  identities. A generation marker cannot stand for either observation.
   type Native_Observation is record
      Live_Mapping, Live_Root : Optional_Digest;
   end record;
   function Classify_Native
     (Authorized_Binding : Binding; Observed : Native_Observation)
      return Native_State
   with Global => null,
     Post => Classify_Native'Result =
       (if Same (Observed.Live_Mapping, Authorized_Binding.Before_Mapping)
          and then Same (Observed.Live_Root, Authorized_Binding.Before_Root)
          and then not
            (Same (Observed.Live_Mapping, Authorized_Binding.Staged_Mapping)
             and then Same (Observed.Live_Root, Authorized_Binding.Staged_Root))
        then Before_Effect
        elsif Same (Observed.Live_Mapping, Authorized_Binding.Staged_Mapping)
          and then Same (Observed.Live_Root, Authorized_Binding.Staged_Root)
          and then not
            (Same (Observed.Live_Mapping, Authorized_Binding.Before_Mapping)
             and then Same (Observed.Live_Root, Authorized_Binding.Before_Root))
        then After_Effect
        else Uncertain);

   --  Before exchange, Recovered_Binding comes from fresh protected capture
   --  under the actuator lock. After exchange it is reconstructed from the
   --  authenticated historical inputs/effect, bound to the actual loaded
   --  kernel mapping. Historical is a redecision of those original raw
   --  inputs. A current revocation/refusal cannot erase an established effect.
   --  Settle/Replay never permit another exchange or another grant use.
   function Action_Reference
     (Data : Q.Byte_Array; State : Use_State;
      Issued_Binding, Recovered_Binding : Binding;
      Fresh : Fresh_Verdict; Historical : Historical_Verdict;
      Grant_Eligible : Boolean; Native : Native_Observation)
      return Recovery_Action
   is
       (if not Same_Binding_Reference (Data, Issued_Binding, Recovered_Binding) then Refuse
        elsif State = Completed
          and then Classify_Native (Issued_Binding, Native) = After_Effect
          and then Historical = Historically_Authorized then Replay
        elsif State = Claimed
          and then Classify_Native (Issued_Binding, Native) = After_Effect
          and then Historical = Historically_Authorized then Settle
        elsif Classify_Native (Issued_Binding, Native) = Before_Effect
          and then (State = Issued or else State = Claimed) then
          (if Fresh = Refused or else not Grant_Eligible then Abort_Use
           elsif State = Issued then Invoke_Actuator
           else Reconcile_Actuator)
        else Refuse)
   with Ghost, Global => null;

   function Select_Action
     (Data : Q.Byte_Array; State : Use_State;
      Issued_Binding, Recovered_Binding : Binding;
      Fresh : Fresh_Verdict; Historical : Historical_Verdict;
      Grant_Eligible : Boolean; Native : Native_Observation)
      return Recovery_Action
   with Global => null,
     Post => Select_Action'Result =
       Action_Reference (Data, State, Issued_Binding, Recovered_Binding,
                         Fresh, Historical, Grant_Eligible, Native);

   function Next_State
     (State : Use_State; Action : Recovery_Action) return Use_State
   with Global => null,
     Post => Next_State'Result =
       (if State = Issued and then Action = Invoke_Actuator then Claimed
        elsif State = Claimed and then Action = Settle then Completed
        elsif (State = Issued or else State = Claimed)
          and then Action = Abort_Use then Denied
        else State);
end Worldline.Recovery_Authorization_V3;
