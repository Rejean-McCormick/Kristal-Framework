export function referenceV9Capabilities(){
 return {
  schema_version:'9.0', artifact_type:'kristal_v9_capabilities',
  compatibility:{reads:['kristal_state/6.0','kristall/7.0','kristall/8.0','kristal.state/9.0'],portable_state:'kristal_state/6.0',semantic_baseline:'kristall/7.0',query_baseline:'kristall/8.0'},
  capabilities:{
   state_architecture:{logical_artifacts:true,immutable_snapshots:true,logical_commitments:true,external_pinned_references:true},
   materialization:{profiles:['kristal.materialization/inline-json/1','kristal.materialization/segmented-jsonl/1','kristal.materialization/kristal-state-v6/1'],multiple_representations:true,segmentation:true,factorization:true},
   lifecycle:{build_publish_activate:true,atomic_activation:true,rollback:true}
  }
 };
}

export function verifyV9Capabilities(doc){
 const issues=[];
 if(!doc||typeof doc!=='object'||Array.isArray(doc))return{ok:false,issues:[{path:'$',message:'capabilities must be object'}]};
 if(doc.schema_version!=='9.0')issues.push({path:'$.schema_version',message:'expected 9.0'});
 if(doc.artifact_type!=='kristal_v9_capabilities')issues.push({path:'$.artifact_type',message:'expected kristal_v9_capabilities'});
 const reads=new Set(doc.compatibility?.reads??[]);
 for(const id of ['kristal_state/6.0','kristall/7.0','kristall/8.0','kristal.state/9.0'])if(!reads.has(id))issues.push({path:'$.compatibility.reads',message:`missing ${id}`});
 if(doc.capabilities?.state_architecture?.logical_artifacts!==true)issues.push({path:'$.capabilities.state_architecture.logical_artifacts',message:'logical_artifacts must be true'});
 return{ok:issues.length===0,issues};
}
