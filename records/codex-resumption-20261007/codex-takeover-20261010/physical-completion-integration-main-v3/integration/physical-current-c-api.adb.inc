   function Full_Physical_Version return Interfaces.Unsigned_32 is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);
      function Native return Interfaces.Unsigned_32
        with Import, Convention => C, External_Name => "wl_internal_full_physical_version_v1";
   begin
      return Native;
      end;
   exception
      when others => return 0;
   end Full_Physical_Version;
   function Full_Physical_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);
      function Native (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long
        with Import, Convention => C, External_Name => "wl_internal_full_physical_layout_v1";
   begin
      return Native (Kind, Field);
      end;
   exception
      when others => return -1;
   end Full_Physical_Layout;
   function Full_Physical_Exchange (Original_Peer_Fd, Data_Fd, Transaction_Fd, Payload_Fd : Interfaces.C.int;
      Input : System.Address; Input_Length : Interfaces.C.size_t;
      Arena : System.Address; Arena_Length : Interfaces.C.size_t;
      Grants : System.Address; Grant_Count, Grant_Length : Interfaces.C.size_t;
      Uses : System.Address; Use_Count, Use_Length : Interfaces.C.size_t;
      Rows : System.Address; Row_Count, Row_Length : Interfaces.C.size_t;
      Observed : System.Address; Observed_Count, Observed_Length : Interfaces.C.size_t;
      Worker_Receipts : System.Address; Worker_Receipt_Count, Worker_Receipt_Length : Interfaces.C.size_t;
      Worker_Events : System.Address; Worker_Event_Count, Worker_Event_Length : Interfaces.C.size_t;
      Effect_Receipts : System.Address; Effect_Receipt_Count, Effect_Receipt_Length : Interfaces.C.size_t;
      Effect_Events : System.Address; Effect_Event_Count, Effect_Event_Length : Interfaces.C.size_t;
      Actuation : System.Address; Actuation_Length : Interfaces.C.size_t;
      Witness : System.Address; Witness_Length : Interfaces.C.size_t) return Interfaces.C.int is
      Native_Attempted, Native_Returned : Boolean := False;
      Native_Status : Interfaces.C.int := 1;
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);
      function Native (Original_Peer_Fd, Data_Fd, Transaction_Fd, Payload_Fd : Interfaces.C.int;
      Input : System.Address; Input_Length : Interfaces.C.size_t;
      Arena : System.Address; Arena_Length : Interfaces.C.size_t;
      Grants : System.Address; Grant_Count, Grant_Length : Interfaces.C.size_t;
      Uses : System.Address; Use_Count, Use_Length : Interfaces.C.size_t;
      Rows : System.Address; Row_Count, Row_Length : Interfaces.C.size_t;
      Observed : System.Address; Observed_Count, Observed_Length : Interfaces.C.size_t;
      Worker_Receipts : System.Address; Worker_Receipt_Count, Worker_Receipt_Length : Interfaces.C.size_t;
      Worker_Events : System.Address; Worker_Event_Count, Worker_Event_Length : Interfaces.C.size_t;
      Effect_Receipts : System.Address; Effect_Receipt_Count, Effect_Receipt_Length : Interfaces.C.size_t;
      Effect_Events : System.Address; Effect_Event_Count, Effect_Event_Length : Interfaces.C.size_t;
      Actuation : System.Address; Actuation_Length : Interfaces.C.size_t;
      Witness : System.Address; Witness_Length : Interfaces.C.size_t) return Interfaces.C.int
        with Import, Convention => C, External_Name => "wl_internal_full_physical_exchange_v1";
   begin
      Native_Attempted := True;
      Native_Status := Native (Original_Peer_Fd, Data_Fd, Transaction_Fd, Payload_Fd, Input, Input_Length, Arena, Arena_Length, Grants, Grant_Count, Grant_Length, Uses, Use_Count, Use_Length, Rows, Row_Count, Row_Length, Observed, Observed_Count, Observed_Length, Worker_Receipts, Worker_Receipt_Count, Worker_Receipt_Length, Worker_Events, Worker_Event_Count, Worker_Event_Length, Effect_Receipts, Effect_Receipt_Count, Effect_Receipt_Length, Effect_Events, Effect_Event_Count, Effect_Event_Length, Actuation, Actuation_Length, Witness, Witness_Length);
      Native_Returned := True;
      Flush_Native_Diagnostic_Trace;
      return Native_Status;
      end;
   exception
      when others =>
         if Native_Returned then return Native_Status;
         elsif Native_Attempted then return 3;
         else return 1; end if;
   end Full_Physical_Exchange;
   function Full_Physical_Recover (Original_Peer_Fd, Data_Fd, Transaction_Fd, Payload_Fd : Interfaces.C.int;
      Input : System.Address; Input_Length : Interfaces.C.size_t;
      Arena : System.Address; Arena_Length : Interfaces.C.size_t;
      Grants : System.Address; Grant_Count, Grant_Length : Interfaces.C.size_t;
      Uses : System.Address; Use_Count, Use_Length : Interfaces.C.size_t;
      Rows : System.Address; Row_Count, Row_Length : Interfaces.C.size_t;
      Observed : System.Address; Observed_Count, Observed_Length : Interfaces.C.size_t;
      Worker_Receipts : System.Address; Worker_Receipt_Count, Worker_Receipt_Length : Interfaces.C.size_t;
      Worker_Events : System.Address; Worker_Event_Count, Worker_Event_Length : Interfaces.C.size_t;
      Effect_Receipts : System.Address; Effect_Receipt_Count, Effect_Receipt_Length : Interfaces.C.size_t;
      Effect_Events : System.Address; Effect_Event_Count, Effect_Event_Length : Interfaces.C.size_t;
      Actuation : System.Address; Actuation_Length : Interfaces.C.size_t;
      Witness : System.Address; Witness_Length : Interfaces.C.size_t) return Interfaces.C.int is
      Native_Attempted, Native_Returned : Boolean := False;
      Native_Status : Interfaces.C.int := 1;
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);
      function Native (Original_Peer_Fd, Data_Fd, Transaction_Fd, Payload_Fd : Interfaces.C.int;
      Input : System.Address; Input_Length : Interfaces.C.size_t;
      Arena : System.Address; Arena_Length : Interfaces.C.size_t;
      Grants : System.Address; Grant_Count, Grant_Length : Interfaces.C.size_t;
      Uses : System.Address; Use_Count, Use_Length : Interfaces.C.size_t;
      Rows : System.Address; Row_Count, Row_Length : Interfaces.C.size_t;
      Observed : System.Address; Observed_Count, Observed_Length : Interfaces.C.size_t;
      Worker_Receipts : System.Address; Worker_Receipt_Count, Worker_Receipt_Length : Interfaces.C.size_t;
      Worker_Events : System.Address; Worker_Event_Count, Worker_Event_Length : Interfaces.C.size_t;
      Effect_Receipts : System.Address; Effect_Receipt_Count, Effect_Receipt_Length : Interfaces.C.size_t;
      Effect_Events : System.Address; Effect_Event_Count, Effect_Event_Length : Interfaces.C.size_t;
      Actuation : System.Address; Actuation_Length : Interfaces.C.size_t;
      Witness : System.Address; Witness_Length : Interfaces.C.size_t) return Interfaces.C.int
        with Import, Convention => C, External_Name => "wl_internal_full_physical_recover_v1";
   begin
      Native_Attempted := True;
      Native_Status := Native (Original_Peer_Fd, Data_Fd, Transaction_Fd, Payload_Fd, Input, Input_Length, Arena, Arena_Length, Grants, Grant_Count, Grant_Length, Uses, Use_Count, Use_Length, Rows, Row_Count, Row_Length, Observed, Observed_Count, Observed_Length, Worker_Receipts, Worker_Receipt_Count, Worker_Receipt_Length, Worker_Events, Worker_Event_Count, Worker_Event_Length, Effect_Receipts, Effect_Receipt_Count, Effect_Receipt_Length, Effect_Events, Effect_Event_Count, Effect_Event_Length, Actuation, Actuation_Length, Witness, Witness_Length);
      Native_Returned := True;
      Flush_Native_Diagnostic_Trace;
      return Native_Status;
      end;
   exception
      when others =>
         if Native_Returned then return Native_Status;
         elsif Native_Attempted then return 3;
         else return 1; end if;
   end Full_Physical_Recover;
   function Actuation_Decide(P:System.Address) return Interfaces.C.unsigned_char is
      Decision_Returned : Boolean := False;
      Decision_Status : Interfaces.C.unsigned_char := 255;
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);
   package W renames Worldline.Actuation_Full_Wire;
   use type System.Address; use System.Storage_Elements;
   type Pointer is access all W.Raw_Request;
   function Convert is new Ada.Unchecked_Conversion(System.Address,Pointer);
   begin
      if P=System.Null_Address or else To_Integer(P) mod W.Raw_Request'Alignment/=0
        or else To_Integer(P)>Integer_Address'Last-W.Raw_Request'Size/System.Storage_Unit
      then return 255; end if;
      declare Value:constant W.Raw_Request:=Convert(P).all;
      begin
         if not W.Well_Formed(Value) then return 255; end if;
         Decision_Status :=
           Interfaces.C.unsigned_char(W.A.Decision'Pos(W.A.Decide(W.Decode(Value))));
         Decision_Returned := True;
         Flush_Native_Diagnostic_Trace;
         return Decision_Status;
      end;
   exception
         when others =>
            if Decision_Returned then return Decision_Status;
            else return 255; end if;
      end;
   exception
      when others =>
         if Decision_Returned then return Decision_Status;
         else return 255; end if;
   end Actuation_Decide;
