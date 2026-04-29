class OmniResult{constructor(i,v,e){this.isOk=i;this.value=v;this.error=e;}}
class LangkitMonitor{
    constructor(){this.MAX_METRICS=50000;this.metrics=[];this.alertThresholds=new Map();}
    recordMetric(name,value){
        if(this.metrics.length>=this.MAX_METRICS)return new OmniResult(false,null,new Error("Metric buffer full"));
        if(typeof value!=='number'||isNaN(value))return new OmniResult(false,null,new Error("Invalid metric value"));
        this.metrics.push({name,value,ts:Date.now()});
        const threshold=this.alertThresholds.get(name);
        if(threshold&&value>threshold)return new OmniResult(true,{alert:true,name,value},null);
        return new OmniResult(true,{alert:false,name,value},null);
    }
    setThreshold(name,val){this.alertThresholds.set(name,val);return new OmniResult(true,true,null);}
}
module.exports={LangkitMonitor,OmniResult};
