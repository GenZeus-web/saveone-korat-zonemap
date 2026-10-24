// ส่งฉากผังใหญ่ (W3.S) ออกเป็น GLB ให้ Blender เรนเดอร์ภาพนิ่ง
// ใช้: เปิดผังผ่าน python blender/recv.py (พอร์ต 8791) แล้วในคอนโซล: await exportScene('market')
// ของซ้ำ (InstancedMesh) แตกเป็นชิ้นจริงแล้วรวมตามสี เพราะ GLTFExporter r128 ส่ง instance ไม่ได้
(function(){
  const load=src=>new Promise((ok,no)=>{ const s=document.createElement('script'); s.src=src; s.onload=ok; s.onerror=no; document.head.appendChild(s); });
  const CDN='https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/';
  window.exportScene=async function(name){
    if(!THREE.GLTFExporter) await load(CDN+'exporters/GLTFExporter.js');
    if(!THREE.BufferGeometryUtils) await load(CDN+'utils/BufferGeometryUtils.js');
    const T=THREE, S=W3.S, out=new T.Scene(), m4=new T.Matrix4(), col=new T.Color();
    S.updateMatrixWorld(true);
    let tris=0;
    const prep=g=>{ g=g.index?g.toNonIndexed():g.clone(); for(const k of Object.keys(g.attributes)) if(!['position','normal','uv'].includes(k)) g.deleteAttribute(k); if(!g.attributes.uv) g.setAttribute('uv',new T.BufferAttribute(new Float32Array(g.attributes.position.count*2),2)); return g; };
    const visible=o=>{ for(let p=o;p;p=p.parent) if(!p.visible) return false; return true; };
    S.traverse(o=>{
      if(!o.isMesh||!visible(o)) return;
      if(o.isInstancedMesh){
        const by={};
        for(let i=0;i<o.count;i++){ o.getMatrixAt(i,m4); m4.premultiply(o.matrixWorld);
          let key='-'; if(o.instanceColor){ col.fromArray(o.instanceColor.array,i*3); key=col.getHexString(); }
          const g=prep(o.geometry); g.applyMatrix4(m4); (by[key]=by[key]||[]).push(g); }
        for(const key in by){ const geo=T.BufferGeometryUtils.mergeBufferGeometries(by[key]); if(!geo) continue;
          const m=o.material.clone(); if(key!=='-') m.color.multiply(col.set('#'+key));
          const me=new T.Mesh(geo,m); me.name=o.name||'inst'; out.add(me); tris+=geo.attributes.position.count/3; }
      } else {
        const me=new T.Mesh(o.geometry,o.material); o.matrixWorld.decompose(me.position,me.quaternion,me.scale); me.name=o.name||'mesh'; out.add(me);
        tris+=(o.geometry.index?o.geometry.index.count:o.geometry.attributes.position.count)/3;
      }
    });
    const glb=await new Promise(ok=>new T.GLTFExporter().parse(out,ok,{binary:true,maxTextureSize:2048}));
    const sun=S.children.find(c=>c.isDirectionalLight), cam=W3.cam;
    const info={camPos:cam.position.toArray(),camTarget:W3.tgt?W3.tgt.toArray?W3.tgt.toArray():W3.tgt:null,camQuat:cam.quaternion.toArray(),fov:cam.fov,aspect:cam.aspect,
      sunDir:sun.position.clone().sub(sun.target.position).normalize().toArray(),sky:'#'+(S.background&&S.background.isColor?S.background.clone().convertLinearToSRGB().getHexString():'93b86f')};
    const post=(n,body)=>fetch('/save?name='+n,{method:'POST',body}).then(r=>r.text());
    return [await post(name+'.glb',glb), await post(name+'.json',JSON.stringify(info)), Math.round(tris)+' tris', out.children.length+' meshes'];
  };
})();
