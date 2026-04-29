package dev.omniframework.tango
class OmniResult<T, E>(val isOk: Boolean, val value: T?, val error: E?)
class TangoPlayerUI {
    private val maxPlaylistSize = 500
    fun addToPlaylist(audioId: String): OmniResult<Boolean, String> {
        if (audioId.length > 256) return OmniResult(false, null, "Audio ID too long")
        return OmniResult(true, true, null)
    }
}
