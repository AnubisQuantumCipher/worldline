with Interfaces;
with Worldline.Recovery_Authorization;

package Worldline.Recovery_Authorization_Wire with SPARK_Mode is
   package R renames Worldline.Recovery_Authorization;
   use type Interfaces.Unsigned_8;
   use type Interfaces.Unsigned_64;
   type Raw_Hash is array (Hash'Range) of Interfaces.Unsigned_8
     with Convention => C;
   type Raw_Digest is record
      Present : Interfaces.Unsigned_8;
      Value : Raw_Hash;
   end record with Convention => C;
   type Raw_Epoch is record
      Present : Interfaces.Unsigned_8;
      Value : Interfaces.Unsigned_64;
   end record with Convention => C;
   type Raw_Binding is record
      Mode : Interfaces.Unsigned_8;
      Operation : Raw_Digest;
      Transaction : Raw_Digest;
      Capability : Raw_Digest;
      Universe_Head : Raw_Digest;
      Instance : Raw_Digest;
      Subject : Raw_Digest;
      Staged_Root : Raw_Digest;
      Current_Requirement : Raw_Digest;
      Resulting_Requirement : Raw_Digest;
      Requester : Raw_Digest;
      Grant_Use : Raw_Digest;
      Policy_Identity : Raw_Digest;
      Selected_Evaluation : Raw_Digest;
      History_Head : Raw_Digest;
      Reservation : Raw_Digest;
      Host : Raw_Digest;
      Before_Prime : Raw_Digest;
      Before_Root : Raw_Digest;
      Before_Mapping : Raw_Digest;
      Staged_Mapping : Raw_Digest;
      Input_Snapshot : Raw_Digest;
      Kernel_Build : Raw_Digest;
      Kernel_Library : Raw_Digest;
      Kernel_Mapping : Raw_Digest;
      Issuer_Head : Raw_Digest;
      Receipt_Head : Raw_Digest;
      Causal_Head : Raw_Digest;
      Policy_Epoch, Resource_Epoch : Raw_Epoch;
   end record with Convention => C;
   type Raw_Native is record
      Live_Mapping, Live_Root : Raw_Digest;
   end record with Convention => C;
   type Raw_Request is record
      State, Fresh, Historical, Grant_Eligible : Interfaces.Unsigned_8;
      Issued_Binding, Recovered_Binding : Raw_Binding;
      Native : Raw_Native;
   end record with Convention => C;
   type Raw_Result is record
      Action, State : Interfaces.Unsigned_8;
   end record with Convention => C;

   function Well_Formed (Raw : Raw_Digest) return Boolean is
     (Raw.Present <= 1
      and then (Raw.Present = 1 or else Raw.Value = Raw_Hash'(others => 0)))
     with Global => null;
   function Well_Formed (Raw : Raw_Epoch) return Boolean is
     (Raw.Present <= 1
      and then (Raw.Present = 1 or else Raw.Value = 0))
     with Global => null;
   function Well_Formed (Raw : Raw_Binding) return Boolean is
     (Raw.Mode <= R.Promotion_Mode'Pos (R.Promotion_Mode'Last)
      and then Well_Formed (Raw.Operation)
      and then Well_Formed (Raw.Transaction)
      and then Well_Formed (Raw.Capability)
      and then Well_Formed (Raw.Universe_Head)
      and then Well_Formed (Raw.Instance)
      and then Well_Formed (Raw.Subject)
      and then Well_Formed (Raw.Staged_Root)
      and then Well_Formed (Raw.Current_Requirement)
      and then Well_Formed (Raw.Resulting_Requirement)
      and then Well_Formed (Raw.Requester)
      and then Well_Formed (Raw.Grant_Use)
      and then Well_Formed (Raw.Policy_Identity)
      and then Well_Formed (Raw.Selected_Evaluation)
      and then Well_Formed (Raw.History_Head)
      and then Well_Formed (Raw.Reservation)
      and then Well_Formed (Raw.Host)
      and then Well_Formed (Raw.Before_Prime)
      and then Well_Formed (Raw.Before_Root)
      and then Well_Formed (Raw.Before_Mapping)
      and then Well_Formed (Raw.Staged_Mapping)
      and then Well_Formed (Raw.Input_Snapshot)
      and then Well_Formed (Raw.Kernel_Build)
      and then Well_Formed (Raw.Kernel_Library)
      and then Well_Formed (Raw.Kernel_Mapping)
      and then Well_Formed (Raw.Issuer_Head)
      and then Well_Formed (Raw.Receipt_Head)
      and then Well_Formed (Raw.Causal_Head)
      and then Well_Formed (Raw.Policy_Epoch)
      and then Well_Formed (Raw.Resource_Epoch))
     with Global => null;
   function Well_Formed (Raw : Raw_Native) return Boolean is
     (Well_Formed (Raw.Live_Mapping) and then Well_Formed (Raw.Live_Root))
     with Global => null;
   function Well_Formed (Raw : Raw_Request) return Boolean is
     (Raw.State <= R.Use_State'Pos (R.Use_State'Last)
      and then Raw.Fresh <= R.Fresh_Verdict'Pos (R.Fresh_Verdict'Last)
      and then Raw.Historical <= R.Historical_Verdict'Pos (R.Historical_Verdict'Last)
      and then Raw.Grant_Eligible <= 1
      and then Well_Formed (Raw.Issued_Binding)
      and then Well_Formed (Raw.Recovered_Binding)
      and then Well_Formed (Raw.Native))
     with Global => null;

   function Decode (Raw : Raw_Digest) return R.Optional_Digest is
     (Present => Raw.Present = 1, Value => Hash (Raw.Value))
     with Global => null, Pre => Well_Formed (Raw);
   function Decode (Raw : Raw_Epoch) return R.Optional_Epoch is
     (Present => Raw.Present = 1, Value => Raw.Value)
     with Global => null, Pre => Well_Formed (Raw);
   function Decode (Raw : Raw_Binding) return R.Binding is
     (Mode => R.Promotion_Mode'Val (Raw.Mode),
      Operation => Decode (Raw.Operation),
      Transaction => Decode (Raw.Transaction),
      Capability => Decode (Raw.Capability),
      Universe_Head => Decode (Raw.Universe_Head),
      Instance => Decode (Raw.Instance),
      Subject => Decode (Raw.Subject),
      Staged_Root => Decode (Raw.Staged_Root),
      Current_Requirement => Decode (Raw.Current_Requirement),
      Resulting_Requirement => Decode (Raw.Resulting_Requirement),
      Requester => Decode (Raw.Requester),
      Grant_Use => Decode (Raw.Grant_Use),
      Policy_Identity => Decode (Raw.Policy_Identity),
      Selected_Evaluation => Decode (Raw.Selected_Evaluation),
      History_Head => Decode (Raw.History_Head),
      Reservation => Decode (Raw.Reservation),
      Host => Decode (Raw.Host),
      Before_Prime => Decode (Raw.Before_Prime),
      Before_Root => Decode (Raw.Before_Root),
      Before_Mapping => Decode (Raw.Before_Mapping),
      Staged_Mapping => Decode (Raw.Staged_Mapping),
      Input_Snapshot => Decode (Raw.Input_Snapshot),
      Kernel_Build => Decode (Raw.Kernel_Build),
      Kernel_Library => Decode (Raw.Kernel_Library),
      Kernel_Mapping => Decode (Raw.Kernel_Mapping),
      Issuer_Head => Decode (Raw.Issuer_Head),
      Receipt_Head => Decode (Raw.Receipt_Head),
      Causal_Head => Decode (Raw.Causal_Head),
      Policy_Epoch => Decode (Raw.Policy_Epoch),
      Resource_Epoch => Decode (Raw.Resource_Epoch))
     with Global => null, Pre => Well_Formed (Raw);
   function Decode (Raw : Raw_Native) return R.Native_Observation is
     (Live_Mapping => Decode (Raw.Live_Mapping),
      Live_Root => Decode (Raw.Live_Root))
     with Global => null, Pre => Well_Formed (Raw);

   function Selected_Action (Raw : Raw_Request) return R.Recovery_Action is
     (R.Select_Action
        (R.Use_State'Val (Raw.State), Decode (Raw.Issued_Binding),
         Decode (Raw.Recovered_Binding), R.Fresh_Verdict'Val (Raw.Fresh),
         R.Historical_Verdict'Val (Raw.Historical), Raw.Grant_Eligible = 1,
         Decode (Raw.Native)))
     with Global => null, Pre => Well_Formed (Raw);

   function Decide (Raw : Raw_Request) return Raw_Result
   with Global => null, Pre => Well_Formed (Raw),
     Post => Decide'Result =
       (Action => R.Recovery_Action'Pos (Selected_Action (Raw)),
        State => R.Use_State'Pos
          (R.Next_State (R.Use_State'Val (Raw.State), Selected_Action (Raw))));
end Worldline.Recovery_Authorization_Wire;
