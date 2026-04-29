using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Business.Spatial
{
    public class Result<T, E>
    {
        public bool IsSuccess { get; }
        public T Value { get; }
        public E Error { get; }

        private Result(bool isSuccess, T value, E error)
        {
            IsSuccess = isSuccess;
            Value = value;
            Error = error;
        }

        public static Result<T, E> Ok(T value) => new Result<T, E>(true, value, default);
        public static Result<T, E> Err(E error) => new Result<T, E>(false, default, error);
    }

    public struct Point
    {
        public double Lat { get; }
        public double Lon { get; }
        public Point(double lat, double lon) { Lat = lat; Lon = lon; }
    }

    public class Polygon
    {
        public string Id { get; }
        public List<Point> Vertices { get; }

        public Polygon(string id, List<Point> vertices)
        {
            Id = id;
            Vertices = vertices;
        }

        // Ray-casting algorithm to determine if point is inside polygon
        public bool Contains(Point p)
        {
            if (Vertices == null || Vertices.Count < 3) return false;
            
            bool inside = false;
            for (int i = 0, j = Vertices.Count - 1; i < Vertices.Count; j = i++)
            {
                if (((Vertices[i].Lon > p.Lon) != (Vertices[j].Lon > p.Lon)) &&
                    (p.Lat < (Vertices[j].Lat - Vertices[i].Lat) * (p.Lon - Vertices[i].Lon) / (Vertices[j].Lon - Vertices[i].Lon) + Vertices[i].Lat))
                {
                    inside = !inside;
                }
            }
            return inside;
        }
    }

    public class GeofenceEngine
    {
        private readonly List<Polygon> _geofences = new();

        public void AddGeofence(Polygon p)
        {
            _geofences.Add(p);
        }

        public Result<List<string>, string> Evaluate(double lat, double lon)
        {
            try
            {
                var pt = new Point(lat, lon);
                var activeFences = _geofences
                    .Where(g => g.Contains(pt))
                    .Select(g => g.Id)
                    .ToList();
                    
                return Result<List<string>, string>.Ok(activeFences);
            }
            catch (Exception ex)
            {
                return Result<List<string>, string>.Err($"Geofence evaluation failed: {ex.Message}");
            }
        }
    }
}
