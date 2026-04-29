class OmniResult<T>{final bool isOk;final T? value;final String? error;OmniResult({required this.isOk,this.value,this.error});}
class SophiaTrainingDash{
  final int maxSteps=1000000;
  OmniResult<Map<String,dynamic>> displayStep(int step,double loss,double lr,double hessianNorm){
    if(step<0)return OmniResult(isOk:false,error:"Negative step");
    if(step>maxSteps)return OmniResult(isOk:false,error:"Step exceeds $maxSteps");
    if(loss.isNaN||lr.isNaN)return OmniResult(isOk:false,error:"NaN in metrics");
    return OmniResult(isOk:true,value:{"step":step,"loss":loss,"lr":lr,"hessian_norm":hessianNorm});
  }
}
