with Worldline.Transitions;

package Worldline.Collapse with SPARK_Mode is
   use type Hash;
   use type Transitions.World_State;


   --  Which evidence speaks for the bytes that would become live (1.8.0).
   --  Candidate_Evaluation: the candidate's own evaluation, fresh against the
   --  current requirements, with a complete roster and the executed verifier
   --  identity. Checkpoint_Return: a previous reality WORLDLINE itself made
   --  live; there is no candidate evaluation, and the case must carry a
   --  lineage witness instead of passing by having nothing to check.
   type Evaluation_Mode is (Candidate_Evaluation, Checkpoint_Return);

   type Collapse_Request is record
      Candidate_State            : Transitions.World_State;
      Has_Conflicts              : Boolean;
      Has_Foreign_Managed_Writes : Boolean;
      Expected_Parent            : Hash;
      Candidate_Parent           : Hash;
      Expected_Owner             : Hash;
      Candidate_Owner            : Hash;
      Expected_Base              : Hash;
      Candidate_Base             : Hash;
      Expected_Delta             : Hash;
      Candidate_Delta            : Hash;
      Expected_Root_Set          : Hash;
      Candidate_Root_Set         : Hash;
      Expected_Staged_Root       : Hash;
      Actual_Staged_Root         : Hash;
      --  Evidence freshness (1.3.0): the requirement identity the candidate's evidence was
      --  evaluated against must equal the one the current PRIME imposes, and the bytes that
      --  will become live (the staged result) must be the bytes that were tested.
      Expected_Validation_Context  : Hash;
      Candidate_Validation_Context : Hash;
      Tested_Root                  : Hash;
      Staged_Content_Root          : Hash;
      --  Execution-time verifier identity (1.5.0). Binding a result to the verifier bytes that
      --  were EXECUTED is a different obligation from binding it to the bytes that exist before
      --  or afterwards, and the difference is a whole attack: replace the examiner, run the
      --  replacement, restore the original, finalize.
      --
      --  Execution_Evidence_Complete is the roster condition. It is False when any required
      --  check has no execution record, an unreadable one, or one whose provenance could not be
      --  established. A missing measurement is not a satisfied one.
      --
      --  The two identities MUST be computed from different sources: the expected one from the
      --  trusted evaluator specification, the actual one from the runner's protected execution
      --  record. Passing one computed value twice would prove an equality that assures nothing,
      --  and that obligation lives outside this package because this package cannot check it.
      Execution_Evidence_Complete  : Boolean;
      Expected_Executed_Verifier   : Hash;
      Actual_Executed_Verifier     : Hash;
      --  1.8.0. In Checkpoint_Return mode the candidate-evaluation fields
      --  above (validation context, roster, executed verifier) are not
      --  consulted; the witness below is. Expected_Checkpoint is the subject's
      --  own content identity; Witnessed_Checkpoint is the content identity a
      --  DIFFERENT record states for it: the PRIME lineage (the child PRIME
      --  that recorded it as its parent) or the PRIME register itself.
      Mode                         : Evaluation_Mode;
      Checkpoint_Witnessed         : Boolean;
      Expected_Checkpoint          : Hash;
      Witnessed_Checkpoint         : Hash;
   end record;

   type Decision is
     (Authorized,
      Invalid_Candidate,
      Parent_Mismatch,
      Owner_Mismatch,
      Base_Mismatch,
      Delta_Mismatch,
      Root_Set_Mismatch,
      Staged_Root_Mismatch,
      Conflict,
      Foreign_Managed_Write,
      Validation_Context_Mismatch,
      Staged_Untested,
      --  Appended, so the ordinals of every existing decision are unchanged and a client that
      --  has not been rebuilt cannot silently reinterpret an old code as a new one.
      Execution_Evidence_Incomplete,
      Verifier_Execution_Identity_Mismatch,
      --  Appended for 1.8.0.
      Checkpoint_Unwitnessed);

   --  The evidence obligation for the request's mode, stated once so the
   --  contract and every reader agree on which fields a mode consults.
   function Evidence_Holds (Request : Collapse_Request) return Boolean is
     (case Request.Mode is
        when Candidate_Evaluation =>
          Request.Expected_Validation_Context =
            Request.Candidate_Validation_Context
          and Request.Execution_Evidence_Complete
          and Request.Expected_Executed_Verifier =
            Request.Actual_Executed_Verifier,
        when Checkpoint_Return =>
          Request.Checkpoint_Witnessed
          and Request.Expected_Checkpoint = Request.Witnessed_Checkpoint)
     with Global => null;

   function Decide (Request : Collapse_Request) return Decision
     with Global => null,
          Post =>
            (Decide'Result = Authorized) =
              (Request.Candidate_State = Transitions.Valid
               and Request.Expected_Parent = Request.Candidate_Parent
               and Request.Expected_Owner = Request.Candidate_Owner
               and Request.Expected_Base = Request.Candidate_Base
               and Request.Expected_Delta = Request.Candidate_Delta
               and Request.Expected_Root_Set = Request.Candidate_Root_Set
               and Request.Expected_Staged_Root = Request.Actual_Staged_Root
               and Request.Tested_Root = Request.Staged_Content_Root
               and Evidence_Holds (Request)
               and not Request.Has_Conflicts
               and not Request.Has_Foreign_Managed_Writes);

end Worldline.Collapse;
