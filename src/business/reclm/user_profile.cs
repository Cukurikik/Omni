namespace Omni.RecLM {
    public class UserProfile {
        public string UserId { get; set; }
        public string[] History { get; set; }

        public UserProfile(string userId, string[] history) {
            UserId = userId;
            History = history;
        }
    }
}
