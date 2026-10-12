with System.Storage_Elements;
with Resource_Quantities;
with Worldline.Recovery_Authorization_V3_Wire;

package body Worldline.Recovery_Authorization_V3_C_API with SPARK_Mode => On is
   package W renames Worldline.Recovery_Authorization_V3_Wire;
   package Q renames Resource_Quantities;
   use System.Storage_Elements;
   use type System.Address;
   use type Interfaces.C.size_t;
   use type Interfaces.C.long;
   use type Interfaces.C.int;
   use type Q.Byte_Count;

   procedure Read_Request (View : access constant Worldline.Recovery_Authorization_V3_Wire.Raw_Request; Item : out Worldline.Recovery_Authorization_V3_Wire.Raw_Request)
     with Exceptional_Cases => (others => True)
   is
   begin
      if View = null then
         raise Constraint_Error;
      end if;
      Item := View.all;
   end Read_Request;

   procedure Read_Byte
     (View : access constant Q.Byte_Array; Position : Q.Byte_Index; Item : out Q.Byte)
     with Exceptional_Cases => (others => True)
   is
   begin
      if View = null or else Position not in View.all'Range then
         raise Constraint_Error;
      end if;
      Item := View.all (Position);
   end Read_Byte;

   procedure Write_Result (View : access Worldline.Recovery_Authorization_V3_Wire.Raw_Result; Item : Worldline.Recovery_Authorization_V3_Wire.Raw_Result)
     with Exceptional_Cases => (others => True)
   is
   begin
      if View = null then
         raise Constraint_Error;
      end if;
      View.all := Item;
   end Write_Result;

   function Version return Interfaces.Unsigned_32 is (3);

   function Layout
     (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long
   is
      Blank : constant W.Raw_Hash := (others => 0);
      V1 : constant W.Raw_Digest := (Present => 0, Value => Blank);
      V2 : constant W.Raw_Epoch := (Present => 0, Negative => 0, First => 0, Length => 0);
      V3 : constant W.Raw_Binding :=
        (Mode => 0, Policy_Epoch => V2, Resource_Epoch => V2, others => V1);
      V4 : constant W.Raw_Native := (others => V1);
      V5 : constant W.Raw_Request :=
        (Schema_Version => 0,
         State | Fresh | Historical | Grant_Eligible => 0,
         Issued_Binding => V3, Recovered_Binding => V3, Native => V4);
      V6 : constant W.Raw_Result := (Action => 0, State => 0);
   begin
      pragma Compile_Time_Error (V1.Present'Position /= 0, "Digest.Present");
      pragma Compile_Time_Error (V1.Value'Position /= 1, "Digest.Value");
      pragma Compile_Time_Error (V2.Present'Position /= 0, "Epoch.Present");
      pragma Compile_Time_Error (V2.Negative'Position /= 1, "Epoch.Negative");
      pragma Compile_Time_Error (V2.First'Position /= 8, "Epoch.First");
      pragma Compile_Time_Error (V2.Length'Position /= 16, "Epoch.Length");
      pragma Compile_Time_Error (V3.Mode'Position /= 0, "Binding.Mode");
      pragma Compile_Time_Error (V3.Operation'Position /= 1, "Binding.Operation");
      pragma Compile_Time_Error (V3.Transaction'Position /= 34, "Binding.Transaction");
      pragma Compile_Time_Error (V3.Capability'Position /= 67, "Binding.Capability");
      pragma Compile_Time_Error (V3.Universe_Head'Position /= 100, "Binding.Universe");
      pragma Compile_Time_Error (V3.Instance'Position /= 133, "Binding.Instance");
      pragma Compile_Time_Error (V3.Subject'Position /= 166, "Binding.Subject");
      pragma Compile_Time_Error (V3.Staged_Root'Position /= 199, "Binding.Staged_Root");
      pragma Compile_Time_Error (V3.Current_Requirement'Position /= 232, "Binding.Current");
      pragma Compile_Time_Error (V3.Resulting_Requirement'Position /= 265, "Binding.Resulting");
      pragma Compile_Time_Error (V3.Requester'Position /= 298, "Binding.Requester");
      pragma Compile_Time_Error (V3.Grant_Use'Position /= 331, "Binding.Grant");
      pragma Compile_Time_Error (V3.Policy_Identity'Position /= 364, "Binding.Policy_Id");
      pragma Compile_Time_Error (V3.Selected_Evaluation'Position /= 397, "Binding.Selected");
      pragma Compile_Time_Error (V3.History_Head'Position /= 430, "Binding.History");
      pragma Compile_Time_Error (V3.Reservation'Position /= 463, "Binding.Reservation");
      pragma Compile_Time_Error (V3.Host'Position /= 496, "Binding.Host");
      pragma Compile_Time_Error (V3.Before_Prime'Position /= 529, "Binding.Before_Prime");
      pragma Compile_Time_Error (V3.Before_Root'Position /= 562, "Binding.Before_Root");
      pragma Compile_Time_Error (V3.Before_Mapping'Position /= 595, "Binding.Before_Mapping");
      pragma Compile_Time_Error (V3.Staged_Mapping'Position /= 628, "Binding.Staged_Mapping");
      pragma Compile_Time_Error (V3.Input_Snapshot'Position /= 661, "Binding.Input");
      pragma Compile_Time_Error (V3.Kernel_Build'Position /= 694, "Binding.Kernel_Build");
      pragma Compile_Time_Error (V3.Kernel_Library'Position /= 727, "Binding.Kernel_Library");
      pragma Compile_Time_Error (V3.Kernel_Mapping'Position /= 760, "Binding.Kernel_Mapping");
      pragma Compile_Time_Error (V3.Issuer_Head'Position /= 793, "Binding.Issuer");
      pragma Compile_Time_Error (V3.Receipt_Head'Position /= 826, "Binding.Receipt");
      pragma Compile_Time_Error (V3.Causal_Head'Position /= 859, "Binding.Causal");
      pragma Compile_Time_Error (V3.Policy_Epoch'Position /= 896, "Binding.Policy_Epoch");
      pragma Compile_Time_Error (V3.Resource_Epoch'Position /= 920, "Binding.Resource_Epoch");
      pragma Compile_Time_Error (V4.Live_Mapping'Position /= 0, "Native.Mapping");
      pragma Compile_Time_Error (V4.Live_Root'Position /= 33, "Native.Root");
      pragma Compile_Time_Error (V5.Schema_Version'Position /= 0, "Request.Schema");
      pragma Compile_Time_Error (V5.State'Position /= 4, "Request.State");
      pragma Compile_Time_Error (V5.Fresh'Position /= 5, "Request.Fresh");
      pragma Compile_Time_Error (V5.Historical'Position /= 6, "Request.Historical");
      pragma Compile_Time_Error (V5.Grant_Eligible'Position /= 7, "Request.Grant");
      pragma Compile_Time_Error (V5.Issued_Binding'Position /= 8, "Request.Issued");
      pragma Compile_Time_Error (V5.Recovered_Binding'Position /= 952, "Request.Recovered");
      pragma Compile_Time_Error (V5.Native'Position /= 1896, "Request.Native");
      pragma Compile_Time_Error (V6.Action'Position /= 0, "Result.Action");
      pragma Compile_Time_Error (V6.State'Position /= 1, "Result.State");
      case Kind is
         when 1 =>
            case Field is
               when 0 => return W.Raw_Digest'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_Digest'Alignment;
               when 2 => return 0;
               when 3 => return 1;
               when others => return -1;
            end case;
         when 2 =>
            case Field is
               when 0 => return W.Raw_Epoch'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_Epoch'Alignment;
               when 2 => return 0;
               when 3 => return 1;
               when 4 => return 8;
               when 5 => return 16;
               when others => return -1;
            end case;
         when 3 =>
            case Field is
               when 0 => return W.Raw_Binding'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_Binding'Alignment;
               when 2 => return 0; when 3 => return 1; when 4 => return 34;
               when 5 => return 67; when 6 => return 100; when 7 => return 133;
               when 8 => return 166; when 9 => return 199; when 10 => return 232;
               when 11 => return 265; when 12 => return 298; when 13 => return 331;
               when 14 => return 364; when 15 => return 397; when 16 => return 430;
               when 17 => return 463; when 18 => return 496; when 19 => return 529;
               when 20 => return 562; when 21 => return 595; when 22 => return 628;
               when 23 => return 661; when 24 => return 694; when 25 => return 727;
               when 26 => return 760; when 27 => return 793; when 28 => return 826;
               when 29 => return 859; when 30 => return 896; when 31 => return 920;
               when others => return -1;
            end case;
         when 4 =>
            case Field is
               when 0 => return W.Raw_Native'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_Native'Alignment;
               when 2 => return 0;
               when 3 => return 33;
               when others => return -1;
            end case;
         when 5 =>
            case Field is
               when 0 => return W.Raw_Request'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_Request'Alignment;
               when 2 => return 0; when 3 => return 4; when 4 => return 5;
               when 5 => return 6; when 6 => return 7; when 7 => return 8;
               when 8 => return 952; when 9 => return 1896;
               when others => return -1;
            end case;
         when 6 =>
            case Field is
               when 0 => return W.Raw_Result'Object_Size / System.Storage_Unit;
               when 1 => return W.Raw_Result'Alignment;
               when 2 => return 0;
               when 3 => return 1;
               when others => return -1;
            end case;
         when others => return -1;
      end case;
   end Layout;

   function Shape (Address : System.Address; Length : Interfaces.C.size_t)
      return Boolean is
     (Address /= System.Null_Address and then Length > 0 and then
      Length <= Interfaces.C.size_t (Storage_Offset'Last) and then
      Integer_Address (Length - 1) <=
        Integer_Address'Last - To_Integer (Address));

   function Transport_Valid
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Arena : System.Address; Arena_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Boolean is
     (not (Input_Length /= W.Raw_Request'Object_Size / System.Storage_Unit or else
        Output_Length /= W.Raw_Result'Object_Size / System.Storage_Unit or else
        not Shape (Input, Input_Length) or else
        not Shape (Output, Output_Length) or else
        Arena_Length > Interfaces.C.size_t (Q.Byte_Count'Last) or else
        (Arena_Length > 0 and then not Shape (Arena, Arena_Length)) or else
        To_Integer (Input) mod W.Raw_Request'Alignment /= 0 or else
        To_Integer (Output) mod W.Raw_Result'Alignment /= 0));

   function Decide
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Arena : System.Address; Arena_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t;
      Input_View : access constant Worldline.Recovery_Authorization_V3_Wire.Raw_Request;
      Output_View : access Worldline.Recovery_Authorization_V3_Wire.Raw_Result;
      Arena_View : access constant Resource_Quantities.Byte_Array)
      return Interfaces.C.int
   is
   begin
      if not Transport_Valid (Input, Input_Length, Arena, Arena_Length, Output, Output_Length) then
         return -1;
      end if;
      if Arena_Length > 0 and then
        (Arena_View = null or else Arena_View.all'First /= 1 or else
         Arena_View.all'Length /= Arena_Length) then
         return -1;
      end if;
      declare
         Raw : W.Raw_Request;
         Data : Q.Byte_Array (1 .. Q.Byte_Count (Arena_Length));
      begin
         Read_Request (Input_View, Raw);
         for Position in Data'Range loop
            Read_Byte (Arena_View, Position, Data (Position));
         end loop;
         if not W.Well_Formed (Data, Raw) then
            return -1;
         end if;
         --  Copy the complete input before writing output, including when a
         --  valid caller's arenas overlap. The SPARK wire body owns semantics.
         Write_Result (Output_View, W.Decide (Data, Raw));
      end;
      return 0;
   exception
      when others => return -1;
   end Decide;
end Worldline.Recovery_Authorization_V3_C_API;
