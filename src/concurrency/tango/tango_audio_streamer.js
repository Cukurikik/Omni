class OmniResult { constructor(i,v,e){this.isOk=i;this.value=v;this.error=e;} }
class TangoAudioStreamer {
    constructor(){this.MAX_STREAMS=1000;this.streams=new Map();}
    startStream(id){
        if(this.streams.size>=this.MAX_STREAMS) return new OmniResult(false,null,new Error("Stream limit"));
        this.streams.set(id,{chunks:[],active:true});
        return new OmniResult(true,id,null);
    }
    pushChunk(id,chunk){
        const s=this.streams.get(id);
        if(!s||!s.active) return new OmniResult(false,null,new Error("No stream"));
        if(chunk.length>1048576) return new OmniResult(false,null,new Error("Chunk >1MB"));
        s.chunks.push(chunk);
        return new OmniResult(true,s.chunks.length,null);
    }
    endStream(id){this.streams.delete(id);return new OmniResult(true,true,null);}
}
module.exports={TangoAudioStreamer,OmniResult};
