with Ada.Command_Line;
with Ada.Text_IO;
with Raw_Decode_Case;
with System;
with Resource_Quantities;
with Resource_Run_Ledger_Wire;
with Worldline.Retained_Raw_Decode;

procedure Raw_Decode_Tests is
   package Q renames Resource_Quantities;
   package W renames Resource_Run_Ledger_Wire;
   package D renames Worldline.Retained_Raw_Decode;
   use type Q.Byte_Count;
   use type W.U8;
   use type W.I64;
   Width : constant Q.Byte_Count := W.Raw_Id'Size / System.Storage_Unit;

   procedure Case_1 is new Raw_Decode_Case (D.D.Raw_Packet, D.Load, D.Source_Padding_Valid,
      D.D.Raw_Packet'Size / System.Storage_Unit);
   procedure Case_2 is new Raw_Decode_Case (D.N.Raw_Packet, D.Load, D.Source_Padding_Valid,
      D.N.Raw_Packet'Size / System.Storage_Unit);
   procedure Case_3 is new Raw_Decode_Case (D.N.Raw_State, D.Load, D.Source_Padding_Valid,
      D.N.Raw_State'Size / System.Storage_Unit);
   procedure Case_4 is new Raw_Decode_Case (D.W.Raw_Context, D.Load, D.Source_Padding_Valid,
      D.W.Raw_Context'Size / System.Storage_Unit);
   procedure Case_5 is new Raw_Decode_Case (D.W.Raw_Id, D.Load, D.Source_Padding_Valid,
      D.W.Raw_Id'Size / System.Storage_Unit);
   procedure Case_6 is new Raw_Decode_Case (D.W.Raw_Epoch, D.Load, D.Source_Padding_Valid,
      D.W.Raw_Epoch'Size / System.Storage_Unit);
   procedure Case_7 is new Raw_Decode_Case (D.W.Raw_Quantity, D.Load, D.Source_Padding_Valid,
      D.W.Raw_Quantity'Size / System.Storage_Unit);
   procedure Case_8 is new Raw_Decode_Case (D.N.Raw_Current_Observation, D.Load, D.Source_Padding_Valid,
      D.N.Raw_Current_Observation'Size / System.Storage_Unit);
   procedure Case_9 is new Raw_Decode_Case (D.N.Raw_Intent, D.Load, D.Source_Padding_Valid,
      D.N.Raw_Intent'Size / System.Storage_Unit);
   procedure Case_10 is new Raw_Decode_Case (D.W.Raw_Request, D.Load, D.Source_Padding_Valid,
      D.W.Raw_Request'Size / System.Storage_Unit);
   procedure Case_11 is new Raw_Decode_Case (D.W.Raw_Binding, D.Load, D.Source_Padding_Valid,
      D.W.Raw_Binding'Size / System.Storage_Unit);
   procedure Case_12 is new Raw_Decode_Case (D.W.Raw_Row, D.Load, D.Source_Padding_Valid,
      D.W.Raw_Row'Size / System.Storage_Unit);
   procedure Case_13 is new Raw_Decode_Case (D.D.Raw_Observation, D.Load, D.Source_Padding_Valid,
      D.D.Raw_Observation'Size / System.Storage_Unit);
   procedure Case_14 is new Raw_Decode_Case (D.X.Raw_Crosswalk, D.Load, D.Source_Padding_Valid,
      D.X.Raw_Crosswalk'Size / System.Storage_Unit);
   procedure Case_15 is new Raw_Decode_Case (D.C.Raw_Digest, D.Load, D.Source_Padding_Valid,
      D.C.Raw_Digest'Size / System.Storage_Unit);
   procedure Case_16 is new Raw_Decode_Case (D.C.Raw_Hash, D.Load, D.Source_Padding_Valid,
      D.C.Raw_Hash'Size / System.Storage_Unit);
   procedure Case_17 is new Raw_Decode_Case (D.Y.Raw_Input, D.Load, D.Source_Padding_Valid,
      D.Y.Raw_Input'Size / System.Storage_Unit);
   procedure Case_18 is new Raw_Decode_Case (D.Y.Raw_Controller, D.Load, D.Source_Padding_Valid,
      D.Y.Raw_Controller'Size / System.Storage_Unit);
   procedure Case_19 is new Raw_Decode_Case (D.Y.Raw_Process, D.Load, D.Source_Padding_Valid,
      D.Y.Raw_Process'Size / System.Storage_Unit);
   procedure Case_20 is new Raw_Decode_Case (D.Y.Raw_Task, D.Load, D.Source_Padding_Valid,
      D.Y.Raw_Task'Size / System.Storage_Unit);
   procedure Case_21 is new Raw_Decode_Case (D.Y.Raw_Namespace, D.Load, D.Source_Padding_Valid,
      D.Y.Raw_Namespace'Size / System.Storage_Unit);
   procedure Case_22 is new Raw_Decode_Case (D.T.Raw_Input, D.Load, D.Source_Padding_Valid,
      D.T.Raw_Input'Size / System.Storage_Unit);
   procedure Case_23 is new Raw_Decode_Case (D.T.Raw_Binding, D.Load, D.Source_Padding_Valid,
      D.T.Raw_Binding'Size / System.Storage_Unit);
   procedure Case_24 is new Raw_Decode_Case (D.T.Raw_Ids, D.Load, D.Source_Padding_Valid,
      D.T.Raw_Ids'Size / System.Storage_Unit);
   procedure Case_25 is new Raw_Decode_Case (D.T.Raw_UID, D.Load, D.Source_Padding_Valid,
      D.T.Raw_UID'Size / System.Storage_Unit);
   procedure Case_26 is new Raw_Decode_Case (D.T.Raw_Quantity, D.Load, D.Source_Padding_Valid,
      D.T.Raw_Quantity'Size / System.Storage_Unit);
   procedure Case_27 is new Raw_Decode_Case (D.T.Raw_Evidence, D.Load, D.Source_Padding_Valid,
      D.T.Raw_Evidence'Size / System.Storage_Unit);
   procedure Case_28 is new Raw_Decode_Case (D.RW.Raw_Request, D.Load, D.Source_Padding_Valid,
      D.RW.Raw_Request'Size / System.Storage_Unit);
   procedure Case_29 is new Raw_Decode_Case (D.RW.Raw_Binding, D.Load, D.Source_Padding_Valid,
      D.RW.Raw_Binding'Size / System.Storage_Unit);
   procedure Case_30 is new Raw_Decode_Case (D.RW.Raw_Digest, D.Load, D.Source_Padding_Valid,
      D.RW.Raw_Digest'Size / System.Storage_Unit);
   procedure Case_31 is new Raw_Decode_Case (D.RW.Raw_Hash, D.Load, D.Source_Padding_Valid,
      D.RW.Raw_Hash'Size / System.Storage_Unit);
   procedure Case_32 is new Raw_Decode_Case (D.RW.Raw_Epoch, D.Load, D.Source_Padding_Valid,
      D.RW.Raw_Epoch'Size / System.Storage_Unit);
   procedure Case_33 is new Raw_Decode_Case (D.RW.Raw_Native, D.Load, D.Source_Padding_Valid,
      D.RW.Raw_Native'Size / System.Storage_Unit);
   procedure Case_34 is new Raw_Decode_Case (D.T.Raw_Grant, D.Load, D.Source_Padding_Valid,
      D.T.Raw_Grant'Size / System.Storage_Unit);
   procedure Case_35 is new Raw_Decode_Case (D.T.Raw_Rights, D.Load, D.Source_Padding_Valid,
      D.T.Raw_Rights'Size / System.Storage_Unit);
   procedure Case_36 is new Raw_Decode_Case (D.T.Raw_Use, D.Load, D.Source_Padding_Valid,
      D.T.Raw_Use'Size / System.Storage_Unit);
   procedure Case_37 is new Raw_Decode_Case (D.C.Raw_Row, D.Load, D.Source_Padding_Valid,
      D.C.Raw_Row'Size / System.Storage_Unit);
   procedure Case_38 is new Raw_Decode_Case (D.D.Raw_Capability, D.Load, D.Source_Padding_Valid,
      D.D.Raw_Capability'Size / System.Storage_Unit);
   procedure Case_39 is new Raw_Decode_Case (D.N.Raw_Scope_Frame, D.Load, D.Source_Padding_Valid,
      D.N.Raw_Scope_Frame'Size / System.Storage_Unit);
   procedure Case_40 is new Raw_Decode_Case (D.N.Raw_Projection, D.Load, D.Source_Padding_Valid,
      D.N.Raw_Projection'Size / System.Storage_Unit);
   procedure Case_41 is new Raw_Decode_Case (D.N.Raw_Physical_Key, D.Load, D.Source_Padding_Valid,
      D.N.Raw_Physical_Key'Size / System.Storage_Unit);
   procedure Case_42 is new Raw_Decode_Case (D.N.Raw_Bucket, D.Load, D.Source_Padding_Valid,
      D.N.Raw_Bucket'Size / System.Storage_Unit);
   procedure Case_43 is new Raw_Decode_Case (D.W.Raw_Native, D.Load, D.Source_Padding_Valid,
      D.W.Raw_Native'Size / System.Storage_Unit);
   procedure Case_44 is new Raw_Decode_Case (D.O.Raw_Facts, D.Load, D.Source_Padding_Valid,
      D.O.Raw_Facts'Size / System.Storage_Unit);
   procedure Case_45 is new Raw_Decode_Case (D.W.Raw_Result, D.Load, D.Source_Padding_Valid,
      D.W.Raw_Result'Size / System.Storage_Unit);
   procedure Case_46 is new Raw_Decode_Case (D.T.Raw_Result, D.Load, D.Source_Padding_Valid,
      D.T.Raw_Result'Size / System.Storage_Unit);
   procedure Case_47 is new Raw_Decode_Case (D.HC.Raw_Input, D.Load, D.Source_Padding_Valid,
      D.HC.Raw_Input'Size / System.Storage_Unit);
   procedure Case_48 is new Raw_Decode_Case (D.CX.Raw_Input, D.Load, D.Source_Padding_Valid,
      D.CX.Raw_Input'Size / System.Storage_Unit);
   procedure Case_49 is new Raw_Decode_Case (D.CO.Raw_Input, D.Load, D.Source_Padding_Valid,
      D.CO.Raw_Input'Size / System.Storage_Unit);
   procedure Case_50 is new Raw_Decode_Case (D.W.Raw_State, D.Load, D.Source_Padding_Valid,
      D.W.Raw_State'Size / System.Storage_Unit);
   procedure Case_51 is new Raw_Decode_Case (D.CW.Raw_Request, D.Load, D.Source_Padding_Valid,
      D.CW.Raw_Request'Size / System.Storage_Unit);
   procedure Case_52 is new Raw_Decode_Case (D.CW.Raw_Optional_Hash, D.Load, D.Source_Padding_Valid,
      D.CW.Raw_Optional_Hash'Size / System.Storage_Unit);
   procedure Case_53 is new Raw_Decode_Case (D.CW.Raw_Bytes_32, D.Load, D.Source_Padding_Valid,
      D.CW.Raw_Bytes_32'Size / System.Storage_Unit);
   procedure Case_54 is new Raw_Decode_Case (D.CW.Raw_Optional_Counter, D.Load, D.Source_Padding_Valid,
      D.CW.Raw_Optional_Counter'Size / System.Storage_Unit);
   procedure Case_55 is new Raw_Decode_Case (D.CW.Raw_Bytes_8, D.Load, D.Source_Padding_Valid,
      D.CW.Raw_Bytes_8'Size / System.Storage_Unit);
   procedure Case_56 is new Raw_Decode_Case (D.CX.Raw_Material, D.Load, D.Source_Padding_Valid,
      D.CX.Raw_Material'Size / System.Storage_Unit);
   procedure Case_57 is new Raw_Decode_Case (D.HC.Raw_Result, D.Load, D.Source_Padding_Valid,
      D.HC.Raw_Result'Size / System.Storage_Unit);
   procedure Case_58 is new Raw_Decode_Case (D.CX.Raw_Result, D.Load, D.Source_Padding_Valid,
      D.CX.Raw_Result'Size / System.Storage_Unit);

   procedure Check_Id (First : Q.Byte_Index) is
      Data : constant Q.Byte_Array (First .. First + (Width - 1)) := [others => 255];
      Value : constant W.Raw_Id := D.Load (Data);
   begin
      pragma Assert (Value.Present = 255);
      pragma Assert (Value.First = -1 and then Value.Length = -1);
   end Check_Id;
   procedure Group_1 is
   begin
      Case_1;
      Ada.Text_IO.Put_Line ("PASS D.Raw_Packet");
      Case_2;
      Ada.Text_IO.Put_Line ("PASS N.Raw_Packet");
      Case_3;
      Ada.Text_IO.Put_Line ("PASS N.Raw_State");
      Case_4;
      Ada.Text_IO.Put_Line ("PASS W.Raw_Context");
      Case_5;
      Ada.Text_IO.Put_Line ("PASS W.Raw_Id");
      Case_6;
      Ada.Text_IO.Put_Line ("PASS W.Raw_Epoch");
      Case_7;
      Ada.Text_IO.Put_Line ("PASS W.Raw_Quantity");
      Case_8;
      Ada.Text_IO.Put_Line ("PASS N.Raw_Current_Observation");
      Case_9;
      Ada.Text_IO.Put_Line ("PASS N.Raw_Intent");
      Case_10;
      Ada.Text_IO.Put_Line ("PASS W.Raw_Request");
      Case_11;
      Ada.Text_IO.Put_Line ("PASS W.Raw_Binding");
      Case_12;
      Ada.Text_IO.Put_Line ("PASS W.Raw_Row");
      Case_13;
      Ada.Text_IO.Put_Line ("PASS D.Raw_Observation");
      Case_14;
      Ada.Text_IO.Put_Line ("PASS X.Raw_Crosswalk");
      Case_15;
      Ada.Text_IO.Put_Line ("PASS C.Raw_Digest");
      Case_16;
      Ada.Text_IO.Put_Line ("PASS C.Raw_Hash");
      Case_17;
      Ada.Text_IO.Put_Line ("PASS Y.Raw_Input");
      Case_18;
      Ada.Text_IO.Put_Line ("PASS Y.Raw_Controller");
      Case_19;
      Ada.Text_IO.Put_Line ("PASS Y.Raw_Process");
      Case_20;
      Ada.Text_IO.Put_Line ("PASS Y.Raw_Task");
   end Group_1;
   procedure Group_2 is
   begin
      Case_21;
      Ada.Text_IO.Put_Line ("PASS Y.Raw_Namespace");
      Case_22;
      Ada.Text_IO.Put_Line ("PASS T.Raw_Input");
      Case_23;
      Ada.Text_IO.Put_Line ("PASS T.Raw_Binding");
      Case_24;
      Ada.Text_IO.Put_Line ("PASS T.Raw_Ids");
      Case_25;
      Ada.Text_IO.Put_Line ("PASS T.Raw_UID");
      Case_26;
      Ada.Text_IO.Put_Line ("PASS T.Raw_Quantity");
      Case_27;
      Ada.Text_IO.Put_Line ("PASS T.Raw_Evidence");
      Case_28;
      Ada.Text_IO.Put_Line ("PASS RW.Raw_Request");
      Case_29;
      Ada.Text_IO.Put_Line ("PASS RW.Raw_Binding");
      Case_30;
      Ada.Text_IO.Put_Line ("PASS RW.Raw_Digest");
      Case_31;
      Ada.Text_IO.Put_Line ("PASS RW.Raw_Hash");
      Case_32;
      Ada.Text_IO.Put_Line ("PASS RW.Raw_Epoch");
      Case_33;
      Ada.Text_IO.Put_Line ("PASS RW.Raw_Native");
      Case_34;
      Ada.Text_IO.Put_Line ("PASS T.Raw_Grant");
      Case_35;
      Ada.Text_IO.Put_Line ("PASS T.Raw_Rights");
      Case_36;
      Ada.Text_IO.Put_Line ("PASS T.Raw_Use");
      Case_37;
      Ada.Text_IO.Put_Line ("PASS C.Raw_Row");
      Case_38;
      Ada.Text_IO.Put_Line ("PASS D.Raw_Capability");
      Case_39;
      Ada.Text_IO.Put_Line ("PASS N.Raw_Scope_Frame");
      Case_40;
      Ada.Text_IO.Put_Line ("PASS N.Raw_Projection");
   end Group_2;
   procedure Group_3 is
   begin
      Case_41;
      Ada.Text_IO.Put_Line ("PASS N.Raw_Physical_Key");
      Case_42;
      Ada.Text_IO.Put_Line ("PASS N.Raw_Bucket");
      Case_43;
      Ada.Text_IO.Put_Line ("PASS W.Raw_Native");
      Case_44;
      Ada.Text_IO.Put_Line ("PASS O.Raw_Facts");
      Case_45;
      Ada.Text_IO.Put_Line ("PASS W.Raw_Result");
      Case_46;
      Ada.Text_IO.Put_Line ("PASS T.Raw_Result");
      Case_47;
      Ada.Text_IO.Put_Line ("PASS HC.Raw_Input");
      Case_48;
      Ada.Text_IO.Put_Line ("PASS CX.Raw_Input");
      Case_49;
      Ada.Text_IO.Put_Line ("PASS CO.Raw_Input");
      Case_50;
      Ada.Text_IO.Put_Line ("PASS W.Raw_State");
      Case_51;
      Ada.Text_IO.Put_Line ("PASS CW.Raw_Request");
      Case_52;
      Ada.Text_IO.Put_Line ("PASS CW.Raw_Optional_Hash");
      Case_53;
      Ada.Text_IO.Put_Line ("PASS CW.Raw_Bytes_32");
      Case_54;
      Ada.Text_IO.Put_Line ("PASS CW.Raw_Optional_Counter");
      Case_55;
      Ada.Text_IO.Put_Line ("PASS CW.Raw_Bytes_8");
      Case_56;
      Ada.Text_IO.Put_Line ("PASS CX.Raw_Material");
      Case_57;
      Ada.Text_IO.Put_Line ("PASS HC.Raw_Result");
      Case_58;
      Ada.Text_IO.Put_Line ("PASS CX.Raw_Result");
   end Group_3;
   procedure Probe_Group_1 (Choice : Positive) is
   begin
      case Choice is
         when 1 => Case_1;
         when 2 => Case_2;
         when 3 => Case_3;
         when 4 => Case_4;
         when 5 => Case_5;
         when 6 => Case_6;
         when 7 => Case_7;
         when 8 => Case_8;
         when 9 => Case_9;
         when 10 => Case_10;
         when 11 => Case_11;
         when 12 => Case_12;
         when 13 => Case_13;
         when 14 => Case_14;
         when 15 => Case_15;
         when 16 => Case_16;
         when 17 => Case_17;
         when 18 => Case_18;
         when 19 => Case_19;
         when 20 => Case_20;
         when others => raise Constraint_Error with "invalid decoder probe";
      end case;
   end Probe_Group_1;
   procedure Probe_Group_2 (Choice : Positive) is
   begin
      case Choice is
         when 21 => Case_21;
         when 22 => Case_22;
         when 23 => Case_23;
         when 24 => Case_24;
         when 25 => Case_25;
         when 26 => Case_26;
         when 27 => Case_27;
         when 28 => Case_28;
         when 29 => Case_29;
         when 30 => Case_30;
         when 31 => Case_31;
         when 32 => Case_32;
         when 33 => Case_33;
         when 34 => Case_34;
         when 35 => Case_35;
         when 36 => Case_36;
         when 37 => Case_37;
         when 38 => Case_38;
         when 39 => Case_39;
         when 40 => Case_40;
         when others => raise Constraint_Error with "invalid decoder probe";
      end case;
   end Probe_Group_2;
   procedure Probe_Group_3 (Choice : Positive) is
   begin
      case Choice is
         when 41 => Case_41;
         when 42 => Case_42;
         when 43 => Case_43;
         when 44 => Case_44;
         when 45 => Case_45;
         when 46 => Case_46;
         when 47 => Case_47;
         when 48 => Case_48;
         when 49 => Case_49;
         when 50 => Case_50;
         when 51 => Case_51;
         when 52 => Case_52;
         when 53 => Case_53;
         when 54 => Case_54;
         when 55 => Case_55;
         when 56 => Case_56;
         when 57 => Case_57;
         when 58 => Case_58;
         when others => raise Constraint_Error with "invalid decoder probe";
      end case;
   end Probe_Group_3;

begin
   if Ada.Command_Line.Argument_Count = 2 then
      declare
         Choice : constant Positive := Positive'Value (Ada.Command_Line.Argument (1));
      begin
         if Choice <= 20 then Probe_Group_1 (Choice);
         elsif Choice <= 40 then Probe_Group_2 (Choice);
         else Probe_Group_3 (Choice);
         end if;
      end;
      return;
   end if;
   Check_Id (7);
   Ada.Text_IO.Put_Line ("PASS rebased raw ID decoding");
   Check_Id (Q.Byte_Index'Last - (Width - 1));
   Ada.Text_IO.Put_Line ("PASS maximum-index raw ID decoding");
   Group_1;
   Group_2;
   Group_3;
   Ada.Text_IO.Put_Line ("PASS all retained raw decoder native-layout controls");
end Raw_Decode_Tests;
