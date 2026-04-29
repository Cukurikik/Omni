package dev.omni.events.pedalboard;

import java.io.InputStream;
import java.io.OutputStream;

public class AudioEffectStream {
    
    // Low latency stream wrapper connecting to C++ Pedalboard engine via JNI/FFI
    public void processStream(InputStream inStream, OutputStream outStream) throws Exception {
        byte[] buffer = new byte[1024];
        int bytesRead;
        while ((bytesRead = inStream.read(buffer)) != -1) {
            // FFI call to C++ Pedalboard DistortionProcessor
            byte[] processed = applyCppPedalboard(buffer, bytesRead);
            outStream.write(processed, 0, bytesRead);
        }
    }

    private native byte[] applyCppPedalboard(byte[] input, int len);
}
