package dev.omni.lab

import android.content.Context
import android.opengl.GLSurfaceView

class LabEnvView(context: Context) : GLSurfaceView(context) {
    init {
        setEGLContextClientVersion(2)
        // Set custom renderer for DeepMind Lab 3D environment
        // setRenderer(LabRenderer())
    }
}
