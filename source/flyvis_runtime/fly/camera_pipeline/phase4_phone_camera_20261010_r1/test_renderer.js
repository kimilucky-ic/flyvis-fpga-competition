// Offline VM harness for our own renderer, not browser automation or camera data.
"use strict";
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const defaults={family:'edge',polarity:'OFF',direction_deg:0,speed_px_s:160,active_s:2,pre_s:1,post_s:1,dot_radius_px:24,flicker_hz:1,gradient_period_px:640,dot_control:'automatic'};
const fields={family:'edge',polarity:'OFF',direction:'0',speed:'160',duration:'2',radius:'24',frequency:'1',period:'640',dotControl:'automatic'};
let lastImage=null,lastArc=null,lastFill=null;
const ctx={fillStyle:'',fillRect(){lastFill=this.fillStyle;},createImageData(w,h){return {data:new Uint8ClampedArray(w*h*4)};},
 putImageData(image){lastImage=image.data;},beginPath(){},arc(x,y,r){lastArc={x,y,r};},fill(){},strokeRect(){}};
const elements=new Map();for(const id of [...Object.keys(fields),'stimulus','stage','status','session','start','standby','exitStage','stop','arm','calibrate'])elements.set(id,{value:fields[id],disabled:false,addEventListener(){},getContext(){return ctx;}});
const sandbox={URLSearchParams,location:{search:'?token=offline-test'},document:{getElementById:id=>elements.get(id),querySelectorAll:()=>[],addEventListener(){}},
 performance:{now:()=>0},window:{addEventListener(){}},setInterval(){},requestAnimationFrame(){},console,Uint8ClampedArray};
vm.createContext(sandbox);vm.runInContext(fs.readFileSync(path.join(__dirname,'web/player.js'),'utf8'),sandbox);
let tests=0;const details=[];
for(const polarity of ['OFF','ON'])for(const degrees of [0,45,90,135,180,225,270,315]){
 const spec={...defaults,polarity,direction_deg:degrees},angle=degrees*Math.PI/180;
 const minus=[Math.round(320-40*Math.cos(angle)),Math.round(320-40*Math.sin(angle))],plus=[Math.round(320+40*Math.cos(angle)),Math.round(320+40*Math.sin(angle))];
 sandbox.render(spec,1.8);let a=[lastImage[4*(minus[1]*640+minus[0])],lastImage[4*(plus[1]*640+plus[0])]];
 sandbox.render(spec,2.3);let b=[lastImage[4*(minus[1]*640+minus[0])],lastImage[4*(plus[1]*640+plus[0])]];
 const before=polarity==='OFF'?255:0,after=255-before;
 assert.deepEqual(a,[after,before]);assert.deepEqual(b,[after,after]);
 details.push({family:'edge',polarity,direction_deg:degrees,early_samples:a,later_samples:b,status:'PASS'});tests++;
}
for(const degrees of [0,90,180,270]){
 sandbox.render({...defaults,family:'dot',direction_deg:degrees},1.5);const a={...lastArc};sandbox.render({...defaults,family:'dot',direction_deg:degrees},2.5);const b={...lastArc};
 assert.ok(Math.abs((b.x-a.x)-160*Math.cos(degrees*Math.PI/180))<1e-10);assert.ok(Math.abs((b.y-a.y)-160*Math.sin(degrees*Math.PI/180))<1e-10);tests++;
 details.push({family:'dot',direction_deg:degrees,start:a,end:b,status:'PASS'});
}
sandbox.render({...defaults,family:'flicker'},1);assert.equal(lastFill,'black');sandbox.render({...defaults,family:'flicker'},1.6);assert.equal(lastFill,'white');tests++;
sandbox.render({...defaults,family:'fade'},1);assert.equal(lastFill,'rgb(0,0,0)');sandbox.render({...defaults,family:'fade'},2);assert.equal(lastFill,'rgb(255,255,255)');sandbox.render({...defaults,family:'fade'},3);assert.equal(lastFill,'rgb(0,0,0)');tests++;
sandbox.render({...defaults,family:'gradient'},1.5);const gradient=new Uint8ClampedArray(lastImage);sandbox.render({...defaults,family:'gradient'},2.5);assert.notDeepEqual(lastImage,gradient);tests++;
console.log(JSON.stringify({schema:'phase4-renderer-offline-validation-v1',status:'PASS',tests,details,
 evidence:'actual execution of own JavaScript renderer in VM with mock canvas; not optical screen/camera/neural test',
 camera_opened:false,gpu_used:false,board_used:false},null,2));
