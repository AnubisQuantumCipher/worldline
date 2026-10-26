with Worldline.Resources;
with Worldline.Producer_Values;
with Worldline.Manager_Resource_Lifecycle;

package body Worldline.Ordinary_Reservation_Replay with SPARK_Mode is
   use Worldline.Producer_Values;
   use type Interfaces.Unsigned_32;
   use type Worldline.Resources.Byte;
   subtype Code_Kind is Interfaces.Unsigned_32 range 0 .. 2;
   subtype Selection_Kind is Worldline.Resources.Byte range 0 .. 2;
   subtype Mask_Array is Worldline.Ordinary_Reservation_Lifecycle.Mask_Array;
   type Row_Result is record
      Valid : Boolean := False;
      Selection : Selection_Kind := 0;
   end record;

   function Boolean_Field (Data : String; Parent : Node; Name : String)
      return Boolean is (Field (Data, Parent, Name).Form = Boolean_Value)
   with Global => null;

   function Flag (Data : String; Parent : Node; Name : String) return Boolean is
     (Is_True (Data, Field (Data, Parent, Name))) with Global => null;

   function Equality_Operation (Op : String) return Boolean is
     (Op = "attach-unit" or else Op = "identity-match" or else
      Op = "identity-update") with Global => null;

   function Row_Operation (Op : String) return Boolean is
     (Op = "release" or else Op = "reconcile" or else Equality_Operation (Op))
   with Global => null;

   function Builtin_Ready (Data : String; Rows : Node; Length : Natural)
      return Boolean with Global => null
   is
   begin
      for K in 1 .. Length loop
         declare
            Row : constant Node := Element (Data, Rows, K);
            Identity : constant Node := Field (Data, Row, "left");
         begin
            if not Boolean_Field (Data, Row, "builtinString") or else
              not Flag (Data, Row, "builtinString") or else
              Field (Data, Identity, "utf8SurrogatepassHex").Form /= String_Value
            then return False; end if;
         end;
      end loop;
      return True;
   end Builtin_Ready;

   function Unique_Ready (Data : String; Rows : Node; Length : Natural)
      return Boolean with Global => null
   is
   begin
      --  One original pairwise pass. Missing/nonstring payloads remain ignored;
      --  Equal retains decoded JSON-string equality, not raw spelling equality.
      for K in 1 .. Length loop
         for J in 1 .. K - 1 loop
            declare
               L : constant Node := Field (Data, Element (Data, Rows, K), "left");
               R : constant Node := Field (Data, Element (Data, Rows, J), "left");
               LH : constant Node := Field (Data, L, "utf8SurrogatepassHex");
               RH : constant Node := Field (Data, R, "utf8SurrogatepassHex");
            begin
               if LH.Form = String_Value and then RH.Form = String_Value and then
                 Equal (Data, LH, Data, RH) then return False; end if;
            end;
         end loop;
      end loop;
      return True;
   end Unique_Ready;

   function Capture_Ready
     (Data : String; Root, Rows : Node; Length : Natural) return Boolean
   with Global => null
   is
   begin
      if Root.Form /= Object_Value or else
        not Is_Text (Data, Field (Data, Root, "schema"),
                     "worldline.ordinary-reservation-v1") or else
        not Is_Text (Data, Field (Data, Root, "profile"),
                     "python-actual-protocol-v1") or else
        Rows.Form /= Array_Value or else Count (Data, Rows) /= Length
      then return False; end if;
      if Flag (Data, Root, "requireBuiltinStrings") and then
        not Builtin_Ready (Data, Rows, Length) then return False; end if;
      if Flag (Data, Root, "requireUnique") and then
        not Unique_Ready (Data, Rows, Length) then return False; end if;
      return True;
   end Capture_Ready;

   function Guard_Settled (Data : String; Root : Node) return Code_Kind
   with Global => null
   is
      Unit : constant Node := Field (Data, Root, "unitObservation");
      Status : constant Node := Field (Data, Root, "codeObservation");
   begin
      if not Boolean_Field (Data, Unit, "eq") or else
        not Boolean_Field (Data, Status, "eq") or else
        Field (Data, Root, "originalState").Form /= Object_Value or else
        not Boolean_Field (Data, Root, "stateMember") then return 0; end if;
      if not Flag (Data, Unit, "eq") or else not Flag (Data, Status, "eq") or else
        not Flag (Data, Root, "stateMember") then return 1; end if;
      declare
         Raw : constant Node := Field (Data, Root, "managerCapture");
      begin
         if Raw.Form = Null_Value then return 2;
         elsif Raw.Form /= Object_Value then return 0;
         end if;
         declare
            Result : constant String :=
              Worldline.Manager_Resource_Lifecycle.Decide (Slice (Data, Raw));
         begin
            return (if Is_True (Result, Field (Result, Parse (Result), "accepted"))
                    then 2 else 1);
         end;
      end;
   end Guard_Settled;

   function Control_Code (Data : String; Root : Node; Op : String)
      return Code_Kind with Global => null
   is
   begin
      if Op = "gate" or else Op = "probe" then
         if not Boolean_Field (Data, Root, "observation") then return 0; end if;
         return (if Flag (Data, Root, "observation") then 2 else 1);
      elsif Op = "failure" then
         return (if Field (Data, Root, "beforeOriginal").Form = Object_Value and then
                    Field (Data, Root, "afterOriginal").Form = Object_Value and then
                    Field (Data, Root, "resultOriginal").Form = Object_Value
                 then 2 else 0);
      elsif Op = "guard-release" then
         if not Boolean_Field (Data, Root, "decisionPresent") or else
           not Boolean_Field (Data, Root, "deferred") then return 0; end if;
         return (if Flag (Data, Root, "decisionPresent") and then
                    not Flag (Data, Root, "deferred") then 2 else 1);
      elsif Op = "identity-unit" then
         declare Observed : constant Node := Field (Data, Root, "unitObservation");
         begin
            if not Boolean_Field (Data, Observed, "ne") then return 0; end if;
            return (if Flag (Data, Observed, "ne") then 1 else 2);
         end;
      elsif Op = "guard-settled" then return Guard_Settled (Data, Root);
      else return 0;
      end if;
   end Control_Code;

   function Equality_Row (Data : String; Row : Node; Op : String)
      return Row_Result with Global => null
   is
   begin
      if not Boolean_Field (Data, Row, "eq") then return (False, 0); end if;
      if not Flag (Data, Row, "eq") then
         return (Op /= "attach-unit" or else
                   Field (Data, Row, "unitEq").Form = Null_Value, 0);
      end if;
      if Op /= "attach-unit" then return (True, 1); end if;
      --  Matching attach writes selection/position BEFORE validating unitEq.
      if not Boolean_Field (Data, Row, "unitEq") then return (False, 1); end if;
      return (True, (if Flag (Data, Row, "unitEq") then 2 else 1));
   end Equality_Row;

   function Inspect_Row (Data : String; Row : Node; Op : String)
      return Row_Result with Global => null
   is
   begin
      if Row.Form /= Object_Value then return (False, 0); end if;
      if Op /= "reconcile" and then
        (Field (Data, Row, "left").Form /= Object_Value or else
         Field (Data, Row, "right").Form /= Object_Value or else
         Field (Data, Row, "operatorResult").Form /= Object_Value)
      then return (False, 0); end if;
      if Op = "release" then
         if not Boolean_Field (Data, Row, "ne") then return (False, 0); end if;
         return (True, (if Is_False (Data, Field (Data, Row, "ne")) then 1 else 0));
      elsif Op = "reconcile" then
         if not Boolean_Field (Data, Row, "literalFalse") or else
           Field (Data, Row, "original").Form /= Object_Value
         then return (False, 0); end if;
         return (True, (if Flag (Data, Row, "literalFalse") then 1 else 0));
      elsif Equality_Operation (Op) then return Equality_Row (Data, Row, Op);
      else return (False, 0);
      end if;
   end Inspect_Row;

   function Zero_Result (Mask : Mask_Array; Code, Expected : Interfaces.Unsigned_32;
                         Position : Natural) return Boolean with Global => null
   is
      Same : Boolean := Code = Expected and then Position = 0;
   begin
      for I in Mask'Range loop
         if Mask (I) /= 0 then Same := False; end if;
      end loop;
      return Same;
   end Zero_Result;

   function Replay_Rows
     (Data : String; Rows : Node; Op : String; Mask : Mask_Array;
      Code : Interfaces.Unsigned_32; Position : Natural) return Boolean
   with Global => null
   is
      Failed : Boolean := False;
      Same : Boolean := True;
      Matches, Last_Match : Natural := 0;
      Expected_Code : Code_Kind := 0;
   begin
      for K in 1 .. Mask'Length loop
         pragma Loop_Invariant (Matches <= K - 1);
         pragma Loop_Invariant (Last_Match <= K - 1);
         declare
            Expected : Selection_Kind := 0;
         begin
            if not Failed then
               declare
                  Result : constant Row_Result :=
                    Inspect_Row (Data, Element (Data, Rows, K), Op);
               begin
                  Expected := Result.Selection;
                  if Expected /= 0 then
                     Matches := Matches + 1;
                     if Equality_Operation (Op) then Last_Match := K; end if;
                  end if;
                  Failed := not Result.Valid;
               end;
            end if;
            if Mask (Mask'First + (K - 1)) /= Expected then Same := False; end if;
         end;
      end loop;
      if not Failed then
         if Op = "identity-match" then
            Expected_Code := (if Matches = 1 then 2 else 1);
            if Matches /= 1 then Last_Match := 0; end if;
         else
            Expected_Code := (if Matches > 0 then 2 else 1);
            Last_Match := 0;
         end if;
      end if;
      return Same and then Code = Expected_Code and then Position = Last_Match;
   end Replay_Rows;

   function Conforms
     (Data : String; Mask : Mask_Array;
      Code : Interfaces.Unsigned_32; Position : Natural) return Boolean
   is
      Root : constant Node := Parse (Data);
      Rows : constant Node := Field (Data, Root, "rows");
      Op : constant String := Text (Data, Field (Data, Root, "operation"));
   begin
      if Code > 2 or else Position > Mask'Length then return False; end if;
      if not Capture_Ready (Data, Root, Rows, Mask'Length) then
         return Zero_Result (Mask, Code, 0, Position);
      elsif not Row_Operation (Op) then
         return Zero_Result (Mask, Code, Control_Code (Data, Root, Op), Position);
      else
         return Replay_Rows (Data, Rows, Op, Mask, Code, Position);
      end if;
   end Conforms;
end Worldline.Ordinary_Reservation_Replay;
