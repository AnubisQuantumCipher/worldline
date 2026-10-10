with Worldline.Archive_Envelope;
--  Consequential gates over complete borrowed original owner captures.
--  Canonical root Quiescent(Data,Span) retains its genuine producer grammar;
--  every runtime action and generation-closure gate uses Finalization bytes.
package Worldline.Runner_Lifecycle with SPARK_Mode is
   package E renames Worldline.Archive_Envelope;
   function Ended (Data : E.Bytes; Rows : E.Span) return Boolean with Global => null;
   function Commands_Ended (Data : E.Bytes; Rows : E.Span) return Boolean with Global => null;
   function Eof_Complete (Data : E.Bytes; Value : E.Span) return Boolean with Global => null;
   function Proxy_Ended (Data : E.Bytes; Proxy : E.Span) return Boolean with Global => null;
   function Quiescent (Data : E.Bytes; Owner : E.Span) return Boolean with Global => null;
   function Quiescent (Data : E.Bytes; Owner : E.View) return Boolean with Global => null;
   function Finalization_Quiescent (Data : E.Bytes; Owner : E.Span) return Boolean with Global => null;
   function Generation_Stable (Data : E.Bytes; Owner : E.Span) return Boolean with Global => null;
   function Finished (Data : E.Bytes; Owner : E.Span) return Boolean with Global => null;
   function Cancellation_Membership (Data : E.Bytes; Capture : E.Span) return Boolean with Global => null;
   function Cancellation_Membership_Valid (Data : E.Bytes; Capture : E.Span) return Boolean with Global => null;
   --  Frozen indices 0..21; timer 22/23 and actual controller truth 24/25 append.
   type Action is
     (Observe_Quiescence, Observe_Finished, Drain_Tails, Close_Streams,
      Release_Guard, Stop_Launcher, Observe_Manager, Observe_Proxy,
      Observe_Command, Observe_Streams_Closed, Observe_Guard_Released,
      Observe_Cancellation_Complete, Query_Publication, Recover_Run,
      Start_Run, Mark_World_Dead, Mark_Job_Dead, Forget_Owner, Run_Stopped,
      Observe_Membership, Capture_Membership_Protocol, Route_Controller,
      Activate_Timer, Capture_Timer_Protocol,
      Stop_Controller, Capture_Controller_Stop_Protocol);
   function Allowed (Data : E.Bytes; Owner : E.Span; Requested : Action)
      return Boolean with Global => null;
end Worldline.Runner_Lifecycle;
