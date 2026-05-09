// @omni-layer Business | @omni-source sgrvinod/chess-transformers | @omni-lang C#
// @omni-description Chess tournament manager: DDD aggregate for tournament
// lifecycle, round-robin pairing, standings, and tiebreak computation.

namespace Omni.Business.Chess
{
    public enum TournamentStatus { Created, InProgress, Completed, Cancelled }
    public enum GameResult { WhiteWin, BlackWin, Draw, InProgress }

    public sealed class OmniResult<T>
    {
        public T Data { get; }
        public string Error { get; }
        public bool IsOk => Error == null;
        private OmniResult(T data, string error) { Data = data; Error = error; }
        public static OmniResult<T> Ok(T data) => new(data, null);
        public static OmniResult<T> Fail(string err) => new(default, err);
    }

    public class Player
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public double ELO { get; set; }
        public double Score { get; set; }
        public int GamesPlayed { get; set; }
    }

    public class Pairing
    {
        public int Round { get; set; }
        public string WhiteId { get; set; }
        public string BlackId { get; set; }
        public GameResult Result { get; set; } = GameResult.InProgress;
    }

    public class TournamentManager
    {
        private readonly Dictionary<string, Player> _players = new();
        private readonly List<Pairing> _pairings = new();
        private TournamentStatus _status = TournamentStatus.Created;
        private int _currentRound;

        public OmniResult<string> AddPlayer(string id, string name, double elo)
        {
            if (_status != TournamentStatus.Created)
                return OmniResult<string>.Fail("Tournament already started");
            _players[id] = new Player { Id = id, Name = name, ELO = elo };
            return OmniResult<string>.Ok($"Added {name} (ELO: {elo})");
        }

        public OmniResult<List<Pairing>> GenerateRoundRobin()
        {
            var ids = _players.Keys.ToList();
            if (ids.Count < 2) return OmniResult<List<Pairing>>.Fail("Need >= 2 players");
            _status = TournamentStatus.InProgress;
            int n = ids.Count;
            if (n % 2 != 0) ids.Add("BYE");
            int rounds = ids.Count - 1;
            for (int r = 0; r < rounds; r++)
            {
                for (int i = 0; i < ids.Count / 2; i++)
                {
                    string w = ids[i], b = ids[ids.Count - 1 - i];
                    if (w == "BYE" || b == "BYE") continue;
                    _pairings.Add(new Pairing { Round = r + 1, WhiteId = w, BlackId = b });
                }
                ids.Insert(1, ids[ids.Count - 1]);
                ids.RemoveAt(ids.Count - 1);
            }
            return OmniResult<List<Pairing>>.Ok(_pairings);
        }

        public OmniResult<Dictionary<string, double>> RecordResult(int round, string whiteId, GameResult result)
        {
            var pairing = _pairings.FirstOrDefault(p => p.Round == round && p.WhiteId == whiteId);
            if (pairing == null) return OmniResult<Dictionary<string, double>>.Fail("Pairing not found");
            pairing.Result = result;
            switch (result)
            {
                case GameResult.WhiteWin:
                    _players[whiteId].Score += 1; break;
                case GameResult.BlackWin:
                    _players[pairing.BlackId].Score += 1; break;
                case GameResult.Draw:
                    _players[whiteId].Score += 0.5;
                    _players[pairing.BlackId].Score += 0.5; break;
            }
            _players[whiteId].GamesPlayed++;
            _players[pairing.BlackId].GamesPlayed++;
            return OmniResult<Dictionary<string, double>>.Ok(
                _players.ToDictionary(p => p.Key, p => p.Value.Score));
        }

        public List<Player> Standings() =>
            _players.Values.OrderByDescending(p => p.Score)
                           .ThenByDescending(p => p.ELO).ToList();
    }
}
