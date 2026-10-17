package body Worldline.Generic_JSON_Syntax with SPARK_Mode is
   function Source_Length
     (Data : Source_Data; Context : Source_Context) return Count is
     (Source_Length_Impl (Data, Context));

   function Read_Unit
     (Data : Source_Data; Context : Source_Context; Position : Count)
      return Reader_Unit is
     (Read_Unit_Impl (Data, Context, Position));

   -- Outside string content, every recognized syntax character is ASCII.
   -- NUL cannot match any punctuation, whitespace, digit, or literal prefix.
   function Peek
     (Data : Source_Data; Context : Source_Context; Position : Count)
      return Character is
     (if Read_Unit (Data, Context, Position).Kind = ASCII_Unit then
         Read_Unit (Data, Context, Position).Value
      else Character'Val (0));

   procedure Advance
     (Data : Source_Data; Context : Source_Context; Position : in out Count)
   with Global => null,
     Post => Position = Read_Unit (Data, Context, Position'Old).Next_Offset and then
       Position >= Position'Old and then
       (if Position'Old <= Source_Length (Data, Context) then
           Position <= Source_Length (Data, Context)
        else Position = Position'Old)
   is
   begin
      Position := Read_Unit (Data, Context, Position).Next_Offset;
   end Advance;

   function Is_Hex (Value : Character) return Boolean is
     (Value in '0' .. '9' | 'a' .. 'f' | 'A' .. 'F');

   type Token_Match is record
      Matched : Boolean := False;
      After : Count := 0;
   end record;

   function Match_Token
     (Data : Source_Data; Context : Source_Context; Position : Count;
      Token : String) return Token_Match
   with Global => null,
     Post =>
       (if Match_Token'Result.Matched then
           Match_Token'Result.After >= Position and then
           Match_Token'Result.After <= Source_Length (Data, Context) and then
           (if Token'Length > 0 then Match_Token'Result.After > Position)
        else Match_Token'Result.After = Position)
   is
      Next : Count := Position;
   begin
      if Position > Source_Length (Data, Context) then return (False, Position); end if;
      for I in Token'Range loop
         pragma Loop_Invariant (Next >= Position);
         pragma Loop_Invariant (Next <= Source_Length (Data, Context));
         pragma Loop_Invariant (if I > Token'First then Next > Position);
         declare Unit : constant Reader_Unit := Read_Unit (Data, Context, Next); begin
            if Unit.Kind /= ASCII_Unit or else Unit.Value /= Token (I) then
               return (False, Position);
            end if;
            Next := Unit.Next_Offset;
         end;
      end loop;
      return (True, Next);
   end Match_Token;

   procedure Space
     (Data : Source_Data; Context : Source_Context; Position : in out Count)
   is
   begin
      while Position < Source_Length (Data, Context) and then
        Peek (Data, Context, Position) in
          ' ' | Character'Val (9) | Character'Val (10) | Character'Val (13)
      loop
         pragma Loop_Invariant (Position >= Position'Loop_Entry);
         pragma Loop_Invariant (Position <= Source_Length (Data, Context));
         pragma Loop_Variant (Decreases => Source_Length (Data, Context) - Position);
         Advance (Data, Context, Position);
      end loop;
   end Space;

   procedure Scan_String
     (Data : Source_Data; Context : Source_Context;
      Position : in out Count; Valid : out Boolean)
   is
   begin
      Valid := False;
      if Peek (Data, Context, Position) /= '"' then return; end if;
      Advance (Data, Context, Position);
      while Position < Source_Length (Data, Context) loop
         pragma Loop_Invariant (Position >= Position'Loop_Entry);
         pragma Loop_Invariant (Position <= Source_Length (Data, Context));
         pragma Loop_Variant (Decreases => Source_Length (Data, Context) - Position);
         declare Unit : constant Reader_Unit := Read_Unit (Data, Context, Position); begin
            if Unit.Kind not in ASCII_Unit | Non_ASCII_Unit then return;
            elsif Unit.Kind = ASCII_Unit and then Unit.Value = '"' then
               Position := Unit.Next_Offset;
               Valid := True;
               return;
            elsif Unit.Kind = ASCII_Unit and then Character'Pos (Unit.Value) < 32 then
               return;
            elsif Unit.Kind = ASCII_Unit and then Unit.Value = '\' then
               Position := Unit.Next_Offset;
               if Position >= Source_Length (Data, Context) then return; end if;
               if Peek (Data, Context, Position) = 'u' then
                  -- Keep Position at 'u' until every required hex digit is
                  -- present. This preserves the old scanner's failure offset.
                  declare Next : Count := Position; begin
                     Advance (Data, Context, Next);
                     for I in 1 .. 4 loop
                        pragma Loop_Invariant (Next > Position);
                        pragma Loop_Invariant (Next <= Source_Length (Data, Context));
                        if not Is_Hex (Peek (Data, Context, Next)) then return; end if;
                        Advance (Data, Context, Next);
                     end loop;
                     Position := Next;
                  end;
               elsif Peek (Data, Context, Position) in
                 '"' | '\' | '/' | 'b' | 'f' | 'n' | 'r' | 't'
               then
                  Advance (Data, Context, Position);
               else return;
               end if;
            else
               Position := Unit.Next_Offset;
            end if;
         end;
      end loop;
   end Scan_String;

   function Scan
     (Data : Source_Data; Context : Source_Context;
      Initial_Position : Count) return Scan_Result
   is
      Position : Count := Initial_Position;
      Item : Node;
      Start : Count;
      Form : Value_Kind range Null_Value .. Object_Value;
      Valid : Boolean;
      Open, Close : Character;
   begin
      Item := No_Node;
      Space (Data, Context, Position);
      if Position >= Source_Length (Data, Context) then return (Position, Item); end if;
      Start := Position;
      for Choice in 1 .. 3 loop
         pragma Loop_Invariant (Position = Start);
         declare
            Token : constant String :=
              (if Choice = 1 then "NaN" elsif Choice = 2 then "Infinity" else "-Infinity");
            Match : constant Token_Match := Match_Token (Data, Context, Position, Token);
         begin
            if Match.Matched then
               Position := Match.After;
               Item := (Number_Value, Start, Position);
               return (Position, Item);
            end if;
         end;
      end loop;
      case Peek (Data, Context, Position) is
         when '"' =>
            Scan_String (Data, Context, Position, Valid);
            if not Valid then return (Position, Item); end if;
            Form := String_Value;
         when '{' | '[' =>
            Open := Peek (Data, Context, Position);
            Close := (if Open = '{' then '}' else ']');
            Form := (if Open = '{' then Object_Value else Array_Value);
            Advance (Data, Context, Position);
            Space (Data, Context, Position);
            if Peek (Data, Context, Position) /= Close then
               loop
                  pragma Loop_Invariant (Position > Start);
                  pragma Loop_Invariant (Position <= Source_Length (Data, Context));
                  pragma Loop_Variant (Decreases => Source_Length (Data, Context) - Position);
                  if Open = '{' then
                     declare
                        Key : constant Scan_Result := Scan (Data, Context, Position);
                     begin
                        Position := Key.Position;
                        if Key.Item.Form /= String_Value then return (Position, Item); end if;
                     end;
                     Space (Data, Context, Position);
                     if Peek (Data, Context, Position) /= ':' then return (Position, Item); end if;
                     Advance (Data, Context, Position);
                  end if;
                  declare
                     Child : constant Scan_Result := Scan (Data, Context, Position);
                  begin
                     Position := Child.Position;
                     if Child.Item.Form = Missing then return (Position, Item); end if;
                  end;
                  Space (Data, Context, Position);
                  exit when Peek (Data, Context, Position) = Close;
                  if Peek (Data, Context, Position) /= ',' then return (Position, Item); end if;
                  Advance (Data, Context, Position);
                  Space (Data, Context, Position);
               end loop;
            end if;
            if Position >= Source_Length (Data, Context) or else
              Peek (Data, Context, Position) /= Close then return (Position, Item); end if;
            Advance (Data, Context, Position);
         when 'n' | 't' | 'f' =>
            declare
               Literal : constant String :=
                 (if Peek (Data, Context, Position) = 'n' then "null"
                  elsif Peek (Data, Context, Position) = 't' then "true" else "false");
               Match : constant Token_Match := Match_Token (Data, Context, Position, Literal);
            begin
               if not Match.Matched then return (Position, Item); end if;
               Position := Match.After;
               Form := (if Literal = "null" then Null_Value else Boolean_Value);
            end;
         when '-' | '0' .. '9' =>
            Form := Integer_Value;
            if Peek (Data, Context, Position) = '-' then
               Advance (Data, Context, Position);
               if Position >= Source_Length (Data, Context) then return (Position, Item); end if;
            end if;
            if Peek (Data, Context, Position) = '0' then Advance (Data, Context, Position);
            elsif Peek (Data, Context, Position) in '1' .. '9' then
               while Position < Source_Length (Data, Context) and then
                 Peek (Data, Context, Position) in '0' .. '9'
               loop
                  pragma Loop_Invariant (Position >= Position'Loop_Entry);
                  pragma Loop_Invariant (Position <= Source_Length (Data, Context));
                  pragma Loop_Variant (Decreases => Source_Length (Data, Context) - Position);
                  Advance (Data, Context, Position);
               end loop;
            else return (Position, Item);
            end if;
            if Peek (Data, Context, Position) = '.' then
               Form := Number_Value;
               Advance (Data, Context, Position);
               if Position >= Source_Length (Data, Context) or else
                 Peek (Data, Context, Position) not in '0' .. '9' then return (Position, Item); end if;
               while Position < Source_Length (Data, Context) and then
                 Peek (Data, Context, Position) in '0' .. '9'
               loop
                  pragma Loop_Invariant (Position >= Position'Loop_Entry);
                  pragma Loop_Invariant (Position <= Source_Length (Data, Context));
                  pragma Loop_Variant (Decreases => Source_Length (Data, Context) - Position);
                  Advance (Data, Context, Position);
               end loop;
            end if;
            if Peek (Data, Context, Position) in 'e' | 'E' then
               Form := Number_Value;
               Advance (Data, Context, Position);
               if Peek (Data, Context, Position) in '+' | '-' then Advance (Data, Context, Position); end if;
               if Position >= Source_Length (Data, Context) or else
                 Peek (Data, Context, Position) not in '0' .. '9' then return (Position, Item); end if;
               while Position < Source_Length (Data, Context) and then
                 Peek (Data, Context, Position) in '0' .. '9'
               loop
                  pragma Loop_Invariant (Position >= Position'Loop_Entry);
                  pragma Loop_Invariant (Position <= Source_Length (Data, Context));
                  pragma Loop_Variant (Decreases => Source_Length (Data, Context) - Position);
                  Advance (Data, Context, Position);
               end loop;
            end if;
         when others => return (Position, Item);
      end case;
      if Position > Start then
         -- Static discriminants keep the missing/present variant explicit.
         case Form is
            when Null_Value => Item := (Null_Value, Start, Position);
            when Boolean_Value => Item := (Boolean_Value, Start, Position);
            when Integer_Value => Item := (Integer_Value, Start, Position);
            when Number_Value => Item := (Number_Value, Start, Position);
            when String_Value => Item := (String_Value, Start, Position);
            when Array_Value => Item := (Array_Value, Start, Position);
            when Object_Value => Item := (Object_Value, Start, Position);
         end case;
      end if;
      return (Position, Item);
   end Scan;

   function Parse
     (Data : Source_Data; Context : Source_Context; Start : Count := 0)
      return Node
   is
      Result : constant Scan_Result := Scan (Data, Context, Start);
      Position : Count := Result.Position;
   begin
      Space (Data, Context, Position);
      if Position = Source_Length (Data, Context) and then
        Read_Unit (Data, Context, Position).Kind = End_Of_Source
      then return Result.Item;
      else return No_Node;
      end if;
   end Parse;
end Worldline.Generic_JSON_Syntax;
