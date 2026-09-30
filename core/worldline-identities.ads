with Interfaces;

--  Distinct identity domains, each with explicit presence (1.9.0).
--
--  An identity the runtime could not establish is Absent, never a zero digest
--  or a sentinel, and two absent values are never the same: Same is True only
--  when both sides are present and equal. Each domain is its own type, so a
--  parent content identity cannot be compared with a state root, and a field
--  swapped between domains does not compile.
--
--  A present value is never all zero bytes; that is enforced where values
--  enter the kernel (Worldline.Collapse_Wire), not here, so these types stay
--  cheap to prove.
package Worldline.Identities with SPARK_Mode is
   use type Interfaces.Unsigned_64;

   type Content_Id is new Hash;        --  world content identity (parent, checkpoint)
   type Subject_Id is new Hash;        --  the world an evaluation speaks for
   type State_Root is new Hash;        --  root-set hash of captured manifests
   type Content_Root is new Hash;      --  content-only root of what was examined
   type Delta_Id is new Hash;          --  a world's delta identity
   type Root_Set_Id is new Hash;       --  the registered root set
   type Requirement_Id is new Hash;    --  a requirement (policy + verifiers) hash
   type Verifier_Set_Id is new Hash;   --  a verifier bundle roster identity
   type Watch_Set_Id is new Hash;      --  the set of roots under watch
   subtype Generation is Interfaces.Unsigned_64;

   type Optional_Content_Id is record
      Present : Boolean := False;
      Value   : Content_Id := [others => 0];
   end record;
   function Same (L, R : Optional_Content_Id) return Boolean is
     (L.Present and then R.Present and then L.Value = R.Value)
     with Global => null;

   type Optional_Subject_Id is record
      Present : Boolean := False;
      Value   : Subject_Id := [others => 0];
   end record;
   function Same (L, R : Optional_Subject_Id) return Boolean is
     (L.Present and then R.Present and then L.Value = R.Value)
     with Global => null;

   type Optional_State_Root is record
      Present : Boolean := False;
      Value   : State_Root := [others => 0];
   end record;
   function Same (L, R : Optional_State_Root) return Boolean is
     (L.Present and then R.Present and then L.Value = R.Value)
     with Global => null;

   type Optional_Content_Root is record
      Present : Boolean := False;
      Value   : Content_Root := [others => 0];
   end record;
   function Same (L, R : Optional_Content_Root) return Boolean is
     (L.Present and then R.Present and then L.Value = R.Value)
     with Global => null;

   type Optional_Delta_Id is record
      Present : Boolean := False;
      Value   : Delta_Id := [others => 0];
   end record;
   function Same (L, R : Optional_Delta_Id) return Boolean is
     (L.Present and then R.Present and then L.Value = R.Value)
     with Global => null;

   type Optional_Root_Set_Id is record
      Present : Boolean := False;
      Value   : Root_Set_Id := [others => 0];
   end record;
   function Same (L, R : Optional_Root_Set_Id) return Boolean is
     (L.Present and then R.Present and then L.Value = R.Value)
     with Global => null;

   type Optional_Requirement_Id is record
      Present : Boolean := False;
      Value   : Requirement_Id := [others => 0];
   end record;
   function Same (L, R : Optional_Requirement_Id) return Boolean is
     (L.Present and then R.Present and then L.Value = R.Value)
     with Global => null;

   type Optional_Verifier_Set_Id is record
      Present : Boolean := False;
      Value   : Verifier_Set_Id := [others => 0];
   end record;
   function Same (L, R : Optional_Verifier_Set_Id) return Boolean is
     (L.Present and then R.Present and then L.Value = R.Value)
     with Global => null;

   type Optional_Watch_Set_Id is record
      Present : Boolean := False;
      Value   : Watch_Set_Id := [others => 0];
   end record;
   function Same (L, R : Optional_Watch_Set_Id) return Boolean is
     (L.Present and then R.Present and then L.Value = R.Value)
     with Global => null;

   type Optional_Generation is record
      Present : Boolean := False;
      Value   : Generation := 0;
   end record;
   function Same (L, R : Optional_Generation) return Boolean is
     (L.Present and then R.Present and then L.Value = R.Value)
     with Global => null;

end Worldline.Identities;
