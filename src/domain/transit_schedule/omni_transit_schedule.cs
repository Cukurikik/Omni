using System;
using System.Collections.Generic;
using System.Linq;

namespace OmniFramework.Domain.TransitSchedule
{
    // OMNI Transit Schedule Domain Engine — Domain Layer
    // Absorbing itinero/transit business logic for schedule management.

    public class TransitResult<T>
    {
        public bool IsOk { get; }
        public T Value { get; }
        public string Error { get; }
        private TransitResult(bool ok, T value, string error) { IsOk = ok; Value = value; Error = error; }
        public static TransitResult<T> Ok(T value) => new TransitResult<T>(true, value, null);
        public static TransitResult<T> Fail(string error) => new TransitResult<T>(false, default, error);
    }

    public class ScheduleEntry
    {
        public string RouteId { get; set; }
        public string StopId { get; set; }
        public TimeSpan DepartureTime { get; set; }
        public TimeSpan ArrivalTime { get; set; }
        public string Mode { get; set; }
    }

    public class OmniTransitScheduleEngine
    {
        private readonly List<ScheduleEntry> _schedule = new List<ScheduleEntry>();
        private int _lookups;

        public TransitResult<bool> AddEntry(string routeId, string stopId, TimeSpan departure, TimeSpan arrival, string mode)
        {
            if (string.IsNullOrWhiteSpace(routeId) || string.IsNullOrWhiteSpace(stopId))
                return TransitResult<bool>.Fail("ScheduleError: Route/stop ID required");
            if (arrival < departure)
                return TransitResult<bool>.Fail("ScheduleError: Arrival before departure");
            _schedule.Add(new ScheduleEntry { RouteId = routeId, StopId = stopId, DepartureTime = departure, ArrivalTime = arrival, Mode = mode });
            return TransitResult<bool>.Ok(true);
        }

        public TransitResult<List<ScheduleEntry>> FindDepartures(string stopId, TimeSpan after)
        {
            _lookups++;
            var results = _schedule.Where(e => e.StopId == stopId && e.DepartureTime >= after)
                                   .OrderBy(e => e.DepartureTime).ToList();
            return TransitResult<List<ScheduleEntry>>.Ok(results);
        }

        public Dictionary<string, object> Diagnostics()
        {
            return new Dictionary<string, object> {
                {"engine", "OmniTransitScheduleEngine"}, {"entries", _schedule.Count},
                {"lookups", _lookups}, {"status", "Operational"}
            };
        }
    }
}
