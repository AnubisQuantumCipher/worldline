with System;
with Resource_Quantities;
with Resource_Run_Ledger_Wire;
package body Resource_Run_Ledger_C_API with SPARK_Mode => On is
   package Q renames Resource_Quantities;
   package W renames Resource_Run_Ledger_Wire;
   use type Interfaces.C.size_t;
   use type Interfaces.C.long;
   use type Interfaces.C.int;
   use type Q.Byte_Count;
   procedure Read_Packet (Source : not null access constant W.Raw_Packet; Item : out W.Raw_Packet)
   is
   begin
      Item := Source.all;
   end Read_Packet;
   procedure Read_Byte (Source : Q.Byte; Item : out Q.Byte) is
   begin
      Item := Source;
   end Read_Byte;
   procedure Read_Row (Source : not null access constant W.Raw_Row_Array; Index : Q.Byte_Index; Item : out W.Raw_Row)
     with Pre => Index in Source'Range
   is
   begin
      Item := Source (Index);
   end Read_Row;
   procedure Read_Native (Source : not null access constant W.Raw_Native_Array; Index : Q.Byte_Index; Item : out W.Raw_Native)
     with Pre => Index in Source'Range
   is
   begin
      Item := Source (Index);
   end Read_Native;
   function Version return Interfaces.Unsigned_32 is (1);
   function Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long is
      V_Id : constant W.Raw_Id := (Present => 0, First => 0, Length => 0);
      V_Quantity : constant W.Raw_Quantity := (Negative => 0, First => 0, Length => 0);
      V_Epoch : constant W.Raw_Epoch := (Present => 0, Value => V_Quantity);
      V_Context : constant W.Raw_Context := (Policy_Epoch => V_Epoch, others => V_Id);
      V_Binding : constant W.Raw_Binding := (Resource_Epoch => V_Epoch, others => V_Id);
      V_Row : constant W.Raw_Row :=
        (Scope => V_Context, Bound => V_Binding, Parent => V_Id,
         Kind => 0, State => 0, Amount => V_Quantity, Observed_Usage => V_Epoch,
         Planned_Unit | Actual_Unit | Cgroup | Invocation => V_Id);
      V_State : constant W.Raw_State :=
        (Scope => V_Context, Resource_Epoch => V_Epoch,
         Universe_Head | Ledger_Head => V_Id,
         Capacity | Held_Total | Charged_Total => V_Quantity);
      V_Native : constant W.Raw_Native :=
        (Scope => V_Context, Resource_Epoch => V_Epoch, Bound => V_Binding,
         Actual_Unit | Cgroup | Invocation | Observation_Head => V_Id,
         Observed => 0);
      V_Request : constant W.Raw_Request :=
        (Kind => 0, Scope => V_Context, Expected_Epoch => V_Epoch,
         Expected_Ledger_Head | Request_Id | Reservation | Operation_Id | Requester => V_Id,
         Bound => V_Binding, New_Row => V_Row);
      V_Packet : constant W.Raw_Packet :=
        (Schema_Version => 0, Before_State => V_State,
         Proposed_State => V_State, Intent => V_Request);
      V_Result : constant W.Raw_Result := (Status => 0);
   begin
      pragma Compile_Time_Error (V_Id.Present'Position /= 0, "Id.Present");
      pragma Compile_Time_Error (V_Id.First'Position /= 8, "Id.First");
      pragma Compile_Time_Error (V_Id.Length'Position /= 16, "Id.Length");
      pragma Compile_Time_Error (V_Quantity.Negative'Position /= 0, "Quantity.Negative");
      pragma Compile_Time_Error (V_Quantity.First'Position /= 8, "Quantity.First");
      pragma Compile_Time_Error (V_Quantity.Length'Position /= 16, "Quantity.Length");
      pragma Compile_Time_Error (V_Epoch.Present'Position /= 0, "Epoch.Present");
      pragma Compile_Time_Error (V_Epoch.Value'Position /= 8, "Epoch.Value");
      pragma Compile_Time_Error (V_Context.Universe'Position /= 0, "Context.Universe");
      pragma Compile_Time_Error (V_Context.Policy'Position /= 24, "Context.Policy");
      pragma Compile_Time_Error (V_Context.Resource'Position /= 48, "Context.Resource");
      pragma Compile_Time_Error (V_Context.Unit'Position /= 72, "Context.Unit");
      pragma Compile_Time_Error (V_Context.Instance'Position /= 96, "Context.Instance");
      pragma Compile_Time_Error (V_Context.Host'Position /= 120, "Context.Host");
      pragma Compile_Time_Error (V_Context.Boot'Position /= 144, "Context.Boot");
      pragma Compile_Time_Error (V_Context.Authority'Position /= 168, "Context.Authority");
      pragma Compile_Time_Error (V_Context.Policy_Epoch'Position /= 192, "Context.Policy_Epoch");
      pragma Compile_Time_Error (V_Binding.Reservation'Position /= 0, "Binding.Reservation");
      pragma Compile_Time_Error (V_Binding.Operation'Position /= 24, "Binding.Operation");
      pragma Compile_Time_Error (V_Binding.Owner'Position /= 48, "Binding.Owner");
      pragma Compile_Time_Error (V_Binding.Workload'Position /= 72, "Binding.Workload");
      pragma Compile_Time_Error (V_Binding.Universe_Head'Position /= 96, "Binding.Universe");
      pragma Compile_Time_Error (V_Binding.Capability'Position /= 120, "Binding.Capability");
      pragma Compile_Time_Error (V_Binding.Grant_Use'Position /= 144, "Binding.Grant");
      pragma Compile_Time_Error (V_Binding.Payload'Position /= 168, "Binding.Payload");
      pragma Compile_Time_Error (V_Binding.Provenance'Position /= 192, "Binding.Provenance");
      pragma Compile_Time_Error (V_Binding.Resource_Epoch'Position /= 216, "Binding.Epoch");
      pragma Compile_Time_Error (V_Row.Scope'Position /= 0, "Row.Scope");
      pragma Compile_Time_Error (V_Row.Bound'Position /= 224, "Row.Bound");
      pragma Compile_Time_Error (V_Row.Parent'Position /= 472, "Row.Parent");
      pragma Compile_Time_Error (V_Row.Kind'Position /= 496, "Row.Kind");
      pragma Compile_Time_Error (V_Row.State'Position /= 497, "Row.State");
      pragma Compile_Time_Error (V_Row.Amount'Position /= 504, "Row.Amount");
      pragma Compile_Time_Error (V_Row.Observed_Usage'Position /= 528, "Row.Observed");
      pragma Compile_Time_Error (V_Row.Planned_Unit'Position /= 560, "Row.Planned");
      pragma Compile_Time_Error (V_Row.Actual_Unit'Position /= 584, "Row.Actual");
      pragma Compile_Time_Error (V_Row.Cgroup'Position /= 608, "Row.Cgroup");
      pragma Compile_Time_Error (V_Row.Invocation'Position /= 632, "Row.Invocation");
      pragma Compile_Time_Error (V_State.Scope'Position /= 0, "State.Scope");
      pragma Compile_Time_Error (V_State.Resource_Epoch'Position /= 224, "State.Epoch");
      pragma Compile_Time_Error (V_State.Universe_Head'Position /= 256, "State.Universe");
      pragma Compile_Time_Error (V_State.Ledger_Head'Position /= 280, "State.Ledger");
      pragma Compile_Time_Error (V_State.Capacity'Position /= 304, "State.Capacity");
      pragma Compile_Time_Error (V_State.Held_Total'Position /= 328, "State.Held");
      pragma Compile_Time_Error (V_State.Charged_Total'Position /= 352, "State.Charged");
      pragma Compile_Time_Error (V_Native.Scope'Position /= 0, "Native.Scope");
      pragma Compile_Time_Error (V_Native.Resource_Epoch'Position /= 224, "Native.Epoch");
      pragma Compile_Time_Error (V_Native.Bound'Position /= 256, "Native.Bound");
      pragma Compile_Time_Error (V_Native.Actual_Unit'Position /= 504, "Native.Actual");
      pragma Compile_Time_Error (V_Native.Cgroup'Position /= 528, "Native.Cgroup");
      pragma Compile_Time_Error (V_Native.Invocation'Position /= 552, "Native.Invocation");
      pragma Compile_Time_Error (V_Native.Observation_Head'Position /= 576, "Native.Observation");
      pragma Compile_Time_Error (V_Native.Observed'Position /= 600, "Native.Observed");
      pragma Compile_Time_Error (V_Request.Kind'Position /= 0, "Request.Kind");
      pragma Compile_Time_Error (V_Request.Scope'Position /= 8, "Request.Scope");
      pragma Compile_Time_Error (V_Request.Expected_Epoch'Position /= 232, "Request.Epoch");
      pragma Compile_Time_Error (V_Request.Expected_Ledger_Head'Position /= 264, "Request.Ledger");
      pragma Compile_Time_Error (V_Request.Request_Id'Position /= 288, "Request.Id");
      pragma Compile_Time_Error (V_Request.Reservation'Position /= 312, "Request.Reservation");
      pragma Compile_Time_Error (V_Request.Operation_Id'Position /= 336, "Request.Operation");
      pragma Compile_Time_Error (V_Request.Requester'Position /= 360, "Request.Requester");
      pragma Compile_Time_Error (V_Request.Bound'Position /= 384, "Request.Bound");
      pragma Compile_Time_Error (V_Request.New_Row'Position /= 632, "Request.Row");
      pragma Compile_Time_Error (V_Packet.Schema_Version'Position /= 0, "Packet.Schema");
      pragma Compile_Time_Error (V_Packet.Before_State'Position /= 8, "Packet.Before");
      pragma Compile_Time_Error (V_Packet.Proposed_State'Position /= 384, "Packet.Proposed");
      pragma Compile_Time_Error (V_Packet.Intent'Position /= 760, "Packet.Intent");
      pragma Compile_Time_Error (V_Result.Status'Position /= 0, "Result.Status");
      case Kind is
         when 1 =>
            case Field is
               when 0 => return W.Raw_Id'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_Id'Alignment;
               when 2 => return 0; when 3 => return 8; when 4 => return 16;
               when others => return -1;
            end case;
         when 2 =>
            case Field is
               when 0 => return W.Raw_Quantity'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_Quantity'Alignment;
               when 2 => return 0; when 3 => return 8; when 4 => return 16;
               when others => return -1;
            end case;
         when 3 =>
            case Field is
               when 0 => return W.Raw_Epoch'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_Epoch'Alignment;
               when 2 => return 0; when 3 => return 8;
               when others => return -1;

            end case;
         when 4 =>
            case Field is
               when 0 => return W.Raw_Context'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_Context'Alignment;
               when 2 => return 0; when 3 => return 24; when 4 => return 48;
               when 5 => return 72; when 6 => return 96; when 7 => return 120;
               when 8 => return 144; when 9 => return 168; when 10 => return 192;
               when others => return -1;
            end case;
         when 5 =>
            case Field is
               when 0 => return W.Raw_Binding'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_Binding'Alignment;
               when 2 => return 0; when 3 => return 24; when 4 => return 48;
               when 5 => return 72; when 6 => return 96; when 7 => return 120;
               when 8 => return 144; when 9 => return 168; when 10 => return 192;
               when 11 => return 216;
               when others => return -1;
            end case;
         when 6 =>
            case Field is
               when 0 => return W.Raw_Row'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_Row'Alignment;
               when 2 => return 0; when 3 => return 224; when 4 => return 472;
               when 5 => return 496; when 6 => return 497; when 7 => return 504;
               when 8 => return 528; when 9 => return 560; when 10 => return 584;
               when 11 => return 608; when 12 => return 632;
               when others => return -1;
            end case;
         when 7 =>
            case Field is
               when 0 => return W.Raw_State'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_State'Alignment;
               when 2 => return 0; when 3 => return 224; when 4 => return 256;
               when 5 => return 280; when 6 => return 304; when 7 => return 328;
               when 8 => return 352;
               when others => return -1;
            end case;
         when 8 =>
            case Field is
               when 0 => return W.Raw_Native'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_Native'Alignment;
               when 2 => return 0; when 3 => return 224; when 4 => return 256;
               when 5 => return 504; when 6 => return 528; when 7 => return 552;
               when 8 => return 576; when 9 => return 600;
               when others => return -1;
            end case;
         when 9 =>
            case Field is
               when 0 => return W.Raw_Request'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_Request'Alignment;
               when 2 => return 0; when 3 => return 8; when 4 => return 232;
               when 5 => return 264; when 6 => return 288; when 7 => return 312;
               when 8 => return 336; when 9 => return 360; when 10 => return 384;
               when 11 => return 632;
               when others => return -1;
            end case;
         when 10 =>
            case Field is
               when 0 => return W.Raw_Packet'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_Packet'Alignment;
               when 2 => return 0; when 3 => return 8; when 4 => return 384;
               when 5 => return 760;
               when others => return -1;
            end case;
         when 11 =>
            case Field is
               when 0 => return W.Raw_Result'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_Result'Alignment;
               when 2 => return 0;
               when others => return -1;
            end case;
         when others => return -1;
      end case;
   end Layout;
   function Check
     (Input : not null access constant Resource_Run_Ledger_Wire.Raw_Packet;
      Arena : not null access constant Resource_Quantities.Byte_Array;
      Before_Rows, Proposed_Rows : not null access constant Resource_Run_Ledger_Wire.Raw_Row_Array;
      Native : not null access constant Resource_Run_Ledger_Wire.Raw_Native_Array;
      Output : out Resource_Run_Ledger_Wire.Raw_Result) return Interfaces.C.int is
   begin
      Output := (Status => 0);
      if Arena'First /= 1 or else Before_Rows'First /= 1 or else Proposed_Rows'First /= 1 or else Native'First /= 1 then return -1; end if;
      declare
         Raw : W.Raw_Packet;
         Data : Q.Byte_Array (1 .. Q.Byte_Count (Arena'Length));
         Before : W.Raw_Row_Array (1 .. Q.Byte_Count (Before_Rows'Length));
         Proposed : W.Raw_Row_Array (1 .. Q.Byte_Count (Proposed_Rows'Length));
         Observed : W.Raw_Native_Array (1 .. Q.Byte_Count (Native'Length));
      begin
         Read_Packet (Input, Raw);
         for I in Data'Range loop
            Read_Byte (Arena (I), Data (I));
         end loop;
         for I in Before'Range loop
            Read_Row
              (Before_Rows, I,
               Before (I));
         end loop;
         for I in Proposed'Range loop
            Read_Row
              (Proposed_Rows, I,
               Proposed (I));
         end loop;
         for I in Observed'Range loop
            Read_Native
              (Native, I,
               Observed (I));
         end loop;
         if not W.Well_Formed (Data, Raw, Before, Proposed, Observed) then
            return -1;
         end if;
         -- Every input is copied before output, including valid overlapping arenas.
         Output := W.Decide (Data, Raw, Before, Proposed, Observed);
      end;
      return 0;
   end Check;
end Resource_Run_Ledger_C_API;
