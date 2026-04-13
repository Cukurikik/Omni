// ===========================================================================
// OMNI THERMAL THROTTLE (SWIFT / NATIVE iOS)
// ===========================================================================
// Hanya Bahasa Native Swift yang mampu memanggil `ProcessInfo` API tertutup Apple.
// Jika iPhone Tuan Ikky memanas saat Model LLM diputar, script ini menahan OS.
// ===========================================================================

import UIKit
import Flutter

@UIApplicationMain
@objc class AppDelegate: FlutterAppDelegate {
  
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    
    let controller : FlutterViewController = window?.rootViewController as! FlutterViewController
    let thermalChannel = FlutterMethodChannel(name: "dev.omniframework.thermal/monitor",
                                              binaryMessenger: controller.binaryMessenger)
    
    thermalChannel.setMethodCallHandler({
      (call: FlutterMethodCall, result: @escaping FlutterResult) -> Void in
      
      if call.method == "getThermalState" {
        self.enforceHardwareSurvival(result: result)
      } else {
        result(FlutterMethodNotImplemented)
      }
    })
    
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
  
  /// Mengukur Suhu Semikonduktor Apple A-Series Bionic.
  private func enforceHardwareSurvival(result: FlutterResult) {
    let state = ProcessInfo.processInfo.thermalState
    
    switch state {
    case .nominal:
      print("[OMNI SWIFT Core] Suhu Sistem Dingin. Eksekusi Model LLM 8B Diizinkan.")
      result("NOMINAL")
    case .fair:
      print("[OMNI SWIFT Core] Pemanasan Ringan. Batasi Konteks Prompt 50%.")
      result("FAIR")
    case .serious:
      print("[OMNI SWIFT Core] \u26a0\ufe0f Ancaman Termal (Serious). Menghapus LLM Raksasa dari RAM...")
      result("THROTTLE_SERIOUS")
    case .critical:
      print("[OMNI SWIFT Core] \u26a0\ufe0f Bahaya Kritis (Critical). Membekukan Mesin OMNI secara asinkron!!!")
      result("THROTTLE_CRITICAL")
    @unknown default:
      result("UNKNOWN")
    }
  }
}
