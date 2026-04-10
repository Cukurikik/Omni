// ═══════════════════════════════════════════════════════════
// OMNI-STD GRAPH — OmniGraph (GraphQL Runtime)
// ═══════════════════════════════════════════════════════════
// Schema-first query builder dan executor
// ═══════════════════════════════════════════════════════════

var OmniGraph = (function() {

    var _schemas = {};
    var _resolvers = {};
    var _data = {};

    function defineSchema(typeName, fields) {
        _schemas[typeName] = fields;
    }

    function addResolver(typeName, resolver) {
        _resolvers[typeName] = resolver;
    }

    function seed(typeName, records) {
        _data[typeName] = records;
    }

    function query(queryString) {
        // Parse simple query: "user id name email" → type=user, fields=[id,name,email]
        var parts = queryString.trim().split(/\s+/);
        // Clean up Ident() wrapper from transpiler
        var cleaned = parts.map(function(p) {
            var match = p.match(/^Ident\("(.+)"\)$/);
            return match ? match[1] : p;
        }).filter(function(p) { return p.length > 0; });

        if (cleaned.length === 0) return null;

        var typeName = cleaned[0];
        var fields = cleaned.slice(1);

        // Check if resolver exists
        if (_resolvers[typeName]) {
            var raw = _resolvers[typeName]();
            if (fields.length === 0) return raw;
            // Select only requested fields
            if (Array.isArray(raw)) {
                return raw.map(function(item) {
                    var projected = {};
                    fields.forEach(function(f) {
                        if (item.hasOwnProperty(f)) projected[f] = item[f];
                    });
                    return projected;
                });
            }
            return raw;
        }

        // Check seeded data
        if (_data[typeName]) {
            var data = _data[typeName];
            if (fields.length === 0) return data;
            return data.map(function(item) {
                var projected = {};
                fields.forEach(function(f) {
                    if (item.hasOwnProperty(f)) projected[f] = item[f];
                });
                return projected;
            });
        }

        return '[GraphQL Result: ' + typeName + ' { ' + fields.join(', ') + ' }]';
    }

    function mutation(mutationString, variables) {
        return { 
            mutation: mutationString, 
            variables: variables || {},
            status: 'executed' 
        };
    }

    return {
        defineSchema: defineSchema,
        addResolver: addResolver,
        seed: seed,
        query: query,
        mutation: mutation
    };
})();
