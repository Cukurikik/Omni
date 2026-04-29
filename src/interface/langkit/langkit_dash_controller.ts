interface OmniResult<T>{isOk:boolean;value:T|null;error:string|null;}
interface LangkitMetric{name:string;value:number;ts:number;}
class LangkitDashController{
    private metrics:LangkitMetric[]=[];
    private readonly MAX=10000;
    addMetric(name:string,value:number):OmniResult<number>{
        if(this.metrics.length>=this.MAX)return{isOk:false,value:null,error:"Buffer full"};
        if(isNaN(value))return{isOk:false,value:null,error:"NaN value"};
        this.metrics.push({name,value,ts:Date.now()});
        return{isOk:true,value:this.metrics.length,error:null};
    }
    getRecent(count:number):OmniResult<LangkitMetric[]>{
        if(count<=0)return{isOk:false,value:null,error:"Count must be positive"};
        return{isOk:true,value:this.metrics.slice(-count),error:null};
    }
}
export{LangkitDashController};
