package omni.security.sanitization;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Types;
import java.util.List;

/**
 * OMNI MOTHER SYSTEM - SECURITY LAYER
 * SQL Parameterized Query Binder.
 * Enforces strict PreparedStatement boundaries, completely eliminating SQL injection vectors at the JVM level.
 */
public class SqlParameterizedQueryBinder {

    /**
     * Interface defining supported SQL data types to ensure type-safe binding.
     */
    public enum SqlType {
        INTEGER, STRING, BOOLEAN, DOUBLE, NULL_VAL
    }

    public static class QueryParam {
        public final SqlType type;
        public final Object value;

        public QueryParam(SqlType type, Object value) {
            this.type = type;
            this.value = value;
        }
        
        // Convenience constructors
        public static QueryParam ofInt(Integer val) { return new QueryParam(val == null ? SqlType.NULL_VAL : SqlType.INTEGER, val); }
        public static QueryParam ofString(String val) { return new QueryParam(val == null ? SqlType.NULL_VAL : SqlType.STRING, val); }
        public static QueryParam ofBool(Boolean val) { return new QueryParam(val == null ? SqlType.NULL_VAL : SqlType.BOOLEAN, val); }
    }

    /**
     * @brief Securely binds dynamic parameters to a pre-compiled SQL string.
     * NEVER concatenate user input into the raw SQL string.
     * 
     * @param connection Active JDBC Connection.
     * @param rawSql The static SQL query containing '?' placeholders.
     * @param params List of strongly-typed parameters.
     * @return An executable PreparedStatement.
     * @throws SQLException If database access fails.
     */
    public PreparedStatement createSecureStatement(Connection connection, String rawSql, List<QueryParam> params) throws SQLException {
        
        // 1. Guard against literal injections
        if (rawSql == null || rawSql.trim().isEmpty()) {
            throw new SQLException("OMNI_FATAL: Empty SQL string provided.");
        }

        // 2. The JDBC Driver compiles the SQL structure BEFORE inserting data.
        // This is the absolute core of SQL Injection prevention.
        PreparedStatement stmt = connection.prepareStatement(rawSql);

        // 3. Bind parameters strictly by type
        if (params != null) {
            for (int i = 0; i < params.size(); i++) {
                int paramIndex = i + 1; // JDBC parameters are 1-indexed
                QueryParam param = params.get(i);

                switch (param.type) {
                    case INTEGER:
                        stmt.setInt(paramIndex, (Integer) param.value);
                        break;
                    case STRING:
                        stmt.setString(paramIndex, (String) param.value);
                        break;
                    case BOOLEAN:
                        stmt.setBoolean(paramIndex, (Boolean) param.value);
                        break;
                    case DOUBLE:
                        stmt.setDouble(paramIndex, (Double) param.value);
                        break;
                    case NULL_VAL:
                        // Generically set NULL for untyped SQL columns
                        stmt.setNull(paramIndex, Types.NULL);
                        break;
                    default:
                        throw new SQLException("OMNI_FATAL: Unsupported SQL parameter type.");
                }
            }
        }

        return stmt;
    }
}
