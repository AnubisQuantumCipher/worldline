with Worldline.Custody_V2_Load_Input;
package Worldline.Excluded_Source_Owner with SPARK_Mode is
   package L renames Worldline.Custody_V2_Load_Input;
   package E renames L.E;
   use type E.Count;
   type Action is (Refused, Bootstrap_Acquired, Actor_Acquired, Completed);
   -- Full scoped archive, owned by the synchronous caller. No RootWorker,
   -- enrollment claim, cached approval, digest-only source or producer grant.
   -- LAUNCH binds private selected plan/request/installation, complete fixed
   -- projection and original source. ACQUIRE additionally rejoins all genuine
   -- per-message SCM credentials, proc/PIDFD/channel/directory observations.
   -- COMPLETE needs actual actor finally, owner finally, waitid/wait/pidfd and
   -- complete retained stdout/stderr; missing/unknown/error remains Refused.
   function Launch_Reference (Data : E.Bytes; Frame : E.Span) return Boolean
     with Global => null, Depends => (Launch_Reference'Result => (Data, Frame)),
       Post => (if Launch_Reference'Result then L.V.S.Valid (Data, Frame));
   function Acquisition_Reference (Data : E.Bytes; Frame : E.Span) return Boolean
     with Global => null, Depends => (Acquisition_Reference'Result => (Data, Frame)),
       Post => (if Acquisition_Reference'Result then Launch_Reference (Data, Frame) and then
         L.V.Is_Sequence (Data, L.V.S.Field (Data, Frame, "messages")) and then
         L.V.Count (Data, L.V.S.Field (Data, Frame, "messages")) > 0);
   function Completion_Reference (Data : E.Bytes; Frame : E.Span) return Boolean
     with Global => null, Depends => (Completion_Reference'Result => (Data, Frame)),
       Post => (if Completion_Reference'Result then Acquisition_Reference (Data, Frame));
   -- Complete iff correspondence for ALL four outcomes, including refusal.
   -- Ghost specification is not a second runtime policy or imported promise.
   function Result_Reference (Data : E.Bytes; Result : Action) return Boolean
     with Ghost, Global => null, Depends => (Result_Reference'Result => (Data, Result));
   function Decide (Data : E.Bytes) return Action with Global => null,
     Depends => (Decide'Result => Data), Always_Terminates,
     Post => Result_Reference (Data, Decide'Result);
end Worldline.Excluded_Source_Owner;
