import { SUPPORTED_QUERY_MODES } from './query.mjs';

export function referenceV8Capabilities(){
  return {
    schema_version:'8.0',artifact_type:'kristall_v8_capabilities',
    compatibility:{reads:['kristal_state/6.0','kristall/7.0','kristall/8.0'],portable_state:'kristal_state/6.0',semantic_baseline:'kristall/7.0'},
    capabilities:{
      language:{protocol:'kristal-language/1.0',bcp47:true,max_stack_layers:64},
      ai_query:{protocol:'kristal-query/1.0',modes:[...SUPPORTED_QUERY_MODES].sort(),encodings:['expanded_json','symbol_table_v1'],pagination:true,federation:false,semantic_fingerprints:true},
    },
  };
}
