   function Full_Physical_Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_full_physical_version_v1";
   function Full_Physical_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long
     with Export, Convention => C, External_Name => "wl_full_physical_layout_v1";
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
      Witness : System.Address; Witness_Length : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_full_physical_exchange_v1";
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
      Witness : System.Address; Witness_Length : Interfaces.C.size_t) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_full_physical_recover_v1";
   function Actuation_Decide(P : System.Address) return Interfaces.C.unsigned_char
     with Export, Convention => C, External_Name => "wl_actuation_decide";
