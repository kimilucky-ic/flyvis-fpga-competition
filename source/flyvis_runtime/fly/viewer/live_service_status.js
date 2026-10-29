/* Status wording shared by both live controls; never starts computation. */
(() => {
 'use strict';
 window.FlyVisServiceStatus = info => {
  if(info.status==='CONNECTED')return {state:'READY',ready:true,terminal:false,message:'GPU 已就绪；点击启动后才会采集和计算。'};
  if(info.service)return {...info.service,ready:false};
  // Older servers must never turn an unknown/disconnected state into an endless spinner.
  return {state:'DISCONNECTED',ready:false,terminal:true,message:'GPU 未连接：'+(info.error||info.status)+'。请查看本次日志；原离线演示仍可使用。'};
 };
})();
