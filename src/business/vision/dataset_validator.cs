using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Omni.Business.Vision
{
    public class DatasetResult<T>
    {
        public T Data { get; }
        public string Error { get; }
        public bool IsOk => Error == null;

        private DatasetResult(T data, string error)
        {
            Data = data;
            Error = error;
        }

        public static DatasetResult<T> Ok(T data) => new DatasetResult<T>(data, null);
        public static DatasetResult<T> Fail(string error) => new DatasetResult<T>(default, error);
    }

    public class DatasetManifest
    {
        public string BaseDirectory { get; set; }
        public int TotalImages { get; set; }
        public Dictionary<string, int> ClassDistribution { get; set; } = new Dictionary<string, int>();
        public bool IsValid { get; set; }
    }

    public class DatasetValidator
    {
        private readonly string[] _allowedExtensions = { ".jpg", ".jpeg", ".png", ".webp" };
        private readonly int _minImagesPerClass;

        public DatasetValidator(int minImagesPerClass = 10)
        {
            _minImagesPerClass = minImagesPerClass;
        }

        public DatasetResult<DatasetManifest> ValidateImageFolder(string directoryPath)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(directoryPath))
                    return DatasetResult<DatasetManifest>.Fail("Directory path cannot be empty.");

                // In zero-mock production, we check actual paths. Using system boundary checks.
                if (!Directory.Exists(directoryPath))
                    return DatasetResult<DatasetManifest>.Fail($"Directory not found: {directoryPath}");

                var manifest = new DatasetManifest { BaseDirectory = directoryPath };
                var classDirs = Directory.GetDirectories(directoryPath);

                if (classDirs.Length < 2)
                    return DatasetResult<DatasetManifest>.Fail("Dataset must contain at least two class directories for classification.");

                foreach (var classDir in classDirs)
                {
                    var className = new DirectoryInfo(classDir).Name;
                    var imageFiles = Directory.GetFiles(classDir)
                        .Where(f => _allowedExtensions.Contains(Path.GetExtension(f).ToLower()))
                        .ToList();

                    if (imageFiles.Count < _minImagesPerClass)
                    {
                        return DatasetResult<DatasetManifest>.Fail($"Class '{className}' has insufficient images ({imageFiles.Count} < {_minImagesPerClass}).");
                    }

                    manifest.ClassDistribution[className] = imageFiles.Count;
                    manifest.TotalImages += imageFiles.Count;
                }

                // Business logic: check for severe class imbalance (> 1:10 ratio)
                int maxClass = manifest.ClassDistribution.Values.Max();
                int minClass = manifest.ClassDistribution.Values.Min();
                
                if (maxClass > minClass * 10)
                {
                    return DatasetResult<DatasetManifest>.Fail("Severe class imbalance detected. Max class is 10x larger than min class.");
                }

                manifest.IsValid = true;
                return DatasetResult<DatasetManifest>.Ok(manifest);
            }
            catch (Exception ex)
            {
                return DatasetResult<DatasetManifest>.Fail($"Dataset validation exception: {ex.Message}");
            }
        }
    }
}
