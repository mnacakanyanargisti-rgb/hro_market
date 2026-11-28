// Load the catalog before React starts, with a safe fallback to original bundled data.
const cfg=window.STORE_CONFIG||{};
if(cfg.url&&cfg.key){
  try{
    const url=new URL('/rest/v1/catalog',cfg.url);url.searchParams.set('id','eq.1');url.searchParams.set('select','products');
    const response=await fetch(url,{headers:{apikey:cfg.key},signal:AbortSignal.timeout(5000),cache:'no-store'});
    if(!response.ok)throw Error('Catalog request failed');
    const rows=await response.json();
    if(Array.isArray(rows[0]?.products))window.HRO_CATALOG=rows[0].products;
  }catch(e){console.warn('Using original catalog:',e)}
}
const script=document.createElement('script');script.src='bundle.js';document.body.append(script);
