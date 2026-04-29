using System;
using System.Collections.Generic;
using System.Linq;
using Omni.Core.Result;

namespace Omni.Business.ImageTagging
{
    // OMNI BUSINESS LAYER: Tag Taxonomy Manager
    // Manages tag hierarchies, aliases, and filters conflicting tags.

    public class TagNode
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public List<int> Implies { get; set; } = new List<int>();
    }

    public class TagTaxonomyManager
    {
        private Dictionary<int, TagNode> _taxonomy;

        public TagTaxonomyManager(Dictionary<int, TagNode> taxonomy)
        {
            _taxonomy = taxonomy;
        }

        public OmniResult<List<string>, string> ResolveTags(Dictionary<int, float> predictedTags)
        {
            try
            {
                var finalTagSet = new HashSet<int>(predictedTags.Keys);

                // Add implied tags (e.g. "cat" implies "animal")
                foreach (var tagId in predictedTags.Keys)
                {
                    if (_taxonomy.TryGetValue(tagId, out var node))
                    {
                        foreach (var implied in node.Implies)
                        {
                            finalTagSet.Add(implied);
                        }
                    }
                }

                // Map back to names
                var resultNames = finalTagSet
                    .Where(id => _taxonomy.ContainsKey(id))
                    .Select(id => _taxonomy[id].Name)
                    .OrderBy(name => name)
                    .ToList();

                return OmniResult<List<string>, string>.Ok(resultNames);
            }
            catch (Exception ex)
            {
                return OmniResult<List<string>, string>.Err($"Tag resolution failed: {ex.Message}");
            }
        }
    }
}
