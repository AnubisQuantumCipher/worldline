with Resource_Actor_Admission_Wire;
with Worldline.Operation_Authority_Wire;
with Worldline.Resource_Actor_Execution;
package Worldline.Resource_Actor_Execution_Wire with SPARK_Mode is
   pragma Elaborate_Body;
   package E renames Worldline.Resource_Actor_Execution;
   package D renames Resource_Actor_Admission_Wire;
   package N renames D.N;
   package W renames N.W;
   package Q renames N.Q;
   package T renames Worldline.Operation_Authority_Wire;
   type Raw_Crosswalk is record
      Resource_Current : N.Raw_Current_Observation;
      Operation_Policy : T.C.Raw_Digest;
      Operation_Root_Set : T.C.Raw_Digest;
      Owner_Genesis : W.Raw_Id;
      Installation : W.Raw_Id;
      Gate_Config : W.Raw_Id;
      Managed_Observation : W.Raw_Id;
      Original_Grant : W.Raw_Id;
      Complete_Crosswalk : W.Raw_Id;
      Current_Source : W.Raw_Id;
      Original_Request : W.Raw_Id;
      Original_Requester : W.Raw_Id;
      Original_Transaction : W.Raw_Id;
      Preparer : W.Raw_Id;
      Selected_Plan : W.Raw_Id;
   end record with Convention => C;
   function Well_Formed (Data : Q.Byte_Array; V : Raw_Crosswalk) return Boolean is
     (N.Well_Formed (Data, V.Resource_Current)
      and then T.C.Well_Formed (V.Operation_Policy) and then T.C.Well_Formed (V.Operation_Root_Set)
      and then W.Well_Formed (Data, V.Owner_Genesis)
      and then W.Well_Formed (Data, V.Installation)
      and then W.Well_Formed (Data, V.Gate_Config)
      and then W.Well_Formed (Data, V.Managed_Observation)
      and then W.Well_Formed (Data, V.Original_Grant)
      and then W.Well_Formed (Data, V.Complete_Crosswalk)
      and then W.Well_Formed (Data, V.Current_Source)
      and then W.Well_Formed (Data, V.Original_Request)
      and then W.Well_Formed (Data, V.Original_Requester)
      and then W.Well_Formed (Data, V.Original_Transaction)
      and then W.Well_Formed (Data, V.Preparer)
      and then W.Well_Formed (Data, V.Selected_Plan)
     ) with Global => null;
   function Decode (Data : Q.Byte_Array; V : Raw_Crosswalk) return E.Crosswalk is
     (Resource_Current => N.Decode (Data, V.Resource_Current),
      Operation_Policy => T.C.Decode (V.Operation_Policy),
      Operation_Root_Set => T.C.Decode (V.Operation_Root_Set),
      Owner_Genesis => W.Decode (Data, V.Owner_Genesis),
      Installation => W.Decode (Data, V.Installation),
      Gate_Config => W.Decode (Data, V.Gate_Config),
      Managed_Observation => W.Decode (Data, V.Managed_Observation),
      Original_Grant => W.Decode (Data, V.Original_Grant),
      Complete_Crosswalk => W.Decode (Data, V.Complete_Crosswalk),
      Current_Source => W.Decode (Data, V.Current_Source),
      Original_Request => W.Decode (Data, V.Original_Request),
      Original_Requester => W.Decode (Data, V.Original_Requester),
      Original_Transaction => W.Decode (Data, V.Original_Transaction),
      Preparer => W.Decode (Data, V.Preparer),
      Selected_Plan => W.Decode (Data, V.Selected_Plan) ) with Global => null, Pre => Well_Formed (Data, V);
end Worldline.Resource_Actor_Execution_Wire;
