/* Start hidden offline tools only when their existing panel is opened. */
(() => {
 'use strict';
 let ready=document.readyState==='complete';const pending=[];
 const visible=id=>{const el=document.getElementById(id);return el&&!el.hidden&&el.getClientRects().length>0;};
 function check(){if(!ready)return;for(const item of pending){if(!item.started&&item.ids.some(visible)){item.started=true;try{Promise.resolve(item.start()).catch(error=>console.error('Panel startup:',error));}catch(error){console.error('Panel startup:',error);}}}}
 window.FlyVisStartup={onPanel(ids,start){pending.push({ids:Array.isArray(ids)?ids:[ids],start,started:false});if(ready)check();}};
 document.addEventListener('DOMContentLoaded',()=>{ready=true;check();},{once:true});
 window.addEventListener('flyvis-workspace',check);
 document.addEventListener('toggle',check,true);
})();
