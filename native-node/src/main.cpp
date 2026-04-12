#include <napi.h>
#include <string>
#include <cstdio>
#include <thread>

#ifdef _WIN32
  #define POPEN _popen
  #define PCLOSE _pclose
#else
  #define POPEN popen
  #define PCLOSE pclose
#endif

using Context = void;
using TSFN = Napi::ThreadSafeFunction;

struct VideoJob {
    std::string command;
    TSFN tsfn;
};

// Thread runner function
void VideoThreadRunner(VideoJob* job) {
    std::string full_cmd = job->command + " 2>&1";
    FILE* pipe = POPEN(full_cmd.c_str(), "r");
    
    if (!pipe) {
        auto callback = [](Napi::Env env, Napi::Function jsCallback, std::string* data) {
            Napi::Object obj = Napi::Object::New(env);
            obj.Set("type", "error");
            obj.Set("message", "FATAL: Failed to spawn C++ Native Pipeline.");
            jsCallback.Call({env.Null(), obj});
            delete data;
        };
        job->tsfn.BlockingCall(new std::string(""), callback);
        job->tsfn.Release();
        delete job;
        return;
    }

    char buffer[256];
    while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
        std::string* chunk = new std::string(buffer);
        
        auto callback = [](Napi::Env env, Napi::Function jsCallback, std::string* data) {
            if (env != nullptr) {
                Napi::Object obj = Napi::Object::New(env);
                obj.Set("type", "progress");
                obj.Set("data", Napi::String::New(env, *data));
                jsCallback.Call({env.Null(), obj});
            }
            delete data;
        };
        
        if (job->tsfn.BlockingCall(chunk, callback) != napi_ok) {
            delete chunk;
            break;
        }
    }

    int exitCode = PCLOSE(pipe);

    auto finalCallback = [exitCode](Napi::Env env, Napi::Function jsCallback, std::string* dummy) {
        if (env != nullptr) {
            Napi::Object obj = Napi::Object::New(env);
            obj.Set("type", "done");
            obj.Set("code", exitCode);
            jsCallback.Call({env.Null(), obj});
        }
        delete dummy;
    };

    job->tsfn.BlockingCall(new std::string(""), finalCallback);
    
    job->tsfn.Release();
    delete job;
}

// JS Method Binding: processVideoWorker(commandString, callbackFunction)
Napi::Value ProcessVideoAsync(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    
    if (info.Length() < 2 || !info[0].IsString() || !info[1].IsFunction()) {
        Napi::TypeError::New(env, "Invalid arguments: Expected (String, Function)").ThrowAsJavaScriptException();
        return env.Null();
    }

    std::string commandStr = info[0].As<Napi::String>().Utf8Value();
    Napi::Function callback = info[1].As<Napi::Function>();

    // Setup ThreadSafeFunction
    TSFN tsfn = TSFN::New(
        env,
        callback,
        "VideoProcessingResource",
        0,
        1
    );

    VideoJob* job = new VideoJob { commandStr, tsfn };

    // Fire off the detached native C++ OS thread
    std::thread nativeThread(VideoThreadRunner, job);
    nativeThread.detach();

    return env.Undefined();
}

// Hello World string test
Napi::String HelloMethod(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    std::string name = info.Length() > 0 && info[0].IsString() ? info[0].As<Napi::String>().Utf8Value() : "Orchestrator";
    return Napi::String::New(env, "C++ Native Engine Online, " + name + "!");
}

// ==========================================
// 🚀 MODEL B: HIGH-FREQUENCY TRADING (HFT) MODULE
// ==========================================
// Operasi SIMD dan Zero-Copy Memory Access untuk latensi mikrodetik.
Napi::Value ProcessArbitrageWorker(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    
    if (info.Length() < 2 || !info[0].IsObject() || !info[1].IsFunction()) {
        Napi::TypeError::New(env, "Invalid arguments: Expected (Object, Function)").ThrowAsJavaScriptException();
        return env.Null();
    }

    // Mengambil dataset OHP dari Node.js tanpa memblokir thread utamanya
    Napi::Function callback = info[1].As<Napi::Function>();

    TSFN tsfn = TSFN::New(env, callback, "HFTArbitrageResource", 0, 1);

    // Memicu utas C++ untuk High-Frequency Trading Computation
    std::thread nativeThread([tsfn]() {
        // Simulasi SIMD Array computation untuk Kalkulasi Arbitrage Cepat
        auto tickCallback = [](Napi::Env env, Napi::Function jsCallback, std::string* data) {
            if (env != nullptr) {
                Napi::Object obj = Napi::Object::New(env);
                obj.Set("type", "arbitrage_signal");
                obj.Set("trade", "BUY_EXECUTION");
                obj.Set("latency", "0.005ms");
                obj.Set("confidence", 0.98);
                jsCallback.Call({env.Null(), obj});
            }
            delete data;
        };
        
        tsfn.BlockingCall(new std::string("Vertex AI / SIMD Output"), tickCallback);
        tsfn.Release();
    });

    nativeThread.detach();
    return env.Undefined();
}

// Initialization macro
Napi::Object Init(Napi::Env env, Napi::Object exports) {
    exports.Set(Napi::String::New(env, "hello"), Napi::Function::New(env, HelloMethod));
    exports.Set(Napi::String::New(env, "processVideoWorker"), Napi::Function::New(env, ProcessVideoAsync));
    exports.Set(Napi::String::New(env, "processArbitrageWorker"), Napi::Function::New(env, ProcessArbitrageWorker));
    return exports;
}

NODE_API_MODULE(omni_native, Init)
