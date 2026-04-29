class OmniResult<T>{final bool isOk;final T? value;final String? error;OmniResult({required this.isOk,this.value,this.error});}
class VideoPlayerDash{
  final int maxFrames=10000;
  OmniResult<Map<String,dynamic>> loadVideo(int totalFrames,int sampledFrames,double durationSec){
    if(totalFrames<=0)return OmniResult(isOk:false,error:"Zero frames");
    if(totalFrames>maxFrames)return OmniResult(isOk:false,error:"Frames exceed $maxFrames");
    if(durationSec<=0||durationSec>3600)return OmniResult(isOk:false,error:"Duration must be (0,3600]s");
    return OmniResult(isOk:true,value:{"total":totalFrames,"sampled":sampledFrames,"fps":totalFrames/durationSec});
  }
}
