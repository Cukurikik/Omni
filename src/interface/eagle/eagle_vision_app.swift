import Foundation
// @omni-domain Interface Layer (Eagle Vision App)
enum OmniResult<T,E:Error>{case ok(T);case err(E)}
enum EagleAppError:Error{case initFailed;case modelLoadFailed}
class EagleVisionApp{
    var modelLoaded=false
    func loadModel(path:String)->OmniResult<Bool,EagleAppError>{
        guard !path.isEmpty else{return .err(.modelLoadFailed)}
        modelLoaded=true;return .ok(true)
    }
    func classify(imageData:[Float])->OmniResult<String,EagleAppError>{
        guard modelLoaded else{return .err(.initFailed)}
        return .ok("eagle_class_prediction")
    }
}
