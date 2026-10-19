with Resource_Run_Ledger_Wire;
with Resource_Observation_Classification;
package Resource_Observation_Classification_Wire with SPARK_Mode is
   package W renames Resource_Run_Ledger_Wire;
   package K renames Resource_Observation_Classification;
   package Q renames W.Q;
   package L renames W.L;
   subtype U8 is W.U8;
   use type U8;
   use type K.Facts;
   use type L.Liveness;
   type Raw_Facts is record
      Current : W.Raw_Context;
      Current_Epoch : W.Raw_Epoch;
      Retained : W.Raw_Binding;
      Current_Universe_Head : W.Raw_Id;
      Current_Ledger_Head : W.Raw_Id;
      Intent : W.Raw_Id;
      Dispatch : W.Raw_Id;
      Observation_Head : W.Raw_Id;
      Actual_Unit : W.Raw_Id;
      Cgroup : W.Raw_Id;
      Invocation : W.Raw_Id;
      Namespace : W.Raw_Id;
      Held_Namespace : W.Raw_Id;
      Peer : W.Raw_Id;
      Held_Peer : W.Raw_Id;
      Helper_Image : W.Raw_Id;
      Expected_Helper_Image : W.Raw_Id;
      Challenge : W.Raw_Id;
      Held_Challenge : W.Raw_Id;
      Protocol : W.Raw_Id;
      Closed_Event : W.Raw_Id;
      Namespace_Wait : W.Raw_Id;
      Helper_Wait : W.Raw_Id;
      Cgroup_Events : W.Raw_Id;
      Cgroup_Type : W.Raw_Id;
      Manager_Delegate : W.Raw_Id;
      Cgroup_Owner : W.Raw_Epoch;
      Cgroup_Group_Write : W.Raw_Epoch;
      Cgroup_Other_Write : W.Raw_Epoch;
      Actual_Store_Genesis : W.Raw_Id;
      Actual_Store_Id : W.Raw_Id;
      Owner_Store_Genesis : W.Raw_Id;
      Owner_Store_Id : W.Raw_Id;
      Genesis_Universe : W.Raw_Id;
      Genesis_Instance : W.Raw_Id;
      Genesis_Context_Head : W.Raw_Id;
      Genesis_Prime : W.Raw_Id;
      Genesis_Root_Count : W.Raw_Epoch;
      Phase : U8;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Facts use record
      Current at 0 range 0 .. 1791;
      Current_Epoch at 224 range 0 .. 255;
      Retained at 256 range 0 .. 1983;
      Current_Universe_Head at 504 range 0 .. 191;
      Current_Ledger_Head at 528 range 0 .. 191;
      Intent at 552 range 0 .. 191;
      Dispatch at 576 range 0 .. 191;
      Observation_Head at 600 range 0 .. 191;
      Actual_Unit at 624 range 0 .. 191;
      Cgroup at 648 range 0 .. 191;
      Invocation at 672 range 0 .. 191;
      Namespace at 696 range 0 .. 191;
      Held_Namespace at 720 range 0 .. 191;
      Peer at 744 range 0 .. 191;
      Held_Peer at 768 range 0 .. 191;
      Helper_Image at 792 range 0 .. 191;
      Expected_Helper_Image at 816 range 0 .. 191;
      Challenge at 840 range 0 .. 191;
      Held_Challenge at 864 range 0 .. 191;
      Protocol at 888 range 0 .. 191;
      Closed_Event at 912 range 0 .. 191;
      Namespace_Wait at 936 range 0 .. 191;
      Helper_Wait at 960 range 0 .. 191;
      Cgroup_Events at 984 range 0 .. 191;
      Cgroup_Type at 1008 range 0 .. 191;
      Manager_Delegate at 1032 range 0 .. 191;
      Cgroup_Owner at 1056 range 0 .. 255;
      Cgroup_Group_Write at 1088 range 0 .. 255;
      Cgroup_Other_Write at 1120 range 0 .. 255;
      Actual_Store_Genesis at 1152 range 0 .. 191;
      Actual_Store_Id at 1176 range 0 .. 191;
      Owner_Store_Genesis at 1200 range 0 .. 191;
      Owner_Store_Id at 1224 range 0 .. 191;
      Genesis_Universe at 1248 range 0 .. 191;
      Genesis_Instance at 1272 range 0 .. 191;
      Genesis_Context_Head at 1296 range 0 .. 191;
      Genesis_Prime at 1320 range 0 .. 191;
      Genesis_Root_Count at 1344 range 0 .. 255;
      Phase at 1376 range 0 .. 7;
   end record;
   for Raw_Facts'Size use 11016;
   for Raw_Facts'Object_Size use 11072;
   for Raw_Facts'Alignment use 8;
   type Raw_Input is record
      State : W.Raw_State;
      Item : W.Raw_Row;
      Captured : Raw_Facts;
   end record with Convention => C;
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Facts) return Boolean is
     (W.Well_Formed (Data, Raw.Current)
      and then W.Well_Formed (Data, Raw.Current_Epoch)
      and then W.Well_Formed (Data, Raw.Retained)
      and then W.Well_Formed (Data, Raw.Current_Universe_Head)
      and then W.Well_Formed (Data, Raw.Current_Ledger_Head)
      and then W.Well_Formed (Data, Raw.Intent)
      and then W.Well_Formed (Data, Raw.Dispatch)
      and then W.Well_Formed (Data, Raw.Observation_Head)
      and then W.Well_Formed (Data, Raw.Actual_Unit)
      and then W.Well_Formed (Data, Raw.Cgroup)
      and then W.Well_Formed (Data, Raw.Invocation)
      and then W.Well_Formed (Data, Raw.Namespace)
      and then W.Well_Formed (Data, Raw.Held_Namespace)
      and then W.Well_Formed (Data, Raw.Peer)
      and then W.Well_Formed (Data, Raw.Held_Peer)
      and then W.Well_Formed (Data, Raw.Helper_Image)
      and then W.Well_Formed (Data, Raw.Expected_Helper_Image)
      and then W.Well_Formed (Data, Raw.Challenge)
      and then W.Well_Formed (Data, Raw.Held_Challenge)
      and then W.Well_Formed (Data, Raw.Protocol)
      and then W.Well_Formed (Data, Raw.Closed_Event)
      and then W.Well_Formed (Data, Raw.Namespace_Wait)
      and then W.Well_Formed (Data, Raw.Helper_Wait)
      and then W.Well_Formed (Data, Raw.Cgroup_Events)
      and then W.Well_Formed (Data, Raw.Cgroup_Type)
      and then W.Well_Formed (Data, Raw.Manager_Delegate)
      and then W.Well_Formed (Data, Raw.Cgroup_Owner)
      and then W.Well_Formed (Data, Raw.Cgroup_Group_Write)
      and then W.Well_Formed (Data, Raw.Cgroup_Other_Write)
      and then W.Well_Formed (Data, Raw.Actual_Store_Genesis)
      and then W.Well_Formed (Data, Raw.Actual_Store_Id)
      and then W.Well_Formed (Data, Raw.Owner_Store_Genesis)
      and then W.Well_Formed (Data, Raw.Owner_Store_Id)
      and then W.Well_Formed (Data, Raw.Genesis_Universe)
      and then W.Well_Formed (Data, Raw.Genesis_Instance)
      and then W.Well_Formed (Data, Raw.Genesis_Context_Head)
      and then W.Well_Formed (Data, Raw.Genesis_Prime)
      and then W.Well_Formed (Data, Raw.Genesis_Root_Count)
      and then Raw.Phase <= K.Journal_Phase'Pos (K.Journal_Phase'Last)) with Global => null;
   function Decode (Data : Q.Byte_Array; Raw : Raw_Facts) return K.Facts is
     (Current => W.Decode (Data, Raw.Current),
      Current_Epoch => W.Decode (Data, Raw.Current_Epoch),
      Retained => W.Decode (Data, Raw.Retained),
      Current_Universe_Head => W.Decode (Data, Raw.Current_Universe_Head),
      Current_Ledger_Head => W.Decode (Data, Raw.Current_Ledger_Head),
      Intent => W.Decode (Data, Raw.Intent),
      Dispatch => W.Decode (Data, Raw.Dispatch),
      Observation_Head => W.Decode (Data, Raw.Observation_Head),
      Actual_Unit => W.Decode (Data, Raw.Actual_Unit),
      Cgroup => W.Decode (Data, Raw.Cgroup),
      Invocation => W.Decode (Data, Raw.Invocation),
      Namespace => W.Decode (Data, Raw.Namespace),
      Held_Namespace => W.Decode (Data, Raw.Held_Namespace),
      Peer => W.Decode (Data, Raw.Peer),
      Held_Peer => W.Decode (Data, Raw.Held_Peer),
      Helper_Image => W.Decode (Data, Raw.Helper_Image),
      Expected_Helper_Image => W.Decode (Data, Raw.Expected_Helper_Image),
      Challenge => W.Decode (Data, Raw.Challenge),
      Held_Challenge => W.Decode (Data, Raw.Held_Challenge),
      Protocol => W.Decode (Data, Raw.Protocol),
      Closed_Event => W.Decode (Data, Raw.Closed_Event),
      Namespace_Wait => W.Decode (Data, Raw.Namespace_Wait),
      Helper_Wait => W.Decode (Data, Raw.Helper_Wait),
      Cgroup_Events => W.Decode (Data, Raw.Cgroup_Events),
      Cgroup_Type => W.Decode (Data, Raw.Cgroup_Type),
      Manager_Delegate => W.Decode (Data, Raw.Manager_Delegate),
      Cgroup_Owner => W.Decode (Data, Raw.Cgroup_Owner),
      Cgroup_Group_Write => W.Decode (Data, Raw.Cgroup_Group_Write),
      Cgroup_Other_Write => W.Decode (Data, Raw.Cgroup_Other_Write),
      Actual_Store_Genesis => W.Decode (Data, Raw.Actual_Store_Genesis),
      Actual_Store_Id => W.Decode (Data, Raw.Actual_Store_Id),
      Owner_Store_Genesis => W.Decode (Data, Raw.Owner_Store_Genesis),
      Owner_Store_Id => W.Decode (Data, Raw.Owner_Store_Id),
      Genesis_Universe => W.Decode (Data, Raw.Genesis_Universe),
      Genesis_Instance => W.Decode (Data, Raw.Genesis_Instance),
      Genesis_Context_Head => W.Decode (Data, Raw.Genesis_Context_Head),
      Genesis_Prime => W.Decode (Data, Raw.Genesis_Prime),
      Genesis_Root_Count => W.Decode (Data, Raw.Genesis_Root_Count),
      Phase => K.Journal_Phase'Val (Raw.Phase))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result = (Current => W.Decode (Data, Raw.Current),
      Current_Epoch => W.Decode (Data, Raw.Current_Epoch),
      Retained => W.Decode (Data, Raw.Retained),
      Current_Universe_Head => W.Decode (Data, Raw.Current_Universe_Head),
      Current_Ledger_Head => W.Decode (Data, Raw.Current_Ledger_Head),
      Intent => W.Decode (Data, Raw.Intent),
      Dispatch => W.Decode (Data, Raw.Dispatch),
      Observation_Head => W.Decode (Data, Raw.Observation_Head),
      Actual_Unit => W.Decode (Data, Raw.Actual_Unit),
      Cgroup => W.Decode (Data, Raw.Cgroup),
      Invocation => W.Decode (Data, Raw.Invocation),
      Namespace => W.Decode (Data, Raw.Namespace),
      Held_Namespace => W.Decode (Data, Raw.Held_Namespace),
      Peer => W.Decode (Data, Raw.Peer),
      Held_Peer => W.Decode (Data, Raw.Held_Peer),
      Helper_Image => W.Decode (Data, Raw.Helper_Image),
      Expected_Helper_Image => W.Decode (Data, Raw.Expected_Helper_Image),
      Challenge => W.Decode (Data, Raw.Challenge),
      Held_Challenge => W.Decode (Data, Raw.Held_Challenge),
      Protocol => W.Decode (Data, Raw.Protocol),
      Closed_Event => W.Decode (Data, Raw.Closed_Event),
      Namespace_Wait => W.Decode (Data, Raw.Namespace_Wait),
      Helper_Wait => W.Decode (Data, Raw.Helper_Wait),
      Cgroup_Events => W.Decode (Data, Raw.Cgroup_Events),
      Cgroup_Type => W.Decode (Data, Raw.Cgroup_Type),
      Manager_Delegate => W.Decode (Data, Raw.Manager_Delegate),
      Cgroup_Owner => W.Decode (Data, Raw.Cgroup_Owner),
      Cgroup_Group_Write => W.Decode (Data, Raw.Cgroup_Group_Write),
      Cgroup_Other_Write => W.Decode (Data, Raw.Cgroup_Other_Write),
      Actual_Store_Genesis => W.Decode (Data, Raw.Actual_Store_Genesis),
      Actual_Store_Id => W.Decode (Data, Raw.Actual_Store_Id),
      Owner_Store_Genesis => W.Decode (Data, Raw.Owner_Store_Genesis),
      Owner_Store_Id => W.Decode (Data, Raw.Owner_Store_Id),
      Genesis_Universe => W.Decode (Data, Raw.Genesis_Universe),
      Genesis_Instance => W.Decode (Data, Raw.Genesis_Instance),
      Genesis_Context_Head => W.Decode (Data, Raw.Genesis_Context_Head),
      Genesis_Prime => W.Decode (Data, Raw.Genesis_Prime),
      Genesis_Root_Count => W.Decode (Data, Raw.Genesis_Root_Count),
      Phase => K.Journal_Phase'Val (Raw.Phase));
   function Current_Reference (Data : Q.Byte_Array; Raw : Raw_Input) return Boolean is
     (W.Well_Formed (Data, Raw.State) and then Well_Formed (Data, Raw.Captured)
      and then K.Current_Reference (Data, W.Decode (Data, Raw.State), Decode (Data, Raw.Captured)))
   with Ghost, Global => null;
   function Current (Data : Q.Byte_Array; Raw : Raw_Input) return Boolean
   with Global => null, Post => Current'Result = Current_Reference (Data, Raw);
   function Genesis_Reference (Data : Q.Byte_Array; Raw : Raw_Input) return Boolean is
     (W.Well_Formed (Data, Raw.State) and then Well_Formed (Data, Raw.Captured)
      and then K.Genesis_Reference (Data, W.Decode (Data, Raw.State), Decode (Data, Raw.Captured)))
   with Ghost, Global => null;
   function Genesis_Current (Data : Q.Byte_Array; Raw : Raw_Input) return Boolean
   with Global => null, Post => Genesis_Current'Result = Genesis_Reference (Data, Raw);
   function Reference (Data : Q.Byte_Array; Raw : Raw_Input) return L.Liveness is
     (if not W.Well_Formed (Data, Raw.State) or else not W.Well_Formed (Data, Raw.Item)
        or else not Well_Formed (Data, Raw.Captured) then L.Unknown
      else K.Reference (Data, W.Decode (Data, Raw.State), W.Decode (Data, Raw.Item), Decode (Data, Raw.Captured)))
   with Ghost, Global => null;
   function Classify (Data : Q.Byte_Array; Raw : Raw_Input) return L.Liveness
   with Global => null, Post => Classify'Result = Reference (Data, Raw);
end Resource_Observation_Classification_Wire;
