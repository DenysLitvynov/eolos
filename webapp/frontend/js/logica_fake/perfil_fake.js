// /js/logica_fake/perfil_fake.js
// 用 localStorage 模拟后端。字段对齐数据库：usuario_id, nombre, apellido, correo, targeta_id, (fecha 可选)

class PerfilFake {
    constructor(prefix='perfil_'){ this.prefix = prefix; this._initSample(); }
    _k(uid){ return `${this.prefix}${uid}`; }

    _initSample(){
        const uid = localStorage.getItem('usuario_id') || 'guest';
        const k = this._k(uid);
        if(!localStorage.getItem(k)){
            localStorage.setItem(k, JSON.stringify({
                usuario_id: uid,
                nombre: 'Juan',
                apellido: 'Pérez',
                correo: 'juanba@gmail.com',
                targeta_id: '12345HDC',
                fecha: '1990-01-01'
            }));
        }
    }
    _delay(ms=80){ return new Promise(r=>setTimeout(r,ms)); }

    async ensureSeed(uid){
        await this._delay();
        const k = this._k(uid);
        if(!localStorage.getItem(k)){
            localStorage.setItem(k, JSON.stringify({
                usuario_id: uid, nombre:'', apellido:'', correo:'', targeta_id:'', fecha:'1990-01-01'
            }));
        }
    }

    async obtenerPerfil(uid){
        await this._delay();
        if(uid==null) throw new Error('usuario_id requerido');
        const raw = localStorage.getItem(this._k(uid));
        try{ return raw? JSON.parse(raw): null; }catch{ return null; }
    }

    async actualizarPerfil(uid, datos){
        await this._delay();
        if(uid==null) throw new Error('usuario_id requerido');
        const k = this._k(uid);
        const base = (()=>{ try{ return JSON.parse(localStorage.getItem(k)||'{}'); }catch{ return {}; }})();
        const allowed = ['nombre','apellido','correo','targeta_id','fecha','contrasena']; // contrasena 只做占位
        for(const a of allowed){ if(a in datos){ if(a==='contrasena' && !datos[a]) continue; base[a]=datos[a]; } }
        base.usuario_id = uid;
        localStorage.setItem(k, JSON.stringify(base));
        return base;
    }

    async borrarPerfil(uid){
        await this._delay(); localStorage.removeItem(this._k(uid)); return true;
    }
}

window.PerfilFake = PerfilFake;
