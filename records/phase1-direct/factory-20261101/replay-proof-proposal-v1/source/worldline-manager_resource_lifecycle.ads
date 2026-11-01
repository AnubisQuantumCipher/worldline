-- Pure policy over captured original manager/launcher/restart facts.
package Worldline.Manager_Resource_Lifecycle with SPARK_Mode is
   function Unit_Valid (Unit : String) return Boolean with Global => null;
   function Identity_Valid (Unit, Invocation, Group : String) return Boolean
     with Global => null;
   function Events_State (Events : String) return Natural
     with Global => null, Post => Events_State'Result <= 2;
   -- Events_State: 0 malformed; 1 populated/unknown; 2 exactly populated=0.
   -- Decide returns JSON containing native action/state/reason/value/live.
   -- Actions request only the next factual I/O; no supplied success flag grants
   -- terminal authority. Invalid/unknown observations retain accounting.
   function Decide (Capture : String) return String with Global => null,
     Subprogram_Variant => (Decreases => Capture'Length);
end Worldline.Manager_Resource_Lifecycle;
