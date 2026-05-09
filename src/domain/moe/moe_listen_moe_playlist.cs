// moe_listen_moe_playlist.cs — Domain
// Layer: Domain — LISTEN.moe Playlist Management
// Inspired by: LISTEN.moe-html (Anime Radio)

using System;
using System.Collections.Generic;

namespace Omni.Domain.MoE
{
    public class Track
    {
        public int Id { get; set; }
        public string Title { get; set; }
        public string AnimeSource { get; set; }
        public int DurationSeconds { get; set; }
    }

    public class RadioPlaylist
    {
        public Guid StationId { get; private set; }
        private Queue<Track> _upcomingTracks;
        private Track _currentlyPlaying;

        public RadioPlaylist()
        {
            StationId = Guid.NewGuid();
            _upcomingTracks = new Queue<Track>();
        }

        public void EnqueueTrack(Track track)
        {
            if (track == null) throw new ArgumentNullException(nameof(track));
            _upcomingTracks.Enqueue(track);
        }

        public Track PopNext()
        {
            if (_upcomingTracks.Count == 0)
            {
                throw new InvalidOperationException("Playlist is empty. Fallback required.");
            }
            
            _currentlyPlaying = _upcomingTracks.Dequeue();
            return _currentlyPlaying;
        }

        public Track GetCurrent() => _currentlyPlaying;
        public int QueueLength => _upcomingTracks.Count;
    }
}
