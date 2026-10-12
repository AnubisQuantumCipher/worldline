with Worldline.Producer_Values;
with Worldline.Manager_Resource_Lifecycle;
with Resource_Reservation_Lifecycle;
package body Worldline.Ordinary_Reservation_Lifecycle with SPARK_Mode is
   use Worldline.Producer_Values;
   use type Interfaces.Unsigned_32;
   use type Worldline.Resources.Byte;
   package Existing renames Resource_Reservation_Lifecycle;
   function Reconciled_Gone (Observed_False : Boolean) return Boolean is
     (Existing.Remove_Row
       (Data => (1 .. 0 => 0),
        Row => (Identity => (First => 1, Length => 0),
                Observed => (if Observed_False then Existing.Gone else Existing.Unknown)),
        Requested => (Present => False), Mode => Existing.Reconcile_Observed));
   procedure Plan (Data : String; Mask : out Mask_Array;
                   Code : out Interfaces.Unsigned_32; Position : out Natural)
   is
      Root : constant Node := Parse (Data);
      Rows : constant Node := Field (Data, Root, "rows");
      Op : constant String := Text (Data, Field (Data, Root, "operation"));
      Matches : Natural := 0;
      function B (Name : String) return Boolean is
        (Is_True (Data, Field (Data, Root, Name)));
      function Bool_Field (Parent : Node; Name : String) return Boolean is
        (Field (Data, Parent, Name).Form = Boolean_Value);
   begin
      Mask := (others => 0); Code := 0; Position := 0;
      if Root.Form /= Object_Value or else
        not Is_Text (Data, Field (Data, Root, "schema"), "worldline.ordinary-reservation-v1") or else
        not Is_Text (Data, Field (Data, Root, "profile"), "python-actual-protocol-v1") or else
        Rows.Form /= Array_Value or else Count (Data, Rows) /= Mask'Length
      then return; end if;
      if B ("requireBuiltinStrings") then
         for K in 1 .. Mask'Length loop
            declare
               Row : constant Node := Element (Data, Rows, K);
               Identity : constant Node := Field (Data, Row, "left");
            begin
               if not Bool_Field (Row, "builtinString") or else
                 not Is_True (Data, Field (Data, Row, "builtinString")) or else
                 Field (Data, Identity, "utf8SurrogatepassHex").Form /= String_Value
               then return; end if;
            end;
         end loop;
      end if;
      if B ("requireUnique") then
         for K in 1 .. Mask'Length loop
            for J in 1 .. K - 1 loop
               declare
                  L : constant Node := Field (Data, Element (Data, Rows, K), "left");
                  R : constant Node := Field (Data, Element (Data, Rows, J), "left");
                  LH : constant Node := Field (Data, L, "utf8SurrogatepassHex");
                  RH : constant Node := Field (Data, R, "utf8SurrogatepassHex");
               begin
                  if LH.Form = String_Value and then RH.Form = String_Value
                    and then Equal (Data, LH, Data, RH)
                  then return; end if;
               end;
            end loop;
         end loop;
      end if;
      if Op = "gate" or else Op = "probe" then
         if not Bool_Field (Root, "observation") then return; end if;
         Code := (if B ("observation") then 2 else 1); return;
      elsif Op = "failure" then
         if Field (Data, Root, "beforeOriginal").Form /= Object_Value or else
           Field (Data, Root, "afterOriginal").Form /= Object_Value or else
           Field (Data, Root, "resultOriginal").Form /= Object_Value
         then return; end if;
         -- Actual __ior__/reflected __or__ completion, not Boolean coercion.
         -- Retain its original value for the manager's independently captured
         -- truth protocol. Python does not decide whether completion releases.
         Code := 2; return;
      elsif Op = "guard-release" then
         if not Bool_Field (Root, "decisionPresent") or else not Bool_Field (Root, "deferred") then return; end if;
         Code := (if B ("decisionPresent") and then not B ("deferred") then 2 else 1); return;
      elsif Op = "guard-settled" then
         if not Bool_Field (Field (Data, Root, "unitObservation"), "eq") or else
           not Bool_Field (Field (Data, Root, "codeObservation"), "eq") or else
           Field (Data, Root, "originalState").Form /= Object_Value or else
           not Bool_Field (Root, "stateMember") then return; end if;
         Code := 1;
         if not Is_True (Data, Field (Data, Field (Data, Root, "unitObservation"), "eq")) or else
           not Is_True (Data, Field (Data, Field (Data, Root, "codeObservation"), "eq")) or else
           not B ("stateMember") then return; end if;
         declare
            Raw : constant Node := Field (Data, Root, "managerCapture");
         begin
            if Raw.Form = Null_Value then Code := 2;
            elsif Raw.Form = Object_Value then
               declare
                  Result : constant String := Worldline.Manager_Resource_Lifecycle.Decide (Slice (Data, Raw));
               begin
                  if Is_True (Result, Field (Result, Parse (Result), "accepted")) then Code := 2; end if;
               end;
            else Code := 0;
            end if;
         end;
         return;
      elsif Op = "identity-unit" then
         declare
            Observed : constant Node := Field (Data, Root, "unitObservation");
         begin
            if not Bool_Field (Observed, "ne") then return; end if;
            Code := (if Is_True (Data, Field (Data, Observed, "ne")) then 1 else 2);
         end;
         return;
      elsif Op /= "release" and then Op /= "attach-unit" and then Op /= "identity-match"
        and then Op /= "identity-update" and then Op /= "reconcile"
      then return;
      end if;
      -- Ordered, complete protocol observations. __ne__ is NOT replaced by
      -- negated __eq__. Stateful equality is captured again for identity-update.
      for K in 1 .. Mask'Length loop
         pragma Loop_Invariant (Matches <= K - 1);
         pragma Loop_Invariant (Position <= Mask'Length);
         declare
            Row : constant Node := Element (Data, Rows, K);
            I : constant Positive := Mask'First + (K - 1);
         begin
            if Row.Form /= Object_Value then Code := 0; return; end if;
            if Op /= "reconcile" and then
              (Field (Data, Row, "left").Form /= Object_Value or else
               Field (Data, Row, "right").Form /= Object_Value or else
               Field (Data, Row, "operatorResult").Form /= Object_Value)
            then Code := 0; return; end if;
            if Op = "release" then
               if not Bool_Field (Row, "ne") then Code := 0; return; end if;
               if Is_False (Data, Field (Data, Row, "ne")) then Mask (I) := 1; Matches := Matches + 1; end if;
            elsif Op = "reconcile" then
               if not Bool_Field (Row, "literalFalse") or else
                 Field (Data, Row, "original").Form /= Object_Value
               then Code := 0; return; end if;
               if Reconciled_Gone (Is_True (Data, Field (Data, Row, "literalFalse"))) then
                  Mask (I) := 1; Matches := Matches + 1;
               end if;
            else
               if not Bool_Field (Row, "eq") then Code := 0; return; end if;
               if Is_True (Data, Field (Data, Row, "eq")) then
                  Mask (I) := 1; Matches := Matches + 1; Position := K;
                  if Op = "attach-unit" then
                     if not Bool_Field (Row, "unitEq") then Code := 0; return; end if;
                     if Is_True (Data, Field (Data, Row, "unitEq")) then Mask (I) := 2; end if;
                  end if;
               elsif Op = "attach-unit" and then Field (Data, Row, "unitEq").Form /= Null_Value then
                  Code := 0; return;
               end if;
            end if;
         end;
      end loop;
      if Op = "identity-match" then
         Code := (if Matches = 1 then 2 else 1);
         if Matches /= 1 then Position := 0; end if;
      else
         Code := (if Matches > 0 then 2 else 1); Position := 0;
      end if;
   end Plan;
end Worldline.Ordinary_Reservation_Lifecycle;
