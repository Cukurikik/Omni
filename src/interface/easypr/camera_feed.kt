package dev.omni.easypr

import android.content.Context
import android.graphics.SurfaceTexture
import android.view.TextureView

class CameraFeedView(context: Context) : TextureView(context), TextureView.SurfaceTextureListener {
    init {
        surfaceTextureListener = this
    }

    override fun onSurfaceTextureAvailable(surface: SurfaceTexture, width: Int, height: Int) {
        // Start camera feed for license plate detection
    }

    override fun onSurfaceTextureSizeChanged(surface: SurfaceTexture, width: Int, height: Int) {}
    override fun onSurfaceTextureDestroyed(surface: SurfaceTexture): Boolean = true
    override fun onSurfaceTextureUpdated(surface: SurfaceTexture) {}
}
